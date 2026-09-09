> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-VL2/3-input-processing](https://deepwiki.com/deepseek-ai/DeepSeek-VL2/3-input-processing)
> DeepWiki deepseek-ai/DeepSeek-VL2

# Input Processing

  Relevant source files 
 - [deepseek_vl2/models/modeling_deepseek_vl_v2.py](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/models/modeling_deepseek_vl_v2.py)
 - [deepseek_vl2/models/processing_deepseek_vl_v2.py](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/models/processing_deepseek_vl_v2.py)
 
  This document explains how DeepSeek-VL2 processes inputs (images and text) before they are fed to the model. Input processing is a critical component that transforms raw user inputs into the format required by the multimodal model architecture. For information about the overall model architecture, see [Model Architecture](https://deepwiki.com/deepseek-ai/DeepSeek-VL2/2-model-architecture).

 
## Overview of Input Processing

 The input processing system in DeepSeek-VL2 handles both text and images, integrating them into a unified representation that can be processed by the model. The main class responsible for this process is `DeepseekVLV2Processor`, which orchestrates tokenization, image transformation, and the merging of different modalities.

 Input Processing Flow:

 
```

```

 Sources: [deepseek_vl2/models/processing_deepseek_vl_v2.py128-521](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/models/processing_deepseek_vl_v2.py#L128-L521)

 
## Key Components

 
### DeepseekVLV2Processor

 The central class responsible for processing inputs is `DeepseekVLV2Processor`. It handles:

 
 - Text tokenization using a LlamaTokenizer
 - Image transformation and processing
 - Integration of text and images into a single sequence
 - Batching multiple samples together
 
 
```

```

 Sources: [deepseek_vl2/models/processing_deepseek_vl_v2.py128-209](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/models/processing_deepseek_vl_v2.py#L128-L209) [deepseek_vl2/models/processing_deepseek_vl_v2.py102-124](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/models/processing_deepseek_vl_v2.py#L102-L124) [deepseek_vl2/models/processing_deepseek_vl_v2.py67-78](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/models/processing_deepseek_vl_v2.py#L67-L78)

 
## Text Processing

 
### Tokenization

 Text inputs are tokenized using the LlamaTokenizer, which converts text into token IDs that the model can process. The processor adds several special tokens to the tokenizer vocabulary:

 
| Token | Purpose |
|---|---|
| <image> | Marks positions where images should be inserted |
| <｜▁pad▁｜> | Used for padding sequences to the same length |
| `< | User |
| `< | ref |

 
### Conversation Formatting

 DeepSeek-VL2 supports various conversation templates. The processor can format messages according to different templates (e.g., "deepseek"), applying the appropriate structure for system messages, user messages, and assistant messages.

 
```

```

 Sources: [deepseek_vl2/models/processing_deepseek_vl_v2.py214-238](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/models/processing_deepseek_vl_v2.py#L214-L238) [deepseek_vl2/models/processing_deepseek_vl_v2.py240-322](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/models/processing_deepseek_vl_v2.py#L240-L322)

 
## Image Processing

 
### Image Transformation

 The `ImageTransform` class is responsible for converting PIL images to tensors and normalizing them. By default, it applies:

 
 - Conversion to PyTorch tensor
 - Normalization with mean and standard deviation (usually 0.5 for both)
 
 
### Resolution Selection and Tiling

 A key feature of DeepSeek-VL2's image processing is its ability to handle different image resolutions through:

 
 - Selecting an optimal resolution from candidate_resolutions
 - Creating a global view of the entire image
 - Creating multiple local views (tiles) for detailed processing
 
 
```

```

 Sources: [deepseek_vl2/models/processing_deepseek_vl_v2.py34-52](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/models/processing_deepseek_vl_v2.py#L34-L52) [deepseek_vl2/models/processing_deepseek_vl_v2.py523-597](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/models/processing_deepseek_vl_v2.py#L523-L597)

 
## Integrating Text and Images

 The method `tokenize_with_images` is responsible for integrating text and images into a unified sequence:

 
 - It splits text on `<image>` tags
 - Processes each text segment and the corresponding images
 - Creates a unified sequence with both text tokens and image tokens
 - Generates a mask (`images_seq_mask`) to identify positions containing image tokens
 
 
```

```

 For each image, the processor creates:

 
 - Tokens for the global view
 - A separator token
 - Tokens for local views (tiles)
 
 This approach preserves both global context and local details of the image.

 Sources: [deepseek_vl2/models/processing_deepseek_vl_v2.py523-597](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/models/processing_deepseek_vl_v2.py#L523-L597)

 
## Model Input Preparation

 After processing by the `DeepseekVLV2Processor`, the output is passed to the model's `prepare_inputs_embeds` method, which:

 
 - Embeds text tokens using the language model's embedding layer
 - Processes images through the vision transformer
 - Projects image features using the MLP projector
 - Integrates image embeddings into the text embeddings at positions marked by `images_seq_mask`
 
 
```

```

 Sources: [deepseek_vl2/models/modeling_deepseek_vl_v2.py336-477](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/models/modeling_deepseek_vl_v2.py#L336-L477)

 
## Spatial Representation of Images

 DeepSeek-VL2 uses a sophisticated approach to represent the spatial layout of images through two main methods:

 
### 2D Tiling (Default)

 In 2D tiling mode (`tile_tag="2D"`), the model:

 
 - Organizes image tokens in a 2D grid that preserves spatial relationships
 - Uses special tokens for newlines (`image_newline`) and separators (`view_seperator`)
 - Arranges global and local features according to `global_view_pos` (typically "head")
 
 
```

```

 Sources: [deepseek_vl2/models/modeling_deepseek_vl_v2.py410-454](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/models/modeling_deepseek_vl_v2.py#L410-L454)

 
### 1D Tiling (Alternative)

 In 1D tiling mode (`tile_tag="1D"`), the model:

 
 - Uses special tile indicator tokens to mark different parts of the image
 - Arranges tiles in a linear sequence
 
 This approach is simpler but preserves less spatial information.

 Sources: [deepseek_vl2/models/modeling_deepseek_vl_v2.py456-469](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/models/modeling_deepseek_vl_v2.py#L456-L469)

 
## Batching and Padding

 For efficient processing, multiple inputs are batched together. Since inputs have varying lengths, padding is applied to ensure all inputs in a batch have the same dimensions:

 
```

```

 The default padding strategy is "left" padding, which matches the causal attention mask used in the model. The `BatchCollateOutput` contains all necessary tensors for the model:

 
| Tensor | Purpose |
|---|---|
| input_ids | Token IDs with padding |
| attention_mask | Indicates real content vs padding |
| images | Batch of processed image tensors |
| images_seq_mask | Indicates image token positions |
| images_spatial_crop | Records tiling information |
| labels | Target IDs for training |

 Sources: [deepseek_vl2/models/processing_deepseek_vl_v2.py599-675](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/models/processing_deepseek_vl_v2.py#L599-L675)

 
## Summary

 The input processing system in DeepSeek-VL2 handles the complex task of transforming raw text and images into a format that the model can process. It preserves both the semantic content of text and the spatial structure of images, allowing the model to understand multimodal inputs effectively.

 Key functionalities include:

 
 - Text tokenization with special tokens for images
 - Image processing with global and local views
 - Integration of text and image features into a unified representation
 - Preservation of spatial information through 2D tiling
 - Efficient batching and padding for model inference
 
 This sophisticated processing pipeline enables DeepSeek-VL2 to handle a wide range of multimodal inputs while maintaining both global context and local detail.
