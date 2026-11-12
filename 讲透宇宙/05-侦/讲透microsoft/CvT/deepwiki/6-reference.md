<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/CvT · page 6 Reference · fetched 2026-10-26 -->

# Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [lib/models/cls_cvt.py](lib/models/cls_cvt.py)

</details>



This page serves as the main entry point for comprehensive reference documentation of the CvT (Convolutional vision Transformers) codebase. It provides an overview of model variants, API documentation, and legal information for developers and researchers working with the CvT implementation.

For step-by-step usage instructions, see [Getting Started](#2). For architectural details and design principles, see [Architecture & Design](#3). For practical guides on training and evaluation, see [Usage Guide](#4).

## Reference Documentation Overview

The reference documentation is organized into three main categories, each covering different aspects of the CvT codebase:

```mermaid
graph TB
    ref["Reference Documentation<br/>Complete technical reference"]
    
    subgraph "Model Specifications"
        variants["Model Variants<br/>[6.1](#6.1)<br/>• CvT-13, CvT-21, CvT-W24<br/>• Configuration parameters<br/>• Performance metrics"]
    end
    
    subgraph "Technical Documentation" 
        api["API Reference<br/>[6.2](#6.2)<br/>• Core classes & functions<br/>• Method signatures<br/>• Implementation details"]
    end
    
    subgraph "Project Information"
        legal["Legal & Governance<br/>[6.3](#6.3)<br/>• MIT License<br/>• Security policies<br/>• Code of conduct"]
    end
    
    ref --> variants
    ref --> api  
    ref --> legal
    
    style ref fill:#f9f9f9,stroke:#333,stroke-width:2px
```

Sources: [LICENSE:1-22]()

## Core Code Entity Mapping

The following diagram maps key system concepts to their corresponding code entities, enabling quick navigation from architectural concepts to implementation details:

```mermaid
graph TB
    subgraph "Model Architecture Entities"
        cvt_model["ConvolutionalVisionTransformer<br/>(Multi-stage CvT model)"]
        vit_stage["VisionTransformer<br/>(Single stage)"] 
        block["Block<br/>(Transformer block)"]
        attention["Attention<br/>(Conv attention mechanism)"]
    end
    
    subgraph "Component Entities"
        conv_embed["ConvEmbed<br/>(Convolutional embedding)"]
        mlp["Mlp<br/>(Feed-forward network)"]
        layer_norm["LayerNorm<br/>(fp16-compatible normalization)"]
        quick_gelu["QuickGELU<br/>(Activation function)"]
    end
    
    subgraph "Factory & Registration"
        get_cls_model["get_cls_model()<br/>(Model factory function)"]
        register_model["@register_model<br/>(Model registration decorator)"]
    end
    
    subgraph "Configuration Specs"
        model_spec["config.MODEL.SPEC<br/>(Architecture configuration)"]
        patch_size["PATCH_SIZE<br/>(Conv kernel sizes)"]
        dim_embed["DIM_EMBED<br/>(Feature dimensions)"]
        num_heads["NUM_HEADS<br/>(Attention heads)"]
    end
    
    cvt_model --> vit_stage
    vit_stage --> block
    block --> attention
    block --> mlp
    
    vit_stage --> conv_embed
    block --> layer_norm
    mlp --> quick_gelu
    
    get_cls_model --> cvt_model
    get_cls_model --> model_spec
    register_model --> get_cls_model
    
    model_spec --> patch_size
    model_spec --> dim_embed  
    model_spec --> num_heads
    
    style cvt_model fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style get_cls_model fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
```

Sources: [lib/models/cls_cvt.py:491-646]()

## Key Reference Tables

### Core Model Classes

| Class | Purpose | Location | Key Methods |
|-------|---------|----------|-------------|
| `ConvolutionalVisionTransformer` | Multi-stage CvT model | [lib/models/cls_cvt.py:491]() | `forward()`, `forward_features()` |
| `VisionTransformer` | Single stage transformer | [lib/models/cls_cvt.py:372]() | `forward()`, `_init_weights_*()` |
| `Attention` | Convolutional attention mechanism | [lib/models/cls_cvt.py:77]() | `forward()`, `forward_conv()` |
| `Block` | Transformer block with residual connections | [lib/models/cls_cvt.py:289]() | `forward()` |
| `ConvEmbed` | Convolutional token embedding | [lib/models/cls_cvt.py:336]() | `forward()` |

### Configuration Parameters

| Parameter Category | Config Keys | Description | 
|-------------------|-------------|-------------|
| Architecture | `NUM_STAGES`, `DEPTH`, `DIM_EMBED` | Stage count, block depth, feature dimensions |
| Attention | `NUM_HEADS`, `QKV_PROJ_METHOD`, `KERNEL_QKV` | Multi-head setup and conv projections |
| Convolution | `PATCH_SIZE`, `PATCH_STRIDE`, `PADDING_*` | Convolutional embedding parameters |
| Training | `DROP_RATE`, `ATTN_DROP_RATE`, `DROP_PATH_RATE` | Regularization and dropout rates |

### Factory Functions

| Function | Purpose | Location | Returns |
|----------|---------|----------|---------|
| `get_cls_model()` | Create CvT model from config | [lib/models/cls_cvt.py:626]() | `ConvolutionalVisionTransformer` |
| `@register_model` | Register model in factory | [lib/models/cls_cvt.py:626]() | Decorator |

Sources: [lib/models/cls_cvt.py:77-646]()

## Model Architecture Hierarchy

```mermaid
graph TB
    subgraph "Multi-Stage CvT Architecture"
        cvt["ConvolutionalVisionTransformer<br/>• num_stages configurable<br/>• stage0, stage1, stage2..."]
        
        subgraph "Per-Stage Components"
            stage["VisionTransformer<br/>• patch_embed (ConvEmbed)<br/>• blocks (ModuleList)<br/>• cls_token (optional)"]
            
            subgraph "Block-Level Components"
                block_comp["Block<br/>• norm1, norm2 (LayerNorm)<br/>• attn (Attention)<br/>• mlp (Mlp)<br/>• drop_path (DropPath)"]
                
                subgraph "Attention Components"
                    attn_comp["Attention<br/>• conv_proj_q/k/v<br/>• proj_q/k/v (Linear)<br/>• attn_drop, proj_drop"]
                end
                
                subgraph "MLP Components" 
                    mlp_comp["Mlp<br/>• fc1, fc2 (Linear)<br/>• act (QuickGELU)<br/>• drop (Dropout)"]
                end
            end
        end
    end
    
    cvt --> stage
    stage --> block_comp
    block_comp --> attn_comp
    block_comp --> mlp_comp
    
    style cvt fill:#f0f8ff,stroke:#4682b4,stroke-width:2px
    style stage fill:#f5f5f5,stroke:#696969,stroke-width:1px
```

Sources: [lib/models/cls_cvt.py:372-646]()

## Legal and Licensing

The CvT codebase is released under the MIT License by Microsoft Corporation. This provides broad permissions for use, modification, and distribution with minimal restrictions.

**License**: MIT License  
**Copyright**: Microsoft Corporation  
**Key Terms**: Permission granted for use, copy, modify, merge, publish, distribute, sublicense, and sell

For complete license text and additional governance information, see [Legal & Governance](#6.3).

Sources: [LICENSE:1-22]()

## Navigation to Detailed References

- **[Model Variants](#6.1)**: Complete specifications for CvT-13, CvT-21, and CvT-W24 models including configuration parameters and performance benchmarks
- **[API Reference](#6.2)**: Detailed documentation of classes, methods, and functions with parameter descriptions and usage examples  
- **[Legal & Governance](#6.3)**: License information, security policies, contribution guidelines, and project governance documents

---

