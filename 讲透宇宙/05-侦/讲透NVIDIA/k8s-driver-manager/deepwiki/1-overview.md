<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/k8s-driver-manager · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)
- [cmd/driver-manager/main.go](cmd/driver-manager/main.go)
- [go.mod](go.mod)

</details>



The NVIDIA k8s-driver-manager is a Kubernetes component designed to orchestrate seamless upgrades of NVIDIA GPU drivers across cluster nodes. It ensures that all prerequisites are met before driver upgrades by managing GPU operator component lifecycle, node operations, and driver module cleanup.

This document covers the overall system purpose, architecture, and key components. For detailed information about the build system and development workflow, see [Build System](#3.1). For container deployment and CI/CD processes, see [Deployment](#4).

## System Purpose and Context

The k8s-driver-manager operates as part of the broader NVIDIA GPU operator ecosystem, coordinating driver upgrades through a systematic process of component eviction, node management, and driver cleanup.

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        Node1["Node 1<br/>NVIDIA GPUs"]
        Node2["Node 2<br/>NVIDIA GPUs"] 
        Node3["Node N<br/>NVIDIA GPUs"]
        
        subgraph "GPU Operator Components"
            DevicePlugin["nvidia-device-plugin-daemonset"]
            GFD["gpu-feature-discovery"]
            DCGM["nvidia-dcgm-exporter"]
            Toolkit["nvidia-container-toolkit-daemonset"]
            Validator["nvidia-operator-validator"]
        end
        
        subgraph "Driver Manager System"
            DM["k8s-driver-manager Pod"]
            CLI["driver-manager CLI"]
            DM --> CLI
        end
    end
    
    subgraph "Host System Integration"
        NVML["NVIDIA Management Library<br/>/usr/lib64/libnvidia-ml.so"]
        DriverFS["Driver Filesystem<br/>/run/nvidia/driver"]
        KernelMods["Kernel Modules<br/>/sys/module/nvidia"]
        VFIOManager["vfio-manage script"]
    end
    
    CLI --> DevicePlugin
    CLI --> GFD
    CLI --> DCGM
    CLI --> Toolkit
    CLI --> Validator
    
    CLI --> NVML
    CLI --> DriverFS
    CLI --> KernelMods
    CLI --> VFIOManager
    
    DM --> Node1
    DM --> Node2  
    DM --> Node3
```

Sources: [README.md:1-12](), [cmd/driver-manager/main.go:43-65]()

## Core Application Components

The system is built around the `DriverManager` struct which coordinates operations through specialized subsystems for Kubernetes integration, driver management, and system utilities.

```mermaid
graph TB
    subgraph "CLI Application Layer"
        MainApp["main() function"]
        UninstallCmd["uninstall_driver command"]
        PreflightCmd["preflight_check command"]
        
        MainApp --> UninstallCmd
        MainApp --> PreflightCmd
    end
    
    subgraph "Core Management Layer"
        DM["DriverManager struct"]
        Config["config struct"]
        ComponentState["componentState struct"]
        
        DM --> Config
        DM --> ComponentState
    end
    
    subgraph "Kubernetes Integration"
        KubeClient["kube.Client"]
        NodeOps["Node Operations<br/>CordonNode()<br/>UncordonNode()<br/>DrainNode()"]
        LabelMgmt["Label Management<br/>UpdateNodeLabels()<br/>GetNodeLabelValue()"]
        PodEviction["Pod Eviction<br/>WaitForPodTermination()<br/>DeleteOrEvictPods()"]
        
        KubeClient --> NodeOps
        KubeClient --> LabelMgmt
        KubeClient --> PodEviction
    end
    
    subgraph "Driver and System Management"
        NVMLClient["nvml.Client<br/>ValidateDriver()"]
        KernelMods["Kernel Module Management<br/>unix.DeleteModule()"]
        MountMgmt["mount.RecursiveUnmount()"]
        VFIOOps["vfio-manage unbind --all"]
        
        NVMLClient --> KernelMods
        KernelMods --> MountMgmt
        MountMgmt --> VFIOOps
    end
    
    UninstallCmd --> DM
    PreflightCmd --> DM
    DM --> KubeClient
    DM --> NVMLClient
```

Sources: [cmd/driver-manager/main.go:100-108](), [cmd/driver-manager/main.go:67-98](), [cmd/driver-manager/main.go:214-242]()

## GPU Operator Component Management

The system manages multiple GPU operator components through a label-based deployment control mechanism, transitioning components between active, paused, and disabled states during driver upgrades.

```mermaid
graph TB
    subgraph "Component State Management"
        CS["componentState struct"]
        
        CS --> pluginDeployed["pluginDeployed<br/>nvidia.com/gpu.deploy.device-plugin"]
        CS --> gfdDeployed["gfdDeployed<br/>nvidia.com/gpu.deploy.gpu-feature-discovery"]
        CS --> dcgmExporterDeployed["dcgmExporterDeployed<br/>nvidia.com/gpu.deploy.dcgm-exporter"]
        CS --> toolkitDeployed["toolkitDeployed<br/>nvidia.com/gpu.deploy.container-toolkit"]
        CS --> validatorDeployed["validatorDeployed<br/>nvidia.com/gpu.deploy.operator-validator"]
    end
    
    subgraph "Label State Transitions"
        True["true<br/>(active)"]
        Paused["paused-for-driver-upgrade<br/>(evicted)"]
        False["false<br/>(disabled)"]
        
        True --> Paused
        Paused --> True
    end
    
    subgraph "Management Operations"
        FetchLabels["fetchCurrentLabels()<br/>GetNodeLabelValue()"]
        EvictComponents["evictAllGPUOperatorComponents()<br/>maybeSetPaused()"]
        RescheduleComponents["rescheduleGPUOperatorComponents()<br/>maybeSetTrue()"]
        WaitTermination["waitForPodsToTerminate()<br/>WaitForPodTermination()"]
        
        FetchLabels --> EvictComponents
        EvictComponents --> WaitTermination
        WaitTermination --> RescheduleComponents
    end
    
    CS --> FetchLabels
    EvictComponents --> True
    RescheduleComponents --> Paused
```

Sources: [cmd/driver-manager/main.go:84-98](), [cmd/driver-manager/main.go:500-535](), [cmd/driver-manager/main.go:777-805](), [cmd/driver-manager/main.go:537-549]()

## Driver Upgrade Workflow

The system follows a structured workflow that ensures safe driver upgrades by coordinating node drainage, component eviction, driver cleanup, and component rescheduling.

```mermaid
sequenceDiagram
    participant CLI as "driver-manager CLI"
    participant DM as "DriverManager"
    participant Kube as "kube.Client"
    participant System as "Host System"
    participant NVML as "nvml.Client"
    
    CLI->>DM: "uninstallDriver()"
    DM->>NVML: "isHostDriver()<br/>ValidateDriver()"
    
    alt Host driver detected
        DM->>Kube: "disableContainerizedDriver()<br/>UpdateNodeLabels()"
        DM-->>CLI: "driver is pre-installed on host"
    else Containerized driver
        DM->>DM: "fetchCurrentLabels()"
        DM->>DM: "evictAllGPUOperatorComponents()"
        DM->>Kube: "UpdateNodeLabels(paused)"
        DM->>DM: "waitForPodsToTerminate()"
        
        alt GPU pod eviction enabled
            DM->>Kube: "CordonNode()"
            DM->>Kube: "nvDrainNode()<br/>DeleteOrEvictPods()"
        end
        
        DM->>DM: "isDriverLoaded()"
        alt Driver loaded
            DM->>DM: "cleanupDriver()"
            DM->>System: "unloadDriver()<br/>unix.DeleteModule()"
            DM->>System: "unmountRootfs()<br/>mount.RecursiveUnmount()"
        end
        
        DM->>System: "unbindVfioPCI()<br/>vfio-manage unbind --all"
        DM->>Kube: "UncordonNode()"
        DM->>DM: "rescheduleGPUOperatorComponents()"
        DM->>Kube: "UpdateNodeLabels(true)"
    end
```

Sources: [cmd/driver-manager/main.go:261-383](), [cmd/driver-manager/main.go:636-693](), [cmd/driver-manager/main.go:695-711](), [cmd/driver-manager/main.go:716-720]()

## Configuration and Environment Integration

The system provides extensive configuration options through environment variables and CLI flags, supporting various deployment scenarios including GPU Direct RDMA, custom node selectors, and different drain policies.

| Configuration Category | Key Parameters | Environment Variables |
|------------------------|----------------|----------------------|
| Node Management | `nodeName`, `drainTimeout`, `drainUseForce` | `NODE_NAME`, `DRAIN_TIMEOUT_SECONDS`, `DRAIN_USE_FORCE` |
| GPU Pod Eviction | `enableGPUPodEviction`, `nodeLabelForGPUPodEviction` | `ENABLE_GPU_POD_EVICTION`, `NODE_LABEL_FOR_GPU_POD_EVICTION` |
| Operator Integration | `operatorNamespace` | `OPERATOR_NAMESPACE` |
| GPU Direct RDMA | `gpuDirectRDMAEnabled`, `useHostMofed` | `GPU_DIRECT_RDMA_ENABLED`, `USE_HOST_MOFED` |
| Auto Drain Policy | `enableAutoDrain` | `ENABLE_AUTO_DRAIN` |

The system integrates with Kubernetes through the `kube.Client` and validates GPU environments using `nvml.Client` with configurable driver root paths and validation policies.

Sources: [cmd/driver-manager/main.go:67-81](), [cmd/driver-manager/main.go:127-212](), [cmd/driver-manager/main.go:43-65]()

---

