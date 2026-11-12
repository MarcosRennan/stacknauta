"""Clone local real sem cache: validadores anteriores, testes 2B e CLI compartilhada.

Não inicia agente/modelo. O apply é limitado aos fixtures temporários autorizados
para teste; obter um hash num teste não substitui autorização em uso normal.
"""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Automacao/project-bootstrap"))
from stacknauta_core.runtimes import AsdfResolver


def run(command, cwd):
    result = subprocess.run(command, cwd=cwd, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
                            capture_output=True, text=True, timeout=120)
    if result.returncode:
        raise SystemExit(result.stdout + "\n" + result.stderr)
    return json.loads(result.stdout)


def snapshot(root):
    return {p.relative_to(root).as_posix(): [hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_ino, p.stat().st_mtime_ns]
            for p in root.rglob("*") if p.is_file() and not p.is_symlink()}


def main():
    AsdfResolver(Path.home()).resolve([])
    previous = run([sys.executable, "-I", "-B", "Automacao/validacao-project-bootstrap/testar_clone.py"], ROOT)
    clone = Path(previous["library"]["temporary_clone"])
    tests = run([sys.executable, "-I", "-B", "Automacao/validacao-integracao-agentes/executar_testes.py"], clone)
    base = Path(tempfile.mkdtemp(prefix="stacknauta-2b-portable-"))
    config = base / "request.json"
    destination = base / "portable-api"
    request = {"name": "portable-api", "destination": str(destination),
               "stack": {"languages": ["python"], "frameworks": ["fastapi"]},
               "requirements": {"features": ["api"]}}
    config.write_text(json.dumps(request) + "\n")
    cli = clone / "Automacao/project-bootstrap/project-bootstrap"
    planned = run([str(cli), "agent-plan", "--config", str(config)], base)
    if destination.exists():
        raise SystemExit("Dry-run criou destino")
    applied = run([str(cli), "agent-apply", "--config", str(config), "--plan-id", planned["plan_id"]], base)
    before = snapshot(destination)
    repeated = run([str(cli), "agent-apply", "--config", str(config), "--plan-id", planned["plan_id"]], destination)
    verified = run([str(cli), "agent-verify", "--config", str(config)], destination)
    if before != snapshot(destination) or repeated["core_result"]["status"] != "unchanged":
        raise SystemExit("Reexecução alterou arquivos")
    for entry in planned["discovery_entries"]:
        if not (destination / entry["original_path"]).is_file():
            raise SystemExit("Skill original indisponível")
    if (clone / "Skills/_repos").exists():
        raise SystemExit("Clone contém cache")
    status = subprocess.check_output(["git", "-C", str(clone), "status", "--porcelain", "--untracked-files=all"], text=True)
    if status:
        raise SystemExit("Clone alterado: " + status)
    report = {"stage": "2B", "tested_at_utc": datetime.now(timezone.utc).isoformat(), "status": "passed",
              "tested_commit": previous["tested_commit"], "temporary_clone": str(clone),
              "previous_validators": previous, "integration_tests": tests,
              "real_cli": {"request": request, "core_plan_id": planned["core_plan_id"],
                           "plan_id": planned["plan_id"], "apply": applied, "verify": verified,
                           "idempotent_bytes_inode_mtime": True},
              "cache_present": False, "tree_clean_after_tests": True, "remote_configured": False,
              "limits": "No new model session or native activation. Evidence commit may add reports; tested_commit identifies the exact candidate. Temporary directories preserved."}
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
