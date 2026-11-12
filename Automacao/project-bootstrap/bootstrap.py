"""CLI JSON compartilhada. Use o launcher para iniciar com Python global asdf."""
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
    parser.add_argument("command", choices=("plan", "apply", "agent-plan", "agent-apply", "agent-verify"), help="plan/agent-plan são dry-run; apply/agent-apply exigem o hash revisado")
    parser.add_argument("--config", required=True, type=Path, help="Arquivo JSON declarativo")
    parser.add_argument("--plan-id", help="Obrigatório em apply/agent-apply; hash do dry-run correspondente")
    args = parser.parse_args(argv)
    if args.command in ("apply", "agent-apply") and not args.plan_id:
        parser.error("apply/agent-apply exige --plan-id; execute e revise o dry-run correspondente antes")
    if args.command not in ("apply", "agent-apply") and args.plan_id:
        parser.error("--plan-id só se aplica a apply/agent-apply")
    try:
        bootstrap = Bootstrap(Path(__file__).resolve().parents[2])
        config = load(args.config)
        if args.command.startswith("agent-"):
            from stacknauta_core.integration import AgentIntegration
            integration = AgentIntegration(bootstrap)
            if args.command == "agent-plan":
                result = integration.plan(config)[2]
            elif args.command == "agent-apply":
                result = integration.apply(config, args.plan_id)
            else:
                result = integration.verify(config)
        else:
            result = bootstrap.plan(config).report() if args.command == "plan" else bootstrap.apply(config, args.plan_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (BootstrapError, OSError, ValueError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc), "production_ready": False}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
