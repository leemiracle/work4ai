<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Cream · extra page TinyViT Architecture · fetched 2026-10-26 -->

# TinyViT Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [TinyViT/.figure/cat.jpg](TinyViT/.figure/cat.jpg)
- [TinyViT/README.md](TinyViT/README.md)
- [TinyViT/data/__init__.py](TinyViT/data/__init__.py)
- [TinyViT/data/imagenet_classnames.py](TinyViT/data/imagenet_classnames.py)
- [TinyViT/inference.py](TinyViT/inference.py)
- [TinyViT/models/tiny_vit.py](TinyViT/models/tiny_vit.py)
- [TinyViT/tests/test_models.py](TinyViT/tests/test_models.py)

</details>



This document provides a detailed explanation of the TinyViT model architecture. TinyViT is a family of small and efficient Vision Transformers designed for high performance with low parameter counts. For information on the TinyViT training pipeline and distillation process, see [TinyViT Training Pipeline](#2.1.2) and [Fast Distillation Framework](#2.1.3).

## Overview

TinyViT is a hierarchical vision transformer architecture optimized for efficiency while maintaining strong performance. The model family ranges from 5M to 21M parameters while achieving competitive accuracy compared to larger models. TinyViT incorporates several architectural innovations:

1. **Hierarchical Design**: Multi-stage architecture with progressively increased channel dimensions and reduced spatial resolution
2. **Hybrid Architecture**: Combines MBConv blocks (Mobile inverted Bottleneck Convolution) in early stages with transformer blocks in later stages
3. **Window-based Attention**: Efficient local attention computation within windows
4. **Relative Position Encoding**: Integrated directly into the attention mechanism

Sources: [TinyViT/models/tiny_vit.py](TinyViT/models/tiny_vit.py), [TinyViT/README.md](TinyViT/README.md)

## Architectural Overview

TinyViT follows a hierarchical design with 4 stages, where each stage has a specific resolution, channel dimension, and block type.

### High-Level Architecture

```mermaid
flowchart TD
    subgraph "TinyViT Architecture"
        Input["Input Image"] --> PatchEmbed["Patch Embedding
        (H/4 × W/4 resolution)"]
        
        PatchEmbed --> Stage1["Stage 1: ConvLayer
        MBConv Blocks"]
        Stage1 --> Downsample1["Patch Merging
        (H/8 × W/8)"]
        
        Downsample1 --> Stage2["Stage 2: BasicLayer
        Transformer Blocks"]
        Stage2 --> Downsample2["Patch Merging
        (H/16 × W/16)"]
        
        Downsample2 --> Stage3["Stage 3: BasicLayer
        Transformer Blocks"]
        Stage3 --> Downsample3["Patch Merging
        (H/32 × W/32)"]
        
        Downsample3 --> Stage4["Stage 4: BasicLayer
        Transformer Blocks"]
        
        Stage4 --> GlobalPool["Global Average
        Pooling"]
        
        GlobalPool --> NormHead["LayerNorm"]
        NormHead --> ClassifierHead["Linear Classifier"]
    end
```

Sources: [TinyViT/models/tiny_vit.py:453-591](TinyViT/models/tiny_vit.py)

### Model Components Relationship

```mermaid
classDiagram
    TinyViT --> PatchEmbed : uses
    TinyViT --> ConvLayer : contains in stage 1
    TinyViT --> BasicLayer : contains in stages 2-4
    TinyViT --> LayerNorm : for normalization
    TinyViT --> Linear : for classification
    
    ConvLayer --> MBConv : contains multiple
    ConvLayer --> PatchMerging : optional downsampling
    
    BasicLayer --> TinyViTBlock : contains multiple
    BasicLayer --> PatchMerging : optional downsampling
    
    TinyViTBlock --> Attention : self-attention mechanism
    TinyViTBlock --> Mlp : feed-forward network
    TinyViTBlock --> Conv2d_BN : for local convolution
    
    MBConv --> Conv2d_BN : for pointwise & depthwise convs
    
    PatchEmbed --> Conv2d_BN : for patch tokenization
    
    class TinyViT {
        +forward()
        +forward_features()
    }
    
    class PatchEmbed {
        +patches_resolution
        +num_patches
        +embed_dim
    }
    
    class TinyViTBlock {
        +window_size
        +input_resolution
        +num_heads
        +forward()
    }
    
    class Attention {
        +num_heads
        +key_dim
        +attention_biases
    }
```

Sources: [TinyViT/models/tiny_vit.py](TinyViT/models/tiny_vit.py)

## Main Components

### Patch Embedding

The patch embedding layer is the first component of TinyViT, responsible for converting the input image into tokens. Unlike standard Vision Transformers that use a single convolution operation, TinyViT uses a sequence of two strided convolutions to reduce the spatial dimensions by a factor of 4 (2×2) while increasing the channel dimension.

```mermaid
flowchart LR
    subgraph "PatchEmbed"
        Input["Input Image
        (B, 3, H, W)"] --> Conv1["Conv2d_BN
        (3→embed_dim/2, kernel=3, stride=2)"]
        
        Conv1 --> Activation1["Activation()"]
        
        Activation1 --> Conv2["Conv2d_BN
        (embed_dim/2→embed_dim, kernel=3, stride=2)"]
        
        Conv2 --> Output["Output Feature Map
        (B, embed_dim, H/4, W/4)"]
    end
```

Sources: [TinyViT/models/tiny_vit.py:64-81](TinyViT/models/tiny_vit.py)

### Model Stages

TinyViT consists of 4 stages, each with different channel dimensions and block types:

1. **Stage 1**: Uses MBConv blocks wrapped in a ConvLayer
2. **Stages 2-4**: Use Transformer blocks (TinyViTBlock) wrapped in BasicLayers

The stages are connected by PatchMerging layers that reduce spatial dimensions and increase channel dimensions.

#### Stage 1: ConvLayer with MBConv Blocks

The first stage uses MBConv blocks, which are efficient mobile inverted bottleneck convolution blocks similar to those in MobileNet and EfficientNet architectures.

```mermaid
flowchart LR
    subgraph "MBConv Block"
        Input["Input"] --> ShortcutBranch["Identity"]
        
        Input --> Conv1["Conv2d_BN
        (dim→hidden_dim, 1×1)"]
        Conv1 --> Act1["Activation"]
        
        Act1 --> Conv2["Conv2d_BN
        (hidden_dim→hidden_dim, 3×3, groups=hidden_dim)"]
        Conv2 --> Act2["Activation"]
        
        Act2 --> Conv3["Conv2d_BN
        (hidden_dim→dim, 1×1, bn_weight_init=0)"]
        
        Conv3 --> DropPath["DropPath"]
        
        DropPath --> Add(("+"))
        ShortcutBranch --> Add
        
        Add --> Act3["Activation"]
        Act3 --> Output["Output"]
    end
```

Sources: [TinyViT/models/tiny_vit.py:84-122](TinyViT/models/tiny_vit.py)

#### Stages 2-4: BasicLayer with TinyViT Blocks

Stages 2-4 use TinyViT Blocks, which are specialized transformer blocks with window-based attention and a local convolution between attention and MLP.

```mermaid
flowchart TB
    subgraph "TinyViT Block"
        Input["Input (B, L, C)"] --> Residual1["Identity"]
        
        Input --> WindowAttention["Window-based Self-Attention"]
        WindowAttention --> DropPath1["DropPath"]
        
        DropPath1 --> Add1(("+"))
        Residual1 --> Add1
        
        Add1 --> Reshape["Reshape to (B, C, H, W)"]
        
        Reshape --> LocalConv["Depthwise Conv
        (kernel_size=local_conv_size)"]
        
        LocalConv --> Reshape2["Reshape to (B, L, C)"]
        
        Reshape2 --> Residual2["Identity"]
        
        Reshape2 --> MLP["MLP with LayerNorm"]
        MLP --> DropPath2["DropPath"]
        
        DropPath2 --> Add2(("+"))
        Residual2 --> Add2
        
        Add2 --> Output["Output (B, L, C)"]
    end
```

Sources: [TinyViT/models/tiny_vit.py:289-379](TinyViT/models/tiny_vit.py)

### Attention Mechanism

TinyViT uses a specialized attention mechanism with a learned relative position bias. This is more efficient than absolute position embeddings and provides better generalization.

```mermaid
flowchart LR
    subgraph "Attention Mechanism"
        Input["Input (B, N, C)"] --> LN["LayerNorm"]
        
        LN --> QKV["QKV Projection"]
        
        QKV --> Split["Split into Q, K, V
        and Reshape"]
        
        Split --> Q["Q: (B, num_heads, N, key_dim)"]
        Split --> K["K: (B, num_heads, N, key_dim)"]
        Split --> V["V: (B, num_heads, N, d)"]
        
        Q --> MatMul["MatMul(Q, K.transpose)"]
        K --> MatMul
        
        MatMul --> Scale["Scale by 1/sqrt(key_dim)"]
        
        Scale --> AddBias["Add RelPos Bias"]
        
        AddBias --> Softmax["Softmax"]
        
        Softmax --> AttV["MatMul with V"]
        V --> AttV
        
        AttV --> Reshape2["Reshape & Transpose"]
        
        Reshape2 --> Proj["Linear Projection"]
        
        Proj --> Output["Output (B, N, dim)"]
    end
```

Sources: [TinyViT/models/tiny_vit.py:216-286](TinyViT/models/tiny_vit.py)

### Window-based Attention

TinyViT uses window-based attention to reduce computational complexity. For image regions larger than the window size, the feature map is divided into non-overlapping windows before applying self-attention.

```mermaid
flowchart TD
    subgraph "Window Attention Process"
        Input["Input (B, H, W, C)"] --> Pad["Optional Padding"]
        
        Pad --> Partition["Window Partition
        (B*nH*nW, window_size*window_size, C)"]
        
        Partition --> Attention["Self-Attention"]
        
        Attention --> Merge["Window Reverse
        (B, H, W, C)"]
        
        Merge --> RemovePad["Remove Padding"]
        
        RemovePad --> Output["Output (B, H*W, C)"]
    end
```

Sources: [TinyViT/models/tiny_vit.py:337-370](TinyViT/models/tiny_vit.py)

### Patch Merging for Downsampling

Between stages, TinyViT uses PatchMerging to reduce spatial resolution and increase channel dimensions:

```mermaid
flowchart LR
    subgraph "PatchMerging"
        Input["Input (B, H*W, C)"] --> Reshape["Reshape to (B, C, H, W)"]
        
        Reshape --> Conv1["Conv2d_BN (C→out_dim, 1×1)"]
        Conv1 --> Act1["Activation"]
        
        Act1 --> Conv2["Conv2d_BN (out_dim→out_dim, 3×3, stride=2, groups=out_dim)"]
        Conv2 --> Act2["Activation"]
        
        Act2 --> Conv3["Conv2d_BN (out_dim→out_dim, 1×1)"]
        
        Conv3 --> FlattenTranspose["Flatten and Transpose"]
        
        FlattenTranspose --> Output["Output (B, H*W/4, out_dim)"]
    end
```

Sources: [TinyViT/models/tiny_vit.py:125-151](TinyViT/models/tiny_vit.py)

## Model Variants

TinyViT comes in several variants with different parameter counts and configurations:

| Model | Parameters | Embed Dims | Depths | Num Heads | Window Sizes |
|-------|------------|------------|--------|-----------|--------------|
| TinyViT-5M | 5.4M | [64, 128, 160, 320] | [2, 2, 6, 2] | [2, 4, 5, 10] | [7, 7, 14, 7] |
| TinyViT-11M | 11M | [64, 128, 256, 448] | [2, 2, 6, 2] | [2, 4, 8, 14] | [7, 7, 14, 7] |
| TinyViT-21M | 21M | [96, 192, 384, 576] | [2, 2, 6, 2] | [3, 6, 12, 18] | [7, 7, 14, 7] |
| TinyViT-21M-384 | 21M | [96, 192, 384, 576] | [2, 2, 6, 2] | [3, 6, 12, 18] | [12, 12, 24, 12] |
| TinyViT-21M-512 | 21M | [96, 192, 384, 576] | [2, 2, 6, 2] | [3, 6, 12, 18] | [16, 16, 32, 16] |

Sources: [TinyViT/models/tiny_vit.py:641-704](TinyViT/models/tiny_vit.py), [TinyViT/README.md:50-60](TinyViT/README.md)

## Implementation and Usage

The TinyViT model is implemented in the `TinyViT` class found in [TinyViT/models/tiny_vit.py](TinyViT/models/tiny_vit.py). To use a pre-trained TinyViT model for inference:

```python
from models.tiny_vit import tiny_vit_21m_224
model = tiny_vit_21m_224(pretrained=True)

# For inference
model.eval()
output = model(image)  # image shape: [B, 3, 224, 224]
```

The main forward pass of the model consists of the following steps:

1. Patch embedding to convert image into tokens
2. Processing through the 4 stages with different block types
3. Global average pooling of features
4. Normalization and classification

Sources: [TinyViT/models/tiny_vit.py:572-591](TinyViT/models/tiny_vit.py), [TinyViT/inference.py:1-34](TinyViT/inference.py)

## Layer-by-Layer Forward Pass

The following diagram illustrates the detailed forward pass through a TinyViT model, showing the transformation of input data dimensions at each stage:

```mermaid
flowchart TD
    Input["Input Image
    (B, 3, H, W)"] --> PatchEmbed["PatchEmbed
    (B, embed_dims[0], H/4, W/4)"]
    
    PatchEmbed --> ConvLayer["Stage 1: ConvLayer
    (B, embed_dims[0], H/4, W/4)"]
    
    ConvLayer --> PatchMerge1["PatchMerging
    (B, H/8 * W/8, embed_dims[1])"]
    
    PatchMerge1 --> BasicLayer1["Stage 2: BasicLayer
    (B, H/8 * W/8, embed_dims[1])"]
    
    BasicLayer1 --> PatchMerge2["PatchMerging
    (B, H/16 * W/16, embed_dims[2])"]
    
    PatchMerge2 --> BasicLayer2["Stage 3: BasicLayer
    (B, H/16 * W/16, embed_dims[2])"]
    
    BasicLayer2 --> PatchMerge3["PatchMerging
    (B, H/32 * W/32, embed_dims[3])"]
    
    PatchMerge3 --> BasicLayer3["Stage 4: BasicLayer
    (B, H/32 * W/32, embed_dims[3])"]
    
    BasicLayer3 --> AvgPool["Global Average Pooling
    (B, embed_dims[3])"]
    
    AvgPool --> LayerNorm["LayerNorm
    (B, embed_dims[3])"]
    
    LayerNorm --> Linear["Linear Classifier
    (B, num_classes)"]
```

Sources: [TinyViT/models/tiny_vit.py:572-591](TinyViT/models/tiny_vit.py)

## Layer Construction

TinyViT dynamically constructs its layers based on the model variant specifications. The initialization process builds each stage with the appropriate number of blocks and configurations:

```mermaid
flowchart LR
    subgraph "TinyViT Initialization"
        Init["__init__"] --> CreatePatchEmbed["Create PatchEmbed"]
        
        CreatePatchEmbed --> BuildLayers["Build Layers Loop"]
        
        BuildLayers --> Stage1["Create Stage 1:
        ConvLayer with MBConv blocks"]
        
        BuildLayers --> Stage2["Create Stage 2:
        BasicLayer with TinyViTBlocks"]
        
        BuildLayers --> Stage3["Create Stage 3:
        BasicLayer with TinyViTBlocks"]
        
        BuildLayers --> Stage4["Create Stage 4:
        BasicLayer with TinyViTBlocks"]
        
        Stage1 --> CreateHead["Create Classifier Head"]
        Stage2 --> CreateHead
        Stage3 --> CreateHead
        Stage4 --> CreateHead
        
        CreateHead --> InitWeights["Initialize Weights"]
        
        InitWeights --> SetLayerLR["Set Layer-wise
        Learning Rate Decay"]
    end
```

Sources: [TinyViT/models/tiny_vit.py:454-558](TinyViT/models/tiny_vit.py)

## Conclusion

TinyViT is a highly efficient vision transformer architecture that achieves strong performance with a small parameter count. Its hierarchical design, with specialized blocks at different stages, enables it to process visual information efficiently while maintaining high accuracy. The model incorporates several innovations like window-based attention, a hybrid architecture with MBConv blocks, and an efficient downsampling strategy.

The architecture has been demonstrated to achieve up to 84.8% top-1 accuracy on ImageNet-1k with just 21M parameters, and even higher accuracy (86.5%) at higher resolutions.

Sources: [TinyViT/README.md:1-27](TinyViT/README.md), [TinyViT/models/tiny_vit.py](TinyViT/models/tiny_vit.py)

---

