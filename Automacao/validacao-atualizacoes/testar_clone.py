"""Clone local sem cache, repetindo testes sem executar scripts de fornecedores."""
import sys
sys.dont_write_bytecode = True
import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'Automacao/project-bootstrap'))
from stacknauta_core.runtimes import AsdfResolver


def run(command, cwd, *, structured=True):
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=240,
                            env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', GIT_OPTIONAL_LOCKS='0',
                                     GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1'))
    if result.returncode:
        raise RuntimeError(result.stdout + '\n' + result.stderr)
    return json.loads(result.stdout) if structured else result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    runtime = AsdfResolver(Path.home()).resolve([])['python']
    git = ['git', '-c', 'core.hooksPath=/dev/null', '-c', 'core.fsmonitor=false']
    if run([*git, 'status', '--porcelain', '--untracked-files=all'], ROOT, structured=False):
        raise RuntimeError('Commit candidato e árvore limpa são obrigatórios')
    commit = run([*git, 'rev-parse', 'HEAD'], ROOT, structured=False)
    base = Path(tempfile.mkdtemp(prefix='stacknauta-3a-clone-'))
    clone = base / 'StackNauta'
    run([*git, 'clone', '--quiet', '--no-hardlinks', '--no-recurse-submodules', str(ROOT), str(clone)], base, structured=False)
    run([*git, 'remote', 'remove', 'origin'], clone, structured=False)
    assert not (clone / 'Skills/_repos').exists()
    assert not (clone / '.git/objects/info/alternates').exists()
    results = {}
    for key, script in (
        ('nucleo', 'Automacao/validacao-project-bootstrap/executar_testes.py'),
        ('integracao', 'Automacao/validacao-integracao-agentes/executar_testes.py'),
        ('atualizacoes', 'Automacao/validacao-atualizacoes/executar_testes.py'),
        ('biblioteca', 'Skills/validacao/validar_biblioteca.py'),
    ):
        extra = ['--sintaxe-node'] if key == 'biblioteca' else []
        results[key] = run([sys.executable, '-I', '-S', '-B', str(clone / script), *extra], base)
    closure_code = (
        "import sys,json;from pathlib import Path;root=Path(sys.argv[1]);"
        "sys.path[:0]=[str(root/'Automacao/manutencao-skills'),str(root/'Skills/manutencao')];"
        "from atualizacoes import Updates;"
        "print(json.dumps(Updates(root,runtime={}).validate(root)))"
    )
    results['fechamentos'] = run([sys.executable, '-I', '-S', '-B', '-c', closure_code, str(clone)], base)
    assert not run([*git, 'status', '--porcelain', '--untracked-files=all'], clone, structured=False)
    report = {'stage': '3A', 'status': 'passed', 'tested_commit': commit,
              'temporary_clone': str(clone), 'runtime': runtime, 'cache_present': False,
              'tree_clean_after_tests': True, 'real_origins_updated': False,
              'vendor_code_executed': False, 'results': results,
              'limits': 'Local fixture updates only; no other agents, network or vendor workflows. Clone retained.'}
    if args.report: args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k:v for k,v in report.items() if k != 'results'}, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
