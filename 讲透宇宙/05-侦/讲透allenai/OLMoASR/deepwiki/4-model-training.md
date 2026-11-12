<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/OLMoASR · page 4 Model Training · fetched 2026-10-26 -->

# Model Training

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [requirements/requirements-train.txt](requirements/requirements-train.txt)
- [scripts/README.md](scripts/README.md)

</details>



This page covers the complete model training system in OLMoASR, including training environment setup, distributed training strategies, and the various training scripts available. The training system supports multiple approaches for different data types and scales, from small-scale DDP training to large-scale FSDP training with various pre-existing datasets.

For information about setting up the training environment and dependencies, see [Training Environment & Dependencies](#4.1). For details on the specific training scripts and distributed strategies, see [Training Scripts & Distributed Strategies](#4.2). For data preparation before training, see [Data Processing Pipeline](#3).

## Training System Architecture

The OLMoASR training system is designed around multiple training strategies that can handle different scales of data and computational resources. The system provides specialized training scripts for different data formats and training paradigms.

```mermaid
flowchart TB
    subgraph "Training Data Sources"
        OLMO_DATA["OLMoASR Processed Data<br/>JSONL Format"]
        OWSM_DATA["OWSM-Eng Dataset<br/>External Format"]
        YODAS_DATA["YODAS-Eng Dataset<br/>External Format"]
    end
    
    subgraph "Training Scripts"
        TRAIN_FSDP["train_fsdp_timestamps.py<br/>FSDP Strategy"]
        TRAIN_DDP["train_timestamps.py<br/>DDP Strategy"] 
        TRAIN_OWSM["train_owsm.py<br/>OWSM Data Pipeline"]
        TRAIN_YODAS["train_yodas.py<br/>YODAS Data Pipeline"]
    end
    
    subgraph "Training Configuration"
        JOB_CONFIGS["configs/job_configs/training/<br/>Training Job Configs"]
        MODEL_CONFIG["Model Architecture<br/>Whisper-based Config"]
        OPTIM_CONFIG["Optimizer Settings<br/>AdamW + Scheduling"]
    end
    
    subgraph "Training Infrastructure" 
        TORCH_DDP["PyTorch DDP<br/>Multi-GPU Training"]
        TORCH_FSDP["PyTorch FSDP<br/>Memory-Efficient Training"]
        WANDB_LOG["Weights & Biases<br/>Experiment Tracking"]
        MIXED_PREC["Mixed Precision<br/>FP16/BF16 Training"]
    end
    
    subgraph "Model Outputs"
        CHECKPOINTS["Model Checkpoints<br/>*.pt Files"]
        TRAIN_LOGS["Training Logs<br/>Loss & Metrics"]
        WANDB_RUNS["W&B Experiment Runs<br/>Visualization & Tracking"]
    end
    
    OLMO_DATA --> TRAIN_FSDP
    OLMO_DATA --> TRAIN_DDP
    OWSM_DATA --> TRAIN_OWSM
    YODAS_DATA --> TRAIN_YODAS
    
    JOB_CONFIGS --> TRAIN_FSDP
    JOB_CONFIGS --> TRAIN_DDP
    JOB_CONFIGS --> TRAIN_OWSM
    JOB_CONFIGS --> TRAIN_YODAS
    
    MODEL_CONFIG --> TRAIN_FSDP
    MODEL_CONFIG --> TRAIN_DDP
    OPTIM_CONFIG --> TRAIN_FSDP
    OPTIM_CONFIG --> TRAIN_DDP
    
    TRAIN_FSDP --> TORCH_FSDP
    TRAIN_DDP --> TORCH_DDP
    TRAIN_OWSM --> TORCH_DDP
    TRAIN_YODAS --> TORCH_DDP
    
    TORCH_DDP --> MIXED_PREC
    TORCH_FSDP --> MIXED_PREC
    
    TRAIN_FSDP --> WANDB_LOG
    TRAIN_DDP --> WANDB_LOG
    TRAIN_OWSM --> WANDB_LOG
    TRAIN_YODAS --> WANDB_LOG
    
    TORCH_DDP --> CHECKPOINTS
    TORCH_FSDP --> CHECKPOINTS
    WANDB_LOG --> TRAIN_LOGS
    WANDB_LOG --> WANDB_RUNS
```

Sources: [scripts/README.md:20-27]()

## Training Dependencies and Environment

The training system requires a comprehensive set of dependencies for deep learning, data processing, audio handling, and experiment tracking. The training-specific requirements are managed separately from the base package requirements.

### Core Training Dependencies

| Category | Dependencies | Purpose |
|----------|--------------|---------|
| Deep Learning | `torch`, `torchaudio` | PyTorch ecosystem for model training |
| Data Processing | `datasets==2.21.0`, `webdataset` | HuggingFace datasets and WebDataset format |
| Audio Processing | `librosa`, `soundfile` | Audio file reading and processing |
| Experiment Tracking | `wandb==0.18.7` | Weights & Biases integration |
| Evaluation | `jiwer` | Word Error Rate calculation |
| Base Model | `openai-whisper` | Whisper model architecture |
| Performance | `torch-tb-profiler`, `ray` | Training profiling and distributed computing |
| Utilities | `fire`, `tqdm`, `regex`, `scipy`, `numpy` | CLI interfaces and utilities |

```mermaid
graph TB
    subgraph "Training Requirements Stack"
        BASE_TORCH["torch + torchaudio<br/>Core Training Framework"]
        WHISPER_BASE["openai-whisper<br/>Base Model Architecture"] 
        DATA_STACK["datasets + webdataset<br/>Data Loading Pipeline"]
        AUDIO_STACK["librosa + soundfile<br/>Audio Processing"]
        TRACK_STACK["wandb + torch-tb-profiler<br/>Experiment Tracking"]
        UTIL_STACK["fire + tqdm + regex + scipy<br/>Utilities & CLI"]
    end
    
    subgraph "Training Script Integration"
        TRAIN_SCRIPTS["scripts/training/*.py<br/>Training Entry Points"]
        OLMO_MODEL["olmoasr/model.py<br/>Training Model Class"]
        PREPROCESS["olmoasr/preprocess.py<br/>Data Preprocessing"]
    end
    
    BASE_TORCH --> TRAIN_SCRIPTS
    WHISPER_BASE --> OLMO_MODEL
    DATA_STACK --> PREPROCESS
    AUDIO_STACK --> PREPROCESS
    TRACK_STACK --> TRAIN_SCRIPTS
    UTIL_STACK --> TRAIN_SCRIPTS
    
    OLMO_MODEL --> TRAIN_SCRIPTS
    PREPROCESS --> TRAIN_SCRIPTS
```

Sources: [requirements/requirements-train.txt:1-19]()

## Training Script Overview

The OLMoASR system provides four distinct training scripts, each optimized for different training scenarios and data formats. These scripts handle different distributed training strategies and dataset formats.

### Training Script Comparison

| Script | Distributed Strategy | Target Dataset | Key Features |
|--------|---------------------|----------------|--------------|
| `train_fsdp_timestamps.py` | FSDP | OLMoASR processed data | Memory-efficient large model training |
| `train_timestamps.py` | DDP | OLMoASR processed data | Standard multi-GPU training |
| `train_owsm.py` | DDP | OWSM-Eng dataset | Pre-configured for OWSM data format |
| `train_yodas.py` | DDP | YODAS-Eng dataset | Pre-configured for YODAS data format |

```mermaid
flowchart LR
    subgraph "Data Format Decision"
        OLMO_FORMAT["OLMoASR Processed Data<br/>JSONL with timestamps"]
        OWSM_FORMAT["OWSM-Eng Dataset<br/>Hugging Face format"]
        YODAS_FORMAT["YODAS-Eng Dataset<br/>Hugging Face format"]
    end
    
    subgraph "Scale Decision"
        SMALL_SCALE["Small to Medium Scale<br/>< 8 GPUs"]
        LARGE_SCALE["Large Scale<br/>8+ GPUs, Memory Constrained"]
    end
    
    subgraph "Training Script Selection"
        DDP_OLMO["train_timestamps.py<br/>DDP + OLMoASR Data"]
        FSDP_OLMO["train_fsdp_timestamps.py<br/>FSDP + OLMoASR Data"]
        DDP_OWSM["train_owsm.py<br/>DDP + OWSM Data"]
        DDP_YODAS["train_yodas.py<br/>DDP + YODAS Data"]
    end
    
    OLMO_FORMAT --> SMALL_SCALE
    OLMO_FORMAT --> LARGE_SCALE
    OWSM_FORMAT --> SMALL_SCALE
    YODAS_FORMAT --> SMALL_SCALE
    
    SMALL_SCALE --> DDP_OLMO
    LARGE_SCALE --> FSDP_OLMO
    SMALL_SCALE --> DDP_OWSM
    SMALL_SCALE --> DDP_YODAS
```

Sources: [scripts/README.md:20-27]()

## Training Configuration System

The training system uses a configuration-based approach where job configurations are stored in `configs/job_configs/training/` and specify all training parameters, data paths, and model settings. This allows for reproducible training runs and easy parameter sweeps.

### Configuration Structure

Training configurations typically include:

- **Data Configuration**: Dataset paths, batch sizes, data loading parameters
- **Model Configuration**: Architecture settings, model size, initialization
- **Optimization Configuration**: Learning rate, scheduler, optimizer settings  
- **Training Configuration**: Number of epochs, checkpoint frequency, distributed settings
- **Logging Configuration**: Weights & Biases project settings, logging frequency

```mermaid
graph TB
    subgraph "Configuration System"
        JOB_CONFIGS["configs/job_configs/training/<br/>Training Job Configurations"]
        YAML_FILES["*.yaml Config Files<br/>Parameter Specifications"]
    end
    
    subgraph "Configuration Categories"
        DATA_CONFIG["Data Configuration<br/>Paths, Batch Sizes, Loading"]
        MODEL_CONFIG["Model Configuration<br/>Architecture, Size, Init"] 
        OPTIM_CONFIG["Optimization Configuration<br/>LR, Scheduler, Optimizer"]
        TRAIN_CONFIG["Training Configuration<br/>Epochs, Checkpoints, Distributed"]
        LOG_CONFIG["Logging Configuration<br/>W&B Settings, Frequency"]
    end
    
    subgraph "Training Script Integration"
        FIRE_CLI["Python Fire CLI<br/>Parameter Parsing"]
        SCRIPT_ARGS["Script Arguments<br/>Config Overrides"]
        RUNTIME_PARAMS["Runtime Parameters<br/>Final Training Config"]
    end
    
    JOB_CONFIGS --> YAML_FILES
    YAML_FILES --> DATA_CONFIG
    YAML_FILES --> MODEL_CONFIG
    YAML_FILES --> OPTIM_CONFIG
    YAML_FILES --> TRAIN_CONFIG
    YAML_FILES --> LOG_CONFIG
    
    DATA_CONFIG --> FIRE_CLI
    MODEL_CONFIG --> FIRE_CLI
    OPTIM_CONFIG --> FIRE_CLI
    TRAIN_CONFIG --> FIRE_CLI
    LOG_CONFIG --> FIRE_CLI
    
    FIRE_CLI --> SCRIPT_ARGS
    SCRIPT_ARGS --> RUNTIME_PARAMS
```

Sources: [scripts/README.md:27]()

## Training Process Flow

The training process follows a standardized workflow regardless of the specific training script used. The process involves data loading, model initialization, distributed training setup, and iterative training with checkpointing.

```mermaid
sequenceDiagram
    participant CLI as "Training Script CLI"
    participant DATA as "Data Loader"
    participant MODEL as "OLMoASR Model"
    participant DIST as "Distributed Training"
    participant WANDB as "W&B Logging"
    participant CKPT as "Checkpoint System"
    
    CLI->>DATA: "Initialize DataLoader<br/>Load training data"
    CLI->>MODEL: "Initialize OLMoASR model<br/>Load base weights"
    CLI->>DIST: "Setup distributed training<br/>DDP/FSDP initialization"
    CLI->>WANDB: "Initialize experiment<br/>Setup logging"
    
    loop Training Epochs
        DATA->>MODEL: "Batch of audio/text pairs"
        MODEL->>MODEL: "Forward pass<br/>Compute loss"
        MODEL->>DIST: "Backward pass<br/>Gradient computation"
        DIST->>MODEL: "Gradient synchronization<br/>Parameter updates"
        MODEL->>WANDB: "Log training metrics<br/>Loss, learning rate"
        
        alt Checkpoint Interval
            MODEL->>CKPT: "Save model checkpoint<br/>Optimizer state"
        end
    end
    
    MODEL->>CKPT: "Save final checkpoint<br/>Training complete"
    WANDB->>WANDB: "Finalize experiment<br/>Upload final metrics"
```

Sources: [scripts/README.md:20-27]()

## Model Checkpointing and Output

The training system generates several types of outputs that capture the trained model state and training progress. These outputs are essential for model deployment, evaluation, and continued training.

### Training Output Types

| Output Type | File Pattern | Purpose |
|-------------|--------------|---------|
| Model Checkpoints | `*.pt` files | Trained model weights and optimizer state |
| Training Logs | Local log files | Detailed training progress and metrics |
| W&B Experiments | Online dashboard | Visualization and experiment tracking |
| Configuration Snapshots | Embedded in checkpoints | Reproducible training parameters |

The checkpoint system is designed to support both inference and continued training scenarios. For model deployment and evaluation workflows, see [Model Evaluation](#5) and [Inference & Deployment](#6).

Sources: [scripts/README.md:20-27](), [scripts/README.md:32-37]()

---

