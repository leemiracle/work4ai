<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/DL4AGX · page 3 Models: Efficient Architectures · fetched 2026-10-26 -->

# Models: Efficient Architectures

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Models/README.md](Models/README.md)
- [Models/ReduceFormer/reduceformer/backbone.py](Models/ReduceFormer/reduceformer/backbone.py)
- [Models/ReduceFormer/reduceformer/cls.py](Models/ReduceFormer/reduceformer/cls.py)

</details>



## Purpose and Scope

This document provides an overview of the efficient model architectures implemented in the Models directory, designed to achieve improved accuracy, faster inference speed, and better resource utilization for edge device deployment in autonomous vehicle applications. These architectures focus on hardware-friendly designs that can be effectively deployed using the solutions documented in [AV-Solutions: Deployment Solutions](#2).

For detailed implementation specifics of individual architectures, see [Design Philosophy and Architecture Overview](#3.1), [ReduceFormer Architecture](#3.2), and [Swin-Free and Additional Models](#3.3).

## Architecture Portfolio

The Models directory contains four distinct efficient architecture families, each targeting different aspects of model optimization:

| Architecture | Primary Focus | Key Innovation | Target Application |
|--------------|---------------|----------------|-------------------|
| **DEST** | Depth Estimation | GPU-friendly simplified attention | Depth estimation, semantic segmentation |
| **ConvSelfAttention** | TensorRT Compatibility | Convolution-only attention emulation | Safety-critical autonomous systems |
| **ReduceFormer** | Transformer Simplification | Reduction operations + element-wise multiplication | General vision tasks, edge deployment |
| **Swin-Free** | Window Attention | Size-varying windows without shifting | High-throughput inference |

**Sources:** [Models/README.md:1-18]()

## Design Philosophy

### Hardware-Friendly Optimization Strategies

The efficient architectures implement several core optimization strategies:

```mermaid
graph TB
    A["Efficient Architecture Design"] --> B["Computation Reduction"]
    A --> C["Memory Optimization"] 
    A --> D["Hardware Compatibility"]
    
    B --> B1["Simplified Attention Mechanisms"]
    B --> B2["Reduction Operations"]
    B --> B3["Element-wise Operations"]
    
    C --> C1["Reduced Parameter Count"]
    C --> C2["Optimized Memory Access"]
    C --> C3["Efficient Feature Reuse"]
    
    D --> D1["TensorRT Compatible Operations"]
    D --> D2["GPU-friendly Computations"]
    D --> D3["Edge Device Deployment"]
    
    B1 --> E["DEST: GPU-friendly attention"]
    B2 --> F["ReduceFormer: RF_Attn mechanism"]
    B3 --> G["ConvSelfAttention: Conv-only operations"]
    
    D1 --> H["ConvSelfAttention restricted mode"]
    D2 --> I["ReduceFormer multi-scale processing"]
    D3 --> J["Swin-Free size-varying windows"]
```

**Sources:** [Models/README.md:2-18]()

## ReduceFormer Implementation Architecture

ReduceFormer represents the most comprehensive implementation in the Models directory, featuring a modular backbone-head architecture:

```mermaid
graph TB
    subgraph "ReduceFormer Architecture"
        A["ReduceFormerCls"] --> B["ReduceFormerBackbone"]
        A --> C["ClsHead"]
        
        B --> D["Input Stem"]
        B --> E["Early Stages"]
        B --> F["Later Stages with RF_Attn"]
        
        F --> G["ReduceFormerBlock"]
        G --> H["RF_Attn (context_module)"]
        G --> I["MBConv (local_module)"]
        
        H --> J["Multi-scale QKV Generation"]
        H --> K["Reduction-based Attention"]
        H --> L["Element-wise Multiplication"]
        
        C --> M["ConvLayer + AdaptiveAvgPool2d"]
        C --> N["LinearLayer Classification"]
    end
    
    subgraph "Model Variants"
        O["reduceformer_backbone_b1<br/>16,32,64,128,256 channels<br/>9.0M parameters"]
        P["reduceformer_backbone_b2<br/>24,48,96,192,384 channels<br/>24.5M parameters"] 
        Q["reduceformer_backbone_b3<br/>32,64,128,256,512 channels<br/>48.1M parameters"]
    end
    
    B --> O
    B --> P
    B --> Q
```

**Sources:** [Models/ReduceFormer/reduceformer/backbone.py:188-338](), [Models/ReduceFormer/reduceformer/cls.py:58-109]()

## Core Implementation Components

### RF_Attn Mechanism

The `RF_Attn` class implements the core attention mechanism using reduction operations:

```mermaid
graph LR
    A["Input Tensor"] --> B["qkv: ConvLayer(3 * total_dim)"]
    B --> C["Multi-scale Aggregation"]
    C --> D["aggreg: ModuleList[Conv2d]"]
    D --> E["rf_att: Reduction Attention"]
    E --> F["proj: ConvLayer(out_channels)"]
    F --> G["Output Tensor"]
    
    subgraph "RF_Attn Components"
        H["kernel_func: build_act('relu')"]
        I["eps: 1.0e-15 (numerical stability)"]
        J["scales: tuple (default: (5,))"]
    end
    
    E --> H
    E --> I
    C --> J
```

**Sources:** [Models/ReduceFormer/reduceformer/backbone.py:40-149]()

### Model Variant Configurations

The three ReduceFormer variants provide different parameter-accuracy trade-offs:

| Variant | Width List | Depth List | Dim | Parameters | Use Case |
|---------|------------|------------|-----|------------|----------|
| **B1** | [16,32,64,128,256] | [1,2,3,3,4] | 16 | 9.0M | Ultra-lightweight edge |
| **B2** | [24,48,96,192,384] | [1,3,4,4,6] | 32 | 24.5M | Balanced efficiency |
| **B3** | [32,64,128,256,512] | [1,4,6,6,9] | 32 | 48.1M | High accuracy applications |

**Sources:** [Models/ReduceFormer/reduceformer/backbone.py:313-338]()

## Code Entity Relationships

### Class Inheritance and Composition

```mermaid
graph TD
    A["nn.Module"] --> B["ReduceFormerBackbone"]
    A --> C["RF_Attn"] 
    A --> D["ReduceFormerBlock"]
    A --> E["ReduceFormerCls"]
    
    B --> F["input_stem: OpSequential"]
    B --> G["stages: nn.ModuleList"]
    
    D --> H["context_module: ResidualBlock[RF_Attn]"]
    D --> I["local_module: ResidualBlock[MBConv]"]
    
    C --> J["qkv: ConvLayer"]
    C --> K["aggreg: nn.ModuleList[Conv2d]"]
    C --> L["proj: ConvLayer"]
    
    E --> M["backbone: ReduceFormerBackbone"]
    E --> N["head: ClsHead"]
    
    subgraph "Factory Functions"
        O["reduceformer_backbone_b1()"]
        P["reduceformer_backbone_b2()"] 
        Q["reduceformer_backbone_b3()"]
        R["reduceformer_cls_b1()"]
        S["reduceformer_cls_b2()"]
        T["reduceformer_cls_b3()"]
    end
    
    O --> B
    P --> B
    Q --> B
    R --> E
    S --> E
    T --> E
```

**Sources:** [Models/ReduceFormer/reduceformer/backbone.py:32-37](), [Models/ReduceFormer/reduceformer/cls.py:23-29]()

## Integration with Deployment Pipeline

The efficient architectures are designed to integrate seamlessly with the TensorRT deployment pipeline:

```mermaid
graph LR
    A["Efficient Models<br/>(Models/)"] --> B["PyTorch Training"]
    B --> C["ONNX Export"]
    C --> D["TensorRT Optimization<br/>(AV-Solutions/)"]
    
    subgraph "Architecture Features for Deployment"
        E["GPU-friendly Operations"]
        F["Reduced Parameter Count"]
        G["Hardware-compatible Attention"]
        H["Optimized Memory Access"]
    end
    
    A --> E
    A --> F
    A --> G
    A --> H
    
    E --> D
    F --> D
    G --> D
    H --> D
```

**Sources:** [Models/README.md:2-18]()

---

