> 来源: [https://deepwiki.com/deepseek-ai/DeepEP/5-nccl-gin-backend-and-kernel-architecture](https://deepwiki.com/deepseek-ai/DeepEP/5-nccl-gin-backend-and-kernel-architecture)
> DeepWiki deepseek-ai/DeepEP

# NCCL Gin Backend and Kernel Architecture

  Relevant source files 
 - [csrc/kernels/backend/api.cuh](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/api.cuh)
 - [csrc/kernels/backend/nccl.cu](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu)
 
  DeepEP V2 introduces a significant architectural shift from the V1 (NVSHMEM-based) design to a more flexible, JIT-compiled system centered around the **NCCL Gin** backend. This layer provides high-performance communication primitives for Mixture-of-Experts (MoE) token routing, utilizing a header-only kernel design that allows for aggressive template specialization based on runtime parameters like SM count, expert count, and quantization formats.

 
## Architecture Overview

 The V2 architecture is divided into three primary layers:

 
 - **NCCL Gin Backend**: A custom transport layer built on top of NCCL that provides low-level RDMA primitives (`put`, `get`, `quiet`) and symmetric memory management.
 - **Header-Only Kernel Templates**: Core logic for dispatch and combine operations resides in `deep_ep/include/deep_ep/impls/`. These are not compiled into the main library but are processed by the JIT system.
 - **JIT Compilation Pipeline**: A runtime system that parses headers, injects template parameters, and compiles optimized kernels using NVRTC.
 
 
### System Relationship Diagram

 The following diagram illustrates how the V2 components interact and relate to the legacy V1 system.

 **V2 Kernel and Backend Integration:**

 
```

```

 **Sources:** [csrc/kernels/backend/nccl.cu18-47](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L18-L47) [csrc/kernels/backend/api.cuh33-45](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/api.cuh#L33-L45)

 
---

 
## Elastic Kernels (V2)

 The V2 kernels are "elastic" because they adapt to the available hardware resources (SMs, QPs) and MoE configurations at runtime. Unlike V1, which used fixed warp roles in `.cu` files, V2 uses template parameters to define warp roles (notify, dispatch/scaleout, forward) and communication modes.

 
### Key Components:

 
 - **Dispatch & Combine**: Implemented as templates in `deep_ep/include/deep_ep/impls/`. The backend provides `NCCLSymmetricMemoryContext` to support these kernels with unified memory views across ranks [csrc/kernels/backend/nccl.cu62-67](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L62-L67)
 - **NCCLGin Handle**: A device-side structure providing RDMA primitives. It supports team tags like `World`, `LSA` (Local SM Area), and `Rail` to optimize topology-aware communication [csrc/kernels/backend/nccl.cu98-99](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L98-L99)
 - **Template Instantiation**: Kernels are specialized via the JIT system for constants like `kNumSMs`, `kNumQPs`, and `kNumExperts`.
 
 For details, see [Elastic Kernels (V2)](https://deepwiki.com/deepseek-ai/DeepEP/5.1-elastic-kernels-(v2)).

 **Sources:** [csrc/kernels/backend/nccl.cu82-99](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L82-L99) [csrc/kernels/backend/api.cuh47-93](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/api.cuh#L47-L93)

 
---

 
## JIT Compilation System

 DeepEP V2 moves kernel specialization from compile-time to runtime. This eliminates the "binary explosion" caused by many MoE configurations and allows for analytical SM tuning.

 
### Key Features:

 
 - **NVRTC-based Compiler**: Compiles kernels at runtime, controlled by environment variables like `EP_JIT_CACHE_DIR` and `EP_JIT_DEBUG`.
 - **Caching**: Uses signature/hash-based caching to avoid redundant compilations across process restarts.
 - **Include Parser**: Automatically resolves dependencies within the `deep_ep/include/` directory to build a complete compilation unit for NVRTC.
 
 For details, see [JIT Compilation System](https://deepwiki.com/deepseek-ai/DeepEP/5.2-jit-compilation-system).

 
---

 
## NCCL Backend Integration

 The NCCL Gin backend replaces NVSHMEM as the primary transport for V2. It utilizes NCCL's symmetric memory capabilities and window allocations to provide a robust RDMA-like interface.

 
### Backend Responsibilities:

 
 - **Symmetric Memory**: `NCCLSymmetricMemoryContext` manages window allocations across the cluster [csrc/kernels/backend/nccl.cu62-66](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L62-L66) It registers GPU memory using `ncclCommWindowRegister` [csrc/kernels/backend/nccl.cu140](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L140-L140)
 - **Domain Management**: Functions like `get_physical_domain_size` and `get_logical_domain_size` define the NVLink vs. RDMA topology based on NCCL teams (World vs. LSA) [csrc/kernels/backend/nccl.cu49-60](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L49-L60)
 - **Gin Configuration**: Configures NCCL device communication requirements including `ginContextCount` (QPs), `ginQueueDepth`, and `ginTrafficClass` (SL) [csrc/kernels/backend/nccl.cu83-99](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L83-L99)
 
 For details, see [NCCL Backend Integration](https://deepwiki.com/deepseek-ai/DeepEP/5.3-nccl-backend-integration).

 **Sources:** [csrc/kernels/backend/nccl.cu49-143](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L49-L143) [csrc/kernels/backend/api.cuh33-95](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/api.cuh#L33-L95)

 
---

 
## Legacy Kernels (V1)

 DeepEP maintains the V1 kernel suite for backward compatibility and as a reference for low-latency RDMA-only paths. These kernels are statically compiled and rely on NVSHMEM.

 
### V1 Modules:

 
 - **Internode**: Asymmetric NVLink+RDMA forwarding for training.
 - **Low-Latency (LL)**: Pure RDMA path optimized for inference decoding, supporting specialized formats like `UE8M0` and `LogFMT`.
 - **Intranode**: Pure NVLink communication using SM90 TMA (Tensor Memory Accelerator) features.
 - **NVSHMEM Backend**: Managed via `csrc/kernels/backend/nvshmem.cu` and defined in the `deep_ep::nvshmem` namespace [csrc/kernels/backend/api.cuh14-31](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/api.cuh#L14-L31)
 
 For details, see [Legacy Kernels (V1)](https://deepwiki.com/deepseek-ai/DeepEP/5.4-legacy-kernels-(v1)).

 **Sources:** [csrc/kernels/backend/api.cuh14-31](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/api.cuh#L14-L31)

 
---

 
## Code Entity Mapping

 The following diagram maps high-level system concepts to specific code entities within the V2 architecture.

 **Entity Mapping Diagram:**

 
```

```

 **Sources:** [csrc/kernels/backend/nccl.cu62-80](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L62-L80) [csrc/kernels/backend/nccl.cu108](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L108-L108) [csrc/kernels/backend/api.cuh47-93](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/api.cuh#L47-L93)

 
### Build and Compilation Summary

 The system orchestrates the build of the C++ backend and the preparation of the JIT environment.

 
| Component | Compilation Type | Key Files |
|---|---|---|
| Backend Integration | Static (at install) | nccl.cu, nvshmem.cu, cuda_driver.cu |
| Legacy Kernels | Static (at install) | legacy/internode.cu, legacy/intranode.cu |
| Elastic Kernels | JIT (at runtime) | impls/dispatch_impl.cuh, impls/combine_impl.cuh |
| Python Bindings | Static (at install) | python_api.cpp |

 **Sources:** [csrc/kernels/backend/nccl.cu1-10](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L1-L10) [csrc/kernels/backend/api.cuh1-105](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/api.cuh#L1-L105)
