<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/TensorRT-LLM · page 18 Multimodal and Visual Generation · fetched 2026-10-26 -->

# Multimodal and Visual Generation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tensorrt_llm/_torch/models/modeling_multimodal_utils.py](tensorrt_llm/_torch/models/modeling_multimodal_utils.py)
- [tensorrt_llm/_torch/models/modeling_nemotron_nano.py](tensorrt_llm/_torch/models/modeling_nemotron_nano.py)
- [tensorrt_llm/_torch/models/modeling_parakeet.py](tensorrt_llm/_torch/models/modeling_parakeet.py)
- [tensorrt_llm/_torch/models/modeling_radio.py](tensorrt_llm/_torch/models/modeling_radio.py)
- [tensorrt_llm/_torch/models/multimodal_encoder_graph.py](tensorrt_llm/_torch/models/multimodal_encoder_graph.py)
- [tensorrt_llm/_torch/shared_tensor/__init__.py](tensorrt_llm/_torch/shared_tensor/__init__.py)
- [tensorrt_llm/_torch/shared_tensor/shared_tensor.py](tensorrt_llm/_torch/shared_tensor/shared_tensor.py)
- [tensorrt_llm/_torch/visual_gen/__init__.py](tensorrt_llm/_torch/visual_gen/__init__.py)
- [tensorrt_llm/_torch/visual_gen/executor.py](tensorrt_llm/_torch/visual_gen/executor.py)
- [tensorrt_llm/_torch/visual_gen/models/flux/pipeline_flux.py](tensorrt_llm/_torch/visual_gen/models/flux/pipeline_flux.py)
- [tensorrt_llm/_torch/visual_gen/models/flux/pipeline_flux2.py](tensorrt_llm/_torch/visual_gen/models/flux/pipeline_flux2.py)
- [tensorrt_llm/_torch/visual_gen/models/wan/pipeline_wan.py](tensorrt_llm/_torch/visual_gen/models/wan/pipeline_wan.py)
- [tensorrt_llm/_torch/visual_gen/models/wan/pipeline_wan_i2v.py](tensorrt_llm/_torch/visual_gen/models/wan/pipeline_wan_i2v.py)
- [tensorrt_llm/_torch/visual_gen/output.py](tensorrt_llm/_torch/visual_gen/output.py)
- [tensorrt_llm/_torch/visual_gen/pipeline.py](tensorrt_llm/_torch/visual_gen/pipeline.py)
- [tensorrt_llm/inputs/__init__.py](tensorrt_llm/inputs/__init__.py)
- [tensorrt_llm/inputs/media_io.py](tensorrt_llm/inputs/media_io.py)
- [tensorrt_llm/inputs/multimodal.py](tensorrt_llm/inputs/multimodal.py)
- [tensorrt_llm/inputs/multimodal_data.py](tensorrt_llm/inputs/multimodal_data.py)
- [tensorrt_llm/inputs/registry.py](tensorrt_llm/inputs/registry.py)
- [tensorrt_llm/inputs/utils.py](tensorrt_llm/inputs/utils.py)
- [tensorrt_llm/serve/chat_utils.py](tensorrt_llm/serve/chat_utils.py)
- [tests/unittest/_torch/modeling/test_modeling_nemotron_nano_v2_vl.py](tests/unittest/_torch/modeling/test_modeling_nemotron_nano_v2_vl.py)
- [tests/unittest/_torch/modeling/test_modeling_parakeet.py](tests/unittest/_torch/modeling/test_modeling_parakeet.py)
- [tests/unittest/_torch/modeling/test_modeling_radio.py](tests/unittest/_torch/modeling/test_modeling_radio.py)
- [tests/unittest/_torch/modeling/test_multimodal_encoder_graph.py](tests/unittest/_torch/modeling/test_multimodal_encoder_graph.py)
- [tests/unittest/_torch/modeling/test_nemotron_nano_preprocessing.py](tests/unittest/_torch/modeling/test_nemotron_nano_preprocessing.py)
- [tests/unittest/_torch/multimodal/test_qwen3vl_mixed_modality_encoder.py](tests/unittest/_torch/multimodal/test_qwen3vl_mixed_modality_encoder.py)
- [tests/unittest/_torch/test_utils.py](tests/unittest/_torch/test_utils.py)
- [tests/unittest/_torch/visual_gen/test_flux_pipeline.py](tests/unittest/_torch/visual_gen/test_flux_pipeline.py)
- [tests/unittest/inputs/test_video_data_hashing.py](tests/unittest/inputs/test_video_data_hashing.py)
- [tests/unittest/inputs/test_video_decode.py](tests/unittest/inputs/test_video_decode.py)
- [tests/unittest/llmapi/apps/test_chat_utils.py](tests/unittest/llmapi/apps/test_chat_utils.py)
- [tests/unittest/llmapi/test_llm_kv_cache_events.py](tests/unittest/llmapi/test_llm_kv_cache_events.py)
- [tests/unittest/visual_gen/test_executor_shared_tensor_ipc.py](tests/unittest/visual_gen/test_executor_shared_tensor_ipc.py)

</details>



The Multimodal and Visual Generation system in TensorRT-LLM provides a unified framework for processing inputs across different modalities (text, image, video, audio) and executing pipelines for visual content generation. This infrastructure bridges the gap between raw media data and high-performance inference.

## Multimodal Architecture Overview

TensorRT-LLM supports multimodal models by integrating specialized input processors that handle media loading, encoding via vision/audio encoders, and embedding fusion. The system supports a wide range of architectures including Qwen2-VL, Qwen2.5-VL, Qwen3-VL, LLaVA-NeXT, Pixtral, Gemma3-VL, VILA, mLLaMA, Step3.7-VL, MiniMax-M3-VL, Nemotron-Nano VL, and Phi-4-MM.

### From Input to Embeddings

The following diagram illustrates how multimodal inputs are transformed into the joint embedding space required by the LLM backbone, mapping system components to their code entities.

**Multimodal Data Flow: Natural Language to Code Entity Space**
```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        [UserPrompt] --> ["TextPrompt (Dict)"]
        [MediaURL] --> ["Media URL/Base64"]
    end

    subgraph "InputProcessingLayer"
        ["TextPrompt (Dict)"] --> [InputProc]
        ["Media URL/Base64"] --> [Loader]
        
        [InputProc] --> ["BaseMultimodalInputProcessor"]
        [Loader] --> ["load_image / load_video"]
        [Registry] --> ["MULTIMODAL_PLACEHOLDER_REGISTRY"]
    end

    subgraph "CodeEntitySpace"
        [Enc] --> ["MultimodalModelMixin"]
        [Proj] --> ["LlavaNextMultiModalProjector"]
        [Fuser] --> ["fuse_input_embeds"]
    end

    ["BaseMultimodalInputProcessor"] --> ["MULTIMODAL_PLACEHOLDER_REGISTRY"]
    ["load_image / load_video"] --> ["BaseMultimodalInputProcessor"]
    ["MULTIMODAL_PLACEHOLDER_REGISTRY"] --> ["MultimodalModelMixin"]
    ["MultimodalModelMixin"] --> ["LlavaNextMultiModalProjector"]
    ["LlavaNextMultiModalProjector"] --> ["fuse_input_embeds"]
    ["fuse_input_embeds"] --> ["DecoderModelForCausalLM"]
```
**Sources:**
- `tensorrt_llm/_torch/models/modeling_multimodal_mixin.py:47-51` []()
- `tensorrt_llm/_torch/models/modeling_multimodal_utils.py:55-55` []()
- `tensorrt_llm/inputs/registry.py:35-36` []()
- `tensorrt_llm/inputs/utils.py:67-69` []()
- `tensorrt_llm/_torch/models/modeling_nemotron_nano.py:27-41` []()

## Multimodal Input Processing

The `InputProcessor` protocol defines the standard interface for preparing multimodal data [tensorrt_llm/inputs/registry.py:134-154](). This includes tokenizing the text prompt and calculating placeholders for media tokens.

*   **Registry System:** Models register their specific input processors using `register_input_processor` [tensorrt_llm/_torch/models/modeling_nemotron_nano.py:39-39](). The `MULTIMODAL_PLACEHOLDER_REGISTRY` tracks placement strategies for different modalities [tensorrt_llm/inputs/registry.py:35-36]().
*   **Media Loading:** Specialized processors like `NanoV2VLInputProcessor` [tensorrt_llm/_torch/models/modeling_nemotron_nano.py:20-20]() handle modality-specific preprocessing. Utility functions like `load_image` [tensorrt_llm/inputs/utils.py:67-69]() and `load_video` [tensorrt_llm/inputs/utils.py:137-142]() handle URL and Base64 decoding.
*   **Nemotron-Nano VL Support:** Implements dynamic resolution tiling via `DynamicResolutionImageTiler` [tensorrt_llm/_torch/models/modeling_nemotron_nano.py:18-19]() and specialized video frame resizing [tensorrt_llm/_torch/models/modeling_nemotron_nano.py:114-146]().
*   **Disaggregated Multimodal:** The system supports disaggregated prefill (E/P split) where encoder processing is separated from the LLM backbone, controlled by the `TLLM_MULTIMODAL_DISAGGREGATED` environment flag [tensorrt_llm/_torch/models/modeling_multimodal_utils.py:35-41]().
*   **Embedding Fusion:** The `fuse_input_embeds` utility merges text embeddings with media embeddings extracted by encoders by replacing placeholder token positions [tensorrt_llm/_torch/models/modeling_multimodal_utils.py:55-55]().
*   **KV Cache Events:** The system supports serialization of multimodal keys (`mm_keys`) in KV cache events, allowing for efficient prefix caching of media content [tests/unittest/llmapi/test_llm_kv_cache_events.py:140-155]().

For details, see [Multimodal Input Processing](#18.1).

## Visual Generation Pipelines

Beyond understanding multimodal inputs, TensorRT-LLM supports high-performance visual generation through the `VisualGen` framework, targeting models like Flux, Wan, and LTX2.

### Pipeline Components
A generation pipeline typically consists of several components discovered via configuration [tensorrt_llm/_torch/visual_gen/pipeline.py:86-104]():
1.  **Transformer/DiT:** The core denoising backbone (e.g., `WanTransformer3DModel` [tensorrt_llm/_torch/visual_gen/models/wan/pipeline_wan.py:48-48]()).
2.  **VAE:** For encoding/decoding latent representations, often utilizing `ParallelVAEFactory` for distributed execution [tensorrt_llm/_torch/visual_gen/pipeline.py:38-38]().
3.  **Text Encoders:** For processing conditioning prompts, managed by the `BasePipeline` [tensorrt_llm/_torch/visual_gen/pipeline.py:102-102]().
4.  **Scheduler:** Manages denoising timesteps and noise levels (e.g., `FlowMatchEulerDiscreteScheduler` [tensorrt_llm/_torch/visual_gen/models/wan/pipeline_wan.py:23-23]()).

**Visual Generation Execution Model**
```mermaid
graph LR
    subgraph "Configuration"
        [Args] --> ["VisualGenArgs"]
        [Exec] --> ["VisualGenExecutor"]
    end

    subgraph "PipelineExecution"
        [Loader] --> ["PipelineLoader"]
        [Pipe] --> ["BasePipeline"]
        [Graph] --> ["CUDAGraphRunner"]
    end

    subgraph "DistributedComponents"
        [Mapping] --> ["Mapping"]
        [Autotune] --> ["_VisualGenAutotuneDist"]
    end

    ["VisualGenArgs"] --> ["PipelineLoader"]
    ["VisualGenExecutor"] --> ["PipelineLoader"]
    ["PipelineLoader"] --> ["BasePipeline"]
    ["BasePipeline"] --> ["CUDAGraphRunner"]
    ["VisualGenExecutor"] --> ["Mapping"]
    ["Mapping"] --> ["_VisualGenAutotuneDist"]
```
**Sources:**
- `tensorrt_llm/_torch/visual_gen/pipeline.py:68-82` []()
- `tensorrt_llm/_torch/visual_gen/executor.py:18-23` []()
- `tensorrt_llm/_torch/visual_gen/pipeline_loader.py:19-19` []()
- `tensorrt_llm/_torch/visual_gen/mapping.py:37-37` []()

### Key Optimizations
*   **Acceleration Backends:** Integrates `TeaCache` and `CacheDiTAccelerator` to skip redundant denoising steps based on feature similarity [tensorrt_llm/_torch/visual_gen/pipeline.py:34-34]().
*   **CUDA Graph Integration:** The `CUDAGraphRunner` wraps transformer forward passes to minimize host overhead during capture and replay [tensorrt_llm/_torch/visual_gen/pipeline.py:140-175]().
*   **Iteration Stats:** The `_IterationStatsTracker` provides metrics for active and queued requests, mirroring the LLM metrics shape [tensorrt_llm/_torch/visual_gen/executor.py:39-50]().
*   **Shared Request Scoping:** The `run_inference` method manages model-specific inference within shared request profiler boundaries [tensorrt_llm/_torch/visual_gen/pipeline.py:118-123]().

For details, see [Visual Generation Pipelines](#18.2).

## Supported Modalities and Models

The framework provides specialized implementations for various multimodal and generative architectures:

| Modality | Key Models Supported | Input Processor / Pipeline |
| :--- | :--- | :--- |
| **Image** | Qwen2-VL, LLaVA-NeXT, Gemma3-VL, mLLaMA, Nemotron-Nano VL | `NanoV2VLInputProcessor`, `LlavaNextInputProcessor` |
| **Video** | Qwen2-VL, VILA, LTX2, Wan | `BaseMultimodalInputProcessor` / `WanPipeline` |
| **Audio** | Phi-4-MM, Parakeet | `Phi4MMInputProcessor`, `ParakeetExtractor` |
| **Generation** | Flux, Wan (2.1, 2.2), LTX2, Cosmos3 | `BasePipeline`, `VisualGenExecutor` |

**Sources:**
- `tensorrt_llm/_torch/models/modeling_nemotron_nano.py:20-20` []()
- `tensorrt_llm/_torch/models/modeling_parakeet.py:60-60` []()
- `tensorrt_llm/_torch/visual_gen/models/wan/pipeline_wan.py:114-114` []()
- `tensorrt_llm/serve/chat_utils.py:61-68` []()

---

