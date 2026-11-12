"""CLI JSON do núcleo 2A. Use o launcher para iniciar com Python global asdf."""
import sys
sys.dont_write_bytecode = True
import argparse
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stacknauta_core import BootstrapError
from stacknauta_core.config import load
from stacknauta_core.core import Bootstrap


def main(argv=None):
    parser = argparse.ArgumentParser(description="Prepara somente o esqueleto inicial; sem geradores, instalações ou serviços.")
    parser.add_argument("command", choices=("plan", "apply"), help="plan é dry-run; apply exige o hash do plano revisado")
    parser.add_argument("--config", required=True, type=Path, help="Arquivo JSON declarativo")
    parser.add_argument("--plan-id", help="Obrigatório em apply; obtido de plan")
    args = parser.parse_args(argv)
    if args.command == "apply" and not args.plan_id:
        parser.error("apply exige --plan-id; execute e revise plan antes")
    if args.command == "plan" and args.plan_id:
        parser.error("--plan-id só se aplica a apply")
    try:
        bootstrap = Bootstrap(Path(__file__).resolve().parents[2])
        config = load(args.config)
        result = bootstrap.plan(config).report() if args.command == "plan" else bootstrap.apply(config, args.plan_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (BootstrapError, OSError, ValueError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc), "production_ready": False}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
