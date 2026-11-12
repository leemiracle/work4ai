> 来源: [https://deepwiki.com/deepseek-ai/DeepEP/4-python-api-reference](https://deepwiki.com/deepseek-ai/DeepEP/4-python-api-reference)
> DeepWiki deepseek-ai/DeepEP

# Python API Reference

  Relevant source files 
 - [deep_ep/__init__.py](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/__init__.py)
 - [deep_ep/buffers/elastic.py](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py)
 - [deep_ep/buffers/legacy.py](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/legacy.py)
 
  This page documents the complete public Python API of the `deep_ep` package (V2). It covers the classes, methods, and type aliases available when you `import deep_ep`. For conceptual background on the V2 architecture and the NCCL Gin backend, see [Core Concepts](https://deepwiki.com/deepseek-ai/DeepEP/3-core-concepts).

 
---

 
## Package Exports

 The `deep_ep` package exports the following symbols, defined in [deep_ep/__init__.py88-95](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/__init__.py#L88-L95):

 
| Symbol | Source | Description |
|---|---|---|
| ElasticBuffer | deep_ep.buffers.elastic | Primary V2 API. Unified communication buffer for all MoE EP operations. |
| EPHandle | deep_ep.buffers.elastic | Metadata handle for EP routing; supports caching for inference. |
| Buffer | deep_ep.buffers.legacy | V1 Legacy API. NVSHMEM-based buffer (archived). |
| EventOverlap | deep_ep.utils.event | CUDA event wrapper for asynchronous execution and overlapping. |
| EventHandle | deep_ep.utils.event | Low-level event handle used for CUDA graph capture. |
| Config | deep_ep._C | Performance tuning parameters (primarily for legacy V1 kernels). |
| topk_idx_t | deep_ep._C | torch.dtype alias for top-k index tensors (typically torch.int64). |

 
---

 
## API Surface Overview

 **Diagram: V2 Module and Class Structure**

 
```

```

 Sources: [deep_ep/__init__.py88-95](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/__init__.py#L88-L95) [deep_ep/buffers/elastic.py25-57](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L25-L57) [deep_ep/buffers/elastic.py123-141](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L123-L141)

 
---

 
## `ElasticBuffer` Class (V2)

 The `ElasticBuffer` class is the central entry point for DeepEP V2. It replaces the V1 `Buffer` and provides a unified interface for high-throughput training, low-latency inference, and experimental primitives like Engram and Pipeline Parallelism.

 
### Key Capabilities

 
 - **Unified Interface**: Handles both "normal" and "low-latency" scenarios via analytical SM tuning rather than separate APIs.
 - **Analytical Resource Allocation**: Automatically calculates optimal SM and QP counts via `get_theoretical_num_sms` and `get_theoretical_num_qps` [deep_ep/buffers/elastic.py440-459](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L440-L459)
 - **Hybrid Mode**: Supports hierarchical communication across NVLink (scale-up) and RDMA (scale-out) domains via `allow_hybrid_mode` [deep_ep/buffers/elastic.py104-106](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L104-L106)
 - **Experimental Primitives**: Includes `engram_fetch` for remote KV cache access and `pp_send`/`pp_recv` for pipeline parallelism.
 
 For a full reference of every method and parameter, see [ElasticBuffer Class](https://deepwiki.com/deepseek-ai/DeepEP/4.1-elasticbuffer-class).

 
---

 
## `EPHandle` and Configuration

 The `EPHandle` object encapsulates the routing metadata generated during a `dispatch` operation. In V2, this handle is critical for:

 
 - **Combine Operations**: Providing the necessary mapping to reverse the dispatch [deep_ep/buffers/elastic.py27-29](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L27-L29)
 - **Inference Caching**: Reusing routing metadata across multiple decoding steps to eliminate CPU-GPU synchronization overhead [deep_ep/buffers/elastic.py27-29](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L27-L29)
 
 **Diagram: V2 Dispatch-Combine Lifecycle**

 
```

```

 Sources: [deep_ep/buffers/elastic.py25-96](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L25-L96) [deep_ep/buffers/elastic.py171-316](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L171-L316)

 For details on handle attributes and caching semantics, see [EPHandle and Configuration Objects](https://deepwiki.com/deepseek-ai/DeepEP/4.2-ephandle-and-configuration-objects).

 
---

 
## Legacy API (V1)

 The `Buffer` class (found in `deep_ep.buffers.legacy`) represents the original V1 implementation. It relies on **NVSHMEM** for internode communication and requires manual auto-tuning of SM counts via `Config` objects.

 
> **Note**: Users are strongly encouraged to migrate to `ElasticBuffer` (V2). V1 is maintained primarily for backward compatibility with existing training pipelines that rely on the `low_latency_dispatch` pure-RDMA path [deep_ep/buffers/legacy.py14-20](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/legacy.py#L14-L20)

 For documentation on the V1 API, see [Legacy Buffer API (V1)](https://deepwiki.com/deepseek-ai/DeepEP/4.3-legacy-buffer-api-(v1)).

 
---

 
## Global Utilities

 DeepEP V2 provides global utility functions to query the communication topology, defined in [deep_ep/utils/envs.py](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/utils/envs.py):

 
| Function | Description |
|---|---|
| get_physical_domain_size() | Returns (rdma_ranks, nvlink_ranks). Represents the physical hardware layout. |
| get_logical_domain_size() | Returns (scaleout_ranks, scaleup_ranks). Represents the logical EP partitioning. |

 These are re-exported at the package level [deep_ep/__init__.py92](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/__init__.py#L92-L92)

 
---

 
## Initialization and JIT

 Upon importing `deep_ep`, the library automatically performs two critical checks:

 
 - **NCCL Version Check**: `check_nccl_so()` ensures the NCCL library loaded by PyTorch matches the one DeepEP was linked against to prevent crashes [deep_ep/__init__.py46-69](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/__init__.py#L46-L69)
 - **JIT Runtime Initialization**: `init_jit()` sets up the paths for the NVRTC-based compiler, enabling runtime kernel generation [deep_ep/__init__.py71-80](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/__init__.py#L71-L80)
 
 Sources: [deep_ep/__init__.py1-97](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/__init__.py#L1-L97) [deep_ep/buffers/elastic.py1-464](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/elastic.py#L1-L464) [deep_ep/buffers/legacy.py14-148](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/deep_ep/buffers/legacy.py#L14-L148)
