<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/go-nvml · page 4 GPU Features · fetched 2026-10-26 -->

# GPU Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [pkg/nvml/device.go](pkg/nvml/device.go)
- [pkg/nvml/gpm.go](pkg/nvml/gpm.go)
- [pkg/nvml/nvml.go](pkg/nvml/nvml.go)
- [pkg/nvml/system.go](pkg/nvml/system.go)

</details>



This page provides an overview of the specialized GPU features accessible through the go-nvml bindings. It covers the broad categories of functionality that allow Go applications to monitor, manage, and interact with NVIDIA GPUs. For details about the core API structure, see [Core API](#3).

## Feature Overview

The go-nvml bindings provide access to various GPU features that can be broadly categorized into the following areas:

```mermaid
flowchart TD
    subgraph "GPU Features"
        PM["Performance Metrics"] --> |"includes"| Util["Utilization Rates"]
        PM --> |"includes"| Mem["Memory Statistics"]
        PM --> |"includes"| Clock["Clock Information"]
        PM --> |"includes"| Temp["Temperature Monitoring"]
        PM --> |"includes"| Power["Power Management"]
        PM --> |"includes"| GPM["GPU Performance Monitoring"]
        
        PART["GPU Partitioning"] --> |"includes"| MIG["Multi-Instance GPU (MIG)"]
        PART --> |"includes"| VGPU["Virtual GPU (vGPU)"]
        
        EVENT["Event Handling"] --> |"monitors"| XID["Xid Error Events"]
        EVENT --> |"monitors"| CONF["Config Change Events"]
        
        TOPO["GPU Topology"] --> |"includes"| P2P["Peer-to-Peer Capabilities"]
        TOPO --> |"includes"| NVL["NVLink Information"]
        
        PROC["Process Monitoring"] --> |"tracks"| CompProc["Compute Processes"]
        PROC --> |"tracks"| GraphProc["Graphics Processes"]
        PROC --> |"tracks"| Acct["Process Accounting"]
    end
```

Sources: [pkg/nvml/device.go:1-1407](), [pkg/nvml/gpm.go:1-171]()

## Performance Metrics

The Go bindings provide extensive capabilities for monitoring GPU performance metrics, which are essential for understanding GPU utilization and optimizing applications.

```mermaid
classDiagram
    class Device {
        GetUtilizationRates()
        GetMemoryInfo()
        GetMemoryInfo_v2()
        GetClockInfo()
        GetMaxClockInfo()
        GetTemperature()
        GetPowerUsage()
        GetTotalEnergyConsumption()
        GetFanSpeed()
        GetPerformanceState()
        GetCurrentClocksThrottleReasons()
    }
    
    class Utilization {
        gpu uint32
        memory uint32
    }
    
    class Memory {
        total uint64
        free uint64
        used uint64
    }
    
    class Memory_v2 {
        version uint32
        total uint64
        reserved uint64
        free uint64
        used uint64
    }
    
    Device -- Utilization : returns
    Device -- Memory : returns
    Device -- Memory_v2 : returns
```

Key performance metrics functions include:

- **Utilization Metrics**: Monitor GPU and memory utilization percentages using `Device.GetUtilizationRates()`
- **Memory Statistics**: Get detailed memory allocation information with `Device.GetMemoryInfo()` and the more detailed `Device.GetMemoryInfo_v2()`
- **Clock Information**: Retrieve clock speeds for various GPU components with `Device.GetClockInfo()` and `Device.GetMaxClockInfo()`
- **Temperature Monitoring**: Monitor GPU temperature with `Device.GetTemperature()`
- **Power Consumption**: Track power usage with `Device.GetPowerUsage()` and `Device.GetTotalEnergyConsumption()`

For more detailed information about performance metrics, see [Performance Metrics](#4.1).

Sources: [pkg/nvml/device.go:788-808]()(Memory info), [pkg/nvml/device.go:897-907]()(Utilization rates), [pkg/nvml/device.go:464-483]()(Clock info), [pkg/nvml/device.go:622-631]()(Temperature), [pkg/nvml/device.go:743-763]()(Power usage)

## GPU Performance Monitoring (GPM)

NVML provides a more advanced GPU Performance Monitoring system that allows for detailed metric collection and analysis:

```mermaid
flowchart LR
    App["Go Application"] --> |"calls"| GPMA["GpmSampleAlloc()"]
    GPMA --> |"returns"| Sample["GpmSample"]
    App --> |"passes to"| GPMS["GpmSampleGet(device, sample)"]
    GPMS --> |"populates"| Sample
    App --> |"passes to"| GPMM["GpmMetricsGet(metricsGet)"]
    Sample --> |"analyzed by"| GPMM
    GPMM --> |"returns"| Metrics["GpmMetric[]"]
    App --> |"when done calls"| GPMF["GpmSampleFree(sample)"]
```

The GPM functions allow for:
- Creating a sample container with `GpmSampleAlloc()`
- Collecting metric samples from a device with `GpmSampleGet()`
- Analyzing samples to extract metrics with `GpmMetricsGet()`
- Proper cleanup with `GpmSampleFree()`

This system provides a more comprehensive set of metrics than the basic utilization functions.

Sources: [pkg/nvml/gpm.go:79-106]()

## GPU Partitioning and Virtualization

NVML supports technologies for partitioning and virtualizing GPUs to enable multi-tenant workloads.

```mermaid
flowchart TD
    subgraph "GPU Partitioning"
        Device["Device"] --> |"can be split into"| GI["GPU Instances"]
        GI --> |"can contain"| CI["Compute Instances"]
        
        Device --> |"can support"| VGPU["vGPU Instances"]
    end
    
    subgraph "MIG Functions"
        GetMigMode["Device.GetMigMode()"]
        SetMigMode["Device.SetMigMode()"]
        CreateGI["Device.CreateGpuInstance()"]
        GetGIs["Device.GetGpuInstances()"]
        CreateCI["GpuInstance.CreateComputeInstance()"]
        GetCIs["GpuInstance.GetComputeInstances()"]
    end
    
    subgraph "vGPU Functions"
        GetVgpuCount["Device.GetVgpuInstanceCount()"]
        GetVgpus["Device.GetVgpuInstances()"]
        GetVgpuMetadata["Device.GetVgpuMetadata()"]
    end
    
    Device --- GetMigMode
    Device --- SetMigMode
    Device --- CreateGI
    Device --- GetGIs
    GI --- CreateCI
    GI --- GetCIs
    
    Device --- GetVgpuCount
    Device --- GetVgpus
    Device --- GetVgpuMetadata
```

### Multi-Instance GPU (MIG)

MIG allows you to partition a single physical GPU into multiple isolated GPU instances, each with its own memory, compute resources, and bandwidth. The API provides functions to:

- Get and set MIG mode on a device
- Create and manage GPU instances
- Create and manage compute instances within GPU instances
- Monitor MIG configurations and resources

For more detailed information, see [Multi-Instance GPU (MIG)](#4.2).

### Virtual GPU (vGPU)

Virtual GPU technology enables sharing a physical GPU across multiple virtual machines or containers. The API provides functions to:

- Get the count and list of vGPU instances on a device
- Retrieve metadata about vGPU instances
- Monitor vGPU resource usage and configurations

For more detailed information, see [Virtual GPU (vGPU)](#4.3).

Sources: [pkg/nvml/device.go:60-99]()(GpuInstance and ComputeInstance types)

## Event Handling

NVML supports monitoring various GPU-related events, allowing applications to react to changes in GPU state or configuration.

```mermaid
flowchart TD
    subgraph "Event System"
        ES["EventSet"] --> |"registers"| Events["Events"]
        ES --> |"waits for"| Occur["Event Occurrence"]
        Occur --> |"triggers"| Handler["Event Handler"]
        ES --> |"eventually calls"| Free["EventSet.Free()"]
    end
    
    subgraph "Event Types"
        XidError["Xid Errors"]
        ConfigChange["Configuration Changes"]
        EccError["ECC Errors"]
        PowerChange["Power State Changes"]
        ThermalAlert["Thermal Alerts"]
    end
    
    Events --- XidError
    Events --- ConfigChange
    Events --- EccError
    Events --- PowerChange
    Events --- ThermalAlert
```

The event handling system allows applications to:
- Register for specific types of events
- Wait for events to occur with configurable timeouts
- React to events with appropriate handling logic
- Properly clean up event resources

For more detailed information about event handling, see [Event Handling](#4.4).

Sources: [pkg/nvml/device.go:1196-1197]()(References to EventSet in the class diagram)

## GPU Topology and Multi-GPU Management

For systems with multiple GPUs, NVML provides functions to understand and optimize the topology and connectivity between GPUs.

```mermaid
flowchart TD
    subgraph "GPU Topology"
        GPU1["GPU 1"] <--> |"P2P Communication"| GPU2["GPU 2"]
        GPU1 <--> |"P2P Communication"| GPU3["GPU 3"]
        GPU2 <--> |"P2P Communication"| GPU3
        
        GPU1 <--> |"via"| NVL1["NVLink"]
        GPU2 <--> |"via"| NVL1
        GPU2 <--> |"via"| NVL2["NVLink"]
        GPU3 <--> |"via"| NVL2
    end
    
    subgraph "Topology Functions"
        GetTopologyCommonAncestor["Device.GetTopologyCommonAncestor()"]
        GetTopologyNearestGpus["Device.GetTopologyNearestGpus()"]
        GetP2PStatus["Device.GetP2PStatus()"]
        OnSameBoard["Device.OnSameBoard()"]
        SystemTopology["SystemGetTopologyGpuSet()"]
    end
```

Key topology features include:
- Discovering GPUs near a specific CPU with `SystemGetTopologyGpuSet()`
- Finding GPUs near another GPU with `Device.GetTopologyNearestGpus()`
- Checking peer-to-peer compatibility with `Device.GetP2PStatus()`
- Determining if GPUs share a common ancestor with `Device.GetTopologyCommonAncestor()`
- Checking if GPUs are on the same board with `Device.OnSameBoard()`

Understanding the topology helps optimize multi-GPU workloads by minimizing data transfer costs between GPUs.

Sources: [pkg/nvml/device.go:234-265]()(Topology functions), [pkg/nvml/system.go:67-81]()(System topology functions)

## Process Monitoring

NVML provides capabilities to monitor processes using the GPU, useful for diagnostics and resource management.

```mermaid
classDiagram
    class Device {
        GetComputeRunningProcesses()
        GetGraphicsRunningProcesses()
        GetMPSComputeRunningProcesses()
        GetAccountingMode()
        GetAccountingStats()
        GetAccountingPids()
    }
    
    class ProcessInfo {
        pid uint32
        usedGpuMemory uint64
        gpuInstanceId uint32
        computeInstanceId uint32
    }
    
    class AccountingStats {
        gpuUtilization uint32
        memoryUtilization uint32
        maxMemoryUsage uint64
        time uint64
        startTime uint64
        isRunning uint32
    }
    
    Device -- ProcessInfo : returns
    Device -- AccountingStats : returns
```

Process monitoring functions allow you to:
- Get information about compute processes with `Device.GetComputeRunningProcesses()`
- Get information about graphics processes with `Device.GetGraphicsRunningProcesses()`
- Get information about MPS compute processes with `Device.GetMPSComputeRunningProcesses()`
- Enable and use the accounting system with various accounting functions to track resource usage over time

These functions help identify which processes are consuming GPU resources and how much they're using.

Sources: [pkg/nvml/device.go:1035-1197]()(Process monitoring functions), [pkg/nvml/device.go:1330-1380]()(Accounting functions)

## Integration with Go Applications

To utilize the GPU features provided by go-nvml, applications follow a common pattern:

```mermaid
sequenceDiagram
    participant App as "Go Application"
    participant NVML as "NVML Interface"
    participant Device as "Device"
    participant Features as "Feature Functions"
    
    App->>NVML: nvml.Init()
    activate NVML
    
    App->>NVML: nvml.DeviceGetCount()
    NVML-->>App: deviceCount
    
    loop For each device
        App->>NVML: nvml.DeviceGetHandleByIndex(index)
        NVML-->>App: device
        
        App->>Device: device.GetName()
        Device-->>App: name
        
        App->>Features: device.GetUtilizationRates()
        Features-->>App: utilization
        
        App->>Features: device.GetMemoryInfo()
        Features-->>App: memoryInfo
        
        App->>Features: device.GetTemperature()
        Features-->>App: temperature
        
        Note over App,Features: Process metrics as needed
    end
    
    App->>NVML: nvml.Shutdown()
    deactivate NVML
```

This sequence demonstrates the typical flow of interacting with GPU features:
1. Initialize the NVML library
2. Get the count of available devices
3. Get handles to each device
4. Query device features as needed
5. Process the obtained metrics
6. Shutdown the NVML library when finished

Sources: [pkg/nvml/nvml.go:15-51]()(Init and Shutdown functions), [pkg/nvml/device.go:100-133]()(Device enumeration functions)

## Summary

The go-nvml bindings provide a rich set of features for interacting with NVIDIA GPUs, ranging from basic monitoring to advanced management capabilities. This page has provided an overview of the main feature categories, which are explored in more detail in the following pages:

- [Performance Metrics](#4.1) - Details about monitoring GPU performance
- [Multi-Instance GPU (MIG)](#4.2) - Information about GPU partitioning capabilities
- [Virtual GPU (vGPU)](#4.3) - Details about GPU virtualization features
- [Event Handling](#4.4) - Information about monitoring GPU events

These GPU features enable Go applications to effectively monitor, manage, and optimize GPU usage for various workloads and scenarios.

Sources: [pkg/nvml/device.go:1-1407](), [pkg/nvml/gpm.go:1-171](), [pkg/nvml/nvml.go:1-1030](), [pkg/nvml/system.go:1-141]()

---

