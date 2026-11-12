"""Inventário estático local. Não baixa, instala, ativa ou executa fornecedores."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import os
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
CATEGORIES = ('Frontend', 'Backend', 'Mobile', 'Seguranca', 'manutencao', 'validacao')


def git(repo, *args):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', GIT_NO_LAZY_FETCH='1')
    return subprocess.check_output(
        ['git', '-c', 'core.hooksPath=/dev/null', '-C', str(repo), *args],
        env=env, text=True).strip()


def require_asdf_python():
    """Exige Python global instalado e realmente usado; nenhuma instalação."""
    global_file = Path.home() / '.tool-versions'
    rows = [line.split('#', 1)[0].split() for line in global_file.read_text().splitlines()]
    versions = next((row[1:] for row in rows if row and row[0] == 'python'), [])
    if not versions or versions[0] == 'system':
        raise RuntimeError('Python global asdf ausente ou inválido')
    current = subprocess.check_output(['asdf', 'current', 'python'], text=True)
    if str(global_file) not in current or 'true' not in current:
        raise RuntimeError('Python não foi resolvido do arquivo global asdf instalado')
    resolved = Path(subprocess.check_output(['asdf', 'which', 'python'], text=True).strip())
    installed = Path(subprocess.check_output(['asdf', 'where', 'python', versions[0]], text=True).strip())
    if resolved.resolve() != Path(sys.executable).resolve() or not resolved.resolve().is_relative_to(installed.resolve()):
        raise RuntimeError('Executor não corresponde ao Python global do asdf')
    return {'manager': 'asdf', 'global_source': '~/.tool-versions', 'version': versions[0]}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frontmatter(text):
    if not text.startswith('---\n') or '\n---\n' not in text[4:]:
        raise ValueError('Frontmatter delimitado ausente')
    raw = text.split('---', 2)[1]
    values = {}
    for match in re.finditer(r'^([A-Za-z][\w-]*):[ \t]*(.*(?:\n[ \t]+[^\n]*)*)', raw, re.M):
        value = match.group(2).strip()
        values[match.group(1)] = value.strip('"\'')
    if not values.get('name') or not values.get('description'):
        raise ValueError('Nome/descrição ausentes')
    return values


def license_id(path):
    text = path.read_text(errors='replace')
    if 'SIL Open Font License' in text:
        return 'OFL-1.1'
    if 'creativecommons.org/licenses/by-sa/4.0' in text:
        return 'CC-BY-SA-4.0'
    if 'Apache License' in text:
        return 'Apache-2.0'
    if 'Permission is hereby granted, free of charge' in text:
        return 'MIT'
    return 'unidentified-see-file'


def category(source, name):
    if source['id'] == 'sentry':
        if name in {'claude-settings-audit','django-access-review','gha-security-review','secret-serialization','security-model','security-review','skill-scanner'}:
            return 'Seguranca'
        if name in {'code-review','find-bugs','typing-exclusion-worker'}:
            return 'validacao'
        if name in {'django-perf-review','document-api-endpoint'}:
            return 'Backend'
        if name == 'triage-frontend-issues':
            return 'Frontend'
        return 'manutencao'
    if source['id'] == 'android':
        if name.startswith('android-') and name.endswith('-security'):
            return 'Seguranca'
        if name == 'testing-setup':
            return 'validacao'
    if source['id'] == 'expo' and name == 'expo-skill-eval':
        return 'validacao'
    if source['id'] == 'chrisbanes':
        if name in {'android-benchmark-comparison','compose-ui-testing-patterns'}:
            return 'validacao'
        if not name.startswith(('compose-', 'kotlin-')):
            return 'manutencao'
    return source['source_category']


def inspect_references(repo, skill, files):
    """Heurística explícita: links Markdown e menções de recursos, sem abrir URLs."""
    checks = []
    required = set(files)
    pattern = r'(?<![\w./-])(?:references|scripts|assets|templates|data|agents)/[A-Za-z0-9_./+-]+\.(?:md|py|cjs|mjs|json|js|sh|csv|png|svg|toml|yaml|yml|txt|css|html|tsx|ts)(?![\w.])'
    for relative in files:
        p = repo / relative
        if p.suffix != '.md':
            continue
        raw = p.read_text(errors='replace')
        prose = re.sub(r'^```.*?^```[^\n]*', '', raw, flags=re.M | re.S)
        links = [(target, 'markdown') for target in re.findall(r'\[[^\]\n]*\]\(([^)\s]+)\)', prose)]
        mentions = [(target, 'resource_mention') for target in re.findall(pattern, raw)]
        for target, kind in sorted(set(links + mentions)):
            token = unquote(target.strip('<>').split('#', 1)[0])
            if not token or urlsplit(token).scheme or token.startswith('//'):
                continue
            record = {'document': relative, 'target': target, 'kind': kind}
            if token.lower() in {'url', 'path/to/screenshot'} or any(c in token for c in '{}<>*`'):
                record['status'] = 'example_or_dynamic'
            else:
                candidates = [p.parent / token, skill / token, repo / token]
                resolved = next((q.resolve() for q in candidates if q.exists() and q.resolve().is_relative_to(repo.resolve())), None)
                if resolved:
                    record.update(status='present', resolved=resolved.relative_to(repo.resolve()).as_posix())
                    if resolved.is_file():
                        required.add(record['resolved'])
                else:
                    record['status'] = 'unresolved_requires_review'
                    record['possible_matches'] = sorted(
                        q.relative_to(repo).as_posix() for q in repo.rglob(Path(token).name)
                        if '.git' not in q.relative_to(repo).parts and q.as_posix().endswith(token))
            checks.append(record)
    return checks, required


def build():
    runtime = require_asdf_python()
    lock = json.loads((ROOT / 'Skills/fontes.lock.json').read_text())
    sources, skills, indexes, reference_index, aliases = [], [], {}, {}, []
    for source in lock['sources']:
        repo = ROOT / source['directory']
        if git(repo, 'rev-parse', 'HEAD') != source['commit']:
            raise ValueError('Commit diverge do lock: ' + source['id'])
        if git(repo, 'status', '--porcelain', '--untracked-files=all'):
            raise ValueError('Origem modificada: ' + source['id'])
        source_files, gitlinks, sparse = [], [], []
        entries = git(repo, 'ls-files', '--stage', '-z').split('\0')
        file_index = []
        for entry in entries:
            if not entry:
                continue
            info, rel = entry.split('\t', 1)
            mode, oid, stage = info.split()
            p = repo / rel
            if mode == '160000':
                gitlinks.append({'path': rel, 'commit': oid, 'initialized': (p / '.git').exists()})
                continue
            if not os.path.lexists(p):
                sparse.append(rel)
                continue
            source_files.append(rel)
            record = {'path': rel, 'git_mode': mode, 'git_blob': oid}
            if p.is_symlink():
                record.update(type='symlink', target=os.readlink(p))
            else:
                record.update(type='file', size=p.stat().st_size, sha256=digest(p))
            file_index.append(record)
        indexes[source['id']] = {'files': file_index, 'sparse_omitted_paths': sparse}
        paths = sorted(p for p in source_files if Path(p).name == 'SKILL.md')
        canonical_paths = []
        for path in paths:
            if source['id'] == 'ui-ux-pro-max' and path.startswith('cli/assets/skills/'):
                canonical = path.replace('cli/assets/skills/', '.claude/skills/', 1)
                if not (repo / canonical).is_file():
                    raise ValueError('Cópia sem fonte canônica: ' + path)
                aliases.append({'source_id':source['id'], 'path':path, 'canonical_path':canonical,
                                'skill_md_identical':digest(repo/path)==digest(repo/canonical)})
            else:
                canonical_paths.append(path)
        source_record = dict(source, acquired=True, physical_skill_files=len(paths), canonical_skill_count=len(canonical_paths),
                             materialized_file_count=len(source_files), sparse_omitted_count=len(sparse), submodules=gitlinks,
                             documentation=[p for p in source_files if Path(p).name.lower().startswith('readme')],
                             license_files=[p for p in source_files if Path(p).name.upper().startswith(('LICENSE','COPYING','NOTICE')) or '-OFL.' in Path(p).name.upper()],
                             licensing_metadata=[p for p in source_files if 'license' in Path(p).name.lower() and Path(p).suffix=='.json'])
        sources.append(source_record)
        for path in canonical_paths:
            skill = (repo / path).parent
            text = (repo / path).read_text()
            fm = frontmatter(text)
            name = fm['name']
            identifier = source['id'] + ':' + name
            prefix = '' if skill == repo else skill.relative_to(repo).as_posix() + '/'
            files = sorted(p for p in source_files if p.startswith(prefix))
            licenses = []
            for parent in [skill, *skill.parents]:
                if not parent.is_relative_to(repo):
                    break
                for p in sorted(parent.iterdir()):
                    if p.is_file() and p.name.upper().startswith(('LICENSE','COPYING','NOTICE')):
                        licenses.append({'path':p.relative_to(repo).as_posix(), 'identified':license_id(p)})
            refs, required = inspect_references(repo, skill, files)
            required.update(item['path'] for item in licenses)
            reference_index[identifier] = refs
            pending = ['Validar compatibilidade com Codex, OpenCode/DeepSeek e Gemini CLI e plano de cópia antes de habilitar.']
            scope = 'catalogued_source'
            if source['id'] == 'ui-ux-pro-max':
                pending.append('Distribuição por templates e/ou dependências entre subskills: revisão de renderização e auditoria de scripts pendentes; não copiar versão Claude como adaptador universal.')
            if path.startswith('.claude/skills/expo-skill-eval/'):
                scope = 'internal_evaluation_not_distributable'
                pending.append('Ferramenta interna do fornecedor; eval-harness é submódulo não adquirido deliberadamente.')
            if path.startswith('plugins/expo-experiments/'):
                scope = 'experimental_source'
                pending.append('Plugin experimental; avaliar separadamente antes de seleção.')
            if source['id']=='expo' and name=='expo-overview':
                pending.append('O mapa da origem menciona expo-tailwind-setup, sem SKILL.md correspondente neste commit; não criar substituto.')
            unresolved = [r for r in refs if r['status'] == 'unresolved_requires_review']
            if unresolved:
                pending.append('Menções/links não resolvidos precisam distinguir recursos, exemplos e saídas de projetos consumidores.')
            if fm.get('license', '').upper() == 'LICENSE' and not (skill/'LICENSE').exists():
                pending.append('Frontmatter cita LICENSE local inexistente; licença da raiz preservada, referência requer esclarecimento.')
            evidence = [{'line':i, 'text':line.strip()} for i,line in enumerate(text.splitlines(),1)
                        if re.search(r'(?i)prerequisit|\brequires?\b|compatibility:|allowed-tools:|\bMCP\b|API.key|\buv run\b|\bpython3?\b|\bbun\b|\bnode\b|\bgh ',line)]
            item = {'id':identifier, 'name':name, 'description':fm['description'], 'source_id':source['id'],
                    'repository':source['url'], 'commit':source['commit'], 'source_path':path,
                    'source_root':source['directory'], 'category':category(source,name), 'source_category':source['source_category'],
                    'scope':scope, 'enabled':False, 'distribution_status':'not_prepared',
                    'frontmatter_fields':fm, 'license':{'identified':licenses[0]['identified'] if licenses else 'unknown', 'evidence':licenses,
                        'asset_licenses':[{'path':p,'identified':license_id(repo/p)} for p in files if '-OFL.' in Path(p).name.upper()],
                        'licensing_metadata':[p for p in files if 'license' in Path(p).name.lower() and Path(p).suffix=='.json'],
                        'scope_note':'Identificação do arquivo mais próximo; preservar todas as evidências. security-review tem referências CC-BY-SA-4.0 sob origem Apache-2.0.'},
                    'required_files':sorted(required), 'required_files_policy':'whole_skill_directory_plus_resolved_resources_and_ancestor_licenses_not_yet_a_copy_plan',
                    'resource_directories':sorted({p[len(prefix):].split('/')[0] for p in files if '/' in p[len(prefix):]}),
                    'script_files':[p for p in files if Path(p).suffix in {'.py','.js','.cjs','.mjs','.sh','.ts'}],
                    'dependency_evidence':evidence,
                    'validation':{'status':'static_inventory_only', 'frontmatter':'delimiters_name_description_only_not_full_yaml_validation',
                                  'required_files_present':True, 'resource_references':dict(Counter(r['status'] for r in refs)),
                                  'vendor_code_executed':False, 'compatibility_tested':False, 'copy_plan_complete':False},
                    'pending':pending}
            skills.append(item)
    # Menções de skills irmãs são evidência para a seleção futura, não seleção automática.
    for item in skills:
        text = (ROOT/item['source_root']/item['source_path']).read_text()
        mentioned = set(re.findall(r'`([a-z][a-z0-9-]+)`', text))
        item['sibling_skill_mentions'] = sorted(other['id'] for other in skills
            if other['source_id']==item['source_id'] and other['id']!=item['id'] and other['name'] in mentioned)
        if item['id']=='chrisbanes:implement-with-subagents':
            item['pending'].append('Modo de implementação depende de tdd externo (Matt Pocock), fora das sete origens; não adquirido.')
    counts = {'sources':len(sources), 'physical_skill_files':sum(s['physical_skill_files'] for s in sources),
              'catalogued_skills':len(skills), 'distribution_aliases':len(aliases), 'enabled_skills':0,
              'prepared_distribution_skills':0, 'by_category':dict(sorted(Counter(s['category'] for s in skills).items())),
              'by_scope':dict(sorted(Counter(s['scope'] for s in skills).items()))}
    catalog = {'schema_version':1, 'generated_at_utc':datetime.now(timezone.utc).isoformat(), 'stage':1,
               'bootstrap_implemented':False, 'python_executor':runtime, 'counts':counts,
               'reference_check_limit':'Static Markdown links and resource mentions; not a complete semantic dependency resolver or script audit. External URLs not tested.',
               'sources':sources, 'skills':skills, 'distribution_aliases':aliases}
    return catalog, indexes, reference_index


def main():
    current = json.loads((ROOT/'Skills/catalogo.json').read_text())
    if current.get('stage') != 1:
        raise SystemExit('Catálogo de distribuição existente: use preparar_biblioteca.py; inventariar.py não sobrescreve a Etapa 1.5.')
    catalog, indexes, references = build()
    # Nenhuma escrita ocorre antes de asdf, revisões e todas as fontes serem verificadas.
    for rel, data in [('Skills/catalogo.json',catalog), ('Skills/validacao/arquivos.json',indexes), ('Skills/validacao/recursos.json',references)]:
        (ROOT/rel).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    for category_name in CATEGORIES:
        rows = [s for s in catalog['skills'] if s['category'] == category_name]
        lines = ['# '+category_name, '', 'Índice gerado de `Skills/catalogo.json`. Fontes preservadas; nenhuma skill habilitada.', '',
                 '| Skill | Origem | Caminho canônico | Escopo |', '|---|---|---|---|']
        for item in rows:
            target = ROOT/item['source_root']/item['source_path']
            link = Path(os.path.relpath(target,ROOT/'Skills'/category_name)).as_posix()
            lines.append(f"| [{item['name']}]({link}) | {item['source_id']} | `{item['source_path']}` | {item['scope']} |")
        (ROOT/'Skills'/category_name/'README.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(catalog['counts'],ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
