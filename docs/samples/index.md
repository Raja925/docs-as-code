---
title: Writing Samples
description: Independent technical writing samples on AI infrastructure, with the reader goal, the skills each one demonstrates, and its verification status.
last_updated: 2026-10-24
status: stable
---

# Writing Samples

These are independent technical writing samples. They aren't affiliated with or endorsed by the companies whose products they describe. Each page cites public sources, states what hasn't been verified, and lists open questions for the documentation or product team.

## Where To Start

Find your interest in the first column, then open the sample.

| If You Want To See | Open | Status |
|---|---|---|
| A goal-first decision table and a glossary of retired names | [NeMo Ecosystem Map](nemo-ecosystem-map.md) | Draft |
| Troubleshooting content organized by symptom across several products | [NIM Troubleshooting Guide](nim-troubleshooting-guide.md) | Draft |
| A setup guide, a tool comparison, and a check for outdated tutorials | [TensorRT-LLM Setup And vLLM Comparison](tensorrt-llm-setup-and-vllm.md) | Draft |

## What These Samples Show

| Skill | Where To See It |
|---|---|
| Organizing a large, fragmented product family by reader goal | [NeMo Ecosystem Map](nemo-ecosystem-map.md) |
| Merging overlapping documentation and reconciling conflicts | [NIM Troubleshooting Guide](nim-troubleshooting-guide.md) |
| Writing numbered procedures with verify steps | [TensorRT-LLM Setup And vLLM Comparison](tensorrt-llm-setup-and-vllm.md) |
| Catching outdated information across sources | [TensorRT-LLM Setup And vLLM Comparison](tensorrt-llm-setup-and-vllm.md) |
| Separating verified facts from open questions | All three samples |

## How I Wrote Them

1. Read the public documentation for each product and note where pages overlap or disagree.
2. Draft around the reader's goal, not the product's table of contents.
3. Run the repository's checks for frontmatter, heading depth, terminology, and links.
4. Mark each page `draft` until its commands and claims are tested against the running product.

!!! warning "Status Means What It Says"
    Every sample is a draft. The commands come from public documentation and haven't been run on a GPU host. Each page lists its gaps.
