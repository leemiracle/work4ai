<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-persistenced · page 2 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [nvidia-persistenced.c](nvidia-persistenced.c)
- [nvidia-persistenced.h](nvidia-persistenced.h)
- [nvpd_rpc.h](nvpd_rpc.h)

</details>



This document describes the overall system architecture of nvidia-persistenced, explaining how the main components interact to provide persistent NVIDIA driver state management. It covers the daemon's internal structure, communication interfaces, and device management subsystems.

For details on specific daemon implementation and lifecycle management, see [Main Daemon Implementation](#2.1). For RPC protocol specifications, see [RPC Communication System](#2.2). For NUMA memory management specifics, see [NUMA Memory Management](#2.4).

## System Overview

nvidia-persistenced is a daemon that maintains persistent driver state for NVIDIA GPUs. The architecture follows a layered design with clear separation between the user interface (RPC), core daemon logic, device management, and hardware abstraction layers.

```mermaid
graph TB
    subgraph "Client Layer"
        NVIDIA_SMI["nvidia-smi"]
        OTHER_CLIENTS["Other Management Tools"]
    end
    
    subgraph "nvidia-persistenced Daemon"
        RPC_SERVER["RPC Server\n(nvpd_prog_1/2)"]
        MAIN_DAEMON["Main Daemon\n(nvidia-persistenced.c)"]
        DEVICE_MGR["Device Manager\n(NvPdDevice array)"]
        OPTIONS["Option Parser\n(parse_options)"]
    end
    
    subgraph "Hardware Abstraction"
        NVIDIA_CFG["libnvidia-cfg.so\n(nv_cfg_api)"]
        NUMA_LIB["nvidia-numa library\n(nvNumaOnlineMemory)"]
    end
    
    subgraph "Kernel Interface"
        IOCTL_LAYER["IOCTL Interface\n(NV_ESC_*)"]
        NVIDIA_DRIVER["NVIDIA Kernel Driver"]
    end
    
    subgraph "System Resources"
        UNIX_SOCKET["Unix Domain Socket\n(/var/run/nvidia-persistenced/socket)"]
        PID_FILE["PID File\n(/var/run/nvidia-persistenced/nvidia-persistenced.pid)"]
        SYSLOG["System Logging"]
    end
    
    NVIDIA_SMI --> RPC_SERVER
    OTHER_CLIENTS --> RPC_SERVER
    RPC_SERVER --> MAIN_DAEMON
    MAIN_DAEMON --> DEVICE_MGR
    MAIN_DAEMON --> OPTIONS
    DEVICE_MGR --> NVIDIA_CFG
    DEVICE_MGR --> NUMA_LIB
    NVIDIA_CFG --> IOCTL_LAYER
    NUMA_LIB --> IOCTL_LAYER
    IOCTL_LAYER --> NVIDIA_DRIVER
    RPC_SERVER -.-> UNIX_SOCKET
    MAIN_DAEMON -.-> PID_FILE
    MAIN_DAEMON -.-> SYSLOG
```

**Sources:** [nvidia-persistenced.c:1-1044](), [nvidia-persistenced.h:28-64](), [nvpd_rpc.h:1-157]()

## Core Data Structures

The daemon's state management centers around the `NvPdDevice` structure, which encapsulates all device-specific information and state.

### Device State Management

```mermaid
classDiagram
    class NvPdDevice {
        +NvCfgDeviceHandle nv_cfg_handle
        +NvCfgPciDevice pci_info
        +NvPersistenceMode mode
        +NvUVMPersistenceMode uvm_pm_mode
        +NvNumaStatus numa_status
        +NvNumaDevice numa_info
    }
    
    class NvCfgPciDevice {
        +int domain
        +int bus
        +int slot
        +int function
    }
    
    class NvNumaDevice {
        +int fd
        +NvCfgPciDevice* pci_info
    }
    
    class NvPdOptions {
        +NvPersistenceMode persistence_mode
        +NvUVMPersistenceMode uvm_persistence_mode
        +char* nvidia_cfg_path
        +int verbose
        +uid_t uid
        +gid_t gid
    }
    
    NvPdDevice --> NvCfgPciDevice
    NvPdDevice --> NvNumaDevice
    NvNumaDevice --> NvCfgPciDevice
```

| Field | Purpose | States |
|-------|---------|--------|
| `nv_cfg_handle` | Device handle for nvidia-cfg operations | NULL (closed) or valid handle |
| `mode` | Persistence mode state | `NV_PERSISTENCE_MODE_DISABLED/ENABLED` |
| `uvm_pm_mode` | UVM persistence state | `NV_UVM_PERSISTENCE_MODE_DISABLED/ENABLED` |
| `numa_status` | NUMA memory state | `NV_NUMA_STATUS_OFFLINE/ONLINE` |

**Sources:** [nvidia-persistenced.c:56-64](), [nvidia-persistenced.h:36-43](), [nvpd_rpc.h:33-82]()

## Component Interaction Flow

The daemon processes client requests through a well-defined flow that coordinates persistence mode changes with NUMA memory management.

### Device Persistence Mode Control Flow

```mermaid
sequenceDiagram
    participant Client as "Client (nvidia-smi)"
    participant RPC as "RPC Server"
    participant Daemon as "nvPdSetDevicePersistenceMode"
    participant DevMgr as "set_device_mode"
    participant NumaMgr as "set_device_numa_status"
    participant NvCfg as "nv_cfg_api"
    participant Driver as "Kernel Driver"
    
    Client->>RPC: SetPersistenceMode request
    RPC->>Daemon: nvPdSetDevicePersistenceMode(domain, bus, slot, mode)
    Daemon->>Daemon: get_device(domain, bus, slot)
    
    Note over Daemon: Set device mode before NUMA state
    Daemon->>DevMgr: set_device_mode(device, mode)
    
    alt Mode: ENABLED
        DevMgr->>NvCfg: open_pci_device()
        NvCfg->>Driver: Device open IOCTL
        opt UVM Persistence Enabled
            DevMgr->>NvCfg: nvCfgEnableUVMPersistence()
        end
    else Mode: DISABLED
        opt UVM Persistence Active
            DevMgr->>NvCfg: nvCfgDisableUVMPersistence()
        end
        DevMgr->>NvCfg: close_device()
    end
    
    DevMgr-->>Daemon: Status
    Daemon->>NumaMgr: set_device_numa_status(device, numa_status)
    NumaMgr->>Driver: NUMA online/offline operations
    NumaMgr-->>Daemon: Status
    
    alt Failure Recovery
        Daemon->>DevMgr: set_device_mode(device, old_mode)
    end
    
    Daemon-->>RPC: NvPdStatus
    RPC-->>Client: Response
```

**Sources:** [nvidia-persistenced.c:109-140](), [nvidia-persistenced.c:343-421](), [nvidia-persistenced.c:427-479]()

## Dynamic Library Integration

The daemon dynamically loads the nvidia-cfg library to interface with the NVIDIA kernel driver, providing runtime flexibility and dependency management.

### Library Symbol Resolution

```mermaid
graph LR
    subgraph "Dynamic Loading Process"
        DLOPEN["dlopen(libnvidia-cfg.so.1)"]
        SYMBOL_LOAD["load_nvidia_cfg_sym()"]
        API_STRUCT["nv_cfg_api structure"]
    end
    
    subgraph "Required Symbols"
        GET_PCI["nvCfgGetPciDevices"]
        OPEN_DEV["nvCfgOpenPciDevice"]
        CLOSE_DEV["nvCfgCloseDevice"]
        ENABLE_UVM["nvCfgEnableUVMPersistence"]
        DISABLE_UVM["nvCfgDisableUVMPersistence"]
    end
    
    DLOPEN --> SYMBOL_LOAD
    SYMBOL_LOAD --> GET_PCI
    SYMBOL_LOAD --> OPEN_DEV
    SYMBOL_LOAD --> CLOSE_DEV
    SYMBOL_LOAD --> ENABLE_UVM
    SYMBOL_LOAD --> DISABLE_UVM
    GET_PCI --> API_STRUCT
    OPEN_DEV --> API_STRUCT
    CLOSE_DEV --> API_STRUCT
    ENABLE_UVM --> API_STRUCT
    DISABLE_UVM --> API_STRUCT
```

The `nv_cfg_api` structure provides function pointers to dynamically loaded symbols:

```c
static struct {
    NvCfgBool (*get_pci_devices)(int *, NvCfgPciDevice **);
    NvCfgBool (*open_pci_device)(int, int, int, int, NvCfgDeviceHandle *);
    NvCfgBool (*close_device)(NvCfgDeviceHandle);
    unsigned int (*nvCfgEnableUVMPersistence)(NvCfgDeviceHandle);
    unsigned int (*nvCfgDisableUVMPersistence)(NvCfgDeviceHandle);
} nv_cfg_api;
```

**Sources:** [nvidia-persistenced.c:78-84](), [nvidia-persistenced.c:590-600](), [nvidia-persistenced.c:606-662]()

## Daemon Lifecycle Management

The daemon follows a structured initialization and shutdown sequence to ensure proper resource management and cleanup.

### Initialization Sequence

```mermaid
graph TD
    START["main()"] --> PARSE["parse_options()"]
    PARSE --> DAEMON["daemonize(uid, gid)"]
    DAEMON --> PIPE_SETUP["Setup init pipe"]
    PIPE_SETUP --> FORK["fork()"]
    
    FORK --> PARENT["Parent Process"]
    FORK --> CHILD["Child Process"]
    
    PARENT --> WAIT["wait_for_init_complete()"]
    WAIT --> PARENT_EXIT["exit()"]
    
    CHILD --> SETSID["setsid()"]
    SETSID --> CLOSE_FDS["Close std file descriptors"]
    CLOSE_FDS --> SETUP_LOG["Setup syslog"]
    SETUP_LOG --> CREATE_DIR["Create runtime directory"]
    CREATE_DIR --> DROP_PERMS["Drop permissions"]
    DROP_PERMS --> LOCK_PID["Lock PID file"]
    LOCK_PID --> SETUP_CFG["setup_nvidia_cfg_api()"]
    SETUP_CFG --> SETUP_DEVS["setup_devices()"]
    SETUP_DEVS --> SETUP_RPC["setup_rpc()"]
    SETUP_RPC --> INIT_COMPLETE["init_complete()"]
    INIT_COMPLETE --> SVC_RUN["svc_run()"]
```

### Resource Management

| Resource | Creation | Cleanup Function | Location |
|----------|----------|------------------|----------|
| PID File | `daemonize()` | `shutdown_daemon()` | `/var/run/nvidia-persistenced/nvidia-persistenced.pid` |
| Unix Socket | `setup_rpc()` | `shutdown_daemon()` | `/var/run/nvidia-persistenced/socket` |
| Device Handles | `setup_devices()` | `shutdown_daemon()` | In-memory `devices` array |
| Library Handle | `setup_nvidia_cfg_api()` | `shutdown_daemon()` | `libnvidia_cfg` pointer |

**Sources:** [nvidia-persistenced.c:799-996](), [nvidia-persistenced.c:487-584](), [nvidia-persistenced.c:998-1044]()

## Error Handling and Status Management

The daemon implements comprehensive error handling with standardized status codes and logging integration.

### Status Code Hierarchy

```mermaid
graph TD
    NVPD_SUCCESS["NVPD_SUCCESS (0)"]
    
    subgraph "System Errors"
        ERR_DAEMON["NVPD_ERR_DAEMON_NOT_PRESENT"]
        ERR_IO["NVPD_ERR_IO"]
        ERR_PERMS["NVPD_ERR_PERMISSIONS"]
        ERR_RPC["NVPD_ERR_RPC"]
        ERR_RESOURCES["NVPD_ERR_INSUFFICIENT_RESOURCES"]
    end
    
    subgraph "Device Errors"
        ERR_DEVICE["NVPD_ERR_DEVICE_NOT_FOUND"]
        ERR_DRIVER["NVPD_ERR_DRIVER"]
        ERR_NUMA["NVPD_ERR_NUMA_FAILURE"]
    end
    
    subgraph "Input Errors"
        ERR_INVALID["NVPD_ERR_INVALID_ARGUMENT"]
        ERR_USER["NVPD_ERR_USER_NOT_FOUND"]
    end
    
    ERR_UNKNOWN["NVPD_ERR_UNKNOWN"]
```

**Sources:** [nvpd_rpc.h:17-31]()

---

