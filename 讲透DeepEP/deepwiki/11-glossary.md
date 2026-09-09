> 来源: [https://deepwiki.com/deepseek-ai/DeepEP/11-glossary](https://deepwiki.com/deepseek-ai/DeepEP/11-glossary)
> DeepWiki deepseek-ai/DeepEP

# Glossary

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1)
 - [csrc/kernels/backend/nccl.cu](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu)
 - [csrc/utils/lazy_driver.hpp](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/utils/lazy_driver.hpp)
 - [deep_ep/__init__.py](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/__init__.py)
 - [deep_ep/include/deep_ep/common/comm.cuh](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/include/deep_ep/common/comm.cuh)
 - [deep_ep/include/deep_ep/common/layout.cuh](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/include/deep_ep/common/layout.cuh)
 - [deep_ep/include/deep_ep/impls/combine_utils.cuh](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/include/deep_ep/impls/combine_utils.cuh)
 
  This page provides definitions for codebase-specific terms, jargon, and domain concepts used in DeepEP. It covers both the high-performance V2 architecture and the legacy V1 system, bridging natural language concepts to their specific implementations in the C++ and Python source code.

 
## Core Concepts

 
### Expert Parallelism (EP)

 A model parallelism strategy for Mixture-of-Experts (MoE) where different experts are hosted on different GPUs. DeepEP provides the communication primitives to move tokens between GPUs based on routing decisions.

 
 - **Sources**: [README.md1-5](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L1-L5) [README.md113-116](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L113-L116)
 
 
### Dispatch

 The "forward" communication phase in MoE. It routes input tokens from their source ranks to the specific GPUs hosting the assigned experts. In V2, this is handled by `ElasticBuffer.dispatch`.

 
 - **Sources**: [README.md17-18](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L17-L18) [deep_ep/buffers/elastic.py175-180](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L175-L180)
 
 
### Combine

 The "reduction" communication phase in MoE. It gathers processed token representations from expert GPUs back to their original source ranks. In V2, this is handled by `ElasticBuffer.combine`.

 
 - **Sources**: [README.md17-18](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L17-L18) [deep_ep/buffers/elastic.py215-220](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L215-L220)
 
 
### Scale-up vs. Scale-out

 
 - **Scale-up Domain**: Communication within a single node or high-speed domain (typically via NVLink). In code, this often refers to `num_nvl_ranks` or `num_scaleup_ranks`.
 - **Scale-out Domain**: Communication across nodes (typically via RDMA/InfiniBand). In code, this refers to `num_rdma_ranks` or `num_scaleout_ranks`.
 - **Hybrid Mode**: A two-phase communication strategy that leverages both domains hierarchically to optimize bandwidth.
 - **Sources**: [README.md17-21](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L17-L21) [csrc/kernels/backend/nccl.cu110-117](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L110-L117) [csrc/kernels/backend/nccl.cu56-60](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L56-L60)
 
 
---

 
## V2 Architecture (Elastic)

 
### ElasticBuffer

 The primary V2 interface that unifies high-throughput and low-latency communication. It manages a contiguous memory workspace and uses analytical resource allocation.

 
 - **Implementation**: `deep_ep::elastic::ElasticBuffer` in [csrc/elastic/buffer.hpp19-140](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp#L19-L140)
 - **Sources**: [README.md17-22](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L17-L22)
 
 
### EPHandle

 An opaque metadata object returned by `dispatch`. It stores routing information (expert alignment, recv counts, etc.) required to perform the corresponding `combine` operation or to cache routing for inference.

 
 - **Sources**: [README.md180-185](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L180-L185) [deep_ep/buffers/elastic.py24-80](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L24-L80)
 
 
### NCCL Gin Backend

 The lightweight communication transport layer introduced in V2, replacing NVSHMEM. It provides header-only primitives for RDMA and NVLink. It utilizes `ncclDevComm_t` and `ncclWindow_t`.

 
 - **Implementation**: [csrc/kernels/backend/nccl.cu82-102](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L82-L102)
 - **Sources**: [README.md13-16](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L13-L16)
 
 
### Analytical Resource Allocation

 The process of calculating the optimal number of SMs (Streaming Multiprocessors) and QPs (Queue Pairs) based on hardware topology and workload, rather than manual tuning.

 
 - **Implementation**: `get_theoretical_num_sms` logic referenced in [README.md158-162](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L158-L162)
 - **Sources**: [README.md20-22](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L20-L22)
 
 
---

 
## V1 Architecture (Legacy)

 
### Buffer (Legacy)

 The V1 communication interface. Unlike V2, it requires separate NVLink and RDMA buffer sizes and supports a specific "low-latency" mode using NVSHMEM.

 
 - **Sources**: [README.md39-40](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L39-L40) [README.md82-84](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L82-L84) [deep_ep/buffers/legacy.py15-40](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/legacy.py#L15-L40)
 
 
### NVSHMEM Backend

 The transport layer used in V1. It requires a custom patch and specific driver configurations (IBGDA).

 
 - **Sources**: [README.md82-84](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L82-L84)
 
 
---

 
## Specialized Features

 
### Engram

 An experimental feature for remote memory access (RMA), primarily used for fetching KV cache during inference with near-zero SM overhead via RDMA.

 
 - **Implementation**: `ElasticBuffer::engram_fetch` in [csrc/elastic/buffer.hpp61-63](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp#L61-L63)
 - **Sources**: [README.md23](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L23-L23) [README.md31](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L31-L31)
 
 
### Pipeline Parallelism (PP) Primitives

 Low-level `send`/`recv` operations designed for zero SM occupation using RDMA.

 
 - **Implementation**: `ElasticBuffer::pp_send` and `ElasticBuffer::pp_recv` in [csrc/elastic/buffer.hpp65-68](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp#L65-L68)
 - **Sources**: [README.md24](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L24-L24)
 
 
### AGRS (All-Gather Reduce-Scatter)

 Experimental primitives for data and tensor parallelism updates.

 
 - **Implementation**: `ElasticBuffer::all_gather` in [csrc/elastic/buffer.hpp70-73](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp#L70-L73)
 - **Sources**: [README.md37](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L37-L37)
 
 
---

 
## System Mapping Diagrams

 
### Dispatch Data Flow: Python to Kernel

 The following diagram bridges the Python API call to the underlying JIT-compiled kernels in V2.

 
```

```

 **Sources**: [csrc/elastic/buffer.hpp19-140](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp#L19-L140) [csrc/kernels/backend/nccl.cu82-102](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L82-L102) [README.md13-25](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L13-L25)

 
### Resource Management: Analytical Tuning

 This diagram shows how the system maps logical MoE parameters to physical hardware resources via the analytical model.

 
```

```

 **Sources**: [README.md158-162](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L158-L162) [csrc/kernels/backend/nccl.cu93-101](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L93-L101) [csrc/kernels/backend/nccl.cu132-133](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L132-L133)

 
---

 
## Technical Glossary Table

 
| Term | Definition | Code Pointer |
|---|---|---|
| Symmetric Memory | Memory registered across all GPUs in a group with the same virtual address, enabling direct RMA. | csrc/kernels/backend/nccl.cu121-133 |
| JIT Compiler | Runtime module using NVRTC to compile specialized kernels based on exact SM/Expert counts. | README.md13-16 deep_ep/__init__.py71-80 |
| FP8 Dispatch | Using E4M3/E5M2 low-precision formats for communication to save bandwidth. | README.md43 deep_ep/buffers/elastic.py175 |
| Workspace | The internal contiguous memory used by ElasticBuffer for staging and communication. | csrc/elastic/buffer.hpp31-36 deep_ep/include/deep_ep/common/layout.cuh10-41 |
| SM90 | NVIDIA Hopper architecture (H100/H800), the primary target for DeepEP performance optimizations. | README.md65-68 |
| RDMA SL | Service Level / Virtual Lane for InfiniBand traffic, configurable via sl_idx. | csrc/kernels/backend/nccl.cu96 csrc/elastic/buffer.hpp87 |
| LSA (Local Share Access) | NCCL terminology for NVLink-accessible peers within a node. | csrc/kernels/backend/nccl.cu51 csrc/kernels/backend/nccl.cu133 |
| Gin Connection | NCCL Gin connection types: RAIL for hybrid or FULL for direct. | csrc/kernels/backend/nccl.cu98-99 |
| WorkspaceLayout | C++ struct defining the memory map for barrier signals, notify counters, and channel metadata. | deep_ep/include/deep_ep/common/layout.cuh10-80 |
| kNumTimeoutCycles | A safety threshold for GPU kernels to trap if a communication peer hangs. | deep_ep/include/deep_ep/common/comm.cuh30-49 |

 **Sources**: [README.md1-160](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L1-L160) [csrc/kernels/backend/nccl.cu1-156](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L1-L156) [csrc/elastic/buffer.hpp1-140](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp#L1-L140) [deep_ep/include/deep_ep/common/layout.cuh10-80](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/include/deep_ep/common/layout.cuh#L10-L80) [deep_ep/include/deep_ep/common/comm.cuh11-50](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/include/deep_ep/common/comm.cuh#L11-L50)
