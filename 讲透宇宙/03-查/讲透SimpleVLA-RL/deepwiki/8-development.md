<!-- source: DeepWiki mcp.deepwiki.com · repo PRIME-RL/SimpleVLA-RL · page 8 Development · fetched 2026-10-30 -->

# Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [SETUP.md](SETUP.md)

</details>



This section provides information for developers contributing to the SimpleVLA-RL project, including development environment setup, code organization, and architectural patterns. For detailed information about the project's internal structure and module organization, see [Project Structure](#5.1). For contribution guidelines and licensing information, see [Contributing](#5.2).

## Development Environment Overview

The SimpleVLA-RL codebase is designed for large-scale distributed training of Vision-Language-Action models using reinforcement learning. The development environment must support multi-GPU and multi-node training configurations with various distributed computing frameworks.

### Ignored Development Artifacts

The project excludes several types of development artifacts from version control, indicating the nature of the development workflow:

| Artifact Type | Examples | Purpose |
|---------------|----------|---------|
| Model Files | `**/*.pt`, `**/*.ckpt` | PyTorch model checkpoints |
| Training Outputs | `**/outputs`, `**/rollouts`, `**/wandb` | Training logs and experiment data |
| Build Artifacts | `**/_build/`, `build/`, `dist/` | Compiled packages and documentation |
| Data Files | `**/*.parquet`, `**/*.tar.gz` | Large datasets and compressed archives |
| Local Logs | `logs`, `log`, `outputs` | Development and debugging logs |

Sources: [.gitignore:1-127]()

## Core Development Architecture

The codebase follows a modular architecture with clear separation of concerns between training orchestration, model implementation, and distributed execution systems.

### Primary Development Components

```mermaid
graph TB
    subgraph "Development Entry Points"
        RunScript["run_openvla_oft_rl.sh"]
        AlignConfig["align.json"]
        MainPPO["verl.trainer.main_ppo"]
    end
    
    subgraph "Model Implementation Layer"
        ModelRegistry["verl.models.registry"]
        ParallelLlama["verl.models.llama.parallel_llama"]
        LlamaLoader["verl.models.llama.llama_loader"]
        LlamaSaver["verl.models.llama.llama_saver"]
    end
    
    subgraph "Distributed Execution Framework"
        DataProto["verl.utils.protocol.DataProto"]
        WorkerGroup["verl.worker.WorkerGroup"]
        RegisterDecorator["verl.worker.register"]
        ResourcePool["verl.worker.ResourcePool"]
    end
    
    subgraph "Layer Components"
        Attention["ParallelLlamaAttention"]
        MLP["ParallelLlamaMLP"]
        RMSNorm["ParallelLlamaRMSNorm"]
        DecoderLayer["ParallelLlamaDecoderLayer"]
    end
    
    RunScript --> MainPPO
    RunScript --> AlignConfig
    MainPPO --> ModelRegistry
    ModelRegistry --> ParallelLlama
    ParallelLlama --> LlamaLoader
    ParallelLlama --> LlamaSaver
    
    MainPPO --> DataProto
    DataProto --> WorkerGroup
    WorkerGroup --> RegisterDecorator
    WorkerGroup --> ResourcePool
    
    ParallelLlama --> Attention
    ParallelLlama --> MLP
    ParallelLlama --> RMSNorm
    ParallelLlama --> DecoderLayer
```

Sources: Based on high-level system architecture diagrams and inferred module structure

### Development Data Flow Pattern

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Script as "run_openvla_oft_rl.sh"
    participant Config as "align.json"
    participant Registry as "ModelRegistry.load_model_cls"
    participant Parallel as "ParallelLlamaForCausalLM"
    participant Worker as "WorkerGroup"
    participant Proto as "DataProto"
    
    Dev->>Script: "Execute training script"
    Script->>Config: "Load environment configuration"
    Script->>Registry: "Initialize model registry"
    Registry->>Parallel: "Load parallel model class"
    Parallel->>Worker: "Setup distributed workers"
    Worker->>Proto: "Initialize data protocol"
    Proto-->>Dev: "Training environment ready"
```

Sources: Based on training pipeline flow and system component relationships

## Key Development Patterns

### Model Registration Pattern

The codebase uses a registry pattern for dynamic model loading, allowing developers to add new model architectures without modifying core training logic:

```mermaid
graph LR
    subgraph "Model Registry System"
        RegisterCall["@register_model_cls"]
        LoadModelCls["load_model_cls()"]
        WeightLoader["get_weight_loader()"]
    end
    
    subgraph "Model Implementations"
        LlamaBase["ParallelLlamaModel"]
        LlamaCausal["ParallelLlamaForCausalLM"]
        LlamaRmPad["ParallelLlamaForCausalLMRmPad"]
        LlamaPP["ParallelLlamaForCausalLMPP"]
    end
    
    RegisterCall --> LlamaBase
    RegisterCall --> LlamaCausal
    RegisterCall --> LlamaRmPad
    RegisterCall --> LlamaPP
    
    LoadModelCls --> RegisterCall
    WeightLoader --> LoadModelCls
```

Sources: Based on model registry architecture and parallel model variants

### Distributed Execution Pattern

The veRL framework implements a decorator-based pattern for distributed function execution:

```mermaid
graph TB
    subgraph "Dispatch Decorators"
        RegisterDec["@register()"]
        DispatchMode["dispatch_mode parameter"]
    end
    
    subgraph "Execution Modes"
        OneToAll["ONE_TO_ALL"]
        AllToAll["ALL_TO_ALL"]
        MegatronComp["MEGATRON_COMPUTE"]
        DPComp["DP_COMPUTE"]
    end
    
    subgraph "Worker Management"
        WorkerGroupCls["WorkerGroup"]
        ResourcePoolCls["ResourcePool"]
        WorkerCls["Worker instances"]
    end
    
    RegisterDec --> DispatchMode
    DispatchMode --> OneToAll
    DispatchMode --> AllToAll
    DispatchMode --> MegatronComp
    DispatchMode --> DPComp
    
    OneToAll --> WorkerGroupCls
    AllToAll --> WorkerGroupCls
    MegatronComp --> WorkerGroupCls
    DPComp --> WorkerGroupCls
    
    WorkerGroupCls --> ResourcePoolCls
    WorkerGroupCls --> WorkerCls
```

Sources: Based on distributed execution framework and dispatch mechanism patterns

## Development Environment Requirements

### Framework Dependencies

The project integrates with several major frameworks that developers need to understand:

| Framework | Purpose | Integration Point |
|-----------|---------|-------------------|
| Megatron-LM | Model parallelization | `ParallelLlama*` classes |
| PyTorch | Deep learning backend | All model and training components |
| Hugging Face | Model loading/saving | Weight loader registry |
| veRL | RL training framework | Core training loop |
| LIBERO | Robotics environment | Environment integration |
| Weights & Biases | Experiment tracking | Training metrics logging |

### Development File Structure

The codebase follows a hierarchical module organization:

```mermaid
graph TB
    subgraph "verl Package Structure"
        VerlRoot["verl/"]
        ModelsDir["verl/models/"]
        WorkerDir["verl/worker/"]
        UtilsDir["verl/utils/"]
        TrainerDir["verl/trainer/"]
    end
    
    subgraph "Model Submodules"
        LlamaDir["verl/models/llama/"]
        RegistryFile["verl/models/registry.py"]
        InitFile["verl/models/__init__.py"]
    end
    
    subgraph "Core Implementation Files"
        ParallelLlamaFile["parallel_llama.py"]
        LoaderFile["llama_loader.py"]
        SaverFile["llama_saver.py"]
    end
    
    VerlRoot --> ModelsDir
    VerlRoot --> WorkerDir
    VerlRoot --> UtilsDir
    VerlRoot --> TrainerDir
    
    ModelsDir --> LlamaDir
    ModelsDir --> RegistryFile
    ModelsDir --> InitFile
    
    LlamaDir --> ParallelLlamaFile
    LlamaDir --> LoaderFile
    LlamaDir --> SaverFile
```

Sources: [verl/models/__init__.py:1-14]()

## License and Development Rights

The project is released under the MIT License, providing broad permissions for development and distribution. The license grants developers the right to use, modify, publish, distribute, sublicense, and sell copies of the software without restriction, subject to including the copyright notice and license text in all copies.

The copyright is held by PRIME-RL as of 2025, indicating active development and maintenance of the codebase.

Sources: [LICENSE:1-22]()

---

