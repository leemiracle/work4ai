<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/CvT · page 3 Architecture & Design · fetched 2026-10-26 -->

# Architecture & Design

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [lib/models/cls_cvt.py](lib/models/cls_cvt.py)

</details>



This document provides a comprehensive overview of the CvT (Convolutional vision Transformers) system architecture and design principles. It covers the core model architecture, training pipeline design, configuration system, and key architectural decisions that enable the integration of convolutional neural networks with vision transformers.

For implementation details of specific model components, see [CvT Model Architecture](#3.1). For training procedures and optimization strategies, see [Training Pipeline](#3.2). For data handling and preprocessing, see [Data Pipeline](#3.3).

## System Overview

The CvT repository implements a hierarchical vision transformer architecture that introduces convolutional operations at key points to improve performance and efficiency. The system is designed around three core principles:

1. **Multi-stage hierarchical processing** - Progressive feature extraction through multiple transformer stages
2. **Convolutional token embeddings** - Replace linear patch embeddings with convolutional projections
3. **Configuration-driven architecture** - YAML-based specification of model variants and training parameters

### High-Level System Architecture

```mermaid
graph TB
    subgraph "Execution Layer"
        runsh["run.sh"] --> trainpy["tools/train.py"]
    end
    
    subgraph "Configuration System"
        yamlconfigs["experiments/imagenet/cvt/*.yaml"] --> configlib["lib/config/"]
    end
    
    subgraph "Core Library"
        models["lib/models/cls_cvt.py"] 
        core["lib/core/function.py"]
        dataset["lib/dataset/"]
        optim["lib/optim/"]
    end
    
    subgraph "CvT Architecture"
        cvtmodel["ConvolutionalVisionTransformer"] --> stages["VisionTransformer stages"]
        stages --> blocks["Block components"]
        blocks --> attention["Attention with conv projections"]
        blocks --> convembed["ConvEmbed token embedding"]
    end
    
    trainpy --> configlib
    trainpy --> core
    core --> models
    core --> dataset
    core --> optim
    models --> cvtmodel
    yamlconfigs --> cvtmodel
    
    style runsh fill:#f9f9f9
    style cvtmodel fill:#f9f9f9
    style trainpy fill:#f9f9f9
```

**Sources:** [README.md:1-148](), [lib/models/cls_cvt.py:491-646]()

## Core Architecture Components

### ConvolutionalVisionTransformer Design

The main model architecture follows a stage-wise design where each stage processes features at different scales. The `ConvolutionalVisionTransformer` class orchestrates multiple `VisionTransformer` stages, each configured with specific parameters for patch sizes, embedding dimensions, and attention heads.

```mermaid
graph TB
    subgraph "ConvolutionalVisionTransformer"
        init["__init__(spec)"] --> stages_creation["Create VisionTransformer stages"]
        stages_creation --> classifier["Linear classification head"]
    end
    
    subgraph "VisionTransformer Stage"
        patch_embed["ConvEmbed patch embedding"] --> cls_token["CLS token (optional)"]
        cls_token --> transformer_blocks["Sequential Block modules"]
        transformer_blocks --> output["Feature output + CLS tokens"]
    end
    
    subgraph "Block Architecture"
        norm1["LayerNorm"] --> attention_layer["Attention with conv projections"]
        attention_layer --> residual1["Residual connection"]
        residual1 --> norm2["LayerNorm"] 
        norm2 --> mlp["Mlp feed-forward"]
        mlp --> residual2["Residual connection"]
    end
    
    stages_creation --> patch_embed
    transformer_blocks --> norm1
    
    style init fill:#f9f9f9
    style patch_embed fill:#f9f9f9
    style attention_layer fill:#f9f9f9
```

**Sources:** [lib/models/cls_cvt.py:491-540](), [lib/models/cls_cvt.py:372-489](), [lib/models/cls_cvt.py:289-334]()

### Convolutional Attention Mechanism

The key innovation in CvT is the `Attention` class that replaces standard linear projections with convolutional projections for Q, K, and V computation. This enables spatial inductive bias while maintaining transformer's global modeling capability.

```mermaid
graph LR
    subgraph "Attention Forward Pass"
        input["x, h, w"] --> conv_projections["forward_conv()"]
        conv_projections --> qkv_linear["proj_q, proj_k, proj_v"]
        qkv_linear --> reshape["rearrange for multi-head"]
        reshape --> attention_comp["einsum attention computation"]
        attention_comp --> output_proj["final projection"]
    end
    
    subgraph "Convolutional Projections"
        spatial_input["2D spatial tokens"] --> conv_q["conv_proj_q (dw_bn/avg)"]
        spatial_input --> conv_k["conv_proj_k (dw_bn/avg)"]
        spatial_input --> conv_v["conv_proj_v (dw_bn/avg)"]
        conv_q --> linear_q["Linear Q projection"]
        conv_k --> linear_k["Linear K projection"] 
        conv_v --> linear_v["Linear V projection"]
    end
    
    conv_projections --> spatial_input
    linear_q --> qkv_linear
    linear_k --> qkv_linear
    linear_v --> qkv_linear
    
    style conv_projections fill:#f9f9f9
    style spatial_input fill:#f9f9f9
```

**Sources:** [lib/models/cls_cvt.py:77-212](), [lib/models/cls_cvt.py:124-160](), [lib/models/cls_cvt.py:162-188]()

## Training System Architecture

### Configuration-Driven Design

The system uses YAML configuration files to specify model architectures and training parameters. The `spec` parameter in `ConvolutionalVisionTransformer` defines all stage-specific settings including patch sizes, embedding dimensions, attention heads, and projection methods.

| Configuration Parameter | Purpose | Code Reference |
|------------------------|---------|----------------|
| `NUM_STAGES` | Number of transformer stages | [lib/models/cls_cvt.py:502]() |
| `PATCH_SIZE` | Convolutional patch sizes per stage | [lib/models/cls_cvt.py:505]() |
| `DIM_EMBED` | Embedding dimensions per stage | [lib/models/cls_cvt.py:508]() |
| `QKV_PROJ_METHOD` | Projection method (dw_bn/avg/linear) | [lib/models/cls_cvt.py:517]() |
| `CLS_TOKEN` | Whether to use CLS token per stage | [lib/models/cls_cvt.py:516]() |

### Training Pipeline Flow

```mermaid
graph TD
    start["run.sh execution"] --> train_script["tools/train.py"]
    train_script --> config_load["Load YAML configuration"]
    config_load --> model_build["get_cls_model()"]
    
    subgraph "Model Construction"
        model_build --> spec_parse["Parse model spec"]
        spec_parse --> stage_creation["Create VisionTransformer stages"]
        stage_creation --> weight_init["Initialize weights"]
    end
    
    subgraph "Training Loop"
        weight_init --> train_epoch["train_one_epoch()"]
        train_epoch --> forward_pass["ConvolutionalVisionTransformer.forward()"]
        forward_pass --> loss_comp["Loss computation"]
        loss_comp --> backprop["Backward pass"]
        backprop --> optimizer_step["Optimizer step"]
        optimizer_step --> validation["Validation evaluation"]
        validation --> checkpoint["Save checkpoint"]
    end
    
    checkpoint --> train_epoch
    
    style model_build fill:#f9f9f9
    style train_epoch fill:#f9f9f9
    style forward_pass fill:#f9f9f9
```

**Sources:** [README.md:85-114](), [lib/models/cls_cvt.py:626-645]()

## Key Architectural Decisions

### Hierarchical Multi-Scale Processing

The CvT architecture processes images through multiple stages with progressively larger receptive fields and embedding dimensions. Each stage uses different patch sizes and strides to capture features at different scales:

- **Stage 1**: Initial feature extraction with larger patches (7x7, stride 4)
- **Stage 2**: Intermediate processing with smaller patches (3x3, stride 2) 
- **Stage 3**: Deep processing with fine-grained features (3x3, stride 2)

### Convolutional Token Embeddings

The `ConvEmbed` class replaces standard linear patch embeddings with convolutional projections, providing translation invariance and better handling of input resolution changes.

```mermaid
graph LR
    subgraph "ConvEmbed Processing"
        input_image["Input image"] --> conv2d["nn.Conv2d projection"]
        conv2d --> reshape_tokens["Reshape to tokens"]
        reshape_tokens --> norm["Optional LayerNorm"]
        norm --> spatial_reshape["Reshape back to spatial"]
    end
    
    subgraph "Configuration"
        patch_size["patch_size"] --> conv2d
        stride["stride"] --> conv2d
        padding["padding"] --> conv2d
        embed_dim["embed_dim"] --> conv2d
    end
    
    style conv2d fill:#f9f9f9
    style input_image fill:#f9f9f9
```

**Sources:** [lib/models/cls_cvt.py:336-370](), [lib/models/cls_cvt.py:397-405]()

### No Positional Encoding

Unlike standard vision transformers, CvT eliminates the need for positional encodings by incorporating spatial inductive bias through convolutional operations. This simplifies the architecture and enables better handling of variable input resolutions.

### Model Variants and Scaling

The system supports multiple model variants through configuration:

| Model Variant | Parameters | FLOPs | Key Characteristics |
|---------------|------------|-------|-------------------|
| CvT-13 | 20M | 4.5G | Lightweight, 13-layer configuration |
| CvT-21 | 32M | 7.1G | Medium-scale, 21-layer configuration |
| CvT-W24 | 277M | 193.2G | Large-scale, wide 24-layer configuration |

**Sources:** [README.md:6-21](), [lib/models/cls_cvt.py:502-534]()

---

