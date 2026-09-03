# Glossary

> 来源: https://deepwiki.com/vllm-project/vllm/13-glossary 抓取日期: 2026-09-02
> 章节: 第 13 章 术语表

---

Relevant source files

  * [cmake/external_projects/vllm_flash_attn.cmake](https://github.com/vllm-project/vllm/blob/185cada3/cmake/external_projects/vllm_flash_attn.cmake)
  * [csrc/cpu/spec_decode_utils.cpp](https://github.com/vllm-project/vllm/blob/185cada3/csrc/cpu/spec_decode_utils.cpp)
  * [docs/design/attention_backends.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/design/attention_backends.md?plain=1)
  * [docs/models/supported_models.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/models/supported_models.md?plain=1)
  * [tests/compile/test_aot_compile.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/compile/test_aot_compile.py)
  * [tests/compile/test_codegen.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/compile/test_codegen.py)
  * [tests/compile/test_compile_ranges.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/compile/test_compile_ranges.py)
  * [tests/compile/test_config.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/compile/test_config.py)
  * [tests/compile/test_dynamic_shapes_compilation.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/compile/test_dynamic_shapes_compilation.py)
  * [tests/compile/test_graph_partition.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/compile/test_graph_partition.py)
  * [tests/compile/test_structured_logging.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/compile/test_structured_logging.py)
  * [tests/config/test_config_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/config/test_config_utils.py)
  * [tests/distributed/eplb_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/distributed/eplb_utils.py)
  * [tests/distributed/test_eplb_algo.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/distributed/test_eplb_algo.py)
  * [tests/distributed/test_eplb_execute.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/distributed/test_eplb_execute.py)
  * [tests/distributed/test_eplb_fused_moe_layer.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/distributed/test_eplb_fused_moe_layer.py)
  * [tests/entrypoints/serve/utils/test_api_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/entrypoints/serve/utils/test_api_utils.py)
  * [tests/kernels/moe/test_cutlass_moe.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/kernels/moe/test_cutlass_moe.py)
  * [tests/kernels/moe/test_flashinfer.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/kernels/moe/test_flashinfer.py)
  * [tests/kernels/moe/test_moe.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/kernels/moe/test_moe.py)
  * [tests/kernels/moe/test_unquantized_backend_selection.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/kernels/moe/test_unquantized_backend_selection.py)
  * [tests/models/multimodal/generation/test_common.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/models/multimodal/generation/test_common.py)
  * [tests/models/multimodal/generation/vlm_utils/model_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/models/multimodal/generation/vlm_utils/model_utils.py)
  * [tests/models/registry.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/models/registry.py)
  * [tests/quantization/test_blackwell_moe.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/quantization/test_blackwell_moe.py)
  * [tests/quantization/test_fp8.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/quantization/test_fp8.py)
  * [tests/test_config.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/test_config.py)
  * [tests/test_envs.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/test_envs.py)
  * [tests/transformers_utils/test_dspark_mla_config.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/transformers_utils/test_dspark_mla_config.py)
  * [tests/v1/attention/test_attention_backends.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/attention/test_attention_backends.py)
  * [tests/v1/attention/test_mla_backends.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/attention/test_mla_backends.py)
  * [tests/v1/attention/test_sparse_mla_backends.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/attention/test_sparse_mla_backends.py)
  * [tests/v1/core/test_async_scheduler.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/core/test_async_scheduler.py)
  * [tests/v1/core/test_contiguous_kv_packing.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/core/test_contiguous_kv_packing.py)
  * [tests/v1/core/test_kv_cache_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/core/test_kv_cache_utils.py)
  * [tests/v1/core/test_prefix_caching.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/core/test_prefix_caching.py)
  * [tests/v1/core/test_scheduler.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/core/test_scheduler.py)
  * [tests/v1/core/test_single_type_kv_cache_manager.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/core/test_single_type_kv_cache_manager.py)
  * [tests/v1/core/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/core/utils.py)
  * [tests/v1/distributed/test_async_llm_dp.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/distributed/test_async_llm_dp.py)
  * [tests/v1/engine/test_engine_args.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/engine/test_engine_args.py)
  * [tests/v1/engine/test_engine_core_client.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/engine/test_engine_core_client.py)
  * [tests/v1/kv_connector/unit/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/kv_connector/unit/utils.py)
  * [tests/v1/spec_decode/test_dflash_prepare_inputs.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/spec_decode/test_dflash_prepare_inputs.py)
  * [tests/v1/spec_decode/test_eagle.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/spec_decode/test_eagle.py)
  * [tests/v1/spec_decode/test_eagle_step_kernel.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/spec_decode/test_eagle_step_kernel.py)
  * [tests/v1/spec_decode/test_max_len.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/spec_decode/test_max_len.py)
  * [tests/v1/spec_decode/test_mtp.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/spec_decode/test_mtp.py)
  * [tests/v1/worker/test_gpu_model_runner.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/worker/test_gpu_model_runner.py)
  * [tests/v1/worker/test_kv_block_zeroer.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/worker/test_kv_block_zeroer.py)
  * [vllm/_aiter_ops.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/_aiter_ops.py)
  * [vllm/compilation/backends.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/compilation/backends.py)
  * [vllm/compilation/caching.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/compilation/caching.py)
  * [vllm/compilation/codegen.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/compilation/codegen.py)
  * [vllm/compilation/compiler_interface.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/compilation/compiler_interface.py)
  * [vllm/compilation/counter.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/compilation/counter.py)
  * [vllm/compilation/decorators.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/compilation/decorators.py)
  * [vllm/compilation/monitor.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/compilation/monitor.py)
  * [vllm/compilation/piecewise_backend.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/compilation/piecewise_backend.py)
  * [vllm/compilation/wrapper.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/compilation/wrapper.py)
  * [vllm/config/cache.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/cache.py)
  * [vllm/config/compilation.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/compilation.py)
  * [vllm/config/model.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/model.py)
  * [vllm/config/parallel.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/parallel.py)
  * [vllm/config/scheduler.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/scheduler.py)
  * [vllm/config/speculative.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/speculative.py)
  * [vllm/config/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/utils.py)
  * [vllm/config/vllm.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/vllm.py)
  * [vllm/distributed/elastic_ep/elastic_execute.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/elastic_ep/elastic_execute.py)
  * [vllm/distributed/elastic_ep/elastic_state.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/elastic_ep/elastic_state.py)
  * [vllm/distributed/eplb/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/eplb/__init__.py)
  * [vllm/distributed/eplb/async_worker.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/eplb/async_worker.py)
  * [vllm/distributed/eplb/eplb_communicator.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/eplb/eplb_communicator.py)
  * [vllm/distributed/eplb/eplb_state.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/eplb/eplb_state.py)
  * [vllm/distributed/eplb/eplb_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/eplb/eplb_utils.py)
  * [vllm/distributed/eplb/policy/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/eplb/policy/__init__.py)
  * [vllm/distributed/eplb/policy/abstract.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/eplb/policy/abstract.py)
  * [vllm/distributed/eplb/policy/default.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/eplb/policy/default.py)
  * [vllm/distributed/eplb/rebalance_execute.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/eplb/rebalance_execute.py)
  * [vllm/distributed/kv_transfer/kv_connector/v1/nixl/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/kv_transfer/kv_connector/v1/nixl/__init__.py)
  * [vllm/distributed/kv_transfer/kv_connector/v1/nixl/stats.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/kv_transfer/kv_connector/v1/nixl/stats.py)
  * [vllm/distributed/kv_transfer/kv_connector/v1/nixl/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/kv_transfer/kv_connector/v1/nixl/utils.py)
  * [vllm/distributed/nixl_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/nixl_utils.py)
  * [vllm/distributed/parallel_state.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/parallel_state.py)
  * [vllm/distributed/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/utils.py)
  * [vllm/engine/arg_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/engine/arg_utils.py)
  * [vllm/engine/protocol.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/engine/protocol.py)
  * [vllm/entrypoints/cli/serve.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/cli/serve.py)
  * [vllm/entrypoints/llm.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/llm.py)
  * [vllm/entrypoints/serve/utils/api_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/serve/utils/api_utils.py)
  * [vllm/envs.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/envs.py)
  * [vllm/model_executor/layers/attention/attention.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/attention/attention.py)
  * [vllm/model_executor/layers/attention/mla_attention.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/attention/mla_attention.py)
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
  * [vllm/model_executor/layers/quantization/modelopt.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/modelopt.py)
  * [vllm/model_executor/layers/quantization/mxfp4.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/mxfp4.py)
  * [vllm/model_executor/layers/quantization/quark/quark_moe.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/quark/quark_moe.py)
  * [vllm/model_executor/layers/quantization/utils/flashinfer_fp4_moe.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/utils/flashinfer_fp4_moe.py)
  * [vllm/model_executor/layers/quantization/utils/flashinfer_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/utils/flashinfer_utils.py)
  * [vllm/model_executor/models/config.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/config.py)
  * [vllm/model_executor/models/hunyuan_v1.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/hunyuan_v1.py)
  * [vllm/model_executor/models/hunyuan_vision.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/hunyuan_vision.py)
  * [vllm/model_executor/models/registry.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/registry.py)
  * [vllm/model_executor/warmup/qwen_triton_warmup.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/warmup/qwen_triton_warmup.py)
  * [vllm/transformers_utils/config.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/transformers_utils/config.py)
  * [vllm/transformers_utils/configs/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/transformers_utils/configs/__init__.py)
  * [vllm/transformers_utils/configs/hunyuan_vl.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/transformers_utils/configs/hunyuan_vl.py)
  * [vllm/transformers_utils/model_arch_config_convertor.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/transformers_utils/model_arch_config_convertor.py)
  * [vllm/transformers_utils/processors/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/transformers_utils/processors/__init__.py)
  * [vllm/utils/cpu_triton_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/utils/cpu_triton_utils.py)
  * [vllm/v1/attention/backend.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backend.py)
  * [vllm/v1/attention/backends/fa_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/fa_utils.py)
  * [vllm/v1/attention/backends/flash_attn.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flash_attn.py)
  * [vllm/v1/attention/backends/flashinfer.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flashinfer.py)
  * [vllm/v1/attention/backends/mla/cutlass_mla.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/mla/cutlass_mla.py)
  * [vllm/v1/attention/backends/mla/flashattn_mla.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/mla/flashattn_mla.py)
  * [vllm/v1/attention/backends/mla/flashattn_mla_sparse.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/mla/flashattn_mla_sparse.py)
  * [vllm/v1/attention/backends/mla/flashinfer_mla.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/mla/flashinfer_mla.py)
  * [vllm/v1/attention/backends/mla/flashinfer_mla_sparse.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/mla/flashinfer_mla_sparse.py)
  * [vllm/v1/attention/backends/mla/flashmla.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/mla/flashmla.py)
  * [vllm/v1/attention/backends/mla/flashmla_sparse.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/mla/flashmla_sparse.py)
  * [vllm/v1/attention/backends/mla/tokenspeed_mla.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/mla/tokenspeed_mla.py)
  * [vllm/v1/attention/backends/mla/triton_mla.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/mla/triton_mla.py)
  * [vllm/v1/attention/backends/mla/xpu_mla_sparse.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/mla/xpu_mla_sparse.py)
  * [vllm/v1/attention/backends/registry.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/registry.py)
  * [vllm/v1/attention/backends/rocm_aiter_fa.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/rocm_aiter_fa.py)
  * [vllm/v1/attention/backends/rocm_aiter_unified_attn.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/rocm_aiter_unified_attn.py)
  * [vllm/v1/attention/backends/rocm_attn.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/rocm_attn.py)
  * [vllm/v1/attention/backends/triton_attn.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/triton_attn.py)
  * [vllm/v1/attention/backends/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/utils.py)
  * [vllm/v1/core/block_pool.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/block_pool.py)
  * [vllm/v1/core/kv_cache_coordinator.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/kv_cache_coordinator.py)
  * [vllm/v1/core/kv_cache_manager.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/kv_cache_manager.py)
  * [vllm/v1/core/kv_cache_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/kv_cache_utils.py)
  * [vllm/v1/core/sched/async_scheduler.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/async_scheduler.py)
  * [vllm/v1/core/sched/interface.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/interface.py)
  * [vllm/v1/core/sched/scheduler.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/scheduler.py)
  * [vllm/v1/core/single_type_kv_cache_manager.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/single_type_kv_cache_manager.py)
  * [vllm/v1/engine/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/__init__.py)
  * [vllm/v1/engine/async_llm.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/async_llm.py)
  * [vllm/v1/engine/coordinator.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/coordinator.py)
  * [vllm/v1/engine/core.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py)
  * [vllm/v1/engine/core_client.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core_client.py)
  * [vllm/v1/engine/input_processor.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/input_processor.py)
  * [vllm/v1/engine/llm_engine.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/llm_engine.py)
  * [vllm/v1/engine/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/utils.py)
  * [vllm/v1/kv_cache_interface.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/kv_cache_interface.py)
  * [vllm/v1/request.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/request.py)
  * [vllm/v1/spec_decode/dflash.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/spec_decode/dflash.py)
  * [vllm/v1/spec_decode/draft_model.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/spec_decode/draft_model.py)
  * [vllm/v1/spec_decode/eagle.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/spec_decode/eagle.py)
  * [vllm/v1/spec_decode/llm_base_proposer.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/spec_decode/llm_base_proposer.py)
  * [vllm/v1/spec_decode/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/spec_decode/utils.py)
  * [vllm/v1/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/utils.py)
  * [vllm/v1/worker/cpu/shm.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/cpu/shm.py)
  * [vllm/v1/worker/cpu_model_runner.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/cpu_model_runner.py)
  * [vllm/v1/worker/gpu/spec_decode/gemma4/speculator.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu/spec_decode/gemma4/speculator.py)
  * [vllm/v1/worker/gpu_model_runner.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_model_runner.py)
  * [vllm/v1/worker/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/utils.py)
  * [vllm/vllm_flash_attn/flash_attn_interface.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/vllm_flash_attn/flash_attn_interface.py)

This glossary provides definitions for codebase-specific terms, jargon, and domain concepts used throughout vLLM. It is intended for onboarding engineers to bridge the gap between high-level concepts and their technical implementation.

* * *

## A

### Attention Backend

The specific implementation of the attention mechanism (e.g., FlashAttention, FlashInfer, Triton). vLLM selects a backend based on hardware (CUDA vs. ROCm), model architecture, and optimization settings.

  * **Implementation** : Defined by the `AttentionBackend` interface [vllm/v1/worker/gpu_model_runner.py139](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_model_runner.py#L139-L139)
  * **Registry** : Backends are registered and selected via `AttentionBackendEnum` [vllm/config/model.py55](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/model.py#L55-L55)
  * **V1 Backends** : Includes specialized implementations like `FlashInfer` [vllm/v1/attention/backends/flashinfer.py1](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flashinfer.py#L1-L1) `FlashAttention` [vllm/v1/attention/backends/flash_attn.py1](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flash_attn.py#L1-L1) and `TritonAttention` [vllm/v1/attention/backends/triton_attn.py1](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/triton_attn.py#L1-L1)

Sources: [vllm/config/model.py55](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/model.py#L55-L55) [vllm/v1/worker/gpu_model_runner.py139](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_model_runner.py#L139-L139) [vllm/v1/attention/backends/flashinfer.py1](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flashinfer.py#L1-L1) [vllm/v1/attention/backends/flash_attn.py1](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/flash_attn.py#L1-L1) [vllm/v1/attention/backends/triton_attn.py1](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/attention/backends/triton_attn.py#L1-L1)

## B

### BlockPool

The physical memory management unit for KV caches. It manages a pool of fixed-size memory blocks allocated on the GPU or CPU.

  * **Implementation** : Managed within `KVCacheManager` in the V1 core [vllm/v1/core/sched/scheduler.py38](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/scheduler.py#L38-L38)
  * **V1 Interface** : Individual blocks are represented by `KVCacheBlock` [vllm/v1/core/sched/scheduler.py40](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/scheduler.py#L40-L40)
  * **Configuration** : Governed by `CacheConfig` [vllm/config/vllm.py31](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/vllm.py#L31-L31)

Sources: [vllm/v1/core/sched/scheduler.py38-40](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/scheduler.py#L38-L40) [vllm/config/vllm.py31](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/vllm.py#L31-L31)

## C

### CompilationConfig

A configuration object that controls how `torch.compile` and Dynamo are applied to the model. It defines optimization levels (O0-O3) and custom operator fusions.

  * **Definition** : `CompilationConfig` class [vllm/config/vllm.py32](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/vllm.py#L32-L32)
  * **Optimization Levels** : `OptimizationLevel` enum (O0-O3) determines whether compilation, cudagraphs, and custom fusions are enabled [vllm/config/vllm.py130-143](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/vllm.py#L130-L143)
  * **Modes** : Approaches include `DYNAMO_TRACE_ONCE` and `VLLM_COMPILE` [vllm/config/compilation.py37-51](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/compilation.py#L37-L51)

Sources: [vllm/config/vllm.py32-143](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/vllm.py#L32-L143) [vllm/config/compilation.py37-51](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/compilation.py#L37-L51)

### CUDA Graph

A feature that allows capturing a sequence of CUDA kernels and replaying them with minimal CPU overhead. vLLM uses "Piecewise" and "Full" CUDA graphs to accelerate the decode phase.

  * **Modes** : Defined in `CUDAGraphMode` (NONE, PIECEWISE, FULL) [vllm/config/compilation.py53-64](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/compilation.py#L53-L64)
  * **V1 Core** : Integrated into the scheduler for managing `CUDAGraphStat` [vllm/v1/core/sched/scheduler.py10](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/scheduler.py#L10-L10)
  * **Wrapper** : Handled via `CUDAGraphWrapper` and `BreakableCUDAGraphWrapper` [vllm/v1/worker/gpu_model_runner.py24-29](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_model_runner.py#L24-L29)

Sources: [vllm/config/compilation.py53-64](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/compilation.py#L53-L64) [vllm/v1/core/sched/scheduler.py10](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/scheduler.py#L10-L10) [vllm/v1/worker/gpu_model_runner.py24-29](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_model_runner.py#L24-L29)

## E

### EngineCore

The central orchestration layer in V1 that coordinates the scheduler, executors, and output processing.

  * **Implementation** : Defined in `EngineCore` [vllm/v1/engine/core.py105](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L105-L105)
  * **Outputs** : Produces `EngineCoreOutput` containing generated tokens and metadata [vllm/v1/engine/core.py63](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L63-L63)
  * **Lifecycle** : Manages events via `EngineCoreEventType` [vllm/v1/engine/core.py55](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L55-L55)

Sources: [vllm/v1/engine/core.py55-105](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/engine/core.py#L55-L105)

### EPLB (Expert Placement Load Balancing)

A mechanism to balance the workload across experts in Mixture-of-Experts (MoE) models by distributing experts across data-parallel ranks.

  * **State** : Tracked via `EplbState` [vllm/v1/worker/gpu_model_runner.py43](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_model_runner.py#L43-L43) and `EplbLayerState` [vllm/model_executor/layers/fused_moe/layer.py16](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/layer.py#L16-L16)
  * **Config** : Defined in `EPLBConfig` [vllm/engine/arg_utils.py45](https://github.com/vllm-project/vllm/blob/185cada3/vllm/engine/arg_utils.py#L45-L45)

Sources: [vllm/v1/worker/gpu_model_runner.py43](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_model_runner.py#L43-L43) [vllm/model_executor/layers/fused_moe/layer.py16](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/layer.py#L16-L16) [vllm/engine/arg_utils.py45](https://github.com/vllm-project/vllm/blob/185cada3/vllm/engine/arg_utils.py#L45-L45)

## F

### FusedMoE

An optimized implementation of the Mixture-of-Experts layer that fuses router and GEMM operations to reduce kernel launch overhead.

  * **Factory** : `FusedMoEFactory` function creates the execution pipeline [vllm/model_executor/layers/fused_moe/layer.py88-138](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/layer.py#L88-L138)
  * **Components** : Comprised of `FusedMoERouter`, `RoutedExperts`, and `MoERunner` [vllm/model_executor/layers/fused_moe/layer.py27-35](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/layer.py#L27-L35)
  * **Optimization** : Supports specialized backends like `Fp8MoeBackend` [vllm/model_executor/layers/quantization/modelopt.py28](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/modelopt.py#L28-L28)

Sources: [vllm/model_executor/layers/fused_moe/layer.py27-138](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/fused_moe/layer.py#L27-L138) [vllm/model_executor/layers/quantization/modelopt.py28](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/modelopt.py#L28-L28)

## K

### KV Cache Manager

The subsystem managing the allocation and sharing of Key-Value cache blocks.

  * **Core Logic** : `KVCacheManager` handles logical to physical block mapping [vllm/v1/core/kv_cache_manager.py38](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/kv_cache_manager.py#L38-L38)
  * **Metrics** : Collected via `KVCacheMetricsCollector` [vllm/v1/core/sched/scheduler.py98-102](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/scheduler.py#L98-L102)
  * **Transfer** : `KVConnector` handles remote KV transfers for disaggregated serving (e.g., Prefill/Decode separation) [vllm/v1/core/sched/scheduler.py149-153](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/scheduler.py#L149-L153)

Sources: [vllm/v1/core/sched/scheduler.py38-153](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/scheduler.py#L38-L153) [vllm/v1/core/kv_cache_manager.py38](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/kv_cache_manager.py#L38-L38)

* * *

## Diagrams: Mapping Concepts to Code

### Request Flow: Natural Language to Execution

This diagram bridges the conceptual "Request" to the specific code entities that handle it through the pipeline.

Title: "Request Pipeline Mapping"

Sources: [vllm/v1/request.py64](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/request.py#L64-L64) [vllm/v1/core/sched/scheduler.py73](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/scheduler.py#L73-L73) [vllm/model_executor/models/registry.py72](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/registry.py#L72-L72) [vllm/v1/worker/gpu_model_runner.py1](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_model_runner.py#L1-L1)

### Memory Management: Concepts to Entities

This diagram maps the abstract concept of "KV Memory" to the actual classes and configurations that manage it.

Title: "KV Cache Architecture"

Sources: [vllm/config/vllm.py31](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/vllm.py#L31-L31) [vllm/v1/core/sched/scheduler.py38](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/core/sched/scheduler.py#L38-L38) [vllm/v1/kv_cache_interface.py59-65](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/kv_cache_interface.py#L59-L65)

* * *

## Technical Terms Table

Term| Definition| Code Pointer  
---|---|---  
**TP (Tensor Parallelism)**|  Sharding weights across GPUs within a node.| `ParallelConfig.tensor_parallel_size` [vllm/config/parallel.py46](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/parallel.py#L46-L46)  
**PP (Pipeline Parallelism)**|  Splitting model layers across multiple GPUs.| `ParallelConfig.pipeline_parallel_size` [vllm/config/parallel.py46](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/parallel.py#L46-L46)  
**LoRA (Low-Rank Adaptation)**|  Dynamic adapter loading and management for fine-tuned models.| `LoRAConfig` [vllm/config/vllm.py41](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/vllm.py#L41-L41)  
**VllmConfig**|  Root configuration object containing all sub-configs (Model, Parallel, Cache, etc.).| `VllmConfig` class [vllm/config/vllm.py124](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/vllm.py#L124-L124)  
**MLA (Multi-Latent Attention)**|  Efficient attention mechanism used in DeepSeek models to reduce KV cache size.| `MLAAttention` [vllm/model_executor/layers/attention.py18](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/attention.py#L18-L18)  
**EngineArgs**|  CLI/API initialization arguments parsed from the user.| `vllm/engine/arg_utils.py` [vllm/engine/arg_utils.py1](https://github.com/vllm-project/vllm/blob/185cada3/vllm/engine/arg_utils.py#L1-L1)  
**Transformers Backend**|  Loading models using the Transformers library logic for non-native architectures.| `model_impl="transformers"` [vllm/config/model.py109](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/model.py#L109-L109)  
**QuantizationConfig**|  Base class for various quantization schemes (FP8, AWQ, GPTQ, etc).| `QuantizationConfig` [vllm/model_executor/layers/quantization/base_config.py54](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/base_config.py#L54-L54)  
**GCN Arch**|  Graphics Core Next architecture identifier for AMD GPUs (e.g., `gfx942`).| `_get_gcn_arch` [vllm/platforms/rocm.py199](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/rocm.py#L199-L199)  
**ModelOpt**|  NVIDIA's library for model optimization, integrated for FP8 and NVFP4 support.| `vllm/model_executor/layers/quantization/modelopt.py` [vllm/model_executor/layers/quantization/modelopt.py1](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/modelopt.py#L1-L1)  
  
Sources: [vllm/config/vllm.py41-124](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/vllm.py#L41-L124) [vllm/model_executor/layers/attention.py18](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/attention.py#L18-L18) [vllm/engine/arg_utils.py1](https://github.com/vllm-project/vllm/blob/185cada3/vllm/engine/arg_utils.py#L1-L1) [vllm/config/model.py109](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/model.py#L109-L109) [vllm/model_executor/layers/quantization/modelopt.py1-54](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/layers/quantization/modelopt.py#L1-L54) [vllm/platforms/rocm.py199](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/rocm.py#L199-L199)
