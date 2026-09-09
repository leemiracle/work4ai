> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-OCR/9-glossary](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/9-glossary)
> DeepWiki deepseek-ai/DeepSeek-OCR

# Glossary

  Relevant source files 
 - [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py)
 - [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/build_linear.py](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/build_linear.py)
 - [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/clip_sdpa.py](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/clip_sdpa.py)
 - [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py)
 - [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py)
 - [DeepSeek-OCR-master/DeepSeek-OCR-vllm/process/image_process.py](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/process/image_process.py)
 - [README.md](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1)
 
  This glossary provides definitions for codebase-specific terms, architectural components, and domain concepts used within the DeepSeek-OCR system. It is intended to assist onboarding engineers in navigating the vision-language model (VLM) and optical character recognition (OCR) implementations.

 
## Core Architectural Components

 
### DeepseekOCRForCausalLM

 The primary model class that integrates the dual vision encoders with the language model backbone. It handles the fusion of visual features and text embeddings for causal language generation [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py35-38](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L35-L38)

 
### Dual-Encoder System

 DeepSeek-OCR utilizes two distinct vision encoders to capture different aspects of the input image:

 
 - **SAM (Segment Anything Model) ViT-B**: Used as a high-resolution spatial encoder to capture structural and layout information [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py77-168](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py#L77-L168)
 - **CLIP-L (Contrastive Language-Image Pre-training)**: Used as a semantic encoder to provide high-level visual context [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/clip_sdpa.py107-156](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/clip_sdpa.py#L107-L156)
 
 
### MlpProjector

 A modular component responsible for projecting vision encoder features into the language model's embedding space. It supports various architectures including linear, MLP with GELU activation, and downsampling variants [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/build_linear.py7-95](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/build_linear.py#L7-L95)

 
### DeepseekOCRProcessor

 The unified preprocessing class that handles image transformations, dynamic cropping, and tokenization. It ensures that images are correctly formatted for the dual encoders and that the text prompt is properly interleaved with vision tokens [DeepSeek-OCR-master/DeepSeek-OCR-vllm/process/image_process.py111-179](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/process/image_process.py#L111-L179)

 
## Vision-Language Concepts

 
### Vision Tokens

 The sequence of embeddings generated from an image. In DeepSeek-OCR, the number of tokens varies based on the resolution mode (e.g., 1024x1024 produces 256 tokens after a 4x downsampling ratio) [README.md192-196](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L192-L196)

 
### Dynamic Preprocessing (Gundam Mode)

 A strategy where an image is split into multiple local "crops" (tiles) plus a global thumbnail. This allows the model to process high-resolution documents without exceeding the vision encoder's native input size [DeepSeek-OCR-master/DeepSeek-OCR-vllm/process/image_process.py45-83](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/process/image_process.py#L45-L83)

 
### Downsample Ratio

 The factor by which the spatial resolution of vision features is reduced before being fed into the LLM. DeepSeek-OCR typically uses a ratio of 4, meaning a $16 \times 16$ patch grid is reduced to a smaller representation to save context window space [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py76-98](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L76-L98)

 
## Special Tokens and Prompts

 
| Token | Description |
|---|---|
| <image> | Placeholder token in the text prompt where visual embeddings are inserted DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py47 |
| `< | grounding |
| `< | ref |
| <td>, <tr> | HTML-style tokens used for structured table parsing, often whitelisted in logits processors to prevent repetition README.md154-155 |

 
## Code-to-System Mapping

 
### Data Flow: Image to Embeddings

 The following diagram illustrates how an input image is processed through the `DeepseekOCRProcessor` and projected into the LLM space via the `MlpProjector`.

 **Vision Processing Pipeline**

 
```

```

 Sources: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/process/image_process.py45-111](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/process/image_process.py#L45-L111) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/build_linear.py54-75](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/build_linear.py#L54-L75) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py35-43](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L35-L43)

 
### Logical Architecture: Framework Integration

 DeepSeek-OCR supports both standard `transformers` and high-performance `vLLM` inference.

 **Framework Integration Diagram**

 
```

```

 Sources: [README.md118-130](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L118-L130) [README.md167-183](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L167-L183) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py17-24](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L17-L24)

 
## Configuration Parameters

 
### Resolution Settings

 
 - **BASE_SIZE**: The resolution used for the global thumbnail (e.g., 1024) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py8](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L8-L8)
 - **IMAGE_SIZE**: The resolution used for individual local crops (e.g., 640) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py9](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L9-L9)
 - **CROP_MODE**: Boolean flag to enable or disable dynamic resolution/cropping [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py10](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L10-L10)
 
 
### Resource Management

 
 - **MAX_CROPS**: The maximum number of tiles the `dynamic_preprocess` function is allowed to generate (typically 6-9) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py12](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L12-L12)
 - **MAX_CONCURRENCY**: Controls the number of parallel requests in vLLM to manage VRAM usage [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py13](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L13-L13)
 
 
### Logits Processing

 
 - **NGramPerReqLogitsProcessor**: A custom vLLM logits processor used to suppress repetitive n-grams during long document OCR, improving output quality [README.md120-128](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L120-L128)
 
 Sources: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py1-17](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L1-L17) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/process/image_process.py28-42](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/process/image_process.py#L28-L42)
