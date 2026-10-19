---
title: Quick Start
description: Get the docs-as-code pipeline running in your repo in under 30 minutes.
last_updated: 2026-10-18
status: stable
---

# Quick Start

Get from zero to a live docs site with full CI/CD and linting in under 30 minutes.

## Prerequisites

- Python 3.9+
- Git
- A GitHub repo with Actions enabled

## Step 1 — Clone and install

```bash
git clone https://github.com/raja925/docs-as-code-starter.git my-docs
cd my-docs
pip install -r requirements.txt
```

## Step 2 — Install pre-commit hooks

```bash
pre-commit install
```

This registers the hooks defined in `.pre-commit-config.yaml`. From this point forward, every `git commit` automatically runs the lint suite against staged files.

## Step 3 — Serve locally

```bash
mkdocs serve
```

Open `http://127.0.0.1:8000`. The site hot-reloads on every file save.

## Step 4 — Enable GitHub Pages

1. Go to your repo **Settings → Pages**
2. Set source to **GitHub Actions**
3. Push any commit to `main`

The `deploy.yml` workflow builds the site and deploys it automatically.

## Step 5 — Configure for your team

Edit these files to match your project:

| File | What to change |
|---|---|
| `mkdocs.yml` | `site_name`, `site_url`, `repo_url`, nav structure |
| `scripts/terminology.json` | Your approved terms and banned variants |
| `scripts/lint_docs.py` | Stale content threshold (default: 90 days) |
| `.pre-commit-config.yaml` | Which hooks run and when |

## Verify the pipeline works

```bash
# Run the full lint suite manually
python scripts/lint_docs.py

# Test a pre-commit run against all files
pre-commit run --all-files

# Build the site locally (same as CI)
mkdocs build --strict
```

All three should pass clean before you open a PR.

!!! warning "If `mkdocs build --strict` fails"
    The `--strict` flag treats warnings as errors, matching CI behavior. Fix all warnings locally before pushing — CI will fail on the same issues.
