<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuCascade · page 3 Architecture Overview · fetched 2026-10-26 -->

# Architecture Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [include/memory/memory_reservation_manager.hpp](include/memory/memory_reservation_manager.hpp)
- [src/data/CMakeLists.txt](src/data/CMakeLists.txt)
- [src/memory/CMakeLists.txt](src/memory/CMakeLists.txt)
- [src/memory/memory_reservation_manager.cpp](src/memory/memory_reservation_manager.cpp)
- [test/CMakeLists.txt](test/CMakeLists.txt)
- [test/memory/test_memory_reservation_manager.cpp](test/memory/test_memory_reservation_manager.cpp)

</details>



This page provides a high-level overview of cuCascade's architecture, describing the three fundamental layers that compose the system: Memory Management, Data Representation, and Data Management. Each layer addresses a specific aspect of heterogeneous memory management and data processing on GPU systems.

For detailed information about specific components within each layer, see [System Components](#3.1). For information about the memory tier hierarchy and data movement patterns, see [Memory Tier Hierarchy](#3.2). For implementation details of individual subsystems, refer to the Memory Management Subsystem ([section 4](#4)), Data Representation Subsystem ([section 5](#5)), and Data Management Subsystem ([section 6](#6)).

## Three-Layer Architecture

cuCascade is organized into three distinct architectural layers, each responsible for a specific domain of functionality:

| Layer | Primary Responsibility | Key Abstractions |
|-------|----------------------|------------------|
| **Memory Management** | Allocate and track memory across heterogeneous memory tiers (GPU, HOST, DISK) | `memory_reservation_manager`, `memory_space`, `reservation` |
| **Data Representation** | Abstract data storage formats and enable cross-tier data movement | `idata_representation`, `gpu_table_representation`, `host_table_representation` |
| **Data Management** | Manage data batch lifecycle and multi-operator routing | `data_batch`, `data_repository`, `data_repository_manager` |

Sources: [include/memory/memory_reservation_manager.hpp:178-303](), [src/data/CMakeLists.txt:18-25](), [src/memory/CMakeLists.txt:18-33]()

```mermaid
graph TB
    subgraph Layer3["Data Management Layer"]
        data_batch["data_batch<br/>(lifecycle & state)"]
        data_repository["data_repository<br/>(FIFO queues)"]
        data_repository_manager["data_repository_manager<br/>(multi-operator coordination)"]
    end
    
    subgraph Layer2["Data Representation Layer"]
        idata_representation["idata_representation<br/>(abstract interface)"]
        gpu_table_representation["gpu_table_representation<br/>(wraps cudf::table_view)"]
        host_table_representation["host_table_representation<br/>(block-based host memory)"]
        representation_converter_registry["representation_converter_registry<br/>(cross-tier conversion)"]
    end
    
    subgraph Layer1["Memory Management Layer"]
        memory_reservation_manager["memory_reservation_manager<br/>(central orchestrator)"]
        memory_space["memory_space<br/>(per-device memory tracking)"]
        reservation["reservation<br/>(RAII memory handle)"]
        topology_discovery["topology_discovery<br/>(NUMA & GPU detection)"]
    end
    
    subgraph External["External Dependencies"]
        cudf["cudf::table_view<br/>cudf::pack/unpack"]
        rmm["rmm::device_memory_resource"]
        cuda["CUDA Runtime<br/>cudaMemcpy"]
    end
    
    data_repository_manager -->|"manages"| data_repository
    data_repository -->|"stores"| data_batch
    data_batch -->|"holds ptr to"| idata_representation
    
    idata_representation <-.->|"polymorphic"| gpu_table_representation
    idata_representation <-.->|"polymorphic"| host_table_representation
    
    representation_converter_registry -->|"converts between"| gpu_table_representation
    representation_converter_registry -->|"converts between"| host_table_representation
    
    gpu_table_representation -->|"allocates via"| memory_reservation_manager
    host_table_representation -->|"allocates via"| memory_reservation_manager
    representation_converter_registry -->|"requests from"| memory_reservation_manager
    
    memory_reservation_manager -->|"manages multiple"| memory_space
    memory_space -->|"creates"| reservation
    topology_discovery -.->|"configures"| memory_reservation_manager
    
    gpu_table_representation -->|"wraps"| cudf
    memory_space -->|"uses"| rmm
    representation_converter_registry -->|"uses"| cuda
    
    style data_repository_manager fill:#f0f0f0,stroke:#333,stroke-width:2px
    style memory_reservation_manager fill:#f0f0f0,stroke:#333,stroke-width:2px
    style representation_converter_registry fill:#f0f0f0,stroke:#333,stroke-width:2px
```

**Diagram: Core Architectural Components and Dependencies**

Sources: [src/data/CMakeLists.txt:18-25](), [src/memory/CMakeLists.txt:18-33](), [include/memory/memory_reservation_manager.hpp:178-303]()

## Memory Management Layer

The Memory Management Layer provides heterogeneous memory allocation and tracking across GPU devices, host memory (with NUMA awareness), and disk storage. This layer is the foundation of cuCascade's multi-tier memory architecture.

### Core Components

- **`memory_reservation_manager`**: Central orchestrator that coordinates memory reservations across all memory spaces. Implements multiple reservation strategies (`any_memory_space_in_tier`, `specific_memory_space`, `any_memory_space_in_tiers`) for flexible allocation policies.

- **`memory_space`**: Represents a single memory space (e.g., GPU device 0, NUMA node 1). Tracks memory capacity, reservations, and enforces limits. Each space owns a `rmm::device_memory_resource` or `fixed_size_host_memory_resource`.

- **`reservation`**: RAII handle for reserved memory. Guarantees memory availability until destroyed. Provides access to the underlying memory resource for actual allocations.

- **`topology_discovery`**: Detects system hardware topology including GPU devices, NUMA nodes, and device-to-NUMA affinity for optimal memory placement.

### Reservation Strategies

The system supports multiple reservation request strategies defined in [include/memory/memory_reservation_manager.hpp:55-167]():

| Strategy Class | Purpose | Use Case |
|---------------|---------|----------|
| `any_memory_space_in_tier_with_preference` | Allocate in a tier, preferring a specific device | GPU allocation with device preference |
| `any_memory_space_in_tier` | Allocate in any device within a tier | Flexible GPU or HOST allocation |
| `any_memory_space_in_tiers` | Allocate across multiple tiers with priority order | Cascading allocation (GPU → HOST → DISK) |
| `specific_memory_space` | Allocate in a specific device | Pinned device allocation |
| `any_memory_space_to_downgrade` | Downgrade from one tier to lower tiers | Memory pressure response |
| `any_memory_space_to_upgrade` | Upgrade from lower tier to higher tier | Performance optimization |

Sources: [include/memory/memory_reservation_manager.hpp:42-306](), [src/memory/memory_reservation_manager.cpp:122-365](), [test/memory/test_memory_reservation_manager.cpp:57-515]()

## Data Representation Layer

The Data Representation Layer abstracts data storage formats and enables seamless conversion between memory tiers. This layer bridges the gap between GPU-native cuDF tables and host memory representations.

### Core Components

- **`idata_representation`**: Abstract interface defining the polymorphic contract for all data representations. Provides methods for memory tier identification, size queries, and conversion operations.

- **`gpu_table_representation`**: Wraps `cudf::table_view` and manages GPU memory. Uses `cudf::pack` for serialization and `cudf::unpack` for deserialization during tier transitions.

- **`host_table_representation`**: Manages data in host memory using a block-based allocation strategy via `host_table_allocation`. Data is stored as serialized contiguous metadata and data blocks.

- **`representation_converter_registry`**: Central registry for conversion operations. Implements conversions for:
  - GPU → HOST (via `cudf::pack` + `cudaMemcpy`)
  - HOST → GPU (via `cudaMemcpy` + `cudf::unpack`)
  - GPU → GPU (via `cudaMemcpyPeer` for peer-to-peer transfer)
  - HOST → HOST (via block-based copy for cross-NUMA transfer)

```mermaid
graph LR
    subgraph Tier_GPU["GPU Tier"]
        gpu_rep["gpu_table_representation"]
        cudf_table["cudf::table_view"]
        gpu_rep -->|"wraps"| cudf_table
    end
    
    subgraph Tier_HOST["HOST Tier"]
        host_rep["host_table_representation"]
        host_alloc["host_table_allocation<br/>(block-based)"]
        host_rep -->|"owns"| host_alloc
    end
    
    subgraph Conversion["representation_converter_registry"]
        pack_op["cudf::pack<br/>(serialize)"]
        unpack_op["cudf::unpack<br/>(deserialize)"]
        memcpy["cudaMemcpy<br/>(data transfer)"]
        peer_copy["cudaMemcpyPeer<br/>(GPU to GPU)"]
    end
    
    gpu_rep -->|"GPU to HOST"| pack_op
    pack_op --> memcpy
    memcpy --> host_rep
    
    host_rep -->|"HOST to GPU"| memcpy
    memcpy --> unpack_op
    unpack_op --> gpu_rep
    
    gpu_rep -.->|"GPU to GPU"| peer_copy
    peer_copy -.-> gpu_rep
    
    host_rep -.->|"HOST to HOST"| host_rep
```

**Diagram: Data Representation Conversion Paths**

Sources: [src/data/CMakeLists.txt:20-25](), [include/memory/memory_reservation_manager.hpp:42-306]()

## Data Management Layer

The Data Management Layer orchestrates the lifecycle of data batches and manages routing to multiple operators. This layer implements the producer-consumer patterns that drive data processing workflows.

### Core Components

- **`data_batch`**: Represents a unit of data with a unique batch ID. Tracks processing state via reference counting (`processing_count`). Holds a polymorphic pointer to `idata_representation` for actual data storage.

- **`data_batch_processing_handle`**: RAII handle acquired when processing a batch. Increments `processing_count` on acquisition, decrements on destruction. Prevents unsafe data movement while processing is active.

- **`data_repository`**: FIFO queue of data batches for a single operator. Two variants:
  - `shared_data_repository`: Holds `std::shared_ptr<data_batch>` for broadcast patterns
  - `unique_data_repository`: Holds `std::unique_ptr<data_batch>` for exclusive ownership

- **`data_repository_manager`**: Routes incoming batches to multiple operator-specific repositories. Generates unique batch IDs and distributes batches according to ownership semantics.

### Batch Lifecycle States

```mermaid
stateDiagram-v2
    [*] --> Created: "new data_batch(id, data)"
    Created --> InRepository: "add_data_batch()"
    
    InRepository --> Processing: "pull_data_batch()<br/>acquire processing_handle"
    
    state Processing {
        [*] --> Active
        Active --> Active: "Additional handles"
        Active --> [*]: "Last handle released"
    }
    
    Processing --> InRepository: "processing_count > 0<br/>batch still in queue"
    Processing --> Available: "processing_count == 0<br/>ready for conversion"
    
    state Available_Choice <<choice>>
    Available --> Available_Choice
    Available_Choice --> Processing: "New processing request"
    Available_Choice --> Converting: "convert_to() called"
    Available_Choice --> Downgrading: "Memory pressure<br/>downgrade triggered"
    
    Converting --> InRepository: "Tier/format changed"
    Downgrading --> InRepository: "Moved to lower tier"
    
    InRepository --> [*]: "Repository destroyed<br/>or batch removed"
    
    note right of Processing
        processing_count tracks
        concurrent processing_handles
        Blocks conversion/downgrade
    end note
```

**Diagram: Data Batch State Machine**

Sources: [src/data/data_batch.cpp](), [src/data/data_repository.cpp](), [src/data/data_repository_manager.cpp]()

## Component Interaction Flow

The following diagram illustrates how the three layers interact during a typical data processing workflow:

```mermaid
sequenceDiagram
    participant App as "Application"
    participant RepoMgr as "data_repository_manager"
    participant Repo as "data_repository"
    participant Batch as "data_batch"
    participant RepReg as "representation_converter_registry"
    participant MemMgr as "memory_reservation_manager"
    participant MemSpace as "memory_space"
    
    App->>MemMgr: "request_reservation(strategy, size)"
    MemMgr->>MemSpace: "make_reservation(size)"
    MemSpace-->>MemMgr: "reservation"
    MemMgr-->>App: "unique_ptr<reservation>"
    
    App->>Batch: "new data_batch(id, gpu_table_representation)"
    App->>RepoMgr: "add_data_batch(batch)"
    RepoMgr->>Repo: "add_data_batch(batch_ptr)"
    
    App->>Repo: "pull_data_batch()"
    Repo->>Batch: "try_to_lock_for_processing()"
    Batch-->>Repo: "processing_handle"
    Repo-->>App: "unique_ptr<processing_handle>"
    
    Note over App,Batch: "Processing occurs..."
    
    App->>Batch: "convert_to(Tier::HOST)"
    Batch->>Batch: "Check processing_count == 0"
    Batch->>RepReg: "convert(from_gpu, to_host)"
    RepReg->>MemMgr: "request_reservation(HOST tier)"
    MemMgr-->>RepReg: "reservation"
    RepReg->>RepReg: "cudf::pack + cudaMemcpy"
    RepReg-->>Batch: "host_table_representation"
    Batch-->>App: "Success"
    
    App->>App: "processing_handle destroyed"
    Note over Batch: "processing_count decremented"
```

**Diagram: Typical Data Flow Sequence**

Sources: [src/data/data_batch.cpp](), [src/data/data_repository_manager.cpp](), [src/data/representation_converter.cpp]()

## Memory Tier Hierarchy

cuCascade organizes memory into three tiers, each with distinct performance and capacity characteristics:

```mermaid
graph TB
    subgraph Tier_GPU["GPU Tier (Tier::GPU)"]
        GPU0["memory_space<br/>device_id=0<br/>rmm::device_memory_resource"]
        GPU1["memory_space<br/>device_id=1<br/>rmm::device_memory_resource"]
        GPU_N["memory_space<br/>device_id=N"]
    end
    
    subgraph Tier_HOST["HOST Tier (Tier::HOST)"]
        HOST0["memory_space<br/>device_id=0 (NUMA 0)<br/>fixed_size_host_memory_resource"]
        HOST1["memory_space<br/>device_id=1 (NUMA 1)<br/>fixed_size_host_memory_resource"]
    end
    
    subgraph Tier_DISK["DISK Tier (Tier::DISK)"]
        DISK["memory_space<br/>device_id=0<br/>File-backed storage"]
    end
    
    subgraph Downgrade["Downgrade Operations"]
        direction LR
        DG1["Memory pressure triggers"]
        DG2["any_memory_space_to_downgrade"]
        DG1 --> DG2
    end
    
    subgraph Upgrade["Upgrade Operations"]
        direction LR
        UP1["Performance optimization"]
        UP2["any_memory_space_to_upgrade"]
        UP1 --> UP2
    end
    
    GPU0 -.->|"Downgrade"| HOST0
    GPU1 -.->|"Downgrade"| HOST1
    HOST0 -.->|"Downgrade"| DISK
    HOST1 -.->|"Downgrade"| DISK
    
    HOST0 -.->|"Upgrade"| GPU0
    HOST1 -.->|"Upgrade"| GPU1
    DISK -.->|"Upgrade"| HOST0
    DISK -.->|"Upgrade"| HOST1
    
    Downgrade -.-> GPU0
    Upgrade -.-> HOST0
```

**Diagram: Memory Tier Hierarchy and Movement**

| Tier | Performance | Capacity | Memory Resource Type | Use Case |
|------|------------|----------|---------------------|----------|
| GPU | Highest (TB/s bandwidth) | Limited (GBs) | `rmm::device_memory_resource` | Active processing |
| HOST | Medium (GB/s bandwidth) | Large (10s-100s GB) | `fixed_size_host_memory_resource` | Staging, overflow |
| DISK | Lowest (MB/s bandwidth) | Very Large (TBs) | File-backed | Archival, cold data |

Sources: [include/memory/memory_reservation_manager.hpp:42-306](), [include/memory/common.hpp](), [test/memory/test_memory_reservation_manager.cpp:52-68]()

## Build and Integration Architecture

cuCascade uses modern CMake practices to integrate with the RAPIDS ecosystem and provide a clean API for downstream consumers:

```mermaid
graph TB
    subgraph Sources["Source Files"]
        mem_src["src/memory/*.cpp<br/>(13 files)"]
        data_src["src/data/*.cpp<br/>(6 files)"]
        headers["include/**/*.hpp<br/>(Public API)"]
    end
    
    subgraph Build["Build Targets"]
        objects["cucascade_objects<br/>(OBJECT library)"]
        static["cucascade_static<br/>(STATIC library)"]
        shared["cucascade_shared<br/>(SHARED library)"]
    end
    
    subgraph Tests["Test Infrastructure"]
        test_src["test/**/*.cpp<br/>test/**/*.cu"]
        test_exe["cucascade_tests<br/>(Catch2 runner)"]
    end
    
    subgraph Dependencies["External Dependencies"]
        rapids["RAPIDS Libraries<br/>cudf::cudf<br/>rmm::rmm"]
        cuda["CUDA Toolkit<br/>CUDA::cudart<br/>CUDA::nvml"]
        system["System Libraries<br/>NUMA<br/>Threads"]
    end
    
    subgraph Install["Installation"]
        pkg_config["cuCascadeConfig.cmake<br/>(Package config)"]
        installed_libs["lib/libcucascade.*"]
        installed_headers["include/cucascade/**"]
    end
    
    mem_src --> objects
    data_src --> objects
    
    objects --> static
    objects --> shared
    objects --> test_exe
    test_src --> test_exe
    
    rapids --> objects
    cuda --> objects
    system --> objects
    
    static --> installed_libs
    shared --> installed_libs
    headers --> installed_headers
    
    installed_libs --> pkg_config
    installed_headers --> pkg_config
    
    pkg_config -->|"find_package(cuCascade)"| Consumer["Downstream Applications"]
```

**Diagram: Build System Architecture**

### Build Configuration

The build system compiles sources once using an `OBJECT` library (`cucascade_objects`), then links into both static and shared library variants. This approach minimizes compilation time while supporting multiple distribution formats.

**Key Build Characteristics:**

- **Language Requirements**: C++20, CUDA 12.0+
- **Build System**: CMake 3.26+
- **Primary Dependencies**: cuDF, RMM (from RAPIDS), CUDA Toolkit
- **Test Framework**: Catch2 v2.13.10
- **Installation**: Produces CMake package config for downstream consumption

Sources: [src/data/CMakeLists.txt:18-25](), [src/memory/CMakeLists.txt:18-33](), [test/CMakeLists.txt:18-61]()

## Thread Safety and Concurrency

cuCascade is designed for concurrent operation with careful synchronization boundaries:

- **`memory_reservation_manager`**: Thread-safe reservation requests with cross-space condition variable for blocking when no space is available
- **`data_batch`**: Thread-safe processing state management via atomic `processing_count` 
- **`data_repository`**: Thread-safe FIFO operations with mutex protection
- **`processing_handle`**: RAII pattern ensures correct reference counting even with exceptions

The system prevents race conditions during tier conversions by blocking `convert_to()` operations when `processing_count > 0`, ensuring data is not moved while being actively processed.

Sources: [test/memory/test_memory_reservation_manager.cpp:210-515](), [src/memory/memory_reservation_manager.cpp:180-191](), [test/data/test_data_batch.cpp]()

---

