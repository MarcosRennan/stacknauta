"""Regressões 2D: evolução, proteção, publicação parcial e formatos anteriores."""
import sys
sys.dont_write_bytecode = True
import json
import os
import stat
from pathlib import Path
from unittest.mock import patch

from test_bootstrap import Base, ROOT
from stacknauta_core import BootstrapError
from stacknauta_core.core import encoded
from stacknauta_core.core import Bootstrap
from stacknauta_core.filesystem import MANIFEST, directory, fingerprint, inspect_files
from stacknauta_core.integration import AgentIntegration, additions, MARKER
from stacknauta_core.library import digest
from stacknauta_core.lifecycle import classification, COMPLETION


class LifecycleTests(Base):
    def setUp(self):
        super().setUp()
        self.integration = AgentIntegration(self.engine)

    def start(self, raw=None):
        raw = raw or self.request(frameworks=("fastapi",))
        plan, files, report = self.integration.plan(raw)
        self.integration.apply(raw, report["plan_id"])
        return raw, plan, report

    def full_snapshot(self):
        result = {}
        for parent, dirs, files in os.walk(self.destination, followlinks=False):
            for name in dirs + files:
                p = Path(parent) / name
                s = p.lstat()
                row = (s.st_mode, s.st_ino, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
                if stat.S_ISREG(s.st_mode):
                    row += (p.read_bytes(),)
                result[p.relative_to(self.destination).as_posix()] = row
        return result

    def legacy(self, *, integrated):
        """Fixture de formato 1, sem campos 2D ou marcador novo, não uma migração."""
        raw = self.request(frameworks=("fastapi",))
        fresh = self.engine.plan(raw)
        identity = json.loads(fresh.manifest)
        identity.pop("plan_id"); identity.pop("lifecycle")
        identity["schema_version"] = 1
        manifest = encoded({**identity, "plan_id": digest(encoded(identity))})
        self.destination.mkdir()
        for relative, data in {MANIFEST: manifest, **fresh.files}.items():
            p = self.destination / relative; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(data)
        legacy_plan = self.engine.plan(raw)
        if integrated:
            _, files, _ = additions(legacy_plan, ROOT)
            for relative, data in files.items():
                p = self.destination / relative; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(data)
        return raw, legacy_plan

    def test_new_manifest_policy_and_final_completion(self):
        order = []
        raw = self.request()
        plan = self.engine.plan(raw)
        self.engine.apply(raw, plan.plan_id, hook=order.append)
        manifest = json.loads(plan.manifest)
        self.assertEqual(manifest["schema_version"], 2)
        self.assertEqual(manifest["lifecycle"]["files"]["pyproject.toml"], "evolutive")
        self.assertEqual(order[-1], COMPLETION)
        self.assertEqual(json.loads((self.destination / COMPLETION).read_text())["manifest_sha256"], digest(plan.manifest))

    def test_intact_agent_bootstrap_verifies(self):
        raw, _, _ = self.start()
        result = self.integration.verify(raw)
        self.assertEqual(result["verification_state"], "intact")
        self.assertFalse(result["lifecycle"]["modified"])

    def test_historical_gemini_policy_preserves_evolution_and_removal(self):
        # Contrato persistido, independente da ausência desse arquivo em planos novos.
        self.assertEqual(classification("GEMINI.md"), "evolutive")
        self.destination.mkdir()
        path = self.destination / "GEMINI.md"
        expected = {"GEMINI.md": b"# historical context\n"}
        path.write_bytes(expected["GEMINI.md"])
        with directory(self.destination) as root:
            self.assertEqual(inspect_files(root, expected, completed=True)["modified"], {})
            path.write_text("# user evolution\n")
            self.assertIn("GEMINI.md", inspect_files(root, expected, completed=True)["modified"])
            path.unlink()
            state = inspect_files(root, expected, completed=True)
            self.assertEqual(state["removed"], ["GEMINI.md"])
            self.assertEqual(state["create"], [])

    def test_unrelated_catalog_and_source_changes_preserve_pinned_consumer(self):
        library=self.minimal_library()
        self.engine=Bootstrap(library,home=self.home,resolver=self.engine.resolver)
        self.integration=AgentIntegration(self.engine)
        raw,_,report=self.start()
        (self.destination/'pyproject.toml').write_text('# legitimate evolution\n')
        before=self.full_snapshot()
        cat_path=library/'Skills/catalogo.json';lock_path=library/'Skills/fontes.lock.json'
        cat=json.loads(cat_path.read_bytes());lock=json.loads(lock_path.read_bytes())
        import copy
        row=copy.deepcopy(next(s for s in cat['skills'] if s['source_id']!='fastapi'))
        row['id']='fixture:unrelated';row['name']='unrelated';row['distribution_status']='pending'
        cat['skills'].append(row)
        cat_path.write_bytes(encoded(cat))
        self.assertEqual(self.integration.verify(raw)['status'],'verified')
        sid=next(s['id'] for s in lock['sources'] if s['id']!='fastapi')
        for source in cat['sources']+lock['sources']:
            if source['id']==sid:source['commit']='a'*40
        cat_path.write_bytes(encoded(cat));lock_path.write_bytes(encoded(lock))
        self.assertEqual(self.integration.verify(raw)['status'],'verified')
        self.assertEqual(self.integration.apply(raw,report['plan_id'])['core_result']['status'],'unchanged')
        self.assertEqual(before,self.full_snapshot())

    def test_schema_one_after_catalog_drift_preserves_original_ids(self):
        library=self.minimal_library()
        self.engine=Bootstrap(library,home=self.home,resolver=self.engine.resolver)
        self.integration=AgentIntegration(self.engine)
        raw,plan=self.legacy(integrated=True)
        before=self.full_snapshot()
        path=library/'Skills/catalogo.json';catalog=json.loads(path.read_bytes())
        catalog['fixture_note']='Unrelated catalog revision'
        path.write_bytes(encoded(catalog))
        self.assertEqual(self.integration.verify(raw)['core_plan_id'],plan.plan_id)
        self.assertEqual(self.engine.apply(raw,plan.plan_id)['status'],'unchanged')
        self.assertEqual(before,self.full_snapshot())

    def test_missing_historical_origin_evidence_blocks_without_writes(self):
        raw,_,_=self.start()
        path=self.destination/'.stacknauta/skills-lock.json'
        lock=json.loads(path.read_bytes());lock.pop('files');path.write_bytes(encoded(lock))
        before=self.full_snapshot()
        with self.assertRaisesRegex(BootstrapError,'evidência histórica'):
            self.integration.verify(raw)
        self.assertEqual(before,self.full_snapshot())

    def test_pyproject_growth_shrink_and_same_size_are_evolution(self):
        raw, plan, report = self.start()
        path = self.destination / "pyproject.toml"
        original = path.read_bytes()
        for data in (original + b"\n# approved dependencies\n" * 100, b"# shorter\n", b"x" * len(original)):
            path.write_bytes(data)
            preview = self.integration.plan(raw)[2]
            self.assertEqual(preview["plan_id"], report["plan_id"])
            self.assertEqual(preview["lifecycle"]["modified"]["pyproject.toml"]["original"]["sha256"], digest(original))
            self.assertEqual(next(f["action"] for f in preview["files"] if f["path"] == "pyproject.toml"), "preserve_modified")
            self.assertEqual(self.integration.verify(raw)["verification_state"], "verified_with_evolution")
        self.assertEqual((self.destination / MANIFEST).read_bytes(), plan.manifest)

    def test_package_json_evolves_with_no_overwrite(self):
        raw, _, report = self.start(self.request(("typescript",), ("nextjs",)))
        path = self.destination / "package.json"
        data = json.loads(path.read_text()); data["scripts"] = {"dev": "user-defined"}
        path.write_text(json.dumps(data))
        before = self.full_snapshot()
        self.integration.apply(raw, report["plan_id"])
        self.assertEqual(before, self.full_snapshot())
        self.assertIn("package.json", self.integration.verify(raw)["lifecycle"]["modified"])

    def test_reapply_preserves_evolved_bytes_inode_permissions_timestamps(self):
        raw, _, report = self.start()
        path = self.destination / "pyproject.toml"; path.write_text("# development\n")
        path.chmod(0o640); os.utime(path, ns=(1_700_000_000_000_000_000, 1_700_000_000_123_456_789))
        before = self.full_snapshot()
        for _ in range(2):
            self.assertEqual(self.integration.apply(raw, report["plan_id"])["core_result"]["status"], "unchanged")
            self.assertEqual(before, self.full_snapshot())

    def test_documentation_configs_and_gemini_can_evolve(self):
        raw, _, report = self.start()
        for name in ("README.md", "AGENTS.md", "GEMINI.md", ".gitignore", "docs/REQUIREMENTS.json"):
            (self.destination / name).write_text("development " + name)
        before = self.full_snapshot()
        self.integration.apply(raw, report["plan_id"])
        self.assertEqual(before, self.full_snapshot())
        self.assertIn("GEMINI.md", [e["path"] for e in self.integration.verify(raw)["integration_lifecycle"]["unmanaged"]])

    def test_classification_is_path_based_and_defaults_closed(self):
        for p in (".stacknauta/config.json", ".agents/skills/a/references/README.md", "unknown.json", ".tool-versions"):
            self.assertEqual(classification(p), "protected")
        for p in ("pyproject.toml", "package.json", "AGENTS.md"):
            self.assertEqual(classification(p), "evolutive")
        self.assertEqual(classification("src/lib.rs"), "development")

    def test_evolution_does_not_hide_protected_tampering(self):
        protected = [MANIFEST, COMPLETION, ".stacknauta/skills-lock.json", ".stacknauta/agent-plan.json",
                     MARKER, ".tool-versions", ".agents/skills/backend-fastapi/PROVENANCE.json",
                     ".agents/skills/backend-fastapi/skills/fastapi/SKILL.md",
                     ".agents/skills/backend-fastapi/skills/fastapi/references/dependencies.md",
                     ".agents/skills/stacknauta-fastapi/SKILL.md"]
        for index, relative in enumerate(protected):
            with self.subTest(relative=relative):
                self.destination = self.temp / f"tampered-{index}"
                raw, _, report = self.start()
                (self.destination / "pyproject.toml").write_text("# user evolution\n")
                path = self.destination / relative; path.write_bytes(path.read_bytes() + b"\nforbidden\n")
                before = self.full_snapshot()
                with self.assertRaises(BootstrapError): self.integration.verify(raw)
                with self.assertRaises(BootstrapError): self.integration.apply(raw, report["plan_id"])
                self.assertEqual(before, self.full_snapshot())

    def test_protected_conflict_reports_hashes_without_original_size_limit(self):
        raw, _, _ = self.start()
        path = self.destination / ".agents/skills/backend-fastapi/LICENSE"
        path.write_text("corrupt" * 1000)
        with self.assertRaisesRegex(BootstrapError, "classe=protected; esperado=.*atual="):
            self.integration.verify(raw)

    def test_protected_size_mismatch_is_rejected_before_reading_payload(self):
        raw, plan, _ = self.start()
        name = ".agents/skills/backend-fastapi/LICENSE"
        (self.destination / name).write_bytes(b"x" * 100_000)
        expected = {"size": len(plan.files[name]), "sha256": digest(plan.files[name])}
        with directory(self.destination) as root_fd, patch("stacknauta_core.filesystem.os.read", side_effect=AssertionError("must not read oversized protected data")):
            with self.assertRaisesRegex(BootstrapError, "classe=protected"):
                fingerprint(root_fd, name, expected=expected)

    def test_unmanaged_source_tests_and_directories_are_preserved_and_reported(self):
        raw, _, report = self.start()
        for relative in ("src/feature/main.py", "tests/new_test.py", "docs/new.md"):
            p = self.destination / relative; p.parent.mkdir(parents=True, exist_ok=True); p.write_text("user content")
        before = self.full_snapshot(); result = self.integration.apply(raw, report["plan_id"])
        self.assertEqual(before, self.full_snapshot())
        additions_set = {x["path"] for x in result["lifecycle"]["unmanaged"]}
        self.assertIn("src/feature/main.py", additions_set); self.assertIn("tests/new_test.py", additions_set)

    def test_unknown_files_or_skills_in_protected_namespaces_are_forbidden(self):
        for index, relative in enumerate((".stacknauta/extra.json", ".agents/skills/unselected/SKILL.md", ".agents/skills/backend-fastapi/new.md")):
            self.destination = self.temp / f"extra-{index}"
            raw, _, _ = self.start()
            p = self.destination / relative; p.parent.mkdir(parents=True, exist_ok=True); p.write_text("untracked")
            with self.assertRaisesRegex(BootstrapError, "Adicional proibido"):
                self.integration.verify(raw)

    def test_removed_evolutive_files_and_placeholders_are_not_restored(self):
        raw, _, report = self.start()
        names = ("pyproject.toml", "README.md", "src/.gitkeep", "tests/.gitkeep", "AGENTS.md")
        for name in names: (self.destination / name).unlink()
        before = self.full_snapshot(); result = self.integration.apply(raw, report["plan_id"])
        self.assertEqual(before, self.full_snapshot())
        self.assertTrue(set(names) <= set(result["lifecycle"]["removed"]) | set(result["integration_lifecycle"]["removed"]))

    def test_removed_protected_file_is_detected_and_not_repaired(self):
        raw, _, report = self.start()
        (self.destination / ".stacknauta/skills-lock.json").unlink()
        before = self.full_snapshot()
        with self.assertRaisesRegex(BootstrapError, "protegido ausente"): self.integration.verify(raw)
        with self.assertRaises(BootstrapError): self.integration.apply(raw, report["plan_id"])
        self.assertEqual(before, self.full_snapshot())

    def test_removed_completion_is_incomplete_not_success(self):
        raw, _, _ = self.start()
        (self.destination / COMPLETION).unlink()
        with self.assertRaisesRegex(BootstrapError, "incompleto"): self.integration.verify(raw)

    def test_directory_replacing_evolutive_file_is_rejected(self):
        raw, _, _ = self.start()
        path = self.destination / "pyproject.toml"; path.unlink(); path.mkdir()
        with self.assertRaises(BootstrapError): self.integration.verify(raw)

    def test_regular_file_replacing_parent_directory_is_rejected(self):
        raw, _, _ = self.start()
        (self.destination / "src/.gitkeep").unlink(); (self.destination / "src").rmdir(); (self.destination / "src").write_text("file")
        with self.assertRaises(BootstrapError): self.integration.verify(raw)

    def test_evolutive_symlink_or_hardlink_cannot_escape(self):
        for kind in ("symlink", "hardlink"):
            self.destination = self.temp / kind
            raw, _, report = self.start(); outside = self.temp / (kind + "-outside"); outside.write_text("untouched")
            p = self.destination / "pyproject.toml"; p.unlink()
            p.symlink_to(outside) if kind == "symlink" else os.link(outside, p)
            with self.assertRaises(BootstrapError): self.integration.apply(raw, report["plan_id"])
            self.assertEqual(outside.read_text(), "untouched")

    def test_unmanaged_link_is_reported_and_never_followed(self):
        raw, _, report = self.start(); outside = self.temp / "outside"; outside.mkdir(); (outside / "note").write_text("untouched")
        (self.destination / "development-link").symlink_to(outside, target_is_directory=True)
        result = self.integration.apply(raw, report["plan_id"])
        self.assertIn({"path": "development-link", "kind": "symlink_not_followed"}, result["lifecycle"]["unmanaged"])
        self.assertNotIn("development-link/note", {x["path"] for x in result["lifecycle"]["unmanaged"]})
        self.assertEqual((outside / "note").read_text(), "untouched")

    def test_invalid_destination_paths_remain_blocked(self):
        for path in ("relative", str(self.temp / "a/../escape"), str(ROOT), "/"):
            with self.assertRaises(BootstrapError): self.integration.plan(self.request(destination=path))

    def test_partial_publication_before_evolutive_file_can_resume(self):
        raw = self.request(); plan = self.engine.plan(raw)
        def fail(relative):
            if relative == "pyproject.toml": raise OSError("injected")
        with self.assertRaises(BootstrapError): self.engine.apply(raw, plan.plan_id, hook=fail)
        self.assertFalse((self.destination / COMPLETION).exists())
        before = self.full_snapshot()
        self.engine.apply(raw, plan.plan_id)
        after = self.full_snapshot()
        # Diretórios recebem novas entradas; arquivos já publicados não mudam.
        self.assertTrue(all(after[p] == v for p, v in before.items() if stat.S_ISREG(v[0])))
        self.assertTrue((self.destination / "pyproject.toml").is_file())

    def test_interruption_at_completion_publishes_only_receipt_on_resume(self):
        raw = self.request(); plan = self.engine.plan(raw)
        def fail(relative):
            if relative == COMPLETION: raise OSError("injected final marker failure")
        with self.assertRaises(BootstrapError): self.engine.apply(raw, plan.plan_id, hook=fail)
        before = self.full_snapshot()
        result = self.engine.apply(raw, plan.plan_id)
        self.assertEqual(result["created_files"], 1)
        self.assertTrue(all(self.full_snapshot()[p] == v for p, v in before.items() if stat.S_ISREG(v[0])))

    def test_development_seed_can_change_or_be_removed_without_restoration(self):
        raw, _, report = self.start(self.request(("rust",)))
        p = self.destination / "src/lib.rs"; p.write_text("// subsequent development\n")
        before = self.full_snapshot(); self.integration.apply(raw, report["plan_id"])
        self.assertEqual(before, self.full_snapshot())
        p.unlink(); self.integration.apply(raw, report["plan_id"])
        self.assertFalse(p.exists())

    def test_format_one_core_reapply_has_no_migration_writes(self):
        raw, legacy = self.legacy(integrated=False)
        (self.destination / "pyproject.toml").write_text("# evolved legacy\n")
        before = self.full_snapshot()
        self.assertEqual(self.engine.apply(raw, legacy.plan_id)["status"], "unchanged")
        self.assertEqual(before, self.full_snapshot())
        self.assertFalse((self.destination / COMPLETION).exists())

    def test_format_one_agent_verify_and_reapply_preserve_original_ids(self):
        raw, legacy = self.legacy(integrated=True)
        original = self.integration.plan(raw)[2]
        (self.destination / "pyproject.toml").write_text("# evolved legacy\n")
        before = self.full_snapshot(); result = self.integration.apply(raw, original["plan_id"])
        self.assertEqual(result["plan_id"], original["plan_id"])
        self.assertEqual(result["core_plan_id"], legacy.plan_id)
        self.assertEqual(result["verification_state"], "verified_with_evolution")
        self.assertEqual(before, self.full_snapshot())

    def test_format_one_removed_evolutive_is_preserved_without_receipt(self):
        raw, legacy = self.legacy(integrated=False)
        (self.destination / "pyproject.toml").unlink()
        self.engine.apply(raw, legacy.plan_id)
        self.assertFalse((self.destination / "pyproject.toml").exists())

    def test_format_one_missing_protected_blocks_conservatively(self):
        raw, legacy = self.legacy(integrated=False)
        (self.destination / ".stacknauta/skills-lock.json").unlink()
        with self.assertRaisesRegex(BootstrapError, "protegido ausente"):
            self.engine.apply(raw, legacy.plan_id)

    def test_unknown_manifest_schema_and_policy_tampering_block(self):
        raw, _, _ = self.start()
        p = self.destination / MANIFEST; data=json.loads(p.read_text()); original=p.read_bytes()
        data["schema_version"] = 99; p.write_text(json.dumps(data))
        with self.assertRaisesRegex(BootstrapError, "schema"): self.integration.verify(raw)
        data=json.loads(original);data["lifecycle"]["files"][".stacknauta/skills-lock.json"]="evolutive";p.write_text(json.dumps(data))
        with self.assertRaises(BootstrapError): self.integration.verify(raw)

    def test_normalized_generated_config_is_accepted_without_changing_ids(self):
        raw, _, report = self.start()
        normalized=json.loads((self.destination / ".stacknauta/config.json").read_text())
        self.assertIsNone(normalized["skills"])
        self.assertEqual(self.integration.plan(normalized)[2]["plan_id"],report["plan_id"])

    def test_wrong_reviewed_hash_still_blocks_with_evolved_files(self):
        raw, _, _ = self.start(); (self.destination / "pyproject.toml").write_text("# evolved\n")
        before=self.full_snapshot()
        with self.assertRaisesRegex(BootstrapError,"plan_id"): self.integration.apply(raw,"0"*64)
        self.assertEqual(before,self.full_snapshot())

    def test_file_growth_during_streaming_verification_is_detected(self):
        raw, _, _ = self.start()
        leaf = self.destination / "pyproject.toml"
        actual_read = os.read
        changed = False
        def grow(fd, count):
            nonlocal changed
            data = actual_read(fd, count)
            if data and not changed:
                changed = True
                with leaf.open("ab") as stream: stream.write(b"\n# concurrent edit\n")
            return data
        with directory(self.destination) as root_fd, patch("stacknauta_core.filesystem.os.read", side_effect=grow):
            with self.assertRaisesRegex(BootstrapError, "mudou durante"):
                fingerprint(root_fd, "pyproject.toml")
