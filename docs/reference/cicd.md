---
title: CI/CD Pipeline Reference
description: How the GitHub Actions CI and deploy workflows work, what they check, and how to debug failures.
last_updated: 2026-10-18
status: stable
---

# CI/CD Pipeline Reference

## Workflows

Two GitHub Actions workflows live in `.github/workflows/`:

| File | Trigger | Purpose |
|---|---|---|
| `ci.yml` | Every push to a PR branch | Lint, build check, external link scan |
| `deploy.yml` | Merge to `main` | Build and deploy to GitHub Pages |

## CI workflow (`ci.yml`)

Runs on every push to an open PR. Merge is blocked until all checks pass.

### Jobs

```
ci
├── lint          → python scripts/lint_docs.py --all
├── build         → mkdocs build --strict
└── check-links   → python scripts/check_links.py --external
```

**lint:** Runs the full linting suite against all docs. Fails on any Error-severity rule. Warnings are reported but don't block merge.

**build:** Runs `mkdocs build --strict`. Treats all MkDocs warnings as errors. Catches broken nav entries, missing files referenced in `mkdocs.yml`, and malformed Markdown.

**check-links:** Crawls every external URL in the docs corpus and reports non-200 responses. Retries once before flagging. Runs last because it's the slowest job.

### Reading CI failures

```
Run python scripts/lint_docs.py --all

FAIL TERM-001: docs/guides/workflow.md, line 23
  "login" → use "sign in"

FAIL LINK-001: docs/reference/cicd.md, line 67
  Link target not found: ../guides/nonexistent.md

2 errors, 0 warnings
```

Fix the named files at the named lines, push to the PR branch, and CI re-runs automatically.

## Deploy workflow (`deploy.yml`)

Triggers on merge to `main`. Runs `mkdocs build` and deploys the `site/` output to the `gh-pages` branch using `peaceiris/actions-gh-pages`.

Typical deploy time: 60–90 seconds from merge to live site.

### Deploy failure debugging

If deploy fails after a clean CI pass:

1. Check the Actions tab for the specific error in the deploy job log.
2. Common cause: GitHub Pages not configured to deploy from Actions. Go to **Settings → Pages → Source → GitHub Actions**.
3. Rare cause: `gh-pages` branch protection rules blocking the push. Remove branch protection from `gh-pages`.

## Secrets and permissions

No secrets beyond `GITHUB_TOKEN` are required. GitHub provides this automatically to all Actions workflows. No additional setup needed.

The deploy workflow uses:

```yaml
permissions:
  contents: write   # Required to push to gh-pages branch
  pages: write      # Required to deploy GitHub Pages
  id-token: write   # Required for OIDC token
```

## Adding a new CI check

To add a check to the CI pipeline:

1. Write the script in `scripts/`.
2. Add a step to `ci.yml`:

```yaml
- name: My new check
  run: python scripts/my_check.py --all
```

3. Test locally: `python scripts/my_check.py --all`
4. Push and verify the step appears in the Actions run.
