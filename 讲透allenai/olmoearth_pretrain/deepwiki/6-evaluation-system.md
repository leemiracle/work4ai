<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/olmoearth_pretrain · page 6 Evaluation System · fetched 2026-10-26 -->

# Evaluation System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [olmoearth_pretrain/evals/finetune/evaluate.py](olmoearth_pretrain/evals/finetune/evaluate.py)
- [olmoearth_pretrain/evals/finetune/train.py](olmoearth_pretrain/evals/finetune/train.py)
- [olmoearth_pretrain/evals/knn.py](olmoearth_pretrain/evals/knn.py)
- [olmoearth_pretrain/evals/linear_probe.py](olmoearth_pretrain/evals/linear_probe.py)
- [olmoearth_pretrain/evals/metrics.py](olmoearth_pretrain/evals/metrics.py)
- [olmoearth_pretrain/internal/all_evals.py](olmoearth_pretrain/internal/all_evals.py)
- [olmoearth_pretrain/internal/constants.py](olmoearth_pretrain/internal/constants.py)
- [olmoearth_pretrain/internal/full_eval_sweep.py](olmoearth_pretrain/internal/full_eval_sweep.py)
- [olmoearth_pretrain/internal/full_eval_sweep_finetune.py](olmoearth_pretrain/internal/full_eval_sweep_finetune.py)
- [olmoearth_pretrain/train/callbacks/evaluator_callback.py](olmoearth_pretrain/train/callbacks/evaluator_callback.py)
- [scripts/tools/get_max_eval_metrics_from_wandb.py](scripts/tools/get_max_eval_metrics_from_wandb.py)
- [scripts/tools/validate_segmentation_metrics.py](scripts/tools/validate_segmentation_metrics.py)
- [tests/integration/eval/test_finetune.py](tests/integration/eval/test_finetune.py)
- [tests/integration/eval/test_probe.py](tests/integration/eval/test_probe.py)
- [tests/unit/eval/__init__.py](tests/unit/eval/__init__.py)
- [tests/unit/eval/test_metrics.py](tests/unit/eval/test_metrics.py)
- [tests/unit/internal/test_full_eval_sweep.py](tests/unit/internal/test_full_eval_sweep.py)

</details>



## Purpose and Scope

The Evaluation System provides infrastructure for measuring the quality of pretrained models on downstream tasks during and after training. It supports three evaluation modes: KNN classification (embedding-based), linear probing (frozen backbone with trainable head), and full model finetuning. The system is designed to run periodically during training via callbacks or standalone using evaluation sweep scripts.

This document covers the complete evaluation pipeline from task configuration to metric reporting. For information about the training system that invokes these evaluations, see [Training System](#5). For details on model architectures being evaluated, see [Model Architecture](#4).

## System Architecture

The evaluation system is implemented as a callback-based architecture that integrates with the training loop. The `DownstreamEvaluatorCallback` orchestrates multiple `DownstreamEvaluator` instances, each responsible for evaluating a single task.

```mermaid
graph TB
    subgraph "Training Loop"
        Trainer["Trainer<br/>(olmo_core)"]
    end
    
    subgraph "Callback System"
        DECallback["DownstreamEvaluatorCallback"]
        Evaluator1["DownstreamEvaluator<br/>(task_1)"]
        Evaluator2["DownstreamEvaluator<br/>(task_2)"]
        EvaluatorN["DownstreamEvaluator<br/>(task_n)"]
    end
    
    subgraph "Task Configuration"
        TaskConfig["DownstreamTaskConfig"]
        EvalMode["EvalMode<br/>(KNN, LINEAR_PROBE, FINETUNE)"]
        DatasetConfig["EvalDatasetConfig"]
    end
    
    subgraph "Execution Path"
        KNN["run_knn()"]
        LinearProbe["train_and_eval_probe()"]
        Finetune["run_finetune_eval()"]
    end
    
    subgraph "Data Pipeline"
        DataLoader["DataLoader"]
        GetEvalDataset["get_eval_dataset()"]
        GetEmbeddings["get_embeddings()"]
    end
    
    subgraph "Results"
        Metrics["val_score, test_score"]
        Bootstrap["bootstrap_stats"]
        WandB["W&B Logging"]
    end
    
    Trainer -->|"post_step() or pre_train()"| DECallback
    DECallback --> Evaluator1
    DECallback --> Evaluator2
    DECallback --> EvaluatorN
    
    Evaluator1 --> TaskConfig
    Evaluator2 --> TaskConfig
    TaskConfig --> EvalMode
    TaskConfig --> DatasetConfig
    
    Evaluator1 -->|"eval_mode=KNN"| KNN
    Evaluator1 -->|"eval_mode=LINEAR_PROBE"| LinearProbe
    Evaluator1 -->|"eval_mode=FINETUNE"| Finetune
    
    KNN --> GetEmbeddings
    LinearProbe --> GetEmbeddings
    Finetune --> DataLoader
    
    GetEvalDataset --> DataLoader
    DataLoader --> GetEmbeddings
    
    KNN --> Metrics
    LinearProbe --> Metrics
    Finetune --> Metrics
    
    Metrics --> Bootstrap
    Metrics --> WandB
```

**Sources:** [olmoearth_pretrain/train/callbacks/evaluator_callback.py:117-782](), [olmoearth_pretrain/train/callbacks/evaluator_callback.py:1-46]()

## Evaluation Modes

The system supports three evaluation modes defined in the `EvalMode` enum:

| Mode | Description | Use Case | Trainable Parameters |
|------|-------------|----------|---------------------|
| `KNN` | K-nearest neighbors on embeddings | Quick assessment, no training | None |
| `LINEAR_PROBE` | Train linear head on frozen features | Standard evaluation | Head only |
| `FINETUNE` | End-to-end finetuning | Maximum performance | All parameters |

```mermaid
graph LR
    subgraph "KNN Evaluation"
        KNN_Embed["Extract Embeddings"]
        KNN_Fit["Fit KNN Classifier"]
        KNN_Eval["Evaluate"]
        KNN_Embed --> KNN_Fit --> KNN_Eval
    end
    
    subgraph "Linear Probe"
        LP_Embed["Extract Embeddings"]
        LP_Train["Train Linear Head"]
        LP_Eval["Evaluate"]
        LP_Embed --> LP_Train --> LP_Eval
    end
    
    subgraph "Finetune"
        FT_Init["Initialize Head"]
        FT_Freeze["Freeze Backbone (20%)"]
        FT_Unfreeze["Unfreeze Backbone"]
        FT_Train["Train End-to-End"]
        FT_Eval["Evaluate"]
        FT_Init --> FT_Freeze --> FT_Unfreeze --> FT_Train --> FT_Eval
    end
```

The mode is selected either by explicitly setting `eval_mode` in the task configuration or automatically based on task type via `get_eval_mode()`.

**Sources:** [olmoearth_pretrain/train/callbacks/evaluator_callback.py:57-63](), [olmoearth_pretrain/evals/datasets/configs.py:29-30]()

## Downstream Evaluator Components

### DownstreamEvaluator Class

The `DownstreamEvaluator` class manages evaluation for a single task:

```mermaid
graph TB
    subgraph "DownstreamEvaluator"
        Init["__init__()<br/>evaluation_name, task, trainer"]
        GetLoader["_get_data_loader()<br/>split, batch_size, seed"]
        GetEmbed["_get_embeddings()<br/>data_loader, is_train"]
        ValEmbedProbe["_val_embed_probe()<br/>(KNN or Linear Probe)"]
        ValFinetune["_val_finetune()<br/>(Finetune)"]
        Val["val()<br/>Returns val_score, test_score, bootstrap_stats"]
    end
    
    Init --> GetLoader
    GetLoader --> GetEmbed
    GetEmbed --> ValEmbedProbe
    GetLoader --> ValFinetune
    ValEmbedProbe --> Val
    ValFinetune --> Val
```

Key methods:

- `_get_data_loader()`: Creates DataLoader for train/val/test splits with optional seeding for reproducibility.
- `_get_embeddings()`: Extracts embeddings using the encoder wrapped by `get_eval_wrapper()`.
- `_val_embed_probe()`: Executes KNN or linear probe evaluation paths.
- `_val_finetune()`: Executes full finetuning evaluation using `run_finetune_eval`.
- `val()`: Main entry point that routes to appropriate evaluation mode.

**Sources:** [olmoearth_pretrain/train/callbacks/evaluator_callback.py:120-432]()

### DownstreamTaskConfig

Configuration for a single evaluation task:

```python
@dataclass
class DownstreamTaskConfig:
    dataset: str  # Dataset identifier
    eval_mode: EvalMode | None = None
    
    # Common parameters
    num_workers: int = 8
    pooling_type: str = PoolingType.MEAN
    norm_stats_from_pretrained: bool = True
    patch_size: int = 4
    
    # LP / KNN
    embedding_batch_size: int = 128
    
    # LP
    probe_lr: float | None = None
    probe_batch_size: int = 32
    linear_probe_eval_interval: int = 50
    
    # FT
    ft_lr: float | None = None
    ft_batch_size: int = 32
    finetune_seed: int = 42
    
    # Training
    epochs: int = 50
    eval_interval: Duration = field(default_factory=lambda: Duration.epochs(1))
```

**Sources:** [olmoearth_pretrain/train/callbacks/evaluator_callback.py:66-115]()

## Evaluation Workflow

### KNN Evaluation Path

```mermaid
sequenceDiagram
    participant Evaluator as DownstreamEvaluator
    participant Loader as DataLoader
    participant Wrapper as get_eval_wrapper
    participant KNN as run_knn
    participant Result as Results
    
    Evaluator->>Loader: _get_data_loader("train")
    Evaluator->>Loader: _get_data_loader("valid")
    Evaluator->>Loader: _get_data_loader("test")
    
    Evaluator->>Wrapper: Get model wrapper
    Wrapper-->>Evaluator: Wrapped model
    
    Evaluator->>Evaluator: _get_embeddings(train_loader)
    Evaluator->>Evaluator: _get_embeddings(val_loader)
    Evaluator->>Evaluator: _get_embeddings(test_loader)
    
    Evaluator->>KNN: run_knn(embeddings, labels)
    KNN->>KNN: Fit KNN classifier
    KNN->>KNN: Evaluate on val/test
    KNN-->>Result: val_score, test_score, bootstrap_stats
    
    Result-->>Evaluator: Return results dict
```

**Sources:** [olmoearth_pretrain/train/callbacks/evaluator_callback.py:277-334](), [olmoearth_pretrain/evals/knn.py:40]()

### Linear Probe Path

The linear probe path trains a task-specific head (e.g., `ProbeType.LINEAR`) on top of frozen embeddings.

```mermaid
sequenceDiagram
    participant Evaluator as DownstreamEvaluator
    participant Probe as train_and_eval_probe
    participant Head as Linear Head
    participant Result as Results
    
    Evaluator->>Evaluator: Extract all embeddings
    Evaluator->>Probe: train_and_eval_probe(embeddings, labels)
    
    Probe->>Head: Initialize linear head
    
    loop Training Epochs
        Probe->>Head: Forward pass
        Probe->>Head: Compute loss
        Probe->>Head: Backward & optimize
    end
    
    Probe->>Probe: Evaluate on test set
    Probe-->>Result: val_score, test_score, bootstrap_stats
    
    Result-->>Evaluator: Return results dict
```

**Sources:** [olmoearth_pretrain/train/callbacks/evaluator_callback.py:277-334](), [olmoearth_pretrain/evals/linear_probe.py:41]()

### Finetune Path

The finetuning path uses a two-phase approach implemented in `run_finetune_eval`:

```mermaid
graph TB
    subgraph "Phase 1: Frozen Backbone (FREEZE_EPOCH_FRACTION)"
        FT1["Initialize BackboneWithHead"]
        FT2["Freeze backbone parameters"]
        FT3["Train head only"]
    end
    
    subgraph "Phase 2: Unfrozen Backbone"
        FT4["Unfreeze backbone"]
        FT5["Reduce LR by UNFREEZE_LR_FACTOR"]
        FT6["Train end-to-end"]
    end
    
    subgraph "Evaluation"
        FT7["Track best val metric"]
        FT8["Load best checkpoint"]
        FT9["Evaluate on test set"]
    end
    
    FT1 --> FT2 --> FT3 --> FT4 --> FT5 --> FT6
    FT3 -.->|"Validation"| FT7
    FT6 -.->|"Validation"| FT7
    FT7 --> FT8 --> FT9
```

Key implementation details:
- Uses `BackboneWithHead` wrapper that combines encoder with task-specific head.
- Backbone is frozen for the first portion of epochs (default `FREEZE_EPOCH_FRACTION` = 0.2).
- Uses `ReduceLROnPlateau` scheduler for optimization.
- Evaluates using `eval_cls` or `eval_seg` depending on `TaskType`.

**Sources:** [olmoearth_pretrain/evals/finetune/train.py:113-375](), [olmoearth_pretrain/evals/finetune/constants.py:26-32]()

## Task Configuration System

### Task Registries

Two dictionaries in `all_evals.py` define available tasks:

```python
# For KNN and Linear Probe evaluation
EVAL_TASKS = {
    "m_eurosat": DownstreamTaskConfig(...),
    "m_forestnet": DownstreamTaskConfig(...),
    "m_sa_crop_type": DownstreamTaskConfig(...),
    # ... more tasks
}

# For finetuning evaluation  
FT_EVAL_TASKS = {
    "m_eurosat": DownstreamTaskConfig(...),
    "m_bigearthnet": DownstreamTaskConfig(...),
    # ... more tasks
}
```

**Sources:** [olmoearth_pretrain/internal/all_evals.py:66-392]()

## Evaluation Sweeps

Evaluation sweeps run multiple evaluation configurations with different hyperparameters.

### Linear Probe / KNN Sweep

The `full_eval_sweep.py` script orchestrates hyperparameter sweeps across learning rates, normalization modes, and pooling types.

```python
LP_LRs = [1e-4, 5e-4, 1e-3, 5e-3, 1e-2, 5e-2, 1e-1, 5e-1]
Normalization_MODES = ["pre_trained", "dataset"]
pooling_types = [PoolingType.MEAN, PoolingType.MAX]
```

**Sources:** [olmoearth_pretrain/internal/full_eval_sweep.py:30-32]()

### Finetune Sweep

The `full_eval_sweep_finetune.py` script provides finetuning sweeps, utilizing `MODEL_PRESETS` to handle model-specific normalization logic.

```python
FT_LRS = [1e-4, 5e-4, 1e-3]

MODEL_PRESETS: dict[str, ModelPreset] = {
    "dino_v3": ModelPreset(per_task_overrides={"norm_method": "NormMethod.NORM_YES_CLIP_MIN_MAX_INT"}),
    "terramind": ModelPreset(supports_pretrained_normalizer=True),
    # ...
}
```

**Sources:** [olmoearth_pretrain/internal/full_eval_sweep_finetune.py:50-185]()

## Evaluation Metrics and Analysis

### Metric Classes

The system uses `EvalResult` to store metrics for both classification and segmentation tasks.

```python
@dataclass
class EvalResult:
    primary: float
    primary_metric: EvalMetric
    primary_metric_key: str
    metrics: dict[str, float]
```

Standard metrics include `ACCURACY`, `F1`, `MIOU`, and `MICRO_F1`. For segmentation, it also computes `OVERALL_ACC` and `MACRO_ACC`.

**Sources:** [olmoearth_pretrain/evals/metrics.py:13-160]()

### Analysis Tools

The script `get_max_eval_metrics_from_wandb.py` provides tools to aggregate and extract the best results from W&B sweeps, grouping by run prefix and identifying the maximum validation scores across different hyperparameter configurations.

**Sources:** [scripts/tools/get_max_eval_metrics_from_wandb.py:170-193]()

## Data Loading and Preprocessing

### Evaluation Dataset Loading

Data loaders for evaluation are created with deterministic seeding to ensure reproducibility.

```python
def _seed_worker(worker_id: int, base_seed: int) -> None:
    worker_seed = base_seed + worker_id
    random.seed(worker_seed)
    np.random.seed(worker_seed)
    torch.manual_seed(worker_seed)
```

**Sources:** [olmoearth_pretrain/train/callbacks/evaluator_callback.py:49-55]()

### Segmentation Post-processing

During segmentation evaluation (e.g., in `eval_seg`), the system handles spatial resolution mismatches between model outputs and ground truth labels using bilinear interpolation.

```python
if logits.shape[-2:] != label.shape[-2:]:
    logits = F.interpolate(
        logits.float(),
        size=label.shape[-2:],
        mode="bilinear",
        align_corners=True,
    )
```

**Sources:** [olmoearth_pretrain/evals/finetune/evaluate.py:81-87]()

---

