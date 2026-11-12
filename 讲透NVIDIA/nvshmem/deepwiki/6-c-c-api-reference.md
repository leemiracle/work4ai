<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvshmem · page 6 C/C++ API Reference · fetched 2026-10-26 -->

# C/C++ API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/host/init/init.cu](src/host/init/init.cu)
- [src/host/mem/mem_heap.cpp](src/host/mem/mem_heap.cpp)
- [src/include/internal/non_abi/nvshmemi_h_to_d_coll_defs.cuh](src/include/internal/non_abi/nvshmemi_h_to_d_coll_defs.cuh)
- [src/include/non_abi/device/coll/fcollect.cuh](src/include/non_abi/device/coll/fcollect.cuh)
- [src/include/non_abi/device/coll/reduce.cuh](src/include/non_abi/device/coll/reduce.cuh)
- [src/include/non_abi/device/coll/reducescatter.cuh](src/include/non_abi/device/coll/reducescatter.cuh)
- [src/include/non_abi/device/coll/utils.cuh](src/include/non_abi/device/coll/utils.cuh)
- [src/include/non_abi/device/pt-to-pt/ibgda_device.cuh](src/include/non_abi/device/pt-to-pt/ibgda_device.cuh)
- [src/include/non_abi/device/pt-to-pt/nvshmemi_transfer_api.cuh](src/include/non_abi/device/pt-to-pt/nvshmemi_transfer_api.cuh)

</details>



This document provides a comprehensive reference for the NVSHMEM C/C++ APIs. It covers both host-side APIs (functions callable from CPU code) and device-side APIs (functions callable from CUDA kernels). 

For detailed transport plugin interface documentation, see [Transport Interface](#6.3). For Python bindings, see [Python API Reference](#4).

## API Organization

NVSHMEM provides two distinct API surfaces that work together to enable symmetric memory operations:

**Host API**: Functions executed on the CPU for initialization, memory management, team operations, and host-initiated collective operations. These functions are prefixed with `nvshmem_` or `nvshmemx_` (for experimental/extended features).

**Device API**: Functions callable from within CUDA kernels (`__device__` functions) for GPU-initiated point-to-point operations, collectives, and atomic memory operations. These functions are also prefixed with `nvshmem_` or `nvshmemx_`.

The two APIs share common types and constants but differ significantly in implementation and usage patterns.

### Host API Structure

```mermaid
graph TB
    subgraph "Host API Headers"
        NVAPI["host/nvshmem_api.h<br/>Core API"]
        NVXAPI["host/nvshmemx_api.h<br/>Extended API"]
        TYPES["device_host/nvshmem_types.h<br/>Common Types"]
    end
    
    subgraph "Host API Categories"
        INIT["Initialization<br/>nvshmem_init()<br/>nvshmem_finalize()"]
        MEM["Memory Management<br/>nvshmem_malloc()<br/>nvshmem_free()"]
        TEAM["Team Management<br/>nvshmem_team_split_strided()<br/>nvshmem_team_destroy()"]
        COLL["Host Collectives<br/>nvshmem_barrier_all_on_stream()<br/>nvshmem_reduce_on_stream()"]
        QUERY["Query Functions<br/>nvshmem_my_pe()<br/>nvshmem_n_pes()"]
    end
    
    subgraph "Implementation"
        INITCU["src/host/init/init.cu"]
        MEMCPP["src/host/mem/mem_heap.cpp"]
        TEAMCPP["src/host/team/team_internal.cpp"]
    end
    
    NVAPI --> INIT
    NVAPI --> MEM
    NVAPI --> TEAM
    NVAPI --> QUERY
    NVXAPI --> COLL
    
    NVAPI --> TYPES
    NVXAPI --> TYPES
    
    INIT --> INITCU
    MEM --> MEMCPP
    TEAM --> TEAMCPP
```

**Sources**: [src/host/init/init.cu:1-850](), [src/host/mem/mem_heap.cpp:1-400]()

### Device API Structure

```mermaid
graph TB
    subgraph "Device API Headers"
        DEVH["device/nvshmem_device_macros.h<br/>Device Macros"]
        DEVAPI["device/nvshmem.cuh<br/>Main Device Header"]
        XFERAPI["non_abi/device/pt-to-pt/nvshmemi_transfer_api.cuh<br/>Transfer API Abstraction"]
    end
    
    subgraph "Device API Categories"
        P2P["Point-to-Point<br/>nvshmem_put()<br/>nvshmem_get()<br/>nvshmem_p()"]
        AMO["Atomics<br/>nvshmem_atomic_fetch_add()<br/>nvshmem_atomic_compare_swap()"]
        SYNC["Synchronization<br/>nvshmem_fence()<br/>nvshmem_quiet()"]
        DEVCOLL["Device Collectives<br/>nvshmemi_barrier_threadgroup()<br/>nvshmemi_reduce_threadgroup()"]
        SIGNAL["Signaling<br/>nvshmem_put_signal()<br/>nvshmem_signal_op()"]
    end
    
    subgraph "Implementation Layers"
        XFER["transfer_device.cuh<br/>Transfer Implementation"]
        IBGDA["ibgda_device.cuh<br/>IB GDA Direct Access"]
        PROXY["proxy_device.cuh<br/>Proxy Path"]
        COLLIMPL["reduce.cuh<br/>fcollect.cuh<br/>barrier.cuh"]
    end
    
    DEVAPI --> P2P
    DEVAPI --> AMO
    DEVAPI --> SYNC
    DEVAPI --> SIGNAL
    DEVAPI --> DEVCOLL
    
    P2P --> XFERAPI
    AMO --> XFERAPI
    SYNC --> XFERAPI
    SIGNAL --> XFERAPI
    
    XFERAPI --> XFER
    XFERAPI --> IBGDA
    XFERAPI --> PROXY
    DEVCOLL --> COLLIMPL
```

**Sources**: [src/include/non_abi/device/pt-to-pt/nvshmemi_transfer_api.cuh:1-76](), [src/include/non_abi/device/coll/reduce.cuh:1-50]()

## Function Categories

NVSHMEM APIs are organized into functional categories:

| Category | Host Functions | Device Functions | Description |
|----------|---------------|------------------|-------------|
| **Initialization** | `nvshmem_init()`, `nvshmem_finalize()`, `nvshmemx_init_attr()` | N/A | Library lifecycle management |
| **Memory Management** | `nvshmem_malloc()`, `nvshmem_free()`, `nvshmem_align()`, `nvshmem_calloc()` | N/A | Symmetric heap allocation |
| **Query** | `nvshmem_my_pe()`, `nvshmem_n_pes()`, `nvshmem_ptr()` | `nvshmem_my_pe()`, `nvshmem_n_pes()`, `nvshmem_ptr()` | PE information |
| **Point-to-Point RMA** | N/A | `nvshmem_put()`, `nvshmem_get()`, `nvshmem_put_nbi()`, `nvshmem_get_nbi()` | Remote memory access |
| **Point-to-Point Signaling** | N/A | `nvshmem_put_signal()`, `nvshmem_signal_op()` | RMA with completion signaling |
| **Atomic Memory Operations** | N/A | `nvshmem_atomic_fetch_add()`, `nvshmem_atomic_compare_swap()`, `nvshmem_atomic_swap()` | Atomic RMA operations |
| **Memory Ordering** | N/A | `nvshmem_fence()`, `nvshmem_quiet()` | Enforce ordering and completion |
| **Collectives (Host)** | `nvshmem_barrier_all_on_stream()`, `nvshmem_reduce_on_stream()`, `nvshmem_broadcast_on_stream()` | N/A | Host-initiated GPU collectives |
| **Collectives (Device)** | N/A | `nvshmemi_barrier_threadgroup()`, `nvshmemi_reduce_threadgroup()`, `nvshmemi_fcollect_threadgroup()` | GPU-initiated collectives |
| **Team Management** | `nvshmem_team_split_strided()`, `nvshmem_team_split_2d()`, `nvshmem_team_destroy()` | N/A | Create and manage PE subgroups |

**Sources**: [src/host/init/init.cu:269-290](), [src/include/non_abi/device/pt-to-pt/nvshmemi_transfer_api.cuh:28-72]()

## API Naming Conventions

NVSHMEM follows consistent naming conventions to indicate function properties:

### Prefixes

- **`nvshmem_`**: Standard API functions (both host and device)
- **`nvshmemx_`**: Extended/experimental functions (may change between versions)
- **`nvshmemi_`**: Internal implementation functions (not part of public API)

### Suffixes and Modifiers

- **`_nbi`**: Non-blocking operations (e.g., `nvshmem_put_nbi()`)
- **`_signal`**: Operations with signaling (e.g., `nvshmem_put_signal()`)
- **`_on_stream`**: Host operations launched on CUDA stream (e.g., `nvshmem_barrier_all_on_stream()`)
- **`_threadgroup`**: Internal device functions accepting threadgroup scope (e.g., `nvshmemi_reduce_threadgroup<SCOPE>()`)

### Type Suffixes

Many functions are type-generic and follow OpenSHMEM conventions with type suffixes:

```c
// Examples of type-specific functions
nvshmem_int_put(int *dest, const int *source, size_t nelems, int pe);
nvshmem_float_put(float *dest, const float *source, size_t nelems, int pe);
nvshmem_double_get(double *dest, const double *source, size_t nelems, int pe);
```

For C++/CUDA, templates are often used instead of explicit type suffixes in device code.

**Sources**: [src/include/non_abi/device/pt-to-pt/nvshmemi_transfer_api.cuh:28-60]()

## Host API Usage Pattern

```mermaid
sequenceDiagram
    participant App as "Application"
    participant HostAPI as "NVSHMEM Host API"
    participant Bootstrap as "Bootstrap System"
    participant Heap as "Symmetric Heap"
    participant Device as "GPU Device"
    
    App->>HostAPI: nvshmem_init()
    HostAPI->>Bootstrap: Initialize PE communication
    HostAPI->>Heap: Allocate symmetric heap
    HostAPI->>Device: Copy device state
    HostAPI-->>App: Return (PE ready)
    
    App->>HostAPI: nvshmem_malloc(size)
    HostAPI->>Heap: Allocate symmetric memory
    Heap->>Heap: Register with transports
    HostAPI-->>App: Return device pointer
    
    App->>HostAPI: Launch kernel with nvshmem_ptr()
    Note over Device: Device operations occur
    
    App->>HostAPI: nvshmem_barrier_all_on_stream(stream)
    HostAPI->>Device: Launch barrier kernel
    
    App->>HostAPI: nvshmem_free(ptr)
    HostAPI->>Heap: Deallocate memory
    
    App->>HostAPI: nvshmem_finalize()
    HostAPI->>Heap: Cleanup symmetric memory
    HostAPI->>Bootstrap: Finalize communication
```

**Sources**: [src/host/init/init.cu:437-597](), [src/host/mem/mem_heap.cpp:150-191]()

## Device API Usage Pattern

Device APIs are designed for use within CUDA kernels and support different threadgroup scopes:

### Threadgroup Scopes

Device collective operations accept a threadgroup scope template parameter:

```cpp
// From nvshmemi_common_device_defines.cuh
typedef enum {
    NVSHMEMI_THREADGROUP_THREAD = 0,  // Single thread
    NVSHMEMI_THREADGROUP_WARP = 1,    // Warp (32 threads)
    NVSHMEMI_THREADGROUP_BLOCK = 2    // Thread block
} threadgroup_t;
```

Operations can be performed by individual threads, warps, or entire blocks cooperatively.

### Device Operation Flow

```mermaid
graph LR
    subgraph "CUDA Kernel"
        THREAD["Thread calls<br/>nvshmem_put()"]
    end
    
    subgraph "Transfer API Layer"
        XFER["nvshmemi_transfer_rma()"]
        CONN["job_connectivity<br/>check"]
    end
    
    subgraph "Execution Paths"
        P2P["GPU Load/Store<br/>Direct memory access"]
        IBGDA["IBGDA WQE<br/>GPU-posted RDMA"]
        PROXY["Proxy Channel<br/>CPU-mediated"]
    end
    
    THREAD --> XFER
    XFER --> CONN
    CONN -->|"job_connectivity <= GPU_LDST"| P2P
    CONN -->|"GDA supported"| IBGDA
    CONN -->|"Otherwise"| PROXY
    
    P2P --> MEM["Symmetric Heap"]
    IBGDA --> NIC["Network Interface"]
    PROXY --> CPU["Proxy Thread"]
```

**Sources**: [src/include/non_abi/device/pt-to-pt/nvshmemi_transfer_api.cuh:36-48](), [src/include/non_abi/device/pt-to-pt/ibgda_device.cuh:665-730]()

## Type System

NVSHMEM defines several key types used across both host and device APIs:

### Core Types

| Type | Definition | Description |
|------|------------|-------------|
| `nvshmem_team_t` | `int` | Team handle (index into team pool) |
| `nvshmemx_qp_handle_t` | `int` | Queue pair handle for multi-rail |
| `nvshmemi_amo_t` | `enum` | Atomic memory operation type |
| `nvshmemi_op_t` | `enum` | Channel operation type (PUT/GET) |
| `rdxn_ops_t` | `enum` | Reduction operation type |

### Reduction Operations

```cpp
// From device_host/nvshmem_common_transport.h
typedef enum {
    RDXN_OPS_SUM = 0,
    RDXN_OPS_PROD,
    RDXN_OPS_AND,
    RDXN_OPS_OR,
    RDXN_OPS_XOR,
    RDXN_OPS_MIN,
    RDXN_OPS_MAX,
    RDXN_OPS_MAXLOC  // Maximum with location
} rdxn_ops_t;
```

**Sources**: [src/include/non_abi/device/coll/reduce.cuh:49-105]()

### Atomic Operations

```cpp
// From device_host_transport/nvshmem_constants.h
typedef enum {
    NVSHMEMI_AMO_SIGNAL,
    NVSHMEMI_AMO_SET,
    NVSHMEMI_AMO_ADD,
    NVSHMEMI_AMO_FETCH_ADD,
    NVSHMEMI_AMO_SWAP,
    NVSHMEMI_AMO_FETCH_SWAP,
    NVSHMEMI_AMO_COMPARE_SWAP,
    NVSHMEMI_AMO_FETCH_AND,
    NVSHMEMI_AMO_FETCH_OR,
    NVSHMEMI_AMO_FETCH_XOR
} nvshmemi_amo_t;
```

**Sources**: [src/include/non_abi/device/pt-to-pt/nvshmemi_transfer_api.cuh:52-59]()

## Device State Access

Device-side operations access a global device state structure containing PE information, heap pointers, and transport metadata:

```mermaid
graph TB
    subgraph "Device State Structure"
        DEVSTATE["nvshmemi_device_host_state_t<br/>nvshmemi_device_state_d"]
        
        PEID["PE Identity<br/>mype, npes"]
        HEAPINFO["Heap Information<br/>heap_base<br/>peer_heap_base_p2p[]<br/>peer_heap_base_actual[]"]
        JOBCONN["Job Connectivity<br/>job_connectivity<br/>enable_rail_opt"]
        TEAMPOOL["Team Pool<br/>team_pool[]"]
        COLLPARAMS["Collective Params<br/>gpu_coll_env_params_var"]
    end
    
    DEVSTATE --> PEID
    DEVSTATE --> HEAPINFO
    DEVSTATE --> JOBCONN
    DEVSTATE --> TEAMPOOL
    DEVSTATE --> COLLPARAMS
    
    KERNEL["CUDA Kernel"] --> DEVSTATE
```

The device state is copied from host to device during initialization:

**Sources**: [src/host/init/init.cu:147-199]()

## Collective Operation Templates

Device-side collective operations are implemented as C++ templates accepting type and scope parameters:

```cpp
// Generic device collective signature pattern
template <typename TYPE, rdxn_ops_t OP, threadgroup_t SCOPE>
__device__ void nvshmemi_reduce_threadgroup(
    nvshmem_team_t team,
    TYPE *dest,
    const TYPE *source,
    size_t nreduce
);

// Example instantiation for sum reduction at block scope
nvshmemi_reduce_threadgroup<float, RDXN_OPS_SUM, NVSHMEMI_THREADGROUP_BLOCK>(
    NVSHMEM_TEAM_WORLD, dest, source, nelems
);
```

### Collective Algorithm Selection

Collectives automatically select algorithms based on:
- Team connectivity (P2P, NVLS available)
- Data size and type
- Environment variable settings

```mermaid
graph TD
    COLL["Collective Call"] --> CHECK["Check Conditions"]
    CHECK --> SIZE{"Data Size"}
    CHECK --> NVLS{"NVLS Available?"}
    CHECK --> P2P{"P2P Connected?"}
    
    SIZE -->|"Small"| LL["LL8/LL128 Algorithm"]
    NVLS -->|"Yes"| NVLSALGO["NVLS Multicast"]
    P2P -->|"Yes"| P2PALGO["P2P Direct"]
    
    SIZE -->|"Large"| ONESHOT["One-Shot Algorithm"]
    NVLS -->|"No"| PROXY["Proxy-based"]
    P2P -->|"No"| PROXY
```

**Sources**: [src/include/non_abi/device/coll/reduce.cuh:113-122](), [src/include/non_abi/device/coll/fcollect.cuh:334-468]()

## Memory Ordering and Synchronization

Device operations provide fine-grained control over memory ordering:

### Fence vs Quiet

```cpp
// Fence: Order operations to a specific PE or all PEs
template <threadgroup_t SCOPE>
__device__ void nvshmemi_transfer_fence(
    int pe = NVSHMEMX_PE_ALL,
    nvshmemx_qp_handle_t *qp_handle = NULL,
    int num_qps = NVSHMEMX_QP_ALL
);

// Quiet: Ensure completion of all operations
template <threadgroup_t SCOPE>
__device__ void nvshmemi_transfer_quiet(
    bool use_membar,
    int pe = NVSHMEMX_PE_ALL,
    nvshmemx_qp_handle_t *qp_handle = NULL,
    int num_qps = NVSHMEMX_QP_ALL
);
```

**Fence** ensures ordering of subsequent operations after prior operations to specified PEs complete.

**Quiet** ensures all prior operations have completed and their results are visible at target PEs.

**Sources**: [src/include/non_abi/device/pt-to-pt/nvshmemi_transfer_api.cuh:62-68]()

## IBGDA Device Functions

For InfiniBand GDA (GPU Direct Async), device code can directly post work queue entries:

```mermaid
graph LR
    subgraph "GPU Kernel Thread"
        CALL["nvshmem_put()"]
    end
    
    subgraph "IBGDA Device Layer"
        WQE["ibgda_write_rdma_write_wqe()"]
        WQEPTR["Get WQE pointer<br/>from QP"]
        DOORBELL["Ring doorbell<br/>(store to MMIO)"]
    end
    
    subgraph "Hardware"
        NIC["InfiniBand NIC"]
        REMOTE["Remote GPU Memory"]
    end
    
    CALL --> WQE
    WQE --> WQEPTR
    WQEPTR --> DOORBELL
    DOORBELL --> NIC
    NIC --> REMOTE
```

### Work Queue Entry Construction

IBGDA allows GPU threads to construct and post RDMA work queue entries directly:

```cpp
// From ibgda_device.cuh - Device function to write RDMA write WQE
template <bool support_half_av_seg>
__device__ void ibgda_write_rdma_write_wqe(
    nvshmemi_ibgda_device_qp_t *qp,
    uint32_t dct_idx,
    uint64_t laddr,
    __be32 lkey,
    uint64_t raddr,
    __be32 rkey,
    uint32_t bytes,
    uint16_t wqe_idx,
    uint8_t fm_ce_se,
    void **out_wqes
);
```

This bypasses CPU involvement entirely for RDMA operations.

**Sources**: [src/include/non_abi/device/pt-to-pt/ibgda_device.cuh:665-730](), [src/include/non_abi/device/pt-to-pt/ibgda_device.cuh:483-607]()

## Host-Launched Device Collectives

Host code can launch device collectives asynchronously on CUDA streams:

```cpp
// Pattern for host-launched device collective
template <typename TYPE>
__global__ void fcollect_on_stream_kernel(
    nvshmem_team_t team,
    TYPE *dest,
    const TYPE *source,
    size_t nelems,
    int in_cuda_graph
) {
    nvshmemi_fcollect_threadgroup<TYPE, NVSHMEMI_THREADGROUP_BLOCK>(
        team, dest, source, dest_offset, nelems
    );
}

// Host API calls this kernel
int nvshmem_fcollect_on_stream(
    nvshmem_team_t team,
    void *dest,
    const void *source,
    size_t nelems,
    cudaStream_t stream
);
```

These kernels are defined in [src/include/internal/non_abi/nvshmemi_h_to_d_coll_defs.cuh:76-95]().

**Sources**: [src/include/internal/non_abi/nvshmemi_h_to_d_coll_defs.cuh:33-151]()

## Error Handling

Host API functions return integer status codes:

```cpp
// Success codes
#define NVSHMEMX_SUCCESS 0

// Error codes
#define NVSHMEMX_ERROR_INTERNAL -1
#define NVSHMEMX_ERROR_OUT_OF_MEMORY -2
#define NVSHMEMX_ERROR_INVALID_VALUE -3
#define NVSHMEMX_ERROR_GPU_NOT_SELECTED -4
#define NVSHMEMX_ERROR_SYMMETRY -5
```

Device API functions typically do not return errors but may use `assert()` for debugging builds.

## Performance Considerations

### Operation Latency

| Operation Type | Typical Path | Latency Characteristics |
|----------------|--------------|-------------------------|
| GPU Load/Store (P2P) | Direct memory access | Lowest (~100s ns) |
| IBGDA Put/Get | GPU-posted WQE | Low (~1-2 μs) |
| Proxy-mediated | CPU thread forwards | Higher (~5-10 μs) |
| Collective (NVLS) | Hardware multicast | Low for small messages |
| Collective (Software) | Multiple point-to-point | Scales with team size |

### Optimization Guidelines

1. **Use non-blocking operations** (`_nbi`) when possible to overlap communication with computation
2. **Batch operations** to amortize overhead
3. **Align to threadgroup scope** matching your kernel's parallelism for collectives
4. **Minimize `quiet()` calls** - use `fence()` when only ordering is needed
5. **Leverage NVLS** for intra-node collectives on supported platforms

**Sources**: [src/include/non_abi/device/pt-to-pt/ibgda_device.cuh:393-397](), [src/include/non_abi/device/coll/reduce.cuh:146-176]()

## API Subsections

For detailed function-by-function documentation:

- **[Host API](#6.1)**: Complete reference for all host-side functions including initialization, memory allocation, team management, and host-launched collectives
- **[Device API](#6.2)**: Complete reference for device-side functions including point-to-point RMA, atomics, synchronization, and GPU-initiated collectives
- **[Transport Interface](#6.3)**: Internal transport plugin interface for implementing custom transport backends

**Sources**: [src/host/init/init.cu:1-850](), [src/host/mem/mem_heap.cpp:1-1500](), [src/include/non_abi/device/pt-to-pt/nvshmemi_transfer_api.cuh:1-76](), [src/include/non_abi/device/coll/reduce.cuh:1-600]()

---

