<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/go-gpuallocator · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [go.mod](go.mod)
- [gpuallocator/allocator.go](gpuallocator/allocator.go)
- [gpuallocator/besteffort_policy.go](gpuallocator/besteffort_policy.go)
- [gpuallocator/device.go](gpuallocator/device.go)
- [internal/links/device.go](internal/links/device.go)

</details>



The go-gpuallocator repository provides an intelligent GPU resource allocation system designed for NVIDIA GPU environments. It implements topology-aware allocation policies that consider NVLink connectivity, PCIe hierarchy, and peer-to-peer communication capabilities to optimize GPU assignments for multi-GPU workloads.

This document covers the high-level system architecture and core components. For detailed information about specific subsystems, see [Device Discovery and Management](#2.1), [Allocation Policies](#2.2), [NVIDIA Integration Layer](#3), and [API Reference](#6).

## System Architecture

The go-gpuallocator system follows a layered architecture that abstracts hardware discovery through NVIDIA's NVML library and provides pluggable allocation policies:

```mermaid
graph TB
    subgraph "Application Layer"
        APP["Client Applications"]
    end
    
    subgraph "Core Allocation System"
        ALLOC["Allocator struct<br/>gpuallocator/allocator.go"]
        POLICY["Policy interface<br/>BestEffortPolicy<br/>SimplePolicy<br/>StaticDGXPolicy"]
    end
    
    subgraph "Device Management"
        DEVICE["Device struct<br/>DeviceList<br/>DeviceSet"]
        TOPO["P2PLink topology<br/>internal/links"]
    end
    
    subgraph "NVIDIA Integration"
        NVLIB["go-nvlib device interface<br/>MIG support"]
        NVML["go-nvml bindings<br/>NVML API wrapper"]
    end
    
    subgraph "Hardware Layer"
        GPU["NVIDIA GPUs<br/>NVLink interconnects<br/>PCIe topology"]
    end
    
    APP --> ALLOC
    ALLOC --> POLICY
    ALLOC --> DEVICE
    POLICY --> DEVICE
    DEVICE --> TOPO
    DEVICE --> NVLIB
    DEVICE --> NVML
    NVLIB --> GPU
    NVML --> GPU
```

Sources: [gpuallocator/allocator.go:1-123](), [gpuallocator/device.go:1-259](), [gpuallocator/besteffort_policy.go:1-399](), [internal/links/device.go:1-229]()

## Core Components

The system is built around several key components that work together to provide intelligent GPU allocation:

```mermaid
graph LR
    subgraph "Device Representation"
        DEV["Device struct<br/>Index: int<br/>UUID: string<br/>Links: map[int][]P2PLink"]
        DEVLIST["DeviceList []*Device"]
        DEVSET["DeviceSet map[string]*Device"]
    end
    
    subgraph "Allocation Engine" 
        ALLOCATOR["Allocator struct<br/>GPUs: []*Device<br/>policy: Policy<br/>remaining: DeviceSet<br/>allocated: DeviceSet"]
        POL_INT["Policy interface<br/>Allocate() method"]
    end
    
    subgraph "Policy Implementations"
        BESTEFFORT["bestEffortPolicy<br/>Score-based optimization<br/>Topology-aware"]
        SIMPLE["simplePolicy<br/>Sequential allocation"]
        STATICDGX["staticDGXPolicy<br/>Predefined patterns"]
    end
    
    subgraph "Topology Information"
        P2PLINK["P2PLink struct<br/>GPU: *Device<br/>Type: P2PLinkType"]
        LINKTYPE["P2PLinkType constants<br/>NVLink counts<br/>PCIe topology levels"]
    end
    
    DEV --> DEVLIST
    DEV --> DEVSET
    DEV --> P2PLINK
    P2PLINK --> LINKTYPE
    
    ALLOCATOR --> POL_INT
    ALLOCATOR --> DEVSET
    
    POL_INT --> BESTEFFORT
    POL_INT --> SIMPLE  
    POL_INT --> STATICDGX
    
    BESTEFFORT --> P2PLINK
```

Sources: [gpuallocator/device.go:16-73](), [gpuallocator/allocator.go:12-32](), [gpuallocator/besteffort_policy.go:13-18](), [internal/links/device.go:26-57]()

## Device Discovery and Topology Mapping

The system discovers GPUs and maps their interconnect topology through NVIDIA's NVML library:

```mermaid
graph TB
    subgraph "Discovery Process"
        START["NewDevices() call"]
        INIT["nvml.Init()"]
        ENUM["devicelib.GetDevices()"]
        CREATE["newDevice() for each GPU"]
        TOPO["Build P2P topology map"]
    end
    
    subgraph "Device Construction"
        NVDEV["nvml.Device"]
        UUID_GET["GetUUID()"]
        PCI_GET["GetPciInfo()"]
        DEV_STRUCT["Device struct creation"]
    end
    
    subgraph "Topology Discovery"
        P2P_DISC["GetP2PLink() for each pair"]
        NV_DISC["GetNVLink() for each pair"]
        LINK_MAP["Links map population"]
    end
    
    START --> INIT
    INIT --> ENUM
    ENUM --> CREATE
    CREATE --> TOPO
    
    CREATE --> NVDEV
    NVDEV --> UUID_GET
    NVDEV --> PCI_GET
    UUID_GET --> DEV_STRUCT
    PCI_GET --> DEV_STRUCT
    
    TOPO --> P2P_DISC
    TOPO --> NV_DISC
    P2P_DISC --> LINK_MAP
    NV_DISC --> LINK_MAP
```

Sources: [gpuallocator/device.go:75-137](), [internal/links/device.go:115-201]()

## Allocation Workflow

The allocation process follows a clear workflow from request to GPU assignment:

| Stage | Component | Function | Purpose |
|-------|-----------|----------|---------|
| 1. Request | `Allocator` | `Allocate(num int)` | Client requests N GPUs |
| 2. Policy Selection | `Policy` interface | `Allocate(available, required, size)` | Apply allocation strategy |
| 3. Device Selection | Policy implementation | Score calculation/selection logic | Choose optimal GPU set |
| 4. State Update | `Allocator` | `AllocateSpecific()` | Move GPUs from remaining to allocated |
| 5. Return | `Allocator` | Return `[]*Device` | Provide allocated GPU list |

Sources: [gpuallocator/allocator.go:83-116]()

## Integration with NVIDIA Ecosystem

The system integrates with NVIDIA's software stack through well-defined interfaces:

```mermaid
graph TB
    subgraph "Go Module Dependencies"
        MOD["github.com/NVIDIA/go-gpuallocator<br/>go.mod"]
        NVLIB_DEP["github.com/NVIDIA/go-nvlib v0.7.3"]
        NVML_DEP["github.com/NVIDIA/go-nvml v0.12.9-0"]
    end
    
    subgraph "Interface Abstraction"
        NVLIB_IF["nvlib/device.Device interface<br/>High-level GPU management"]
        NVML_IF["nvml.Interface<br/>Low-level NVML bindings"]
    end
    
    subgraph "Hardware Interaction"
        NVML_LIB["NVIDIA NVML Library<br/>libnvidia-ml.so"]
        GPU_HW["NVIDIA GPU Hardware<br/>Topology discovery<br/>Device enumeration"]
    end
    
    MOD --> NVLIB_DEP
    MOD --> NVML_DEP
    
    NVLIB_DEP --> NVLIB_IF
    NVML_DEP --> NVML_IF
    
    NVLIB_IF --> NVML_LIB
    NVML_IF --> NVML_LIB
    NVML_LIB --> GPU_HW
```

Sources: [go.mod:1-17](), [gpuallocator/device.go:10-14]()

## Key Features

The go-gpuallocator system provides several important capabilities:

- **Topology-Aware Allocation**: Uses NVLink and PCIe topology information to optimize GPU selections for communication efficiency
- **Pluggable Policies**: Supports multiple allocation strategies through the `Policy` interface
- **Device State Management**: Tracks available and allocated GPUs through `DeviceSet` collections  
- **P2P Link Discovery**: Automatically discovers and maps inter-GPU communication links
- **NVML Integration**: Leverages NVIDIA's official management library for hardware interaction

For implementation details of these features, see [Core GPU Allocation System](#2), [NVIDIA Integration Layer](#3), and [API Reference](#6).

Sources: [gpuallocator/allocator.go:12-32](), [gpuallocator/besteffort_policy.go:20-95](), [internal/links/device.go:26-139]()

---

