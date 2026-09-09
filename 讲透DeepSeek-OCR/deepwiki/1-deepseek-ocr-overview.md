> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-OCR/1-deepseek-ocr-overview](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/1-deepseek-ocr-overview)
> DeepWiki deepseek-ai/DeepSeek-OCR

# DeepSeek-OCR Overview

  Relevant source files 
 - [DeepSeek_OCR_paper.pdf](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek_OCR_paper.pdf)
 - [README.md](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1)
 - [assets/badge.svg](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/assets/badge.svg)
 - [assets/fig1.png](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/assets/fig1.png)
 - [assets/logo.svg](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/assets/logo.svg)
 
  
## Purpose and Scope

 DeepSeek-OCR is a specialized vision-language model architecture designed for high-performance optical character recognition (OCR) and document understanding. It investigates the role of vision encoders from an LLM-centric viewpoint, specifically optimizing how visual features are compressed and presented to a Large Language Model (LLM) for text extraction and layout analysis [README.md57-58](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L57-L58)

 The system is designed with a dual-framework approach:

 
 - **Production-oriented vLLM integration** for high-throughput processing (~2500 tokens/s on A100) [README.md100-103](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L100-L103)
 - **Research-oriented Transformers interface** for fine-grained control over image processing parameters [README.md165-183](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L165-L183)
 
 This page details the system's architecture, the relationship between its vision and language components, and the data flow through its processing pipeline.

 **Sources:** [README.md35-58](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L35-L58) [README.md89-107](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L89-L107)

 
---

 
## Key Capabilities

 DeepSeek-OCR supports multiple task-specific prompts that trigger different behaviors in the underlying `DeepseekOCRForCausalLM` model.

 
| Capability | Description | Prompt Template |
|---|---|---|
| Document to Markdown | Full document parsing with layout and formula preservation. | `\n< |
| Free OCR | Plain text extraction without structural layout overhead. | <image>\nFree OCR. |
| Visual Grounding | Localization of specific text elements using reference tags. | `\nLocate < |
| Figure Parsing | Specialized extraction for charts and diagrams. | <image>\nParse the figure. |
| General Description | Detailed visual understanding of non-textual elements. | <image>\nDescribe this image in detail. |

 **Sources:** [README.md178-179](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L178-L179) [README.md201-209](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L201-L209)

 
---

 
## System Architecture

 
### High-Level Design

 The system architecture bridges "Natural Language Space" (prompts and generated text) with "Code Entity Space" (model classes and processing logic) through a unified `DeepseekOCRForCausalLM` backbone.

 
#### System Entry Points and Workflows

 The following diagram illustrates how user-facing scripts interact with the core engine components.

 Title: DeepSeek-OCR Execution Flow

 
```

```

 **Sources:** [README.md91-107](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L91-L107) [README.md119-129](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L119-L129) [README.md168-176](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L168-L176)

 
---

 
### Dual Framework Approach

 DeepSeek-OCR maintains two distinct implementation paths to satisfy different performance requirements.

 
#### 1. vLLM Framework (High Throughput)

 The vLLM implementation is located in `DeepSeek-OCR-vllm/`. It is optimized for batch processing and high concurrency.

 
 - **Engine:** Uses the `vllm.LLM` class for execution [README.md124-129](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L124-L129)
 - **Repetition Control:** Implements `NGramPerReqLogitsProcessor` (also referred to as `NoRepeatNGramLogitsProcessor`) to prevent the model from getting stuck in repetitive loops during long document generation [README.md120-129](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L120-L129)
 - **Sampling:** Configured via `SamplingParams` with specific `extra_args` for n-gram windowing [README.md147-157](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L147-L157)
 
 
#### 2. Transformers Framework (Research & Control)

 The Transformers implementation is located in `DeepSeek-OCR-hf/`. It exposes the `model.infer()` method for direct manipulation of the vision pipeline.

 
 - **Model Loading:** Uses `AutoModel.from_pretrained` with `trust_remote_code=True` [README.md174-175](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L174-L175)
 - **Inference Method:** The `model.infer()` function allows users to toggle `crop_mode`, `base_size`, and `test_compress` dynamically [README.md183](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L183-L183)
 
 **Sources:** [README.md109-164](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L109-L164) [README.md165-189](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L165-L189)

 
---

 
## Model Architecture: DeepseekOCRForCausalLM

 The core of the system is the `DeepseekOCRForCausalLM` class. It employs a dual-encoder vision system to capture both high-level semantics and fine-grained spatial details.

 Title: DeepseekOCRForCausalLM Internal Structure

 
```

```

 
### Vision Encoders

 
 - **SAM ViT-B:** Built via `build_sam_vit_b`. This encoder focuses on spatial features and fine-grained details necessary for character recognition [README.md176-183](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L176-L183)
 - **CLIP-L:** Built via `build_clip_l`. This encoder provides semantic context, helping the model understand the overall structure of the document or image [README.md176-183](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L176-L183)
 
 
### Feature Projection

 The `MlpProjector` handles the dimensionality reduction from the combined vision encoders (2048 dimensions) to the language model's embedding space (1280 dimensions). It supports different strategies such as `downsample`, `split`, and `hybrid` projection [README.md183](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L183-L183)

 **Sources:** [README.md168-183](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L168-L183)

 
---

 
## Resolution and Processing Modes

 DeepSeek-OCR handles images using several resolution modes, ranging from static native resolutions to a dynamic multi-scale approach.

 
### Native Resolution Modes

 These modes process the image at a fixed size, resulting in a constant number of vision tokens:

 
 - **Tiny:** 512×512 (64 tokens) [README.md193](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L193-L193)
 - **Small:** 640×640 (100 tokens) [README.md194](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L194-L194)
 - **Base:** 1024×1024 (256 tokens) [README.md195](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L195-L195)
 - **Large:** 1280×1280 (400 tokens) [README.md196](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L196-L196)
 
 
### Dynamic Resolution (Gundam Mode)

 The "Gundam" mode is the most advanced processing strategy. It uses an asymmetric approach:

 
 - **Global View:** 1 view at `1024×1024` resolution to capture layout [README.md198](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L198-L198)
 - **Local Views:** `n` crops at `640×640` resolution to capture fine text [README.md198](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L198-L198)
 - **Integration:** The `DeepseekOCRProcessor` manages the cropping and inserts special tokens like `view_separator` and `image_newline` to maintain spatial relationships [README.md183](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L183-L183)
 
 **Sources:** [README.md183](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L183-L183) [README.md191-199](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L191-L199)
