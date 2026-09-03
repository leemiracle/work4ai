# Overview

> 来源: https://deepwiki.com/vllm-project/vllm/1-overview 抓取日期: 2026-09-02
> 章节: 第 1 章 概述

---

Relevant source files

  * [README.md](https://github.com/vllm-project/vllm/blob/185cada3/README.md?plain=1)
  * [csrc/cpu/spec_decode_utils.cpp](https://github.com/vllm-project/vllm/blob/185cada3/csrc/cpu/spec_decode_utils.cpp)
  * [docker/Dockerfile.xpu](https://github.com/vllm-project/vllm/blob/185cada3/docker/Dockerfile.xpu)
  * [docs/README.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/README.md?plain=1)
  * [docs/community/meetups.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/community/meetups.md?plain=1)
  * [docs/community/sponsors.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/community/sponsors.md?plain=1)
  * [docs/contributing/model/basic.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/contributing/model/basic.md?plain=1)
  * [docs/deployment/docker.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/deployment/docker.md?plain=1)
  * [docs/getting_started/installation/.nav.yml](https://github.com/vllm-project/vllm/blob/185cada3/docs/getting_started/installation/.nav.yml)
  * [docs/getting_started/installation/README.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/getting_started/installation/README.md?plain=1)
  * [docs/getting_started/installation/gpu.apple.inc.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/getting_started/installation/gpu.apple.inc.md?plain=1)
  * [docs/getting_started/installation/gpu.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/getting_started/installation/gpu.md?plain=1)
  * [docs/getting_started/installation/gpu.rocm.inc.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/getting_started/installation/gpu.rocm.inc.md?plain=1)
  * [docs/getting_started/installation/gpu.xpu.inc.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/getting_started/installation/gpu.xpu.inc.md?plain=1)
  * [docs/getting_started/installation/python_env_setup.inc.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/getting_started/installation/python_env_setup.inc.md?plain=1)
  * [docs/getting_started/quickstart.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/getting_started/quickstart.md?plain=1)
  * [docs/models/supported_models.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/models/supported_models.md?plain=1)
  * [requirements/xpu.txt](https://github.com/vllm-project/vllm/blob/185cada3/requirements/xpu.txt)
  * [tests/config/test_config_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/config/test_config_utils.py)
  * [tests/models/multimodal/generation/test_common.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/models/multimodal/generation/test_common.py)
  * [tests/models/multimodal/generation/vlm_utils/model_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/models/multimodal/generation/vlm_utils/model_utils.py)
  * [tests/models/registry.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/models/registry.py)
  * [tests/test_config.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/test_config.py)
  * [tests/v1/core/test_async_scheduler.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/core/test_async_scheduler.py)
  * [tests/v1/core/test_contiguous_kv_packing.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/core/test_contiguous_kv_packing.py)
  * [tests/v1/core/test_kv_cache_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/core/test_kv_cache_utils.py)
  * [tests/v1/core/test_prefix_caching.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/core/test_prefix_caching.py)
  * [tests/v1/core/test_scheduler.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/core/test_scheduler.py)
  * [tests/v1/core/test_single_type_kv_cache_manager.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/core/test_single_type_kv_cache_manager.py)
  * [tests/v1/core/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/core/utils.py)
  * [tests/v1/distributed/test_async_llm_dp.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/distributed/test_async_llm_dp.py)
  * [tests/v1/engine/test_engine_args.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/engine/test_engine_args.py)
  * [tests/v1/engine/test_engine_core_client.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/engine/test_engine_core_client.py)
  * [tests/v1/kv_connector/unit/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/kv_connector/unit/utils.py)
  * [tests/v1/spec_decode/test_eagle.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/spec_decode/test_eagle.py)
  * [tests/v1/spec_decode/test_eagle_step_kernel.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/spec_decode/test_eagle_step_kernel.py)
  * [tests/v1/spec_decode/test_max_len.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/spec_decode/test_max_len.py)
  * [tests/v1/spec_decode/test_mtp.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/spec_decode/test_mtp.py)
  * [tests/v1/worker/test_gpu_model_runner.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/worker/test_gpu_model_runner.py)
  * [tests/v1/worker/test_kv_block_zeroer.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/worker/test_kv_block_zeroer.py)
  * [vllm/config/cache.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/cache.py)
  * [vllm/config/model.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/model.py)
  * [vllm/config/scheduler.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/scheduler.py)
  * [vllm/config/speculative.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/speculative.py)
  * [vllm/config/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/utils.py)
  * [vllm/config/vllm.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/vllm.py)
  * [vllm/engine/arg_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/engine/arg_utils.py)
  * [vllm/engine/protocol.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/engine/protocol.py)
  * [vllm/entrypoints/cli/serve.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/cli/serve.py)
  * [vllm/entrypoints/llm.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/llm.py)
  * [vllm/model_executor/models/config.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/config.py)
  * [vllm/model_executor/models/hunyuan_v1.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/hunyuan_v1.py)
  * [vllm/model_executor/models/hunyuan_vision.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/hunyuan_vision.py)
  * [vllm/model_executor/models/registry.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/registry.py)
  * [vllm/model_executor/warmup/qwen_triton_warmup.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/warmup/qwen_triton_warmup.py)
  * [vllm/transformers_utils/config.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/transformers_utils/config.py)
  * [vllm/transformers_utils/configs/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/transformers_utils/configs/__init__.py)
  * [vllm/transformers_utils/configs/hunyuan_vl.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/transformers_utils/configs/hunyuan_vl.py)
  * [vllm/transformers_utils/model_arch_config_convertor.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/transformers_utils/model_arch_config_convertor.py)
  * [vllm/transformers_utils/processors/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/transformers_utils/processors/__init__.py)
  * [vllm/utils/cpu_triton_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/utils/cpu_triton_utils.py)
  * [vllm/v1/core/block_pool.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/block_pool.py)
  * [vllm/v1/core/kv_cache_coordinator.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/kv_cache_coordinator.py)
  * [vllm/v1/core/kv_cache_manager.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/kv_cache_manager.py)
  * [vllm/v1/core/kv_cache_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/kv_cache_utils.py)
  * [vllm/v1/core/sched/async_scheduler.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/async_scheduler.py)
  * [vllm/v1/core/sched/interface.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/interface.py)
  * [vllm/v1/core/sched/scheduler.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/scheduler.py)
  * [vllm/v1/core/single_type_kv_cache_manager.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/single_type_kv_cache_manager.py)
  * [vllm/v1/engine/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/__init__.py)
  * [vllm/v1/engine/async_llm.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/async_llm.py)
  * [vllm/v1/engine/coordinator.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/coordinator.py)
  * [vllm/v1/engine/core.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py)
  * [vllm/v1/engine/core_client.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core_client.py)
  * [vllm/v1/engine/input_processor.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/input_processor.py)
  * [vllm/v1/engine/llm_engine.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/llm_engine.py)
  * [vllm/v1/engine/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/utils.py)
  * [vllm/v1/kv_cache_interface.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/kv_cache_interface.py)
  * [vllm/v1/request.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/request.py)
  * [vllm/v1/spec_decode/dflash.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/spec_decode/dflash.py)
  * [vllm/v1/spec_decode/draft_model.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/spec_decode/draft_model.py)
  * [vllm/v1/spec_decode/eagle.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/spec_decode/eagle.py)
  * [vllm/v1/spec_decode/llm_base_proposer.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/spec_decode/llm_base_proposer.py)
  * [vllm/v1/spec_decode/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/spec_decode/utils.py)
  * [vllm/v1/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/utils.py)
  * [vllm/v1/worker/cpu/shm.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/cpu/shm.py)
  * [vllm/v1/worker/cpu_model_runner.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/cpu_model_runner.py)
  * [vllm/v1/worker/gpu_model_runner.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_model_runner.py)
  * [vllm/v1/worker/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/utils.py)

This page provides a high-level introduction to vLLM's architecture, core components, and design principles. It serves as an entry point for understanding how vLLM orchestrates large language model inference across multiple hardware platforms with optimized memory management and execution.

vLLM V1 represents a significant re-architecture of the core engine (scheduler, KV cache manager, worker, and sampler) to provide a cohesive, modular, and high-performance framework while retaining the stable model implementations and kernels from V0.

* * *

## What is vLLM

vLLM is a fast and easy-to-use library for LLM inference and serving. It optimizes throughput and memory efficiency through several key technologies:

  * **PagedAttention** : Efficient management of attention key and value memory that eliminates fragmentation.
  * **Continuous Batching** : Dynamic request scheduling and iteration-level batching.
  * **Chunked Prefill** : Processes large prefills in smaller chunks to balance compute and eliminate pipeline bubbles [vllm/v1/engine/core.py153-157](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L153-L157)
  * **Speculative Decoding** : Support for n-gram, suffix, EAGLE, Medusa, and DFlash to accelerate generation [vllm/config/vllm.py49-51](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/vllm.py#L49-L51) [vllm/v1/worker/gpu_model_runner.py197-203](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_model_runner.py#L197-L203)
  * **Multi-platform Support** : Support for NVIDIA GPUs (CUDA), AMD GPUs (ROCm), Intel GPUs (XPU), TPUs (XLA), and CPUs [vllm/platforms/__init__.py28-36](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/__init__.py#L28-L36)
  * **Torch Compilation** : Integration with `torch.compile` and custom Inductor-based backends for kernel fusion and graph optimization [vllm/config/vllm.py31-38](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/vllm.py#L31-L38)

* * *

## System Architecture

vLLM follows a layered architecture with a clear separation of concerns. The V1 engine introduces a decoupled execution model where the `EngineCore` runs in a separate process from the API frontend to minimize CPU overhead and Python GIL contention [vllm/v1/engine/core.py104-113](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L104-L113)

### High-Level System Components

Title: "vLLM System Architecture (Natural Language to Code Entities)"

Sources: [vllm/engine/arg_utils.py35-67](https://github.com/vllm-project/vllm/blob/185cada3/vllm/engine/arg_utils.py#L35-L67) [vllm/config/vllm.py30-53](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/vllm.py#L30-L53) [vllm/config/model.py124-167](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/model.py#L124-L167) [vllm/v1/engine/core.py104-113](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L104-L113) [vllm/v1/core/sched/scheduler.py73-84](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/scheduler.py#L73-L84) [vllm/v1/worker/gpu_model_runner.py280-300](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_model_runner.py#L280-L300) [vllm/v1/kv_cache_interface.py160-173](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/kv_cache_interface.py#L160-L173)

**Layered Architecture Overview**

Layer| Purpose| Key Components  
---|---|---  
**External Interface**|  Entry points for users| `LLM`, `AsyncLLM`, OpenAI API server [vllm/entrypoints/llm.py67](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/llm.py#L67-L67) [vllm/v1/engine/async_llm.py72](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/async_llm.py#L72-L72)  
**Configuration**|  Argument parsing and config assembly| `EngineArgs`, `VllmConfig`, `ModelConfig`, `ParallelConfig` [vllm/engine/arg_utils.py35](https://github.com/vllm-project/vllm/blob/185cada3/vllm/engine/arg_utils.py#L35-L35) [vllm/config/vllm.py124](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/vllm.py#L124-L124)  
**Engine Orchestration**|  Request lifecycle and IPC coordination| `EngineCore`, `InputProcessor` [vllm/v1/engine/core.py104](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L104-L104) [vllm/v1/engine/input_processor.py20](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/input_processor.py#L20-L20)  
**Scheduling & Memory**| Resource allocation and KV management| `Scheduler`, `KVCacheManager`, `BlockPool` [vllm/v1/core/sched/scheduler.py73](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/scheduler.py#L73-L73) [vllm/v1/core/kv_cache_manager.py25](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/kv_cache_manager.py#L25-L25)  
**Execution**|  Model forward passes on hardware| `Executor`, `GPUModelRunner`, `Sampler` [vllm/v1/worker/gpu_model_runner.py280](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_model_runner.py#L280-L280) [vllm/v1/sample/sampler.py25](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/sample/sampler.py#L25-L25)  
  
Sources: [vllm/v1/engine/core.py104-169](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L104-L169) [vllm/engine/arg_utils.py35-120](https://github.com/vllm-project/vllm/blob/185cada3/vllm/engine/arg_utils.py#L35-L120) [vllm/config/vllm.py124-213](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/vllm.py#L124-L213) [vllm/v1/core/sched/scheduler.py73-106](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/scheduler.py#L73-L106)

* * *

## Core Components

### EngineCore: The Central Serving Loop

`EngineCore` is the high-performance inner loop of vLLM. It manages the `SchedulerInterface` and the `Executor` [vllm/v1/engine/core.py104-133](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L104-L133) It initializes specialized configurations and hardware-specific optimizations.

**Key responsibilities:**

  * **Initialization** : Profiles GPU memory, initializes KV caches via `_initialize_kv_caches`, and sets up the model executor and scheduler [vllm/v1/engine/core.py133-169](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L133-L169)
  * **Request Handling** : Processes `EngineCoreRequest` objects containing prompt token IDs, multimodal features, and sampling parameters [vllm/v1/engine/core.py64-67](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L64-L67)
  * **Iteration Loop** : Orchestrates the model forward pass and output collection via `step()` [vllm/v1/engine/core.py326-340](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L326-L340)
  * **Structured Output** : Manages guided decoding and structured grammars via `StructuredOutputManager` [vllm/v1/engine/core.py146](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L146-L146)

Sources: [vllm/v1/engine/core.py104-194](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L104-L194)

### Model Registry and Support

vLLM supports a wide array of architectures through a native registry that maps HuggingFace `model_type` to optimized vLLM implementations [vllm/model_executor/models/registry.py72-164](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/registry.py#L72-L164)

  * **Native vLLM Models** : Highly optimized implementations using custom kernels (e.g., `LlamaForCausalLM`, `DeepseekV3ForCausalLM`) [vllm/model_executor/models/registry.py92-153](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/registry.py#L92-L153)
  * **Transformers Backend** : Fallback for models without native support, enabling compatibility with any HF-compatible model [docs/models/supported_models.md16-18](https://github.com/vllm-project/vllm/blob/185cada3/docs/models/supported_models.md?plain=1#L16-L18)
  * **Multimodal Support** : Interfaces for vision-language and audio models (e.g., `Qwen2VL`, `HunyuanVision`) [docs/models/supported_models.md22](https://github.com/vllm-project/vllm/blob/185cada3/docs/models/supported_models.md?plain=1#L22-L22) [vllm/model_executor/models/hunyuan_vision.py20](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/hunyuan_vision.py#L20-L20)

Sources: [vllm/model_executor/models/registry.py72-164](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/registry.py#L72-L164) [docs/models/supported_models.md9-70](https://github.com/vllm-project/vllm/blob/185cada3/docs/models/supported_models.md?plain=1#L9-L70)

* * *

## Request Processing Flow

The flow below demonstrates how a user request traverses the system from a high-level API call to GPU execution.

Title: "vLLM V1 Request Lifecycle (Code Entity Space)"

Sources: [vllm/v1/engine/core.py161-169](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L161-L169) [vllm/v1/engine/core.py326-340](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L326-L340) [vllm/v1/core/sched/scheduler.py73-106](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/scheduler.py#L73-L106) [vllm/v1/worker/gpu_model_runner.py280-300](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_model_runner.py#L280-L300)

* * *

## Optimization and Serving Modes

vLLM V1 is designed for extreme scale and performance:

  * **Distributed Execution** : Supports Tensor, Pipeline, and Data Parallelism configured via `ParallelConfig` [vllm/config/parallel.py98-104](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/parallel.py#L98-L104)
  * **Compilation & CUDA Graphs**: Support for `torch.compile` and CUDA graph capture modes (`CUDAGraphMode`) to minimize kernel launch overhead [vllm/config/compilation.py32-33](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/compilation.py#L32-L33)
  * **Optimization Levels** : Pre-defined levels (O0-O3) that automatically configure compilation, CUDA graphs, and fusion passes [vllm/config/vllm.py130-143](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/vllm.py#L130-L143)
  * **Prefix Caching** : Automatic prefix caching to reuse KV cache for common prompt prefixes [vllm/config/cache.py76-81](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/cache.py#L76-L81)
  * **Quantization** : Support for FP8, AWQ, GPTQ, and other low-precision formats to reduce memory footprint [vllm/engine/arg_utils.py98-104](https://github.com/vllm-project/vllm/blob/185cada3/vllm/engine/arg_utils.py#L98-L104) [vllm/config/model.py25](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/model.py#L25-L25)

Sources: [vllm/config/vllm.py130-143](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/vllm.py#L130-L143) [vllm/config/compilation.py31-38](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/compilation.py#L31-L38) [vllm/config/parallel.py98-105](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/parallel.py#L98-L105) [vllm/config/cache.py70-81](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/cache.py#L70-L81)
