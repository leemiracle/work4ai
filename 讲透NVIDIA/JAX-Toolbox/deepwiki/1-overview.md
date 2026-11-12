<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/JAX-Toolbox · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/container/manifest.yaml](.github/container/manifest.yaml)
- [.github/workflows/_ci.yaml](.github/workflows/_ci.yaml)
- [.github/workflows/ci.yaml](.github/workflows/ci.yaml)
- [README.md](README.md)

</details>



This page provides a high-level overview of JAX-Toolbox, a comprehensive system that delivers optimized Docker containers, a robust CI/CD pipeline, and performance-tuned examples for JAX-based deep learning frameworks on NVIDIA GPUs. 

JAX-Toolbox simplifies the development and deployment experience of JAX applications on NVIDIA hardware through containerization, automated testing, and performance optimization. For specific details about container architecture, see [Container System Architecture](#2), and for CI/CD pipeline details, refer to [CI/CD Pipeline](#3).

Sources: [README.md:1-6]()

## Core Components

JAX-Toolbox consists of the following core components:

1. **Container System**: A hierarchical set of Docker containers from base CUDA images to framework-specific containers
2. **CI/CD Pipeline**: Automated workflows for building, testing, and publishing containers
3. **Framework Support**: Integration with popular JAX-based ML frameworks
4. **Testing Infrastructure**: Comprehensive testing across different hardware configurations
5. **Performance Tools**: Utilities for profiling and optimizing JAX applications

Sources: [README.md:6-17](), [.github/workflows/ci.yaml:1-47]()

## Container Architecture

JAX-Toolbox uses a layered container architecture that builds from NVIDIA CUDA base images up to specialized framework containers.

```mermaid
flowchart TD
    subgraph "Container Hierarchy"
        cuda["NVIDIA CUDA Base Image"]
        base["Base Container
        (CUDA + cuDNN + NCCL + OFED)"]
        jax["JAX Core Container
        (Base + JAX + Flax + TE)"]
        
        cuda --> base
        base --> jax
        
        jax --> maxtext["MaxText Container"]
        jax --> t5x["T5X Container"]
        jax --> equinox["Equinox Container"]
        jax --> axlearn["AXLearn Container"]
        t5x --> rosetta_t5x["Rosetta T5X Container"]
    end
    
    classDef container fill:white,stroke:#333,stroke-width:2px
    class cuda,base,jax,maxtext,t5x,equinox,axlearn,rosetta_t5x container
```

Each container serves a specific purpose:

| Container | Purpose | Image |
|-----------|---------|-------|
| Base | Foundation with CUDA, cuDNN, NCCL, and networking libraries | `ghcr.io/nvidia/jax:base` |
| JAX Core | JAX, Flax, and Transformer Engine | `ghcr.io/nvidia/jax:jax` |
| MaxText | Large language model training | `ghcr.io/nvidia/jax:maxtext` |
| T5X | Text-to-text and vision transformers | `ghcr.io/nvidia/jax:t5x` |
| Equinox | Scientific machine learning | `ghcr.io/nvidia/jax:equinox` |
| AXLearn | Advanced ML research | `ghcr.io/nvidia/jax:axlearn` |

Sources: [README.md:11-16](), [.github/workflows/_ci.yaml:40-139]()

## Build and CI/CD System

JAX-Toolbox employs a sophisticated CI/CD pipeline to build, test, and publish Docker containers. The pipeline is triggered by pull requests, scheduled events, or manual dispatch.

```mermaid
flowchart TD
    trigger["Pipeline Triggers:
    - Schedule (Daily)
    - Pull Request
    - Manual"]
    
    metadata["Metadata Job:
    - Version
    - Build Date
    - Flags"]
    
    bump_manifest["Manifest Update:
    - Update Dependencies
    - Check Versions
    - Apply Patches"]
    
    build_base["Build Base Image:
    - CUDA
    - Libraries"]
    
    build_jax["Build JAX Image:
    - JAX Core
    - Flax
    - TransformerEngine"]
    
    build_frameworks["Build Framework Images:
    - T5X
    - MaxText
    - Equinox
    - AXLearn"]
    
    testing["Testing:
    - Unit Tests
    - Integration Tests
    - Multi-GPU Tests"]
    
    publish["Publish Containers:
    - GitHub Container Registry
    - Status Badges"]
    
    trigger --> metadata
    metadata --> bump_manifest
    bump_manifest --> build_base
    build_base --> build_jax
    build_jax --> build_frameworks
    build_frameworks --> testing
    testing --> publish

    classDef step fill:white,stroke:#333,stroke-width:2px
    class trigger,metadata,bump_manifest,build_base,build_jax,build_frameworks,testing,publish step
```

The build process consists of several stages:

1. **Metadata Collection**: Determines build date, version tags, and publication settings
2. **Manifest Update**: Ensures all dependencies are at their latest verified commits
3. **Base Image Build**: Creates the foundation CUDA container
4. **JAX Core Build**: Builds JAX with GPU optimizations
5. **Framework-Specific Builds**: Builds containers for each supported framework
6. **Testing**: Runs various test suites on different hardware configurations
7. **Publication**: Publishes containers to GitHub Container Registry

Sources: [.github/workflows/ci.yaml:57-437](), [.github/workflows/_ci.yaml:1-39]()

## Dependency Management

JAX-Toolbox manages dependencies through a manifest system that tracks specific commits of various components to ensure compatibility and reproducibility.

```mermaid
flowchart LR
    manifest["manifest.yaml"]
    
    subgraph "Core Dependencies"
        jax["JAX
        (google/jax)"]
        xla["XLA
        (openxla/xla)"]
        flax["Flax
        (google/flax)"]
        te["Transformer Engine
        (NVIDIA/TransformerEngine)"]
    end
    
    subgraph "Framework Dependencies"
        t5x_repo["T5X
        (google-research/t5x)"]
        maxtext_repo["MaxText
        (google/maxtext)"]
        equinox_repo["Equinox
        (patrick-kidger/equinox)"]
        airio["AirIO
        (google/airio)"]
    end
    
    manifest --> jax
    manifest --> xla
    manifest --> flax
    manifest --> te
    manifest --> t5x_repo
    manifest --> maxtext_repo
    manifest --> equinox_repo
    manifest --> airio

    classDef component fill:white,stroke:#333,stroke-width:2px
    class manifest,jax,xla,flax,te,t5x_repo,maxtext_repo,equinox_repo,airio component
```

The manifest system:
- Tracks specific git commits for each dependency
- Supports patching through the patch distribution system
- Enables reproducible builds with consistent dependencies
- Simplifies updating dependencies across the entire system

Sources: [.github/container/manifest.yaml:1-104](), [.github/workflows/ci.yaml:134-190]()

## Supported Frameworks and Models

JAX-Toolbox supports several key JAX-based machine learning frameworks:

| Framework | Supported Models | Use Cases | Container |
|-----------|-----------------|-----------|-----------|
| MaxText | GPT, LLaMA, Gemma, Mistral, Mixtral | Pre-training | `ghcr.io/nvidia/jax:maxtext` |
| T5X | T5, ViT | Pre-training, fine-tuning | `ghcr.io/nvidia/jax:t5x` |
| T5X (Imagen) | Imagen | Pre-training | `ghcr.io/nvidia/jax:t5x-imagen` |
| AXLearn | Fuji | Pre-training | `ghcr.io/nvidia/jax:axlearn` |
| Equinox | Various | Scientific ML | `ghcr.io/nvidia/jax:equinox` |

These frameworks support different parallelism strategies for efficient multi-GPU, multi-node training:

```mermaid
flowchart TD
    subgraph "Frameworks"
        mt["MaxText"]
        t5x["T5X"]
        axl["AXLearn"]
        eq["Equinox"]
    end
    
    subgraph "Parallelism Strategies"
        dp["Data Parallelism"]
        fsdp["Fully Sharded Data Parallelism"]
        tp["Tensor Parallelism"]
        pp["Pipeline Parallelism"]
    end
    
    mt --> dp & fsdp & tp & pp
    t5x --> dp & fsdp & tp
    axl --> dp & fsdp & tp & pp
    eq --> dp

    classDef framework fill:white,stroke:#333,stroke-width:2px
    class mt,t5x,axl,eq,dp,fsdp,tp,pp framework
```

Sources: [README.md:8-16](), [.github/workflows/_ci.yaml:84-138]()

## Testing Infrastructure

JAX-Toolbox employs a comprehensive testing infrastructure to ensure quality and performance across different hardware configurations.

```mermaid
flowchart LR
    subgraph "Test Types"
        unit["Unit Tests"]
        integration["Integration Tests"]
        mgmn["Multi-GPU
        Multi-Node Tests"]
        perf["Performance Tests"]
    end
    
    subgraph "Hardware"
        a100["NVIDIA A100"]
        h100["NVIDIA H100"]
        slurm["SLURM Cluster"]
        eks["Kubernetes/EKS"]
    end
    
    unit --> a100
    integration --> a100 & h100
    mgmn --> slurm & eks
    perf --> a100 & h100
    
    subgraph "Test Components"
        jax_test["JAX Core Tests"]
        te_test["Transformer Engine Tests"]
        t5x_test["T5X Tests"]
        maxtext_test["MaxText Tests"]
        axlearn_test["AXLearn Tests"]
    end
    
    a100 --> jax_test & te_test & t5x_test & maxtext_test
    h100 --> te_test & axlearn_test
    slurm --> t5x_test & maxtext_test
    eks --> axlearn_test

    classDef testcomp fill:white,stroke:#333,stroke-width:2px
    class unit,integration,mgmn,perf,a100,h100,slurm,eks,jax_test,te_test,t5x_test,maxtext_test,axlearn_test testcomp
```

The testing system verifies:
- Core JAX functionality on GPUs
- Framework-specific components
- Multi-GPU and multi-node scaling
- Performance characteristics
- Integration with various cluster management systems

Sources: [.github/workflows/_ci.yaml:179-570](), [README.md:18-205]()

## Performance Optimization

JAX-Toolbox includes performance optimizations for NVIDIA GPUs through environment variables and XLA flags:

| XLA Flag | Purpose |
|----------|---------|
| `--xla_gpu_enable_latency_hiding_scheduler` | Improves communication/compute overlap |
| `--xla_gpu_enable_triton_gemm` | Controls GEMM kernel selection |

| Environment Variable | Purpose |
|---------------------|---------|
| `NCCL_NVLS_ENABLE` | Controls NVLink SHARP for multi-GPU communication |

The repository also provides profiling tools like `nsys-jax` for performance analysis and optimization.

Sources: [README.md:213-226](), [.github/workflows/_ci.yaml:233-337]()

## Usage and Access

JAX-Toolbox containers are publicly available via GitHub Container Registry:

```
ghcr.io/nvidia/jax:<framework>       # Latest build
ghcr.io/nvidia/jax:<framework>-YYYY-MM-DD  # Specific date
```

For example:
```bash
docker pull ghcr.io/nvidia/jax:maxtext
docker run --gpus all --shm-size=1g ghcr.io/nvidia/jax:maxtext
```

Special considerations:
- Docker containers require `--gpus all` flag for GPU access
- Shared memory size should be increased with `--shm-size=1g` to avoid bus errors
- Multi-node deployments can leverage SLURM or Kubernetes integration

Sources: [README.md:209-211](), [README.md:249-279]()

---

