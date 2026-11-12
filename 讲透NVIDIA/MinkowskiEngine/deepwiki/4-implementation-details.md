<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/MinkowskiEngine · page 4 Implementation Details · fetched 2026-10-26 -->

# Implementation Details

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [MinkowskiEngine/MinkowskiCoordinateManager.py](MinkowskiEngine/MinkowskiCoordinateManager.py)
- [pybind/extern.hpp](pybind/extern.hpp)
- [src/coordinate_map.hpp](src/coordinate_map.hpp)
- [src/coordinate_map_manager.cpp](src/coordinate_map_manager.cpp)
- [src/coordinate_map_manager.hpp](src/coordinate_map_manager.hpp)
- [src/kernel_region.hpp](src/kernel_region.hpp)
- [src/types.hpp](src/types.hpp)

</details>



This document provides a technical overview of the core architecture and implementation details of MinkowskiEngine. It focuses on the internal design decisions, memory management strategies, and how the Python and C++ layers interact. For information about specific operations like convolutions and pooling, see [Neural Network Operations](#3).

## Architecture Overview

MinkowskiEngine uses a hybrid architecture that combines Python and C++ code to achieve both flexibility and performance. The high-level Python interface provides user-friendly APIs, while the performance-critical operations are implemented in C++ with both CPU and GPU (CUDA) backends.

```mermaid
flowchart TD
    subgraph "Python Layer"
        PythonAPI["Python API Classes"]
        PyMgr["MinkowskiCoordinateManager.py"]
    end
    
    subgraph "Python/C++ Binding"
        Pybind["pybind11 Binding Layer"]
    end
    
    subgraph "C++ Implementation"
        CPPCore["C++ Core Implementation"]
        subgraph "Backend Implementation"
            CPUImpl["CPU Backend"]
            GPUImpl["GPU/CUDA Backend"]
        end
        CoordMgr["CoordinateMapManager"]
        CoordMap["CoordinateMap"]
    end
    
    PythonAPI --> PyMgr
    PyMgr --> Pybind
    Pybind --> CPPCore
    CPPCore --> CoordMgr
    CoordMgr --> CoordMap
    CoordMap --> CPUImpl
    CoordMap --> GPUImpl
```

Sources: [pybind/extern.hpp:1-515](). [MinkowskiEngine/MinkowskiCoordinateManager.py:1-100]().

## Python-C++ Interface Architecture

The Python-C++ interface is implemented using pybind11, which allows for seamless integration between the two languages. The binding code is primarily located in `pybind/extern.hpp`, which defines the functions exposed to Python.

```mermaid
flowchart LR
    subgraph "Python Side"
        PyClass["SparseTensor/TensorField Classes"]
        PyOps["MinkowskiOps Functions"]
        PyMgr["CoordinateManager Class"]
    end
    
    subgraph "Binding Layer"
        PYBIND["PYBIND11_MODULE"]
        PyTypes["Python Type Converters"]
        TemplateInst["Template Instantiation"]
    end
    
    subgraph "C++ Side"
        CPPFuncs["C++ Implementation Functions"]
        CPPClasses["C++ Core Classes"]
        KeyTypes["Coordinate Map Keys & Types"]
    end
    
    PyClass --> PYBIND
    PyOps --> PYBIND
    PyMgr --> PYBIND
    
    PYBIND --> PyTypes
    PYBIND --> TemplateInst
    
    PyTypes --> CPPFuncs
    TemplateInst --> CPPFuncs
    TemplateInst --> CPPClasses
    CPPClasses --> KeyTypes
```

The interface follows a template-based approach to support different coordinate data types (e.g., `int32_t` for sparse tensors) and coordinate field types (e.g., `float` for continuous coordinates).

Key components in the binding layer:

1. **Type Definitions**: Various type definitions (in `types.hpp`) enable consistent data handling across the Python-C++ boundary.
2. **Template Instantiation**: Functions like `instantiate_cpu_func()` and `instantiate_gpu_func()` create the necessary template instances for different coordinate types.
3. **Exposed Classes**: Core classes like `CoordinateMapKey` and `CoordinateMapManager` are exposed directly to Python.

Sources: [pybind/extern.hpp:49-515](). [pybind/extern.hpp:513-668](). [src/types.hpp:37-106]().

## Coordinate System Implementation

The coordinate system is the foundation of MinkowskiEngine, managing sparse tensor coordinates efficiently.

```mermaid
flowchart TD
    subgraph "Coordinate System Components"
        CoordKey["CoordinateMapKey"]
        CoordMap["CoordinateMap"]
        CoordMgr["CoordinateMapManager"]
        KernelRegion["KernelRegion"]
    end
    
    subgraph "Map Types"
        CPUMap["CoordinateMapCPU"]
        GPUMap["CoordinateMapGPU"]
        FieldMap["CoordinateFieldMap"]
    end
    
    subgraph "Operations"
        Insert["Insert/Map Operations"]
        Stride["Stride Operations"]
        KernelMapOp["Kernel Map Operations"]
        Pruning["Pruning Operations"]
    end
    
    CoordKey --> CoordMap
    CoordMap --> CPUMap
    CoordMap --> GPUMap
    CoordMap --> FieldMap
    
    CoordMgr --> CoordKey
    CoordMgr --> CoordMap
    CoordMgr --> KernelRegion
    
    CoordMgr --> Insert
    CoordMgr --> Stride
    CoordMgr --> KernelMapOp
    CoordMgr --> Pruning
    
    KernelRegion --> KernelMapOp
```

### Core Coordinate Components

1. **CoordinateMapKey**: Uniquely identifies a coordinate system with tensor stride and string ID
   ```cpp
   using coordinate_map_key_type = std::pair<default_types::stride_type, std::string>;
   ```

2. **CoordinateMap**: Base template class for different coordinate map implementations
   - Maps coordinates to their indices in the feature tensor
   - Handles coordinate insertion, lookup, and transformation

3. **CoordinateMapManager**: Manages multiple coordinate maps 
   - Handles creation, transformation, and operations between coordinate maps
   - Stores mappings between different coordinate systems

4. **KernelRegion**: Defines regions of coordinates for convolution and pooling operations
   - Implements different region types (HYPER_CUBE, HYPER_CROSS, CUSTOM)
   - Provides efficient iteration through kernel offsets

Sources: [src/coordinate_map_manager.hpp:87-149](). [src/coordinate_map.hpp:106-132](). [src/types.hpp:77-101](). [src/kernel_region.hpp:47-172]().

## CPU and GPU Implementation

MinkowskiEngine provides both CPU and GPU (CUDA) implementations for all operations. The code is structured to allow seamless switching between the two backends.

```mermaid
flowchart LR
    subgraph "Core Operations"
        Conv["Convolution"]
        Pool["Pooling"]
        Prune["Pruning"]
        Interp["Interpolation"]
        Broadcast["Broadcasting"]
    end
    
    subgraph "CPU Implementation"
        CPUConv["ConvolutionForwardCPU"]
        CPUPool["LocalPoolingForwardCPU"]
        CPUPrune["PruningForwardCPU"]
        CPUMap["CoordinateMapCPU"]
    end
    
    subgraph "GPU Implementation"
        GPUConv["ConvolutionForwardGPU"]
        GPUPool["LocalPoolingForwardGPU"]
        GPUPrune["PruningForwardGPU"]
        GPUMap["CoordinateMapGPU"]
        CUDAKernels["CUDA Kernels"]
    end
    
    Conv --> CPUConv
    Conv --> GPUConv
    Pool --> CPUPool
    Pool --> GPUPool
    Prune --> CPUPrune
    Prune --> GPUPrune
    
    CPUConv --> CPUMap
    CPUPool --> CPUMap
    CPUPrune --> CPUMap
    
    GPUConv --> GPUMap
    GPUPool --> GPUMap
    GPUPrune --> GPUMap
    GPUMap --> CUDAKernels
```

### CPU Implementation

- Implemented in standard C++ with OpenMP parallelization for multi-threading
- CPU functions are defined with templates like `ConvolutionForwardCPU<coordinate_type>` in `extern.hpp`
- Exposed to Python through `instantiate_cpu_func` function

### GPU Implementation

- Built on CUDA for GPU acceleration
- Uses template metaprogramming for memory management
- Supports two memory allocation strategies:
  1. PyTorch memory allocator (default)
  2. Direct CUDA memory allocation (can be faster but less memory-efficient)
- GPU functions are defined with templates like `ConvolutionForwardGPU<coordinate_type, TemplatedAllocator>`
- Conditional compilation with `#ifndef CPU_ONLY` to enable CPU-only builds

Sources: [pybind/extern.hpp:53-115](). [pybind/extern.hpp:150-182](). [pybind/extern.hpp:213-245](). [pybind/extern.hpp:580-646]().

## Memory Management

MinkowskiEngine implements sophisticated memory management strategies, particularly for GPU operations.

```mermaid
flowchart TD
    subgraph "Memory Management Strategies"
        PyTorch["PyTorch Memory Pool"]
        DirectCUDA["Direct CUDA Allocation"]
        Modes["Algorithm Modes"]
    end
    
    subgraph "Allocator Types"
        C10["c10_allocator (PyTorch)"]
        DefaultAlloc["default_allocator (CUDA)"]
    end
    
    subgraph "Algorithm Modes"
        Default["DEFAULT Mode"]
        MemEff["MEMORY_EFFICIENT Mode"]
        SpeedOpt["SPEED_OPTIMIZED Mode"]
    end
    
    PyTorch --> C10
    DirectCUDA --> DefaultAlloc
    Modes --> Default
    Modes --> MemEff
    Modes --> SpeedOpt
    
    Default --> KernelMap["CUDA Kernel Map Mode"]
    MemEff --> KernelMap
    SpeedOpt --> KernelMap
```

### Memory Allocator Types

1. **PyTorch Allocator** (`GPUMemoryAllocatorType.PYTORCH`):
   - Uses PyTorch's memory pool for GPU allocations
   - Enables shared memory management with PyTorch tensors
   - Better memory efficiency for large batch sizes

2. **CUDA Allocator** (`GPUMemoryAllocatorType.CUDA`):
   - Uses direct CUDA calls for memory allocation
   - Can be faster but less memory-efficient
   - Useful for performance-critical applications

### Algorithm Modes

The `MinkowskiAlgorithm` enum defines different optimization strategies:

1. **DEFAULT**: Balanced between memory and speed (default)
2. **MEMORY_EFFICIENT**: Prioritizes memory efficiency
3. **SPEED_OPTIMIZED**: Prioritizes execution speed

These modes affect:
- CUDA kernel map generation strategy
- GPU memory usage patterns
- Default GPU occupancy levels

Sources: [src/types.hpp:115-130](). [src/coordinate_map_manager.hpp:128-156](). [MinkowskiEngine/MinkowskiCoordinateManager.py:46-97]().

## Coordinate Management System

The coordinate management system is responsible for tracking, transforming, and mapping coordinates between different tensor strides and operations.

```mermaid
flowchart TD
    subgraph "Coordinate Management"
        InsertMap["insert_and_map()"]
        FieldMap["insert_field()"]
        Stride["stride()"]
        KMap["kernel_map()"]
    end
    
    subgraph "Key Storage"
        Maps["m_coordinate_maps"]
        FieldMaps["m_field_coordinates"]
        KernelMaps["m_kernel_maps"]
        Field2Sparse["m_field_to_sparse_maps"]
    end
    
    subgraph "Map Generation"
        MapCoord["Maps Sparse Coordinates"]
        FieldCoord["Maps Field Coordinates"]
        F2S["Field to Sparse Conversion"]
    end
    
    InsertMap --> MapCoord
    InsertMap --> Maps
    
    FieldMap --> FieldCoord
    FieldMap --> FieldMaps
    
    F2S --> Field2Sparse
    
    Stride --> Maps
    KMap --> KernelMaps
    
    MapCoord --> KMap
    FieldCoord --> F2S
```

### Core Functions

1. **`insert_and_map`**: Inserts coordinates and returns mappings
   - Takes integer coordinates and tensor stride
   - Returns a key and mapping tensors (unique_map, inverse_map)

2. **`insert_field`**: Inserts continuous coordinates
   - Takes floating-point coordinates
   - Used for TensorField operations

3. **`field_to_sparse_map`**: Converts field coordinates to sparse coordinates
   - Quantizes continuous coordinates to discrete grid
   - Creates mappings between field and sparse representations

4. **`kernel_map`**: Creates mappings for convolution/pooling kernels
   - Maps input and output coordinates for sparse convolution
   - Supports different region types and kernel configurations

5. **`stride`**: Creates strided coordinate maps
   - Generates new coordinates at different tensor strides
   - Used for hierarchical operations (e.g., pooling)

Sources: [src/coordinate_map_manager.cpp:139-186](). [src/coordinate_map_manager.cpp:193-266](). [src/coordinate_map_manager.cpp:353-399](). [src/coordinate_map_manager.cpp:632-662]().

## Operation Implementation

MinkowskiEngine implements various neural network operations for sparse tensors. Here's how the key operations are implemented:

### Convolution Operations

```mermaid
flowchart LR
    subgraph "Python Interface"
        PyConv["MinkowskiConvolution"]
    end
    
    subgraph "C++ Implementation"
        ConvFwd["ConvolutionForward"]
        ConvBwd["ConvolutionBackward"]
    end
    
    subgraph "Backend Specialization"
        CPUConv["ConvolutionForwardCPU"]
        GPUConv["ConvolutionForwardGPU"]
        CPUBwd["ConvolutionBackwardCPU"]
        GPUBwd["ConvolutionBackwardGPU"]
    end
    
    PyConv --> ConvFwd
    PyConv --> ConvBwd
    
    ConvFwd --> CPUConv
    ConvFwd --> GPUConv
    ConvBwd --> CPUBwd
    ConvBwd --> GPUBwd
    
    CPUConv --> KernelMap["Kernel Map Generation"]
    GPUConv --> KernelMap
    KernelMap --> MatMul["Matrix Multiplication"]
```

Convolution operations involve:
1. Generating a kernel map between input and output coordinates
2. Using the kernel map to perform sparse tensor operations
3. Executing optimized matrix multiplications for the actual convolution

### Pooling Operations

Pooling operations follow a similar pattern to convolutions, with specialized implementations for different pooling types:

- **Local Pooling**: Pooling within a kernel region
- **Global Pooling**: Pooling across the entire spatial dimension
- **Pooling Transpose**: Unpooling operations

### Other Operations

- **Broadcasting**: Operations that combine sparse and dense tensors
- **Pruning**: Removing coordinates based on specified criteria
- **Interpolation**: Sampling between sparse coordinate points

Sources: [pybind/extern.hpp:53-115](). [pybind/extern.hpp:187-245](). [pybind/extern.hpp:356-467]().

## Memory and Performance Optimization

MinkowskiEngine implements several strategies to optimize memory usage and computational performance:

1. **Custom Memory Allocators**:
   - Template-based allocators for different scenarios
   - Special handling for CUDA memory allocation

2. **Algorithm Mode Selection**:
   - Different modes prioritize memory efficiency vs. speed
   - Configurable at runtime through Python API

3. **Kernel Map Generation**:
   - Two modes for kernel map generation:
     - MEMORY_EFFICIENT: Uses less memory but might be slower
     - SPEED_OPTIMIZED: Faster but uses more memory

4. **Sparse Tensor Operations**:
   - Optimized sparse matrix multiplication algorithms
   - Efficient implementation of sparse convolution

Sources: [src/coordinate_map_manager.hpp:128-156](). [src/types.hpp:115-130](). [pybind/extern.hpp:671-691]().

## Python API Integration

The Python interface is designed to be intuitive while providing efficient access to the C++ implementation. The `CoordinateManager` class serves as the primary interface for coordinate management.

```mermaid
flowchart TD
    subgraph "Python API Classes"
        SparseTensor["SparseTensor"]
        TensorField["TensorField"]
        CoordManager["CoordinateManager"]
    end
    
    subgraph "Implementation Details"
        PyCoordMgr["MinkowskiCoordinateManager.py"]
        CoordMapKey["CoordinateMapKey"]
        RegionType["RegionType"]
        PoolingMode["PoolingMode"]
    end
    
    subgraph "C++ Interface"
        CPPMgr["CoordinateMapManager"]
        Algorithms["MinkowskiAlgorithm"]
        MemTypes["GPUMemoryAllocatorType"]
    end
    
    SparseTensor --> CoordManager
    TensorField --> CoordManager
    
    CoordManager --> PyCoordMgr
    PyCoordMgr --> CoordMapKey
    PyCoordMgr --> RegionType
    PyCoordMgr --> PoolingMode
    
    PyCoordMgr --> CPPMgr
    PyCoordMgr --> Algorithms
    PyCoordMgr --> MemTypes
```

Key implementation details:

1. **Configuration Options**:
   - GPU memory allocator selection
   - Algorithm mode selection
   - Coordinate map type (CPU or CUDA)

2. **Core Python Methods**:
   - `insert_and_map`: Creates coordinate mappings
   - `kernel_map`: Generates kernel mappings for operations
   - `stride`: Creates strided coordinate maps

3. **C++ Integration**:
   - Uses dynamic dispatch to select appropriate C++ implementation
   - Handles tensor format conversion between PyTorch and C++

Sources: [MinkowskiEngine/MinkowskiCoordinateManager.py:107-144](). [MinkowskiEngine/MinkowskiCoordinateManager.py:153-186](). [MinkowskiEngine/MinkowskiCoordinateManager.py:377-421]().

## Conclusion

The implementation of MinkowskiEngine combines Python for ease of use with C++ for performance, leveraging both CPU and GPU computing capabilities. The core design centers around efficient coordinate management and sparse tensor operations, with specialized implementations for different backends and optimization strategies. This architecture enables high-performance processing of sparse 3D data while maintaining a user-friendly interface.

---

