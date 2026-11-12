<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/DeepEP · page 2 Getting Started · fetched 2026-11-11 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [install.sh](install.sh)

</details>



This page provides an entry point for new users to install and begin using DeepEP. It covers system requirements, dependency installation, building the library via `install.sh`, and an overview of the buffer family (`EPBuffer`, `BucketBuffer`, `EngramBuffer`, `PPBuffer`) and `BufferAllocator` [README.md:11-15]().

For detailed build configuration options, environment variables, and binary-identity validation, see [Installation and Build](#2.1). For complete working examples of dispatch/combine, buffer size hints, and bucket collectives, see [Quick Start Guide](#2.2).

**Sources:** [README.md:1-58]()

---

## Prerequisites and System Requirements

DeepEP is optimized for modern NVIDIA Hopper GPUs and high-performance interconnects.

### Hardware Requirements

| Component | Requirement | Purpose |
|-----------|-------------|---------|
| GPU Architecture | Hopper (SM90) or newer | Primary target for high-performance kernels [README.md:49]() |
| Intra-node Interconnect | NVLink | High-bandwidth scale-up communication [README.md:54]() |
| Inter-node Network | RDMA (InfiniBand/RoCE) | Scale-out communication [README.md:55]() |

### Software Requirements

| Component | Version | Notes |
|-----------|---------|-------|
| Python | 3.10+ | [README.md:48]() |
| CUDA Toolkit | 13.1+ | Required for DeepJIT compilation [README.md:50]() |
| PyTorch | 2.10+ | With CUDA support [README.md:52]() |
| NCCL | 2.32.3+ | Required for the NCCL Gin backend [README.md:53]() |

**Sources:** [README.md:47-55]()

---

## Installation Workflow Overview

The following diagram illustrates the installation and setup pipeline, mapping steps to specific code entities and environment variables.

### Installation and Setup Pipeline
```mermaid
---
title: "Installation and Setup Pipeline"
graph TB
    Start["User: Installation Start"]
    
    subgraph "Dependency Setup"
        InstallNCCL["pip install nvidia-nccl-cu13>=2.32.3"]
        Submodule["git submodule update --init --recursive"]
    end
    
    subgraph "Environment Configuration"
        SetNCCL["Set EP_NCCL_ROOT_DIR"]
        SetJIT["Set EP_JIT_CACHE_DIR"]
        SetTopk["Set EP_NUM_TOPK_IDX_BITS"]
    end
    
    subgraph "Build Process"
        RunInstall["bash install.sh"]
        SetupPy["python setup.py bdist_wheel"]
        PipInstall["pip install dist/*.whl"]
    end
    
    subgraph "Verification"
        TestEP["python tests/ep/test_ep.py"]
        TestBucket["python tests/bucket/test_all_gather.py"]
    end
    
    Start --> InstallNCCL
    InstallNCCL --> Submodule
    Submodule --> SetNCCL
    SetNCCL --> SetJIT
    SetJIT --> SetTopk
    SetTopk --> RunInstall
    RunInstall --> SetupPy
    SetupPy --> PipInstall
    PipInstall --> TestEP
    TestEP --> TestBucket
    TestBucket --> Done["Ready for Use"]
```

**Sources:** [README.md:63-99](), [install.sh:1-12]()

---

## Core Installation Steps

### 1. Install NCCL
DeepEP relies on NCCL matching your CUDA environment so headers and libraries can be properly discovered [README.md:59-67]().

```bash
# CUDA 13.x
python -m pip install "nvidia-nccl-cu13>=2.32.3" --no-deps
```

### 2. Environment Variables and Submodules
Initialize the DeepJIT submodule and ensure required environment variables (`EP_NCCL_ROOT_DIR`, `EP_JIT_CACHE_DIR`, `EP_NUM_TOPK_IDX_BITS`) are configured if using custom paths [README.md:74-79]().

### 3. Build and Install
Run the installation script to build the wheel and install it into the current Python environment [README.md:73-79](), [install.sh:1-12]():

```bash
git submodule update --init --recursive
bash install.sh
```

For a detailed guide on binary identity validation, `find_pkgs`, and JIT initialization, see [Installation and Build](#2.1).

**Sources:** [README.md:59-81](), [install.sh:1-12]()

---

## First Steps with Buffers

DeepEP provides a unified buffer family (`EPBuffer`, `BucketBuffer`, `EngramBuffer`, `PPBuffer`) sharing the `BufferBase` lifecycle and managed via `BufferAllocator` [README.md:11-15]().

### Component Relationship
```mermaid
---
title: "Component Relationship"
graph LR
    subgraph "Python API (deep_ep)"
        EB["EPBuffer / BucketBuffer<br/>(deep_ep/buffers)"]
        BA["BufferAllocator<br/>(deep_ep/buffers/base.py)"]
    end

    subgraph "C++ Backend"
        CEB["Buffer Classes<br/>(csrc/buffers)"]
        JIT["DeepJIT Compiler<br/>(third-party/deep_jit)"]
        NCCL["NCCL Gin Backend<br/>(csrc/kernels/comm)"]
    end

    BA --> EB
    EB --> CEB
    CEB --> JIT
    CEB --> NCCL
```

### Basic Initialization
Construct an `EPBuffer` or use analytical sizing helpers like `get_buffer_size_hint` and `get_theoretical_num_sms` [README.md:31](). For details on constructing buffers, running dispatch/combine, bucket collectives, and caching, see [Quick Start Guide](#2.2).

**Sources:** [README.md:11-35](), [README.md:105-134]()

---

## Verification

Run test scripts from the test suite to verify correct operation across environments [README.md:83-99]():

```bash
python tests/ep/test_ep.py
python tests/bucket/test_all_gather.py
python tests/buffer/test_allocation.py
```

**Sources:** [README.md:83-99]()

---

