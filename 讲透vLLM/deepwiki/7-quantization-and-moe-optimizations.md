# Quantization and MoE Optimizations

> 来源: https://deepwiki.com/vllm-project/vllm/7-quantization-and-moe-optimizations 抓取日期: 2026-09-02
> 章节: 第 7 章 量化与 MoE 优化

---

Relevant source files

  * [csrc/libtorch_stable/attention/merge_attn_states.cu](https://github.com/vllm-project/vllm/blob/185cada3/csrc/libtorch_stable/attention/merge_attn_states.cu)
  * [csrc/libtorch_stable/mamba/selective_scan.h](https://github.com/vllm-project/vllm/blob/185cada3/csrc/libtorch_stable/mamba/selective_scan.h)
  * [csrc/libtorch_stable/mamba/selective_scan_fwd.cu](https://github.com/vllm-project/vllm/blob/185cada3/csrc/libtorch_stable/mamba/selective_scan_fwd.cu)
  * [csrc/libtorch_stable/mamba/static_switch.h](https://github.com/vllm-project/vllm/blob/185cada3/csrc/libtorch_stable/mamba/static_switch.h)
  * [csrc/libtorch_stable/sampler.cu](https://github.com/vllm-project/vllm/blob/185cada3/csrc/libtorch_stable/sampler.cu)
  * [tests/kernels/attention/test_deepgemm_attention.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/kernels/attention/test_deepgemm_attention.py)
  * [tests/kernels/attention/test_rocm_aiter_mla_causal_verify_mask.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/kernels/attention/test_rocm_aiter_mla_causal_verify_mask.py)
  * [tests/kernels/attention/test_rocm_aiter_mla_head_padding.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/kernels/attention/test_rocm_aiter_mla_head_padding.py)
  * [tests/kernels/attention/test_rocm_triton_attn_dsv4.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/kernels/attention/test_rocm_triton_attn_dsv4.py)
  * [tests/kernels/moe/test_cutlass_moe.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/kernels/moe/test_cutlass_moe.py)
  * [tests/kernels/moe/test_flashinfer.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/kernels/moe/test_flashinfer.py)
  * [tests/kernels/moe/test_moe.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/kernels/moe/test_moe.py)
  * [tests/kernels/moe/test_unquantized_backend_selection.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/kernels/moe/test_unquantized_backend_selection.py)
  * [tests/kernels/quantization/test_fp8_quant_group.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/kernels/quantization/test_fp8_quant_group.py)
  * [tests/kernels/test_top_k_per_row.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/kernels/test_top_k_per_row.py)
  * [tests/quantization/test_blackwell_moe.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/quantization/test_blackwell_moe.py)
  * [tests/quantization/test_fp8.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/quantization/test_fp8.py)
  * [tests/tool_parsers/test_dots_tool_parser.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/tool_parsers/test_dots_tool_parser.py)
  * [tests/v1/attention/test_indexer_native_next_n.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/attention/test_indexer_native_next_n.py)
  * [tests/v1/attention/test_rocm_aiter_mla_fp8_decode_routing.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/attention/test_rocm_aiter_mla_fp8_decode_routing.py)
  * [tests/v1/attention/test_rocm_aiter_mla_mtp_split.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/attention/test_rocm_aiter_mla_mtp_split.py)
  * [vllm/model_executor/layers/fused_moe/config.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/config.py)
  * [vllm/model_executor/layers/fused_moe/experts/cutlass_moe.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/experts/cutlass_moe.py)
  * [vllm/model_executor/layers/fused_moe/experts/rocm_aiter_moe.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/experts/rocm_aiter_moe.py)
  * [vllm/model_executor/layers/fused_moe/experts/xpu_moe.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/experts/xpu_moe.py)
  * [vllm/model_executor/layers/fused_moe/fused_moe.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/fused_moe.py)
  * [vllm/model_executor/layers/fused_moe/fused_moe_method_base.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/fused_moe_method_base.py)
  * [vllm/model_executor/layers/fused_moe/fused_moe_modular_method.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/fused_moe_modular_method.py)
  * [vllm/model_executor/layers/fused_moe/layer.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/layer.py)
  * [vllm/model_executor/layers/fused_moe/modular_kernel.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/modular_kernel.py)
  * [vllm/model_executor/layers/fused_moe/oracle/fp8.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/oracle/fp8.py)
  * [vllm/model_executor/layers/fused_moe/oracle/mxfp4.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/oracle/mxfp4.py)
  * [vllm/model_executor/layers/fused_moe/oracle/nvfp4.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/oracle/nvfp4.py)
  * [vllm/model_executor/layers/fused_moe/oracle/unquantized.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/oracle/unquantized.py)
  * [vllm/model_executor/layers/fused_moe/oracle/w4a8.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/oracle/w4a8.py)
  * [vllm/model_executor/layers/fused_moe/topk_weight_and_reduce.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/topk_weight_and_reduce.py)
  * [vllm/model_executor/layers/fused_moe/unquantized_fused_moe_method.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/unquantized_fused_moe_method.py)
  * [vllm/model_executor/layers/fused_moe/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/utils.py)
  * [vllm/model_executor/layers/quantization/compressed_tensors/compressed_tensors_moe/compressed_tensors_moe_w4a4_mxfp4.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/compressed_tensors/compressed_tensors_moe/compressed_tensors_moe_w4a4_mxfp4.py)
  * [vllm/model_executor/layers/quantization/compressed_tensors/compressed_tensors_moe/compressed_tensors_moe_w4a8_fp8.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/compressed_tensors/compressed_tensors_moe/compressed_tensors_moe_w4a8_fp8.py)
  * [vllm/model_executor/layers/quantization/fp8.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/fp8.py)
  * [vllm/model_executor/layers/quantization/input_quant_fp8.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/input_quant_fp8.py)
  * [vllm/model_executor/layers/quantization/modelopt.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/modelopt.py)
  * [vllm/model_executor/layers/quantization/mxfp4.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/mxfp4.py)
  * [vllm/model_executor/layers/quantization/quark/quark_moe.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/quark/quark_moe.py)
  * [vllm/model_executor/layers/quantization/utils/flashinfer_fp4_moe.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/utils/flashinfer_fp4_moe.py)
  * [vllm/model_executor/layers/quantization/utils/flashinfer_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/utils/flashinfer_utils.py)
  * [vllm/model_executor/layers/quantization/utils/fp8_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/utils/fp8_utils.py)
  * [vllm/model_executor/layers/sparse_attn_indexer.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/sparse_attn_indexer.py)
  * [vllm/models/deepseek_v4/amd/rocm.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/models/deepseek_v4/amd/rocm.py)
  * [vllm/models/dots3_note/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/models/dots3_note/__init__.py)
  * [vllm/models/dots3_note/common/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/models/dots3_note/common/__init__.py)
  * [vllm/utils/deep_gemm.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/utils/deep_gemm.py)
  * [vllm/v1/attention/backends/mla/indexer.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/mla/indexer.py)
  * [vllm/v1/attention/backends/mla/rocm_aiter_mla.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/mla/rocm_aiter_mla.py)
  * [vllm/v1/attention/backends/mla/rocm_aiter_mla_sparse.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/mla/rocm_aiter_mla_sparse.py)
  * [vllm/v1/attention/ops/rocm_aiter_mla_sparse.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/ops/rocm_aiter_mla_sparse.py)

This page covers vLLM's quantization infrastructure and Mixture-of-Experts (MoE) kernel system. It explains the quantization method registry, the FP8 linear and MoE pipelines, the modular MoE kernel abstraction, and how backend selection is performed at runtime.

For details on the linear layer and normalization implementations that host quantized weights, see Linear Layers and Normalization. For distributed expert parallelism configuration, see [Parallelism Strategies](/vllm-project/vllm/9.1-parallelism-strategies). For the general attention backend system, see [Attention Backends](/vllm-project/vllm/8-attention-backends).

* * *

## Quantization System Overview

Every quantization scheme implements the `QuantizationConfig` abstract base class ([vllm/model_executor/layers/quantization/base_config.py45-48](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/base_config.py#L45-L48)) and is registered in a central registry. When a model is loaded, the config's `get_quant_method` is called per layer to return a `QuantizeMethodBase` that knows how to `create_weights`, `process_weights_after_loading`, and `apply` the kernel.

**Quantization method dispatch diagram:**

Sources: [vllm/model_executor/layers/quantization/fp8.py175-200](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/fp8.py#L175-L200) [vllm/model_executor/layers/quantization/modelopt.py183-205](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/modelopt.py#L183-L205) [vllm/model_executor/layers/quantization/mxfp4.py81-103](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/mxfp4.py#L81-L103)

* * *

### Supported Quantization Methods

vLLM supports a wide array of quantization formats, from standard FP8 to specialized 4-bit formats like NVFP4 and MXFP4.

Method| Config Class| Key File  
---|---|---  
`fp8`| `Fp8Config`| [vllm/model_executor/layers/quantization/fp8.py95-109](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/fp8.py#L95-L109)  
`modelopt`| `ModelOptQuantConfigBase`| [vllm/model_executor/layers/quantization/modelopt.py133-142](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/modelopt.py#L133-L142)  
`mxfp4`| `Mxfp4Config`| [vllm/model_executor/layers/quantization/mxfp4.py45-55](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/mxfp4.py#L45-L55)  
`quark`| `QuarkMoEMethod`| [vllm/model_executor/layers/quantization/quark/quark_moe.py95-101](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/quark/quark_moe.py#L95-L101)  
`compressed-tensors`| `CompressedTensorsConfig`| [vllm/model_executor/layers/quantization/__init__.py119-121](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/__init__.py#L119-L121)  
  
Sources: [vllm/model_executor/layers/quantization/fp8.py136-137](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/fp8.py#L136-L137) [vllm/model_executor/layers/quantization/mxfp4.py65-66](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/mxfp4.py#L65-L66) [vllm/model_executor/layers/quantization/quark/quark_moe.py100-137](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/quark/quark_moe.py#L100-L137) [vllm/model_executor/layers/quantization/__init__.py12-46](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/__init__.py#L12-L46)

For more details on specific methods, see [Quantization Methods Overview](/vllm-project/vllm/7.1-quantization-methods-overview).

* * *

## FP8 Quantization

FP8 quantization in vLLM is configured via `Fp8Config` and implemented through `Fp8LinearMethod` for linear layers and `Fp8MoEMethod` for MoE layers.

### Fp8Config

`Fp8Config` ([vllm/model_executor/layers/quantization/fp8.py95-174](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/fp8.py#L95-L174)) controls:

  * `activation_scheme`: `"static"` or `"dynamic"` — whether activation scales are pre-computed or computed per-token at runtime ([vllm/model_executor/layers/quantization/fp8.py110-112](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/fp8.py#L110-L112)).
  * `is_checkpoint_fp8_serialized`: `True` if weights are stored as FP8 in the checkpoint ([vllm/model_executor/layers/quantization/fp8.py108](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/fp8.py#L108-L108)).
  * `weight_block_size`: enables block-wise quantization (e.g. `[128, 128]`). Requires `is_checkpoint_fp8_serialized=True` and `activation_scheme="dynamic"` ([vllm/model_executor/layers/quantization/fp8.py115-132](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/fp8.py#L115-L132)).

For detailed implementation details on block quantization and backend selection (CUTLASS, DeepGemm, etc.), refer to [FP8 and Low-Precision Quantization](/vllm-project/vllm/7.2-fp8-and-low-precision-quantization).

Sources: [vllm/model_executor/layers/quantization/fp8.py19-21](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/fp8.py#L19-L21) [vllm/model_executor/layers/quantization/fp8.py190-196](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/fp8.py#L190-L196)

* * *

## FusedMoE Layer Architecture

The `FusedMoE` layer is a core component for Mixture-of-Experts models, designed for efficiency and flexibility. It integrates various quantization methods and execution backends.

### FusedMoE Factory and Runner

The `FusedMoEFactory` ([vllm/model_executor/layers/fused_moe/layer.py88-138](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/layer.py#L88-L138)) constructs the MoE execution pipeline. It orchestrates:

  * **Router** : Token-to-expert assignment via `FusedMoERouter` created by `create_fused_moe_router` ([vllm/model_executor/layers/fused_moe/layer.py27-32](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/layer.py#L27-L32)).
  * **Experts** : Parameters stored in `RoutedExperts` ([vllm/model_executor/layers/fused_moe/layer.py26](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/layer.py#L26-L26)).
  * **Runner** : Orchestration via `MoERunner` ([vllm/model_executor/layers/fused_moe/layer.py33-35](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/layer.py#L33-L35)).

**FusedMoE Code Entity Space Diagram:**

Sources: [vllm/model_executor/layers/fused_moe/layer.py43-69](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/layer.py#L43-L69) [vllm/model_executor/layers/fused_moe/layer.py139-152](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/layer.py#L139-L152)

### Modular Kernel Architecture

The MoE execution pipeline is decomposed into independent stages in `modular_kernel.py`. This allows mixing and matching different backends for routing, expert execution, and reduction.

Interface| Role  
---|---  
`FusedMoEExperts`| Executes core expert GEMMs + activations. Supports `DeepGemm`, `FlashInfer`, `Triton`, and `AITER` ([vllm/model_executor/layers/fused_moe/modular_kernel.py65-69](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/modular_kernel.py#L65-L69)).  
`FusedMoEPrepareAndFinalize`| Handles input quantization, token dispatch (EP), and result finalization ([vllm/model_executor/layers/fused_moe/modular_kernel.py180-188](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/modular_kernel.py#L180-L188)).  
  
For details on the sub-modules (oracle, experts, runner), see [FusedMoE Layer Architecture](/vllm-project/vllm/7.3-fusedmoe-layer-architecture).

Sources: [vllm/model_executor/layers/fused_moe/modular_kernel.py46-81](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/modular_kernel.py#L46-L81) [vllm/model_executor/layers/fused_moe/layer.py139-145](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/layer.py#L139-L145)

* * *

## MoE Quantization and Backend Selection

Each quantization config supplies a `FusedMoEMethodBase` subclass for `FusedMoE` layers. vLLM uses an "oracle" system to select the best backend based on hardware and quantization format.

### Backend Selection Flow

Backends like `FLASHINFER_TRTLLM`, `DEEPGEMM`, and `AITER` are prioritized based on platform capability. For example, `select_fp8_moe_backend` chooses the optimal FP8 implementation ([vllm/model_executor/layers/fused_moe/oracle/fp8.py69-133](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/oracle/fp8.py#L69-L133)).

**MoE Backend Selection Flow:**

Sources: [vllm/model_executor/layers/fused_moe/oracle/mxfp4.py154-199](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/oracle/mxfp4.py#L154-L199) [vllm/model_executor/layers/fused_moe/modular_kernel.py50-57](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/modular_kernel.py#L50-L57)

For detailed documentation on MoE-specific quantization and backends, see [MoE Quantization and Backend Selection](/vllm-project/vllm/7.4-moe-quantization-and-backend-selection).

* * *

## Triton and FlashInfer Kernels

The Triton-based MoE kernels implement a "sorted token" pattern to efficiently process tokens routed to different experts ([vllm/model_executor/layers/fused_moe/fused_moe.py113-138](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/fused_moe.py#L113-L138)). vLLM also integrates `FlashInfer` for high-performance MoE kernels, especially for FP8 and FP4 formats.

The routing method is configurable via `RoutingMethodType`, supporting methods like `Default` (Softmax), `DeepSeekV3` (Sigmoid + Bias), and `Llama4` ([vllm/model_executor/layers/fused_moe/config.py102-130](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/config.py#L102-L130)).

Sources: [vllm/model_executor/layers/fused_moe/config.py132-171](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/config.py#L132-L171) [vllm/model_executor/layers/fused_moe/fused_moe.py142-150](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/fused_moe.py#L142-L150)

* * *

## Weight Scale Granularities

The `FusedMoEQuantDesc` and associated logic capture the scale granularities supported by MoE kernels ([vllm/model_executor/layers/fused_moe/config.py175-194](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/config.py#L175-L194)):

Granularity| Description  
---|---  
**Per-Tensor**|  Single scale for the entire weight tensor ([vllm/model_executor/layers/quantization/utils/quant_utils.py67-71](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/utils/quant_utils.py#L67-L71)).  
**Per-Row/Column**|  Scaling per individual row or column ([vllm/model_executor/layers/fused_moe/config.py188-189](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/config.py#L188-L189)).  
**Block-wise**|  2D block-wise scaling (e.g., 128x128 for DeepSeek or 1x32 for MXFP4) ([vllm/model_executor/layers/fused_moe/config.py190-193](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/config.py#L190-L193)).  
  
Sources: [vllm/model_executor/layers/fused_moe/config.py186-193](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/config.py#L186-L193) [vllm/model_executor/layers/fused_moe/oracle/mxfp4.py78-82](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/oracle/mxfp4.py#L78-L82) [vllm/model_executor/layers/quantization/utils/quant_utils.py67-71](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/utils/quant_utils.py#L67-L71)
