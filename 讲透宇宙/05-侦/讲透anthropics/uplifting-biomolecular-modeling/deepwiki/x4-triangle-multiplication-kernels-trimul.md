<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/uplifting-biomolecular-modeling · extra page Triangle Multiplication Kernels (trimul) · fetched 2026-10-26 -->

# Triangle Multiplication Kernels (trimul)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [common/opt_core/opt_core/kernels/META/triattn_xla.json](common/opt_core/opt_core/kernels/META/triattn_xla.json)
- [common/opt_core/opt_core/kernels/META/trimul_xla.json](common/opt_core/opt_core/kernels/META/trimul_xla.json)
- [common/opt_core/opt_core/kernels/fpf_pallas/trimul_pallas.py](common/opt_core/opt_core/kernels/fpf_pallas/trimul_pallas.py)
- [common/opt_core/opt_core/kernels/fpf_trimul/DESIGN.md](common/opt_core/opt_core/kernels/fpf_trimul/DESIGN.md)
- [common/opt_core/opt_core/kernels/fpf_trimul_rows/kernels.py](common/opt_core/opt_core/kernels/fpf_trimul_rows/kernels.py)
- [common/opt_core/opt_core/kernels/fpf_trimul_v4/DESIGN.md](common/opt_core/opt_core/kernels/fpf_trimul_v4/DESIGN.md)
- [common/opt_core/opt_core/kernels/fpf_trimul_v4/README.md](common/opt_core/opt_core/kernels/fpf_trimul_v4/README.md)
- [common/opt_core/opt_core/kernels/fpf_trimul_v4/__init__.py](common/opt_core/opt_core/kernels/fpf_trimul_v4/__init__.py)
- [common/opt_core/opt_core/kernels/fpf_trimul_v4/generic.py](common/opt_core/opt_core/kernels/fpf_trimul_v4/generic.py)
- [common/opt_core/opt_core/kernels/fpf_trimul_v4/kdesc.py](common/opt_core/opt_core/kernels/fpf_trimul_v4/kdesc.py)
- [common/opt_core/opt_core/kernels/fpf_trimul_v4/kernels.py](common/opt_core/opt_core/kernels/fpf_trimul_v4/kernels.py)
- [common/opt_core/opt_core/kernels/fpf_trimul_v4/kexp.py](common/opt_core/opt_core/kernels/fpf_trimul_v4/kexp.py)
- [common/opt_core/opt_core/kernels/fpf_trimul_v4/trimul.py](common/opt_core/opt_core/kernels/fpf_trimul_v4/trimul.py)
- [common/opt_core/opt_core/kernels/pallas/cd_trimul/NOTICE](common/opt_core/opt_core/kernels/pallas/cd_trimul/NOTICE)
- [common/opt_core/opt_core/kernels/pallas/cd_trimul/trimul_pallas.py](common/opt_core/opt_core/kernels/pallas/cd_trimul/trimul_pallas.py)
- [common/opt_core/opt_core/kernels/trimul/DESIGN.md](common/opt_core/opt_core/kernels/trimul/DESIGN.md)
- [common/opt_core/opt_core/kernels/trimul/DESIGN_tx_sm90a.md](common/opt_core/opt_core/kernels/trimul/DESIGN_tx_sm90a.md)
- [common/opt_core/opt_core/kernels/trimul/esm_v61/DESIGN.md](common/opt_core/opt_core/kernels/trimul/esm_v61/DESIGN.md)
- [common/opt_core/opt_core/kernels/trimul/native/DESIGN.md](common/opt_core/opt_core/kernels/trimul/native/DESIGN.md)
- [common/opt_core/opt_core/kernels/trimul/native/__init__.py](common/opt_core/opt_core/kernels/trimul/native/__init__.py)
- [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/README.md](common/opt_core/opt_core/kernels/trimul/native/pkg/v5/README.md)
- [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z128_h128.cu](common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z128_h128.cu)
- [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z128_h256.cu](common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z128_h256.cu)
- [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z128_h384.cu](common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z128_h384.cu)
- [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z128_h64.cu](common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z128_h64.cu)
- [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z256_h128.cu](common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z256_h128.cu)
- [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z256_h256.cu](common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z256_h256.cu)
- [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z256_h384.cu](common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z256_h384.cu)
- [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z256_h64.cu](common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z256_h64.cu)
- [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z384_h128.cu](common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z384_h128.cu)
- [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z384_h256.cu](common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z384_h256.cu)
- [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z384_h384.cu](common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z384_h384.cu)
- [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z384_h64.cu](common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z384_h64.cu)
- [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z64_h128.cu](common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z64_h128.cu)
- [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z64_h256.cu](common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z64_h256.cu)
- [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z64_h384.cu](common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z64_h384.cu)
- [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z64_h64.cu](common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z64_h64.cu)
- [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/python/trimul_native/__init__.py](common/opt_core/opt_core/kernels/trimul/native/pkg/v5/python/trimul_native/__init__.py)
- [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/python/trimul_native/face.py](common/opt_core/opt_core/kernels/trimul/native/pkg/v5/python/trimul_native/face.py)
- [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/python/trimul_native/kernel.py](common/opt_core/opt_core/kernels/trimul/native/pkg/v5/python/trimul_native/kernel.py)
- [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/python/trimul_native/launch.py](common/opt_core/opt_core/kernels/trimul/native/pkg/v5/python/trimul_native/launch.py)
- [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/python/trimul_native/ops.py](common/opt_core/opt_core/kernels/trimul/native/pkg/v5/python/trimul_native/ops.py)
- [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/python/trimul_native/sm80_ops.py](common/opt_core/opt_core/kernels/trimul/native/pkg/v5/python/trimul_native/sm80_ops.py)
- [common/opt_core/opt_core/kernels/trimul/tx_sm90a/INTEGRATION.md](common/opt_core/opt_core/kernels/trimul/tx_sm90a/INTEGRATION.md)
- [common/opt_core/opt_core/kernels/trimul/tx_sm90a/NOTICE.md](common/opt_core/opt_core/kernels/trimul/tx_sm90a/NOTICE.md)
- [common/opt_core/opt_core/kernels/trimul/tx_sm90a/TESTVECTORS.json](common/opt_core/opt_core/kernels/trimul/tx_sm90a/TESTVECTORS.json)
- [common/opt_core/opt_core/kernels/trimul/tx_sm90a/__init__.py](common/opt_core/opt_core/kernels/trimul/tx_sm90a/__init__.py)
- [common/opt_core/opt_core/kernels/trimul/tx_sm90a/ops.py](common/opt_core/opt_core/kernels/trimul/tx_sm90a/ops.py)
- [common/opt_core/opt_core/kernels/trimul/tx_sm90a/trimul.py](common/opt_core/opt_core/kernels/trimul/tx_sm90a/trimul.py)
- [common/opt_core/opt_core/kernels/trimul/tx_sm90a/trimul_exact.py](common/opt_core/opt_core/kernels/trimul/tx_sm90a/trimul_exact.py)
- [common/opt_core/opt_core/kernels/trimul_esm_shapes/DESIGN.md](common/opt_core/opt_core/kernels/trimul_esm_shapes/DESIGN.md)
- [common/opt_core/opt_core/kernels/trimul_esm_shapes/kernels.py](common/opt_core/opt_core/kernels/trimul_esm_shapes/kernels.py)
- [common/opt_core/opt_core/kernels/trimul_xla/DESIGN.md](common/opt_core/opt_core/kernels/trimul_xla/DESIGN.md)
- [common/opt_core/opt_core/kernels/trimul_xla/NOTICE](common/opt_core/opt_core/kernels/trimul_xla/NOTICE)
- [common/opt_core/opt_core/kernels/trimul_xla/__init__.py](common/opt_core/opt_core/kernels/trimul_xla/__init__.py)
- [common/opt_core/opt_core/kernels/trimul_xla/pkg/v1/README.md](common/opt_core/opt_core/kernels/trimul_xla/pkg/v1/README.md)
- [common/opt_core/opt_core/kernels/trimul_xla/pkg/v1/csrc/tmn90_z128_h128.cu](common/opt_core/opt_core/kernels/trimul_xla/pkg/v1/csrc/tmn90_z128_h128.cu)
- [common/opt_core/tests/gpu/test_apb_core_gpu.py](common/opt_core/tests/gpu/test_apb_core_gpu.py)
- [common/opt_core/tests/test_triattn_xla_pkg.py](common/opt_core/tests/test_triattn_xla_pkg.py)
- [common/opt_core/tests/test_trimul_xla_pkg.py](common/opt_core/tests/test_trimul_xla_pkg.py)
- [opendde/opt/opendde_opt/tests/test_lnstream_prebuilt.py](opendde/opt/opendde_opt/tests/test_lnstream_prebuilt.py)
- [protenix_v2/opt/forward/flashpairformer/third_party/fpf_smalln/__init__.py](protenix_v2/opt/forward/flashpairformer/third_party/fpf_smalln/__init__.py)

</details>



This page details the various implementations of Triangle Multiplication (trimul) kernels within the `opt_core` framework. These kernels are critical for performance-sensitive operations in biomolecular modeling, particularly within pairformer architectures. The implementations include native CUDA, Triton, and XLA variants, each optimized for specific hardware and use cases. We will cover the `fpf_trimul_v4` Triton-based kernels, the `trimul_native` CUDA kernels, and the `trimul_xla` XLA-based kernels, along with their build processes and design considerations.

## Triangle Multiplication Operation

The core operation performed by these kernels is the Triangle Multiplication, which can be either "outgoing" or "incoming". The mathematical formulation is as follows:
Given an input pair tensor `z` (shape `[B, N, N, c_z]`) and an optional `mask` (shape `[B, N, N]`), the operation proceeds in three main stages:

1.  **Prologue (K1):**
    `x = LN_in(z)`
    `a_ij = sigmoid(x_ij W_ag^T + b_ag) * (x_ij W_ap^T + b_ap) * mask_ij`
    `b_ij` is computed similarly.
    This stage involves Layer Normalization (`LN_in`), gated projections, and masking, producing two sets of channel-major bf16 planes (`ab[2, B, D, Np, Np]`).
    Sources: [common/opt_core/opt_core/kernels/fpf_trimul_v4/DESIGN.md:4-6](), [common/opt_core/opt_core/kernels/trimul/native/DESIGN.md:7-8]()

2.  **Contraction (BMM):**
    `X_ij = sum_k a_ik * b_jk` (for "outgoing") or `sum_k a_ki * b_kj` (for "incoming").
    This is typically a cuBLAS strided-batched GEMM operation on the bf16 planes, accumulating in fp32 and outputting bf16.
    Sources: [common/opt_core/opt_core/kernels/fpf_trimul_v4/DESIGN.md:26-27](), [common/opt_core/opt_core/kernels/trimul/native/DESIGN.md:23-24]()

3.  **Epilogue (K3):**
    `update = sigmoid(x W_og^T + b_og) * (LN_out(X) W_o^T + b_o)`
    The final output is `update`, or `z + update` if `residual=True`. This stage involves another Layer Normalization (`LN_out`), output projection, and gating.
    Sources: [common/opt_core/opt_core/kernels/fpf_trimul_v4/DESIGN.md:7-8](), [common/opt_core/opt_core/kernels/trimul/native/DESIGN.md:9-10]()

## `fpf_trimul_v4` (Triton)

The `fpf_trimul_v4` package provides a portable Triton implementation of the Triangle Multiplication. It is designed as a member of the FlashPairformer kernel family.

### Architecture and Data Flow

The `fpf_trimul_v4` kernels are structured as three launches per call:
1.  **K1 (Prologue):** Fused `LN_in` + dual gated projection prologue, writing channel-major bf16 planes.
2.  **BMM (Contraction):** One cuBLAS strided-batched contraction on the zero-padded planes.
3.  **K3 (Epilogue):** Fused `LN_out` + output projection + gate (+ residual) epilogue.
Sources: [common/opt_core/opt_core/kernels/fpf_trimul_v4/README.md:3-6]()

The kernels support various channel widths (`c_z`, `c_hidden`) and input data types (bf16 or fp32). When `z` is fp32, the `LN_in` input is fp32, and the output is fp32, but the GEMM operands remain bf16.
Sources: [common/opt_core/opt_core/kernels/fpf_trimul_v4/README.md:30-31]()

#### `fpf_trimul_v4.generic` API

The `fpf_trimul_v4.generic` module provides a module-agnostic API for the triangle multiplication.
It exposes functions like `pack_weights`, `supported`, and `trimul`.
Sources: [common/opt_core/opt_core/kernels/fpf_trimul_v4/README.md:19-28](), [common/opt_core/opt_core/kernels/fpf_trimul_v4/generic.py:1-26]()

-   `pack_weights(...)`: Packs the canonical weight tensors into a single structure. This can be cached on a `cache_owner` module.
    Sources: [common/opt_core/opt_core/kernels/fpf_trimul_v4/README.md:20-22](), [common/opt_core/opt_core/kernels/fpf_trimul_v4/generic.py:5-6]()
-   `supported(z, mask, weights)`: Checks if the given inputs are supported by the kernel without raising an error.
    Sources: [common/opt_core/opt_core/kernels/fpf_trimul_v4/README.md:23](), [common/opt_core/opt_core/kernels/fpf_trimul_v4/generic.py:6]()
-   `trimul(z, mask, direction, weights, residual, pad)`: Executes the triangle multiplication. Returns a new tensor.
    Sources: [common/opt_core/opt_core/kernels/fpf_trimul_v4/README.md:24](), [common/opt_core/opt_core/kernels/fpf_trimul_v4/generic.py:7]()

#### Triton Kernel Details

The Triton kernels, such as those found in `common/opt_core/opt_core/kernels/trimul_esm_shapes/kernels.py` and `common/opt_core/opt_core/kernels/fpf_trimul_rows/kernels.py`, implement the K1 and K3 stages. They are designed to handle various channel widths by processing them in power-of-two chunks.
Sources: [common/opt_core/opt_core/kernels/trimul_esm_shapes/kernels.py:9-15](), [common/opt_core/opt_core/kernels/fpf_trimul_rows/kernels.py:15-19]()

Key features include:
-   **Channel Chunking:** `C` and `CH` (pair and hidden widths) are processed as `NCK x CK` / `NCH x CHK` chunks. This allows native execution for widths like 64, 128, 256, 384, 512.
    Sources: [common/opt_core/opt_core/kernels/trimul_esm_shapes/kernels.py:11-15]()
-   **I/O Dtype:** Supports bf16 or fp32 for `z` and output. LayerNorm statistics are always fp32, and MMAs are bf16 x bf16 -> fp32 accumulate.
    Sources: [common/opt_core/opt_core/kernels/trimul_esm_shapes/kernels.py:16-18]()
-   **Descriptors:** Kernels can use Triton's tensor descriptor API (`tl.make_tensor_descriptor`) for `cc 9.0` or pointer loads for `cc 8.0`.
    Sources: [common/opt_core/opt_core/kernels/trimul_esm_shapes/kernels.py:19-21]()
-   **Residual:** K3 can optionally add `z` as a residual.
    Sources: [common/opt_core/opt_core/kernels/trimul_esm_shapes/kernels.py:22]()
-   **Levers:** Includes levers for `sigmoid` approximation, `stagger` (weight-block offset), `incnt`/`form` (contraction form), `x32` (fp32 contraction output), and `stock_round`.
    Sources: [common/opt_core/opt_core/kernels/trimul_esm_shapes/kernels.py:23-24]()

#### Layer Normalization in Triton Kernels

The Triton kernels implement two-pass Layer Normalization over resident channel chunks.
-   `_ln_rows`: Normalizes across channels for `[BM, CK]` fp32 chunks (tokens x channels).
    Sources: [common/opt_core/opt_core/kernels/trimul_esm_shapes/kernels.py:68-110]()
-   `_ln_cols`: Normalizes across channels for `[CK, BM]` fp32 chunks (channels x tokens).
    Sources: [common/opt_core/opt_core/kernels/trimul_esm_shapes/kernels.py:113-152]()

These functions calculate mean and variance in fp32 and then apply normalization, converting to bf16 for the output chunks.
Sources: [common/opt_core/opt_core/kernels/trimul_esm_shapes/kernels.py:79-80, 109-110, 139-140]()

#### Environment Variables
Several environment variables control the behavior of `fpf_trimul_v4`:
-   `FPF_TRIMUL_V4_NMIN`: Minimum token count for the served cell (default 101).
-   `FPF_TRIMUL_V4_CELLS`: Path to a kit's custom cells table.
-   `FPF_TRIMUL_V4_BATCH`: Controls batch processing ("loop" for single-plane launches, "native" for one launch set).
-   `FPF_TRIMUL_V4_STOCK_ROUND`: Overrides `stock_round` behavior.
-   `FPF_TRIMUL_V4_CFG`: Engineering variable for literal `{k1, k3}` cell configuration.
-   `FPF_TRIMUL_V4_ALLOW_DEFAULT_CELLS`: Engineering variable to admit table rows with non-served status.
-   `OPT_CORE_VERDICT_DIR`: Directory for warm-probe verdict stamps.
Sources: [common/opt_core/opt_core/kernels/fpf_trimul_v4/README.md:49-56]()

### Diagram: `fpf_trimul_v4` Data Flow

```mermaid
graph TD
    subgraph "fpf_trimul_v4.generic"
        A[Input: z, mask, weights] --> B{G.pack_weights};
        B --> C[Packed Weights];
        C --> D{G.supported};
        D -- "ok=False" --> E[Stock Path];
        D -- "ok=True" --> F{G.trimul};
        F --> G[Output: update / z + update];
    end

    subgraph "Kernel Stages"
        F --> K1_Stage[K1: LN_in + Gated Projections + Mask];
        K1_Stage -- "bf16 planes" --> BMM_Stage[BMM: cuBLAS Strided-Batched GEMM];
        BMM_Stage -- "bf16 X" --> K3_Stage[K3: LN_out + Output Projection + Gate (+ Residual)];
        K3_Stage --> G;
    end

    subgraph "Triton Kernel Details"
        K1_Stage --> K1_LN[LN_in (fp32 stats, two-pass)];
        K1_LN --> K1_Proj[Gated Projections (bf16 MMAs)];
        K1_Proj --> K1_Mask[Masking];
        K1_Mask --> K1_Output[Channel-major bf16 planes];

        K3_Stage --> K3_LN[LN_out (fp32 stats, two-pass)];
        K3_LN --> K3_Proj[Output Projection];
        K3_Proj --> K3_Gate[Output Gate (recomputed LN_in(z))];
        K3_Gate --> K3_Residual[Optional Residual Add];
        K3_Residual --> K3_Output[Output in z's dtype];
    end

    style K1_Stage fill:#fff,stroke:#333,stroke-width:2px
    style BMM_Stage fill:#fff,stroke:#333,stroke-width:2px
    style K3_Stage fill:#fff,stroke:#333,stroke-width:2px
```
Sources: [common/opt_core/opt_core/kernels/fpf_trimul_v4/README.md:3-6](), [common/opt_core/opt_core/kernels/fpf_trimul_v4/DESIGN.md:21-29]()

## `trimul_native` (CUDA)

The `trimul_native` package provides triangle multiplication kernels implemented as arch-keyed CUDA cubins. These are designed for high performance on specific GPU architectures (sm_90a and sm_80).
Sources: [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/README.md:1-5]()

### Architecture and Data Flow

The `trimul_native` kernels follow the same three-stage structure (K1, BMM, K3) as `fpf_trimul_v4`.
Sources: [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/README.md:22-24]()

Key characteristics:
-   **Arch-keyed Cubins:** Kernels are compiled into cubins for specific architectures (e.g., `sm_90a`, `sm_80`).
    Sources: [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/README.md:3-4]()
-   **Parameterization:** Parameterized over channel widths (`c_z`, `c_hidden` in {64, 128, 256, 384}) and token counts (16-4096).
    Sources: [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/README.md:5-6]()
-   **Binary Route:** Cubins are loaded using `cuModuleLoadData` and launched via `cuLaunchKernel` on `torch.cuda.current_stream()`. Workspaces are managed by the framework's caching allocator.
    Sources: [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/README.md:43-45]()
-   **Sealed Package:** The kernels are distributed as a sealed payload (`pkg/vN/`) containing all necessary files, including sources, build manifests, and test vectors. This ensures byte-for-byte reproducibility and prevents tampering.
    Sources: [common/opt_core/opt_core/kernels/trimul/native/__init__.py:1-2]()

#### Per-Shape `.cu` Variants

The `trimul_native` implementation uses individual `.cu` files for specific `c_z` and `c_hidden` combinations. For example:
-   `tmn90_z64_h128.cu`: For `c_z = 64`, `c_hidden = 128` on `sm_90a`.
    Sources: [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z64_h128.cu:4-5]()
-   `tmn90_z128_h256.cu`: For `c_z = 128`, `c_hidden = 256` on `sm_90a`.
    Sources: [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z128_h256.cu:4-5]()

These `.cu` files include a common header (`tmn_sm90_unit.cuh`) that instantiates the kernel family with the defined `TMN_CZ` and `TMN_CH` macros.
Sources: [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z64_h128.cu:6]()

#### `trimul_native` Build Pipeline

The build process for `trimul_native` involves `nvcc` compilation of the `.cu` sources into cubins.
Sources: [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/README.md:32]()

The `build.py` script handles:
-   Compiling all units (`--all`) or specific architectures (`--archs`).
-   Generating `build/<arch>/<unit>.cubin` and `build/manifest.json`.
-   The `manifest.json` records cubin and source digests, `nvcc` release, flags, and ELF facts.
Sources: [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/README.md:53-54]()

Test vectors are generated and replayed to ensure byte-gate correctness.
Sources: [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/README.md:56-57]()

#### `trimul_native` Refusals

The `trimul_native` kernels employ a strict refusal policy. If inputs or environment conditions do not match the supported configurations, the operation is refused by name, never silently substituted.
Examples of refusal reasons include: `no_cubin:<arch>`, `driver_unavailable:<why>`, `cc_unsupported:<cc>`, `shape:`, `dtype:`, `variant:`.
Sources: [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/README.md:68-70](), [common/opt_core/opt_core/kernels/trimul/native/DESIGN.md:18-20]()

### Diagram: `trimul_native` Build and Deployment

```mermaid
graph TD
    subgraph "Development"
        A[csrc/*.cuh] --> B[csrc/*.cu: TMN_CZ, TMN_CH macros];
        B --> C[trimul_native.build: nvcc];
        C -- "build/<arch>/<unit>.cubin" --> D[build/manifest.json];
        C -- "build/<arch>/<unit>.ptxas.txt" --> D;
        E[testvectors/ (closed-form)] --> F[trimul_native.vectors make];
        F --> G[testvectors/manifest.json];
    end

    subgraph "Sealed Release (pkg/vN)"
        D & G --> H[trimul_native.seal];
        H -- "pkg/vN/ (sealed payload)" --> I[opt_core.kernels.trimul.native];
    end

    subgraph "Runtime"
        I --> J[face.check(): verify_digests, load cubins];
        J -- "cuModuleLoadData" --> K[CUDA Driver];
        K --> L[face.forward(): cuLaunchKernel];
        L --> M[torch.cuda.current_stream()];
        M --> N[Output];
    end

    style A fill:#fff,stroke:#333,stroke-width:2px
    style B fill:#fff,stroke:#333,stroke-width:2px
    style C fill:#fff,stroke:#333,stroke-width:2px
    style D fill:#fff,stroke:#333,stroke-width:2px
    style E fill:#fff,stroke:#333,stroke-width:2px
    style F fill:#fff,stroke:#333,stroke-width:2px
    style G fill:#fff,stroke:#333,stroke-width:2px
    style H fill:#fff,stroke:#333,stroke-width:2px
    style I fill:#fff,stroke:#333,stroke-width:2px
    style J fill:#fff,stroke:#333,stroke-width:2px
    style K fill:#fff,stroke:#333,stroke-width:2px
    style L fill:#fff,stroke:#333,stroke-width:2px
    style M fill:#fff,stroke:#333,stroke-width:2px
    style N fill:#fff,stroke:#333,stroke-width:2px
```
Sources: [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/README.md:28-39, 43-45, 52-62](), [common/opt_core/opt_core/kernels/trimul/native/__init__.py:1-4, 19-20, 27-30]()

## `trimul_xla` (XLA)

The `trimul_xla` package provides XLA-based triangle multiplication kernels. While the provided `README.md` for `trimul_xla` is identical to `trimul_native`, indicating a similar underlying structure and design philosophy, the key difference lies in the target compilation backend: XLA instead of native CUDA.
Sources: [common/opt_core/opt_core/kernels/trimul_xla/pkg/v1/README.md:1-85]()

This implies that `trimul_xla` would leverage XLA's capabilities for compilation and execution, potentially targeting different hardware or offering different optimization strategies. The `DESIGN.md` for `trimul_xla` would detail these XLA-specific aspects.
Sources: [common/opt_core/opt_core/kernels/trimul_xla/DESIGN.md]()

## `fpf_trimul_rows` (Triton for Row-Blocks)

The `fpf_trimul_rows` package contains Triton kernels specifically designed for row-block statements of the triangle multiplicative update. These are used when `opt_core.mem.rowpair.trimul_fused` is active for `P > 1` (multiple partitions).
Sources: [common/opt_core/opt_core/kernels/fpf_trimul_rows/kernels.py:1-3]()

These kernels are similar to `fpf_trimul_v4` but are adapted to operate on channel-last `z` row blocks and write channel-major bf16 planes through specific strides. They support the same channel widths and chunking mechanisms.
Sources: [common/opt_core/opt_core/kernels/fpf_trimul_rows/kernels.py:4-14, 15-20]()

## Numerics and Precision

All `trimul` implementations prioritize numerical stability and correctness.
-   **bf16 Tensor-Core GEMMs:** Utilize bf16 for matrix multiplications with fp32 accumulation.
-   **fp32 LayerNorm Statistics:** Layer Normalization statistics are computed in fp32.
-   **fp32 Gating:** Gating operations are performed in fp32.
-   **Rounding Points:** The rounding points are carefully chosen to match the `cuEquivariance` operation under bf16 autocast, ensuring a specific tolerance class rather than bit-identical results to stock ops.
Sources: [common/opt_core/opt_core/kernels/fpf_trimul_v4/DESIGN.md:42-46](), [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/README.md:73-77]()

The `trimul_native` kernels, by default, keep `--use_fast_math` off during compilation to ensure precise IEEE division and `expf` for sigmoid and LayerNorm.
Sources: [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/README.md:73-74]()

An "exact" variant (`native_exact`) aims for bitwise identity with `cuequivariance_torch` by specific choices in LayerNorm evaluation, plane handling, and arithmetic order.
Sources: [common/opt_core/opt_core/kernels/trimul/native/DESIGN.md:61-67]()

## Warm Probe and Verification

A "warm probe" mechanism (`generic.probe`) is used to verify the numerical correctness of the served kernels.
-   It runs once per process and shape class (C, D, bias, input dtype).
-   Compares kernel output against an fp64 reference statement.
-   Verifies against `SAME_CLASS_RMS` and `SAME_CLASS_MAX` bars.
-   A passed verdict is stamped, keyed by package version, digest, cell word, device, driver, CUDA, torch, triton, and python versions. This allows subsequent processes to skip the probe.
Sources: [common/opt_core/opt_core/kernels/fpf_trimul_v4/DESIGN.md:36-41](), [common/opt_core/opt_core/kernels/fpf_trimul_v4/generic.py:41-50]()

## Memory Management

The kernels manage memory for transient workspaces, including the bf16 planes and contraction results. The `workspace_bytes` function provides an analytic formula for the per-call transient device memory.
Sources: [common/opt_core/opt_core/kernels/fpf_trimul_v4/generic.py:58-63](), [common/opt_core/opt_core/kernels/trimul/native/pkg/v5/README.md:8-13]()

For batched operations, `BATCH_MODE="native"` allocates the entire batch's workspace at once, while `BATCH_MODE="loop"` processes single-plane launch sets sequentially, reducing peak memory.
Sources: [common/opt_core/opt_core/kernels/fpf_trimul_v4/generic.py:18-25]()

## Glossary of Key Terms

-   **K1:** The prologue kernel stage, performing LayerNorm, gated projections, and masking.
-   **K3:** The epilogue kernel stage, performing LayerNorm, output projection, and gating.
-   **`c_z`:** The channel width of the input `z` tensor.
-   **`c_hidden`:** The hidden channel width used in projections.
-   **`Np`:** `N` (token count) rounded up to a padding multiple (e.g., 16).
-   **`bf16`:** Bfloat16 floating-point format.
-   **`sm_90a` / `sm_80`:** NVIDIA GPU compute capabilities (e.g., Hopper, Ampere).
-   **Cubins:** CUDA binary files containing compiled GPU code.
-   **Triton:** A DSL for writing highly optimized GPU kernels.
-   **XLA:** Accelerated Linear Algebra, a domain-specific compiler for linear algebra.
-   **Warm Probe:** A runtime verification step to ensure numerical correctness.
-   **Refusal:** A mechanism to explicitly reject unsupported inputs or configurations by name, preventing silent fallbacks.

Sources:
- `common/opt_core/opt_core/kernels/fpf_trimul_v4/README.md`
- `common/opt_core/opt_core/kernels/trimul_esm_shapes/kernels.py`
- `common/opt_core/opt_core/kernels/fpf_trimul_v4/DESIGN.md`
- `common/opt_core/opt_core/kernels/trimul/native/pkg/v5/README.md`
- `common/opt_core/opt_core/kernels/trimul/native/DESIGN.md`
- `common/opt_core/opt_core/kernels/trimul/native/__init__.py`
- `common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z64_h128.cu`
- `common/opt_core/opt_core/kernels/trimul_xla/pkg/v1/README.md`
- `common/opt_core/opt_core/kernels/fpf_trimul_rows/kernels.py`
- `common/opt_core/opt_core/kernels/fpf_trimul_v4/generic.py`
- `common/opt_core/opt_core/kernels/trimul/native/pkg/v5/csrc/tmn90_z128_h256.cu`

---

