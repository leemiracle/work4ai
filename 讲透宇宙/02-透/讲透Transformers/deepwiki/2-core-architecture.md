> 来源: [https://deepwiki.com/huggingface/transformers/2-core-architecture](https://deepwiki.com/huggingface/transformers/2-core-architecture)
> DeepWiki huggingface/transformers | Last indexed: 3 September 2026 (8f5420

# Core Architecture

  Relevant source files 
 - [README.md](https://github.com/huggingface/transformers/blob/8f542025/README.md?plain=1)
 - [docs/source/en/_toctree.yml](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/_toctree.yml)
 - [docs/source/en/index.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/index.md?plain=1)
 - [docs/source/en/main_classes/quantization.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/main_classes/quantization.md?plain=1)
 - [docs/source/en/quantization/overview.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/quantization/overview.md?plain=1)
 - [src/transformers/__init__.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/__init__.py)
 - [src/transformers/configuration_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/configuration_utils.py)
 - [src/transformers/conversion_mapping.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/conversion_mapping.py)
 - [src/transformers/core_model_loading.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/core_model_loading.py)
 - [src/transformers/distributed/pipeline_parallel.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/distributed/pipeline_parallel.py)
 - [src/transformers/integrations/__init__.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/__init__.py)
 - [src/transformers/integrations/accelerate.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/accelerate.py)
 - [src/transformers/integrations/deepspeed.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/deepspeed.py)
 - [src/transformers/modeling_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py)
 - [src/transformers/models/__init__.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/__init__.py)
 - [src/transformers/models/auto/auto_mappings.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/auto_mappings.py)
 - [src/transformers/models/auto/configuration_auto.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/configuration_auto.py)
 - [src/transformers/models/auto/feature_extraction_auto.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/feature_extraction_auto.py)
 - [src/transformers/models/auto/image_processing_auto.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/image_processing_auto.py)
 - [src/transformers/models/auto/modeling_auto.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/modeling_auto.py)
 - [src/transformers/models/auto/processing_auto.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/processing_auto.py)
 - [src/transformers/models/auto/tokenization_auto.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/tokenization_auto.py)
 - [src/transformers/models/auto/video_processing_auto.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/video_processing_auto.py)
 - [src/transformers/quantizers/auto.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/quantizers/auto.py)
 - [src/transformers/testing_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/testing_utils.py)
 - [src/transformers/trainer.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py)
 - [src/transformers/trainer_pt_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer_pt_utils.py)
 - [src/transformers/trainer_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer_utils.py)
 - [src/transformers/training_args.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/training_args.py)
 - [src/transformers/utils/__init__.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/__init__.py)
 - [src/transformers/utils/dummy_pt_objects.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/dummy_pt_objects.py)
 - [src/transformers/utils/import_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/import_utils.py)
 - [src/transformers/utils/loading_report.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/loading_report.py)
 - [src/transformers/utils/quantization_config.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/quantization_config.py)
 - [tests/generation/test_configuration_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/generation/test_configuration_utils.py)
 - [tests/pipeline_parallel/test_pipeline_parallel.py](https://github.com/huggingface/transformers/blob/8f542025/tests/pipeline_parallel/test_pipeline_parallel.py)
 - [tests/test_modeling_common.py](https://github.com/huggingface/transformers/blob/8f542025/tests/test_modeling_common.py)
 - [tests/trainer/test_trainer.py](https://github.com/huggingface/transformers/blob/8f542025/tests/trainer/test_trainer.py)
 - [tests/utils/test_configuration_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_configuration_utils.py)
 - [tests/utils/test_core_model_loading.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_core_model_loading.py)
 - [tests/utils/test_feature_extraction_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_feature_extraction_utils.py)
 - [tests/utils/test_image_processing_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_image_processing_utils.py)
 - [tests/utils/test_modeling_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_modeling_utils.py)
 - [tests/utils/test_tokenization_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_tokenization_utils.py)
 - [utils/check_config_attributes.py](https://github.com/huggingface/transformers/blob/8f542025/utils/check_config_attributes.py)
 - [utils/check_repo.py](https://github.com/huggingface/transformers/blob/8f542025/utils/check_repo.py)
 
  The Hugging Face Transformers library is built upon a unified set of foundational abstractions that standardize the lifecycle of machine learning models across diverse modalities (text, vision, audio, etc.). This architecture ensures that regardless of the specific model architecture, users interact with a consistent API for configuration, initialization, weight loading, and inference.

 
## Foundational Abstractions

 The core of the library revolves around three primary base classes and a factory system that orchestrates their instantiation.

 
### PreTrainedConfig

 `PreTrainedConfig` serves as the serialization contract for model hyperparameters [src/transformers/configuration_utils.py23](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/configuration_utils.py#L23-L23) It handles the storage of architectural settings (e.g., `hidden_size`, `num_attention_heads`) and provides the mechanisms for loading from and saving to the Hugging Face Hub or local storage.

 
 - **Key Roles:** Serialization via `save_pretrained`, identification of model types, and hosting quantization or generation parameters.
 - **Details:** See [PreTrainedModel & PreTrainedConfig](https://deepwiki.com/huggingface/transformers/2.1-pretrainedmodel-and-pretrainedconfig).
 
 
### PreTrainedModel

 `PreTrainedModel` is the abstract base class for all PyTorch models in the library [src/transformers/modeling_utils.py164](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L164-L164) It inherits from `nn.Module` and adds high-level functionality for weight initialization, gradient checkpointing, and device management.

 
 - **Key Roles:** Implements `from_pretrained` for weight loading [src/transformers/modeling_utils.py171](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L171-L171) manages weight tying via `_tied_weights_keys` [src/transformers/modeling_utils.py62](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L62-L62) and provides the interface for attention backend selection (SDPA, Flash Attention, etc.).
 - **Details:** See [PreTrainedModel & PreTrainedConfig](https://deepwiki.com/huggingface/transformers/2.1-pretrainedmodel-and-pretrainedconfig).
 
 
### Auto Factory System

 The `Auto` classes (e.g., `AutoModel`, `AutoConfig`, `AutoTokenizer`, `AutoProcessor`) provide a unified entry point to the library. They use a lazy-mapping system to resolve a model identifier (like `google-bert/bert-base-uncased`) to the correct concrete class without requiring the user to import the specific model module [src/transformers/models/auto/auto_factory.py24](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/auto_factory.py#L24-L24)

 
 - **Key Roles:** Dynamic class resolution via `MODEL_MAPPING_NAMES` [src/transformers/models/auto/modeling_auto.py41](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/modeling_auto.py#L41-L41) `trust_remote_code` support, and lazy-loading of heavy model modules to reduce memory overhead via `_LazyModule` [src/transformers/utils/__init__.py33](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/__init__.py#L33-L33)
 - **Details:** See [Auto Classes & Lazy-Loading Factory](https://deepwiki.com/huggingface/transformers/2.2-auto-classes-and-lazy-loading-factory).
 
 
### The Weight Loading Lifecycle

 The library uses a sophisticated loading system capable of handling sharded checkpoints, `safetensors`, and heterogeneous weight mappings. The `WeightConverter` and `WeightRenaming` classes allow the library to load checkpoints from external sources that use different naming conventions or tensor layouts [src/transformers/modeling_utils.py51-53](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L51-L53)

 
 - **Key Roles:** Converting legacy weights, handling fused QKV projections, and managing expert stacking for Mixture-of-Experts (MoE) models.
 - **Details:** See [Model Weight Loading & Conversion](https://deepwiki.com/huggingface/transformers/2.3-model-weight-loading-and-conversion).
 
 
## System Entity Map

 The following diagrams illustrate how model identifiers are resolved and how core components interact.

 
### Diagram: Model Resolution Flow

 
```

```

 **Sources:** [src/transformers/models/auto/modeling_auto.py21-27](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/modeling_auto.py#L21-L27) [src/transformers/models/auto/modeling_auto.py41-86](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/modeling_auto.py#L41-L86) [src/transformers/utils/__init__.py33](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/__init__.py#L33-L33)

 
### Diagram: Component Interaction

 This diagram shows the relationship between the base classes and the loading/optimization utilities.

 
```

```

 **Sources:** [src/transformers/modeling_utils.py50-55](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L50-L55) [src/transformers/modeling_utils.py81-87](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L81-L87) [src/transformers/modeling_utils.py99-100](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L99-L100) [tests/test_modeling_common.py61](https://github.com/huggingface/transformers/blob/8f542025/tests/test_modeling_common.py#L61-L61)

 
## Core Architecture Components

 
| Component | Code Entity | Responsibility |
|---|---|---|
| Configuration | PreTrainedConfig | Holds model metadata and hyperparams src/transformers/configuration_utils.py23 |
| Model Base | PreTrainedModel | Lifecycle management and weight loading src/transformers/modeling_utils.py164 |
| Dynamic Mapping | _LazyAutoMapping | Maps model types to classes lazily src/transformers/models/auto/auto_factory.py24 |
| Weights Manager | WeightConverter | Handles cross-architecture weight conversion src/transformers/modeling_utils.py52 |
| Quantization Interface | HfQuantizer | Orchestrates model quantization backends src/transformers/modeling_utils.py99 |

 
## Detailed Subsystems

 
### [PreTrainedModel & PreTrainedConfig](https://deepwiki.com/huggingface/transformers/2.1-pretrainedmodel-and-pretrainedconfig)

 Covers the base classes providing the `from_pretrained` and `save_pretrained` lifecycle. It explains how `PreTrainedModel` handles weight tying via `_tied_weights_keys` [tests/test_modeling_common.py62](https://github.com/huggingface/transformers/blob/8f542025/tests/test_modeling_common.py#L62-L62) device placement via Accelerate [src/transformers/modeling_utils.py69-77](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L69-L77) and the selection of attention backends.

 
### [Auto Classes & Lazy-Loading Factory](https://deepwiki.com/huggingface/transformers/2.2-auto-classes-and-lazy-loading-factory)

 Explains the `AutoModel` registry system. It details how the library avoids importing all models at once using `_LazyModule` [src/transformers/utils/__init__.py33](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/__init__.py#L33-L33) and how `TOKENIZER_MAPPING_NAMES` links model strings to their respective tokenizer backends [src/transformers/models/auto/tokenization_auto.py65](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/tokenization_auto.py#L65-L65)

 
### [Model Weight Loading & Conversion](https://deepwiki.com/huggingface/transformers/2.3-model-weight-loading-and-conversion)

 Details the `WeightConverter` system. This handles logic for loading checkpoints where keys might not match the internal implementation, such as converting fused QKV weights or reordering RoPE-related tensors [src/transformers/modeling_utils.py50-56](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L50-L56)

 
### [Common Modeling Layers & Utilities](https://deepwiki.com/huggingface/transformers/2.4-common-modeling-layers-and-utilities)

 An overview of shared building blocks, including `GradientCheckpointingLayer` [tests/test_modeling_common.py61](https://github.com/huggingface/transformers/blob/8f542025/tests/test_modeling_common.py#L61-L61) and utilities for attention backends like SDPA, Flash Attention, and Flex Attention [src/transformers/modeling_utils.py81-88](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L81-L88)

 **Sources:** [src/transformers/modeling_utils.py1-184](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L1-L184) [src/transformers/models/auto/modeling_auto.py41-175](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/modeling_auto.py#L41-L175) [src/transformers/models/auto/tokenization_auto.py61-136](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/tokenization_auto.py#L61-L136) [src/transformers/utils/import_utils.py33-57](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/import_utils.py#L33-L57)
