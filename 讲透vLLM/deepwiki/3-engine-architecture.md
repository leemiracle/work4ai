# Engine Architecture

> 来源: https://deepwiki.com/vllm-project/vllm/3-engine-architecture 抓取日期: 2026-09-02
> 章节: 第 3 章 引擎架构

---

Relevant source files

  * [tests/config/test_config_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/config/test_config_utils.py)
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
  * [tests/v1/worker/test_gpu_model_runner.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/worker/test_gpu_model_runner.py)
  * [tests/v1/worker/test_kv_block_zeroer.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/worker/test_kv_block_zeroer.py)
  * [vllm/engine/protocol.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/engine/protocol.py)
  * [vllm/entrypoints/cli/serve.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/cli/serve.py)
  * [vllm/entrypoints/llm.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/llm.py)
  * [vllm/model_executor/warmup/qwen_triton_warmup.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/warmup/qwen_triton_warmup.py)
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
  * [vllm/v1/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/utils.py)
  * [vllm/v1/worker/gpu_model_runner.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_model_runner.py)
  * [vllm/v1/worker/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/utils.py)

This page describes the overall architecture of the vLLM v1 inference engine: its layered components, how they communicate, and how a request flows from API submission through GPU execution and back to the caller. Detailed documentation for each component is provided in the child pages listed below.

For configuration of these components at startup, see [Configuration and Initialization](/vllm-project/vllm/2-configuration-and-initialization). For details on how model inference is executed on the GPU, see [Model Execution on GPU](/vllm-project/vllm/4-model-execution-on-gpu). For the HTTP serving layer built on top of this engine, see [Serving APIs](/vllm-project/vllm/6-serving-apis).

* * *

## Overview

vLLM's v1 engine is organized into a multi-process, multi-layer architecture designed for high-throughput inference serving. The engine consists of:

Layer| Purpose| Key Classes| Detailed Coverage  
---|---|---|---  
**Client API**|  Accept and return requests| `LLM`, `AsyncLLM`, `EngineCoreClient`| [EngineCore and Client APIs](/vllm-project/vllm/3.1-enginecore-and-client-apis)  
**Engine Core**|  Schedule, execute, coordinate| `EngineCore`, `EngineCoreProc`, `EngineCoreClient`| [EngineCore and Client APIs](/vllm-project/vllm/3.1-enginecore-and-client-apis)  
**Request Management**|  Track request lifecycle and state| `Request`, `RequestStatus`, `EngineCoreRequest`| [Request Lifecycle and State Management](/vllm-project/vllm/3.2-request-lifecycle-and-state-management)  
**Scheduler**|  Batch requests, allocate resources| `Scheduler`, `RequestQueue`| [Scheduler and Resource Allocation](/vllm-project/vllm/3.3-scheduler-and-resource-allocation)  
**KV Cache**|  Manage GPU memory for KV cache| `KVCacheManager`, `BlockPool`, `SingleTypeKVCacheManager`| [KV Cache Management and Prefix Caching](/vllm-project/vllm/3.4-kv-cache-management-and-prefix-caching)  
**I/O Processing**|  Tokenization, detokenization| `InputProcessor`, `OutputProcessor`| [Input and Output Processing](/vllm-project/vllm/3.5-input-and-output-processing)  
**Observability**|  Metrics, logging, monitoring| `SchedulerStats`, `KVCacheMetricsCollector`| [Metrics and Observability](/vllm-project/vllm/3.6-metrics-and-observability)  
  
### Process Architecture

The v1 engine uses a **process-split architecture** where the client-facing layer and the GPU execution loop run in separate processes, communicating via ZMQ sockets. This design enables isolation of GPU work from HTTP/API handling and asynchronous pipelining of requests.

**High-level architecture diagram:**

Title: vLLM V1 Process Architecture

**Alternative in-process mode** : When using `InprocClient`, `EngineCore` runs directly in the client process without separate processes or ZMQ communication. This is simpler but less scalable.

Sources: [vllm/v1/engine/core.py105-170](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L105-L170) [vllm/v1/engine/core_client.py78-112](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core_client.py#L78-L112) [vllm/v1/engine/utils.py179-196](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/utils.py#L179-L196) [vllm/v1/engine/async_llm.py149-156](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/async_llm.py#L149-L156)

* * *

## Client API Layer

There are two main entry points into the engine:

### `LLM` — Synchronous Offline Inference

`LLM` is intended for offline batch inference. It drives the engine loop synchronously, wrapping the engine logic to process a fixed set of prompts [vllm/entrypoints/llm.py67-75](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/llm.py#L67-L75)

### `AsyncLLM` — Asynchronous Online Serving

`AsyncLLM` is the engine used by the HTTP server. It is asyncio-native and designed for concurrent request handling [vllm/v1/engine/async_llm.py72-89](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/async_llm.py#L72-L89)

  * It creates an `EngineCoreClient` (specifically `AsyncMPClient`) that communicates with `EngineCoreProc` in a background process via ZMQ [vllm/v1/engine/async_llm.py149-156](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/async_llm.py#L149-L156)
  * It pulls `EngineCoreOutputs` from the engine core and routes them to the appropriate request streams via the `OutputProcessor` [vllm/v1/engine/async_llm.py141-146](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/async_llm.py#L141-L146)

### `EngineCoreClient` Abstraction

`EngineCoreClient` provides a unified interface for the frontend to interact with the backend [vllm/v1/engine/core_client.py78-87](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core_client.py#L78-L87)

  * `SyncMPClient`: ZMQ communication for synchronous callers [vllm/v1/engine/core_client.py109-110](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core_client.py#L109-L110)
  * `AsyncMPClient`: ZMQ asyncio sockets for high-concurrency serving [vllm/v1/engine/core_client.py116-139](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core_client.py#L116-L139)

Sources: [vllm/v1/engine/core_client.py78-139](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core_client.py#L78-L139) [vllm/v1/engine/utils.py144-172](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/utils.py#L144-L172) [vllm/v1/engine/async_llm.py149-156](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/async_llm.py#L149-L156)

* * *

## Engine Core Layer

### `EngineCore`

`EngineCore` is the inner execution loop [vllm/v1/engine/core.py105-106](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L105-L106) It is responsible for initializing the `Executor`, profiling GPU memory for the KV cache, and running the core iteration loop.

Key components initialized in `EngineCore`:

  * `model_executor`: The hardware abstraction (e.g., `Executor`) for model forward passes [vllm/v1/engine/core.py134-138](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L134-L138)
  * `scheduler`: The core logic for request batching and memory allocation [vllm/v1/engine/core.py162-170](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L162-L170)
  * `structured_output_manager`: Manages constrained decoding (e.g., JSON mode) [vllm/v1/engine/core.py146](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L146-L146)

### `EngineCoreProc`

`EngineCoreProc` is a wrapper used to run `EngineCore` in a background process [vllm/v1/engine/utils.py179](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/utils.py#L179-L179) It handles process initialization and exposes the engine over ZMQ sockets using `MsgpackEncoder`/`MsgpackDecoder` [vllm/v1/v1/serial_utils.py91-92](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/v1/serial_utils.py#L91-L92)

**Class relationship diagram:**

Title: Engine Client and Core Entities

Sources: [vllm/v1/engine/core.py105-170](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L105-L170) [vllm/v1/engine/core_client.py78-112](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core_client.py#L78-L112) [vllm/v1/engine/utils.py144-196](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/utils.py#L144-L196)

* * *

## Scheduler and KV Cache Layer

### `Scheduler`

`Scheduler` manages request queues and KV cache allocation [vllm/v1/core/sched/scheduler.py73-84](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/scheduler.py#L73-L84) It maintains priority queues for `waiting` and `running` requests [vllm/v1/core/sched/scheduler.py49-53](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/scheduler.py#L49-L53) The `schedule()` method produces a `SchedulerOutput` specifying token budgets and KV block assignments [vllm/v1/core/sched/output.py47-48](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/output.py#L47-L48)

For details, see [Scheduler and Resource Allocation](/vllm-project/vllm/3.3-scheduler-and-resource-allocation).

### `KVCacheManager`

`KVCacheManager` manages physical GPU blocks [vllm/v1/core/kv_cache_manager.py118-135](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/kv_cache_manager.py#L118-L135) It coordinates multiple `SingleTypeKVCacheManager` instances [vllm/v1/core/single_type_kv_cache_manager.py36-55](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/single_type_kv_cache_manager.py#L36-L55) It uses a `BlockPool` for raw block accounting and prefix caching [vllm/v1/core/block_pool.py15](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/block_pool.py#L15-L15)

For details, see [KV Cache Management and Prefix Caching](/vllm-project/vllm/3.4-kv-cache-management-and-prefix-caching).

**Scheduler and KV Cache data flow:**

Title: Scheduling and Resource Allocation Flow

Sources: [vllm/v1/core/sched/scheduler.py73-170](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/scheduler.py#L73-L170) [vllm/v1/core/kv_cache_manager.py118-166](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/kv_cache_manager.py#L118-L166) [vllm/v1/core/single_type_kv_cache_manager.py36-55](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/single_type_kv_cache_manager.py#L36-L55)

* * *

## Request Lifecycle

### `Request` and `RequestStatus`

`Request` is the internal state container [vllm/v1/request.py64-65](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/request.py#L64-L65) It tracks generated tokens, computed token counts, and KV block hashes. Its lifecycle is managed via `RequestStatus`, transitioning from `WAITING` to `RUNNING` and eventually `FINISHED_STOPPED` or other terminal states [vllm/v1/request.py27-41](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/request.py#L27-L41)

For details, see [Request Lifecycle and State Management](/vllm-project/vllm/3.2-request-lifecycle-and-state-management).

### End-to-End Request Flow

  1. **Submission** : The frontend sends an `EngineCoreRequest` to the core via the `EngineCoreClient` [vllm/v1/engine/core_client.py82](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core_client.py#L82-L82)
  2. **Scheduling** : `Scheduler` moves the request to `RUNNING` and allocates KV blocks [vllm/v1/core/sched/scheduler.py73](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/scheduler.py#L73-L73)
  3. **Execution** : `Executor` runs the model on GPUs, using the allocated blocks [vllm/v1/executor/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/__init__.py)
  4. **Output** : `EngineCore` collects `ModelRunnerOutput` and produces `EngineCoreOutputs` to be sent back to the client [vllm/v1/engine/core.py64-65](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L64-L65)

Sources: [vllm/v1/request.py27-64](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/request.py#L27-L64) [vllm/v1/engine/core.py55-74](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L55-L74) [vllm/v1/core/sched/scheduler.py73-170](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/scheduler.py#L73-L170)

* * *

## Process Architecture and Communication

The engine utilizes ZMQ for inter-process communication when multiprocess mode is enabled [vllm/v1/engine/core.py21](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L21-L21)

Communication is optimized using:

  * **`MsgpackEncoder`** : Efficient binary serialization for ZMQ transport [vllm/v1/serial_utils.py91-92](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/serial_utils.py#L91-L92)
  * **Handshake** : `EngineHandshakeMetadata` coordinates ZMQ addresses and parallel configuration between the client and engine processes during startup [vllm/v1/engine/utils.py102-110](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/utils.py#L102-L110)
  * **Tensor IPC** : `TensorIpcReceiver` facilitates high-performance tensor data transfer between processes [vllm/v1/engine/core.py75](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L75-L75)

Sources: [vllm/v1/engine/core.py92](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L92-L92) [vllm/v1/engine/utils.py86-110](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/utils.py#L86-L110) [vllm/v1/engine/core_client.py78-139](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core_client.py#L78-L139)

* * *

## Supporting Subsystems

Inside `EngineCore`, several subsystems support the scheduling and execution pipeline:

Component| Class| Purpose  
---|---|---  
**Structured Output**| `StructuredOutputManager`| Manages grammars and bitmasks for guided decoding [vllm/v1/structured_output.py67](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/structured_output.py#L67-L67)  
**Multimodal Receiver**| `mm_receiver_cache`| Manages multimodal input data receiving and caching [vllm/v1/engine/core.py181-183](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L181-L183)  
**KV Transfer**| `KVConnectorFactory`| Handles KV cache migration for disaggregated or distributed serving [vllm/v1/core/sched/scheduler.py149-153](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/scheduler.py#L149-L153)  
  
For details on metrics and observability, see [Metrics and Observability](/vllm-project/vllm/3.6-metrics-and-observability).

Sources: [vllm/v1/engine/core.py146-183](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L146-L183) [vllm/v1/core/sched/scheduler.py134-153](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/scheduler.py#L134-L153)
