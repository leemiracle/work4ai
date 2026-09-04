> 来源: [https://deepwiki.com/sgl-project/sglang/9-quantization-system](https://deepwiki.com/sgl-project/sglang/9-quantization-system)
> DeepWiki sgl-project/sglang | Last indexed: 27 Aug 2026 (94183a)

# Quantization System

  Relevant source files 
 - [python/sglang/kernels/ops/moe/ep_moe_kernels.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/ops/moe/ep_moe_kernels.py)
 - [python/sglang/srt/configs/load_config.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/configs/load_config.py)
 - [python/sglang/srt/layers/linear.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/linear.py)
 - [python/sglang/srt/layers/moe/ep_moe/layer.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/ep_moe/layer.py)
 - [python/sglang/srt/layers/moe/flashinfer_trtllm_moe.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/flashinfer_trtllm_moe.py)
 - [python/sglang/srt/layers/moe/fused_moe_triton/layer.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/fused_moe_triton/layer.py)
 - [python/sglang/srt/layers/moe/moe_runner/deep_gemm.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/moe_runner/deep_gemm.py)
 - [python/sglang/srt/layers/moe/moe_runner/flashinfer_cutedsl.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/moe_runner/flashinfer_cutedsl.py)
 - [python/sglang/srt/layers/moe/moe_runner/flashinfer_trtllm.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/moe_runner/flashinfer_trtllm.py)
 - [python/sglang/srt/layers/moe/moe_runner/runner.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/moe_runner/runner.py)
 - [python/sglang/srt/layers/moe/token_dispatcher/__init__.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/token_dispatcher/__init__.py)
 - [python/sglang/srt/layers/moe/token_dispatcher/base.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/token_dispatcher/base.py)
 - [python/sglang/srt/layers/moe/token_dispatcher/deepep_v2.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/token_dispatcher/deepep_v2.py)
 - [python/sglang/srt/layers/moe/utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/utils.py)
 - [python/sglang/srt/layers/quantization/compressed_tensors/schemes/compressed_tensors_w8a8_fp8_moe.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/compressed_tensors/schemes/compressed_tensors_w8a8_fp8_moe.py)
 - [python/sglang/srt/layers/quantization/dequantization.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/dequantization.py)
 - [python/sglang/srt/layers/quantization/fp8.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/fp8.py)
 - [python/sglang/srt/layers/quantization/fp8_utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/fp8_utils.py)
 - [python/sglang/srt/layers/quantization/modelopt_quant.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/modelopt_quant.py)
 - [python/sglang/srt/layers/quantization/quark/quark.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/quark/quark.py)
 - [python/sglang/srt/layers/quantization/quark/schemes/quark_w4a4_mxfp4.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/quark/schemes/quark_w4a4_mxfp4.py)
 - [python/sglang/srt/layers/quantization/quark/schemes/quark_w4a4_mxfp4_moe.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/quark/schemes/quark_w4a4_mxfp4_moe.py)
 - [python/sglang/srt/layers/quantization/quark/utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/quark/utils.py)
 - [python/sglang/srt/layers/quantization/unquant.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/unquant.py)
 - [python/sglang/srt/layers/quantization/utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/utils.py)
 - [python/sglang/srt/model_loader/loader.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_loader/loader.py)
 - [python/sglang/srt/model_loader/remote_instance_weight_loader_utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_loader/remote_instance_weight_loader_utils.py)
 - [python/sglang/srt/model_loader/utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_loader/utils.py)
 - [python/sglang/srt/model_loader/weight_utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_loader/weight_utils.py)
 - [python/sglang/srt/models/deepseek_nextn.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/deepseek_nextn.py)
 - [python/sglang/srt/models/deepseek_v2.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/deepseek_v2.py)
 - [test/registered/quant/test_is_layer_skipped.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/quant/test_is_layer_skipped.py)
 - [test/registered/quant/test_quark_mxfp4.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/quant/test_quark_mxfp4.py)
 - [test/registered/unit/model_loader/test_prefetch_checkpoints.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/model_loader/test_prefetch_checkpoints.py)
 - [test/registered/xpu/test_moe_ld_padding.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/xpu/test_moe_ld_padding.py)
 
  This document provides a high-level overview of the SGLang quantization system. Quantization in SGLang aims to reduce memory footprints and computational cost for large language models (LLMs) and vision-language models (VLMs) by supporting various weight and activation quantization techniques. The system is designed to be flexible, modular, and extensible, allowing configurable quantization schemes across multiple hardware platforms including NVIDIA CUDA GPUs, AMD ROCm GPUs, Huawei NPUs, and Intel CPUs with AMX.

 The quantization system covers method configuration and registry, multiple quantization formats and kernels (FP8, ModelOpt FP4, MXFP4, INT8 and others), integration with linear and MoE layers, and hardware-specific kernel implementations. This page serves as a parent and roadmap to child pages that present detailed documentation and technical specifics.

 
---

 
## Quantization Configuration and Registry

 SGLang uses a **registry pattern** to map string quantization names to their corresponding configuration classes derived from `QuantizationConfig`. This registry combines base quant methods with hardware/platform-specific overrides and extension modules.

 The factory function `get_quantization_config()` reliably returns the appropriate config class based on user inputs and platform detection, enabling transparent platform dispatch (e.g., Intel AMX vs CUDA vs AMD ROCm). This registry system makes it straightforward to add new quant methods and select them at runtime. The `LoadConfig` and `ModelConfig` objects work together to resolve the specific quantization requirements during model initialization [python/sglang/srt/model_loader/loader.py167-210](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_loader/loader.py#L167-L210)

 
### High-Level Registry Map

 
```

```

 This system is implemented predominantly in `python/sglang/srt/layers/quantization/__init__.py` and `python/sglang/srt/layers/quantization/base_config.py` [python/sglang/srt/layers/quantization/base_config.py49-54](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/base_config.py#L49-L54)

 **For full details, examples, and configuration parameters, see** [Quantization Configuration and Registry](https://deepwiki.com/sgl-project/sglang/9.1-quantization-configuration-and-registry).

 
---

 
## Quantization Method Architecture

 Each quantization method encapsulates a complete lifecycle:

 
 - **Weight Creation:** Parameters are initialized for quantized storage (e.g., `BlockQuantScaleParameter`, `PerTensorScaleParameter`) via `create_weights` [python/sglang/srt/layers/quantization/fp8.py49-54](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/fp8.py#L49-L54)
 - **Checkpoint Loading:** State dicts map weights via a flexible `WeightsMapper` system, which can probe routed expert weight dtypes to determine if specific layouts (like DeepSeek V4) are used [python/sglang/srt/model_loader/weight_utils.py89-131](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_loader/weight_utils.py#L89-L131)
 - **Post-Loading Processing:** Platform-specific transformations, such as weight shuffling for ROCm AITER [python/sglang/srt/layers/quantization/fp8.py143-145](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/fp8.py#L143-L145) or AMX processing for CPUs [python/sglang/srt/layers/quantization/fp8.py26-29](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/fp8.py#L26-L29)
 - **Forward Execution:** Forward `apply()` calls dispatch optimized kernels based on quant method and hardware (e.g., `apply_fp8_linear`) [python/sglang/srt/layers/quantization/fp8.py57-68](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/fp8.py#L57-L68)
 
 
### Typical Flow Overview

 
```

```

 This core architecture is defined primarily by `QuantizeMethodBase` and its derivatives, including `LinearMethodBase` and `FusedMoEMethodBase` [python/sglang/srt/layers/quantization/base_config.py50-54](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/base_config.py#L50-L54) and used by linear and MoE layers [python/sglang/srt/layers/moe/fused_moe_triton/layer.py58-61](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/fused_moe_triton/layer.py#L58-L61)

 
---

 
## FP8 and ModelOpt Quantization

 
### FP8

 FP8 (8-bit floating point) quantization is supported with multiple backends including NVIDIA DeepGEMM, CUTLASS, Triton, and HIP-based AITER kernels. The system selects the best kernel depending on GPU architecture and platform capabilities [python/sglang/srt/layers/quantization/fp8_utils.py10-25](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/fp8_utils.py#L10-L25)

 Key features:

 
 - Supports per-token group quantization scales via `per_token_group_quant_fp8` [python/sglang/srt/layers/quantization/fp8.py18](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/fp8.py#L18-L18)
 - Block-wise scaling kernel support for DeepSeek models, including logic to requantize block scales for DeepGEMM [python/sglang/srt/layers/quantization/fp8_utils.py60-66](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/fp8_utils.py#L60-L66)
 - Integration with MoE layers for gated experts using `Fp8MoEMethod` [python/sglang/srt/layers/quantization/fp8.py65](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/fp8.py#L65-L65)
 
 
### ModelOpt Quantization

 ModelOpt quantization extends FP4 and mixed precision techniques tailored for NVIDIA hardware, supporting block-wise weight scales and specialized GEMMs.

 Features include:

 
 - NVFP4 (native FP4 data type) quantization support [python/sglang/srt/layers/quantization/modelopt_quant.py34-37](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/modelopt_quant.py#L34-L37)
 - Mixed FP4/FP8 quantization through blockscale swizzling [python/sglang/srt/layers/quantization/modelopt_quant.py62-63](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/modelopt_quant.py#L62-L63)
 - Support for fused MoE FP8/FP4 execution with FlashInfer TRTLLM kernels [python/sglang/srt/layers/moe/moe_runner/flashinfer_trtllm.py27-31](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/moe_runner/flashinfer_trtllm.py#L27-L31)
 - NVFP4 weight padding to satisfy alignment constraints via `pad_nvfp4_weight` [python/sglang/srt/layers/quantization/modelopt_quant.py172-192](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/modelopt_quant.py#L172-L192)
 
 **For details, see** [FP8 and ModelOpt Quantization](https://deepwiki.com/sgl-project/sglang/9.2-fp8-and-modelopt-quantization).

 
---

 
## FP4 and MXFP4 Quantization

 SGLang supports ultra-low-bit FP4 and Microscaling FP4 (MXFP4) quantization methods optimized for modern architectures:

 
 - **NVIDIA Blackwell (SM100):** Native hardware support for FP4 GEMMs via FlashInfer `mm_fp4` [python/sglang/srt/layers/quantization/modelopt_quant.py103-109](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/modelopt_quant.py#L103-L109)
 - **AMD Graphics (gfx95+):** Specialized AITER kernels for MXFP4 and block-fp8, including logic to force specific GEMM backends [python/sglang/srt/layers/quantization/fp8_utils.py65-81](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/fp8_utils.py#L65-L81)
 - **Microscaling:** Support for `MXFP8` (fp8_e4m3 + e8m0 block scale) and `MXFP4` through `MXFP4QuantizeUtil` [python/sglang/srt/layers/moe/utils.py237-243](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/utils.py#L237-L243) [python/sglang/srt/layers/quantization/fp8_utils.py84-85](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/fp8_utils.py#L84-L85)
 
 For technical details on these low bit-width quant modes, see [FP4 and MXFP4 Quantization](https://deepwiki.com/sgl-project/sglang/9.3-fp4-and-mxfp4-quantization).

 
---

 
## INT8 and Other Quantization Methods

 SGLang provides mature support for a range of other quantization types:

 
 - **INT8 and INT4:** Integer quantization methods, including `BlockInt8LinearMethod` and `QuarkInt4Fp8LinearMethod` [python/sglang/srt/layers/linear.py63-77](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/linear.py#L63-L77)
 - **AWQ and GPTQ:** Optimized 4-bit quantization methods integrated into the configuration registry [python/sglang/srt/layers/linear.py60-70](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/linear.py#L60-L70)
 - **Quantized KV Cache:** Efficient FP8 and FP4 KV cache implementations via `BaseKVCacheMethod` [python/sglang/srt/layers/quantization/fp8.py69](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/fp8.py#L69-L69)
 - **GGUF Support:** Weight loading and iteration for GGUF format checkpoints [python/sglang/srt/model_loader/loader.py114-116](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_loader/loader.py#L114-L116)
 
 For a comprehensive look at these methods, see [INT8 and Other Quantization Methods](https://deepwiki.com/sgl-project/sglang/9.4-int8-and-other-quantization-methods).

 
---

 
## Kernel Implementations (`sgl-kernel`)

 Performance-critical quantization kernels are implemented in the `sgl-kernel` library, providing:

 
 - **Per-token-group quantization:** Dynamic scaling for FP8 [python/sglang/kernels/ops/quantization/fp8_kernel.py18](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/ops/quantization/fp8_kernel.py#L18-L18)
 - **FP8/FP4 Scaled Matrix Multiplication:** High-performance GEMMs including `w8a8_block_fp8_matmul_deepgemm` and `fp4_gemm` [python/sglang/srt/layers/quantization/fp8_utils.py23](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/fp8_utils.py#L23-L23) [python/sglang/srt/layers/quantization/modelopt_quant.py133-141](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/modelopt_quant.py#L133-L141)
 - **MoE Fused Kernels:** Efficient top-k gating and routing (e.g., `PackTopkIds`) [python/sglang/srt/layers/moe/moe_runner/flashinfer_trtllm.py12](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/moe_runner/flashinfer_trtllm.py#L12-L12)
 
 
---

 
## Quantization System: Natural Language <-> Code Entity Mapping

 
### Quantization Registry Architecture

 
```

```

 
### Quant Method Application Flow

 
```

```

 
---

 
# Child Pages for Details

 
 - [Quantization Configuration and Registry](https://deepwiki.com/sgl-project/sglang/9.1-quantization-configuration-and-registry) — Document `QuantizationConfig` classes, `get_quantization_config` factory, and method registration.
 - [FP8 and ModelOpt Quantization](https://deepwiki.com/sgl-project/sglang/9.2-fp8-and-modelopt-quantization) — Explain FP8 quantization (E4M3), ModelOpt integration, block-wise quantization, and `DeepGEMM` wrapper.
 - [FP4 and MXFP4 Quantization](https://deepwiki.com/sgl-project/sglang/9.3-fp4-and-mxfp4-quantization) — Document FP4/MXFP4/NVFP4 quantization for Blackwell GPUs, microscaling, SM100 support, and Quark schemes.
 - [INT8 and Other Quantization Methods](https://deepwiki.com/sgl-project/sglang/9.4-int8-and-other-quantization-methods) — Cover INT8, AWQ, GPTQ, QServe, GGUF, AutoRound, Petit, ModelSlim, BitsAndBytes, and other quantization methods; also covers quantized KV cache (FP8/FP4 KV).
 
 
---

 
# Sources

 
 - [python/sglang/srt/layers/quantization/base_config.py49-54](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/base_config.py#L49-L54)
 - [python/sglang/srt/layers/quantization/fp8.py15-69](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/fp8.py#L15-L69)
 - [python/sglang/srt/layers/quantization/fp8_utils.py10-25](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/fp8_utils.py#L10-L25)
 - [python/sglang/srt/layers/quantization/modelopt_quant.py34-192](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/modelopt_quant.py#L34-L192)
 - [python/sglang/srt/layers/moe/fused_moe_triton/layer.py58-61](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/fused_moe_triton/layer.py#L58-L61)
 - [python/sglang/srt/layers/moe/moe_runner/flashinfer_trtllm.py12-31](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/moe_runner/flashinfer_trtllm.py#L12-L31)
 - [python/sglang/srt/model_loader/loader.py167-210](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_loader/loader.py#L167-L210)
 - [python/sglang/srt/model_loader/weight_utils.py89-131](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_loader/weight_utils.py#L89-L131)
 - [python/sglang/srt/layers/linear.py60-80](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/linear.py#L60-L80)
 - [python/sglang/srt/layers/moe/utils.py237-243](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/utils.py#L237-L243)
