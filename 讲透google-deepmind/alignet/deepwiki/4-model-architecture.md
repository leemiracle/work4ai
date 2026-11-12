<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/alignet · page 4 Model Architecture · fetched 2026-10-26 -->

# Model Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [bv_vit.py](bv_vit.py)
- [bv_wrapper.py](bv_wrapper.py)

</details>



## Purpose and Scope

This document provides comprehensive documentation of the Vision Transformer (ViT) architecture used in AligNet, including the core model implementation, component structure, and integration with the Kauldron training framework. 

For details on specific components like `Encoder1DBlock` and `MAPHead`, see [Model Components](#4.2). For configuration of model variants (B/16, L/16, etc.), see [Model Variants and Configuration](#4.3). For checkpoint loading and management, see [Checkpoint Management](#5). For training configuration using these models, see [Training System](#6).

**Sources:** [README.md:1-31](), [bv_vit.py:1-21](), [bv_wrapper.py:16-19]()

## Overview

The AligNet model architecture consists of three layers:

1. **Core Vision Transformer** (`bv_vit.py`): A flexible ViT implementation forked from Big Vision
2. **Kauldron Integration Wrappers** (`bv_wrapper.py`): Classes that bridge Big Vision models to the Kauldron training framework
3. **Triplet-Specific Extensions**: Additional heads and modifications for triplet learning

The architecture supports 8 different pre-trained base models (SigLIP, DINOv2, ViT, etc.) and can be configured for various input resolutions and model scales.

**Sources:** [bv_vit.py:16-21](), [bv_wrapper.py:16-19](), [README.md:161-171]()

## Architecture Diagram: Complete Model Stack

```mermaid
graph TB
    subgraph Input["Input Layer"]
        IMG["images: Float[B, 224, 224, 3]"]
    end
    
    subgraph CoreViT["Core Vision Transformer (bv_vit.py)"]
        PATCH["nn.Conv<br/>patch_size=(16,16)<br/>→ embedding"]
        POSEMB["pos_embedding<br/>learn or sincos2d"]
        ENCODER["Encoder<br/>depth=12<br/>num_heads=12"]
        POOL["Pooling Layer<br/>gap/map/tok/0"]
        REPR["pre_logits representation"]
    end
    
    subgraph Heads["Classification Heads"]
        I1K_HEAD["nn.Dense(1000)<br/>ImageNet head"]
        TRIPLET_HEAD["nn.Dense(1024)<br/>triplet_head"]
    end
    
    subgraph Wrapper["Kauldron Integration (bv_wrapper.py)"]
        MODEL_WRAP["Model<br/>nn.Module wrapper"]
        TRIPLET_WRAP["TripletWrapper<br/>Adds triplet_head<br/>Handles batch reshaping"]
    end
    
    subgraph Output["Model Outputs"]
        LOGITS["logits: Float[B, 1000]"]
        PRE_LOGITS["pre_logits: Float[B, 768]"]
        TRIPLET_LOGITS["triplet_logits: Float[B, 1024]"]
    end
    
    IMG --> PATCH
    PATCH --> POSEMB
    POSEMB --> ENCODER
    ENCODER --> POOL
    POOL --> REPR
    
    REPR --> I1K_HEAD
    REPR --> TRIPLET_HEAD
    
    I1K_HEAD --> LOGITS
    REPR --> PRE_LOGITS
    TRIPLET_HEAD --> TRIPLET_LOGITS
    
    MODEL_WRAP -.wraps.-> PATCH
    TRIPLET_WRAP -.wraps.-> MODEL_WRAP
    TRIPLET_WRAP -.adds.-> TRIPLET_HEAD
```

**Sources:** [bv_vit.py:212-309](), [bv_wrapper.py:38-163]()

## Core Vision Transformer Implementation

The `_Model` class in [bv_vit.py:212-309]() implements a standard Vision Transformer with configurable components. The model processes images through the following stages:

### Forward Pass Flow

```mermaid
graph LR
    subgraph InputProcessing["Input Processing"]
        INPUT["image<br/>Float[B,H,W,3]"]
        CONV["nn.Conv<br/>embedding<br/>stride=patch_size"]
        RESHAPE["Reshape<br/>[B,h*w,width]"]
        POSEMB_ADD["Add pos_embedding<br/>[1,h*w,width]"]
    end
    
    subgraph TransformerStack["Transformer Encoder"]
        DROP1["nn.Dropout<br/>rate=dropout"]
        ENC["Encoder<br/>depth layers of<br/>Encoder1DBlock"]
        NORM["LayerNorm<br/>encoder_norm"]
    end
    
    subgraph PoolingOptions["Pooling Strategy"]
        MAP["MAPHead<br/>Attention pooling"]
        GAP["Mean pooling<br/>axis=1"]
        TOK["Select [:, 0]<br/>CLS token"]
        ZERO["Select [:, 0]<br/>First token"]
    end
    
    subgraph OutputStage["Output Stage"]
        REPR["pre_logits<br/>Float[B,width]"]
        HEAD["nn.Dense<br/>num_classes"]
        OUT["logits<br/>Float[B,num_classes]"]
    end
    
    INPUT --> CONV
    CONV --> RESHAPE
    RESHAPE --> POSEMB_ADD
    POSEMB_ADD --> DROP1
    DROP1 --> ENC
    ENC --> NORM
    
    NORM --> MAP
    NORM --> GAP
    NORM --> TOK
    NORM --> ZERO
    
    MAP --> REPR
    GAP --> REPR
    TOK --> REPR
    ZERO --> REPR
    
    REPR --> HEAD
    HEAD --> OUT
```

**Sources:** [bv_vit.py:232-309]()

### Model Configuration Parameters

The `_Model` class accepts the following key parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `num_classes` | `Optional[int]` | `None` | Number of output classes; if `None`, no classification head |
| `patch_size` | `Sequence[int]` | `(16, 16)` | Size of image patches |
| `width` | `int` | `768` | Hidden dimension width |
| `depth` | `int` | `12` | Number of transformer layers |
| `mlp_dim` | `Optional[int]` | `None` | MLP hidden dimension (defaults to 4×width) |
| `num_heads` | `int` | `12` | Number of attention heads |
| `posemb` | `str` | `"learn"` | Position embedding type: `"learn"` or `"sincos2d"` |
| `pool_type` | `str` | `"gap"` | Pooling strategy: `"gap"`, `"map"`, `"tok"`, `"0"`, or `"none"` |
| `scan` | `bool` | `False` | Use `lax.scan` for memory-efficient encoder |
| `dtype_mm` | `str` | `"float32"` | Data type for matrix multiplication |
| `dropout` | `float` | `0.0` | Dropout rate |

**Sources:** [bv_vit.py:212-229]()

## Pooling Strategies

The model supports multiple pooling strategies defined by the `pool_type` parameter in [bv_vit.py:274-288]():

```mermaid
graph TD
    ENCODED["Encoded tokens<br/>Float[B, L, width]"]
    
    ENCODED -->|"pool_type='map'"| MAP["MAPHead<br/>Attention pooling<br/>→ Float[B, width]"]
    ENCODED -->|"pool_type='gap'"| GAP["jnp.mean(x, axis=1)<br/>Global average pooling<br/>→ Float[B, width]"]
    ENCODED -->|"pool_type='0'"| ZERO["x[:, 0]<br/>First token<br/>→ Float[B, width]"]
    ENCODED -->|"pool_type='tok'"| TOK["x[:, 0]<br/>CLS token<br/>→ Float[B, width]"]
    ENCODED -->|"pool_type='none'"| NONE["No pooling<br/>→ Float[B, L, width]"]
    
    MAP --> OUTPUT["head_input"]
    GAP --> OUTPUT
    ZERO --> OUTPUT
    TOK --> OUTPUT
    NONE --> OUTPUT
```

The `"map"` strategy uses `MAPHead` (Multi-head Attention Pooling) defined in [bv_vit.py:187-210](). This learnable attention-based pooling is particularly effective for fine-grained tasks.

**Sources:** [bv_vit.py:274-288](), [bv_vit.py:187-210]()

## Kauldron Integration

The [bv_wrapper.py]() module provides three classes that integrate Big Vision models with Kauldron:

### Integration Class Hierarchy

```mermaid
graph TB
    subgraph KauldronBase["Kauldron Framework"]
        NN_MODULE["nn.Module<br/>Flax base class"]
        PARTIAL_LOADER["kd.ckpts.AbstractPartialLoader<br/>Checkpoint loading interface"]
    end
    
    subgraph WrapperClasses["bv_wrapper.py Classes"]
        MODEL["Model<br/>Basic nn.Module wrapper"]
        LOADER["Loader<br/>Pretrained weight loader"]
        TRIPLET["TripletWrapper<br/>Triplet-specific wrapper"]
    end
    
    subgraph CoreModel["bv_vit.py"]
        BV_MODEL["bv_vit.Model<br/>Core ViT implementation"]
    end
    
    NN_MODULE -.inherits.-> MODEL
    NN_MODULE -.inherits.-> TRIPLET
    PARTIAL_LOADER -.inherits.-> LOADER
    
    MODEL -->|"instantiates"| BV_MODEL
    TRIPLET -->|"wraps"| MODEL
    LOADER -->|"loads weights into"| MODEL
```

**Sources:** [bv_wrapper.py:38-163]()

### Model Wrapper

The `Model` class [bv_wrapper.py:38-54]() provides a simple Kauldron-compatible wrapper:

```python
class Model(nn.Module):
  variant: str = "B/16"
  model_kwargs: dict[str, Any] = dataclasses.field(default_factory=dict)
  image: Optional[kd.kontext.Key] = kd.kontext.REQUIRED
  is_training = kd.nn.train_property()
```

This wrapper:
- Instantiates `bv_vit.Model` with specified variant and kwargs
- Integrates with Kauldron's context system via `kd.kontext.Key`
- Returns a dictionary containing `logits` and intermediate outputs

**Sources:** [bv_wrapper.py:38-54]()

### Loader for Pretrained Weights

The `Loader` class [bv_wrapper.py:57-107]() implements `kd.ckpts.AbstractPartialLoader` to load pretrained weights:

| Attribute | Type | Description |
|-----------|------|-------------|
| `init_file` | `str` | Path to checkpoint file or vanity name |
| `dont_load` | `Optional[Sequence[str]]` | Parameter patterns to skip loading |
| `prefix` | `Optional[str]` | Prefix path in state dict |

The `transform()` method [bv_wrapper.py:65-107]() performs:
1. Extracts initialized parameters from state
2. Loads pretrained checkpoint using `bv_utils.load_params()`
3. Converts scan-style checkpoints to pyloop format (Kauldron requirement)
4. Merges parameters according to `dont_load` patterns
5. Resamples positional embeddings if resolution differs
6. Removes device sharding from loaded parameters

**Sources:** [bv_wrapper.py:57-107]()

### TripletWrapper for Triplet Learning

The `TripletWrapper` class [bv_wrapper.py:118-162]() adds triplet-specific functionality:

```mermaid
graph LR
    subgraph Input
        TRIPLET_IMG["image<br/>Float[B, 3, 224, 224, 3]<br/>Triplets of images"]
    end
    
    subgraph Processing["TripletWrapper Processing"]
        FLATTEN["einops.rearrange<br/>(...) h w c → (B*3) h w c"]
        MODEL_CALL["self.model(flat_images)<br/>Forward through base model"]
        GAP_OPT["Optional GAP<br/>if self.gap=True"]
        STOP_GRAD["Optional stop_gradient<br/>if self.stop_grad=True"]
        TRIPLET_HEAD["nn.Dense(out_features)<br/>name='triplet_head'"]
        RESHAPE["Reshape back<br/>(B*3) → B 3"]
    end
    
    subgraph Output["TripletOutput TypedDict"]
        OUT_LOGITS["logits: Float[B, 3, 1000]"]
        OUT_PRE["pre_logits: Float[B, 3, hidden]"]
        OUT_TRIPLET["triplet_logits: Float[B, 3, 1024]"]
    end
    
    TRIPLET_IMG --> FLATTEN
    FLATTEN --> MODEL_CALL
    MODEL_CALL --> GAP_OPT
    GAP_OPT --> STOP_GRAD
    STOP_GRAD --> TRIPLET_HEAD
    TRIPLET_HEAD --> RESHAPE
    
    RESHAPE --> OUT_LOGITS
    RESHAPE --> OUT_PRE
    RESHAPE --> OUT_TRIPLET
```

Key parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | `nn.Module` | Required | Base model to wrap |
| `out_features` | `int` | `1024` | Dimension of triplet head output |
| `stop_grad` | `bool` | `False` | Apply gradient stopping to pre_logits |
| `gap` | `bool` | `False` | Add global average pooling before head |

The wrapper handles batch dimension manipulation to process triplets efficiently: it flattens triplet batches before the forward pass and reshapes them back afterward.

**Sources:** [bv_wrapper.py:118-162]()

## Model Output Structure

Both wrappers return dictionaries with consistent output formats:

### Model Output Keys

```mermaid
graph TB
    subgraph MainOutputs["Primary Outputs"]
        LOGITS["logits<br/>Float[B, num_classes]<br/>ImageNet classification"]
        PRE_LOGITS["pre_logits<br/>Float[B, width]<br/>Final embeddings"]
        TRIPLET_LOGITS["triplet_logits<br/>Float[B, out_features]<br/>Triplet task head"]
    end
    
    subgraph IntermediateOutputs["Intermediate Outputs (from _Model)"]
        STEM["stem<br/>Patch embeddings"]
        WITH_POSEMB["with_posemb<br/>After adding pos_embedding"]
        ENCODER_OUT["encoder<br/>Dict of layer outputs"]
        ENCODED["encoded<br/>Final encoder output"]
        HEAD_INPUT["head_input<br/>After pooling"]
        PRE_LOGITS_2D["pre_logits_2d<br/>2D spatial representation"]
    end
    
    LOGITS -.primary.-> MainOutputs
    PRE_LOGITS -.primary.-> MainOutputs
    TRIPLET_LOGITS -.added by TripletWrapper.-> MainOutputs
```

The `encoder` output contains per-layer information with keys like `"block00"`, `"block01"`, etc., each containing:
- `"sa"`: Self-attention output
- `"+sa"`: After residual connection
- `"mlp"`: MLP block output  
- `"+mlp"`: After residual connection

**Sources:** [bv_vit.py:232-309](), [bv_wrapper.py:110-116](), [bv_wrapper.py:129-162]()

## Encoder Implementation Modes

The `Encoder` class [bv_vit.py:129-184]() supports two implementation modes:

### Scan vs PyLoop Modes

```mermaid
graph TB
    subgraph ScanMode["scan=True: Memory Efficient"]
        SCAN_BLOCK["nn.remat(Encoder1DBlock)<br/>Rematerialization wrapper"]
        SCAN_CALL["nn.scan(..., length=depth)<br/>Scanned application"]
        SCAN_PARAMS["Variable axes: params: 0<br/>Stacked parameters"]
    end
    
    subgraph PyLoopMode["scan=False: Explicit Layers"]
        LOOP["for lyr in range(depth)"]
        BLOCK["Encoder1DBlock<br/>name=f'encoderblock_{lyr}'"]
        SEQUENTIAL["Sequential layer application"]
    end
    
    INPUT["x: Float[B, L, width]"]
    
    INPUT --> SCAN_BLOCK
    INPUT --> LOOP
    
    SCAN_BLOCK --> SCAN_CALL
    SCAN_CALL --> SCAN_PARAMS
    
    LOOP --> BLOCK
    BLOCK --> SEQUENTIAL
    
    SCAN_PARAMS --> OUTPUT["Encoded output"]
    SEQUENTIAL --> OUTPUT
```

**Scan mode** [bv_vit.py:145-169]():
- Uses `nn.scan` to apply a single `Encoder1DBlock` multiple times
- Stacks parameters along dimension 0
- Enables gradient checkpointing via `nn.remat`
- Reduces memory usage but requires parameter conversion for loading checkpoints

**PyLoop mode** [bv_vit.py:171-181]():
- Creates separate `Encoder1DBlock` instances for each layer
- Standard sequential execution
- Direct checkpoint compatibility
- Higher memory usage but simpler structure

The checkpoint conversion functions `pyloop_to_scan()` [bv_vit.py:458-482]() and `scan_to_pyloop()` [bv_vit.py:485-501]() handle parameter format conversion between modes.

**Sources:** [bv_vit.py:129-184](), [bv_vit.py:458-501]()

## Integration with Training Configuration

The model architecture is configured in training configs like [configs/siglip.py](). Example configuration:

```python
cfg.model = TripletWrapper(
    model=Model(
        variant="B/16",
        model_kwargs={
            "pool_type": "map",
            "rep_size": True,
            "out_features": 1024,
        },
    ),
    out_features=1024,
)

cfg.init_transform = Loader(
    init_file="SigLIP B/16 224",
    dont_load=("head", "triplet_head"),
)
```

This configuration:
1. Creates a Vision Transformer with variant "B/16" (Base model, 16×16 patches)
2. Uses MAP attention pooling
3. Adds a representation layer (`rep_size=True`)
4. Wraps with `TripletWrapper` adding a 1024-dim triplet head
5. Initializes from SigLIP checkpoint, excluding task-specific heads

**Sources:** [configs/siglip.py]() (referenced in diagrams), [bv_wrapper.py:38-163]()

## Summary of Key Components

| Component | File | Lines | Purpose |
|-----------|------|-------|---------|
| `_Model` | bv_vit.py | 212-309 | Core Vision Transformer implementation |
| `Encoder` | bv_vit.py | 129-184 | Transformer encoder stack |
| `Encoder1DBlock` | bv_vit.py | 91-126 | Single transformer block (MHSA + MLP) |
| `MlpBlock` | bv_vit.py | 66-88 | Feed-forward network block |
| `MAPHead` | bv_vit.py | 187-210 | Multi-head attention pooling |
| `Model` | bv_wrapper.py | 38-54 | Kauldron wrapper for ViT |
| `Loader` | bv_wrapper.py | 57-107 | Pretrained checkpoint loader |
| `TripletWrapper` | bv_wrapper.py | 118-162 | Triplet-specific model wrapper |
| `decode_variant()` | bv_vit.py | 317-392 | Convert variant strings to parameters |
| `resample_posemb()` | bv_vit.py | 395-410 | Resample positional embeddings |

**Sources:** [bv_vit.py:1-605](), [bv_wrapper.py:1-163]()

---

