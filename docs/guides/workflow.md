---
title: Docs-as-Code Workflow
description: Branching strategy, review process, and team conventions for writing docs alongside code.
last_updated: 2026-10-18
status: stable
---

# Docs-as-Code Workflow

## Core principle

Documentation follows the same lifecycle as code: branch, write, review, merge. Every doc change goes through a PR. No direct commits to `main`.

## Branch strategy

```
main
  └── release/v2.4          ← version-tagged docs branch
  └── feat/new-auth-flow    ← feature branch (code + docs together)
  └── docs/fix-api-ref      ← docs-only fix
  └── docs/stale-content    ← bulk freshness update
```

**Naming convention:**

| Branch type | Prefix | Example |
|---|---|---|
| Feature (code + docs) | `feat/` | `feat/webhook-support` |
| Docs-only fix | `docs/` | `docs/fix-broken-links` |
| Docs-only new content | `docs/` | `docs/add-rate-limits-guide` |
| Release docs | `release/` | `release/v2.4` |

## Writing workflow

### 1. Branch off main

```bash
git checkout main && git pull
git checkout -b docs/add-webhook-guide
```

### 2. Write in Markdown

All docs live in `docs/`. Use frontmatter on every page:

```markdown
---
title: Webhook Events
description: Reference for all webhook event types and their payload schemas.
last_updated: 2026-10-18
status: draft   # draft | review | stable | deprecated
---
```

The `status` field controls the banner displayed on the page:

- `draft` → yellow "Work in progress" banner
- `review` → blue "Awaiting review" banner  
- `stable` → no banner
- `deprecated` → red "This page is deprecated" banner

### 3. Serve locally and verify

```bash
mkdocs serve
```

Check rendering, navigation placement, and that all internal links resolve.

### 4. Commit — hooks run automatically

```bash
git add docs/guides/webhooks.md
git commit -m "docs: add webhook events reference guide"
```

Pre-commit hooks run on staged files. Fix any failures before the commit lands.

### 5. Open a PR

PR title format: `docs: <what changed>`

PR description template (in `.github/pull_request_template.md`):

```
## What changed
<!-- One paragraph: what this doc covers and why it exists now -->

## Pages added or modified
- [ ] docs/guides/webhooks.md (new)

## SME review
- [ ] Reviewed by: @engineer-name
- [ ] Technical accuracy confirmed

## Checklist
- [ ] Frontmatter complete (title, description, last_updated, status: stable)
- [ ] All internal links verified
- [ ] Terminology follows approved list
- [ ] No content older than 90 days left as stale
```

### 6. CI runs automatically

GitHub Actions runs the full lint suite and build check on every PR. Merge is blocked until CI passes.

### 7. Merge → auto-deploy

Merge to `main` triggers the deploy workflow. Site is live within ~2 minutes.

## SME review process

For technical accuracy, route PRs to the owning engineer before merging:

1. Tag `@engineer` as reviewer in the PR
2. Engineer reviews for technical accuracy only (not prose style)
3. Writer resolves any technical corrections
4. Writer approves final prose, updates `status: stable`
5. Merge

Keep SME review cycles short: send engineers a bulleted list of specific questions rather than asking them to read the whole doc.

## Release docs process

For version-specific docs (release notes, upgrade guides, breaking changes):

```bash
git checkout -b release/v2.4
# Write release notes, upgrade guide, changelog
git push origin release/v2.4
# Open PR targeting main, tag release milestone
```

Tag the release in GitHub after merge — MkDocs versioning picks it up automatically if mike is configured.
