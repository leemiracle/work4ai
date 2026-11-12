> 来源: [https://deepwiki.com/deepseek-ai/DeepEP/6-advanced-features](https://deepwiki.com/deepseek-ai/DeepEP/6-advanced-features)
> DeepWiki deepseek-ai/DeepEP

# Advanced Features

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1)
 
  DeepEP V2 introduces several specialized features beyond basic Expert Parallelism (EP) dispatch and combine operations. These features are designed for extreme performance in large-scale Mixture-of-Experts (MoE) training and inference, providing primitives for remote memory access, pipeline parallelism, and low-precision communication with minimal SM overhead.

 
## Engram: Remote Memory Access

 Engram is a V2 feature providing zero-SM (via RDMA) or near-zero SM remote memory access. It is primarily used for fetching KV cache from remote ranks during inference decoding without interrupting the primary computation [README.md23](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L23-L23)

 
 - **`engram_write`**: Asynchronously writes local data to a remote rank's engram storage [csrc/elastic/buffer.hpp63-64](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp#L63-L64)
 - **`engram_fetch`**: Issues an RDMA `get` request to fetch remote data. It returns a hook (callable) that the user calls to synchronize the result, allowing for maximum overlap [deep_ep/buffers/elastic.py534-585](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L534-L585)
 - **`get_engram_storage_size_hint`**: Static method to calculate required buffer space for engram operations [deep_ep/buffers/elastic.py175-181](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L175-L181)
 
 The underlying `engram_fetch_impl` kernel leverages the **NCCL Gin** backend to issue RDMA requests per warp using `ncclGinRequest_t`, achieving high throughput with minimal resource footprint [deep_ep/include/deep_ep/impls/engram_fetch_impl.cuh20-50](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/include/deep_ep/impls/engram_fetch_impl.cuh#L20-L50)

 For details, see [Engram: Remote Memory Access](https://deepwiki.com/deepseek-ai/DeepEP/6.1-engram:-remote-memory-access).

 **Sources:** [README.md23](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L23-L23) [deep_ep/buffers/elastic.py534-585](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L534-L585) [deep_ep/include/deep_ep/impls/engram_fetch_impl.cuh20-50](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/include/deep_ep/impls/engram_fetch_impl.cuh#L20-L50) [csrc/elastic/buffer.hpp63-64](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp#L63-L64)

 
---

 
## Pipeline Parallelism and AGRS

 DeepEP V2 includes experimental support for Pipeline Parallelism (PP) and All-Gather Reduce-Scatter (AGRS) operations, optimized for the same high-performance communication fabric as the EP kernels.

 
### Pipeline Parallelism (PP)

 The PP API provides `pp_send` and `pp_recv` primitives designed for ring topologies where communication only occurs between `prev_rank_idx` and `next_rank_idx` [csrc/elastic/buffer.hpp67-70](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp#L67-L70)

 
 - **Zero-SM RDMA**: Like Engram, these kernels are designed to saturate RDMA bandwidth while leaving SMs available for model computation [README.md24](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L24-L24)
 - **Configuration**: Managed via `pp_set_config` and `get_pp_buffer_size_hint` [deep_ep/buffers/elastic.py587-628](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L587-L628)
 
 
### All-Gather Reduce-Scatter (AGRS)

 The AGRS API provides high-performance collective primitives often used for Data Parallelism (DP) or Tensor Parallelism (TP) [README.md37](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L37-L37)

 
 - **Session Management**: Uses a context manager `agrs_new_session` or explicit `create_agrs_session` calls to manage collective state and buffer offsets [deep_ep/buffers/elastic.py630-695](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L630-L695)
 - **In-place Operations**: Supports `agrs_get_inplace_tensor` for memory-efficient collectives [deep_ep/buffers/elastic.py674-681](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L674-L681)
 
 For details, see [Pipeline Parallelism and AGRS](https://deepwiki.com/deepseek-ai/DeepEP/6.2-pipeline-parallelism-and-agrs).

 **Sources:** [README.md24-25](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L24-L25) [deep_ep/buffers/elastic.py587-695](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L587-L695) [deep_ep/include/deep_ep/impls/pp_send_recv.cuh1-50](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/include/deep_ep/impls/pp_send_recv.cuh#L1-L50) [csrc/elastic/buffer.hpp67-80](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp#L67-L80)

 
---

 
## Asynchronous Execution and Overlapping

 V2 introduces a more flexible asynchronous execution model compared to V1's `return_recv_hook` pattern. This model is designed for deep communication-computation overlapping and full CUDA graph compatibility.

 
 - **`async_with_compute_stream`**: A flag that allows communication kernels to be launched on a dedicated communication stream while the compute stream continues [deep_ep/buffers/elastic.py277-278](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L277-L278)
 - **`EventOverlap` and `EventHandle`**: Objects used to capture kernel completion via `EventHandle.capture` and synchronize streams via `current_stream_wait` [deep_ep/utils/event.py15-50](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/utils/event.py#L15-L50)
 - **`get_comm_stream`**: Returns the internal communication stream managed by the `ElasticBuffer` [csrc/elastic/buffer.hpp171-173](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp#L171-L173)
 - **`allocate_on_comm_stream`**: Utility to allocate temporary tensors directly on the communication stream's allocator to avoid synchronization [deep_ep/buffers/elastic.py222-230](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L222-L230)
 
 
### Communication-Computation Overlap Workflow

 DeepEP V2 Bridge: System Operations to Code Entities

 
```

```

 For details, see [Asynchronous Execution and Overlapping](https://deepwiki.com/deepseek-ai/DeepEP/6.3-asynchronous-execution-and-overlapping).

 **Sources:** [deep_ep/buffers/elastic.py202-230](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L202-L230) [deep_ep/utils/event.py1-50](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/utils/event.py#L1-L50) [csrc/elastic/buffer.hpp171-173](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp#L171-L173)

 
---

 
## FP8 Quantization and Compression

 To maximize effective bandwidth, DeepEP V2 supports native FP8 (E4M3) quantization for dispatch operations. This reduces the data volume by 2x compared to BF16 [README.md43-51](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L43-L51)

 
 - **`use_fp8_dispatch`**: When enabled, the dispatch kernel performs per-token quantization on the fly [deep_ep/buffers/elastic.py270-272](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L270-L272)
 - **`sf_pack_t`**: Scale factor packs used to manage quantization scales across the communication boundary, controlled by the `kNumSFPacks` template parameter [deep_ep/include/deep_ep/impls/dispatch_impl.cuh38-45](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/include/deep_ep/impls/dispatch_impl.cuh#L38-L45)
 - **Math Utilities**: `per_token_cast_to_fp8` and `per_token_cast_back` are provided in `deep_ep/utils/math.py` for manual quantization tasks [deep_ep/utils/math.py1-100](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/utils/math.py#L1-L100)
 - **Precision Control**: The `allow_multiple_reduction` flag in `ElasticBuffer` allows for finer control over precision during accumulation [csrc/elastic/buffer.hpp45-46](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp#L45-L46)
 
 
### Quantization Entity Mapping

 DeepEP V2 Bridge: Quantization Logic to Code Entities

 
```

```

 For details, see [FP8 Quantization and Compression](https://deepwiki.com/deepseek-ai/DeepEP/6.4-fp8-quantization-and-compression).

 **Sources:** [README.md43-51](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L43-L51) [deep_ep/buffers/elastic.py270-350](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L270-L350) [deep_ep/utils/math.py1-100](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/utils/math.py#L1-L100) [csrc/elastic/buffer.hpp45-46](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/csrc/elastic/buffer.hpp#L45-L46) [deep_ep/include/deep_ep/impls/dispatch_impl.cuh38-45](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/include/deep_ep/impls/dispatch_impl.cuh#L38-L45)
