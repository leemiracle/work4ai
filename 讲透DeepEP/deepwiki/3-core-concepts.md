> 来源: [https://deepwiki.com/deepseek-ai/DeepEP/3-core-concepts](https://deepwiki.com/deepseek-ai/DeepEP/3-core-concepts)
> DeepWiki deepseek-ai/DeepEP

# Core Concepts

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1)
 - [deep_ep/include/deep_ep/common/comm.cuh](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/include/deep_ep/common/comm.cuh)
 
  This page introduces the foundational ideas behind DeepEP V2, a high-performance communication library for Mixture-of-Experts (MoE) parallelism. V2 represents a significant architectural shift from V1, moving from an NVSHMEM-based backend to the lightweight **NCCL Gin** backend and introducing an analytical resource allocation model.

 For detailed deep dives into specific subsystems, see:

 
 - [Dispatch and Combine Operations](https://deepwiki.com/deepseek-ai/DeepEP/3.1-dispatch-and-combine-operations) — Detailed routing logic, metadata handles, and layout options.
 - [Communication Modes and Topology](https://deepwiki.com/deepseek-ai/DeepEP/3.2-communication-modes-and-topology) — Scale-up vs. scale-out domains and hybrid RDMA+NVLink communication.
 - [Memory and Buffer Architecture](https://deepwiki.com/deepseek-ai/DeepEP/3.3-memory-and-buffer-architecture) — The ElasticBuffer model and symmetric memory management.
 - [Analytical Resource Allocation](https://deepwiki.com/deepseek-ai/DeepEP/3.4-analytical-resource-allocation) — Automatic SM and QP calculation without manual tuning.
 
 
---

 
## Foundational Ideas of DeepEP V2

 DeepEP V2 is built around several core concepts that distinguish it from standard collective communication libraries like NCCL or NVSHMEM.

 
### 1. The MoE Expert Parallelism Pattern

 In MoE models, tokens are dynamically routed to a subset of "experts" distributed across multiple GPU ranks. This creates an irregular All-to-All communication pattern where the volume of data sent between any two ranks is determined at runtime by a gating function. DeepEP optimizes this by splitting the process into two phases:

 
 - **Dispatch**: Sending tokens from source ranks to the ranks owning the selected experts.
 - **Combine**: Returning the processed expert outputs to the original source ranks for summation.
 
 **Sources**: [README.md1-26](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L1-L26) [README.md115-116](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L115-L116)

 
### 2. Two-Phase Dispatch/Combine with EPHandle

 Unlike V1, which used separate low-latency and high-throughput APIs, V2 unifies these into a single interface. A key concept is the `EPHandle`, a metadata object produced during the `dispatch` phase. It stores routing information (e.g., expert counts, token mapping) that can be cached and reused during the `combine` phase or across multiple inference decoding steps to eliminate redundant layout calculations.

 **Sources**: [README.md165-175](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L165-L175)

 
### 3. Scale-up vs. Scale-out Domains

 DeepEP V2 models the cluster as a hierarchical topology:

 
 - **Scale-up (NVLink)**: High-bandwidth communication within a single node or NVLink-connected island.
 - **Scale-out (RDMA)**: Communication across nodes via InfiniBand or RoCE.
 
 V2 introduces a "hybrid mode" (`allow_hybrid_mode=True`) that uses a hierarchical dispatch strategy to saturate both NVLink and RDMA bandwidth simultaneously by differentiating between logical and physical domains.

 **Sources**: [README.md18-21](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L18-L21) [csrc/kernels/backend/api.cuh43](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/api.cuh#L43-L43) [csrc/kernels/backend/api.cuh58-63](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/api.cuh#L58-L63)

 
### 4. NCCL Gin Backend

 DeepEP V2 replaces NVSHMEM with the **NCCL Gin backend**. Gin is a lightweight, header-only transport layer that allows DeepEP to reuse existing NCCL communicators and windows while providing low-level "put/get" primitives. This reduces initialization overhead and simplifies integration into existing training frameworks. The backend uses specific tags (e.g., `kDispatchTag0`, `kCombineTag0`) to manage concurrent operations.

 **Sources**: [README.md9-16](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L9-L16) [csrc/kernels/backend/api.cuh67-72](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/api.cuh#L67-L72) [deep_ep/include/deep_ep/common/comm.cuh15-25](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/include/deep_ep/common/comm.cuh#L15-L25)

 
---

 
## System Architecture: From Natural Language to Code

 The following diagrams bridge high-level system concepts to the specific code entities found in the repository.

 
### Diagram 1: Communication Workflow and Data Entities

 This diagram maps the logical flow of a MoE forward pass to the Python classes and C++ implementation headers.

 
```

```

 **Sources**: [csrc/kernels/backend/api.cuh46-92](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/api.cuh#L46-L92) [README.md115-162](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L115-L162) [deep_ep/include/deep_ep/impls/combine_utils.cuh1-72](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/include/deep_ep/impls/combine_utils.cuh#L1-L72)

 
### Diagram 2: Logical vs. Physical Domain Mapping

 DeepEP V2 maps logical MoE ranks to physical hardware ranks using NCCL symmetric memory contexts and workspace layouts. It uses `ncclGin` primitives for cross-rank communication and synchronization.

 
```

```

 **Sources**: [deep_ep/include/deep_ep/common/layout.cuh10-41](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/include/deep_ep/common/layout.cuh#L10-L41) [csrc/kernels/backend/api.cuh46-84](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/api.cuh#L46-L84) [deep_ep/include/deep_ep/common/comm.cuh56-86](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/include/deep_ep/common/comm.cuh#L56-L86) [deep_ep/include/deep_ep/common/comm.cuh135-156](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/include/deep_ep/common/comm.cuh#L135-L156)

 
---

 
## Core Component Summary

 
| Component | Code Location | Role |
|---|---|---|
| ElasticBuffer | deep_ep/buffers/elastic.py | Primary user-facing class for V2. Manages memory and kernel launches. |
| EPHandle | deep_ep/buffers/elastic.py | Stores routing metadata; enables communication-computation overlap. |
| WorkspaceLayout | deep_ep/include/deep_ep/common/layout.cuh 10-80 | Defines the memory offsets for barriers, counters, and channel metadata. |
| NCCLSymmetricMemoryContext | csrc/kernels/backend/api.cuh 46-92 | Manages NCCL windows, device communicators, and symmetric memory pointers. |
| CombineVecTraits | deep_ep/include/deep_ep/impls/combine_utils.cuh 29-39 | Determines optimal vector types (int4, longlong4_t) for data movement. |
| Analytical Model | deep_ep/buffers/elastic.py | get_theoretical_num_sms logic that replaces V1 auto-tuning. |
| NCCLGin Handle | deep_ep/include/deep_ep/common/handle.cuh | Device-side handle for RDMA/NVLink put/get operations. |

 
### Summary of Child Pages

 
#### [Dispatch and Combine Operations](https://deepwiki.com/deepseek-ai/DeepEP/3.1-dispatch-and-combine-operations)

 Covers the mechanics of how `topk_idx` is used to route tokens, the layout options like `do_expand`, and how expert alignment padding ensures high-performance memory access.

 
#### [Communication Modes and Topology](https://deepwiki.com/deepseek-ai/DeepEP/3.2-communication-modes-and-topology)

 Details the distinction between `rdma_ranks` and `nvlink_ranks`, and how the `allow_hybrid_mode` flag triggers hierarchical kernels that optimize for complex network topologies.

 
#### [Memory and Buffer Architecture](https://deepwiki.com/deepseek-ai/DeepEP/3.3-memory-and-buffer-architecture)

 Explains the `ElasticBuffer` memory layout, including how it uses `ncclWindow_t` and `SymmetricMemory` to provide a global address space across the cluster.

 
#### [Analytical Resource Allocation](https://deepwiki.com/deepseek-ai/DeepEP/3.4-analytical-resource-allocation)

 Explains the mathematical formulas used to determine the optimal number of SMs and QPs based on hardware bandwidth (RDMA vs. NVLink GB/s), eliminating the need for empirical auto-tuning.

 **Sources**: [README.md113-116](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L113-L116) [README.md158-160](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L158-L160) [csrc/kernels/backend/api.cuh1-105](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/api.cuh#L1-L105) [deep_ep/include/deep_ep/common/comm.cuh1-25](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/include/deep_ep/common/comm.cuh#L1-L25)
