<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/vgpu-device-manager · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)

</details>



## Purpose and Scope

The NVIDIA vGPU Device Manager is a comprehensive system designed to manage virtual GPU (vGPU) configurations in Kubernetes environments and standalone deployments. This system enables administrators to declaratively define and apply vGPU device configurations across GPU-enabled nodes, providing fine-grained control over how physical GPUs are partitioned into virtual devices for different workloads.

This document provides a high-level overview of the system architecture, core components, and operational workflows. For detailed information about specific components, see [CLI Tools](#2.1), [Kubernetes Daemon](#2.2), and [Configuration System](#2.3). For build and deployment procedures, refer to [Build System & Development](#4) and [Deployment & Operations](#7).

*Sources: [README.md:1-190]()*

## System Architecture Overview

The NVIDIA vGPU Device Manager consists of two primary applications that work together to manage vGPU configurations:

```mermaid
graph TB
    subgraph "Core Applications"
        CLI["nvidia-vgpu-dm<br/>CLI Tool"]
        K8S_DAEMON["nvidia-k8s-vgpu-dm<br/>Kubernetes Daemon"]
    end
    
    subgraph "Configuration Layer"
        CONFIG_FILES["YAML Configuration Files<br/>config-t4.yaml, config-example.yaml"]
        API_SPECS["API Specifications<br/>v1.Spec, VGPUConfigSpec"]
    end
    
    subgraph "Target Systems"
        NVIDIA_VGPU_MGR["NVIDIA vGPU Manager<br/>libnvidia-ml.so"]
        PHYSICAL_GPUS["Physical GPUs<br/>Tesla T4, etc."]
        VGPU_DEVICES["Virtual GPU Devices<br/>T4-1Q, T4-2Q, etc."]
    end
    
    subgraph "Kubernetes Integration"
        NODE_LABELS["Node Labels<br/>nvidia.com/vgpu.config"]
        CONFIGMAPS["ConfigMaps<br/>vgpu-devices-config"]
        DAEMONSET["DaemonSet<br/>nvidia-vgpu-device-manager"]
    end
    
    CLI --> CONFIG_FILES
    CLI --> API_SPECS
    CLI --> NVIDIA_VGPU_MGR
    
    K8S_DAEMON --> CONFIG_FILES
    K8S_DAEMON --> API_SPECS
    K8S_DAEMON --> NODE_LABELS
    K8S_DAEMON --> CONFIGMAPS
    K8S_DAEMON --> NVIDIA_VGPU_MGR
    
    NVIDIA_VGPU_MGR --> PHYSICAL_GPUS
    PHYSICAL_GPUS --> VGPU_DEVICES
    
    DAEMONSET --> K8S_DAEMON
```

*Sources: [README.md:8-16](), diagrams provided by user*

## Core Applications

The system provides two main entry points for vGPU management:

### Standalone CLI Tool (`nvidia-vgpu-dm`)

The CLI tool enables direct interaction with vGPU configurations on individual nodes:

```mermaid
graph LR
    subgraph "CLI Commands"
        APPLY["apply command<br/>Apply vGPU config"]
        ASSERT["assert command<br/>Validate current config"]
    end
    
    subgraph "CLI Implementation"
        MAIN_CLI["main.go<br/>CLI orchestration"]
        CMD_APPLY["cmd/nvidia-vgpu-dm/apply"]
        CMD_ASSERT["cmd/nvidia-vgpu-dm/assert"]
    end
    
    subgraph "Configuration Processing"
        CONFIG_PARSER["ParseConfigFile<br/>YAML parsing"]
        DEVICE_MATCHER["GetSelectedVGPUConfig<br/>Device selection"]
    end
    
    subgraph "vGPU Operations"
        VGPU_MANAGER["VGPUConfigManager<br/>nvlib interaction"]
        DEVICE_CREATE["CreateVGPUDevices"]
        DEVICE_VALIDATE["ValidateVGPUDevices"]
    end
    
    APPLY --> CMD_APPLY
    ASSERT --> CMD_ASSERT
    CMD_APPLY --> MAIN_CLI
    CMD_ASSERT --> MAIN_CLI
    
    MAIN_CLI --> CONFIG_PARSER
    CONFIG_PARSER --> DEVICE_MATCHER
    DEVICE_MATCHER --> VGPU_MANAGER
    
    VGPU_MANAGER --> DEVICE_CREATE
    VGPU_MANAGER --> DEVICE_VALIDATE
```

*Sources: [README.md:77-102](), [README.md:114-163]()*

### Kubernetes Daemon (`nvidia-k8s-vgpu-dm`)

The Kubernetes daemon manages vGPU configurations automatically based on node labels and ConfigMaps:

```mermaid
graph TB
    subgraph "Daemon Core"
        MAIN_K8S["main.go<br/>Node monitoring loop"]
        FIND_GPU["find.go<br/>GPU discovery"]
        RECONFIG_MIG["reconfigure_mig.go<br/>MIG management"]
    end
    
    subgraph "Kubernetes Watchers"
        NODE_WATCHER["Node Label Watcher<br/>nvidia.com/vgpu.config"]
        CONFIG_WATCHER["ConfigMap Watcher<br/>vgpu-devices-config"]
    end
    
    subgraph "GPU Operand Management"
        SHUTDOWN_OPERANDS["Shutdown GPU Services<br/>device-plugin, validator"]
        APPLY_CONFIG["Apply vGPU Configuration"]
        RESTART_OPERANDS["Restart GPU Services"]
        UPDATE_STATUS["Update Node Status"]
    end
    
    NODE_WATCHER --> MAIN_K8S
    CONFIG_WATCHER --> MAIN_K8S
    MAIN_K8S --> FIND_GPU
    MAIN_K8S --> SHUTDOWN_OPERANDS
    SHUTDOWN_OPERANDS --> APPLY_CONFIG
    APPLY_CONFIG --> RECONFIG_MIG
    RECONFIG_MIG --> RESTART_OPERANDS
    RESTART_OPERANDS --> UPDATE_STATUS
    UPDATE_STATUS --> NODE_WATCHER
```

*Sources: [README.md:164-190](), diagrams provided by user*

## Configuration System

The system uses a YAML-based configuration format that defines vGPU device arrangements:

```mermaid
graph LR
    subgraph "Configuration Structure"
        YAML_CONFIG["YAML Configuration<br/>version: v1"]
        VGPU_CONFIGS["vgpu-configs section<br/>Named configurations"]
        DEVICE_SPECS["Device specifications<br/>devices, vgpu-devices"]
    end
    
    subgraph "API Types"
        V1_SPEC["v1.Spec<br/>Top-level structure"]
        VGPU_CONFIG_SPEC["VGPUConfigSpec<br/>GPU-specific config"]
        VGPU_CONFIG["VGPUConfig<br/>Device mapping"]
        MIG_CONFIG_SPEC["MigConfigSpec<br/>MIG conversion"]
    end
    
    subgraph "Device Selection"
        DEVICE_FILTER["DeviceFilter<br/>PCI ID matching"]
        DEVICE_LIST["Device indices<br/>[0], [1], etc."]
        ALL_DEVICES["all keyword<br/>All matching GPUs"]
    end
    
    YAML_CONFIG --> VGPU_CONFIGS
    VGPU_CONFIGS --> DEVICE_SPECS
    DEVICE_SPECS --> V1_SPEC
    V1_SPEC --> VGPU_CONFIG_SPEC
    VGPU_CONFIG_SPEC --> VGPU_CONFIG
    VGPU_CONFIG_SPEC --> MIG_CONFIG_SPEC
    
    DEVICE_SPECS --> DEVICE_FILTER
    DEVICE_SPECS --> DEVICE_LIST
    DEVICE_SPECS --> ALL_DEVICES
```

Example configuration structure from the repository:

| Configuration Name | Devices | vGPU Type | Count | Description |
|-------------------|---------|-----------|--------|-------------|
| `T4-1Q` | `all` | `T4-1Q` | 16 | Creates 16 T4-1Q devices on all GPUs |
| `T4-8Q` | `all` | `T4-8Q` | 2 | Creates 2 T4-8Q devices on all GPUs |
| `T4-small` | `[0], [1]` | `T4-1Q, T4-2Q` | 16, 8 | Custom mixed configuration |

*Sources: [README.md:18-75](), diagrams provided by user*

## Key Operational Workflows

### Configuration Application Workflow

```mermaid
sequenceDiagram
    participant CLI as "nvidia-vgpu-dm CLI"
    participant Parser as "Configuration Parser"
    participant Manager as "VGPUConfigManager"
    participant NVML as "NVIDIA vGPU Manager"
    participant GPU as "Physical GPU"
    
    CLI->>Parser: "ParseConfigFile(config.yaml)"
    Parser->>Parser: "Validate v1.Spec"
    Parser->>CLI: "Return parsed config"
    CLI->>Manager: "GetSelectedVGPUConfig(config-name)"
    Manager->>Manager: "Match devices by PCI ID"
    Manager->>NVML: "Enumerate existing vGPU devices"
    NVML->>Manager: "Current device state"
    Manager->>NVML: "Apply new vGPU configuration"
    NVML->>GPU: "Create vGPU devices"
    GPU->>NVML: "Device creation status"
    NVML->>Manager: "Configuration applied"
    Manager->>CLI: "Success/Failure status"
```

### Kubernetes Node Management Workflow

```mermaid
sequenceDiagram
    participant K8s as "Kubernetes API"
    participant Daemon as "nvidia-k8s-vgpu-dm"
    participant Operands as "GPU Operands"
    participant SystemD as "systemd Services"
    participant vGPU as "vGPU Manager"
    
    K8s->>Daemon: "Node label change event"
    Daemon->>Daemon: "Parse new configuration"
    Daemon->>Operands: "Shutdown device-plugin, validator"
    Operands->>Daemon: "Services stopped"
    Daemon->>vGPU: "Apply vGPU configuration"
    vGPU->>Daemon: "Configuration applied"
    Daemon->>SystemD: "Handle MIG reconfiguration"
    SystemD->>Daemon: "Services restarted"
    Daemon->>Operands: "Restart GPU services"
    Operands->>Daemon: "Services running"
    Daemon->>K8s: "Update node status labels"
```

*Sources: diagrams provided by user, [README.md:189-190]()*

## Technology Stack and Dependencies

The system is built using the following key technologies and dependencies:

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Core Language** | Go | Primary implementation language |
| **Configuration** | YAML | Declarative vGPU configuration format |
| **Container Runtime** | Docker/Podman | Containerized deployment |
| **Orchestration** | Kubernetes | Cluster-wide vGPU management |
| **GPU Interface** | NVIDIA vGPU Manager | Low-level vGPU device management |
| **GPU Library** | libnvidia-ml.so | NVIDIA Management Library |
| **Build System** | Make | Build automation and tooling |

### External Dependencies

```mermaid
graph TB
    subgraph "NVIDIA Dependencies"
        VGPU_MGR["NVIDIA vGPU Manager<br/>Hypervisor component"]
        NVML["NVIDIA ML Library<br/>libnvidia-ml.so"]
        GPU_DRIVER["NVIDIA GPU Driver<br/>Host driver stack"]
    end
    
    subgraph "Kubernetes Dependencies"
        K8S_API["Kubernetes API<br/>Node labels, ConfigMaps"]
        DEVICE_PLUGIN["NVIDIA Device Plugin<br/>GPU resource management"]
        GPU_OPERATOR["NVIDIA GPU Operator<br/>Lifecycle management"]
    end
    
    subgraph "System Dependencies"
        SYSTEMD["systemd<br/>Service management"]
        CONTAINER_RUNTIME["Container Runtime<br/>Docker/containerd"]
    end
    
    VGPU_MGR --> NVML
    NVML --> GPU_DRIVER
    K8S_API --> DEVICE_PLUGIN
    DEVICE_PLUGIN --> GPU_OPERATOR
    SYSTEMD --> CONTAINER_RUNTIME
```

*Sources: [README.md:118](), [LICENSE:1-203](), diagrams provided by user*

---

