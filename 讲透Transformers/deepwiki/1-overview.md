> 来源: [https://deepwiki.com/huggingface/transformers/1-overview](https://deepwiki.com/huggingface/transformers/1-overview)
> DeepWiki huggingface/transformers | Last indexed: 3 September 2026 (8f5420

# Overview

  Relevant source files 
 - [MIGRATION_GUIDE_V5.md](https://github.com/huggingface/transformers/blob/8f542025/MIGRATION_GUIDE_V5.md?plain=1)
 - [README.md](https://github.com/huggingface/transformers/blob/8f542025/README.md?plain=1)
 - [docs/source/en/_toctree.yml](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/_toctree.yml)
 - [docs/source/en/index.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/index.md?plain=1)
 - [docs/source/en/main_classes/quantization.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/main_classes/quantization.md?plain=1)
 - [docs/source/en/quantization/overview.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/quantization/overview.md?plain=1)
 - [docs/source/ja/_toctree.yml](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ja/_toctree.yml)
 - [docs/source/ja/model_doc/albert.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ja/model_doc/albert.md?plain=1)
 - [docs/source/ja/model_doc/bart.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ja/model_doc/bart.md?plain=1)
 - [docs/source/ja/model_doc/bert.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ja/model_doc/bert.md?plain=1)
 - [docs/source/ja/model_doc/big_bird.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ja/model_doc/big_bird.md?plain=1)
 - [docs/source/ja/model_doc/bigbird_pegasus.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ja/model_doc/bigbird_pegasus.md?plain=1)
 - [docs/source/ja/model_doc/bloom.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ja/model_doc/bloom.md?plain=1)
 - [docs/source/ja/model_doc/camembert.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ja/model_doc/camembert.md?plain=1)
 - [docs/source/ja/model_doc/canine.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ja/model_doc/canine.md?plain=1)
 - [docs/source/ja/model_doc/convbert.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ja/model_doc/convbert.md?plain=1)
 - [docs/source/ja/model_doc/ctrl.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ja/model_doc/ctrl.md?plain=1)
 - [docs/source/ja/model_doc/data2vec.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ja/model_doc/data2vec.md?plain=1)
 - [docs/source/ja/model_doc/deberta-v2.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ja/model_doc/deberta-v2.md?plain=1)
 - [docs/source/ja/model_doc/deberta.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ja/model_doc/deberta.md?plain=1)
 - [docs/source/ko/_toctree.yml](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ko/_toctree.yml)
 - [docs/source/ko/accelerator_selection.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ko/accelerator_selection.md?plain=1)
 - [src/transformers/__init__.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/__init__.py)
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
 - [src/transformers/models/cohere/tokenization_cohere.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/cohere/tokenization_cohere.py)
 - [src/transformers/models/cpmant/modeling_cpmant.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/cpmant/modeling_cpmant.py)
 - [src/transformers/models/nllb/tokenization_nllb.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/nllb/tokenization_nllb.py)
 - [src/transformers/models/vits/modeling_vits.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/vits/modeling_vits.py)
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
 - [tests/models/albert/test_tokenization_albert.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/albert/test_tokenization_albert.py)
 - [tests/models/cpmant/test_modeling_cpmant.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/cpmant/test_modeling_cpmant.py)
 - [tests/models/cpmant/test_tokenization_cpmant.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/cpmant/test_tokenization_cpmant.py)
 - [tests/models/mbart/test_tokenization_mbart.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/mbart/test_tokenization_mbart.py)
 - [tests/models/nllb/test_tokenization_nllb.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/nllb/test_tokenization_nllb.py)
 - [tests/models/pegasus/test_tokenization_pegasus.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/pegasus/test_tokenization_pegasus.py)
 - [tests/models/plbart/test_tokenization_plbart.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/plbart/test_tokenization_plbart.py)
 - [tests/models/seamless_m4t/test_tokenization_seamless_m4t.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/seamless_m4t/test_tokenization_seamless_m4t.py)
 - [tests/models/vits/test_modeling_vits.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/vits/test_modeling_vits.py)
 - [tests/pipeline_parallel/test_pipeline_parallel.py](https://github.com/huggingface/transformers/blob/8f542025/tests/pipeline_parallel/test_pipeline_parallel.py)
 - [tests/test_modeling_common.py](https://github.com/huggingface/transformers/blob/8f542025/tests/test_modeling_common.py)
 - [tests/trainer/test_trainer.py](https://github.com/huggingface/transformers/blob/8f542025/tests/trainer/test_trainer.py)
 - [tests/utils/test_core_model_loading.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_core_model_loading.py)
 - [tests/utils/test_model_output.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_model_output.py)
 - [tests/utils/test_modeling_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_modeling_utils.py)
 - [utils/check_config_attributes.py](https://github.com/huggingface/transformers/blob/8f542025/utils/check_config_attributes.py)
 - [utils/check_repo.py](https://github.com/huggingface/transformers/blob/8f542025/utils/check_repo.py)
 
  The Hugging Face Transformers library provides thousands of pretrained models to perform tasks on different modalities such as text, vision, and audio. Its primary goal is to provide a unified API to load, train, and export state-of-the-art machine learning models while maintaining a "single-file-per-model" philosophy that prioritizes readability over complex inheritance [README.md70-84](https://github.com/huggingface/transformers/blob/8f542025/README.md?plain=1#L70-L84)

 
## Design Philosophy

 The library is built on several core principles:

 
 - **Ease of Use**: High-level abstractions like `pipeline()` allow for inference in just a few lines of code [src/transformers/pipelines/__init__.py141-173](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/pipelines/__init__.py#L141-L173)
 - **Performance**: Deep integration with specialized attention backends (SDPA, Flash Attention) and quantization frameworks (BitsAndBytes, GPTQ, AWQ) [src/transformers/utils/import_utils.py46-55](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/import_utils.py#L46-L55)
 - **Hackability**: Model implementations are designed to be self-contained in their respective directories within `src/transformers/models/`, making them easy to modify [src/transformers/models/__init__.py1-200](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/__init__.py#L1-L200)
 - **Ecosystem Pivot**: Acts as a central model definition that is compatible with various training frameworks (DeepSpeed, FSDP) and inference engines [README.md73-76](https://github.com/huggingface/transformers/blob/8f542025/README.md?plain=1#L73-L76)
 
 For a deep dive into the V5 migration and composition-over-abstraction principles, see **[Design Philosophy & V5 Migration Guide](https://deepwiki.com/huggingface/transformers/1.2-design-philosophy-and-v5-migration-guide)**.

 
## Key Subsystems

 The library is organized into several major subsystems that work together to handle the lifecycle of a model:

 
### 1. Model & Configuration

 All models inherit from `PreTrainedModel` [src/transformers/modeling_utils.py76](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L76-L76) which provides standard methods for loading and saving weights (`from_pretrained`, `save_pretrained`). Each model is paired with a `PreTrainedConfig` [src/transformers/configuration_utils.py66](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/configuration_utils.py#L66-L66) that defines the architecture's hyperparameters.

 
### 2. Auto Factories & Lazy Loading

 To simplify model access, the library uses "Auto" classes (e.g., `AutoModel`, `AutoConfig`, `AutoTokenizer`). These classes use `_LazyAutoMapping` [src/transformers/models/auto/auto_factory.py24](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/auto_factory.py#L24-L24) and `_LazyModule` [src/transformers/__init__.py33](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/__init__.py#L33-L33) to resolve model identifiers to specific implementation classes without importing every model in the library at once.

 
### 3. Training & Optimization

 The `Trainer` class [src/transformers/trainer.py45](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py#L45-L45) provides a feature-complete training loop that handles distributed training, mixed precision, and evaluation. It integrates with `TrainingArguments` [src/transformers/training_args.py180](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/training_args.py#L180-L180) to control hyperparameters and `TrainerCallback` [src/transformers/trainer_callback.py91](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer_callback.py#L91-L91) for extending behavior.

 
### 4. Input Processing

 Raw data is converted into tensors using Tokenizers (for text), Image Processors (for vision), and Feature Extractors (for audio). The `ProcessorMixin` [src/transformers/processing_utils.py178](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/processing_utils.py#L178-L178) often combines these for multimodal models.

 
### 5. Text Generation

 The `GenerationMixin` [src/transformers/generation/utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/utils.py) (referenced in [src/transformers/models/auto/modeling_auto.py31](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/modeling_auto.py#L31-L31)) provides the `generate()` method, which supports various decoding strategies like beam search and speculative decoding, controlled via `GenerationConfig` [src/transformers/modeling_utils.py67](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L67-L67)

 
## System Architecture

 The following diagrams illustrate the relationship between high-level APIs and the underlying code entities.

 
### Request Flow and Entity Mapping

 
```

```

 **Sources:** [src/transformers/models/auto/modeling_auto.py41-175](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/modeling_auto.py#L41-L175) [src/transformers/models/auto/tokenization_auto.py65-136](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/tokenization_auto.py#L65-L136) [src/transformers/modeling_utils.py51-56](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L51-L56)

 
### Training Subsystem Relationships

 This diagram shows how the `Trainer` orchestrates various components during the fine-tuning process.

 
```

```

 **Sources:** [src/transformers/trainer.py85-100](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py#L85-L100) [src/transformers/training_args.py113-160](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/training_args.py#L113-L160) [src/transformers/__init__.py88-101](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/__init__.py#L88-L101)

 
## Exploration Guide

 Detailed documentation is split into the following sections:

 
 - **[Getting Started & Installation](https://deepwiki.com/huggingface/transformers/1.1-getting-started-and-installation)**: Setup, dependency management via `setup.py`/`pyproject.toml`, and initial inference with `pipeline()`.
 - **[Design Philosophy & V5 Migration Guide](https://deepwiki.com/huggingface/transformers/1.2-design-philosophy-and-v5-migration-guide)**: Understanding the single-file-per-model approach and the V5 dynamic weight loading API.
 - **Core Architecture**: Deep dives into `PreTrainedModel`, the `Auto` factory, and the `WeightConverter` system [src/transformers/core_model_loading.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/core_model_loading.py)
 - **Model Architectures**: Exploration of LLMs, MoEs, SSMs (Mamba), and Multimodal models [src/transformers/models/auto/modeling_auto.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/modeling_auto.py)
 - **Tokenization & Input Processing**: Detailed look at `PreTrainedTokenizerBase` and modality-specific processors [src/transformers/models/auto/tokenization_auto.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/auto/tokenization_auto.py)
 - **Text Generation**: Detailed look at `GenerationMixin`, KV caching strategies, and speculative decoding [src/transformers/generation/utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/generation/utils.py)
 - **Training**: Comprehensive guide to the `Trainer`, `DataCollator`, and optimization utilities [src/transformers/trainer.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py)
 - **Quantization & Attention**: Using BitsAndBytes, Flash Attention-2, and Hub-loaded kernels [src/transformers/modeling_utils.py80-95](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L80-L95)
 - **CI/CD & Infrastructure**: Overview of the CircleCI pipeline and repository consistency tools like `check_repo.py` [utils/check_repo.py](https://github.com/huggingface/transformers/blob/8f542025/utils/check_repo.py)
 
 **Sources:** [docs/source/en/_toctree.yml1-221](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/_toctree.yml#L1-L221) [src/transformers/__init__.py1-185](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/__init__.py#L1-L185)
