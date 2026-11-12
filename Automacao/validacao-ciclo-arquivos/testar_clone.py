"""Reutiliza todos os validadores anteriores; exercita evolução pela CLI no clone."""
import sys
sys.dont_write_bytecode = True
import json
import os
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]


def run(command, cwd):
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=120,
                            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", GIT_OPTIONAL_LOCKS="0"))
    if result.returncode:
        raise SystemExit(result.stdout + "\n" + result.stderr)
    return json.loads(result.stdout)


def snapshot(destination):
    return {p.relative_to(destination).as_posix(): (p.read_bytes(), p.stat().st_ino, p.stat().st_mode,
                                                  p.stat().st_mtime_ns, p.stat().st_ctime_ns)
            for p in destination.rglob("*") if p.is_file()}


def main():
    previous = run([sys.executable, "-I", "-B", "Automacao/validacao-integracao-agentes/testar_clone.py"], ROOT)
    clone = pathlib.Path(previous["temporary_clone"])
    base = pathlib.Path(tempfile.mkdtemp(prefix="stacknauta-2d-portable-"))
    destination = base / "evolving-api"
    config = base / "config.json"
    config.write_text(json.dumps({"name": "evolving-api", "destination": str(destination),
                                 "stack": {"languages": ["python"], "frameworks": [{"name": "fastapi", "version": "0.162.5"}]}}))
    cli = clone / "Automacao/project-bootstrap/project-bootstrap"
    plan = run([str(cli), "agent-plan", "--config", str(config)], base)
    run([str(cli), "agent-apply", "--config", str(config), "--plan-id", plan["plan_id"]], base)
    with (destination / "pyproject.toml").open("a") as f:
        f.write("\n# legitimate technology setup\n" * 100)
    (destination / "src/user_module.py").write_text("# subsequent development\n")
    (destination / "tests/user_test.py").write_text("# subsequent tests\n")
    before = snapshot(destination)
    verified = run([str(cli), "agent-verify", "--config", str(destination / ".stacknauta/config.json")], base)
    applied = run([str(cli), "agent-apply", "--config", str(config), "--plan-id", plan["plan_id"]], base)
    assert snapshot(destination) == before
    assert verified["verification_state"] == "verified_with_evolution"
    assert applied["core_result"]["status"] == "unchanged"
    assert not (clone / "Skills/_repos").exists()
    assert not subprocess.check_output(["git", "-C", str(clone), "status", "--porcelain"], text=True)
    print(json.dumps({"stage": "2D", "status": "passed", "tested_commit": previous["tested_commit"],
                      "temporary_clone": str(clone), "cache_present": False,
                      "prior_validators": previous, "evolved_cli": {"plan_id": plan["plan_id"],
                          "core_plan_id": plan["core_plan_id"], "verification_state": verified["verification_state"],
                          "modified": verified["lifecycle"]["modified"], "reapply_status": applied["core_result"]["status"],
                          "bytes_inode_mode_mtime_ctime_preserved": True}, "tree_clean_after_tests": True,
                      "limits": "No dependencies installed, generators or other agents. Temporary projects preserved. Evidence commit may add reports only."}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
