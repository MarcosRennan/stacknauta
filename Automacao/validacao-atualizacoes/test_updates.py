"""Fixtures Git locais; nenhum update das sete origens reais ou de consumidores."""
import sys
sys.dont_write_bytecode = True
import copy
import json
import os
import shutil
import subprocess
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Skills/manutencao"))
sys.path.insert(0, str(ROOT / "Automacao/manutencao-skills"))
from atualizacoes import Updates, tree, read_bytes, safe, atomic_json, move, SOURCES, load
from atualizacao_receita import replay_patch, relative_python_resources, python_dependencies
from biblioteca import json_bytes, sha
from stacknauta_core import BootstrapError


def git(repo, *args):
    return subprocess.check_output(["git", "-c", "core.hooksPath=/dev/null", "-c", "gc.auto=0",
        "-c", "user.name=StackNauta Fixture", "-c", "user.email=fixture@invalid.example", "-C", str(repo), *args],
        text=True, stderr=subprocess.STDOUT, env=dict(os.environ, GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")).strip()


def reverse(diff):
    return "".join(("-" + row[1:] if row.startswith("+") and not row.startswith("+++") else
                    "+" + row[1:] if row.startswith("-") and not row.startswith("---") else row)
                   for row in diff.splitlines(True))


class RelativePythonTests(unittest.TestCase):
    def check(self, text, path='pkg/sub/main.py', **extra):
        files={'pkg/__init__.py':b'', 'pkg/sub/__init__.py':b'', **extra}
        return relative_python_resources(text.encode(),path,files,files.__getitem__)

    def test_existing_modules_and_parent_levels(self):
        for text,target in [('from . import helper','pkg/sub/helper.py'),
                            ('from .helper import function','pkg/sub/helper.py'),
                            ('from ..utils import tool','pkg/utils.py'),
                            ('from .. import utils','pkg/utils/__init__.py')]:
            with self.subTest(text=text):
                self.assertIn(target,self.check(text,**{target:b'raise RuntimeError("never execute")'}))
        self.assertIn('helper.py',self.check('from . import helper',path='main.py',**{
            '__init__.py':b'', 'helper.py':b''}))

    def test_absent_modules_are_not_satisfied_by_init_or_namesakes(self):
        for text,files in [('from . import missing',{}),('from .missing import tool',{}),
                           ('from ..utils import tool',{'pkg/sub/utils.py':b''}),
                           ('from .helpers.child import tool',{'pkg/sub/helpers.py':b'','pkg/sub/helpers/child.py':b''}),
                           ('from ... import missing',{})]:
            with self.subTest(text=text),self.assertRaisesRegex(ValueError,'Dependência local'):
                self.check(text,**files)

    def test_package_precedes_module_and_namespace_is_physical(self):
        result=self.check('from .helpers.child import tool',**{
            'pkg/sub/helpers.py':b'', 'pkg/sub/helpers/__init__.py':b'', 'pkg/sub/helpers/child.py':b''})
        self.assertIn('pkg/sub/helpers/__init__.py',result)
        self.assertNotIn('pkg/sub/helpers.py',result)
        self.assertIn('pkg/sub/ns/child.py',self.check('from . import ns',**{'pkg/sub/ns/child.py':b''}))
        self.assertIn('pkg/sub/helpers/child.py',self.check('from .helpers import child',**{
            'pkg/sub/helpers/__init__.py':b'', 'pkg/sub/helpers/child.py':b''}))

    def test_static_exports_and_dynamic_uncertainty(self):
        self.assertIn('pkg/sub/__init__.py',self.check('from . import helper',**{'pkg/sub/__init__.py':b'helper = 1'}))
        self.assertIn('pkg/sub/__init__.py',self.check('from . import alias',**{
            'pkg/sub/__init__.py':b'from . import helper as alias', 'pkg/sub/helper.py':b''}))
        for init in (b'from . import missing',b'def __getattr__(name): return 1'):
            with self.assertRaises(ValueError):
                self.check('from . import missing',**{'pkg/sub/__init__.py':init})

    def test_absolute_external_and_invalid_syntax_keep_existing_contract(self):
        python_dependencies(b'',b'import local\nimport json',{'local'})
        python_dependencies(b'import external',b'import external',set())
        with self.assertRaises(ValueError):python_dependencies(b'',b'import external',set())
        with self.assertRaises(SyntaxError):self.check('from . import')


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp(prefix="stacknauta-update-test-"))
        token = uuid.uuid4().hex
        marker = self.base / ".stage3a-fixture-owner"; marker.write_text(token)
        def cleanup():
            if self.base.parent == Path(tempfile.gettempdir()) and not self.base.is_symlink() and marker.is_file() and marker.read_text() == token:
                shutil.rmtree(self.base)  # Apenas dados criados por este teste, nunca recuperação de biblioteca.
        self.addCleanup(cleanup)
        self.root = self.base / "StackNauta"
        self.root.mkdir()
        paths = [ROOT / p for p in (".gitignore", "README.md", "AGENTS.md", "GEMINI.md", "Automacao/python-global", ".agents/skills/project-bootstrap/SKILL.md", "Automacao/validacao-project-bootstrap/test_bootstrap.py")]
        for pattern in ("Automacao/project-bootstrap/*.py", "Automacao/project-bootstrap/STATUS.json", "Automacao/project-bootstrap/project-bootstrap",
                        "Automacao/project-bootstrap/stacknauta_core/*.py", "Automacao/manutencao-skills/*", "Skills/manutencao/*.py", "Skills/validacao/*.py", "Skills/validacao/*.json",
                        "Skills/catalogo.json", "Skills/fontes.lock.json", "Skills/manutencao/distribuicao-politica.json"):
            paths.extend(p for p in ROOT.glob(pattern) if p.is_file())
        for p in set(paths):
            dest = self.root / p.relative_to(ROOT); dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, dest)
        for package in ("Backend/fastapi", "Backend/remy"):
            shutil.copytree(ROOT / "Skills" / package, self.root / "Skills" / package)
        self.repos = {}; self.original = json.loads((self.root / "Skills/catalogo.json").read_text())
        lock = json.loads((self.root / "Skills/fontes.lock.json").read_text()); cat = self.original
        cat["skills"] = [s for s in cat["skills"] if s["source_id"] in {"fastapi", "remy"}]
        cat["distribution_packages"] = [p for p in cat["distribution_packages"] if p["id"] in {"Backend/fastapi", "Backend/remy"}]
        cat["distribution_aliases"] = []; cat["template_inputs"] = {}
        cat["counts"].update(catalogued_skills=4, prepared_distribution_skills=4, approved_skills=4, pending_skills=0, excluded_skills=0,
                              physical_skill_files=4, distribution_aliases=0, distribution_packages=2, by_category={"Backend":4}, by_scope={"catalogued_source":4}, approved_by_category={"Backend":4})
        for s in cat["sources"]:
            if s["id"] not in {"fastapi", "remy"}: s.update(physical_skill_files=0, canonical_skill_count=0)
        policy = json.loads((self.root / "Skills/manutencao/distribuicao-politica.json").read_text())
        policy["rows"] = [r for r in policy["rows"] if r["id"].split(':',1)[0] in {"fastapi", "remy"}]
        (self.root / "Skills/manutencao/distribuicao-politica.json").write_bytes(json_bytes(policy))
        cat["generation"]["policy_sha256"] = sha(json_bytes(policy))
        for name in ("adaptacoes.json", "revisao-recursos.json"):
            p = self.root / "Skills/validacao" / name
            rows = json.loads(p.read_text())
            rows = [r for r in rows if (r['package'].split('/',1)[1] if name == 'adaptacoes.json' else r['skill_id'].split(':',1)[0]) in {'fastapi','remy'}]
            p.write_bytes(json_bytes(rows))
        patches = {(p["package"], p["path"]): p for p in json.loads((self.root / "Skills/validacao/adaptacoes.json").read_text())}
        for source in lock["sources"]:
            repo = self.base / "remotes" / source["id"]; repo.mkdir(parents=True); self.repos[source["id"]] = repo
            if source["id"] in {"fastapi", "remy"}:
                for descriptor in cat["distribution_packages"]:
                    package = json.loads((self.root / descriptor["directory"] / "PROVENANCE.json").read_text())
                    if package["source_id"] != source["id"]: continue
                    for relative, record in package["files"].items():
                        if not record["inputs"]: continue
                        self.assertEqual(len(record["inputs"]), 1)
                        data = (self.root / package["directory"] / relative).read_bytes()
                        if (package["id"], relative) in patches:
                            data = replay_patch(data, reverse(patches[(package["id"], relative)]["diff"]))
                        self.assertEqual(sha(data), record["inputs"][0]["sha256"])
                        p = repo / record["inputs"][0]["path"]; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(data)
            else:
                (repo / "README.md").write_text("Origem local de teste: " + source["id"])
            git(repo, "init", "--quiet", "--initial-branch=" + source["branch"])
            git(repo, "add", "."); git(repo, "commit", "--quiet", "-m", "fixture base")
            previous_url, previous_commit = source["url"], source["commit"]
            source.update(url=str(repo), commit=git(repo, "rev-parse", "HEAD"))
            for s in cat["sources"]:
                if s["id"] == source["id"]: s.update(url=source["url"], commit=source["commit"])
            for s in cat["skills"]:
                if s["source_id"] == source["id"]: s.update(repository=source["url"], commit=source["commit"])
            for descriptor in cat["distribution_packages"]:
                p = self.root / descriptor["directory"] / "PROVENANCE.json"; package = json.loads(p.read_text())
                if package["source_id"] != source["id"]: continue
                package.update(repository=source["url"], commit=source["commit"])
                readme = p.parent / "README.md"
                data = readme.read_bytes().replace(previous_url.encode(), source["url"].encode()).replace(previous_commit.encode(), source["commit"].encode())
                readme.write_bytes(data); package["files"]["README.md"].update(sha256=sha(data), size=len(data))
                p.write_bytes(json_bytes(package)); descriptor["manifest_sha256"] = sha(p.read_bytes())
        (self.root / "Skills/fontes.lock.json").write_bytes(json_bytes(lock))
        cat["generation"]["source_lock_sha256"] = sha(json_bytes(lock))
        (self.root / "Skills/catalogo.json").write_bytes(json_bytes(cat))
        git(self.root, "init", "--quiet", "--initial-branch=main"); git(self.root, "add", "."); git(self.root, "commit", "--quiet", "-m", "fixture library")
        self.consumer = self.base / "consumer"; self.consumer.mkdir(); (self.consumer / "sentinel").write_text("intocado")
        self.engine = Updates(self.root, runtime=cat["python_executor"], allow_local=True)
        self.before = tree(self.root / "Skills")

    def change(self, sid="fastapi", relative="fastapi/.agents/skills/fastapi/references/dependencies.md", text="\nParágrafo adicional de teste.\n"):
        p = self.repos[sid] / relative
        with p.open("a") as stream: stream.write(text)
        git(self.repos[sid], "add", "."); git(self.repos[sid], "commit", "--quiet", "-m", "fixture update")

    def plan(self, ids={"fastapi"}):
        result = self.engine.prepare(ids)
        self.assertEqual(result["status"], "preparado", {k:result[k] for k in ("status", "motivo", "origens") if k in result})
        return result

    def apply(self, plan, **kwargs):
        return self.engine.apply(plan["session_id"], plan["plan_id"], approve=True, **kwargs)

    def test_check_unchanged_is_read_only(self):
        sources = self.engine.sources()
        rows = self.engine.check()
        self.assertEqual(len(rows), len(sources))
        by_id = {r["origem"]: r for r in rows}
        self.assertEqual(set(by_id), {s["id"] for s in sources})
        for source in sources:
            row = by_id[source["id"]]
            pinned = source.get("revision_type") in {"commit", "tag"}
            self.assertEqual(row["estado"], "revisao_fixada" if pinned else "sem_alteracoes")
            self.assertEqual(row["atual"], source["commit"])
            self.assertEqual(row["disponivel"], None if pinned else source["commit"])
        self.assertEqual(tree(self.root / "Skills"), self.before)
        self.assertFalse((self.root / ".stacknauta-updates").exists())

    def test_origin_does_not_disable_integrity_validation(self):
        clone=self.base/'clone'
        git(self.base,'clone','--quiet','--no-hardlinks',str(self.root),str(clone))
        self.engine.validate(clone)  # origin local preservado pelo clone.
        git(clone,'remote','remove','origin')
        self.engine.validate(clone)
        for url in (str(self.repos['fastapi']), 'git@example.org:team/library.git', 'https://example.org/team/library.git'):
            with self.subTest(url=url):
                git(self.root, 'config', 'remote.origin.url', url)
                self.engine.validate(self.root)
        path = self.root / 'Skills/Backend/fastapi/LICENSE'
        path.write_bytes(path.read_bytes() + b'corrupt')
        with self.assertRaises(ValueError):
            self.engine.validate(self.root)

    def test_update_rejects_missing_relative_python_with_init_present(self):
        directory='fastapi/.agents/skills/fastapi/'
        self.change(relative=directory+'__init__.py',text='')
        self.change(relative=directory+'main.py',text='from . import absent\n')
        result=self.engine.prepare({'fastapi'})
        self.assertEqual(result['status'],'bloqueado',result)
        self.assertIn('Dependência local Python',result['motivo'])
        self.assertEqual(tree(self.root/'Skills'),self.before)

    def test_update_accepts_existing_relative_modules_without_execution(self):
        folder=self.repos['fastapi']/'fastapi/.agents/skills/fastapi'
        (folder/'__init__.py').write_text('')
        (folder/'main.py').write_text('from . import helper\nfrom .helper import tool\n')
        (folder/'helper.py').write_text('raise RuntimeError("never execute")\n')
        self.change()
        plan=self.plan();self.apply(plan)
        self.assertTrue((self.root/'Skills/Backend/fastapi/skills/fastapi/helper.py').is_file())

    def test_detect_commit_prepare_and_authorized_update(self):
        self.change(); plan = self.plan()
        self.assertEqual(tree(self.root / "Skills"), self.before)
        self.assertEqual(self.engine.check({"fastapi"})[0]["estado"], "atualizacao_disponivel")
        result=self.apply(plan)
        self.assertEqual(result['status'],'aplicado')
        self.assertEqual(result['origens'][0]['resultado'],'atualizada')
        self.assertEqual(self.engine.check({"fastapi"})[0]["estado"], "sem_alteracoes")
        self.engine.validator(self.root)
        self.assertEqual((self.consumer / "sentinel").read_text(), "intocado")

    def test_git_environment_cannot_redirect_inventory_or_validation(self):
        self.change()
        with patch.dict(os.environ, {'GIT_DIR': str(self.base / 'nonexistent-git'), 'GIT_WORK_TREE': str(self.consumer),
                                      'GIT_CONFIG_COUNT': '1', 'GIT_CONFIG_KEY_0': 'core.fsmonitor', 'GIT_CONFIG_VALUE_0': '/invalid-hook'}):
            plan = self.plan(); self.apply(plan)
        self.engine.validator(self.root)
        self.assertEqual((self.consumer / 'sentinel').read_text(), 'intocado')

    def test_update_multiple_only_fetches_changed_sources(self):
        self.change()
        remy_file = next(p for p in self.repos["remy"].rglob("*.md") if p.name != "SKILL.md")
        self.change("remy", remy_file.relative_to(self.repos["remy"]).as_posix())
        with patch.object(self.engine.git, "acquire", wraps=self.engine.git.acquire) as acquire:
            plan = self.plan(SOURCES)
        self.assertEqual({c.args[0]["id"] for c in acquire.call_args_list}, {"fastapi", "remy"})
        self.apply(plan); self.engine.validator(self.root)

    def test_network_failure_is_not_reported_as_update(self):
        sources = self.engine.sources()
        branches = {s["id"] for s in sources if s.get("revision_type") not in {"commit", "tag"}}
        self.assertTrue(branches)
        with patch.object(self.engine.git, "remote", side_effect=ValueError("Conexão indisponível")) as remote:
            rows = self.engine.check(); result = self.engine.prepare(branches)
        self.assertEqual(len(rows), len(sources))
        self.assertEqual({r["origem"] for r in rows}, {s["id"] for s in sources})
        for row in rows:
            self.assertEqual(row["estado"], "erro_consulta" if row["origem"] in branches else "revisao_fixada")
            self.assertIsNone(row["disponivel"])
            source = next(s for s in sources if s["id"] == row["origem"])
            self.assertEqual(row["atual"], source["commit"])
        self.assertEqual({call.args[0]["id"] for call in remote.call_args_list}, branches)
        self.assertEqual(result["status"], "bloqueado"); self.assertEqual(tree(self.root / "Skills"), self.before)

    def test_missing_branch(self):
        git(self.repos["fastapi"], "symbolic-ref", "HEAD", "refs/heads/other")
        git(self.repos["fastapi"], "update-ref", "-d", "refs/heads/master")
        self.assertEqual(self.engine.check({"fastapi"})[0]["estado"], "erro_consulta")

    def test_new_skill_stays_pending_and_not_distributed(self):
        p = self.repos["fastapi"] / "fastapi/.agents/skills/fastapi/references/dependencies.md"
        # FastAPI sparse checkout intentionally only acquires its configured path;
        # a nested discovery cannot be distributed silently.
        new = self.repos["remy"] / "new-helper/SKILL.md"; new.parent.mkdir(); new.write_text("---\nname: new-helper\ndescription: New test skill.\n---\n\nTest only.\n")
        git(self.repos["remy"], "add", "."); git(self.repos["remy"], "commit", "--quiet", "-m", "new pending skill")
        plan = self.plan({"remy"}); self.assertEqual(plan["details"]["new_skills_pending"], ["remy:new-helper"])
        self.apply(plan); catalog = load(self.root, "Skills/catalogo.json")
        row = next(s for s in catalog["skills"] if s["id"] == "remy:new-helper")
        self.assertEqual(row["distribution_status"], "pending"); self.assertIsNone(row["distribution"])
        self.assertFalse(any(p.parent.name == "new-helper" for p in (self.root / "Skills/Backend").rglob("SKILL.md")))

    def test_missing_resource_blocks_whole_promotion(self):
        p = self.repos["fastapi"] / "fastapi/.agents/skills/fastapi/references/dependencies.md"; p.unlink()
        git(self.repos["fastapi"], "add", "."); git(self.repos["fastapi"], "commit", "--quiet", "-m", "missing resource")
        result = self.engine.prepare({"fastapi"}); self.assertEqual(result["status"], "bloqueado")
        self.assertEqual(tree(self.root / "Skills"), self.before)

    def test_new_skill_outside_sparse_scope_is_reported_and_blocked(self):
        repo = self.repos['fastapi']; path = repo / 'outside/SKILL.md'
        path.parent.mkdir(); path.write_text('---\nname: outside\ndescription: Outside scope.\n---\n')
        git(repo, 'add', '.'); git(repo, 'commit', '--quiet', '-m', 'new outside scope skill')
        result = self.engine.prepare({'fastapi'})
        self.assertEqual(result['status'], 'bloqueado')
        self.assertEqual(result['details']['new_skill_paths_outside_scope']['fastapi'], ['outside/SKILL.md'])
        self.assertEqual(tree(self.root / 'Skills'), self.before)

    def test_license_change_blocks_promotion(self):
        path = self.repos['fastapi'] / 'LICENSE'
        path.write_text('Unknown license terms require manual review.\n')
        self.change()
        result = self.engine.prepare({'fastapi'})
        self.assertEqual(result['status'], 'bloqueado')
        self.assertIn('Licença', result['motivo'])
        self.assertEqual(tree(self.root / 'Skills'), self.before)

    def test_changed_adaptation_context_blocks(self):
        p = self.repos["fastapi"] / "fastapi/.agents/skills/fastapi/SKILL.md"
        p.write_text(p.read_text().replace("# FastAPI", "# Revised FastAPI", 1))
        git(self.repos["fastapi"], "add", "."); git(self.repos["fastapi"], "commit", "--quiet", "-m", "changed adaptation context")
        result = self.engine.prepare({"fastapi"})
        self.assertEqual(result["status"], "bloqueado"); self.assertIn("adaptação", result["motivo"])
        self.assertEqual(tree(self.root / "Skills"), self.before)

    def test_licenses_provenance_and_classifications_preserved(self):
        self.change(); plan = self.plan(); self.apply(plan)
        cat = load(self.root, "Skills/catalogo.json")
        self.assertEqual({s["id"]: s["distribution_status"] for s in cat["skills"]}, {s["id"]: s["distribution_status"] for s in self.original["skills"]})
        p = load(self.root, "Skills/Backend/fastapi/PROVENANCE.json")
        self.assertEqual(p["commit"], git(self.repos["fastapi"], "rev-parse", "HEAD"))
        self.assertEqual((self.root / "Skills/Backend/fastapi/LICENSE").read_bytes(), (ROOT / "Skills/Backend/fastapi/LICENSE").read_bytes())

    def test_adapted_skill_update_replays_contract_and_new_resource(self):
        repo = self.repos["fastapi"]
        new = repo / "fastapi/.agents/skills/fastapi/references/new-guide.md"; new.write_text("# Novo recurso\n")
        self.change(relative="fastapi/.agents/skills/fastapi/SKILL.md", text="\nNova orientação técnica.\n")
        plan = self.plan(); self.apply(plan)
        skill = (self.root / "Skills/Backend/fastapi/skills/fastapi/SKILL.md").read_text()
        self.assertIn("Nova orientação técnica", skill)
        self.assertEqual(skill.count("## StackNauta distribution"), 1)
        self.assertEqual((self.root / "Skills/Backend/fastapi/skills/fastapi/references/new-guide.md").read_text(), "# Novo recurso\n")

    def test_new_unmet_prerequisite_blocks(self):
        self.change(relative="fastapi/.agents/skills/fastapi/SKILL.md", text="\nRequires nonexistent-tool for runtime.\n")
        result = self.engine.prepare({"fastapi"}); self.assertEqual(result["status"], "bloqueado")
        self.assertIn("pré-requisito", result["motivo"])
        self.assertEqual(tree(self.root / "Skills"), self.before)

    def test_new_python_external_dependency_requires_manual_review(self):
        p = self.repos["fastapi"] / "fastapi/.agents/skills/fastapi/helper.py"; p.write_text("import definitely_not_installed_dependency\n")
        self.change()
        result = self.engine.prepare({"fastapi"}); self.assertEqual(result["status"], "bloqueado")
        self.assertIn("dependência Python", result["motivo"])

    def test_new_javascript_external_dependency_requires_manual_review(self):
        p = self.repos['fastapi'] / 'fastapi/.agents/skills/fastapi/helper.mjs'
        p.write_text('import missing from "definitely-not-installed";\n')
        self.change(); result = self.engine.prepare({'fastapi'})
        self.assertEqual(result['status'], 'bloqueado')
        self.assertIn('dependência JavaScript', result['motivo'])
        self.assertEqual(tree(self.root / 'Skills'), self.before)

    def test_new_javascript_local_import_requires_resource(self):
        p = self.repos['fastapi'] / 'fastapi/.agents/skills/fastapi/helper.mjs'
        p.write_text('import missing from "./missing-resource.mjs";\n')
        self.change(); result = self.engine.prepare({'fastapi'})
        self.assertEqual(result['status'], 'bloqueado')
        self.assertIn('Recurso JavaScript local', result['motivo'])
        self.assertEqual(tree(self.root / 'Skills'), self.before)

    def test_javascript_local_resources_are_validated_without_execution(self):
        folder = self.repos['fastapi'] / 'fastapi/.agents/skills/fastapi'
        (folder / 'helper.mjs').write_text('import {value} from "./resource.mjs";\nthrow new Error("Never execute vendor");\n')
        (folder / 'resource.mjs').write_text('export const value = 1;\n')
        self.change(); plan = self.plan(); self.apply(plan)
        self.engine.validator(self.root)
        self.assertTrue((self.root / 'Skills/Backend/fastapi/skills/fastapi/resource.mjs').is_file())

    def test_missing_node_runtime_records_pending_without_promotion(self):
        p = self.repos['fastapi'] / 'fastapi/.agents/skills/fastapi/helper.mjs'
        p.write_text('export const value = 1;\n'); self.change()
        with patch('stacknauta_core.runtimes.AsdfResolver.resolve', side_effect=BootstrapError('Node global ausente')):
            result = self.engine.prepare({'fastapi'})
        self.assertEqual(result['status'], 'bloqueado'); self.assertIn('Node global ausente', result['motivo'])
        self.assertTrue((self.engine.session(result['session_id']) / 'blocked.json').is_file())
        self.assertEqual(tree(self.root / 'Skills'), self.before)

    def test_new_unresolved_reference_blocks(self):
        self.change(text="\n[Recurso obrigatório](missing-required.md)\n")
        self.assertEqual(self.engine.prepare({"fastapi"})["status"], "bloqueado")
        self.assertEqual(tree(self.root / "Skills"), self.before)

    def test_closure_validation_checks_available_paths_not_full_package(self):
        sys.path.insert(0, str(ROOT / "Skills/validacao"))
        from validar_biblioteca import check_links
        folder = self.base / "closure"; folder.mkdir()
        (folder / "one.md").write_text("[dependência](two.md)")
        (folder / "two.md").write_text("not selected")
        self.assertTrue(check_links(folder, ["one.md"], {"one.md"})[1])
        self.assertFalse(check_links(folder, ["one.md"], {"one.md", "two.md"})[1])

    def test_source_content_must_match_git_blob(self):
        self.change(); original = self.engine.git.acquire
        def corrupt(source, repo):
            original(source, repo)
            p = repo / "fastapi/.agents/skills/fastapi/references/dependencies.md"; p.write_text("uncommitted corruption")
        with patch.object(self.engine.git, "acquire", side_effect=corrupt):
            result = self.engine.prepare({"fastapi"})
        self.assertEqual(result["status"], "bloqueado"); self.assertIn("Blob Git", result["motivo"])
        self.assertEqual(tree(self.root / "Skills"), self.before)

    def test_post_publication_validation_failure_rolls_back(self):
        self.change(); plan = self.plan(); validate = self.engine.validator
        def reject_new_active(root):
            if root == self.root and load(root, "Skills/fontes.lock.json")["sources"][1]["commit"] != self.original["sources"][1]["commit"]:
                raise ValueError("Falha de validação pós-publicação")
            return validate(root)
        self.engine.validator = reject_new_active
        with self.assertRaisesRegex(ValueError, "pós-publicação"): self.apply(plan)
        self.assertEqual(tree(self.root / "Skills"), self.before)
        validate(self.root)

    def test_state_symlink_and_unknown_source_are_rejected(self):
        with self.assertRaises(ValueError): self.engine.prepare({"new-source"})
        outside = self.base / "outside"; outside.mkdir()
        (self.root / ".stacknauta-updates").symlink_to(outside, target_is_directory=True)
        self.change()
        with self.assertRaises(ValueError): self.engine.prepare({"fastapi"})
        self.assertFalse(list(outside.iterdir()))

    def test_failure_after_old_move_restores_consistency(self):
        self.change(); plan = self.plan()
        def fail(phase):
            if phase == "old_moved": raise OSError("falha simulada")
        with self.assertRaises(OSError): self.apply(plan, hook=fail)
        self.assertEqual(tree(self.root / "Skills"), self.before); self.engine.validator(self.root)

    def test_failure_after_new_publish_restores_consistency(self):
        self.change(); plan = self.plan()
        with self.assertRaises(OSError): self.apply(plan, hook=lambda phase: (_ for _ in ()).throw(OSError("falha")) if phase == "new_published" else None)
        self.assertEqual(tree(self.root / "Skills"), self.before)

    def test_explicit_recovery_when_active_skills_is_absent(self):
        self.change(); plan = self.plan(); session = self.engine.session(plan["session_id"])
        move(self.root / "Skills", session / "previous-Skills")
        atomic_json(session / "journal.json", {"phase": "old_moved", "plan_id": plan["plan_id"]})
        r = subprocess.run([str(self.root / "Automacao/manutencao-skills/skills"), "recover", plan["session_id"], "--approve"], capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr); self.assertEqual(tree(self.root / "Skills"), self.before)

    def test_reexecution_has_no_updates_and_same_apply_is_noop(self):
        self.change(); plan = self.plan(); self.apply(plan); before = tree(self.root / "Skills")
        def metadata():
            return {p.relative_to(self.root).as_posix(): (p.stat().st_ino, p.stat().st_mode, p.stat().st_mtime_ns, p.stat().st_ctime_ns)
                    for p in (self.root / "Skills").rglob('*') if p.is_file()}
        original_metadata = metadata()
        self.assertEqual(self.apply(plan)["status"], "ja_aplicado"); self.assertEqual(tree(self.root / "Skills"), before)
        self.assertEqual(metadata(), original_metadata)
        git(self.root, "add", "Skills"); git(self.root, "commit", "--quiet", "-m", "record update")
        self.assertEqual(self.engine.prepare({"fastapi"})["status"], "sem_alteracoes")

    def test_approval_hash_and_local_changes_are_required(self):
        self.change(); plan = self.plan()
        with self.assertRaises(ValueError): self.engine.apply(plan["session_id"], plan["plan_id"])
        with self.assertRaises(ValueError): self.engine.apply(plan["session_id"], "0" * 64, approve=True)
        (self.root / "README.md").write_text("local change")
        with self.assertRaises(ValueError): self.apply(plan)
        self.assertEqual(tree(self.root / "Skills"), self.before)

    def test_mismatched_journal_is_not_authorized(self):
        self.change(); plan = self.plan(); session = self.engine.session(plan['session_id'])
        atomic_json(session / 'journal.json', {'phase': 'prepared', 'plan_id': '0' * 64})
        with self.assertRaisesRegex(ValueError, 'Diário'): self.apply(plan)
        with self.assertRaisesRegex(ValueError, 'Diário'): self.engine.recover(plan['session_id'], approve=True)
        self.assertEqual(tree(self.root / 'Skills'), self.before)

    def test_unsafe_paths_links_and_tampered_candidate_are_blocked(self):
        for path in ("../outside", "/outside", "a/../b", ".git/config"):
            with self.assertRaises(ValueError): safe(self.root, path)
        self.change(); plan = self.plan(); session = self.engine.session(plan["session_id"])
        p = session / "candidate/Skills/Backend/fastapi/LICENSE"; p.write_text("tampered")
        with self.assertRaises(ValueError): self.apply(plan)
        self.assertEqual(tree(self.root / "Skills"), self.before)

    def test_candidate_automation_is_sealed_before_validation(self):
        self.change(); plan = self.plan(); session = self.engine.session(plan['session_id'])
        path = session / 'candidate/Automacao/manutencao-skills/atualizacao_receita.py'
        path.write_text('raise RuntimeError("Candidate automation must not execute")\n')
        with self.assertRaisesRegex(ValueError, 'Candidato alterado'): self.apply(plan)
        self.assertEqual(tree(self.root / 'Skills'), self.before)

    def test_source_symlink_escape_is_blocked(self):
        p = self.repos["fastapi"] / "fastapi/.agents/skills/fastapi/escape"; p.symlink_to("/etc/passwd")
        git(self.repos["fastapi"], "add", "."); git(self.repos["fastapi"], "commit", "--quiet", "-m", "unsafe link")
        self.assertEqual(self.engine.prepare({"fastapi"})["status"], "bloqueado")
        self.assertEqual(tree(self.root / "Skills"), self.before)

    def test_missing_repo(self):
        source = self.engine.sources()[0]; source["url"] = str(self.base / "does-not-exist")
        with self.assertRaises(ValueError): self.engine.git.remote(source)


if __name__ == "__main__": unittest.main(verbosity=2)
