---
title: Raja Antony Mandal, Technical Writing Portfolio
description: Portfolio of Raja Antony Mandal, a documentation engineer. Independent technical writing samples on AI infrastructure, plus a docs-as-code pipeline that keeps documentation correct.
last_updated: 2026-10-24
status: stable
hide:
  - navigation
  - toc
---

<!-- terminology: ignore-next-line -->
<div class="hero" markdown>

# Documentation That Works The First Time

<p class="hero-lead">I'm Raja Antony Mandal, a documentation engineer. I write task-first technical documentation, then build the pipelines that keep it accurate: linting, terminology control, and automated checks on every change.</p>

[View Writing Samples](samples/index.md){ .md-button .md-button--primary }
[See The Docs-as-Code Kit](starter-kit.md){ .md-button }

</div>

## Writing Samples

Independent samples on AI infrastructure. Each one starts from the reader's goal, uses numbered steps with a verify step, and ends with open questions for the product team.

<!-- terminology: ignore-next-line -->
<div class="grid cards" markdown>

- **[NeMo Ecosystem Map](samples/nemo-ecosystem-map.md)**

    Matches each goal to the right library, decodes retired product names, and flags a claim that needs confirmation.

- **[NIM Troubleshooting Guide](samples/nim-troubleshooting-guide.md)**

    Merges troubleshooting advice from three separate microservice pages into one symptom-first guide, and lists where the sources disagree.

- **[TensorRT-LLM Setup And vLLM Comparison](samples/tensorrt-llm-setup-and-vllm.md)**

    Shows the current install and serve steps and translates outdated engine-build instructions still found in tutorials.

</div>

!!! note "Independent Work"
    These samples aren't affiliated with or endorsed by the companies whose products they describe. Each page cites its public sources and lists what hasn't been verified.

## What I Do

<!-- terminology: ignore-next-line -->
<div class="grid cards two-col" markdown>

- **Write For Tasks**

    Goal-first tables, numbered steps, and a verify step after each procedure, so readers can tell whether it worked.

- **Verify Against Sources**

    Compare documentation with the product and with current release notes. Flag conflicts as open questions instead of guessing.

- **Build The Pipeline**

    Docs live in Git, and a linter, a terminology registry, and CI checks run on every pull request.

- **Work In Manufacturing**

    Write procedures for a battery cell manufacturing environment, where an unclear step has real consequences.

</div>

## How This Site Is Built

This site is itself a working docs-as-code project. Every page has required frontmatter, a heading-depth limit, and approved terminology, and a pull request can't merge until the checks pass. Refer to the [Docs-as-Code Starter Kit](starter-kit.md) for the pipeline and the [Writing Style Guide](guides/style-guide.md) for the rules.

## Contact

Find me on [LinkedIn](https://linkedin.com/in/raja-antony) or [GitHub](https://github.com/raja925).
