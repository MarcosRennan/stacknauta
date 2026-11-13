"""Validação offline da biblioteca; cache somente quando --origens é explícito."""
import sys
sys.dont_write_bytecode=True
import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import unquote,urlsplit

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Skills/manutencao'))
from biblioteca import DOMAINS, CONTRACT, sha, safe_path, selected_files, render_official, require_asdf_python
from inventariar import frontmatter, git


def check_links(root, paths=None, available_paths=None):
    checked,errors=0,[]
    paths=paths if paths is not None else [p.relative_to(root).as_posix() for p in root.rglob('*.md')]
    for relative in paths:
        p=root/relative
        if p.suffix!='.md':
            continue
        text=re.sub(r'^```.*?^```[^\n]*','',p.read_text(errors='replace'),flags=re.M|re.S)
        for target in re.findall(r'\[[^\]\n]*\]\(([^)\s]+)\)',text):
            token=unquote(target.strip('<>').split('#',1)[0])
            if not token or urlsplit(token).scheme or token.startswith('//') or token.lower() in {'url','path/to/screenshot'} or any(c in token for c in '{}<>*`'):
                continue
            q=p.parent/token
            unavailable=False
            if available_paths is not None and q.exists() and q.resolve().is_relative_to(root.resolve()):
                local=q.resolve().relative_to(root.resolve()).as_posix()
                unavailable=local not in available_paths and not (q.is_dir() and any(p.startswith(local+'/') for p in available_paths))
            if not q.exists() or not q.resolve().is_relative_to(root.resolve()) or unavailable:
                errors.append(relative+' -> '+target)
            checked+=1
    return checked,errors


def check_record(path,record):
    if path.is_symlink() or not path.is_file():
        raise ValueError('Arquivo não físico: '+path.name)
    data=path.read_bytes()
    if sha(data)!=record['sha256'] or len(data)!=record['size']:
        raise ValueError('Integridade divergente: '+path.name)
    return data


def source_validation(catalog,indexes):
    from inventariar import build
    original,current,refs=build()
    if current!=indexes or refs!=json.loads((ROOT/'Skills/validacao/recursos.json').read_text()):
        raise ValueError('Cache diverge do índice de aquisição')
    if {s['id']:s['source_path'] for s in original['skills']}!={s['id']:s['source_path'] for s in catalog['skills']}:
        raise ValueError('Skills adquiridas divergem do catálogo')
    checked,links=0,0
    for source in catalog['sources']:
        root=ROOT/source['directory']
        if git(root,'remote','get-url','origin')!=source['url'] or git(root,'branch','--show-current')!=source['branch']:
            raise ValueError('URL/branch da origem divergente: '+source['id'])
        git(root,'fsck','--full','--no-dangling')
        for record in indexes[source['id']]['files']:
            p=root/record['path']
            data=os.readlink(p).encode() if record['type']=='symlink' else p.read_bytes()
            if record['type']=='symlink':
                if Path(os.readlink(p)).is_absolute() or not p.exists() or not p.resolve().is_relative_to(root.resolve()):
                    raise ValueError('Link de origem inválido: '+record['path'])
                links+=1
            else:
                if sha(data)!=record['sha256']:
                    raise ValueError('SHA de origem divergente: '+record['path'])
                checked+=1
            blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            if blob!=record['git_blob']:
                raise ValueError('Blob original divergente: '+record['path'])
    return {'status':'passed','sources':len(catalog['sources']),'files':checked,'relative_links':links}


def verify_copies(catalog,packages,*,vendor_smoke=True):
    temp=Path(tempfile.mkdtemp(prefix='stacknauta-copy-'))
    # Evidências temporárias mantidas; nenhuma exclusão recursiva.
    tests=[]
    for skill in catalog['skills']:
        if skill['distribution_status']!='approved':
            continue
        package=packages[skill['distribution']['package']]
        files,closure=selected_files(skill['id'],catalog,package)
        destination=temp/skill['id'].replace(':','-')
        destination.mkdir()
        for relative in files:
            source=safe_path(ROOT/package['directory'],relative)
            target=safe_path(destination,relative)
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,target)
            if target.is_symlink() or os.path.samefile(source,target) or target.read_bytes()!=source.read_bytes():
                raise ValueError('Cópia não física/íntegra: '+skill['id']+':'+relative)
        checked,broken=check_links(destination,files)
        if broken:
            raise ValueError('Cópia sem fechamento: '+skill['id']+': '+repr(broken[:3]))
        tests.append({'skill':skill['id'],'skills_in_closure':len(closure),'files_copied':len(files),'local_links_checked':checked})
    ui=temp/'ui-ux-pro-max-ui-ux-pro-max'/'skills/ui-ux-pro-max'
    script=ui/'scripts/search.py'
    environment=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    searches=[]
    commands=[['keyboard focus','--domain','ux','--json'],['server components','--stack','nextjs','--json'],['saas dashboard','--design-system','--json']] if vendor_smoke else []
    for args in commands:
        result=subprocess.run([sys.executable,'-B',str(script),*args],cwd=temp,env=environment,capture_output=True,text=True,timeout=30,check=True)
        data=json.loads(result.stdout)
        if '--design-system' in args:
            if not data.get('design_system') or data.get('persistence') is not None:
                raise ValueError('Busca de design-system falhou ou persistiu dados')
        elif not data.get('count') or data.get('error'):
            raise ValueError('Busca UI/UX sem recursos utilizáveis: '+repr(data))
        searches.append({'arguments':args,'status':'passed','result_count':data.get('count')})
    if (temp/'design-system').exists():
        raise ValueError('Smoke test escreveu design-system indevidamente')
    # Testes adversariais usam um recurso REAL da cópia e o mesmo verificador da biblioteca.
    sample=ui/'data/ux-guidelines.csv'
    record=packages['Frontend/ui-ux-pro-max']['files']['skills/ui-ux-pro-max/data/ux-guidelines.csv']
    original=sample.read_bytes();sample.write_bytes(original+b'\ncorrupted')
    try:
        check_record(sample,record)
        detects_hash=False
    except ValueError:
        detects_hash=True
    sample.write_bytes(original)
    document=ui/'SKILL.md';before=document.read_bytes()
    document.write_bytes(before+b'\n[invalid required resource](references/absent-negative-test.md)\n')
    _,broken=check_links(ui.parent.parent,['skills/ui-ux-pro-max/SKILL.md'])
    detects_reference=any('absent-negative-test.md' in r for r in broken)
    document.write_bytes(before)
    try:
        safe_path(temp,'../escape')
        detects_traversal=False
    except ValueError:
        detects_traversal=True
    if not detects_hash or not detects_traversal or not detects_reference:
        raise ValueError('Verificação adversarial falhou')
    return {'status':'passed','temporary_directory':str(temp),'physical_copy_cases':len(tests),
            'files_copied':sum(t['files_copied'] for t in tests),'cases':tests,'ui_smoke_tests':searches,
            'ui_smoke_tests_status':'passed' if vendor_smoke else 'not_requested','vendor_code_executed':bool(searches),
            'adversarial_checks':{'changed_content_detected':detects_hash,'missing_reference_detected':detects_reference,'path_escape_rejected':detects_traversal}}


def validate(origins=False,copies=False,node_syntax=False,*,vendor_smoke=True):
    runtime=require_asdf_python()
    catalog=json.loads((ROOT/'Skills/catalogo.json').read_text())
    lock=json.loads((ROOT/'Skills/fontes.lock.json').read_text())
    policy=json.loads((ROOT/'Skills/manutencao/distribuicao-politica.json').read_text())
    indexes=json.loads((ROOT/'Skills/validacao/arquivos.json').read_text())
    source_records={source:{r['path']:r for r in entry['files']} for source,entry in indexes.items()}
    errors,checks=[],[]
    generation=catalog['generation']
    for relative,expected in ((generation['tool'],generation['tool_sha256']),
                              ('Skills/manutencao/distribuicao-politica.json',generation['policy_sha256']),
                              ('Skills/fontes.lock.json',generation['source_lock_sha256'])):
        if sha(safe_path(ROOT,relative).read_bytes())!=expected:
            errors.append('Receita/política/lock mudou sem regeneração: '+relative)
    if catalog['stage']!='1.5' or catalog.get('bootstrap_implemented') is not False:
        errors.append('Etapa/estado do bootstrap incorretos')
    if (not lock['sources'] or len({s['id'] for s in lock['sources']})!=len(lock['sources']) or
        len({s['id'] for s in catalog['sources']})!=len(catalog['sources']) or
        {s['id']:(s['commit'],s['url']) for s in lock['sources']}!={s['id']:(s['commit'],s['url']) for s in catalog['sources']}):
        errors.append('Lock e catálogo divergem nas origens/revisões ou possuem IDs duplicados')
    decisions={r['id']:r for r in policy['rows']}
    skills={s['id']:s for s in catalog['skills']}
    if set(decisions)!=set(skills) or len(skills)!=len(catalog['skills']):
        errors.append('Cobertura da política ou IDs inválidos')
    packages={}
    all_skill_paths=set();checked_files=0;python_files=0;node_files=[];local_links=0;adapted=set()
    for descriptor in catalog['distribution_packages']:
        root=safe_path(ROOT,descriptor['directory'])
        if Path(descriptor['directory']).parts[1] not in DOMAINS or root.is_symlink():
            raise ValueError('Pacote fora das categorias/real: '+descriptor['id'])
        manifest=root/'PROVENANCE.json'
        if sha(manifest.read_bytes())!=descriptor['manifest_sha256']:
            raise ValueError('Manifesto adulterado: '+descriptor['id'])
        package=json.loads(manifest.read_text())
        packages[package['id']]=package
        actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() or p.is_symlink()}
        if actual!=set(package['files'])|{'PROVENANCE.json'}:
            errors.append('Arquivos ausentes/adicionais: '+package['id'])
        for rel,record in package['files'].items():
            path=safe_path(root,rel)
            data=check_record(path,record)
            if stat.S_IMODE(path.stat().st_mode)&0o111:
                errors.append('Arquivo de distribuição executável fora do contrato: '+package['id']+':'+rel)
            if b'_repos/' in data or str(Path.home()).encode() in data or ('/'+'App-Web'+'/').encode() in data:
                errors.append('Dependência/caminho da aquisição ou instalação: '+package['id']+':'+rel)
            for item in record['inputs']:
                expected=source_records[package['source_id']].get(item['path'])
                if not expected or item['sha256']!=expected.get('sha256'):
                    errors.append('Proveniência incompatível com aquisição: '+rel)
            if len(record['inputs'])==1 and not record['adaptation'] and record['sha256']!=record['inputs'][0]['sha256']:
                errors.append('Mudança de fornecedor não declarada: '+rel)
            if record['adaptation']:
                adapted.add((package['id'],rel))
            if path.suffix=='.py':
                ast.parse(data,filename=rel);python_files+=1
            elif path.suffix in ('.js','.cjs','.mjs'):
                node_files.append(path)
            if path.name=='SKILL.md':
                fm=frontmatter(data.decode())
                all_skill_paths.add((package['id'],rel))
                if 'StackNauta distribution' not in data.decode():
                    errors.append('Contrato de consumo ausente: '+rel)
                declared=fm.get('license','')
                license_match=re.search(r'(?:^|\s)([\w./-]*LICENSE(?:\.txt)?)$',declared)
                if license_match:
                    if not (path.parent/license_match[1]).is_file():
                        errors.append('Licença referenciada ausente: '+rel)
            checked_files+=1
        count,broken=check_links(root)
        local_links+=count
        errors.extend('Link local obrigatório inválido: '+package['id']+':'+b for b in broken)
        if not any(Path(p).name.upper().startswith(('LICENSE','COPYING','NOTICE')) for p in package['shared_files']):
            errors.append('Licença raiz não compartilhada: '+package['id'])
    expected_paths=set()
    for identifier,skill in skills.items():
        if skill['enabled'] or skill['distribution_status']!=decisions[identifier]['status'] or skill['category']!=decisions[identifier]['category']:
            errors.append('Habilitação/classificação divergente: '+identifier)
        if skill['distribution_status']=='approved':
            dist=skill['distribution'];expected_paths.add((dist['package'],dist['skill_directory']+'/SKILL.md'))
            selected,closure=selected_files(identifier,catalog,packages[dist['package']])
            if any(not (ROOT/packages[dist['package']]['directory']/rel).is_file() for rel in selected):
                errors.append('Plano de cópia incompleto: '+identifier)
        elif skill['distribution'] is not None or not skill['decision_reason']:
            errors.append('Skill não aprovada tem pacote ou não tem justificativa: '+identifier)
    if expected_paths!=all_skill_paths:
        errors.append('SKILL.md não aprovado ou ausente nos pacotes')
    observed=Counter(s['distribution_status'] for s in skills.values())
    for key in ('approved','pending','excluded'):
        if catalog['counts'][key+'_skills']!=observed[key]:
            errors.append('Contagem divergente: '+key)
    patches=json.loads((ROOT/'Skills/validacao/adaptacoes.json').read_text())
    if {(p['package'],p['path']) for p in patches}!=adapted:
        errors.append('Adaptações sem diff auditável ou diffs sem arquivo')
    for patch in patches:
        if patch['after_sha256']!=packages[patch['package']]['files'][patch['path']]['sha256']:
            errors.append('Diff de adaptação divergente: '+patch['path'])
    template_root=ROOT/'Skills/manutencao/ui-ux-pro-max-templates'
    for relative,record in catalog['template_inputs'].items():
        if sha((template_root/relative).read_bytes())!=record['sha256']:
            errors.append('Template oficial versionado divergente: '+relative)
    core_marker=ROOT/'Automacao/project-bootstrap/STATUS.json'
    core_state={}
    if core_marker.exists():
        sys.path.insert(0,str(ROOT/'Automacao/project-bootstrap'))
        from stacknauta_core.compatibility import catalog_policies
        catalog_policies(catalog['skills'])
        core_state=json.loads(core_marker.read_text())
        if core_state!={'stage':'2A','core_implemented':True,'agent_integration_tested':False,'production_ready':False}:
            errors.append('Estado do núcleo fora da etapa 2A declarada.')
        for relative in ('Automacao/project-bootstrap/bootstrap.py','Automacao/project-bootstrap/project-bootstrap',
                         'Automacao/project-bootstrap/stacknauta_core/core.py',
                         'Automacao/validacao-project-bootstrap/test_bootstrap.py'):
            path=ROOT/relative
            if not path.is_file() or path.is_symlink():
                errors.append('Artefato obrigatório do núcleo ausente/não físico: '+relative)
        integration_skill=ROOT/'.agents/skills/project-bootstrap/SKILL.md'
        if integration_skill.exists():
            if integration_skill.is_symlink():
                errors.append('Skill de integração não física')
            metadata=frontmatter(integration_skill.read_text())
            if metadata.get('name')!='project-bootstrap' or not metadata.get('description'):
                errors.append('Metadados da skill de integração inválidos')
            if sorted(p.name for p in (ROOT/'.agents/skills').iterdir())!=['project-bootstrap']:
                errors.append('Skills de automação não registradas')
            for relative in ('AGENTS.md','GEMINI.md','Automacao/project-bootstrap/stacknauta_core/integration.py'):
                if not (ROOT/relative).is_file() or (ROOT/relative).is_symlink():
                    errors.append('Integração incompleta: '+relative)
            empty_directories=()
        else:
            empty_directories=('.agents/skills',)
    else:
        empty_directories=('Automacao/project-bootstrap','Automacao/validacao-project-bootstrap','.agents/skills')
    for relative in empty_directories:
        if sorted(p.name for p in (ROOT/relative).iterdir())!=['.gitkeep']:
            errors.append('Automação/ativação implementada fora do escopo: '+relative)
    for root,dirs,files in os.walk(ROOT/'Skills'):
        dirs[:]=[d for d in dirs if d not in ('_repos','__pycache__')]
        for name in dirs+files:
            if (Path(root)/name).is_symlink():
                errors.append('Link simbólico na biblioteca: '+str(Path(root)/name))
    node_report={'status':'not_requested','files':len(node_files)}
    if node_syntax:
        previous_errors=len(errors)
        current=subprocess.check_output(['asdf','current','nodejs'],text=True)
        if str(Path.home()/'.tool-versions') not in current or 'true' not in current:
            raise ValueError('Node global asdf instalado não resolvido')
        node=subprocess.check_output(['asdf','which','node'],text=True).strip()
        for path in node_files:
            result=subprocess.run([node,'--check',str(path)],capture_output=True,text=True,timeout=30)
            if result.returncode:
                errors.append('Sintaxe JS: '+str(path.relative_to(ROOT))+': '+result.stderr[:300])
        node_report={'status':'passed' if len(errors)==previous_errors else 'failed','files':len(node_files),'execution':'syntax parsing only, vendor code not executed'}
    cache=source_validation(catalog,indexes) if origins else {'status':'not_required_for_distribution'}
    copy_report=verify_copies(catalog,packages,vendor_smoke=vendor_smoke) if copies and not errors else {'status':'not_requested' if not copies else 'blocked_by_integrity_errors'}
    checks.extend(['Revisões e proveniência de cada arquivo confrontadas com o lock e índices adquiridos.',
                   'Hashes, inventários completos, recursos, referências Markdown locais e licenças conferidos.',
                   'Planos de cópia fechados sobre dependências; nenhum SKILL.md pendente/excluído nos pacotes.',
                   'Adaptações explícitas com hashes antes/depois e unified diff.',
                   'Sem links simbólicos, caminhos locais ou dependência de cache nos pacotes.',
                   'Nenhuma ativação de agentes; estado do núcleo validado separadamente da biblioteca.'])
    return {'schema_version':2,'stage':'1.5','validated_at_utc':datetime.now(timezone.utc).isoformat(),
            'status':'failed' if errors else 'passed_with_documented_pending', 'python_executor':runtime,
            'counts':catalog['counts'],'package_files_verified':checked_files,'python_files_parsed':python_files,
            'node_syntax':node_report,'local_markdown_links_checked':local_links,'adapted_files':len(adapted),
            'cache_validation':cache,'physical_copy_test':copy_report,'checks':checks,'errors':errors,
            'limits':['Packaging approval does not certify agent discovery or all application workflows.',
                      'Consumer SDKs, hardware, authenticated services and CLIs were not provisioned or exercised.',
                      'Frontmatter delimiters/name/description and declared licence paths checked; not full YAML schema validation.'],
            'bootstrap_implemented':bool(core_state.get('core_implemented')),
            'bootstrap_core_stage':core_state.get('stage'),
            'agent_integration_tested':False,'production_ready':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--origens',action='store_true',help='Também confrontar os sete caches de aquisição')
    parser.add_argument('--copias',action='store_true',help='Testar planos físicos de todas as skills aprovadas e smoke tests UI/UX previamente analisados')
    parser.add_argument('--sintaxe-node',action='store_true',help='Parsear JS/CJS/MJS com Node global asdf, sem executar scripts')
    parser.add_argument('--sem-smoke-fornecedor',action='store_true',help='Com --copias, validar cópias sem executar buscas/scripts do fornecedor')
    args=parser.parse_args()
    try:
        result=validate(args.origens,args.copias,args.sintaxe_node,vendor_smoke=not args.sem_smoke_fornecedor)
    except (ValueError,OSError,subprocess.SubprocessError,SyntaxError) as exc:
        result={'status':'failed','errors':[str(exc)]}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    sys.exit(1 if result['errors'] else 0)


if __name__=='__main__':
    main()
