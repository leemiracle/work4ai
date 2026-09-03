# router

> 来源: https://deepwiki.com/vllm-project/router 抓取日期: 2026-09-02（overview 级摘要）

---

Overview

# Overview

Relevant source files

  * [.buildkite/build-wheel.sh](https://github.com/vllm-project/router/blob/eb57b66b/.buildkite/build-wheel.sh)
  * [Cargo.lock](https://github.com/vllm-project/router/blob/eb57b66b/Cargo.lock)
  * [Cargo.toml](https://github.com/vllm-project/router/blob/eb57b66b/Cargo.toml)
  * [README.md](https://github.com/vllm-project/router/blob/eb57b66b/README.md?plain=1)
  * [py_src/vllm_router/version.py](https://github.com/vllm-project/router/blob/eb57b66b/py_src/vllm_router/version.py)
  * [pyproject.toml](https://github.com/vllm-project/router/blob/eb57b66b/pyproject.toml)
  * [src/lib.rs](https://github.com/vllm-project/router/blob/eb57b66b/src/lib.rs)

## Purpose and Scope

The vLLM Router is a high-performance request routing system designed for large-scale vLLM deployments. It acts as an intelligent proxy between clients and vLLM worker instances, providing advanced load balancing, fault tolerance, and specialized routing capabilities for modern LLM serving architectures.

The project is built as a hybrid system with a performance-critical Rust core and Python bindings, allowing it to be used as a standalone binary or integrated into Python-based AI infrastructure.

This page provides a high-level introduction to the system's purpose, architecture, and operational modes. For detailed information about specific subsystems:

  * Architecture details and component interactions: [Architecture](/vllm-project/router/1.1-architecture)
  * Technology choices and dependencies: [Technology Stack](/vllm-project/router/1.2-technology-stack)
  * Routing logic and worker selection: [Routing Architecture](/vllm-project/router/3-routing-architecture)
  * Prefill-Decode disaggregation specifics: [Prefill-Decode Disaggregation](/vllm-project/router/4-prefill-decode-disaggregation)
  * Kubernetes-native service discovery: [Worker Management](/vllm-project/router/5-worker-management)
  * Fault tolerance and resilience: [Resilience & Reliability](/vllm-project/router/6-resilience-and-reliability)

**Sources:** [README.md1-11](https://github.com/vllm-project/router/blob/eb57b66b/README.md?plain=1#L1-L11) [pyproject.toml5-12](https://github.com/vllm-project/router/blob/eb57b66b/pyproject.toml#L5-L12)

## Core Capabilities

The vLLM Router provides three primary capabilities:

Capability| Description| Configuration Flag  
---|---|---  
**Load Balancing**|  Distributes requests across worker pools using multiple algorithms (round_robin, random, consistent_hash, power_of_two, cache_aware)| `--policy`  
**PD Disaggregation**|  Routes prefill and decode phases to separate worker pools for specialized hardware utilization| `--vllm-pd-disaggregation`  
**Service Discovery**|  Automatically discovers and monitors vLLM workers in Kubernetes clusters via pod watching| `--service-discovery`  
  
Additional enterprise features include circuit breakers for fault isolation, automatic retry logic with exponential backoff, Prometheus metrics export, and distributed request ID tracking.

**Sources:** [README.md5-11](https://github.com/vllm-project/router/blob/eb57b66b/README.md?plain=1#L5-L11) [src/lib.rs21-29](https://github.com/vllm-project/router/blob/eb57b66b/src/lib.rs#L21-L29) [src/lib.rs70-82](https://github.com/vllm-project/router/blob/eb57b66b/src/lib.rs#L70-L82)

## System Architecture Overview

The following diagram shows how the router fits between clients and vLLM backend workers:

Title: vLLM Router System Overview

The `Server` component manages HTTP endpoints. The `RouterManager` instantiates the appropriate router based on operational mode: `OpenAIRouter` for standard routing or `PDRouter` for PD disaggregation. Each router applies load balancing policies from the `policies` module to select workers tracked by `WorkerRegistry`. The `CircuitBreaker` wraps worker requests for fault isolation, while `ServiceDiscovery` updates the registry when Kubernetes pods change.

**Sources:** [src/server.rs1-100](https://github.com/vllm-project/router/blob/eb57b66b/src/server.rs#L1-L100) [src/routers/router_manager.rs1-50](https://github.com/vllm-project/router/blob/eb57b66b/src/routers/router_manager.rs#L1-L50) [src/routers/http/openai_router.rs1-50](https://github.com/vllm-project/router/blob/eb57b66b/src/routers/http/openai_router.rs#L1-L50) [src/core/worker_registry.rs1-50](https://github.com/vllm-project/router/blob/eb57b66b/src/core/worker_registry.rs#L1-L50) [src/service_discovery.rs1-50](https://github.com/vllm-project/router/blob/eb57b66b/src/service_discovery.rs#L1-L50)

## Operational Modes

The router supports three distinct operational modes:

### Standard Routing Mode

In standard mode, the router forwards requests to a pool of homogeneous vLLM workers. Each worker serves the complete request lifecycle (prefill and decode phases).

Title: Standard Routing Flow

Configuration example:

**Sources:** [README.md58-65](https://github.com/vllm-project/router/blob/eb57b66b/README.md?plain=1#L58-L65) [src/lib.rs143-147](https://github.com/vllm-project/router/blob/eb57b66b/src/lib.rs#L143-L147)

### Data Parallel (DP) Routing Mode

When `--intra-node-data-parallel-size` is set to a value greater than 1, the router creates replica-aware workers. Each worker URL is expanded into N replicas (e.g., `worker1:8000` becomes `worker1:8000` with `X-Data-Parallel-Rank` headers for each rank).

**Sources:** [README.md58-78](https://github.com/vllm-project/router/blob/eb57b66b/README.md?plain=1#L58-L78) [src/lib.rs187](https://github.com/vllm-project/router/blob/eb57b66b/src/lib.rs#L187-L187)

### Prefill-Decode (PD) Disaggregation Mode

In PD mode (`--vllm-pd-disaggregation`), the router separates prefill and decode phases, routing them to specialized worker pools. This enables optimal hardware utilization by assigning compute-intensive prefill to high-throughput GPUs and memory-bandwidth-limited decode to high-capacity GPUs.

Title: PD Disaggregation Routing

**Sources:** [README.md80-124](https://github.com/vllm-project/router/blob/eb57b66b/README.md?plain=1#L80-L124) [src/lib.rs135-142](https://github.com/vllm-project/router/blob/eb57b66b/src/lib.rs#L135-L142)

## Hybrid Rust/Python Architecture

The system employs a hybrid architecture with a performance-critical Rust core wrapped by a Python layer for ecosystem compatibility.

Title: Hybrid Architecture and Code Mapping

The Rust core is compiled as both a shared library for Python FFI and a standalone executable.

  * **`cdylib`** : Shared library for Python FFI via `pyo3` [Cargo.toml6-10](https://github.com/vllm-project/router/blob/eb57b66b/Cargo.toml#L6-L10)
  * **`bin`** : Standalone executable `vllm-router` [Cargo.toml12-14](https://github.com/vllm-project/router/blob/eb57b66b/Cargo.toml#L12-L14)

**Sources:** [Cargo.toml1-15](https://github.com/vllm-project/router/blob/eb57b66b/Cargo.toml#L1-L15) [src/lib.rs31-33](https://github.com/vllm-project/router/blob/eb57b66b/src/lib.rs#L31-L33) [pyproject.toml35-36](https://github.com/vllm-project/router/blob/eb57b66b/pyproject.toml#L35-L36)

## Request Flow and Resilience

The router implements defense-in-depth resilience patterns including circuit breakers and retries.

**Circuit Breaker States** [src/lib.rs77-82](https://github.com/vllm-project/router/blob/eb57b66b/src/lib.rs#L77-L82):

  * **Closed** : Normal operation, requests pass through.
  * **Open** : Fast-fail mode after reaching `cb_failure_threshold`.
  * **HalfOpen** : Test mode after `cb_timeout_duration_secs` to check if worker recovered.

**Retry Policy** [src/lib.rs70-76](https://github.com/vllm-project/router/blob/eb57b66b/src/lib.rs#L70-L76):

  * Retries on specific HTTP status codes (408, 429, 500, 502, 503, 504).
  * Uses exponential backoff with jitter to prevent thundering herd problems.

**Sources:** [README.md153-185](https://github.com/vllm-project/router/blob/eb57b66b/README.md?plain=1#L153-L185) [src/lib.rs70-82](https://github.com/vllm-project/router/blob/eb57b66b/src/lib.rs#L70-L82)

## Protocol and Metrics

### HTTP Interface

The router serves OpenAI-compatible endpoints including `/v1/chat/completions` and `/v1/completions`. It handles both streaming and non-streaming responses.

### Metrics Interface

Prometheus metrics are exposed by default (typically on port 29000). These metrics track request latency, worker health, and routing decisions.

**Sources:** [README.md141-151](https://github.com/vllm-project/router/blob/eb57b66b/README.md?plain=1#L141-L151) [src/lib.rs59-60](https://github.com/vllm-project/router/blob/eb57b66b/src/lib.rs#L59-L60) [src/lib.rs168-175](https://github.com/vllm-project/router/blob/eb57b66b/src/lib.rs#L168-L175)
