"""Política 4B: catálogos e consumidores sintéticos; nenhum fornecedor executado."""
import copy
import json
import shutil
from pathlib import Path
from unittest.mock import patch

from test_bootstrap import Base, ROOT, FakeResolver
from stacknauta_core import BootstrapError
from stacknauta_core.compatibility import declared_policy
from stacknauta_core.core import Bootstrap, encoded
from stacknauta_core.filesystem import MANIFEST
from stacknauta_core.integration import AgentIntegration
from stacknauta_core.library import Library, digest


POLICY = {"languages_any": ["javascript", "typescript"], "frameworks_any": [],
          "frameworks_all": [], "features_all": ["ui"], "architecture": None,
          "tools": [], "runtimes": []}


class SelectionTests(Base):
    def setUp(self):
        super().setUp()
        self.addCleanup(shutil.rmtree, self.temp)
        self.root = self.temp / "synthetic-library"
        self.folder = self.root / "Skills/Frontend/fixture"
        self.folder.mkdir(parents=True)
        for name in ("biblioteca.py", "inventariar.py"):
            target = self.root / "Skills/manutencao" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / "Skills/manutencao" / name, target)
        self.catalog = {"sources": [{"id": "fixture", "commit": "a" * 40}],
                        "skills": [], "distribution_packages": []}
        self.package = {"id": "Frontend/fixture", "directory": "Skills/Frontend/fixture",
                        "repository": "https://github.com/synthetic/fixture", "commit": "a" * 40,
                        "skills": [], "shared_files": ["LICENSE"], "files": {}}
        self.put("LICENSE", b"Synthetic fixture, no vendor code.\n")
        self.add_skill("general")
        self.save()
        self.engine = Bootstrap(self.root, home=self.home, resolver=FakeResolver())

    def put(self, path, data):
        target = self.folder / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        self.package["files"][path] = {"sha256": digest(data), "inputs": []}

    def add_skill(self, name, *, mode=None, status="approved", requires=(), policy=None):
        identifier = "fixture:" + name
        compatibility = copy.deepcopy(policy or POLICY)
        if mode is not None:
            compatibility["selection_mode"] = mode
        self.catalog["skills"].append({"id": identifier, "name": name, "description": "Synthetic " + name,
            "repository": self.package["repository"], "commit": self.package["commit"],
            "source_path": "skills/" + name + "/SKILL.md", "distribution_status": status,
            "compatibility": compatibility, "distribution": {
                "package": self.package["id"], "skill_directory": "skills/" + name,
                "requires_skills": list(requires)}})
        self.package["skills"].append(identifier)
        self.put("skills/" + name + "/SKILL.md", ("---\nname: " + name + "\ndescription: Synthetic\n---\nFixture.\n").encode())
        return identifier

    def save(self):
        manifest = encoded(self.package)
        (self.folder / "PROVENANCE.json").write_bytes(manifest)
        self.catalog["distribution_packages"] = [{"id": self.package["id"], "directory": self.package["directory"],
                                                    "manifest_sha256": digest(manifest)}]
        (self.root / "Skills/catalogo.json").write_bytes(encoded(self.catalog))
        (self.root / "Skills/fontes.lock.json").write_bytes(encoded({"sources": self.catalog["sources"]}))

    def web(self, **changes):
        return self.request(("typescript",), ("react",), ("ui", "animation"), **changes)

    def plan(self, **changes):
        self.save()
        return self.engine.plan(self.web(**changes))

    def test_historical_skill_without_metadata_keeps_automatic_selection(self):
        self.assertEqual(self.plan().selection["roots"], ["fixture:general"])
        self.assertNotIn("selection_mode", self.catalog["skills"][0]["compatibility"])

    def test_explicit_automatic_skill_is_selected(self):
        self.add_skill("automatic", mode="automatic")
        self.assertEqual(self.plan().selection["roots"], ["fixture:automatic", "fixture:general"])

    def test_explicit_is_not_selected_just_for_matching_technical_requirements(self):
        identifier = self.add_skill("specialist", mode="explicit")
        plan = self.plan(skills=None)
        self.assertEqual(plan.selection["selected"], ["fixture:general"])
        self.assertTrue(any(r["skill"] == identifier and "explícita" in r["reason"] for r in plan.selection["skipped"]))
        self.assertFalse(self.destination.exists())

    def test_matching_specialist_can_be_requested(self):
        identifier = self.add_skill("specialist", mode="explicit")
        self.assertEqual(self.plan(skills=[identifier]).selection["roots"], [identifier])

    def test_incompatible_specialist_requested_is_rejected(self):
        identifier = self.add_skill("specialist", mode="explicit", policy={**POLICY, "frameworks_all": ["vue"]})
        with self.assertRaisesRegex(BootstrapError, "vue"):
            self.plan(skills=[identifier])

    def test_pending_and_excluded_requests_are_rejected(self):
        for status in ("pending", "excluded"):
            identifier = self.add_skill(status, mode="explicit", status=status)
            with self.subTest(status=status), self.assertRaisesRegex(BootstrapError, "pendente ou excluída"):
                self.plan(skills=[identifier])
        self.assertFalse(self.destination.exists())

    def test_unknown_request_is_rejected(self):
        with self.assertRaisesRegex(BootstrapError, "inexistente"):
            self.plan(skills=["fixture:absent"])

    def test_duplicate_request_is_rejected(self):
        with self.assertRaisesRegex(BootstrapError, "duplicad"):
            self.plan(skills=["fixture:general", "fixture:general"])

    def test_explicit_list_is_complete_set_of_roots_including_automatic_and_specialist(self):
        identifier = self.add_skill("specialist", mode="explicit")
        self.assertEqual(self.plan(skills=[identifier]).selection["selected"], [identifier])
        self.assertEqual(self.plan(skills=[identifier, "fixture:general"]).selection["roots"], ["fixture:general", identifier])

    def test_missing_null_and_empty_list_keep_their_semantics(self):
        self.add_skill("specialist", mode="explicit")
        self.save()
        absent = self.engine.plan(self.web())
        null = self.engine.plan(self.web(skills=None))
        self.assertEqual(absent.plan_id, null.plan_id)
        self.assertEqual(self.plan(skills=[]).selection["selected"], [])

    def test_generic_frontend_ui_does_not_select_specialist(self):
        self.add_skill("specialist", mode="explicit")
        self.save()
        raw = self.web(); raw["requirements"]["features"] = ["ui"]
        self.assertEqual(self.engine.plan(raw).selection["selected"], ["fixture:general"])

    def test_backend_does_not_select_web_specialist(self):
        self.add_skill("specialist", mode="explicit")
        self.save()
        self.assertEqual(self.engine.plan(self.request()).selection["selected"], [])

    def test_explicit_root_keeps_automatic_dependencies(self):
        identifier = self.add_skill("specialist", mode="explicit", requires=["fixture:general"])
        plan = self.plan(skills=[identifier])
        self.assertEqual(plan.selection["roots"], [identifier])
        self.assertEqual(plan.selection["selected"], ["fixture:general", identifier])

    def test_automatic_root_cannot_pull_an_explicit_dependency(self):
        identifier = self.add_skill("specialist", mode="explicit")
        self.catalog["skills"][0]["distribution"]["requires_skills"] = [identifier]
        self.assertEqual(self.plan().selection["selected"], [])
        with self.assertRaisesRegex(BootstrapError, "explícita"):
            self.plan(skills=["fixture:general"])
        self.assertEqual(self.plan(skills=["fixture:general", identifier]).selection["selected"], ["fixture:general", identifier])

    def test_missing_and_pending_dependencies_are_rejected(self):
        identifier = self.add_skill("specialist", mode="explicit", requires=["fixture:absent"])
        with self.assertRaises(BootstrapError): self.plan(skills=[identifier])
        self.add_skill("absent", status="pending")
        with self.assertRaises(BootstrapError): self.plan(skills=[identifier])

    def test_runtime_and_tool_requirements_are_not_bypassed(self):
        identifier = self.add_skill("specialist", mode="explicit", policy={**POLICY, "runtimes": ["java"]})
        self.engine = Bootstrap(self.root, home=self.home, resolver=FakeResolver(missing=["java"]))
        with self.assertRaisesRegex(BootstrapError, "Runtime global ausente"):
            self.plan(skills=[identifier])
        self.catalog["skills"][-1]["compatibility"] = {**POLICY, "selection_mode": "explicit", "tools": ["fixture-measurer"]}
        with patch("stacknauta_core.library.shutil.which", return_value=None), self.assertRaisesRegex(BootstrapError, "ferramenta obrigatória"):
            self.plan(skills=[identifier])
        self.assertFalse(self.destination.exists())

    def test_missing_and_tampered_resources_still_block(self):
        identifier = self.add_skill("specialist", mode="explicit")
        self.save()
        path = self.folder / "skills/specialist/SKILL.md"
        original = path.read_bytes(); path.unlink()
        with self.assertRaises(BootstrapError): self.engine.plan(self.web(skills=[identifier]))
        path.write_bytes(original + b"tampered")
        with self.assertRaisesRegex(BootstrapError, "adulterado"):
            self.engine.plan(self.web(skills=[identifier]))

    def test_invalid_selection_metadata_fails_closed(self):
        for value in (None, "", "auto", True, [], {}):
            with self.subTest(value=value), self.assertRaises(BootstrapError):
                declared_policy({**POLICY, "selection_mode": value})

    def test_dry_run_is_deterministic_and_binds_catalog_policy(self):
        identifier = self.add_skill("specialist", mode="explicit")
        plan = self.plan(skills=[identifier])
        self.assertEqual(plan.report()["skills"]["roots"], [identifier])
        self.assertEqual(plan.plan_id, self.engine.plan(self.web(skills=[identifier])).plan_id)
        self.assertFalse(self.destination.exists())
        self.catalog["skills"][-1]["compatibility"]["selection_mode"] = "automatic"
        self.save()
        with self.assertRaisesRegex(BootstrapError, "plan_id"):
            self.engine.apply(self.web(skills=[identifier]), plan.plan_id)
        self.assertFalse(self.destination.exists())

    def test_agent_integration_and_idempotence_share_the_selection(self):
        identifier = self.add_skill("specialist", mode="explicit")
        self.save()
        raw = self.web(skills=["fixture:general", identifier])
        integration = AgentIntegration(self.engine)
        plan, files, report = integration.plan(raw)
        self.assertEqual(sorted(r["id"] for r in report["discovery_entries"]), plan.selection["selected"])
        self.assertNotIn("GEMINI.md", files)
        integration.apply(raw, report["plan_id"])
        snapshot = self.snapshot()
        self.assertEqual(integration.verify(raw)["verification_state"], "intact")
        self.assertEqual(integration.apply(raw, report["plan_id"])["core_result"]["status"], "unchanged")
        self.assertEqual(snapshot, self.snapshot())

    def test_schemas_one_and_two_preserve_pinned_locks_and_evolutive_files(self):
        identifier = self.add_skill("specialist", mode="explicit")
        self.save()
        for schema in (1, 2):
            with self.subTest(schema=schema):
                raw = self.web(destination=str(self.temp / ("consumer-" + str(schema))), skills=[identifier])
                fresh = self.engine.plan(raw)
                destination = Path(raw["destination"])
                if schema == 1:
                    identity = json.loads(fresh.manifest)
                    identity.pop("plan_id"); identity.pop("lifecycle"); identity["schema_version"] = 1
                    manifest = encoded({**identity, "plan_id": digest(encoded(identity))})
                    for relative, data in {MANIFEST: manifest, **fresh.files}.items():
                        path = destination / relative; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
                else:
                    self.engine.apply(raw, fresh.plan_id)
                protected = {p:(destination/p).read_bytes() for p in (MANIFEST, ".stacknauta/skills-lock.json")}
                package_json = destination / "package.json"
                package_json.write_text("{\"evolved\": true}\n")
                before = self.snapshot(destination)
                plan = self.engine.plan(raw)
                self.assertEqual(json.loads(plan.manifest)["schema_version"], schema)
                self.assertEqual(self.engine.apply(raw, plan.plan_id)["status"], "unchanged")
                self.assertEqual(before, self.snapshot(destination))
                self.assertEqual(protected, {p:(destination/p).read_bytes() for p in protected})

    def test_protected_consumer_files_still_block_when_tampered(self):
        identifier = self.add_skill("specialist", mode="explicit")
        self.save()
        for relative in (MANIFEST, ".stacknauta/skills-lock.json", ".agents/skills/frontend-fixture/skills/specialist/SKILL.md"):
            with self.subTest(relative=relative):
                raw = self.web(destination=str(self.temp / ("tamper-" + str(len(relative)))), skills=[identifier])
                plan = self.engine.plan(raw); self.engine.apply(raw, plan.plan_id)
                path = Path(raw["destination"]) / relative
                path.write_bytes(path.read_bytes() + b"tampered")
                with self.assertRaises(BootstrapError): self.engine.plan(raw)
