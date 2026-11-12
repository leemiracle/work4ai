<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/physicsnemo · extra page Layer Modules (physicsnemo.nn.module) · fetched 2026-10-21 -->

# Layer Modules (physicsnemo.nn.module)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/api/nn/layers/rope.rst](docs/api/nn/layers/rope.rst)
- [docs/api/physicsnemo.nn.layers.rst](docs/api/physicsnemo.nn.layers.rst)
- [physicsnemo/domain_parallel/shard_utils/halo.py](physicsnemo/domain_parallel/shard_utils/halo.py)
- [physicsnemo/models/afno/distributed/afno.py](physicsnemo/models/afno/distributed/afno.py)
- [physicsnemo/models/afno/distributed/layers.py](physicsnemo/models/afno/distributed/layers.py)
- [physicsnemo/models/dit/dit.py](physicsnemo/models/dit/dit.py)
- [physicsnemo/nn/__init__.py](physicsnemo/nn/__init__.py)
- [physicsnemo/nn/module/__init__.py](physicsnemo/nn/module/__init__.py)
- [physicsnemo/nn/module/attention_layers.py](physicsnemo/nn/module/attention_layers.py)
- [physicsnemo/nn/module/dit_layers.py](physicsnemo/nn/module/dit_layers.py)
- [physicsnemo/nn/module/point_transformer_attention.py](physicsnemo/nn/module/point_transformer_attention.py)
- [physicsnemo/nn/module/rope.py](physicsnemo/nn/module/rope.py)
- [physicsnemo/nn/module/utils/__init__.py](physicsnemo/nn/module/utils/__init__.py)
- [physicsnemo/nn/module/utils/weight_init.py](physicsnemo/nn/module/utils/weight_init.py)
- [test/common/fwdaccuracy.py](test/common/fwdaccuracy.py)
- [test/experimental/models/aerojepa/encoders/test_point.py](test/experimental/models/aerojepa/encoders/test_point.py)
- [test/models/afno/data/afno_output.pth](test/models/afno/data/afno_output.pth)
- [test/models/afno/data/modafno_output.pth](test/models/afno/data/modafno_output.pth)
- [test/models/dit/test_dit.py](test/models/dit/test_dit.py)
- [test/nn/module/data/local_point_transformer_block_output.pth](test/nn/module/data/local_point_transformer_block_output.pth)
- [test/nn/module/data/local_token_cross_attention_block_output.pth](test/nn/module/data/local_token_cross_attention_block_output.pth)
- [test/nn/module/test_dit_layers.py](test/nn/module/test_dit_layers.py)
- [test/nn/module/test_point_transformer_attention.py](test/nn/module/test_point_transformer_attention.py)
- [test/nn/module/test_rope.py](test/nn/module/test_rope.py)
- [test/nn/module/test_weight_init.py](test/nn/module/test_weight_init.py)

</details>



## Purpose and Scope

The `physicsnemo.nn.module` package provides a GPU-accelerated collection of reusable neural network layers, blocks, and utility functions tailored for physics-informed machine learning, climate modeling, and computational fluid dynamics (CFD). This subsystem supplies foundational modules ranging from standard multi-layer perceptrons (MLPs) and spectral convolutions to advanced physics-informed attention mechanisms (GALE, Point Transformer, FLARE), Rotary Position Embeddings (RoPE), and Diffusion Transformer (DiT) building blocks.

Sources: `physicsnemo/nn/__init__.py:20-171` [physicsnemo/nn/__init__.py:20-171]()

---

## Attention Subsystem & Physics Attention

PhysicsNeMo implements specialized attention variants optimized for irregular grids, point clouds, physical manifolds, and spatiotemporal scientific data.

### Point Transformer and Vector Attention
The point transformer subsystem implements local $k$-NN vector attention in the style of Point Transformer (Zhao et al.) and Point Transformer v2, augmented with optional AdaLN/AdaLN-Zero conditioning. 
- `LocalPointTransformerBlock`: Computes self-attention over a per-point dynamic or precomputed $k$-NN graph.
- `LocalTokenCrossAttentionBlock`: Computes cross-attention from query tokens to a neighborhood of context tokens.
- `AdaLNResidualMLP`: Pre-norm residual feed-forward block with adaptive layer normalization conditioning.

Sources: `physicsnemo/nn/module/point_transformer_attention.py:17-42` [physicsnemo/nn/module/point_transformer_attention.py:17-42]()

### Physics Attention and Specialized Transformers
- `UNetAttention`: Combines GroupNorm, 1x1 QKV convolutions, and scaled dot-product attention for U-Net backbones [physicsnemo/nn/module/attention_layers.py:69-110]().
- `EarthAttention2D` / `EarthAttention3D`: Windowed attention modules incorporating Earth position biases for spherical/cubed-sphere climate geometries [physicsnemo/nn/module/attention_layers.py:181-190]().
- `FLARE` and `GALE`: Specialized geometry-aware attention modules designed for aerodynamic and unstructured mesh regression tasks [physicsnemo/nn/__init__.py:95-118]().

```mermaid
graph TD
    Input["Input Tensor (B, L, D)"] --> LN["LayerNorm / AdaLN"]
    LN --> QKV["Q, K, V Projections"]
    QKV --> KNN["_dilated_knn (k-NN Graph)"]
    KNN --> AttnOp["Local Vector Attention / Softmax"]
    AttnOp --> Proj["Output Projection"]
    Proj --> Res["Residual Addition"]
    
    sub: "Code Entity Mapping"
    LN -->|Implemented by| A1["AdaLNResidualMLP"]
    KNN -->|Implemented by| A2["_dilated_knn"]
    AttnOp -->|Implemented by| A3["LocalPointTransformerBlock"]

    Sources: physicsnemo/nn/module/point_transformer_attention.py:17-128
```
*Figure 1: Execution flow mapping natural language attention steps to code entities in `physicsnemo.nn.module.point_transformer_attention`.*

Sources: `physicsnemo/nn/module/point_transformer_attention.py:57-128` [physicsnemo/nn/module/point_transformer_attention.py:57-128](), `physicsnemo/nn/module/attention_layers.py:69-190` [physicsnemo/nn/module/attention_layers.py:69-190]()

---

## Diffusion Transformer (DiT) Layers & Conditioning

The DiT module family supplies transformer building blocks tuned for generative diffusion models in scientific applications.

### Core DiT Modules
- `DiTBlock`: Transformer block integrating adaptive layer norm zero (`adaLN-Zero`), self-attention, and an MLP expansion block [physicsnemo/nn/module/dit_layers.py:68-86]().
- `get_attention(...)`: Factory supporting `"timm"`, `"transformer_engine"`, `"natten2d"`, and `"natten2d_rope"` attention backends [physicsnemo/nn/module/dit_layers.py:86-153]().
- `get_layer_norm(...)`: Instantiates either PyTorch standard `nn.LayerNorm` or Apex `FusedLayerNorm` [physicsnemo/nn/module/dit_layers.py:48-84]().
- `ConvDetokenizer` and `ProjReshape2DDetokenizer`: Convert token sequences back into spatial feature maps [physicsnemo/nn/module/dit_layers.py:70-78]().

### Conditioning Embedders
- `DiTConditionEmbedder` and `EDMConditionEmbedder`: Map diffusion timesteps and external condition vectors into scale/shift modulation parameters for `DiTBlock` adaptive normalization layers [physicsnemo/nn/__init__.py:50-57]().

```mermaid
graph TD
    Model["DiT Model"] --> Cond["ConditioningEmbedder"]
    Model --> Tok["TokenizerModuleBase"]
    Tok --> Block["DiTBlock"]
    Cond -->|Modulation Vectors| Block
    Block --> Attn["get_attention (backend)"]
    Block --> Norm["get_layer_norm (apex/torch)"]
    Block --> Detok["DetokenizerModuleBase"]
    
    sub: "Code Entity Space"
    Cond --> E1["DiTConditionEmbedder"]
    Block --> E2["DiTBlock"]
    Attn --> E3["Natten2DSelfAttention / TimmSelfAttention"]
    Detok --> E4["ConvDetokenizer"]

    Sources: physicsnemo/models/dit/dit.py:58-114, physicsnemo/nn/module/dit_layers.py:48-153
```
*Figure 2: Architectural bridge linking Diffusion Transformer systems to their concrete implementation classes.*

Sources: `physicsnemo/nn/module/dit_layers.py:48-153` [physicsnemo/nn/module/dit_layers.py:48-153](), `physicsnemo/models/dit/dit.py:58-114` [physicsnemo/models/dit/dit.py:58-114]()

---

## Rotary Position Embedding (RoPE) Primitives

Rotary Position Embedding encodes token positions by rotating query and key vectors in complex planes, providing relative position awareness without learned embedding parameters.

- `RotaryEmbedding2DTables`: Precomputes and owns axial 2D RoPE cosine and sine tables for an $h \times w$ token grid in layout `(h, w, head_dim)` [physicsnemo/nn/module/rope.py:30-44](). Tables use `persistent=False` so they do not pollute state dict checkpoints.
- `RotaryEmbedding1DTables`: Owns standard 1D sequence RoPE tables of shape `(max_seq_len, head_dim)` [physicsnemo/nn/module/rope.py:33-35]().
- `build_axial_rope_cos_sin_2d` & `build_rope_cos_sin_1d`: Functional builders returning frequency schedules [physicsnemo/nn/module/rope.py:83-162]().
- `apply_rotary_pos_emb`: Applies rotary transformations to query or key tensors while preserving data types and channel norms [physicsnemo/nn/module/rope.py:46-51]().

Sources: `physicsnemo/nn/module/rope.py:17-80` [physicsnemo/nn/module/rope.py:17-80]()

---

## MLP, Spectral, AFNO, and HEALPix Layers

PhysicsNeMo includes specialized layer implementations for operator learning and spherical grids:

- **MLP Layers**: `Mlp` implements standard multi-layer perceptrons with configurable activation functions and dropout [physicsnemo/nn/__init__.py:133]().
- **Spectral Convolutions**: `SpectralConv1d`, `SpectralConv2d`, `SpectralConv3d`, and `SpectralConv4d` execute Fourier-space convolutions for Neural Operators (FNO) [physicsnemo/nn/__init__.py:156-161]().
- **AFNO Layers**: `AFNO2DLayer`, `ModAFNO2DLayer`, and `AFNOMlp` provide Adaptive Fourier Neural Operator blocks used in global weather forecasting models [physicsnemo/nn/__init__.py:29-37]().
- **HEALPix Layers**: `HEALPixLayer`, `HEALPixAvgPool`, `HEALPixMaxPool`, and `HEALPixPadding` handle tensor operations tailored to equal-area spherical Hierarchical Equal Area isoLatitude Pixelation grids [physicsnemo/nn/__init__.py:121-131]().

Sources: `physicsnemo/nn/__init__.py:29-161` [physicsnemo/nn/__init__.py:29-161]()

---

## Normalization, Activations, and Weight Initialization Utilities

### Weight Initialization
- `shrink_and_perturb_`: Implements shrink-and-perturb warm-start re-initialization ($\theta \leftarrow \lambda\theta + p\varepsilon$) for pretrained modules. This restores plasticity while preserving pretrained feature directions [physicsnemo/nn/module/utils/weight_init.py:113-138](). Supports presets like `scaled_normal` and custom callables [physicsnemo/nn/module/utils/weight_init.py:118-121]().

### Normalization and Activations
- **Normalization**: `GroupNorm`, `RunningNorm`, and dynamic selection via `get_group_norm` [physicsnemo/nn/__init__.py:119,154]().
- **Activations**: Custom activation functionals and modules including `CappedGELU`, `CappedLeakyReLU`, `Sin`, `SquarePlus`, `Stan`, and `get_activation(...)` [physicsnemo/nn/__init__.py:20-28]().

Sources: `physicsnemo/nn/module/utils/weight_init.py:113-160` [physicsnemo/nn/module/utils/weight_init.py:113-160](), `physicsnemo/nn/__init__.py:20-28` [physicsnemo/nn/__init__.py:20-28]()

---

