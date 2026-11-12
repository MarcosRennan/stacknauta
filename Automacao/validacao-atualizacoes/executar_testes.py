"""Executa fixtures locais com Python global asdf, sem atualizar origens reais."""
import sys
sys.dont_write_bytecode = True
import argparse
import io
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Automacao/project-bootstrap"))
from stacknauta_core.runtimes import AsdfResolver

def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--report", type=Path); args = parser.parse_args()
    runtime = AsdfResolver(Path.home()).resolve([])
    suite = unittest.defaultTestLoader.discover(str(Path(__file__).parent), pattern="test_*.py")
    output = io.StringIO(); result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    report = {"stage": "3A", "status": "passed" if result.wasSuccessful() else "failed", "tests_run": result.testsRun,
              "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped),
              "runtime": runtime, "log": output.getvalue(), "real_origins_updated": False}
    if args.report: args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "log"}, ensure_ascii=False, indent=2))
    if not result.wasSuccessful(): print(output.getvalue(), file=sys.stderr)
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__": raise SystemExit(main())
