<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvkind · page 5 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [pkg/nvkind/api.go](pkg/nvkind/api.go)
- [pkg/nvkind/cluster.go](pkg/nvkind/cluster.go)
- [pkg/nvkind/config.go](pkg/nvkind/config.go)

</details>



This document provides a technical overview of nvkind's internal architecture, including its layered design, core abstractions, and integration mechanisms. It explains how the system is structured to enable GPU-enabled KIND cluster creation through clean separation of concerns and well-defined interfaces.

For detailed information about specific architectural components, see:
- System component interactions and data flows: [System Overview](#5.1)
- Core library API and implementation details: [Core Library (pkg/nvkind)](#5.2)
- CLI command structure and flag processing: [CLI Tool (cmd/nvkind)](#5.3)
- NVIDIA GPU integration mechanisms: [GPU Integration Mechanism](#5.4)

## Architectural Overview

nvkind follows a **layered architecture** with clear separation between the user-facing CLI and the reusable core library. This design enables the core library to be consumed programmatically by other Go applications while providing a convenient command-line interface for direct user interaction.

```mermaid
graph TB
    subgraph "CLI Layer"
        Main["cmd/nvkind/main.go<br/>Entry Point"]
        CreateCmd["cluster_create.go<br/>Create Command"]
        ListCmd["cluster_list.go<br/>List Command"]
        PrintGPUsCmd["print_gpus.go<br/>Print GPUs Command"]
    end
    
    subgraph "Core Library - pkg/nvkind"
        API["api.go<br/>Public API Types"]
        Config["config.go<br/>Configuration Builder"]
        Cluster["cluster.go<br/>Cluster Operations"]
    end
    
    subgraph "External Systems"
        KIND["KIND<br/>sigs.k8s.io/kind"]
        K8sClient["Kubernetes Client<br/>client-go"]
        NVML["NVIDIA NVML<br/>go-nvlib/pkg/nvml"]
        Docker["Docker with<br/>nvidia-container-toolkit"]
    end
    
    Main --> CreateCmd
    Main --> ListCmd
    Main --> PrintGPUsCmd
    
    CreateCmd --> API
    ListCmd --> API
    PrintGPUsCmd --> API
    
    API --> Config
    API --> Cluster
    
    Config --> NVML
    Cluster --> KIND
    Cluster --> K8sClient
    Cluster --> NVML
    
    KIND --> Docker
```

**Sources:** [pkg/nvkind/api.go:1-177](), [pkg/nvkind/cluster.go:1-378](), [pkg/nvkind/config.go:1-157]()

## Core Abstractions

The architecture is built around four primary abstractions defined in [pkg/nvkind/api.go:35-63]():

| Type | Purpose | Key Responsibilities |
|------|---------|---------------------|
| `Config` | Configuration builder | Template processing, GPU detection, KIND cluster configuration generation |
| `Cluster` | Cluster lifecycle manager | Cluster creation, node discovery, RuntimeClass registration, configuration persistence |
| `Node` | Node representation | Individual node operations and GPU information retrieval |
| `GPUInfo` | GPU metadata | Stores GPU index, name, and UUID for display and debugging |

```mermaid
classDiagram
    class Config {
        +kind.Cluster
        -nvml.Interface
        -io.Writer stdout
        -io.Writer stderr
    }
    
    class Cluster {
        +string Name
        -kind.Cluster config
        -string kubeconfig
        -nvml.Interface
        -io.Writer stdout
        -io.Writer stderr
        +Create(opts) error
        +GetNodes() []Node
        +RegisterNvidiaRuntimeClass() error
        +PrintClusterInfo() error
    }
    
    class Node {
        +string Name
        -kind.Node config
        -nvml.Interface
        -io.Writer stdout
        -io.Writer stderr
    }
    
    class GPUInfo {
        +string Index
        +string Name
        +string UUID
    }
    
    Config --> Cluster : "creates"
    Cluster --> Node : "contains"
    Node --> GPUInfo : "provides"
```

**Sources:** [pkg/nvkind/api.go:35-63](), [pkg/nvkind/cluster.go:68-95]()

## Functional Options Pattern

nvkind uses the **functional options pattern** extensively to provide flexible, extensible configuration without breaking API compatibility. This pattern is implemented through option types and constructor functions.

```mermaid
graph LR
    subgraph "Config Construction"
        NewConfig["NewConfig(opts...)"]
        ConfigOption["ConfigOption<br/>functions"]
        WithImage["WithImage(image)"]
        WithNvml["WithNvml(nvml)"]
        WithConfigTemplate["WithConfigTemplate()"]
        WithConfigValues["WithConfigValues()"]
        WithOutput["WithOutput(stdout, stderr)"]
    end
    
    subgraph "Cluster Construction"
        NewCluster["NewCluster(opts...)"]
        ClusterOption["ClusterOption<br/>functions"]
        WithName["WithName(name)"]
        WithConfig["WithConfig(config)"]
        WithKubeConfig["WithKubeConfig(path)"]
    end
    
    ConfigOption --> WithImage
    ConfigOption --> WithNvml
    ConfigOption --> WithConfigTemplate
    ConfigOption --> WithConfigValues
    ConfigOption --> WithOutput
    
    WithImage --> NewConfig
    WithNvml --> NewConfig
    WithConfigTemplate --> NewConfig
    WithConfigValues --> NewConfig
    WithOutput --> NewConfig
    
    ClusterOption --> WithName
    ClusterOption --> WithConfig
    ClusterOption --> WithKubeConfig
    
    WithName --> NewCluster
    WithConfig --> NewCluster
    WithKubeConfig --> NewCluster
```

**Example option type definitions:**

| Option Type | Definition Location | Purpose |
|-------------|-------------------|---------|
| `ConfigOption` | [pkg/nvkind/api.go:78]() | Customize configuration generation behavior |
| `ClusterOption` | [pkg/nvkind/api.go:139]() | Customize cluster construction parameters |
| `ClusterCreateOption` | [pkg/nvkind/api.go:164]() | Customize cluster creation behavior (retain, wait) |

**Sources:** [pkg/nvkind/api.go:65-176](), [pkg/nvkind/config.go:32-109](), [pkg/nvkind/cluster.go:68-95]()

## Template Processing Architecture

The configuration system uses Go's `text/template` engine with custom functions to generate KIND cluster configurations dynamically based on GPU availability.

```mermaid
flowchart TD
    Start["NewConfig()"] --> LoadTemplate["Load Template<br/>(embedded or file)"]
    LoadTemplate --> LoadValues["Load Values<br/>(embedded or file)"]
    LoadValues --> BuildFuncMap["buildFuncMap()<br/>Sprig + numGPUs"]
    
    BuildFuncMap --> ParseTemplate["template.Parse()"]
    ParseTemplate --> UnmarshalValues["yaml.Unmarshal(values)"]
    UnmarshalValues --> ExecuteTemplate["template.Execute()"]
    
    ExecuteTemplate --> NumGPUs["numGPUs() function<br/>calls nvml.DeviceGetCount()"]
    NumGPUs --> NVML["NVML Library"]
    
    ExecuteTemplate --> UnmarshalConfig["yaml.Unmarshal()<br/>into kind.Cluster"]
    UnmarshalConfig --> ApplyImageOverride["Apply image override<br/>if specified"]
    ApplyImageOverride --> Return["Return Config"]
```

**Function map composition** ([pkg/nvkind/config.go:111-122]()):
1. Custom `numGPUs` function queries NVML for GPU count
2. User-provided `extraFuncMap` for extensibility
3. Sprig template functions for general-purpose operations

**Sources:** [pkg/nvkind/config.go:32-156](), [pkg/nvkind/api.go:29-33]()

## Integration Architecture

nvkind integrates with external systems through well-defined boundaries, using subprocess execution for CLI tools and Go SDKs for programmatic APIs.

```mermaid
graph TB
    subgraph "nvkind Core"
        ClusterOps["Cluster Operations<br/>cluster.go"]
        ConfigGen["Config Generation<br/>config.go"]
    end
    
    subgraph "CLI Integration"
        KIND_CLI["KIND CLI<br/>subprocess exec"]
        Kubectl_CLI["kubectl CLI<br/>subprocess exec"]
    end
    
    subgraph "SDK Integration"
        K8sClientGo["Kubernetes client-go<br/>ConfigMap persistence"]
        NVML_SDK["go-nvlib NVML<br/>GPU enumeration"]
    end
    
    subgraph "Runtime"
        Docker["Docker with<br/>nvidia-container-toolkit"]
        GPU["Host GPU Devices<br/>/dev/nvidia*"]
    end
    
    ClusterOps -->|"kind create cluster"| KIND_CLI
    ClusterOps -->|"kind get nodes"| KIND_CLI
    ClusterOps -->|"kind get clusters"| KIND_CLI
    
    ClusterOps -->|"kubectl apply"| Kubectl_CLI
    ClusterOps -->|"kubectl cluster-info"| Kubectl_CLI
    
    ClusterOps -->|"ConfigMap CRUD"| K8sClientGo
    ConfigGen -->|"DeviceGetCount()"| NVML_SDK
    
    KIND_CLI --> Docker
    Docker --> GPU
```

**Integration methods:**

| System | Integration Method | Key Functions |
|--------|-------------------|---------------|
| KIND | Subprocess execution | [cluster.go:54-66]() `GetClusterNames()`, [cluster.go:97-134]() `Create()` |
| kubectl | Subprocess execution | [cluster.go:161-173]() `RegisterNvidiaRuntimeClass()` |
| Kubernetes API | client-go SDK | [cluster.go:294-326]() `addConfigBytesToExistingCluster()` |
| NVIDIA NVML | go-nvlib SDK | [config.go:124-136]() `numGPUs()` |

**Sources:** [pkg/nvkind/cluster.go:54-377](), [pkg/nvkind/config.go:124-136]()

## Configuration Persistence

nvkind persists cluster configuration in a Kubernetes ConfigMap to enable retrieval and validation when connecting to existing clusters.

```mermaid
sequenceDiagram
    participant CLI as "CLI Command"
    participant Cluster as "Cluster.Create()"
    participant KIND as "KIND CLI"
    participant K8s as "Kubernetes API"
    
    CLI->>Cluster: Create cluster
    Cluster->>KIND: kind create cluster --config -
    KIND-->>Cluster: Cluster created
    
    Cluster->>K8s: Create ConfigMap<br/>"nvkind-cluster-config"
    Note over K8s: namespace: default<br/>data["config"]: YAML bytes
    K8s-->>Cluster: ConfigMap created
    
    Note over CLI,K8s: Later: Connect to existing cluster
    
    CLI->>Cluster: NewCluster(WithName("existing"))
    Cluster->>K8s: Get ConfigMap<br/>"nvkind-cluster-config"
    K8s-->>Cluster: YAML config bytes
    Cluster->>Cluster: Validate config<br/>if provided
    Cluster-->>CLI: Cluster object
```

**ConfigMap structure:**
- Name: `nvkind-cluster-config` (constant defined at [cluster.go:43]())
- Namespace: `default`
- Data key: `config` containing marshaled `kind.Cluster` YAML

**Sources:** [pkg/nvkind/cluster.go:42-44](), [cluster.go:294-348]()

## Dependency Injection

The architecture uses **dependency injection** for testability and flexibility, particularly for the NVML interface and I/O streams.

**Injectable dependencies:**

| Dependency | Interface/Type | Purpose | Default Value |
|------------|---------------|---------|---------------|
| NVML | `nvml.Interface` | GPU detection and enumeration | `nvml.New()` [config.go:40-42]() |
| stdout | `io.Writer` | Standard output stream | `os.Stdout` [config.go:43-45]() |
| stderr | `io.Writer` | Standard error stream | `os.Stderr` [config.go:46-48]() |

This enables:
- **Unit testing** with mock NVML implementations
- **Output capture** for testing and automation
- **Runtime flexibility** without modifying core logic

**Sources:** [pkg/nvkind/api.go:92-96](), [pkg/nvkind/config.go:40-48]()

## Error Handling Strategy

nvkind follows Go's idiomatic error handling with structured error wrapping using `fmt.Errorf` with `%w` verb for error chain preservation.

**Common error patterns:**
- Template processing errors: [config.go:70-89]()
- Subprocess execution errors: [cluster.go:120-127]()
- Kubernetes API errors: [cluster.go:317-323]()
- NVML operation errors: [config.go:125-133]()

All errors are wrapped with contextual information to provide clear error messages and enable error inspection via `errors.Is()` and `errors.As()`.

**Sources:** [pkg/nvkind/cluster.go:1-378](), [pkg/nvkind/config.go:1-157]()

---

