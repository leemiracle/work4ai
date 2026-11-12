> 来源: [https://deepwiki.com/deepseek-ai/TileKernels/4-manifold-hyperconnection-%28mhc%29-module](https://deepwiki.com/deepseek-ai/TileKernels/4-manifold-hyperconnection-%28mhc%29-module)
> DeepWiki deepseek-ai/TileKernels

# Manifold HyperConnection (mHC) Module

  Relevant source files 
 - [tile_kernels/mhc/__init__.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/mhc/__init__.py)
 - [tile_kernels/modeling/mhc/__init__.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/modeling/mhc/__init__.py)
 - [tile_kernels/modeling/mhc/functional.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/modeling/mhc/functional.py)
 
  The Manifold HyperConnection (mHC) module provides a high-performance implementation of multi-head residual connections. Unlike standard transformer residuals that simply sum a sublayer output back into the main stream, mHC maintains multiple "heads" of residuals and uses a learned, normalized mixing mechanism to combine them. This subsystem includes low-level TileLang kernels for Sinkhorn normalization, RMSNorm-fused GEMMs, and specialized mixing operations, all coordinated by a high-level modeling API.

 
## Architecture Overview

 The mHC pipeline is divided into three primary stages: **Pre-processing**, **Sublayer Execution** (Attention/FFN), and **Post-processing**. The system supports both a standard training path with full autograd support and an optimized inference path that fuses multiple operations into a single kernel to minimize memory bandwidth.

 
### Core Pipeline Flow

 
 - **Expansion**: A standard embedding is expanded into multiple residual heads using `expand_from_embedding` [tile_kernels/modeling/mhc/functional.py14-27](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/modeling/mhc/functional.py#L14-L27)
 - **Pre-processing (`mhc_pre`)**: Computes mixing coefficients, applies Sinkhorn normalization to ensure doubly-stochastic properties, and produces the input for the next sublayer [tile_kernels/modeling/mhc/functional.py30-105](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/modeling/mhc/functional.py#L30-L105)
 - **Head Processing (`mhc_head`)**: A specialized variant used for the final language model head [tile_kernels/modeling/mhc/functional.py108-161](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/modeling/mhc/functional.py#L108-L161)
 - **Post-processing (`mhc_post`)**: Integrates the sublayer output back into the multi-head residual stream.
 
 
### Logic to Code Mapping

 The following diagram illustrates how the conceptual mHC stages map to specific functions within the `modeling` and `ops` layers.

 "mHC Logic to Code Entity Mapping"

 
```

```

 
## mHC Modeling API

 The modeling API provides the functional interface used by the transformer layers. It abstracts the complexity of choosing between training and inference paths.

 
 - **Training Path**: When gradients are enabled, `mhc_pre` executes a sequence of discrete kernels (`mhc_pre_norm_fn` -> `mhc_pre_split_mixes` -> `sinkhorn_normalize` -> `mhc_pre_apply_mix`) to allow PyTorch to track intermediate tensors for the backward pass [tile_kernels/modeling/mhc/functional.py84-105](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/modeling/mhc/functional.py#L84-L105)
 - **Inference Path**: When `torch.is_grad_enabled()` is false, the system dispatches to `mhc_pre_big_fuse`, which executes the entire pre-processing logic in a single fused kernel to reduce global memory round-trips [tile_kernels/modeling/mhc/functional.py69-82](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/modeling/mhc/functional.py#L69-L82)
 
 For details, see [mHC Modeling API](https://deepwiki.com/deepseek-ai/TileKernels/4.2-mhc-modeling-api).

 
## mHC Kernels

 The mHC module relies on nine specialized TileLang kernels designed for high-throughput tensor manipulation.

 
| Kernel Name | Role |
|---|---|
| sinkhorn_kernel | Performs iterative doubly-stochastic normalization (fwd and bwd). |
| norm_fn_kernel | Fuses RMSNorm with a Linear GEMM to generate raw mix values. |
| pre_big_fuse_kernel | The inference-only "super kernel" combining norm, mix, and Sinkhorn. |
| pre_split_mixes_kernel | Splits the raw GEMM output into pre, post, and combination mixes. |
| multilayer_recompute_kernel | Specialized for memory-efficient training across multiple layers. |

 The pipeline frequently uses a `mhc_mult` value of 4, representing the number of hyper-connection heads [tile_kernels/modeling/mhc/functional.py22-38](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/modeling/mhc/functional.py#L22-L38)

 
### Kernel Interaction Diagram

 This diagram shows how data flows through the low-level kernels during a standard `mhc_pre` forward pass.

 "mHC Kernel Execution Pipeline"

 
```

```

 For details, see [mHC Kernels](https://deepwiki.com/deepseek-ai/TileKernels/4.1-mhc-kernels).

 
## Sub-Pages

 
 - **[mHC Kernels](https://deepwiki.com/deepseek-ai/TileKernels/4.1-mhc-kernels)**: Reference for the nine TileLang kernels, including Sinkhorn iterations and fused GEMM logic.
 - **[mHC Modeling API](https://deepwiki.com/deepseek-ai/TileKernels/4.2-mhc-modeling-api)**: Documentation for `functional.py` and the `ops/` autograd wrappers that bridge Python and TileLang.
 
 
---

 **Sources:**

 
 - [tile_kernels/modeling/mhc/functional.py1-161](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/modeling/mhc/functional.py#L1-L161)
 - [tile_kernels/modeling/mhc/__init__.py1-2](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/modeling/mhc/__init__.py#L1-L2)
