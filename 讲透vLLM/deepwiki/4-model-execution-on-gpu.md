# Model Execution on GPU

> 来源: https://deepwiki.com/vllm-project/vllm/4-model-execution-on-gpu 抓取日期: 2026-09-02
> 章节: 第 4 章 GPU 上的模型执行

---

Relevant source files

  * [tests/config/test_config_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/config/test_config_utils.py)
  * [tests/distributed/test_multiproc_executor.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/distributed/test_multiproc_executor.py)
  * [tests/distributed/test_ray_v2_executor.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/distributed/test_ray_v2_executor.py)
  * [tests/kernels/moe/test_routed_experts_capture_monolithic.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/kernels/moe/test_routed_experts_capture_monolithic.py)
  * [tests/model_executor/model_loader/tensorizer_loader/conftest.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/model_executor/model_loader/tensorizer_loader/conftest.py)
  * [tests/models/transformers/test_backend.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/models/transformers/test_backend.py)
  * [tests/v1/core/test_async_scheduler.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/core/test_async_scheduler.py)
  * [tests/v1/core/test_contiguous_kv_packing.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/core/test_contiguous_kv_packing.py)
  * [tests/v1/core/test_kv_cache_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/core/test_kv_cache_utils.py)
  * [tests/v1/core/test_prefix_caching.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/core/test_prefix_caching.py)
  * [tests/v1/core/test_scheduler.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/core/test_scheduler.py)
  * [tests/v1/core/test_single_type_kv_cache_manager.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/core/test_single_type_kv_cache_manager.py)
  * [tests/v1/core/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/core/utils.py)
  * [tests/v1/engine/test_engine_args.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/engine/test_engine_args.py)
  * [tests/v1/executor/test_executor.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/executor/test_executor.py)
  * [tests/v1/executor/test_ray_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/executor/test_ray_utils.py)
  * [tests/v1/kv_connector/unit/test_output_aggregator.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/kv_connector/unit/test_output_aggregator.py)
  * [tests/v1/kv_connector/unit/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/kv_connector/unit/utils.py)
  * [tests/v1/worker/test_encoder_runner.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/worker/test_encoder_runner.py)
  * [tests/v1/worker/test_gpu_block_table.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/worker/test_gpu_block_table.py)
  * [tests/v1/worker/test_gpu_model_runner.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/worker/test_gpu_model_runner.py)
  * [tests/v1/worker/test_kv_block_zeroer.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/worker/test_kv_block_zeroer.py)
  * [tests/v1/worker/test_prompt_embeds_state.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/worker/test_prompt_embeds_state.py)
  * [vllm/model_executor/models/diffusion_gemma.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/diffusion_gemma.py)
  * [vllm/model_executor/models/longcat_flash_ngram.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/longcat_flash_ngram.py)
  * [vllm/model_executor/warmup/qwen_triton_warmup.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/warmup/qwen_triton_warmup.py)
  * [vllm/utils/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/utils/__init__.py)
  * [vllm/v1/core/block_pool.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/block_pool.py)
  * [vllm/v1/core/kv_cache_coordinator.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/kv_cache_coordinator.py)
  * [vllm/v1/core/kv_cache_manager.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/kv_cache_manager.py)
  * [vllm/v1/core/kv_cache_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/kv_cache_utils.py)
  * [vllm/v1/core/sched/async_scheduler.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/async_scheduler.py)
  * [vllm/v1/core/sched/interface.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/interface.py)
  * [vllm/v1/core/sched/scheduler.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/scheduler.py)
  * [vllm/v1/core/single_type_kv_cache_manager.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/single_type_kv_cache_manager.py)
  * [vllm/v1/executor/abstract.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/abstract.py)
  * [vllm/v1/executor/multiproc_executor.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/multiproc_executor.py)
  * [vllm/v1/executor/ray_executor.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/ray_executor.py)
  * [vllm/v1/executor/ray_executor_v2.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/ray_executor_v2.py)
  * [vllm/v1/executor/ray_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/ray_utils.py)
  * [vllm/v1/executor/uniproc_executor.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/uniproc_executor.py)
  * [vllm/v1/kv_cache_interface.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/kv_cache_interface.py)
  * [vllm/v1/request.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/request.py)
  * [vllm/v1/worker/gpu/attn_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/attn_utils.py)
  * [vllm/v1/worker/gpu/block_table.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/block_table.py)
  * [vllm/v1/worker/gpu/buffer_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/buffer_utils.py)
  * [vllm/v1/worker/gpu/cudagraph_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/cudagraph_utils.py)
  * [vllm/v1/worker/gpu/input_batch.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/input_batch.py)
  * [vllm/v1/worker/gpu/mm/encoder_runner.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/mm/encoder_runner.py)
  * [vllm/v1/worker/gpu/model_runner.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/model_runner.py)
  * [vllm/v1/worker/gpu/model_states/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/model_states/__init__.py)
  * [vllm/v1/worker/gpu/model_states/default.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/model_states/default.py)
  * [vllm/v1/worker/gpu/model_states/encoder_decoder.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/model_states/encoder_decoder.py)
  * [vllm/v1/worker/gpu/model_states/interface.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/model_states/interface.py)
  * [vllm/v1/worker/gpu/spec_decode/eagle/speculator.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/spec_decode/eagle/speculator.py)
  * [vllm/v1/worker/gpu_model_runner.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_model_runner.py)
  * [vllm/v1/worker/gpu_worker.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_worker.py)
  * [vllm/v1/worker/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/utils.py)
  * [vllm/v1/worker/worker_base.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/worker_base.py)

## Purpose and Scope

This document describes the GPU-based model execution subsystem in vLLM, which is responsible for running model forward passes, managing device resources, and coordinating memory allocation for inference. The execution layer sits between the scheduler (which decides what to run) and the model implementations (which define the computation).

**Scope** : This page covers the overall architecture and lifecycle of GPU execution. For detailed information on specific components, see:

  * GPUModelRunner implementation details: [GPUModelRunner](/vllm-project/vllm/4.1-gpumodelrunner)
  * Worker and Executor Architecture: [Worker and Executor Architecture](/vllm-project/vllm/4.2-worker-and-executor-architecture)
  * Request batching and state tracking: [InputBatch and Request State Management](/vllm-project/vllm/4.3-inputbatch-and-request-state-management)
  * Token sampling methods: [Sampling and Token Generation](/vllm-project/vllm/4.4-sampling-and-token-generation)
  * Speculative decoding mechanisms: [Speculative Decoding](/vllm-project/vllm/4.5-speculative-decoding)

* * *

## Architecture Overview

The GPU execution subsystem consists of three primary components that work together to execute model inference: the **Executor** (managing process/actor lifecycle), the **Worker** (managing device/distributed state), and the **ModelRunner** (coordinating the model forward pass).

### GPU Execution Entity Map

The following diagram bridges the natural language concepts of execution to the specific classes and files in the codebase.

**Sources** : [vllm/v1/worker/gpu_worker.py143-158](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_worker.py#L143-L158) [vllm/v1/worker/gpu/model_runner.py158-173](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/model_runner.py#L158-L173) [vllm/v1/worker/gpu/input_batch.py100-110](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/input_batch.py#L100-L110) [vllm/v1/executor/multiproc_executor.py111-116](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/multiproc_executor.py#L111-L116)

* * *

## Worker Lifecycle

The `Worker` class manages the complete lifecycle of GPU resources, from device initialization through model loading and memory profiling.

### Device Initialization

The worker initializes the GPU device and distributed environment before any model operations.

**Key operations in`Worker`**:

  1. **Precision Setup** : Configures `torch.set_float32_matmul_precision` based on the `VLLM_FLOAT32_MATMUL_PRECISION` environment variable [vllm/v1/worker/gpu_worker.py161-162](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_worker.py#L161-L162)
  2. **Distributed Initialization** : Establishes communication groups for Tensor Parallelism (TP) and Pipeline Parallelism (PP) using `ensure_model_parallel_initialized` [vllm/v1/worker/gpu_worker.py23-27](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_worker.py#L23-L27)
  3. **Model Loading** : Loads the model architecture and weights using the configured model loader [vllm/v1/worker/gpu/model_runner.py48-49](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/model_runner.py#L48-L49)

**Sources** : [vllm/v1/worker/gpu_worker.py143-193](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_worker.py#L143-L193) [vllm/v1/worker/gpu/model_runner.py158-183](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/model_runner.py#L158-L183)

### Memory Profiling and CUDA Graphs

After loading the model, the worker profiles available memory to determine the KV cache capacity.

**The profiling process** :

  1. **Profile Run** : Executes dummy forward passes to measure peak activation memory via `memory_profiling` [vllm/v1/worker/gpu_worker.py69](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_worker.py#L69-L69)
  2. **CUDA Graph Dispatch** : `GPUModelRunner` manages optimized execution paths via `ModelCudaGraphManager` [vllm/v1/worker/gpu/cudagraph_utils.py93-96](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/cudagraph_utils.py#L93-L96)
  3. **Static Forward Context** : During graph capture, the runner sets a `forward_context` to provide metadata to layers without CPU overhead [vllm/v1/worker/gpu/model_runner.py38](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/model_runner.py#L38-L38)

**Sources** : [vllm/v1/worker/gpu_worker.py69](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_worker.py#L69-L69) [vllm/v1/worker/gpu/cudagraph_utils.py93-102](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/cudagraph_utils.py#L93-L102) [vllm/v1/worker/gpu/model_runner.py93-96](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/model_runner.py#L93-L96)

* * *

## Model Execution Pipeline

The execution pipeline transforms a `SchedulerOutput` into a `ModelRunnerOutput` through several stages.

### Stage 1: Update States and Input Preparation

The `GPUModelRunner` synchronizes its internal state with the scheduler's decisions.

**Operations** :

  * **Input Batching** : Uses `InputBatch` to manage the lifecycle of requests on the GPU, including `input_ids` and `block_table` buffers [vllm/v1/worker/gpu/input_batch.py100-110](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/input_batch.py#L100-L110)
  * **Request State** : Tracks per-request metadata such as `num_computed_tokens` and `output_token_ids` in `RequestState` [vllm/v1/worker/gpu/states.py12-30](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/states.py#L12-L30)
  * **Buffer Management** : `InputBuffers` maintains pre-allocated GPU tensors for `input_ids`, `positions`, and `slot_mapping` to avoid per-step allocation overhead [vllm/v1/worker/gpu/input_batch.py36-40](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/input_batch.py#L36-L40)

**Sources** : [vllm/v1/worker/gpu/input_batch.py36-110](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/input_batch.py#L36-L110) [vllm/v1/worker/gpu/states.py12-30](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/states.py#L12-L30)

### Stage 2: Execute Model and Sample

The model forward pass is followed by token sampling.

**Execution Flow** :

  1. **Forward Pass** : `GPUModelRunner` coordinates the model's forward execution, handling multi-modal inputs and KV cache updates [vllm/v1/worker/gpu/model_runner.py158-173](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/model_runner.py#L158-L173)
  2. **Sampling** : The `Sampler` applies `SamplingParams` (temperature, top-p, top-k) to select the next token [vllm/v1/worker/gpu/sample/sampler.py129](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/sample/sampler.py#L129-L129)
  3. **Logits Processing** : `LogitsProcessors` modify the distribution before sampling, supporting features like logit bias and frequency penalties [vllm/v1/v1/sample/logits_processor/interface.py192-193](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/v1/sample/logits_processor/interface.py#L192-L193)

**Sources** : [vllm/v1/worker/gpu/model_runner.py124-129](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/model_runner.py#L124-L129) [vllm/v1/worker/gpu/sample/sampler.py129](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/sample/sampler.py#L129-L129) [vllm/v1/worker/gpu/input_batch.py100-107](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/input_batch.py#L100-L107)

* * *

## Memory and KV Cache Management

### Block Table Translation

The `BlockTables` class handles the translation of logical sequence indices to physical GPU memory blocks. It manages `block_table` tensors that are passed to attention kernels [vllm/v1/worker/gpu/block_table.py87](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/block_table.py#L87-L87)

### KV Block Zeroing

Newly allocated KV cache blocks are zeroed out to prevent stale data from interfering with new generations. This is managed by `KVBlockZeroer`, which uses a specialized Triton kernel for high-performance zeroing [vllm/v1/worker/utils.py102-135](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/utils.py#L102-L135)

**Sources** : [vllm/v1/worker/gpu/block_table.py87](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/block_table.py#L87-L87) [vllm/v1/worker/utils.py56-102](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/utils.py#L56-L102)

* * *

## Child Pages

For detailed technical information, please refer to the following child pages:

  * **[GPUModelRunner](/vllm-project/vllm/4.1-gpumodelrunner)** : Deep dive into the `GPUModelRunner` class, coordinating forward passes, KV cache interaction, and Model Runner V2 subcomponents.
  * **[Worker and Executor Architecture](/vllm-project/vllm/4.2-worker-and-executor-architecture)** : Details on `Worker` initialization, device management, and distributed coordination via Ray or Multiprocessing.
  * **[InputBatch and Request State Management](/vllm-project/vllm/4.3-inputbatch-and-request-state-management)** : Detailed explanation of how `InputBatch` and `RequestState` track request data across execution steps.
  * **[Sampling and Token Generation](/vllm-project/vllm/4.4-sampling-and-token-generation)** : Documentation of the sampling pipeline, including `LogitsProcessors` and the `Sampler`.
  * **[Speculative Decoding](/vllm-project/vllm/4.5-speculative-decoding)** : Overview of speculative methods like Eagle, Medusa, and Ngram, and how draft tokens are managed and verified on GPU.
