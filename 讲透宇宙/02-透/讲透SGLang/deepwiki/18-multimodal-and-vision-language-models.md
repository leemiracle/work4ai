> 来源: [https://deepwiki.com/sgl-project/sglang/18-multimodal-and-vision-language-models](https://deepwiki.com/sgl-project/sglang/18-multimodal-and-vision-language-models)
> DeepWiki sgl-project/sglang | Last indexed: 27 Aug 2026 (94183a)

# Multimodal and Vision-Language Models

  Relevant source files 
 - [python/sglang/multimodal_gen/test/unit/test_component_accuracy_parallel_runtime.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/test/unit/test_component_accuracy_parallel_runtime.py)
 - [python/sglang/multimodal_gen/test/unit/test_srt_siglip_reuse.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/test/unit/test_srt_siglip_reuse.py)
 - [python/sglang/srt/hardware_backend/npu/graph_runner/vit_npu_graph_runner.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/hardware_backend/npu/graph_runner/vit_npu_graph_runner.py)
 - [python/sglang/srt/layers/attention/vision.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/vision.py)
 - [python/sglang/srt/models/dots_vlm_vit.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/dots_vlm_vit.py)
 - [python/sglang/srt/models/glm4.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/glm4.py)
 - [python/sglang/srt/models/glm4v.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/glm4v.py)
 - [python/sglang/srt/models/idefics2.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/idefics2.py)
 - [python/sglang/srt/models/internvl.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/internvl.py)
 - [python/sglang/srt/models/paddleocr_vl.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/paddleocr_vl.py)
 - [python/sglang/srt/models/qwen2_5_vl.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/qwen2_5_vl.py)
 - [python/sglang/srt/models/qwen2_vl.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/qwen2_vl.py)
 - [python/sglang/srt/models/qwen3_vl.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/qwen3_vl.py)
 - [python/sglang/srt/multimodal/internvl_vit_cuda_graph_runner.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multimodal/internvl_vit_cuda_graph_runner.py)
 - [python/sglang/srt/multimodal/processors/base_processor.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multimodal/processors/base_processor.py)
 - [python/sglang/srt/multimodal/processors/ernie45_vl.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multimodal/processors/ernie45_vl.py)
 - [python/sglang/srt/multimodal/processors/executor.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multimodal/processors/executor.py)
 - [python/sglang/srt/multimodal/processors/midashenglm.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multimodal/processors/midashenglm.py)
 - [python/sglang/srt/multimodal/processors/qwen_vl.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multimodal/processors/qwen_vl.py)
 - [python/sglang/srt/multimodal/processors/sarashina2_vision.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multimodal/processors/sarashina2_vision.py)
 - [python/sglang/srt/multimodal/vit_cuda_graph_runner.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multimodal/vit_cuda_graph_runner.py)
 - [python/sglang/srt/utils/cuda_ipc_transport_utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/cuda_ipc_transport_utils.py)
 - [test/manual/nightly/test_vlms_piecewise_cuda_graph.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/manual/nightly/test_vlms_piecewise_cuda_graph.py)
 - [test/manual/nightly/test_vlms_vit_cuda_graph.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/manual/nightly/test_vlms_vit_cuda_graph.py)
 - [test/registered/unit/layers/attention/test_vision_backend_selection.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/layers/attention/test_vision_backend_selection.py)
 - [test/registered/unit/managers/test_mm_process_config.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/managers/test_mm_process_config.py)
 - [test/registered/unit/models/test_paddleocr_vl_serving_defaults.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/models/test_paddleocr_vl_serving_defaults.py)
 - [test/registered/unit/multimodal/test_cuda_ipc_pool_budget.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/multimodal/test_cuda_ipc_pool_budget.py)
 - [test/registered/unit/multimodal/test_cuda_ipc_transport.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/multimodal/test_cuda_ipc_transport.py)
 - [test/registered/unit/multimodal/test_processor_async_call_sites.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/multimodal/test_processor_async_call_sites.py)
 - [test/registered/unit/multimodal/test_processor_clone_isolation.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/multimodal/test_processor_clone_isolation.py)
 - [test/registered/unit/multimodal/test_vit_cuda_graph_runner.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/multimodal/test_vit_cuda_graph_runner.py)
 
  This page provides an overview of SGLang's support for vision-language models (VLMs) and other multimodal architectures. SGLang enables efficient serving of models that process images, video, and audio alongside text, with optimizations for caching visual features, batching heterogeneous requests, and high-performance vision tower execution.

 **Sub-pages:**

 
 - [Vision-Language Model Architecture](https://deepwiki.com/sgl-project/sglang/18.1-vision-language-model-architecture) — Vision towers, projectors, and VLM-specific layers.
 - [Multimodal Input Processing](https://deepwiki.com/sgl-project/sglang/18.2-multimodal-input-processing) — Image encoding, feature projection, and embedding merging.
 - [Supported Vision-Language Models](https://deepwiki.com/sgl-project/sglang/18.3-supported-vision-language-models) — Comprehensive list of supported VLM architectures (LLaVA, Qwen-VL, InternVL, Gemma3, Llama4, Kimi-VL, etc.).
 
 
---

 
## Overview

 SGLang's multimodal subsystem extends the core serving infrastructure to handle models that process multiple modalities. Key capabilities:

 
 - **Vision Encoding**: Process images, video frames, and audio through dedicated encoder modules like `Qwen2_5_VisionPatchEmbed` [python/sglang/srt/models/qwen2_5_vl.py86-120](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/qwen2_5_vl.py#L86-L120) `Qwen3_VisionBlock` [python/sglang/srt/models/qwen3_vl.py204-245](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/qwen3_vl.py#L204-L245) or `InternVisionEmbeddings` [python/sglang/srt/models/internvl.py107-179](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/internvl.py#L107-L179)
 - **Feature Caching**: Cache encoded visual features to avoid redundant computation using `MultimodalPreprocessCache` [python/sglang/srt/multimodal/processors/base_processor.py31-35](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multimodal/processors/base_processor.py#L31-L35)
 - **Embedding Fusion**: Merge visual token embeddings into the text token sequence via `general_mm_embed_routine` [python/sglang/srt/managers/mm_utils.py54-57](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/mm_utils.py#L54-L57)
 - **Prefix Sharing**: Pad multimodal token regions to enable `RadixCache` prefix matching across requests using patterns like `MultiModalityDataPaddingPatternMultimodalTokens` [python/sglang/srt/managers/mm_utils.py54-55](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/mm_utils.py#L54-L55) or `MultiModalityDataPaddingPatternTokenPairs` [python/sglang/srt/models/internvl.py28-31](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/internvl.py#L28-L31)
 - **Attention Backends**: Specialized `VisionAttention` layer supporting FlashAttention, FlashInfer, and other backends for high-resolution visual inputs [python/sglang/srt/layers/attention/vision.py32-105](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/vision.py#L32-L105)
 - **Batching Support**: Handle mixed text-only and multimodal requests in the same batch using `MultimodalInputs` and `ScheduleBatch` [python/sglang/srt/managers/schedule_batch.py25-30](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L25-L30)
 
 **Sources:** [python/sglang/srt/models/qwen2_5_vl.py86-120](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/qwen2_5_vl.py#L86-L120) [python/sglang/srt/models/qwen3_vl.py204-245](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/qwen3_vl.py#L204-L245) [python/sglang/srt/managers/mm_utils.py54-57](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/mm_utils.py#L54-L57) [python/sglang/srt/layers/attention/vision.py32-105](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/vision.py#L32-L105) [python/sglang/srt/multimodal/processors/base_processor.py31-35](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multimodal/processors/base_processor.py#L31-L35)

 
---

 
## Multimodal Model Detection

 SGLang automatically detects multimodal models during initialization. The `BaseMultimodalProcessor` and its subclasses manage the specific requirements of each architecture.

 
 - **Modality Mapping**: `BaseMultimodalProcessor` identifies modalities such as `Modality.IMAGE`, `Modality.VIDEO`, and `Modality.AUDIO` [python/sglang/srt/multimodal/processors/base_processor.py86-95](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multimodal/processors/base_processor.py#L86-L95)
 - **Special Tokens**: `MultimodalSpecialTokens` parses and builds regex patterns to identify placeholders (e.g., `<image>`, `<video>`) in input text [python/sglang/srt/multimodal/processors/base_processor.py99-191](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multimodal/processors/base_processor.py#L99-L191)
 - **Dynamic Resolution**: Framework supports dynamic scaling for video/image inputs through utilities like `smart_resize` [python/sglang/srt/multimodal/processors/qwen_vl.py110-140](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multimodal/processors/qwen_vl.py#L110-L140) and `smart_nframes` [python/sglang/srt/multimodal/processors/qwen_vl.py158-202](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multimodal/processors/qwen_vl.py#L158-L202)
 - **Config Validation**: `ServerArgs` validates `mm_process_config` to ensure correct modality settings [test/registered/unit/managers/test_mm_process_config.py22-32](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/managers/test_mm_process_config.py#L22-L32)
 
 **Sources:** [python/sglang/srt/multimodal/processors/base_processor.py86-191](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multimodal/processors/base_processor.py#L86-L191) [python/sglang/srt/multimodal/processors/qwen_vl.py110-202](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multimodal/processors/qwen_vl.py#L110-L202) [test/registered/unit/managers/test_mm_process_config.py22-32](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/managers/test_mm_process_config.py#L22-L32)

 
---

 
## High-Level Architecture

 The following diagram illustrates the data flow from client input through the tokenizer manager to the model execution in the runner.

 **Multimodal Request Processing Pipeline**

 
```

```

 **Key Components:**

 
 - **BaseMultimodalProcessor**: Converts raw media to pixel tensors and handles tokenization [python/sglang/srt/multimodal/processors/base_processor.py205-212](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multimodal/processors/base_processor.py#L205-L212)
 - **MultimodalDataItem**: Encapsulates pixel values, modality type, and token offsets [python/sglang/srt/managers/schedule_batch.py27](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L27-L27)
 - **Vision Tower**: Encodes visual inputs into patch embeddings (e.g., `Qwen3VLVisionPatchEmbed` [python/sglang/srt/models/qwen3_vl.py171-201](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/qwen3_vl.py#L171-L201)).
 - **Multimodal Projector**: Projects vision embeddings to language model hidden dimension (e.g., `Qwen3_VisionMLP` [python/sglang/srt/models/qwen3_vl.py124-168](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/qwen3_vl.py#L124-L168)).
 - **Embedding Fusion**: Replaces image token placeholders with projected visual features via `general_mm_embed_routine` [python/sglang/srt/managers/mm_utils.py54-57](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/mm_utils.py#L54-L57)
 
 **Sources:** [python/sglang/srt/multimodal/processors/base_processor.py205-212](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multimodal/processors/base_processor.py#L205-L212) [python/sglang/srt/models/qwen3_vl.py124-201](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/qwen3_vl.py#L124-L201) [python/sglang/srt/managers/mm_utils.py54-57](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/mm_utils.py#L54-L57)

 
---

 
## Request Lifecycle for Multimodal Inputs

 The sequence below details the transition from the "Natural Language Space" (client prompt) to the "Code Entity Space" (internal SGLang structures).

 **VLM Request Processing Sequence**

 
```

```

 **Sources:** [python/sglang/srt/multimodal/processors/base_processor.py86-95](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multimodal/processors/base_processor.py#L86-L95) [python/sglang/srt/managers/mm_utils.py54-57](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/mm_utils.py#L54-L57) [python/sglang/srt/model_executor/forward_batch_info.py63](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/forward_batch_info.py#L63-L63)

 
---

 
## Efficient Vision Tower Execution

 SGLang implements specialized mechanisms to handle large pixel and feature tensors efficiently.

 
 - **VisionAttention**: A custom attention layer for vision encoders that supports `cu_seqlens` for variable-sized image/video patches [python/sglang/srt/layers/attention/vision.py154-168](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/vision.py#L154-L168)
 - **ViTCudaGraphRunner**: Accelerates vision tower execution by capturing and replaying CUDA graphs for Vision Transformer (ViT) components [python/sglang/srt/multimodal/vit_cuda_graph_runner.py30-43](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multimodal/vit_cuda_graph_runner.py#L30-L43)
 - **CUDA IPC Transport**: Efficiently transfers large multimodal features between processes using `CudaIpcTensorTransportProxy` [python/sglang/srt/utils/cuda_ipc_transport_utils.py6-14](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/cuda_ipc_transport_utils.py#L6-L14)
 - **Data Parallel Attention**: Supports sharded vision model execution via `run_dp_sharded_mrope_vision_model` [python/sglang/srt/multimodal/mm_utils.py71-74](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multimodal/mm_utils.py#L71-L74)
 
 **Sources:** [python/sglang/srt/layers/attention/vision.py154-168](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/vision.py#L154-L168) [python/sglang/srt/multimodal/vit_cuda_graph_runner.py30-43](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multimodal/vit_cuda_graph_runner.py#L30-L43) [python/sglang/srt/utils/cuda_ipc_transport_utils.py6-14](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/cuda_ipc_transport_utils.py#L6-L14) [python/sglang/srt/multimodal/mm_utils.py71-74](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multimodal/mm_utils.py#L71-L74)
