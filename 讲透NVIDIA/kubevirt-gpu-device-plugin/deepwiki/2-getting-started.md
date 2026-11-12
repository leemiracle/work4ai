<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/kubevirt-gpu-device-plugin · page 2 Getting Started · fetched 2026-10-26 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [examples/kubevirt-featuregate-cm.yaml](examples/kubevirt-featuregate-cm.yaml)
- [manifests/nvidia-kubevirt-gpu-device-plugin.yaml](manifests/nvidia-kubevirt-gpu-device-plugin.yaml)

</details>



This page provides an overview of the prerequisites and installation process for the NVIDIA KubeVirt GPU Device Plugin. It introduces the setup workflow and key deployment components. For detailed step-by-step instructions on host preparation, see [Prerequisites and Host Setup](#2.1). For deployment procedures, see [Installing the Device Plugin](#2.2).

## Purpose and Scope

The NVIDIA KubeVirt GPU Device Plugin enables GPU and vGPU passthrough to KubeVirt virtual machines running in a Kubernetes cluster. This Getting Started guide covers the complete setup process from host preparation through deployment verification. 

This page focuses on installation and initial configuration. For architectural details about how the device plugin works internally, see [Architecture](#3). For build and development workflows, see [Development Guide](#5).

## Installation Overview

Setting up the device plugin requires preparation at three layers:

| Layer | Configuration Required | Purpose |
|-------|----------------------|---------|
| **Host System** | IOMMU enablement, kernel driver binding | Enable hardware virtualization and device isolation |
| **KubeVirt** | Feature gates, permitted device allowlisting | Allow GPU/vGPU attachment to VMs |
| **Device Plugin** | DaemonSet deployment | Discover and advertise GPU resources to Kubernetes |

The installation follows a sequential dependency chain where each layer must be configured before proceeding to the next.

## Setup Workflow

The following diagram illustrates the complete setup workflow from bare-metal host configuration through device plugin deployment:

```mermaid
flowchart TD
    START["Fresh Kubernetes Node<br/>with NVIDIA GPU Hardware"]
    
    subgraph PREP["Host Preparation (Page 2.1)"]
        IOMMU["Enable IOMMU in GRUB<br/>/etc/default/grub"]
        NOUVEAU["Blacklist nouveau Driver<br/>modprobe.blacklist=nouveau"]
        
        CHOICE{"GPU Mode?"}
        
        subgraph PASSTHROUGH["GPU Passthrough Path"]
            VFIO_IDS["Determine PCI IDs<br/>lspci -nn | grep nvidia"]
            VFIO_CONF["Configure VFIO-PCI<br/>/etc/modprobe.d/vfio.conf"]
            VFIO_LOAD["Load vfio-pci Module<br/>/etc/modules-load.d/vfio-pci.conf"]
            VFIO_VERIFY["Verify Driver Binding<br/>lspci -nnk -d 10de:"]
        end
        
        subgraph VGPU["vGPU Path"]
            VGPU_MGR["Install NVIDIA vGPU Manager"]
            MDEV_TYPE["Select mdev_supported_types<br/>/sys/bus/pci/devices/.../mdev_supported_types/"]
            MDEV_CREATE["Create mdev Instance<br/>echo uuid > nvidia-*/create"]
            MDEV_VERIFY["Verify mdev Device<br/>/sys/bus/mdev/devices/"]
        end
    end
    
    subgraph KUBEVIRT["KubeVirt Configuration (Page 2.2)"]
        KV_CR["Update KubeVirt CR<br/>spec.configuration.permittedHostDevices"]
        PCI_LIST["Configure pciHostDevices<br/>pciVendorSelector"]
        MDEV_LIST["Configure mediatedDevices<br/>mdevNameSelector"]
        GPU_GATE["Enable GPU Feature Gate<br/>featureGates: [GPU]"]
    end
    
    subgraph DEPLOY["Device Plugin Deployment (Page 2.2)"]
        MANIFEST["Apply DaemonSet<br/>nvidia-kubevirt-gpu-device-plugin.yaml"]
        DS_CREATE["DaemonSet Creates Pods<br/>kube-system namespace"]
        DISCOVER["Device Plugin Discovers GPUs<br/>registers with Kubelet"]
        ADVERTISE["Resources Advertised<br/>nvidia.com/GPU_TYPE"]
    end
    
    VERIFY["Verify Installation<br/>kubectl describe node"]
    
    START --> IOMMU
    IOMMU --> NOUVEAU
    NOUVEAU --> CHOICE
    
    CHOICE -->|"Passthrough"| VFIO_IDS
    VFIO_IDS --> VFIO_CONF
    VFIO_CONF --> VFIO_LOAD
    VFIO_LOAD --> VFIO_VERIFY
    
    CHOICE -->|"vGPU"| VGPU_MGR
    VGPU_MGR --> MDEV_TYPE
    MDEV_TYPE --> MDEV_CREATE
    MDEV_CREATE --> MDEV_VERIFY
    
    VFIO_VERIFY --> KV_CR
    MDEV_VERIFY --> KV_CR
    
    KV_CR --> PCI_LIST
    KV_CR --> MDEV_LIST
    PCI_LIST --> GPU_GATE
    MDEV_LIST --> GPU_GATE
    
    GPU_GATE --> MANIFEST
    MANIFEST --> DS_CREATE
    DS_CREATE --> DISCOVER
    DISCOVER --> ADVERTISE
    
    ADVERTISE --> VERIFY
```

**Sources**: [README.md:27-173](), [manifests/nvidia-kubevirt-gpu-device-plugin.yaml:1-40](), [examples/kubevirt-featuregate-cm.yaml:1-22]()

## Component Deployment Architecture

The following diagram maps the deployed Kubernetes resources to their source files and shows how they interact at runtime:

```mermaid
graph TB
    subgraph FILES["Configuration Files"]
        MANIFEST["manifests/nvidia-kubevirt-gpu-device-plugin.yaml<br/>DaemonSet Definition"]
        EXAMPLE["examples/kubevirt-featuregate-cm.yaml<br/>KubeVirt CR Example"]
    end
    
    subgraph CLUSTER["Kubernetes Cluster Resources"]
        subgraph NS_SYSTEM["Namespace: kube-system"]
            DS["DaemonSet<br/>nvidia-kubevirt-gpu-dp-daemonset"]
            
            subgraph NODE1["GPU Worker Node 1"]
                POD1["Pod<br/>nvidia-kubevirt-gpu-dp-ds-xxxxx"]
                CTR1["Container<br/>nvidia-kubevirt-gpu-dp-ctr<br/>image: nvcr.io/nvidia/kubevirt-gpu-device-plugin:v1.4.0"]
            end
            
            subgraph NODE2["GPU Worker Node 2"]
                POD2["Pod<br/>nvidia-kubevirt-gpu-dp-ds-yyyyy"]
                CTR2["Container<br/>nvidia-kubevirt-gpu-dp-ctr"]
            end
        end
        
        subgraph NS_KUBEVIRT["Namespace: kubevirt"]
            KVCR["KubeVirt CR<br/>kind: KubeVirt<br/>spec.configuration.permittedHostDevices"]
            KVOP["KubeVirt Operator<br/>Manages VM Infrastructure"]
        end
    end
    
    subgraph HOST["Host System Configuration"]
        VFIO_DEV["/dev/vfio/*<br/>VFIO Device Files"]
        KUBELET_SOCK["/var/lib/kubelet/device-plugins<br/>Device Plugin Socket Directory"]
        SYS_PCI["/sys/bus/pci/devices/<br/>PCI Device Information"]
        SYS_MDEV["/sys/bus/mdev/devices/<br/>mdev Device Information"]
    end
    
    MANIFEST -.->|"kubectl apply"| DS
    EXAMPLE -.->|"kubectl apply"| KVCR
    
    DS -->|"creates"| POD1
    DS -->|"creates"| POD2
    POD1 -->|"runs"| CTR1
    POD2 -->|"runs"| CTR2
    
    CTR1 -->|"volumeMount: /dev/vfio"| VFIO_DEV
    CTR1 -->|"volumeMount: /var/lib/kubelet/device-plugins"| KUBELET_SOCK
    CTR1 -->|"reads"| SYS_PCI
    CTR1 -->|"reads"| SYS_MDEV
    
    CTR2 -->|"volumeMount: /dev/vfio"| VFIO_DEV
    CTR2 -->|"volumeMount: /var/lib/kubelet/device-plugins"| KUBELET_SOCK
    
    KVCR -->|"configures"| KVOP
    KVOP -.->|"permits GPU attachment"| POD1
    KVOP -.->|"permits GPU attachment"| POD2
```

**Sources**: [manifests/nvidia-kubevirt-gpu-device-plugin.yaml:1-40](), [examples/kubevirt-featuregate-cm.yaml:1-22]()

## Key Requirements

Before proceeding with installation, ensure the following prerequisites are met:

### Software Versions

| Component | Minimum Version | Notes |
|-----------|----------------|-------|
| Kubernetes | v1.11 | Required for Device Plugin API v1beta1 |
| KubeVirt | v0.36.0 | Earlier versions require device plugin v1.0.1 |
| Linux Kernel | IOMMU-capable | Check with `dmesg \| grep -E "DMAR\|IOMMU"` |

**Sources**: [README.md:22-24]()

### Hardware Prerequisites

- NVIDIA GPU hardware with either:
  - VFIO-PCI driver binding support (for GPU passthrough), or
  - NVIDIA vGPU Manager compatibility (for vGPU mode)
- IOMMU support in BIOS/UEFI and CPU (Intel VT-d or AMD-Vi)

**Sources**: [README.md:21-22]()

### Configuration Files Reference

The installation process uses the following key configuration files:

| File Path | Purpose | Applied With |
|-----------|---------|--------------|
| `manifests/nvidia-kubevirt-gpu-device-plugin.yaml` | DaemonSet deployment specification | `kubectl apply -f` |
| `examples/kubevirt-featuregate-cm.yaml` | KubeVirt CR with GPU feature gate and permitted devices | `kubectl apply -f` |
| `/etc/default/grub` | Host GRUB configuration for IOMMU | Host-level edit + `grub2-mkconfig` |
| `/etc/modprobe.d/vfio.conf` | VFIO-PCI driver binding configuration | Host-level edit |
| `/etc/modules-load.d/vfio-pci.conf` | VFIO-PCI module auto-load | Host-level edit |

**Sources**: [README.md:37-96](), [manifests/nvidia-kubevirt-gpu-device-plugin.yaml:1-40](), [examples/kubevirt-featuregate-cm.yaml:1-22]()

## DaemonSet Deployment Model

The device plugin uses a DaemonSet deployment pattern to ensure GPU resource discovery on every GPU-capable node:

```mermaid
graph LR
    subgraph DAEMONSET["DaemonSet: nvidia-kubevirt-gpu-dp-daemonset"]
        SELECTOR["spec.selector.matchLabels<br/>name: nvidia-kubevirt-gpu-dp-ds"]
        TEMPLATE["spec.template"]
    end
    
    subgraph POD_SPEC["Pod Template Specification"]
        PRIORITY["priorityClassName:<br/>system-node-critical"]
        TOLERATIONS["tolerations:<br/>- key: CriticalAddonsOnly"]
        
        subgraph CONTAINER["Container: nvidia-kubevirt-gpu-dp-ctr"]
            IMAGE["image:<br/>nvcr.io/nvidia/kubevirt-gpu-device-plugin:v1.4.0"]
            SECURITY["securityContext:<br/>allowPrivilegeEscalation: false<br/>capabilities.drop: [ALL]"]
        end
        
        subgraph VOLUMES["Volume Mounts"]
            VOL_DP["device-plugin<br/>hostPath: /var/lib/kubelet/device-plugins"]
            VOL_VFIO["vfio<br/>hostPath: /dev/vfio"]
        end
    end
    
    DAEMONSET --> POD_SPEC
    POD_SPEC --> PRIORITY
    POD_SPEC --> TOLERATIONS
    POD_SPEC --> CONTAINER
    POD_SPEC --> VOLUMES
    
    CONTAINER --> IMAGE
    CONTAINER --> SECURITY
    CONTAINER -.->|"mounts"| VOL_DP
    CONTAINER -.->|"mounts"| VOL_VFIO
```

**Sources**: [manifests/nvidia-kubevirt-gpu-device-plugin.yaml:1-40]()

### DaemonSet Configuration Highlights

The DaemonSet manifest [manifests/nvidia-kubevirt-gpu-device-plugin.yaml:1-40]() includes several critical configurations:

- **System Priority**: [manifests/nvidia-kubevirt-gpu-device-plugin.yaml:15]() sets `priorityClassName: system-node-critical`, ensuring the device plugin pods are not evicted during resource pressure.

- **Critical Add-on Toleration**: [manifests/nvidia-kubevirt-gpu-device-plugin.yaml:16-20]() allows pods to run even when nodes are in maintenance mode.

- **Security Hardening**: [manifests/nvidia-kubevirt-gpu-device-plugin.yaml:24-27]() drops all capabilities and disables privilege escalation, following least-privilege principles.

- **Required Host Access**: 
  - [manifests/nvidia-kubevirt-gpu-device-plugin.yaml:28-30]() mounts `/var/lib/kubelet/device-plugins` for gRPC socket communication with kubelet.
  - [manifests/nvidia-kubevirt-gpu-device-plugin.yaml:31-32]() mounts `/dev/vfio` for VFIO device file access.

**Sources**: [manifests/nvidia-kubevirt-gpu-device-plugin.yaml:1-40]()

## KubeVirt Integration Requirements

KubeVirt must be configured to permit GPU devices before VMs can use them. The configuration uses the KubeVirt Custom Resource:

```mermaid
graph TB
    subgraph KVCR["KubeVirt CR (examples/kubevirt-featuregate-cm.yaml)"]
        METADATA["apiVersion: kubevirt.io/v1alpha3<br/>kind: KubeVirt<br/>metadata.name: kubevirt<br/>metadata.namespace: kubevirt"]
        
        subgraph CONFIG["spec.configuration"]
            subgraph PERMITTED["permittedHostDevices"]
                PCI["pciHostDevices[]<br/>Physical GPU Passthrough"]
                MDEV["mediatedDevices[]<br/>vGPU Support"]
            end
            
            subgraph FEATURES["developerConfiguration.featureGates"]
                GPU_GATE["- GPU"]
            end
        end
    end
    
    subgraph PCI_CONFIG["pciHostDevices Entry"]
        PCI_VENDOR["pciVendorSelector: '10DE:1EB8'<br/>Vendor:Device ID"]
        PCI_RESOURCE["resourceName: 'nvidia.com/TU104GL_Tesla_T4'<br/>Kubernetes Resource Name"]
        PCI_EXTERNAL["externalResourceProvider: true<br/>Managed by Device Plugin"]
    end
    
    subgraph MDEV_CONFIG["mediatedDevices Entry"]
        MDEV_SELECTOR["mdevNameSelector: 'GRID T4-1Q'<br/>mdev Type Name"]
        MDEV_RESOURCE["resourceName: 'nvidia.com/GRID_T4-1Q'<br/>Kubernetes Resource Name"]
    end
    
    KVCR --> METADATA
    KVCR --> CONFIG
    CONFIG --> PERMITTED
    CONFIG --> FEATURES
    
    PERMITTED --> PCI
    PERMITTED --> MDEV
    
    PCI -.->|"example configuration"| PCI_CONFIG
    MDEV -.->|"example configuration"| MDEV_CONFIG
    
    PCI_CONFIG --> PCI_VENDOR
    PCI_CONFIG --> PCI_RESOURCE
    PCI_CONFIG --> PCI_EXTERNAL
    
    MDEV_CONFIG --> MDEV_SELECTOR
    MDEV_CONFIG --> MDEV_RESOURCE
```

**Sources**: [examples/kubevirt-featuregate-cm.yaml:1-22](), [README.md:31-32]()

### Permitted Device Configuration

The KubeVirt CR [examples/kubevirt-featuregate-cm.yaml:1-22]() demonstrates two types of device permissions:

**Physical GPU (Passthrough)**:
- [examples/kubevirt-featuregate-cm.yaml:11-15]() configures PCI device passthrough
- `pciVendorSelector: "10DE:1EB8"` specifies the NVIDIA vendor ID (10DE) and Tesla T4 device ID (1EB8)
- `resourceName` must match the resource name advertised by the device plugin
- `externalResourceProvider: true` indicates the device plugin manages this resource

**Virtual GPU (mdev)**:
- [examples/kubevirt-featuregate-cm.yaml:16-18]() configures mediated device support
- `mdevNameSelector: "GRID T4-1Q"` specifies the vGPU profile name
- The device plugin discovers and advertises these mdev devices automatically

**Feature Gate**:
- [examples/kubevirt-featuregate-cm.yaml:20-22]() enables the GPU feature gate, required for any GPU passthrough functionality

**Sources**: [examples/kubevirt-featuregate-cm.yaml:1-22]()

## Next Steps

With an understanding of the overall setup workflow and component architecture, proceed to the detailed configuration guides:

1. **[Prerequisites and Host Setup](#2.1)**: Complete IOMMU enablement, driver binding (VFIO-PCI or vGPU), and host verification.

2. **[Installing the Device Plugin](#2.2)**: Deploy the DaemonSet, configure KubeVirt permissions, and verify GPU resources are advertised to Kubernetes.

After successful installation, see [Architecture](#3) to understand the internal implementation details, or proceed directly to creating GPU-enabled VMs using the example manifests in the `examples/` directory.

**Sources**: [README.md:1-211]()

---

