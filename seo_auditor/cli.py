"""CLI: audit a live page's AI readability and search visibility via TinyFish."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .audit import run_audit
from .tinyfish_client import TinyFishError


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="seo-audit",
        description=(
            "Audit whether AI search and fetch tools can read a page, and how that ties to "
            "search visibility. Uses TinyFish Search, Fetch, and Agent against the live page."
        ),
    )
    p.add_argument("url", help="The page URL to audit (live, fetched fresh)")
    p.add_argument(
        "query", nargs="?", default=None, help="Optional target search query to check visibility for"
    )
    p.add_argument("--out", "-o", help="Write markdown report to a file instead of stdout")
    p.add_argument(
        "--json",
        action="store_true",
        help="Also write a machine-readable JSON report next to the markdown output",
    )
    p.add_argument(
        "--no-browser",
        action="store_true",
        help="Skip the TinyFish Agent browser probe (avoids the metered run)",
    )
    p.add_argument(
        "--fail-under",
        type=int,
        metavar="N",
        help="Exit 1 if the overall score is below N — use as a CI gate for AI-readiness",
    )
    p.add_argument("--location", help="Search geo, e.g. US, GB, IN")
    p.add_argument("--language", help="Search language, e.g. en, es")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    url = args.url if "://" in args.url else f"https://{args.url}"

    print(f"Auditing {url} (live)…", file=sys.stderr)
    print("  TinyFish Fetch: reading page as an AI tool would…", file=sys.stderr)
    if not args.no_browser:
        print("  TinyFish Agent: browser comprehension probe…", file=sys.stderr)
    print("  TinyFish Search: checking visibility…", file=sys.stderr)
    try:
        result = run_audit(
            url,
            args.query,
            with_browser=not args.no_browser,
            location=args.location,
            language=args.language,
        )
    except TinyFishError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    md = result.markdown
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        print(f"report: {out_path}", file=sys.stderr)
        if args.json:
            json_path = out_path.with_suffix(".json")
            json_path.write_text(result.json(), encoding="utf-8")
            print(f"json:   {json_path}", file=sys.stderr)
    else:
        print(md)
        if args.json:
            print(result.json(), file=sys.stderr)

    # Summary line to stderr
    s = result.scores
    crit = sum(1 for f in result.findings if f.severity == "critical")
    high = sum(1 for f in result.findings if f.severity == "high")
    print(
        f"\nOverall {s['overall_score']}/100 · readability {s['ai_readability_score']}/100 · "
        f"visibility {s['ai_visibility_score']}/100 · {len(result.findings)} findings "
        f"({crit} critical, {high} high)",
        file=sys.stderr,
    )
    print(s["verdict"], file=sys.stderr)
    if args.fail_under is not None and s["overall_score"] < args.fail_under:
        print(
            f"score gate: {s['overall_score']}/100 is below --fail-under {args.fail_under}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
