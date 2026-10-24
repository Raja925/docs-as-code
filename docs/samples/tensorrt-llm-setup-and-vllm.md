---
title: NVIDIA TensorRT-LLM Setup And vLLM Comparison
description: An independent writing sample that shows how to install and serve a model with NVIDIA TensorRT-LLM, compares it with vLLM, and flags outdated advice.
last_updated: 2026-10-24
status: draft
---

# NVIDIA TensorRT-LLM Setup And vLLM Comparison

!!! note "Independent Sample"
    This page is an independent technical writing sample. It isn't affiliated with or endorsed by NVIDIA or the vLLM project. NVIDIA and TensorRT are trademarks of NVIDIA Corporation, used here only to identify NVIDIA products. Every fact comes from a public source listed in [Sources](#sources). Check the current documentation for each tool before you rely on any detail.

NVIDIA TensorRT-LLM and vLLM both serve large language models (LLMs) and both expose an OpenAI-compatible server. Many articles describe TensorRT-LLM as a tool that needs a slow, separate engine-build step. NVIDIA's own migration guide says that step has been removed. This page shows the current setup and compares the two tools using their official documentation.

## Where To Start

Find your goal in the first column, then go to the section in the second column.

| Goal | Go To |
|---|---|
| Understand how the two tools differ | [Compare The Tools](#compare-the-tools) |
| Install TensorRT-LLM | [Install TensorRT-LLM](#install-tensorrt-llm) |
| Serve a model with TensorRT-LLM | [Serve A Model With TensorRT-LLM](#serve-a-model-with-tensorrt-llm) |
| Serve the same model with vLLM | [Serve A Model With vLLM](#serve-a-model-with-vllm) |
| Check whether a tutorial you found is out of date | [Outdated Instructions](#outdated-instructions) |
| Decide which tool fits your project | [Choose Between The Tools](#choose-between-the-tools) |

## Compare The Tools

This table uses statements from each project's official documentation. Rows where the documentation is silent say so.

| Topic | TensorRT-LLM | vLLM |
|---|---|---|
| Description | An open-source library for accelerating and optimizing LLM inference on NVIDIA GPUs | An open-source engine for LLM inference and serving |
| Hardware | NVIDIA GPUs. The overview cites B200 for native FP4 and H100 or later for FP8. | NVIDIA CUDA, AMD ROCm, Intel GPU, Google TPU, Ascend NPU, and Apple Silicon |
| Execution backend | PyTorch is the only backend. The TensorRT engine backend was removed. | Not applicable |
| Engine-build step | None. Hugging Face checkpoints load directly. | None in the quickstart. Some kernels compile at startup unless you run `vllm download-kernels`. |
| Install method | `pip3 install tensorrt_llm` or a pre-built NGC container | `pip` with an environment manager, as the quickstart describes |
| Tested Python version | 3.12 on Ubuntu 24.04 | 3.11 to 3.14 on Linux |
| Serve command | `trtllm-serve <model>` | `vllm serve <model>` |
| Default server port | 8000 | 8000 |
| Python API | `from tensorrt_llm import LLM, SamplingParams` | `from vllm import LLM, SamplingParams` |
| Speculative decoding | EAGLE, MTP, NGram | Draft models, EAGLE, MTP, N-gram, suffix decoding |

!!! note "Throughput Claims"
    The official pages reviewed for this sample don't publish a head-to-head benchmark. Third-party articles do, but their results depend on the GPU, model, and settings. This page doesn't repeat them. Refer to [Choose Between The Tools](#choose-between-the-tools) for how to test on your own workload.

## Install TensorRT-LLM

The pip path below follows NVIDIA's Linux installation page. That page lists Ubuntu 24.04 and Python 3.12 as the tested platform. It doesn't list other supported versions.

### Prepare The Host

1. If you use an NVIDIA Blackwell or Grace Hopper GPU, install the PyTorch build for CUDA 12.8. Earlier GPUs don't need this step.

    ```bash
    pip3 install torch==2.7.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
    ```

2. Install the OpenMPI development package.

    ```bash
    sudo apt-get -y install libopenmpi-dev
    ```

### Install The Package

1. Upgrade the packaging tools and install the wheel.

    ```bash
    pip3 install --upgrade pip setuptools && pip3 install tensorrt_llm
    ```

2. Run a short script to confirm the install. The first run downloads the model.

    ```python
    from tensorrt_llm import LLM, SamplingParams


    def main():
        llm = LLM(model="TinyLlama/TinyLlama-1.1B-Chat-v1.0")
        prompts = ["Hello, my name is", "The capital of France is"]
        sampling_params = SamplingParams(temperature=0.8, top_p=0.95)
        for output in llm.generate(prompts, sampling_params):
            print(f"Prompt: {output.prompt!r}, Generated text: {output.outputs[0].text!r}")


    if __name__ == "__main__":
        main()
    ```

**Verify:** The script prints a generated continuation for each prompt and exits without an error.

!!! tip "Use The Container To Skip The Prerequisites"
    The Quick Start Guide calls the pre-built release container on NVIDIA NGC the quickest option. The installation page suggests the Develop container instead of installing the prerequisites by hand. Refer to the Container Images page for current tags.

!!! warning "The Package Doesn't Install The CUDA Toolkit"
    The installation page says `pip install tensorrt-llm` doesn't install the CUDA Toolkit. You don't need it to deploy an existing engine. You do need it for Model Optimizer quantization. If you see a warning that `CUDA_HOME` isn't set, install the toolkit.

## Serve A Model With TensorRT-LLM

1. Inside the container or environment where TensorRT-LLM is installed, start the server.

    ```bash
    trtllm-serve "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    ```

2. In a second terminal, send a chat request. If the server runs in Docker, either publish port 8000 or attach to the container with `docker exec -it <container_id> bash`.

    ```bash
    curl -X POST http://localhost:8000/v1/chat/completions \
        -H "Content-Type: application/json" \
        -d '{
            "model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            "messages": [{"role": "user", "content": "Where is New York? Tell me in a single sentence."}],
            "max_tokens": 32,
            "temperature": 0
        }'
    ```

**Verify:** The response is a `chat.completion` object with an assistant message and token counts.

For a pre-quantized model, pass its name instead, such as `nvidia/Qwen3-8B-FP8`. Confirm that your GPU supports FP8 first.

## Serve A Model With vLLM

The vLLM quickstart documents this server command and default address.

1. Start the server.

    ```bash
    vllm serve Qwen/Qwen2.5-1.5B-Instruct
    ```

2. List the served models.

    ```bash
    curl http://localhost:8000/v1/models
    ```

**Verify:** The response lists `Qwen/Qwen2.5-1.5B-Instruct`. Use `--host` and `--port` to change the address.

For installation, the quickstart recommends the `uv` environment manager with Python 3.12. After installing, run `vllm download-kernels` to fetch precompiled kernels that would otherwise compile at startup. Refer to the vLLM quickstart for the full commands.

## Outdated Instructions

Search results and tutorials still describe the removed TensorRT engine workflow. Use this table to translate them. The migration guide doesn't name the release that removed the backend, so check the TensorRT-LLM release notes before you pin a version.

| Old Instruction | Current Behavior |
|---|---|
| Run `trtllm-build` to create an engine before serving | Not needed. `trtllm-build`, `trtllm-refit`, and `trtllm-prune` were removed. |
| Run `convert_checkpoint.py` for your model | Not needed. Hugging Face checkpoints load directly. |
| `LLM(backend="tensorrt")` | Raises a `ValueError`. Omit the `backend` argument. |
| `TrtLlmArgs` | Replaced by `TorchLlmArgs`, the default. |
| `from tensorrt_llm._tensorrt_engine import LLM` | Use `from tensorrt_llm import LLM`. |
| `--backend tensorrt` on the command line | Omit it, or pass `--backend pytorch`. |
| Plan for a long build every time the model changes | The migration guide describes no build step. |

!!! warning "Check The Date And The Commands"
    A third-party comparison article published in August 2026 and updated in October 2026 still describes a quantize-then-`trtllm-build` pipeline and a roughly 28-minute build. It also says the PyTorch backend is the default. If an article tells you to run `trtllm-build`, compare it against the migration guide before you follow it.

## Choose Between The Tools

The official documentation supports a few hardware and setup questions. Performance questions need your own test.

1. **Which GPUs do you run on?** If you use AMD, Intel, TPU, or Apple Silicon hardware, vLLM's documentation lists support and TensorRT-LLM's doesn't. If you use only NVIDIA GPUs, both are options.
2. **Which Python version do you need?** vLLM lists 3.11 to 3.14. TensorRT-LLM's pip page tests only 3.12.
3. **Do you need a feature only one tool lists?** For example, TensorRT-LLM documents disaggregated serving as a beta feature, and vLLM documents several quantization methods. Compare the feature pages for your model.
4. **How does each perform on your workload?** Start both servers with the same model, then send the same requests at your expected concurrency. Compare latency, throughput, and memory on your GPU.

## Open Questions

These are gaps a reader may hit. They're offered as suggestions for follow-up documentation, not as errors.

1. **Which release removed the TensorRT backend?** The migration guide doesn't say. A reader who pins an older version can't tell whether `trtllm-build` still applies.
2. **Which Python, CUDA, and driver versions are supported?** The pip page lists one tested platform and no support matrix. The legacy support matrix page I tried to read wasn't retrievable.
3. **What does the quickstart assume?** The Quick Start Guide gives no prerequisites or install commands and points to the Installation Guide.
4. **Does the Linux page cover the container commands?** It suggests the container but gives no `docker run` command.
5. **How should a reader compare performance?** NVIDIA's overview describes state-of-the-art performance but doesn't mention vLLM and doesn't link a comparable benchmark method.

## Conventions Used On This Page

This page mirrors writing conventions observed in NVIDIA documentation:

- Title Case headings
- A goal-to-section table at the top
- Numbered, imperative steps with a verify step
- "Refer to" for cross-references
- Note, tip, and warning callouts
- Commands and variable names in code formatting

NVIDIA's own style guide files weren't reviewed, so treat these as observed patterns, not official rules. This kit's own [Writing Style Guide](../guides/style-guide.md) uses sentence case for headings. This sample uses Title Case on purpose, to match the NVIDIA pages it studies.

## Sources

- [TensorRT-LLM Quick Start Guide](https://nvidia.github.io/TensorRT-LLM/latest/quick-start-guide.html)
- [TensorRT-LLM installation overview](https://nvidia.github.io/TensorRT-LLM/latest/installation/index.html)
- [Installing TensorRT-LLM on Linux](https://nvidia.github.io/TensorRT-LLM/latest/installation/linux.html)
- [TensorRT-LLM overview](https://nvidia.github.io/TensorRT-LLM/latest/overview.html)
- [Migration Guide: TensorRT Backend Removed](https://nvidia.github.io/TensorRT-LLM/legacy/tensorrt-backend-removal.html)
- [vLLM Quickstart](https://docs.vllm.ai/en/latest/getting_started/quickstart.html)
- [vLLM features](https://docs.vllm.ai/en/latest/features/)
- [vLLM vs TensorRT-LLM 2026 (third-party article)](https://www.spheron.network/blog/vllm-vs-tensorrt-llm-2026/)
