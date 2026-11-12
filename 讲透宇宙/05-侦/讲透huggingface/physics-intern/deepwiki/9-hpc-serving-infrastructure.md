<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/physics-intern · page 9 HPC Serving Infrastructure · fetched 2026-10-26 -->

# HPC Serving Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [serve/drain_backends.py](serve/drain_backends.py)
- [serve/load_balancer.py](serve/load_balancer.py)
- [serve/serve.slurm](serve/serve.slurm)

</details>



The PhysicsIntern codebase utilizes a robust, vLLM-based serving infrastructure designed for large-scale physics reasoning benchmarks on HPC clusters (specifically Slurm-managed H100 nodes). This infrastructure provides automated deployment, distributed inference, and a resilient load-balancing layer to handle the high throughput required by multi-agent research loops.

The stack is divided into two primary components: the **vLLM Serve Scripts** for managing individual model instances, and the **Load Balancer** for orchestrating a pool of replicas.

## High-Level Serving Architecture

The following diagram illustrates the relationship between the evaluation jobs, the load balancer, and the distributed vLLM backends.

**Serving Stack Overview**
```mermaid
graph TD
    subgraph "Slurm Evaluation Job"
        [Batch_Runner] --> |"localhost:9000"| [load_balancer.py]
    end

    subgraph "Distributed vLLM Replicas (Slurm Jobs)"
        [load_balancer.py] --> |"Round Robin /v1"| B1["serve.slurm (Replica 1)"]
        [load_balancer.py] --> |"Round Robin /v1"| B2["serve.slurm (Replica 2)"]
        [load_balancer.py] --> |"Round Robin /v1"| B3["serve.slurm (Replica N)"]
    end

    B1 --> |"TP/PP"| G1["H100 GPUs"]
    B2 --> |"TP/PP"| G2["H100 GPUs"]
    B3 --> |"TP/PP"| G3["H100 GPUs"]

    [load_balancer.py] -.-> |"squeue/scancel"| B1
    [load_balancer.py] -.-> |"sbatch"| B1
```
Sources: [serve/serve.slurm:1-81](), [serve/load_balancer.py:1-20]()

## vLLM Serve Scripts

The `serve.slurm` script is the core entry point for deploying models. It is designed to be "self-submitting," meaning it can be executed directly as a shell script, which then calculates required resources and submits itself to Slurm via `sbatch` [serve/serve.slurm:74-81]().

Key features include:
*   **Distributed Launch Sequence**: Supports Tensor Parallelism (TP), Pipeline Parallelism (PP), and Data Parallelism (DP) configurations [serve/serve.slurm:40-55]().
*   **Idle Watchdog**: A background process monitors the `/metrics` endpoint and automatically cancels the Slurm job if the server remains idle for a configurable period (default 2 hours) [serve/serve.slurm:57-59](), [serve/serve.slurm:197-204]().
*   **Self-Healing**: Includes a `max-restarts` mechanism to recover from vLLM crashes without losing the Slurm allocation [serve/serve.slurm:60-61]().
*   **Multi-Replica Dispatch**: The `multi_serve.sh` script (invoked by `serve.slurm`) can launch multiple replicas across different Slurm Quality of Service (QOS) levels, such as combining high-priority "normal" replicas with "low" priority preemptible ones [serve/serve.slurm:64-69]().

For details on configuration and distributed launch logic, see [vLLM Serve Scripts](#9.1).

Sources: [serve/serve.slurm:19-81](), [serve/serve.slurm:197-210]()

## Load Balancer and Management

The `load_balancer.py` script acts as a resilient proxy that sits between the PhysicsIntern agents and the vLLM backends. It exposes an OpenAI-compatible API and distributes requests across the healthy pool of Slurm jobs.

**Code Entity Mapping: Load Balancer Internals**
```mermaid
graph LR
    subgraph "load_balancer.py"
        [BackendPool] --> |"tracks"| [Backend]
        [BackendPool] --> |"vends"| [BackendLease]
        [BackendPool] -.-> |"monitors"| [get_slurm_job_state]
        [BackendPool] -.-> |"recovers"| [resubmit_serve_job]
    end

    [BackendPool] -- "HTTP Proxy" --> VLLM["vLLM Endpoint"]
```
Sources: [serve/load_balancer.py:51-66](), [serve/load_balancer.py:102-142](), [serve/load_balancer.py:160-178](), [serve/load_balancer.py:219-225]()

### Key Capabilities
*   **Backend Pool Management**: The `BackendPool` class tracks the health and request load of every `Backend` [serve/load_balancer.py:219-225]().
*   **Auto-Resubmission**: If a backend job fails or is cancelled, the load balancer can automatically call `resubmit_serve_job` to maintain the desired replica count [serve/load_balancer.py:102-142]().
*   **Graceful Draining**: The `drain_backends.py` utility allows administrators to signal a backend to stop accepting new requests and shut down only after finishing in-flight work [serve/drain_backends.py:85-91]().
*   **Evaluation Integration**: Slurm evaluation jobs (e.g., `full_eval.slurm`) typically launch the load balancer within their own allocation to provide a stable endpoint for the duration of the benchmark [serve/drain_backends.py:21-52]().

For details on the round-robin logic and self-healing mechanisms, see [Load Balancer and Evaluation Slurm Jobs](#9.2).

Sources: [serve/load_balancer.py:1-20](), [serve/load_balancer.py:150-178](), [serve/drain_backends.py:1-13]()

## Summary of Components

| Component | File | Role |
| :--- | :--- | :--- |
| **Serve Script** | `serve/serve.slurm` | Main entry point for launching a vLLM instance on Slurm. |
| **Load Balancer** | `serve/load_balancer.py` | Round-robin proxy with auto-resubmit and health checks. |
| **Drain Utility** | `serve/drain_backends.py` | CLI tool to gracefully decommission backends. |
| **Replica Manager** | `serve/multi_serve.sh` | Orchestrates multiple `serve.slurm` instances for DP. |

Sources: [serve/serve.slurm:1-13](), [serve/load_balancer.py:1-20](), [serve/drain_backends.py:1-13]()

---

