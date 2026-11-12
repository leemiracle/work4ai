> 来源: [https://deepwiki.com/sgl-project/sglang/5-memory-management-and-kv-cache](https://deepwiki.com/sgl-project/sglang/5-memory-management-and-kv-cache)
> DeepWiki sgl-project/sglang | Last indexed: 27 Aug 2026 (94183a)

# Memory Management and KV Cache

  Relevant source files 
 - [python/sglang/srt/disaggregation/decode_hicache_mixin.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/decode_hicache_mixin.py)
 - [python/sglang/srt/disaggregation/decode_kvcache_offload_manager.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/decode_kvcache_offload_manager.py)
 - [python/sglang/srt/hardware_backend/npu/allocator_npu.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/hardware_backend/npu/allocator_npu.py)
 - [python/sglang/srt/managers/cache_controller.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/cache_controller.py)
 - [python/sglang/srt/managers/hisparse_coordinator.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/hisparse_coordinator.py)
 - [python/sglang/srt/managers/schedule_policy.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_policy.py)
 - [python/sglang/srt/mem_cache/allocator/__init__.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/allocator/__init__.py)
 - [python/sglang/srt/mem_cache/allocator/base.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/allocator/base.py)
 - [python/sglang/srt/mem_cache/allocator/hisparse.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/allocator/hisparse.py)
 - [python/sglang/srt/mem_cache/allocator/paged.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/allocator/paged.py)
 - [python/sglang/srt/mem_cache/allocator/token.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/allocator/token.py)
 - [python/sglang/srt/mem_cache/base_prefix_cache.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/base_prefix_cache.py)
 - [python/sglang/srt/mem_cache/cache_init_params.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/cache_init_params.py)
 - [python/sglang/srt/mem_cache/chunk_cache.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/chunk_cache.py)
 - [python/sglang/srt/mem_cache/hicache_storage.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/hicache_storage.py)
 - [python/sglang/srt/mem_cache/hiradix_cache.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/hiradix_cache.py)
 - [python/sglang/srt/mem_cache/hisparse_memory_pool.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/hisparse_memory_pool.py)
 - [python/sglang/srt/mem_cache/hybrid_cache/hybrid_cache_controller.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/hybrid_cache/hybrid_cache_controller.py)
 - [python/sglang/srt/mem_cache/hybrid_cache/hybrid_pool_assembler.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/hybrid_cache/hybrid_pool_assembler.py)
 - [python/sglang/srt/mem_cache/kv_cache_builder.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/kv_cache_builder.py)
 - [python/sglang/srt/mem_cache/mamba_radix_cache.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/mamba_radix_cache.py)
 - [python/sglang/srt/mem_cache/memory_pool.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/memory_pool.py)
 - [python/sglang/srt/mem_cache/memory_pool_host.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/memory_pool_host.py)
 - [python/sglang/srt/mem_cache/pool_host/base.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/pool_host/base.py)
 - [python/sglang/srt/mem_cache/pool_host/mha.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/pool_host/mha.py)
 - [python/sglang/srt/mem_cache/pool_host/mla.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/pool_host/mla.py)
 - [python/sglang/srt/mem_cache/radix_cache.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/radix_cache.py)
 - [python/sglang/srt/mem_cache/radix_cache_cpp.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/radix_cache_cpp.py)
 - [python/sglang/srt/mem_cache/storage/lmcache/lmc_radix_cache.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/storage/lmcache/lmc_radix_cache.py)
 - [python/sglang/srt/mem_cache/storage/mooncake_store/mooncake_store.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/storage/mooncake_store/mooncake_store.py)
 - [python/sglang/srt/mem_cache/swa_memory_pool.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/swa_memory_pool.py)
 - [python/sglang/srt/mem_cache/swa_radix_cache.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/swa_radix_cache.py)
 - [python/sglang/srt/mem_cache/unified_radix_cache.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/unified_radix_cache.py)
 - [test/registered/disaggregation/test_disaggregation_decode_radix_cache.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/disaggregation/test_disaggregation_decode_radix_cache.py)
 - [test/registered/disaggregation/test_disaggregation_decode_radix_cache_swa.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/disaggregation/test_disaggregation_decode_radix_cache_swa.py)
 - [test/registered/radix_cache/test_mamba2_extra_buffer_kl.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/radix_cache/test_mamba2_extra_buffer_kl.py)
 - [test/registered/unit/disaggregation/test_decode_queue_cleanup.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/disaggregation/test_decode_queue_cleanup.py)
 - [test/registered/unit/managers/test_hisparse_unit.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/managers/test_hisparse_unit.py)
 - [test/registered/unit/managers/test_prefill_adder.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/managers/test_prefill_adder.py)
 - [test/registered/unit/mem_cache/test_decode_retraction_backup.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/mem_cache/test_decode_retraction_backup.py)
 - [test/registered/unit/mem_cache/test_hicache_dcp_host_pool.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/mem_cache/test_hicache_dcp_host_pool.py)
 - [test/registered/unit/mem_cache/test_hicache_staged_write_back_dispatch.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/mem_cache/test_hicache_staged_write_back_dispatch.py)
 - [test/registered/unit/mem_cache/test_hisparse_allocator.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/mem_cache/test_hisparse_allocator.py)
 - [test/registered/unit/mem_cache/test_mem_pool_host.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/mem_cache/test_mem_pool_host.py)
 - [test/registered/unit/mem_cache/test_minimax_sparse_pool_host_unit.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/mem_cache/test_minimax_sparse_pool_host_unit.py)
 - [test/registered/unit/mem_cache/test_paged_free_segment.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/mem_cache/test_paged_free_segment.py)
 - [test/registered/unit/mem_cache/test_swa_cpu_copy_filter.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/mem_cache/test_swa_cpu_copy_filter.py)
 - [test/registered/unit/mem_cache/test_unified_radix_cache_unittest.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/mem_cache/test_unified_radix_cache_unittest.py)
 
  This page documents SGLang's memory management system and KV (Key-Value) cache architecture. It covers the hierarchical caching subsystem, memory pools, prefix sharing mechanisms, and their integration with the scheduler and model execution pipeline.

 
## Overview

 SGLang implements a sophisticated **three-tier hierarchical caching system** designed to maximize GPU memory efficiency while minimizing recomputation. The system is built around two core abstractions:

 
 - **Memory Pools**: Manage physical memory allocation at request and token levels. [python/sglang/srt/mem_cache/memory_pool.py15-21](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/memory_pool.py#L15-L21)
 - **Prefix Caches**: Enable intelligent sharing of computed KV cache across requests with common prefixes using a Radix Tree structure. [python/sglang/srt/mem_cache/radix_cache.py20-22](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/radix_cache.py#L20-L22)
 
 The memory hierarchy spans:

 
 - **L1 (Device)**: GPU VRAM for actively executing requests, managed by various `TokenToKVPool` implementations. [python/sglang/srt/mem_cache/memory_pool.py19-20](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/memory_pool.py#L19-L20)
 - **L2 (Host)**: CPU RAM for secondary cache and backup, managed by host-side pools like `HostKVCache` and `LogicalHostPool`. [python/sglang/srt/mem_cache/memory_pool_host.py37-70](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/memory_pool_host.py#L37-L70)
 - **L3 (Storage)**: Persistent or distributed storage backends (Mooncake, HF3FS, LMCache, NIXL) for cold or large KV cache data. [python/sglang/srt/mem_cache/hiradix_cache.py175-183](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/hiradix_cache.py#L175-L183)
 
 These layers work in concert within SGLang's runtime to ensure efficient KV cache storage, retrieval, and eviction based on request needs, prefix sharing, and hardware capabilities.

 **Sources**: [python/sglang/srt/mem_cache/memory_pool.py1-21](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/memory_pool.py#L1-L21) [python/sglang/srt/mem_cache/radix_cache.py1-22](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/radix_cache.py#L1-L22) [python/sglang/srt/mem_cache/hiradix_cache.py76-183](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/hiradix_cache.py#L76-L183) [python/sglang/srt/mem_cache/memory_pool_host.py37-75](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/memory_pool_host.py#L37-L75)

 
---

 
## Memory Pool Architecture

 The memory pool system in SGLang separates logical requests from physical KV cache storage through a multi-level pooling design:

 
 - **ReqToTokenPool**: Maps each incoming request to its allocation of token locations in the global pool. [python/sglang/srt/mem_cache/memory_pool.py18](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/memory_pool.py#L18-L18)
 - **TokenToKVPoolAllocator**: Manages the indices to KV cache data, handling allocation strategies. [python/sglang/srt/mem_cache/memory_pool.py19](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/memory_pool.py#L19-L19)
 - **KVCache**: The actual physical buffer holding the KV data. [python/sglang/srt/mem_cache/memory_pool.py20](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/memory_pool.py#L20-L20)
 
 
### Diagram: Memory Pools and Relationships in SGLang

 
```

```

 SGLang supports specialized pool variants:

 
 - **MHATokenToKVPool**: Standard multi-head attention. [python/sglang/srt/mem_cache/memory_pool.py86-88](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/memory_pool.py#L86-L88)
 - **MLATokenToKVPool**: Multi-head latent attention (e.g., DeepSeek). [python/sglang/srt/mem_cache/memory_pool.py101-105](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/memory_pool.py#L101-L105)
 - **DSATokenToKVPool**: Native Structured Attention (NSA/DSA). [python/sglang/srt/mem_cache/hiradix_cache.py95-97](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/hiradix_cache.py#L95-L97)
 - **DeepSeekV4HiSparseTokenToKVPoolAllocator**: Supports the sparse KV cache architecture of DeepSeek-V4. [python/sglang/srt/managers/schedule_policy.py46-48](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_policy.py#L46-L48)
 - **MambaSlotAllocator**: Specialized for Mamba linear states. [python/sglang/srt/mem_cache/memory_pool.py60](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/memory_pool.py#L60-L60)
 
 For details, see [Memory Pools and Token-to-KV Mapping](https://deepwiki.com/sgl-project/sglang/5.1-memory-pools-and-token-to-kv-mapping).

 **Sources**: [python/sglang/srt/mem_cache/memory_pool.py14-130](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/memory_pool.py#L14-L130) [python/sglang/srt/mem_cache/hiradix_cache.py84-116](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/hiradix_cache.py#L84-L116) [python/sglang/srt/managers/schedule_policy.py46-62](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_policy.py#L46-L62)

 
---

 
## RadixCache and Prefix Sharing

 To maximize cache reuse, SGLang implements prefix sharing using a Radix Tree structure. [python/sglang/srt/mem_cache/radix_cache.py20-22](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/radix_cache.py#L20-L22)

 
### Key Components:

 
 - **UnifiedRadixCache**: The primary class for managing hybrid cache components (FULL, MAMBA, SWA). [python/sglang/srt/mem_cache/unified_radix_cache.py148-178](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/unified_radix_cache.py#L148-L178)
 - **RadixKey**: Represents a sequence of tokens used for matching in the tree, supporting bigrams and page alignment. [python/sglang/srt/mem_cache/radix_cache.py59-63](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/radix_cache.py#L59-L63)
 - **UnifiedTreeNode**: A node in the unified tree that can hold multiple component values (e.g., `value` for FULL, `mamba_value`, `swa_uuid`). [python/sglang/srt/mem_cache/unified_radix_cache.py78-79](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/unified_radix_cache.py#L78-L79) [python/sglang/srt/mem_cache/mamba_radix_cache.py74-85](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/mamba_radix_cache.py#L74-L85)
 
 
### Diagram: UnifiedRadixCache Node and Component Space

 
```

```

 
### Matching and Eviction

 
 - **MatchPrefixParams**: Encapsulates the key and requirements for a tree search. [python/sglang/srt/mem_cache/base_prefix_cache.py26](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/base_prefix_cache.py#L26-L26)
 - **match_prefix_for_req**: A utility function used by the scheduler to find the longest cached prefix for a `Req` object. [python/sglang/srt/managers/schedule_policy.py138-145](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_policy.py#L138-L145)
 - **LRUList**: Manages the eviction order for cache nodes. [python/sglang/srt/mem_cache/mamba_radix_cache.py182-185](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/mamba_radix_cache.py#L182-L185)
 
 For details, see [RadixCache and Prefix Sharing](https://deepwiki.com/sgl-project/sglang/5.2-radixcache-and-prefix-sharing).

 **Sources**: [python/sglang/srt/mem_cache/unified_radix_cache.py148-205](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/unified_radix_cache.py#L148-L205) [python/sglang/srt/mem_cache/radix_cache.py59-154](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/radix_cache.py#L59-L154) [python/sglang/srt/managers/schedule_policy.py138-167](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_policy.py#L138-L167)

 
---

 
## HiCache Multi-Tier Storage

 The **HiCache** system extends the KV cache into a multi-tier hierarchy spanning GPU device memory, host CPU memory, and remote/persistent storage.

 
### Tiers and Control

 
 - **HiRadixCache**: A hierarchical implementation of `RadixCache` that tracks data across `StorageMedium` tiers. [python/sglang/srt/mem_cache/hiradix_cache.py81-83](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/hiradix_cache.py#L81-L83)
 - **HiCacheController**: Coordinates asynchronous transfers between L1, L2, and L3. [python/sglang/srt/managers/cache_controller.py172-188](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/cache_controller.py#L172-L188)
 - **Host Pools**: Specialized CPU memory pools like `MLATokenToKVPoolHost` and `DeepSeekV4PagedHostPool` provide the L2 backing. [python/sglang/srt/mem_cache/memory_pool_host.py174-200](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/memory_pool_host.py#L174-L200)
 - **HiSparse**: Support for sparse attention models (DeepSeek-V4) using `HiSparseHostPoolMixin`. [python/sglang/srt/mem_cache/memory_pool_host.py174](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/memory_pool_host.py#L174-L174)
 
 For details, see [HiCache Multi-Tier Storage](https://deepwiki.com/sgl-project/sglang/5.3-hicache-multi-tier-storage).

 **Sources**: [python/sglang/srt/mem_cache/hiradix_cache.py81-188](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/hiradix_cache.py#L81-L188) [python/sglang/srt/managers/cache_controller.py172-188](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/cache_controller.py#L172-L188) [python/sglang/srt/mem_cache/memory_pool_host.py174-217](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/memory_pool_host.py#L174-L217)

 
---

 
## Storage Backends and Transfer Optimization

 SGLang provides abstractions to integrate with various distributed and local storage backends for L3 caching.

 
 - **Storage Backends**: Integrated backends include `MooncakeStore` for RDMA-based distributed caching and `LMCache` for generic sharing. [python/sglang/srt/mem_cache/storage/mooncake_store/mooncake_store.py93-107](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/storage/mooncake_store/mooncake_store.py#L93-L107) [python/sglang/srt/mem_cache/storage/lmcache/lmc_radix_cache.py1-5](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/storage/lmcache/lmc_radix_cache.py#L1-L5)
 - **CacheOperation**: Encapsulates a unit of transfer (host/device indices) managed by the controller. [python/sglang/srt/managers/cache_controller.py102-124](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/cache_controller.py#L102-L124)
 - **Async Transfers**: Uses `PoolTransfer` and specialized JIT kernels to perform low-overhead IO. [python/sglang/srt/managers/cache_controller.py132-152](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/cache_controller.py#L132-L152) [python/sglang/srt/mem_cache/memory_pool_host.py9-15](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/memory_pool_host.py#L9-L15)
 
 For details, see [Storage Backends and Transfer Optimization](https://deepwiki.com/sgl-project/sglang/5.4-storage-backends-and-transfer-optimization).

 **Sources**: [python/sglang/srt/managers/cache_controller.py102-188](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/cache_controller.py#L102-L188) [python/sglang/srt/mem_cache/hicache_storage.py30-40](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/hicache_storage.py#L30-L40) [python/sglang/srt/mem_cache/storage/mooncake_store/mooncake_store.py93-107](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/storage/mooncake_store/mooncake_store.py#L93-L107)

 
---

 
## Summary Diagram: Request Dataflow to KV Storage

 
```

```

 **Sources**: [python/sglang/srt/mem_cache/memory_pool.py15-21](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/memory_pool.py#L15-L21) [python/sglang/srt/mem_cache/unified_radix_cache.py148-178](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/unified_radix_cache.py#L148-L178) [python/sglang/srt/managers/cache_controller.py172-188](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/cache_controller.py#L172-L188) [python/sglang/srt/managers/schedule_policy.py138-167](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_policy.py#L138-L167)

 
---

 For more detailed technical explanations, refer to the child pages:

 
 - [Memory Pools and Token-to-KV Mapping](https://deepwiki.com/sgl-project/sglang/5.1-memory-pools-and-token-to-kv-mapping)
 - [RadixCache and Prefix Sharing](https://deepwiki.com/sgl-project/sglang/5.2-radixcache-and-prefix-sharing)
 - [HiCache Multi-Tier Storage](https://deepwiki.com/sgl-project/sglang/5.3-hicache-multi-tier-storage)
 - [Storage Backends and Transfer Optimization](https://deepwiki.com/sgl-project/sglang/5.4-storage-backends-and-transfer-optimization)
