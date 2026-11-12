<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/SAGE · page 1 Getting Started · fetched 2026-10-26 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [rl_train/trainer/config/_generated_ppo_megatron_trainer.yaml](rl_train/trainer/config/_generated_ppo_megatron_trainer.yaml)
- [rl_train/trainer/config/_generated_ppo_trainer.yaml](rl_train/trainer/config/_generated_ppo_trainer.yaml)
- [rl_train/trainer/config/critic/megatron_critic.yaml](rl_train/trainer/config/critic/megatron_critic.yaml)
- [verl/recipe/langgraph_agent/__init__.py](verl/recipe/langgraph_agent/__init__.py)
- [verl/recipe/r1/__init__.py](verl/recipe/r1/__init__.py)
- [verl/scripts/__init__.py](verl/scripts/__init__.py)
- [verl/verl/experimental/dataset/__init__.py](verl/verl/experimental/dataset/__init__.py)
- [verl/verl/model_merger/__init__.py](verl/verl/model_merger/__init__.py)
- [verl/verl/models/__init__.py](verl/verl/models/__init__.py)
- [verl/verl/models/transformers/__init__.py](verl/verl/models/transformers/__init__.py)
- [verl/verl/trainer/__init__.py](verl/verl/trainer/__init__.py)
- [verl/verl/trainer/config/_generated_ppo_megatron_trainer.yaml](verl/verl/trainer/config/_generated_ppo_megatron_trainer.yaml)
- [verl/verl/trainer/config/_generated_ppo_trainer.yaml](verl/verl/trainer/config/_generated_ppo_trainer.yaml)
- [verl/verl/trainer/config/critic/megatron_critic.yaml](verl/verl/trainer/config/critic/megatron_critic.yaml)
- [verl/verl/trainer/ppo/__init__.py](verl/verl/trainer/ppo/__init__.py)
- [verl/verl/workers/__init__.py](verl/verl/workers/__init__.py)

</details>



This document introduces the SAGE repository and the **verl** (Versatile Efficient Reinforcement Learning) framework. It provides an overview of the system's purpose, architecture, and capabilities to help new users understand how the components fit together and begin running RLHF training experiments.

For detailed information about specific subsystems, see:
- Core training concepts: [Core Concepts](#2)
- Algorithm implementations: [Training Algorithms](#3)
- Model support and parallelism: [Model Support](#4)
- Advanced optimizations: [Advanced Topics](#6)

## What is SAGE?

SAGE is a comprehensive framework for **Reinforcement Learning from Human Feedback (RLHF)** training of large language models (LLMs) and vision-language models (VLMs). Built on the verl framework, it provides production-ready implementations of multiple policy optimization algorithms with extensive support for distributed training at scale.

### Core Purpose

The framework enables:
- **Policy optimization** using algorithms like PPO, DAPO, GSPO, SPPO, and PRIME
- **Distributed training** across multiple GPUs/nodes using PyTorch FSDP or Megatron-LM
- **Efficient inference** during rollout generation via vLLM and SGLang integration
- **Flexible hardware support** including NVIDIA GPUs and Ascend NPUs

Sources: [verl/verl/trainer/config/_generated_ppo_trainer.yaml:1-533]()

## Key Capabilities

| Capability | Description | Implementation |
|------------|-------------|----------------|
| **Algorithms** | PPO variants including DAPO, GSPO, SPPO, PRIME | `RayPPOTrainer`, `RayDAPOTrainer`, `RaySPPOTrainer` |
| **Distributed Training** | FSDP or Megatron-LM parallelism strategies | `FSDPEngine`, `MegatronEngine` |
| **Efficient Inference** | High-throughput generation during rollout | vLLM, SGLang backends |
| **Model Support** | LLaMA, Qwen2/3, Molmo2, with MoE variants | `verl.models` module |
| **Hardware** | GPU (CUDA) and NPU (Ascend) support | Fused kernels, NPU patches |
| **Configuration** | Hydra-based YAML configuration system | `verl.trainer.config` |

Sources: [verl/verl/trainer/config/_generated_ppo_trainer.yaml:6-533](), [verl/verl/trainer/config/_generated_ppo_megatron_trainer.yaml:6-549]()

## System Architecture

### High-Level Component Overview

```mermaid
graph TB
    User["User / Researcher"]
    
    subgraph "Entry Points"
        MainPPO["verl.trainer.main_ppo<br/>Main training entry point"]
        Config["Hydra Configuration<br/>ppo_trainer.yaml<br/>ppo_megatron_trainer.yaml"]
    end
    
    subgraph "Orchestration Layer"
        Trainer["Ray Trainers<br/>RayPPOTrainer<br/>RayDAPOTrainer<br/>RaySPPOTrainer"]
        Ray["Ray Cluster<br/>Distributed execution"]
    end
    
    subgraph "Worker Layer"
        ActorWorker["ActorRolloutRefWorker<br/>actor_rollout_ref section"]
        CriticWorker["Critic Workers<br/>critic section"]
        RMWorker["Reward Model Workers<br/>reward_model section"]
    end
    
    subgraph "Execution Engines"
        FSDP["FSDPEngine<br/>PyTorch FSDP backend"]
        Megatron["MegatronEngine<br/>Megatron-LM backend"]
        vLLM["vLLM/SGLang<br/>Rollout inference"]
    end
    
    subgraph "Configuration Sections"
        DataCfg["data:<br/>train_files, val_files<br/>max_prompt_length"]
        AlgoCfg["algorithm:<br/>gamma, lam<br/>adv_estimator"]
        TrainerCfg["trainer:<br/>nnodes, n_gpus_per_node<br/>total_epochs"]
    end
    
    User --> Config
    Config --> MainPPO
    MainPPO --> Trainer
    Trainer --> Ray
    Ray --> ActorWorker
    Ray --> CriticWorker
    Ray --> RMWorker
    
    ActorWorker --> FSDP
    ActorWorker --> Megatron
    ActorWorker --> vLLM
    CriticWorker --> FSDP
    CriticWorker --> Megatron
    RMWorker --> FSDP
    
    Config --> DataCfg
    Config --> AlgoCfg
    Config --> TrainerCfg
```

Sources: [verl/verl/trainer/config/_generated_ppo_trainer.yaml:6-533](), [verl/verl/trainer/config/_generated_ppo_megatron_trainer.yaml:6-549]()

### Configuration Structure to Code Mapping

The framework uses a hierarchical YAML configuration that maps directly to Python dataclasses. This diagram shows how configuration sections instantiate specific worker and engine components:

```mermaid
graph LR
    subgraph "YAML Configuration Hierarchy"
        Root["ppo_trainer.yaml"]
        ActorRolloutRef["actor_rollout_ref:<br/>model, actor, ref, rollout"]
        Critic["critic:<br/>model, optim, strategy"]
        RM["reward_model:<br/>enable, model, strategy"]
        Algo["algorithm:<br/>adv_estimator, kl_ctrl"]
        Data["data:<br/>train_files, tokenizer"]
    end
    
    subgraph "Python Dataclass Configs"
        ActorConfig["FSDPActorConfig<br/>McoreActorConfig<br/>_target_ field"]
        RefConfig["Reference Config<br/>strategy, fsdp_config"]
        RolloutConfig["RolloutConfig<br/>_target_: verl.workers.config"]
        CriticConfig["FSDPCriticConfig<br/>McoreCriticConfig"]
        AlgoConfig["AlgoConfig<br/>_target_: verl.trainer.config"]
    end
    
    subgraph "Runtime Components"
        ActorWorker["ActorRolloutRefWorker<br/>Instantiated via Ray"]
        CriticWorkers["Critic Worker Pool<br/>Value function training"]
        RewardWorkers["Reward Model Pool<br/>Optional scoring"]
        Engines["FSDPEngine<br/>MegatronEngine"]
    end
    
    Root --> ActorRolloutRef
    Root --> Critic
    Root --> RM
    Root --> Algo
    Root --> Data
    
    ActorRolloutRef --> ActorConfig
    ActorRolloutRef --> RefConfig
    ActorRolloutRef --> RolloutConfig
    Critic --> CriticConfig
    Algo --> AlgoConfig
    
    ActorConfig --> ActorWorker
    RefConfig --> ActorWorker
    RolloutConfig --> ActorWorker
    CriticConfig --> CriticWorkers
    
    ActorWorker --> Engines
    CriticWorkers --> Engines
    RewardWorkers --> Engines
```

Sources: [verl/verl/trainer/config/_generated_ppo_trainer.yaml:6-270](), [rl_train/trainer/config/critic/megatron_critic.yaml:1-44]()

### Training Strategy Selection

The framework supports two primary distributed training strategies, selected via the `strategy` configuration field:

```mermaid
graph TB
    Start["Configuration"]
    
    subgraph "FSDP Strategy"
        FSDPConfig["actor_rollout_ref.actor.strategy: fsdp<br/>_target_: FSDPActorConfig"]
        FSDPEngine["FSDPEngine<br/>fsdp_config section"]
        FSDPFeatures["- PyTorch native FSDP<br/>- Ulysses sequence parallel<br/>- Parameter/optimizer offload<br/>- HuggingFace model support"]
        FSDPWorker["ActorRolloutRefWorker<br/>FSDP mode"]
    end
    
    subgraph "Megatron Strategy"
        MegatronConfig["actor_rollout_ref.actor.strategy: megatron<br/>_target_: McoreActorConfig"]
        MegatronEngine["MegatronEngine<br/>megatron section"]
        MegatronFeatures["- Tensor parallelism TP<br/>- Pipeline parallelism PP<br/>- Expert parallelism EP<br/>- Context parallelism CP"]
        MegatronWorker["ActorRolloutRefWorker<br/>Megatron mode"]
    end
    
    Start --> FSDPConfig
    Start --> MegatronConfig
    
    FSDPConfig --> FSDPEngine
    FSDPEngine --> FSDPFeatures
    FSDPEngine --> FSDPWorker
    
    MegatronConfig --> MegatronEngine
    MegatronEngine --> MegatronFeatures
    MegatronEngine --> MegatronWorker
```

**FSDP** is recommended for:
- Models from HuggingFace Hub (7B-70B range)
- Rapid prototyping and experimentation
- Long context training (with Ulysses SP)

**Megatron** is recommended for:
- Maximum scale (100B+ parameters)
- MoE models requiring expert parallelism
- Pipeline parallelism across multiple nodes

Sources: [verl/verl/trainer/config/_generated_ppo_trainer.yaml:23-40](), [verl/verl/trainer/config/_generated_ppo_megatron_trainer.yaml:29-56]()

## Configuration Overview

### Main Configuration Sections

The training configuration is organized into seven major sections:

| Section | Purpose | Key Parameters |
|---------|---------|----------------|
| `actor_rollout_ref` | Actor model, rollout, reference policy | `model.path`, `rollout.name`, `actor.strategy` |
| `data` | Training/validation data sources | `train_files`, `val_files`, `max_prompt_length` |
| `critic` | Value function configuration | `enable`, `strategy`, `ppo_mini_batch_size` |
| `reward_model` | External reward model (optional) | `enable`, `model.path`, `strategy` |
| `algorithm` | RL algorithm parameters | `adv_estimator`, `gamma`, `lam`, `kl_ctrl` |
| `trainer` | Training orchestration | `nnodes`, `n_gpus_per_node`, `total_epochs` |
| `global_profiler` | Performance profiling | `tool`, `steps`, `save_path` |

### Example: FSDP Configuration Structure

```yaml
actor_rollout_ref:
  model:
    path: ~/models/qwen2-7b-instruct    # Model path
    
  actor:
    strategy: fsdp                       # Use FSDP
    ppo_mini_batch_size: 256
    fsdp_config:
      ulysses_sequence_parallel_size: 4  # Sequence parallelism
      param_offload: false
      
  rollout:
    name: vllm                           # Use vLLM for inference
    tensor_model_parallel_size: 2
    
data:
  train_files: ~/data/train.parquet
  max_prompt_length: 512
  max_response_length: 512
  
trainer:
  nnodes: 1
  n_gpus_per_node: 8
  total_epochs: 30
```

Sources: [verl/verl/trainer/config/_generated_ppo_trainer.yaml:6-270]()

### Example: Megatron Configuration Structure

```yaml
actor_rollout_ref:
  model:
    path: ~/models/qwen2-30b-instruct
    
  actor:
    strategy: megatron                   # Use Megatron-LM
    megatron:
      tensor_model_parallel_size: 4      # 4-way TP
      pipeline_model_parallel_size: 2    # 2-way PP
      sequence_parallel: true
      use_distributed_optimizer: true
      
  rollout:
    name: vllm
    tensor_model_parallel_size: 4
    
trainer:
  nnodes: 2
  n_gpus_per_node: 8
```

Sources: [verl/verl/trainer/config/_generated_ppo_megatron_trainer.yaml:29-261]()

## Quick Start

### Basic Training Flow

```mermaid
flowchart LR
    Step1["1. Prepare<br/>Configuration"]
    Step2["2. Launch<br/>Ray Cluster"]
    Step3["3. Start<br/>Training"]
    Step4["4. Monitor<br/>Progress"]
    Step5["5. Merge<br/>Checkpoints"]
    
    Step1 --> Step2
    Step2 --> Step3
    Step3 --> Step4
    Step4 --> Step5
    
    subgraph "Step 1 Details"
        Config["Create/modify YAML<br/>Select algorithm<br/>Set model paths<br/>Configure parallelism"]
    end
    
    subgraph "Step 3 Details"
        Launch["python -m verl.trainer.main_ppo<br/>--config-name=my_config.yaml"]
    end
    
    subgraph "Step 4 Details"
        Monitor["WandB dashboard<br/>Console logs<br/>Checkpoint directory"]
    end
```

### Typical Execution Command

Training is launched via the `main_ppo` entry point with Hydra configuration:

```bash
# FSDP-based training
python -m verl.trainer.main_ppo \
  --config-name=ppo_trainer \
  actor_rollout_ref.model.path=/path/to/model \
  data.train_files=/path/to/train.parquet \
  trainer.nnodes=1 \
  trainer.n_gpus_per_node=8

# Megatron-based training
python -m verl.trainer.main_ppo \
  --config-name=ppo_megatron_trainer \
  actor_rollout_ref.model.path=/path/to/model \
  data.train_files=/path/to/train.parquet \
  actor_rollout_ref.actor.megatron.tensor_model_parallel_size=4
```

### Configuration Override Syntax

Hydra enables command-line configuration overrides:

```bash
# Override individual parameters
python -m verl.trainer.main_ppo \
  actor_rollout_ref.actor.ppo_mini_batch_size=512 \
  algorithm.adv_estimator=gae \
  trainer.total_epochs=50

# Switch to different algorithm
python -m verl.trainer.main_ppo \
  --config-name=dapo_trainer \
  actor_rollout_ref.rollout.filter_groups.enable=true
```

Sources: [verl/verl/trainer/config/_generated_ppo_trainer.yaml:472-501]()

## Training Pipeline Overview

The core training loop orchestrates three phases: generation, evaluation, and training.

```mermaid
graph TB
    subgraph "Phase 1: Generation"
        Prompts["Data Loader<br/>Parquet files"]
        Rollout["Rollout Workers<br/>vLLM/SGLang backend"]
        Responses["Generated<br/>Responses"]
        Prompts --> Rollout --> Responses
    end
    
    subgraph "Phase 2: Evaluation"
        RefModel["Reference Model<br/>Compute log probs<br/>KL divergence"]
        RewardFn["Reward Function<br/>Custom or RM-based<br/>compute_score"]
        Advantages["Advantage<br/>Estimation<br/>GAE/GRPO/RLOO"]
        
        Responses --> RefModel
        Responses --> RewardFn
        RefModel --> Advantages
        RewardFn --> Advantages
    end
    
    subgraph "Phase 3: Training"
        ActorUpdate["Actor Update<br/>PPO loss<br/>Policy gradient"]
        CriticUpdate["Critic Update<br/>Value loss<br/>Optional"]
        
        Advantages --> ActorUpdate
        Advantages --> CriticUpdate
    end
    
    subgraph "Orchestration"
        Trainer["RayPPOTrainer<br/>or variant<br/>Coordinates phases"]
    end
    
    Trainer -.manages.-> Rollout
    Trainer -.manages.-> RefModel
    Trainer -.manages.-> ActorUpdate
    Trainer -.manages.-> CriticUpdate
    
    CriticUpdate --> Prompts
```

**Key Components:**
- **Data Loader**: Reads prompts from parquet files ([verl/verl/trainer/config/_generated_ppo_trainer.yaml:270-303]())
- **Rollout Workers**: Generate responses using vLLM or SGLang ([verl/verl/trainer/config/_generated_ppo_trainer.yaml:162-246]())
- **Reference Model**: Computes KL penalty ([verl/verl/trainer/config/_generated_ppo_trainer.yaml:108-161]())
- **Reward Function**: Custom Python function or reward model ([verl/verl/trainer/config/_generated_ppo_trainer.yaml:445-447]())
- **Advantage Estimator**: GAE, GRPO, or RLOO ([verl/verl/trainer/config/_generated_ppo_trainer.yaml:448-471]())
- **Actor Update**: Policy optimization via PPO ([verl/verl/trainer/config/_generated_ppo_trainer.yaml:6-107]())
- **Critic Update**: Optional value function training ([verl/verl/trainer/config/_generated_ppo_trainer.yaml:304-402]())

Sources: [verl/verl/trainer/config/_generated_ppo_trainer.yaml:1-533]()

## Supported Models

The framework provides first-class support for multiple model architectures:

| Model Family | Variants | Strategy Support | Features |
|--------------|----------|------------------|----------|
| **LLaMA** | LLaMA 2, LLaMA 3 | FSDP, Megatron | Standard LLM training |
| **Qwen** | Qwen2, Qwen2.5, Qwen3 | FSDP, Megatron | MoE support (Qwen3-MoE) |
| **Molmo2** | Molmo2-7B, Molmo2-72B | FSDP | Vision-language multimodal |

Models are specified via the `actor_rollout_ref.model.path` configuration field and can be loaded from:
- Local filesystem paths
- HuggingFace Hub identifiers
- Custom model implementations via `external_lib` parameter

Sources: [verl/verl/trainer/config/_generated_ppo_trainer.yaml:247-268]()

## Resource Allocation

### Ray Worker Pool Configuration

The framework uses Ray to manage distributed worker pools:

```mermaid
graph TB
    subgraph "Controller Node"
        Trainer["RayPPOTrainer<br/>Main controller process"]
    end
    
    subgraph "Actor/Rollout/Ref Pool"
        ARR1["Worker 1<br/>ActorRolloutRefWorker"]
        ARR2["Worker 2<br/>ActorRolloutRefWorker"]
        ARRn["Worker N<br/>ActorRolloutRefWorker"]
    end
    
    subgraph "Critic Pool Optional"
        C1["Critic Worker 1"]
        C2["Critic Worker 2"]
    end
    
    subgraph "Reward Model Pool Optional"
        RM1["RM Worker 1<br/>reward_model.enable=true"]
        RM2["RM Worker 2"]
    end
    
    Trainer --> ARR1
    Trainer --> ARR2
    Trainer --> ARRn
    Trainer --> C1
    Trainer --> C2
    Trainer --> RM1
    Trainer --> RM2
```

**Resource Pool Sizing:**
- **Actor/Rollout/Ref**: Determined by `trainer.nnodes` × `trainer.n_gpus_per_node`
- **Critic**: Enabled via `critic.enable`, shares or uses separate GPUs
- **Reward Model**: Enabled via `reward_model.enable`, configured with `reward_model.nnodes` and `reward_model.n_gpus_per_node`

Sources: [verl/verl/trainer/config/_generated_ppo_trainer.yaml:484-485](), [verl/verl/trainer/config/_generated_ppo_trainer.yaml:403-444]()

## Next Steps

After understanding the basic architecture and configuration structure, explore these topics:

1. **[Core Concepts](#2)**: Learn about the training pipeline, configuration system, and distributed architecture in detail
2. **[Training Algorithms](#3)**: Choose the right algorithm (DAPO, GSPO, SPPO, PRIME) for your task
3. **[Model Support](#4)**: Understand model-specific configurations and parallelism strategies
4. **[System Components](#5)**: Deep dive into trainers, workers, engines, and checkpoint management
5. **[Advanced Topics](#6)**: Explore hardware optimizations, long context training, and inference integration

### Common Configuration Patterns

| Use Case | Recommended Config | Key Settings |
|----------|-------------------|--------------|
| **Quick experimentation** | FSDP, 7B model | `strategy: fsdp`, `nnodes: 1`, `n_gpus_per_node: 8` |
| **Math reasoning** | DAPO/GSPO | Use `dapo_trainer` or `gspo_trainer` config |
| **Large scale (30B+)** | Megatron | `strategy: megatron`, increase TP/PP sizes |
| **Long context (8K+)** | FSDP with Ulysses | `ulysses_sequence_parallel_size: 4-8` |
| **MoE models** | Megatron with EP | `expert_model_parallel_size: 8` |

### Important Configuration Files

- **FSDP Training**: [verl/trainer/config/ppo_trainer.yaml]() → [verl/verl/trainer/config/_generated_ppo_trainer.yaml]()
- **Megatron Training**: [verl/trainer/config/ppo_megatron_trainer.yaml]() → [verl/verl/trainer/config/_generated_ppo_megatron_trainer.yaml]()
- **FSDP Critic**: [verl/trainer/config/critic/fsdp_critic.yaml]()
- **Megatron Critic**: [verl/trainer/config/critic/megatron_critic.yaml]() → [verl/verl/trainer/config/critic/megatron_critic.yaml:1-44]()

Sources: [verl/verl/trainer/config/_generated_ppo_trainer.yaml:1-533](), [verl/verl/trainer/config/_generated_ppo_megatron_trainer.yaml:1-549](), [verl/verl/trainer/config/critic/megatron_critic.yaml:1-44]()

---

