> 来源: [https://deepwiki.com/sgl-project/sglang/10-model-execution-layers](https://deepwiki.com/sgl-project/sglang/10-model-execution-layers)
> DeepWiki sgl-project/sglang | Last indexed: 27 Aug 2026 (94183a)

# Model Execution Layers

  Relevant source files 
 - [benchmark/kernels/all_reduce/benchmark_fused_ar_rms_amd.py](https://github.com/sgl-project/sglang/blob/94183a8d/benchmark/kernels/all_reduce/benchmark_fused_ar_rms_amd.py)
 - [benchmark/kernels/all_reduce/benchmark_fused_ar_rms_quant_amd.py](https://github.com/sgl-project/sglang/blob/94183a8d/benchmark/kernels/all_reduce/benchmark_fused_ar_rms_quant_amd.py)
 - [python/sglang/kernels/ops/attention/verify_mla.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/ops/attention/verify_mla.py)
 - [python/sglang/srt/distributed/communication_op.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/distributed/communication_op.py)
 - [python/sglang/srt/distributed/device_communicators/pynccl.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/distributed/device_communicators/pynccl.py)
 - [python/sglang/srt/distributed/device_communicators/pynccl_wrapper.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/distributed/device_communicators/pynccl_wrapper.py)
 - [python/sglang/srt/distributed/parallel_state.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/distributed/parallel_state.py)
 - [python/sglang/srt/layers/attention/aiter_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/aiter_backend.py)
 - [python/sglang/srt/layers/attention/cutlass_mla_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/cutlass_mla_backend.py)
 - [python/sglang/srt/layers/attention/flashattention_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/flashattention_backend.py)
 - [python/sglang/srt/layers/attention/flashinfer_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/flashinfer_backend.py)
 - [python/sglang/srt/layers/attention/flashinfer_mla_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/flashinfer_mla_backend.py)
 - [python/sglang/srt/layers/attention/flashmla_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/flashmla_backend.py)
 - [python/sglang/srt/layers/attention/tokenspeed_mla_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/tokenspeed_mla_backend.py)
 - [python/sglang/srt/layers/attention/triton_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/triton_backend.py)
 - [python/sglang/srt/layers/attention/trtllm_mla_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/trtllm_mla_backend.py)
 - [python/sglang/srt/layers/attention/wave_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/wave_backend.py)
 - [python/sglang/srt/layers/communicator.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/communicator.py)
 - [python/sglang/srt/layers/dp_attention.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/dp_attention.py)
 - [python/sglang/srt/layers/flashinfer_comm_fusion.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/flashinfer_comm_fusion.py)
 - [python/sglang/srt/layers/layernorm.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/layernorm.py)
 - [test/registered/amd/perf/mi35x/test_qwen35_fp8_ar_fusion_mi35x.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/amd/perf/mi35x/test_qwen35_fp8_ar_fusion_mi35x.py)
 - [test/registered/attention/test_verify_shared_kv.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/attention/test_verify_shared_kv.py)
 - [test/registered/ops/test_aiter_allreduce_fusion_amd.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/ops/test_aiter_allreduce_fusion_amd.py)
 - [test/registered/ops/test_aiter_greedy_sample_amd.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/ops/test_aiter_greedy_sample_amd.py)
 - [test/registered/unit/layers/test_flashinfer_comm_fusion.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/layers/test_flashinfer_comm_fusion.py)
 
  This page documents the layer implementations that comprise model architectures in SGLang. These layers are the fundamental building blocks that are composed to create transformer-based language models. For information about model configuration and loading, see [Model Configuration and Loading](https://deepwiki.com/sgl-project/sglang/7-model-configuration-and-loading). For model parallelism strategies, see [Distributed Execution Strategies](https://deepwiki.com/sgl-project/sglang/6-distributed-execution-strategies).

 
## Overview

 Model execution layers in SGLang are modular components that implement the mathematical operations required by transformer architectures. Each layer type handles a specific operation such as attention, normalization, activation, linear transformation, and more.

 SGLang's layer system supports multiple backend implementations optimized for various hardware platforms and quantization schemes, enabling flexible and high-performance serving of large language models and vision-language models.

 Key characteristics:

 
 - **Support for multiple hardware platforms:** Including NVIDIA CUDA GPUs, AMD GPUs (via ROCm), Ascend NPUs, CPU with Intel AMX, XPU (Intel GPUs), MUSA (Moore Threads), and Apple MPS [python/sglang/srt/layers/layernorm.py35-45](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/layernorm.py#L35-L45) [python/sglang/srt/layers/attention/triton_backend.py46-55](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/triton_backend.py#L46-L55)
 - **Diverse quantization schemes:** FP8 (E4M3, E5M2), FP4 variants (NVFP4, MXFP4), INT8, and block-wise quantization [python/sglang/srt/layers/attention/flashattention_backend.py29-31](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/flashattention_backend.py#L29-L31) [python/sglang/srt/layers/communicator.py62-65](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/communicator.py#L62-L65)
 - **Rich attention implementations:** Multi-head Attention (MHA), Multi-head Latent Attention (MLA), Grouped Query Attention (GQA), DeepSeek Sparse Attention (NSA), and specialized attention kernels [python/sglang/srt/layers/attention/flashinfer_mla_backend.py5-12](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/flashinfer_mla_backend.py#L5-L12) [python/sglang/srt/layers/attention/flashmla_backend.py1-3](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/flashmla_backend.py#L1-L3)
 - **Distributed Communication Fusion:** Fused kernels that combine communication (all-reduce) with computation (RMSNorm) to reduce latency in tensor-parallel execution [python/sglang/srt/layers/layernorm.py191-207](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/layernorm.py#L191-L207) [python/sglang/srt/layers/flashinfer_comm_fusion.py46-63](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/flashinfer_comm_fusion.py#L46-L63)
 
 
## Layer Class Hierarchy and File Structure

 The SGLang codebase organizes layer implementations by functionality and backend specialization. The following diagram maps the major layer class categories to their core implementing classes and files:

 
### Model Layer Entity Mapping

 
```

```

 Sources: [python/sglang/srt/layers/layernorm.py101-106](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/layernorm.py#L101-L106) [python/sglang/srt/layers/attention/flashattention_backend.py130-143](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/flashattention_backend.py#L130-L143) [python/sglang/srt/layers/attention/trtllm_mla_backend.py187-205](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/trtllm_mla_backend.py#L187-L205) [python/sglang/srt/layers/communicator.py197-205](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/communicator.py#L197-L205)

 
## Layer Backend Dispatch Mechanism

 SGLang employs a multi-platform operator dispatch mechanism. At runtime, hardware detection and capability checks select the correct forwarding path:

 
 - **CUDA GPUs:** Trigger CUDA-specific forward methods using `sgl_kernel` or libraries like `flashinfer`. Supports Blackwell (SM100) and Hopper (SM90) optimizations [python/sglang/srt/layers/flashinfer_comm_fusion.py46-63](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/flashinfer_comm_fusion.py#L46-L63)
 - **ROCm AMD GPUs:** Employ ROCm-specific kernels or the `aiter` library. Supports gfx942 and gfx95 hardware [python/sglang/srt/layers/attention/aiter_backend.py60-78](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/aiter_backend.py#L60-L78) [python/sglang/srt/layers/attention/triton_backend.py63-65](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/triton_backend.py#L63-L65)
 - **NPUs:** Use Ascend device backends such as `torch_npu` and specialized kernels from `sgl_kernel_npu` [python/sglang/srt/layers/layernorm.py173-175](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/layernorm.py#L173-L175) [python/sglang/srt/distributed/parallel_state.py97-104](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/distributed/parallel_state.py#L97-L104)
 - **CPU Execution:** Uses specialized kernels (e.g., AMX support) and `torch.compile` infrastructure [python/sglang/srt/layers/layernorm.py54-56](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/layernorm.py#L54-L56)
 
 
### Hardware Dispatch Flow

 
```

```

 Sources: [python/sglang/srt/layers/layernorm.py48-60](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/layernorm.py#L48-L60) [python/sglang/srt/layers/attention/triton_backend.py57-63](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/triton_backend.py#L57-L63) [python/sglang/srt/distributed/parallel_state.py57-69](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/distributed/parallel_state.py#L57-L69)

 
## Normalization and Activation Layers

 Normalization layers provide critical transforms and support fusion for performance.

 
 - **Fused Kernels:** `fused_add_rmsnorm` and `gemma_fused_add_rmsnorm` combine residual addition and normalization [python/sglang/srt/layers/layernorm.py101-106](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/layernorm.py#L101-L106)
 - **All-Reduce Fusion:** `tensor_model_parallel_fused_allreduce_rmsnorm` fuses the TP all-reduce operation with the subsequent normalization pass to save memory bandwidth [python/sglang/srt/layers/layernorm.py191-207](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/layernorm.py#L191-L207)
 - **Quantization Integration:** Supports per-token quantization during the normalization pass (e.g., `rmsnorm_quant`) [python/sglang/srt/layers/layernorm.py88-96](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/layernorm.py#L88-L96)
 
 For thorough details, see [Normalization and Activation Layers](https://deepwiki.com/sgl-project/sglang/10.4-normalization-and-activation-layers).

 Sources: [python/sglang/srt/layers/layernorm.py14-28](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/layernorm.py#L14-L28) [python/sglang/srt/layers/communicator.py114-120](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/communicator.py#L114-L120)

 
## Linear Layers and Distributed Communication

 Linear layers implement the weight transformations for projections and MLPs, integrated with `LayerCommunicator` for distributed execution.

 
 - **LayerCommunicator:** Manages communication patterns (all-reduce, all-gather, reduce-scatter) for linear layers in TP/DP/EP configurations [python/sglang/srt/layers/communicator.py197-205](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/communicator.py#L197-L205)
 - **Communication Fusion:** Uses `flashinfer.comm` or `aiter` for low-latency all-reduce fusion on NVIDIA and AMD hardware respectively [python/sglang/srt/layers/flashinfer_comm_fusion.py90-110](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/flashinfer_comm_fusion.py#L90-L110) [python/sglang/srt/layers/communicator.py182-194](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/communicator.py#L182-L194)
 - **Symmetric Memory:** Optimizes collectives using symmetric memory allocations via `pynccl` or specialized hardware features [python/sglang/srt/layers/dp_attention.py189-194](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/dp_attention.py#L189-L194) [python/sglang/srt/distributed/parallel_state.py37-43](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/distributed/parallel_state.py#L37-L43)
 
 For implementation details, see [Linear Layers and Distributed Communication](https://deepwiki.com/sgl-project/sglang/10.5-linear-layers-and-distributed-communication).

 Sources: [python/sglang/srt/layers/communicator.py165-179](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/communicator.py#L165-L179) [python/sglang/srt/layers/dp_attention.py137-143](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/dp_attention.py#L137-L143)

 
## Attention Mechanisms and Backends

 Attention is optimized via multiple specialized backends:

 
 - **FlashAttentionBackend:** Optimized for standard MHA/GQA on NVIDIA GPUs, supporting FA3/FA4 features [python/sglang/srt/layers/attention/flashattention_backend.py130-143](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/flashattention_backend.py#L130-L143)
 - **FlashInferAttnBackend:** High-performance backend using the FlashInfer library for prefill and decode [python/sglang/srt/layers/attention/flashinfer_backend.py74-80](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/flashinfer_backend.py#L74-L80)
 - **TritonAttnBackend:** Flexible backend using Triton kernels, supporting sliding windows and unified KV pools [python/sglang/srt/layers/attention/triton_backend.py141-155](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/triton_backend.py#L141-L155)
 - **AiterAttnBackend:** Specialized for AMD GPUs, supporting MLA and vectorized 5D layouts [python/sglang/srt/layers/attention/aiter_backend.py142-150](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/aiter_backend.py#L142-L150)
 - **MLA Backends:** Dedicated support for Multi-head Latent Attention via `FlashMLABackend` and `TRTLLMMLABackend` (using FlashInfer's TRTLLM-compatible kernels) [python/sglang/srt/layers/attention/flashmla_backend.py58-70](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/flashmla_backend.py#L58-L70) [python/sglang/srt/layers/attention/trtllm_mla_backend.py187-205](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/trtllm_mla_backend.py#L187-L205)
 
 For comprehensive descriptions, see [Attention Mechanisms and Backends](https://deepwiki.com/sgl-project/sglang/10.2-attention-mechanisms-and-backends).

 Sources: [python/sglang/srt/layers/attention/flashinfer_mla_backend.py5-17](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/flashinfer_mla_backend.py#L5-L17) [python/sglang/srt/layers/attention/triton_backend.py174-184](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/triton_backend.py#L174-L184)

 
## Position Embeddings

 SGLang implements various positional embedding schemes:

 
 - **RoPE (Rotary Positional Embeddings):** Standard rotary embeddings with support for YaRN and other scaling methods.
 - **MLA RoPE:** Specialized RoPE handling for Multi-head Latent Attention that decouples RoPE from latent projections [python/sglang/srt/layers/attention/trtllm_mla_backend.py36-40](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/trtllm_mla_backend.py#L36-L40)
 
 For details, refer to [Positional Embeddings](https://deepwiki.com/sgl-project/sglang/10.3-positional-embeddings).

 
## Hybrid and Linear Attention Models

 SGLang supports hybrid architectures combining attention with linear recurrent layers:

 
 - **Mamba & Linear States:** Support for architectures like Mamba and hybrid models via specialized Triton wrappers [python/sglang/srt/layers/attention/triton_backend.py13-17](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/triton_backend.py#L13-L17)
 - **GDN/Kimi-Linear:** Support for models with alternative value head dimensions or non-standard attention structures [python/sglang/srt/layers/attention/aiter_backend.py189-197](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/aiter_backend.py#L189-L197)
 
 For further information, see [Hybrid and Linear Attention Models](https://deepwiki.com/sgl-project/sglang/10.6-hybrid-and-linear-attention-models).

 
---

 
## Child Pages

 
 - [Multi-Platform Layer Abstraction](https://deepwiki.com/sgl-project/sglang/10.1-multi-platform-layer-abstraction) — Explain MultiPlatformOp pattern, platform detection, hardware dispatch, and custom_op framework.
 - [Attention Mechanisms and Backends](https://deepwiki.com/sgl-project/sglang/10.2-attention-mechanisms-and-backends) — Document attention implementations (MHA, MLA, GQA), FlashAttention/FlashInfer/TrtLLM/AITER/Wave/NSA backends, backend selection, and dual-chunk attention.
 - [Positional Embeddings](https://deepwiki.com/sgl-project/sglang/10.3-positional-embeddings) — Document RoPE, YaRN, and other positional embedding implementations.
 - [Normalization and Activation Layers](https://deepwiki.com/sgl-project/sglang/10.4-normalization-and-activation-layers) — Explain RMSNorm, LayerNorm, SiLU, GELU, and fused operations.
 - [Linear Layers and Distributed Communication](https://deepwiki.com/sgl-project/sglang/10.5-linear-layers-and-distributed-communication) — Document LinearBase, ColumnParallelLinear, RowParallelLinear, and LayerCommunicator.
 - [Hybrid and Linear Attention Models](https://deepwiki.com/sgl-project/sglang/10.6-hybrid-and-linear-attention-models) — Document hybrid attention backends, linear attention (Mamba, GDN, FLA, Lightning), and models like Qwen3-Next, Falcon-H1, Kimi-Linear.
