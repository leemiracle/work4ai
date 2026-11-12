# API Overview

The Game Agent SDK is a collection of C functions (with a thin C++ wrapper) for running on-device AI inference on the GPU. To integrate, include the public headers, link against the SDK's import library, and ensure the DLLs are on the application's DLL search path. By utilizing a C99 ABI, the SDK can also be loaded dynamically from C++, Python, Rust, and other front ends.

## What's in the box

The source repository is organized as follows:

* `source/core/`: public C headers (`ace.h`, `ace_types.h`, `ace_result.h`) and the optional C++ wrapper (`ace_cpp.h`), plus the SDK implementation. Headers under `source/core/internal/` and `source/core/rag/` are implementation-only and not part of the public ABI.
* `source/samples/`: source code for the prebuilt sample applications (`Agent-Sample.cpp`, `Chat-Sample.cpp`, `MultiAgent-Sample.cpp`). See [Samples](samples.md) for what each one does.
* `source/tools/`: source for `BuildRag.exe`. See [Building a RAG Database](rag-building-a-database.md) for how to use it.
* `source/tests/`: source for the SDK's automated test suite.
* `data/`: SLM and embedding models, prebuilt RAG databases, sample game-state JSONs, and raw text files used to build the databases.
* `external/`: third-party libraries the SDK builds against (llama.cpp, ONNX Runtime, faiss, OpenBLAS, nlohmann/json, tracy, etc.). See `THIRD-PARTY-LICENSES.md` at the repo root for the full list and license texts.
* `tools/`: the `premake5` binary used by `setup.bat`, plus `vswhere.exe` used by `build.bat` to locate Visual Studio.
* `docs/`: documentation source. `build_docs_html.bat` in this folder produces HTML output under `sphinx/build/html/`.

After running `build.bat`, built artifacts land under:

* `_out/`: the SDK DLL (`ACE.SDK.dll`), its import library (`ACE.SDK.lib`), runtime dependency DLLs (llama.cpp + ggml backends, ONNX Runtime, OpenBLAS, CUDA runtime), and the sample / utility executables.
* `_artifacts/`: per-project intermediate build outputs.

The release zip produced by `package.bat` flattens these into `include/`, `lib/`, `bin/`, `samples/`, `data/`, `docs/` for downstream consumers who don't need the source.

## Three groups of APIs

Applications interact with the SDK through three groups of APIs:

* **Agent APIs** (`ace_agent*`) are **stateful**: the agent owns the conversation lifecycle on top of an {cpp:type}`ACEModel`. It maintains the conversation history (a list of messages), applies a rolling history window, tracks transient and redacted message consumption, manages a configurable preamble, and caps autonomous tool-call chains via a step counter. Configuration (system instructions, history window, step cap) is set on {cpp:type}`ACEAgentParams` and captured at agent creation. Tools are registered with `ace_agentAddTool`. The application then drives the agent through an event loop: feed input via `ace_agentAddUserInput` and `ace_agentAddToolResult` (tool results may be delivered later from another thread for long-running tools), then call `ace_agentRun`. The call returns one of the following statuses, telling the application what to do next:

  | Status | Meaning |
  |---|---|
  | `ACEAgentStatus_Idle` | Nothing to deliver; the loop can rest until new input arrives. |
  | `ACEAgentStatus_ResponseText` | User-facing response available via {cpp:func}`ace_agentGetResponseText`. |
  | `ACEAgentStatus_ToolCalls` | Tool calls available via {cpp:func}`ace_agentGetToolCalls`; execute them and feed results back via {cpp:func}`ace_agentAddToolResult`. |
  | `ACEAgentStatus_Error` | Error occurred; details via {cpp:func}`ace_agentGetError`. |
  | `ACEAgentStatus_Cancelled` | A cancel request was honored (see {cpp:func}`ace_agentCancel`). |
  | `ACEAgentStatus_Shutdown` | Session is over; exit the loop. |

  See [Agent APIs Deep Dive](agent-deep-dive.md) for the rest of the Agent APIs (instruction changes, message manipulation, preamble, introspection, serialization, cancellation, skip-inference).
* **Chat APIs** (`ace_Model_Chat`, `ace_chat*`, `ace_chatMessage*`) are **stateless**: each call to `ace_Model_Chat` takes a full {cpp:type}`ACEChat` (a list of role-tagged messages: system, user, assistant, tool) and returns one assistant response message. Tool definitions can be attached to the chat via `ace_chatAddTool` and are sent to the model alongside the messages. The application owns the chat history and decides what to append and when to call inference. Suited for callers that already have their own orchestration loop or only need straightforward inference without conversation management.
* **RAG APIs** (`ace_loadDatabase`, `ace_databaseSearch`, `ace_hybridSearch`, `ace_searchResult*`) provide knowledge retrieval over a developer-built corpus. Semantic-only search runs against an {cpp:type}`ACEDatabase` of type `ACEIndexType_Semantic`. Lexical-only search runs against an `ACEDatabase` of type `ACEIndexType_Lexical`. Hybrid search combines both across multiple databases. Returned {cpp:type}`ACESearchResults` carry document text, metadata, and per-hit scores.

The Agent and Chat APIs both take an `ACEModel`. RAG can be invoked standalone from the application or wired in as a tool that the SLM calls during inference (the SDK samples do the latter).

## Lifecycle and Configuration

Setup proceeds in order; teardown is the reverse:

1. **Create the context.** `ace_initContext` takes an {cpp:type}`ACEInitArgs` and returns an {cpp:type}`ACEContext`. The context owns all subsequent SDK objects.
2. **Load one or more models.** `ace_loadModel` takes a path to a GGUF file plus an optional {cpp:type}`ACEModelLoadParams` handle. Each model is bound to its context.
3. **Load one or more databases.** For RAG, `ace_loadDatabase` takes a path to a RAG database directory (see [Building a RAG Database](rag-building-a-database.md)) and an {cpp:type}`ACEDatabaseLoadParams` handle. Skip this step if the application does not use RAG.
4. **Use the APIs.** Either the Agent path (create with `ace_agentCreate`, drive with `ace_agentRun`) or the Chat path (create an `ACEChat`, fill it, call `ace_Model_Chat`). RAG searches can run at any point against the loaded databases.
5. **Destroy in reverse.** Agents (`ace_agentDestroy`), chats (`ace_destroyChat`), databases (`ace_destroyDatabase`), models (`ace_destroyModel`), then `ace_destroyContext`. Search results, inference options, and other handles have their own explicit destroy calls; per-symbol detail is in the [API Reference](api-reference.md).

A single context can host multiple models and multiple databases. Loading N models means N copies of model weights and KV caches resident in VRAM, so keep an eye on GPU memory when stacking large models.

### Model load parameters

{cpp:type}`ACEModelLoadParams` is a handle, created with `ace_createModelLoadParams` and configured through its setters. It controls how a model is loaded:

* **Max context size** caps the number of tokens the model can hold in its context window. Setting it lower than the model's intrinsic max trades capability for VRAM (smaller KV cache). A value of 0 uses the model's default.
* **Inference output buffer size** caps the number of streaming events the model's internal output buffer can hold. Increasing it lets a fast streaming reader keep up with the model; decreasing it saves a small amount of memory. A value of 0 lets the SDK choose.
* **Backend** selects the inference backend. Currently only `ACEInferenceBackend_Llama` (llama.cpp) is supported.

See {cpp:enum}`ACEModelLoadParam` in the API reference for the full enum and per-option defaults.

### Inference options

{cpp:type}`ACEInferenceOptions` is a handle, created with `ace_createInferenceOptions` and configured through its setters. It captures sampling and behavior knobs:

* **Sampling parameters**: temperature, top-p, top-k, min-p, repeat penalty
* **Streaming**: when enabled, tokens stream into the model's output buffer as they're generated
* **Think mode**: when enabled, the model performs extended reasoning (model-dependent; relevant for Qwen3 and similar)
* **Output think tokens**: include reasoning tokens in the streamed output

See {cpp:enum}`ACEInferenceOption` in the API reference for the full enum and per-option defaults.

## Threading rules

* **A single model is not thread-safe for concurrent inference.** Do not call `ace_agentRun` or `ace_Model_Chat` from two threads against the same `ACEModel`. The same applies to two `ACEAgent`s that share one `ACEModel`.
* **Inference is synchronous.** The thread that calls `ace_agentRun` or `ace_Model_Chat` blocks for the duration of the inference. Most applications run the inference call from a worker thread to keep the main thread responsive.
* **Concurrent inference across distinct models is safe.** If the application loads N models, it can run N inferences in parallel from N threads, each against a different model.
* **Cancel and shutdown are thread-safe.** `ace_agentCancel` and `ace_agentShutdown` can be called from any thread, including while another thread is blocked in `ace_agentRun`. The blocked call returns `ACEAgentStatus_Cancelled` or `ACEAgentStatus_Shutdown` accordingly.

## Logging

Logging is handled via a callback registered at context initialization. `ACEInitArgs::logFuncCallback` is invoked with a level (`ACELogLevel_Error` / `Warn` / `Info` / `InferenceDebug`), a UTF-8 message string, and the user-data pointer the application passed in `ACEInitArgs::logUserData`. `ACEInitArgs::level` sets the minimum severity that the SDK will deliver to the callback.

Log lines look like:

```text
[INFO][NVIGI][2025-05-23 12:16:48.709][nvigi][info][framework.cpp:633][nvigiInitImpl]Starting 'nvigi.core.framework':
```

The first bracket is the severity. The second is the originating component:

* `[SDK]`: from the Game Agent SDK DLL
* `[APP]`: from the application (or any other component using the same callback)
* `[NVIGI]`: from the underlying NvIGI library

The samples write logs to a file in their callback; for example, Agent-Sample writes to a file in its working directory.

## Reference

For struct fields, function parameters, return codes, and per-symbol documentation, see the [API Reference](api-reference.md).

The C++ wrapper in `include/ace_cpp.h` mirrors the C API as RAII classes; refer to the header directly when working in C++.
