<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nv-embedding-cache · page 13 Release History · fetched 2026-10-26 -->

# Release History

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [version.txt](version.txt)

</details>



This page documents the complete version history of the NV Embedding Cache SDK, including new features, improvements, and bug fixes for each release. The SDK follows a time-based versioning scheme where releases are named in the format `vYY.MM[.P]` (e.g., `v26.03.0` for the March 2026 release, patch 0).

For detailed information about specific release features, see the child pages: [Version 26.03](#13.1), [Version 26.02.1](#13.2), and [Version 26.02](#13.3). For information about contributing to future releases, see [Contributing](#12). For build system details and feature flags, see [Build System Details](#10).

**Sources:** [CHANGELOG.md:1-41](), [version.txt:1]()

## Versioning Scheme

The NV Embedding Cache SDK uses a time-based versioning format:

| Component | Format | Example | Description |
|-----------|--------|---------|-------------|
| Major | `YY` | `26` | Two-digit year (2026) |
| Minor | `MM` | `03` | Two-digit month (March) |
| Patch | `P` (optional) | `0`, `1`, `2` | Patch number for hotfixes |

The complete version is: `vYY.MM.P` (e.g., `v26.03.0`)

**Current Version:** `26.03.0` as defined in [version.txt:1]()

**Sources:** [CHANGELOG.md:5-6](), [version.txt:1]()

## Release Timeline

```mermaid
timeline
    title "NV Embedding Cache Release Evolution"
    
    section "v26.02 (Feb 2026)"
        Initial Release : Core embedding cache functionality
                       : GPUEmbeddingLayer
                       : LinearUVMEmbeddingLayer
                       : HierarchicalEmbeddingLayer
                       : Basic plugin system
        Critical Gap : Missing NVHM submodule
                     : libnve-plugin-nvhm.so unavailable
                     : Some tests/samples fail
    
    section "v26.02.1 (Feb 2026)"
        Stabilization : Added nvhashmap submodule
                      : libnve-plugin-nvhm.so functional
                      : All tests passing
                      : Production-ready baseline
    
    section "v26.03 (Mar 2026)"
        Major Expansion : Multi-GPU support
                        : Triton Inference Server samples
                        : Checkpoint save/load
                        : Extended Python API
                        : Kernel optimizations
                        : Redis parameter server bindings
                        : erase() API support
```

**Sources:** [CHANGELOG.md:7-28]()

## Feature Evolution by Release

```mermaid
graph TB
    subgraph "v26.02: Foundation"
        V2602_CORE["Core Architecture<br/>EmbeddingLayerBase"]
        V2602_GPU["GPUEmbeddingLayer<br/>src/embeddinglayer/noevo/noevoembeddinglayer_base.hpp"]
        V2602_LINEAR["LinearUVMEmbeddingLayer<br/>src/embeddinglayer/uvm/linearuvmembeddinglayer.hpp"]
        V2602_HIER["HierarchicalEmbeddingLayer<br/>src/embeddinglayer/hier/hierarchicalembeddinglayer.hpp"]
        V2602_GPU_TABLE["GpuTable<br/>src/table/gpu/gpu_table.cu"]
        V2602_REDIS["RedisClusterTable<br/>plugins/redis/redis_cluster_table.cpp"]
        V2602_ROCKS["RocksDBTable<br/>plugins/rocksdb/rocksdb_table.cpp"]
        V2602_MISSING["❌ NVHM Missing<br/>libnve-plugin-nvhm.so"]
    end
    
    subgraph "v26.02.1: Stability"
        V26021_NVHM["✓ NVHM Submodule<br/>third_party/nvhashmap"]
        V26021_PLUGIN["✓ NvhmMapTable<br/>plugins/nvhm/nvhm_map_table.cpp"]
        V26021_LIB["✓ libnve-plugin-nvhm.so"]
    end
    
    subgraph "v26.03: Production Features"
        V2603_MGPU["Multi-GPU Support<br/>docs/multi_gpu.md"]
        V2603_TRITON["Triton Integration<br/>samples/triton/"]
        V2603_CKPT["Checkpoint I/O<br/>samples/checkpoint/"]
        V2603_KERNEL["Kernel Optimizations<br/>src/ec/kernels/"]
        V2603_PY_REDIS["Python Redis Bindings<br/>python/pynve/"]
        V2603_PY_ERASE["erase() API<br/>python/pynve/"]
        V2603_PY_BUFFER["Shared Host Buffer<br/>python/pynve/"]
        V2603_BUG_OVFL["Fixed NVHM Overflow<br/>plugins/nvhm/"]
        V2603_BENCH["Benchmark Scripts<br/>samples/benchmark/"]
    end
    
    V2602_CORE --> V2602_GPU
    V2602_CORE --> V2602_LINEAR
    V2602_CORE --> V2602_HIER
    
    V2602_MISSING -.->|fixed in| V26021_NVHM
    V26021_NVHM --> V26021_PLUGIN
    V26021_PLUGIN --> V26021_LIB
    
    V26021_LIB -.->|enabled| V2603_MGPU
    V26021_LIB -.->|enabled| V2603_TRITON
    V26021_LIB -.->|enabled| V2603_CKPT
    
    V2602_GPU --> V2603_KERNEL
    V2603_KERNEL --> V2603_MGPU
    
    V2602_REDIS --> V2603_PY_REDIS
    
    V26021_PLUGIN --> V2603_BUG_OVFL
    
    style V2602_MISSING fill:#fee
    style V26021_NVHM fill:#efe
    style V26021_PLUGIN fill:#efe
    style V26021_LIB fill:#efe
```

**Sources:** [CHANGELOG.md:7-28]()

## Release Details

### v26.03 (March 2026) - Current Release

The latest production release with comprehensive multi-GPU support, production deployment features, and extensive Python API improvements.

#### New Features

| Feature | Code Location | Description |
|---------|---------------|-------------|
| **Load/Save Checkpoint** | `samples/checkpoint/` | Checkpoint save/load samples for fault tolerance |
| **Triton Inference Server** | `samples/triton/` | Production inference deployment with NVIDIA Triton |
| **Multi-GPU Documentation** | `docs/multi_gpu.md` | Comprehensive multi-GPU configuration guide |
| **Benchmark Scripts** | `samples/benchmark/` | Single-GPU and multi-GPU performance benchmarking |

#### Improvements

| Area | Changes | Code Location |
|------|---------|---------------|
| **Kernel Optimizations** | Additional tile sizes supported | `src/ec/kernels/` |
| **Python Bindings** | Redis parameter server support | `python/pynve/` |
| **Python Bindings** | Shared host buffer access API | `python/pynve/` |
| **Python Bindings** | `erase()` API for removing embeddings | `python/pynve/` |

#### Bug Fixes

| Issue | Resolution | Code Location |
|-------|------------|---------------|
| **Excessive Overflow Handling** | Fixed NVHM table overflow handling | `plugins/nvhm/` |

For complete details, see [Version 26.03](#13.1).

**Sources:** [CHANGELOG.md:7-19]()

---

### v26.02.1 (February 2026) - Stabilization Release

Critical patch release that added the missing NVHM dependency, enabling full functionality of the system memory cache tier.

#### New Features

| Feature | Code Location | Description |
|---------|---------------|-------------|
| **NVHM Submodule** | `third_party/nvhashmap` | Added nvHashMap as git submodule |
| **NVHM Plugin** | `plugins/nvhm/nvhm_map_table.cpp` | Enabled `NvhmMapTable` implementation |
| **NVHM Library** | Build output: `libnve-plugin-nvhm.so` | Shared library for NVHM table backend |

#### Impact

Before v26.02.1, the following components were non-functional:
- `HierarchicalEmbeddingLayer` with NVHM system memory tier
- Tests and samples requiring `NvhmMapTable`
- Multi-tier caching scenarios

After v26.02.1, the system became fully functional with all three caching strategies operational.

```mermaid
graph LR
    subgraph "Before v26.02.1"
        APP1["Application"]
        HIER1["HierarchicalEmbeddingLayer"]
        GPU1["GpuTable"]
        NVHM1["❌ NvhmMapTable<br/>Missing dependency"]
        
        APP1 --> HIER1
        HIER1 --> GPU1
        HIER1 -.->|unavailable| NVHM1
    end
    
    subgraph "After v26.02.1"
        APP2["Application"]
        HIER2["HierarchicalEmbeddingLayer"]
        GPU2["GpuTable"]
        NVHM2["✓ NvhmMapTable<br/>libnve-plugin-nvhm.so"]
        SUBMOD["third_party/nvhashmap"]
        
        APP2 --> HIER2
        HIER2 --> GPU2
        HIER2 --> NVHM2
        NVHM2 --> SUBMOD
    end
```

For complete details, see [Version 26.02.1](#13.2).

**Sources:** [CHANGELOG.md:20-23]()

---

### v26.02 (February 2026) - Initial Release

The foundational release establishing the core architecture, three-tier caching strategies, and plugin system.

#### New Features

This release established the complete base architecture:

| Component Category | Features | Code Locations |
|-------------------|----------|----------------|
| **Embedding Layers** | GPUEmbeddingLayer, LinearUVMEmbeddingLayer, HierarchicalEmbeddingLayer | `src/embeddinglayer/noevo/`, `src/embeddinglayer/uvm/`, `src/embeddinglayer/hier/` |
| **GPU Tables** | GpuTable with set-associative cache | `src/table/gpu/gpu_table.cu` |
| **Host Tables** | AbseilFlatMapTable, PHMapFlatMapTable, LinearHostTable | `plugins/abseil/`, `plugins/phmap/`, `src/table/linear_host_table.cu` |
| **Remote Tables** | RedisClusterTable, RocksDBTable | `plugins/redis/`, `plugins/rocksdb/` |
| **Low-Level Cache** | Set-associative GPU cache kernels | `src/ec/ec_set_associative.cu` |
| **Python Bindings** | pynve module with PyTorch integration | `python/pynve/` |
| **C++ API** | Public headers for embedding layers and tables | `include/nve/` |
| **Build System** | CMake configuration with feature selection | `CMakeLists.txt` |
| **Samples** | Basic C++ and Python examples | `samples/` |

#### Known Limitations

As documented in [CHANGELOG.md:27-28]():

> **Note:** NVHM is not included in this release, so some tests/samples that rely on it will fail and complain about a missing `libnve-plugin-nvhm.so`.

This limitation was addressed in the immediate follow-up release v26.02.1.

```mermaid
graph TB
    subgraph "v26.02 Component Status"
        WORKING["✓ Fully Functional"]
        LIMITED["⚠ Limited Functionality"]
        
        WORKING --> GPU_ONLY["GPUEmbeddingLayer<br/>Complete dataset in GPU"]
        WORKING --> LINEAR["LinearUVMEmbeddingLayer<br/>UVM-based caching"]
        WORKING --> REDIS_TABLE["RedisClusterTable"]
        WORKING --> ROCKS_TABLE["RocksDBTable"]
        WORKING --> ABSEIL_TABLE["AbseilFlatMapTable"]
        WORKING --> PHMAP_TABLE["PHMapFlatMapTable"]
        
        LIMITED --> HIER["HierarchicalEmbeddingLayer<br/>Missing NVHM tier"]
        LIMITED --> NVHM_DEP["NvhmMapTable<br/>Dependency unavailable"]
    end
```

For complete details, see [Version 26.02](#13.3).

**Sources:** [CHANGELOG.md:24-28]()

## Component Lifecycle Matrix

The following table shows when each major component became available:

| Component | v26.02 | v26.02.1 | v26.03 | Code Path |
|-----------|---------|----------|--------|-----------|
| **Core Layers** ||||
| `GPUEmbeddingLayer` | ✓ | ✓ | ✓ | `src/embeddinglayer/noevo/` |
| `LinearUVMEmbeddingLayer` | ✓ | ✓ | ✓ | `src/embeddinglayer/uvm/` |
| `HierarchicalEmbeddingLayer` | ⚠ | ✓ | ✓ | `src/embeddinglayer/hier/` |
| **GPU Components** ||||
| `GpuTable` | ✓ | ✓ | ✓ | `src/table/gpu/gpu_table.cu` |
| Set-associative cache | ✓ | ✓ | ✓ | `src/ec/ec_set_associative.cu` |
| Multi-GPU support | ✗ | ✗ | ✓ | `src/embeddinglayer/*/` |
| **System Memory Plugins** ||||
| `NvhmMapTable` | ✗ | ✓ | ✓ | `plugins/nvhm/nvhm_map_table.cpp` |
| `AbseilFlatMapTable` | ✓ | ✓ | ✓ | `plugins/abseil/abseil_flat_map_table.cpp` |
| `PHMapFlatMapTable` | ✓ | ✓ | ✓ | `plugins/phmap/phmap_flat_map_table.cpp` |
| `LinearHostTable` | ✓ | ✓ | ✓ | `src/table/linear_host_table.cu` |
| **Remote Storage Plugins** ||||
| `RedisClusterTable` | ✓ | ✓ | ✓ | `plugins/redis/redis_cluster_table.cpp` |
| `RocksDBTable` | ✓ | ✓ | ✓ | `plugins/rocksdb/rocksdb_table.cpp` |
| **Python API** ||||
| Basic `NVEmbedding` | ✓ | ✓ | ✓ | `python/pynve/nve.py` |
| Redis parameter server | ✗ | ✗ | ✓ | `python/pynve/` |
| `erase()` API | ✗ | ✗ | ✓ | `python/pynve/` |
| Shared host buffer | ✗ | ✗ | ✓ | `python/pynve/` |
| **Samples & Docs** ||||
| Basic samples | ✓ | ✓ | ✓ | `samples/basic/` |
| Checkpoint samples | ✗ | ✗ | ✓ | `samples/checkpoint/` |
| Triton samples | ✗ | ✗ | ✓ | `samples/triton/` |
| Benchmark scripts | ✗ | ✗ | ✓ | `samples/benchmark/` |
| Multi-GPU docs | ✗ | ✗ | ✓ | `docs/multi_gpu.md` |

**Legend:**
- ✓ = Fully functional
- ⚠ = Limited functionality (NVHM tier missing)
- ✗ = Not available

**Sources:** [CHANGELOG.md:7-28]()

## Breaking Changes and Migration Notes

### From v26.02 to v26.02.1

**No breaking changes.** This was a pure addition release that added the missing NVHM dependency. Existing code continues to work without modification.

**Migration Required:** None

### From v26.02.1 to v26.03

**No breaking changes.** All improvements and new features are additive. The API remains backward compatible.

**New Optional Features:**
- Multi-GPU configurations require explicit setup (see [Multi-GPU Support](#8.1))
- Extended Python API methods are available but not required
- Checkpoint save/load is opt-in functionality

**Migration Required:** None for existing code. New features can be adopted incrementally.

**Sources:** [CHANGELOG.md:7-28]()

## Version Format for Future Releases

Future releases will follow the same format as documented in [CHANGELOG.md:31-40]():

```markdown
## NV Embedding Cache YY.MM(.PP)
### New Features
- ...
### Improvements
- ...
### Bug Fixes
- ...
```

Releases are published at approximately monthly intervals, with patch releases (`.P`) issued as needed for critical bug fixes.

**Sources:** [CHANGELOG.md:31-40]()

---

For more information about specific release features and detailed migration guides, see the child pages:
- [Version 26.03](#13.1) - Current release details
- [Version 26.02.1](#13.2) - NVHM stabilization
- [Version 26.02](#13.3) - Initial release features

For information about contributing to future releases, see [Contributing](#12).

---

