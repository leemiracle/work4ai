<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuCascade · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CMakeLists.txt](CMakeLists.txt)
- [cmake/cuCascadeConfig.cmake.in](cmake/cuCascadeConfig.cmake.in)
- [src/data/CMakeLists.txt](src/data/CMakeLists.txt)
- [test/CMakeLists.txt](test/CMakeLists.txt)

</details>



This document provides a high-level introduction to cuCascade, its architecture, and core concepts. For detailed information about building and configuring cuCascade, see [Getting Started](#2). For in-depth documentation of individual subsystems, see [Architecture Overview](#3), [Memory Management Subsystem](#4), [Data Representation Subsystem](#5), and [Data Management Subsystem](#6).

## Purpose and Scope

cuCascade is a GPU memory management and data representation library designed to enable efficient multi-tier data processing across heterogeneous memory spaces (GPU, HOST, and DISK). The library provides abstractions for managing data lifecycle, coordinating access across multiple operators, and automatically converting data between different memory representations based on access patterns and memory pressure.

**Sources:** [CMakeLists.txt:21-25]()

## What cuCascade Provides

cuCascade delivers three core capabilities:

| Capability | Description | Key Components |
|------------|-------------|----------------|
| **Heterogeneous Memory Management** | Orchestrate allocations across GPU, HOST (with NUMA awareness), and DISK tiers | `memory_reservation_manager`, `memory_space` |
| **Data Representation Abstraction** | Polymorphic data storage with automatic conversion between GPU tables (cuDF) and HOST tables | `idata_representation`, `gpu_table_representation`, `host_table_representation`, `representation_converter_registry` |
| **Batch Lifecycle Management** | Thread-safe data batch processing with FIFO queues, multi-operator routing, and RAII-based state management | `data_batch`, `data_repository`, `data_repository_manager`, `data_batch_processing_handle` |

The library integrates with the RAPIDS ecosystem, wrapping cuDF for GPU dataframes and RMM for GPU memory allocation, while adding support for HOST and DISK storage tiers with automatic conversion capabilities.

**Sources:** [CMakeLists.txt:48-56](), [src/data/CMakeLists.txt:18-25]()

## System Architecture

cuCascade is organized into three architectural layers, each building on the layer below:

```mermaid
graph TB
    subgraph "Layer 3: Data Management"
        data_repository_manager["data_repository_manager<br/>Multi-operator coordination"]
        shared_data_repository["shared_data_repository<br/>Broadcast to operators"]
        unique_data_repository["unique_data_repository<br/>Transfer to operator"]
        data_batch["data_batch<br/>Processing state tracking"]
        data_batch_processing_handle["data_batch_processing_handle<br/>RAII lifecycle guard"]
    end
    
    subgraph "Layer 2: Data Representation"
        idata_representation["idata_representation<br/>Abstract interface"]
        gpu_table_representation["gpu_table_representation<br/>Wraps cudf::table"]
        host_table_representation["host_table_representation<br/>Block-based HOST memory"]
        representation_converter_registry["representation_converter_registry<br/>Cross-tier conversion"]
    end
    
    subgraph "Layer 1: Memory Management"
        memory_reservation_manager["memory_reservation_manager<br/>Multi-tier orchestration"]
        memory_space["memory_space<br/>GPU/HOST/DISK abstraction"]
        topology_discovery["topology_discovery<br/>NUMA hardware detection"]
    end
    
    subgraph "External Dependencies"
        cudf["cudf::table<br/>GPU DataFrames"]
        rmm["rmm::device_memory_resource<br/>GPU allocations"]
        cuda["CUDA Runtime<br/>cudart, nvml"]
    end
    
    data_repository_manager --> shared_data_repository
    data_repository_manager --> unique_data_repository
    shared_data_repository --> data_batch
    unique_data_repository --> data_batch
    data_batch --> data_batch_processing_handle
    
    data_batch --> idata_representation
    idata_representation --> gpu_table_representation
    idata_representation --> host_table_representation
    representation_converter_registry --> gpu_table_representation
    representation_converter_registry --> host_table_representation
    
    gpu_table_representation --> cudf
    memory_space --> rmm
    memory_space --> cuda
    
    memory_reservation_manager --> memory_space
    topology_discovery -.informs.-> memory_reservation_manager
    
    representation_converter_registry -.allocates via.-> memory_reservation_manager
```

**Diagram: Three-Layer Architecture with Key Classes**

Each layer provides a distinct abstraction:

- **Layer 1 (Memory Management)**: Manages heterogeneous memory resources across GPU, HOST, and DISK tiers with NUMA-aware allocation strategies
- **Layer 2 (Data Representation)**: Provides polymorphic data storage with transparent conversion between memory tiers
- **Layer 3 (Data Management)**: Coordinates data batch lifecycle, operator routing, and concurrent access control

**Sources:** [CMakeLists.txt:105-107](), [src/data/CMakeLists.txt:18-25]()

## Core Concepts

### Memory Tier Hierarchy

cuCascade operates on a three-tier memory model where data can reside in different storage locations with varying access performance:

```mermaid
graph LR
    subgraph "Memory Tiers"
        GPU["GPU Tier<br/>gpu_table_representation<br/>Fast, Limited Capacity"]
        HOST["HOST Tier<br/>host_table_representation<br/>Medium Speed, Larger Capacity"]
        DISK["DISK Tier<br/>Serialized Data<br/>Slow, Unlimited Capacity"]
    end
    
    GPU -->|"downgrade<br/>cudf::pack"| HOST
    HOST -->|"upgrade<br/>cudf::unpack"| GPU
    HOST -->|"evict"| DISK
    DISK -->|"restore"| HOST
```

**Diagram: Memory Tier Transitions**

Data moves between tiers based on:
- **Memory pressure**: When a tier runs low on space, data is downgraded to the next tier
- **Access patterns**: Data is upgraded to faster tiers when needed for processing
- **Explicit conversion**: Applications can request specific tier placement via `convert_to()` operations

**Sources:** [CMakeLists.txt:49-56]()

### Data Batch Lifecycle

The `data_batch` class tracks data through its lifecycle with concurrent access support:

```mermaid
stateDiagram-v2
    [*] --> Created: "data_batch constructor"
    Created --> InRepository: "repository.add_data_batch()"
    InRepository --> Processing: "try_to_lock_for_processing()"
    Processing --> InRepository: "processing_handle released"
    InRepository --> Converting: "convert_to() called"
    Converting --> InRepository: "conversion complete"
    InRepository --> [*]: "repository destroyed"
    
    note right of Processing
        Multiple threads can acquire
        data_batch_processing_handle
        objects simultaneously
    end note
```

**Diagram: Data Batch State Machine**

The `data_batch_processing_handle` RAII class ensures safe concurrent access: multiple threads can process the same batch simultaneously, but conversions are blocked while processing is active.

**Sources:** [src/data/CMakeLists.txt:21]()

## Key Components and Their Relationships

The following diagram maps cuCascade's major components to their implementation classes and shows data flow through the system:

```mermaid
graph TB
    subgraph "Application Layer"
        APP["Application Code"]
    end
    
    subgraph "Data Management Layer"
        APP -->|"create batch with ID"| data_batch
        APP -->|"route to operators"| data_repository_manager
        
        data_repository_manager -->|"shared_ptr for broadcast"| shared_data_repository
        data_repository_manager -->|"unique_ptr for transfer"| unique_data_repository
        
        shared_data_repository -->|"FIFO queue"| data_batch
        unique_data_repository -->|"FIFO queue"| data_batch
        
        shared_data_repository -->|"pull_data_batch()"| processing_handle[data_batch_processing_handle]
        unique_data_repository -->|"pull_data_batch()"| processing_handle
    end
    
    subgraph "Data Representation Layer"
        data_batch -->|"holds shared_ptr"| rep[idata_representation]
        
        rep -->|"polymorphic"| gpu_table_representation
        rep -->|"polymorphic"| host_table_representation
        
        converter[representation_converter_registry] -->|"converts"| gpu_table_representation
        converter -->|"converts"| host_table_representation
        
        gpu_table_representation -->|"wraps"| cudf_table["cudf::table"]
        host_table_representation -->|"manages"| host_table_allocation["host_table_allocation<br/>Block-based memory"]
    end
    
    subgraph "Memory Management Layer"
        converter -->|"allocates via"| memory_reservation_manager
        
        memory_reservation_manager -->|"manages"| gpu_space["memory_space<br/>GPU devices"]
        memory_reservation_manager -->|"manages"| host_space["memory_space<br/>HOST NUMA nodes"]
        memory_reservation_manager -->|"manages"| disk_space["memory_space<br/>DISK storage"]
        
        topology_discovery -->|"discovers hardware"| memory_reservation_manager
        
        gpu_space -->|"allocates with"| rmm_resource["rmm::device_memory_resource"]
        gpu_space -->|"uses"| cuda_runtime["CUDA Runtime APIs"]
    end
```

**Diagram: Component Relationships and Data Flow**

This architecture enables:
- **Decoupled processing**: Operators process batches independently via their own repositories
- **Flexible ownership**: Batches can be broadcast (shared) or transferred (unique) between operators
- **Transparent tier migration**: Data representations handle memory tier transitions without application intervention
- **Concurrent access**: RAII handles coordinate safe multi-threaded batch access

**Sources:** [src/data/CMakeLists.txt:18-25](), [CMakeLists.txt:116-117]()

## Build System Organization

cuCascade uses a modern CMake build system with an object library pattern for efficient compilation:

| Target | Type | Purpose |
|--------|------|---------|
| `cucascade_objects` | OBJECT | Compiles all sources once, shared by static and shared libraries |
| `cucascade_static` | STATIC | Static library variant |
| `cucascade_shared` | SHARED | Shared library variant with versioning |
| `cuCascade::cucascade` | ALIAS | Convenience alias pointing to preferred library variant |
| `cucascade_tests` | EXECUTABLE | Test suite using Catch2 framework |

The build system requires:
- **CMake 3.26.4+**
- **C++20** compiler with full standard library support
- **CUDA Toolkit** with CUDA 20 support
- **RAPIDS ecosystem**: RMM and cuDF libraries
- **System libraries**: NUMA, pthreads

**Sources:** [CMakeLists.txt:18-46](), [CMakeLists.txt:94-120](), [test/CMakeLists.txt:18-24]()

## Integration with RAPIDS Ecosystem

cuCascade extends the RAPIDS ecosystem by adding multi-tier memory management capabilities:

```mermaid
graph TB
    subgraph "cuCascade Extensions"
        cascade_mem["memory_reservation_manager<br/>+ memory_space"]
        cascade_rep["host_table_representation<br/>+ representation_converter_registry"]
        cascade_batch["data_batch<br/>+ data_repository"]
    end
    
    subgraph "RAPIDS cuDF"
        cudf_table["cudf::table<br/>GPU DataFrame"]
        cudf_pack["cudf::pack<br/>Serialization"]
        cudf_unpack["cudf::unpack<br/>Deserialization"]
    end
    
    subgraph "RAPIDS RMM"
        rmm_resource["rmm::device_memory_resource<br/>GPU memory allocator"]
        rmm_pool["rmm::pool_memory_resource"]
    end
    
    subgraph "CUDA"
        cuda_runtime["CUDA Runtime<br/>cudaMemcpy, cudaMemcpyPeer"]
        nvml["NVIDIA NVML<br/>GPU topology queries"]
    end
    
    cascade_mem --> rmm_resource
    cascade_mem --> nvml
    
    cascade_rep --> cudf_table
    cascade_rep --> cudf_pack
    cascade_rep --> cudf_unpack
    cascade_rep --> cuda_runtime
    
    cascade_batch --> cascade_rep
    
    rmm_resource --> cuda_runtime
```

**Diagram: cuCascade Integration with RAPIDS and CUDA**

cuCascade wraps `cudf::table` in `gpu_table_representation`, uses `rmm::device_memory_resource` for GPU allocations, and leverages cuDF's pack/unpack operations for serialization during tier migrations.

**Sources:** [CMakeLists.txt:49-56](), [CMakeLists.txt:116-117](), [cmake/cuCascadeConfig.cmake.in:5-9]()

## Thread Safety and Concurrency Model

cuCascade is designed for high-concurrency workloads with the following guarantees:

- **Concurrent reads**: Multiple threads can hold `data_batch_processing_handle` objects for the same batch simultaneously
- **Exclusive conversions**: Tier conversions (via `convert_to()`) and batch state changes acquire locks and block processing
- **Lock-free batch addition**: Adding batches to repositories uses atomic operations where possible
- **RAII-based resource management**: All resource lifetimes are tied to scoped handle objects

For detailed concurrency patterns and best practices, see [Thread Safety and Concurrency](#8.1).

**Sources:** [src/data/CMakeLists.txt:21]()

## Next Steps

To get started with cuCascade:

1. **Build and Install**: Follow the instructions in [Building and Installation](#2.1)
2. **Understand the Architecture**: Read [Architecture Overview](#3) for detailed layer descriptions
3. **Explore Components**: Review subsystem documentation:
   - [Memory Management Subsystem](#4) for heterogeneous memory management
   - [Data Representation Subsystem](#5) for data format abstractions
   - [Data Management Subsystem](#6) for batch lifecycle coordination
4. **Review Examples**: See test cases in [Testing and Development](#7) for usage patterns

**Sources:** [CMakeLists.txt:1-242](), [test/CMakeLists.txt:1-62]()

---

