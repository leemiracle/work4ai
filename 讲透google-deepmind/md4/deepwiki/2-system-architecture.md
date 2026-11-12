<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/md4 · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [md4/__init__.py](md4/__init__.py)

</details>



This document provides an overview of the MD4 (Masked Diffusion for Discrete Data) system architecture, explaining the key components and their interactions. It covers the high-level architecture design, core components, data flow, and how the different subsystems work together to implement the masked diffusion approach for discrete data types. For specific model variants and their differences, see [Model Variants](#2.1).

## High-Level System Architecture

The MD4 system consists of several interrelated components that work together to train diffusion models on discrete data such as text and images.

```mermaid
flowchart TD
    subgraph "Initialization & Configuration"
        Main["main.py - Entry Point"]
        Config["Configuration System"]
        Main --> Config
    end
    
    subgraph "Data Processing"
        InputPipeline["input_pipeline.py"]
        TextProcessing["Text Processing"]
        ImageProcessing["Image Processing"]
        
        InputPipeline --> TextProcessing
        InputPipeline --> ImageProcessing
    end
    
    subgraph "Model Architecture"
        CoreModel["md4_model.py"]
        Transformer["Transformer Layers"]
        Diffusion["Diffusion Process"]
        
        CoreModel --> Transformer
        CoreModel --> Diffusion
    end
    
    subgraph "Training & Inference"
        Train["Training Loop"]
        Sample["Sampling Methods"]
        BinarySearch["binary_search.py"]
        
        Train --> Sample
        Sample --> BinarySearch
    end
    
    Config --> InputPipeline
    Config --> CoreModel
    Config --> Train
    
    InputPipeline --> CoreModel
    CoreModel --> Train
```

Sources: README.md

## Core Components

### Configuration System

The configuration system defines the model parameters, training settings, and dataset-specific configurations. The system supports several pre-defined configurations for both text and image datasets.

```mermaid
flowchart TD
    subgraph "Configuration Hierarchy"
        ConfigRoot["Configuration System"]
        
        MD4["MD4 Configs"]
        GenMD4["GenMD4 Configs"]
        
        ConfigRoot --> MD4
        ConfigRoot --> GenMD4
        
        MD4 --> Text["Text Configs<br>(openwebtext.py, text8.py, fineweb_edu.py)"]
        MD4 --> Image["Image Configs<br>(cifar10.py, imagenet64.py)"]
        GenMD4 --> GenText["Text Configs<br>(openwebtext.py, text8.py)"]
    end
    
    subgraph "Parameter Categories"
        ModelParams["Model Parameters"]
        DiffusionParams["Diffusion Parameters"]
        TrainingParams["Training Parameters"]
        SamplingParams["Sampling Parameters"]
        
        Text & Image & GenText -.-> ModelParams & DiffusionParams & TrainingParams & SamplingParams
    end
```

Sources: README.md

### Input Pipeline

The input pipeline handles data loading, preprocessing, and batching for both text and image datasets. It supports multiple datasets including OpenWebText, Text8, and FineWeb-EDU for text, and CIFAR-10 and ImageNet-64 for images.

```mermaid
flowchart TD
    subgraph "Input Pipeline Structure"
        InputPipeline["input_pipeline.py"]
        
        TextDatasets["Text Datasets"]
        ImageDatasets["Image Datasets"]
        
        InputPipeline --> TextDatasets
        InputPipeline --> ImageDatasets
        
        TextDatasets --> OpenWebText["OpenWebText<br>(50257 vocab size)"]
        TextDatasets --> Text8["Text8<br>(27 vocab size)"]
        TextDatasets --> FinewebEDU["Fineweb-EDU<br>(50257 vocab size)"]
        
        ImageDatasets --> CIFAR10["CIFAR-10<br>(32x32x3)"]
        ImageDatasets --> ImageNet64["ImageNet-64<br>(64x64x3)"]
    end
    
    subgraph "Processing Steps"
        Tokenization["Tokenization (Text)"]
        Discretization["Discretization (Images)"]
        Batching["Batching"]
        
        OpenWebText & Text8 & FinewebEDU --> Tokenization --> Batching
        CIFAR10 & ImageNet64 --> Discretization --> Batching
    end
```

Sources: README.md

### Model Architecture

The MD4 model architecture is based on transformer layers with a diffusion process applied to discrete data. The architecture is designed to be flexible and can be applied to both text and image modalities.

```mermaid
flowchart TD
    subgraph "Model Components"
        CoreModel["md4_model.py"]
        
        TransformerBlock["Transformer Blocks"]
        TokenEmbedding["Token Embedding"]
        TimeEmbedding["Time Embedding"]
        DiffusionProcess["Diffusion Process"]
        
        CoreModel --> TokenEmbedding
        CoreModel --> TimeEmbedding
        CoreModel --> TransformerBlock
        CoreModel --> DiffusionProcess
        
        TransformerBlock --> SelfAttention["Self-Attention Layer"]
        TransformerBlock --> FeedForward["Feed Forward Layer"]
        TransformerBlock --> LayerNorm["Layer Normalization"]
    end
    
    subgraph "Diffusion Components"
        ForwardProcess["Forward Process<br>(Adding Noise)"]
        ReverseProcess["Reverse Process<br>(Denoising)"]
        
        DiffusionProcess --> ForwardProcess
        DiffusionProcess --> ReverseProcess
    end
```

Sources: README.md

### Training and Sampling System

The training process includes forward diffusion, loss calculation, and optimization. The sampling system supports various generation strategies including ancestral sampling, mean-based sampling, and top-p (nucleus) sampling.

```mermaid
flowchart LR
    subgraph "Training Process"
        Input["Input Data"]
        NoiseAddition["Noise Addition"]
        ModelPrediction["Model Prediction"]
        LossCalc["Loss Calculation"]
        Optimizer["Optimizer (Adam)"]
        
        Input --> NoiseAddition
        NoiseAddition --> ModelPrediction
        ModelPrediction --> LossCalc
        LossCalc --> Optimizer
        Optimizer -->|Update Weights| ModelPrediction
    end
    
    subgraph "Sampling Process"
        NoisySample["Random Noise"]
        StepDenoising["Step-by-Step Denoising"]
        SamplingMethod["Sampling Method"]
        Output["Generated Output"]
        
        NoisySample --> StepDenoising
        StepDenoising --> SamplingMethod
        SamplingMethod --> Output
        
        SamplingMethod --> Ancestral["Ancestral Sampling"]
        SamplingMethod --> MeanBased["Mean-Based Sampling"]
        SamplingMethod --> TopP["Top-p Sampling"]
        
        TopP --> BinarySearch["binary_search.py"]
    end
```

Sources: README.md

## Data Flow and Component Interactions

This diagram illustrates how data flows through the MD4 system during training and generation:

```mermaid
sequenceDiagram
    participant Config as Configuration
    participant Data as Data Pipeline
    participant Model as MD4 Model
    participant Train as Training Loop
    participant Sample as Sampling System
    
    Config->>Data: Configure dataset & preprocessing
    Config->>Model: Set model architecture parameters
    Config->>Train: Set training parameters
    Config->>Sample: Set sampling parameters
    
    Note over Data,Model: Training Flow
    Data->>Model: Provide batched data
    Model->>Model: Add noise (forward diffusion)
    Model->>Train: Output predictions
    Train->>Model: Update weights
    
    Note over Model,Sample: Generation Flow
    Sample->>Model: Initialize with random noise
    loop For each diffusion timestep
        Model->>Model: Predict denoised state
        Model->>Sample: Output intermediate prediction
        Sample->>Model: Apply sampling strategy
    end
    Sample->>Sample: Return final generated output
```

Sources: README.md

## Hardware and Deployment Requirements

The MD4 system supports different hardware accelerators for training and inference:

| Hardware | Supported | Batch Size (MD4-S, seq_len=1024) | Notes |
|----------|-----------|----------------------------------|-------|
| GPU (A100) | Yes | Up to 128 | Using 8x A100 GPUs |
| TPU (v5litepod) | Yes | Up to 32 | Using 8x v5litepod chips |

The system is designed to scale based on available hardware resources. Batch sizes need to be adjusted according to the compute resources available. For optimal performance:

1. For GPU deployments: Use `requirements_gpu.txt` for dependencies
2. For TPU deployments: Use `requirements_tpu.txt` for dependencies

```mermaid
flowchart LR
    subgraph "Deployment Options"
        Setup["Setup Environment"]
        
        Setup --> GPU["GPU Deployment"]
        Setup --> TPU["TPU Deployment"]
        
        GPU --> GPUReq["requirements_gpu.txt"]
        TPU --> TPUReq["requirements_tpu.txt"]
        
        GPUReq --> Train["Training"]
        TPUReq --> Train
        
        Train --> Config["Configuration Selection"]
        Config --> TextConfig["Text Config<br>(openwebtext.py, etc.)"]
        Config --> ImageConfig["Image Config<br>(cifar10.py, etc.)"]
    end
```

Sources: README.md

## System Integration

The following diagram shows how all components of the MD4 system integrate together, from configuration to output generation:

```mermaid
flowchart TD
    Main["main.py<br>Entry Point"] --> Config["Configuration"]
    
    Config --> ModelConfig["Model Configuration"]
    Config --> DataConfig["Data Configuration"]
    Config --> TrainConfig["Training Configuration"]
    Config --> SampleConfig["Sampling Configuration"]
    
    DataConfig --> InputPipeline["input_pipeline.py"]
    InputPipeline --> Batches["Batched Data"]
    
    ModelConfig --> ModelInit["Model Initialization"]
    ModelInit --> Transformer["Transformer Architecture"]
    
    Batches --> TrainingLoop["Training Loop"]
    Transformer --> TrainingLoop
    TrainConfig --> TrainingLoop
    
    TrainingLoop --> TrainedModel["Trained Model"]
    
    TrainedModel --> SamplingLoop["Sampling Loop"]
    SampleConfig --> SamplingLoop
    
    SamplingLoop --> BinarySearch["binary_search.py<br>(for top-k/top-p)"]
    SamplingLoop --> GeneratedOutput["Generated Output<br>(Text or Images)"]
```

Sources: README.md

## Summary

The MD4 system implements a masked diffusion approach for discrete data types. The architecture is designed to be flexible, supporting various datasets and model configurations. Key architectural components include:

1. **Configuration System**: Provides dataset-specific and model-specific parameters
2. **Input Pipeline**: Handles data loading and preprocessing for text and image datasets
3. **Model Architecture**: Based on transformer layers with diffusion process
4. **Training System**: Implements the forward diffusion process and optimization
5. **Sampling System**: Supports various generation strategies with efficient implementations

This modular design allows for easy experimentation with different datasets, model sizes, and sampling strategies. For specific model variants and their differences, see [Model Variants](#2.1), and for detailed configuration options, see [Configuration System](#3).

---

