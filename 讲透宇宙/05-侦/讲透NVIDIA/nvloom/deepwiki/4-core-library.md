<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvloom · page 4 Core Library · fetched 2026-10-26 -->

# Core Library

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [library/README.md](library/README.md)
- [library/nvloom.cpp](library/nvloom.cpp)
- [library/nvloom.h](library/nvloom.h)

</details>



The Core Library provides nvloom's primary API for multi-node GPU fabric benchmarking. It includes the main `NvLoom` class, which orchestrates memory copy operations across distributed GPUs, and supporting infrastructure for MPI coordination, timing measurement, and GPU fabric discovery.

For detailed information about memory allocation strategies and pooling mechanisms, see [Memory Management System](#4.1). For GPU kernel implementations and CUDA operations, see [GPU Operations and CUDA Kernels](#4.2). For error handling and debugging utilities, see [Error Handling and Debugging](#4.3).

## Core Library Architecture

```mermaid
graph TB
    subgraph "Public API"
        NvLoom["NvLoom Class<br/>Static Methods"]
        initialize["NvLoom::initialize()"]
        doBenchmark["NvLoom::doBenchmark()"]
        finalize["NvLoom::finalize()"]
    end
    
    subgraph "Core Data Structures"
        Copy["Copy Class<br/>Operation Definition"]
        MemoryAllocation["MemoryAllocation<br/>Base Class"]
        CopyDirection["CopyDirection Enum<br/>READ/WRITE"]
        CopyType["CopyType Enum<br/>CE/SM/Multicast"]
    end
    
    subgraph "MPI Infrastructure"
        MPIWrapper["MPIWrapper Class<br/>Singleton Pattern"]
        MPIOutput["MPIOutput Class<br/>Rank 0 Output"]
        MPI_COMM_WORLD["MPI_COMM_WORLD<br/>Global Communicator"]
    end
    
    subgraph "GPU Management"
        localCuDevice["localCuDevice<br/>CUdevice Handle"]
        localCtx["localCtx<br/>CUcontext Handle"]
        localDevice["localDevice<br/>Device Index"]
    end
    
    subgraph "Fabric Discovery"
        getNvmlDevice["getNvmlDevice()<br/>NVML Integration"]
        checkCliques["checkCliques()<br/>Fabric Validation"]
        getRackGuid["getRackGuid()<br/>Topology Info"]
    end
    
    NvLoom --> initialize
    NvLoom --> doBenchmark
    NvLoom --> finalize
    
    initialize --> localCuDevice
    initialize --> localCtx
    initialize --> checkCliques
    
    doBenchmark --> Copy
    Copy --> MemoryAllocation
    Copy --> CopyDirection
    Copy --> CopyType
    
    MPIWrapper --> MPI_COMM_WORLD
    NvLoom --> MPIWrapper
    NvLoom --> MPIOutput
    
    checkCliques --> getNvmlDevice
    initialize --> getRackGuid
```

**Core Library Component Architecture**: This diagram shows the main classes and their relationships within the nvloom core library. The `NvLoom` class serves as the primary interface, coordinating MPI operations, GPU management, and fabric discovery.

Sources: [library/nvloom.h:108-146](), [library/nvloom.cpp:48-184](), [library/nvloom.cpp:319-337]()

## NvLoom Class

The `NvLoom` class provides a static interface for all core library operations. It maintains global state for the local GPU device and coordinates distributed benchmarking operations.

| Method | Purpose | Return Type |
|--------|---------|-------------|
| `initialize()` | Initialize CUDA context and MPI coordination | `void` |
| `doBenchmark()` | Execute synchronized memory copy benchmarks | `std::vector<double>` |
| `finalize()` | Clean up MPI resources | `void` |
| `getLocalDevice()` | Get local GPU device index | `int` |
| `getLocalCuDevice()` | Get CUDA device handle | `CUdevice` |
| `getLocalCtx()` | Get CUDA context handle | `CUcontext` |

### Static Member Variables

The `NvLoom` class maintains several static inline variables that store global state:

```cpp
static inline int localDevice;                    // GPU device index
static inline CUdevice localCuDevice;            // CUDA device handle  
static inline CUcontext localCtx;                // CUDA context handle
static inline int localMultiprocessorCount;       // SM count
static inline int localClockRate;                // GPU clock rate
static inline int localCpuNumaNode;              // CPU NUMA node
static inline std::string localHostname;          // Local hostname
static inline std::map<std::string, std::vector<int>> rackToProcessMap;  // Topology map
```

Sources: [library/nvloom.h:108-118](), [library/nvloom.h:134-144]()

## Initialization and Lifecycle

### Initialization Process

```mermaid
sequenceDiagram
    participant Client
    participant NvLoom
    participant CUDA
    participant MPI
    participant NVML
    
    Client->>NvLoom: initialize(_localDevice, _rackToProcessMap)
    NvLoom->>CUDA: cuInit(0)
    NvLoom->>CUDA: cuDeviceGet(&localCuDevice, localDevice)
    NvLoom->>CUDA: cuDevicePrimaryCtxRetain(&localCtx, localCuDevice)
    NvLoom->>CUDA: cuCtxSetCurrent(localCtx)
    NvLoom->>CUDA: cuDeviceGetAttribute() calls
    NvLoom->>CUDA: preloadKernels(localDevice)
    NvLoom->>MPI: MPIWrapper::getWorldRank()
    NvLoom->>NVML: checkCliques()
    NvLoom-->>Client: Initialization complete
```

**NvLoom Initialization Sequence**: Shows the initialization flow including CUDA context setup, device attribute queries, kernel preloading, and fabric validation.

The `initialize()` method performs several critical setup operations:

1. **CUDA Initialization**: Initializes CUDA driver and retains primary context for the specified device
2. **Device Attribute Queries**: Retrieves SM count, clock rate, and NUMA node information
3. **Kernel Preloading**: Loads CUDA kernels for memory operations
4. **Fabric Validation**: Verifies GPU fabric clique consistency across MPI ranks

Sources: [library/nvloom.cpp:319-337]()

### Lifecycle Management

The `finalize()` method handles cleanup by checking if MPI was initialized and calling `MPI_Finalize()` if necessary. This ensures proper resource cleanup in distributed environments.

Sources: [library/nvloom.cpp:339-345]()

## Benchmarking Execution Engine

### Core Benchmark Workflow

```mermaid
graph TD
    doBenchmark_start["doBenchmark(std::vector<Copy> copies)"]
    filter_copies["Filter copies by executingMPIrank"]
    create_streams["Create CUDA streams and events"]
    fill_buffers["Fill source/destination buffers"]
    warmup["Execute warmup iterations"]
    block_streams["Block streams with spinKernel"]
    schedule_work["Schedule benchmark work"]
    release_work["Release synchronization barrier"]
    round_robin["Round-robin execution loop"]
    calculate_bandwidth["Calculate bandwidths from events"]
    verify_buffers["Verify destination buffer correctness"]
    exchange_results["MPI_Bcast bandwidth results"]
    
    doBenchmark_start --> filter_copies
    filter_copies --> create_streams
    create_streams --> fill_buffers
    fill_buffers --> warmup
    warmup --> block_streams
    block_streams --> schedule_work
    schedule_work --> release_work
    release_work --> round_robin
    round_robin --> calculate_bandwidth
    calculate_bandwidth --> verify_buffers
    verify_buffers --> exchange_results
```

**Benchmark Execution Flow**: The `doBenchmark()` method implements a sophisticated workflow that ensures synchronized execution across multiple MPI ranks and accurate bandwidth measurement.

### Synchronization Strategy

The benchmark engine uses a multi-stage synchronization approach:

1. **Stream Blocking**: Uses `spinKernelMultistage()` to block all CUDA streams
2. **Work Scheduling**: Schedules copy operations while streams are blocked
3. **Synchronized Release**: All ranks reach `MPI_Barrier()` before releasing work
4. **Precise Timing**: CUDA events capture exact execution times

This approach ensures that all memory operations start simultaneously across the distributed system, providing accurate concurrent bandwidth measurements.

Sources: [library/nvloom.cpp:48-184](), [library/nvloom.cpp:102-106](), [library/nvloom.cpp:118-124]()

## Copy Operations Framework

### Copy Class Structure

The `Copy` class encapsulates a memory copy operation with all necessary parameters:

```cpp
class Copy {
public:
    std::shared_ptr<MemoryAllocation> dst;    // Destination memory
    std::shared_ptr<MemoryAllocation> src;    // Source memory  
    CopyDirection copyDirection;               // READ or WRITE
    CopyType copyType;                        // CE, SM, or Multicast
    int executingMPIrank;                     // MPI rank executing copy
    int iterations;                           // Number of iterations
};
```

### Copy Direction and Execution

The `executingMPIrank` is automatically determined based on `copyDirection`:
- **COPY_DIRECTION_READ**: Executed by destination rank (dst->MPIrank)
- **COPY_DIRECTION_WRITE**: Executed by source rank (src->MPIrank)

This design allows flexible control over which GPU initiates each memory transfer.

Sources: [library/nvloom.h:36-58](), [library/nvloom.h:52-56]()

### Copy Type Implementation

```mermaid
graph LR
    doMemcpy["doMemcpy()"]
    COPY_TYPE_CE["COPY_TYPE_CE<br/>cuMemcpyAsync()"]
    COPY_TYPE_SM["COPY_TYPE_SM<br/>copyKernel()"]
    COPY_TYPE_MULTICAST_WRITE["COPY_TYPE_MULTICAST_WRITE<br/>copyKernelMulticast()"]
    COPY_TYPE_MULTICAST_LD_REDUCE["COPY_TYPE_MULTICAST_LD_REDUCE<br/>copyKernelMulticastLdReduce()"]
    COPY_TYPE_MULTICAST_RED["COPY_TYPE_MULTICAST_RED_*<br/>copyKernelMulticastRed()"]
    
    doMemcpy --> COPY_TYPE_CE
    doMemcpy --> COPY_TYPE_SM
    doMemcpy --> COPY_TYPE_MULTICAST_WRITE
    doMemcpy --> COPY_TYPE_MULTICAST_LD_REDUCE
    doMemcpy --> COPY_TYPE_MULTICAST_RED
```

**Copy Type Dispatch**: The `doMemcpy()` method dispatches to different implementation strategies based on the `CopyType` enumeration.

Sources: [library/nvloom.cpp:186-202](), [library/nvloom.cpp:204-223]()

## MPI Integration

### MPIWrapper Singleton

The `MPIWrapper` class provides a singleton interface for MPI operations:

```cpp
class MPIWrapper {
private:
    int worldSize;
    int worldRank;
    MPIWrapper();  // Private constructor

public:
    static MPIWrapper& instance();
    static int getWorldSize();
    static int getWorldRank();
};
```

The singleton automatically initializes MPI if not already initialized and caches world size and rank for efficient access.

Sources: [library/nvloom.h:60-88]()

### MPIOutput Class

The `MPIOutput` class ensures that console output only occurs from MPI rank 0, preventing duplicate messages in distributed environments:

```cpp
template<typename T>
MPIOutput& operator<<(T input) {
    if (MPIWrapper::getWorldRank() == 0) std::cout << input;
    return *this;
}
```

This class supports the standard stream operator interface while maintaining single-rank output semantics.

Sources: [library/nvloom.h:90-106]()

## GPU Fabric Discovery

### NVML Integration

The core library integrates with NVML to discover and validate GPU fabric topology:

```mermaid
graph TD
    getNvmlDevice["getNvmlDevice(int device)"]
    cuDeviceGetUuid["cuDeviceGetUuid_v2()"]
    convertUuid["convertUuid(CUuuid)"]
    nvmlDeviceGetHandleByUUID["nvmlDeviceGetHandleByUUID()"]
    
    checkCliques["checkCliques()"]
    nvmlDeviceGetGpuFabricInfoV["nvmlDeviceGetGpuFabricInfoV()"]
    MPI_Allgather_clique["MPI_Allgather(cliqueId)"]
    MPI_Allgather_uuid["MPI_Allgather(clusterUuid)"]
    
    getNvmlDevice --> cuDeviceGetUuid
    cuDeviceGetUuid --> convertUuid
    convertUuid --> nvmlDeviceGetHandleByUUID
    
    checkCliques --> getNvmlDevice
    checkCliques --> nvmlDeviceGetGpuFabricInfoV
    checkCliques --> MPI_Allgather_clique
    checkCliques --> MPI_Allgather_uuid
```

**NVML Fabric Discovery**: The library uses NVML to query GPU fabric information and validate that all MPI ranks belong to the same fabric clique.

### Rack GUID Discovery

The `getRackGuid()` function extracts rack-level topology information:

```cpp
std::string getRackGuid(int device) {
    nvmlDevice_t nvmlDev = getNvmlDevice(device);
    nvmlPlatformInfo_v2_t platformInfo;
    platformInfo.version = nvmlPlatformInfo_v2;
    NVML_ASSERT(nvmlDeviceGetPlatformInfo(nvmlDev, &platformInfo));
    // Return chassis serial number as rack identifier
}
```

This enables rack-aware test patterns and topology-based optimizations.

Sources: [library/nvloom.cpp:246-258](), [library/nvloom.cpp:260-292](), [library/nvloom.cpp:301-309]()

---

