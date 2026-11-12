<!-- source: DeepWiki mcp.deepwiki.com · repo vllm-project/vllm · page 8 Attention Backends · fetched 2026-10-28 -->

# Attention Backends

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/design/attention_backends.md](docs/design/attention_backends.md)
- [tests/compile/passes/test_rocm_aiter_qk_norm_rope_kvcache_fusion.py](tests/compile/passes/test_rocm_aiter_qk_norm_rope_kvcache_fusion.py)
- [tests/compile/passes/test_rope_kvcache_fusion.py](tests/compile/passes/test_rope_kvcache_fusion.py)
- [tests/kernels/attention/test_rocm_aiter_fa.py](tests/kernels/attention/test_rocm_aiter_fa.py)
- [tests/kernels/attention/test_rocm_aiter_unified_attn.py](tests/kernels/attention/test_rocm_aiter_unified_attn.py)
- [tests/v1/attention/test_rocm_attention_backends_selection.py](tests/v1/attention/test_rocm_attention_backends_selection.py)
- [vllm/compilation/passes/fusion/qk_norm_rope_kvcache_fusion.py](vllm/compilation/passes/fusion/qk_norm_rope_kvcache_fusion.py)
- [vllm/compilation/passes/fusion/rope_kvcache_fusion.py](vllm/compilation/passes/fusion/rope_kvcache_fusion.py)
- [vllm/model_executor/layers/attention/kv_transfer_utils.py](vllm/model_executor/layers/attention/kv_transfer_utils.py)
- [vllm/v1/attention/backends/registry.py](vllm/v1/attention/backends/registry.py)
- [vllm/v1/attention/backends/rocm_aiter_fa.py](vllm/v1/attention/backends/rocm_aiter_fa.py)
- [vllm/v1/attention/backends/rocm_aiter_unified_attn.py](vllm/v1/attention/backends/rocm_aiter_unified_attn.py)
- [vllm/v1/attention/backends/rocm_attn.py](vllm/v1/attention/backends/rocm_attn.py)

</details>



## Purpose and Scope

Attention backends provide alternative implementations of attention for different hardware platforms, attention patterns, and model configurations. vLLM exposes backend names through `AttentionBackendEnum`; the registry maps many of those names to implementation classes, including standard attention, MLA, sparse attention, and platform-specific backends. [vllm/v1/attention/backends/registry.py:34-162]()

This parent page connects backend selection, general-purpose implementations, specialized attention, and platform-specific optimizations. For details, see [Attention Backend Selection](#8.1), [FlashAttention, FlashInfer and FlexAttention](#8.2), [MLA and Specialized Attention](#8.3), and [ROCm and Platform-Specific Attention](#8.4).

Sources: [vllm/v1/attention/backends/registry.py:34-162]()

---

## Architecture Overview

The registry associates backend identifiers such as `FLASH_ATTN`, `FLASHINFER`, `FLEX_ATTENTION`, `ROCM_ATTN`, and `CPU_ATTN` with implementation paths. It also includes entries for specialized MLA and model-specific sparse backends. [vllm/v1/attention/backends/registry.py:34-162]()

At a high level, backend selection connects user configuration and model or platform needs to a backend implementation. Backend-specific metadata and execution details vary; for example, ROCm backends define metadata builders alongside their backend classes. For the selection process and `Attention` layer abstraction, see [Attention Backend Selection](#8.1). [vllm/v1/attention/backends/rocm_attn.py:48-73]()

**Diagram: Attention subsystem concepts mapped to registry and implementation entities**

```mermaid
graph LR
    "Attention_backend_choices" --> "AttentionBackendEnum"
    "AttentionBackendEnum" --> "FLASH_ATTN"
    "AttentionBackendEnum" --> "FLASHINFER"
    "AttentionBackendEnum" --> "FLEX_ATTENTION"
    "AttentionBackendEnum" --> "ROCM_ATTN"
    "AttentionBackendEnum" --> "ROCM_AITER_UNIFIED_ATTN"
    "FLASH_ATTN" --> "vllm.v1.attention.backends.flash_attn.FlashAttentionBackend"
    "FLASHINFER" --> "vllm.v1.attention.backends.flashinfer.FlashInferBackend"
    "ROCM_ATTN" --> "vllm.v1.attention.backends.rocm_attn.RocmAttentionBackend"
    "ROCM_AITER_UNIFIED_ATTN" --> "RocmAiterUnifiedAttentionBackend"
    "RocmAiterUnifiedAttentionBackend" --> "RocmAiterUnifiedAttentionMetadataBuilder"
```

Sources: [vllm/v1/attention/backends/registry.py:34-75](), [vllm/v1/attention/backends/registry.py:147-162](), [vllm/v1/attention/backends/rocm_attn.py:48-73](), [vllm/v1/attention/backends/rocm_aiter_unified_attn.py:50-61]()

---

## Attention Backend Selection

The backend registry defines the available backend names and their default class paths; the enum documentation notes that runtime registration can override a path. [vllm/v1/attention/backends/registry.py:34-42]() Users can set a backend with `--attention-backend` or through `--attention-config.backend`; the two command-line forms are mutually exclusive. [docs/design/attention_backends.md:8-33]()

When a backend is specified explicitly, it is validated against the configuration, and an incompatibility raises an error. When no backend is specified, vLLM tries backends in priority order and selects the first compatible one; the design document notes that ROCm and CPU have their own selection logic. [docs/design/attention_backends.md:108-152]() For details, see [Attention Backend Selection](#8.1).

Sources: [vllm/v1/attention/backends/registry.py:34-42](), [docs/design/attention_backends.md:8-33](), [docs/design/attention_backends.md:108-152]()

---

## FlashAttention, FlashInfer and FlexAttention

The registry includes backend entries for FlashAttention, FlashInfer, Triton, FlexAttention, and composite Triton-based backends. [vllm/v1/attention/backends/registry.py:44-53](), [vllm/v1/attention/backends/registry.py:71-74](), [vllm/v1/attention/backends/registry.py:147-148]() The design documentation describes composite routing for compatible multimodal-prefix configurations: on Hopper, `TRITON_FLASH_ATTN` can route bidirectional image attention to Triton and causal text attention to FlashAttention; on Blackwell, `TRITON_FLASHINFER` can route those query patterns to Triton and FlashInfer. [docs/design/attention_backends.md:59-89]()

Backend compatibility and configuration options—including attention version selection and supported features—are handled in backend validation and configuration. For implementation and configuration details, see [FlashAttention, FlashInfer and FlexAttention](#8.2). [docs/design/attention_backends.md:110-123](), [docs/design/attention_backends.md:154-179]()

Sources: [vllm/v1/attention/backends/registry.py:44-53](), [vllm/v1/attention/backends/registry.py:71-74](), [vllm/v1/attention/backends/registry.py:147-148](), [docs/design/attention_backends.md:59-89](), [docs/design/attention_backends.md:110-123](), [docs/design/attention_backends.md:154-179]()

---

## MLA and Specialized Attention

The registry includes MLA backends such as `FLASHMLA`, `FLASHINFER_MLA`, `TRITON_MLA`, and `CUTLASS_MLA`, as well as sparse MLA entries and model-specific DeepSeek V4/V4.1 backends. [vllm/v1/attention/backends/registry.py:75-134]() The design documentation describes separate priority selection for standard attention and MLA, with additional preference rules for sparse MLA. [docs/design/attention_backends.md:135-152]()

This family also includes specialized sparse-attention entries for models such as MiniMax M3 and Step5. [vllm/v1/attention/backends/registry.py:135-146]() For MLA, sparse attention, indexers, and hybrid metadata builders, see [MLA and Specialized Attention](#8.3).

Sources: [vllm/v1/attention/backends/registry.py:75-146](), [docs/design/attention_backends.md:135-152]()

---

## ROCm and Platform-Specific Attention

The registry lists ROCm backends including `ROCM_ATTN`, `ROCM_AITER_FA`, `ROCM_AITER_UNIFIED_ATTN`, and ROCm MLA variants. [vllm/v1/attention/backends/registry.py:55-68](), [vllm/v1/attention/backends/registry.py:155-158]() The ROCm attention implementation documents native paged-attention kernel constraints and a Triton path for supported block-size multiples. [vllm/v1/attention/backends/rocm_attn.py:137-172]() The AITER unified backend provides its own metadata builder and declares supported cache, attention-type, and feature constraints. [vllm/v1/attention/backends/rocm_aiter_unified_attn.py:50-150]()

The registry also includes CPU attention and CPU/AMX MLA backend identifiers. [vllm/v1/attention/backends/registry.py:159-162]() For AITER, ROCm selection and optimizations, and CPU/XPU/TPU backends, see [ROCm and Platform-Specific Attention](#8.4).

Sources: [vllm/v1/attention/backends/registry.py:55-68](), [vllm/v1/attention/backends/registry.py:155-162](), [vllm/v1/attention/backends/rocm_attn.py:137-172](), [vllm/v1/attention/backends/rocm_aiter_unified_attn.py:50-150]()

---

## Backend Families at a Glance

| Concern | Registry examples | Details |
|---|---|---|
| Standard attention | `FLASH_ATTN`, `FLASHINFER`, `TRITON_ATTN`, `FLEX_ATTENTION` | See [FlashAttention, FlashInfer and FlexAttention](#8.2). [vllm/v1/attention/backends/registry.py:44-53](), [vllm/v1/attention/backends/registry.py:71-74](), [vllm/v1/attention/backends/registry.py:147-148]() |
| MLA and sparse attention | `FLASHMLA`, `FLASHINFER_MLA`, `TRITON_MLA`, `FLASHMLA_SPARSE_DSV4` | See [MLA and Specialized Attention](#8.3). [vllm/v1/attention/backends/registry.py:75-134]() |
| ROCm | `ROCM_ATTN`, `ROCM_AITER_FA`, `ROCM_AITER_UNIFIED_ATTN` | See [ROCm and Platform-Specific Attention](#8.4). [vllm/v1/attention/backends/registry.py:55-68](), [vllm/v1/attention/backends/registry.py:155-158]() |
| CPU | `CPU_ATTN`, `CPU_MLA`, `AMX_MLA` | See [ROCm and Platform-Specific Attention](#8.4). [vllm/v1/attention/backends/registry.py:159-162]() |

Sources: [vllm/v1/attention/backends/registry.py:44-162]()

---

## Natural-Language Topics Mapped to Code Entities

**Diagram: Selection and configuration concepts mapped to registry symbols**

```mermaid
graph LR
    "Choose_attention_backend" --> "AttentionBackendEnum"
    "Set_backend_on_command_line" --> "--attention-backend"
    "Set_structured_attention_configuration" --> "--attention-config.backend"
    "Validate_explicit_backend" --> "AttentionBackend.validate_configuration"
    "Backend_registry_entry" --> "AttentionBackendEnum.FLASH_ATTN"
    "AttentionBackendEnum.FLASH_ATTN" --> "vllm.v1.attention.backends.flash_attn.FlashAttentionBackend"
    "Automatic_priority_selection" --> "priority-standard"
    "MLA_priority_selection" --> "priority-mla"
```

Sources: [vllm/v1/attention/backends/registry.py:34-54](), [docs/design/attention_backends.md:8-33](), [docs/design/attention_backends.md:110-152]()

**Diagram: Platform and specialized attention concepts mapped to code entities**

```mermaid
graph LR
    "ROCm_paged_attention" --> "ROCM_ATTN"
    "ROCM_ATTN" --> "RocmAttentionBackend"
    "RocmAttentionBackend" --> "RocmAttentionMetadataBuilder"
    "AITER_unified_attention" --> "ROCM_AITER_UNIFIED_ATTN"
    "ROCM_AITER_UNIFIED_ATTN" --> "RocmAiterUnifiedAttentionBackend"
    "RocmAiterUnifiedAttentionBackend" --> "RocmAiterUnifiedAttentionMetadataBuilder"
    "Sparse_MLA_for_DeepSeek_V4" --> "FLASHMLA_SPARSE_DSV4"
    "CPU_attention" --> "CPU_ATTN"
```

Sources: [vllm/v1/attention/backends/registry.py:55-68](), [vllm/v1/attention/backends/registry.py:99-120](), [vllm/v1/attention/backends/registry.py:159-162](), [vllm/v1/attention/backends/rocm_attn.py:73-73](), [vllm/v1/attention/backends/rocm_aiter_unified_attn.py:50-61]()

---

This page is an overview of attention backend families and their relationships. For selection behavior, backend implementation details, and platform-specific support, follow the child pages linked above.

Sources: [vllm/v1/attention/backends/registry.py:34-162](), [docs/design/attention_backends.md:8-152]()

---

