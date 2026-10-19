---
title: Writing Style Guide
description: Voice, tone, and formatting conventions for this documentation system.
last_updated: 2026-10-18
status: stable
---

# Writing Style Guide

## Voice and tone

Write for a developer who knows their domain but is new to this product. Assume competence; don't over-explain basics. Be direct.

**Do:** "Call the `/auth` endpoint with your API key in the `Authorization` header."  
**Don't:** "In order to successfully authenticate with the system, you will need to make a request..."

## Sentence structure

- One idea per sentence.
- Active voice. Subject does the action.
- Present tense for UI instructions ("Click **Save**"), past tense only for historical context.

**Do:** "The linter flags unapproved terms before your commit lands."  
**Don't:** "Unapproved terms will be flagged by the linter."

## Headings

- H1 (`#`): Page title only. One per page. Matches the `title` frontmatter field.
- H2 (`##`): Major sections.
- H3 (`###`): Subsections within a major section.
- Never skip levels. Never go deeper than H3.

```markdown
# Page Title          ← H1, one per page
## Major Section      ← H2
### Subsection        ← H3, maximum depth
```

## Procedures (step-by-step instructions)

Use numbered lists for any sequence where order matters:

```markdown
1. Open the terminal.
2. Run `mkdocs serve`.
3. Open `http://127.0.0.1:8000`.
```

Start each step with an imperative verb: Open, Run, Click, Select, Enter, Copy.

Never write steps as paragraphs. If a reader has to count, use a numbered list.

## Code blocks

Always specify the language for syntax highlighting:

````markdown
```python
def check_links(path: str) -> list[str]:
    ...
```
````

For commands the reader runs in a terminal, use `bash`:

````markdown
```bash
pre-commit run --all-files
```
````

For file paths and inline code, use backticks: `mkdocs.yml`, `scripts/lint_docs.py`.

## Admonitions

Use sparingly. If everything is a warning, nothing is.

```markdown
!!! tip "Optional: faster local builds"
    Run `mkdocs serve --dirtyreload` during active writing to skip full rebuilds.

!!! warning "Required before merge"
    All CI checks must pass. Merge is blocked otherwise.

!!! danger "Data loss risk"
    This action cannot be undone.
```

- `tip` → optional enhancement, shortcut, or nice-to-know
- `note` → important context that isn't a warning
- `warning` → something will break or fail if you skip this
- `danger` → data loss, security risk, or irreversible action

## Terminology

See the [Terminology Management guide](terminology.md) for the full approved term list.

Quick rules:
- Use the exact casing in `scripts/terminology.json` — the linter enforces it.
- When introducing a term for the first time on a page, bold it: **pre-commit hook**.
- Don't coin new terms. If something needs a name that isn't in the registry, add it there first.

## Links

Internal links use relative paths:

```markdown
See the [Configuration guide](../getting-started/configuration.md).
See the [linting rules](../reference/linting-rules.md#term-001-unapproved-terminology).
```

Never use absolute URLs for internal links — they break on versioned deployments.

External links open in the same tab by default. For links that leave the docs site, note this in the link text only if the destination is unexpected.

## Frontmatter (required on every page)

```yaml
---
title: Page Title            # Matches H1, used in nav and search
description: One sentence.   # Used in search results and social previews
last_updated: YYYY-MM-DD     # Updated every time the page content changes
status: stable               # draft | review | stable | deprecated
---
```

The linter fails the commit if any required frontmatter field is missing.
