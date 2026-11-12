<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/denoised-smoothing · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document provides an overview of the Microsoft denoised-smoothing repository, which implements a provable defense method for protecting pretrained image classifiers against adversarial attacks. The system combines denoising preprocessing with randomized smoothing to provide certified L2-robustness guarantees for any pretrained classifier without requiring retraining.

This overview covers the core methodology, system architecture, and primary code components. For detailed information about the theoretical foundations, see [Denoised Smoothing Methodology](#1.1). For implementation details of specific subsystems, see [System Components](#2). For experimental results and performance analysis, see [Experimental Results](#3).

## Core Methodology

Denoised smoothing enhances the certified robustness of pretrained classifiers through a two-stage process: denoising followed by randomized smoothing. The methodology converts any pretrained classifier into a provably robust version by preprocessing inputs through a trained denoiser before applying Monte Carlo sampling with Gaussian noise to compute certified L2-radii.

### System Architecture Overview

```mermaid
graph TB
    subgraph "Input Processing"
        A["Input Image"] --> B["Optional Denoiser"]
        B --> C["Pretrained Classifier"]
    end
    
    subgraph "Core Components"
        D["train_classifier.py"] --> E["Trained Classifiers"]
        F["train_denoiser.py"] --> G["Trained Denoisers"]
        H["architectures.py"] --> D
        H --> F
    end
    
    subgraph "Certification Pipeline"
        I["certify.py"] --> J["Certified L2-Radius"]
        E --> I
        G --> I
        K["Cohen et al. Algorithm"] --> I
        L["Gaussian Noise σ"] --> I
    end
    
    subgraph "Evaluation & Analysis"
        M["test_denoiser.py"] --> N["Performance Metrics"]
        O["analyze.py"] --> P["LaTeX Tables"]
        O --> Q["Result Plots"]
    end
    
    subgraph "Vision API Integration"
        R["RobustAPI Class"] --> S["Cloud API Robustification"]
        G --> R
    end
    
    E --> M
    G --> M
    J --> O
    N --> O
```

**System Architecture Overview**
This diagram shows the primary workflow from input processing through certification to analysis, highlighting the key Python scripts and their relationships.

Sources: [README.md:21-49]()

### Code Component Mapping

```mermaid
graph LR
    subgraph "Training Scripts"
        A["train_classifier.py"] --> B["ResNet110_90epochs"]
        C["train_denoiser.py"] --> D["cifar_dncnn"]
        E["train_denoiser_multi_classifier.py"] --> F["Multi-Surrogate Models"]
    end
    
    subgraph "Architecture Definitions"
        G["architectures.py"] --> H["get_architecture()"]
        H --> I["Classifier Architectures"]
        H --> J["Denoiser Architectures"]
    end
    
    subgraph "Certification Engine"
        K["certify.py"] --> L["Smooth.certify()"]
        K --> M["predict()"]
        N["core.Smooth"] --> K
    end
    
    subgraph "Testing & Evaluation"
        O["test_denoiser.py"] --> P["test_classifier_with_denoiser()"]
        O --> Q["test_denoiser_on_dataset()"]
    end
    
    subgraph "Vision API System"
        R["vision_api/robust_api.py"] --> S["RobustAPI.predict()"]
        R --> T["RobustAPI.certify()"]
        U["vision_api/query_api.py"] --> V["query_azure()"]
        U --> W["query_google()"]
    end
    
    A --> G
    C --> G
    B --> K
    D --> K
```

**Code Component to Functionality Mapping**
This diagram maps specific Python files and classes to their primary functions, showing how code entities implement the denoised smoothing methodology.

Sources: [README.md:40-49]()

## Key Workflows

### Training Workflow

The system supports training both classifiers and denoisers independently:

1. **Classifier Training**: `train_classifier.py` trains standard or Gaussian-augmented classifiers on CIFAR-10 or ImageNet datasets
2. **Denoiser Training**: `train_denoiser.py` trains denoising models using MSE or adversarial objectives to handle Gaussian noise
3. **Architecture Selection**: `architectures.py` provides a unified interface for specifying model architectures

### Certification Workflow  

The certification process combines trained components to provide robustness guarantees:

1. **Input**: Pretrained classifier and optional denoiser
2. **Processing**: `certify.py` applies randomized smoothing with specified noise level σ
3. **Output**: Certified L2-radius for each test sample using Cohen et al. algorithm

### Vision API Integration

The `RobustAPI` class enables robustification of commercial vision APIs:

```python
# Online API robustification
majority_class, radius, logs = RobustAPI(api_name, denoiser=denoiser, online=True).certify(img, ...)

# Offline log analysis  
majority_class, radius = RobustAPI(api_name, online=False).certify(logs, ...)
```

Sources: [README.md:27-35]()

## Repository Structure

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `code/` | Core implementation | `train_classifier.py`, `train_denoiser.py`, `certify.py` |
| `vision_api/` | Cloud API integration | `robust_api.py`, `query_api.py` |
| `analysis/` | Result processing | `analyze.py`, plotting scripts |
| `pretrained_models/` | Trained models | Classifiers and denoisers for CIFAR-10/ImageNet |
| `data/` | Certification logs | Experimental results and performance data |

Sources: [README.md:21-38]()

## Usage Examples

### Basic Certification Example

```bash
# Certify CIFAR-10 model with MSE-trained denoiser
pretrained_classifier="pretrained_models/cifar10_classifiers/ResNet110_90epochs/noise_0.00/checkpoint.pth.tar"
denoiser="pretrained_models/trained_denoisers/cifar10/mse_obj/dncnn/epochs_90/noise_0.25/checkpoint.pth.tar"
python code/certify.py --dataset cifar10 --base_classifier $pretrained_classifier --sigma 0.25 --outfile certification_output/sigma_0.25 --denoiser $denoiser
```

### Training Custom Denoiser

```bash
# Train denoiser for noise level 0.25
python code/train_denoiser.py --dataset cifar10 --arch cifar_dncnn --outdir denoiser_output_dir --noise 0.25
```

Sources: [README.md:73-79](), [README.md:96-104]()

This overview establishes the foundation for understanding the denoised-smoothing system. The following sections provide detailed documentation of each subsystem and comprehensive experimental results.

---

