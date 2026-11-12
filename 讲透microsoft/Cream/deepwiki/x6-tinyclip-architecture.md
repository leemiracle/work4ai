<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Cream · extra page TinyCLIP Architecture · fetched 2026-10-26 -->

# TinyCLIP Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [TinyCLIP/README.md](TinyCLIP/README.md)
- [TinyCLIP/script/auto_weight_inherit_50to25.sh](TinyCLIP/script/auto_weight_inherit_50to25.sh)
- [TinyCLIP/script/auto_weight_inherit_75to50.sh](TinyCLIP/script/auto_weight_inherit_75to50.sh)
- [TinyCLIP/src/open_clip/model.py](TinyCLIP/src/open_clip/model.py)
- [TinyCLIP/src/open_clip/resnet.py](TinyCLIP/src/open_clip/resnet.py)
- [TinyCLIP/src/open_clip/weight_inherit.py](TinyCLIP/src/open_clip/weight_inherit.py)
- [TinyCLIP/src/training/data.py](TinyCLIP/src/training/data.py)
- [TinyCLIP/src/training/main.py](TinyCLIP/src/training/main.py)
- [TinyCLIP/src/training/main_for_test.py](TinyCLIP/src/training/main_for_test.py)
- [TinyCLIP/src/training/optimizer.py](TinyCLIP/src/training/optimizer.py)
- [TinyCLIP/src/training/train.py](TinyCLIP/src/training/train.py)

</details>



This document provides a detailed technical explanation of the TinyCLIP architecture, focusing on the model structure, components, and their relationships. TinyCLIP is a distilled version of CLIP (Contrastive Language-Image Pre-training) that achieves comparable performance with significantly reduced model size and increased inference speed through two key techniques: affinity mimicking and weight inheritance. For information about the training process, see [TinyCLIP Training System](#2.2.2). For details on affinity mimicking and weight inheritance techniques, see [Affinity Mimicking & Weight Inheritance](#2.2.3).

## 1. Overview

TinyCLIP follows the dual-encoder architecture of CLIP, consisting of an image encoder and a text encoder that project images and text into a shared embedding space. The architecture is designed for efficiency while maintaining strong cross-modal understanding.

```mermaid
flowchart LR
    subgraph "TinyCLIP Architecture"
        direction TB
        image["Image Input"]
        text["Text Input"]
        
        subgraph "Image Encoder"
            direction TB
            img_enc["ImageEncoder"]
            vision["VisualTransformer/ModifiedResNet"]
            img_enc --> vision
        end
        
        subgraph "Text Encoder"
            direction TB
            txt_enc["TextEncoder"]
            transformer["Transformer"]
            tokenizer["Token Embedding"]
            txt_enc --> tokenizer
            txt_enc --> transformer
        end
        
        image --> img_enc
        text --> txt_enc
        
        img_feat["Image Features"]
        txt_feat["Text Features"]
        
        img_enc --> img_feat
        txt_enc --> txt_feat
        
        img_feat --> similarity["Cosine Similarity"]
        txt_feat --> similarity
        
        logit_scale["Logit Scale\n(Temperature)"] --> similarity
        
        similarity --> output["Normalized Scores"]
    end
```

Sources: [TinyCLIP/README.md:1-39](). [TinyCLIP/src/open_clip/model.py:592-680](), [TinyCLIP/src/open_clip/model.py:682-819]()

## 2. Image Encoder Architecture

TinyCLIP supports two types of image encoders: Vision Transformer (ViT) and Modified ResNet. The image encoder transforms input images into fixed-dimensional feature vectors.

### 2.1 Vision Transformer (ViT) Architecture

The ViT architecture in TinyCLIP follows the standard Vision Transformer design with modifications for efficiency:

```mermaid
flowchart TD
    subgraph "VisualTransformer"
        direction TB
        input["Image (3×224×224)"]
        patches["Patch Embedding\n(conv1)"]
        cls_token["Class Token\n(class_embedding)"]
        pos_embed["Positional Embedding\n(positional_embedding)"]
        
        transformer_blocks["Transformer Blocks\n(n layers)"]
        
        subgraph "Transformer Block"
            direction TB
            ln1["LayerNorm (ln_pre)"]
            attn["Multi-Head Attention\n(ResidualAttentionBlock)"]
            ln2["LayerNorm (ln_2)"]
            mlp["MLP\n(c_fc, GELU, c_proj)"]
            residual1["+ (Residual)"]
            residual2["+ (Residual)"]
            
            ln1 --> attn --> residual1
            attn_skip["Skip Connection"] --> residual1
            residual1 --> ln2 --> mlp --> residual2
            mlp_skip["Skip Connection"] --> residual2
        end
        
        ln_post["LayerNorm (ln_post)"]
        projection["Linear Projection\n(proj)"]
        
        input --> patches
        patches --> transformer_input["Transformer Input"]
        cls_token --> transformer_input
        pos_embed --> transformer_input
        
        transformer_input --> transformer_blocks
        transformer_blocks --> select_cls["Select Class Token"]
        select_cls --> ln_post --> projection --> output["Image Embeddings"]
    end
```

Sources: [TinyCLIP/src/open_clip/model.py:442-566]()

### 2.2 Modified ResNet Architecture

An alternative to ViT is the Modified ResNet, which is more efficient for smaller model sizes:

```mermaid
flowchart TD
    subgraph "ModifiedResNet"
        direction TB
        input["Image (3×224×224)"]
        
        subgraph "3-layer Stem"
            conv1["Conv2d (3→width/2)"]
            bn1["BatchNorm2d"]
            act1["ReLU"]
            conv2["Conv2d (width/2→width/2)"]
            bn2["BatchNorm2d"]
            act2["ReLU"]
            conv3["Conv2d (width/2→width)"]
            bn3["BatchNorm2d"]
            act3["ReLU"]
            avgpool["AvgPool2d (2×2)"]
            
            conv1 --> bn1 --> act1
            act1 --> conv2 --> bn2 --> act2
            act2 --> conv3 --> bn3 --> act3
            act3 --> avgpool
        end
        
        layer1["Layer1 (Bottleneck×n)"]
        layer2["Layer2 (Bottleneck×n)"]
        layer3["Layer3 (Bottleneck×n)"]
        layer4["Layer4 (Bottleneck×n)"]
        
        attnpool["AttentionPool2d"]
        
        avgpool --> layer1 --> layer2 --> layer3 --> layer4 --> attnpool --> output["Image Embeddings"]
    end
```

Sources: [TinyCLIP/src/open_clip/resnet.py:96-187]()

### 2.3 Image Encoder Variants

TinyCLIP offers several image encoder variants with different parameter counts:

| Model | Type | Parameters | Image Size | Patch Size | Width | Heads |
|-------|------|------------|------------|------------|-------|-------|
| ViT-39M/16 | ViT | 39M | 224 | 16 | 512 | 8 |
| ViT-8M/16 | ViT | 8M | 224 | 16 | 256 | 4 |
| ResNet-30M | ResNet | 30M | 224 | - | 64 | - |
| ResNet-19M | ResNet | 19M | 224 | - | 64 | - |
| ViT-61M/32 | ViT | 61M | 224 | 32 | 768 | 12 |
| ViT-40M/32 | ViT | 40M | 224 | 32 | 512 | 8 |

Sources: [TinyCLIP/README.md:25-38]()

## 3. Text Encoder Architecture

The text encoder in TinyCLIP is a transformer-based model that processes tokenized text:

```mermaid
flowchart TD
    subgraph "TextEncoder"
        direction TB
        input["Text Tokens"]
        token_embed["Token Embedding\n(token_embedding)"]
        pos_embed["Positional Embedding\n(positional_embedding)"]
        
        transformer_blocks["Transformer Blocks\n(n layers)"]
        
        subgraph "Transformer Block"
            direction TB
            ln1["LayerNorm"]
            attn["Multi-Head Self-Attention\n(heads=8)"]
            ln2["LayerNorm"]
            mlp["MLP\n(c_fc, GELU, c_proj)"]
            residual1["+ (Residual)"]
            residual2["+ (Residual)"]
            
            ln1 --> attn --> residual1
            attn_skip["Skip Connection"] --> residual1
            residual1 --> ln2 --> mlp --> residual2
            mlp_skip["Skip Connection"] --> residual2
        end
        
        ln_final["LayerNorm (ln_final)"]
        projection["Linear Projection\n(text_projection)"]
        
        input --> token_embed --> embeddings["Embeddings"]
        pos_embed --> embeddings
        embeddings --> transformer_blocks
        transformer_blocks --> select_eot["Select EOT Token Features"]
        select_eot --> ln_final --> projection --> output["Text Embeddings"]
    end
```

Sources: [TinyCLIP/src/open_clip/model.py:342-433](), [TinyCLIP/src/open_clip/model.py:682-819]()

### 3.1 Text Encoder Variants

TinyCLIP offers several text encoder variants with different parameter counts:

| Model | Parameters | Context Length | Width | Heads | Layers |
|-------|------------|----------------|-------|-------|--------|
| Text-29M | 29M | 77 | 512 | 8 | 12 |
| Text-19M | 19M | 77 | 384 | 6 | 12 |
| Text-3M | 3M | 77 | 256 | 4 | 6 |

Sources: [TinyCLIP/README.md:25-38]()

## 4. Weight Inheritance Mechanism

Weight inheritance is a key innovation in TinyCLIP that enables the smaller model to leverage knowledge from larger pre-trained models. This process requires careful handling of architectural differences.

```mermaid
flowchart LR
    subgraph "Weight Inheritance Process"
        direction TB
        teacher["Teacher Model\n(e.g., ViT-B/32)"]
        student["Student Model\n(e.g., TinyCLIP ViT-45M/32)"]
        
        teacher_weights["Teacher Weights"]
        student_weights["Student Weights"]
        
        teacher --> teacher_weights
        
        subgraph "weight_inherit Function"
            direction TB
            get_depth["Extract Layer Structure"]
            remap["Remap Depth\n(interval_front)"]
            prune["Prune Parameters\nto Fit Student"]
            update["Update Student State Dict"]
        end
        
        teacher_weights --> get_depth
        get_depth --> remap --> prune --> update
        update --> student_weights
        student_weights --> student
    end
```

Sources: [TinyCLIP/src/open_clip/weight_inherit.py:71-138](), [TinyCLIP/src/training/main.py:422-467]()

### 4.1 Manual vs Automatic Weight Inheritance

TinyCLIP supports both manual and automatic weight inheritance:

- **Manual Inheritance**: Predefined configurations for inheriting weights from a larger model
- **Automatic Inheritance**: Automated process that determines optimal inheritance patterns

```mermaid
flowchart LR
    subgraph "Weight Inheritance Types"
        direction TB
        
        subgraph "Manual Inheritance"
            manual_config["Predefined Configuration"]
            manual_inherit["weight_inherit Function"]
            manual_config --> manual_inherit
        end
        
        subgraph "Automatic Inheritance"
            auto_target["Target Sparsity\n(e.g., 50% or 75%)"]
            prune_step["Pruning Step"]
            l0_module["L0Module for Pruning"]
            
            auto_target --> l0_module
            prune_step --> l0_module
        end
        
        manual_inherit --> student["Student Model"]
        l0_module --> student
    end
```

Sources: [TinyCLIP/script/auto_weight_inherit_50to25.sh:1-37](), [TinyCLIP/script/auto_weight_inherit_75to50.sh:1-37]()

## 5. Model Integration and Component Interaction

The complete TinyCLIP architecture integrates the image encoder, text encoder, and contrastive learning components through a unified training framework:

```mermaid
flowchart TD
    subgraph "TinyCLIP Integration"
        direction TB
        
        image["Image"]
        text["Text"]
        
        image_encoder["ImageEncoder Class\n(visual: VisualTransformer/ModifiedResNet)"]
        text_encoder["TextEncoder Class\n(transformer: Transformer)"]
        
        image --> image_encoder
        text --> text_encoder
        
        image_features["Image Features"]
        text_features["Text Features"]
        
        image_encoder --> image_features
        text_encoder --> text_features
        
        subgraph "Contrastive Learning"
            direction TB
            normalize["F.normalize"]
            logit_scale["logit_scale (Temperature)"]
            similarity["Cosine Similarity"]
            
            normalize --> similarity
            logit_scale --> similarity
        end
        
        image_features --> normalize
        text_features --> normalize
        similarity --> loss["ClipLoss / ClipSoftLoss"]
        
        subgraph "Affinity Mimicking"
            direction TB
            teacher_outputs["Teacher Model Outputs"]
            student_outputs["Student Model Outputs"]
            
            teacher_outputs --> soft_loss["Soft Distillation Loss"]
            student_outputs --> soft_loss
        end
        
        loss --> total_loss["Total Loss"]
        soft_loss --> total_loss
    end
```

Sources: [TinyCLIP/src/training/train.py:160-205](), [TinyCLIP/src/open_clip/model.py:595-675](), [TinyCLIP/src/open_clip/model.py:682-819]()

## 6. Architecture Configuration and Hyperparameters

TinyCLIP models are configured with a set of hyperparameters that define their architecture:

| Parameter | Description | Example Values |
|-----------|-------------|---------------|
| width | Base dimension of the model | 256, 384, 512, 768 |
| layers | Number of transformer layers | 6, 12 |
| heads | Number of attention heads | 4, 6, 8, 12 |
| mlp_ratio | Multiplier for MLP hidden dimension | 4.0 |
| patch_size | Size of image patches (ViT only) | 16, 32 |
| image_size | Input image resolution | 224 |
| context_length | Maximum text sequence length | 77 |
| vocab_size | Size of the text vocabulary | 49408 |

Sources: [TinyCLIP/src/open_clip/model.py:569-594]()

## 7. Model Variants and Performance

TinyCLIP offers various model configurations that balance efficiency and performance:

| Model | Image Encoder | Text Encoder | ImageNet-1K | MACs(G) | Throughput (pairs/s) |
|-------|---------------|--------------|-------------|---------|---------------------|
| TinyCLIP ViT-39M/16 Text-19M | ViT-39M/16 | Text-19M | 63.5% | 9.5 | 1,469 |
| TinyCLIP ViT-8M/16 Text-3M | ViT-8M/16 | Text-3M | 41.1% | 2.0 | 4,150 |
| TinyCLIP ResNet-30M Text-29M | ResNet-30M | Text-29M | 59.1% | 6.9 | 1,811 |
| TinyCLIP ResNet-19M Text-19M | ResNet-19M | Text-19M | 56.4% | 4.4 | 3,024 |
| TinyCLIP ViT-61M/32 Text-29M | ViT-61M/32 | Text-29M | 62.4% | 5.3 | 3,191 |
| TinyCLIP ViT-40M/32 Text-19M | ViT-40M/32 | Text-19M | 59.8% | 3.5 | 4,641 |
| TinyCLIP ViT-63M/32 Text-31M (auto) | ViT-63M/32 | Text-31M | 63.9% | 5.6 | 2,905 |
| TinyCLIP ViT-45M/32 Text-18M (auto) | ViT-45M/32 | Text-18M | 61.4% | 3.7 | 3,682 |

Sources: [TinyCLIP/README.md:25-38]()

## 8. Key Architectural Components

The TinyCLIP architecture builds on several core components, each with specific architectural details:

### 8.1 Transformer Block

The transformer block is the fundamental building block for both vision and text transformers:

```mermaid
flowchart TD
    subgraph "ResidualAttentionBlock"
        direction TB
        input["Input"]
        ln_1["LayerNorm (ln_1)"]
        attn["MultiheadAttention (attn)"]
        
        ln_2["LayerNorm (ln_2)"]
        mlp["MLP (mlp)"]
        
        input --> |"+ Residual"| attn_out["Attention Output"]
        input --> ln_1 --> attn --> attn_out
        
        attn_out --> |"+ Residual"| mlp_out["MLP Output"] 
        attn_out --> ln_2 --> mlp --> mlp_out
    end
```

Sources: [TinyCLIP/src/open_clip/model.py:208-339]()

### 8.2 MLP Block

The MLP module consists of two linear layers with a non-linearity:

```mermaid
flowchart LR
    subgraph "Mlp"
        direction LR
        input["Input (d_model)"]
        c_fc["Linear (c_fc)\nd_model → mlp_width"]
        gelu["GELU Activation"]
        c_proj["Linear (c_proj)\nmlp_width → d_model"]
        output["Output (d_model)"]
        
        input --> c_fc --> gelu --> c_proj --> output
    end
```

Sources: [TinyCLIP/src/open_clip/model.py:108-137]()

### 8.3 Optimizer Configuration

TinyCLIP uses specialized optimizer configurations for different model components:

```mermaid
flowchart TD
    subgraph "Optimizer Structure"
        direction TB
        model["TinyCLIP Model"]
        
        subgraph "Optimizers"
            direction TB
            img_opt["Image Encoder Optimizer"]
            txt_opt["Text Encoder Optimizer"]
            joint_opt["Joint Components Optimizer"]
            l0_opt["L0 Module Optimizer\n(for pruning)"]
        end
        
        model --> separate["Separate Parameter Groups"]
        separate --> img_params["Image Parameters"]
        separate --> txt_params["Text Parameters"]
        separate --> joint_params["Joint Parameters"]
        separate --> l0_params["L0 Module Parameters"]
        
        img_params --> img_opt
        txt_params --> txt_opt
        joint_params --> joint_opt
        l0_params --> l0_opt
    end
```

Sources: [TinyCLIP/src/training/optimizer.py:22-101]()

---

