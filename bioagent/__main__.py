"""Command line entry point; offline unless the pubmed command is selected."""
import argparse
import json
from pathlib import Path
import sys
from .demo import run_demo
from .pubmed import PubMedClient, PubMedError


def main():
    parser = argparse.ArgumentParser(description="BioAgentLab teaching toolkit")
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo", help="Run the synthetic offline workflow")
    demo.add_argument("--out", type=Path, default=Path("runs/micrometacell"))
    demo.add_argument("--budget", type=int, default=30)
    demo.add_argument("--overwrite", action="store_true")
    search = sub.add_parser("pubmed", help="Explicit online PubMed search (read-only)")
    search.add_argument("query")
    search.add_argument("--email", required=True)
    search.add_argument("--limit", type=int, default=5)
    search.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "demo":
            result = run_demo(args.out, args.budget, args.overwrite)
            print(json.dumps({"output": str(args.out), "stop_reason": result["stop_reason"],
                              "mode": result["mode"]}, ensure_ascii=False))
            return 2 if result["stop_reason"] == "budget_exhausted" else 0
        if args.out.exists():
            raise FileExistsError("Output file already exists")
        result = PubMedClient(args.email).search(args.query, args.limit)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Saved metadata: {args.out}")
        return 0
    except (ValueError, FileExistsError, PermissionError, PubMedError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
