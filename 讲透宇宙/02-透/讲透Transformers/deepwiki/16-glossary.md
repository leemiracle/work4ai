> 来源: [https://deepwiki.com/huggingface/transformers/16-glossary](https://deepwiki.com/huggingface/transformers/16-glossary)
> DeepWiki huggingface/transformers | Last indexed: 3 September 2026 (8f5420

# Glossary

  Relevant source files 
 - [benchmark_v2/benchmark_scripts/continuous_batching_overall.py](https://github.com/huggingface/transformers/blob/8f542025/benchmark_v2/benchmark_scripts/continuous_batching_overall.py)
 - [docs/source/en/continuous_batching.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/continuous_batching.md?plain=1)
 - [docs/source/en/continuous_batching_architecture.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/continuous_batching_architecture.md?plain=1)
 - [docs/source/en/expert_parallelism.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/expert_parallelism.md?plain=1)
 - [docs/source/en/experts_interface.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/experts_interface.md?plain=1)
 - [docs/source/en/feature_extractors.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/feature_extractors.md?plain=1)
 - [docs/source/en/internal/generation_utils.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/internal/generation_utils.md?plain=1)
 - [docs/source/en/main_classes/continuous_batching.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/main_classes/continuous_batching.md?plain=1)
 - [docs/source/en/main_classes/quantization.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/main_classes/quantization.md?plain=1)
 - [docs/source/en/main_classes/text_generation.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/main_classes/text_generation.md?plain=1)
 - [docs/source/en/optimization_overview.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/optimization_overview.md?plain=1)
 - [docs/source/en/perf_infer_gpu_multi.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/perf_infer_gpu_multi.md?plain=1)
 - [docs/source/en/quantization/finegrained_fp8.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/quantization/finegrained_fp8.md?plain=1)
 - [docs/source/en/quantization/overview.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/quantization/overview.md?plain=1)
 - [docs/source/en/quantization/torchao.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/quantization/torchao.md?plain=1)
 - [docs/source/en/tensor_parallelism.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/tensor_parallelism.md?plain=1)
 - [docs/source/en/weightconverter.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/weightconverter.md?plain=1)
 - [docs/source/ko/internal/generation_utils.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ko/internal/generation_utils.md?plain=1)
 - [examples/pytorch/continuous_batching.py](https://github.com/huggingface/transformers/blob/8f542025/examples/pytorch/continuous_batching.py)
 - [src/transformers/cache_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cache_utils.py)
 - [src/transformers/conversion_mapping.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/conversion_mapping.py)
 - [src/transformers/core_model_loading.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/core_model_loading.py)
 - [src/transformers/distributed/__init__.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/distributed/__init__.py)
 - [src/transformers/distributed/configuration_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/distributed/configuration_utils.py)
 - [src/transformers/distributed/fsdp.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/distributed/fsdp.py)
 - [src/transformers/distributed/mixin.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/distributed/mixin.py)
 - [src/transformers/distributed/pipeline_parallel.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/distributed/pipeline_parallel.py)
 - [src/transformers/distributed/sharding_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/distributed/sharding_utils.py)
 - [src/transformers/distributed/tensor_parallel.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/distributed/tensor_parallel.py)
 - [src/transformers/distributed/utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/distributed/utils.py)
 - [src/transformers/generation/__init__.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/__init__.py)
 - [src/transformers/generation/candidate_generator.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/candidate_generator.py)
 - [src/transformers/generation/configuration_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/configuration_utils.py)
 - [src/transformers/generation/continuous_batching/cache.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/continuous_batching/cache.py)
 - [src/transformers/generation/continuous_batching/cache_manager.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/continuous_batching/cache_manager.py)
 - [src/transformers/generation/continuous_batching/continuous_api.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/continuous_batching/continuous_api.py)
 - [src/transformers/generation/continuous_batching/initialization.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/continuous_batching/initialization.py)
 - [src/transformers/generation/continuous_batching/input_outputs.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/continuous_batching/input_outputs.py)
 - [src/transformers/generation/continuous_batching/model_runner.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/continuous_batching/model_runner.py)
 - [src/transformers/generation/continuous_batching/requests.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/continuous_batching/requests.py)
 - [src/transformers/generation/continuous_batching/scheduler.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/continuous_batching/scheduler.py)
 - [src/transformers/generation/continuous_batching/utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/continuous_batching/utils.py)
 - [src/transformers/generation/logits_process.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/logits_process.py)
 - [src/transformers/generation/utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/utils.py)
 - [src/transformers/generation/watermarking.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/watermarking.py)
 - [src/transformers/integrations/__init__.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/__init__.py)
 - [src/transformers/integrations/accelerate.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/accelerate.py)
 - [src/transformers/integrations/bitsandbytes.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/bitsandbytes.py)
 - [src/transformers/integrations/deepspeed.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/deepspeed.py)
 - [src/transformers/integrations/eager_paged.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/eager_paged.py)
 - [src/transformers/integrations/eetq.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/eetq.py)
 - [src/transformers/integrations/executorch.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/executorch.py)
 - [src/transformers/integrations/fbgemm_fp8.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/fbgemm_fp8.py)
 - [src/transformers/integrations/flash_paged.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/flash_paged.py)
 - [src/transformers/integrations/mxfp4.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/mxfp4.py)
 - [src/transformers/integrations/quanto.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/quanto.py)
 - [src/transformers/integrations/sdpa_paged.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/sdpa_paged.py)
 - [src/transformers/integrations/tensor_parallel.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/tensor_parallel.py)
 - [src/transformers/integrations/torchao.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/torchao.py)
 - [src/transformers/masking_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/masking_utils.py)
 - [src/transformers/modeling_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py)
 - [src/transformers/models/cohere/modeling_cohere.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/cohere/modeling_cohere.py)
 - [src/transformers/models/gemma/modeling_gemma.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/gemma/modeling_gemma.py)
 - [src/transformers/models/llama/modeling_llama.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/llama/modeling_llama.py)
 - [src/transformers/models/mistral/modeling_mistral.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/mistral/modeling_mistral.py)
 - [src/transformers/models/mixtral/modeling_mixtral.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/mixtral/modeling_mixtral.py)
 - [src/transformers/models/olmo/modeling_olmo.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/olmo/modeling_olmo.py)
 - [src/transformers/models/persimmon/modeling_persimmon.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/persimmon/modeling_persimmon.py)
 - [src/transformers/models/phi/modeling_phi.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/phi/modeling_phi.py)
 - [src/transformers/models/phi3/modeling_phi3.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/phi3/modeling_phi3.py)
 - [src/transformers/models/qwen2/modeling_qwen2.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/qwen2/modeling_qwen2.py)
 - [src/transformers/models/qwen2_moe/modeling_qwen2_moe.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/qwen2_moe/modeling_qwen2_moe.py)
 - [src/transformers/models/stablelm/modeling_stablelm.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/stablelm/modeling_stablelm.py)
 - [src/transformers/models/starcoder2/modeling_starcoder2.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/starcoder2/modeling_starcoder2.py)
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
 - [tests/generation/test_candidate_generator.py](https://github.com/huggingface/transformers/blob/8f542025/tests/generation/test_candidate_generator.py)
 - [tests/generation/test_continuous_batching.py](https://github.com/huggingface/transformers/blob/8f542025/tests/generation/test_continuous_batching.py)
 - [tests/generation/test_logits_process.py](https://github.com/huggingface/transformers/blob/8f542025/tests/generation/test_logits_process.py)
 - [tests/generation/test_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/generation/test_utils.py)
 - [tests/pipeline_parallel/test_pipeline_parallel.py](https://github.com/huggingface/transformers/blob/8f542025/tests/pipeline_parallel/test_pipeline_parallel.py)
 - [tests/quantization/bnb/test_4bit.py](https://github.com/huggingface/transformers/blob/8f542025/tests/quantization/bnb/test_4bit.py)
 - [tests/quantization/bnb/test_mixed_int8.py](https://github.com/huggingface/transformers/blob/8f542025/tests/quantization/bnb/test_mixed_int8.py)
 - [tests/quantization/eetq_integration/test_eetq.py](https://github.com/huggingface/transformers/blob/8f542025/tests/quantization/eetq_integration/test_eetq.py)
 - [tests/quantization/fbgemm_fp8/test_fbgemm_fp8.py](https://github.com/huggingface/transformers/blob/8f542025/tests/quantization/fbgemm_fp8/test_fbgemm_fp8.py)
 - [tests/quantization/gptq/test_gptq.py](https://github.com/huggingface/transformers/blob/8f542025/tests/quantization/gptq/test_gptq.py)
 - [tests/quantization/mxfp4/test_mxfp4.py](https://github.com/huggingface/transformers/blob/8f542025/tests/quantization/mxfp4/test_mxfp4.py)
 - [tests/quantization/quanto_integration/test_quanto.py](https://github.com/huggingface/transformers/blob/8f542025/tests/quantization/quanto_integration/test_quanto.py)
 - [tests/quantization/torchao_integration/test_torchao.py](https://github.com/huggingface/transformers/blob/8f542025/tests/quantization/torchao_integration/test_torchao.py)
 - [tests/tensor_parallel/test_tensor_parallel.py](https://github.com/huggingface/transformers/blob/8f542025/tests/tensor_parallel/test_tensor_parallel.py)
 - [tests/test_modeling_common.py](https://github.com/huggingface/transformers/blob/8f542025/tests/test_modeling_common.py)
 - [tests/trainer/test_trainer.py](https://github.com/huggingface/transformers/blob/8f542025/tests/trainer/test_trainer.py)
 - [tests/utils/test_cache_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_cache_utils.py)
 - [tests/utils/test_core_model_loading.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_core_model_loading.py)
 - [tests/utils/test_distributed_sharding_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_distributed_sharding_utils.py)
 - [tests/utils/test_masking_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_masking_utils.py)
 - [tests/utils/test_modeling_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_modeling_utils.py)
 
  This glossary defines codebase-specific terms, abbreviations, and domain concepts essential for engineers onboarding to the Hugging Face Transformers library. It provides technical definitions and code pointers to help navigate the core abstractions and implementation patterns.

 
## Core Abstractions

 
### PreTrainedModel

 The base class for all PyTorch models in the library. It handles the lifecycle of a model, including weight initialization, downloading from the Hub, saving, and common utilities like gradient checkpointing and weight tying [src/transformers/modeling_utils.py165](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L165-L165) It inherits from `DistributedMixin` to support sharded loading and tensor parallelism [src/transformers/modeling_utils.py58](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L58-L58)

 
 - **Key Method**: `from_pretrained()` - The entry point for loading model weights and configuration, handling device dispatch and quantization [src/transformers/modeling_utils.py2500-2600](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L2500-L2600)
 - **Key Method**: `save_pretrained()` - Serializes the model weights (optionally as `safetensors`) and configuration to a directory [src/transformers/modeling_utils.py2200-2250](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L2200-L2250)
 
 
### PreTrainedConfig

 The base class for all model configurations. It stores hyperparameters (e.g., `hidden_size`, `num_attention_heads`) and handles serialization to/from JSON [src/transformers/configuration_utils.py55](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/configuration_utils.py#L55-L55) It also manages `generation_config` defaults [src/transformers/generation/configuration_utils.py100](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/configuration_utils.py#L100-L100)

 
### Auto Classes

 A factory system that allows instantiating the correct model, configuration, or tokenizer class from a model identifier (e.g., `google-bert/bert-base-uncased`) using a lookup mapping [src/transformers/models/auto/modeling_auto.py64-87](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/modeling_auto.py#L64-L87)

 
 - **AutoModel**: Resolves to the base model class for a given architecture [src/transformers/models/auto/modeling_auto.py37](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/modeling_auto.py#L37-L37)
 - **AutoConfig**: Resolves to the specific `PreTrainedConfig` subclass [src/transformers/models/auto/modeling_auto.py33](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/modeling_auto.py#L33-L33)
 
 
## Code Entity Space Mapping

 The following diagram bridges high-level library concepts to their specific implementation classes and registry mappings.

 
### Registry and Factory Mapping

 
```

```

 **Sources:** [src/transformers/models/auto/modeling_auto.py64-87](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/modeling_auto.py#L64-L87) [src/transformers/modeling_utils.py2500-2600](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L2500-L2600) [src/transformers/core_model_loading.py51-54](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/core_model_loading.py#L51-L54)

 
## Text Generation Terms

 
### GenerationMixin

 A mixin class providing the `generate()` method, which orchestrates various decoding strategies like greedy search, beam search, and sampling [tests/utils/test_modeling_utils.py123](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_modeling_utils.py#L123-L123) It manages the interaction between the model and the `GenerationConfig` [src/transformers/generation/configuration_utils.py100](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/configuration_utils.py#L100-L100)

 
### KV Cache

 A mechanism to store previously computed Key and Value tensors to avoid redundant computations during autoregressive generation [src/transformers/cache_utils.py1-35](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cache_utils.py#L1-L35)

 
 - **DynamicCache**: A cache that grows dynamically in length, storing tensors of shape `[batch_size, num_heads, seq_len, head_dim]` [src/transformers/cache_utils.py113-117](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cache_utils.py#L113-L117)
 - **StaticCache**: A fixed-size cache designed for `torch.compile` compatibility [src/transformers/cache_utils.py34](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cache_utils.py#L34-L34)
 - **QuantizedCache**: A cache that stores keys and values in a lower precision format (e.g., using HQQ or Quanto) to save memory [src/transformers/cache_utils.py33](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cache_utils.py#L33-L33)
 
 
### LogitsProcessor

 A class that modifies the prediction scores (logits) of a language model before sampling. Examples include `TemperatureLogitsWarper`, `TopKLogitsWarper`, and `RepetitionPenaltyLogitsProcessor` [src/transformers/generation/logits_process.py77-104](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/logits_process.py#L77-L104)

 
### Text Generation Flow

 
```

```

 **Sources:** [src/transformers/generation/utils.py137-148](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/utils.py#L137-L148) [src/transformers/cache_utils.py30-35](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cache_utils.py#L30-L35) [src/transformers/generation/logits_process.py87-104](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/logits_process.py#L87-L104) [src/transformers/generation/stopping_criteria.py105-113](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/stopping_criteria.py#L105-L113)

 
## Training & Optimization

 
### Trainer

 A feature-complete training loop for PyTorch. It abstracts away the complexity of distributed training (DDP, FSDP, DeepSpeed), mixed precision, and evaluation [src/transformers/trainer.py45](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py#L45-L45) It handles the integration of callbacks via `CallbackHandler` [src/transformers/trainer.py86](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py#L86-L86)

 
### TrainingArguments

 A dataclass containing all the hyperparameters for the `Trainer`, such as `learning_rate`, `fp16`, `bf16`, and optimization settings defined in `OptimizerNames` [src/transformers/training_args.py113-180](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/training_args.py#L113-L180)

 
### Data Collator

 Functions or classes that form a batch from a list of dataset elements, often handling dynamic padding [src/transformers/trainer.py56](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py#L56-L56)

 
 - **DataCollatorWithPadding**: Pads inputs to the maximum length in the batch [src/transformers/trainer.py56](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py#L56-L56)
 - **DataCollatorForLanguageModeling**: Handles masking and token alignment for Causal or Masked Language Modeling [tests/trainer/test_trainer.py38](https://github.com/huggingface/transformers/blob/8f542025/tests/trainer/test_trainer.py#L38-L38)
 
 
## Infrastructure & Formats

 
### Safetensors

 A safe and fast file format for storing tensors. Transformers uses this as the preferred format for model weights to avoid security risks associated with `pickle` [src/transformers/modeling_utils.py38-40](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L38-L40)

 
### SDPA (Scaled Dot Product Attention)

 A PyTorch native attention implementation (`torch.nn.functional.scaled_dot_product_attention`) that provides memory and speed optimizations [src/transformers/modeling_utils.py87](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L87-L87) The library manages fallbacks via `FLASH_ATTN_KERNEL_FALLBACK` [src/transformers/modeling_utils.py92](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L92-L92)

 
### Quantization

 Techniques to reduce model size and latency by lowering the precision of weights and/or activations.

 
 - **BitsAndBytes**: Support for 8-bit and 4-bit quantization via `BnbQuantizer` [src/transformers/modeling_utils.py118](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L118-L118)
 - **TorchAO**: Integration for advanced quantization techniques like FP8 or INT4 [src/transformers/cache_utils.py21](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cache_utils.py#L21-L21)
 
 
## Domain Concept Definitions

 
| Term | Definition | Code Pointer |
|---|---|---|
| Pipeline | High-level API for performing inference on specific tasks (e.g., text-generation) | tests/generation/test_utils.py39 |
| Processor | A class combining a tokenizer and a feature extractor (e.g., for multimodal models) | src/transformers/trainer.py82 |
| Speculative Decoding | Using a smaller "assistant" model to speed up generation via candidate validation | src/transformers/generation/utils.py54-68 |
| Weight Tying | Sharing weights between specific layers, often the embedding and LM head | src/transformers/modeling_utils.py62 |
| PEFT | Parameter-Efficient Fine-Tuning; integrated via adapters | src/transformers/modeling_utils.py86 |
| Continuous Batching | High-throughput inference by scheduling requests at the token level | src/transformers/generation/utils.py76 |

 **Sources:** [src/transformers/modeling_utils.py38-40](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L38-L40) [src/transformers/trainer.py45](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py#L45-L45) [src/transformers/training_args.py180](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/training_args.py#L180-L180) [src/transformers/generation/utils.py137-148](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/utils.py#L137-L148) [src/transformers/cache_utils.py30-35](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/cache_utils.py#L30-L35) [src/transformers/generation/candidate_generator.py54-68](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/candidate_generator.py#L54-L68)
