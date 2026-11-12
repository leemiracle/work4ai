<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/MoCapAct · page 3 Core Components · fetched 2026-10-26 -->

# Core Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [mocapact/download_dataset.py](mocapact/download_dataset.py)

</details>



This document provides an overview of the main components of the MoCapAct system and their interactions. It serves as a central reference for understanding the system architecture and how different parts work together to train humanoid controllers using motion capture data.

For specific implementation details about individual components, see their dedicated pages:
- [Clip Experts](#3.1)
- [Dataset Generation and Management](#3.2)
- [Policy Distillation](#3.3)
- [Transfer Learning](#3.4)
- [Motion Completion](#3.5)

## System Architecture Overview

```mermaid
graph TD
    MoCap["Motion Capture Data\n(CMU MoCap)"] --> ClipExperts["Clip Snippet Experts"]
    ClipExperts --> Dataset["Expert Dataset\n(HDF5 Files)"]
    Dataset --> MultiClip["Multi-clip Policy"]
    Dataset --> GPT["GPT Policy"]
    MultiClip --> Transfer["RL Transfer Tasks"]
    GPT --> MotionCompletion["Motion Completion"]
    
    subgraph "Infrastructure"
        DMControl["dm_control\n(CMU Humanoid)"]
        SB3["Stable-Baselines3\n(PPO)"]
        PyTorch["PyTorch Lightning"]
    end
    
    DMControl --> ClipExperts
    DMControl --> Transfer
    DMControl --> MotionCompletion
    SB3 --> ClipExperts
    SB3 --> Transfer
    PyTorch --> MultiClip
    PyTorch --> GPT
```

Sources: [README.md:9-20]()

The MoCapAct system consists of five core components working together to train and utilize humanoid controllers based on motion capture data. The system pipeline begins with training expert policies for specific motion clip snippets, then collecting rollouts from these experts to create a dataset. This dataset is used to train either a multi-clip policy (for general motion tracking) or a GPT policy (for motion completion). The multi-clip policy can be further refined for downstream tasks through reinforcement learning.

## 1. Clip Snippet Experts

Clip snippet experts are specialized policies trained to track specific segments (snippets) of motion capture clips.

```mermaid
graph TD
    train["clip_expert.train.py"] --> PPO["Stable-Baselines3\nPPO Algorithm"]
    PPO --> VecEnv["Vectorized Environments\nDummyVecEnv/SubprocVecEnv"]
    VecEnv --> MocapEnv["MocapTrackingGymEnv\nTracking Environment"]
    
    MocapEnv --> ClipCollection["ClipCollection\nMoCap Reference"]
    MocapEnv --> CMUHumanoid["CMU Humanoid\ndm_control Model"]
    
    evaluate["clip_expert.evaluate.py"] --> LoadPolicy["load_policy\nLoad Expert Policy"]
    LoadPolicy --> MocapEnv
```

Sources: [README.md:163-202]()

Each clip snippet expert focuses on accurately reproducing a single segment of motion. These experts are the foundation of the MoCapAct system, as they generate the data used in subsequent components.

| Component | Description | Source File |
|-----------|-------------|-------------|
| Trainer | Trains clip snippet experts using PPO | `mocapact/clip_expert/train.py` |
| Evaluator | Evaluates expert performance | `mocapact/clip_expert/evaluate.py` |
| Environment | MoCap tracking Gym environment | `mocapact/envs/tracking.py` |
| Utilities | Helper functions for setup | `mocapact/clip_expert/utils.py` |
| Callbacks | Training callbacks | `mocapact/clip_expert/callbacks.py` |

Technical details:
- Uses Proximal Policy Optimization (PPO) from Stable-Baselines3
- Employs vectorized environments for parallel training
- Includes evaluation callbacks with early stopping
- CMU Humanoid model from dm_control serves as the physical agent
- Stores both policy parameters and observation normalizers

## 2. Expert Dataset Generation

The expert dataset consists of rollouts collected from trained clip snippet experts, providing the foundation for policy distillation.

```mermaid
graph TD
    Rollout["rollout_experts.py"] --> Experts["Trained Clip Experts"]
    Experts --> Episodes["Expert Episodes"]
    Episodes --> HDF5["HDF5 Dataset Files"]
    
    subgraph "Dataset Structure"
        ClipLevel["Clip Level\n(CMU_xxx_yy.hdf5)"]
        SnippetLevel["Snippet Level\n(CMU_xxx_yy-start-end)"]
        EpisodeLevel["Episode Level\n(0, 1, ..., R+S-1)"]
        TransitionData["Transition Data\n(obs, actions, rewards)"]
    end
    
    HDF5 --> ClipLevel
    ClipLevel --> SnippetLevel
    SnippetLevel --> EpisodeLevel
    EpisodeLevel --> TransitionData
    
    DatasetClass["ExpertDataset Class"] --> HDF5
    DatasetClass --> PyTorchDataset["PyTorch Dataset Interface"]
```

Sources: [README.md:205-224](), [README.md:81-144]()

The dataset maintains a hierarchical structure in HDF5 format, organizing data by clips, snippets, and episodes. This organization facilitates efficient storage and retrieval of expert demonstrations.

| Component | Description | Source File |
|-----------|-------------|-------------|
| Rollout Generator | Collects expert rollouts | `mocapact/distillation/rollout_experts.py` |
| Dataset Class | Manages dataset access | `mocapact/distillation/dataset.py` |
| D4RL Dataset | Interface for offline RL | `mocapact/offline_rl/d4rl_dataset.py` |

Dataset structure details:
- HDF5 files organized by clip, snippet, and episode
- Contains proprioceptive observations, actions, rewards, values, advantages
- Includes episodes starting from beginning of snippets and random points
- Stores statistics (means, variances) for observation and action normalization
- Accessible through `ExpertDataset` and `D4RLDataset` classes

## 3. Policy Distillation

Policy distillation trains a general multi-clip policy using the expert dataset, creating a model that can perform across various motion clips.

```mermaid
graph TD
    Train["train.py"] --> Dataset["ExpertDataset\nLoads Data"]
    Train --> PolicyModel["Policy Models"]
    Train --> WeightingScheme["Weighting Schemes"]
    
    subgraph "Policy Models"
        MLP["MlpPolicy"]
        HMLP["HierarchicalMlpPolicy"]
        NPMP["NpmpPolicy"]
        MCP["McpPolicy"]
        GPT["GPTPolicy"]
    end
    
    PolicyModel --> MLP
    PolicyModel --> HMLP
    PolicyModel --> NPMP
    PolicyModel --> MCP
    PolicyModel --> GPT
    
    subgraph "Weighting Schemes"
        AWR["Advantage Weighting (AWR)"]
        RWR["Return-based Weighting (RWR)"]
        CWR["Clip-based Weighting (CWR)"]
        BC["Behavior Cloning (BC)"]
    end
    
    WeightingScheme --> AWR
    WeightingScheme --> RWR
    WeightingScheme --> CWR
    WeightingScheme --> BC
    
    PyTorchLightning["PyTorch Lightning\nTrainer"] --> Train
    EvalCallback["EvaluationCallback"] --> PyTorchLightning
```

Sources: [README.md:227-290]()

Policy distillation is the process of transferring knowledge from multiple specialized experts into a single, versatile policy. MoCapAct offers several policy architectures and weighting schemes to optimize this process.

| Model | Description | Use Case |
|-------|-------------|----------|
| MlpPolicy | Basic feedforward network | Simple tracking |
| HierarchicalMlpPolicy | Encoder-decoder architecture | Better generalization |
| NpmpPolicy | Neural Probabilistic Motor Primitives | Complex motion tracking |
| McpPolicy | Multiplicative Compositional Policy | Compositional control |
| GPTPolicy | Transformer-based model | Motion completion |

Key features:
- PyTorch Lightning framework for efficient training
- Multiple policy architectures with different capabilities
- Various weighting schemes (AWR, RWR, CWR, BC) for training optimization
- Regular evaluation during training with multiple metrics
- Checkpoint saving and training resumption

## 4. Transfer Learning

The multi-clip policy serves as a foundation for reinforcement learning on downstream tasks, such as goal-directed movement or velocity control.

```mermaid
graph TD
    Transfer["transfer.train.py"] --> PretrainedPolicy["Pretrained Multi-clip Policy"]
    Transfer --> TaskEnv["Task Environment"]
    Transfer --> PPO["PPO Algorithm"]
    
    subgraph "Task Environments"
        GoToTarget["Go-To-Target Task"]
        VelocityControl["Velocity Control Task"]
    end
    
    TaskEnv --> GoToTarget
    TaskEnv --> VelocityControl
    
    subgraph "Low-level Policy Integration"
        LLPolicy["Optional Low-level Policy"]
        ActionEmbed["EmbedToActionVecWrapper"]
    end
    
    PretrainedPolicy --> LLPolicy
    LLPolicy --> ActionEmbed
    
    Evaluate["transfer.evaluate.py"] --> TestEnv["Test Environment"]
```

Sources: [README.md:293-310]()

Transfer learning enables the application of learned motion skills to practical tasks. MoCapAct supports two primary transfer tasks: go-to-target (navigation) and velocity control (speed management).

| Component | Description | Source File |
|-----------|-------------|-------------|
| Trainer | Trains policies for transfer tasks | `mocapact/transfer/train.py` |
| Evaluator | Evaluates transfer task performance | `mocapact/transfer/evaluate.py` |
| Task Configurations | Task definitions | `mocapact/transfer/config.py` |

Technical details:
- Uses Proximal Policy Optimization (PPO) for transfer learning
- Supports optional integration with a pre-trained low-level policy
- Implements action embedding for more effective control
- Includes regular evaluation during training with model saving
- Supports go-to-target and velocity control tasks

## 5. Motion Completion

Motion completion uses a GPT-based policy to complete partial motion sequences, enabling the generation of continued movements from an initial prompt.

```mermaid
graph TD
    MotionCompletion["motion_completion.py"] --> GPTPolicy["GPT Policy\nTransformer Model"]
    MotionCompletion --> PromptPolicy["Prompt Policy\nExpert or Distilled"]
    
    GPTPolicy --> PromptWrapper["PromptWrapper\nEnvironment Wrapper"]
    PromptPolicy --> PromptWrapper
    
    PromptWrapper --> CompletionEnv["MotionCompletionGymEnv"]
    
    subgraph "Completion Process"
        InitMotion["Initial Motion\nFrom Prompt Policy"]
        Completion["Completion\nFrom GPT Policy"]
        Evaluation["Evaluation\nCompare with Reference"]
    end
    
    PromptWrapper --> InitMotion
    PromptWrapper --> Completion
    CompletionEnv --> Evaluation
```

Sources: [README.md:313-340]()

Motion completion represents a more advanced application of the system, where a transformer-based model learns to predict and generate continuation motions based on initial movement patterns.

| Component | Description | Source File |
|-----------|-------------|-------------|
| Completion Runner | Executes motion completion | `mocapact/distillation/motion_completion.py` |
| GPT Policy | Transformer model for completion | `mocapact/distillation/model.py` |
| Completion Environment | Environment for completion | `mocapact/envs/motion_completion.py` |
| Prompt Wrapper | Handles transition from prompt to completion | `mocapact/envs/wrappers.py` |

Technical details:
- GPT-based transformer model for sequence completion
- Prompt-based approach using an initial expert policy
- PromptWrapper environment to handle the transition from prompt to completion
- Supports both numerical evaluation and visualization

## Integration and Data Flow

The complete system integrates these components through a data flow pipeline:

```mermaid
flowchart LR
    MoCap["Motion Capture\nData"] --> ClipExperts["Clip Snippet\nExperts"]
    ClipExperts --> ExpertDataset["Expert Dataset\n(HDF5)"]
    ExpertDataset --> MultiClip["Multi-clip Policy\nDistillation"]
    ExpertDataset --> GPT["GPT Policy\nTraining"]
    MultiClip --> Transfer["Transfer Learning\nTasks"]
    GPT --> Completion["Motion\nCompletion"]
```

Sources: [README.md:11-20]()

This flow represents the full life cycle from raw motion capture data to practical applications:

1. Motion capture data is used to train specialized expert policies
2. These experts generate a dataset of demonstrations
3. The dataset trains either general policies (multi-clip) or specialized ones (GPT)
4. The trained policies enable downstream applications like task-specific control or motion completion

## Infrastructure Dependencies

MoCapAct relies on several key external libraries that provide the foundation for its functionality:

| Dependency | Usage | Integration Point |
|------------|-------|-------------------|
| dm_control | Provides the CMU Humanoid model and physics simulation | `mocapact/envs/tracking.py` |
| Stable-Baselines3 | Reinforcement learning algorithms (PPO) | `mocapact/clip_expert/train.py`, `mocapact/transfer/train.py` |
| PyTorch Lightning | Training framework for distilled policies | `mocapact/distillation/train.py` |
| HDF5 | Storage format for expert rollouts | `mocapact/distillation/dataset.py` |

Sources: [README.md:21-25](), [README.md:27-41]()

These dependencies provide the infrastructure necessary for simulation, reinforcement learning, neural network training, and efficient data storage.

---

