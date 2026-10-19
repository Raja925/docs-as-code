---
title: Script Reference
description: CLI reference for all Python scripts in the scripts/ directory.
last_updated: 2026-10-18
status: stable
---

# Script Reference

All scripts live in `scripts/` and are designed to run both locally and in GitHub Actions CI.

---

## lint_docs.py

Main linting entrypoint. Runs frontmatter validation, heading structure checks, stale content detection, and word count checks.

```bash
python scripts/lint_docs.py [OPTIONS]
```

| Option | Default | Description |
|---|---|---|
| `--all` | — | Scan all `.md` files in `docs/` |
| `--staged` | — | Scan only git-staged `.md` files |
| `--path PATH` | — | Scan a specific file or directory |
| `--config PATH` | `scripts/config.yaml` | Path to config file |
| `--strict` | `false` | Exit non-zero on warnings (used in CI) |
| `--json` | `false` | Output results as JSON |

**Exit codes:**

- `0` — No errors (warnings may exist)
- `1` — One or more errors found
- `2` — Configuration error

**Example output:**

```
Scanning 42 files...

FAIL FRONT-001: docs/guides/new-guide.md
  Missing required frontmatter: description

WARN STALE-001: docs/reference/old-api.md
  last_updated: 2026-05-12 (158 days ago, threshold: 90)

1 error, 1 warning
```

---

## check_links.py

Link checker for internal and external links.

```bash
python scripts/check_links.py [OPTIONS]
```

| Option | Default | Description |
|---|---|---|
| `--internal` | — | Check internal links only |
| `--external` | — | Check external `https://` links only |
| `--all` | — | Check both internal and external |
| `--staged` | — | Staged files only |
| `--timeout INT` | `10` | HTTP timeout in seconds for external links |
| `--retry INT` | `1` | Retry count for failed external links |

**Example output:**

```
Checking internal links in 42 files...

FAIL LINK-001: docs/guides/workflow.md, line 34
  → ../reference/nonexistent.md (file not found)

FAIL LINK-002: docs/reference/cicd.md, line 67
  → ../guides/style-guide.md#nonexistent-heading (anchor not found)

2 errors
```

---

## check_terminology.py

Scans Markdown files for banned term variants defined in `scripts/terminology.json`.

```bash
python scripts/check_terminology.py [OPTIONS]
```

| Option | Default | Description |
|---|---|---|
| `--all` | — | Scan all docs |
| `--staged` | — | Staged files only |
| `--registry PATH` | `scripts/terminology.json` | Path to terminology registry |
| `--add-term` | — | Interactive: add a new approved term |

**Example output:**

```
Scanning terminology in 42 files...

FAIL TERM-001: docs/getting-started/quickstart.md, line 18
  "login" → use "sign in" (see terminology.json)

FAIL TERM-001: docs/guides/workflow.md, line 23
  "API Key" → use "API key" (case-sensitive rule)

2 errors
```

---

## generate_release_notes.py

Parses git log between two tags and generates a structured release notes draft.

```bash
python scripts/generate_release_notes.py --from v2.3 --to v2.4
```

| Option | Required | Description |
|---|---|---|
| `--from TAG` | Yes | Starting git tag |
| `--to TAG` | Yes | Ending git tag |
| `--output PATH` | No | Write to file instead of stdout |
<!-- terminology: ignore-next-line -->
| `--format` | `markdown` | Output format: `markdown` or `json` |

**Example output:**

```markdown
## v2.4 — 2026-10-18

### New features
- feat: add webhook event filtering (#234)
- feat: support multi-region deployments (#241)

### Bug fixes
- fix: resolve race condition in auth token refresh (#239)
- fix: correct broken link in getting-started guide (#242)

### Documentation
- docs: add webhook events reference guide (#238)
- docs: update CI/CD pipeline reference (#240)
```

---

## stale_report.py

Generates a report of all docs pages sorted by `last_updated`, oldest first.

```bash
python scripts/stale_report.py [OPTIONS]
```

| Option | Default | Description |
|---|---|---|
| `--threshold INT` | `90` | Flag pages older than this many days |
| `--format` | `table` | Output: `table`, `csv`, or `json` |
| `--output PATH` | stdout | Write to file |

Use this to plan quarterly freshness audits.
