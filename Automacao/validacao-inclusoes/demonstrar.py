"""Demonstra três candidatas em biblioteca de teste isolada; não incorpora reais."""
import sys
sys.dont_write_bytecode=True
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from test_additions import AdditionTests, fixtures
from stacknauta_core.core import Bootstrap
from stacknauta_core.integration import AgentIntegration


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--report',type=Path);args=parser.parse_args()
    test=AdditionTests();test.setUp()  # Ambiente preservado para inspeção; não chamar cleanup.
    discovery=test.add();document=test.decision(discovery,'fastapi',conflicts_acknowledged=['fastapi:fastapi'])
    path=test.base/'rejected-decisions.json';path.write_text(json.dumps(document))
    try:
        test.inc.review(discovery['session_id'],decisions=path,review_id=discovery['review_id'])
    except ValueError as exc: rejected=str(exc)
    else:raise RuntimeError('Conflito indevidamente aprovado')
    plan=test.stage(discovery);applied=test.apply(plan)
    catalog=json.loads((test.root/'Skills/catalogo.json').read_text())
    rows=[{'id':s['id'],'status':s['distribution_status'],'category':s['category'],'distributed':s['distribution'] is not None,'enabled':s['enabled']}
          for s in catalog['skills'] if s['source_id']==discovery['source']['id']]
    assert sum(s['status']=='approved' for s in rows)==1
    assert sum(s['status']=='pending' for s in rows)==2
    assert not any(s['enabled'] for s in rows)
    raw={'name':'demo-api','destination':str(test.base/'demo-api'),'stack':{'languages':['python'],'frameworks':[{'name':'fastapi','version':'0.162.5'}]},'requirements':{'features':['api']}}
    integration=AgentIntegration(Bootstrap(test.root));_,_,bootstrap_plan=integration.plan(raw)
    bootstrap=integration.apply(raw,bootstrap_plan['plan_id']);reapply=integration.apply(raw,bootstrap_plan['plan_id'])
    assert bootstrap['status']=='verified' and reapply['core_result']['status']=='unchanged'
    assert (test.consumer/'sentinel').read_text()=='intocado'
    report={'stage':'3B','status':'passed','scope':'Isolated local fixture, not the real library','temporary_directory':str(test.base),
            'discovery':discovery,'plan_id':plan['plan_id'],'plan_file':str(test.engine.session(plan['session_id'])/'plan.json'),
            'diff_file':str(test.engine.session(plan['session_id'])/'review.diff'),'rejected_conflict':rejected,'applied':applied,
            'skills':rows,'validation':test.engine.validate(test.root),'bootstrap':bootstrap,
            'reapply':reapply['core_result']['status'],'existing_fixture_consumer_preserved':True,'real_origins_added':False,
            'vendor_code_executed':False,'native_agent_activation_tested':False,'temporary_environment_retained':True}
    if args.report:args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in {'discovery','applied','bootstrap'}},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
