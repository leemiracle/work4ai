<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/transformers · page 6 Training · fetched 2026-10-26 -->

# Training

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [awesome-transformers.md](awesome-transformers.md)
- [docs/source/ar/llm_tutorial_optimization.md](docs/source/ar/llm_tutorial_optimization.md)
- [docs/source/ar/sagemaker.md](docs/source/ar/sagemaker.md)
- [docs/source/ar/serialization.md](docs/source/ar/serialization.md)
- [docs/source/ar/trainer.md](docs/source/ar/trainer.md)
- [docs/source/en/llm_tutorial_optimization.md](docs/source/en/llm_tutorial_optimization.md)
- [docs/source/en/main_classes/optimizer_schedules.md](docs/source/en/main_classes/optimizer_schedules.md)
- [docs/source/en/main_classes/quantization.md](docs/source/en/main_classes/quantization.md)
- [docs/source/en/model_doc/prophetnet.md](docs/source/en/model_doc/prophetnet.md)
- [docs/source/en/quantization/overview.md](docs/source/en/quantization/overview.md)
- [docs/source/en/trainer.md](docs/source/en/trainer.md)
- [docs/source/es/trainer.md](docs/source/es/trainer.md)
- [docs/source/ja/serialization.md](docs/source/ja/serialization.md)
- [docs/source/ko/llm_tutorial_optimization.md](docs/source/ko/llm_tutorial_optimization.md)
- [docs/source/ko/model_doc/mamba.md](docs/source/ko/model_doc/mamba.md)
- [docs/source/ko/model_doc/mamba2.md](docs/source/ko/model_doc/mamba2.md)
- [docs/source/ko/serialization.md](docs/source/ko/serialization.md)
- [docs/source/ko/trainer.md](docs/source/ko/trainer.md)
- [docs/source/zh/serialization.md](docs/source/zh/serialization.md)
- [examples/scheduler/README.md](examples/scheduler/README.md)
- [examples/scheduler/run_greedy.py](examples/scheduler/run_greedy.py)
- [src/transformers/integrations/__init__.py](src/transformers/integrations/__init__.py)
- [src/transformers/models/layoutlmv2/configuration_layoutlmv2.py](src/transformers/models/layoutlmv2/configuration_layoutlmv2.py)
- [src/transformers/optimization.py](src/transformers/optimization.py)
- [src/transformers/quantizers/auto.py](src/transformers/quantizers/auto.py)
- [src/transformers/testing_utils.py](src/transformers/testing_utils.py)
- [src/transformers/trainer.py](src/transformers/trainer.py)
- [src/transformers/trainer_pt_utils.py](src/transformers/trainer_pt_utils.py)
- [src/transformers/trainer_utils.py](src/transformers/trainer_utils.py)
- [src/transformers/training_args.py](src/transformers/training_args.py)
- [src/transformers/utils/__init__.py](src/transformers/utils/__init__.py)
- [src/transformers/utils/import_utils.py](src/transformers/utils/import_utils.py)
- [src/transformers/utils/quantization_config.py](src/transformers/utils/quantization_config.py)
- [tests/optimization/test_greedy_lr.py](tests/optimization/test_greedy_lr.py)
- [tests/optimization/test_optimization.py](tests/optimization/test_optimization.py)
- [tests/trainer/test_trainer.py](tests/trainer/test_trainer.py)
- [tests/trainer/test_trainer_optimizers.py](tests/trainer/test_trainer_optimizers.py)

</details>



The training infrastructure in Transformers provides a high-level API for fine-tuning and evaluating models across various hardware backends. It centers around the `Trainer` class [src/transformers/trainer.py:15-16](), which abstracts the complexity of the training loop, distributed orchestration, and device-specific optimizations.

Sources: [src/transformers/trainer.py:15-16]()

## Core Infrastructure

The training system is built on two primary pillars: the `Trainer` and `TrainingArguments`.

*   **`Trainer`**: An optimized PyTorch training loop that handles gradient accumulation, mixed precision (FP16/BF16), evaluation strategies, and checkpointing [src/transformers/trainer.py:15-16](). It integrates with `accelerate` to support distributed training modes such as DDP and Fully Sharded Data Parallel (FSDP), as well as with `deepspeed` for efficient large-scale training [src/transformers/trainer.py:216-233]().
*   **`TrainingArguments`**: A comprehensive dataclass centralizing all training hyperparameters and infrastructure settings, such as learning rates, batch sizes, precision flags (`fp16`, `bf16`, `tf32`), gradient accumulation, logging schedules, and checkpoint strategies [src/transformers/training_args.py:180-200]().

The `Trainer` class orchestrates training by consuming a model, datasets, and an instance of `TrainingArguments` to configure its behavior. It invokes optimization utilities, manages distributed device contexts, and coordinates evaluation and prediction runs.

For complete details, see the child page [Trainer & TrainingArguments](#6.1).

### Trainer System Orchestration Diagram

This diagram bridges the conceptual training system components with their code entities:

```mermaid
title "Trainer System Orchestration"
graph TD
    subgraph "Natural_Language_Space"
        TA["TrainingArguments"]
        T["Trainer"]
        CH["CallbackHandler"]
    end

    subgraph "Code_Entity_Space"
        T_Class["Trainer (src/transformers/trainer.py)"]
        TA_Class["TrainingArguments (src/transformers/training_args.py)"]
        OC_Class["OptimizerContext (src/transformers/trainer_optimizer.py)"]
        DC_Class["DataCollator (src/transformers/data/data_collator.py)"]
    end

    TA -- "configures" --> T
    T -- "executes optimization via" --> OC_Class
    T -- "manages callbacks via" --> CH
    T -- "uses data preprocessing via" --> DC_Class
    TA_Class -- "defines parameters for" --> TA
    T_Class -- "implements training loop" --> T
```

Sources: [src/transformers/trainer.py:15-233](), [src/transformers/training_args.py:180-200](), [src/transformers/trainer_optimizer.py:90-102](), [src/transformers/data/data_collator.py:30-90]()

## Callbacks, Optimizers & Schedulers

Training behavior extension and optimization configuration are achieved with:

*   **TrainerCallback System**: The `TrainerCallback` base class allows users to hook into key lifecycle events in the training loop such as start/end of epochs or steps, evaluation start/end, or checkpoint saving [src/transformers/trainer.py:86-95](). The `CallbackHandler` inside `Trainer` manages callback execution to modularize behavior.
*   **Built-in Callbacks**: Includes callbacks for early stopping, progress reporting, TensorBoard logging, and integration with experiment tracking services like WandB or Comet. These are often managed via `integration_utils.py` [src/transformers/integrations/__init__.py:84-126]().
*   **Optimizers & LR Schedulers**: Supports standard optimizers like `AdamW` and `Adafactor`, as well as schedulers for learning rate annealing. Custom and advanced optimizers (e.g., paged versions, 8-bit optimizers) are available via `trainer_optimizer.py` [src/transformers/trainer.py:96-102](), and registered in `OptimizerNames` in `TrainingArguments` [src/transformers/training_args.py:113-160](). The `GreedyLR` scheduler is also available [src/transformers/trainer.py:82]().

This structure allows flexible customization of training schedules and logging.

For full technical specifics, see [Callbacks, Optimizers & Schedulers](#6.2).

Sources: [src/transformers/trainer.py:86-95](), [src/transformers/integrations/__init__.py:84-126](), [src/transformers/trainer.py:96-102](), [src/transformers/training_args.py:113-160](), [src/transformers/trainer.py:82]()

## Data Collators & Datasets

Proper input batching and preprocessing is critical for training efficiency:

*   **DataCollator Classes**: Implement dynamic padding and batching strategies to transform raw input samples into tensors suitable for model input [src/transformers/trainer.py:57]():
    *   `DataCollatorWithPadding`: Handles dynamic padding to batch inputs of unequal length [src/transformers/trainer.py:57]().
    *   `DataCollatorForSeq2Seq`: Specialized collator for encoder-decoder models.
    *   `DataCollatorForLanguageModeling`: Adds masked tokens for MLM or manages causal padding for CLM.
    *   `DataCollatorForTokenClassification`: Supports token classification task-specific batching.
*   **Dataset Support**: Works with both standard map-style datasets and `IterableDataset`s, enabling streaming or very large datasets usage [src/transformers/trainer.py:53](). Utilities in `trainer_pt_utils.py` assist with handling distributed data shards (`IterableDatasetShard`) and optimized sampler strategies (`LengthGroupedSampler`, `BatchRebalanceSampler`) [src/transformers/trainer_pt_utils.py:106-108]().
*   **Preprocessing Utilities**: Task-specific processing logic and argument parsers are provided in the `data/processors` and related modules. The `hf_argparser` is used for command-line argument parsing.

These components interact seamlessly with the `Trainer` to provide batches efficiently.

For detailed usage and classes, see [Data Collators & Datasets](#6.3).

Sources: [src/transformers/trainer.py:57](), [src/transformers/trainer.py:53](), [src/transformers/trainer_pt_utils.py:106-108]()

## Training Examples & Scripts

The `examples/pytorch/` directory demonstrates practical usage with diverse scenarios:

1.  **Trainer-based scripts**: Standard fine-tuning and training using the `Trainer` abstraction on tasks like language modeling (CLM, MLM), named entity recognition (NER), GLUE, summarization, translation, speech recognition, and image classification.
2.  **Accelerate based no-trainer scripts**: Offers lower-level training loops leveraging the `accelerate` library for customization and control, especially valuable for research or advanced workflows requiring full control. This pattern is used when the `Trainer` class is not suitable for specific needs.
3.  Supports advanced features like mixed precision, distributed training, gradient accumulation, and more.

These examples serve as templates and starting points for building custom training workflows.

For full script listings and details, see [Training Examples & Scripts](#6.4).

Sources: [src/transformers/trainer.py:216-233]()

## Quantization-Aware Training & Fine-Tuning

Transformers support training and fine-tuning quantized models seamlessly with PEFT integration and advanced quantization backends:

*   **Validation Before Training**: The framework validates:
    *   That quantized models are not combined with `torch.compile()` (unsupported) [src/transformers/trainer_utils.py:124-128]().
    *   That fully quantized models have trainable adapters (like PEFT modules such as LoRA) attached; direct training of quantized weights is unsupported [src/transformers/trainer_utils.py:130-135]().
    *   That the quantization method supports training, raising errors otherwise [src/transformers/trainer_utils.py:137-142]().
*   **Integration**: The validation is performed by `validate_quantization_for_training` in the Trainer utilities [src/transformers/trainer_utils.py:102-143]().
*   **Quantization Methods**: A variety of quantization approaches are enumerated in `QuantizationMethod` from `utils/quantization_config.py` [src/transformers/utils/quantization_config.py:43-70]() for reference. These methods are mapped to specific quantizers in `quantizers/auto.py` [src/transformers/quantizers/auto.py:77-108]().

This enables efficient and safe fine-tuning workflows leveraging quantized models with adapter strategies.

### Quantization Training Validation Diagram

```mermaid
title "Quantization Training Validation"
graph LR
    subgraph "Natural_Language_Space"
        QM["QuantizedModel"]
        AM["AdapterPEFT"]
    end

    subgraph "Code_Entity_Space"
        VQ["validate_quantization_for_training (src/transformers/trainer_utils.py)"]
        TC["Training Capability Checks"]
        QM_Enum["QuantizationMethod (src/transformers/utils/quantization_config.py)"]
        AQ_Map["AUTO_QUANTIZER_MAPPING (src/transformers/quantizers/auto.py)"]
    end

    QM --> VQ
    AM --> VQ
    VQ -- "Enforces" --> TC
    TC -- "Raises Error on" --> E1["Quantized + Compiled Model"]
    TC -- "Raises Error on" --> E2["Quantized + No Trainable Adapters"]
    TC -- "Raises Error on" --> E3["Quantization Method Lacks Training Support"]
    QM_Enum -- "Defines" --> E3
    AQ_Map -- "Maps to" --> QM_Enum
```

Sources: [src/transformers/trainer_utils.py:102-143](), [src/transformers/utils/quantization_config.py:43-70](), [src/transformers/quantizers/auto.py:77-108]()

---

### Child Pages
*   **[Trainer & TrainingArguments](#6.1)**: Deep dive into the training loop and hyperparameter configuration.
*   **[Callbacks, Optimizers & Schedulers](#6.2)**: Extending the trainer and configuring optimization logic.
*   **[Data Collators & Datasets](#6.3)**: Utilities for batching and preprocessing training data.
*   **[Training Examples & Scripts](#6.4)**: Reference implementations and the no-trainer pattern.

---

