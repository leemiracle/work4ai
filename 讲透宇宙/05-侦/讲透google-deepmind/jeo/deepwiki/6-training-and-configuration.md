<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/jeo · page 6 Training and Configuration · fetched 2026-10-26 -->

# Training and Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jeo/configs/config_utils.py](jeo/configs/config_utils.py)
- [jeo/train.py](jeo/train.py)

</details>



This page provides a comprehensive guide to configuring and running training experiments in Jeo. It covers the main training script, configuration system, command-line interface, and available utilities for experiment management.

For information about specific model architectures and task definitions, see [Models and Tasks](#5). For details about the evaluation system and metrics, see [Evaluation and Metrics](#7). For training utilities like checkpointing and distributed training, see [Training Utilities](#6.3).

## Overview

Jeo's training and configuration system is built around a central training script (`train.py`) that orchestrates the entire training process through a modular configuration system. The framework uses ML Collections for configuration management and provides flexible parameter parsing for experiment customization.

## Training Script Architecture

The main training script follows a structured approach with eight distinct sections that handle different aspects of the training lifecycle.

```mermaid
flowchart TD
    CLI["Command Line Interface<br/>--config, --workdir, --cleanup"]
    ConfigLoad["config_flags.DEFINE_config_file<br/>Configuration Loading"]
    
    subgraph "Training Script Sections"
        Setup["Section 1: Setup<br/>validate_and_update_config_inplace<br/>ThreadPool initialization"]
        Datasets["Section 2: Datasets<br/>input_pipeline.get_data<br/>start_input_pipeline"]
        ModelInit["Section 3: Model/Task/Optimizer<br/>model_mod.Model<br/>task_builder.from_config<br/>bv_optax.make"]
        UpdateFn["Section 4: Train Step<br/>update_fn (pmap)<br/>loss_fn, grads"]
        Checkpoint["Section 5: Checkpoint Init<br/>checkpointing.load_checkpoint<br/>train_utils.load"]
        PreLoop["Section 6: Pre-loop Setup<br/>flax.jax_utils.replicate<br/>eval_builder.from_config"]
        TrainLoop["Section 7: Train Loop<br/>update_fn execution<br/>run_evaluators"]
        PostLoop["Section 8: Post-loop<br/>pool.close<br/>finalize_and_cleanup"]
    end
    
    CLI --> ConfigLoad
    ConfigLoad --> Setup
    Setup --> Datasets
    Datasets --> ModelInit
    ModelInit --> UpdateFn
    UpdateFn --> Checkpoint
    Checkpoint --> PreLoop
    PreLoop --> TrainLoop
    TrainLoop --> PostLoop
```

Sources: [jeo/train.py:70-481]()

The training script uses a systematic approach where each section has specific responsibilities:

| Section | Purpose | Key Functions |
|---------|---------|---------------|
| Setup | Environment initialization, config validation | `validate_and_update_config_inplace`, `import_module` |
| Datasets | Data pipeline setup | `input_pipeline.get_data`, `start_input_pipeline` |
| Model/Task/Optimizer | Core component initialization | `task_builder.from_config`, `bv_optax.make` |
| Train Step | Update function definition | `update_fn` (pmapped), `loss_fn` |
| Checkpoint | Model state loading | `checkpointing.load_checkpoint`, `train_utils.load` |
| Pre-loop | Replication and evaluator setup | `flax.jax_utils.replicate`, `eval_builder.from_config` |
| Train Loop | Main training execution | Training step execution, evaluation |
| Post-loop | Cleanup and finalization | `pool.close`, `finalize_and_cleanup` |

Sources: [jeo/train.py:72-481]()

## Configuration System

Jeo uses a sophisticated configuration parsing system that supports both file-based configurations and command-line parameter overrides.

```mermaid
flowchart LR
    subgraph "Configuration Sources"
        ConfigFile["Configuration File<br/>.py files with get_config()"]
        CLIArgs["Command Line Arguments<br/>:key=value,flag syntax"]
    end
    
    subgraph "Parsing System"
        ParseArg["parse_arg()<br/>config_utils.py"]
        TypeConversion["Type Conversion<br/>get_type_with_default<br/>autotype"]
        ConfigDict["ml_collections.ConfigDict<br/>Type-safe configuration"]
    end
    
    subgraph "Standard Configurations"
        Transformers["TRANSFORMERS dict<br/>Predefined architectures"]
        FewShot["get_fewshot()<br/>Standard evaluation config"]
        LinearProbe["get_linear_probe_imagenet()<br/>Linear probe config"]
    end
    
    ConfigFile --> ParseArg
    CLIArgs --> ParseArg
    ParseArg --> TypeConversion
    TypeConversion --> ConfigDict
    
    Transformers --> ConfigDict
    FewShot --> ConfigDict
    LinearProbe --> ConfigDict
```

Sources: [jeo/configs/config_utils.py:47-108](), [jeo/configs/config_utils.py:19-39](), [jeo/configs/config_utils.py:144-212]()

### Parameter Parsing

The `parse_arg` function provides flexible configuration parsing with several supported formats:

```python
# Examples of configuration syntax
--config amazing.py:runlocal,schedule=long,res=128
--config amazing.py:res=128
--config amazing.py:runlocal              # Boolean flag
--config amazing.py:runlocal=False        # Explicit false
--config amazing.py:128                   # Unnamed first parameter
```

The parser supports automatic type conversion and strict boolean parsing for robust configuration handling.

Sources: [jeo/configs/config_utils.py:47-108]()

### Predefined Configurations

Jeo includes several standard configuration templates:

**Transformer Architectures**
```python
TRANSFORMERS = {
    "TinyToy": dict(num_layers=3, num_heads=1, mlp_dim=192, emb_dim=48),
    "B": dict(num_layers=12, num_heads=12, mlp_dim=3072, emb_dim=768),
    "L": dict(num_layers=24, num_heads=16, mlp_dim=4096, emb_dim=1024),
    # ... additional architectures
}
```

**Standard Evaluation Configurations**
- `get_fewshot()`: Few-shot learning evaluation setup
- `get_linear_probe_imagenet()`: ImageNet linear probing configuration

Sources: [jeo/configs/config_utils.py:19-39](), [jeo/configs/config_utils.py:144-176](), [jeo/configs/config_utils.py:178-212]()

## Command-Line Interface

The training script provides several command-line flags for experiment control:

| Flag | Type | Purpose |
|------|------|---------|
| `--config` | config_file | Training configuration file path |
| `--workdir` | string | Work unit directory for outputs |
| `--cleanup` | boolean | Delete workdir after successful completion |
| `--file_group` | string | Permission group for file storage |
| `--data_service_address` | string | tf.data service address |

Sources: [jeo/train.py:45-58]()

### Configuration File Integration

The training script uses ML Collections' `config_flags.DEFINE_config_file()` to load configuration files with lock protection to prevent accidental modification during training.

Sources: [jeo/train.py:45-46]()

## Training Flow and Lifecycle

The training process follows a well-defined lifecycle with clear separation of concerns:

```mermaid
flowchart TD
    subgraph "Initialization Phase"
        ConfigValidation["train_utils.validate_and_update_config_inplace<br/>Configuration validation"]
        DatasetSetup["input_pipeline.get_data<br/>Dataset initialization"]
        ModelSetup["Model/Task/Optimizer<br/>Component initialization"]
    end
    
    subgraph "Training Phase"
        UpdateFunction["update_fn (pmapped)<br/>Parallel training step"]
        LossComputation["loss_fn<br/>Task-specific loss calculation"]
        GradientUpdate["optax.apply_updates<br/>Parameter updates"]
    end
    
    subgraph "Monitoring Phase"
        Evaluation["run_evaluators<br/>Periodic evaluation"]
        Metrics["mw.measure<br/>Metrics logging"]
        EarlyStopping["early_stopper.should_stop<br/>Training termination"]
    end
    
    subgraph "Persistence Phase"
        Checkpointing["checkpointing.save_checkpoint<br/>Model state saving"]
        MetricsSaving["train_utils.save_metrics<br/>Results persistence"]
    end
    
    ConfigValidation --> DatasetSetup
    DatasetSetup --> ModelSetup
    ModelSetup --> UpdateFunction
    UpdateFunction --> LossComputation
    LossComputation --> GradientUpdate
    GradientUpdate --> Evaluation
    Evaluation --> Metrics
    Metrics --> EarlyStopping
    Evaluation --> Checkpointing
    Metrics --> MetricsSaving
    
    EarlyStopping -.->|Stop Signal| UpdateFunction
    GradientUpdate -.->|Continue| UpdateFunction
```

Sources: [jeo/train.py:80-463]()

### Key Training Components

**Update Function**: The core training step is implemented as a pmapped function that handles:
- Random number generation for stochastic components
- Mixup augmentation for segmentation tasks
- Loss computation and gradient calculation
- Parameter updates and state management

**Evaluation Integration**: Training integrates with the evaluation system through:
- `eval_builder.from_config()` for evaluator initialization
- `run_evaluators()` for periodic evaluation
- Early stopping based on evaluation metrics

**Checkpointing**: Model persistence is handled through:
- Automatic checkpoint saving at configured intervals
- Resume functionality from existing checkpoints
- Model initialization from pretrained weights

Sources: [jeo/train.py:256-301](), [jeo/train.py:361-381](), [jeo/train.py:308-332]()

## Integration with Framework Components

The training and configuration system serves as the central orchestrator that integrates all framework components:

```mermaid
graph TB
    subgraph "Configuration Layer"
        ConfigFiles["Configuration Files<br/>.py with get_config()"]
        ConfigUtils["config_utils.py<br/>parse_arg, TRANSFORMERS"]
    end
    
    subgraph "Training Orchestration"
        TrainScript["train.py<br/>Main training loop"]
        TrainUtils["train_utils.py<br/>Utilities and validation"]
    end
    
    subgraph "Core Components"
        InputPipeline["input_pipeline<br/>Data loading"]
        TaskBuilder["task_builder<br/>Task definitions"]
        Models["Model implementations<br/>BIT, ViT, MTSViT"]
        EvalBuilder["eval_builder<br/>Evaluation setup"]
        BVOptax["bv_optax<br/>Optimizer setup"]
    end
    
    subgraph "Infrastructure"
        Checkpointing["checkpointing<br/>Model persistence"]
        MetricWriters["metric_writers<br/>Logging infrastructure"]
        EarlyStopping["early_stopping<br/>Training control"]
    end
    
    ConfigFiles --> ConfigUtils
    ConfigUtils --> TrainScript
    TrainScript --> TrainUtils
    
    TrainScript --> InputPipeline
    TrainScript --> TaskBuilder
    TrainScript --> Models
    TrainScript --> EvalBuilder
    TrainScript --> BVOptax
    
    TrainScript --> Checkpointing
    TrainScript --> MetricWriters
    TrainScript --> EarlyStopping
```

Sources: [jeo/train.py:29-41](), [jeo/train.py:185-355]()

This architecture provides a clean separation between configuration management, training orchestration, and component integration, enabling flexible experimentation while maintaining code organization and reusability.

---

