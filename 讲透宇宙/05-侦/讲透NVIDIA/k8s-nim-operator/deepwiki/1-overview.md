<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/k8s-nim-operator · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/bug_report.md](.github/ISSUE_TEMPLATE/bug_report.md)
- [PROJECT](PROJECT)
- [README.md](README.md)

</details>



This document provides an overview of the k8s-nim-operator project, introducing its purpose, core components, and high-level architecture. For detailed API reference documentation, see [API Reference](#5). For installation and deployment instructions, see [Getting Started](#2) and [Deployment](#7).

## Purpose and Scope

The k8s-nim-operator is a Kubernetes Operator designed to facilitate the deployment, management, and scaling of NVIDIA NIM (NVIDIA Inference Microservices) on Kubernetes clusters. NVIDIA NIM microservices deliver AI foundation models as accelerated inference microservices that are portable across data center, workstation, and cloud environments, accelerating generative AI development and deployment. [README.md:6-13]()

This operator implements the Kubernetes operator pattern to manage custom resources representing NIM services, model caching, inference pipelines, and NeMo microservices through a declarative API. [PROJECT:11-98]()

**Sources**: [README.md:1-13](), [PROJECT:1-99]()

## What is k8s-nim-operator?

The k8s-nim-operator extends Kubernetes with custom resource definitions (CRDs) and controllers that automate the lifecycle management of NVIDIA AI inference workloads. The operator runs as a deployment within the Kubernetes cluster and continuously reconciles the desired state (defined in custom resources) with the actual cluster state.

### Project Structure

```mermaid
graph TB
    subgraph "Repository: github.com/NVIDIA/k8s-nim-operator"
        PROJECT["PROJECT<br/>(Kubebuilder config)"]
        API["api/apps/v1alpha1/<br/>(CRD type definitions)"]
        CONTROLLERS["internal/controller/<br/>(reconciliation logic)"]
        WEBHOOKS["internal/webhook/<br/>(validation webhooks)"]
        CONFIG["config/<br/>(deployment manifests)"]
        HELM["deployments/helm/<br/>(Helm chart)"]
    end
    
    PROJECT -->|"defines"| API
    API -->|"used by"| CONTROLLERS
    API -->|"validated by"| WEBHOOKS
    CONTROLLERS -->|"generates"| CONFIG
    CONFIG -->|"packaged in"| HELM
    
    API -->|"NIMService"| CONTROLLERS
    API -->|"NIMCache"| CONTROLLERS
    API -->|"NIMPipeline"| CONTROLLERS
    API -->|"NemoCustomizer"| CONTROLLERS
    API -->|"NemoEvaluator"| CONTROLLERS
```

**Key Components**:

| Component | Location | Purpose |
|-----------|----------|---------|
| CRD Type Definitions | `api/apps/v1alpha1/` | Go structs defining custom resource schemas [PROJECT:19,31,43]() |
| Controllers | `internal/controller/` | Reconciliation loops for each resource type [PROJECT:15,27,39]() |
| Validation Webhooks | `internal/webhook/` | Admission webhooks for `NIMService` and `NIMCache` [PROJECT:21-22,33-34]() |
| Deployment Manifests | `config/` | Kustomize-based Kubernetes manifests [README.md:59]() |
| Helm Chart | `deployments/helm/` | Helm packaging for operator installation |

**Sources**: [README.md:1-110](), [PROJECT:1-99]()

## Custom Resources

The operator manages multiple custom resources under the API group `apps.nvidia.com/v1alpha1`. These resources are divided into functional categories:

### Resource Categories

```mermaid
graph LR
    subgraph "API Group: apps.nvidia.com/v1alpha1"
        subgraph "NIM Resources"
            NS["NIMService<br/>(controller + webhook)"]
            NC["NIMCache<br/>(controller + webhook)"]
            NP["NIMPipeline<br/>(controller)"]
            NB["NIMBuild"]
        end
        
        subgraph "NeMo Microservices"
            NEMO_CUST["NemoCustomizer<br/>(controller)"]
            NEMO_EVAL["NemoEvaluator<br/>(controller)"]
            NEMO_GUARD["NemoGuardrails<br/>(controller)"]
            NEMO_ENT["NemoEntitystore<br/>(controller)"]
            NEMO_DATA["NemoDatastore<br/>(controller)"]
        end
    end
    
    NS -.manages.-> PODS["Kubernetes Pods<br/>(inference workloads)"]
    NC -.manages.-> JOBS["Kubernetes Jobs<br/>(model caching)"]
    NP -.orchestrates.-> NS
```

### Resource Summary Table

| Custom Resource | Controller | Webhook | Purpose |
|-----------------|------------|---------|---------|
| `NIMService` | ✓ | ✓ | Deploys and manages NIM inference microservices [PROJECT:17-23]() |
| `NIMCache` | ✓ | ✓ | Manages model caching to PersistentVolumeClaims [PROJECT:29-35]() |
| `NIMPipeline` | ✓ | ✗ | Orchestrates multi-step inference workflows [PROJECT:41-44]() |
| `NIMBuild` | ✗ | ✗ | Builds custom NIM containers [PROJECT:94-97]() |
| `NemoCustomizer` | ✓ | ✗ | Manages model customization workflows [PROJECT:87-89]() |
| `NemoEvaluator` | ✓ | ✗ | Evaluates model performance [PROJECT:51-53]() |
| `NemoGuardrails` | ✓ | ✗ | Implements safety guardrails for AI models [PROJECT:78-80]() |
| `NemoEntitystore` | ✓ | ✗ | Manages entity data for NeMo workflows [PROJECT:60-62]() |
| `NemoDatastore` | ✓ | ✗ | Manages data storage for NeMo services [PROJECT:69-71]() |

**Sources**: [PROJECT:11-98]()

## Core Architecture

The operator follows the standard Kubernetes operator pattern with controllers, webhooks, and custom resource definitions.

```mermaid
graph TB
    subgraph "Kubernetes API Server"
        ETCD["etcd<br/>(cluster state)"]
    end
    
    subgraph "k8s-nim-operator Deployment"
        MGR["manager.go<br/>(main controller manager)"]
        
        subgraph "Controllers"
            NS_CTRL["nimservice_controller.go"]
            NC_CTRL["nimcache_controller.go"]
            NP_CTRL["nimpipeline_controller.go"]
            NEMO_CTRL["nemo_*_controller.go"]
        end
        
        subgraph "Webhooks"
            NS_WH["nimservice_webhook.go<br/>(validation)"]
            NC_WH["nimcache_webhook.go<br/>(validation)"]
        end
    end
    
    subgraph "Managed Resources"
        NS_CR["NIMService CR"]
        NC_CR["NIMCache CR"]
        
        DEPLOY["Deployment"]
        SVC["Service"]
        JOB["Job"]
        PVC["PVC"]
    end
    
    subgraph "External Dependencies"
        NGC["NGC Registry<br/>(nvcr.io)"]
        HF["Hugging Face"]
        GPU_OP["GPU Operator<br/>(nvidia-driver-ctr)"]
    end
    
    ETCD --> NS_CR
    ETCD --> NC_CR
    
    NS_CR -.watch.-> NS_CTRL
    NC_CR -.watch.-> NC_CTRL
    
    NS_CR -.validate.-> NS_WH
    NC_CR -.validate.-> NC_WH
    
    NS_CTRL -->|"creates/updates"| DEPLOY
    NS_CTRL -->|"creates/updates"| SVC
    NC_CTRL -->|"creates/updates"| JOB
    NC_CTRL -->|"creates/updates"| PVC
    
    MGR -->|"runs"| NS_CTRL
    MGR -->|"runs"| NC_CTRL
    MGR -->|"runs"| NP_CTRL
    MGR -->|"runs"| NEMO_CTRL
    MGR -->|"registers"| NS_WH
    MGR -->|"registers"| NC_WH
    
    DEPLOY -.pulls images.-> NGC
    DEPLOY -.pulls models.-> HF
    DEPLOY -.requires.-> GPU_OP
```

### Controller Reconciliation Pattern

The operator implements the Kubernetes reconciliation pattern where each controller:

1. **Watches** for changes to its custom resource type via the Kubernetes API.
2. **Reconciles** the actual cluster state to match the desired state defined in the custom resource.
3. **Updates** the custom resource status to reflect the current state.
4. **Re-queues** reconciliation if the operation fails or needs to be retried.

For detailed information on the reconciliation loops, see [Operator Pattern](#3.1).

**Sources**: [PROJECT:11-98](), [README.md:1-110]()

## Key Features

### 1. Declarative Model Deployment
Users define NIM services using Kubernetes custom resources. The operator handles:
- Container deployment and configuration.
- GPU resource allocation.
- Service exposure (ClusterIP, LoadBalancer, Ingress, Gateway API).
- Auto-scaling via Horizontal Pod Autoscaler. [README.md:8-10]()

### 2. Model Caching
The `NIMCache` resource pre-downloads and caches model artifacts to PersistentVolumeClaims, enabling:
- Faster pod startup times.
- Shared model storage across multiple pods.
- Reduced external registry traffic. [.github/ISSUE_TEMPLATE/bug_report.md:31-36]()

### 3. Validation Webhooks
Both `NIMService` and `NIMCache` implement admission webhooks that validate resource specifications before they are persisted to etcd, preventing invalid configurations from being applied. [PROJECT:21-22,33-34]()

### 4. Multi-Architecture Support
The operator is built and distributed as multi-architecture images supporting `linux/amd64` and `linux/arm64`. [README.md:24-28]()

**Sources**: [PROJECT:21-35](), [README.md:50-52](), [README.md:8-10](), [.github/ISSUE_TEMPLATE/bug_report.md:31-36]()

## Dependencies and Integration Points

### Required Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Kubernetes | v1.28+ | Orchestration platform [README.md:19]() |
| NVIDIA GPU Operator | Latest | GPU driver and runtime management [.github/ISSUE_TEMPLATE/bug_report.md:15]() |
| NVIDIA GPUs | Supported by NIM | Hardware acceleration for inference [README.md:20]() |

### External Integrations

```mermaid
graph TB
    subgraph "k8s-nim-operator"
        OP["Operator Controllers"]
    end
    
    subgraph "Container Registries"
        NGC["NGC Registry<br/>(nvcr.io)<br/>- NIM container images<br/>- Model artifacts"]
        GHCR["GitHub Container Registry<br/>(ghcr.io)<br/>- Operator images"]
        HF["Hugging Face<br/>- Model weights<br/>- Tokenizers"]
    end
    
    subgraph "Kubernetes APIs"
        CORE["Core API<br/>(Pod, Service, PVC)"]
        BATCH["Batch API<br/>(Job)"]
        HPA["Autoscaling API<br/>(HorizontalPodAutoscaler)"]
        GW["Gateway API<br/>(optional)"]
    end
    
    subgraph "NVIDIA Components"
        GPU_OP["GPU Operator<br/>- nvidia-driver-ctr<br/>- Device Plugin"]
    end
    
    OP -->|"pulls operator images"| GHCR
    OP -->|"configures pods to pull"| NGC
    OP -->|"configures pods to pull"| HF
    
    OP -->|"creates/manages"| CORE
    OP -->|"creates/manages"| BATCH
    OP -->|"creates/manages"| HPA
    OP -->|"optionally creates"| GW
    
    OP -.requires.-> GPU_OP
```

### Authentication Requirements
The operator and deployed workloads require credentials for access to the NVIDIA container registry and model repositories. [README.md:30-32]()

**Sources**: [.github/ISSUE_TEMPLATE/bug_report.md:10-46](), [README.md:15-21]()

## Deployment Targets

The operator supports multiple deployment methods:

1. **Helm Chart** - Recommended for production deployments.
2. **OLM Bundle** - For OpenShift and OLM-enabled clusters.
3. **Raw Manifests** - For development and testing. [README.md:81-92]()

**Sources**: [README.md:74-92]()

## System Requirements

### Kubernetes Environment

| Component | Requirement |
|-----------|-------------|
| Kubernetes Version | v1.28 or higher [README.md:19]() |
| Container Runtime | Containerd, CRI-O, or Docker [.github/ISSUE_TEMPLATE/bug_report.md:13]() |
| Kubernetes Flavors | K8s, OCP, Rancher, GKE, EKS [.github/ISSUE_TEMPLATE/bug_report.md:14]() |

### Hardware Requirements

| Resource | Requirement |
|----------|-------------|
| GPUs | NVIDIA GPUs supported by target NIM microservices [README.md:20]() |
| Storage | PVC support for model caching [.github/ISSUE_TEMPLATE/bug_report.md:36]() |

**Sources**: [README.md:17-21](), [.github/ISSUE_TEMPLATE/bug_report.md:10-18]()

## Project Layout

The repository follows the Kubebuilder v4 project structure: [PROJECT:7]()

```
k8s-nim-operator/
├── api/                      # CRD type definitions
│   └── apps/v1alpha1/       # API group version
├── internal/
│   ├── controller/          # Controller reconciliation logic
│   └── webhook/             # Admission webhook handlers
├── config/                  # Kustomize manifests
│   ├── crd/                # Generated CRD YAML files
│   ├── rbac/               # RBAC manifests
│   └── default/            # Default deployment configuration
├── deployments/
│   ├── container/          # Container build files
│   └── helm/               # Helm chart
├── bundle/                 # OLM bundle manifests
├── pkg/                    # Shared packages
└── PROJECT                 # Kubebuilder project metadata
```

**Sources**: [PROJECT:1-99](), [README.md:99-110]()

## Next Steps

- To install and configure the operator, see [Getting Started](#2)
- To understand the operator architecture in depth, see [Architecture](#3)
- To learn about individual custom resources, see [Custom Resources](#4)
- To contribute to the project, see [Contributing](#10)
- For troubleshooting common issues, see [Troubleshooting](#11)

---

