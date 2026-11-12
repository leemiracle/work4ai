<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/nanoVLM · page 3 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [models/config.py](models/config.py)
- [models/language_model.py](models/language_model.py)
- [models/modality_projector.py](models/modality_projector.py)
- [models/vision_language_model.py](models/vision_language_model.py)
- [models/vision_transformer.py](models/vision_transformer.py)

</details>



This document provides a high-level overview of the nanoVLM system architecture, covering the core components and their relationships. The architecture implements a Vision-Language Model that combines a Vision Transformer for image processing with a decoder-only language model for text generation, connected through a modality projection layer.

For detailed implementation of individual components, see [Vision Language Model](#3.1), [Vision Transformer](#3.2), [Language Model](#3.3), and [Modality Projector](#3.4). For configuration details, see [Configuration System](#4).

## System Overview

The nanoVLM architecture follows a modular design with three primary components orchestrated by the `VisionLanguageModel` class defined in [models/vision_language_model.py:21-35](). The system processes multimodal inputs (images and text) through separate encoders and projects them into a shared embedding space for unified processing by the language model.

**Key Components:**
- **Vision Encoder**: `ViT` processes images up to 2048px, producing 768-dimensional features
- **Modality Projector**: `ModalityProjector` reduces spatial dimensions via pixel shuffle and projects to language model dimension (960)
- **Language Model**: `LanguageModel` (SmolLM2-360M) generates text with 960-dimensional hidden states
</thinking>

```mermaid
graph TB
    subgraph "Input Processing"
        IMG_INPUT["Image Input<br/>Up to 2048px<br/>Resized to 512×512"]
        TEXT_INPUT["Text Input<br/>Token IDs<br/>vocab_size: 49218"]
    end
    
    subgraph "VisionLanguageModel - models/vision_language_model.py"
        VLM_INIT["VisionLanguageModel.__init__<br/>Line 22-35"]
        
        subgraph "Vision Pipeline"
            VIT["self.vision_encoder<br/>ViT instance"]
            PATCH_EMB["ViTPatchEmbeddings<br/>16×16 patches<br/>32×32 grid = 1024 patches"]
            VIT_BLOCKS["12 × ViTBlock<br/>hidden_dim: 768<br/>n_heads: 12"]
            VIT_OUT["Output: [B, 1024, 768]"]
        end
        
        subgraph "Modality Bridge"
            MP["self.MP<br/>ModalityProjector instance"]
            PIXEL_SHUFFLE["Pixel Shuffle<br/>factor: 4<br/>32×32 → 8×8 grid<br/>1024 → 64 tokens"]
            LINEAR_PROJ["Linear Projection<br/>12288 → 960"]
            MP_OUT["Output: [B, 64, 960]"]
        end
        
        subgraph "Language Pipeline"
            TOKEN_EMB["self.decoder.token_embedding<br/>vocab: 49152 + 66 = 49218<br/>hidden_dim: 960"]
            REPLACE_TOKENS["_replace_img_tokens_with_embd<br/>Line 36-49"]
            LM["self.decoder<br/>LanguageModel instance"]
            LM_BLOCKS["32 × LanguageModelBlock<br/>hidden_dim: 960<br/>n_heads: 15, n_kv_heads: 5"]
            LM_HEAD["self.decoder.head<br/>960 → 49218<br/>Weight tied to embedding"]
        end
    end
    
    subgraph "Output Generation"
        LOGITS["Logits<br/>[B, T, 49218]"]
        GENERATED_TEXT["Generated Text<br/>Autoregressive Sampling"]
    end
    
    IMG_INPUT --> VIT
    VIT --> PATCH_EMB
    PATCH_EMB --> VIT_BLOCKS
    VIT_BLOCKS --> VIT_OUT
    VIT_OUT --> MP
    
    MP --> PIXEL_SHUFFLE
    PIXEL_SHUFFLE --> LINEAR_PROJ
    LINEAR_PROJ --> MP_OUT
    
    TEXT_INPUT --> TOKEN_EMB
    TOKEN_EMB --> REPLACE_TOKENS
    MP_OUT --> REPLACE_TOKENS
    
    REPLACE_TOKENS --> LM
    LM --> LM_BLOCKS
    LM_BLOCKS --> LM_HEAD
    LM_HEAD --> LOGITS
    LOGITS --> GENERATED_TEXT
    
    VLM_INIT -.creates.-> VIT
    VLM_INIT -.creates.-> MP
    VLM_INIT -.creates.-> LM
```

Sources: [models/vision_language_model.py:21-35](), [models/config.py:5-55](), [models/vision_transformer.py:131-169](), [models/language_model.py:390-418](), [models/modality_projector.py:4-45]()

```mermaid
graph TB
    subgraph "Input Processing"
        IMG_INPUT["Image Input<br/>(PIL/Tensor)"]
        TEXT_INPUT["Text Input<br/>(Token IDs)"]
    end
    
    subgraph "Core Architecture"
        VLM_MAIN["VisionLanguageModel<br/>models/vision_language_model.py"]
        
        subgraph "Vision Pipeline"
            VIT["ViT<br/>models/vision_transformer.py"]
            VIT_PATCH["Patch Embeddings"]
            VIT_BLOCKS["Transformer Blocks"]
        end
        
        subgraph "Modality Bridge"
            MP["ModalityProjector<br/>models/modality_projector.py"]
            PIXEL_SHUFFLE["Pixel Shuffle Operation"]
            LINEAR_PROJ["Linear Projection"]
        end
        
        subgraph "Language Pipeline"
            LM["LanguageModel<br/>models/language_model.py"]
            TOKEN_EMB["Token Embeddings"]
            LM_BLOCKS["Language Model Blocks"]
            LM_HEAD["Language Model Head"]
        end
    end
    
    subgraph "Output Generation"
        LOGITS["Logits Output"]
        GENERATED_TEXT["Generated Text"]
    end
    
    IMG_INPUT --> VIT
    TEXT_INPUT --> TOKEN_EMB
    
    VIT --> VIT_PATCH
    VIT_PATCH --> VIT_BLOCKS
    VIT_BLOCKS --> MP
    
    MP --> PIXEL_SHUFFLE
    PIXEL_SHUFFLE --> LINEAR_PROJ
    LINEAR_PROJ --> VLM_MAIN
    
    TOKEN_EMB --> VLM_MAIN
    VLM_MAIN --> LM_BLOCKS
    LM_BLOCKS --> LM_HEAD
    LM_HEAD --> LOGITS
    LOGITS --> GENERATED_TEXT
    
    VLM_MAIN -.-> VIT
    VLM_MAIN -.-> LM
    VLM_MAIN -.-> MP
```

Sources: [models/vision_language_model.py:21-35](), [models/README.md:1-24]()

## Component Initialization and Integration

The `VisionLanguageModel.__init__` method in [models/vision_language_model.py:22-35]() orchestrates component initialization with conditional backbone loading.

**Initialization Flow:**

```mermaid
graph TB
    subgraph "VisionLanguageModel.__init__ - Line 22-35"
        CFG_INPUT["cfg: VLMConfig<br/>load_backbone: bool"]
        
        subgraph "Conditional Loading"
            LOAD_CHECK{"load_backbone<br/>is True?"}
            
            PRETRAINED_PATH["Pretrained Path"]
            VIT_PRETRAINED["ViT.from_pretrained(cfg)<br/>Line 27<br/>Loads google/siglip2-base"]
            LM_PRETRAINED["LanguageModel.from_pretrained(cfg)<br/>Line 28<br/>Loads SmolLM2-360M-Instruct"]
            
            SCRATCH_PATH["From Scratch Path"]
            VIT_SCRATCH["ViT(cfg)<br/>Line 30"]
            LM_SCRATCH["LanguageModel(cfg)<br/>Line 31"]
        end
        
        MP_INIT["ModalityProjector(cfg)<br/>Line 32<br/>Always fresh initialization"]
        TOKENIZER_INIT["get_tokenizer(...)<br/>Line 34<br/>With vlm_extra_tokens"]
        
        COMPONENTS_OUT["self.vision_encoder<br/>self.decoder<br/>self.MP<br/>self.tokenizer"]
    end
    
    CFG_INPUT --> LOAD_CHECK
    
    LOAD_CHECK -->|True| PRETRAINED_PATH
    PRETRAINED_PATH --> VIT_PRETRAINED
    PRETRAINED_PATH --> LM_PRETRAINED
    
    LOAD_CHECK -->|False| SCRATCH_PATH
    SCRATCH_PATH --> VIT_SCRATCH
    SCRATCH_PATH --> LM_SCRATCH
    
    VIT_PRETRAINED --> MP_INIT
    LM_PRETRAINED --> MP_INIT
    VIT_SCRATCH --> MP_INIT
    LM_SCRATCH --> MP_INIT
    
    MP_INIT --> TOKENIZER_INIT
    TOKENIZER_INIT --> COMPONENTS_OUT
```

**Component Specifications:**

| Component | Initialization Method | Pretrained Source | Parameters |
|-----------|----------------------|-------------------|------------|
| `self.vision_encoder` | `ViT.from_pretrained(cfg)` or `ViT(cfg)` | `google/siglip2-base-patch16-512` | ~85M |
| `self.decoder` | `LanguageModel.from_pretrained(cfg)` or `LanguageModel(cfg)` | `SmolLM2-360M-Instruct` | ~360M |
| `self.MP` | `ModalityProjector(cfg)` | Always random init | ~11M |
| `self.tokenizer` | `get_tokenizer(...)` | Matches language model | Extended vocab: 49218 |

Sources: [models/vision_language_model.py:22-35](), [models/config.py:15](), [models/config.py:33]()

## Tensor Shape Transformations

The following table documents the tensor shape transformations through each component of the architecture:

| Stage | Component | Input Shape | Output Shape | Notes |
|-------|-----------|-------------|--------------|-------|
| **Vision Processing** |
| Patch Embedding | `ViTPatchEmbeddings` | `[B, 3, 512, 512]` | `[B, 1024, 768]` | 16×16 patches → 32×32 grid |
| Vision Blocks | `12 × ViTBlock` | `[B, 1024, 768]` | `[B, 1024, 768]` | Bidirectional attention |
| Layer Norm | `ViT.layer_norm` | `[B, 1024, 768]` | `[B, 1024, 768]` | Final normalization |
| **Modality Projection** |
| Pixel Shuffle | `ModalityProjector.pixel_shuffle` | `[B, 1024, 768]` | `[B, 64, 12288]` | 4× spatial reduction, 16× channel expansion |
| Linear Projection | `ModalityProjector.proj` | `[B, 64, 12288]` | `[B, 64, 960]` | Maps to language hidden dim |
| **Text Processing** |
| Token Embedding | `self.decoder.token_embedding` | `[B, T_seq]` | `[B, T_seq, 960]` | Vocab size: 49218 |
| Image Token Replace | `_replace_img_tokens_with_embd` | `[B, T_seq, 960]` + image embeddings | `[B, T_seq, 960]` | Replaces `<\|image\|>` tokens |
| **Language Generation** |
| Language Blocks | `32 × LanguageModelBlock` | `[B, T_seq, 960]` | `[B, T_seq, 960]` | Causal attention with KV cache |
| RMS Norm | `LanguageModel.norm` | `[B, T_seq, 960]` | `[B, T_seq, 960]` | Final normalization |
| LM Head | `self.decoder.head` | `[B, T_seq, 960]` | `[B, T_seq, 49218]` | Weight tied to embedding |

Sources: [models/vision_transformer.py:7-44](), [models/modality_projector.py:23-44](), [models/language_model.py:397-403](), [models/vision_language_model.py:36-49]()

## Data Flow Architecture

The system processes multimodal inputs through distinct pathways that converge at the modality projection layer, enabling unified processing in the language model's embedding space. The architecture supports two execution modes: training (forward pass with loss computation) and inference (autoregressive generation with KV caching).

### Training Forward Pass

The `VisionLanguageModel.forward` method in [models/vision_language_model.py:62-80]() processes batched multimodal inputs for training:

```mermaid
flowchart TD
    subgraph "Input Stage"
        INPUT_IDS["input_ids<br/>Shape: [B, T_seq]"]
        IMAGE["image<br/>Shape: [B, C, H, W]"]
        ATTENTION_MASK["attention_mask<br/>Shape: [B, T_seq]"]
        TARGETS["targets<br/>Shape: [B, T_seq]"]
    end
    
    subgraph "Vision Processing"
        VISION_ENCODER["self.vision_encoder(image)<br/>Line 52"]
        IMAGE_EMBD["image_embd<br/>Shape: [num_images, T_img, D_model]"]
    end
    
    subgraph "Modality Projection"
        MODALITY_PROJ["self.MP(image_embd)<br/>Line 53"]
        PROJECTED_EMBD["image_embd<br/>Shape: [num_images, mp_image_token_length, D_lm]"]
    end
    
    subgraph "Text Processing"
        TOKEN_EMBEDDING["self.decoder.token_embedding(input_ids)<br/>Line 55"]
        TOKEN_EMBD["token_embd<br/>Shape: [B, T_seq, D_lm]"]
    end
    
    subgraph "Multimodal Integration"
        REPLACE_TOKENS["_replace_img_tokens_with_embd<br/>Line 57"]
        UPDATED_EMBD["updated_token_embd<br/>Shape: [B, T_seq, D_lm]"]
    end
    
    subgraph "Language Model Processing"
        DECODER_FORWARD["self.decoder(updated_token_embd)<br/>Line 61"]
        LOGITS_RAW["logits<br/>Shape: [B, T_seq, D_lm]"]
        LM_HEAD["self.decoder.head(logits)<br/>Line 65"]
        FINAL_LOGITS["logits<br/>Shape: [B, T_seq, vocab_size]"]
    end
    
    subgraph "Loss Computation"
        CROSS_ENTROPY["F.cross_entropy<br/>Line 68"]
        LOSS["loss<br/>Scalar"]
    end
    
    INPUT_IDS --> TOKEN_EMBEDDING
    IMAGE --> VISION_ENCODER
    
    VISION_ENCODER --> IMAGE_EMBD
    IMAGE_EMBD --> MODALITY_PROJ
    MODALITY_PROJ --> PROJECTED_EMBD
    
    TOKEN_EMBEDDING --> TOKEN_EMBD
    TOKEN_EMBD --> REPLACE_TOKENS
    PROJECTED_EMBD --> REPLACE_TOKENS
    INPUT_IDS --> REPLACE_TOKENS
    
    REPLACE_TOKENS --> UPDATED_EMBD
    UPDATED_EMBD --> DECODER_FORWARD
    ATTENTION_MASK --> DECODER_FORWARD
    
    DECODER_FORWARD --> LOGITS_RAW
    LOGITS_RAW --> LM_HEAD
    LM_HEAD --> FINAL_LOGITS
    
    FINAL_LOGITS --> CROSS_ENTROPY
    TARGETS --> CROSS_ENTROPY
    CROSS_ENTROPY --> LOSS
```

Sources: [models/vision_language_model.py:51-70]()

### Inference Generation Pipeline

The `VisionLanguageModel.generate` method in [models/vision_language_model.py:82-183]() implements two-phase generation: multimodal prefill followed by autoregressive decoding with KV caching.

```mermaid
flowchart TD
    subgraph "Prefill Phase"
        PREFILL_INPUT["initial_combined_embeds<br/>Line 83"]
        PREFILL_DECODER["self.decoder(..., kv_cache=None)<br/>Line 89-94"]
        PREFILL_OUTPUT["prefill_output, kv_cache_list<br/>Line 89"]
        LAST_TOKEN["last_token_output_from_prefill<br/>Line 96"]
        INITIAL_LOGITS["current_logits<br/>Line 99-101"]
    end
    
    subgraph "Autoregressive Loop"
        LOOP_START["for _ in range(max_new_tokens)<br/>Line 107"]
        
        subgraph "Sampling Strategy"
            GREEDY_CHECK["if greedy<br/>Line 108"]
            GREEDY_SAMPLE["torch.argmax<br/>Line 109"]
            FILTERED_SAMPLE["top_k_top_p_filtering<br/>Line 111-113"]
        end
        
        NEXT_TOKEN["next_token_id<br/>Line 109 or 113"]
        TOKEN_EMBED["self.decoder.token_embedding<br/>Line 118"]
        
        subgraph "KV Cache Decode"
            UPDATE_ATTENTION["Update attention_mask<br/>Line 125-126"]
            DECODE_STEP["self.decoder(..., kv_cache=kv_cache_list)<br/>Line 129-134"]
            UPDATE_KV["Update kv_cache_list<br/>Line 129"]
        end
        
        NEW_LOGITS["current_logits<br/>Line 140 or 142"]
    end
    
    subgraph "Post Processing"
        EOS_HANDLING["EOS token handling<br/>Line 150-172"]
        FINAL_OUTPUT["generated_ids<br/>Line 147"]
    end
    
    PREFILL_INPUT --> PREFILL_DECODER
    PREFILL_DECODER --> PREFILL_OUTPUT
    PREFILL_OUTPUT --> LAST_TOKEN
    LAST_TOKEN --> INITIAL_LOGITS
    
    INITIAL_LOGITS --> LOOP_START
    LOOP_START --> GREEDY_CHECK
    GREEDY_CHECK --> GREEDY_SAMPLE
    GREEDY_CHECK --> FILTERED_SAMPLE
    GREEDY_SAMPLE --> NEXT_TOKEN
    FILTERED_SAMPLE --> NEXT_TOKEN
    
    NEXT_TOKEN --> TOKEN_EMBED
    TOKEN_EMBED --> UPDATE_ATTENTION
    UPDATE_ATTENTION --> DECODE_STEP
    DECODE_STEP --> UPDATE_KV
    DECODE_STEP --> NEW_LOGITS
    
    NEW_LOGITS --> LOOP_START
    LOOP_START --> EOS_HANDLING
    EOS_HANDLING --> FINAL_OUTPUT
```

Sources: [models/vision_language_model.py:72-174]()

## Configuration System Integration

The system uses `VLMConfig` from [models/config.py:4-55]() to centralize all architectural parameters. This configuration drives component initialization and defines cross-component compatibility.

**Key Configuration Parameters:**

```mermaid
graph TB
    subgraph "VLMConfig - models/config.py"
        subgraph "Vision Encoder Config"
            VIT_PARAMS["vit_hidden_dim: 768<br/>vit_patch_size: 16<br/>vit_img_size: 512<br/>vit_n_heads: 12<br/>vit_n_blocks: 12<br/>vit_model_type: google/siglip2-base"]
        end
        
        subgraph "Language Model Config"
            LM_PARAMS["lm_hidden_dim: 960<br/>lm_inter_dim: 2560<br/>lm_n_heads: 15<br/>lm_n_kv_heads: 5<br/>lm_n_blocks: 32<br/>lm_vocab_size: 49218<br/>lm_model_type: SmolLM2-360M-Instruct"]
        end
        
        subgraph "Modality Projector Config"
            MP_PARAMS["mp_pixel_shuffle_factor: 4<br/>mp_image_token_length: 64"]
        end
        
        subgraph "Special Tokens Config"
            EXTRA_TOKENS["extra_token_amount: 66<br/>vlm_extra_tokens: dict<br/>&lt;|image|&gt;, &lt;|global_image|&gt;<br/>64 grid position tokens"]
        end
    end
    
    subgraph "Component Initialization"
        VIT_INIT["ViT(cfg)<br/>or from_pretrained"]
        LM_INIT["LanguageModel(cfg)<br/>or from_pretrained"]
        MP_INIT["ModalityProjector(cfg)"]
    end
    
    VIT_PARAMS --> VIT_INIT
    LM_PARAMS --> LM_INIT
    MP_PARAMS --> MP_INIT
    EXTRA_TOKENS --> LM_INIT
```

**Vocabulary Extension:**

The vocabulary is extended from the base language model to include vision-specific tokens:
- Base vocabulary: `lm_base_vocab_size = 49152` (from SmolLM2)
- Extra tokens: `extra_token_amount = 66`
  - 1 × `<|image|>` token (standard image placeholder)
  - 1 × `<|global_image|>` token (global image context)
  - 64 × grid position tokens (`<row_X_col_Y>`) for spatial reasoning
- Extended vocabulary: `lm_vocab_size = 49218`

The token embedding matrix and LM head are extended to accommodate these tokens in [models/language_model.py:538-682]().

Sources: [models/config.py:4-55](), [models/config.py:23-24](), [models/config.py:43-51]()

## Model Persistence and Distribution

The architecture includes built-in support for model serialization and distribution through standardized methods:

```mermaid
graph LR
    subgraph "Model Loading"
        FROM_PRETRAINED["from_pretrained<br/>Line 176-224"]
        LOCAL_PATH["Local Directory<br/>config.json + model.safetensors"]
        HF_HUB["Hugging Face Hub<br/>hf_hub_download"]
    end
    
    subgraph "Model Saving"
        SAVE_PRETRAINED["save_pretrained<br/>Line 226-241"]
        CONFIG_JSON["config.json<br/>asdict(self.cfg)"]
        MODEL_SAFETENSORS["model.safetensors<br/>save_model()"]
    end
    
    subgraph "Model Distribution"  
        PUSH_TO_HUB["push_to_hub<br/>Line 243-271"]
        CREATE_REPO["create_repo"]
        UPLOAD_FOLDER["upload_folder"]
        MODEL_CARD["README.md<br/>MODEL_CARD_TEMPLATE"]
    end
    
    FROM_PRETRAINED --> LOCAL_PATH
    FROM_PRETRAINED --> HF_HUB
    
    SAVE_PRETRAINED --> CONFIG_JSON
    SAVE_PRETRAINED --> MODEL_SAFETENSORS
    
    PUSH_TO_HUB --> CREATE_REPO
    PUSH_TO_HUB --> UPLOAD_FOLDER
    PUSH_TO_HUB --> MODEL_CARD
    PUSH_TO_HUB --> SAVE_PRETRAINED
```

Sources: [models/vision_language_model.py:176-301]()

## Image Token Integration Strategy

The architecture implements a flexible image token replacement mechanism that supports variable numbers of images per sample through the `_replace_img_tokens_with_embd` method.

The system uses special image token placeholders (`self.tokenizer.image_token_id`) in the input sequence, which are dynamically replaced with projected image embeddings during forward pass. This approach enables:

- **Variable Image Count**: Different samples in a batch can contain different numbers of images
- **Flexible Positioning**: Image tokens can appear anywhere in the input sequence
- **Unified Processing**: Image and text embeddings are processed together in the language model

The replacement operation creates a boolean mask for image token positions and uses tensor indexing to substitute embeddings in-place, maintaining the original sequence structure while incorporating visual information.

Sources: [models/vision_language_model.py:36-49](), [models/vision_language_model.py:46-47]()

---

