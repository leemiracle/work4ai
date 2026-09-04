> 来源: [https://deepwiki.com/sgl-project/sglang/7-model-configuration-and-loading](https://deepwiki.com/sgl-project/sglang/7-model-configuration-and-loading)
> DeepWiki sgl-project/sglang | Last indexed: 27 Aug 2026 (94183a)

# Model Configuration and Loading

  Relevant source files 
 - [python/sglang/srt/configs/__init__.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/configs/__init__.py)
 - [python/sglang/srt/configs/load_config.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/configs/load_config.py)
 - [python/sglang/srt/configs/model_config.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/configs/model_config.py)
 - [python/sglang/srt/configs/spark2_5.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/configs/spark2_5.py)
 - [python/sglang/srt/function_call/function_call_parser.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/function_call/function_call_parser.py)
 - [python/sglang/srt/function_call/spark25_detector.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/function_call/spark25_detector.py)
 - [python/sglang/srt/layers/linear.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/linear.py)
 - [python/sglang/srt/layers/quantization/compressed_tensors/schemes/compressed_tensors_w8a8_fp8_moe.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/compressed_tensors/schemes/compressed_tensors_w8a8_fp8_moe.py)
 - [python/sglang/srt/layers/quantization/dequantization.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/dequantization.py)
 - [python/sglang/srt/layers/quantization/quark/quark.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/quark/quark.py)
 - [python/sglang/srt/layers/quantization/quark/schemes/quark_w4a4_mxfp4.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/quark/schemes/quark_w4a4_mxfp4.py)
 - [python/sglang/srt/layers/quantization/quark/schemes/quark_w4a4_mxfp4_moe.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/quark/schemes/quark_w4a4_mxfp4_moe.py)
 - [python/sglang/srt/layers/quantization/quark/utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/quark/utils.py)
 - [python/sglang/srt/layers/quantization/utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/utils.py)
 - [python/sglang/srt/model_loader/loader.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_loader/loader.py)
 - [python/sglang/srt/model_loader/remote_instance_weight_loader_utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_loader/remote_instance_weight_loader_utils.py)
 - [python/sglang/srt/model_loader/weight_utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_loader/weight_utils.py)
 - [python/sglang/srt/models/spark2_5.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/spark2_5.py)
 - [python/sglang/srt/utils/hf_transformers/__init__.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/hf_transformers/__init__.py)
 - [python/sglang/srt/utils/hf_transformers/common.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/hf_transformers/common.py)
 - [python/sglang/srt/utils/hf_transformers/config.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/hf_transformers/config.py)
 - [python/sglang/srt/utils/hf_transformers/mistral_utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/hf_transformers/mistral_utils.py)
 - [python/sglang/srt/utils/hf_transformers/processor.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/hf_transformers/processor.py)
 - [python/sglang/srt/utils/hf_transformers/tokenizer.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/hf_transformers/tokenizer.py)
 - [python/sglang/srt/utils/hf_transformers_patches.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/hf_transformers_patches.py)
 - [python/sglang/srt/utils/hf_transformers_utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/hf_transformers_utils.py)
 - [test/registered/quant/test_is_layer_skipped.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/quant/test_is_layer_skipped.py)
 - [test/registered/quant/test_quark_mxfp4.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/quant/test_quark_mxfp4.py)
 - [test/registered/unit/constrained/test_mistral_common_xgrammar.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/constrained/test_mistral_common_xgrammar.py)
 - [test/registered/unit/function_call/test_spark25_detector.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/function_call/test_spark25_detector.py)
 - [test/registered/unit/model_loader/test_prefetch_checkpoints.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/model_loader/test_prefetch_checkpoints.py)
 - [test/registered/unit/tokenizer/test_mistral_empty_assistant.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/tokenizer/test_mistral_empty_assistant.py)
 - [test/registered/unit/tokenizer/test_tekken_tokenizer_routing.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/tokenizer/test_tekken_tokenizer_routing.py)
 - [test/registered/unit/utils/test_hf_transformers.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/utils/test_hf_transformers.py)
 
  
## Purpose and Scope

 This page presents a high-level overview of the model configuration and loading subsystem in SGLang. It describes how models are configured, validated, and prepared with loaded weights for serving in the system. The process integrates with quantization configuration, supports distributed and parallel loading, and accommodates a wide range of model architectures and file formats.

 Deep technical details and specific implementation aspects are delegated to the following child pages:

 
 - [ModelConfig System](https://deepwiki.com/sgl-project/sglang/7.1-modelconfig-system) — Details the `ModelConfig` class, including model parameter derivation and validation.
 - [Model Loading Pipeline](https://deepwiki.com/sgl-project/sglang/7.2-model-loading-pipeline) — Explains the full model loading flow, file format support, tokenizer/processor loading, remote loading (R-Fork), and checkpoint integration.
 - [Supported Model Architectures](https://deepwiki.com/sgl-project/sglang/7.3-supported-model-architectures) — Enumerates supported model families with relevant configuration and execution traits.
 
 
## System Overview

 The model configuration and loading subsystem converts raw inputs from server arguments and user parameters into a fully constructed model instance with properly loaded and distributed weights ready for inference or training. This process involves three key stages:

 
 - **Model Configuration**: Parsing input parameters and deriving model metadata such as context length, layer count, hidden sizes, quantization strategies, and multimodal support. This occurs in the `ModelConfig` class [python/sglang/srt/configs/model_config.py236-258](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/configs/model_config.py#L236-L258)
 - **Load Preparation**: Deciding on the model weight format, download location, and loading options via the `LoadConfig` class. This includes support for formats like PyTorch `.pt`, Safetensors, GGUF, BitsAndBytes, FastSafetensors, Remote Loading (R-Fork), and specialized caches [python/sglang/srt/configs/load_config.py17-38](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/configs/load_config.py#L17-L38)
 - **Weight Loading**: Orchestrating downloading and loading model weights, potentially distributed across tensor-parallel ranks. The loader streams weights through format-specific iterators, handles quantization transformations (such as FP8 to MXFP4 online requantization), sharding, and dispatches loaded tensors to model layers [python/sglang/srt/model_loader/loader.py220-280](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_loader/loader.py#L220-L280) [python/sglang/srt/layers/quantization/quark/quark.py127-144](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/quark/quark.py#L127-L144)
 
 
### Model Loading Architecture

 
```

```

 Sources: [python/sglang/srt/configs/model_config.py236-258](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/configs/model_config.py#L236-L258) [python/sglang/srt/model_loader/loader.py220-280](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_loader/loader.py#L220-L280) [python/sglang/srt/configs/load_config.py17-38](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/configs/load_config.py#L17-L38) [python/sglang/srt/model_loader/weight_utils.py105-122](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_loader/weight_utils.py#L105-L122)

 
## ModelConfig System

 `ModelConfig` is the core class responsible for interpreting server and user parameters into a coherent model specification. It loads HF-style configs, reconciles legacy and current attributes, performs validations, and fills in derived fields necessary for model construction and runtime behavior.

 Key aspects:

 
 - **Architecture Detection**: Automatically detects architecture classes, support for multi-modal inputs, and specialized attentions such as DeepSeek DSA or MLA [python/sglang/srt/configs/model_config.py120-137](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/configs/model_config.py#L120-L137)
 - **Quantization Attributes**: Incorporates quantization method, bit-width, and supported tensor parallelism layouts. It also handles specific logic for sparse models like MiniMax M3 [python/sglang/srt/configs/model_config.py173-193](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/configs/model_config.py#L173-L193)
 - **MTP Support**: Handles Multi-Token Prediction (MTP) configurations, including specific sharding for fused QKV tensors in MiMoV2 architectures [python/sglang/srt/configs/model_config.py46-76](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/configs/model_config.py#L46-L76)
 
 
### ModelConfig Initialization Flow

 
```

```

 Sources: [python/sglang/srt/configs/model_config.py30-75](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/configs/model_config.py#L30-L75) [python/sglang/srt/configs/model_config.py236-258](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/configs/model_config.py#L236-L258)

 
## Model Loading Pipeline

 The model loading pipeline handles the retrieval, processing, and loading of model weights into the runtime model instance. It supports multiple weight formats and network-backed weight distribution architectures.

 
### Weight Loading Loop

 
```

```

 
### Features of the Loading Pipeline

 
 - **Multi-Format Support**: Incorporates reading from Safetensors, PyTorch `.pt` files, GGUF, npcache, dummy (random init), BitsAndBytes, FastSafetensors, and RunAI object storage [python/sglang/srt/configs/load_config.py17-39](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/configs/load_config.py#L17-L39)
 - **Quantization Loading**: Enables runtime quantization or loading pre-quantized weights (FP8, AWQ, GPTQ, Quark MXFP4). The system can perform online requantization from FP8 to MXFP4 during loading [python/sglang/srt/layers/quantization/quark/quark.py127-144](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/quark/quark.py#L127-L144)
 - **Remote Instance Weight Loading (R-Fork)**: Supports loading weights from remote instances over RPC, enabling distributed service deployments [python/sglang/srt/model_loader/remote_instance_weight_loader_utils.py15-80](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_loader/remote_instance_weight_loader_utils.py#L15-L80)
 - **Efficient Device Management**: Uses `device_loading_context` to manage parameter placement during the load, moving parameters to the target device (e.g., GPU) and optionally using pin memory [python/sglang/srt/model_loader/loader.py150-162](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_loader/loader.py#L150-L162)
 
 Sources: [python/sglang/srt/configs/load_config.py17-39](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/configs/load_config.py#L17-L39) [python/sglang/srt/model_loader/loader.py150-204](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_loader/loader.py#L150-L204) [python/sglang/srt/model_loader/remote_instance_weight_loader_utils.py15-80](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_loader/remote_instance_weight_loader_utils.py#L15-L80) [python/sglang/srt/model_loader/weight_utils.py105-122](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_loader/weight_utils.py#L105-L122)

 
## Supported Model Architectures

 SGLang supports a broad set of model families spanning LLMs and VLMs. The system employs family-specific configuration derivation and loading logic registered in the `_CONFIG_REGISTRY` [python/sglang/srt/utils/hf_transformers/common.py92-146](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/hf_transformers/common.py#L92-L146)

 
| Model Family | Description and Traits |
|---|---|
| DeepSeek | V3/V4 models with MLA, DSA, and MTP support python/sglang/srt/utils/hf_transformers/common.py154-165 |
| Qwen | Qwen3.5 and Qwen3-Next featuring fused kernels and optimized pipeline support python/sglang/srt/utils/hf_transformers/common.py114-128 |
| Gemma | Supports Gemma4 unified architectures with sliding-window attention (SWA) handling python/sglang/srt/utils/hf_transformers/config.py161-190 |
| InternVL | Vision-language models with specialized InternVLChatConfig handling python/sglang/srt/utils/hf_transformers/config.py153-157 |
| Mellum | Newer architectures supported via specialized config aliases python/sglang/srt/utils/hf_transformers/common.py176-198 |
| Others | Includes Kimi, Bailing, Exaone, Olmo, Step, MiniMax, Falcon, and Nemotron python/sglang/srt/utils/hf_transformers/common.py92-146 |

 
### Natural Language to Code Entity Association Diagram

 
```

```

 Sources: [python/sglang/srt/configs/model_config.py46-76](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/configs/model_config.py#L46-L76) [python/sglang/srt/model_loader/loader.py198-236](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_loader/loader.py#L198-L236) [python/sglang/srt/utils/hf_transformers/common.py92-146](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/hf_transformers/common.py#L92-L146) [python/sglang/srt/utils/hf_transformers/config.py77-202](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/hf_transformers/config.py#L77-L202) [python/sglang/srt/layers/linear.py58-80](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/linear.py#L58-L80)

 
---

 For further technical details and implementation specifics, please consult the respective child pages:

 
 - [ModelConfig System](https://deepwiki.com/sgl-project/sglang/7.1-modelconfig-system)
 - [Model Loading Pipeline](https://deepwiki.com/sgl-project/sglang/7.2-model-loading-pipeline)
 - [Supported Model Architectures](https://deepwiki.com/sgl-project/sglang/7.3-supported-model-architectures)
