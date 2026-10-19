---
title: Pre-commit Hooks Reference
description: What each pre-commit hook does, how to configure them, and how to run them manually.
last_updated: 2026-10-18
status: stable
---

# Pre-commit Hooks Reference

Pre-commit hooks are the first line of defense. They run locally on staged files before every commit, catching issues before they reach the PR queue.

## Installed hooks

| Hook ID | Script | What it checks | Blocks commit? |
|---|---|---|---|
| `lint-docs` | `scripts/lint_docs.py` | Frontmatter, heading structure, word count | Yes (errors only) |
| `check-terminology` | `scripts/check_terminology.py` | Unapproved term variants | Yes |
| `check-internal-links` | `scripts/check_links.py --internal` | Broken internal links | Yes |

External link checking runs in CI only (too slow for local pre-commit).

## Running hooks manually

```bash
# Run all hooks against staged files (same as git commit)
pre-commit run

# Run all hooks against every file in the repo
pre-commit run --all-files

# Run a single hook
pre-commit run lint-docs
pre-commit run check-terminology
pre-commit run check-internal-links

# Run against a specific file
pre-commit run --files docs/guides/workflow.md
```

## Skipping hooks

To skip all hooks for a single commit:

```bash
git commit --no-verify -m "wip: rough draft, fixing hooks next"
```

To skip a specific hook:

```bash
SKIP=check-internal-links git commit -m "adding stub pages, links coming"
```

Use `--no-verify` sparingly. CI will catch everything the hooks catch, so skipping locally just moves the failure to the PR.

## Updating hooks

Hook versions are pinned in `.pre-commit-config.yaml`. To update:

```bash
pre-commit autoupdate
```

Review the diff before committing — hook updates can introduce new rules.

## Adding a new hook

1. Write the script in `scripts/`.
2. Add an entry to `.pre-commit-config.yaml`:

```yaml
- id: my-new-hook
  name: My new check
  entry: python scripts/my_check.py --staged
  language: python
  types: [markdown]
  pass_filenames: false
```

3. Test: `pre-commit run my-new-hook --all-files`
4. Install the updated config: `pre-commit install`
