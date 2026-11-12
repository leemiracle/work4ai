<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/vscode-jupyter · page 3 Kernel Management · fetched 2026-10-26 -->

# Kernel Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/api.proposed.kernelStartHook.d.ts](src/api.proposed.kernelStartHook.d.ts)
- [src/kernels/kernel.ts](src/kernels/kernel.ts)
- [src/kernels/kernelProvider.base.ts](src/kernels/kernelProvider.base.ts)
- [src/kernels/kernelProvider.node.ts](src/kernels/kernelProvider.node.ts)
- [src/kernels/kernelProvider.node.unit.test.ts](src/kernels/kernelProvider.node.unit.test.ts)
- [src/kernels/kernelProvider.web.ts](src/kernels/kernelProvider.web.ts)
- [src/kernels/kernelProvider.web.unit.test.ts](src/kernels/kernelProvider.web.unit.test.ts)
- [src/kernels/kernelStatusProvider.ts](src/kernels/kernelStatusProvider.ts)
- [src/kernels/serviceRegistry.node.ts](src/kernels/serviceRegistry.node.ts)
- [src/kernels/serviceRegistry.web.ts](src/kernels/serviceRegistry.web.ts)
- [src/kernels/types.ts](src/kernels/types.ts)
- [src/notebooks/serviceRegistry.node.ts](src/notebooks/serviceRegistry.node.ts)
- [src/notebooks/serviceRegistry.web.ts](src/notebooks/serviceRegistry.web.ts)
- [src/platform/constants.ts](src/platform/constants.ts)
- [src/standalone/userJupyterServer/serverSelectorForTests.ts](src/standalone/userJupyterServer/serverSelectorForTests.ts)
- [src/test/client/api.vscode.test.ts](src/test/client/api.vscode.test.ts)

</details>



This document covers the complete kernel management system in the VS Code Jupyter extension, which is responsible for discovering, creating, managing, and executing code against Jupyter kernels. The system handles both local and remote kernels, provides lifecycle management, and serves as the foundation for notebook and interactive window execution.

For information about notebook controllers and VS Code integration, see [Notebook Controllers](#4.1). For details about Python environment discovery, see [Environment Discovery](#6.2).

## System Overview

The kernel management system is built around a three-layer architecture that separates kernel discovery, lifecycle management, and execution coordination. The system supports multiple kernel types including local Python interpreters, kernel specifications, remote Jupyter servers, and third-party provided kernels.

```mermaid
graph TB
    subgraph "Kernel Discovery Layer"
        KF["KernelFinder"] --> LPF["LocalPythonAndRelatedNonPythonKernelSpecFinder"]
        KF --> LKF["LocalKnownPathKernelSpecFinder"] 
        KF --> CKF["ContributedLocalKernelSpecFinder"]
        KF --> RKF["RemoteKernelFinder"]
    end
    
    subgraph "Kernel Provider Layer"
        KP["KernelProvider"] --> K["Kernel"]
        TKP["ThirdPartyKernelProvider"] --> TK["ThirdPartyKernel"]
        KP --> KE["NotebookKernelExecution"]
    end
    
    subgraph "Session Layer"
        KSF["KernelSessionFactory"] --> JKS["JupyterKernelSession"]
        KSF --> RKS["RawKernelSession"]
        K --> KSF
        TK --> KSF
    end
    
    subgraph "Connection Types"
        LKSM["LocalKernelSpecConnectionMetadata"]
        PKM["PythonKernelConnectionMetadata"]  
        RKSM["RemoteKernelSpecConnectionMetadata"]
        LRKM["LiveRemoteKernelConnectionMetadata"]
    end
    
    KF --> KP
    KF --> TKP
    
    LKSM --> K
    PKM --> K
    RKSM --> K
    LRKM --> K
```

**Sources**: [src/kernels/types.ts:525-579](), [src/kernels/kernelProvider.base.ts:25-122](), [src/kernels/kernelFinder.ts]()

## Core Kernel Types and Abstractions

The system defines several key abstractions that form the foundation of kernel management. The base kernel interface `IBaseKernel` provides common functionality, while specialized implementations handle different kernel types.

```mermaid
graph TB
    subgraph "Kernel Abstractions"
        IBK["IBaseKernel"] --> IK["IKernel"]
        IBK --> ITK["IThirdPartyKernel"]
        IK --> K["Kernel"]
        ITK --> TK["ThirdPartyKernel"]
    end
    
    subgraph "Connection Metadata Types"
        KCM["KernelConnectionMetadata"] --> LKCM["LocalKernelConnectionMetadata"]
        KCM --> RKCM["RemoteKernelConnectionMetadata"]
        LKCM --> LKSM["LocalKernelSpecConnectionMetadata"]
        LKCM --> PKM["PythonKernelConnectionMetadata"]
        RKCM --> RKSM["RemoteKernelSpecConnectionMetadata"]
        RKCM --> LRKM["LiveRemoteKernelConnectionMetadata"]
    end
    
    subgraph "Session Types"
        IKS["IKernelSession"] --> IJKS["IJupyterKernelSession"]
        IKS --> IRKS["IRawKernelSession"]
    end
    
    K --> KCM
    TK --> KCM
    K --> IKS
    TK --> IKS
```

The `BaseKernel` class provides core functionality including status management, lifecycle hooks, and execution coordination. All kernels extend this base to inherit common behavior while specializing for their specific use cases.

**Sources**: [src/kernels/types.ts:345-429](), [src/kernels/kernel.ts:119-244](), [src/kernels/types.ts:55-295]()

## Kernel Provider System

The kernel provider system manages kernel instances and their lifecycle. It uses a factory pattern to create kernels and maintains mappings between notebooks/resources and their associated kernels.

```mermaid
graph TB
    subgraph "Provider Hierarchy"
        IBKP["IBaseKernelProvider<T>"] --> IKP["IKernelProvider"]
        IBKP --> ITKP["IThirdPartyKernelProvider"]
        IKP --> BCKP["BaseCoreKernelProvider"]
        ITKP --> BTKP["BaseThirdPartyKernelProvider"]
        BCKP --> KP_NODE["KernelProvider.node"]
        BCKP --> KP_WEB["KernelProvider.web"]
        BTKP --> TKP_NODE["ThirdPartyKernelProvider.node"]
        BTKP --> TKP_WEB["ThirdPartyKernelProvider.web"]
    end
    
    subgraph "Kernel Storage"
        KP_NODE --> KBND["kernelsByNotebook: WeakMap"]
        KP_NODE --> KBID["kernelsById: Map"]
        KP_NODE --> EXEC["executions: WeakMap"]
    end
    
    subgraph "Events"
        KP_NODE --> OCK["onDidCreateKernel"]
        KP_NODE --> OSK["onDidStartKernel"]
        KP_NODE --> ORK["onDidRestartKernel"]
        KP_NODE --> ODK["onDidDisposeKernel"]
        KP_NODE --> OPIK["onDidPostInitializeKernel"]
    end
```

The provider maintains weak references to notebooks to automatically clean up kernels when notebooks are closed, while using strong references by ID for programmatic access.

**Sources**: [src/kernels/kernelProvider.base.ts:25-190](), [src/kernels/kernelProvider.node.ts:38-118](), [src/kernels/types.ts:524-579]()

## Kernel Connection Metadata

Connection metadata describes how to connect to or start a kernel. The system supports four primary connection types, each with specific metadata requirements and connection procedures.

| Connection Type | Class | Use Case | Key Properties |
|----------------|-------|----------|----------------|
| Local Kernel Spec | `LocalKernelSpecConnectionMetadata` | Kernels started from local kernel.json specs | `kernelSpec`, `interpreter?` |
| Python Interpreter | `PythonKernelConnectionMetadata` | Python kernels started directly from interpreter | `interpreter`, `kernelSpec` |
| Remote Kernel Spec | `RemoteKernelSpecConnectionMetadata` | Kernels started on remote Jupyter servers | `kernelSpec`, `baseUrl`, `serverProviderHandle` |
| Live Remote Kernel | `LiveRemoteKernelConnectionMetadata` | Connect to existing remote kernels | `kernelModel`, `baseUrl`, `serverProviderHandle` |

```mermaid
graph LR
    subgraph "Connection Factories"
        LKSM["LocalKernelSpecConnectionMetadata::create()"]
        PKM["PythonKernelConnectionMetadata::create()"]
        RKSM["RemoteKernelSpecConnectionMetadata::create()"]
        LRKM["LiveRemoteKernelConnectionMetadata::create()"]
    end
    
    subgraph "Serialization"
        BKCM["BaseKernelConnectionMetadata::fromJSON()"]
        LKSM --> JSON1["toJSON()"]
        PKM --> JSON2["toJSON()"]
        RKSM --> JSON3["toJSON()"]
        LRKM --> JSON4["toJSON()"]
        JSON1 --> BKCM
        JSON2 --> BKCM
        JSON3 --> BKCM
        JSON4 --> BKCM
    end
```

All connection metadata classes support JSON serialization for persistence and provide hashed IDs for telemetry and caching purposes.

**Sources**: [src/kernels/types.ts:55-295](), [src/kernels/types.ts:301-328]()

## Kernel Lifecycle Management

The kernel lifecycle is managed through a series of hooks and events that coordinate startup, execution, interruption, restart, and disposal operations. The `BaseKernel` class orchestrates these operations while maintaining consistent state.

```mermaid
graph TB
    subgraph "Lifecycle States"
        UNKNOWN["unknown"] --> STARTING["starting"]
        STARTING --> IDLE["idle"]
        IDLE --> BUSY["busy"]
        BUSY --> IDLE
        IDLE --> RESTARTING["restarting"]
        RESTARTING --> IDLE
        IDLE --> TERMINATING["terminating"]
        BUSY --> TERMINATING
        TERMINATING --> DEAD["dead"]
    end
    
    subgraph "Lifecycle Operations"
        START["start()"] --> STARTING
        EXECUTE["execute()"] --> BUSY
        INTERRUPT["interrupt()"] --> IDLE
        RESTART["restart()"] --> RESTARTING
        DISPOSE["dispose()"] --> TERMINATING
    end
    
    subgraph "Hooks and Events"
        START --> WS["hook: willStart"]
        RESTART --> WR["hook: willRestart"] 
        INTERRUPT --> WI["hook: willInterrupt"]
        DISPOSE --> WC["hook: willCancel"]
        IDLE --> DS["hook: didStart"]
        RESTARTING --> RC["hook: restartCompleted"]
        IDLE --> IC["hook: interruptCompleted"]
    end
```

The hook system allows external components to participate in kernel lifecycle events, enabling features like progress reporting, telemetry, and cleanup operations.

**Sources**: [src/kernels/kernel.ts:246-366](), [src/kernels/types.ts:330-336](), [src/kernels/kernel.ts:367-451]()

## Kernel Session Management

Kernel sessions provide the communication layer between the kernel management system and actual kernel processes. The system supports different session types depending on the kernel connection method.

```mermaid
graph TB
    subgraph "Session Factory"
        KSF["KernelSessionFactory"] --> IJSC["IJupyterServerConnector"]
        KSF --> IRKSF["IRawKernelSessionFactory"]
        IJSC --> IJC["IJupyterConnection"]
        IJC --> IJKS["IJupyterKernelSession"]
        IRKSF --> IRKS["IRawKernelSession"]
    end
    
    subgraph "Session Types"
        IJKS --> RJ["kind: 'remoteJupyter'"]
        IJKS --> LJ["kind: 'localJupyter'"]
        IRKS --> LR["kind: 'localRaw'"]
    end
    
    subgraph "Session Capabilities"
        IJKS --> JL["JupyterLab Protocol"]
        IRKS --> DP["Direct Process"]
        JL --> WS["WebSocket Communication"]
        DP --> ST["Stdio Communication"]
    end
```

Sessions abstract the communication protocol differences between raw kernel processes and Jupyter server connections, providing a unified interface for kernel operations.

**Sources**: [src/kernels/types.ts:606-620](), [src/kernels/types.ts:737-743](), [src/kernels/types.ts:721-735]()

## Service Registration and Dependency Injection

The kernel management system uses dependency injection to manage component relationships and enable platform-specific implementations. Services are registered differently for Node.js and web environments.

```mermaid
graph TB
    subgraph "Core Services"
        IKF["IKernelFinder"] --> KF["KernelFinder"]
        IKP["IKernelProvider"] --> KP_IMPL["KernelProvider.node|web"]
        ITKP["IThirdPartyKernelProvider"] --> TKP_IMPL["ThirdPartyKernelProvider.node|web"]
        IKSF["IKernelSessionFactory"] --> KSF_IMPL["KernelSessionFactory.node|web"]
    end
    
    subgraph "Platform Specific - Node"
        IRNS["IRawNotebookSupportedService"] --> RNS_NODE["RawNotebookSupportedService"]
        IKL["IKernelLauncher"] --> KL["KernelLauncher"]
        IRKSF["IRawKernelSessionFactory"] --> RKSF["RawKernelSessionFactory"]
        IKWD["IKernelWorkingDirectory"] --> KWD["KernelWorkingDirectory"]
    end
    
    subgraph "Platform Specific - Web"
        IRNS --> RNS_WEB["RawNotebookSupportedService (stub)"]
    end
    
    subgraph "Support Services"
        ISCP["IStartupCodeProviders"] --> SCP["KernelStartupCodeProviders"]
        IKDS["IKernelDependencyService"] --> KDS["KernelDependencyService"]
        IKSP["IKernelStatusProvider"] --> KSP["KernelStatusProvider"]
    end
```

The registration system enables different implementations for Node.js (supporting raw kernels) and web (Jupyter server only) while maintaining the same interfaces.

**Sources**: [src/kernels/serviceRegistry.node.ts:52-146](), [src/kernels/serviceRegistry.web.ts:44-106]()

## Kernel Discovery System

The kernel discovery system finds available kernels from multiple sources and presents them as connection options. Discovery is coordinated by the `KernelFinder` which aggregates results from specialized finder components.

```mermaid
graph TB
    subgraph "Kernel Finder Coordination"
        KF["KernelFinder"] --> LPNPF["LocalPythonAndRelatedNonPythonKernelSpecFinder"]
        KF --> LKPF["LocalKnownPathKernelSpecFinder"]
        KF --> CLKSF["ContributedLocalKernelSpecFinder"]
        KF --> IKF["IContributedKernelFinder[]"]
    end
    
    subgraph "Discovery Sources"
        LPNPF --> PE["Python Environments"]
        LPNPF --> KS["Kernel Specs"]
        LKPF --> JP["Jupyter Paths"]
        LKPF --> SYS["System Kernel Specs"]
        CLKSF --> EXT["Extension Contributions"]
        IKF --> TP["Third Party Finders"]
    end
    
    subgraph "Remote Discovery"
        RKF["RemoteKernelFinder"] --> JS["Jupyter Servers"]
        RKF --> LK["Live Kernels"]
        RKF --> RS["Remote Specs"]
    end
    
    subgraph "Connection Metadata Output"
        PE --> PKM["PythonKernelConnectionMetadata"]
        KS --> LKSM["LocalKernelSpecConnectionMetadata"]
        SYS --> LKSM
        JS --> RKSM["RemoteKernelSpecConnectionMetadata"]
        LK --> LRKM["LiveRemoteKernelConnectionMetadata"]
    end
```

The discovery system runs continuously and updates available kernels as environments change, kernel specs are added, or remote servers are configured.

**Sources**: [src/kernels/kernelFinder.ts](), [src/kernels/raw/finder/localPythonAndRelatedNonPythonKernelSpecFinder.node.ts](), [src/kernels/raw/finder/localKnownPathKernelSpecFinder.node.ts]()

## Integration with VS Code

The kernel management system integrates with VS Code through several coordination mechanisms that bridge the kernel abstraction with VS Code's notebook API and user interface components.

```mermaid
graph TB
    subgraph "VS Code Integration Points"
        KP["KernelProvider"] --> NC["NotebookController"]
        KP --> NKE["NotebookKernelExecution"]
        NC --> VSC_NB["VS Code Notebook API"]
        NKE --> VSC_EXEC["VS Code Execution API"]
    end
    
    subgraph "User Interface"
        KSP["KernelStatusProvider"] --> PR["Progress Reporting"]
        KRI["KernelRefreshIndicator"] --> UI["Status Bar Updates"]
        KCM["KernelCrashMonitor"] --> ERR["Error Notifications"]
    end
    
    subgraph "Lifecycle Coordination"
        KARM["KernelAutoReconnectMonitor"] --> AUTO["Automatic Reconnection"]
        KARSM["KernelAutoRestartMonitor"] --> RESTART["Restart on Crash"]
        KST["KernelStartupTelemetry"] --> TEL["Telemetry Events"]
    end
    
    subgraph "Third Party API"
        TPKP["ThirdPartyKernelProvider"] --> API["Extension API"]
        API --> EXT["External Extensions"]
    end
```

The integration layer ensures that kernel lifecycle events are properly reflected in the VS Code user interface and that external extensions can participate in the kernel ecosystem.

**Sources**: [src/kernels/kernelStatusProvider.ts:19-121](), [src/notebooks/controllers/types.ts](), [src/kernels/kernelProvider.node.ts:80-117]()

---

