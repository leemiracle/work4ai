> 来源: [https://deepwiki.com/sgl-project/sglang/21-sglang-model-gateway-%28sgl-model-gateway%29](https://deepwiki.com/sgl-project/sglang/21-sglang-model-gateway-%28sgl-model-gateway%29)
> DeepWiki sgl-project/sglang | Last indexed: 27 Aug 2026 (94183a)

# SGLang Model Gateway (sgl-model-gateway)

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
 
  The SGLang Model Gateway (`sgl-model-gateway`) is a high-performance, Rust-based inference gateway designed to sit in front of one or more SGLang (or other compatible) inference servers. It provides a unified entry point for LLM applications, offering advanced load balancing, request routing, and workflow orchestration.

 The gateway is built for high-concurrency scenarios, utilizing an asynchronous architecture powered by `tokio` and `axum` [sgl-model-gateway/src/server.rs9-22](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/server.rs#L9-L22) It supports multiple protocols, including OpenAI-compatible HTTP and high-throughput gRPC [sgl-model-gateway/src/routers/http/router.rs46-53](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/routers/http/router.rs#L46-L53)

 
### Core Components and Code Entities

 The following diagram illustrates the relationship between the gateway's natural language concepts and the specific Rust entities that implement them.

 **Gateway Entity Mapping**

 
```

```

 **Sources:** [sgl-model-gateway/src/server.rs71-78](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/server.rs#L71-L78) [sgl-model-gateway/src/routers/router_manager.rs1-20](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/routers/router_manager.rs#L1-L20) [sgl-model-gateway/src/policies/registry.rs1-20](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/policies/registry.rs#L1-L20) [sgl-model-gateway/src/core/worker_registry.rs179-199](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/core/worker_registry.rs#L179-L199) [sgl-model-gateway/src/observability/metrics.rs148-158](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/observability/metrics.rs#L148-L158)

 
---

 
## Gateway Architecture and Worker Management

 The gateway operates a centralized **Control Plane** managed via the `AppContext` [sgl-model-gateway/src/server.rs71-78](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/server.rs#L71-L78) This context coordinates the `WorkerRegistry`, which maintains a real-time view of all backend inference nodes.

 
 - **Worker Registry:** Manages a pool of `Worker` objects, indexing them by model ID, worker type (Regular, Prefill, or Decode), and connection mode (HTTP/gRPC) [sgl-model-gateway/src/core/worker_registry.rs179-199](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/core/worker_registry.rs#L179-L199) It uses immutable `Arc` snapshots for lock-free reads to ensure high-concurrency performance [sgl-model-gateway/src/core/worker_registry.rs5-7](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/core/worker_registry.rs#L5-L7)
 - **Circuit Breakers:** Each worker is protected by a `CircuitBreaker` that monitors success/failure rates and can "trip" to prevent routing requests to failing backends [sgl-model-gateway/src/core/worker.rs195-206](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/core/worker.rs#L195-L206)
 - **Service Discovery:** Supports dynamic worker registration through various backends, including Kubernetes and static CLI configurations [sgl-model-gateway/src/service_discovery.rs1-20](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/service_discovery.rs#L1-L20)
 - **Hash Ring:** Maintains a pre-computed `HashRing` per model using virtual nodes for stable consistent hashing via `blake3` [sgl-model-gateway/src/core/worker_registry.rs29-48](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/core/worker_registry.rs#L29-L48)
 
 For details, see [Gateway Architecture and Worker Management](https://deepwiki.com/sgl-project/sglang/21.1-gateway-architecture-and-worker-management).

 **Sources:** [sgl-model-gateway/src/core/worker_registry.rs179-199](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/core/worker_registry.rs#L179-L199) [sgl-model-gateway/src/core/worker.rs141-160](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/core/worker.rs#L141-L160) [sgl-model-gateway/src/core/worker_registry.rs5-13](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/core/worker_registry.rs#L5-L13) [sgl-model-gateway/src/core/worker_registry.rs29-48](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/core/worker_registry.rs#L29-L48) [sgl-model-gateway/src/server.rs71-78](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/server.rs#L71-L78)

 
---

 
## Routing Policies and Load Balancing

 The gateway's **Data Plane** uses a `PolicyRegistry` to determine how requests are distributed across workers [sgl-model-gateway/src/routers/http/router.rs46-53](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/routers/http/router.rs#L46-L53)

 
| Policy | Description | Key Code Entity |
|---|---|---|
| Cache-Aware | Routes based on prefix matching to maximize KV cache reuse using an approximate radix tree. | CacheAwarePolicy sgl-model-gateway/src/policies/cache_aware.rs111-116 |
| Power of Two | Selects two random workers and chooses the one with the lowest load. | PowerOfTwoPolicy sgl-model-gateway/src/main.rs150-151 |
| PD Routing | Disaggregates Prefill and Decode phases to different worker pools. | PDRouter sgl-model-gateway/src/routers/http/pd_router.rs48-55 |
| Consistent Hashing | Uses a pre-computed hash ring with virtual nodes for O(log n) worker selection. | HashRing sgl-model-gateway/src/core/worker_registry.rs43-50 |
| IGW Mode | Inference Gateway mode for multi-model routing in a single endpoint. | RouterConfig.enable_igw sgl-model-gateway/src/main.rs193-195 |

 **Request Routing Flow**

 
```

```

 **Sources:** [sgl-model-gateway/src/routers/http/router.rs133-191](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/routers/http/router.rs#L133-L191) [sgl-model-gateway/src/policies/cache_aware.rs111-157](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/policies/cache_aware.rs#L111-L157) [sgl-model-gateway/src/routers/http/pd_router.rs48-55](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/routers/http/pd_router.rs#L48-L55) [sgl-model-gateway/src/core/worker_registry.rs33-48](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/core/worker_registry.rs#L33-L48)

 For details, see [Routing Policies and Load Balancing](https://deepwiki.com/sgl-project/sglang/21.2-routing-policies-and-load-balancing).

 
---

 
## Workflow Engine and WASM Middleware

 Beyond simple routing, the gateway includes a **Workflow Engine** and a plugin system for request transformation.

 
 - **WASM Middleware:** Allows users to inject custom logic (e.g., authentication, logging, or prompt modification) using WebAssembly modules powered by `wasmtime` [sgl-model-gateway/Cargo.toml129](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/Cargo.toml#L129-L129) [sgl-model-gateway/src/server.rs68-69](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/server.rs#L68-L69)
 - **Conversation Connectors:** Manages chat templates and conversation state to ensure requests are formatted correctly [sgl-model-gateway/src/server.rs56](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/server.rs#L56-L56)
 - **MCP Integration:** Support for the Model Context Protocol (MCP) to bridge LLMs with external data sources and tools via `smg-mcp` and `rmcp` [sgl-model-gateway/Cargo.toml89](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/Cargo.toml#L89-L89) [sgl-model-gateway/Cargo.toml95](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/Cargo.toml#L95-L95)
 - **Job Queue:** Manages request concurrency and queuing through `JobQueue` and `TokenBucket` for rate limiting [sgl-model-gateway/src/server.rs30-36](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/server.rs#L30-L36) [sgl-model-gateway/src/middleware.rs29](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/middleware.rs#L29-L29)
 
 For details, see [Workflow Engine and WASM Middleware](https://deepwiki.com/sgl-project/sglang/21.3-workflow-engine-and-wasm-middleware).

 **Sources:** [sgl-model-gateway/src/server.rs67-69](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/server.rs#L67-L69) [sgl-model-gateway/src/middleware.rs37-46](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/middleware.rs#L37-L46) [sgl-model-gateway/Cargo.toml85-86](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/Cargo.toml#L85-L86) [sgl-model-gateway/src/server.rs68-69](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/server.rs#L68-L69) [sgl-model-gateway/src/middleware.rs29](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/middleware.rs#L29-L29)

 
---

 
## Observability and Performance

 The gateway is instrumented for high-performance monitoring and low-latency execution:

 
 - **Metrics:** Uses `metrics-exporter-prometheus` to track request latency (`smg_http_request_duration_seconds`), throughput, and worker health [sgl-model-gateway/src/observability/metrics.rs148-174](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/observability/metrics.rs#L148-L174)
 - **Tracing:** Integrated with OpenTelemetry for distributed tracing across the gateway and backend workers [sgl-model-gateway/Cargo.toml64-67](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/Cargo.toml#L64-L67)
 - **String Interning:** Uses a global `STRING_INTERNER` with `DashMap` for lock-free concurrent access to avoid repeated allocations for common labels like `model_id` [sgl-model-gateway/src/observability/metrics.rs26-35](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/observability/metrics.rs#L26-L35)
 - **Status Code Optimization:** Employs `status_code_to_static_str` to avoid allocations for common HTTP response codes [sgl-model-gateway/src/observability/metrics.rs73-92](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/observability/metrics.rs#L73-L92)
 - **Request ID Generation:** Generates OpenAI-compatible request IDs (e.g., `chatcmpl-...`, `gnt-...`) using an optimized byte-array indexing approach [sgl-model-gateway/src/middleware.rs153-178](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/middleware.rs#L153-L178)
 
 **Sources:** [sgl-model-gateway/src/observability/metrics.rs26-47](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/observability/metrics.rs#L26-L47) [sgl-model-gateway/src/observability/metrics.rs148-174](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/observability/metrics.rs#L148-L174) [sgl-model-gateway/src/observability/metrics.rs73-92](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/observability/metrics.rs#L73-L92) [sgl-model-gateway/src/middleware.rs153-178](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/src/middleware.rs#L153-L178)
