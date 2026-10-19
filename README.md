# Docs-as-Code Starter Kit

A production-ready documentation pipeline built with MkDocs Material, GitHub Actions, and Python tooling. Designed for engineering teams that want docs treated with the same rigor as software — versioned, tested, reviewed, and deployed automatically.

**[Live demo →](https://raja925.github.io/docs-as-code-starter)**

---

## What's in here

| Layer | What it does |
|---|---|
| **MkDocs Material site** | Searchable, responsive docs with dark mode, tabbed navigation, and copy-ready code blocks |
| **Docs linter** | Catches missing frontmatter, invalid status values, stale content, heading depth violations, and word count issues before they reach review |
| **Link checker** | Validates internal file references and heading anchors on every PR; checks external URLs in CI |
| **Terminology enforcer** | Keeps approved terms consistent across the entire corpus — no "login" when the standard is "sign in" |
| **Release notes generator** | Parses conventional commits between two git tags and outputs structured Markdown grouped by change type |
| **Stale content reporter** | Surfaces pages that haven't been updated past a configurable threshold, with CSV and JSON export for audit tracking |
| **Pre-commit hooks** | Runs the linter, terminology check, and internal link checker locally before any commit lands |
| **GitHub Actions CI/CD** | Lint → build → external link check on every PR; auto-deploy to GitHub Pages on merge to main |

---

## Quick start

```bash
git clone https://github.com/raja925/docs-as-code-starter.git
cd docs-as-code-starter
pip install -r requirements.txt
pre-commit install
mkdocs serve
```

Open `http://127.0.0.1:8000` — live-reloading preview updates as you edit.

---

## Pipeline overview

```
Author (branch) → pre-commit hooks → PR → CI lint/build → Merge → Deploy
      │                  │                    │
      │         lint_docs.py          check_links.py (external)
      │         check_terminology.py  mkdocs build --strict
      │         check_links.py (internal)
      │
      └── locally: mkdocs serve (live preview)
```

---

## Scripts

All scripts are standalone Python CLIs with no dependencies beyond the requirements file.

```bash
# Catch frontmatter issues, stale flags, heading depth violations
python scripts/lint_docs.py --all

# Enforce the terminology registry
python scripts/check_terminology.py --all

# Validate internal links and anchors
python scripts/check_links.py --internal --all

# Check external URLs (CI-friendly — warns, doesn't block)
python scripts/check_links.py --external --all

# Generate release notes from git log
python scripts/generate_release_notes.py --from v1.0 --to v1.1 --output docs/release-notes/v1.1.md

# Stale content report with threshold override
python scripts/stale_report.py --threshold 60 --format csv --output stale.csv
```

Full CLI reference in [`docs/api/scripts.md`](docs/api/scripts.md).

---

## Skills demonstrated

Built as a portfolio project to show what "docs as a product" looks like when applied end to end:

- **Content architecture** — nav taxonomy, page templates, frontmatter schema, and a style guide that enforces consistent voice across contributors
- **Tooling from scratch** — five Python scripts that do real work (AST parsing, git subprocess calls, HTTP link checking, YAML frontmatter validation) rather than wrapping existing tools
- **CI/CD for docs** — three-job GitHub Actions pipeline with dependency ordering, path filtering, and separate deploy workflow with GitHub Pages concurrency control
- **Developer experience** — pre-commit hooks keep the feedback loop local; contributors see lint failures before pushing, not after CI
- **Terminology governance** — registry-based enforcement with a suppress token for intentional exceptions; adding a new term is a one-line JSON change
- **Audit-readiness** — stale reporter outputs machine-readable CSV/JSON for quarterly freshness audits; linter exits non-zero so CI can gate on it

---

## Configuration

Lint thresholds and required fields live in `scripts/config.yaml`:

```yaml
lint:
  stale_threshold_days: 90
  min_word_count: 50
  require_frontmatter: [title, description, last_updated, status]
  valid_statuses: [draft, review, stable, deprecated]
  heading_max_depth: 3
```

Terminology rules live in `scripts/terminology.json` — one entry per term with `approved`, `banned`, and an optional `note`.

---

## Repo structure

```
docs-as-code-starter/
├── docs/
│   ├── index.md
│   ├── getting-started/
│   │   ├── quickstart.md
│   │   ├── installation.md
│   │   └── configuration.md
│   ├── guides/
│   │   ├── workflow.md
│   │   ├── style-guide.md
│   │   └── terminology.md
│   ├── reference/
│   │   ├── linting-rules.md
│   │   ├── cicd.md
│   │   └── pre-commit.md
│   └── api/
│       └── scripts.md
├── scripts/
│   ├── lint_docs.py
│   ├── check_links.py
│   ├── check_terminology.py
│   ├── generate_release_notes.py
│   ├── stale_report.py
│   ├── config.yaml
│   └── terminology.json
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   └── deploy.yml
│   └── pull_request_template.md
├── .pre-commit-config.yaml
├── mkdocs.yml
└── requirements.txt
```

---

## Author

**Raja Antony Mandal** — Documentation Engineer  
[LinkedIn](https://linkedin.com/in/rajaantony) · [Portfolio](https://raja925.github.io/portfolio) · rajaantony908@gmail.com
