"""CLI pequena, sem aplicação implícita e sem configuração de remotos."""
import sys
sys.dont_write_bytecode = True
import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Automacao/manutencao-skills"))
sys.path.insert(0, str(ROOT / "Skills/manutencao"))
sys.path.insert(0, str(ROOT / "Automacao/project-bootstrap"))
from stacknauta_core.runtimes import AsdfResolver
from stacknauta_core import BootstrapError
from atualizacoes import Updates
from inclusoes import Inclusions


def main():
    parser = argparse.ArgumentParser(description="Atualizações manuais da biblioteca StackNauta")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="Consultar origens cadastradas; somente leitura")
    update = sub.add_parser("update", help="Preparar candidato isolado e dry-run")
    update.add_argument("source", nargs="?")
    update.add_argument("--all", action="store_true")
    apply = sub.add_parser("apply", help="Promover plano revisado com autorização")
    apply.add_argument("session"); apply.add_argument("--plan-id", required=True); apply.add_argument("--approve", action="store_true")
    recover = sub.add_parser("recover", help="Recuperar transação interrompida sem exclusões")
    recover.add_argument("session"); recover.add_argument("--approve", action="store_true")
    add = sub.add_parser('add', help='Inspecionar origem/skill GitHub em área isolada, sem incorporar')
    add.add_argument('url');add.add_argument('--ref',dest='revision');add.add_argument('--path');add.add_argument('--source-id')
    review = sub.add_parser('review', help='Revisar candidatas; decisões individuais preparam um dry-run')
    review.add_argument('session',nargs='?');review.add_argument('--decisions',type=Path);review.add_argument('--review-id')
    args = parser.parse_args()
    try:
        runtime = AsdfResolver(Path.home()).resolve([])["python"]
        engine = Updates(ROOT, runtime={"manager": "asdf", "global_source": "~/.tool-versions", "version": runtime["version"]})
        if args.command == "check":
            rows = engine.check(); result = {"status": "consulta_concluida", "consultado_em_utc": datetime.now(timezone.utc).isoformat(), "origens": rows}
            failed = any(r["estado"] == "erro_consulta" for r in rows)
        elif args.command == "update":
            if bool(args.source) == bool(args.all): parser.error("Informe uma origem OU --all")
            result = engine.prepare({s['id'] for s in engine.sources()} if args.all else {args.source}); failed = result["status"] == "bloqueado"
        elif args.command == 'add':
            result=Inclusions(engine).add(args.url,revision=args.revision,path=args.path,source_id=args.source_id);failed=result['status']=='bloqueado'
        elif args.command == 'review':
            result=Inclusions(engine).review(args.session,decisions=args.decisions,review_id=args.review_id);failed=result['status']=='bloqueado'
        elif args.command == "apply":
            result = engine.apply(args.session, args.plan_id, approve=args.approve); failed = False
        else:
            result = engine.recover(args.session, approve=args.approve); failed = False
        if result.get('status')=='preparado':
            result = {k: result[k] for k in ("status", "session_id", "plan_id", "origens", "validacao", "autorizacao", "atomicidade")} | {
                "pacotes_afetados": result["details"]["affected_packages"], "novas_skills_pendentes": result["details"]["new_skills_pending"],
                "aprovadas_no_plano":result['details'].get('approved',[]),
                "arquivos_alterados": len(result["files"]), "plano_completo": str(engine.session(result["session_id"]) / "plan.json"),
                "diff_para_revisao": str(engine.session(result["session_id"]) / "review.diff")}
        print(json.dumps(result, ensure_ascii=False, indent=2)); return 2 if failed else 0
    except (ValueError, OSError, RuntimeError, BootstrapError, subprocess.SubprocessError, KeyError, TypeError) as exc:
        print(json.dumps({"status": getattr(exc, 'stacknauta_status', 'bloqueado'), "erro": str(exc)}, ensure_ascii=False), file=sys.stderr); return 2


if __name__ == "__main__": raise SystemExit(main())
