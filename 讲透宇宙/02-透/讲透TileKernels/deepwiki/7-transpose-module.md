> 来源: [https://deepwiki.com/deepseek-ai/TileKernels/7-transpose-module](https://deepwiki.com/deepseek-ai/TileKernels/7-transpose-module)
> DeepWiki deepseek-ai/TileKernels

# Transpose Module

  Relevant source files 
 - [tests/transpose/test_transpose.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tests/transpose/test_transpose.py)
 
  The Transpose Module provides optimized TileLang kernels for performing 2D and 3D (batched) tensor transpositions. These operations are fundamental building blocks in Transformer architectures, particularly for preparing data for attention mechanisms and shuffling tokens in Mixture of Experts (MoE) layers.

 
## Overview

 The module provides two primary interfaces:

 
 - **`transpose()`**: Transposes a 2D tensor of shape `[M, N]` to `[N, M]`.
 - **`batched_transpose()`**: Transposes a 3D tensor of shape `[B, M, N]` to `[B, N, M]`, where the batch dimension `B` remains fixed.
 
 These kernels are designed to handle both standard data types (e.g., `torch.bfloat16`, `torch.float32`) and low-precision formats like `torch.float8_e4m3fn`, which are critical for high-performance inference and training [tests/transpose/test_transpose.py51-62](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tests/transpose/test_transpose.py#L51-L62)

 
### Use Cases

 
 - **Attention Mechanisms**: Transposing head dimensions for query, key, and value projections.
 - **MoE Shuffle**: Reorganizing expert-parallel buffers where tokens and hidden dimensions need to be swapped within a batch of experts [tests/transpose/test_transpose.py35-43](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tests/transpose/test_transpose.py#L35-L43)
 - **Quantization Prep**: Preparing tensors for per-channel quantization kernels that may require specific memory layouts.
 
 Sources: [tests/transpose/test_transpose.py69-109](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tests/transpose/test_transpose.py#L69-L109)

 
## Kernel Implementation and Data Flow

 The transposition logic is implemented as a batched kernel where the transformation is applied to the last two dimensions. The kernel utilizes TileLang's tiling capabilities to move blocks of data through shared memory to ensure coalesced global memory access.

 
### Data Flow Diagram

 The following diagram illustrates the transformation from an input tensor to a transposed output tensor using the `batched_transpose` operation.

 "Batched Transpose Data Flow"

 
```

```

 Sources: [tests/transpose/test_transpose.py97-98](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tests/transpose/test_transpose.py#L97-L98)

 
## API Reference

 The module is accessed via the `tile_kernels.transpose` namespace.

 
### `transpose(x)`

 Transposes a 2D tensor.

 
 - **Input**: `x` (torch.Tensor) - A 2D tensor of shape `[M, N]`.
 - **Output**: A 2D tensor of shape `[N, M]`.
 - **Behavior**: The implementation handles non-contiguous inputs by effectively performing a copy-and-transpose into a new contiguous allocation [tests/transpose/test_transpose.py14-20](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tests/transpose/test_transpose.py#L14-L20)
 
 
### `batched_transpose(x)`

 Transposes the inner dimensions of a 3D tensor.

 
 - **Input**: `x` (torch.Tensor) - A 3D tensor of shape `[B, M, N]`.
 - **Output**: A 3D tensor of shape `[B, N, M]`.
 - **Batching**: The first dimension is treated as the batch dimension and is typically mapped to the `z` dimension of the CUDA grid [tests/transpose/test_transpose.py96-98](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tests/transpose/test_transpose.py#L96-L98)
 
 Sources: [tests/transpose/test_transpose.py69-109](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tests/transpose/test_transpose.py#L69-L109)

 
## Testing and Verification

 The Transpose module includes comprehensive tests to ensure correctness across various shapes and data types.

 
### Test Coverage Matrix

 
| Feature | Supported Types | Shapes Tested |
|---|---|---|
| Transpose (2D) | bf16, fp8_e4m3 | generate_num_tokens x generate_hidden_sizes |
| Batched Transpose (3D) | bf16, fp8_e4m3, fp32 | num_experts (8, 32) x tokens x hidden |

 Sources: [tests/transpose/test_transpose.py46-62](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tests/transpose/test_transpose.py#L46-L62)

 
### Verification Logic

 Correctness is verified by comparing the kernel output against PyTorch's native `T.contiguous()` or `torch.transpose(x, 1, 2).contiguous()` operations [tests/transpose/test_transpose.py72-74](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tests/transpose/test_transpose.py#L72-L74) [tests/transpose/test_transpose.py98-100](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tests/transpose/test_transpose.py#L98-L100)

 
### Performance Benchmarking

 The test suite includes `@pytest.mark.benchmark` fixtures that measure:

 
 - **Latency**: Execution time in microseconds (`t_us`) [tests/transpose/test_transpose.py83](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tests/transpose/test_transpose.py#L83-L83)
 - **Throughput**: Bandwidth in GB/s, calculated using the total bytes moved (input + output) [tests/transpose/test_transpose.py90](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tests/transpose/test_transpose.py#L90-L90)
 
 "Verification and Benchmarking Flow"

 
```

```

 Sources: [tests/transpose/test_transpose.py79-91](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tests/transpose/test_transpose.py#L79-L91)
