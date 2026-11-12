<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/DreamCraft3D · page 1 Overview · fetched 2026-10-30 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



DreamCraft3D is a hierarchical 3D content generation system that produces high-fidelity, coherent 3D objects from a single 2D reference image and text prompt. This page provides an introduction to the system architecture, key components, and workflow. For detailed installation instructions, see [Installation and Setup](#1.1), and for a quick start guide, see [Quick Start Guide](#1.2).

## Introduction

DreamCraft3D addresses consistency challenges in 3D generation by employing a three-stage hierarchical approach that progressively refines both geometry and texture. The system's primary innovation is Bootstrapped Score Distillation, which creates a mutually reinforcing feedback loop between the optimized 3D scene and a personalized diffusion model to achieve exceptional texture quality and view consistency.

## System Architecture

The following diagram illustrates the high-level architecture of DreamCraft3D:

```mermaid
graph TD
    A["User Input"] --> |"2D Reference Image\n+ Text Prompt"| B["Preprocessing"]
    B --> C["Stage 1: Coarse Geometry"]
    C --> D["Stage 2: Geometry Refinement"]
    D --> E["Stage 3: Texture Refinement"]
    E --> F["Textured 3D Mesh"]
    
    subgraph "Preprocessing"
        B1["Background Removal"]
        B2["Depth Map Generation"]
        B3["Normal Map Generation"]
    end
    
    subgraph "Supporting Systems"
        S1["Prompt Processing"]
        S2["Image Processing"]
        S3["Pre-trained Models"]
    end
    
    S1 -.-> C
    S1 -.-> D
    S1 -.-> E
    S2 -.-> B
    S3 -.-> B
    S3 -.-> C
    S3 -.-> D
    S3 -.-> E
```

Sources: [README.md:5-19](), [README.md:26-29]()

## Three-Stage Pipeline

DreamCraft3D employs a hierarchical approach divided into three distinct stages, each building upon the previous:

```mermaid
flowchart LR
    A["Input Image"] --> B["Preprocessed Image"]
    B --> C["Stage 1: Coarse Geometry"]
    C --> D["Stage 2: Geometry Refinement"]
    D --> E["Stage 3: Texture Refinement"]
    E --> F["Final 3D Model"]
    
    subgraph "preprocess_image.py"
        PP1["Background Removal"]
        PP2["Depth Prediction"]
        PP3["Normal Prediction"]
    end
    
    subgraph "Stage 1"
        S1A["NeRF Training"]
        S1B["NeuS Training"]
        S1A --> S1B
    end
    
    subgraph "Stage 2"
        S2A["Score Distillation Sampling"]
        S2B["View-Dependent Diffusion"]
    end
    
    subgraph "Stage 3"
        S3A["Bootstrapped Score Distillation"]
        S3B["Personalized Dreambooth Model"]
        S3A <--> S3B
    end
```

Sources: [README.md:97-121]()

### Stage 1: Coarse Geometry Generation

The first stage establishes the initial 3D structure using a combination of Neural Radiance Fields (NeRF) and Neural Surface Reconstruction (NeuS):

1. **NeRF Training**: Creates a volumetric representation of the object from the reference image
2. **NeuS Training**: Refines the volumetric representation into a more accurate surface model

This stage focuses on establishing consistent geometry while preparing for subsequent refinement.

Sources: [README.md:107-111]()

### Stage 2: Geometry Refinement

The second stage enhances the geometric details through score distillation sampling via a view-dependent diffusion model. This process sculpts the geometry to ensure coherent renders from multiple viewpoints.

Sources: [README.md:113-115]()

### Stage 3: Texture Refinement

The final stage employs Bootstrapped Score Distillation, a key innovation of DreamCraft3D:

1. A personalized diffusion model (Dreambooth) is trained on augmented renderings of the scene
2. This model provides view-consistent guidance for texture optimization
3. Through alternating optimization, improvements become mutually reinforcing:
   - The optimized 3D scene improves training of the scene-specific diffusion model
   - The improved diffusion model provides better guidance for 3D optimization

This bootstrap mechanism significantly enhances texture quality and coherence.

Sources: [README.md:118-120](), [README.md:12-19]()

## Data Flow

The following diagram illustrates the data flow through the DreamCraft3D pipeline:

```mermaid
flowchart TD
    A["User Input"] --> B["2D Reference Image"]
    A --> C["Text Prompt"]
    
    B --> D["preprocess_image.py"]
    
    D --> E["RGBA Image"]
    D --> F["Depth Map"]
    D --> G["Normal Map"]
    
    E --> H["Stage 1 - Coarse Geometry"]
    F --> H
    G --> H
    C --> H
    
    H --> |"last.ckpt"| I["Stage 2 - Geometry Refinement"]
    C --> I
    
    I --> |"last.ckpt"| J["Stage 3 - Texture Refinement"]
    C --> J
    
    J --> K["Textured 3D Mesh"]
```

Sources: [README.md:98-121]()

## Key Components

DreamCraft3D leverages several critical components and pre-trained models:

| Component | Purpose | Configuration File |
|-----------|---------|-------------------|
| Zero123 | View-dependent diffusion model | `configs/dreamcraft3d-coarse-nerf.yaml` |
| Omnidata | Depth and normal prediction | `preprocess_image.py` |
| NeRF | Initial volumetric representation | `configs/dreamcraft3d-coarse-nerf.yaml` |
| NeuS | Surface reconstruction | `configs/dreamcraft3d-coarse-neus.yaml` |
| Score Distillation Sampling | Geometry refinement | `configs/dreamcraft3d-geometry.yaml` |
| Dreambooth Lora | Personalized diffusion model | `configs/dreamcraft3d-texture.yaml` |

Sources: [README.md:83-96](), [README.md:107-120]()

## Code Structure Mapping

The following diagram maps the high-level concepts to specific code entities:

```mermaid
classDiagram
    class launch_py {
        Main entry point
        Loads configurations
        Initiates training stages
    }
    
    class preprocess_image_py {
        Background removal
        Depth prediction
        Normal prediction
    }
    
    class Stage1 {
        dreamcraft3d-coarse-nerf.yaml
        dreamcraft3d-coarse-neus.yaml
    }
    
    class Stage2 {
        dreamcraft3d-geometry.yaml
    }
    
    class Stage3 {
        dreamcraft3d-texture.yaml
        train_dreambooth_lora.py
    }
    
    class SupportingSystems {
        Prompt processors
        Image loaders
        Pre-trained models
    }
    
    launch_py --> Stage1
    launch_py --> Stage2
    launch_py --> Stage3
    preprocess_image_py --> Stage1
    SupportingSystems --> Stage1
    SupportingSystems --> Stage2
    SupportingSystems --> Stage3
    Stage1 --> Stage2: last.ckpt
    Stage2 --> Stage3: last.ckpt
```

Sources: [README.md:107-120]()

## Handling Advanced Scenarios

For certain inputs, additional steps may be required to achieve optimal results:

- **Janus Problem**: When faces appear on both sides of an object in Stage 1 (an issue with view synthesis), training a custom Text2Image model can help. This involves:
  1. Generating multi-view images from the reference image using Zero123++
  2. Training a personalized DeepFloyd model using Dreambooth Lora
  3. Using this model for guidance during Stage 1

For more details on handling this specific issue, see [Handling the Janus Problem](#5.1).

Sources: [README.md:123-161]()

## Memory Requirements and Optimization

DreamCraft3D requires GPUs with significant VRAM (at least 20GB). The default configurations are designed for 40GB A100 GPUs. Memory usage can be reduced by:

- Decreasing rendering resolution in NeuS and other stages
- Adjusting batch sizes and other parameters

Sources: [README.md:49](), [README.md:164]()

## Exporting Results

The final 3D model can be exported as a textured mesh (OBJ+MTL) using the mesh-exporter:

```
python launch.py --config path/to/trial/dir/configs/parsed.yaml --export --gpu 0 resume=path/to/trial/dir/ckpts/last.ckpt system.exporter_type=mesh-exporter
```

Sources: [README.md:166-171]()

This overview provides a foundation for understanding the DreamCraft3D system. For more detailed information on specific components and processes, please refer to the relevant sections in the documentation.

---

