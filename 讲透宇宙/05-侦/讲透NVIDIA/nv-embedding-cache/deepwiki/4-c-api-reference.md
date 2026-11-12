<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nv-embedding-cache · page 4 C++ API Reference · fetched 2026-10-26 -->

# C++ API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/cpp_api.md](docs/cpp_api.md)

</details>



## Purpose and Scope

This document provides a complete reference for the C++ API of the NV Embedding Cache SDK. It covers all public C++ classes, interfaces, and functions available to application developers.

The C++ API is organized into three main levels:
- **High-level Embedding Layers** - Complete embedding management with automatic caching and memory hierarchy
- **Mid-level Table Interfaces** - Direct access to storage backends for custom implementations
- **Low-level GPU Cache Primitives** - Fine-grained control over GPU-resident cache operations

For Python API documentation, see [Python API Reference](#5). For conceptual explanations of layers, tables, and caching strategies, see [Core Concepts](#3). For usage examples, see [Examples and Samples](#9).

Sources: [docs/cpp_api.md:1-80](), [README.md:1-94]()

---

## API Architecture Overview

The following diagram illustrates the complete C++ API hierarchy and how components relate to each other:

```mermaid
graph TB
    subgraph "Application Code"
        APP["User Application"]
    end
    
    subgraph "High-Level API - Embedding Layers"
        BASE["EmbeddingLayerBase<br/>(embedding_layer.hpp)"]
        GPU_LAYER["GPUEmbeddingLayer<br/>(gpu_embedding_layer.hpp)"]
        LINEAR_LAYER["LinearUVMEmbeddingLayer<br/>(linear_embedding_layer.hpp)"]
        HIER_LAYER["HierarchicalEmbeddingLayer<br/>(hierarchical_embedding_layer.hpp)"]
    end
    
    subgraph "Mid-Level API - Tables"
        TABLE_IFACE["Table Interface<br/>(table.hpp)"]
        GPU_TABLE["GpuTable<br/>(gpu_table.hpp)"]
        
        subgraph "Host Memory Plugins"
            NVHM["NvhmMapTable<br/>(plugins/nvhm)"]
            ABSEIL["AbseilFlatMapTable<br/>(plugins/abseil)"]
            PHMAP["PHMapFlatMapTable<br/>(plugins/phmap)"]
        end
        
        subgraph "Remote Storage Plugins"
            REDIS["RedisClusterTable<br/>(plugins/redis)"]
            ROCKS["RocksDBTable<br/>(plugins/rocksdb)"]
        end
    end
    
    subgraph "Low-Level API - GPU Cache"
        ECACHE["EmbedCache<br/>(ecache/embed_cache.h)"]
        EC_SA["ECSetAssociative<br/>(ecache/ec_set_associative.h)"]
    end
    
    subgraph "Utility APIs"
        ALLOC["Allocator<br/>(allocator.hpp)"]
        LOGGER["Logger/LoggerBackend<br/>(logging.hpp)"]
        TPOOL["ThreadPool<br/>(thread_pool.hpp)"]
        EXECCTX["ExecutionContext<br/>(execution_context.hpp)"]
    end
    
    APP --> BASE
    BASE --> GPU_LAYER
    BASE --> LINEAR_LAYER
    BASE --> HIER_LAYER
    
    GPU_LAYER --> GPU_TABLE
    LINEAR_LAYER --> GPU_TABLE
    HIER_LAYER --> GPU_TABLE
    HIER_LAYER --> NVHM
    HIER_LAYER --> REDIS
    HIER_LAYER --> ROCKS
    
    TABLE_IFACE --> GPU_TABLE
    TABLE_IFACE --> NVHM
    TABLE_IFACE --> ABSEIL
    TABLE_IFACE --> PHMAP
    TABLE_IFACE --> REDIS
    TABLE_IFACE --> ROCKS
    
    GPU_TABLE --> EC_SA
    EC_SA --> ECACHE
    
    GPU_LAYER -.->|uses| ALLOC
    GPU_LAYER -.->|uses| LOGGER
    GPU_LAYER -.->|uses| EXECCTX
    
    LINEAR_LAYER -.->|uses| ALLOC
    LINEAR_LAYER -.->|uses| LOGGER
    LINEAR_LAYER -.->|uses| EXECCTX
    
    HIER_LAYER -.->|uses| ALLOC
    HIER_LAYER -.->|uses| LOGGER
    HIER_LAYER -.->|uses| TPOOL
    HIER_LAYER -.->|uses| EXECCTX
```

Sources: [docs/cpp_api.md:14-80](), [include/embedding_layer.hpp](), [include/table.hpp](), [include/ecache/embed_cache.h]()

---

## Compilation and Linking

### Building the SDK

Follow the instructions in [Installation and Setup](#2) to build the SDK. The build process produces the following libraries:

| Library | Location | Purpose |
|---------|----------|---------|
| `libnve-common.so` | `build/lib/` | Core SDK with layers, GpuTable, and utilities |
| `libnve-plugin-nvhm.so` | `build/lib/` | NVHM host memory table plugin |
| `libnve-plugin-abseil.so` | `build/lib/` | Abseil host memory table plugin |
| `libnve-plugin-phmap.so` | `build/lib/` | PHMap host memory table plugin |
| `libnve-plugin-redis.so` | `build/lib/` | Redis cluster table plugin |
| `libnve-plugin-rocksdb.so` | `build/lib/` | RocksDB table plugin |

### Linking Applications

Most applications should link against:
- `build/lib/libnve-common.so` - Core SDK functionality
- `libcudart.so` - CUDA runtime
- Any required plugin libraries (e.g., `libnve-plugin-redis.so`)

Plugin libraries must be present in `LD_LIBRARY_PATH` at runtime if they are used by the application.

### Include Paths

Add the following to your include path:
- `include/` - Public SDK headers
- `plugins/[plugin_name]/include/` - Plugin-specific headers (if using plugins directly)

Sources: [docs/cpp_api.md:9-12](), [README.md:44-55]()

---

## Core API Concepts

### Memory Location Types

The SDK uses these memory location identifiers:

| Type | Description | Usage |
|------|-------------|-------|
| `MemoryLocation::kGPU` | GPU device memory | Data resident in GPU VRAM |
| `MemoryLocation::kHost` | System memory | Data in CPU-accessible RAM |
| `MemoryLocation::kManaged` | Unified memory | CUDA managed memory (UVM) |

### Operation Types

All layer and table operations are categorized:

| Operation | Purpose | Modifies Cache State |
|-----------|---------|---------------------|
| `lookup()` | Retrieve embedding rows for given keys | Yes (may trigger inserts) |
| `insert()` | Update cache residency with new keys | Yes |
| `update()` | Modify values for existing keys | No (residency unchanged) |
| `accumulate()` | Add gradients to existing values | No (residency unchanged) |
| `erase()` | Remove keys from cache | Yes |

### Execution Contexts

Execution contexts encapsulate temporary state and memory buffers needed for operations. Create contexts using `layer->create_execution_context()` and reuse them across operations to avoid allocation overhead.

```mermaid
graph LR
    APP["Application Thread"]
    CTX1["ExecutionContext 1"]
    CTX2["ExecutionContext 2"]
    LAYER["EmbeddingLayer"]
    
    APP -->|"create_execution_context()"| LAYER
    LAYER -->|returns| CTX1
    LAYER -->|returns| CTX2
    
    APP -->|"lookup(ctx1, ...)"| LAYER
    APP -->|"lookup(ctx2, ...)"| LAYER
    
    CTX1 -.->|"stores buffers"| TEMP1["Temporary Buffers"]
    CTX2 -.->|"stores buffers"| TEMP2["Temporary Buffers"]
```

For details, see [Execution Contexts](#3.4).

Sources: [docs/cpp_api.md:14-38](), [include/embedding_layer.hpp](), [include/execution_context.hpp]()

---

## Embedding Layer Operations

The following diagram shows the typical workflow for using embedding layers:

```mermaid
sequenceDiagram
    participant App as Application
    participant Layer as EmbeddingLayer
    participant ExecCtx as ExecutionContext
    participant Table as Table(s)
    
    App->>Layer: Constructor(config)
    Layer->>Table: Create table instances
    
    App->>Layer: create_execution_context()
    Layer->>ExecCtx: Allocate buffers
    Layer-->>App: ExecutionContext*
    
    App->>Layer: lookup(ctx, keys, values)
    Layer->>Table: query(keys)
    Table-->>Layer: cached_values + miss_keys
    Layer->>Table: insert(miss_keys)
    Layer-->>App: Success
    
    App->>Layer: update(ctx, keys, new_values)
    Layer->>Table: update(keys, new_values)
    Layer-->>App: Success
    
    App->>Layer: accumulate(ctx, keys, grads)
    Layer->>Table: accumulate(keys, grads)
    Layer-->>App: Success
    
    App->>ExecCtx: delete
    App->>Layer: delete
```

### Common Layer Operations

| Method | Signature | Description |
|--------|-----------|-------------|
| `lookup()` | `Status lookup(ExecutionContext*, keys, values_out)` | Retrieve embedding rows |
| `insert()` | `Status insert(table_type, keys, values)` | Update cache residency |
| `update()` | `Status update(ExecutionContext*, keys, values)` | Modify existing embeddings |
| `accumulate()` | `Status accumulate(ExecutionContext*, keys, grads)` | Add gradients to embeddings |
| `erase()` | `Status erase(table_type, keys)` | Remove embeddings from cache |
| `create_execution_context()` | `ExecutionContext* create_execution_context()` | Allocate execution state |

Sources: [docs/cpp_api.md:24-38](), [include/embedding_layer.hpp]()

---

## Class Hierarchy

The following diagram shows the inheritance relationships between key classes:

```mermaid
classDiagram
    class EmbeddingLayerBase {
        <<abstract>>
        +lookup(ctx, keys, values)*
        +insert(table_type, keys, values)*
        +update(ctx, keys, values)*
        +accumulate(ctx, keys, grads)*
        +erase(table_type, keys)*
        +create_execution_context()*
    }
    
    class GPUEmbeddingLayer {
        +GPUEmbeddingLayer(config)
        +lookup(ctx, keys, values)
        -GpuTable* gpu_table_
    }
    
    class LinearUVMEmbeddingLayer {
        +LinearUVMEmbeddingLayer(config)
        +lookup(ctx, keys, values)
        -GpuTable* gpu_cache_
        -void* uvm_base_ptr_
    }
    
    class HierarchicalEmbeddingLayer {
        +HierarchicalEmbeddingLayer(config)
        +lookup(ctx, keys, values)
        -GpuTable* l1_cache_
        -Table* l2_cache_
        -Table* l3_storage_
    }
    
    class Table {
        <<interface>>
        +lookup(keys, values)*
        +insert(keys, values)*
        +update(keys, values)*
        +contains(keys, results)*
    }
    
    class GpuTable {
        +GpuTable(config)
        +lookup(keys, values)
        -ECSetAssociative* cache_impl_
    }
    
    class NvhmMapTable {
        +NvhmMapTable(config)
        +lookup(keys, values)
    }
    
    class RedisClusterTable {
        +RedisClusterTable(config)
        +lookup(keys, values)
    }
    
    class RocksDBTable {
        +RocksDBTable(config)
        +lookup(keys, values)
    }
    
    EmbeddingLayerBase <|-- GPUEmbeddingLayer
    EmbeddingLayerBase <|-- LinearUVMEmbeddingLayer
    EmbeddingLayerBase <|-- HierarchicalEmbeddingLayer
    
    Table <|.. GpuTable
    Table <|.. NvhmMapTable
    Table <|.. RedisClusterTable
    Table <|.. RocksDBTable
    
    GPUEmbeddingLayer --> GpuTable
    LinearUVMEmbeddingLayer --> GpuTable
    HierarchicalEmbeddingLayer --> GpuTable
    HierarchicalEmbeddingLayer --> Table
```

Sources: [include/embedding_layer.hpp](), [include/gpu_embedding_layer.hpp](), [include/linear_embedding_layer.hpp](), [include/hierarchical_embedding_layer.hpp](), [include/table.hpp](), [include/gpu_table.hpp]()

---

## Data Types and Structures

### Key-Value Representation

Embeddings are represented as key-value pairs:

| Type | Description | Typical Size |
|------|-------------|--------------|
| `KeyType` | Embedding ID (typically `int64_t`) | 8 bytes |
| `ValueType` | Embedding vector element (typically `float`) | 4 bytes |
| Embedding row | Array of `ValueType` with length `embedding_vec_size` | `embedding_vec_size * 4` bytes |

### Configuration Structures

Different components use specific configuration structures:

```mermaid
graph TB
    subgraph "Layer Configuration"
        BASE_CFG["EmbeddingLayerConfig"]
        GPU_CFG["GPUEmbeddingLayerConfig"]
        LINEAR_CFG["LinearUVMEmbeddingLayerConfig"]
        HIER_CFG["HierarchicalEmbeddingLayerConfig"]
    end
    
    subgraph "Table Configuration"
        TABLE_CFG["TableConfig"]
        GPU_TBL_CFG["GpuTableConfig"]
        NVHM_CFG["NvhmMapTableConfig"]
        REDIS_CFG["RedisClusterTableConfig"]
    end
    
    subgraph "Cache Configuration"
        CACHE_CFG["ECConfig"]
        SA_CFG["ECSetAssociativeConfig"]
    end
    
    GPU_CFG -.->|"contains"| GPU_TBL_CFG
    LINEAR_CFG -.->|"contains"| GPU_TBL_CFG
    HIER_CFG -.->|"contains"| GPU_TBL_CFG
    HIER_CFG -.->|"contains"| NVHM_CFG
    HIER_CFG -.->|"contains"| REDIS_CFG
    
    GPU_TBL_CFG -.->|"contains"| SA_CFG
```

Sources: [include/embedding_layer.hpp](), [include/gpu_table.hpp](), [include/ecache/ec_set_associative.h]()

---

## Header File Organization

The SDK organizes headers into logical groups:

### Core Layer Headers

| Header | Classes | Purpose |
|--------|---------|---------|
| [include/embedding_layer.hpp]() | `EmbeddingLayerBase` | Abstract base class for all layers |
| [include/gpu_embedding_layer.hpp]() | `GPUEmbeddingLayer` | GPU-only embedding storage |
| [include/linear_embedding_layer.hpp]() | `LinearUVMEmbeddingLayer` | UVM-based embeddings with GPU cache |
| [include/hierarchical_embedding_layer.hpp]() | `HierarchicalEmbeddingLayer` | Multi-tier hierarchical caching |

### Table Headers

| Header | Classes | Purpose |
|--------|---------|---------|
| [include/table.hpp]() | `Table` | Abstract table interface |
| [include/gpu_table.hpp]() | `GpuTable` | GPU-resident hash table |
| [plugins/nvhm/include/nvhm_map_table.hpp]() | `NvhmMapTable` | nvHashMap-based system memory table |
| [plugins/abseil/include/abseil_flat_map_table.hpp]() | `AbseilFlatMapTable` | Abseil flat_hash_map table |
| [plugins/phmap/include/phmap_flat_map_table.hpp]() | `PHMapFlatMapTable` | Parallel hashmap table |
| [plugins/redis/include/redis_cluster_table.hpp]() | `RedisClusterTable` | Redis cluster storage |
| [plugins/rocksdb/include/rocksdb_table.hpp]() | `RocksDBTable` | RocksDB storage |

### Low-Level Cache Headers

| Header | Classes/Functions | Purpose |
|--------|-------------------|---------|
| [include/ecache/embed_cache.h]() | `EmbedCache` | Base cache interface |
| [include/ecache/ec_set_associative.h]() | `ECSetAssociative` | Set-associative cache implementation |
| [include/ecache/ec_nocache.h]() | `ECNoCache` | Pass-through (no caching) implementation |

### Utility Headers

| Header | Classes | Purpose |
|--------|---------|---------|
| [include/allocator.hpp]() | `Allocator` | Memory allocation interface |
| [include/logging.hpp]() | `Logger`, `LoggerBackend` | Logging system |
| [include/thread_pool.hpp]() | `ThreadPool`, `SimpleThreadPool` | Thread pool for parallel execution |
| [include/execution_context.hpp]() | `ExecutionContext` | Operation execution state |
| [include/common.hpp]() | Global utilities | Common functions (e.g., `GetGlobalLogger()`) |

Sources: [docs/cpp_api.md:1-80](), [include/]()

---

## Building Custom Applications

### Minimal Example Structure

```mermaid
graph LR
    APP["my_app.cpp"]
    HEADERS["SDK Headers<br/>include/*.hpp"]
    LIBNVE["libnve-common.so"]
    PLUGINS["Plugin .so files<br/>(if needed)"]
    CUDA["libcudart.so"]
    BINARY["my_app executable"]
    
    APP -->|includes| HEADERS
    APP -->|links| LIBNVE
    APP -->|links| CUDA
    APP -.->|runtime loads| PLUGINS
    
    APP --> BINARY
```

### Required Compiler Flags

| Flag | Purpose |
|------|---------|
| `-std=c++17` | C++17 standard required |
| `-I/path/to/nve/include` | SDK headers |
| `-L/path/to/nve/build/lib` | SDK libraries |
| `-lnve-common` | Link core library |
| `-lcudart` | Link CUDA runtime |
| `-Wl,-rpath,/path/to/nve/build/lib` | Runtime library path |

### Runtime Environment

```bash
export LD_LIBRARY_PATH=/path/to/nve/build/lib:$LD_LIBRARY_PATH
export CUDA_VISIBLE_DEVICES=0  # Set available GPUs
```

Sources: [docs/cpp_api.md:9-12](), [README.md:44-55]()

---

## API Usage Patterns

### Pattern 1: Direct Layer Usage

This is the recommended pattern for most applications:

```mermaid
graph TB
    INIT["1. Create layer instance<br/>(GPUEmbeddingLayer, etc.)"]
    CTX["2. Create execution context<br/>layer->create_execution_context()"]
    LOOP_START["3. Enter inference loop"]
    LOOKUP["4. Lookup embeddings<br/>layer->lookup(ctx, keys, values)"]
    COMPUTE["5. Perform computation<br/>(model forward pass)"]
    UPDATE["6. Update embeddings<br/>layer->update(ctx, keys, new_vals)"]
    LOOP_END["7. End inference loop"]
    CLEANUP["8. Delete context and layer"]
    
    INIT --> CTX
    CTX --> LOOP_START
    LOOP_START --> LOOKUP
    LOOKUP --> COMPUTE
    COMPUTE --> UPDATE
    UPDATE --> LOOP_START
    LOOP_START --> LOOP_END
    LOOP_END --> CLEANUP
```

### Pattern 2: Custom Table Composition

For advanced users building custom caching strategies:

```mermaid
graph TB
    CREATE_GPU["1. Create GpuTable instance"]
    CREATE_HOST["2. Create host Table instance<br/>(NvhmMapTable, etc.)"]
    CREATE_REMOTE["3. Create remote Table instance<br/>(RedisClusterTable, etc.)"]
    
    CUSTOM["4. Build custom logic:<br/>- Query GPU table first<br/>- Fallback to host on miss<br/>- Fallback to remote on miss<br/>- Promote data up hierarchy"]
    
    CREATE_GPU --> CUSTOM
    CREATE_HOST --> CUSTOM
    CREATE_REMOTE --> CUSTOM
```

### Pattern 3: Low-Level Cache Control

For applications requiring fine-grained cache management:

```mermaid
graph TB
    CREATE_CACHE["1. Create ECSetAssociative instance"]
    ALLOC_MEM["2. Allocate GPU memory<br/>for key/value storage"]
    INIT_CACHE["3. Initialize cache<br/>cache->init(memory, config)"]
    
    QUERY["4. Query cache<br/>cache->query(keys, ...)"]
    UPDATE_CACHE["5. Update cache<br/>cache->update(keys, values, ...)"]
    
    CREATE_CACHE --> ALLOC_MEM
    ALLOC_MEM --> INIT_CACHE
    INIT_CACHE --> QUERY
    QUERY --> UPDATE_CACHE
    UPDATE_CACHE --> QUERY
```

Sources: [docs/cpp_api.md:40-44](), [samples/simple_cpp/](), [samples/layer_sample/]()

---

## Thread Safety and Concurrency

### Thread Safety Guarantees

| Component | Thread Safety | Notes |
|-----------|---------------|-------|
| `EmbeddingLayer` | Thread-safe | Safe to call from multiple threads with different `ExecutionContext` instances |
| `ExecutionContext` | Not thread-safe | Each thread must use its own context |
| `Table` | Implementation-specific | `GpuTable`: thread-safe; Host tables: varies by plugin |
| `GpuTable` | Thread-safe | Safe for concurrent reads and writes |
| `NvhmMapTable` | Thread-safe | Built on thread-safe nvHashMap |
| `ECSetAssociative` | Thread-safe | Atomic operations in CUDA kernels |

### Concurrent Access Pattern

```mermaid
graph TB
    subgraph "Thread 1"
        T1_CTX["ExecutionContext 1"]
        T1_OPS["lookup/update/accumulate"]
    end
    
    subgraph "Thread 2"
        T2_CTX["ExecutionContext 2"]
        T2_OPS["lookup/update/accumulate"]
    end
    
    subgraph "Thread 3"
        T3_CTX["ExecutionContext 3"]
        T3_OPS["lookup/update/accumulate"]
    end
    
    LAYER["EmbeddingLayer<br/>(shared, thread-safe)"]
    
    T1_CTX --> T1_OPS
    T2_CTX --> T2_OPS
    T3_CTX --> T3_OPS
    
    T1_OPS --> LAYER
    T2_OPS --> LAYER
    T3_OPS --> LAYER
```

### CUDA Context Management

Applications using custom thread pools must set the CUDA device context per thread:

```cpp
// Before any CUDA calls in worker thread:
cudaSetDevice(device_id);
// Or use ScopedDevice helper class
```

Sources: [docs/cpp_api.md:74-80](), [include/thread_pool.hpp]()

---

## Error Handling

### Status Return Type

Most operations return a `Status` object indicating success or failure:

```mermaid
graph LR
    CALL["API Call"]
    CHECK{"status.ok()?"}
    SUCCESS["Continue execution"]
    ERROR["Handle error<br/>status.message()"]
    
    CALL --> CHECK
    CHECK -->|true| SUCCESS
    CHECK -->|false| ERROR
```

### Exception Policy

The SDK minimizes exception usage:
- Constructors may throw on invalid configuration
- Runtime operations return `Status` objects
- CUDA errors are checked and reported via `Status`

### Error Categories

| Category | Examples | Recovery |
|----------|----------|----------|
| Configuration errors | Invalid parameter values | Fix configuration and retry |
| Memory allocation errors | Out of GPU/host memory | Reduce cache sizes or batch sizes |
| I/O errors | Redis connection failed | Check network/service availability |
| Capacity errors | Key overflow in cache | Increase cache capacity or use different strategy |

Sources: [include/status.hpp]()

---

## Performance Considerations

### Memory Alignment

The SDK assumes aligned memory for optimal performance:
- Embedding rows should be aligned to 128-byte boundaries
- Use SDK `Allocator` interface for automatic alignment

### Batch Sizes

Operations perform best with batch sizes of:
- Minimum: 256 keys
- Optimal: 1024-8192 keys
- Maximum: Limited by available GPU memory

### CUDA Stream Management

Layers and tables support asynchronous execution via CUDA streams:
- Pass CUDA stream handle to operations
- Synchronize appropriately in application code

```mermaid
graph LR
    APP["Application"]
    STREAM1["CUDA Stream 1"]
    STREAM2["CUDA Stream 2"]
    GPU["GPU Execution"]
    
    APP -->|"lookup(stream1)"| STREAM1
    APP -->|"update(stream2)"| STREAM2
    STREAM1 --> GPU
    STREAM2 --> GPU
```

Sources: [docs/cpp_api.md:14-80]()

---

## Subsection References

For detailed information on specific API components, see:

- **Embedding Layer API**: [Embedding Layer API](#4.1) - Complete reference for `EmbeddingLayerBase` and derived classes
- **Table API**: [Table API](#4.2) - Table interface and all storage backend implementations
- **Low-Level GPU Cache API**: [Low-Level GPU Cache API](#4.3) - Direct access to `ECSetAssociative` and cache primitives
- **Utility Classes**: [Utility Classes](#4.4) - `Allocator`, `Logger`, `ThreadPool`, and helper classes

For conceptual understanding, see:
- [Core Concepts](#3) - Fundamental concepts and design patterns
- [Embedding Layers](#3.1) - Layer types and their use cases
- [Tables and Storage Backends](#3.2) - Storage backend options
- [Memory Hierarchy](#3.3) - How the SDK manages multi-tier memory

For usage examples, see:
- [Basic C++ Example](#9.1) - Simple embedding lookup
- [Layer Sample (Advanced)](#9.3) - Complex multi-layer usage
- [Multi-threaded Inference](#9.4) - Concurrent operations example

Sources: [docs/cpp_api.md:1-80]()

---

