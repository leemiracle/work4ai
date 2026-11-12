<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/PhoneCLI · page 5 OpenPhone Model: Data and Training · fetched 2026-11-09 -->

# OpenPhone Model: Data and Training

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README_CN.md](README_CN.md)
- [figures/phone_cli.png](figures/phone_cli.png)

</details>



This page provides a high-level overview of the OpenPhone-3B model, detailing its pipeline from data synthesis to Supervised Fine-Tuning (SFT) and Generative Reinforcement Learning from Human Feedback (GRPO) training, and finally, model serving. The OpenPhone model is a core component of the PhoneCLI framework, designed to enhance mobile agent capabilities by integrating both GUI and CLI modalities. The model is open and replaceable, serving as an engine for tasks that cannot be handled by the deterministic CLI path [README.md:55-55]().

The OpenPhone model is a 3B parameter on-device model [README.md:55-55](), specifically a Qwen2.5-VL-3B variant, trained to understand and interact with mobile interfaces. Its development focuses on efficiency and effectiveness, aiming to reduce reliance on expensive and slow cloud-based Vision-Language Models (VLMs) for common navigation tasks. The training methodology combines supervised learning with reinforcement learning to optimize its performance in mobile environments.

This page serves as a parent for more detailed discussions on each stage of the model pipeline. For in-depth information on data preparation, training specifics, and serving configurations, please refer to the linked child pages.

## OpenPhone Model Pipeline Overview

The OpenPhone model pipeline consists of three main stages: data preparation, model training, and model serving. This structured approach ensures that the model is robust, efficient, and capable of handling diverse mobile interaction scenarios.

### Training Data Preparation

The first stage involves synthesizing high-quality training data. This process is crucial for teaching the model to interpret mobile screens and generate appropriate actions. Data generation leverages techniques like Chain-of-Thought (CoT) and reflection to create rich, instructional examples. These examples are then converted into formats suitable for both supervised fine-tuning and reinforcement learning.

For details on the data synthesis process, including the use of `data_maker.py` for CoT+reflection generation, `sft_data_maker.py` for Alpaca conversion, and `rl/convert_to_hf_vl.py` for creating Hugging Face VL datasets for GRPO, see [Training Data Preparation (prepare_data)](#5.1).

Sources:
- [README.md:84-84]()

### SFT and GRPO Training

The prepared data is then used to train the OpenPhone model. The training regimen involves two primary phases: Supervised Fine-Tuning (SFT) and Generative Reinforcement Learning from Human Feedback (GRPO). SFT initializes the model with a strong foundation in mobile interaction, while GRPO further refines its behavior based on reward signals, optimizing for task success and efficiency. The model used is a Qwen2.5-VL-3B variant [README.md:55-55]().

For a comprehensive understanding of the SFT scripts, the R1-V GRPO setup, the reward design implemented in `grpo_agent.py`, GPU requirements, and dataset sampling constraints, refer to [SFT and GRPO Training (model_training)](#5.2).

Sources:
- [README.md:55-55]()
- [README.md:84-84]()

### Model Serving with vLLM

Once trained, the OpenPhone model is deployed for inference. This stage focuses on efficient and scalable serving, allowing the model to be integrated into the PhoneCLI agent. The serving infrastructure is designed to support both on-device and cloud-based model deployments, providing flexibility based on performance and privacy requirements.

To learn more about the `vllm_script/` launch configuration, how `api_base` is wired into agent configurations, and the selection process between on-device and cloud models, see [Model Serving with vLLM](#5.3).

Sources:
- [README.md:54-55]()

### OpenPhone Model Pipeline

The following diagram illustrates the overall pipeline for the OpenPhone model, from data generation to deployment.

```mermaid
graph TD
    subgraph "Data Preparation (prepare_data)"
        A[Raw Data] --> B{CoT+Reflection Generation};
        B --> C[data_maker.py];
        C --> D{Alpaca Conversion};
        D --> E[sft_data_maker.py];
        E --> F{HF VL Dataset Conversion};
        F --> G[rl/convert_to_hf_vl.py];
        G --> H[SFT Dataset];
        G --> I[GRPO Dataset];
    end

    subgraph "Model Training (model_training)"
        H --> J[SFT Training (LLaMA-Factory)];
        J --> K[Qwen2.5-VL-3B (SFT Model)];
        I --> L[GRPO Training (R1-V)];
        L --> M[grpo_agent.py (Reward Design)];
        K & M --> N[OpenPhone-3B (GRPO Model)];
    end

    subgraph "Model Serving (vllm_script)"
        N --> O[vLLM Deployment];
        O --> P[API Base Configuration];
        P --> Q[On-device/Cloud Model Selection];
        Q --> R[PhoneCLI Agent];
    end

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bbf,stroke:#333,stroke-width:2px
    style D fill:#bbf,stroke:#333,stroke-width:2px
    style E fill:#bbf,stroke:#333,stroke-width:2px
    style F fill:#bbf,stroke:#333,stroke-width:2px
    style G fill:#bbf,stroke:#333,stroke-width:2px
    style H fill:#f9f,stroke:#333,stroke-width:2px
    style I fill:#f9f,stroke:#333,stroke-width:2px
    style J fill:#bbf,stroke:#333,stroke-width:2px
    style K fill:#f9f,stroke:#333,stroke-width:2px
    style L fill:#bbf,stroke:#333,stroke-width:2px
    style M fill:#bbf,stroke:#333,stroke-width:2px
    style N fill:#f9f,stroke:#333,stroke-width:2px
    style O fill:#bbf,stroke:#333,stroke-width:2px
    style P fill:#bbf,stroke:#333,stroke-width:2px
    style Q fill:#bbf,stroke:#333,stroke-width:2px
    style R fill:#f9f,stroke:#333,stroke-width:2px
```
Sources:
- [README.md:55-55]()
- [README.md:84-84]()
- [figures/phone_cli.png:1-31]()

---

