<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/llm-42 · page 9 sgl-model-gateway: Routing and Load Balancing · fetched 2026-10-26 -->

# sgl-model-gateway: Routing and Load Balancing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/pr-benchmark-rust.yml](.github/workflows/pr-benchmark-rust.yml)
- [.github/workflows/pr-test-rust.yml](.github/workflows/pr-test-rust.yml)
- [docs/advanced_features/sgl_model_gateway.md](docs/advanced_features/sgl_model_gateway.md)
- [sgl-model-gateway/Cargo.toml](sgl-model-gateway/Cargo.toml)
- [sgl-model-gateway/README.md](sgl-model-gateway/README.md)
- [sgl-model-gateway/bindings/python/src/lib.rs](sgl-model-gateway/bindings/python/src/lib.rs)
- [sgl-model-gateway/bindings/python/src/sglang_router/router.py](sgl-model-gateway/bindings/python/src/sglang_router/router.py)
- [sgl-model-gateway/bindings/python/src/sglang_router/router_args.py](sgl-model-gateway/bindings/python/src/sglang_router/router_args.py)
- [sgl-model-gateway/build.rs](sgl-model-gateway/build.rs)
- [sgl-model-gateway/e2e_test/router/test_worker_api.py](sgl-model-gateway/e2e_test/router/test_worker_api.py)
- [sgl-model-gateway/src/config/builder.rs](sgl-model-gateway/src/config/builder.rs)
- [sgl-model-gateway/src/config/types.rs](sgl-model-gateway/src/config/types.rs)
- [sgl-model-gateway/src/config/validation.rs](sgl-model-gateway/src/config/validation.rs)
- [sgl-model-gateway/src/core/circuit_breaker.rs](sgl-model-gateway/src/core/circuit_breaker.rs)
- [sgl-model-gateway/src/core/worker.rs](sgl-model-gateway/src/core/worker.rs)
- [sgl-model-gateway/src/core/worker_builder.rs](sgl-model-gateway/src/core/worker_builder.rs)
- [sgl-model-gateway/src/core/worker_registry.rs](sgl-model-gateway/src/core/worker_registry.rs)
- [sgl-model-gateway/src/lib.rs](sgl-model-gateway/src/lib.rs)
- [sgl-model-gateway/src/main.rs](sgl-model-gateway/src/main.rs)
- [sgl-model-gateway/src/middleware.rs](sgl-model-gateway/src/middleware.rs)
- [sgl-model-gateway/src/observability/metrics.rs](sgl-model-gateway/src/observability/metrics.rs)
- [sgl-model-gateway/src/policies/bucket.rs](sgl-model-gateway/src/policies/bucket.rs)
- [sgl-model-gateway/src/policies/cache_aware.rs](sgl-model-gateway/src/policies/cache_aware.rs)
- [sgl-model-gateway/src/policies/factory.rs](sgl-model-gateway/src/policies/factory.rs)
- [sgl-model-gateway/src/policies/manual.rs](sgl-model-gateway/src/policies/manual.rs)
- [sgl-model-gateway/src/policies/mod.rs](sgl-model-gateway/src/policies/mod.rs)
- [sgl-model-gateway/src/policies/power_of_two.rs](sgl-model-gateway/src/policies/power_of_two.rs)
- [sgl-model-gateway/src/policies/random.rs](sgl-model-gateway/src/policies/random.rs)
- [sgl-model-gateway/src/policies/registry.rs](sgl-model-gateway/src/policies/registry.rs)
- [sgl-model-gateway/src/policies/round_robin.rs](sgl-model-gateway/src/policies/round_robin.rs)
- [sgl-model-gateway/src/routers/grpc/client.rs](sgl-model-gateway/src/routers/grpc/client.rs)
- [sgl-model-gateway/src/routers/grpc/common/stages/worker_selection.rs](sgl-model-gateway/src/routers/grpc/common/stages/worker_selection.rs)
- [sgl-model-gateway/src/routers/http/pd_router.rs](sgl-model-gateway/src/routers/http/pd_router.rs)
- [sgl-model-gateway/src/routers/http/router.rs](sgl-model-gateway/src/routers/http/router.rs)
- [sgl-model-gateway/tests/common/mock_worker.rs](sgl-model-gateway/tests/common/mock_worker.rs)
- [sgl-model-gateway/tests/common/test_config.rs](sgl-model-gateway/tests/common/test_config.rs)
- [sgl-model-gateway/tests/routing/manual_routing_test.rs](sgl-model-gateway/tests/routing/manual_routing_test.rs)

</details>



The **sgl-model-gateway** is a Rust-based model gateway designed to orchestrate large-scale deployments of large language model (LLM) workers. It serves as a sophisticated routing and load balancing layer that manages fleets of backend workers running various model types, interfaces with multiple communication protocols (HTTP, gRPC, and PD-prefill/decode modes), and applies flexible load balancing policies for optimal utilization and reliability.

This page offers a high-level overview of the gateway’s core concepts, architecture, and responsibilities, emphasizing how routing and load balancing are performed at scale. For detailed information on the gateway’s architecture and routing policies, PD disaggregation routing, and observability aspects, please refer to the child pages [Gateway Architecture and Routing Policies](#9.1) and [Gateway PD Disaggregation and Observability](#9.2).

---

## Gateway Purpose and Scope

The sgl-model-gateway primarily functions as:

- **Control Plane:** Managing worker registration, health checks, circuit breaker state, and maintaining an up-to-date view of worker availability and capabilities.
- **Data Plane:** Routing incoming requests from clients to appropriate workers according to model ID, connection mode, request context, and load balancing policies.
- **Reliability Layer:** Implementing retry mechanisms, token bucket rate limiting, queuing, and circuit breaker controls to deliver robustness.
- **Observability Endpoint:** Emitting rich Prometheus metrics and OpenTelemetry traces that cover HTTP and gRPC ingress, worker load, routing decisions, and error conditions.

These responsibilities enable efficient execution of inference requests against backend LLM workers in diverse deployment topologies, including multi-model fleets, segmented prefill/decode pipelines, and hybrid HTTP/gRPC protocols.

---

## Core Components Overview

### Worker Registry

At the core is the **Worker Registry**, a centralized registry that tracks all active workers, indexing them by model, worker type (regular, prefill, decode), and connection mode (HTTP, gRPC). To maximize concurrency, the registry uses immutable snapshots (`Arc` snapshots) of worker lists for each model, enabling lock-free read access even under high load.

Additionally, it maintains **consistent hash rings** per model, with virtual nodes per physical worker (typically 150) for even key distribution and efficient O(log n) lookup during routing. This setup supports routing strategies that rely on consistent hashing for cache affinity and sticky session policies.

### Router Implementations

Requests received by the gateway are routed through specialized router implementations:

- **HTTP Router:** Handles HTTP traffic with integrated load balancing, circuit breaking, and retries. It filters available workers by model and connection mode, then selects a backend using the configured load balancing policy.
- **PD Router:** A dedicated router handling the prefill/decode disaggregation pattern, routing prefill requests separately from decode requests, supporting batch sizes and streaming flags.
- **gRPC Router:** Implements a tokenized gRPC request pipeline with full support for streaming responses, token-level reasoning, and OpenAI-compatible protocols.

The gateway supports multi-router coordination via the **Router Manager**, especially in "multi-model inference gateway" (`--enable-igw`) mode, which runs several routers in parallel and applies per-model routing policies.

### Load Balancing Policies

The gateway supports configurable load balancing policies selectable per model. Core policies include:

- **Random:** Picks an available worker at random.
- **Round Robin:** Cycles through available workers evenly.
- **Cache Aware:** Combines cache affinity routing using approximate radix trees with load-aware switching to shortest queue routing under imbalance.
- **Power of Two Choices:** Picks the better among two randomly sampled workers.
- **Tree-Based:** Uses hierarchical prefix matching structures for routing affinity.

These policies implement asynchronous selection logic considering request text, token contexts (where available), and headers. The policy registry allows defining model-specific policies transparently.  

### Circuit Breaker and Retry Integration

Each worker has an associated circuit breaker tracking consecutive success or failure outcomes. Only workers with closed or half-open circuit breakers, and marked healthy, are considered available for routing. The retry executor transparently retries failed requests against alternative workers within configured bounds and backoff strategies.

### Observability and Metrics

The gateway features extensive observability instrumentation:

- **Prometheus Metrics:** Including HTTP request counts and durations, router-level routing events, upstream worker response statuses, circuit breaker states, and retry statistics. Metrics use string interning to minimize allocation overhead.
- **OpenTelemetry Tracing:** Distributed tracing with context propagation, enabling detailed request flow tracking.
- **Structured Logging:** Request ID propagation and event-based logging augment debugging.

These observability features allow deep insight into traffic patterns, load balancing efficiency, and failure modes.

---

## Architecture Diagrams

```mermaid
flowchart TD
  subgraph Client
    O[Client Request]
  end
  subgraph Gateway ["sgl-model-gateway (Rust)"]
    WReg[Worker Registry]
    RouterMgr[Router Manager]
    PolicyReg[Policy Registry]
    HLBR[Load Balancer Policy (e.g. CacheAwarePolicy)]
    CircuitBrk[Circuit Breakers per Worker]
    RetryExec[Retry Executor]
    Observ[Observability (Metrics & Traces)]
    
    O --> RouterMgr
    RouterMgr -->|Lookup model workers| WReg
    RouterMgr -->|Select policy| PolicyReg
    PolicyReg --> HLBR
    HLBR -->|Select worker| WReg
    WReg --> CircuitBrk
    RouterMgr --> RetryExec
    RouterMgr --> Observ
  end
  subgraph Workers ["Model Workers"]
    Worker1["Worker #1"]
    Worker2["Worker #2"]
    WorkerN["Worker #N"]
  end
  RouterMgr -->|Route request| Worker1 & Worker2 & WorkerN
```

*Diagram 1: High-Level Gateway Routing Flow and Core Components*

```mermaid
flowchart TD
  subgraph Code_Entities
    WR[WorkerRegistry (core/worker_registry.rs)]
    RRouter[HTTP Router (routers/http/router.rs)]
    PDRouter[PDRouter (routers/http/pd_router.rs)]
    PolicyReg[PolicyRegistry (policies/registry.rs)]
    CacheAware[CacheAwarePolicy (policies/cache_aware.rs)]
    CircuitBrk[CircuitBreaker (core/circuit_breaker.rs)]
    Metrics[Metrics (observability/metrics.rs)]
  end
  WR --> |Provides workers & hash rings| RRouter
  WR --> |Provides prefill/decode workers| PDRouter
  RRouter --> |Uses policy| PolicyReg
  PolicyReg --> |Contains| CacheAware
  RRouter --> |Checks & updates| CircuitBrk
  PDRouter --> |Uses HTTP client for routing| WR
  RRouter & PDRouter --> |Emit metrics| Metrics
```

*Diagram 2: Mapping Gateway System Names to Code Entities*

---

## How These Components Relate

- The **Worker Registry** acts as the source of truth for which backend workers exist, their health, connection modes, and their consistent hash rings used in routing strategies.
- The **Routers** consult the Worker Registry and the **Policy Registry** to pick workers according to the current policy for the request's model.
- Load balancing policies, such as the **CacheAwarePolicy**, leverage internal data structures (e.g., radix trees) to route based on cache affinity and request characteristics while balancing load between workers.
- The **Circuit Breaker** logic wraps availability checks to avoid sending traffic to unhealthy workers.
- The **Retry Executor** is integrated within routers to transparently handle retryable failures.
- The **Observability** subsystem collects runtime metrics for HTTP requests, routing decisions, worker load, and errors, feeding Prometheus and OpenTelemetry.

This modular architecture enables flexible customization and scaling of routing logic while maintaining reliability and observability.

---

## Deployment Modes and Flexibility

The gateway supports:

- **Multi-model routing** via `enable_igw` flag: running multiple routers concurrently with per-model policies.
- **Prefill/Decode Disaggregation:** splitting prefill (memory-heavy initial token generation) and decode (streaming token completion) across separate workers and routing paths.
- **Multiple Protocols:** seamless routing across HTTP and gRPC workers, including the specialized PD routing.
- **Policy Pluggability:** plugging in new load balancing policies or customizing existing ones for sophisticated deployment needs.
- **Python Bindings:** exposing routing functionality via Python for custom integration and orchestration.

---

## Links to Child Pages for Details

For the in-depth technical details on the topics introduced here, please refer directly to the child pages:

- **[Gateway Architecture and Routing Policies](#9.1)**  
  Covers the Worker Registry internals, job queue management, circuit breaker implementation, and a comprehensive overview of supported load balancing policies including random, round robin, cache-aware, power of two choices, and tree-based policies. Also details HTTP and gRPC router implementations.

- **[Gateway PD Disaggregation and Observability](#9.2)**  
  Explains the architecture for PD (prefill/decode) routing in the gateway, how the specialized `pd_router.rs` handles requests, Python bindings under `sglang_router`, and how Prometheus metrics and OpenTelemetry tracing are integrated. Includes coverage of the end-to-end test infrastructure validating gateway functionality.

---

# Summary Table of Key Gateway Subsystems

| Subsystem           | Responsibility                                  | Primary Code Files                                  |
|---------------------|------------------------------------------------|---------------------------------------------------|
| Worker Registry     | Central storage and indexing of backend workers | `src/core/worker_registry.rs`                      |
| Router Manager      | Coordinates routing across multiple router types | `src/routers/mod.rs` (implied), `src/main.rs`     |
| HTTP Router          | Route HTTP-based requests to workers             | `src/routers/http/router.rs`                       |
| PD Router            | Prefill/decode request routing                    | `src/routers/http/pd_router.rs`                    |
| Load Balancing Policies | Worker selection strategies, e.g., cache-aware    | `src/policies/cache_aware.rs`, `src/policies/*.rs`|
| Circuit Breakers     | Health and failure tracking for workers           | `src/core/circuit_breaker.rs`, `src/core/worker.rs` |
| Retry Executor       | Reliable request retries                            | Scattered in router logic                          |
| Observability        | Metrics and tracing instrumentation                | `src/observability/metrics.rs`, tracing subsystems |
| Python Bindings      | Python-friendly router interface                    | `bindings/python/`                                 |

---

# References

- Worker Registry and consistent hash ring: `src/core/worker_registry.rs:1-262`  
- HTTP Router implementation and worker selection: `src/routers/http/router.rs:1-~`  
- PD Router for prefill/decode routing: `src/routers/http/pd_router.rs:1-~`  
- Cache-Aware load balancing policy: `src/policies/cache_aware.rs:1-~`  
- Circuit Breaker and Worker abstractions: `src/core/worker.rs:1-~`  
- Prometheus metrics definitions and observability: `src/observability/metrics.rs:1-~`  
- Build and CI workflows ensure correctness and benchmarking: `.github/workflows/pr-test-rust.yml:1-~`  

Sources:  
`sgl-model-gateway/src/core/worker_registry.rs`,  
`sgl-model-gateway/src/routers/http/router.rs`,  
`sgl-model-gateway/src/routers/http/pd_router.rs`,  
`sgl-model-gateway/src/policies/cache_aware.rs`,  
`sgl-model-gateway/src/core/worker.rs`,  
`sgl-model-gateway/src/observability/metrics.rs`,  
`.github/workflows/pr-test-rust.yml`

---

