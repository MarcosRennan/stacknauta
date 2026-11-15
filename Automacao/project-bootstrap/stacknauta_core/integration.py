"""Integração aditiva de descoberta. O único motor de criação continua Bootstrap.

Os recursos e manifestos 2A permanecem byte a byte iguais. Entradas rasas delegam
às cópias físicas originais, sem links e sem duplicação dos recursos de terceiros.
"""
import json
import posixpath
import re

from . import BootstrapError
from .core import encoded
from .filesystem import MANIFEST, directory, publish, read, fingerprint, inspect_files, inventory
from .library import Library, digest
from . import lifecycle

MARKER = ".stacknauta/agent-integration.json"
# Template legado do Gemini CLI convencional, preservado para avaliação na 2H.
# Novos consumidores usam AGENTS.md diretamente, inclusive no Antigravity CLI.
LEGACY_GEMINI_IMPORTS = b"@./AGENTS.md\n\n@./.stacknauta/AGENT-INTEGRATION.md\n"


def additions(plan, library_root):
    catalog = Library(library_root).skills
    lock = json.loads(plan.files[".stacknauta/skills-lock.json"])
    files, entries, names = {}, [], set()
    for skill in lock["skills"]:
        record = catalog[skill["id"]]
        name = "stacknauta-" + record["name"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64 or name in names:
            raise BootstrapError(f"Nome de descoberta inválido/duplicado: {name}")
        names.add(name)
        path = f".agents/skills/{name}/SKILL.md"
        source = skill["path"]
        relative = posixpath.relpath(source, posixpath.dirname(path))
        description = "StackNauta: " + record["description"].strip()
        # JSON quoted scalars are valid YAML, including punctuation and newlines.
        body = (f"---\nname: {name}\ndescription: {json.dumps(description, ensure_ascii=False)}\n---\n\n"
                f"# {record['name']}\n\n"
                f"Entrada portátil para a skill aprovada `{skill['id']}`.\n\n"
                f"Leia integralmente [{record['name']}]({relative}) antes de executar a tarefa.\n"
                "Essa cópia original contém as instruções e o contrato de distribuição. "
                "Resolva scripts, referências, dados, licenças e caminhos relativos a partir "
                "do diretório do SKILL.md original, nunca deste encaminhador. "
                "Carregue os recursos necessários e analise scripts antes de executá-los. "
                "Preserve as permissões do ambiente e a autorização do usuário.\n\n"
                f"Origem: {skill['repository']}\n\nCommit: `{skill['commit']}`\n\n"
                "Rastreabilidade e pré-requisitos: `.stacknauta/skills-lock.json` na raiz do projeto.\n")
        files[path] = body.encode()
        entries.append({"name": name, "id": skill["id"], "path": path,
                        "original_path": source, "original_sha256": digest(plan.files[source]),
                        "repository": skill["repository"], "commit": skill["commit"]})
    lines = ["# Descoberta das skills copiadas", "",
             "Entradas portáveis estão em .agents/skills/stacknauta-*/SKILL.md.",
             "Cada entrada exige ler o SKILL.md original indicado e usar seu diretório como base dos recursos.",
             "As cópias originais, licenças e arquivos geridos pelo núcleo 2A estão preservados.",
             "Codex e OpenCode podem também listar entradas originais aninhadas; use o alias stacknauta-* para o fluxo portátil.",
             "AGENTS.md é a base compartilhada de Codex, OpenCode e Gemini no Antigravity CLI (agy).",
             "Abra uma nova sessão no destino; no Antigravity CLI confira as skills com /skills.",
             "Respeite confiança do workspace, consentimento de ativação e permissões do agente.",
             "Leia .stacknauta/agent-plan.json: tarefas listadas não autorizam geradores, instalações ou serviços.",
             "Operações tecnológicas precisam de versões explícitas, plano, pré-requisitos e autorização aplicável.", ""]
    lines += [f"- `{s['name']}` → `{s['original_path']}`" for s in entries]
    files[".stacknauta/AGENT-INTEGRATION.md"] = ("\n".join(lines) + "\n").encode()
    identity = {"schema_version": 1, "integration_version": "2B.1", "core_plan_id": plan.plan_id,
                "skills": entries, "files": {p: {"sha256": digest(b), "size": len(b)} for p, b in sorted(files.items())}}
    plan_id = digest(encoded(identity))
    files[MARKER] = encoded({**identity, "plan_id": plan_id})
    if set(files) & (set(plan.files) | {MANIFEST, lifecycle.COMPLETION}):
        raise BootstrapError("Colisão entre integração e arquivos do núcleo")
    return plan_id, files, entries


def inspect(plan, files, *, complete=False):
    # Core.inspect already checks boundaries, hardlinks, symlinks and conflicts.
    if complete and plan.state["create"]:
        raise BootstrapError("Esqueleto incompleto; reaplique o mesmo plano autorizado antes de verificar")
    try:
        with directory(plan.target.path) as root:
            completed = fingerprint(root, MARKER, expected={"sha256": digest(files[MARKER]), "size": len(files[MARKER])}) is not None
            try:
                state = inspect_files(root, files, completed=completed)
            except BootstrapError as exc:
                raise BootstrapError(f"Integração preexistente diferente; preservada: {exc}") from exc
            state["initialization"] = "complete" if completed else "initializing"
            state["unmanaged"] = inventory(root, set(plan.expected_files()) | set(files))
            for entry in state["unmanaged"]:
                if entry["path"].startswith((".agents/skills/", ".stacknauta/")):
                    raise BootstrapError(f"Adicional proibido em área protegida: {entry['path']}")
    except FileNotFoundError:
        state = {"create": sorted(files), "unchanged": [], "modified": {}, "removed": [], "unmanaged": [], "initialization": "new"}
    except OSError as exc:
        raise BootstrapError(f"Destino da integração inacessível: {exc.strerror}") from exc
    if complete and state["create"]:
        raise BootstrapError("Integração incompleta: " + ", ".join(state["create"]))
    return state


class AgentIntegration:
    def __init__(self, bootstrap):
        self.bootstrap = bootstrap

    def plan(self, raw):
        plan = self.bootstrap.plan(raw)
        plan_id, files, entries = additions(plan, self.bootstrap.library_root)
        state = inspect(plan, files)
        report = plan.report()
        report.update({"plan_id": plan_id, "core_plan_id": plan.plan_id,
                       "integration_version": "2B.1", "discovery_entries": entries,
                       "integration_files": [{"path": p, "sha256": digest(b), "size": len(b),
                                              "classification": lifecycle.classification(p), "action": lifecycle.action(p, state)}
                                             for p, b in sorted(files.items())],
                       "integration_lifecycle": lifecycle.report(state),
                       "authorization": "Review both file lists and both hashes. A hash is not user authorization."})
        report["lifecycle"]["unmanaged"] = state["unmanaged"]
        return plan, files, report

    def apply(self, raw, expected_plan_id):
        plan, files, report = self.plan(raw)
        if expected_plan_id != report["plan_id"]:
            raise BootstrapError("plan_id da integração difere do dry-run; revise agent-plan novamente")
        # Reuses the original hash approval and all core runtime/library checks.
        core = self.bootstrap.apply(raw, report["core_plan_id"])
        try:
            with directory(plan.target.path) as root:
                # Recheck core ownership using the exact descriptor used to write.
                if read(root, MANIFEST, len(plan.manifest)) != plan.manifest:
                    raise BootstrapError("Manifesto do núcleo mudou antes da integração")
                state = inspect_files(root, files, completed=fingerprint(root, MARKER, expected={"sha256": digest(files[MARKER]), "size": len(files[MARKER])}) is not None)
                for path, data in files.items():
                    if path in state["create"]:
                        publish(root, path, data)
        except (OSError, BootstrapError) as exc:
            raise BootstrapError(f"Integração interrompida; arquivos existentes preservados. Reexecute o mesmo plano para completar ausências. Motivo: {exc}") from exc
        result = self.verify(raw)
        return {**result, "mode": "apply", "core_result": core}

    def verify(self, raw):
        plan, files, report = self.plan(raw)
        state = inspect(plan, files, complete=True)
        return {"status": "verified", "mode": "verify", "plan_id": report["plan_id"],
                "core_plan_id": plan.plan_id, "destination": plan.config["destination"],
                "core_files_verified": len(plan.expected_files()) - len(plan.state["removed"]),
                "integration_files_verified": len(files) - len(state["removed"]),
                "verification_state": "verified_with_evolution" if plan.state["modified"] or plan.state["removed"] or state["modified"] or state["removed"] else "intact",
                "lifecycle": report["lifecycle"], "integration_lifecycle": lifecycle.report(state),
                "discovery_entries": report["discovery_entries"], "production_ready": False,
                "native_agent_discovery": "Must be tested in a fresh session of the selected agent; filesystem verification is not native discovery."}
