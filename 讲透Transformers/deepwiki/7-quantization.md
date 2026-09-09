> 来源: [https://deepwiki.com/huggingface/transformers/7-quantization](https://deepwiki.com/huggingface/transformers/7-quantization)
> DeepWiki huggingface/transformers | Last indexed: 3 September 2026 (8f5420

# Quantization

  Relevant source files 
 - [docs/source/en/main_classes/quantization.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/main_classes/quantization.md?plain=1)
 - [docs/source/en/quantization/overview.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/quantization/overview.md?plain=1)
 - [docs/source/en/quantization/torchao.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/quantization/torchao.md?plain=1)
 - [src/transformers/conversion_mapping.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/conversion_mapping.py)
 - [src/transformers/core_model_loading.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/core_model_loading.py)
 - [src/transformers/distributed/pipeline_parallel.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/distributed/pipeline_parallel.py)
 - [src/transformers/integrations/__init__.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/__init__.py)
 - [src/transformers/integrations/accelerate.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/accelerate.py)
 - [src/transformers/integrations/bitsandbytes.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/bitsandbytes.py)
 - [src/transformers/integrations/deepspeed.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/deepspeed.py)
 - [src/transformers/integrations/eetq.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/eetq.py)
 - [src/transformers/integrations/fbgemm_fp8.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/fbgemm_fp8.py)
 - [src/transformers/integrations/mxfp4.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/mxfp4.py)
 - [src/transformers/integrations/quanto.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/quanto.py)
 - [src/transformers/integrations/torchao.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/torchao.py)
 - [src/transformers/modeling_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py)
 - [src/transformers/quantizers/auto.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/quantizers/auto.py)
 - [src/transformers/quantizers/base.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/quantizers/base.py)
 - [src/transformers/quantizers/quantizer_bnb_4bit.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/quantizers/quantizer_bnb_4bit.py)
 - [src/transformers/quantizers/quantizer_bnb_8bit.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/quantizers/quantizer_bnb_8bit.py)
 - [src/transformers/quantizers/quantizer_eetq.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/quantizers/quantizer_eetq.py)
 - [src/transformers/quantizers/quantizer_fbgemm_fp8.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/quantizers/quantizer_fbgemm_fp8.py)
 - [src/transformers/quantizers/quantizer_mxfp4.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/quantizers/quantizer_mxfp4.py)
 - [src/transformers/quantizers/quantizer_quanto.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/quantizers/quantizer_quanto.py)
 - [src/transformers/quantizers/quantizer_torchao.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/quantizers/quantizer_torchao.py)
 - [src/transformers/quantizers/quantizers_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/quantizers/quantizers_utils.py)
 - [src/transformers/testing_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/testing_utils.py)
 - [src/transformers/trainer.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py)
 - [src/transformers/trainer_pt_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer_pt_utils.py)
 - [src/transformers/trainer_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer_utils.py)
 - [src/transformers/training_args.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/training_args.py)
 - [src/transformers/utils/__init__.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/__init__.py)
 - [src/transformers/utils/import_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/import_utils.py)
 - [src/transformers/utils/loading_report.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/loading_report.py)
 - [src/transformers/utils/quantization_config.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/quantization_config.py)
 - [tests/pipeline_parallel/test_pipeline_parallel.py](https://github.com/huggingface/transformers/blob/8f542025/tests/pipeline_parallel/test_pipeline_parallel.py)
 - [tests/quantization/bnb/test_4bit.py](https://github.com/huggingface/transformers/blob/8f542025/tests/quantization/bnb/test_4bit.py)
 - [tests/quantization/bnb/test_mixed_int8.py](https://github.com/huggingface/transformers/blob/8f542025/tests/quantization/bnb/test_mixed_int8.py)
 - [tests/quantization/eetq_integration/test_eetq.py](https://github.com/huggingface/transformers/blob/8f542025/tests/quantization/eetq_integration/test_eetq.py)
 - [tests/quantization/fbgemm_fp8/test_fbgemm_fp8.py](https://github.com/huggingface/transformers/blob/8f542025/tests/quantization/fbgemm_fp8/test_fbgemm_fp8.py)
 - [tests/quantization/gptq/test_gptq.py](https://github.com/huggingface/transformers/blob/8f542025/tests/quantization/gptq/test_gptq.py)
 - [tests/quantization/mxfp4/test_mxfp4.py](https://github.com/huggingface/transformers/blob/8f542025/tests/quantization/mxfp4/test_mxfp4.py)
 - [tests/quantization/quanto_integration/test_quanto.py](https://github.com/huggingface/transformers/blob/8f542025/tests/quantization/quanto_integration/test_quanto.py)
 - [tests/quantization/torchao_integration/test_torchao.py](https://github.com/huggingface/transformers/blob/8f542025/tests/quantization/torchao_integration/test_torchao.py)
 - [tests/test_modeling_common.py](https://github.com/huggingface/transformers/blob/8f542025/tests/test_modeling_common.py)
 - [tests/trainer/test_trainer.py](https://github.com/huggingface/transformers/blob/8f542025/tests/trainer/test_trainer.py)
 - [tests/utils/test_core_model_loading.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_core_model_loading.py)
 - [tests/utils/test_modeling_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_modeling_utils.py)
 
  The quantization framework in 🤗 Transformers provides a unified interface for loading and running models in reduced precision (e.g., 8-bit, 4-bit, FP8). By leveraging the `HfQuantizer` abstraction, the library supports a wide range of backends including `bitsandbytes`, `GPTQ`, `AWQ`, `torchao`, and specialized FP8/MXFP4 kernels. This allows for significant reductions in memory footprint and increases in inference throughput while maintaining model quality.

 
## Core Infrastructure

 Quantization is orchestrated through a specialized lifecycle during model loading. The `HfQuantizer` base class defines the contract for environment validation, model preprocessing (such as module replacement), and weight conversion [src/transformers/quantizers/base.py23-32](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/quantizers/base.py#L23-L32)

 
### The HfQuantizer Lifecycle

 The quantization process is triggered when a `QuantizationConfigMixin` is passed to `from_pretrained`. The `get_hf_quantizer` factory resolves the correct subclass based on the `QuantizationMethod` defined in the configuration [src/transformers/quantizers/auto.py27-89](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/quantizers/auto.py#L27-L89)

 
 - **Validation**: `validate_environment()` checks for required libraries (e.g., `accelerate`, `bitsandbytes`, `torchao`) and hardware compatibility [src/transformers/quantizers/base.py136-142](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/quantizers/base.py#L136-L142)
 - **Preprocessing**: `preprocess_model()` is called while the model is on the `meta` device. It typically replaces standard `nn.Linear` layers with quantized variants (e.g., `bnb.nn.Linear4bit`) [src/transformers/quantizers/base.py155-172](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/quantizers/base.py#L155-L172)
 - **Weight Loading**: During `from_pretrained`, the quantizer uses `WeightConverter` and `ConversionOps` to transform standard weights into the format required by the backend [src/transformers/modeling_utils.py51-56](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L51-L56) [src/transformers/core_model_loading.py81-94](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/core_model_loading.py#L81-L94)
 - **Post-processing**: `postprocess_model()` finalizes the model, such as setting flags like `is_loaded_in_4bit` or initializing specific backend states [src/transformers/quantizers/base.py182-192](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/quantizers/base.py#L182-L192)
 
 
### System Architecture: From Config to Kernel

 The following diagram illustrates how a `QuantizationConfig` travels through the `PreTrainedModel` loading logic to trigger specific `HfQuantizer` implementations.

 **Quantization Dispatch Flow**

 
```

```

 Sources: [src/transformers/quantizers/base.py23-32](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/quantizers/base.py#L23-L32) [src/transformers/utils/quantization_config.py43-69](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/quantization_config.py#L43-L69) [src/transformers/quantizers/auto.py27-89](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/quantizers/auto.py#L27-L89) [src/transformers/core_model_loading.py51-56](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/core_model_loading.py#L51-L56)

 
## Supported Backends

 Transformers supports multiple quantization backends, categorized by their underlying technology and precision.

 
### BitsAndBytes, GPTQ & AWQ

 These are the most common methods for 4-bit and 8-bit quantization. `bitsandbytes` is widely used for on-the-fly quantization and QLoRA training via `BnbQuantizer8bit` and `BnbQuantizer4bit`, while GPTQ and AWQ are typically used for static, post-training quantization (PTQ) to maximize inference speed.

 
 - **BitsAndBytes**: Supports `load_in_8bit` and `load_in_4bit` (NF4/FP4) formats [src/transformers/utils/quantization_config.py44](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/quantization_config.py#L44-L44)
 - **GPTQ/AWQ**: Optimized 4-bit kernels for high-throughput LLM inference, often requiring a calibration dataset during the quantization phase [src/transformers/utils/quantization_config.py45-46](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/quantization_config.py#L45-L46)
 
 For details, see [BitsAndBytes, GPTQ & AWQ](https://deepwiki.com/huggingface/transformers/7.1-bitsandbytes-gptq-and-awq).

 
### FP8, GGUF/GGML & Other Quantization Backends

 Modern hardware and specific deployment targets require a broader set of backends. Transformers integrates specialized Triton kernels, the `torchao` library, and native GGUF loading.

 
 - **TorchAO**: A modular library for PyTorch architecture optimization, supporting various `int8` and `int4` schemes. It integrates with `torch.compile` for high-performance inference [src/transformers/utils/quantization_config.py55](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/quantization_config.py#L55-L55)
 - **GGUF/GGML**: Native loading of GGUF files, commonly used for CPU-efficient inference [src/transformers/utils/import_utils.py146](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/import_utils.py#L146-L146)
 - **Advanced Formats**: Support for `MXFP4`, `HQQ`, `EETQ`, `AQLM`, and `VPTQ` via dedicated `HfQuantizer` implementations [src/transformers/utils/quantization_config.py43-69](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/quantization_config.py#L43-L69)
 
 For details, see [FP8, GGUF/GGML & Other Quantization Backends](https://deepwiki.com/huggingface/transformers/7.2-fp8-ggufggml-and-other-quantization-backends).

 
## Key Utilities

 
| Utility | Role |
|---|---|
| get_keys_to_not_convert | Automatically detects modules that should remain in full precision (e.g., lm_head) for stability src/transformers/quantizers/base.py38-62 |
| validate_quantization_for_training | Ensures a quantized model is correctly configured for PEFT/QLoRA training src/transformers/trainer_utils.py149 |
| WeightConverter | Maps source checkpoint keys to target parameters during quantized loading src/transformers/core_model_loading.py52 |
| ConversionOps | Abstract class for defining weight transformations like Chunk or Concatenate src/transformers/core_model_loading.py81-94 |

 
### Weight Transformation Logic

 The transformation from standard weights to quantized structures involves specific `ConversionOps` that interact with the model's `state_dict`.

 **Weight Conversion Sequence**

 
```

```

 Sources: [src/transformers/quantizers/base.py155-174](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/quantizers/base.py#L155-L174) [src/transformers/core_model_loading.py54-56](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/core_model_loading.py#L54-L56) [src/transformers/modeling_utils.py99-101](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L99-L101)
