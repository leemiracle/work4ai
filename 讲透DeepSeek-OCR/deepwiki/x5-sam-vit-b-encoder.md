<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/DeepSeek-OCR · extra page SAM ViT-B Encoder · fetched 2026-10-30 -->

# SAM ViT-B Encoder

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py](DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py)

</details>



## Purpose

This document provides a technical deep-dive into the SAM (Segment Anything Model) ViT-B encoder used in DeepSeek-OCR's vision encoding system. The SAM encoder is one of two parallel vision encoders (the other being CLIP-L, see [4.3.2]()) that process image inputs. The SAM encoder specializes in extracting spatially-aware, high-resolution features using window attention and relative positional embeddings, making it particularly effective for document understanding tasks that require precise spatial layout comprehension.

For information about how SAM and CLIP features are combined, see [4.3.3](). For the overall vision encoding pipeline, see [4.3]().

**Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:1-528]()

## Architecture Overview

The SAM ViT-B encoder is implemented as the `ImageEncoderViT` class [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:77-184]() and follows a Vision Transformer architecture adapted from Meta's Segment Anything Model. The encoder processes images through a hierarchical pipeline:

```mermaid
graph TD
    Input["Input Image<br/>(B, 3, H, W)"]
    PatchEmbed["PatchEmbed<br/>(DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:447)"]
    PosEmbed["Absolute Position Embedding<br/>(self.pos_embed)"]
    Blocks["12 Transformer Blocks<br/>(Block class: 186)"]
    Neck["Neck Module<br/>(self.neck: 148)"]
    Net2["net_2<br/>(Conv2d 256 to 512)"]
    Net3["net_3<br/>(Conv2d 512 to 1024)"]
    Output["Output Features<br/>(B, 1024, H/64, W/64)"]
    
    Input --> PatchEmbed
    PatchEmbed --> PosEmbed
    PosEmbed --> Blocks
    Blocks --> Neck
    Neck --> Net2
    Net2 --> Net3
    Net3 --> Output
```

**Key architectural parameters:**
| Parameter | Value | Description |
|-----------|-------|-------------|
| `img_size` | 1024 | Input image size [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:80]() |
| `patch_size` | 16 | Patch embedding kernel size [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:81]() |
| `embed_dim` | 768 | Transformer embedding dimension [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:83]() |
| `depth` | 12 | Number of transformer blocks [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:84]() |
| `num_heads` | 12 | Attention heads per block [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:85]() |
| `mlp_ratio` | 4.0 | MLP hidden dimension ratio [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:86]() |
| `window_size` | 14 | Window size for windowed attention [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:491]() |
| `global_attn_indexes` | [2, 5, 8, 11] | Blocks using global attention [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:492]() |

**Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:77-184](), [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:481-528]()

## Patch Embedding

The `PatchEmbed` class [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:447-478]() converts the input image into a sequence of patch embeddings using a convolutional projection:

```mermaid
graph LR
    Input["Image<br/>(B, 3, 1024, 1024)"]
    Conv["nn.Conv2d<br/>(proj: 465)"]
    Permute["Permute<br/>(B, H, W, C)"]
    Output["Patches<br/>(B, 64, 64, 768)"]
    
    Input --> Conv
    Conv --> Permute
    Permute --> Output
```

The patch embedding layer:
- Uses a `16×16` kernel with stride `16` to divide the `1024×1024` image into `64×64` patches [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:119-120]().
- Projects each 3-channel patch to a 768-dimensional embedding [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:122]().
- Outputs in `(B, H, W, C)` format, preserving spatial structure for subsequent processing [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:477]().

**Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:447-478](), [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:118-123]()

## Absolute Positional Embeddings

The encoder uses absolute positional embeddings to inject spatial information:

```python
# From ImageEncoderViT.__init__
self.pos_embed = nn.Parameter(
    torch.zeros(1, img_size // patch_size, img_size // patch_size, embed_dim)
)
```
[DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:128-130]()

**Adaptive interpolation:** The `get_abs_pos` function [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:19-38]() dynamically interpolates positional embeddings when the input image size differs from the pretrained size:

```mermaid
graph TD
    Check{"src_size == tgt_size?"}
    Direct["Return original pos_embed"]
    Permute["Permute to (B, C, H, W)"]
    Interp["F.interpolate<br/>(bicubic: 31)"]
    PermuteBack["Permute back to (B, H, W, C)"]
    
    Check -->|Yes| Direct
    Check -->|No| Permute
    Permute --> Interp
    Interp --> PermuteBack
```

This allows the model to handle variable image resolutions at inference time while maintaining spatial awareness learned during pretraining [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:173]().

**Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:19-38](), [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:125-130](), [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:171-173]()

## Transformer Block Structure

Each transformer block (`Block` class [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:186]()) implements a residual architecture with pre-normalization:

```mermaid
graph TD
    Input["x (B, H, W, C)"]
    Norm1["LayerNorm (norm1)"]
    WindowPart["window_partition<br/>(if window_size > 0)"]
    Attn["Attention (attn)"]
    WindowUnpart["window_unpartition<br/>(if window_size > 0)"]
    Add1["Residual Add"]
    Norm2["LayerNorm (norm2)"]
    MLP["MLPBlock (248)"]
    Add2["Residual Add"]
    Output["x (B, H, W, C)"]
    
    Input --> Norm1
    Norm1 --> WindowPart
    WindowPart --> Attn
    Attn --> WindowUnpart
    WindowUnpart --> Add1
    Input --> Add1
    Add1 --> Norm2
    Norm2 --> MLP
    MLP --> Add2
    Add1 --> Add2
    Add2 --> Output
```

**Block configuration:**
- 8 of 12 blocks use **windowed attention** with `window_size=14` [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:143]().
- 4 blocks (at indices 2, 5, 8, 11) use **global attention** with `window_size=0` [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:492]().
- All blocks use **relative positional embeddings** (`use_rel_pos=True`) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:490]().

**Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:186-249](), [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:43-56]()

## Window Attention Mechanism

Window attention partitions the spatial feature map into non-overlapping windows to reduce computational complexity:

```mermaid
graph TD
    subgraph "window_partition (326)"
        Input["Input x (B, H, W, C)"]
        Pad["Pad to window_size"]
        Reshape["Reshape (B, H/ws, ws, W/ws, ws, C)"]
        Permute["Permute (0,1,3,2,4,5)"]
        Windows["Windows (B*N, ws, ws, C)"]
        
        Input --> Pad
        Pad --> Reshape
        Reshape --> Permute
        Permute --> Windows
    end
    
    subgraph "window_unpartition (353)"
        WindowsIn["Windows (B*N, ws, ws, C)"]
        ReshapeBack["Reshape (B, H/ws, W/ws, ws, ws, C)"]
        PermuteBack["Permute (0,1,3,2,4,5)"]
        Unpad["Remove padding"]
        OutputUnpart["Output x (B, H, W, C)"]
        
        WindowsIn --> ReshapeBack
        ReshapeBack --> PermuteBack
        PermuteBack --> Unpad
        Unpad --> OutputUnpart
    end
```

**Example with `H=64, W=64, window_size=14`:**
- Padding: `64` is padded to `70` (multiple of 14) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:334-335]().
- Windows: Creates `5×5=25` windows per image [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:341]().
- After attention: `window_unpartition` restores original `(B, 64, 64, 768)` shape [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:371]().

**Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:326-372](), [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:233-244]()

## Relative Positional Embeddings

The `Attention` module [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:252]() uses **decomposed relative positional embeddings** that encode spatial relationships:

```mermaid
graph TD
    subgraph "Relative Position Encoding"
        RelH["rel_pos_h (2*H-1, head_dim)"]
        RelW["rel_pos_w (2*W-1, head_dim)"]
        Query["Query q (B, H, W, C)"]
        
        GetRelH["get_rel_pos (375)"]
        GetRelW["get_rel_pos (375)"]
        
        EinsumH["add_decomposed_rel_pos (410)"]
        EinsumW["add_decomposed_rel_pos (410)"]
        
        Combine["Combine rel_h + rel_w"]
        AttnBias["Attention Bias (444)"]
        
        RelH --> GetRelH
        RelW --> GetRelW
        Query --> EinsumH
        Query --> EinsumW
        GetRelH --> EinsumH
        GetRelW --> EinsumW
        EinsumH --> Combine
        EinsumW --> Combine
        Combine --> AttnBias
    end
```

**Key features:**
- **Decomposition:** Relative positions are factored into height and width components [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:410-444]().
- **Interpolation:** The `get_rel_pos` function interpolates embeddings when query/key sizes differ from the initialized size [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:375-407]().
- **Integration:** Relative position biases are added to the attention logits via `attn_mask` parameter in `scaled_dot_product_attention` [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:314]().

**Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:282-289](), [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:298-310](), [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:410-444](), [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:375-407]()

## Attention Implementation

The `Attention` class implements multi-head attention using PyTorch's optimized `scaled_dot_product_attention` [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:314]():

```mermaid
graph LR
    Input["x (B, H, W, C)"]
    QKV["qkv linear (279)"]
    Reshape["Reshape & Permute"]
    
    subgraph "Attention Computation"
        Q["Query q"]
        K["Key k"]
        V["Value v"]
        RelPos["add_decomposed_rel_pos"]
        SDPA["scaled_dot_product_attention"]
    end
    
    Proj["proj linear (321)"]
    Output["output (B, H, W, C)"]
    
    Input --> QKV
    QKV --> Reshape
    Reshape --> Q
    Reshape --> K
    Reshape --> V
    RelPos --> SDPA
    Q --> SDPA
    K --> SDPA
    V --> SDPA
    SDPA --> Proj
    Proj --> Output
```

The use of `scaled_dot_product_attention` enables hardware-optimized implementations (Flash Attention, memory-efficient attention) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:314-319]().

**Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:252-323]()

## Neck and Downsampling

After the transformer blocks, a "neck" module [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:148-164]() processes the features through multiple convolutional layers with progressive downsampling:

```mermaid
graph TD
    Input["Transformer Output (B, 64, 64, 768)"]
    Permute["Permute (0,3,1,2)"]
    
    subgraph "Neck Module (148)"
        Conv1["Conv2d 768 to 256"]
        LN1["LayerNorm2d"]
        Conv2["Conv2d 256 to 256"]
        LN2["LayerNorm2d"]
    end
    
    Net2["net_2 (166)<br/>Conv2d 256 to 512<br/>stride=2"]
    Net3["net_3 (167)<br/>Conv2d 512 to 1024<br/>stride=2"]
    
    Output["Final Features (B, 1024, 16, 16)"]
    
    Input --> Permute
    Permute --> Conv1
    Conv1 --> LN1
    LN1 --> Conv2
    Conv2 --> LN2
    LN2 --> Net2
    Net2 --> Net3
    Net3 --> Output
```

The final output is `(B, 1024, 16, 16)` for a `1024×1024` input image [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:178-183]().

**Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:148-183](), [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:61-73]()

## Model Construction and Weight Loading

The `build_sam_vit_b` function [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:481]() constructs the SAM ViT-B encoder with predefined hyperparameters:

```mermaid
graph TD
    BuildCall["build_sam_vit_b (481)"]
    
    subgraph "Parameter Configuration"
        Embed["encoder_embed_dim=768"]
        Depth["encoder_depth=12"]
        Heads["encoder_num_heads=12"]
        GlobalIdx["encoder_global_attn_indexes=[2, 5, 8, 11]"]
    end
    
    BuildSam["_build_sam (497)"]
    
    subgraph "Weight Loading (515)"
        CheckCkpt{"checkpoint exists?"}
        LoadDict["torch.load"]
        FilterKeys["Filter 'vision_tower_high'"]
        StripPrefix["Strip prefix (k[30:])"]
        LoadState["load_state_dict"]
    end
    
    Return["Return image_encoder"]
    
    BuildCall --> Embed
    BuildCall --> Depth
    BuildCall --> Heads
    BuildCall --> GlobalIdx
    Embed --> BuildSam
    Depth --> BuildSam
    Heads --> BuildSam
    GlobalIdx --> BuildSam
    
    BuildSam --> CheckCkpt
    CheckCkpt -->|Yes| LoadDict
    LoadDict --> FilterKeys
    FilterKeys --> StripPrefix
    StripPrefix --> LoadState
    LoadState --> Return
```

**Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:481-528]()

## SAM vs CLIP Architecture Differences

| Feature | SAM ViT-B | CLIP-L |
|---------|-----------|---------|
| **Positional Embeddings** | Relative (decomposed) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:410]() | Absolute |
| **Attention Pattern** | Windowed + Global [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:143]() | Fully Global |
| **Window Size** | 14×14 [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:491]() | N/A |
| **Embedding Dimension** | 768 [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:483]() | 1024 |
| **Number of Blocks** | 12 [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:484]() | 24 |
| **Output Processing** | Neck + 2× downsampling [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:178-181]() | Direct output |

**Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:77-184](), [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py:481-528]()

---

