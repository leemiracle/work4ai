<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/k8s-cc-manager · page 3 Core Application · fetched 2026-10-26 -->

# Core Application

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cmd/main.go](cmd/main.go)
- [scripts/cc-manager.sh](scripts/cc-manager.sh)

</details>



The core application consists of the main Go binary and shell script that together implement the NVIDIA GPU Confidential Computing mode management for Kubernetes nodes. This page documents the primary application components and their interactions.

For detailed information about the Go application implementation, see [Main Application (Go)](#3.1). For shell script functionality, see [GPU Management Script](#3.2). For dependency management, see [Dependencies](#3.3).

## Application Architecture

The core application follows a two-tier architecture where a Go application serves as the Kubernetes-native controller and a shell script handles the low-level GPU management operations.

```mermaid
graph TD
    subgraph "Core Application Components"
        MainGo["main.go<br/>Go Controller Application"]
        CCScript["cc-manager.sh<br/>GPU Management Script"]
        SyncConfig["SyncableCCModeConfig<br/>Thread-safe Configuration"]
        CLIFramework["urfave/cli<br/>Command Line Interface"]
    end
    
    subgraph "External Dependencies"
        K8sAPI["Kubernetes API Server"]
        GPUTools["gpu-admin-tools<br/>Python GPU Tools"]
        Kubectl["kubectl Binary"]
    end
    
    subgraph "Environment Input"
        NodeName["NODE_NAME"]
        CCDevices["CC_CAPABLE_DEVICE_IDS"]
        KubeConfig["KUBECONFIG"]
        DefaultMode["DEFAULT_CC_MODE"]
    end
    
    CLIFramework --> MainGo
    NodeName --> MainGo
    CCDevices --> MainGo
    KubeConfig --> MainGo
    DefaultMode --> MainGo
    
    MainGo --> SyncConfig
    MainGo --> K8sAPI
    MainGo --> CCScript
    
    CCScript --> GPUTools
    CCScript --> Kubectl
    CCScript --> K8sAPI
    
    style MainGo fill:#e1f5fe
    style CCScript fill:#f3e5f5
    style SyncConfig fill:#fff3e0
```

**Sources**: [cmd/main.go:1-212](), [scripts/cc-manager.sh:1-537]()

## Component Interaction Flow

The application operates through a well-defined interaction flow that ensures safe GPU CC mode transitions while maintaining Kubernetes integration.

```mermaid
sequenceDiagram
    participant "K8s API" as API
    participant "main.go" as Main
    participant "SyncableCCModeConfig" as Sync
    participant "cc-manager.sh" as Script
    participant "GPU Hardware" as GPU
    
    Note over Main: Application Startup
    Main->>API: Get node labels for NODE_NAME
    Main->>Sync: Initialize configuration
    Main->>Main: Start ContinuouslySyncCCModeConfigChanges
    
    Note over API: Label Change Event
    API->>Main: Node label updated (nvidia.com/cc.mode)
    Main->>Sync: Set new CC mode value
    Sync->>Main: Notify waiting goroutine
    
    Note over Main: CC Mode Change Processing
    Main->>Script: Execute /usr/bin/cc-manager.sh set-cc-mode
    Script->>API: Fetch current GPU operator labels
    Script->>API: Evict GPU operator components
    Script->>GPU: Set CC mode on hardware
    Script->>API: Update nvidia.com/cc.mode.state label
    Script->>API: Reschedule GPU operator components
    Script->>Main: Return success/failure
    
    Note over Main: Continue Monitoring
    Main->>Sync: Wait for next configuration change
```

**Sources**: [cmd/main.go:119-170](), [cmd/main.go:184-211](), [scripts/cc-manager.sh:336-382]()

## Kubernetes Integration Points

The application integrates with Kubernetes through multiple API interaction patterns and label management strategies.

| Integration Point | Component | Purpose | Code Location |
|-------------------|-----------|---------|---------------|
| Node Label Watching | main.go | Monitor `nvidia.com/cc.mode` changes | [cmd/main.go:184-211]() |
| GPU Operator Labels | cc-manager.sh | Control component deployment | [scripts/cc-manager.sh:217-257]() |
| Pod Lifecycle Management | cc-manager.sh | Evict and reschedule pods | [scripts/cc-manager.sh:259-334]() |
| Status Reporting | cc-manager.sh | Update `nvidia.com/cc.mode.state` | [scripts/cc-manager.sh:359-376]() |

```mermaid
graph LR
    subgraph "Kubernetes Node Labels"
        CCModeLabel["nvidia.com/cc.mode<br/>(Input)"]
        CCStateLabel["nvidia.com/cc.mode.state<br/>(Output)"]
        VfioLabel["nvidia.com/gpu.deploy.vfio-manager"]
        VgpuLabel["nvidia.com/gpu.deploy.vgpu-manager"]
        SandboxLabel["nvidia.com/gpu.deploy.sandbox-*"]
    end
    
    subgraph "Application Components"
        WatchController["cache.NewInformer<br/>Label Watcher"]
        ScriptExecutor["runScript Function"]
        LabelManager["kubectl label Commands"]
    end
    
    CCModeLabel --> WatchController
    WatchController --> ScriptExecutor
    ScriptExecutor --> LabelManager
    LabelManager --> CCStateLabel
    LabelManager --> VfioLabel
    LabelManager --> VgpuLabel
    LabelManager --> SandboxLabel
```

**Sources**: [cmd/main.go:37-41](), [cmd/main.go:194-206](), [scripts/cc-manager.sh:218-256]()

## Configuration Management

The application uses a thread-safe configuration management system to coordinate between the Kubernetes watcher and the CC mode execution logic.

```mermaid
graph TD
    subgraph "SyncableCCModeConfig Structure"
        Mutex["mutex sync.Mutex"]
        Cond["cond *sync.Cond"]
        Current["current string"]
        LastRead["lastRead string"]
    end
    
    subgraph "Operations"
        SetOp["Set(value) Method<br/>Updates current value"]
        GetOp["Get() Method<br/>Waits for changes"]
        BroadcastOp["cond.Broadcast()<br/>Notifies waiters"]
        WaitOp["cond.Wait()<br/>Blocks until change"]
    end
    
    SetOp --> Current
    SetOp --> BroadcastOp
    GetOp --> WaitOp
    GetOp --> LastRead
    
    Mutex --> SetOp
    Mutex --> GetOp
    Cond --> BroadcastOp
    Cond --> WaitOp
```

**Sources**: [cmd/main.go:48-76]()

## Error Handling and Recovery

The application implements comprehensive error handling with automatic recovery mechanisms for failed CC mode transitions.

| Error Scenario | Handler | Recovery Action | Code Location |
|----------------|---------|-----------------|---------------|
| Environment validation failure | `validateFlagsOrEnv` | Exit with error | [cmd/main.go:109-117]() |
| Kubernetes API errors | `start` function | Return formatted error | [cmd/main.go:120-134]() |
| Script execution failure | `runScript` | Log error and continue | [cmd/main.go:164-167]() |
| GPU operation failure | `_exit_failed` | Reschedule components and exit | [scripts/cc-manager.sh:210-215]() |
| Label update failure | Individual functions | Return error status | [scripts/cc-manager.sh:269-271]() |

The shell script includes a comprehensive cleanup mechanism that ensures GPU operator components are properly rescheduled even during failure scenarios:

```mermaid
graph TD
    FailureDetected["GPU Operation Failure"]
    ExitFailed["_exit_failed Function"]
    RescheduleComponents["_reschedule_gpu_operator_components"]
    RestoreLabels["Restore Original Label Values"]
    Exit["exit 1"]
    
    FailureDetected --> ExitFailed
    ExitFailed --> RescheduleComponents
    RescheduleComponents --> RestoreLabels
    RestoreLabels --> Exit
    
    subgraph "Label Restoration Logic"
        MaybeSetTrue["_maybe_set_true Function"]
        RemovePaused["Remove PAUSED_STR suffix"]
        HonorFalse["Honor 'false' values"]
    end
    
    RestoreLabels --> MaybeSetTrue
    MaybeSetTrue --> RemovePaused
    MaybeSetTrue --> HonorFalse
```

**Sources**: [scripts/cc-manager.sh:210-215](), [scripts/cc-manager.sh:320-334](), [scripts/cc-manager.sh:196-208]()

## Command Line Interface

The main application uses the `urfave/cli` framework to provide a structured command-line interface with environment variable support:

| Flag | Environment Variable | Purpose | Default |
|------|---------------------|---------|---------|
| `--kubeconfig` | `KUBECONFIG` | Path to kubeconfig file | "" |
| `--default-cc-mode` | `DEFAULT_CC_MODE` | Default CC mode when label absent | "" |

**Required Environment Variables:**
- `NODE_NAME`: Kubernetes node name for the current instance
- `CC_CAPABLE_DEVICE_IDS`: Comma-separated list of CC-capable GPU device IDs

**Sources**: [cmd/main.go:83-99](), [cmd/main.go:109-117]()

The shell script provides its own command interface supporting GPU management operations with device-specific or node-wide scope through the commands `set-cc-mode` and `get-cc-mode` with options for targeting all devices (`-a`) or specific device IDs (`-d`).

**Sources**: [scripts/cc-manager.sh:472-482](), [scripts/cc-manager.sh:489-513]()

---

