"""Descoberta e incorporação individual; promoção/recuperação pertencem a Updates."""
import copy
import difflib
import json
import os
import posixpath
import re
import shutil
import subprocess
from pathlib import Path

from atualizacoes import atomic_json, load, read_bytes, write_bytes, move, safe, tree, sha, json_bytes, NODE_BUILTINS
from stacknauta_core.filesystem import directory
from atualizacao_receita import inventory, source_bytes, skill_prefix, recount, python_dependencies, relative_python_resources, javascript_imports, category_indexes
from origens import parse_url, resolve
from stacknauta_core import BootstrapError
from stacknauta_core.compatibility import declared_policy, policies, catalog_policies
from stacknauta_core.config import load as load_decisions, keys, strings
from stacknauta_core.runtimes import AsdfResolver


class Inclusions:
    def __init__(self, engine):
        self.engine=engine

    def add(self, url, *, revision=None, path=None, source_id=None):
        e=self.engine
        parsed=parse_url(url, allow_local=e.git.allow_local)
        sources=e.sources()
        existing=next((s for s in sources if parse_url(s['url'],allow_local=e.git.allow_local)['identity']==parsed['identity']),None)
        source=resolve(e.git,parsed,revision=revision,path=path,existing=existing)
        if existing and source_id and source_id!=existing['id']: raise ValueError('Origem já cadastrada; não criar um segundo identificador')
        generated=re.sub(r'[^a-z0-9]+','-',('gh-'+parsed['owner']+'-'+parsed['repo']).lower()).strip('-')
        if len(generated)>120: generated=generated[:100].rstrip('-')+'-'+sha(parsed['identity'].encode())[:12]
        identifier=existing['id'] if existing else source_id or generated
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',identifier) or len(identifier)>120: raise ValueError('ID de origem inválido; use --source-id com um slug')
        if not existing and any(s['id']==identifier for s in sources): raise ValueError('ID de origem já utilizado; informe --source-id distinto')
        scope=source.pop('requested_path',None)
        if scope and Path(scope).name=='SKILL.md': scope=Path(scope).parent.as_posix();scope=None if scope=='.' else scope
        source.update(id=identifier,directory=existing['directory'] if existing else 'Skills/_repos/'+identifier,
                      source_category=existing['source_category'] if existing else None,
                      acquisition='shallow-depth-1-no-checkout-manual-materialization')
        source['sparse_paths']=([] if existing and not existing.get('sparse_paths') else sorted(set(source.get('sparse_paths',[])) | {scope})) if scope else source.get('sparse_paths',[])
        with e.exclusive():
            session,inspection,head,baseline=e.begin()
            try:
                e.git.acquire(source,safe(inspection,source['directory']),discover=bool(existing and not scope))
                acquired=safe(inspection,source['directory'])
                if scope and not safe(acquired,scope).is_dir(): raise ValueError('Subdiretório solicitado ausente ou não regular')
                if (parsed['kind']=='blob' or (path and Path(path).name=='SKILL.md')) and not (acquired/(scope or '')/'SKILL.md').is_file():
                    raise ValueError('SKILL.md solicitado ausente')
                lock=load(inspection,'Skills/fontes.lock.json')
                lock['sources']=[source if s['id']==identifier else s for s in lock['sources']]
                if not existing: lock['sources'].append(source)
                write_bytes(inspection,'Skills/fontes.lock.json',json_bytes(lock))
                raw,indexes,refs=inventory(inspection,{identifier},read_bytes,e.runtime,e.git.run)
                records={r['path']:r for r in indexes[identifier]['files']}
                for p,r in records.items():
                    if r['type']=='file': source_bytes(inspection,source,records,p,read_bytes)
                catalog=load(e.root,'Skills/catalogo.json');old={s['id']:s for s in catalog['skills']}
                if not raw['skills']: raise ValueError('Nenhum SKILL.md válido encontrado no escopo adquirido')
                candidates=[]
                for skill in raw['skills']:
                    previous=old.get(skill['id'])
                    if previous and previous['source_path']!=skill['source_path']: raise ValueError('ID existente com outro caminho: '+skill['id'])
                    if previous and previous['distribution_status']=='approved': continue
                    if previous and scope and not skill['source_path'].startswith(scope+'/'): continue
                    candidates.append(self.analyze(inspection,source,skill,raw['skills'],records,refs,catalog))
                # Preservar a inspeção e cache; o candidato promovível será separado.
                move(inspection,session/'inspection')
                identity={'schema_version':1,'head':head,'baseline':baseline,'source':source,'lock':lock,'scope':scope,
                          'raw':raw,'indexes':indexes,'references':refs,'candidates':candidates,'existing_source':bool(existing)}
                report={**identity,'review_id':sha(json_bytes(identity)),'session_id':session.name,
                        'status':'descoberto' if candidates else 'sem_novas_candidatas','active_library_modified':False}
                atomic_json(session/'analysis.json',report)
                return self.view(report)
            except (ValueError,OSError,SyntaxError,BootstrapError,subprocess.SubprocessError) as exc:
                result={'status':'bloqueado','session_id':session.name,'motivo':str(exc),'promovidas':[]}
                atomic_json(session/'blocked.json',result);return result

    def analyze(self, root, source, skill, siblings, records, refs, catalog):
        from inventariar import inspect_references
        prefix=skill_prefix(skill['source_path']);files={p for p in records if p.startswith(prefix)}
        blockers=[]; dependencies=set(skill['sibling_skill_mentions'])
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',skill['name']) or len(skill['name'])>64: blockers.append('Nome inválido; adaptação manual necessária')
        if len('stacknauta-'+skill['name'])>64: blockers.append('Nome excede o limite do alias portátil existente; adaptação manual necessária')
        if not re.fullmatch(r'[A-Za-z0-9_./-]+',skill['source_path']): blockers.append('Caminho de SKILL.md exige adaptação para os links portáteis existentes')
        if sum(s['id']==skill['id'] for s in siblings)>1: blockers.append('Identificador duplicado na origem')
        for other in siblings:
            if other['source_path']!=skill['source_path'] and other['source_path'].startswith(prefix): dependencies.add(other['id'])
        # Fechamento de referências de documentos externos, sem executar recursos.
        all_refs=[]
        for _ in range(128):
            found,required=inspect_references(root/source['directory'],root/source['directory']/Path(skill['source_path']).parent,sorted(files))
            all_refs=found;expanded=files | required
            for item in found:
                if item['status']=='present':
                    resolved=item['resolved']
                    if resolved not in records: expanded.update(p for p in records if p.startswith(resolved+'/'))
            for path in files:
                if path not in records or records[path]['type']!='file': continue
                data=source_bytes(root,source,records,path,read_bytes)
                targets=[]
                if Path(path).suffix in {'.js','.mjs','.cjs'}:
                    for specifier in javascript_imports(data):
                        if specifier.removeprefix('node:') in NODE_BUILTINS: continue
                        if not specifier.startswith(('./','../')): blockers.append('Dependência JavaScript externa exige análise específica: '+specifier);continue
                        base=posixpath.normpath(posixpath.join(posixpath.dirname(path),specifier))
                        targets.append([base,*[base+ext for ext in ('.js','.mjs','.cjs','.json')],*[base+'/index'+ext for ext in ('.js','.mjs','.cjs')]])
                if Path(path).suffix=='.py':
                    try:
                        expanded.update(relative_python_resources(data,path,
                            [p for p,r in records.items() if r['type']=='file'],
                            lambda p: source_bytes(root,source,records,p,read_bytes)))
                    except SyntaxError as exc: blockers.append('Sintaxe Python inválida: '+str(exc))
                    except ValueError as exc: blockers.append(str(exc))
                for alternatives in targets:
                    target=next((p for p in alternatives if p in records and records[p]['type']=='file'),None)
                    if target is None: blockers.append('Dependência local ausente/fora do escopo: '+alternatives[0])
                    else: expanded.add(target)
            if expanded==files: break
            files=expanded
        else: blockers.append('Fechamento de recursos excessivamente profundo')
        files.update(r['path'] for r in skill['license']['evidence'])
        if skill['license']['identified'] not in {'MIT','Apache-2.0','CC-BY-SA-4.0','OFL-1.1'}: blockers.append('Licença ausente ou não identificada')
        if any(r['identified'] not in {'MIT','Apache-2.0','CC-BY-SA-4.0','OFL-1.1'} for r in skill['license']['asset_licenses']): blockers.append('Licença específica de asset não identificada')
        declared=skill['frontmatter_fields'].get('license','')
        for license_id in ('MIT','Apache-2.0','CC-BY-SA-4.0','OFL-1.1'):
            if re.search(r'(?<![\w-])'+re.escape(license_id)+r'(?![\w-])',declared) and license_id!=skill['license']['identified']:
                blockers.append('Licença declarada incompatível com a evidência')
        if any(r['status']=='unresolved_requires_review' for r in all_refs): blockers.append('Recursos/referências ausentes ou fora do escopo adquirido')
        if skill['scope']!='catalogued_source' or any(p in {'internal','experimental','experiments','eval','evals'} for p in Path(skill['source_path']).parts):
            blockers.append('Conteúdo interno/experimental exige análise específica')
        for path in files:
            if path not in records or records[path]['type']!='file': blockers.append('Recurso não físico ou ausente: '+path);continue
            for other in siblings:
                other_prefix=skill_prefix(other['source_path'])
                if other['id']!=skill['id'] and (path==other['source_path'] or (other_prefix and path.startswith(other_prefix) and not path.startswith(prefix))): dependencies.add(other['id'])
        local={Path(p).stem for p in files if p.endswith('.py')}
        for path in files:
            if path in records and records[path]['type']=='file' and path.endswith('.py'):
                try: python_dependencies(b'',source_bytes(root,source,records,path,read_bytes),local)
                except (ValueError,SyntaxError) as exc: blockers.append(str(exc))
        # Comparar nomes e bytes originais, não apenas o texto adaptado distribuído.
        conflicts=[s['id'] for s in catalog['skills'] if s['name']==skill['name'] and s['id']!=skill['id']]
        old_indexes=load(self.engine.root,'Skills/validacao/arquivos.json')
        content_duplicates=[]
        current=records[skill['source_path']].get('sha256')
        text=source_bytes(root,source,records,skill['source_path'],read_bytes).decode() if current else ''
        if source['id']=='ui-ux-pro-max' or re.search(r'\{\{[#/A-Z_]',text): blockers.append('Distribuição exige renderização/adaptação específica; não fabricar uma skill genérica')
        if re.search(r'\b(?:curl|wget)\b[^\n]*\|\s*(?:bash|sh|zsh)\b',text): blockers.append('Instalação remota por pipe exige adaptação e revisão manual')
        for old in catalog['skills']:
            row=next((r for r in old_indexes[old['source_id']]['files'] if r['path']==old['source_path']),{})
            if current and old['id']!=skill['id'] and row.get('sha256')==current: content_duplicates.append(old['id'])
        if content_duplicates: blockers.append('Conteúdo já catalogado: '+', '.join(content_duplicates))
        return {'id':skill['id'],'name':skill['name'],'description':skill['description'],'repository':source['url'],
                'commit':source['commit'],'source_path':skill['source_path'],'proposed_category':skill['category'],
                'current_status':next((s['distribution_status'] for s in catalog['skills'] if s['id']==skill['id']),'pending'),
                'license':skill['license'],'resources':sorted(files),'dependencies':sorted(dependencies),
                'dependency_evidence':skill['dependency_evidence'],'conflicts':conflicts,
                'reference_checks':all_refs,
                'script_files':sorted(p for p in files if Path(p).suffix in {'.py','.js','.cjs','.mjs','.sh','.ts','.tsx','.rb','.ps1'}),
                'content_duplicates':content_duplicates,'blockers':sorted(set(blockers)),'enabled':False}

    def view(self, report):
        result={k:copy.deepcopy(report[k]) for k in ('status','session_id','review_id','source','scope','candidates','existing_source','active_library_modified')}
        current={s['id']:s for s in load(self.engine.root,'Skills/catalogo.json')['skills']}
        for c in result['candidates']:
            c['discovery_status']=c['current_status']
            c['current_status']=current.get(c['id'],{}).get('distribution_status','pending')
        return result

    def analysis(self, identifier):
        session=self.engine.session(identifier);report=load(session,'analysis.json')
        identity={k:v for k,v in report.items() if k not in {'review_id','session_id','status','active_library_modified'}}
        if sha(json_bytes(identity))!=report['review_id']: raise ValueError('Inspeção alterada após descoberta')
        if report['session_id']!=identifier: raise ValueError('ID de inspeção divergente')
        return session,report

    def review(self, identifier=None, *, decisions=None, review_id=None):
        if identifier is None:
            if decisions: raise ValueError('Informe a sessão de descoberta para preparar decisões')
            cat=load(self.engine.root,'Skills/catalogo.json');sessions=[]
            folder=safe(self.engine.root,'.stacknauta-updates')
            if folder.exists():
                with directory(folder) as fd: names=sorted(os.listdir(fd))
                for name in names:
                    if re.fullmatch(r'[0-9a-f]{32}',name):
                        try: _,report=self.analysis(name)
                        except FileNotFoundError: continue
                        sessions.append({'session_id':name,'review_id':report['review_id'],'status':report['status'],'candidates':len(report['candidates'])})
            return {'status':'revisao','sessions':sessions,'skills':[{k:s.get(k) for k in ('id','name','repository','commit','category','description','license','distribution_status','pending','compatibility','required_files','script_files','dependency_evidence','distribution')} for s in cat['skills']]}
        session,report=self.analysis(identifier)
        if decisions is None: return self.view(report)
        if review_id!=report['review_id']: raise ValueError('Preparação exige --review-id da descoberta revisada')
        raw_decisions=load_decisions(decisions)
        keys(raw_decisions,{'schema_version','skills'},'decisões')
        if type(raw_decisions.get('schema_version')) is not int or raw_decisions.get('schema_version')!=1 or not isinstance(raw_decisions.get('skills'),dict): raise ValueError('Decisões exigem schema_version 1 e skills por ID')
        if (session/'plan.json').exists():
            plan=load(session,'plan.json')
            if plan['details'].get('decisions_sha256')!=sha(json_bytes(raw_decisions)): raise ValueError('Sessão já selada com outras decisões; execute add novamente')
            return plan
        e=self.engine
        with e.exclusive():
            if e.clean()!=report['head'] or e.tracked()!=report['baseline']: raise ValueError('Git/arquivos mudaram desde a descoberta')
            inspection=safe(session,'inspection')
            if load(inspection,'Skills/fontes.lock.json')!=report['lock']: raise ValueError('Lock da inspeção alterado')
            raw,indexes,refs=inventory(inspection,{report['source']['id']},read_bytes,e.runtime,e.git.run)
            if indexes!=report['indexes'] or refs!=report['references'] or raw['skills']!=report['raw']['skills']:
                raise ValueError('Origem/recursos alterados após descoberta')
            choices=self.validate_decisions(report,raw_decisions)
            candidate=safe(session,'candidate');e.copy_snapshot(candidate,report['baseline'])
            try:
                outputs,details=self.package(inspection,candidate,report,choices,raw_decisions)
                for relative,data in outputs.items():
                    write_bytes(candidate,relative,data)
                e.check_changed_scripts(candidate,outputs,report['baseline'])
                validation=e.validator(candidate)
                checks=[{'origem':report['source']['id'],'branch':report['source']['branch'],'atual':report['source']['commit'] if report['existing_source'] else None,
                         'disponivel':report['source']['commit'],'estado':'inclusao_revisada'}]
                return e.finish(session,candidate,report['head'],report['baseline'],checks,details,validation)
            except (ValueError,OSError,SyntaxError,BootstrapError,subprocess.SubprocessError) as exc:
                blocked={'status':'bloqueado','session_id':identifier,'motivo':str(exc),'promovidas':[]}
                atomic_json(session/'blocked.json',blocked);return blocked

    def validate_decisions(self, report, document):
        candidates={c['id']:c for c in report['candidates']}
        if len(candidates)!=len(report['candidates']): raise ValueError('IDs duplicados impedem incorporação; origem precisa de correção')
        keys(document['skills'],set(candidates),'IDs nas decisões')
        choices={}
        for identifier,decision in document['skills'].items():
            keys(decision,{'status','category','reason','compatibility','prerequisites_review','requires_skills','conflicts_acknowledged'},'decisão '+identifier)
            if decision.get('status') not in {'approved','pending','excluded'} or not isinstance(decision.get('reason'),str) or not decision['reason'].strip():
                raise ValueError('Cada decisão exige status e justificativa explícitos')
            c=candidates[identifier];category=decision.get('category',c['proposed_category'])
            category='Seguranca' if category=='Segurança' else category
            if category is not None and category not in {'Frontend','Backend','Mobile','Seguranca'}: raise ValueError('Categoria fora das quatro categorias permitidas')
            decision={**decision,'category':category}
            if decision['status']=='approved':
                if category is None: raise ValueError('Classificação explícita obrigatória: '+identifier)
                if c['blockers']: raise ValueError(identifier+': '+ '; '.join(c['blockers']))
                current={s['id']:s for s in load(self.engine.root,'Skills/catalogo.json')['skills']}
                if any(current[i]['distribution_status']=='approved' for i in c['conflicts']):
                    raise ValueError('Conflitos de nomes aprovados impedem aliases portáteis únicos: '+identifier)
                if set(strings(decision.get('conflicts_acknowledged',[]),'conflitos revisados'))!=set(c['conflicts']): raise ValueError('Conflitos de nomes precisam de revisão explícita: '+identifier)
                policy=declared_policy(decision.get('compatibility'))
                if policy['blocked']: raise ValueError('Restrição de compatibilidade não resolvida: '+identifier)
                if identifier in policies() and policy!=policies()[identifier]: raise ValueError('Não substituir regra de compatibilidade legada')
                missing=[tool for tool in policy['tools'] if not shutil.which(tool)]
                if missing: raise ValueError('Ferramentas ausentes; manter pendente: '+', '.join(missing))
                if policy['runtimes']: AsdfResolver(Path.home()).resolve([],extra_plugins=policy['runtimes'])
                evidence={d['text'] for d in c['dependency_evidence']}
                review=decision.get('prerequisites_review',{})
                keys(review,evidence,'revisão de pré-requisitos')
                if set(review)!=evidence: raise ValueError('Todos os pré-requisitos exigem mapeamento/revisão explícita')
                for text,mapping in review.items():
                    keys(mapping,{'tools','runtimes','reason'},'pré-requisito')
                    tools=strings(mapping.get('tools',[]),'ferramentas do pré-requisito')
                    runtimes=strings(mapping.get('runtimes',[]),'runtimes do pré-requisito')
                    if set(tools)-policy['tools'] or set(runtimes)-policy['runtimes'] or not isinstance(mapping.get('reason'),str) or not mapping['reason'].strip():
                        raise ValueError('Pré-requisito precisa de justificativa e condições presentes na compatibilidade')
                requires=strings(decision.get('requires_skills',[]),'skills obrigatórias')
                if set(requires)!=set(c['dependencies']): raise ValueError('Dependências entre skills exigem aprovação e fechamento explícitos')
            choices[identifier]=decision
        selected={i for i,d in choices.items() if d['status']=='approved'}
        old={s['id']:s for s in load(self.engine.root,'Skills/catalogo.json')['skills']}
        for identifier in selected:
            for dependency in choices[identifier].get('requires_skills',[]):
                if dependency not in selected and old.get(dependency,{}).get('distribution_status')!='approved':
                    raise ValueError('Dependência ainda pendente: '+dependency)
        return choices

    def package(self, inspection, candidate, report, choices, document):
        from biblioteca import CONTRACT, add_contract
        cat=load(candidate,'Skills/catalogo.json');policy=load(candidate,'Skills/manutencao/distribuicao-politica.json')
        indexes=load(candidate,'Skills/validacao/arquivos.json');refs=load(candidate,'Skills/validacao/recursos.json');patches=load(candidate,'Skills/validacao/adaptacoes.json')
        source=report['source'];sid=source['id'];raw=report['raw'];records={r['path']:r for r in report['indexes'][sid]['files']}
        outputs={};packages={};affected=[];old={s['id']:s for s in cat['skills']};decisions={r['id']:r for r in policy['rows']}
        def read(path):return source_bytes(inspection,source,records,path,read_bytes)
        def put(package,path,data,origin=None,reason=None,before=None):
            target=package['directory']+'/'+path;safe(candidate,target)
            record={'sha256':sha(data),'size':len(data),'mode':'100644','inputs':[{'path':origin,'sha256':sha(read(origin))}] if origin else [],'adaptation':reason,'origin':'vendor' if origin else 'StackNauta'}
            if path in package['files']:
                existing=outputs.get(target,read_bytes(candidate,target) if (candidate/target).exists() else None)
                if existing!=data: raise ValueError('Colisão de recursos: '+target)
                return
            package['files'][path]=record;outputs[target]=data
            if reason:
                patches.append({'package':package['id'],'path':path,'reason':reason,'before_sha256':sha(before),'after_sha256':sha(data),
                                'diff':''.join(difflib.unified_diff(before.decode().splitlines(True),data.decode().splitlines(True),fromfile='upstream',tofile='distribution'))})
        for c in report['candidates']:
            original=next(s for s in raw['skills'] if s['id']==c['id']);previous=old.get(c['id'])
            d=choices.get(c['id'])
            if previous and d is None: continue
            d=d or {'status':'pending','category':c['proposed_category'] if c['proposed_category'] in {'Frontend','Backend','Mobile','Seguranca'} else None,'reason':'Descoberta nova; análise, classificação e aprovação individual pendentes.'}
            row=copy.deepcopy(original)
            row['required_files']=c['resources']
            row['required_files_policy']='whole_skill_directory_plus_closed_static_resources_and_licenses'
            row.update(acquisition_category=row['category'],category=d['category'],acquisition_validation=row.pop('validation'),
                       distribution_status=d['status'],decision_reason=d['reason'],pending=[] if d['status']=='approved' else [d['reason'],*c['blockers']],distribution=None,
                       validation={'status':'packaged' if d['status']=='approved' else 'not_distributed','copy_plan_complete':d['status']=='approved','enabled':False,'agent_integration_tested':False,'vendor_workflow_certified':False},
                       inclusion_review={'review_id':report['review_id'],'decision':d,'origin_commit':source['commit']})
            if d['status']=='approved':
                row['compatibility']=d['compatibility']
                key=d['category']+'/'+sid
                descriptor=next((p for p in cat['distribution_packages'] if p['id']==key),None)
                if descriptor:
                    existing_package=load(candidate,descriptor['directory']+'/PROVENANCE.json')
                    if existing_package.get('layout')!='source-relative-v1': key+='-adicionais'
                if key not in packages:
                    descriptor=next((p for p in cat['distribution_packages'] if p['id']==key),None)
                    package=load(candidate,descriptor['directory']+'/PROVENANCE.json') if descriptor else {'id':key,'directory':'Skills/'+key,'source_id':sid,'repository':source['url'],'commit':source['commit'],'skills':[],'files':{},'shared_files':[],'skill_extra_files':{},'layout':'source-relative-v1'}
                    if package['source_id']!=sid or package.get('layout')!='source-relative-v1' or package['commit']!=source['commit']: raise ValueError('Colisão de identidade/layout/revisão de pacote')
                    packages[key]=package
                package=packages[key];package['skills'].append(row['id'])
                parent=Path(row['source_path']).parent.as_posix();directory='vendor'+('/'+parent if parent!='.' else '')
                row['distribution']={'package':key,'skill_directory':directory,'requires_skills':d.get('requires_skills',[]),'runtime_requirements':row['dependency_evidence'],'application_requirements_not_installed':True}
                package['skill_extra_files'][row['id']]=[]
                for path in c['resources']:
                    data=read(path);before=data;target='vendor/'+path;reason=None
                    if Path(path).name=='SKILL.md':
                        if path!=row['source_path']: continue  # Companheira somente pela própria aprovação.
                        text=data.decode()
                        declared=row['frontmatter_fields'].get('license','')
                        if declared and re.search(r'(?:^|\s)LICENSE(?:\.txt)?$',declared) and not (inspection/source['directory']/Path(row['source_path']).parent/declared.split()[-1]).is_file():
                            license_path=row['license']['evidence'][0]['path']
                            text=text.replace('license: '+declared,'license: '+declared.replace(declared.split()[-1],posixpath.relpath('vendor/'+license_path,directory)),1)
                        text=add_contract(text).replace('../../README.md#execution-contract',posixpath.relpath('README.md',directory)+'#execution-contract',1)
                        data=text.encode();reason='Contrato explícito de distribuição/asdf e caminhos relativos para README/licença; layout de origem preservado.'
                    put(package,target,data,path,reason,before)
                    if not path.startswith(skill_prefix(row['source_path'])): package['skill_extra_files'][row['id']].append(target)
                for evidence in row['license']['evidence']:
                    target='vendor/'+evidence['path']
                    if target not in package['files']: put(package,target,read(evidence['path']),evidence['path'])
                    package['shared_files'].append(target)
                affected.append(key)
            old[row['id']]=row
            decisions[row['id']]={'id':row['id'],'status':row['distribution_status'],'category':row['category'],'bundle':sid,'reason':row['decision_reason']}
        # Dependências só entre skills aprovadas no mesmo pacote, sem inferência de aprovação.
        for row in old.values():
            if row.get('distribution') and row['distribution']['package'] in packages:
                for identifier in row['distribution']['requires_skills']:
                    other=old.get(identifier)
                    if not other or not other.get('distribution') or other['distribution']['package']!=row['distribution']['package']:
                        raise ValueError('Dependência entre pacotes não suportada; manter pendente: '+identifier)
        for key,package in packages.items():
            package['skills']=sorted(set(package['skills']));package['shared_files']=sorted(set(package['shared_files'])|{'README.md'})
            # README é gerado e evolui quando o conjunto de skills aumenta.
            package['files'].pop('README.md',None)
            text='# '+key+'\n\n'+CONTRACT+'\n## Included skills\n\n'+'\n'.join('- `'+identifier+'`' for identifier in package['skills'])+'\n\n## Provenance\n\n'+source['url']+' at `'+source['commit']+'`.\n'
            put(package,'README.md',text.encode())
            outputs[package['directory']+'/PROVENANCE.json']=json_bytes(package)
            descriptor={'id':key,'directory':package['directory'],'skills':package['skills'],'manifest_sha256':sha(outputs[package['directory']+'/PROVENANCE.json'])}
            cat['distribution_packages']=[p for p in cat['distribution_packages'] if p['id']!=key]+[descriptor]
        cat['skills']=list(old.values());policy['rows']=list(decisions.values())
        merged={r['path']:r for r in indexes.get(sid,{}).get('files',[])}
        for path,record in records.items():
            if path in merged and record!=merged[path]: raise ValueError('Aquisição diverge da revisão já registrada: '+path)
            merged[path]=record
        omitted=set(indexes.get(sid,{}).get('sparse_omitted_paths',[])) | set(report['indexes'][sid]['sparse_omitted_paths'])
        indexes[sid]={'files':[merged[p] for p in sorted(merged)],'sparse_omitted_paths':sorted(omitted-set(merged))}
        refs.update(report['references'])
        cat['distribution_aliases']=[a for a in cat['distribution_aliases'] if a['source_id']!=sid]+raw['distribution_aliases']
        record=copy.deepcopy(raw['sources'][0]);record.update(physical_skill_files=sum(Path(p).name=='SKILL.md' for p in merged),canonical_skill_count=sum(s['source_id']==sid for s in cat['skills']),materialized_file_count=len(merged),sparse_omitted_count=len(indexes[sid]['sparse_omitted_paths']))
        cat['sources']=[record if s['id']==sid else s for s in cat['sources']]
        if not report['existing_source']: cat['sources'].append(record)
        cat['python_executor']=self.engine.runtime;recount(cat);catalog_policies(cat['skills'])
        outputs.update({'Skills/fontes.lock.json':json_bytes(report['lock']),'Skills/manutencao/distribuicao-politica.json':json_bytes(policy),
                        'Skills/validacao/arquivos.json':json_bytes(indexes),'Skills/validacao/recursos.json':json_bytes(refs),'Skills/validacao/adaptacoes.json':json_bytes(patches)})
        cat['generation'].update(tool='Automacao/manutencao-skills/inclusoes.py',tool_sha256=sha(read_bytes(candidate,'Automacao/manutencao-skills/inclusoes.py')),
                                 policy_sha256=sha(outputs['Skills/manutencao/distribuicao-politica.json']),source_lock_sha256=sha(outputs['Skills/fontes.lock.json']))
        outputs['Skills/catalogo.json']=json_bytes(cat)
        outputs.update(category_indexes(cat,{s['category'] for s in cat['skills'] if s['source_id']==sid and s['id'] in candidates_ids(report)}))
        return outputs,{'operation':'inclusion','review_id':report['review_id'],'decisions_sha256':sha(json_bytes(document)),
                        'affected_packages':sorted(set(affected)),'new_skills_pending':[i for i in candidates_ids(report) if old[i]['distribution_status']=='pending'],
                        'approved':[i for i,d in choices.items() if d['status']=='approved'],'excluded':[i for i,d in choices.items() if d['status']=='excluded']}


def candidates_ids(report): return [c['id'] for c in report['candidates']]
