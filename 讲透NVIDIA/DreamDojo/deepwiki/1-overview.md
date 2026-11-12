<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/DreamDojo · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This document provides a high-level introduction to DreamDojo, its core capabilities, and system architecture. It covers the system's purpose as a generalist robot world model, its three-stage training pipeline, model variants, and key components.

## What is DreamDojo?

DreamDojo is a generalist robot world model that learns physical dynamics and visual semantics from large-scale human egocentric videos. The system enables interactive video generation conditioned on text descriptions and robot actions, allowing it to simulate diverse manipulation tasks across multiple robot embodiments.

The system achieves three key technical contributions:

| Contribution | Description | Implementation |
|--------------|-------------|----------------|
| **Large-Scale Dataset** | 44,000 hours of diverse human egocentric videos for world model pretraining | Largest dataset to date for robot world models |
| **Foundation Model** | First robot world model demonstrating strong generalization after post-training | 2B and 14B parameter variants with transformer architecture |
| **Distillation Pipeline** | Stable autoregressive generation at 10 FPS for over 1 minute | Achieved through distillation pipeline |

**Sources:** [README.md:14-20]()

## Key Capabilities

### Multi-Robot Support

DreamDojo employs a unified 384-dimensional action space that supports multiple robot embodiments simultaneously. This design enables a single model to generalize across diverse embodiments without requiring separate training for each robot platform.

- **GR-1 Robot**: Fourier arms (dims 0-29) and Manus gloves (dims 29-58)
- **Unitree G1**: Humanoid robot (dims 58-101)
- **Bimanual YAM**: 170+ manipulation tasks (dims 101-147)
- **AgiBot**: Commercial robot platform (dims 147-169)
- **MANO Hand**: Human hand model (dims 220-352)
- **Latent Actions**: Learned representations from `LatentActionModel` (dims 352-384)

### Model Variants

Two model scales are available:

| Model | Parameters | Use Case | Hidden Dim | Attention Heads | Transformer Blocks |
|-------|------------|----------|------------|-----------------|-------------------|
| **2B** | 2 billion | Standard training and inference | 2048 | 32 | 24 |
| **14B** | 14 billion | Maximum capability | 3840 | 60 | 40 |

Both variants share the same architecture (`Text2WorldModelRectifiedFlow`) but differ in network capacity.

### Generation Capabilities

- **Training Resolution**: 480×640 pixels
- **Frame Generation**: 13 frames (training), up to 49 frames (evaluation)
- **Real-Time Performance**: 10 FPS after distillation
- **Stability**: 1+ minute continuous generation
- **Conditioning**: Text captions + 384-dim robot actions + 32-dim latent actions

**Sources:** [README.md:14-26]()

## High-Level System Architecture

The following diagram illustrates the complete DreamDojo system, from data sources through training to deployment:

**System Data Flow and Component Map**
```mermaid
graph TB
    subgraph "External_Data_Sources"
        [HF_Data] --> ["Hugging Face Datasets"]
        [HF_Models] --> ["Hugging Face Models"]
        [HumanVideo] --> ["44k Hours Human Videos"]
    end
    
    subgraph "LAM_Subsystem" [Latent Action Model Subsystem]
        [LAM_Train] --> ["external/lam_project"]
        [LAM_Ckpt] --> ["32-dim latent actions"]
    end
    
    subgraph "Training_Pipeline" [Three-Stage Training Pipeline]
        [Stage1] --> ["Stage 1: Pretraining"]
        [Stage2] --> ["Stage 2: Post-Training"]
        [Stage3] --> ["Stage 3: Distillation"]
    end
    
    subgraph "Core_Model_Components" [Code Entity Space]
        [Model] --> ["Text2WorldModelRectifiedFlow"]
        [Network] --> ["MiniTrainDIT"]
        [VAE] --> ["BaseVAE Tokenizer"]
        [Cond] --> ["Text2WorldCondition"]
    end
    
    subgraph "Configuration_System"
        [BaseConf] --> ["_default_groot_config"]
        [YAMLConf] --> ["configs/*.yaml"]
        [ActionConf] --> ["ActionConditionedSetupArguments"]
    end
    
    subgraph "Data_Pipeline"
        [DataDef] --> ["action_conditioned/data.py"]
        [Multi] --> ["MultiVideoActionDataset"]
        [Loader] --> ["DistributedSampler"]
    end
    
    [HumanVideo] --> [Stage1]
    [HF_Data] --> [Stage2]
    [LAM_Ckpt] --> [Stage1]
    [LAM_Ckpt] --> [Stage2]
    
    [Stage1] --> [Stage2]
    [Stage2] --> [Stage3]
    
    [Model] --> [Network]
    [Model] --> [VAE]
    [Model] --> [Cond]
    
    [BaseConf] --> [YAMLConf]
    [YAMLConf] --> [ActionConf]
    
    [DataDef] --> [Multi]
    [Multi] --> [Loader]
    [Loader] --> [Stage1]
    [Loader] --> [Stage2]
```
**Sources:** [README.md:1-56](), [cosmos_predict2/text2world_model_rectified_flow.py:41-129](), [cosmos_predict2/minimal_v4_dit.py:270-437]()

## Three-Stage Training Pipeline

DreamDojo follows a sequential training approach optimized for generalization and efficiency:

### Stage 1: Pretraining
**Purpose**: Learn general physical dynamics and visual semantics from human demonstrations.
- **Dataset**: 44,000 hours of human egocentric videos.
- **Action Conditioning**: LAM-extracted 32-dim latent actions only (dims 352-384).
- **Scripts**: `launch.sh` with `dreamdojo_2b_480_640_pretrain`.

### Stage 2: Post-Training
**Purpose**: Adapt the pretrained model to specific robot embodiments and action spaces.
- **Dataset**: Robot-specific teleoperation data (GR-1, G1, AgiBot, YAM).
- **Action Space**: Full 384-dim unified action space.
- **Configuration**: Robot-specific YAML files (e.g., `2b_480_640_gr1.yaml`).

### Stage 3: Distillation
**Purpose**: Achieve real-time generation performance (10 FPS) while maintaining quality for 1+ minute rollouts.
- **Method**: Distill multi-step diffusion into fewer steps using DMD2.
- **Output**: Distilled checkpoints for interactive applications.

**Sources:** [README.md:14-35]()

## Repository Structure and Key Files

The following diagram maps the repository structure to its functional components:

**Repository Functional Mapping**
```mermaid
graph TB
    subgraph "Root"
        [README] --> ["README.md"]
        [Install] --> ["install.sh"]
    end
    
    subgraph "Docs_Dir" [docs/]
        [SETUP_DOC] --> ["SETUP.md"]
        [PRETRAIN_DOC] --> ["PRETRAIN.md"]
        [POSTTRAIN_DOC] --> ["POSTTRAIN.md"]
    end
    
    subgraph "Configs_Dir" [configs/]
        [YAML_CFG] --> ["*.yaml (Experiment Overrides)"]
    end
    
    subgraph "Action_Conditioned_Dir" [action_conditioned/]
        [AC_CFG] --> ["action_conditioned_config.py"]
        [AC_DATA] --> ["data.py"]
        [AC_ACT] --> ["action.py"]
    end
    
    subgraph "Cosmos_Predict2_Dir" [cosmos_predict2/]
        [FLOW_MODEL] --> ["text2world_model_rectified_flow.py"]
        [DIT_NET] --> ["minimal_v4_dit.py"]
    end
    
    subgraph "External_Dir" [external/]
        [LAM_CODE] --> ["lam_project/"]
    end
    
    [README] --> [SETUP_DOC]
    [PRETRAIN_DOC] --> [YAML_CFG]
    [POSTTRAIN_DOC] --> [YAML_CFG]
    
    [YAML_CFG] --> [AC_CFG]
    [AC_CFG] --> [AC_DATA]
    [AC_DATA] --> [FLOW_MODEL]
    
    [FLOW_MODEL] --> [DIT_NET]
```
**Sources:** [README.md:29-37]()

## Core Model Architecture

The `Text2WorldModelRectifiedFlow` class serves as the top-level orchestrator, managing the tokenizer, network, conditioner, and rectified flow algorithms.

- **`Text2WorldModelRectifiedFlow`**: Implements the rectified flow diffusion process, handling training and sampling loops. [cosmos_predict2/text2world_model_rectified_flow.py:41-129]()
- **`MiniTrainDIT`**: The core video transformer architecture utilizing 3D positional embeddings and various attention backends (e.g., `transformer_engine`, `torch-flex`). [cosmos_predict2/minimal_v4_dit.py:270-437]()
- **`BaseVAE`**: Handles spatial and temporal compression of video into latent space.
- **`Text2WorldCondition`**: Manages conditioning signals from text encoders and action MLPs.

**Sources:** [cosmos_predict2/text2world_model_rectified_flow.py:41-129](), [cosmos_predict2/minimal_v4_dit.py:270-437]()

## Available Checkpoints

DreamDojo provides pretrained and post-trained checkpoints on Hugging Face:

| Checkpoint Type | Model Size | Download Location | Description |
|----------------|------------|-------------------|-------------|
| **Pretrained 2B/14B** | 2B / 14B | `nvidia/DreamDojo` | Trained on 44k hours human video |
| **Post-trained GR-1** | 2B / 14B | `nvidia/DreamDojo` | Adapted for GR-1 robot |

**Sources:** [README.md:23-26]()

---

