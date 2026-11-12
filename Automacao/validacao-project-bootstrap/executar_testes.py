"""Executa unittest e opcionalmente grava evidência; não instala ferramentas."""
import sys
sys.dont_write_bytecode = True
import argparse
import io
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Automacao/project-bootstrap"))
from stacknauta_core.runtimes import AsdfResolver


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="Destino explícito para relatório JSON, depois dos testes")
    args = parser.parse_args()
    runtimes = AsdfResolver(Path.home()).resolve([])
    suite = unittest.defaultTestLoader.discover(str(Path(__file__).parent), pattern="test_*.py")
    output = io.StringIO()
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    report = {"stage": "2A", "tested_at_utc": datetime.now(timezone.utc).isoformat(),
              "status": "passed" if result.wasSuccessful() else "failed", "tests_run": result.testsRun,
              "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped),
              "python_executor": runtimes["python"], "log": output.getvalue(),
              "limits": "Runtimes Go/JVM/Rust simulados sem execução; CLI real usa somente Python/Node globais já instalados. Projetos de teste são temporários; sem integração com agentes."}
    if args.report:
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "log"}, ensure_ascii=False, indent=2))
    if not result.wasSuccessful():
        print(output.getvalue(), file=sys.stderr)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
