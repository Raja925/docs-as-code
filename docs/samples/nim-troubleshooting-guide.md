---
title: NVIDIA NIM Troubleshooting Guide
description: An independent writing sample that unifies NVIDIA NIM troubleshooting advice into one symptom-first guide and flags where the source pages disagree.
last_updated: 2026-10-24
status: draft
---

# NVIDIA NIM Troubleshooting Guide

!!! note "Independent Sample"
    This page is an independent technical writing sample. It isn't affiliated with or endorsed by NVIDIA. NVIDIA and NIM are trademarks of NVIDIA Corporation, used here only to identify NVIDIA products. Every fact comes from a public source listed in [Sources](#sources). Check the documentation for your NIM and version before you rely on any detail.

NVIDIA NIM microservices ship as containers, and each NIM family publishes its own troubleshooting page. The same failures appear on several pages under different headings, and the advice doesn't always match. This page merges them into one guide organized by what you see, not by which NIM you run.

The guide draws on the NIM for LLM and VLM, Speech NIM, and Earth-2 FourCastNet NIM pages. Other NIM families may behave differently.

## Where To Start

Find the symptom in the first column, then go to the section in the second column.

| Symptom | Go To |
|---|---|
| The container exits right away and mentions a missing or invalid NGC key | [Fix NGC Authentication Failures](#fix-ngc-authentication-failures) |
| Logs say no CUDA device or no GPUs are available | [Fix GPU Visibility And Driver Errors](#fix-gpu-visibility-and-driver-errors) |
| Startup stops with "CUDA driver failed to initialize" (Error 802 or 803) | [Fix GPU Visibility And Driver Errors](#fix-gpu-visibility-and-driver-errors) |
| `torch.OutOfMemoryError: CUDA out of memory` at any point | [Fix GPU Out-Of-Memory Errors](#fix-gpu-out-of-memory-errors) |
| The health endpoint returns 503 or "not ready" | [Fix Health Check Failures](#fix-health-check-failures) |
| Port 8000 is already in use | [Fix Port Conflicts](#fix-port-conflicts) |
| Startup takes a long time or the model downloads every run | [Cache The Model Between Runs](#cache-the-model-between-runs) |
| The container can't find model files or reads them in the wrong format | [Fix Missing Or Invalid Model Files](#fix-missing-or-invalid-model-files) |
| A Kubernetes pod stays in `Pending` | [Fix Kubernetes Scheduling And Storage Problems](#fix-kubernetes-scheduling-and-storage-problems) |
| Requests return 400 or 500 errors, or time out | [Fix Request Errors](#fix-request-errors) |

## Before You Troubleshoot

Collect these three things first. Most steps below depend on them.

1. **Container logs.** Run `docker logs <container_name_or_id>`. Note the first error, not the last one, because later errors are often a result of the first.
2. **GPU state.** Run `nvidia-smi` on the host. Note the driver version, the free memory, and any other processes using the GPU.
3. **Detailed logging.** For NIM for LLM and VLM, set `NIM_LOG_LEVEL` to `INFO` or `DEBUG`. The output then includes GPU topology and estimated memory requirements.

## Fix NGC Authentication Failures

NIM containers download models from NVIDIA NGC, so a missing or wrong key stops startup.

**Symptoms**

- `nimlib.exceptions.ManifestDownloadError: Error downloading manifest: The requested operation requires an API key, but none was found`
- `401 Unauthorized` or `NGC_API_KEY not set`
- `HTTP status client error (400 Bad Request)` for a URL at `api.ngc.nvidia.com`

**Steps**

1. Run `echo $NGC_API_KEY` on the host. If it prints nothing, export the key and pass it to the container with `-e NGC_API_KEY`.
2. Confirm the key has NGC Catalog access. If it doesn't, generate a new one on the NGC API keys page.
3. If you get a `400 Bad Request` and the key is set, check the key type. The NIM for LLM and VLM page attributes this error to a Legacy API key in `NGC_API_KEY`. Generate a Personal API key and set that instead.

**Verify:** Restart the container. The error no longer appears, and the logs show the model download starting.

!!! note "Kubernetes Certificate Errors Look Like Authentication Errors"
    In Kubernetes, `InvalidCertificate(NotValidForName)`, `hostname mismatch`, or `certificate verify failed` during a model download is a DNS problem, not a key problem. Refer to [Fix Kubernetes Scheduling And Storage Problems](#fix-kubernetes-scheduling-and-storage-problems).

## Fix GPU Visibility And Driver Errors

**Symptoms**

- Logs report no CUDA-capable device or no available GPUs.
- Startup stops with a `RuntimeError` that begins "CUDA driver failed to initialize".
- Error 803: "system has unsupported display driver / cuda driver combination".
- Error 802: "system not yet initialized".

**Steps**

1. Confirm the NVIDIA Container Toolkit is installed: `nvidia-ctk --version`.
2. Test GPU access from a plain container: `docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi`. If this fails, reinstall or reconfigure the toolkit before you go further.
3. Start NIM with the NVIDIA runtime: `docker run --runtime=nvidia --gpus all ...`.
4. If Error 803 persists, check which `libcuda.so` the container loaded. The path should point to the host driver, such as `/usr/lib/x86_64-linux-gnu/libcuda.so.1`, not to a `compat` directory.
5. If Error 802 persists on an NVSwitch system such as DGX A100 or H100, compare the driver and fabric manager versions with `nvidia-smi` and `nv-fabricmanager --version`. Start the service with `sudo systemctl start nvidia-fabricmanager`.

**Why Error 803 happens:** The NIM for LLM and VLM page explains that the image bundles CUDA compatibility libraries. The container toolkit should mount the host driver over them. If that mount fails, the bundled driver loads and may not match the host kernel driver. Causes include a missing toolkit, a runtime that isn't set to `nvidia`, a misconfigured Container Device Interface (CDI) mode, or an `LD_LIBRARY_PATH` that puts the compatibility libraries first.

**Verify:** The container passes the startup driver check and moves on to loading the model.

## Fix GPU Out-Of-Memory Errors

The right fix depends on when the error happens, so read the logs to find the phase first.

| Phase | What You See | Likely Cause |
|---|---|---|
| Weight loading | The error appears early, before any KV cache or graph messages | The weights don't fit at this precision and parallelism |
| KV cache allocation | The error follows weight loading and mentions KV cache or block allocation | The default context length needs more cache than is available |
| Fragmentation | The error cites memory "reserved by PyTorch but unallocated" | Temporary allocations split GPU memory into small blocks |
| CUDA graph capture or warm-up | The error follows messages about graph capture | Capture needs more memory than remains |
| After startup | Requests fail, or the server exits | Concurrency or context length exceeds headroom |

### Estimate Weight Memory

For NIM for LLM and VLM, estimate per-GPU weight memory as total parameters multiplied by bytes per parameter, divided by the tensor parallelism (TP) degree. BF16 and FP16 use 2 bytes per parameter, FP8 uses 1, and INT4 and NVFP4 use 0.5. For example, Llama 3.1 8B in BF16 at TP1 needs about 16 GB for weights alone.

### Fix Weight-Loading Errors

1. Run `list-model-profiles` in the container.
2. Choose a profile with higher TP or pipeline parallelism, or one that uses FP8 or NVFP4.
3. Prefer a precision your GPU supports natively, to avoid a performance penalty.

### Fix KV Cache Errors

1. Set `NIM_MAX_MODEL_LEN` to a lower value. Use the value in the warning NIM prints, or one that suits your workload. This caps input plus output tokens per request.
2. If the error is about fragmentation, set `PYTORCH_ALLOC_CONF=expandable_segments:True`. This changes allocator behavior and doesn't add capacity.

!!! warning "Don't Lower NIM_KVCACHE_PERCENT To Fix A KV Cache Error"
    Despite its name, `NIM_KVCACHE_PERCENT` sets the fraction of GPU memory the backend uses overall. The NIM for LLM and VLM page warns that lowering it to fix a KV cache error can make the error worse.

### Fix Graph Capture Errors

1. If the error follows KV cache allocation, lower `NIM_KVCACHE_PERCENT` in small steps. The source page uses 0.9 to 0.85 as an illustration, not as a validated value.
2. To test whether graph capture is the cause, set `NIM_DISABLE_CUDA_GRAPH=1`. This can reduce throughput.

### Fix Errors After Startup

1. Check the container logs and the readiness endpoint. Restart the container if the engine exited.
2. Review concurrency, context length, and memory headroom before you resend traffic.

### Fix Speech NIM Memory Errors

The Speech NIM page gives sizing examples. Magpie TTS Multilingual uses about 12.58 GiB at `batch_size=8` and 41.46 GiB at `batch_size=32`. To select the smaller batch size, set `NIM_TAGS_SELECTOR="name=magpie-tts-multilingual,batch_size=8"`. If other processes hold GPU memory, free them or select another device with `--gpus '"device=1"'`.

**Verify:** The container finishes loading, and the health endpoint returns ready.

## Fix Health Check Failures

**Symptoms**

- `/v1/health/ready` returns 503 or `{"status":"not ready"}`.
- `/v1/health/live` returns 503.

**Steps**

1. Watch the logs with `docker logs -f <container_name_or_id>`. A 503 during startup usually means the model is still downloading, deploying, or compiling. Wait for the ready message before you treat it as a failure.
2. If the logs show shared memory errors, add `--shm-size` to `docker run`. Refer to [Open Questions](#open-questions) for the conflicting values the source pages give.
3. If the container never becomes ready, return to the logs and find the first error. Then use the matching section of this guide.

**Verify:** Run `curl http://localhost:<port>/v1/health/ready`. The response reports ready. Use the port you published, which is 8000 by default for NIM for LLM and VLM and 9000 for Speech NIM.

## Fix Port Conflicts

**Symptom:** `Can't bind on address ('0.0.0.0', 8000): address already in use`, or an error that `0.0.0.0:8000` is in use.

**Steps**

1. Find the process holding the port: `sudo lsof -i :8000`.
2. Remap the host port when you start the container, for example `-p 8080:8000`.
3. Update client URLs to use the new host port.

!!! warning "Speech NIM Reserves Ports 8000 And 8001"
    On Speech NIM, port 8000 is the Triton HTTP endpoint and 8001 is the Triton gRPC endpoint. Don't set `NIM_HTTP_API_PORT` to either value. The default is 9000.

## Cache The Model Between Runs

**Symptom:** The container takes a long time to become ready, or it downloads the model on every start. The Speech NIM page reports startup times over 30 minutes on a first run, because the container downloads the model and may build TensorRT engines.

**Steps**

1. Create a cache directory on the host, for example `export LOCAL_NIM_CACHE=~/.cache/nim` and `mkdir -p "$LOCAL_NIM_CACHE"`.
2. Make the directory writable by the container user.
3. Mount it with `-v $LOCAL_NIM_CACHE:/opt/nim/.cache`.

**Verify:** Stop and restart the container. The second start skips the download.

For an air-gapped deployment, pre-populate the cache by following the caching workflow in your NIM's deployment guide. Make sure the container user can read the mounted directory.

## Fix Missing Or Invalid Model Files

This section applies to NIM for LLM when you serve your own model files. Run `list-model-profiles --model $NIM_MODEL_NAME` first to inspect compatibility and artifacts.

| Symptom | Cause | Fix |
|---|---|---|
| `Missing HuggingFace configuration file named config.json` | No `config.json` at the model root | Add `config.json` from the Hugging Face Hub. For unified checkpoints, also add `hf_quant_config.json`. |
| `Expected model format to be one of ['hf-safetensor', 'trtllm-engine', 'trtllm-ckpt', 'gguf']` | TensorRT-LLM config files are missing from the `trtllm_ckpt` or `trtllm_engine` subfolder | Place the TensorRT-LLM `config.json` in the subfolder that matches the model format |
| `Missing safetensors weights in /models/...` | No `*.safetensors` files | Add the weight files |
| `Missing gguf weights in /models/...` | No `*.gguf` files | Add the weight files |
| `Missing TRTLLM rank.*safetensors` | No `trtllm_ckpt/rank.*.safetensors` files | Add the rank checkpoint files |
| `Missing TRTLLM rank.*engine files` | No `trtllm_engine/rank.*.engine` files | Add the rank engine files |
| `Model architecture is None` | The configuration has no model architecture | Use a valid `config.json` that includes it |
| `Found unknown format of weights` | The weights aren't in a supported format | Convert them to a format the error message lists |
| `Failed to load the model config` and a prompt about `trust_remote_code` | The model uses custom code outside the Hugging Face transformers library | Set `NIM_FORCE_TRUST_REMOTE_CODE` |

!!! tip "Set A Served Model Name For Local Models"
    Without `NIM_SERVED_MODEL_NAME`, requests for a local model must use the absolute model path as the model name. Set the variable to a short name and use that name in the `model` field of requests.

## Fix Kubernetes Scheduling And Storage Problems

### Pod Stays In Pending

1. Run `kubectl describe pod <pod-name>` and read the Events section.
2. For taints, add tolerations to your Helm values.
3. For GPU shortages, run `kubectl describe nodes` and check the allocated resources.
4. For storage, run `kubectl get pvc` and check whether the claim is bound.

### Pods Fail After Scaling Or Upgrading

The Speech NIM page describes one specific case. With `statefulSet.enabled: false` and `persistence.enabled: true`, all replicas share one persistent volume claim. The default access mode, `ReadWriteOnce`, lets only one pod mount it. Choose one fix:

1. Set `persistence.accessMode: ReadWriteMany`, which needs a storage class such as NFS or CephFS. The page recommends this option.
2. Set `statefulSet.enabled: true` so each replica gets its own claim.
3. Set `nfs.enabled: true` and provide `nfs.server` and `nfs.path`.
4. Set `persistence.enabled: false`. Each pod then downloads the model again.

### Certificate Errors During Model Download

**Symptoms:** `InvalidCertificate(NotValidForName)`, `hostname mismatch`, or `certificate verify failed`.

**Cause:** The default `ClusterFirst` DNS policy with `ndots:5` expands `api.ngc.nvidia.com` through the pod's search domains. If a wildcard search domain exists, it returns an incorrect record.

**Fix:** Remove external wildcard domains from the pod search path, or keep `dnsPolicy: ClusterFirst` and set `dnsConfig.options` so `ndots` is `"1"`.

## Fix Request Errors

### Timeouts

If the client raises `requests.exceptions.ReadTimeout` while the container keeps computing, raise the client timeout. For Earth-2 FourCastNet NIM, you can also reduce `simulation_length`.

### HTTP 400 Or 500 Responses

For Earth-2 FourCastNet NIM on `/v1/infer`, check these in order:

1. `input_time` must be RFC 3339 without fractional seconds, for example `2023-01-01T00:00:00Z`.
2. `simulation_length` must be in the range the OpenAPI schema allows.
3. `variables` must be a comma-separated list of variable IDs, for example `t2m,z500,u10m`.
4. The input array must match the schema shape of batch size, 1, variables, latitudes, longitudes. The page recommends FP32.

### Parameters That Have No Effect

On NIM for LLM, `best_of` works only with the legacy TensorRT-LLM backend. On the vLLM backend, set `n` to request multiple completions and set `logprobs` to 1. Then rank the completions on the client by average log probability.

### Guided Decoding Fails

If a `guided_whitespace_pattern` fails to compile, the `outlines` backend may not support the regular expression. Switch to the `xgrammar` backend, which supports a wider range.

## Open Questions

These are gaps a reader may hit. They're offered as suggestions for follow-up documentation, not as errors.

1. **What shared memory size should I use?** The Earth-2 FourCastNet page recommends `--shm-size 4g`, and 8g for systems with many CPU cores. The Speech NIM page recommends `--shm-size=8GB`. The pages don't say whether the difference comes from the NIM or is an oversight.
2. **Which health endpoint port applies?** The Speech NIM page tests health on port 9000, while the other pages use 8000. A shared table of default ports per NIM would remove the guesswork.
3. **Is the `NIM_SERVED_MODEL_NAME` example correct?** An older NIM for LLM page shows `llama3-8b-instruct` in the export command and `lama3-8b-instruct` in the example request. This looks like a typo, but a reader would have to guess.
4. **Where is the cause for each driver check?** The NIM for LLM and VLM troubleshooting index lists the memory and driver pages without stating causes or fixes. A one-line cause on the index would let readers pick the right page faster.
5. **Which key types do other NIM families accept?** Only the NIM for LLM and VLM page names Legacy and Personal API keys. The other pages say only "API key".

## Conventions Used On This Page

This page mirrors writing conventions observed in NVIDIA documentation:

- Title Case headings
- A symptom-to-section table at the top
- Numbered, imperative steps with a verify step
- "Refer to" for cross-references
- Note, tip, and warning callouts
- Variable names and commands in code formatting

NVIDIA's own style guide files weren't reviewed, so treat these as observed patterns, not official rules. This kit's own [Writing Style Guide](../guides/style-guide.md) uses sentence case for headings. This sample uses Title Case on purpose, to match the NVIDIA pages it studies.

## Sources

- [Troubleshooting GPU Memory Out-of-Memory Errors, NIM for LLM and VLM](https://docs.nvidia.com/nim/large-language-models/latest/troubleshooting/memory.html)
- [Troubleshooting CUDA Driver Initialization Failures, NIM for LLM and VLM](https://docs.nvidia.com/nim/large-language-models/latest/troubleshooting/cuda-driver.html)
- [Troubleshooting index, NIM for LLM and VLM 2.0.4](https://docs.nvidia.com/nim/large-language-models/2.0.4/troubleshooting/index.html)
- [Troubleshoot NVIDIA NIM for LLMs, version 1.15.0](https://docs.nvidia.com/nim/large-language-models/1.15.0/troubleshoot.html)
- [Troubleshooting Common Issues for NVIDIA Speech NIM Microservices](https://docs.nvidia.com/nim/speech/latest/troubleshooting/common-issues.html)
- [Troubleshooting Guide for NVIDIA Earth-2 FourCastNet NIM](https://docs.nvidia.com/nim/earth-2/fourcastnet/latest/troubleshooting.html)
