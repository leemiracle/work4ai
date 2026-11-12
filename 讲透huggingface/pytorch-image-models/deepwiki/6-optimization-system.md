<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/pytorch-image-models · page 6 Optimization System · fetched 2026-10-26 -->

# Optimization System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [tests/test_optim.py](tests/test_optim.py)
- [timm/optim/_optim_factory.py](timm/optim/_optim_factory.py)
- [timm/optim/_param_groups.py](timm/optim/_param_groups.py)
- [timm/optim/kron.py](timm/optim/kron.py)
- [timm/optim/muon.py](timm/optim/muon.py)
- [timm/version.py](timm/version.py)

</details>



The Optimization System provides a comprehensive framework for creating, configuring, and managing optimizers used during model training. This system includes a factory pattern for optimizer creation, an extensive collection of state-of-the-art optimizer implementations, utilities for parameter grouping (such as layer-wise learning rate decay), and integration with experiment tracking tools.

For information about training scripts and infrastructure, see [Training Scripts and Infrastructure](#4.1). For details about learning rate scheduling, refer to the broader [Training and Evaluation](#4) system.

## Optimizer Factory Architecture

The optimization system is built around a central factory pattern that provides a unified interface for creating optimizers across the entire library.

```mermaid
graph TB
    subgraph "Factory Interface"
        CREATE_V2["create_optimizer_v2()"]
        CREATE["create_optimizer()"]
        LIST["list_optimizers()"]
        GET_CLASS["get_optimizer_class()"]
    end
    
    subgraph "Registry System"
        REGISTRY["OptimizerRegistry"]
        INFO["OptimInfo"]
        KWARGS["optimizer_kwargs()"]
    end
    
    subgraph "Parameter Grouping"
        LAYER_DECAY["param_groups_layer_decay()"]
        WEIGHT_DECAY["param_groups_weight_decay()"]
        AUTO_GROUP["auto_group_layers()"]
    end
    
    subgraph "Optimizer Instances"
        CUSTOM["Custom Optimizers<br/>AdaBelief, Adafactor, MADGRAD"]
        TORCH["PyTorch Optimizers<br/>Adam, AdamW, SGD"]
        WRAPPER["Optimizer Wrappers<br/>Lookahead"]
    end
    
    CREATE_V2 --> REGISTRY
    CREATE --> REGISTRY
    REGISTRY --> INFO
    REGISTRY --> KWARGS
    
    LAYER_DECAY --> CREATE_V2
    WEIGHT_DECAY --> CREATE_V2
    AUTO_GROUP --> CREATE_V2
    
    REGISTRY --> CUSTOM
    REGISTRY --> TORCH
    REGISTRY --> WRAPPER
    
    LIST --> REGISTRY
    GET_CLASS --> REGISTRY
```

Sources: [timm/optim/__init__.py:32-34](), [timm/optim/optim_factory.py:1-8]()

## Available Optimizer Implementations

The system provides an extensive collection of optimizer implementations, ranging from PyTorch built-ins to cutting-edge research optimizers.

### Core Optimizer Categories

```mermaid
graph LR
    subgraph "Adaptive Optimizers"
        ADABELIEF["AdaBelief"]
        ADAFACTOR["Adafactor"]
        ADAFACTOR_BV["AdafactorBigVision"]
        MADGRAD["MADGRAD"]
        NVNOVOGRAD["NvNovoGrad"]
    end
    
    subgraph "Adam Variants"
        ADAM["Adam"]
        ADAMW["AdamW"]
        ADAMP["AdamP"]
        ADAN["Adan"]
        NADAM["NAdam"]
        NADAMW["NAdamW"]
        RADAM["RAdam"]
    end
    
    subgraph "SGD Variants"
        SGD["SGD"]
        SGDP["SGDP"]
        SGDW["SGDW"]
        LARS["Lars"]
        LAMB["Lamb"]
    end
    
    subgraph "Specialized"
        LION["Lion"]
        MARS["Mars"]
        ADOPT["Adopt"]
        LAPROP["LaProp"]
        LOOKAHEAD["Lookahead<br/>(Wrapper)"]
    end
    
    subgraph "Legacy/Research"
        ADAMW_LEGACY["AdamWLegacy"]
        NADAM_LEGACY["NAdamLegacy"]
        RADAM_LEGACY["RAdamLegacy"]
        ADAHESSIAN["Adahessian"]
    end
```

Sources: [timm/optim/__init__.py:1-35]()

### Key Optimizer Features

| Optimizer | Key Features | Use Cases |
|-----------|-------------|-----------|
| `Adafactor` | Memory-efficient, factorized second moments | Large models, memory-constrained training |
| `AdaBelief` | Adapts step size by "belief" in gradient direction | General purpose, often better than Adam |
| `MADGRAD` | Momentumized adaptive dual averaging | Fast convergence, good generalization |
| `Lion` | Sign-based updates, memory efficient | Large scale training |
| `Lookahead` | Meta-optimizer wrapper for stability | Wraps other optimizers for stability |

Sources: [timm/optim/adafactor.py:21-44](), [timm/optim/adabelief.py:34-39](), [timm/optim/madgrad.py:25-53](), [timm/optim/lookahead.py:15-24]()

## Parameter Grouping System

The optimization system provides sophisticated parameter grouping utilities that allow different optimizer settings for different parts of the model.

```mermaid
graph TB
    subgraph "Parameter Grouping Functions"
        LAYER_DECAY["param_groups_layer_decay()"]
        WEIGHT_DECAY["param_groups_weight_decay()"]
        AUTO_GROUP["auto_group_layers()"]
        GROUP_PARAMS["group_parameters()"]
    end
    
    subgraph "Model Parameters"
        BACKBONE["Backbone Layers"]
        HEAD["Classification Head"]
        NORM["Normalization Layers"]
        BIAS["Bias Parameters"]
    end
    
    subgraph "Grouped Parameters"
        GROUP1["Group 1: High LR"]
        GROUP2["Group 2: Medium LR"]
        GROUP3["Group 3: Low LR"]
        GROUP4["Group 4: No Weight Decay"]
    end
    
    LAYER_DECAY --> BACKBONE
    LAYER_DECAY --> HEAD
    WEIGHT_DECAY --> NORM
    WEIGHT_DECAY --> BIAS
    
    BACKBONE --> GROUP1
    HEAD --> GROUP2
    NORM --> GROUP3
    BIAS --> GROUP4
    
    AUTO_GROUP --> LAYER_DECAY
    GROUP_PARAMS --> WEIGHT_DECAY
```

Sources: [timm/optim/__init__.py:34](), [timm/optim/optim_factory.py:4]()

### Layer-wise Learning Rate Decay

The `param_groups_layer_decay` function implements layer-wise learning rate decay, where deeper layers receive progressively smaller learning rates:

- **Purpose**: Apply different learning rates to different layers
- **Pattern**: `lr = base_lr * (decay_rate ^ layer_depth)`
- **Benefits**: Stabilizes training of very deep networks

### Weight Decay Grouping

The `param_groups_weight_decay` function separates parameters that should and shouldn't receive weight decay:

- **No Weight Decay**: Bias parameters, normalization layer parameters
- **Standard Weight Decay**: Weight matrices, embedding layers
- **Custom Patterns**: User-defined parameter matching

Sources: [timm/optim/optim_factory.py:4]()

## Optimizer Factory Usage Flow

The following diagram shows how the factory system creates configured optimizers from model parameters:

```mermaid
graph TD
    subgraph "Input"
        MODEL["model.named_parameters()"]
        CONFIG["Optimizer Config<br/>name, lr, weight_decay"]
        ARGS["Additional Args<br/>layer_decay, momentum"]
    end
    
    subgraph "Factory Process"
        CREATE_OPT["create_optimizer_v2()"]
        PARAM_GROUP["Parameter Grouping"]
        GET_CLASS["get_optimizer_class()"]
        INSTANTIATE["Optimizer.__init__()"]
    end
    
    subgraph "Output"
        OPTIMIZER["Configured Optimizer<br/>Ready for Training"]
    end
    
    MODEL --> CREATE_OPT
    CONFIG --> CREATE_OPT
    ARGS --> CREATE_OPT
    
    CREATE_OPT --> PARAM_GROUP
    PARAM_GROUP --> GET_CLASS
    GET_CLASS --> INSTANTIATE
    
    INSTANTIATE --> OPTIMIZER
    
    subgraph "Example Flow"
        EX_INPUT["'adamw', lr=1e-3<br/>layer_decay=0.8"]
        EX_GROUPS["[{params: early_layers, lr: 8e-4}<br/>{params: late_layers, lr: 1e-3}]"]
        EX_CLASS["torch.optim.AdamW"]
        EX_OPT["AdamW(param_groups, ...)"]
    end
    
    EX_INPUT --> EX_GROUPS
    EX_GROUPS --> EX_CLASS
    EX_CLASS --> EX_OPT
```

Sources: [timm/optim/__init__.py:32-34]()

## Experiment Tracking Integration

The optimization system integrates with experiment tracking tools to monitor training progress and optimizer behavior.

```mermaid
graph LR
    subgraph "Training Loop"
        TRAIN_STEP["Training Step"]
        METRICS["Compute Metrics"]
        UPDATE_SUMMARY["update_summary()"]
    end
    
    subgraph "Summary System"
        CSV_LOG["CSV Logging"]
        WANDB_LOG["Weights & Biases"]
        GET_OUTDIR["get_outdir()"]
    end
    
    subgraph "Logged Information"
        TRAIN_LOSS["train_loss"]
        EVAL_METRICS["eval_accuracy"]
        LR["learning_rate"]
        EPOCH["epoch"]
    end
    
    TRAIN_STEP --> METRICS
    METRICS --> UPDATE_SUMMARY
    
    UPDATE_SUMMARY --> CSV_LOG
    UPDATE_SUMMARY --> WANDB_LOG
    UPDATE_SUMMARY --> GET_OUTDIR
    
    TRAIN_LOSS --> UPDATE_SUMMARY
    EVAL_METRICS --> UPDATE_SUMMARY
    LR --> UPDATE_SUMMARY
    EPOCH --> UPDATE_SUMMARY
```

Sources: [timm/utils/summary.py:30-51]()

### Summary Logging Features

The `update_summary` function provides comprehensive logging capabilities:

- **CSV Output**: Structured logging to CSV files for analysis
- **Weights & Biases**: Real-time experiment tracking via `wandb.log()`
- **Metric Aggregation**: Combines training and evaluation metrics
- **Learning Rate Tracking**: Monitors optimizer learning rate changes

Key parameters tracked:
- `epoch`: Current training epoch
- `train_*`: Training metrics (loss, accuracy, etc.)
- `eval_*`: Evaluation metrics
- `lr`: Current learning rate

Sources: [timm/utils/summary.py:30-51]()

## Advanced Optimizer Features

### Mixed Precision Support

Many optimizers in the system support mixed precision training with automatic gradient scaling:

```python
# Example from Adafactor implementation
if grad.dtype in {torch.float16, torch.bfloat16}:
    grad = grad.float()
# ... optimizer computation in float32 ...
if p.dtype in {torch.float16, torch.bfloat16}:
    p.copy_(p_fp32)
```

Sources: [timm/optim/adafactor.py:143-144](), [timm/optim/adafactor.py:226-227]()

### Factorized Optimizers

Optimizers like `Adafactor` use memory-efficient factorization for large parameter tensors:

- **Row/Column Factorization**: Reduces memory for 2D+ tensors
- **Automatic Dimension Selection**: Heuristics for choosing factorization dimensions
- **Fallback to Full**: Uses full tensors when factorization isn't beneficial

Sources: [timm/optim/adafactor.py:100-115]()

### Optimizer Wrappers

The `Lookahead` optimizer demonstrates the wrapper pattern:

- **Base Optimizer**: Wraps any existing optimizer
- **Slow Weights**: Maintains a separate set of "slow" weights
- **Periodic Updates**: Updates slow weights every `k` steps

Sources: [timm/optim/lookahead.py:15-67]()