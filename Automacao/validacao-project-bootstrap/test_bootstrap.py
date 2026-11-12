"""Testes stdlib: somente destinos temporários; runtimes sintéticos não são executados."""
import sys
sys.dont_write_bytecode = True
import copy
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "Automacao/project-bootstrap"
sys.path.insert(0, str(CORE))
from stacknauta_core import BootstrapError
from stacknauta_core.compatibility import policies
from stacknauta_core.config import normalize, load
from stacknauta_core.core import Bootstrap
from stacknauta_core.filesystem import MANIFEST, Target, directory, publish
from stacknauta_core.library import Library, digest
from stacknauta_core.runtimes import AsdfResolver, LANGUAGE_PLUGINS, EXECUTABLES


VERSIONS = {"python": "3.14.8", "nodejs": "24.21.0", "golang": "1.25.3", "java": "temurin-21.0.9+10", "rust": "1.90.0"}
OBSERVED = {"python": "3.14.8", "node": "24.21.0", "go": "1.25.3", "java": "21.0.9", "javac": "21.0.9", "rustc": "1.90.0", "cargo": "1.90.0"}


class FakeResolver:
    def __init__(self, missing=()):
        self.missing = set(missing)
        self.diagnostics = [{"test": "synthetic runtimes, no installation or execution"}]

    def resolve(self, languages, requested=None, extra_plugins=()):
        apps = {LANGUAGE_PLUGINS[s] for s in languages}
        plugins = apps | {"python"} | set(extra_plugins)
        if plugins & self.missing:
            raise BootstrapError("Runtime global ausente: " + ", ".join(sorted(plugins & self.missing)))
        result = {}
        for plugin in sorted(plugins):
            if requested and plugin in requested and requested[plugin] != VERSIONS[plugin]:
                raise BootstrapError("Versão global diferente da solicitada")
            result[plugin] = {"version": VERSIONS[plugin], "detected": {name: OBSERVED[name] for name in EXECUTABLES[plugin]},
                              "roles": (["executor"] if plugin == "python" else []) + (["application"] if plugin in apps else []) or ["skill-helper"]}
        return result


class Base(unittest.TestCase):
    def setUp(self):
        self.temp = Path(tempfile.mkdtemp(prefix="stacknauta-core-test-"))
        self.home = self.temp / "home"
        self.home.mkdir()
        self.destination = self.temp / "project"
        self.engine = Bootstrap(ROOT, home=self.home, resolver=FakeResolver())

    def request(self, languages=("python",), frameworks=(), features=(), architecture=None, skills=None, **extra):
        request = {"name": "example", "destination": str(self.destination),
                   "stack": {"languages": list(languages), "frameworks": list(frameworks)},
                   "requirements": {"features": list(features)}}
        if architecture is not None:
            request["stack"]["architecture"] = architecture
        if skills is not None:
            request["skills"] = skills
        request.update(extra)
        return request

    def apply(self, request):
        plan = self.engine.plan(request)
        return self.engine.apply(request, plan.plan_id), plan

    def snapshot(self, root=None):
        root = root or self.destination
        return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_ino, p.stat().st_mtime_ns)
                for p in root.rglob("*") if p.is_file() and not p.is_symlink()}

    def minimal_library(self):
        library = self.temp / "portable-library"
        for relative in ("Skills/catalogo.json", "Skills/fontes.lock.json", "Skills/manutencao/biblioteca.py", "Skills/manutencao/inventariar.py"):
            target = library / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        shutil.copytree(ROOT / "Skills/Backend/fastapi", library / "Skills/Backend/fastapi")
        return library


class ConfigurationTests(Base):
    def test_valid_normalized_config_and_default_home(self):
        request = self.request()
        request.pop("destination")
        result = normalize(request, self.home)
        self.assertEqual(result["destination"], str(self.home / "Projetos/example"))
        self.assertIsNone(result["stack"]["architecture"])

    def test_invalid_names_no_writes(self):
        for name in ("../escape", "/absolute", "", "Name", "x/y", "x;touch", "a" * 65, 7):
            with self.subTest(name=name), self.assertRaises(BootstrapError):
                self.engine.plan(self.request(name=name))
        self.assertFalse(self.destination.exists())

    def test_invalid_types_and_unknown_fields(self):
        variants = [[], {"name": "example"}, self.request(schema_version=True), self.request(schema_version=1.0), self.request(extra="unknown")]
        for value in (None, "python", ["python", "python"], ["unknown"], [5]):
            request = self.request(); request["stack"]["languages"] = value; variants.append(request)
        for request in variants:
            with self.subTest(request=request), self.assertRaises(BootstrapError):
                self.engine.plan(request)
        self.assertFalse(self.destination.exists())

    def test_framework_must_not_choose_language(self):
        with self.assertRaisesRegex(BootstrapError, "explicitamente"):
            self.engine.plan(self.request(("python",), ("nextjs",)))

    def test_invalid_framework_objects(self):
        for entry in (["fastapi"], {"name": []}, {"name": "fastapi", "version": "latest"}, {"name": "fastapi", "version": "1.0\ncommand"}, {"name": "unknown"}):
            request = self.request(); request["stack"]["frameworks"] = [entry]
            with self.subTest(entry=entry), self.assertRaises(BootstrapError):
                self.engine.plan(request)

    def test_unknown_architecture_and_features(self):
        with self.assertRaises(BootstrapError):
            self.engine.plan(self.request(architecture="invented"))
        with self.assertRaises(BootstrapError):
            self.engine.plan(self.request(features=("invented-feature",)))

    def test_json_duplicate_keys_rejected(self):
        path = self.temp / "bad.json"; path.write_text('{"name":"first","name":"second"}')
        with self.assertRaisesRegex(BootstrapError, "duplicada"):
            load(path)

    def test_config_fifo_symlink_and_size_limit_rejected(self):
        fifo = self.temp / "pipe.json"; os.mkfifo(fifo)
        with self.assertRaises(BootstrapError):
            load(fifo)
        real = self.temp / "real.json"; real.write_text("{}")
        alias = self.temp / "alias.json"; alias.symlink_to(real)
        with self.assertRaises(BootstrapError):
            load(alias)
        real.write_bytes(b" " * 1_000_001)
        with self.assertRaisesRegex(BootstrapError, "1 MB"):
            load(real)

    def test_destination_traversal_relative_and_reserved(self):
        for destination in ("relative/path", str(self.temp / "x/../outside"), "/", str(self.home), str(self.temp / ".git/new"), "bad\x00path"):
            with self.subTest(destination=destination), self.assertRaises(BootstrapError):
                self.engine.plan(self.request(destination=destination))

    def test_go_module_is_explicit(self):
        with self.assertRaisesRegex(BootstrapError, "go_module"):
            self.engine.plan(self.request(("go",)))
        request = self.request(("go",)); request["stack"]["go_module"] = "example.org/team/project"
        self.assertIn("go.mod", self.engine.plan(request).files)

    def test_concrete_framework_version_only_records_dependency(self):
        request = self.request(frameworks=({"name": "fastapi", "version": "0.123.4"},))
        plan = self.engine.plan(request)
        pyproject = tomllib.loads(plan.files["pyproject.toml"].decode())
        self.assertEqual(pyproject["project"]["dependencies"], ["fastapi==0.123.4"])
        self.assertFalse(self.destination.exists())
        self.assertTrue(all(not t["executed"] for t in json.loads(plan.files[".stacknauta/agent-plan.json"])["tasks"]))


class RuntimeTests(Base):
    def setUp(self):
        super().setUp()
        self.calls = []
        self.installs = {}
        for plugin, version in VERSIONS.items():
            install = self.temp / "asdf-data/installs" / plugin / version
            (install / "bin").mkdir(parents=True)
            for name in EXECUTABLES[plugin]:
                binary = install / "bin" / name; binary.write_text("synthetic, never executed"); binary.chmod(0o755)
            self.installs[plugin] = install
        (self.home / ".tool-versions").write_text("".join(f"{p} {v}\n" for p, v in VERSIONS.items()))
        self.outputs = {"python": "Python 3.14.8", "node": "v24.21.0", "go": "go version go1.25.3 linux/amd64",
                        "java": 'openjdk version "21.0.9" 2025-10-21', "javac": "javac 21.0.9", "rustc": "rustc 1.90.0 (test)", "cargo": "cargo 1.90.0 (test)"}

    def runner(self, command, **kwargs):
        self.calls.append((command, kwargs))
        if command[1] == "where":
            output = str(self.installs[command[2]])
        elif command[1] == "which":
            plugin = next(p for p, names in EXECUTABLES.items() if command[2] in names)
            output = str(self.installs[plugin] / "bin" / command[2])
        else:
            output = self.outputs[Path(command[0]).name]
        return subprocess.CompletedProcess(command, 0, output, "")

    def resolver(self, **kwargs):
        return AsdfResolver(self.home, runner=self.runner, executable="/fake/asdf", **kwargs)

    def resolve(self, languages=("python",), **kwargs):
        return self.resolver().resolve(languages, executor=self.installs["python"] / "bin/python", **kwargs)

    def test_all_installed_runtimes_and_real_versions(self):
        values = self.resolve(("python", "typescript", "go", "java", "rust"))
        self.assertEqual(set(values), set(VERSIONS))
        self.assertEqual(values["java"]["detected"]["javac"], "21.0.9")

    def test_missing_global_configuration(self):
        (self.home / ".tool-versions").unlink()
        with self.assertRaisesRegex(BootstrapError, "global"):
            self.resolve()
        os.mkfifo(self.home / ".tool-versions")
        with self.assertRaisesRegex(BootstrapError, "não regular"):
            self.resolve()

    def test_missing_language_configuration_and_no_system_fallback(self):
        (self.home / ".tool-versions").write_text("python 3.14.8\n")
        with self.assertRaisesRegex(BootstrapError, "nodejs"):
            self.resolve(("typescript",))
        self.assertFalse(any(c[0][0].endswith("/node") for c in self.calls))

    def test_multiple_versions_system_paths_refs_and_duplicate_globals_rejected(self):
        for value in ("system", "3.14.8 3.13.0", "path:/usr/bin", "ref:master", "latest", ""):
            (self.home / ".tool-versions").write_text("python " + value + "\n")
            with self.subTest(value=value), self.assertRaises(BootstrapError):
                self.resolve()
        (self.home / ".tool-versions").write_text("python 3.14.8\npython 3.14.8\n")
        with self.assertRaises(BootstrapError):
            self.resolve()

    def test_not_installed_or_not_executable(self):
        binary = self.installs["python"] / "bin/python"
        binary.chmod(0o644)
        with self.assertRaisesRegex(BootstrapError, "executável"):
            self.resolve()
        binary.unlink()
        with self.assertRaises(BootstrapError):
            self.resolve()

    def test_binary_symlink_to_system_is_rejected_before_probe(self):
        binary = self.installs["python"] / "bin/python"; binary.unlink(); binary.symlink_to(sys.executable)
        with self.assertRaisesRegex(BootstrapError, "instalação"):
            self.resolve()
        self.assertFalse(any(Path(c[0][0]).name.startswith("python") for c in self.calls))

    def test_requested_and_detected_versions_must_match(self):
        with self.assertRaisesRegex(BootstrapError, "solicitada"):
            self.resolve(requested={"python": "3.13.0"})
        self.outputs["python"] = "Python 3.13.0"
        with self.assertRaisesRegex(BootstrapError, "real"):
            self.resolve()

    def test_wrong_executor_is_rejected(self):
        with self.assertRaisesRegex(BootstrapError, "Executor atual"):
            self.resolver().resolve(["python"], executor=sys.executable)

    def test_overrides_are_isolated_and_hook_environments_removed(self):
        env = {"PATH": "/synthetic", "ASDF_PYTHON_VERSION": "system", "ASDF_NODEJS_VERSION": "bad", "PYTHONPATH": "unsafe", "NODE_OPTIONS": "--require unsafe", "JAVA_TOOL_OPTIONS": "-javaagent:unsafe"}
        result = self.resolver(env=env).resolve(["typescript"], executor=self.installs["python"] / "bin/python")
        self.assertEqual(result["python"]["version"], "3.14.8")
        for command, kwargs in self.calls:
            self.assertEqual(kwargs["cwd"], self.home)
            for hook in ("PYTHONPATH", "NODE_OPTIONS", "JAVA_TOOL_OPTIONS"):
                self.assertNotIn(hook, kwargs["env"])
            self.assertNotIn("system", kwargs["env"].values())

    def test_subprocess_failure_is_clear_and_never_installs(self):
        resolver = AsdfResolver(self.home, executable="/fake/asdf", runner=lambda command, **kwargs: subprocess.CompletedProcess(command, 1, "", "not installed"))
        with self.assertRaisesRegex(BootstrapError, "Pré-requisito"):
            resolver.resolve(["python"])
        self.assertTrue(all("install" not in c[0] for c in self.calls))

    def test_managed_installation_symlink_cannot_alias_another_runtime(self):
        install = self.installs["python"]
        saved = install.with_name("saved")
        install.rename(saved)
        install.symlink_to(Path(sys.executable).resolve().parent.parent, target_is_directory=True)
        with self.assertRaisesRegex(BootstrapError, "física gerenciada"):
            self.resolve()

    def test_probe_disables_automatic_go_and_rust_toolchain_installation(self):
        self.resolve(("go", "rust"))
        for _, kwargs in self.calls:
            self.assertEqual(kwargs["env"]["GOTOOLCHAIN"], "local")
            self.assertEqual(kwargs["env"]["RUSTUP_AUTO_INSTALL"], "0")

    def test_jvm_opaque_vendor_label_and_compiler_consistency(self):
        result = self.resolve(("java",))
        self.assertEqual(result["java"]["version"], "temurin-21.0.9+10")
        self.outputs["javac"] = "javac 21.0.8"
        with self.assertRaisesRegex(BootstrapError, "divergem"):
            self.resolve(("java",))


class SelectionTests(Base):
    def selected(self, request):
        return set(self.engine.plan(request).selection["selected"])

    def test_every_approved_skill_has_an_explicit_policy(self):
        library = Library(ROOT)
        approved = {s for s, value in library.skills.items() if value["distribution_status"] == "approved"}
        self.assertEqual(approved, set(policies()))

    def test_fastapi_and_explicit_hexagonal_ddd(self):
        self.assertEqual(self.selected(self.request(frameworks=("fastapi",), features=("api",), architecture="hexagonal-ddd")), {"fastapi:fastapi", "remy:hexagonal-python"})
        self.assertEqual(self.selected(self.request(frameworks=("fastapi",), architecture="hexagonal")), {"fastapi:fastapi"})

    def test_no_architecture_or_language_is_selected_implicitly(self):
        plan = self.engine.plan(self.request())
        self.assertEqual(plan.selection["selected"], [])
        self.assertNotIn("src/domain/.gitkeep", plan.files)
        self.assertNotIn("package.json", plan.files)
        self.assertNotIn("remy:hexagonal-python", plan.selection["selected"])

    def test_typescript_next_ui_and_express_hexagonal(self):
        self.assertEqual(self.selected(self.request(("typescript",), ("nextjs",), ("ui",))), {"ui-ux-pro-max:ui-ux-pro-max"})
        self.assertEqual(self.selected(self.request(("typescript",), ("express",), ("api",), "hexagonal-ddd")), {"remy:hexagonal-typescript"})

    def test_frontend_hexagonal_does_not_imply_backend_api(self):
        selected = self.selected(self.request(("typescript",), ("nextjs",), ("ui",), "hexagonal-ddd"))
        self.assertNotIn("remy:hexagonal-typescript", selected)

    def test_go_and_rust_are_not_confused(self):
        request = self.request(("go",), features=("api",), architecture="hexagonal-ddd")
        request["stack"]["go_module"] = "example.org/team/example"
        self.assertEqual(self.selected(request), {"remy:hexagonal-go"})
        self.assertEqual(self.selected(self.request(("rust",))), set())

    def test_pending_excluded_unknown_and_incompatible_explicit_skills(self):
        for identifier in ("ui-ux-pro-max:design-system", "expo:expo-skill-eval", "expo:expo-migrate-module", "unknown:skill", "remy:hexagonal-go", "sentry:django-access-review"):
            with self.subTest(identifier=identifier), self.assertRaises(BootstrapError):
                self.engine.plan(self.request(skills=[identifier]))
        self.assertFalse(self.destination.exists())

    def test_empty_explicit_selection_disables_automatic_roots(self):
        self.assertEqual(self.selected(self.request(frameworks=("fastapi",), skills=[])), set())

    def test_incompatible_security_dependency_is_not_copied(self):
        plan = self.engine.plan(self.request(frameworks=("fastapi",), features=("security-review",)))
        self.assertNotIn("sentry:security-review", plan.selection["selected"])
        omitted = next(s for s in plan.selection["skipped"] if s["skill"] == "sentry:security-review")
        self.assertTrue(any(dependency in omitted["reason"] for dependency in ("django-access-review", "gha-security-review")))
        with self.assertRaises(BootstrapError):
            self.engine.plan(self.request(frameworks=("fastapi",), features=("security-review",), skills=["sentry:security-review"]))

    def test_compatible_security_dependency_closure(self):
        selected = self.selected(self.request(frameworks=("django",), features=("security-review", "github-actions")))
        self.assertEqual(selected, {"sentry:django-access-review", "sentry:gha-security-review", "sentry:security-review"})

    def test_expo_closure_cannot_add_undeclared_functionalities(self):
        plan = self.engine.plan(self.request(("typescript",), ("expo",), ("ui", "navigation")))
        self.assertFalse(any(s.startswith("expo:") for s in plan.selection["selected"]))
        self.assertTrue(plan.selection["skipped"])

    def test_full_declared_expo_feature_set_accepts_only_stable_family(self):
        features = set()
        for identifier, policy in policies().items():
            if identifier.startswith("expo:"):
                features |= policy["features_all"]
        selected = self.selected(self.request(("typescript",), ("expo",), sorted(features)))
        self.assertEqual(len([s for s in selected if s.startswith("expo:")]), 23)
        self.assertNotIn("expo:expo-migrate-module", selected)

    def test_kotlin_android_compose_dependencies_are_closed(self):
        selected = self.selected(self.request(("kotlin",), ("android", "jetpack-compose"), ("ui", "animation", "navigation", "testing", "performance", "gradle")))
        self.assertIn("chrisbanes:kotlin-api-design", selected)
        self.assertIn("chrisbanes:gradle-run", selected)
        self.assertNotIn("android:camerax", selected)
        self.assertNotIn("android:r8-analyzer", selected)

    def test_helper_runtime_missing_blocks_before_destination(self):
        engine = Bootstrap(ROOT, home=self.home, resolver=FakeResolver(missing=["nodejs"]))
        with self.assertRaisesRegex(BootstrapError, "nodejs"):
            engine.plan(self.request(features=("branding",)))
        self.assertFalse(self.destination.exists())


class FilesystemTests(Base):
    def test_dry_run_does_not_create_destination_or_default_root(self):
        request = self.request(); request.pop("destination")
        plan = self.engine.plan(request)
        self.assertTrue(plan.state["create"])
        self.assertFalse((self.home / "Projetos").exists())

    def test_default_root_created_only_on_apply(self):
        request = self.request(); request.pop("destination")
        result, plan = self.apply(request)
        self.assertEqual(result["status"], "prepared")
        self.assertTrue((self.home / "Projetos/example/.tool-versions").is_file())

    def test_physical_complete_copy_provenance_and_licenses(self):
        request = self.request(frameworks=("fastapi",), features=("api",), architecture="hexagonal-ddd")
        result, plan = self.apply(request)
        self.assertEqual(result["status"], "prepared")
        lock = json.loads((self.destination / ".stacknauta/skills-lock.json").read_text())
        self.assertEqual(len(lock["skills"]), 2)
        for relative, data in plan.files.items():
            path = self.destination / relative
            self.assertFalse(path.is_symlink())
            self.assertEqual(path.stat().st_nlink, 1)
            self.assertEqual(path.read_bytes(), data)
        for relative, origin in lock["files"].items():
            source = ROOT / "Skills" / origin["package"] / origin["package_path"]
            self.assertFalse(os.path.samefile(source, self.destination / relative))
            self.assertEqual(digest((self.destination / relative).read_bytes()), origin["sha256"])
            self.assertEqual(len(origin["commit"]), 40)
        self.assertTrue((self.destination / ".agents/skills/backend-fastapi/LICENSE").is_file())
        self.assertFalse((self.destination / "node_modules").exists())

    def test_idempotence_preserves_bytes_inode_mtime_and_unmanaged_files(self):
        request = self.request(frameworks=("fastapi",))
        _, plan = self.apply(request)
        (self.destination / "user-note.txt").write_text("preserve me")
        before = self.snapshot()
        result = self.engine.apply(request, plan.plan_id)
        self.assertEqual(result["status"], "unchanged")
        self.assertEqual(before, self.snapshot())

    def test_path_and_diagnostics_do_not_change_generated_identity(self):
        request = self.request()
        _, plan = self.apply(request)
        before = self.snapshot()
        self.engine.resolver.diagnostics = [{"PATH": "/different/location", "executable": "/another/asdf/python"}]
        with patch.dict(os.environ, {"PATH": "/changed"}):
            other = self.engine.plan(request)
            result = self.engine.apply(request, plan.plan_id)
        self.assertEqual(other.plan_id, plan.plan_id)
        self.assertEqual(result["status"], "unchanged")
        self.assertEqual(before, self.snapshot())

    def test_foreign_nonempty_destination_and_existing_changed_file_preserved(self):
        self.destination.mkdir(); p = self.destination / "README.md"; p.write_text("foreign")
        with self.assertRaises(BootstrapError):
            self.engine.plan(self.request())
        self.assertEqual(p.read_text(), "foreign")
        self.assertFalse((self.destination / ".stacknauta").exists())

    def test_modified_evolutive_file_is_preserved_on_reapplication(self):
        request = self.request(); _, plan = self.apply(request)
        (self.destination / "README.md").write_text("user changes")
        before = self.snapshot()
        self.assertEqual(self.engine.apply(request, plan.plan_id)["status"], "unchanged")
        self.assertEqual(before, self.snapshot())

    def test_wrong_preview_id_and_changed_runtime_have_no_writes(self):
        request = self.request(); plan = self.engine.plan(request)
        with self.assertRaisesRegex(BootstrapError, "plan_id"):
            self.engine.apply(request, "0" * 64)
        self.assertFalse(self.destination.exists())
        old = VERSIONS["python"]
        try:
            VERSIONS["python"] = "3.14.9"
            with self.assertRaisesRegex(BootstrapError, "plan_id"):
                self.engine.apply(request, plan.plan_id)
        finally:
            VERSIONS["python"] = old
        self.assertFalse(self.destination.exists())

    def test_failed_runtime_does_not_create_default_parent(self):
        engine = Bootstrap(ROOT, home=self.home, resolver=FakeResolver(missing=["python"]))
        request = self.request(); request.pop("destination")
        with self.assertRaises(BootstrapError):
            engine.plan(request)
        self.assertFalse((self.home / "Projetos").exists())

    def test_partial_failure_is_resumable_without_rewriting_completed_files(self):
        request = self.request(frameworks=("fastapi",)); plan = self.engine.plan(request)
        def fail(relative):
            if relative.endswith("/skills/fastapi/SKILL.md"):
                raise OSError("injected disk failure")
        with self.assertRaisesRegex(BootstrapError, "interrompida"):
            self.engine.apply(request, plan.plan_id, hook=fail)
        before = self.snapshot()
        self.assertIn(MANIFEST, before)
        result = self.engine.apply(request, plan.plan_id)
        self.assertEqual(result["status"], "prepared")
        for relative, value in before.items():
            self.assertEqual(self.snapshot()[relative], value)

    def test_failure_before_manifest_leaves_only_empty_owned_directories(self):
        request = self.request(); plan = self.engine.plan(request)
        def fail(relative):
            if relative == MANIFEST:
                raise OSError("first publication failure")
        with self.assertRaises(BootstrapError):
            self.engine.apply(request, plan.plan_id, hook=fail)
        self.assertEqual(list((self.destination / ".stacknauta").iterdir()), [])
        self.assertEqual(self.engine.apply(request, plan.plan_id)["status"], "prepared")

    def test_missing_explicit_parent_is_not_created_outside_authorized_target(self):
        request = self.request(destination=str(self.temp / "missing-parent/target"))
        with self.assertRaisesRegex(BootstrapError, "pai"):
            self.engine.plan(request)
        self.assertFalse((self.temp / "missing-parent").exists())

    def test_library_and_legacy_paths_are_protected(self):
        for destination in (ROOT / "new-project", ROOT.parent / "App-Web/new-project"):
            with self.subTest(destination=destination), self.assertRaisesRegex(BootstrapError, "protegida"):
                self.engine.plan(self.request(destination=str(destination)))

    def test_double_slash_cannot_bypass_protected_destination(self):
        destination = "//" + str(ROOT.parent / "App-Web/new-project").lstrip("/")
        with self.assertRaisesRegex(BootstrapError, "protegida"):
            self.engine.plan(self.request(destination=destination))

    def test_tilde_path_remains_under_configured_home(self):
        value = normalize(self.request(destination="~//new-project"), self.home)
        self.assertEqual(value["destination"], str(self.home / "new-project"))

    def test_symlink_parent_and_target_rejected(self):
        outside = self.temp / "outside"; outside.mkdir()
        alias = self.temp / "alias"; alias.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(BootstrapError):
            self.engine.plan(self.request(destination=str(alias / "child")))
        self.destination.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(BootstrapError):
            self.engine.plan(self.request())
        self.assertEqual(list(outside.iterdir()), [])

    def test_managed_leaf_symlink_and_hardlink_rejected(self):
        request = self.request(); _, plan = self.apply(request)
        outside = self.temp / "outside.txt"; outside.write_text("outside")
        leaf = self.destination / "README.md"; leaf.unlink(); leaf.symlink_to(outside)
        with self.assertRaises(BootstrapError):
            self.engine.apply(request, plan.plan_id)
        self.assertEqual(outside.read_text(), "outside")
        leaf.unlink(); os.link(outside, leaf)
        with self.assertRaises(BootstrapError):
            self.engine.plan(request)
        self.assertEqual(outside.read_text(), "outside")

    def test_fifo_is_rejected_without_blocking(self):
        request = self.request(); _, plan = self.apply(request)
        leaf = self.destination / "README.md"; leaf.unlink(); os.mkfifo(leaf)
        with self.assertRaises(BootstrapError):
            self.engine.apply(request, plan.plan_id)

    def test_concurrent_leaf_symlink_never_writes_outside(self):
        request = self.request(); plan = self.engine.plan(request)
        outside = self.temp / "outside.txt"; outside.write_text("outside")
        def race(relative):
            if relative == "README.md":
                (self.destination / relative).symlink_to(outside)
        with self.assertRaises(BootstrapError):
            self.engine.apply(request, plan.plan_id, hook=race)
        self.assertEqual(outside.read_text(), "outside")

    def test_concurrent_intermediate_directory_symlink_never_writes_outside(self):
        request = self.request(frameworks=("fastapi",)); plan = self.engine.plan(request)
        outside = self.temp / "outside"; outside.mkdir()
        def race(relative):
            if relative == ".agents/skills/backend-fastapi/LICENSE":
                folder = self.destination / ".agents/skills/backend-fastapi"
                folder.rename(self.destination / "moved-package")
                folder.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(BootstrapError):
            self.engine.apply(request, plan.plan_id, hook=race)
        self.assertEqual(list(outside.iterdir()), [])

    def test_portable_library_without_repos_or_original_home(self):
        library = self.minimal_library()
        self.assertFalse((library / "Skills/_repos").exists())
        engine = Bootstrap(library, home=self.home, resolver=FakeResolver())
        request = self.request(frameworks=("fastapi",), skills=["fastapi:fastapi"])
        plan = engine.plan(request)
        self.assertEqual(engine.apply(request, plan.plan_id)["status"], "prepared")

    def test_corrupt_resource_and_source_symlink_block_before_writes(self):
        library = self.minimal_library()
        resource = library / "Skills/Backend/fastapi/skills/fastapi/SKILL.md"
        resource.write_bytes(resource.read_bytes() + b"corrupted")
        engine = Bootstrap(library, home=self.home, resolver=FakeResolver())
        request = self.request(frameworks=("fastapi",), skills=["fastapi:fastapi"])
        with self.assertRaisesRegex(BootstrapError, "adulterado"):
            engine.plan(request)
        resource.unlink(); resource.symlink_to(ROOT / "Skills/Backend/fastapi/skills/fastapi/SKILL.md")
        with self.assertRaisesRegex(BootstrapError, "simbólico"):
            engine.plan(request)
        self.assertFalse(self.destination.exists())

    def test_brand_extra_helper_copied_without_fake_skill(self):
        request = self.request(features=("branding",))
        _, plan = self.apply(request)
        base = self.destination / ".agents/skills/frontend-ui-ux-pro-max"
        self.assertTrue((base / "skills/design-system/scripts/generate-tokens.cjs").is_file())
        self.assertFalse((base / "skills/design-system/SKILL.md").exists())
        self.assertEqual(plan.runtimes["nodejs"]["roles"], ["skill-helper"])


class RealCliTests(Base):
    def test_launcher_real_asdf_plan_apply_and_noop_in_temp_with_local_overrides(self):
        # Somente runtimes reais já instalados; sem geradores ou scripts de skills.
        config = self.temp / "request.json"
        request = self.request(("typescript",), ("nextjs",), ("ui",))
        config.write_text(json.dumps(request))
        (self.temp / ".tool-versions").write_text("python system\nnodejs system\n")
        environment = dict(os.environ, ASDF_PYTHON_VERSION="system", ASDF_NODEJS_VERSION="system", PYTHONPATH=str(self.temp / "malicious"))
        launcher = CORE / "project-bootstrap"
        def run(*args):
            return subprocess.run([str(launcher), *args, "--config", str(config)], cwd=self.temp, env=environment,
                                  capture_output=True, text=True, timeout=30)
        preview = run("plan")
        self.assertEqual(preview.returncode, 0, preview.stderr)
        plan = json.loads(preview.stdout)
        self.assertFalse(self.destination.exists())
        applied = run("apply", "--plan-id", plan["plan_id"])
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertEqual(json.loads(applied.stdout)["status"], "prepared")
        again = run("apply", "--plan-id", plan["plan_id"])
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertEqual(json.loads(again.stdout)["status"], "unchanged")
        self.assertFalse((self.destination / "node_modules").exists())
        self.assertFalse((self.destination / ".git").exists())

    def test_real_python_fastapi_cli_copies_approved_resources(self):
        config = self.temp / "api.json"
        config.write_text(json.dumps(self.request(frameworks=("fastapi",), features=("api",), architecture="hexagonal-ddd")))
        launcher = CORE / "project-bootstrap"
        preview = subprocess.run([str(launcher), "plan", "--config", str(config)], cwd=self.temp, capture_output=True, text=True, timeout=30)
        self.assertEqual(preview.returncode, 0, preview.stderr)
        plan = json.loads(preview.stdout)
        self.assertEqual(set(plan["skills"]["selected"]), {"fastapi:fastapi", "remy:hexagonal-python"})
        applied = subprocess.run([str(launcher), "apply", "--config", str(config), "--plan-id", plan["plan_id"]], cwd=self.temp, capture_output=True, text=True, timeout=30)
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertTrue((self.destination / ".agents/skills/backend-fastapi/skills/fastapi/references/dependencies.md").is_file())
        self.assertFalse((self.destination / ".venv").exists())

    def test_launcher_missing_global_stops_before_python_and_writes(self):
        environment = dict(os.environ, HOME=str(self.home))
        config = self.temp / "request.json"; config.write_text(json.dumps(self.request()))
        result = subprocess.run([str(CORE / "project-bootstrap"), "plan", "--config", str(config)], env=environment,
                                capture_output=True, text=True, timeout=15)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("global", result.stderr)
        self.assertFalse(self.destination.exists())
        os.mkfifo(self.home / ".tool-versions")
        invalid = subprocess.run([str(CORE / "project-bootstrap"), "plan", "--config", str(config)], env=environment,
                                 capture_output=True, text=True, timeout=5)
        self.assertNotEqual(invalid.returncode, 0)
        self.assertIn("não regular", invalid.stderr)

    def test_apply_requires_reviewed_plan_id(self):
        config = self.temp / "request.json"; config.write_text(json.dumps(self.request()))
        result = subprocess.run([str(CORE / "project-bootstrap"), "apply", "--config", str(config)],
                                capture_output=True, text=True, timeout=15)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("plan-id", result.stderr)
        self.assertFalse(self.destination.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
