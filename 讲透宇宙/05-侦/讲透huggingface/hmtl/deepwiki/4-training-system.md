<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/hmtl · page 4 Training System · fetched 2026-10-26 -->

# Training System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [hmtl/training/sampler_multi_task_trainer.py](hmtl/training/sampler_multi_task_trainer.py)

</details>



This document covers the multi-task training infrastructure in HMTL, which enables simultaneous training of multiple NLP tasks with shared parameters and hierarchical dependencies. The training system handles task sampling, optimization coordination, metrics tracking, and model checkpointing across all supported tasks.

For detailed information about specific training components, see [Multi-Task Training](#4.1), [Model Evaluation](#4.2), and [Fine-tuning](#4.3).

## Architecture Overview

The HMTL training system is built around the `SamplerMultiTaskTrainer` class, which extends AllenNLP's training framework to support multi-task learning scenarios. The system coordinates training across multiple tasks while maintaining shared model parameters and task-specific optimization strategies.

### Core Training Architecture

```mermaid
graph TB
    subgraph "Training Controller"
        SMT["SamplerMultiTaskTrainer"]
        MT["MultiTaskTrainer (base)"]
        SMT --> MT
    end
    
    subgraph "Task Management"
        TL["task_list: List[Task]"]
        TI["_task_infos: Dict"]
        MI["_metric_infos: Dict"]
        
        SMT --> TL
        SMT --> TI
        SMT --> MI
    end
    
    subgraph "Training Components"
        OPT["_optimizers: Dict[str, Optimizer]"]
        SCH["_schedulers: Dict[str, LRScheduler]"]
        TRG["_tr_generators: Dict[str, Iterator]"]
        
        SMT --> OPT
        SMT --> SCH
        SMT --> TRG
    end
    
    subgraph "Sampling Strategy"
        SP["sampling_prob: List[float]"]
        SM["_sampling_method: str"]
        
        SMT --> SP
        SMT --> SM
    end
    
    subgraph "Logging & Persistence"
        TB["_tensorboard: TensorboardWriter"]
        CP["_save_checkpoint()"]
        
        SMT --> TB
        SMT --> CP
    end
```

Sources: [hmtl/training/sampler_multi_task_trainer.py:40-83]()

## Core Components

### SamplerMultiTaskTrainer Class

The `SamplerMultiTaskTrainer` is the primary training coordinator that manages multi-task learning through strategic task sampling. It inherits from `MultiTaskTrainer` and adds sampling-based task selection capabilities.

| Component | Type | Purpose |
|-----------|------|---------|
| `_sampling_method` | `str` | Controls task selection strategy ("uniform" or "proportional") |
| `_task_infos` | `Dict` | Tracks training statistics per task |
| `_metric_infos` | `Dict` | Manages validation metrics and early stopping |
| `_tr_generators` | `Dict` | Maintains data iterators for each task |

### Task Information Tracking

The trainer maintains detailed statistics for each task throughout training:

```mermaid
graph LR
    subgraph "Task Info Structure"
        TI["task_infos[task_name]"]
        NTB["n_tr_batches: int"]
        NVB["n_val_batches: int"]
        TNBT["total_n_batches_trained: int"]
        NBTE["n_batches_trained_this_epoch: int"]
        TLC["tr_loss_cum: float"]
        LL["last_log: float"]
        
        TI --> NTB
        TI --> NVB
        TI --> TNBT
        TI --> NBTE
        TI --> TLC
        TI --> LL
    end
    
    subgraph "Metric Info Structure"
        MI["metric_infos[task_name]"]
        VM["val_metric: str"]
        HIST["hist: List[float]"]
        OOP["is_out_of_patience: bool"]
        MLR["min_lr_hit: bool"]
        BEST["best: Tuple[int, Dict]"]
        
        MI --> VM
        MI --> HIST
        MI --> OOP
        MI --> MLR
        MI --> BEST
    end
```

Sources: [hmtl/training/sampler_multi_task_trainer.py:142-171]()

## Training Process Flow

The training process follows a structured epoch-based approach with task sampling and comprehensive validation:

### Main Training Loop

```mermaid
flowchart TD
    START["train() method entry"] --> INIT["Initialize task_infos and metric_infos"]
    INIT --> SETUP["Setup generators and sampling probabilities"]
    SETUP --> EPOCH["Begin epoch loop"]
    
    EPOCH --> TRAIN["Training phase"]
    TRAIN --> SAMPLE["Sample task using multinomial distribution"]
    SAMPLE --> FORWARD["Forward pass on selected task batch"]
    FORWARD --> BACKWARD["Backward pass and optimization"]
    BACKWARD --> UPDATE["Update task statistics and metrics"]
    UPDATE --> CHECK1{"All training batches processed?"}
    CHECK1 -->|No| SAMPLE
    CHECK1 -->|Yes| VAL["Validation phase"]
    
    VAL --> VALTASK["Validate each task sequentially"]
    VALTASK --> VALMETRICS["Compute validation metrics"]
    VALMETRICS --> PATIENCE["Check patience and update best models"]
    PATIENCE --> EARLYSTOP{"Early stopping conditions met?"}
    EARLYSTOP -->|No| CHECKPOINT["Save checkpoint"]
    EARLYSTOP -->|Yes| END["Training complete"]
    CHECKPOINT --> EPOCH
    
    END --> RETURN["Return training metrics"]
```

### Task Sampling Implementation

The trainer implements two sampling strategies for selecting which task to train on each iteration:

```mermaid
graph LR
    subgraph "Sampling Strategy Selection"
        SM["_sampling_method"]
        UNI["uniform"]
        PROP["proportional"]
        
        SM --> UNI
        SM --> PROP
    end
    
    subgraph "Uniform Sampling"
        USP["sampling_prob = [1/n_tasks] * n_tasks"]
        UNI --> USP
    end
    
    subgraph "Proportional Sampling"
        PSP["sampling_prob = [n_batches_i / total_batches]"]
        PROP --> PSP
    end
    
    subgraph "Task Selection"
        MN["np.random.multinomial(1, sampling_prob)"]
        IDX["task_idx = np.argmax(result)"]
        TSK["selected_task = task_list[task_idx]"]
        
        USP --> MN
        PSP --> MN
        MN --> IDX
        IDX --> TSK
    end
```

Sources: [hmtl/training/sampler_multi_task_trainer.py:188-193](), [hmtl/training/sampler_multi_task_trainer.py:224-227]()

## Task Sampling Strategies

### Uniform Sampling
- Each task has equal probability of selection: `1/n_tasks`
- Provides balanced training across all tasks regardless of dataset size
- Implementation: [hmtl/training/sampler_multi_task_trainer.py:189-190]()

### Proportional Sampling  
- Task selection probability proportional to training dataset size
- Larger datasets get more training iterations
- Formula: `P(task_i) = n_batches_i / total_n_batches`
- Implementation: [hmtl/training/sampler_multi_task_trainer.py:191-192]()

## Metrics and Validation

### Validation Process
The trainer performs comprehensive validation after each training epoch:

1. **Sequential Task Validation**: Each task is validated independently using its validation dataset
2. **Metric Computation**: Task-specific metrics are computed and aggregated  
3. **Best Model Tracking**: Best performing epoch is tracked for each task based on validation metric
4. **Early Stopping**: Training stops when all tasks reach patience limits or minimum learning rate

### Metric Tracking Structure

| Metric Category | Storage Location | Purpose |
|----------------|------------------|---------|
| Training Metrics | `all_tr_metrics[task_name]` | Current epoch training performance |
| Validation Metrics | `all_val_metrics[task_name]` | Current epoch validation performance |
| Metric History | `metric_infos[task_name]["hist"]` | Historical validation scores for patience checking |
| Best Performance | `metric_infos[task_name]["best"]` | Best epoch and corresponding metrics |

Sources: [hmtl/training/sampler_multi_task_trainer.py:328-396]()

## Checkpointing and Recovery

The training system implements comprehensive checkpointing for training recovery and model persistence:

### Checkpoint Components
- Model state dictionary
- Optimizer states for all tasks  
- Learning rate scheduler states
- Training metrics and task statistics
- Current epoch and global step counters

### Recovery Process
Training can be recovered from checkpoints using the `recover=True` parameter in the `train()` method. The system automatically restores all training state and continues from the last saved epoch.

Sources: [hmtl/training/sampler_multi_task_trainer.py:128-140](), [hmtl/training/sampler_multi_task_trainer.py:435]()

---

