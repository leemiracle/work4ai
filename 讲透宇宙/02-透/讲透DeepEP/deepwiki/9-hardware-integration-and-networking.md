> 来源: [https://deepwiki.com/deepseek-ai/DeepEP/9-hardware-integration-and-networking](https://deepwiki.com/deepseek-ai/DeepEP/9-hardware-integration-and-networking)
> DeepWiki deepseek-ai/DeepEP

# Hardware Integration and Networking

  Relevant source files 
 - [csrc/kernels/backend/api.cuh](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/api.cuh)
 - [csrc/kernels/backend/nccl.cu](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu)
 
  DeepEP integrates with high-performance interconnects including **NVLink** for scale-up (intranode) and **InfiniBand/RDMA** for scale-out (internode) communication. The library has transitioned from a legacy architecture based on **NVSHMEM** (V1) to a modern, lightweight **NCCL Gin** transport layer (V2).

 
---

 
## Hardware Requirements

 DeepEP V2 targets modern GPU architectures and high-speed networking environments.

 
| Component | Requirement | Purpose |
|---|---|---|
| GPU Architecture | Hopper (SM90) or newer | Support for SM90 PTX ISA and TMA features README.md63-65 |
| CUDA Version | 12.3+ | Required for SM90-specific JIT compilation README.md67-68 |
| NCCL Version | 2.30.4+ | Core transport for the Gin backend README.md70 |
| Intranode | NVLink | High-bandwidth scale-up communication README.md71 |
| Internode | RDMA Network (e.g., InfiniBand) | Low-latency scale-out communication README.md72 |
| PCIe | Atomic Support | Fast RDMA atomics for coordination csrc/kernels/backend/nccl.cu86-99 |

 Sources: [README.md63-72](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L63-L72) [csrc/kernels/backend/nccl.cu86-99](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L86-L99)

 
---

 
## Transport Layer Evolution

 DeepEP V2 introduces the **NCCL Gin** backend, a header-only transport layer that replaces the heavy NVSHMEM dependency for primary operations. This shift enables several key improvements:

 
 - **Reduced Resource Usage**: SM usage for training is reduced from 24 to 4-6 while maintaining performance [README.md22](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L22-L22)
 - **Communicator Reuse**: DeepEP can now reuse existing NCCL communicators via the `EP_REUSE_NCCL_COMM` logic [README.md16](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L16-L16)
 - **Unified Interface**: Both high-throughput and low-latency modes are unified under the `ElasticBuffer` interface [README.md113-115](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L113-L115)
 
 
### System Architecture Overview

 The following diagram bridges the high-level Python API to the underlying hardware transport entities.

 **DeepEP System Mapping**

 
```

```

 Sources: [README.md9-25](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L9-L25) [csrc/kernels/backend/nccl.cu62-143](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L62-L143)

 
---

 
## NCCL Gin Transport (V2)

 The NCCL Gin backend provides the core primitives for the `ElasticBuffer`. It manages symmetric memory windows across the cluster and provides GPU-side `put`, `get`, and `quiet` operations.

 
 - **Resource Management**: The `NCCLSymmetricMemoryContext` initializes the `ncclDevComm_t` with specific requirements such as `ginContextCount` (mapped to `num_allocated_qps`) and `ginTrafficClass` (mapped to `sl_idx`) [csrc/kernels/backend/nccl.cu82-99](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L82-L99)
 - **Topology Awareness**: The backend distinguishes between `num_nvl_ranks` (LSA size) and `num_rdma_ranks` to calculate scale-up and scale-out domain indices [csrc/kernels/backend/nccl.cu111-125](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L111-L125)
 - **Symmetric Memory**: Uses `ncclCommWindowRegister` to create a globally accessible memory window, allowing direct `ncclGetLsaDevicePointer` access for intranode peers [csrc/kernels/backend/nccl.cu129-148](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L129-L148)
 - **Fallback Mechanism**: Users can force a fallback from Gin via the `EP_DISABLE_GIN` environment variable [csrc/kernels/backend/nccl.cu86](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L86-L86)
 
 For details on the V2 transport architecture, see [NCCL Gin Transport (V2)](https://deepwiki.com/deepseek-ai/DeepEP/9.1-nccl-gin-transport-(v2)).

 Sources: [csrc/kernels/backend/nccl.cu62-148](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L62-L148) [csrc/kernels/backend/api.cuh47-93](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/api.cuh#L47-L93)

 
---

 
## Legacy NVSHMEM and IBGDA (V1)

 The V1 architecture relies on a patched version of **NVSHMEM** (3.3.9+) to provide **IBGDA** (InfiniBand GPUDirect Async) support. This allows CUDA kernels to initiate RDMA operations directly from the GPU.

 **V1 Integration Entity Mapping**

 
```

```

 Sources: [README.md39](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L39-L39) [README.md82-84](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L82-L84)

 
### IBGDA Requirements

 
 - **Driver**: `NV_PEER_MEM` or **GDRCopy** must be configured for peer-to-peer memory access.
 - **Patching**: A custom patch is required to enable advanced IBGDA features and correct connection timing at scale. Reference `docs/nvshmem.md` for setup.
 - **Runtime Lifecycle**: The legacy backend is managed via `deep_ep::nvshmem` namespace functions including `init`, `alloc`, and `barrier` [csrc/kernels/backend/api.cuh14-31](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/api.cuh#L14-L31)
 
 For details on the V1 hardware path, see [Legacy NVSHMEM and IBGDA Integration (V1)](https://deepwiki.com/deepseek-ai/DeepEP/9.2-legacy-nvshmem-and-ibgda-integration-(v1)).

 Sources: [csrc/kernels/backend/api.cuh14-31](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/api.cuh#L14-L31) [README.md9-39](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L9-L39)

 
---

 
## Sub-pages

 
 - [NCCL Gin Transport (V2)](https://deepwiki.com/deepseek-ai/DeepEP/9.1-nccl-gin-transport-(v2)) — Deep dive into the V2 backend, `ncclDevComm` configuration, and window registration.
 - [Legacy NVSHMEM and IBGDA Integration (V1)](https://deepwiki.com/deepseek-ai/DeepEP/9.2-legacy-nvshmem-and-ibgda-integration-(v1)) — Technical details on the NVSHMEM integration, IBGDA primitives, and legacy runtime lifecycle.
 
 Sources: [README.md9-39](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L9-L39) [csrc/kernels/backend/nccl.cu62-157](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L62-L157)
