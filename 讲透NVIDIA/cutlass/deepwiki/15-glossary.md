<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cutlass · page 15 Glossary · fetched 2026-10-26 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [include/cutlass/gemm/collective/sm120_blockscaled_mma_array_tma.hpp](include/cutlass/gemm/collective/sm120_blockscaled_mma_array_tma.hpp)
- [include/cutlass/gemm/collective/sm120_blockscaled_mma_tma.hpp](include/cutlass/gemm/collective/sm120_blockscaled_mma_tma.hpp)
- [include/cutlass/gemm/collective/sm120_mma_array_tma_blockwise_scaling.hpp](include/cutlass/gemm/collective/sm120_mma_array_tma_blockwise_scaling.hpp)
- [include/cutlass/gemm/collective/sm120_mma_tma.hpp](include/cutlass/gemm/collective/sm120_mma_tma.hpp)
- [include/cutlass/gemm/collective/sm120_mma_tma_blockwise_scaling.hpp](include/cutlass/gemm/collective/sm120_mma_tma_blockwise_scaling.hpp)
- [include/cutlass/gemm/kernel/sm90_gemm_array_tma_warpspecialized_cooperative.hpp](include/cutlass/gemm/kernel/sm90_gemm_array_tma_warpspecialized_cooperative.hpp)
- [include/cutlass/gemm/kernel/sm90_gemm_array_tma_warpspecialized_pingpong.hpp](include/cutlass/gemm/kernel/sm90_gemm_array_tma_warpspecialized_pingpong.hpp)
- [include/cutlass/gemm/kernel/sm90_gemm_tma_warpspecialized_cooperative.hpp](include/cutlass/gemm/kernel/sm90_gemm_tma_warpspecialized_cooperative.hpp)
- [include/cutlass/gemm/kernel/sm90_gemm_tma_warpspecialized_pingpong.hpp](include/cutlass/gemm/kernel/sm90_gemm_tma_warpspecialized_pingpong.hpp)
- [include/cutlass/gemm/kernel/tile_scheduler_params.h](include/cutlass/gemm/kernel/tile_scheduler_params.h)
- [include/cutlass/version.h](include/cutlass/version.h)
- [media/docs/cpp/cute/02_layout_algebra.md](media/docs/cpp/cute/02_layout_algebra.md)
- [media/docs/cpp/cute/03_tensor.md](media/docs/cpp/cute/03_tensor.md)
- [media/docs/cpp/cute/0t_mma_atom.md](media/docs/cpp/cute/0t_mma_atom.md)
- [media/docs/cpp/cute/0x_gemm_tutorial.md](media/docs/cpp/cute/0x_gemm_tutorial.md)
- [python/CuTeDSL/cutlass/base_dsl/env_manager.py](python/CuTeDSL/cutlass/base_dsl/env_manager.py)
- [python/CuTeDSL/cutlass/base_dsl/runtime/cuda.py](python/CuTeDSL/cutlass/base_dsl/runtime/cuda.py)
- [python/CuTeDSL/cutlass/cute/__init__.py](python/CuTeDSL/cutlass/cute/__init__.py)
- [python/CuTeDSL/cutlass/cute/arch/nvvm_wrappers.py](python/CuTeDSL/cutlass/cute/arch/nvvm_wrappers.py)
- [python/CuTeDSL/cutlass/cute/core.py](python/CuTeDSL/cutlass/cute/core.py)
- [python/CuTeDSL/cutlass/jax/primitive.py](python/CuTeDSL/cutlass/jax/primitive.py)
- [python/CuTeDSL/requirements-cu13.txt](python/CuTeDSL/requirements-cu13.txt)
- [python/CuTeDSL/requirements.txt](python/CuTeDSL/requirements.txt)
- [python/cutlass_cppgen/__init__.py](python/cutlass_cppgen/__init__.py)
- [python/setup_cutlass.py](python/setup_cutlass.py)
- [python/setup_library.py](python/setup_library.py)
- [python/setup_pycute.py](python/setup_pycute.py)
- [test/unit/layout/tensor.cu](test/unit/layout/tensor.cu)
- [test/unit/layout/tensor_nhwc.cu](test/unit/layout/tensor_nhwc.cu)

</details>



This glossary defines codebase-specific terms, hardware-centric jargon, and domain concepts essential for navigating the CUTLASS repository. CUTLASS (CUDA Templates for Linear Algebra Subroutines and Solvers) is a collection of CUDA C++ and Python DSL abstractions for high-performance matrix-matrix multiplication (GEMM) and related computations [README.md:8-11]().

## Core Architectural Concepts

### GEMM (General Matrix Multiply)
The fundamental operation $C = \alpha AB + \beta C$. CUTLASS implements GEMM using a hierarchical decomposition strategy that maps to GPU hardware structures (Grid, Cluster, Threadblock, Warp, Thread) [README.md:8-15]().

### TMA (Tensor Memory Accelerator)
A hardware feature introduced in the NVIDIA Hopper (SM90) and Blackwell (SM100) architectures. TMA allows for asynchronous, multidimensional data movement between Global Memory (GMEM) and Shared Memory (SMEM) or TMEM without requiring thread-level address calculation [README.md:26-34]().
*   **TmaDescriptor**: A 128-byte hardware structure describing the shape, stride, and data type of a tensor for TMA operations. The library includes logic to detect TMA creation driver bugs related to tensor compactness [README.md:77-78]().
*   **TMA Multicast**: A feature where a single TMA load can broadcast data to multiple threadblocks within a cluster [README.md:97-99]().

### WGMMA / UMMA
*   **WGMMA (Warp Group MMA)**: SM90+ instructions that perform matrix multiply-accumulate operations at the warp-group level (128 threads).
*   **UMMA / tcgen05.mma**: Enhanced MMA instructions for the Blackwell architecture. CUTLASS 4.7 includes optimized support for these instructions to leverage Blackwell's increased throughput [README.md:30-34]().

### Warp Specialization
A software architecture pattern where different warps within a threadblock are assigned distinct roles, such as "Producers" (loading data via TMA) and "Consumers" (performing MMA math) [include/cutlass/gemm/kernel/sm90_gemm_tma_warpspecialized_pingpong.hpp:128-135]().
*   **Pingpong Schedule**: A scheduling policy where producers and consumers alternate work to overlap data movement and computation [include/cutlass/gemm/kernel/sm90_gemm_tma_warpspecialized_pingpong.hpp:69-70]().
*   **Cooperative Schedule**: A policy where multiple warp groups cooperate on a single large tile to maximize throughput [include/cutlass/gemm/kernel/sm90_gemm_array_tma_warpspecialized_cooperative.hpp:70-71]().

## CuTe (CUDA Layouts and Tensors)
CuTe is the foundational library for CUTLASS 3.x and 4.x, providing an algebraic approach to describing layouts and tensors [README.md:30-34]().

### Layout Algebra
*   **Shape**: The logical dimensions of a tensor [media/docs/cpp/cute/02_layout_algebra.md:31-33]().
*   **Stride**: The mapping from logical coordinates to physical memory offsets [media/docs/cpp/cute/02_layout_algebra.md:31-33]().
*   **Coalesce**: A "simplify" operation on layouts that reduces the number of modes without changing the logical function [media/docs/cpp/cute/02_layout_algebra.md:13-26]().
*   **Composition**: Applying one layout to another (e.g., $R(c) = A(B(c))$), used to create complex mappings like tiling or partitioning [media/docs/cpp/cute/02_layout_algebra.md:77-85]().

### MMA Atom & TiledMMA
*   **MMA Atom**: The smallest hardware-level MMA operation supported by the architecture.
*   **TiledMMA**: A CuTe abstraction that tiles an MMA Atom across a threadblock or warp group to form a larger logical operation [include/cutlass/gemm/kernel/sm90_gemm_array_tma_warpspecialized_cooperative.hpp:99]().

## Memory Hierarchy Symbols

| Symbol | Description | Code Pointer |
| :--- | :--- | :--- |
| **GMEM** | Global Memory (Device VRAM) | `ElementA`, `ElementB` pointers in `GemmUniversal` |
| **SMEM** | Shared Memory (On-chip, per-CTA) | `TileSchedulerStorage` [include/cutlass/gemm/kernel/sm90_gemm_tma_warpspecialized_pingpong.hpp:120]() |
| **TMEM** | Blackwell-specific Tensor Memory | Used for high-speed accumulator storage in SM100 kernels. |
| **RMEM** | Register Memory (Per-thread) | `RegsPerThread` calculation [include/cutlass/gemm/kernel/sm90_gemm_tma_warpspecialized_pingpong.hpp:143-144]() |

## Data Types and Formats

### MX Formats & Blockwise Scaling
NVIDIA Blackwell (SM100) and OCP standard formats (MXFP4, MXFP6, MXFP8) that use block-level scale factors to maintain high dynamic range at low precision [README.md:23-26]().
*   **BlockwiseScaling**: Implementation where inputs are scaled by shared exponents at a granular block level (e.g., 1x32 or 1x16 blocks) [include/cutlass/gemm/collective/sm120_mma_tma_blockwise_scaling.hpp:1-20]().
*   **NVF4 / FP4**: 4-bit floating point types (e2m1) supported on Blackwell, including optimized LUT decode helpers [README.md:73-74]().

### Mixed Precision
Operations where inputs (A, B) and accumulators/outputs (C, D) have different types. CUTLASS 4.7 adds enhanced support for FP8 (e4m3/e5m2) and FP4 (e2m1) [README.md:73-74]().

## Advanced Kernel Architectures

### StreamK
A work-decomposition strategy that improves load balancing by allowing "split-K" work to be dynamically scheduled across SMs, minimizing tail effect on irregular problem sizes.
*   **DP Blocks**: Data-parallel blocks that process a whole tile.
*   **SK Blocks**: Stream-K blocks that process partial tiles and require a reduction step.
*   **Heuristics**: CUTLASS 4.7 updated StreamK heuristics to optimize kernels with mixed cluster sizes [README.md:76]().

### FMHA (Fused Multi-Head Attention)
Highly optimized kernels for Transformer attention, fusing Softmax and MMA operations.
*   **MLA (Multi-head Latent Attention)**: A variant used in DeepSeek-style models, utilizing latent dimensions to reduce KV cache size.
*   **GQA / MQA**: Grouped-Query and Multi-Query Attention variants.
*   **2-Kernel Backward**: A Blackwell-specific optimization providing ~25% improvement over 1-kernel implementations at FP8 [README.md:69-71]().

### GDC (Grid Dependency Control) / PDL
A feature for programmatic dependent launches (PDL) allowing grids to wait on or trigger other grids directly on the GPU hardware [include/cutlass/gemm/kernel/sm90_gemm_array_tma_warpspecialized_cooperative.hpp:51]().

### Green Context
A Blackwell feature that supports SM partitioning, enabling the launch of GEMM on a stream with a partial SM allocation.

## Software Engineering & Build

### Collective
A design pattern where a group of threads (Warp or Warp Group) performs a coordinated operation.
*   **CollectiveMma**: Handles the loading of A/B tiles and the MMA math loop [include/cutlass/gemm/kernel/sm90_gemm_array_tma_warpspecialized_cooperative.hpp:97]().
*   **CollectiveEpilogue**: Handles the processing of accumulators and storing to C/D [include/cutlass/gemm/kernel/sm90_gemm_array_tma_warpspecialized_cooperative.hpp:115]().

### EVT (Epilogue Visitor Tree)
A flexible tree-based abstraction for defining complex fused operations in the GEMM epilogue (e.g., adding bias, applying activation functions, then quantizing).

### Dispatch Policy
A template parameter that determines the hardware-specific execution strategy [include/cutlass/gemm/kernel/sm90_gemm_array_tma_warpspecialized_cooperative.hpp:107]().

## System Mapping Diagrams

### Code Entity Space: GEMM Universal Hierarchy
The following diagram maps high-level GEMM concepts to specific C++ class templates in the CUTLASS 3.x/4.x hierarchy.

```mermaid
graph TD
    subgraph ["Natural Language Space"]
        A["Problem Specification"]
        B["Work Distribution"]
        C["Math Execution"]
        D["Output Processing"]
    end

    subgraph ["Code Entity Space"]
        A1["cutlass::gemm::kernel::GemmUniversal"]
        B1["cutlass::gemm::kernel::detail::TileSchedulerSelector"]
        C1["CollectiveMainloop"]
        D1["CollectiveEpilogue"]
        
        A --> A1
        B --> B1
        C --> C1
        D --> D1
        
        A1 --> B1
        A1 --> C1
        A1 --> D1
    end
```
*Sources: [include/cutlass/gemm/kernel/sm90_gemm_array_tma_warpspecialized_cooperative.hpp:65-123]()*

### Code Entity Space: Python DSL Compilation Pipeline
Mapping of the CuTe DSL components from Python to hardware execution.

```mermaid
graph LR
    subgraph ["Python DSL Space"]
        DSL["@cute.jit / @cute.kernel"]
        FFI["TVM FFI / DLPack"]
    end

    subgraph ["Compiler Stack"]
        IR["CuTe IR (MLIR Dialect)"]
        CppGen["cutlass_cppgen"]
        NVCC["NVCC / NVRTC"]
    end

    subgraph ["Runtime Space"]
        Executor["cute.compile_to"]
        CudaRuntime["cuda-python"]
    end

    DSL --> IR
    IR --> CppGen
    CppGen --> NVCC
    NVCC --> Executor
    FFI --> Executor
    Executor --> CudaRuntime
```
*Sources: [python/cutlass_cppgen/__init__.py:136-161](), [CHANGELOG.md:58-65]()*

## Glossary Table

| Term | Code Pointer | Context |
| :--- | :--- | :--- |
| **cutlass_cppgen** | `python/cutlass_cppgen/__init__.py` | Python package for generating C++ CUTLASS kernels [python/cutlass_cppgen/__init__.py:53](). |
| **pycute** | `python/setup_pycute.py` | Python implementation of CuTe core abstractions [python/setup_pycute.py:38-41](). |
| **cutlass_library** | `python/setup_library.py` | Scripts and manifests for kernel library generation [python/setup_library.py:38-41](). |
| **Primitives API** | `README.md:49-52` | Low-level SIMT wrapper over NVVM operations in CuTe DSL. |
| **IKET** | `CHANGELOG.md:61-62` | In-Kernel-Event-Tracing profiler for intra-kernel activity. |
| **StreamK** | `include/cutlass/gemm/kernel/sm90_tile_scheduler.hpp` | Dynamic work-balancing tile scheduler for SM90+ [include/cutlass/gemm/kernel/sm90_gemm_array_tma_warpspecialized_cooperative.hpp:49](). |
| **EVT** | `python/cutlass_cppgen/backend/evt/ir/tensor.py` | Epilogue Visitor Tree for fused operations [python/cutlass_cppgen/__init__.py:144](). |

*Sources: [README.md:46-80](), [CHANGELOG.md:5-40](), [python/cutlass_cppgen/__init__.py:136-146]()*