> 来源: [https://deepwiki.com/deepseek-ai/TileKernels/3-engram-module](https://deepwiki.com/deepseek-ai/TileKernels/3-engram-module)
> DeepWiki deepseek-ai/TileKernels

# Engram Module

  Relevant source files 
 - [tile_kernels/engram/__init__.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/engram/__init__.py)
 - [tile_kernels/modeling/engram/__init__.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/modeling/engram/__init__.py)
 - [tile_kernels/modeling/engram/engram_gate.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/modeling/engram/engram_gate.py)
 
  The Engram module provides a high-performance implementation of the Engram gating mechanism. This subsystem is designed to perform a fused gating operation that combines RMSNorm, a dot-product interaction, and a non-linear activation (signed-square-root sigmoid) to modulate hidden states.

 The module is split into two layers:

 
 - **Low-level Kernels**: Highly optimized TileLang kernels for forward and backward passes.
 - **Modeling Layer**: A PyTorch autograd wrapper that manages memory, tensor reshaping, and gradient accumulation into high-precision buffers (`main_grad`).
 
 
### Mathematical Definition

 The Engram Gate computes the following interaction:

 $$ \text{gate} = \sigma\left(\text{signed_sqrt}\left(\frac{\text{RMSNorm}(x, w_h) \cdot \text{RMSNorm}(k, w_e)}{\sqrt{d}}\right)\right) $$ $$ \text{output} = x + \text{gate} \cdot v $$

 Where:

 
 - $\sigma$ is the Sigmoid function.
 - $\text{signed_sqrt}(a) = \text{sign}(a) \cdot \sqrt{|a|}$.
 - $d$ is the hidden dimension size.
 - $w_h$ and $w_e$ are learnable RMSNorm weights.
 
 
## Module Structure

 The following diagram illustrates how the modeling layer interfaces with the low-level TileLang kernels.

 **Engram System Architecture**

 
```

```

 **Sources:** [tile_kernels/modeling/engram/engram_gate.py6-95](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/modeling/engram/engram_gate.py#L6-L95) [tile_kernels/engram/__init__.py1-4](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/engram/__init__.py#L1-L4)

 
## Exported Kernels

 The Engram module exports four primary kernels for the gating operation and one utility kernel for hashing. These are designed to minimize global memory round-trips by fusing normalization and element-wise logic.

 
| Kernel Name | Purpose | File Reference |
|---|---|---|
| engram_gate_fwd | Fused RMSNorm + Dot Product + Gating + Addition. | tile_kernels/engram/__init__.py2 |
| engram_gate_bwd | Persistent backward kernel for gradients of $x, k, v$. | tile_kernels/engram/__init__.py2 |
| fused_weight | Element-wise product of $w_h$ and $w_e$ used in the forward pass. | tile_kernels/engram/__init__.py1 |
| grad_w_reduce | Reduces partial weight gradients into high-precision buffers. | tile_kernels/engram/__init__.py3 |
| engram_hash | Utility for specialized Engram hashing operations. | tile_kernels/engram/__init__.py4 |

 For a detailed technical breakdown of kernel implementations and tiling strategies, see **[Engram Kernels (#3.1)]**.

 
## Autograd Integration

 The `EngramGateFn` class [tile_kernels/modeling/engram/engram_gate.py6-92](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/modeling/engram/engram_gate.py#L6-L92) bridges the optimized kernels with PyTorch's autograd engine. It handles complex tensor reshaping for multi-head configurations and implements a custom gradient accumulation pattern.

 
### Key Features:

 
 - **Shape Management**: Handles inputs of shape `[*, hc_mult, hidden_size]` and ensures the output matches the input dimensionality [tile_kernels/modeling/engram/engram_gate.py37-55](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/modeling/engram/engram_gate.py#L37-L55)
 - **Gradient Accumulation**: The backward pass checks for the existence of a `.main_grad` attribute on weight tensors. If present, it accumulates gradients in-place in FP32 to maintain precision during training [tile_kernels/modeling/engram/engram_gate.py74-81](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/modeling/engram/engram_gate.py#L74-L81)
 - **Memory Efficiency**: Saves intermediate values like `rstd_x` (inverse standard deviation) and `gate_score` during the forward pass to avoid recomputation in the backward pass [tile_kernels/modeling/engram/engram_gate.py49-52](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/modeling/engram/engram_gate.py#L49-L52)
 
 For details on the autograd lifecycle and the `main_grad` pattern, see **[EngramGateFn: Autograd Integration (#3.2)]**.

 **Sources:** [tile_kernels/modeling/engram/engram_gate.py6-92](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/modeling/engram/engram_gate.py#L6-L92)

 
## Data Flow Mapping

 The following diagram maps the logical variables used in the mathematical definition to the specific tensor names used in the code implementation.

 **Natural Language to Code Entity Mapping**

 
```

```

 **Sources:** [tile_kernels/modeling/engram/engram_gate.py11-22](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/modeling/engram/engram_gate.py#L11-L22) [tile_kernels/modeling/engram/engram_gate.py44-47](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/modeling/engram/engram_gate.py#L44-L47)
