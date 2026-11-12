<!-- source: DeepWiki mcp.deepwiki.com · repo lightseekorg/tokenspeed · page 2 Python Runtime · fetched 2026-10-21 -->

# Python Runtime

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [python/tokenspeed/runtime/engine/event_loop.py](python/tokenspeed/runtime/engine/event_loop.py)
- [python/tokenspeed/runtime/engine/scheduler_utils.py](python/tokenspeed/runtime/engine/scheduler_utils.py)
- [python/tokenspeed/runtime/execution/model_executor.py](python/tokenspeed/runtime/execution/model_executor.py)
- [python/tokenspeed/runtime/layers/attention/deepseek_v4_ops.py](python/tokenspeed/runtime/layers/attention/deepseek_v4_ops.py)
- [python/tokenspeed/runtime/models/deepseek_v4.py](python/tokenspeed/runtime/models/deepseek_v4.py)
- [python/tokenspeed/runtime/utils/env.py](python/tokenspeed/runtime/utils/env.py)
- [test/runtime/test_aligned_max_scheduled_tokens.py](test/runtime/test_aligned_max_scheduled_tokens.py)
- [test/runtime/test_deepseek_v4_config.py](test/runtime/test_deepseek_v4_config.py)
- [tokenspeed-scheduler/CMakeLists.txt](tokenspeed-scheduler/CMakeLists.txt)
- [tokenspeed-scheduler/bindings/python_module.cpp](tokenspeed-scheduler/bindings/python_module.cpp)
- [tokenspeed-scheduler/csrc/scheduler/types.h](tokenspeed-scheduler/csrc/scheduler/types.h)
- [tokenspeed-scheduler/python/tests/test_kv_cache.py](tokenspeed-scheduler/python/tests/test_kv_cache.py)

</details>



The `python/tokenspeed/runtime` package serves as the high-level orchestration layer of the TokenSpeed inference engine. It is responsible for managing the lifecycle of inference requests, coordinating distributed model execution, and interfacing with the C++ scheduler and custom hardware kernels.

The runtime is designed for high-throughput serving, supporting features like continuous batching, prefix caching, and prefill-decode disaggregation. It utilizes `uvloop` for high-performance asynchronous event handling `[python/tokenspeed/runtime/engine/async_llm.py:102-102]()`.

### Architecture Overview

The Python runtime acts as a bridge between the external API layers and low-level hardware execution components. The `AsyncLLM` class serves as the main-process async frontend, owning request intake, per-request state, scheduler IPC via `EngineCoreClient`, and the output-dispatch loop `[python/tokenspeed/runtime/engine/async_llm.py:118-125](), [python/tokenspeed/runtime/engine/core_client.py:78-85]()`. The `EventLoop` orchestrates rank-local execution, interacting with the `tokenspeed_scheduler.Scheduler` C++ bindings `[python/tokenspeed/runtime/engine/event_loop.py:32-34](), [python/tokenspeed/runtime/engine/event_loop.py:131-145]()`.

#### System Component Map

The following diagram illustrates the relationship between primary Python entities, communication channels, and underlying execution layers, bridging natural language spaces to code entities.

**Diagram: Runtime Entity Relationships**
```mermaid
graph TD
    subgraph "Natural Language Space (API)"
        "HTTP_Server"["api_server.py"]
        "AsyncLLM"["AsyncLLM (async_llm.py)"]
    end

    subgraph "Code Entity Space (Python Runtime)"
        "EngineCoreClient"["EngineCoreClient (core_client.py)"]
        "EventLoop"["EventLoop (event_loop.py)"]
        "ModelExecutor"["ModelExecutor (model_executor.py)"]
        "InputBuffers"["InputBuffers (input_buffer.py)"]
    end

    subgraph "Execution Space (C++ / Kernels)"
        "Scheduler"["Scheduler (tokenspeed-scheduler)"]
        "Kernels"["tokenspeed-kernel"]
    end

    "HTTP_Server" --> "AsyncLLM"
    "AsyncLLM" --> "EngineCoreClient"
    "EngineCoreClient" -- "ZMQ IPC" --> "EventLoop"
    "EventLoop" -- "Nanobind" --> "Scheduler"
    "EventLoop" --> "ModelExecutor"
    "ModelExecutor" --> "InputBuffers"
    "ModelExecutor" --> "Kernels"
```
Sources: `[python/tokenspeed/runtime/engine/async_llm.py:118-125](), [python/tokenspeed/runtime/engine/core_client.py:78-85](), [python/tokenspeed/runtime/engine/event_loop.py:32-34](), [python/tokenspeed/runtime/execution/model_executor.py:52-57]()`

---

### Subsystems and Child Pages

The runtime is organized into several specialized modules. Detailed documentation for each is covered in the respective child pages:

#### [Engine and Request Lifecycle](#2.1)
This subsystem handles the entry point for all requests. `AsyncLLM` manages request intake, validation, and per-request state tracking `[python/tokenspeed/runtime/engine/async_llm.py:118-125]()`. IPC communication with the scheduler uses `EngineCoreClient` over ZMQ sockets `[python/tokenspeed/runtime/engine/core_client.py:78-85]()`. The `EventLoop` drives the iteration process, advancing the C++ scheduler and processing execution results `[python/tokenspeed/runtime/engine/event_loop.py:131-145]()`.
*   **Key Entities:** `AsyncLLM`, `EngineCoreClient`, `EventLoop`, `RequestHandler`, `OutputProcesser`.
*   For details, see [Engine and Request Lifecycle](#2.1).
Sources: `[python/tokenspeed/runtime/engine/async_llm.py:118-125](), [python/tokenspeed/runtime/engine/core_client.py:78-85](), [python/tokenspeed/runtime/engine/event_loop.py:131-145]()`

#### [KV Cache and Memory Management](#2.2)
TokenSpeed utilizes a sophisticated prefix cache and slab pools to manage attention key-value caches across varying sequence lengths and model recipes (such as MHA, MLA, and hybrid variants). The runtime coordinates cache state alongside the C++ scheduler and memory allocators.
*   **Key Entities:** `CachePool`, `MemoryOccupationController`, `RuntimeStates`.
*   For details, see [KV Cache and Memory Management](#2.2).
Sources: `[python/tokenspeed/runtime/execution/runtime_states.py:25-27]()`

#### [Model Execution and Layers](#2.3)
The execution layer is responsible for loading weights, building forward contexts, and running the model forward pass. `ModelExecutor` and `ModelRunner` orchestrate execution steps, using `InputBuffers` to manage tensor data sources and `RuntimeStates` to maintain per-request pool indices and cached lengths `[python/tokenspeed/runtime/execution/model_executor.py:52-61](), [python/tokenspeed/runtime/execution/input_buffer.py:41-47](), [python/tokenspeed/runtime/execution/runtime_states.py:25-27]()`.
*   **Key Entities:** `ModelExecutor`, `ModelRunner`, `InputBuffers`, `RuntimeStates`.
*   For details, see [Model Execution and Layers](#2.3).
Sources: `[python/tokenspeed/runtime/execution/model_executor.py:52-61](), [python/tokenspeed/runtime/execution/input_buffer.py:41-47](), [python/tokenspeed/runtime/execution/runtime_states.py:25-27]()`

#### [Distributed Communication](#2.4)
The runtime orchestrates distributed inference across multiple GPUs and nodes using process group managers. It supports tensor, expert, data, and pipeline parallelism via pluggable communication backends such as NCCL and Triton allreduce.
*   **Key Entities:** `process_group_manager`, `DistributedInitializer`.
*   For details, see [Distributed Communication](#2.4).
Sources: `[python/tokenspeed/runtime/distributed/process_group_manager.py]()`

#### [Prefill-Decode Disaggregation (PD/EPD)](#2.5)
TokenSpeed supports disaggregating prefill and decode phases into separate execution instances. Prefill and decode executors coordinate KV cache transfers using external transfer mechanisms like Mooncake and specialized transfer plans.
*   **Key Entities:** `DisaggPrefillExecutor`, `DisaggDecodeExecutor`, `KVEventBatch`.
*   For details, see [Prefill-Decode Disaggregation (PD/EPD)](#2.5).
Sources: `[python/tokenspeed/runtime/pd/kv_events]()`

#### [Speculative Decoding and Grammar](#2.6)
For accelerated generation and structured output, the runtime provides drafter registries (supporting algorithms such as EAGLE, MTP, and DFLASH) alongside capturable grammar runtimes.
*   **Key Entities:** `BaseDrafter`, `GrammarStepInputs`, `SamplingParams`.
*   For details, see [Speculative Decoding and Grammar](#2.6).
Sources: `[python/tokenspeed/runtime/grammar/capturable_grammar.py]()`

#### [Multimodal and Sampling](#2.7)
The multimodal pipeline handles input embedders, multi-modal rotary position embeddings (MRoPE), and shared-memory transport. The sampling subsystem handles token selection through backends like FlashInfer and logits processors.
*   **Key Entities:** `SamplingBackend`, `LogitsProcessor`, `MultimodalRuntime`.
*   For details, see [Multimodal and Sampling](#2.7).
Sources: `[python/tokenspeed/runtime/sampling/backends/base.py]()`

---

### Configuration and Subprocess Orchestration

The runtime reads configuration parameters via `ServerArgs` and initializes rank-local subprocesses for execution and scheduling over ZMQ IPC channels `[python/tokenspeed/runtime/engine/async_llm.py:126-140](), [python/tokenspeed/runtime/engine/event_loop.py:131-150]()`.

**Diagram: Configuration to Execution Flow**
```mermaid
graph LR
    subgraph "Configuration Space"
        "ServerArgs"["ServerArgs (server_args.py)"]
    end
    
    subgraph "Orchestration & IPC"
        "ServerArgs" --> "AsyncLLM"["AsyncLLM (async_llm.py)"]
        "AsyncLLM" --> "EngineCoreClient"["EngineCoreClient (core_client.py)"]
        "EngineCoreClient" -- "ZMQ IPC" --> "EventLoop"["EventLoop (event_loop.py)"]
    end

    subgraph "Execution Layer"
        "EventLoop" --> "ModelExecutor"["ModelExecutor (model_executor.py)"]
        "ModelExecutor" --> "InputBuffers"["InputBuffers (input_buffer.py)"]
    end
```
Sources: `[python/tokenspeed/runtime/engine/async_llm.py:126-140](), [python/tokenspeed/runtime/engine/core_client.py:78-85](), [python/tokenspeed/runtime/engine/event_loop.py:131-150](), [python/tokenspeed/runtime/execution/model_executor.py:52-61](), [python/tokenspeed/runtime/execution/input_buffer.py:41-47]()`

---

