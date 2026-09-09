> 来源: [https://deepwiki.com/deepseek-ai/DeepEP/7-c%2B%2B-runtime-and-build-system](https://deepwiki.com/deepseek-ai/DeepEP/7-c%2B%2B-runtime-and-build-system)
> DeepWiki deepseek-ai/DeepEP

# C++ Runtime and Build System

  Relevant source files 
 - [csrc/elastic/buffer.hpp](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp)
 - [setup.py](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/setup.py)
 
  The C++ Runtime layer bridges the Python API to high-performance CUDA kernels. In DeepEP V2, this layer manages the lifecycle of `ElasticBuffer` (V2) and `Buffer` (Legacy V1), orchestrates memory via NCCL Symmetric Memory, and handles the infrastructure for JIT compilation of kernels.

 
## Architecture Overview

 The C++ layer is primarily implemented in `csrc/` and exposed via `pybind11` in `csrc/python_api.cpp` [csrc/python_api.cpp1-20](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/python_api.cpp#L1-L20) It coordinates with the NCCL Gin backend for V2 features and NVSHMEM for legacy V1 features.

 
### Core C++ Entities

 
| Entity | Location | Role |
|---|---|---|
| deep_ep::elastic::ElasticBuffer | csrc/elastic/buffer.hpp19 | Primary V2 coordinator for MoE communication, PP, and Engram. |
| NCCLSymmetricMemoryContext | csrc/elastic/buffer.hpp54 | Manages V2 memory registration, RDMA windows, and QP allocation. |
| WorkspaceLayout | csrc/elastic/buffer.hpp35 | Defines the memory layout for metadata, barriers, and expert counting. |
| persistent_envs | setup.py13 | Stores build-time environment variables for runtime consistency in deep_ep/envs.py. |

 
### System to Code Mapping

 The following diagram illustrates how high-level system components map to specific C++ classes and files.

 **C++ Entity Mapping**

 
```

```

 **Sources:** [csrc/python_api.cpp1-39](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/python_api.cpp#L1-L39) [csrc/elastic/buffer.hpp18-54](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp#L18-L54) [setup.py112-127](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/setup.py#L112-L127)

 
## ElasticBuffer C++ Implementation

 `ElasticBuffer` is the core class for V2. It replaces the static buffer management of V1 with a flexible system that supports analytical SM tuning, handle caching, and multi-functional communication (EP, PP, Engram, AGRS).

 
 - **Constructor and Initialization**: The constructor [csrc/elastic/buffer.hpp81-140](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp#L81-L140) initializes the `NCCLSymmetricMemoryContext`, calculates the `WorkspaceLayout`, and sets up the `comm_stream`.
 - **Memory Layout**: It organizes memory into three contiguous segments: `Workspace`, `GPU buffer`, and `CPU buffer` [csrc/elastic/buffer.hpp21-25](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp#L21-L25)
 - **Kernel Dispatch**: Methods such as `dispatch`, `combine`, and `engram_fetch` are bound to Python and trigger JIT-compiled kernels via the `jit::KernelRuntime`.
 - **Resource Lifecycle**: Supports explicit destruction via `destroy()` [csrc/elastic/buffer.hpp152-166](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp#L152-L166) which performs a barrier and finalizes the NCCL context to prevent resource leaks.
 
 For implementation details, see [ElasticBuffer C++ Implementation](https://deepwiki.com/deepseek-ai/DeepEP/7.1-elasticbuffer-c++-implementation).

 **Sources:** [csrc/elastic/buffer.hpp18-166](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp#L18-L166) [csrc/python_api.cpp39](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/python_api.cpp#L39-L39)

 
## Memory Management and NCCL Symmetric Memory

 DeepEP V2 utilizes **NCCL Symmetric Memory** to provide a unified address space across the cluster, which is essential for the RDMA-based NCCL Gin backend.

 
 - **Window Allocation**: `NCCLSymmetricMemoryContext` manages the allocation of RDMA windows and handles the registration of symmetric memory across scale-out and scale-up domains [csrc/elastic/buffer.hpp110-114](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp#L110-L114)
 - **Workspace Layout**: The `WorkspaceLayout` is carved out at the front of the GPU segment and is aligned to 2 MB boundaries (`symmetric::kNumAlignmentBytes`) [csrc/elastic/buffer.hpp104-105](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp#L104-L105)
 - **Network Configuration**: It manages InfiniBand Queue Pairs (QPs) and service levels (SL) through parameters like `num_allocated_qps` and `sl_idx` [csrc/elastic/buffer.hpp87](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp#L87-L87)
 - **Timeouts**: Configures CPU and GPU timeout thresholds to handle network hangs or synchronization issues [csrc/elastic/buffer.hpp121-123](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp#L121-L123)
 
 For details on memory registration and layout, see [Memory Management and NCCL Symmetric Memory](https://deepwiki.com/deepseek-ai/DeepEP/7.2-memory-management-and-nccl-symmetric-memory).

 **Sources:** [csrc/elastic/buffer.hpp81-136](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp#L81-L136) [csrc/kernels/backend/nccl.cu1-20](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/kernels/backend/nccl.cu#L1-L20)

 
## Build System and Compilation Options

 DeepEP uses a `setup.py` script that leverages PyTorch's `CUDAExtension` to compile the C++ and CUDA source files.

 
### Build Pipeline Logic

 The build system identifies available libraries (NCCL, NVSHMEM) and configures the compiler flags based on the target hardware (SM90 for H100/H800 vs SM80 for A100).

 **Compilation and Build Flow**

 
```

```

 
### Key Build Configurations

 
 - **Persistent Environments**: Variables like `EP_JIT_CACHE_DIR`, `EP_NCCL_ROOT_DIR`, and `EP_NUM_TOPK_IDX_BITS` are captured during `setup.py` execution and written to `deep_ep/envs.py` via `CustomBuildPy` to ensure runtime consistency [setup.py13](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/setup.py#L13-L13) [setup.py78-90](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/setup.py#L78-L90)
 - **Library Discovery**: The script dynamically finds versioned shared objects (e.g., `libnccl.so.2` or `libnvshmem_host.so.3`) using `_find_versioned_so` to support both tarball and pip wheel installations [setup.py26-49](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/setup.py#L26-L49)
 - **Architecture Tuning**: It sets `TORCH_CUDA_ARCH_LIST` based on the `DISABLE_SM90_FEATURES` flag, defaulting to `9.0` for Hopper GPUs [setup.py130-146](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/setup.py#L130-L146)
 - **PTX Optimization**: Supports disabling aggressive PTX instructions (e.g., `.L1::no_allocate`) for compatibility with specific CUDA versions via `DISABLE_AGGRESSIVE_PTX_INSTRS` [setup.py153-155](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/setup.py#L153-L155)
 
 For build flags and setup instructions, see [Build System and Compilation Options](https://deepwiki.com/deepseek-ai/DeepEP/7.3-build-system-and-compilation-options).

 **Sources:** [setup.py13-18](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/setup.py#L13-L18) [setup.py26-49](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/setup.py#L26-L49) [setup.py71-165](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/setup.py#L71-L165)

 
## Page Hierarchy

 
 - [ElasticBuffer C++ Implementation](https://deepwiki.com/deepseek-ai/DeepEP/7.1-elasticbuffer-c++-implementation): Deep dive into the `deep_ep::elastic` namespace and public method signatures.
 - [Memory Management and NCCL Symmetric Memory](https://deepwiki.com/deepseek-ai/DeepEP/7.2-memory-management-and-nccl-symmetric-memory): Details on window allocation, QP management, and the initialization sequence.
 - [Build System and Compilation Options](https://deepwiki.com/deepseek-ai/DeepEP/7.3-build-system-and-compilation-options): Documentation of `setup.py`, environment variables, and JIT compilation flags.
