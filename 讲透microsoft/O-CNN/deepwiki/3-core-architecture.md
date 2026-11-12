<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/O-CNN · page 3 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [octree/octree/octree.cpp](octree/octree/octree.cpp)
- [octree/octree/octree_nn.cpp](octree/octree/octree_nn.cpp)
- [octree/octree/octree_nn.cu](octree/octree/octree_nn.cu)
- [octree/octree/octree_nn.h](octree/octree/octree_nn.h)
- [octree/octree/octree_parser.cpp](octree/octree/octree_parser.cpp)
- [octree/octree/octree_parser.h](octree/octree/octree_parser.h)
- [octree/test/test_util.cpp](octree/test/test_util.cpp)
- [octree/tools/chamfer_distance.cpp](octree/tools/chamfer_distance.cpp)
- [octree/tools/octree_bbox.cpp](octree/tools/octree_bbox.cpp)

</details>



This document explains the fundamental data structures and neural network operations that form the foundation of the O-CNN system. The core architecture provides the essential octree data structures, specialized neural network operations for processing octree data, and unified interfaces for accessing octree properties across CPU and GPU execution contexts.

For information about framework-specific integrations (TensorFlow, PyTorch, Caffe), see [Framework Integration](#4). For details about octree construction and point cloud processing, see [Point Cloud Processing](#3.3).

## System Overview

The O-CNN core architecture is built around three primary components: the octree data structure itself, specialized neural network operations that can process octree data efficiently, and a unified parser interface that provides consistent access to octree properties.

### Core Architecture Components

```mermaid
graph TB
    subgraph "Core Data Structures"
        Octree["Octree<br/>octree.cpp"]
        OctreeInfo["OctreeInfo<br/>octree_info.h"]
        OctreeParser["OctreeParser<br/>octree_parser.cpp"]
    end
    
    subgraph "Neural Network Operations"
        OctreeNN["OctreeNN Operations<br/>octree_nn.cpp/cu"]
        O2C["octree2col_gpu/cpu"]
        C2O["col2octree_gpu/cpu"]
        MaxPool["octree_max_pool_gpu/cpu"]
        NeighCalc["calc_neigh_gpu/cpu"]
    end
    
    subgraph "Memory Management"
        CPUPtr["CPU Pointers<br/>ptr_cpu()"]
        GPUPtr["GPU Pointers<br/>ptr_gpu()"]
        MemOps["memset/memcpy<br/>CPU/GPU variants"]
    end
    
    subgraph "Key Operations"
        KeyOps["Key/Coordinate<br/>Conversions"]
        KeyXYZ["key2xyz_gpu/cpu"]
        XYZKey["xyz2key_gpu/cpu"]
        ComputeKey["compute_key()"]
    end
    
    Octree --> OctreeInfo
    Octree --> OctreeParser
    OctreeParser --> CPUPtr
    OctreeParser --> GPUPtr
    
    OctreeNN --> O2C
    OctreeNN --> C2O
    OctreeNN --> MaxPool
    OctreeNN --> NeighCalc
    
    O2C --> KeyOps
    C2O --> KeyOps
    NeighCalc --> KeyOps
    
    KeyOps --> KeyXYZ
    KeyOps --> XYZKey
    KeyOps --> ComputeKey
    
    CPUPtr --> MemOps
    GPUPtr --> MemOps
```

Sources: [octree/octree/octree.cpp:1-1569](), [octree/octree/octree_nn.h:1-255](), [octree/octree/octree_parser.h:1-86]()

## Fundamental Data Structures

### Octree Class

The `Octree` class serves as the primary container for octree data and provides methods for building, serializing, and manipulating octree structures.

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| `buffer_` | Raw octree data storage | `resize_octree()`, `get_binary_string()` |
| `keys_` | Spatial keys for each level | `sort_keys()`, `unique_key()` |
| `children_` | Child node relationships | `build_structure()` |
| `avg_normals_`, `avg_features_` | Averaged node properties | `calc_signal()` |

The octree building process follows this workflow:

```mermaid
graph LR
    Points["Point Cloud<br/>Points class"] --> Normalize["normalize_pts()<br/>Scale to depth range"]
    Normalize --> SortKeys["sort_keys()<br/>Compute spatial keys"]
    SortKeys --> BuildStruct["build_structure()<br/>Create hierarchy"]
    BuildStruct --> CalcSignal["calc_signal()<br/>Average properties"]
    CalcSignal --> Serialize["serialize()<br/>Pack into buffer_"]
    
    subgraph "Key Operations"
        ComputeKey["compute_key()<br/>Point to key"]
        UniqueKey["unique_key()<br/>Remove duplicates"]
    end
    
    SortKeys --> ComputeKey
    SortKeys --> UniqueKey
```

Sources: [octree/octree/octree.cpp:74-121](), [octree/octree/octree.cpp:172-203](), [octree/octree/octree.cpp:205-283]()

### OctreeParser Interface

The `OctreeParser` class provides a unified interface for accessing octree data across different execution contexts, supporting both CPU and GPU memory layouts.

```mermaid
graph TB
    subgraph "OctreeParser Interface"
        SetCPU["set_cpu()<br/>Initialize CPU pointers"]
        SetGPU["set_gpu()<br/>Initialize GPU pointers"]
        
        subgraph "Property Accessors"
            KeyCPU["key_cpu(depth)"]
            ChildrenCPU["children_cpu(depth)"]
            FeatureCPU["feature_cpu(depth)"]
            NeighborCPU["neighbor_cpu(depth)"]
        end
        
        subgraph "GPU Equivalents"
            KeyGPU["key_gpu(depth)"]
            ChildrenGPU["children_gpu(depth)"]
            FeatureGPU["feature_gpu(depth)"]
            NeighborGPU["neighbor_gpu(depth)"]
        end
        
        subgraph "Mutable Access"
            MutablePtr["mutable_ptr_cpu/gpu()"]
            MutableKey["mutable_key_cpu/gpu()"]
        end
    end
    
    SetCPU --> KeyCPU
    SetCPU --> ChildrenCPU
    SetGPU --> KeyGPU
    SetGPU --> ChildrenGPU
    
    KeyCPU --> MutableKey
    KeyGPU --> MutableKey
```

Sources: [octree/octree/octree_parser.cpp:8-91](), [octree/octree/octree_parser.h:13-83]()

## Neural Network Operations

### Core Convolution Operations

The heart of octree-based CNNs lies in the `octree2col` and `col2octree` operations, which enable efficient convolution by transforming octree data into a format suitable for standard matrix operations.

#### octree2col Operation

```mermaid
graph LR
    subgraph "octree2col Process"
        OctreeData["Octree Data<br/>data_octree[channel][height]"]
        NeighborLookup["Neighbor Lookup<br/>neigh[node_id * 64]"]
        KernelIndex["Kernel Index<br/>ni[kernel_pos]"]
        ColData["Column Data<br/>data_col[channel][kernel][height]"]
    end
    
    OctreeData --> NeighborLookup
    NeighborLookup --> KernelIndex
    KernelIndex --> ColData
    
    subgraph "Implementation Variants"
        CPU["octree2col_cpu<br/>Sequential processing"]
        GPU["octree2col_gpu<br/>Parallel CUDA kernels"]
        Pooling["octree2colP_cpu/gpu<br/>With pooling support"]
    end
    
    ColData --> CPU
    ColData --> GPU
    ColData --> Pooling
```

The `octree2col_kernel` implementation processes each thread in parallel:

| Parameter | Purpose | Range |
|-----------|---------|-------|
| `height` | Current octree level height | `[0, node_count]` |
| `kernel_sdim` | Kernel spatial dimension | Typically 27 for 3³ kernel |
| `stride` | Convolution stride | 1 or 2 |
| `neigh` | Neighborhood lookup table | 64 entries per node |
| `ni` | Kernel index mapping | Maps kernel positions to neighbor indices |

Sources: [octree/octree/octree_nn.cu:109-159](), [octree/octree/octree_nn.cpp:188-241]()

#### Neighborhood Calculation

The `NeighHelper` singleton manages kernel patterns and neighborhood relationships:

```mermaid
graph TB
    subgraph "NeighHelper Singleton"
        InitNeigh["init_neigh_index()<br/>Initialize kernel patterns"]
        
        subgraph "Kernel Types"
            K333["333: 27-point kernel<br/>3x3x3 neighborhood"]
            K111["111: 1-point kernel<br/>Center only"]
            K222["222: 8-point kernel<br/>Octant corners"]
        end
        
        subgraph "Lookup Tables"
            NIMap["ni_map_<br/>Kernel name to index"]
            ParentArray["parent_<br/>Parent node mapping"]
            DisArray["displacement_<br/>Spatial offsets"]
        end
    end
    
    InitNeigh --> K333
    InitNeigh --> K111
    InitNeigh --> K222
    
    K333 --> NIMap
    K111 --> NIMap
    K222 --> NIMap
    
    NIMap --> ParentArray
    NIMap --> DisArray
```

Sources: [octree/octree/octree_nn.cpp:6-108](), [octree/octree/octree_nn.h:15-47]()

### Pooling Operations

Octree-specific pooling operations maintain the hierarchical structure while downsampling features:

```mermaid
graph LR
    subgraph "Max Pooling"
        Input["Input Data<br/>btm_data[channel][8*height]"]
        MaxPool["octree_max_pool_kernel<br/>Find max in each octant"]
        Output["Output Data<br/>top_data[channel][height]"]
        Mask["Mask Data<br/>mask[channel][height]"]
    end
    
    Input --> MaxPool
    MaxPool --> Output
    MaxPool --> Mask
    
    subgraph "Unpooling"
        UnpoolInput["top_data + mask"]
        Unpool["octree_max_unpool_kernel<br/>Restore spatial positions"]
        UnpoolOutput["btm_data"]
    end
    
    Output --> UnpoolInput
    Mask --> UnpoolInput
    UnpoolInput --> Unpool
    Unpool --> UnpoolOutput
```

The pooling operations exploit the octree's natural 8-to-1 hierarchy where each parent node corresponds to exactly 8 children nodes.

Sources: [octree/octree/octree_nn.cu:257-327](), [octree/octree/octree_nn.cpp:301-354]()

## Key and Coordinate Systems

### Spatial Key Encoding

The system uses a sophisticated key encoding scheme to map 3D coordinates to linear indices that preserve spatial locality:

```mermaid
graph TB
    subgraph "Key Encoding Process"
        XYZ["3D Coordinates<br/>(x, y, z, batch_id)"]
        Morton["Morton Encoding<br/>Interleave bits"]
        Key["Spatial Key<br/>uintk format"]
        
        subgraph "Bit Layout"
            X["X bits: positions 2,5,8..."]
            Y["Y bits: positions 1,4,7..."]
            Z["Z bits: positions 0,3,6..."]
            Batch["Batch ID: high bits"]
        end
    end
    
    XYZ --> Morton
    Morton --> Key
    
    Morton --> X
    Morton --> Y  
    Morton --> Z
    Morton --> Batch
    
    subgraph "Operations"
        ComputeKey["compute_key()<br/>xyz → key"]
        ComputePt["compute_pt()<br/>key → xyz"]
        XYZ2Key["xyz2key_cpu/gpu()"]
        Key2XYZ["key2xyz_cpu/gpu()"]
    end
    
    Key --> ComputeKey
    Key --> ComputePt
    Key --> XYZ2Key
    Key --> Key2XYZ
```

The key encoding ensures that spatially adjacent octree nodes have similar key values, enabling efficient neighbor lookup and spatial operations.

Sources: [octree/octree/octree_nn.cpp:551-575](), [octree/octree/octree_nn.cu:593-649]()

## Memory Management and Device Abstraction

The architecture provides consistent interfaces across CPU and GPU execution contexts through template-based memory operations:

| Operation | CPU Version | GPU Version | Purpose |
|-----------|-------------|-------------|---------|
| Memory Set | `memset_cpu<T>()` | `memset_gpu<T>()` | Initialize arrays |
| Memory Copy | `memcpy_cpu<T>()` | `memcpy_gpu<T>()` | Transfer data |
| Padding | `pad_forward_cpu<T>()` | `pad_forward_gpu<T>()` | Handle sparse data |
| Gather/Scatter | `align_forward_gpu<T>()` | `octree_gather_gpu<T>()` | Reorder data |

The GPU implementations use CUDA kernels with thread-level parallelism, while CPU versions provide sequential fallbacks for debugging and smaller datasets.

Sources: [octree/octree/octree_nn.cu:38-106](), [octree/octree/octree_nn.cpp:143-185](), [octree/octree/octree_nn.h:56-78]()

---

