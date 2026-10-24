---
title: NVIDIA NeMo Ecosystem Map
description: An independent writing sample that maps NVIDIA NeMo libraries to the jobs they do and lists retired product names.
last_updated: 2026-10-24
status: draft
---

# NVIDIA NeMo Ecosystem Map

!!! note "Independent Sample"
    This page is an independent technical writing sample. It isn't affiliated with or endorsed by NVIDIA. NVIDIA and NeMo are trademarks of NVIDIA Corporation, used here only to identify NVIDIA products. Every fact comes from a public source listed in [Sources](#sources). Check current NVIDIA documentation before you rely on any detail.

NVIDIA NeMo is a set of libraries and services for training generative AI models and optimizing AI agents. It isn't a single product, so the first question is usually "Which piece do I need?" This page answers that question and decodes older names that still appear in articles and package registries.

## Where To Start

Find your goal in the first column, then follow the library name.

| Goal | Start With | What It Does |
|---|---|---|
| Prepare, filter, and deduplicate training data | NeMo Curator | Prepares data for training at scale |
| Detect and replace sensitive data | NeMo Anonymizer | Finds sensitive information and substitutes it |
| Pretrain or fine-tune on roughly 1 to 1,000 GPUs | NeMo Automodel | Provides PyTorch-native training for Hugging Face models |
| Pretrain or fine-tune on more than 1,000 GPUs | NeMo Megatron-Bridge | Provides pretraining and fine-tuning with Megatron-Core |
| Post-train with supervised fine-tuning (SFT), direct preference optimization (DPO), or group relative policy optimization (GRPO) | NeMo RL | Runs scalable post-training against environments |
| Build environments for evaluating and training agents | NeMo Gym | Defines the tasks, verification, tools, and state for an environment |
| Evaluate and benchmark models | NeMo Evaluator | Evaluates and benchmarks models |
| Add safety and policy rules to an LLM application | NeMo Guardrails | Adds programmable guardrails to conversational systems |
| Connect and optimize teams of agents | NVIDIA NeMo Agent toolkit | Connects existing agents to data sources and tools across frameworks |
| Extract documents and retrieve content for retrieval-augmented generation (RAG) | NeMo Retriever | Provides document extraction and retrieval for RAG pipelines |
| Customize, evaluate, and secure models through APIs on Kubernetes | NeMo microservices | Offers modular, API-first services for Kubernetes deployments |
| Work on speech models | NeMo (original repository) | Focuses on speech components |

Descriptions paraphrase the NVIDIA-NeMo GitHub organization page and the NeMo Gym ecosystem page. Refer to [Sources](#sources) for the links.

## How The Pieces Fit Together

The NeMo Gym documentation describes three libraries that cover much of the model lifecycle:

1. NeMo Curator prepares, filters, and deduplicates training data.
2. NeMo Gym defines the environments that agents are evaluated and trained in.
3. NeMo RL runs post-training against those environments.

The same page also lists NeMo Megatron-Bridge and NeMo Automodel as training libraries, and NeMo Guardrails, NeMo Agent toolkit, and NeMo Retriever as related libraries.

### Choosing By GPU Scale

!!! tip "Choose By GPU Scale First"
    The NVIDIA-NeMo GitHub organization page recommends different libraries depending on how many GPUs you have. Decide your scale before you pick a training library.

| GPU Scale | Recommended Libraries |
|---|---|
| 1 to 1,000 GPUs | NeMo Automodel, NeMo RL |
| More than 1,000 GPUs | NeMo Megatron-Bridge, NeMo RL |

## Old Names And Current Names

Articles, tutorials, and package registries still use names that NVIDIA has retired. Use this table to translate them.

| Old Name | Current Name | Notes |
|---|---|---|
| AgentIQ, then Agent Intelligence (AIQ) toolkit | NVIDIA NeMo Agent toolkit | Renamed in release 1.2.0 to align with the NeMo family of products. The release notes describe backward compatibility. |
| `agentiq` package | `nvidia-nat` | Renamed to `aiqtoolkit` in version 1.1.0, then to `nvidia-nat` in version 1.2.0. The transitional packages are planned for removal. |
| `aiq` module and command | `nat` | Deprecated in version 1.2.0 and planned for removal. |
| `nat info mcp` | `nat mcp client` commands | Changed in version 1.3.0. The `nat mcp serve` command now starts the MCP server. |
| `NVIDIA/NeMo-Automodel` repository path | `NVIDIA-NeMo/Automodel` | A documentation fix corrected links that used the old path. |
| NeMo Aligner | NeMo RL | Reported by a third-party article, not by NVIDIA documentation. Refer to the warning below. |
| Original NeMo repository (all components) | NeMo repository (speech) plus separate libraries | The original repository now focuses on speech. Other parts moved into libraries such as NeMo Automodel, NeMo Gym, and NeMo RL. |

!!! warning "Verify Before Relying On This"
    The NeMo Aligner row comes from a third-party article that says Aligner was archived on 2025-11-19 and consolidated into NeMo RL. Confirm the status on the NVIDIA-NeMo repositories before you act on it.

!!! note "Naming Rule For The Agent Toolkit"
    NVIDIA's contributor rules for the toolkit's documentation call for the full name "NVIDIA NeMo Agent toolkit" on first use and "NeMo Agent toolkit" afterward. The rules also forbid the retired names listed above.

## Open Questions

These are gaps a reader may hit. They're offered as suggestions for follow-up documentation, not as errors.

1. **How do NeMo microservices relate to NVIDIA NIM?** The microservices overview lists a NIM Proxy that gives one endpoint for all deployed NIM microservices. A third-party article asks whether NIM is part of NeMo and groups the two under inference and deployment. The pages reviewed don't state the relationship directly.
2. **What does "NeMo platform" refer to?** The NeMo Gym ecosystem page describes NeMo as a platform of specialized libraries. The microservices documentation describes a separate, Kubernetes-based suite. A reader can't tell from either page whether "platform" means one or both.
3. **Which libraries does the ecosystem page list?** Search-result excerpts of the NeMo Gym ecosystem page show different sibling libraries in different versions. For example, the version 0.5.0 excerpt mentions NeMo Evaluator, while the main-branch excerpt mentions NeMo Megatron-Bridge, NeMo Agent toolkit, and NeMo Retriever. The excerpts may be partial, but one complete, maintained list would still help.

## Conventions Used On This Page

This page mirrors writing conventions observed in NVIDIA documentation:

- Title Case headings
- A goal-to-library table at the top
- "Refer to" for cross-references
- Note, tip, and warning callouts
- Full product names on first use, with short names afterward
- Acronyms spelled out on first use

The conventions come from the public NVIDIA NeMo Relay README and the NeMo Agent toolkit contributor rules. NVIDIA's own style guide files weren't reviewed, so treat these as observed patterns, not official rules.

This kit's own [Writing Style Guide](../guides/style-guide.md) uses sentence case for headings. This sample uses Title Case on purpose, to match the NVIDIA pages it studies.

## Sources

- [NVIDIA-NeMo GitHub organization](https://github.com/nvidia-nemo)
- [NeMo Gym ecosystem page](https://docs.nvidia.com/nemo/gym/main/about/ecosystem)
- [NeMo Gym ecosystem page, version 0.5.0](https://docs.nvidia.com/nemo/gym/v0.5.0/about/ecosystem)
- [NeMo Gym ecosystem page, version 0.6.0](https://docs.nvidia.com/nemo/gym/v0.6.0/about/ecosystem)
- [NVIDIA NeMo Agent toolkit overview](https://docs.nvidia.com/nemo/agent-toolkit/1.3/index.html)
- [NeMo Agent toolkit 1.2 release notes](https://docs.nvidia.com/nemo/agent-toolkit/1.2/release-notes.html)
- [NeMo Agent toolkit 1.2 migration guide](https://docs.nvidia.com/nemo/agent-toolkit/1.2/resources/migration-guide.html)
- [NeMo Agent toolkit 1.3 migration guide](https://docs.nvidia.com/nemo/agent-toolkit/1.3/resources/migration-guide.html)
- [Overview of NeMo microservices](https://docs.nvidia.com/nemo/microservices/latest/about/index.html)
- [Automodel documentation link fixes](https://github.com/NVIDIA-NeMo/Automodel/pull/1374)
- [NeMo Agent toolkit documentation rules](https://github.com/NVIDIA/NeMo-Agent-Toolkit/pull/941)
- [NVIDIA NeMo Relay README](https://github.com/nvidia/nemo-relay)
- [NeMo framework overview (third-party article)](https://dev.classmethod.jp/en/articles/dgx-spark-nvidia-nemo-framework-overview-and-index/)
