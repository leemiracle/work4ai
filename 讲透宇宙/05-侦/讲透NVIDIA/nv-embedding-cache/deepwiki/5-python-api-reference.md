<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nv-embedding-cache · page 5 Python API Reference · fetched 2026-10-26 -->

# Python API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/samples.md](docs/samples.md)
- [python/pynve/bindings/binding_layers.hpp](python/pynve/bindings/binding_layers.hpp)

</details>



This document provides comprehensive reference documentation for the Python API of the NV Embedding Cache SDK. The Python bindings, provided through the `pynve` module, expose the C++ core functionality with idiomatic Python interfaces and seamless PyTorch integration.

**Scope**: This page covers the Python-specific API, including the `NVEmbedding` class, configuration objects, data type enumerations, and PyTorch integration patterns. For C++ API details, see [C++ API Reference](#4). For conceptual understanding of the three caching strategies, see [Cache Configuration Strategies](#1.2). For practical examples, see [Python Embedding Layers](#5.1) and [PyTorch Integration](#5.2).

**Sources**: [README.md:1-94](), [docs/samples.md:1-29]()

---

## Python Module Structure

The Python API is organized into several key components that mirror the C++ architecture while providing Pythonic interfaces:

```mermaid
graph TB
    subgraph "Python Package: pynve"
        NVE["NVEmbedding<br/>(Main API)"]
        CONFIG["Configuration Classes<br/>EmbedLayerConfig"]
        ENUMS["Enumerations<br/>DataType, PoolingType,<br/>CacheType"]
        UTILS["Utilities<br/>DLPack, Serialization"]
    end
    
    subgraph "C++ Bindings Layer"
        BIND_BASE["NVEmbedBinding&lt;IndexT&gt;<br/>python/pynve/bindings/binding_layers.hpp:58"]
        BIND_HIER["HierarchicalEmbedding&lt;IndexT&gt;<br/>python/pynve/bindings/binding_layers.hpp:363"]
        BIND_LINEAR["LinearUVMEmbedding&lt;IndexT&gt;<br/>python/pynve/bindings/binding_layers.hpp:479"]
        BIND_GPU["GPUEmbedding&lt;IndexT&gt;<br/>python/pynve/bindings/binding_layers.hpp:627"]
    end
    
    subgraph "C++ Core Layer"
        LAYER_BASE["EmbeddingLayerBase<br/>include/embedding_layer.hpp"]
        LAYER_HIER["HierarchicalEmbeddingLayer<br/>include/hierarchical_embedding_layer.hpp"]
        LAYER_LINEAR["LinearUVMEmbeddingLayer<br/>include/linear_embedding_layer.hpp"]
        LAYER_GPU["GPUEmbeddingLayer<br/>include/gpu_embedding_layer.hpp"]
    end
    
    NVE --> CONFIG
    NVE --> ENUMS
    NVE --> UTILS
    
    NVE -.->|"instantiates via pybind11"| BIND_BASE
    
    BIND_BASE --> BIND_HIER
    BIND_BASE --> BIND_LINEAR
    BIND_BASE --> BIND_GPU
    
    BIND_HIER -.->|wraps| LAYER_HIER
    BIND_LINEAR -.->|wraps| LAYER_LINEAR
    BIND_GPU -.->|wraps| LAYER_GPU
    
    LAYER_HIER --> LAYER_BASE
    LAYER_LINEAR --> LAYER_BASE
    LAYER_GPU --> LAYER_BASE
```

**Sources**: [python/pynve/bindings/binding_layers.hpp:1-660]()

---

## Core Python Classes

### NVEmbedding Class

The `NVEmbedding` class is the primary Python interface for embedding lookups. It provides a unified API that automatically instantiates the appropriate underlying C++ layer based on the `cache_type` parameter.

#### Class Hierarchy and Code Mapping

```mermaid
graph LR
    subgraph "Python Layer"
        PY_NVE["NVEmbedding<br/>(Python API)"]
    end
    
    subgraph "Binding Templates"
        BIND["NVEmbedBinding&lt;IndexT&gt;<br/>:58-360"]
        HIER["HierarchicalEmbedding&lt;IndexT&gt;<br/>:363-476"]
        LINEAR["LinearUVMEmbedding&lt;IndexT&gt;<br/>:479-624"]
        GPU["GPUEmbedding&lt;IndexT&gt;<br/>:627-657"]
    end
    
    PY_NVE -->|"cache_type='Hierarchical'"| HIER
    PY_NVE -->|"cache_type='LinearUVM'"| LINEAR
    PY_NVE -->|"cache_type='NoCache'"| GPU
    
    HIER --> BIND
    LINEAR --> BIND
    GPU --> BIND
```

**Sources**: [python/pynve/bindings/binding_layers.hpp:58-657](), [README.md:11-15]()

#### Constructor Parameters

The `NVEmbedding` constructor accepts the following parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `device_id` | `int` | CUDA device ID for GPU operations |
| `row_size` | `int` | Embedding dimension (number of elements per embedding) |
| `dtype` | `DataType` | Data type of embeddings (Float32 or Float16) |
| `cache_type` | `str` | Cache strategy: `"NoCache"`, `"LinearUVM"`, or `"Hierarchical"` |
| `num_embeddings` | `int` | Total number of embeddings (required for NoCache and LinearUVM) |
| `gpu_cache_size` | `int` | Size of GPU cache in bytes (for LinearUVM and Hierarchical) |
| `host_cache_size` | `int` | Size of host memory cache in bytes (for Hierarchical only) |
| `remote_table` | `Table` | Remote parameter server table (for Hierarchical only) |
| `embedding_table` | `int` | Pointer to GPU memory (for NoCache only) |
| `mem_block` | `MemBlock` | UVM memory block (for LinearUVM only) |
| `config` | `EmbedLayerConfig` | Advanced configuration options |

**Sources**: [python/pynve/bindings/binding_layers.hpp:266-283](), [python/pynve/bindings/binding_layers.hpp:369-427](), [python/pynve/bindings/binding_layers.hpp:484-537](), [python/pynve/bindings/binding_layers.hpp:632-650]()

### EmbedLayerConfig

Configuration object for advanced layer settings:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `logging_interval` | `int` | `-1` | Number of lookups between hit rate logs (-1 disables) |
| `kernel_mode` | `int` | `0` | Kernel execution mode (see Kernel Modes below) |
| `kernel_mode_value_1` | `int` | `0` | First kernel mode parameter |
| `kernel_mode_value_2` | `int` | `0` | Second kernel mode parameter |

**Kernel Modes**:
- `0`: Default kernel
- `KernelType.SortGather`: Sort-based gather (uses `kernel_mode_value_1` as task size, default 1024)
- `KernelType.PipelineGather`: Pipelined gather (uses `kernel_mode_value_1` as task size and `kernel_mode_value_2` as number of auxiliary streams)

**Sources**: [python/pynve/bindings/binding_layers.hpp:50-55](), [python/pynve/bindings/binding_layers.hpp:516-526]()

---

## Core Operations

All embedding layer types expose a consistent set of operations through the `NVEmbedBinding` base class:

```mermaid
graph TB
    subgraph "Read Operations"
        LOOKUP["lookup(num_keys, keys, output, stream)<br/>:61-76"]
        LOOKUP_POOL["lookup_with_pooling(...)<br/>:78-103"]
    end
    
    subgraph "Write Operations"
        INSERT["insert(num_keys, keys, values, table_id, stream)<br/>:242-252"]
        UPDATE["update(num_keys, keys, updates, stream)<br/>:232-240"]
        ACCUM["accumulate(num_keys, keys, updates, stream)<br/>:221-230"]
        ERASE["erase(num_keys, keys, table_id, stream)<br/>:260-264"]
        CLEAR["clear(stream)<br/>:254-258"]
    end
    
    subgraph "Backpropagation"
        CONCAT_BP["concat_backprop(...)<br/>:105-160"]
        POOL_BP["pooling_backprop(...)<br/>:162-219"]
    end
    
    subgraph "Execution Context Management"
        GET_CTX["get_exec_context(stream)<br/>:308-321"]
        STREAM_MAP["stream_ctx_map_<br/>:355"]
    end
    
    LOOKUP --> GET_CTX
    LOOKUP_POOL --> GET_CTX
    INSERT --> GET_CTX
    UPDATE --> GET_CTX
    ACCUM --> GET_CTX
    ERASE --> GET_CTX
    
    GET_CTX --> STREAM_MAP
```

**Sources**: [python/pynve/bindings/binding_layers.hpp:61-321]()

### lookup

Retrieves embeddings for the given keys.

**Python Signature**:
```python
def lookup(self, num_keys: int, keys: int, output: int, stream: int) -> None
```

**Parameters**:
- `num_keys`: Number of embedding IDs to look up
- `keys`: Memory address (uintptr_t) of embedding IDs array (`IndexT*`)
- `output`: Memory address (uintptr_t) of output buffer for embeddings
- `stream`: CUDA stream handle (cudaStream_t cast to int)

**Behavior**: Performs embedding lookup and writes results to the output buffer. Returns hit rates through the configured logging mechanism.

**Sources**: [python/pynve/bindings/binding_layers.hpp:61-76]()

### lookup_with_pooling

Retrieves embeddings with sparse feature pooling.

**Python Signature**:
```python
def lookup_with_pooling(self, num_keys: int, keys: int, output: int,
                        pooling_type: int, num_offsets: int, offsets: int,
                        weight_data_type: int, weights: int, stream: int) -> None
```

**Parameters**:
- `num_keys`: Total number of embedding IDs
- `keys`: Memory address of embedding IDs array
- `output`: Memory address of pooled output buffer
- `pooling_type`: Pooling operation type (see PoolingType enumeration)
- `num_offsets`: Number of offset entries (batch size + 1 for CSR format)
- `offsets`: Memory address of CSR offset array (`int64_t*`)
- `weight_data_type`: Data type of weights (DataType enumeration)
- `weights`: Memory address of weight values (nullable)
- `stream`: CUDA stream handle

**Pooling Types**:
- `PoolingType.Sum`: Sum pooling
- `PoolingType.Mean`: Average pooling
- `PoolingType.Concatenate`: Concatenation (no pooling)

**Sources**: [python/pynve/bindings/binding_layers.hpp:78-103]()

### insert

Inserts new embedding vectors into the cache hierarchy.

**Python Signature**:
```python
def insert(self, num_keys: int, keys: int, values: int, table_id: int, stream: int) -> None
```

**Parameters**:
- `num_keys`: Number of embeddings to insert
- `keys`: Memory address of embedding IDs
- `values`: Memory address of embedding values (row-major format)
- `table_id`: Target table ID in the hierarchy (-1 for all levels)
- `stream`: CUDA stream handle

**Behavior**: Inserts embeddings into the specified table level. The insert heuristic determines whether to propagate to higher cache levels.

**Sources**: [python/pynve/bindings/binding_layers.hpp:242-252]()

### update

Overwrites existing embedding values.

**Python Signature**:
```python
def update(self, num_keys: int, keys: int, updates: int, stream: int) -> None
```

**Parameters**:
- `num_keys`: Number of embeddings to update
- `keys`: Memory address of embedding IDs
- `updates`: Memory address of new embedding values
- `stream`: CUDA stream handle

**Behavior**: Replaces existing embedding values with new values. Does not insert if the key doesn't exist.

**Sources**: [python/pynve/bindings/binding_layers.hpp:232-240]()

### accumulate

Applies additive updates to embeddings (gradient accumulation).

**Python Signature**:
```python
def accumulate(self, num_keys: int, keys: int, updates: int, stream: int) -> None
```

**Parameters**:
- `num_keys`: Number of gradient updates
- `keys`: Memory address of embedding IDs
- `updates`: Memory address of gradient values
- `stream`: CUDA stream handle

**Behavior**: Adds the update values to existing embeddings using atomic operations. Commonly used for gradient descent training.

**Sources**: [python/pynve/bindings/binding_layers.hpp:221-230]()

### erase

Removes embeddings from the cache.

**Python Signature**:
```python
def erase(self, num_keys: int, keys: int, table_id: int, stream: int) -> None
```

**Parameters**:
- `num_keys`: Number of embeddings to remove
- `keys`: Memory address of embedding IDs to erase
- `table_id`: Target table ID (-1 for all levels)
- `stream`: CUDA stream handle

**Behavior**: Removes the specified embeddings from cache. Available in version 26.03+.

**Sources**: [python/pynve/bindings/binding_layers.hpp:260-264]()

### clear

Clears all embeddings from the cache.

**Python Signature**:
```python
def clear(self, stream: int) -> None
```

**Parameters**:
- `stream`: CUDA stream handle

**Behavior**: Removes all cached embeddings across all cache levels.

**Sources**: [python/pynve/bindings/binding_layers.hpp:254-258]()

---

## Backpropagation Operations

The SDK provides specialized operations for computing gradients during training:

### concat_backprop

Computes gradients for concatenated embeddings.

**Python Signature**:
```python
def concat_backprop(self, num_keys: int, keys: int, grads: int,
                    unique_keys: int, output_grads: int, stream: int) -> int
```

**Parameters**:
- `num_keys`: Number of embedding IDs in the forward pass
- `keys`: Memory address of embedding IDs
- `grads`: Memory address of upstream gradients
- `unique_keys`: Memory address for output unique key buffer
- `output_grads`: Memory address for output gradient buffer (deduped)
- `stream`: CUDA stream handle

**Returns**: Number of unique keys after deduplication

**Behavior**: Deduplicates embedding IDs and aggregates their gradients. This is essential for efficiently handling repeated IDs in sparse features.

**Sources**: [python/pynve/bindings/binding_layers.hpp:105-160]()

### pooling_backprop

Computes gradients for pooled embeddings.

**Python Signature**:
```python
def pooling_backprop(self, num_keys: int, keys: int, grads: int,
                     unique_keys: int, output_grads: int,
                     pooling_type: int, num_offsets: int, offsets: int,
                     data_type: int, weights: int, stream: int) -> int
```

**Parameters**:
- `num_keys`: Total number of embedding IDs
- `keys`: Memory address of embedding IDs
- `grads`: Memory address of upstream gradients (pooled)
- `unique_keys`: Memory address for output unique keys
- `output_grads`: Memory address for output gradients (expanded)
- `pooling_type`: Pooling operation used in forward pass
- `num_offsets`: Number of offset entries (batch size + 1)
- `offsets`: Memory address of CSR offset array
- `data_type`: Data type of weights
- `weights`: Memory address of weight values (nullable)
- `stream`: CUDA stream handle

**Returns**: Number of unique keys after deduplication

**Behavior**: Distributes pooled gradients back to individual embeddings according to the pooling operation and CSR structure.

**Sources**: [python/pynve/bindings/binding_layers.hpp:162-219]()

**Implementation Detail**: Both backpropagation operations use the `GradientCalculator` template class internally with a maximum run size of 1024 embeddings per batch.

**Sources**: [python/pynve/bindings/binding_layers.hpp:110-122](), [python/pynve/bindings/binding_layers.hpp:344]()

---

## Layer-Specific Python Interfaces

### LinearUVMEmbedding Extensions

The `LinearUVMEmbedding` class provides additional methods for accessing the underlying UVM memory:

```mermaid
graph TB
    LINEAR["LinearUVMEmbedding"]
    
    DLPACK["get_dl_tensor(dtype)<br/>Returns DLPack capsule<br/>:572-591"]
    SAVE["write_tensor_to_stream(stream, name)<br/>Serialize to file<br/>:593-597"]
    LOAD["load_tensor_from_stream(stream, name)<br/>Deserialize from file<br/>:599-603"]
    
    LINEAR --> DLPACK
    LINEAR --> SAVE
    LINEAR --> LOAD
    
    DLPACK -.->|creates| DLMANAGED["DLManagedTensor<br/>:540-570"]
    SAVE -.->|uses| WRITER["TensorFileFormat::write_tensor_to_stream"]
    LOAD -.->|uses| READER["TensorFileFormat::load_tensor_from_stream"]
```

**Sources**: [python/pynve/bindings/binding_layers.hpp:479-624]()

#### get_dl_tensor

Returns a DLPack tensor capsule for PyTorch interoperability.

**Python Signature**:
```python
def get_dl_tensor(self, dtype: DataType) -> capsule
```

**Parameters**:
- `dtype`: Data type of the tensor (Float32 or Float16)

**Returns**: Python capsule containing a `DLManagedTensor` pointer

**Usage**: Allows zero-copy access to UVM embeddings from PyTorch:
```python
# Example usage (conceptual)
embedding_layer = LinearUVMEmbedding(...)
capsule = embedding_layer.get_dl_tensor(DataType.Float32)
torch_tensor = torch.from_dlpack(capsule)
```

**Sources**: [python/pynve/bindings/binding_layers.hpp:572-591](), [python/pynve/bindings/binding_layers.hpp:540-570]()

#### Serialization Methods

**write_tensor_to_stream**: Saves embeddings to a file stream
**load_tensor_from_stream**: Loads embeddings from a file stream

**Python Signature**:
```python
def write_tensor_to_stream(self, stream: object, name: int) -> None
def load_tensor_from_stream(self, stream: object, name: int) -> None
```

**Parameters**:
- `stream`: Python file object
- `name`: Tensor identifier (integer key)

**Sources**: [python/pynve/bindings/binding_layers.hpp:593-603]()

### HierarchicalEmbedding Extensions

The `HierarchicalEmbedding` class provides parameter server integration:

#### set_ps_table

Dynamically sets or updates the remote parameter server table.

**Python Signature**:
```python
def set_ps_table(self, table: Table) -> None
```

**Parameters**:
- `table`: Parameter server table implementation (e.g., RedisClusterTable)

**Behavior**: Allows late binding of the parameter server, enabling dynamic configuration after layer initialization.

**Sources**: [python/pynve/bindings/binding_layers.hpp:429-432](), [python/pynve/bindings/binding_layers.hpp:420-422]()

---

## Data Types and Enumerations

### DataType Enumeration

Specifies the precision of embedding values:

| Value | Description | Bytes per Element |
|-------|-------------|-------------------|
| `DataType.Float32` | 32-bit floating point | 4 |
| `DataType.Float16` | 16-bit floating point (half precision) | 2 |
| `DataType.Unknown` | Uninitialized/invalid | N/A |

**Sources**: [python/pynve/bindings/binding_layers.hpp:266](), [python/pynve/bindings/binding_layers.hpp:116]()

### PoolingType Enumeration

Specifies the sparse feature aggregation method:

| Value | Description |
|-------|-------------|
| `PoolingType.Sum` | Sum all embeddings in the group |
| `PoolingType.Mean` | Average all embeddings in the group |
| `PoolingType.Concatenate` | Concatenate embeddings (no aggregation) |

**Sources**: [python/pynve/bindings/binding_layers.hpp:86](), [python/pynve/bindings/binding_layers.hpp:155-156]()

### CacheType String Values

Configuration strings for selecting the caching strategy:

| Value | Maps To | Description |
|-------|---------|-------------|
| `"NoCache"` | `GPUEmbedding` | All embeddings in GPU memory |
| `"LinearUVM"` | `LinearUVMEmbedding` | GPU cache + UVM storage |
| `"Hierarchical"` | `HierarchicalEmbedding` | Multi-tier cache hierarchy |

**Sources**: [README.md:12-15]()

---

## Memory Management

### Execution Context System

The Python bindings automatically manage execution contexts per CUDA stream:

```mermaid
graph TB
    subgraph "Stream-Context Mapping"
        STREAM1["CUDA Stream 1"]
        STREAM2["CUDA Stream 2"]
        STREAMN["CUDA Stream N"]
        
        CTX1["ExecutionContext 1<br/>lookup_stream: Stream 1<br/>modify_stream: shared"]
        CTX2["ExecutionContext 2<br/>lookup_stream: Stream 2<br/>modify_stream: shared"]
        CTXN["ExecutionContext N<br/>lookup_stream: Stream N<br/>modify_stream: shared"]
        
        STREAM1 --> CTX1
        STREAM2 --> CTX2
        STREAMN --> CTXN
    end
    
    subgraph "Shared Resources"
        MODIFY["Shared Modify Stream<br/>modify_stream_<br/>:280"]
        MAP["stream_ctx_map_<br/>std::map&lt;cudaStream_t, ExecutionContext&gt;<br/>:355"]
    end
    
    CTX1 -.->|uses| MODIFY
    CTX2 -.->|uses| MODIFY
    CTXN -.->|uses| MODIFY
    
    GET_CTX["get_exec_context(stream)<br/>:308-321"]
    
    GET_CTX --> MAP
    GET_CTX -.->|creates if missing| CTX1
```

**Key Points**:
- Each CUDA stream gets its own `ExecutionContext`
- All contexts share a single modify stream for write operations
- Context creation is lazy and automatic
- Contexts are destroyed when the layer is destroyed

**Sources**: [python/pynve/bindings/binding_layers.hpp:308-321](), [python/pynve/bindings/binding_layers.hpp:280](), [python/pynve/bindings/binding_layers.hpp:355-356]()

### Resource Lifecycle

The binding classes manage GPU resources with RAII semantics:

```mermaid
graph TB
    CONSTRUCT["Constructor<br/>:266-283"]
    ALLOCATE["Allocate Resources<br/>- modify_stream_<br/>- h_num_runs_out_<br/>- temporary buffers"]
    
    USE["Operations<br/>lookup, update, etc."]
    
    RELEASE["release_contexts()<br/>:298-306"]
    WAIT["Wait on streams<br/>ctx->wait()"]
    DESTROY["Destructor<br/>:285-295"]
    FREE["Free Resources<br/>- Free host memory<br/>- Destroy CUDA streams"]
    
    CONSTRUCT --> ALLOCATE
    ALLOCATE --> USE
    USE --> DESTROY
    DESTROY --> RELEASE
    RELEASE --> WAIT
    WAIT --> FREE
```

**Memory Allocations**:
- `h_num_runs_out_`: Host memory for tracking unique runs (2 x sizeof(IndexT))
- `d_tmp_device_buf_`: Resizable device memory for gradient computation
- `d_tmp_host_buf_`: Resizable host memory for gradient computation
- `modify_stream_`: Dedicated CUDA stream for modify operations

**Sources**: [python/pynve/bindings/binding_layers.hpp:266-295](), [python/pynve/bindings/binding_layers.hpp:298-306]()

---

## PyTorch Integration Patterns

### Tensor Interoperability

The Python API integrates with PyTorch through multiple mechanisms:

```mermaid
graph TB
    subgraph "PyTorch Tensors"
        TORCH_IN["Input Tensor<br/>torch.Tensor"]
        TORCH_OUT["Output Tensor<br/>torch.Tensor"]
    end
    
    subgraph "NVEmbedding Operations"
        NVE["NVEmbedding"]
        LOOKUP["lookup(num_keys, keys_ptr, out_ptr, stream)"]
        BACKPROP["concat_backprop/pooling_backprop"]
    end
    
    subgraph "Memory Pointers"
        PTR_IN["keys_ptr = tensor.data_ptr()"]
        PTR_OUT["out_ptr = tensor.data_ptr()"]
    end
    
    subgraph "CUDA Stream"
        STREAM["torch.cuda.current_stream().cuda_stream"]
    end
    
    TORCH_IN --> PTR_IN
    TORCH_OUT --> PTR_OUT
    
    PTR_IN --> LOOKUP
    PTR_OUT --> LOOKUP
    STREAM --> LOOKUP
    
    LOOKUP --> NVE
    BACKPROP --> NVE
    
    NVE -.->|modifies| TORCH_OUT
```

**Usage Pattern**:
```python
# Conceptual example
import torch
import nve

embedding_layer = nve.NVEmbedding(...)
keys = torch.tensor([1, 2, 3], dtype=torch.int64, device='cuda')
output = torch.empty((3, embedding_dim), dtype=torch.float32, device='cuda')
stream = torch.cuda.current_stream().cuda_stream

embedding_layer.lookup(
    num_keys=len(keys),
    keys=keys.data_ptr(),
    output=output.data_ptr(),
    stream=stream
)
```

**Sources**: [python/pynve/bindings/binding_layers.hpp:61-76]()

### DLPack Zero-Copy Access

For `LinearUVMEmbedding`, the entire embedding table can be accessed as a PyTorch tensor without copying:

```mermaid
graph LR
    UVM["UVM Memory<br/>Embedding Table"]
    
    DLPACK["DLPack Capsule<br/>get_dl_tensor()"]
    
    TORCH["torch.from_dlpack(capsule)"]
    
    TENSOR["PyTorch Tensor<br/>Zero-copy view"]
    
    UVM --> DLPACK
    DLPACK --> TORCH
    TORCH --> TENSOR
    
    TENSOR -.->|"shared memory"| UVM
```

**Tensor Structure**:
- Shape: `[num_embeddings, embedding_dim]`
- Device: CUDA device specified during layer creation
- Memory: Backed by UVM (accessible from both CPU and GPU)
- Lifetime: Managed by the DLManagedTensor deleter

**Sources**: [python/pynve/bindings/binding_layers.hpp:540-591]()

---

## Advanced Features

### Hit Rate Logging

The SDK provides automatic hit rate logging for monitoring cache performance:

```python
config = EmbedLayerConfig()
config.logging_interval = 100  # Log every 100 lookups

embedding_layer = NVEmbedding(..., config=config)
```

**Logged Metrics**:
- Hit rate at each cache level (GPU, Host, Remote)
- Printed via `NVE_LOG_PERF_` macro

**Sources**: [python/pynve/bindings/binding_layers.hpp:324-341](), [python/pynve/bindings/binding_layers.hpp:51]()

### Custom Kernel Modes

For `LinearUVMEmbedding`, specialized kernel execution modes can improve performance:

```python
from nve import KernelType

config = EmbedLayerConfig()
config.kernel_mode = KernelType.PipelineGather
config.kernel_mode_value_1 = 2048  # Task size
config.kernel_mode_value_2 = 32    # Number of auxiliary streams

embedding_layer = LinearUVMEmbedding(..., config=config)
```

**Available Kernel Modes**:
1. **Default Kernel** (mode=0): Standard gather operation
2. **SortGather**: Sort keys before gathering to improve memory access patterns
3. **PipelineGather**: Pipeline gather operations across multiple streams

**Sources**: [python/pynve/bindings/binding_layers.hpp:516-526]()

### Private Streams

Both `LinearUVMEmbedding` and `HierarchicalEmbedding` support private CUDA streams for overlapping operations:

```python
embedding_layer = LinearUVMEmbedding(..., use_private_stream=True)
```

**Benefits**:
- GPU cache operations can proceed independently of user streams
- Better concurrency for multi-threaded inference
- Automatic synchronization when needed

**Sources**: [python/pynve/bindings/binding_layers.hpp:390-394](), [python/pynve/bindings/binding_layers.hpp:507-511]()

### Dynamic Buffer Management

The binding layer automatically resizes temporary buffers for gradient computation:

```mermaid
graph TB
    CALL["concat_backprop/<br/>pooling_backprop called"]
    
    CHECK{"num_keys ><br/>max_num_keys_?"}
    
    RESIZE["Resize Buffers<br/>GetAllocRequirements<br/>SetAndInitBuffers<br/>:115-121"]
    
    COMPUTE["Compute Gradients<br/>GradientCalculator::ComputeGradients<br/>:130-158"]
    
    REUSE["Reuse Existing Buffers"]
    
    CALL --> CHECK
    CHECK -->|Yes| RESIZE
    CHECK -->|No| REUSE
    RESIZE --> COMPUTE
    REUSE --> COMPUTE
```

**Memory Pools**:
- `d_tmp_device_buf_`: Device memory (managed by `ResizeableBuffer`)
- `d_tmp_host_buf_`: Pinned host memory (managed by `ResizeableBuffer`)

**Sources**: [python/pynve/bindings/binding_layers.hpp:113-122](), [python/pynve/bindings/binding_layers.hpp:351-352]()

---

## Type Safety and Index Types

All Python binding classes are templated on the index type `IndexT`, which is typically `int64_t` for PyTorch compatibility:

```mermaid
graph TB
    subgraph "Template Instantiations"
        BIND_INT32["NVEmbedBinding&lt;int32_t&gt;"]
        BIND_INT64["NVEmbedBinding&lt;int64_t&gt;"]
    end
    
    subgraph "Python Exposure"
        PY_INT32["pynve.NVEmbedding_Int32"]
        PY_INT64["pynve.NVEmbedding_Int64"]
    end
    
    BIND_INT32 -.->|"pybind11"| PY_INT32
    BIND_INT64 -.->|"pybind11"| PY_INT64
    
    TORCH["PyTorch Default<br/>torch.int64"]
    
    TORCH -.->|"typically uses"| PY_INT64
```

**Key Considerations**:
- PyTorch uses `int64_t` for indices by default
- Ensure consistency between PyTorch tensors and NVEmbedding index type
- 32-bit indices reduce memory overhead but limit to 2^31 embeddings

**Sources**: [python/pynve/bindings/binding_layers.hpp:57](), [python/pynve/bindings/binding_layers.hpp:363](), [python/pynve/bindings/binding_layers.hpp:479](), [python/pynve/bindings/binding_layers.hpp:627]()

---

## Error Handling

The Python bindings propagate C++ exceptions to Python through pybind11:

```mermaid
graph TB
    PY["Python Call<br/>embedding_layer.lookup(...)"]
    
    BIND["C++ Binding<br/>NVEmbedBinding::lookup"]
    
    CHECK{"Error?"}
    
    NVE_CHECK["NVE_CHECK_ macro<br/>throws std::runtime_error"]
    
    PYBIND["pybind11 Exception Handler"]
    
    PY_EXC["Python Exception<br/>RuntimeError"]
    
    SUCCESS["Return to Python"]
    
    PY --> BIND
    BIND --> CHECK
    CHECK -->|Error| NVE_CHECK
    CHECK -->|Success| SUCCESS
    NVE_CHECK --> PYBIND
    PYBIND --> PY_EXC
```

**Common Exceptions**:
- `RuntimeError`: CUDA errors, invalid parameters, memory allocation failures
- `ValueError`: Invalid configuration (caught at Python layer if applicable)

**Best Practices**:
- Always check CUDA stream synchronization status after operations
- Validate tensor shapes and data types before passing pointers
- Use proper RAII patterns for resource management

**Sources**: [python/pynve/bindings/binding_layers.hpp:280](), [python/pynve/bindings/binding_layers.hpp:393]()

---

This Python API reference provides the foundation for building embedding-based recommender systems with the NV Embedding Cache SDK. For practical examples, see the samples in [samples/pytorch/](). For advanced usage patterns including multi-GPU deployment and Triton integration, see [Advanced Topics](#8).

---

