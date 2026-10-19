#!/usr/bin/env python3
"""
lint_docs.py — Main documentation linter.

Checks frontmatter completeness, heading structure, stale content,
and word count across Markdown files.

Usage:
    python scripts/lint_docs.py --all
    python scripts/lint_docs.py --staged
    python scripts/lint_docs.py --path docs/guides/workflow.md
"""

import argparse
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

import yaml

# ── Configuration ────────────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "lint": {
        "stale_threshold_days": 90,
        "min_word_count": 50,
        "require_frontmatter": ["title", "description", "last_updated", "status"],
        "valid_statuses": ["draft", "review", "stable", "deprecated"],
        "heading_max_depth": 3,
    }
}

RESET  = "\033[0m"
RED    = "\033[31m"
YELLOW = "\033[33m"
GREEN  = "\033[32m"
BOLD   = "\033[1m"


def load_config(config_path: Path) -> dict:
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f) or DEFAULT_CONFIG
    return DEFAULT_CONFIG


# ── File collection ──────────────────────────────────────────────────────────

def get_staged_files() -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True, text=True
    )
    return [
        Path(f) for f in result.stdout.splitlines()
        if f.endswith(".md") and Path(f).exists()
    ]


def get_all_files(docs_dir: Path) -> list[Path]:
    return list(docs_dir.rglob("*.md"))


def get_path_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix == ".md" else []
    return list(path.rglob("*.md"))


# ── Frontmatter parsing ──────────────────────────────────────────────────────

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body_without_frontmatter)."""
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        fm = {}
    return fm, parts[2]


# ── Individual checks ────────────────────────────────────────────────────────

class LintResult:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, rule: str, path: Path, msg: str, line: int = None):
        loc = f"line {line}" if line else ""
        self.errors.append(f"{RED}FAIL {rule}{RESET}: {path}" + (f", {loc}" if loc else "") + f"\n  {msg}")

    def warn(self, rule: str, path: Path, msg: str, line: int = None):
        loc = f"line {line}" if line else ""
        self.warnings.append(f"{YELLOW}WARN {rule}{RESET}: {path}" + (f", {loc}" if loc else "") + f"\n  {msg}")


def check_frontmatter(path: Path, fm: dict, body: str, config: dict, result: LintResult):
    required = config["lint"]["require_frontmatter"]
    valid_statuses = config["lint"]["valid_statuses"]

    # FRONT-001: missing required fields
    for field in required:
        if field not in fm or fm[field] is None:
            result.error("FRONT-001", path, f"Missing required frontmatter field: '{field}'")

    # FRONT-002: invalid status
    if "status" in fm and fm["status"] not in valid_statuses:
        result.error("FRONT-002", path,
                     f"Invalid status '{fm['status']}'. Must be one of: {', '.join(valid_statuses)}")

    # STALE-001: stale content
    if "last_updated" in fm and fm["last_updated"]:
        try:
            lu = fm["last_updated"]
            if isinstance(lu, date):
                last = lu
            else:
                last = datetime.strptime(str(lu), "%Y-%m-%d").date()
            delta = (date.today() - last).days
            threshold = config["lint"]["stale_threshold_days"]
            if delta > threshold:
                result.warn("STALE-001", path,
                            f"last_updated: {last} ({delta} days ago, threshold: {threshold})")
        except ValueError:
            result.error("FRONT-001", path,
                         f"last_updated format invalid: '{fm['last_updated']}'. Use YYYY-MM-DD.")


def check_headings(path: Path, content: str, config: dict, result: LintResult):
    max_depth = config["lint"]["heading_max_depth"]
    lines = content.split("\n")
    h1_count = 0
    h1_title = None
    in_code_block = False

    for i, line in enumerate(lines, 1):
        # Track fenced code blocks so we skip their contents
        if line.startswith("```") or line.startswith("~~~"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if not m:
            continue
        level = len(m.group(1))
        text = m.group(2).strip()

        if level == 1:
            h1_count += 1
            h1_title = text

        # STRUCT-001: heading depth exceeded
        if level > max_depth:
            result.warn("STRUCT-001", path, i,
                        f"Heading depth H{level} exceeds maximum H{max_depth}: '{text}'")

    # STRUCT-002: missing or multiple H1
    if h1_count == 0:
        result.error("STRUCT-002", path, "No H1 heading found. Every page must have exactly one H1.")
    elif h1_count > 1:
        result.error("STRUCT-002", path, f"Found {h1_count} H1 headings. Each page must have exactly one.")


def check_word_count(path: Path, body: str, config: dict, result: LintResult):
    # Strip markdown syntax for word count
    text = re.sub(r'```.*?```', '', body, flags=re.DOTALL)
    text = re.sub(r'`[^`]+`', '', text)
    text = re.sub(r'[#*_\[\]()>|]', ' ', text)
    words = text.split()
    min_words = config["lint"]["min_word_count"]
    if len(words) < min_words:
        result.warn("WORD-001", path,
                    f"Page has {len(words)} words (minimum: {min_words}). Likely a stub.")


# ── Main ─────────────────────────────────────────────────────────────────────

def lint_file(path: Path, config: dict, result: LintResult):
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        result.error("READ-ERR", path, f"Could not read file: {e}")
        return

    fm, body = parse_frontmatter(content)
    check_frontmatter(path, fm, body, config, result)
    check_headings(path, content, config, result)
    check_word_count(path, body, config, result)


def main():
    parser = argparse.ArgumentParser(description="Docs linter — frontmatter, headings, stale content")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="Scan all docs")
    group.add_argument("--staged", action="store_true", help="Scan staged files only")
    group.add_argument("--path", type=Path, help="Scan a specific file or directory")
    parser.add_argument("--config", type=Path, default=Path("scripts/config.yaml"))
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on warnings")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    config = load_config(args.config)
    result = LintResult()

    if args.all:
        files = get_all_files(Path("docs"))
    elif args.staged:
        files = get_staged_files()
    else:
        files = get_path_files(args.path)

    if not files:
        print("No Markdown files to lint.")
        sys.exit(0)

    print(f"Scanning {len(files)} file{'s' if len(files) != 1 else ''}...\n")
    for f in sorted(files):
        lint_file(f, config, result)

    if args.json:
        import json
        print(json.dumps({
            "errors": [re.sub(r'\033\[[0-9;]*m', '', e) for e in result.errors],
            "warnings": [re.sub(r'\033\[[0-9;]*m', '', w) for w in result.warnings],
        }, indent=2))
    else:
        for msg in result.errors + result.warnings:
            print(msg)

        e, w = len(result.errors), len(result.warnings)
        summary_color = RED if e else (YELLOW if w else GREEN)
        print(f"\n{summary_color}{BOLD}{e} error{'s' if e != 1 else ''}, {w} warning{'s' if w != 1 else ''}{RESET}")

    if result.errors or (args.strict and result.warnings):
        sys.exit(1)


if __name__ == "__main__":
    main()
