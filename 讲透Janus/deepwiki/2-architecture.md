> 来源: [https://deepwiki.com/deepseek-ai/Janus/2-architecture](https://deepwiki.com/deepseek-ai/Janus/2-architecture)
> DeepWiki deepseek-ai/Janus

# Architecture

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1)
 - [images/teaser_janusflow.png](https://github.com/deepseek-ai/Janus/blob/1daa72fa/images/teaser_janusflow.png)
 - [janus/janusflow/models/__init__.py](https://github.com/deepseek-ai/Janus/blob/1daa72fa/janus/janusflow/models/__init__.py)
 - [janus/janusflow/models/modeling_vlm.py](https://github.com/deepseek-ai/Janus/blob/1daa72fa/janus/janusflow/models/modeling_vlm.py)
 
  This document provides a detailed overview of the Janus system architecture, explaining the key components and their relationships across all Janus model variants. It covers the core systems that enable multimodal understanding (text + images) and text-to-image generation capabilities in the Janus model family.

 For information on specific models and their capabilities, see [Models in Detail](https://deepwiki.com/deepseek-ai/Janus/3-models-in-detail). For installation and usage instructions, see [Usage Guide](https://deepwiki.com/deepseek-ai/Janus/4-usage-guide).

 
## High-Level Architecture Overview

 Janus is designed as a unified architecture that supports both multimodal understanding and text-to-image generation using a shared autoregressive transformer foundation. The system's architecture varies slightly between the three main variants: Janus, JanusFlow, and Janus-Pro, but they share common underlying principles.

 
```

```

 Sources:

 
 - [janus/janusflow/models/modeling_vlm.py132-227](https://github.com/deepseek-ai/Janus/blob/1daa72fa/janus/janusflow/models/modeling_vlm.py#L132-L227)
 - [README.md10-101](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L10-L101)
 
 
## Core Components

 The Janus architecture is built around several key components that work together to provide multimodal capabilities:

 
### MultiModalityCausalLM

 This is the central model class that integrates vision and language components. It serves as the backbone of the Janus architecture, connecting vision encoders/decoders with the language model.

 
```

```

 The MultiModalityCausalLM class handles:

 
 - Integrating vision and language models
 - Converting between different embedding spaces through aligners
 - Preparing input embeddings for the model
 - Managing the generation of images or text responses
 
 Sources:

 
 - [janus/janusflow/models/modeling_vlm.py132-220](https://github.com/deepseek-ai/Janus/blob/1daa72fa/janus/janusflow/models/modeling_vlm.py#L132-L220)
 - [README.md87-101](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L87-L101)
 
 
### Processing Components

 The processing pipeline is responsible for preparing inputs for the model:

 
```

```

 
 - **VLChatProcessor**: Prepares inputs for the model, including tokenizing text and processing images
 - **VLMImageProcessor**: Handles image preprocessing, such as resizing and normalization
 - **Conversation**: Manages conversation history and formats prompts for the model
 
 Sources:

 
 - [janus/janusflow/models/__init__.py20-28](https://github.com/deepseek-ai/Janus/blob/1daa72fa/janus/janusflow/models/__init__.py#L20-L28)
 - [README.md347-353](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L347-L353)
 
 
## Vision Components

 The vision components are responsible for processing images in both understanding and generation modes:

 
### Vision Understanding Encoder

 This component (typically a CLIPVisionTower) processes input images to extract features for understanding tasks:

 
```

```

 Sources:

 
 - [janus/janusflow/models/modeling_vlm.py138-143](https://github.com/deepseek-ai/Janus/blob/1daa72fa/janus/janusflow/models/modeling_vlm.py#L138-L143)
 - [janus/janusflow/models/clip_encoder.py](https://github.com/deepseek-ai/Janus/blob/1daa72fa/janus/janusflow/models/clip_encoder.py) (referenced but not shown in the provided files)
 
 
### Vision Generation Components

 For text-to-image generation, Janus uses different architectures based on the model variant:

 
#### Janus and Janus-Pro

 
```

```

 
#### JanusFlow

 
```

```

 In JanusFlow, the vision generation uses a rectified flow approach with specialized encoder and decoder components, while Janus and Janus-Pro use a more direct token-by-token generation approach.

 Sources:

 
 - [janus/janusflow/models/modeling_vlm.py148-169](https://github.com/deepseek-ai/Janus/blob/1daa72fa/janus/janusflow/models/modeling_vlm.py#L148-L169)
 - [janus/janusflow/models/uvit.py](https://github.com/deepseek-ai/Janus/blob/1daa72fa/janus/janusflow/models/uvit.py) (referenced but not shown in the provided files)
 - [README.md573-698](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L573-L698)
 
 
## Processing Flows

 
### Multimodal Understanding Flow

 The process for understanding images and text together follows this flow:

 
```

```

 Sources:

 
 - [README.md324-371](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L324-L371)
 
 
### Text-to-Image Generation Flow

 
#### Janus/Janus-Pro Generation Flow

 
```

```

 
#### JanusFlow Generation Flow

 
```

```

 Sources:

 
 - [README.md374-470](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L374-L470) (Janus)
 - [README.md575-697](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L575-L697) (JanusFlow)
 
 
## Model Variants and Architecture Differences

 While all Janus models share a common core architecture, there are key differences between the variants:

 
### Janus vs JanusFlow Architecture

 
```

```

 The key architectural differences are:

 
 - **Text-to-Image Generation**:

 
 - **Janus/Janus-Pro**: Uses a token-by-token autoregressive generation approach with a specialized GenVisionModel and GenHead
 - **JanusFlow**: Uses a rectified flow ODE approach with Vision Generation Encoder/Decoder components and a VAE for final decoding
 - **Model Size and Scaling**:

 
 - **Janus**: Base model at 1.3B parameters
 - **JanusFlow**: 1.3B parameters but with additional VAE component
 - **Janus-Pro**: Scaled versions at 1B and 7B parameters with optimized training
 
 Sources:

 
 - [README.md86-101](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L86-L101) (Janus intro)
 - [README.md94-101](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L94-L101) (JanusFlow intro)
 - [README.md76-83](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L76-L83) (Janus-Pro intro)
 
 
### Implementation Details

 The MultiModalityCausalLM class is implemented differently for each variant but follows similar principles:

 
```

```

 The implementation includes configuration classes that define the model components and their parameters:

 
 - VisionUnderstandEncoderConfig
 - VisionGenerationEncoderConfig
 - VisionGenerationDecoderConfig
 - MultiModalityConfig
 
 Sources:

 
 - [janus/janusflow/models/modeling_vlm.py51-124](https://github.com/deepseek-ai/Janus/blob/1daa72fa/janus/janusflow/models/modeling_vlm.py#L51-L124)
 - [janus/janusflow/models/modeling_vlm.py132-169](https://github.com/deepseek-ai/Janus/blob/1daa72fa/janus/janusflow/models/modeling_vlm.py#L132-L169)
 
 
## Summary

 The Janus architecture is a flexible framework for multimodal understanding and generation that:

 
 - Uses a shared language model backbone (Llama-based) for both tasks
 - Incorporates specialized vision encoders for understanding images
 - Employs different image generation approaches based on the model variant: 
 - Token-by-token generation (Janus/Janus-Pro)
 - Rectified flow ODE (JanusFlow)
 - Provides consistent processing interfaces through VLChatProcessor and related components
 
 This unified architecture allows all Janus model variants to perform both multimodal understanding and text-to-image generation while optimizing for their specific strengths.

 Sources:

 
 - [README.md10-101](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L10-L101)
 - [janus/janusflow/models/modeling_vlm.py132-227](https://github.com/deepseek-ai/Janus/blob/1daa72fa/janus/janusflow/models/modeling_vlm.py#L132-L227)
 - [janus/janusflow/models/__init__.py20-28](https://github.com/deepseek-ai/Janus/blob/1daa72fa/janus/janusflow/models/__init__.py#L20-L28)
