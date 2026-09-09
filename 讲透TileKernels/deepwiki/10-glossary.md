> 来源: [https://deepwiki.com/deepseek-ai/TileKernels/10-glossary](https://deepwiki.com/deepseek-ai/TileKernels/10-glossary)
> DeepWiki deepseek-ai/TileKernels

# Glossary

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1)
 - [pyproject.toml](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/pyproject.toml)
 - [tile_kernels/config.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/config.py)
 - [tile_kernels/engram/engram_gate_kernel.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/engram/engram_gate_kernel.py)
 - [tile_kernels/mhc/sinkhorn_kernel.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/mhc/sinkhorn_kernel.py)
 - [tile_kernels/modeling/mhc/functional.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/modeling/mhc/functional.py)
 - [tile_kernels/moe/scoring.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/moe/scoring.py)
 - [tile_kernels/quant/common.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/common.py)
 
  This page provides definitions for codebase-specific terms, abbreviations, and domain concepts used throughout the **TileKernels** repository. It serves as a technical reference for engineers to understand the mapping between mathematical concepts and their implementation in code.

 
## Core Concepts

 
### TileLang

 The domain-specific language (DSL) used to author all kernels in this repository. It allows writing GPU kernels in Python that are compiled into high-performance CUDA/C++ code [README.md1-5](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L1-L5)

 
### Persistent Blocks

 A scheduling pattern where the number of thread blocks is decoupled from the total workload size. Instead of launching one block per data tile, a fixed number of blocks (usually proportional to the number of SMs) is launched. Each block contains a loop that fetches the next available work item [tile_kernels/engram/engram_gate_kernel.py86-90](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/engram/engram_gate_kernel.py#L86-L90)

 
 - **Implementation:** See `num_persistent_blocks` calculation in `get_engram_gate_fwd_kernel` [tile_kernels/engram/engram_gate_kernel.py41-49](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/engram/engram_gate_kernel.py#L41-L49)
 
 
### SM (Streaming Multiprocessor)

 The hardware unit on NVIDIA GPUs. TileKernels queries the number of SMs and shared memory per SM to optimize occupancy [tile_kernels/config.py7-30](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/config.py#L7-L30)

 
---

 
## Engram Subsystem

 The Engram module implements a gated residual connection mechanism.

 
| Term | Definition | Code Entity |
|---|---|---|
| Engram Gate | A fused operation combining RMSNorm, a signed-sqrt sigmoid gate, and element-wise multiplication README.md13 | engram_gate_fwd tile_kernels/engram/engram_gate_kernel.py59 |
| hc_mult | Hyper-connection multiplier, defining the number of residual heads (typically 4) tile_kernels/engram/engram_gate_kernel.py26 | hc_mult |
| Weight Fused | A pre-computed product of weights used in the gating calculation to reduce memory loads tile_kernels/engram/engram_gate_kernel.py63 | weight_fused |

 **Data Flow: Engram Forward Kernel** The diagram below illustrates how the persistent block loop processes tokens across multiple residual heads.

 
```

```

 Sources: [tile_kernels/engram/engram_gate_kernel.py59-152](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/engram/engram_gate_kernel.py#L59-L152)

 
---

 
## Manifold HyperConnection (mHC)

 A subsystem for complex multi-head residual mixing.

 
 - **Sinkhorn Normalization:** An iterative algorithm to produce doubly-stochastic matrices (rows and columns sum to 1) [tile_kernels/mhc/sinkhorn_kernel.py11-16](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/mhc/sinkhorn_kernel.py#L11-L16)
 - **Big Fuse:** An inference-optimized kernel that fuses multiple mHC steps (norm, split, mix) into a single GPU launch to minimize global memory round-trips [tile_kernels/modeling/mhc/functional.py70-82](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/modeling/mhc/functional.py#L70-L82)
 - **n_splits:** A parameter for split-K GEMM decomposition, used to increase parallelism when the batch size is small but the hidden dimension is large [tile_kernels/modeling/mhc/functional.py63-64](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/modeling/mhc/functional.py#L63-L64)
 
 **Entity Mapping: mHC Pipeline**

 
```

```

 Sources: [tile_kernels/modeling/mhc/functional.py30-105](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/modeling/mhc/functional.py#L30-L105) [tile_kernels/mhc/sinkhorn_kernel.py20-58](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/mhc/sinkhorn_kernel.py#L20-L58)

 
---

 
## Quantization and Casting

 TileKernels supports high-performance casting between standard floating point (BF16/FP32) and low-precision formats.

 
### Scaling Factor (SF)

 A value used to scale tensors during quantization. TileKernels supports multiple granularities:

 
 - **Per-token:** One SF per row.
 - **Per-block:** SFs for tiles of size `(M, N)`.
 - **Per-channel:** One SF per column.
 
 
### Layout Formats

 
 - **TMA Aligned Col-Major:** A specific memory layout for scaling factors designed to be compatible with NVIDIA's Tensor Memory Accelerator (TMA) [tile_kernels/quant/common.py24](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/common.py#L24-L24)
 - **UE8M0:** A packed format for scaling factors where 4 values are packed into a 32-bit integer [tile_kernels/quant/common.py25](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/common.py#L25-L25)
 - **E5M6 / E4M3 / E2M1:** Specific exponent-mantissa configurations for 8-bit and 4-bit floating point formats [tile_kernels/quant/common.py99-104](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/common.py#L99-L104)
 
 
### Code Definitions

 
 - **BaseCastConfig:** Dataclass defining the target dtype and SF block size [tile_kernels/quant/common.py21-38](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/common.py#L21-L38)
 - **get_sf_and_inv:** A TileLang macro that calculates the scaling factor and its inverse, optionally rounding to the nearest power of two [tile_kernels/quant/common.py196-210](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/common.py#L196-L210)
 
 
---

 
## Mixture of Experts (MoE)

 
### Scoring Functions

 The method used to calculate expert affinity scores.

 
 - **SIGMOID:** [tile_kernels/moe/scoring.py6](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/moe/scoring.py#L6-L6)
 - **SQRTSOFTPLUS:** [tile_kernels/moe/scoring.py7](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/moe/scoring.py#L7-L7)
 - **SOFTMAX:** [tile_kernels/moe/scoring.py8](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/moe/scoring.py#L8-L8)
 
 
### Routing Terms

 
 - **Top-K:** Selecting the `K` experts with the highest scores for each token.
 - **Fused Mapping:** A kernel that constructs the mapping between tokens and their assigned expert buffers in a single pass [README.md10](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L10-L10)
 - **Group Counting:** Calculating how many tokens are assigned to each expert to manage buffer offsets [README.md10](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L10-L10)
 
 
---

 
## Utility Functions

 
| Function | Purpose | Location |
|---|---|---|
| ceil_div(a, b) | Performs (a + b - 1) // b. | tile_kernels/utils.py |
| align(n, m) | Rounds n up to the nearest multiple of m. | tile_kernels/utils.py |
| get_num_sms() | Returns the number of SMs available for kernel grid sizing. | tile_kernels/config.py19-24 |
| T.alloc_fragment | Allocates registers for a tile of data in TileLang. | tile_kernels/mhc/sinkhorn_kernel.py25 |
| T.async_copy | Initiates an asynchronous memory copy from Global to Shared memory. | tile_kernels/engram/engram_gate_kernel.py93 |

 Sources: [tile_kernels/utils.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/utils.py) [tile_kernels/config.py19-24](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/config.py#L19-L24) [tile_kernels/engram/engram_gate_kernel.py93](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/engram/engram_gate_kernel.py#L93-L93) [tile_kernels/mhc/sinkhorn_kernel.py25](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/mhc/sinkhorn_kernel.py#L25-L25)
