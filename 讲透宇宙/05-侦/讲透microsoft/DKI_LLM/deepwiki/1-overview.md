<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/DKI_LLM · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document provides a comprehensive overview of the Microsoft DKI LLM Paper Code Collection repository, which hosts three distinct research systems for large language model enhancement and optimization. The repository contains production-ready implementations of reinforcement learning pipelines, instruction tuning systems, and reward learning frameworks developed by Microsoft's Data Knowledge Intelligence (DKI) group.

This overview covers the high-level architecture, system relationships, and research domains. For detailed implementation guides, see the individual system pages: [WarriorCoder System](#2), [RePrompt System](#3), and [SER System](#4). For development setup and contribution guidelines, see [Contributing Guidelines](#5).

## Repository Architecture

The repository is organized into three primary research systems, each with dedicated documentation and implementation directories:

### Repository Structure Diagram

```mermaid
graph TB
    subgraph "DKI_LLM Repository"
        ROOT["📁 Repository Root"]
        README["📄 README.md"]
        
        subgraph "Research Systems"
            WC_DIR["📁 WarriorCoder/"]
            RP_DIR["📁 RePrompt/"] 
            SER_DIR["📁 SER/"]
        end
        
        subgraph "Documentation Site"
            DOCS_DIR["📁 docs/"]
            INDEX_HTML["📄 docs/index.html"]
            SER_DOC["📄 docs/ser/ser_index.html"]
            RP_DOC["📄 docs/reprompt/reprompt_index.html"]
        end
        
        subgraph "Configuration Files"
            GITIGNORE["📄 .gitignore"]
            LICENSE["📄 LICENSE"]
            SECURITY["📄 SECURITY.md"]
            SUPPORT["📄 SUPPORT.md"]
        end
    end
    
    ROOT --> README
    ROOT --> WC_DIR
    ROOT --> RP_DIR
    ROOT --> SER_DIR
    ROOT --> DOCS_DIR
    ROOT --> GITIGNORE
    ROOT --> LICENSE
    ROOT --> SECURITY
    ROOT --> SUPPORT
    
    DOCS_DIR --> INDEX_HTML
    DOCS_DIR --> SER_DOC
    DOCS_DIR --> RP_DOC
    
    SER_DOC -.-> SER_DIR
    RP_DOC -.-> RP_DIR
```

Sources: [README.md:1-42]()

### System Integration Overview

```mermaid
graph TD
    subgraph "WarriorCoder Pipeline"
        VLLM_LAN["vllmlan.py"]
        FHW_DEDUP["fhw_deduplication.py"]
        QUALITY_SCORE["qualityscoring.py"]
        KCENTER["kcenter.py"]
        VLLM_ANS["vllmans.py"]
        BATTLE["battle.py"]
        ELO_CALC["cal_elorating.py"]
        RUN_SFT["run_sft_warrior.py"]
        CONFIG_SFT["config_sft_warrior.yaml"]
    end
    
    subgraph "RePrompt System"
        RP_TRAIN["training pipeline"]
        RP_REWARDS["multi-reward optimization"]
        RP_RL["reinforcement learning"]
    end
    
    subgraph "SER System"  
        SER_PPO["PPO training"]
        SER_RM["reward model evolution"]
        SER_POLICY["policy optimization"]
    end
    
    subgraph "Shared Infrastructure"
        ACCELERATE["🚀 accelerate"]
        DEEPSPEED["⚡ deepspeed"]
        WANDB["📊 wandb"]
        HF_MODELS["🤗 huggingface models"]
    end
    
    VLLM_LAN --> FHW_DEDUP
    FHW_DEDUP --> QUALITY_SCORE
    QUALITY_SCORE --> KCENTER
    KCENTER --> VLLM_ANS
    VLLM_ANS --> BATTLE
    BATTLE --> ELO_CALC
    ELO_CALC --> CONFIG_SFT
    CONFIG_SFT --> RUN_SFT
    
    RP_TRAIN --> RP_REWARDS
    RP_REWARDS --> RP_RL
    
    SER_PPO --> SER_RM
    SER_RM --> SER_POLICY
    
    RUN_SFT --> ACCELERATE
    RP_RL --> ACCELERATE
    SER_POLICY --> ACCELERATE
    
    RUN_SFT --> DEEPSPEED
    RP_RL --> DEEPSPEED
    SER_POLICY --> DEEPSPEED
    
    RUN_SFT --> WANDB
    RP_RL --> WANDB
    SER_POLICY --> WANDB
    
    RUN_SFT --> HF_MODELS
    RP_RL --> HF_MODELS
    SER_POLICY --> HF_MODELS
```

Sources: [README.md:12-21]()

## Research Systems Overview

The repository implements three complementary research directions in large language model enhancement:

### System Comparison Matrix

| System | Domain | Primary Method | Key Innovation | Training Framework |
|--------|---------|----------------|----------------|-------------------|
| **WarriorCoder** | Code Generation | Multi-stage Pipeline + Elo Rating | Challenging instruction synthesis | Supervised Fine-tuning |
| **RePrompt** | Text-to-Image | Reinforcement Learning | Reasoning-augmented prompting | Multi-reward RL |
| **SER** | Reward Learning | Self-evolution | Reduced human annotation dependency | PPO + Iterative RM |

### WarriorCoder System

WarriorCoder implements a comprehensive 7-stage pipeline for generating challenging coding instructions and training specialized coding language models. The system uses competitive evaluation through model battles and Elo rating systems to identify optimal training data.

**Core Components:**
- `vllmlan.py` - Instruction generation using vLLM
- `fhw_deduplication.py` - MinHash-based deduplication
- `qualityscoring.py` - LLM-based quality assessment
- `battle.py` - Pairwise model evaluation system
- `run_sft_warrior.py` - Supervised fine-tuning execution

### RePrompt System  

RePrompt focuses on improving text-to-image generation through reinforcement learning-based prompt optimization. The system integrates reasoning capabilities into prompt generation and uses multiple reward models for optimization.

**Core Features:**
- Reinforcement learning for prompt optimization
- Multi-reward system integration
- Support for multiple T2I backends (FLUX, SD3, PixArt)
- GPT-4V-based evaluation metrics

### SER System

SER (Self-Evolved Reward Learning) implements an iterative approach to reward model improvement that reduces dependency on human-annotated data for RLHF. The system uses self-evolution techniques to progressively improve reward models.

**Core Components:**
- PPO-based policy optimization
- Iterative reward model training
- Self-evolution mechanisms
- Reduced human annotation requirements

Sources: [README.md:14-21]()

## Technical Architecture

### Shared Technology Stack

All three systems leverage a common technology foundation:

```mermaid
graph LR
    subgraph "Core Technologies"
        PYTORCH["PyTorch"]
        TRANSFORMERS["🤗 transformers"]
        ACCELERATE["🚀 accelerate"] 
        DEEPSPEED["⚡ deepspeed"]
        VLLM["vLLM"]
    end
    
    subgraph "Evaluation & Monitoring"
        WANDB["📊 wandb"]
        GPT4V["GPT-4V API"]
        CUSTOM_METRICS["Custom metrics"]
    end
    
    subgraph "Data & Models"
        HF_DATASETS["🤗 datasets"]
        HF_MODELS["🤗 models"]
        CUSTOM_DATA["Custom datasets"]
    end
    
    PYTORCH --> TRANSFORMERS
    TRANSFORMERS --> ACCELERATE
    ACCELERATE --> DEEPSPEED
    PYTORCH --> VLLM
    
    WANDB --> CUSTOM_METRICS
    GPT4V --> CUSTOM_METRICS
    
    HF_DATASETS --> CUSTOM_DATA
    HF_MODELS --> CUSTOM_DATA
```

### Research Domain Relationships

```mermaid
graph TD
    subgraph "Problem Domains"
        CODE_GEN["Code Generation Enhancement"]
        T2I_PROMPT["Text-to-Image Prompting"]
        REWARD_LEARNING["Reward Model Learning"]
    end
    
    subgraph "Methodological Approaches"
        INSTRUCTION_TUNING["Instruction Tuning"]
        RL_OPTIMIZATION["RL Optimization"]
        COMPETITIVE_EVAL["Competitive Evaluation"]
        SELF_EVOLUTION["Self-Evolution"]
    end
    
    subgraph "Technical Implementations"
        ELO_RATING["Elo Rating Systems"]
        PPO_TRAINING["PPO Training"]
        MULTI_REWARD["Multi-Reward Systems"]
        PIPELINE_AUTOMATION["Pipeline Automation"]
    end
    
    CODE_GEN --> INSTRUCTION_TUNING
    CODE_GEN --> COMPETITIVE_EVAL
    
    T2I_PROMPT --> RL_OPTIMIZATION
    T2I_PROMPT --> MULTI_REWARD
    
    REWARD_LEARNING --> SELF_EVOLUTION
    REWARD_LEARNING --> PPO_TRAINING
    
    INSTRUCTION_TUNING --> ELO_RATING
    COMPETITIVE_EVAL --> ELO_RATING
    
    RL_OPTIMIZATION --> PPO_TRAINING
    RL_OPTIMIZATION --> MULTI_REWARD
    
    SELF_EVOLUTION --> PIPELINE_AUTOMATION
```

Sources: [README.md:6-21]()

## Getting Started

### System Selection Guide

Choose the appropriate system based on your research objectives:

- **WarriorCoder**: For improving code generation capabilities through challenging instruction synthesis and competitive evaluation
- **RePrompt**: For enhancing text-to-image generation through reinforcement learning-based prompt optimization  
- **SER**: For developing self-evolving reward models with reduced human annotation requirements

### Next Steps

1. **Environment Setup**: Each system has specific dependencies and setup requirements detailed in their respective sections
2. **System Deep-Dive**: Navigate to individual system pages for comprehensive implementation details:
   - [WarriorCoder System](#2) - Complete instruction generation and training pipeline
   - [RePrompt System](#3) - Text-to-image prompt optimization framework
   - [SER System](#4) - Self-evolved reward learning implementation
3. **Development**: See [Contributing Guidelines](#5) for development environment setup and contribution processes

### Repository Statistics

- **Primary Language**: Python
- **Framework Dependencies**: PyTorch, Hugging Face ecosystem, vLLM
- **Training Infrastructure**: Accelerate, DeepSpeed
- **Documentation**: GitHub Pages with comprehensive system guides
- **License**: MIT License

Sources: [README.md:1-42]()

---

