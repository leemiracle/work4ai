<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/cartography · page 3 Core Systems · fetched 2026-10-26 -->

# Core Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [cartography/__init__.py](cartography/__init__.py)
- [cartography/classification/__init__.py](cartography/classification/__init__.py)
- [cartography/selection/__init__.py](cartography/selection/__init__.py)

</details>



## Purpose and Scope

This document provides a comprehensive overview of the core architectural components that make up the Dataset Cartography system and how they interact to enable training dynamics analysis and data selection. The system consists of two primary workflows: training models while collecting dynamics data, and analyzing those dynamics to create data maps and filtered datasets.

For specific implementation details of individual components, see [Training with Dynamics Collection](#3.1), [Data Analysis and Selection](#3.2), and [Data Processing Utilities](#3.3). For configuration management, see [Configuration Management](#4).

## System Overview

The Dataset Cartography system is built around a two-phase architecture that separates model training from data analysis. The core systems work together to collect training dynamics during model training, then analyze those dynamics to understand dataset characteristics.

### Primary System Components

```mermaid
graph TB
    subgraph "Phase 1: Training & Dynamics Collection"
        A["cartography.classification.run_glue"] 
        B["cartography.classification.models"]
        C["cartography.classification.glue_utils"]
    end
    
    subgraph "Phase 2: Analysis & Selection"
        D["cartography.selection.train_dy_filtering"]
        E["cartography.selection.selection_utils"]
        F["cartography.selection.random_filtering"]
    end
    
    subgraph "Configuration Layer"
        G["cartography.classification.params"]
        H["configs/*.jsonnet"]
    end
    
    subgraph "Data Infrastructure"
        I["cartography.data_utils"]
        J["cartography.data_utils_glue"]
    end
    
    subgraph "Analysis Tools"
        K["cartography.classification.diagnostics_evaluation"]
        L["notebooks/"]
    end
    
    H --> G
    G --> A
    I --> A
    J --> A
    B --> A
    C --> A
    
    A --> E
    E --> D
    I --> D
    I --> F
    
    D --> L
    A --> K
    
    style A fill:#f9f9f9
    style D fill:#f9f9f9
```

**Sources:** [README.md:26-46](), [README.md:48-68](), [README.md:70-87]()

## Core Pipeline Architecture

The system implements a clear separation between training and analysis phases, with standardized data formats enabling interoperability between components.

### Training Dynamics Pipeline

```mermaid
flowchart TD
    A["configs/TASK.jsonnet"] --> B["cartography.classification.run_glue"]
    C["GLUE TSV datasets"] --> D["cartography.data_utils"]
    D --> B
    
    B --> E["training_dynamics/dynamics_epoch_X.jsonl"]
    
    E --> F["cartography.selection.train_dy_filtering"]
    
    F --> G{Analysis Mode}
    G -->|"--plot"| H["Data Map Visualizations"]
    G -->|"--filter"| I["Filtered Training Sets"]
    
    subgraph "Training Dynamics Format"
        J["guid: instance_id"]
        K["logits_epoch_X: predictions"]
        L["gold: true_labels"]
    end
    
    subgraph "Computed Metrics"
        M["confidence"]
        N["variability"] 
        O["correctness"]
        P["forgetfulness"]
        Q["threshold_closeness"]
    end
    
    E --> J
    E --> K
    E --> L
    
    F --> M
    F --> N
    F --> O
    F --> P
    F --> Q
```

**Sources:** [README.md:26-46](), [README.md:42-46](), [README.md:70-87]()

## Component Interactions

The core systems interact through well-defined interfaces and standardized data formats, enabling modular development and experimentation.

### Data Flow and System Integration

```mermaid
graph LR
    subgraph "Input Layer"
        A["GLUE TSV Files"]
        B["JSONNet Configs"]
    end
    
    subgraph "Processing Layer"
        C["cartography.data_utils.read_data"]
        D["cartography.classification.params"]
        E["cartography.classification.run_glue.main"]
    end
    
    subgraph "Training Infrastructure"
        F["HuggingFace Transformers"]
        G["cartography.classification.models"]
        H["Multi-GPU Support"]
    end
    
    subgraph "Dynamics Collection"
        I["training_dynamics/"]
        J["dynamics_epoch_X.jsonl"]
    end
    
    subgraph "Analysis Layer"
        K["cartography.selection.selection_utils.read_training_dynamics"]
        L["cartography.selection.train_dy_filtering.main"]
        M["cartography.selection.train_dy_filtering.compute_metrics"]
    end
    
    subgraph "Output Layer"
        N["Data Map PDFs"]
        O["Filtered Datasets"]
        P["Diagnostic Results"]
    end
    
    A --> C
    B --> D
    C --> E
    D --> E
    
    E --> F
    F --> G
    G --> H
    
    E --> I
    I --> J
    
    J --> K
    K --> L
    L --> M
    
    L --> N
    L --> O
    E --> P
```

**Sources:** [README.md:26-36](), [README.md:48-58](), [README.md:70-81]()

## Key Architectural Patterns

### Configuration-Driven Design

The system uses a centralized configuration approach where `cartography.classification.params` manages all training parameters, while task-specific configurations are defined in JSONNet files under `configs/`. This pattern enables:

- **Reproducible Experiments**: All parameters are versioned and declarative
- **Task Extensibility**: New tasks can be added by creating new configuration files
- **Parameter Sharing**: Common settings are centralized while task-specific overrides are isolated

### Training Dynamics as First-Class Data

Training dynamics are collected and stored in a standardized JSONL format with required fields `guid`, `logits_epoch_X`, and `gold`. This design enables:

- **Cross-Model Compatibility**: Any training setup can produce compatible dynamics files
- **Offline Analysis**: Training and analysis phases are completely decoupled
- **Metric Computation**: Multiple analysis metrics can be computed from the same dynamics data

### Modular Analysis Pipeline

The `cartography.selection.train_dy_filtering` module serves as the central analysis engine, supporting both visualization (`--plot`) and data selection (`--filter`) modes. This modularity allows:

- **Flexible Workflows**: Users can run analysis without retraining models
- **Multiple Metrics**: Support for `confidence`, `variability`, `correctness`, `forgetfulness`, and `threshold_closeness`
- **Baseline Comparisons**: Integration with `cartography.selection.random_filtering` for control experiments

**Sources:** [README.md:37](), [README.md:42-46](), [README.md:75-87]()

## System Dependencies

| Component | Primary Dependencies | Purpose |
|-----------|---------------------|---------|
| `cartography.classification.run_glue` | HuggingFace Transformers, `cartography.classification.models` | Model training with dynamics collection |
| `cartography.selection.train_dy_filtering` | `cartography.selection.selection_utils`, `cartography.data_utils` | Dynamics analysis and data selection |
| `cartography.classification.params` | `configs/*.jsonnet` | Centralized parameter management |
| `cartography.data_utils` | - | GLUE-style data reading and processing |

The system's modular architecture allows components to be used independently or in combination, supporting both end-to-end workflows and specialized analysis tasks.

**Sources:** [README.md:22](), [cartography/classification/__init__.py:1](), [cartography/selection/__init__.py:1]()

---

