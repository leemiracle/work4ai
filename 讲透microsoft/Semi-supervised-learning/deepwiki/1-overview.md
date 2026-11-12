<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Semi-supervised-learning · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGE_LOG.md](CHANGE_LOG.md)
- [README.md](README.md)
- [docs/algorithm_zoo.md](docs/algorithm_zoo.md)
- [docs/benchmark.md](docs/benchmark.md)
- [docs/contributors.md](docs/contributors.md)
- [docs/tutorial.md](docs/tutorial.md)
- [semilearn/algorithms/defixmatch/defixmatch.py](semilearn/algorithms/defixmatch/defixmatch.py)
- [semilearn/core/hooks/aim.py](semilearn/core/hooks/aim.py)
- [semilearn/datasets/audio_datasets/datasetbase.py](semilearn/datasets/audio_datasets/datasetbase.py)

</details>



This document provides an introduction to USB (Unified Semi-supervised Learning Benchmark), a comprehensive framework for semi-supervised learning research and applications across multiple domains. This overview explains the purpose, key features, and high-level architecture of the USB framework.

USB is a PyTorch-based framework that offers implementations of various semi-supervised learning (SSL) algorithms with support for computer vision (CV), natural language processing (NLP), and audio tasks. It is designed to be easy to use, extensible, and affordable for research groups of all sizes.

For detailed installation instructions, see [Installation and Setup](#1.1). For a deeper examination of the system architecture, refer to [System Architecture](#1.2).

## Purpose and Goals

USB aims to provide a unified benchmark for semi-supervised learning that:

1. Standardizes the implementation and evaluation of SSL algorithms
2. Supports multiple domains (CV, NLP, and audio) with a consistent interface
3. Enables fair comparisons between different SSL approaches
4. Offers a flexible framework for developing new SSL algorithms
5. Provides reproducible benchmarks for the research community

## High-Level Architecture

The USB framework consists of several interconnected components organized around a core architecture that supports multiple algorithms, datasets, and training methods.

### System Overview Diagram

```mermaid
graph TD
    subgraph "Core Components"
        AB["AlgorithmBase"] --> Model["Neural Network Models"]
        AB --> Hooks["Hooks System"]
        AB --> Dataset["Dataset Management"]
        
        subgraph "Neural Networks"
            Model --> CV["Vision Models (ViT, ResNet)"]
            Model --> NLP["Text Models (BERT)"]
            Model --> Audio["Audio Models (Wave2vec, Hubert)"]
        end
        
        subgraph "Hook System"
            Hooks --> HK1["Parameter Hooks"]
            Hooks --> HK2["Monitoring Hooks"]
            Hooks --> HK3["Algorithm-Specific Hooks"]
        end
        
        subgraph "Data Management"
            Dataset --> DL["Data Loaders"]
            Dataset --> Split["SSL Data Splitting"]
            Dataset --> Aug["Data Augmentation"]
        end
    end
    
    subgraph "Entry Points"
        Train["train.py"] --> AB
        Eval["eval.py"] --> AB
        Config["Configuration Files"] --> Train
    end
    
    subgraph "Algorithms"
        AlgoRegistry["Algorithm Registry"] --> SSLAlgos["SSL Algorithms"]
        AlgoRegistry --> ImbalancedAlgos["Imbalanced Algorithms"]
        AB --> AlgoRegistry
    end
```

Sources: [README.md:112-118](), [semilearn/algorithms/defixmatch/defixmatch.py:11-14]()

### Algorithm Hierarchy

USB implements numerous SSL algorithms that all inherit from a common `AlgorithmBase` class, which provides the foundation for implementing SSL techniques.

```mermaid
classDiagram
    AlgorithmBase <|-- FixMatch
    AlgorithmBase <|-- UDA
    AlgorithmBase <|-- FlexMatch
    AlgorithmBase <|-- MeanTeacher
    AlgorithmBase <|-- PiModel
    AlgorithmBase <|-- VAT
    AlgorithmBase <|-- DeFixMatch
    AlgorithmBase <|-- FreeMatch
    AlgorithmBase <|-- SoftMatch
    AlgorithmBase <|-- ImbAlgorithmBase
    ImbAlgorithmBase <|-- CREST
    ImbAlgorithmBase <|-- ABC
    
    class AlgorithmBase {
        +train_step()
        +set_hooks()
        +evaluate()
        +load_model()
        +save_model()
    }
    
    class ImbAlgorithmBase {
        +imb_init()
    }
```

Sources: [docs/algorithm_zoo.md:1-21]()

## Key Features

USB offers several key features that make it a valuable tool for SSL research and applications:

| Feature | Description |
|---------|-------------|
| Multiple Domains | Supports CV, NLP, and audio tasks with a unified API |
| Algorithm Library | Implements 15+ SSL algorithms including FixMatch, UDA, MeanTeacher, etc. |
| Extensibility | Plugin architecture with hooks for customizing algorithm behavior |
| Benchmarking | Standardized evaluation across datasets and algorithms |
| Experiment Tracking | Integration with wandb, Aim, and other logging tools |
| Reproducibility | Configuration-based experiment setup for reproducible results |

Sources: [README.md:113-115](), [CHANGE_LOG.md:14-21]()

## Data Processing Pipeline

The USB framework handles data through a standardized pipeline that prepares it for semi-supervised learning:

```mermaid
flowchart TB
    RawData["Raw Data"] --> GetDataset["get_dataset()"]
    GetDataset --> Split["split_ssl_data()"]
    
    subgraph "SSL Data Splitting"
        Split --> LabeledData["Labeled Data (small)"]
        Split --> UnlabeledData["Unlabeled Data (large)"]
        Split --> EvalData["Evaluation Data"]
    end
    
    LabeledData --> BasicDataset1["BasicDataset(is_ulb=False)"]
    UnlabeledData --> BasicDataset2["BasicDataset(is_ulb=True)"]
    EvalData --> BasicDataset3["BasicDataset(is_ulb=False)"]
    
    subgraph "Data Loading"
        BasicDataset1 --> LBLoader["Labeled Batch Loader"]
        BasicDataset2 --> ULBLoader["Unlabeled Batch Loader"]
        BasicDataset3 --> EvalLoader["Evaluation Loader"]
    end
    
    subgraph "Algorithm Training"
        LBLoader --> TrainStep["algorithm.train_step()"]
        ULBLoader --> TrainStep
    end
    
    EvalLoader --> Eval["algorithm.evaluate()"]
```

Sources: [semilearn/datasets/audio_datasets/datasetbase.py:45-135](), [docs/tutorial.md:72-82]()

## Hooks System

One of the unique aspects of USB is its hook system, which allows for customization of algorithm behavior at various points in the training process:

```mermaid
graph LR
    subgraph "Hook Registration System"
        Train["train.py"] --> Algorithm["AlgorithmBase"]
        Algorithm --> RegisterHook["register_hook()"]
        RegisterHook --> HooksDict["Hooks Dictionary"]
        
        HooksDict --> A["Parameter Hooks"]
        HooksDict --> B["Monitoring Hooks"]
        HooksDict --> C["Algorithm-Specific Hooks"]
        
        A --> A1["EMAHook"]
        A --> A2["ParamUpdateHook"]
        
        B --> B1["LoggingHook"]
        B --> B2["WANDBHook"]
        B --> B3["AimHook"]
        
        C --> C1["PseudoLabelingHook"]
        C --> C2["MaskingHook"]
        C --> C3["DistAlignHook"]
    end
    
    subgraph "Hook Execution"
        TrainStep["train_step()"] --> CallHook["call_hook()"]
        CallHook --> H1["before_train_step"]
        CallHook --> H2["after_train_step"]
    end
```

Sources: [semilearn/algorithms/defixmatch/defixmatch.py:43-46](), [semilearn/core/hooks/aim.py:9-49]()

## Supported Algorithms

USB implements numerous semi-supervised learning algorithms, including:

1. **Consistency-based methods**:
   - PiModel - Forces outputs of perturbed versions of data to be similar
   - MeanTeacher - Uses exponential moving average of model weights
   - VAT - Virtual Adversarial Training for robustness

2. **Pseudo-labeling methods**:
   - FixMatch - Uses weak augmentations for pseudo-label generation and strong augmentations for learning
   - FlexMatch - Dynamic class-specific thresholds for pseudo-labeling
   - DeFixMatch - Debiased version of FixMatch
   - SoftMatch - Addresses quantity-quality tradeoff in pseudo-labeling

3. **Contrastive methods**:
   - CoMatch - Combines consistency regularization and contrastive learning
   - SimMatch - Extends CoMatch with semantic and instance-level consistency

4. **Imbalanced learning methods**:
   - Various algorithms for handling class imbalance in SSL settings

Sources: [docs/algorithm_zoo.md:4-20]()

## Supported Datasets

USB provides support for datasets across three domains:

1. **Computer Vision**:
   - CIFAR-100, STL10, TissueMNIST, SemiAves, EuroSAT, ImageNet

2. **Natural Language Processing**:
   - IMDB, Amazon Review, Yelp Review, AG News, Yahoo! Answer

3. **Audio**:
   - GTZAN, UrbanSound8k, FSDNoisy18k, Keyword Spotting, ESC-50

Sources: [docs/benchmark.md:1-42]()

## Training Process Flow

The standard training process in USB follows this general flow:

```mermaid
flowchart TD
    Start([Start]) --> LoadConfig["Load Configuration"]
    LoadConfig --> CreateModel["Initialize Model"]
    CreateModel --> CreateAlgorithm["Create Algorithm"]
    CreateAlgorithm --> LoadData["Load Datasets"]
    LoadData --> SetHooks["Set Algorithm Hooks"]
    SetHooks --> StartTraining["Start Training"]
    
    subgraph "Training Loop"
        StartTraining --> FetchBatches["Fetch Labeled & Unlabeled Batches"]
        FetchBatches --> BeforeStep["Call before_train_step Hooks"]
        BeforeStep --> TrainStep["Execute algorithm.train_step()"]
        TrainStep --> AfterStep["Call after_train_step Hooks"]
        AfterStep --> EvalCheck{"Evaluation Iteration?"}
        EvalCheck -->|Yes| Evaluate["Evaluate Model"]
        EvalCheck -->|No| NextIter["Next Iteration"]
        Evaluate --> NextIter
        NextIter --> |Loop Until Done| FetchBatches
    end
    
    StartTraining --> SaveModel["Save Best Model"]
    SaveModel --> FinalEval["Final Evaluation"]
    FinalEval --> End([End])
```

Sources: [README.md:147-150](), [docs/tutorial.md:86-90]()

## Summary

USB provides a comprehensive framework for semi-supervised learning research and application across multiple domains. Its modular design, extensible architecture, and rich algorithm library make it a valuable tool for both exploring existing SSL techniques and developing new approaches. The framework's standardized benchmarking capabilities enable fair comparisons between different methods, contributing to the advancement of the field.

In the following sections of the documentation, we will dive deeper into the individual components of the USB framework, explaining how to use them effectively and how to extend the framework with custom algorithms and datasets.

---

