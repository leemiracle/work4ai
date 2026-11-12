<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/TimeCraft · page 2 Core Framework Architecture · fetched 2026-10-26 -->

# Core Framework Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [BRIDGE/README.md](BRIDGE/README.md)
- [README.md](README.md)
- [figures/pt_like_word_newcolors.png](figures/pt_like_word_newcolors.png)
- [supplementary/inference_guidance.md](supplementary/inference_guidance.md)
- [supplementary/inference_prototype.md](supplementary/inference_prototype.md)
- [supplementary/inference_prototype_text.md](supplementary/inference_prototype_text.md)

</details>



## Purpose and Scope

This document provides a comprehensive overview of the TimeCraft framework's core architecture, focusing on its three primary capabilities: cross-domain generalization, text-based control, and target-aware adaptation. The architecture is designed as a unified diffusion-based time series generation system with flexible conditioning mechanisms.

For detailed implementation of specific capabilities, see [Cross-Domain Generation with Semantic Prototypes](#2.1), [Text-Based Control and BRIDGE System](#2.2), and [Target-Aware Adaptation](#2.3). For information about specialized domain implementations, see [Specialized Systems](#3).

## Framework Overview

TimeCraft implements a modular architecture centered around a diffusion model backbone with three distinct input conditioning branches. The system provides a unified inference interface while supporting multiple generation modes based on different types of conditioning inputs.

### Core Architecture Components

```mermaid
graph TB
    subgraph "Input Conditioning Branches"
        PAM["Prototype Assignment Module (PAM)"]
        BRIDGE["BRIDGE Multi-Agent System"]
        GUIDE["Guidance Module"]
    end
    
    subgraph "Core Generation Engine"
        INF["inference.py"]
        MAIN["main.py"]
        LDM["LatentDiffusion Model"]
        UNET["UNet1D Architecture"]
    end
    
    subgraph "Supporting Infrastructure"
        CONFIG["config.yaml"]
        TSG["TSG Dataset Modules"]
        PREP["prepare_datasets.py"]
    end
    
    PAM --> INF
    BRIDGE --> INF
    GUIDE --> INF
    INF --> LDM
    LDM --> UNET
    MAIN --> LDM
    CONFIG --> MAIN
    TSG --> MAIN
    PREP --> TSG
```

**Sources:** [README.md:26-38](), [main.py](), [inference.py]()

### Three-Branch Input System

The framework supports three flexible input branches that can be used independently or in combination:

| Branch | Component | Input Type | Purpose |
|--------|-----------|------------|---------|
| **Cross-Domain** | `PAM` | Few-shot examples | Domain adaptation via semantic prototypes |
| **Text-Based** | `BRIDGE` | Natural language | Controllable generation via text descriptions |
| **Target-Aware** | `Guidance Module` | Downstream model | Task-oriented optimization |

**Sources:** [README.md:28-37](), [supplementary/inference_prototype.md:1-28](), [supplementary/inference_prototype_text.md:1-24](), [supplementary/inference_guidance.md:1-28]()

## Core Generation Pipeline

### Unified Inference Interface

The `inference.py` script serves as the central orchestrator for all generation modes, providing a unified interface that dynamically configures the diffusion process based on input conditioning:

```mermaid
graph LR
    subgraph "Inference Flow"
        INPUT["Input Conditioning"]
        PROC["Processing Logic"]
        DIFF["Diffusion Process"]
        OUTPUT["Generated Time Series"]
    end
    
    subgraph "Conditioning Modes"
        UNCOND["--uncond"]
        PAM_FLAG["--use_pam"]
        TEXT_FLAG["--use_text"]
        GUIDE_FLAG["--use_guidance"]
    end
    
    INPUT --> PROC
    PROC --> DIFF
    DIFF --> OUTPUT
    
    UNCOND --> PROC
    PAM_FLAG --> PROC
    TEXT_FLAG --> PROC
    GUIDE_FLAG --> PROC
```

**Sources:** [inference.py](), [supplementary/inference_prototype.md:17-26](), [supplementary/inference_prototype_text.md:9-23](), [supplementary/inference_guidance.md:10-25]()

### Diffusion Model Architecture

The core generation engine implements a LatentDiffusion model with UNet1D architecture optimized for time series data:

```mermaid
graph TB
    subgraph "Model Components"
        ENCODER["Encoder Modules"]
        UNET1D["UNet1D"]
        DECODER["Decoder"]
        NORM["Normalizers"]
    end
    
    subgraph "Training Pipeline"
        TRAIN_MAIN["main.py"]
        LIGHTNING["PyTorch Lightning"]
        OMEGA["OmegaConf"]
    end
    
    subgraph "Configuration"
        BASE_CONFIG["config.yaml"]
        MODEL_CONFIG["Model Parameters"]
        DATASET_CONFIG["Dataset Settings"]
    end
    
    ENCODER --> UNET1D
    UNET1D --> DECODER
    NORM --> ENCODER
    
    TRAIN_MAIN --> LIGHTNING
    LIGHTNING --> UNET1D
    OMEGA --> TRAIN_MAIN
    
    BASE_CONFIG --> OMEGA
    MODEL_CONFIG --> BASE_CONFIG
    DATASET_CONFIG --> BASE_CONFIG
```

**Sources:** [README.md:199-201](), [main.py](), [supplementary/training_details.md]()

## Cross-Domain Generation Capability

### Semantic Prototypes System

The cross-domain generation capability centers on learning universal semantic prototypes that encode domain-invariant temporal patterns. These prototypes function as a "dictionary" of reusable temporal components:

```mermaid
graph TB
    subgraph "Prototype Learning"
        PROTO["Semantic Prototypes"]
        DICT["Temporal Pattern Dictionary"]
        INVARIANT["Domain-Invariant Features"]
    end
    
    subgraph "Domain Adaptation"
        PAM_MOD["Prototype Assignment Module"]
        WEIGHTS["Dynamic Weights"]
        PROMPT["Domain Prompt"]
    end
    
    subgraph "Few-Shot Input"
        EXAMPLES["Few-shot Examples"]
        DOMAIN_CHAR["Domain Characteristics"]
    end
    
    PROTO --> DICT
    DICT --> INVARIANT
    INVARIANT --> PAM_MOD
    
    EXAMPLES --> PAM_MOD
    PAM_MOD --> WEIGHTS
    WEIGHTS --> PROMPT
    DOMAIN_CHAR --> PROMPT
```

**Sources:** [README.md:9-12](), [README.md:226-245]()

## Text-Based Control Capability

### BRIDGE Multi-Agent System

The text-based control capability implements a sophisticated multi-agent framework for generating and refining textual descriptions of time series patterns:

```mermaid
graph TB
    subgraph "BRIDGE System Components"
        COLLECT["Candidate Collection"]
        EXTRACT["Template Extraction"]
        REFINE["Multi-Agent Refinement"]
        OPTIMIZE["LLM Optimization"]
    end
    
    subgraph "Text Processing Pipeline"
        TS_TO_TEXT["ts_to_text.py"]
        TEMPLATES["Text Templates"]
        DESCRIPTIONS["Time Series Descriptions"]
    end
    
    subgraph "Hybrid Conditioning"
        PROTO_COND["Prototype Conditioning"]
        TEXT_COND["Text Conditioning"]
        HYBRID["Hybrid Prompt"]
    end
    
    COLLECT --> EXTRACT
    EXTRACT --> REFINE
    REFINE --> OPTIMIZE
    
    TS_TO_TEXT --> TEMPLATES
    TEMPLATES --> DESCRIPTIONS
    DESCRIPTIONS --> TEXT_COND
    
    PROTO_COND --> HYBRID
    TEXT_COND --> HYBRID
```

**Sources:** [README.md:14-15](), [README.md:248-268](), [BRIDGE/README.md:1-92]()

## Target-Aware Adaptation Capability

### Influence-Guided Diffusion

The target-aware adaptation capability uses influence functions to guide the diffusion process toward generating data that improves downstream task performance:

```mermaid
graph TB
    subgraph "Guidance Components"
        GUIDE_SET["Guidance Set"]
        DOWNSTREAM["Downstream Model"]
        INFLUENCE["Influence Functions"]
        GUIDANCE_MOD["Guidance Module"]
    end
    
    subgraph "Task Optimization"
        GRADIENTS["Loss Gradients"]
        STEERING["Diffusion Steering"]
        TASK_AWARE["Task-Aware Generation"]
    end
    
    subgraph "Integration"
        DENOISING["Denoising Steps"]
        FEEDBACK["Feedback Loop"]
        SYNTHETIC["Synthetic Data"]
    end
    
    GUIDE_SET --> GUIDANCE_MOD
    DOWNSTREAM --> GRADIENTS
    GRADIENTS --> INFLUENCE
    INFLUENCE --> GUIDANCE_MOD
    
    GUIDANCE_MOD --> STEERING
    STEERING --> DENOISING
    DENOISING --> FEEDBACK
    FEEDBACK --> TASK_AWARE
    TASK_AWARE --> SYNTHETIC
```

**Sources:** [README.md:17-18](), [README.md:271-282](), [supplementary/inference_guidance.md:1-28]()

## Data Processing Infrastructure

### Dataset Preparation Pipeline

The framework includes comprehensive data handling infrastructure for processing various time series datasets:

```mermaid
graph TB
    subgraph "Data Sources"
        MONASH["Monash Datasets"]
        GLUON["GluonTS"]
        FINANCIAL["Financial Data"]
        MEDICAL["Medical Records"]
    end
    
    subgraph "Processing Pipeline"
        PREP_SCRIPT["prepare_datasets.py"]
        DOWNLOAD["Dataset Download"]
        PREPROCESS["Data Preprocessing"]
        SEGMENT["Sliding Window Segmentation"]
    end
    
    subgraph "TSG Dataset Modules"
        TSG_CLASSES["TSG Dataset Classes"]
        NORMALIZATION["Normalization Methods"]
        PYTORCH_INTEGRATION["PyTorch Lightning Integration"]
    end
    
    MONASH --> PREP_SCRIPT
    GLUON --> PREP_SCRIPT
    FINANCIAL --> PREP_SCRIPT
    MEDICAL --> PREP_SCRIPT
    
    PREP_SCRIPT --> DOWNLOAD
    DOWNLOAD --> PREPROCESS
    PREPROCESS --> SEGMENT
    
    SEGMENT --> TSG_CLASSES
    TSG_CLASSES --> NORMALIZATION
    NORMALIZATION --> PYTORCH_INTEGRATION
```

**Sources:** [README.md:107-137](), [prepare_datasets.py](), [supplementary/dataset_split.md]()

## Configuration and Training

### Configuration Management

The framework uses OmegaConf for hierarchical configuration management, enabling flexible model and dataset configuration:

```mermaid
graph TB
    subgraph "Configuration Hierarchy"
        BASE["config.yaml"]
        MODEL_PARAMS["Model Parameters"]
        DATASET_PARAMS["Dataset Settings"]
        TRAINING_PARAMS["Training Configuration"]
    end
    
    subgraph "Training Scripts"
        MAIN_SCRIPT["main.py"]
        TARDIFF_TRAIN["TarDiff/train_main.py"]
        DIGA_TRAIN["DiGA/train.py"]
    end
    
    subgraph "Framework Integration"
        OMEGA_CONF["OmegaConf"]
        PYTORCH_LIGHTNING["PyTorch Lightning"]
        WANDB["Weights & Biases"]
    end
    
    BASE --> MODEL_PARAMS
    BASE --> DATASET_PARAMS
    BASE --> TRAINING_PARAMS
    
    MODEL_PARAMS --> MAIN_SCRIPT
    DATASET_PARAMS --> MAIN_SCRIPT
    TRAINING_PARAMS --> MAIN_SCRIPT
    
    MAIN_SCRIPT --> OMEGA_CONF
    OMEGA_CONF --> PYTORCH_LIGHTNING
    PYTORCH_LIGHTNING --> WANDB
    
    TARDIFF_TRAIN --> PYTORCH_LIGHTNING
    DIGA_TRAIN --> PYTORCH_LIGHTNING
```

**Sources:** [main.py](), [supplementary/training_details.md](), [TarDiff/train_main.py](), [DiGA/train.py]()

The TimeCraft framework's modular architecture enables flexible time series generation across multiple domains while maintaining a unified interface for different conditioning modes. The three-branch input system allows users to leverage domain knowledge, natural language descriptions, or task-specific objectives to guide the generation process effectively.

---

