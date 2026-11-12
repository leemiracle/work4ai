<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-persistenced · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [COPYING](COPYING)
- [README](README)
- [nvidia-persistenced.c](nvidia-persistenced.c)
- [nvidia-persistenced.h](nvidia-persistenced.h)

</details>



This document provides a comprehensive overview of the nvidia-persistenced repository, which contains the source code for the NVIDIA Persistence Daemon. This daemon maintains persistent NVIDIA driver state across system operations and provides a foundation for managing GPU device persistence modes and NUMA memory management.

This overview covers the high-level architecture, key components, and their relationships. For detailed implementation information, see [Core Architecture](#2). For build system specifics, see [Build System](#3). For user-facing interfaces, see [User Interface](#4).

## Purpose and Scope

The `nvidia-persistenced` daemon serves as a critical system service that:

- **Maintains GPU Device State**: Keeps NVIDIA GPU devices in an active state to avoid driver initialization overhead
- **Manages NUMA Memory**: Controls onlining and offlining of GPU memory for NUMA-aware systems  
- **Provides RPC Interface**: Offers a client-server communication mechanism for device management
- **Integrates with System Services**: Works with init systems (systemd, SysV, Upstart) for automatic startup

The daemon primarily targets Linux systems with NVIDIA GPUs and integrates closely with the NVIDIA kernel driver and associated user-space libraries.

Sources: [nvidia-persistenced.c:1-26](), [README:1-33]()

## System Architecture

The `nvidia-persistenced` system follows a layered architecture where client applications communicate with the daemon through RPC calls, which then interact with NVIDIA libraries and kernel drivers.

### Core Components Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        NVIDIA_SMI["nvidia-smi"]
        CLIENT_APPS["Other Client Applications"]
    end
    
    subgraph "nvidia-persistenced Daemon"
        MAIN_DAEMON["main() - nvidia-persistenced.c"]
        RPC_SERVER["nvpd_prog_1/2() - RPC Server"]
        DEVICE_MGR["nvPdSetDevicePersistenceMode()"]
        NUMA_MGR["nvPdSetDeviceNumaStatus()"]
        OPTIONS_PARSER["parse_options()"]
    end
    
    subgraph "NVIDIA Libraries"
        NVIDIA_CFG["libnvidia-cfg.so"]
        NVIDIA_NUMA["nvidia-numa library"]
    end
    
    subgraph "Kernel Interface"
        NV_DRIVER["NVIDIA Kernel Driver"]
        GPU_HW["GPU Hardware"]
    end
    
    subgraph "System Integration"
        SYSLOG["syslog()"]
        PID_FILE["NVPD_PID_FILE"]
        UNIX_SOCKET["NVPD_SOCKET_PATH"]
    end
    
    NVIDIA_SMI --> RPC_SERVER
    CLIENT_APPS --> RPC_SERVER
    RPC_SERVER --> DEVICE_MGR
    RPC_SERVER --> NUMA_MGR
    MAIN_DAEMON --> OPTIONS_PARSER
    MAIN_DAEMON --> RPC_SERVER
    
    DEVICE_MGR --> NVIDIA_CFG
    NUMA_MGR --> NVIDIA_NUMA
    NVIDIA_CFG --> NV_DRIVER
    NVIDIA_NUMA --> NV_DRIVER
    NV_DRIVER --> GPU_HW
    
    MAIN_DAEMON --> SYSLOG
    MAIN_DAEMON --> PID_FILE
    RPC_SERVER --> UNIX_SOCKET
```

Sources: [nvidia-persistenced.c:42-49](), [nvidia-persistenced.h:57-59](), [nvidia-persistenced.c:998-1043]()

### Key Data Structures and State Management

The daemon manages device state through well-defined data structures that track both persistence mode and NUMA status for each GPU device.

```mermaid
graph TB
    subgraph "Device Management"
        NV_PD_DEVICE["NvPdDevice struct"]
        PCI_INFO["NvCfgPciDevice pci_info"]
        CFG_HANDLE["NvCfgDeviceHandle nv_cfg_handle"] 
        PERSIST_MODE["NvPersistenceMode mode"]
        UVM_MODE["NvUVMPersistenceMode uvm_pm_mode"]
        NUMA_STATUS["NvNumaStatus numa_status"]
        NUMA_INFO["NvNumaDevice numa_info"]
    end
    
    subgraph "Global State"
        DEVICES_ARRAY["NvPdDevice *devices"]
        NUM_DEVICES["int num_devices"]
        NVIDIA_CFG_LIB["void *libnvidia_cfg"]
        NV_CFG_API["nv_cfg_api struct"]
    end
    
    subgraph "Configuration"
        NV_PD_OPTIONS["NvPdOptions struct"]
        DEFAULT_MODE["persistence_mode"]
        UVM_PM["uvm_persistence_mode"]
        NVIDIA_CFG_PATH["nvidia_cfg_path"]
        UID_GID["uid_t uid, gid_t gid"]
    end
    
    NV_PD_DEVICE --> PCI_INFO
    NV_PD_DEVICE --> CFG_HANDLE
    NV_PD_DEVICE --> PERSIST_MODE
    NV_PD_DEVICE --> UVM_MODE
    NV_PD_DEVICE --> NUMA_STATUS
    NV_PD_DEVICE --> NUMA_INFO
    
    DEVICES_ARRAY --> NV_PD_DEVICE
    NVIDIA_CFG_LIB --> NV_CFG_API
    NV_PD_OPTIONS --> DEFAULT_MODE
    NV_PD_OPTIONS --> UVM_PM
    NV_PD_OPTIONS --> NVIDIA_CFG_PATH
    NV_PD_OPTIONS --> UID_GID
```

Sources: [nvidia-persistenced.c:56-64](), [nvidia-persistenced.c:67-84](), [nvidia-persistenced.h:36-43]()

## Communication Flow

The daemon operates through a request-response pattern where client applications send RPC commands that result in device state changes through the NVIDIA driver stack.

### RPC Command Processing Flow

```mermaid
sequenceDiagram
    participant Client as "Client Application"
    participant RPC as "nvpd_prog_1()"
    participant DevMgr as "nvPdSetDevicePersistenceMode()"
    participant GetDev as "get_device()"
    participant SetMode as "set_device_mode()"
    participant NvCfgAPI as "nv_cfg_api.*"
    participant Driver as "NVIDIA Driver"
    
    Client->>RPC: "RPC Call"
    RPC->>DevMgr: "domain, bus, slot, mode"
    DevMgr->>GetDev: "domain, bus, slot"
    GetDev-->>DevMgr: "NvPdDevice*"
    DevMgr->>SetMode: "device, mode"
    
    alt "Enable Persistence"
        SetMode->>NvCfgAPI: "open_pci_device()"
        NvCfgAPI->>Driver: "Device Open"
    else "Disable Persistence" 
        SetMode->>NvCfgAPI: "close_device()"
        NvCfgAPI->>Driver: "Device Close"
    end
    
    Driver-->>NvCfgAPI: "Status"
    NvCfgAPI-->>SetMode: "NvCfgBool"
    SetMode-->>DevMgr: "NvPdStatus"
    DevMgr-->>RPC: "Result"
    RPC-->>Client: "Response"
```

Sources: [nvidia-persistenced.c:109-140](), [nvidia-persistenced.c:343-421](), [nvidia-persistenced.c:208-223]()

## Daemon Lifecycle Management

The daemon follows a standard Unix daemon pattern with comprehensive initialization, signal handling, and cleanup procedures.

### Initialization and Shutdown Process

```mermaid
graph TD
    subgraph "Startup Sequence"
        PARSE_OPTS["parse_options()"]
        DAEMONIZE["daemonize()"]
        SETUP_CFG["setup_nvidia_cfg_api()"]
        SETUP_DEVS["setup_devices()"]
        SETUP_RPC["setup_rpc()"]
        SVC_RUN["svc_run()"]
    end
    
    subgraph "Runtime State"
        PID_FILE_LOCK["PID File Lock"]
        SIGNAL_HANDLER["signal_handler()"]
        RPC_DISPATCH["RPC Dispatch Loop"]
    end
    
    subgraph "Shutdown Sequence"
        SHUTDOWN_DAEMON["shutdown_daemon()"]
        CLOSE_DEVICES["Close NvCfgDeviceHandle"]
        UNLINK_SOCKET["unlink(NVPD_SOCKET_PATH)"]
        UNLINK_PID["unlink(NVPD_PID_FILE)"]
        DLCLOSE_LIB["dlclose(libnvidia_cfg)"]
    end
    
    PARSE_OPTS --> DAEMONIZE
    DAEMONIZE --> SETUP_CFG
    SETUP_CFG --> SETUP_DEVS
    SETUP_DEVS --> SETUP_RPC
    SETUP_RPC --> SVC_RUN
    
    SVC_RUN --> RPC_DISPATCH
    PID_FILE_LOCK -.-> SIGNAL_HANDLER
    SIGNAL_HANDLER --> SHUTDOWN_DAEMON
    
    SHUTDOWN_DAEMON --> CLOSE_DEVICES
    SHUTDOWN_DAEMON --> UNLINK_SOCKET
    SHUTDOWN_DAEMON --> UNLINK_PID
    SHUTDOWN_DAEMON --> DLCLOSE_LIB
```

Sources: [nvidia-persistenced.c:998-1043](), [nvidia-persistenced.c:799-996](), [nvidia-persistenced.c:487-584]()

## Key Features and Capabilities

### Device Persistence Management

The daemon's primary function is managing the persistence state of NVIDIA GPU devices. This involves:

- **Device Discovery**: Uses `nvCfgGetPciDevices()` to enumerate available NVIDIA GPUs
- **Persistence Control**: Implements `nvPdSetDevicePersistenceMode()` and `nvPdGetDevicePersistenceMode()`
- **UVM Integration**: Supports Unified Virtual Memory persistence through `nvCfgEnableUVMPersistence()`
- **PCI Device Addressing**: Manages devices by domain:bus:slot addressing scheme

### NUMA Memory Management

For NUMA-aware systems, the daemon provides:

- **Memory Onlining**: `nvNumaOnlineMemory()` brings GPU memory online
- **Memory Offlining**: `nvNumaOfflineMemory()` takes GPU memory offline  
- **Status Tracking**: Maintains `NvNumaStatus` for each device
- **Coordinated Operations**: Synchronizes persistence mode changes with NUMA state

Sources: [nvidia-persistenced.c:668-728](), [nvidia-persistenced.c:427-479](), [nvidia-persistenced.c:290-336]()

## Integration Points

The `nvidia-persistenced` system integrates with several external components:

| Component | Interface | Purpose |
|-----------|-----------|---------|
| **libnvidia-cfg.so** | Dynamic library loading via `dlopen()` | GPU device configuration and control |
| **NVIDIA Kernel Driver** | IOCTL interface through nvidia-cfg | Low-level hardware communication |
| **Init Systems** | Service files (systemd/SysV/Upstart) | Automatic daemon startup and management |
| **Syslog** | `syslog()` calls throughout codebase | System logging and monitoring |
| **Client Applications** | Unix domain socket RPC | External device management requests |

For detailed information about RPC communication, see [RPC Communication System](#2.2). For build system integration, see [Build System](#3). For deployment and service management, see [System Integration](#5).

Sources: [nvidia-persistenced.c:606-662](), [nvidia-persistenced.c:734-771](), [nvidia-persistenced.c:777-793]()

---

