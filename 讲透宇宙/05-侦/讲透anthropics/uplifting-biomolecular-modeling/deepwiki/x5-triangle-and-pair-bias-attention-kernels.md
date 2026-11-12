<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/uplifting-biomolecular-modeling · extra page Triangle and Pair-Bias Attention Kernels · fetched 2026-10-26 -->

# Triangle and Pair-Bias Attention Kernels

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [af3_jax/stock/src/src/alphafold3/model/components/haiku_modules.py](af3_jax/stock/src/src/alphafold3/model/components/haiku_modules.py)
- [af3_jax/stock/src/src/alphafold3/model/components/mapping.py](af3_jax/stock/src/src/alphafold3/model/components/mapping.py)
- [af3_torch/opt/forward/af3t/af3_torch/xfold/nn/primitives.py](af3_torch/opt/forward/af3t/af3_torch/xfold/nn/primitives.py)
- [af3_torch/opt/forward/af3t/af3_torch/xfold/nn/triangle_multiplication.py](af3_torch/opt/forward/af3t/af3_torch/xfold/nn/triangle_multiplication.py)
- [atlasfold/opt/atlasfold_opt/cells/pair_fused/README.md](atlasfold/opt/atlasfold_opt/cells/pair_fused/README.md)
- [atlasfold/opt/atlasfold_opt/hooks/pair_cells.py](atlasfold/opt/atlasfold_opt/hooks/pair_cells.py)
- [atlasfold/opt/atlasfold_opt/tests/test_epilogue_follows_cell_cpu.py](atlasfold/opt/atlasfold_opt/tests/test_epilogue_follows_cell_cpu.py)
- [boltz2/stock/src/boltz/model/layers/triangular_mult.py](boltz2/stock/src/boltz/model/layers/triangular_mult.py)
- [common/opt_core/opt_core/attn/pair_fused.py](common/opt_core/opt_core/attn/pair_fused.py)
- [common/opt_core/opt_core/kernels/fpf_glue_v2/NOTICE](common/opt_core/opt_core/kernels/fpf_glue_v2/NOTICE)
- [common/opt_core/opt_core/kernels/fpf_mkpf/NOTICE](common/opt_core/opt_core/kernels/fpf_mkpf/NOTICE)
- [common/opt_core/opt_core/kernels/fpf_transition/NOTICE](common/opt_core/opt_core/kernels/fpf_transition/NOTICE)
- [common/opt_core/opt_core/kernels/fpf_triatt_epi/NOTICE](common/opt_core/opt_core/kernels/fpf_triatt_epi/NOTICE)
- [common/opt_core/opt_core/kernels/fpf_triatt_k2b/NOTICE](common/opt_core/opt_core/kernels/fpf_triatt_k2b/NOTICE)
- [common/opt_core/opt_core/kernels/fpf_triatt_pro/NOTICE](common/opt_core/opt_core/kernels/fpf_triatt_pro/NOTICE)
- [common/opt_core/opt_core/kernels/fpf_trimul/NOTICE](common/opt_core/opt_core/kernels/fpf_trimul/NOTICE)
- [common/opt_core/opt_core/kernels/fpf_trimul_v4/NOTICE](common/opt_core/opt_core/kernels/fpf_trimul_v4/NOTICE)
- [common/opt_core/opt_core/kernels/triattn/cuda_sm90a/csrc/triattn_mw.cu](common/opt_core/opt_core/kernels/triattn/cuda_sm90a/csrc/triattn_mw.cu)
- [common/opt_core/opt_core/kernels/triattn/cuda_sm90a/prebuilt/torch2.10.0+cu128-cpython-311-x86_64-linux-gnu-sm90/SHA256SUMS](common/opt_core/opt_core/kernels/triattn/cuda_sm90a/prebuilt/torch2.10.0+cu128-cpython-311-x86_64-linux-gnu-sm90/SHA256SUMS)
- [common/opt_core/opt_core/kernels/triattn/cuda_sm90a/prebuilt/torch2.11.0+cu128-cpython-312-x86_64-linux-gnu-sm90/SHA256SUMS](common/opt_core/opt_core/kernels/triattn/cuda_sm90a/prebuilt/torch2.11.0+cu128-cpython-312-x86_64-linux-gnu-sm90/SHA256SUMS)
- [common/opt_core/opt_core/kernels/triattn/cuda_sm90a/prebuilt/torch2.12.0+cu130-cpython-311-x86_64-linux-gnu-sm90/SHA256SUMS](common/opt_core/opt_core/kernels/triattn/cuda_sm90a/prebuilt/torch2.12.0+cu130-cpython-311-x86_64-linux-gnu-sm90/SHA256SUMS)
- [common/opt_core/opt_core/kernels/triattn/cuda_sm90a/prebuilt/torch2.13.0+cu130-cpython-311-x86_64-linux-gnu-sm90/SHA256SUMS](common/opt_core/opt_core/kernels/triattn/cuda_sm90a/prebuilt/torch2.13.0+cu130-cpython-311-x86_64-linux-gnu-sm90/SHA256SUMS)
- [common/opt_core/opt_core/kernels/triattn/cuda_sm90a/prebuilt/torch2.13.0+cu130-cpython-312-x86_64-linux-gnu-sm90/SHA256SUMS](common/opt_core/opt_core/kernels/triattn/cuda_sm90a/prebuilt/torch2.13.0+cu130-cpython-312-x86_64-linux-gnu-sm90/SHA256SUMS)
- [common/opt_core/opt_core/kernels/triattn/cuda_sm90a/prebuilt/torch2.7.1+cu126-cpython-311-x86_64-linux-gnu-sm90/SHA256SUMS](common/opt_core/opt_core/kernels/triattn/cuda_sm90a/prebuilt/torch2.7.1+cu126-cpython-311-x86_64-linux-gnu-sm90/SHA256SUMS)
- [common/opt_core/opt_core/kernels/triattn/cuda_sm90a/prebuilt/torch2.7.1+cu128-cpython-311-x86_64-linux-gnu-sm90/SHA256SUMS](common/opt_core/opt_core/kernels/triattn/cuda_sm90a/prebuilt/torch2.7.1+cu128-cpython-311-x86_64-linux-gnu-sm90/SHA256SUMS)
- [common/opt_core/opt_core/kernels/triattn/triattn_native/pkg/v11/triattn_pkg/cuda/csrc/triattn_binding.cu](common/opt_core/opt_core/kernels/triattn/triattn_native/pkg/v11/triattn_pkg/cuda/csrc/triattn_binding.cu)
- [common/opt_core/opt_core/kernels/triattn/triattn_native/pkg/v11/triattn_pkg/cuda_80/csrc/sm80_binding.cu](common/opt_core/opt_core/kernels/triattn/triattn_native/pkg/v11/triattn_pkg/cuda_80/csrc/sm80_binding.cu)
- [common/opt_core/opt_core/kernels/triattn/triattn_native/pkg/v11/triattn_pkg/cuda_80/csrc/triattn_sm80.cuh](common/opt_core/opt_core/kernels/triattn/triattn_native/pkg/v11/triattn_pkg/cuda_80/csrc/triattn_sm80.cuh)
- [common/opt_core/opt_core/kernels/triattn/triattn_native/pkg/v11/triattn_pkg/cuda_b/csrc/launch.cuh](common/opt_core/opt_core/kernels/triattn/triattn_native/pkg/v11/triattn_pkg/cuda_b/csrc/launch.cuh)
- [common/opt_core/opt_core/kernels/triattn/triattn_native/pkg/v11/triattn_pkg/cuda_b/csrc/m1/launch_m1.cuh](common/opt_core/opt_core/kernels/triattn/triattn_native/pkg/v11/triattn_pkg/cuda_b/csrc/m1/launch_m1.cuh)
- [common/opt_core/opt_core/kernels/triattn/triattn_native/pkg/v11/triattn_pkg/cuda_b/csrc/m1/m1_binding.cu](common/opt_core/opt_core/kernels/triattn/triattn_native/pkg/v11/triattn_pkg/cuda_b/csrc/m1/m1_binding.cu)
- [common/opt_core/opt_core/kernels/triattn/triattn_native/pkg/v11/triattn_pkg/cuda_b/csrc/prep.cu](common/opt_core/opt_core/kernels/triattn/triattn_native/pkg/v11/triattn_pkg/cuda_b/csrc/prep.cu)
- [common/opt_core/opt_core/kernels/triattn/triattn_native/pkg/v11/triattn_pkg/cuda_c/csrc/triattn_mw.cu](common/opt_core/opt_core/kernels/triattn/triattn_native/pkg/v11/triattn_pkg/cuda_c/csrc/triattn_mw.cu)
- [common/opt_core/opt_core/kernels/triattn_exact/csrc/cuda_mma/triattn_v3.cu](common/opt_core/opt_core/kernels/triattn_exact/csrc/cuda_mma/triattn_v3.cu)
- [common/opt_core/opt_core/kernels/triattn_xla/csrc/triattn_m1_xla.cu](common/opt_core/opt_core/kernels/triattn_xla/csrc/triattn_m1_xla.cu)
- [common/opt_core/opt_core/kernels/triattn_xla/csrc/triattn_sm80_xla.cu](common/opt_core/opt_core/kernels/triattn_xla/csrc/triattn_sm80_xla.cu)
- [common/opt_core/opt_core/mem/rowpair_jax/shard.py](common/opt_core/opt_core/mem/rowpair_jax/shard.py)
- [common/opt_core/opt_core/trimul.py](common/opt_core/opt_core/trimul.py)
- [common/opt_core/tests/test_rowpair_jax_a2a_split.py](common/opt_core/tests/test_rowpair_jax_a2a_split.py)
- [common/opt_core/tests/test_rowpair_jax_logic.py](common/opt_core/tests/test_rowpair_jax_logic.py)
- [common/opt_core/tests/test_rowpair_jax_rowchunk.py](common/opt_core/tests/test_rowpair_jax_rowchunk.py)
- [common/opt_core/tests/test_rowpair_logic.py](common/opt_core/tests/test_rowpair_logic.py)
- [common/opt_core/tests/test_rowpair_msa_mp_043.py](common/opt_core/tests/test_rowpair_msa_mp_043.py)
- [common/opt_core/tests/test_rowpair_pairstack_043.py](common/opt_core/tests/test_rowpair_pairstack_043.py)
- [common/opt_core/tests/test_rowpair_shard_043.py](common/opt_core/tests/test_rowpair_shard_043.py)
- [common/opt_core/tests/test_rowpair_staging_045.py](common/opt_core/tests/test_rowpair_staging_045.py)
- [common/opt_core/tests/test_rowpair_template_0511.py](common/opt_core/tests/test_rowpair_template_0511.py)
- [common/opt_core/tests/test_rowpair_transpose_onerow_0518.py](common/opt_core/tests/test_rowpair_transpose_onerow_0518.py)
- [common/opt_core/tests/test_rowpair_trimul_dtype_044.py](common/opt_core/tests/test_rowpair_trimul_dtype_044.py)
- [common/opt_core/tests/test_rowpair_trimul_operands_043.py](common/opt_core/tests/test_rowpair_trimul_operands_043.py)
- [common/opt_core/tests/test_rowpair_trunk_043.py](common/opt_core/tests/test_rowpair_trunk_043.py)
- [protenix_v2/opt/forward/flashpairformer/third_party/protenix_fpf_triatt_procuda/binding.py](protenix_v2/opt/forward/flashpairformer/third_party/protenix_fpf_triatt_procuda/binding.py)
- [protenix_v2/opt/forward/flashpairformer/third_party/protenix_fpf_triatt_procuda/csrc/triatt_procuda_sm90.cu](protenix_v2/opt/forward/flashpairformer/third_party/protenix_fpf_triatt_procuda/csrc/triatt_procuda_sm90.cu)

</details>



This page details the implementation of optimized triangle and pair-bias attention kernels within `opt_core`. It covers CUDA kernels for `sm80` and `sm90a` architectures, XLA implementations, the `k2b` binaries, the `apb`/`pair-fused` attention mechanism, `gather_attn` functionality, `sdpa_bias` handling, and the verification process for prebuilt ABI SHA256SUMs.

## Triangle Attention CUDA Kernels (sm80/sm90a)

The `opt_core` provides highly optimized CUDA kernels for triangle attention, specifically tailored for NVIDIA's `sm80` (Ampere) and `sm90a` (Hopper) architectures. These kernels are designed for efficiency in biomolecular modeling tasks, particularly within pairformer architectures.

### sm90a "Many-Warp MMA.Sync" Formulation

The `sm90a` kernels, such as those found in `common/opt_core/opt_core/kernels/triattn/cuda_sm90a/csrc/triattn_mw.cu` and `common/opt_core/opt_core/kernels/triattn/triattn_native/pkg/v11/triattn_pkg/cuda_c/csrc/triattn_mw.cu`, implement a "many-warp mma.sync" formulation. This approach is optimized for H100 GPUs, using `bf16` input, `fp32` accumulation, and `bf16` output.

The core operation is:
`out[b,i,h,q,:] = softmax_k( scale * q[b,i,h,q,:].k[b,i,h,k,:] + bias[b,h,q,k] (-inf where mask[b,i,k] == 0) ) @ v[b,i,h,k,:]` [common/opt_core/opt_core/kernels/triattn/cuda_sm90a/csrc/triattn_mw.cu:3-3]

Key features of this implementation include:
*   **CTA Structure**: One CTA (Cooperative Thread Array) consists of 12 warps, processing 3 pair rows (R=3) and 4 warps per row, covering a 128-query tile. [common/opt_core/opt_core/kernels/triattn/cuda_sm90a/csrc/triattn_mw.cu:5-6]
*   **Softmax Calculation**: A MAX-FREE softmax approach is used, where a per-row integer offset `m` is adjusted to keep the running sum within a specific range `[2^-20, 2^20]`. This avoids explicit maximum tracking, with a fallback "safe" pass for rare cases of `inf/nan` or zero sums. [common/opt_core/opt_core/kernels/triattn/cuda_sm90a/csrc/triattn_mw.cu:8-11]
*   **Software Pipelining**: Work is software-pipelined over half tiles, allowing for concurrent execution of exponentials, P V products, and S mma operations. [common/opt_core/opt_core/kernels/triattn/cuda_sm90a/csrc/triattn_mw.cu:12-14]
*   **Bias Handling**: The bias is provided as `[128 q x 32 k]` `fp32` boxes. Ring A stages hold bias keys 0-31 and K tiles, while Ring B stages hold bias keys 32-63 and V tiles. [common/opt_core/opt_core/kernels/triattn/cuda_sm90a/csrc/triattn_mw.cu:14-16]
*   **Masking**: Keys that are not attended to (due to padding or other masks) are folded into the staged bias as `-inf` columns. Irregular rows (e.g., with interior holes) are handled in a second pass. [common/opt_core/opt_core/kernels/triattn/cuda_sm90a/csrc/triattn_mw.cu:17-23]
*   **Shared Memory (`Smem`)**: A `Smem` struct manages shared memory for staging data, including `stage` buffers, `full`/`empty` flags, `tick` for release tickets, and `flagged` status. [common/opt_core/opt_core/kernels/triattn/cuda_sm90a/csrc/triattn_mw.cu:72-78]
    *   The `Smem` size is asserted to be within the shared memory budget. [common/opt_core/opt_core/kernels/triattn/cuda_sm90a/csrc/triattn_mw.cu:80]

### sm80 Kernels

The `sm80` kernels, such as `common/opt_core/opt_core/kernels/triattn/triattn_native/pkg/v11/triattn_pkg/cuda_80/csrc/triattn_sm80.cuh`, provide similar optimized triangle attention functionality for Ampere architectures. These kernels are designed to leverage the specific features of `sm80` for efficient computation.

### Parameters (`Params` struct)

Both `sm90a` and `sm80` kernels utilize a `Params` struct to pass configuration and tensor information to the kernel. This includes:
*   `tmK`, `tmV`, `tmB`: CUtensorMap for K, V, and Bias.
*   `q`, `out`: Pointers to query and output tensors, with their respective strides.
*   `mask`, `rowkind`: Pointers to mask and row kind tensors for handling attention masks.
*   `fix`, `list`: Pointers for managing fix-up passes and list-based recomputations.
*   `B, N, H, S, n_ktiles`: Batch size, sequence length, number of heads, sequence length (keys), and number of key tiles.
*   `ktend`: Pointer to an array indicating the end of key tiles for attended keys.
*   `qb`: CTA order for query tiles.
*   `c1`: Scale factor for softmax.
*   `dbg`: Debugging flags.
*   `tl`: Timeline stamps for profiling.
[common/opt_core/opt_core/kernels/triattn/cuda_sm90a/csrc/triattn_mw.cu:53-69]

```mermaid
graph TD
    subgraph "Triangle Attention Kernel (sm90a)"
        A[Input Q, K, V, Bias, Mask] --> B{CTA Processing}
        B --> C{Warp 1..12}
        C --> D[Compute S = Q K^T + Bias/Scale]
        D --> E[Max-Free Softmax]
        E --> F[Compute O += P V]
        F --> G{Output O}
        G --> H[Fix-up Pass (if needed)]
        H --> I[Final Output]
    end

    subgraph "Shared Memory (Smem)"
        J[Stage Buffers]
        K[Full/Empty Flags]
        L[Release Tickets (tick)]
        M[Flagged Status]
        N[Mask Bits (mbits)]
        O[Class (cls)]
        P[Key Tile End (kt_endr, kt_end)]
    end

    B -- "Uses" --> J
    B -- "Uses" --> K
    B -- "Uses" --> L
    B -- "Uses" --> M
    B -- "Uses" --> N
    B -- "Uses" --> O
    B -- "Uses" --> P

    subgraph "Parameters (Params)"
        Q[tmK, tmV, tmB]
        R[q, out, strides]
        S[mask, rowkind]
        T[fix, list]
        U[B, N, H, S, n_ktiles]
        V[ktend, qb, c1, dbg, tl]
    end

    B -- "Configured by" --> Q
    B -- "Configured by" --> R
    B -- "Configured by" --> S
    B -- "Configured by" --> T
    B -- "Configured by" --> U
    B -- "Configured by" --> V
```
**Diagram 1: Triangle Attention Kernel Data Flow and Components**

Sources:
*   `common/opt_core/opt_core/kernels/triattn/cuda_sm90a/csrc/triattn_mw.cu`
*   `common/opt_core/opt_core/kernels/triattn/triattn_native/pkg/v11/triattn_pkg/cuda_c/csrc/triattn_mw.cu`
*   `common/opt_core/opt_core/kernels/triattn/triattn_native/pkg/v11/triattn_pkg/cuda_80/csrc/triattn_sm80.cuh`

## Triangle Attention XLA Kernels

The `opt_core` also includes XLA implementations for triangle attention, such as `common/opt_core/opt_core/kernels/triattn_xla/csrc/triattn_m1_xla.cu` and `common/opt_core/opt_core/kernels/triattn_xla/csrc/triattn_sm80_xla.cu`. These kernels enable efficient execution on XLA-compatible backends, often used in JAX-based models. The XLA kernels provide an alternative path for triangle attention computation, leveraging XLA's graph compilation and optimization capabilities.

Sources:
*   `common/opt_core/opt_core/kernels/triattn_xla/csrc/triattn_m1_xla.cu`
*   `common/opt_core/opt_core/kernels/triattn_xla/csrc/triattn_sm80_xla.cu`

## K2B Binaries

The `k2b` binaries refer to specific kernel implementations, often associated with the "FlashPairformer Fusion" (`fpf`) kernels. For instance, `fpf_triatt_k2b` is a FlashPairformer kernel carried in `opt_core`. [common/opt_core/opt_core/kernels/fpf_triatt_k2b/NOTICE:1] These kernels are derived from or re-state the arithmetic of Protenix's pair-stack modules. [common/opt_core/opt_core/kernels/fpf_triatt_k2b/NOTICE:3-4]

The `k2b` core is one of the named attention cores that `opt_core.attn.pair_fused` can dispatch to. [common/opt_core/opt_core/attn/pair_fused.py:69]

Sources:
*   `common/opt_core/opt_core/kernels/fpf_triatt_k2b/NOTICE`
*   `common/opt_core/opt_core/attn/pair_fused.py`

## APB / Pair-Fused Attention

The `opt_core.attn.pair_fused` module provides a comprehensive framework for pair-fused attention, encompassing the prologue, core attention dispatch, and epilogue. This module is engine-agnostic and supports different implementations. [common/opt_core/opt_core/attn/pair_fused.py:1-4]

### Implementations

Three main implementations are supported, selected by name:
*   `'fpf'`: FlashPairformer Fusion kernels (`fpf_triatt_pro`, `fpf_triatt_epi`, `fpf_transition`). This is the reference recipe. [common/opt_core/opt_core/attn/pair_fused.py:7-8]
*   `'lnl'`: `lnl_fused` kernels (ln_linear prologue, cuBLAS GEMM, gate_transpose epilogue, fused_transition). [common/opt_core/opt_core/attn/pair_fused.py:9]
*   `'torch'`: Plain PyTorch implementation around the attention core, used for non-power-of-two dimensions and as a baseline. [common/opt_core/opt_core/attn/pair_fused.py:10-12]

### Fused Components

The `pair_fused` attention mechanism integrates several operations into single kernels for efficiency:
*   **Prologue**: LayerNorm -> q|k|v|g|pair-bias projections. [common/opt_core/opt_core/attn/pair_fused.py:1-2]
*   **Core Attention Dispatch**: Dispatches to `flash_triattn`, `k2b`, or other vendor kernels. [common/opt_core/opt_core/attn/pair_fused.py:2-3]
*   **Epilogue**: Sigmoid gate * o @ W_o^T [+ residual, transposed scatter]. [common/opt_core/opt_core/attn/pair_fused.py:3-4]
*   **Fused SwiGLU Transition**: LN -> W_a|W_b -> silu(a)*b -> W_out [+ residual]. [common/opt_core/opt_core/attn/pair_fused.py:4-5]

### Cell Resolution

The `pair_fused` module uses a cell table (`pair_fused_cells.json`) to resolve and pin launch configurations. [common/opt_core/opt_core/attn/pair_fused.py:16-17]
*   `lookup_cell` and `preflight` functions determine the appropriate kernel based on `impl`, `piece`, `shape key`, `compute capability`, and Triton version. [common/opt_core/opt_core/attn/pair_fused.py:17-25]
*   If a key is `MEASURED OFF` or `UNKNOWN`, it falls back to stock statements or safe settings, respectively. [common/opt_core/opt_core/attn/pair_fused.py:18-25]
*   Refusals are handled by raising an `Unsupported` exception with a reason token. [common/opt_core/opt_core/attn/pair_fused.py:25-26]

### Canonical Weights

The module defines canonical weight keys for triangle attention (`TRIATTN_KEYS`) and transition (`TRANSITION_KEYS`) to ensure consistent parameter mapping. [common/opt_core/opt_core/attn/pair_fused.py:28-31]

```mermaid
graph TD
    subgraph "opt_core.attn.pair_fused"
        A[Input Pair Tensor (z)] --> B{Prologue}
        B -- "LayerNorm, Projections" --> C[Q, K, V, G, Pair-Bias]
        C --> D{Core Attention Dispatch}
        D -- "flash_triattn, k2b, tier:fast, etc." --> E[Attention Output (o)]
        E --> F{Epilogue}
        F -- "Sigmoid Gate, W_o^T, Residual" --> G[Updated Pair Tensor (u)]
        G --> H{Fused SwiGLU Transition}
        H -- "LayerNorm, W_a|W_b, silu, W_out, Residual" --> I[Transition Output]
    end

    subgraph "Cell Resolution"
        J[pair_fused_cells.json]
        K[lookup_cell / preflight]
        L[CellDecision]
        M[Unsupported Exception]
    end

    D -- "Selects Kernel via" --> K
    K -- "Reads from" --> J
    K -- "Returns" --> L
    K -- "On Refusal" --> M

    subgraph "Implementations"
        N[fpf: FlashPairformer Fusion]
        O[lnl: lnl_fused kernels]
        P[torch: Plain PyTorch]
    end

    D -- "Uses" --> N
    D -- "Uses" --> O
    D -- "Uses" --> P

    subgraph "Weight Packing"
        Q[pack_triattn_weights]
        R[pack_transition_weights]
    end

    A -- "Uses" --> Q
    H -- "Uses" --> R
```
**Diagram 2: Pair-Fused Attention Data Flow and Components**

Sources:
*   `common/opt_core/opt_core/attn/pair_fused.py`
*   `common/opt_core/opt_core/kernels/fpf_triatt_pro/NOTICE`
*   `common/opt_core/opt_core/kernels/fpf_triatt_epi/NOTICE`
*   `common/opt_core/opt_core/kernels/fpf_transition/NOTICE`

## Gather Attention (`gather_attn`)

While not explicitly detailed in the provided snippets, `gather_attn` refers to a mechanism for gathering attention outputs, often in distributed or sharded environments. The `rowpair` module, particularly `opt_core.mem.rowpair.shard`, includes functions like `shard_rows` and `gather_rows` that are crucial for managing tensor distribution and collection across multiple ranks or devices. [common/opt_core/tests/test_rowpair_shard_043.py:121] This is essential for attention mechanisms operating on large tensors that need to be sharded.

Sources:
*   `common/opt_core/tests/test_rowpair_shard_043.py`

## SDPA Bias

The term `sdpa_bias` refers to the bias component within Scaled Dot-Product Attention (SDPA). In the context of the triangle attention kernels, the bias is a critical input. The `sm90a` kernel description explicitly mentions the `bias[b,h,q,k]` term in the softmax calculation. [common/opt_core/opt_core/kernels/triattn/cuda_sm90a/csrc/triattn_mw.cu:3] The bias is pre-scaled and arrives as `fp32` boxes, serving as the `mma` C operand. [common/opt_core/opt_core/kernels/triattn/cuda_sm90a/csrc/triattn_mw.cu:6-7]

The `pair_fused` module also handles pair-bias rounding, where `bias = fp32(bf16 GEMM output of the bf16 LN output)`. [common/opt_core/opt_core/attn/pair_fused.py:13-14] This ensures consistency with autocast-stock rounding.

Sources:
*   `common/opt_core/opt_core/kernels/triattn/cuda_sm90a/csrc/triattn_mw.cu`
*   `common/opt_core/opt_core/attn/pair_fused.py`

## Prebuilt ABI SHA256SUMS Verification

The `opt_core` repository includes prebuilt binaries for its CUDA kernels, and their integrity is verified using SHA256 checksums. These checksums are stored in `SHA256SUMS` files within the `prebuilt` directories for specific CUDA architectures, PyTorch versions, and Python versions.

For example, for `sm90a` kernels:
*   `common/opt_core/opt_core/kernels/triattn/cuda_sm90a/prebuilt/torch2.11.0+cu128-cpython-312-x86_64-linux-gnu-sm90/SHA256SUMS` contains the checksum for `triattn_cuda_sm90.so`. [common/opt_core/opt_core/kernels/triattn/cuda_sm90a/prebuilt/torch2.11.0+cu128-cpython-312-x86_64-linux-gnu-sm90/SHA256SUMS:1]
*   Similar files exist for other PyTorch and CUDA versions, such as `torch2.7.1+cu126` [common/opt_core/opt_core/kernels/triattn/cuda_sm90a/prebuilt/torch2.7.1+cu126-cpython-311-x86_64-linux-gnu-sm90/SHA256SUMS:1] and `torch2.12.0+cu130` [common/opt_core/opt_core/kernels/triattn/cuda_sm90a/prebuilt/torch2.12.0+cu130-cpython-311-x86_64-linux-gnu-sm90/SHA256SUMS:1].

This verification process ensures that the prebuilt kernel binaries have not been tampered with and are the exact versions intended for use with specific software stacks.

Sources:
*   `common/opt_core/opt_core/kernels/triattn/cuda_sm90a/prebuilt/torch2.11.0+cu128-cpython-312-x86_64-linux-gnu-sm90/SHA256SUMS`
*   `common/opt_core/opt_core/kernels/triattn/cuda_sm90a/prebuilt/torch2.7.1+cu126-cpython-311-x86_64-linux-gnu-sm90/SHA256SUMS`
*   `common/opt_core/opt_core/kernels/triattn/cuda_sm90a/prebuilt/torch2.12.0+cu130-cpython-311-x86_64-linux-gnu-sm90/SHA256SUMS`

---

