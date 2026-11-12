<!-- source: DeepWiki mcp.deepwiki.com · repo linux-rdma/rdma-core · page 2 Core Libraries · fetched 2026-11-11 -->

# Core Libraries

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [debian/libibnetdisc5.symbols](debian/libibnetdisc5.symbols)
- [debian/libibumad-dev.install](debian/libibumad-dev.install)
- [debian/libibverbs1.symbols](debian/libibverbs1.symbols)
- [debian/librdmacm-dev.install](debian/librdmacm-dev.install)
- [debian/librdmacm1.symbols](debian/librdmacm1.symbols)
- [infiniband-diags/CMakeLists.txt](infiniband-diags/CMakeLists.txt)
- [infiniband-diags/ibdiag_common.c](infiniband-diags/ibdiag_common.c)
- [kernel-headers/rdma/rdma_user_ioctl.h](kernel-headers/rdma/rdma_user_ioctl.h)
- [libibnetdisc/CMakeLists.txt](libibnetdisc/CMakeLists.txt)
- [libibnetdisc/chassis.c](libibnetdisc/chassis.c)
- [libibnetdisc/chassis.h](libibnetdisc/chassis.h)
- [libibnetdisc/ibnetdisc.c](libibnetdisc/ibnetdisc.c)
- [libibnetdisc/ibnetdisc_cache.c](libibnetdisc/ibnetdisc_cache.c)
- [libibnetdisc/ibnetdisc_osd.h](libibnetdisc/ibnetdisc_osd.h)
- [libibnetdisc/internal.h](libibnetdisc/internal.h)
- [libibnetdisc/libibnetdisc.map](libibnetdisc/libibnetdisc.map)
- [libibnetdisc/man/CMakeLists.txt](libibnetdisc/man/CMakeLists.txt)
- [libibverbs/CMakeLists.txt](libibverbs/CMakeLists.txt)
- [libibverbs/cmd.c](libibverbs/cmd.c)
- [libibverbs/cmd_counters.c](libibverbs/cmd_counters.c)
- [libibverbs/cmd_cq.c](libibverbs/cmd_cq.c)
- [libibverbs/cmd_dm.c](libibverbs/cmd_dm.c)
- [libibverbs/cmd_fallback.c](libibverbs/cmd_fallback.c)
- [libibverbs/cmd_flow_action.c](libibverbs/cmd_flow_action.c)
- [libibverbs/cmd_ioctl.c](libibverbs/cmd_ioctl.c)
- [libibverbs/cmd_ioctl.h](libibverbs/cmd_ioctl.h)
- [libibverbs/cmd_mr.c](libibverbs/cmd_mr.c)
- [libibverbs/cmd_write.h](libibverbs/cmd_write.h)
- [libibverbs/compat-1_0.c](libibverbs/compat-1_0.c)
- [libibverbs/device.c](libibverbs/device.c)
- [libibverbs/driver.h](libibverbs/driver.h)
- [libibverbs/dummy_ops.c](libibverbs/dummy_ops.c)
- [libibverbs/ibdev_nl.c](libibverbs/ibdev_nl.c)
- [libibverbs/ibverbs.h](libibverbs/ibverbs.h)
- [libibverbs/init.c](libibverbs/init.c)
- [libibverbs/kern-abi.h](libibverbs/kern-abi.h)
- [libibverbs/libibverbs.map.in](libibverbs/libibverbs.map.in)
- [libibverbs/man/CMakeLists.txt](libibverbs/man/CMakeLists.txt)
- [libibverbs/man/ibv_alloc_dm.3](libibverbs/man/ibv_alloc_dm.3)
- [libibverbs/man/ibv_create_flow.3](libibverbs/man/ibv_create_flow.3)
- [libibverbs/man/ibv_dm_export_dmabuf_fd.3.md](libibverbs/man/ibv_dm_export_dmabuf_fd.3.md)
- [libibverbs/man/ibv_is_fork_initialized.3.md](libibverbs/man/ibv_is_fork_initialized.3.md)
- [libibverbs/man/ibv_reg_mr.3](libibverbs/man/ibv_reg_mr.3)
- [libibverbs/memory.c](libibverbs/memory.c)
- [libibverbs/verbs.c](libibverbs/verbs.c)
- [libibverbs/verbs.h](libibverbs/verbs.h)
- [librdmacm/CMakeLists.txt](librdmacm/CMakeLists.txt)
- [librdmacm/cma.c](librdmacm/cma.c)
- [librdmacm/ib.h](librdmacm/ib.h)
- [librdmacm/librdmacm.map](librdmacm/librdmacm.map)
- [librdmacm/man/rdma_establish.3.md](librdmacm/man/rdma_establish.3.md)
- [librdmacm/man/rdma_join_multicast_ex.3](librdmacm/man/rdma_join_multicast_ex.3)
- [librdmacm/rdma_cma.h](librdmacm/rdma_cma.h)
- [librdmacm/rdma_cma_abi.h](librdmacm/rdma_cma_abi.h)
- [util/open_cdev.c](util/open_cdev.c)
- [util/rdma_nl.c](util/rdma_nl.c)
- [util/rdma_nl.h](util/rdma_nl.h)

</details>



The rdma-core project provides four primary userspace libraries that form the foundation of RDMA programming on Linux. These libraries abstract hardware specifics and kernel interfaces, providing standardized APIs for different aspects of RDMA functionality.

| Library | Shared Object | Purpose | Primary Header |
|---------|--------------|---------|----------------|
| **libibverbs** | `libibverbs.so.1` | RDMA Verbs API - core data path operations | `infiniband/verbs.h` |
| **librdmacm** | `librdmacm.so.1` | Connection management with socket-like API | `rdma/rdma_cma.h` |
| **libibumad** | `libibumad.so.3` | Management datagrams for subnet administration | `infiniband/umad.h` |
| **libibnetdisc** | `libibnetdisc.so.5` | InfiniBand network topology discovery | `infiniband/ibnetdisc.h` |

For detailed information about:
- The libibverbs Verbs API implementation and provider architecture, see [libibverbs](#2.1)
- The RDMA Connection Manager library, see [librdmacm](#2.2)
- The InfiniBand network discovery library, see [libibnetdisc](#2.3)
- Hardware-specific provider implementations, see [RDMA Providers](#3)

Sources: [libibverbs/CMakeLists.txt:1-59](), [librdmacm/CMakeLists.txt:1-50](), [libibnetdisc/CMakeLists.txt:1-40]()

## Library Architecture Overview

**Architecture: Core Libraries and Their Kernel Interfaces**

```mermaid
graph TB
    subgraph "Application Layer"
        DATA_APP["Data Path Application<br/>(MPI, Storage, Networking)"]
        MGMT_APP["Management Application<br/>(OpenSM, Diagnostics)"]
        DIAG_APP["Diagnostic Tools<br/>(ibnetdiscover, perfquery)"]
    end
    
    subgraph "Core Libraries Layer"
        VERBS["libibverbs.so.1<br/>struct ibv_context<br/>ibv_post_send/recv<br/>ibv_poll_cq"]
        RDMACM["librdmacm.so.1<br/>struct rdma_cm_id<br/>rdma_connect<br/>rdma_create_qp"]
        UMAD["libibumad.so.3<br/>umad_open_port<br/>umad_send/recv<br/>Management Datagrams"]
        NETDISC["libibnetdisc.so.5<br/>ibnd_discover_fabric<br/>Topology Scanning"]
    end
    
    subgraph "Provider Interface"
        DRIVER_H["libibverbs/driver.h<br/>struct verbs_device_ops<br/>struct verbs_context_ops"]
    end
    
    subgraph "Hardware Providers"
        MLX5["libmlx5.so<br/>mlx5_alloc_context<br/>mlx5_post_send"]
        HNS["libhns.so"]
        EFA["libefa.so"]
        RXE["librxe.so<br/>(Software RoCE)"]
    end
    
    subgraph "Kernel Character Devices"
        UVERBS["/dev/infiniband/uverbsX<br/>Data path & resource mgmt"]
        RDMA_CM_DEV["/dev/infiniband/rdma_cm<br/>Connection events"]
        UMAD_DEV["/dev/infiniband/umadX<br/>Subnet management packets"]
        ISSM["/dev/infiniband/issmX<br/>Subnet management"]
    end
    
    DATA_APP --> VERBS
    DATA_APP --> RDMACM
    MGMT_APP --> UMAD
    DIAG_APP --> NETDISC
    
    RDMACM --> VERBS
    NETDISC --> UMAD
    
    VERBS --> DRIVER_H
    DRIVER_H -.loads.-> MLX5
    DRIVER_H -.loads.-> HNS
    DRIVER_H -.loads.-> EFA
    DRIVER_H -.loads.-> RXE
    
    VERBS --> UVERBS
    RDMACM --> RDMA_CM_DEV
    UMAD --> UMAD_DEV
    UMAD --> ISSM
    
    MLX5 --> UVERBS
    HNS --> UVERBS
    EFA --> UVERBS
    RXE --> UVERBS
```

Sources: [libibverbs/verbs.h:95-113](), [libibverbs/driver.h:218-267](), [librdmacm/cma.c:101-121]()

## Core Library Descriptions

### libibverbs: Verbs API Library

The `libibverbs` library provides the fundamental RDMA Verbs API, implementing direct userspace access to RDMA hardware. It is the lowest-level library that all RDMA applications use, either directly or indirectly.

**Key Responsibilities:**
- Device enumeration and context creation (`ibv_get_device_list`, `ibv_open_device`) [libibverbs/device.c:54-96]()
- Resource allocation (Protection Domains, Memory Regions, Queue Pairs, Completion Queues) [libibverbs/verbs.h:1700-1800]()
- Data path operations (`ibv_post_send`, `ibv_post_recv`, `ibv_poll_cq`) [libibverbs/verbs.h:1850-1950]()
- Provider plugin architecture for hardware-specific implementations [libibverbs/driver.h:295-479]()
- Memory registration and management [libibverbs/cmd.c:99-138]()

**Location:** [libibverbs/]()  
**Build Artifacts:** `libibverbs.so.1.16.x` [libibverbs/CMakeLists.txt:22-24]()  
**Symbol Versioning:** IBVERBS_1.0 through IBVERBS_1.16 [libibverbs/libibverbs.map.in:1-178]()

The library uses a provider plugin system where hardware-specific implementations (e.g., `libmlx5.so`) are dynamically loaded based on detected hardware. See [libibverbs](#2.1) for detailed documentation.

Sources: [libibverbs/verbs.h:1-100](), [libibverbs/driver.h:295-324](), [libibverbs/CMakeLists.txt:1-65]()

### librdmacm: Connection Manager Library

The `librdmacm` library provides connection-oriented semantics on top of libibverbs, offering a socket-like API for RDMA connection establishment and management.

**Key Responsibilities:**
- Address resolution and binding [librdmacm/cma.c:187-205]()
- Connection establishment and event-driven management [librdmacm/cma.c:136-141]()
- Automatic Queue Pair creation and integration with Verbs [librdmacm/cma.c:113-121]()
- Support for both InfiniBand and RoCE/iWARP transports [librdmacm/cma.c:247-254]()

**Location:** [librdmacm/]()  
**Character Device:** `/dev/infiniband/rdma_cm` [librdmacm/cma.c:148-150]()

The library handles the complexities of RDMA connection setup, making it easier for applications to establish reliable connections similar to TCP sockets. See [librdmacm](#2.2) for detailed documentation.

Sources: [librdmacm/cma.c:1-254](), [librdmacm/rdma_cma.h:1-100]()

### libibnetdisc: Network Discovery Library

The `libibnetdisc` library provides InfiniBand fabric topology discovery and analysis capabilities.

**Key Responsibilities:**
- Fabric topology discovery and scanning [libibnetdisc/ibnetdisc.c:1-100]()
- Node and port iteration across the fabric
- Fabric configuration caching and chassis management [libibnetdisc/chassis.c:1-50]()

**Location:** [libibnetdisc/]()  
**Dependencies:** `libibumad.so.3`

Diagnostic tools like `ibnetdiscover` use this library to map out the complete InfiniBand network topology. See [libibnetdisc](#2.3) for detailed documentation.

Sources: [libibnetdisc/ibnetdisc.c:1-100](), [libibnetdisc/CMakeLists.txt:1-40]()

## libibverbs Provider Plugin Architecture

The libibverbs library uses a dynamic provider plugin system to support multiple hardware vendors through a common API.

**Provider Plugin Loading and Operation Dispatch**

```mermaid
graph TB
    subgraph "libibverbs Core"
        VERBS_H["libibverbs/verbs.h<br/>ibv_post_send<br/>ibv_poll_cq<br/>ibv_reg_mr"]
        DRIVER_H["libibverbs/driver.h<br/>struct verbs_device_ops<br/>struct verbs_context_ops"]
        INIT_C["libibverbs/init.c<br/>ibverbs_init<br/>load_drivers"]
        DEVICE_C["libibverbs/device.c<br/>ibv_open_device<br/>try_drivers"]
        VERBS_C["libibverbs/verbs.c<br/>Operation dispatch<br/>get_ops()->create_qp()"]
        DUMMY_OPS["libibverbs/dummy_ops.c<br/>Default EOPNOTSUPP<br/>implementations"]
    end
    
    subgraph "Provider Registration"
        MLX5_SO["libmlx5.so"]
        HNS_SO["libhns.so"]
        EFA_SO["libefa.so"]
        PROVIDER_DRIVER["PROVIDER_DRIVER macro<br/>__attribute__((constructor))"]
        REGISTER["verbs_register_driver<br/>Add to driver_list"]
    end
    
    subgraph "Runtime Loading"
        DLOPEN["dlopen() providers"]
        MATCH["match_modalias()<br/>Check PCI ID or driver_id"]
        ALLOC_CTX["verbs_init_context()<br/>Create provider context"]
    end
    
    VERBS_H --> VERBS_C
    VERBS_C --> DRIVER_H
    DRIVER_H --> DUMMY_OPS
    
    INIT_C --> DLOPEN
    DLOPEN --> MLX5_SO
    DLOPEN --> HNS_SO
    DLOPEN --> EFA_SO
    
    MLX5_SO --> PROVIDER_DRIVER
    HNS_SO --> PROVIDER_DRIVER
    EFA_SO --> PROVIDER_DRIVER
    
    PROVIDER_DRIVER --> REGISTER
    REGISTER --> INIT_C
    
    DEVICE_C --> MATCH
    MATCH --> ALLOC_CTX
    ALLOC_CTX --> VERBS_C
```

### Provider Operation Tables

Each provider implements operation structures defined in `libibverbs/driver.h`:

- **`struct verbs_device_ops`**: Handles device matching and context allocation [libibverbs/driver.h:240-255]()
- **`struct verbs_context_ops`**: Contains the function pointers for all verbs operations (e.g., `post_send`, `poll_cq`) [libibverbs/ibverbs.h:86-88]()

Operations not implemented by a provider default to `libibverbs/dummy_ops.c` which returns `EOPNOTSUPP`. [libibverbs/verbs.c:163-172]()

Sources: [libibverbs/driver.h:218-267](), [libibverbs/init.c:240-255](), [libibverbs/device.c:230-258]()

## Library Initialization and Command Dispatch

**Device Discovery and Context Creation Flow**

```mermaid
sequenceDiagram
    participant App as "Application"
    participant Verbs as "libibverbs/device.c<br/>ibv_get_device_list"
    participant Init as "libibverbs/init.c<br/>ibverbs_init"
    participant Provider as "Provider (e.g. libmlx5)"
    participant Kernel as "/dev/infiniband/uverbs0"
    
    App->>Verbs: ibv_get_device_list()
    Verbs->>Init: ibverbs_init()
    Init->>Init: find_sysfs_devs()
    Init->>Init: load_drivers()
    Init-->>Verbs: driver_list populated
    
    loop For each sysfs device
        Verbs->>Init: match_modalias()
        Init-->>Verbs: Match Result
    end
    
    Verbs-->>App: struct ibv_device **list
    
    App->>Verbs: ibv_open_device(dev)
    Verbs->>Kernel: open() -> cmd_fd
    Verbs->>Verbs: verbs_init_context()
    Verbs->>Provider: alloc_context()
    Provider->>Kernel: execute_ioctl(GET_CONTEXT)
    Provider-->>Verbs: struct verbs_context *
    Verbs-->>App: struct ibv_context *
```

### Command Dispatch Mechanisms

The core libraries communicate with the kernel via two primary methods:

1. **Legacy Write-Based Commands**: Uses `write()` syscall with fixed structures [libibverbs/cmd.c:56-57]()
2. **Modern IOCTL-Based Commands**: Uses `ioctl()` with extensible attributes [libibverbs/device.c:203-223]()

The `execute_cmd_write` and `execute_ioctl` functions abstract these kernel interfaces for the providers. [libibverbs/cmd.c:56-57](), [libibverbs/device.c:217-218]()

Sources: [libibverbs/device.c:54-96](), [libibverbs/init.c:204-238](), [libibverbs/cmd.c:50-65]()

## ABI Versioning and Compatibility

The libibverbs library uses ELF symbol versioning to maintain ABI stability. [libibverbs/libibverbs.map.in:1-183]()

- **Public API**: Symbols like `ibv_open_device` are versioned (e.g., `IBVERBS_1.1`). [libibverbs/libibverbs.map.in:53-101]()
- **Private Provider ABI (PABI)**: Internal symbols used between libibverbs and providers are versioned using `IBVERBS_PRIVATE_@IBVERBS_PABI_VERSION@`. [libibverbs/libibverbs.map.in:183-264]()
- **Fork Safety**: `ibv_fork_init()` enables `MADV_DONTFORK` handling for memory regions. [libibverbs/verbs.h:142-146]()

Sources: [libibverbs/libibverbs.map.in:1-264](), [debian/libibverbs1.symbols:1-131](), [libibverbs/kern-abi.h:48-49]()

---

