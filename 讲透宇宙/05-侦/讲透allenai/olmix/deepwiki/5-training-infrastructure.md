<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/olmix · page 5 Training Infrastructure · fetched 2026-10-26 -->

# Training Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [olmix/__init__.py](olmix/__init__.py)
- [olmix/fit/__init__.py](olmix/fit/__init__.py)
- [olmix/launch/__init__.py](olmix/launch/__init__.py)
- [olmix/launch/beaker.py](olmix/launch/beaker.py)
- [olmix/launch/train.py](olmix/launch/train.py)
- [olmix/model/__init__.py](olmix/model/__init__.py)
- [olmix/model/evaluators.py](olmix/model/evaluators.py)
- [olmix/model/transformer.py](olmix/model/transformer.py)
- [tests/test_cli.py](tests/test_cli.py)
- [tests/test_config.py](tests/test_config.py)
- [tests/test_imports.py](tests/test_imports.py)

</details>



This document provides an overview of how olmix integrates with Beaker and OLMo Core for distributed GPU training. The training infrastructure orchestrates the execution of proxy model experiments, applying Chinchilla scaling laws to automatically configure training parameters and logging comprehensive evaluation metrics to Weights & Biases.

**Scope**: This page covers the end-to-end training pipeline from experiment submission to result collection. For detailed information on specific components:
- Beaker experiment creation and submission: see [Beaker Integration](#5.1)
- Chinchilla scaling and parameter computation: see [TransformerConfigBuilder](#5.2)
- Data loading and mixture configuration: see [Data Pipeline](#5.3)
- Evaluation task definitions: see [Evaluation Tasks](#5.4)

For the broader workflow (generation, optimization, iteration), see [Overview](#1).

## Architecture Overview

The training infrastructure bridges olmix's high-level experiment definitions with Beaker's distributed execution platform and OLMo Core's training framework. The system follows a three-stage pipeline:

```mermaid
graph TB
    subgraph "Stage 1: Experiment Definition"
        LC["LaunchConfig YAML<br/>(from olmix generate)"]
        LC --> MkExpGroup["mk_experiment_group()"]
        MkExpGroup --> ExpGroup["ExperimentGroup<br/>group_id + instances[]"]
    end
    
    subgraph "Stage 2: Beaker Submission"
        ExpGroup --> MkLaunch["mk_launch_configs()"]
        MkLaunch --> BeakerConfigs["BeakerLaunchConfig[]<br/>environment, secrets, commands"]
        BeakerConfigs --> LaunchNI["launch_noninteractive()"]
        LaunchNI --> BeakerAPI["Beaker API<br/>experiment submission"]
    end
    
    subgraph "Stage 3: Training Execution"
        BeakerAPI --> TrainPy["olmix/launch/train.py<br/>CLI entry point"]
        TrainPy --> TCB["TransformerConfigBuilder<br/>Chinchilla scaling"]
        TCB --> OLMoCore["OLMo Core Trainer<br/>trainer.fit()"]
        OLMoCore --> WandB["W&B Logging<br/>metrics + checkpoints"]
    end
    
    style MkExpGroup fill:#f9f9f9
    style MkLaunch fill:#f9f9f9
    style TCB fill:#f9f9f9
```

**Stage 1** converts LaunchConfig objects (which contain explicit mixture weights) into ExperimentGroup structures with individual ExperimentInstance records. **Stage 2** transforms these into Beaker-specific launch configurations with appropriate environment variables, secrets, and command-line arguments. **Stage 3** executes the training script, which uses TransformerConfigBuilder to apply scaling laws and delegates actual training to OLMo Core.

Sources: [olmix/launch/beaker.py:18-42](), [olmix/launch/beaker.py:101-163](), [olmix/launch/train.py:157-238]()

## Key Components

The training infrastructure consists of several interconnected components:

| Component | File Location | Purpose |
|-----------|---------------|---------|
| `mk_experiment_group` | [olmix/launch/beaker.py:18-42]() | Groups LaunchConfigs into ExperimentGroup with shared configuration |
| `mk_launch_configs` | [olmix/launch/beaker.py:101-163]() | Converts ExperimentGroup to Beaker-specific launch configs |
| `launch_noninteractive` | [olmix/launch/beaker.py:166-181]() | Submits experiments to Beaker without interactive prompts |
| `TransformerConfigBuilder` | [olmix/model/transformer.py:92-443]() | Builds training configuration with Chinchilla scaling |
| `train` CLI command | [olmix/launch/train.py:157-238]() | Entry point executed on Beaker workers |

Sources: [olmix/launch/beaker.py](), [olmix/model/transformer.py](), [olmix/launch/train.py]()

## Experiment Submission Flow

The following diagram shows how code entities map to the submission process:

```mermaid
graph TB
    subgraph "Python Objects"
        LaunchConfigs["list[LaunchConfig]<br/>name, mix, infra, training, data"]
        GroupUUID["group_uuid: str<br/>unique identifier"]
        
        LaunchConfigs --> mkExpGrp["mk_experiment_group()<br/>olmix/launch/beaker.py:18"]
        GroupUUID --> mkExpGrp
        
        mkExpGrp --> ExpGrp["ExperimentGroup<br/>config, group_id, instances"]
        
        ExpGrp --> mkLaunchCfg["mk_launch_configs()<br/>olmix/launch/beaker.py:101"]
        BeakerUser["beaker_user: str"] --> mkLaunchCfg
        
        mkLaunchCfg --> BLCs["list[BeakerLaunchConfig]<br/>olmo_core.launch.beaker"]
    end
    
    subgraph "Beaker API"
        BLCs --> launchNI["launch_noninteractive()<br/>olmix/launch/beaker.py:166"]
        launchNI --> Recipe["recipe.launch()<br/>gantry recipe"]
        Recipe --> BeakerExps["Beaker Experiments<br/>running on cluster"]
    end
    
    style mkExpGrp fill:#f9f9f9
    style mkLaunchCfg fill:#f9f9f9
    style launchNI fill:#f9f9f9
```

### ExperimentGroup Creation

The `mk_experiment_group` function transforms a list of LaunchConfig objects into an ExperimentGroup. Each LaunchConfig must have a `mix` field containing `MixEntry` objects with explicit weights and repetition factors:

```mermaid
graph LR
    LC1["LaunchConfig<br/>name: swarm-abc-0001<br/>mix: {wiki: 0.6, code: 0.4}"]
    LC2["LaunchConfig<br/>name: swarm-abc-0002<br/>mix: {wiki: 0.3, code: 0.7}"]
    LC3["LaunchConfig<br/>name: swarm-abc-0003<br/>mix: {wiki: 0.8, code: 0.2}"]
    
    LC1 --> mkExpGrp["mk_experiment_group()<br/>configs, group_uuid"]
    LC2 --> mkExpGrp
    LC3 --> mkExpGrp
    
    mkExpGrp --> ExpGrp["ExperimentGroup<br/>config: LC1 (shared base)<br/>group_id: abc123<br/>instances: [Inst1, Inst2, Inst3]"]
    
    ExpGrp --> Inst1["ExperimentInstance<br/>name: swarm-abc-0001<br/>sources: [SourceInstance...]"]
    ExpGrp --> Inst2["ExperimentInstance<br/>name: swarm-abc-0002<br/>sources: [SourceInstance...]"]
    ExpGrp --> Inst3["ExperimentInstance<br/>name: swarm-abc-0003<br/>sources: [SourceInstance...]"]
```

The group uses the first LaunchConfig as the shared base configuration (infrastructure, training parameters, evaluation settings), while each instance retains its unique mixture specification via `sources` field.

Sources: [olmix/launch/beaker.py:18-42](), [olmix/launch/utils.py]()

### BeakerLaunchConfig Generation

The `mk_launch_configs` function converts an ExperimentGroup into a list of `BeakerLaunchConfig` objects. Each config includes:

**Environment Variables** ([olmix/launch/beaker.py:116-132]()):
- `WORLD_SIZE`, `RANK`, `LOCAL_RANK` for single-GPU jobs
- `MASTER_ADDR`, `MASTER_PORT` for distributed setup
- `WANDB_DEBUG` if debugging is enabled

**Environment Secrets** ([olmix/launch/beaker.py:152-158]()):
- `BEAKER_TOKEN` for Beaker API access
- `WANDB_API_KEY` for W&B logging
- `R2_ENDPOINT_URL`, `WEKA_ENDPOINT_URL` for cloud storage
- `GOOGLE_CLOUD_PROJECT` for GCS access
- AWS credentials (`AWS_CONFIG`, `AWS_CREDENTIALS`)

**Weka Buckets** ([olmix/launch/beaker.py:112-114]()):
- Mounts `/weka/oe-training-default` if `weka` is enabled
- Used for high-performance shared filesystem access

**Training Command** ([olmix/launch/beaker.py:45-98]()):
The `mk_instance_cmd` function builds the command-line arguments for `olmix/launch/train.py`:

```
olmix/launch/train.py train
  -n <instance.name>
  -g <group_id>
  -x <chinchilla_multiple>
  -S <seed>
  -c <cluster>
  -u <beaker_user>
  -d <dtype>
  -T <tokenizer>
  -m <proxy_model_id>
  -w <weka>
  -y <train_type>
  -b <device_batch_size>
  [-B <global_batch_size>]
  [-C <checkpoint_path>]
  [--no-eval | -E <eval_interval> -e <task_id> ...]
  -s ("source_name", ["path1", "path2"], ratio, repetition_factor) ...
```

Sources: [olmix/launch/beaker.py:45-98](), [olmix/launch/beaker.py:101-163]()

## Training Execution

Once Beaker schedules the job on a GPU cluster, the training script [olmix/launch/train.py]() executes the following sequence:

```mermaid
sequenceDiagram
    participant Beaker
    participant TrainPy as "train.py CLI"
    participant TCB as "TransformerConfigBuilder"
    participant OLMoCore as "OLMo Core"
    participant WandB as "W&B"
    
    Beaker->>TrainPy: Execute with CLI args
    TrainPy->>TrainPy: Parse source tuples<br/>into SourceInstance[]
    TrainPy->>TCB: __init__()<br/>(sources, model_id, chinchilla_multiple)
    TCB->>TCB: Load tokenizer config<br/>TOKENIZERS[tokenizer]()
    TCB->>TCB: Load model config<br/>TransformerConfig.olmo2_30M()
    TCB->>TCB: Calculate scaling params<br/>get_batch_size(), get_lr(), get_duration()
    TCB->>TCB: Build data pipeline<br/>SourceMixtureConfig
    TCB->>TrainPy: Return ModelTrainConfig
    TrainPy->>OLMoCore: dataset.build()
    TrainPy->>OLMoCore: model.build(init_device="meta")
    TrainPy->>OLMoCore: train_module.build(model)
    TrainPy->>OLMoCore: data_loader.build(dataset)
    TrainPy->>OLMoCore: trainer.build(train_module, data_loader)
    TrainPy->>OLMoCore: trainer.fit()
    
    loop Training Loop
        OLMoCore->>WandB: Log metrics (step, loss, BPB)
        OLMoCore->>OLMoCore: Checkpoint if save_interval
        OLMoCore->>OLMoCore: Evaluate if eval_interval
    end
    
    OLMoCore->>WandB: Final metrics and checkpoint
    OLMoCore->>TrainPy: Training complete
```

Sources: [olmix/launch/train.py:157-238](), [olmix/model/transformer.py:350-443]()

## Chinchilla Scaling Laws

TransformerConfigBuilder automatically computes training hyperparameters using Chinchilla scaling laws. These formulas ensure compute-optimal training by relating model size to batch size, learning rate, and training duration.

| Parameter | Formula | Implementation |
|-----------|---------|----------------|
| **Batch Size** | `2048 * 160 * (N / 108M)^(2/3)` rounded to next power of 2 | [olmix/model/transformer.py:225-232]() |
| **Learning Rate** | `0.0047 * (N / 108M)^(-1/3) / 2` | [olmix/model/transformer.py:238-245]() |
| **Training Duration** | `20 * N * chinchilla_multiple` tokens | [olmix/model/transformer.py:247-253]() |
| **Warmup Tokens** | `min(N, 0.05 * total_tokens)` | [olmix/model/transformer.py:214-223]() |

The system uses `TOKENS_PER_PARAM = 20` ([olmix/model/transformer.py:53]()) as the Chinchilla-optimal token budget per parameter. The `chinchilla_multiple` parameter allows training for longer (e.g., `5.0` for 5x Chinchilla) or shorter (e.g., `0.5` for proxy models) than the optimal budget.

Sources: [olmix/model/transformer.py:225-253]()

## Configuration Pipeline

The following diagram shows how configuration flows from YAML files through Python objects to OLMo Core:

```mermaid
graph TB
    subgraph "YAML Configuration"
        YAML["LaunchConfig YAML<br/>infra, training, data, eval"]
    end
    
    subgraph "Python Configuration Objects"
        YAML --> LC["LaunchConfig<br/>olmix/aliases.py"]
        LC --> InfraC["InfraConfig<br/>cluster, gpus, budget"]
        LC --> TrainC["TrainingConfig<br/>proxy_model_id, chinchilla_multiple"]
        LC --> DataC["DataConfig<br/>sources[]"]
        LC --> EvalC["EvalConfig<br/>tasks, interval"]
        LC --> Mix["mix: dict[str, MixEntry]<br/>weights, repetition_factors"]
    end
    
    subgraph "Builder Layer"
        Mix --> SI["SourceInstance[]<br/>name, paths, ratio, repetition_factor"]
        SI --> TCB["TransformerConfigBuilder<br/>olmix/model/transformer.py:92"]
        TrainC --> TCB
        
        TCB --> TokenizerCfg["TokenizerConfig<br/>olmo_core.data"]
        TCB --> TransformerCfg["TransformerConfig<br/>olmo_core.nn.transformer"]
        TCB --> SourceMix["SourceMixtureConfig<br/>olmo_core.data.source_mixture"]
    end
    
    subgraph "OLMo Core Training"
        TokenizerCfg --> MTC["ModelTrainConfig"]
        TransformerCfg --> MTC
        SourceMix --> MTC
        
        MTC --> Dataset["NumpyFSLDataset<br/>olmo_core.data"]
        MTC --> DataLoader["NumpyDataLoader<br/>olmo_core.data"]
        MTC --> Trainer["TrainerConfig<br/>olmo_core.train"]
    end
    
    style TCB fill:#f9f9f9
    style MTC fill:#f9f9f9
```

The `TransformerConfigBuilder.build()` method ([olmix/model/transformer.py:350-443]()) produces a `ModelTrainConfig` object that aggregates all configuration needed for training:

- **Model**: `TransformerConfig` from olmo-core model factories
- **Dataset**: `NumpyFSLDatasetConfig` with `SourceMixtureConfig`
- **DataLoader**: `NumpyDataLoaderConfig` with caching settings
- **Trainer**: `TrainerConfig` with callbacks (WandB, checkpointing, evaluation)
- **TrainModule**: `TransformerTrainModuleConfig` with optimizer, scheduler, compilation settings

Sources: [olmix/model/transformer.py:350-443](), [olmix/model/aliases.py:7-18]()

## Data Pipeline Integration

TransformerConfigBuilder constructs a `SourceMixtureConfig` that specifies how to mix multiple data sources with different sampling ratios and repetition factors:

```mermaid
graph LR
    subgraph "Input: SourceInstance[]"
        SI1["SourceInstance<br/>name: wiki<br/>paths: [s3://.../wiki/*.npy]<br/>ratio: 0.6<br/>repetition_factor: 1.0"]
        SI2["SourceInstance<br/>name: code<br/>paths: [s3://.../code/*.npy]<br/>ratio: 0.4<br/>repetition_factor: 1.5"]
    end
    
    subgraph "Builder Process"
        SI1 --> Expand["expand_cloud_globs()<br/>glob patterns → concrete paths"]
        SI2 --> Expand
        
        Expand --> SMC["SourceMixtureConfig<br/>source_name<br/>paths (expanded)<br/>target_ratio<br/>max_repetition_ratio"]
    end
    
    subgraph "Output: SourceMixtureDatasetConfig"
        SMC --> SMDC["SourceMixtureDatasetConfig<br/>source_list: SourceMixtureList<br/>requested_tokens<br/>global_batch_size<br/>seed<br/>processes"]
        
        SMDC --> NFSLDC["NumpyFSLDatasetConfig<br/>source_mixture_config<br/>sequence_length: 8192<br/>tokenizer<br/>work_dir (cache)"]
    end
```

The [olmix/model/transformer.py:366-393]() code constructs the data pipeline:

1. **Glob Expansion**: Cloud storage patterns (e.g., `s3://bucket/**/*.npy`) are expanded to concrete file paths using `expand_cloud_globs()` ([olmix/utils/cloud.py]())
2. **Source Mixing**: Each `SourceInstance` becomes a `SourceMixtureConfig` with its target ratio and repetition factor
3. **Token Budget**: `requested_tokens` is set to the Chinchilla training duration
4. **Caching**: `work_dir` specifies where tokenized sequences are cached (varies by cluster/weka configuration)

The resulting `NumpyFSLDatasetConfig` uses OLMo Core's `NumpyFSLDataset` for efficient fixed-sequence-length training with automatic tokenization and caching.

Sources: [olmix/model/transformer.py:366-393](), [olmix/utils/cloud.py]()

## Callbacks and Monitoring

TransformerConfigBuilder configures several callbacks for monitoring and checkpointing ([olmix/model/transformer.py:304-348]()):

| Callback | Purpose | Configuration |
|----------|---------|---------------|
| `GPUMemoryMonitorCallback` | Track GPU memory usage | Default settings |
| `ConfigSaverCallback` | Save configuration to checkpoint | Saves `config_dict` |
| `ProfilerCallback` | PyTorch profiling (optional) | `enabled=self.profile` |
| `CheckpointerCallback` | Save model checkpoints | `save_interval=1000`<br/>`ephemeral_save_interval=250`<br/>`save_async=True` |
| `WandBCallback` | Log metrics to Weights & Biases | `project="olmix"`<br/>`group=group_id`<br/>`name=run_name` |
| `DownstreamEvaluatorCallbackConfig` | Evaluate on downstream tasks | `tasks=eval_tasks`<br/>`eval_interval=eval_interval`<br/>`fixed_steps=[final_step]` |

The **WandB callback** is configured with the experiment's `group_id`, enabling all variants in a swarm to be grouped together for analysis. The `group_id` is later used by the `fit` command to query and aggregate results across the entire swarm.

The **Downstream Evaluator** runs in-loop evaluation on specified tasks (see [Evaluation Tasks](#5.4)). It evaluates at regular intervals and ensures a final evaluation at the last training step, even if that step doesn't align with the regular interval.

Sources: [olmix/model/transformer.py:304-348]()

## Cluster-Specific Configuration

TransformerConfigBuilder adapts directory paths based on the target cluster ([olmix/model/transformer.py:196-212]()):

```mermaid
graph TB
    subgraph "Cluster Detection"
        Cluster["cluster: str"]
        Weka["weka: bool"]
    end
    
    subgraph "Directory Configuration"
        Cluster --> Check{Check cluster name}
        
        Check -->|"augusta"| GCS["GCS Configuration<br/>root_dir: gs://ai2-llm<br/>checkpoint_dir: gs://...<br/>work_dir: /tmp/.../dataset-cache"]
        
        Check -->|"jupiter, saturn, etc<br/>AND weka=True"| WekaFS["Weka Configuration<br/>root_dir: /weka/oe-training-default/ai2-llm<br/>checkpoint_dir: /weka/.../checkpoints<br/>work_dir: /weka/.../dataset-cache"]
        
        Check -->|"other"| S3["S3 Configuration<br/>root_dir: /tmp/...<br/>checkpoint_dir: s3://ai2-llm/checkpoints<br/>work_dir: /tmp/.../dataset-cache"]
    end
```

**Augusta cluster** (GCP): Uses Google Cloud Storage (`gs://`) for checkpoints and a local temporary directory for caching.

**AI2 clusters with Weka**: Uses the Weka shared filesystem for both checkpoints and caching, providing high-performance shared access across nodes.

**Default (S3)**: Uses S3 for checkpoints and local temporary storage for caching.

The `work_dir` is where `NumpyFSLDataset` caches tokenized sequences for fast repeated access.

Sources: [olmix/model/transformer.py:196-212]()

## WSDS Scheduler

Training uses the WSDS (Warmup-Stable-Decay-Stable) learning rate scheduler with multi-period checkpoints ([olmix/model/transformer.py:255-302]()):

```mermaid
graph LR
    subgraph "Scheduler Configuration"
        Params["num_params<br/>chinchilla_multiple"]
        
        Params --> CalcPeriods["Calculate checkpoint periods<br/>0.5xC, 1xC, 2xC, 4xC, ..."]
        
        CalcPeriods --> Periods["periods = [0.5, 1.0, 2.0, ...]<br/>up to chinchilla_multiple"]
        
        Periods --> Lengths["Calculate period_lengths<br/>tokens between checkpoints<br/>rounded to batch boundaries"]
        
        Lengths --> WSDS["WSDS Scheduler<br/>units: tokens<br/>warmup: min(N, 0.05*total)<br/>decay_fraction: 0.1<br/>period_lengths: [...]"]
    end
```

For example, with a 30M parameter model and `chinchilla_multiple=5.0`:
- **0.5xC**: Checkpoint at 300M tokens (0.5 * 20 * 30M)
- **1xC**: Checkpoint at 600M tokens (1.0 * 20 * 30M)
- **2xC**: Checkpoint at 1.2B tokens (2.0 * 20 * 30M)
- **4xC**: Checkpoint at 2.4B tokens (4.0 * 20 * 30M)
- **5xC**: Final training at 3B tokens (5.0 * 20 * 30M)

This allows analysis at intermediate Chinchilla multiples without running separate experiments. For very short runs (`chinchilla_multiple < 0.5`), the scheduler uses a single period for the full duration.

Sources: [olmix/model/transformer.py:255-302]()

## Model Architectures

The system supports OLMo2 and OLMo3 model families through factory functions in olmo-core ([olmix/model/transformer.py:62-88]()):

**OLMo2 Models**:
- `olmo2_1m`: 1M parameters
- `olmo2_30m`: 30M parameters (most common for swarms)
- `olmo2_60m`: 60M parameters
- `olmo2_190m`: 190M parameters
- `olmo2_1b`: 1B parameters
- `olmo2_7b`: 7B parameters

**OLMo3 Models**:
- `olmo3_1m` through `olmo3_32b`: Wide range from 1M to 32B parameters

The model factory is selected based on the `proxy_model_id` parameter in `TrainingConfig`. The tokenizer's `padded_vocab_size()` is used to configure the model's embedding layer.

Sources: [olmix/model/transformer.py:62-88](), [olmix/model/transformer.py:175-183]()

## Result Collection

After training completes, results are available in Weights & Biases under the project `olmix` with the experiment's `group_id`. The `fit` command queries W&B to retrieve metrics for all variants in the swarm:

```mermaid
graph LR
    subgraph "Training"
        Trainer["trainer.fit()"]
        Trainer --> WandBLog["WandBCallback<br/>project: olmix<br/>group: group_id<br/>name: run_name"]
    end
    
    subgraph "W&B Storage"
        WandBLog --> Runs["W&B Runs<br/>60 BPB metrics<br/>per variant"]
    end
    
    subgraph "Fit Pipeline"
        Runs --> LoadWandB["load_from_wandb()<br/>query by group_id"]
        LoadWandB --> Ratios["ratios.csv<br/>mixture weights"]
        LoadWandB --> Metrics["metrics.csv<br/>BPB scores"]
    end
    
    subgraph "Optimization"
        Ratios --> Fit["olmix fit<br/>regression + optimization"]
        Metrics --> Fit
        Fit --> Optimal["Optimal mixture weights"]
    end
```

The `group_id` serves as the key linking mechanism between:
1. Experiment generation (`olmix generate` assigns the same `group_id` to all variants)
2. Training execution (logged to W&B with this `group_id`)
3. Result retrieval (`olmix fit` queries W&B by `group_id`)
4. Analysis and optimization (all variants are analyzed together)

For details on data loading, see [Loading from WandB](#6.1) and [Loading from CSV](#6.2).

Sources: [olmix/model/transformer.py:319-324](), [olmix/fit/core.py]()

---

