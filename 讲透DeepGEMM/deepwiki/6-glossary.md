> 来源: [https://deepwiki.com/deepseek-ai/DeepGEMM/6-glossary](https://deepwiki.com/deepseek-ai/DeepGEMM/6-glossary)
> DeepWiki deepseek-ai/DeepGEMM

# Glossary

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/README.md?plain=1)
 - [csrc/jit/compiler.hpp](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/compiler.hpp)
 - [csrc/jit/device_runtime.hpp](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/device_runtime.hpp)
 - [csrc/jit_kernels/heuristics/common.hpp](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/heuristics/common.hpp)
 - [csrc/jit_kernels/heuristics/sm100.hpp](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/heuristics/sm100.hpp)
 - [csrc/jit_kernels/heuristics/sm90.hpp](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/heuristics/sm90.hpp)
 - [csrc/jit_kernels/impls/smxx_layout.hpp](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/impls/smxx_layout.hpp)
 - [csrc/utils/system.hpp](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/utils/system.hpp)
 - [deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh)
 - [deep_gemm/utils/math.py](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/utils/math.py)
 - [tests/test_fp8_fp4.py](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/tests/test_fp8_fp4.py)
 - [tests/test_layout.py](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/tests/test_layout.py)
 
  This page provides definitions for codebase-specific terms, hardware-specific jargon, and domain concepts used throughout DeepGEMM. It serves as a technical reference for onboarding engineers to understand the implementation details and data flow within the library.

 
## Core Concepts and Terminology

 
### Data Types and Numerical Formats

 
 - **FP8 (E4M3)**: An 8-bit floating-point format (1 sign bit, 4 exponent bits, 3 mantissa bits). Used for activations and weights in high-performance GEMM operations [README.md65-69](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/README.md?plain=1#L65-L69)
 - **FP4**: A 4-bit floating-point format introduced for Blackwell (SM100). DeepGEMM supports mixed FP8/FP4 GEMM and MoE operations [README.md3](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/README.md?plain=1#L3-L3) [README.md11-13](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/README.md?plain=1#L11-L13)
 - **UE8M0**: An alternate 8-bit floating-point format (unsigned exponent 8-bit, 0-bit mantissa) used specifically for scaling factors on the SM100 architecture. DeepGEMM packs four UE8M0 values into a single `torch.int` [README.md69-71](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/README.md?plain=1#L69-L71) [csrc/jit_kernels/impls/smxx_layout.hpp155-178](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/impls/smxx_layout.hpp#L155-L178)
 - **Scaling Factor (SF)**: Multipliers used to dequantize FP8/FP4 values to higher precision. SM90 requires SFs in FP32 format, while SM100 requires them in packed UE8M0 format [README.md67-71](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/README.md?plain=1#L67-L71)
 - **TF32 (Tensor Float 32)**: A format providing FP32 range with FP16 precision. Used in DeepGEMM for hyperconnection kernels such as `tf32_hc_prenorm_gemm` [README.md3](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/README.md?plain=1#L3-L3)
 
 
### GEMM Variants

 
 - **NT / NN / TN / TT**: Notation for matrix multiplication $D = C + A \times B$. 
 - **N**: Non-transposed (Row-Major).
 - **T**: Transposed (Column-Major).
 - Example: `fp8_gemm_nt` performs $A \times B^T$ [README.md65-66](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/README.md?plain=1#L65-L66)
 - **M-Grouped (Contiguous)**: A GEMM where the M-axis is partitioned into multiple segments (e.g., experts in MoE), but N and K remain fixed. Tokens are concatenated into a single "contiguous" tensor [README.md78-81](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/README.md?plain=1#L78-L81)
 - **M-Grouped (Masked)**: Used during inference decoding with CUDA graphs. A mask tensor determines which portions of the experts are computed when CPU-side token counts are unknown [README.md84-88](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/README.md?plain=1#L84-L88)
 - **K-Grouped**: Grouping along the K-axis, primarily used for MoE weight backward operations where M and N are fixed [README.md82-83](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/README.md?plain=1#L82-L83)
 
 
## System Architecture Entities

 The following diagram maps high-level system components to their specific C++ classes and implementation files.

 
### Component Mapping: Natural Language to Code

 
```

```

 Sources: [csrc/jit/compiler.hpp23](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/compiler.hpp#L23-L23) [csrc/jit/device_runtime.hpp14](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/device_runtime.hpp#L14-L14) [deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh39-40](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh#L39-L40) [csrc/jit_kernels/impls/smxx_layout.hpp15](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/impls/smxx_layout.hpp#L15-L15)

 
## Hardware-Specific Terms (SM90/SM100)

 
### TMA (Tensor Memory Accelerator)

 A hardware unit introduced in Hopper (SM90) and enhanced in Blackwell (SM100) that handles multi-dimensional data transfers between Global Memory and Shared Memory asynchronously.

 
 - **TmaDescriptor**: A hardware structure describing the layout of a tensor for TMA operations. In code, these are often passed as `__grid_constant__ cute::TmaDescriptor` [deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh44-48](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh#L44-L48)
 - **TMA Multicast**: A feature allowing a single TMA load to broadcast data to multiple Thread Block Clusters (CTAs) simultaneously [deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh36](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh#L36-L36)
 
 
### TMEM (Tensor Memory)

 A specialized on-chip memory in the SM100 (Blackwell) architecture used to store intermediate results and accumulators for UMMA instructions.

 
 - **TMEM Alignment**: Scale factors on SM100 must be aligned to TMEM requirements, handled by `get_sf_uttcp_aligned_block_sizes` [csrc/jit_kernels/heuristics/sm100.hpp17-18](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/heuristics/sm100.hpp#L17-L18)
 
 
### MMA / UMMA Instructions

 
 - **WGMMA (Warp Group MMA)**: SM90 instructions for matrix-matrix multiplication performed by a group of 4 warps. DeepGEMM uses `mma::sm90::FP8MMASelector` to choose the appropriate instruction [deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh59](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh#L59-L59)
 - **UMMA (Unified MMA)**: SM100 instructions that utilize TMEM for accumulation. DeepGEMM uses `cute::UMMA` for managing these operations [csrc/jit_kernels/heuristics/sm100.hpp98](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/heuristics/sm100.hpp#L98-L98)
 
 
## Kernel Execution Flow

 The GEMM execution involves a complex pipeline of TMA loads, MMA/WGMMA computations, and epilogue processing, synchronized via hardware barriers.

 
### Data Flow: Global Memory to Output (SM90)

 
```

```

 Sources: [deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh44-48](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh#L44-L48) [deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh60](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh#L60-L60) [deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh103-116](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh#L103-L116) [deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh138-141](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh#L138-L141)

 
## Codebase Abbreviations

 
| Term | Full Name / Description | Code Pointer |
|---|---|---|
| SF | Scaling Factor (for FP8/FP4 quantization) | README.md67-71 |
| MQA | Multi-Query Attention | README.md90-92 |
| Smem | Shared Memory | deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh68 |
| CTA | Cooperative Thread Array (Thread Block) | deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh135-136 |
| JIT | Just-In-Time Compilation | README.md3 |
| LHS / RHS | Left-Hand Side (Matrix A) / Right-Hand Side (Matrix B) | README.md67 |
| SASS | Shader Assembly (low-level GPU assembly) | csrc/jit/compiler.hpp124-127 |
| CUBIN | CUDA Binary | csrc/jit/compiler.hpp115 |

 
## Internal Logic Definitions

 
 - **PatternVisitor**: A utility template used to access indexed shared memory buffers (like stages in a pipeline) with consistent pointer arithmetic [deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh104-116](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh#L104-L116)
 - **ClusterTransactionBarrier**: A synchronization primitive used to coordinate asynchronous TMA transfers across a cluster of SMs [deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh60](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh#L60-L60)
 - **GemmType**: An enumeration defining the layout and grouping logic of the GEMM (e.g., `Normal`, `MGroupedContiguous`, `KGroupedContiguous`) [deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh53](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh#L53-L53)
 - **DeviceRuntime**: A singleton class managing GPU properties, cuBLASLt handles, and architecture detection [csrc/jit/device_runtime.hpp14-15](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/device_runtime.hpp#L14-L15) [csrc/jit/device_runtime.hpp136](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/device_runtime.hpp#L136-L136)
 - **Mega MoE**: A fused kernel architecture that overlaps EP (Expert Parallelism) dispatch/combine with dual-linear compute [README.md114-116](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/README.md?plain=1#L114-L116)
 - **Compiler**: The base class for the JIT compilation system, handling cache directories and build signatures [csrc/jit/compiler.hpp23](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/compiler.hpp#L23-L23)
 - **Heuristics**: Logic to select optimal `GemmConfig` (block sizes, clusters, stages) based on `GemmDesc` and architecture specs [csrc/jit_kernels/heuristics/common.hpp14](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/heuristics/common.hpp#L14-L14)
 
 Sources: [README.md1-120](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/README.md?plain=1#L1-L120) [csrc/jit/compiler.hpp23-149](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/compiler.hpp#L23-L149) [csrc/jit/device_runtime.hpp14-138](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/device_runtime.hpp#L14-L138) [deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh30-141](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh#L30-L141) [csrc/jit_kernels/impls/smxx_layout.hpp15-180](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/impls/smxx_layout.hpp#L15-L180) [csrc/jit_kernels/heuristics/sm100.hpp14-148](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/heuristics/sm100.hpp#L14-L148) [csrc/jit_kernels/heuristics/sm90.hpp13-118](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/heuristics/sm90.hpp#L13-L118) [csrc/jit_kernels/heuristics/common.hpp14-52](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit_kernels/heuristics/common.hpp#L14-L52)
