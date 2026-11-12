<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/DeepSeek-OCR · page 4 Architecture · fetched 2026-10-30 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py](DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py)
- [DeepSeek_OCR_paper.pdf](DeepSeek_OCR_paper.pdf)

</details>



## Purpose and Scope

This page provides a technical overview of DeepSeek-OCR's system architecture, focusing on the major structural components and how they relate to each other. It explains the dual-framework design (vLLM and Transformers), the layered component hierarchy, and the overall data flow through the system.

For detailed information about specific subsystems, see:
- Model architecture internals: [Model Architecture](#4.2)
- Vision encoders (SAM and CLIP): [Vision Encoding System](#4.3)
- Image preprocessing logic: [Image Processing Pipeline](#4.4)
- How vision and text tokens are merged: [Multimodal Integration](#4.5)

For practical usage guides, see:
- Configuration parameters: [Configuration System](#3.3)
- Running inference: [vLLM Inference](#3.2) and [Transformers Inference](#3.1)

---

## Architectural Principles

DeepSeek-OCR is designed around several key architectural principles:

1. **Dual-Framework Support**: The system provides both vLLM and Transformers inference paths that share the same underlying model weights, enabling production throughput optimization and research flexibility. [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:2-38]()

2. **Dual-Encoder Vision**: Combines SAM (Segment Anything Model) for spatial detail with CLIP for semantic understanding, creating complementary feature representations. [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:40-41]()

3. **Hierarchical Resolution Processing**: Implements dynamic cropping (Gundam mode) to process large documents as multiple high-resolution local views plus one global view, balancing detail preservation with memory constraints. [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:78-106]()

4. **Token-Based Spatial Encoding**: Uses special learned embeddings (`image_newline`, `view_seperator`) to maintain 2D spatial relationships within the 1D token sequence fed to the language model. [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:318-322]()

5. **Configurable Resolution Modes**: Offers processing modes defined in `config.py` with different quality/speed/memory tradeoffs. [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:45]()

**Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:1-583]()

---

## System Layers

The DeepSeek-OCR system is organized into distinct layers with clear responsibilities:

DeepSeek-OCR Component Hierarchy
```mermaid
graph TB
    subgraph "Layer 1: Entry Points"
        run_dpsk_ocr_image["run_dpsk_ocr_image.py<br/>(Single image + streaming)"]
        run_dpsk_ocr_pdf["run_dpsk_ocr_pdf.py<br/>(Multi-page PDF)"]
        run_dpsk_ocr_eval_batch["run_dpsk_ocr_eval_batch.py<br/>(Batch evaluation)"]
    end
    
    subgraph "Layer 2: Configuration"
        config_py["config.py"]
        modes["Resolution modes:<br/>IMAGE_SIZE, BASE_SIZE,<br/>CROP_MODE"]
    end
    
    subgraph "Layer 3: Inference Frameworks"
        vllm_engine["vLLM:<br/>AsyncLLMEngine<br/>SamplingParams"]
        hf_api["Transformers:<br/>AutoModel<br/>model.infer()"]
    end
    
    subgraph "Layer 4: Multimodal Processing"
        DeepseekOCRMultiModalProcessor["DeepseekOCRMultiModalProcessor"]
        DeepseekOCRProcessor["DeepseekOCRProcessor<br/>(image tokenization)"]
        DeepseekOCRDummyInputsBuilder["DeepseekOCRDummyInputsBuilder"]
    end
    
    subgraph "Layer 5: Core Model"
        DeepseekOCRForCausalLM["DeepseekOCRForCausalLM"]
    end
    
    subgraph "Layer 6: Vision Encoders"
        build_sam_vit_b["build_sam_vit_b()<br/>ImageEncoderViT"]
        build_clip_l["build_clip_l()<br/>VitModel"]
    end
    
    subgraph "Layer 7: Feature Projection"
        MlpProjector["MlpProjector<br/>(2048 → 1280 dim)"]
        special_tokens["image_newline<br/>view_seperator"]
    end
    
    subgraph "Layer 8: Language Model"
        language_model["DeepseekV3/V2/V1<br/>ForCausalLM"]
    end
    
    run_dpsk_ocr_image --> config_py
    run_dpsk_ocr_pdf --> config_py
    run_dpsk_ocr_eval_batch --> config_py
    
    config_py --> modes
    modes --> vllm_engine
    modes --> hf_api
    
    vllm_engine --> DeepseekOCRMultiModalProcessor
    hf_api --> DeepseekOCRProcessor
    
    DeepseekOCRMultiModalProcessor --> DeepseekOCRForCausalLM
    DeepseekOCRProcessor --> DeepseekOCRForCausalLM
    DeepseekOCRDummyInputsBuilder --> DeepseekOCRMultiModalProcessor
    
    DeepseekOCRForCausalLM --> build_sam_vit_b
    DeepseekOCRForCausalLM --> build_clip_l
    
    build_sam_vit_b --> MlpProjector
    build_clip_l --> MlpProjector
    
    MlpProjector --> special_tokens
    special_tokens --> language_model
    
    DeepseekOCRForCausalLM --> language_model
```

**Layer Responsibilities:**

| Layer | Components | Purpose |
|-------|-----------|---------|
| 1: Entry Points | CLI scripts | User-facing interfaces for different use cases |
| 2: Configuration | `config.py` | Central parameter definition (resolution, cropping, workers) |
| 3: Inference Frameworks | vLLM, Transformers | Production serving vs. research/fine-tuning |
| 4: Multimodal Processing | Processor classes | Image tokenization, aspect ratio handling, dummy inputs |
| 5: Core Model | `DeepseekOCRForCausalLM` | Main orchestrator, weight loading, forward pass |
| 6: Vision Encoders | SAM, CLIP | Spatial and semantic feature extraction |
| 7: Feature Projection | `MlpProjector`, special tokens | Dimensionality reduction, spatial structure preservation |
| 8: Language Model | DeepseekV3/V2/V1 | Causal language modeling on fused multimodal tokens |

**Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:261-330](), [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:50-255]()

---

## Dual-Framework Design

DeepSeek-OCR uniquely provides two parallel inference frameworks that operate on the same model checkpoint:

Framework Comparison and Data Paths
```mermaid
graph LR
    subgraph "vLLM Path"
        vllm_scripts["Entry scripts:<br/>run_dpsk_ocr_image.py<br/>run_dpsk_ocr_pdf.py"]
        vllm_config["vLLM-specific config"]
        AsyncLLMEngine["AsyncLLMEngine"]
        
        vllm_scripts --> vllm_config
        vllm_config --> AsyncLLMEngine
    end
    
    subgraph "Transformers Path"
        hf_script["run_dpsk_ocr.py"]
        AutoModel["AutoModel.from_pretrained()"]
        model_infer["model.infer()"]
        
        hf_script --> AutoModel
        AutoModel --> model_infer
    end
    
    shared_checkpoint["Shared Model Weights:<br/>deepseek-ai/DeepSeek-OCR"]
    
    AsyncLLMEngine --> DeepseekOCRForCausalLM
    model_infer --> DeepseekOCRForCausalLM
    
    DeepseekOCRForCausalLM --> shared_checkpoint
```

**Framework Comparison:**

| Aspect | vLLM | Transformers |
|--------|------|--------------|
| **Use Case** | Production serving, batch evaluation | Research, fine-tuning, experimentation |
| **Engine** | `AsyncLLMEngine` with batching | Direct `model.infer()` calls |
| **Implementation** | `DeepseekOCRMultiModalProcessor` | `DeepseekOCRProcessor` |
| **Special Features** | Streaming output, prefix caching | Direct logits access, `test_compress` |

The `DeepseekOCRForCausalLM` class is designed to work with both frameworks through:
- vLLM integration via `MULTIMODAL_REGISTRY.register_processor` decorator [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:257-260]()
- Shared weight loading through `load_weights()` method [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:564-582]()

**Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:257-261](), [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:150-189]()

---

## Core Model Architecture

The `DeepseekOCRForCausalLM` class orchestrates all model components:

DeepseekOCRForCausalLM Internal Architecture
```mermaid
graph TB
    subgraph "DeepseekOCRForCausalLM Components"
        init["__init__()"]
        sam_model["self.sam_model<br/>= build_sam_vit_b()"]
        vision_model["self.vision_model<br/>= build_clip_l()"]
        projector["self.projector<br/>= MlpProjector()"]
        language_model["self.language_model<br/>= DeepseekV3/V2/V1"]
        
        init --> sam_model
        init --> vision_model
        init --> projector
        init --> language_model
    end
    
    subgraph "Forward Pass Methods"
        parse_validate["_parse_and_validate_image_input()"]
        pixel_to_embed["_pixel_values_to_embedding()"]
        process_image["_process_image_input()"]
        get_mm_embeds["get_multimodal_embeddings()"]
        forward["forward()"]
        
        parse_validate --> process_image
        pixel_to_embed --> process_image
        process_image --> get_mm_embeds
        get_mm_embeds --> forward
    end
```

**Key Methods:**

| Method | Location | Purpose |
|--------|----------|---------|
| `__init__()` | [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:267-329]() | Initialize encoders, projector, and LLM |
| `_parse_and_validate_image_input()` | [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:333-360]() | Validate `pixel_values` and `images_crop` |
| `_pixel_values_to_embedding()` | [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:364-467]() | Vision encoding: SAM + CLIP → projection |
| `get_multimodal_embeddings()` | [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:498-504]() | Public API for getting vision embeddings |
| `forward()` | [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:530-553]() | Complete forward pass through LLM |

**Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:261-583]()

---

## Vision Encoding Pipeline

The vision encoding pipeline implements the dual-encoder architecture:

Vision Feature Extraction Pipeline
```mermaid
graph TB
    input["Input: pixel_values & images_crop"]
    
    subgraph "Encoding Step"
        sam_enc["SAM ViT-B:<br/>self.sam_model()"]
        clip_enc["CLIP-L:<br/>self.vision_model()"]
    end
    
    concat["Concatenate:<br/>CLIP + SAM features"]
    proj["MlpProjector:<br/>2048 -> 1280"]
    
    spatial["Spatial Structure:<br/>Add image_newline<br/>Add view_seperator"]
    
    input --> sam_enc
    input --> clip_enc
    sam_enc --> concat
    clip_enc --> concat
    concat --> proj
    proj --> spatial
```

**Encoding Steps:**

1. **Dual Encoding**: 
   - SAM extracts spatial features [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:394]().
   - CLIP extracts semantic features [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:397]().
2. **Feature Fusion**: Concatenates CLIP (1280) and SAM (768) features to form 2048-dim vectors [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:400]().
3. **Projection**: `MlpProjector` reduces dimensions to match the language model (1280) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:401]().
4. **Spatial Structuring**: Reshapes the 1D token stream back to 2D rows and inserts `image_newline` and `view_seperator` tokens [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:425-438]().

**Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:364-467]()

---

## Multimodal Processing Classes

The system uses specialized processor classes to manage the interface between raw images and model inputs:

| Class | Purpose | Key Methods |
|-------|---------|-------------|
| `DeepseekOCRProcessingInfo` | Metadata for vLLM | `get_num_image_tokens()` [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:61-106]() |
| `DeepseekOCRDummyInputsBuilder` | Profiling utilities | `get_dummy_mm_data()` [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:126-145]() |
| `DeepseekOCRMultiModalProcessor` | vLLM input handler | `_call_hf_processor()` [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:154-176]() |
| `DeepseekOCRProcessor` | Core preprocessing | `tokenize_with_images()`, `count_tiles()` [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:30-31]() |

**Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:50-255]()

---

## Weight Loading and Model Registration

The model uses custom weight loading to map checkpoint keys to the internal module structure:

Weight Mapping and Loading Flow
```mermaid
graph TB
    checkpoint["HF Checkpoint Weights"]
    
    subgraph "load_weights() Logic"
        vision_map["Vision Weights:<br/>model.sam_model -> sam_model"]
        llm_map["LLM Weights:<br/>model.layers -> language_model.model.layers"]
    end
    
    loader["AutoWeightsLoader"]
    
    checkpoint --> vision_map
    checkpoint --> llm_map
    vision_map --> loader
    llm_map --> loader
```

**Weight Loading Logic** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:564-582]():
The `load_weights` method remaps keys by checking if they belong to the vision system (SAM, CLIP, Projector) or the language model. Vision keys have their `model.` prefix removed, while LLM keys are prefixed with `language.` to route them to the `self.language_model` submodule.

**Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:564-582]()

---

