<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/lerobot · page 3 Training and Evaluation · fetched 2026-10-26 -->

# Training and Evaluation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/lerobot/common/train_utils.py](src/lerobot/common/train_utils.py)
- [src/lerobot/configs/train.py](src/lerobot/configs/train.py)
- [src/lerobot/policies/factory.py](src/lerobot/policies/factory.py)
- [src/lerobot/rewards/factory.py](src/lerobot/rewards/factory.py)
- [src/lerobot/scripts/lerobot_train.py](src/lerobot/scripts/lerobot_train.py)
- [tests/common/test_publish.py](tests/common/test_publish.py)
- [tests/configs/test_resume_from_hub.py](tests/configs/test_resume_from_hub.py)
- [tests/policies/test_factory_peft_revision.py](tests/policies/test_factory_peft_revision.py)
- [tests/policies/test_language_processor_factory.py](tests/policies/test_language_processor_factory.py)
- [tests/rewards/test_reward_model_base.py](tests/rewards/test_reward_model_base.py)
- [tests/utils/test_train_utils.py](tests/utils/test_train_utils.py)

</details>



This page introduces LeRobot's training and evaluation pipeline, tracking the transformation of configurations and raw datasets into deployed, evaluated models through `lerobot-train` [src/lerobot/scripts/lerobot_train.py:16-29]() and `lerobot-eval` [src/lerobot/scripts/lerobot_eval.py:115]().

As a parent page, this section provides a high-level overview of the pipeline components, configuration systems, optimization strategies, multi-gpu tooling, and evaluation protocols. Detailed mechanics are documented in the dedicated child pages linked below:

- For orchestration of dataset loading, training loops, and checkpointing, see [Training Pipeline](#3.1).
- For `TrainPipelineConfig` and draccus parsing, see [Training Configuration](#3.2).
- For optimizers, learning rate schedulers, and warmup presets, see [Optimizers and Schedulers](#3.3).
- For Accelerate integration, DDP, FSDP, and HSDP parallelism, see [Multi-GPU and Distributed Training](#3.4).
- For rollout execution, metrics collection, and parallel evaluation, see [Evaluation Pipeline](#3.5).
- For RL policies, actor-learner architectures, and Gym environments, see [Reinforcement Learning](#3.6).
- For reward models and RA-BC weighting mechanisms, see [Reward Modeling](#3.7).

---

## System Overview

Training and evaluation share a unified structural pattern: a configuration dataclass (`TrainPipelineConfig` [src/lerobot/configs/train.py:110-160] or `EvalConfig` [src/lerobot/configs/default.py:140-160]) acts as the single source of truth, factory modules instantiate datasets, policies, and environments, and orchestration loops manage forward-backward execution or simulation rollouts.

**Training and Evaluation Pipeline Architecture**

```mermaid
flowchart TD
    CLI_train[""lerobot-train"\nsrc/lerobot/scripts/lerobot_train.py"]
    CLI_eval[""lerobot-eval"\nsrc/lerobot/scripts/lerobot_eval.py"]

    subgraph Config["Configuration"]
        TC["TrainPipelineConfig\nsrc/lerobot/configs/train.py"]
        EC["EvalConfig\nsrc/lerobot/configs/default.py"]
    end

    subgraph Factories["Factory Modules"]
        MDS["make_train_eval_datasets()\nsrc/lerobot/datasets/factory.py"]
        MP["make_policy()\nsrc/lerobot/policies/factory.py"]
        ME["make_env()\nsrc/lerobot/envs/factory.py"]
        MOS["make_optimizer_and_scheduler()\nsrc/lerobot/optim/factory.py"]
        MRM["make_reward_model()\nsrc/lerobot/rewards/factory.py"]
    end

    subgraph TrainingLoop["Training Loop & Evaluation"]
        UPD["_train_step()\nsrc/lerobot/scripts/lerobot_train.py"]
        CKPT["save_checkpoint()\nsrc/lerobot/common/train_utils.py"]
        EPA["eval_policy_all()\nsrc/lerobot/scripts/lerobot_eval.py"]
        WANDB["WandBLogger\nsrc/lerobot/common/wandb_utils.py"]
    end

    CLI_train --> TC
    CLI_eval --> EC
    TC --> MDS
    TC --> MP
    TC --> ME
    TC --> MOS
    TC --> MRM
    EC --> MP
    EC --> ME

    MDS --> UPD
    MP --> UPD
    MOS --> UPD
    MRM --> UPD
    UPD --> CKPT
    UPD --> EPA
    UPD --> WANDB
    EPA --> WANDB
```

Sources: [src/lerobot/scripts/lerobot_train.py:48-78](), [src/lerobot/configs/train.py:110-160](), [src/lerobot/configs/default.py:140-160](), [src/lerobot/rewards/factory.py:108-148]()

---

## CLI Entrypoints

The framework exposes command-line utilities powered by `draccus` [src/lerobot/configs/train.py:25]() for parsing nested configuration objects directly from shell arguments.

| Command | Script Path | Configuration Class | Core Function |
|---|---|---|---|
| `lerobot-train` | `src/lerobot/scripts/lerobot_train.py` | `TrainPipelineConfig` | `train()` [src/lerobot/scripts/lerobot_train.py:30]() |
| `lerobot-eval` | `src/lerobot/scripts/lerobot_eval.py` | `EvalConfig` | `eval_main()` [src/lerobot/scripts/lerobot_eval.py:115]() |

For distributed training, `lerobot-train` is launched via `torchrun` or `accelerate launch`, where parallel topologies are explicitly defined via configuration flags rather than external YAML engines [src/lerobot/scripts/lerobot_train.py:25-28]().

Sources: [src/lerobot/scripts/lerobot_train.py:16-29](), [src/lerobot/configs/train.py:25](), [src/lerobot/scripts/lerobot_train.py:25-28]()

---

## Core Sub-Topics & Child Pages

### 3.1 Training Pipeline
The training orchestration loop manages data streaming from `LeRobotDataset`, feeds micro-batches through policy processors, executes forward passes, computes losses, and triggers gradient updates via PyTorch `Optimizer` instances [src/lerobot/scripts/lerobot_train.py:49-50](). It handles periodic EMA weight updates [src/lerobot/scripts/lerobot_train.py:120-137](), checkpoint serialization [src/lerobot/common/train_utils.py:58](), and mid-run evaluation rollouts [src/lerobot/scripts/lerobot_train.py:115]().
- For deep-dive details, see [Training Pipeline](#3.1).

Sources: [src/lerobot/scripts/lerobot_train.py:49-50](), [src/lerobot/scripts/lerobot_train.py:120-137](), [src/lerobot/common/train_utils.py:58](), [src/lerobot/scripts/lerobot_train.py:115]()

### 3.2 Training Configuration
`TrainPipelineConfig` serves as the root container governing hyperparameters, dataset repositories, hardware paths, logging frequency, and resume behaviors [src/lerobot/configs/train.py:110-160](). It integrates draccus-based parsing to load and save complete experiment snapshots (`train_config.json`), ensuring reproducibility across distributed nodes [src/lerobot/configs/train.py:25-42](). The resume mechanism allows picking up training from a local checkpoint or a Hugging Face Hub repository [src/lerobot/common/train_utils.py:55-56]().
- For configuration hierarchy and resume semantics, see [Training Configuration](#3.2).

Sources: [src/lerobot/configs/train.py:110-160](), [src/lerobot/configs/train.py:25-42](), [src/lerobot/common/train_utils.py:55-56]()

### 3.3 Optimizers and Schedulers
Optimizer instantiation is handled via modular builders like `make_optimizer_and_scheduler` [src/lerobot/optim/factory.py:16](), supporting standard configurations such as `AdamConfig`, `AdamWConfig`, and specialized parameter groups (e.g., differential learning rates for Vision-Language-Action backbones via `XVLAAdamWConfig`). Warmup strategies and learning rate decay schedules coordinate with step-wise training iterations.
- For optimizer subclasses and presets, see [Optimizers and Schedulers](#3.3).

Sources: [src/lerobot/optim/factory.py:16]()

### 3.4 Multi-GPU and Distributed Training
LeRobot integrates with Hugging Face `Accelerate` to support Data Parallel (DDP), Fully Sharded Data Parallel (FSDP), and Hybrid Sharded Data Parallel (HSDP) configurations [src/lerobot/distributed/parallel_dims.py:10-12](). Parallelism parameters (`--parallelism.dp_shard`, `--accelerator.mixed_precision`) manage gradient accumulation, activation checkpointing, and distributed checkpoint (DCP) saving [src/lerobot/configs/train.py:45-71]().
- For sharding topologies and multi-node execution, see [Multi-GPU and Distributed Training](#3.4).

Sources: [src/lerobot/distributed/parallel_dims.py:10-12](), [src/lerobot/configs/train.py:45-71]()

### 3.5 Evaluation Pipeline
Evaluation functions (`eval_policy_all` [src/lerobot/scripts/lerobot_train.py:115]() and `eval_policy` [src/lerobot/scripts/lerobot_eval.py:115]()) execute rollouts across simulation environments (such as PushT or LIBERO) using `VectorEnv` wrappers. They aggregate reward sums, compute task success rates, render rollout videos, and log evaluation metrics alongside training statistics.
- For rollout execution and parallel evaluation metrics, see [Evaluation Pipeline](#3.5).

Sources: [src/lerobot/scripts/lerobot_train.py:115](), [src/lerobot/scripts/lerobot_eval.py:115]()

### 3.6 Reinforcement Learning
Reinforcement learning pipelines support actor-learner architectures and algorithm implementations including SAC, TDMPC, and QC-FQL. These pipelines couple policy execution with environment reward streams, experience replay buffers, and actor-learner process coordination.
- For RL algorithms and Gym manipulator environments, see [Reinforcement Learning](#3.6).

Sources: No direct citations from provided files for specific RL algorithms, but the general concept is covered.

### 3.7 Reward Modeling
Reward modeling components encapsulate models such as SARM [src/lerobot/rewards/sarm/configuration_sarm.py:16](), RewardClassifier [src/lerobot/rewards/classifier/configuration_classifier.py:16](), ROBOMETER [src/lerobot/rewards/robometer/configuration_robometer.py:16](), and TOPReward [src/lerobot/rewards/topreward/configuration_topreward.py:16](). They drive Reward-Aware Behavioral Cloning (RA-BC) weighting mechanisms by scoring demonstration quality or progress, enabling filtered or weighted imitation learning from heterogeneous datasets [src/lerobot/configs/train.py:73-106]().
- For reward model variants and weighting scripts, see [Reward Modeling](#3.7).

Sources: [src/lerobot/rewards/sarm/configuration_sarm.py:16](), [src/lerobot/rewards/classifier/configuration_classifier.py:16](), [src/lerobot/rewards/robometer/configuration_robometer.py:16](), [src/lerobot/rewards/topreward/configuration_topreward.py:16](), [src/lerobot/configs/train.py:73-106]()

---

