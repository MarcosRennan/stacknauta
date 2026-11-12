"""Regressão 4A.1 uma vez, em clone local com origin preservado e sem cache."""
import sys
sys.dont_write_bytecode = True
import argparse
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(command, cwd, timeout=240):
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True,
        timeout=timeout, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1',
        GIT_OPTIONAL_LOCKS='0', GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    git = ['git', '-c', 'core.hooksPath=/dev/null', '-c', 'core.fsmonitor=false']
    status = run([*git, 'status', '--porcelain', '--untracked-files=all'], ROOT)
    if status.returncode or status.stdout.strip():
        raise SystemExit('Commit candidato e árvore limpa são obrigatórios')
    base = Path(tempfile.mkdtemp(prefix='stacknauta-4a1-regression-'))
    clone = base / 'StackNauta'
    result = run([*git, 'clone', '--quiet', '--no-hardlinks', '--no-recurse-submodules', str(ROOT), str(clone)], base)
    if result.returncode:
        raise SystemExit(result.stderr)
    origin = run([*git, 'remote', 'get-url', 'origin'], clone).stdout.strip()
    assert origin == str(ROOT)
    assert not (clone / 'Skills/_repos').exists()
    assert not (clone / '.git/objects/info/alternates').exists()
    report = {'stage': '4A.1', 'started_at_utc': datetime.now(timezone.utc).isoformat(),
              'tested_commit': run([*git, 'rev-parse', 'HEAD'], clone).stdout.strip(),
              'temporary_clone': str(clone), 'origin_preserved': origin,
              'cache_present': False, 'results': {}, 'status': 'passed'}
    for key, script in (
        ('nucleo', 'Automacao/validacao-project-bootstrap/executar_testes.py'),
        ('integracao', 'Automacao/validacao-integracao-agentes/executar_testes.py'),
        ('atualizacoes', 'Automacao/validacao-atualizacoes/executar_testes.py'),
        ('inclusoes', 'Automacao/validacao-inclusoes/executar_testes.py'),
        ('biblioteca', 'Skills/validacao/validar_biblioteca.py'),
    ):
        output = base / (key + '.json')
        extra = ['--copias', '--sintaxe-node'] if key == 'biblioteca' else ['--report', str(output)]
        print('Executando ' + key, flush=True)
        try:
            result = run([sys.executable, '-I', '-S', '-B', str(clone / script), *extra], base)
            data = json.loads(result.stdout) if key == 'biblioteca' else json.loads(output.read_text())
            report['results'][key] = data
            if result.returncode:
                report['status'] = 'failed'
                report['results'][key]['stderr'] = result.stderr
        except (subprocess.TimeoutExpired, ValueError, OSError) as exc:
            report['status'] = 'failed'
            report['results'][key] = {'status': 'pending_or_environment_error', 'reason': str(exc)}
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    report['origin_unchanged'] = run([*git, 'remote', 'get-url', 'origin'], clone).stdout.strip() == origin
    report['tree_clean_after_tests'] = not run([*git, 'status', '--porcelain', '--untracked-files=all'], clone).stdout.strip()
    if not report['origin_unchanged'] or not report['tree_clean_after_tests']:
        report['status'] = 'failed'
    report['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k:v for k,v in report.items() if k != 'results'}, ensure_ascii=False, indent=2))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
