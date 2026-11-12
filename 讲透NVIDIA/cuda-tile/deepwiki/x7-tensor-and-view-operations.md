<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuda-tile · extra page Tensor and View Operations · fetched 2026-10-26 -->

# View and Tile Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [lib/Dialect/CudaTile/IR/CudaTile.cpp](lib/Dialect/CudaTile/IR/CudaTile.cpp)
- [python/cuda_tile/dialects/cuda_tile_ops.py](python/cuda_tile/dialects/cuda_tile_ops.py)

</details>



## Purpose and Scope

This document describes operations in the CudaTile dialect that manipulate views and tiles. These operations enable transformation of tile shapes, broadcasting across dimensions, offsetting views, generating sequential indices, and partitioning tensors into tiled representations. 

View and tile operations work closely with the type system, particularly `TensorViewType`, `PartitionViewType`, and `TileType`. For details on these types, see [Type System](#3.1). For memory operations that load/store using views, see [Memory Operations](#3.3.2).

---

## Overview

View and tile operations provide the foundation for describing tiled tensor computations. They enable:

- **Shape transformation**: Reshaping tiles to different dimensions
- **Broadcasting**: Expanding tiles across dimensions
- **View manipulation**: Applying offsets to tensor views
- **Index generation**: Creating sequential tile indices with iota
- **Partitioning**: Decomposing tensors into tiled partition views

These operations bridge the abstract tile space with concrete memory layout strategies, working through the `TileView` interface to enforce consistent indexing contracts.

**Sources:** [include/cuda_tile/Dialect/CudaTile/IR/Interfaces.td:30-63]()

---

## The TileView Interface

The `TileView` interface is the core abstraction for view operations. It represents a view within a memref from which tiles can be loaded or stored, acting as a converter from abstract tile-space coordinates to tiles.

```mermaid
graph TB
    subgraph "TileView Interface Contract"
        TileViewIface["TileView TypeInterface<br/>mlir::cuda_tile::TileView"]
    end
    
    subgraph "Interface Methods"
        GetIndexRank["getViewIndexRank()<br/>Returns rank of tile indices"]
        GetTileType["getViewTileType()<br/>Returns type of tiles"]
    end
    
    subgraph "Implementing Types"
        PartitionView["PartitionViewType<br/>!cuda_tile.partition_view"]
        TensorView["TensorViewType<br/>!cuda_tile.tensor_view"]
    end
    
    subgraph "Usage Context"
        LoadOp["load_ptr_tko operation<br/>Loads tiles from view"]
        StoreOp["store_ptr_tko operation<br/>Stores tiles to view"]
    end
    
    TileViewIface --> GetIndexRank
    TileViewIface --> GetTileType
    
    PartitionView -.implements.- TileViewIface
    TensorView -.implements.- TileViewIface
    
    LoadOp --> TileViewIface
    StoreOp --> TileViewIface
```

### Interface Contract

The `TileView` interface defines two key methods:

| Method | Return Type | Purpose |
|--------|-------------|---------|
| `getViewIndexRank()` | `size_t` | Returns the rank of tile indices (tile-space coordinates) |
| `getViewTileType()` | `mlir::Type` | Returns the type of tiles loaded from/stored to the view |

**Key invariant:** Views must always access tiles of the same type regardless of the index used. This ensures type consistency across tile operations.

**Sources:** [include/cuda_tile/Dialect/CudaTile/IR/Interfaces.td:30-63]()

---

## View Manipulation Operations

### Reshape Operation

The `reshape` operation transforms the shape of a tile without changing its element count. It enables reinterpretation of tile dimensions for operations requiring different layouts.

```mermaid
graph LR
    subgraph "Input"
        InputTile["Tile<br/>shape: [M, N]<br/>element_type: T"]
    end
    
    subgraph "Reshape Operation"
        ReshapeOp["cuda_tile.reshape<br/>target_shape: [P, Q]<br/>where M × N = P × Q"]
    end
    
    subgraph "Output"
        OutputTile["Tile<br/>shape: [P, Q]<br/>element_type: T"]
    end
    
    InputTile --> ReshapeOp
    ReshapeOp --> OutputTile
```

**Constraints:**
- Total element count must remain constant
- Element type is preserved
- Shape transformation is purely layout reinterpretation

### Broadcast Operation

The `broadcast` operation expands a tile across specified dimensions, replicating values to match a target shape.

```mermaid
graph LR
    subgraph "Input"
        InputTile["Tile<br/>shape: [M]<br/>element_type: T"]
    end
    
    subgraph "Broadcast Operation"
        BroadcastOp["cuda_tile.broadcast<br/>target_shape: [M, N]<br/>broadcast_dim: 1"]
    end
    
    subgraph "Output"
        OutputTile["Tile<br/>shape: [M, N]<br/>element_type: T<br/>values replicated along dim 1"]
    end
    
    InputTile --> BroadcastOp
    BroadcastOp --> OutputTile
```

**Use cases:**
- Expanding scalars or vectors to match matrix dimensions
- Replicating tile values for elementwise operations
- Preparing operands for broadcasting arithmetic

### Offset Operation

The `offset` operation applies a coordinate offset to a view, shifting the tile-space origin for subsequent load/store operations.

```mermaid
graph TB
    subgraph "Original View"
        OrigView["TensorView or PartitionView<br/>base_offset: [0, 0]"]
    end
    
    subgraph "Offset Operation"
        OffsetOp["cuda_tile.offset<br/>offset_values: [dx, dy]"]
    end
    
    subgraph "Offset View"
        NewView["Modified View<br/>effective_offset: [dx, dy]"]
    end
    
    subgraph "Subsequent Operations"
        Load["load_ptr_tko<br/>uses new effective offset"]
        Store["store_ptr_tko<br/>uses new effective offset"]
    end
    
    OrigView --> OffsetOp
    OffsetOp --> NewView
    NewView --> Load
    NewView --> Store
```

**Purpose:**
- Enables sliding window patterns
- Facilitates stencil computations
- Supports relative addressing in tile space

**Sources:** Based on overview diagrams and view operation patterns

---

## Tile Generation Operations

### Iota Operation

The `iota` operation generates a tile containing sequential indices, useful for coordinate-based computations and index generation.

```mermaid
graph TB
    subgraph "Iota Operation"
        IotaOp["cuda_tile.iota<br/>shape: [M, N]<br/>dimension: dim<br/>element_type: index_type"]
    end
    
    subgraph "Output Patterns"
        Dim0["dimension=0:<br/>[0,0,0,...]<br/>[1,1,1,...]<br/>[2,2,2,...]"]
        Dim1["dimension=1:<br/>[0,1,2,...]<br/>[0,1,2,...]<br/>[0,1,2,...]"]
    end
    
    IotaOp --> Dim0
    IotaOp --> Dim1
```

**Generated values:**
- For `dimension=0`: Values increase along rows (first dimension)
- For `dimension=1`: Values increase along columns (second dimension)
- Element type is typically an integer type suitable for indexing

**Common use cases:**
- Generating tile coordinates for index-dependent computations
- Creating masks based on position
- Implementing gather/scatter patterns

**Sources:** Based on architecture overview and tile operation patterns

---

## Partitioning Operations

### Partition Operation

The `partition` operation decomposes a tensor into a tiled representation, creating a `PartitionViewType` that describes how the tensor is divided into tiles. This is a fundamental operation for expressing tiled algorithms.

```mermaid
graph TB
    subgraph "Input Tensor"
        Tensor["TensorViewType<br/>shape: [H, W]<br/>strides: [s0, s1]<br/>element_type: T"]
    end
    
    subgraph "Partition Operation"
        PartitionOp["cuda_tile.partition<br/>tile_shape: [th, tw]<br/>dimension_mapping"]
    end
    
    subgraph "Output Partition View"
        PartView["PartitionViewType<br/>tile_shape: [th, tw]<br/>tile_space: [H/th, W/tw]<br/>element_type: T"]
    end
    
    subgraph "Tile Indexing"
        Index["Tile indices [i, j]<br/>0 ≤ i < H/th<br/>0 ≤ j < W/tw"]
        Access["Access tile at [i,j]<br/>via TileView interface"]
    end
    
    Tensor --> PartitionOp
    PartitionOp --> PartView
    PartView --> Index
    Index --> Access
```

### PartitionViewType Structure

The `PartitionViewType` combines multiple concepts:

| Component | Description |
|-----------|-------------|
| **Tile Shape** | Dimensions of individual tiles (e.g., `[16, 16]`) |
| **Tensor View** | Underlying tensor with stride information |
| **Dimension Mapping** | How tensor dimensions map to tile space |
| **Tile Space Rank** | Number of dimensions in the tiled coordinate system |

**Key properties:**
- Implements the `TileView` interface for uniform access patterns
- Enables load/store operations in tile-space coordinates
- Encodes tiling strategy as part of the type system

```mermaid
graph TB
    subgraph "PartitionViewType Components"
        PVType["PartitionViewType"]
    end
    
    subgraph "Embedded Information"
        TileShape["Tile Shape<br/>[th, tw, ...]"]
        TensorView["TensorViewType<br/>base tensor + strides"]
        DimMap["Dimension Mapping<br/>tensor_dim → tile_dim"]
    end
    
    subgraph "TileView Interface Implementation"
        IndexRank["getViewIndexRank()<br/>returns tile-space rank"]
        TileType["getViewTileType()<br/>returns tile<[th,tw] × T>"]
    end
    
    PVType --> TileShape
    PVType --> TensorView
    PVType --> DimMap
    
    PVType -.implements.- IndexRank
    PVType -.implements.- TileType
```

**Sources:** [include/cuda_tile/Dialect/CudaTile/IR/Interfaces.td:30-63](), architecture overview diagrams

---

## Type Relationships

View and tile operations interact with several key types in the CudaTile type system:

```mermaid
graph TB
    subgraph "Base Types"
        TileType["TileType<br/>tile<shape × element_type>"]
        TensorView["TensorViewType<br/>tensor_view with strides"]
    end
    
    subgraph "View Types (TileView Interface)"
        PartitionView["PartitionViewType<br/>Tiled tensor decomposition"]
        TensorViewDerived["TensorViewType<br/>Strided tensor view"]
    end
    
    subgraph "Operations"
        Reshape["reshape<br/>tile → tile"]
        Broadcast["broadcast<br/>tile → tile"]
        Offset["offset<br/>view → view"]
        Iota["iota<br/>() → tile"]
        Partition["partition<br/>tensor_view → partition_view"]
    end
    
    TileType --> Reshape
    TileType --> Broadcast
    Reshape --> TileType
    Broadcast --> TileType
    
    Iota --> TileType
    
    TensorView --> Partition
    Partition --> PartitionView
    
    PartitionView --> Offset
    TensorViewDerived --> Offset
    Offset --> PartitionView
    
    PartitionView -.implements.- TileViewInterface["TileView Interface"]
    TensorViewDerived -.implements.- TileViewInterface
```

### Type Transformation Summary

| Operation | Input Type | Output Type | Transformation |
|-----------|-----------|-------------|----------------|
| `reshape` | `TileType` | `TileType` | Shape reinterpretation |
| `broadcast` | `TileType` | `TileType` | Dimension expansion |
| `offset` | `TileView` | `TileView` | Coordinate translation |
| `iota` | (none) | `TileType` | Index generation |
| `partition` | `TensorViewType` | `PartitionViewType` | Tiling decomposition |

**Sources:** [include/cuda_tile/Dialect/CudaTile/IR/Interfaces.td:30-63](), architecture overview

---

## Integration with Memory Operations

View and tile operations work in conjunction with memory operations to implement tiled memory access patterns:

```mermaid
graph LR
    subgraph "Setup Phase"
        TensorPtr["Tensor Pointer<br/>ptr<tensor_view>"]
        CreateView["Create tensor_view"]
        PartitionOp["partition operation"]
        PartView["PartitionViewType"]
    end
    
    subgraph "Access Phase"
        OffsetOp["offset operation<br/>(optional)"]
        TileCoord["Tile coordinates [i,j]"]
        LoadOp["load_ptr_tko<br/>Memory operation"]
        Tile["TileType result"]
    end
    
    subgraph "Computation Phase"
        ReshapeOp["reshape<br/>(optional)"]
        BroadcastOp["broadcast<br/>(optional)"]
        Compute["Arithmetic operations"]
    end
    
    subgraph "Write-back Phase"
        StoreOp["store_ptr_tko<br/>Memory operation"]
    end
    
    TensorPtr --> CreateView
    CreateView --> PartitionOp
    PartitionOp --> PartView
    
    PartView --> OffsetOp
    OffsetOp --> LoadOp
    TileCoord --> LoadOp
    LoadOp --> Tile
    
    Tile --> ReshapeOp
    ReshapeOp --> BroadcastOp
    BroadcastOp --> Compute
    
    Compute --> StoreOp
    PartView --> StoreOp
```

This pipeline demonstrates how view operations set up the addressing strategy, tile operations transform loaded data, and memory operations perform the actual data movement. The `TileView` interface ensures consistent type contracts throughout the pipeline.

**Sources:** [include/cuda_tile/Dialect/CudaTile/IR/Interfaces.td:30-63](), [include/cuda_tile/Dialect/CudaTile/IR/Ops.h:33-39]()

---

## Implementation Notes

### Interface Verification

The `TileView` interface enforces critical invariants through its contract methods. Types implementing this interface must correctly implement:

- `getViewIndexRank()`: Must return a consistent rank value that matches the dimensionality expected by load/store operations
- `getViewTileType()`: Must return a `TileType` that remains constant regardless of which tile-space coordinate is accessed

These invariants enable the verifier to catch inconsistencies at IR construction time rather than during execution.

### Type System Integration

View and tile operations are deeply integrated with the CudaTile type system:

- The `TileType` captures shape and element type information
- The `TensorViewType` includes stride information for memory layout
- The `PartitionViewType` combines tiling strategy with tensor layout
- The `TileView` interface provides a uniform abstraction over view types

This layered type system enables the dialect to express complex tiled memory access patterns while maintaining strong type safety.

**Sources:** [include/cuda_tile/Dialect/CudaTile/IR/Interfaces.td:30-63](), [include/cuda_tile/Dialect/CudaTile/IR/Ops.h:1-100]()

---

