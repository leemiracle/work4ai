<!-- source: DeepWiki mcp.deepwiki.com · repo vllm-project/vllm · page 4 Model Execution on GPU · fetched 2026-10-28 -->

# Model Execution on GPU

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tests/lora/test_gemma4_tp.py](tests/lora/test_gemma4_tp.py)
- [tests/model_executor/test_mamba_triton_warmup.py](tests/model_executor/test_mamba_triton_warmup.py)
- [tests/model_executor/test_qwen_triton_warmup.py](tests/model_executor/test_qwen_triton_warmup.py)
- [tests/model_executor/test_qwen_vl_triton_warmup.py](tests/model_executor/test_qwen_vl_triton_warmup.py)
- [tests/v1/cudagraph/test_cudagraph_manager.py](tests/v1/cudagraph/test_cudagraph_manager.py)
- [tests/v1/spec_decode/test_dynamic_sd_cug.py](tests/v1/spec_decode/test_dynamic_sd_cug.py)
- [tests/v1/spec_decode/test_eagle_draft_attn_metadata.py](tests/v1/spec_decode/test_eagle_draft_attn_metadata.py)
- [tests/v1/worker/test_gpu_batch_ordering.py](tests/v1/worker/test_gpu_batch_ordering.py)
- [tests/v1/worker/test_gpu_model_runner.py](tests/v1/worker/test_gpu_model_runner.py)
- [tests/v1/worker/test_gpu_model_runner_v2.py](tests/v1/worker/test_gpu_model_runner_v2.py)
- [tests/v1/worker/test_gpu_model_runner_v2_cudagraph_profiling.py](tests/v1/worker/test_gpu_model_runner_v2_cudagraph_profiling.py)
- [tests/v1/worker/test_gpu_model_runner_v2_eplb.py](tests/v1/worker/test_gpu_model_runner_v2_eplb.py)
- [tests/v1/worker/test_gpu_pcp_manager.py](tests/v1/worker/test_gpu_pcp_manager.py)
- [tests/v1/worker/test_gpu_ubatch_slicing.py](tests/v1/worker/test_gpu_ubatch_slicing.py)
- [tests/v1/worker/test_kv_block_zeroer.py](tests/v1/worker/test_kv_block_zeroer.py)
- [tests/v1/worker/test_workspace.py](tests/v1/worker/test_workspace.py)
- [vllm/model_executor/models/diffusion_gemma.py](vllm/model_executor/models/diffusion_gemma.py)
- [vllm/model_executor/warmup/mamba_triton_warmup.py](vllm/model_executor/warmup/mamba_triton_warmup.py)
- [vllm/model_executor/warmup/qwen_triton_warmup.py](vllm/model_executor/warmup/qwen_triton_warmup.py)
- [vllm/model_executor/warmup/qwen_vl_triton_warmup.py](vllm/model_executor/warmup/qwen_vl_triton_warmup.py)
- [vllm/third_party/flash_linear_attention/ops/layernorm_guard.py](vllm/third_party/flash_linear_attention/ops/layernorm_guard.py)
- [vllm/v1/attention/ops/pcp.py](vllm/v1/attention/ops/pcp.py)
- [vllm/v1/worker/cp_utils.py](vllm/v1/worker/cp_utils.py)
- [vllm/v1/worker/gpu/attn_utils.py](vllm/v1/worker/gpu/attn_utils.py)
- [vllm/v1/worker/gpu/cp_utils.py](vllm/v1/worker/gpu/cp_utils.py)
- [vllm/v1/worker/gpu/cudagraph_utils.py](vllm/v1/worker/gpu/cudagraph_utils.py)
- [vllm/v1/worker/gpu/dp_utils.py](vllm/v1/worker/gpu/dp_utils.py)
- [vllm/v1/worker/gpu/eplb_utils.py](vllm/v1/worker/gpu/eplb_utils.py)
- [vllm/v1/worker/gpu/input_batch.py](vllm/v1/worker/gpu/input_batch.py)
- [vllm/v1/worker/gpu/mm/lora.py](vllm/v1/worker/gpu/mm/lora.py)
- [vllm/v1/worker/gpu/model_runner.py](vllm/v1/worker/gpu/model_runner.py)
- [vllm/v1/worker/gpu/model_states/__init__.py](vllm/v1/worker/gpu/model_states/__init__.py)
- [vllm/v1/worker/gpu/model_states/default.py](vllm/v1/worker/gpu/model_states/default.py)
- [vllm/v1/worker/gpu/model_states/encoder_decoder.py](vllm/v1/worker/gpu/model_states/encoder_decoder.py)
- [vllm/v1/worker/gpu/model_states/encoder_only.py](vllm/v1/worker/gpu/model_states/encoder_only.py)
- [vllm/v1/worker/gpu/model_states/interface.py](vllm/v1/worker/gpu/model_states/interface.py)
- [vllm/v1/worker/gpu/pcp_manager.py](vllm/v1/worker/gpu/pcp_manager.py)
- [vllm/v1/worker/gpu/spec_decode/dflash/cudagraph.py](vllm/v1/worker/gpu/spec_decode/dflash/cudagraph.py)
- [vllm/v1/worker/gpu/spec_decode/dflash/speculator.py](vllm/v1/worker/gpu/spec_decode/dflash/speculator.py)
- [vllm/v1/worker/gpu/spec_decode/eagle/speculator.py](vllm/v1/worker/gpu/spec_decode/eagle/speculator.py)
- [vllm/v1/worker/gpu/spec_decode/extract_hidden_states.py](vllm/v1/worker/gpu/spec_decode/extract_hidden_states.py)
- [vllm/v1/worker/gpu/spec_decode/multi_module_mtp/speculator.py](vllm/v1/worker/gpu/spec_decode/multi_module_mtp/speculator.py)
- [vllm/v1/worker/gpu/spec_decode/speculator.py](vllm/v1/worker/gpu/spec_decode/speculator.py)
- [vllm/v1/worker/gpu/spec_decode/standalone_ar/speculator.py](vllm/v1/worker/gpu/spec_decode/standalone_ar/speculator.py)
- [vllm/v1/worker/gpu/spec_decode/target_dependent_ar/speculator.py](vllm/v1/worker/gpu/spec_decode/target_dependent_ar/speculator.py)
- [vllm/v1/worker/gpu/states.py](vllm/v1/worker/gpu/states.py)
- [vllm/v1/worker/gpu/ubatch_utils.py](vllm/v1/worker/gpu/ubatch_utils.py)
- [vllm/v1/worker/gpu_model_runner.py](vllm/v1/worker/gpu_model_runner.py)
- [vllm/v1/worker/utils.py](vllm/v1/worker/utils.py)

</details>



## Purpose and Scope

This page gives a high-level map of GPU model execution in vLLM: how worker-side execution connects scheduled batches to model computation and outputs. It introduces `GPUModelRunner`, `Worker`, and the main execution stages, then links to child pages for implementation detail. The stable runner file explicitly aims to keep shared logic minimal and move model-specific behavior elsewhere. [vllm/v1/worker/gpu/model_runner.py:3-16]()

Sources: [vllm/v1/worker/gpu/model_runner.py:3-16]()

## Architecture Overview

GPU execution sits between the engine’s scheduling decisions and the model’s device-side computation. The runner prepares batch inputs and execution metadata, coordinates the forward pass and related cache work, and returns model outputs. Worker and executor concerns—such as device setup and process coordination—form the surrounding execution layer. [vllm/v1/worker/gpu_model_runner.py:143-169]()

### GPU Execution Entity Map: Natural Language to Code Entities

```mermaid
graph TB
    subgraph "Execution orchestration"
        "Worker" --> "GPUModelRunner"
    end

    subgraph "Batch preparation"
        "SchedulerOutput" --> "InputBatch"
        "InputBuffers" --> "InputBatch"
        "InputBatch" --> "BlockTables"
    end

    subgraph "GPU computation"
        "GPUModelRunner" --> "ModelState"
        "GPUModelRunner" --> "Attention metadata"
        "GPUModelRunner" --> "KV cache"
        "GPUModelRunner" --> "Sampler"
        "GPUModelRunner" --> "ModelRunnerOutput"
    end

    "InputBatch" --> "GPUModelRunner"
    "BlockTables" --> "GPUModelRunner"
```

The diagram connects execution concepts to code names: `Worker` and `GPUModelRunner` are imported together in the runner tests; `InputBatch` and its device buffers are defined in `input_batch.py`; and the runner’s imports identify model-state, attention, sampling, cache, and output components. [tests/v1/worker/test_gpu_model_runner.py:73-76](), [vllm/v1/worker/gpu/input_batch.py:19-40](), [vllm/v1/worker/gpu_model_runner.py:123-169]()

Sources: [tests/v1/worker/test_gpu_model_runner.py:73-76](), [vllm/v1/worker/gpu/input_batch.py:19-40](), [vllm/v1/worker/gpu_model_runner.py:123-169]()

| Concept | Code entity | Role in the overview |
|---|---|---|
| GPU execution coordinator | `GPUModelRunner` | Coordinates per-step execution; see [GPUModelRunner](#4.1). [tests/v1/worker/test_gpu_model_runner.py:73-76]() |
| Device worker | `Worker` | Worker-side entry into GPU execution; see [Worker and Executor Architecture](#4.2). [tests/v1/worker/test_gpu_model_runner.py:73-76]() |
| Per-step batch | `InputBatch` | Carries request mappings, token inputs, sequence metadata, and execution flags. [vllm/v1/worker/gpu/input_batch.py:38-116]() |
| Attention and cache setup | `get_kv_cache_spec`, `init_attn_backend`, `init_kv_cache` | Names used by GPU attention utilities for cache specifications and backend/cache initialization. [vllm/v1/worker/gpu/attn_utils.py:139-156]() |
| Captured execution dispatch | `BatchExecutionDescriptor`, `CudaGraphManager` | Describes execution shape and CUDA graph capture/dispatch coordination. [vllm/v1/worker/gpu/cudagraph_utils.py:70-96](), [vllm/v1/worker/gpu/cudagraph_utils.py:150-170]() |
| Model result | `ModelRunnerOutput`, `SamplerOutput` | Output types imported by the runner. [vllm/v1/worker/gpu_model_runner.py:157-169]() |

Sources: [tests/v1/worker/test_gpu_model_runner.py:73-76](), [vllm/v1/worker/gpu/input_batch.py:38-116](), [vllm/v1/worker/gpu/attn_utils.py:139-156](), [vllm/v1/worker/gpu/cudagraph_utils.py:70-96](), [vllm/v1/worker/gpu/cudagraph_utils.py:150-170](), [vllm/v1/worker/gpu_model_runner.py:157-169]()

## 4.1. GPUModelRunner

`GPUModelRunner` is the central coordination point for a GPU execution step. Its dependencies show the breadth of that role: it works with `InputBatch`, attention and KV-cache utilities, model states, CUDA graph support, sampling, speculative decoding, and result types. The separate `vllm/v1/worker/gpu/model_runner.py` describes a shared runner path intended to contain only behavior common across model types. [vllm/v1/worker/gpu_model_runner.py:123-169](), [vllm/v1/worker/gpu/model_runner.py:3-16]()

Execution can include generative or pooling paths and multimodal inputs; the runner imports corresponding interfaces and components. The details of forward-pass coordination, model states, CUDA graphs, block tables, and pooling or multimodal subcomponents belong in the child page. [vllm/v1/worker/gpu_model_runner.py:70-107](), [vllm/v1/worker/gpu_model_runner.py:157-171]()

For details, see [GPUModelRunner](#4.1).

Sources: [vllm/v1/worker/gpu_model_runner.py:70-107](), [vllm/v1/worker/gpu_model_runner.py:123-169](), [vllm/v1/worker/gpu_model_runner.py:157-171](), [vllm/v1/worker/gpu/model_runner.py:3-16]()

## 4.2. Worker and Executor Architecture

A `Worker` provides the worker-side context for GPU execution; the runner tests import `Worker` alongside `GPUModelRunner`, establishing their place in the GPU worker architecture. The supplied code excerpts do not show worker initialization or executor implementations, so device setup, memory profiling, and executor coordination are covered by the child page rather than detailed here. [tests/v1/worker/test_gpu_model_runner.py:73-76]()

For details, see [Worker and Executor Architecture](#4.2).

Sources: [tests/v1/worker/test_gpu_model_runner.py:73-76]()

## 4.3. InputBatch and Request State Management

`InputBatch` is the runner-facing representation of a batch. It contains request identifiers and mappings, scheduled-token counts, sequence and query metadata, token IDs and positions, padding information, and logit indices. `InputBuffers` provides reusable device buffers for several of these inputs. [vllm/v1/worker/gpu/input_batch.py:19-36](), [vllm/v1/worker/gpu/input_batch.py:38-116]()

This batch representation connects request state to GPU execution; the runner also imports `RequestState` and `BlockTables`. See the child page for how these state structures are maintained and updated across steps. [vllm/v1/worker/gpu_model_runner.py:105-105](), [vllm/v1/worker/gpu_model_runner.py:177-177]()

For details, see [InputBatch and Request State Management](#4.3).

Sources: [vllm/v1/worker/gpu/input_batch.py:19-36](), [vllm/v1/worker/gpu/input_batch.py:38-116](), [vllm/v1/worker/gpu_model_runner.py:105-105](), [vllm/v1/worker/gpu_model_runner.py:177-177]()

## 4.4. Sampling and Token Generation

Sampling follows model computation in the GPU execution path. The runner imports `Sampler`, logits-processing utilities, sampling metadata, and output types, indicating that token selection and associated processing are coordinated as part of execution. [vllm/v1/worker/gpu_model_runner.py:157-169](), [vllm/v1/worker/gpu_model_runner.py:172-176]()

For details on sampling parameters, logits processors, constraints, token selection, and logprobs, see [Sampling and Token Generation](#4.4).

Sources: [vllm/v1/worker/gpu_model_runner.py:157-169](), [vllm/v1/worker/gpu_model_runner.py:172-176]()

## 4.5. Speculative Decoding

Speculative decoding adds proposal and verification work to the target-model execution path. The runner imports speculator initialization and rejection-sampling components; the shared speculator interface includes proposal inputs such as hidden states and draft-token counts. [vllm/v1/worker/gpu_model_runner.py:157-170](), [vllm/v1/worker/gpu/spec_decode/speculator.py:61-103]()

For details on supported methods, draft-token handling, verification, and acceptance, see [Speculative Decoding](#4.5).

Sources: [vllm/v1/worker/gpu_model_runner.py:157-170](), [vllm/v1/worker/gpu/spec_decode/speculator.py:61-103]()

## 4.6. Determinism and Batch Invariance

Batch shape and execution mode are explicit parts of CUDA graph dispatch: `BatchExecutionDescriptor` records properties such as token and request counts, graph mode, and microbatch count. These mechanisms concern execution compatibility and performance; see the child page for determinism and batch-invariance guarantees. [vllm/v1/worker/gpu/cudagraph_utils.py:70-96]()

For details, see [Determinism and Batch Invariance](#4.6).

Sources: [vllm/v1/worker/gpu/cudagraph_utils.py:70-96]()

### GPU Model Execution Pipeline Overview

```mermaid
flowchart LR
    "SchedulerOutput" --> "InputBatch"
    "InputBatch" --> "Prepare inputs"
    "Prepare inputs" --> "Attention metadata and KV cache"
    "Attention metadata and KV cache" --> "Model forward"
    "Model forward" --> "Logits processing"
    "Logits processing" --> "Sampler"
    "Sampler" --> "Optional speculative proposal and verification"
    "Optional speculative proposal and verification" --> "ModelRunnerOutput"
```

This is a conceptual pipeline, not a literal call graph. The code excerpts show `SchedulerOutput` and `InputBatch` as runner dependencies, attention and cache setup utilities, and sampling, speculative-decoding, and output types as execution components. [vllm/v1/worker/gpu/model_runner.py:72-83](), [vllm/v1/worker/gpu/input_batch.py:38-116](), [vllm/v1/worker/gpu/attn_utils.py:139-156](), [vllm/v1/worker/gpu_model_runner.py:157-176]()

Sources: [vllm/v1/worker/gpu/model_runner.py:72-83](), [vllm/v1/worker/gpu/input_batch.py:38-116](), [vllm/v1/worker/gpu/attn_utils.py:139-156](), [vllm/v1/worker/gpu_model_runner.py:157-176]()

## Summary

GPU execution connects worker-side orchestration to batched model computation. `InputBatch` supplies request and token metadata; the runner coordinates attention/cache setup, model execution, sampling, and optional speculative decoding, then works with model-runner output types. The child pages provide the implementation-level detail for each part of this pipeline. [vllm/v1/worker/gpu/input_batch.py:38-116](), [vllm/v1/worker/gpu_model_runner.py:123-169](), [vllm/v1/worker/gpu_model_runner.py:172-176]()

Sources: [vllm/v1/worker/gpu/input_batch.py:38-116](), [vllm/v1/worker/gpu_model_runner.py:123-169](), [vllm/v1/worker/gpu_model_runner.py:172-176]()

---

