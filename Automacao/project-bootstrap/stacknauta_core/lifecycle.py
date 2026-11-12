"""Política por caminhos do contrato de geração, não por extensões."""
VERSION = "2D.1"
COMPLETION = ".stacknauta/bootstrap-complete.json"
EVOLUTIVE = frozenset({
    "pyproject.toml", "package.json", "tsconfig.json", "go.mod", "Cargo.toml",
    ".gitignore", "README.md", "AGENTS.md", "GEMINI.md", "BUILD-PLAN.md",
    "docs/REQUIREMENTS.json",
})


def classification(path):
    if path.startswith((".stacknauta/", ".agents/skills/")) or path == ".tool-versions":
        return "protected"
    if path in EVOLUTIVE:
        return "evolutive"
    if path == "src/lib.rs" or (path.startswith(("src/", "tests/")) and path.endswith("/.gitkeep")):
        return "development"
    return "protected"  # Caminhos gerados desconhecidos não recebem exceção implícita.


def action(path, state):
    if path in state["create"]:
        return "create"
    if path in state.get("modified", {}):
        return "preserve_modified"
    if path in state.get("removed", []):
        return "preserve_removed"
    return "unchanged"


def report(state):
    return {"policy_version": VERSION, "initialization": state["initialization"],
            "modified": state["modified"], "removed": state["removed"],
            "unmanaged": state.get("unmanaged", []),
            "content_validation": "Physical structure and protected hashes; application syntax/semantics are not certified."}
