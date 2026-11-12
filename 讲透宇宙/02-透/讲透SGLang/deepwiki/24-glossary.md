> 来源: [https://deepwiki.com/sgl-project/sglang/24-glossary](https://deepwiki.com/sgl-project/sglang/24-glossary)
> DeepWiki sgl-project/sglang | Last indexed: 27 Aug 2026 (94183a)

# Glossary

  Relevant source files 
 - [python/sglang/srt/disaggregation/base/conn.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/base/conn.py)
 - [python/sglang/srt/disaggregation/common/conn.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/common/conn.py)
 - [python/sglang/srt/disaggregation/common/staging_buffer.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/common/staging_buffer.py)
 - [python/sglang/srt/disaggregation/common/staging_handler.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/common/staging_handler.py)
 - [python/sglang/srt/disaggregation/decode.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/decode.py)
 - [python/sglang/srt/disaggregation/decode_kvcache_offload_manager.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/decode_kvcache_offload_manager.py)
 - [python/sglang/srt/disaggregation/fake/conn.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/fake/conn.py)
 - [python/sglang/srt/disaggregation/mooncake/conn.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/mooncake/conn.py)
 - [python/sglang/srt/disaggregation/mori/conn.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/mori/conn.py)
 - [python/sglang/srt/disaggregation/nixl/conn.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/nixl/conn.py)
 - [python/sglang/srt/disaggregation/prefill.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/prefill.py)
 - [python/sglang/srt/disaggregation/utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/utils.py)
 - [python/sglang/srt/entrypoints/http_server.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/http_server.py)
 - [python/sglang/srt/environ.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/environ.py)
 - [python/sglang/srt/managers/cache_controller.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/cache_controller.py)
 - [python/sglang/srt/managers/data_parallel_controller.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/data_parallel_controller.py)
 - [python/sglang/srt/managers/detokenizer_manager.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/detokenizer_manager.py)
 - [python/sglang/srt/managers/io_struct.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/io_struct.py)
 - [python/sglang/srt/managers/multi_tokenizer_mixin.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/multi_tokenizer_mixin.py)
 - [python/sglang/srt/managers/schedule_batch.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py)
 - [python/sglang/srt/managers/schedule_policy.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_policy.py)
 - [python/sglang/srt/managers/scheduler.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py)
 - [python/sglang/srt/managers/scheduler_pp_mixin.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler_pp_mixin.py)
 - [python/sglang/srt/managers/tokenizer_manager.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py)
 - [python/sglang/srt/managers/tp_worker.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tp_worker.py)
 - [python/sglang/srt/mem_cache/base_prefix_cache.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/base_prefix_cache.py)
 - [python/sglang/srt/mem_cache/cache_init_params.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/cache_init_params.py)
 - [python/sglang/srt/mem_cache/chunk_cache.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/chunk_cache.py)
 - [python/sglang/srt/mem_cache/common.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/common.py)
 - [python/sglang/srt/mem_cache/hicache_storage.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/hicache_storage.py)
 - [python/sglang/srt/mem_cache/hiradix_cache.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/hiradix_cache.py)
 - [python/sglang/srt/mem_cache/hybrid_cache/hybrid_cache_controller.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/hybrid_cache/hybrid_cache_controller.py)
 - [python/sglang/srt/mem_cache/hybrid_cache/hybrid_pool_assembler.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/hybrid_cache/hybrid_pool_assembler.py)
 - [python/sglang/srt/mem_cache/kv_cache_builder.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/kv_cache_builder.py)
 - [python/sglang/srt/mem_cache/mamba_radix_cache.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/mamba_radix_cache.py)
 - [python/sglang/srt/mem_cache/memory_pool_host.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/memory_pool_host.py)
 - [python/sglang/srt/mem_cache/pool_host/base.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/pool_host/base.py)
 - [python/sglang/srt/mem_cache/pool_host/mha.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/pool_host/mha.py)
 - [python/sglang/srt/mem_cache/pool_host/mla.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/pool_host/mla.py)
 - [python/sglang/srt/mem_cache/radix_cache.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/radix_cache.py)
 - [python/sglang/srt/mem_cache/radix_cache_cpp.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/radix_cache_cpp.py)
 - [python/sglang/srt/mem_cache/storage/lmcache/lmc_radix_cache.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/storage/lmcache/lmc_radix_cache.py)
 - [python/sglang/srt/mem_cache/storage/mooncake_store/mooncake_store.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/storage/mooncake_store/mooncake_store.py)
 - [python/sglang/srt/mem_cache/swa_radix_cache.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/swa_radix_cache.py)
 - [python/sglang/srt/mem_cache/unified_radix_cache.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/unified_radix_cache.py)
 - [python/sglang/srt/model_executor/model_runner.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py)
 - [python/sglang/srt/multiplex/multiplexing_mixin.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multiplex/multiplexing_mixin.py)
 - [python/sglang/srt/server_args.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py)
 - [test/registered/amd/disaggregation/test_mori_transfer_engine_e2e.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/amd/disaggregation/test_mori_transfer_engine_e2e.py)
 - [test/registered/disaggregation/test_disaggregation_different_tp.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/disaggregation/test_disaggregation_different_tp.py)
 - [test/registered/unit/disaggregation/test_nixl_backend_basic.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/disaggregation/test_nixl_backend_basic.py)
 - [test/registered/unit/disaggregation/test_receiver_connection_pool.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/disaggregation/test_receiver_connection_pool.py)
 - [test/registered/unit/managers/test_prefill_adder.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/managers/test_prefill_adder.py)
 - [test/registered/unit/mem_cache/test_decode_retraction_backup.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/mem_cache/test_decode_retraction_backup.py)
 - [test/registered/unit/mem_cache/test_hicache_dcp_host_pool.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/mem_cache/test_hicache_dcp_host_pool.py)
 - [test/registered/unit/mem_cache/test_hicache_staged_write_back_dispatch.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/mem_cache/test_hicache_staged_write_back_dispatch.py)
 - [test/registered/unit/mem_cache/test_mem_pool_host.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/mem_cache/test_mem_pool_host.py)
 - [test/registered/unit/mem_cache/test_minimax_sparse_pool_host_unit.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/mem_cache/test_minimax_sparse_pool_host_unit.py)
 - [test/registered/unit/mem_cache/test_unified_radix_cache_unittest.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/mem_cache/test_unified_radix_cache_unittest.py)
 
  This page provides definitions and technical details for SGLang-specific terminology, architectural components, and domain concepts. It serves as a reference for onboarding engineers to understand the jargon and implementation patterns used throughout the codebase.

 
## Core System Entities

 The following diagram bridges the gap between natural language concepts and the specific classes/files that implement them.

 
### System Entity Mapping

 
```

```

 **Sources:** [python/sglang/srt/managers/tokenizer_manager.py14-46](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L14-L46) [python/sglang/srt/managers/scheduler.py14-43](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L14-L43) [python/sglang/srt/managers/schedule_batch.py34-46](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L34-L46) [python/sglang/srt/managers/io_struct.py83-106](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/io_struct.py#L83-L106)

 
---

 
## Glossary of Terms

 
### A

 
 - **Adaptive Speculative Decoding**: An enhancement to speculative decoding where the draft length or strategy is adjusted dynamically based on acceptance rates. Integrated via `SpeculativeAlgorithm` [python/sglang/srt/model_executor/model_runner.py170-182](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L170-L182) For details, see [Glossary: Runtime, Scheduling, and Memory Terms](https://deepwiki.com/sgl-project/sglang/24.1-glossary:-runtime-scheduling-and-memory-terms).
 
 
### B

 
 - **Breakable CUDA Graph**: A mechanism to handle CUDA Graph execution that can be interrupted or "broken" to accommodate operations not supported inside a graph. Referenced in `ModelRunner` [python/sglang/srt/model_executor/model_runner.py93-95](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L93-L95) For details, see [Glossary: Runtime, Scheduling, and Memory Terms](https://deepwiki.com/sgl-project/sglang/24.1-glossary:-runtime-scheduling-and-memory-terms).
 
 
### C

 
 - **Checkpoint Engine**: A system for managing model weights and states, facilitating efficient loading and saving of model checkpoints. Integrated into the scheduler for weight updates and snapshots [python/sglang/srt/managers/scheduler.py182](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L182-L182) For details, see [Glossary: Runtime, Scheduling, and Memory Terms](https://deepwiki.com/sgl-project/sglang/24.1-glossary:-runtime-scheduling-and-memory-terms).
 - **CUDA Graph**: An optimization technique where a sequence of CUDA kernels is captured once and replayed to reduce CPU launch overhead. SGLang uses `capture_cuda_graphs` and specialized variants for prefill and decode phases [python/sglang/srt/model_executor/model_runner.py116-120](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L116-L120) For details, see [Glossary: Runtime, Scheduling, and Memory Terms](https://deepwiki.com/sgl-project/sglang/24.1-glossary:-runtime-scheduling-and-memory-terms).
 
 
### D

 
 - **Disaggregation (P/D Disagg)**: The architectural split between Prefill (encoding) and Decode nodes. Prefill nodes compute the initial KV cache and transfer it to Decode nodes via backends like `mooncake`, `nixl`, or `mori` [python/sglang/srt/server_args.py56-58](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L56-L58) [python/sglang/srt/managers/scheduler.py74-96](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L74-L96) For details, see [Glossary: Distributed, Quantization, Multimodal, and Gateway Terms](https://deepwiki.com/sgl-project/sglang/24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms).
 - **DLLM (Diffusion LLM)**: Support for discrete diffusion models (e.g., LLaDA). Managed via `DllmConfig` and `SchedulerDllmMixin` [python/sglang/srt/managers/scheduler.py100](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L100-L100) [python/sglang/srt/managers/schedule_batch.py3](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L3-L3) For details, see [Glossary: Runtime, Scheduling, and Memory Terms](https://deepwiki.com/sgl-project/sglang/24.1-glossary:-runtime-scheduling-and-memory-terms).
 
 
### E

 
 - **EAGLE**: A speculative decoding algorithm using a draft model to predict future tokens in a tree structure [python/sglang/srt/model_executor/model_runner.py182](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L182-L182) [python/sglang/srt/managers/schedule_batch.py154](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L154-L154) For details, see [Glossary: Runtime, Scheduling, and Memory Terms](https://deepwiki.com/sgl-project/sglang/24.1-glossary:-runtime-scheduling-and-memory-terms).
 - **Elastic EP**: A dynamic expert parallelism strategy that allows experts to be re-mapped or backed up across ranks to handle load imbalance. Managed by `ElasticEPStateManager` [python/sglang/srt/model_executor/model_runner.py42-52](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L42-L52) For details, see [Glossary: Distributed, Quantization, Multimodal, and Gateway Terms](https://deepwiki.com/sgl-project/sglang/24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms).
 - **EPD Disaggregation**: A specialized disaggregation mode for Vision-Language Models (VLMs) separating Encoder, Prefill, and Decode stages [python/sglang/srt/managers/scheduler.py74-87](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L74-L87) [python/sglang/srt/managers/tokenizer_manager.py183-199](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L183-L199) For details, see [Glossary: Distributed, Quantization, Multimodal, and Gateway Terms](https://deepwiki.com/sgl-project/sglang/24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms).
 - **EPLB (Expert Load Balancing)**: A manager for balancing MoE expert distribution across ranks to prevent hotspots [python/sglang/srt/model_executor/model_runner.py55-71](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L55-L71) For details, see [Glossary: Distributed, Quantization, Multimodal, and Gateway Terms](https://deepwiki.com/sgl-project/sglang/24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms).
 - **ExpertPack**: A unified format (`SGLANG-EXPERTPACK-v1`) for sharded expert weights, often used for DeepSeek or MoE models [python/sglang/srt/server_args.py127-132](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L127-L132)
 
 
### F

 
 - **Forward Hooks**: Custom functions registered to run before or after the model's forward pass, often used for debugging or tensor dumping. Managed via `maybe_register_debug_tensor_dump_hook` [python/sglang/srt/model_executor/model_runner.py138](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L138-L138) For details, see [Glossary: Runtime, Scheduling, and Memory Terms](https://deepwiki.com/sgl-project/sglang/24.1-glossary:-runtime-scheduling-and-memory-terms).
 - **ForwardBatch**: The low-level GPU tensor data structure used by `ModelRunner` [python/sglang/srt/managers/schedule_batch.py43-52](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L43-L52) [python/sglang/srt/model_executor/forward_batch_info.py97-99](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/forward_batch_info.py#L97-L99) For details, see [Glossary: Runtime, Scheduling, and Memory Terms](https://deepwiki.com/sgl-project/sglang/24.1-glossary:-runtime-scheduling-and-memory-terms).
 
 
### H

 
 - **HiCache Design**: The multi-tier storage system (device/host/storage) for the Radix Cache. Includes `HiRadixCache` and `HiCacheController` [python/sglang/srt/mem_cache/unified_radix_cache.py42-44](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/unified_radix_cache.py#L42-L44) For details, see [Glossary: Runtime, Scheduling, and Memory Terms](https://deepwiki.com/sgl-project/sglang/24.1-glossary:-runtime-scheduling-and-memory-terms).
 - **HiSparse**: A high-performance sparse attention or memory management coordinator for handling large-scale sparse operations. Managed by `HiSparseCoordinator` [python/sglang/srt/managers/scheduler.py112](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L112-L112) For details, see [Glossary: Runtime, Scheduling, and Memory Terms](https://deepwiki.com/sgl-project/sglang/24.1-glossary:-runtime-scheduling-and-memory-terms).
 
 
### K

 
 - **KV Events**: A synchronization mechanism used in multi-tier KV cache systems (HiCache) to track the readiness of KV cache transfers between host and device. Defined in [python/sglang/srt/disaggregation/kv_events.py21-25](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/kv_events.py#L21-L25) For details, see [Glossary: Runtime, Scheduling, and Memory Terms](https://deepwiki.com/sgl-project/sglang/24.1-glossary:-runtime-scheduling-and-memory-terms).
 - **KV-event-driven routing**: An experimental routing strategy used in `sgl-router` that uses KV events to make cache-aware routing decisions. For details, see [Glossary: Distributed, Quantization, Multimodal, and Gateway Terms](https://deepwiki.com/sgl-project/sglang/24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms).
 
 
### L

 
 - **llm-d**: A Kubernetes-native fleet orchestration system for prefix-aware routing and distributed KV-cache management at scale. For details, see [Glossary: Distributed, Quantization, Multimodal, and Gateway Terms](https://deepwiki.com/sgl-project/sglang/24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms).
 
 
### M

 
 - **MLA (Multi-head Latent Attention)**: An attention architecture used in DeepSeek models to compress KV cache [python/sglang/srt/model_executor/model_runner.py83-84](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L83-L84) For details, see [Glossary: Distributed, Quantization, Multimodal, and Gateway Terms](https://deepwiki.com/sgl-project/sglang/24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms).
 - **MmFamilyProcessor**: Part of the `sglang-mm` Rust-accelerated multimodal preprocessing pipeline [python/sglang/srt/managers/multimodal_processor.py88](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/multimodal_processor.py#L88-L88) For details, see [Glossary: Distributed, Quantization, Multimodal, and Gateway Terms](https://deepwiki.com/sgl-project/sglang/24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms).
 
 
### O

 
 - **Object Storage Loading**: Support for loading model weights directly from object storage (e.g., S3, GCS) via `runai_streamer` or `ObjectStorageModel` [python/sglang/srt/server_args.py141](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L141-L141) [python/sglang/srt/server_args.py108](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L108-L108) For details, see [Glossary: Distributed, Quantization, Multimodal, and Gateway Terms](https://deepwiki.com/sgl-project/sglang/24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms).
 
 
### P

 
 - **PD-Multiplexing**: A mode where a single instance can dynamically switch between Prefill and Decode roles or handle both simultaneously to maximize utilization. Integrated via `ForwardMode` [python/sglang/srt/model_executor/forward_batch_info.py125](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/forward_batch_info.py#L125-L125) For details, see [Glossary: Distributed, Quantization, Multimodal, and Gateway Terms](https://deepwiki.com/sgl-project/sglang/24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms).
 - **Piecewise CUDA Graph**: A strategy that breaks the model execution into multiple smaller CUDA graphs ("pieces") to allow for dynamic batching or memory management between pieces. For details, see [Glossary: Runtime, Scheduling, and Memory Terms](https://deepwiki.com/sgl-project/sglang/24.1-glossary:-runtime-scheduling-and-memory-terms).
 - **Post-Training Integration**: Framework integrations (e.g., verl, Miles, slime, AReaL, ROLL) that allow SGLang to be used as an inference engine during RL and post-training loops. For details, see [Glossary: Distributed, Quantization, Multimodal, and Gateway Terms](https://deepwiki.com/sgl-project/sglang/24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms).
 - **Production Metrics**: Standardized observability metrics such as TTFT (Time to First Token), TPOT (Time Per Output Token), and cache hit rates [python/sglang/srt/managers/tokenizer_manager.py114-118](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L114-L118) For details, see [Glossary: Distributed, Quantization, Multimodal, and Gateway Terms](https://deepwiki.com/sgl-project/sglang/24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms).
 
 
### Q

 
 - **Quantized KV Cache**: The practice of storing Key and Value tensors in lower precision (e.g., FP8, FP4) to reduce memory footprint [python/sglang/srt/server_args.py151-187](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L151-L187) For details, see [Glossary: Distributed, Quantization, Multimodal, and Gateway Terms](https://deepwiki.com/sgl-project/sglang/24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms).
 
 
### R

 
 - **R-Fork (Remote Fork)**: A mechanism for loading model weights from a remote instance or URI, often used in distributed or serverless environments. Supported via `ObjectStorageModel` and `remote` load formats [python/sglang/srt/server_args.py118-142](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L118-L142) For details, see [Glossary: Runtime, Scheduling, and Memory Terms](https://deepwiki.com/sgl-project/sglang/24.1-glossary:-runtime-scheduling-and-memory-terms).
 - **RadixCache**: A hierarchical KV cache management system using a radix tree for prefix sharing [python/sglang/srt/managers/schedule_batch.py121](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L121-L121) For details, see [Glossary: Runtime, Scheduling, and Memory Terms](https://deepwiki.com/sgl-project/sglang/24.1-glossary:-runtime-scheduling-and-memory-terms).
 - **Runtime Attach/Detach**: The ability to dynamically add or remove storage backends (like HiCache tiers) to a running engine instance [python/sglang/srt/managers/scheduler.py118-130](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L118-L130) For details, see [Glossary: Distributed, Quantization, Multimodal, and Gateway Terms](https://deepwiki.com/sgl-project/sglang/24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms).
 
 
### S

 
 - **sgl-router (experimental)**: A slim, Rust-based high-performance router designed for KV-aware routing and PD disaggregation support [python/sglang/srt/managers/tokenizer_manager.py199](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L199-L199) For details, see [Glossary: Distributed, Quantization, Multimodal, and Gateway Terms](https://deepwiki.com/sgl-project/sglang/24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms).
 - **sglang.kernels**: A unified kernel namespace introduced to consolidate custom operations [python/sglang/srt/server_args.py35](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L35-L35) For details, see [Glossary: Distributed, Quantization, Multimodal, and Gateway Terms](https://deepwiki.com/sgl-project/sglang/24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms).
 - **sglang-mm**: A Rust-based multimodal preprocessor for efficient image/video handling [python/sglang/srt/managers/multimodal_processor.py88](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/multimodal_processor.py#L88-L88) For details, see [Glossary: Distributed, Quantization, Multimodal, and Gateway Terms](https://deepwiki.com/sgl-project/sglang/24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms).
 
 
---

 
## Memory Management Concepts

 SGLang uses a multi-tier memory system to manage GPU and Host resources.

 
### Memory Pool Hierarchy

 
```

```

 **Sources:** [python/sglang/srt/managers/schedule_batch.py102-121](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L102-L121) [python/sglang/srt/model_executor/model_runner.py88-92](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L88-L92)

 
### Detailed Definitions:

 
 - **`ReqToTokenPool`**: A memory pool that maps a request to its token locations in the physical KV cache [python/sglang/srt/model_executor/model_runner.py92](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L92-L92) For details, see [Glossary: Runtime, Scheduling, and Memory Terms](https://deepwiki.com/sgl-project/sglang/24.1-glossary:-runtime-scheduling-and-memory-terms).
 - **`HiSparse`**: Provides coordination for sparse memory structures, reducing the effective size of the KV cache for long sequences [python/sglang/srt/managers/scheduler.py112](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L112-L112) For details, see [Glossary: Runtime, Scheduling, and Memory Terms](https://deepwiki.com/sgl-project/sglang/24.1-glossary:-runtime-scheduling-and-memory-terms).
 
 
---

 
## Request Lifecycle Data Flow

 
| Data Structure | Managed By | Purpose |
|---|---|---|
| GenerateReqInput | TokenizerManager | User input and sampling parameters python/sglang/srt/managers/io_struct.py168 |
| Req | Scheduler | Tracking lifecycle, status, and KV indices python/sglang/srt/managers/schedule_batch.py204 |
| ScheduleBatch | Scheduler | Group of Req objects for one execution step python/sglang/srt/managers/schedule_batch.py205 |
| ForwardBatch | ModelRunner | Flattened tensors for GPU kernels python/sglang/srt/model_executor/forward_batch_info.py97-99 |

 **Sources:** [python/sglang/srt/managers/schedule_batch.py43-52](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py#L43-L52) [python/sglang/srt/managers/io_struct.py83-106](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/io_struct.py#L83-L106)

 
---

 
## Hardware and Backend Jargon

 
 - **TP (Tensor Parallelism)**: Sharding weights within a node [python/sglang/srt/managers/scheduler.py98](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L98-L98) For details, see [Glossary: Distributed, Quantization, Multimodal, and Gateway Terms](https://deepwiki.com/sgl-project/sglang/24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms).
 - **PP (Pipeline Parallelism)**: Sharding layers across GPUs [python/sglang/srt/managers/scheduler.py97](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py#L97-L97) For details, see [Glossary: Distributed, Quantization, Multimodal, and Gateway Terms](https://deepwiki.com/sgl-project/sglang/24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms).
 - **EP (Expert Parallelism)**: Sharding MoE experts. SGLang supports various dispatch backends like `DeepEP`, `Mooncake`, and `NIXL` [python/sglang/srt/model_executor/model_runner.py143-147](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L143-L147) For details, see [Glossary: Distributed, Quantization, Multimodal, and Gateway Terms](https://deepwiki.com/sgl-project/sglang/24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms).
 - **FlashInfer**: Primary high-performance attention/sampling backend [python/sglang/srt/server_args.py116](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L116-L116) [python/sglang/srt/server_args.py203](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L203-L203) For details, see [Glossary: Distributed, Quantization, Multimodal, and Gateway Terms](https://deepwiki.com/sgl-project/sglang/24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms).
 - **Triton**: Language for custom kernels (MoE, Attention) [python/sglang/srt/server_args.py192](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L192-L192) For details, see [Glossary: Distributed, Quantization, Multimodal, and Gateway Terms](https://deepwiki.com/sgl-project/sglang/24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms).
 
 For more detailed information, see the following child pages:

 
 - [Glossary: Runtime, Scheduling, and Memory Terms](https://deepwiki.com/sgl-project/sglang/24.1-glossary:-runtime-scheduling-and-memory-terms)
 - [Glossary: Distributed, Quantization, Multimodal, and Gateway Terms](https://deepwiki.com/sgl-project/sglang/24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms)
