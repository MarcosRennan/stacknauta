"""Consome pacotes versionados; não consulta cache, executa skills ou altera biblioteca."""
import hashlib
import json
import shutil
import sys
from pathlib import Path, PurePosixPath

from . import BootstrapError
from .compatibility import mismatch, catalog_policies
from .filesystem import directory, read


def digest(data):
    return hashlib.sha256(data).hexdigest()


def regular(root, relative):
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or "\\" in relative or not relative:
        raise BootstrapError(f"Caminho inválido na biblioteca: {relative}")
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise BootstrapError(f"Link simbólico na biblioteca: {relative}")
    try:
        with directory(root) as root_fd:
            data = read(root_fd, relative, 64_000_000)
        if data is None:
            raise BootstrapError(f"Recurso indisponível na biblioteca: {relative}")
        return data
    except OSError as exc:
        raise BootstrapError(f"Recurso indisponível na biblioteca: {relative}") from exc


class Library:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.catalog_bytes = regular(self.root, "Skills/catalogo.json")
        try:
            self.catalog = json.loads(self.catalog_bytes)
            self.lock_bytes = regular(self.root, "Skills/fontes.lock.json")
            lock = json.loads(self.lock_bytes)
            self.skills = {s["id"]: s for s in self.catalog["skills"]}
            if len(self.skills) != len(self.catalog["skills"]):
                raise BootstrapError("IDs duplicados no catálogo")
            expected = {s["id"]: s["commit"] for s in lock["sources"]}
            if {s["id"]: s["commit"] for s in self.catalog["sources"]} != expected:
                raise BootstrapError("Revisões do catálogo divergem do lock")
            self.descriptors = {p["id"]: p for p in self.catalog["distribution_packages"]}
        except (ValueError, KeyError, TypeError) as exc:
            raise BootstrapError("Catálogo/lock inválidos") from exc
        self.rules = catalog_policies(self.catalog["skills"])
        self.packages = {}
        sys.path.insert(0, str(self.root / "Skills/manutencao"))
        # Reutiliza o contrato de cópia da Etapa 1.5; função pura, sem acesso ao cache.
        try:
            from biblioteca import selected_files
        except ImportError as exc:
            raise BootstrapError("Ferramenta de plano de cópia da biblioteca indisponível") from exc
        self.selected_files = selected_files

    def closure(self, identifier, config):
        found, queue = set(), [identifier]
        while queue:
            current = queue.pop()
            if current in found:
                continue
            skill = self.skills.get(current)
            if not skill or skill.get("distribution_status") != "approved" or not skill.get("distribution"):
                raise BootstrapError(f"{current}: skill inexistente, pendente ou excluída")
            if self.rules.get(current, {}).get("selection_mode") == "explicit" and current not in (config["skills"] or ()):
                raise BootstrapError(f"{current}: seleção explícita obrigatória, inclusive como dependência")
            reason = mismatch(self.rules.get(current), config)
            if reason:
                raise BootstrapError(f"{current}: {reason}")
            for tool in self.rules[current]["tools"]:
                if not shutil.which(tool):
                    raise BootstrapError(f"{current}: ferramenta obrigatória indisponível: {tool}")
            found.add(current)
            queue.extend(skill["distribution"]["requires_skills"])
        return sorted(found)

    def select(self, config):
        selected, roots, skipped = set(), [], []
        explicit = config["skills"] is not None
        if not explicit:
            for identifier, skill in sorted(self.skills.items()):
                if skill["distribution_status"] == "approved" and self.rules.get(identifier, {}).get("selection_mode") == "explicit":
                    skipped.append({"skill": identifier, "reason": "Seleção explícita obrigatória"})
                    continue
                if skill["distribution_status"] == "approved" and "compatibility" in skill:
                    reason = mismatch(self.rules.get(identifier), config)
                    if reason: skipped.append({"skill": identifier, "reason": reason})
        candidates = config["skills"] if explicit else sorted(
            identifier for identifier, skill in self.skills.items()
            if skill["distribution_status"] == "approved"
            and self.rules.get(identifier, {}).get("selection_mode") != "explicit"
            and not mismatch(self.rules.get(identifier), config))
        for identifier in candidates:
            try:
                closure = self.closure(identifier, config)
            except BootstrapError as exc:
                if explicit:
                    raise
                skipped.append({"skill": identifier, "reason": str(exc)})
                continue
            selected.update(closure)
            roots.append(identifier)
        extra_runtimes = set()
        for identifier in selected:
            extra_runtimes.update(self.rules[identifier]["runtimes"])
        return {"roots": sorted(roots), "selected": sorted(selected), "skipped": skipped,
                "extra_runtimes": sorted(extra_runtimes)}

    def package(self, key):
        if key not in self.packages:
            descriptor = self.descriptors.get(key)
            if not descriptor or not descriptor["directory"].startswith("Skills/") or "_repos" in PurePosixPath(descriptor["directory"]).parts:
                raise BootstrapError(f"Pacote não aprovado: {key}")
            data = regular(self.root, descriptor["directory"] + "/PROVENANCE.json")
            if digest(data) != descriptor["manifest_sha256"]:
                raise BootstrapError(f"Manifesto de pacote adulterado: {key}")
            package = json.loads(data)
            if package["id"] != key or package["directory"] != descriptor["directory"]:
                raise BootstrapError(f"Identidade do pacote divergente: {key}")
            self.packages[key] = package
        return self.packages[key]

    def export(self, selection):
        files, origins, exported = {}, {}, []
        for identifier in selection["roots"]:
            skill = self.skills[identifier]
            key = skill["distribution"]["package"]
            package = self.package(key)
            if identifier not in package["skills"]:
                raise BootstrapError(f"Skill não pertence ao pacote declarado: {identifier}")
            try:
                relative_paths, closure = self.selected_files(identifier, self.catalog, package)
            except (ValueError, KeyError, TypeError) as exc:
                raise BootstrapError(f"Fechamento inválido de pacote: {identifier}") from exc
            if set(closure) - set(selection["selected"]):
                raise BootstrapError("Plano de exportação contém skill não selecionada")
            namespace = key.replace("/", "-").lower()
            for relative in relative_paths:
                source = package["directory"] + "/" + relative
                data = regular(self.root, source)
                expected = self.descriptors[key]["manifest_sha256"] if relative == "PROVENANCE.json" else package["files"][relative]["sha256"]
                if digest(data) != expected:
                    raise BootstrapError(f"Recurso adulterado: {source}")
                destination = ".agents/skills/" + namespace + "/" + relative
                if destination in files and files[destination] != data:
                    raise BootstrapError(f"Colisão entre skills: {destination}")
                files[destination] = data
                origins[destination] = {"package": key, "package_path": relative, "sha256": digest(data),
                                        "repository": package["repository"], "commit": package["commit"],
                                        "inputs": package["files"].get(relative, {}).get("inputs", [])}
        for identifier in selection["selected"]:
            skill = self.skills[identifier]
            key = skill["distribution"]["package"]
            exported.append({"id": identifier, "repository": skill["repository"], "commit": skill["commit"],
                             "source_path": skill["source_path"],
                             "prerequisites": skill["distribution"].get("runtime_requirements", []),
                             "path": ".agents/skills/" + key.replace("/", "-").lower() + "/" + skill["distribution"]["skill_directory"] + "/SKILL.md"})
        return files, origins, exported
