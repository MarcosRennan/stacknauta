"""Inclusões simuladas; reutiliza a fixture mínima Git da Etapa 3A."""
import sys
sys.dont_write_bytecode=True
import copy
import importlib.util
import io
import json
import os
import subprocess
import unittest
from types import SimpleNamespace
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'Automacao/manutencao-skills'),str(ROOT/'Automacao/project-bootstrap'),str(ROOT/'Skills/manutencao')]
spec=importlib.util.spec_from_file_location('stage3a_fixtures',ROOT/'Automacao/validacao-atualizacoes/test_updates.py')
fixtures=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixtures)
from inclusoes import Inclusions
from atualizacoes import Updates,Git,load,tree,atomic_json
from origens import parse_url,resolve,relative_path
from biblioteca import json_bytes
from stacknauta_core.library import Library
from stacknauta_core.config import normalize
from stacknauta_core import BootstrapError
from stacknauta_core.core import Bootstrap
from stacknauta_core.integration import AgentIntegration
from stacknauta_core.compatibility import declared_policy,mismatch

POLICY={'languages_any':['python'],'frameworks_any':['fastapi'],'frameworks_all':[],
        'features_all':['api'],'architecture':None,'tools':[],'runtimes':[]}


class AdditionTests(unittest.TestCase):
    setUp=fixtures.UpdateTests.setUp

    def repo(self, skills=None):
        repo=self.base/'remotes/candidates';repo.mkdir()
        (repo/'LICENSE').write_bytes((ROOT/'Skills/Backend/fastapi/LICENSE').read_bytes())
        for path,name,body in skills or [('skills/good','good-helper','Guia técnico de API.\n'),('skills/missing','missing-helper','[Recurso](references/absent.md)\n'),('skills/conflict','fastapi','Conflito de nome deliberado.\n')]:
            folder=repo/path;folder.mkdir(parents=True,exist_ok=True)
            (folder/'SKILL.md').write_text('---\nname: '+name+'\ndescription: Guia local de validação.\nlicense: MIT\n---\n\n'+body)
        fixtures.git(repo,'init','--quiet','--initial-branch=main');fixtures.git(repo,'add','.');fixtures.git(repo,'commit','--quiet','-m','fixture origin')
        return repo

    def add(self, repo=None, **kwargs):
        self.inc=Inclusions(self.engine)
        result=self.inc.add(str(repo or self.repo()),**kwargs)
        self.assertIn(result['status'],{'descoberto','sem_novas_candidatas'},result)
        return result

    def decision(self, report, suffix='good-helper', **changes):
        identifier=next(c['id'] for c in report['candidates'] if c['name']==suffix)
        row={'status':'approved','category':'Backend','reason':'Análise individual explícita da fixture.','compatibility':copy.deepcopy(POLICY)}
        row.update(changes)
        return {'schema_version':1,'skills':{identifier:row}}

    def stage(self, report, document=None):
        file=self.base/'decisions.json';file.write_bytes(json_bytes(document or self.decision(report)))
        plan=self.inc.review(report['session_id'],decisions=file,review_id=report['review_id'])
        self.assertEqual(plan['status'],'preparado',{k:plan.get(k) for k in ('status','motivo')})
        return plan

    def apply(self, plan, **kwargs):return self.engine.apply(plan['session_id'],plan['plan_id'],approve=True,**kwargs)

    def test_discovery_isolated_multiple_skills_all_pending(self):
        report=self.add()
        self.assertEqual(len(report['candidates']),3)
        self.assertTrue(all(c['current_status']=='pending' and not c['enabled'] for c in report['candidates']))
        self.assertEqual(tree(self.root/'Skills'),self.before)
        self.assertFalse((self.engine.session(report['session_id'])/'plan.json').exists())
        self.assertIsNone(report['candidates'][0]['proposed_category'])

    def test_individual_approval_only_and_physical_export(self):
        report=self.add();plan=self.stage(report);self.assertEqual(tree(self.root/'Skills'),self.before)
        self.apply(plan);self.engine.validate(self.root)
        cat=load(self.root,'Skills/catalogo.json');new=[s for s in cat['skills'] if s['source_id']==report['source']['id']]
        self.assertEqual(sum(s['distribution_status']=='approved' for s in new),1)
        self.assertEqual(sum(s['distribution_status']=='pending' for s in new),2)
        config=normalize({'name':'consumer-api','destination':str(self.base/'new-consumer'),'stack':{'languages':['python'],'frameworks':['fastapi']},'requirements':{'features':['api']}},self.base)
        library=Library(self.root);selection=library.select(config)
        identifier=plan['details']['approved'][0];self.assertIn(identifier,selection['selected'])
        files,origins,exported=library.export(selection)
        destination=self.base/'new-consumer';destination.mkdir()
        for relative,data in files.items():
            target=destination/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        self.assertTrue(any(s['id']==identifier for s in exported))
        self.assertFalse(any(p.is_symlink() for p in destination.rglob('*')))
        package=next(s['distribution']['package'] for s in new if s['distribution_status']=='approved')
        self.assertTrue(any('/vendor/LICENSE' in p and row['package']==package for p,row in origins.items()))
        self.assertEqual((self.consumer/'sentinel').read_text(),'intocado')

    def test_new_skill_bootstrap_plan_apply_and_verify(self):
        report=self.add();plan=self.stage(report);self.apply(plan)
        integration=AgentIntegration(Bootstrap(self.root))
        raw={'name':'new-project','destination':str(self.base/'new-project'),
             'stack':{'languages':['python'],'frameworks':['fastapi']},'requirements':{'features':['api']}}
        core,files,proposal=integration.plan(raw)
        self.assertFalse((self.base/'new-project').exists())
        result=integration.apply(raw,proposal['plan_id']);self.assertEqual(result['status'],'verified')
        identifier=plan['details']['approved'][0]
        self.assertTrue(any(s['id']==identifier for s in result['discovery_entries']))
        self.assertEqual(integration.verify(raw)['verification_state'],'intact')
        self.assertEqual(integration.apply(raw,proposal['plan_id'])['core_result']['status'],'unchanged')

    def test_url_subdirectory_scope_and_root_license(self):
        report=self.add(path='skills/good')
        self.assertEqual([c['name'] for c in report['candidates']],['good-helper'])
        plan=self.stage(report);self.apply(plan)
        package=next(p for p in load(self.root,'Skills/catalogo.json')['distribution_packages'] if report['source']['id'] in p['id'])
        self.assertTrue((self.root/package['directory']/'vendor/LICENSE').is_file())

    def test_root_skill_layout_and_resources(self):
        repo=self.repo([('.','good-helper','[Dados](references/data.md)\n')])
        (repo/'references').mkdir();(repo/'references/data.md').write_text('Dado técnico.\n')
        fixtures.git(repo,'add','.');fixtures.git(repo,'commit','--quiet','-m','root resource')
        report=self.add(repo);plan=self.stage(report);self.apply(plan)
        self.engine.validate(self.root)
        row=next(s for s in load(self.root,'Skills/catalogo.json')['skills'] if s['id'] in plan['details']['approved'])
        self.assertEqual(row['distribution']['skill_directory'],'vendor')

    def test_external_relative_assets_and_scripts_have_complete_closure(self):
        repo=self.repo([('skills/good','good-helper','[Referência](../common/info.md)\n')])
        for path,text in {'skills/common/info.md':'[Dados](../../assets/data.csv)', 'assets/data.csv':'a,b\n1,2\n',
                          'skills/good/helper.mjs':'import {value} from "../shared/resource.mjs";\nthrow new Error("Never execute");\n',
                          'skills/shared/resource.mjs':'export const value=1;\n'}.items():
            p=repo/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
        fixtures.git(repo,'add','.');fixtures.git(repo,'commit','--quiet','-m','closed resources')
        report=self.add(repo);plan=self.stage(report);self.apply(plan)
        row=next(s for s in load(self.root,'Skills/catalogo.json')['skills'] if s['id'] in plan['details']['approved'])
        lib=Library(self.root);package=lib.package(row['distribution']['package'])
        paths,_=lib.selected_files(row['id'],lib.catalog,package)
        for relative in ['vendor/assets/data.csv','vendor/skills/common/info.md','vendor/skills/shared/resource.mjs']:
            self.assertIn(relative,paths);self.assertTrue((self.root/package['directory']/relative).is_file())

    def test_subdirectory_does_not_require_unselected_root_orchestrator(self):
        repo=self.repo([('.','orchestrator','Guia raiz.'),('skills/good','good-helper','Guia independente.')])
        report=self.add(repo,path='skills/good');plan=self.stage(report);self.apply(plan)
        rows=[s for s in load(self.root,'Skills/catalogo.json')['skills'] if s['source_id']==report['source']['id']]
        self.assertEqual(next(s for s in rows if s['name']=='orchestrator')['distribution_status'],'pending')
        self.assertEqual(next(s for s in rows if s['name']=='good-helper')['distribution_status'],'approved')

    def test_existing_origin_reuses_identity_and_pending_metadata(self):
        repo=self.repos['remy'];path=repo/'new-helper/SKILL.md';path.parent.mkdir();path.write_text('---\nname: good-helper\ndescription: Nova skill local.\n---\n\nGuia.\n')
        fixtures.git(repo,'add','.');fixtures.git(repo,'commit','--quiet','-m','new pending helper')
        update=self.engine.prepare({'remy'});self.assertEqual(update['status'],'preparado',update.get('motivo'))
        self.apply(update);fixtures.git(self.root,'add','Skills');fixtures.git(self.root,'commit','--quiet','-m','record pending fixture')
        before=load(self.root,'Skills/catalogo.json');report=self.add(repo)
        self.assertEqual(report['source']['id'],'remy');plan=self.stage(report);self.apply(plan)
        after=load(self.root,'Skills/catalogo.json');self.assertEqual(len(after['sources']),7)
        for row in before['skills']:
            if row['id']!='remy:good-helper':self.assertEqual(row,next(s for s in after['skills'] if s['id']==row['id']))
        self.assertTrue((self.root/'Skills/Backend/remy-adicionais/PROVENANCE.json').exists())

    def test_existing_full_acquisition_is_never_narrowed(self):
        path=Path(next(s['source_path'] for s in self.original['skills'] if s['id']=='remy:hexagonal-python')).parent.as_posix()
        report=self.add(self.repos['remy'],path=path)
        self.assertEqual(report['source']['sparse_paths'],[])
        self.assertEqual(len(self.engine.sources()),7)

    def test_source_identifier_collision_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'ID de origem já utilizado'):Inclusions(self.engine).add(str(self.repo()),source_id='fastapi')

    def test_missing_requested_subdirectory_is_not_silently_ignored(self):
        result=Inclusions(self.engine).add(str(self.repo()),path='nonexistent/path')
        self.assertEqual(result['status'],'bloqueado');self.assertIn('Subdiretório',result['motivo'])
        self.assertEqual(tree(self.root/'Skills'),self.before)

    def test_duplicate_content_and_name_conflicts_reported(self):
        report=self.add();conflict=next(c for c in report['candidates'] if c['name']=='fastapi')
        self.assertIn('fastapi:fastapi',conflict['conflicts'])
        file=self.base/'decisions.json';file.write_bytes(json_bytes(self.decision(report,'fastapi')))
        with self.assertRaisesRegex(ValueError,'Conflitos'):self.inc.review(report['session_id'],decisions=file,review_id=report['review_id'])

    def test_same_vendor_bytes_are_detected_as_duplicate(self):
        repo=self.repo([('copy','good-helper','Temporary.')])
        (repo/'copy/SKILL.md').write_bytes((self.repos['fastapi']/'fastapi/.agents/skills/fastapi/SKILL.md').read_bytes())
        fixtures.git(repo,'add','.');fixtures.git(repo,'commit','--quiet','-m','identical vendor bytes')
        report=self.add(repo);self.assertIn('fastapi:fastapi',report['candidates'][0]['content_duplicates'])

    def test_acknowledgment_cannot_bypass_approved_alias_collision(self):
        report=self.add();document=self.decision(report,'fastapi',conflicts_acknowledged=['fastapi:fastapi'])
        file=self.base/'decisions.json';file.write_bytes(json_bytes(document))
        with self.assertRaisesRegex(ValueError,'aliases'):self.inc.review(report['session_id'],decisions=file,review_id=report['review_id'])

    def test_duplicate_identifiers_block_registration(self):
        report=self.add(self.repo([('one','good-helper','A'),('two','good-helper','B')]))
        self.assertTrue(all('Identificador duplicado na origem' in c['blockers'] for c in report['candidates']))
        file=self.base/'decisions.json';file.write_bytes(json_bytes({'schema_version':1,'skills':{}}))
        with self.assertRaisesRegex(ValueError,'IDs duplicados'):self.inc.review(report['session_id'],decisions=file,review_id=report['review_id'])
        self.assertEqual(tree(self.root/'Skills'),self.before)

    def test_missing_license_cannot_be_approved(self):
        repo=self.repo([('good','good-helper','Guia.')]);(repo/'LICENSE').unlink();fixtures.git(repo,'add','.');fixtures.git(repo,'commit','--quiet','-m','no license')
        report=self.add(repo);file=self.base/'decisions.json';file.write_bytes(json_bytes(self.decision(report)))
        with self.assertRaisesRegex(ValueError,'Licença'):self.inc.review(report['session_id'],decisions=file,review_id=report['review_id'])

    def test_incompatible_license_is_pending(self):
        repo=self.repo([('good','good-helper','Guia.')]);p=repo/'good/SKILL.md';p.write_text(p.read_text().replace('license: MIT','license: Apache-2.0'))
        fixtures.git(repo,'add','.');fixtures.git(repo,'commit','--quiet','-m','conflicting license')
        report=self.add(repo);self.assertTrue(any('incompatível' in b for b in report['candidates'][0]['blockers']))
        p.write_text(p.read_text().replace('license: Apache-2.0','license: MIT'))
        asset=repo/'good/assets/font-OFL.txt';asset.parent.mkdir();asset.write_text('Unknown terms for this asset.')
        fixtures.git(repo,'add','.');fixtures.git(repo,'commit','--quiet','-m','unknown asset license')
        report=self.add(repo);self.assertTrue(any('asset' in b for b in report['candidates'][0]['blockers']))

    def test_renderer_templates_and_long_alias_remain_pending(self):
        repo=self.repo([('template','good-helper','{{SKILL_BODY}}\n'),('long','a'*55,'Guia.')])
        report=self.add(repo);self.assertTrue(any('renderização' in b for b in next(c for c in report['candidates'] if c['name']=='good-helper')['blockers']))
        self.assertTrue(any('alias' in b for b in next(c for c in report['candidates'] if c['name']=='a'*55)['blockers']))
        file=self.base/'decisions.json';file.write_bytes(json_bytes(self.decision(report)))
        with self.assertRaisesRegex(ValueError,'renderização'):self.inc.review(report['session_id'],decisions=file,review_id=report['review_id'])

    def test_missing_resource_stays_pending_and_cannot_be_approved(self):
        report=self.add();file=self.base/'decisions.json';file.write_bytes(json_bytes(self.decision(report,'missing-helper')))
        with self.assertRaisesRegex(ValueError,'Recursos'):self.inc.review(report['session_id'],decisions=file,review_id=report['review_id'])
        plan=self.stage(report);self.apply(plan)
        row=next(s for s in load(self.root,'Skills/catalogo.json')['skills'] if s['name']=='missing-helper')
        self.assertIsNone(row['distribution'])

    def test_no_approvals_registers_only_pending(self):
        report=self.add();plan=self.stage(report,{'schema_version':1,'skills':{}});self.apply(plan)
        cat=load(self.root,'Skills/catalogo.json');self.assertEqual(cat['counts']['approved_skills'],4)
        self.assertEqual(len(cat['distribution_packages']),2)
        self.assertEqual(sum(s['distribution_status']=='pending' for s in cat['skills']),3)

    def test_explicit_exclusion_and_prior_classifications(self):
        report=self.add();decision=self.decision(report);missing=next(c['id'] for c in report['candidates'] if c['name']=='missing-helper')
        decision['skills'][missing]={'status':'excluded','reason':'Exclusão individual explícita.'}
        plan=self.stage(report,decision);self.apply(plan)
        cat=load(self.root,'Skills/catalogo.json');old={s['id']:s for s in cat['skills']}
        for row in self.original['skills']:self.assertEqual(old[row['id']],row)
        self.assertEqual(old[missing]['distribution_status'],'excluded')

    def test_category_and_applicability_are_mandatory(self):
        report=self.add();file=self.base/'decisions.json';document=self.decision(report)
        identifier=next(iter(document['skills']));document['skills'][identifier].pop('category')
        file.write_bytes(json_bytes(document))
        with self.assertRaisesRegex(ValueError,'Classificação'):self.inc.review(report['session_id'],decisions=file,review_id=report['review_id'])
        document=self.decision(report,category='Database');file.write_bytes(json_bytes(document))
        with self.assertRaisesRegex(ValueError,'Categoria'):self.inc.review(report['session_id'],decisions=file,review_id=report['review_id'])

    def test_framework_versions_and_incompatible_explicit_selection(self):
        report=self.add();document=self.decision(report);identifier=next(iter(document['skills']))
        document['skills'][identifier]['compatibility']['framework_versions']={'fastapi':['0.162.5']}
        plan=self.stage(report,document);self.apply(plan);lib=Library(self.root)
        config=normalize({'name':'api','stack':{'languages':['python'],'frameworks':['fastapi']},'requirements':{'features':['api']}},self.base)
        selection=lib.select(config);self.assertNotIn(identifier,selection['selected']);self.assertTrue(any(s['skill']==identifier for s in selection['skipped']))
        config['skills']=[identifier]
        with self.assertRaisesRegex(BootstrapError,'Versão explícita'):lib.select(config)
        config['stack']['frameworks'][0]['version']='0.162.5';self.assertIn(identifier,lib.select(config)['selected'])
        config['stack']['languages']=['javascript']
        with self.assertRaisesRegex(BootstrapError,'Linguagem'):lib.select(config)

    def test_review_hash_and_apply_authorization(self):
        report=self.add();file=self.base/'decisions.json';file.write_bytes(json_bytes(self.decision(report)))
        with self.assertRaisesRegex(ValueError,'review-id'):self.inc.review(report['session_id'],decisions=file,review_id='0'*64)
        plan=self.stage(report)
        with self.assertRaises(ValueError):self.engine.apply(plan['session_id'],plan['plan_id'])
        with self.assertRaises(ValueError):self.engine.apply(plan['session_id'],'0'*64,approve=True)
        self.assertEqual(tree(self.root/'Skills'),self.before)

    def test_tampered_source_and_analysis_are_rejected(self):
        report=self.add();session=self.engine.session(report['session_id']);p=session/'inspection'/report['source']['directory']/'skills/good/SKILL.md'
        p.write_text(p.read_text()+'\nAlteração não revisada.\n')
        file=self.base/'decisions.json';file.write_bytes(json_bytes(self.decision(report)))
        with self.assertRaisesRegex(ValueError,'alterados'):self.inc.review(report['session_id'],decisions=file,review_id=report['review_id'])
        record=load(session,'analysis.json');record['source']['commit']='0'*40;atomic_json(session/'analysis.json',record)
        with self.assertRaisesRegex(ValueError,'Inspeção alterada'):self.inc.review(report['session_id'])

    def test_unexpected_candidate_changes_block_apply(self):
        report=self.add();plan=self.stage(report);candidate=self.engine.session(plan['session_id'])/'candidate'
        (candidate/'Skills/catalogo.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'Candidato'):self.apply(plan)

    def test_paths_symlinks_and_production_local_urls_are_rejected(self):
        with self.assertRaises(ValueError):parse_url(str(self.base))
        for path in ['.','../outside','/outside','.git/config','a/../b']:
            with self.assertRaises(ValueError):relative_path(path)
        for value in ['https://evil.example/a/b','https://user:secret@github.com/a/b','https://github.com/a/b/tree/main/../escape','git@evil.example:a/b','ssh://git@github.com:2222/a/b']:
            with self.assertRaises(ValueError):parse_url(value)
        repo=self.repo();(repo/'skills/good/escape').symlink_to('/etc/passwd');fixtures.git(repo,'add','.');fixtures.git(repo,'commit','--quiet','-m','unsafe link')
        result=Inclusions(self.engine).add(str(repo));self.assertEqual(result['status'],'bloqueado');self.assertEqual(tree(self.root/'Skills'),self.before)

    def test_network_failure_and_unavailable_repo(self):
        inc=Inclusions(self.engine)
        with patch.object(self.engine.git,'run',side_effect=ValueError('Rede indisponível')):
            with self.assertRaisesRegex(ValueError,'Rede'):inc.add('https://github.com/demo/skills')
        with self.assertRaises(ValueError):inc.add(str(self.base/'missing-origin'))
        self.assertEqual(tree(self.root/'Skills'),self.before)

    def test_recovery_and_consumer_preservation(self):
        report=self.add();plan=self.stage(report)
        with self.assertRaises(OSError):self.apply(plan,hook=lambda _:(_ for _ in ()).throw(OSError('falha simulada')))
        self.assertEqual(tree(self.root/'Skills'),self.before)
        self.assertEqual((self.consumer/'sentinel').read_text(),'intocado');self.engine.validate(self.root)

    def test_failure_after_new_publication_recovers_original_library(self):
        report=self.add();plan=self.stage(report)
        def fail(phase):
            if phase=='new_published':raise OSError('falha após publicação')
        with self.assertRaises(OSError):self.apply(plan,hook=fail)
        self.assertEqual(tree(self.root/'Skills'),self.before);self.engine.validate(self.root)

    def test_companion_requires_its_own_approval_and_compatible_copy_closure(self):
        repo=self.repo([('one','good-helper','Utilizar `companion`.\n'),('two','companion','Guia complementar.\n')])
        report=self.add(repo);document=self.decision(report)
        good=next(iter(document['skills']));companion=next(c['id'] for c in report['candidates'] if c['name']=='companion')
        document['skills'][good]['requires_skills']=[companion]
        file=self.base/'decisions.json';file.write_bytes(json_bytes(document))
        with self.assertRaisesRegex(ValueError,'ainda pendente'):self.inc.review(report['session_id'],decisions=file,review_id=report['review_id'])
        document['skills'][companion]=self.decision(report,'companion')['skills'][companion]
        plan=self.stage(report,document);self.apply(plan)
        config=normalize({'name':'companion-project','stack':{'languages':['python'],'frameworks':['fastapi']},'requirements':{'features':['api']},'skills':[good]},self.base)
        lib=Library(self.root);selected=lib.select(config);self.assertEqual(set(selected['selected']),{good,companion})
        files,_,_=lib.export(selected);self.assertTrue(any(p.endswith('/vendor/two/SKILL.md') for p in files))

    def test_idempotent_review_apply_and_rediscovery(self):
        repo=self.repo([('good','good-helper','Guia.')]);report=self.add(repo);plan=self.stage(report)
        self.assertEqual(self.stage(report)['plan_id'],plan['plan_id'])
        self.apply(plan);before=tree(self.root/'Skills');self.assertEqual(self.apply(plan)['status'],'ja_aplicado')
        current=self.inc.review(report['session_id']);self.assertEqual(current['candidates'][0]['current_status'],'approved')
        fixtures.git(self.root,'add','Skills');fixtures.git(self.root,'commit','--quiet','-m','record addition')
        result=self.add(repo);self.assertEqual(result['status'],'sem_novas_candidatas');self.assertEqual(tree(self.root/'Skills'),before)

    def test_update_new_registered_origin_preserves_compatibility(self):
        repo=self.repo([('good','good-helper','Guia.')]);report=self.add(repo);plan=self.stage(report);self.apply(plan)
        fixtures.git(self.root,'add','Skills');fixtures.git(self.root,'commit','--quiet','-m','record addition')
        path=repo/'good/SKILL.md';path.write_text(path.read_text()+'\nOrientação nova.\n');fixtures.git(repo,'add','.');fixtures.git(repo,'commit','--quiet','-m','update added source')
        update=self.engine.prepare({report['source']['id']});self.assertEqual(update['status'],'preparado',update.get('motivo'));self.apply(update)
        row=next(s for s in load(self.root,'Skills/catalogo.json')['skills'] if s['id'] in plan['details']['approved']);self.assertEqual(row['compatibility'],POLICY)
        self.engine.validate(self.root);self.assertEqual(len(self.engine.check()),8)

    def test_url_formats_refs_with_slashes_and_ssh_no_config_changes(self):
        for url in ['https://github.com/Owner/Repo','git@github.com:Owner/Repo.git','ssh://git@github.com/Owner/Repo.git']:
            self.assertEqual(parse_url(url)['identity'],'owner/repo')
        for url in ['https://github.com:443/owner/.github','https://www.github.com/owner/.github','git@GitHub.com:owner/.github.git']:
            self.assertEqual(parse_url(url)['identity'],'owner/.github')
        self.assertEqual(parse_url('https://github.com/owner/-skills')['repo'],'-skills')
        parsed=parse_url('https://github.com/Owner/Repo/tree/feature/topic/skills/good')
        result='ref: refs/heads/main\tHEAD\n'+'a'*40+'\trefs/heads/main\n'+'b'*40+'\trefs/heads/feature/topic\n'
        with patch.object(self.engine.git,'run',return_value=result):
            resolved=resolve(self.engine.git,parsed)
        self.assertEqual(resolved['branch'],'feature/topic');self.assertEqual(resolved['requested_path'],'skills/good')

    def test_blob_url_and_pinned_revisions(self):
        parsed=parse_url('https://github.com/owner/repo/blob/'+('a'*40)+'/skills/good/SKILL.md')
        remote='ref: refs/heads/main\tHEAD\n'+'b'*40+'\trefs/heads/main\n'
        with patch.object(self.engine.git,'run',return_value=remote):result=resolve(self.engine.git,parsed)
        self.assertEqual(result['requested_path'],'skills/good');self.assertEqual(result['revision_type'],'commit')
        source=copy.deepcopy(self.engine.sources()[0]);source.update(revision_type='commit')
        with patch.object(self.engine,'sources',return_value=[source]),patch.object(self.engine.git,'remote',side_effect=AssertionError('Do not track pinned branch')):
            self.assertEqual(self.engine.check()[0]['estado'],'revisao_fixada')

    def test_real_local_branch_with_slash_and_annotated_tag(self):
        repo=self.repo([('good','good-helper','Guia.')]);fixtures.git(repo,'branch','feature/topic')
        fixtures.git(repo,'tag','-a','v1','-m','fixture tag')
        branch=self.add(repo,revision='feature/topic',path='good');self.assertEqual(branch['source']['branch'],'feature/topic')
        tag=self.add(repo,revision='v1',path='good');self.assertEqual(tag['source']['revision_type'],'tag')
        self.assertEqual(tag['source']['commit'],fixtures.git(repo,'rev-parse','HEAD'))

    def test_ssh_transport_is_noninteractive_without_configuration_writes(self):
        result=SimpleNamespace(returncode=0,stdout='refs',stderr='')
        with patch('atualizacoes.subprocess.run',return_value=result) as run:
            Git().run(self.base,'ls-remote','git@github.com:owner/repo.git','HEAD')
        environment=run.call_args.kwargs['env'];command=run.call_args.args[0]
        self.assertIn('StrictHostKeyChecking=yes',environment['GIT_SSH_COMMAND'])
        self.assertIn('UpdateHostKeys=no',environment['GIT_SSH_COMMAND'])
        self.assertNotIn('GIT_CONFIG_GLOBAL',environment)
        self.assertEqual(environment['GIT_TERMINAL_PROMPT'],'0')
        self.assertIn('core.hooksPath=/dev/null',command)

    def test_existing_revision_cannot_update_implicitly(self):
        source=self.engine.sources()[0];parsed=parse_url(source['url'],allow_local=True)
        remote='ref: refs/heads/main\tHEAD\n'+'b'*40+'\trefs/heads/main\n'
        with patch.object(self.engine.git,'run',return_value=remote):
            with self.assertRaisesRegex(ValueError,'revisão diferente'):resolve(self.engine.git,parsed,revision='main',existing=source)

    def test_reject_unknown_compatibility_and_runtime_as_tool(self):
        for field,value in [('frameworks_any',['unsupported-framework']),('architecture',['hexagonal']),('tools',['python']),('tools',['../escape'])]:
            policy=copy.deepcopy(POLICY);policy[field]=value
            with self.assertRaises(BootstrapError):declared_policy(policy)
        policy=copy.deepcopy(POLICY);policy['unknown_rule']=True
        with self.assertRaises(BootstrapError):declared_policy(policy)
        policy=copy.deepcopy(POLICY);policy['languages_all']=['python','javascript']
        config=normalize({'name':'dual','stack':{'languages':['python'],'frameworks':['fastapi']},'requirements':{'features':['api']}},self.base)
        self.assertIn('Linguagens obrigatórias',mismatch(declared_policy(policy),config))
        config['stack']['languages'].append('javascript');self.assertIsNone(mismatch(declared_policy(policy),config))

    def test_missing_declared_tool_and_unreviewed_prerequisite_block(self):
        repo=self.repo([('good','good-helper','Requires missing-test-tool.\n')]);report=self.add(repo);file=self.base/'decisions.json'
        document=self.decision(report);file.write_bytes(json_bytes(document))
        with self.assertRaisesRegex(ValueError,'pré-requisitos'):self.inc.review(report['session_id'],decisions=file,review_id=report['review_id'])
        document['skills'][next(iter(document['skills']))]['compatibility']['tools']=['missing-stacknauta-tool-xyz'];file.write_bytes(json_bytes(document))
        with self.assertRaisesRegex(ValueError,'Ferramentas ausentes'):self.inc.review(report['session_id'],decisions=file,review_id=report['review_id'])

    def test_cli_review_and_3a_check_are_compatible(self):
        report=self.add()
        import skills_cli
        for args in [('check',),('review',report['session_id']),('review',)]:
            output=io.StringIO()
            with patch.object(skills_cli,'ROOT',self.root),patch.object(skills_cli,'Updates',return_value=self.engine),patch.object(sys,'argv',['skills',*args]),redirect_stdout(output):
                code=skills_cli.main()
            self.assertEqual(code,0);self.assertIn('status',json.loads(output.getvalue()))

    def test_cli_add_review_apply_end_to_end(self):
        import skills_cli
        def call(args):
            output=io.StringIO()
            with patch.object(skills_cli,'ROOT',self.root),patch.object(skills_cli,'Updates',return_value=self.engine),patch.object(sys,'argv',['skills',*args]),redirect_stdout(output):
                self.assertEqual(skills_cli.main(),0)
            return json.loads(output.getvalue())
        report=call(['add',str(self.repo())]);file=self.base/'decisions.json';file.write_bytes(json_bytes(self.decision(report)))
        plan=call(['review',report['session_id'],'--decisions',str(file),'--review-id',report['review_id']])
        self.assertEqual(tree(self.root/'Skills'),self.before)
        result=call(['apply',report['session_id'],'--plan-id',plan['plan_id'],'--approve'])
        self.assertEqual(result['status'],'aplicado');self.engine.validate(self.root)


if __name__=='__main__':unittest.main()
