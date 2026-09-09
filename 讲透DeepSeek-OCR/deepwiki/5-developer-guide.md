> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-OCR/5-developer-guide](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/5-developer-guide)
> DeepWiki deepseek-ai/DeepSeek-OCR

# Developer Guide

  Relevant source files 
 - [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/build_linear.py](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/build_linear.py)
 - [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py)
 
  This guide is for developers who want to extend, customize, or deeply understand the DeepSeek-OCR codebase. It covers the key architectural components, extension points, and common patterns for modifying the system.

 **Scope**: This page provides an overview of the development architecture and common customization patterns. For detailed API references, see [API Reference](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/6-api-reference). For architectural deep-dives, see [Architecture](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/4-architecture). For specific customization tasks:

 
 - Model components and weight loading: [Model Components Reference](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/5.1-model-components-reference)
 - Custom inference logic: [Custom Logits Processors](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/5.2-custom-logits-processors)
 - Vision feature projection: [Custom Projector Architectures](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/5.3-custom-projector-architectures)
 - Image preprocessing: [Extending Image Processing](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/5.4-extending-image-processing)
 - Output parsing: [Output Post-Processing](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/5.5-output-post-processing)
 
 
---

 
## System Architecture for Developers

 The DeepSeek-OCR codebase is structured around **two parallel inference frameworks** (vLLM and Transformers) that share a common model core. Understanding this dual-path architecture is essential for development work.

 
### Core Model Class Hierarchy

 
```

```

 **Sources**: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py261-583](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L261-L583)

 
---

 
## Component Initialization Flow

 Understanding the initialization order is critical when adding custom components or modifying the architecture.

 
```

```

 **Key Configuration Points**:

 
 - **Line 288-289**: Vision encoders are instantiated with `build_sam_vit_b()` and `build_clip_l()` [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py288-289](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L288-L289)
 - **Line 292**: Projector uses `MlpProjector` with configurable `projector_type` [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py292](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L292-L292)
 - **Line 307-308**: Special tokens `image_newline` and `view_seperator` are learnable parameters [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py307-308](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L307-L308)
 - **Line 321-326**: Language model is dynamically selected based on `text_config.topk_method` [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py321-326](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L321-L326)
 
 **Sources**: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py267-330](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L267-L330) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py564-582](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L564-L582)

 
---

 
## Extension Points

 
### 1. Vision Encoder Customization

 The dual-encoder architecture can be extended or replaced. The system uses two separate encoders that are concatenated before projection.

 
```

```

 **Implementation locations**:

 
 - SAM encoder instantiation: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py288](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L288-L288)
 - CLIP encoder instantiation: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py289](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L289-L289)
 - Feature concatenation: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py400](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L400-L400) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py406](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L406-L406) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py443](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L443-L443)
 
 **Sources**: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py288-292](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L288-L292) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py394-407](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L394-L407) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py441-444](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L441-L444)

 
---

 
### 2. Projector Architecture Modification

 The `MlpProjector` reduces vision features from 2048 to 1280 dimensions. This is a key bottleneck that can be customized.

 
| Projector Parameter | Location | Purpose |
|---|---|---|
| projector_type | deepseek_ocr.py292 | Determines projection architecture |
| input_dim | deepseek_ocr.py292 | Input dimension (2048 for dual encoder) |
| n_embed | deepseek_ocr.py291-292 | Output dimension matching LLM (1280) |

 **Customization approach**: See [Custom Projector Architectures](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/5.3-custom-projector-architectures) for implementing new projection strategies. The `MlpProjector` supports multiple types including `linear`, `mlp_gelu`, `downsample_mlp_gelu`, and hybrid split variants [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/build_linear.py15-87](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/build_linear.py#L15-L87)

 **Sources**: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py291-292](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L291-L292) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/build_linear.py7-96](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepencoder/build_linear.py#L7-L96)

 
---

 
### 3. Special Token Handling

 The system uses learnable special tokens to structure the 2D image features into a 1D sequence.

 
```

```

 **Implementation details**:

 
 - Token initialization: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py304-312](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L304-L312)
 - `image_newline` usage: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py426](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L426-L426) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py434](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L434-L434) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py458](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L458-L458)
 - `view_seperator` usage: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py438](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L438-L438) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py463](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L463-L463)
 
 **Extension**: Add new special tokens by modifying the initialization block at lines 304-312 and including them in weight loading at line 568.

 **Sources**: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py304-312](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L304-L312) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py423-438](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L423-L438) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py455-463](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L455-L463)

 
---

 
## Forward Pass Pipeline

 Understanding the complete forward pass is essential for debugging and adding custom processing logic.

 
```

```

 **Key methods**:

 
| Method | Location | Purpose |
|---|---|---|
| forward() | deepseek_ocr.py530-553 | Main forward pass coordination |
| _parse_and_validate_image_input() | deepseek_ocr.py333-360 | Extract and validate image tensors |
| _pixel_values_to_embedding() | deepseek_ocr.py364-467 | Vision encoding per image |
| _process_image_input() | deepseek_ocr.py469-493 | Batch vision processing |
| get_multimodal_embeddings() | deepseek_ocr.py498-504 | Entry point for vision features |
| get_input_embeddings() | deepseek_ocr.py508-528 | Merge vision and text embeddings |
| compute_logits() | deepseek_ocr.py555-561 | Final logit computation |

 **Sources**: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py530-561](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L530-L561) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py333-360](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L333-L360) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py364-467](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L364-L467) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py498-528](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L498-L528)

 
---

 
## Vision Feature Processing Details

 The `_pixel_values_to_embedding()` method contains the core vision encoding logic. This is the primary extension point for custom vision processing.

 
### Processing Logic Flow

 
```

```

 **Critical implementation details**:

 
 - **Dual encoder calls**: SAM encoder runs first, then CLIP encoder receives SAM features as additional input ([lines 394-397](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/lines 394-397) [404-405](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/404-405) [441-442](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/441-442)).
 - **Feature concatenation**: CLIP tokens `[:, 1:]` (excluding CLS) + SAM spatial features ([lines 400](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/lines 400) [406](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/406) [443](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/443)).
 - **Gradient context**: All vision encoding happens in `torch.no_grad()` context ([line 384](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/line 384)).
 - **Newline insertion**: `image_newline` is expanded and concatenated to maintain 2D structure ([lines 426](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/lines 426) [434](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/434) [458](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/458)).
 
 **Sources**: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py364-467](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L364-L467) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py384-438](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L384-L438) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py440-463](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L440-L463)

 
---

 
## Multimodal Processing Pipeline

 The vLLM integration requires specialized processing components to handle multimodal inputs correctly.

 
### Processor Registration Pattern

 
```

```

 **Processor methods**:

 
| Method | Location | Purpose |
|---|---|---|
| _call_hf_processor() | deepseek_ocr.py154-176 | Invoke HuggingFace processor for tokenization |
| _get_mm_fields_config() | deepseek_ocr.py178-188 | Map BatchFeature fields to modality types |
| _get_prompt_updates() | deepseek_ocr.py190-229 | Replace <image> with correct number of tokens |

 **ProcessingInfo methods**:

 
| Method | Location | Purpose |
|---|---|---|
| get_num_image_tokens() | deepseek_ocr.py61-106 | Calculate tokens based on image size and cropping |
| get_image_size_with_most_features() | deepseek_ocr.py108-112 | Return maximum supported image size |

 **Sources**: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py257-260](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L257-L260) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py150-229](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L150-L229) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py50-112](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L50-L112)

 
---

 
## Token Count Calculation

 Understanding how image tokens are counted is crucial for memory planning and prompt construction.

 
### Token Calculation Logic

 The `get_num_image_tokens()` method implements the core token counting logic based on configuration and image dimensions:

 
```

```

 **Configuration dependencies**:

 
 - `IMAGE_SIZE`: Local crop resolution ([line 73](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/line 73)).
 - `BASE_SIZE`: Global view resolution ([line 74](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/line 74)).
 - `CROP_MODE`: Whether to enable dynamic cropping ([line 78](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/line 78)).
 
 **Sources**: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py61-106](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L61-L106) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py73-105](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L73-L105)

 
---

 
## Weight Loading Strategy

 The weight loading mechanism handles the mapping between HuggingFace checkpoint names and vLLM internal names.

 
### Weight Name Mapping

 
```

```

 **Mapping rules**:

 
| Original Name Pattern | New Name Pattern | Component |
|---|---|---|
| model.sam_model.* | sam_model.* | SAM encoder |
| model.vision_model.* | vision_model.* | CLIP encoder |
| model.projector.* | projector.* | MLP projector |
| model.image_newline | image_newline | Special token |
| model.view_seperator | view_seperator | Special token |
| * (other) | language.* | Language model |
| language.* | language_model.* | vLLM mapping |

 **Implementation**: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py564-582](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L564-L582)

 **WeightsMapper configuration**: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py263-265](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L263-L265)

 **Sources**: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py564-582](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L564-L582) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py263-265](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L263-L265)

 
---

 
## Development Best Practices

 
### 1. Adding Custom Vision Encoders

 To add a new vision encoder:

 
 - **Import or define encoder**: Add builder function in `deepencoder/` directory.
 - **Instantiate in `__init__`**: Add encoder initialization at [deepseek_ocr.py288-289](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/deepseek_ocr.py#L288-L289)
 - **Modify feature extraction**: Update `_pixel_values_to_embedding()` at [deepseek_ocr.py394-407](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/deepseek_ocr.py#L394-L407)
 - **Update concatenation**: Adjust feature concatenation dimension at [deepseek_ocr.py400](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/deepseek_ocr.py#L400-L400)
 - **Adjust projector**: Update `MlpProjector` `input_dim` at [deepseek_ocr.py292](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/deepseek_ocr.py#L292-L292)
 - **Update weight loading**: Add encoder name to whitelist at [deepseek_ocr.py568](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/deepseek_ocr.py#L568-L568)
 
 
### 2. Modifying Token Structure

 To change how image features are structured:

 
 - **Define new special tokens**: Add parameters in `__init__` at [deepseek_ocr.py304-312](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/deepseek_ocr.py#L304-L312)
 - **Update token usage**: Modify reshape/concatenation logic at [deepseek_ocr.py423-438](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/deepseek_ocr.py#L423-L438)
 - **Adjust token counting**: Update `get_num_image_tokens()` at [deepseek_ocr.py61-106](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/deepseek_ocr.py#L61-L106)
 - **Update weight loading**: Include new tokens in whitelist at [deepseek_ocr.py568](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/deepseek_ocr.py#L568-L568)
 
 
### 3. Extending Multimodal Processing

 To customize prompt processing:

 
 - **Modify processor**: Extend `DeepseekOCRMultiModalProcessor` methods at [deepseek_ocr.py150-255](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/deepseek_ocr.py#L150-L255)
 - **Update field config**: Adjust `_get_mm_fields_config()` at [deepseek_ocr.py178-188](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/deepseek_ocr.py#L178-L188)
 - **Customize prompt updates**: Modify `_get_prompt_updates()` at [deepseek_ocr.py190-229](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/deepseek_ocr.py#L190-L229)
 - **Add dummy inputs**: Update `DeepseekOCRDummyInputsBuilder` at [deepseek_ocr.py115-146](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/deepseek_ocr.py#L115-L146)
 
 
### 4. Debugging Vision Features

 Key debugging points:

 
 - **Print token counts**: Set `PRINT_NUM_VIS_TOKENS=True` in config ([lines 409-413](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/lines 409-413) [446-450](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/446-450)).
 - **Check feature dimensions**: Monitor concatenation shapes at [lines 400](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/lines 400) [406](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/406) [443](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/443)
 - **Validate embeddings**: Inspect `get_multimodal_embeddings()` output at [line 504](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/line 504)
 - **Trace merge process**: Debug `merge_multimodal_embeddings()` at [line 520](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/line 520)
 
 **Sources**: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py288-292](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L288-L292) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py304-312](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L304-L312) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py394-463](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L394-L463) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py568](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L568-L568)

 
---

 
## Configuration Integration

 The model integrates with global configuration from `config.py`:

 
| Config Variable | Usage Location | Purpose |
|---|---|---|
| IMAGE_SIZE | deepseek_ocr.py73 85 | Local crop resolution |
| BASE_SIZE | deepseek_ocr.py74 95 | Global view resolution |
| CROP_MODE | deepseek_ocr.py78 140 219 | Enable dynamic cropping |
| PRINT_NUM_VIS_TOKENS | deepseek_ocr.py409 446 | Debug vision token counts |
| PROMPT | deepseek_ocr.py135 | Default prompt template |

 **Import statement**: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py45](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L45-L45)

 See [Configuration System](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/3.3-configuration-system) for detailed parameter documentation.

 **Sources**: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py45](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L45-L45) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py73-106](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L73-L106) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py135](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L135-L135) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py409-450](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L409-L450)

 
---

 
## Common Development Patterns

 
### Pattern 1: Adding Pre/Post-Processing Hooks

 To add custom processing before/after vision encoding:

 
```

```

 
### Pattern 2: Adding Custom Special Tokens

 To add a new structural token (e.g., for marking sections):

 
```

```

 
### Pattern 3: Multi-Resolution Encoding

 To encode at multiple resolutions simultaneously:

 
```

```

 **Sources**: [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py364-467](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L364-L467) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py304-312](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py#L304-L312)

 
---

 
## Next Steps

 For detailed implementation guides:

 
 - **Model internals**: [Model Components Reference](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/5.1-model-components-reference)
 - **Output processing**: [Custom Logits Processors](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/5.2-custom-logits-processors)
 - **Feature projection**: [Custom Projector Architectures](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/5.3-custom-projector-architectures)
 - **Image preprocessing**: [Extending Image Processing](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/5.4-extending-image-processing)
 - **Result parsing**: [Output Post-Processing](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/5.5-output-post-processing)
 
 For API specifications:

 
 - **vLLM model API**: [vLLM Model API](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/6.2-vllm-model-api)
 - **Processing API**: [Processing API](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/6.4-processing-api)
 - **Encoder API**: [Encoder API](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/6.5-encoder-api)
