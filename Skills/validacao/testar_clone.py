"""Clone Git local descartável, sem cache/remotos finais; não cria aplicações."""
import sys
sys.dont_write_bytecode=True
import json
import os
import subprocess
import tempfile
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Skills/manutencao'))
from biblioteca import require_asdf_python,sha
from inventariar import git


def main():
    runtime=require_asdf_python()
    if git(ROOT,'status','--porcelain','--untracked-files=all'):
        raise SystemExit('Teste exige um commit candidato com árvore limpa.')
    if git(ROOT,'remote'):
        raise SystemExit('Git principal não deve ter remoto.')
    base=Path(tempfile.mkdtemp(prefix='stacknauta-clone-'))
    clone=base/'StackNauta'
    subprocess.run(['git','-c','core.hooksPath=/dev/null','-c','maintenance.auto=false',
                    'clone','--no-hardlinks','--no-recurse-submodules','--quiet',str(ROOT),str(clone)],check=True,timeout=60)
    # clone cria origin local automaticamente; remover imediatamente nesse Git temporário.
    subprocess.run(['git','-c','core.hooksPath=/dev/null','-C',str(clone),'remote','remove','origin'],check=True,timeout=10)
    if (clone/'Skills/_repos').exists() or (clone/'.git/objects/info/alternates').exists():
        raise SystemExit('Clone depende do cache ou dos objetos externos.')
    if git(clone,'remote') or git(clone,'status','--porcelain','--untracked-files=all'):
        raise SystemExit('Clone tem remoto ou árvore não limpa.')
    expected=json.loads((ROOT/'Skills/catalogo.json').read_text())
    observed=json.loads((clone/'Skills/catalogo.json').read_text())
    if expected['distribution_packages']!=observed['distribution_packages']:
        raise SystemExit('Manifestos divergentes no clone.')
    environment=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',GIT_OPTIONAL_LOCKS='0')
    result=subprocess.run([sys.executable,'-B','Skills/validacao/validar_catalogo.py','--copias','--sintaxe-node'],
                          cwd=clone,env=environment,capture_output=True,text=True,timeout=60)
    if result.returncode:
        raise SystemExit(result.stdout+'\n'+result.stderr)
    validation=json.loads(result.stdout)
    if validation['cache_validation']['status']!='not_required_for_distribution' or validation['physical_copy_test']['status']!='passed':
        raise SystemExit('Validação do clone não demonstrou independência e cópias.')
    if git(clone,'status','--porcelain','--untracked-files=all'):
        raise SystemExit('Validador escreveu na árvore do clone.')
    fingerprint=sha(json.dumps(expected['distribution_packages'],sort_keys=True).encode())
    report={'schema_version':1,'stage':'1.5','tested_at_utc':datetime.now(timezone.utc).isoformat(),
            'status':'passed','python_executor':runtime,'tested_commit':git(clone,'rev-parse','HEAD'),
            'package_manifest_fingerprint':fingerprint,'temporary_clone':str(clone),
            'cache_present':False,'remote_configured':False,'object_alternates':False,
            'git_tree_clean_after_validation':True,'validation':validation,
            'limits':'Commit de evidência pode apenas acrescentar este relatório; o fingerprint identifica exatamente os pacotes testados. Diretórios temporários mantidos, sem exclusão recursiva.'}
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
