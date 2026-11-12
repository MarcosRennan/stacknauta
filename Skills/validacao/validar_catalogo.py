"""Verificação local, offline e sem executar scripts das origens. Saída JSON."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'Skills/manutencao'))
from inventariar import CATEGORIES, build, digest, git, require_asdf_python


def validate():
    runtime = require_asdf_python()
    catalog = json.loads((ROOT/'Skills/catalogo.json').read_text())
    indexes = json.loads((ROOT/'Skills/validacao/arquivos.json').read_text())
    references = json.loads((ROOT/'Skills/validacao/recursos.json').read_text())
    errors, warnings, checks = [], [], []
    actual, actual_indexes, actual_refs = build()
    # Regeneração em memória detecta cadastro obsoleto e não escreve nada.
    actual['generated_at_utc'] = catalog['generated_at_utc']
    if catalog != actual or indexes != actual_indexes or references != actual_refs:
        errors.append('Inventário diverge das fontes/lock/classificação atuais.')
    else:
        checks.append('Catálogo e índices reproduzidos em memória, sem divergência.')
    expected_ids = {s['id'] for s in catalog['sources']}
    if git(ROOT,'remote'):
        errors.append('Git principal tem remoto configurado fora do escopo.')
    if len(expected_ids) != 7:
        errors.append('Quantidade de origens difere das sete origens aprovadas.')
    checked_files, checked_symlinks = 0, []
    for source in catalog['sources']:
        repo = ROOT/source['directory']
        if not repo.resolve().is_relative_to(ROOT.resolve()):
            errors.append('Origem fora do projeto: '+source['id'])
        if git(repo,'remote','get-url','origin') != source['url']:
            errors.append('URL remota divergente: '+source['id'])
        if git(repo,'branch','--show-current') != source['branch']:
            errors.append('Branch divergente: '+source['id'])
        if git(repo,'rev-parse','refs/remotes/origin/'+source['branch']) != source['commit']:
            errors.append('Referência de acompanhamento remoto divergente: '+source['id'])
        if git(repo,'rev-parse','--is-shallow-repository') != 'true':
            errors.append('Origem não é rasa: '+source['id'])
        git(repo,'fsck','--full','--no-dangling')
        for record in indexes[source['id']]['files']:
            path = repo/record['path']
            if record['type'] == 'symlink':
                target = os.readlink(path)
                if Path(target).is_absolute() or not path.resolve().is_relative_to(repo.resolve()) or not path.exists():
                    errors.append('Link absoluto, externo ou quebrado: '+str(path.relative_to(ROOT)))
                checked_symlinks.append({'source_id':source['id'],'path':record['path'],'target':target})
                data = target.encode()
            else:
                data = path.read_bytes()
                if hashlib.sha256(data).hexdigest() != record['sha256']:
                    errors.append('SHA-256 divergente: '+record['path'])
                checked_files += 1
            blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            if blob != record['git_blob']:
                errors.append('Conteúdo difere do blob Git original: '+source['id']+':'+record['path'])
            if ('/'+'App-Web'+'/').encode() in data or str(Path.home()).encode() in data:
                errors.append('Caminho da instalação anterior/local encontrado: '+source['id']+':'+record['path'])
        for module in source['submodules']:
            if module['initialized']:
                errors.append('Submódulo foi inicializado: '+source['id']+':'+module['path'])
        flags = {line[2:]:line[0] for line in git(repo,'ls-files','-v').splitlines()}
        for path in indexes[source['id']]['sparse_omitted_paths']:
            if flags.get(path) != 'S' or not source['sparse_paths']:
                errors.append('Arquivo omitido fora do sparse-checkout: '+source['id']+':'+path)
        for sparse_path in source['sparse_paths']:
            if not (repo/sparse_path/'SKILL.md').is_file():
                errors.append('Skill sparse não materializada: '+source['id'])
        checks.append('Origem íntegra, commit/URL/branch fixados e Git fsck concluído: '+source['id'])
    seen = set()
    for skill in catalog['skills']:
        if skill['id'] in seen:
            errors.append('ID duplicado: '+skill['id'])
        seen.add(skill['id'])
        if skill['category'] not in CATEGORIES or skill['enabled'] or skill['distribution_status'] != 'not_prepared':
            errors.append('Classificação ou habilitação indevida: '+skill['id'])
        repo = ROOT/skill['source_root']
        for relative in skill['required_files']:
            p = repo/relative
            if not p.is_file() or not p.resolve().is_relative_to(repo.resolve()):
                errors.append('Recurso necessário ausente/externo: '+skill['id']+':'+relative)
        if not skill['license']['evidence'] or skill['license']['identified'] in {'unknown','unidentified-see-file'}:
            warnings.append('Licença precisa de identificação: '+skill['id'])
        for ref in references[skill['id']]:
            if ref['status'] == 'present' and not (repo/ref['resolved']).exists():
                errors.append('Referência deixou de existir: '+skill['id']+':'+ref['resolved'])
    counts = catalog['counts']
    if counts['physical_skill_files'] != counts['catalogued_skills']+counts['distribution_aliases']:
        errors.append('Contagem de skills e cópias não fecha.')
    for alias in catalog['distribution_aliases']:
        if not alias['skill_md_identical']:
            errors.append('Cópia de distribuição diverge do canônico: '+alias['path'])
    for relative in ['Automacao/project-bootstrap','Automacao/validacao-project-bootstrap','.agents/skills']:
        contents = sorted(p.name for p in (ROOT/relative).iterdir())
        if contents != ['.gitkeep']:
            errors.append('Automação/ativação fora do escopo da Etapa 1: '+relative)
    own_files = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in {'.git','_repos','__pycache__'}]
        for name in files:
            p=Path(base)/name
            if p.is_symlink():
                errors.append('Link criado fora das origens: '+str(p.relative_to(ROOT)))
            own_files.append(p)
    forbidden = (str(Path.home()), '/'+'App-Web'+'/')
    for p in own_files:
        text = p.read_text(errors='replace')
        if any(token in text for token in forbidden):
            errors.append('Caminho local/legado em artefato próprio: '+str(p.relative_to(ROOT)))
    preservation_path = ROOT/'Skills/validacao/preservacao.json'
    preservation = json.loads(preservation_path.read_text()) if preservation_path.exists() else {}
    if preservation.get('status')!='unchanged' or preservation.get('baseline_sha256')!=preservation.get('after_sha256'):
        errors.append('Evidência de preservação legada ausente ou divergente.')
    else:
        checks.append('Relatório de preservação registra baseline e comparação final idênticos.')
    allrefs = [r for refs in references.values() for r in refs]
    unresolved = [r for r in allrefs if r['status']=='unresolved_requires_review']
    if unresolved:
        warnings.append(f'{len(unresolved)} menções de recursos aguardam interpretação; ver recursos.json e INSPECAO.md.')
    warnings.extend(['Compatibilidade de agentes, renderização UI/UX, dependências e execução de scripts não validadas.',
                     'Um submódulo de avaliação Expo preservado sem checkout; avaliação interna não disponível.',
                     'Fontes são clones locais ignorados pelo Git principal; preservar as pastas ao transportar esta instalação.'])
    checks.extend(['Todos os arquivos materializados comparados aos blobs Git originais e SHA-256.',
                   'Todos os SKILL.md reais contabilizados como canônicos ou cópias identificadas.',
                   'Todos os arquivos necessários catalogados estão fisicamente presentes.',
                   'Licenças da raiz e exceções locais preservadas por skill.',
                   'Links das origens relativos, internos e existentes; nenhum link criado para agentes.',
                   'Diretórios de automação e ativação contêm somente .gitkeep.',
                   'Nenhum caminho da instalação anterior ou diretório pessoal em recursos/artefatos próprios.'])
    return {'schema_version':1,'validated_at_utc':datetime.now(timezone.utc).isoformat(),
            'status':'failed' if errors else 'passed_with_documented_pending', 'python_executor':runtime,
            'counts':counts, 'source_files_verified':checked_files,'upstream_relative_symlinks':checked_symlinks,
            'legacy_preservation':preservation.get('status','missing'),
            'artifact_sha256':{relative:digest(ROOT/relative) for relative in ['Skills/fontes.lock.json','Skills/catalogo.json','Skills/validacao/arquivos.json','Skills/validacao/recursos.json','Skills/validacao/preservacao.json'] if (ROOT/relative).exists()},
            'resource_references':dict(Counter(r['status'] for r in allrefs)),
            'checks':checks,'errors':errors,'warnings':warnings,'bootstrap_implemented':False}


if __name__=='__main__':
    current=json.loads((ROOT/'Skills/catalogo.json').read_text())
    if current.get('stage')=='1.5':
        from validar_biblioteca import main
        main()
        raise SystemExit(0)
    result=validate()
    print(json.dumps(result,ensure_ascii=False,indent=2))
    sys.exit(1 if result['errors'] else 0)
