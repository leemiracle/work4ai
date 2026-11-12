<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/PhysioPro · page 2 Core Components · fetched 2026-10-26 -->

# Core Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [physiopro/dataset/__init__.py](physiopro/dataset/__init__.py)
- [physiopro/model/__init__.py](physiopro/model/__init__.py)
- [physiopro/network/__init__.py](physiopro/network/__init__.py)

</details>



PhysioPro is built around a modular architecture with several core components that work together to process and analyze physiological data. This page provides an overview of these key subsystems and how they interrelate. For detailed information about individual components, please refer to their dedicated documentation pages.

The core components of PhysioPro consist of:
- Dataset System: For loading and processing physiological data [Dataset System](#2.1)
- Network Architectures: Deep learning models specialized for time series [Network Architectures](#2.2)
- Model System: Classes that manage training and evaluation [Model System](#2.3)

## Component Architecture

The following diagram illustrates the high-level architecture and interactions between PhysioPro's core components:

```mermaid
graph TD
    subgraph "Core Components"
        DS["DATASETS Registry"] --> BaseD["BaseDataset Classes"]
        NET["NETWORKS Registry"] --> BaseN["Network Architectures"]
        MOD["MODELS Registry"] --> BaseM["BaseModel"]
        
        BaseD --> |"Data Input"| BaseM
        BaseN --> |"Neural Network"| BaseM
        BaseM --> |"Training & Inference"| OUT["Results/Metrics"]
    end
    
    subgraph "Configuration"
        CFG["YAML Config"] --> DS
        CFG --> NET
        CFG --> MOD
    end
```

Sources: [physiopro/dataset/__init__.py](physiopro/dataset/__init__.py), [physiopro/model/__init__.py](physiopro/model/__init__.py), [physiopro/network/__init__.py](physiopro/network/__init__.py)

## Dataset System

The Dataset System handles data loading, preprocessing, and batching for physiological data. PhysioPro implements various dataset classes to support different data types and processing needs.

### Dataset Class Hierarchy

```mermaid
graph TD
    DATASETS["DATASETS Registry"] --> BaseDS["BaseDataset"]
    BaseDS --> TS["TSDataset"]
    BaseDS --> DF["DfDataset"]
    BaseDS --> ED["EventDataset"]
    
    TS --> MTS["MaskTSDataset"]
    
    BaseDS --> CinC["CinC2020"]
    BaseDS --> SEED["SEED"]
```

Sources: [physiopro/dataset/__init__.py:4-10](physiopro/dataset/__init__.py:4-10)

### Available Dataset Classes

| Dataset Class | Purpose |
|---------------|---------|
| `TSDataset` | Base class for time series data |
| `MaskTSDataset` | For time series with missing values |
| `DfDataset` | For pandas DataFrame-based data |
| `EventDataset` | For temporal point process/event data |
| `CinC2020` | For cardiac signal analysis |
| `SEED` | For EEG-based emotion recognition |

Sources: [physiopro/dataset/__init__.py:4-10](physiopro/dataset/__init__.py:4-10)

## Network Architectures

PhysioPro provides multiple neural network architectures specialized for physiological and time series data. These networks serve as the computational backbone for models.

### Network Architecture Hierarchy

```mermaid
graph TD
    NETWORKS["NETWORKS Registry"] --> TSRNN["TSRNN"]
    NETWORKS --> TCN["TemporalConvNet"]
    NETWORKS --> TST["TSTransformer"]
    NETWORKS --> DAW["DeepAndWide"]
    NETWORKS --> CF["ContiFormer"]
    NETWORKS --> MMM["MMM_Encoder"]
```

Sources: [physiopro/network/__init__.py:1-6](physiopro/network/__init__.py:1-6)

### Available Network Architectures

| Network Architecture | Purpose |
|---------------------|---------|
| `TSRNN` | Recurrent Neural Networks for time series |
| `TemporalConvNet` | Temporal convolutional networks |
| `TSTransformer` | Transformer architecture for time series |
| `DeepAndWide` | Network for CinC2020 cardiac data |
| `ContiFormer` | Continuous-time transformer for irregular time series |
| `MMM_Encoder` | Specialized encoder for EEG data |

Sources: [physiopro/network/__init__.py:1-6](physiopro/network/__init__.py:1-6)

## Model System

The Model System combines datasets and networks with training logic to create end-to-end solutions for physiological data analysis tasks. Models handle training loops, evaluation metrics, and checkpointing.

### Model Class Hierarchy

```mermaid
graph TD
    MODELS["MODELS Registry"] --> BM["BaseModel"]
    BM --> TS["TS"]
    BM --> MTS["MaskTS"]
    BM --> CinC["CinC2020"]
    BM --> MMF["MMM_Finetune"]
    BM --> TPP["TPP"]
```

Sources: [physiopro/model/__init__.py:1-6](physiopro/model/__init__.py:1-6)

### Available Model Classes

| Model Class | Purpose |
|-------------|---------|
| `BaseModel` | Base class with common functionality |
| `TS` | For general time series prediction |
| `MaskTS` | For time series with missing values |
| `CinC2020` | For cardiac signal analysis |
| `MMM_Finetune` | For EEG-based emotion recognition |
| `TPP` | For temporal point process modeling |

Sources: [physiopro/model/__init__.py:1-6](physiopro/model/__init__.py:1-6)

## Component Integration and Data Flow

The following diagram illustrates how data flows through PhysioPro's core components during a typical training or inference process:

```mermaid
flowchart LR
    CFG["YAML Config"] --> |"Instantiates"| DS["Dataset Class"]
    CFG --> |"Instantiates"| NET["Network Architecture"]
    CFG --> |"Instantiates"| MOD["Model Class"]
    
    DS --> |"Data Batches"| MOD
    NET --> |"Neural Network"| MOD
    
    MOD --> |"Forward Pass"| PRED["Predictions"]
    PRED --> |"Compare with Targets"| LOSS["Loss Calculation"]
    LOSS --> |"Backward Pass"| OPT["Optimizer Step"]
    OPT --> |"Update"| NET
    
    MOD --> |"Evaluation"| METRIC["Metrics"]
    MOD --> |"Checkpointing"| CKPT["Model Checkpoints"]
```

Sources: [physiopro/dataset/__init__.py](physiopro/dataset/__init__.py), [physiopro/model/__init__.py](physiopro/model/__init__.py), [physiopro/network/__init__.py](physiopro/network/__init__.py)

## Registry Pattern

PhysioPro uses a registry pattern for component management. Each core component type (Dataset, Network, Model) has an associated registry that enables dynamic component selection via configuration.

```mermaid
graph TD
    subgraph "Registry System"
        DATASETS["DATASETS Registry"] --> |"Registers"| DS1["Dataset Classes"]
        NETWORKS["NETWORKS Registry"] --> |"Registers"| NET1["Network Classes"]
        MODELS["MODELS Registry"] --> |"Registers"| MOD1["Model Classes"]
        
        CFG["YAML Config"] --> |"References by name"| DATASETS
        CFG --> |"References by name"| NETWORKS
        CFG --> |"References by name"| MODELS
        
        DATASETS --> |"Instantiates"| DSI["Dataset Instance"]
        NETWORKS --> |"Instantiates"| NETI["Network Instance"]
        MODELS --> |"Instantiates"| MODI["Model Instance"]
    end
```

Sources: [physiopro/dataset/__init__.py:4](physiopro/dataset/__init__.py:4), [physiopro/model/__init__.py:1](physiopro/model/__init__.py:1), [physiopro/network/__init__.py:1](physiopro/network/__init__.py:1)

## Specialized Components

Two key specialized components in PhysioPro deserve special attention:

1. **MMM_Encoder**: A specialized architecture for processing EEG data that preserves topological relationships between channels.

2. **ContiFormer**: A continuous-time transformer that handles irregularly sampled time series through ODE-based components.

For detailed information about these specialized components, see [MMM_Encoder](#2.2.1) and [ContiFormer](#2.2.2).

## Summary

PhysioPro's core components provide a flexible, modular framework for physiological data analysis:

- **Dataset System**: Handles data loading and preprocessing
- **Network Architectures**: Provide specialized neural networks for time series
- **Model System**: Manages the training and evaluation process

Each component type follows a consistent organization with:
- A registry for dynamic component selection
- A base class defining common functionality
- Specialized implementations for specific data types and tasks

For more detailed information about specific components, refer to their dedicated documentation pages:
- [Dataset System](#2.1)
- [Network Architectures](#2.2)
- [Model System](#2.3)

---

