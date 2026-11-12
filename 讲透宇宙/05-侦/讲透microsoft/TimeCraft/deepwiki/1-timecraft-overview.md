<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/TimeCraft · page 1 TimeCraft Overview · fetched 2026-10-26 -->

# TimeCraft Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [BRIDGE/README.md](BRIDGE/README.md)
- [README.md](README.md)
- [figures/pt_like_word_newcolors.png](figures/pt_like_word_newcolors.png)

</details>



## Purpose and Scope

TimeCraft is a diffusion-based time series generation framework designed for real-world applications. This document provides a high-level overview of the system architecture, core capabilities, and key components. For detailed information about specific subsystems, see [Core Framework Architecture](#2), [Specialized Systems](#3), and [Data Infrastructure](#4).

The framework addresses three main challenges in time series generation: cross-domain generalization, text-based controllability, and target-aware adaptation for downstream tasks.

## System Architecture

TimeCraft follows a layered architecture with three primary tiers: the core framework, specialized implementations, and supporting infrastructure.

### Overall System Structure

```mermaid
graph TB
    subgraph "Core Framework"
        TC["TimeCraft Core<br/>main.py"]
        INF["Unified Inference<br/>inference.py"]
        PAM["Prototype Assignment Module<br/>PAM"]
        BRIDGE["BRIDGE System<br/>BRIDGE/"]
        GUIDE["Guidance Module<br/>influence functions"]
    end
    
    subgraph "Specialized Systems"
        TD["TarDiff<br/>EHR Time Series<br/>TarDiff/"]
        DG["DiGA<br/>Market Trading<br/>DiGA/"]
    end
    
    subgraph "Data Infrastructure"
        PREP["Dataset Preparation<br/>prepare_datasets.py"]
        TSG["TSG Dataset Modules<br/>TSG/"]
        NORM["Normalizers<br/>data preprocessing"]
    end
    
    subgraph "Model Components"
        DIFF["Diffusion Models<br/>LatentDiffusion"]
        ENC["Encoders<br/>conditional processing"]
        UNET["UNet1D<br/>architecture"]
    end
    
    TC --> INF
    TC --> PAM
    TC --> BRIDGE
    TC --> GUIDE
    
    INF --> TD
    INF --> DG
    
    PREP --> TSG
    TSG --> TC
    
    DIFF --> INF
    ENC --> DIFF
    UNET --> DIFF
    
    PAM --> INF
    BRIDGE --> INF
    GUIDE --> INF
```

**Sources:** [README.md:1-308]()

### Core Input-Output Flow

```mermaid
graph LR
    subgraph "Input Types"
        FS["Few-shot Examples<br/>Domain Prompts"]
        TXT["Text Descriptions<br/>Natural Language"]
        DS["Downstream Tasks<br/>Gradient Guidance"]
    end
    
    subgraph "Processing Pipeline"
        PAM_MOD["PAM Module<br/>prototype assignment"]
        BRIDGE_SYS["BRIDGE System<br/>multi-agent text processing"]
        GUIDE_MOD["Guidance Module<br/>influence functions"]
        INFERENCE["inference.py<br/>unified generation"]
    end
    
    subgraph "Output Modes"
        CROSS["Cross-Domain<br/>Time Series"]
        CTRL["Text-Controlled<br/>Time Series"]
        TARGET["Target-Aware<br/>Time Series"]
    end
    
    FS --> PAM_MOD
    TXT --> BRIDGE_SYS
    DS --> GUIDE_MOD
    
    PAM_MOD --> INFERENCE
    BRIDGE_SYS --> INFERENCE
    GUIDE_MOD --> INFERENCE
    
    INFERENCE --> CROSS
    INFERENCE --> CTRL
    INFERENCE --> TARGET
```

**Sources:** [README.md:26-37]()

## Core Capabilities

### 1. Cross-Domain Generalization

TimeCraft introduces semantic prototypes that act as reusable temporal patterns across domains. The `PAM` (Prototype Assignment Module) dynamically computes domain-specific weights using few-shot examples to construct domain prompts.

| Component | File/Module | Function |
|-----------|-------------|----------|
| Semantic Prototypes | Core framework | Learn domain-invariant features |
| PAM Module | `PAM` class | Compute domain-specific weights |
| Domain Prompts | Generated representations | Capture target domain characteristics |

### 2. Text-Based Control

The BRIDGE system enables natural language control over time series generation through a multi-agent framework.

```mermaid
graph TB
    subgraph "BRIDGE System"
        COLLECT["Candidate Collection<br/>web scraping"]
        EXTRACT["Template Extraction<br/>template_extractor.py"]
        REFINE["Multi-Agent Refinement<br/>multi_agent_refiner.py"]
        GENERATE["Text Generation<br/>ts_to_text.py"]
    end
    
    subgraph "Text Processing Pipeline"
        TEMPLATES["Text Templates<br/>text_templates_example.json"]
        FEATURES["Statistical Features<br/>extraction"]
        DESCRIPTIONS["Time Series Descriptions<br/>_with_descriptions.csv"]
    end
    
    COLLECT --> EXTRACT
    EXTRACT --> REFINE
    REFINE --> GENERATE
    
    TEMPLATES --> FEATURES
    FEATURES --> DESCRIPTIONS
    GENERATE --> DESCRIPTIONS
```

**Sources:** [README.md:139-155](), [BRIDGE/README.md:1-92]()

### 3. Target-Aware Adaptation

TimeCraft optimizes synthetic sample generation for downstream task performance using influence-guided diffusion.

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| Guidance Set | Approximate downstream distribution | Training set or custom subset |
| Downstream Model | Task-specific requirements | Any differentiable architecture |
| Guidance Module | Gradient injection | Influence function computation |

## Key Components and Files

### Training and Inference

```mermaid
graph TB
    subgraph "Training Pipeline"
        MAIN["main.py<br/>TimeCraft training"]
        TAR_TRAIN["train_main.py<br/>TarDiff training"]
        DIGA_TRAIN["train.py<br/>DiGA training"]
        CONFIG["YAML configs<br/>model parameters"]
    end
    
    subgraph "Inference Pipeline"
        INF_MAIN["inference.py<br/>unified interface"]
        GEN_SCRIPTS["generate.py<br/>generation scripts"]
        GUIDE_GEN["guidance_generation.py<br/>target-aware generation"]
        VIS["visualize.py<br/>domain prompt visualization"]
    end
    
    CONFIG --> MAIN
    CONFIG --> TAR_TRAIN
    CONFIG --> DIGA_TRAIN
    
    MAIN --> INF_MAIN
    TAR_TRAIN --> GUIDE_GEN
    DIGA_TRAIN --> GEN_SCRIPTS
    
    INF_MAIN --> VIS
```

**Sources:** [README.md:199-217]()

### Data Processing Architecture

```mermaid
graph LR
    subgraph "Data Sources"
        MONASH["Monash Datasets<br/>temperature, wind, pedestrian"]
        GLUON["GluonTS Datasets<br/>solar, electricity, traffic"]
        MIMIC["MIMIC-III<br/>EHR data"]
        FINANCIAL["Financial Data<br/>stock, trading"]
    end
    
    subgraph "Processing Pipeline"
        PREP_SCRIPT["prepare_datasets.py<br/>download & preprocess"]
        TSG_MODULES["TSG Dataset Classes<br/>normalization & splitting"]
        SLIDING["Sliding Window<br/>segmentation"]
        ZERO_SHOT["Zero-shot Setup<br/>test/prompt splits"]
    end
    
    subgraph "Output Formats"
        NPY["NumPy Arrays<br/>train/val splits"]
        CSV["CSV Files<br/>time-indexed data"]
        PICKLE["Pickle Files<br/>tuples (data, labels)"]
    end
    
    MONASH --> PREP_SCRIPT
    GLUON --> PREP_SCRIPT
    MIMIC --> TSG_MODULES
    FINANCIAL --> PREP_SCRIPT
    
    PREP_SCRIPT --> SLIDING
    TSG_MODULES --> SLIDING
    SLIDING --> ZERO_SHOT
    
    SLIDING --> NPY
    PREP_SCRIPT --> CSV
    TSG_MODULES --> PICKLE
```

**Sources:** [README.md:99-138]()

## Usage Patterns

### Command-Line Interface

The framework supports flexible input combinations through command-line arguments:

```bash
# Domain prompt generation
python inference.py --domain_prompt

# Text-controlled generation  
python inference.py --text_control

# Target-aware generation
python inference.py --guidance_mode
```

### Configuration Management

The system uses YAML configuration files with OmegaConf for parameter management, supporting:

- Model architecture parameters
- Training hyperparameters  
- Dataset specifications
- Inference modes

### Extensibility

TimeCraft's modular design allows for:

- Custom dataset integration via TSG modules
- New specialized systems (like TarDiff and DiGA)
- Additional guidance mechanisms
- Custom text processing pipelines

**Sources:** [README.md:92-223]()

---

