> 来源: [https://deepwiki.com/sgl-project/sglang/3-core-server-architecture](https://deepwiki.com/sgl-project/sglang/3-core-server-architecture)
> DeepWiki sgl-project/sglang | Last indexed: 27 Aug 2026 (94183a)

# Core Server Architecture

  Relevant source files 
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
 
  This page describes SGLang's multi-process server architecture, covering the division of responsibilities across processes, inter-process communication (IPC) methods, and the configuration system. It provides a high-level overview, linking to detailed child pages for in-depth explanations.

 
## Purpose and Scope

 SGLang adopts a **multi-process architecture** for its inference runtime, comprising separate processes for tokenization, scheduling and model execution, and detokenization. This design:

 
 - **Bypasses Python GIL limitations:** Separating CPU-intensive tokenization and detokenization from GPU-bound model execution permits better hardware utilization and concurrency [python/sglang/srt/managers/tokenizer_manager.py14-16](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L14-L16)
 - **Enables asynchronous processing:** Each process runs independently and communicates asynchronously, allowing efficient batching, streaming, and parallelism [python/sglang/srt/managers/tokenizer_manager.py14-16](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L14-L16)
 - **Supports distributed parallelism:** Through Tensor Parallelism, Pipeline Parallelism, Data Parallelism, and Expert Parallelism integrated in the core [python/sglang/srt/model_executor/model_runner.py42-86](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L42-L86)
 - **Improves robustness:** Process isolation combined with subprocess watchdogs supports fault tolerance and controlled restarts [python/sglang/srt/entrypoints/engine.py135-136](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L135-L136)
 
 The main components in this architecture are:

 
 - **HTTP Server + Engine (Main Process):** Handles client API requests, lifecycle management, and dispatch [python/sglang/srt/entrypoints/engine.py207-214](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L207-L214)
 - **TokenizerManager Process:** Responsible for tokenizing incoming text and processing multimodal inputs [python/sglang/srt/managers/tokenizer_manager.py14-16](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L14-L16)
 - **Scheduler Process:** Manages request batch scheduling, memory pools, forwarding tokens through the model runner(s), and distributed coordination [python/sglang/srt/managers/scheduler.py14-17](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L14-L17)
 - **DetokenizerManager Process:** Converts generated token IDs into strings asynchronously, sending results back to the tokenizer [python/sglang/srt/entrypoints/engine.py51-52](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L51-L52)
 
 For detailed descriptions, see the child pages:

 
 - [Multi-Process Architecture and IPC](https://deepwiki.com/sgl-project/sglang/3.1-multi-process-architecture-and-ipc)
 - [Server Configuration (ServerArgs)](https://deepwiki.com/sgl-project/sglang/3.2-server-configuration-(serverargs))
 - [TokenizerManager and DetokenizerManager](https://deepwiki.com/sgl-project/sglang/3.3-tokenizermanager-and-detokenizermanager)
 
 
---

 
## Multi-Process Design Overview

 SGLang’s architecture decomposes the serving runtime into independent processes communicating over ZeroMQ (ZMQ) with well-defined message types, enabling full asynchronicity and scalability.

 
### High-Level Data Flow

 
 - **HTTP Server / Engine** receives client requests and forwards them to the **TokenizerManager**
 - **TokenizerManager** tokenizes the input along with any multimodal encoding and sends tokenized requests to the **Scheduler**
 - **Scheduler** batches requests, manages KV cache memory, and delegates to **ModelRunner(s)** for inference
 - The scheduler streams generated token IDs to the **DetokenizerManager**
 - **DetokenizerManager** converts token IDs to strings asynchronously, sending text back to the TokenizerManager for client response
 
 
### Core Component Interaction Diagram

 
```

```

 This architecture cleanly separates concerns and stages, connected via asynchronous ZMQ sockets. The isolated processes enable improved throughput, resource utilization, and easier scalability.

 **Sources:**

 
 - [python/sglang/srt/managers/scheduler.py14-15](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L14-L15)
 - [python/sglang/srt/managers/tokenizer_manager.py14-16](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L14-L16)
 - [python/sglang/srt/model_executor/model_runner.py1-14](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L1-L14)
 - [python/sglang/srt/managers/schedule_batch.py36-48](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L36-L48)
 
 
---

 
## Process Roles and Responsibilities

 
### TokenizerManager

 The TokenizerManager process converts raw input into tokenized form suitable for the scheduler and underlying model.

 
 - Accepts requests, tokenizes and prepares multimodal inputs with `get_mm_processor()` [python/sglang/srt/managers/tokenizer_manager.py93](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L93-L93)
 - Maintains request states (`ReqState`) to track incremental decoding progress, streaming offsets, and output tokens [python/sglang/srt/managers/tokenizer_manager.py215-221](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L215-L221)
 - Supports batching optimizations via `AsyncDynamicbatchTokenizer` mixin to improve throughput on CPU-bound tokenization [python/sglang/srt/managers/tokenizer_manager.py54](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L54-L54)
 - Communicates tokenized batches to the scheduler asynchronously over ZMQ [python/sglang/srt/managers/tokenizer_manager.py81-82](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L81-L82)
 
 
### Scheduler

 The scheduler is the central process that orchestrates batch formation, memory allocation, and model execution.

 
 - Receives batched tokenized input, schedules requests into `ScheduleBatch` following policies [python/sglang/srt/managers/scheduler.py14-17](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L14-L17) [python/sglang/srt/managers/schedule_batch.py199-204](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L199-L204)
 - Manages memory pools (`ReqToTokenPool`, `BaseTokenToKVPoolAllocator`) to allocate token KV cache slots with eviction and radix caching [python/sglang/srt/managers/schedule_batch.py90-94](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L90-L94)
 - Invokes `ModelRunner` to execute forward passes which may use distributed parallelism and CUDA Graphs for performance [python/sglang/srt/model_executor/model_runner.py1-14](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L1-L14)
 - Sends generated tokens to DetokenizerManager asynchronously via ZMQ [python/sglang/srt/managers/io_struct.py63-64](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/io_struct.py#L63-L64)
 
 
### DetokenizerManager

 Dedicated to turning generated token IDs into readable strings without blocking the scheduler.

 
 - Runs as a standalone process to convert token batches into text [python/sglang/srt/managers/detokenizer_manager.py14-15](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/detokenizer_manager.py#L14-L15)
 - Supports incremental decoding state management to handle streaming output efficiently [python/sglang/srt/managers/detokenizer_manager.py75-100](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/detokenizer_manager.py#L75-L100)
 - Sends text results back to the TokenizerManager via IPC [python/sglang/srt/entrypoints/engine.py51-52](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L51-L52)
 
 
---

 
## Inter-Process Communication (IPC)

 SGLang employs **ZeroMQ (ZMQ)** for high-performance asynchronous IPC between the core server processes.

 
### IPC Message Types and Flow

 
```

```

 
 - `TokenizedGenerateReqInput` messages flow from TokenizerManager to Scheduler for processing [python/sglang/srt/managers/tokenizer_manager.py82](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L82-L82)
 - The Scheduler outputs batches of token IDs as `BatchTokenIDOutput` sent to DetokenizerManager [python/sglang/srt/managers/io_struct.py64](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/io_struct.py#L64-L64)
 - DetokenizerManager returns generated strings as `BatchStrOutput` back to TokenizerManager [python/sglang/srt/managers/io_struct.py63](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/io_struct.py#L63-L63)
 - TokenizerManager forwards final string output to the HTTP server for client response
 
 IPC endpoints, socket types, and addresses are dynamically configured by `PortArgs` and `ServerArgs` [python/sglang/srt/entrypoints/engine.py155-162](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L155-L162)

 This IPC design provides a loosely coupled, scalable pipeline that decouples process lifetimes and maximizes throughput.

 **Sources:**

 
 - [python/sglang/srt/managers/io_struct.py14-21](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/io_struct.py#L14-L21)
 - [python/sglang/srt/managers/tokenizer_manager.py44-45](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L44-L45)
 - [python/sglang/srt/entrypoints/engine.py51-52](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L51-L52)
 
 
---

 
## Configuration and Management

 
### Server Configuration (ServerArgs)

 Server configuration controls runtime behavior, hardware settings, IPC channels, and model loading options. The `ServerArgs` dataclass aggregates these parameters.

 
| Configuration Area | Examples of Parameters |
|---|---|
| Model | model_path, load_format, trust_remote_code, chat_template |
| Quantization | quant_method (e.g., FP8, MXFP4, AWQ, GPTQ, ModelOpt) |
| Parallelism | tp_size, pp_size, dp_size, ep_size |
| Hardware | CUDA/ROCm/XPU/NPU device flags, platform-specific options |
| IPC Ports | Addresses and socket names for IPC channels (scheduler_input_ipc, tokenizer_ipc, detokenizer_ipc) |

 These settings allow flexible deployment on diverse hardware, with fine-grained control over distributed execution, memory, and runtime optimizations [python/sglang/srt/server_args.py14-200](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L14-L200)

 For a detailed explanation, see [Server Configuration (ServerArgs)](https://deepwiki.com/sgl-project/sglang/3.2-server-configuration-(serverargs)).

 
---

 
### Tokenizer and Detokenizer Management

 The tokenizer and detokenizer components manage complex request lifecycles and multi-tokenizer support:

 
 - **Multi-tokenizer support:** The `MultiTokenizerRouter` and related mixins allow multiple tokenizer instances to serve different models or clients simultaneously [python/sglang/srt/managers/multi_tokenizer_mixin.py92-94](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/multi_tokenizer_mixin.py#L92-L94)
 - **Dynamic batching:** The tokenizer employs the `AsyncDynamicbatchTokenizer` mixin for efficient dynamic batch formation on CPU [python/sglang/srt/managers/tokenizer_manager.py54](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L54-L54)
 - **Request state management:** `TokenizerControlMixin` handles lifecycles, aborts, and incremental output notifications [python/sglang/srt/managers/tokenizer_manager.py99](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L99-L99)
 - **Detokenizer isolation:** Detokenization runs in a separate process to avoid stalls in the scheduler loop caused by string operations, ensuring smooth latency and throughput [python/sglang/srt/entrypoints/engine.py51-52](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L51-L52)
 
 For details, see the child page [TokenizerManager and DetokenizerManager](https://deepwiki.com/sgl-project/sglang/3.3-tokenizermanager-and-detokenizermanager).

 
---

 
### Multi-Process Architecture and IPC

 Underlying the architecture is the robust IPC framework and process management:

 
 - IPC messages use custom-defined msgspec-structured types for compact, typed serialization [python/sglang/srt/managers/io_struct.py79-102](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/io_struct.py#L79-L102)
 - The TokenizerManager tracks request states (`ReqState`) and streaming progress to coordinate with Scheduler and Detokenizer [python/sglang/srt/managers/tokenizer_manager.py215-221](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L215-L221)
 - IPC endpoints are configured centrally and passed as arguments to subprocesses for socket binding and communication setup [python/sglang/srt/entrypoints/engine.py155-162](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L155-L162)
 - Watchdog monitors supervise child processes for fault detection and recovery actions [python/sglang/srt/entrypoints/engine.py135-136](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L135-L136)
 
 See the detailed child page [Multi-Process Architecture and IPC](https://deepwiki.com/sgl-project/sglang/3.1-multi-process-architecture-and-ipc).

 
---

 
# Summary

 SGLang’s core server architecture features:

 
 - **Dedicated processes** for tokenizer, scheduler/model execution, and detokenizer components enabling asynchronous, parallel processing.
 - **ZMQ-based IPC** with strongly typed message payloads to connect components and enable robust distributed processing.
 - A centralized **ServerArgs configuration system** supporting rich deployment tuning and hardware targeting.
 - Sophisticated **TokenizerManager and DetokenizerManager modules** that manage request states, streaming, multi-tokenizer support, and multimodal processing.
 - A capable **Scheduler** that manages request batching, memory pools, and orchestrates forward passes potentially across distributed resources.
 
 This organization supports efficient high-throughput LLM and VLM serving with scalability and fault tolerance.

 
---

 
# References and Further Reading

 
 - See [Multi-Process Architecture and IPC](https://deepwiki.com/sgl-project/sglang/3.1-multi-process-architecture-and-ipc) for comprehensive process model and IPC protocols.
 - See [Server Configuration (ServerArgs)](https://deepwiki.com/sgl-project/sglang/3.2-server-configuration-(serverargs)) for detailed configuration parameters and effects.
 - See [TokenizerManager and DetokenizerManager](https://deepwiki.com/sgl-project/sglang/3.3-tokenizermanager-and-detokenizermanager) for deep dives into tokenization/detokenization handling.
 
 
---

 **Sources:**

 
 - [python/sglang/srt/server_args.py14-200](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L14-L200)
 - [python/sglang/srt/managers/tokenizer_manager.py14-221](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L14-L221)
 - [python/sglang/srt/managers/io_struct.py14-64](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/io_struct.py#L14-L64)
 - [python/sglang/srt/managers/scheduler.py14-17](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L14-L17)
 - [python/sglang/srt/managers/schedule_batch.py36-94](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L36-L94)
 - [python/sglang/srt/model_executor/model_runner.py1-86](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L1-L86)
 - [python/sglang/srt/entrypoints/engine.py51-214](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L51-L214)
