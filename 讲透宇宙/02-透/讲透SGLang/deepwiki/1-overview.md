> 来源: [https://deepwiki.com/sgl-project/sglang/1-overview](https://deepwiki.com/sgl-project/sglang/1-overview)
> DeepWiki sgl-project/sglang | Last indexed: 27 Aug 2026 (94183a)

# Overview

  Relevant source files 
 - [3rdparty/amd/wheel/sglang/pyproject.toml](https://github.com/sgl-project/sglang/blob/94183a8d/3rdparty/amd/wheel/sglang/pyproject.toml)
 - [benchmark/deepseek_v3/README.md](https://github.com/sgl-project/sglang/blob/94183a8d/benchmark/deepseek_v3/README.md?plain=1)
 - [docker/Dockerfile](https://github.com/sgl-project/sglang/blob/94183a8d/docker/Dockerfile)
 - [docker/xeon.Dockerfile](https://github.com/sgl-project/sglang/blob/94183a8d/docker/xeon.Dockerfile)
 - [python/pyproject.toml](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject.toml)
 - [python/pyproject_cpu.toml](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject_cpu.toml)
 - [python/pyproject_npu.toml](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject_npu.toml)
 - [python/pyproject_other.toml](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject_other.toml)
 - [python/pyproject_xpu.toml](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject_xpu.toml)
 - [python/sglang/srt/entrypoints/engine.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py)
 - [python/sglang/srt/entrypoints/http_server.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/http_server.py)
 - [python/sglang/srt/environ.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/environ.py)
 - [python/sglang/srt/managers/data_parallel_controller.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/data_parallel_controller.py)
 - [python/sglang/srt/managers/detokenizer_manager.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/detokenizer_manager.py)
 - [python/sglang/srt/managers/io_struct.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/io_struct.py)
 - [python/sglang/srt/managers/multi_tokenizer_mixin.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/multi_tokenizer_mixin.py)
 - [python/sglang/srt/managers/schedule_batch.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py)
 - [python/sglang/srt/managers/scheduler.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py)
 - [python/sglang/srt/managers/tokenizer_manager.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py)
 - [python/sglang/srt/managers/tp_worker.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tp_worker.py)
 - [python/sglang/srt/mem_cache/common.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/common.py)
 - [python/sglang/srt/model_executor/model_runner.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py)
 - [python/sglang/srt/server_args.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py)
 - [python/sglang/srt/utils/common.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/common.py)
 - [python/sglang/version.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/version.py)
 - [scripts/ci/cuda/ci_download_flashinfer_jit_cache.sh](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/cuda/ci_download_flashinfer_jit_cache.sh)
 - [scripts/ci/cuda/ci_install_dependency.sh](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/cuda/ci_install_dependency.sh)
 - [scripts/ci/utils/install_protoc.sh](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/utils/install_protoc.sh)
 - [scripts/ci/utils/install_rust_protoc.sh](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/utils/install_rust_protoc.sh)
 - [scripts/ci/utils/install_rustup.sh](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/utils/install_rustup.sh)
 - [sgl-model-gateway/rust-toolchain.toml](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/rust-toolchain.toml)
 - [test/registered/unit/tools/test_get_version_tag.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/tools/test_get_version_tag.py)
 
  
## Introduction

 SGLang is a high-performance serving framework for large language models (LLMs) and vision-language models (VLMs), optimized for low-latency and high-throughput inference. It offers a full-featured runtime environment integrating advanced capabilities such as automatic prefix caching (RadixAttention), hierarchical multi-tier memory management (HiCache), adaptive speculative decoding (EAGLE), and comprehensive parallelism across tensor, pipeline, expert, and data-parallel dimensions.

 **Purpose:** SGLang is designed both as a production-grade inference engine and as a flexible research platform for optimizing serving of LLMs and VLMs. It supports user interaction via OpenAI-compatible HTTP APIs, gRPC interfaces, and a native Python API for tight integration or experimentation [python/pyproject.toml5-10](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject.toml#L5-L10) [python/sglang/srt/entrypoints/engine.py14-18](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L14-L18)

 **Scope:** This overview provides a high-level architectural introduction covering SGLang's modular components and the request lifecycle. Detailed internals and usage scenarios are documented in child pages.

 Key highlights include:

 
 - **Fast Runtime Execution:** Zero-overhead CPU scheduling with continuous batching, support for prefill-decode disaggregation, and efficient multi-token streaming [python/pyproject.toml5-10](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject.toml#L5-L10)
 - **Wide Model Compatibility:** Supports many model families, including LLaMA, Qwen, DeepSeek (V3/R1/V4 with MLA and DSA support), Mistral, and multimodal models such as LLaVA and Qwen-VL [python/sglang/srt/server_args.py193-220](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L193-L220) [python/sglang/srt/configs/model_config.py106-141](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/configs/model_config.py#L106-L141)
 - **Multi-Platform Hardware Support:** Runs on NVIDIA Hopper/Blackwell GPUs, AMD MI300 via ROCm, Intel CPUs with AMX, as well as Ascend NPUs and other accelerators [python/sglang/srt/server_args.py61-91](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L61-L91) [python/sglang/srt/utils/common.py127-226](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/common.py#L127-L226)
 
 
---

 
## System Architecture

 The design separates components into cooperating processes to maximize concurrency, avoid Python GIL bottlenecks, and isolate concerns such as tokenization, model execution, and scheduling. Communication between components is implemented over ZeroMQ (ZMQ) IPC channels with asynchronous I/O used where appropriate.

 
### Process Architecture

 The system consists of the following primary processes:

 
 - **Engine:** The main orchestrator launching and managing subprocesses. Provides user-facing APIs and manages lifecycle [python/sglang/srt/entrypoints/engine.py199-210](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L199-L210)
 - **TokenizerManager:** Responsible for text and multimodal input tokenization, batching requests, and forwarding tokenized requests to the scheduler [python/sglang/srt/managers/tokenizer_manager.py14-15](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L14-L15)
 - **Scheduler:** Handles request batching, scheduling policy decisions, GPU memory management, and invokes model forward passes. It also manages distributed parallelism and disaggregation features [python/sglang/srt/managers/scheduler.py14](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L14-L14)
 - **ModelRunner:** Executes forward passes of models on GPU or other hardware backends, supporting multi-mode forward passes and CUDA graph optimization [python/sglang/srt/model_executor/model_runner.py14](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L14-L14)
 - **DetokenizerManager:** Converts output token IDs back into human-readable strings [python/sglang/srt/entrypoints/engine.py64](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L64-L64)
 - **DataParallelController:** Coordinates distributed execution and parallelism control across nodes and devices [python/sglang/srt/entrypoints/engine.py60-63](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L60-L63)
 
 
```

```

 **Design Features:**

 
 - **Isolation for Efficiency:** CPU-bound operations such as tokenization and scheduling run in separate processes to avoid GIL contention, while the Scheduler houses GPU-bound execution alongside the ModelRunner [python/sglang/srt/entrypoints/engine.py199-210](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L199-L210) [python/sglang/srt/managers/tokenizer_manager.py14](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L14-L14) [python/sglang/srt/managers/scheduler.py14](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L14-L14)
 - **Lightweight IPC:** ZeroMQ is used extensively between processes to efficiently pass messages and batch data [python/sglang/srt/managers/tokenizer_manager.py44-46](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L44-L46) [python/sglang/srt/utils/network.py149](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/network.py#L149-L149)
 - **Asynchronous Networking:** TokenizerManager leverages `asyncio` and high-performance `uvloop` to handle many simultaneous client requests and forward them promptly to the scheduler [python/sglang/srt/managers/tokenizer_manager.py43-46](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L43-L46) [python/sglang/srt/managers/tokenizer_manager.py154](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L154-L154)
 
 Sources: [python/sglang/srt/entrypoints/engine.py199-210](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L199-L210) [python/sglang/srt/managers/tokenizer_manager.py14-154](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L14-L154) [python/sglang/srt/managers/scheduler.py14](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L14-L14) [python/sglang/srt/model_executor/model_runner.py14](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L14-L14)

 
---

 
### Data Flow and Request Lifecycle

 Requests progress through the system via a staged pipeline with increasing refinement from raw text to batched GPU execution and back to human-readable output. This pipeline enables optimizations like prefix caching, continuous batching, and streaming.

 
```

```

 Key data structures:

 
 - **ScheduleBatch:** Represents a scheduled batch managed by the Scheduler, containing request metadata and batching information. Mostly CPU-based data [python/sglang/srt/managers/schedule_batch.py41-42](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L41-L42)
 - **ForwardBatch:** Represents GPU tensors for a batch constructed from ScheduleBatch, used by ModelRunner for inference [python/sglang/srt/managers/schedule_batch.py43-46](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L43-L46) [python/sglang/srt/model_executor/forward_batch_info.py98](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/forward_batch_info.py#L98-L98)
 
 This pipeline architecture efficiently reuses prefixes, facilitates multi-turn conversations, and supports streaming incremental outputs.

 Sources: [python/sglang/srt/managers/schedule_batch.py25-46](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L25-L46) [python/sglang/srt/managers/tokenizer_manager.py57-82](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L57-L82) [python/sglang/srt/model_executor/model_runner.py98-100](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L98-L100) [python/sglang/srt/managers/io_struct.py160-182](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/io_struct.py#L160-L182)

 
---

 
## Core Components

 
### Engine

 The `Engine` class is the primary runtime entry point implemented in `python/sglang/srt/entrypoints/engine.py`. It is responsible for:

 
 - Launching and managing the lifecycle of subprocesses including the TokenizerManager, Scheduler, and DetokenizerManager [python/sglang/srt/entrypoints/engine.py199-210](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L199-L210)
 - Exposing synchronous and asynchronous APIs for text generation and embedding queries.
 - Orchestrating startup, shutdown, and error recovery logistics.
 
 This component acts as the centralized interface for clients and external systems interacting with SGLang.

 For in-depth discussion of repository structure and entrypoints, see [Repository Layout, Major Packages, and Entry Points](https://deepwiki.com/sgl-project/sglang/1.1-repository-layout-major-packages-and-entry-points).

 Sources: [python/sglang/srt/entrypoints/engine.py199-210](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L199-L210)

 
---

 
### TokenizerManager

 Implemented in `python/sglang/srt/managers/tokenizer_manager.py`, the TokenizerManager handles:

 
 - Conversion of raw text and multimodal inputs into tokens suitable for model consumption.
 - Request bookkeeping and asynchronous batching management.
 - Integration with multimodal feature extractors and processors supporting images, video, audio, etc.
 - Asynchronous networking via ZeroMQ and the uvloop event loop to efficiently handle high request loads.
 
 It transforms user-facing inputs into token sequences and multimodal feature arrays, forwarding these to the Scheduler for further processing.

 Sources: [python/sglang/srt/managers/tokenizer_manager.py14-212](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L14-L212)

 
---

 
### Scheduler

 The Scheduler is the core scheduling process defined in `python/sglang/srt/managers/scheduler.py`. Its responsibilities include:

 
 - Managing GPU memory budgeting and scheduling policy decisions.
 - Forming batches (`ScheduleBatch`) from incoming tokenized requests.
 - Invoking the `ModelRunner` to perform actual model forward computations.
 - Handling multi-dimensional parallelism, including tensor parallelism (TP), pipeline parallelism (PP), expert parallelism (EP), and data parallelism (DP).
 - Overseeing disaggregation techniques to support prefill-decode separation and large-scale distributed inference.
 - Allocating and managing KV cache slots and memory pools.
 
 The Scheduler ensures efficient utilization of hardware resources and orchestrates the flow of inference computations.

 For conceptual dataflow and runtime roles, see [Core Concepts and Dataflow (Tokenizer → Scheduler → ModelRunner → Detokenizer)](https://deepwiki.com/sgl-project/sglang/1.2-core-concepts-and-dataflow-(tokenizer-scheduler-modelrunner-detokenizer)).

 Sources: [python/sglang/srt/managers/scheduler.py14-100](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L14-L100) [python/sglang/srt/managers/schedule_batch.py193-198](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L193-L198)

 
---

 
### ModelRunner

 `ModelRunner` executes the model inference forward passes on GPU or other hardware backends. Located in `python/sglang/srt/model_executor/model_runner.py`, it supports:

 
 - Multiple forward pass modes: prefill, decode, extend, and mixed modes.
 - Recording and managing CUDA graphs (capture and replay) for low-overhead repeated inference calls.
 - Managing per-model memory pools, KV cache layouts, and quantization-aware forward execution.
 - Integrating specialized backends for MoE layers, quantization kernels, and different attention mechanisms.
 
 The ModelRunner serves as the low-level execution engine of SGLang, running inference on the loaded large models.

 Sources: [python/sglang/srt/model_executor/model_runner.py14-165](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L14-L165) [python/sglang/srt/model_executor/forward_batch_info.py111](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/forward_batch_info.py#L111-L111)

 
---

 
## Memory and Cache System

 SGLang uses a hierarchical and prefix-aware memory and cache system to optimize computation reuse and memory efficiency:

 
| Memory/Caching Component | Role | Code Reference |
|---|---|---|
| ReqToTokenPool | Maps inference requests to allocated token positions in the KV cache. | python/sglang/srt/model_executor/model_runner.py93 |
| BaseTokenToKVPoolAllocator | Basis for allocating KV slots and indices in token pools. | python/sglang/srt/model_executor/model_runner.py89 |
| RadixCache | Tree-structured prefix cache facilitating automatic prefix reuse and attention caching. | python/sglang/srt/managers/schedule_batch.py96-100 |
| ScheduleBatch | Contains the metadata and allocation information of a batched request schedule. | python/sglang/srt/managers/schedule_batch.py193-198 |

 This system supports the HiCache multi-tier persistent cache model (device, host, and storage tiers) and integrates with attention kernel optimizations via chunking and prefix reuse.

 Sources: [python/sglang/srt/model_executor/model_runner.py88-93](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L88-L93) [python/sglang/srt/managers/schedule_batch.py96-107](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L96-L107) [python/sglang/srt/managers/schedule_batch.py193-198](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L193-L198)

 
---

 
## Key Features

 
 - **Multi-Dimensional Parallelism:** SGLang supports tensor parallelism (TP), pipeline parallelism (PP), expert parallelism (EP), and data parallelism (DP) to efficiently scale large models across hardware resources [python/sglang/srt/server_args.py46-86](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L46-L86) [python/sglang/srt/model_executor/model_runner.py40-75](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L40-L75)
 - **Advanced Quantization Support:** Includes multiple quantization schemes such as fp8 (E4M3), mxfp8, AWQ, GPTQ, Marlin, nvfp4_online, and others for storage and execution efficiency [python/sglang/srt/server_args.py141-177](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L141-L177)
 - **Speculative Decoding:** Implements advanced algorithms like EAGLE and N-gram-based adaptive speculative decoding to improve generation latency [python/sglang/srt/model_executor/model_runner.py149-158](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L149-L158)
 - **Structured and Constrained Output:** Supports grammar constraints, JSON schema enforcement, and structured generation via integrations with `xgrammar`, `outlines`, and `llguidance` [python/pyproject.toml42-91](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject.toml#L42-L91)
 
 
---

 This page presents a high-level architectural overview of SGLang, highlighting its modular multi-process design, request dataflow from tokenization through scheduling to model execution and output detokenization, core runtime components, and key system features essential for fast and scalable serving of LLMs and VLMs. For detailed coverage of repository layout, core concepts, deployment, and advanced internals, refer to the child pages below:

 
 - [Repository Layout, Major Packages, and Entry Points](https://deepwiki.com/sgl-project/sglang/1.1-repository-layout-major-packages-and-entry-points)
 - [Core Concepts and Dataflow (Tokenizer → Scheduler → ModelRunner → Detokenizer)](https://deepwiki.com/sgl-project/sglang/1.2-core-concepts-and-dataflow-(tokenizer-scheduler-modelrunner-detokenizer))
 
 
---

 Sources:

 
 - [python/pyproject.toml5-10](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject.toml#L5-L10)
 - [python/sglang/srt/entrypoints/engine.py14-210](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L14-L210)
 - [python/sglang/srt/server_args.py61-220](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L61-L220)
 - [python/sglang/srt/configs/model_config.py106-141](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/configs/model_config.py#L106-L141)
 - [python/sglang/srt/utils/common.py127-226](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/common.py#L127-L226)
 - [python/sglang/srt/managers/tokenizer_manager.py14-154](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L14-L154)
 - [python/sglang/srt/managers/scheduler.py14-100](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L14-L100)
 - [python/sglang/srt/managers/schedule_batch.py25-198](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L25-L198)
 - [python/sglang/srt/model_executor/model_runner.py14-165](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L14-L165)
 - [python/sglang/srt/managers/io_struct.py160-182](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/io_struct.py#L160-L182)
