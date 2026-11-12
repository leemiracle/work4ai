> 来源: [https://deepwiki.com/huggingface/transformers/6-training](https://deepwiki.com/huggingface/transformers/6-training)
> DeepWiki huggingface/transformers | Last indexed: 3 September 2026 (8f5420

# Training

  Relevant source files 
 - [docs/source/en/main_classes/callback.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/main_classes/callback.md?plain=1)
 - [docs/source/en/main_classes/quantization.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/main_classes/quantization.md?plain=1)
 - [docs/source/en/quantization/overview.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/quantization/overview.md?plain=1)
 - [docs/source/ja/main_classes/callback.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ja/main_classes/callback.md?plain=1)
 - [docs/source/ko/main_classes/callback.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ko/main_classes/callback.md?plain=1)
 - [docs/source/zh/main_classes/callback.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/zh/main_classes/callback.md?plain=1)
 - [examples/pytorch/README.md](https://github.com/huggingface/transformers/blob/8f542025/examples/pytorch/README.md?plain=1)
 - [examples/pytorch/instance-segmentation/README.md](https://github.com/huggingface/transformers/blob/8f542025/examples/pytorch/instance-segmentation/README.md?plain=1)
 - [examples/pytorch/object-detection/README.md](https://github.com/huggingface/transformers/blob/8f542025/examples/pytorch/object-detection/README.md?plain=1)
 - [examples/pytorch/test_accelerate_examples.py](https://github.com/huggingface/transformers/blob/8f542025/examples/pytorch/test_accelerate_examples.py)
 - [examples/pytorch/test_pytorch_examples.py](https://github.com/huggingface/transformers/blob/8f542025/examples/pytorch/test_pytorch_examples.py)
 - [src/transformers/conversion_mapping.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/conversion_mapping.py)
 - [src/transformers/core_model_loading.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/core_model_loading.py)
 - [src/transformers/distributed/pipeline_parallel.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/distributed/pipeline_parallel.py)
 - [src/transformers/integrations/__init__.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/__init__.py)
 - [src/transformers/integrations/accelerate.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/accelerate.py)
 - [src/transformers/integrations/deepspeed.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/deepspeed.py)
 - [src/transformers/integrations/integration_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/integration_utils.py)
 - [src/transformers/modeling_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py)
 - [src/transformers/quantizers/auto.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/quantizers/auto.py)
 - [src/transformers/testing_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/testing_utils.py)
 - [src/transformers/trainer.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py)
 - [src/transformers/trainer_callback.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer_callback.py)
 - [src/transformers/trainer_pt_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer_pt_utils.py)
 - [src/transformers/trainer_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer_utils.py)
 - [src/transformers/training_args.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/training_args.py)
 - [src/transformers/utils/__init__.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/__init__.py)
 - [src/transformers/utils/import_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/import_utils.py)
 - [src/transformers/utils/loading_report.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/loading_report.py)
 - [src/transformers/utils/quantization_config.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/quantization_config.py)
 - [tests/pipeline_parallel/test_pipeline_parallel.py](https://github.com/huggingface/transformers/blob/8f542025/tests/pipeline_parallel/test_pipeline_parallel.py)
 - [tests/test_modeling_common.py](https://github.com/huggingface/transformers/blob/8f542025/tests/test_modeling_common.py)
 - [tests/trainer/test_trainer.py](https://github.com/huggingface/transformers/blob/8f542025/tests/trainer/test_trainer.py)
 - [tests/trainer/test_trainer_accelerator.py](https://github.com/huggingface/transformers/blob/8f542025/tests/trainer/test_trainer_accelerator.py)
 - [tests/trainer/test_trainer_callback.py](https://github.com/huggingface/transformers/blob/8f542025/tests/trainer/test_trainer_callback.py)
 - [tests/trainer/test_trainer_checkpointing.py](https://github.com/huggingface/transformers/blob/8f542025/tests/trainer/test_trainer_checkpointing.py)
 - [tests/trainer/test_trainer_evaluation.py](https://github.com/huggingface/transformers/blob/8f542025/tests/trainer/test_trainer_evaluation.py)
 - [tests/trainer/test_training_args.py](https://github.com/huggingface/transformers/blob/8f542025/tests/trainer/test_training_args.py)
 - [tests/trainer/trainer_test_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/trainer/trainer_test_utils.py)
 - [tests/utils/test_core_model_loading.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_core_model_loading.py)
 - [tests/utils/test_modeling_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_modeling_utils.py)
 
  The training infrastructure in Transformers provides a high-level API for fine-tuning and evaluating models across various hardware backends. It centers around the `Trainer` class, which abstracts the complexity of the training loop, distributed orchestration, and device-specific optimizations.

 
## Core Infrastructure

 The training system is built on two primary pillars: the `Trainer` and `TrainingArguments`.

 
 - **`Trainer`**: An optimized PyTorch training loop that handles gradient accumulation, mixed precision (FP16/BF16), evaluation strategies, and checkpointing [src/transformers/trainer.py15-16](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py#L15-L16) It integrates with `accelerate` to support distributed training (DDP, FSDP) and `deepspeed` for large-scale model training [src/transformers/trainer.py63-69](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py#L63-L69) [src/transformers/trainer.py217-219](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py#L217-L219)
 - **`TrainingArguments`**: A comprehensive dataclass that centralizes all hyperparameters, including learning rate, batch sizes, and infrastructure choices like `fp16`, `bf16`, or `tf32` [src/transformers/training_args.py180-200](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/training_args.py#L180-L200) It also manages complex configurations like `AcceleratorConfig` [src/transformers/training_args.py74](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/training_args.py#L74-L74) and `FSDPOption` [src/transformers/training_args.py29](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/training_args.py#L29-L29)
 
 For details, see [Trainer & TrainingArguments](https://deepwiki.com/huggingface/transformers/6.1-trainer-and-trainingarguments).

 
### Training Flow Architecture

 The following diagram illustrates the relationship between the `Trainer` orchestration and the underlying utilities.

 **Trainer System Orchestration**

 
```

```

 Sources: [src/transformers/trainer.py85-117](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py#L85-L117) [src/transformers/training_args.py180-200](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/training_args.py#L180-L200) [src/transformers/trainer.py217-219](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py#L217-L219)

 
## Callbacks, Optimizers & Schedulers

 The `Trainer` is highly extensible through a callback system. `TrainerCallback` allows users to inject custom behavior into the training loop at specific stages (e.g., `on_step_end`, `on_epoch_end`) [src/transformers/trainer_callback.py85-94](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer_callback.py#L85-L94) Default callbacks include `ProgressCallback` and `DefaultFlowCallback` [src/transformers/trainer.py185-186](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py#L185-L186)

 Optimization is handled via the `optimization.py` module, which provides implementations for `AdamW`, `Adafactor`, and a variety of learning rate schedulers [src/transformers/trainer.py81](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py#L81-L81) The library supports a wide array of optimizers through `OptimizerNames`, including `ADEMAMIX`, `LION`, `GALORE`, and `PAGED_ADAMW` [src/transformers/training_args.py113-159](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/training_args.py#L113-L159)

 For details, see [Callbacks, Optimizers & Schedulers](https://deepwiki.com/huggingface/transformers/6.2-callbacks-optimizers-and-schedulers).

 
## Data Collators & Datasets

 Training requires converting raw datasets into batches of tensors. `DataCollator` classes handle task-specific batching, such as:

 
 - `DataCollatorWithPadding`: Dynamically pads inputs to the maximum length in a batch [src/transformers/trainer.py56](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py#L56-L56)
 - `DataCollatorForLanguageModeling`: Handles masking for MLM or causal padding for CLM [src/transformers/trainer.py38](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py#L38-L38)
 
 The `Trainer` also supports `IterableDataset` for large-scale streaming data [src/transformers/trainer.py52](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py#L52-L52) and provides utilities for managing shards in distributed environments via `IterableDatasetShard` [src/transformers/trainer_pt_utils.py104](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer_pt_utils.py#L104-L104)

 For details, see [Data Collators & Datasets](https://deepwiki.com/huggingface/transformers/6.3-data-collators-and-datasets).

 
## Training Examples & Scripts

 The `examples/pytorch/` directory contains reference implementations for various tasks. These scripts demonstrate two patterns:

 
 - **Trainer-based**: Using the `Trainer` API for standard tasks like GLUE, SQuAD, or Causal Language Modeling.
 - **Accelerate-based**: "No-trainer" scripts that use raw PyTorch with the `accelerate` library for users who need full control over the training loop, often referred to as the "no-trainer" pattern [src/transformers/trainer.py217-218](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py#L217-L218)
 
 For details, see [Training Examples & Scripts](https://deepwiki.com/huggingface/transformers/6.4-training-examples-and-scripts).

 
## Quantization & Model Loading in Training

 The training infrastructure supports fine-tuning quantized models, primarily through PEFT (Parameter-Efficient Fine-Tuning). The `Trainer` validates if a quantized model is trainable using `validate_quantization_for_training`, ensuring that adapters (like LoRA) are attached if the base model is frozen [src/transformers/trainer_utils.py149](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer_utils.py#L149-L149)

 The library also provides a sophisticated weight loading system via `WeightConverter` and `ConversionOps` to handle model weights during initialization or checkpoint loading [src/transformers/core_model_loading.py52-82](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/core_model_loading.py#L52-L82)

 **Quantization Training Validation**

 
```

```

 Sources: [src/transformers/trainer_utils.py149](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer_utils.py#L149-L149) [src/transformers/utils/quantization_config.py43-69](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/quantization_config.py#L43-L69) [src/transformers/core_model_loading.py81-112](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/core_model_loading.py#L81-L112)

 
---

 
### Child Pages

 
 - **[Trainer & TrainingArguments](https://deepwiki.com/huggingface/transformers/6.1-trainer-and-trainingarguments)**: Deep dive into the training loop, evaluation, and hyperparameter configuration.
 - **[Callbacks, Optimizers & Schedulers](https://deepwiki.com/huggingface/transformers/6.2-callbacks-optimizers-and-schedulers)**: Extending the trainer and configuring optimization logic including 8-bit and paged variants.
 - **[Data Collators & Datasets](https://deepwiki.com/huggingface/transformers/6.3-data-collators-and-datasets)**: Utilities for batching, padding, and preprocessing training data for various modalities.
 - **[Training Examples & Scripts](https://deepwiki.com/huggingface/transformers/6.4-training-examples-and-scripts)**: Reference implementations for specific tasks and the Accelerate-based no-trainer pattern.
