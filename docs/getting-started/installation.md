---
title: Installation
description: Full dependency list and setup options for the docs-as-code starter kit.
last_updated: 2026-10-18
status: stable
---

# Installation

## Python dependencies

All dependencies are pinned in `requirements.txt`:

```
mkdocs==1.6.0
mkdocs-material==9.5.18
mkdocs-minify-plugin==0.8.0
pre-commit==3.7.1
linkchecker==10.4.0
pyyaml==6.0.1
python-frontmatter==1.1.0
rich==13.7.1
typer==0.12.3
```

Install with:

```bash
pip install -r requirements.txt
```

## Virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Node dependencies (optional)

If you want to use the Vale prose linter for additional style checks:

```bash
npm install -g vale
vale sync
```

Vale config is in `.vale.ini`. It runs as an optional pre-commit hook — the pipeline works without it.

## Docker (CI-equivalent local run)

To run the exact same environment as GitHub Actions:

```bash
docker run --rm -v $(pwd):/docs squidfunk/mkdocs-material build --strict
```

## Verify installation

```bash
mkdocs --version     # should print mkdocs, version 1.6.0
pre-commit --version # should print pre-commit 3.7.1
python scripts/lint_docs.py --help
```
