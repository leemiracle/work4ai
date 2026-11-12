<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/go-gpuallocator · page 2 Core GPU Allocation System · fetched 2026-10-26 -->

# Core GPU Allocation System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [gpuallocator/allocator.go](gpuallocator/allocator.go)
- [gpuallocator/besteffort_policy.go](gpuallocator/besteffort_policy.go)
- [gpuallocator/device.go](gpuallocator/device.go)
- [internal/links/device.go](internal/links/device.go)

</details>



This document covers the core components of the go-gpuallocator system that handle GPU device discovery, allocation policies, and resource management. The system provides intelligent NVIDIA GPU allocation based on topology-aware policies that consider P2P links, NVLinks, and GPU interconnectivity.

For NVIDIA integration details, see [NVIDIA Integration Layer](#3). For testing infrastructure, see [Testing Framework](#4). For public APIs, see [API Reference](#6).

## System Architecture

The Core GPU Allocation System consists of three primary components that work together to provide intelligent GPU resource allocation:

```mermaid
graph TB
    subgraph "Device Management Layer"
        Device["Device struct<br/>UUID, Index, Links"]
        DeviceList["DeviceList []*Device<br/>Ordered device collections"]
        DeviceSet["DeviceSet map[string]*Device<br/>Unique device sets"]
        NewDevices["NewDevices()<br/>Device discovery entry point"]
    end
    
    subgraph "Policy Layer" 
        Policy["Policy interface<br/>Allocate() method"]
        BestEffort["bestEffortPolicy<br/>Score-based optimization"]
        Simple["SimplePolicy<br/>Sequential allocation"]
        StaticDGX["StaticDGXPolicy<br/>Predefined patterns"]
    end
    
    subgraph "Allocator Engine"
        Allocator["Allocator struct<br/>GPUs, policy, remaining, allocated"]
        AllocateMethod["Allocate(num int)<br/>Main allocation method"]
        AllocateSpecific["AllocateSpecific(...*Device)<br/>Target specific GPUs"]
        Free["Free(...*Device)<br/>Return GPUs to pool"]
    end
    
    subgraph "P2P Discovery"
        P2PLink["P2PLink struct<br/>GPU, Type"]
        GetP2PLink["GetP2PLink()<br/>PCIe topology discovery"]
        GetNVLink["GetNVLink()<br/>NVLink enumeration"]
    end
    
    NewDevices --> Device
    Device --> DeviceList
    DeviceList --> DeviceSet
    Device --> P2PLink
    GetP2PLink --> P2PLink
    GetNVLink --> P2PLink
    
    Allocator --> Policy
    Policy --> BestEffort
    Policy --> Simple
    Policy --> StaticDGX
    
    AllocateMethod --> Policy
    Allocator --> DeviceSet
    AllocateSpecific --> DeviceSet
    Free --> DeviceSet
    
    BestEffort --> DeviceList
    Simple --> DeviceList
```

**Sources:** [gpuallocator/device.go:16-22](), [gpuallocator/device.go:69-73](), [gpuallocator/allocator.go:12-20](), [gpuallocator/allocator.go:22-32](), [gpuallocator/besteffort_policy.go:13-17](), [internal/links/device.go:64-67]()

## Core Components Overview

### Device Representation

The system uses a structured approach to represent GPU devices and their relationships:

| Component | Type | Purpose |
|-----------|------|---------|
| `Device` | `struct` | Individual GPU with P2P links and metadata |
| `DeviceList` | `[]*Device` | Ordered collections for iteration and filtering |
| `DeviceSet` | `map[string]*Device` | Set operations using UUID keys |
| `P2PLink` | `struct` | Point-to-point connectivity information |

The `Device` struct embeds an `nvlibDevice` which provides NVML integration while adding allocation-specific fields:

```mermaid
graph LR
    Device["Device struct"]
    nvlibDevice["nvlibDevice<br/>device.Device, UUID, PCI, CPUAffinity"]
    Index["Index int<br/>Device position"]
    Links["Links map[int][]P2PLink<br/>Connectivity map"]
    
    Device --> nvlibDevice
    Device --> Index  
    Device --> Links
    
    nvlibDevice --> NVML["device.Device<br/>NVML bindings"]
    nvlibDevice --> UUID["UUID string<br/>Unique identifier"]
    nvlibDevice --> PCI["PCI.BusID string<br/>Bus location"]
    nvlibDevice --> CPU["CPUAffinity *uint<br/>NUMA affinity"]
```

**Sources:** [gpuallocator/device.go:16-34](), [gpuallocator/device.go:64-67]()

### Policy System

The allocation system uses a pluggable policy architecture where different algorithms can be selected based on workload requirements:

| Policy | Implementation | Algorithm |
|--------|---------------|-----------|
| `Policy` | `interface` | Common allocation contract |
| `bestEffortPolicy` | Score-based | Optimizes total partition score |
| `SimplePolicy` | Sequential | First-available allocation |
| `StaticDGXPolicy` | Pattern-based | Predefined optimal configurations |

The `Policy` interface defines the allocation contract:
- `Allocate(available []*Device, required []*Device, size int) []*Device`

**Sources:** [gpuallocator/allocator.go:22-32](), [gpuallocator/besteffort_policy.go:13-17]()

### Allocator Engine

The `Allocator` struct maintains allocation state and coordinates between policies and device management:

```mermaid
graph TB
    Allocator["Allocator struct"]
    GPUs["GPUs []*Device<br/>All discovered devices"]
    policy["policy Policy<br/>Selected allocation algorithm"] 
    remaining["remaining DeviceSet<br/>Available for allocation"]
    allocated["allocated DeviceSet<br/>Currently allocated"]
    
    Methods["Core Methods"]
    NewAllocator["NewAllocator(Policy)<br/>Constructor with NVML init"]
    Allocate["Allocate(int)<br/>Request N GPUs"]
    AllocateSpecific["AllocateSpecific(...*Device)<br/>Target specific GPUs"]
    Free["Free(...*Device)<br/>Return to available pool"]
    
    Allocator --> GPUs
    Allocator --> policy
    Allocator --> remaining
    Allocator --> allocated
    
    Methods --> NewAllocator
    Methods --> Allocate
    Methods --> AllocateSpecific  
    Methods --> Free
    
    Allocate --> policy
    AllocateSpecific --> remaining
    AllocateSpecific --> allocated
    Free --> remaining
    Free --> allocated
```

**Sources:** [gpuallocator/allocator.go:12-20](), [gpuallocator/allocator.go:46-68](), [gpuallocator/allocator.go:83-122]()

## Allocation Data Flow

The following diagram shows how GPU allocation requests flow through the system components:

```mermaid
sequenceDiagram
    participant App as "Client Application"
    participant Alloc as "Allocator"
    participant Policy as "Policy Implementation"
    participant DevSet as "DeviceSet (remaining)"
    participant P2P as "P2P Link Discovery"
    
    Note over App,P2P: Initialization Phase
    App->>Alloc: NewAllocator(policy)
    Alloc->>P2P: NewDevices()
    P2P->>P2P: GetP2PLink(), GetNVLink()
    P2P-->>Alloc: DeviceList with topology
    Alloc->>DevSet: Insert(devices...)
    
    Note over App,P2P: Allocation Phase
    App->>Alloc: Allocate(num)
    Alloc->>DevSet: SortedSlice()
    DevSet-->>Alloc: []*Device (available)
    Alloc->>Policy: Allocate(available, nil, num)
    
    alt BestEffort Policy
        Policy->>Policy: iterateGPUPartitions()
        Policy->>Policy: calculateGPUPartitionScore()
        Policy->>Policy: calculateGPUPairScore()
    else Simple Policy
        Policy->>Policy: sequential selection
    end
    
    Policy-->>Alloc: []*Device (selected)
    Alloc->>Alloc: AllocateSpecific(selected...)
    Alloc->>DevSet: Delete(selected...)
    Alloc-->>App: []*Device (allocated)
    
    Note over App,P2P: Cleanup Phase
    App->>Alloc: Free(devices...)
    Alloc->>DevSet: Insert(devices...)
```

**Sources:** [gpuallocator/allocator.go:83-95](), [gpuallocator/allocator.go:97-116](), [gpuallocator/besteffort_policy.go:36-95](), [gpuallocator/device.go:75-136]()

## P2P Link Discovery System

The system discovers and categorizes GPU interconnectivity to enable topology-aware allocation:

```mermaid
graph TB
    subgraph "Link Types"
        P2PTypes["P2PLinkType enum"]
        CrossCPU["P2PLinkCrossCPU<br/>Score: 10"]
        SameCPU["P2PLinkSameCPU<br/>Score: 20"] 
        HostBridge["P2PLinkHostBridge<br/>Score: 30"]
        MultiSwitch["P2PLinkMultiSwitch<br/>Score: 40"]
        SingleSwitch["P2PLinkSingleSwitch<br/>Score: 50"]
        SameBoard["P2PLinkSameBoard<br/>Score: 60"]
    end
    
    subgraph "NVLink Types"
        NVLinkTypes["NVLink Link Counts"]
        Single["SingleNVLINKLink<br/>Score: 100"]
        Two["TwoNVLINKLinks<br/>Score: 200"]
        Multiple["...up to EighteenNVLINKLinks<br/>Score: 1800"]
    end
    
    subgraph "Discovery Functions"
        GetP2P["GetP2PLink(dev1, dev2)<br/>PCIe topology analysis"]
        GetNV["GetNVLink(dev1, dev2)<br/>NVLink enumeration"]
        CommonAncestor["GetTopologyCommonAncestor()<br/>NVML topology query"]
        NVLinkState["GetNvLinkState(linkId)<br/>Per-link status check"]
    end
    
    GetP2P --> CommonAncestor
    GetP2P --> CrossCPU
    GetP2P --> SameCPU
    GetP2P --> HostBridge
    GetNV --> NVLinkState
    GetNV --> Single
    GetNV --> Two
    GetNV --> Multiple
```

**Sources:** [internal/links/device.go:26-57](), [internal/links/device.go:115-139](), [internal/links/device.go:141-201](), [gpuallocator/besteffort_policy.go:298-374]()

## Integration Points

The Core GPU Allocation System integrates with several external components:

| Integration | Interface | Purpose |
|-------------|-----------|---------|
| NVML Library | `nvml.Interface` | Hardware device enumeration |
| go-nvlib | `device.Device` | High-level device operations |
| P2P Discovery | `links.GetP2PLink()` | Topology information |
| Testing Framework | Mock interfaces | Development and testing |

The system uses dependency injection through the `Option` pattern in `NewDevices()` to allow for flexible integration and testing scenarios.

**Sources:** [gpuallocator/device.go:75-89](), [gpuallocator/allocator.go:46-67](), [internal/links/device.go:115-139]()

---

