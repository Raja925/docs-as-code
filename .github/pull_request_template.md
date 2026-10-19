## What changed

<!-- One sentence: what did you add, update, or remove? -->

## Why

<!-- What problem does this solve, or what request does it address? -->

## Checklist

### Content
- [ ] Frontmatter is complete (`title`, `description`, `last_updated`, `status`)
- [ ] `status` reflects the actual state of the content (`draft` / `review` / `stable`)
- [ ] All new terms follow the [terminology registry](../docs/guides/terminology.md)
- [ ] No banned terms used (ran `python scripts/check_terminology.py --all`)

### Links and structure
- [ ] All internal links resolve (ran `python scripts/check_links.py --internal --all`)
- [ ] Heading depth does not exceed H3
- [ ] Code blocks include a language identifier (` ```python `, ` ```bash `, etc.)

### Lint
- [ ] Docs linter passes with no errors (ran `python scripts/lint_docs.py --all`)
- [ ] `mkdocs build --strict` passes locally

### Review
- [ ] SME review requested (if content is technical or product-specific)
- [ ] Screenshots or example output updated if the procedure changed
