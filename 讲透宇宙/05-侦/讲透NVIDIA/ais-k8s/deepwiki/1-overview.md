<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/ais-k8s · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md)
- [docs/README.md](docs/README.md)
- [docs/network_configuration.md](docs/network_configuration.md)
- [docs/prerequisites.md](docs/prerequisites.md)
- [operator/README.md](operator/README.md)
- [operator/config/samples/ais_v1beta1_aistore.yaml](operator/config/samples/ais_v1beta1_aistore.yaml)
- [operator/config/samples/ais_v1beta1_aistore_tls_certmanager_csi.yaml](operator/config/samples/ais_v1beta1_aistore_tls_certmanager_csi.yaml)
- [operator/config/samples/ais_v1beta1_aistore_tracing.yaml](operator/config/samples/ais_v1beta1_aistore_tracing.yaml)
- [playbooks/README.md](playbooks/README.md)
- [playbooks/ais-deployment/docs/ais_cluster_management.md](playbooks/ais-deployment/docs/ais_cluster_management.md)
- [playbooks/host-config/README.md](playbooks/host-config/README.md)

</details>



This document provides a comprehensive overview of the AIStore Kubernetes (ais-k8s) repository, which serves as a complete toolkit for deploying and managing AIStore clusters in Kubernetes environments. AIStore is a lightweight, scalable object storage solution designed for AI applications that requires specialized Kubernetes integration for production deployments.

The ais-k8s repository encompasses four primary systems: the AIStore Kubernetes Operator for cluster lifecycle management, Helm Charts for package-based deployment, Ansible Playbooks for infrastructure automation, and a comprehensive monitoring stack. For detailed deployment instructions, see [Getting Started](#2). For operator-specific documentation, see [AIStore Kubernetes Operator](#3).

## System Architecture

The ais-k8s repository implements a multi-layered architecture that provides multiple deployment paths while converging on a unified runtime management system.

```mermaid
graph TB
    subgraph "Infrastructure Layer"
        K8S["Kubernetes Cluster"]
        NODES["K8s Nodes<br/>(Worker Nodes)"]
        STORAGE["Persistent Volumes<br/>(Block Storage)"]
    end
    
    subgraph "Deployment Tools"
        HELM["Helm Charts<br/>ais-operator, ais-cluster"]
        ANSIBLE["Ansible Playbooks<br/>ais_deploy_operator.yml<br/>ais_deploy_cluster.yml"]
        KUBECTL["Direct kubectl<br/>Manual YAML application"]
    end
    
    subgraph "Runtime Management"
        OPERATOR["AIS Operator<br/>ais-operator-controller-manager"]
        CRD["AIStore CRD<br/>ais.nvidia.com/v1beta1"]
        CR["AIStore Custom Resource<br/>kind: AIStore"]
    end
    
    subgraph "Generated Resources"
        CONFIGMAPS["ConfigMaps<br/>Global & Local Config"]
        STATEFULSETS["StatefulSets<br/>Proxy & Target Pods"]
        SERVICES["Services<br/>LoadBalancer & ClusterIP"]
        RBAC["RBAC Resources<br/>ServiceAccount/Role"]
    end
    
    subgraph "AIStore Runtime"
        PROXYPODS["Proxy Pods<br/>Gateway Layer"]
        TARGETPODS["Target Pods<br/>Storage Layer"]
        PVCS["PersistentVolumeClaims<br/>Data Storage"]
    end
    
    subgraph "Observability"
        MONITORING["Monitoring Stack<br/>Prometheus/Grafana/Alloy"]
        METRICS["Metrics Endpoint<br/>/metrics"]
        LOGS["Logs<br/>stdout/stderr"]
    end
    
    %% Deployment paths
    HELM --> OPERATOR
    ANSIBLE --> OPERATOR
    KUBECTL --> OPERATOR
    
    %% Operator management
    OPERATOR --> CRD
    OPERATOR --> CR
    CR --> CONFIGMAPS
    CR --> STATEFULSETS
    CR --> SERVICES
    CR --> RBAC
    
    %% Runtime deployment
    STATEFULSETS --> PROXYPODS
    STATEFULSETS --> TARGETPODS
    PVCS --> TARGETPODS
    
    %% Infrastructure dependencies
    PROXYPODS --> NODES
    TARGETPODS --> NODES
    PVCS --> STORAGE
    NODES --> K8S
    STORAGE --> K8S
    
    %% Monitoring flow
    PROXYPODS --> METRICS
    TARGETPODS --> METRICS
    METRICS --> MONITORING
    PROXYPODS --> LOGS
    TARGETPODS --> LOGS
    LOGS --> MONITORING
```

Sources: [README.md:1-36](), [operator/README.md:1-12](), [docs/README.md:35-89]()

## Core Components

### AIStore Kubernetes Operator

The operator implements the standard Kubernetes controller pattern to manage AIStore cluster lifecycle through custom resources. The core controller reconciles the desired state defined in `AIStore` custom resources with the actual cluster state.

```mermaid
graph TB
    subgraph "Operator Process"
        MAIN["main.go<br/>cmd/main.go"]
        MANAGER["Controller Manager<br/>ctrl.Manager"]
        RECONCILER["AIStore Reconciler<br/>controllers/aistore_controller.go"]
        WEBHOOK["Admission Webhook<br/>Validation Logic"]
        CLIENT["AIS Client<br/>API Communication"]
    end
    
    subgraph "Custom Resource API"
        AISTORETYPE["AIStore Type<br/>api/v1beta1/aistore_types.go"]
        AISTORESPEC["AIStoreSpec<br/>Desired Configuration"]
        AISTORESTATUS["AIStoreStatus<br/>Current State"]
        CRD_MANIFEST["CRD Manifest<br/>config/crd/bases"]
    end
    
    subgraph "Generated K8s Resources"
        GLOBALCONFIG["Global ConfigMap<br/>ais-operator-system"]
        LOCALCONFIG["Local ConfigMap<br/>Per-node configuration"]
        PROXYSS["Proxy StatefulSet<br/>aistore-sample-proxy"]
        TARGETSS["Target StatefulSet<br/>aistore-sample-target"]
        PROXYSVC["Proxy Service<br/>LoadBalancer type"]
        TARGETSVC["Target Service<br/>LoadBalancer type"]
    end
    
    subgraph "Runtime Pods"
        PROXYPOD["Proxy Pod<br/>aistore-sample-proxy-0"]
        TARGETPOD["Target Pod<br/>aistore-sample-target-0"]
        INITCONTAINER["Init Container<br/>aistorage/ais-init"]
        NODECONTAINER["Node Container<br/>aistorage/aisnode"]
    end
    
    %% Control flow
    MAIN --> MANAGER
    MANAGER --> RECONCILER
    MANAGER --> WEBHOOK
    MANAGER --> CLIENT
    
    %% API definitions
    RECONCILER --> AISTORETYPE
    AISTORETYPE --> AISTORESPEC
    AISTORETYPE --> AISTORESTATUS
    
    %% Resource generation
    RECONCILER --> GLOBALCONFIG
    RECONCILER --> LOCALCONFIG
    RECONCILER --> PROXYSS
    RECONCILER --> TARGETSS
    RECONCILER --> PROXYSVC
    RECONCILER --> TARGETSVC
    
    %% Pod creation
    PROXYSS --> PROXYPOD
    TARGETSS --> TARGETPOD
    PROXYPOD --> INITCONTAINER
    PROXYPOD --> NODECONTAINER
    TARGETPOD --> INITCONTAINER
    TARGETPOD --> NODECONTAINER
    
    %% Status reporting
    PROXYPOD --> AISTORESTATUS
    TARGETPOD --> AISTORESTATUS
    CLIENT --> AISTORESTATUS
```

Sources: [operator/README.md:1-12](), [operator/config/samples/ais_v1beta1_aistore.yaml:1-49]()

### Deployment Methods

The repository provides three primary deployment approaches, each targeting different use cases and automation levels.

```mermaid
graph LR
    subgraph "Helm Deployment"
        HELMOPS["helm install ais-operator<br/>ais-k8s/ais-operator"]
        HELMCLUSTER["helm install ais-cluster<br/>ais-k8s/ais-cluster"]
        HELMFILE["helmfile sync<br/>helmfile.yaml"]
    end
    
    subgraph "Ansible Deployment"
        ANSIBLEOPS["ansible-playbook<br/>ais_deploy_operator.yml"]
        ANSIBLECLUSTER["ansible-playbook<br/>ais_deploy_cluster.yml"]
        HOSTCONFIG["ansible-playbook<br/>ais_host_config.yml"]
    end
    
    subgraph "Manual Deployment"
        MAKEINSTALL["make install<br/>CRD installation"]
        MAKEDEPLOY["make deploy<br/>Operator deployment"]
        KUBECTLAPPLY["kubectl apply<br/>AIStore CR"]
    end
    
    subgraph "Common Infrastructure"
        OPERATOR_POD["ais-operator-controller-manager<br/>Operator Pod"]
        AISTORE_CR["AIStore Custom Resource<br/>kind: AIStore"]
        CLUSTER_PODS["AIStore Cluster Pods<br/>proxy-0, target-0"]
    end
    
    %% Helm flow
    HELMOPS --> OPERATOR_POD
    HELMCLUSTER --> AISTORE_CR
    HELMFILE --> HELMOPS
    HELMFILE --> HELMCLUSTER
    
    %% Ansible flow
    HOSTCONFIG --> ANSIBLEOPS
    ANSIBLEOPS --> OPERATOR_POD
    ANSIBLECLUSTER --> AISTORE_CR
    
    %% Manual flow
    MAKEINSTALL --> MAKEDEPLOY
    MAKEDEPLOY --> OPERATOR_POD
    KUBECTLAPPLY --> AISTORE_CR
    
    %% Common convergence
    OPERATOR_POD --> CLUSTER_PODS
    AISTORE_CR --> CLUSTER_PODS
```

Sources: [docs/README.md:39-71](), [operator/README.md:55-83](), [playbooks/ais-deployment/docs/ais_cluster_management.md:21-82]()

## Configuration and Resource Management

The operator transforms high-level AIStore specifications into concrete Kubernetes resources through a layered configuration system.

```mermaid
graph TD
    subgraph "Configuration Sources"
        DEFAULTS["Default Values<br/>roles/*/defaults/main.yml"]
        USERSPEC["User AIStore Spec<br/>spec.configToUpdate"]
        ENVVARS["Environment Variables<br/>spec.targetSpec.env"]
        SECRETS["Kubernetes Secrets<br/>aws-creds, gcp-creds"]
    end
    
    subgraph "Template Processing"
        JINJA2["Jinja2 Templates<br/>ais.yaml.j2"]
        GOTEMPLATE["Go Templates<br/>Helm charts/*.gotmpl"]
        RECONCILER_LOGIC["Reconciler Logic<br/>Resource generation"]
    end
    
    subgraph "Generated Configuration"
        GLOBAL_CM["Global ConfigMap<br/>ais-global-config"]
        LOCAL_CM["Local ConfigMap<br/>ais-local-config"]
        NETWORK_CONFIG["Network Configuration<br/>servicePort, hostPort"]
        STORAGE_CONFIG["Storage Configuration<br/>mounts, PVCs"]
    end
    
    subgraph "Kubernetes Resources"
        PROXY_SS["Proxy StatefulSet<br/>spec.proxySpec"]
        TARGET_SS["Target StatefulSet<br/>spec.targetSpec"]
        PROXY_SVC["Proxy Service<br/>enableExternalLB"]
        TARGET_SVC["Target Service<br/>LoadBalancer type"]
        PVCS["PersistentVolumeClaims<br/>spec.targetSpec.mounts"]
    end
    
    subgraph "Runtime Pods"
        PROXY_PODS["Proxy Pods<br/>portPublic: 51080"]
        TARGET_PODS["Target Pods<br/>portPublic: 51081"]
        MOUNTED_STORAGE["Mounted Storage<br/>/ais1, /ais2"]
    end
    
    %% Configuration flow
    DEFAULTS --> JINJA2
    USERSPEC --> GOTEMPLATE
    ENVVARS --> RECONCILER_LOGIC
    SECRETS --> RECONCILER_LOGIC
    
    %% Template processing
    JINJA2 --> GLOBAL_CM
    GOTEMPLATE --> LOCAL_CM
    RECONCILER_LOGIC --> NETWORK_CONFIG
    RECONCILER_LOGIC --> STORAGE_CONFIG
    
    %% Resource generation
    GLOBAL_CM --> PROXY_SS
    LOCAL_CM --> TARGET_SS
    NETWORK_CONFIG --> PROXY_SVC
    NETWORK_CONFIG --> TARGET_SVC
    STORAGE_CONFIG --> PVCS
    
    %% Runtime deployment
    PROXY_SS --> PROXY_PODS
    TARGET_SS --> TARGET_PODS
    PVCS --> MOUNTED_STORAGE
    MOUNTED_STORAGE --> TARGET_PODS
```

Sources: [operator/config/samples/ais_v1beta1_aistore.yaml:8-31](), [playbooks/ais-deployment/docs/ais_cluster_management.md:41-74]()

## Key Resource Specifications

The AIStore custom resource defines the complete cluster configuration through structured specifications:

| Component | Key Fields | Purpose |
|-----------|------------|---------|
| `spec.size` | Integer | Number of target pods in cluster |
| `spec.proxySpec` | `servicePort`, `hostPort`, `portPublic` | Proxy pod network configuration |
| `spec.targetSpec` | `servicePort`, `hostPort`, `mounts` | Target pod and storage configuration |
| `spec.targetSpec.mounts` | `path`, `size`, `label` | Persistent volume mount specifications |
| `spec.nodeImage` | Container image | AIStore runtime container |
| `spec.initImage` | Container image | Initialization container |
| `spec.enableExternalLB` | Boolean | External LoadBalancer service creation |
| `spec.configToUpdate` | Nested object | AIStore-specific configuration overrides |

Sources: [operator/config/samples/ais_v1beta1_aistore.yaml:1-49]()

## Monitoring and Observability

The monitoring stack provides comprehensive observability for AIStore clusters through industry-standard tools integrated with Kubernetes-native collection mechanisms.

```mermaid
graph TB
    subgraph "AIStore Runtime"
        PROXY_METRICS["Proxy /metrics<br/>HTTP endpoint"]
        TARGET_METRICS["Target /metrics<br/>HTTP endpoint"] 
        PROXY_LOGS["Proxy Logs<br/>stdout/stderr"]
        TARGET_LOGS["Target Logs<br/>stdout/stderr"]
    end
    
    subgraph "Collection Layer"
        ALLOY["Grafana Alloy<br/>Telemetry Pipeline"]
        PROMETHEUS["Prometheus<br/>Metrics Storage"]
        LOKI["Loki<br/>Log Aggregation"]
    end
    
    subgraph "Visualization"
        GRAFANA["Grafana<br/>Dashboard Platform"]
        DASHBOARDS["AIS Dashboards<br/>Performance/Capacity"]
        ALERTMANAGER["AlertManager<br/>Notification System"]
    end
    
    subgraph "Configuration"
        MONITORING_HELM["monitoring Helm Charts<br/>Stack deployment"]
        SERVICEMONITOR["ServiceMonitor<br/>Prometheus discovery"]
        ALERTRULES["PrometheusRule<br/>Alert definitions"]
    end
    
    %% Data flow
    PROXY_METRICS --> ALLOY
    TARGET_METRICS --> ALLOY
    PROXY_LOGS --> ALLOY
    TARGET_LOGS --> ALLOY
    
    %% Processing
    ALLOY --> PROMETHEUS
    ALLOY --> LOKI
    PROMETHEUS --> GRAFANA
    LOKI --> GRAFANA
    PROMETHEUS --> ALERTMANAGER
    
    %% Configuration
    MONITORING_HELM --> SERVICEMONITOR
    MONITORING_HELM --> ALERTRULES
    SERVICEMONITOR --> PROMETHEUS
    ALERTRULES --> ALERTMANAGER
    GRAFANA --> DASHBOARDS
```

Sources: [docs/README.md:122-127](), [monitoring/README.md]()

## Development and Testing Infrastructure

The repository includes comprehensive development tooling and continuous integration systems for maintaining code quality and deployment reliability.

| Component | Purpose | Key Files |
|-----------|---------|-----------|
| E2E Testing | End-to-end cluster validation | [tests/README.md]() |
| GitHub Actions | CI/CD pipeline automation | [.github/workflows/]() |
| Kind Integration | Local Kubernetes testing | Test configuration |
| Ginkgo Framework | Behavior-driven testing | Test specifications |
| Docker Build | Container image automation | [Makefile](), [Dockerfile]() |

The testing framework validates operator functionality across multiple Kubernetes distributions and deployment scenarios, ensuring compatibility with production environments.

Sources: [operator/README.md:329-332](), [operator/tests/README.md]()

---

