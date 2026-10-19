---
title: Terminology Management
description: How the terminology registry works and how to add or update approved terms.
last_updated: 2026-10-18
status: stable
---

# Terminology Management

## Why terminology management matters

<!-- terminology: ignore-next-line -->
Terminology drift is one of the most common sources of documentation debt. When the same concept is called "API key," "api key," "apikey," and "access token" across different pages, readers lose confidence in the docs and search results fragment.

The terminology registry is the single source of truth for approved terms. The linter enforces it automatically.

## How it works

`scripts/terminology.json` defines every approved term, its banned variants, and a note explaining the rule. The pre-commit hook scans every staged `.md` file against this registry before a commit lands.

```
Writer types "login" instead of "sign in"
         ↓
git commit
         ↓
pre-commit hook runs scripts/check_terminology.py
         ↓
FAIL: terminology.md, line 14: "login" → use "sign in"
         ↓
Writer fixes and recommits
```

## Registry structure

```json
{
  "terms": [
    {
      "approved": "sign in",
      "banned": ["login", "log in", "log-in", "signin"],
      "note": "Verb form: 'sign in'. Adjective form: 'sign-in page'.",
      "case_sensitive": false
    },
    {
      "approved": "API key",
      "banned": ["api key", "API Key", "apikey", "api_key", "access key"],
      "note": "Two words, title-case 'API', lowercase 'key'.",
      "case_sensitive": true
    }
  ]
}
```

## Adding a new term

1. Open `scripts/terminology.json`.
2. Add an entry following the structure above.
3. Run `python scripts/check_terminology.py --all` to scan the full docs corpus for existing violations.
4. Fix any violations, then commit both the registry update and the fixes in the same PR.

## Requesting a term change

If an approved term needs to change (product rename, style guide update):

1. Open a PR that updates `scripts/terminology.json`.
2. Run `python scripts/check_terminology.py --all` to find all existing uses.
3. Update all occurrences in the same PR.
4. Tag your tech writer lead for review.

Never change a term in the registry without fixing all existing uses in the same commit — the CI scan will catch orphaned violations.

## Suppressing a false positive

If a term legitimately appears in a code block or as an example of what **not** to use, suppress the check inline:

```markdown
<!-- terminology: ignore-next-line -->
The old `login` endpoint is deprecated. Use `sign-in` instead.
```

Use this sparingly. Every suppression is a place where the registry isn't the source of truth.
