<!-- source: DeepWiki mcp.deepwiki.com · repo mit-han-lab/torchsparse · page 4 Functional API · fetched 2026-10-30 -->

# Functional API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [torchsparse/nn/functional/__init__.py](torchsparse/nn/functional/__init__.py)

</details>



## Purpose and Scope

The Functional API in TorchSparse provides low-level operations for manipulating point cloud data and sparse tensors. These functions serve as the foundational building blocks upon which the higher-level neural network modules are built. The Functional API enables efficient point cloud processing through operations such as voxelization, devoxelization, hashing, and quantization.

For information about neural network modules that use these functional operations, see [Neural Network Modules](#3). For details about the SparseTensor data structure that these functions operate on, see [SparseTensor Data Structure](#2.1).

Sources: [torchsparse/nn/functional/__init__.py:1-10]()

## Functional Operations Overview

The Functional API includes several categories of operations that can be directly applied to point clouds and sparse tensors:

```mermaid
graph TD
    A["Functional API"] --> B["Voxelization/Devoxelization"]
    A --> C["Hashing/Quantization"]
    A --> D["Spatial Operations"]
    A --> E["Feature Computation"]
    
    B --> B1["voxelize"]
    B --> B2["point_to_voxel"]
    B --> B3["devoxelize"]
    
    C --> C1["hash_table"]
    C --> C2["kernel_hash_query"]
    C --> C3["sparse_quantize"]
    
    D --> D1["sparse_crop"]
    D --> D2["downsample"]
    
    E --> E1["sparse_conv"]
    E --> E2["count_neighbors"]
    E --> E3["activation functions"]
    E --> E4["pooling operations"]
    E --> E5["query operations"]
```

These functional operations form the foundation of TorchSparse's processing capabilities, allowing for efficient manipulation of sparse 3D data.

Sources: [torchsparse/nn/functional/__init__.py:1-10]()

## Relation to Processing Pipeline

In the TorchSparse processing pipeline, functional operations are applied at different stages:

```mermaid
flowchart LR
    A["Raw Point Cloud"] --> B["sparse_quantize"]
    B --> C["SparseTensor Creation"]
    C --> D["Neural Network Processing"]
    D --> E["Feature Extraction"]
    
    subgraph "Functional API Operations"
        B
        F["voxelize/point_to_voxel"]
        G["hash_table"]
        H["downsample"]
        I["sparse_crop"]
        J["devoxelize"]
    end
    
    A --> F
    F --> C
    C --> G
    C --> H
    C --> I
    D --> J
    J --> E
```

The diagram shows how functional operations are used throughout the point cloud processing workflow, from initial quantization to final feature extraction.

Sources: [torchsparse/nn/functional/__init__.py:1-10]()

## Core Functional Operations

### Voxelization and Devoxelization

Voxelization converts continuous point cloud data into a discrete voxel grid representation, while devoxelization performs the reverse operation.

```mermaid
graph TD
    A["Point Cloud <br> (x,y,z coordinates)"] --> B["voxelize()"]
    B --> C["Voxel Grid <br> (SparseTensor)"]
    C --> D["Neural Network <br> Processing"]
    D --> E["devoxelize()"]
    E --> F["Point Features"]
    
    subgraph "Voxelization Process"
        G["Input Points"] --> H["Quantize Points"]
        H --> I["Aggregate Features"]
        I --> J["Create SparseTensor"]
    end
    
    subgraph "Devoxelization Process"
        K["Processed Voxels"] --> L["Map Voxels to Points"]
        L --> M["Interpolate Features"]
        M --> N["Point-wise Features"]
    end
```

Voxelization functions include:
- `voxelize`: Converts points to voxels
- `point_to_voxel`: Maps points to voxel indices
- `devoxelize`: Converts voxels back to point features

Sources: [torchsparse/nn/functional/__init__.py:5-9]()

### Hashing and Quantization

Hashing and quantization are fundamental operations for efficient sparse tensor processing. These functions enable fast neighbor finding and coordinate space discretization.

```mermaid
graph TD
    A["Continuous Coordinates"] --> B["sparse_quantize()"]
    B --> C["Discrete Coordinates"]
    C --> D["hash_table()"]
    D --> E["Hash Table"]
    E --> F["kernel_hash_query()"]
    F --> G["Neighbor Indices"]
    
    subgraph "Hash Table Structure"
        H["Coordinate Hash"] --> I["Voxel Index"]
        J["Key-Value Pairs"] --> K["O(1) Lookup"]
    end
```

Key hashing and quantization functions:
- `sparse_quantize`: Discretizes continuous coordinates
- `hash_table`: Creates a hash table for fast coordinate lookup
- `kernel_hash_query`: Queries the hash table for neighbor finding

Sources: [torchsparse/nn/functional/__init__.py:6]()

### Spatial Operations

Spatial operations manipulate the geometry of sparse tensors through operations like cropping and downsampling.

```mermaid
graph TD
    A["Input SparseTensor"] --> B["sparse_crop()"]
    A --> C["downsample()"]
    
    B --> D["Cropped SparseTensor"]
    C --> E["Downsampled SparseTensor"]
    
    subgraph "Cropping Process"
        F["Define Crop Region"] --> G["Filter Coordinates"]
        G --> H["Select Features"]
    end
    
    subgraph "Downsampling Process"
        I["Increase Stride"] --> J["Aggregate Features"]
        J --> K["Reduce Resolution"]
    end
```

Key spatial operations:
- `sparse_crop`: Extracts a spatial region from a sparse tensor
- `downsample`: Reduces the resolution of a sparse tensor by increasing stride

Sources: [torchsparse/nn/functional/__init__.py:4]()

## Feature Computation Operations

Feature computation operations process the features of sparse tensors without changing their spatial structure.

```mermaid
graph TD
    A["Input SparseTensor"] --> B["sparse_conv()"]
    A --> C["count_neighbors()"]
    A --> D["Activation Functions"]
    A --> E["Pooling Operations"]
    
    B --> F["Convolved Features"]
    C --> G["Neighbor Count Tensor"]
    D --> H["Activated Features"]
    E --> I["Pooled Features"]
    
    subgraph "Convolution Process"
        J["Find Neighbors"] --> K["Gather Features"]
        K --> L["Apply Kernel"]
        L --> M["Scatter Results"]
    end
```

Feature computation functions include:
- Sparse convolution operations
- Activation functions (ReLU, LeakyReLU, etc.)
- Pooling operations (max pooling, average pooling)
- Count operations for neighborhood analysis

Sources: [torchsparse/nn/functional/__init__.py:1-3]()

## Code Structure and Organization

The functional API is organized into several Python modules within the TorchSparse codebase:

```mermaid
classDiagram
    class TorchSparse_Functional_API {
        +activation.py
        +conv.py
        +count.py
        +crop.py
        +devoxelize.py
        +hash.py
        +pooling.py
        +query.py
        +voxelize.py
    }
    
    class activation {
        +relu()
        +leaky_relu()
    }
    
    class voxelize {
        +voxelize()
        +point_to_voxel()
    }
    
    class devoxelize {
        +devoxelize()
    }
    
    class hash {
        +hash_table()
        +kernel_hash_query()
        +sparse_quantize()
    }
    
    class crop {
        +sparse_crop()
    }
    
    class conv {
        +sparse_conv()
    }
    
    class count {
        +count_neighbors()
    }
    
    class pooling {
        +sparse_max_pool()
        +sparse_avg_pool()
    }
    
    class query {
        +sparse_query()
    }
    
    TorchSparse_Functional_API --> activation
    TorchSparse_Functional_API --> voxelize
    TorchSparse_Functional_API --> devoxelize
    TorchSparse_Functional_API --> hash
    TorchSparse_Functional_API --> crop
    TorchSparse_Functional_API --> conv
    TorchSparse_Functional_API --> count
    TorchSparse_Functional_API --> pooling
    TorchSparse_Functional_API --> query
```

Each module in the functional API contains related operations and is imported through the `__init__.py` file to provide a unified interface.

Sources: [torchsparse/nn/functional/__init__.py:1-10]()

## Functional API vs. Module API

The TorchSparse library provides both a functional API and a module API. The relationship between them is illustrated below:

```mermaid
graph TD
    A["TorchSparse Library"] --> B["Functional API"]
    A --> C["Module API"]
    
    B --> B1["Low-level operations"]
    B --> B2["Direct tensor manipulation"]
    
    C --> C1["OOP interfaces"]
    C --> C2["Stateful operations"]
    
    B1 --> D["voxelize(), devoxelize()"]
    B1 --> E["hash_table(), sparse_quantize()"]
    B1 --> F["sparse_conv(), sparse_crop()"]
    
    C1 --> G["Conv3d, Pool3d"]
    C1 --> H["ToBEVConvolution"]
    C1 --> I["SparseNorm, BatchNorm"]
    
    J["Backbone Networks"] --> C
    C --> B
```

The functional API provides the core building blocks that are used by the module API to implement higher-level neural network components.

| API Type | Characteristics | Example Operations | Usage Context |
|----------|----------------|-------------------|---------------|
| Functional API | Stateless, Pure functions | `voxelize()`, `sparse_quantize()` | Direct tensor manipulation, Custom operations |
| Module API | Stateful, OOP interfaces | `Conv3d`, `Pool3d` | Neural network building, Training loops |

Sources: [torchsparse/nn/functional/__init__.py:1-10]()

## Summary

The TorchSparse Functional API provides the fundamental operations needed for efficient point cloud processing. These operations include:

1. Voxelization and devoxelization for converting between point clouds and voxel grids
2. Hashing and quantization for efficient neighbor finding and coordinate processing
3. Spatial operations like cropping and downsampling for manipulating tensor geometry
4. Feature computation operations for processing sparse tensor features

These functional operations form the foundation upon which the higher-level neural network modules are built. For more detailed information on specific operations, refer to the dedicated pages:
- [Voxelization and Devoxelization](#4.1)
- [Hashing and Quantization](#4.2)
- [Downsampling and Cropping](#4.3)

Sources: [torchsparse/nn/functional/__init__.py:1-10]()

---

