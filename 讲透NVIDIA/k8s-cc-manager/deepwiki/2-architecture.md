<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/k8s-cc-manager · page 2 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cmd/main.go](cmd/main.go)
- [scripts/cc-manager.sh](scripts/cc-manager.sh)

</details>



This document describes the high-level system architecture of the k8s-cc-manager, covering how the Go application, shell scripts, Kubernetes integration, and GPU management components work together to enable dynamic NVIDIA GPU Confidential Computing mode management in Kubernetes clusters.

For information about the specific implementation details of the core application components, see [Core Application](#3). For container build and deployment details, see [Container System](#4).

## System Overview

The k8s-cc-manager implements a Kubernetes controller pattern that watches for node label changes and orchestrates GPU Confidential Computing mode transitions. The system consists of three primary layers: a Go-based Kubernetes controller, a shell script orchestrator, and Python-based GPU management tools.

```mermaid
graph TD
    subgraph "Kubernetes Cluster"
        APIServer["Kubernetes API Server"]
        NodeLabels["Node Labels<br/>nvidia.com/cc.mode"]
        GPUOperatorPods["GPU Operator Pods<br/>vfio-manager, vgpu-manager, etc."]
    end
    
    subgraph "k8s-cc-manager Pod"
        MainApp["main.go<br/>Go Application"]
        CCManagerScript["cc-manager.sh<br/>Shell Orchestrator"]
        GPUAdminTools["gpu-admin-tools<br/>Python Tools"]
        KubectlBinary["kubectl binary"]
    end
    
    subgraph "NVIDIA Hardware"
        GPUDevices["GPU Devices<br/>CC-capable GPUs"]
        CCModeState["CC Mode State<br/>on/off/devtools"]
    end
    
    MainApp -->|"watches<br/>CCModeConfigLabel"| NodeLabels
    MainApp -->|"calls runScript()"| CCManagerScript
    CCManagerScript -->|"kubectl commands"| KubectlBinary
    CCManagerScript -->|"evict/reschedule"| GPUOperatorPods
    CCManagerScript -->|"calls python3"| GPUAdminTools
    GPUAdminTools -->|"sets CC mode"| CCModeState
    CCModeState -->|"configures"| GPUDevices
    
    KubectlBinary -->|"API calls"| APIServer
    APIServer -->|"manages"| NodeLabels
    APIServer -->|"manages"| GPUOperatorPods
```

**System Architecture Overview**

Sources: [cmd/main.go:1-212](), [scripts/cc-manager.sh:1-537]()

## Core Controller Pattern

The Go application implements a standard Kubernetes controller pattern using the client-go library to watch for changes to specific node labels and react accordingly.

```mermaid
graph TD
    subgraph "Go Application Process"
        MainFunc["main()<br/>Entry Point"]
        StartFunc["start()<br/>Controller Logic"]
        ValidateFlags["validateFlagsOrEnv()<br/>Environment Validation"]
        RunScript["runScript()<br/>Shell Script Executor"]
    end
    
    subgraph "Kubernetes Watch System"
        ListWatch["cache.NewListWatchFromClient()<br/>Node Watcher"]
        Informer["cache.NewInformer()<br/>Event Handler"]
        EventHandlers["ResourceEventHandlerFuncs<br/>Add/Update Functions"]
    end
    
    subgraph "Synchronization"
        SyncConfig["SyncableCCModeConfig<br/>Thread-safe Config"]
        CondVariable["sync.Cond<br/>Condition Variable"]
        ContinuousSync["ContinuouslySyncCCModeConfigChanges()<br/>Background Watcher"]
    end
    
    subgraph "Environment Variables"
        NodeName["NODE_NAME<br/>Current Node"]
        CCDeviceIDs["CC_CAPABLE_DEVICE_IDS<br/>Supported GPU IDs"]
        DefaultMode["DEFAULT_CC_MODE<br/>Fallback Mode"]
    end
    
    MainFunc --> ValidateFlags
    ValidateFlags --> StartFunc
    StartFunc --> ListWatch
    ListWatch --> Informer
    Informer --> EventHandlers
    StartFunc --> ContinuousSync
    ContinuousSync --> SyncConfig
    SyncConfig --> CondVariable
    EventHandlers --> SyncConfig
    StartFunc --> RunScript
    
    NodeName --> ValidateFlags
    CCDeviceIDs --> ValidateFlags
    DefaultMode --> StartFunc
```

**Controller Pattern Implementation**

The system uses several key constants and data structures:
- `CCModeConfigLabel` constant (`"nvidia.com/cc.mode"`) for the watched node label
- `SyncableCCModeConfig` struct for thread-safe configuration synchronization
- `ResourceNodes` constant for the Kubernetes resource type being watched

Sources: [cmd/main.go:37-41](), [cmd/main.go:48-76](), [cmd/main.go:184-211]()

## GPU Management Workflow

The shell script orchestrates complex GPU mode transitions by coordinating with multiple GPU operator components and managing hardware state changes.

```mermaid
graph TD
    subgraph "Shell Script Functions"
        SetCCMode["set_cc_mode()<br/>Main Orchestrator"]
        PopulateDevices["_populate_cc_capable_device_ids()<br/>Device Discovery"]
        GetAllGPUs["_get_all_cc_capable_gpus()<br/>GPU Enumeration"]
        AssertMode["_assert_cc_mode()<br/>Mode Verification"]
    end
    
    subgraph "GPU Operator Management"
        FetchLabels["_fetch_current_labels()<br/>Get Deployment State"]
        EvictComponents["_evict_gpu_operator_components()<br/>Graceful Shutdown"]
        RescheduleComponents["_reschedule_gpu_operator_components()<br/>Restart Services"]
        MaybeSetPaused["_maybe_set_paused()<br/>Label Management"]
    end
    
    subgraph "Hardware Operations"
        UnbindDevice["_unbind_device()<br/>Driver Unbinding"]
        SetGPUMode["set_gpu_cc_mode()<br/>Hardware Configuration"]
        ResetGPU["_reset_gpu_after_cc_mode()<br/>Post-change Reset"]
        PythonTools["nvidia_gpu_tools.py<br/>Low-level GPU Control"]
    end
    
    subgraph "Node Label Updates"
        StateLabel["nvidia.com/cc.mode.state<br/>success/failed"]
        DeploymentLabels["nvidia.com/gpu.deploy.*<br/>Component Control"]
        PausedString["PAUSED_STR<br/>paused-for-cc-mode-change"]
    end
    
    SetCCMode --> PopulateDevices
    SetCCMode --> GetAllGPUs
    SetCCMode --> AssertMode
    SetCCMode --> FetchLabels
    SetCCMode --> EvictComponents
    SetCCMode --> UnbindDevice
    SetCCMode --> SetGPUMode
    SetCCMode --> RescheduleComponents
    
    EvictComponents --> MaybeSetPaused
    RescheduleComponents --> MaybeSetPaused
    MaybeSetPaused --> PausedString
    
    SetGPUMode --> ResetGPU
    SetGPUMode --> PythonTools
    UnbindDevice --> PythonTools
    
    SetCCMode --> StateLabel
    EvictComponents --> DeploymentLabels
    RescheduleComponents --> DeploymentLabels
```

**GPU Management Orchestration**

The script manages five specific GPU operator components through node labels:
- `nvidia.com/gpu.deploy.vfio-manager`
- `nvidia.com/gpu.deploy.vgpu-manager` 
- `nvidia.com/gpu.deploy.sandbox-validator`
- `nvidia.com/gpu.deploy.sandbox-device-plugin`
- `nvidia.com/gpu.deploy.vgpu-device-manager`

Sources: [scripts/cc-manager.sh:336-382](), [scripts/cc-manager.sh:259-318](), [scripts/cc-manager.sh:320-334]()

## Component State Management

The system implements sophisticated state management to ensure safe GPU mode transitions without disrupting running workloads.

```mermaid
stateDiagram-v2
    [*] --> WatchingLabels : Application Start
    
    state "Label Change Detection" as Detection {
        WatchingLabels --> ValidatingMode : nvidia.com/cc.mode changed
        ValidatingMode --> WatchingLabels : Invalid mode
        ValidatingMode --> CheckingCurrent : Valid mode
    }
    
    state "Pre-transition Phase" as PreTransition {
        CheckingCurrent --> AlreadySet : Mode matches current
        CheckingCurrent --> FetchingLabels : Mode differs
        FetchingLabels --> EvictingPods : Got current labels
        EvictingPods --> WaitingForEviction : Pods marked paused
    }
    
    state "Transition Phase" as Transition {
        WaitingForEviction --> UnbindingDrivers : All pods terminated
        UnbindingDrivers --> SettingHardware : Drivers unbound
        SettingHardware --> VerifyingMode : Python tools complete
        VerifyingMode --> UpdatingStateLabel : Hardware verified
    }
    
    state "Post-transition Phase" as PostTransition {
        UpdatingStateLabel --> ReschedulingPods : State = success
        ReschedulingPods --> WatchingLabels : Pods rescheduled
        UpdatingStateLabel --> ErrorState : State = failed
        ErrorState --> ReschedulingPods : Recovery attempt
    }
    
    AlreadySet --> WatchingLabels
    
    note right of EvictingPods : Uses _maybe_set_paused()
    note right of ReschedulingPods : Uses _maybe_set_true()
    note right of SettingHardware : Calls nvidia_gpu_tools.py
```

**State Transition Management**

The system uses specific state indicators:
- `nvidia.com/cc.mode.state` label with values `"success"` or `"failed"`
- `PAUSED_STR` constant (`"paused-for-cc-mode-change"`) for component coordination
- Timeout values (5 minutes) for pod eviction operations

Sources: [scripts/cc-manager.sh:170-208](), [scripts/cc-manager.sh:259-318](), [scripts/cc-manager.sh:336-382]()

## Kubernetes Integration Architecture

The application integrates deeply with Kubernetes APIs using the client-go library for both watching resources and managing node labels.

| Component | Purpose | Key APIs Used |
|-----------|---------|---------------|
| **Node Watcher** | Monitor label changes | `cache.NewListWatchFromClient()`, `fields.OneTermEqualSelector()` |
| **Event Handler** | Process label updates | `cache.ResourceEventHandlerFuncs{}` |
| **Label Manager** | Update node labels | `kubectl` CLI commands via shell execution |
| **Pod Coordinator** | Manage operator pods | `kubectl wait --for=delete pod` commands |

The system requires specific environment variables for proper Kubernetes integration:
- `NODE_NAME`: Identifies the current node for label operations
- `KUBECONFIG`: Optional kubeconfig file path for API access
- `CC_CAPABLE_DEVICE_IDS`: Comma-separated list of supported GPU device IDs

```mermaid
graph LR
    subgraph "Kubernetes API Operations"
        GetNode["clientset.CoreV1().Nodes().Get()"]
        WatchNodes["ListWatch with field selector"]
        UpdateLabels["kubectl label --overwrite"]
        WaitPods["kubectl wait --for=delete pod"]
    end
    
    subgraph "Configuration Sources"
        EnvVars["Environment Variables<br/>NODE_NAME, KUBECONFIG"]
        CLIFlags["CLI Flags<br/>--kubeconfig, --default-cc-mode"]
        FieldSelector["fields.OneTermEqualSelector<br/>metadata.name filter"]
    end
    
    subgraph "API Resources"
        NodeResource["v1.Node<br/>Label target"]
        PodResources["Pods<br/>GPU operator components"]
        Namespaces["OPERATOR_NAMESPACE<br/>Component namespace"]
    end
    
    EnvVars --> GetNode
    CLIFlags --> GetNode
    FieldSelector --> WatchNodes
    WatchNodes --> NodeResource
    UpdateLabels --> NodeResource
    WaitPods --> PodResources
    PodResources --> Namespaces
```

**Kubernetes API Integration**

Sources: [cmd/main.go:119-170](), [cmd/main.go:184-211](), [scripts/cc-manager.sh:217-257]()

---

