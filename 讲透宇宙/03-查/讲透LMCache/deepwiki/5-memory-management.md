<!-- source: DeepWiki mcp.deepwiki.com · repo LMCache/LMCache · page 5 Memory Management · fetched 2026-10-21 -->

# Memory Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [lmcache/observability.py](lmcache/observability.py)
- [lmcache/v1/memory_management.py](lmcache/v1/memory_management.py)
- [lmcache/v1/storage_backend/__init__.py](lmcache/v1/storage_backend/__init__.py)
- [lmcache/v1/storage_backend/abstract_backend.py](lmcache/v1/storage_backend/abstract_backend.py)
- [lmcache/v1/storage_backend/local_cpu_backend.py](lmcache/v1/storage_backend/local_cpu_backend.py)
- [lmcache/v1/storage_backend/local_disk_backend.py](lmcache/v1/storage_backend/local_disk_backend.py)
- [lmcache/v1/storage_backend/remote_backend.py](lmcache/v1/storage_backend/remote_backend.py)
- [lmcache/v1/storage_backend/storage_manager.py](lmcache/v1/storage_backend/storage_manager.py)
- [tests/test_observability.py](tests/test_observability.py)
- [tests/v1/storage_backend/test_local_cpu_backend.py](tests/v1/storage_backend/test_local_cpu_backend.py)
- [tests/v1/storage_backend/test_local_disk_backend.py](tests/v1/storage_backend/test_local_disk_backend.py)
- [tests/v1/storage_backend/test_storage_manager.py](tests/v1/storage_backend/test_storage_manager.py)
- [tests/v1/test_address_manager.py](tests/v1/test_address_manager.py)
- [tests/v1/test_memory_management.py](tests/v1/test_memory_management.py)

</details>



The memory management subsystem in LMCache provides a unified framework for allocating, tracking, and reclaiming memory used to store KV caches. It manages memory across CPU, GPU, and specialized hardware with support for several allocator types optimized for different deployment environments.

Key responsibilities of this subsystem include:
- Allocating buffers with various backing storage models.
- Tracking memory usage and lifetime with reference counting and pinning.
- Providing multiple memory formats to represent KV cache tensors.
- Coordinating with the storage backends subsystem for managing cached entries.
- Supporting eviction through cache policies to maintain memory usage within limits.

The subsystem interfaces closely with the storage architecture [Storage Architecture](#4) and GPU memory transfer pipelines [GPU Memory Transfer](#6).

Sources: [lmcache/v1/memory_management.py:1-208](), [lmcache/v1/storage_backend/local_cpu_backend.py:20-28](), [lmcache/v1/storage_backend/storage_manager.py:36-40]()

---

## 5.1. Memory Allocators

LMCache implements a set of memory allocators conforming to the `MemoryAllocatorInterface` abstract base class, specialized for different memory spaces and use cases.

Primary allocator types include:
- **TensorMemoryAllocator**: Allocates raw tensor buffers as PyTorch tensors [tests/v1/test_memory_management.py:136-149]().
- **MixedMemoryAllocator**: Supports pooled allocations mixing pinned host memory and device memory [tests/v1/test_memory_management.py:16-21]().
- **PagedTensorMemoryAllocator**: Supports paged memory allocations for tensor buffers [tests/v1/test_memory_management.py:17-19]().

An `AddressManager` component helps with address space management by tracking free blocks and merging adjacent free segments to reduce fragmentation. This facility ensures efficient memory reuse during allocations and evictions.

These allocators expose consistent APIs for allocation (`allocate`), querying existing allocations (`contains`), and freeing memory. Higher-level cache engine components rely on these allocators to back `MemoryObj` instances for storing KV cache data.

For comprehensive technical details on memory allocator implementations, methods, and address management, see the child page: [Memory Allocators](#5.1).

### Allocator Subsystem Code Architecture

```mermaid
graph TD
    subgraph "Allocator_Code_Space"
        MAI["MemoryAllocatorInterface lmcache/v1/memory_management.py"]
        TMA["TensorMemoryAllocator lmcache/v1/memory_allocators/tensor_memory_allocator.py"]
        MMA["MixedMemoryAllocator lmcache/v1/memory_allocators/mixed_memory_allocator.py"]
        PTMA["PagedTensorMemoryAllocator lmcache/v1/memory_allocators/paged_tensor_memory_allocator.py"]
    end

    MAI <|-- TMA
    MAI <|-- MMA
    MAI <|-- PTMA
```

Sources: [lmcache/v1/memory_management.py:1-208](), [tests/v1/test_memory_management.py:14-21]()

---

## 5.2. Memory Objects and Formats

Memory objects represent the actual cached data stored in memory pools allocated by the allocators. LMCache distinguishes:

- **MemoryObj**: Base class encapsulating common metadata and reference management for buffers.
- **TensorMemoryObj**: Specialization that wraps PyTorch tensors as the backing store [tests/v1/test_memory_management.py:22-26]().

Each `MemoryObj` is associated with a `MemoryObjMetadata` instance, containing:
- Logical tensor shape and dtype [lmcache/v1/memory_management.py:146-152]().
- Physical memory address and allocated size [lmcache/v1/memory_management.py:154-158]().
- Reference count and pin count (for eviction control) [lmcache/v1/memory_management.py:160-166]().
- Memory format describing the layout of key-value cache data [lmcache/v1/memory_management.py:168-169]().

The `MemoryFormat` enum defines common layouts, including:
- `KV_2LTD` — 4D tensor with shape `[2, num_layers, num_tokens, hidden_dim]` [lmcache/v1/memory_management.py:77-80]().
- `KV_T2D` — 3D tensor with shape `[2, num_tokens, hidden_dim]` [lmcache/v1/memory_management.py:86-88]().
- `KV_MLA_FMT` — specialized 4D tensor format `[1, num_layers, num_tokens, aligned_head_size]` [lmcache/v1/memory_management.py:97-99]().
- Others include binary formats and encoder cache formats [lmcache/v1/memory_management.py:101-113]().

These formats ensure consistent interpretation of cache tensors across GPU transfer and storage layers.

For an exhaustive description of memory objects, metadata fields, and supported tensor formats, see the child page: [Memory Objects and Formats](#5.2).

### Memory Object and Format Code Hierarchy

```mermaid
graph TD
    subgraph "Object_Code_Space"
        MO["MemoryObj lmcache/v1/memory_management.py"]
        TMO["TensorMemoryObj lmcache/v1/memory_management.py"]
        MOM["MemoryObjMetadata lmcache/v1/memory_management.py"]
        MF["MemoryFormat lmcache/v1/memory_management.py"]
    end

    MO <|-- TMO
    TMO --> MOM
    MOM --> MF
```

Sources: [lmcache/v1/memory_management.py:77-170]()

---

## 5.3. Reference Counting and Eviction

LMCache uses a dual-count mechanism for managing the lifecycle of cached memory objects:

- **Reference Count (`ref_count`)**: Tracks active references held by system components to prevent premature deallocation [lmcache/v1/memory_management.py:161-161]().
- **Pin Count (`pin_count`)**: Indicates persistent pins, e.g., by cache controllers or ongoing lookups, which prevent eviction while active [lmcache/v1/memory_management.py:163-166]().

When both `ref_count` and `pin_count` drop to zero for a `MemoryObj`, the buffer is eligible for deallocation and reuse by the allocator.

Eviction coordination involves:
- Cache policies like LRU, LFU, FIFO, and MRU that select candidates for removal based on usage patterns [lmcache/v1/storage_backend/local_cpu_backend.py:62-63]().
- The `PinMonitor` tracks pinned objects to avoid eviction of in-use memory [lmcache/v1/memory_management.py:22-22]().
- Interaction with the storage manager to enforce watermarks and manage eviction triggers [lmcache/v1/storage_backend/storage_manager.py:36-40]().

This approach ensures safe reclamation of memory while maximizing cache hit rates and minimizing unwanted cache misses.

For detailed workflows on reference counting, pin/unpin operations, eviction candidate selection, and cache policies, consult the child page: [Reference Counting and Eviction](#5.3).

Sources: [lmcache/v1/storage_backend/local_cpu_backend.py:62-63](), [lmcache/v1/memory_management.py:22-166](), [lmcache/v1/storage_backend/storage_manager.py:36-40]()

---

## Child Pages

For more technical detail and implementation specifics, please refer to the following linked sub-pages:

* **[Memory Allocators](#5.1)** — Detailed documentation of `MemoryAllocatorInterface`, allocator implementations including `TensorMemoryAllocator`, `MixedMemoryAllocator`, `CuFileMemoryAllocator`, lazy and devdax allocators, and the `AddressManager`.
* **[Memory Objects and Formats](#5.2)** — Explanation of `MemoryObj`, `TensorMemoryObj`, associated `MemoryObjMetadata`, and the `MemoryFormat` enumeration (e.g., `KV_2LTD`, `KV_T2D`, `KV_MLA_FMT`).
* **[Reference Counting and Eviction](#5.3)** — Coverage of reference counting methods (`ref_count_up`/`ref_count_down`), pinning (`pin`/`unpin`), the `PinMonitor` utility, eviction candidate selection, and cache eviction policies (LRU, LFU, FIFO, MRU).

---

