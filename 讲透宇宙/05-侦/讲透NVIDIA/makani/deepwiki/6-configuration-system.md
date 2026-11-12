<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/makani · page 6 Configuration System · fetched 2026-10-26 -->

# Configuration System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [config/README.md](config/README.md)
- [config/afnonet.yaml](config/afnonet.yaml)
- [config/sfnonet.yaml](config/sfnonet.yaml)

</details>



The Configuration System provides a comprehensive YAML-based parameter management framework for defining model architectures, training hyperparameters, data processing settings, and deployment options. This system enables reproducible experiments and easy configuration management across different model types and training scenarios.

For information about model architectures and their implementations, see [Neural Network Models](#4). For details about the training and inference workflows that consume these configurations, see [Training and Inference Engines](#3.1).

## Configuration Architecture

The configuration system is built around YAML files that use anchors and references to enable inheritance and reduce duplication. The main configuration files are organized by model type and provide both base configurations and specialized variants.

```mermaid
graph TB
    subgraph "Configuration Files"
        BASE_YAML["config/*.yaml<br/>Configuration Files"]
        AFNO_YAML["afnonet.yaml<br/>AFNO Configurations"]
        SFNO_YAML["sfnonet.yaml<br/>SFNO Configurations"] 
        VIT_YAML["vit.yaml<br/>ViT Configurations"]
        ICML_YAML["icml_models.yaml<br/>Dataloader Configs"]
    end
    
    subgraph "Configuration Structure"
        BASE_CONFIG["BASE_CONFIG<br/>Anchor Definition"]
        INHERITED_CONFIGS["Inherited Configs<br/><<: *BASE_CONFIG"]
        SPECIALIZED_CONFIGS["Specialized Configs<br/>Override Parameters"]
    end
    
    subgraph "Configuration Categories"
        DATA_CONFIG["Data Configuration<br/>Paths, Statistics, Channels"]
        MODEL_CONFIG["Model Configuration<br/>Architecture, Hyperparameters"]
        TRAINING_CONFIG["Training Configuration<br/>Optimization, Scheduling"]
        INFRA_CONFIG["Infrastructure Configuration<br/>Distributed, Logging"]
    end
    
    subgraph "Consumption"
        TRAIN_CLI["makani.train<br/>Training Engine"]
        INFERENCE_CLI["makani.inference<br/>Inference Engine"]
        CONFIG_LOADER["Configuration Loader<br/>YAML Parser"]
    end
    
    BASE_YAML --> AFNO_YAML
    BASE_YAML --> SFNO_YAML
    BASE_YAML --> VIT_YAML
    BASE_YAML --> ICML_YAML
    
    AFNO_YAML --> BASE_CONFIG
    SFNO_YAML --> BASE_CONFIG
    BASE_CONFIG --> INHERITED_CONFIGS
    INHERITED_CONFIGS --> SPECIALIZED_CONFIGS
    
    BASE_CONFIG --> DATA_CONFIG
    BASE_CONFIG --> MODEL_CONFIG
    BASE_CONFIG --> TRAINING_CONFIG
    BASE_CONFIG --> INFRA_CONFIG
    
    CONFIG_LOADER --> TRAIN_CLI
    CONFIG_LOADER --> INFERENCE_CLI
    AFNO_YAML --> CONFIG_LOADER
    SFNO_YAML --> CONFIG_LOADER
```

Sources: [config/README.md:1-19](), [config/afnonet.yaml:1-147](), [config/sfnonet.yaml:1-175]()

## Configuration Structure and Inheritance

The configuration system uses YAML anchors (`&`) and references (`<<: *`) to implement inheritance patterns. Base configurations define common parameters, while specialized configurations override specific settings for different model variants or experimental scenarios.

```mermaid
graph TD
    subgraph "YAML Inheritance Pattern"
        ANCHOR["&BASE_CONFIG<br/>Anchor Definition"]
        REFERENCE["<<: *BASE_CONFIG<br/>Reference Inheritance"]
        OVERRIDE["param: new_value<br/>Parameter Override"]
    end
    
    subgraph "AFNO Configuration Hierarchy"
        AFNO_BASE["full_field: &BASE_CONFIG<br/>Base AFNO Configuration"]
        AFNO_26CH["afno_26ch_arxiv_network: &AFNO_26CH<br/>26-Channel Variant"]
        AFNO_FINETUNE["afno_26ch_arxiv_network_finetune<br/>Finetuning Configuration"]
        AFNO_TEST["afno_26ch_arxiv_network_test_config<br/>Test Configuration"]
    end
    
    subgraph "SFNO Configuration Hierarchy"
        SFNO_BASE["base_config: &BASE_CONFIG<br/>Base SFNO Configuration"]
        SFNO_73CH["base_73chq: &BASELINE_73CHQ<br/>73-Channel Baseline"]
        SFNO_FINETUNE["base_73chq_finetune<br/>Finetuning Configuration"]
        SFNO_BEST["sfno_linear_73chq_sc3_layers8_edim384_wstgl2<br/>Best Single GPU Model"]
    end
    
    ANCHOR --> REFERENCE
    REFERENCE --> OVERRIDE
    
    AFNO_BASE --> AFNO_26CH
    AFNO_26CH --> AFNO_FINETUNE
    AFNO_26CH --> AFNO_TEST
    
    SFNO_BASE --> SFNO_73CH
    SFNO_73CH --> SFNO_FINETUNE
    SFNO_73CH --> SFNO_BEST
```

Sources: [config/afnonet.yaml:1-2, 108-147](), [config/sfnonet.yaml:1-2, 137-175]()

## Configuration Categories

### Data Configuration

Data configuration parameters define input/output paths, statistics files for normalization, and data processing options.

| Parameter Category | Key Parameters | Purpose |
|-------------------|---------------|---------|
| **Data Paths** | `train_data_path`, `valid_data_path`, `inf_data_path` | Define dataset locations |
| **Metadata** | `metadata_json_path`, `img_shape_x`, `img_shape_y` | Dataset structure information |
| **Statistics** | `global_means_path`, `global_stds_path`, `time_means_path` | Normalization statistics |
| **Channels** | `channel_names`, `normalization` | Variable selection and preprocessing |

### Model Architecture Configuration

Model configuration parameters define the neural network architecture and its hyperparameters.

| Parameter Category | AFNO Parameters | SFNO Parameters | Purpose |
|-------------------|----------------|----------------|---------|
| **Network Type** | `nettype: "AFNOv1"` | `nettype: "SFNO"` | Model architecture selection |
| **Core Architecture** | `embed_dim`, `num_blocks`, `patch_size` | `embed_dim`, `num_layers`, `scale_factor` | Network dimensions |
| **Spectral Processing** | `hard_thresholding_fraction` | `filter_type`, `sht_grid_type`, `complex_activation` | Spectral transform configuration |
| **Grid Configuration** | `model_grid_type: "equiangular"` | `model_grid_type`, `sht_grid_type` | Spatial discretization |

### Training Configuration

Training configuration parameters control the optimization process, scheduling, and training dynamics.

```mermaid
graph LR
    subgraph "Optimization Parameters"
        OPTIMIZER["optimizer_type<br/>Adam/AdamW"]
        LR["lr<br/>Learning Rate"]
        WEIGHT_DECAY["weight_decay<br/>Regularization"]
        GRAD_NORM["optimizer_max_grad_norm<br/>Gradient Clipping"]
    end
    
    subgraph "Scheduler Parameters"
        SCHEDULER["scheduler<br/>CosineAnnealingLR/StepLR"]
        SCHEDULER_PARAMS["scheduler_T_max<br/>scheduler_step_size<br/>scheduler_gamma"]
        WARMUP["lr_warmup_steps<br/>Warmup Configuration"]
    end
    
    subgraph "Training Dynamics"
        BATCH_SIZE["batch_size<br/>Batch Configuration"]
        MAX_EPOCHS["max_epochs<br/>Training Duration"]
        LOSS["loss<br/>Loss Function"]
        PREDICTION["prediction_type<br/>prediction_length"]
    end
    
    OPTIMIZER --> SCHEDULER
    SCHEDULER --> SCHEDULER_PARAMS
    SCHEDULER_PARAMS --> WARMUP
    
    BATCH_SIZE --> MAX_EPOCHS
    MAX_EPOCHS --> LOSS
    LOSS --> PREDICTION
```

Sources: [config/afnonet.yaml:20-26, 51-52, 88-92](), [config/sfnonet.yaml:42-58, 115-118]()

## Model-Specific Configuration Patterns

### AFNO Configuration Pattern

AFNO configurations focus on patch-based processing with adaptive Fourier filtering.

Key AFNO-specific parameters:
- `nettype: "AFNOv1"` or `"AFNO"` - Model variant selection
- `patch_size: [8,8]` - Spatial patch dimensions
- `num_blocks: 8` - Number of AFNO blocks
- `embed_dim: 768` - Feature embedding dimension
- `nested_skip_fno: !!bool True` - Skip connection configuration

### SFNO Configuration Pattern

SFNO configurations emphasize spherical harmonic transforms and spectral filtering.

Key SFNO-specific parameters:
- `nettype: "SFNO"` - Spherical Fourier Neural Operator
- `sht_grid_type: "legendre-gauss"` - Spherical harmonic grid
- `filter_type: "linear"` - Spectral filter type
- `scale_factor: 3` - Spectral mode scaling
- `complex_activation: "real"` - Complex number handling
- `operator_type: "dhconv"` - Convolution operator type

```mermaid
graph TB
    subgraph "AFNO Configuration Flow"
        AFNO_NET["nettype: AFNOv1"]
        AFNO_PATCH["patch_size: [8,8]"]
        AFNO_BLOCKS["num_blocks: 8"]
        AFNO_EMBED["embed_dim: 768"]
        AFNO_SKIP["nested_skip_fno: true"]
    end
    
    subgraph "SFNO Configuration Flow"
        SFNO_NET["nettype: SFNO"]
        SFNO_GRID["sht_grid_type: legendre-gauss"]
        SFNO_FILTER["filter_type: linear"]
        SFNO_SCALE["scale_factor: 3"]
        SFNO_ACTIVATION["complex_activation: real"]
    end
    
    subgraph "Common Architecture Parameters"
        EMBED_DIM["embed_dim"]
        NORM_LAYER["normalization_layer: instance_norm"]
        GRID_TYPE["model_grid_type: equiangular"]
        THRESHOLD["hard_thresholding_fraction"]
    end
    
    AFNO_NET --> AFNO_PATCH
    AFNO_PATCH --> AFNO_BLOCKS
    AFNO_BLOCKS --> AFNO_EMBED
    AFNO_EMBED --> AFNO_SKIP
    
    SFNO_NET --> SFNO_GRID
    SFNO_GRID --> SFNO_FILTER
    SFNO_FILTER --> SFNO_SCALE
    SFNO_SCALE --> SFNO_ACTIVATION
    
    AFNO_EMBED --> EMBED_DIM
    SFNO_NET --> EMBED_DIM
    EMBED_DIM --> NORM_LAYER
    NORM_LAYER --> GRID_TYPE
    GRID_TYPE --> THRESHOLD
```

Sources: [config/afnonet.yaml:52-59](), [config/sfnonet.yaml:24-40]()

## Advanced Configuration Features

### Channel and Variable Configuration

The configuration system supports flexible channel selection and variable management:

- `channel_names` - List of atmospheric variables to include
- `add_grid`, `add_zenith`, `add_orography`, `add_landmask` - Additional input channels
- `normalization` - Data normalization strategy (`"zscore"`, `"minmax"`, `"none"`)

### Distributed Training Configuration

Parameters for multi-GPU and multi-node training:

- `wireup_info: "mpi"` - Process communication method
- `wireup_store: "tcp"` - Communication backend
- `num_data_workers` - Data loading parallelism
- Spatial and model parallelism settings (handled by distributed framework)

### Logging and Monitoring Configuration

Comprehensive logging and experiment tracking:

- `log_to_wandb: !!bool True` - Weights & Biases integration
- `wandb_project`, `wandb_entity`, `wandb_group` - W&B organization
- `save_checkpoint: "legacy"` - Checkpoint format and frequency
- `log_video: 20` - Visualization logging interval

Sources: [config/afnonet.yaml:28-32, 64-79, 83-87, 100-106](), [config/sfnonet.yaml:63-68, 91-106, 109-129]()

## Configuration Usage Patterns

### Training Configuration

Training workflows consume configurations to set up:
1. Model architecture parameters via model registry
2. Data loading and preprocessing pipelines
3. Optimization and scheduling strategies
4. Distributed training coordination
5. Logging and checkpointing behavior

### Inference Configuration

Inference workflows use configurations for:
1. Model loading and architecture reconstruction
2. Data preprocessing consistency
3. Prediction parameters (`prediction_type`, `prediction_length`)
4. Output format and saving options

### Finetuning Configuration

Specialized finetuning configurations modify base configurations:
- `finetune: !!bool True` - Enable finetuning mode
- `pretrained_checkpoint_path` - Path to pretrained weights
- Reduced learning rates and shorter training schedules
- Modified scheduler parameters for transfer learning

Sources: [config/afnonet.yaml:115-122, 140-147](), [config/sfnonet.yaml:140-147]()

---

