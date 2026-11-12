<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/jeo · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [jeo/__init__.py](jeo/__init__.py)

</details>



## Purpose and Scope

This document provides a high-level introduction to the Jeo repository, a JAX-based machine learning framework specifically designed for geospatial remote sensing and Earth Observation applications. Jeo enables researchers and practitioners to train and deploy ML models on satellite imagery and other geospatial data using modern distributed computing frameworks.

This overview covers the framework's core architecture, key dependencies, and integration patterns. For detailed installation and setup instructions, see [Getting Started](#2). For in-depth technical documentation of specific components, see [Core Architecture](#3) and its subsections.

Sources: [README.md:1-126](), [jeo/__init__.py:1-15]()

## Core Design Philosophy

Jeo is built around several key design principles that make it effective for geospatial ML workflows:

| Design Principle | Implementation | Benefits |
|------------------|----------------|----------|
| **JAX-First** | Built on JAX/Flax for computation | Hardware-agnostic execution (CPU/GPU/TPU) |
| **Scalable Data** | TensorFlow Datasets integration | Reproducible, version-controlled datasets |
| **Geospatial Focus** | GeeFlow integration for Earth Engine | Direct access to petabyte-scale satellite data |
| **Modular Architecture** | Component-based system design | Easy customization and extension |
| **Research-Ready** | Configuration-driven experiments | Rapid prototyping and reproducible research |

The framework has been successfully used in multiple research publications focusing on deforestation monitoring, forest classification, and global environmental analysis.

Sources: [README.md:10-25](), [README.md:31-54]()

## High-Level System Architecture

```mermaid
graph TB
    subgraph "External Dependencies"
        JAX["JAX/Flax<br/>jax.numpy, flax.linen"]
        TFDS["TensorFlow Datasets<br/>tensorflow_datasets"]
        GeeFlow["GeeFlow<br/>geeflow"]
        GEE["Google Earth Engine<br/>earthengine-api"]
    end
    
    subgraph "Jeo Core Framework"
        TrainScript["jeo.train<br/>Main Training Entry Point"]
        InputPipeline["jeo.input_pipeline<br/>Data Loading & Processing"]
        Models["Model Implementations<br/>jeo.models.*"]
        TaskSystem["Task Framework<br/>jeo.task_builder"]
        ConfigSystem["Configuration<br/>jeo.config_utils"]
    end
    
    subgraph "Data Processing Pipeline"
        PPBuilder["jeo.pp_builder<br/>Preprocessing Registry"]
        PPOps["Preprocessing Operations<br/>jeo.pp_ops, jeo.image_ops"]
        DataTransform["Data Transformation<br/>Applied Operations"]
    end
    
    subgraph "Training Infrastructure"
        TrainUtils["jeo.train_utils<br/>Checkpointing & Utilities"]
        Losses["jeo.losses<br/>Loss Functions"]
        Evaluators["jeo.evaluators<br/>Performance Assessment"]
        Metrics["jeo.clu_metrics<br/>Metrics Collection"]
    end
    
    %% External connections
    GeeFlow --> GEE
    TFDS --> InputPipeline
    GeeFlow --> InputPipeline
    JAX --> Models
    JAX --> TrainScript
    
    %% Core framework connections
    ConfigSystem --> TrainScript
    TrainScript --> InputPipeline
    TrainScript --> Models
    TrainScript --> TaskSystem
    
    %% Data processing flow
    InputPipeline --> PPBuilder
    PPBuilder --> PPOps
    PPOps --> DataTransform
    DataTransform --> Models
    
    %% Training flow
    TrainScript --> TrainUtils
    TrainScript --> Losses
    TrainScript --> Evaluators
    Metrics --> Evaluators
    TaskSystem --> Losses
```

Sources: [README.md:10-18](), [README.md:22-25]()

## Core Components

### Training System
The `jeo.train` module serves as the main entry point for all training workflows. It orchestrates the interaction between data loading, model initialization, training loops, and evaluation cycles. The system supports distributed training across multiple devices and provides comprehensive checkpointing capabilities.

### Data Pipeline
Jeo's data pipeline is built around TensorFlow Datasets (`tensorflow_datasets`) for standardized dataset access, with specialized support for geospatial data through GeeFlow integration. The `jeo.input_pipeline` module handles data loading, while the preprocessing system (`jeo.pp_builder`, `jeo.pp_ops`) provides extensible data transformation capabilities.

### Model Architecture Framework
The framework supports multiple model architectures optimized for different geospatial tasks:
- **BIT (Big Transfer)**: ResNetV1-based convolutional networks with GroupNorm
- **ViT (Vision Transformer)**: Standard vision transformer architecture
- **MTSViT**: Multi-Modal Temporal-Spatial Vision Transformers for time-series analysis

### Task Abstraction
The `jeo.task_builder` provides a unified interface for defining different ML tasks (classification, segmentation, regression) with task-specific loss functions and evaluation metrics.

Sources: [README.md:83-89]()

## Integration with Geospatial Ecosystem

```mermaid
graph LR
    subgraph "Data Sources"
        GEE["Google Earth Engine<br/>Satellite Imagery API"]
        TFDS_Catalog["TensorFlow Datasets<br/>Standard ML Datasets"]
        CustomData["Custom Datasets<br/>User-provided Data"]
    end
    
    subgraph "Data Processing"
        GeeFlow_Pipeline["GeeFlow<br/>geeflow.preprocess"]
        TFDS_Pipeline["TFDS Pipeline<br/>tensorflow_datasets.load"]
        JeoInputPipeline["jeo.input_pipeline<br/>get_data()"]
    end
    
    subgraph "Jeo Training"
        JeoTrain["jeo.train<br/>Training Loop"]
        Models["jeo.models<br/>BIT, ViT, MTSViT"]
        Evaluation["jeo.evaluators<br/>Task-specific Metrics"]
    end
    
    subgraph "Outputs"
        Checkpoints["Model Checkpoints<br/>.pkl files"]
        Metrics_Output["Training Metrics<br/>Performance Logs"]
        Predictions["Model Predictions<br/>Inference Results"]
    end
    
    %% Data flow
    GEE --> GeeFlow_Pipeline
    TFDS_Catalog --> TFDS_Pipeline
    CustomData --> JeoInputPipeline
    
    GeeFlow_Pipeline --> JeoInputPipeline
    TFDS_Pipeline --> JeoInputPipeline
    
    JeoInputPipeline --> JeoTrain
    JeoTrain --> Models
    JeoTrain --> Evaluation
    
    Models --> Checkpoints
    Evaluation --> Metrics_Output
    Models --> Predictions
```

The integration pattern shown above demonstrates how Jeo serves as a bridge between large-scale geospatial data sources and modern ML training infrastructure. GeeFlow handles the complexity of interfacing with Google Earth Engine's API, while Jeo provides the ML training and evaluation framework.

Sources: [README.md:22-29]()

## Quick Start Example

The simplest way to understand Jeo's operation is through the provided demo configuration:

```bash
python -m jeo.train --config configs/tests/tiny_bit.py:runlocal \
--workdir /tmp/jeo/demo_tiny_bit
```

This command demonstrates the key components in action:
- `jeo.train`: Main training module
- `configs/tests/tiny_bit.py`: Configuration file defining model, data, and training parameters
- `:runlocal`: Configuration modifier for local CPU execution
- `--workdir`: Directory for checkpoints and output artifacts

The example trains a BIT model on CIFAR-10 data, showcasing the framework's ability to work with both standard ML datasets and geospatial data using the same unified interface.

Sources: [README.md:74-92]()

## Hardware and Deployment Support

Jeo is designed to run efficiently across different computing environments:

| Environment | Support Level | Key Features |
|-------------|---------------|--------------|
| **Local CPU** | Full support | Development and small-scale experiments |
| **GPU** | Full support | Accelerated training with CUDA |
| **Google Cloud TPU VMs** | Full support | Large-scale distributed training |
| **Multi-device** | Native support | Automatic sharding and parallelization |

The JAX foundation provides automatic device placement and distributed computing capabilities, making it straightforward to scale from laptop development to cloud-scale training without code changes.

Sources: [README.md:16-18]()

---

