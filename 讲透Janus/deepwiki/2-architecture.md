<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/Janus · page 2 Architecture · fetched 2026-10-30 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [images/teaser_janusflow.png](images/teaser_janusflow.png)
- [janus/janusflow/models/__init__.py](janus/janusflow/models/__init__.py)
- [janus/janusflow/models/modeling_vlm.py](janus/janusflow/models/modeling_vlm.py)

</details>



This document provides a detailed overview of the Janus system architecture, explaining the key components and their relationships across all Janus model variants. It covers the core systems that enable multimodal understanding (text + images) and text-to-image generation capabilities in the Janus model family.

For information on specific models and their capabilities, see [Models in Detail](#3). For installation and usage instructions, see [Usage Guide](#4).

## High-Level Architecture Overview

Janus is designed as a unified architecture that supports both multimodal understanding and text-to-image generation using a shared autoregressive transformer foundation. The system's architecture varies slightly between the three main variants: Janus, JanusFlow, and Janus-Pro, but they share common underlying principles.

```mermaid
graph TD
    subgraph "Janus Architecture Overview"
        MultiModalityModel["MultiModalityCausalLM"]
        
        subgraph "Vision Components"
            VisUndEncoder["Vision Understanding Encoder"]
            VisGenEncoder["Vision Generation Encoder (JanusFlow)"]
            VisGenDecoder["Vision Generation Decoder (JanusFlow)"]
            GenVisionModel["Gen Vision Model (Janus/Pro)"]
        end
        
        subgraph "Language Component"
            LLM["Language Model (Llama-based)"]
        end
        
        subgraph "Processing Components" 
            VLChatProcessor["VLChatProcessor"]
            ImageProcessor["VLMImageProcessor"]
            Conversation["Conversation"]
        end
        
        VLChatProcessor --> ImageProcessor
        VLChatProcessor --> Conversation
        
        MultiModalityModel --> VisUndEncoder
        MultiModalityModel --> LLM
        
        MultiModalityModel --"Janus/Janus-Pro"--> GenVisionModel
        MultiModalityModel --"JanusFlow"--> VisGenEncoder
        MultiModalityModel --"JanusFlow"--> VisGenDecoder
        
        VLChatProcessor --> MultiModalityModel
    end
```

Sources:
- [janus/janusflow/models/modeling_vlm.py:132-227]()
- [README.md:10-101]()

## Core Components

The Janus architecture is built around several key components that work together to provide multimodal capabilities:

### MultiModalityCausalLM

This is the central model class that integrates vision and language components. It serves as the backbone of the Janus architecture, connecting vision encoders/decoders with the language model.

```mermaid
classDiagram
    class MultiModalityCausalLM {
        +vision_und_enc_model
        +vision_und_enc_aligner
        +language_model
        +vision_gen_enc_model (JanusFlow)
        +vision_gen_enc_aligner (JanusFlow)
        +vision_gen_dec_model (JanusFlow)
        +vision_gen_dec_aligner (JanusFlow)
        +gen_vision_model (Janus/Pro)
        +gen_head (Janus/Pro)
        +prepare_inputs_embeds()
        +prepare_gen_img_embeds()
    }
    
    MultiModalityCausalLM --> "1" LlamaForCausalLM: language_model
    MultiModalityCausalLM --> "1" VisionUnderstandingEncoder: vision_und_enc_model
    MultiModalityCausalLM --> "0..1" VisionGenerationEncoder: vision_gen_enc_model
    MultiModalityCausalLM --> "0..1" VisionGenerationDecoder: vision_gen_dec_model
```

The MultiModalityCausalLM class handles:
- Integrating vision and language models
- Converting between different embedding spaces through aligners
- Preparing input embeddings for the model
- Managing the generation of images or text responses

Sources:
- [janus/janusflow/models/modeling_vlm.py:132-220]()
- [README.md:87-101]()

### Processing Components

The processing pipeline is responsible for preparing inputs for the model:

```mermaid
classDiagram
    class VLChatProcessor {
        +tokenizer
        +image_processor
        +image_tag
        +image_start_tag
        +image_end_tag
        +sft_format
        +process_one()
        +batchify()
        +apply_sft_template_for_multi_turn_prompts()
    }
    
    class VLMImageProcessor {
        +image_size
        +image_mean
        +image_std
        +preprocess()
    }
    
    class Conversation {
        +name
        +system_template
        +system_message
        +roles
        +messages
        +get_prompt()
        +append_message()
    }
    
    VLChatProcessor --> VLMImageProcessor: uses
    VLChatProcessor --> Conversation: manages
```

- **VLChatProcessor**: Prepares inputs for the model, including tokenizing text and processing images
- **VLMImageProcessor**: Handles image preprocessing, such as resizing and normalization
- **Conversation**: Manages conversation history and formats prompts for the model

Sources:
- [janus/janusflow/models/__init__.py:20-28]()
- [README.md:347-353]()

## Vision Components

The vision components are responsible for processing images in both understanding and generation modes:

### Vision Understanding Encoder

This component (typically a CLIPVisionTower) processes input images to extract features for understanding tasks:

```mermaid
graph TD
    subgraph "Vision Understanding Pipeline"
        InputImage["Input Image"]
        CLIPVisionTower["CLIPVisionTower"]
        VisFeatures["Vision Features"]
        Aligner["Vision Understanding Aligner"]
        LLMEmbeddings["LLM-Compatible Embeddings"]
        
        InputImage --> CLIPVisionTower
        CLIPVisionTower --> VisFeatures
        VisFeatures --> Aligner
        Aligner --> LLMEmbeddings
    end
```

Sources:
- [janus/janusflow/models/modeling_vlm.py:138-143]()
- [janus/janusflow/models/clip_encoder.py]() (referenced but not shown in the provided files)

### Vision Generation Components

For text-to-image generation, Janus uses different architectures based on the model variant:

#### Janus and Janus-Pro

```mermaid
graph TD
    subgraph "Janus/Janus-Pro Image Generation"
        TextEmb["Text Embedding"]
        LLM["Language Model"]
        GenHead["Generation Head"]
        GenVisionModel["Gen Vision Model"]
        Image["Generated Image"]
        
        TextEmb --> LLM
        LLM --> GenHead
        GenHead --> GenVisionModel
        GenVisionModel --> Image
    end
```

#### JanusFlow

```mermaid
graph TD
    subgraph "JanusFlow Image Generation"
        TextEmb["Text Embedding"]
        LLM["Language Model"]
        VisGenEncoder["Vision Generation Encoder"]
        VisGenDecoder["Vision Generation Decoder"]
        ODESolver["Rectified Flow ODE"]
        VAE["SDXL VAE"]
        Image["Generated Image"]
        
        TextEmb --> LLM
        VisGenEncoder --> LLM
        LLM --> VisGenDecoder
        VisGenEncoder --> ODESolver
        VisGenDecoder --> ODESolver
        ODESolver --> VAE
        VAE --> Image
    end
```

In JanusFlow, the vision generation uses a rectified flow approach with specialized encoder and decoder components, while Janus and Janus-Pro use a more direct token-by-token generation approach.

Sources:
- [janus/janusflow/models/modeling_vlm.py:148-169]()
- [janus/janusflow/models/uvit.py]() (referenced but not shown in the provided files)
- [README.md:573-698]()

## Processing Flows

### Multimodal Understanding Flow

The process for understanding images and text together follows this flow:

```mermaid
sequenceDiagram
    participant User
    participant VLChatProcessor
    participant MultiModalityCausalLM
    participant VisionEncoder
    participant LanguageModel

    User->>VLChatProcessor: Input image and text question
    VLChatProcessor->>VLChatProcessor: Tokenize text
    VLChatProcessor->>VLChatProcessor: Process images
    VLChatProcessor->>MultiModalityCausalLM: Prepare inputs
    MultiModalityCausalLM->>VisionEncoder: Extract image features
    VisionEncoder->>MultiModalityCausalLM: Return vision embeddings
    MultiModalityCausalLM->>MultiModalityCausalLM: Align vision embeddings
    MultiModalityCausalLM->>LanguageModel: Combine text and vision embeddings
    LanguageModel->>MultiModalityCausalLM: Generate response
    MultiModalityCausalLM->>VLChatProcessor: Return text output
    VLChatProcessor->>User: Text response
```

Sources:
- [README.md:324-371]()

### Text-to-Image Generation Flow

#### Janus/Janus-Pro Generation Flow

```mermaid
sequenceDiagram
    participant User
    participant VLChatProcessor
    participant MultiModalityCausalLM
    participant LanguageModel
    participant GenHead
    participant GenVisionModel

    User->>VLChatProcessor: Input text prompt
    VLChatProcessor->>MultiModalityCausalLM: Prepare input with image tag
    MultiModalityCausalLM->>LanguageModel: Process text input
    
    loop For each image token
        LanguageModel->>GenHead: Generate next token
        GenHead->>MultiModalityCausalLM: Return image token
        MultiModalityCausalLM->>LanguageModel: Feed token back
    end
    
    MultiModalityCausalLM->>GenVisionModel: Generated tokens
    GenVisionModel->>User: Output image
```

#### JanusFlow Generation Flow

```mermaid
sequenceDiagram
    participant User
    participant VLChatProcessor
    participant MultiModalityCausalLM
    participant VisGenEncoder
    participant LanguageModel
    participant VisGenDecoder
    participant ODESolver
    participant VAE

    User->>VLChatProcessor: Input text prompt
    VLChatProcessor->>MultiModalityCausalLM: Prepare input with image tag
    
    loop For ODE steps
        MultiModalityCausalLM->>VisGenEncoder: Initial latent & timestep
        VisGenEncoder->>LanguageModel: Vision features & embeddings
        LanguageModel->>VisGenDecoder: Hidden states
        VisGenDecoder->>ODESolver: Velocity prediction
        ODESolver->>MultiModalityCausalLM: Update latent
    end
    
    MultiModalityCausalLM->>VAE: Final latent
    VAE->>User: Output image
```

Sources:
- [README.md:374-470]() (Janus)
- [README.md:575-697]() (JanusFlow)

## Model Variants and Architecture Differences

While all Janus models share a common core architecture, there are key differences between the variants:

### Janus vs JanusFlow Architecture

```mermaid
graph TB
    subgraph "Common Components"
        VLC["VLChatProcessor"]
        MMLM["MultiModalityCausalLM"]
        VUE["Vision Understanding Encoder"]
        LLM["Language Model"]
    end
    
    subgraph "Janus/Janus-Pro"
        GVM["Gen Vision Model"]
        GH["Generation Head"]
    end
    
    subgraph "JanusFlow"
        VGE["Vision Generation Encoder"]
        VGD["Vision Generation Decoder"]
        RF["Rectified Flow ODE"]
        SDXLVAE["SDXL VAE"]
    end
    
    VLC --> MMLM
    MMLM --> VUE
    MMLM --> LLM
    
    MMLM --"Janus/Pro"--> GVM
    MMLM --"Janus/Pro"--> GH
    
    MMLM --"JanusFlow"--> VGE
    MMLM --"JanusFlow"--> VGD
    VGE --"JanusFlow"--> RF
    VGD --"JanusFlow"--> RF
    RF --"JanusFlow"--> SDXLVAE
```

The key architectural differences are:

1. **Text-to-Image Generation**:
   - **Janus/Janus-Pro**: Uses a token-by-token autoregressive generation approach with a specialized GenVisionModel and GenHead
   - **JanusFlow**: Uses a rectified flow ODE approach with Vision Generation Encoder/Decoder components and a VAE for final decoding

2. **Model Size and Scaling**:
   - **Janus**: Base model at 1.3B parameters
   - **JanusFlow**: 1.3B parameters but with additional VAE component
   - **Janus-Pro**: Scaled versions at 1B and 7B parameters with optimized training

Sources:
- [README.md:86-101]() (Janus intro)
- [README.md:94-101]() (JanusFlow intro)
- [README.md:76-83]() (Janus-Pro intro)

### Implementation Details

The MultiModalityCausalLM class is implemented differently for each variant but follows similar principles:

```mermaid
classDiagram
    class MultiModalityConfig {
        +vision_und_enc_config
        +vision_gen_enc_config
        +vision_gen_dec_config
        +language_config
    }
    
    class MultiModalityCausalLM {
        +vision_und_enc_model
        +vision_und_enc_aligner
        +language_model
        +prepare_inputs_embeds()
    }
    
    MultiModalityConfig --* MultiModalityCausalLM: configures
```

The implementation includes configuration classes that define the model components and their parameters:
- VisionUnderstandEncoderConfig
- VisionGenerationEncoderConfig
- VisionGenerationDecoderConfig
- MultiModalityConfig

Sources:
- [janus/janusflow/models/modeling_vlm.py:51-124]()
- [janus/janusflow/models/modeling_vlm.py:132-169]()

## Summary

The Janus architecture is a flexible framework for multimodal understanding and generation that:

1. Uses a shared language model backbone (Llama-based) for both tasks
2. Incorporates specialized vision encoders for understanding images
3. Employs different image generation approaches based on the model variant:
   - Token-by-token generation (Janus/Janus-Pro)
   - Rectified flow ODE (JanusFlow)
4. Provides consistent processing interfaces through VLChatProcessor and related components

This unified architecture allows all Janus model variants to perform both multimodal understanding and text-to-image generation while optimizing for their specific strengths.

Sources:
- [README.md:10-101]()
- [janus/janusflow/models/modeling_vlm.py:132-227]()
- [janus/janusflow/models/__init__.py:20-28]()

---

