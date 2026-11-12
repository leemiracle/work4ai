<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/denoised-smoothing · page 2 System Components · fetched 2026-10-26 -->

# System Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document provides an overview of the core system components that implement the denoised smoothing pipeline in the Microsoft denoised-smoothing repository. It describes the high-level architecture and interaction between major subsystems that enable provable adversarial robustness for pretrained image classifiers.

For detailed information about specific subsystems, see:
- Training pipeline implementation details: [Training Pipeline](#2.1)
- Certification process and algorithms: [Certification Engine](#2.2)  
- Cloud vision API integration: [Vision API Integration](#2.3)

## Core Architecture Overview

The denoised-smoothing system consists of four primary components that work together to provide certified robustness guarantees:

```mermaid
graph TB
    subgraph "Core Training Components"
        A["train_classifier.py"] 
        B["train_denoiser.py"]
        C["architectures.py"]
    end
    
    subgraph "Certification & Evaluation"
        D["certify.py"]
        E["test_denoiser.py"]
    end
    
    subgraph "Vision API Integration"
        F["RobustAPI class"]
        G["vision_api/ module"]
    end
    
    subgraph "Analysis & Reporting"
        H["analyze.py"]
        I["generate_github_result.py"]
        J["visualize.py"]
    end
    
    C --> A
    C --> B
    A --> D
    B --> D
    A --> E
    B --> E
    B --> F
    D --> H
    E --> H
    D --> I
    H --> J
```

**Component Interaction Flow**

Sources: [README.md:40-48](), [README.md:23-38]()

## File Organization and Data Flow

```mermaid
flowchart TD
    subgraph "code/ Directory"
        A["train_classifier.py"]
        B["train_denoiser.py"] 
        C["train_denoiser_multi_classifier.py"]
        D["certify.py"]
        E["test_denoiser.py"]
        F["architectures.py"]
        G["visualize.py"]
        H["analyze.py"]
        I["generate_github_result.py"]
    end
    
    subgraph "vision_api/ Directory"
        J["RobustAPI"]
        K["tutorial.ipynb"]
    end
    
    subgraph "External Data"
        L["CIFAR-10 Dataset"]
        M["ImageNet Dataset"]
        N["Cloud Vision APIs"]
    end
    
    subgraph "Model Assets"
        O["pretrained_models/"]
        P["Trained Classifiers"]
        Q["Trained Denoisers"]
    end
    
    subgraph "Results & Analysis"
        R["data/ (certification logs)"]
        S["analysis/ (plots & tables)"]
    end
    
    F --> A
    F --> B
    L --> A
    M --> A
    L --> B
    M --> B
    A --> P
    B --> Q
    C --> Q
    
    P --> D
    Q --> D
    L --> D
    M --> D
    D --> R
    
    P --> E
    Q --> E
    E --> R
    
    Q --> J
    N --> J
    
    R --> H
    H --> S
    R --> I
    I --> S
    
    P --> G
    Q --> G
```

**System Data Flow Architecture**

Sources: [README.md:40-48](), [README.md:25-38]()

## Component Responsibilities

### Training Infrastructure

| Component | File Path | Primary Function |
|-----------|-----------|------------------|
| **Classifier Training** | `code/train_classifier.py` | Train ImageNet/CIFAR-10 classifiers with optional Gaussian augmentation |
| **Denoiser Training** | `code/train_denoiser.py` | Train denoisers using MSE or stability objectives |
| **Multi-Classifier Training** | `code/train_denoiser_multi_classifier.py` | Train denoisers using multiple surrogate models |
| **Architecture Registry** | `code/architectures.py` | Define and specify model architectures for classifiers and denoisers |

Sources: [README.md:42-48]()

### Certification and Evaluation

| Component | File Path | Primary Function |
|-----------|-----------|------------------|
| **Certification Engine** | `code/certify.py` | Compute certified L2-radius using Cohen et al. algorithm |
| **Denoiser Testing** | `code/test_denoiser.py` | Evaluate denoiser reconstruction and classification performance |
| **Visualization** | `code/visualize.py` | Generate visual comparisons of noisy and denoised images |

Sources: [README.md:45-47]()

### Analysis and Reporting

```mermaid
graph LR
    A["certify.py output"] --> B["analyze.py"]
    C["test_denoiser.py results"] --> B
    B --> D["LaTeX Tables"]
    B --> E["Performance Plots"]
    A --> F["generate_github_result.py"]
    F --> G["Certification Curves"]
```

**Analysis Pipeline Components**

| Component | File Path | Primary Function |
|-----------|-----------|------------------|
| **Result Analysis** | `code/analyze.py` | Generate paper tables and figures from certification logs |
| **GitHub Results** | `code/generate_github_result.py` | Create certification curve visualizations |

Sources: [README.md:146-151](), [README.md:137-143]()

### Vision API Integration

The `vision_api/` module provides a unified interface for robustifying cloud-based vision services:

```mermaid
graph TB
    A["RobustAPI class"] --> B["predict() method"]
    A --> C["certify() method"]
    
    B --> D["Online Mode"]
    B --> E["Offline Mode"]
    C --> D
    C --> E
    
    D --> F["azure API"]
    D --> G["google API"] 
    D --> H["aws API"]
    D --> I["clarifai API"]
    
    E --> J["Query Logs"]
```

**RobustAPI Architecture**

Key methods and usage patterns:
- `RobustAPI(api_name, denoiser=denoiser, online=True).predict(img, ...)` - Online prediction
- `RobustAPI(api_name, denoiser=denoiser, online=True).certify(img, ...)` - Online certification  
- `RobustAPI(api_name, online=False).predict(logs, ...)` - Offline prediction from logs
- `RobustAPI(api_name, online=False).certify(logs, ...)` - Offline certification from logs

Sources: [README.md:25-35]()

## System Integration Points

The components integrate through several key interfaces:

1. **Model Loading**: `architectures.py` provides factory functions for instantiating classifiers and denoisers
2. **Checkpoint Management**: Training scripts save models to `pretrained_models/` directory structure
3. **Certification Pipeline**: `certify.py` loads both classifiers and denoisers to compute robustness certificates
4. **Result Aggregation**: Analysis scripts read from standardized `data/` directory structure containing certification logs

This modular design enables independent development and testing of each component while maintaining clear data flow and integration points throughout the system.

Sources: [README.md:69-83](), [README.md:92-124]()

---

