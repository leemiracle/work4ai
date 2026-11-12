<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/vgpu-device-manager · page 7 Deployment & Operations · fetched 2026-10-26 -->

# Deployment & Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [cmd/nvidia-k8s-vgpu-dm/main.go](cmd/nvidia-k8s-vgpu-dm/main.go)
- [deployments/container/Dockerfile.ubi9](deployments/container/Dockerfile.ubi9)

</details>



This document covers deployment strategies, operational procedures, and production considerations for running the NVIDIA vGPU Device Manager in Kubernetes environments. It focuses on container-based deployments, configuration management, and day-to-day operational workflows.

For information about the configuration file format and vGPU device specifications, see [Configuration Format & Examples](#3). For details about the CLI tools and core components, see [Architecture & Core Components](#2).

## Deployment Methods

The NVIDIA vGPU Device Manager supports two primary deployment models: integration with the NVIDIA GPU Operator for production use, and standalone DaemonSet deployment for development and testing.

### GPU Operator Integration

The primary production deployment method is through the NVIDIA GPU Operator, where the vGPU Device Manager runs as a managed component within the GPU stack.

```mermaid
graph TB
    subgraph "NVIDIA GPU Operator"
        GPU_OP["GPU Operator Controller"]
        NODE_STATUS["Node Feature Discovery"]
        
        subgraph "GPU Stack DaemonSets"
            DRIVER_DS["NVIDIA Driver DaemonSet"]
            TOOLKIT_DS["Container Toolkit DaemonSet"]
            DEVICE_PLUGIN_DS["Device Plugin DaemonSet"]
            VGPU_DM_DS["vGPU Device Manager DaemonSet"]
            VALIDATOR_DS["GPU Feature Discovery DaemonSet"]
        end
    end
    
    subgraph "Kubernetes Node"
        KUBELET["kubelet"]
        SYSTEMD["systemd services"]
        NVIDIA_DRIVER["NVIDIA Driver"]
        PHYSICAL_GPUS["Physical GPUs"]
    end
    
    GPU_OP --> VGPU_DM_DS
    VGPU_DM_DS --> KUBELET
    VGPU_DM_DS --> SYSTEMD
    VGPU_DM_DS --> NVIDIA_DRIVER
    NVIDIA_DRIVER --> PHYSICAL_GPUS
    
    VGPU_DM_DS -.-> DEVICE_PLUGIN_DS
    VGPU_DM_DS -.-> VALIDATOR_DS
```

**GPU Operator Managed Deployment**

Sources: [README.md:166-168]()

### Standalone DaemonSet Deployment

For development and testing purposes, the vGPU Device Manager can be deployed as a standalone DaemonSet outside of the GPU Operator.

```mermaid
graph TB
    subgraph "Standalone Deployment"
        CONFIG_MAP["vgpu-devices-config ConfigMap"]
        VGPU_DAEMONSET["nvidia-vgpu-device-manager DaemonSet"]
        
        subgraph "Container Spec"
            VGPU_CONTAINER["vGPU Manager Container"]
            VOLUME_MOUNTS["Volume Mounts:<br/>- /dev<br/>- /sys<br/>- /host<br/>- config volume"]
        end
    end
    
    subgraph "Node Resources"
        NODE_LABELS["Node Labels:<br/>nvidia.com/vgpu.config<br/>nvidia.com/vgpu.config.state"]
        HOST_FILESYSTEM["Host Filesystem"]
        NVIDIA_LIBS["NVIDIA Libraries"]
    end
    
    CONFIG_MAP --> VGPU_CONTAINER
    VGPU_DAEMONSET --> VGPU_CONTAINER
    VGPU_CONTAINER --> VOLUME_MOUNTS
    VOLUME_MOUNTS --> HOST_FILESYSTEM
    VOLUME_MOUNTS --> NVIDIA_LIBS
    VGPU_CONTAINER --> NODE_LABELS
```

**Standalone Development Deployment**

The deployment process involves creating a ConfigMap with vGPU configuration and deploying the DaemonSet:

```bash
# Create configuration ConfigMap
kubectl create configmap vgpu-devices-config --from-file=config.yaml

# Deploy vGPU Device Manager DaemonSet  
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/vgpu-device-manager/main/examples/nvidia-vgpu-device-manager-example.yaml
```

Sources: [README.md:171-189]()

## Container Image Architecture

The vGPU Device Manager container includes both CLI and daemon binaries along with required dependencies.

```mermaid
graph TB
    subgraph "Container Build Process"
        BUILD_STAGE["Build Stage:<br/>nvcr.io/nvidia/cuda:13.0.0-base-ubi9"]
        MIG_STAGE["MIG Manager Stage:<br/>k8s-mig-manager:v0.12.3-ubi9"]
        FINAL_STAGE["Final Stage:<br/>nvcr.io/nvidia/distroless/go:v3.1.11-dev"]
    end
    
    subgraph "Binary Artifacts"
        VGPU_CLI["/usr/bin/nvidia-vgpu-dm"]
        VGPU_DAEMON["/usr/bin/nvidia-k8s-vgpu-dm"]
        MIG_PARTED["/usr/bin/nvidia-mig-parted"]
    end
    
    subgraph "Runtime Configuration"
        ENTRYPOINT["ENTRYPOINT: nvidia-k8s-vgpu-dm"]
        ENV_VARS["NVIDIA_VISIBLE_DEVICES=void"]
        USER_CONTEXT["USER 0:0"]
    end
    
    BUILD_STAGE --> VGPU_CLI
    BUILD_STAGE --> VGPU_DAEMON
    MIG_STAGE --> MIG_PARTED
    
    VGPU_CLI --> FINAL_STAGE
    VGPU_DAEMON --> FINAL_STAGE
    MIG_PARTED --> FINAL_STAGE
    
    FINAL_STAGE --> ENTRYPOINT
    FINAL_STAGE --> ENV_VARS
    FINAL_STAGE --> USER_CONTEXT
```

**Multi-stage Container Build**

Sources: [deployments/container/Dockerfile.ubi9:15-61]()

## Configuration Management

The vGPU Device Manager uses Kubernetes ConfigMaps to manage vGPU device configurations and supports dynamic configuration updates through node labeling.

### ConfigMap-Based Configuration

```mermaid
graph LR
    subgraph "Configuration Sources"
        CONFIG_YAML["config.yaml<br/>vGPU Configurations"]
        EXAMPLES["examples/config-t4.yaml<br/>examples/config-example.yaml"]
    end
    
    subgraph "Kubernetes Resources"
        CONFIG_MAP["ConfigMap:<br/>vgpu-devices-config"]
        VOLUME["Volume Mount:<br/>/etc/vgpu-devices"]
    end
    
    subgraph "Runtime Processing"
        CONFIG_FILE_FLAG["--config-file flag"]
        PARSE_CONFIG["ParseConfigFile()"]
        SELECT_CONFIG["GetSelectedVGPUConfig()"]
    end
    
    CONFIG_YAML --> CONFIG_MAP
    EXAMPLES --> CONFIG_MAP
    CONFIG_MAP --> VOLUME
    VOLUME --> CONFIG_FILE_FLAG
    CONFIG_FILE_FLAG --> PARSE_CONFIG
    PARSE_CONFIG --> SELECT_CONFIG
```

**Configuration Flow from YAML to Runtime**

Sources: [cmd/nvidia-k8s-vgpu-dm/main.go:158-165](), [README.md:171-181]()

### Node Label Management

The daemon manages configuration state through specific Kubernetes node labels:

| Label | Purpose | Values |
|-------|---------|--------|
| `nvidia.com/vgpu.config` | Specifies desired vGPU configuration | Configuration name from ConfigMap |
| `nvidia.com/vgpu.config.state` | Indicates configuration application status | `success`, `failed`, `pending` |
| `nvidia.com/gpu.deploy.sandbox-device-plugin` | Controls device plugin deployment | `true`, `false`, `paused-for-vgpu-change` |
| `nvidia.com/gpu.deploy.sandbox-validator` | Controls validator deployment | `true`, `false`, `paused-for-vgpu-change` |

Sources: [cmd/nvidia-k8s-vgpu-dm/main.go:51-54]()

## Operational Workflow

The vGPU Device Manager follows a specific operational sequence when applying configuration changes.

```mermaid
graph TD
    WATCH_LABELS["Watch Node Labels<br/>continuouslySyncVGPUConfigChanges()"]
    LABEL_CHANGE["Label Change Detected<br/>nvidia.com/vgpu.config"]
    VALIDATE_CONFIG["Validate Configuration<br/>assertValidConfig()"]
    CHECK_CURRENT["Check Current State<br/>assertConfig()"]
    
    subgraph "Configuration Application"
        SET_PENDING["Set State: pending<br/>vGPUConfigStateLabel"]
        SHUTDOWN_OPERANDS["Shutdown GPU Operands<br/>shutdownGPUOperands()"]
        HANDLE_MIG["Handle MIG Configuration<br/>handleMIGConfiguration()"]
        APPLY_VGPU["Apply vGPU Config<br/>applyConfig()"]
        RESTART_OPERANDS["Restart GPU Operands<br/>rescheduleGPUOperands()"]
        UPDATE_STATUS["Update Status Label<br/>success/failed"]
    end
    
    WATCH_LABELS --> LABEL_CHANGE
    LABEL_CHANGE --> VALIDATE_CONFIG
    VALIDATE_CONFIG --> CHECK_CURRENT
    CHECK_CURRENT -->|Config Already Applied| WATCH_LABELS
    CHECK_CURRENT -->|Config Change Needed| SET_PENDING
    
    SET_PENDING --> SHUTDOWN_OPERANDS
    SHUTDOWN_OPERANDS --> HANDLE_MIG
    HANDLE_MIG --> APPLY_VGPU
    APPLY_VGPU --> RESTART_OPERANDS
    RESTART_OPERANDS --> UPDATE_STATUS
    UPDATE_STATUS --> WATCH_LABELS
```

**vGPU Configuration Application Workflow**

Sources: [cmd/nvidia-k8s-vgpu-dm/main.go:347-395]()

### GPU Operand Lifecycle Management

The daemon coordinates with other GPU stack components during configuration changes:

```mermaid
graph TB
    subgraph "Shutdown Phase"
        GET_LABELS["getNodeStateLabels()<br/>Read current operand state"]
        SET_PAUSED["maybeSetPaused()<br/>Mark as paused-for-vgpu-change"]
        UPDATE_NODE["Update Node Labels<br/>Trigger operand shutdown"]
        WAIT_DELETION["waitForPodDeletion()<br/>120s timeout"]
    end
    
    subgraph "Configuration Phase"
        MIG_RECONFIG["MIG Reconfiguration<br/>reconfigureMIG()"]
        VGPU_APPLY["vGPU Application<br/>nvidia-vgpu-dm apply"]
    end
    
    subgraph "Restart Phase"
        SET_TRUE["maybeSetTrue()<br/>Restore operand state"]
        RESCHEDULE["Update Node Labels<br/>Trigger operand restart"]
    end
    
    GET_LABELS --> SET_PAUSED
    SET_PAUSED --> UPDATE_NODE
    UPDATE_NODE --> WAIT_DELETION
    WAIT_DELETION --> MIG_RECONFIG
    MIG_RECONFIG --> VGPU_APPLY
    VGPU_APPLY --> SET_TRUE
    SET_TRUE --> RESCHEDULE
```

**GPU Stack Component Coordination**

Sources: [cmd/nvidia-k8s-vgpu-dm/main.go:460-544]()

## Command-Line Interface Integration

The Kubernetes daemon internally uses the CLI tools for configuration operations:

| Operation | CLI Command | Purpose |
|-----------|-------------|---------|
| Configuration Validation | `nvidia-vgpu-dm assert --valid-config -f config.yaml -c T4-1Q` | Verify config exists in file |
| State Assertion | `nvidia-vgpu-dm assert -f config.yaml -c T4-1Q` | Check if config is currently applied |
| Configuration Application | `nvidia-vgpu-dm -d apply -f config.yaml -c T4-1Q` | Apply vGPU configuration to GPUs |

Sources: [cmd/nvidia-k8s-vgpu-dm/main.go:397-433]()

## MIG Configuration Handling

For GPUs supporting Multi-Instance GPU (MIG), the daemon performs additional configuration steps:

```mermaid
graph TB
    subgraph "MIG Configuration Process"
        DETERMINE_MIG["determineMIGConfig()<br/>Parse vGPU config for MIG requirements"]
        CONVERT_CONFIG["convertToMIGConfig()<br/>Transform to mig-parted format"]
        SAVE_TEMP["saveMIGConfigToTempFile()<br/>Create temporary YAML"]
        UPDATE_MIG["updateMIGConfig()<br/>Apply via mig-parted"]
    end
    
    subgraph "Host System Integration"
        PARSE_CLIENTS["parseGPUClientsFile()<br/>Read GPU client services"]
        SHUTDOWN_SERVICES["Shutdown systemd services"]
        MIG_PARTED["nvidia-mig-parted execution"]
        RESTART_SERVICES["Restart systemd services"]
    end
    
    subgraph "Configuration Options"
        WITH_REBOOT["--with-reboot flag<br/>Node reboot on failure"]
        GPU_CLIENTS["--gpu-clients-file<br/>systemd services list"]
        KUBELET_SERVICE["--host-kubelet-systemd-service<br/>kubelet service name"]
    end
    
    DETERMINE_MIG --> CONVERT_CONFIG
    CONVERT_CONFIG --> SAVE_TEMP
    SAVE_TEMP --> UPDATE_MIG
    UPDATE_MIG --> PARSE_CLIENTS
    PARSE_CLIENTS --> SHUTDOWN_SERVICES
    SHUTDOWN_SERVICES --> MIG_PARTED
    MIG_PARTED --> RESTART_SERVICES
    
    WITH_REBOOT -.-> UPDATE_MIG
    GPU_CLIENTS -.-> PARSE_CLIENTS
    KUBELET_SERVICE -.-> SHUTDOWN_SERVICES
```

**MIG Configuration and Host Service Management**

Sources: [cmd/nvidia-k8s-vgpu-dm/main.go:591-715]()

## Monitoring and Troubleshooting

### Node Label Status Monitoring

Monitor vGPU configuration status through node labels:

```bash
# Check current vGPU configuration
kubectl get nodes -l nvidia.com/vgpu.config -o custom-columns=NAME:.metadata.name,VGPU_CONFIG:.metadata.labels.nvidia\.com/vgpu\.config,STATE:.metadata.labels.nvidia\.com/vgpu\.config\.state

# Monitor configuration changes
kubectl get nodes <node-name> -w -o jsonpath='{.metadata.labels.nvidia\.com/vgpu\.config\.state}'
```

### Common Operational States

| State | Description | Action Required |
|-------|-------------|-----------------|
| `success` | Configuration successfully applied | None |
| `failed` | Configuration application failed | Check daemon logs and vGPU configuration |
| `pending` | Configuration change in progress | Wait for completion |
| `paused-for-vgpu-change` | GPU operands temporarily paused | Normal during configuration updates |

### Daemon Configuration Flags

Key operational flags for the `nvidia-k8s-vgpu-dm` daemon:

| Flag | Environment Variable | Default | Purpose |
|------|---------------------|---------|---------|
| `--node-name` | `NODE_NAME` | Required | Target node for configuration |
| `--namespace` | `NAMESPACE` | Required | GPU operand namespace |
| `--config-file` | `CONFIG_FILE` | Required | vGPU configuration file path |
| `--default-vgpu-config` | `DEFAULT_VGPU_CONFIG` | Required | Fallback configuration name |
| `--with-reboot` | `WITH_REBOOT` | `false` | Reboot on MIG failure |
| `--host-root-mount` | `HOST_ROOT_MOUNT` | `/host` | Host filesystem mount point |

Sources: [cmd/nvidia-k8s-vgpu-dm/main.go:134-230]()

## Prerequisites and Dependencies

### Runtime Requirements

- NVIDIA vGPU Manager installed on host system
- Container runtime with GPU support (containerd/docker)
- Kubernetes cluster with node labeling capabilities
- Sufficient privileges for systemd service management (when using MIG)

### Container Dependencies

- Base CUDA runtime environment
- `nvidia-mig-parted` binary for MIG operations
- Go runtime for daemon execution
- Host filesystem access for driver interaction

Sources: [README.md:116-119](), [deployments/container/Dockerfile.ubi9:41-49]()

This deployment and operations guide provides the foundation for running the NVIDIA vGPU Device Manager in production Kubernetes environments, with proper monitoring and troubleshooting capabilities for reliable vGPU configuration management.