"""Integração comum, destinos temporários e nenhuma execução de outros agentes."""
import sys
sys.dont_write_bytecode = True
import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Automacao/validacao-project-bootstrap"))
from test_bootstrap import Base, FakeResolver
from stacknauta_core import BootstrapError
from stacknauta_core.core import Bootstrap
from stacknauta_core.integration import AgentIntegration, MARKER, additions
from stacknauta_core.library import Library, digest


class IntegrationTests(Base):
    def setUp(self):
        super().setUp()
        self.integration = AgentIntegration(self.engine)

    def test_dry_run_has_two_hashes_and_no_destination(self):
        plan, files, report = self.integration.plan(self.request(frameworks=("fastapi",), features=("api",)))
        self.assertFalse(self.destination.exists())
        self.assertEqual(report["core_plan_id"], plan.plan_id)
        self.assertNotEqual(report["plan_id"], plan.plan_id)
        self.assertEqual(len(report["integration_files"]), len(files))
        self.assertTrue(report["discovery_entries"])

    def test_wrong_hash_and_core_hash_cannot_authorize_integration(self):
        raw = self.request()
        plan, _, _ = self.integration.plan(raw)
        for value in ("0" * 64, plan.plan_id):
            with self.assertRaisesRegex(BootstrapError, "dry-run"):
                self.integration.apply(raw, value)
        self.assertFalse(self.destination.exists())

    def test_apply_copies_full_originals_and_portable_entries(self):
        raw = self.request(frameworks=("fastapi",), features=("api",))
        plan, files, report = self.integration.plan(raw)
        result = self.integration.apply(raw, report["plan_id"])
        self.assertEqual(result["status"], "verified")
        for path, data in {**plan.files, **files}.items():
            physical = self.destination / path
            self.assertFalse(physical.is_symlink())
            self.assertEqual(physical.stat().st_nlink, 1)
            self.assertEqual(physical.read_bytes(), data)
        for entry in report["discovery_entries"]:
            self.assertEqual(digest((self.destination / entry["original_path"]).read_bytes()), entry["original_sha256"])
            self.assertEqual(entry["commit"], Library(ROOT).skills[entry["id"]]["commit"])
            text = (self.destination / entry["path"]).read_text()
            link = re.search(r"\]\(([^)]+)\)", text)[1]
            self.assertEqual(((self.destination / entry["path"]).parent / link).resolve(), (self.destination / entry["original_path"]).resolve())
        self.assertFalse((self.destination / "GEMINI.md").exists())

    def test_shared_instructions_and_explicit_ui_selection_without_gemini(self):
        raw = self.request(("typescript",), ("react",), features=("ui",),
                           skills=["ui-ux-pro-max:ui-ux-pro-max", "gh-anthropics-skills:frontend-design"])
        raw["requirements"].update(description="Responsive web", constraints=["No dependency installation"])
        plan, files, report = self.integration.plan(raw)
        self.assertNotIn("GEMINI.md", plan.files | files)
        self.assertEqual(set(plan.selection["selected"]), set(raw["skills"]))
        self.assertIsNone(plan.config["stack"]["architecture"])
        self.integration.apply(raw, report["plan_id"])
        text = (self.destination / "AGENTS.md").read_text()
        for target in re.findall(r"\]\(([^)]+)\)", text):
            self.assertFalse(Path(target).is_absolute())
            self.assertTrue((self.destination / target).is_file(), target)
        self.assertIn("read .stacknauta/AGENT-INTEGRATION.md if present", text)
        self.assertTrue((self.destination / ".stacknauta/AGENT-INTEGRATION.md").is_file())
        self.assertIn("Explicit requirements and approved decisions take precedence", text)
        self.assertIn("Preserve StackNauta-managed", text)
        self.assertIn("Do not infer", text)
        self.assertNotIn("@./", text)
        self.assertNotIn("GEMINI.md", text)
        self.assertNotIn("Agent-specific integrations", text)
        self.assertEqual(json.loads((self.destination / "docs/REQUIREMENTS.json").read_text()), raw["requirements"])
        contract = (self.destination / ".stacknauta/AGENT-INTEGRATION.md").read_text()
        self.assertIn("Antigravity CLI", contract)
        self.assertNotIn("Gemini CLI use", contract)
        marker = json.loads((self.destination / MARKER).read_text())
        self.assertNotIn("GEMINI.md", marker["files"])
        self.assertEqual({e["name"] for e in report["discovery_entries"]},
                         {"stacknauta-ui-ux-pro-max", "stacknauta-frontend-design"})
        self.assertEqual(self.integration.verify(raw)["verification_state"], "intact")
        self.assertFalse((self.destination / "node_modules").exists())

    def test_idempotence_preserves_bytes_inode_mtime_and_original_core(self):
        raw = self.request(frameworks=("fastapi",))
        plan, _, report = self.integration.plan(raw)
        self.integration.apply(raw, report["plan_id"])
        snapshot = self.snapshot()
        self.integration.apply(raw, report["plan_id"])
        self.assertEqual(self.engine.apply(raw, plan.plan_id)["status"], "unchanged")
        self.assertEqual(self.snapshot(), snapshot)
        self.assertTrue(all(f["action"] == "unchanged" for f in self.integration.plan(raw)[2]["integration_files"]))

    def test_changed_configuration_requires_review(self):
        raw = self.request()
        report = self.integration.plan(raw)[2]
        raw["requirements"]["description"] = "changed"
        with self.assertRaises(BootstrapError):
            self.integration.apply(raw, report["plan_id"])
        self.assertFalse(self.destination.exists())

    def test_pending_and_incompatible_skills_block(self):
        pending = next(s["id"] for s in Library(ROOT).skills.values() if s["distribution_status"] == "pending")
        for skill in (pending, "invented:unknown"):
            with self.assertRaises(BootstrapError):
                self.integration.plan(self.request(skills=[skill]))
        raw = self.request(("typescript",), ("nextjs",), features=("ui",))
        ids = self.integration.plan(raw)[0].selection["selected"]
        self.assertFalse(any("fastapi" in s for s in ids))
        self.assertTrue(all(Library(ROOT).skills[s]["distribution_status"] == "approved" for s in ids))
        raw["skills"] = ["fastapi:fastapi"]
        with self.assertRaises(BootstrapError):
            self.integration.plan(raw)

    def test_missing_runtime_blocks_before_writes(self):
        engine = Bootstrap(ROOT, home=self.home, resolver=FakeResolver(missing=("nodejs",)))
        with self.assertRaisesRegex(BootstrapError, "Runtime global ausente"):
            AgentIntegration(engine).plan(self.request(("typescript",), ("nextjs",)))
        self.assertFalse(self.destination.exists())

    def test_user_gemini_file_is_unmanaged_and_preserved(self):
        raw = self.request()
        plan = self.engine.plan(raw)
        self.engine.apply(raw, plan.plan_id)
        (self.destination / "GEMINI.md").write_text("user context")
        before = self.snapshot()
        report = self.integration.plan(raw)[2]
        self.integration.apply(raw, report["plan_id"])
        after = self.snapshot()
        self.assertTrue(all(after[p] == value for p, value in before.items()))
        self.assertIn("GEMINI.md", [e["path"] for e in self.integration.verify(raw)["integration_lifecycle"]["unmanaged"]])

    def test_dangerous_symlink_and_hardlink_block(self):
        for kind in ("symlink", "hardlink"):
            self.destination = self.temp / kind
            raw = self.request(); plan = self.engine.plan(raw)
            self.engine.apply(raw, plan.plan_id)
            outside = self.temp / (kind + "-outside"); outside.write_text("untouched")
            target = self.destination / ".stacknauta/AGENT-INTEGRATION.md"
            target.symlink_to(outside) if kind == "symlink" else os.link(outside, target)
            with self.assertRaises(BootstrapError):
                self.integration.plan(raw)
            self.assertEqual(outside.read_text(), "untouched")

    def test_permission_failure_preserves_existing_files(self):
        raw = self.request(); plan = self.engine.plan(raw)
        self.engine.apply(raw, plan.plan_id)
        report = self.integration.plan(raw)[2]
        before = self.snapshot()
        # A integração agora publica apenas em subdiretórios, sem GEMINI.md na raiz.
        protected = self.destination / ".stacknauta"
        protected.chmod(0o555)
        try:
            if os.geteuid() == 0:
                self.skipTest("Permission semantics require an unprivileged user")
            with self.assertRaisesRegex(BootstrapError, "interrompida"):
                self.integration.apply(raw, report["plan_id"])
        finally:
            protected.chmod(0o755)
        self.assertEqual(before, self.snapshot())

    def test_partial_failure_resumes_without_overwrite(self):
        raw = self.request(frameworks=("fastapi",))
        report = self.integration.plan(raw)[2]
        from stacknauta_core.integration import publish
        count = 0
        def interrupted(*args):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError("simulated interruption")
            return publish(*args)
        with patch("stacknauta_core.integration.publish", side_effect=interrupted):
            with self.assertRaisesRegex(BootstrapError, "interrompida"):
                self.integration.apply(raw, report["plan_id"])
        before = self.snapshot()
        self.integration.apply(raw, report["plan_id"])
        after = self.snapshot()
        self.assertTrue(all(after[p] == info for p, info in before.items()))

    def test_verify_rejects_absent_or_damaged_files(self):
        raw = self.request()
        with self.assertRaisesRegex(BootstrapError, "incompleto"):
            self.integration.verify(raw)
        report = self.integration.plan(raw)[2]
        self.integration.apply(raw, report["plan_id"])
        (self.destination / MARKER).write_text("damaged")
        with self.assertRaises(BootstrapError):
            self.integration.verify(raw)

    def test_no_skills_no_invented_aliases(self):
        _, files, report = self.integration.plan(self.request(skills=[]))
        self.assertEqual(report["discovery_entries"], [])
        self.assertFalse(any(p.endswith("SKILL.md") for p in files))

    def test_portable_without_cache_and_personal_root(self):
        library = self.minimal_library()
        engine = Bootstrap(library, home=self.home, resolver=FakeResolver())
        raw = self.request(frameworks=("fastapi",))
        integration = AgentIntegration(engine)
        _, files, report = integration.plan(raw)
        integration.apply(raw, report["plan_id"])
        for data in files.values():
            self.assertNotIn(str(ROOT).encode(), data)
            self.assertNotIn(b"_repos/", data)
            self.assertNotIn(b"/home/", data)
        self.assertFalse((library / "Skills/_repos").exists())

    def test_cli_requires_reviewed_hash(self):
        config = self.temp / "config.json"; config.write_text(json.dumps(self.request()))
        result = subprocess.run([str(ROOT / "Automacao/project-bootstrap/project-bootstrap"), "agent-apply", "--config", str(config)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.destination.exists())

    def test_all_approved_alias_names_and_descriptions_are_valid(self):
        catalog = Library(ROOT).skills
        selected = [s for s in catalog.values() if s["distribution_status"] == "approved"]
        # Test projection metadata independently of compatibility: not permission to select all.
        skill_files, _, skills = Library(ROOT).export({"roots": [s["id"] for s in selected], "selected": [s["id"] for s in selected]})
        class Projection:
            plan_id = "0" * 64
            files = {**skill_files, ".stacknauta/skills-lock.json": json.dumps({"skills": skills}).encode()}
        _, files, entries = additions(Projection(), ROOT)
        self.assertEqual(len(entries), len(selected))
        for entry in entries:
            self.assertLessEqual(len(entry["name"]), 64)
            self.assertEqual(len(Path(entry["path"]).parts), 4)
            text = files[entry["path"]].decode()
            self.assertTrue(text.startswith("---\nname: "))
            description = json.loads(next(s for s in text.splitlines() if s.startswith("description: ")).removeprefix("description: "))
            self.assertTrue(description)
            self.assertLessEqual(len(description), 1024)


if __name__ == "__main__":
    unittest.main()
