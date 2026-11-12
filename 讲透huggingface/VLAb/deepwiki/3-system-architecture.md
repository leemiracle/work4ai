<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/VLAb · page 3 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)
- [VLAb.png](VLAb.png)

</details>



## Purpose and Scope

This document describes the high-level architecture of VLAb, explaining how major components are organized and interact to enable Vision-Language-Action (VLA) model pretraining. The architecture is designed around four core pillars: configuration management, data processing, model training, and distributed execution.

For detailed information about specific subsystems, see:
- Dataset handling and multi-dataset aggregation: [Dataset System](#4)
- Model architecture and training strategies: [Policy and Model System](#5)
- Configuration parameters and options: [Configuration System](#6)
- Training script and execution flow: [Training Execution](#7)
- HuggingFace Hub and experiment tracking: [External Integrations](#9)

---

## Architectural Overview

VLAb follows a layered architecture with clear separation of concerns. The system is built on top of the HuggingFace ecosystem, leveraging `datasets`, `transformers`, `accelerate`, and `peft` libraries for core functionality.

### Core System Layers

```mermaid
graph TB
    subgraph "User Interface Layer"
        CLI["Command Line Interface<br/>accelerate launch + train.py"]
        ConfigFiles["Configuration Files<br/>YAML + Command Line Args"]
    end
    
    subgraph "Configuration Layer"
        TrainPipelineConfig["TrainPipelineConfig<br/>src/lerobot/configs/train.py"]
        DatasetConfig["DatasetConfig<br/>src/lerobot/configs/dataset.py"]
        PolicyConfig["PolicyConfig<br/>src/lerobot/configs/policy.py"]
        OptimConfig["OptimizerConfig<br/>src/lerobot/configs/optim.py"]
    end
    
    subgraph "Data Processing Layer"
        DatasetFactory["make_dataset()<br/>src/lerobot/datasets/factory.py"]
        LeRobotDataset["LeRobotDataset<br/>src/lerobot/datasets/lerobot_dataset.py"]
        MultiLeRobotDataset["MultiLeRobotDataset<br/>src/lerobot/datasets/multi_lerobot_dataset.py"]
        VideoUtils["Video Processing<br/>src/lerobot/common/datasets/video_utils.py"]
    end
    
    subgraph "Model Layer"
        PolicyFactory["make_policy()<br/>src/lerobot/policies/factory.py"]
        SmolVLA2["SmolVLA2Policy<br/>src/lerobot/policies/smolvla2/modeling_smolvla2.py"]
        SmolVLM["SmolVLM Base<br/>Via transformers library"]
    end
    
    subgraph "Training Orchestration Layer"
        TrainScript["train()<br/>src/lerobot/scripts/train.py"]
        UpdatePolicy["update_policy()<br/>src/lerobot/scripts/train.py"]
        Accelerator["Accelerator<br/>accelerate.Accelerator"]
    end
    
    subgraph "Execution Infrastructure"
        LocalExec["Local Execution<br/>accelerate_configs/single_gpu.yaml<br/>accelerate_configs/multi_gpu.yaml"]
        SlurmExec["SLURM Execution<br/>examples/scripts/*.slurm"]
    end
    
    CLI --> ConfigFiles
    ConfigFiles --> TrainPipelineConfig
    
    TrainPipelineConfig --> DatasetConfig
    TrainPipelineConfig --> PolicyConfig
    TrainPipelineConfig --> OptimConfig
    
    DatasetConfig --> DatasetFactory
    DatasetFactory --> LeRobotDataset
    DatasetFactory --> MultiLeRobotDataset
    VideoUtils --> LeRobotDataset
    
    PolicyConfig --> PolicyFactory
    PolicyFactory --> SmolVLA2
    SmolVLA2 --> SmolVLM
    
    TrainPipelineConfig --> TrainScript
    LeRobotDataset --> TrainScript
    MultiLeRobotDataset --> TrainScript
    SmolVLA2 --> TrainScript
    TrainScript --> UpdatePolicy
    Accelerator --> TrainScript
    
    LocalExec --> Accelerator
    SlurmExec --> Accelerator
```

**Sources:** [README.md:289-309](), [README.md:1-43]()

---

## Component Relationships

### Configuration to Execution Flow

The system uses a declarative configuration approach where `TrainPipelineConfig` acts as the master orchestrator, aggregating all subsystem configurations.

```mermaid
graph LR
    subgraph "Configuration Construction"
        CLIArgs["CLI Arguments<br/>--policy.type=smolvla2<br/>--dataset.repo_id=..."]
        YAMLConfig["YAML Config Files<br/>accelerate_configs/*.yaml"]
        TrainPipelineConfig["TrainPipelineConfig<br/>instantiate()"]
    end
    
    subgraph "Component Factories"
        MakeDataset["make_dataset()<br/>returns LeRobotDataset or<br/>MultiLeRobotDataset"]
        MakePolicy["make_policy()<br/>returns SmolVLA2Policy"]
        MakeOptimizer["Optimizer Creation<br/>AdamW from torch.optim"]
        MakeScheduler["Scheduler Creation<br/>get_scheduler from transformers"]
    end
    
    subgraph "Runtime Objects"
        DatasetObj["Dataset Object<br/>LeRobotDataset/<br/>MultiLeRobotDataset"]
        DataLoader["DataLoader<br/>torch.utils.data.DataLoader"]
        PolicyObj["Policy Object<br/>SmolVLA2Policy"]
        OptimizerObj["Optimizer<br/>torch.optim.AdamW"]
        SchedulerObj["Scheduler<br/>transformers LR Scheduler"]
    end
    
    subgraph "Training Loop"
        TrainFunction["train()<br/>Main training loop"]
        UpdatePolicyFn["update_policy()<br/>Single training step"]
    end
    
    CLIArgs --> TrainPipelineConfig
    YAMLConfig --> TrainPipelineConfig
    
    TrainPipelineConfig --> MakeDataset
    TrainPipelineConfig --> MakePolicy
    TrainPipelineConfig --> MakeOptimizer
    TrainPipelineConfig --> MakeScheduler
    
    MakeDataset --> DatasetObj
    DatasetObj --> DataLoader
    MakePolicy --> PolicyObj
    MakeOptimizer --> OptimizerObj
    MakeScheduler --> SchedulerObj
    
    DataLoader --> TrainFunction
    PolicyObj --> TrainFunction
    OptimizerObj --> TrainFunction
    SchedulerObj --> TrainFunction
    
    TrainFunction --> UpdatePolicyFn
```

**Sources:** [README.md:96-120](), [README.md:163-195]()

---

## Data Pipeline Architecture

The data pipeline transforms raw datasets from HuggingFace Hub or local storage into batched tensors ready for model consumption.

### Dataset Factory and Loading Chain

```mermaid
graph TB
    subgraph "Data Sources"
        HFHub["HuggingFace Hub<br/>datasets.load_dataset()"]
        LocalRoot["Local Storage<br/>--dataset.root"]
    end
    
    subgraph "Factory Layer"
        MakeDataset["make_dataset()<br/>src/lerobot/datasets/factory.py"]
        ParseRepoID["Parse repo_id<br/>Comma-separated list"]
        ResolveDatasets["Resolve Dataset Paths<br/>hub_dataset_path() or local path"]
    end
    
    subgraph "Metadata Layer"
        LeRobotMetadata["LeRobotDatasetMetadata<br/>src/lerobot/common/datasets/lerobot_dataset/lerobot_dataset.py"]
        LoadInfo["load_info()<br/>Load meta_info/info.json"]
        ResolveDeltaTS["resolve_delta_timestamps()<br/>Compute temporal offsets"]
    end
    
    subgraph "Dataset Objects"
        SingleDS["LeRobotDataset<br/>src/lerobot/datasets/lerobot_dataset.py<br/>__getitem__() returns single frame"]
        MultiDS["MultiLeRobotDataset<br/>src/lerobot/datasets/multi_lerobot_dataset.py<br/>Aggregates multiple datasets"]
    end
    
    subgraph "Sampling Layer"
        EpisodeSampler["EpisodeAwareSampler<br/>src/lerobot/common/datasets/sampler.py<br/>Respects episode boundaries"]
        WeightedSampling["Weighted Sampling<br/>--dataset.sampling_weights"]
    end
    
    subgraph "Loading and Batching"
        DataLoader["torch.utils.data.DataLoader<br/>num_workers, batch_size"]
        CollateFn["multidataset_collate_fn()<br/>src/lerobot/datasets/multi_lerobot_dataset.py<br/>Pads heterogeneous features"]
    end
    
    HFHub --> MakeDataset
    LocalRoot --> MakeDataset
    
    MakeDataset --> ParseRepoID
    ParseRepoID --> ResolveDatasets
    
    ResolveDatasets --> LeRobotMetadata
    LeRobotMetadata --> LoadInfo
    LoadInfo --> ResolveDeltaTS
    
    ResolveDeltaTS --> SingleDS
    ResolveDeltaTS --> MultiDS
    
    SingleDS --> EpisodeSampler
    MultiDS --> EpisodeSampler
    WeightedSampling --> MultiDS
    
    EpisodeSampler --> DataLoader
    CollateFn --> DataLoader
```

**Sources:** [README.md:147-161](), [README.md:176-195]()

The `make_dataset` factory function determines whether to instantiate a single `LeRobotDataset` or a `MultiLeRobotDataset` based on the number of datasets specified in `--dataset.repo_id`. The `MultiLeRobotDataset` handles feature alignment across heterogeneous datasets through automatic padding.

---

## Model Architecture Components

### Policy Factory and Model Instantiation

```mermaid
graph TB
    subgraph "Policy Configuration"
        PolicyConfig["PolicyConfig<br/>--policy.type=smolvla2<br/>--policy.repo_id"]
        LoadWeights["--policy.load_vlm_weights<br/>Load pretrained VLM"]
        TrainStrategy["Training Strategy Flags<br/>--policy.train_expert_only<br/>--policy.freeze_vision_encoder"]
        PEFTConfig["PEFT Configuration<br/>--policy.peft_method=lora<br/>--policy.peft_config"]
    end
    
    subgraph "Model Factory"
        MakePolicy["make_policy()<br/>src/lerobot/policies/factory.py"]
        LoadPretrained["Load from Hub<br/>PreTrainedModel.from_pretrained()"]
        InitRandom["Initialize Random<br/>SmolVLA2Config()"]
    end
    
    subgraph "SmolVLA2 Components"
        VLMModel["SmolVLM Base<br/>self.vlm<br/>Vision + Language Model"]
        ExpertModel["Expert Model<br/>self.expert<br/>Smaller LM for actions"]
        VisionEncoder["Vision Encoder<br/>self.vlm.vision_model<br/>Process images/videos"]
        Connector["Connector<br/>self.vlm.connector<br/>Visual token projection"]
        TextModel["Text Model<br/>self.vlm.text_model<br/>24 transformer layers"]
        ExpertLayers["Expert Layers<br/>self.expert.model.layers<br/>6 layers with optional cross-attn"]
    end
    
    subgraph "Training Modes"
        SelfAttention["Self-Attention Mode<br/>attention_mode='self'<br/>Independent processing"]
        CrossAttention["Cross-Attention Mode<br/>attention_mode='cross'<br/>Expert attends to VLM"]
    end
    
    PolicyConfig --> MakePolicy
    LoadWeights --> MakePolicy
    TrainStrategy --> MakePolicy
    PEFTConfig --> MakePolicy
    
    MakePolicy --> LoadPretrained
    MakePolicy --> InitRandom
    
    LoadPretrained --> VLMModel
    LoadPretrained --> ExpertModel
    
    VLMModel --> VisionEncoder
    VLMModel --> Connector
    VLMModel --> TextModel
    
    ExpertModel --> ExpertLayers
    
    ExpertLayers --> SelfAttention
    ExpertLayers --> CrossAttention
    TextModel --> CrossAttention
```

**Sources:** [README.md:96-120]()

The `SmolVLA2Policy` class in [src/lerobot/policies/smolvla2/modeling_smolvla2.py]() combines a full SmolVLM model with a smaller expert model. The expert model has reduced hidden dimensions (controlled by `--policy.expert_width_multiplier`) and fewer layers (controlled by `--policy.num_expert_layers`).

---

## Training Execution Flow

### Main Training Loop

```mermaid
graph TB
    subgraph "Initialization Phase"
        ParseArgs["Parse Arguments<br/>parse_train_args()"]
        InitAccelerator["Initialize Accelerator<br/>accelerate.Accelerator()"]
        CreateDataset["Create Dataset<br/>make_dataset()"]
        CreatePolicy["Create Policy<br/>make_policy()"]
        CreateOptimizer["Create Optimizer<br/>torch.optim.AdamW"]
        CreateScheduler["Create Scheduler<br/>transformers.get_scheduler()"]
        PrepareAccel["Prepare for Distributed<br/>accelerator.prepare()"]
    end
    
    subgraph "Training Loop"
        IterateDataLoader["Iterate DataLoader<br/>for batch in dataloader"]
        UpdatePolicyFn["update_policy()<br/>src/lerobot/scripts/train.py:300-400"]
        ForwardPass["Forward Pass<br/>policy.forward(batch)"]
        ComputeLoss["Compute Loss<br/>loss.backward()"]
        ClipGradients["Clip Gradients<br/>accelerator.clip_grad_norm_()"]
        OptimizerStep["Optimizer Step<br/>optimizer.step()"]
        SchedulerStep["Scheduler Step<br/>scheduler.step()"]
        LogMetrics["Log Metrics<br/>WandB / TrackIO"]
    end
    
    subgraph "Checkpointing"
        SaveCheckpoint["Save Checkpoint<br/>Every --save_freq steps"]
        SaveLast["Update 'last' symlink<br/>outputs/checkpoints/last"]
    end
    
    subgraph "Resumption"
        CheckResume["Check --resume flag"]
        LoadCheckpoint["Load Checkpoint<br/>accelerator.load_state()"]
    end
    
    ParseArgs --> InitAccelerator
    InitAccelerator --> CheckResume
    CheckResume --> LoadCheckpoint
    CheckResume --> CreateDataset
    LoadCheckpoint --> CreateDataset
    
    CreateDataset --> CreatePolicy
    CreatePolicy --> CreateOptimizer
    CreateOptimizer --> CreateScheduler
    CreateScheduler --> PrepareAccel
    
    PrepareAccel --> IterateDataLoader
    IterateDataLoader --> UpdatePolicyFn
    
    UpdatePolicyFn --> ForwardPass
    ForwardPass --> ComputeLoss
    ComputeLoss --> ClipGradients
    ClipGradients --> OptimizerStep
    OptimizerStep --> SchedulerStep
    SchedulerStep --> LogMetrics
    
    LogMetrics --> SaveCheckpoint
    SaveCheckpoint --> SaveLast
    SaveLast --> IterateDataLoader
```

**Sources:** [README.md:96-120]()

The `train()` function in [src/lerobot/scripts/train.py]() orchestrates the entire training process. It uses the Accelerate library's `Accelerator` class to handle distributed training transparently across single GPU, multi-GPU, and multi-node configurations.

### Update Policy Function

The `update_policy()` function handles a single training step:

| Step | Function | Description |
|------|----------|-------------|
| 1 | Forward Pass | Execute `policy.forward(batch)` to compute predictions and loss |
| 2 | Backward Pass | Call `loss.backward()` or `accelerator.backward(loss)` for gradient computation |
| 3 | Gradient Clipping | Apply `accelerator.clip_grad_norm_(policy.parameters(), max_norm=1.0)` |
| 4 | Optimizer Step | Execute `optimizer.step()` to update parameters |
| 5 | Zero Gradients | Call `optimizer.zero_grad()` to reset gradients |
| 6 | Scheduler Step | Execute `scheduler.step()` to update learning rate |

**Sources:** [README.md:96-120]()

---

## Configuration System Hierarchy

VLAb uses a hierarchical configuration system with `TrainPipelineConfig` as the root configuration class.

```mermaid
graph TB
    subgraph "Master Configuration"
        TrainPipeline["TrainPipelineConfig<br/>src/lerobot/configs/train.py"]
    end
    
    subgraph "Subsystem Configurations"
        Dataset["DatasetConfig<br/>src/lerobot/configs/dataset.py<br/>repo_id, root, sampling_weights"]
        Policy["PolicyConfig<br/>src/lerobot/configs/policy.py<br/>type, repo_id, peft_method"]
        Optimizer["OptimizerConfig<br/>src/lerobot/configs/optim.py<br/>lr, betas, weight_decay"]
        Scheduler["LRSchedulerConfig<br/>src/lerobot/configs/optim.py<br/>warmup_steps, scheduler_type"]
        Eval["EvalConfig<br/>src/lerobot/configs/eval.py<br/>n_episodes, batch_size"]
        WandB["WandBConfig<br/>src/lerobot/configs/train.py<br/>project, entity, mode"]
        TrackIO["TrackIOConfig<br/>src/lerobot/configs/train.py<br/>project, space_id"]
    end
    
    subgraph "Nested Configurations"
        ImageTransforms["ImageTransformsConfig<br/>src/lerobot/configs/dataset.py<br/>Augmentation pipeline"]
        PEFTConfig["LoRAConfig / PEFTConfig<br/>Via peft library<br/>r, alpha, target_modules"]
        AttentionConfig["Attention Parameters<br/>attention_mode, num_expert_layers"]
    end
    
    TrainPipeline --> Dataset
    TrainPipeline --> Policy
    TrainPipeline --> Optimizer
    TrainPipeline --> Scheduler
    TrainPipeline --> Eval
    TrainPipeline --> WandB
    TrainPipeline --> TrackIO
    
    Dataset --> ImageTransforms
    Policy --> PEFTConfig
    Policy --> AttentionConfig
```

**Sources:** [README.md:96-120](), [README.md:176-195]()

Configuration values can be specified through:
1. Command-line arguments: `--policy.type=smolvla2`
2. Configuration files: YAML files loaded via `--config_path`
3. Default values: Defined in configuration classes

Command-line arguments take precedence over file-based configuration, which takes precedence over defaults.

---

## Distributed Training Infrastructure

### Accelerate Integration

```mermaid
graph LR
    subgraph "Configuration Layer"
        AccelConfig["Accelerate Config<br/>accelerate_configs/single_gpu.yaml<br/>accelerate_configs/multi_gpu.yaml"]
        TrainConfig["Training Config<br/>TrainPipelineConfig"]
    end
    
    subgraph "Accelerate Library"
        Accelerator["Accelerator Object<br/>accelerate.Accelerator"]
        Prepare["accelerator.prepare()<br/>Wraps model, optimizer, dataloader"]
        Backward["accelerator.backward()<br/>Gradient synchronization"]
        ClipGrad["accelerator.clip_grad_norm_()<br/>Distributed gradient clipping"]
        SaveState["accelerator.save_state()<br/>Save distributed checkpoint"]
        LoadState["accelerator.load_state()<br/>Load distributed checkpoint"]
    end
    
    subgraph "Execution Backends"
        SingleGPU["Single GPU<br/>MULTI_GPU backend: NO"]
        MultiGPU["Multi-GPU<br/>MULTI_GPU backend: YES<br/>DDP or FSDP"]
        MultiNode["Multi-Node<br/>SLURM + DeepSpeed/FSDP"]
    end
    
    subgraph "Runtime"
        TrainScript["train()<br/>src/lerobot/scripts/train.py"]
        TrainingLoop["Training Loop<br/>Transparent distributed execution"]
    end
    
    AccelConfig --> Accelerator
    TrainConfig --> TrainScript
    
    Accelerator --> Prepare
    Prepare --> TrainScript
    
    TrainScript --> Backward
    TrainScript --> ClipGrad
    TrainScript --> SaveState
    TrainScript --> LoadState
    TrainScript --> TrainingLoop
    
    Accelerator --> SingleGPU
    Accelerator --> MultiGPU
    Accelerator --> MultiNode
```

**Sources:** [README.md:163-174](), [README.md:202-218]()

The Accelerate library provides a unified interface for distributed training. The configuration file (e.g., `accelerate_configs/multi_gpu.yaml`) specifies:
- `compute_environment`: LOCAL_MACHINE or CLUSTER
- `mixed_precision`: "no", "fp16", or "bf16"
- `num_processes`: Number of GPUs/processes
- `multi_gpu_backend`: DDP, FSDP, or DeepSpeed

---

## External System Integration

### HuggingFace Ecosystem Integration

```mermaid
graph TB
    subgraph "VLAb Core"
        TrainScript["train.py<br/>Training orchestrator"]
        DatasetFactory["make_dataset()<br/>Dataset factory"]
        PolicyFactory["make_policy()<br/>Policy factory"]
    end
    
    subgraph "HuggingFace Hub"
        HubDatasets["HuggingFace Hub Datasets<br/>datasets.load_dataset()"]
        HubModels["HuggingFace Hub Models<br/>PreTrainedModel.from_pretrained()"]
        PushToHub["Push to Hub<br/>policy.push_to_hub()"]
    end
    
    subgraph "HuggingFace Libraries"
        DatasetsLib["datasets library<br/>Parquet-backed loading"]
        TransformersLib["transformers library<br/>SmolVLM, PreTrainedModel"]
        AccelerateLib["accelerate library<br/>Distributed training"]
        PEFTLib["peft library<br/>LoRA, PrefixTuning"]
    end
    
    subgraph "Experiment Tracking"
        WandB["Weights & Biases<br/>wandb.init(), wandb.log()"]
        TrackIO["TrackIO<br/>trackio.init(), trackio.log()"]
    end
    
    subgraph "Community Datasets"
        CDv1["community_dataset_v1<br/>128 datasets, 119 GB"]
        CDv2["community_dataset_v2<br/>340 datasets, 59 GB"]
    end
    
    DatasetFactory --> DatasetsLib
    DatasetFactory --> HubDatasets
    CDv1 --> HubDatasets
    CDv2 --> HubDatasets
    
    PolicyFactory --> TransformersLib
    PolicyFactory --> HubModels
    PolicyFactory --> PEFTLib
    
    TrainScript --> AccelerateLib
    TrainScript --> WandB
    TrainScript --> TrackIO
    TrainScript --> PushToHub
```

**Sources:** [README.md:1-43](), [README.md:122-145](), [README.md:249-255]()

VLAb is deeply integrated with the HuggingFace ecosystem:

| Integration | Purpose | Key Functions |
|-------------|---------|---------------|
| **datasets** | Load and process robotics datasets | `datasets.load_dataset()`, Parquet backend |
| **transformers** | Load pretrained VLMs, model architectures | `PreTrainedModel.from_pretrained()`, `AutoModel` |
| **accelerate** | Distributed training abstraction | `Accelerator()`, `prepare()`, `backward()` |
| **peft** | Parameter-efficient fine-tuning | `LoraConfig`, `get_peft_model()` |

---

## Checkpoint and State Management

### Checkpoint Structure

Checkpoints are saved to `--output_dir/checkpoints/` with the following structure:

```
outputs/training/checkpoints/
├── 010000/                    # Checkpoint at step 10,000
│   ├── optimizer.bin          # Optimizer state
│   ├── scheduler.bin          # LR scheduler state
│   ├── random_states.pkl      # Random number generator states
│   ├── pytorch_model.bin      # Model weights
│   └── config.json            # Model configuration
├── 020000/                    # Checkpoint at step 20,000
├── last -> 020000             # Symlink to latest checkpoint
└── config.pkl                 # Training configuration
```

**Sources:** [README.md:220-227]()

The `accelerator.save_state()` function in [src/lerobot/scripts/train.py]() handles checkpoint saving, ensuring all distributed state is properly synchronized and saved. The `--resume` flag enables training resumption from the latest checkpoint.

---

## Summary

VLAb's architecture is organized into distinct layers:

1. **Configuration Layer**: Declarative system using `TrainPipelineConfig` and nested configs
2. **Data Processing Layer**: Factory-based dataset instantiation with `make_dataset()` and multi-dataset support
3. **Model Layer**: Factory-based policy instantiation with `make_policy()` and SmolVLA2 architecture
4. **Training Orchestration**: `train()` function and `update_policy()` step function with Accelerate integration
5. **Execution Infrastructure**: Support for local GPU and SLURM cluster execution

The system emphasizes modularity, allowing each component to be independently configured and tested while maintaining clean interfaces between layers. All components integrate with the HuggingFace ecosystem for model/dataset access and experiment tracking.

**Sources:** [README.md:1-309](), [README.md:289-309]()

---

