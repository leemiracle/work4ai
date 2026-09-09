> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-Prover-V2/1-overview](https://deepwiki.com/deepseek-ai/DeepSeek-Prover-V2/1-overview)
> DeepWiki deepseek-ai/DeepSeek-Prover-V2

# Overview

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1)
 - [deep_ep/__init__.py](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/__init__.py)
 
  
## Purpose and Scope

 DeepEP (DeepEveryParallel) is a high-performance communication library tailored for modern machine learning training and inference, specifically optimized for **Mixture-of-Experts (MoE) expert parallelism**. It provides high-throughput and low-latency all-to-all GPU kernels for MoE dispatch and combine operations, supporting low-precision formats like FP8 [README.md1-5](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L1-L5)

 The library features a lightweight **Just-In-Time (JIT)** compilation system, allowing it to run without pre-compilation of CUDA kernels during installation [README.md3-5](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L3-L5) DeepEP V2 introduces a significant architectural shift from the NVSHMEM-based V1 to a more efficient **NCCL Gin backend**, achieving up to 1.3x peak performance while reducing SM occupancy by up to 4x [README.md9-57](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L9-L57)

 **Sources:** [README.md1-17](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L1-L17) [deep_ep/__init__.py71-84](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/__init__.py#L71-L84)

 
---

 
## Architectural Evolution: V1 to V2

 DeepEP V2 represents a complete refactoring of the communication layer. The transition from V1 to V2 involves several major shifts in backend technology and resource management:

 
| Feature | V1 (Legacy) | V2 (Elastic) |
|---|---|---|
| Backend | NVSHMEM (IBGDA/Symmetric Heap) | NCCL Gin (Header-only, lightweight) |
| Interface | Buffer class | ElasticBuffer & EPHandle |
| Resource Allocation | Manual tuning (num_sms, Config) | Analytical calculation via formulas |
| Domain Scale | Limited scale-out | Up to EP2048 |
| SM Occupancy | High (e.g., 24 SMs) | Low (e.g., 4-6 SMs) |
| JIT Pipeline | Partial / Pre-compiled | Fully JIT (NVRTC-based) |

 **Sources:** [README.md9-25](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L9-L25) [README.md115-116](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L115-L116) [deep_ep/buffers/elastic.py16-30](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L16-L30)

 
---

 
## System Architecture and Code Entities

 The following diagram maps the high-level system components to their corresponding code entities and files, illustrating the bridge between the Python user space and the CUDA kernel implementations.

 
```

```

 **Diagram: DeepEP V2 Code Entity Mapping**

 **Sources:** [deep_ep/__init__.py87-97](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/__init__.py#L87-L97) [deep_ep/buffers/elastic.py16-30](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L16-L30) [README.md13-17](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L13-L17) [csrc/python_api.cpp1-39](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/python_api.cpp#L1-L39)

 
---

 
## Core Abstractions: ElasticBuffer and EPHandle

 
### ElasticBuffer

 The `ElasticBuffer` is the primary interface in V2. It manages a single contiguous GPU buffer that serves as a symmetric memory window across the communication group [README.md115-116](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L115-L116) It uses `NCCLSymmetricMemoryContext` to handle cross-GPU memory registration and RDMA window management [csrc/kernels/backend/nccl.cu10-50](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L10-L50) It supports both standard EP operations and experimental features like PP and Engram.

 
### EPHandle

 The `EPHandle` is a metadata object produced during the dispatch phase. It caches critical routing information, including:

 
 - **Expert Alignment**: Padding information for memory efficiency [deep_ep/buffers/elastic.py32-40](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L32-L40)
 - **Token Counts**: `psum_num_recv_tokens_per_expert` and `num_recv_tokens` [deep_ep/buffers/elastic.py45-55](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L45-L55)
 - **Routing Metadata**: `topk_idx` and `recv_src_metadata` for the combine phase [deep_ep/buffers/elastic.py42-50](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L42-L50)
 
 This handle can be reused for subsequent `combine` operations or cached during inference decoding to eliminate redundant metadata calculation [README.md18-20](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L18-L20)

 **Sources:** [deep_ep/buffers/elastic.py16-110](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L16-L110) [README.md115-130](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L115-L130)

 
---

 
## Supported Communication Modes

 DeepEP V2 provides a unified interface for several high-performance primitives, executed via the NCCL Gin backend:

 
 - **EP Dispatch/Combine**: The core MoE all-to-all kernels. Supports `do_expand` for GEMM layout optimization and `expert_alignment` for memory efficiency [deep_ep/buffers/elastic.py134-210](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L134-L210)
 - **Engram (Remote Memory Access)**: Zero-SM RDMA-based remote memory fetching (e.g., for KV cache). Uses `engram_write` and `engram_fetch` (returning a hook) to access remote memory with minimal compute overhead [README.md23-31](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L23-L31)
 - **Pipeline Parallelism (PP)**: Experimental zero-SM RDMA primitives (`pp_send`, `pp_recv`) for point-to-point communication between pipeline stages [README.md24-100](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L24-L100)
 - **All-Gather Reduce-Scatter (AGRS)**: Experimental primitives for data and tensor parallelism, including `all_gather` updates [README.md37-98](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L37-L98)
 
 
```

```

 **Diagram: V2 Dispatch Execution Flow**

 **Sources:** [deep_ep/buffers/elastic.py113-400](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L113-L400) [README.md97-101](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L97-L101) [csrc/kernels/backend/nccl.cu60-100](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L60-L100)

 
---

 
## Resource Allocation and Topology

 V2 eliminates the need for manual auto-tuning by using analytical formulas to determine optimal resource usage.

 
### Analytical SM Tuning

 The method `get_theoretical_num_sms` calculates the required SM count based on hardware performance characteristics:

 
 - **Bandwidth Modeling**: Considers `sm_read_gbs`, `sm_write_gbs`, `rdma_gbs`, and `nvlink_gbs` [deep_ep/buffers/elastic.py441-450](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L441-L450)
 - **Overlap**: Adjusts counts based on the `prefer_overlap_with_compute` flag to allow communication to hide behind computation [deep_ep/buffers/elastic.py121-125](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L121-L125)
 
 
### Topology Domains

 DeepEP models the cluster as a logical grid of ranks:

 
 - **Scale-up Domain**: Communication via NVLink (Intra-node/Intra-LSA) [deep_ep/utils/envs.py10-25](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/utils/envs.py#L10-L25)
 - **Scale-out Domain**: Communication via RDMA (Inter-node/Rail-only) [deep_ep/utils/envs.py10-25](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/utils/envs.py#L10-L25)
 - **Hybrid Mode**: When `allow_hybrid_mode=True`, the library uses a hierarchical approach, combining NVLink and RDMA to maximize throughput in large clusters [deep_ep/buffers/elastic.py120-121](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L120-L121)
 
 **Sources:** [deep_ep/buffers/elastic.py113-470](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L113-L470) [README.md18-22](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L18-L22) [deep_ep/utils/envs.py7-30](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/utils/envs.py#L7-L30)

 
---

 
## Hardware and Software Requirements

 To utilize DeepEP V2, the following environment is required:

 
 - **GPU Architecture**: NVIDIA Hopper (SM90) or newer (e.g., Blackwell/SM100) [README.md63-65](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L63-L65)
 - **CUDA**: 12.3 or above for SM90 support [README.md67-68](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L67-L68)
 - **NCCL**: 2.30.4 or above (recommended via `nvidia-nccl-cu13` pip package) [README.md70-79](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L70-L79)
 - **Interconnect**: NVLink for intra-node; RDMA (InfiniBand/RoCE) for inter-node [README.md71-72](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L71-L72)
 - **Python**: 3.8+ with PyTorch 2.10+ [README.md66-69](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L66-L69)
 
 **Sources:** [README.md63-72](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L63-L72) [deep_ep/__init__.py46-70](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/__init__.py#L46-L70)
