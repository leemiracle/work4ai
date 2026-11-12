<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/XPretrain · page 4 Development Guide · fetched 2026-10-26 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LF-VILA/docker/Dockerfile](LF-VILA/docker/Dockerfile)
- [LF-VILA/docker/requirements.txt](LF-VILA/docker/requirements.txt)

</details>



This document provides comprehensive guidance for developers working with XPretrain components, covering environment setup, containerized development workflows, and configuration management across the video-language and image-language research tracks. 

For information about specific model architectures and training procedures, see [HD-VILA Model](#2.2), [LF-VILA Model](#2.3), and [CLIP-ViP Model](#2.4). For dataset preparation and processing details, see [HD-VILA-100M Dataset](#2.1) and [Data Processing](#4.2). For licensing and responsible AI considerations, see [Legal and Governance](#5).

## Development Environment Architecture

The XPretrain repository uses a containerized development approach with Docker to ensure consistent environments across different research components. The development stack is built around GPU-accelerated training with distributed computing capabilities.

## Development Stack Architecture

```mermaid
graph TB
    subgraph "Host System"
        A[nvidia-docker] --> B["CUDA 11.1.1 Runtime"]
        B --> C["GPU Hardware<br/>(Tensor Core Compatible)"]
    end
    
    subgraph "Container Environment"
        D["nvidia/cuda:11.1.1-devel-ubuntu18.04"] --> E["Python 3.8 Environment"]
        E --> F["PyTorch 1.10.0+cu111"]
        E --> G["Horovod Distributed Training"]
        E --> H["DeepSpeed 0.5.8"]
        F --> I["Model Training Framework"]
        G --> I
        H --> I
    end
    
    subgraph "ML Libraries"
        J["transformers==4.30.0"] --> I
        K["timm==0.4.12"] --> I
        L["einops==0.3.2"] --> I
        M["decord==0.6.0"] --> I
        N["mmcv-full==1.4.2"] --> I
    end
    
    subgraph "Storage & Data"
        O["Local Storage<br/>PATH_TO_STORAGE"] --> I
        P["Azure Blob Storage"] --> O
        Q["Video Processing<br/>FFmpeg"] --> I
    end
    
    A --> D
```

Sources: [LF-VILA/docker/Dockerfile:1-134](), [LF-VILA/docker/requirements.txt:1-10]()

## Container Setup Process

The containerized environment follows a multi-stage build process that establishes the complete development stack including distributed training capabilities and video processing tools.

## Docker Build Pipeline

```mermaid
graph TD
    subgraph "Base System Setup"
        A["FROM nvidia/cuda:11.1.1-devel-ubuntu18.04"] --> B["apt-get system packages<br/>build-essential, cmake, git"]
        B --> C["CUDA/cuDNN libraries<br/>libcudnn8, libnccl2"]
        C --> D["FFmpeg video processing<br/>libsm6, libxext6"]
    end
    
    subgraph "Communication Layer"
        D --> E["OpenMPI 3.0.0<br/>Distributed communication"]
        E --> F["OpenSSH configuration<br/>Container networking"]
    end
    
    subgraph "Python Environment"
        F --> G["Python 3.8 installation"]
        G --> H["pip package manager"]
        H --> I["PyTorch 1.10.0+cu111<br/>torchvision 0.11.0+cu111"]
    end
    
    subgraph "Training Frameworks"
        I --> J["Horovod build from source<br/>NCCL + PyTorch support"]
        J --> K["DeepSpeed 0.5.8<br/>Memory optimization"]
        K --> L["Apex mixed precision<br/>NVIDIA optimization"]
    end
    
    subgraph "ML Dependencies"
        L --> M["transformers, timm, einops<br/>Model components"]
        M --> N["decord, opencv-python<br/>Video processing"]
        N --> O["CLIP, mmcv-full<br/>Vision-language models"]
    end
```

Sources: [LF-VILA/docker/Dockerfile:24-134]()

## Core Dependencies and Versions

The development environment maintains specific version constraints to ensure reproducibility across distributed training scenarios.

| Component | Version | Purpose |
|-----------|---------|---------|
| `nvidia/cuda` | 11.1.1-devel-ubuntu18.04 | Base CUDA development environment |
| `python` | 3.8 | Core Python runtime |
| `torch` | 1.10.0+cu111 | PyTorch framework with CUDA 11.1 support |
| `torchvision` | 0.11.0+cu111 | Computer vision utilities |
| `deepspeed` | 0.5.8 | Memory-efficient distributed training |
| `transformers` | 4.30.0 | Hugging Face transformer models |
| `timm` | 0.4.12 | PyTorch image models library |
| `decord` | 0.6.0 | Efficient video loading |
| `mmcv-full` | 1.4.2 | OpenMMLab computer vision framework |

Sources: [LF-VILA/docker/Dockerfile:7-11](), [LF-VILA/docker/requirements.txt:2-10]()

## Distributed Training Configuration

The container environment includes comprehensive distributed training support through multiple communication backends and optimization frameworks.

## Training Infrastructure Components

```mermaid
graph LR
    subgraph "Communication Backends"
        A["OpenMPI 3.0.0"] --> D["Horovod"]
        B["NCCL 2.8.4"] --> D
        C["SSH networking"] --> D
    end
    
    subgraph "Optimization Frameworks"
        D --> E["DeepSpeed 0.5.8<br/>Memory optimization"]
        D --> F["Apex<br/>Mixed precision"]
        D --> G["PyTorch Lightning 1.2.9<br/>Training loops"]
    end
    
    subgraph "Model Components"
        E --> H["transformer models"]
        F --> H
        G --> H
        H --> I["Video-language training"]
        H --> J["Image-language training"]
    end
    
    subgraph "Data Pipeline"
        K["decord video loading"] --> I
        L["timm image models"] --> J
        M["FFmpeg processing"] --> K
        N["CLIP preprocessing"] --> L
    end
```

Sources: [LF-VILA/docker/Dockerfile:52-99](), [LF-VILA/docker/Dockerfile:108-121]()

## Environment Variables and Paths

The development environment expects specific configuration through environment variables and storage paths for data and model artifacts.

| Variable | Purpose | Example |
|----------|---------|---------|
| `CUDA_HOME` | CUDA installation path | `/usr/local/cuda` |
| `PATH_TO_STORAGE` | Local storage root | `/data/storage` |
| `HOROVOD_GPU_ALLREDUCE` | GPU communication backend | `NCCL` |
| `HOROVOD_NCCL_LINK` | NCCL linking mode | `SHARED` |
| `HOROVOD_WITH_PYTORCH` | PyTorch integration | `1` |

## Video Processing Dependencies

The container includes specialized video processing capabilities essential for video-language model development.

## Video Processing Pipeline

```mermaid
graph TB
    subgraph "System Libraries"
        A["FFmpeg<br/>Video codec support"] --> D["Video Processing Pipeline"]
        B["libsm6, libxext6<br/>GUI library support"] --> D
        C["OpenCV<br/>Computer vision ops"] --> D
    end
    
    subgraph "Python Video Libraries"
        E["decord==0.6.0<br/>Efficient video decoding"] --> D
        F["opencv-python<br/>Video manipulation"] --> D
        G["timm models<br/>Video feature extraction"] --> D
    end
    
    subgraph "Processing Capabilities"
        D --> H["Video frame extraction"]
        D --> I["Format conversion"]
        D --> J["Temporal sampling"]
        D --> K["Resolution scaling"]
    end
    
    subgraph "Model Integration"
        H --> L["HD-VILA preprocessing"]
        I --> M["LF-VILA long-form handling"]
        J --> N["CLIP-ViP adaptation"]
        K --> O["Feature extraction"]
    end
```

Sources: [LF-VILA/docker/Dockerfile:49-50](), [LF-VILA/docker/Dockerfile:119-120](), [LF-VILA/docker/requirements.txt:8]()

## Container Launch Workflow

The development workflow involves building the container with appropriate CUDA support and mounting storage volumes for data access.

## Development Container Workflow

```mermaid
graph TD
    subgraph "Container Build"
        A["docker build<br/>-f Dockerfile"] --> B["Base image pull<br/>nvidia/cuda:11.1.1-devel"]
        B --> C["System dependencies<br/>apt-get install"]
        C --> D["Python environment<br/>pip install"]
        D --> E["ML frameworks<br/>Horovod, DeepSpeed"]
    end
    
    subgraph "Container Launch"
        E --> F["nvidia-docker run<br/>--gpus all"]
        F --> G["Volume mounts<br/>-v PATH_TO_STORAGE"]
        G --> H["Environment variables<br/>CUDA_HOME, etc"]
        H --> I["SSH/MPI setup<br/>Distributed training"]
    end
    
    subgraph "Development Tasks"
        I --> J["Data preprocessing<br/>Video/text processing"]
        I --> K["Model training<br/>Multi-GPU distributed"]
        I --> L["Evaluation<br/>Downstream tasks"]
        I --> M["Checkpoint management<br/>Model artifacts"]
    end
```

Sources: [LF-VILA/docker/Dockerfile:1-134]()

## Configuration Management

The XPretrain components use JSON and YAML configuration files to manage model parameters, training settings, and data paths across different research tracks.

Configuration files typically specify:
- Model architecture parameters (`hidden_size`, `num_layers`, `attention_heads`)
- Training hyperparameters (`learning_rate`, `batch_size`, `epochs`)
- Data paths and preprocessing settings
- Distributed training configurations
- Evaluation and checkpoint settings

For specific configuration details for each model, refer to the individual model documentation: [HD-VILA Model](#2.2), [LF-VILA Model](#2.3), and [CLIP-ViP Model](#2.4).

## Development Prerequisites

Before beginning development with XPretrain components, ensure your system meets the following requirements:

| Requirement | Specification |
|-------------|---------------|
| GPU | NVIDIA GPU with Tensor Core support (V100, A100, RTX series) |
| CUDA | Version 11.1 or compatible |
| Docker | nvidia-docker2 runtime support |
| Storage | Sufficient space for datasets (TB-scale for video data) |
| Memory | 32GB+ RAM recommended for large-scale training |
| Network | High-bandwidth connection for distributed training |

Sources: [LF-VILA/docker/Dockerfile:1-11](), [LF-VILA/docker/requirements.txt:1-10]()

---

