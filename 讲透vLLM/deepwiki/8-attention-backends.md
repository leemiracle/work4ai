# Attention Backends

> 来源: https://deepwiki.com/vllm-project/vllm/8-attention-backends 抓取日期: 2026-09-02
> 章节: 第 8 章 注意力后端

---

Relevant source files

  * [cmake/external_projects/vllm_flash_attn.cmake](https://github.com/vllm-project/vllm/blob/185cada3/cmake/external_projects/vllm_flash_attn.cmake)
  * [docs/design/attention_backends.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/design/attention_backends.md?plain=1)
  * [tests/entrypoints/serve/utils/test_api_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/entrypoints/serve/utils/test_api_utils.py)
  * [tests/test_envs.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/test_envs.py)
  * [tests/transformers_utils/test_dspark_mla_config.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/transformers_utils/test_dspark_mla_config.py)
  * [tests/v1/attention/test_attention_backends.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/attention/test_attention_backends.py)
  * [tests/v1/attention/test_mla_backends.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/attention/test_mla_backends.py)
  * [tests/v1/attention/test_sparse_mla_backends.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/attention/test_sparse_mla_backends.py)
  * [tests/v1/spec_decode/test_dflash_prepare_inputs.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/spec_decode/test_dflash_prepare_inputs.py)
  * [vllm/_aiter_ops.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/_aiter_ops.py)
  * [vllm/entrypoints/serve/utils/api_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/serve/utils/api_utils.py)
  * [vllm/envs.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/envs.py)
  * [vllm/model_executor/layers/attention/attention.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/attention/attention.py)
  * [vllm/model_executor/layers/attention/mla_attention.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/attention/mla_attention.py)
  * [vllm/v1/attention/backend.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backend.py)
  * [vllm/v1/attention/backends/fa_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/fa_utils.py)
  * [vllm/v1/attention/backends/flash_attn.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flash_attn.py)
  * [vllm/v1/attention/backends/flashinfer.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flashinfer.py)
  * [vllm/v1/attention/backends/mla/cutlass_mla.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/mla/cutlass_mla.py)
  * [vllm/v1/attention/backends/mla/flashattn_mla.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/mla/flashattn_mla.py)
  * [vllm/v1/attention/backends/mla/flashattn_mla_sparse.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/mla/flashattn_mla_sparse.py)
  * [vllm/v1/attention/backends/mla/flashinfer_mla.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/mla/flashinfer_mla.py)
  * [vllm/v1/attention/backends/mla/flashinfer_mla_sparse.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/mla/flashinfer_mla_sparse.py)
  * [vllm/v1/attention/backends/mla/flashmla.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/mla/flashmla.py)
  * [vllm/v1/attention/backends/mla/flashmla_sparse.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/mla/flashmla_sparse.py)
  * [vllm/v1/attention/backends/mla/tokenspeed_mla.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/mla/tokenspeed_mla.py)
  * [vllm/v1/attention/backends/mla/triton_mla.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/mla/triton_mla.py)
  * [vllm/v1/attention/backends/mla/xpu_mla_sparse.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/mla/xpu_mla_sparse.py)
  * [vllm/v1/attention/backends/registry.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/registry.py)
  * [vllm/v1/attention/backends/rocm_aiter_fa.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/rocm_aiter_fa.py)
  * [vllm/v1/attention/backends/rocm_aiter_unified_attn.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/rocm_aiter_unified_attn.py)
  * [vllm/v1/attention/backends/rocm_attn.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/rocm_attn.py)
  * [vllm/v1/attention/backends/triton_attn.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/triton_attn.py)
  * [vllm/v1/attention/backends/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/utils.py)
  * [vllm/v1/worker/gpu/spec_decode/gemma4/speculator.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/spec_decode/gemma4/speculator.py)
  * [vllm/vllm_flash_attn/flash_attn_interface.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/vllm_flash_attn/flash_attn_interface.py)

## Purpose and Scope

Attention backends are pluggable components that implement the core attention computation in vLLM's inference engine. Each backend provides optimized kernels for different hardware platforms, attention patterns, and data types. This page documents the attention backend architecture, available backends, and selection mechanisms.

For information about the overall model execution flow, see [Model Execution on GPU](/vllm-project/vllm/4-model-execution-on-gpu). For KV cache management, see [KV Cache Management and Prefix Caching](/vllm-project/vllm/3.4-kv-cache-management-and-prefix-caching).

## Architecture Overview

The attention backend system uses an abstract interface pattern that allows multiple implementations to coexist and be selected based on hardware capabilities, model requirements, and performance characteristics.

### Core Abstractions

The following diagram maps the high-level architecture to the specific code entities in the `vllm/v1/attention` directory.

**Sources:** [vllm/v1/attention/backend.py59-118](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backend.py#L59-L118) [vllm/v1/attention/backends/flashinfer.py60-89](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flashinfer.py#L60-L89) [vllm/v1/attention/backends/flash_attn.py78-147](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flash_attn.py#L78-L147) [vllm/model_executor/layers/attention/mla_attention.py230-245](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/attention/mla_attention.py#L230-L245) [vllm/v1/attention/backends/rocm_aiter_unified_attn.py29-110](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/rocm_aiter_unified_attn.py#L29-L110)

The core components of any attention backend are defined by the `AttentionBackend` interface.

Component| Purpose| Key Methods  
---|---|---  
`AttentionBackend`| Backend metadata and capabilities| `get_name()`, `get_impl_cls()`, `get_builder_cls()`, `supports_head_size()` [vllm/v1/attention/backend.py72-103](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backend.py#L72-L103)  
`AttentionImpl`| Actual attention computation| `forward()`, `do_kv_cache_update()` [vllm/v1/attention/backend.py214-257](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backend.py#L214-L257)  
`AttentionMetadataBuilder`| Prepare metadata for attention kernels| `build()`, `get_cudagraph_support()` [vllm/v1/attention/backend.py175-200](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backend.py#L175-L200)  
  
### Backend Capabilities and Configuration

Each backend declares its capabilities through static methods and constants. The following diagram illustrates how a `FlashAttentionBackend` exposes its requirements to the selection logic.

**Sources:** [vllm/v1/attention/backends/flash_attn.py78-208](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flash_attn.py#L78-L208) [vllm/v1/attention/backends/flashinfer.py279-383](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flashinfer.py#L279-L383)

## Standard Attention Backends

### FlashInfer Backend

FlashInfer is a primary backend for NVIDIA GPUs, providing optimized paged attention. It supports advanced features like TRTLLM-style attention for Blackwell (SM100) GPUs using `trtllm_batch_decode_with_kv_cache` [vllm/v1/attention/backends/flashinfer.py19](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flashinfer.py#L19-L19)

**Key Features:**

  * **TRTLLM Attention Path:** Automatically uses TRTLLM-optimized kernels for decode when `use_trtllm_attention` is true [vllm/v1/attention/backends/flashinfer.py47-48](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flashinfer.py#L47-L48)
  * **FP8/NVFP4 KV Cache:** Supports FP8 and NVFP4 quantized KV caches with dequantization via Triton kernels like `_trtllm_prefill_attn_kvfp8_dequant` [vllm/v1/attention/backends/flashinfer.py156-212](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flashinfer.py#L156-L212)
  * **Cascade Attention:** Efficiently handles prefix caching using `MultiLevelCascadeAttentionWrapper` [vllm/v1/attention/backends/flashinfer.py17-18](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flashinfer.py#L17-L18)

For details, see [FlashAttention and FlashInfer](/vllm-project/vllm/8.2-flashattention-and-flashinfer).

**Sources:** [vllm/v1/attention/backends/flashinfer.py12-215](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flashinfer.py#L12-L215) [vllm/utils/flashinfer.py42-48](https://github.com/vllm-project/vllm/blob/185cada3/vllm/utils/flashinfer.py#L42-L48)

### FlashAttention Backend

The FlashAttention backend provides a standard implementation using `flash_attn_varlen_func`. It supports various attention types including decoder, encoder, and encoder-decoder [vllm/v1/attention/backends/flash_attn.py117-124](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flash_attn.py#L117-L124)

**Key Features:**

  * **Version Support:** Detects FlashAttention versions (FA2, FA3, FA4) and feature availability via `get_flash_attn_version` [vllm/v1/attention/backends/fa_utils.py29](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/fa_utils.py#L29-L29)
  * **SM90/SM100 Logic:** Includes specialized logic for SM90 FA3 and SM100 FA4 FP8 KV block sizes [vllm/v1/attention/backends/flash_attn.py189-207](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flash_attn.py#L189-L207)
  * **DCP Support:** Integrates with Decode Context Parallelism via `run_split_fa2_dcp_context_attention` [vllm/v1/attention/backends/flash_attn.py68-73](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flash_attn.py#L68-L73)

For details, see [FlashAttention and FlashInfer](/vllm-project/vllm/8.2-flashattention-and-flashinfer).

**Sources:** [vllm/v1/attention/backends/flash_attn.py78-208](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flash_attn.py#L78-L208) [vllm/v1/attention/backends/fa_utils.py26-32](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/fa_utils.py#L26-L32)

### Triton Attention Backend

The Triton backend provides a high-performance implementation using pure Triton kernels. It uses `seq_threshold_3D` to switch between 2D and 3D kernels based on batch size to optimize occupancy [vllm/v1/attention/backends/triton_attn.py133-139](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/triton_attn.py#L133-L139)

**Key Features:**

  * **Unified Attention:** Uses `unified_attention` for flexible execution paths [vllm/v1/attention/backends/triton_attn.py42](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/triton_attn.py#L42-L42)
  * **Cascade Support:** Implements cascade attention for shared prefixes using `cu_prefix_query_lens` [vllm/v1/attention/backends/triton_attn.py86-88](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/triton_attn.py#L86-L88)
  * **Multimodal Support:** Handles specialized prefix ranges for multimodal models via `compute_mm_prefix_range_tensor` [vllm/v1/attention/backends/utils.py54-81](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/utils.py#L54-L81)

**Sources:** [vllm/v1/attention/backends/triton_attn.py57-184](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/triton_attn.py#L57-L184) [vllm/v1/attention/backends/utils.py54-81](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/utils.py#L54-L81)

## ROCm and Specialized Backends

### ROCm AITER Backend

For AMD GPUs, vLLM provides optimized backends using AITER ops.

**Key Features:**

  * **Aiter Unified Attention:** Provides a specialized backend `RocmAiterUnifiedAttentionBackend` that supports fused output quantization and sinks [vllm/v1/attention/backends/rocm_aiter_unified_attn.py29-75](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/rocm_aiter_unified_attn.py#L29-L75)
  * **Gather Cache:** Implements Triton-based `cp_mha_gather_cache_kernel` to handle paged KV cache access on ROCm [vllm/v1/attention/backends/rocm_aiter_fa.py48-152](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/rocm_aiter_fa.py#L48-L152)
  * **Platform Detection:** AITER is supported on ROCm platforms with CDNA 3 (gfx942) or better [vllm/_aiter_ops.py150-153](https://github.com/vllm-project/vllm/blob/185cada3/vllm/_aiter_ops.py#L150-L153)

For details, see [ROCm and Platform-Specific Attention](/vllm-project/vllm/8.4-rocm-and-platform-specific-attention).

**Sources:** [vllm/v1/attention/backends/rocm_aiter_unified_attn.py29-145](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/rocm_aiter_unified_attn.py#L29-L145) [vllm/v1/attention/backends/rocm_aiter_fa.py36-152](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/rocm_aiter_fa.py#L36-L152) [vllm/_aiter_ops.py150-154](https://github.com/vllm-project/vllm/blob/185cada3/vllm/_aiter_ops.py#L150-L154)

### Multi-Latent Attention (MLA) Backends

MLA is a specialized attention mechanism used in models like DeepSeek. MLA uses separate backends for prefill (compute-friendly) and decode (data-movement friendly) phases [vllm/model_executor/layers/attention/mla_attention.py13-24](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/attention/mla_attention.py#L13-L24)

**Implementations:**

  * **FlashMLA:** Optimized dense MLA for Hopper/Blackwell GPUs [docs/design/attention_backends.md163-165](https://github.com/vllm-project/vllm/blob/185cada3/docs/design/attention_backends.md?plain=1#L163-L165)
  * **Sparse MLA:** Used for DeepSeek V4, selected via `FLASHMLA_SPARSE_DSV4` or `FLASHINFER_MLA_SPARSE_DSV4` [docs/design/attention_backends.md167-176](https://github.com/vllm-project/vllm/blob/185cada3/docs/design/attention_backends.md?plain=1#L167-L176)
  * **Chunked Prefill:** Mitigates memory usage during prefill by chunking computation with respect to existing context [vllm/model_executor/layers/attention/mla_attention.py121-148](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/attention/mla_attention.py#L121-L148)

For details, see [MLA and Specialized Attention](/vllm-project/vllm/8.3-mla-and-specialized-attention).

**Sources:** [vllm/model_executor/layers/attention/mla_attention.py8-148](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/attention/mla_attention.py#L8-L148) [docs/design/attention_backends.md141-176](https://github.com/vllm-project/vllm/blob/185cada3/docs/design/attention_backends.md?plain=1#L141-L176)

## Backend Selection

The selection logic is platform-dependent and considers device capabilities, model architecture (e.g., MLA), and user configuration.

### Manual vs Automatic Selection

Users can explicitly set a backend via the command line using `--attention-backend` [docs/design/attention_backends.md14-18](https://github.com/vllm-project/vllm/blob/185cada3/docs/design/attention_backends.md?plain=1#L14-L18) When no backend is specified, vLLM iterates through backends in a priority-ordered list and selects the first compatible one [docs/design/attention_backends.md78-89](https://github.com/vllm-project/vllm/blob/185cada3/docs/design/attention_backends.md?plain=1#L78-L89)

### Selection Logic Factors

Selection is performed by analyzing:

  * **Hardware:** CUDA Compute Capability (e.g., SM80 for FlashAttention) [vllm/v1/attention/backends/flash_attn.py170-171](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flash_attn.py#L170-L171) ROCm GCN architecture detection.
  * **Model Config:** Parameters like head size and attention type (Decoder, Encoder, etc.) [vllm/v1/attention/backends/flash_attn.py117-124](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flash_attn.py#L117-L124)
  * **Quantization:** Support for FP8, INT8, or NVFP4 KV caches varies by backend [vllm/v1/attention/backends/flashinfer.py34-38](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flashinfer.py#L34-L38) [vllm/v1/attention/backends/flash_attn.py150-157](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flash_attn.py#L150-L157)

For details, see [Attention Backend Selection](/vllm-project/vllm/8.1-attention-backend-selection).

**Sources:** [vllm/v1/attention/backends/flash_attn.py78-208](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flash_attn.py#L78-L208) [docs/design/attention_backends.md78-95](https://github.com/vllm-project/vllm/blob/185cada3/docs/design/attention_backends.md?plain=1#L78-L95)

## Metadata Building and Utilities

Attention backends rely on utility functions to manage KV cache layouts and sequence lengths.

  * **KV Cache Layout:** FlashInfer conventionally uses "NHD" or "HND" strings for layout mapping [vllm/v1/attention/backends/utils.py154-170](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/utils.py#L154-L170)
  * **MM Prefix:** `fill_mm_prefix_query_ranges()` maps scheduled query tokens to multimodal prefix ranges for bidirectional attention [vllm/v1/attention/backends/utils.py83-151](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/utils.py#L83-L151)
  * **KV Cache Shape:** Backends like FlashAttention define their own physical layout, typically `(num_blocks, page_size, num_heads, head_dim)` [vllm/v1/attention/backends/rocm_aiter_fa.py49-52](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/rocm_aiter_fa.py#L49-L52)

**Sources:** [vllm/v1/attention/backends/utils.py83-170](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/utils.py#L83-L170) [vllm/v1/attention/backends/rocm_aiter_fa.py48-152](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/rocm_aiter_fa.py#L48-L152)
