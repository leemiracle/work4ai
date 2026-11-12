<!-- source: DeepWiki mcp.deepwiki.com · repo ray-project/ray · page 9 Cluster Deployment and Kubernetes · fetched 2026-10-21 -->

# Cluster Deployment and Kubernetes

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.vale/styles/Google/WordList.yml](.vale/styles/Google/WordList.yml)
- [.vale/styles/config/vocabularies/Core/accept.txt](.vale/styles/config/vocabularies/Core/accept.txt)
- [.vale/styles/config/vocabularies/General/accept.txt](.vale/styles/config/vocabularies/General/accept.txt)
- [.vale/styles/config/vocabularies/Train/accept.txt](.vale/styles/config/vocabularies/Train/accept.txt)
- [cpp/include/ray/api/ray_config.h](cpp/include/ray/api/ray_config.h)
- [doc/source/cluster/kubernetes/getting-started/kuberay-operator-installation.md](doc/source/cluster/kubernetes/getting-started/kuberay-operator-installation.md)
- [doc/source/cluster/kubernetes/images/platform-events-ui.png](doc/source/cluster/kubernetes/images/platform-events-ui.png)
- [doc/source/cluster/kubernetes/troubleshooting/rayservice-troubleshooting.md](doc/source/cluster/kubernetes/troubleshooting/rayservice-troubleshooting.md)
- [doc/source/cluster/kubernetes/user-guides.md](doc/source/cluster/kubernetes/user-guides.md)
- [doc/source/cluster/kubernetes/user-guides/config.md](doc/source/cluster/kubernetes/user-guides/config.md)
- [doc/source/cluster/kubernetes/user-guides/k8s-autoscaler.md](doc/source/cluster/kubernetes/user-guides/k8s-autoscaler.md)
- [doc/source/cluster/kubernetes/user-guides/k8s-events.md](doc/source/cluster/kubernetes/user-guides/k8s-events.md)
- [doc/source/cluster/kubernetes/user-guides/kuberay-gcs-rocksdb-ft.md](doc/source/cluster/kubernetes/user-guides/kuberay-gcs-rocksdb-ft.md)
- [doc/source/cluster/kubernetes/user-guides/network-policy.md](doc/source/cluster/kubernetes/user-guides/network-policy.md)
- [doc/source/cluster/kubernetes/user-guides/observability.md](doc/source/cluster/kubernetes/user-guides/observability.md)
- [doc/source/cluster/kubernetes/user-guides/scheduling.md](doc/source/cluster/kubernetes/user-guides/scheduling.md)
- [doc/source/ray-core/fault_tolerance/gcs.rst](doc/source/ray-core/fault_tolerance/gcs.rst)
- [doc/source/rllib/doc_code/rllib_on_ray_readme.py](doc/source/rllib/doc_code/rllib_on_ray_readme.py)
- [doc/source/serve/doc_code/fake_email_creator.yaml](doc/source/serve/doc_code/fake_email_creator.yaml)
- [doc/source/serve/doc_code/fault_tolerance/k8s_config.yaml](doc/source/serve/doc_code/fault_tolerance/k8s_config.yaml)
- [doc/source/serve/production-guide/fault-tolerance.md](doc/source/serve/production-guide/fault-tolerance.md)
- [doc/source/train/examples/transformers/transformer_reinforcement_learning/README.ipynb](doc/source/train/examples/transformers/transformer_reinforcement_learning/README.ipynb)
- [doc/source/train/examples/transformers/transformer_reinforcement_learning/README.md](doc/source/train/examples/transformers/transformer_reinforcement_learning/README.md)
- [doc/source/train/examples/transformers/transformer_reinforcement_learning/ci/aws.yaml](doc/source/train/examples/transformers/transformer_reinforcement_learning/ci/aws.yaml)
- [doc/source/train/examples/transformers/transformer_reinforcement_learning/ci/gce.yaml](doc/source/train/examples/transformers/transformer_reinforcement_learning/ci/gce.yaml)
- [doc/source/train/examples/transformers/transformer_reinforcement_learning/ci/nb2py.py](doc/source/train/examples/transformers/transformer_reinforcement_learning/ci/nb2py.py)
- [doc/source/train/examples/transformers/transformer_reinforcement_learning/ci/tests.sh](doc/source/train/examples/transformers/transformer_reinforcement_learning/ci/tests.sh)
- [doc/source/train/examples/transformers/transformer_reinforcement_learning/configs/aws.yaml](doc/source/train/examples/transformers/transformer_reinforcement_learning/configs/aws.yaml)
- [doc/source/train/examples/transformers/transformer_reinforcement_learning/configs/gce.yaml](doc/source/train/examples/transformers/transformer_reinforcement_learning/configs/gce.yaml)
- [python/ray/autoscaler/_private/kuberay/autoscaling_config.py](python/ray/autoscaler/_private/kuberay/autoscaling_config.py)
- [python/ray/autoscaler/_private/kuberay/node_provider.py](python/ray/autoscaler/_private/kuberay/node_provider.py)
- [python/ray/autoscaler/_private/kuberay/utils.py](python/ray/autoscaler/_private/kuberay/utils.py)
- [python/ray/autoscaler/batching_node_provider.py](python/ray/autoscaler/batching_node_provider.py)
- [python/ray/autoscaler/kuberay/init-config.sh](python/ray/autoscaler/kuberay/init-config.sh)
- [python/ray/autoscaler/kuberay/ray-cluster.complete.yaml](python/ray/autoscaler/kuberay/ray-cluster.complete.yaml)
- [python/ray/autoscaler/tags.py](python/ray/autoscaler/tags.py)
- [python/ray/tests/kuberay/test_autoscaling_config.py](python/ray/tests/kuberay/test_autoscaling_config.py)
- [python/ray/tests/kuberay/test_files/podlist1.yaml](python/ray/tests/kuberay/test_files/podlist1.yaml)
- [python/ray/tests/kuberay/test_files/podlist2.yaml](python/ray/tests/kuberay/test_files/podlist2.yaml)
- [python/ray/tests/kuberay/test_kuberay_node_provider.py](python/ray/tests/kuberay/test_kuberay_node_provider.py)
- [python/ray/tests/test_batch_node_provider_unit.py](python/ray/tests/test_batch_node_provider_unit.py)
- [release/k8s_tests/ray_rayservice_template.yaml](release/k8s_tests/ray_rayservice_template.yaml)
- [release/k8s_tests/run_gcs_ft_on_k8s.py](release/k8s_tests/run_gcs_ft_on_k8s.py)
- [rllib/core/distribution/__init__.py](rllib/core/distribution/__init__.py)
- [rllib/core/distribution/torch/__init__.py](rllib/core/distribution/torch/__init__.py)

</details>



This page provides an overview of deploying Ray clusters on Kubernetes using the KubeRay operator, as well as general cluster management concepts. Ray is designed to run seamlessly on Kubernetes, providing cloud-native abstractions for distributed computing.

## KubeRay: Ray on Kubernetes

KubeRay is the recommended way to deploy Ray on Kubernetes. It provides a Kubernetes operator that manages the lifecycle of Ray clusters, jobs, and services through Custom Resource Definitions (CRDs).

### Core Custom Resources

KubeRay defines three primary resources to manage different workload types:

| Resource | Purpose | Key Features |
| :--- | :--- | :--- |
| `RayCluster` | Foundation | Manages a head Pod and a set of worker Pods. [doc/source/cluster/kubernetes/user-guides/config.md:15-18]() |
| `RayJob` | Batch Workloads | Automatically creates a `RayCluster`, submits a job via `ray job submit`, and optionally cleans up resources upon completion. |
| `RayService` | Model Serving | Manages a `RayCluster` and Ray Serve applications with support for zero-downtime upgrades and high availability. |

### System Interaction

The following diagram shows how KubeRay components interact within a Kubernetes namespace.

**KubeRay Resource Orchestration**
```mermaid
graph TD
    subgraph "Kubernetes_Control_Plane"
        [KubeRay_Operator]
        [RayCluster_CR]
        [RayJob_CR]
        [RayService_CR]
    end

    subgraph "Ray_Cluster_Pods"
        [Ray_Head_Pod]
        [Ray_Worker_Pod]
        [Autoscaler_Sidecar]
    end

    [RayJob_CR] --> [KubeRay_Operator]
    [RayService_CR] --> [KubeRay_Operator]
    [KubeRay_Operator] --> [RayCluster_CR]
    [RayCluster_CR] --> [Ray_Head_Pod]
    [RayCluster_CR] --> [Ray_Worker_Pod]
    
    [Ray_Head_Pod] -->|Reports_Demand| [Autoscaler_Sidecar]
    [Autoscaler_Sidecar] -->|Updates_Replicas| [RayCluster_CR]
```
Sources: [doc/source/cluster/kubernetes/user-guides/config.md:15-18](), [doc/source/cluster/kubernetes/user-guides/config.md:95-101]()

For details on resource configuration and operator usage, see [KubeRay and Kubernetes Integration](#9.1).

---

## Cluster Management and Autoscaling

Ray clusters can scale dynamically based on the resource requirements of the workload (tasks, actors, and placement groups).

### Ray Autoscaler
On Kubernetes, the Ray Autoscaler typically runs as a sidecar container within the Ray head Pod. It monitors the resource demands of the cluster and adjusts the `replicas` field in the `RayCluster` CR. The KubeRay operator then reconciles this change by creating or deleting worker Pods.

The autoscaler configuration is derived from the Ray CR by the `AutoscalingConfigProducer` [python/ray/autoscaler/_private/kuberay/autoscaling_config.py:44-57](). This producer fetches the CR from the K8s API and generates an internal `autoscaling_config` [python/ray/autoscaler/_private/kuberay/autoscaling_config.py:65-68]().

**Autoscaling Logic to Code Mapping**
```mermaid
graph TD
    subgraph "Python_Autoscaler_Entities"
        [AutoscalingConfigProducer]
        [KubeRayNodeProvider]
        [KubernetesHttpApiClient]
    end

    subgraph "K8s_API_Entities"
        [RayCluster_Spec]
        [WorkerGroupSpecs]
    end

    [AutoscalingConfigProducer] -->|Calls| [KubernetesHttpApiClient]
    [KubernetesHttpApiClient] -->|GET| [RayCluster_Spec]
    [KubeRayNodeProvider] -->|Patch| [WorkerGroupSpecs]
    [KubeRayNodeProvider] -->|Calls| [worker_delete_patch]
```
Sources: [python/ray/autoscaler/_private/kuberay/autoscaling_config.py:44-68](), [python/ray/autoscaler/_private/kuberay/node_provider.py:87-97](), [python/ray/autoscaler/_private/kuberay/node_provider.py:170-172]()

### Fault Tolerance
The Global Control Service (GCS) is a critical component of the Ray head node. KubeRay supports GCS fault tolerance by using external storage to persist cluster metadata, allowing the GCS process to recover state upon Pod restart [doc/source/cluster/kubernetes/user-guides/user-guides.md:28-30]().

---

## Ecosystem Integration

Ray on Kubernetes integrates with several cloud-native tools to provide a production-ready environment:

*   **Observability:** Integration with **Prometheus** and **Grafana** [doc/source/cluster/kubernetes/user-guides/user-guides.md:23-23]().
*   **Service Mesh:** Support for **Istio** and ingress controls for traffic management.
*   **Scheduling:** Integration with batch schedulers like **Volcano**, **Yunikorn**, and **Kueue** [-.vale/styles/config/vocabularies/General/accept.txt:83-83]().

---

## Tooling and Development

Deploying and managing Ray clusters is supported by various CLI tools:

*   **kubectl ray:** A plugin for `kubectl` that simplifies RayCluster management, allowing users to create, get, and scale clusters without manual YAML manipulation [doc/source/cluster/kubernetes/user-guides/user-guides.md:41-41]().
*   **Ray Job CLI:** Used by `RayJob` to submit applications via `ray job submit`.

For security-related configurations, including RBAC and TLS, see [Logging, Tracing, and Security](#9.2).

---

## Child Pages
*   [KubeRay and Kubernetes Integration](#9.1) — Detailed documentation on KubeRay CRDs (`RayCluster`, `RayJob`, `RayService`), autoscaling v2, GCS fault tolerance, and ecosystem integrations.
*   [Logging, Tracing, and Security](#9.2) — Covers Ray's logging infrastructure, distributed tracing with OpenTelemetry, and security models including Kubernetes RBAC and token-based authentication.

---

