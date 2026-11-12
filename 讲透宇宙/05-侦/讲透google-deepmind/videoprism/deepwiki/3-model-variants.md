<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/videoprism · page 3 Model Variants · fetched 2026-10-26 -->

# Model Variants

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [videoprism/models.py](videoprism/models.py)

</details>



This page provides an overview of the VideoPrism model family, including the different variants available, their configurations, and how they are organized in the codebase. For detailed usage instructions of each variant type, see [Video-Only Models](#3.1) and [Video-Text Models (VideoCLIP)](#3.2).

VideoPrism offers four publicly released model variants with different architectures and capabilities. All variants are built on the factorized spatial-temporal architecture and share a common configuration system managed through the `videoprism.models` module.

## Model Registry Structure

The VideoPrism model system organizes variants through three core dictionaries defined in [videoprism/models.py:224-233]():

```mermaid
graph TB
    subgraph "Model Registry System"
        MODELS["MODELS dict<br/>videoprism/models.py:224-233"]
        CONFIGS["CONFIGS dict<br/>videoprism/models.py:82-161"]
        CHECKPOINTS["CHECKPOINTS dict<br/>videoprism/models.py:62-80"]
    end
    
    subgraph "Model Names (Public API)"
        VB["'videoprism_public_v1_base'"]
        VL["'videoprism_public_v1_large'"]
        LVTB["'videoprism_lvt_public_v1_base'"]
        LVTL["'videoprism_lvt_public_v1_large'"]
    end
    
    subgraph "Builder Functions"
        BF_VB["videoprism_v1_base()<br/>Line 164-166"]
        BF_VL["videoprism_v1_large()<br/>Line 169-171"]
        BF_LVTB["videoprism_lvt_v1_base()<br/>Line 179-183"]
        BF_LVTL["videoprism_lvt_v1_large()<br/>Line 186-190"]
    end
    
    subgraph "Configurations"
        CFG_VB["'videoprism_v1_base'<br/>patch_size=18<br/>model_dim=768<br/>num_spatial_layers=12"]
        CFG_VL["'videoprism_v1_large'<br/>patch_size=18<br/>model_dim=1024<br/>num_spatial_layers=24"]
        CFG_LVTB["'videoprism_lvt_v1_base'<br/>model_dim=768<br/>num_unimodal_layers=12"]
        CFG_LVTL["'videoprism_lvt_v1_large'<br/>model_dim=1024<br/>num_unimodal_layers=12"]
    end
    
    subgraph "HuggingFace Checkpoints"
        HF_VB["google/videoprism-base-f16r288<br/>flax_base_f16r288_repeated.npz"]
        HF_VL["google/videoprism-large-f8r288<br/>flax_large_f8r288_repeated.npz"]
        HF_LVTB["google/videoprism-lvt-base-f16r288<br/>flax_lvt_base_f16r288_repeated.npz"]
        HF_LVTL["google/videoprism-lvt-large-f8r288<br/>flax_lvt_large_f8r288_repeated.npz"]
    end
    
    VB --> MODELS
    VL --> MODELS
    LVTB --> MODELS
    LVTL --> MODELS
    
    MODELS --> BF_VB
    MODELS --> BF_VL
    MODELS --> BF_LVTB
    MODELS --> BF_LVTL
    
    BF_VB --> CFG_VB
    BF_VL --> CFG_VL
    BF_LVTB --> CFG_LVTB
    BF_LVTL --> CFG_LVTL
    
    CFG_VB --> CONFIGS
    CFG_VL --> CONFIGS
    CFG_LVTB --> CONFIGS
    CFG_LVTL --> CONFIGS
    
    VB --> HF_VB
    VL --> HF_VL
    LVTB --> HF_LVTB
    LVTL --> HF_LVTL
    
    HF_VB --> CHECKPOINTS
    HF_VL --> CHECKPOINTS
    HF_LVTB --> CHECKPOINTS
    HF_LVTL --> CHECKPOINTS
```

**Sources:** [videoprism/models.py:62-233]()

## Available Model Variants

VideoPrism provides four publicly released models across two architecture families:

| Model Name | Configuration Name | Architecture | Backbone | Parameters | File Size | Frame Count | Resolution |
|------------|-------------------|--------------|----------|------------|-----------|-------------|-----------|
| VideoPrism-B | `videoprism_public_v1_base` | FactorizedEncoder | ViT-B | 114M | 458MB | 16 | 288×288 |
| VideoPrism-L | `videoprism_public_v1_large` | FactorizedEncoder | ViT-L | 354M | 1.42GB | 8 | 288×288 |
| VideoPrism-LvT-B | `videoprism_lvt_public_v1_base` | FactorizedVideoCLIP | ViT-B | 248M | 991MB | 16 | 288×288 |
| VideoPrism-LvT-L | `videoprism_lvt_public_v1_large` | FactorizedVideoCLIP | ViT-L | 580M | 2.30GB | 8 | 288×288 |

**Sources:** [README.md:88-98](), [videoprism/models.py:62-80]()

### Model Family Hierarchy

```mermaid
graph TB
    subgraph "Video-Only Models"
        VB["VideoPrism-B<br/>FactorizedEncoder<br/>114M params"]
        VL["VideoPrism-L<br/>FactorizedEncoder<br/>354M params"]
    end
    
    subgraph "Video-Text Models"
        LVTB["VideoPrism-LvT-B<br/>FactorizedVideoCLIP<br/>248M params"]
        LVTL["VideoPrism-LvT-L<br/>FactorizedVideoCLIP<br/>580M params"]
    end
    
    subgraph "Encoder Classes"
        FE["encoders.FactorizedEncoder<br/>videoprism/encoders.py"]
        FVCLIP["encoders.FactorizedVideoCLIP<br/>videoprism/encoders.py"]
    end
    
    VB --> FE
    VL --> FE
    LVTB --> FVCLIP
    LVTL --> FVCLIP
    
    subgraph "Use Cases"
        UC1["Action Recognition<br/>Video Classification<br/>Temporal Localization"]
        UC2["Video-Text Retrieval<br/>Zero-Shot Classification<br/>Video QA"]
    end
    
    FE --> UC1
    FVCLIP --> UC2
```

**Sources:** [videoprism/models.py:164-197](), [README.md:88-112]()

## Configuration Details

Each model variant has a corresponding configuration in the `CONFIGS` dictionary that specifies its architecture parameters:

### Video-Only Model Configurations

**Base Configuration** (`videoprism_v1_base`):
- `patch_size`: 18
- `pos_emb_shape`: (16, 16, 16) - temporal × height × width tokens
- `model_dim`: 768
- `num_spatial_layers`: 12
- `num_temporal_layers`: 4
- `num_heads`: 12
- `mlp_dim`: 3072
- `atten_logit_cap`: 50.0
- `scan`: True

**Large Configuration** (`videoprism_v1_large`):
- `patch_size`: 18
- `pos_emb_shape`: (8, 16, 16) - fewer temporal tokens
- `model_dim`: 1024
- `num_spatial_layers`: 24 - doubled depth
- `num_temporal_layers`: 4
- `num_heads`: 16
- `mlp_dim`: 4096
- `atten_logit_cap`: 50.0
- `scan`: True

**Sources:** [videoprism/models.py:83-104]()

### Video-Text Model Configurations

**LvT Base Configuration** (`videoprism_lvt_v1_base`):
- All base model parameters, plus:
- `num_auxiliary_layers`: 2
- `enable_causal_atten`: True
- `num_unimodal_layers`: 12
- `norm_policy`: 'pre'
- `vocabulary_size`: 32,000 (from TEXT_TOKENIZERS)

**LvT Large Configuration** (`videoprism_lvt_v1_large`):
- All large model parameters, plus:
- `num_auxiliary_layers`: 2
- `enable_causal_atten`: True
- `num_unimodal_layers`: 12
- `norm_policy`: 'pre'
- `vocabulary_size`: 32,000

**Sources:** [videoprism/models.py:116-145](), [videoprism/models.py:55-60]()

## Model Name Resolution

The system supports multiple ways to identify models:

```mermaid
graph LR
    subgraph "Model Identification"
        NAME1["Configuration Name<br/>'videoprism_public_v1_base'"]
        NAME2["HuggingFace Model ID<br/>'google/videoprism-base-f16r288'"]
    end
    
    subgraph "Resolution Functions"
        HAS["has_model()<br/>Line 255-265"]
        GET["get_model()<br/>Line 268-303"]
        LOAD["load_pretrained_weights()<br/>Line 306-336"]
        RESOLVE["_get_model_name_by_hf_model_id()<br/>Line 236-252"]
    end
    
    NAME1 --> HAS
    NAME2 --> HAS
    HAS --> RESOLVE
    
    NAME1 --> GET
    NAME2 --> GET
    GET --> RESOLVE
    
    NAME1 --> LOAD
    NAME2 --> LOAD
    LOAD --> RESOLVE
    
    subgraph "Registry Lookup"
        MODELS_DICT["MODELS dict"]
        CHECKPOINTS_DICT["CHECKPOINTS dict"]
    end
    
    RESOLVE --> MODELS_DICT
    RESOLVE --> CHECKPOINTS_DICT
```

**Sources:** [videoprism/models.py:236-303]()

### Model Name Patterns

Model names follow these conventions:

| Pattern | Example | Description |
|---------|---------|-------------|
| Configuration name | `videoprism_public_v1_base` | Used in `get_model()` and `load_pretrained_weights()` |
| HuggingFace repo ID | `google/videoprism-base-f16r288` | Alternative identifier, auto-resolved to configuration name |
| Internal config key | `videoprism_v1_base` | Used in CONFIGS dict, not public-facing |

The system automatically converts HuggingFace model IDs to configuration names via [videoprism/models.py:236-252]().

**Sources:** [videoprism/models.py:236-303](), [README.md:88-98]()

## Checkpoint Loading

Checkpoints are stored on HuggingFace Hub and downloaded automatically:

```mermaid
graph TB
    subgraph "Checkpoint Registry"
        CKPT_DICT["CHECKPOINTS dict<br/>Line 62-80"]
    end
    
    subgraph "Checkpoint Entries"
        E1["'videoprism_public_v1_base'<br/>→ ('google/videoprism-base-f16r288',<br/>'flax_base_f16r288_repeated.npz')"]
        E2["'videoprism_public_v1_large'<br/>→ ('google/videoprism-large-f8r288',<br/>'flax_large_f8r288_repeated.npz')"]
        E3["'videoprism_lvt_public_v1_base'<br/>→ ('google/videoprism-lvt-base-f16r288',<br/>'flax_lvt_base_f16r288_repeated.npz')"]
        E4["'videoprism_lvt_public_v1_large'<br/>→ ('google/videoprism-lvt-large-f8r288',<br/>'flax_lvt_large_f8r288_repeated.npz')"]
    end
    
    CKPT_DICT --> E1
    CKPT_DICT --> E2
    CKPT_DICT --> E3
    CKPT_DICT --> E4
    
    subgraph "Loading Process"
        LOAD_FN["load_pretrained_weights()<br/>Line 306-336"]
        HF_DL["huggingface_hub.hf_hub_download()<br/>Line 331-333"]
        UTILS_LOAD["utils.load_checkpoint()<br/>Line 335"]
    end
    
    E1 --> LOAD_FN
    E2 --> LOAD_FN
    E3 --> LOAD_FN
    E4 --> LOAD_FN
    
    LOAD_FN --> HF_DL
    HF_DL --> UTILS_LOAD
    
    UTILS_LOAD --> JAX["JAX Pytree<br/>Model Parameters"]
```

**Sources:** [videoprism/models.py:62-80](), [videoprism/models.py:306-336]()

## Additional Model Variants (Not Publicly Released)

The codebase also defines configurations for additional variants that are not publicly released:

### Giant Models

- `videoprism_v1_giant` [videoprism/models.py:105-115]()
  - 1408 model_dim
  - 40 spatial layers
  - 6144 MLP dim
  
- `videoprism_lvt_v1_giant` [videoprism/models.py:146-160]()
  - 1408 model_dim
  - 40 spatial layers
  - 16 unimodal layers
  - Uses 'primer_hybrid' norm policy

### Video Classifier Models

The `FactorizedVideoClassifier` variants add a classification head to the base encoders:

- `videoprism_vc_v1_base(num_classes)` [videoprism/models.py:200-205]()
- `videoprism_vc_v1_large(num_classes)` [videoprism/models.py:208-213]()
- `videoprism_vc_v1_giant(num_classes)` [videoprism/models.py:216-221]()

These are used for supervised fine-tuning on classification tasks but do not have public checkpoints.

**Sources:** [videoprism/models.py:105-221]()

## Common Features Across All Variants

All VideoPrism model variants share these characteristics:

| Feature | Description |
|---------|-------------|
| Input format | Videos with shape `(batch_size, num_frames, 288, 288, 3)` |
| Normalization | RGB values in [0.0, 1.0] |
| Patch size | 18×18 pixels |
| Position embedding interpolation | Supports variable frame counts |
| Framework | JAX/Flax |
| Attention logit capping | 50.0 to stabilize training |
| Scan optimization | Enabled for memory efficiency |

**Sources:** [videoprism/models.py:15-36](), [README.md:99-107]()

## Model Instantiation Pattern

The standard pattern for using any model variant:

```python
from videoprism import models as vp

# Step 1: Get model architecture
model = vp.get_model('videoprism_public_v1_base')

# Step 2: Load pretrained weights
params = vp.load_pretrained_weights('videoprism_public_v1_base')

# Step 3: Apply model with weights
outputs = model.apply(params, inputs, train=False)
```

The separation of architecture instantiation (`get_model`) and weight loading (`load_pretrained_weights`) allows flexibility in using custom initializations or different checkpoint versions.

**Sources:** [videoprism/models.py:22-36](), [README.md:49-64]()

---

