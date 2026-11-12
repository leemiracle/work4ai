<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/GR00T-Dreams · page 3 Core IDM System · fetched 2026-10-26 -->

# Core IDM System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [IDM_dump/dump_idm_actions.py](IDM_dump/dump_idm_actions.py)
- [IDM_dump/raw_to_lerobot.py](IDM_dump/raw_to_lerobot.py)
- [IDM_dump/scripts/finetune/franka.sh](IDM_dump/scripts/finetune/franka.sh)
- [IDM_dump/scripts/finetune/gr1.sh](IDM_dump/scripts/finetune/gr1.sh)

</details>



## Purpose and Scope

The Core IDM System implements the Inverse Dynamics Model (IDM) for robotic action prediction and model finetuning across multiple robot embodiments. This system serves as the central processing engine for converting raw robot demonstrations into actionable predictions and training improved models.

This document covers the IDM architecture, action prediction pipeline, and finetuning capabilities. For data preprocessing and format conversion, see [Data Processing Pipeline](#4). For robot-specific configurations, see [Robot Embodiments](#5).

## IDM Architecture Overview

The IDM system consists of three primary components: action prediction, model finetuning, and multi-GPU processing orchestration. The system is designed to handle large-scale datasets across different robot embodiments using distributed processing.

### Core IDM Components

```mermaid
graph TB
    subgraph "IDM Core Architecture"
        IDM_MODEL["IDM Model<br/>gr00t.model.idm.IDM"]
        DATASET["LeRobotSingleDataset<br/>gr00t.data.dataset"]
        EMBODIMENT["EmbodimentTag<br/>gr00t.data.embodiment_tags"]
    end
    
    subgraph "Action Prediction Pipeline"
        DUMP_ACTIONS["dump_idm_actions.py<br/>validate_checkpoint()"]
        WORKER_FUNC["worker_func()<br/>Multi-GPU processing"]
        COLLATE_FN["collate_fn()<br/>Batch preparation"]
    end
    
    subgraph "Model Finetuning"
        FINETUNE_SCRIPT["gr00t_finetune.py<br/>Distributed training"]
        FRANKA_SCRIPT["franka.sh<br/>Franka finetuning"]
        GR1_SCRIPT["gr1.sh<br/>GR1 finetuning"]
    end
    
    subgraph "Configuration Management"
        CONFIG_LOADER["load_dataset_and_config()<br/>YAML/HuggingFace config"]
        MODALITY_CONFIGS["modality_configs<br/>Embodiment-specific"]
        TRANSFORM_INST["transform_inst<br/>Data transforms"]
    end
    
    IDM_MODEL --> DUMP_ACTIONS
    DATASET --> DUMP_ACTIONS
    EMBODIMENT --> DATASET
    
    DUMP_ACTIONS --> WORKER_FUNC
    WORKER_FUNC --> COLLATE_FN
    
    CONFIG_LOADER --> MODALITY_CONFIGS
    CONFIG_LOADER --> TRANSFORM_INST
    MODALITY_CONFIGS --> DATASET
    TRANSFORM_INST --> DATASET
    
    FINETUNE_SCRIPT --> FRANKA_SCRIPT
    FINETUNE_SCRIPT --> GR1_SCRIPT
```

**Sources:** [IDM_dump/dump_idm_actions.py:1-476](), [IDM_dump/scripts/finetune/franka.sh:1-2](), [IDM_dump/scripts/finetune/gr1.sh:1-3]()

## Action Prediction Pipeline

The action prediction pipeline processes robot trajectories through the IDM model to generate predicted actions. The system supports both local checkpoints and HuggingFace model repositories.

### IDM Action Prediction Workflow

```mermaid
flowchart TD
    START["validate_checkpoint()"]
    
    subgraph "Configuration Loading"
        LOAD_CONFIG["load_dataset_and_config()<br/>• HuggingFace or local path<br/>• YAML config parsing<br/>• Embodiment detection"]
        CREATE_DATASET["LeRobotSingleDataset<br/>• Modality configs<br/>• Transform pipeline<br/>• EmbodimentTag"]
    end
    
    subgraph "Multi-GPU Distribution"
        GPU_SPLIT["Split trajectories<br/>across GPUs"]
        PROCESS_POOL["ProcessPoolExecutor<br/>max_workers=num_gpus"]
    end
    
    subgraph "Per-GPU Processing"
        LOAD_MODEL["IDM.from_pretrained()<br/>Load on cuda:gpu_id"]
        PROCESS_TRAJ["Process trajectory<br/>worker_func()"]
        PREFETCH_DATA["ThreadPoolExecutor<br/>load_and_transform_step()"]
        BATCH_INFERENCE["Batch inference<br/>model.get_action()"]
        SAVE_RESULTS["save_trajectory_data()<br/>Parquet output"]
    end
    
    START --> LOAD_CONFIG
    LOAD_CONFIG --> CREATE_DATASET
    CREATE_DATASET --> GPU_SPLIT
    GPU_SPLIT --> PROCESS_POOL
    PROCESS_POOL --> LOAD_MODEL
    LOAD_MODEL --> PROCESS_TRAJ
    PROCESS_TRAJ --> PREFETCH_DATA
    PREFETCH_DATA --> BATCH_INFERENCE
    BATCH_INFERENCE --> SAVE_RESULTS
```

**Sources:** [IDM_dump/dump_idm_actions.py:298-382](), [IDM_dump/dump_idm_actions.py:141-297]()

### Data Processing and Batch Preparation

The system implements efficient data loading with video preprocessing and batch collation for GPU inference:

| Component | Function | Key Features |
|-----------|----------|--------------|
| `get_step_data()` | [IDM_dump/dump_idm_actions.py:113-127]() | Extracts state, action, language data |
| `load_and_transform_step()` | [IDM_dump/dump_idm_actions.py:176-191]() | Video frame extraction and transforms |
| `collate_fn()` | [IDM_dump/dump_idm_actions.py:100-111]() | Batch tensor preparation for GPU |
| `get_all_frames_and_timestamps()` | [IDM_dump/dump_idm_actions.py:199]() | Video backend processing |

**Sources:** [IDM_dump/dump_idm_actions.py:100-127](), [IDM_dump/dump_idm_actions.py:176-200]()

## Model Finetuning System

The IDM system supports distributed model finetuning across different robot embodiments using the `gr00t_finetune.py` script with embodiment-specific configurations.

### Finetuning Configuration

```mermaid
graph LR
    subgraph "Embodiment Scripts"
        FRANKA_SH["franka.sh<br/>--embodiment_tag franka"]
        GR1_SH["gr1.sh<br/>--embodiment_tag gr1"]
    end
    
    subgraph "Finetuning Engine"
        FINETUNE_PY["gr00t_finetune.py<br/>torchrun distributed"]
        DATASET_PATH["--dataset-path<br/>IDM_dump/data/"]
        DATA_CONFIG["--data-config<br/>Embodiment-specific"]
    end
    
    subgraph "Dataset Paths"
        FRANKA_DATA["franka.data_idm<br/>Franka trajectories"]
        GR1_DATA["gr1_unified.data_idm<br/>GR1 trajectories"]
    end
    
    FRANKA_SH --> FINETUNE_PY
    GR1_SH --> FINETUNE_PY
    
    FINETUNE_PY --> DATASET_PATH
    FINETUNE_PY --> DATA_CONFIG
    
    DATASET_PATH --> FRANKA_DATA
    DATASET_PATH --> GR1_DATA
```

**Sources:** [IDM_dump/scripts/finetune/franka.sh:1-2](), [IDM_dump/scripts/finetune/gr1.sh:1-3]()

### Embodiment-Specific Processing

The system automatically detects and configures processing parameters based on the dataset embodiment:

| Embodiment | EmbodimentTag | Data Config | Features |
|------------|---------------|-------------|----------|
| Franka | `EmbodimentTag.FRANKA` | `franka` | 7-DOF arm control |
| GR1 | `EmbodimentTag.GR1_unified` | `gr1_arms_waist` | Humanoid body control |
| SO100 | `EmbodimentTag.SO100` | `so100` | 6-DOF arm control |
| RoboCasa | `EmbodimentTag.ROBOCASA` | `robocasa` | Kitchen simulation |

**Sources:** [IDM_dump/dump_idm_actions.py:78-87]()

## Multi-GPU Processing Architecture

The IDM system implements efficient multi-GPU processing for large-scale action prediction using process-based parallelism with CUDA device assignment.

### GPU Processing Distribution

```mermaid
graph TB
    subgraph "Main Process"
        MAIN["validate_checkpoint()<br/>GPU coordination"]
        TRAJECTORY_SPLIT["Split trajectories<br/>chunk_size calculation"]
        PROCESS_EXECUTOR["ProcessPoolExecutor<br/>max_workers=num_gpus"]
    end
    
    subgraph "GPU 0 Process"
        GPU0_WORKER["worker_func(gpu_id=0)<br/>cuda:0"]
        GPU0_MODEL["IDM model on GPU 0"]
        GPU0_BATCH["Batch processing"]
    end
    
    subgraph "GPU 1 Process"
        GPU1_WORKER["worker_func(gpu_id=1)<br/>cuda:1"]
        GPU1_MODEL["IDM model on GPU 1"]
        GPU1_BATCH["Batch processing"]
    end
    
    subgraph "GPU N Process"
        GPUN_WORKER["worker_func(gpu_id=N)<br/>cuda:N"]
        GPUN_MODEL["IDM model on GPU N"]
        GPUN_BATCH["Batch processing"]
    end
    
    subgraph "Shared Resources"
        DATASET_CONFIG["Dataset configuration<br/>Read-only access"]
        VIDEO_DATA["Video data<br/>ThreadPoolExecutor prefetch"]
        OUTPUT_DIR["Output directory<br/>Parquet files"]
    end
    
    MAIN --> TRAJECTORY_SPLIT
    TRAJECTORY_SPLIT --> PROCESS_EXECUTOR
    
    PROCESS_EXECUTOR --> GPU0_WORKER
    PROCESS_EXECUTOR --> GPU1_WORKER
    PROCESS_EXECUTOR --> GPUN_WORKER
    
    GPU0_WORKER --> GPU0_MODEL
    GPU1_WORKER --> GPU1_MODEL
    GPUN_WORKER --> GPUN_MODEL
    
    GPU0_MODEL --> GPU0_BATCH
    GPU1_MODEL --> GPU1_BATCH
    GPUN_MODEL --> GPUN_BATCH
    
    DATASET_CONFIG --> GPU0_WORKER
    DATASET_CONFIG --> GPU1_WORKER
    DATASET_CONFIG --> GPUN_WORKER
    
    VIDEO_DATA --> GPU0_BATCH
    VIDEO_DATA --> GPU1_BATCH
    VIDEO_DATA --> GPUN_BATCH
    
    GPU0_BATCH --> OUTPUT_DIR
    GPU1_BATCH --> OUTPUT_DIR
    GPUN_BATCH --> OUTPUT_DIR
```

**Sources:** [IDM_dump/dump_idm_actions.py:308-382](), [IDM_dump/dump_idm_actions.py:141-297]()

### Performance Optimization Features

The system includes several optimization strategies for efficient processing:

- **Process-based Parallelism**: Uses `multiprocessing.set_start_method("spawn")` for GPU isolation
- **ThreadPoolExecutor Prefetching**: Concurrent video frame loading within each GPU process
- **Batch Processing**: Configurable batch sizes for memory optimization
- **CUDA Memory Management**: Automatic `torch.cuda.empty_cache()` after processing
- **Chunked Output**: Trajectories saved in chunks to prevent memory overflow

**Sources:** [IDM_dump/dump_idm_actions.py:436](), [IDM_dump/dump_idm_actions.py:203-212](), [IDM_dump/dump_idm_actions.py:380-381](), [IDM_dump/dump_idm_actions.py:129-137]()

## Configuration and Model Loading

The IDM system supports flexible model loading from both local checkpoints and HuggingFace repositories with automatic configuration detection.

### Model Loading Pipeline

```mermaid
flowchart TD
    CHECK_PATH["Check checkpoint_path<br/>Local vs HuggingFace"]
    
    subgraph "Local Path Loading"
        LOCAL_CONFIG["Load conf.yaml<br/>experiment_cfg/conf.yaml"]
        LOCAL_MODEL["Load local checkpoint"]
    end
    
    subgraph "HuggingFace Loading"
        HF_DOWNLOAD["hf_hub_download()<br/>conf.yaml from repo"]
        HF_MODEL["IDM.from_pretrained()<br/>HuggingFace repo_id"]
    end
    
    subgraph "Configuration Processing"
        OMEGA_CONF["OmegaConf.create()<br/>YAML to config"]
        EMBODIMENT_DETECT["Detect embodiment<br/>from dataset name"]
        MODALITY_SETUP["Instantiate modality_configs<br/>and transforms"]
    end
    
    CHECK_PATH --> LOCAL_CONFIG
    CHECK_PATH --> HF_DOWNLOAD
    
    LOCAL_CONFIG --> OMEGA_CONF
    HF_DOWNLOAD --> OMEGA_CONF
    
    OMEGA_CONF --> EMBODIMENT_DETECT
    EMBODIMENT_DETECT --> MODALITY_SETUP
    
    LOCAL_MODEL --> LOCAL_CONFIG
    HF_MODEL --> HF_DOWNLOAD
```

**Sources:** [IDM_dump/dump_idm_actions.py:22-97](), [IDM_dump/dump_idm_actions.py:156-162]()

---

