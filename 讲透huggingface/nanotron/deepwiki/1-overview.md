<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/nanotron · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/3d_parallelism.md](docs/3d_parallelism.md)
- [docs/docs.md](docs/docs.md)
- [pyproject.toml](pyproject.toml)
- [src/nanotron/__init__.py](src/nanotron/__init__.py)

</details>



## Purpose and Scope

Nanotron is a distributed training framework designed for pretraining large language models with advanced parallelism strategies. It provides a comprehensive system for training transformer-based models across multiple GPUs and nodes, supporting 3D parallelism (data parallel, tensor parallel, and pipeline parallel), multiple model architectures, and performance optimizations for large-scale training workloads.

This document provides a high-level overview of the Nanotron framework architecture, core components, and supported features. For specific implementation details of distributed training strategies, see [Distributed Training](#4). For model architecture specifics, see [Supported Models](#3). For configuration and workflow details, see [Training Configuration](#6).

## Core Architecture

Nanotron is built around a modular architecture that separates concerns between training orchestration, model implementations, data pipelines, and distributed communication. The framework enables efficient scaling from single-GPU training to multi-node clusters with thousands of GPUs.

### System Architecture Overview

```mermaid
graph TB
    subgraph "Training Orchestration"
        DT["DistributedTrainer<br/>Main Training Loop"]
        Config["Config<br/>YAML/Python Configuration"]
        Checkpoint["CheckpointManager<br/>State Persistence"]
    end
    
    subgraph "Model Layer"
        NanotronModel["NanotronModel<br/>Base Model Class"]
        Qwen2["Qwen2ForTraining"]
        Llama["LlamaForTraining"] 
        Mamba["MambaForTraining"]
        MoE["LlaMoEForTraining"]
    end
    
    subgraph "Distributed Computing"
        ParallelContext["ParallelContext<br/>Process Group Manager"]
        PipelineBlock["PipelineBlock<br/>Pipeline Stage Wrapper"]
        TensorParallel["TensorParallelLinear<br/>Sharded Operations"]
    end
    
    subgraph "Data Pipeline"
        Nanoset["Nanoset<br/>Large Dataset Handler"]
        DataLoader["DataLoader<br/>Distributed Sampling"]
        Collator["DataCollator<br/>Batch Assembly"]
    end
    
    subgraph "Infrastructure"
        SlurmLauncher["SlurmLauncher<br/>Multi-node Jobs"]
        Logging["LoggerManager<br/>Training Metrics"]
        RandomStates["RandomStates<br/>Deterministic Training"]
    end
    
    Config --> DT
    DT --> NanotronModel
    DT --> ParallelContext
    DT --> DataLoader
    NanotronModel --> Qwen2
    NanotronModel --> Llama
    NanotronModel --> Mamba
    NanotronModel --> MoE
    ParallelContext --> PipelineBlock
    ParallelContext --> TensorParallel
    DataLoader --> Nanoset
    DataLoader --> Collator
    DT --> Checkpoint
    SlurmLauncher --> Config
    DT --> Logging
    DT --> RandomStates
```

**Sources:** [README.md:29-33](), [src/nanotron/__init__.py](), [docs/docs.md:14-35]()

### Training Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant run_train as "run_train.py"
    participant DistributedTrainer
    participant ParallelContext
    participant Model as "NanotronModel"
    participant DataLoader
    participant PipelineEngine
    
    User->>run_train: "torchrun --nproc_per_node=8 run_train.py"
    run_train->>DistributedTrainer: "Initialize with config"
    DistributedTrainer->>ParallelContext: "Setup 3D parallelism topology"
    DistributedTrainer->>Model: "Create model with PipelineBlocks"
    DistributedTrainer->>DataLoader: "Initialize distributed data loading"
    
    loop Training Steps
        DistributedTrainer->>DataLoader: "Get next batch"
        DistributedTrainer->>PipelineEngine: "Execute forward/backward"
        PipelineEngine->>Model: "Run pipeline stages"
        Model-->>PipelineEngine: "Return loss/gradients"
        DistributedTrainer->>DistributedTrainer: "Optimizer step"
        
        alt Checkpoint Interval
            DistributedTrainer->>DistributedTrainer: "Save checkpoint"
        end
    end
```

**Sources:** [README.md:94-98](), [docs/3d_parallelism.md:355-361]()

## Key Components

### DistributedTrainer

The `DistributedTrainer` class serves as the central orchestrator for training execution, managing the training loop, checkpointing, logging, and coordination between all system components. It handles the lifecycle from initialization through training completion.

**Sources:** [docs/3d_parallelism.md:302-326]()

### ParallelContext

The `ParallelContext` manages distributed process groups for 3D parallelism, providing access to tensor parallel (`tp_pg`), pipeline parallel (`pp_pg`), and data parallel (`dp_pg`) process groups. It maintains a 5D rank matrix that maps between local 3D coordinates and global ranks.

**Sources:** [docs/docs.md:14-35]()

### NanotronModel

The `NanotronModel` base class defines the interface for all model implementations, providing methods for parameter initialization, tied parameter management, and pipeline stage assignment. All supported model architectures inherit from this base class.

**Sources:** [docs/3d_parallelism.md:74-76]()

### PipelineBlock

`PipelineBlock` encapsulates computation stages for pipeline parallelism, handling lazy module instantiation, inter-stage communication via `TensorPointer` objects, and device-specific execution. It enables transparent distribution of model layers across multiple devices.

**Sources:** [docs/docs.md:144-191]()

## 3D Parallelism Implementation

```mermaid
graph TB
    subgraph "Tensor Parallelism"
        TPLinear["TensorParallelLinear<br/>Column/Row Linear"]
        TPVocab["ParallelVocabulary<br/>Sharded Embeddings"]
        TPCrossEntropy["sharded_cross_entropy<br/>Distributed Loss"]
    end
    
    subgraph "Pipeline Parallelism"
        PB1["PipelineBlock<br/>Stage 0"]
        PB2["PipelineBlock<br/>Stage 1"] 
        PB3["PipelineBlock<br/>Stage N"]
        TensorPointer["TensorPointer<br/>Inter-stage References"]
        PipelineEngine["PipelineEngine<br/>AFAB/1F1B Scheduling"]
    end
    
    subgraph "Data Parallelism"
        DDP["DistributedDataParallel<br/>Gradient Synchronization"]
        ZeRO["ZeRODistributedOptimizer<br/>State Sharding"]
        Samplers["MegatronPretrainingSampler<br/>Data Distribution"]
    end
    
    subgraph "Process Groups"
        world_pg["world_pg<br/>All Ranks"]
        tp_pg["tp_pg<br/>Tensor Parallel Group"]
        pp_pg["pp_pg<br/>Pipeline Parallel Group"]
        dp_pg["dp_pg<br/>Data Parallel Group"]
    end
    
    ParallelContext --> world_pg
    ParallelContext --> tp_pg
    ParallelContext --> pp_pg  
    ParallelContext --> dp_pg
    
    tp_pg --> TPLinear
    tp_pg --> TPVocab
    tp_pg --> TPCrossEntropy
    
    pp_pg --> PB1
    pp_pg --> PB2
    pp_pg --> PB3
    PB1 --> TensorPointer
    PB2 --> TensorPointer
    PipelineEngine --> PB1
    PipelineEngine --> PB2
    PipelineEngine --> PB3
    
    dp_pg --> DDP
    dp_pg --> ZeRO
    dp_pg --> Samplers
```

**Sources:** [docs/3d_parallelism.md:3-48](), [docs/docs.md:121-143](), [docs/3d_parallelism.md:99-205]()

## Supported Features

Nanotron provides comprehensive support for large-scale distributed training with the following key capabilities:

| Feature Category | Supported Components |
|------------------|---------------------|
| **Parallelism** | 3D Parallelism (DP+TP+PP), Expert Parallelism for MoEs |
| **Pipeline Scheduling** | AFAB (All Forward All Backward), 1F1B (One Forward One Backward) |
| **Model Architectures** | Llama, Qwen2, Mamba (State Space Models), Mixture of Experts |
| **Optimization** | ZeRO-1 Optimizer, FP32 Gradient Accumulation, Custom Optimizers |
| **Memory Management** | Parameter Tying/Sharding, Custom Module Checkpointing |
| **Performance** | FP8 Quantization, Flash Attention, Custom CUDA Kernels |
| **Data Pipeline** | Nanoset (Pre-tokenized), Custom DataLoaders, DoReMi Domain Reweighting |
| **Infrastructure** | SLURM Integration, S3 Checkpointing, Comprehensive Logging |

**Sources:** [README.md:166-185](), [pyproject.toml:16-26]()

### Model Support Matrix

```mermaid
graph LR
    subgraph "Transformer Models"
        Llama["LlamaForTraining<br/>src/nanotron/models/llama.py"]
        Qwen2["Qwen2ForTraining<br/>src/nanotron/models/qwen2.py"]
    end
    
    subgraph "State Space Models"
        Mamba["MambaForTraining<br/>src/nanotron/models/mamba.py"]
    end
    
    subgraph "Mixture of Experts"
        LlaMoE["LlaMoEForTraining<br/>src/nanotron/models/llama_moe.py"]
    end
    
    subgraph "Conversion Utilities"
        HF2Nano["HF to Nanotron<br/>Checkpoint Conversion"]
        Nano2HF["Nanotron to HF<br/>Export for Inference"]
    end
    
    NanotronModel --> Llama
    NanotronModel --> Qwen2
    NanotronModel --> Mamba
    NanotronModel --> LlaMoE
    
    Llama --> HF2Nano
    Qwen2 --> HF2Nano
    Mamba --> HF2Nano
    LlaMoE --> HF2Nano
    
    HF2Nano --> Nano2HF
```

**Sources:** [README.md:144-153]()

## Getting Started

The framework provides multiple entry points for different use cases:

- **Training**: Use `run_train.py` with YAML or Python configuration files
- **Generation**: Use `run_generate.py` for inference from checkpoints  
- **Multi-node**: SLURM integration for cluster-scale training
- **Custom Data**: Extensible data pipeline for custom datasets

For detailed setup instructions, see [Getting Started](#1.1). For training your first model, see [Training Workflow](#6.1).

**Sources:** [README.md:90-105](), [README.md:38-89]()

---

