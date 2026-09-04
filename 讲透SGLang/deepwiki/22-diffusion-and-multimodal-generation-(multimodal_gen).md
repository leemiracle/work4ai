> 来源: [https://deepwiki.com/sgl-project/sglang/22-diffusion-and-multimodal-generation-%28multimodal_gen%29](https://deepwiki.com/sgl-project/sglang/22-diffusion-and-multimodal-generation-%28multimodal_gen%29)
> DeepWiki sgl-project/sglang | Last indexed: 27 Aug 2026 (94183a)

# Diffusion and Multimodal Generation (multimodal_gen)

  Relevant source files 
 - [python/sglang/multimodal_gen/configs/models/dits/hunyuanvideo.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/configs/models/dits/hunyuanvideo.py)
 - [python/sglang/multimodal_gen/configs/models/dits/mova_audio.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/configs/models/dits/mova_audio.py)
 - [python/sglang/multimodal_gen/configs/models/dits/mova_video.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/configs/models/dits/mova_video.py)
 - [python/sglang/multimodal_gen/configs/models/dits/wanvideo.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/configs/models/dits/wanvideo.py)
 - [python/sglang/multimodal_gen/configs/models/dits/zimage.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/configs/models/dits/zimage.py)
 - [python/sglang/multimodal_gen/configs/pipeline_configs/base.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/configs/pipeline_configs/base.py)
 - [python/sglang/multimodal_gen/configs/pipeline_configs/zimage.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/configs/pipeline_configs/zimage.py)
 - [python/sglang/multimodal_gen/configs/sample/sampling_params.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/configs/sample/sampling_params.py)
 - [python/sglang/multimodal_gen/configs/sample/zimage.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/configs/sample/zimage.py)
 - [python/sglang/multimodal_gen/runtime/entrypoints/cli/generate.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/entrypoints/cli/generate.py)
 - [python/sglang/multimodal_gen/runtime/entrypoints/diffusion_generator.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/entrypoints/diffusion_generator.py)
 - [python/sglang/multimodal_gen/runtime/entrypoints/http_server.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/entrypoints/http_server.py)
 - [python/sglang/multimodal_gen/runtime/entrypoints/openai/common_api.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/entrypoints/openai/common_api.py)
 - [python/sglang/multimodal_gen/runtime/entrypoints/openai/image_api.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/entrypoints/openai/image_api.py)
 - [python/sglang/multimodal_gen/runtime/entrypoints/openai/protocol.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/entrypoints/openai/protocol.py)
 - [python/sglang/multimodal_gen/runtime/entrypoints/openai/utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/entrypoints/openai/utils.py)
 - [python/sglang/multimodal_gen/runtime/entrypoints/openai/video_api.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/entrypoints/openai/video_api.py)
 - [python/sglang/multimodal_gen/runtime/entrypoints/utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/entrypoints/utils.py)
 - [python/sglang/multimodal_gen/runtime/launch_server.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/launch_server.py)
 - [python/sglang/multimodal_gen/runtime/layers/attention/backends/xpu_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/layers/attention/backends/xpu_backend.py)
 - [python/sglang/multimodal_gen/runtime/layers/elementwise.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/layers/elementwise.py)
 - [python/sglang/multimodal_gen/runtime/layers/layernorm.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/layers/layernorm.py)
 - [python/sglang/multimodal_gen/runtime/managers/gpu_worker.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/managers/gpu_worker.py)
 - [python/sglang/multimodal_gen/runtime/managers/scheduler.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/managers/scheduler.py)
 - [python/sglang/multimodal_gen/runtime/models/bridges/mova_dual_tower.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/models/bridges/mova_dual_tower.py)
 - [python/sglang/multimodal_gen/runtime/models/dits/causal_wanvideo.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/models/dits/causal_wanvideo.py)
 - [python/sglang/multimodal_gen/runtime/models/dits/flux.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/models/dits/flux.py)
 - [python/sglang/multimodal_gen/runtime/models/dits/flux_2.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/models/dits/flux_2.py)
 - [python/sglang/multimodal_gen/runtime/models/dits/glm_image.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/models/dits/glm_image.py)
 - [python/sglang/multimodal_gen/runtime/models/dits/hunyuanvideo.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/models/dits/hunyuanvideo.py)
 - [python/sglang/multimodal_gen/runtime/models/dits/mova_audio_dit.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/models/dits/mova_audio_dit.py)
 - [python/sglang/multimodal_gen/runtime/models/dits/mova_video_dit.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/models/dits/mova_video_dit.py)
 - [python/sglang/multimodal_gen/runtime/models/dits/qwen_image.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/models/dits/qwen_image.py)
 - [python/sglang/multimodal_gen/runtime/models/dits/wanvideo.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/models/dits/wanvideo.py)
 - [python/sglang/multimodal_gen/runtime/models/dits/zimage.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/models/dits/zimage.py)
 - [python/sglang/multimodal_gen/runtime/pipelines_core/composed_pipeline_base.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/pipelines_core/composed_pipeline_base.py)
 - [python/sglang/multimodal_gen/runtime/pipelines_core/executors/parallel_executor.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/pipelines_core/executors/parallel_executor.py)
 - [python/sglang/multimodal_gen/runtime/pipelines_core/executors/pipeline_executor.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/pipelines_core/executors/pipeline_executor.py)
 - [python/sglang/multimodal_gen/runtime/pipelines_core/executors/sync_executor.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/pipelines_core/executors/sync_executor.py)
 - [python/sglang/multimodal_gen/runtime/pipelines_core/schedule_batch.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/pipelines_core/schedule_batch.py)
 - [python/sglang/multimodal_gen/runtime/pipelines_core/stages/base.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/pipelines_core/stages/base.py)
 - [python/sglang/multimodal_gen/runtime/pipelines_core/stages/decoding.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/pipelines_core/stages/decoding.py)
 - [python/sglang/multimodal_gen/runtime/pipelines_core/stages/denoising.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/pipelines_core/stages/denoising.py)
 - [python/sglang/multimodal_gen/runtime/pipelines_core/stages/denoising_dmd.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/pipelines_core/stages/denoising_dmd.py)
 - [python/sglang/multimodal_gen/runtime/pipelines_core/stages/model_specific_stages/mova.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/pipelines_core/stages/model_specific_stages/mova.py)
 - [python/sglang/multimodal_gen/runtime/utils/model_overlay.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/utils/model_overlay.py)
 - [python/sglang/multimodal_gen/runtime/utils/perf_logger.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/utils/perf_logger.py)
 - [python/sglang/multimodal_gen/test/unit/test_model_overlay.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/test/unit/test_model_overlay.py)
 - [python/sglang/multimodal_gen/test/unit/test_zimage_pipeline_config.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/test/unit/test_zimage_pipeline_config.py)
 
  The SGLang diffusion framework provides a high-performance runtime for image and video generation using Diffusion Transformer (DiT) architectures. It extends SGLang's serving capabilities beyond text to include multimodal generation tasks such as Text-to-Image (T2I), Text-to-Video (T2V), and Image-to-Video (I2V) [python/sglang/multimodal_gen/runtime/entrypoints/diffusion_generator.py7-9](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/entrypoints/diffusion_generator.py#L7-L9)

 The system is designed with a multi-process architecture that separates request scheduling from GPU execution, supporting advanced optimizations like sequence parallelism (SP), classifier-free guidance (CFG) parallelism, and dynamic batching [python/sglang/multimodal_gen/runtime/managers/gpu_worker.py26-45](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/managers/gpu_worker.py#L26-L45)

 
### System Architecture Overview

 The framework uses a `DiffGenerator` as the primary entrypoint, which orchestrates a local or remote scheduler and multiple GPU workers [python/sglang/multimodal_gen/runtime/entrypoints/diffusion_generator.py101-125](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/entrypoints/diffusion_generator.py#L101-L125) Requests are encapsulated in `Req` objects that carry state through a multi-stage pipeline, delegating sampling parameters to a `SamplingParams` member [python/sglang/multimodal_gen/runtime/pipelines_core/schedule_batch.py68-80](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/pipelines_core/schedule_batch.py#L68-L80)

 
#### Code Entity Mapping

 The following diagram illustrates how high-level system components map to specific code entities within the `multimodal_gen` directory.

 **Component to Code Entity Map**

 
```

```

 Sources: [python/sglang/multimodal_gen/runtime/entrypoints/diffusion_generator.py101-125](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/entrypoints/diffusion_generator.py#L101-L125) [python/sglang/multimodal_gen/runtime/managers/gpu_worker.py131-154](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/managers/gpu_worker.py#L131-L154) [python/sglang/multimodal_gen/runtime/pipelines_core/schedule_batch.py68-80](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/pipelines_core/schedule_batch.py#L68-L80) [python/sglang/multimodal_gen/runtime/pipelines_core/schedule_batch.py50-64](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/pipelines_core/schedule_batch.py#L50-L64)

 
### Diffusion Runtime Architecture

 The runtime architecture is built around a functional pipeline where each generation request passes through distinct stages: validation, text encoding, latent preparation, denoising, and VAE decoding.

 
 - **DiffGenerator**: Provides a `from_pretrained` interface similar to HuggingFace Diffusers but backed by the SGLang optimized runtime [python/sglang/multimodal_gen/runtime/entrypoints/diffusion_generator.py127-147](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/entrypoints/diffusion_generator.py#L127-L147)
 - **GPU Workers**: Each `GPUWorker` manages a single device, initializing the distributed environment (TP, SP, Ring Parallel, or CFG parallel) and loading model components like Transformers and VAEs [python/sglang/multimodal_gen/runtime/managers/gpu_worker.py131-159](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/managers/gpu_worker.py#L131-L159) It manages `MemoryOccupationController` to handle model state and layerwise offloading [python/sglang/multimodal_gen/runtime/managers/gpu_worker.py52-57](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/managers/gpu_worker.py#L52-L57)
 - **Denoising Pipeline**: The `DenoisingContext` manages loop-scoped state including latents, timesteps, and guidance across inference steps [python/sglang/multimodal_gen/runtime/pipelines_core/stages/denoising.py209-218](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/pipelines_core/stages/denoising.py#L209-L218) It supports kernel fusions like `fused_linear_gelu` and `fused_ln_modulate` for performance [python/sglang/multimodal_gen/runtime/pipelines_core/stages/denoising.py161-199](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/pipelines_core/stages/denoising.py#L161-L199)
 
 Sources: [python/sglang/multimodal_gen/runtime/entrypoints/diffusion_generator.py101-125](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/entrypoints/diffusion_generator.py#L101-L125) [python/sglang/multimodal_gen/runtime/managers/gpu_worker.py131-159](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/managers/gpu_worker.py#L131-L159) [python/sglang/multimodal_gen/runtime/pipelines_core/stages/denoising.py209-218](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/pipelines_core/stages/denoising.py#L209-L218)

 For details, see [Diffusion Runtime Architecture](https://deepwiki.com/sgl-project/sglang/22.1-diffusion-runtime-architecture).

 
### Supported Models and Architectures

 SGLang supports a variety of state-of-the-art DiT models including video generation models like **WanVideo** and **HunyuanVideo**, as well as image models like **Flux**, **Qwen-Image**, and **Z-Image**. The framework is designed to be extensible via `SamplingParams` and model-specific configurations [python/sglang/multimodal_gen/configs/sample/sampling_params.py98-194](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/configs/sample/sampling_params.py#L98-L194)

 
| Model Family | Modality | Key Features Supported |
|---|---|---|
| Flux / Flux.2 | Image | SwiGLU activations, fused LN modulation, and latent IDs for Flux-2 python/sglang/multimodal_gen/runtime/models/dits/flux_2.py88-143 python/sglang/multimodal_gen/runtime/pipelines_core/schedule_batch.py131 |
| WanVideo | Video | T2V, I2V, TI2V blending, and Ulysses sequence parallelism python/sglang/multimodal_gen/runtime/models/dits/wanvideo.py197-208 python/sglang/multimodal_gen/runtime/managers/gpu_worker.py43-46 |
| Qwen-Image | Image | Multi-layered processing, fused linear-GELU, and specialized vision encoding python/sglang/multimodal_gen/runtime/models/dits/qwen_image.py17-22 python/sglang/multimodal_gen/runtime/models/dits/qwen_image.py112-142 |
| Z-Image | Image | Native BF16 RMSNorm, fused scale/shift kernels, and specialized latent padding python/sglang/multimodal_gen/runtime/models/dits/zimage.py61-79 python/sglang/multimodal_gen/runtime/models/dits/zimage.py82-102 |
| LTX-2 | Video/Audio | Audio prompt embeddings, fused RMSNorm+modulate, and diffusion-based decoding python/sglang/multimodal_gen/runtime/pipelines_core/schedule_batch.py122-126 python/sglang/multimodal_gen/runtime/pipelines_core/stages/denoising.py29 python/sglang/multimodal_gen/configs/sample/sampling_params.py187 |

 Sources: [python/sglang/multimodal_gen/configs/pipeline_configs/base.py51-112](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/configs/pipeline_configs/base.py#L51-L112) [python/sglang/multimodal_gen/runtime/pipelines_core/schedule_batch.py121-146](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/pipelines_core/schedule_batch.py#L121-L146) [python/sglang/multimodal_gen/runtime/pipelines_core/stages/denoising.py161-199](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/pipelines_core/stages/denoising.py#L161-L199)

 For details, see [Supported Diffusion Models and DiT Architectures](https://deepwiki.com/sgl-project/sglang/22.2-supported-diffusion-models-and-dit-architectures).

 
### Diffusion API and LoRA Support

 The framework provides an OpenAI-compatible HTTP API for image and video generation. It also includes native support for Low-Rank Adaptation (LoRA) and efficient memory management.

 
 - **LoRA Management**: Supports loading and swapping adapters. The `LoRAPipeline` handles the integration of these weights at runtime [python/sglang/multimodal_gen/runtime/managers/gpu_worker.py59-60](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/managers/gpu_worker.py#L59-L60)
 - **API Protocol**: Implements `SamplingParams` with support for parameters like `num_inference_steps`, `guidance_scale`, and `seed` [python/sglang/multimodal_gen/configs/sample/sampling_params.py165-194](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/configs/sample/sampling_params.py#L165-L194) The HTTP server supports both standard and realtime video endpoints.
 - **Memory Efficiency**: Uses `LayerwiseOffloadableModuleMixin` to enable serving large models that exceed single-GPU memory by offloading inactive layers to host memory [python/sglang/multimodal_gen/runtime/managers/memory_managers/layerwise_offload.py52-54](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/managers/memory_managers/layerwise_offload.py#L52-L54)
 
 **API Request Lifecycle**

 
```

```

 Sources: [python/sglang/multimodal_gen/runtime/entrypoints/diffusion_generator.py180-189](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/entrypoints/diffusion_generator.py#L180-L189) [python/sglang/multimodal_gen/runtime/managers/gpu_worker.py131-159](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/managers/gpu_worker.py#L131-L159) [python/sglang/multimodal_gen/runtime/pipelines_core/schedule_batch.py68-80](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/pipelines_core/schedule_batch.py#L68-L80)

 For details, see [Diffusion API and LoRA Support](https://deepwiki.com/sgl-project/sglang/22.3-diffusion-api-and-lora-support).
