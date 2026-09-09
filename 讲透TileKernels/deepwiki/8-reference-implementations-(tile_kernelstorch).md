> 来源: [https://deepwiki.com/deepseek-ai/TileKernels/8-reference-implementations-%28tile_kernelstorch%29](https://deepwiki.com/deepseek-ai/TileKernels/8-reference-implementations-%28tile_kernelstorch%29)
> DeepWiki deepseek-ai/TileKernels

# Reference Implementations (tile_kernels/torch)

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1)
 - [tile_kernels/__init__.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/__init__.py)
 
  The `tile_kernels/torch/` sub-package provides PyTorch-native reference implementations for the high-performance kernels defined in TileLang. These implementations serve as the "ground truth" for numerical correctness during development and testing. By implementing the same mathematical logic using standard PyTorch operators, the library ensures that optimized TileLang kernels produce results within acceptable floating-point tolerance of their Python-based counterparts.

 
## Purpose and Role in Lifecycle

 The reference implementations are critical for the library's stability and development velocity. Their primary roles include:

 
 - **Correctness Validation**: During `pytest` execution, the reference implementations generate the expected output tensors against which the TileLang kernel outputs are compared [README.md41-48](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L41-L48)
 - **Mathematical Specification**: They serve as readable, executable documentation of the algorithms implemented in low-level CUDA/TileLang code.
 - **Triton/PyTorch Baseline**: They provide a performance baseline to quantify the speedup achieved by the optimized TileLang kernels.
 
 
### Reference Implementation Import Map

 The `tile_kernels/torch/` package is structured to mirror the optimized kernel families.

 
| Kernel Family | Reference File | Key Functions |
|---|---|---|
| Quantization | tile_kernels/torch/cast.py | per_token_cast, per_block_cast, per_channel_cast |
| Special Formats | tile_kernels/torch/cast_e5m6.py | per_token_cast_to_e5m6, cast_back_e5m6 |
| Engram Gating | tile_kernels/torch/engram.py | engram_gate_fwd, engram_gate_bwd, engram_hash |
| mHC | tile_kernels/torch/mhc.py | sinkhorn_torch, mhc_pre_torch, mhc_post_torch |
| MoE Routing | tile_kernels/torch/moe.py | topk_gate_torch, group_count_torch |
| MoE Dispatch | tile_kernels/torch/expand_to_fused.py | expand_to_fused_torch |
| MoE Reduction | tile_kernels/torch/reduce_fused.py | reduce_fused_torch |
| Fused Ops | tile_kernels/torch/swiglu.py | swiglu_forward_torch, swiglu_backward_torch |

 **Sources:** [tile_kernels/__init__.py3-13](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/__init__.py#L3-L13) [README.md58-68](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L58-L68)

 
---

 
## Data Flow and Entity Mapping

 The reference implementations bridge the gap between abstract mathematical operations and the specific memory layouts required by TileLang kernels.

 
### System Entity Mapping: Correctness Validation Flow

 The following diagram illustrates how the `tile_kernels/torch` entities interact with the testing infrastructure to validate TileLang kernels.

 
```

```

 **Sources:** [README.md41-48](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L41-L48) [tile_kernels/__init__.py11-12](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/__init__.py#L11-L12)

 
---

 
## Implementation Details by Module

 
### Quantization (cast.py & cast_e5m6.py)

 The reference implementations for quantization focus on simulating the hardware-level behavior of FP8/FP4/E5M6 formats. They use PyTorch's `clamp` and `round` operations to emulate limited dynamic range and precision.

 
 - **Scaling Factor Calculation**: Implements the logic for calculating max values across tokens or blocks.
 - **Format Simulation**: For formats like `E5M6`, which are not natively supported by all PyTorch versions, the reference code performs manual bit manipulation or high-precision simulation to ensure the TileLang kernel's bit-exactness is verified.
 
 
### Mixture of Experts (moe.py, expand_to_fused.py, reduce_fused.py)

 MoE references are essential for validating complex indexing logic:

 
 - **Top-K Selection**: Implements the routing logic, including group-based scoring and expert masking [README.md9-10](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L9-L10)
 - **Fused Dispatch**: The `expand_to_fused_torch` function replicates the scattering of tokens into expert-specific buffers, handling the mapping from `(token_idx)` to `(expert_idx, pos_in_expert)`.
 - **Fused Reduction**: Replicates the weighted summation of expert outputs back into the original token stream.
 
 
### Engram and mHC (engram.py & mhc.py)

 These modules provide standard PyTorch implementations for complex multi-step pipelines:

 
 - **Engram**: Implements the RMSNorm followed by the signed-sqrt sigmoid gate and the associated backward gradient calculations [README.md13](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L13-L13)
 - **mHC**: Implements the iterative Sinkhorn normalization using standard PyTorch loops to verify the convergence and accuracy of the optimized TileLang Sinkhorn kernel [README.md14](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L14-L14)
 
 
### Fused Activations (swiglu.py)

 Validates the fusion of the SwiGLU activation function with subsequent quantization steps. It ensures that the mathematical identity `SwiGLU(x) = (x_gate * sigmoid(x_gate)) * x_up` is maintained while also verifying the correct application of per-token or per-channel scaling factors during the fused cast.

 
---

 
## Integration in Testing

 The reference implementations are never used in production (modeling) code. They are strictly imported by the test suite. A typical test pattern follows this structure:

 
 - **Setup**: Generate random input tensors using `tile_kernels/testing/generator.py`.
 - **Reference Run**: Invoke the function from `tile_kernels.torch`.
 - **Kernel Run**: Invoke the optimized kernel from `tile_kernels.<module>`.
 - **Comparison**: Use `tile_kernels.testing.numeric.assert_equal` to compare the two outputs.
 
 
```

```

 **Sources:** [tile_kernels/__init__.py11-12](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/__init__.py#L11-L12) [README.md58-68](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L58-L68)
