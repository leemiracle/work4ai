<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/k8s-operator-libs · page 2 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [pkg/upgrade/common_manager.go](pkg/upgrade/common_manager.go)
- [pkg/upgrade/consts.go](pkg/upgrade/consts.go)
- [pkg/upgrade/upgrade_state.go](pkg/upgrade/upgrade_state.go)

</details>



This document provides a comprehensive overview of the k8s-operator-libs system architecture, focusing on the core driver upgrade management components and their interactions. It covers the main orchestration components, state management, and the two supported upgrade modes.

For information about specific API definitions and custom resources, see [APIs and Custom Resources](#4). For details on individual manager components, see [Manager Components](#3.3).

## System Overview

The k8s-operator-libs library provides a state machine-driven approach to managing Kubernetes driver upgrades. The system is built around a central orchestrator that coordinates specialized managers to handle different aspects of the upgrade process.

```mermaid
graph TB
    subgraph "Core Orchestration"
        CUSM["ClusterUpgradeStateManager<br/>(Interface)"]
        CUSMI["ClusterUpgradeStateManagerImpl<br/>(Main Implementation)"]
        CUMI["CommonUpgradeManagerImpl<br/>(Shared Logic)"]
    end
    
    subgraph "Upgrade Mode Implementations"
        INSM["InplaceNodeStateManagerImpl<br/>(Direct Node Operations)"]
        RNSM["RequestorNodeStateManagerImpl<br/>(Maintenance Operator)"]
    end
    
    subgraph "Specialized Managers"
        PM["PodManager<br/>(Pod Operations)"]
        DM["DrainManager<br/>(Node Draining)"]
        CM["CordonManager<br/>(Node Scheduling)"]
        VM["ValidationManager<br/>(Driver Validation)"]
        SDLM["SafeDriverLoadManager<br/>(Safe Initialization)"]
    end
    
    subgraph "Data Structures"
        CUS["ClusterUpgradeState<br/>(Cluster Snapshot)"]
        NUS["NodeUpgradeState<br/>(Node + Pod + DS)"]
        StateConsts["Upgrade State Constants<br/>(12 States)"]
    end
    
    CUSM --> CUSMI
    CUSMI --> CUMI
    CUSMI --> INSM
    CUSMI --> RNSM
    
    CUMI --> PM
    CUMI --> DM
    CUMI --> CM
    CUMI --> VM
    CUMI --> SDLM
    
    CUSMI --> CUS
    CUS --> NUS
    StateConsts --> NUS
```

Sources: [pkg/upgrade/upgrade_state.go:34-92](), [pkg/upgrade/common_manager.go:22-54](), [pkg/upgrade/common_manager.go:82-133]()

## Core Upgrade Orchestration

The upgrade orchestration follows a well-defined flow from state building through processing. The `ClusterUpgradeStateManagerImpl` serves as the central coordinator.

```mermaid
graph LR
    subgraph "State Building Phase"
        BuildState["BuildState()<br/>Line 99-164"]
        GetDriverDS["GetDriverDaemonSets()<br/>Line 105-109"]
        ListPods["List Driver Pods<br/>Line 114-123"]
        BuildNodeState["buildNodeUpgradeState()<br/>Line 354-378"]
    end
    
    subgraph "State Processing Phase"
        ApplyState["ApplyState()<br/>Line 171-281"]
        ProcessDone["ProcessDoneOrUnknownNodes()<br/>Line 205-214"]
        ProcessUpgrade["ProcessUpgradeRequiredNodesWrapper()<br/>Line 216-221"]
        ProcessStates["Process All Other States<br/>Line 223-278"]
    end
    
    subgraph "State Options"
        StateOpts["StateOptions<br/>Line 94-96"]
        RequestorOpts["RequestorOptions<br/>UseMaintenanceOperator"]
    end
    
    BuildState --> GetDriverDS
    GetDriverDS --> ListPods
    ListPods --> BuildNodeState
    BuildNodeState --> ApplyState
    
    ApplyState --> ProcessDone
    ProcessDone --> ProcessUpgrade
    ProcessUpgrade --> ProcessStates
    
    StateOpts --> ProcessUpgrade
    RequestorOpts --> StateOpts
```

Sources: [pkg/upgrade/upgrade_state.go:98-164](), [pkg/upgrade/upgrade_state.go:171-281](), [pkg/upgrade/upgrade_state.go:94-96]()

## Upgrade State Machine

The system implements a comprehensive state machine with 12 distinct states that nodes transition through during driver upgrades.

```mermaid
stateDiagram-v2
    [*] --> UpgradeStateUnknown
    
    UpgradeStateUnknown --> UpgradeStateUpgradeRequired: "Driver outdated or upgrade requested"
    UpgradeStateDone --> UpgradeStateUpgradeRequired: "Safe driver load or upgrade annotation"
    
    UpgradeStateUpgradeRequired --> UpgradeStateCordonRequired: "In-place mode"
    UpgradeStateUpgradeRequired --> UpgradeStateNodeMaintenanceRequired: "Requestor mode"
    
    UpgradeStateCordonRequired --> UpgradeStateWaitForJobsRequired: "Node cordoned"
    UpgradeStateWaitForJobsRequired --> UpgradeStatePodDeletionRequired: "Jobs completed"
    UpgradeStatePodDeletionRequired --> UpgradeStateDrainRequired: "Pods deleted"
    UpgradeStateDrainRequired --> UpgradeStatePodRestartRequired: "Node drained"
    
    UpgradeStateNodeMaintenanceRequired --> UpgradeStatePostMaintenanceRequired: "External maintenance complete"
    UpgradeStatePostMaintenanceRequired --> UpgradeStatePodRestartRequired: "Ready for pod restart"
    
    UpgradeStatePodRestartRequired --> UpgradeStateValidationRequired: "Pod restarted (validation enabled)"
    UpgradeStatePodRestartRequired --> UpgradeStateUncordonRequired: "Pod restarted (validation disabled)"
    
    UpgradeStateValidationRequired --> UpgradeStateUncordonRequired: "Validation passed"
    UpgradeStateUncordonRequired --> UpgradeStateDone: "Node uncordoned"
    
    UpgradeStatePodRestartRequired --> UpgradeStateFailed: "Pod restart failure"
    UpgradeStateValidationRequired --> UpgradeStateFailed: "Validation timeout"
    UpgradeStateDrainRequired --> UpgradeStateFailed: "Drain failure"
    
    UpgradeStateFailed --> UpgradeStateUncordonRequired: "Recovery successful"
    
    UpgradeStateDone --> [*]
```

Sources: [pkg/upgrade/consts.go:48-82](), [pkg/upgrade/upgrade_state.go:184-198]()

## Manager Subsystem Architecture

The system uses specialized managers to handle different aspects of the upgrade process, all coordinated through the `CommonUpgradeManagerImpl`.

```mermaid
graph TB
    subgraph "State Provider Layer"
        NUSP["NodeUpgradeStateProvider<br/>(Labels & Annotations)"]
    end
    
    subgraph "Manager Layer"
        CUMI["CommonUpgradeManagerImpl"]
        
        PM["PodManager<br/>- SchedulePodsRestart()<br/>- SchedulePodEviction()<br/>- ScheduleCheckOnPodCompletion()"]
        
        DM["DrainManager<br/>- ScheduleNodesDrain()<br/>- DrainConfiguration"]
        
        CM["CordonManager<br/>- Cordon()<br/>- Uncordon()"]
        
        VM["ValidationManager<br/>- Validate()<br/>- podSelector"]
        
        SDLM["SafeDriverLoadManager<br/>- UnblockLoading()<br/>- IsWaitingForSafeDriverLoad()"]
    end
    
    subgraph "Processing Methods"
        ProcessCordon["ProcessCordonRequiredNodes()<br/>Line 361-379"]
        ProcessWait["ProcessWaitForJobsRequiredNodes()<br/>Line 384-419"]
        ProcessDeletion["ProcessPodDeletionRequiredNodes()<br/>Line 424-453"]
        ProcessDrain["ProcessDrainNodes()<br/>Line 329-357"]
        ProcessRestart["ProcessPodRestartNodes()<br/>Line 457-524"]
        ProcessValidation["ProcessValidationRequiredNodes()<br/>Line 573-603"]
    end
    
    CUMI --> PM
    CUMI --> DM
    CUMI --> CM
    CUMI --> VM
    CUMI --> SDLM
    CUMI --> NUSP
    
    ProcessCordon --> CM
    ProcessWait --> PM
    ProcessDeletion --> PM
    ProcessDrain --> DM
    ProcessRestart --> PM
    ProcessRestart --> SDLM
    ProcessValidation --> VM
    ProcessValidation --> SDLM
```

Sources: [pkg/upgrade/common_manager.go:82-133](), [pkg/upgrade/common_manager.go:361-379](), [pkg/upgrade/common_manager.go:384-419](), [pkg/upgrade/common_manager.go:424-453]()

## Upgrade Mode Comparison

The system supports two distinct upgrade modes, each implementing the `ProcessNodeStateManager` interface with different operational approaches.

| Aspect | In-Place Mode (`InplaceNodeStateManagerImpl`) | Requestor Mode (`RequestorNodeStateManagerImpl`) |
|--------|-----------------------------------------------|--------------------------------------------------|
| **Node Operations** | Direct Kubernetes API calls | External maintenance operator integration |
| **Cordoning** | Internal `CordonManager.Cordon()` | Via NodeMaintenance CRD |
| **Draining** | Internal `DrainManager.ScheduleNodesDrain()` | Handled by external operator |
| **State Flow** | `UpgradeRequired` → `CordonRequired` → ... | `UpgradeRequired` → `NodeMaintenanceRequired` → ... |
| **Dependencies** | Only Kubernetes API | NodeMaintenance CRDs + external operator |
| **Configuration** | Always available | Requires `UseMaintenanceOperator: true` |

```mermaid
graph LR
    subgraph "Mode Selection Logic"
        StateOpts["StateOptions<br/>Line 94-96"]
        UseMaintenanceOp["UseMaintenanceOperator<br/>(boolean flag)"]
        
        StateOpts --> UseMaintenanceOp
    end
    
    subgraph "In-Place Flow"
        InplaceUpgrade["ProcessUpgradeRequiredNodes()<br/>(inplace)"]
        InplaceUncordon["ProcessUncordonRequiredNodes()<br/>(inplace)"]
        
        InplaceUpgrade --> InplaceUncordon
    end
    
    subgraph "Requestor Flow"
        RequestorUpgrade["ProcessUpgradeRequiredNodes()<br/>(requestor)"]
        RequestorMaintenance["ProcessNodeMaintenanceRequiredNodes()<br/>(requestor)"]
        RequestorUncordon["ProcessUncordonRequiredNodes()<br/>(requestor)"]
        
        RequestorUpgrade --> RequestorMaintenance
        RequestorMaintenance --> RequestorUncordon
    end
    
    UseMaintenanceOp -->|"false"| InplaceUpgrade
    UseMaintenanceOp -->|"true"| RequestorUpgrade
```

Sources: [pkg/upgrade/upgrade_state.go:287-325](), [pkg/upgrade/upgrade_state.go:57-92]()

---

