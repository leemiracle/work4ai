> 来源: [https://deepwiki.com/sgl-project/sglang/20-sglang-router-%28sgl-router%29](https://deepwiki.com/sgl-project/sglang/20-sglang-router-%28sgl-router%29)
> DeepWiki sgl-project/sglang | Last indexed: 27 Aug 2026 (94183a)

# SGLang Router (sgl-router)

  Relevant source files 
 - [.github/workflows/pr-benchmark-rust.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/pr-benchmark-rust.yml)
 - [sgl-model-gateway/Cargo.toml](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/Cargo.toml)
 - [sgl-model-gateway/README.md](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/README.md?plain=1)
 - [sgl-model-gateway/benches/manual_policy_benchmark.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/benches/manual_policy_benchmark.rs)
 - [sgl-model-gateway/benches/request_processing.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/benches/request_processing.rs)
 - [sgl-model-gateway/benches/router_registry_bench.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/benches/router_registry_bench.rs)
 - [sgl-model-gateway/benches/tree_benchmark.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/benches/tree_benchmark.rs)
 - [sgl-model-gateway/bindings/python/src/lib.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/bindings/python/src/lib.rs)
 - [sgl-model-gateway/bindings/python/src/sglang_router/mini_lb.py](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/bindings/python/src/sglang_router/mini_lb.py)
 - [sgl-model-gateway/bindings/python/src/sglang_router/router.py](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/bindings/python/src/sglang_router/router.py)
 - [sgl-model-gateway/bindings/python/src/sglang_router/router_args.py](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/bindings/python/src/sglang_router/router_args.py)
 - [sgl-model-gateway/bindings/python/tests/test_pyo3_binding.py](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/bindings/python/tests/test_pyo3_binding.py)
 - [sgl-model-gateway/src/config/builder.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/config/builder.rs)
 - [sgl-model-gateway/src/config/types.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/config/types.rs)
 - [sgl-model-gateway/src/config/validation.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/config/validation.rs)
 - [sgl-model-gateway/src/core/circuit_breaker.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/core/circuit_breaker.rs)
 - [sgl-model-gateway/src/core/worker.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/core/worker.rs)
 - [sgl-model-gateway/src/core/worker_builder.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/core/worker_builder.rs)
 - [sgl-model-gateway/src/core/worker_manager.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/core/worker_manager.rs)
 - [sgl-model-gateway/src/core/worker_registry.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/core/worker_registry.rs)
 - [sgl-model-gateway/src/lib.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/lib.rs)
 - [sgl-model-gateway/src/main.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/main.rs)
 - [sgl-model-gateway/src/middleware.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/middleware.rs)
 - [sgl-model-gateway/src/observability/metrics.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/observability/metrics.rs)
 - [sgl-model-gateway/src/policies/bucket.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/policies/bucket.rs)
 - [sgl-model-gateway/src/policies/cache_aware.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/policies/cache_aware.rs)
 - [sgl-model-gateway/src/policies/consistent_hashing.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/policies/consistent_hashing.rs)
 - [sgl-model-gateway/src/policies/factory.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/policies/factory.rs)
 - [sgl-model-gateway/src/policies/manual.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/policies/manual.rs)
 - [sgl-model-gateway/src/policies/mod.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/policies/mod.rs)
 - [sgl-model-gateway/src/policies/power_of_two.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/policies/power_of_two.rs)
 - [sgl-model-gateway/src/policies/prefix_hash.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/policies/prefix_hash.rs)
 - [sgl-model-gateway/src/policies/random.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/policies/random.rs)
 - [sgl-model-gateway/src/policies/registry.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/policies/registry.rs)
 - [sgl-model-gateway/src/policies/round_robin.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/policies/round_robin.rs)
 - [sgl-model-gateway/src/policies/tree.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/policies/tree.rs)
 - [sgl-model-gateway/src/routers/factory.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/routers/factory.rs)
 - [sgl-model-gateway/src/routers/grpc/common/stages/worker_selection.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/routers/grpc/common/stages/worker_selection.rs)
 - [sgl-model-gateway/src/routers/grpc/regular/stages/classify/mod.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/routers/grpc/regular/stages/classify/mod.rs)
 - [sgl-model-gateway/src/routers/grpc/regular/stages/classify/response_processing.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/routers/grpc/regular/stages/classify/response_processing.rs)
 - [sgl-model-gateway/src/routers/header_utils.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/routers/header_utils.rs)
 - [sgl-model-gateway/src/routers/http/pd_router.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/routers/http/pd_router.rs)
 - [sgl-model-gateway/src/routers/http/router.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/routers/http/router.rs)
 - [sgl-model-gateway/src/routers/router_manager.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/routers/router_manager.rs)
 - [sgl-model-gateway/src/server.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/server.rs)
 - [sgl-model-gateway/src/service_discovery.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/service_discovery.rs)
 - [sgl-model-gateway/tests/common/redis_test_server.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/tests/common/redis_test_server.rs)
 - [sgl-model-gateway/tests/common/test_config.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/tests/common/test_config.rs)
 - [sgl-model-gateway/tests/routing/manual_routing_test.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/tests/routing/manual_routing_test.rs)
 - [sgl-model-gateway/tests/spec/embedding.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/tests/spec/embedding.rs)
 - [sgl-model-gateway/tests/spec/rerank.rs](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/tests/spec/rerank.rs)
 
  The SGLang Router (also known as the **SGLang Model Gateway** or `smg`) is a high-performance, Rust-based orchestration layer designed for large-scale LLM deployments. It centralizes worker lifecycle management, balances traffic across heterogeneous protocols (HTTP, gRPC, OpenAI-compatible), and provides enterprise-ready control over history storage, tool-use parsing, and privacy-sensitive workflows [sgl-model-gateway/Cargo.toml5-23](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/Cargo.toml#L5-L23)

 While deeply optimized for the SGLang serving runtime, the router is flexible enough to route requests to any OpenAI-compatible backend, providing features like Prefill-Decode (PD) disaggregation and cache-aware load balancing [sgl-model-gateway/src/main.rs86-114](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/main.rs#L86-L114)

 
## System Overview

 The router operates as a unified control and data plane for fleets of LLM workers. It is built to handle high-throughput scenarios where request latency and reliability are critical.

 
### Key Capabilities

 
 - **Multi-Protocol Routing**: Supports HTTP, gRPC, and OpenAI-compatible backends [sgl-model-gateway/src/server.rs172-205](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/server.rs#L172-L205)
 - **Load Balancing Policies**: Includes `random`, `round_robin`, `cache_aware`, `power_of_two`, `prefix_hash`, `bucket`, and `manual` [sgl-model-gateway/src/main.rs149-152](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/main.rs#L149-L152)
 - **PD Disaggregation**: Native support for splitting traffic between dedicated prefill and decode instances to optimize Time To First Token (TTFT) and throughput [sgl-model-gateway/src/main.rs98-105](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/main.rs#L98-L105)
 - **Reliability Primitives**: Built-in retries with exponential backoff, circuit breakers, and token-bucket rate limiting [sgl-model-gateway/src/core/worker.rs195-207](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/core/worker.rs#L195-L207) [sgl-model-gateway/src/middleware.rs29-47](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/middleware.rs#L29-L47)
 - **Rust-Native Pipeline**: High-performance pipeline with in-process tokenization and tool parsing using `llm-tokenizer`, `tool-parser`, and `reasoning-parser` [sgl-model-gateway/Cargo.toml82-85](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/Cargo.toml#L82-L85)
 - **Mesh Synchronization**: Supports cluster-wide state synchronization using CRDTs and Redis for distributed rate limiting and policy state [sgl-model-gateway/Cargo.toml123-124](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/Cargo.toml#L123-L124) [sgl-model-gateway/src/server.rs19-21](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/server.rs#L19-L21)
 - **WASM Middleware**: Supports custom request/response modification via a WebAssembly plugin system [sgl-model-gateway/src/server.rs68](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/server.rs#L68-L68) [sgl-model-gateway/src/middleware.rs37-46](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/middleware.rs#L37-L46)
 
 
### Component Architecture

 The following diagram illustrates the relationship between the Router's internal components and the external worker fleet.

 **Router Component Mapping**

 
```

```

 Sources: [sgl-model-gateway/src/server.rs70-78](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/server.rs#L70-L78) [sgl-model-gateway/src/routers/router_manager.rs1-15](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/routers/router_manager.rs#L1-L15) [sgl-model-gateway/src/core/worker.rs142-143](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/core/worker.rs#L142-L143)

 
## Core Components

 
### Experimental sgl-router: Slim KV-Aware Router

 SGLang maintains an experimental, slim router crate (located in `experimental/sgl-router`) designed for high-efficiency KV-aware routing. This implementation focuses on lightweight event-driven cache awareness, supporting Kubernetes `EndpointSlice` discovery and various load balancing policies such as `cache-aware-zmq`. It is optimized for scenarios requiring minimal overhead and tight integration with the KV-cache state of backend workers, often utilizing ZMQ for low-latency communication.

 For details, see [Experimental sgl-router: Slim KV-Aware Router](https://deepwiki.com/sgl-project/sglang/20.1-experimental-sgl-router:-slim-kv-aware-router).

 
### Router gRPC Pipeline and Tool Parsing

 The production router includes native support for advanced LLM features like function calling and reasoning. It utilizes specialized Rust crates to process model outputs in-flight [sgl-model-gateway/Cargo.toml82-85](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/Cargo.toml#L82-L85) This allows the router to separate reasoning content via `parse_reasoning` or extract tool calls via `parse_function_call` [sgl-model-gateway/src/server.rs80-92](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/server.rs#L80-L92) The pipeline also handles tokenization and detokenization directly in Rust to minimize overhead [sgl-model-gateway/src/server.rs51](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/server.rs#L51-L51) For high-throughput streaming, it uses a gRPC-based communication layer to reduce overhead compared to standard HTTP.

 For details, see [Router gRPC Pipeline and Tool Parsing](https://deepwiki.com/sgl-project/sglang/20.2-router-grpc-pipeline-and-tool-parsing).

 
## Deployment and CI/CD

 The router is distributed as a Rust crate with Python bindings. It provides multiple entry points including a CLI and library bindings.

 
| Deployment Method | Command / Entry Point | Primary Use Case |
|---|---|---|
| Rust Binary | cargo run --bin smg | High-performance production deployments sgl-model-gateway/Cargo.toml24-34 |
| CLI Launch | smg launch [OPTIONS] | Standard standalone orchestration sgl-model-gateway/src/main.rs127-130 |
| Python Bindings | maturin develop | Direct embedding in Python applications sgl-model-gateway/bindings/python/src/lib.rs1-6 |

 
### Performance and Observability

 The router project maintains a rigorous performance profile:

 
 - **Metrics Stack**: Features a Prometheus-compatible exporter for tracking HTTP, router, and worker metrics with string interning via `intern_string` to avoid allocations [sgl-model-gateway/src/observability/metrics.rs16-47](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/observability/metrics.rs#L16-L47)
 - **Tracing**: Integrates with OpenTelemetry for distributed tracing of requests through the gateway [sgl-model-gateway/src/main.rs15-18](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/main.rs#L15-L18)
 - **Benchmarks**: Continuous performance measurement for `consistent_hash_bench`, `wasm_middleware_latency`, and `request_processing` [sgl-model-gateway/Cargo.toml149-174](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/Cargo.toml#L149-L174)
 - **CI/CD**: The project uses GitHub Actions for automated testing, including linting, Rust unit tests, and performance benchmarks [.github/workflows/pr-benchmark-rust.yml1-20](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/pr-benchmark-rust.yml#L1-L20)
 
 **Entity Mapping: Configuration to Code**

 
```

```

 Sources: [sgl-model-gateway/src/main.rs133-210](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/main.rs#L133-L210) [sgl-model-gateway/src/server.rs70-78](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/server.rs#L70-L78) [sgl-model-gateway/bindings/python/src/lib.rs7-25](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/bindings/python/src/lib.rs#L7-L25)

 
## Hardware and Platform Support

 The router is designed to orchestrate SGLang workers across various backends, including `sglang`, `vllm`, `trtllm`, `openai`, and `anthropic` [sgl-model-gateway/src/main.rs56-67](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/main.rs#L56-L67) It manages worker health and readiness, specifically checking for the presence of both prefill and decode workers when operating in PD disaggregated mode [sgl-model-gateway/src/server.rs102-122](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/server.rs#L102-L122) While the router itself is CPU-bound and written in Rust, it is optimized to support workers running on diverse hardware (CUDA, ROCm, NPU, etc.) by abstracting the backend connection.

 Sources: [sgl-model-gateway/src/main.rs56-80](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/main.rs#L56-L80) [sgl-model-gateway/src/server.rs98-148](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/server.rs#L98-L148)
