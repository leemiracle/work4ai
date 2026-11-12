<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/vgpu-device-manager · page 2 Architecture & Core Components · fetched 2026-10-26 -->

# Architecture & Core Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [cmd/nvidia-k8s-vgpu-dm/main.go](cmd/nvidia-k8s-vgpu-dm/main.go)
- [cmd/nvidia-vgpu-dm/main.go](cmd/nvidia-vgpu-dm/main.go)

</details>



This document provides a detailed overview of the NVIDIA vGPU Device Manager's system architecture, core applications, and how the major components interact to manage virtual GPU devices in Kubernetes environments. For specific configuration formats and examples, see [Configuration Format & Examples](#3). For deployment and operational considerations, see [Deployment & Operations](#7).

## System Overview

The NVIDIA vGPU Device Manager consists of two primary applications that work together to provide declarative vGPU device management:

- **CLI Tool (`nvidia-vgpu-dm`)**: Standalone command-line interface for direct vGPU configuration management
- **Kubernetes Daemon (`nvidia-k8s-vgpu-dm`)**: Node-level daemon that integrates with Kubernetes to automatically manage vGPU configurations based on node labels

Both applications share a common configuration system and interact with the underlying NVIDIA driver stack to create and manage virtual GPU instances.

## Core System Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        CLI["nvidia-vgpu-dm CLI<br/>cmd/nvidia-vgpu-dm/main.go"]
        K8S_DAEMON["nvidia-k8s-vgpu-dm<br/>cmd/nvidia-k8s-vgpu-dm/main.go"]
    end
    
    subgraph "Command Layer"
        APPLY_CMD["apply.BuildCommand()<br/>cmd/nvidia-vgpu-dm/apply"]
        ASSERT_CMD["assert.BuildCommand()<br/>cmd/nvidia-vgpu-dm/assert"]
    end
    
    subgraph "Configuration Processing"
        PARSE_CONFIG["assert.ParseConfigFile()<br/>Configuration parsing"]
        GET_SELECTED["assert.GetSelectedVGPUConfig()<br/>Device selection"]
        SPEC_VALIDATION["v1.Spec validation<br/>api/spec/v1"]
    end
    
    subgraph "System Integration"
        NODE_WATCH["continuouslySyncVGPUConfigChanges()<br/>Node label monitoring"]
        GPU_SHUTDOWN["shutdownGPUOperands()<br/>Component coordination"]
        MIG_HANDLING["handleMIGConfiguration()<br/>MIG management"]
    end
    
    subgraph "Hardware Interaction"
        DRIVER_ROOT["driverRoot.getDriverLibraryPath()<br/>Driver discovery"]
        VGPU_APPLY["VGPUConfigManager<br/>nvlib interaction"]
        MIG_PARTED["mig-parted integration<br/>MIG partitioning"]
    end
    
    CLI --> APPLY_CMD
    CLI --> ASSERT_CMD
    K8S_DAEMON --> NODE_WATCH
    K8S_DAEMON --> GPU_SHUTDOWN
    
    APPLY_CMD --> PARSE_CONFIG
    ASSERT_CMD --> PARSE_CONFIG
    NODE_WATCH --> GET_SELECTED
    
    PARSE_CONFIG --> SPEC_VALIDATION
    GET_SELECTED --> SPEC_VALIDATION
    
    GPU_SHUTDOWN --> MIG_HANDLING
    MIG_HANDLING --> DRIVER_ROOT
    
    SPEC_VALIDATION --> VGPU_APPLY
    DRIVER_ROOT --> MIG_PARTED
```

**Sources:** [cmd/nvidia-vgpu-dm/main.go:53-56](), [cmd/nvidia-k8s-vgpu-dm/main.go:316-345](), [cmd/nvidia-k8s-vgpu-dm/main.go:460-499](), [cmd/nvidia-k8s-vgpu-dm/main.go:591-610]()

## Application Components

### CLI Tool Architecture

The `nvidia-vgpu-dm` CLI provides direct vGPU management capabilities through two primary commands:

```mermaid
graph LR
    subgraph "CLI Entry Point"
        MAIN["main.go<br/>Application setup"]
        FLAGS["Flags struct<br/>Debug configuration"]
    end
    
    subgraph "Command Handlers"
        APPLY["apply.BuildCommand()<br/>Configuration application"]
        ASSERT["assert.BuildCommand()<br/>Configuration validation"]
    end
    
    subgraph "Shared Processing"
        PARSE["ParseConfigFile()<br/>YAML parsing"]
        SELECT["GetSelectedVGPUConfig()<br/>Config selection"]
        VALIDATE["Config validation<br/>Schema checking"]
    end
    
    MAIN --> APPLY
    MAIN --> ASSERT
    MAIN --> FLAGS
    
    APPLY --> PARSE
    ASSERT --> PARSE
    
    PARSE --> SELECT
    SELECT --> VALIDATE
```

The CLI supports both file-based and stdin configuration input, with debug logging controlled through the `Flags.Debug` field at [cmd/nvidia-vgpu-dm/main.go:31-33]().

**Sources:** [cmd/nvidia-vgpu-dm/main.go:35-74]()

### Kubernetes Daemon Architecture

The `nvidia-k8s-vgpu-dm` daemon provides automated vGPU management in Kubernetes environments:

```mermaid
graph TB
    subgraph "Daemon Lifecycle"
        START["start() function<br/>Main orchestration"]
        VALIDATE_FLAGS["validateFlags()<br/>Configuration validation"]
        CLIENT_SETUP["kubernetes.NewForConfig()<br/>API client initialization"]
    end
    
    subgraph "Configuration Synchronization"
        SYNC_CONFIG["SyncableVGPUConfig<br/>Thread-safe config sync"]
        LIST_WATCH["cache.NewListWatchFromClient()<br/>Node watching"]
        INFORMER["cache.NewInformerWithOptions()<br/>Event handling"]
    end
    
    subgraph "Update Processing"
        UPDATE_CONFIG["updateConfig()<br/>Configuration application"]
        ASSERT_VALID["assertValidConfig()<br/>Validation check"]
        ASSERT_CURRENT["assertConfig()<br/>Current state check"]
    end
    
    subgraph "Component Management"
        GET_LABELS["getNodeStateLabels()<br/>Component state retrieval"]
        SHUTDOWN["shutdownGPUOperands()<br/>Component shutdown"]
        RESCHEDULE["rescheduleGPUOperands()<br/>Component restart"]
    end
    
    START --> VALIDATE_FLAGS
    START --> CLIENT_SETUP
    START --> SYNC_CONFIG
    
    SYNC_CONFIG --> LIST_WATCH
    LIST_WATCH --> INFORMER
    
    INFORMER --> UPDATE_CONFIG
    UPDATE_CONFIG --> ASSERT_VALID
    UPDATE_CONFIG --> ASSERT_CURRENT
    
    UPDATE_CONFIG --> GET_LABELS
    GET_LABELS --> SHUTDOWN
    SHUTDOWN --> RESCHEDULE
```

The daemon uses the `SyncableVGPUConfig` type at [cmd/nvidia-k8s-vgpu-dm/main.go:86-125]() to coordinate configuration changes between the node label watcher and the main processing loop.

**Sources:** [cmd/nvidia-k8s-vgpu-dm/main.go:258-314](), [cmd/nvidia-k8s-vgpu-dm/main.go:316-345](), [cmd/nvidia-k8s-vgpu-dm/main.go:347-395]()

## Configuration System Integration

Both applications share a common configuration processing pipeline:

```mermaid
graph TD
    subgraph "Input Sources"
        CONFIG_FILE["Configuration File<br/>-f flag parameter"]
        STDIN_INPUT["STDIN Input<br/>-f - parameter"]
        DEFAULT_CONFIG["defaultVGPUConfigFlag<br/>Fallback configuration"]
    end
    
    subgraph "Parsing Layer"
        PARSE_FUNC["assert.ParseConfigFile()<br/>YAML unmarshaling"]
        SPEC_STRUCT["v1.Spec<br/>Top-level structure"]
        VGPU_CONFIGS["VGPUConfigSpecSlice<br/>Device configurations"]
    end
    
    subgraph "Selection Logic"
        GET_SELECTED["assert.GetSelectedVGPUConfig()<br/>Config matching"]
        DEVICE_FILTER["Device filtering<br/>PCI ID matching"]
        VALIDATION["Schema validation<br/>Type checking"]
    end
    
    subgraph "Application"
        CLI_APPLY["CLI apply command<br/>Direct execution"]
        K8S_APPLY["applyConfig()<br/>Daemon execution"]
        EXEC_COMMAND["exec.Command(cliName)<br/>Process delegation"]
    end
    
    CONFIG_FILE --> PARSE_FUNC
    STDIN_INPUT --> PARSE_FUNC
    
    PARSE_FUNC --> SPEC_STRUCT
    SPEC_STRUCT --> VGPU_CONFIGS
    
    VGPU_CONFIGS --> GET_SELECTED
    GET_SELECTED --> DEVICE_FILTER
    DEVICE_FILTER --> VALIDATION
    
    VALIDATION --> CLI_APPLY
    VALIDATION --> K8S_APPLY
    K8S_APPLY --> EXEC_COMMAND
```

The configuration system supports device selection through multiple methods: `"all"` for all devices, numeric indices for specific devices, or PCI ID patterns for device matching.

**Sources:** [cmd/nvidia-k8s-vgpu-dm/main.go:397-408](), [cmd/nvidia-k8s-vgpu-dm/main.go:410-420](), [cmd/nvidia-k8s-vgpu-dm/main.go:422-433]()

## Kubernetes Integration Layer

The daemon manages integration with Kubernetes components through a sophisticated orchestration system:

```mermaid
graph TB
    subgraph "Node Label Management"
        VGPU_LABEL["nvidia.com/vgpu.config<br/>Target configuration"]
        STATE_LABEL["nvidia.com/vgpu.config.state<br/>Application status"]
        PLUGIN_LABEL["nvidia.com/gpu.deploy.sandbox-device-plugin<br/>Device plugin state"]
        VALIDATOR_LABEL["nvidia.com/gpu.deploy.sandbox-validator<br/>Validator state"]
    end
    
    subgraph "Component Coordination"
        WAIT_DELETION["waitForPodDeletion()<br/>Graceful shutdown"]
        MAYBE_SET_PAUSED["maybeSetPaused()<br/>State transition"]
        MAYBE_SET_TRUE["maybeSetTrue()<br/>State restoration"]
    end
    
    subgraph "Pod Management"
        DEVICE_PLUGIN_PODS["nvidia-sandbox-device-plugin-daemonset<br/>GPU device exposure"]
        VALIDATOR_PODS["nvidia-sandbox-validator<br/>Configuration validation"]
        FIELD_SELECTOR["spec.nodeName filter<br/>Node-specific targeting"]
    end
    
    VGPU_LABEL --> STATE_LABEL
    PLUGIN_LABEL --> MAYBE_SET_PAUSED
    VALIDATOR_LABEL --> MAYBE_SET_PAUSED
    
    MAYBE_SET_PAUSED --> WAIT_DELETION
    WAIT_DELETION --> DEVICE_PLUGIN_PODS
    WAIT_DELETION --> VALIDATOR_PODS
    
    DEVICE_PLUGIN_PODS --> FIELD_SELECTOR
    VALIDATOR_PODS --> FIELD_SELECTOR
    
    WAIT_DELETION --> MAYBE_SET_TRUE
```

The daemon coordinates component shutdowns by temporarily setting state labels to `"paused-for-vgpu-change"` and waiting for pod deletion with a 120-second timeout, as implemented in [cmd/nvidia-k8s-vgpu-dm/main.go:501-525]().

**Sources:** [cmd/nvidia-k8s-vgpu-dm/main.go:48-60](), [cmd/nvidia-k8s-vgpu-dm/main.go:460-499](), [cmd/nvidia-k8s-vgpu-dm/main.go:527-544](), [cmd/nvidia-k8s-vgpu-dm/main.go:546-558]()

## MIG Configuration Handling

The system includes specialized handling for Multi-Instance GPU (MIG) configurations:

```mermaid
graph LR
    subgraph "MIG Processing Pipeline"
        DETERMINE["determineMIGConfig()<br/>Configuration analysis"]
        CONVERT["convertToMIGConfig()<br/>Format conversion"]
        SAVE_TEMP["saveMIGConfigToTempFile()<br/>Temporary storage"]
        UPDATE_MIG["updateMIGConfig()<br/>Application"]
    end
    
    subgraph "External Integration"
        MIG_PARTED["migpartedv1.Spec<br/>mig-parted configuration"]
        GPU_CLIENTS["parseGPUClientsFile()<br/>Service coordination"]
        RECONFIG_OPTIONS["reconfigureMIGOptions<br/>Operation parameters"]
    end
    
    subgraph "System Services"
        SYSTEMD_SERVICES["SystemdServices<br/>Host service management"]
        KUBELET_SERVICE["HostKubeletService<br/>kubelet coordination"]
        MIG_MANAGER["HostMIGManagerStateFile<br/>MIG manager state"]
    end
    
    DETERMINE --> CONVERT
    CONVERT --> MIG_PARTED
    CONVERT --> SAVE_TEMP
    
    SAVE_TEMP --> UPDATE_MIG
    UPDATE_MIG --> GPU_CLIENTS
    GPU_CLIENTS --> RECONFIG_OPTIONS
    
    RECONFIG_OPTIONS --> SYSTEMD_SERVICES
    RECONFIG_OPTIONS --> KUBELET_SERVICE
    RECONFIG_OPTIONS --> MIG_MANAGER
```

The MIG handling converts vGPU configurations to `migpartedv1.Spec` format and coordinates with host systemd services. The `GPUClients` struct at [cmd/nvidia-k8s-vgpu-dm/main.go:81-84]() defines which systemd services need coordination during MIG reconfiguration.

**Sources:** [cmd/nvidia-k8s-vgpu-dm/main.go:591-610](), [cmd/nvidia-k8s-vgpu-dm/main.go:612-632](), [cmd/nvidia-k8s-vgpu-dm/main.go:634-646](), [cmd/nvidia-k8s-vgpu-dm/main.go:667-693](), [cmd/nvidia-k8s-vgpu-dm/main.go:695-715]()

---

