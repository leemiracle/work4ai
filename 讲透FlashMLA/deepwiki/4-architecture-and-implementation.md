> 来源: [https://deepwiki.com/deepseek-ai/FlashMLA/4-architecture-and-implementation](https://deepwiki.com/deepseek-ai/FlashMLA/4-architecture-and-implementation)
> DeepWiki deepseek-ai/FlashMLA

# Architecture and Implementation

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/README.md?plain=1)
 - [docs/20250422-new-kernel-deep-dive.md](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/docs/20250422-new-kernel-deep-dive.md?plain=1)
 - [docs/20250929-hopper-fp8-sparse-deep-dive.md](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/docs/20250929-hopper-fp8-sparse-deep-dive.md?plain=1)
 - [setup.py](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/setup.py)
 
  
## Purpose and Scope

 This page provides a high-level overview of FlashMLA's architecture, explaining how the system is organized into layers, how kernels are structured across different GPU architectures, and the key design decisions that enable high performance. For detailed implementation specifics, see the child pages: System Architecture Overview ([System Architecture Overview](https://deepwiki.com/deepseek-ai/FlashMLA/4.1-system-architecture-overview)), FP8 KV Cache Format and Quantization ([FP8 KV Cache Format and Quantization](https://deepwiki.com/deepseek-ai/FlashMLA/4.2-fp8-kv-cache-format-and-quantization)), Tile Scheduler and Split-KV Strategy ([Tile Scheduler and Split-KV Strategy](https://deepwiki.com/deepseek-ai/FlashMLA/4.3-tile-scheduler-and-split-kv-strategy)), Kernel Performance Optimizations ([Kernel Performance Optimizations](https://deepwiki.com/deepseek-ai/FlashMLA/4.4-kernel-performance-optimizations)), and Sparse Attention Implementation ([Sparse Attention Implementation](https://deepwiki.com/deepseek-ai/FlashMLA/4.5-sparse-attention-implementation)). For kernel-specific details, refer to SM90 Kernels ([SM90 Kernels (Hopper)](https://deepwiki.com/deepseek-ai/FlashMLA/5.1-sm90-kernels-(hopper))) and SM100 Kernels ([SM100 Kernels (Blackwell)](https://deepwiki.com/deepseek-ai/FlashMLA/5.2-sm100-kernels-(blackwell))).

 
## Three-Layer Architecture

 FlashMLA follows a three-layer design that separates user-facing APIs from low-level GPU implementations:

 
```

```

 **Layer 1: Python API** - Provides high-level interfaces with PyTorch integration. The `FlashMLASchedMeta` class [flash_mla/flash_mla_interface.py9-35](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/flash_mla/flash_mla_interface.py#L9-L35) caches scheduling metadata across calls to avoid recomputation. The API automatically selects between sparse and dense modes based on whether the `indices` tensor is provided [flash_mla/flash_mla_interface.py151-170](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/flash_mla/flash_mla_interface.py#L151-L170)

 **Layer 2: C++ Extension** - Compiled via `setup.py` [setup.py62-134](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/setup.py#L62-L134) into `flash_mla.cuda.so`. This layer performs architecture detection using the `Arch` struct and validates that requested features are supported on the detected GPU architecture. The dispatcher pattern ensures kernels only execute with valid configurations.

 **Layer 3: CUDA Kernels** - Architecture-specific implementations optimized for SM90 (Hopper) and SM100 (Blackwell). Kernels are compiled conditionally based on `FLASH_MLA_DISABLE_SM90` and `FLASH_MLA_DISABLE_SM100` flags [setup.py36-46](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/setup.py#L36-L46)

 Sources: [flash_mla/flash_mla_interface.py1-435](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/flash_mla/flash_mla_interface.py#L1-L435) [setup.py1-151](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/setup.py#L1-L151) [README.md1-234](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/README.md?plain=1#L1-L234)

 
## Kernel Organization Matrix

 FlashMLA kernels are organized along three dimensions: GPU architecture, operation phase, and attention mode.

 
```

```

 
| Operation | Sparsity | SM90 Support | SM100 Support | Key Features |
|---|---|---|---|---|
| Decode | Dense | ✓ FP16/BF16 | ✗ Not available | Memory-bound, 3000 GB/s README.md35 |
| Decode | Sparse | ✓ FP8 KV cache | ✓ FP8 KV cache | 410 TFlops (SM90), 350 TFlops (SM100) README.md35 |
| Prefill | Dense | ✗ Not available | ✓ FMHA with bwd | 1460 TFlops fwd, 1000 TFlops bwd README.md43 |
| Prefill | Sparse | ✓ k512/k576 | ✓ head64/128 | 640 TFlops (SM90), 1450 TFlops (SM100) README.md51 |

 The kernel files are listed in [setup.py65-105](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/setup.py#L65-L105) SM90 has 14 kernel source files, while SM100 has 18 files. The `model1` and `v32` variants refer to different FP8 KV cache layouts, with `model1` using tile size 1×128 and `v32` optimized for specific memory access patterns.

 Sources: [setup.py65-105](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/setup.py#L65-L105) [README.md26-71](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/README.md?plain=1#L26-L71)

 
## Architecture-Specific Dispatch

 The C++ API layer performs runtime architecture detection and feature validation:

 
```

```

 The dispatch logic ensures that:

 
 - SM90 sparse decode requires FP8 KV cache [README.md64](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/README.md?plain=1#L64-L64)
 - SM100 dense prefill uses CUTLASS-based FMHA implementation
 - Causal masking is only available for dense attention [flash_mla/flash_mla_interface.py118](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/flash_mla/flash_mla_interface.py#L118-L118)
 - Head dimensions must match kernel requirements (e.g., 576 for MQA mode, 128/192 for MHA mode) [README.md70](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/README.md?plain=1#L70-L70)
 
 Sources: [flash_mla/flash_mla_interface.py115-170](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/flash_mla/flash_mla_interface.py#L115-L170) [README.md59-71](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/README.md?plain=1#L59-L71)

 
## Memory Hierarchy and Data Flow

 FlashMLA kernels leverage the full GPU memory hierarchy to maximize performance:

 
```

```

 **Global Memory** stores the FP8 KV cache with a specialized layout: 512 bytes of quantized NoPE (float8_e4m3), 16 bytes of scale factors (4×float32), and 128 bytes of unquantized RoPE (64×bfloat16) [README.md118-122](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/README.md?plain=1#L118-L122) This format enables fine-grained tile-level quantization (tile size 1×128) while preserving accuracy for rotation-sensitive components.

 **Shared Memory** serves as the primary staging area. In SM90 sparse decode, the crossover technique uses Distributed Shared Memory (DSM) to share dequantized data between CTAs in a cluster, reducing per-CTA dequantization work by 50% [docs/20250929-hopper-fp8-sparse-deep-dive.md32-45](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/docs/20250929-hopper-fp8-sparse-deep-dive.md?plain=1#L32-L45)

 **Tensor Memory (TMEM)** is a Hopper/Blackwell feature that provides a 1MB fast buffer for staging data during TMA operations. The SM100 backward pass uses overlapped TMEM allocation to maximize utilization.

 **Registers** hold warp-local data and MMA operands. The SM90 sparse decode kernel performs dequantization in registers through a four-step conversion: float8_e4m3 → half → float32 → bfloat16, then scales by float32 factors [docs/20250929-hopper-fp8-sparse-deep-dive.md19-24](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/docs/20250929-hopper-fp8-sparse-deep-dive.md?plain=1#L19-L24)

 Sources: [README.md118-122](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/README.md?plain=1#L118-L122) [docs/20250929-hopper-fp8-sparse-deep-dive.md1-52](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/docs/20250929-hopper-fp8-sparse-deep-dive.md?plain=1#L1-L52)

 
## Key Design Decisions

 
### Stateful Metadata Caching

 The `FlashMLASchedMeta` class [flash_mla/flash_mla_interface.py9-35](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/flash_mla/flash_mla_interface.py#L9-L35) caches tile scheduler metadata across invocations. On the first call to `flash_mla_with_kvcache()`, the system initializes a `Config` object with batch size, sequence length, head counts, and other parameters [flash_mla/flash_mla_interface.py115-135](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/flash_mla/flash_mla_interface.py#L115-L135) Subsequent calls validate that input shapes match the cached configuration [flash_mla/flash_mla_interface.py137-149](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/flash_mla/flash_mla_interface.py#L137-L149) This design eliminates redundant scheduling computations during token generation loops.

 
### Architecture-Specific Optimization

 Rather than a single "universal" kernel, FlashMLA provides specialized implementations for SM90 and SM100 architectures. SM90 kernels focus on sparse operations with FP8 optimization, achieving 410 TFlops through the crossover technique. SM100 kernels provide dense FMHA with full forward/backward passes using CUTLASS primitives, reaching 1460 TFlops forward and 1000 TFlops backward [README.md43](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/README.md?plain=1#L43-L43) This specialization enables 5-15% performance improvements over generic implementations [README.md24](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/README.md?plain=1#L24-L24)

 
### Seesaw Scheduling and Warp Specialization

 FlashMLA introduces "seesaw scheduling" to overlap CUDA Core operations with Tensor Core operations. By splitting the output matrix vertically and interleaving two warp groups, the kernel can perform softmax and scaling on one part while the other part undergoes matrix multiplication [docs/20250422-new-kernel-deep-dive.md25-46](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/docs/20250422-new-kernel-deep-dive.md?plain=1#L25-L46) This technique is particularly effective for MLA decoding, which is compute-bound when $h_q s_q \ge 128$ [docs/20250422-new-kernel-deep-dive.md13](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/docs/20250422-new-kernel-deep-dive.md?plain=1#L13-L13)

 
### Tile-Based Scheduling

 The tile scheduler divides attention computation into tiles that can be processed independently, enabling split-KV strategies for long sequences. The scheduler metadata is computed once and reused across layers [README.md85-97](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/README.md?plain=1#L85-L97) reducing CPU overhead during inference.

 
### Conditional Compilation

 The build system supports selective compilation of SM90/SM100 kernels via `FLASH_MLA_DISABLE_SM90` and `FLASH_MLA_DISABLE_SM100` flags [setup.py36-46](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/setup.py#L36-L46) This allows deployment on systems with CUDA 12.8 (SM90 only) or CUDA 12.9+ (both architectures). The system enforces minimum CUDA 12.9 for SM100 compilation [setup.py38-39](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/setup.py#L38-L39)

 Sources: [flash_mla/flash_mla_interface.py9-173](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/flash_mla/flash_mla_interface.py#L9-L173) [README.md24-51](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/README.md?plain=1#L24-L51) [setup.py36-46](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/setup.py#L36-L46) [docs/20250422-new-kernel-deep-dive.md25-46](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/docs/20250422-new-kernel-deep-dive.md?plain=1#L25-L46)

 
## FP8 KV Cache Layout

 The FP8 KV cache format is central to FlashMLA's memory efficiency:

 
```

```

 For DeepSeek V3/V3.1/V3.2 with `head_dim_k=576` and `head_dim_v=512`:

 
 - The first 512 dimensions are quantized with tile-level scaling (4 tiles of 128 elements each)
 - The last 64 dimensions (RoPE embeddings) remain in BF16 for accuracy [README.md121](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/README.md?plain=1#L121-L121)
 - Each scale factor covers 128 consecutive float8_e4m3 values [README.md120](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/README.md?plain=1#L120-L120)
 
 This layout reduces per-token storage from 1152 bytes (576×2 BF16) to 656 bytes, a 43% reduction while maintaining model quality. The kernel dequantizes on-the-fly during attention computation [docs/20250929-hopper-fp8-sparse-deep-dive.md11](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/docs/20250929-hopper-fp8-sparse-deep-dive.md?plain=1#L11-L11)

 Sources: [README.md115-122](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/README.md?plain=1#L115-L122) [docs/20250929-hopper-fp8-sparse-deep-dive.md7-11](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/docs/20250929-hopper-fp8-sparse-deep-dive.md?plain=1#L7-L11)

 
## Execution Flow Example: Sparse Decode

 The following diagram shows the end-to-end execution path for sparse decoding with FP8 KV cache:

 
```

```

 The sparse decode path validates that `indices` is provided and `is_fp8_kvcache=True` [flash_mla/flash_mla_interface.py151-160](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/flash_mla/flash_mla_interface.py#L151-L160) The kernel uses the indices tensor to select which tokens to attend to, with invalid indices set to -1 [README.md130](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/README.md?plain=1#L130-L130) The crossover technique reduces dequantization overhead from 50 cycles to 25 cycles per token per CTA [docs/20250929-hopper-fp8-sparse-deep-dive.md27-32](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/docs/20250929-hopper-fp8-sparse-deep-dive.md?plain=1#L27-L32)

 Sources: [flash_mla/flash_mla_interface.py53-173](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/flash_mla/flash_mla_interface.py#L53-L173) [README.md125-137](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/README.md?plain=1#L125-L137) [docs/20250929-hopper-fp8-sparse-deep-dive.md27-48](https://github.com/deepseek-ai/FlashMLA/blob/15f13e50/docs/20250929-hopper-fp8-sparse-deep-dive.md?plain=1#L27-L48)
