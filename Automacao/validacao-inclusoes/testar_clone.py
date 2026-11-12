"""Reutiliza clone 3A sem cache e acrescenta testes e demonstração 3B."""
import sys
sys.dont_write_bytecode=True
import argparse
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('clone3a',ROOT/'Automacao/validacao-atualizacoes/testar_clone.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--report',type=Path);args=parser.parse_args()
    base=Path(tempfile.mkdtemp(prefix='stacknauta-3b-clone-report-'));previous=base/'clone3a.json'
    prior.run([sys.executable,'-I','-S','-B',str(ROOT/'Automacao/validacao-atualizacoes/testar_clone.py'),'--report',str(previous)],ROOT)
    inherited=json.loads(previous.read_text());clone=Path(inherited['temporary_clone'])
    tests_file=base/'inclusoes.json';demo_file=base/'demonstracao.json'
    prior.run([sys.executable,'-I','-S','-B',str(clone/'Automacao/validacao-inclusoes/executar_testes.py'),'--report',str(tests_file)],base)
    prior.run([sys.executable,'-I','-S','-B',str(clone/'Automacao/validacao-inclusoes/demonstrar.py'),'--report',str(demo_file)],base)
    assert not (clone/'Skills/_repos').exists()
    assert not subprocess.check_output(['git','-C',str(clone),'status','--porcelain'],text=True).strip()
    tests=json.loads(tests_file.read_text());demo=json.loads(demo_file.read_text())
    assert tests['status']=='passed' and demo['status']=='passed'
    report={'stage':'3B','status':'passed','tested_commit':inherited['tested_commit'],'temporary_clone':str(clone),
            'cache_present':False,'tree_clean_after_tests':True,'prior_validators':inherited,'inclusions':tests,'demonstration':demo,
            'real_origins_added':False,'vendor_code_executed':False,'other_agents_executed':False}
    if args.report:args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in {'prior_validators','inclusions','demonstration'}},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
