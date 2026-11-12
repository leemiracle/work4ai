<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/apex · page 3 Distributed Training · fetched 2026-10-26 -->

# Distributed Training

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apex/__init__.py](apex/__init__.py)
- [csrc/syncbn.cpp](csrc/syncbn.cpp)

</details>



APEX provides a suite of optimized tools for distributed training that extend or improve upon PyTorch's native capabilities. These tools are designed to maximize throughput and scalability in multi-GPU and multi-node environments, specifically targeting NVIDIA GPU architectures. The distributed training stack in APEX focuses on three primary areas: efficient gradient synchronization, cross-GPU batch normalization, and model parallelism for massive architectures.

### High-Level Architecture

The following diagram illustrates how APEX's distributed components interface with the PyTorch ecosystem and the underlying hardware.

**Distributed Training Component Interaction**
```mermaid
graph TD
    subgraph "User Code"
        "Model"["torch.nn.Module"]
        "Opt"["Optimizer"]
    end

    subgraph "APEX Distributed Layers"
        "DDP"["apex.parallel.DistributedDataParallel"]
        "SBN"["apex.parallel.SyncBatchNorm"]
        "PP"["apex.transformer.pipeline_parallel"]
    end

    subgraph "Backend Communication"
        "NCCL"["NCCL / torch.distributed"]
        "CudaKernels"["Optimized CUDA Kernels"]
    end

    "Model" --> "DDP"
    "Model" --> "SBN"
    "Model" --> "PP"
    "DDP" --> "NCCL"
    "SBN" --> "CudaKernels"
    "PP" --> "NCCL"
    "CudaKernels" --> "NCCL"
```
**Sources:** [apex/__init__.py:14-15](), [csrc/syncbn.cpp:71-89]()

---

### DistributedDataParallel (DDP)

APEX's `DistributedDataParallel` is a high-performance wrapper for multi-GPU training. While PyTorch provides a native DDP, APEX's implementation was historically optimized for specific use cases involving mixed precision and custom gradient reduction logic. It manages the synchronization of gradients across different processes using `torch.distributed` backends (primarily NCCL).

A key feature often paired with APEX DDP is support for Large Batch Training (LARC), which helps maintain stability when scaling to very large cluster sizes.

For details, see [DistributedDataParallel](#3.1).

**Sources:** [apex/__init__.py:37-44]()

---

### SyncBatchNorm

In standard distributed training, `BatchNorm` layers calculate statistics independently on each GPU, which can lead to inaccurate estimates if the per-GPU batch size is small. APEX provides `SyncBatchNorm`, which synchronizes mean and variance statistics across all participating GPUs (or specific process groups).

APEX's implementation is highly optimized via custom C++/CUDA kernels that utilize the Welford algorithm for numerically stable variance computation [csrc/syncbn.cpp:7-15](). It also supports "Channel Last" (NHWC) memory formats for increased performance on Tensor Cores [csrc/syncbn.cpp:39-49]().

For details, see [SyncBatchNorm](#3.2).

**Code Entity Mapping: SyncBatchNorm Kernels**
```mermaid
graph LR
    subgraph "Python API"
        "SBN_PY"["apex.parallel.SyncBatchNorm"]
    end

    subgraph "C++ Dispatch (csrc/syncbn.cpp)"
        "WF"["welford_parallel"]
        "BN_FWD"["batchnorm_forward"]
        "BN_BWD"["batchnorm_backward"]
    end

    subgraph "CUDA Implementation"
        "W_CUDA"["welford_parallel_CUDA"]
        "F_CUDA"["batchnorm_forward_CUDA"]
        "B_CUDA"["batchnorm_backward_CUDA"]
    end

    "SBN_PY" -- "calls" --> "WF"
    "SBN_PY" -- "calls" --> "BN_FWD"
    "SBN_PY" -- "calls" --> "BN_BWD"
    "WF" --> "W_CUDA"
    "BN_FWD" --> "F_CUDA"
    "BN_BWD" --> "B_CUDA"
```
**Sources:** [csrc/syncbn.cpp:8-35](), [csrc/syncbn.cpp:72-79]()

---

### Pipeline Parallelism

For models too large to fit on a single GPU's memory (such as large-scale Transformer models), APEX provides Pipeline Parallelism. This allows the model to be partitioned into stages, with different stages residing on different GPUs. APEX handles the complex scheduling of microbatches to ensure high GPU utilization and manages the Peer-to-Peer (P2P) communication required between stages.

The implementation supports both simple non-interleaved schedules and advanced interleaved schedules to reduce the "pipeline bubble" (idle time).

For details, see [Pipeline Parallelism](#3.3).

**Sources:** [apex/__init__.py:21-30]() (Version checking logic used in distributed setups)

---

### Summary of Distributed Components

| Component | Purpose | Key Code Entities |
| :--- | :--- | :--- |
| **DDP** | Data Parallelism | `apex.parallel.DistributedDataParallel` |
| **SyncBN** | Cross-GPU Batch Norm | `welford_parallel`, `batchnorm_forward` |
| **Pipeline** | Model Parallelism | `apex.transformer.pipeline_parallel` |
| **Optimizers** | Distributed States | `DistributedFusedAdam` (See [DistributedFusedAdam](#4.2)) |

**Sources:** [csrc/syncbn.cpp:71-89](), [apex/__init__.py:14-18]()

---

