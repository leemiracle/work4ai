<!-- source: DeepWiki mcp.deepwiki.com · repo sgl-project/sglang · page 21 SGLang Model Gateway (sgl-model-gateway) · fetched 2026-10-30 -->

# SGLang Model Gateway (sgl-model-gateway)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [proto/sglang/api/v1/sampling.proto](proto/sglang/api/v1/sampling.proto)
- [python/sglang/srt/managers/disagg_service.py](python/sglang/srt/managers/disagg_service.py)
- [python/sglang/srt/rust_server/config.py](python/sglang/srt/rust_server/config.py)
- [python/sglang/srt/rust_server/server.py](python/sglang/srt/rust_server/server.py)
- [rust/sglang-server/src/api_server/core/handle.rs](rust/sglang-server/src/api_server/core/handle.rs)
- [rust/sglang-server/src/api_server/core/prefetch.rs](rust/sglang-server/src/api_server/core/prefetch.rs)
- [rust/sglang-server/src/api_server/http.rs](rust/sglang-server/src/api_server/http.rs)
- [rust/sglang-server/src/api_server/http/app.rs](rust/sglang-server/src/api_server/http/app.rs)
- [rust/sglang-server/src/api_server/http/info.rs](rust/sglang-server/src/api_server/http/info.rs)
- [rust/sglang-server/src/api_server/http/loads.rs](rust/sglang-server/src/api_server/http/loads.rs)
- [rust/sglang-server/src/api_server/http/metrics.rs](rust/sglang-server/src/api_server/http/metrics.rs)
- [rust/sglang-server/src/api_server/http/native_api.rs](rust/sglang-server/src/api_server/http/native_api.rs)
- [rust/sglang-server/src/api_server/http/openai.rs](rust/sglang-server/src/api_server/http/openai.rs)
- [rust/sglang-server/src/api_server/http/openai/chat.rs](rust/sglang-server/src/api_server/http/openai/chat.rs)
- [rust/sglang-server/src/api_server/http/openai/completions.rs](rust/sglang-server/src/api_server/http/openai/completions.rs)
- [rust/sglang-server/src/api_server/http/openai/template.rs](rust/sglang-server/src/api_server/http/openai/template.rs)
- [rust/sglang-server/src/api_server/http/openai/test_utils.rs](rust/sglang-server/src/api_server/http/openai/test_utils.rs)
- [rust/sglang-server/src/api_server/http/openai/tokenize.rs](rust/sglang-server/src/api_server/http/openai/tokenize.rs)
- [rust/sglang-server/src/api_server/http/openai/tools.rs](rust/sglang-server/src/api_server/http/openai/tools.rs)
- [rust/sglang-server/src/lib.rs](rust/sglang-server/src/lib.rs)
- [rust/sglang-server/src/message.rs](rust/sglang-server/src/message.rs)
- [rust/sglang-server/src/message/config.rs](rust/sglang-server/src/message/config.rs)
- [rust/sglang-server/src/message/detok.rs](rust/sglang-server/src/message/detok.rs)
- [rust/sglang-server/src/message/finish_reason.rs](rust/sglang-server/src/message/finish_reason.rs)
- [rust/sglang-server/src/message/multimodal.rs](rust/sglang-server/src/message/multimodal.rs)
- [rust/sglang-server/src/message/types.rs](rust/sglang-server/src/message/types.rs)
- [rust/sglang-server/src/message/wire.rs](rust/sglang-server/src/message/wire.rs)
- [rust/sglang-server/src/multi_modality/payload.rs](rust/sglang-server/src/multi_modality/payload.rs)
- [rust/sglang-server/src/multi_modality/worker.rs](rust/sglang-server/src/multi_modality/worker.rs)
- [rust/sglang-server/src/tokenizer_manager.rs](rust/sglang-server/src/tokenizer_manager.rs)
- [rust/sglang-server/src/tokenizer_manager/detokenizer.rs](rust/sglang-server/src/tokenizer_manager/detokenizer.rs)
- [rust/sglang-server/src/tokenizer_manager/to_scheduler.rs](rust/sglang-server/src/tokenizer_manager/to_scheduler.rs)
- [rust/sglang-server/src/tokenizer_manager/to_scheduler_tests.rs](rust/sglang-server/src/tokenizer_manager/to_scheduler_tests.rs)
- [rust/sglang-server/src/tokenizer_manager/to_scheduler_validation.rs](rust/sglang-server/src/tokenizer_manager/to_scheduler_validation.rs)
- [rust/sglang-server/src/tokenizer_manager/tokenizer.rs](rust/sglang-server/src/tokenizer_manager/tokenizer.rs)
- [rust/sglang-server/src/tokenizer_manager/wiring.rs](rust/sglang-server/src/tokenizer_manager/wiring.rs)
- [rust/sglang-server/src/utils/runtime.rs](rust/sglang-server/src/utils/runtime.rs)
- [test/registered/unit/entrypoints/test_rust_server_dp_ports.py](test/registered/unit/entrypoints/test_rust_server_dp_ports.py)
- [test/registered/unit/multimodal/rust/shared/test_rust_server_extension.py](test/registered/unit/multimodal/rust/shared/test_rust_server_extension.py)

</details>



## Purpose and scope

This page gives a high-level view of the model-gateway topic and points to its child pages for gateway-specific details. The available source files describe `sglang-server`, a Rust HTTP/gRPC frontend embedded in the Python scheduler process; they do not establish the implementation details of a separate `sgl-model-gateway` crate. The overview below therefore distinguishes the documented server frontend from gateway features that are covered by the child pages. 

Sources: [rust/sglang-server/src/lib.rs:1-12]()

## Gateway Architecture and Worker Management

A useful starting point for understanding serving boundaries is `sglang-server`: its `api_server` provides HTTP and gRPC adapters over a shared, transport-independent `CoreHandle`. The runtime bootstrap wires the API server to tokenizer, detokenizer, and scheduler-facing channels. This describes the serving frontend and its runtime pipeline, rather than a gateway worker registry or gateway control plane.

For gateway control-plane details such as worker registration, job queues, circuit breakers, and service discovery, see [Gateway Architecture and Worker Management](#21.1).

**Diagram: Serving frontend entities in code**

```mermaid
graph LR
    HTTP["HttpLayer"] --> "CoreHandle"
    GRPC["gRPC adapter"] --> "CoreHandle"
    "CoreHandle" --> "TmEvent"
    "Runtime::start" --> "to_scheduler_rx"
    "Runtime::start" --> "from_scheduler_tx"
```

Sources: [rust/sglang-server/src/api_server/core/handle.rs:95-117]() [rust/sglang-server/src/utils/runtime.rs:34-52]() [rust/sglang-server/src/utils/runtime.rs:128-150]() [rust/sglang-server/src/lib.rs:158-162]()

## Routing Policies and Load Balancing

Gateway routing policies determine which backend handles a request. The available source files show request submission through `CoreHandle::generate` into the runtime pipeline, but do not document gateway-level cache-aware routing, power-of-two selection, or multi-model routing behavior.

For routing strategies and load-balancing details, see [Routing Policies and Load Balancing](#21.2).

**Diagram: Request submission path documented in the server frontend**

```mermaid
graph LR
    HTTP["chat_completions"] --> "CoreHandle::generate"
    GRPC["gRPC adapter"] --> "CoreHandle"
    "CoreHandle::generate" --> "intake_tx"
    "intake_tx" --> "TmEvent"
```

Sources: [rust/sglang-server/src/api_server/core/handle.rs:95-117]() [rust/sglang-server/src/api_server/core/handle.rs:161-177]() [rust/sglang-server/src/api_server/http/openai/chat.rs:84-90]()

## Workflow Engine and WASM Middleware

The documented Rust server frontend assembles HTTP routes for info, loads, native API, OpenAI-compatible API, and optional metrics; it can also wrap the app with an `HttpLayer`. These are server-side routing and middleware extension points, not evidence of the gateway workflow engine or its WASM plugin system.

For workflow orchestration, WASM middleware, MCP integration, conversation connectors, and e2e testing, see [Workflow Engine and WASM Middleware](#21.3).

Sources: [rust/sglang-server/src/api_server/http/app.rs:85-106]() [rust/sglang-server/src/lib.rs:158-162]()

## Summary Diagram: Serving Concepts to Code Entities

This diagram maps documented serving concepts to code identifiers, contrasting natural language descriptions with exact symbols found in the codebase.

```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        "HTTP and gRPC entry"
        "Shared request core"
        "Python scheduler boundary"
        "HTTP route composition"
    end

    subgraph "CodeEntitySpace"
        "api_server::http"
        "api_server::grpc"
        "CoreHandle"
        "ToSchedulerRx"
        "FromSchedulerTx"
        "serve"
        "AppState"
    end

    "HTTP and gRPC entry" --> "api_server::http"
    "HTTP and gRPC entry" --> "api_server::grpc"
    "Shared request core" --> "CoreHandle"
    "Python scheduler boundary" --> "ToSchedulerRx"
    "Python scheduler boundary" --> "FromSchedulerTx"
    "HTTP route composition" --> "serve"
    "HTTP route composition" --> "AppState"
```

Sources: [rust/sglang-server/src/utils/runtime.rs:42-45]() [rust/sglang-server/src/api_server/http/app.rs:64-70]() [rust/sglang-server/src/api_server/http/app.rs:27-35]() [rust/sglang-server/src/api_server/core/handle.rs:102-106]()

## Child Pages

- [Gateway Architecture and Worker Management](#21.1) — Control plane, worker registry, job queue, circuit breakers, and service discovery.
- [Routing Policies and Load Balancing](#21.2) — Cache-aware routing, power-of-two selection, PD routing, and multi-model IGW mode.
- [Workflow Engine and WASM Middleware](#21.3) — Workflow engine, WASM plugins, MCP integration, conversation connectors, and e2e test infrastructure.

Sources: [rust/sglang-server/src/lib.rs:1-12]()

---

