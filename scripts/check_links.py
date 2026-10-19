#!/usr/bin/env python3
"""
check_links.py — Internal and external link checker.

Validates that all Markdown links resolve to existing files/anchors (internal)
and return 200 status codes (external).

Usage:
    python scripts/check_links.py --internal --all
    python scripts/check_links.py --external --all
    python scripts/check_links.py --internal --staged
"""

import argparse
import re
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path
from urllib.parse import urlparse

RESET = "\033[0m"
RED   = "\033[31m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
BOLD  = "\033[1m"

DOCS_DIR = Path("docs")

# Patterns
INTERNAL_LINK_RE = re.compile(r'\[([^\]]+)\]\((?!https?://)([^)]+)\)')
EXTERNAL_LINK_RE = re.compile(r'\[([^\]]+)\]\((https?://[^)]+)\)')
HEADING_RE       = re.compile(r'^#{1,6}\s+(.*)', re.MULTILINE)


def get_staged_files() -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True, text=True
    )
    return [Path(f) for f in result.stdout.splitlines()
            if f.endswith(".md") and Path(f).exists()]


def get_all_files() -> list[Path]:
    return list(DOCS_DIR.rglob("*.md"))


def heading_to_anchor(heading: str) -> str:
    """Convert heading text to GitHub-style anchor slug."""
    anchor = heading.lower()
    anchor = re.sub(r'[^\w\s-]', '', anchor)
    anchor = re.sub(r'\s+', '-', anchor.strip())
    return anchor


def get_page_anchors(path: Path) -> set[str]:
    """Return all heading anchors available on a page."""
    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return set()
    headings = HEADING_RE.findall(content)
    return {heading_to_anchor(h) for h in headings}


# ── Internal link checking ───────────────────────────────────────────────────

def check_internal_links(files: list[Path]) -> tuple[list[str], list[str]]:
    errors = []
    warnings = []

    for md_file in files:
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue

        in_code_block = False
        for i, line in enumerate(content.split("\n"), 1):
            # Skip fenced code blocks
            if line.startswith("```") or line.startswith("~~~"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue
            # Strip inline code spans before link matching
            line_stripped = re.sub(r'`[^`]+`', '', line)
            for match in INTERNAL_LINK_RE.finditer(line_stripped):
                raw_target = match.group(2)

                # Strip anchor from path
                if "#" in raw_target:
                    path_part, anchor = raw_target.split("#", 1)
                else:
                    path_part, anchor = raw_target, None

                # Skip mailto, tel, data URIs
                if path_part.startswith(("mailto:", "tel:", "data:")):
                    continue

                # Resolve relative to the linking file's directory
                if path_part:
                    target_path = (md_file.parent / path_part).resolve()
                else:
                    # Link is anchor-only (#section), refers to current page
                    target_path = md_file.resolve()

                # LINK-001: File not found
                if not target_path.exists():
                    errors.append(
                        f"{RED}FAIL LINK-001{RESET}: {md_file}, line {i}\n"
                        f"  Link target not found: {raw_target}"
                    )
                    continue

                # LINK-002: Anchor not found
                if anchor:
                    available = get_page_anchors(target_path)
                    if anchor not in available:
                        errors.append(
                            f"{RED}FAIL LINK-002{RESET}: {md_file}, line {i}\n"
                            f"  Anchor '#{anchor}' not found in {target_path.name}\n"
                            f"  Available: {', '.join(sorted(available)[:5]) or 'none'}"
                        )

    return errors, warnings


# ── External link checking ───────────────────────────────────────────────────

def check_url(url: str, timeout: int, retries: int) -> tuple[bool, str]:
    """Return (ok, reason)."""
    # Strip tracking params and fragments for cleaner requests
    parsed = urlparse(url)
    clean_url = parsed._replace(fragment="").geturl()

    headers = {"User-Agent": "docs-link-checker/1.0 (github.com/raja925/docs-as-code-starter)"}

    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(clean_url, headers=headers, method="HEAD")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status < 400:
                    return True, str(resp.status)
                return False, f"HTTP {resp.status}"
        except urllib.error.HTTPError as e:
            if e.code == 405:
                # HEAD not allowed, try GET
                try:
                    req = urllib.request.Request(clean_url, headers=headers)
                    with urllib.request.urlopen(req, timeout=timeout) as resp:
                        return resp.status < 400, str(resp.status)
                except Exception:
                    pass
            if attempt < retries:
                continue
            return False, f"HTTP {e.code}"
        except urllib.error.URLError as e:
            if attempt < retries:
                continue
            return False, str(e.reason)
        except Exception as e:
            if attempt < retries:
                continue
            return False, str(e)

    return False, "max retries exceeded"


def check_external_links(files: list[Path], timeout: int, retries: int) -> tuple[list[str], list[str]]:
    errors = []
    warnings = []
    seen_urls: dict[str, tuple[bool, str]] = {}

    for md_file in files:
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue

        for i, line in enumerate(content.split("\n"), 1):
            for match in EXTERNAL_LINK_RE.finditer(line):
                url = match.group(2)
                if url not in seen_urls:
                    ok, reason = check_url(url, timeout, retries)
                    seen_urls[url] = (ok, reason)
                else:
                    ok, reason = seen_urls[url]

                if not ok:
                    warnings.append(
                        f"{YELLOW}WARN LINK-003{RESET}: {md_file}, line {i}\n"
                        f"  External link returned {reason}: {url}"
                    )

    return errors, warnings


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Link checker for Markdown documentation")
    parser.add_argument("--internal", action="store_true")
    parser.add_argument("--external", action="store_true")
    parser.add_argument("--all-links", action="store_true", dest="all_links",
                        help="Check both internal and external")
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--all", action="store_true", dest="all_files")
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--retry", type=int, default=1)
    args = parser.parse_args()

    if args.all_links:
        args.internal = args.external = True

    if not args.internal and not args.external:
        parser.error("Specify at least one of --internal, --external, or --all-links")

    if args.staged:
        files = get_staged_files()
    else:
        files = get_all_files()

    if not files:
        print("No Markdown files to check.")
        sys.exit(0)

    all_errors, all_warnings = [], []

    if args.internal:
        print(f"Checking internal links in {len(files)} file(s)...\n")
        errors, warnings = check_internal_links(files)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    if args.external:
        print(f"Checking external links in {len(files)} file(s)...\n")
        errors, warnings = check_external_links(files, args.timeout, args.retry)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    for msg in all_errors + all_warnings:
        print(msg)

    e, w = len(all_errors), len(all_warnings)
    color = RED if e else (YELLOW if w else GREEN)
    print(f"\n{color}{BOLD}{e} error{'s' if e != 1 else ''}, {w} warning{'s' if w != 1 else ''}{RESET}")

    if all_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
