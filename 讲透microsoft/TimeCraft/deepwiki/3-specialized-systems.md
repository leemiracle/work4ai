<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/TimeCraft · page 3 Specialized Systems · fetched 2026-10-26 -->

# Specialized Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [DiGA/README.md](DiGA/README.md)
- [TarDiff/README.md](TarDiff/README.md)

</details>



This document covers the specialized implementations built on top of the TimeCraft framework for domain-specific time series generation. These systems extend the core TimeCraft capabilities to address specific use cases in healthcare and financial domains.

For information about the core TimeCraft framework architecture, see [Core Framework Architecture](#2). For details about training and inference procedures, see [Training and Inference](#6).

## System Architecture Overview

The specialized systems leverage TimeCraft's diffusion-based generation capabilities while implementing domain-specific adaptations for targeted applications.

### Specialized System Relationship to TimeCraft Core

```mermaid
graph TB
    subgraph "TimeCraft Core Framework"
        TC["TimeCraft Core"]
        DIFF["Diffusion Models"]
        GUIDE["Guidance Systems"]
    end
    
    subgraph "TarDiff Specialization"
        TD["TarDiff System"]
        TRAIN_MAIN["train_main.py"]
        GUIDANCE_GEN["guidance_generation.py"]
        EHR_DATA["EHR Data Processing"]
        CLASSIFIER["classifier/"]
    end
    
    subgraph "DiGA Specialization"
        DG["DiGA System"]
        TRAIN_PY["train.py"]
        GENERATE_PY["generate.py"]
        MARKET_DATA["Market Data Processing"]
        RLTASK["rltask/"]
    end
    
    TC --> TD
    TC --> DG
    DIFF --> TRAIN_MAIN
    DIFF --> TRAIN_PY
    GUIDE --> GUIDANCE_GEN
    GUIDE --> GENERATE_PY
    
    TD --> EHR_DATA
    TD --> CLASSIFIER
    DG --> MARKET_DATA
    DG --> RLTASK
```

**Sources:** [DiGA/README.md:1-88](), [TarDiff/README.md:1-101]()

## TarDiff: EHR Time Series Generation System

TarDiff implements target-oriented diffusion guidance for synthetic Electronic Health Record time series generation. The system addresses data scarcity and class imbalance in healthcare analytics through influence-guided generation.

### TarDiff Training Pipeline

```mermaid
graph LR
    subgraph "Stage 1: Base Training"
        BASE_CONFIG["configs/base/"]
        TRAIN_SH["train.sh"]
        BASE_MODEL["Base Diffusion Model"]
    end
    
    subgraph "Stage 2: Classifier Training"
        CLASSIFIER_DIR["classifier/"]
        CLASSIFIER_TRAIN["classifier/train.sh"]
        TASK_MODEL["Task Model Weights"]
    end
    
    subgraph "Stage 3: Guided Generation"
        GENERATION_SH["generation.sh"]
        GUIDANCE_GEN["guidance_generation.py"]
        SYNTHETIC_DATA["Synthetic EHR Data"]
    end
    
    subgraph "Stage 4: Evaluation"
        TSTR["TSTR Protocol"]
        TSRTR["TSRTR Protocol"]
        UTILITY_EVAL["Utility Assessment"]
    end
    
    BASE_CONFIG --> TRAIN_SH
    TRAIN_SH --> BASE_MODEL
    CLASSIFIER_DIR --> CLASSIFIER_TRAIN
    CLASSIFIER_TRAIN --> TASK_MODEL
    
    BASE_MODEL --> GENERATION_SH
    TASK_MODEL --> GENERATION_SH
    GENERATION_SH --> GUIDANCE_GEN
    GUIDANCE_GEN --> SYNTHETIC_DATA
    
    SYNTHETIC_DATA --> TSTR
    SYNTHETIC_DATA --> TSRTR
    TSTR --> UTILITY_EVAL
    TSRTR --> UTILITY_EVAL
```

**Sources:** [TarDiff/README.md:35-100]()

### TarDiff Data Processing

The system processes EHR data from MIMIC-III and eICU databases, focusing on multivariate time-series recordings. Data preprocessing utilities are provided for extraction and preparation.

| Component | Location | Purpose |
|-----------|----------|---------|
| Data Preprocessing | `data_preprocess/` | High-level extraction scripts |
| MIMIC-III Support | Raw data access | Clinical database integration |
| eICU Support | Raw data access | Collaborative research database |

**Sources:** [TarDiff/README.md:21-32]()

### TarDiff Evaluation Protocols

The system implements two complementary evaluation protocols for assessing synthetic data utility:

| Protocol | Training Set | Test Set | Purpose |
|----------|-------------|----------|---------|
| TSTR | Synthetic only | Real | Assess pure synthetic training effectiveness |
| TSRTR | Synthetic + Real (α ratios) | Real | Evaluate augmentation benefits |

**Sources:** [TarDiff/README.md:73-96]()

## DiGA: Market Trading Data Generation System

DiGA (Diffusion Guided Meta Agent) specializes in generating synthetic market trading records for training reinforcement learning agents in financial applications.

### DiGA System Components

```mermaid
graph TB
    subgraph "Meta Controller Training"
        TRAIN_PY["train.py"]
        CTRL_CONFIG["Control Configuration"]
        META_CTRL["Meta Controller Model"]
    end
    
    subgraph "Meta Agent Generation"
        GENERATE_PY["generate.py"]
        CTRL_CLASS["Control Classes"]
        TRADE_RECORDS["Trading Records"]
    end
    
    subgraph "RL Environment"
        RLTASK_DIR["rltask/"]
        TRAIN_TEST_RL["train_test_rl.py"]
        RL_AGENT["RL Agent"]
    end
    
    subgraph "Data Processing"
        MARKET_DATA["Market State Data"]
        DATA_SHAPE["(N, C, T) Format"]
        PRICE_ORDERS["Price/Order Features"]
    end
    
    TRAIN_PY --> CTRL_CONFIG
    CTRL_CONFIG --> META_CTRL
    META_CTRL --> GENERATE_PY
    GENERATE_PY --> CTRL_CLASS
    CTRL_CLASS --> TRADE_RECORDS
    
    TRADE_RECORDS --> RLTASK_DIR
    RLTASK_DIR --> TRAIN_TEST_RL
    TRAIN_TEST_RL --> RL_AGENT
    
    MARKET_DATA --> DATA_SHAPE
    DATA_SHAPE --> PRICE_ORDERS
    PRICE_ORDERS --> TRAIN_PY
```

**Sources:** [DiGA/README.md:1-43]()

### DiGA Training Configuration

The system supports flexible control mechanisms for generating targeted market behaviors:

| Parameter | Options | Purpose |
|-----------|---------|---------|
| `ctrl_type` | continuous, discrete | Control encoder type |
| `ctrl_target` | return, volatility | Target market characteristic |
| `n_bins` | Integer | Discretization granularity |
| `ctrl_class` | 0-n | Specific control condition |

**Sources:** [DiGA/README.md:44-78]()

### DiGA Data Format Requirements

The system requires market data in specific tensor format:
- **Shape**: `(N, C, T)` where N=samples, C=features, T=time steps
- **Features**: C=2 dimensions (mid-price log return rate, order count)
- **Temporal**: T=236 effective trading minutes per day

**Sources:** [DiGA/README.md:16-17]()

## Implementation Comparison

### Training Script Patterns

```mermaid
graph LR
    subgraph "TarDiff Training"
        TD_TRAIN["train.sh"]
        TD_CONFIG["configs/base/"]
        TD_MAIN["train_main.py"]
    end
    
    subgraph "DiGA Training"
        DG_TRAIN["train.py"]
        DG_ARGS["Command Line Args"]
        DG_CTRL["Control Parameters"]
    end
    
    subgraph "Common Elements"
        DIFFUSION["Diffusion Models"]
        CHECKPOINTS["Model Checkpoints"]
        DATA_PATHS["Data Path Management"]
    end
    
    TD_TRAIN --> TD_CONFIG
    TD_CONFIG --> TD_MAIN
    DG_TRAIN --> DG_ARGS
    DG_ARGS --> DG_CTRL
    
    TD_MAIN --> DIFFUSION
    DG_CTRL --> DIFFUSION
    DIFFUSION --> CHECKPOINTS
    CHECKPOINTS --> DATA_PATHS
```

**Sources:** [TarDiff/README.md:37-43](), [DiGA/README.md:22-28]()

### Generation and Evaluation Workflows

Both systems implement distinct generation and evaluation approaches:

- **TarDiff**: Uses influence-guided generation with `guidance_generation.py` and evaluates through TSTR/TSRTR protocols
- **DiGA**: Employs meta-agent sampling with `generate.py` and evaluates through RL training environments

The specialized systems demonstrate domain-specific adaptations while maintaining compatibility with the core TimeCraft diffusion framework.

**Sources:** [TarDiff/README.md:61-96](), [DiGA/README.md:30-42]()

---

