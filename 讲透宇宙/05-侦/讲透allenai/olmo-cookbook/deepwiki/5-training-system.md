<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/olmo-cookbook · page 5 Training System · fetched 2026-10-26 -->

# Training System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/cookbook/model/builder.py](src/cookbook/model/builder.py)
- [src/cookbook/recipes/spring2code/scaling/spring2code-1b-5xC-weka-top15-bpb-hlr-superbpe.yaml](src/cookbook/recipes/spring2code/scaling/spring2code-1b-5xC-weka-top15-bpb-hlr-superbpe.yaml)
- [src/cookbook/utils/config.py](src/cookbook/utils/config.py)

</details>



The Training System is responsible for configuring, launching, and managing OLMo model training runs. It provides a comprehensive framework for building training configurations from YAML files, setting up distributed training environments, and integrating with external compute platforms like Beaker. For information about evaluation workflows, see [Evaluation System](#4). For infrastructure management details, see [Infrastructure Management](#6).

## System Overview

The Training System consists of several key components that work together to transform high-level training specifications into executable training configurations:

```mermaid
graph TB
    subgraph "Configuration Sources"
        YAML["YAML Config Files<br/>(e.g., spring2code-1b.yaml)"]
        CLI_ARGS["CLI Arguments<br/>(run_name, group_id)"]
        CONSTANTS["Constants<br/>(model configs, defaults)"]
    end
    
    subgraph "Configuration Processing"
        config_from_path["config_from_path()"]
        mk_experiments["mk_experiments()"]
        build_train_config["build_train_config()"]
    end
    
    subgraph "Configuration Building"
        TransformerConfigBuilder["TransformerConfigBuilder"]
        MODEL_CONFIG["ModelTrainConfig"]
        BEAKER_CONFIG["BeakerLaunchConfig"]
    end
    
    subgraph "Training Execution"
        TRAIN_SCRIPT["train.py"]
        OLMO_CORE["OLMo-core Trainer"]
        CALLBACKS["Callbacks<br/>(WandB, Checkpointer)"]
    end
    
    subgraph "External Systems"
        BEAKER["Beaker Platform"]
        WANDB["Weights & Biases"]
        STORAGE["Storage<br/>(S3, Weka, GCS)"]
    end
    
    YAML --> config_from_path
    CLI_ARGS --> build_train_config
    CONSTANTS --> TransformerConfigBuilder
    
    config_from_path --> build_train_config
    build_train_config --> mk_experiments
    build_train_config --> TransformerConfigBuilder
    
    TransformerConfigBuilder --> MODEL_CONFIG
    MODEL_CONFIG --> TRAIN_SCRIPT
    
    mk_experiments --> BEAKER_CONFIG
    BEAKER_CONFIG --> BEAKER
    
    TRAIN_SCRIPT --> OLMO_CORE
    OLMO_CORE --> CALLBACKS
    CALLBACKS --> WANDB
    CALLBACKS --> STORAGE
    
    BEAKER --> TRAIN_SCRIPT
```

Sources: [src/cookbook/utils/config.py:34-38](), [src/cookbook/utils/config.py:124-217](), [src/cookbook/model/builder.py:85-162]()

## Configuration Loading and Processing

The system begins by loading training configurations from YAML files using a structured approach:

```mermaid
flowchart LR
    subgraph "YAML Structure"
        YAML_FILE["YAML Config"]
        EXPERIMENT_CONFIG["ExperimentConfig"]
        DATASET_CONFIG["dataset.sources"]
        MODEL_PARAMS["model, tokenizer, etc."]
    end
    
    subgraph "Processing Functions"
        config_from_path["config_from_path()"]
        mk_source_instances["mk_source_instances()"]
        mk_experiments["mk_experiments()"]
    end
    
    subgraph "Result"
        SOURCE_INSTANCES["SourceInstance[]"]
        EXPERIMENT_INSTANCES["ExperimentInstance[]"]
    end
    
    YAML_FILE --> config_from_path
    config_from_path --> EXPERIMENT_CONFIG
    EXPERIMENT_CONFIG --> DATASET_CONFIG
    EXPERIMENT_CONFIG --> MODEL_PARAMS
    
    DATASET_CONFIG --> mk_source_instances
    mk_source_instances --> SOURCE_INSTANCES
    
    SOURCE_INSTANCES --> mk_experiments
    mk_experiments --> EXPERIMENT_INSTANCES
```

| Function | Purpose | Key Parameters |
|----------|---------|----------------|
| `config_from_path()` | Load YAML config into `ExperimentConfig` | `config: Path` |
| `mk_source_instances()` | Convert source configs to instances | `sources`, `priors` |
| `mk_experiments()` | Generate experiment instances | `config`, `group_id`, `priors` |

Sources: [src/cookbook/utils/config.py:34-38](), [src/cookbook/utils/config.py:41-73]()

## TransformerConfigBuilder

The `TransformerConfigBuilder` is the central component responsible for constructing comprehensive training configurations. It takes high-level parameters and builds detailed configurations for all training components:

```mermaid
graph TB
    subgraph "Input Parameters"
        RUN_NAME["run_name"]
        SOURCES["sources: SourceInstance[]"]
        MODEL_ID["model_identifier"]
        CLUSTER["cluster"]
        USER["beaker_user"]
    end
    
    subgraph "TransformerConfigBuilder Methods"
        GET_TOKENIZER["get_tokenizer_config()"]
        GET_BATCH_SIZE["get_global_batch_size()"]
        GET_LR["get_learning_rate()"]
        BUILD_CALLBACKS["build_callbacks()"]
        BUILD_DATASET["build_dataset_config()"]
        GET_SCHEDULER["get_scheduler_config()"]
        GET_OPTIMIZER["get_optimizer_config()"]
    end
    
    subgraph "Output Components"
        TRANSFORMER_CONFIG["TransformerConfig"]
        DATASET_CONFIG["NumpyDatasetConfig"]
        TRAINER_CONFIG["TrainerConfig"]
        CALLBACKS_DICT["Dict[str, Callback]"]
        MODEL_TRAIN_CONFIG["ModelTrainConfig"]
    end
    
    RUN_NAME --> TransformerConfigBuilder
    SOURCES --> TransformerConfigBuilder
    MODEL_ID --> TransformerConfigBuilder
    CLUSTER --> TransformerConfigBuilder
    USER --> TransformerConfigBuilder
    
    TransformerConfigBuilder --> GET_TOKENIZER
    TransformerConfigBuilder --> GET_BATCH_SIZE
    TransformerConfigBuilder --> GET_LR
    TransformerConfigBuilder --> BUILD_CALLBACKS
    TransformerConfigBuilder --> BUILD_DATASET
    TransformerConfigBuilder --> GET_SCHEDULER
    TransformerConfigBuilder --> GET_OPTIMIZER
    
    GET_TOKENIZER --> TRANSFORMER_CONFIG
    BUILD_DATASET --> DATASET_CONFIG
    BUILD_CALLBACKS --> CALLBACKS_DICT
    GET_SCHEDULER --> TRAINER_CONFIG
    GET_OPTIMIZER --> TRAINER_CONFIG
    
    TRANSFORMER_CONFIG --> MODEL_TRAIN_CONFIG
    DATASET_CONFIG --> MODEL_TRAIN_CONFIG
    TRAINER_CONFIG --> MODEL_TRAIN_CONFIG
    CALLBACKS_DICT --> MODEL_TRAIN_CONFIG
```

### Key Configuration Methods

| Method | Return Type | Purpose |
|--------|-------------|---------|
| `get_tokenizer_config()` | `TokenizerConfig` | Maps tokenizer string to config |
| `get_global_batch_size()` | `int` | Calculates optimal batch size |
| `get_learning_rate()` | `float` | Uses model-specific defaults or user override |
| `build_callbacks()` | `Dict[str, Callback]` | Sets up training callbacks |
| `build_dataset_config()` | `NumpyDatasetConfig` | Configures dataset loading |
| `get_scheduler_config()` | `Scheduler` | Creates learning rate scheduler |

Sources: [src/cookbook/model/builder.py:85-162](), [src/cookbook/model/builder.py:281-332](), [src/cookbook/model/builder.py:337-413]()

## Training Configuration Build Process

The `build_train_config()` function orchestrates the entire configuration building process:

```mermaid
sequenceDiagram
    participant CLI as "CLI/User"
    participant BTC as "build_train_config()"
    participant TCB as "TransformerConfigBuilder"
    participant FS as "File Systems"
    participant TRAINER as "OLMo Trainer"
    
    CLI->>BTC: config_path, run_name, group_id
    BTC->>BTC: config_from_path()
    BTC->>FS: normalize_source_paths()
    BTC->>BTC: mk_source_instances()
    BTC->>TCB: Create builder with params
    TCB->>TCB: build()
    TCB-->>BTC: ModelTrainConfig
    
    alt not dry_run
        BTC->>BTC: dataset.build()
        BTC->>BTC: model.build()
        BTC->>BTC: train_module.build()
        BTC->>TRAINER: trainer.build()
        
        alt load_path exists
            TRAINER->>TRAINER: maybe_load_checkpoint()
            alt no checkpoint in save_folder
                TRAINER->>FS: load_checkpoint(load_path)
            end
        end
        
        TRAINER->>TRAINER: setup callbacks
    end
    
    BTC-->>CLI: trainer (or None if dry_run)
```

Sources: [src/cookbook/utils/config.py:124-217]()

## Callback System Integration

The Training System integrates with various external services through a callback system:

```mermaid
graph LR
    subgraph "Core Callbacks"
        CHECKPOINTER["CheckpointerCallback"]
        CONFIG_SAVER["ConfigSaverCallback"]
        PROFILER["ProfilerCallback"]
        GC["GarbageCollectorCallback"]
    end
    
    subgraph "Platform Integration"
        BEAKER_CB["BeakerCallback"]
        GPU_MONITOR["GPUMemoryMonitorCallback"]
    end
    
    subgraph "Metrics Backends"
        WANDB_CB["WandBCallback"]
        COMET_CB["CometCallback"]
    end
    
    subgraph "Evaluation Callbacks"
        LM_EVAL["LMEvaluatorCallbackConfig"]
        DOWNSTREAM["DownstreamEvaluatorCallbackConfig"]
    end
    
    subgraph "External Services"
        WANDB_SERVICE["Weights & Biases"]
        COMET_SERVICE["Comet ML"]
        STORAGE_SERVICE["S3/Weka/GCS"]
        BEAKER_SERVICE["Beaker Platform"]
    end
    
    CHECKPOINTER --> STORAGE_SERVICE
    BEAKER_CB --> BEAKER_SERVICE
    WANDB_CB --> WANDB_SERVICE
    COMET_CB --> COMET_SERVICE
    
    LM_EVAL --> STORAGE_SERVICE
    DOWNSTREAM --> STORAGE_SERVICE
```

Sources: [src/cookbook/model/builder.py:337-413]()

## Beaker Integration

The Training System generates Beaker launch configurations for distributed training:

```mermaid
graph TB
    subgraph "Launch Configuration"
        MK_LAUNCH["mk_launch_configs()"]
        BEAKER_CONFIG["BeakerLaunchConfig"]
    end
    
    subgraph "Beaker Resources"
        CLUSTERS["clusters"]
        NODES["num_nodes"]
        GPUS["num_gpus"]
        WEKA_BUCKETS["weka_buckets"]
        IMAGE["beaker_image"]
    end
    
    subgraph "Environment Setup"
        ENV_VARS["env_vars<br/>(NCCL_DEBUG)"]
        SECRETS["env_secrets<br/>(BEAKER_TOKEN, WANDB_API_KEY)"]
        SETUP_STEPS["setup_steps<br/>(git clone, pip install)"]
    end
    
    subgraph "Command Generation"
        MK_INSTANCE_CMD["mk_instance_cmd()"]
        TRAIN_CMD["train.py command"]
    end
    
    MK_LAUNCH --> BEAKER_CONFIG
    BEAKER_CONFIG --> CLUSTERS
    BEAKER_CONFIG --> NODES
    BEAKER_CONFIG --> GPUS
    BEAKER_CONFIG --> WEKA_BUCKETS
    BEAKER_CONFIG --> IMAGE
    
    BEAKER_CONFIG --> ENV_VARS
    BEAKER_CONFIG --> SECRETS
    BEAKER_CONFIG --> SETUP_STEPS
    
    MK_LAUNCH --> MK_INSTANCE_CMD
    MK_INSTANCE_CMD --> TRAIN_CMD
```

Sources: [src/cookbook/utils/config.py:219-268](), [src/cookbook/utils/config.py:88-104]()

## Storage and Path Handling

The system handles multiple storage backends with intelligent path normalization:

| Storage Type | Local Path | Remote Path | Use Case |
|-------------|------------|-------------|----------|
| S3 | `s3://ai2-llm/...` | `s3://ai2-llm/...` | General cloud storage |
| Weka | `/weka/oe-training-default/...` | `weka://oe-training-default/...` | High-performance training |
| GCS | `gs://ai2-llm/...` | `gs://ai2-llm/...` | Google Cloud clusters |

The `remote_fs_cache()` function maintains filesystem instances for different storage backends, while path normalization occurs in `build_train_config()` based on execution context (local vs. Beaker).

Sources: [src/cookbook/utils/config.py:107-122](), [src/cookbook/utils/config.py:140-149]()

---

