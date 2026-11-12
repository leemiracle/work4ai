<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/inference-benchmarker · page 4 Deployment Options · fetched 2026-10-26 -->

# Deployment Options

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [Makefile](Makefile)
- [README.md](README.md)

</details>



This page provides an overview of the different deployment methods available for the inference-benchmarker system. The benchmarker is designed to run in various environments, from local development setups to large-scale HPC clusters, enabling performance testing across different infrastructure configurations.

For detailed information about specific deployment methods, see [Docker Deployment](#4.1), [Kubernetes Deployment](#4.2), and [HPC and Slurm Deployment](#4.3). For information about analyzing results from deployed benchmarks, see [Results Analysis and Visualization](#5).

## Deployment Architecture Overview

The inference-benchmarker supports multiple deployment strategies, each optimized for different use cases and infrastructure requirements:

```mermaid
graph TB
    subgraph "Source_Code"
        RUST_SRC["Rust Source Code<br/>(cargo build)"]
        DOCKERFILE["Dockerfile<br/>(Multi-stage build)"]
        HELM_CHART["Helm Chart<br/>(extra/k8s/inference-benchmarker)"]
        SLURM_SCRIPTS["Slurm Scripts<br/>(extra/slurm)"]
    end
    
    subgraph "Build_Artifacts"
        BINARY["inference-benchmarker<br/>(Native Binary)"]
        CONTAINER["Container Image<br/>(ghcr.io registry)"]
        HELM_PACKAGE["Helm Package<br/>(Kubernetes manifest)"]
    end
    
    subgraph "Runtime_Environments"
        LOCAL["Local Machine<br/>(Direct execution)"]
        DOCKER_LOCAL["Docker Desktop<br/>(Container runtime)"]
        K8S_CLUSTER["Kubernetes Cluster<br/>(Pod orchestration)"]
        SLURM_CLUSTER["HPC Cluster<br/>(Job scheduling)"]
    end
    
    subgraph "Target_Services"
        TGI_SERVER["TGI Server<br/>(text-generation-inference)"]
        VLLM_SERVER["vLLM Server<br/>(vllm-openai)"]
        OPENAI_API["OpenAI Compatible API<br/>(http endpoints)"]
    end
    
    RUST_SRC --> BINARY
    DOCKERFILE --> CONTAINER
    HELM_CHART --> HELM_PACKAGE
    
    BINARY --> LOCAL
    CONTAINER --> DOCKER_LOCAL
    CONTAINER --> K8S_CLUSTER
    CONTAINER --> SLURM_CLUSTER
    HELM_PACKAGE --> K8S_CLUSTER
    SLURM_SCRIPTS --> SLURM_CLUSTER
    
    LOCAL --> TGI_SERVER
    DOCKER_LOCAL --> TGI_SERVER
    K8S_CLUSTER --> VLLM_SERVER
    SLURM_CLUSTER --> OPENAI_API
```

Sources: [README.md:50-240](), [Dockerfile:1-14]()

## Deployment Methods Comparison

| Method | Use Case | Prerequisites | Scalability | Complexity |
|--------|----------|---------------|-------------|------------|
| **Local Binary** | Development, quick testing | Rust toolchain or pre-built binary | Single machine | Low |
| **Docker** | Consistent environments, CI/CD | Docker runtime | Single machine | Low |
| **Kubernetes** | Production workloads, auto-scaling | K8s cluster, Helm | High | Medium |
| **HPC/Slurm** | Large-scale research, batch jobs | Slurm cluster access | Very High | High |

## Installation Methods

### Binary Installation

The benchmarker can be installed directly as a native binary:

```bash
# Via cargo (requires Rust toolchain)
cargo install --git https://github.com/huggingface/inference-benchmarker/

# Or download pre-built release
curl -L https://github.com/huggingface/inference-benchmarker/releases/latest
```

### Container Image

The system provides containerized deployment through a multi-stage Docker build:

```mermaid
graph LR
    subgraph "Build_Stage"
        RUST_BASE["rust:1-bullseye"]
        CARGO_INSTALL["cargo install --path ."]
    end
    
    subgraph "Runtime_Stage"
        DEBIAN_BASE["debian:bullseye-slim"]
        CA_CERTS["ca-certificates"]
        WORKDIR["/opt/inference-benchmarker"]
        RESULTS_DIR["/opt/inference-benchmarker/results"]
    end
    
    RUST_BASE --> CARGO_INSTALL
    CARGO_INSTALL --> DEBIAN_BASE
    DEBIAN_BASE --> CA_CERTS
    CA_CERTS --> WORKDIR
    WORKDIR --> RESULTS_DIR
```

Sources: [README.md:54-61](), [Dockerfile:1-14]()

## Configuration and Execution Patterns

### Command Interface Consistency

Regardless of deployment method, the benchmarker maintains a consistent CLI interface:

```mermaid
graph TD
    subgraph "CLI_Parameters"
        TOKENIZER["--tokenizer-name<br/>(HuggingFace model ID)"]
        URL["--url<br/>(Target server endpoint)"]
        PROFILE["--profile<br/>(chat, code-generation, etc.)"]
        BENCHMARK_KIND["--benchmark-kind<br/>(sweep, rate, throughput)"]
        DURATION["--duration<br/>(Benchmark duration)"]
        OUTPUT["JSON Results<br/>(Structured output)"]
    end
    
    subgraph "Deployment_Targets"
        LOCAL_EXEC["Local: inference-benchmarker"]
        DOCKER_EXEC["Docker: docker run <image>"]
        K8S_EXEC["K8s: kubectl/helm"]
        SLURM_EXEC["Slurm: sbatch"]
    end
    
    TOKENIZER --> LOCAL_EXEC
    URL --> DOCKER_EXEC
    PROFILE --> K8S_EXEC
    BENCHMARK_KIND --> SLURM_EXEC
    DURATION --> OUTPUT
```

Sources: [README.md:93-148]()

## Resource and Networking Requirements

### Network Connectivity

All deployment methods require network access to target LLM services:

```mermaid
graph TB
    subgraph "Benchmarker_Deployments"
        LOCAL_BENCH["Local Binary<br/>(host network)"]
        DOCKER_BENCH["Docker Container<br/>(bridge/host network)"]
        K8S_BENCH["Kubernetes Pod<br/>(cluster network)"]
        SLURM_BENCH["Slurm Job<br/>(compute network)"]
    end
    
    subgraph "Target_Infrastructure"
        LOCAL_TGI["localhost:8080<br/>(Local TGI/vLLM)"]
        CLUSTER_LB["LoadBalancer Service<br/>(K8s exposed service)"]
        INTERNAL_EP["Internal Endpoint<br/>(Cluster-internal service)"]
        EXTERNAL_API["External API<br/>(OpenAI, cloud providers)"]
    end
    
    LOCAL_BENCH --> LOCAL_TGI
    DOCKER_BENCH --> LOCAL_TGI
    DOCKER_BENCH --> EXTERNAL_API
    K8S_BENCH --> CLUSTER_LB
    K8S_BENCH --> INTERNAL_EP
    SLURM_BENCH --> INTERNAL_EP
    SLURM_BENCH --> EXTERNAL_API
```

Sources: [README.md:65-88](), [README.md:93-98]()

## Output and Results Management

### Results Persistence Across Deployments

Each deployment method handles results storage differently:

```mermaid
graph LR
    subgraph "Execution_Context"
        BENCH_PROCESS["inference-benchmarker<br/>(Running process)"]
    end
    
    subgraph "Output_Locations"
        LOCAL_CWD["Current Directory<br/>(Local filesystem)"]
        CONTAINER_VOL["Mounted Volume<br/>(Docker bind mount)"]
        K8S_PVC["PersistentVolumeClaim<br/>(K8s storage)"]
        SLURM_SHARED["Shared Filesystem<br/>(NFS, Lustre, etc.)"]
    end
    
    subgraph "Result_Formats"
        JSON_FILES["JSON Results<br/>(.json benchmark data)"]
        STDOUT_LOGS["Console Output<br/>(Real-time progress)"]
    end
    
    BENCH_PROCESS --> LOCAL_CWD
    BENCH_PROCESS --> CONTAINER_VOL
    BENCH_PROCESS --> K8S_PVC
    BENCH_PROCESS --> SLURM_SHARED
    
    LOCAL_CWD --> JSON_FILES
    CONTAINER_VOL --> JSON_FILES
    K8S_PVC --> JSON_FILES
    SLURM_SHARED --> JSON_FILES
    
    BENCH_PROCESS --> STDOUT_LOGS
```

Sources: [README.md:100](), [Dockerfile:11-12]()

## Scaling Considerations

### Concurrent Execution Patterns

Different deployment methods support varying levels of parallelization:

| Deployment | Concurrent Benchmarks | Resource Isolation | Job Management |
|------------|----------------------|-------------------|----------------|
| **Local** | Limited by system resources | Process-level | Manual |
| **Docker** | Container-based isolation | Container-level | Docker Compose |
| **Kubernetes** | Pod-based scaling | Namespace/Pod-level | Built-in scheduler |
| **Slurm** | Job queue management | Job-level allocation | Advanced scheduling |

The benchmarker's internal concurrency is controlled through parameters like `--max-vus` (maximum virtual users), which remains consistent across all deployment methods.

Sources: [README.md:138](), [README.md:244-252]()

## Next Steps

For implementation details of each deployment method:

- **[Docker Deployment](#4.1)**: Container configuration, volume mounting, and networking setup
- **[Kubernetes Deployment](#4.2)**: Helm chart configuration, resource management, and cluster integration  
- **[HPC and Slurm Deployment](#4.3)**: Job submission, resource allocation, and batch processing workflows

For analyzing results from any deployment method, see [Results Analysis and Visualization](#5).

Sources: [README.md:209-230]()

---

