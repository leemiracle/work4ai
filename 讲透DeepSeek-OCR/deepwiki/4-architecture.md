> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-OCR/4-architecture](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/4-architecture)
> DeepWiki deepseek-ai/DeepSeek-OCR

# Architecture

  Relevant source files 
 - [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py)
 - [DeepSeek_OCR_paper.pdf](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek_OCR_paper.pdf)
 
  
## Purpose and Scope

 This page provides a technical overview of DeepSeek-OCR's system architecture, focusing on the major structural components and how they relate to each other. It explains the dual-framework design (vLLM and Transformers), the layered component hierarchy, and the overall data flow through the system.

 For detailed information about specific subsystems, see:

 
 - Model architecture internals: [Model Architecture](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/4.2-model-architecture)
 - Vision encoders (SAM and CLIP): [Vision Encoding System](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/4.3-vision-encoding-system)
 - Image preprocessing logic: [Image Processing Pipeline](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/4.4-image-processing-pipeline)
 - How vision and text tokens are merged: [Multimodal Integration](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/4.5-multimodal-integration)
 
 For practical usage guides, see:

 
 - Configuration parameters: [Configuration System](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/3.3-configuration-system)
 - Running inference: [vLLM Inference](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/3.2-vllm-inference) and [Transformers Inference](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/3.1-transformers-inference)
 
 
---

 
## Architectural Principles

 DeepSeek-OCR is designed around several key architectural principles:

 
 - **Dual-Framework Support**: The system provides both vLLM and Transformers inference paths that share the same underlying model weights, enabling production throughput optimization and research flexibility. [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py2-38](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L2-L38)
 - **Dual-Encoder Vision**: Combines SAM (Segment Anything Model) for spatial detail with CLIP for semantic understanding, creating complementary feature representations. [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py40-41](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L40-L41)
 - **Hierarchical Resolution Processing**: Implements dynamic cropping (Gundam mode) to process large documents as multiple high-resolution local views plus one global view, balancing detail preservation with memory constraints. [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py78-106](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L78-L106)
 - **Token-Based Spatial Encoding**: Uses special learned embeddings (`image_newline`, `view_seperator`) to maintain 2D spatial relationships within the 1D token sequence fed to the language model. [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py318-322](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L318-L322)
 - **Configurable Resolution Modes**: Offers processing modes defined in `config.py` with different quality/speed/memory tradeoffs. [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py45](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L45-L45)
 
 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py1-583](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L1-L583)

 
---

 
## System Layers

 The DeepSeek-OCR system is organized into distinct layers with clear responsibilities:

 DeepSeek-OCR Component Hierarchy

 
```

```

 **Layer Responsibilities:**

 
| Layer | Components | Purpose |
|---|---|---|
| 1: Entry Points | CLI scripts | User-facing interfaces for different use cases |
| 2: Configuration | config.py | Central parameter definition (resolution, cropping, workers) |
| 3: Inference Frameworks | vLLM, Transformers | Production serving vs. research/fine-tuning |
| 4: Multimodal Processing | Processor classes | Image tokenization, aspect ratio handling, dummy inputs |
| 5: Core Model | DeepseekOCRForCausalLM | Main orchestrator, weight loading, forward pass |
| 6: Vision Encoders | SAM, CLIP | Spatial and semantic feature extraction |
| 7: Feature Projection | MlpProjector, special tokens | Dimensionality reduction, spatial structure preservation |
| 8: Language Model | DeepseekV3/V2/V1 | Causal language modeling on fused multimodal tokens |

 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py261-330](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L261-L330) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py50-255](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L50-L255)

 
---

 
## Dual-Framework Design

 DeepSeek-OCR uniquely provides two parallel inference frameworks that operate on the same model checkpoint:

 Framework Comparison and Data Paths

 
```

```

 **Framework Comparison:**

 
| Aspect | vLLM | Transformers |
|---|---|---|
| Use Case | Production serving, batch evaluation | Research, fine-tuning, experimentation |
| Engine | AsyncLLMEngine with batching | Direct model.infer() calls |
| Implementation | DeepseekOCRMultiModalProcessor | DeepseekOCRProcessor |
| Special Features | Streaming output, prefix caching | Direct logits access, test_compress |

 The `DeepseekOCRForCausalLM` class is designed to work with both frameworks through:

 
 - vLLM integration via `MULTIMODAL_REGISTRY.register_processor` decorator [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py257-260](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L257-L260)
 - Shared weight loading through `load_weights()` method [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py564-582](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L564-L582)
 
 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py257-261](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L257-L261) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py150-189](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L150-L189)

 
---

 
## Core Model Architecture

 The `DeepseekOCRForCausalLM` class orchestrates all model components:

 DeepseekOCRForCausalLM Internal Architecture

 
```

```

 **Key Methods:**

 
| Method | Location | Purpose |
|---|---|---|
| __init__() | DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py267-329 | Initialize encoders, projector, and LLM |
| _parse_and_validate_image_input() | DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py333-360 | Validate pixel_values and images_crop |
| _pixel_values_to_embedding() | DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py364-467 | Vision encoding: SAM + CLIP → projection |
| get_multimodal_embeddings() | DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py498-504 | Public API for getting vision embeddings |
| forward() | DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py530-553 | Complete forward pass through LLM |

 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py261-583](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L261-L583)

 
---

 
## Vision Encoding Pipeline

 The vision encoding pipeline implements the dual-encoder architecture:

 Vision Feature Extraction Pipeline

 
```

```

 **Encoding Steps:**

 
 - **Dual Encoding**: 
 - SAM extracts spatial features [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py394](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L394-L394)
 - CLIP extracts semantic features [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py397](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L397-L397)
 - **Feature Fusion**: Concatenates CLIP (1280) and SAM (768) features to form 2048-dim vectors [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py400](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L400-L400)
 - **Projection**: `MlpProjector` reduces dimensions to match the language model (1280) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py401](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L401-L401)
 - **Spatial Structuring**: Reshapes the 1D token stream back to 2D rows and inserts `image_newline` and `view_seperator` tokens [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py425-438](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L425-L438)
 
 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py364-467](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L364-L467)

 
---

 
## Multimodal Processing Classes

 The system uses specialized processor classes to manage the interface between raw images and model inputs:

 
| Class | Purpose | Key Methods |
|---|---|---|
| DeepseekOCRProcessingInfo | Metadata for vLLM | get_num_image_tokens() DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py61-106 |
| DeepseekOCRDummyInputsBuilder | Profiling utilities | get_dummy_mm_data() DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py126-145 |
| DeepseekOCRMultiModalProcessor | vLLM input handler | _call_hf_processor() DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py154-176 |
| DeepseekOCRProcessor | Core preprocessing | tokenize_with_images(), count_tiles() DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py30-31 |

 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py50-255](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L50-L255)

 
---

 
## Weight Loading and Model Registration

 The model uses custom weight loading to map checkpoint keys to the internal module structure:

 Weight Mapping and Loading Flow

 
```

```

 **Weight Loading Logic** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py564-582](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L564-L582): The `load_weights` method remaps keys by checking if they belong to the vision system (SAM, CLIP, Projector) or the language model. Vision keys have their `model.` prefix removed, while LLM keys are prefixed with `language.` to route them to the `self.language_model` submodule.

 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py564-582](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L564-L582)
