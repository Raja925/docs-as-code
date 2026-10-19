#!/usr/bin/env python3
"""
stale_report.py — Stale content reporter.

Lists all docs pages sorted by last_updated, oldest first.
Useful for planning quarterly freshness audits.

Usage:
    python scripts/stale_report.py
    python scripts/stale_report.py --threshold 60
    python scripts/stale_report.py --format csv --output stale_report.csv
"""

import argparse
import csv
import io
import sys
from datetime import date, datetime
from pathlib import Path

import yaml

DOCS_DIR = Path("docs")
RESET  = "\033[0m"
RED    = "\033[31m"
YELLOW = "\033[33m"
GREEN  = "\033[32m"
BOLD   = "\033[1m"


def parse_frontmatter(content: str) -> dict:
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}


def get_page_data(path: Path, threshold_days: int) -> dict:
    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return None

    fm = parse_frontmatter(content)
    title = fm.get("title", path.stem)
    status = fm.get("status", "unknown")
    lu = fm.get("last_updated")

    if lu:
        try:
            if isinstance(lu, date):
                last = lu
            else:
                last = datetime.strptime(str(lu), "%Y-%m-%d").date()
            days_old = (date.today() - last).days
            stale = days_old > threshold_days
        except ValueError:
            last = None
            days_old = None
            stale = False
    else:
        last = None
        days_old = None
        stale = True  # No date = assume stale

    return {
        "path": str(path),
        "title": title,
        "status": status,
        "last_updated": str(last) if last else "missing",
        "days_old": days_old if days_old is not None else 9999,
        "stale": stale,
    }


def render_table(pages: list[dict], threshold: int):
    stale = [p for p in pages if p["stale"]]
    fresh = [p for p in pages if not p["stale"]]

    print(f"\n{BOLD}Stale Content Report{RESET} — threshold: {threshold} days")
    print(f"Scanned: {len(pages)} pages | "
          f"{RED}{len(stale)} stale{RESET} | "
          f"{GREEN}{len(fresh)} fresh{RESET}\n")

    if stale:
        print(f"{RED}{BOLD}Stale pages (oldest first):{RESET}")
        for p in sorted(stale, key=lambda x: x["days_old"], reverse=True):
            age = f"{p['days_old']}d" if p['days_old'] != 9999 else "no date"
            print(f"  {RED}●{RESET} {p['path']}")
            print(f"    Title: {p['title']} | Status: {p['status']} | Last updated: {p['last_updated']} ({age})")
        print()

    if fresh:
        print(f"{GREEN}{BOLD}Fresh pages:{RESET}")
        for p in sorted(fresh, key=lambda x: x["days_old"]):
            print(f"  {GREEN}●{RESET} {p['path']} — {p['last_updated']} ({p['days_old']}d)")


def render_csv(pages: list[dict]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["path", "title", "status", "last_updated", "days_old", "stale"])
    writer.writeheader()
    writer.writerows(pages)
    return output.getvalue()


def main():
    parser = argparse.ArgumentParser(description="Stale content report")
    parser.add_argument("--threshold", type=int, default=90,
                        help="Flag pages not updated in this many days (default: 90)")
    parser.add_argument("--format", choices=["table", "csv", "json"], default="table")
    parser.add_argument("--output", type=Path, help="Write to file instead of stdout")
    args = parser.parse_args()

    files = list(DOCS_DIR.rglob("*.md"))
    pages = [get_page_data(f, args.threshold) for f in files]
    pages = [p for p in pages if p is not None]
    pages.sort(key=lambda x: x["days_old"], reverse=True)

    if args.format == "table":
        render_table(pages, args.threshold)
    elif args.format == "csv":
        output = render_csv(pages)
        if args.output:
            args.output.write_text(output)
            print(f"Report written to {args.output}")
        else:
            print(output)
    elif args.format == "json":
        import json
        output = json.dumps(pages, indent=2)
        if args.output:
            args.output.write_text(output)
            print(f"Report written to {args.output}")
        else:
            print(output)

    # Exit non-zero if stale pages exist (useful for CI warnings)
    stale_count = sum(1 for p in pages if p["stale"])
    if stale_count > 0 and args.format == "table":
        sys.exit(1)


if __name__ == "__main__":
    main()
