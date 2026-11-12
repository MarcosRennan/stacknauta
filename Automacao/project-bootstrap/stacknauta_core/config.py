"""Entrada declarativa: nenhum framework, linguagem ou arquitetura inferidos."""
import json
import os
import re
import stat
from pathlib import Path

from . import BootstrapError

LANGUAGES = {"python", "javascript", "typescript", "go", "java", "kotlin", "rust"}
FRAMEWORKS = {
    "fastapi": {"python"}, "flask": {"python"}, "django": {"python"},
    "react": {"javascript", "typescript"}, "nextjs": {"javascript", "typescript"},
    "vue": {"javascript", "typescript"}, "nuxt": {"javascript", "typescript"},
    "svelte": {"javascript", "typescript"}, "astro": {"javascript", "typescript"},
    "express": {"javascript", "typescript"}, "nestjs": {"typescript"},
    "fastify": {"javascript", "typescript"}, "expo": {"javascript", "typescript"},
    "react-native": {"javascript", "typescript"}, "android": {"java", "kotlin"},
    "tailwind": {"javascript", "typescript"}, "shadcn": {"javascript", "typescript"},
    "jetpack-compose": {"kotlin"}, "gin": {"go"}, "chi": {"go"},
    "echo": {"go"}, "fiber": {"go"}, "axum": {"rust"}, "actix-web": {"rust"},
}
FEATURES = {
    "api", "ui", "design-tokens", "branding", "banners", "networking", "animation",
    "navigation", "testing", "performance", "accessibility", "security-review",
    "security-model", "secret-serialization", "permissions", "intents", "github-actions",
    "git-workflow", "code-review", "refactoring", "documentation", "typing", "prompts",
    "deployment", "ota", "observability", "native-modules", "brownfield", "app-clip",
    "web-migration", "sdk-upgrade", "examples", "simulator", "dev-client", "release",
    "gradle", "ci", "benchmark", "camera", "cars", "appfunctions", "on-device-ai", "identity",
    "adaptive-layout", "ink", "xml-migration", "casting", "anr", "play-engage",
    "billing", "play-policy", "profiling", "edge-to-edge", "widgets", "tv", "wear", "xr",
}
ARCHITECTURES = {None, "flat", "hexagonal", "hexagonal-ddd"}
VERSION = re.compile(r"[0-9][A-Za-z0-9._+\-]*\Z")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise BootstrapError(f"Chave JSON duplicada: {key}")
        result[key] = value
    return result


def load(path):
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
        with os.fdopen(fd, "rb") as source:
            if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
                raise BootstrapError("Configuração precisa ser um arquivo regular físico")
            data = source.read(1_000_001)
        if len(data) > 1_000_000:
            raise BootstrapError("Configuração excede 1 MB")
        return json.loads(data, object_pairs_hook=unique_object)
    except (OSError, ValueError, UnicodeError) as exc:
        raise BootstrapError(f"Configuração JSON inválida: {exc}") from exc


def keys(value, allowed, label):
    if not isinstance(value, dict):
        raise BootstrapError(f"{label} deve ser um objeto JSON")
    extra = set(value) - allowed
    if extra:
        raise BootstrapError(f"Campos desconhecidos em {label}: {', '.join(sorted(extra))}")


def strings(value, label, allowed=None):
    if not isinstance(value, list) or any(not isinstance(v, str) or not v for v in value):
        raise BootstrapError(f"{label} deve ser uma lista de strings não vazias")
    if len(value) != len(set(value)):
        raise BootstrapError(f"{label} contém entradas duplicadas")
    if allowed is not None and set(value) - allowed:
        raise BootstrapError(f"{label} não suportado: {', '.join(sorted(set(value) - allowed))}")
    return sorted(value)


def normalize(raw, home):
    keys(raw, {"schema_version", "name", "destination", "stack", "requirements", "skills", "runtime_versions"}, "configuração")
    if type(raw.get("schema_version", 1)) is not int or raw.get("schema_version", 1) != 1:
        raise BootstrapError("schema_version deve ser 1")
    name = raw.get("name")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", name) or len(name) > 64:
        raise BootstrapError("name deve ser um slug minúsculo de até 64 caracteres, sem barras")
    stack = raw.get("stack")
    keys(stack, {"languages", "frameworks", "architecture", "go_module"}, "stack")
    languages = strings(stack.get("languages"), "stack.languages", LANGUAGES)
    if not languages:
        raise BootstrapError("Informe ao menos uma linguagem; nenhuma será escolhida automaticamente")
    frameworks = stack.get("frameworks", [])
    if not isinstance(frameworks, list):
        raise BootstrapError("stack.frameworks deve ser uma lista")
    normalized = []
    for item in frameworks:
        item = {"name": item} if isinstance(item, str) else item
        keys(item, {"name", "version"}, "framework")
        framework = item.get("name")
        if not isinstance(framework, str) or framework not in FRAMEWORKS:
            raise BootstrapError(f"Framework não suportado: {framework}")
        if not FRAMEWORKS[framework].intersection(languages):
            raise BootstrapError(f"{framework} exige linguagem explicitamente declarada: {', '.join(sorted(FRAMEWORKS[framework]))}")
        version = item.get("version")
        if version is not None and (not isinstance(version, str) or not VERSION.fullmatch(version)):
            raise BootstrapError(f"Versão de {framework} deve ser concreta; sem latest, intervalos ou comandos")
        normalized.append({"name": framework, "version": version})
    if len({f["name"] for f in normalized}) != len(normalized):
        raise BootstrapError("Frameworks duplicados")
    architecture = stack.get("architecture")
    if not isinstance(architecture, (str, type(None))) or architecture not in ARCHITECTURES:
        raise BootstrapError("Arquitetura suportada: flat, hexagonal ou hexagonal-ddd; omitir não escolhe uma")
    go_module = stack.get("go_module")
    if "go" in languages:
        if not isinstance(go_module, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._\-/]*", go_module) or any(p in ("", ".", "..") for p in go_module.split("/")):
            raise BootstrapError("Go exige stack.go_module explícito e válido; não se inventa uma origem de módulo")
    elif go_module is not None:
        raise BootstrapError("go_module requer a linguagem go")
    requirements = raw.get("requirements", {})
    keys(requirements, {"features", "description", "constraints"}, "requirements")
    features = strings(requirements.get("features", []), "requirements.features", FEATURES)
    description = requirements.get("description", "")
    constraints = strings(requirements.get("constraints", []), "requirements.constraints")
    if not isinstance(description, str) or len(description) > 100_000 or "\x00" in description:
        raise BootstrapError("requirements.description inválido")
    if any(len(s) > 10_000 or "\x00" in s for s in constraints):
        raise BootstrapError("Restrição inválida")
    skills = strings(raw["skills"], "skills") if "skills" in raw else None
    versions = raw.get("runtime_versions", {})
    keys(versions, {"python", "nodejs", "golang", "java", "rust"}, "runtime_versions")
    for plugin, version in versions.items():
        if not isinstance(version, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+\-]*", version) or version in {"system", "latest"}:
            raise BootstrapError(f"Versão de runtime inválida: {plugin}")
    default_parent = home / "Projetos"
    explicit = raw.get("destination")
    if explicit is None:
        target = default_parent / name
    else:
        if not isinstance(explicit, str) or not explicit or any(ord(c) < 32 for c in explicit):
            raise BootstrapError("destination inválido")
        if explicit.startswith("~/"):
            explicit = str(home / explicit[2:].lstrip("/"))
        target = Path(explicit)
        if not target.is_absolute() or ".." in target.parts:
            raise BootstrapError("destination deve ser absoluto, sem travessia '..'")
    # Linux aceita // como /; canonicalizar antes da comparação de áreas protegidas.
    target = Path("/" + target.as_posix().lstrip("/"))
    if target == Path("/") or target == home or target == default_parent:
        raise BootstrapError("O destino deve ser uma pasta própria do novo projeto")
    if any(p in {".git", ".agents", ".stacknauta", "_repos"} for p in target.parts):
        raise BootstrapError("Destino atravessa diretório reservado")
    return {
        "schema_version": 1, "name": name, "destination": str(target),
        "stack": {"languages": languages, "frameworks": sorted(normalized, key=lambda f: f["name"]),
                  "architecture": architecture, "go_module": go_module},
        "requirements": {"features": features, "description": description, "constraints": constraints},
        "skills": skills, "runtime_versions": dict(sorted(versions.items())),
    }
