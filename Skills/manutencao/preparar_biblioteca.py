"""Empacotamento determinístico de revisões locais fixadas, sem executar fornecedores."""
import sys
sys.dont_write_bytecode = True
import argparse
import difflib
import json
import os
import re
from collections import Counter
from pathlib import Path

from inventariar import build, digest, git
from biblioteca import ROOT, DOMAINS, CONTRACT, add_contract, json_bytes, render_official, sha, safe_path, require_asdf_python


def prepare():
    runtime = require_asdf_python()
    original, indexes, references = build()
    policy = json.loads((ROOT/'Skills/manutencao/distribuicao-politica.json').read_text())
    decisions = {r['id']:r for r in policy['rows']}
    if len(decisions)!=len(policy['rows']) or set(decisions)!={s['id'] for s in original['skills']}:
        raise ValueError('Política não classifica exatamente as skills adquiridas')
    sources = {s['id']:s for s in original['sources']}
    original_skills = {s['id']:s for s in original['skills']}
    records = {source:{r['path']:r for r in index['files']} for source,index in indexes.items()}
    outputs, packages, patches = {}, {}, []

    def read(source_id, relative):
        source = sources[source_id]
        path = safe_path(ROOT/source['directory'],relative)
        record = records[source_id].get(relative)
        if not record or record['type']!='file' or path.is_symlink():
            raise ValueError('Arquivo da origem não regular: '+source_id+':'+relative)
        data = path.read_bytes()
        # Índice SHA-256 e blob Git imutável são conferidos, não somente stat/status.
        blob = __import__('hashlib').sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if sha(data)!=record['sha256'] or blob!=record['git_blob']:
            raise ValueError('Origem diverge do commit: '+source_id+':'+relative)
        return data

    def put(package, relative, data, source_paths=(), adaptation=None, original_data=None):
        safe_path(ROOT/package['directory'],relative)
        if relative in package['files']:
            if outputs[package['directory']+'/'+relative]!=data:
                raise ValueError('Colisão de conteúdo: '+relative)
            return
        inputs = [{'path':p,'sha256':sha(read(package['source_id'],p))} for p in source_paths]
        record = {'sha256':sha(data),'size':len(data),'mode':'100644','inputs':inputs,
                  'adaptation':adaptation,'origin':'vendor' if inputs else 'StackNauta'}
        package['files'][relative]=record
        outputs[package['directory']+'/'+relative]=data
        if adaptation and original_data is not None and original_data!=data:
            before,after=original_data.decode().splitlines(True),data.decode().splitlines(True)
            patches.append({'package':package['id'],'path':relative,'reason':adaptation,
                            'before_sha256':sha(original_data),'after_sha256':sha(data),
                            'diff':''.join(difflib.unified_diff(before,after,fromfile='upstream',tofile='distribution'))})

    # Templates de manutenção preservados uma vez; não são dependência em runtime.
    ui = sources['ui-ux-pro-max']
    template_inputs = {}
    template_paths = ['base/skill-content.md','base/quick-reference.md']+['platforms/'+n+'.json' for n in ('universal','codex','opencode','gemini')]
    for relative in template_paths:
        origin='src/ui-ux-pro-max/templates/'+relative
        data=read('ui-ux-pro-max',origin)
        dest='Skills/manutencao/ui-ux-pro-max-templates/'+relative
        outputs[dest]=data
        template_inputs[relative]={'path':origin,'sha256':sha(data)}
    outputs['Skills/manutencao/ui-ux-pro-max-templates/LICENSE']=read('ui-ux-pro-max','LICENSE')
    # Render com a fonte fixada; a cópia versionada será verificada e reproduzível no clone.
    templates=ROOT/ui['directory']/'src/ui-ux-pro-max/templates'
    universal=json.loads(read('ui-ux-pro-max','src/ui-ux-pro-max/templates/platforms/universal.json'))

    catalog=json.loads(json.dumps(original))
    catalog.pop('generated_at_utc',None)
    catalog.update(schema_version=2,stage='1.5',
                   generation={'deterministic':True,'tool':'Skills/manutencao/preparar_biblioteca.py',
                               'tool_sha256':sha(Path(__file__).read_bytes()),
                               'policy_sha256':sha((ROOT/'Skills/manutencao/distribuicao-politica.json').read_bytes()),
                               'source_lock_sha256':sha((ROOT/'Skills/fontes.lock.json').read_bytes())},
                   approval_scope=policy['approval_scope'],bootstrap_implemented=False)
    for skill in catalog['skills']:
        decision=decisions[skill['id']]
        skill['acquisition_category']=skill['category']
        skill['category']=decision['category']
        skill['acquisition_validation']=skill.pop('validation')
        skill['distribution_status']=decision['status']
        skill['decision_reason']=decision['reason']
        skill['pending']=[decision['reason']] if decision['status']!='approved' else []
        skill['validation']={'status':'packaged' if decision['status']=='approved' else 'not_distributed',
                             'copy_plan_complete':decision['status']=='approved','enabled':False,
                             'agent_integration_tested':False,'vendor_workflow_certified':False}
        skill['distribution']=None
        if decision['status']!='approved':
            continue
        category=decision['category']
        if category not in DOMAINS:
            raise ValueError('Categoria de distribuição inválida')
        key=category+'/'+skill['source_id']
        package=packages.setdefault(key,{'id':key,'directory':'Skills/'+key,'source_id':skill['source_id'],
                    'repository':skill['repository'],'commit':skill['commit'],'skills':[], 'files':{},'shared_files':[], 'skill_extra_files':{}})
        package['skills'].append(skill['id'])
        skill_root=Path(skill['source_path']).parent.as_posix()
        prefix=skill_root+'/'
        folder='skills/'+skill['name']
        skill['distribution']={'package':key,'skill_directory':folder,'requires_skills':[],
                               'runtime_requirements':skill['dependency_evidence'],
                               'application_requirements_not_installed':True}
        for relative, record in records[skill['source_id']].items():
            if not relative.startswith(prefix):
                continue
            target=folder+'/'+relative[len(prefix):]
            data=read(skill['source_id'],relative)
            before=data
            adaptation=[]
            source_paths=[relative]
            if relative==skill['source_path']:
                text=data.decode()
                if skill['id']=='ui-ux-pro-max:ui-ux-pro-max':
                    text=render_official(universal,templates)
                    before=text.encode()
                    source_paths=['src/ui-ux-pro-max/templates/base/skill-content.md','src/ui-ux-pro-max/templates/platforms/universal.json']
                    # Comandos não pressupõem pasta de agente ou cwd de instalação.
                    start=text.index('# Prerequisites')
                    end=text.index('---',start)
                    text=text[:start]+'# Prerequisites\n\nUse the verified installed global asdf Python described in the execution contract.\nNo fallback runtime or automatic installation is permitted.\n\n'+text[end:]
                    rooted=universal['folderStructure']['root']+'/'+universal['scriptPath']
                    text=text.replace('python3 '+rooted,'"<asdf-global-python>" "<skill-dir>/scripts/search.py"')
                    adaptation.append('Official universal template rendering; portable skill path; asdf global prerequisite replaces system fallbacks.')
                if skill['id']=='expo:expo-overview':
                    text=text.replace('- `expo-tailwind-setup` — Tailwind / NativeWind styling',
                        '- Tailwind / NativeWind styling — no dedicated skill is supplied by this pinned revision; stop this route and report that limitation instead of loading a nonexistent skill.')
                    text=text.replace('`references/native-ios.md`','`../eas-app-stores/references/native-ios.md`')
                    adaptation.append('Removed stale route to absent expo-tailwind-setup; resolved iOS reference to bundled companion.')
                if skill['id']=='sentry:agents-md':
                    text=text.replace('symlink `CLAUDE.md` to `AGENTS.md`','physically copy `AGENTS.md` to `CLAUDE.md` and keep both copies synchronized')
                    adaptation.append('Physical agent entrypoint copies replace consumer symlink guidance.')
                declared_license=skill['frontmatter_fields'].get('license','')
                license_match=re.search(r'(?:^|\s)(LICENSE(?:\.txt)?)$',declared_license)
                license_name=license_match[1] if license_match else None
                if license_name and not (ROOT/skill['source_root']/skill_root/license_name).exists():
                    if not (ROOT/skill['source_root']/license_name).is_file():
                        raise ValueError('Licença declarada sem arquivo raiz: '+skill['id'])
                    text=text.replace('license: '+declared_license,'license: '+declared_license.replace(license_name,'../../'+license_name),1)
                    adaptation.append('Missing local LICENSE reference resolves to preserved bundle root licence.')
                data=add_contract(text).encode()
                adaptation.append('Explicit relative distribution/execution contract; vendor examples remain subordinate to global asdf policy.')
            if skill['id']=='ui-ux-pro-max:ui-ux-pro-max' and relative.startswith(prefix+'data/') or skill['id']=='ui-ux-pro-max:ui-ux-pro-max' and relative.startswith(prefix+'scripts/'):
                canonical='src/ui-ux-pro-max/'+relative[len(prefix):]
                data=read('ui-ux-pro-max',canonical)
                source_paths=[canonical]
                before=data
            if target.endswith('brand/scripts/sync-brand-to-tokens.cjs'):
                data=data.replace(b"execFileSync('node',",b'execFileSync(process.execPath,')
                adaptation.append('Child Node inherits the verified parent executable instead of a PATH/system fallback.')
            put(package,target,data,source_paths,' '.join(adaptation) or None,before)

    by_id={s['id']:s for s in catalog['skills']}
    # Recursos de uma skill irmã são copiados uma vez, mantendo o caminho oficial.
    ui_package=packages['Frontend/ui-ux-pro-max']
    auxiliary='.claude/skills/design-system/scripts/generate-tokens.cjs'
    put(ui_package,'skills/design-system/scripts/generate-tokens.cjs',read('ui-ux-pro-max',auxiliary),[auxiliary])
    ui_package['skill_extra_files']['ui-ux-pro-max:brand']=['skills/design-system/scripts/generate-tokens.cjs']
    for skill in catalog['skills']:
        if skill['distribution_status']!='approved':
            continue
        dependencies=set()
        # Arquivos referenciados em outra skill demandam o diretório completo da irmã.
        for relative in original_skills[skill['id']]['required_files']:
            for other in original['skills']:
                if other['source_id']==skill['source_id'] and other['id']!=skill['id'] and relative.startswith(Path(other['source_path']).parent.as_posix()+'/'):
                    dependencies.add(other['id'])
        # Roteamento por nome, quando o alvo também é distribuído neste pacote.
        for identifier in skill['sibling_skill_mentions']:
            if by_id[identifier]['distribution_status']=='approved':
                dependencies.add(identifier)
        if skill['source_id']=='expo':
            dependencies.add('expo:expo-overview')
            if skill['id']=='expo:expo-overview':
                dependencies.update(s['id'] for s in catalog['skills'] if s['source_id']=='expo' and s['distribution_status']=='approved')
        if skill['id']=='sentry:secret-serialization':
            dependencies.add('sentry:security-review')
        dependencies.discard(skill['id'])
        for identifier in dependencies:
            other=by_id[identifier]
            if other['distribution_status']!='approved' or other['distribution']['package']!=skill['distribution']['package']:
                raise ValueError('Dependência de pacote não fechada: '+skill['id']+' -> '+identifier)
        skill['distribution']['requires_skills']=sorted(dependencies)

    for key,package in packages.items():
        source=sources[package['source_id']]
        # Licenças ancestrais são comuns, uma única cópia física por pacote.
        for relative in source['license_files']:
            if '/' not in relative:
                put(package,relative,read(source['id'],relative),[relative])
                package['shared_files'].append(relative)
        lines=['# '+key,'',CONTRACT,'','## Included skills','']
        lines.extend('- `'+by_id[identifier]['name']+'`: `'+by_id[identifier]['distribution']['skill_directory']+'/SKILL.md`' for identifier in sorted(package['skills']))
        lines.extend(['','## Provenance','',source['url']+' at `'+source['commit']+'`.','All file origins, hashes and adaptations are recorded in PROVENANCE.json.',''])
        put(package,'README.md','\n'.join(lines).encode())
        package['shared_files'].append('README.md')
        package['skills'].sort()
        package['shared_files']=sorted(set(package['shared_files']))
        outputs[package['directory']+'/PROVENANCE.json']=json_bytes(package)
    counts=catalog['counts']
    counts.update(approved_skills=sum(r['status']=='approved' for r in decisions.values()),
                  pending_skills=sum(r['status']=='pending' for r in decisions.values()),
                  excluded_skills=sum(r['status']=='excluded' for r in decisions.values()),
                  prepared_distribution_skills=sum(r['status']=='approved' for r in decisions.values()),
                  distribution_packages=len(packages),
                  approved_by_category=dict(sorted(Counter(s['category'] for s in catalog['skills'] if s['distribution_status']=='approved').items())),
                  by_category=dict(sorted(Counter(s['category'] for s in catalog['skills']).items())))
    catalog['distribution_packages']=[{'id':p['id'],'directory':p['directory'],'skills':p['skills'],
                                    'manifest_sha256':sha(outputs[p['directory']+'/PROVENANCE.json'])} for p in packages.values()]
    catalog['template_inputs']=template_inputs
    catalog['python_executor']=runtime
    outputs['Skills/catalogo.json']=json_bytes(catalog)
    outputs['Skills/validacao/adaptacoes.json']=json_bytes(patches)
    review=[]
    for identifier,items in references.items():
        for item in items:
            if item['status']!='unresolved_requires_review':
                continue
            target=item['target']
            if identifier.startswith('ui-ux-pro-max:'):
                if target in ('assets/css/slide-animations.css','assets/designs/slides/claudekit-pitch-251223.html'):
                    outcome='pending_upstream_gap'
                    reason='Recurso/exemplo ausente na origem: fluxos design-system, slides e design não aprovados.'
                else:
                    outcome='consumer_output_or_example'
                    reason='Tokens, CSS e banners são arquivos do projeto consumidor/exemplos, não dependências locais da biblioteca.'
            elif identifier=='expo:expo-overview':
                outcome='resolved_companion'
                reason='SKILL.md distribuído aponta explicitamente a ../eas-app-stores/references/native-ios.md; companheira incluída no fechamento.'
            elif identifier in ('sentry:security-model','sentry:secret-serialization'):
                outcome='upstream_maintenance_only'
                reason='SPEC registra validação executada a partir de skill-writer; não é helper de runtime desta skill. Fonte original preservada no histórico de aquisição.'
            elif identifier=='sentry:browse-local-sentry':
                outcome='external_source_attribution'
                reason='SOURCES.md cita código de getsentry/sentry, não recurso desta skill. Fluxo organizacional permanece pendente.'
            else:
                outcome='example_or_generated_artifact'
                reason='Exemplo de relatório, roteamento ou arquivo a criar; não é entrada de runtime fornecida pela skill.'
            review.append(dict(item,skill_id=identifier,disposition=outcome,reason=reason))
    outputs['Skills/validacao/revisao-recursos.json']=json_bytes(review)
    for category in (*DOMAINS,'manutencao','validacao'):
        lines=['# '+category,'','Biblioteca preparada na Etapa 1.5. Nenhuma skill ativada.','',
               '| Skill | Status | Pacote ou impedimento |','|---|---|---|']
        rows=[s for s in catalog['skills'] if s['category']==category]
        for s in rows:
            dist=s['distribution']
            if dist:
                p=next(p for p in packages.values() if p['id']==dist['package'])
                target=os.path.relpath(ROOT/p['directory']/dist['skill_directory']/'SKILL.md',ROOT/'Skills'/category)
                label='['+s['name']+']('+target+')'
                detail=dist['package']
            else:
                label=s['name'];detail=s['decision_reason']
            lines.append('| '+label+' | '+s['distribution_status']+' | '+detail+' |')
        if not rows:
            lines.extend(['','Diretório reservado às ferramentas e evidências da biblioteca; os pacotes de consumo estão nas quatro categorias de domínio.'])
        outputs['Skills/'+category+'/README.md']='\n'.join(lines).encode()+b'\n'
    return outputs,catalog


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true',help='Gravar pacotes e metadados após validar as origens')
    args=parser.parse_args()
    outputs,catalog=prepare()
    previous=json.loads((ROOT/'Skills/catalogo.json').read_text())
    # Recusa sobrescrever alterações ou arquivos estranhos dentro de pacotes existentes.
    for old in previous.get('distribution_packages',[]):
        folder=ROOT/old['directory'];manifest=folder/'PROVENANCE.json'
        if folder.is_symlink():
            raise SystemExit('Destino de pacote é link simbólico: '+old['id'])
        if sha(manifest.read_bytes())!=old['manifest_sha256']:
            raise SystemExit('Manifesto de pacote modificado: '+old['id'])
        data=json.loads(manifest.read_text())
        actual={p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file() or p.is_symlink()}
        if actual!=set(data['files'])|{'PROVENANCE.json'}:
            raise SystemExit('Arquivos estranhos/ausentes em pacote: '+old['id'])
        for relative,record in data['files'].items():
            path=safe_path(folder,relative)
            if path.is_symlink() or sha(path.read_bytes())!=record['sha256']:
                raise SystemExit('Conteúdo de pacote modificado: '+old['id']+':'+relative)
            if old['directory']+'/'+relative not in outputs:
                raise SystemExit('Arquivo ficaria obsoleto; revisão manual necessária: '+relative)
    mismatches=[p for p,data in outputs.items() if not (ROOT/p).is_file() or (ROOT/p).read_bytes()!=data]
    if not previous.get('distribution_packages'):
        for p in catalog['distribution_packages']:
            if (ROOT/p['directory']).exists():
                raise SystemExit('Destino de pacote já existe; revisão necessária: '+p['directory'])
    if args.write:
        for relative,data in outputs.items():
            target=safe_path(ROOT,relative)
            if target.exists() and relative not in mismatches:
                continue
            if target.exists() and relative.startswith(tuple(p['directory']+'/' for p in catalog['distribution_packages'])) and not previous.get('distribution_packages'):
                raise SystemExit('Destino de pacote já existe; não sobrescrever: '+relative)
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(data)
    elif mismatches:
        raise SystemExit('Artefatos precisam de regeneração: '+', '.join(mismatches[:12]))
    print(json.dumps(catalog['counts'],ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
