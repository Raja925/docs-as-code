---
title: Linting Rules Reference
description: Full reference for every rule the docs linter enforces, with examples and fix guidance.
last_updated: 2026-10-18
status: stable
---

# Linting Rules Reference

The linter runs in two modes:

- **Pre-commit (staged files only):** Fast. Runs on every `git commit`. Checks frontmatter, terminology, and internal links on staged files.
- **CI (full corpus):** Thorough. Runs on every PR. Checks everything including external links, cross-references, and stale content across all docs.

## Rule catalog

### FRONT-001: Missing required frontmatter field

**Severity:** Error (blocks commit)

Every `.md` file must include these frontmatter fields:

```yaml
---
title: string
description: string
last_updated: YYYY-MM-DD
status: draft | review | stable | deprecated
---
```

**Fix:** Add the missing field. The error message names the specific field.

---

### FRONT-002: Invalid status value

**Severity:** Error (blocks commit)

`status` must be one of: `draft`, `review`, `stable`, `deprecated`.

**Fix:** Use one of the four valid values.

---

### FRONT-003: last_updated not updated

**Severity:** Warning (CI only)

If a file's `last_updated` date matches the date from the previous commit for that file, the linter warns that the frontmatter date was not updated.

**Fix:** Set `last_updated` to today's date whenever you change page content.

---

### LINK-001: Broken internal link

**Severity:** Error (blocks commit in pre-commit, blocks merge in CI)

A link like `[text](../path.md)` points to a file that does not exist.

```
FAIL LINK-001: docs/guides/workflow.md, line 42
  Link target not found: ../reference/nonexistent.md
```

**Fix:** Correct the path or remove the link.

---

### LINK-002: Broken anchor reference

**Severity:** Error (CI only)

A link like `[text](page.md#heading-anchor)` points to a heading that does not exist in the target file.

**Fix:** Check the heading exists and the anchor slug matches exactly (lowercase, hyphens, no special characters).

---

### LINK-003: Broken external link

**Severity:** Warning (CI only)

An external URL returned a non-200 status code.

**Fix:** Update the URL or remove the link. Transient failures (503, timeout) are retried once before flagging.

---

### TERM-001: Unapproved terminology

**Severity:** Error (blocks commit)

A banned term variant was found. The error names the banned term, the approved replacement, and the line number.

```
FAIL TERM-001: docs/guides/workflow.md, line 14
  "login" → use "sign in" (see terminology.json)
```

**Fix:** Replace the banned variant with the approved term. To suppress a false positive, use `<!-- terminology: ignore-next-line -->`.

---

### STALE-001: Content not updated within threshold

**Severity:** Warning (CI only)

`last_updated` is more than 90 days ago (configurable in `scripts/config.yaml`).

**Fix:** Review the page for accuracy and update `last_updated` to today's date. If the content is intentionally frozen (an archived version), set `status: deprecated`.

---

### STRUCT-001: Heading depth exceeded

**Severity:** Warning

Headings go deeper than H3 (`###`).

**Fix:** Restructure the content. If you need H4, the section is probably better split into a new page.

---

### STRUCT-002: H1 missing or multiple H1s

**Severity:** Error (blocks commit)

Every page must have exactly one H1. The H1 must match the `title` frontmatter field.

---

### WORD-001: Page below minimum word count

**Severity:** Warning (CI only)

Page has fewer than 50 words (configurable). Likely a stub or placeholder.

**Fix:** Complete the page or mark it `status: draft`.
