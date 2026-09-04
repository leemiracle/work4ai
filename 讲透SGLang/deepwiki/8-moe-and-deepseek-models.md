> 来源: [https://deepwiki.com/sgl-project/sglang/8-moe-and-deepseek-models](https://deepwiki.com/sgl-project/sglang/8-moe-and-deepseek-models)
> DeepWiki sgl-project/sglang | Last indexed: 27 Aug 2026 (94183a)

# MoE and DeepSeek Models

  Relevant source files 
 - [python/sglang/kernels/ops/moe/ep_moe_kernels.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/ops/moe/ep_moe_kernels.py)
 - [python/sglang/srt/layers/attention/base_attn_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/base_attn_backend.py)
 - [python/sglang/srt/layers/attention/deepseek_v4_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/deepseek_v4_backend.py)
 - [python/sglang/srt/layers/attention/deepseek_v4_backend_hip_radix.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/deepseek_v4_backend_hip_radix.py)
 - [python/sglang/srt/layers/attention/dsv4/compress_hip.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/dsv4/compress_hip.py)
 - [python/sglang/srt/layers/attention/dsv4/compressor.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/dsv4/compressor.py)
 - [python/sglang/srt/layers/attention/dsv4/compressor_v2.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/dsv4/compressor_v2.py)
 - [python/sglang/srt/layers/attention/dsv4/indexer.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/dsv4/indexer.py)
 - [python/sglang/srt/layers/attention/dsv4/metadata.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/dsv4/metadata.py)
 - [python/sglang/srt/layers/attention/hip_flash_mla.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/hip_flash_mla.py)
 - [python/sglang/srt/layers/attention/hybrid_attn_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/hybrid_attn_backend.py)
 - [python/sglang/srt/layers/attention/tbo_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/tbo_backend.py)
 - [python/sglang/srt/layers/moe/ep_moe/layer.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/ep_moe/layer.py)
 - [python/sglang/srt/layers/moe/flashinfer_trtllm_moe.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/flashinfer_trtllm_moe.py)
 - [python/sglang/srt/layers/moe/fused_moe_triton/layer.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/fused_moe_triton/layer.py)
 - [python/sglang/srt/layers/moe/moe_runner/deep_gemm.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/moe_runner/deep_gemm.py)
 - [python/sglang/srt/layers/moe/moe_runner/flashinfer_cutedsl.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/moe_runner/flashinfer_cutedsl.py)
 - [python/sglang/srt/layers/moe/moe_runner/flashinfer_trtllm.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/moe_runner/flashinfer_trtllm.py)
 - [python/sglang/srt/layers/moe/moe_runner/runner.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/moe_runner/runner.py)
 - [python/sglang/srt/layers/moe/token_dispatcher/__init__.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/token_dispatcher/__init__.py)
 - [python/sglang/srt/layers/moe/token_dispatcher/base.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/token_dispatcher/base.py)
 - [python/sglang/srt/layers/moe/token_dispatcher/deepep_v2.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/token_dispatcher/deepep_v2.py)
 - [python/sglang/srt/layers/moe/utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/utils.py)
 - [python/sglang/srt/layers/quantization/fp8.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/fp8.py)
 - [python/sglang/srt/layers/quantization/fp8_utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/fp8_utils.py)
 - [python/sglang/srt/layers/quantization/modelopt_quant.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/modelopt_quant.py)
 - [python/sglang/srt/layers/quantization/unquant.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/unquant.py)
 - [python/sglang/srt/mem_cache/deepseek_v4_compress_state.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/deepseek_v4_compress_state.py)
 - [python/sglang/srt/mem_cache/deepseek_v4_memory_pool.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/deepseek_v4_memory_pool.py)
 - [python/sglang/srt/model_executor/model_runner_components/attention_backend_setup.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner_components/attention_backend_setup.py)
 - [python/sglang/srt/model_executor/runner_utils/shared_read_event.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/runner_utils/shared_read_event.py)
 - [python/sglang/srt/model_loader/utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_loader/utils.py)
 - [python/sglang/srt/models/deepseek_nextn.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/deepseek_nextn.py)
 - [python/sglang/srt/models/deepseek_v2.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/deepseek_v2.py)
 - [python/sglang/srt/models/deepseek_v4.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/deepseek_v4.py)
 - [python/sglang/srt/models/deepseek_v4_nextn.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/deepseek_v4_nextn.py)
 - [test/registered/amd/test_deepseek_v4_pro_fp4_mtp.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/amd/test_deepseek_v4_pro_fp4_mtp.py)
 - [test/registered/attention/test_trtllm_mha_encoder_only.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/attention/test_trtllm_mha_encoder_only.py)
 - [test/registered/attention/test_trtllm_mha_graph_metadata.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/attention/test_trtllm_mha_graph_metadata.py)
 - [test/registered/attention/unittests/dsv4/test_deepseek_v4.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/attention/unittests/dsv4/test_deepseek_v4.py)
 - [test/registered/kernels/benchmark/attention/bench_dsv4_fp4_indexer.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/kernels/benchmark/attention/bench_dsv4_fp4_indexer.py)
 - [test/registered/unit/configs/test_multimodal_piecewise_cuda_graph.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/configs/test_multimodal_piecewise_cuda_graph.py)
 - [test/registered/unit/layers/test_dsv4_nonpaged_indexer.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/layers/test_dsv4_nonpaged_indexer.py)
 - [test/registered/unit/model_executor/model_runner_components/test_attention_backend_setup.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/model_executor/model_runner_components/test_attention_backend_setup.py)
 - [test/registered/unit/model_executor/runner/test_decode_cuda_graph_shared_read_fence.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/model_executor/runner/test_decode_cuda_graph_shared_read_fence.py)
 - [test/registered/unit/model_executor/runner/test_prefill_cuda_graph_padding.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/model_executor/runner/test_prefill_cuda_graph_padding.py)
 - [test/registered/unit/model_executor/runner/test_prefill_shared_read_done.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/model_executor/runner/test_prefill_shared_read_done.py)
 - [test/registered/unit/spec/test_dflash_overlap_hostsync.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/spec/test_dflash_overlap_hostsync.py)
 - [test/registered/xpu/test_moe_ld_padding.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/xpu/test_moe_ld_padding.py)
 
  This document provides a high-level overview of Mixture of Experts (MoE) architectures and DeepSeek-specific enhancements within the SGLang codebase. It covers the core MoE layer implementations, the DeepSeek V2/V3/V4 model architectures including Multi-head Latent Attention (MLA) and Native Sparse Attention (NSA), routing mechanisms that distribute tokens to experts, and MoE-specific quantization and optimization strategies.

 As this is a parent page, detailed technical information and implementation specifics are delegated to child pages:

 
 - [MoE Layer Architecture](https://deepwiki.com/sgl-project/sglang/8.1-moe-layer-architecture) — Document FusedMoE implementation, MoE forward pass, expert computation, and FlashInfer/TrtLLM MoE backends.
 - [DeepSeek Architecture and MLA](https://deepwiki.com/sgl-project/sglang/8.2-deepseek-architecture-and-mla) — Explain DeepSeek-V2/V3/V4 architecture, Multi-head Latent Attention (MLA), NSA attention, and auxiliary loss.
 - [Expert Routing and Token Dispatch](https://deepwiki.com/sgl-project/sglang/8.3-expert-routing-and-token-dispatch) — Document TopK routing, token dispatch mechanisms, hierarchical expert selection, and EPLB (Expert Load Balancing).
 - [MoE Quantization and Optimization](https://deepwiki.com/sgl-project/sglang/8.4-moe-quantization-and-optimization) — Explain MoE-specific quantization, expert specialization kernels, two-batch overlap, two-batch overlap interactions, and optimization techniques.
 
 
---

 
## MoE Layer Architecture

 SGLang uses two main MoE implementations – `FusedMoE` and `DeepEPMoE`. These layers enable expert parallelism (EP) and tensor parallelism (TP), and integrate with various backend kernels for expert computation. They handle the critical MoE flow of routing tokens to experts, running expert computations, and combining the outputs.

 
 - `FusedMoE` is the core MoE implementation [python/sglang/srt/layers/moe/fused_moe_triton/layer.py105](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/fused_moe_triton/layer.py#L105-L105) supporting multiple backends (Triton, FlashInfer, DeepGEMM). It manages fused up and gate linear projections (`w13`) and the down projection (`w2`), coordinated by a `MoeRunnerConfig` [python/sglang/srt/layers/moe/moe_runner/base.py32-34](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/moe_runner/base.py#L32-L34)
 - `DeepEPMoE` [python/sglang/srt/layers/moe/ep_moe/layer.py63-67](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/ep_moe/layer.py#L63-L67) inherits `FusedMoE` and specializes for DeepEP and Mooncake backends, providing optimized execution and integration with hardware-specific dispatchers like `MaybeTboDeepEPDispatcher` [python/sglang/srt/layers/moe/fused_moe_triton/layer.py181-192](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/fused_moe_triton/layer.py#L181-L192)
 
 
### MoE Layer Architecture Diagram

 
```

```

 **Sources**:

 
 - [python/sglang/srt/layers/moe/fused_moe_triton/layer.py105-192](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/fused_moe_triton/layer.py#L105-L192)
 - [python/sglang/srt/layers/moe/moe_runner/base.py32-36](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/moe_runner/base.py#L32-L36)
 - [python/sglang/srt/layers/moe/ep_moe/layer.py63-180](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/ep_moe/layer.py#L63-L180)
 - [python/sglang/srt/layers/quantization/base_config.py49-60](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/base_config.py#L49-L60)
 
 
---

 
## DeepSeek Architecture and MLA

 DeepSeek models use innovative attention mechanisms designed for sparse, large-scale expert networks. The main DeepSeek variants V2, V3, and V4 leverage Multi-head Latent Attention (MLA) and Native Sparse Attention (NSA) to efficiently scale attention.

 Key components:

 
 - **MLA** supports multi-head sparse attention using learned latent tokens. Implementation details are found in `DeepseekMLAForwardMixin` [python/sglang/srt/models/deepseek_common/attention_forward_methods.py174](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/deepseek_common/attention_forward_methods.py#L174-L174)
 - **NSA** (Native Sparse Attention) optimizes sparse attention with indexed routing using the `Indexer` operator [python/sglang/srt/layers/attention/dsa/dsa_indexer.py64](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/dsa/dsa_indexer.py#L64-L64)
 - **DeepSeek-V4** introduces specialized kernels like `sglang_per_token_group_quant_fp8_dsv4_wo_a` [python/sglang/srt/models/deepseek_v4.py30-31](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/deepseek_v4.py#L30-L31) and optimized RoPE implementations like `Dsv4NpuRoPE` [python/sglang/srt/models/deepseek_v4.py47](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/deepseek_v4.py#L47-L47) It also utilizes `C4Indexer` for hierarchical indexing [python/sglang/srt/models/deepseek_v4.py55](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/deepseek_v4.py#L55-L55)
 - **NextN Speculative Decoding** is supported for DeepSeek models through `DeepseekModelNextN` [python/sglang/srt/models/deepseek_nextn.py101](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/deepseek_nextn.py#L101-L101) which utilizes specialized norm kernels like `fused_eh_norm` [python/sglang/srt/models/deepseek_nextn.py27](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/deepseek_nextn.py#L27-L27)
 
 
### DeepSeek Architecture to Code Entity Mapping

 
```

```

 **Sources**:

 
 - [python/sglang/srt/models/deepseek_v2.py44-51](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/deepseek_v2.py#L44-L51)
 - [python/sglang/srt/models/deepseek_v4.py36-60](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/deepseek_v4.py#L36-L60)
 - [python/sglang/srt/models/deepseek_nextn.py101-188](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/deepseek_nextn.py#L101-L188)
 - [python/sglang/srt/layers/attention/deepseek_v4_backend.py169-199](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/attention/deepseek_v4_backend.py#L169-L199)
 
 
---

 
## Expert Routing and Token Dispatch

 Routing policies select which experts handle each token dynamically. SGLang supports advanced routing mechanisms like TopK routing with weighted selections, grouped expert sets, and fused dispatch kernels.

 
 - The `TopKConfig` dataclass [python/sglang/srt/layers/moe/topk.py49](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/topk.py#L49-L49) defines routing parameters such as `top_k`, groups, and scoring strategies.
 - `fused_topk_deepseek` [python/sglang/srt/layers/moe/topk.py158](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/topk.py#L158-L158) provides a high-performance kernel for DeepSeek-style routing.
 - Dispatchers like `StandardDispatcher`, `FlashinferDispatcher`, and `DeepEPv2Dispatcher` [python/sglang/srt/layers/moe/fused_moe_triton/layer.py161-200](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/fused_moe_triton/layer.py#L161-L200) implement the actual token movement across the network or GPU memory.
 - `ExpertLocationDispatchInfo` [python/sglang/srt/models/deepseek_v2.py60](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/deepseek_v2.py#L60-L60) manages the mapping between tokens and their target expert locations in distributed environments.
 
 
### Routing Components Table

 
| Entity/Function | Description | Location |
|---|---|---|
| TopKConfig | Defines TopK routing parameters | layers/moe/topk.py49 |
| fused_topk_deepseek | Fused kernel for DeepSeek grouped top-k | layers/moe/topk.py158 |
| StandardTopKOutput | Standard format for routing results | layers/moe/topk.py29 |
| MaybeTboDeepEPDispatcher | Dispatcher supporting two-batch overlap | layers/moe/fused_moe_triton/layer.py181-192 |
| RoutingMethodType | Enum for routing algorithms (TopK, Hash, etc.) | layers/moe/utils.py115 |

 **Sources**:

 
 - [python/sglang/srt/layers/moe/topk.py29-158](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/topk.py#L29-L158)
 - [python/sglang/srt/layers/moe/fused_moe_triton/layer.py161-200](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/fused_moe_triton/layer.py#L161-L200)
 - [python/sglang/srt/layers/moe/utils.py115](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/utils.py#L115-L115)
 
 
---

 
## MoE Quantization and Optimization

 SGLang includes MoE-specific quantization strategies to balance model accuracy and efficiency, supporting formats like FP8, FP4, and MXFP4.

 
 - `Fp8MoEMethod` [python/sglang/srt/layers/quantization/fp8.py65](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/fp8.py#L65-L65) handles 8-bit floating point quantization with per-token and block-scaling support.
 - `ModelOptNvFp4FusedMoEMethod` [python/sglang/srt/layers/quantization/modelopt_quant.py67](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/modelopt_quant.py#L67-L67) implements specialized FP4 kernels for Blackwell GPUs, including padding logic for alignment [python/sglang/srt/layers/quantization/modelopt_quant.py172-207](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/modelopt_quant.py#L172-L207)
 - `Mxfp4MoEMethod` [python/sglang/srt/layers/quantization/mxfp4.py45](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/mxfp4.py#L45-L45) supports the OAI MXFP4 format using Triton and FlashInfer backends.
 - Optimizations like **Two-Batch Overlap (TBO)** [python/sglang/srt/batch_overlap/two_batch_overlap.py40-43](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/batch_overlap/two_batch_overlap.py#L40-L43) and `MaybeTboDeepEPDispatcher` [python/sglang/srt/layers/moe/fused_moe_triton/layer.py181-192](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/fused_moe_triton/layer.py#L181-L192) allow for overlapping communication and computation.
 - Specialized FP8 group quantization kernels like `sglang_per_token_group_quant_fp8` [python/sglang/srt/models/deepseek_v4.py33-34](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/models/deepseek_v4.py#L33-L34) are used to prepare activations for MoE GEMMs.
 
 
### MoE Quantization Formats Comparison

 
| Feature | FP8 MoE | FP4 MoE (NVFP4) | MXFP4 MoE |
|---|---|---|---|
| Format | E4M3 FP8 | 2 FP4 per byte | Block-scaled FP4 |
| Primary Backend | Triton / DeepGEMM | FlashInfer | Triton / FlashInfer |
| Configuration | Fp8MoEMethod | ModelOptNvFp4FusedMoEMethod | Mxfp4MoEMethod |
| Key File | fp8.py | modelopt_quant.py | mxfp4.py |

 **Sources**:

 
 - [python/sglang/srt/layers/quantization/fp8.py31-65](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/fp8.py#L31-L65)
 - [python/sglang/srt/layers/quantization/modelopt_quant.py67-152](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/modelopt_quant.py#L67-L152)
 - [python/sglang/srt/layers/quantization/fp8_utils.py168-186](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/fp8_utils.py#L168-L186)
 - [python/sglang/srt/layers/moe/moe_runner/flashinfer_trtllm.py150-182](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/moe_runner/flashinfer_trtllm.py#L150-L182)
