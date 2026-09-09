> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-VL/3-components](https://deepwiki.com/deepseek-ai/DeepSeek-VL/3-components)
> DeepWiki deepseek-ai/DeepSeek-VL

# Components

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/README.md?plain=1)
 - [deepseek_vl/__init__.py](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/deepseek_vl/__init__.py)
 - [deepseek_vl/models/siglip_vit.py](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/deepseek_vl/models/siglip_vit.py)
 - [inference.py](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/inference.py)
 
  This page provides a comprehensive overview of the main components that make up the DeepSeek-VL system. DeepSeek-VL is a vision-language model designed to process and understand both visual and textual information, generating cohesive natural language responses. For information about model architecture specifics, see [Model Architecture](https://deepwiki.com/deepseek-ai/DeepSeek-VL/1.1-model-architecture). For details on installation and usage, see [Getting Started](https://deepwiki.com/deepseek-ai/DeepSeek-VL/2-getting-started).

 
## Core Components Overview

 DeepSeek-VL is composed of several key components that work together to enable multimodal understanding. These components can be categorized into three main subsystems:

 
```

```

 Sources: [README.md60-68](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/README.md?plain=1#L60-L68) [inference.py20-37](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/inference.py#L20-L37)

 
## Component Interaction Flow

 The following diagram illustrates how these components interact during the inference process:

 
```

```

 Sources: [inference.py64-86](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/inference.py#L64-L86)

 
## Vision Processing Component

 The vision component of DeepSeek-VL is based on a SigLIP (Simple Gated CLIP) Vision Transformer architecture.

 
### Vision Transformer

 
```

```

 The VisionTransformer processes images through the following steps:

 
 - Images are divided into patches using the PatchEmbed component
 - Positional embeddings are added to provide spatial information
 - The embedded patches are processed through a series of transformer blocks
 - Each block contains self-attention mechanisms and MLP layers
 - The output is a sequence of token embeddings representing the visual content
 
 The primary implementation is in the `VisionTransformer` class, with different configurations available based on model size:

 
 - SigLIP SO400M patch14 (384px)
 - SigLIP SO400M patch14 (224px)
 - SigLIP Large patch16 (384px)
 
 Sources: [deepseek_vl/models/siglip_vit.py259-589](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/deepseek_vl/models/siglip_vit.py#L259-L589) [deepseek_vl/models/siglip_vit.py606-626](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/deepseek_vl/models/siglip_vit.py#L606-L626)

 
## Language Processing Component

 The language model component is a decoder-only transformer architecture that processes tokenized text and generates responses. It works with the embeddings provided by the multimodal integration component.

 The language model:

 
 - Takes combined visual and textual embeddings as input
 - Uses the causal attention mechanism to generate tokens sequentially
 - Processes through transformer blocks with self-attention and feed-forward layers
 - Outputs probability distributions over vocabulary tokens
 
 The generation process is controlled by parameters such as:

 
 - `max_new_tokens`: Maximum length of the generated response
 - `do_sample`: Whether to use sampling techniques for generation
 - `use_cache`: Enables faster generation by caching key/value pairs
 
 Sources: [inference.py73-84](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/inference.py#L73-L84)

 
## Multimodal Integration Component

 The `MultiModalityCausalLM` is the core component that bridges vision and language processing, implemented as a class that inherits from `AutoModelForCausalLM`.

 
```

```

 The `MultiModalityCausalLM` performs these key functions:

 
 - Processes images through the vision encoder
 - Projects image embeddings to the language model's dimension space
 - Combines image and text embeddings in the proper sequence
 - Passes the combined embeddings to the language model for generation
 - The crucial method `prepare_inputs_embeds()` handles the fusion of modalities
 
 Sources: [inference.py31-32](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/inference.py#L31-L32) [inference.py70-71](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/inference.py#L70-L71)

 
## Processing Pipeline Components

 
### VLChatProcessor

 The `VLChatProcessor` is responsible for preparing inputs for the model by handling both text and images:

 
```

```

 The VLChatProcessor handles:

 
 - Loading and preprocessing images from file paths
 - Converting conversation format to model-compatible format
 - Handling image placeholders in text
 - Tokenizing text content
 - Creating attention masks
 - Packaging all inputs in a format expected by the model
 
 Sources: [inference.py23-24](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/inference.py#L23-L24) [inference.py65-68](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/inference.py#L65-L68)

 
### Image Processing

 Image processing in DeepSeek-VL involves:

 
 - Loading images using PIL
 - Resizing and normalizing images
 - Preparing images for the vision encoder
 
 The `load_pil_images` utility function handles converting image paths to PIL Image objects for processing.

 Sources: [inference.py65](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/inference.py#L65-L65) [README.md164](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/README.md?plain=1#L164-L164)

 
### Text Processing

 Text processing involves:

 
 - Tokenization of text inputs
 - Handling special tokens like image placeholders
 - Creating attention masks for the transformer model
 - Handling the conversation format with roles (User/Assistant)
 
 The tokenizer is a core component used for both encoding inputs and decoding generated outputs.

 Sources: [inference.py23-29](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/inference.py#L23-L29) [inference.py85-86](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/inference.py#L85-L86)

 
## Component Implementation Details

 
### Model Variants

 DeepSeek-VL components are available in different configurations:

 
| Model Variant | Parameter Size | Vision Encoder | Language Model |
|---|---|---|---|
| DeepSeek-VL-1.3B-base | 1.3 Billion | SigLIP-based VisionTransformer | 1.3B LM |
| DeepSeek-VL-1.3B-chat | 1.3 Billion | SigLIP-based VisionTransformer | 1.3B LM (chat-tuned) |
| DeepSeek-VL-7B-base | 7 Billion | SigLIP-based VisionTransformer | 7B LM |
| DeepSeek-VL-7B-chat | 7 Billion | SigLIP-based VisionTransformer | 7B LM (chat-tuned) |

 All variants share the same component architecture but differ in the size and capabilities of individual components.

 Sources: [README.md91-103](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/README.md?plain=1#L91-L103)

 
### Loading Components

 Components are typically loaded and initialized as follows:

 
 - Load the VLChatProcessor from the model path
 - Extract the tokenizer from the processor
 - Load the MultiModalityCausalLM model
 - Convert model to appropriate precision (e.g., bfloat16)
 - Move model to appropriate device (e.g., CUDA)
 
 This pattern is consistent across different interfaces (CLI, Gradio, Python API).

 Sources: [inference.py27-34](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/inference.py#L27-L34) [README.md129-133](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/README.md?plain=1#L129-L133)

 
## Component Relationships in Codebase

 The following diagram shows how the components are structured in the codebase:

 
```

```

 Sources: [README.md192-203](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/README.md?plain=1#L192-L203) [inference.py20-24](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/inference.py#L20-L24)

 The DeepSeek-VL component architecture is designed to be modular and flexible, allowing for different model sizes and applications while maintaining a consistent interface for developers.
