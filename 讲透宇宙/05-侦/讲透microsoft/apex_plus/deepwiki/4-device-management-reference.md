<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/apex_plus · page 4 Device Management Reference · fetched 2026-10-26 -->

# Device Management Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apex_plus/cluster/cluster.py](apex_plus/cluster/cluster.py)
- [apex_plus/cluster/device.py](apex_plus/cluster/device.py)
- [apex_plus/cluster/gpu.py](apex_plus/cluster/gpu.py)

</details>



## Purpose and Scope

This document provides a technical reference for APEX+'s device management system, which abstracts computational hardware and organizes it into hierarchical clusters with different topologies. The device management system serves as the foundation for execution planning by providing information about available compute resources, their capabilities, and interconnection topologies.

For detailed information about how device clusters are used in execution planning, see [Execution Planning](#3.3). For specific device abstraction details, see [Device Abstraction](#4.1). For GPU-specific implementations, see [GPU Devices](#4.2). For cluster topology management, see [Cluster Topology](#4.3).

## Device Management Architecture

The device management system in APEX+ consists of three main components that work together to represent and organize computational resources:

### Device Class Hierarchy

```mermaid
classDiagram
    class Device {
        <<abstract>>
        +int device_id
        +str device_type
        +__init__(device_id, device_type)
        +get_memory_capacity()* int
    }
    
    class GPU {
        +GPUType gpu_type
        +int total_memory
        +dict peak_flops
        +float peak_mem_bandwidth
        +__init__(device_id, device_type)
        +get_memory_capacity() int
        +get_topology(gpu)$ str
    }
    
    class GPUType {
        <<enumeration>>
        V100_PCIE_16GB
        H100_SXM_80GB
        H200_SXM_141GB
    }
    
    Device <|-- GPU
    GPU --> GPUType
```

Sources: [apex_plus/cluster/device.py:1-12](), [apex_plus/cluster/gpu.py:69-103](), [apex_plus/cluster/gpu.py:9-16]()

### Cluster Topology Structure

```mermaid
graph TB
    subgraph "Cluster Hierarchy"
        RootCluster["Cluster(level=2+)"]
        NodeCluster1["Cluster(level=1)"]
        NodeCluster2["Cluster(level=1)"]
        
        subgraph "GPU Devices"
            GPU1["GPU(device_id=0)"]
            GPU2["GPU(device_id=1)"]
            GPU3["GPU(device_id=2)"]
            GPU4["GPU(device_id=3)"]
        end
    end
    
    subgraph "Topology Types"
        FlatTopo["from_flat_topology()"]
        NVLinkTopo["from_nvlink_topology()"]
        PCIeTopo["from_pcie_topology()"]
    end
    
    RootCluster --> NodeCluster1
    RootCluster --> NodeCluster2
    NodeCluster1 --> GPU1
    NodeCluster1 --> GPU2
    NodeCluster2 --> GPU3
    NodeCluster2 --> GPU4
    
    FlatTopo --> RootCluster
    NVLinkTopo --> RootCluster
    PCIeTopo --> RootCluster
```

Sources: [apex_plus/cluster/cluster.py:7-35](), [apex_plus/cluster/cluster.py:127-246]()

## Device Abstraction

The `Device` class provides the base abstraction for all computational devices in APEX+. It defines a minimal interface that all device implementations must support, including device identification and memory capacity reporting.

| Method | Purpose | Implementation |
|--------|---------|----------------|
| `__init__(device_id, device_type)` | Initialize device with ID and type | Abstract - must be implemented by subclasses |
| `get_memory_capacity()` | Return device memory in bytes | Abstract - must be implemented by subclasses |

The abstract nature of the `Device` class allows APEX+ to support different types of computational resources through a uniform interface. For complete device abstraction details, see [Device Abstraction](#4.1).

Sources: [apex_plus/cluster/device.py:1-12]()

## GPU Device Support

The `GPU` class implements the `Device` interface for GPU hardware, providing detailed specifications for supported GPU types including memory capacity, peak FLOPS, and memory bandwidth.

### Supported GPU Types

| GPU Type | Memory | Peak FLOPS (FP16) | Memory Bandwidth | Topology |
|----------|--------|-------------------|------------------|----------|
| `V100_PCIE_16GB` | 16 GB | 14 TFLOPS | 900 GB/s | PCIe |
| `H100_SXM_80GB` | 80 GB | 1979 TFLOPS | 3.35 TB/s | NVLink |
| `H200_SXM_141GB` | 141 GB | 1979 TFLOPS | 4.8 TB/s | NVLink |

### GPU Registration System

```mermaid
graph LR
    subgraph "GPU Registry System"
        DeviceString["device_type: str"]
        Registry["_GPU_REGISTRY"]
        GPUTypeEnum["GPUType enum"]
        
        subgraph "Specification Lookups"
            MemoryLookup["_GPU_TYPE_TO_MEMORY_GB"]
            TopologyLookup["_GPU_TYPE_TO_TOPOLOGY"]
            FLOPSLookup["_GPU_PEAK_FLOPS"]
            BandwidthLookup["_GPU_PEAK_MEM_BANDWIDTH"]
        end
    end
    
    DeviceString --> Registry
    Registry --> GPUTypeEnum
    GPUTypeEnum --> MemoryLookup
    GPUTypeEnum --> TopologyLookup
    GPUTypeEnum --> FLOPSLookup
    GPUTypeEnum --> BandwidthLookup
```

For detailed GPU specifications and implementations, see [GPU Devices](#4.2).

Sources: [apex_plus/cluster/gpu.py:18-66](), [apex_plus/cluster/gpu.py:69-103]()

## Cluster Topology Management

The `Cluster` class implements hierarchical organization of devices with support for different interconnection topologies. Clusters can be partitioned for parallel execution and support three main topology types.

### Cluster Factory Methods

```mermaid
graph TD
    subgraph "Cluster Creation"
        FromGPU["from_gpu(gpu_type, num_nodes, num_devices_per_node)"]
        GetTopology["GPU.get_topology(gpu_type)"]
        
        subgraph "Topology-Specific Factories"
            FlatFactory["from_flat_topology(gpu_type, num_devices)"]
            NVLinkFactory["from_nvlink_topology(gpu_type, num_nodes, devices_per_node)"]
            PCIeFactory["from_pcie_topology(gpu_type, num_nodes, devices_per_node)"]
        end
        
        subgraph "Topology Types"
            Flat["flat: Single-node direct connections"]
            NVLink["nvlink: Full-mesh intra-node connections"]
            PCIe["pcie: Hierarchical PCIe lanes"]
        end
    end
    
    FromGPU --> GetTopology
    GetTopology --> FlatFactory
    GetTopology --> NVLinkFactory
    GetTopology --> PCIeFactory
    
    FlatFactory --> Flat
    NVLinkFactory --> NVLink
    PCIeFactory --> PCIe
```

### Cluster Partitioning

The `partition(n)` method enables splitting clusters into `n` sub-clusters for parallel execution planning:

| Partition Scenario | Behavior |
|-------------------|----------|
| `n == 1` | Returns the cluster unchanged |
| `n <= num_children` | Partitions by grouping child clusters |
| `n > num_children` | Recursively partitions child clusters |
| Leaf cluster | Partitions devices directly |

For complete cluster topology details, see [Cluster Topology](#4.3).

Sources: [apex_plus/cluster/cluster.py:55-125](), [apex_plus/cluster/cluster.py:217-246]()

## Integration with Execution Planning

The device management system integrates with APEX+'s execution planning through the cluster abstraction, enabling the plan generator to understand available computational resources and their capabilities.

### Device Management in Execution Flow

```mermaid
graph LR
    subgraph "Device Management"
        ClusterSpec["Cluster Configuration"]
        DeviceSpecs["Device Specifications"]
        TopologyInfo["Topology Information"]
    end
    
    subgraph "Execution Planning"
        PlanGenerator["Plan Generator"]
        StageMapping["Stage → Cluster Mapping"]
        CellMapping["Cell Replicas → Cluster Mapping"]
    end
    
    subgraph "Performance Simulation"
        Simulator["Dynamism-Aware Simulator"]
        ProfilingData["Op-level Profiling Data"]
    end
    
    ClusterSpec --> PlanGenerator
    DeviceSpecs --> PlanGenerator
    TopologyInfo --> PlanGenerator
    
    PlanGenerator --> StageMapping
    PlanGenerator --> CellMapping
    
    StageMapping --> Simulator
    CellMapping --> Simulator
    DeviceSpecs --> ProfilingData
    ProfilingData --> Simulator
```

The cluster's `get_device()`, `get_device_memory_capacity()`, and `get_num_devices()` methods provide essential information for execution plan generation, while the `partition()` method enables cluster subdivision for different parallelization strategies.

Sources: [apex_plus/cluster/cluster.py:40-54](), [apex_plus/cluster/cluster.py:55-125]()

---

