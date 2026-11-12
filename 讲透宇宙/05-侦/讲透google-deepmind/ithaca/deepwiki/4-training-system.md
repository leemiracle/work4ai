<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/ithaca · page 4 Training System · fetched 2026-10-26 -->

# Training System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ithaca/util/loss.py](ithaca/util/loss.py)
- [ithaca/util/optim.py](ithaca/util/optim.py)
- [train/experiment.py](train/experiment.py)

</details>



## Purpose and Scope

This document describes the training system for Ithaca models, including experiment orchestration, optimization strategies, loss functions, and data pipelines. The training system is built on the JAXline platform and implements distributed training with multi-task learning objectives.

For information about the model architecture being trained, see [Model Architecture](#3). For information about using trained models for inference, see [Inference System](#5). For details about data processing utilities, see [Data Processing Utilities](#6).

## System Architecture

The training system orchestrates the complete training workflow from data loading through model updates and evaluation. The system is centered around the `Experiment` class in [train/experiment.py](), which coordinates all training components.

```mermaid
graph TB
    subgraph "JAXline Platform"
        JAXLINE["jaxline.experiment.AbstractExperiment"]
    end
    
    subgraph "Experiment Class"
        EXP["Experiment"]
        INIT["__init__()"]
        STEP["step()"]
        EVAL["evaluate()"]
        
        EXP --> INIT
        EXP --> STEP
        EXP --> EVAL
    end
    
    subgraph "Model Components"
        MODEL["Model (from ithaca.models.model)"]
        PARAMS["_params (FrozenDict)"]
        FORWARD["forward.apply()"]
    end
    
    subgraph "Optimization"
        OPT_STATE["_opt_state"]
        OPT_INIT["_opt_init()"]
        OPT_UPDATE["_opt_update()"]
        LR_FN["_learning_rate_fn()"]
        GRAD_CLIP["adaptive_grad_clip()"]
    end
    
    subgraph "Loss Computation"
        LOSS_FN["_loss_fn()"]
        DATE_LOSS["date_loss_l1()"]
        REGION_LOSS["cross_entropy_label_smoothing_loss()"]
        MASK_LOSS["cross_entropy_label_smoothing_loss()"]
        NSP_LOSS["cross_entropy_mask_loss()"]
    end
    
    subgraph "Data Pipelines"
        TRAIN_INPUT["_train_input (iterator)"]
        EVAL_INPUT["_eval_input (iterator)"]
        BUILD_TRAIN["_build_train_input()"]
        BUILD_EVAL["_build_eval_input()"]
        DATALOADER["dataloader.loader_tf()"]
    end
    
    subgraph "Update Flow"
        UPDATE_FUNC["_update_func() (pmapped)"]
        GRAD_FN["jax.grad(_loss_fn)"]
        TREE_PSUM["jl_utils.tree_psum()"]
        APPLY_UPDATES["optax.apply_updates()"]
    end
    
    JAXLINE --> EXP
    
    INIT --> MODEL
    INIT --> OPT_INIT
    INIT --> LR_FN
    
    STEP --> TRAIN_INPUT
    STEP --> UPDATE_FUNC
    
    EVAL --> EVAL_INPUT
    EVAL --> FORWARD
    
    UPDATE_FUNC --> GRAD_FN
    GRAD_FN --> LOSS_FN
    LOSS_FN --> FORWARD
    LOSS_FN --> DATE_LOSS
    LOSS_FN --> REGION_LOSS
    LOSS_FN --> MASK_LOSS
    LOSS_FN --> NSP_LOSS
    
    UPDATE_FUNC --> TREE_PSUM
    UPDATE_FUNC --> OPT_UPDATE
    UPDATE_FUNC --> APPLY_UPDATES
    
    OPT_UPDATE --> LR_FN
    OPT_UPDATE --> GRAD_CLIP
    
    BUILD_TRAIN --> DATALOADER
    BUILD_EVAL --> DATALOADER
    DATALOADER --> TRAIN_INPUT
    DATALOADER --> EVAL_INPUT
    
    PARAMS --> FORWARD
    PARAMS --> APPLY_UPDATES
    OPT_STATE --> OPT_UPDATE
```

**Sources:** [train/experiment.py:50-679]()

## Training Loop Architecture

The training loop follows JAX's functional programming paradigm with explicit state management and distributed execution via `pmap`.

```mermaid
graph LR
    subgraph "Training Step (step method)"
        GET_BATCH["next(_train_input)"]
        UPDATE["_update_func() pmapped"]
        LOG["Return scalars"]
    end
    
    subgraph "_update_func (per device)"
        GRAD["jax.grad(_loss_fn)"]
        PSUM["tree_psum(grads)"]
        OPT["_opt_update(grads)"]
        APPLY["optax.apply_updates()"]
    end
    
    subgraph "_loss_fn"
        FWD["forward.apply()"]
        COMPUTE["Compute multi-task losses"]
        SCALE["Scale by device count"]
    end
    
    STATE_IN["(params, opt_state)"] --> UPDATE
    GET_BATCH --> UPDATE
    UPDATE --> UPDATE_OUT["(params', opt_state', scalars)"]
    
    UPDATE --> GRAD
    GRAD --> FWD
    FWD --> COMPUTE
    COMPUTE --> SCALE
    
    GRAD --> PSUM
    PSUM --> OPT
    OPT --> APPLY
    APPLY --> UPDATE_OUT
```

**Sources:** [train/experiment.py:131-143](), [train/experiment.py:335-368]()

### Training Step Execution

The `step()` method implements a single training iteration:

| Component | File:Lines | Description |
|-----------|-----------|-------------|
| `step()` | [train/experiment.py:131-143]() | Main training step, gets batch and calls update |
| `_initialize_train()` | [train/experiment.py:145-170]() | One-time initialization of params and optimizer state |
| `_update_func()` | [train/experiment.py:335-368]() | Pmapped function computing gradients and updating params |
| `_loss_fn()` | [train/experiment.py:198-333]() | Computes multi-task loss with all enabled objectives |

**Sources:** [train/experiment.py:131-368]()

## Optimizer Configuration

The optimization system uses Optax to compose gradient transformations including learning rate scheduling and gradient clipping.

```mermaid
graph TB
    subgraph "optimizer() method"
        CONFIG["config.optimizer"]
        CREATE_OPT["optax.[name]()"]
        CHAIN["optax.chain()"]
    end
    
    subgraph "Learning Rate Schedule"
        LR_FN["_learning_rate_fn"]
        WARMUP["linear_warmup_and_sqrt_decay()"]
        MAX_LR["max_lr from config"]
        WARMUP_STEPS["warmup_steps from config"]
    end
    
    subgraph "Gradient Clipping"
        CLIP_DECISION{"clip_adaptive?"}
        ADAPTIVE["adaptive_grad_clip()"]
        GLOBAL["optax.clip_by_global_norm()"]
    end
    
    subgraph "Optimizer Chain"
        CLIP_LAYER["Clipping Transformation"]
        OPT_LAYER["Optimizer (e.g., Adam)"]
        FINAL_CHAIN["optax.chain(clip, opt)"]
    end
    
    CONFIG --> CREATE_OPT
    CONFIG --> CLIP_DECISION
    
    LR_FN --> WARMUP
    MAX_LR --> WARMUP
    WARMUP_STEPS --> WARMUP
    WARMUP --> CREATE_OPT
    
    CLIP_DECISION -->|"Yes"| ADAPTIVE
    CLIP_DECISION -->|"No"| GLOBAL
    
    ADAPTIVE --> CLIP_LAYER
    GLOBAL --> CLIP_LAYER
    CLIP_LAYER --> FINAL_CHAIN
    CREATE_OPT --> OPT_LAYER
    OPT_LAYER --> FINAL_CHAIN
    
    FINAL_CHAIN --> RETURN["Return (init_fn, update_fn)"]
```

**Sources:** [train/experiment.py:110-122](), [train/experiment.py:85-89]()

### Learning Rate Scheduling

The system uses a composite learning rate schedule with linear warmup followed by square root decay:

```mermaid
graph LR
    GLOBAL_STEP["global_step"] --> LR_FN["linear_warmup_and_sqrt_decay()"]
    MAX_LR["max_lr"] --> LR_FN
    WARMUP["warmup_steps"] --> LR_FN
    
    LR_FN --> PHASE{"step < warmup?"}
    PHASE -->|"Yes"| LINEAR["lr = (max_lr / warmup) * step"]
    PHASE -->|"No"| SQRT["lr = max_lr * sqrt(warmup) / sqrt(step)"]
    
    LINEAR --> OUTPUT["learning_rate"]
    SQRT --> OUTPUT
```

The `linear_warmup_and_sqrt_decay()` function in [ithaca/util/optim.py:31-36]() implements this schedule:

$$\text{lr}(t) = \min\left(\frac{\text{max\_lr}}{\text{warmup\_steps}} \cdot t, \text{max\_lr} \cdot \sqrt{\frac{\text{warmup\_steps}}{t}}\right)$$

**Sources:** [ithaca/util/optim.py:31-36](), [train/experiment.py:85-89]()

### Gradient Clipping

Two gradient clipping strategies are available:

| Strategy | Function | Description |
|----------|----------|-------------|
| Global Norm | `optax.clip_by_global_norm()` | Clips gradients by global L2 norm |
| Adaptive | `adaptive_grad_clip()` | Clips unit-wise by ratio to parameter norm |

The adaptive gradient clipping from [ithaca/util/optim.py:140-167]() implements the method from Brock et al. (2021), clipping gradients to be at most `clipping * parameter_norm` on a per-unit basis.

**Sources:** [train/experiment.py:117-121](), [ithaca/util/optim.py:140-167]()

## Multi-Task Loss Functions

The training system optimizes four objectives simultaneously, with configurable weights and scheduling.

```mermaid
graph TB
    subgraph "Loss Computation Flow"
        BATCH["Batch Data"]
        FORWARD["forward.apply()"]
        PREDICTIONS["(date_pred, region_logits, mask_logits, nsp_logits)"]
    end
    
    subgraph "Date Loss"
        DATE_ENABLED{"date.enabled?"}
        DATE_L1["date_loss_l1()"]
        DATE_DIST["categorical_kl_divergence()"]
        DATE_WEIGHT["linear_weight() schedule"]
        DATE_TOTAL["date_loss"]
    end
    
    subgraph "Region Loss"
        REGION_ENABLED{"region.enabled?"}
        REGION_CE["cross_entropy_label_smoothing_loss()"]
        REGION_WEIGHT["linear_weight() schedule"]
        REGION_TOTAL["subregion_loss"]
    end
    
    subgraph "Mask Loss"
        MASK_ENABLED{"mask.enabled?"}
        MASK_CE["cross_entropy_label_smoothing_loss()"]
        MASK_WEIGHT["linear_weight() schedule"]
        MASK_TOTAL["mask_loss"]
    end
    
    subgraph "NSP Loss"
        NSP_ENABLED{"nsp.enabled?"}
        NSP_CE["cross_entropy_mask_loss()"]
        NSP_WEIGHT["linear_weight() schedule"]
        NSP_TOTAL["nsp_loss"]
    end
    
    BATCH --> FORWARD
    FORWARD --> PREDICTIONS
    
    PREDICTIONS --> DATE_ENABLED
    DATE_ENABLED -->|"Yes"| DATE_L1
    DATE_ENABLED -->|"Yes"| DATE_DIST
    DATE_L1 --> DATE_WEIGHT
    DATE_DIST --> DATE_WEIGHT
    DATE_WEIGHT --> DATE_TOTAL
    
    PREDICTIONS --> REGION_ENABLED
    REGION_ENABLED -->|"Yes"| REGION_CE
    REGION_CE --> REGION_WEIGHT
    REGION_WEIGHT --> REGION_TOTAL
    
    PREDICTIONS --> MASK_ENABLED
    MASK_ENABLED -->|"Yes"| MASK_CE
    MASK_CE --> MASK_WEIGHT
    MASK_WEIGHT --> MASK_TOTAL
    
    PREDICTIONS --> NSP_ENABLED
    NSP_ENABLED -->|"Yes"| NSP_CE
    NSP_CE --> NSP_WEIGHT
    NSP_WEIGHT --> NSP_TOTAL
    
    DATE_TOTAL --> SUM["Total Loss"]
    REGION_TOTAL --> SUM
    MASK_TOTAL --> SUM
    NSP_TOTAL --> SUM
    
    SUM --> SCALE["Scale by device_count"]
```

**Sources:** [train/experiment.py:198-333]()

### Loss Function Details

#### Date Loss

Date prediction uses two complementary losses:

| Loss Type | Function | Purpose |
|-----------|----------|---------|
| L1 Loss | `date_loss_l1()` | Penalizes predictions outside [date_min, date_max] range |
| Distribution Loss | `categorical_kl_divergence()` | Matches predicted distribution to ground truth |

The date loss in [train/experiment.py:230-269]() combines both components:
- **L1 component**: Computes mean predicted date from softmax distribution, penalizes deviation from valid range
- **Distribution component**: KL divergence between ground truth date distribution and predicted logits
- **Optional label smoothing**: Randomly perturbs ground truth distribution probabilities

**Sources:** [train/experiment.py:230-269](), [ithaca/util/loss.py:102-117](), [ithaca/util/loss.py:32-52]()

#### Region Loss

Region classification uses cross-entropy with label smoothing:

```python
# Implemented in train/experiment.py:272-285
subregion_loss = cross_entropy_label_smoothing_loss(
    subregion_logits,  # [batch, 84]
    subregion,         # [batch]
    label_smoothing=config.loss.region.label_smoothing
)
```

Label smoothing from [ithaca/util/loss.py:21-29]() converts one-hot labels to:
$$\text{label}_i = (1 - \epsilon) \cdot \mathbb{1}_{i=y} + \frac{\epsilon}{K}$$

where $\epsilon$ is the smoothing factor and $K$ is the number of classes (84 subregions).

**Sources:** [train/experiment.py:272-285](), [ithaca/util/loss.py:55-69]()

#### Masked Language Model Loss

The MLM loss computes cross-entropy only on masked positions:

```python
# Implemented in train/experiment.py:288-307
mask_loss = cross_entropy_label_smoothing_loss(
    mask_logits,      # [batch, seq_len, vocab_size]
    text_unmasked,    # [batch, seq_len]
    text_mask,        # [batch, seq_len] - binary mask
    label_smoothing=config.loss.mask.label_smoothing
)
```

The loss is masked to only consider positions marked for prediction, enabling efficient training on masked spans.

**Sources:** [train/experiment.py:288-307](), [ithaca/util/loss.py:55-69]()

#### Next Sentence Prediction Loss

NSP uses cross-entropy with masking to predict if sentence pairs are consecutive:

```python
# Implemented in train/experiment.py:310-327
nsp_loss = cross_entropy_mask_loss(
    nsp_logits,           # [batch, num_sentences, 2]
    next_sentence_label,  # [batch, num_sentences]
    next_sentence_mask    # [batch, num_sentences]
)
```

**Sources:** [train/experiment.py:310-327](), [ithaca/util/loss.py:78-81]()

### Loss Scheduling

Each loss component can be gradually introduced during training using `linear_weight()` from [ithaca/util/optim.py:21-28]():

```mermaid
graph LR
    STEP["global_step"]
    START["step_start"]
    END["step_end"]
    
    STEP --> COMPUTE["linear_weight()"]
    START --> COMPUTE
    END --> COMPUTE
    
    COMPUTE --> WEIGHT["weight ∈ [0, 1]"]
    WEIGHT --> SCALE["loss * weight"]
```

This allows curriculum learning where simpler tasks are learned before more complex ones.

**Sources:** [train/experiment.py:268-269](), [train/experiment.py:283-285](), [train/experiment.py:306-307](), [train/experiment.py:326-327](), [ithaca/util/optim.py:21-28]()

## Data Pipeline

The data pipeline loads PHI inscriptions and prepares batches for training and evaluation.

```mermaid
graph TB
    subgraph "Pipeline Components"
        DATASET_FILE["dataset_path (JSON file)"]
        CONFIG["config.dataset"]
        ALPHABET["GreekAlphabet"]
        REGION_MAP["region_map"]
    end
    
    subgraph "Data Loading"
        LOADER["dataloader.loader_tf()"]
        TFDS["TensorFlow Dataset"]
        BATCH_LOCAL["batch(local_device_count)"]
        ITERATOR["as_numpy(ds)"]
    end
    
    subgraph "Prefetching"
        PY_PREFETCH["py_prefetch()"]
        GPU_BUFFER["double_buffer_on_gpu()"]
    end
    
    subgraph "Batch Structure"
        TEXT_CHAR["text_char [devices, batch, seq]"]
        TEXT_WORD["text_word [devices, batch, seq]"]
        MASKS["text_mask, next_sentence_mask"]
        LABELS["region_sub_id, date_min/max, date_dist"]
    end
    
    DATASET_FILE --> LOADER
    CONFIG --> LOADER
    ALPHABET --> LOADER
    REGION_MAP --> LOADER
    
    LOADER --> TFDS
    TFDS --> BATCH_LOCAL
    BATCH_LOCAL --> ITERATOR
    
    ITERATOR --> PY_PREFETCH
    PY_PREFETCH --> GPU_BUFFER
    
    GPU_BUFFER --> TEXT_CHAR
    GPU_BUFFER --> TEXT_WORD
    GPU_BUFFER --> MASKS
    GPU_BUFFER --> LABELS
```

**Sources:** [train/experiment.py:171-196]()

### Batch Construction

The `_build_train_input()` method in [train/experiment.py:171-196]() creates the training data pipeline:

1. **Compute batch sizes**: Global batch size is divided across devices
2. **Load dataset**: Opens JSON dataset file and creates TensorFlow dataset
3. **Apply dataloader**: Calls `dataloader.loader_tf()` with per-device batch size
4. **Batch across devices**: Groups batches by local device count (for pmap)
5. **Convert to numpy**: Converts TensorFlow tensors to JAX-compatible numpy arrays
6. **Prefetch**: Applies Python-side prefetching and GPU double-buffering

The resulting iterator yields batches with shape `[num_local_devices, per_device_batch_size, ...]`.

**Sources:** [train/experiment.py:171-196]()

### Data Augmentation

Data augmentation is handled by the `dataloader` module (not shown in provided files). Based on the high-level diagrams, augmentation includes:
- Random mask span selection for MLM
- Random sentence swap for NSP
- Random word deletion and swapping for robustness

See [Data Loading and Augmentation](#4.5) for implementation details.

## Evaluation System

Evaluation runs periodically during training to assess model performance and select the best checkpoint.

```mermaid
graph TB
    subgraph "evaluate() method"
        CHECK_INIT{"_eval_input initialized?"}
        INIT_EVAL["_initialize_eval()"]
        EVAL_EPOCH["_eval_epoch()"]
        COMPUTE_SCORE["Compute composite score"]
        CHECK_BEST{"score > best_score?"}
        SAVE_OUTPUTS["Save outputs.pkl.bz2"]
        SAVE_SCORE["Save best_score.txt"]
        SAVE_MODEL["Copy model_log to best_model_log"]
    end
    
    subgraph "_eval_epoch()"
        ITER_BATCHES["Iterate eval batches"]
        EVAL_BATCH["_eval_batch()"]
        ACCUMULATE["Accumulate metrics"]
        NORMALIZE["Normalize by counts"]
    end
    
    subgraph "_eval_batch()"
        GET_PARAMS["Get first device params"]
        FWD_EVAL["forward.apply(is_training=False)"]
        COMPUTE_METRICS["Compute all losses & accuracies"]
        RETURN_SCALARS["Return scalars, outputs, model_log"]
    end
    
    CHECK_INIT -->|"No"| INIT_EVAL
    CHECK_INIT -->|"Yes"| EVAL_EPOCH
    INIT_EVAL --> EVAL_EPOCH
    
    EVAL_EPOCH --> ITER_BATCHES
    ITER_BATCHES --> EVAL_BATCH
    EVAL_BATCH --> GET_PARAMS
    GET_PARAMS --> FWD_EVAL
    FWD_EVAL --> COMPUTE_METRICS
    COMPUTE_METRICS --> RETURN_SCALARS
    RETURN_SCALARS --> ACCUMULATE
    ACCUMULATE --> NORMALIZE
    
    NORMALIZE --> COMPUTE_SCORE
    COMPUTE_SCORE --> CHECK_BEST
    CHECK_BEST -->|"Yes"| SAVE_OUTPUTS
    SAVE_OUTPUTS --> SAVE_SCORE
    SAVE_SCORE --> SAVE_MODEL
```

**Sources:** [train/experiment.py:377-434](), [train/experiment.py:588-674]()

### Composite Scoring

The evaluation metric combines multiple objectives:

```python
# From train/experiment.py:559-560
score = mask_accuracy + subregion_accuracy - date_l1_loss * 0.01
```

This composite score balances:
- **Mask accuracy**: Character restoration performance
- **Subregion accuracy**: Geographical attribution performance  
- **Date L1 loss**: Temporal attribution error (scaled down by 0.01)

The best model is selected based on this composite score, ensuring good performance across all tasks.

**Sources:** [train/experiment.py:559-560](), [train/experiment.py:665-667]()

### Checkpoint Management

The system maintains two types of checkpoints:

| Checkpoint Type | Location | Purpose |
|----------------|----------|---------|
| Regular | `checkpoint.pkl` | Periodic saves for resumption |
| Best Model | `best_model_log/` | Model with highest eval score |

The JAXline framework handles regular checkpointing automatically via the `CHECKPOINT_ATTRS` specification in [train/experiment.py:56-59](). Best model selection is handled by [train/experiment.py:409-429]().

**Sources:** [train/experiment.py:56-59](), [train/experiment.py:409-429]()

## Distributed Training

The system uses JAX's `pmap` for data parallelism across multiple devices (GPUs/TPUs).

```mermaid
graph TB
    subgraph "Device Distribution"
        DEVICES["jax.device_count()"]
        LOCAL_DEVICES["jax.local_device_count()"]
        GLOBAL_BATCH["global_batch_size"]
        PER_DEVICE["per_device_batch_size"]
    end
    
    subgraph "State Replication"
        BCAST["jl_utils.bcast_local_devices()"]
        RNG["_rng_key"]
        PARAMS_INIT["Initialize params on all devices"]
        OPT_INIT["Initialize opt_state on all devices"]
    end
    
    subgraph "Parallel Computation"
        PMAP_UPDATE["pmap(_update_func, axis_name='i')"]
        GRAD_COMPUTE["Compute grads per device"]
        TREE_PSUM["tree_psum(grads, axis_name='i')"]
        PMEAN["pmean(scalars, axis_name='i')"]
    end
    
    DEVICES --> PER_DEVICE
    GLOBAL_BATCH --> PER_DEVICE
    LOCAL_DEVICES --> BCAST
    
    BCAST --> RNG
    BCAST --> PARAMS_INIT
    PARAMS_INIT --> OPT_INIT
    
    PARAMS_INIT --> PMAP_UPDATE
    OPT_INIT --> PMAP_UPDATE
    
    PMAP_UPDATE --> GRAD_COMPUTE
    GRAD_COMPUTE --> TREE_PSUM
    TREE_PSUM --> PMEAN
```

**Sources:** [train/experiment.py:70](), [train/experiment.py:82-83](), [train/experiment.py:152-166](), [train/experiment.py:345-346](), [train/experiment.py:366]()

### Gradient Synchronization

Gradients are computed independently on each device, then synchronized using `tree_psum()`:

1. **Loss computation**: Each device computes `scaled_loss = loss / device_count` in [train/experiment.py:330]()
2. **Gradient computation**: `jax.grad()` computes gradients of scaled loss
3. **All-reduce**: `jl_utils.tree_psum(scaled_grads, axis_name='i')` sums gradients across devices
4. **Result**: Each device has the average gradient across all devices

This ensures gradient updates are equivalent to single-device training with a larger batch size.

**Sources:** [train/experiment.py:335-345]()

## Configuration Management

The training system uses `ml_collections.ConfigDict` for hierarchical configuration:

```mermaid
graph TB
    subgraph "Configuration Structure"
        ROOT["config"]
        
        MODEL["config.model"]
        OPTIMIZER["config.optimizer"]
        LOSS["config.loss"]
        DATASET["config.dataset"]
        TRAINING["config.training"]
        EVAL["config.evaluation"]
        ALPHABET["config.alphabet"]
    end
    
    subgraph "Optimizer Config"
        OPT_NAME["name (e.g., 'adam')"]
        OPT_KWARGS["kwargs (learning_rate, etc.)"]
        OPT_WARMUP["warmup"]
        OPT_CLIP["clip_level"]
        OPT_ADAPTIVE["clip_adaptive"]
    end
    
    subgraph "Loss Config"
        LOSS_DATE["date (enabled, type, weight_l1, weight_dist)"]
        LOSS_REGION["region (enabled, weight, label_smoothing)"]
        LOSS_MASK["mask (enabled, weight, label_smoothing)"]
        LOSS_NSP["nsp (enabled, weight)"]
    end
    
    ROOT --> MODEL
    ROOT --> OPTIMIZER
    ROOT --> LOSS
    ROOT --> DATASET
    ROOT --> TRAINING
    ROOT --> EVAL
    ROOT --> ALPHABET
    
    OPTIMIZER --> OPT_NAME
    OPTIMIZER --> OPT_KWARGS
    OPTIMIZER --> OPT_WARMUP
    OPTIMIZER --> OPT_CLIP
    OPTIMIZER --> OPT_ADAPTIVE
    
    LOSS --> LOSS_DATE
    LOSS --> LOSS_REGION
    LOSS --> LOSS_MASK
    LOSS --> LOSS_NSP
```

Key configuration sections accessed in the code:

| Config Path | Usage | File:Lines |
|------------|-------|-----------|
| `config.model` | Model architecture params | [train/experiment.py:81]() |
| `config.optimizer` | Optimizer and LR schedule | [train/experiment.py:111-122]() |
| `config.loss.date` | Date loss settings | [train/experiment.py:230-269]() |
| `config.loss.region` | Region loss settings | [train/experiment.py:272-285]() |
| `config.loss.mask` | MLM loss settings | [train/experiment.py:288-307]() |
| `config.loss.nsp` | NSP loss settings | [train/experiment.py:310-327]() |
| `config.dataset` | Data paths and settings | [train/experiment.py:185-193]() |
| `config.training.batch_size` | Global batch size | [train/experiment.py:174]() |
| `config.evaluation` | Eval settings | [train/experiment.py:92-93]() |
| `config.alphabet` | Vocabulary settings | [train/experiment.py:96-99]() |

**Sources:** [train/experiment.py:61-109]()

## Initialization and Warmup

Model initialization follows these steps:

1. **Create sample batch**: Get first batch from training data in [train/experiment.py:150]()
2. **Split RNG**: Create separate RNGs for params and dropout in [train/experiment.py:153]()
3. **Initialize parameters**: Call `forward.init()` with sample batch in [train/experiment.py:156-163]()
4. **Initialize optimizer**: Call `_opt_init()` with parameters in [train/experiment.py:165-166]()
5. **Setup data pipeline**: Create prefetched, GPU-buffered iterator in [train/experiment.py:168-169]()

The initialization is pmapped to create replicated state across all devices.

**Sources:** [train/experiment.py:145-169]()

## Training Metrics and Logging

The system logs comprehensive metrics during training:

| Metric | Type | Description |
|--------|------|-------------|
| `loss/train` | scalar | Total training loss |
| `loss/date` | scalar | Date prediction loss |
| `loss/subregion` | scalar | Region classification loss |
| `loss/mask` | scalar | Masked LM loss |
| `loss/nsp` | scalar | Next sentence prediction loss |
| `accuracy/subregion` | scalar | Region classification accuracy |
| `accuracy/mask` | scalar | Character restoration accuracy |
| `accuracy/nsp` | scalar | Next sentence prediction accuracy |
| `opt/learning_rate` | scalar | Current learning rate |
| `opt/grad_norm` | scalar | Global norm of gradients |
| `opt/param_norm` | scalar | Global norm of parameters |

Metrics are computed per-device, then averaged across devices using `jax.lax.pmean()` in [train/experiment.py:366]().

**Sources:** [train/experiment.py:353-366]()

## Summary

The training system implements a sophisticated distributed training pipeline with:

- **Multi-task learning**: Four complementary objectives (date, region, mask, NSP)
- **Flexible optimization**: Configurable LR schedules and gradient clipping
- **Efficient data loading**: Prefetched, GPU-buffered TensorFlow datasets
- **Distributed execution**: Data parallelism via JAX pmap
- **Automatic checkpointing**: JAXline-managed state persistence
- **Best model selection**: Composite scoring across tasks

For detailed information about specific subsystems, see:
- [Training Overview](#4.1) for the high-level workflow
- [Experiment Configuration](#4.2) for config management
- [Optimization and Schedulers](#4.3) for LR schedules and gradient clipping
- [Loss Functions](#4.4) for detailed loss computation
- [Data Loading and Augmentation](#4.5) for the data pipeline
- [Evaluation and Checkpointing](#4.6) for evaluation and model selection

**Sources:** [train/experiment.py:1-679](), [ithaca/util/optim.py:1-168](), [ithaca/util/loss.py:1-118]()

---

