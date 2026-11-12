"""Resolve versões GLOBAIS explicitamente, isolando overrides locais/ambiente."""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from . import BootstrapError

LANGUAGE_PLUGINS = {"python": "python", "javascript": "nodejs", "typescript": "nodejs",
                    "go": "golang", "java": "java", "kotlin": "java", "rust": "rust"}
EXECUTABLES = {"python": ("python",), "nodejs": ("node",), "golang": ("go",),
               "java": ("java", "javac"), "rust": ("rustc", "cargo")}
HOOK_ENV = {"PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP", "NODE_OPTIONS", "NODE_PATH",
            "JAVA_TOOL_OPTIONS", "JDK_JAVA_OPTIONS", "_JAVA_OPTIONS", "RUSTC_WRAPPER",
            "RUSTC_WORKSPACE_WRAPPER", "LD_PRELOAD", "LD_LIBRARY_PATH", "LD_AUDIT", "GOROOT", "GOTOOLDIR"}


class AsdfResolver:
    def __init__(self, home, *, runner=subprocess.run, env=None, executable=None):
        self.home = Path(home)
        self.runner = runner
        self.env = dict(os.environ if env is None else env)
        self.asdf = executable or shutil.which("asdf", path=self.env.get("PATH", ""))
        self.diagnostics = []

    def run(self, command, env):
        try:
            result = self.runner(command, cwd=self.home, env=env, capture_output=True, text=True, timeout=15, check=False)
        except (OSError, subprocess.SubprocessError) as exc:
            raise BootstrapError(f"Falha consultando runtime: {command[0]} ({exc})") from exc
        if result.returncode:
            raise BootstrapError(f"Pré-requisito falhou: {' '.join(command[:3])}; runtime ausente, inválido ou não executável")
        return (result.stdout + "\n" + result.stderr).strip()

    def global_versions(self):
        if not (self.home / ".tool-versions").is_file():
            raise BootstrapError("Configuração global asdf ~/.tool-versions ausente ou não regular")
        try:
            lines = (self.home / ".tool-versions").read_text().splitlines()
        except OSError as exc:
            raise BootstrapError("Configuração global asdf ~/.tool-versions ausente ou ilegível") from exc
        versions = {}
        for line in lines:
            fields = line.split("#", 1)[0].split()
            if not fields:
                continue
            if fields[0] in versions:
                raise BootstrapError(f"Runtime global duplicado: {fields[0]}")
            versions[fields[0]] = fields[1:]
        return versions

    def resolve(self, languages, requested=None, *, executor=None, extra_plugins=()):
        if not self.asdf:
            raise BootstrapError("asdf não está disponível; não usar runtimes do sistema")
        versions = self.global_versions()
        application = {LANGUAGE_PLUGINS[language] for language in languages}
        required = {"python"} | application | set(extra_plugins)
        requested = requested or {}
        if set(requested) - required:
            raise BootstrapError("runtime_versions contém runtime não exigido pela stack/executor")
        result = {}
        for plugin in sorted(required):
            choices = versions.get(plugin, [])
            if len(choices) != 1 or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+\-]*", choices[0]) or choices[0] in {"system", "latest"}:
                raise BootstrapError(f"asdf global: {plugin} precisa de uma única versão instalada explícita; fallback/system/path/ref não aceitos")
            version = choices[0]
            if plugin in requested and requested[plugin] != version:
                raise BootstrapError(f"{plugin}: versão solicitada {requested[plugin]} difere da global {version}")
            environment = {k: v for k, v in self.env.items() if k not in HOOK_ENV and not (k.startswith("ASDF_") and k.endswith("_VERSION"))}
            environment.update({"HOME": str(self.home), "LC_ALL": "C", "LANG": "C", f"ASDF_{plugin.upper()}_VERSION": version})
            environment.update({"GOTOOLCHAIN": "local", "RUSTUP_AUTO_INSTALL": "0"})
            if plugin == "rust":
                environment["RUSTUP_TOOLCHAIN"] = version
            installation_text = self.run([self.asdf, "where", plugin, version], environment)
            if "\n" in installation_text or not Path(installation_text).is_absolute():
                raise BootstrapError(f"asdf retornou instalação inválida: {plugin}")
            installation_path = Path(installation_text)
            installation = installation_path.resolve()
            if installation_path.parts[-3:] != ("installs", plugin, version) or not installation.is_relative_to(installation_path.parent.resolve()):
                raise BootstrapError(f"Instalação {plugin} não é uma versão física gerenciada pelo asdf")
            if not installation.is_dir():
                raise BootstrapError(f"Runtime global não instalado: {plugin} {version}")
            detected = {}
            for command in EXECUTABLES[plugin]:
                path_text = self.run([self.asdf, "which", command], environment)
                if "\n" in path_text or not Path(path_text).is_absolute():
                    raise BootstrapError(f"asdf which inválido: {command}")
                path = Path(path_text).resolve()
                if not path.is_relative_to(installation) or not path.is_file() or not os.access(path, os.X_OK):
                    raise BootstrapError(f"{command} não pertence à instalação global asdf ou não é executável")
                output = self.run([str(path), "-version" if command in {"java", "javac"} else "version" if command == "go" else "--version"], environment)
                patterns = {"python": r"Python\s+(\S+)", "node": r"v(\d[^\s]*)", "go": r"go version go(\S+)",
                            "java": r'(?:java|openjdk) version "([^\"]+)"', "javac": r"javac\s+(\S+)",
                            "rustc": r"rustc\s+(\S+)", "cargo": r"cargo\s+(\S+)"}
                match = re.search(patterns[command], output)
                if not match:
                    raise BootstrapError(f"Não foi possível confirmar a versão real de {command}")
                observed = match[1]
                # Labels de fornecedores JVM (e PyPy/nightly) são opacos; o vínculo
                # à instalação é verificado pelo caminho, e a versão real é registrada.
                configured_numeric = re.match(r"\d+(?:[._]\d+)*", version) if plugin != "java" else None
                if configured_numeric and not (observed.replace("_", ".") == configured_numeric[0].replace("_", ".") or observed.replace("_", ".").startswith(configured_numeric[0].replace("_", ".") + ".") or observed.startswith(configured_numeric[0] + "+")):
                    raise BootstrapError(f"Versão real de {command} ({observed}) não corresponde à global ({version})")
                if command == "python":
                    if tuple(int(v) for v in observed.split(".")[:2]) < (3, 11):
                        raise BootstrapError("Executor exige Python global >=3.11")
                    expected_executor = Path(executor or sys.executable).resolve()
                    if expected_executor != path:
                        raise BootstrapError("Executor atual não é o Python global asdf; use o launcher project-bootstrap")
                detected[command] = observed
                self.diagnostics.append({"plugin": plugin, "command": command, "executable": str(path)})
            if plugin == "java" and detected["java"] != detected["javac"]:
                raise BootstrapError("java e javac divergem dentro da instalação global")
            roles = (["executor"] if plugin == "python" else []) + (["application"] if plugin in application else [])
            result[plugin] = {"version": version, "detected": detected, "roles": roles or ["skill-helper"]}
        self.diagnostics.append({"resolution": "explicit-global", "local_and_environment_version_overrides": "ignored_explicitly",
                                 "global_file": str(self.home / ".tool-versions")})
        return result
