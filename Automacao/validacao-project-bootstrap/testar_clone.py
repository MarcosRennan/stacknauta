"""Reutiliza o clone da validação 1.5 e testa o núcleo inteiro sem cache."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Automacao/project-bootstrap"))
from stacknauta_core.runtimes import AsdfResolver


def run(command, cwd):
    result = subprocess.run(command, cwd=cwd, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
                            capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise SystemExit(result.stdout + "\n" + result.stderr)
    return json.loads(result.stdout)


def main():
    AsdfResolver(Path.home()).resolve([])
    library = run([sys.executable, "-I", "-B", "Skills/validacao/testar_clone.py"], ROOT)
    clone = Path(library["temporary_clone"])
    if (clone / "Skills/_repos").exists():
        raise SystemExit("Clone não deve conter cache")
    core = run([sys.executable, "-I", "-B", "Automacao/validacao-project-bootstrap/executar_testes.py"], clone)
    if core["status"] != "passed":
        raise SystemExit("Núcleo falhou no clone")
    status = subprocess.check_output(["git", "-C", str(clone), "status", "--porcelain"], text=True)
    if status:
        raise SystemExit("Testes alteraram a árvore do clone: " + status)
    tracked = subprocess.check_output(["git", "ls-files", "-z", "--", "Automacao"], cwd=clone, text=True).split("\0")
    fingerprints = {}
    for relative in tracked:
        if relative and (relative.endswith(".py") or "/examples/" in relative or relative.endswith("/project-bootstrap") or relative.endswith("/STATUS.json")):
            fingerprints[relative] = hashlib.sha256((clone / relative).read_bytes()).hexdigest()
    report = {"stage": "2A", "tested_at_utc": datetime.now(timezone.utc).isoformat(), "status": "passed",
              "tested_commit": library["tested_commit"], "core_file_fingerprints": fingerprints,
              "library": library, "core_tests": core, "cache_present": False,
              "tree_clean_after_tests": True, "agent_integration_tested": False, "production_ready": False,
              "limits": "Relatório pode ser incorporado por commit de evidência posterior; fingerprints identificam exatamente o código e os pacotes testados. Clone/temporários preservados."}
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
