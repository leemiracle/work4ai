> 来源: [https://deepwiki.com/deepseek-ai/DualPipe/6-api-reference](https://deepwiki.com/deepseek-ai/DualPipe/6-api-reference)
> DeepWiki deepseek-ai/DualPipe

# API Reference

  Relevant source files 
 - [DeepSeek-OCR-master/DeepSeek-OCR-hf/run_dpsk_ocr.py](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-hf/run_dpsk_ocr.py)
 - [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py)
 
  This document provides a complete reference for all public interfaces in the DeepSeek-OCR codebase. The API is organized into five main categories: Transformers interface for standard HuggingFace workflows, vLLM interface for production deployment, configuration system, image processing utilities, and vision encoder modules.

 For implementation guides and usage patterns, see [User Guide](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/3-user-guide). For architectural details about how these APIs work internally, see [Architecture](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/4-architecture).

 
## API Structure Overview

 DeepSeek-OCR exposes two primary inference interfaces: a standard Transformers-based API for development and experimentation, and a vLLM-based API for high-throughput production use. Both interfaces share the same underlying model architecture and processing pipeline but differ in execution strategy.

 
```

```

 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-hf/run_dpsk_ocr.py1-35](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-hf/run_dpsk_ocr.py#L1-L35) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py1-583](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L1-L583)

 
## API Categories

 
### Transformers API ([Transformers API](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/6.1-transformers-api))

 The Transformers API provides a simple, synchronous interface for OCR inference using HuggingFace's standard model loading and inference patterns.

 
| Component | Purpose | Key Methods |
|---|---|---|
| AutoModel.from_pretrained() | Load model from HuggingFace | Standard HF loading |
| model.infer() | Execute OCR inference | Single entry point for all OCR tasks |
| AutoTokenizer.from_pretrained() | Load tokenizer | Standard HF tokenizer loading |

 **Primary Entry Point:** `model.infer(tokenizer, prompt, image_file, output_path, base_size, image_size, crop_mode, test_compress, save_results)` [DeepSeek-OCR-master/DeepSeek-OCR-hf/run_dpsk_ocr.py25-34](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-hf/run_dpsk_ocr.py#L25-L34)

 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-hf/run_dpsk_ocr.py1-35](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-hf/run_dpsk_ocr.py#L1-L35)

 
### vLLM Model API ([vLLM Model API](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/6.2-vllm-model-api))

 The vLLM API provides asynchronous, high-throughput inference capabilities with GPU memory optimization and batch processing.

 
| Component | Purpose | Key Methods |
|---|---|---|
| DeepseekOCRForCausalLM | Main model class for vLLM | forward(), get_multimodal_embeddings(), load_weights() |
| DeepseekOCRMultiModalProcessor | Multimodal input processing | _call_hf_processor(), _get_prompt_updates() |
| DeepseekOCRProcessingInfo | vLLM configuration metadata | get_num_image_tokens(), get_image_size_with_most_features() |
| DeepseekOCRDummyInputsBuilder | Profiling support | get_dummy_text(), get_dummy_mm_data() |

 **Primary Entry Point:** Registered with `@MULTIMODAL_REGISTRY.register_processor()` at [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py257-260](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L257-L260)

 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py50-583](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L50-L583)

 
### Configuration API ([Configuration API](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/6.3-configuration-api))

 Centralized configuration parameters that control all aspects of model behavior, from image preprocessing to inference settings.

 
| Parameter Category | Examples | Effect |
|---|---|---|
| Image Resolution | IMAGE_SIZE, BASE_SIZE | Controls input image dimensions |
| Processing Mode | CROP_MODE, MIN_CROPS, MAX_CROPS | Enables/configures dynamic tiling |
| Model Selection | MODEL_PATH, PROMPT | Specifies model and task |

 **Configuration Source:** `config.py` module (imported throughout codebase) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py45](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L45-L45)

 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py45](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L45-L45)

 
### Processing API ([Processing API](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/6.4-processing-api))

 The Processing API handles image preprocessing, tokenization, and conversion of raw inputs into model-ready tensors.

 
| Component | Purpose | Key Methods |
|---|---|---|
| DeepseekOCRProcessor | Main processor class | tokenize_with_images(), dynamic_preprocess() |
| count_tiles() | Tile count calculation | Determines crop grid dimensions |

 **Primary Entry Point:** `DeepseekOCRProcessor.tokenize_with_images(images, bos, eos, cropping)` [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py138-140](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L138-L140)

 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py30-31](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L30-L31) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py138-140](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L138-L140)

 
### Encoder API ([Encoder API](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/6.5-encoder-api))

 The Encoder API provides access to the dual vision encoding system that extracts visual features from images.

 
| Component | Purpose | Key Functions |
|---|---|---|
| build_sam_vit_b() | Build SAM encoder | Returns SAM ViT-B model |
| build_clip_l() | Build CLIP encoder | Returns CLIP-L model |
| MlpProjector | Feature projection | Projects concatenated features to LLM space |

 **Builder Functions:** Located in `deepencoder/` module [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py40-42](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L40-L42)

 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py40-42](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L40-L42) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py288-292](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L288-L292)

 
## Code-to-API Mapping

 The following diagram maps user-facing entry points to internal code components:

 
```

```

 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-hf/run_dpsk_ocr.py1-35](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-hf/run_dpsk_ocr.py#L1-L35) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py261-582](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L261-L582)

 
## Special Tokens and Parameters

 DeepSeek-OCR uses several special tokens and learnable parameters to structure multimodal information:

 
| Token/Parameter | Location | Purpose | Dimensions |
|---|---|---|---|
| image_newline | DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py307 | Row separator in image grids | [n_embed] |
| view_seperator | DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py308 | Separator between global/local views | [n_embed] |
| image_token_id | DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py286 | Placeholder for image embeddings | Scalar (from tokenizer) |
| _IMAGE_TOKEN | DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py47 | String token "<image>" | String constant |

 **Initialization:** Special tokens are initialized as learnable parameters with standard deviation `1/sqrt(n_embed)` at [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py304-312](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L304-L312)

 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py47](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L47-L47) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py286](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L286-L286) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py304-312](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L304-L312)

 
## Model Registration and Integration

 The vLLM integration uses a registration system to enable custom multimodal models:

 
```

```

 **Registration Call:** `@MULTIMODAL_REGISTRY.register_processor(DeepseekOCRMultiModalProcessor, info=DeepseekOCRProcessingInfo, dummy_inputs=DeepseekOCRDummyInputsBuilder)` at [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py257-260](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L257-L260)

 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py257-260](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L257-L260)

 
## Weight Loading and Name Mapping

 The model uses a custom weight mapper to handle differences between HuggingFace checkpoint names and vLLM internal structure:

 
| HuggingFace Name Pattern | vLLM Name Pattern | Transformation |
|---|---|---|
| language.* | language_model.* | Prefix replacement |
| sam_model.* | sam_model.* | Direct (remove model. prefix) |
| vision_model.* | vision_model.* | Direct (remove model. prefix) |
| projector.* | projector.* | Direct (remove model. prefix) |
| image_newline | image_newline | Direct (remove model. prefix) |
| view_seperator | view_seperator | Direct (remove model. prefix) |

 **Mapper Definition:** `hf_to_vllm_mapper = WeightsMapper(orig_to_new_prefix={"language.": "language_model."})` at [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py263-265](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L263-L265)

 **Weight Loading Logic:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py564-582](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L564-L582)

 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py263-265](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L263-L265) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py564-582](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L564-L582)

 
## Operational Modes Reference

 DeepSeek-OCR supports five preconfigured operational modes with different resolution and cropping settings:

 
| Mode | base_size | image_size | crop_mode | Use Case |
|---|---|---|---|---|
| Tiny | 512 | 512 | False | Low-resource inference |
| Small | 640 | 640 | False | Standard single-view |
| Base | 1024 | 1024 | False | High-resolution single-view |
| Large | 1280 | 1280 | False | Very high-resolution single-view |
| Gundam | 1024 | 640 | True | Multi-scale with dynamic tiling (default) |

 **Configuration Reference:** [DeepSeek-OCR-master/DeepSeek-OCR-hf/run_dpsk_ocr.py27-32](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-hf/run_dpsk_ocr.py#L27-L32)

 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-hf/run_dpsk_ocr.py27-32](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-hf/run_dpsk_ocr.py#L27-L32)

 
## Data Flow Through APIs

 This diagram shows how data flows through the API layers:

 
```

```

 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py261-583](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L261-L583) [DeepSeek-OCR-master/DeepSeek-OCR-hf/run_dpsk_ocr.py1-35](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-hf/run_dpsk_ocr.py#L1-L35)

 
## Detailed API References

 For detailed documentation of each API category, see the following pages:

 
 - **[Transformers API](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/6.1-transformers-api)** - Complete reference for `model.infer()` and standard HuggingFace interface
 - **[vLLM Model API](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/6.2-vllm-model-api)** - Detailed documentation of `DeepseekOCRForCausalLM` and vLLM-specific classes
 - **[Configuration API](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/6.3-configuration-api)** - Comprehensive parameter reference with default values and effects
 - **[Processing API](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/6.4-processing-api)** - Documentation for `DeepseekOCRProcessor`, image transforms, and utilities
 - **[Encoder API](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/6.5-encoder-api)** - Reference for vision encoder construction and usage
 
 Each subsection provides method signatures, parameter descriptions, return types, and usage examples.
