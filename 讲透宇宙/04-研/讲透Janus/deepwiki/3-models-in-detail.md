<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/Janus · page 3 Models in Detail · fetched 2026-10-30 -->

# Models in Detail

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [images/teaser_janusflow.png](images/teaser_janusflow.png)

</details>



This document provides comprehensive technical information about the architecture, components, and implementation details of each model in the Janus family: Janus, JanusFlow, and Janus-Pro. For installation and usage information, see [Usage Guide](#4).

## Model Family Overview

The Janus model family consists of three main variants, all built on a unified architecture that can handle both multimodal understanding and text-to-image generation:

```mermaid
graph TD
    subgraph "Janus Model Family"
        Janus["Janus-1.3B"]
        JanusFlow["JanusFlow-1.3B"]
        JanusPro1["Janus-Pro-1B"]
        JanusPro7["Janus-Pro-7B"]
    end
    
    subgraph "Capabilities"
        MultiUnderstanding["Multimodal Understanding"]
        TextToImage["Text-to-Image Generation"]
    end
    
    Janus --> MultiUnderstanding
    Janus --> TextToImage
    
    JanusFlow --> MultiUnderstanding
    JanusFlow --> TextToImage
    
    JanusPro1 --> MultiUnderstanding
    JanusPro1 --> TextToImage
    
    JanusPro7 --> MultiUnderstanding
    JanusPro7 --> TextToImage
```

Sources: [README.md:75-116]()

## Shared Architecture Components

All models in the Janus family share a common foundation built around these core components:

```mermaid
classDiagram
    class MultiModalityCausalLM {
        +language_model
        +vision_und_encoder
        +vision_und_enc_aligner
        +prepare_inputs_embeds()
        +forward()
    }
    
    class VLChatProcessor {
        +tokenizer
        +image_processor
        +image_tag
        +image_start_tag
        +image_end_tag
        +num_image_tokens
        +process_one()
        +batchify()
        +apply_sft_template_for_multi_turn_prompts()
    }
    
    class VLMImageProcessor {
        +image_size
        +rescale_factor
        +image_mean
        +image_std
        +resize()
        +preprocess()
    }
    
    class Conversation {
        +system_message
        +messages
        +roles
        +sep_style
        +get_prompt()
        +append_message()
        +reset_message()
    }
    
    MultiModalityCausalLM --> VLChatProcessor : uses
    VLChatProcessor --> VLMImageProcessor : uses
    VLChatProcessor --> Conversation : uses
```

Sources: [README.md:323-371](), [README.md:524-571]()

### Common Processing Flow

All Janus models follow the same basic processing flow for multimodal understanding:

```mermaid
flowchart LR
    Image["Image Input"] --> VLChatProcessor["VLChatProcessor"]
    Text["Text Input"] --> VLChatProcessor
    VLChatProcessor --> ProcessedInputs["Processed Inputs"]
    ProcessedInputs --> MultiModalityCausalLM["MultiModalityCausalLM.prepare_inputs_embeds()"]
    MultiModalityCausalLM --> InputsEmbeds["inputs_embeds"]
    InputsEmbeds --> LanguageModel["language_model.generate()"]
    LanguageModel --> TextOutput["Text Output"]
```

Sources: [README.md:338-371](), [README.md:539-571](), [README.md:152-184]()

## Janus Model (1.3B)

The standard Janus model implements a unified architecture that decouples visual encoding for understanding and generation tasks within a single transformer-based model.

### Janus Architecture Components

```mermaid
classDiagram
    class MultiModalityCausalLM {
        +language_model
        +vision_und_encoder
        +vision_und_enc_aligner
        +gen_vision_model
        +gen_head
        +prepare_inputs_embeds()
        +prepare_gen_img_embeds()
    }
    
    class CLIPVisionTower {
        +vision_model
        +forward()
    }
    
    class GenVisionModel {
        +decode_code()
    }
    
    MultiModalityCausalLM -- CLIPVisionTower : for understanding
    MultiModalityCausalLM -- GenVisionModel : for generation
```

Sources: [README.md:324-337](), [README.md:375-392]()

### Janus Text-to-Image Generation Process

Janus generates images using a token-by-token autoregressive approach:

```mermaid
flowchart TD
    Text["Text Prompt"] --> VLChatProcessor["VLChatProcessor"]
    VLChatProcessor --> SFTFormat["apply_sft_template_for_multi_turn_prompts()"]
    SFTFormat --> Prompt["prompt + image_start_tag"]
    
    Prompt --> InputIds["tokenizer.encode()"]
    InputIds --> ParallelTokens["Setup Parallel Tokens\n(for Classifier-Free Guidance)"]
    
    ParallelTokens --> InputEmbeds["language_model.get_input_embeddings()"]
    InputEmbeds --> ForLoop["For each position in image (576 tokens)"]
    
    ForLoop --> LLMPredict["language_model.model()"]
    LLMPredict --> GenHead["gen_head()"]
    GenHead --> CFG["Apply Classifier-Free Guidance"]
    CFG --> NextToken["Select Next Token"]
    NextToken --> GenImgEmbeds["prepare_gen_img_embeds()"]
    
    GenImgEmbeds --> ForLoop
    
    ForLoop --> GenVisionDecoding["gen_vision_model.decode_code()"]
    GenVisionDecoding --> PostProcess["Post-processing"]
    PostProcess --> GeneratedImage["Generated Image"]
```

Sources: [README.md:394-472]()

## JanusFlow Model (1.3B)

JanusFlow introduces a different approach to image generation by integrating autoregressive language models with rectified flow, while maintaining the same multimodal understanding capabilities.

### JanusFlow Architecture Components

```mermaid
classDiagram
    class MultiModalityCausalLM {
        +language_model
        +vision_und_encoder
        +vision_und_enc_aligner
        +vision_gen_enc_model
        +vision_gen_enc_aligner
        +vision_gen_dec_model
        +vision_gen_dec_aligner
        +vision_gen_dec_aligner_norm
        +prepare_inputs_embeds()
    }
    
    class VisionGenEncModel {
        +forward(z, t)
    }
    
    class VisionGenDecModel {
        +forward(hidden_states, hs, t)
    }
    
    class SDXLVAEModel {
        +decode(z)
    }
    
    MultiModalityCausalLM -- VisionGenEncModel : encodes latents
    MultiModalityCausalLM -- VisionGenDecModel : decodes features
    SDXLVAEModel -- MultiModalityCausalLM : external component
```

Sources: [README.md:525-538](), [README.md:574-597]()

### JanusFlow Text-to-Image Generation Process

JanusFlow generates images using a rectified flow approach with ODE solving:

```mermaid
flowchart TD
    Text["Text Prompt"] --> VLChatProcessor["VLChatProcessor"]
    VLChatProcessor --> SFTFormat["apply_sft_template_for_multi_turn_prompts()"]
    SFTFormat --> Prompt["prompt + image_gen_tag"]
    
    Prompt --> InputIds["tokenizer.encode()"]
    InputIds --> ParallelTokens["Setup Parallel Tokens\n(for Classifier-Free Guidance)"]
    
    RandomNoise["Random Noise z"] --> ODELoop["Rectified Flow ODE\n(num_inference_steps iterations)"]
    Timestep["Timestep t"] --> ODELoop
    
    ODELoop --> VisionGenEnc["vision_gen_enc_model(z, t)"]
    VisionGenEnc --> Encoder["z_enc, t_emb, hs"]
    Encoder --> VisionGenEncAligner["vision_gen_enc_aligner()"]
    VisionGenEncAligner --> CombinedEmbeds["Combine with text embeddings"]
    
    CombinedEmbeds --> LLM["language_model.model()"]
    LLM --> VisionGenDecAligner["vision_gen_dec_aligner()"]
    VisionGenDecAligner --> VisionGenDec["vision_gen_dec_model()"]
    VisionGenDec --> CFG["Apply Classifier-Free Guidance"]
    CFG --> UpdateZ["Update z"]
    UpdateZ --> ODELoop
    
    ODELoop --> SDXLVAE["SDXL VAE decode()"]
    SDXLVAE --> GeneratedImage["Generated Image"]
```

Sources: [README.md:599-697]()

## Janus-Pro Models (1B and 7B)

Janus-Pro models are enhanced versions of the original Janus with improved training strategies, expanded training data, and scaling to larger model sizes (available in 1B and 7B parameters).

### Janus-Pro Architecture Components

The architecture is similar to the original Janus but with enhanced components:

```mermaid
classDiagram
    class MultiModalityCausalLM {
        +language_model
        +vision_und_encoder
        +vision_und_enc_aligner
        +gen_vision_model
        +gen_head
        +prepare_inputs_embeds()
        +prepare_gen_img_embeds()
    }
    
    class EnhancedVisionEncoder {
        +vision_model
        +forward()
    }
    
    class EnhancedGenVisionModel {
        +decode_code()
    }
    
    MultiModalityCausalLM -- EnhancedVisionEncoder : for understanding
    MultiModalityCausalLM -- EnhancedGenVisionModel : for generation
```

Sources: [README.md:137-151](), [README.md:188-205]()

### Janus-Pro Improvements

The key enhancements in Janus-Pro include:

1. Optimized training strategy
2. Expanded training data
3. Scaling to larger model sizes (1B and 7B)
4. Enhanced stability for text-to-image generation
5. Significantly improved performance on both multimodal understanding and generation tasks

Sources: [README.md:75-86](), [README.md:124-185]()

## Model Comparison

### Feature Comparison

| Feature | Janus-1.3B | JanusFlow-1.3B | Janus-Pro-1B | Janus-Pro-7B |
|---------|------------|----------------|--------------|--------------|
| Parameters | 1.3B | 1.3B | 1B | 7B |
| Understanding Encoder | CLIP-based | CLIP-based | Enhanced CLIP-based | Enhanced CLIP-based |
| Generation Method | Token-by-token | Rectified Flow | Token-by-token | Token-by-token |
| Generation Implementation | Autoregressive | ODE Solver | Autoregressive | Autoregressive |
| External Components | None | SDXL VAE | None | None |
| CFG Implementation | Conditional/Unconditional Pairs | Conditional/Unconditional Pairs | Same as Janus | Same as Janus |

Sources: [README.md:103-116](), [README.md:394-472](), [README.md:599-697]()

### Processing Pipeline Comparison

```mermaid
flowchart TD
    subgraph "Multimodal Understanding (All Models)"
        Image1["Image Input"] --> VLChatProcessor1["VLChatProcessor"]
        Text1["Text Question"] --> VLChatProcessor1
        VLChatProcessor1 --> InputsEmbeds1["prepare_inputs_embeds()"]
        InputsEmbeds1 --> LLMGenerate1["language_model.generate()"]
        LLMGenerate1 --> TextOutput["Text Response"]
    end
    
    subgraph "Text-to-Image (Janus/Janus-Pro)"
        Text2["Text Prompt"] --> VLChatProcessor2["VLChatProcessor"]
        VLChatProcessor2 --> TokenGen["Token-by-Token Generation"]
        TokenGen --> GenVisionModel["gen_vision_model.decode_code()"]
        GenVisionModel --> ImageOutput1["Generated Image"]
    end
    
    subgraph "Text-to-Image (JanusFlow)"
        Text3["Text Prompt"] --> VLChatProcessor3["VLChatProcessor"]
        VLChatProcessor3 --> RectifiedFlow["Rectified Flow ODE"]
        RectifiedFlow --> VAEDecoding["SDXL VAE decode()"]
        VAEDecoding --> ImageOutput2["Generated Image"]
    end
```

Sources: [README.md:338-371](), [README.md:394-472](), [README.md:599-697]()

## Integration with Demo Applications

The models are integrated into demo applications through these implementations:

```mermaid
flowchart TD
    subgraph "Demo Applications"
        JanusDemo["app.py\n(Janus Demo)"]
        JanusFlowDemo["app_janusflow.py\n(JanusFlow Demo)"]
        JanusProDemo["app_januspro.py\n(Janus-Pro Demo)"]
    end
    
    subgraph "Model Components"
        JanusModel["janus/models/MultiModalityCausalLM"]
        JanusFlowModel["janus/janusflow/models/MultiModalityCausalLM"]
        VLChatProcessor["janus/models/VLChatProcessor"]
        Utilities["janus/utils/io"]
    end
    
    JanusDemo --> JanusModel
    JanusDemo --> VLChatProcessor
    JanusDemo --> Utilities
    
    JanusFlowDemo --> JanusFlowModel
    JanusFlowDemo --> VLChatProcessor
    JanusFlowDemo --> Utilities
    
    JanusProDemo --> JanusModel
    JanusProDemo --> VLChatProcessor
    JanusProDemo --> Utilities
```

Sources: [README.md:474-503](), [README.md:698-710](), [README.md:287-302]()

## Technical Implementation Details

### Classifier-Free Guidance

All models implement classifier-free guidance for image generation, but with different approaches:

- **Janus/Janus-Pro**: Processes paired conditional/unconditional inputs and combines logits with a weighting factor
- **JanusFlow**: Applies guidance on the velocity predictions in the rectified flow process

Sources: [README.md:425-444](), [README.md:627-680]()

### Image Token Representation

- **Janus/Janus-Pro**: Uses 576 discrete tokens (24×24 grid) for image representation
- **JanusFlow**: Uses continuous latent representation with dimensions 4×48×48

Sources: [README.md:432](), [README.md:636]()

### External Dependencies

- **Janus/Janus-Pro**: Self-contained, uses internal components only
- **JanusFlow**: Requires SDXL VAE for final image decoding

Sources: [README.md:394-472](), [README.md:594-596]()

---

