#!/usr/bin/env python3
"""
check_terminology.py — Terminology registry enforcer.

Scans Markdown files for banned term variants defined in terminology.json
and reports violations with the approved replacement.

Usage:
    python scripts/check_terminology.py --all
    python scripts/check_terminology.py --staged
    python scripts/check_terminology.py --add-term
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

RESET  = "\033[0m"
RED    = "\033[31m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
BOLD   = "\033[1m"
CYAN   = "\033[36m"

DOCS_DIR      = Path("docs")
REGISTRY_PATH = Path("scripts/terminology.json")
SUPPRESS_TOKEN = "terminology: ignore-next-line"


def load_registry(registry_path: Path) -> list[dict]:
    if not registry_path.exists():
        print(f"{YELLOW}Warning: terminology registry not found at {registry_path}{RESET}")
        return []
    with open(registry_path) as f:
        data = json.load(f)
    return data.get("terms", [])


def get_staged_files() -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True, text=True
    )
    return [Path(f) for f in result.stdout.splitlines()
            if f.endswith(".md") and Path(f).exists()]


def get_all_files() -> list[Path]:
    return list(DOCS_DIR.rglob("*.md"))


def is_in_code_block(lines: list[str], line_idx: int) -> bool:
    """Check if a line index is inside a fenced code block."""
    in_block = False
    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_block = not in_block
        if i == line_idx:
            return in_block
    return False


def check_file(path: Path, terms: list[dict]) -> list[str]:
    errors = []
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"{RED}FAIL READ{RESET}: {path}\n  Could not read: {e}"]

    lines = content.split("\n")

    for i, line in enumerate(lines):
        # Check for suppression token on previous line
        if i > 0 and SUPPRESS_TOKEN in lines[i - 1]:
            continue

        # Skip lines inside code blocks
        if is_in_code_block(lines, i):
            continue

        for term in terms:
            approved = term["approved"]
            case_sensitive = term.get("case_sensitive", False)
            note = term.get("note", "")

            for banned in term["banned"]:
                flags = 0 if case_sensitive else re.IGNORECASE
                # Word boundary match
                pattern = r'\b' + re.escape(banned) + r'\b'
                if re.search(pattern, line, flags):
                    errors.append(
                        f"{RED}FAIL TERM-001{RESET}: {path}, line {i + 1}\n"
                        f"  \"{banned}\" → use \"{approved}\""
                        + (f"\n  Note: {note}" if note else "")
                    )

    return errors


def add_term_interactive(registry_path: Path):
    """Interactive prompt to add a new term to the registry."""
    print(f"\n{CYAN}{BOLD}Add a new term to the registry{RESET}\n")

    approved = input("Approved term: ").strip()
    if not approved:
        print("No term entered. Exiting.")
        return

    banned_input = input("Banned variants (comma-separated): ").strip()
    banned = [b.strip() for b in banned_input.split(",") if b.strip()]

    note = input("Rule note (optional): ").strip()
    case_sensitive = input("Case-sensitive? (y/N): ").strip().lower() == "y"

    new_term = {
        "approved": approved,
        "banned": banned,
        "case_sensitive": case_sensitive,
    }
    if note:
        new_term["note"] = note

    # Load existing registry
    if registry_path.exists():
        with open(registry_path) as f:
            data = json.load(f)
    else:
        data = {"terms": []}

    data["terms"].append(new_term)

    with open(registry_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\n{GREEN}Added '{approved}' to {registry_path}{RESET}")
    print(f"Run `python scripts/check_terminology.py --all` to find existing violations.")


def main():
    parser = argparse.ArgumentParser(description="Terminology registry enforcer")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true", help="Scan all docs")
    group.add_argument("--staged", action="store_true", help="Staged files only")
    group.add_argument("--add-term", action="store_true", help="Interactively add a term")
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH)
    args = parser.parse_args()

    if args.add_term:
        add_term_interactive(args.registry)
        return

    terms = load_registry(args.registry)
    if not terms:
        print("No terms in registry. Nothing to check.")
        sys.exit(0)

    if args.staged:
        files = get_staged_files()
    else:
        files = get_all_files()

    if not files:
        print("No Markdown files to check.")
        sys.exit(0)

    print(f"Scanning terminology in {len(files)} file(s) against {len(terms)} rules...\n")

    all_errors = []
    for f in sorted(files):
        all_errors.extend(check_file(f, terms))

    for msg in all_errors:
        print(msg)

    e = len(all_errors)
    color = RED if e else GREEN
    print(f"\n{color}{BOLD}{e} error{'s' if e != 1 else ''}{RESET}")

    if all_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
