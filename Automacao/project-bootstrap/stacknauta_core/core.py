"""Plano determinístico e aplicação do esqueleto; não executa geradores/serviços."""
import dataclasses
import json
from pathlib import Path

from . import BootstrapError, VERSION
from .config import FRAMEWORKS, normalize
from .filesystem import MANIFEST, Target
from .library import Library, digest
from .runtimes import AsdfResolver
from . import lifecycle


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def agent_tasks(config):
    tasks = []
    for framework in config["stack"]["frameworks"]:
        tasks.append({"technology": framework["name"], "version": framework["version"],
                      "status": "requires_explicit_version" if framework["version"] is None else "requires_agent_plan_and_authorization",
                      "operations": ["review official prerequisites for declared version", "propose generator or manual configuration", "review commands, outputs and network/install effects before execution"],
                      "executed": False})
    if {"java", "kotlin"} & set(config["stack"]["languages"]):
        tasks.append({"technology": "jvm-build", "status": "requires_explicit_build_tool_and_plugin_versions", "executed": False})
    if "typescript" in config["stack"]["languages"]:
        tasks.append({"technology": "typescript-compiler", "status": "requires_explicit_compiler_version_before_installation", "executed": False})
    if "rust" in config["stack"]["languages"]:
        tasks.append({"technology": "rust-edition", "status": "requires_explicit_edition_before_build", "executed": False})
    return {"schema_version": 1, "agent_independent": True, "application_development_started": False,
            "authorization": "No generator, dependency installation or service startup is authorized by this file.",
            "tasks": tasks, "requirements": config["requirements"],
            "architecture": config["stack"]["architecture"]}


def skeleton(config, runtimes, exported):
    name = config["name"]
    languages = config["stack"]["languages"]
    architecture = config["stack"]["architecture"]
    files = {
        ".stacknauta/config.json": encoded(config), ".stacknauta/agent-plan.json": encoded(agent_tasks(config)),
        ".tool-versions": ("".join(f"{p} {r['version']}\n" for p, r in sorted(runtimes.items()))).encode(),
        "docs/REQUIREMENTS.json": encoded(config["requirements"]), "tests/.gitkeep": b"",
        "README.md": (f"# {name}\n\nEsqueleto preparado pelo StackNauta ({VERSION}). Desenvolvimento da aplicação ainda não iniciado.\n\n"
                      "A stack foi declarada pelo usuário; versões de runtimes vêm exclusivamente do asdf global.\n"
                      "Consulte `.stacknauta/config.json`, `docs/REQUIREMENTS.json` e `.stacknauta/agent-plan.json`.\n"
                      "Geradores, instalação de dependências e serviços exigem plano explícito e pré-requisitos verificados pelo agente.\n"
                      "Nenhum código de negócio, build de aplicação ou integração com agentes foi executado.\n\n"
                      f"Arquitetura declarada: {architecture or 'não informada; nenhuma escolhida'}.\n"
                      "A versão inicial 0.0.0 nos metadados é apenas um marcador de esqueleto.\n").encode(),
        "AGENTS.md": b"# Initial development context\n\nRead .stacknauta/config.json, docs/REQUIREMENTS.json and .stacknauta/agent-plan.json before development.\nDo not infer a language, framework or architecture. Missing choices must be resolved with the user.\nUse installed global asdf runtimes; do not install runtimes or use system fallbacks.\nSkills and provenance are indexed in .agents/skills/README.md and .stacknauta/skills-lock.json.\nAgent-specific integrations and automatic generator execution are not provided by this core.\n",
    }
    ignores = [".env", ".env.*", "!.env.example"]
    if "python" in languages:
        ignores += ["__pycache__/", "*.pyc", ".venv/"]
    if {"javascript", "typescript"} & set(languages):
        ignores += ["node_modules/", "dist/", ".next/"]
    if "rust" in languages:
        ignores += ["target/"]
    files[".gitignore"] = ("\n".join(ignores) + "\n").encode()
    layers = ("domain", "application", "adapters", "bootstrap") if architecture in {"hexagonal", "hexagonal-ddd"} else ()
    if layers:
        for layer in layers:
            files[f"src/{layer}/.gitkeep"] = b""
    else:
        files["src/.gitkeep"] = b""
    frameworks = config["stack"]["frameworks"]
    if "python" in languages:
        dependencies = [f['name'] + "==" + f['version'] for f in frameworks if f['version'] and FRAMEWORKS[f['name']] == {"python"}]
        text = f'[project]\nname = {json.dumps(name)}\nversion = "0.0.0"\nrequires-python = {json.dumps("=="+runtimes["python"]["detected"]["python"])}\ndependencies = {json.dumps(dependencies)}\n'
        files["pyproject.toml"] = text.encode()
    if {"javascript", "typescript"} & set(languages):
        npm = {"nextjs": "next", "nestjs": "@nestjs/core", "react-native": "react-native", "tailwind": "tailwindcss"}
        dependencies = {npm.get(f['name'], f['name']): f['version'] for f in frameworks if f['version'] and FRAMEWORKS[f['name']] & {"javascript", "typescript"} and f['name'] != "shadcn"}
        files["package.json"] = encoded({"name": name, "version": "0.0.0", "private": True, "engines": {"node": runtimes["nodejs"]["detected"]["node"]}, "dependencies": dependencies})
    if "typescript" in languages:
        files["tsconfig.json"] = encoded({"compilerOptions": {"noEmit": True}, "include": ["src"]})
    if "go" in languages:
        go_language_version = ".".join(runtimes['golang']['detected']['go'].split('.')[:2])
        files["go.mod"] = (f"module {config['stack']['go_module']}\n\ngo {go_language_version}\n").encode()
    if "rust" in languages:
        files["Cargo.toml"] = (f'[package]\nname = {json.dumps(name)}\nversion = "0.0.0"\npublish = false\n\n[lib]\npath = "src/lib.rs"\n').encode()
        files["src/lib.rs"] = b"//! Initial skeleton. No business implementation.\n"
    if {"java", "kotlin"} & set(languages):
        for language in sorted({"java", "kotlin"} & set(languages)):
            files[f"src/{language}/.gitkeep"] = b""
        files["BUILD-PLAN.md"] = b"# JVM build plan\n\nChoose the build tool, DSL, framework/plugin versions and SDK prerequisites explicitly with the user.\nNo Gradle/Maven wrapper, plugin installation or build was executed. See .stacknauta/agent-plan.json.\n"
    lines = ["# Skills selected by StackNauta", "", "Physical, namespaced copies preserving the approved package layout.",
             "Agent discovery must be verified during integration; no agent-specific adapter is installed.", ""]
    for skill in exported:
        lines.append(f"- [{skill['id']}]({skill['path'].removeprefix('.agents/skills/')}) — `{skill['commit']}`")
    if not exported:
        lines.append("No compatible skill selected for these explicit requirements.")
    files[".agents/skills/README.md"] = ("\n".join(lines) + "\n").encode()
    return files


@dataclasses.dataclass
class Plan:
    config: dict
    runtimes: dict
    selection: dict
    files: dict
    manifest: bytes
    plan_id: str
    target: Target
    diagnostics: list
    state: dict
    completion: tuple | None = None

    def expected_files(self):
        return {MANIFEST: self.manifest, **self.files, **(dict([self.completion]) if self.completion else {})}

    def report(self):
        return {"schema_version": 1, "core_version": VERSION, "mode": "dry-run", "plan_id": self.plan_id,
                "destination": self.config["destination"], "config": self.config, "runtimes": self.runtimes,
                "runtime_resolution": self.diagnostics, "skills": self.selection,
                "files": [{"path": name, "sha256": digest(data), "size": len(data),
                           "classification": lifecycle.classification(name), "action": lifecycle.action(name, self.state)}
                          for name, data in sorted(self.expected_files().items())],
                "lifecycle": lifecycle.report(self.state),
                "agent_plan": json.loads(self.files[".stacknauta/agent-plan.json"]),
                "production_ready": False, "agent_integration_tested": False}


class Bootstrap:
    def __init__(self, library_root, *, home=None, resolver=None, protected=()):
        self.library_root = Path(library_root).resolve()
        self.home = Path(home) if home is not None else Path.home()
        self.resolver = resolver or AsdfResolver(self.home)
        self.protected = (self.library_root, self.library_root.parent / "App-Web", *protected)

    def plan(self, raw):
        config = normalize(raw, self.home)
        target = Target(config["destination"], self.home / "Projetos", self.protected)
        target.boundaries()
        library = Library(self.library_root)
        selection = library.select(config)
        runtimes = self.resolver.resolve(config["stack"]["languages"], config["runtime_versions"], extra_plugins=selection["extra_runtimes"])
        skill_files, origins, exported = library.export(selection)
        files = skeleton(config, runtimes, exported)
        if set(files) & set(skill_files):
            raise BootstrapError("Colisão entre esqueleto e recursos de skills")
        files.update(skill_files)
        files[".stacknauta/skills-lock.json"] = encoded({"schema_version": 1, "catalog_sha256": digest(library.catalog_bytes),
            "sources_lock_sha256": digest(library.lock_bytes), "skills": exported, "files": origins})
        schema = target.manifest_schema() or 2
        identity = {"schema_version": schema, "core_version": VERSION, "config": config, "runtimes": runtimes,
                    "skills": selection["selected"],
                    "files": {name: {"sha256": digest(data), "size": len(data)} for name, data in sorted(files.items())}}
        if schema == 2:
            identity["lifecycle"] = {"policy_version": lifecycle.VERSION, "completion": lifecycle.COMPLETION,
                                     "files": {name: lifecycle.classification(name) for name in sorted(files)}}
        plan_id = digest(encoded(identity))
        manifest = encoded({**identity, "plan_id": plan_id})
        completion = (lifecycle.COMPLETION, encoded({"schema_version": 1, "policy_version": lifecycle.VERSION,
                      "core_plan_id": plan_id, "manifest_sha256": digest(manifest)})) if schema == 2 else None
        state = target.inspect(manifest, files, completion=completion)
        return Plan(config, runtimes, selection, files, manifest, plan_id, target,
                    list(getattr(self.resolver, "diagnostics", [])), state, completion)

    def apply(self, raw, expected_plan_id, *, hook=None):
        plan = self.plan(raw)
        if expected_plan_id != plan.plan_id:
            raise BootstrapError("plan_id não corresponde ao dry-run atual; gere e revise o plano novamente")
        result = plan.target.apply(plan.manifest, plan.files, hook, completion=plan.completion)
        plan.state = plan.target.inspect(plan.manifest, plan.files, completion=plan.completion)
        return {**result, "plan_id": plan.plan_id, "destination": plan.config["destination"],
                "skills": plan.selection["selected"], "lifecycle": lifecycle.report(plan.state),
                "production_ready": False, "agent_integration_tested": False}
