<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvshmem · page 2 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cmake_config/NVSHMEMEnv.cmake](cmake_config/NVSHMEMEnv.cmake)
- [nvshmem4py/scripts/generate_pyproject_toml.py](nvshmem4py/scripts/generate_pyproject_toml.py)
- [src/CMakeLists.txt](src/CMakeLists.txt)
- [src/host/init/init.cu](src/host/init/init.cu)
- [src/host/mem/mem_heap.cpp](src/host/mem/mem_heap.cpp)
- [src/host/topo/topo.cpp](src/host/topo/topo.cpp)
- [src/host/transport/transport.cpp](src/host/transport/transport.cpp)
- [src/include/non_abi/device/coll/utils.cuh](src/include/non_abi/device/coll/utils.cuh)
- [src/modules/transport/common/transport_common.cpp](src/modules/transport/common/transport_common.cpp)

</details>



This page provides a high-level architectural overview of NVSHMEM, explaining the layered design from application APIs down to hardware, and how the major subsystems interact. For detailed information on specific subsystems, see the child pages: [Core Library Architecture](#2.1), [Transport Layer](#2.2), [Device Programming Model](#2.3), [Memory Management and Symmetric Heap](#2.4), [Host Proxy Architecture](#2.5), [Team Management](#2.6), and [Python Bindings Architecture](#2.7).

## Five-Layer Design

NVSHMEM implements a five-layer architecture that separates concerns from high-level API abstractions down to hardware-specific communication mechanisms:

**Layer Architecture**

```mermaid
graph TB
    subgraph "1. Application Layer"
        USER_APP["User Application<br/>(C/C++/CUDA/Python)"]
    end
    
    subgraph "2. API Layer"
        HOST_API["Host API<br/>nvshmem.h<br/>nvshmem_api.h"]
        DEVICE_API["Device API<br/>nvshmem_device.h<br/>nvshmemx_defines.h"]
        PYTHON_API["Python API<br/>nvshmem.core"]
    end
    
    subgraph "3. Runtime Layer"
        INIT["Initialization<br/>nvshmemi_state_t<br/>init.cu:437-1231"]
        MEMORY["Memory Management<br/>nvshmemi_symmetric_heap<br/>mem_heap.cpp"]
        TEAM["Team Management<br/>nvshmemi_team_t<br/>team_internal.cpp"]
        TOPO["Topology Discovery<br/>nvshmemi_build_transport_map<br/>topo.cpp:438-506"]
    end
    
    subgraph "4. Communication Layer"
        TRANSPORT_MGR["Transport Manager<br/>nvshmemi_transport_init<br/>transport.cpp:50-319"]
        
        P2P_T["P2P Transport<br/>nvshmemt_p2p_init<br/>p2p.cpp"]
        IBRC_T["IBRC Transport<br/>nvshmem_transport_ibrc.so"]
        IBGDA_T["IBGDA Transport<br/>nvshmem_transport_ibgda.so"]
        UCX_T["UCX Transport<br/>nvshmem_transport_ucx.so"]
        LIBFAB_T["Libfabric Transport<br/>nvshmem_transport_libfabric.so"]
        
        PROXY["Proxy System<br/>nvshmemi_proxy_ops_t<br/>proxy.cpp"]
    end
    
    subgraph "5. Device/Hardware Layer"
        GPU["NVIDIA GPUs<br/>CUdevice<br/>CUcontext"]
        NIC["Network Hardware<br/>InfiniBand/Ethernet"]
        BOOTSTRAP["Bootstrap<br/>nvshmemi_boot_handle<br/>PMI/MPI/PMIx"]
    end
    
    USER_APP --> HOST_API
    USER_APP --> DEVICE_API
    USER_APP --> PYTHON_API
    
    HOST_API --> INIT
    HOST_API --> MEMORY
    HOST_API --> TEAM
    DEVICE_API --> TRANSPORT_MGR
    
    PYTHON_API --> HOST_API
    
    INIT --> TOPO
    INIT --> MEMORY
    TOPO --> TRANSPORT_MGR
    
    TRANSPORT_MGR --> P2P_T
    TRANSPORT_MGR --> IBRC_T
    TRANSPORT_MGR --> IBGDA_T
    TRANSPORT_MGR --> UCX_T
    TRANSPORT_MGR --> LIBFAB_T
    
    TRANSPORT_MGR --> PROXY
    
    P2P_T --> GPU
    IBRC_T --> NIC
    IBGDA_T --> NIC
    UCX_T --> NIC
    LIBFAB_T --> NIC
    
    INIT --> BOOTSTRAP
    BOOTSTRAP --> NIC
```

**Sources:** [src/host/init/init.cu:437-1231](), [src/host/transport/transport.cpp:50-319](), [src/host/mem/mem_heap.cpp:74-119](), [src/host/topo/topo.cpp:438-506]()

The layers provide clear separation:
- **Application Layer**: User code written in C/C++, CUDA kernels, or Python
- **API Layer**: Public interfaces (`nvshmem.h`, `nvshmemx.h`, Python `nvshmem.core`)
- **Runtime Layer**: State management, memory allocation, team operations
- **Communication Layer**: Pluggable transport system with proxy fallback
- **Device/Hardware Layer**: CUDA runtime, network hardware, bootstrap coordination

## Core State Management

The central state object `nvshmemi_state_t` (defined in [src/include/internal/host/nvshmemi_types.h]()) coordinates all subsystems:

**State Object Structure**

```mermaid
graph TB
    subgraph "nvshmemi_state_t"
        STATE["nvshmemi_state_t<br/>Defined: nvshmemi_types.h"]
        
        PE_INFO["PE Information<br/>int mype, npes<br/>int mype_node, npes_node"]
        
        HEAP["heap_obj<br/>nvshmemi_symmetric_heap*<br/>Points to active heap impl"]
        
        TRANSPORTS["transports[]<br/>nvshmem_transport_t*<br/>Array of transport instances"]
        
        TRANSPORT_MAP["transport_map[]<br/>int*<br/>PE-to-PE reachability matrix"]
        
        CUCONTEXT["cucontext<br/>CUcontext<br/>CUDA context handle"]
        
        TEAMS["teams<br/>nvshmemi_team_t*<br/>Team structures"]
        
        P2P_TRANS["p2p_transport<br/>nvshmemi_mem_p2p_transport*<br/>P2P memory manager"]
    end
    
    STATE --> PE_INFO
    STATE --> HEAP
    STATE --> TRANSPORTS
    STATE --> TRANSPORT_MAP
    STATE --> CUCONTEXT
    STATE --> TEAMS
    STATE --> P2P_TRANS
    
    HEAP --> HEAP_IMPL["Heap Implementation<br/>- nvshmemi_symmetric_heap_vidmem_dynamic_vmm<br/>- nvshmemi_symmetric_heap_vidmem_static_pinned<br/>- nvshmemi_symmetric_heap_sysmem_static_shm"]
    
    TRANSPORTS --> TRANS_INST["Transport Instances<br/>Each implements nvshmem_transport interface"]
    
    TRANSPORT_MAP --> REACH["Reachability<br/>transport_map[pe1*npes+pe2]<br/>Bitmap of usable transports"]
```

**Sources:** [src/include/internal/host/nvshmemi_types.h](), [src/host/init/init.cu:437-446]()

The state object is initialized in `nvshmemi_init_nvshmemi_state()` at [src/host/init/init.cu:437-446]() and accessed globally via the `nvshmemi_state` pointer.

## Initialization Flow

Initialization follows a carefully orchestrated sequence to establish process coordination, select hardware, allocate memory, and set up communication:

**Initialization Sequence**

```mermaid
graph TB
    START["nvshmem_init() / nvshmemx_init_attr()"]
    
    OPTIONS["nvshmemi_options_init()<br/>Parse environment variables<br/>bootstrap_host_transport/env_defs_internal.h"]
    
    BOOTSTRAP_PRE["nvshmemi_bootstrap_preinit()<br/>Discover network topology<br/>init.cu:322-328"]
    
    BOOTSTRAP["nvshmemi_bootstrap()<br/>Establish PE ranks, counts<br/>init.cu:330-435"]
    
    GPU_SELECT["nvshmemi_get_cucontext()<br/>Select/retain GPU context<br/>init.cu:495-597"]
    
    STATE_INIT["nvshmemi_init_nvshmemi_state()<br/>Initialize state object<br/>init.cu:437-446"]
    
    DETECT["nvshmemi_detect_same_device()<br/>Detect multi-process-per-GPU<br/>topo.cpp:523-573"]
    
    HEAP_INIT["nvshmemi_init_symmetric_heap()<br/>Allocate symmetric memory<br/>mem_heap.cpp:74-100"]
    
    TRANSPORT_INIT["nvshmemi_transport_init()<br/>Load transport plugins<br/>transport.cpp:50-319"]
    
    BUILD_MAP["nvshmemi_build_transport_map()<br/>Build PE reachability matrix<br/>topo.cpp:438-506"]
    
    CONNECT["nvshmemi_setup_connections()<br/>Connect transport endpoints<br/>transport.cpp:372-456"]
    
    REGISTER["register_heap_memory()<br/>Register heap with transports<br/>mem_heap.cpp:681-683"]
    
    TEAM_INIT["nvshmemi_team_init()<br/>Create default teams<br/>team_internal.cpp"]
    
    DEVICE_STATE["nvshmemi_update_device_state()<br/>Copy state to GPU<br/>init.cu:147-199"]
    
    READY["Initialization Complete<br/>nvshmemi_is_initialized = 1"]
    
    START --> OPTIONS
    OPTIONS --> BOOTSTRAP_PRE
    BOOTSTRAP_PRE --> BOOTSTRAP
    BOOTSTRAP --> GPU_SELECT
    GPU_SELECT --> STATE_INIT
    STATE_INIT --> DETECT
    DETECT --> HEAP_INIT
    HEAP_INIT --> TRANSPORT_INIT
    TRANSPORT_INIT --> BUILD_MAP
    BUILD_MAP --> CONNECT
    CONNECT --> REGISTER
    REGISTER --> TEAM_INIT
    TEAM_INIT --> DEVICE_STATE
    DEVICE_STATE --> READY
```

**Sources:** [src/host/init/init.cu:322-328](), [src/host/init/init.cu:330-435](), [src/host/init/init.cu:495-597](), [src/host/mem/mem_heap.cpp:74-100](), [src/host/transport/transport.cpp:50-319](), [src/host/topo/topo.cpp:438-506]()

Key initialization steps:

1. **Options Parsing**: Environment variables configure behavior (e.g., `NVSHMEM_SYMMETRIC_SIZE`, `NVSHMEM_DISABLE_P2P`)
2. **Bootstrap**: PMI/MPI establishes process group, determines `mype` and `npes`
3. **GPU Selection**: CUDA context is obtained or created
4. **Topology Detection**: Determines if multiple PEs share a GPU (MPG mode)
5. **Heap Allocation**: Symmetric memory allocated based on heap kind (VMM/static/sysmem)
6. **Transport Loading**: Plugins dynamically loaded (`.so` files for IBRC, UCX, etc.)
7. **Reachability Matrix**: Each PE determines which transports can reach which peers
8. **Endpoint Connection**: Transport-specific setup (QP creation, memory registration)
9. **Device State Copy**: Host state copied to device-accessible `nvshmemi_device_state_d`

## Communication Path Selection

NVSHMEM selects communication paths based on PE connectivity and operation type. The decision is made at runtime using the `job_connectivity` metric and transport capabilities:

**Communication Path Decision Tree**

```mermaid
graph TB
    START["Communication Request<br/>(RMA, AMO, Collective)"]
    
    CHECK_CONN["Check nvshmemi_device_state_d.job_connectivity<br/>set_job_connectivity() in init.cu"]
    
    GPU_LDST["job_connectivity == NVSHMEMI_JOB_GPU_LDST<br/>All PEs P2P-connected with GPU LD/ST"]
    
    GPU_LDST_ATOMICS["job_connectivity == NVSHMEMI_JOB_GPU_LDST_ATOMICS<br/>P2P with atomics support"]
    
    PROXY_ONLY["job_connectivity == NVSHMEMI_JOB_GPU_PROXY<br/>No P2P, proxy required"]
    
    PATH_LDST["Direct Load/Store Path<br/>nvshmem_ptr() returns peer address<br/>Direct GPU memory access"]
    
    PATH_IBGDA["IBGDA Device Path<br/>GPU-initiated RDMA<br/>ibgda_device.cuh functions"]
    
    PATH_PROXY["Proxy Path<br/>nvshmemi_proxy_ops_t<br/>CPU mediates via channel"]
    
    START --> CHECK_CONN
    CHECK_CONN --> GPU_LDST
    CHECK_CONN --> GPU_LDST_ATOMICS
    CHECK_CONN --> PROXY_ONLY
    
    GPU_LDST --> PATH_LDST
    GPU_LDST_ATOMICS --> PATH_LDST
    GPU_LDST_ATOMICS --> PATH_IBGDA
    PROXY_ONLY --> PATH_PROXY
```

**Sources:** [src/host/init/init.cu:1094-1164](), [src/include/non_abi/device/pt-to-pt/nvshmemi_transfer_api.cuh]()

The `job_connectivity` value is computed in `set_job_connectivity()` at [src/host/init/init.cu:1094-1164]() and considers:

- **NVSHMEMI_JOB_GPU_LDST**: All PEs can perform direct load/store via `nvshmem_ptr()`
- **NVSHMEMI_JOB_GPU_LDST_ATOMICS**: P2P connections support GPU-side atomics
- **NVSHMEMI_JOB_GPU_PROXY**: Operations must go through CPU proxy

Device-side code checks this at [src/include/non_abi/device/pt-to-pt/nvshmemi_transfer_api.cuh]() to route operations correctly.

## Transport Plugin Architecture

Transports implement the `nvshmem_transport` interface defined in [src/include/internal/host_transport/transport.h](). The transport manager dynamically loads plugins and builds a reachability matrix:

**Transport Plugin System**

```mermaid
graph TB
    subgraph "Transport Manager"
        MGR["nvshmemi_transport_init()<br/>transport.cpp:50-319"]
        DLOPEN["dlopen()<br/>Load .so file<br/>transport.cpp:179"]
        INIT_FN["nvshmemt_init()<br/>Plugin entry point<br/>transport.cpp:185-197"]
    end
    
    subgraph "Transport Interface"
        IFACE["struct nvshmem_transport<br/>Defined: transport.h"]
        
        HOST_OPS["host_ops<br/>- can_reach_peer<br/>- connect_endpoints<br/>- get_mem_handle<br/>- rma (put/get)<br/>- amo (atomics)<br/>- fence/quiet"]
        
        DEVICE_OPS["device_ops<br/>- device_init<br/>Not used in current impl"]
        
        ATTRS["Attributes<br/>- attr (CONNECTED)<br/>- cap[] per PE<br/>- n_devices<br/>- heap_base"]
    end
    
    subgraph "Plugin Implementations"
        P2P["P2P Transport<br/>nvshmemt_p2p_init<br/>p2p.cpp<br/>Direct GPU access"]
        
        IBRC["IBRC Plugin<br/>nvshmem_transport_ibrc.so<br/>ibrc.cpp<br/>Reliable Connected QPs"]
        
        IBGDA["IBGDA Plugin<br/>nvshmem_transport_ibgda.so<br/>ibgda.cpp<br/>GPU Direct Async"]
        
        UCX["UCX Plugin<br/>nvshmem_transport_ucx.so<br/>ucx.cpp<br/>UCX library"]
        
        LIBFAB["Libfabric Plugin<br/>nvshmem_transport_libfabric.so<br/>libfabric.cpp<br/>OFI API"]
    end
    
    subgraph "Memory Handle Cache"
        CACHE["transport_mem_handle_info_cache<br/>O(1) lookup by address<br/>transport_common.cpp:15-227"]
    end
    
    MGR --> DLOPEN
    DLOPEN --> INIT_FN
    INIT_FN --> IFACE
    
    IFACE --> HOST_OPS
    IFACE --> DEVICE_OPS
    IFACE --> ATTRS
    
    INIT_FN --> P2P
    INIT_FN --> IBRC
    INIT_FN --> IBGDA
    INIT_FN --> UCX
    INIT_FN --> LIBFAB
    
    P2P --> CACHE
    IBRC --> CACHE
    IBGDA --> CACHE
    UCX --> CACHE
    LIBFAB --> CACHE
```

**Sources:** [src/host/transport/transport.cpp:50-319](), [src/include/internal/host_transport/transport.h](), [src/modules/transport/common/transport_common.cpp:85-227]()

Transport loading sequence:

1. **Plugin Selection**: Based on `NVSHMEM_REMOTE_TRANSPORT` environment variable (defaults to IBRC)
2. **Dynamic Loading**: `dlopen()` loads shared object at [src/host/transport/transport.cpp:179]()
3. **Initialization**: Each transport's `nvshmemt_init()` function called at [src/host/transport/transport.cpp:185-197]()
4. **Capability Detection**: `can_reach_peer()` determines PE-to-PE connectivity
5. **Endpoint Connection**: `connect_endpoints()` sets up communication channels
6. **Memory Registration**: Heap registered via `get_mem_handle()`, cached in `transport_mem_handle_info_cache`

The reachability matrix `transport_map[pe1*npes + pe2]` (built at [src/host/topo/topo.cpp:438-506]()) is a bitmap indicating which transports can connect each PE pair.

## Memory Management Components

The memory subsystem uses a polymorphic design with three heap implementations sharing a common interface:

**Symmetric Heap Architecture**

```mermaid
graph TB
    subgraph "Abstract Interface"
        BASE["nvshmemi_symmetric_heap<br/>Abstract base class<br/>nvshmemi_symmetric_heap.hpp"]
        
        OPS["Operations<br/>- heap_malloc(size)<br/>- heap_calloc(size, count)<br/>- heap_align(size, alignment)<br/>- heap_deallocate(ptr)"]
        
        REG["Registration<br/>- register_heap_memory()<br/>- map_heap_range_by_size()"]
    end
    
    subgraph "Heap Implementations"
        VMM["nvshmemi_symmetric_heap_vidmem_dynamic_vmm<br/>CUDA Virtual Memory Manager<br/>cuMemAddressReserve/cuMemMap<br/>mem_heap.cpp:478-519"]
        
        STATIC["nvshmemi_symmetric_heap_vidmem_static_pinned<br/>cudaMalloc-backed<br/>mem_heap.cpp:344-352"]
        
        SYSMEM["nvshmemi_symmetric_heap_sysmem_static_shm<br/>POSIX shared memory<br/>mem_heap.cpp:354-388"]
    end
    
    subgraph "Memory Registration"
        P2P_REG["P2P Registration<br/>nvshmemi_mem_p2p_transport<br/>export_memory/import_memory<br/>CUDA IPC handles"]
        
        REMOTE_REG["Remote Registration<br/>nvshmemi_mem_remote_transport<br/>register_mem_handle<br/>Transport-specific handles"]
        
        CACHE_MGR["Handle Cache<br/>nvshmemt_mem_handle_cache_*<br/>transport_common.cpp:85-227"]
    end
    
    subgraph "Device State"
        DEV_STATE["nvshmemi_device_state_d<br/>Device-accessible structure<br/>- peer_heap_base_p2p[]<br/>- peer_heap_base_remote[]<br/>- heap_base<br/>- heap_size"]
    end
    
    BASE --> OPS
    BASE --> REG
    
    BASE --> VMM
    BASE --> STATIC
    BASE --> SYSMEM
    
    REG --> P2P_REG
    REG --> REMOTE_REG
    
    P2P_REG --> CACHE_MGR
    REMOTE_REG --> CACHE_MGR
    
    REG --> DEV_STATE
```

**Sources:** [src/include/internal/host/nvshmemi_symmetric_heap.hpp](), [src/host/mem/mem_heap.cpp:74-100](), [src/host/mem/mem_heap.cpp:344-388](), [src/host/mem/mem_heap.cpp:478-519](), [src/modules/transport/common/transport_common.cpp:85-227]()

Heap selection logic in `nvshmemi_init_symmetric_heap()` at [src/host/mem/mem_heap.cpp:74-100]():

- **VMM Heap**: Used when `NVSHMEM_USE_CUDA_VMM=1` or dynamically required
  - Provides fine-grained allocation control
  - Supports on-demand physical memory backing
  - Required for NVLS (NVLINK SHARP) features
  
- **Static VIDMEM**: Default GPU memory heap
  - Single `cudaMalloc()` allocation at [src/host/mem/mem_heap.cpp:344-352]()
  - Fixed size determined by `NVSHMEM_SYMMETRIC_SIZE`
  
- **SYSMEM**: System memory heap for intra-node only
  - POSIX shared memory (`shm_open()`) at [src/host/mem/mem_heap.cpp:354-388]()
  - Accessible by all PEs on same node
  - Registered with `cudaHostRegister()` for GPU access

Memory registration creates two handle types:
- **P2P handles**: CUDA IPC or VMM handles for direct GPU access
- **Remote handles**: Transport-specific (IB lkey/rkey, UCX rkey, etc.)

All handles cached in `transport_mem_handle_info_cache` for O(1) lookup during RMA operations.

## Device State Synchronization

The host-side `nvshmemi_state_t` structure is mirrored on the device as `nvshmemi_device_state_d`, a device-accessible constant structure:

**Device State Copy Mechanism**

```mermaid
graph LR
    subgraph "Host State"
        HOST["nvshmemi_state_t<br/>Host memory<br/>nvshmemi_state global"]
        
        HEAP_INFO["Heap Information<br/>- heap_base<br/>- heap_size<br/>- peer_heap_base arrays"]
        
        TRANS_INFO["Transport Info<br/>- job_connectivity<br/>- transport_bitmap<br/>- selected_transport arrays"]
        
        TEAM_INFO["Team Info<br/>- team pointers<br/>- psync arrays"]
    end
    
    subgraph "Device State"
        DEVICE["nvshmemi_device_state_d<br/>__constant__ memory<br/>Device-side accessible"]
        
        DEV_STRUCT["nvshmemi_device_host_state_t<br/>Mirrored structure<br/>nvshmem_types.h"]
    end
    
    subgraph "Update Mechanism"
        UPDATE["nvshmemi_update_device_state()<br/>init.cu:147-199"]
        
        CALLBACK["Registered Callbacks<br/>registered_device_state_cb<br/>init.cu:154-168"]
        
        MEMCPY["cudaMemcpy<br/>Host to Device<br/>init.cu:179-183"]
    end
    
    HOST --> HEAP_INFO
    HOST --> TRANS_INFO
    HOST --> TEAM_INFO
    
    UPDATE --> CALLBACK
    CALLBACK --> MEMCPY
    MEMCPY --> DEVICE
    
    DEVICE --> DEV_STRUCT
    
    HEAP_INFO -.synchronized.-> DEV_STRUCT
    TRANS_INFO -.synchronized.-> DEV_STRUCT
    TEAM_INFO -.synchronized.-> DEV_STRUCT
```

**Sources:** [src/host/init/init.cu:147-199](), [src/include/device_host/nvshmem_types.h]()

State synchronization flow:

1. **Callback Registration**: Device libraries register callbacks to receive state pointer via `nvshmemx_device_lib_init_cb`
2. **State Update**: `nvshmemi_update_device_state()` at [src/host/init/init.cu:147-199]() invoked after state changes
3. **Memory Copy**: `cudaMemcpy()` transfers `nvshmemi_device_host_state_t` to all registered device pointers at [src/host/init/init.cu:179-183]()
4. **Device Access**: GPU kernels read from `nvshmemi_device_state_d` via `__ldg()` or direct access

Critical fields synchronized to device:
- `peer_heap_base_p2p[]`: Base addresses for direct P2P access
- `peer_heap_base_remote[]`: Base addresses for remote operations
- `job_connectivity`: Communication path selection
- `selected_transport_for_rma[]`, `selected_transport_for_amo[]`: Per-PE transport indices

## Python Bindings Integration

The Python bindings (`nvshmem4py`) provide a three-tier architecture that bridges Python to the C/C++ implementation:

**Python Bindings Layers**

```mermaid
graph TB
    subgraph "Python User API"
        PY_COLL["nvshmem.core.collective<br/>reduce, broadcast, barrier<br/>Python functions"]
        
        PY_RMA["nvshmem.core.rma<br/>put, get, put_signal<br/>Python functions"]
        
        PY_MEM["nvshmem.core.NvshmemResource<br/>allocate, deallocate<br/>cuda.core.experimental.MemoryResource"]
    end
    
    subgraph "Low-Level Bindings"
        CYTHON["nvshmem.bindings<br/>Cython-generated C bindings<br/>Link to libnvshmem_host.so"]
        
        NUMBAST["nvshmem.bindings.device.numba<br/>Numbast-generated Numba bindings<br/>Link to libnvshmem_device.a"]
    end
    
    subgraph "Binding Generation"
        NUMBAST_TOOL["Numbast Tool<br/>C++ header parser<br/>addNumbast.cmake"]
        
        CONFIG["config_nvshmem.yml<br/>Generated from .j2 template<br/>Specifies functions to bind"]
        
        GENERATORS["generate_*.py<br/>generate_rma.py<br/>generate_coll.py<br/>High-level wrapper generators"]
    end
    
    subgraph "C/C++ NVSHMEM"
        HOST_LIB["libnvshmem_host.so<br/>Host-side operations"]
        
        DEVICE_LIB["libnvshmem_device.a<br/>Device-side operations<br/>Linked via Numba"]
    end
    
    PY_COLL --> CYTHON
    PY_RMA --> CYTHON
    PY_MEM --> CYTHON
    
    CYTHON --> HOST_LIB
    
    PY_COLL --> NUMBAST
    PY_RMA --> NUMBAST
    
    NUMBAST --> DEVICE_LIB
    
    NUMBAST_TOOL --> CONFIG
    CONFIG --> NUMBAST
    NUMBAST --> GENERATORS
    GENERATORS --> PY_COLL
    GENERATORS --> PY_RMA
```

**Sources:** [nvshmem4py/scripts/generate_pyproject_toml.py:1-106](), [cmake_config/NVSHMEMEnv.cmake:54-55]()

Python binding generation occurs at build time:
1. **Numbast Processing**: CMake invokes Numbast tool (configured at [cmake_config/NVSHMEMEnv.cmake:54-55]()) to parse C++ headers
2. **YAML Configuration**: `config_nvshmem.yml.j2` template generates configuration specifying which functions to bind
3. **Numba Bindings**: Numbast produces raw Numba-compatible bindings for device functions
4. **Wrapper Generation**: Python scripts (`generate_rma.py`, `generate_coll.py`) create ergonomic high-level APIs
5. **Package Assembly**: `generate_pyproject_toml.py` at [nvshmem4py/scripts/generate_pyproject_toml.py:1-106]() creates final package metadata

The bindings integrate with:
- **PyTorch**: Via tensor interop
- **CuPy**: Via ndarray support
- **CUDA Python**: Via `cuda.core.experimental.MemoryResource` interface

For detailed Python architecture, see [Python Bindings Architecture](#2.7).

## Summary

NVSHMEM's architecture provides:

- **Layered Abstraction**: Clean separation from API to hardware
- **Pluggable Transports**: Dynamic loading of network-specific implementations
- **Flexible Memory**: Three heap types for different use cases
- **Dual Programming Model**: Both host and device APIs
- **Path Optimization**: Runtime selection between P2P, IBGDA, and proxy paths
- **Language Bindings**: Native Python support via Cython and Numbast

The architecture enables NVSHMEM to support diverse GPU clusters (single-node NVLink, multi-node InfiniBand, cloud EFA) with a single unified API while optimizing communication paths based on available hardware capabilities.

---

