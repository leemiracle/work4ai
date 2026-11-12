<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/k8s-operator-libs · page 3 Core Upgrade System · fetched 2026-10-26 -->

# Core Upgrade System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [pkg/upgrade/upgrade_state.go](pkg/upgrade/upgrade_state.go)
- [pkg/upgrade/upgrade_state_test.go](pkg/upgrade/upgrade_state_test.go)

</details>



## Purpose and Scope

The Core Upgrade System is the central orchestration layer responsible for managing driver upgrades across Kubernetes clusters. This system implements a sophisticated state machine that coordinates node-by-node driver upgrades while respecting operational constraints such as maximum parallel upgrades, node availability requirements, and validation policies.

This document covers the core state management, orchestration logic, and upgrade workflows. For information about specific manager components (PodManager, DrainManager, etc.), see [Manager Components](#3.3). For details about upgrade modes implementation, see [Upgrade Modes](#3.2). For API specifications and custom resource definitions, see [APIs and Custom Resources](#4).

## System Architecture

The Core Upgrade System is built around the `ClusterUpgradeStateManager` interface and its primary implementation `ClusterUpgradeStateManagerImpl`. This manager serves as a state machine that processes cluster-wide upgrade states and coordinates transitions between upgrade phases.

```mermaid
graph TB
    subgraph "Core Upgrade System"
        CUSM["ClusterUpgradeStateManagerImpl<br/>(State Machine)"]
        CUM["CommonUpgradeManagerImpl<br/>(Shared Logic)"]
        
        subgraph "Upgrade Mode Processors"
            InPlace["InplaceNodeStateManagerImpl<br/>(Direct Operations)"]
            Requestor["RequestorNodeStateManagerImpl<br/>(Maintenance Operator)"]
        end
        
        subgraph "Manager Components"
            PodMgr["PodManager"]
            DrainMgr["DrainManager"] 
            CordonMgr["CordonManager"]
            ValidationMgr["ValidationManager"]
            SafeLoadMgr["SafeDriverLoadManager"]
        end
        
        subgraph "State Provider"
            NUSP["NodeUpgradeStateProvider<br/>(Labels & Annotations)"]
        end
    end
    
    CUSM --> CUM
    CUSM --> InPlace
    CUSM --> Requestor
    CUM --> PodMgr
    CUM --> DrainMgr
    CUM --> CordonMgr
    CUM --> ValidationMgr
    CUM --> SafeLoadMgr
    CUM --> NUSP
    
    InPlace --> CUM
    Requestor --> CUM
```

**Core State Management Flow**

```mermaid
graph LR
    BuildState["BuildState()<br/>Snapshot Creation"] --> ApplyState["ApplyState()<br/>State Processing"]
    ApplyState --> ProcessNodes["Process Nodes by State<br/>- ProcessDoneOrUnknownNodes<br/>- ProcessUpgradeRequiredNodes<br/>- ProcessCordonRequiredNodes<br/>- etc."]
    ProcessNodes --> StateTransitions["Node State Transitions<br/>Based on Current State"]
```

Sources: [pkg/upgrade/upgrade_state.go:34-92](), [pkg/upgrade/upgrade_state.go:98-164](), [pkg/upgrade/upgrade_state.go:166-281]()

## Upgrade State Machine

The system implements a comprehensive state machine with 12 distinct node upgrade states. Each state represents a specific phase in the upgrade lifecycle, with well-defined entry and exit conditions.

### State Definitions and Transitions

```mermaid
stateDiagram-v2
    [*] --> UpgradeStateUnknown: "Node discovered"
    UpgradeStateUnknown --> UpgradeStateDone: "Pod up-to-date"
    UpgradeStateUnknown --> UpgradeStateUpgradeRequired: "Pod outdated"
    UpgradeStateDone --> UpgradeStateUpgradeRequired: "Pod outdated or<br/>safe load annotation"
    
    UpgradeStateUpgradeRequired --> UpgradeStateCordonRequired: "In-place mode"
    UpgradeStateUpgradeRequired --> UpgradeStateNodeMaintenanceRequired: "Requestor mode"
    
    UpgradeStateCordonRequired --> UpgradeStateWaitForJobsRequired: "Node cordoned"
    UpgradeStateWaitForJobsRequired --> UpgradeStatePodDeletionRequired: "Jobs completed<br/>(if enabled)"
    UpgradeStateWaitForJobsRequired --> UpgradeStateDrainRequired: "Jobs completed<br/>(if pod deletion disabled)"
    UpgradeStatePodDeletionRequired --> UpgradeStateDrainRequired: "Pods deleted"
    UpgradeStateDrainRequired --> UpgradeStatePodRestartRequired: "Node drained<br/>or drain disabled"
    
    UpgradeStateNodeMaintenanceRequired --> UpgradeStatePostMaintenanceRequired: "Maintenance operator<br/>completed"
    UpgradeStatePostMaintenanceRequired --> UpgradeStatePodRestartRequired: "Post-maintenance<br/>cleanup done"
    
    UpgradeStatePodRestartRequired --> UpgradeStateValidationRequired: "Pod restarted<br/>(if validation enabled)"
    UpgradeStatePodRestartRequired --> UpgradeStateUncordonRequired: "Pod restarted<br/>(if validation disabled)"
    UpgradeStatePodRestartRequired --> UpgradeStateFailed: "Pod restart failure"
    
    UpgradeStateValidationRequired --> UpgradeStateUncordonRequired: "Validation passed"
    UpgradeStateValidationRequired --> UpgradeStateFailed: "Validation timeout"
    
    UpgradeStateUncordonRequired --> UpgradeStateDone: "Node uncordoned"
    
    UpgradeStateFailed --> UpgradeStateUncordonRequired: "Recovery possible"
```

### State Processing Methods

The `ClusterUpgradeStateManagerImpl` processes nodes through dedicated methods for each state:

| State | Processing Method | Purpose |
|-------|------------------|---------|
| `UpgradeStateUnknown` / `UpgradeStateDone` | `ProcessDoneOrUnknownNodes()` | Determine if upgrade is needed |
| `UpgradeStateUpgradeRequired` | `ProcessUpgradeRequiredNodes()` | Start upgrade process |
| `UpgradeStateCordonRequired` | `ProcessCordonRequiredNodes()` | Cordon nodes |
| `UpgradeStateWaitForJobsRequired` | `ProcessWaitForJobsRequiredNodes()` | Wait for job completion |
| `UpgradeStatePodDeletionRequired` | `ProcessPodDeletionRequiredNodes()` | Delete pods (optional) |
| `UpgradeStateDrainRequired` | `ProcessDrainNodes()` | Drain nodes |
| `UpgradeStateNodeMaintenanceRequired` | `ProcessNodeMaintenanceRequiredNodes()` | Handle maintenance operator |
| `UpgradeStatePodRestartRequired` | `ProcessPodRestartNodes()` | Restart driver pods |
| `UpgradeStateValidationRequired` | `ProcessValidationRequiredNodes()` | Validate upgrade |
| `UpgradeStateUncordonRequired` | `ProcessUncordonRequiredNodes()` | Uncordon nodes |
| `UpgradeStateFailed` | `ProcessUpgradeFailedNodes()` | Handle failures |

Sources: [pkg/upgrade/upgrade_state.go:204-281](), [pkg/upgrade/upgrade_state_test.go:196-225](), [pkg/upgrade/upgrade_state_test.go:884-918]()

## Operational Constraints

The upgrade system enforces several operational constraints to maintain cluster stability and control upgrade velocity.

### Parallel Upgrade Limits

```mermaid
graph TB
    subgraph "Constraint Evaluation"
        MaxParallel["MaxParallelUpgrades<br/>Policy Setting"]
        MaxUnavailable["MaxUnavailable<br/>Policy Setting"] 
        CurrentUpgrades["Current Upgrades<br/>In Progress"]
        UnavailableNodes["Currently Unavailable<br/>Nodes"]
    end
    
    subgraph "Constraint Logic"
        ParallelCheck{"Available Parallel<br/>Slots?"}
        UnavailableCheck{"Within Unavailable<br/>Limit?"}
        CanUpgrade["Can Start<br/>Upgrade"]
        MustWait["Must Wait"]
    end
    
    MaxParallel --> ParallelCheck
    CurrentUpgrades --> ParallelCheck
    MaxUnavailable --> UnavailableCheck
    UnavailableNodes --> UnavailableCheck
    
    ParallelCheck -->|Yes| UnavailableCheck
    ParallelCheck -->|No| MustWait
    UnavailableCheck -->|Yes| CanUpgrade
    UnavailableCheck -->|No| MustWait
```

The system supports flexible upgrade constraints:
- `MaxParallelUpgrades`: Limits concurrent upgrades (0 = unlimited)
- `MaxUnavailable`: Limits total unavailable nodes (supports percentage or absolute values)
- The more restrictive constraint takes precedence

Sources: [pkg/upgrade/upgrade_state_test.go:294-349](), [pkg/upgrade/upgrade_state_test.go:384-440](), [pkg/upgrade/upgrade_state_test.go:514-544]()

### Node State Tracking

The system tracks node state through Kubernetes labels and annotations:

```mermaid
graph LR
    subgraph "Node State Storage"
        StateLabel["Label:<br/>upgrade.cattle.io/state"]
        RequestedAnnotation["Annotation:<br/>upgrade.cattle.io/requested"]
        UnschedulableAnnotation["Annotation:<br/>upgrade.cattle.io/initial-state"]
        SafeLoadAnnotation["Annotation:<br/>upgrade.cattle.io/wait-for-safe-load"]
        RequestorAnnotation["Annotation:<br/>upgrade.cattle.io/requestor-mode"]
    end
    
    StateLabel --> NodeState["Current Upgrade State"]
    RequestedAnnotation --> ForceUpgrade["Force Upgrade Flag"]
    UnschedulableAnnotation --> InitialState["Node Was Initially<br/>Unschedulable"]
    SafeLoadAnnotation --> SafeDriverLoad["Safe Driver Loading<br/>Required"]
    RequestorAnnotation --> RequestorMode["Using Maintenance<br/>Operator Mode"]
```

Sources: [pkg/upgrade/upgrade_state.go:354-378](), [pkg/upgrade/upgrade_state_test.go:226-270](), [pkg/upgrade/upgrade_state_test.go:271-293]()

## Key Processing Workflows  

### BuildState Workflow

The `BuildState()` method creates a point-in-time snapshot of the cluster upgrade state:

```mermaid
flowchart TD
    Start["BuildState()"] --> GetDS["GetDriverDaemonSets()<br/>Find driver DaemonSets"]
    GetDS --> GetPods["List driver pods<br/>by namespace and labels"]
    GetPods --> FilterPods["Filter pods:<br/>- Owned by DaemonSets<br/>- Orphaned pods<br/>- Skip unscheduled"]
    FilterPods --> BuildNode["buildNodeUpgradeState()<br/>for each pod"]
    BuildNode --> GetNode["Get Node object"]
    GetNode --> GetNM["Get NodeMaintenance<br/>(if requestor mode)"]
    GetNM --> CreateState["Create NodeUpgradeState<br/>with Node, Pod, DaemonSet, NodeMaintenance"]
    CreateState --> GroupStates["Group by upgrade state<br/>into ClusterUpgradeState"]
    GroupStates --> Return["Return ClusterUpgradeState"]
```

### ApplyState Workflow

The `ApplyState()` method processes the cluster state and applies upgrade policy:

```mermaid
flowchart TD
    Start["ApplyState()"] --> ValidateInputs["Validate inputs<br/>Check AutoUpgrade enabled"]
    ValidateInputs --> LogStates["Log current state counts<br/>for all upgrade states"]
    LogStates --> ProcessUnknown["ProcessDoneOrUnknownNodes()<br/>UpgradeStateUnknown"]
    ProcessUnknown --> ProcessDone["ProcessDoneOrUnknownNodes()<br/>UpgradeStateDone"]
    ProcessDone --> ProcessRequired["ProcessUpgradeRequiredNodes()<br/>Start upgrades within limits"]
    ProcessRequired --> ProcessCordon["ProcessCordonRequiredNodes()<br/>Cordon nodes"]
    ProcessCordon --> ProcessJobs["ProcessWaitForJobsRequiredNodes()<br/>Wait for job completion"]
    ProcessJobs --> ProcessPodDelete["ProcessPodDeletionRequiredNodes()<br/>Delete pods (if enabled)"]
    ProcessPodDelete --> ProcessDrain["ProcessDrainNodes()<br/>Drain nodes"]
    ProcessDrain --> ProcessMaintenance["ProcessNodeMaintenanceRequiredNodes()<br/>Handle maintenance operator"]
    ProcessMaintenance --> ProcessRestart["ProcessPodRestartNodes()<br/>Restart driver pods"]
    ProcessRestart --> ProcessFailed["ProcessUpgradeFailedNodes()<br/>Handle upgrade failures"]
    ProcessFailed --> ProcessValidation["ProcessValidationRequiredNodes()<br/>Validate upgrades"]
    ProcessValidation --> ProcessUncordon["ProcessUncordonRequiredNodes()<br/>Uncordon nodes"]
    ProcessUncordon --> Complete["Complete processing"]
```

Sources: [pkg/upgrade/upgrade_state.go:98-164](), [pkg/upgrade/upgrade_state.go:166-281]()

## Integration Points

The Core Upgrade System integrates with several external components and systems:

### Kubernetes API Integration

```mermaid
graph TB
    subgraph "Core Upgrade System"
        CUSM["ClusterUpgradeStateManagerImpl"]
        BuildState["BuildState()"]
        ApplyState["ApplyState()"]
    end
    
    subgraph "Kubernetes Resources"
        Nodes["Nodes<br/>(Labels & Annotations)"]
        Pods["Pods<br/>(Driver Pods)"]
        DaemonSets["DaemonSets<br/>(Driver Definitions)"]
        NodeMaintenance["NodeMaintenance CRDs<br/>(Maintenance Operator)"]
    end
    
    BuildState --> Nodes
    BuildState --> Pods  
    BuildState --> DaemonSets
    BuildState --> NodeMaintenance
    
    ApplyState --> Nodes
    ApplyState --> Pods
    ApplyState --> NodeMaintenance
```

### Manager Component Integration

The Core Upgrade System delegates specific operations to specialized manager components:

| Manager | Responsibility | Integration Point |
|---------|---------------|-------------------|
| `PodManager` | Pod lifecycle operations | Pod restart, deletion, validation |
| `DrainManager` | Node draining operations | Node drain scheduling and monitoring |
| `CordonManager` | Node scheduling control | Cordon/uncordon operations |
| `ValidationManager` | Upgrade validation | Post-upgrade validation checks |
| `SafeDriverLoadManager` | Safe driver loading | Driver initialization coordination |
| `NodeUpgradeStateProvider` | State persistence | Node label/annotation management |

Sources: [pkg/upgrade/upgrade_state.go:57-62](), [pkg/upgrade/upgrade_state.go:327-350](), [pkg/upgrade/upgrade_state_test.go:46-71]()

---

