<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/kubevirt-gpu-device-plugin · page 3 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [manifests/nvidia-kubevirt-gpu-device-plugin.yaml](manifests/nvidia-kubevirt-gpu-device-plugin.yaml)
- [pkg/device_plugin/device_plugin.go](pkg/device_plugin/device_plugin.go)
- [pkg/device_plugin/device_plugin_test.go](pkg/device_plugin/device_plugin_test.go)
- [pkg/device_plugin/generic_device_plugin.go](pkg/device_plugin/generic_device_plugin.go)
- [pkg/device_plugin/generic_vgpu_device_plugin.go](pkg/device_plugin/generic_vgpu_device_plugin.go)

</details>



## Purpose and Scope

This document provides a comprehensive technical overview of the NVIDIA KubeVirt GPU Device Plugin's internal architecture and design. It covers the core components, their interactions, and the technical implementation that enables GPU passthrough and vGPU support for KubeVirt virtual machines within Kubernetes clusters.

For installation and deployment procedures, see [Getting Started](#2). For detailed subsystem documentation, see the following child pages:
- System architecture overview: [System Architecture Overview](#3.1)
- Device discovery mechanisms: [Device Discovery and Mapping](#3.2)
- Physical GPU management: [Physical GPU Device Plugin](#3.3)
- Virtual GPU management: [Virtual GPU Device Plugin](#3.4)
- Kubernetes API integration: [Kubernetes Integration](#3.5)
- Observability infrastructure: [Logging and Observability](#3.6)

---

## Architectural Overview

The device plugin operates as a Kubernetes DaemonSet pod on GPU-enabled nodes, implementing the Kubernetes Device Plugin API v1beta1 to advertise GPU resources and handle allocation requests. The system supports both physical GPU passthrough via VFIO-PCI and virtual GPU (vGPU) allocation via Linux mdev subsystem.

### Core Components

```mermaid
graph TB
    subgraph "Entry Point"
        MAIN["InitiateDevicePlugin()<br/>(device_plugin.go:89)"]
    end
    
    subgraph "Discovery Layer"
        CREATE_IOMMU["createIommuDeviceMap()<br/>(device_plugin.go:187)"]
        CREATE_VGPU["createVgpuIDMap()<br/>(device_plugin.go:255)"]
        
        IOMMU_MAP["iommuMap<br/>map[string][]NvidiaGpuDevice"]
        DEVICE_MAP["deviceMap<br/>map[string][]NvidiaGpuDevice"]
        VGPU_MAP["vGpuMap<br/>map[string][]NvidiaGpuDevice"]
        BDF_MAP["bdfToIommuMap<br/>map[string]string"]
        GPU_VGPU_MAP["gpuVgpuMap<br/>map[string][]string"]
    end
    
    subgraph "Device Plugin Layer"
        CREATE_DP["createDevicePlugins()<br/>(device_plugin.go:99)"]
        GDP["GenericDevicePlugin<br/>(generic_device_plugin.go:63)"]
        GVDP["GenericVGpuDevicePlugin<br/>(generic_vgpu_device_plugin.go:55)"]
    end
    
    subgraph "Kubernetes Interface"
        GRPC_SERVER["grpc.Server<br/>Device Plugin gRPC"]
        KUBELET["pluginapi.KubeletSocket<br/>/var/lib/kubelet/device-plugins/kubelet.sock"]
    end
    
    subgraph "Hardware Interface"
        SYSFS["/sys/bus/pci/devices/<br/>/sys/bus/mdev/devices"]
        VFIO["/dev/vfio/*"]
    end
    
    MAIN --> CREATE_IOMMU
    MAIN --> CREATE_VGPU
    MAIN --> CREATE_DP
    
    CREATE_IOMMU --> SYSFS
    CREATE_VGPU --> SYSFS
    
    CREATE_IOMMU --> IOMMU_MAP
    CREATE_IOMMU --> DEVICE_MAP
    CREATE_IOMMU --> BDF_MAP
    CREATE_VGPU --> VGPU_MAP
    CREATE_VGPU --> GPU_VGPU_MAP
    
    CREATE_DP --> GDP
    CREATE_DP --> GVDP
    
    GDP --> GRPC_SERVER
    GVDP --> GRPC_SERVER
    
    GRPC_SERVER --> KUBELET
    
    GDP --> VFIO
    GVDP --> VFIO
```

**Sources:** [pkg/device_plugin/device_plugin.go:89-176](), [pkg/device_plugin/generic_device_plugin.go:63-90](), [pkg/device_plugin/generic_vgpu_device_plugin.go:55-81]()

---

## Data Structures and Mapping

The system maintains several critical maps to track GPU devices, their IOMMU groups, and relationships between physical and virtual GPUs:

| Map Variable | Type | Purpose | Source |
|--------------|------|---------|--------|
| `iommuMap` | `map[string][]NvidiaGpuDevice` | IOMMU group ID → GPU devices in that group | [device_plugin.go:56]() |
| `deviceMap` | `map[string][]NvidiaGpuDevice` | GPU device ID → all GPUs of that type | [device_plugin.go:59]() |
| `bdfToIommuMap` | `map[string]string` | PCI BDF address → IOMMU group ID | [device_plugin.go:62]() |
| `vGpuMap` | `map[string][]NvidiaGpuDevice` | vGPU type → vGPU devices of that type | [device_plugin.go:65]() |
| `gpuVgpuMap` | `map[string][]string` | GPU device ID → associated vGPU IDs | [device_plugin.go:68]() |

### NvidiaGpuDevice Structure

```go
type NvidiaGpuDevice struct {
    addr     string // PCI address (e.g., "0000:03:00.0")
    numaNode int64  // NUMA node ID for topology-aware scheduling
}
```

**Sources:** [pkg/device_plugin/device_plugin.go:49-68]()

---

## Device Discovery Process

Device discovery occurs at startup through two parallel scanning operations:

```mermaid
sequenceDiagram
    participant Main as "InitiateDevicePlugin()"
    participant CreateIOMMU as "createIommuDeviceMap()"
    participant CreateVGPU as "createVgpuIDMap()"
    participant FS as "Filesystem<br/>(sysfs)"
    participant PCI as "PCI Database<br/>(pci.ids)"
    
    Main->>CreateIOMMU: Scan physical GPUs
    CreateIOMMU->>FS: filepath.Walk(/sys/bus/pci/devices)
    loop For each device
        CreateIOMMU->>FS: readIDFromFile(vendor)
        FS-->>CreateIOMMU: "10de" (NVIDIA vendor ID)
        CreateIOMMU->>FS: readLink(driver)
        FS-->>CreateIOMMU: "vfio-pci" or "nvgrace_gpu_vfio_pci"
        CreateIOMMU->>FS: readLink(iommu_group)
        FS-->>CreateIOMMU: IOMMU group ID
        CreateIOMMU->>FS: readNUMANode()
        FS-->>CreateIOMMU: NUMA node ID
        CreateIOMMU->>FS: readIDFromFile(device)
        FS-->>CreateIOMMU: Device ID (e.g., "1b38")
        CreateIOMMU->>CreateIOMMU: Populate iommuMap, deviceMap, bdfToIommuMap
    end
    
    Main->>CreateVGPU: Scan vGPUs
    CreateVGPU->>FS: filepath.Walk(/sys/bus/mdev/devices)
    loop For each vGPU
        CreateVGPU->>FS: readVgpuIDFromFile(mdev_type/name)
        FS-->>CreateVGPU: vGPU type name
        CreateVGPU->>FS: readGpuIDForVgpu()
        FS-->>CreateVGPU: Parent GPU ID
        CreateVGPU->>CreateVGPU: Populate vGpuMap, gpuVgpuMap
    end
    
    Main->>PCI: getDeviceName(deviceID)
    PCI-->>Main: Human-readable device name
    Main->>Main: createDevicePlugins()
```

**Sources:** [pkg/device_plugin/device_plugin.go:89-96](), [pkg/device_plugin/device_plugin.go:187-247](), [pkg/device_plugin/device_plugin.go:255-291](), [pkg/device_plugin/device_plugin.go:371-438]()

### Discovery Functions

| Function | Path | Purpose |
|----------|------|---------|
| `createIommuDeviceMap()` | [device_plugin.go:187-247]() | Scans `/sys/bus/pci/devices`, identifies NVIDIA GPUs with VFIO drivers, maps to IOMMU groups |
| `createVgpuIDMap()` | [device_plugin.go:255-291]() | Scans `/sys/bus/mdev/devices`, identifies vGPU instances, links to parent GPUs |
| `readIDFromFileFunc()` | [device_plugin.go:294-302]() | Reads vendor/device IDs from sysfs |
| `readLinkFunc()` | [device_plugin.go:323-331]() | Resolves symlinks for driver and IOMMU group |
| `readNUMANodeFunc()` | [device_plugin.go:304-320]() | Reads NUMA topology information |
| `readVgpuIDFromFileFunc()` | [device_plugin.go:334-344]() | Extracts vGPU type name |
| `getDeviceName()` | [device_plugin.go:371-422]() | Resolves device ID to human-readable name from pci.ids database |

**Sources:** [pkg/device_plugin/device_plugin.go:187-438]()

---

## Dual Device Plugin Architecture

The system instantiates separate device plugin instances for each discovered GPU type and vGPU type. Each plugin operates independently with its own gRPC server and socket.

```mermaid
graph LR
    subgraph "Physical GPU Plugins"
        GDP1["GenericDevicePlugin<br/>nvidia.com/TESLA_V100_PCIE_32GB"]
        GDP2["GenericDevicePlugin<br/>nvidia.com/A100_PCIE_40GB"]
    end
    
    subgraph "vGPU Plugins"
        GVDP1["GenericVGpuDevicePlugin<br/>nvidia.com/GRID_V100D_8Q"]
        GVDP2["GenericVGpuDevicePlugin<br/>nvidia.com/GRID_A100D_10Q"]
    end
    
    subgraph "Kubelet Sockets"
        SOCK1["/var/lib/kubelet/device-plugins/<br/>kubevirt-TESLA_V100_PCIE_32GB.sock"]
        SOCK2["/var/lib/kubelet/device-plugins/<br/>kubevirt-A100_PCIE_40GB.sock"]
        SOCK3["/var/lib/kubelet/device-plugins/<br/>kubevirt-GRID_V100D_8Q.sock"]
        SOCK4["/var/lib/kubelet/device-plugins/<br/>kubevirt-GRID_A100D_10Q.sock"]
    end
    
    GDP1 -.->|gRPC| SOCK1
    GDP2 -.->|gRPC| SOCK2
    GVDP1 -.->|gRPC| SOCK3
    GVDP2 -.->|gRPC| SOCK4
```

### Plugin Instantiation Flow

```mermaid
sequenceDiagram
    participant CDP as "createDevicePlugins()"
    participant DM as "deviceMap/vGpuMap"
    participant GDP as "GenericDevicePlugin"
    participant GVDP as "GenericVGpuDevicePlugin"
    participant Start as "Start()"
    
    CDP->>DM: Iterate over deviceMap
    loop For each GPU type
        CDP->>CDP: Build pluginapi.Device list with NUMA topology
        CDP->>GDP: NewGenericDevicePlugin(deviceName, /dev/vfio/, devs)
        GDP-->>CDP: device plugin instance
        CDP->>Start: startDevicePlugin(dp)
        Start->>Start: Start gRPC server, register with kubelet
    end
    
    CDP->>DM: Iterate over vGpuMap
    loop For each vGPU type
        CDP->>CDP: Build pluginapi.Device list with NUMA topology
        CDP->>GVDP: NewGenericVGpuDevicePlugin(deviceName, basePath, devs)
        GVDP-->>CDP: vGPU device plugin instance
        CDP->>Start: startVgpuDevicePlugin(dp)
        Start->>Start: Start gRPC server, register with kubelet
    end
    
    CDP->>CDP: Block on stop channel
```

**Sources:** [pkg/device_plugin/device_plugin.go:99-176](), [pkg/device_plugin/generic_device_plugin.go:77-90](), [pkg/device_plugin/generic_vgpu_device_plugin.go:68-81]()

---

## Kubernetes Device Plugin API Implementation

Both `GenericDevicePlugin` and `GenericVGpuDevicePlugin` implement the `pluginapi.DevicePluginServer` interface, providing the following methods:

### Device Plugin Methods

| Method | GenericDevicePlugin | GenericVGpuDevicePlugin | Purpose |
|--------|---------------------|-------------------------|---------|
| `Register()` | [generic_device_plugin.go:202-223]() | [generic_vgpu_device_plugin.go:156-175]() | Registers with kubelet via gRPC |
| `ListAndWatch()` | [generic_device_plugin.go:226-263]() | [generic_vgpu_device_plugin.go:178-206]() | Streams device list and health updates |
| `Allocate()` | [generic_device_plugin.go:266-361]() | [generic_vgpu_device_plugin.go:209-247]() | Handles device allocation requests |
| `GetDevicePluginOptions()` | [generic_device_plugin.go:371-377]() | [generic_vgpu_device_plugin.go:257-262]() | Returns plugin capabilities |
| `GetPreferredAllocation()` | [generic_device_plugin.go:387-525]() | [generic_vgpu_device_plugin.go:270-278]() | Provides NUMA-aware allocation hints |
| `PreStartContainer()` | [generic_device_plugin.go:379-382]() | [generic_vgpu_device_plugin.go:264-267]() | Pre-start hook (no-op) |

**Sources:** [pkg/device_plugin/generic_device_plugin.go:63-634](), [pkg/device_plugin/generic_vgpu_device_plugin.go:55-438]()

---

## Physical GPU Allocation Flow

The `GenericDevicePlugin.Allocate()` method performs validation and constructs device specifications for physical GPU allocation:

```mermaid
sequenceDiagram
    participant Kubelet as "Kubelet"
    participant GDP as "GenericDevicePlugin.Allocate()"
    participant Maps as "iommuMap, bdfToIommuMap"
    participant FS as "Filesystem"
    
    Kubelet->>GDP: AllocateRequest(DeviceIDs=[BDF1, BDF2])
    
    GDP->>GDP: supportsIOMMUFD()
    GDP->>FS: Check /dev/iommu existence
    FS-->>GDP: iommufdSupported bool
    
    loop For each requested BDF
        GDP->>Maps: bdfToIommuMap[bdf]
        Maps-->>GDP: IOMMU group ID
        
        GDP->>Maps: iommuMap[iommuGroupID]
        Maps-->>GDP: []NvidiaGpuDevice
        
        loop For each device in IOMMU group
            GDP->>FS: readLink(basePath, dev.addr, "iommu_group")
            FS-->>GDP: Verify IOMMU group unchanged
            
            GDP->>FS: readIDFromFile(basePath, dev.addr, "vendor")
            FS-->>GDP: Verify vendor is "10de"
            
            alt iommufdSupported
                GDP->>FS: readVFIODev(basePath, dev.addr)
                FS-->>GDP: vfio device name
                GDP->>GDP: Add /dev/vfio/devices/vfioX to DeviceSpec
            end
        end
        
        GDP->>GDP: Add /dev/vfio/vfio to DeviceSpec
        GDP->>GDP: Add /dev/vfio/{iommuGroupID} to DeviceSpec
        
        alt iommufdSupported
            GDP->>GDP: Add /dev/iommu to DeviceSpec
        end
        
        GDP->>GDP: Build environment variable:<br/>PCI_RESOURCE_NVIDIA_COM_{DEVICE_NAME}
    end
    
    GDP-->>Kubelet: AllocateResponse(Devices, Envs)
```

### Allocation Output

For a physical GPU allocation, the response includes:

**Device Specifications:**
- `/dev/vfio/vfio` - VFIO container device
- `/dev/vfio/{iommuGroupID}` - IOMMU group device (e.g., `/dev/vfio/26`)
- `/dev/vfio/devices/vfioX` - Per-device IOMMUFD device (if supported)
- `/dev/iommu` - IOMMUFD device (if supported)

**Environment Variables:**
- `PCI_RESOURCE_NVIDIA_COM_{DEVICE_NAME}` - Comma-separated list of BDF addresses

**Sources:** [pkg/device_plugin/generic_device_plugin.go:266-361](), [pkg/device_plugin/generic_device_plugin.go:609-633]()

---

## Virtual GPU Allocation Flow

The `GenericVGpuDevicePlugin.Allocate()` method handles vGPU allocation:

```mermaid
sequenceDiagram
    participant Kubelet as "Kubelet"
    participant GVDP as "GenericVGpuDevicePlugin.Allocate()"
    participant FS as "Filesystem"
    
    Kubelet->>GVDP: AllocateRequest(DeviceIDs=[mdev_uuid1, mdev_uuid2])
    
    loop For each mdev UUID
        GVDP->>FS: readVgpuIDFromFile(vGpuBasePath, uuid, "mdev_type/name")
        FS-->>GVDP: vGPU type name
        
        GVDP->>GVDP: Verify vGPU type matches deviceName
        
        GVDP->>GVDP: Add to environment variable:<br/>MDEV_PCI_RESOURCE_NVIDIA_COM_{VGPU_TYPE}
    end
    
    GVDP->>GVDP: Add /dev/vfio to DeviceSpec (entire directory)
    
    GVDP-->>Kubelet: AllocateResponse(Devices, Envs)
```

### Allocation Output

For a vGPU allocation, the response includes:

**Device Specifications:**
- `/dev/vfio` - Entire VFIO directory (mdev devices appear here)

**Environment Variables:**
- `MDEV_PCI_RESOURCE_NVIDIA_COM_{VGPU_TYPE}` - Comma-separated list of mdev UUIDs

**Sources:** [pkg/device_plugin/generic_vgpu_device_plugin.go:209-247]()

---

## NUMA-Aware Allocation

The `GetPreferredAllocation()` method in `GenericDevicePlugin` implements topology-aware device selection to optimize NUMA affinity:

```mermaid
graph TB
    GPA["GetPreferredAllocation()"]
    
    MUST["Process MustIncludeDeviceIDs<br/>(required devices)"]
    TOPO["Build device to NUMA map"]
    GROUP["Group available devices by NUMA node"]
    
    SINGLE{"Can satisfy from<br/>single NUMA node?"}
    
    SELECT_NODE["Select NUMA node with<br/>enough available + selected devices"]
    FILL_NODE["Fill remaining slots<br/>from selected node"]
    
    FALLBACK["Fallback to kubelet-provided<br/>device order"]
    
    RESPONSE["Return preferred device list"]
    
    GPA --> TOPO
    GPA --> MUST
    TOPO --> GROUP
    MUST --> SINGLE
    GROUP --> SINGLE
    
    SINGLE -->|Yes| SELECT_NODE
    SELECT_NODE --> FILL_NODE
    FILL_NODE --> RESPONSE
    
    SINGLE -->|No| FALLBACK
    FALLBACK --> RESPONSE
```

### Algorithm Details

1. **Build NUMA topology map**: Extract NUMA node ID from each device's `Topology.Nodes[0].ID`
2. **Process must-include devices**: Add all required devices first, preserving order
3. **Attempt single-node allocation**: Try to find a NUMA node with sufficient devices (including already selected)
4. **Fill from selected node**: If a suitable node found, add remaining devices from that node
5. **Fallback**: If no single node can satisfy, use kubelet's original device order

**Sources:** [pkg/device_plugin/generic_device_plugin.go:387-525]()

---

## Health Monitoring

Both device plugin types implement continuous health monitoring through goroutines started in `Start()`:

### Physical GPU Health Check

```mermaid
graph TB
    HC["healthCheck() goroutine"]
    
    WATCHER["fsnotify.Watcher"]
    WATCH_SOCK["Watch device plugin socket"]
    WATCH_DEV["Watch /dev/vfio/{iommuGroupID}<br/>for each device"]
    
    SELECT["select on channels"]
    
    EVENT_CREATE["fsnotify.Create"]
    EVENT_REMOVE["fsnotify.Remove/Rename"]
    EVENT_SOCK["Socket removed"]
    
    HEALTHY["Send to healthy channel"]
    UNHEALTHY["Send to unhealthy channel"]
    RESTART["Restart device plugin"]
    
    HC --> WATCHER
    WATCHER --> WATCH_SOCK
    WATCHER --> WATCH_DEV
    WATCH_DEV --> SELECT
    WATCH_SOCK --> SELECT
    
    SELECT --> EVENT_CREATE
    SELECT --> EVENT_REMOVE
    SELECT --> EVENT_SOCK
    
    EVENT_CREATE --> HEALTHY
    EVENT_REMOVE --> UNHEALTHY
    EVENT_SOCK --> RESTART
    
    HEALTHY --> UPDATE["Update device health in devs[]"]
    UNHEALTHY --> UPDATE
    UPDATE --> STREAM["Send via ListAndWatch stream"]
```

**Sources:** [pkg/device_plugin/generic_device_plugin.go:528-607]()

### Virtual GPU Health Check

The vGPU health check adds NVML-based XID error monitoring:

```mermaid
graph TB
    VHC["healthCheck() goroutine<br/>(vGPU)"]
    
    NVML_INIT["nvml.Init()"]
    GET_DEVS["getDevices()"]
    WATCH_XID["watchXIDs() goroutine"]
    
    WATCHER["fsnotify.Watcher"]
    WATCH_SOCK["Watch device plugin socket"]
    WATCH_MDEV["Watch /sys/bus/mdev/devices/{uuid}<br/>for each vGPU"]
    
    SELECT["select on channels"]
    
    XID_CHAN["XID error on GPU"]
    MDEV_EVENT["mdev device event"]
    SOCK_EVENT["Socket event"]
    
    MAP_LOOKUP["gpuVgpuMap[GPU.BusID]<br/>Get affected vGPUs"]
    MARK_UNHEALTHY["Mark all vGPUs on GPU unhealthy"]
    
    VHC --> NVML_INIT
    NVML_INIT --> GET_DEVS
    GET_DEVS --> WATCH_XID
    
    VHC --> WATCHER
    WATCHER --> WATCH_SOCK
    WATCHER --> WATCH_MDEV
    
    WATCH_MDEV --> SELECT
    WATCH_SOCK --> SELECT
    WATCH_XID --> SELECT
    
    SELECT --> XID_CHAN
    SELECT --> MDEV_EVENT
    SELECT --> SOCK_EVENT
    
    XID_CHAN --> MAP_LOOKUP
    MAP_LOOKUP --> MARK_UNHEALTHY
    
    MDEV_EVENT --> HANDLE["Handle create/remove events"]
    SOCK_EVENT --> RESTART["Restart device plugin"]
```

### XID Error Monitoring

The `watchXIDs()` function monitors critical GPU errors via NVML:

```go
nvml.RegisterEventForDevice(eventSet, nvml.XidCriticalError, device.UUID)
```

Critical XID errors (excluding application errors 31, 43, 45) trigger marking all vGPUs on the affected physical GPU as unhealthy via the `gpuVgpuMap` lookup.

**Sources:** [pkg/device_plugin/generic_vgpu_device_plugin.go:281-438](), [pkg/device_plugin/generic_vgpu_device_plugin.go:388-437]()

---

## Lifecycle and Registration

```mermaid
stateDiagram-v2
    [*] --> Discovery: InitiateDevicePlugin()
    Discovery --> Creation: createDevicePlugins()
    Creation --> Starting: Start()
    
    Starting --> Cleanup: cleanup() - remove old socket
    Cleanup --> Listen: net.Listen("unix", socketPath)
    Listen --> ServerStart: grpc.NewServer()
    ServerStart --> Register: Register() with kubelet
    Register --> HealthCheck: Start healthCheck() goroutine
    HealthCheck --> Ready: Ready
    
    Ready --> Running: ListAndWatch() streams
    
    Running --> SocketRemoved: Kubelet restart detected
    SocketRemoved --> Restarting: restart()
    Restarting --> Cleanup
    
    Running --> Stopping: Stop channel signal
    Stopping --> [*]
    
    note right of Register
        Via /var/lib/kubelet/device-plugins/kubelet.sock
        Resource: nvidia.com/{DEVICE_NAME}
    end note
    
    note right of HealthCheck
        fsnotify watches device paths
        vGPU: also watches XID errors via NVML
    end note
```

**Sources:** [pkg/device_plugin/generic_device_plugin.go:130-170](), [pkg/device_plugin/generic_device_plugin.go:188-199](), [pkg/device_plugin/generic_device_plugin.go:202-223]()

---

## DaemonSet Deployment Architecture

The device plugin runs as a privileged DaemonSet in the `kube-system` namespace:

```mermaid
graph TB
    subgraph "DaemonSet Pod"
        POD["nvidia-kubevirt-gpu-dp-ctr<br/>Container"]
        
        subgraph "Volume Mounts"
            VOL1["/var/lib/kubelet/device-plugins<br/>(hostPath)"]
            VOL2["/dev/vfio<br/>(hostPath)"]
        end
    end
    
    subgraph "Host"
        KUBELET_DIR["/var/lib/kubelet/device-plugins/<br/>Device plugin sockets"]
        VFIO_DIR["/dev/vfio/<br/>VFIO devices"]
        
        KUBELET["Kubelet process"]
    end
    
    POD --> VOL1
    POD --> VOL2
    
    VOL1 -.->|mounted from| KUBELET_DIR
    VOL2 -.->|mounted from| VFIO_DIR
    
    KUBELET -.->|reads sockets| KUBELET_DIR
    POD -.->|accesses devices| VFIO_DIR
```

### Security Configuration

| Setting | Value | Purpose |
|---------|-------|---------|
| `allowPrivilegeEscalation` | `false` | Prevents privilege escalation |
| `capabilities.drop` | `["ALL"]` | Drops all Linux capabilities |
| `priorityClassName` | `system-node-critical` | Ensures high scheduling priority |
| Tolerations | `CriticalAddonsOnly` | Allows running during maintenance |

**Sources:** [manifests/nvidia-kubevirt-gpu-device-plugin.yaml:1-40]()

---

## Key Constants and Configuration

### Resource Namespaces and Prefixes

```go
const (
    DeviceNamespace   = "nvidia.com"                // Kubernetes resource namespace
    connectionTimeout = 5 * time.Second             // gRPC connection timeout
    vfioDevicePath    = "/dev/vfio"                 // VFIO device directory
    iommuDevicePath   = "/dev/iommu"                // IOMMUFD device
    gpuPrefix         = "PCI_RESOURCE_NVIDIA_COM"   // Physical GPU env var prefix
    vgpuPrefix        = "MDEV_PCI_RESOURCE_NVIDIA_COM" // vGPU env var prefix
    nvidiaVendorID    = "10de"                      // NVIDIA PCI vendor ID
)
```

### Filesystem Paths

| Path | Variable | Purpose |
|------|----------|---------|
| `/sys/bus/pci/devices` | `basePath` | Physical GPU discovery |
| `/sys/bus/mdev/devices` | `vGpuBasePath` | vGPU discovery |
| `/usr/pci.ids` | `pciIdsFilePath` | PCI device name database |
| `/var/lib/kubelet/device-plugins/kubelet.sock` | `pluginapi.KubeletSocket` | Kubelet registration endpoint |
| `/var/lib/kubelet/device-plugins/kubevirt-{NAME}.sock` | Computed | Device plugin socket |

### Supported VFIO Drivers

```go
var supportedVfioDrivers = map[string]struct{}{
    "vfio-pci":             {},  // Standard VFIO-PCI driver
    "nvgrace_gpu_vfio_pci": {},  // NVIDIA Grace GPU VFIO driver
}
```

**Sources:** [pkg/device_plugin/generic_device_plugin.go:50-57](), [pkg/device_plugin/device_plugin.go:45-79]()

---

## Summary

The NVIDIA KubeVirt GPU Device Plugin implements a sophisticated architecture with clear separation of concerns:

1. **Discovery Layer**: Scans sysfs to build comprehensive maps of physical and virtual GPU devices with topology information
2. **Plugin Layer**: Instantiates separate device plugin instances per GPU/vGPU type, each with independent gRPC servers
3. **Allocation Layer**: Validates IOMMU isolation, provides NUMA-aware allocation hints, and constructs device specifications
4. **Health Layer**: Continuously monitors device paths via fsnotify and GPU errors via NVML
5. **Integration Layer**: Implements standard Kubernetes Device Plugin API for seamless kubelet integration

This design enables robust GPU resource management for KubeVirt virtual machines with support for both passthrough and vGPU scenarios, NUMA-aware scheduling, and comprehensive health monitoring.

---

