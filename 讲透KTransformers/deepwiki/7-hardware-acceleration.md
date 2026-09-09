> 来源: [https://deepwiki.com/kvcache-ai/ktransformers/7-hardware-acceleration](https://deepwiki.com/kvcache-ai/ktransformers/7-hardware-acceleration)
> DeepWiki kvcache-ai/ktransformers | Last indexed: 30 April 2026 (02be2b

# Hardware Acceleration

  Relevant source files 
 - [doc/assets/amx.png](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/assets/amx.png)
 - [doc/assets/amx_avx.png](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/assets/amx_avx.png)
 - [doc/assets/amx_intro.png](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/assets/amx_intro.png)
 - [doc/assets/onednn_1.png](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/assets/onednn_1.png)
 - [doc/en/AMX.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/AMX.md?plain=1)
 - [kt-kernel/operators/amx/awq-moe.hpp](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/operators/amx/awq-moe.hpp)
 - [kt-kernel/operators/amx/fp8-moe.hpp](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/operators/amx/fp8-moe.hpp)
 - [kt-kernel/operators/amx/moe.hpp](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/operators/amx/moe.hpp)
 - [kt-kernel/operators/amx/moe_base.hpp](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/operators/amx/moe_base.hpp)
 
  
## Purpose and Scope

 This page documents CPU hardware acceleration technologies used in KTransformers for efficient inference of large MoE models. It covers the Intel AMX instruction set, custom kernel implementations, AVX/AVX512 support, and the llamafile backend integration. For GPU acceleration and attention mechanisms, see [SGLang Integration](https://deepwiki.com/kvcache-ai/ktransformers/4.3-sglang-integration). For overall CPU-GPU heterogeneous computing architecture, see [CPU-GPU Heterogeneous Computing](https://deepwiki.com/kvcache-ai/ktransformers/3.2-cpu-gpu-heterogeneous-computing).

 
## CPU Acceleration Technologies Overview

 KTransformers leverages specialized CPU instruction sets to accelerate matrix multiplication operations required for MoE expert computation. The framework uses a multi-variant build system that includes progressive CPU variants, with automatic runtime selection based on detected hardware features.

 
### Multi-Variant Architecture

 
```

```

 **CPU Variant Capabilities:**

 
| Variant | CPU Requirements | Data Types | Performance Tier | Example CPUs |
|---|---|---|---|---|
| AMX | AMX + AVX512 (F/BW/VNNI/VBMI/BF16) | INT4, INT8, BF16, FP8 | ⚡⚡⚡ Best | Intel Sapphire Rapids (2023+) |
| AVX512_BF16 | AVX512F/BW/VNNI/VBMI/BF16 | BF16, RAWINT4 | ⚡⚡⚡ Excellent | Ice Lake server, Zen 4+ (2021+) |
| AVX512_VBMI | AVX512F/BW/VNNI/VBMI | INT4, INT8 | ⚡⚡ Great | Ice Lake client (2019+) |
| AVX512_VNNI | AVX512F/BW/VNNI | INT8, FP32 | ⚡⚡ Great | Cascade Lake+ (2019+) |
| AVX512_BASE | AVX512F/BW | INT4, INT8, FP32 | ⚡⚡ Good | Skylake-X+ (2017+) |
| AVX2 | AVX2 | BF16, FP8, GPTQ_INT4 | ⚡ Good | Haswell+ (2013+), AMD Zen+ |

 Sources: [doc/en/AMX.md34-66](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/AMX.md?plain=1#L34-L66) [kt-kernel/operators/amx/moe_base.hpp35-37](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/operators/amx/moe_base.hpp#L35-L37)

 
## Intel AMX Optimization

 Intel Advanced Matrix Extensions (AMX) provide hardware acceleration for matrix operations through specialized tile registers and compute instructions. AMX can theoretically provide 8 times the performance of AVX-512 by performing matrix multiply-accumulate operations at the register level [doc/en/AMX.md64-66](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/AMX.md?plain=1#L64-L66)

 
### Tile Register Architecture

 
```

```

 **Key AMX Instructions:**

 
| Instruction Category | Instructions | Description |
|---|---|---|
| Configuration | LDTILECFG, STTILECFG, TILERELEASE, TILEZERO | Configure/reset tile registers and metadata |
| Load/Store | TILELOADD, TILELOADDT1, TILESTORED | Transfer data between memory and tiles |
| INT8 Compute | TDPBSSD, TDPBUSD, TDPBUUD, TDPBSUD | INT8 matrix multiply-accumulate |
| BF16 Compute | TDPBF16PS | BF16 matrix multiply-accumulate |

 For implementation details, see [Intel AMX Optimization](https://deepwiki.com/kvcache-ai/ktransformers/7.1-intel-amx-optimization).

 Sources: [doc/en/AMX.md34-66](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/AMX.md?plain=1#L34-L66) [kt-kernel/operators/amx/moe_base.hpp15-17](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/operators/amx/moe_base.hpp#L15-L17)

 
## AMX Kernel Implementation

 KTransformers implements custom AMX kernels optimized for MoE inference with cache-aware memory layouts and multi-level tiling strategies.

 
### AMX_MOE_BASE and CRTP Pattern

 The AMX backend uses the Curiously Recurring Template Pattern (CRTP) to implement specialized MoE operators. The `AMX_MOE_BASE` class provides the common infrastructure for memory allocation and forward pass logic [kt-kernel/operators/amx/moe_base.hpp39-85](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/operators/amx/moe_base.hpp#L39-L85)

 
```

```

 **Key Implementation Features:**

 
 - **Tiling-aware Memory Layout**: Expert weight matrices are pre-rearranged into Tile-friendly sub-matrices whose shapes precisely match AMX Tile register dimensions [doc/en/AMX.md78-85](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/AMX.md?plain=1#L78-L85)
 - **Expert Mapping**: Uses a `physical_to_logical_map` to handle expert distribution across NUMA nodes and CPU cores [kt-kernel/operators/amx/fp8-moe.hpp175-177](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/operators/amx/fp8-moe.hpp#L175-L177)
 - **Quantization Support**: Specialized implementations for AWQ INT4 [kt-kernel/operators/amx/awq-moe.hpp29-30](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/operators/amx/awq-moe.hpp#L29-L30) and Native FP8 [kt-kernel/operators/amx/fp8-moe.hpp28-29](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/operators/amx/fp8-moe.hpp#L28-L29)
 
 For details, see [AMX Kernel Implementation](https://deepwiki.com/kvcache-ai/ktransformers/7.2-amx-kernel-implementation).

 
## AVX/AVX512 Support

 KTransformers provides support for CPUs without AMX, including older Intel and AMD processors, through AVX2 and AVX512 fallback paths.

 **Key Features:**

 
 - **Runtime Kernel Selection**: The system detects CPU flags like `AVX512_BF16` or `AVX512_VNNI` to select the most efficient available kernel [doc/en/AMX.md74-77](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/AMX.md?plain=1#L74-L77)
 - **BF16 Support**: Native BF16 computation is supported on CPUs with `AVX512_BF16` instructions [doc/en/AMX.md47-48](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/AMX.md?plain=1#L47-L48)
 - **INT8/INT4 fallback**: Provides optimized kernels for quantized weights even on consumer-grade hardware [doc/en/AMX.md17-19](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/AMX.md?plain=1#L17-L19)
 
 For details, see [AVX/AVX512 Support](https://deepwiki.com/kvcache-ai/ktransformers/7.3-avxavx512-support).

 
## llamafile Backend

 The llamafile backend serves as a high-compatibility layer, particularly useful for GGUF formatted models. It integrates `iqk_mul_mat` operations and `sgemm` implementations.

 **Integration Details:**

 
 - **GGUF Support**: Allows loading and executing models in GGUF format [doc/en/AMX.md24-25](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/AMX.md?plain=1#L24-L25)
 - **AMX Synergy**: While the llamafile backend was the initial CPU path, KTransformers v0.3 introduced native AMX kernels to overcome performance bottlenecks in the llamafile implementation [doc/en/AMX.md74-77](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/AMX.md?plain=1#L74-L77)
 
 For details, see [llamafile Backend](https://deepwiki.com/kvcache-ai/ktransformers/7.4-llamafile-backend).

 
## AMD, Intel GPU, and Alternative Hardware Support

 KTransformers is expanding its hardware support beyond Intel CPUs to include AMD processors and alternative accelerators.

 
 - **AMD Support**: Leverages AVX2 and AVX512 (on Zen 4+) for CPU acceleration. Performance is sensitive to memory frequency and channel configuration [doc/en/AMX.md8-10](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/AMX.md?plain=1#L8-L10)
 - **Intel GPU (XPU)**: Support for Intel Arc and Data Center GPUs.
 - **Heterogeneous Scaling**: The framework is designed to hit "performance sweet spots" for both server-grade Xeon workstations and consumer-grade PCs with RTX 4090 GPUs [doc/en/AMX.md4-10](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/AMX.md?plain=1#L4-L10)
 
 For details, see [AMD, Intel GPU, and Alternative Hardware Support](https://deepwiki.com/kvcache-ai/ktransformers/7.5-amd-intel-gpu-and-alternative-hardware-support).

 Sources: [doc/en/AMX.md1-19](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/AMX.md?plain=1#L1-L19) [kt-kernel/operators/amx/moe_base.hpp39-85](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/operators/amx/moe_base.hpp#L39-L85) [kt-kernel/operators/amx/awq-moe.hpp29-30](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/operators/amx/awq-moe.hpp#L29-L30) [kt-kernel/operators/amx/fp8-moe.hpp28-29](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/operators/amx/fp8-moe.hpp#L28-L29)
