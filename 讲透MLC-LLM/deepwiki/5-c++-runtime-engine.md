> 来源: [https://deepwiki.com/mlc-ai/mlc-llm/5-c++-runtime-engine](https://deepwiki.com/mlc-ai/mlc-llm/5-c++-runtime-engine)
> DeepWiki mlc-ai/mlc-llm | Last indexed: 30 March 2026 (fcce2c

# C++ Runtime Engine

  Relevant source files 
 - [cpp/json_ffi/json_ffi_engine.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/json_ffi/json_ffi_engine.cc)
 - [cpp/multi_gpu/builtin.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/multi_gpu/builtin.cc)
 - [cpp/multi_gpu/multi_gpu_loader.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/multi_gpu/multi_gpu_loader.cc)
 - [cpp/serve/config.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/config.cc)
 - [cpp/serve/config.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/config.h)
 - [cpp/serve/data.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/data.cc)
 - [cpp/serve/data.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/data.h)
 - [cpp/serve/engine.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/engine.cc)
 - [cpp/serve/engine.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/engine.h)
 - [cpp/serve/engine_actions/action.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/engine_actions/action.h)
 - [cpp/serve/engine_state.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/engine_state.cc)
 - [cpp/serve/engine_state.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/engine_state.h)
 - [cpp/serve/event_trace_recorder.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/event_trace_recorder.cc)
 - [cpp/serve/event_trace_recorder.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/event_trace_recorder.h)
 - [cpp/serve/function_table.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/function_table.cc)
 - [cpp/serve/function_table.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/function_table.h)
 - [cpp/serve/logit_processor.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/logit_processor.h)
 - [cpp/serve/model.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/model.cc)
 - [cpp/serve/model.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/model.h)
 - [cpp/serve/prefix_cache.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/prefix_cache.cc)
 - [cpp/serve/prefix_cache.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/prefix_cache.h)
 - [cpp/serve/radix_tree.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/radix_tree.cc)
 - [cpp/serve/radix_tree.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/radix_tree.h)
 - [cpp/serve/request.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/request.cc)
 - [cpp/serve/request.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/request.h)
 - [cpp/serve/request_state.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/request_state.cc)
 - [cpp/serve/request_state.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/request_state.h)
 - [cpp/serve/threaded_engine.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/threaded_engine.cc)
 - [cpp/serve/threaded_engine.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/threaded_engine.h)
 - [cpp/tokenizers/streamer.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/tokenizers/streamer.cc)
 - [cpp/tokenizers/tokenizers.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/tokenizers/tokenizers.cc)
 
  The C++ runtime engine is the core inference execution system in MLC LLM. Implemented primarily in [cpp/serve/](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/) it provides a high-performance, multi-threaded request serving infrastructure that runs compiled models across various hardware backends. This engine handles request queuing, batching, memory management through paged KV cache, and coordinates distributed multi-GPU execution.

 The engine operates on a step-based execution model where each step runs an `EngineAction` (prefill, decode, draft, verify, etc.) on a batch of requests, advancing their generation state and streaming tokens back to callers via a background thread.

 
## Engine Core Architecture

 
### Core Component Overview

 The engine architecture consists of tightly integrated C++ classes that manage the complete inference lifecycle:

 **Title: Core Engine Component Relationships**

 
```

```

 Sources: [cpp/serve/engine.cc343-502](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/engine.cc#L343-L502) [cpp/serve/engine_state.h20-100](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/engine_state.h#L20-L100) [cpp/serve/model.h92-220](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/model.h#L92-L220) [cpp/serve/function_table.h48-143](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/function_table.h#L48-L143) [cpp/json_ffi/json_ffi_engine.cc21-25](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/json_ffi/json_ffi_engine.cc#L21-L25)

 
### EngineImpl and ThreadedEngine

 `EngineImpl` is the primary implementation of the `Engine` interface in [cpp/serve/engine.cc343](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/engine.cc#L343-L343) It is designed to be synchronous per `Step()`, while `ThreadedEngine` [cpp/serve/threaded_engine.cc40](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/threaded_engine.cc#L40-L40) wraps it to provide an asynchronous background loop.

 
| Class | Role |
|---|---|
| EngineImpl | Logic for AddRequest, Step (one iteration of inference), and AbortRequest. |
| ThreadedEngine | Manages a background thread that continuously calls EngineImpl::Step() and handles an instruction queue for thread-safe request management. |
| JSONFFIEngine | Provides a JSON-based FFI layer cpp/json_ffi/json_ffi_engine.cc21 translating OpenAI-style JSON requests into internal Request objects. |

 For details on model loading and internal request lifecycle, see [Engine Core Architecture](https://deepwiki.com/mlc-ai/mlc-llm/5.1-engine-core-architecture).

 Sources: [cpp/serve/engine.cc343-502](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/engine.cc#L343-L502) [cpp/serve/threaded_engine.cc40-188](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/threaded_engine.cc#L40-L188) [cpp/json_ffi/json_ffi_engine.cc21-137](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/json_ffi/json_ffi_engine.cc#L21-L137)

 
### EngineState and Prefix Cache

 `EngineState` [cpp/serve/engine_state.h20](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/engine_state.h#L20-L20) tracks all active requests and manages queues. It holds the `PrefixCache`, which enables KV cache reuse across requests with shared prefixes (e.g., system prompts).

 
```

```

 For details on queue management and radix-tree based prefix caching, see [Engine State and Prefix Cache](https://deepwiki.com/mlc-ai/mlc-llm/5.4-engine-state-and-prefix-cache).

 Sources: [cpp/serve/engine_state.h20-100](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/engine_state.h#L20-L100) [cpp/serve/engine.cc104-147](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/engine.cc#L104-L147)

 
### RequestState Hierarchy

 Requests are tracked through a hierarchical state structure to support parallel generation (`n > 1`) and speculative decoding:

 **Title: RequestState Hierarchy**

 
```

```

 
 - **RequestState**: Container for one user request.
 - **RequestStateEntry**: Represents one generation path (a single sequence).
 - **RequestModelState**: Tracks the state of a sequence on a specific model (e.g., main model vs. draft model).
 
 Sources: [cpp/serve/request_state.h36-142](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/request_state.h#L36-L142) [cpp/serve/request_state.h196-263](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/request_state.h#L196-L263) [cpp/serve/request_state.h276-294](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/request_state.h#L276-L294) [cpp/serve/request_state.cc22-38](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/request_state.cc#L22-L38)

 
## Engine Actions and Request Processing

 The engine advances inference through `EngineAction` objects. In each `Step()`, the engine iterates through its actions (e.g., `NewRequestPrefillActionObj`, `BatchDecodeActionObj`) to process the `waiting_queue` and `running_queue`.

 
| Action | Description |
|---|---|
| NewRequestPrefill | Handles initial prompt processing and KV cache allocation. |
| BatchDecode | Performs standard incremental decoding for all running requests. |
| BatchVerify | Validates proposed tokens in speculative decoding modes. |

 For details on the `Step()` lifecycle and preemption logic, see [Engine Actions and Request Processing](https://deepwiki.com/mlc-ai/mlc-llm/5.2-engine-actions-and-request-processing).

 Sources: [cpp/serve/engine.cc745-765](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/engine.cc#L745-L765) [cpp/serve/engine_actions/action.h32-49](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/engine_actions/action.h#L32-L49)

 
## Token Sampling and Logit Processing

 After a model forward pass (prefill or decode), the engine produces logits. The `LogitProcessor` applies penalties (repetition, frequency) and biases, while the `Sampler` (CPU or GPU-based) selects the next token.

 
 - **LogitProcessor**: Applies `InplaceUpdateLogits` based on `GenerationConfig` [cpp/serve/config.h117](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/config.h#L117-L117)
 - **GPUSampler**: Uses highly optimized kernels (e.g., FlashInfer) to perform top-p/top-k sampling directly on the GPU.
 
 For details on sampling algorithms and speculative verification, see [Token Sampling and Logit Processing](https://deepwiki.com/mlc-ai/mlc-llm/5.3-token-sampling-and-logit-processing).

 Sources: [cpp/serve/logit_processor.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/logit_processor.h) [cpp/serve/sampler/sampler.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/sampler/sampler.h) [cpp/serve/config.h117-147](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/config.h#L117-L147)

 
## Multi-GPU and Distributed Execution

 MLC LLM leverages TVM **Disco** to support multi-GPU execution via Tensor Parallelism (TP) and Pipeline Parallelism (PP).

 
 - **FunctionTable**: Orchestrates calls to either a local TVM VM or a distributed Disco session [cpp/serve/function_table.cc67](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/function_table.cc#L67-L67)
 - **DRef**: Distributed references allow the engine to manage tensors that are sharded across multiple GPUs.
 
 For details on Disco sessions and multi-GPU loading strategies, see [Multi-GPU and Distributed Execution](https://deepwiki.com/mlc-ai/mlc-llm/5.5-multi-gpu-and-distributed-execution).

 Sources: [cpp/serve/function_table.cc67-153](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/function_table.cc#L67-L153) [cpp/serve/function_table.h48-143](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/function_table.h#L48-L143) [cpp/serve/model.cc31-37](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cpp/serve/model.cc#L31-L37)
