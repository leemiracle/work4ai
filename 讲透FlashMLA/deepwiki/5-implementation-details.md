> 来源: [https://deepwiki.com/deepseek-ai/FlashMLA/5-implementation-details](https://deepwiki.com/deepseek-ai/FlashMLA/5-implementation-details)
> DeepWiki deepseek-ai/FlashMLA

# Implementation Details

  Relevant source files 
 - [csrc/sm100/helpers.h](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/csrc/sm100/helpers.h)
 - [csrc/sm90/decode/dense/config.h](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/csrc/sm90/decode/dense/config.h)
 - [setup.py](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/setup.py)
 
  This page provides technical details about FlashMLA's kernel implementations, architecture-specific primitives, and low-level optimizations. The content focuses on the internal CUDA kernel structure across different GPU architectures (SM90/SM100) and operation types (decoding/prefill, dense/sparse attention).

 For information about using the API, see [API Reference](https://deepwiki.com/deepseek-ai/FlashMLA/3-api-reference). For high-level architecture and design decisions, see [Architecture and Implementation](https://deepwiki.com/deepseek-ai/FlashMLA/4-architecture-and-implementation).

 
## Kernel Dispatch Architecture

 FlashMLA's kernel dispatch is implemented in `csrc/api/api.cpp` through the `flash_mla_with_kvcache` and `flash_mla_sparse_fwd` functions, which route to architecture- and configuration-specific kernels based on GPU capabilities and attention patterns.

 **Dispatch Factors:**

 
 - GPU architecture (SM90 vs SM100)
 - Attention pattern (dense vs sparse)
 - KV cache format (BF16 vs FP8)
 - Data type (BF16 vs FP16)
 
 **Kernel Dispatch Flow Diagram**

 
```

```

 Sources: [csrc/api/api.cpp15](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/csrc/api/api.cpp#L15-L15) [csrc/api/api.cpp15](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/csrc/api/api.cpp#L15-L15)

 
## Kernel Implementation Matrix

 The following table shows which kernel implementations exist for each combination of architecture, operation type, attention pattern, and data format:

 
| Architecture | Operation | Attention | KV Cache Format | Implementation Location | Status |
|---|---|---|---|---|---|
| SM90 | Decoding | Dense | BF16/FP16 | csrc/sm90/decode/dense/ | ✓ Supported |
| SM90 | Decoding | Sparse | FP8 | csrc/sm90/decode/sparse_fp8/ | ✓ Supported |
| SM90 | Prefill | Sparse | BF16 | csrc/sm90/prefill/sparse/ | ✓ Supported |
| SM100 | Decoding | Sparse | FP8 | csrc/sm100/decode/ | ✓ Supported |
| SM100 | Prefill | Sparse | BF16 | csrc/sm100/prefill/sparse/ | ✓ Supported |
| SM100 | Prefill | Dense | BF16 | csrc/sm100/prefill/dense/ | ✓ Supported (fwd+bwd) |

 **Key Observations:**

 
 - SM90 supports dense decoding with BF16/FP16 and sparse decoding with FP8.
 - SM100 provides high-performance dense prefill (FMHA) with both forward and backward passes using CUTLASS.
 - FP8 KV cache is optimized for sparse attention patterns using specific block scaling.
 - Sparse prefill operations use multi-phase kernels (e.g., `phase1_k512.cu`) to handle large head dimensions.
 
 Sources: [setup.py73-105](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/setup.py#L73-L105) [csrc/api/api.cpp15](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/csrc/api/api.cpp#L15-L15)

 
## Common Implementation Patterns

 
### Warp Specialization

 FlashMLA kernels use warp specialization to maximize hardware utilization by assigning different roles to different warp groups. This is critical for SM100 FMHA kernels to overlap TMA data movement with UMMA compute.

 **SM100 Warp Role Assignment (Example)**

 
```

```

 In the SM100 backward pass, roles are even more granular, separating MMA operations from reduction and compute warps to maximize pipeline depth.

 For details, see [SM100 Backward Pass Architecture](https://deepwiki.com/deepseek-ai/FlashMLA/5.3-sm100-backward-pass-architecture).

 
### Pipeline Stages and Synchronization

 Kernels use multiple pipeline stages to overlap computation with memory operations. SM100 kernels define numerous pipeline types for different producer-consumer relationships, coordinated via `cutlass::Pipeline`.

 **SM100 Pipeline Coordination**

 
| Pipeline Type | Usage |
|---|---|
| MainloopPipeline | Manages K/V data loading into shared memory |
| TmaDescriptorPipeline | Prefetches TMA descriptors for upcoming tiles |
| SmemBarrier | Synchronizes shared memory access between producer and consumer warps |

 Sources: [csrc/sm100/prefill/dense/fmha_cutlass_bwd_sm100.cu10-50](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/csrc/sm100/prefill/dense/fmha_cutlass_bwd_sm100.cu#L10-L50)

 
### Tile Sizes and Block Dimensions

 Different kernels use different tile configurations optimized for their specific computation patterns. For MLA, these are often fixed to match the DeepSeek model architecture.

 
| Parameter | Value | File Reference |
|---|---|---|
| BLOCK_SIZE_M | 64 | csrc/sm90/decode/dense/config.h5 |
| PAGE_BLOCK_SIZE | 64 | csrc/sm90/decode/dense/config.h6 |
| HEAD_DIM_K | 576 | csrc/sm90/decode/dense/config.h8 |
| HEAD_DIM_V | 512 | csrc/sm90/decode/dense/config.h9 |

 For details, see [SM90 Kernels (Hopper)](https://deepwiki.com/deepseek-ai/FlashMLA/5.1-sm90-kernels-(hopper)).

 
## Memory Hierarchy

 
### Shared Memory Organization

 FlashMLA kernels carefully organize shared memory to maximize throughput and enable overlapping of computation phases. Shared memory is used as a staging area for TMA loads and as a buffer for UMMA inputs.

 For details, see [TMA Operations and Memory Hierarchy](https://deepwiki.com/deepseek-ai/FlashMLA/5.4-tma-operations-and-memory-hierarchy).

 
### TMEM (Tensor Memory) on SM100

 SM100 introduces TMEM, a fast on-chip memory separate from shared memory, used for accumulating intermediate results and storing MMA operands. TMEM allocation is managed per-SM and must be explicitly allocated/freed.

 **TMEM Lifecycle in SM100 Kernels**

 
 - **Allocation**: Compute warps allocate TMEM slices for accumulation.
 - **Compute**: UMMA instructions read from Shared Memory and write to TMEM.
 - **Epilogue**: Results are moved from TMEM to Shared Memory or Global Memory via TMA.
 
 For details, see [SM100 Kernels (Blackwell)](https://deepwiki.com/deepseek-ai/FlashMLA/5.2-sm100-kernels-(blackwell)).

 
## FP8 Quantization and Dequantization

 FlashMLA supports FP8 E4M3 format for KV cache compression. The FP8 KV cache layout stores quantized K and V values along with per-group scaling factors.

 
### FP8 KV Cache Scaling

 The implementation provides helpers to convert FP8 values to BF16 using scales:

 
```

```

 Sources: [csrc/sm100/helpers.h25-33](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/csrc/sm100/helpers.h#L25-L33)

 
## Architecture Primitives and Utilities

 The codebase includes a robust set of utilities for architecture detection and error handling.

 
 - **Dispatcher Pattern**: `ImplBase` provides a unified interface for kernel execution across architectures.
 - **Arch Detection**: The `Arch` struct identifies the current GPU (SM90/SM100).
 - **CUDA Macros**: `FLASH_MLA_CUDA_CHECK` ensures all asynchronous operations are validated.
 
 For details, see [Architecture Primitives and Utilities](https://deepwiki.com/deepseek-ai/FlashMLA/5.5-architecture-primitives-and-utilities).
