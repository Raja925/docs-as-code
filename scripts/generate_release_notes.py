#!/usr/bin/env python3
"""
generate_release_notes.py — Release notes generator.

Parses git log between two tags and generates structured release notes
grouped by commit type (feat, fix, docs, breaking change).

Usage:
    python scripts/generate_release_notes.py --from v2.3 --to v2.4
    python scripts/generate_release_notes.py --from v2.3 --to v2.4 --output docs/release-notes/v2.4.md
"""

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path


COMMIT_TYPES = {
    "feat":     ("New features",      "✨"),
    "fix":      ("Bug fixes",         "🐛"),
    "docs":     ("Documentation",     "📝"),
    "perf":     ("Performance",       "⚡"),
    "refactor": ("Refactoring",       "♻️"),
    "test":     ("Tests",             "✅"),
    "chore":    ("Maintenance",       "🔧"),
    "ci":       ("CI/CD",             "🤖"),
    "breaking": ("Breaking changes",  "💥"),
}

CONVENTIONAL_RE = re.compile(
    r'^(?P<type>feat|fix|docs|perf|refactor|test|chore|ci|build)'
    r'(?:\((?P<scope>[^)]+)\))?'
    r'(?P<breaking>!)?'
    r':\s+(?P<description>.+?)(?:\s+\(#(?P<pr>\d+)\))?$',
    re.IGNORECASE
)


def get_commits(from_tag: str, to_tag: str) -> list[dict]:
    """Get commits between two tags."""
    range_spec = f"{from_tag}..{to_tag}"
    try:
        result = subprocess.run(
            ["git", "log", range_spec, "--pretty=format:%H|%s|%an|%ae"],
            capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error: git log failed: {e.stderr}", file=sys.stderr)
        sys.exit(1)

    commits = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("|", 3)
        if len(parts) < 4:
            continue
        sha, subject, author, email = parts
        commits.append({
            "sha": sha[:8],
            "subject": subject,
            "author": author,
        })

    return commits


def parse_commit(commit: dict) -> dict:
    """Parse a commit into its type, scope, and description."""
    subject = commit["subject"]
    m = CONVENTIONAL_RE.match(subject)

    if m:
        ctype = m.group("type").lower()
        breaking = bool(m.group("breaking")) or "BREAKING CHANGE" in subject
        if breaking:
            ctype = "breaking"
        return {
            **commit,
            "type": ctype,
            "scope": m.group("scope"),
            "description": m.group("description"),
            "pr": m.group("pr"),
            "breaking": breaking,
            "parsed": True,
        }

    # Non-conventional commit — put in misc
    return {
        **commit,
        "type": "misc",
        "scope": None,
        "description": subject,
        "pr": None,
        "breaking": False,
        "parsed": False,
    }


def format_markdown(from_tag: str, to_tag: str, commits: list[dict]) -> str:
    today = date.today().isoformat()
    lines = [f"## {to_tag} — {today}\n"]

    # Group by type
    groups: dict[str, list[dict]] = {}
    for c in commits:
        groups.setdefault(c["type"], []).append(c)

    # Render breaking changes first
    type_order = ["breaking", "feat", "fix", "perf", "docs", "refactor", "test", "chore", "ci", "misc"]

    for ctype in type_order:
        if ctype not in groups:
            continue
        label, emoji = COMMIT_TYPES.get(ctype, ("Other", "•"))
        lines.append(f"### {emoji} {label}\n")
        for c in groups[ctype]:
            scope = f"**{c['scope']}:** " if c.get("scope") else ""
            pr = f" (#{c['pr']})" if c.get("pr") else f" ({c['sha']})"
            lines.append(f"- {scope}{c['description']}{pr}")
        lines.append("")

    lines.append(f"\n**Full changelog:** `{from_tag}...{to_tag}`")
    return "\n".join(lines)


def format_frontmatter(to_tag: str) -> str:
    today = date.today().isoformat()
    return f"""---
title: Release Notes {to_tag}
description: What changed in {to_tag}.
last_updated: {today}
status: stable
---

"""


def main():
    parser = argparse.ArgumentParser(description="Generate release notes from git log")
    parser.add_argument("--from", dest="from_tag", required=True, help="Starting git tag")
    parser.add_argument("--to", dest="to_tag", required=True, help="Ending git tag")
    parser.add_argument("--output", type=Path, help="Write to file (default: stdout)")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    raw_commits = get_commits(args.from_tag, args.to_tag)
    if not raw_commits:
        print(f"No commits found between {args.from_tag} and {args.to_tag}.")
        sys.exit(0)

    parsed = [parse_commit(c) for c in raw_commits]

    if args.format == "json":
        import json
        output = json.dumps(parsed, indent=2)
    else:
        content = format_markdown(args.from_tag, args.to_tag, parsed)
        if args.output:
            content = format_frontmatter(args.to_tag) + content
        output = content

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
        print(f"Release notes written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
