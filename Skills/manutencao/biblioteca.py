"""Formatos da biblioteca versionada; nenhuma aquisição ou criação de aplicações."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import re
from pathlib import Path, PurePosixPath

from inventariar import require_asdf_python

ROOT = Path(__file__).resolve().parents[2]
DOMAINS = ('Frontend', 'Backend', 'Mobile', 'Seguranca')
CONTRACT = '''## Execution contract

This is a physical StackNauta distribution, not an agent activation or an application bootstrap.
Resolve each skill's scripts and references from its SKILL.md directory. Keep the application's
working directory for project inputs and outputs. Shared resources and licences live in this bundle.

Before executing Python, Node.js, Java or Rust, resolve the **installed global asdf version** from
`~/.tool-versions`, confirm that `asdf current` selects that global file, and obtain the full executable
path with `asdf which`. A project override, missing version or missing installation must stop execution.
Use that verified executable for vendor command examples; never fall back to a system runtime,
install a runtime or auto-install a missing tool/dependency. For standard-library Python helpers,
invoke the verified Python directly instead of `uv run`. Do not execute shebangs implicitly.
Application SDKs, authenticated CLIs, hardware and services are prerequisites in the consumer's
environment, not supplied dependencies or authorization to install, publish, push or contact services.

Copy the closure recorded in catalogo.json: the selected skill, required companion skills, their
resources and the shared files. Preserve this layout and PROVENANCE.json. No symlinks are needed.
Named optional skills outside the supplied closure are unavailable: stop that optional workflow
instead of inventing or installing a replacement. Pending/internal/experimental skills are not supplied.
Agent integration and end-to-end application workflows are not certified by packaging approval.
'''
SKILL_CONTRACT = '''<!-- StackNauta: documented distribution adaptation; see PROVENANCE.json. -->
## StackNauta distribution

Before following vendor commands, read the [execution contract](../../README.md#execution-contract).
Script paths are relative to this skill's directory; project input/output paths remain project-relative.
Use only the verified installed global asdf runtimes. No system fallback or implicit installation.

'''


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode()


def safe_path(root, relative):
    parts = PurePosixPath(relative)
    if parts.is_absolute() or '..' in parts.parts or '\\' in relative:
        raise ValueError('Caminho inseguro: '+relative)
    path = root / relative
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('Caminho externo: '+relative)
    return path


def render_official(config, templates):
    """Semântica de renderSkillFile upstream (instalação local), somente stdlib.

    Não executa init/update/uninstall nem reproduz seus efeitos. A equivalência
    com o renderer oficial é testada separadamente com as quatro configurações.
    """
    content = (templates/'base/skill-content.md').read_text()
    qr = config['sections']['quickReference']
    drop, keep = ('NOQR','QR') if qr else ('QR','NOQR')
    content = re.sub(r'\{\{#'+drop+r'\}\}[\s\S]*?\{\{/'+drop+r'\}\}', '', content)
    content = re.sub(r'\{\{#'+keep+r'\}\}([\s\S]*?)\{\{/'+keep+r'\}\}', lambda m:m[1], content)
    reference = (templates/'base/quick-reference.md').read_text() if qr else ''
    front = ['---']
    for key, value in config['frontmatter'].items():
        if any(c in value for c in (':','"','\n')):
            value = '"'+value.replace('"','\\"')+'"'
        front.append(key+': '+value)
    front.extend(['---',''])
    substitutions = {'TITLE':config['title'], 'DESCRIPTION':config['description'],
                     'SCRIPT_PATH':re.sub(r'/{2,}', '/', config['folderStructure']['root']+'/'+config['scriptPath']),
                     'SKILL_OR_WORKFLOW':config['skillOrWorkflow'], 'QUICK_REFERENCE':'\n'+reference if reference else ''}
    for key, value in substitutions.items():
        content = content.replace('{{'+key+'}}', value)
    return '\n'.join(front)+content


def add_contract(text):
    if not text.startswith('---\n'):
        raise ValueError('SKILL.md sem frontmatter')
    end = text.index('\n---\n',4)+5
    return text[:end]+'\n'+SKILL_CONTRACT+text[end:].lstrip('\n')


def closure_for(identifier, skills):
    found, pending = set(), [identifier]
    while pending:
        current = pending.pop()
        if current in found:
            continue
        row = skills[current]
        if row['distribution_status'] != 'approved':
            raise ValueError('Dependência não aprovada: '+current)
        found.add(current)
        pending.extend(row['distribution']['requires_skills'])
    return sorted(found)


def selected_files(identifier, catalog, package):
    """Plano físico de um conjunto fechado dentro de UM pacote, sem executar nada."""
    skills = {s['id']:s for s in catalog['skills']}
    closure = closure_for(identifier, skills)
    key = skills[identifier]['distribution']['package']
    for current in closure:
        if skills[current]['distribution']['package'] != key:
            raise ValueError('Dependência entre pacotes precisa de plano explícito: '+current)
    prefixes = [skills[current]['distribution']['skill_directory']+'/' for current in closure]
    files = set(package['shared_files'])
    for relative in package['files']:
        if any(relative.startswith(prefix) for prefix in prefixes):
            files.add(relative)
    for current in closure:
        files.update(package.get('skill_extra_files',{}).get(current,[]))
    files.add('PROVENANCE.json')
    return sorted(files), closure
