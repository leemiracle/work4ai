<!-- source: DeepWiki mcp.deepwiki.com · repo vectordotdev/vector · page 7 Deployment · fetched 2026-10-29 -->

# Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [distribution/install.sh](distribution/install.sh)
- [distribution/kubernetes/vector-agent/README.md](distribution/kubernetes/vector-agent/README.md)
- [distribution/kubernetes/vector-agent/configmap.yaml](distribution/kubernetes/vector-agent/configmap.yaml)
- [distribution/kubernetes/vector-agent/daemonset.yaml](distribution/kubernetes/vector-agent/daemonset.yaml)
- [distribution/kubernetes/vector-agent/rbac.yaml](distribution/kubernetes/vector-agent/rbac.yaml)
- [distribution/kubernetes/vector-agent/serviceaccount.yaml](distribution/kubernetes/vector-agent/serviceaccount.yaml)
- [distribution/kubernetes/vector-aggregator/README.md](distribution/kubernetes/vector-aggregator/README.md)
- [distribution/kubernetes/vector-aggregator/configmap.yaml](distribution/kubernetes/vector-aggregator/configmap.yaml)
- [distribution/kubernetes/vector-aggregator/service-headless.yaml](distribution/kubernetes/vector-aggregator/service-headless.yaml)
- [distribution/kubernetes/vector-aggregator/service.yaml](distribution/kubernetes/vector-aggregator/service.yaml)
- [distribution/kubernetes/vector-aggregator/serviceaccount.yaml](distribution/kubernetes/vector-aggregator/serviceaccount.yaml)
- [distribution/kubernetes/vector-aggregator/statefulset.yaml](distribution/kubernetes/vector-aggregator/statefulset.yaml)
- [distribution/kubernetes/vector-stateless-aggregator/README.md](distribution/kubernetes/vector-stateless-aggregator/README.md)
- [distribution/kubernetes/vector-stateless-aggregator/service-headless.yaml](distribution/kubernetes/vector-stateless-aggregator/service-headless.yaml)
- [distribution/kubernetes/vector-stateless-aggregator/service.yaml](distribution/kubernetes/vector-stateless-aggregator/service.yaml)
- [website/content/en/releases/0.22.3.md](website/content/en/releases/0.22.3.md)
- [website/cue/reference/administration/interfaces/kubectl.cue](website/cue/reference/administration/interfaces/kubectl.cue)
- [website/cue/reference/releases/0.22.0.cue](website/cue/reference/releases/0.22.0.cue)
- [website/cue/reference/releases/0.22.3.cue](website/cue/reference/releases/0.22.3.cue)
- [website/cue/reference/versions.cue](website/cue/reference/versions.cue)

</details>



This document covers Vector's deployment methods and infrastructure. It explains how Vector can be installed and run in production environments, including bare-metal/VM installations via the `install.sh` script, containerized deployments using Docker images, and Kubernetes deployments across three distinct roles (Agent, Aggregator, and Stateless-Aggregator).

For information about building Vector from source and the development environment, see [Environment Setup](#8.1). For details about the CI/CD pipeline that produces deployment artifacts, see [CI/CD Pipeline](#8.3).

## Deployment Methods Overview

Vector supports three primary deployment methods, each targeting different operational environments and use cases:

Title: Deployment Strategy Overview
```mermaid
graph TB
    subgraph "Deployment Methods"
        [install.sh] --> ["distribution/install.sh"]
        [ContainerImages] --> ["distribution/docker/"]
        [K8sManifests] --> ["distribution/kubernetes/"]
    end
    
    subgraph "Target Environments"
        [BareMetal] --> ["Bare Metal / VMs"]
        [Container] --> ["Docker / Containerd"]
        [K8sCluster] --> ["Kubernetes Cluster"]
    end
    
    subgraph "Artifacts"
        [TarGz] --> ["vector-VERSION-ARCH.tar.gz"]
        [DockerImage] --> ["timberio/vector:latest"]
        [K8sYAML] --> ["ConfigMap / Service / RBAC"]
    end
    
    ["distribution/install.sh"] --> [TarGz]
    [TarGz] --> [BareMetal]
    
    ["distribution/docker/"] --> [DockerImage]
    [DockerImage] --> [Container]
    [DockerImage] --> [K8sCluster]
    
    ["distribution/kubernetes/"] --> [K8sYAML]
    [K8sYAML] --> [K8sCluster]
```

**Platform Detection and Architecture Support**

The deployment infrastructure supports multiple architectures and operating systems through platform-specific artifacts. The installer script [distribution/install.sh:146-168]() maps detected architectures to specific archive targets.

| Architecture | Target Triple | C Library | Docker Support | K8s Support |
|--------------|--------------|-----------|----------------|-------------|
| x86_64 | x86_64-unknown-linux-gnu | glibc >= 2.18 | ✓ | ✓ |
| x86_64 | x86_64-unknown-linux-musl | musl | ✓ | ✓ |
| aarch64 | aarch64-unknown-linux-musl | musl | ✓ | ✓ |
| aarch64 | aarch64-apple-darwin | macOS | ✗ | ✗ |
| armv7 | armv7-unknown-linux-gnueabihf | glibc | ✓ | ✓ |
| armv7 | armv7-unknown-linux-musleabihf | musl | ✓ | ✓ |

Sources: [distribution/install.sh:146-168](), [distribution/kubernetes/vector-agent/rbac.yaml:13]()

## Binary Installation

The `install.sh` script provides automated installation for Unix-like systems by detecting the platform, downloading the appropriate archive, extracting it, and optionally configuring the system PATH.

### Installation Script Architecture

Title: install.sh Logic Flow
```mermaid
graph TB
    ["main()"] -- "distribution/install.sh:58" --> [GetArch]
    
    subgraph "Platform Detection"
        [GetArch] --> ["get_architecture()"]
        ["get_architecture()"] -- "distribution/install.sh:137" --> [DetectLibc]
    end
    
    subgraph "Archive Handling"
        [GetArch] --> [BuildURL]
        [BuildURL] -- "distribution/install.sh:170" --> [Download]
        [Download] -- "downloader()" --> [Extract]
    end
    
    subgraph "Installation"
        [Extract] --> [CopyFiles]
        [CopyFiles] -- "distribution/install.sh:197" --> [ModifyPath]
        [ModifyPath] -- "add_to_path()" --> [Complete]
    end
```

**Architecture Mapping Logic**

The script maps detected system architectures to Vector's release archive naming convention [distribution/install.sh:146-168](). For example, `aarch64-apple-darwin` maps to `arm64-apple-darwin` [distribution/install.sh:147-149]().

**Installation Modes**

The script supports two directory structure modes controlled by the `--prefix` flag [distribution/install.sh:72-77](). When `--prefix` is specified, it uses an FHS-compliant layout, copying binaries to `bin/` and configurations to `share/vector/config/` [distribution/install.sh:192-206]().

For details, see [Binary Installation](#7.1).

Sources: [distribution/install.sh:1-228](), [distribution/install.sh:146-168](), [distribution/install.sh:192-206]()

## Container Images

Vector's container images are built with multiple base operating systems and architectures to support diverse deployment scenarios.

**Image Variants**

Vector supports several base images:
- **Alpine**: Minimal size using `musl`.
- **Debian**: Standard `glibc` with full utilities.
- **Distroless**: Minimal attack surface, available in `libc` and `static` variants.

The Kubernetes manifests reference the `distroless-libc` variant by default (e.g., version `0.57.0-distroless-libc`) [distribution/kubernetes/vector-aggregator/service.yaml:12](), [distribution/kubernetes/vector-agent/rbac.yaml:13]().

**Multi-Architecture Support**

Images are published for multiple architectures including `x86_64` and `aarch64`. The registry automatically serves the correct architecture based on the host runtime. Version metadata is tracked manually in CUE [website/cue/reference/versions.cue:4-108]().

For details, see [Container Images](#7.2).

Sources: [distribution/kubernetes/vector-aggregator/service.yaml:12](), [distribution/kubernetes/vector-agent/rbac.yaml:13](), [website/cue/reference/versions.cue:1-109]()

## Kubernetes Deployment

Vector's Kubernetes deployment provides three distinct roles, each optimized for specific data collection and processing patterns. These manifests are typically generated via Helm [distribution/kubernetes/vector-aggregator/README.md:1-3]().

### Deployment Roles and Workload Types

Title: Kubernetes Resource Mapping
```mermaid
graph TB
    subgraph "Agent Role [DaemonSet]"
        [AgentDS] --> ["distribution/kubernetes/vector-agent/daemonset.yaml"]
        [AgentRBAC] --> ["distribution/kubernetes/vector-agent/rbac.yaml"]
        [AgentSA] --> ["distribution/kubernetes/vector-agent/serviceaccount.yaml"]
    end
    
    subgraph "Aggregator Role [StatefulSet]"
        [AggSS] --> ["distribution/kubernetes/vector-aggregator/statefulset.yaml"]
        [AggSvc] --> ["distribution/kubernetes/vector-aggregator/service.yaml"]
        [AggCM] --> ["distribution/kubernetes/vector-aggregator/configmap.yaml"]
    end
    
    subgraph "Stateless-Aggregator Role [Deployment]"
        [StatelessDep] --> ["distribution/kubernetes/vector-stateless-aggregator/deployment.yaml"]
        [StatelessSvc] --> ["distribution/kubernetes/vector-stateless-aggregator/service-headless.yaml"]
    end

    [AgentDS] -.-> [AgentSA]
    [AgentSA] -.-> [AgentRBAC]
    [AggSS] -.-> [AggCM]
    [AggSS] -.-> [AggSvc]
    [StatelessDep] -.-> [StatelessSvc]
```

**Role Definitions**

1.  **Agent**: Deployed as a `DaemonSet` [distribution/kubernetes/vector-agent/daemonset.yaml:4](). It requires specific RBAC permissions to `list` and `watch` `namespaces`, `nodes`, and `pods` [distribution/kubernetes/vector-agent/rbac.yaml:15-23](). It mounts host paths for log collection and process information [distribution/kubernetes/vector-agent/daemonset.yaml:91-104]().
2.  **Aggregator**: Deployed as a `StatefulSet` [distribution/kubernetes/vector-aggregator/README.md:1-3](). It provides stable network identities and is designed for centralized processing.
3.  **Stateless-Aggregator**: Deployed as a standard `Deployment` [distribution/kubernetes/vector-stateless-aggregator/README.md:6](). It is optimized for horizontal scaling where persistent state is not required and uses a headless service for direct pod addressing [distribution/kubernetes/vector-stateless-aggregator/service-headless.yaml:15]().

**Service Exposure**

Aggregator roles expose a variety of ports via `Service` objects [distribution/kubernetes/vector-aggregator/service.yaml:15-40](), including:
- `datadog-agent` (8282)
- `fluent` (24224)
- `logstash` (5044)
- `splunk-hec` (8080)
- `statsd` (8125)
- `syslog` (9000)
- `vector` (6000)
- `prom-exporter` (9090)

For details, see [Kubernetes Deployment](#7.3).

Sources: [distribution/kubernetes/vector-agent/rbac.yaml:1-43](), [distribution/kubernetes/vector-agent/daemonset.yaml:1-105](), [distribution/kubernetes/vector-aggregator/service.yaml:1-45](), [distribution/kubernetes/vector-stateless-aggregator/service-headless.yaml:1-46](), [distribution/kubernetes/vector-stateless-aggregator/README.md:1-7]()

---

