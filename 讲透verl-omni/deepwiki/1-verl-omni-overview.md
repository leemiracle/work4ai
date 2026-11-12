<!-- source: DeepWiki mcp.deepwiki.com · repo verl-project/verl-omni · page 1 VeRL-Omni Overview · fetched 2026-10-30 -->

# VeRL-Omni Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/gpu_smoke.yml](.github/workflows/gpu_smoke.yml)
- [.github/workflows/gpu_smoke_verl_latest.yml](.github/workflows/gpu_smoke_verl_latest.yml)
- [README.md](README.md)
- [docs/assets/WeChat.jpg](docs/assets/WeChat.jpg)
- [docs/assets/arch.png](docs/assets/arch.png)
- [docs/index.md](docs/index.md)
- [docs/start/install.md](docs/start/install.md)
- [pyproject.toml](pyproject.toml)
- [verl_omni/agent_loop/single_turn_agent_loop.py](verl_omni/agent_loop/single_turn_agent_loop.py)
- [verl_omni/pipelines/sd3_flow_grpo/common.py](verl_omni/pipelines/sd3_flow_grpo/common.py)
- [verl_omni/pipelines/sd3_flow_grpo/vllm_omni_rollout_adapter.py](verl_omni/pipelines/sd3_flow_grpo/vllm_omni_rollout_adapter.py)

</details>



`VeRL-Omni` is a general-purpose reinforcement learning (RL) framework specifically designed for post-training multimodal generative models. Built as an evolution of the multimodal efforts within the [`verl`](https://github.com/verl-project/verl) project, it provides a high-performance, stable, and modular infrastructure for training diffusion models and omni-modality systems [README.md:13-15]().

The framework addresses the unique I/O patterns and compute characteristics of multimodal RL, such as high-throughput generation requirements and complex reward modeling across different modalities including image, video, audio, and text [README.md:23-27]().

## System Purpose and Scope

VeRL-Omni targets RL post-training for three primary families of generative models [README.md:29-35](), [docs/index.md:7-13]():
1.  **Diffusion Generative Models**: Models for image, video, and audio (e.g., Qwen-Image, Wan2.2, SD3.5, LTX2.3) [README.md:89-128](), [README.md:144-157]().
2.  **Unified Multimodal Models**: Models that jointly handle understanding and generation (e.g., BAGEL, HunyuanImage-3.0) [README.md:137-142](), [README.md:159-160]().
3.  **Omni-modality Models**: Models processing and generating across text, image, audio, and video simultaneously (e.g., Qwen3-Omni) [README.md:22](), [README.md:35]().

The system is optimized for high training throughput, achieving approximately 25% higher end-to-end performance compared to standard reference implementations by leveraging `vLLM-Omni` for rollouts and asynchronous reward computation [README.md:39-43](), [docs/index.md:21]().

Sources: [README.md:13-43](), [docs/index.md:5-21](), [README.md:89-160]()

## High-Level Architecture

VeRL-Omni follows a distributed actor-rollout-reward topology managed by **Ray** [pyproject.toml:35](). The architecture decouples the generation of samples (rollout) from the optimization of the model (training), allowing for heterogeneous resource allocation and efficient scaling across multiple nodes [README.md:39-42]().

### System Components Diagram
The following diagram illustrates the relationship between the major subsystems and the core code entities that manage them.

**VeRL-Omni Distributed Topology**
```mermaid
graph TD
    subgraph "Orchestration_Layer"
        [Trainer] --> ["BaseRayDiffusionTrainer"]
        [Trainer] --> ["PolicyGradientRayTrainer"]
        [Trainer] --> ["DirectPreferenceRayTrainer"]
        style [Trainer] stroke-dasharray: 5 5
    end

    subgraph "Rollout_Space_vLLM-Omni"
        [RolloutWorker] --> ["vLLMOmniHttpServer"]
        [AgentLoop] --> ["DiffusionAgentLoopWorker"]
        [Manager] --> ["AgentLoopManager"]
    end

    subgraph "Training_Space_FSDP2_VeOmni"
        [TrainingEngine] --> ["DiffusersFSDPEngine"]
        [TrainingEngine] --> ["DPODiffusersFSDPEngine"]
        [Worker] --> ["TrainingWorker"]
    end

    subgraph "Reward_Space"
        [RewardMgr] --> ["VisualRewardManager"]
        [RewardMgr] --> ["MultiVisualRewardManager"]
    end

    ["PolicyGradientRayTrainer"] -->|"Schedule_Fit_Loop"| ["DiffusionAgentLoopWorker"]
    ["DiffusionAgentLoopWorker"] -->|"Request_Generation"| ["vLLMOmniHttpServer"]
    ["DiffusionAgentLoopWorker"] -->|"Request_Scores"| ["VisualRewardManager"]
    ["PolicyGradientRayTrainer"] -->|"Update_Weights"| ["TrainingWorker"]
    ["TrainingWorker"] -->|"Engine_Logic"| ["DiffusersFSDPEngine"]
    ["DiffusersFSDPEngine"] -->|"Sync_LoRA_Weights"| ["vLLMOmniHttpServer"]
```
Sources: [README.md:46-48](), [docs/index.md:15-21](), [pyproject.toml:35](), [verl_omni/agent_loop/single_turn_agent_loop.py:104-113]()

## Major Subsystems

### 1. Distributed Training Engines
VeRL-Omni supports multiple modular backends for model optimization. The default is **FSDP2** (Fully Sharded Data Parallel), which integrates with USP (Ulysses Sequence Parallelism) for distributed training [README.md:41](). The trainer abstracts the underlying engine, supporting both standard FSDP and the **VeOmni** backend [docs/start/install.md:91-93]().
*   **Key Classes**: `DiffusersFSDPEngine` (FSDP-based implementation) and `VeOmniDiffusionEngineConfig` (VeOmni alternative) [docs/start/install.md:93]().
*   For details, see [System Architecture and Key Concepts](#1.2).

### 2. Rollout and Generation
Generation is handled by `vLLM-Omni`, a specialized version of vLLM tailored for high-throughput multimodal generation [README.md:39](). The `vLLMOmniHttpServer` manages the rollout lifecycle, supporting both Autoregressive (AR) and Diffusion modes [README.md:22]().
*   **Key Classes**: `vLLMOmniHttpServer` and `DiffusionAgentLoopWorker` [verl_omni/agent_loop/single_turn_agent_loop.py:104-113]().
*   For details, see [System Architecture and Key Concepts](#1.2).

### 3. Reward Infrastructure
The framework features a flexible reward pipeline that supports rule-based, model-based (e.g., HPSv3, GenRM-OCR, ImageBind, CLAP), and multimodal rewards [README.md:40](). It includes an **Async Reward** mechanism and an **HTTP Scorer** to overlap reward computation with other phases [README.md:40](), [docs/index.md:21]().
*   **Key Classes**: `VisualRewardManager`, `MultiVisualRewardManager`.

### 4. Algorithm Implementations
VeRL-Omni implements several state-of-the-art RL algorithms adapted for diffusion and omni-modality models [README.md:79-170]():
*   **FlowGRPO**: Policy gradient for flow-matching models (e.g., Qwen-Image, SD3.5, LTX2.3) [README.md:92](), [README.md:126]().
*   **DiffusionNFT**: Optimizes the forward diffusion process using implicit branches [README.md:23]().
*   **GSPO**: Designed for omni-modal models like Qwen3-Omni [README.md:22]().
*   **DanceGRPO**: Specialized for video generation tasks like Wan2.2 [README.md:23]().
*   **DiffusionOPD**: On-policy distillation for diffusion models [docs/index.md:64]().

**Code Entity Mapping: Algorithm to Trainer**
```mermaid
graph LR
    subgraph "Algorithm_Category"
        ["FlowGRPO"]
        ["DanceGRPO"]
        ["MixGRPO"]
        ["DiffusionNFT"]
        ["Diffusion_DPO"]
        ["Flow-DPPO"]
        ["DiffusionOPD"]
    end

    subgraph "Trainer_Classes"
        ["PolicyGradientRayTrainer"]
        ["DirectPreferenceRayTrainer"]
    end

    ["FlowGRPO"] --> ["PolicyGradientRayTrainer"]
    ["DanceGRPO"] --> ["PolicyGradientRayTrainer"]
    ["MixGRPO"] --> ["PolicyGradientRayTrainer"]
    ["DiffusionNFT"] --> ["DirectPreferenceRayTrainer"]
    ["Diffusion_DPO"] --> ["DirectPreferenceRayTrainer"]
    ["Flow-DPPO"] --> ["PolicyGradientRayTrainer"]
    ["DiffusionOPD"] --> ["PolicyGradientRayTrainer"]
```
Sources: [README.md:79-170](), [docs/index.md:58-64]()

## Getting Started and Next Steps

To begin using VeRL-Omni, you should first set up your environment (CUDA or NPU) and then explore the system architecture in depth.

*   **[Getting Started: Installation and Environment Setup](#1.1)**: Detailed instructions on installation using `uv`, Docker configurations, and hardware-specific requirements for NVIDIA GPUs and Ascend NPUs [docs/start/install.md:1-53]().
*   **[System Architecture and Key Concepts](#1.2)**: A deep dive into the distributed actors, the role of Ray, and the training loop lifecycle.

Sources: [README.md:51-56](), [docs/index.md:25-34](), [docs/start/install.md:1-53]()

---

