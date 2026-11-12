> 来源: [https://deepwiki.com/sgl-project/sglang/4-request-processing-pipeline](https://deepwiki.com/sgl-project/sglang/4-request-processing-pipeline)
> DeepWiki sgl-project/sglang | Last indexed: 27 Aug 2026 (94183a)

# Request Processing Pipeline

  Relevant source files 
 - [python/sglang/srt/entrypoints/http_server.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/http_server.py)
 - [python/sglang/srt/environ.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/environ.py)
 - [python/sglang/srt/managers/data_parallel_controller.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/data_parallel_controller.py)
 - [python/sglang/srt/managers/detokenizer_manager.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/detokenizer_manager.py)
 - [python/sglang/srt/managers/io_struct.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/io_struct.py)
 - [python/sglang/srt/managers/multi_tokenizer_mixin.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/multi_tokenizer_mixin.py)
 - [python/sglang/srt/managers/schedule_batch.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py)
 - [python/sglang/srt/managers/scheduler.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py)
 - [python/sglang/srt/managers/scheduler_components/batch_result_processor.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler_components/batch_result_processor.py)
 - [python/sglang/srt/managers/scheduler_components/output_streamer.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler_components/output_streamer.py)
 - [python/sglang/srt/managers/tokenizer_manager.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py)
 - [python/sglang/srt/managers/tp_worker.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tp_worker.py)
 - [python/sglang/srt/managers/utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/utils.py)
 - [python/sglang/srt/mem_cache/common.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/common.py)
 - [python/sglang/srt/model_executor/model_runner.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py)
 - [python/sglang/srt/server_args.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py)
 - [python/sglang/srt/session/streaming_session.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/session/streaming_session.py)
 - [test/registered/scheduler/test_retract_decode_logprob.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/scheduler/test_retract_decode_logprob.py)
 - [test/registered/unit/managers/test_batch_result_processor_hidden_states.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/managers/test_batch_result_processor_hidden_states.py)
 - [test/registered/unit/managers/test_batch_result_processor_mamba_boundary.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/managers/test_batch_result_processor_mamba_boundary.py)
 - [test/registered/unit/managers/test_batch_result_processor_spec_grammar.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/managers/test_batch_result_processor_spec_grammar.py)
 - [test/registered/unit/managers/test_output_streamer_customized_info.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/managers/test_output_streamer_customized_info.py)
 - [test/registered/unit/managers/test_output_streamer_logprobs.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/managers/test_output_streamer_logprobs.py)
 - [test/registered/unit/managers/test_scheduler_timeouts.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/managers/test_scheduler_timeouts.py)
 - [test/registered/unit/spec/test_decode_bookkeeping_ownership.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/spec/test_decode_bookkeeping_ownership.py)
 
  
## Purpose and Scope

 This document describes the end-to-end lifecycle of a request in SGLang, tracing its flow from arrival at the HTTP server, through tokenization, scheduling, model execution, and finally detokenization back to text output. The discussion focuses on core data structure transformations, process responsibilities, and interaction protocols across the multi-process architecture. [python/sglang/srt/managers/schedule_batch.py43-52](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L43-L52)

 Technical details such as request state management, scheduling algorithms, forward pass modes, and CUDA graph optimizations are covered in child pages for depth and clarity:

 
 - [Request Lifecycle and Data Structures](https://deepwiki.com/sgl-project/sglang/4.1-request-lifecycle-and-data-structures) — Document request data structures (`Req`, `ScheduleBatch`, `ForwardBatch`), state transitions, and lifecycle management. [python/sglang/srt/managers/schedule_batch.py200-205](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L200-L205)
 - [Scheduler and Batch Formation](https://deepwiki.com/sgl-project/sglang/4.2-scheduler-and-batch-formation) — Explain scheduling policies (LPM, FCFS, DFS), batch formation, memory budgeting, and the DLLM (Diffusion LLM) scheduler mixin. [python/sglang/srt/managers/scheduler.py208-212](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L208-L212)
 - [Model Execution and Forward Pass](https://deepwiki.com/sgl-project/sglang/4.3-model-execution-and-forward-pass) — Document `ModelRunner`, forward pass modes (prefill/decode/extend/mixed), and output processing. [python/sglang/srt/model_executor/model_runner.py165-168](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L165-L168)
 - [CUDA Graphs and Performance Optimizations](https://deepwiki.com/sgl-project/sglang/4.4-cuda-graphs-and-performance-optimizations) — Explain CUDA Graph capture/replay, piecewise CUDA graphs, breakable CUDA graphs, batch size selection, and decode optimizations. [python/sglang/srt/model_executor/model_runner_components/cuda_graph_setup.py116-120](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner_components/cuda_graph_setup.py#L116-L120)
 
 **Sources**: [python/sglang/srt/managers/scheduler.py14-17](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L14-L17) [python/sglang/srt/managers/schedule_batch.py43-52](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L43-L52)

 
---

 
## Overview

 SGLang implements a **multi-process request pipeline** to maximize throughput and resource utilization by separating concerns across specialized subprocesses communicating predominantly via ZMQ IPC. Each request advances through multiple data representation layers optimized for each functional stage of the pipeline. [python/sglang/srt/managers/tokenizer_manager.py44-46](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L44-L46)

 
### Code Entity Space Bridge: Core Processes

 
```

```

 
 - **HTTP Server**: Receives client API requests and initiates processing using `FastAPI`. [python/sglang/srt/entrypoints/http_server.py49-60](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/http_server.py#L49-L60)
 - **TokenizerManager**: Converts raw text and multimodal inputs to token IDs and embeddings using `get_tokenizer`. [python/sglang/srt/managers/tokenizer_manager.py157-162](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L157-L162)
 - **Scheduler**: Batches tokenized requests, manages memory via `ReqToTokenPool`, and handles execution scheduling. [python/sglang/srt/managers/scheduler.py199-206](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L199-L206)
 - **DetokenizerManager**: Converts generated token IDs back into text strings asynchronously. [python/sglang/srt/managers/detokenizer_manager.py102-109](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/detokenizer_manager.py#L102-L109)
 
 Process isolation eliminates GIL contention and facilitates efficient batching and GPU utilization. Async communication via ZMQ and event loops enables high concurrency and streaming support. [python/sglang/srt/managers/tokenizer_manager.py44-46](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L44-L46) [python/sglang/srt/managers/io_struct.py49-50](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/io_struct.py#L49-L50)

 **Sources**: [python/sglang/srt/entrypoints/http_server.py14-18](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/http_server.py#L14-L18) [python/sglang/srt/managers/tokenizer_manager.py14-17](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L14-L17) [python/sglang/srt/managers/scheduler.py14-15](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L14-L15)

 
---

 
## Request Data Structure Transformations

 During its lifecycle, a request is transformed through different data types tailored for each pipeline stage:

 
```

```

 
| Data Structure | Location | Role |
|---|---|---|
| GenerateReqInput | python/sglang/srt/managers/io_struct.py:168 | High-level API input request, including raw text, multimodal items, and sampling params. |
| TokenizedGenerateReqInput | python/sglang/srt/managers/io_struct.py:86 | Tokenized request containing input IDs and multimodal features. |
| Req | python/sglang/srt/managers/schedule_batch.py:204 | Internal scheduler request object tracking scheduling states and runtime metadata. |
| ScheduleBatch | python/sglang/srt/managers/schedule_batch.py:205 | Group of Req forming a batched unit for model forward execution. |
| ForwardBatch | python/sglang/srt/model_executor/forward_batch_info.py:97 | GPU-optimized batch input to ModelRunner containing tensors for forward passes. |

 Each step adapts the data for the next process’s specific requirements, optimizing for data locality and execution efficiency. [python/sglang/srt/managers/schedule_batch.py43-52](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L43-L52)

 **Sources**: [python/sglang/srt/managers/schedule_batch.py43-52](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L43-L52) [python/sglang/srt/model_executor/forward_batch_info.py96-100](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/forward_batch_info.py#L96-L100) [python/sglang/srt/managers/io_struct.py168-182](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/io_struct.py#L168-L182)

 
---

 
## Process-Level Pipeline Details

 
### 1. HTTP Server Process

 Implemented in `python/sglang/srt/entrypoints/http_server.py`, using FastAPI and `uvicorn`, it exposes OpenAI, Anthropic, and Ollama compatible endpoints. Incoming requests are parsed into `GenerateReqInput` objects and dispatched asynchronously to the `TokenizerManager`. [python/sglang/srt/entrypoints/http_server.py87-109](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/http_server.py#L87-L109)

 
### 2. TokenizerManager Process

 Located in `python/sglang/srt/managers/tokenizer_manager.py`, this process handles chat templates, text tokenization, and multimodal feature extraction. It manages async per-request state via `ReqState` to track partial results and streaming outputs. [python/sglang/srt/managers/tokenizer_manager.py213-220](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L213-L220)

 
### 3. Scheduler Process

 The `Scheduler` (`python/sglang/srt/managers/scheduler.py`) manages the request queue, forms batches based on policies like LPM (Longest Prefix Match), and allocates memory from the `ReqToTokenPool`. It dispatches `ForwardBatch` to GPU workers for execution in modes such as `EXTEND` or `DECODE`. [python/sglang/srt/managers/scheduler.py199-206](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L199-L206) [python/sglang/srt/model_executor/forward_batch_info.py125-126](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/forward_batch_info.py#L125-L126)

 
### 4. DetokenizerManager Process

 The `DetokenizerManager` handles output token ID decoding. It converts batched token IDs into text strings using incremental decoding and sends text chunks back to the `TokenizerManager` for client response assembly. [python/sglang/srt/managers/detokenizer_manager.py102-109](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/detokenizer_manager.py#L102-L109)

 **Sources**: [python/sglang/srt/entrypoints/http_server.py75-80](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/http_server.py#L75-L80) [python/sglang/srt/managers/tokenizer_manager.py14-17](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L14-L17) [python/sglang/srt/managers/scheduler.py199-206](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L199-L206) [python/sglang/srt/managers/detokenizer_manager.py102-109](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/detokenizer_manager.py#L102-L109)

 
---

 
## Execution Phases Overview

 
| Phase | Description |
|---|---|
| Tokenization | Data converted to token IDs; chat templates applied. python/sglang/srt/managers/tokenizer_manager.py157-162 |
| Prefill (Extend) | Model processes input tokens; uses ForwardMode.EXTEND. python/sglang/srt/model_executor/forward_batch_info.py125-126 |
| Decode (Generation) | Model generates tokens one-by-one; uses ForwardMode.DECODE. python/sglang/srt/model_executor/forward_batch_info.py125-126 |
| Detokenization | Token IDs converted back to strings. python/sglang/srt/managers/detokenizer_manager.py102-109 |

 **Sources**: [python/sglang/srt/model_executor/forward_batch_info.py125-126](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/forward_batch_info.py#L125-L126) [python/sglang/srt/managers/tokenizer_manager.py14-17](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L14-L17)

 
---

 
## Streaming vs Non-Streaming Modes

 
 - **Streaming Mode**: Uses incremental streaming metadata and `ReqState` to yield each decoded text chunk incrementally as it becomes available from the `DetokenizerManager`. [python/sglang/srt/managers/tokenizer_manager.py213-220](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L213-L220)
 - **Non-Streaming Mode**: Buffers all generated tokens and signals completion once stop sequences or length limits are reached. [python/sglang/srt/managers/schedule_batch.py200-205](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L200-L205)
 
 **Sources**: [python/sglang/srt/managers/tokenizer_manager.py213-220](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L213-L220) [python/sglang/srt/managers/schedule_batch.py141-145](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L141-L145)

 
---

 
# Summary Diagram: Request Lifecycle

 
```

```

 **Sources**: [python/sglang/srt/entrypoints/http_server.py75-80](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/http_server.py#L75-L80) [python/sglang/srt/managers/tokenizer_manager.py14-17](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L14-L17) [python/sglang/srt/managers/scheduler.py14-15](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L14-L15) [python/sglang/srt/managers/schedule_batch.py43-52](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L43-L52)
