> 来源: [https://deepwiki.com/deepseek-ai/TileKernels/6-quantization-module](https://deepwiki.com/deepseek-ai/TileKernels/6-quantization-module)
> DeepWiki deepseek-ai/TileKernels

# Quantization Module

  Relevant source files 
 - [tile_kernels/quant/__init__.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/__init__.py)
 - [tile_kernels/quant/common.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/common.py)
 
  The Quantization Module provides a comprehensive suite of high-performance kernels for converting between high-precision formats (BF16, FP32) and low-precision formats (FP8, FP4, E5M6). It supports various quantization granularities and scaling-factor (SF) layouts required for modern LLM inference and training, particularly targeting NVIDIA Hopper (SM90) and Blackwell architectures.

 
### Supported Formats and Granularities

 The module supports three primary low-precision formats defined in `BaseCastConfig`:

 
 - **FP8 (E4M3):** Standard `torch.float8_e4m3fn` [tile_kernels/quant/common.py22](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/common.py#L22-L22)
 - **FP4 (E2M1):** Packed into `torch.int8` containers [tile_kernels/quant/common.py29](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/common.py#L29-L29)
 - **E5M6:** A custom 11-bit format used for specific weight/activation storage [tile_kernels/quant/common.py101](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/common.py#L101-L101)
 
 Quantization can be applied at different granularities:

 
 - **Per-Token:** Scaling factors are calculated for each row (token) [tile_kernels/quant/__init__.py8](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/__init__.py#L8-L8)
 - **Per-Block:** Scaling factors are calculated for 2D blocks (e.g., 1x128 or 128x128) [tile_kernels/quant/__init__.py9](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/__init__.py#L9-L9)
 - **Per-Channel:** Scaling factors are calculated for each column (channel) [tile_kernels/quant/__init__.py2-4](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/__init__.py#L2-L4)
 
 
### Scaling Factor (SF) Management

 The module handles complex scaling factor layouts to satisfy hardware requirements like Tensor Memory Accelerator (TMA) alignment.

 
 - **Row-Major:** Standard layout where `sf_shape` is `(num_block_m, num_block_k)` [tile_kernels/quant/common.py138](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/common.py#L138-L138)
 - **TMA-Aligned Col-Major:** Transposed layout optimized for TMA loads, requiring 16-byte alignment [tile_kernels/quant/common.py153-154](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/common.py#L153-L154)
 - **Packed UE8M0:** A specialized format where four factors are packed into a single `int32` for specific hardware acceleration paths [tile_kernels/quant/common.py135-137](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/common.py#L135-L137)
 
 
### Code Entity Mapping

 The following diagram maps the logical quantization configurations to their implementation structures and helper functions.

 **Quantization Configuration Flow**

 
```

```

 Sources: [tile_kernels/quant/common.py20-61](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/common.py#L20-L61) [tile_kernels/quant/common.py62-113](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/common.py#L62-L113) [tile_kernels/quant/common.py141-165](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/common.py#L141-L165) [tile_kernels/quant/common.py168-194](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/common.py#L168-L194)

 
### Sub-Modules

 
#### [Cast and Dequantization Kernels](https://deepwiki.com/deepseek-ai/TileKernels/6.1-cast-and-dequantization-kernels)

 This sub-module contains the core logic for converting tensors between formats. It includes forward cast kernels for per-token, per-block, and per-channel granularities, as well as dequantization kernels (`cast_back`) for returning to BF16. It also handles specialized "lossless" block casting.

 For details, see [Cast and Dequantization Kernels](https://deepwiki.com/deepseek-ai/TileKernels/6.1-cast-and-dequantization-kernels).

 
#### [Fused SwiGLU + Quantization Kernels](https://deepwiki.com/deepseek-ai/TileKernels/6.2-fused-swiglu-+-quantization-kernels)

 To minimize memory bandwidth bottlenecks, the module provides kernels that fuse the SwiGLU activation function with the subsequent quantization step. This prevents writing high-precision intermediate activations back to VRAM before they are quantized for the next layer.

 For details, see [Fused SwiGLU + Quantization Kernels](https://deepwiki.com/deepseek-ai/TileKernels/6.2-fused-swiglu-+-quantization-kernels).

 
### Quantization Pipeline Overview

 The following diagram illustrates how data flows from high-precision input through the quantization kernels to produce a `QuantTensor` (a tuple of the quantized data and its scaling factors).

 **Quantization Execution Pipeline**

 
```

```

 Sources: [tile_kernels/quant/common.py168-194](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/common.py#L168-L194) [tile_kernels/quant/common.py196-205](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/common.py#L196-L205) [tile_kernels/quant/types.py9](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/types.py#L9-L9)

 
### Key Files

 
 - `tile_kernels/quant/common.py`: Contains the base dataclasses (`BaseCastConfig`) and scaling factor allocation logic [tile_kernels/quant/common.py1-210](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/common.py#L1-L210)
 - `tile_kernels/quant/__init__.py`: Exports the primary API for all quantization operations [tile_kernels/quant/__init__.py1-11](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/__init__.py#L1-L11)
 - `tile_kernels/quant/types.py`: Defines the `QuantTensor` type alias [tile_kernels/quant/types.py1-10](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/types.py#L1-L10)
 
 Sources: [tile_kernels/quant/common.py1-210](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/common.py#L1-L210) [tile_kernels/quant/__init__.py1-11](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/__init__.py#L1-L11) [tile_kernels/quant/types.py1-10](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/quant/types.py#L1-L10)
