> 来源: [https://deepwiki.com/deepseek-ai/DeepGEMM/4-kernel-implementations](https://deepwiki.com/deepseek-ai/DeepGEMM/4-kernel-implementations)
> DeepWiki deepseek-ai/DeepGEMM

# Kernel Implementations

  Relevant source files 
 - [csrc/apis/layout.hpp](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/apis/layout.hpp)
 - [csrc/jit_kernels/impls/sm100_bf16_gemm.hpp](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/impls/sm100_bf16_gemm.hpp)
 - [csrc/jit_kernels/impls/sm90_bf16_gemm.hpp](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/impls/sm90_bf16_gemm.hpp)
 - [deep_gemm/include/deep_gemm/common/utils.cuh](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/include/deep_gemm/common/utils.cuh)
 - [deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh)
 
  This document provides a comprehensive overview of the CUDA kernel implementations in DeepGEMM. It covers the organization and structure of kernels across different GPU architectures (SM90/SM100), operation types (GEMM, Attention, Einsum, Layout), and data types (FP8, BF16, FP4).

 For detailed implementation specifics of SM90 kernels, see [SM90 Kernel Implementations](https://deepwiki.com/deepseek-ai/DeepGEMM/4.1-sm90-kernel-implementations). For SM100 kernels, see [SM100 Kernel Implementations](https://deepwiki.com/deepseek-ai/DeepGEMM/4.2-sm100-kernel-implementations). For specialized MQA kernel details, see [MQA Kernel Implementation](https://deepwiki.com/deepseek-ai/DeepGEMM/4.3-mqa-kernel-implementation). For Mega MoE specific fused kernels, see [Mega MoE Kernel Implementation](https://deepwiki.com/deepseek-ai/DeepGEMM/4.4-mega-moe-kernel-implementation). Memory management and synchronization patterns are covered in [Memory Management and Synchronization](https://deepwiki.com/deepseek-ai/DeepGEMM/4.5-memory-management-and-synchronization).

 
## Kernel Organization

 DeepGEMM's kernel implementations are organized by GPU architecture and operation type. All kernel headers are located in the `deep_gemm/include/deep_gemm/impls/` directory, with each kernel implementing a specific combination of architecture, data type, and operation.

 The kernel organization follows a clear naming convention: `{architecture}_{datatype}_{operation}`. For example, `sm100_fp8_gemm_1d1d` is an SM100 (Blackwell) kernel for FP8 data performing GEMM with 1D cluster and 1D output tiling.

 **Kernel Categories by Architecture**

 
```

```

 Sources: [deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh39-48](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh#L39-L48) [csrc/jit_kernels/impls/sm90_bf16_gemm.hpp34-46](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/impls/sm90_bf16_gemm.hpp#L34-L46) [csrc/jit_kernels/impls/sm100_bf16_gemm.hpp36-51](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/impls/sm100_bf16_gemm.hpp#L36-L51)

 
## Kernel Catalog

 The following table maps primary kernel implementations to their specific purposes and source files:

 
| Kernel File | Architecture | Data Type | Operation | Key Features |
|---|---|---|---|---|
| sm90_fp8_gemm_1d1d.cuh | SM90 | FP8 | GEMM | WGMMA, TMA Multicast, ClusterTransactionBarrier deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh59-60 |
| sm90_bf16_gemm.cuh | SM90 | BF16 | GEMM | WGMMA, TMA, Cluster support csrc/jit_kernels/impls/sm90_bf16_gemm.hpp29-30 |
| sm100_bf16_gemm.cuh | SM100 | BF16 | GEMM | UMMA, TMEM, Blackwell-specific scheduling csrc/jit_kernels/impls/sm100_bf16_gemm.hpp31-33 |
| smxx_layout.cuh | SM90/100 | Utility | Layout | TMA alignment, UE8M0 scaling factor packing csrc/apis/layout.hpp41-61 |

 Sources: [deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh1-143](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh#L1-L143) [csrc/jit_kernels/impls/sm90_bf16_gemm.hpp1-130](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/impls/sm90_bf16_gemm.hpp#L1-L130) [csrc/jit_kernels/impls/sm100_bf16_gemm.hpp1-131](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/impls/sm100_bf16_gemm.hpp#L1-L131)

 
## GEMM Kernel Variants

 DeepGEMM implements multiple GEMM kernel variants to handle different problem shapes and memory access patterns. The variants differ in their clustering strategy, output tiling, and supported transpose modes.

 **GEMM Kernel Type Mapping**

 
```

```

 Sources: [deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh53](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh#L53-L53) [csrc/jit_kernels/impls/sm90_bf16_gemm.hpp85-95](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/impls/sm90_bf16_gemm.hpp#L85-L95) [csrc/jit_kernels/impls/sm100_bf16_gemm.hpp143-146](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/impls/sm100_bf16_gemm.hpp#L143-L146)

 
### 1D1D vs 1D2D Kernels

 The distinction between `1d1d` and `1d2d` kernels refers to their clustering and output tiling strategy:

 
 - **1D1D**: Uses 1-dimensional thread block clusters and produces 1D output tiles. This is the primary kernel variant used for most operations.
 - **1D2D**: Uses 1-dimensional thread block clusters but produces 2-dimensional output tiles, enabling larger effective tile sizes.
 
 For BF16 operations on SM100, the implementation leverages `sm100_bf16_gemm_impl` which handles various layout configurations including `MGroupedContiguousWithPsumLayout` [csrc/jit_kernels/impls/sm100_bf16_gemm.hpp143-146](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/impls/sm100_bf16_gemm.hpp#L143-L146)

 
## Common Kernel Structure (SM90 Example)

 DeepGEMM kernels for SM90 follow a pattern utilizing Hopper-specific features like WGMMA and TMA:

 **SM90 Implementation Flow**

 
```

```

 Sources: [deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh82-143](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh#L82-L143) [deep_gemm/include/deep_gemm/common/utils.cuh11-22](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/include/deep_gemm/common/utils.cuh#L11-L22)

 
## Template Instantiation Strategy

 Each kernel header defines template functions that are instantiated by the JIT compiler. Key parameters include:

 
 - **Shapes**: `SHAPE_M`, `SHAPE_N`, `SHAPE_K` [deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh30](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh#L30-L30)
 - **Tiling**: `BLOCK_M`, `BLOCK_N`, `BLOCK_K` [deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh32](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh#L32-L32)
 - **Pipeline**: `kNumStages` [deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh34](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh#L34-L34)
 - **Thread Config**: `kNumTMAThreads`, `kNumMathThreads` [deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh35](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh#L35-L35)
 
 This approach allows a single kernel implementation to support multiple configurations while enabling the compiler to fully optimize each instantiation for the specific problem shape. For example, `sm90_bf16_gemm_impl` is instantiated with specific `GemmType` and `cd_dtype` to handle accumulation and output precision [csrc/jit_kernels/impls/sm90_bf16_gemm.hpp34-46](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/impls/sm90_bf16_gemm.hpp#L34-L46)

 
## JIT Compilation and Kernel Dispatch

 DeepGEMM utilizes a JIT (Just-In-Time) compilation pipeline to generate and build optimized kernels at runtime. The `LaunchRuntime` classes (e.g., `SM90BF16GemmRuntime`) manage the string-based code generation and kernel launching [csrc/jit_kernels/impls/sm90_bf16_gemm.hpp14](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/impls/sm90_bf16_gemm.hpp#L14-L14)

 **JIT Compilation Flow**

 
```

```

 The `generate_impl` function uses `fmt::format` to inject compile-time constants into the C++ source code, which is then compiled into a `KernelHandle` for execution [csrc/jit_kernels/impls/sm90_bf16_gemm.hpp27-66](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/impls/sm90_bf16_gemm.hpp#L27-L66) Layout transformations, such as packing scaling factors for SM100, are performed before kernel launch to ensure compatibility with hardware requirements [csrc/apis/layout.hpp49-54](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/apis/layout.hpp#L49-L54)
