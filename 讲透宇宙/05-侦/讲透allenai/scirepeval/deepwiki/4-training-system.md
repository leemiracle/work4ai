<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/scirepeval · page 4 Training System · fetched 2026-10-26 -->

# Training System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [evaluation/EVALUATION.md](evaluation/EVALUATION.md)
- [training/TRAINING.md](training/TRAINING.md)
- [training/pl_training.py](training/pl_training.py)
- [training/tasks.py](training/tasks.py)

</details>



The training system provides a PyTorch Lightning-based framework for training multi-task scientific document representation models. This system supports various model architectures including standard multi-task learning, control token-based training, BERT PALs, and adapter-based approaches. The training framework is designed to handle multiple scientific tasks simultaneously with different loss functions and data formats.

For information about evaluating trained models, see [Core Evaluation Framework](#2). For details about model architectures and variants, see [Model Architecture and Variants](#3).

## Training Framework Architecture

The training system is built around the `SciRepTrain` PyTorch Lightning module which orchestrates multi-task training across different scientific document understanding tasks. The framework supports four main model variants and handles task-specific components through a modular design.

```mermaid
graph TB
    subgraph "Training Framework Core"
        SRT["SciRepTrain"] 
        PL["PyTorch Lightning Trainer"]
        TC["load_tasks()"]
    end
    
    subgraph "Task Management"
        TF["TaskFamily"]
        TH["TaskHead"] 
        LOSSES["Loss Functions"]
        CONFIG["tasks_config.json"]
    end
    
    subgraph "Model Variants"
        CLS["MTL CLS Mode"]
        CTRL["MTL CTRL Mode"] 
        PALS["BERT PALs Mode"]
        ADP["Adapter Mode"]
    end
    
    subgraph "Data Pipeline"
        CD["ClassificationDataset"]
        RD["RegressionDataset"] 
        IRD["IRDataset"]
        TD["TripletDataset"]
        CCD["CustomChainDataset"]
    end
    
    CONFIG --> TC
    TC --> TF
    TF --> TH
    TF --> LOSSES
    SRT --> TF
    SRT --> CLS
    SRT --> CTRL
    SRT --> PALS
    SRT --> ADP
    SRT --> CCD
    CCD --> CD
    CCD --> RD
    CCD --> IRD
    CCD --> TD
    PL --> SRT
```

Sources: [training/pl_training.py:45-99](), [training/tasks.py:9-36]()

## Task Configuration System

Tasks are defined using JSON configuration files that specify the task type, data sources, labels, and training parameters. The `TaskFamily` class encapsulates each task's configuration and associated components.

```mermaid
graph LR
    subgraph "Task Configuration"
        JSON["tasks_config.json"]
        TF["TaskFamily"]
        LOAD["load_tasks()"]
    end
    
    subgraph "Task Types"
        CLF["classification"]
        REG["regression"] 
        IR["ir"]
        TRP["triplet"]
    end
    
    subgraph "Task Components"
        HEAD["TaskHead"]
        LOSS["Loss Function"]
        CTRL["ctrl_token"]
        LABELS["labels"]
    end
    
    JSON --> LOAD
    LOAD --> TF
    TF --> CLF
    TF --> REG
    TF --> IR
    TF --> TRP
    CLF --> HEAD
    REG --> HEAD
    IR --> LOSS
    TRP --> LOSS
    TF --> CTRL
    TF --> LABELS
```

### Task Configuration Format

Each task is defined with the following structure:

| Field | Description | Required |
|-------|-------------|----------|
| `name` | Task identifier | Yes |
| `type` | Task type: classification, regression, ir, triplet | Yes |
| `data_files` or `dataset` | Data source specification | Yes |
| `ctrl_token` | Control token or task ID | Yes (for non-CLS variants) |
| `labels` | Label file path (classification only) | Conditional |
| `labels_field` | Label field name | Conditional |
| `multi_label` | Multi-label classification flag | Optional |
| `sample_size` | Sample size limits | Optional |

Sources: [training/TRAINING.md:20-63](), [training/tasks.py:124-151]()

## Model Variants and Training Modes

The training system supports four distinct model variants, each with different architectural approaches to multi-task learning:

```mermaid
graph TB
    subgraph "SciRepTrain Configuration"
        USE_CTRL["use_ctrl_tokens"]
        PALS_CFG["pals_cfg"] 
        ADAPTER_TYPE["adapter_type"]
    end
    
    subgraph "Model Variant Selection"
        MTL_CLS["MTL CLS<br/>Standard [CLS] token"]
        MTL_CTRL["MTL CTRL<br/>Control codes"]
        BERT_PALS["BERT PALs<br/>Task modules"]
        ADAPTERS["Adapters<br/>Task adapters"]
    end
    
    subgraph "Implementation"
        AUTOMODEL["AutoModel.from_pretrained()"]
        BERT_PALS_ENC["BertPalsEncoder"]
        ADAPTER_FACTORY["AdapterFactory.get_adapter()"]
        RESIZE_EMBED["resize_token_embeddings()"]
    end
    
    USE_CTRL --> MTL_CTRL
    PALS_CFG --> BERT_PALS
    ADAPTER_TYPE --> ADAPTERS
    
    MTL_CLS --> AUTOMODEL
    MTL_CTRL --> AUTOMODEL
    MTL_CTRL --> RESIZE_EMBED
    BERT_PALS --> BERT_PALS_ENC
    ADAPTERS --> ADAPTER_FACTORY
```

### Training Mode Selection

The training mode is determined by command-line arguments:

- **MTL CLS**: Default mode using `[CLS]` token embeddings
- **MTL CTRL**: Enable with `--ctrl-tokens` flag
- **BERT PALs**: Enable with `--pals-config` parameter
- **Adapters**: Enable with `--adapter-type single`
- **Fusion**: Enable with `--adapter-type fusion`

Sources: [training/pl_training.py:65-94](), [training/TRAINING.md:67-89]()

## Loss Functions and Task Heads

The training system implements task-specific loss functions and classification heads based on the task type:

| Task Type | Loss Function | Head Type | Use Case |
|-----------|---------------|-----------|----------|
| Classification | CrossEntropyLoss | TaskHead(num_labels) | Document categorization |
| Multi-label Classification | BCEWithLogitsLoss | TaskHead(num_labels) | Multi-category assignment |
| Regression | MSELoss | TaskHead(1) | Continuous prediction |
| IR/Triplet | TripletLoss | None | Similarity learning |

```mermaid
graph LR
    subgraph "Task Processing"
        BATCH["Training Batch"]
        CALC_LOSS["calc_loss()"]
        TASK_DICT["task_dict"]
    end
    
    subgraph "Loss Calculation"
        CLF_LOSS["CrossEntropyLoss"]
        REG_LOSS["MSELoss"] 
        TRP_LOSS["TripletLoss"]
        SCL_LOSS["SCLLoss (optional)"]
    end
    
    subgraph "Forward Pass"
        ENCODING["self()"]
        HEADS["self.heads[name]"]
        LOGITS["logits"]
    end
    
    BATCH --> CALC_LOSS
    CALC_LOSS --> TASK_DICT
    CALC_LOSS --> ENCODING
    ENCODING --> HEADS
    HEADS --> LOGITS
    LOGITS --> CLF_LOSS
    LOGITS --> REG_LOSS
    ENCODING --> TRP_LOSS
    ENCODING --> SCL_LOSS
```

Sources: [training/pl_training.py:148-179](), [training/tasks.py:38-151]()

## Data Loading and Multi-Task Processing

The training system uses a sophisticated data loading pipeline that handles multiple datasets simultaneously through the `CustomChainDataset` class:

```mermaid
graph TB
    subgraph "Data Loading Pipeline"
        LOAD_DATA["load_data()"]
        DATASETS_LIB["datasets.load_dataset()"]
        TASK_DATASET_MAP["task_dataset_map"]
    end
    
    subgraph "Dataset Classes"
        CD["ClassificationDataset"]
        RD["RegressionDataset"]
        IRD["IRDataset"] 
        TD["TripletDataset"]
        MLCD["MultiLabelClassificationDataset"]
    end
    
    subgraph "Multi-Task Coordination" 
        CCD["CustomChainDataset"]
        BATCH_STRAT["BatchingStrategy.MIXED_PROPORTIONAL"]
        MULTI_COLLATE["multi_collate()"]
    end
    
    LOAD_DATA --> DATASETS_LIB
    DATASETS_LIB --> TASK_DATASET_MAP
    TASK_DATASET_MAP --> CD
    TASK_DATASET_MAP --> RD
    TASK_DATASET_MAP --> IRD
    TASK_DATASET_MAP --> TD
    TASK_DATASET_MAP --> MLCD
    CD --> CCD
    RD --> CCD
    IRD --> CCD
    TD --> CCD
    MLCD --> CCD
    CCD --> BATCH_STRAT
    CCD --> MULTI_COLLATE
```

The data loading process supports both HuggingFace datasets and local JSON files, with automatic streaming for large datasets.

Sources: [training/pl_training.py:202-245](), [training/mtl_datasets.py]()

## Training Process Flow

The training process follows the standard PyTorch Lightning workflow with multi-task loss computation:

```mermaid
graph TB
    subgraph "Training Step"
        TRAIN_STEP["training_step()"]
        CALC_LOSS["calc_loss()"]
        LOSS_PER_TASK["loss_per_task"]
        TOTAL_LOSS["torch.sum(loss_per_task)"]
    end
    
    subgraph "Validation Step"
        VAL_STEP["validation_step()"]
        VAL_LOSS["val_loss"]
        SYNC_DDP["sync_ddp_if_available()"]
        LOG_METRICS["self.log()"]
    end
    
    subgraph "Optimizer Configuration"
        CONFIG_OPT["configure_optimizers()"]
        ADAMW["AdamW"]
        SCHEDULER["get_linear_schedule_with_warmup"]
        INV_SQRT["InverseSquareRootSchedule"]
    end
    
    TRAIN_STEP --> CALC_LOSS
    CALC_LOSS --> LOSS_PER_TASK
    LOSS_PER_TASK --> TOTAL_LOSS
    
    VAL_STEP --> VAL_LOSS
    VAL_LOSS --> SYNC_DDP
    SYNC_DDP --> LOG_METRICS
    
    CONFIG_OPT --> ADAMW
    CONFIG_OPT --> SCHEDULER
    CONFIG_OPT --> INV_SQRT
```

### Checkpointing and Model Saving

The training system automatically saves model checkpoints and tokenizers:

- Checkpoints saved to `<output>/full_run/<version>/checkpoints/`
- Model and tokenizer saved via `on_save_checkpoint()` callback
- TensorBoard logging enabled by default

Sources: [training/pl_training.py:181-200](), [training/pl_training.py:247-257](), [training/pl_training.py:287-325]()

## Command Line Usage

The training system provides a comprehensive command-line interface through `pl_training.py`:

### Basic Usage Examples

**MTL CLS Training:**
```bash
python pl_training.py --gpu 2 --tasks-config sample_data/tasks_config.json allenai/specter experiment_v1
```

**MTL CTRL Training:**
```bash
python pl_training.py --gpu 2 --ctrl-tokens --tasks-config sample_data/tasks_config.json allenai/specter experiment_ctrl
```

**BERT PALs Training:**
```bash
python pl_training.py --gpu 2 --pals-config pals.config.json --tasks-config sample_data/tasks_config.json allenai/specter experiment_pals
```

**Adapter Training:**
```bash
python pl_training.py --gpu 2 --adapter-type single --tasks-config sample_data/tasks_config.json allenai/specter experiment_adapters
```

### Key Training Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--batch-size` | Training batch size | 16 |
| `--lr` | Initial learning rate | 1e-4 |
| `--peak-lr` | Peak learning rate | 5e-5 |
| `--warmup` | Warmup steps | 700 |
| `--epochs` | Training epochs | 2 |
| `--grad-accum` | Gradient accumulation steps | 8 |
| `--max-len` | Maximum sequence length | 512 |

Sources: [training/TRAINING.md:67-136](), [training/pl_training.py:259-325]()

---

