<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/videoprism · page 8 Appendix · fetched 2026-10-26 -->

# Appendix

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)

</details>



This appendix provides supplementary reference material for the VideoPrism codebase, including complete model configuration specifications, checkpoint registry details, and licensing information. This section is intended as a quick-reference guide for developers and users who need detailed technical specifications or legal information.

For model architecture details and usage patterns, see [Core Architecture](#4). For practical usage examples, see [Usage Guide](#5). For API documentation, see [API Reference](#6).

---

## Overview of Reference Material

The appendix is organized into three main sections:

1. **Model Configurations** ([8.1](#8.1)): Complete specifications of all model variants including architectural parameters, layer counts, embedding dimensions, and backbone configurations
2. **Checkpoint Registry** ([8.2](#8.2)): Registry mapping model names to HuggingFace Hub locations and checkpoint metadata
3. **License Information** ([8.3](#8.3)): Apache 2.0 license text and usage terms

---

## Model Registry System Structure

The VideoPrism model management system uses three core dictionaries that work together to enable model instantiation and weight loading:

```mermaid
graph TB
    subgraph "Model Registry System"
        MODELS["MODELS dict<br/>videoprism/models.py"]
        CONFIGS["CONFIGS dict<br/>videoprism/models.py"]
        CHECKPOINTS["CHECKPOINTS dict<br/>videoprism/models.py"]
    end
    
    subgraph "Model Names (Keys)"
        VPB["'videoprism_public_v1_base'"]
        VPL["'videoprism_public_v1_large'"]
        LVTB["'videoprism_lvt_public_v1_base'"]
        LVTL["'videoprism_lvt_public_v1_large'"]
    end
    
    subgraph "Architecture Classes"
        FE["FactorizedEncoder<br/>videoprism/encoders.py"]
        FVCLIP["FactorizedVideoCLIP<br/>videoprism/encoders.py"]
    end
    
    subgraph "HuggingFace Hub"
        HFB["google/videoprism-base-f16r288"]
        HFL["google/videoprism-large-f8r288"]
        HFLTB["google/videoprism-lvt-base-f16r288"]
        HFLTL["google/videoprism-lvt-large-f8r288"]
    end
    
    VPB --> MODELS
    VPL --> MODELS
    LVTB --> MODELS
    LVTL --> MODELS
    
    VPB --> CONFIGS
    VPL --> CONFIGS
    LVTB --> CONFIGS
    LVTL --> CONFIGS
    
    VPB --> CHECKPOINTS
    VPL --> CHECKPOINTS
    LVTB --> CHECKPOINTS
    LVTL --> CHECKPOINTS
    
    MODELS --> FE
    MODELS --> FVCLIP
    
    CONFIGS --> FE
    CONFIGS --> FVCLIP
    
    CHECKPOINTS --> HFB
    CHECKPOINTS --> HFL
    CHECKPOINTS --> HFLTB
    CHECKPOINTS --> HFLTL
```

**Sources:** [README.md:88-97](), [videoprism/models.py]()

The model registry follows a three-tier lookup pattern:

1. **MODELS dict**: Maps model name strings to architecture class constructors (`FactorizedEncoder` or `FactorizedVideoCLIP`)
2. **CONFIGS dict**: Maps model name strings to configuration dictionaries containing architectural hyperparameters
3. **CHECKPOINTS dict**: Maps model name strings to tuples of `(repo_id, filename)` for HuggingFace Hub downloads

---

## Model Configuration Parameters

Each model configuration in the `CONFIGS` dict contains the following parameter categories:

```mermaid
graph LR
    subgraph "Config Dictionary Structure"
        CONFIG["Model Config Dict"]
        
        SPATIAL["Spatial Parameters"]
        TEMP["Temporal Parameters"]
        TEXT["Text Parameters"]
        SHARED["Shared Parameters"]
    end
    
    CONFIG --> SPATIAL
    CONFIG --> TEMP
    CONFIG --> TEXT
    CONFIG --> SHARED
    
    SPATIAL --> SP1["patch_size"]
    SPATIAL --> SP2["spatial_num_layers"]
    SPATIAL --> SP3["spatial_num_heads"]
    SPATIAL --> SP4["spatial_mlp_dim"]
    
    TEMP --> TP1["temporal_num_layers"]
    TEMP --> TP2["temporal_num_heads"]
    TEMP --> TP3["temporal_mlp_dim"]
    TEMP --> TP4["temporal_encoding_type"]
    
    TEXT --> TX1["text_num_layers"]
    TEXT --> TX2["text_num_heads"]
    TEXT --> TX3["text_mlp_dim"]
    TEXT --> TX4["text_vocab_size"]
    
    SHARED --> SH1["hidden_size"]
    SHARED --> SH2["dtype"]
    SHARED --> SH3["dropout_rate"]
```

**Sources:** [videoprism/models.py](), [videoprism/encoders.py]()

### Video-Only Model Configurations

The video encoder models (`videoprism_public_v1_base` and `videoprism_public_v1_large`) use `FactorizedEncoder` with these key parameters:

| Parameter | Base (ViT-B) | Large (ViT-L) | Description |
|-----------|--------------|---------------|-------------|
| Total Parameters | 114M | 354M | Total trainable parameters |
| `hidden_size` | 768 | 1024 | Embedding dimension |
| `patch_size` | 16 | 16 | Spatial patch size (pixels) |
| `spatial_num_layers` | 12 | 24 | Number of spatial transformer layers |
| `spatial_num_heads` | 12 | 16 | Attention heads in spatial encoder |
| `temporal_num_layers` | 4 | 4 | Number of temporal transformer layers |
| `temporal_num_heads` | 12 | 16 | Attention heads in temporal encoder |
| Input Shape | (B, 16, 288, 288, 3) | (B, 8, 288, 288, 3) | Default frame count differs |
| Output Shape | (B, 16×16×F, C) | (B, 16×16×F, C) | Spatiotemporal features |

**Sources:** [README.md:99-106]()

### Video-Text Model Configurations

The video-text models (`videoprism_lvt_public_v1_base` and `videoprism_lvt_public_v1_large`) use `FactorizedVideoCLIP` with additional text encoder parameters:

| Parameter | LvT-Base | LvT-Large | Description |
|-----------|----------|-----------|-------------|
| Total Parameters | 248M | 580M | Video + text encoder parameters |
| Video `hidden_size` | 768 | 1024 | Video embedding dimension |
| Text `hidden_size` | 768 | 1024 | Text embedding dimension |
| `text_num_layers` | 12 | 24 | Transformer layers in text encoder |
| `text_num_heads` | 12 | 16 | Attention heads in text encoder |
| `text_vocab_size` | 32128 | 32128 | SentencePiece vocabulary size |
| Output Shape (Video) | (B, C) | (B, C) | Global video embedding |
| Output Shape (Text) | (B, C) | (B, C) | Global text embedding |

**Sources:** [README.md:108-111]()

---

## Checkpoint File Structure

Each model checkpoint is stored on HuggingFace Hub and contains serialized JAX parameters:

```mermaid
graph TB
    subgraph "HuggingFace Hub Repository"
        REPO["Repository: google/videoprism-*"]
        
        CKPT["Checkpoint File<br/>videoprism_*.checkpoint"]
        META["Model Card<br/>README.md"]
        CONFIG_FILE["Config JSON<br/>config.json"]
    end
    
    subgraph "Checkpoint Contents"
        PARAMS["JAX Pytree<br/>Nested dict of arrays"]
        
        SPATIAL_W["spatial_encoder/<br/>layer weights"]
        TEMP_W["temporal_encoder/<br/>layer weights"]
        TEXT_W["text_encoder/<br/>layer weights"]
        EMBED_W["embedding/<br/>positional embeddings"]
        PROJ_W["projection/<br/>final layers"]
    end
    
    REPO --> CKPT
    REPO --> META
    REPO --> CONFIG_FILE
    
    CKPT --> PARAMS
    
    PARAMS --> SPATIAL_W
    PARAMS --> TEMP_W
    PARAMS --> TEXT_W
    PARAMS --> EMBED_W
    PARAMS --> PROJ_W
```

**Sources:** [README.md:88-97](), [videoprism/utils.py]()

### Checkpoint Loading Flow

The checkpoint loading process uses the `load_checkpoint` utility function:

```mermaid
sequenceDiagram
    participant User
    participant models as "videoprism.models"
    participant HF as "huggingface_hub"
    participant utils as "videoprism.utils"
    participant File as "Checkpoint File"
    
    User->>models: "load_pretrained_weights('videoprism_public_v1_base')"
    models->>models: "Lookup in CHECKPOINTS dict"
    models->>models: "Extract (repo_id, filename)"
    
    models->>HF: "hf_hub_download(repo_id, filename)"
    HF->>File: "Download to cache"
    File-->>HF: "Return local path"
    HF-->>models: "Return path string"
    
    models->>utils: "load_checkpoint(path)"
    utils->>File: "Open file"
    utils->>utils: "Deserialize JAX Pytree"
    utils-->>models: "Return parameters dict"
    
    models-->>User: "Return loaded_state"
```

**Sources:** [videoprism/models.py](), [videoprism/utils.py]()

---

## Model Naming Convention

The model naming scheme follows this pattern:

| Component | Purpose | Example Values |
|-----------|---------|----------------|
| Base prefix | Product name | `videoprism` |
| Model type | Architecture variant | `lvt` (Locked video-text), omitted for video-only |
| Access level | Release designation | `public` |
| Version | Release version | `v1` |
| Size | Model scale | `base`, `large` |

Full model names:
- `videoprism_public_v1_base`: Video-only, base size
- `videoprism_public_v1_large`: Video-only, large size
- `videoprism_lvt_public_v1_base`: Video-text (LvT), base size
- `videoprism_lvt_public_v1_large`: Video-text (LvT), large size

**Sources:** [README.md:88-97]()

---

## HuggingFace Repository Structure

Each model variant has a dedicated HuggingFace repository:

| Model Name | HuggingFace Repository | File Size | Checkpoint Filename |
|------------|------------------------|-----------|---------------------|
| `videoprism_public_v1_base` | `google/videoprism-base-f16r288` | 458MB | `videoprism_base.checkpoint` |
| `videoprism_public_v1_large` | `google/videoprism-large-f8r288` | 1.42GB | `videoprism_large.checkpoint` |
| `videoprism_lvt_public_v1_base` | `google/videoprism-lvt-base-f16r288` | 991MB | `videoprism_lvt_base.checkpoint` |
| `videoprism_lvt_public_v1_large` | `google/videoprism-lvt-large-f8r288` | 2.30GB | `videoprism_lvt_large.checkpoint` |

The repository naming convention includes frame count (`f16` or `f8`) and resolution (`r288`) information:
- `f16`: 16 frames (base models)
- `f8`: 8 frames (large models)
- `r288`: 288×288 spatial resolution

**Sources:** [README.md:88-97]()

---

## Input/Output Specifications

### Video Encoder Models

**Input Requirements:**
- Shape: `(batch_size, num_frames, 288, 288, 3)`
- RGB values normalized to `[0.0, 1.0]`
- Frame count can vary through positional embedding interpolation
- Default frame counts: 16 for Base, 8 for Large

**Output Format:**
- Shape: `(batch_size, num_frames * 16 * 16, feature_channels)`
- Can be reshaped to: `(batch_size, num_frames, 16, 16, feature_channels)`
- Feature channels: 768 for Base, 1024 for Large
- Spatiotemporal feature representation

**Sources:** [README.md:99-106]()

### Video-Text Models

**Video Input:**
- Same as video encoder models
- Can pass `None` to skip video encoding

**Text Input:**
- Token IDs: `(batch_size, max_tokens)`
- Padding masks: `(batch_size, max_tokens)`
- Tokenized using SentencePiece `c4_en` model
- Vocabulary size: 32,128 tokens

**Output Format:**
- Video embeddings: `(batch_size, feature_channels)`
- Text embeddings: `(batch_size, feature_channels)`
- L2-normalized for cosine similarity computation
- Feature channels: 768 for Base, 1024 for Large

**Sources:** [README.md:108-111]()

---

## Text Tokenization Details

The text tokenization system uses SentencePiece with the following specifications:

```mermaid
graph LR
    subgraph "Text Processing Pipeline"
        RAW["Raw Text String"]
        CANON["canonicalize_text()<br/>videoprism.utils"]
        TOKENIZE["tokenize_texts()<br/>videoprism.models"]
        SP["SentencePieceTokenizer<br/>videoprism.tokenizers"]
        OUTPUT["Token IDs + Padding"]
    end
    
    RAW --> CANON
    CANON --> TOKENIZE
    TOKENIZE --> SP
    SP --> OUTPUT
    
    CANON --> C1["Lowercase"]
    CANON --> C2["Remove punctuation"]
    CANON --> C3["Strip whitespace"]
    
    SP --> S1["c4_en model"]
    SP --> S2["32,128 vocab"]
    SP --> S3["BOS/EOS tokens"]
```

**Sources:** [README.md:110](), [videoprism/tokenizers.py](), [videoprism/utils.py]()

### Tokenizer Configuration

| Property | Value | Description |
|----------|-------|-------------|
| Model | `c4_en` | SentencePiece model trained on C4 dataset |
| Vocabulary Size | 32,128 | Total number of tokens |
| Special Tokens | BOS, EOS, PAD | Begin/end of sequence, padding |
| Max Sequence Length | Configurable | Depends on model input |
| Encoding | UTF-8 | Character encoding |

**Sources:** [videoprism/tokenizers.py]()

---

## Performance Benchmarks

The following tables summarize the performance of public release models compared to paper models and prior state-of-the-art:

### VideoGLUE Benchmarks (Video-Only Tasks)

| Model | K400 | MiT | SSv2 | D48 | Charades | ActivityNet | AVA | AVA-K |
|-------|------|-----|------|-----|----------|-------------|-----|-------|
| VideoPrism-B (public) | 82.9 | 39.7 | 62.2 | 64.3 | 43.5 | 36.5 | 28.3 | 30.8 |
| VideoPrism-L (public) | 85.0 | 43.3 | 64.6 | 67.6 | 53.2 | 37.0 | 32.4 | 34.5 |
| VideoPrism-B (paper) | 84.2 | 40.8 | 63.6 | 67.4 | 40.4 | 36.6 | 30.6 | 31.8 |
| VideoPrism-g (paper) | 87.2 | 45.5 | 68.5 | 71.3 | 62.3 | 37.8 | 36.2 | 37.3 |

Note: Public models use different pre-training image-text data than paper models due to data policy.

**Sources:** [README.md:113-130]()

### Zero-Shot Video-Text Retrieval

| Model | MSRVTT (v2t) | MSRVTT (t2v) | VATEX (v2t) | VATEX (t2v) | ActivityNet (v2t) | ActivityNet (t2v) |
|-------|--------------|--------------|-------------|-------------|-------------------|-------------------|
| VideoPrism-LvT-B (public) | 49.8 | 50.1 | 73.1 | 56.2 | 47.9 | 48.8 |
| VideoPrism-LvT-L (public) | 50.6 | 50.1 | 75.0 | 57.2 | 49.1 | 51.3 |
| VideoPrism-LvT-B (paper) | 50.2 | 51.4 | 76.2 | 57.7 | 47.9 | 49.6 |
| VideoPrism-LvT-g (paper) | 51.7 | 52.7 | 77.1 | 62.5 | 50.3 | 52.7 |

**Sources:** [README.md:132-141]()

### Zero-Shot Video Classification

| Model | K400 | SSv2 (Temporal) | SSv2 (Events) | NExT-QA | Charades | Charades (STA) |
|-------|------|-----------------|---------------|---------|----------|----------------|
| VideoPrism-LvT-B (public) | 69.2 | 14.6 | 11.3 | 31.1 | 26.9 | 48.6 |
| VideoPrism-LvT-L (public) | 72.4 | 18.0 | 12.4 | 32.1 | 32.4 | 50.2 |
| VideoPrism-LvT-B (paper) | 71.3 | 16.1 | 11.9 | 31.3 | 29.2 | 50.0 |
| VideoPrism-LvT-g (paper) | 74.6 | 18.6 | 15.7 | 32.7 | 32.4 | 50.4 |

**Sources:** [README.md:143-152]()

---

## Citation Information

When using VideoPrism in research, cite the following papers:

### VideoPrism Paper

```bibtex
@inproceedings{zhao2024videoprism,
  title = {{VideoPrism}: A Foundational Visual Encoder for Video Understanding},
  author = {Long Zhao and Nitesh B. Gundavarapu and Liangzhe Yuan and Hao Zhou and Shen Yan and Jennifer J. Sun and Luke Friedman and Rui Qian and Tobias Weyand and Yue Zhao and Rachel Hornung and Florian Schroff and Ming-Hsuan Yang and David A. Ross and Huisheng Wang and Hartwig Adam and Mikhail Sirotenko and Ting Liu and Boqing Gong},
  booktitle = {International Conference on Machine Learning (ICML)},
  year = {2024}
}
```

### VideoGLUE Paper

```bibtex
@article{yuan2024videoglue,
  title = {{VideoGLUE}: Video General Understanding Evaluation of Foundation Models},
  author = {Liangzhe Yuan and Nitesh Bharadwaj Gundavarapu and Long Zhao and Hao Zhou and Yin Cui and Lu Jiang and Xuan Yang and Menglin Jia and Tobias Weyand and Luke Friedman and Mikhail Sirotenko and Huisheng Wang and Florian Schroff and Hartwig Adam and Ming-Hsuan Yang and Ting Liu and Boqing Gong},
  journal = {Transactions on Machine Learning Research (TMLR)},
  year = {2024}
}
```

**Sources:** [README.md:154-173]()

---

## License Summary

The VideoPrism codebase uses dual licensing:

### Software License

**License:** Apache License, Version 2.0  
**Applies to:** All source code files (`.py`, `.ipynb`, etc.)  
**Full text:** See section [8.3](#8.3) or [LICENSE file](LICENSE)  
**Key permissions:**
- Commercial use allowed
- Modification allowed
- Distribution allowed
- Patent use granted
- Private use allowed

**Key conditions:**
- License and copyright notice must be included
- State changes must be documented
- Same license applies to derivative works
- No trademark use without permission

**Sources:** [README.md:175-189](), [LICENSE:1-202]()

### Documentation License

**License:** Creative Commons Attribution 4.0 International (CC-BY)  
**Applies to:** Non-software materials (documentation, images, etc.)  
**URL:** https://creativecommons.org/licenses/by/4.0/legalcode  
**Key permissions:**
- Share and adapt the material
- Commercial use allowed
- Must give appropriate credit

**Sources:** [README.md:175-189]()

### Copyright Notice

```
Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
```

All software and materials are provided "AS IS" WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

**Sources:** [README.md:177-189]()

---

## Disclaimer

This is not an official Google product. The codebase is provided as research software for educational and research purposes.

**Sources:** [README.md:191-193]()

---

## External Resources

The following external resources are referenced throughout the codebase:

| Resource | Purpose | URL |
|----------|---------|-----|
| arXiv Paper | Research publication | https://arxiv.org/abs/2402.13217 |
| Google Research Blog | Product announcement | https://research.google/blog/videoprism-* |
| HuggingFace Collection | Model weights | https://huggingface.co/collections/google/videoprism-* |
| Video Encoder Colab | Demo notebook | https://colab.research.google.com/.../videoprism_video_encoder_demo.ipynb |
| Video-Text Colab | Demo notebook | https://colab.research.google.com/.../videoprism_video_text_demo.ipynb |
| JAX Documentation | Framework docs | https://github.com/jax-ml/jax |
| Flax Documentation | Framework docs | https://github.com/google/flax |
| SentencePiece | Tokenization library | https://github.com/google/sentencepiece |

**Sources:** [README.md:1-9]()

---

