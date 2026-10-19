---
title: Configuration
description: All configuration options for the docs-as-code starter kit.
last_updated: 2026-10-18
status: stable
---

# Configuration

## mkdocs.yml

The main site configuration. Key fields to update for your project:

```yaml
site_name: Your Project Docs          # Displayed in browser tab and header
site_url: https://yourorg.github.io/repo/  # Required for sitemap and canonical URLs
repo_url: https://github.com/yourorg/repo  # Adds "Edit on GitHub" links
edit_uri: edit/main/docs/             # Path to docs in your repo
```

## Lint script configuration

`scripts/lint_docs.py` reads settings from `scripts/config.yaml`:

```yaml
lint:
  stale_threshold_days: 90       # Flag pages not updated in this many days
  min_word_count: 50             # Flag suspiciously short pages
  require_frontmatter:
    - title
    - description
    - last_updated
    - status
  heading_max_depth: 3           # Warn if headings go deeper than H3

cross_refs:
  check_internal: true           # Validate all internal links
  check_anchors: true            # Validate #heading-anchors exist in target
  exclude_patterns:
    - "*.png"
    - "*.jpg"
    - "http*"                    # External links checked separately by CI
```

## Terminology registry

`scripts/terminology.json` defines approved terms and banned variants:

```json
{
  "terms": [
    {
      "approved": "API key",
      "banned": ["api key", "API Key", "apikey", "api_key"],
      "note": "Use title case: API key (not API Key)"
    },
    {
      "approved": "sign in",
      "banned": ["login", "log in", "log-in"],
      "note": "Use 'sign in' as verb, 'sign-in' as adjective"
    }
  ]
}
```

Add your project's terminology to this file. The pre-commit hook scans every staged `.md` file against these rules.

## Pre-commit hooks

`.pre-commit-config.yaml` controls which hooks run on commit:

```yaml
repos:
  - repo: local
    hooks:
      - id: lint-docs
        name: Docs linter (frontmatter, terminology, stale content)
        entry: python scripts/lint_docs.py --staged
        language: python
        types: [markdown]
        pass_filenames: false

      - id: check-links
        name: Internal link checker
        entry: python scripts/check_links.py --staged
        language: python
        types: [markdown]
        pass_filenames: false
```

To skip a hook for a single commit (use sparingly):

```bash
SKIP=check-links git commit -m "wip: draft"
```

## GitHub Actions

Two workflows live in `.github/workflows/`:

| Workflow | Trigger | What it does |
|---|---|---|
| `ci.yml` | Every PR | Full lint, build check, external link scan |
| `deploy.yml` | Merge to `main` | Build + deploy to GitHub Pages |

Configure the deploy target in `deploy.yml`:

```yaml
- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./site
```

No additional secrets needed — `GITHUB_TOKEN` is provided automatically by GitHub Actions.
