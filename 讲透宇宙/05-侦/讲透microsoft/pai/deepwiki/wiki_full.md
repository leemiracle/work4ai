# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [RELEASE_NOTE.md](RELEASE_NOTE.md)
- [contrib/debug-tools/docs/remote-debug-pai-job_zh_CN.md](contrib/debug-tools/docs/remote-debug-pai-job_zh_CN.md)
- [contrib/kubespray/config/config.yaml](contrib/kubespray/config/config.yaml)
- [docs/manual/cluster-admin/installation-guide.md](docs/manual/cluster-admin/installation-guide.md)
- [docs_zh_CN/manual/cluster-admin/installation-guide.md](docs_zh_CN/manual/cluster-admin/installation-guide.md)
- [version/K8S.VERSION](version/K8S.VERSION)
- [version/PAI.VERSION](version/PAI.VERSION)

</details>



OpenPAI (Open Platform for AI) is an open-source platform designed to manage AI workloads on Kubernetes. It provides a comprehensive solution for organizations to efficiently share and utilize computing resources (particularly GPU farms), manage AI assets, and simplify IT operations for AI workloads.

This documentation covers the OpenPAI system architecture, core components, installation requirements, and operational flows. For deployment instructions, refer to [Installation and Deployment](#2).

## What is OpenPAI?

OpenPAI is a full-stack solution that enables:

- Sharing powerful AI computing resources (GPU/FPGA farms) among teams
- Sharing and reusing common AI assets (models, data, environments)
- Easy IT operations platform for AI workloads
- Running complete training pipelines in one place

As of version 1.8.1 (current stable version), OpenPAI uses a pure Kubernetes-based architecture, having transitioned from its previous architecture that used Kubernetes combined with Hadoop YARN.

Sources: [README.md:79-84](), [README.md:228-230](), [version/PAI.VERSION:1-2]()

## System Architecture

OpenPAI follows a modular architecture with distinct components handling different aspects of the platform. Below is a high-level overview of the system architecture:

```mermaid
graph TD
    User["User"] --> WebPortal["Web Portal"]
    User --> VSCode["VSCode Extension"]
    WebPortal --> RestAPI["REST Server API"]
    VSCode --> RestAPI
    RestAPI --> K8s["Kubernetes API"]
    RestAPI --> DB[("Database")]
    
    subgraph "Core Components"
        K8s --> FrameworkController["Framework Controller"]
        K8s --> HivedScheduler["Hived Scheduler"]
        K8s --> Runtime["OpenPAI Runtime"]
    end
    
    subgraph "Monitoring"
        Prometheus["Prometheus"]
        AlertManager["Alert Manager"]
    end
    
    K8s --> Prometheus
    Prometheus --> AlertManager
    
    FrameworkController --> Pods["Job Pods"]
    HivedScheduler --> Pods
    Runtime --> Pods
```

Sources: [README.md:11-12](), [README.md:154-163]()

### Core Components

OpenPAI consists of one main repository along with 7 standalone component repositories:

1. **hivedscheduler**: A specialized scheduler for multi-tenant GPU clusters, providing resource isolation, GPU topology guarantees, and efficient gang scheduling
2. **frameworkcontroller**: Orchestrates applications on Kubernetes with a single controller
3. **openpai-protocol**: Defines the job protocol specification for OpenPAI
4. **openpai-runtime**: Provides runtime support for the protocol, including error pattern classification
5. **openpaisdk**: JavaScript SDK for developers building upon OpenPAI
6. **openpaimarketplace**: Stores job examples and templates for sharing
7. **openpaivscode**: VSCode extension for connecting to OpenPAI clusters

Sources: [README.md:154-163](), [README.md:234-247]()

### Deployment Architecture

OpenPAI requires at least 3 separate machines for a minimal deployment:

```mermaid
graph TD
    subgraph "Deployment Structure"
        DevBox["Dev Box Machine"] -->|deploys to| Master["Master Node"]
        DevBox -->|deploys to| Worker["Worker Node(s)"]
        
        subgraph "Master Node"
            K8sMaster["Kubernetes Control Plane"]
            PAIServices["OpenPAI Core Services"]
        end
        
        subgraph "Worker Node(s)"
            K8sWorker["Kubernetes Node Components"]
            UserJobs["User AI Jobs"]
        end
    end
    
    subgraph "Configuration Files"
        LayoutYAML["layout.yaml\n(Cluster Structure)"]
        ConfigYAML["config.yaml\n(Deployment Settings)"]
    end
    
    DevBox --- LayoutYAML
    DevBox --- ConfigYAML
```

- **Dev Box**: Controls masters and workers through SSH during installation and management
- **Master**: Runs Kubernetes control plane and core OpenPAI services (currently only one master supported)
- **Worker**: Executes user jobs with specialized hardware (GPU, CPU, etc.)

Sources: [docs/manual/cluster-admin/installation-guide.md:9-146]()

## Job Lifecycle

The following sequence diagram illustrates how a job flows through the OpenPAI system:

```mermaid
sequenceDiagram
    participant User
    participant WebPortal as "Web Portal"
    participant RestServer as "REST Server"
    participant FrameworkCtrl as "Framework Controller"
    participant HivedScheduler as "Hived Scheduler"
    participant Runtime as "OpenPAI Runtime"
    participant JobPods as "Job Pods"
    
    User->>WebPortal: Submit job via UI
    WebPortal->>RestServer: POST /api/v2/jobs
    RestServer->>RestServer: Validate job protocol
    RestServer->>FrameworkCtrl: Create Framework
    FrameworkCtrl->>HivedScheduler: Request resources
    HivedScheduler->>FrameworkCtrl: Allocate resources
    FrameworkCtrl->>JobPods: Create pods
    JobPods->>Runtime: Execute job
    Runtime->>JobPods: Set up environment
    
    loop Job monitoring
        User->>WebPortal: View job status
        WebPortal->>RestServer: GET /api/v2/jobs/:jobName
        RestServer->>FrameworkCtrl: Query status
        FrameworkCtrl-->>RestServer: Return status
        RestServer-->>WebPortal: Display status
    end
    
    Runtime->>FrameworkCtrl: Job completion/failure
    FrameworkCtrl->>RestServer: Update job status
    RestServer->>WebPortal: Update UI
    WebPortal->>User: Show final status
```

Sources: [README.md:143-151]()

## Supported Features

OpenPAI provides a range of features for both users and administrators:

### For Cluster Users

- **Job Management**: Submit and monitor AI jobs through Web Portal or SDK
- **Resource Allocation**: Access to specialized computing resources (GPU, CPU, etc.)
- **Data Management**: Use cluster-provisioned storage or custom storage
- **Collaboration**: Share job templates through marketplace
- **Tools**: Web Portal, VSCode extension, and command-line tools

### For Cluster Administrators

- **Cluster Management**: Add/remove nodes, monitor services
- **User Management**: Manage users and permissions
- **Resource Isolation**: Create virtual clusters for teams
- **Monitoring & Alerts**: Track cluster health and usage
- **Customization**: Extend functionality through plugins

Sources: [README.md:102-151]()

## Infrastructure Support

OpenPAI supports various types of computing hardware:

- CPU workers
- NVIDIA GPU workers
- AMD GPU workers
- Enflame DTU workers
- Other specialized computing hardware (TPU, NPU, etc.)

OpenPAI also supports two schedulers:
- **Hived Scheduler** (default): Supports virtual cluster division, topology-aware resource guarantee
- **Kubernetes Default Scheduler**: Used for specialized hardware beyond CPU/NVIDIA GPU

Sources: [docs/manual/cluster-admin/installation-guide.md:67-79]()

## Component Interaction

The following diagram illustrates how different components of OpenPAI interact with each other:

```mermaid
graph LR
    subgraph "User Interface"
        WebPortal["Web Portal"]
        VSCodeExt["VSCode Extension"]
        SDK["OpenPAI SDK"]
    end
    
    subgraph "API Layer"
        RestServer["REST Server API"]
    end
    
    subgraph "Core Services"
        K8s["Kubernetes API"]
        FrameworkCtrl["Framework Controller"]
        HivedSched["Hived Scheduler"]
        Runtime["OpenPAI Runtime"]
    end
    
    subgraph "Storage"
        StorageManager["Storage Manager"]
    end
    
    subgraph "Monitoring"
        Prometheus["Prometheus"]
        AlertManager["Alert Manager"]
    end
    
    WebPortal --> RestServer
    VSCodeExt --> RestServer
    SDK --> RestServer
    
    RestServer --> K8s
    RestServer --> StorageManager
    
    K8s --> FrameworkCtrl
    K8s --> HivedSched
    K8s --> Runtime
    
    K8s --> Prometheus
    Prometheus --> AlertManager
    AlertManager --> RestServer
```

Sources: [README.md:17-55]()

## Installation Overview

The installation of OpenPAI involves three main steps:

1. **Preparation**: Create configuration files (`layout.yaml` and `config.yaml`)
2. **Kubernetes Installation**: Deploy Kubernetes using Kubespray
3. **OpenPAI Services Installation**: Deploy OpenPAI services on Kubernetes

The installation requires careful configuration of the dev box, master node, and worker nodes, with specific hardware and software requirements for each.

For detailed installation instructions, refer to [Installation and Deployment](#2).

Sources: [docs/manual/cluster-admin/installation-guide.md:148-153](), [docs/manual/cluster-admin/installation-guide.md:401-411]()

## Version History

OpenPAI has gone through significant changes over time. The current stable version is v1.8.1 (released December 2021).

Key architectural changes:

| Component | Before v1.0.0 | v1.0.0 and later |
|-----------|---------------|------------------|
| Architecture | Kubernetes + Hadoop YARN | Pure Kubernetes |
| Scheduler | YARN Scheduler | HiveD / K8S default |
| Job Orchestrating | YARN Framework Launcher | Framework Controller |
| Storage | Team-wise storage plugin | PV/PVC storage sharing |
| API | v1 + v2 | Pure v2 |

For complete release notes, refer to the [RELEASE_NOTE.md]() file.

Sources: [docs/manual/cluster-admin/installation-guide.md:3-4](), [docs/manual/cluster-admin/installation-guide.md:121-129](), [RELEASE_NOTE.md:3-8]()

## Current Status

As of the release of v1.8.1, OpenPAI has entered stable mode with no major feature releases planned. The repository is in read-only mode, and for collaboration, users should contact repository administrators directly.

Sources: [README.md:9-10]()

---

# Page: Installation and Deployment

# Installation and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [RELEASE_NOTE.md](RELEASE_NOTE.md)
- [contrib/debug-tools/docs/remote-debug-pai-job_zh_CN.md](contrib/debug-tools/docs/remote-debug-pai-job_zh_CN.md)
- [contrib/kubespray/config/config.yaml](contrib/kubespray/config/config.yaml)
- [contrib/kubespray/pre-installation.yml](contrib/kubespray/pre-installation.yml)
- [contrib/kubespray/quick-start-service.sh](contrib/kubespray/quick-start-service.sh)
- [contrib/kubespray/requirement.sh](contrib/kubespray/requirement.sh)
- [contrib/kubespray/roles/kubectl/tasks/main.yml](contrib/kubespray/roles/kubectl/tasks/main.yml)
- [contrib/kubespray/roles/pre-installation/defaults/main.yml](contrib/kubespray/roles/pre-installation/defaults/main.yml)
- [contrib/kubespray/roles/pre-installation/tasks/main.yml](contrib/kubespray/roles/pre-installation/tasks/main.yml)
- [contrib/kubespray/roles/set-python3/defaults/main.yml](contrib/kubespray/roles/set-python3/defaults/main.yml)
- [contrib/kubespray/roles/set-python3/tasks/main.yml](contrib/kubespray/roles/set-python3/tasks/main.yml)
- [contrib/kubespray/script/__init__.py](contrib/kubespray/script/__init__.py)
- [contrib/kubespray/script/configuration-kubespray.sh](contrib/kubespray/script/configuration-kubespray.sh)
- [contrib/kubespray/script/kubernetes-boot.sh](contrib/kubespray/script/kubernetes-boot.sh)
- [contrib/kubespray/script/requirements.txt](contrib/kubespray/script/requirements.txt)
- [contrib/kubespray/script/service-boot.sh](contrib/kubespray/script/service-boot.sh)
- [contrib/kubespray/script/start-service-in-dev-box.sh](contrib/kubespray/script/start-service-in-dev-box.sh)
- [contrib/kubespray/set-host-daemon-port-range.yml](contrib/kubespray/set-host-daemon-port-range.yml)
- [contrib/kubespray/set-kubectl.yml](contrib/kubespray/set-kubectl.yml)
- [docs/manual/cluster-admin/installation-guide.md](docs/manual/cluster-admin/installation-guide.md)
- [docs_zh_CN/manual/cluster-admin/installation-guide.md](docs_zh_CN/manual/cluster-admin/installation-guide.md)
- [src/dev-box/build/dev-box.common.dockerfile](src/dev-box/build/dev-box.common.dockerfile)
- [src/pylon/build/pylon.common.dockerfile](src/pylon/build/pylon.common.dockerfile)
- [version/K8S.VERSION](version/K8S.VERSION)
- [version/PAI.VERSION](version/PAI.VERSION)

</details>



This document provides a comprehensive guide on how to install and deploy OpenPAI (Platform for AI) on a cluster of machines. OpenPAI is designed to help organizations manage AI computing resources and run deep learning workloads efficiently.

## Overview

Since version 1.0.0, OpenPAI has adopted a pure Kubernetes-based architecture, moving away from the previous Yarn and Kubernetes hybrid approach. This guide focuses on deploying this modern version of OpenPAI.

The installation process consists of three main steps:
1. Preparing configuration files
2. Starting Kubernetes
3. Deploying OpenPAI services

## Installation Requirements

The deployment of OpenPAI requires at least 3 separate machines:

```mermaid
graph TD
    subgraph "Deployment Architecture"
        DevBox["Dev Box Machine"]
        Master["Master Machine"]
        Worker1["Worker Machine 1"]
        Worker2["Worker Machine 2"]
        WorkerN["Worker Machine N..."]
        
        DevBox -->|"deploys to"| Master
        DevBox -->|"deploys to"| Worker1
        DevBox -->|"deploys to"| Worker2
        DevBox -->|"deploys to"| WorkerN
        
        Master -->|"runs"| K8sMaster["Kubernetes\nControl Plane"]
        Master -->|"runs"| PAIServices["OpenPAI\nCore Services"]
        
        Worker1 -->|"runs"| K8sWorker1["Kubernetes\nNode Components"]
        Worker1 -->|"runs"| Jobs1["User Jobs"]
        
        Worker2 -->|"runs"| K8sWorker2["Kubernetes\nNode Components"]
        Worker2 -->|"runs"| Jobs2["User Jobs"]
        
        WorkerN -->|"runs"| K8sWorkerN["Kubernetes\nNode Components"]
        WorkerN -->|"runs"| JobsN["User Jobs"]
    end
```

Sources: [docs/manual/cluster-admin/installation-guide.md:9-146]()), [contrib/kubespray/script/service-boot.sh:1-58]()

### Machine Requirements

#### Dev Box Machine

| Hardware Requirements | Software Requirements |
|------------------------|------------------------|
| - Ability to communicate with all other machines<br>- Separate from the cluster<br>- Internet access (particularly Docker Hub) | - Ubuntu 16.04 (18.04, 20.04 should work)<br>- SSH service enabled<br>- Passwordless SSH to all other machines<br>- Docker installed |

#### Master Machine

| Hardware Requirements | Software Requirements |
|------------------------|------------------------|
| - At least 40GB of free memory<br>- Static LAN IP address<br>- Communication with all other machines<br>- Internet access | - Ubuntu 16.04 (18.04, 20.04 should work)<br>- SSH service enabled<br>- Same username/password as worker machines<br>- Docker installed<br>- NTP service enabled<br>- Dedicated for OpenPAI |

#### Worker Machines

OpenPAI supports various types of worker machines:

| Worker Type | Hardware Requirements | Additional Software Requirements |
|-------------|------------------------|----------------------------------|
| CPU Worker | - At least 16GB of free memory<br>- Static LAN IP address<br>- Internet access | Same as master |
| NVIDIA GPU Worker | Same as CPU worker | - NVIDIA GPU Driver<br>- nvidia-container-runtime (configured as Docker default runtime) |
| Other Computing Devices<br>(TPU, NPU, etc.) | Same as CPU worker | - Device driver<br>- Container runtime for the device<br>- Device plugin for Kubernetes |

Sources: [docs/manual/cluster-admin/installation-guide.md:9-146]()

## Installation Process

### 1. Prepare Configuration Files

First, clone the OpenPAI repository and switch to the desired version:

```bash
git clone https://github.com/microsoft/pai.git
cd pai
git checkout v1.8.1
```

Edit the following configuration files in the `<pai-code-dir>/contrib/kubespray/config` directory:

#### layout.yaml

This file defines your cluster's machine layout:

```yaml
machine-sku:
  master-machine:
    mem: 60Gi
    cpu:
      vcore: 24
  gpu-machine:
    computing-device:
      type: nvidia.com/gpu
      model: K80
      count: 4
    mem: 220Gi
    cpu:
      vcore: 24

machine-list:
  - hostname: pai-master
    hostip: 10.0.0.1
    machine-type: master-machine
    pai-master: "true"
  - hostname: pai-worker1
    hostip: 10.0.0.2
    machine-type: gpu-machine
    pai-worker: "true"
  - hostname: pai-worker2
    hostip: 10.0.0.3
    machine-type: gpu-machine
    pai-worker: "true"
```

#### config.yaml

This file contains configuration settings for both Kubernetes and OpenPAI:

```yaml
user: username
password: password
docker_image_tag: v1.8.1

# Optional settings can be uncommented and modified as needed
# enable_hived_scheduler: true
# enable_docker_cache: true
# openpai_kube_network_plugin: calico
```

Sources: [docs/manual/cluster-admin/installation-guide.md:154-323]()), [contrib/kubespray/config/config.yaml:1-96]()

### 2. Start Kubernetes

Navigate to the Kubespray directory and run the installation script:

```bash
cd <pai-code-dir>/contrib/kubespray
/bin/bash quick-start-kubespray.sh
```

This script performs several key actions:
1. Validates your environment requirements
2. Creates Kubernetes configuration based on your files
3. Uses Kubespray to install Kubernetes on all machines

If successful, you'll see output indicating how to set up kubectl:

```
You can run the following commands to set up kubectl on your localhost:
ansible-playbook -i ${HOME}/pai-deploy/kubespray/inventory/pai/hosts.yml set-kubectl.yml --ask-become-pass
```

The Kubernetes configuration file will be placed at `~/pai-deploy/kube/config`.

Sources: [docs/manual/cluster-admin/installation-guide.md:324-376]()), [contrib/kubespray/script/kubernetes-boot.sh:1-15]()

### 3. Deploy OpenPAI Services

After Kubernetes is successfully installed, deploy OpenPAI services:

```bash
/bin/bash quick-start-service.sh
```

This script will:
1. Save your configuration files to the deployment directory
2. Generate OpenPAI service configurations
3. Start all OpenPAI services on the Kubernetes cluster

If successful, you'll see output similar to:

```
Kubernetes cluster config :     ~/pai-deploy/kube/config
OpenPAI cluster config    :     ~/pai-deploy/cluster-cfg
OpenPAI cluster ID        :     pai
Default username          :     admin
Default password          :     admin-password

You can go to http://<your-master-ip>, then use the default username and password to log in.
```

Sources: [docs/manual/cluster-admin/installation-guide.md:377-397]()), [contrib/kubespray/quick-start-service.sh:1-16]()), [contrib/kubespray/script/service-boot.sh:1-58](), [contrib/kubespray/script/start-service-in-dev-box.sh:1-17]()

## Installation Flow Diagram

```mermaid
flowchart TD
    A["Clone PAI repository"]
    B["Edit configuration files\n(layout.yaml, config.yaml)"]
    C["Run quick-start-kubespray.sh\nto install Kubernetes"]
    D["Run quick-start-service.sh\nto deploy OpenPAI services"]
    E["Access web portal\nwith admin credentials"]
    
    A --> B
    B --> C
    C --> D
    D --> E
    
    subgraph "Configuration Phase"
        A
        B
    end
    
    subgraph "Kubernetes Installation"
        C
        C1["Check requirements"]
        C2["Configure kubespray"]
        C3["Deploy Kubernetes"]
        C1 --> C2 --> C3
    end
    
    subgraph "OpenPAI Services Deployment"
        D
        D1["Generate service configurations"]
        D2["Push configurations to Kubernetes"]
        D3["Start OpenPAI services"]
        D1 --> D2 --> D3
    end
    
    subgraph "Post-Installation"
        E
    end
```

Sources: [docs/manual/cluster-admin/installation-guide.md:148-410]()), [contrib/kubespray/script/start-service-in-dev-box.sh:1-17]()

## Component Architecture

```mermaid
graph TD
    subgraph "OpenPAI Architecture"
        Kubespray["Kubespray\n(Kubernetes Deployment)"]
        K8s["Kubernetes Cluster"]
        
        subgraph "OpenPAI Core Services"
            WebPortal["Web Portal"]
            RestServer["REST Server"]
            Pylon["Pylon (Gateway)"]
            FrameworkController["Framework Controller"]
            HivedScheduler["Hived Scheduler"]
            PAIRuntime["OpenPAI Runtime"]
            Monitoring["Monitoring\n(Prometheus/AlertManager)"]
        end
        
        Kubespray -->|"installs"| K8s
        K8s -->|"hosts"| WebPortal
        K8s -->|"hosts"| RestServer
        K8s -->|"hosts"| Pylon
        K8s -->|"hosts"| FrameworkController
        K8s -->|"hosts"| HivedScheduler
        K8s -->|"hosts"| PAIRuntime
        K8s -->|"hosts"| Monitoring
        
        WebPortal -->|"uses"| Pylon
        Pylon -->|"routes to"| RestServer
        RestServer -->|"manages"| FrameworkController
        RestServer -->|"configures"| HivedScheduler
        FrameworkController -->|"schedules using"| HivedScheduler
        FrameworkController -->|"runs with"| PAIRuntime
    end
```

Sources: [README.md:1-221]()), [docs/manual/cluster-admin/installation-guide.md:67-78]()

## Post-Installation

After successful installation, you should:

1. Keep the `~/pai-deploy` folder for future maintenance and operations
2. Record your OpenPAI cluster ID (default is `pai`)
3. Access the web portal at `http://<master-ip>` with the default credentials:
   - Username: `admin`
   - Password: `admin-password`

The most important files in the deployment folder are:
- Kubernetes cluster config (`~/pai-deploy/kube/config`)
- OpenPAI cluster config (`~/pai-deploy/cluster-cfg`)

Sources: [docs/manual/cluster-admin/installation-guide.md:399-410](), [contrib/kubespray/script/service-boot.sh:47-57]()

## Special Considerations

### For Azure Users
If deploying on Azure, uncomment and change the network plugin configuration:
```yaml
openpai_kube_network_plugin: weave
```
This is because Azure doesn't support Calico networking.

### For Chinese Users
If deploying in mainland China, you may encounter network issues. Refer to [this issue](https://github.com/microsoft/pai/issues/5592) for special configuration options, including:
- Docker registry mirrors
- Kubernetes image repositories

### For Non-Standard Computing Devices
When using worker types other than CPU or NVIDIA GPU:
1. Set `enable_hived_scheduler: false` in your config
2. Manually deploy the appropriate device plugin after Kubernetes installation

Sources: [docs/manual/cluster-admin/installation-guide.md:321-323]()), [docs/manual/cluster-admin/installation-guide.md:172-173]()), [docs/manual/cluster-admin/installation-guide.md:313-314]()), [docs/manual/cluster-admin/installation-guide.md:398]()

## Troubleshooting

If you encounter issues during installation:

1. Verify that all installation requirements are met using:
   ```bash
   /bin/bash requirement.sh -l config/layout.yaml -c config/config.yaml
   ```

2. Check network connectivity, especially to Docker Hub and other required services

3. Refer to the [installation FAQs and troubleshooting guide](#7.1) for common issues and solutions

4. For network-related issues, search for solutions combining the error with "kubespray" as a keyword

Sources: [docs/manual/cluster-admin/installation-guide.md:354-366]()), [contrib/kubespray/requirement.sh:1-32]()

---

# Page: Configuration Files

# Configuration Files

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [contrib/kubespray/quick-start/services-configuration.yaml.template](contrib/kubespray/quick-start/services-configuration.yaml.template)
- [deployment/quick-start/services-configuration.yaml.template](deployment/quick-start/services-configuration.yaml.template)
- [docs/manual/cluster-admin/how-to-use-alert-system.md](docs/manual/cluster-admin/how-to-use-alert-system.md)
- [docs_zh_CN/manual/cluster-admin/how-to-use-alert-system.md](docs_zh_CN/manual/cluster-admin/how-to-use-alert-system.md)
- [examples/cluster-configuration/services-configuration.yaml](examples/cluster-configuration/services-configuration.yaml)
- [src/alert-manager/build/alert-handler.common.dockerfile](src/alert-manager/build/alert-handler.common.dockerfile)
- [src/alert-manager/build/build-pre.sh](src/alert-manager/build/build-pre.sh)
- [src/alert-manager/build/cert-expiration-checker.common.dockerfile](src/alert-manager/build/cert-expiration-checker.common.dockerfile)
- [src/alert-manager/build/cluster-utilization.common.dockerfile](src/alert-manager/build/cluster-utilization.common.dockerfile)
- [src/alert-manager/build/job-status-change-notification.common.dockerfile](src/alert-manager/build/job-status-change-notification.common.dockerfile)
- [src/alert-manager/build/nvidia-gpu-low-perf-fixer.common.dockerfile](src/alert-manager/build/nvidia-gpu-low-perf-fixer.common.dockerfile)
- [src/alert-manager/config/alert-manager.md](src/alert-manager/config/alert-manager.md)
- [src/alert-manager/config/alert-manager.yaml](src/alert-manager/config/alert-manager.yaml)
- [src/alert-manager/config/alert_manager.py](src/alert-manager/config/alert_manager.py)
- [src/alert-manager/deploy/alert-manager-configmap.yaml.template](src/alert-manager/deploy/alert-manager-configmap.yaml.template)
- [src/alert-manager/deploy/alert-manager-deployment.yaml.template](src/alert-manager/deploy/alert-manager-deployment.yaml.template)
- [src/alert-manager/deploy/service.yaml](src/alert-manager/deploy/service.yaml)
- [src/alert-manager/deploy/start.sh.template](src/alert-manager/deploy/start.sh.template)
- [src/alert-manager/deploy/stop.sh](src/alert-manager/deploy/stop.sh)
- [src/alert-manager/src/alert-handler/controllers/mail.js](src/alert-manager/src/alert-handler/controllers/mail.js)
- [src/alert-manager/src/alert-handler/index.js](src/alert-manager/src/alert-handler/index.js)
- [src/alert-manager/src/cert-expiration-checker/__init__.py](src/alert-manager/src/cert-expiration-checker/__init__.py)
- [src/alert-manager/src/cert-expiration-checker/pylintrc](src/alert-manager/src/cert-expiration-checker/pylintrc)
- [src/alert-manager/src/cert-expiration-checker/requirements.txt](src/alert-manager/src/cert-expiration-checker/requirements.txt)
- [src/alert-manager/src/cert-expiration-checker/send_alert.py](src/alert-manager/src/cert-expiration-checker/send_alert.py)
- [src/alert-manager/src/job-status-change-notification/.editorconfig](src/alert-manager/src/job-status-change-notification/.editorconfig)
- [src/alert-manager/src/job-status-change-notification/.eslintrc.js](src/alert-manager/src/job-status-change-notification/.eslintrc.js)
- [src/alert-manager/src/job-status-change-notification/controllers/alert.js](src/alert-manager/src/job-status-change-notification/controllers/alert.js)
- [src/alert-manager/src/job-status-change-notification/controllers/framework.js](src/alert-manager/src/job-status-change-notification/controllers/framework.js)
- [src/rest-server/src/config/index.js](src/rest-server/src/config/index.js)

</details>



This document details the configuration files in OpenPAI that control deployment, service behavior, and system settings. Configuration files are central to the installation, customization, and maintenance of an OpenPAI cluster.

## Core Configuration Files

OpenPAI uses YAML-based configuration files to control system behavior. The primary files are:

- `services-configuration.yaml` - Main configuration file for all services
- Template files (e.g., `services-configuration.yaml.template`) - Used during deployment
- Service-specific configuration maps (e.g., `alert-manager-configmap.yaml.template`)

```mermaid
graph TD
    A["services-configuration.yaml"] --> |"processed by"| B["paictl.py"]
    C["*.yaml.template"] --> |"rendered to"| D["Kubernetes ConfigMaps"]
    B --> |"generates"| D
    D --> |"configures"| E["OpenPAI Services"]
```

Sources: [contrib/kubespray/quick-start/services-configuration.yaml.template](), [examples/cluster-configuration/services-configuration.yaml](), [deployment/quick-start/services-configuration.yaml.template]()

## Configuration Structure

The main `services-configuration.yaml` file is organized into sections for individual services:

```mermaid
graph TD
    A["services-configuration.yaml"] --> B["cluster"]
    A --> C["rest-server"]
    A --> D["webportal"]
    A --> E["hivedscheduler"]
    A --> F["authentication"]
    A --> G["alert-manager"]
    A --> H["prometheus"]
    A --> I["pylon"]
    A --> J["Other services"]
    
    B --> B1["common: cluster-id, data-path"]
    B --> B2["docker-registry: namespace, domain"]
    
    C --> C1["default-pai-admin-username"]
    C --> C2["default-pai-admin-password"]
    
    G --> G1["port"]
    G --> G2["alert-handler"]
    G --> G3["customized-routes"]
    G --> G4["customized-receivers"]
```

Sources: [contrib/kubespray/quick-start/services-configuration.yaml.template:1-317]()

## Key Configuration Sections

### Cluster Configuration

The `cluster` section defines basic cluster settings and Docker registry configuration:

```yaml
cluster:
  common:
    cluster-id: pai
    cluster-type: k8s
    data-path: "/datastorage"
    
  docker-registry:
    namespace: openpai
    domain: docker.io
    tag: latest
    secret-name: pai-secret
```

Sources: [contrib/kubespray/quick-start/services-configuration.yaml.template:1-37]()

### REST Server Configuration

The `rest-server` section configures the REST API server:

```yaml
rest-server:
  default-pai-admin-username: admin
  default-pai-admin-password: admin-password
```

Sources: [contrib/kubespray/quick-start/services-configuration.yaml.template:64-70]()

### Authentication Configuration

The `authentication` section configures authentication methods and user group management:

```yaml
authentication:
  OIDC: false
  # OIDC settings when enabled
  
  group-manager:
    group-data-source: basic
    admin-group:
      groupname: admingroup
      description: "admin's group"
```

Sources: [contrib/kubespray/quick-start/services-configuration.yaml.template:130-196]()

## Alert System Configuration

The alert system is one of the most complex configuration areas in OpenPAI. It consists of several components that work together.

### Alert System Architecture

```mermaid
graph TD
    A["Prometheus"] --> |"fires alerts"| B["Alert Manager"]
    B --> |"routes to"| C["Alert Handler"]
    
    C --> D1["Email Actions"]
    C --> D2["Job Actions"]
    C --> D3["Node Actions"]
    
    E["Configuration Files"] --> |"configures"| F["Alert Rules"]
    E --> |"configures"| G["Routes"]
    E --> |"configures"| H["Receivers"]
    
    F --> A
    G --> B
    H --> C
```

Sources: [docs/manual/cluster-admin/how-to-use-alert-system.md:5-21]()

### Alert Configuration Components

The alert system has three main configuration components:

1. **Alert Rules** (in Prometheus configuration):
   ```yaml
   prometheus:
     customized-alerts: |
       groups:
       - name: customized-alerts
         rules:
         - alert: PAIJobGpuPercentLowerThan0_3For1h
           expr: avg(task_gpu_percent{virtual_cluster=~"default"}) by (job_name, username) < 0.3
           for: 1h
           labels:
             severity: warn
   ```

2. **Alert Routes** (in Alert Manager configuration):
   ```yaml
   alert-manager:
     customized-routes:
       routes:
       - receiver: pai-email-admin-user-and-stop-job
         match:
           alertname: PAIJobGpuPercentLowerThan0_3For1h
   ```

3. **Alert Receivers** (in Alert Manager configuration):
   ```yaml
   alert-manager:
     customized-receivers:
     - name: "pai-email-admin-user-and-stop-job"
       actions:
         email-admin:
         email-user:
           template: 'kill-low-efficiency-job-alert'
         stop-jobs:
         tag-jobs:
           tags:
           - 'stopped-by-alert-manager'
   ```

Sources: [contrib/kubespray/quick-start/services-configuration.yaml.template:215-255](), [docs/manual/cluster-admin/how-to-use-alert-system.md:35-53]()

### Alert Action Dependencies

Different alert actions have different configuration dependencies:

| Action | Requires `email-configs` | Requires `pai-bearer-token` |
|--------|--------------------------|----------------------------|
| cordon-nodes | No | No |
| email-admin | Yes | No |
| email-user | Yes | Yes |
| stop-jobs | No | Yes |
| tag-jobs | No | Yes |
| fix-nvidia-gpu-low-perf | No | No |

Sources: [src/alert-manager/config/alert_manager.py:77-83](), [docs/manual/cluster-admin/how-to-use-alert-system.md:112-128]()

### Email Configuration

To enable email notifications for alerts, configure the `email-configs` section:

```yaml
alert-manager:
  alert-handler:
    email-configs:
      admin-receiver: addr-of-admin-receiver@example.com
      smtp-host: smtp.office365.com
      smtp-port: 587
      smtp-from: alert-sender@example.com
      smtp-auth-username: alert-sender@example.com
      smtp-auth-password: password-for-alert-sender
```

Sources: [src/alert-manager/deploy/alert-manager-deployment.yaml.template:83-95](), [src/alert-manager/src/alert-handler/controllers/mail.js:25-33]()

## HiveD Scheduler Configuration

The `hivedscheduler` section configures the resource scheduler that manages GPU allocation:

```yaml
hivedscheduler:
  config: |
    physicalCluster:
      skuTypes:
        gpu-type:
          gpu: 1
          cpu: 5
          memory: 40Gi
      cellTypes:
        gpu-type-NODE:
          childCellType: gpu-type
          childCellNumber: 4
          isNodeLevel: true
    virtualClusters:
      default:
        virtualCells:
        - cellType: gpu-type-NODE
          cellNumber: 2
```

Sources: [contrib/kubespray/quick-start/services-configuration.yaml.template:78-126]()

## Configuration Deployment Process

The configuration deployment process involves updating configuration files and applying them to the cluster:

```mermaid
sequenceDiagram
    participant Admin as "Admin"
    participant PaiCTL as "paictl.py"
    participant K8s as "Kubernetes"
    participant Services as "OpenPAI Services"
    
    Admin->>PaiCTL: "./paictl.py service stop -n <service>"
    PaiCTL->>Services: "Stop service"
    
    Admin->>PaiCTL: "./paictl.py config push -p /cluster-configuration -m service"
    PaiCTL->>K8s: "Apply ConfigMaps"
    
    Admin->>PaiCTL: "./paictl.py service start -n <service>"
    PaiCTL->>Services: "Start service with new config"
```

Example for updating alert-manager configuration:

```bash
./paictl.py service stop -n alert-manager
./paictl.py config push -p /cluster-configuration -m service
./paictl.py service start -n alert-manager
```

Sources: [docs/manual/cluster-admin/how-to-use-alert-system.md:60-65]()

## Configuration Files Generated During Deployment

During deployment, template files are processed to generate actual configuration files. For example, the `alert-manager-configmap.yaml.template` is processed to create ConfigMaps in Kubernetes:

```mermaid
graph TD
    A["services-configuration.yaml"] --> |"values for"| B["template processing"]
    C["*.yaml.template files"] --> |"processed by"| B
    B --> D["Kubernetes ConfigMaps"]
    D --> |"mounted to"| E["Service Containers"]
```

Sources: [src/alert-manager/deploy/alert-manager-configmap.yaml.template](), [src/alert-manager/deploy/start.sh.template:20-41]()

## Prometheus Configuration

The `prometheus` section configures the monitoring system and alert rules:

```yaml
prometheus:
  port: 9091
  scrape_interval: 30
  customized-alerts: |
    groups:
    - name: customized-alerts
      rules:
      - alert: PAIJobGpuPercentLowerThan0_3For1h
        expr: avg(task_gpu_percent{virtual_cluster=~"default"}) by (job_name, username) < 0.3
        for: 1h
        labels:
          severity: warn
```

Sources: [contrib/kubespray/quick-start/services-configuration.yaml.template:260-275]()

## Handling Service-Specific Configuration Changes

To apply configuration changes to a specific service:

1. **Stop the service**:
   ```bash
   ./paictl.py service stop -n <service-name>
   ```

2. **Push the updated configuration**:
   ```bash
   ./paictl.py config push -p /cluster-configuration -m service
   ```

3. **Start the service**:
   ```bash
   ./paictl.py service start -n <service-name>
   ```

Sources: [docs/manual/cluster-admin/how-to-use-alert-system.md:199-206]()

## Common Configuration Scenarios

### Adding a Customized Alert

```yaml
prometheus:
  customized-alerts: |
    groups:
    - name: customized-alerts
      rules:
      - alert: PAIJobGpuPercentLowerThan0_3For1h
        expr: avg(task_gpu_percent{virtual_cluster=~"default"}) by (job_name, username) < 0.3
        for: 1h
        labels:
          severity: warn
        annotations:
          summary: "{% raw %}{{$labels.job_name}}{% endraw %} has a job gpu percent lower than 30% for 1 hour"
```

Sources: [docs/manual/cluster-admin/how-to-use-alert-system.md:40-53]()

### Configuring Alert Actions

```yaml
alert-manager:
  customized-receivers:
  - name: "pai-email-admin-user-and-stop-job"
    actions:
      email-admin:
      email-user:
        template: 'kill-low-efficiency-job-alert'
      stop-jobs:
      tag-jobs:
        tags:
        - 'stopped-by-alert-manager'
```

Sources: [docs/manual/cluster-admin/how-to-use-alert-system.md:160-171]()

### Setting Up OIDC Authentication

```yaml
authentication:
  OIDC: true
  OIDC-type: AAD
  
  AAD:
    wellKnownURL: https://login.microsoftonline.com/{tenantID}/v2.0/.well-known/openid-configuration
    tenantID: <your-tenant-id>
    clientID: <your-client-id>
    clientSecret: '<your-client-secret>'
```

Sources: [contrib/kubespray/quick-start/services-configuration.yaml.template:134-152]()

## Conclusion

OpenPAI's configuration files, particularly `services-configuration.yaml`, provide comprehensive control over all aspects of the system. Understanding these files is essential for deploying, customizing, and maintaining an OpenPAI cluster. This document has covered the key configuration sections, their purpose, and how to apply configuration changes.

For more details on service-specific configurations, refer to the documentation for individual services, such as the [Alert System](2.3).

---

# Page: System Architecture

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [RELEASE_NOTE.md](RELEASE_NOTE.md)
- [contrib/debug-tools/docs/remote-debug-pai-job_zh_CN.md](contrib/debug-tools/docs/remote-debug-pai-job_zh_CN.md)
- [contrib/kubespray/config/config.yaml](contrib/kubespray/config/config.yaml)
- [docs/manual/cluster-admin/installation-guide.md](docs/manual/cluster-admin/installation-guide.md)
- [docs_zh_CN/manual/cluster-admin/installation-guide.md](docs_zh_CN/manual/cluster-admin/installation-guide.md)
- [src/database-controller/src/write-merger/app.js](src/database-controller/src/write-merger/app.js)
- [src/rest-server/config/rest-server.md](src/rest-server/config/rest-server.md)
- [src/rest-server/config/rest-server.yaml](src/rest-server/config/rest-server.yaml)
- [src/rest-server/config/rest_server.py](src/rest-server/config/rest_server.py)
- [src/rest-server/deploy/rest-server.yaml.template](src/rest-server/deploy/rest-server.yaml.template)
- [src/rest-server/docs/swagger.yaml](src/rest-server/docs/swagger.yaml)
- [src/rest-server/package.json](src/rest-server/package.json)
- [src/rest-server/src/config/express.js](src/rest-server/src/config/express.js)
- [src/rest-server/src/config/launcher.js](src/rest-server/src/config/launcher.js)
- [src/rest-server/src/config/schedule-port.js](src/rest-server/src/config/schedule-port.js)
- [src/rest-server/src/controllers/internal/tail-log.js](src/rest-server/src/controllers/internal/tail-log.js)
- [src/rest-server/src/controllers/v2/job.js](src/rest-server/src/controllers/v2/job.js)
- [src/rest-server/src/controllers/v2/task.js](src/rest-server/src/controllers/v2/task.js)
- [src/rest-server/src/models/v2/job/index.js](src/rest-server/src/models/v2/job/index.js)
- [src/rest-server/src/models/v2/job/k8s.js](src/rest-server/src/models/v2/job/k8s.js)
- [src/rest-server/src/models/v2/job/log.js](src/rest-server/src/models/v2/job/log.js)
- [src/rest-server/src/models/v2/task.js](src/rest-server/src/models/v2/task.js)
- [src/rest-server/src/models/v2/utils/frameworkConverter.js](src/rest-server/src/models/v2/utils/frameworkConverter.js)
- [src/rest-server/src/models/v2/utils/name.js](src/rest-server/src/models/v2/utils/name.js)
- [src/rest-server/src/routes/internal/index.js](src/rest-server/src/routes/internal/index.js)
- [src/rest-server/src/routes/internal/tail-log.js](src/rest-server/src/routes/internal/tail-log.js)
- [src/rest-server/src/routes/v2/job.js](src/rest-server/src/routes/v2/job.js)
- [src/rest-server/src/utils/error.d.ts](src/rest-server/src/utils/error.d.ts)
- [src/rest-server/test/setup.js](src/rest-server/test/setup.js)
- [src/rest-server/yarn.lock](src/rest-server/yarn.lock)
- [tests/jenkins/test_rest_server_js_sdk.sh](tests/jenkins/test_rest_server_js_sdk.sh)
- [version/K8S.VERSION](version/K8S.VERSION)
- [version/PAI.VERSION](version/PAI.VERSION)

</details>



This document provides a comprehensive overview of OpenPAI's system architecture - a platform for running AI workloads on Kubernetes. It covers the core components, their interactions, and the underlying infrastructure that enables job submission, scheduling, execution, and monitoring.

## Overview

OpenPAI has evolved from a Yarn and Kubernetes-based architecture to a pure Kubernetes-based architecture since v1.0.0. This architecture provides better modularity, extensibility, and resource management capabilities.

```mermaid
flowchart TB
    subgraph "User Interfaces"
        WebPortal["Web Portal"]
        VSCode["VSCode Extension"]
    end

    subgraph "API Layer"
        RestServer["REST Server API<br>(Express.js)"]
    end

    subgraph "Core Services"
        K8sAPI["Kubernetes API"]
        FrameworkController["Framework Controller"]
        HivedScheduler["Hived Scheduler"]
        Runtime["OpenPAI Runtime"]
    end

    subgraph "Storage & Database"
        DB[(PostgreSQL)]
        Storage["Storage Services"]
    end

    subgraph "Monitoring & Alerting"
        Prometheus["Prometheus"]
        AlertManager["Alert Manager"]
    end

    WebPortal --> RestServer
    VSCode --> RestServer
    RestServer --> K8sAPI
    RestServer --> DB
    RestServer --> Storage
    K8sAPI --> FrameworkController
    K8sAPI --> HivedScheduler
    FrameworkController --> Runtime
    K8sAPI --> Prometheus
    Prometheus --> AlertManager
    AlertManager --> RestServer
```

Sources:
- [README.md:10-57]()
- [src/rest-server/src/config/express.js:1-54]()
- [src/rest-server/src/controllers/v2/job.js:1-40]()
- [src/rest-server/package.json:1-92]()

## Core Components

OpenPAI consists of several core components that work together to provide a complete AI platform:

### REST Server

The REST Server is the central API service that handles all client requests. It processes job submissions, manages user authentication, and communicates with the Kubernetes API.

The REST server is implemented as an Express.js application and exposes APIs for:
- Job management (submit, list, get, delete)
- User and authentication management
- Virtual cluster management
- Storage management
- Monitoring and alerting

```mermaid
flowchart TB
    subgraph "REST Server"
        API["API Routes (v1, v2)"]
        Controllers["Controllers"]
        Models["Models"]
        Middlewares["Middlewares"]
        JobProtocol["Job Protocol"]
    end

    subgraph "External Systems"
        K8s["Kubernetes API"]
        DB[(PostgreSQL)]
    end

    API --> Controllers
    Controllers --> Models
    Models --> K8s
    Models --> DB
    JobProtocol --> Models
    Middlewares --> Controllers
```

Sources:
- [src/rest-server/src/config/express.js:18-54]()
- [src/rest-server/src/controllers/v2/job.js:1-355]()
- [src/rest-server/src/routes/v2/job.js:1-108]()
- [src/rest-server/src/models/v2/job/k8s.js:1-150]()

### Framework Controller

The Framework Controller is a Kubernetes extension that orchestrates the execution of complex jobs with multiple task roles. It manages the lifecycle of jobs and handles retries, completions, and failures.

Key features:
- Supports gang scheduling
- Handles job retries
- Provides job status tracking
- Manages pod lifecycle

```mermaid
flowchart TB
    subgraph "Framework Controller"
        FrameworkAPI["Framework API"]
        FrameworkController["Controller Core"]
        TaskRoleMgr["Task Role Manager"]
        FrameworkStatus["Framework Status"]
    end

    subgraph "Kubernetes"
        K8sAPI["Kubernetes API"]
        Pods["Pods"]
    end

    RestServer["REST Server"] --> FrameworkAPI
    FrameworkAPI --> FrameworkController
    FrameworkController --> TaskRoleMgr
    TaskRoleMgr --> K8sAPI
    FrameworkController --> FrameworkStatus
    K8sAPI --> Pods
```

Sources:
- [src/rest-server/src/models/v2/job/k8s.js:351-805]()
- [README.md:40-42]()

### Hived Scheduler

Hived Scheduler is a specialized Kubernetes scheduler designed for deep learning workloads. It provides:
- GPU topology-aware scheduling
- Multi-level resource quota management (virtual clusters)
- Gang scheduling capabilities
- Support for heterogeneous hardware

```mermaid
flowchart TB
    subgraph "Hived Scheduler"
        CellTree["Cell Tree Hierarchy"]
        VCManager["Virtual Cluster Manager"]
        GangScheduler["Gang Scheduler"]
        ResourceAlloc["Resource Allocator"]
    end

    K8sAPI["Kubernetes API"] --> CellTree
    GangScheduler --> ResourceAlloc
    VCManager --> ResourceAlloc
    CellTree --> ResourceAlloc
    ResourceAlloc --> K8sAPI
```

Sources:
- [src/rest-server/src/models/v2/job/k8s.js:650-674]()
- [README.md:43-45]()
- [docs/manual/cluster-admin/installation-guide.md:70-74]()

### OpenPAI Runtime

OpenPAI Runtime is responsible for setting up the execution environment for jobs within containers. It:
- Prepares the running environment for tasks
- Sets up storage mounts
- Handles logging and monitoring
- Manages the lifecycle of the actual user code

```mermaid
flowchart TB
    subgraph "Runtime"
        InitContainer["Init Container"]
        RuntimeContainer["Runtime Container"]
        LogCollection["Log Collection"]
        StorageMount["Storage Mounting"]
    end

    UserCode["User Job Code"] --> RuntimeContainer
    InitContainer --> RuntimeContainer
    RuntimeContainer --> LogCollection
    StorageMount --> RuntimeContainer
```

Sources:
- [src/rest-server/src/models/v2/job/k8s.js:435-476]()
- [src/rest-server/src/models/v2/job/k8s.js:479-534]()
- [README.md:47-49]()

## Job Lifecycle

The job lifecycle in OpenPAI involves several stages from submission to completion:

```mermaid
sequenceDiagram
    participant User as "User"
    participant WebPortal as "Web Portal"
    participant RestServer as "REST Server"
    participant FrameworkController as "Framework Controller"
    participant HivedScheduler as "Hived Scheduler"
    participant K8s as "Kubernetes API"
    participant Runtime as "OpenPAI Runtime"
    
    User->>WebPortal: Submit job via UI
    WebPortal->>RestServer: POST /api/v2/jobs
    RestServer->>RestServer: Validate protocol
    
    RestServer->>K8s: Create framework, secrets
    Note over RestServer,K8s: job.update() creates framework description
    
    K8s->>FrameworkController: Watch framework resources
    FrameworkController->>HivedScheduler: Request scheduling
    HivedScheduler->>K8s: Create pods with resource allocation
    
    K8s->>Runtime: Initialize job container
    Runtime->>Runtime: Setup environment
    Runtime->>Runtime: Execute user code
    
    Runtime->>K8s: Update status
    K8s->>FrameworkController: Update framework status
    FrameworkController->>K8s: Update framework object
    
    User->>WebPortal: Query job status
    WebPortal->>RestServer: GET /api/v2/jobs/:name
    RestServer->>K8s: Get framework status
    K8s->>RestServer: Return framework status
    RestServer->>WebPortal: Return job status
    WebPortal->>User: Display job status
```

Sources:
- [src/rest-server/src/controllers/v2/job.js:177-229]()
- [src/rest-server/src/models/v2/job/k8s.js:679-805]()
- [src/rest-server/src/models/v2/job/k8s.js:351-618]()

## System Components and Data Flow

### REST Server API Flow

```mermaid
flowchart TB
    subgraph "Client Requests"
        WebPortal["Web Portal"]
        VSCode["VSCode Extension"]
        CLI["Command Line Tool"]
    end
    
    subgraph "REST Server"
        Express["Express.js App"]
        Routes["Routes"]
        Controllers["Controllers"]
        Models["Data Models"]
        Middlewares["Middlewares (Auth, Protocol)"]
    end
    
    subgraph "Storage Systems"
        K8sAPI["Kubernetes API"]
        Database[(PostgreSQL)]
        AzureStorage["Azure Storage/Log Service"]
    end
    
    WebPortal --> Express
    VSCode --> Express
    CLI --> Express
    
    Express --> Routes
    Routes --> Middlewares
    Middlewares --> Controllers
    Controllers --> Models
    
    Models --> K8sAPI
    Models --> Database
    Models --> AzureStorage
```

Sources:
- [src/rest-server/src/config/express.js:1-54]()
- [src/rest-server/src/routes/v2/job.js:1-108]()
- [src/rest-server/src/controllers/v2/job.js:1-355]()
- [src/rest-server/src/models/v2/job/k8s.js:1-100]()

### Job Submission and Execution Flow

```mermaid
flowchart LR
    subgraph "Job Submission Flow"
        UserProtocol["User Job Protocol"]
        ProtocolValid["Protocol Validation"]
        FrameworkGen["Framework Generation"]
        K8sObjects["K8s Objects Creation"]
    end
    
    subgraph "Execution Flow"
        FCWatch["Framework Controller Watch"]
        Scheduling["Scheduling (HivedScheduler)"]
        PodCreation["Pod Creation"]
        ContainerRun["Container Runtime Execution"]
    end
    
    subgraph "Status Flow"
        PodStatus["Pod Status Updates"]
        FCStatus["Framework Status Updates"]
        DBStatus["Database Status Records"]
        UserQuery["User Status Query"]
    end
    
    UserProtocol --> ProtocolValid
    ProtocolValid --> FrameworkGen
    FrameworkGen --> K8sObjects
    
    K8sObjects --> FCWatch
    FCWatch --> Scheduling
    Scheduling --> PodCreation
    PodCreation --> ContainerRun
    
    ContainerRun --> PodStatus
    PodStatus --> FCStatus
    FCStatus --> DBStatus
    DBStatus --> UserQuery
```

Sources:
- [src/rest-server/src/controllers/v2/job.js:185-205]()
- [src/rest-server/src/models/v2/job/k8s.js:679-805]()
- [src/rest-server/src/models/v2/job/k8s.js:962-1026]()

## Storage and Logging Architecture

OpenPAI provides storage and logging capabilities for jobs:

```mermaid
flowchart TB
    subgraph "Job Storage Management"
        StorageConfig["Storage Configuration"]
        StorageMount["Storage Volume Mounting"]
        DataPersistence["Data Persistence"]
    end
    
    subgraph "Logging System"
        TaskLog["Task Log Generation"]
        LogManagerAPI["Log Manager API"]
        AzureBlobStorage["Azure Blob Storage"]
        LogCollection["Log Collection Service"]
    end
    
    subgraph "User Access"
        WebPortalLog["Web Portal Log View"]
        RestServerAPI["REST Server Log API"]
    end
    
    StorageConfig --> StorageMount
    StorageMount --> DataPersistence
    
    TaskLog --> LogCollection
    LogCollection --> LogManagerAPI
    LogManagerAPI --> AzureBlobStorage
    
    WebPortalLog --> RestServerAPI
    RestServerAPI --> LogManagerAPI
    RestServerAPI --> AzureBlobStorage
```

Sources:
- [src/rest-server/src/models/v2/job/k8s.js:599-617]()
- [src/rest-server/src/models/v2/job/log.js:1-90]()
- [src/rest-server/src/controllers/v2/job.js:320-341]()

## Monitoring and Alerting Architecture

OpenPAI includes monitoring and alerting capabilities:

```mermaid
flowchart TB
    subgraph "Monitoring Components"
        Prometheus["Prometheus"]
        NodeExporter["Node Exporter"]
        K8sMetrics["Kubernetes Metrics"]
    end
    
    subgraph "Alerting System"
        AlertManager["Alert Manager"]
        AlertRules["Alert Rules"]
        NotificationChannels["Notification Channels"]
    end
    
    subgraph "User-facing Alerts"
        RestServer["REST Server API"]
        WebPortal["Web Portal UI"]
        Email["Email Notifications"]
    end
    
    NodeExporter --> Prometheus
    K8sMetrics --> Prometheus
    Prometheus --> AlertRules
    AlertRules --> AlertManager
    AlertManager --> NotificationChannels
    NotificationChannels --> Email
    NotificationChannels --> RestServer
    RestServer --> WebPortal
```

Sources:
- [src/rest-server/src/config/launcher.js:132-138]()
- [src/rest-server/config/rest-server.yaml:41-46]()
- [src/rest-server/deploy/rest-server.yaml.template:151-152]()

## Integration with Kubernetes

OpenPAI is deeply integrated with Kubernetes:

```mermaid
flowchart TB
    subgraph "OpenPAI Components"
        RestServer["REST Server"]
        FrameworkController["Framework Controller"]
        HivedScheduler["Hived Scheduler"]
    end
    
    subgraph "Kubernetes Resources"
        K8sAPI["Kubernetes API Server"]
        Framework["Framework CRD"]
        Pods["Pods"]
        Secrets["Secrets"]
        ConfigMaps["ConfigMaps"]
        PV["Persistent Volumes"]
    end
    
    RestServer -->|"createFramework()"| K8sAPI
    RestServer -->|"createSecret()"| K8sAPI
    K8sAPI --> Framework
    FrameworkController -->|"watches"| Framework
    FrameworkController -->|"creates"| Pods
    HivedScheduler -->|"schedules"| Pods
    Pods -->|"uses"| Secrets
    Pods -->|"uses"| ConfigMaps
    Pods -->|"mounts"| PV
```

Sources:
- [src/rest-server/src/models/v2/job/k8s.js:694-805]()
- [src/rest-server/src/models/v2/job/k8s.js:822-885]()
- [src/rest-server/deploy/rest-server.yaml.template:18-188]()

## Database Schema

OpenPAI uses PostgreSQL for storing job information, user data, and other persistent information:

| Table | Description | Key Columns |
|-------|-------------|-------------|
| Framework | Stores job framework information | name, username, jobName, state, subState, executionType |
| FrameworkHistory | Stores historical job attempts | frameworkName, attemptIndex, snapshot |
| Tag | Stores tags associated with jobs | name, frameworkName |
| User | Stores user information | username, password, admin, email |
| Group | Stores group information | groupname, description |
| Namespace | Stores virtual cluster information | name, description |
| Storage | Stores storage configuration | name, mountPath, share |

Sources:
- [src/rest-server/src/models/v2/job/k8s.js:933-961]()
- [src/rest-server/package.json:58-61]()
- [src/rest-server/src/config/launcher.js:98-101]()

## Security and Authentication

OpenPAI supports multiple authentication methods:

```mermaid
flowchart TB
    subgraph "Authentication Types"
        BasicAuth["Basic Authentication"]
        OIDCAuth["OIDC Authentication"]
    end
    
    subgraph "Token Management"
        JWTGen["JWT Token Generation"]
        TokenStore["Token Storage"]
        TokenValidation["Token Validation"]
    end
    
    subgraph "API Security"
        Middleware["Auth Middleware"]
        RateLimit["Rate Limiting"]
        Authorization["Authorization Check"]
    end
    
    BasicAuth --> JWTGen
    OIDCAuth --> JWTGen
    JWTGen --> TokenStore
    TokenStore --> TokenValidation
    TokenValidation --> Middleware
    Middleware --> Authorization
    RateLimit --> Middleware
```

Sources:
- [src/rest-server/docs/swagger.yaml:77-278]()
- [src/rest-server/config/rest-server.yaml:25-35]()
- [src/rest-server/deploy/rest-server.yaml.template:98-120]()

## Conclusion

OpenPAI has a modular architecture built on Kubernetes that enables efficient management and execution of AI workloads. The REST Server provides the central API interface, while specialized components like Framework Controller and Hived Scheduler handle job orchestration and resource allocation. Storage, logging, monitoring, and security systems are integrated to provide a complete platform for AI development and execution.

---

# Page: Core Components

# Core Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [RELEASE_NOTE.md](RELEASE_NOTE.md)
- [contrib/debug-tools/docs/remote-debug-pai-job_zh_CN.md](contrib/debug-tools/docs/remote-debug-pai-job_zh_CN.md)
- [contrib/kubespray/config/config.yaml](contrib/kubespray/config/config.yaml)
- [contrib/submit-job-v2/README.md](contrib/submit-job-v2/README.md)
- [contrib/submit-job-v2/package.json](contrib/submit-job-v2/package.json)
- [contrib/submit-job-v2/src/App/ProtocolForm.tsx](contrib/submit-job-v2/src/App/ProtocolForm.tsx)
- [contrib/submit-job-v2/src/App/TensorBoard.tsx](contrib/submit-job-v2/src/App/TensorBoard.tsx)
- [contrib/submit-job-v2/src/index.ts](contrib/submit-job-v2/src/index.ts)
- [contrib/submit-job-v2/webpack.config.js](contrib/submit-job-v2/webpack.config.js)
- [contrib/submit-job-v2/yarn.lock](contrib/submit-job-v2/yarn.lock)
- [docs/manual/cluster-admin/installation-guide.md](docs/manual/cluster-admin/installation-guide.md)
- [docs_zh_CN/manual/cluster-admin/installation-guide.md](docs_zh_CN/manual/cluster-admin/installation-guide.md)
- [src/database-controller/src/write-merger/app.js](src/database-controller/src/write-merger/app.js)
- [src/rest-server/config/rest-server.md](src/rest-server/config/rest-server.md)
- [src/rest-server/config/rest-server.yaml](src/rest-server/config/rest-server.yaml)
- [src/rest-server/config/rest_server.py](src/rest-server/config/rest_server.py)
- [src/rest-server/deploy/rest-server.yaml.template](src/rest-server/deploy/rest-server.yaml.template)
- [src/rest-server/docs/swagger.yaml](src/rest-server/docs/swagger.yaml)
- [src/rest-server/package.json](src/rest-server/package.json)
- [src/rest-server/src/config/express.js](src/rest-server/src/config/express.js)
- [src/rest-server/src/config/launcher.js](src/rest-server/src/config/launcher.js)
- [src/rest-server/src/config/schedule-port.js](src/rest-server/src/config/schedule-port.js)
- [src/rest-server/src/controllers/internal/tail-log.js](src/rest-server/src/controllers/internal/tail-log.js)
- [src/rest-server/src/controllers/v2/job.js](src/rest-server/src/controllers/v2/job.js)
- [src/rest-server/src/controllers/v2/task.js](src/rest-server/src/controllers/v2/task.js)
- [src/rest-server/src/models/v2/job/index.js](src/rest-server/src/models/v2/job/index.js)
- [src/rest-server/src/models/v2/job/k8s.js](src/rest-server/src/models/v2/job/k8s.js)
- [src/rest-server/src/models/v2/job/log.js](src/rest-server/src/models/v2/job/log.js)
- [src/rest-server/src/models/v2/task.js](src/rest-server/src/models/v2/task.js)
- [src/rest-server/src/models/v2/utils/frameworkConverter.js](src/rest-server/src/models/v2/utils/frameworkConverter.js)
- [src/rest-server/src/models/v2/utils/name.js](src/rest-server/src/models/v2/utils/name.js)
- [src/rest-server/src/routes/internal/index.js](src/rest-server/src/routes/internal/index.js)
- [src/rest-server/src/routes/internal/tail-log.js](src/rest-server/src/routes/internal/tail-log.js)
- [src/rest-server/src/routes/v2/job.js](src/rest-server/src/routes/v2/job.js)
- [src/rest-server/src/utils/error.d.ts](src/rest-server/src/utils/error.d.ts)
- [src/rest-server/test/setup.js](src/rest-server/test/setup.js)
- [src/rest-server/yarn.lock](src/rest-server/yarn.lock)
- [src/webportal/config/webpack.common.js](src/webportal/config/webpack.common.js)
- [src/webportal/package.json](src/webportal/package.json)
- [src/webportal/yarn.lock](src/webportal/yarn.lock)
- [tests/jenkins/test_rest_server_js_sdk.sh](tests/jenkins/test_rest_server_js_sdk.sh)
- [version/K8S.VERSION](version/K8S.VERSION)
- [version/PAI.VERSION](version/PAI.VERSION)

</details>



This page provides a detailed technical overview of the core components that make up the OpenPAI platform. It describes the main architectural components, their relationships, and how they work together to provide a comprehensive platform for AI workloads on Kubernetes.

## Architecture Overview

OpenPAI is a platform for AI that has evolved from a Yarn-based architecture to a pure Kubernetes-based architecture since v1.0.0. The platform consists of several core components that work together to provide a comprehensive solution for managing AI workloads.

```mermaid
graph TD
    User["User"] --> WebPortal["Web Portal"]
    User --> VSCode["VSCode Extension"]
    WebPortal --> RestAPI["REST Server API"]
    VSCode --> RestAPI
    RestAPI --> K8sAPI["Kubernetes API"]
    RestAPI --> DB[("Database (PostgreSQL)")]
    
    subgraph "Core Components"
        K8sAPI --> FC["Framework Controller"]
        K8sAPI --> HS["Hived Scheduler"]
        K8sAPI --> Runtime["OpenPAI Runtime"]
    end
    
    FC --> Pods["Job Pods"]
    HS --> Pods
    Runtime --> Pods
```

*Diagram: High-level component architecture of OpenPAI*

Sources:
- [README.md:16-57]()
- [docs/manual/cluster-admin/installation-guide.md:1-89]()

## REST Server

The REST Server is a central component that provides RESTful APIs for interacting with OpenPAI. It handles requests from clients (Web Portal and VSCode Extension) and translates them into operations on the Kubernetes cluster.

### Key Features

- **Job Management**: Submit, list, get, stop, and delete jobs
- **User Authentication**: Basic and OIDC authentication methods
- **User and Group Management**: Manage users, groups, and permissions
- **Virtual Cluster Management**: Create and manage virtual clusters for resource isolation
- **Storage Management**: Manage shared storage for jobs

### Implementation Details

The REST server is implemented in Node.js and Express. It follows a modular architecture with controllers, models, and middleware.

```mermaid
graph TD
    subgraph "REST Server"
        API["API Endpoints"] --> Controllers["Controllers"]
        Controllers --> Models["Models"]
        Models --> K8sAPI["Kubernetes API Client"]
        Models --> DB["Database Client"]
    end
    
    K8sAPI --> K8s["Kubernetes API Server"]
    DB --> PostgreSQL["PostgreSQL Database"]
```

*Diagram: REST Server internal architecture*

Sources:
- [src/rest-server/package.json:1-93]()
- [src/rest-server/src/controllers/v2/job.js:1-323]()
- [src/rest-server/src/models/v2/job/k8s.js:1-100]()
- [src/rest-server/src/routes/v2/job.js:1-50]()
- [src/rest-server/src/config/express.js:1-150]()

### API Endpoints

The REST server provides a comprehensive set of API endpoints for managing various aspects of the OpenPAI platform.

| API Category | Description | Key Endpoints |
|--------------|-------------|--------------|
| Authentication | User login/logout | `/api/v2/authn/basic/login`, `/api/v2/authn/oidc/login` |
| Job | Job lifecycle management | `/api/v2/jobs`, `/api/v2/jobs/:jobName`, `/api/v2/jobs/:jobName/executionType` |
| User | User management | `/api/v2/users`, `/api/v2/users/:username` |
| Virtual Cluster | Virtual cluster management | `/api/v2/virtual-clusters`, `/api/v2/virtual-clusters/:vcName` |
| Storage | Storage management | `/api/v2/storages`, `/api/v2/storages/:storageName` |

Sources:
- [src/rest-server/docs/swagger.yaml:1-450]()

## Framework Controller

Framework Controller is a Kubernetes extension for orchestrating stateful applications with instance type requirements. In OpenPAI, it's responsible for managing the lifecycle of job frameworks.

### Key Features

- **Job Orchestration**: Creates and manages Kubernetes pods for job execution
- **Task Role Management**: Handles multiple task roles within a job
- **Retry Mechanisms**: Implements sophisticated retry policies for failed tasks
- **Status Tracking**: Maintains and reports detailed job status information

```mermaid
graph TD
    subgraph "Framework Controller"
        FCCore["Framework Controller Core"] --> FrameworkStore["Framework Store"]
        FCCore --> PodController["Pod Controller"]
        PodController --> PodStore["Pod Store"]
    end
    
    RestAPI["REST Server"] --> FCCore
    PodController --> K8sPods["Kubernetes Pods"]
```

*Diagram: Framework Controller architecture*

Sources:
- [README.md:40-42]()
- [README.md:157-157]()
- [src/rest-server/src/models/v2/job/k8s.js:351-677]()

### Job Lifecycle Management

Framework Controller handles the job lifecycle through a series of states:

1. **AttemptCreationPending**: Framework is being created
2. **AttemptCreationRequested**: Framework creation has been requested
3. **AttemptPreparing**: Resources are being prepared
4. **AttemptRunning**: Job is running
5. **AttemptDeletionPending**: Job is being deleted
6. **AttemptDeletionRequested**: Job deletion has been requested
7. **AttemptDeleting**: Job is being deleted
8. **AttemptCompleted**: Job has completed (successfully or unsuccessfully)

Sources:
- [src/rest-server/src/models/v2/job/k8s.js:154-349]()
- [src/rest-server/src/models/v2/utils/frameworkConverter.js:1-100]()

## Hived Scheduler

Hived Scheduler is a Kubernetes scheduler extension for hierarchical resource management in AI clusters. It provides advanced scheduling capabilities beyond what the default Kubernetes scheduler offers.

### Key Features

- **Hierarchical Resource Management**: Organizes resources in a tree-like structure
- **Virtual Clusters**: Provides resource isolation through virtual clusters
- **Topology-aware Scheduling**: Optimizes job placement based on hardware topology
- **Gang Scheduling**: Ensures all tasks of a job start together
- **GPU Allocation**: Sophisticated management of GPU resources

```mermaid
graph TD
    subgraph "Hived Scheduler"
        SchedulerExtender["Scheduler Extender"] --> CellTree["Cell Tree"]
        SchedulerExtender --> AffinityGroups["Affinity Groups"]
        SchedulerExtender --> SchedulingAlgorithm["Scheduling Algorithm"]
    end
    
    K8sScheduler["Kubernetes Scheduler"] --> SchedulerExtender
    SchedulerExtender --> K8sAPI["Kubernetes API"]
```

*Diagram: Hived Scheduler architecture*

Sources:
- [README.md:43-45]()
- [README.md:158-158]()
- [src/rest-server/src/config/launcher.js:22-77]()
- [src/rest-server/src/models/v2/job/k8s.js:646-674]()

### Virtual Clusters

Hived Scheduler organizes resources into virtual clusters to provide isolation and quota management:

| Feature | Description |
|---------|-------------|
| Cell Structure | Resources are organized in a hierarchical tree of cells |
| Resource Types | Supports CPU, GPU, and other compute resources |
| Affinity Groups | Groups resources based on hardware topology for optimal performance |
| Preemption | Supports preemptive scheduling for priority jobs |

Sources:
- [docs/manual/cluster-admin/installation-guide.md:70-74]()

## OpenPAI Runtime

OpenPAI Runtime is responsible for setting up the execution environment for jobs and managing the job execution process.

### Key Features

- **Environment Setup**: Prepares container environments for job execution
- **Task Execution**: Runs user-specified commands in containers
- **Resource Allocation**: Allocates resources (CPU, memory, GPU, etc.) to tasks
- **Log Management**: Collects and manages job logs
- **Storage Mounting**: Mounts shared storage into job containers

```mermaid
graph TD
    subgraph "OpenPAI Runtime"
        RuntimeCore["Runtime Core"] --> InitContainer["Init Container"]
        RuntimeCore --> AppContainer["App Container"]
    end
    
    FrameworkController["Framework Controller"] --> RuntimeCore
    InitContainer --> UserScript["User Script"]
    AppContainer --> UserCommand["User Command"]
    AppContainer --> StorageMount["Storage Mount"]
```

*Diagram: OpenPAI Runtime architecture*

Sources:
- [README.md:47-49]()
- [README.md:160-160]()
- [src/rest-server/src/models/v2/job/k8s.js:435-459]()
- [src/rest-server/src/models/v2/job/k8s.js:479-535]()

### Container Setup

The runtime creates two containers for each task:

1. **Init Container**: Sets up the environment, downloads necessary files, and prepares the task
2. **App Container**: Runs the actual user command with the allocated resources

This two-container approach provides a clean separation between setup and execution.

Sources:
- [src/rest-server/src/models/v2/job/k8s.js:435-459]()
- [src/rest-server/src/models/v2/job/k8s.js:479-535]()

## Web Portal

The Web Portal provides a user-friendly interface for interacting with OpenPAI. It allows users to submit jobs, monitor job status, and manage resources.

### Key Features

- **Job Submission**: Interface for submitting jobs with various parameters
- **Job Monitoring**: Dashboard for monitoring job status and performance
- **Cluster Overview**: Visualization of cluster resource usage
- **User Management**: Interface for user and group management
- **Storage Management**: Interface for managing shared storage

```mermaid
graph TD
    subgraph "Web Portal"
        WebUI["Web UI"] --> JobSubmission["Job Submission Page"]
        WebUI --> JobList["Job List Page"]
        WebUI --> Dashboard["Dashboard"]
        WebUI --> ClusterAdmin["Cluster Admin"]
    end
    
    JobSubmission --> RestAPI["REST Server API"]
    JobList --> RestAPI
    Dashboard --> RestAPI
    ClusterAdmin --> RestAPI
```

*Diagram: Web Portal architecture*

Sources:
- [src/webportal/package.json:1-143]()
- [README.md:17-27]()

## Job Lifecycle Flow

The following diagram illustrates the complete job lifecycle in OpenPAI, showing how the different components interact:

```mermaid
sequenceDiagram
    participant User
    participant WebPortal
    participant RestServer as "REST Server"
    participant FrameworkController as "Framework Controller"
    participant HivedScheduler as "Hived Scheduler"
    participant Runtime as "OpenPAI Runtime"
    participant K8sPods as "Kubernetes Pods"
    
    User->>WebPortal: Submit job
    WebPortal->>RestServer: POST /api/v2/jobs
    RestServer->>RestServer: Validate job protocol
    RestServer->>FrameworkController: Create Framework
    FrameworkController->>HivedScheduler: Schedule Framework
    HivedScheduler->>FrameworkController: Resource allocation
    FrameworkController->>K8sPods: Create Pods
    K8sPods->>Runtime: Execute job
    
    loop Job Monitoring
        User->>WebPortal: View job status
        WebPortal->>RestServer: GET /api/v2/jobs/:name
        RestServer->>FrameworkController: Get Framework status
        FrameworkController-->>RestServer: Framework status
        RestServer-->>WebPortal: Job status
        WebPortal-->>User: Display status
    end
    
    K8sPods->>Runtime: Job completion/failure
    Runtime->>FrameworkController: Update status
    FrameworkController->>RestServer: Status update
    RestServer->>WebPortal: Status update
    WebPortal->>User: Final job status
```

*Diagram: Job lifecycle flow in OpenPAI*

Sources:
- [src/rest-server/src/models/v2/job/k8s.js:679-880]()
- [src/rest-server/src/controllers/v2/job.js:27-323]()

## Component Dependencies

The following table summarizes the dependencies between the core components:

| Component | Depends On | Description |
|-----------|------------|-------------|
| Web Portal | REST Server | Uses REST APIs to interact with the cluster |
| REST Server | Kubernetes API, PostgreSQL | Manages jobs through Kubernetes API and stores data in PostgreSQL |
| Framework Controller | Kubernetes API | Extends Kubernetes with framework management capabilities |
| Hived Scheduler | Kubernetes Scheduler | Extends Kubernetes scheduler with hierarchical resource management |
| OpenPAI Runtime | Kubernetes Pods | Runs in Kubernetes pods to execute user jobs |

Sources:
- [README.md:153-163]()
- [src/rest-server/src/models/v2/job/k8s.js:1-100]()

## Deployment Architecture

In a typical deployment, OpenPAI components are deployed as Kubernetes services across master and worker nodes:

```mermaid
graph TD
    subgraph "Master Node"
        K8sMaster["Kubernetes Master Components"]
        RestServer["REST Server"]
        WebPortal["Web Portal"]
        FrameworkController["Framework Controller"]
        HivedScheduler["Hived Scheduler"]
    end
    
    subgraph "Worker Nodes"
        K8sWorker["Kubernetes Worker Components"]
        JobPods["Job Pods"]
        RuntimePods["Runtime Pods"]
    end
    
    DevBox["Development Box"] -->|Deploys| Master
    DevBox -->|Deploys| Worker
    
    RestServer --> K8sMaster
    FrameworkController --> K8sMaster
    HivedScheduler --> K8sMaster
    K8sMaster --> K8sWorker
    K8sWorker --> JobPods
    K8sWorker --> RuntimePods
```

*Diagram: Deployment architecture of OpenPAI*

Sources:
- [docs/manual/cluster-admin/installation-guide.md:9-74]()
- [src/rest-server/deploy/rest-server.yaml.template:1-157]()

## Conclusion

The core components of OpenPAI work together to provide a comprehensive platform for AI workloads. The REST Server provides the API interface, the Web Portal offers a user-friendly UI, the Framework Controller orchestrates jobs, the Hived Scheduler manages resources, and the OpenPAI Runtime executes jobs. This architecture leverages Kubernetes while adding specialized components for AI workload management.

---

# Page: Job Lifecycle

# Job Lifecycle

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/database-controller/src/write-merger/app.js](src/database-controller/src/write-merger/app.js)
- [src/frameworkcontroller/deploy/frameworkcontroller-config.yaml.template](src/frameworkcontroller/deploy/frameworkcontroller-config.yaml.template)
- [src/frameworkcontroller/deploy/frameworkcontroller.yaml.template](src/frameworkcontroller/deploy/frameworkcontroller.yaml.template)
- [src/frameworkcontroller/deploy/refresh.sh](src/frameworkcontroller/deploy/refresh.sh)
- [src/k8s-job-exit-spec/config/k8s-job-exit-spec.yaml](src/k8s-job-exit-spec/config/k8s-job-exit-spec.yaml)
- [src/openpai-runtime/build/openpai-runtime.k8s.dockerfile](src/openpai-runtime/build/openpai-runtime.k8s.dockerfile)
- [src/openpai-runtime/deploy/runtime-exit-spec.yaml.template](src/openpai-runtime/deploy/runtime-exit-spec.yaml.template)
- [src/rest-server/config/rest-server.md](src/rest-server/config/rest-server.md)
- [src/rest-server/config/rest-server.yaml](src/rest-server/config/rest-server.yaml)
- [src/rest-server/config/rest_server.py](src/rest-server/config/rest_server.py)
- [src/rest-server/deploy/rest-server.yaml.template](src/rest-server/deploy/rest-server.yaml.template)
- [src/rest-server/docs/swagger.yaml](src/rest-server/docs/swagger.yaml)
- [src/rest-server/package.json](src/rest-server/package.json)
- [src/rest-server/src/config/express.js](src/rest-server/src/config/express.js)
- [src/rest-server/src/config/launcher.js](src/rest-server/src/config/launcher.js)
- [src/rest-server/src/config/schedule-port.js](src/rest-server/src/config/schedule-port.js)
- [src/rest-server/src/controllers/internal/tail-log.js](src/rest-server/src/controllers/internal/tail-log.js)
- [src/rest-server/src/controllers/v2/job.js](src/rest-server/src/controllers/v2/job.js)
- [src/rest-server/src/controllers/v2/task.js](src/rest-server/src/controllers/v2/task.js)
- [src/rest-server/src/models/v2/job/index.js](src/rest-server/src/models/v2/job/index.js)
- [src/rest-server/src/models/v2/job/k8s.js](src/rest-server/src/models/v2/job/k8s.js)
- [src/rest-server/src/models/v2/job/log.js](src/rest-server/src/models/v2/job/log.js)
- [src/rest-server/src/models/v2/task.js](src/rest-server/src/models/v2/task.js)
- [src/rest-server/src/models/v2/utils/frameworkConverter.js](src/rest-server/src/models/v2/utils/frameworkConverter.js)
- [src/rest-server/src/models/v2/utils/name.js](src/rest-server/src/models/v2/utils/name.js)
- [src/rest-server/src/routes/internal/index.js](src/rest-server/src/routes/internal/index.js)
- [src/rest-server/src/routes/internal/tail-log.js](src/rest-server/src/routes/internal/tail-log.js)
- [src/rest-server/src/routes/v2/job.js](src/rest-server/src/routes/v2/job.js)
- [src/rest-server/src/utils/error.d.ts](src/rest-server/src/utils/error.d.ts)
- [src/rest-server/test/setup.js](src/rest-server/test/setup.js)
- [src/rest-server/yarn.lock](src/rest-server/yarn.lock)
- [src/webportal/src/app/job/job-view/fabric/JobList/utils.js](src/webportal/src/app/job/job-view/fabric/JobList/utils.js)
- [tests/jenkins/test_rest_server_js_sdk.sh](tests/jenkins/test_rest_server_js_sdk.sh)

</details>



This document explains the complete lifecycle of a job in OpenPAI from submission to completion. It covers how jobs are submitted, scheduled, executed, monitored, and terminated in the OpenPAI platform. For API-specific details, refer to [API Reference](#4.1).

## Overview of Job Lifecycle

The job lifecycle in OpenPAI follows a well-defined path through several components of the platform, with jobs transitioning through various states from creation to completion.

```mermaid
flowchart TB
    Submit["Job Submission"]
    Validate["Job Validation"]
    Database["Database Storage"]
    Create["Framework Creation"]
    Schedule["Resource Scheduling"]
    Launch["Container Launch"]
    Execute["Job Execution"]
    Monitor["State Monitoring"]
    Complete["Job Completion"]
    Cleanup["Resource Cleanup"]

    Submit --> Validate
    Validate --> Database
    Database --> Create
    Create --> Schedule
    Schedule --> Launch
    Launch --> Execute
    Execute --> Monitor
    Monitor -->|Running| Monitor
    Monitor -->|Completed| Complete
    Complete --> Cleanup
```

Sources:
- [src/rest-server/src/models/v2/job/k8s.js:100-350]()
- [src/rest-server/src/controllers/v2/job.js:177-183]()
- [src/rest-server/src/routes/v2/job.js:30-55]()

## Job States and Transitions

Jobs in OpenPAI can exist in various states. Understanding these states and the transitions between them is essential for tracking and managing job execution.

```mermaid
stateDiagram-v2
    [*] --> "Waiting"
    "Waiting" --> "Running": Resource allocation successful
    "Waiting" --> "Failed": Resource allocation failed
    "Running" --> "Succeeded": Job completed successfully
    "Running" --> "Failed": Job exited with error
    "Running" --> "Stopping": User requested stop
    "Stopping" --> "Stopped": Stop completed
    "Failed" --> [*]
    "Succeeded" --> [*]
    "Stopped" --> [*]
```

The state of a job is determined by the underlying Framework status in Kubernetes and is converted to user-friendly states through the `convertState` function.

Sources:
- [src/rest-server/src/models/v2/utils/frameworkConverter.js:156-200]()
- [src/webportal/src/app/job/job-view/fabric/JobList/utils.js:23-39]()

## Job Submission Process

The job submission process involves several steps from API request to the creation of a Framework in Kubernetes.

```mermaid
sequenceDiagram
    participant Client as "Client"
    participant REST as "REST Server"
    participant DB as "Database"
    participant K8s as "Kubernetes API"
    participant FC as "Framework Controller"
    
    Client->>REST: POST /api/v2/jobs
    REST->>REST: Validate job protocol
    REST->>DB: Store job metadata
    REST->>K8s: Create Framework
    K8s->>FC: Create Framework
    FC->>FC: Process Framework
    REST-->>Client: Return acceptance
```

When a job is submitted, the REST server:
1. Validates the job protocol
2. Checks for duplicate job names
3. Generates a framework description
4. Creates necessary Kubernetes resources (secrets, priority classes)
5. Submits the framework to Kubernetes via Framework Controller

Sources:
- [src/rest-server/src/controllers/v2/job.js:185-210]()
- [src/rest-server/src/models/v2/job/k8s.js:679-805]()

## Framework Generation

OpenPAI translates job configurations into Kubernetes Frameworks with the following structure:

```mermaid
classDiagram
    class Framework {
        apiVersion
        kind
        metadata
        spec
    }
    
    class FrameworkSpec {
        executionType
        retryPolicy
        taskRoles[]
    }
    
    class TaskRole {
        name
        taskNumber
        frameworkAttemptCompletionPolicy
        task
    }
    
    class Task {
        retryPolicy
        podGracefulDeletionTimeoutSec
        pod
    }
    
    class Pod {
        metadata
        spec
    }
    
    Framework --> FrameworkSpec
    FrameworkSpec --> TaskRole
    TaskRole --> Task
    Task --> Pod
```

The framework includes:
- Task roles specified in the job
- Container specifications
- Resource requirements
- Environment variables
- Storage configurations
- Retry policies

Sources:
- [src/rest-server/src/models/v2/job/k8s.js:351-677]()
- [src/frameworkcontroller/deploy/frameworkcontroller.yaml.template:17-42]()

## Resource Scheduling

Resource scheduling for jobs is handled by either:
1. **Default Scheduler** - for basic scheduling needs
2. **Hived Scheduler** - for advanced GPU topology-aware scheduling

```mermaid
flowchart TD
    A["Job Submission"] --> B["Framework Creation"]
    B --> C{"Hived Enabled?"}
    C -->|"Yes"| D["Hived Scheduler"]
    C -->|"No"| E["Default Scheduler"]
    D --> F["GPU Topology Aware Scheduling"]
    E --> G["Basic Resource Scheduling"]
    F --> H["Container Launch"]
    G --> H
```

For Hived Scheduler:
- Jobs specify `hivedPodSpec` that defines GPU requirements
- OpenPAI sets scheduling annotations in the pod metadata
- The scheduler selects the appropriate nodes based on GPU topology

Sources:
- [src/rest-server/src/models/v2/job/k8s.js:651-674]()
- [src/rest-server/src/config/launcher.js:92-102]()

## Container Environment Setup

Once resources are allocated, OpenPAI sets up the container environment for job execution:

```mermaid
flowchart TD
    A["Pod Created"] --> B["Init Container Starts"]
    B --> C["Environment Setup"]
    C --> D["Main Container Starts"]
    D --> E["Job Script Execution"]
    
    subgraph "Init Container"
    C --> C1["Mount Volumes"]
    C --> C2["Set Environment Variables"]
    C --> C3["Prepare Runtime Scripts"]
    end
    
    subgraph "Main Container"
    E --> E1["Execute User Code"]
    E --> E2["Collect Metrics/Logs"]
    end
```

Key aspects of the container setup:
- Runtime image is specified via `LAUNCHER_RUNTIME_IMAGE`
- Environment variables include PAI_CURRENT_TASK_ROLE_NAME, GPU visibility settings
- Storage volumes are mounted
- Shared memory configuration
- Network ports allocation

Sources:
- [src/rest-server/src/models/v2/job/k8s.js:435-475]()
- [src/openpai-runtime/build/openpai-runtime.k8s.dockerfile:18-19]()

## Job and Task Monitoring

OpenPAI continuously monitors the status of jobs and their constituent tasks:

```mermaid
flowchart TD
    A["Framework Controller"] -->|"Updates"| B["Framework Status"]
    B --> C["Job Status API"]
    C --> D["Client/Web Portal"]
    
    B --> E["Task Status Tracking"]
    E --> F["Task Attempt Status"]
    F --> G["Container Status"]
    
    H["Log Collection"] --> I["Log Storage"]
    I --> J["Log API"]
    J --> D
```

Monitoring components:
- Framework Controller provides status updates on jobs and tasks
- Task status includes state, container info, and completion status
- Exit diagnostics are generated for completed tasks
- Logs are collected and made available through the API

Sources:
- [src/rest-server/src/models/v2/job/k8s.js:155-349]()
- [src/rest-server/src/controllers/v2/job.js:320-341]()

## Exit Codes and Diagnostics

OpenPAI employs a comprehensive exit code system to diagnose job failures:

| Exit Code Range | Owner       | Description                  |
|-----------------|-------------|------------------------------|
| 0               | USER        | Success                      |
| -999 to -1      | PAI_FC      | Framework controller failures|
| -1099 to -1000  | PAI_K8S     | Kubernetes failures         |
| -2000+          | Various     | Other component failures     |
| 1-255           | USER        | User application failures    |

The exit diagnostics contain:
- Exit code and phrase
- Causer and issuer information
- Detailed error messages
- Suggested solutions

Sources:
- [src/k8s-job-exit-spec/config/k8s-job-exit-spec.yaml:17-167]()
- [src/rest-server/src/models/v2/utils/frameworkConverter.js:32-112]()

## API Interaction

The REST server exposes several endpoints for job lifecycle management:

```mermaid
flowchart LR
    A["/api/v2/jobs"] -->|"GET"| B["List jobs"]
    A -->|"POST"| C["Submit job"]
    
    D["/api/v2/jobs/:frameworkName"] -->|"GET"| E["Get job details"]
    
    F["/api/v2/jobs/:frameworkName/executionType"] -->|"PUT"| G["Start/Stop job"]
    
    H["/api/v2/jobs/:frameworkName/config"] -->|"GET"| I["Get job config"]
    
    J["/api/v2/jobs/:frameworkName/ssh"] -->|"GET"| K["Get SSH info"]
    
    L["/api/v2/jobs/:frameworkName/events"] -->|"GET"| M["Get events"]
    
    N["/api/v2/jobs/:frameworkName/.../:taskAttemptId/logs"] -->|"GET"| O["Get logs"]
```

Key API functionalities:
- Job submission and retrieval
- Job execution control (start/stop)
- Task-level monitoring
- Log access

Sources:
- [src/rest-server/src/routes/v2/job.js:32-105]()
- [src/rest-server/src/controllers/v2/job.js:27-341]()
- [src/rest-server/docs/swagger.yaml:40-116]()

## Storage and Logging

OpenPAI provides mechanisms for persistent storage and comprehensive logging:

```mermaid
flowchart TD
    A["Job"] --> B["Container Logs"]
    B --> C{"Log Server Type"}
    C -->|"Log Manager"| D["Node-level Log Manager"]
    C -->|"Azure Storage"| E["Azure Blob Storage"]
    D --> F["REST API for Log Access"]
    E --> F
    
    A --> G["Storage Volume Mounts"]
    G --> H["Persistent Storage"]
```

Log handling includes:
- Runtime logs collection
- Standard output and error streams
- Log storage in either local log manager or Azure Blob Storage
- API access to logs including streaming capability

Sources:
- [src/rest-server/src/models/v2/job/log.js:17-295]()
- [src/rest-server/src/controllers/internal/tail-log.js:18-61]()

## Job Retries and Fault Tolerance

OpenPAI includes mechanisms for handling job failures and retries:

```mermaid
flowchart TD
    A["Job Failure Detected"] --> B{"Retry Policy"}
    B -->|"ALWAYS_RETRY"| C["Automatic Retry"]
    B -->|"NEVER_RETRY"| D["Terminal Failure"]
    B -->|"RETRY_TO_MAX"| E["Retry Until Max Count"]
    
    C --> F["New Job Attempt"]
    E -->|"Under Max"| F
    E -->|"Reached Max"| D
    
    F --> G["Resource Allocation"]
```

Retry policy is based on the:
- Nature of the failure (transient vs. permanent)
- Failure source (platform vs. user code)
- Configuration in the job specification
- Exit code classification

Sources:
- [src/k8s-job-exit-spec/config/k8s-job-exit-spec.yaml:96-116]()
- [src/rest-server/src/models/v2/job/k8s.js:387-394]()

## Job Priority and Resource Management

OpenPAI supports job prioritization and resource management:

```mermaid
flowchart TD
    A["Job Submission"] --> B["Priority Assignment"]
    B --> C["Priority Class Creation"]
    C --> D["Queue Placement"]
    D --> E["Resource Allocation"]
    
    F["System Resources"] --> G["Virtual Clusters"]
    G --> E
```

Priority management includes:
- Job priority specification in job configuration
- Priority class creation in Kubernetes
- Preemption policies based on priority
- Virtual cluster resource allocation

Sources:
- [src/rest-server/src/models/v2/job/k8s.js:807-820]()
- [src/rest-server/src/controllers/v2/job.js:84-97]()

## Conclusion

The job lifecycle in OpenPAI encompasses a complex but well-structured flow from submission to completion. By leveraging Kubernetes through the Framework Controller and specialized scheduling with the Hived Scheduler, OpenPAI provides a robust platform for running AI workloads with advanced resource management, monitoring, and fault tolerance capabilities.

Understanding this lifecycle is essential for effectively using, troubleshooting, and optimizing jobs in an OpenPAI cluster.

---

# Page: REST Server

# REST Server

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/database-controller/src/write-merger/app.js](src/database-controller/src/write-merger/app.js)
- [src/rest-server/config/rest-server.md](src/rest-server/config/rest-server.md)
- [src/rest-server/config/rest-server.yaml](src/rest-server/config/rest-server.yaml)
- [src/rest-server/config/rest_server.py](src/rest-server/config/rest_server.py)
- [src/rest-server/deploy/rest-server.yaml.template](src/rest-server/deploy/rest-server.yaml.template)
- [src/rest-server/docs/swagger.yaml](src/rest-server/docs/swagger.yaml)
- [src/rest-server/package.json](src/rest-server/package.json)
- [src/rest-server/src/config/express.js](src/rest-server/src/config/express.js)
- [src/rest-server/src/config/launcher.js](src/rest-server/src/config/launcher.js)
- [src/rest-server/src/config/schedule-port.js](src/rest-server/src/config/schedule-port.js)
- [src/rest-server/src/controllers/internal/tail-log.js](src/rest-server/src/controllers/internal/tail-log.js)
- [src/rest-server/src/controllers/v2/job.js](src/rest-server/src/controllers/v2/job.js)
- [src/rest-server/src/controllers/v2/task.js](src/rest-server/src/controllers/v2/task.js)
- [src/rest-server/src/models/v2/job/index.js](src/rest-server/src/models/v2/job/index.js)
- [src/rest-server/src/models/v2/job/k8s.js](src/rest-server/src/models/v2/job/k8s.js)
- [src/rest-server/src/models/v2/job/log.js](src/rest-server/src/models/v2/job/log.js)
- [src/rest-server/src/models/v2/task.js](src/rest-server/src/models/v2/task.js)
- [src/rest-server/src/models/v2/utils/frameworkConverter.js](src/rest-server/src/models/v2/utils/frameworkConverter.js)
- [src/rest-server/src/models/v2/utils/name.js](src/rest-server/src/models/v2/utils/name.js)
- [src/rest-server/src/routes/internal/index.js](src/rest-server/src/routes/internal/index.js)
- [src/rest-server/src/routes/internal/tail-log.js](src/rest-server/src/routes/internal/tail-log.js)
- [src/rest-server/src/routes/v2/job.js](src/rest-server/src/routes/v2/job.js)
- [src/rest-server/src/utils/error.d.ts](src/rest-server/src/utils/error.d.ts)
- [src/rest-server/test/setup.js](src/rest-server/test/setup.js)
- [src/rest-server/yarn.lock](src/rest-server/yarn.lock)
- [tests/jenkins/test_rest_server_js_sdk.sh](tests/jenkins/test_rest_server_js_sdk.sh)

</details>



The REST Server is a central component in OpenPAI that provides RESTful APIs for clients to interact with the platform. It handles job submission, management, authentication, user management, virtual cluster management, and various other platform operations. This component serves as the primary interface between users (through the Web Portal or API clients) and the underlying Kubernetes infrastructure.

## Overview

```mermaid
graph TD
    Client["Client Applications"] -->|"HTTP Requests"| REST["REST Server"]
    WebPortal["Web Portal"] -->|"API Calls"| REST
    VSCode["VSCode Extension"] -->|"API Calls"| REST
    
    REST -->|"Framework Operations"| FC["Framework Controller"]
    REST -->|"Authentication"| Auth["Authentication Module"]
    REST -->|"Data Storage"| DB[(SQL Database)]
    REST -->|"Job Management"| K8s["Kubernetes API"]
    
    FC -->|"Job Scheduling"| HS["Hived Scheduler"]
    FC -->|"Create Pods"| K8s
    
    subgraph "REST Server Components"
        RM["Route Management"]
        CM["Controller Management"]
        MM["Model Management"]
        Auth
    end
    
    REST --> RM
    RM --> CM
    CM --> MM
    MM -->|"Database Operations"| DB
    MM -->|"Kubernetes Operations"| K8s
```

The REST Server provides APIs for various operations including:
- Job submission and management
- User authentication and authorization
- User management
- Virtual cluster management
- Job log retrieval
- Storage management
- Alert management

Sources: [src/rest-server/src/config/express.js:37-62](), [src/rest-server/docs/swagger.yaml:28-50](), [src/rest-server/src/routes/v2/index.js]()

## Architecture

The REST Server is built on Node.js using the Express.js framework. It follows a traditional web service architecture with routes, controllers, and models.

```mermaid
classDiagram
    class "Express App" {
        +routes
        +middleware
        +errorHandlers
    }
    
    class "API Routes" {
        +v1Routes
        +v2Routes
        +internalRoutes
    }
    
    class "Controllers" {
        +jobController
        +userController
        +authController
        +taskController
        +vcController
    }
    
    class "Models" {
        +jobModel
        +userModel
        +authModel
        +k8sModel
    }
    
    class "Config" {
        +launcherConfig
        +authConfig
        +k8sConfig
    }
    
    class "Middleware" {
        +tokenMiddleware
        +asyncHandler
        +paramValidator
        +protocolMiddleware
    }
    
    "Express App" --> "API Routes"
    "API Routes" --> "Controllers"
    "Controllers" --> "Models"
    "Models" --> "Config"
    "Express App" --> "Middleware"
    "Controllers" --> "Middleware"
```

Sources: [src/rest-server/src/config/express.js](), [src/rest-server/src/routes/v2/index.js](), [src/rest-server/src/controllers/v2/job.js](), [src/rest-server/src/models/v2/job/index.js]()

### Key Components

1. **Routes**: Define API endpoints and map them to controllers
2. **Controllers**: Handle HTTP requests, validate input, and call models
3. **Models**: Implement business logic and interact with databases and external services
4. **Middleware**: Provide common functionality like authentication, error handling, and request processing

## Job Management

One of the primary functions of the REST Server is job management. It handles the submission, execution, monitoring, and termination of jobs.

### Job Submission Flow

```mermaid
sequenceDiagram
    participant Client
    participant REST as "REST Server"
    participant K8s as "Kubernetes API"
    participant FC as "Framework Controller"
    participant HS as "Hived Scheduler"
    
    Client->>REST: POST /api/v2/jobs
    REST->>REST: Validate job protocol
    REST->>REST: Generate framework description
    REST->>K8s: Create framework
    
    K8s->>FC: Framework created
    FC->>HS: Schedule framework
    HS->>FC: Resource allocation
    FC->>K8s: Create pods
    
    REST-->>Client: 202 Accepted
    
    Client->>REST: GET /api/v2/jobs/{name}
    REST->>K8s: Get framework status
    K8s-->>REST: Framework status
    REST-->>Client: Job details
```

Sources: [src/rest-server/src/controllers/v2/job.js:177-183](), [src/rest-server/src/controllers/v2/job.js:185-210](), [src/rest-server/src/models/v2/job/k8s.js:679-805]()

### Job Framework Conversion

The REST Server converts user job requests into Kubernetes framework definitions. This involves:

1. **Protocol Validation**: Ensuring the job request adheres to the OpenPAI protocol
2. **Framework Generation**: Converting the protocol to a Kubernetes framework object
3. **Resource Allocation**: Specifying CPU, memory, GPU, and other resource requirements
4. **Environment Setup**: Setting up the job environment with necessary variables

Sources: [src/rest-server/src/models/v2/job/k8s.js:351-677](), [src/rest-server/src/models/v2/job/k8s.js:806-885]()

### Job Status and Monitoring

The REST Server provides APIs to monitor job status:

```mermaid
graph TD
    subgraph "Job States"
        WAITING --> RUNNING
        RUNNING --> SUCCEEDED
        RUNNING --> FAILED
        RUNNING --> STOPPING
        STOPPING --> STOPPED
    end
    
    subgraph "Task States"
        TASK_WAITING["WAITING"] --> TASK_RUNNING["RUNNING"]
        TASK_RUNNING --> TASK_COMPLETED["COMPLETED"]
        TASK_RUNNING --> TASK_FAILED["FAILED"]
    end
```

Sources: [src/rest-server/src/models/v2/utils/frameworkConverter.js:156-184](), [src/rest-server/src/models/v2/utils/frameworkConverter.js:186-214]()

## Job API Endpoints

The REST Server provides several API endpoints for job management:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v2/jobs` | GET | List jobs with filtering and pagination |
| `/api/v2/jobs` | POST | Submit a new job |
| `/api/v2/jobs/{name}` | GET | Get job details |
| `/api/v2/jobs/{name}/config` | GET | Get job configuration |
| `/api/v2/jobs/{name}/ssh` | GET | Get job SSH information |
| `/api/v2/jobs/{name}/executionType` | PUT | Start or stop a job |
| `/api/v2/jobs/{name}/attempts/{id}` | GET | Get specific job attempt |
| `/api/v2/jobs/{name}/events` | GET | Get job events |
| `/api/v2/jobs/{name}/tag` | PUT/DELETE | Add or delete a job tag |

Sources: [src/rest-server/src/routes/v2/job.js:32-105](), [src/rest-server/docs/swagger.yaml:52-654]()

## Authentication

The REST Server supports multiple authentication methods:

1. **Basic Authentication**: Username and password
2. **OIDC Authentication**: OAuth/OpenID Connect
3. **Token-based Authentication**: JWT tokens for API access

```mermaid
sequenceDiagram
    participant User
    participant Client
    participant REST as "REST Server"
    participant DB as "Database"
    
    User->>Client: Enter credentials
    Client->>REST: POST /api/v2/authn/basic/login
    REST->>DB: Validate credentials
    DB-->>REST: Credential validation result
    
    alt Valid credentials
        REST->>REST: Generate JWT token
        REST-->>Client: Return token
        Client->>Client: Store token
    else Invalid credentials
        REST-->>Client: 401 Unauthorized
    end
    
    Client->>REST: API request with Authorization header
    REST->>REST: Validate token
    
    alt Valid token
        REST->>REST: Process request
        REST-->>Client: Response
    else Invalid token
        REST-->>Client: 401 Unauthorized
    end
```

Sources: [src/rest-server/docs/swagger.yaml:177-280](), [src/rest-server/src/config/express.js:69-80]()

## Virtual Cluster Management

The REST Server provides APIs to manage virtual clusters, which are logical groupings of resources:

1. **List Virtual Clusters**: View available virtual clusters
2. **Get Virtual Cluster**: View details of a specific virtual cluster
3. **Create Virtual Cluster**: Create a new virtual cluster
4. **Update Virtual Cluster**: Modify virtual cluster configuration
5. **Delete Virtual Cluster**: Remove a virtual cluster

Virtual clusters help in resource isolation and quota management across different user groups.

## Log Management

The REST Server provides APIs to access job logs. It supports multiple log storage backends:

1. **Log Manager**: Logs stored on the node running the job
2. **Azure Storage**: Logs stored in Azure Blob Storage

```mermaid
graph TD
    Client["Client"] -->|"GET /api/v2/.../logs"| REST["REST Server"]
    
    REST -->|"If logServer=log_manager"| LM["Log Manager"]
    REST -->|"If logServer=azure_storage"| AS["Azure Storage"]
    
    LM -->|"Access Node Logs"| Node["Node File System"]
    AS -->|"Access Blob Storage"| Blob["Azure Blob Container"]
    
    LM ---->|"Return Log URLs"| REST
    AS ---->|"Return Log URLs"| REST
    
    REST ---->|"Log Location URLs"| Client
    Client -->|"Fetch Logs Directly"| Node
    Client -->|"Fetch Logs Directly"| Blob
```

Sources: [src/rest-server/src/models/v2/job/log.js:34-308](), [src/rest-server/src/controllers/v2/job.js:320-341]()

## Deployment

The REST Server is deployed as a DaemonSet in Kubernetes. The deployment configuration includes:

1. **Environment Variables**: Configuration for various components
2. **Volume Mounts**: Access to configuration files and logs
3. **Resource Limits**: CPU and memory allocations
4. **Ports**: Exposed service ports

Sources: [src/rest-server/deploy/rest-server.yaml.template:18-188]()

## Configuration Options

The REST Server can be configured through various parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `server-port` | REST server listening port | 9186 |
| `jwt-secret` | Secret for JWT token generation | pai-secret |
| `jwt-expire-time` | JWT token expiration time | 7d |
| `default-pai-admin-username` | Default admin username | - |
| `default-pai-admin-password` | Default admin password | - |
| `schedule-port-start` | Starting port for job scheduling | 15000 |
| `schedule-port-end` | Ending port for job scheduling | 40000 |
| `sql-max-connection` | Max SQL database connections | 50 |
| `log-server` | Log server type (log_manager or azure_storage) | log_manager |

Sources: [src/rest-server/config/rest-server.yaml:18-46](), [src/rest-server/config/rest-server.md:40-51]()

## Error Handling

The REST Server uses a standardized error format for API responses:

```json
{
  "code": "ErrorCode",
  "message": "Detailed error message"
}
```

Common error codes include:
- `NoJobError`: Job not found
- `ConflictJobError`: Job already exists
- `ForbiddenUserError`: User not authorized
- `NoTaskLogError`: Task logs not found

Sources: [src/rest-server/src/utils/error.d.ts:20-54](), [src/rest-server/src/config/express.js:83-96]()

## Integration Points

The REST Server integrates with several OpenPAI components:

1. **Framework Controller**: Job scheduling and management
2. **Hived Scheduler**: Resource allocation for GPU workloads
3. **PostgreSQL Database**: Storage for user and job information
4. **Alert Manager**: System alerting and notification
5. **Kubernetes API**: Container orchestration

Sources: [src/rest-server/src/config/launcher.js:81-152](), [src/rest-server/package.json:26-66]()

---

# Page: API Reference

# API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/database-controller/src/write-merger/app.js](src/database-controller/src/write-merger/app.js)
- [src/rest-server/config/rest-server.md](src/rest-server/config/rest-server.md)
- [src/rest-server/config/rest-server.yaml](src/rest-server/config/rest-server.yaml)
- [src/rest-server/config/rest_server.py](src/rest-server/config/rest_server.py)
- [src/rest-server/deploy/rest-server.yaml.template](src/rest-server/deploy/rest-server.yaml.template)
- [src/rest-server/docs/swagger.yaml](src/rest-server/docs/swagger.yaml)
- [src/rest-server/package.json](src/rest-server/package.json)
- [src/rest-server/src/config/express.js](src/rest-server/src/config/express.js)
- [src/rest-server/src/config/launcher.js](src/rest-server/src/config/launcher.js)
- [src/rest-server/src/config/schedule-port.js](src/rest-server/src/config/schedule-port.js)
- [src/rest-server/src/controllers/internal/tail-log.js](src/rest-server/src/controllers/internal/tail-log.js)
- [src/rest-server/src/controllers/v2/job.js](src/rest-server/src/controllers/v2/job.js)
- [src/rest-server/src/controllers/v2/task.js](src/rest-server/src/controllers/v2/task.js)
- [src/rest-server/src/models/v2/job/index.js](src/rest-server/src/models/v2/job/index.js)
- [src/rest-server/src/models/v2/job/k8s.js](src/rest-server/src/models/v2/job/k8s.js)
- [src/rest-server/src/models/v2/job/log.js](src/rest-server/src/models/v2/job/log.js)
- [src/rest-server/src/models/v2/task.js](src/rest-server/src/models/v2/task.js)
- [src/rest-server/src/models/v2/utils/frameworkConverter.js](src/rest-server/src/models/v2/utils/frameworkConverter.js)
- [src/rest-server/src/models/v2/utils/name.js](src/rest-server/src/models/v2/utils/name.js)
- [src/rest-server/src/routes/internal/index.js](src/rest-server/src/routes/internal/index.js)
- [src/rest-server/src/routes/internal/tail-log.js](src/rest-server/src/routes/internal/tail-log.js)
- [src/rest-server/src/routes/v2/job.js](src/rest-server/src/routes/v2/job.js)
- [src/rest-server/src/utils/error.d.ts](src/rest-server/src/utils/error.d.ts)
- [src/rest-server/test/setup.js](src/rest-server/test/setup.js)
- [src/rest-server/yarn.lock](src/rest-server/yarn.lock)
- [tests/jenkins/test_rest_server_js_sdk.sh](tests/jenkins/test_rest_server_js_sdk.sh)

</details>



This document provides a comprehensive reference for the OpenPAI (Platform for AI) RESTful API. The API allows programmatic access to the platform's functionality, including job management, user administration, virtual cluster controls, and storage operations.

## Overview

The OpenPAI REST API serves as the interface between clients (Web Portal, VSCode Extension, custom scripts) and the underlying Kubernetes infrastructure. It provides a standardized way to interact with the platform's resources and services.

```mermaid
graph TD
    subgraph "API Architecture"
        Client["Client Applications"] -->|HTTP Requests| REST_API["REST API Server"]
        REST_API -->|Kubernetes API Calls| K8S["Kubernetes API Server"]
        REST_API -->|Query/Update| DB[(Database)]
        
        REST_API -->|Framework Operations| FC["Framework Controller"]
        REST_API -->|Scheduling| HS["Hived Scheduler"]
        REST_API -->|Storage Access| Storage["Storage Services"]
        
        FC --> K8S
        HS --> K8S
    end
```

Sources: [src/rest-server/src/config/express.js:36-62](), [src/rest-server/src/models/v2/job/index.js:40-43]()

## API Versioning

OpenPAI supports multiple API versions for backward compatibility:

- **API v1**: Legacy API endpoints at `/api/v1/...`
- **API v2**: Current API endpoints at `/api/v2/...`
- **Internal API**: System-internal endpoints at `/api/internal/...`

This documentation focuses on the v2 API, which is the recommended version for new integrations.

Sources: [src/rest-server/src/config/express.js:54-62]()

## Authentication

OpenPAI supports two authentication methods:

### Basic Authentication

```mermaid
sequenceDiagram
    participant Client
    participant API as "REST API Server"
    participant DB as "Database"
    
    Client->>API: POST /api/v2/authn/basic/login
    Note over Client,API: {username, password, expiration}
    API->>DB: Validate credentials
    DB->>API: Valid user info
    API->>Client: JWT token response
    
    Client->>API: Request with Bearer token
    Note over Client,API: Authorization: Bearer <token>
    API->>API: Validate token
    API->>Client: Requested resource
```

**Login Endpoint:**
```
POST /api/v2/authn/basic/login
```

**Request Body:**
```json
{
  "username": "your_username",
  "password": "your_password",
  "expiration": 604800  // Token expiration in seconds (7 days)
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
  "user": "username",
  "admin": true
}
```

### OIDC Authentication

For systems configured with OpenID Connect:

```
GET /api/v2/authn/oidc/login
```

This redirects to the configured identity provider for authentication.

Sources: [src/rest-server/docs/swagger.yaml:177-196](), [src/rest-server/src/config/express.js:69-80]()

## Core API Endpoints

The OpenPAI API is organized into several categories:

| Category | Base Path | Purpose |
|----------|-----------|---------|
| Authentication | `/api/v2/authn/` | User login/logout |
| Token | `/api/v2/tokens/` | Token management |
| Job | `/api/v2/jobs/` | Job submission and management |
| User | `/api/v2/users/` | User management |
| Virtual Cluster | `/api/v2/virtual-clusters/` | VC management |
| Storage | `/api/v2/storages/` | Storage configuration |
| Group | `/api/v2/groups/` | User group management |
| Alert | `/api/v2/alerts/` | System alert management |
| Info | `/api/v2/info/` | Cluster information |

Sources: [src/rest-server/docs/swagger.yaml:51-1008]()

## Job API

The Job API is the most commonly used part of OpenPAI's REST interface. It enables job submission, monitoring, and management.

### Job Lifecycle

```mermaid
stateDiagram-v2
    [*] --> WAITING: Submit Job
    WAITING --> RUNNING: Resources allocated
    RUNNING --> SUCCEEDED: Exit code 0
    RUNNING --> FAILED: Non-zero exit
    RUNNING --> STOPPED: User stop
    RUNNING --> STOPPING: Stop in progress
    STOPPING --> STOPPED
    SUCCEEDED --> [*]
    FAILED --> [*]
    STOPPED --> [*]
```

Sources: [src/rest-server/src/models/v2/utils/frameworkConverter.js:156-184]()

### Job Endpoints

#### List Jobs

```
GET /api/v2/jobs
```

**Parameters:**
- `username`: Filter by username(s) (comma-separated)
- `vc`: Filter by virtual cluster(s) (comma-separated)
- `state`: Filter by job state(s) (comma-separated)
- `offset`: Pagination offset
- `limit`: Pagination limit (max 50000, default 5000)
- `withTotalCount`: Include total count (true/false)
- `tagsContain`: Filter by jobs containing tag(s) (comma-separated)
- `tagsNotContain`: Filter by jobs not containing tag(s) (comma-separated)
- `keyword`: Search in username, jobname, or virtual cluster
- `jobPriority`: Filter by job priority
- `order`: Sorting order (field,ASC/DESC, e.g., "submissionTime,DESC")

**Response:**
```json
{
  "totalCount": 1,
  "data": [
    {
      "name": "jobName",
      "username": "userName",
      "state": "RUNNING",
      "subState": "AttemptRunning",
      "executionType": "START",
      "tags": ["tag1", "tag2"],
      "retries": 0,
      "retryDetails": {
        "user": 0,
        "platform": 0,
        "resource": 0
      },
      "retryDelayTime": 0,
      "submissionTime": 1649926800000,
      "createdTime": 1649926810000,
      "launchedTime": 1649926820000,
      "completedTime": null,
      "appExitCode": null,
      "virtualCluster": "default",
      "totalGpuNumber": 1,
      "totalTaskNumber": 1,
      "totalTaskRoleNumber": 1,
      "jobPriority": 10
    }
  ]
}
```

Sources: [src/rest-server/src/controllers/v2/job.js:27-175](), [src/rest-server/src/routes/v2/job.js:34-37]()

#### Get Job Details

```
GET /api/v2/jobs/{frameworkName}
```

**Response:**
```json
{
  "debugId": "userName~jobName",
  "name": "jobName",
  "tags": ["tag1", "tag2"],
  "jobPriority": 10,
  "jobStatus": {
    "username": "userName",
    "state": "RUNNING",
    "subState": "AttemptRunning",
    "executionType": "START",
    "retries": 0,
    "retryDetails": {
      "user": 0,
      "platform": 0,
      "resource": 0
    },
    "retryDelayTime": 0,
    "createdTime": 1649926810000,
    "launchedTime": 1649926820000,
    "completedTime": null,
    "attemptId": 0,
    "attemptState": "RUNNING",
    "appId": "appId",
    "appProgress": 0,
    "appTrackingUrl": "",
    "appCreatedTime": 1649926810000,
    "appLaunchedTime": 1649926820000,
    "appCompletedTime": null,
    "appExitCode": null,
    "appExitSpec": null,
    "appExitDiagnostics": null,
    "virtualCluster": "default",
    "submissionTime": 1649926800000
  },
  "taskRoles": {
    "taskRoleName": {
      "taskRoleStatus": {
        "name": "taskRoleName"
      },
      "taskStatuses": [
        {
          "taskIndex": 0,
          "taskUid": "uid",
          "taskState": "RUNNING",
          "containerId": "podUid",
          "containerIp": "10.0.0.1",
          "containerNodeName": "node1",
          "containerPorts": {
            "ssh": "23456",
            "http": "23457"
          },
          "containerGpus": null,
          "containerLog": "/api/v2/jobs/userName~jobName/attempts/0/taskRoles/taskRoleName/taskIndex/0/attempts/0/logs",
          "containerExitCode": null,
          "retries": 0,
          "accountableRetries": 0,
          "createdTime": 1649926810000,
          "launchedTime": 1649926820000,
          "completedTime": null,
          "attemptId": 0,
          "attemptState": "RUNNING",
          "hived": {
            "affinityGroupName": "default/podName",
            "lazyPreempted": null,
            "lazyPreemptionStatus": null
          }
        }
      ]
    }
  }
}
```

Sources: [src/rest-server/src/controllers/v2/job.js:177-183](), [src/rest-server/src/routes/v2/job.js:39-42](), [src/rest-server/src/models/v2/job/k8s.js:155-349]()

#### Submit Job

```
POST /api/v2/jobs
```

**Request Body:** 
Job configuration in OpenPAI protocol format

**Response:**
```json
{
  "status": 202,
  "message": "Update job jobName for user userName successfully."
}
```

Sources: [src/rest-server/src/controllers/v2/job.js:185-210](), [src/rest-server/src/routes/v2/job.js:34-37](), [src/rest-server/src/models/v2/job/k8s.js:679-805]()

#### Start/Stop Job

```
PUT /api/v2/jobs/{frameworkName}/executionType
```

**Request Body:**
```json
{
  "value": "START"
}
```
or
```json
{
  "value": "STOP"
}
```

**Response:**
```json
{
  "status": 202,
  "message": "Execute job userName~jobName successfully."
}
```

Sources: [src/rest-server/src/controllers/v2/job.js:212-229](), [src/rest-server/src/routes/v2/job.js:63-70]()

#### Get Job Configuration

```
GET /api/v2/jobs/{frameworkName}/config
```

**Response:** Job configuration in YAML format

Sources: [src/rest-server/src/controllers/v2/job.js:231-246](), [src/rest-server/src/routes/v2/job.js:72-75]()

#### Get Job SSH Info

```
GET /api/v2/jobs/{frameworkName}/ssh
```

**Response:**
```json
{
  "containers": [
    {
      "id": "containerID",
      "sshIp": "10.0.0.1",
      "sshPort": "23456"
    }
  ],
  "keyPair": {
    "privateKey": "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----",
    "publicKey": "ssh-rsa ..."
  }
}
```

Sources: [src/rest-server/src/controllers/v2/job.js:248-251](), [src/rest-server/src/routes/v2/job.js:77-80]()

#### Job Tags

Add a tag:
```
PUT /api/v2/jobs/{frameworkName}/tag
```

**Request Body:**
```json
{
  "value": "tagName"
}
```

**Response:**
```json
{
  "status": 200,
  "message": "Add tag tagName for job userName~jobName successfully."
}
```

Delete a tag:
```
DELETE /api/v2/jobs/{frameworkName}/tag
```

**Request Body:**
```json
{
  "value": "tagName"
}
```

**Response:**
```json
{
  "status": 200,
  "message": "Delete tag tagName from job userName~jobName successfully."
}
```

Sources: [src/rest-server/src/controllers/v2/job.js:253-286](), [src/rest-server/src/routes/v2/job.js:84-100]()

#### Job Events

```
GET /api/v2/jobs/{frameworkName}/events
```

**Parameters:**
- `type`: Filter by event type

**Response:**
```json
[
  {
    "uid": "eventUid",
    "frameworkName": "userName~jobName",
    "podUid": "podUid",
    "taskroleName": "taskRoleName",
    "taskName": "taskName",
    "taskIndex": 0,
    "type": "Warning",
    "reason": "Failed",
    "message": "Error message",
    "firstTimestamp": "2023-01-01T00:00:00Z",
    "lastTimestamp": "2023-01-01T00:00:01Z",
    "count": 1,
    "sourceComponent": "kubelet",
    "sourceHost": "node1"
  }
]
```

Sources: [src/rest-server/src/controllers/v2/job.js:289-318](), [src/rest-server/src/routes/v2/job.js:102-105]()

#### Job Logs

```
GET /api/v2/jobs/{frameworkName}/attempts/{jobAttemptId}/taskRoles/{taskRoleName}/taskIndex/{taskIndex}/attempts/{taskAttemptId}/logs
```

**Parameters:**
- `tail-mode`: If true, return only the tail of logs

**Response:**
```json
{
  "locations": [
    {
      "name": "stdout",
      "uri": "/log-manager/10.0.0.1:9103/api/v1/logs?token=token&username=user&taskrole=taskRoleName&framework-name=user~job&pod-uid=podUid"
    },
    {
      "name": "stderr",
      "uri": "/log-manager/10.0.0.1:9103/api/v1/logs?token=token&username=user&taskrole=taskRoleName&framework-name=user~job&pod-uid=podUid"
    },
    {
      "name": "all",
      "uri": "/log-manager/10.0.0.1:9103/api/v1/logs?token=token&username=user&taskrole=taskRoleName&framework-name=user~job&pod-uid=podUid"
    }
  ]
}
```

Sources: [src/rest-server/src/controllers/v2/job.js:320-341](), [src/rest-server/src/routes/v2/job.js:57-61](), [src/rest-server/src/models/v2/job/log.js:52-308]()

### Job Submission Flow

```mermaid
sequenceDiagram
    participant Client
    participant REST as "REST Server"
    participant K8S as "Kubernetes API"
    participant FC as "Framework Controller"
    participant HS as "Hived Scheduler"
    participant Runtime as "Runtime Container"
    
    Client->>REST: Submit job with protocol
    REST->>REST: Validate job protocol
    REST->>K8S: Create framework objects
    Note over REST,K8S: Framework, secrets, priorityClass
    K8S->>FC: Manage framework lifecycle
    FC->>HS: Request scheduling
    HS->>FC: Return resource allocation
    FC->>K8S: Create job pods
    K8S->>Runtime: Start runtime containers
    Runtime->>Client: Job execution
    
    Client->>REST: GET job status/logs
    REST->>K8S: Query job state
    K8S->>REST: Return job information
    REST->>Client: Job status/logs
```

Sources: [src/rest-server/src/models/v2/job/k8s.js:351-677](), [src/rest-server/src/models/v2/job/k8s.js:679-805]()

## API Resource Management

The OpenPAI REST Server is designed to manage resources across the cluster efficiently:

### Rate Limiting

The API has built-in rate limiting to prevent abuse:

- Default API calls: 600 requests per minute
- List jobs: 120 requests per minute
- Job submission: 3600 submissions per hour

These limits can be configured in the server settings.

### Port Management

For job containers, the REST server manages a pool of ports (default 15000-40000) that are:

1. Assigned deterministically based on the container's unique identifiers
2. Used for services like SSH, web interfaces, and custom applications
3. Exposed via container port mappings

The port allocation is handled by generating a hash from the pod UID and port name.

Sources: [src/rest-server/config/rest-server.yaml:21-26](), [src/rest-server/src/models/v2/utils/frameworkConverter.js:216-247](), [src/rest-server/src/config/schedule-port.js:21-46]()

## Error Handling

The API uses standard HTTP status codes along with detailed error responses:

```json
{
  "code": "ErrorCode",
  "message": "Detailed error message",
  "stack": ["Error stack trace (only in development mode)"]
}
```

Common error codes include:

| Error Code | Description |
|------------|-------------|
| NoUserError | User not found |
| NoJobError | Job not found |
| ConflictJobError | Job already exists |
| ForbiddenUserError | User doesn't have permission |
| NoVirtualClusterError | Virtual cluster not found |
| NoTaskLogError | Log not found |
| InvalidParametersError | Invalid request parameters |

Sources: [src/rest-server/src/config/express.js:82-96](), [src/rest-server/src/utils/error.d.ts:20-56]()

## Implementation Details

### Architecture Components

```mermaid
graph TD
    subgraph "REST Server Components"
        Routes["Routes (/api/v2/*)"] --> Controllers["Controllers"]
        Controllers --> Models["Models"]
        Models --> K8sClient["Kubernetes Client"]
        Models --> DB[(Database)]
        
        subgraph "Job Management"
            JobRoutes["Job Routes"] --> JobControllers["Job Controllers"]
            JobControllers --> JobModels["Job Models"]
            JobModels --> FrameworkConverter["Framework Converter"]
        end
        
        K8sClient --> KubeAPI["Kubernetes API"]
    end
```

The server is built with:
- Express.js for HTTP request handling
- Sequelize for database operations
- JWT for authentication
- Kubernetes client for cluster management

Sources: [src/rest-server/package.json:26-66](), [src/rest-server/src/config/express.js:18-37]()

### Deployment

The REST server is deployed as a DaemonSet in Kubernetes with configurations for:

- Connection to the Kubernetes API server
- Framework controller integration
- Hived scheduler integration (if enabled)
- Database connection settings
- Authentication settings
- Job resource management

Sources: [src/rest-server/deploy/rest-server.yaml.template:18-188]()

## Extensions and Integrations

The OpenPAI REST API can be integrated with:

1. **Log Management**:
   - Built-in log manager for accessing container logs
   - Azure Storage for persistent log storage

2. **Storage Solutions**:
   - Support for various storage configurations
   - Integration with PersistentVolumeClaims in Kubernetes

3. **External Authentication**:
   - OIDC for single sign-on
   - Basic authentication for simpler deployments

4. **CI/CD Systems**:
   - Test integration via JS SDK
   - Support for automated job submission

Sources: [src/rest-server/src/models/v2/job/log.js:32-308](), [tests/jenkins/test_rest_server_js_sdk.sh:1-60]()

## Conclusion

The OpenPAI REST API provides a comprehensive interface for managing AI workloads on Kubernetes. The API is designed to be robust, scalable, and easy to integrate with various client applications.

For job submission details and protocol schema, see [Job Protocol Schema](#7.2).

For authentication and user management information, see [Authentication](#4.3).

For cluster monitoring capabilities, see [Monitoring and Alerting](#6).

---

# Page: Job Management

# Job Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/database-controller/src/write-merger/app.js](src/database-controller/src/write-merger/app.js)
- [src/frameworkcontroller/deploy/frameworkcontroller-config.yaml.template](src/frameworkcontroller/deploy/frameworkcontroller-config.yaml.template)
- [src/frameworkcontroller/deploy/frameworkcontroller.yaml.template](src/frameworkcontroller/deploy/frameworkcontroller.yaml.template)
- [src/frameworkcontroller/deploy/refresh.sh](src/frameworkcontroller/deploy/refresh.sh)
- [src/k8s-job-exit-spec/config/k8s-job-exit-spec.yaml](src/k8s-job-exit-spec/config/k8s-job-exit-spec.yaml)
- [src/openpai-runtime/build/openpai-runtime.k8s.dockerfile](src/openpai-runtime/build/openpai-runtime.k8s.dockerfile)
- [src/openpai-runtime/deploy/runtime-exit-spec.yaml.template](src/openpai-runtime/deploy/runtime-exit-spec.yaml.template)
- [src/rest-server/config/rest-server.md](src/rest-server/config/rest-server.md)
- [src/rest-server/config/rest-server.yaml](src/rest-server/config/rest-server.yaml)
- [src/rest-server/config/rest_server.py](src/rest-server/config/rest_server.py)
- [src/rest-server/deploy/rest-server.yaml.template](src/rest-server/deploy/rest-server.yaml.template)
- [src/rest-server/docs/swagger.yaml](src/rest-server/docs/swagger.yaml)
- [src/rest-server/package.json](src/rest-server/package.json)
- [src/rest-server/src/config/express.js](src/rest-server/src/config/express.js)
- [src/rest-server/src/config/launcher.js](src/rest-server/src/config/launcher.js)
- [src/rest-server/src/config/schedule-port.js](src/rest-server/src/config/schedule-port.js)
- [src/rest-server/src/controllers/internal/tail-log.js](src/rest-server/src/controllers/internal/tail-log.js)
- [src/rest-server/src/controllers/v2/job.js](src/rest-server/src/controllers/v2/job.js)
- [src/rest-server/src/controllers/v2/task.js](src/rest-server/src/controllers/v2/task.js)
- [src/rest-server/src/models/v2/job/index.js](src/rest-server/src/models/v2/job/index.js)
- [src/rest-server/src/models/v2/job/k8s.js](src/rest-server/src/models/v2/job/k8s.js)
- [src/rest-server/src/models/v2/job/log.js](src/rest-server/src/models/v2/job/log.js)
- [src/rest-server/src/models/v2/task.js](src/rest-server/src/models/v2/task.js)
- [src/rest-server/src/models/v2/utils/frameworkConverter.js](src/rest-server/src/models/v2/utils/frameworkConverter.js)
- [src/rest-server/src/models/v2/utils/name.js](src/rest-server/src/models/v2/utils/name.js)
- [src/rest-server/src/routes/internal/index.js](src/rest-server/src/routes/internal/index.js)
- [src/rest-server/src/routes/internal/tail-log.js](src/rest-server/src/routes/internal/tail-log.js)
- [src/rest-server/src/routes/v2/job.js](src/rest-server/src/routes/v2/job.js)
- [src/rest-server/src/utils/error.d.ts](src/rest-server/src/utils/error.d.ts)
- [src/rest-server/test/setup.js](src/rest-server/test/setup.js)
- [src/rest-server/yarn.lock](src/rest-server/yarn.lock)
- [src/webportal/src/app/job/job-view/fabric/JobList/utils.js](src/webportal/src/app/job/job-view/fabric/JobList/utils.js)
- [tests/jenkins/test_rest_server_js_sdk.sh](tests/jenkins/test_rest_server_js_sdk.sh)

</details>



This document explains how OpenPAI's REST server handles job management operations, including job submission, monitoring, updating, and execution. It covers the lifecycle of jobs from submission to completion, the API endpoints for job management, and the various components involved in processing jobs.

For information about job submission through the web portal, see [Job Submission](#5.1).

## Job Management Overview

The OpenPAI job management system provides a set of REST APIs to manage AI jobs running on Kubernetes. It allows users to submit, monitor, control, and retrieve information about their jobs.

```mermaid
flowchart TB
    subgraph "Client Applications"
        WebPortal["Web Portal"]
        VSCode["VSCode Extension"]
        API["Other API Clients"]
    end

    subgraph "REST Server"
        JobController["Job Controller\n(src/controllers/v2/job.js)"]
        JobModel["Job Model\n(src/models/v2/job/k8s.js)"]
        LogModel["Log Model\n(src/models/v2/job/log.js)"]
    end

    subgraph "Kubernetes"
        FC["Framework Controller"]
        K8sAPI["Kubernetes API"]
        Pods["Job Pods"]
    end

    subgraph "Storage"
        DB[(Database)]
        Logs["Log Storage"]
    end

    WebPortal --> JobController
    VSCode --> JobController
    API --> JobController
    
    JobController --> JobModel
    JobController --> LogModel
    
    JobModel --> K8sAPI
    JobModel --> DB
    LogModel --> Logs
    
    K8sAPI --> FC
    FC --> Pods
```

Sources:
- [src/rest-server/src/controllers/v2/job.js:1-355]()
- [src/rest-server/src/models/v2/job/k8s.js:1-1175]()
- [src/rest-server/src/models/v2/job/log.js:1-363]()
- [src/rest-server/src/routes/v2/job.js:1-108]()

## Job Lifecycle

A job in OpenPAI goes through several states from submission to completion:

```mermaid
stateDiagram-v2
    [*] --> Waiting: Submit Job
    Waiting --> Running: Resource Allocated
    Running --> Succeeded: Tasks Complete Successfully
    Running --> Failed: Tasks Fail
    Running --> Stopped: User Stops Job
    Running --> Stopping: Stopping in Progress
    Stopping --> Stopped: Stop Complete
    Succeeded --> [*]
    Failed --> [*]
    Stopped --> [*]
```

Sources:
- [src/webportal/src/app/job/job-view/fabric/JobList/utils.js:23-39]()
- [src/rest-server/src/models/v2/utils/frameworkConverter.js:156-223]()

## Job Management API

The REST API provides endpoints for managing jobs:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v2/jobs` | GET | List jobs with filtering and pagination |
| `/api/v2/jobs` | POST | Submit a new job |
| `/api/v2/jobs/:frameworkName` | GET | Get job details |
| `/api/v2/jobs/:frameworkName/executionType` | PUT | Start or stop a job |
| `/api/v2/jobs/:frameworkName/config` | GET | Get job configuration |
| `/api/v2/jobs/:frameworkName/ssh` | GET | Get SSH information for job |
| `/api/v2/jobs/:frameworkName/tag` | PUT | Add a tag to a job |
| `/api/v2/jobs/:frameworkName/tag` | DELETE | Remove a tag from a job |
| `/api/v2/jobs/:frameworkName/events` | GET | Get events related to a job |
| `/api/v2/jobs/:frameworkName/attempts/:jobAttemptId` | GET | Get specific job attempt details |
| `/api/v2/jobs/:frameworkName/attempts/:jobAttemptId/taskRoles/:taskRoleName/taskIndex/:taskIndex/attempts/:taskAttemptId/logs` | GET | Get logs for a specific task |

Sources:
- [src/rest-server/src/routes/v2/job.js:32-105]()
- [src/rest-server/docs/swagger.yaml:42-1078]()

## Job Submission and Processing Flow

When a job is submitted, it goes through several processing steps before execution:

```mermaid
sequenceDiagram
    participant User
    participant RestServer as "REST Server"
    participant JobModel as "Job Model"
    participant K8sAPI as "Kubernetes API"
    participant FrameworkController as "Framework Controller"
    participant Pod as "Job Pods"

    User->>RestServer: Submit Job (POST /api/v2/jobs)
    RestServer->>JobModel: Validate Protocol
    JobModel->>JobModel: Generate Framework Description
    JobModel->>K8sAPI: Create Framework
    K8sAPI->>FrameworkController: Register Framework
    FrameworkController->>K8sAPI: Create PriorityClass
    FrameworkController->>K8sAPI: Create Secrets (if needed)
    FrameworkController->>K8sAPI: Create Pods
    K8sAPI->>Pod: Schedule and Run Job
    Pod-->>K8sAPI: Update Status
    K8sAPI-->>FrameworkController: Report Status
    FrameworkController-->>K8sAPI: Update Framework Status
    User->>RestServer: Get Job Status (GET /api/v2/jobs/:name)
    RestServer->>JobModel: Get Job
    JobModel->>K8sAPI: Query Framework Status
    K8sAPI-->>JobModel: Return Framework Status
    JobModel-->>RestServer: Convert to API Format
    RestServer-->>User: Return Job Status
```

Sources:
- [src/rest-server/src/models/v2/job/k8s.js:351-804]()
- [src/rest-server/src/controllers/v2/job.js:177-229]()

## Job Model Structure

The job management system uses several data structures to represent jobs:

```mermaid
classDiagram
    class Framework {
        metadata: Object
        spec: Object
        status: Object
    }
    
    class FrameworkStatus {
        state: String
        attemptStatus: AttemptStatus
        retryPolicyStatus: RetryPolicyStatus
    }
    
    class AttemptStatus {
        id: Number
        startTime: String
        completionTime: String
        completionStatus: CompletionStatus
        taskRoleStatuses: TaskRoleStatus[]
    }
    
    class TaskRoleStatus {
        name: String
        taskStatuses: TaskStatus[]
    }
    
    class TaskStatus {
        index: Number
        state: String
        attemptStatus: TaskAttemptStatus
        retryPolicyStatus: RetryPolicyStatus
    }
    
    class TaskAttemptStatus {
        id: Number
        startTime: String
        completionTime: String
        podUID: String
        podName: String
        podNodeName: String
        podHostIP: String
        completionStatus: CompletionStatus
    }
    
    class CompletionStatus {
        code: Number
        type: Object
        diagnostics: String
        trigger: Object
    }
    
    Framework --> FrameworkStatus
    FrameworkStatus --> AttemptStatus
    AttemptStatus --> TaskRoleStatus
    TaskRoleStatus --> TaskStatus
    TaskStatus --> TaskAttemptStatus
    TaskAttemptStatus --> CompletionStatus
```

Sources:
- [src/rest-server/src/models/v2/job/k8s.js:80-348]()
- [src/rest-server/src/models/v2/utils/frameworkConverter.js:1-223]()

## Job Configuration

Jobs are configured using a protocol specification that defines resource requirements, Docker images, commands to run, and other settings. The configuration is converted into a Kubernetes framework.

Key configuration components include:

1. **Task Roles**: Each job consists of one or more task roles, which are sets of identical tasks.
2. **Resources**: CPU, memory, and GPU requirements for each task role.
3. **Docker Images**: Container images to be used for the tasks.
4. **Commands**: Commands to run inside the containers.
5. **Retries**: Number of times to retry a failed task or job.

### Framework Generation

The system generates a framework description from the job configuration:

```mermaid
flowchart TD
    JobConfig["Job Configuration"] --> ConfigProcessor["Generate Framework Description"]
    ConfigProcessor --> Framework["Kubernetes Framework"]
    
    subgraph "Framework Generation"
        ConfigProcessor --> TaskRoles["Generate Task Roles"]
        TaskRoles --> Secrets["Generate Secrets (if needed)"]
        TaskRoles --> PriorityClass["Generate PriorityClass"]
        TaskRoles --> Pods["Generate Pod Specs"]
        Pods --> Resources["Set Resource Requirements"]
        Pods --> Envs["Set Environment Variables"]
        Pods --> Mounts["Set Volume Mounts"]
    end
    
    Framework --> K8sAPI["Submit to Kubernetes API"]
```

Sources:
- [src/rest-server/src/models/v2/job/k8s.js:679-805]()
- [src/rest-server/src/models/v2/job/k8s.js:351-677]()

## Job Operations

### Listing Jobs

The `list` function retrieves jobs with filtering, sorting, and pagination:

```mermaid
flowchart LR
    Request["GET /api/v2/jobs"] --> Controller["Job Controller"]
    Controller --> Model["Job Model list()"]
    Model --> DB[(Database)]
    DB --> Model
    Model --> Converter["Convert to API Format"]
    Converter --> Response["Return Job List"]
    
    subgraph "Filtering Options"
        Username["username"]
        VirtualCluster["vc"]
        State["state"]
        Keyword["keyword"]
        Tags["tags"]
        JobPriority["jobPriority"]
    end
    
    subgraph "Sorting Options"
        SortField["sort field"]
        SortOrder["sort order"]
    end
    
    Username --> Controller
    VirtualCluster --> Controller
    State --> Controller
    Keyword --> Controller
    Tags --> Controller
    JobPriority --> Controller
    SortField --> Controller
    SortOrder --> Controller
```

Sources:
- [src/rest-server/src/controllers/v2/job.js:27-175]()
- [src/rest-server/src/models/v2/job/k8s.js:886-961]()

### Getting Job Details

The `get` function retrieves details for a specific job:

```mermaid
flowchart LR
    Request["GET /api/v2/jobs/:frameworkName"] --> Controller["Job Controller"]
    Controller --> Model["Job Model get()"]
    Model --> DB[(Database)]
    Model --> K8s["Kubernetes API"]
    DB --> Model
    K8s --> Model
    Model --> Converter["Convert to API Format"]
    Converter --> Response["Return Job Details"]
```

Sources:
- [src/rest-server/src/controllers/v2/job.js:177-183]()
- [src/rest-server/src/models/v2/job/k8s.js:963-1026]()

### Executing Job Actions

The `execute` function allows starting or stopping a job:

```mermaid
flowchart LR
    Request["PUT /api/v2/jobs/:frameworkName/executionType"] --> Controller["Job Controller"]
    Controller --> Auth["Check Authorization"]
    Auth --> Model["Job Model execute()"]
    Model --> K8s["Kubernetes API"]
    K8s --> Model
    Model --> Response["Return Success"]
```

Sources:
- [src/rest-server/src/controllers/v2/job.js:212-229]()
- [src/rest-server/src/models/v2/job/k8s.js:1027-1175]()

### Getting Job Logs

The `getLogs` function retrieves logs for a specific task:

```mermaid
flowchart LR
    Request["GET /api/v2/jobs/:frameworkName/attempts/:jobAttemptId/taskRoles/:taskRoleName/taskIndex/:taskIndex/attempts/:taskAttemptId/logs"] --> Controller["Job Controller"]
    Controller --> LogModel["Log Model getLogListFromLogServer()"]
    
    subgraph "Log Servers"
        LogManager["Log Manager"]
        AzureStorage["Azure Storage"]
    end
    
    LogModel --> LogServer{"Log Server Type?"}
    LogServer -->|log_manager| LogManager
    LogServer -->|azure_storage| AzureStorage
    LogManager --> TaskLogs["Task Logs"]
    AzureStorage --> TaskLogs
    TaskLogs --> Response["Return Log List"]
```

Sources:
- [src/rest-server/src/controllers/v2/job.js:320-341]()
- [src/rest-server/src/models/v2/job/log.js:44-294]()

## Job Error Handling

The system provides detailed error diagnostics for failed jobs using exit codes and completion statuses:

```mermaid
flowchart TD
    JobFailure["Job Failure"] --> ExitCode["Get Exit Code"]
    ExitCode --> ExitSpec["Generate Exit Spec"]
    ExitSpec --> Diagnostics["Generate Diagnostics"]
    
    subgraph "Exit Spec Components"
        Code["Exit Code"]
        Phrase["Textual Phrase"]
        Type["Error Type"]
        Reason["Error Reason"]
        Solution["Suggested Solution"]
    end
    
    ExitSpec --> Code
    ExitSpec --> Phrase
    ExitSpec --> Type
    ExitSpec --> Reason
    ExitSpec --> Solution
    
    Code --> UserInterface["Show in UI"]
    Phrase --> UserInterface
    Type --> UserInterface
    Reason --> UserInterface
    Solution --> UserInterface
```

Sources:
- [src/k8s-job-exit-spec/config/k8s-job-exit-spec.yaml:13-1115]()
- [src/rest-server/src/models/v2/utils/frameworkConverter.js:73-112]()
- [src/rest-server/src/models/v2/utils/frameworkConverter.js:134-154]()

## Job Database Integration

The job management system integrates with a PostgreSQL database to persist job information:

```mermaid
flowchart LR
    JobModel["Job Model"] --> Database[(PostgreSQL)]
    
    subgraph "Database Tables"
        Framework["Framework Table"]
        FrameworkHistory["FrameworkHistory Table"]
        Tags["Tags Table"]
        Events["Events Table"]
    end
    
    Database --> Framework
    Database --> FrameworkHistory
    Database --> Tags
    Database --> Events
    
    JobOperations["Job Operations"] --> JobModel
    
    subgraph "Job Operations"
        List["list()"]
        Get["get()"]
        Put["put()"]
        Execute["execute()"]
        AddTag["addTag()"]
        DeleteTag["deleteTag()"]
        GetEvents["getEvents()"]
    end
```

Sources:
- [src/rest-server/src/models/v2/job/k8s.js:886-1026]()
- [src/rest-server/config/rest-server.yaml:1-46]()
- [src/rest-server/package.json:57-60]()

## Configuration Components

The job management system relies on several configuration components:

| Component | Description |
|-----------|-------------|
| Launcher Config | Configures the framework controller, API paths, and runtime |
| Schedule Port | Defines port range for job containers |
| Kubernetes Config | Configures access to the Kubernetes API |
| Exit Spec | Defines exit codes and their meanings |
| Log Server | Configures access to log storage |

Sources:
- [src/rest-server/src/config/launcher.js:22-155]()
- [src/rest-server/config/rest-server.yaml:20-46]()
- [src/rest-server/src/config/schedule-port.js:1-46]()

## Rate Limiting

The job management system applies rate limits to API calls to prevent overloading the system:

| API | Rate Limit |
|-----|------------|
| General API | 600 requests per minute |
| List Jobs | 120 requests per minute |
| Submit Jobs | 3600 requests per hour |

Sources:
- [src/rest-server/config/rest-server.yaml:21-23]()
- [src/rest-server/src/config/express.js:50-50]()

## Security and Permissions

The job management system implements authorization to ensure users can only manage their own jobs unless they have admin privileges:

```mermaid
flowchart TD
    Request["API Request"] --> TokenCheck["Verify Token"]
    TokenCheck --> Valid{"Valid Token?"}
    Valid -->|No| Unauthorized["401 Unauthorized"]
    Valid -->|Yes| ExtractUser["Extract Username"]
    ExtractUser --> PermissionCheck{"Check Permission"}
    PermissionCheck -->|"User is owner or admin"| Allow["Allow Operation"]
    PermissionCheck -->|"User is not owner and not admin"| Forbidden["403 Forbidden"]
```

Sources:
- [src/rest-server/src/controllers/v2/job.js:212-229]()
- [src/rest-server/src/controllers/v2/job.js:253-288]()

## Integration with Framework Controller

The job management system uses the Framework Controller to manage job lifecycle in Kubernetes:

```mermaid
flowchart TD
    RestServer["REST Server"] --> JobModel["Job Model"]
    JobModel --> K8sAPI["Kubernetes API"]
    K8sAPI --> FrameworkController["Framework Controller"]
    
    subgraph "Framework Controller"
        CreateFramework["Create Framework"]
        UpdateFramework["Update Framework"]
        DeleteFramework["Delete Framework"]
        MonitorFramework["Monitor Framework"]
    end
    
    FrameworkController --> CreatePods["Create Pods"]
    CreatePods --> JobPods["Job Pods"]
    
    JobPods --> UpdateStatus["Update Status"]
    UpdateStatus --> FrameworkController
    FrameworkController --> K8sAPI
    K8sAPI --> JobModel
```

Sources:
- [src/frameworkcontroller/deploy/frameworkcontroller.yaml.template:1-53]()
- [src/frameworkcontroller/deploy/frameworkcontroller-config.yaml.template:1-134]()
- [src/rest-server/src/models/v2/job/index.js:19-43]()

## Job Runtime Environment

The OpenPAI runtime environment is responsible for executing jobs in the container:

```mermaid
flowchart TD
    Framework["Framework"] --> TaskRoles["Task Roles"]
    TaskRoles --> Pods["Pods"]
    
    subgraph "Pod"
        InitContainer["Init Container"]
        RuntimeContainer["Runtime Container (User Job)"]
    end
    
    Pods --> InitContainer
    InitContainer --> RuntimeContainer
    
    InitContainer --> SetupEnvironment["Setup Environment"]
    SetupEnvironment --> MountVolumes["Mount Volumes"]
    MountVolumes --> PrepareRuntime["Prepare Runtime"]
    
    RuntimeContainer --> ExecuteUserCommand["Execute User Command"]
    ExecuteUserCommand --> CaptureExitCode["Capture Exit Code"]
    CaptureExitCode --> GenerateDiagnostics["Generate Diagnostics"]
```

Sources:
- [src/openpai-runtime/build/openpai-runtime.k8s.dockerfile:1-20]()
- [src/openpai-runtime/deploy/runtime-exit-spec.yaml.template:1-38]()
- [src/rest-server/src/models/v2/job/k8s.js:412-477]()

## Job Output and Artifacts

Job outputs and artifacts include:

1. **Logs**: Standard output and error logs from the job.
2. **Exit Codes**: The exit status of the job, indicating success or failure.
3. **Metrics**: Resource usage metrics for the job.
4. **Output Files**: Files generated by the job, stored in mounted volumes.

The system provides APIs to access these outputs and artifacts.

Sources:
- [src/rest-server/src/models/v2/job/log.js:1-363]()
- [src/rest-server/src/routes/v2/job.js:58-61]()
- [src/rest-server/src/controllers/v2/job.js:320-341]()

## Conclusion

The job management system in OpenPAI provides a comprehensive set of APIs and tools for submitting, monitoring, and controlling AI jobs. It integrates with Kubernetes through the Framework Controller, manages job lifecycle, and provides detailed diagnostics for job failures.

The system's architecture allows for scalability, reliability, and detailed control over job execution, making it suitable for running complex AI workloads in a cluster environment.

---

# Page: Virtual Cluster Management

# Virtual Cluster Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/rest-server/src/config/v2/hived.js](src/rest-server/src/config/v2/hived.js)
- [src/rest-server/src/config/vc.js](src/rest-server/src/config/vc.js)
- [src/rest-server/src/controllers/v2/alert.js](src/rest-server/src/controllers/v2/alert.js)
- [src/rest-server/src/controllers/v2/virtual-cluster.js](src/rest-server/src/controllers/v2/virtual-cluster.js)
- [src/rest-server/src/middlewares/v2/hived.js](src/rest-server/src/middlewares/v2/hived.js)
- [src/rest-server/src/models/v2/alert.js](src/rest-server/src/models/v2/alert.js)
- [src/rest-server/src/models/v2/virtual-cluster/index.js](src/rest-server/src/models/v2/virtual-cluster/index.js)
- [src/rest-server/src/models/v2/virtual-cluster/k8s.js](src/rest-server/src/models/v2/virtual-cluster/k8s.js)
- [src/rest-server/src/routes/v2/alert.js](src/rest-server/src/routes/v2/alert.js)
- [src/rest-server/src/routes/v2/index.js](src/rest-server/src/routes/v2/index.js)
- [src/rest-server/src/routes/v2/virtual-cluster.js](src/rest-server/src/routes/v2/virtual-cluster.js)
- [src/rest-server/src/utils/k8sUtils.js](src/rest-server/src/utils/k8sUtils.js)

</details>



## 1. Introduction

Virtual Cluster (VC) Management in OpenPAI provides administrators with the ability to partition and allocate cluster resources among different user groups. This document covers the architecture, API, and operations related to virtual cluster management in OpenPAI.

For information about job management within virtual clusters, see [Job Management](#4.2).

## 2. Architecture

Virtual clusters in OpenPAI serve as logical partitions of the physical Kubernetes cluster. Each virtual cluster is allocated a portion of the cluster's resources and can be assigned to specific user groups.

```mermaid
graph TD
    User["User"] --> WebPortal["Web Portal"]
    WebPortal --> RESTServer["REST Server"]
    RESTServer --> VCController["VirtualClusterController"]
    VCController --> VCModel["VirtualClusterModel"]
    
    subgraph "Virtual Cluster Management"
        VCModel --> K8sImplementation["K8sImplementation"]
        VCModel --> HivedScheduler["HivedScheduler"]
    end
    
    K8sImplementation --> K8sAPI["Kubernetes API"]
    HivedScheduler --> K8sAPI
    
    subgraph "Physical Resources"
        K8sAPI --> Nodes["Worker Nodes"]
        Nodes --> GPUs["GPUs"]
        Nodes --> CPUs["CPUs"]
        Nodes --> Memory["Memory"]
    end
```

Sources: [src/rest-server/src/routes/v2/index.js:14-14](), [src/rest-server/src/controllers/v2/virtual-cluster.js](), [src/rest-server/src/models/v2/virtual-cluster/k8s.js]()

### 2.1 Key Components

The virtual cluster management system consists of the following key components:

1. **REST Server API**: Exposes endpoints for virtual cluster operations
2. **Virtual Cluster Controller**: Handles API requests and responses
3. **Virtual Cluster Model**: Implements the business logic for virtual cluster operations
4. **Hived Scheduler**: A Kubernetes scheduler extension that manages resource allocation

```mermaid
sequenceDiagram
    participant Client as "Client (Admin User)"
    participant REST as "REST Server"
    participant VCController as "VC Controller"
    participant VCModel as "VC Model"
    participant HivedScheduler as "Hived Scheduler"
    participant K8s as "Kubernetes API"
    
    Client->>REST: HTTP Request (GET/PUT/DELETE)
    REST->>VCController: Route to controller
    VCController->>VCModel: Call model function
    
    alt If Hived Scheduler enabled
        VCModel->>HivedScheduler: Query/Update VC resources
        HivedScheduler->>K8s: Manage K8s resources
    else
        VCModel->>K8s: Direct K8s resource management
    end
    
    K8s-->>VCModel: Return result
    VCModel-->>VCController: Return data
    VCController-->>REST: Format response
    REST-->>Client: HTTP Response
```

Sources: [src/rest-server/src/routes/v2/virtual-cluster.js](), [src/rest-server/src/controllers/v2/virtual-cluster.js](), [src/rest-server/src/models/v2/virtual-cluster/k8s.js]()

## 3. Resource Allocation

Virtual clusters manage three types of resources:

| Resource Type | Description |
|---------------|-------------|
| CPU (vCores)  | Allocatable CPU cores for computation |
| Memory        | RAM in MB available to applications |
| GPU           | Number of GPU units available |

Each virtual cluster has the following resource metrics:

| Metric | Description |
|--------|-------------|
| resourcesTotal | Total resources allocated to the virtual cluster |
| resourcesGuaranteed | Resources guaranteed to be available |
| resourcesUsed | Currently consumed resources by running jobs |
| capacity | Percentage of total cluster GPUs allocated to this VC |
| usedCapacity | Percentage of total cluster GPUs currently in use |

Sources: [src/rest-server/src/models/v2/virtual-cluster/k8s.js:204-347]()

### 3.1 Resource Units

The Hived Scheduler uses the concept of "resource units" (or SKUs) to define standard resource allocations. Each resource unit specifies a combination of CPU, memory, and GPU resources.

```mermaid
graph TD
    subgraph "ResourceUnits"
        RU["resourceUnits"] --> SKU1["SKU Type 1"]
        RU --> SKU2["SKU Type 2"]
        RU --> SKU3["SKU Type n"]
        
        SKU1 --> SKU1_Resources["CPU: x<br>Memory: y<br>GPU: z"]
        SKU2 --> SKU2_Resources["CPU: a<br>Memory: b<br>GPU: c"]
        SKU3 --> SKU3_Resources["CPU: d<br>Memory: e<br>GPU: f"]
    end
    
    subgraph "Virtual Clusters"
        VC1["Virtual Cluster 1"] --> VC1_RU["Allocated SKUs"]
        VC2["Virtual Cluster 2"] --> VC2_RU["Allocated SKUs"]
    end
    
    SKU1 --> VC1_RU
    SKU2 --> VC1_RU
    SKU2 --> VC2_RU
    SKU3 --> VC2_RU
```

Sources: [src/rest-server/src/config/vc.js:42-66](), [src/rest-server/src/middlewares/v2/hived.js:118-134]()

## 4. Virtual Cluster API

The REST server exposes the following endpoints for virtual cluster management:

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v2/virtual-clusters | List all virtual clusters |
| GET | /api/v2/virtual-clusters/:vcName | Get details of a specific virtual cluster |
| PUT | /api/v2/virtual-clusters/:vcName | Create or update a virtual cluster |
| DELETE | /api/v2/virtual-clusters/:vcName | Remove a virtual cluster |
| PUT | /api/v2/virtual-clusters/:vcName/status | Change virtual cluster status (running/stopped) |

Sources: [src/rest-server/src/routes/v2/virtual-cluster.js:27-56]()

### 4.1 API Request and Response Format

#### 4.1.1 Listing Virtual Clusters

**Request:**
```
GET /api/v2/virtual-clusters
```

**Response:**
```json
{
  "default": {
    "capacity": 100,
    "usedCapacity": 30,
    "dedicated": false,
    "resourcesUsed": {
      "cpu": 10,
      "memory": 20480,
      "gpu": 4,
      "vCores": 10,
      "GPUs": 4
    },
    "resourcesGuaranteed": {
      "cpu": 32,
      "memory": 61440,
      "gpu": 8,
      "vCores": 32,
      "GPUs": 8
    },
    "resourcesTotal": {
      "cpu": 32,
      "memory": 61440,
      "gpu": 8,
      "vCores": 32,
      "GPUs": 8
    }
  },
  "vc1": {
    /* Similar structure */
  }
}
```

Sources: [src/rest-server/src/models/v2/virtual-cluster/k8s.js:203-348]()

#### 4.1.2 Creating/Updating a Virtual Cluster

**Request:**
```
PUT /api/v2/virtual-clusters/new-vc
Content-Type: application/json

{
  "vcCapacity": 20,
  "vcMaxCapacity": 30,
  "description": "A virtual cluster for AI training",
  "externalName": "AI Training Cluster"
}
```

**Response:**
```json
{
  "status": 201,
  "message": "Create virtual cluster new-vc to capacity 20 successfully."
}
```

Sources: [src/rest-server/src/controllers/v2/virtual-cluster.js:59-121](), [src/rest-server/src/config/vc.js:26-33]()

## 5. Implementation Details

### 5.1 Resource Calculation

The system calculates resource usage and allocation using the following approach:

1. For clusters with Hived Scheduler enabled:
   - Query the Hived Scheduler for virtual cluster status
   - Traverse the cell hierarchy to calculate resources
   - Map each resource unit to corresponding CPU, memory, and GPU allocations

2. For clusters without Hived Scheduler:
   - Directly query Kubernetes for node and pod information
   - Calculate resource usage based on running pods' resource requests

```mermaid
flowchart TD
    Start["Calculate VC Resources"] --> HivedEnabled{"Is Hived Enabled?"}
    
    HivedEnabled -- "Yes" --> QueryHived["Query Hived API for VC status"]
    HivedEnabled -- "No" --> QueryK8s["Query K8s API for nodes and pods"]
    
    QueryHived --> TraverseCells["Traverse cell hierarchy"]
    TraverseCells --> CalcHivedResources["Calculate resources from cells"]
    
    QueryK8s --> FetchNodes["Fetch worker nodes"]
    FetchNodes --> FetchPods["Fetch running pods"]
    FetchPods --> CalcK8sResources["Calculate resources from pods"]
    
    CalcHivedResources --> FormatOutput["Format output with used/guaranteed/total resources"]
    CalcK8sResources --> FormatOutput
    
    FormatOutput --> ReturnResult["Return VC resource information"]
```

Sources: [src/rest-server/src/models/v2/virtual-cluster/k8s.js:122-201](), [src/rest-server/src/models/v2/virtual-cluster/k8s.js:218-316]()

### 5.2 Virtual Cluster Integration with Job Submission

When a job is submitted to OpenPAI, it is assigned to a specific virtual cluster. The job submission process includes validation of resource requests against the virtual cluster's available resources.

```mermaid
flowchart TD
    JobSubmission["Job Submission"] --> ValidateVC["Validate VC exists"]
    ValidateVC --> GetVCStatus["Get VC status"]
    GetVCStatus --> CheckResources["Check resource availability"]
    
    CheckResources -- "Resources available" --> ScheduleJob["Schedule job in VC"]
    CheckResources -- "Insufficient resources" --> RejectJob["Reject job submission"]
    
    ScheduleJob --> AllocateResources["Allocate resources"]
    AllocateResources --> UpdateVCUsage["Update VC resource usage"]
```

Sources: [src/rest-server/src/middlewares/v2/hived.js:77-283]()

#### 5.2.1 Hived Scheduler Integration

The Hived Scheduler plays a crucial role in job scheduling within virtual clusters. It:

1. Validates job resource requests against virtual cluster capacity
2. Maps requested resources to appropriate SKU types
3. Handles affinity groups for gang scheduling
4. Manages job priorities within virtual clusters

Job priority classes in Hived Scheduler:

| Priority Class | Value | Description |
|----------------|-------|-------------|
| crit | 120 | Critical priority |
| prod | 100 | Production priority |
| test | 10 | Testing priority (default) |
| oppo | -1 | Opportunistic priority |

Sources: [src/rest-server/src/middlewares/v2/hived.js:27-37](), [src/rest-server/src/middlewares/v2/hived.js:77-98]()

## 6. Troubleshooting

Common issues that may occur when managing virtual clusters:

| Issue | Possible Cause | Resolution |
|-------|----------------|------------|
| Cannot create VC | Invalid VC name format | VC names must contain only alphanumeric and underscore characters |
| Cannot update default VC | Operation not allowed | The default VC has special protection and cannot be modified |
| Cannot allocate resources | Insufficient cluster resources | Check the physical cluster resource availability |
| Resource calculation discrepancy | Hived Scheduler state inconsistency | Restart the Hived Scheduler pod |

Sources: [src/rest-server/src/controllers/v2/virtual-cluster.js:26-42](), [src/rest-server/src/controllers/v2/virtual-cluster.js:148-166]()

## 7. Limitations

Current implementation has the following limitations:

1. Some operations (`updateVc`, `stopVc`, `activeVc`, and `removeVc`) are not fully implemented in the Kubernetes version of the virtual cluster manager.
2. The `default` virtual cluster cannot be modified or removed.
3. When Hived Scheduler is not enabled, resource allocation accuracy may be lower.

Sources: [src/rest-server/src/models/v2/virtual-cluster/k8s.js:362-392](), [src/rest-server/src/controllers/v2/virtual-cluster.js:33-38]()

---

# Page: Web Portal

# Web Portal

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [contrib/submit-job-v2/README.md](contrib/submit-job-v2/README.md)
- [contrib/submit-job-v2/package.json](contrib/submit-job-v2/package.json)
- [contrib/submit-job-v2/src/App/ProtocolForm.tsx](contrib/submit-job-v2/src/App/ProtocolForm.tsx)
- [contrib/submit-job-v2/src/App/TensorBoard.tsx](contrib/submit-job-v2/src/App/TensorBoard.tsx)
- [contrib/submit-job-v2/src/index.ts](contrib/submit-job-v2/src/index.ts)
- [contrib/submit-job-v2/webpack.config.js](contrib/submit-job-v2/webpack.config.js)
- [contrib/submit-job-v2/yarn.lock](contrib/submit-job-v2/yarn.lock)
- [src/webportal/config/webpack.common.js](src/webportal/config/webpack.common.js)
- [src/webportal/package.json](src/webportal/package.json)
- [src/webportal/src/app/components/util/job.js](src/webportal/src/app/components/util/job.js)
- [src/webportal/src/app/home/home.jsx](src/webportal/src/app/home/home.jsx)
- [src/webportal/src/app/home/home/abnormal-job-list.jsx](src/webportal/src/app/home/home/abnormal-job-list.jsx)
- [src/webportal/src/app/home/home/c3.scss](src/webportal/src/app/home/home/c3.scss)
- [src/webportal/src/app/home/home/conn.js](src/webportal/src/app/home/home/conn.js)
- [src/webportal/src/app/home/home/gpu-chart.jsx](src/webportal/src/app/home/home/gpu-chart.jsx)
- [src/webportal/src/app/home/home/header.jsx](src/webportal/src/app/home/home/header.jsx)
- [src/webportal/src/app/home/home/job-status.jsx](src/webportal/src/app/home/home/job-status.jsx)
- [src/webportal/src/app/home/home/recent-job-list.jsx](src/webportal/src/app/home/home/recent-job-list.jsx)
- [src/webportal/src/app/home/home/resource-bar.jsx](src/webportal/src/app/home/home/resource-bar.jsx)
- [src/webportal/src/app/home/home/util.js](src/webportal/src/app/home/home/util.js)
- [src/webportal/src/app/home/home/utilization-chart.jsx](src/webportal/src/app/home/home/utilization-chart.jsx)
- [src/webportal/src/app/home/home/virtual-cluster-statistics.jsx](src/webportal/src/app/home/home/virtual-cluster-statistics.jsx)
- [src/webportal/src/app/home/index/bottom.jsx](src/webportal/src/app/home/index/bottom.jsx)
- [src/webportal/src/app/home/index/jumbotron.jsx](src/webportal/src/app/home/index/jumbotron.jsx)
- [src/webportal/src/app/layout/components/navbar.jsx](src/webportal/src/app/layout/components/navbar.jsx)
- [src/webportal/src/assets/img/sign-in-background.svg](src/webportal/src/assets/img/sign-in-background.svg)
- [src/webportal/yarn.lock](src/webportal/yarn.lock)

</details>



The Web Portal is the main user interface component of OpenPAI (Platform for AI), providing a browser-based application for users and administrators to interact with the platform. It offers a comprehensive interface for job submission, monitoring, and management, as well as cluster resource visualization and administration.

## Architecture Overview

The Web Portal connects users with the underlying OpenPAI infrastructure by communicating with the REST Server API. It provides various views including a home dashboard, job submission forms, job lists, and detailed monitoring interfaces.

```mermaid
flowchart TD
    User["User (Browser)"] --> WebPortal["Web Portal (Frontend)"]
    WebPortal --> RestAPI["REST Server API"]
    RestAPI --> K8s["Kubernetes API"]
    
    subgraph "OpenPAI Infrastructure"
        K8s --> FC["Framework Controller"]
        K8s --> HS["Hived Scheduler"]
        K8s --> Runtime["OpenPAI Runtime"]
        K8s --> Monitoring["Monitoring System\n(Prometheus, Alert Manager)"]
    end
    
    FC --> Jobs["Job Pods"]
    HS --> Jobs
    Runtime --> Jobs
```

Sources:
- [src/webportal/src/app/home/home.jsx:27-38]()
- [src/webportal/src/app/home/home/conn.js:4-17]()
- [src/webportal/package.json:33-96]()

## Technical Implementation

The Web Portal is built as a modern single-page application using React, with the following key technologies:

- **React**: The primary UI framework
- **Office UI Fabric React**: Microsoft's component library providing UI elements
- **Webpack**: Module bundler for application building
- **OpenPAI JS SDK**: JavaScript SDK for communicating with the REST API

The application is organized into multiple pages, each focusing on specific functionality, with a modular architecture that loads components as needed.

```mermaid
flowchart TD
    subgraph "Web Portal Structure"
        WebpackEntries["Webpack Entry Points"]
        Components["Reusable Components"]
        Pages["Application Pages"]
        APIConnectors["API Connectors"]
    end

    WebpackEntries --> |"defines"| Pages
    Pages --> |"uses"| Components
    Pages --> |"calls"| APIConnectors
    APIConnectors --> |"communicates with"| RestServer["REST Server API"]
    
    WebpackEntries --> Layout["Layout\n(Header, Sidebar, Content)"]
    WebpackEntries --> Home["Home Dashboard"]
    WebpackEntries --> JobSubmission["Job Submission"]
    WebpackEntries --> JobList["Job List"]
    WebpackEntries --> JobDetail["Job Detail"]
    WebpackEntries --> ClusterView["Cluster View"]
```

Sources:
- [src/webportal/config/webpack.common.js:60-85]()
- [src/webportal/package.json:33-96]()
- [src/webportal/src/app/home/home/conn.js:4-17]()

## Main Pages and Features

### Home Dashboard

The home dashboard provides a comprehensive overview of the system status, displaying:

1. **Job Status Panel**: Summary of job statuses (waiting, running, stopped, failed, succeeded)
2. **Virtual Cluster Statistics**: Resource utilization for each virtual cluster
3. **GPU Node Availability**: Chart showing available GPU nodes  
4. **Job Lists**:
   - For administrators: Abnormal jobs list and recent jobs
   - For regular users: Recent jobs list

```mermaid
flowchart TD
    Home["Home Dashboard"] --> JobStatus["Job Status\n(counts by state)"]
    Home --> VCStats["Virtual Cluster\nStatistics"]
    Home --> GPUChart["GPU Node\nAvailability Chart"]
    Home --> JobLists["Job Lists"]
    
    JobLists --> AbnormalJobs["Abnormal Jobs\n(admin only)"]
    JobLists --> RecentJobs["Recent Jobs"]
    
    AbnormalJobs --> LongRunning["Long Running Jobs"]
    AbnormalJobs --> LowGPUUsage["Low GPU Usage Jobs"]
```

Sources:
- [src/webportal/src/app/home/home.jsx:49-214]()
- [src/webportal/src/app/home/home/job-status.jsx:79-159]()
- [src/webportal/src/app/home/home/virtual-cluster-statistics.jsx:246-295]()
- [src/webportal/src/app/home/home/gpu-chart.jsx:45-302]()
- [src/webportal/src/app/home/home/abnormal-job-list.jsx:51-218]()
- [src/webportal/src/app/home/home/recent-job-list.jsx:139-170]()

### Job Submission

The portal provides interfaces for submitting jobs to the OpenPAI platform:

1. **Job Submission Form**: User-friendly form to configure and submit jobs
2. **Protocol YAML Editor**: Advanced editor for directly editing job protocol YAML
3. **Marketplace Integration**: Option to choose templates from the marketplace

Users can submit jobs using different methods:
- Through a structured form interface
- By uploading protocol YAML files 
- By selecting and customizing templates from the marketplace

Sources:
- [contrib/submit-job-v2/src/App/ProtocolForm.tsx:150-1041]()
- [contrib/submit-job-v2/README.md:1-53]()
- [src/webportal/config/webpack.common.js:69-71]()

### Job List and Management

The job list view provides:

1. **Filterable Table**: List of jobs with sorting and filtering capabilities
2. **Status Visualization**: Visual indicators of job statuses
3. **Management Actions**: Options to stop, view details, or manage jobs
4. **Search and Filter**: Capabilities to find specific jobs

The interface allows users to view their own jobs, while administrators can see and manage all jobs in the system.

Sources:
- [src/webportal/config/webpack.common.js:72-76]()
- [src/webportal/src/app/home/home/recent-job-list.jsx:89-170]()
- [src/webportal/src/app/home/home/abnormal-job-list.jsx:56-176]()

### Resource Monitoring

The portal provides visualizations for monitoring cluster resources:

1. **Virtual Cluster Utilization**: Charts showing memory, CPU, and GPU usage for each virtual cluster
2. **GPU Allocation**: Visualization of GPU allocation across nodes
3. **Resource Bars**: Intuitive progress bars showing resource utilization percentages

```mermaid
flowchart TD
    VCStats["Virtual Cluster Statistics"] --> AllocationChart["Allocation Utilization Chart"]
    VCStats --> ResourceDetails["Resource Detail Tables"]
    
    ResourceDetails --> MemoryBars["Memory Utilization Bars"]
    ResourceDetails --> CPUBars["CPU Utilization Bars"]
    ResourceDetails --> GPUBars["GPU Utilization Bars"]
    
    GPUChart["GPU Chart"] --> NodeCount["Node Count by GPU Number"]
    GPUChart --> SharedNodes["Shared VC Nodes"]
    GPUChart --> DedicatedNodes["Dedicated VC Nodes"]
```

Sources:
- [src/webportal/src/app/home/home/virtual-cluster-statistics.jsx:205-295]()
- [src/webportal/src/app/home/home/gpu-chart.jsx:45-302]()
- [src/webportal/src/app/home/home/resource-bar.jsx:16-79]()
- [src/webportal/src/app/home/home/utilization-chart.jsx:28-101]()

## User Interface Components

### Layout Components

The Web Portal uses a consistent layout structure with:

1. **Navigation Bar**: Top navigation with user menu and notifications
2. **Sidebar**: Left sidebar for navigation between different sections
3. **Content Area**: Main content area for displaying page content

The UI is built with responsive design, adapting to different screen sizes using media queries.

```mermaid
flowchart TD
    Layout["Layout Component"] --> Navbar["Navigation Bar"]
    Layout --> Sidebar["Sidebar Navigation"]
    Layout --> Content["Content Area"]
    
    Navbar --> Logo["PAI Logo"]
    Navbar --> Notifications["Notification Button"]
    Navbar --> Help["Help Link"]
    Navbar --> UserMenu["User Menu"]
    
    UserMenu --> Profile["User Profile"]
    UserMenu --> Logout["Logout"]
    
    Content --> RouterOutput["Router Output\n(Different Pages)"]
```

Sources:
- [src/webportal/src/app/layout/components/navbar.jsx:28-197]()
- [src/webportal/config/webpack.common.js:65]()

### Data Visualization Components

The Web Portal uses various visualization components:

1. **C3.js Charts**: For GPU utilization and cluster statistics
2. **Resource Bars**: Custom progress bars showing resource utilization
3. **Status Badges**: Visual indicators of job statuses
4. **Detail Lists**: Office UI Fabric DetailsList components for tabular data

These components provide intuitive visualizations of complex system data.

Sources:
- [src/webportal/src/app/home/home/utilization-chart.jsx:28-101]()
- [src/webportal/src/app/home/home/resource-bar.jsx:16-79]()
- [src/webportal/src/app/home/home/c3.scss:1-312]()

## Data Flow

The Web Portal interacts with the REST API to retrieve and manipulate data. The general flow is:

1. **User Authentication**: User logs in and receives an authentication token
2. **Data Fetching**: Components request data from the REST API using the token
3. **Data Display**: Retrieved data is processed and displayed in the UI
4. **User Actions**: User actions (e.g., submitting a job) are sent to the REST API
5. **Feedback**: Results of actions are displayed to the user

```mermaid
sequenceDiagram
    participant User as User
    participant WebPortal as Web Portal
    participant RestAPI as REST Server API
    participant Backend as OpenPAI Backend
    
    User->>WebPortal: Access portal
    WebPortal->>RestAPI: Authenticate (token)
    RestAPI-->>WebPortal: Authentication response
    
    WebPortal->>RestAPI: Request data (job list, cluster info)
    RestAPI->>Backend: Process request
    Backend-->>RestAPI: Return data
    RestAPI-->>WebPortal: Return formatted data
    WebPortal-->>User: Display data
    
    User->>WebPortal: Submit job
    WebPortal->>RestAPI: Create job request
    RestAPI->>Backend: Process job creation
    Backend-->>RestAPI: Job creation result
    RestAPI-->>WebPortal: Job submission response
    WebPortal-->>User: Display submission result
```

Sources:
- [src/webportal/src/app/home/home.jsx:60-89]()
- [src/webportal/src/app/home/home/conn.js:26-151]()
- [src/webportal/src/app/components/util/job.js:23-150]()

## Admin vs. User Views

The Web Portal provides different views based on user roles:

### Administrator View
- Complete job list for all users
- Abnormal job monitoring and management
- Cluster resource management
- Virtual cluster administration

### Regular User View
- Personal job list and management
- Virtual clusters assigned to the user
- Resource usage for accessible virtual clusters

The role-based views ensure appropriate access control while providing the necessary functionality for each user type.

Sources:
- [src/webportal/src/app/home/home.jsx:58-203]()
- [src/webportal/src/app/home/home/virtual-cluster-statistics.jsx:46-203]()
- [src/webportal/src/app/home/home/job-status.jsx:79-159]()

## Special Features

### Abnormal Job Detection

The Web Portal includes intelligent detection of abnormal jobs:

1. **Long-Running Jobs**: Jobs that have been running for an unusually long time (over 5 days)
2. **Low GPU Usage Jobs**: Running jobs with GPU utilization below 10%

Administrators can easily identify and manage these jobs to improve cluster efficiency.

```mermaid
flowchart TD
    AbnormalDetection["Abnormal Job Detection"] --> LongRunning["Long Running Jobs\n(>5 days)"]
    AbnormalDetection --> LowGPU["Low GPU Usage\n(<10%)"]
    
    LongRunning --> Identify["Identify from\njob duration"]
    LowGPU --> Prometheus["Query from\nPrometheus metrics"]
    
    Identify --> Display["Display in\nAbnormal Jobs List"]
    Prometheus --> Display
    
    Display --> ManagementOptions["Management Options\n(Stop, View Details)"]
```

Sources:
- [src/webportal/src/app/components/util/job.js:21-150]()
- [src/webportal/src/app/home/home/conn.js:123-144]()
- [src/webportal/src/app/home/home/abnormal-job-list.jsx:51-218]()

### Resource Visualization

The portal provides detailed visualizations of cluster resources:

1. **Virtual Cluster Statistics**: Shows used vs. total resources for each virtual cluster
2. **GPU Node Distribution**: Chart showing the distribution of nodes by number of GPUs
3. **Resource Utilization Bars**: Visual indicators of resource usage percentages

These visualizations help users and administrators understand the current state of the cluster and make informed decisions.

Sources:
- [src/webportal/src/app/home/home/virtual-cluster-statistics.jsx:29-203]()
- [src/webportal/src/app/home/home/gpu-chart.jsx:45-302]()
- [src/webportal/src/app/home/home/resource-bar.jsx:16-79]()

## Summary

The OpenPAI Web Portal provides a comprehensive user interface for interacting with the OpenPAI platform. It offers intuitive visualizations, efficient job management, and resource monitoring capabilities. The modular, React-based architecture allows for easy extension and maintenance, while the responsive design ensures usability across various devices.

---

# Page: Job Submission

# Job Submission

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [contrib/submit-job-v2/README.md](contrib/submit-job-v2/README.md)
- [contrib/submit-job-v2/package.json](contrib/submit-job-v2/package.json)
- [contrib/submit-job-v2/src/App/ProtocolForm.tsx](contrib/submit-job-v2/src/App/ProtocolForm.tsx)
- [contrib/submit-job-v2/src/App/TensorBoard.tsx](contrib/submit-job-v2/src/App/TensorBoard.tsx)
- [contrib/submit-job-v2/src/index.ts](contrib/submit-job-v2/src/index.ts)
- [contrib/submit-job-v2/webpack.config.js](contrib/submit-job-v2/webpack.config.js)
- [contrib/submit-job-v2/yarn.lock](contrib/submit-job-v2/yarn.lock)
- [src/rest-server/src/controllers/v2/cluster.js](src/rest-server/src/controllers/v2/cluster.js)
- [src/rest-server/src/routes/v2/cluster.js](src/rest-server/src/routes/v2/cluster.js)
- [src/webportal/config/webpack.common.js](src/webportal/config/webpack.common.js)
- [src/webportal/package.json](src/webportal/package.json)
- [src/webportal/src/app/job-submission/components/basic-section.jsx](src/webportal/src/app/job-submission/components/basic-section.jsx)
- [src/webportal/src/app/job-submission/components/context.jsx](src/webportal/src/app/job-submission/components/context.jsx)
- [src/webportal/src/app/job-submission/components/controls/tooltip-icon.jsx](src/webportal/src/app/job-submission/components/controls/tooltip-icon.jsx)
- [src/webportal/src/app/job-submission/components/customized-components.jsx](src/webportal/src/app/job-submission/components/customized-components.jsx)
- [src/webportal/src/app/job-submission/components/docker-section.jsx](src/webportal/src/app/job-submission/components/docker-section.jsx)
- [src/webportal/src/app/job-submission/components/form-text-field.jsx](src/webportal/src/app/job-submission/components/form-text-field.jsx)
- [src/webportal/src/app/job-submission/components/job-information.jsx](src/webportal/src/app/job-submission/components/job-information.jsx)
- [src/webportal/src/app/job-submission/components/sidebar/sidebar-card.jsx](src/webportal/src/app/job-submission/components/sidebar/sidebar-card.jsx)
- [src/webportal/src/app/job-submission/components/submission-section.jsx](src/webportal/src/app/job-submission/components/submission-section.jsx)
- [src/webportal/src/app/job-submission/components/tab-form-content.jsx](src/webportal/src/app/job-submission/components/tab-form-content.jsx)
- [src/webportal/src/app/job-submission/components/task-role/completion-policy.jsx](src/webportal/src/app/job-submission/components/task-role/completion-policy.jsx)
- [src/webportal/src/app/job-submission/job-submission-page.jsx](src/webportal/src/app/job-submission/job-submission-page.jsx)
- [src/webportal/src/app/job-submission/job-submission.jsx](src/webportal/src/app/job-submission/job-submission.jsx)
- [src/webportal/src/app/job-submission/models/completion.js](src/webportal/src/app/job-submission/models/completion.js)
- [src/webportal/src/app/job-submission/models/docker-info.js](src/webportal/src/app/job-submission/models/docker-info.js)
- [src/webportal/src/app/job-submission/models/job-protocol.js](src/webportal/src/app/job-submission/models/job-protocol.js)
- [src/webportal/src/app/job-submission/models/job-task-role.js](src/webportal/src/app/job-submission/models/job-task-role.js)
- [src/webportal/src/app/job-submission/models/protocol-schema.js](src/webportal/src/app/job-submission/models/protocol-schema.js)
- [src/webportal/src/app/job-submission/utils/conn.js](src/webportal/src/app/job-submission/utils/conn.js)
- [src/webportal/src/app/job-submission/utils/constants.js](src/webportal/src/app/job-submission/utils/constants.js)
- [src/webportal/src/app/job-submission/utils/task-roles-manager.js](src/webportal/src/app/job-submission/utils/task-roles-manager.js)
- [src/webportal/src/app/job-submission/utils/utils.js](src/webportal/src/app/job-submission/utils/utils.js)
- [src/webportal/yarn.lock](src/webportal/yarn.lock)

</details>



This page explains the job submission functionality in OpenPAI, which allows users to define and submit AI workloads to be executed on the cluster. It covers the job submission interface, configuration options, and submission process. For information on monitoring and managing submitted jobs, see the [Job List View](#5.2) and [Job Detail View](#5.3) pages.

## 1. Job Submission Overview

The job submission feature provides a user-friendly interface for defining and submitting jobs to the OpenPAI platform. Users can create job configurations either through a form-based interface or by directly editing YAML configurations.

### Job Submission Flow

```mermaid
flowchart TD
    User["User"] --> WebPortal["Web Portal"]
    WebPortal --> SubmissionForm["Job Submission Form"]
    WebPortal --> YamlEditor["YAML Editor"]
    WebPortal --> Templates["Job Templates"]
    SubmissionForm --> JobProtocol["Job Protocol"]
    YamlEditor --> JobProtocol
    Templates --> JobProtocol
    JobProtocol --> RESTServer["REST Server API"]
    RESTServer --> Kubernetes["Kubernetes API"]
    Kubernetes --> FrameworkController["Framework Controller"]
    FrameworkController --> JobPods["Job Pods"]

    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px;
```

Sources:
- [src/webportal/src/app/job-submission/job-submission-page.jsx:73-106](src/webportal/src/app/job-submission/job-submission-page.jsx:73-106)
- [src/webportal/src/app/job-submission/components/submission-section.jsx:225-236](src/webportal/src/app/job-submission/components/submission-section.jsx:225-236)
- [src/webportal/src/app/job-submission/utils/conn.js:44-47](src/webportal/src/app/job-submission/utils/conn.js:44-47)

## 2. Job Protocol Structure

All jobs in OpenPAI are defined using a protocol schema. The job protocol represents the complete job configuration, including task roles, resource requirements, commands to execute, and more.

### Key Protocol Components

```mermaid
classDiagram
    JobProtocol -- JobBasicInfo
    JobProtocol -- TaskRole
    JobProtocol -- Parameters
    JobProtocol -- Secrets
    JobProtocol -- Prerequisites
    TaskRole -- DockerInfo
    TaskRole -- ContainerSize
    TaskRole -- Completion
    TaskRole -- Deployment
    
    class JobProtocol {
        +name: string
        +description: string
        +type: "job"
        +jobRetryCount: number
        +parameters: object
        +taskRoles: object
        +prerequisites: array
        +secrets: object
        +extras: object
    }
    
    class JobBasicInfo {
        +name: string
        +virtualCluster: string
    }
    
    class TaskRole {
        +name: string
        +instances: number
        +commands: string[]
        +containerSize: ContainerSize
        +dockerInfo: DockerInfo
        +completion: Completion
    }
    
    class DockerInfo {
        +uri: string
        +auth: object
    }
    
    class Parameters {
        +key: string
        +value: string
    }
    
    class Secrets {
        +key: string
        +value: string
    }
    
    class ContainerSize {
        +cpu: number
        +memoryMB: number
        +gpu: number
    }
```

Sources:
- [src/webportal/src/app/job-submission/models/protocol-schema.js:29-190](src/webportal/src/app/job-submission/models/protocol-schema.js:29-190)
- [src/webportal/src/app/job-submission/models/job-protocol.js:35-189](src/webportal/src/app/job-submission/models/job-protocol.js:35-189)
- [src/webportal/src/app/job-submission/models/job-task-role.js:38-209](src/webportal/src/app/job-submission/models/job-task-role.js:38-209)

## 3. Job Submission Interface

The job submission interface consists of several key components that allow users to configure their jobs.

### Interface Components

```mermaid
flowchart TD
    JSP["JobSubmissionPage"] --> Topbar["Topbar"]
    JSP --> JobInformation["JobInformation"]
    JSP --> TaskRoles["TaskRoles"]
    JSP --> Sidebar["Sidebar"]
    JSP --> SubmissionSection["SubmissionSection"]
    
    Sidebar --> Parameters["Parameters"]
    Sidebar --> Secrets["Secrets"]
    Sidebar --> EnvVar["Environment Variables"]
    Sidebar --> Data["Data Configuration"]
    Sidebar --> Tool["Tool Configuration"]
    
    TaskRoles --> TaskRole["TaskRole Form"]
    TaskRole --> DockerSection["Docker Section"]
    TaskRole --> CommandSection["Command Section"]
    TaskRole --> ContainerSize["Container Size"]
    TaskRole --> Ports["Ports"]
    
    SubmissionSection --> ProtocolYAML["Protocol YAML"]

    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px;
```

Sources:
- [src/webportal/src/app/job-submission/job-submission-page.jsx:420-552](src/webportal/src/app/job-submission/job-submission-page.jsx:420-552)
- [src/webportal/config/webpack.common.js:67-70](src/webportal/config/webpack.common.js:67-70)

### Form Sections

#### 1. Job Information

The job information section allows users to specify basic job information:

- **Job name**: A unique identifier for the job (must match pattern `/^[A-Za-z0-9\-._~]+$/`)
- **Virtual cluster**: The virtual cluster to run the job on
- **Retry count**: (Advanced) Number of times to retry the job if it fails

Sources:
- [src/webportal/src/app/job-submission/components/job-information.jsx:67-94](src/webportal/src/app/job-submission/components/job-information.jsx:67-94)
- [src/webportal/src/app/job-submission/components/job-information.jsx:36-37](src/webportal/src/app/job-submission/components/job-information.jsx:36-37)

#### 2. Task Roles

Task roles define the individual components of a job. Each task role can have:

- **Task role name**: Identifier for the task role (must match pattern `/^[a-z0-9]{1,63}$/`)
- **Instances**: Number of instances of this task role to create
- **Docker image**: Container image to use for the task
- **Commands**: Shell commands to execute in the container
- **Resource requirements**: CPU, memory, GPU allocation
- **Ports**: Port mappings for the container
- **Completion policy**: Rules for job completion based on task status

Sources:
- [src/webportal/src/app/job-submission/components/tab-form-content.jsx:44-185](src/webportal/src/app/job-submission/components/tab-form-content.jsx:44-185)
- [src/webportal/src/app/job-submission/models/job-task-role.js:38-209](src/webportal/src/app/job-submission/models/job-task-role.js:38-209)

#### 3. Docker Settings

Docker settings allow users to configure the container environment:

- **Pre-defined images**: Select from common AI frameworks (PyTorch, TensorFlow, etc.)
- **Custom image**: Specify a custom Docker image URI
- **Authentication**: Provide credentials for private Docker registries

Sources:
- [src/webportal/src/app/job-submission/components/docker-section.jsx:26-208](src/webportal/src/app/job-submission/components/docker-section.jsx:26-208)
- [src/webportal/src/app/job-submission/utils/constants.js:116-169](src/webportal/src/app/job-submission/utils/constants.js:116-169)

#### 4. Parameters and Secrets

- **Parameters**: Key-value pairs that can be referenced in commands
- **Secrets**: Sensitive values (passwords, tokens) that are securely stored

Sources:
- [src/webportal/src/app/job-submission/components/sidebar/parameters.jsx](src/webportal/src/app/job-submission/components/sidebar/parameters.jsx)
- [src/webportal/src/app/job-submission/components/sidebar/secrets.jsx](src/webportal/src/app/job-submission/components/sidebar/secrets.jsx)

#### 5. Data and Tools

- **Data mounts**: Configure data sources to be mounted in the job containers
- **Tool configurations**: Set up debugging tools like SSH and TensorBoard

Sources:
- [src/webportal/src/app/job-submission/components/data/data-component.jsx](src/webportal/src/app/job-submission/components/data/data-component.jsx)
- [src/webportal/src/app/job-submission/components/tools/tool-component.jsx](src/webportal/src/app/job-submission/components/tools/tool-component.jsx)

## 4. Job Submission Process

### Form to Protocol Conversion

When a user configures a job using the form interface, the UI components create a structured job protocol object that is then converted to YAML format for submission.

```mermaid
sequenceDiagram
    participant User
    participant UI as "Job Submission UI"
    participant Protocol as "JobProtocol"
    participant REST as "REST Server"
    participant Kube as "Kubernetes"
    
    User->>UI: Fill job form
    UI->>Protocol: Create JobProtocol object
    Note over Protocol: Validate protocol
    UI->>UI: Show validation errors
    User->>UI: Submit job
    UI->>Protocol: Generate YAML
    Protocol->>REST: Submit job protocol
    REST->>Kube: Create framework
    Kube->>User: Redirect to job detail page
```

Sources:
- [src/webportal/src/app/job-submission/components/submission-section.jsx:99-119](src/webportal/src/app/job-submission/components/submission-section.jsx:99-119)
- [src/webportal/src/app/job-submission/components/submission-section.jsx:225-236](src/webportal/src/app/job-submission/components/submission-section.jsx:225-236)
- [src/webportal/src/app/job-submission/utils/conn.js:44-47](src/webportal/src/app/job-submission/utils/conn.js:44-47)

### Protocol Validation

The job protocol is validated against a schema before submission to ensure it meets all requirements.

```javascript
// Schema validation process
const valid = JobProtocol.validateFromYaml(text);
setValidationMsg(valid);
```

If validation fails, error messages are displayed, and submission is prevented.

Sources:
- [src/webportal/src/app/job-submission/components/submission-section.jsx:182-194](src/webportal/src/app/job-submission/components/submission-section.jsx:182-194)
- [src/webportal/src/app/job-submission/models/job-protocol.js:75-106](src/webportal/src/app/job-submission/models/job-protocol.js:75-106)

## 5. Advanced Features

### Job Templates

Users can save and reuse job configurations as templates, making it easy to launch similar jobs in the future.

```mermaid
flowchart TD
    User["User"] --> SelectTemplate["Select Template"]
    User --> FillForm["Fill Job Form"]
    User --> EditYAML["Edit YAML"]
    
    SelectTemplate --> SubmitJob["Submit Job"]
    FillForm --> SaveTemplate["Save as Template"]
    FillForm --> SubmitJob
    EditYAML --> SaveTemplate
    EditYAML --> SubmitJob
    
    SaveTemplate --> TemplateStorage["Template Storage"]
    TemplateStorage --> SelectTemplate

    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px;
```

Sources:
- [src/webportal/src/app/job-submission/job-submission-page.jsx:383-404](src/webportal/src/app/job-submission/job-submission-page.jsx:383-404)
- [src/webportal/src/app/job-submission/components/submission-section.jsx:197-223](src/webportal/src/app/job-submission/components/submission-section.jsx:197-223)
- [src/webportal/src/app/job-submission/utils/conn.js:129-172](src/webportal/src/app/job-submission/utils/conn.js:129-172)

### Environment Variables

OpenPAI provides predefined environment variables that can be referenced in job commands:

| Variable | Description |
|----------|-------------|
| PAI_JOB_NAME | Job name in config file |
| PAI_USER_NAME | User who submitted the job |
| PAI_DEFAULT_FS_URI | Default file system URI in PAI |
| PAI_TASK_ROLE_COUNT | Total number of task roles |
| PAI_TASK_ROLE_LIST | Comma-separated task role names |
| PAI_TASK_ROLE_TASK_COUNT_$taskRole | Task count of the task role |
| PAI_HOST_IP_$taskRole_$taskIndex | The host IP for a specific task |
| PAI_RESOURCE_$taskRole | Resource requirement in "gpuNumber,cpuNumber,memMB,shmMB" format |

Sources:
- [src/webportal/src/app/job-submission/utils/constants.js:31-85](src/webportal/src/app/job-submission/utils/constants.js:31-85)

### Direct YAML Editing

Advanced users can directly edit the job protocol YAML for fine-grained control over the job configuration.

Sources:
- [src/webportal/src/app/job-submission/components/submission-section.jsx:121-180](src/webportal/src/app/job-submission/components/submission-section.jsx:121-180)

## 6. Implementation Details

### Main Components

The job submission feature is implemented primarily in React, with the following key components:

| Component | Purpose |
|-----------|---------|
| JobSubmissionPage | Main container for the submission interface |
| JobInformation | Form for job basic information |
| TaskRoles | Management of task role configurations |
| SubmissionSection | Job submission controls and YAML editor |
| Parameters/Secrets | Sidebar components for parameter/secret management |
| DockerSection | Docker image configuration |
| CommandSection | Command input for task roles |

Sources:
- [src/webportal/src/app/job-submission/job-submission.jsx:35-77](src/webportal/src/app/job-submission/job-submission.jsx:35-77)
- [src/webportal/src/app/job-submission/job-submission-page.jsx:73-552](src/webportal/src/app/job-submission/job-submission-page.jsx:73-552)

### Protocol Models

The submission interface uses several model classes to represent job components:

| Model | Description |
|-------|-------------|
| JobProtocol | Represents the full job protocol and handles validation |
| JobBasicInfo | Stores basic job information (name, VC, etc.) |
| JobTaskRole | Represents a task role configuration |
| DockerInfo | Contains Docker image settings |
| Completion | Defines job completion policies |

Sources:
- [src/webportal/src/app/job-submission/models/job-protocol.js:35-189](src/webportal/src/app/job-submission/models/job-protocol.js:35-189)
- [src/webportal/src/app/job-submission/models/job-task-role.js:38-209](src/webportal/src/app/job-submission/models/job-task-role.js:38-209)
- [src/webportal/src/app/job-submission/models/docker-info.js:1-200](src/webportal/src/app/job-submission/models/docker-info.js:1-200)

### API Connectivity

The job submission page communicates with the OpenPAI REST API to:

1. Fetch available virtual clusters
2. Retrieve storage configurations
3. List available Kubernetes SKU types
4. Submit jobs
5. Fetch and save templates

Sources:
- [src/webportal/src/app/job-submission/utils/conn.js:14-172](src/webportal/src/app/job-submission/utils/conn.js:14-172)

## 7. Additional Resources

- The job protocol schema is documented at: https://github.com/microsoft/openpai-protocol/blob/master/schemas/v2/schema.yaml
- For information about monitoring jobs after submission, see the [Job List View](#5.2) and [Job Detail View](#5.3) pages.
- For debugging jobs, see the [Job Event](#5.3) and [Task Attempt](#5.3) pages.

---

# Page: Job List View

# Job List View

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/webportal/src/app/job/job-view/fabric/JobList/Context.js](src/webportal/src/app/job/job-view/fabric/JobList/Context.js)
- [src/webportal/src/app/job/job-view/fabric/JobList/Filter.js](src/webportal/src/app/job/job-view/fabric/JobList/Filter.js)
- [src/webportal/src/app/job/job-view/fabric/JobList/FilterButton.jsx](src/webportal/src/app/job/job-view/fabric/JobList/FilterButton.jsx)
- [src/webportal/src/app/job/job-view/fabric/JobList/Ordering.js](src/webportal/src/app/job/job-view/fabric/JobList/Ordering.js)
- [src/webportal/src/app/job/job-view/fabric/JobList/Pagination.js](src/webportal/src/app/job/job-view/fabric/JobList/Pagination.js)
- [src/webportal/src/app/job/job-view/fabric/JobList/Paginator.jsx](src/webportal/src/app/job/job-view/fabric/JobList/Paginator.jsx)
- [src/webportal/src/app/job/job-view/fabric/JobList/Table.jsx](src/webportal/src/app/job/job-view/fabric/JobList/Table.jsx)
- [src/webportal/src/app/job/job-view/fabric/JobList/TopBar.jsx](src/webportal/src/app/job/job-view/fabric/JobList/TopBar.jsx)
- [src/webportal/src/app/job/job-view/fabric/JobList/index.jsx](src/webportal/src/app/job/job-view/fabric/JobList/index.jsx)

</details>



The Job List View provides a comprehensive interface for users to view, filter, sort, and manage jobs in the OpenPAI platform. This page documents the functionality and implementation of the job listing interface, which serves as the central dashboard for monitoring and managing all jobs in the system.

For information about submitting new jobs, see [Job Submission](#5.1). For detailed information about a specific job, see [Job Detail View](#5.3).

## Overview

The Job List View displays all jobs in a tabular format with extensive filtering, sorting, and pagination capabilities. It allows users to:

- View all jobs or filter by various criteria
- Sort jobs by different attributes
- Navigate through pages of job results
- Stop running jobs
- Access detailed information about specific jobs

```mermaid
graph TD
    User["User"] --> JobList["Job List View"]
    JobList --> Filter["Filtering System"]
    JobList --> Sort["Sorting System"]
    JobList --> Paginate["Pagination System"]
    JobList --> Actions["Job Actions"]
    JobList --> REST["REST API"]
    
    Filter --> REST
    Sort --> REST
    Paginate --> REST
    Actions --> REST
    
    REST --> K8s["Kubernetes API"]
```

Sources: 
- [src/webportal/src/app/job/job-view/fabric/JobList/index.jsx:38-336]()
- [src/webportal/src/app/job/job-view/fabric/JobList/Table.jsx:40-345]()

## Component Architecture

The Job List View is built using React with a component-based architecture. It uses React Context for state management and communicates with the OpenPAI REST API to fetch and manipulate job data.

```mermaid
graph TD
    subgraph "Core Components"
        JobList["JobList (index.jsx)"]
        Context["Context Provider"]
        Table["Table Component"]
        TopBar["TopBar Component"]
        Paginator["Paginator Component"]
    end
    
    subgraph "State Management"
        Filter["Filter (Filter.js)"]
        Ordering["Ordering (Ordering.js)"]
        Pagination["Pagination (Pagination.js)"]
        FilterButton["FilterButton Component"]
    end
    
    subgraph "API Communication"
        PAIV2["PAIV2.OpenPAIClient"]
        RESTServer["REST Server API"]
    end
    
    JobList --> Context
    Context --> Table
    Context --> TopBar
    Context --> Paginator
    
    TopBar --> FilterButton
    FilterButton --> Filter
    
    Context --> Filter
    Context --> Ordering
    Context --> Pagination
    
    Context --> PAIV2
    PAIV2 --> RESTServer
```

Sources:
- [src/webportal/src/app/job/job-view/fabric/JobList/index.jsx:25-36]()
- [src/webportal/src/app/job/job-view/fabric/JobList/Context.js:1-42]()

## User Interface

The Job List View interface consists of several key sections:

1. **Top Bar**: Contains action buttons (Stop, New, Refresh) and filter controls
2. **Filter Panel**: Expandable panel with filters for Priority, User, Virtual Cluster, and Status
3. **Job Table**: Displays jobs with multiple columns for different job attributes
4. **Pagination Controls**: Navigation controls for moving through pages of results

### Job Table Columns

The table displays the following information for each job:

| Column | Description | Sortable |
|--------|-------------|----------|
| Name | Job name (links to Job Detail) | Yes |
| Submission Time | When the job was submitted | Yes |
| User | Job owner username | Yes |
| Duration | Job running time | No |
| Virtual Cluster | Virtual cluster the job runs on | Yes |
| Retries | Number of retries | Yes |
| Tasks | Number of tasks in the job | Yes |
| GPUs | Number of GPUs used | Yes |
| Priority | Job priority (Default, Product, Test, Opportunistic) | Yes |
| Status | Current job status | Yes |
| Actions | Available actions (e.g., Stop) | No |

Sources:
- [src/webportal/src/app/job/job-view/fabric/JobList/Table.jsx:100-284]()
- [src/webportal/src/app/job/job-view/fabric/JobList/TopBar.jsx:72-423]()

## Filtering System

The Job List View provides comprehensive filtering capabilities through multiple mechanisms:

1. **Keyword Search**: Filter jobs by a text keyword
2. **Priority Filter**: Filter by job priority (Default, Product, Test, Opportunistic)
3. **User Filter**: Filter by job owner
4. **Virtual Cluster Filter**: Filter by the virtual cluster
5. **Status Filter**: Filter by job status (Waiting, Running, Succeeded, Failed, Stopped)

The filter state is persisted in local storage, so user preferences are remembered between sessions. URL parameters can also be used to apply filters directly.

```mermaid
graph TD
    subgraph "Filter Types"
        Keyword["Keyword Filter"]
        Priority["Priority Filter"]
        User["User Filter"]
        VC["Virtual Cluster Filter"]
        Status["Status Filter"]
    end
    
    subgraph "Filter Components"
        TopBar["TopBar Component"]
        FilterButton["FilterButton Component"]
        SearchBox["KeywordSearchBox Component"]
    end
    
    subgraph "Filter Implementation"
        FilterClass["Filter Class"]
        LocalStorage["LocalStorage"]
        URLParams["URL Parameters"]
    end
    
    TopBar --> SearchBox
    TopBar --> FilterButton
    
    SearchBox --> Keyword
    FilterButton --> Priority
    FilterButton --> User
    FilterButton --> VC
    FilterButton --> Status
    
    Keyword --> FilterClass
    Priority --> FilterClass
    User --> FilterClass
    VC --> FilterClass
    Status --> FilterClass
    
    FilterClass --> LocalStorage
    FilterClass --> URLParams
    URLParams --> FilterClass
    LocalStorage --> FilterClass
```

Sources:
- [src/webportal/src/app/job/job-view/fabric/JobList/Filter.js:6-106]()
- [src/webportal/src/app/job/job-view/fabric/JobList/TopBar.jsx:40-70]()
- [src/webportal/src/app/job/job-view/fabric/JobList/FilterButton.jsx:30-182]()

## Sorting System

The Job List View allows sorting jobs by various columns. Sorting is handled by the `Ordering` class, which manages the sort field and direction. Clicking a column header toggles between ascending, descending, and no sorting.

The sort state is persisted in local storage, so user preferences are remembered between sessions.

```mermaid
flowchart TD
    subgraph "UI Interaction"
        ColumnHeader["Column Header Click"]
    end
    
    subgraph "Ordering Implementation"
        OrderingClass["Ordering Class"]
        onColumnClick["onColumnClick Function"]
        applySortProps["applySortProps Function"]
    end
    
    subgraph "State and Storage"
        OrderingState["Current Ordering State"]
        LocalStorage["LocalStorage"]
    end
    
    subgraph "API Request"
        QueryParams["order Query Parameter"]
        APIRequest["REST API Request"]
    end
    
    ColumnHeader --> onColumnClick
    onColumnClick --> OrderingClass
    OrderingClass --> OrderingState
    OrderingState --> applySortProps
    OrderingClass --> LocalStorage
    LocalStorage --> OrderingClass
    
    OrderingClass --> QueryParams
    QueryParams --> APIRequest
```

Sources:
- [src/webportal/src/app/job/job-view/fabric/JobList/Ordering.js:6-88]()
- [src/webportal/src/app/job/job-view/fabric/JobList/Table.jsx:77-98]()

## Pagination System

The Job List View uses pagination to manage large sets of job results. The pagination is implemented with the `Pagination` class and the `Paginator` component, which provide controls for:

1. Setting the number of items per page (20, 50, or 100)
2. Navigating between pages
3. Jumping to a specific page

The pagination state is persisted in local storage, so user preferences are remembered between sessions.

```mermaid
graph TD
    subgraph "UI Components"
        PaginatorComponent["Paginator Component"]
        PageButtons["Page Navigation Buttons"]
        ItemsPerPageDropdown["Items Per Page Dropdown"]
        GotoPageInput["Go to Page Input"]
    end
    
    subgraph "Pagination Implementation"
        PaginationClass["Pagination Class"]
        LocalStorage["LocalStorage"]
    end
    
    subgraph "API Request"
        QueryParams["offset/limit Query Parameters"]
        APIRequest["REST API Request"]
    end
    
    PaginatorComponent --> PageButtons
    PaginatorComponent --> ItemsPerPageDropdown
    PaginatorComponent --> GotoPageInput
    
    PageButtons --> PaginationClass
    ItemsPerPageDropdown --> PaginationClass
    GotoPageInput --> PaginationClass
    
    PaginationClass --> LocalStorage
    LocalStorage --> PaginationClass
    
    PaginationClass --> QueryParams
    QueryParams --> APIRequest
```

Sources:
- [src/webportal/src/app/job/job-view/fabric/JobList/Pagination.js:6-47]()
- [src/webportal/src/app/job/job-view/fabric/JobList/Paginator.jsx:51-197]()

## Job Actions

The Job List View allows users to perform actions on jobs, primarily stopping running jobs. This functionality is implemented in the following way:

1. **Stop Button**: Each job row has a Stop button if the job is in a stoppable state
2. **Multi-Select**: Users can select multiple jobs and stop them all at once
3. **Confirmation Dialog**: A confirmation dialog is shown before stopping jobs

```mermaid
sequenceDiagram
    participant User
    participant StopButton as "Stop Button"
    participant ConfirmDialog as "Confirm Dialog"
    participant StopJob as "stopJob Function"
    participant PAIClient as "OpenPAI Client"
    participant REST as "REST API"
    
    User->>StopButton: Click Stop
    StopButton->>ConfirmDialog: Show dialog
    ConfirmDialog->>User: Confirm action
    User->>ConfirmDialog: Confirm
    ConfirmDialog->>StopJob: Call stopJob(job)
    StopJob->>PAIClient: Call updateJobExecutionType(username, name, 'STOP')
    PAIClient->>REST: HTTP Request
    REST-->>PAIClient: Response
    PAIClient-->>StopJob: Update job state
    StopJob-->>User: Update UI
```

Sources:
- [src/webportal/src/app/job/job-view/fabric/JobList/index.jsx:173-209]()
- [src/webportal/src/app/job/job-view/fabric/JobList/Table.jsx:237-284]()

## Data Fetching and Refresh

The Job List View fetches job data from the OpenPAI REST API. The data fetching is implemented with the following features:

1. **Initial Load**: Jobs are loaded when the component mounts
2. **Refresh Button**: Users can manually refresh the job list
3. **Filter/Sort/Paginate**: Jobs are re-fetched when filter, sort, or pagination changes
4. **Debouncing**: Changes to filters are debounced to prevent excessive API calls

```mermaid
sequenceDiagram
    participant Component as "JobList Component"
    participant Filter as "Filter"
    participant Ordering as "Ordering"
    participant Pagination as "Pagination"
    participant GetJobs as "getJobs Function"
    participant PAIClient as "OpenPAI Client"
    participant REST as "REST API"
    
    Component->>Component: Mount component
    Component->>Component: Initialize filter, ordering, pagination
    Component->>GetJobs: Call getJobs with parameters
    GetJobs->>PAIClient: Create OpenPAI client
    PAIClient->>REST: HTTP Request
    REST-->>PAIClient: Response with job data
    PAIClient-->>GetJobs: Return data
    GetJobs-->>Component: Update filteredJobsInfo state
    
    alt When filter changes
        Filter->>Component: Filter changes
        Component->>Component: Debounce
        Component->>GetJobs: Call getJobs with updated parameters
        GetJobs->>REST: New HTTP Request
        REST-->>Component: New job data
    end
    
    alt When ordering changes
        Ordering->>Component: Ordering changes
        Component->>Component: Debounce
        Component->>GetJobs: Call getJobs with updated parameters
        GetJobs->>REST: New HTTP Request
        REST-->>Component: New job data
    end
    
    alt When pagination changes
        Pagination->>Component: Pagination changes
        Component->>Component: Debounce
        Component->>GetJobs: Call getJobs with updated parameters
        GetJobs->>REST: New HTTP Request
        REST-->>Component: New job data
    end
    
    alt When refresh button clicked
        Component->>GetJobs: Call getJobs
        GetJobs->>REST: New HTTP Request
        REST-->>Component: New job data
    end
```

Sources:
- [src/webportal/src/app/job/job-view/fabric/JobList/index.jsx:116-257]()
- [src/webportal/src/app/job/job-view/fabric/JobList/TopBar.jsx:219-231]()

## Error Handling

The Job List View includes error handling for various scenarios:

1. **API Errors**: Errors from the REST API are caught and displayed to the user
2. **Authentication Errors**: If the user's token is invalid, they are redirected to login
3. **No Results**: A friendly message is shown when no jobs match the current filters

Sources:
- [src/webportal/src/app/job/job-view/fabric/JobList/index.jsx:129-135]()
- [src/webportal/src/app/job/job-view/fabric/JobList/Table.jsx:300-324]()

## State Persistence

The Job List View persists user preferences across sessions using local storage. This includes:

1. **Filter State**: The current filters are saved to local storage
2. **Ordering State**: The current sort field and direction are saved
3. **Pagination State**: The current page and items per page are saved

This allows users to maintain their view preferences between visits to the page.

Sources:
- [src/webportal/src/app/job/job-view/fabric/JobList/Filter.js:28-65]()
- [src/webportal/src/app/job/job-view/fabric/JobList/Ordering.js:16-57]()
- [src/webportal/src/app/job/job-view/fabric/JobList/Pagination.js:16-37]()

## Configuration and Customization

The Job List View can be accessed via URL parameters to customize the initial view. Supported parameters include:

- `vcName`: Filter by virtual cluster
- `status`: Filter by job status
- `user`: Filter by username
- `jobPriority`: Filter by job priority
- `keyword`: Filter by keyword
- `field`: Sort by field
- `descending`: Sort direction
- `pageIndex`: Initial page
- `itemsPerPage`: Items per page

This allows creating links to specific filtered views of the job list.

Sources:
- [src/webportal/src/app/job/job-view/fabric/JobList/index.jsx:45-105]()

---

# Page: Job Detail View

# Job Detail View

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/webportal/.browserslistrc](src/webportal/.browserslistrc)
- [src/webportal/src/app/components/status-badge.jsx](src/webportal/src/app/components/status-badge.jsx)
- [src/webportal/src/app/components/tachyons.scss](src/webportal/src/app/components/tachyons.scss)
- [src/webportal/src/app/components/theme.js](src/webportal/src/app/components/theme.js)
- [src/webportal/src/app/job/job-view/fabric/job-detail.jsx](src/webportal/src/app/job/job-view/fabric/job-detail.jsx)
- [src/webportal/src/app/job/job-view/fabric/job-detail/components/summary.jsx](src/webportal/src/app/job/job-view/fabric/job-detail/components/summary.jsx)
- [src/webportal/src/app/job/job-view/fabric/job-detail/components/task-role-container-list.jsx](src/webportal/src/app/job/job-view/fabric/job-detail/components/task-role-container-list.jsx)
- [src/webportal/src/app/job/job-view/fabric/job-detail/conn.js](src/webportal/src/app/job/job-view/fabric/job-detail/conn.js)
- [src/webportal/src/app/job/job-view/fabric/job-detail/util.js](src/webportal/src/app/job/job-view/fabric/job-detail/util.js)
- [src/webportal/src/app/job/job-view/fabric/job-event.jsx](src/webportal/src/app/job/job-view/fabric/job-event.jsx)
- [src/webportal/src/app/job/job-view/fabric/job-event/conn.js](src/webportal/src/app/job/job-view/fabric/job-event/conn.js)
- [src/webportal/src/app/job/job-view/fabric/job-event/job-event-list.jsx](src/webportal/src/app/job/job-view/fabric/job-event/job-event-list.jsx)
- [src/webportal/src/app/job/job-view/fabric/job-list.jsx](src/webportal/src/app/job/job-view/fabric/job-list.jsx)
- [src/webportal/src/app/job/job-view/fabric/task-attempt/conn.js](src/webportal/src/app/job/job-view/fabric/task-attempt/conn.js)
- [src/webportal/src/app/job/job-view/fabric/task-attempt/task-attempt-list.jsx](src/webportal/src/app/job/job-view/fabric/task-attempt/task-attempt-list.jsx)

</details>



## Purpose and Scope

The Job Detail View provides a comprehensive interface for monitoring and managing individual jobs in OpenPAI. This page documents the components, features, and usage of the Job Detail View interface, allowing users to track job status, access logs, and perform management actions. For information about submitting jobs, see [Job Submission](#5.1), and for viewing the list of all jobs, see [Job List View](#5.2).

## Architecture Overview

The Job Detail View is structured as a hierarchy of React components that retrieve and display job information from the REST Server API.

```mermaid
graph TD
    JobDetail["JobDetail Component"] --> Summary["Summary Component"]
    JobDetail --> TaskRoleContainer["TaskRoleContainerList"]
    JobDetail --> AttemptInfo["Job Attempt Information"]
    
    Summary --> JobStatus["Job Status Badge"]
    Summary --> JobActions["Job Actions (Stop, Clone)"]
    Summary --> JobLinks["Job Links (Metrics, Config)"]
    
    TaskRoleContainer --> TaskList["Task List"]
    TaskList --> TaskRow["Task Row"]
    
    TaskRow --> LogAccess["Log Access (stdout/stderr)"]
    TaskRow --> SSHInfo["SSH Information"]
    TaskRow --> ExitInfo["Exit Diagnostics"]
    
    JobDetail -- "API Calls" --> ConnMethods["Connection Methods"]
    ConnMethods -- "fetchJobInfo()" --> JobInfo["Job Information"]
    ConnMethods -- "fetchJobConfig()" --> JobConfig["Job Configuration"]
    ConnMethods -- "fetchSshInfo()" --> SSHConfig["SSH Configuration"]
    ConnMethods -- "getContainerLog()" --> Logs["Container Logs"]
```

Sources:
- [src/webportal/src/app/job/job-view/fabric/job-detail.jsx:49-552]()
- [src/webportal/src/app/job/job-view/fabric/job-detail/conn.js:1-211]()

## User Interface Components

The Job Detail View is composed of three main sections:

```mermaid
graph TB
    JobDetailView["Job Detail View"] --> SummarySection["1. Summary Section"]
    JobDetailView --> AttemptSection["2. Job Attempt Section"]
    JobDetailView --> TaskRoleSection["3. Task Role Sections"]
    
    SummarySection --> StatusInfo["Status Information"]
    SummarySection --> TimeInfo["Time & Duration"]
    SummarySection --> UserInfo["User & VC Info"]
    SummarySection --> ActionButtons["Action Buttons"]
    
    AttemptSection --> AttemptSelector["Attempt Selector"]
    AttemptSection --> AttemptStatus["Attempt Status"]
    AttemptSection --> AttemptDuration["Attempt Duration"]
    AttemptSection --> DiagnosticsToggle["More Diagnostics Toggle"]
    
    TaskRoleSection --> TaskRoleInfo["Task Role Information"]
    TaskRoleSection --> TaskRoleContainerList["Container List"]
    TaskRoleContainerList --> TaskDetails["Task Details"]
    TaskRoleContainerList --> LogAccess["Log Access"]
    TaskRoleContainerList --> SSHAccess["SSH Access"]
    TaskRoleContainerList --> ExitInfo["Exit Information"]
```

Sources:
- [src/webportal/src/app/job/job-view/fabric/job-detail.jsx:360-546]()
- [src/webportal/src/app/job/job-view/fabric/job-detail/components/summary.jsx:81-482]()

### 1. Job Summary Section

The summary section provides key information about the job and actions:

| Field | Description |
|-------|-------------|
| Job Name | Name of the job |
| Job State | Current state with visual status badge (Running, Waiting, Succeeded, Failed, Stopped) |
| Submission Time | When the job was submitted |
| User | Username of the job submitter |
| Virtual Cluster | The virtual cluster where the job is running |
| Duration | Total running time of the job |
| Retries | Number of job retry attempts |

The section also includes action buttons and links:
- View Job Config: Opens the job configuration in YAML/JSON format
- Go to Job Metrics Page: Links to Grafana dashboards for job metrics
- Go to Job Event Page: Shows job-related events
- TensorBoard Page: Available for jobs with TensorBoard enabled
- Clone/Stop buttons: Actions to clone or stop the job

Sources:
- [src/webportal/src/app/job/job-view/fabric/job-detail/components/summary.jsx:257-478]()
- [src/webportal/src/app/components/status-badge.jsx:151-168]()

### 2. Job Attempt Information

For jobs with multiple attempts (retries), this section provides:

- A dropdown to select different job attempts
- Information about the selected attempt:
  - Attempt state (with status badge)
  - Creation time and duration
  - Running start time and duration
- "View Exit Diagnostics" link for failed attempts
- "More Diagnostics" toggle for additional technical information

Sources:
- [src/webportal/src/app/job/job-view/fabric/job-detail.jsx:442-516]()

### 3. Task Role Container List

This section displays information about each task in a task role:

| Column | Description |
|--------|-------------|
| Task Index | Index number of the task |
| Task State | Current state with visual indicator |
| Task Retries | Number of retries for this task |
| IP | IP address of the container |
| Ports | Exposed ports of the container |
| Info & Logs | Buttons for accessing logs and SSH info |
| Exit Type | Type of exit for completed tasks |
| Exit Code | Exit code for completed tasks |

When "More Diagnostics" is enabled, additional columns appear:
- Running Start Time
- Running Duration
- Node Name
- Exit Diagnostics (button to show detailed diagnostics)
- Container ID

Sources:
- [src/webportal/src/app/job/job-view/fabric/job-detail/components/task-role-container-list.jsx:567-950]()
- [src/webportal/src/app/job/job-view/fabric/job-detail.jsx:526-531]()

## Key Features

### Log Access

The Task Role Container List provides multiple ways to access logs:

```mermaid
sequenceDiagram
    participant User
    participant TaskRow as "Task Row"
    participant LogAPI as "Container Log API"
    participant MonacoPanel as "Monaco Editor Panel"
    
    User->>TaskRow: Click "Stdout" button
    TaskRow->>LogAPI: getContainerLogList()
    LogAPI-->>TaskRow: Return log URLs
    TaskRow->>LogAPI: getContainerLog("stdout")
    LogAPI-->>TaskRow: Return log content
    TaskRow->>MonacoPanel: Show log in editor
    MonacoPanel-->>User: Display log content
    
    User->>MonacoPanel: Click "View Full Log"
    MonacoPanel->>User: Opens full log in new tab
```

Log viewing options:
1. **Stdout**: Shows standard output (last 16KB)
2. **Stderr**: Shows standard error (last 16KB)
3. **Stdout+Stderr**: Shows merged output and error streams
4. **Show All Logs**: Opens a dialog with links to all log files

Sources:
- [src/webportal/src/app/job/job-view/fabric/job-detail/components/task-role-container-list.jsx:719-789]()
- [src/webportal/src/app/job/job-view/fabric/job-detail/conn.js:159-210]()

### SSH Access

For running tasks, the view provides SSH information to connect to containers:

1. Click the "SSH Info" button for a task
2. A dialog appears with connection instructions
3. Follow the provided commands to connect to the container via SSH

The SSH information adapts to the job configuration, providing different instructions for Kubernetes-based jobs versus legacy deployment mode.

Sources:
- [src/webportal/src/app/job/job-view/fabric/job-detail/components/task-role-container-list.jsx:305-405]()

### Exit Diagnostics

For failed or completed tasks, detailed diagnostics are available:

```mermaid
graph TD
    ExitDiag["Exit Diagnostics"] --> ExitCode["Exit Code"]
    ExitDiag --> ExitType["Exit Type (USER_FAILURE, etc.)"]
    ExitDiag --> ExitSpec["Exit Specification"]
    ExitDiag --> ExitMessage["Exit Message"]
    
    ExitSpec --> Reason["Failure Reason"]
    ExitSpec --> Solution["Suggested Solutions"]
    ExitSpec --> Phrase["Exit Phrase"]
```

The diagnostics help users understand:
- Why a job or task failed
- What the exit code means
- Possible solutions to fix the issue
- Detailed error messages for troubleshooting

Sources:
- [src/webportal/src/app/job/job-view/fabric/job-detail/components/task-role-container-list.jsx:864-926]()
- [src/webportal/src/app/job/job-view/fabric/job-detail/components/summary.jsx:142-255]()
- [src/webportal/src/app/job/job-view/fabric/job-detail.jsx:185-245]()

## Data Flow and Interactions

The Job Detail View loads and updates data through REST API calls:

```mermaid
sequenceDiagram
    participant User
    participant JobDetail as "JobDetail Component"
    participant RESTServer as "REST Server API"
    
    User->>JobDetail: Access Job Detail page
    JobDetail->>RESTServer: fetchJobInfo()
    JobDetail->>RESTServer: fetchJobConfig()
    JobDetail->>RESTServer: fetchSshInfo()
    RESTServer-->>JobDetail: Return job data
    JobDetail-->>User: Render Job Detail View
    
    User->>JobDetail: Select job attempt
    JobDetail->>RESTServer: fetchJobInfo(attemptIndex)
    RESTServer-->>JobDetail: Return attempt data
    JobDetail-->>User: Update view with attempt data
    
    User->>JobDetail: View task logs
    JobDetail->>RESTServer: getContainerLogList()
    JobDetail->>RESTServer: getContainerLog()
    RESTServer-->>JobDetail: Return log data
    JobDetail-->>User: Display logs in Monaco editor
```

Sources:
- [src/webportal/src/app/job/job-view/fabric/job-detail.jsx:84-158]()
- [src/webportal/src/app/job/job-view/fabric/job-detail/conn.js:46-156]()

## Technical Implementation

The Job Detail View is implemented as a React component hierarchy:

- `JobDetail`: Main container component that fetches and manages job data
- `Summary`: Displays job summary information and actions
- `TaskRoleContainerList`: Displays task information for each task role
- `MonacoPanel`: Used for displaying logs and configuration

The components use auto-refresh functionality to update the display:
- Users can select refresh intervals (10s, 30s, 60s) or disable auto-refresh
- Components use a `Timer` component to trigger periodic updates

Sources:
- [src/webportal/src/app/job/job-view/fabric/job-detail.jsx:49-83]()
- [src/webportal/src/app/job/job-view/fabric/job-detail/components/summary.jsx:324-347]()
- [src/webportal/src/app/job/job-view/fabric/job-detail/components/task-role-container-list.jsx:528-534]()

## Usage Guide

### Viewing Job Status and Information

1. The Status Badge in the summary section indicates the current job state
2. Job duration, submission time, and other basic information is displayed in the summary
3. For failed jobs, look for error information and suggested solutions in the summary section
4. Use the auto-refresh dropdown to control how often the data updates

### Working with Job Attempts

1. Use the "Job Attempt Index" dropdown to select a specific job attempt
2. The latest attempt is indicated with "(latest)" in the dropdown
3. View attempt-specific information such as creation time, duration, and status
4. For failed attempts, click "View Exit Diagnostics" to see detailed error information

### Accessing Task Logs

1. In the Task Role Container List, find the task you want to view logs for
2. Use the log buttons in the "Info & Logs" column:
   - Click "Stdout" to view standard output
   - Click "Stderr" to view standard error
   - Use the dropdown menu for "Stdout+Stderr" or "Show All Logs"
3. The log viewer displays the last 16KB of logs by default
4. Click "View Full Log" to access the complete log file

### Connecting to Running Containers

1. Find a running task in the Task Role Container List
2. Click "SSH Info" to view SSH connection instructions
3. Follow the provided commands to connect to the container
4. The SSH information varies based on your job configuration and OpenPAI deployment mode

### Troubleshooting Failed Tasks

1. Check the task state and exit code in the Task Role Container List
2. For failed tasks, look at the Exit Type and Exit Code columns
3. Click "Show Exit Diagnostics" to view detailed error information
4. Check the task logs for specific error messages
5. For consistent resource conflicts, adjust the resource requirements in your job configuration

## Summary

The Job Detail View is a comprehensive interface for monitoring and managing jobs in OpenPAI. It provides detailed information about job status, tasks, logs, and exit diagnostics, enabling users to effectively track job progress and troubleshoot issues when they occur.

Sources:
- [src/webportal/src/app/job/job-view/fabric/job-detail.jsx:1-552]()
- [src/webportal/src/app/job/job-view/fabric/job-detail/components/summary.jsx:1-494]()
- [src/webportal/src/app/job/job-view/fabric/job-detail/components/task-role-container-list.jsx:1-963]()

---

# Page: Dashboard

# Dashboard

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/webportal/src/app/components/util/job.js](src/webportal/src/app/components/util/job.js)
- [src/webportal/src/app/home/home.jsx](src/webportal/src/app/home/home.jsx)
- [src/webportal/src/app/home/home/abnormal-job-list.jsx](src/webportal/src/app/home/home/abnormal-job-list.jsx)
- [src/webportal/src/app/home/home/c3.scss](src/webportal/src/app/home/home/c3.scss)
- [src/webportal/src/app/home/home/conn.js](src/webportal/src/app/home/home/conn.js)
- [src/webportal/src/app/home/home/gpu-chart.jsx](src/webportal/src/app/home/home/gpu-chart.jsx)
- [src/webportal/src/app/home/home/header.jsx](src/webportal/src/app/home/home/header.jsx)
- [src/webportal/src/app/home/home/job-status.jsx](src/webportal/src/app/home/home/job-status.jsx)
- [src/webportal/src/app/home/home/recent-job-list.jsx](src/webportal/src/app/home/home/recent-job-list.jsx)
- [src/webportal/src/app/home/home/resource-bar.jsx](src/webportal/src/app/home/home/resource-bar.jsx)
- [src/webportal/src/app/home/home/util.js](src/webportal/src/app/home/home/util.js)
- [src/webportal/src/app/home/home/utilization-chart.jsx](src/webportal/src/app/home/home/utilization-chart.jsx)
- [src/webportal/src/app/home/home/virtual-cluster-statistics.jsx](src/webportal/src/app/home/home/virtual-cluster-statistics.jsx)
- [src/webportal/src/app/home/index/bottom.jsx](src/webportal/src/app/home/index/bottom.jsx)
- [src/webportal/src/app/home/index/jumbotron.jsx](src/webportal/src/app/home/index/jumbotron.jsx)
- [src/webportal/src/app/layout/components/navbar.jsx](src/webportal/src/app/layout/components/navbar.jsx)
- [src/webportal/src/assets/img/sign-in-background.svg](src/webportal/src/assets/img/sign-in-background.svg)

</details>



The Dashboard serves as the primary landing page for users after logging into the OpenPAI web portal. It provides an at-a-glance overview of job status, resource allocation, and system health. This page offers different information and capabilities depending on whether the user has admin privileges or not.

For information about accessing specific job details, see [Job Detail View](#5.3). For information about navigating the complete list of jobs, see [Job List View](#5.2).

## Overview

The Dashboard combines multiple visual components to give users immediate insights into:

1. Job status counts across different states
2. Virtual cluster resource allocation and utilization
3. GPU resource availability across nodes
4. Recent jobs submitted by the user
5. Abnormal jobs requiring attention (admin-only view)

These components are arranged differently based on screen size, providing a responsive experience for both desktop and mobile users.

```mermaid
graph TD
    subgraph "OpenPAI Dashboard"
        subgraph "Top Section"
            JobStatus["Job Status Component"]
            VCStats["Virtual Cluster Statistics"]
            GPUChart["GPU Chart"]
        end
        
        subgraph "Bottom Section"
            AbnormalJobs["Abnormal Jobs List (Admin Only)"]
            RecentJobs["Recent Jobs List"]
        end
    end
```

Sources:
- [src/webportal/src/app/home/home.jsx:94-207]()

## Dashboard Components

### Job Status Component

The Job Status component provides a summary of job counts organized by their current state: Waiting, Running, Stopped, Failed, and Succeeded. Each status category includes:

- A status badge indicating the state
- The count of jobs in that state
- A "View all" button that links to the Job List page filtered by that status

For regular users, this component shows only their own jobs. For administrators, it displays counts for all jobs in the system.

```mermaid
graph LR
    JS["Job Status Component"]
    JS --> WJ["Waiting Jobs: count + link"]
    JS --> RJ["Running Jobs: count + link"]
    JS --> SJ["Stopped Jobs: count + link"]
    JS --> FJ["Failed Jobs: count + link"]
    JS --> SUJ["Succeeded Jobs: count + link"]
```

Sources:
- [src/webportal/src/app/home/home/job-status.jsx:79-159]()
- [src/webportal/src/app/home/home.jsx:99-102]()
- [src/webportal/src/app/home/home.jsx:154-157]()

### Virtual Cluster Statistics

This component displays resource allocation and utilization for virtual clusters the user has access to. For each virtual cluster, it shows:

- A utilization chart showing the overall resource usage percentage
- Resource bars for Memory, CPU, and GPU utilization
- Detailed metrics of used resources vs. total resources
- For admin users, information about which user groups have access to each virtual cluster

Regular users only see virtual clusters they have permission to access, while administrators see all virtual clusters in the system.

```mermaid
graph TD
    VC["Virtual Cluster Statistics"]
    VC --> VCList["VirtualClusterDetailsList"]
    VCList --> MemBar["Memory Resource Bar"]
    VCList --> CPUBar["CPU Resource Bar"] 
    VCList --> GPUBar["GPU Resource Bar"]
    VCList --> UtilChart["Utilization Chart"]
    VCList --> GA["Group Access (Admin only)"]
```

Sources:
- [src/webportal/src/app/home/home/virtual-cluster-statistics.jsx:246-295]()
- [src/webportal/src/app/home/home.jsx:104-108]()
- [src/webportal/src/app/home/home.jsx:158-162]()

### GPU Chart

The GPU Chart visualizes GPU availability across all nodes in the cluster. It displays:

- A bar chart showing the distribution of nodes by the number of available GPUs
- Distinction between GPUs in shared virtual clusters and dedicated virtual clusters
- Interactive tooltips providing detailed information when hovering over chart elements

This component helps users understand where GPU resources are available and plan their job submissions accordingly.

```mermaid
graph TD
    GC["GPU Chart"]
    GC --> BC["Bar Chart Component"]
    BC --> SVC["Shared VC Nodes"]
    BC --> DVC["Dedicated VC Nodes"]
    BC --> TT["Interactive Tooltips"]
```

Sources:
- [src/webportal/src/app/home/home/gpu-chart.jsx:45-469]()
- [src/webportal/src/app/home/home.jsx:109-114]()
- [src/webportal/src/app/home/home.jsx:163-168]()

### Recent Job List

The Recent Job List displays the user's most recently submitted jobs (up to 10), sorted by the most recently modified. Each job entry shows:

- Job name (with a link to the Job Detail page)
- Date modified
- Duration
- Virtual cluster
- Current status with a visual status badge

If the user hasn't submitted any jobs, a welcome message is displayed with links to create a job or view tutorials.

```mermaid
graph TD
    RJL["Recent Job List"]
    RJL --> JobTable["Job List Table"]
    JobTable --> cols["Columns: Name, Date Modified, Duration, VC, Status"]
    RJL --> EmptyState["Empty State: Create Job/Tutorial links"]
```

Sources:
- [src/webportal/src/app/home/home/recent-job-list.jsx:89-170]()
- [src/webportal/src/app/home/home.jsx:134-141]()
- [src/webportal/src/app/home/home.jsx:189-193]()

### Abnormal Job List (Admin Only)

Available only to administrators, this component identifies jobs that require attention:

- Long-running jobs (executing for more than 5 days)
- Jobs with low GPU utilization (less than 10%)

Each job entry includes details about the job and a "Stop" button allowing administrators to terminate problematic jobs directly from the dashboard. Long-running jobs show their duration in red, while low GPU usage jobs display their GPU usage percentage in red.

```mermaid
graph TD
    AJL["Abnormal Job List"]
    AJL --> LongRunning["Long Running Jobs: duration > 5 days"]
    AJL --> LowGPU["Low GPU Usage Jobs: < 10%"]
    AJL --> StopAction["Stop Job Action"]
```

Sources:
- [src/webportal/src/app/home/home/abnormal-job-list.jsx:51-218]()
- [src/webportal/src/app/components/util/job.js:111-150]()
- [src/webportal/src/app/home/home.jsx:129-131]()
- [src/webportal/src/app/home/home.jsx:183-186]()

## Data Flow Architecture

The Dashboard operates through a clear data flow pattern, starting from API requests to rendering the final UI components:

```mermaid
sequenceDiagram
    participant User
    participant Home as "Home Component"
    participant API as "conn.js API Module"
    participant REST as "OpenPAI REST API"
    participant Prometheus as "Prometheus API"
    
    User->>Home: Access Dashboard
    activate Home
    Home->>API: Request data
    activate API
    
    par Parallel API Calls
        API->>REST: getJobStatusNumber()
        REST-->>API: Job status counts
        
        API->>REST: listJobs()
        REST-->>API: User jobs
        
        API->>REST: listAllJobs(state: 'RUNNING')
        REST-->>API: Running jobs
        
        API->>REST: getUserInfo()
        REST-->>API: User information
        
        API->>REST: listVirtualClusters()
        REST-->>API: Virtual cluster config
        
        API->>REST: getAvailableGpuPerNode()
        REST-->>API: GPU availability
        
        alt is Admin
            API->>Prometheus: getLowGpuJobInfos()
            Prometheus-->>API: Low GPU usage jobs
        end
    end
    
    API-->>Home: Return all data
    deactivate API
    
    Home->>Home: Process abnormal jobs
    Home-->>User: Render Dashboard components
    deactivate Home
```

The main component makes parallel API calls to fetch all necessary data when the Dashboard loads. After receiving the data, it processes and distributes it to each subcomponent for rendering. For administrators, additional processing is performed to identify abnormal jobs by combining long-running jobs and low GPU usage information.

Sources:
- [src/webportal/src/app/home/home.jsx:60-89]()
- [src/webportal/src/app/home/home/conn.js:38-151]()

## Component Relationship

This diagram shows how the Dashboard components interact with each other and with the backend API services:

```mermaid
graph TD
    Home["Home Component"]
    JobStatus["Job Status Component"]
    VCStats["Virtual Cluster Statistics"]
    GPUChart["GPU Chart"]
    RecentJobs["Recent Job List"]
    AbnormalJobs["Abnormal Job List"]
    APIConn["conn.js API Module"]
    
    Home --> JobStatus
    Home --> VCStats
    Home --> GPUChart
    Home --> RecentJobs
    Home --"Admin only"--> AbnormalJobs
    
    Home --> APIConn
    
    subgraph "Backend Services"
        REST["OpenPAI REST API"]
        Prometheus["Prometheus API"]
    end
    
    APIConn --> REST
    APIConn --> Prometheus
```

Sources:
- [src/webportal/src/app/home/home.jsx:49-209]()

## Responsive Design

The Dashboard implements a responsive design that adapts to different screen sizes:

```mermaid
graph TD
    subgraph "Large Screen Layout"
        TopRow["Three components in a row:<br>JobStatus | VCStats | GPUChart"]
        BottomPanel["Full-width panel with tabs:<br>AbnormalJobs | RecentJobs"]
    end
    
    subgraph "Small Screen Layout"
        Stack["Components stacked vertically:<br>JobStatus<br>VCStats<br>GPUChart<br>Panel with tabs"]
    end
```

For large screens (width > 1400px), the components are arranged in a grid layout with the top row showing Job Status, Virtual Cluster Statistics, and GPU Chart side by side. The bottom panel spans the full width.

For small screens (width ≤ 1400px), the components stack vertically with each taking the full width of the screen.

Sources:
- [src/webportal/src/app/home/home.jsx:97-145]()
- [src/webportal/src/app/home/home.jsx:148-206]()
- [src/webportal/src/app/home/home/util.js:23-24]()

## User Experience Differences

The Dashboard provides different experiences based on the user's role:

| Feature | Regular User | Administrator |
|---------|--------------|---------------|
| Job Status | Shows only user's jobs | Shows all jobs in the system |
| Virtual Clusters | Shows only accessible clusters | Shows all virtual clusters |
| Bottom Panel | Only Recent Jobs tab | Both Recent Jobs and Abnormal Jobs tabs |
| Group Details | Not available | Can view user groups with access to each VC |
| Job Control | Cannot stop jobs from dashboard | Can stop abnormal jobs directly |

Sources:
- [src/webportal/src/app/home/home.jsx:58]()
- [src/webportal/src/app/home/home.jsx:62-66]()
- [src/webportal/src/app/home/home.jsx:117-142]()
- [src/webportal/src/app/home/home.jsx:174-202]()
- [src/webportal/src/app/home/home/virtual-cluster-statistics.jsx:45-255]()

## Implementation Details

### Abnormal Job Detection

The system identifies two types of abnormal jobs:

1. **Long-running jobs**: Jobs running for more than 5 days (defined by `MIN_ABNORMAL_JOB_DURATION_MILLISECOND` constant set to 5 days in milliseconds)
2. **Low GPU utilization jobs**: Jobs using less than 10% of their allocated GPU resources

Abnormal jobs are identified by:
1. Filtering running jobs to find those created more than 5 days ago
2. Querying Prometheus metrics with the expression `avg(avg_over_time(task_gpu_percent[10m]) < 10) by (job_name)` to identify jobs with GPU utilization below 10%
3. Merging these two lists to create a comprehensive view of potentially problematic jobs

Sources:
- [src/webportal/src/app/components/util/job.js:21-117]()
- [src/webportal/src/app/home/home/conn.js:123-144]()
- [src/webportal/src/app/components/util/job.js:119-150]()

### Resource Utilization Visualization

The Dashboard uses several visualization techniques:

1. **Utilization Chart**: A donut chart showing the percentage of resources being used, with color coding based on utilization levels:
   - Green: < 50% utilization
   - Yellow: 50-90% utilization
   - Red: > 90% utilization

2. **Resource Bars**: Horizontal bars showing memory, CPU, and GPU usage with the same color coding scheme

3. **GPU Distribution Chart**: A bar chart showing the distribution of nodes by available GPUs, with different colors for shared and dedicated virtual clusters

Sources:
- [src/webportal/src/app/home/home/utilization-chart.jsx:28-100]()
- [src/webportal/src/app/home/home/resource-bar.jsx:16-79]()
- [src/webportal/src/app/home/home/gpu-chart.jsx:105-240]()

## Tables and Data Structures

### Job List Table Columns

The job list tables (both Recent Jobs and Abnormal Jobs) use the following column structure:

| Column | Description | Special Features |
|--------|-------------|-----------------|
| Name | Job name linked to job details | Clickable link to job detail page |
| GPUs (Abnormal Jobs only) | GPU count and usage percentage | Shows usage in red if below 10% |
| Date Modified | Last modification timestamp | Formatted date and time |
| User (Abnormal Jobs only) | Job owner username | - |
| Duration | Running time of the job | Shows in red if abnormally long |
| Virtual Cluster | The VC where the job is running | - |
| Status | Current job state | Visual status badge |
| Action (Abnormal Jobs only) | Stop button for jobs | Only enabled for stoppable jobs |

Sources:
- [src/webportal/src/app/home/home/recent-job-list.jsx:89-137]()
- [src/webportal/src/app/home/home/abnormal-job-list.jsx:56-176]()

### Virtual Cluster Table Columns

The Virtual Cluster Statistics component displays the following columns:

| Column | Description | Admin-only Features |
|--------|-------------|-------------------|
| Name | Virtual cluster name | Shows "(dedicated)" label if applicable |
| Allocation | Utilization chart showing resource usage | - |
| Detail | Resource bars for Memory, CPU, and GPU | Shows used vs. (total - bad) resources |
| Granted Groups | User groups with access to the VC | Shows group names and detail button |

Sources:
- [src/webportal/src/app/home/home/virtual-cluster-statistics.jsx:46-203]()

## Conclusion

The OpenPAI Dashboard provides a comprehensive overview of the system's current state, resource utilization, and job status. Its responsive design, role-based information display, and interactive elements make it an effective tool for both regular users and administrators to monitor and manage their AI workloads.

For administrators, the Dashboard serves as a central monitoring point to identify problematic jobs and take quick action. For regular users, it offers a quick summary of their jobs and available resources, helping them plan their work efficiently.

---

# Page: Monitoring and Alerting

# Monitoring and Alerting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [contrib/kubespray/quick-start/services-configuration.yaml.template](contrib/kubespray/quick-start/services-configuration.yaml.template)
- [deployment/quick-start/services-configuration.yaml.template](deployment/quick-start/services-configuration.yaml.template)
- [docs/manual/cluster-admin/how-to-use-alert-system.md](docs/manual/cluster-admin/how-to-use-alert-system.md)
- [docs_zh_CN/manual/cluster-admin/how-to-use-alert-system.md](docs_zh_CN/manual/cluster-admin/how-to-use-alert-system.md)
- [examples/cluster-configuration/services-configuration.yaml](examples/cluster-configuration/services-configuration.yaml)
- [src/alert-manager/build/alert-handler.common.dockerfile](src/alert-manager/build/alert-handler.common.dockerfile)
- [src/alert-manager/build/build-pre.sh](src/alert-manager/build/build-pre.sh)
- [src/alert-manager/build/cert-expiration-checker.common.dockerfile](src/alert-manager/build/cert-expiration-checker.common.dockerfile)
- [src/alert-manager/build/cluster-utilization.common.dockerfile](src/alert-manager/build/cluster-utilization.common.dockerfile)
- [src/alert-manager/build/job-status-change-notification.common.dockerfile](src/alert-manager/build/job-status-change-notification.common.dockerfile)
- [src/alert-manager/build/nvidia-gpu-low-perf-fixer.common.dockerfile](src/alert-manager/build/nvidia-gpu-low-perf-fixer.common.dockerfile)
- [src/alert-manager/config/alert-manager.md](src/alert-manager/config/alert-manager.md)
- [src/alert-manager/config/alert-manager.yaml](src/alert-manager/config/alert-manager.yaml)
- [src/alert-manager/config/alert_manager.py](src/alert-manager/config/alert_manager.py)
- [src/alert-manager/deploy/alert-manager-configmap.yaml.template](src/alert-manager/deploy/alert-manager-configmap.yaml.template)
- [src/alert-manager/deploy/alert-manager-deployment.yaml.template](src/alert-manager/deploy/alert-manager-deployment.yaml.template)
- [src/alert-manager/deploy/rbac.yaml](src/alert-manager/deploy/rbac.yaml)
- [src/alert-manager/deploy/service.yaml](src/alert-manager/deploy/service.yaml)
- [src/alert-manager/deploy/start.sh.template](src/alert-manager/deploy/start.sh.template)
- [src/alert-manager/deploy/stop.sh](src/alert-manager/deploy/stop.sh)
- [src/alert-manager/src/alert-handler/controllers/job.js](src/alert-manager/src/alert-handler/controllers/job.js)
- [src/alert-manager/src/alert-handler/controllers/mail.js](src/alert-manager/src/alert-handler/controllers/mail.js)
- [src/alert-manager/src/alert-handler/controllers/node.js](src/alert-manager/src/alert-handler/controllers/node.js)
- [src/alert-manager/src/alert-handler/index.js](src/alert-manager/src/alert-handler/index.js)
- [src/alert-manager/src/alert-handler/package.json](src/alert-manager/src/alert-handler/package.json)
- [src/alert-manager/src/alert-handler/routes/actions.js](src/alert-manager/src/alert-handler/routes/actions.js)
- [src/alert-manager/src/alert-handler/yarn.lock](src/alert-manager/src/alert-handler/yarn.lock)
- [src/alert-manager/src/cert-expiration-checker/__init__.py](src/alert-manager/src/cert-expiration-checker/__init__.py)
- [src/alert-manager/src/cert-expiration-checker/pylintrc](src/alert-manager/src/cert-expiration-checker/pylintrc)
- [src/alert-manager/src/cert-expiration-checker/requirements.txt](src/alert-manager/src/cert-expiration-checker/requirements.txt)
- [src/alert-manager/src/cert-expiration-checker/send_alert.py](src/alert-manager/src/cert-expiration-checker/send_alert.py)
- [src/alert-manager/src/job-status-change-notification/.editorconfig](src/alert-manager/src/job-status-change-notification/.editorconfig)
- [src/alert-manager/src/job-status-change-notification/.eslintrc.js](src/alert-manager/src/job-status-change-notification/.eslintrc.js)
- [src/alert-manager/src/job-status-change-notification/controllers/alert.js](src/alert-manager/src/job-status-change-notification/controllers/alert.js)
- [src/alert-manager/src/job-status-change-notification/controllers/framework.js](src/alert-manager/src/job-status-change-notification/controllers/framework.js)
- [src/prometheus/deploy/alerting/customized.rules.template](src/prometheus/deploy/alerting/customized.rules.template)

</details>



OpenPAI includes a comprehensive monitoring and alerting system that helps cluster administrators track system health, resource utilization, and job performance. This document explains how to use and customize the monitoring and alerting features to detect issues in your cluster and take automated actions in response.

## System Architecture

The monitoring and alerting system in OpenPAI consists of several interconnected components that work together to detect issues and respond to them.

### Component Overview Diagram

```mermaid
flowchart TD
    subgraph "Monitoring"
        Prometheus["Prometheus"]
        NodeExporter["Node Exporter"]
        JobExporter["Job Exporter"]
        GrafanaUI["Grafana UI"]
    end
    
    subgraph "Alerting"
        AlertManager["Alert Manager"]
        AlertHandler["Alert Handler"]
        AlertTemplates["Alert Templates"]
    end
    
    subgraph "Automated Services"
        ClusterUtilization["Cluster Utilization Reporter"]
        CertExpiration["Cert Expiration Checker"]
        JobStatusNotify["Job Status Change Notification"]
    end
    
    subgraph "Management"
        WebPortal["WebPortal"]
        RestServer["REST Server"]
    end
    
    Prometheus --> AlertManager
    NodeExporter --> Prometheus
    JobExporter --> Prometheus
    Prometheus --> GrafanaUI
    
    AlertManager --> AlertHandler
    AlertHandler --> AlertTemplates
    
    AlertManager --> ClusterUtilization
    AlertManager --> CertExpiration
    AlertManager --> JobStatusNotify
    
    AlertHandler --> RestServer
    AlertHandler --> KubernetesAPI["Kubernetes API"]
    
    WebPortal --> Prometheus
    WebPortal --> AlertManager
```

Sources: [src/alert-manager/deploy/alert-manager-deployment.yaml.template](), [src/alert-manager/src/alert-handler/index.js](), [src/alert-manager/config/alert_manager.py]()

### Alert Flow Diagram

```mermaid
sequenceDiagram
    participant Prometheus
    participant AlertManager
    participant AlertHandler
    participant Receivers
    participant Actions
    
    Prometheus->>AlertManager: Send alert (firing)
    Note over AlertManager: Match alert to receiver
    AlertManager->>AlertHandler: Forward to appropriate endpoint
    AlertHandler->>Receivers: Route to receiver
    
    alt email-admin action
        Receivers->>Actions: Send email to admin
    else email-user action
        Receivers->>Actions: Send email to job user
    else stop-jobs action
        Receivers->>Actions: Stop problematic jobs
    else tag-jobs action
        Receivers->>Actions: Tag jobs for review
    else cordon-nodes action
        Receivers->>Actions: Cordon problematic nodes
    else fix-nvidia-gpu-low-perf action
        Receivers->>Actions: Fix GPU performance issues
    end
```

Sources: [src/alert-manager/deploy/alert-manager-configmap.yaml.template](), [src/alert-manager/src/alert-handler/routes/actions.js]()

## Alert Rules

Alert rules define the conditions that trigger alerts. OpenPAI uses Prometheus to evaluate these rules against collected metrics.

### How Alert Rules Work

An alert rule consists of:
- A name that identifies the alert
- An expression (in PromQL) that defines the condition
- A duration for which the condition must be true before firing
- Labels to categorize the alert
- Annotations with human-readable information

Example rule:
```yaml
alert: PAIJobGpuPercentLowerThan0_3For1h
expr: avg(task_gpu_percent{virtual_cluster=~"default"}) by (job_name, username) < 0.3
for: 1h
labels:
  severity: warn
annotations:
  summary: "{{$labels.job_name}} has a job gpu percent lower than 30% for 1 hour"
  description: Monitor job level gpu utilization in certain virtual clusters.
```

This rule fires when a job's average GPU utilization on the "default" virtual cluster is below 30% for more than an hour.

Sources: [docs/manual/cluster-admin/how-to-use-alert-system.md:35-53](), [examples/cluster-configuration/services-configuration.yaml:152-163]()

### Predefined Metrics

OpenPAI provides many built-in metrics that you can use in alert rules:

| Metric Name | Description | Use Case |
|-------------|-------------|----------|
| task_gpu_percent | GPU usage percent for a task | Detect low GPU utilization |
| task_cpu_percent | CPU usage percent for a task | Detect high/low CPU usage |
| node_memory_MemTotal_bytes | Total memory in bytes | Track memory resources |
| node_memory_MemAvailable_bytes | Available memory in bytes | Detect memory shortage |
| gpu_used_by_external_process_count | Count of GPU used by external processes | Detect unauthorized GPU usage |

Sources: [docs/manual/cluster-admin/how-to-use-alert-system.md:25-31]()

### Adding Custom Alert Rules

You can add custom alert rules in the `services-configuration.yml` file under the `prometheus` section:

```yaml
prometheus:
  customized-alerts: |
    groups:
    - name: customized-alerts
      rules:
      - alert: PAIJobGpuPercentLowerThan0_3For1h
        expr: avg(task_gpu_percent{virtual_cluster=~"default"}) by (job_name, username) < 0.3
        for: 1h
        labels:
          severity: warn
        annotations:
          summary: "{{$labels.job_name}} has a job gpu percent lower than 30% for 1 hour"
          description: Monitor job level gpu utilization in certain virtual clusters.
```

After modifying the configuration, you need to update the cluster and restart the Prometheus service:

```bash
./paictl.py service stop -n prometheus
./paictl.py config push -p /cluster-configuration -m service
./paictl.py service start -n prometheus
```

Sources: [docs/manual/cluster-admin/how-to-use-alert-system.md:35-67]()

## Alert Actions and Routes

When alerts are triggered, OpenPAI can take various actions in response. These actions are configured in the Alert Manager and executed by the Alert Handler.

### Available Alert Actions

```mermaid
flowchart TD
    AlertHandler["Alert Handler"]
    
    AlertHandler --> EmailAdmin["email-admin<br>Send email to administrators"]
    AlertHandler --> EmailUser["email-user<br>Send email to job owners"]
    AlertHandler --> StopJobs["stop-jobs<br>Terminate problematic jobs"]
    AlertHandler --> TagJobs["tag-jobs<br>Add tags to jobs"]
    AlertHandler --> CordonNodes["cordon-nodes<br>Mark nodes as unschedulable"]
    AlertHandler --> FixGPUPerf["fix-nvidia-gpu-low-perf<br>Fix GPU performance issues"]
```

Sources: [src/alert-manager/src/alert-handler/routes/actions.js](), [docs/manual/cluster-admin/how-to-use-alert-system.md:110-118]()

### Action Requirements

Each action has specific configuration requirements:

| Action | email-configs | pai-bearer-token | Dependent Labels |
|--------|---------------|------------------|------------------|
| email-admin | Required | Not Required | None |
| email-user | Required | Required | None |
| stop-jobs | Not Required | Required | job_name |
| tag-jobs | Not Required | Required | job_name |
| cordon-nodes | Not Required | Not Required | node_name |
| fix-nvidia-gpu-low-perf | Not Required | Not Required | node_name, minor_number |

Sources: [docs/manual/cluster-admin/how-to-use-alert-system.md:119-140](), [src/alert-manager/config/alert_manager.md:36-42]()

### Alert Routing

Routes determine which alerts trigger which actions. Routing is based on matching alert labels to receivers. A receiver is a group of actions.

Default configuration routes all alerts to the `email-admin` action. Custom routes can be added in `services-configuration.yml`:

```yaml
alert-manager:
  customized-routes:
    routes:
    - receiver: pai-email-admin-user-and-stop-job
      match:
        alertname: PAIJobGpuPercentLowerThan0_3For1h
  customized-receivers:
  - name: "pai-email-admin-user-and-stop-job"
    actions:
      email-admin:
      email-user:
        template: 'kill-low-efficiency-job-alert'
      stop-jobs:
      tag-jobs:
        tags:
        - 'stopped-by-alert-manager'
```

In this example, alerts with name `PAIJobGpuPercentLowerThan0_3For1h` will be routed to the `pai-email-admin-user-and-stop-job` receiver, which will:
1. Send an email to admins
2. Send an email to the job owner using the 'kill-low-efficiency-job-alert' template
3. Stop the job
4. Add a tag 'stopped-by-alert-manager' to the job

Sources: [docs/manual/cluster-admin/how-to-use-alert-system.md:141-196](), [src/alert-manager/deploy/alert-manager-configmap.yaml.template:28-144]()

## Special Features

OpenPAI's monitoring and alerting system includes several specialized features for common administrative tasks.

### Cluster GPU Utilization Report

This feature sends periodic reports about GPU utilization to administrators. The report includes:

- Cluster-level GPU utilization
- User-level GPU utilization
- Job-level GPU utilization

To enable this feature, configure:

```yaml
alert-manager:
  pai-bearer-token: 'your-application-token-for-pai-rest-server'
  cluster-utilization:
    schedule: "0 0 * * *" # daily report at UTC 00:00
```

Sources: [docs/manual/cluster-admin/how-to-use-alert-system.md:255-291](), [contrib/kubespray/quick-start/services-configuration.yaml.template:228-231]()

### Kubernetes Certificate Expiration Checker

This feature checks for expiring Kubernetes certificates and sends alerts to administrators when they are close to expiration. To configure it:

```yaml
alert-manager:
  cert-expiration-checker:
    schedule: '0 0 * * *' # daily check at UTC 00:00
    alert-residual-days: 30 # send alert if expiration is within 30 days
    cert-path: '/etc/kubernetes/ssl' # kubernetes cert path
```

Sources: [docs/manual/cluster-admin/how-to-use-alert-system.md:286-311](), [src/alert-manager/config/alert-manager.yaml:25-28]()

### Job Status Change Notification

This feature sends email notifications to users when their jobs change status. To enable:

```yaml
alert-manager:
  pai-bearer-token: 'your-application-token-for-pai-rest-server'
  job-status-change-notification:
    enable: true
```

Users can customize which status changes trigger notifications in their job configurations.

Sources: [docs/manual/cluster-admin/how-to-use-alert-system.md:313-336](), [src/alert-manager/src/job-status-change-notification/controllers/alert.js]()

## Configuration

The monitoring and alerting system is primarily configured through the `services-configuration.yml` file.

### Core Configuration Parameters

```yaml
alert-manager:
  port: 9093 # AlertManager listening port
  pai-bearer-token: 'your-application-token-for-pai-rest-server'
  alert-handler:
    port: 9095 # AlertHandler listening port
    log-level: "info"
    email-configs:
      admin-receiver: addr-of-admin-receiver@example.com
      smtp-host: smtp.office365.com
      smtp-port: 587
      smtp-from: alert-sender@example.com
      smtp-auth-username: alert-sender@example.com
      smtp-auth-password: password-for-alert-sender
  repeat-interval: '24h' # Minimum interval between repeated alert notifications
```

Sources: [examples/cluster-configuration/services-configuration.yaml:106-145](), [deployment/quick-start/services-configuration.yaml.template:74-113]()

### Email Templates

Alert emails use customizable templates. OpenPAI provides several built-in templates:

- `general-template`: Default general-purpose template
- `cluster-usage`: Template for cluster usage reports
- `kill-low-efficiency-job-alert`: Template for low efficiency job alerts
- `job-status-change`: Template for job status change notifications

You can create custom templates by adding a folder in `pai/src/alert-manager/deploy/alert-templates` with `html.ejs` and `subject.ejs` files.

Sources: [docs/manual/cluster-admin/how-to-use-alert-system.md:186-196](), [src/alert-manager/deploy/alert-manager-deployment.yaml.template:129-138]()

### Applying Configuration Changes

After modifying the alert configuration, update the cluster with:

```bash
./paictl.py service stop -n alert-manager
./paictl.py config push -p /cluster-configuration -m service
./paictl.py service start -n alert-manager
```

Sources: [docs/manual/cluster-admin/how-to-use-alert-system.md:198-206]()

## Extending the Alerting System

### Custom Alert Actions

You can add your own alert actions by:

1. Adding a new API endpoint in the Alert Handler
2. Defining dependencies for your action
3. Updating the renderer to generate the webhook configuration

Custom actions are implemented in the `alert-handler` service, which is a lightweight Express application.

Sources: [docs/manual/cluster-admin/how-to-use-alert-system.md:208-253](), [src/alert-manager/src/alert-handler/controllers/mail.js](), [src/alert-manager/src/alert-handler/controllers/node.js]()

### Alert Handler Implementation

```mermaid
flowchart LR
    AlertManager["Alert Manager<br>webhook_configs"]
    
    subgraph "Alert Handler Routes"
        SendEmailToAdmin["/alert-handler/send-email-to-admin"]
        SendEmailToUser["/alert-handler/send-email-to-user"]
        StopJobs["/alert-handler/stop-jobs"]
        TagJobs["/alert-handler/tag-jobs/:tag"]
        CordonNodes["/alert-handler/cordon-nodes"]
        FixNvidiaGPU["/alert-handler/fix-nvidia-gpu-low-perf"]
    end
    
    subgraph "Controller Functions"
        MailController["mail.js<br>sendEmailToAdmin()<br>sendEmailToUser()"]
        JobController["job.js<br>stopJobs()<br>tagJobs()"]
        NodeController["node.js<br>cordonNodes()<br>fixNvidiaGPULowPerf()"]
    end
    
    AlertManager --> SendEmailToAdmin
    AlertManager --> SendEmailToUser
    AlertManager --> StopJobs
    AlertManager --> TagJobs
    AlertManager --> CordonNodes
    AlertManager --> FixNvidiaGPU
    
    SendEmailToAdmin --> MailController
    SendEmailToUser --> MailController
    StopJobs --> JobController
    TagJobs --> JobController
    CordonNodes --> NodeController
    FixNvidiaGPU --> NodeController
    
    MailController --> SMTP["SMTP Server"]
    JobController --> RestAPI["OpenPAI REST API"]
    NodeController --> K8sAPI["Kubernetes API"]
```

Sources: [src/alert-manager/src/alert-handler/routes/actions.js](), [src/alert-manager/src/alert-handler/controllers/mail.js](), [src/alert-manager/src/alert-handler/controllers/job.js](), [src/alert-manager/src/alert-handler/controllers/node.js]()

---

# Page: Alert Manager

# Alert Manager

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [contrib/kubespray/quick-start/services-configuration.yaml.template](contrib/kubespray/quick-start/services-configuration.yaml.template)
- [deployment/quick-start/services-configuration.yaml.template](deployment/quick-start/services-configuration.yaml.template)
- [docs/manual/cluster-admin/how-to-use-alert-system.md](docs/manual/cluster-admin/how-to-use-alert-system.md)
- [docs_zh_CN/manual/cluster-admin/how-to-use-alert-system.md](docs_zh_CN/manual/cluster-admin/how-to-use-alert-system.md)
- [examples/cluster-configuration/services-configuration.yaml](examples/cluster-configuration/services-configuration.yaml)
- [src/alert-manager/build/alert-handler.common.dockerfile](src/alert-manager/build/alert-handler.common.dockerfile)
- [src/alert-manager/build/build-pre.sh](src/alert-manager/build/build-pre.sh)
- [src/alert-manager/build/cert-expiration-checker.common.dockerfile](src/alert-manager/build/cert-expiration-checker.common.dockerfile)
- [src/alert-manager/build/cluster-utilization.common.dockerfile](src/alert-manager/build/cluster-utilization.common.dockerfile)
- [src/alert-manager/build/job-status-change-notification.common.dockerfile](src/alert-manager/build/job-status-change-notification.common.dockerfile)
- [src/alert-manager/build/nvidia-gpu-low-perf-fixer.common.dockerfile](src/alert-manager/build/nvidia-gpu-low-perf-fixer.common.dockerfile)
- [src/alert-manager/config/alert-manager.md](src/alert-manager/config/alert-manager.md)
- [src/alert-manager/config/alert-manager.yaml](src/alert-manager/config/alert-manager.yaml)
- [src/alert-manager/config/alert_manager.py](src/alert-manager/config/alert_manager.py)
- [src/alert-manager/deploy/alert-manager-configmap.yaml.template](src/alert-manager/deploy/alert-manager-configmap.yaml.template)
- [src/alert-manager/deploy/alert-manager-deployment.yaml.template](src/alert-manager/deploy/alert-manager-deployment.yaml.template)
- [src/alert-manager/deploy/rbac.yaml](src/alert-manager/deploy/rbac.yaml)
- [src/alert-manager/deploy/service.yaml](src/alert-manager/deploy/service.yaml)
- [src/alert-manager/deploy/start.sh.template](src/alert-manager/deploy/start.sh.template)
- [src/alert-manager/deploy/stop.sh](src/alert-manager/deploy/stop.sh)
- [src/alert-manager/src/alert-handler/controllers/job.js](src/alert-manager/src/alert-handler/controllers/job.js)
- [src/alert-manager/src/alert-handler/controllers/mail.js](src/alert-manager/src/alert-handler/controllers/mail.js)
- [src/alert-manager/src/alert-handler/controllers/node.js](src/alert-manager/src/alert-handler/controllers/node.js)
- [src/alert-manager/src/alert-handler/index.js](src/alert-manager/src/alert-handler/index.js)
- [src/alert-manager/src/alert-handler/package.json](src/alert-manager/src/alert-handler/package.json)
- [src/alert-manager/src/alert-handler/routes/actions.js](src/alert-manager/src/alert-handler/routes/actions.js)
- [src/alert-manager/src/alert-handler/yarn.lock](src/alert-manager/src/alert-handler/yarn.lock)
- [src/alert-manager/src/cert-expiration-checker/__init__.py](src/alert-manager/src/cert-expiration-checker/__init__.py)
- [src/alert-manager/src/cert-expiration-checker/pylintrc](src/alert-manager/src/cert-expiration-checker/pylintrc)
- [src/alert-manager/src/cert-expiration-checker/requirements.txt](src/alert-manager/src/cert-expiration-checker/requirements.txt)
- [src/alert-manager/src/cert-expiration-checker/send_alert.py](src/alert-manager/src/cert-expiration-checker/send_alert.py)
- [src/alert-manager/src/job-status-change-notification/.editorconfig](src/alert-manager/src/job-status-change-notification/.editorconfig)
- [src/alert-manager/src/job-status-change-notification/.eslintrc.js](src/alert-manager/src/job-status-change-notification/.eslintrc.js)
- [src/alert-manager/src/job-status-change-notification/controllers/alert.js](src/alert-manager/src/job-status-change-notification/controllers/alert.js)
- [src/alert-manager/src/job-status-change-notification/controllers/framework.js](src/alert-manager/src/job-status-change-notification/controllers/framework.js)
- [src/prometheus/deploy/alerting/customized.rules.template](src/prometheus/deploy/alerting/customized.rules.template)

</details>



The Alert Manager is a key component of the OpenPAI monitoring and alerting system. It is responsible for handling alerts generated by Prometheus, routing them to appropriate receivers, and triggering various actions in response to different alert conditions. This document explains the architecture of the Alert Manager, available alert actions, and how to configure and customize the system.

For general monitoring information, see [Monitoring and Alerting](#6).

## Architecture Overview

The Alert Manager system consists of several interconnected components that work together to detect issues, generate alerts, and take appropriate actions.

```mermaid
graph TD
    subgraph "Monitoring"
        Prometheus["Prometheus"] --> |"fires alerts"| AlertManager["Alert Manager"]
    end
    
    subgraph "Action Handling"
        AlertManager --> |"routes alerts"| AlertHandler["Alert Handler"]
        AlertHandler --> |"implements"| EmailAdmin["Email Admin"]
        AlertHandler --> |"implements"| EmailUser["Email User"]
        AlertHandler --> |"implements"| StopJobs["Stop Jobs"]
        AlertHandler --> |"implements"| TagJobs["Tag Jobs"]
        AlertHandler --> |"implements"| CordonNodes["Cordon Nodes"]
        AlertHandler --> |"implements"| FixGPU["Fix NVIDIA GPU Issues"]
    end
    
    subgraph "Scheduled Tasks"
        AlertManager --> |"schedules"| ClusterUtilization["Cluster Utilization Reporter"]
        AlertManager --> |"schedules"| CertChecker["Cert Expiration Checker"]
    end
    
    subgraph "Integration"
        EmailAdmin --> |"uses"| SMTP["SMTP Server"]
        EmailUser --> |"uses"| SMTP
        StopJobs --> |"calls"| RestAPI["OpenPAI REST API"]
        TagJobs --> |"calls"| RestAPI
        CordonNodes --> |"calls"| K8sAPI["Kubernetes API"]
        FixGPU --> |"calls"| K8sAPI
    end
    
    subgraph "Job Status Monitoring"
        JobStatusNotifier["Job Status Change Notifier"] --> |"sends alerts to"| AlertManager
    end
```

Sources: [src/alert-manager/deploy/alert-manager-deployment.yaml.template](), [src/alert-manager/deploy/alert-manager-configmap.yaml.template](), [src/alert-manager/config/alert_manager.py]()

### Components

1. **Alert Manager**: Core component that receives alerts from Prometheus and routes them to appropriate receivers
2. **Alert Handler**: Service that implements various actions in response to alerts
3. **Cluster Utilization Reporter**: Scheduled job that reports on cluster GPU utilization
4. **Certificate Expiration Checker**: Monitors and alerts on expiring Kubernetes certificates
5. **Job Status Change Notifier**: Sends notifications when job status changes

## Alert Flow

The following diagram illustrates the flow of an alert from detection to action:

```mermaid
sequenceDiagram
    participant P as "Prometheus"
    participant AM as "Alert Manager"
    participant AH as "Alert Handler"
    participant Ext as "External Systems"
    
    P->>AM: Fire alert
    Note over AM: Match alert to route based on labels
    AM->>AM: Route alert to appropriate receiver
    
    Note over AM,AH: For each action in receiver
    
    alt Email Admin Action
        AM->>AH: POST /alert-handler/send-email-to-admin
        AH->>Ext: Send email to admin via SMTP
    else Email User Action
        AM->>AH: POST /alert-handler/send-email-to-user
        AH->>Ext: Get user email from REST API
        AH->>Ext: Send email to user via SMTP
    else Stop Jobs Action
        AM->>AH: POST /alert-handler/stop-jobs
        AH->>Ext: Stop job via REST API
    else Tag Jobs Action
        AM->>AH: POST /alert-handler/tag-jobs/:tag
        AH->>Ext: Tag job via REST API
    else Cordon Nodes Action
        AM->>AH: POST /alert-handler/cordon-nodes
        AH->>Ext: Cordon node via K8s API
    else Fix GPU Action
        AM->>AH: POST /alert-handler/fix-nvidia-gpu-low-perf
        AH->>Ext: Create K8s job to fix GPU
    end
```

Sources: [src/alert-manager/src/alert-handler/routes/actions.js](), [src/alert-manager/deploy/alert-manager-configmap.yaml.template]()

## Alert Actions

The Alert Manager supports the following actions that can be triggered in response to alerts:

| Action | Description | Dependent on Config | Required Label |
|--------|-------------|---------------------|---------------|
| `email-admin` | Send email to administrator | email-configs | - |
| `email-user` | Send email to job owner | email-configs, pai-bearer-token | - |
| `stop-jobs` | Stop OpenPAI jobs | pai-bearer-token | job_name |
| `tag-jobs` | Add tags to OpenPAI jobs | pai-bearer-token | job_name |
| `cordon-nodes` | Mark Kubernetes nodes as unschedulable | - | node_name |
| `fix-nvidia-gpu-low-perf` | Start a container to fix GPU low-performance issues | - | node_name, minor_number |

Sources: [docs/manual/cluster-admin/how-to-use-alert-system.md:117-139](), [src/alert-manager/config/alert_manager.md:33-42]()

## Configuration

The Alert Manager is configured in the `alert-manager` section of the `services-configuration.yaml` file. Below is a sample configuration:

```yaml
alert-manager:
  port: 9093  # Optional, port alert-manager listens on
  pai-bearer-token: 'your-application-token-for-pai-rest-server'
  alert-handler:
    port: 9095  # Optional, port alert-handler listens on
    log-level: "info"  # Optional
    email-configs:  # Required for email actions
      admin-receiver: addr-of-admin-receiver@example.com
      smtp-host: smtp.office365.com
      smtp-port: 587
      smtp-from: alert-sender@example.com
      smtp-auth-username: alert-sender@example.com
      smtp-auth-password: password-for-alert-sender
  cluster-utilization:  # Cluster utilization reporter
    schedule: "0 0 * * *"  # Cron schedule syntax, daily at midnight UTC
  job-status-change-notification:  # Job status change notifier
    enable: true
    log-level: "info"  # Optional
  customized-routes:  # Route configuration
    routes:
    - receiver: pai-email-admin-user-and-stop-job
      match:
        alertname: PAIJobGpuPercentLowerThan0_3For1h
  customized-receivers:  # Action receivers
  - name: "pai-email-admin-user-and-stop-job"
    actions:
      email-admin:
      email-user:
        template: 'kill-low-efficiency-job-alert'
      stop-jobs:
      tag-jobs:
        tags:
        - 'stopped-by-alert-manager'
```

Sources: [examples/cluster-configuration/services-configuration.yaml:105-145](), [contrib/kubespray/quick-start/services-configuration.yaml.template:214-257]()

### Configuration Sections

1. **pai-bearer-token**: Application token for PAI REST server, required for job operations
2. **alert-handler**: Configuration for the alert handler service
   - **email-configs**: Email settings for notifications
3. **cluster-utilization**: Configuration for cluster utilization reports
4. **job-status-change-notification**: Configuration for job status change notifications
5. **customized-routes**: Alert routing rules
6. **customized-receivers**: Receivers with associated actions

## Setting Up Alert Rules

Alert rules are defined in the `prometheus` section of the `services-configuration.yaml` file. Here's an example:

```yaml
prometheus:
  scrape_interval: 30
  customized-alerts: |
    groups:
    - name: customized-alerts
      rules:
      - alert: PAIJobGpuPercentLowerThan0_3For1h
        expr: avg(task_gpu_percent{virtual_cluster=~"default"}) by (job_name, username) < 0.3
        for: 1h
        labels:
          severity: warn
        annotations:
          summary: "{{$labels.job_name}} has a job gpu percent lower than 30% for 1 hour"
          description: Monitor job level gpu utilization in certain virtual clusters.
```

This example defines an alert that triggers when a job's GPU utilization is below 30% for more than an hour.

Sources: [examples/cluster-configuration/services-configuration.yaml:146-163](), [docs/manual/cluster-admin/how-to-use-alert-system.md:44-52]()

## Customizing Alert Routes and Receivers

Routes and receivers determine how alerts are handled. Routes match alerts to receivers based on label values, and receivers define the actions to take.

```mermaid
graph TD
    subgraph "Alert Routing Configuration"
        Alert["Alert"] --> |"Match by labels"| Route["Route"]
        Route --> |"Directs to"| Receiver["Receiver"]
        Receiver --> |"Executes"| Actions["Actions"]
    end
    
    subgraph "Example"
        ExAlert["Alert: PAIJobGpuPercentLowerThan0_3For1h"] --> |"Match: alertname=PAIJobGpuPercentLowerThan0_3For1h"| ExRoute["Route to: pai-email-admin-user-and-stop-job"]
        ExRoute --> ExReceiver["Receiver: pai-email-admin-user-and-stop-job"]
        ExReceiver --> ExActions["Actions: email-admin, email-user, stop-jobs, tag-jobs"]
    end
```

Sources: [docs/manual/cluster-admin/how-to-use-alert-system.md:69-91](), [src/alert-manager/deploy/alert-manager-configmap.yaml.template:28-64]()

### Defining Routes

Routes match alerts to receivers using label matchers:

```yaml
customized-routes:
  routes:
  - receiver: pai-email-admin-user-and-stop-job
    match:
      alertname: PAIJobGpuPercentLowerThan0_3For1h
  - receiver: pai-email-admin-and-fix-nvidia-gpu-low-perf
    match:
      alertname: NodeGpuLowPerfState
```

### Defining Receivers

Receivers specify the actions to take for matched alerts:

```yaml
customized-receivers:
- name: "pai-email-admin-user-and-stop-job"
  actions:
    email-admin:
    email-user:
      template: 'kill-low-efficiency-job-alert'
    stop-jobs:
    tag-jobs:
      tags:
      - 'stopped-by-alert-manager'
- name: "pai-email-admin-and-fix-nvidia-gpu-low-perf"
  actions:
    email-admin:
    fix-nvidia-gpu-low-perf:
```

## Email Templates

The Alert Handler provides several built-in email templates:

1. **general-template**: Default template for generic alerts
2. **kill-low-efficiency-job-alert**: Template for low GPU efficiency alerts
3. **cluster-usage**: Template for cluster usage reports
4. **job-status-change**: Template for job status change notifications

You can also add custom email templates by placing them in the `alert-templates` directory with the following files:
- `html.ejs`: Email body template
- `subject.ejs`: Email subject template

Sources: [docs/manual/cluster-admin/how-to-use-alert-system.md:181-196]()

## Additional Features

### Cluster GPU Utilization Report

The Alert Manager can send regular GPU utilization reports to administrators. To enable this feature, configure:

```yaml
alert-manager:
  pai-bearer-token: 'your-application-token-for-pai-rest-server'
  cluster-utilization:
    schedule: "0 0 * * *"  # daily report at UTC 00:00
```

Sources: [docs/manual/cluster-admin/how-to-use-alert-system.md:255-268]()

### Certificate Expiration Checker

The Alert Manager can check Kubernetes certificate expiration dates and send warnings to administrators:

```yaml
alert-manager:
  cert-expiration-checker:
    schedule: '0 0 * * *'  # daily check at UTC 00:00
    alert-residual-days: 30  # alert if expiring within 30 days
    cert-path: '/etc/kubernetes/ssl'  # path to certificates
```

Sources: [docs/manual/cluster-admin/how-to-use-alert-system.md:268-291]()

### Job Status Change Notification

The Alert Manager can notify users about job status changes:

```yaml
alert-manager:
  pai-bearer-token: 'your-application-token-for-pai-rest-server'
  job-status-change-notification:
    enable: true
```

Sources: [docs/manual/cluster-admin/how-to-use-alert-system.md:313-336]()

## Applying Configuration Changes

After modifying the configuration, you need to apply the changes with the following commands:

```bash
./paictl.py service stop -n alert-manager
./paictl.py config push -p /cluster-configuration -m service
./paictl.py service start -n alert-manager
```

These commands should be executed in the dev-box container.

Sources: [docs/manual/cluster-admin/how-to-use-alert-system.md:199-206]()

## Custom Alert Actions

If the built-in actions don't meet your needs, you can implement custom actions by:

1. Adding new API endpoints in the Alert Handler
2. Defining how to render the action to webhook configurations
3. Implementing the action logic

For details, see the full documentation on how to add custom actions.

Sources: [docs/manual/cluster-admin/how-to-use-alert-system.md:208-253]()

## Troubleshooting

- Ensure the `alert-manager` and `prometheus` services are running correctly
- Check if email settings are properly configured if email notifications aren't working
- Verify that the PAI bearer token is correct for job operations
- Check the Alert Manager logs for error messages

---

# Page: Cluster Utilization Monitoring

# Cluster Utilization Monitoring

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/continuous-integration.yml](.github/workflows/continuous-integration.yml)
- [.github/workflows/lint.yml](.github/workflows/lint.yml)
- [contrib/kubespray/quick-start/services-configuration.yaml.template](contrib/kubespray/quick-start/services-configuration.yaml.template)
- [deployment/quick-start/services-configuration.yaml.template](deployment/quick-start/services-configuration.yaml.template)
- [docs/manual/cluster-admin/how-to-use-alert-system.md](docs/manual/cluster-admin/how-to-use-alert-system.md)
- [docs_zh_CN/manual/cluster-admin/how-to-use-alert-system.md](docs_zh_CN/manual/cluster-admin/how-to-use-alert-system.md)
- [examples/cluster-configuration/services-configuration.yaml](examples/cluster-configuration/services-configuration.yaml)
- [src/alert-manager/build/alert-handler.common.dockerfile](src/alert-manager/build/alert-handler.common.dockerfile)
- [src/alert-manager/build/build-pre.sh](src/alert-manager/build/build-pre.sh)
- [src/alert-manager/build/cert-expiration-checker.common.dockerfile](src/alert-manager/build/cert-expiration-checker.common.dockerfile)
- [src/alert-manager/build/cluster-utilization.common.dockerfile](src/alert-manager/build/cluster-utilization.common.dockerfile)
- [src/alert-manager/build/job-status-change-notification.common.dockerfile](src/alert-manager/build/job-status-change-notification.common.dockerfile)
- [src/alert-manager/build/nvidia-gpu-low-perf-fixer.common.dockerfile](src/alert-manager/build/nvidia-gpu-low-perf-fixer.common.dockerfile)
- [src/alert-manager/config/alert-manager.md](src/alert-manager/config/alert-manager.md)
- [src/alert-manager/config/alert-manager.yaml](src/alert-manager/config/alert-manager.yaml)
- [src/alert-manager/config/alert_manager.py](src/alert-manager/config/alert_manager.py)
- [src/alert-manager/deploy/alert-manager-configmap.yaml.template](src/alert-manager/deploy/alert-manager-configmap.yaml.template)
- [src/alert-manager/deploy/alert-manager-cronjob.yaml.template](src/alert-manager/deploy/alert-manager-cronjob.yaml.template)
- [src/alert-manager/deploy/alert-manager-deployment.yaml.template](src/alert-manager/deploy/alert-manager-deployment.yaml.template)
- [src/alert-manager/deploy/alert-templates/cluster-usage/html.ejs](src/alert-manager/deploy/alert-templates/cluster-usage/html.ejs)
- [src/alert-manager/deploy/service.yaml](src/alert-manager/deploy/service.yaml)
- [src/alert-manager/deploy/start.sh.template](src/alert-manager/deploy/start.sh.template)
- [src/alert-manager/deploy/stop.sh](src/alert-manager/deploy/stop.sh)
- [src/alert-manager/src/alert-handler/controllers/mail.js](src/alert-manager/src/alert-handler/controllers/mail.js)
- [src/alert-manager/src/alert-handler/index.js](src/alert-manager/src/alert-handler/index.js)
- [src/alert-manager/src/cert-expiration-checker/__init__.py](src/alert-manager/src/cert-expiration-checker/__init__.py)
- [src/alert-manager/src/cert-expiration-checker/pylintrc](src/alert-manager/src/cert-expiration-checker/pylintrc)
- [src/alert-manager/src/cert-expiration-checker/requirements.txt](src/alert-manager/src/cert-expiration-checker/requirements.txt)
- [src/alert-manager/src/cert-expiration-checker/send_alert.py](src/alert-manager/src/cert-expiration-checker/send_alert.py)
- [src/alert-manager/src/cluster-utilization/pylintrc](src/alert-manager/src/cluster-utilization/pylintrc)
- [src/alert-manager/src/cluster-utilization/send_alert.py](src/alert-manager/src/cluster-utilization/send_alert.py)
- [src/alert-manager/src/job-status-change-notification/.editorconfig](src/alert-manager/src/job-status-change-notification/.editorconfig)
- [src/alert-manager/src/job-status-change-notification/.eslintrc.js](src/alert-manager/src/job-status-change-notification/.eslintrc.js)
- [src/alert-manager/src/job-status-change-notification/controllers/alert.js](src/alert-manager/src/job-status-change-notification/controllers/alert.js)
- [src/alert-manager/src/job-status-change-notification/controllers/framework.js](src/alert-manager/src/job-status-change-notification/controllers/framework.js)
- [src/utilities/doc_checker.py](src/utilities/doc_checker.py)
- [src/utilities/gen-amtool-config.py](src/utilities/gen-amtool-config.py)
- [src/utilities/release.sh](src/utilities/release.sh)

</details>



Cluster Utilization Monitoring provides visibility into resource usage patterns in an OpenPAI cluster, particularly focusing on GPU utilization metrics. This feature generates periodic reports on GPU utilization at cluster, user, and job levels, helping administrators identify resource usage trends and inefficiencies. The system leverages Prometheus metrics and presents data in an organized, actionable format through email reports.

For information about general alerting configurations and management, see [Alert Manager](#6.1).

## Architecture

The monitoring system operates as part of the alert-manager service in OpenPAI. It runs as a Kubernetes CronJob that collects data from Prometheus and the REST API, then processes and sends this data as alerts.

**Cluster Utilization Monitoring Architecture**
```mermaid
graph TD
    ConfigFile["services-configuration.yaml"] --> AlertManagerConfig["alert_manager.py"]
    AlertManagerConfig --> CronJobDef["alert-manager-cronjob.yaml.template"]
    CronJobDef --> ClusterUtilCronJob["cluster-utilization CronJob"]
    ClusterUtilCronJob --> SendAlertScript["send_alert.py"]
    SendAlertScript -- "collect_metrics()" --> Prometheus["Prometheus API"]
    SendAlertScript -- "get_related_jobs()" --> RESTAPI["REST Server API"]
    SendAlertScript -- "send_alert()" --> AlertManagerAPI["Alert Manager API"]
    AlertManagerAPI --> EmailTemplate["cluster-usage HTML template"]
    EmailTemplate --> AdminEmail["Email to Admin"]
```

Sources:
- [src/alert-manager/deploy/alert-manager-cronjob.yaml.template]()
- [src/alert-manager/src/cluster-utilization/send_alert.py]()
- [src/alert-manager/config/alert_manager.py:85-90]()

## Configuration

To enable cluster utilization monitoring, you need to configure it in the `alert-manager` section of your `services-configuration.yaml` file:

```yaml
alert-manager:
  pai-bearer-token: 'your-application-token-for-pai-rest-server'
  cluster-utilization: # cluster-utilization is a k8s CronJob which reports the GPU utilization of the cluster
    # for schedule syntax, refer to https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/#cron-schedule-syntax
    schedule: "0 0 * * *" # daily report at UTC 00:00
```

The required configuration parameters are:

1. `pai-bearer-token`: An authentication token for the REST server API. You can generate this token from your user profile page in the web portal.
2. `cluster-utilization.schedule`: A cron expression defining when the report should be generated. The example above sets it to run daily at midnight UTC.

Email configuration must also be set up in the alert-manager to deliver the reports. For email configuration details, see [Alert Manager](#6.1).

Sources:
- [contrib/kubespray/quick-start/services-configuration.yaml.template:228-231]()
- [examples/cluster-configuration/services-configuration.yaml:119-121]()
- [docs/manual/cluster-admin/how-to-use-alert-system.md:256-269]()

## Implementation Details

**Cluster Utilization Monitoring Data Flow**
```mermaid
flowchart TD
    Start["main()"] --> CollectMetrics["collect_metrics()"]
    CollectMetrics --> QueryCluster["Query cluster GPU utilization"]
    QueryCluster --> QueryUser["Query user GPU utilization"]
    QueryUser --> QueryJobPercent["Query job GPU percent"]
    QueryJobPercent --> QueryJobHours["Query job GPU hours"] 
    QueryJobHours --> GetUsageInfo["get_usage_info()"]
    GetUsageInfo --> GetJobs["get_related_jobs()"]
    GetJobs --> ProcessUserData["Process user metrics"]
    ProcessUserData --> ProcessJobData["Process job metrics"]
    ProcessJobData --> SendAlert["send_alert()"]
    SendAlert --> FormatAlerts["Format cluster/user/job alerts"]
    FormatAlerts --> PostAlerts["POST to Alert Manager"]
    PostAlerts --> End["End"]
```

Sources:
- [src/alert-manager/src/cluster-utilization/send_alert.py:160-192]()
- [src/alert-manager/src/cluster-utilization/send_alert.py:196-262]()
- [src/alert-manager/src/cluster-utilization/send_alert.py:264-269]()

### Data Collection

The system collects data through the `send_alert.py` script, which queries Prometheus for metrics and the REST API for job information. The main metrics collected are:

| Metric | Prometheus Query | Description |
|--------|-----------------|-------------|
| Cluster GPU Utilization | `avg(avg_over_time(nvidiasmi_utilization_gpu[7d]))` | Average GPU utilization across the cluster over 7 days |
| Job GPU Percent | `avg by (job_name) (avg_over_time(task_gpu_percent[7d]))` | Average GPU utilization for each job over 7 days |
| Job GPU Hours | `sum by (job_name) (count_over_time(task_gpu_percent[7d]))` | Count of GPU hours used by each job over 7 days |
| User GPU Utilization | `(sum by (username) (sum_over_time(task_gpu_percent[7d]))) / (sum by (username) (count_over_time(task_gpu_percent[7d])*100)) * 100` | User's GPU utilization percentage over 7 days |

The script uses `collect_metrics()` to gather these metrics and `get_related_jobs()` to retrieve job details from the REST API. Job information is used to associate metrics with specific jobs and calculate additional statistics like duration and resources occupied (GPU*hours).

Sources:
- [src/alert-manager/src/cluster-utilization/send_alert.py:6-11]()
- [src/alert-manager/src/cluster-utilization/send_alert.py:59-85]()
- [src/alert-manager/src/cluster-utilization/send_alert.py:89-158]()

### Report Generation

After collecting the metrics, the system:

1. Processes the data to calculate utilization statistics
2. Formats the data as alerts with specific labels
3. Sends the alerts to the alert-manager
4. The alert-manager applies the email template and sends the report

The alerts are structured with labels that the email template uses to generate different sections of the report. Each metric type (cluster, user, job) gets its own alert with appropriate labels.

Sources:
- [src/alert-manager/src/cluster-utilization/send_alert.py:196-262]()
- [src/alert-manager/deploy/alert-manager-configmap.yaml.template:74-79]()
- [src/alert-manager/deploy/alert-templates/cluster-usage/html.ejs]()

## Report Content

The utilization report contains three main sections:

### Cluster GPU Utilization

This section displays the overall GPU utilization across the cluster, averaged over the past 7 days.

Example:
```
Cluster GPU utilization: 75.3%
```

This provides a high-level metric to assess overall cluster efficiency.

### User GPU Utilization

This section shows GPU usage broken down by user, sorted by resources occupied:

| User name | Resources occupied (GPU*hour) | GPU utilization |
|-----------|-------------------------------|----------------|
| user1     | 120.45                        | 78.5%          |
| user2     | 85.23                         | 45.2%          |
| ...       | ...                           | ...            |

This helps identify which users are consuming the most resources and how efficiently they're using them.

### Job GPU Utilization

This section presents detailed information for the top 10 jobs by resource consumption:

| Job name | Resources occupied (GPU*hour) | GPU number | GPU utilization | Job duration | Job start time | Job status |
|----------|-------------------------------|------------|----------------|--------------|---------------|------------|
| job1     | 45.67                         | 4          | 85.3%          | 11:23:45     | 2023-05-01    | SUCCEEDED  |
| job2     | 38.92                         | 2          | 42.1%          | 19:28:36     | 2023-05-02    | RUNNING    |
| ...      | ...                           | ...        | ...            | ...          | ...           | ...        |

This detailed breakdown helps identify specific jobs that might be using resources inefficiently or consuming a large portion of the cluster's resources.

Sources:
- [src/alert-manager/deploy/alert-templates/cluster-usage/html.ejs:15-26]()
- [src/alert-manager/deploy/alert-templates/cluster-usage/html.ejs:29-49]()
- [src/alert-manager/deploy/alert-templates/cluster-usage/html.ejs:52-89]()

### Alert Data Structure

The system creates and sends three types of alerts to the alert-manager:

1. **Cluster Usage Alert**: Contains the overall cluster utilization
2. **Job Usage Alerts**: One per job, containing detailed job metrics
3. **User Usage Alerts**: One per user, containing user-level metrics

Each alert contains various labels that the email template uses to generate the report. An example alert structure:

```json
{
  "labels": {
    "alertname": "usage",
    "report_type": "cluster-usage",
    "severity": "info",
    "job_name": "user1~job1",
    "resources_occupied": "45.67",
    "gpu_number": "4",
    "usage": "85.3%",
    "duration": "11:23:45",
    "start_time": "2023-05-01",
    "status": "SUCCEEDED",
    "trigger_time": "2023-05-10"
  },
  "annotations": {
    "summary": "The cluster usage has been reported, please check your email-box for details."
  },
  "generatorURL": "alert/script"
}
```

Sources:
- [src/alert-manager/src/cluster-utilization/send_alert.py:201-256]()

## Troubleshooting

If you encounter issues with the cluster utilization monitoring, check these common areas:

### Configuration Issues

- Verify that `pai-bearer-token` is correctly set and has not expired
- Ensure email configuration in the alert-manager is properly set
- Check that the cron schedule syntax is valid

### Runtime Issues

- Examine the logs of the cluster-utilization pod for errors
- Verify that Prometheus is running and collecting metrics
- Ensure the REST server is accessible from the cluster-utilization pod

### Debugging Commands

```bash
# Check the status of the CronJob
kubectl get cronjob cluster-utilization

# Check the logs of the most recent job run
kubectl logs $(kubectl get pods -l job-name=cluster-utilization-<timestamp> -o name)
```

### Common Problems

- **No jobs shown in report**: Ensure there have been jobs running in the last 7 days
- **Missing metrics**: Verify job-exporter is properly collecting GPU metrics
- **No email received**: Check SMTP configuration and alert-manager routing

Sources:
- [src/alert-manager/src/cluster-utilization/send_alert.py:196-262]()
- [src/alert-manager/deploy/alert-manager-cronjob.yaml.template]()
- [src/alert-manager/config/alert_manager.py:85-90]()
- [docs/manual/cluster-admin/how-to-use-alert-system.md:256-269]()

---

# Page: Developer Guide

# Developer Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/continuous-integration.yml](.github/workflows/continuous-integration.yml)
- [.github/workflows/lint.yml](.github/workflows/lint.yml)
- [Jenkinsfile](Jenkinsfile)
- [deployment/clusterCmd.py](deployment/clusterCmd.py)
- [deployment/k8sPaiLibrary/maintainlib/kubectl_install.py](deployment/k8sPaiLibrary/maintainlib/kubectl_install.py)
- [deployment/machineCmd.py](deployment/machineCmd.py)
- [deployment/utility/__init__.py](deployment/utility/__init__.py)
- [deployment/utility/sftp_copy.py](deployment/utility/sftp_copy.py)
- [deployment/utility/ssh.py](deployment/utility/ssh.py)
- [src/alert-manager/deploy/alert-manager-cronjob.yaml.template](src/alert-manager/deploy/alert-manager-cronjob.yaml.template)
- [src/alert-manager/deploy/alert-templates/cluster-usage/html.ejs](src/alert-manager/deploy/alert-templates/cluster-usage/html.ejs)
- [src/alert-manager/src/cluster-utilization/pylintrc](src/alert-manager/src/cluster-utilization/pylintrc)
- [src/alert-manager/src/cluster-utilization/send_alert.py](src/alert-manager/src/cluster-utilization/send_alert.py)
- [src/utilities/doc_checker.py](src/utilities/doc_checker.py)
- [src/utilities/gen-amtool-config.py](src/utilities/gen-amtool-config.py)
- [src/utilities/release.sh](src/utilities/release.sh)
- [tests/jenkins/config_yarn_cluster.yaml](tests/jenkins/config_yarn_cluster.yaml)
- [tests/jenkins/config_yarn_singlebox.yaml](tests/jenkins/config_yarn_singlebox.yaml)
- [tests/jenkins/stage_build.sh](tests/jenkins/stage_build.sh)
- [tests/jenkins/stage_clean.sh](tests/jenkins/stage_clean.sh)
- [tests/jenkins/stage_deploy.sh](tests/jenkins/stage_deploy.sh)
- [tests/jenkins/stage_prepare.sh](tests/jenkins/stage_prepare.sh)
- [tests/jenkins/stage_test.sh](tests/jenkins/stage_test.sh)
- [tests/jenkins/test_generate_config.sh](tests/jenkins/test_generate_config.sh)
- [tests/jenkins/test_rest_server.sh](tests/jenkins/test_rest_server.sh)

</details>



This guide is intended for developers who want to contribute to the OpenPAI project. It covers development environment setup, project structure, CI/CD pipeline, testing framework, and contribution guidelines. For information about using OpenPAI as an end-user, please refer to the [Overview](#1) page.

## Development Environment Setup

To set up a development environment for OpenPAI, you need the following prerequisites:

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 2.7 or 3.7+ | Different components use different Python versions |
| Node.js | 10.x | Required for REST server and web portal development |
| Go | 1.13+ | Required for watchdog component |
| Docker | Latest | For building and testing service images |
| Kubernetes | 1.14+ | For local deployment testing |

### Setting Up Local Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/microsoft/pai.git
   cd pai
   ```

2. Install dependencies for the component you're working on:
   - For REST server: `cd src/rest-server && yarn install`
   - For web portal: `cd src/webportal && yarn install`
   - For Python components: Install the specific requirements from the component's directory

3. Configure kubectl for accessing your test cluster:
   ```bash
   python paictl.py cluster k8s-set-env
   ```

## Project Structure Overview

The OpenPAI codebase is organized into several key directories:

```
pai/
├── build/           # Build scripts for OpenPAI services
├── contrib/         # Community-contributed components and tools
├── deployment/      # Deployment tools and configuration
├── docs/            # Documentation
├── src/             # Source code for all OpenPAI services
│   ├── alert-manager/        # Alert management service
│   ├── rest-server/          # RESTful API server
│   ├── webportal/            # Web UI
│   ├── watchdog/             # System monitoring component
│   └── other services...
├── tests/           # Test scripts and configurations
└── paictl.py        # PAI control script for cluster management
```

### Component Architecture

Below is a diagram showing the relationship between key components in the OpenPAI development ecosystem:

```mermaid
graph TD
    subgraph "Development Tools"
        paictl["paictl.py Command Line Tool"]
        devbox["Development Box"]
    end

    subgraph "CI/CD Pipeline"
        jenkins["Jenkins Pipeline"]
        githubActions["GitHub Actions"]
        dockerRegistry["Docker Registry"]
    end

    subgraph "Core Components"
        restServer["REST Server (src/rest-server)"]
        webPortal["Web Portal (src/webportal)"]
        frameworkController["Framework Controller"]
        hivedScheduler["Hived Scheduler"]
        alertManager["Alert Manager (src/alert-manager)"]
        watchdog["Watchdog (src/watchdog)"]
    end

    paictl --> devbox
    devbox --> restServer
    devbox --> webPortal
    jenkins --> dockerRegistry
    githubActions --> dockerRegistry
    dockerRegistry --> restServer
    dockerRegistry --> webPortal
    dockerRegistry --> alertManager
    dockerRegistry --> watchdog
```

Sources: [Jenkinsfile](), [.github/workflows/continuous-integration.yml](), [deployment/clusterCmd.py]()

## Development Workflow

### Development Process Overview

The recommended workflow for developing features or fixing bugs in OpenPAI:

```mermaid
sequenceDiagram
    participant Developer
    participant LocalRepo as "Local Repository"
    participant CI as "CI System"
    participant GitHub as "GitHub Repository"
    
    Developer->>LocalRepo: 1. Create branch
    Developer->>LocalRepo: 2. Make changes
    Developer->>LocalRepo: 3. Run local tests
    Developer->>GitHub: 4. Push branch
    GitHub->>CI: 5. Trigger CI checks
    CI->>GitHub: 6. Report check results
    Developer->>GitHub: 7. Create Pull Request
    GitHub->>CI: 8. Run PR validation
    CI->>GitHub: 9. Update PR status
    GitHub->>Developer: 10. Review feedback
    Developer->>LocalRepo: 11. Address feedback
    Developer->>GitHub: 12. Update PR
    GitHub->>Developer: 13. PR approved
    GitHub->>GitHub: 14. Merge PR
```

Sources: [.github/workflows/continuous-integration.yml](), [Jenkinsfile]()

### Making Changes

1. Create a new branch from `master` or the appropriate release branch
2. Make your changes to the relevant components
3. Run local tests to validate your changes
4. Create a pull request to the main repository

### Building Components

To build Docker images for OpenPAI services:

```bash
python build/pai_build.py build -c /path/to/cluster-configuration
```

This script reads the cluster configuration and builds the necessary Docker images for all services.

Sources: [tests/jenkins/stage_build.sh:26-29]()

## CI/CD Pipeline

OpenPAI uses two main CI/CD systems:

1. GitHub Actions - for pull request validation and unit tests
2. Jenkins - for integration testing and deployment validation

### GitHub Actions Workflow

The GitHub Actions workflows are defined in `.github/workflows/` and include:

- Continuous integration (`continuous-integration.yml`)
- Linting checks (`lint.yml`)

These workflows run various tests for different components:

| Component | Test Type | Python/Node Version |
|-----------|-----------|---------------------|
| Deployment scripts | Unit tests | Python 2.7 |
| Exporters | Unit tests | Python 3.7 |
| Watchdog | Build & Test | Go 1.13.8 |
| REST Server | Unit tests | Node 10 |
| Webportal | Build & Test | Node 8 & 10 |

Sources: [.github/workflows/continuous-integration.yml:14-164](), [.github/workflows/lint.yml:13-111]()

### Jenkins Pipeline

The Jenkins pipeline defined in `Jenkinsfile` performs end-to-end testing with the following stages:

```mermaid
flowchart TD
    A["Occupy Bed"] --> B["Prepare Cluster"]
    B --> C["Build Images"]
    C --> D["Deploy PAI"]
    D --> E["Test PAI"]
    E --> F["Pause on Failure"]
    F --> G["Clean up Cluster"]
```

Sources: [Jenkinsfile:52-231]()

#### Pipeline Stages

1. **Prepare Cluster**: Prepares the test environment
   ```bash
   bash -Eeuxo pipefail ${WORKSPACE}/tests/jenkins/stage_prepare.sh
   ```

2. **Build Images**: Builds Docker images for all components
   ```bash
   bash -Eeuxo pipefail ${WORKSPACE}/tests/jenkins/stage_build.sh
   ```

3. **Deploy PAI**: Deploys the OpenPAI system on a Kubernetes cluster
   ```bash
   bash -Eeuxo pipefail ${WORKSPACE}/tests/jenkins/stage_deploy.sh k8s cluster
   ```

4. **Test PAI**: Runs integration tests against the deployed system
   ```bash
   bash -Eeuxo pipefail ${WORKSPACE}/tests/jenkins/stage_test.sh k8s ${K8S_CLUSTER_URI}/rest-server
   ```

5. **Clean up Cluster**: Cleans up after tests
   ```bash
   bash -Eeuxo pipefail ${WORKSPACE}/tests/jenkins/stage_clean.sh k8s cluster
   ```

Sources: [Jenkinsfile:79-190](), [tests/jenkins/stage_prepare.sh](), [tests/jenkins/stage_build.sh](), [tests/jenkins/stage_deploy.sh](), [tests/jenkins/stage_test.sh](), [tests/jenkins/stage_clean.sh]()

## Testing Guide

### Unit Testing

Each component has its own unit tests. Run component-specific tests by navigating to the component directory:

- REST Server: `cd src/rest-server && yarn test`
- Web Portal: `cd src/webportal && yarn test`
- Job Exporter: `cd src/job-exporter/test && python -m unittest discover .`
- Watchdog: `cd src/watchdog/src && go test -cover ./pkg/watchdog`

Sources: [.github/workflows/continuous-integration.yml:111-111](), [.github/workflows/continuous-integration.yml:162-164](), [.github/workflows/continuous-integration.yml:65-65](), [.github/workflows/continuous-integration.yml:89-90]()

### Integration Testing

Integration tests in the `tests/jenkins` directory validate the entire system functionality:

1. REST Server API Test:
   ```bash
   bash ${WORKSPACE}/tests/jenkins/test_rest_server.sh k8s http://your-cluster-url/rest-server
   ```

2. Job Submission Test:
   ```bash
   bash ${WORKSPACE}/tests/jenkins/test_rest_server_js_sdk.sh k8s http://your-cluster-url/rest-server
   ```

Sources: [tests/jenkins/stage_test.sh:20-21](), [tests/jenkins/test_rest_server.sh]()

### Code Coverage

Code coverage tests are implemented for key components:

```bash
cd src/rest-server
yarn run coveralls
```

The results are reported to Coveralls.

Sources: [.github/workflows/continuous-integration.yml:132-135]()

## Documentation Standards

Documentation is critical for the project. All code changes should be accompanied by documentation updates. The project uses a documentation checker to validate markdown files:

```bash
python src/utilities/doc_checker.py [path-to-doc-or-directory]
```

This tool checks for broken links in markdown files.

Sources: [src/utilities/doc_checker.py](), [.github/workflows/lint.yml:31-32]()

## Monitoring and Alerting

### Cluster Utilization Monitoring

OpenPAI includes a cluster utilization monitoring system that collects metrics and sends alerts:

```mermaid
flowchart TD
    A["Prometheus Metrics Collection"] --> B["Alert Manager Configuration"]
    B --> C["Cluster Utilization Reporter"]
    C --> D["Send Utilization Reports"]
    D --> E["Email Notifications"]
```

The cluster utilization monitor runs as a cron job, collecting metrics about GPU utilization, job performance, and user activity. These metrics are used to generate reports and alerts.

Sources: [src/alert-manager/src/cluster-utilization/send_alert.py](), [src/alert-manager/deploy/alert-manager-cronjob.yaml.template](), [src/alert-manager/deploy/alert-templates/cluster-usage/html.ejs]()

## Release Process

The release process for OpenPAI is managed with the `release.sh` script:

```bash
./src/utilities/release.sh
```

This script:
1. Tags the current master branch with a version number
2. Creates a corresponding release branch (e.g., `pai-1.2.y` for version `v1.2.3`)
3. Pushes both the tag and branch to the repository

Sources: [src/utilities/release.sh:21-41]()

## Utility Tools

### SSH and SFTP Utilities

OpenPAI provides utility scripts for interacting with cluster machines:

- SSH utility: `deployment/utility/ssh.py` - For executing commands across multiple machines
- SFTP utility: `deployment/utility/sftp_copy.py` - For copying files to multiple machines

These tools can filter machines based on specified criteria.

Sources: [deployment/utility/ssh.py](), [deployment/utility/sftp_copy.py]()

### Alert Manager Tools

The `gen-amtool-config.py` script generates configuration for the Prometheus AlertManager tool:

```bash
python src/utilities/gen-amtool-config.py -p /path/to/config
```

Sources: [src/utilities/gen-amtool-config.py]()

## Contribution Guidelines

### Pull Request Process

1. Create a branch with an appropriate naming convention:
   - For new features: `feature-name-of-feature`
   - For bug fixes: `fix-issue-description`

2. Ensure your code passes all lint checks and tests:
   - Python code: `pylint` with the appropriate configuration
   - JavaScript code: Use project-specific lint rules with `yarn lint`

3. Write comprehensive tests for your changes

4. Create a pull request with a clear description:
   - What problem does it solve?
   - How does it solve it?
   - Any related issues or documentation changes

5. Update documentation if your changes affect the user experience

### Code Style Guidelines

- Python: Follow PEP 8 with project-specific adjustments in pylintrc files
- JavaScript: Follow the project's ESLint configuration
- Go: Use standard Go formatting (gofmt)

Sources: [src/alert-manager/src/cluster-utilization/pylintrc]()

### Debugging Tips

1. Use the development box for debugging cluster issues:
   ```bash
   python paictl.py cluster k8s-set-env
   ```

2. Check service logs in the Kubernetes cluster:
   ```bash
   kubectl logs -n openpai <pod-name>
   ```

3. For REST server debugging, enable verbose logging by setting environment variables in the deployment configuration.

4. Monitor alerts and metrics through the Alert Manager and Prometheus interfaces.

---

# Page: CI/CD Pipeline

# CI/CD Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/continuous-integration.yml](.github/workflows/continuous-integration.yml)
- [.github/workflows/lint.yml](.github/workflows/lint.yml)
- [Jenkinsfile](Jenkinsfile)
- [deployment/clusterCmd.py](deployment/clusterCmd.py)
- [deployment/k8sPaiLibrary/maintainlib/kubectl_install.py](deployment/k8sPaiLibrary/maintainlib/kubectl_install.py)
- [deployment/machineCmd.py](deployment/machineCmd.py)
- [deployment/utility/__init__.py](deployment/utility/__init__.py)
- [deployment/utility/sftp_copy.py](deployment/utility/sftp_copy.py)
- [deployment/utility/ssh.py](deployment/utility/ssh.py)
- [src/alert-manager/deploy/alert-manager-cronjob.yaml.template](src/alert-manager/deploy/alert-manager-cronjob.yaml.template)
- [src/alert-manager/deploy/alert-templates/cluster-usage/html.ejs](src/alert-manager/deploy/alert-templates/cluster-usage/html.ejs)
- [src/alert-manager/src/cluster-utilization/pylintrc](src/alert-manager/src/cluster-utilization/pylintrc)
- [src/alert-manager/src/cluster-utilization/send_alert.py](src/alert-manager/src/cluster-utilization/send_alert.py)
- [src/utilities/doc_checker.py](src/utilities/doc_checker.py)
- [src/utilities/gen-amtool-config.py](src/utilities/gen-amtool-config.py)
- [src/utilities/release.sh](src/utilities/release.sh)
- [tests/jenkins/config_yarn_cluster.yaml](tests/jenkins/config_yarn_cluster.yaml)
- [tests/jenkins/config_yarn_singlebox.yaml](tests/jenkins/config_yarn_singlebox.yaml)
- [tests/jenkins/stage_build.sh](tests/jenkins/stage_build.sh)
- [tests/jenkins/stage_clean.sh](tests/jenkins/stage_clean.sh)
- [tests/jenkins/stage_deploy.sh](tests/jenkins/stage_deploy.sh)
- [tests/jenkins/stage_prepare.sh](tests/jenkins/stage_prepare.sh)
- [tests/jenkins/stage_test.sh](tests/jenkins/stage_test.sh)
- [tests/jenkins/test_generate_config.sh](tests/jenkins/test_generate_config.sh)
- [tests/jenkins/test_rest_server.sh](tests/jenkins/test_rest_server.sh)

</details>



This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline used in the OpenPAI project. It covers the automated testing, building, and deployment processes that ensure code quality and reliability of the platform.

## Overview

OpenPAI employs a multi-faceted CI/CD approach, utilizing both Jenkins for end-to-end deployment testing and GitHub Actions for component-level testing and validation. This combined approach ensures comprehensive coverage across different aspects of the codebase.

```mermaid
flowchart TD
    PR["Pull Request/Commit"]
    GH["GitHub Actions"]
    JK["Jenkins Pipeline"]
    
    PR --> GH
    PR --> JK
    
    subgraph "Component Testing"
        GH --> UnitTests["Unit Tests"]
        GH --> Linting["Code Linting"]
        GH --> DocTests["Documentation Tests"]
        GH --> CompTests["Component Tests"]
    end
    
    subgraph "E2E Testing"
        JK --> Prepare["Prepare Cluster"]
        Prepare --> Build["Build Images"]
        Build --> Deploy["Deploy PAI"]
        Deploy --> Test["Test PAI"]
        Test --> Clean["Clean up Cluster"]
    end
```

Sources: [Jenkinsfile](), [.github/workflows/continuous-integration.yml](), [.github/workflows/lint.yml]()

## GitHub Actions Workflow

GitHub Actions is used for fast, component-level testing that runs on every pull request and commit to main branches.

### Continuous Integration Workflow

The continuous integration workflow runs multiple jobs in parallel to test different components of the system:

```mermaid
flowchart LR
    Trigger["Code Push/PR"]
    
    subgraph "GitHub Actions CI"
        Trigger --> Deployment["Test Deployment"]
        Trigger --> Exporters["Test Exporters"]
        Trigger --> Watchdog["Test Watchdog"]
        Trigger --> RestServer["Test REST Server"]
        Trigger --> CodeCoverage["Code Coverage"]
        Trigger --> WebPortal["Test Web Portal"]
        Trigger --> Plugins["Test Plugins"]
    end
    
    Deployment --> Results["Pass/Fail Results"]
    Exporters --> Results
    Watchdog --> Results
    RestServer --> Results
    CodeCoverage --> Results
    WebPortal --> Results
    Plugins --> Results
```

Sources: [.github/workflows/continuous-integration.yml:1-165]()

The CI workflow is configured to run on:
- Push to `master` and `pai-**` branches
- Pull requests targeting these branches

Each job runs on specified Python/Node.js versions and operating systems (primarily Ubuntu 18.04 and latest). The key jobs include:

| Job | Runs On | Tests |
|-----|---------|-------|
| deployment | Python 2.7 | Cluster Object Model, template generation |
| exporters | Python 3.7 | Job exporter functionality |
| watchdog | Go 1.13.8 | Watchdog component |
| rest-server | Node.js 10 | REST API functionality |
| code-coverage | Node.js 10 | Coverage reporting for REST server |
| webportal | Node.js 8, 10 | Web portal build and tests |
| webportal-plugins | Node.js 10 | Plugin build |

### Linting Workflow

A separate workflow handles code quality checks:

```mermaid
flowchart TD
    Trigger["Code Push/PR"]
    
    subgraph "GitHub Actions Lint"
        Trigger --> Docs["Lint Documentation"]
        Trigger --> Spelling["Spelling Check"]
        Trigger --> PyLintDeployment["Pylint Deployment"]
        Trigger --> PyLintAlertManager["Pylint Alert Manager"]
        Trigger --> SwaggerValidate["Validate Swagger"]
    end
```

Sources: [.github/workflows/lint.yml:1-112]()

This workflow ensures code quality and documentation standards are maintained across the codebase.

## Jenkins Pipeline

The Jenkins pipeline provides end-to-end testing by deploying a complete OpenPAI cluster in a test environment and running integration tests.

```mermaid
flowchart TD
    subgraph "Jenkins Pipeline Stages"
        OccupyBed["Occupy Bed: Setup Environment"]
        PrepareCluster["Prepare Cluster: Clean Environment"]
        BuildImages["Build Images: Build Docker Images"]
        DeployPAI["Deploy PAI: Setup K8s Cluster"]
        TestPAI["Test PAI: Run Integration Tests"]
        PauseFailure["Pause on Failure: Debug Option"]
        CleanCluster["Clean up Cluster: Teardown"]
    end

    OccupyBed --> PrepareCluster
    PrepareCluster --> BuildImages
    BuildImages --> DeployPAI
    DeployPAI --> TestPAI
    TestPAI --> PauseFailure
    PauseFailure --> CleanCluster
```

Sources: [Jenkinsfile:52-231](), [tests/jenkins/stage_prepare.sh](), [tests/jenkins/stage_build.sh](), [tests/jenkins/stage_deploy.sh](), [tests/jenkins/stage_test.sh](), [tests/jenkins/stage_clean.sh]()

### Jenkins Pipeline Stages in Detail

1. **Occupy Bed**:
   - Sets up environment variables
   - Generates a unique image tag based on branch name, commit hash, and build ID

2. **Prepare Cluster**:
   - Cleans up the testing environment
   - Removes unused packages
   - Stops and removes Docker containers
   - Prepares remote nodes for testing
   - Starts a Docker registry for test images

3. **Build Images**:
   - Generates configuration files for the build
   - Builds OpenPAI Docker images
   - Pushes images to the test registry

4. **Deploy PAI**:
   - Launches a dev-box container for deployment
   - Copies configuration and codebase into the container
   - Bootstraps Kubernetes on test nodes
   - Deploys OpenPAI services

5. **Test PAI**:
   - Verifies REST API accessibility
   - Submits test jobs to the cluster
   - Monitors job execution
   - Validates expected outcomes

6. **Pause on Failure**:
   - If tests fail, provides an option to keep the environment for debugging
   - Waits for manual intervention if requested

7. **Clean up Cluster**:
   - Removes PAI services
   - Cleans up Kubernetes resources
   - Removes dev-box container

Sources: [Jenkinsfile:63-190]()

### Health Check and Error Handling

The Jenkins pipeline includes robust error handling and health checking mechanisms:

```mermaid
flowchart TD
    Start["Start Health Check"]
    Wait["Wait 30s"]
    Request["HTTP Request to REST API"]
    Check["Check Status"]
    Success["Continue Pipeline"]
    Failure["Mark Build as Failed"]
    
    Start --> Wait
    Wait --> Request
    Request --> Check
    Check -->|Status 200| Success
    Check -->|Other Status| Wait
    Check -->|Timeout| Failure
```

Sources: [Jenkinsfile:30-50]()

The pipeline also includes notifications via Office 365 Connector and email alerts on failure:

```javascript
post {
    success {
      office365ConnectorSend(status: "Build success", webhookUrl: "${env.HOOK}")
    }
    failure {
      office365ConnectorSend(status: "Build failure", webhookUrl: "${env.HOOK}")
      step([
        $class: "Mailer",
        notifyEveryUnstableBuild: true,
        recipients: emailextrecipients([
          [$class: "CulpritsRecipientProvider"],
          [$class: "RequesterRecipientProvider"]
        ]),
        to: "paialert@microsoft.com"
      ])
    }
}
```

Sources: [Jenkinsfile:193-226]()

## Testing Strategy

### Component Level Testing

Component tests verify the functionality of individual modules:

1. **Deployment Scripts**:
   - Tests for the cluster object model
   - Template generation tests
   - Forward compatibility tests

2. **Job Exporter**:
   - Python unit tests for monitoring components

3. **Watchdog**:
   - Go tests for the watchdog module
   - Build verification

4. **REST Server**:
   - Unit tests for API endpoints
   - Code coverage reporting

5. **Web Portal**:
   - Build verification
   - Component tests

Sources: [.github/workflows/continuous-integration.yml:31-41](), [.github/workflows/continuous-integration.yml:62-66](), [.github/workflows/continuous-integration.yml:88-91](), [.github/workflows/continuous-integration.yml:108-111](), [.github/workflows/continuous-integration.yml:163-164]()

### Integration Testing

Integration tests verify the end-to-end functionality of the system:

```mermaid
sequenceDiagram
    participant Jenkins
    participant TestScript
    participant RestServer
    participant K8s
    
    Jenkins->>TestScript: Execute test_rest_server.sh
    TestScript->>RestServer: Request authentication token
    RestServer-->>TestScript: Return token
    TestScript->>RestServer: Submit test job (Keras MNIST)
    RestServer->>K8s: Create job
    
    loop Check Job Status
        TestScript->>RestServer: Query job status
        RestServer->>K8s: Get job status
        K8s-->>RestServer: Return status
        RestServer-->>TestScript: Return status
        Note over TestScript: Wait if not complete
    end
    
    TestScript-->>Jenkins: Report success/failure
```

Sources: [tests/jenkins/test_rest_server.sh:20-56](), [tests/jenkins/stage_test.sh:20-21]()

The integration test:
1. Obtains an authentication token from the REST API
2. Submits a test job (Keras TensorFlow MNIST example)
3. Monitors the job until completion
4. Verifies successful execution

## Cluster Utilization Monitoring

As part of the CI/CD process, OpenPAI includes monitoring for cluster utilization, which helps assess the performance and resource usage of the platform.

```mermaid
flowchart LR
    CronJob["Cluster Utilization CronJob"]
    Metrics["Collect Metrics"]
    Alert["Send Alerts"]
    Email["Email Reports"]
    
    CronJob --> Metrics
    Metrics --> Alert
    Alert --> Email
    
    subgraph "Metrics Collected"
        ClusterUsage["Cluster GPU Usage"]
        JobUsage["Job GPU Usage"]
        UserUsage["User GPU Usage"]
    end
    
    Metrics --> ClusterUsage
    Metrics --> JobUsage
    Metrics --> UserUsage
```

Sources: [src/alert-manager/src/cluster-utilization/send_alert.py:1-278](), [src/alert-manager/deploy/alert-manager-cronjob.yaml.template:1-49]()

The cluster utilization monitoring:
1. Runs as a scheduled Kubernetes CronJob
2. Collects metrics on cluster, job, and user GPU utilization
3. Sends alerts with detailed reports
4. Formats data in HTML for email reporting

## Release Process

The release process involves tagging and branching to create stable release versions:

```mermaid
flowchart TD
    MasterBranch["Master Branch"]
    Tag["Create Version Tag"]
    ReleaseBranch["Create Release Branch"]
    
    MasterBranch --> Tag
    Tag --> ReleaseBranch
    
    subgraph "Release Steps"
        PullMaster["Pull Latest Master"]
        CreateTag["Create and Push Tag"]
        CreateBranch["Create and Push Branch"]
    end
    
    PullMaster --> CreateTag
    CreateTag --> CreateBranch
```

Sources: [src/utilities/release.sh:1-42]()

The release script:
1. Pulls the latest master branch
2. Creates and pushes a version tag (e.g., v1.2.3)
3. Creates and pushes a corresponding branch (e.g., pai-1.2.y)

## Conclusion

The CI/CD pipeline in OpenPAI provides comprehensive testing and deployment automation, ensuring code quality and system reliability. By combining GitHub Actions for component testing and Jenkins for end-to-end validation, the pipeline offers both speed and thoroughness.

The pipeline supports:
- Fast feedback on code changes
- Comprehensive testing across multiple components
- Automated deployment for integration testing
- Performance and utilization monitoring
- Structured release management

This multi-layered approach helps maintain the stability and reliability of the OpenPAI platform while allowing for continuous improvement and feature development.

---

# Page: Job Protocol Schema

# Job Protocol Schema

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/database-controller/src/write-merger/app.js](src/database-controller/src/write-merger/app.js)
- [src/rest-server/config/rest-server.md](src/rest-server/config/rest-server.md)
- [src/rest-server/config/rest-server.yaml](src/rest-server/config/rest-server.yaml)
- [src/rest-server/config/rest_server.py](src/rest-server/config/rest_server.py)
- [src/rest-server/deploy/rest-server.yaml.template](src/rest-server/deploy/rest-server.yaml.template)
- [src/rest-server/docs/swagger.yaml](src/rest-server/docs/swagger.yaml)
- [src/rest-server/package.json](src/rest-server/package.json)
- [src/rest-server/src/config/express.js](src/rest-server/src/config/express.js)
- [src/rest-server/src/config/launcher.js](src/rest-server/src/config/launcher.js)
- [src/rest-server/src/config/schedule-port.js](src/rest-server/src/config/schedule-port.js)
- [src/rest-server/src/controllers/internal/tail-log.js](src/rest-server/src/controllers/internal/tail-log.js)
- [src/rest-server/src/controllers/v2/cluster.js](src/rest-server/src/controllers/v2/cluster.js)
- [src/rest-server/src/controllers/v2/job.js](src/rest-server/src/controllers/v2/job.js)
- [src/rest-server/src/controllers/v2/task.js](src/rest-server/src/controllers/v2/task.js)
- [src/rest-server/src/models/v2/job/index.js](src/rest-server/src/models/v2/job/index.js)
- [src/rest-server/src/models/v2/job/k8s.js](src/rest-server/src/models/v2/job/k8s.js)
- [src/rest-server/src/models/v2/job/log.js](src/rest-server/src/models/v2/job/log.js)
- [src/rest-server/src/models/v2/task.js](src/rest-server/src/models/v2/task.js)
- [src/rest-server/src/models/v2/utils/frameworkConverter.js](src/rest-server/src/models/v2/utils/frameworkConverter.js)
- [src/rest-server/src/models/v2/utils/name.js](src/rest-server/src/models/v2/utils/name.js)
- [src/rest-server/src/routes/internal/index.js](src/rest-server/src/routes/internal/index.js)
- [src/rest-server/src/routes/internal/tail-log.js](src/rest-server/src/routes/internal/tail-log.js)
- [src/rest-server/src/routes/v2/cluster.js](src/rest-server/src/routes/v2/cluster.js)
- [src/rest-server/src/routes/v2/job.js](src/rest-server/src/routes/v2/job.js)
- [src/rest-server/src/utils/error.d.ts](src/rest-server/src/utils/error.d.ts)
- [src/rest-server/test/setup.js](src/rest-server/test/setup.js)
- [src/rest-server/yarn.lock](src/rest-server/yarn.lock)
- [src/webportal/src/app/job-submission/components/basic-section.jsx](src/webportal/src/app/job-submission/components/basic-section.jsx)
- [src/webportal/src/app/job-submission/components/context.jsx](src/webportal/src/app/job-submission/components/context.jsx)
- [src/webportal/src/app/job-submission/components/controls/tooltip-icon.jsx](src/webportal/src/app/job-submission/components/controls/tooltip-icon.jsx)
- [src/webportal/src/app/job-submission/components/customized-components.jsx](src/webportal/src/app/job-submission/components/customized-components.jsx)
- [src/webportal/src/app/job-submission/components/docker-section.jsx](src/webportal/src/app/job-submission/components/docker-section.jsx)
- [src/webportal/src/app/job-submission/components/form-text-field.jsx](src/webportal/src/app/job-submission/components/form-text-field.jsx)
- [src/webportal/src/app/job-submission/components/job-information.jsx](src/webportal/src/app/job-submission/components/job-information.jsx)
- [src/webportal/src/app/job-submission/components/sidebar/sidebar-card.jsx](src/webportal/src/app/job-submission/components/sidebar/sidebar-card.jsx)
- [src/webportal/src/app/job-submission/components/submission-section.jsx](src/webportal/src/app/job-submission/components/submission-section.jsx)
- [src/webportal/src/app/job-submission/components/tab-form-content.jsx](src/webportal/src/app/job-submission/components/tab-form-content.jsx)
- [src/webportal/src/app/job-submission/components/task-role/completion-policy.jsx](src/webportal/src/app/job-submission/components/task-role/completion-policy.jsx)
- [src/webportal/src/app/job-submission/job-submission-page.jsx](src/webportal/src/app/job-submission/job-submission-page.jsx)
- [src/webportal/src/app/job-submission/job-submission.jsx](src/webportal/src/app/job-submission/job-submission.jsx)
- [src/webportal/src/app/job-submission/models/completion.js](src/webportal/src/app/job-submission/models/completion.js)
- [src/webportal/src/app/job-submission/models/docker-info.js](src/webportal/src/app/job-submission/models/docker-info.js)
- [src/webportal/src/app/job-submission/models/job-protocol.js](src/webportal/src/app/job-submission/models/job-protocol.js)
- [src/webportal/src/app/job-submission/models/job-task-role.js](src/webportal/src/app/job-submission/models/job-task-role.js)
- [src/webportal/src/app/job-submission/models/protocol-schema.js](src/webportal/src/app/job-submission/models/protocol-schema.js)
- [src/webportal/src/app/job-submission/utils/conn.js](src/webportal/src/app/job-submission/utils/conn.js)
- [src/webportal/src/app/job-submission/utils/constants.js](src/webportal/src/app/job-submission/utils/constants.js)
- [src/webportal/src/app/job-submission/utils/task-roles-manager.js](src/webportal/src/app/job-submission/utils/task-roles-manager.js)
- [src/webportal/src/app/job-submission/utils/utils.js](src/webportal/src/app/job-submission/utils/utils.js)
- [tests/jenkins/test_rest_server_js_sdk.sh](tests/jenkins/test_rest_server_js_sdk.sh)

</details>



The Job Protocol Schema defines the structure and format of job submissions in OpenPAI. It serves as a contract between clients (Web Portal, VSCode Extension, API clients) and the REST server, ensuring that job submissions contain all necessary information in the correct format. This document explains the schema's structure, components, validation process, and how it integrates with other parts of the OpenPAI system.

For information about job lifecycle, see [Job Lifecycle](#3.2).

## Schema Overview

The Job Protocol Schema defines the expected structure of a job submission in YAML or JSON format. It is used both for validating incoming job requests and for generating the appropriate Kubernetes resources.

```mermaid
graph TD
    User["User"] -->|"submits job via"| Client["Web Portal/VSCode/API"]
    Client -->|"validates against"| Schema["Job Protocol Schema"]
    Client -->|"sends valid job to"| REST["REST Server"]
    REST -->|"validates again using"| Schema
    REST -->|"converts to"| K8s["Kubernetes Resources"]
    K8s -->|"creates"| Pods["Job Pods"]
    
    subgraph "Job Protocol Components"
        Basic["Basic Information"]
        TaskRoles["Task Roles"]
        Prerequisites["Prerequisites"]
        Parameters["Parameters"]
        Secrets["Secrets"]
        Extras["Extras"]
    end
    
    Schema --- Basic
    Schema --- TaskRoles
    Schema --- Prerequisites
    Schema --- Parameters
    Schema --- Secrets
    Schema --- Extras
```

Sources: 
- [src/webportal/src/app/job-submission/models/protocol-schema.js:1-190](src/webportal/src/app/job-submission/models/protocol-schema.js:1-190)
- [src/webportal/src/app/job-submission/models/job-protocol.js:1-110](src/webportal/src/app/job-submission/models/job-protocol.js:1-110)

## Core Schema Components

The job protocol schema consists of several key components, as defined in `jobProtocolSchema`:

### 1. Basic Information

These fields provide general information about the job:

- `protocolVersion`: Version of the protocol (currently 2)
- `name`: Name of the job
- `type`: Always "job" for job submissions
- `version`: Version of the job
- `contributor`: Job creator
- `description`: Job description

### 2. Task Roles

The task roles define the different components of the job, each potentially with different resource requirements and commands. Each task role can have multiple instances.

```mermaid
graph TD
    TaskRole["Task Role"] --> Instances["instances: Number of replicas"]
    TaskRole --> Completion["completion: Success/failure policies"]
    TaskRole --> Resources["resourcePerInstance: CPU/Memory/GPU requirements"]
    TaskRole --> DockerImage["dockerImage: Container image"]
    TaskRole --> Commands["commands: Commands to execute"]
    TaskRole --> Retry["taskRetryCount: Number of retries"]
    TaskRole --> ExtraOptions["extraContainerOptions: Additional container settings"]
```

Sources:
- [src/webportal/src/app/job-submission/models/protocol-schema.js:29-67](src/webportal/src/app/job-submission/models/protocol-schema.js:29-67)
- [src/webportal/src/app/job-submission/models/job-task-role.js:38-143](src/webportal/src/app/job-submission/models/job-task-role.js:38-143)

### 3. Prerequisites

Prerequisites define the external resources needed by the job, such as:

- Docker images
- Data
- Scripts
- Output locations

Each prerequisite has:
- `name`: Unique identifier
- `type`: One of "data", "script", "dockerimage", or "output"
- `uri`: Location of the resource
- Optional authentication information

```mermaid
graph TD
    Prerequisite["Prerequisite"] --> Name["name: Unique identifier"]
    Prerequisite --> Type["type: dockerimage/data/script/output"]
    Prerequisite --> Uri["uri: Resource location"]
    Prerequisite --> Auth["auth: Optional authentication details"]
    
    Type -->|"if dockerimage"| Docker["Docker image specification"]
    Type -->|"if data"| Data["Input data location"]
    Type -->|"if script"| Script["Script to execute"]
    Type -->|"if output"| Output["Output location"]
```

Sources:
- [src/webportal/src/app/job-submission/models/protocol-schema.js:74-98](src/webportal/src/app/job-submission/models/protocol-schema.js:74-98)

### 4. Parameters and Secrets

Parameters allow for configurable values that can be referenced in commands:
- `parameters`: Key-value pairs for job configuration
- `secrets`: Sensitive key-value pairs that are handled securely

### 5. Deployments

Deployments define how task roles are deployed, including:
- Pre-commands: Commands to run before the main task
- Post-commands: Commands to run after the main task

Sources:
- [src/webportal/src/app/job-submission/models/protocol-schema.js:101-118](src/webportal/src/app/job-submission/models/protocol-schema.js:101-118)

### 6. Extras

The extras section contains platform-specific extensions, primarily runtime plugins:

```mermaid
graph TD
    Extras["extras"] --> RuntimePlugins["com.microsoft.pai.runtimeplugin[]"]
    RuntimePlugins --> Plugin["plugin: Plugin name"]
    RuntimePlugins --> Parameters["parameters: Plugin-specific configuration"]
    RuntimePlugins --> FailurePolicy["failurePolicy: fail/ignore"]
    
    Plugin -->|"if tensorboard"| Tensorboard["Tensorboard configuration"]
    Plugin -->|"if ssh"| SSH["SSH configuration"]
    Plugin -->|"if storage"| Storage["Storage configuration"]
```

Sources:
- [src/webportal/src/app/job-submission/models/protocol-schema.js:120-156](src/webportal/src/app/job-submission/models/protocol-schema.js:120-156)
- [src/webportal/src/app/job-submission/utils/constants.js:171-173](src/webportal/src/app/job-submission/utils/constants.js:171-173)

## Complete Schema Structure

The complete job protocol schema structure is defined as follows:

```mermaid
classDiagram
    class JobProtocol {
        protocolVersion: string|number
        name: string
        type: string
        version: string|number
        contributor: string
        description: string
        prerequisites: Prerequisite[]
        parameters: object
        secrets: object
        jobRetryCount: number
        taskRoles: object
        deployments: Deployment[]
        defaults: object
        extras: object
    }
    
    class TaskRole {
        instances: number
        completion: Completion
        taskRetryCount: number
        dockerImage: string
        data: string
        output: string
        script: string
        prerequisites: string[]
        extraContainerOptions: object
        resourcePerInstance: ResourceRequirements
        commands: string[]
    }
    
    class ResourceRequirements {
        cpu: number
        memoryMB: number
        gpu: number
        ports: object
    }
    
    class Completion {
        minFailedInstances: number
        minSucceededInstances: number
    }
    
    class Prerequisite {
        name: string
        type: string
        plugin: string
        require: string[]
        contributor: string
        description: string
        auth: Auth
        uri: string|string[]
        version: string|number
    }
    
    class Auth {
        username: string
        password: string
        registryuri: string
    }
    
    class Deployment {
        name: string
        taskRoles: object
    }
    
    class RuntimePlugin {
        plugin: string
        parameters: object
        failurePolicy: string
        hook: string
    }
    
    JobProtocol "1" --* "many" TaskRole: contains
    JobProtocol "1" --* "many" Prerequisite: contains
    JobProtocol "1" --* "many" Deployment: contains
    TaskRole "1" --* "1" ResourceRequirements: contains
    TaskRole "1" --* "1" Completion: contains
    Prerequisite "1" --* "1" Auth: may contain
    JobProtocol "1" --* "many" RuntimePlugin: in extras
```

Sources:
- [src/webportal/src/app/job-submission/models/protocol-schema.js:160-190](src/webportal/src/app/job-submission/models/protocol-schema.js:160-190)

## Schema Validation Process

The job protocol validation process ensures that job submissions conform to the expected schema:

```mermaid
sequenceDiagram
    participant User
    participant WebPortal as "Web Portal"
    participant JobProtocol as "JobProtocol Class"
    participant JoiValidator as "Joi Schema Validator"
    participant RESTServer as "REST Server"
    participant K8s as "Kubernetes API"
    
    User->>WebPortal: Submit job
    WebPortal->>JobProtocol: Create job protocol
    JobProtocol->>JoiValidator: Validate using schema
    
    alt Invalid Schema
        JoiValidator-->>WebPortal: Return validation errors
        WebPortal-->>User: Display validation errors
    else Valid Schema
        JoiValidator-->>JobProtocol: Validation success
        JobProtocol-->>WebPortal: Return validated protocol
        WebPortal->>RESTServer: POST /api/v2/jobs
        RESTServer->>RESTServer: Validate protocol again
        RESTServer->>RESTServer: Convert to framework description
        RESTServer->>K8s: Create Kubernetes resources
        K8s-->>RESTServer: Resources created
        RESTServer-->>WebPortal: Job submitted successfully
        WebPortal-->>User: Show success message
    end
```

Sources:
- [src/webportal/src/app/job-submission/models/job-protocol.js:65-125](src/webportal/src/app/job-submission/models/job-protocol.js:65-125)
- [src/rest-server/src/routes/v2/job.js:32-38](src/rest-server/src/routes/v2/job.js:32-38)
- [src/rest-server/src/controllers/v2/job.js:177-206](src/rest-server/src/controllers/v2/job.js:177-206)

## Conversion to Kubernetes Resources

The REST server converts the validated job protocol into Kubernetes resources:

```mermaid
graph TD
    Protocol["Job Protocol"] -->|"generateFrameworkDescription()"| Framework["Kubernetes Framework Resource"]
    Framework --> TaskRoleResources["Task Role Resources"]
    Framework --> Secrets["Secret Resources"]
    Framework --> PriorityClass["Priority Class Resource"]
    
    TaskRoleResources --> Pod["Pod Template"]
    Pod --> Containers["Main Container + Init Container"]
    Pod --> Volumes["Volumes (incl. Storage, Secrets)"]
    Pod --> Affinity["Node Affinity"]
    Pod --> Resources["Resource Requirements"]
```

During this conversion:
1. The job protocol is validated
2. User access to the requested virtual cluster is checked
3. Storage configurations are validated
4. Docker image authentication is handled
5. A Kubernetes Framework resource is generated with all necessary pod definitions
6. Additional resources like secrets and priority classes are created as needed

Sources:
- [src/rest-server/src/models/v2/job/k8s.js:679-805](src/rest-server/src/models/v2/job/k8s.js:679-805)
- [src/rest-server/src/models/v2/job/k8s.js:351-677](src/rest-server/src/models/v2/job/k8s.js:351-677)

## Job Submission Flow

The complete job submission flow from the user interface to Kubernetes execution:

```mermaid
sequenceDiagram
    participant User
    participant WebPortal as "Web Portal"
    participant RESTServer as "REST Server"
    participant K8s as "Kubernetes API"
    participant FrameworkController as "Framework Controller"
    participant HivedScheduler as "Hived Scheduler"
    participant Pods as "Job Pods"
    
    User->>WebPortal: Fill job submission form
    WebPortal->>WebPortal: Create JobProtocol object
    WebPortal->>WebPortal: Validate job protocol
    WebPortal->>RESTServer: POST /api/v2/jobs
    
    RESTServer->>RESTServer: Validate protocol
    RESTServer->>RESTServer: Check user permissions for VC
    RESTServer->>RESTServer: Validate storage configs
    
    RESTServer->>RESTServer: generateFrameworkDescription()
    RESTServer->>K8s: Create Framework resource
    RESTServer->>K8s: Create Docker secrets if needed
    RESTServer->>K8s: Create config secrets if needed
    RESTServer->>K8s: Create priority class if needed
    
    K8s->>FrameworkController: Framework created event
    FrameworkController->>HivedScheduler: Schedule Framework
    HivedScheduler->>FrameworkController: Resource allocation
    FrameworkController->>K8s: Create Pods
    
    K8s->>Pods: Create and start containers
    Pods->>Pods: Run init container
    Pods->>Pods: Run job container
    
    Pods-->>FrameworkController: Completion status
    FrameworkController-->>K8s: Update Framework status
    K8s-->>RESTServer: Framework status updated
    RESTServer-->>WebPortal: Job status updated
    WebPortal-->>User: Show job status
```

Sources:
- [src/webportal/src/app/job-submission/components/submission-section.jsx:95-140](src/webportal/src/app/job-submission/components/submission-section.jsx:95-140)
- [src/webportal/src/app/job-submission/utils/conn.js:44-46](src/webportal/src/app/job-submission/utils/conn.js:44-46)
- [src/rest-server/src/controllers/v2/job.js:185-206](src/rest-server/src/controllers/v2/job.js:185-206)
- [src/rest-server/src/models/v2/job/k8s.js:1027-1149](src/rest-server/src/models/v2/job/k8s.js:1027-1149)

## Schema Handling in REST Server

The REST server processes job submissions through several key steps:

1. **Route handling**: The `/api/v2/jobs` route accepts POST requests for job submissions
2. **Middleware processing**: The `protocol.submit` middleware validates the job protocol
3. **Controller action**: The `controller.update` function processes the validated job
4. **Job model conversion**: The `job.put` function converts the protocol to Kubernetes resources

The REST server also has multiple endpoints for managing jobs:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v2/jobs` | GET | List jobs with filtering options |
| `/api/v2/jobs` | POST | Submit a new job |
| `/api/v2/jobs/:frameworkName` | GET | Get details of a specific job |
| `/api/v2/jobs/:frameworkName/executionType` | PUT | Start or stop a job |
| `/api/v2/jobs/:frameworkName/config` | GET | Get the job configuration |
| `/api/v2/jobs/:frameworkName/ssh` | GET | Get SSH information for a job |
| `/api/v2/jobs/:frameworkName/tag` | PUT/DELETE | Add or remove a tag from a job |

Sources:
- [src/rest-server/src/routes/v2/job.js:32-105](src/rest-server/src/routes/v2/job.js:32-105)
- [src/rest-server/src/controllers/v2/job.js:177-206](src/rest-server/src/controllers/v2/job.js:177-206)

## Environment Variables in the Job Protocol

The job protocol supports referencing environment variables that are available to the job at runtime. These variables provide information about the job, task roles, and resources:

| Environment Variable | Description |
|---------------------|-------------|
| `PAI_JOB_NAME` | Job name as specified in the config |
| `PAI_USER_NAME` | User who submitted the job |
| `PAI_DEFAULT_FS_URI` | Default file system URI in PAI |
| `PAI_TASK_ROLE_COUNT` | Total number of task roles |
| `PAI_TASK_ROLE_LIST` | Comma-separated list of all task role names |
| `PAI_TASK_ROLE_TASK_COUNT_$taskRole` | Number of tasks in a specific task role |
| `PAI_HOST_IP_$taskRole_$taskIndex` | Host IP for a specific task |
| `PAI_PORT_LIST_$taskRole_$taskIndex_$portType` | Port list for a specific task |
| `PAI_RESOURCE_$taskRole` | Resource requirements in "gpuNumber,cpuNumber,memMB,shmMB" format |
| `PAI_CURRENT_TASK_ROLE_NAME` | Name of the current task role |
| `PAI_CURRENT_TASK_ROLE_CURRENT_TASK_INDEX` | Index of the current task in the task role |

Sources:
- [src/webportal/src/app/job-submission/utils/constants.js:31-85](src/webportal/src/app/job-submission/utils/constants.js:31-85)
- [src/rest-server/src/models/v2/job/k8s.js:397-509](src/rest-server/src/models/v2/job/k8s.js:397-509)

## Runtime Plugins

OpenPAI supports runtime plugins to extend job functionality. These are specified in the `extras` field under `com.microsoft.pai.runtimeplugin`:

| Plugin | Purpose | Key Parameters |
|--------|---------|----------------|
| `ssh` | Enables SSH access to job containers | `jobssh`: Boolean to enable/disable |
| `tensorboard` | Sets up TensorBoard for visualization | `port`: Port to expose TensorBoard, `logdir`: Log directory |
| `teamwise_storage` | Configures storage for the job | `storageConfigNames`: Array of storage configurations to mount |

Example of a runtime plugin configuration in the job protocol:

```json
"extras": {
  "com.microsoft.pai.runtimeplugin": [
    {
      "plugin": "ssh",
      "parameters": {
        "jobssh": true
      }
    },
    {
      "plugin": "teamwise_storage",
      "parameters": {
        "storageConfigNames": ["nfs", "azure"]
      }
    }
  ]
}
```

Sources:
- [src/webportal/src/app/job-submission/models/protocol-schema.js:120-156](src/webportal/src/app/job-submission/models/protocol-schema.js:120-156)
- [src/webportal/src/app/job-submission/utils/constants.js:171-173](src/webportal/src/app/job-submission/utils/constants.js:171-173)
- [src/webportal/src/app/job-submission/job-submission-page.jsx:221-259](src/webportal/src/app/job-submission/job-submission-page.jsx:221-259)

## Integration with Web Portal

The Web Portal provides a user interface for creating and submitting jobs:

```mermaid
graph TB
    UI["Web Portal UI"] --> Form["Job Submission Form"]
    Form --> Basic["Basic Information Section"]
    Form --> TaskRoles["Task Roles Section"]
    Form --> Parameters["Parameters Section"]
    Form --> Secrets["Secrets Section"]
    Form --> EnvVars["Environment Variables Section"]
    Form --> Data["Data Section"]
    Form --> Tools["Tools Section"]
    
    Form -->|"validate"| Protocol["JobProtocol Object"]
    Protocol -->|"to YAML"| YamlEditor["YAML Editor"]
    Protocol -->|"submit"| REST["REST Server API"]
    
    YamlEditor -->|"validate & update"| Protocol
    
    subgraph "JobSubmissionPage Component"
        Form
        Protocol
        YamlEditor
    end
```

Key components:
1. `JobSubmissionPage`: Main component for job submission
2. `JobProtocol`: Class for handling job protocol validation and submission
3. `Submission-section`: Component for submitting the job
4. Various sidebar components for editing different aspects of the job

The Web Portal UI validates the job protocol using the same schema as the REST server, ensuring consistency in validation.

Sources:
- [src/webportal/src/app/job-submission/job-submission-page.jsx:73-396](src/webportal/src/app/job-submission/job-submission-page.jsx:73-396)
- [src/webportal/src/app/job-submission/components/submission-section.jsx:65-365](src/webportal/src/app/job-submission/components/submission-section.jsx:65-365)
- [src/webportal/src/app/job-submission/job-submission.jsx:1-78](src/webportal/src/app/job-submission/job-submission.jsx:1-78)

## Example Job Protocol

A simplified example of a job protocol for a PyTorch training job:

```yaml
protocolVersion: 2
name: pytorch_example
type: job
jobRetryCount: 0
prerequisites:
  - name: pytorch_image
    type: dockerimage
    uri: openpai/standard:python_3.6-pytorch_1.4.0-gpu
taskRoles:
  train:
    instances: 1
    completion:
      minSucceededInstances: 1
    dockerImage: pytorch_image
    resourcePerInstance:
      cpu: 4
      memoryMB: 8192
      gpu: 1
    commands:
      - pip install -r requirements.txt
      - python train.py --epochs 10
parameters:
  data_dir: /mnt/data
  epochs: 10
extras:
  com.microsoft.pai.runtimeplugin:
    - plugin: ssh
      parameters:
        jobssh: true
    - plugin: teamwise_storage
      parameters:
        storageConfigNames:
          - nfs-data
```

## Conclusion

The Job Protocol Schema is a central component in OpenPAI that defines the structure of job submissions. It serves as a bridge between the user interface and the underlying Kubernetes execution environment. Understanding the schema is essential for creating, debugging, and automating job submissions in OpenPAI.

The schema validation occurs at multiple levels in the system: in the Web Portal before submission, in the REST server after receiving the submission, and during conversion to Kubernetes resources. This multi-layered validation ensures that only valid job configurations are processed, providing clear error messages when validation fails.

The job protocol's structure is designed to be flexible, allowing for various job configurations from simple single-task jobs to complex distributed training with multiple task roles and custom runtime plugins.