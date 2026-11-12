> 来源: [https://deepwiki.com/ray-project/ray/9-cluster-deployment-and-kubernetes](https://deepwiki.com/ray-project/ray/9-cluster-deployment-and-kubernetes)
> DeepWiki ray-project/ray | Last indexed: 25 June 2026 (bf1295

# Cluster Deployment and Kubernetes

  Relevant source files 
 - [ci/env/install-core-prerelease-dependencies.sh](https://github.com/ray-project/ray/blob/bf129559/ci/env/install-core-prerelease-dependencies.sh)
 - [doc/source/cluster/kubernetes/examples/mobilenet-rayservice.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/examples/mobilenet-rayservice.md?plain=1)
 - [doc/source/cluster/kubernetes/examples/rayjob-batch-inference-example.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/examples/rayjob-batch-inference-example.md?plain=1)
 - [doc/source/cluster/kubernetes/getting-started/kuberay-operator-installation.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/getting-started/kuberay-operator-installation.md?plain=1)
 - [doc/source/cluster/kubernetes/getting-started/raycluster-quick-start.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/getting-started/raycluster-quick-start.md?plain=1)
 - [doc/source/cluster/kubernetes/getting-started/rayjob-quick-start.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/getting-started/rayjob-quick-start.md?plain=1)
 - [doc/source/cluster/kubernetes/getting-started/rayservice-quick-start.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/getting-started/rayservice-quick-start.md?plain=1)
 - [doc/source/cluster/kubernetes/images/rayservice-no-ray-serve-replica-dashboard.png](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/images/rayservice-no-ray-serve-replica-dashboard.png)
 - [doc/source/cluster/kubernetes/k8s-ecosystem/ingress.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/k8s-ecosystem/ingress.md?plain=1)
 - [doc/source/cluster/kubernetes/k8s-ecosystem/istio.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/k8s-ecosystem/istio.md?plain=1)
 - [doc/source/cluster/kubernetes/k8s-ecosystem/prometheus-grafana.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/k8s-ecosystem/prometheus-grafana.md?plain=1)
 - [doc/source/cluster/kubernetes/k8s-ecosystem/volcano.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/k8s-ecosystem/volcano.md?plain=1)
 - [doc/source/cluster/kubernetes/k8s-ecosystem/yunikorn.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/k8s-ecosystem/yunikorn.md?plain=1)
 - [doc/source/cluster/kubernetes/user-guides/configuring-autoscaling.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/user-guides/configuring-autoscaling.md?plain=1)
 - [doc/source/cluster/kubernetes/user-guides/gcp-gke-tpu-cluster.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/user-guides/gcp-gke-tpu-cluster.md?plain=1)
 - [doc/source/cluster/kubernetes/user-guides/gke-gcs-bucket.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/user-guides/gke-gcs-bucket.md?plain=1)
 - [doc/source/cluster/kubernetes/user-guides/helm-chart-rbac.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/user-guides/helm-chart-rbac.md?plain=1)
 - [doc/source/cluster/kubernetes/user-guides/kubectl-plugin.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/user-guides/kubectl-plugin.md?plain=1)
 - [doc/source/cluster/kubernetes/user-guides/kuberay-gcs-ft.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/user-guides/kuberay-gcs-ft.md?plain=1)
 - [doc/source/cluster/kubernetes/user-guides/rayservice-high-availability.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/user-guides/rayservice-high-availability.md?plain=1)
 - [doc/source/cluster/kubernetes/user-guides/rayservice-no-ray-serve-replica.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/user-guides/rayservice-no-ray-serve-replica.md?plain=1)
 - [doc/source/cluster/kubernetes/user-guides/rayservice.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/user-guides/rayservice.md?plain=1)
 - [doc/source/cluster/kubernetes/user-guides/tls.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/user-guides/tls.md?plain=1)
 - [doc/source/cluster/kubernetes/user-guides/upgrade-guide.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/user-guides/upgrade-guide.md?plain=1)
 - [doc/source/cluster/kubernetes/user-guides/uv.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/user-guides/uv.md?plain=1)
 - [python/ray/autoscaler/_private/kuberay/autoscaling_config.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/autoscaler/_private/kuberay/autoscaling_config.py)
 - [python/ray/autoscaler/_private/kuberay/node_provider.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/autoscaler/_private/kuberay/node_provider.py)
 - [python/ray/autoscaler/_private/kuberay/run_autoscaler.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/autoscaler/_private/kuberay/run_autoscaler.py)
 - [python/ray/autoscaler/_private/kuberay/utils.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/autoscaler/_private/kuberay/utils.py)
 - [python/ray/autoscaler/batching_node_provider.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/autoscaler/batching_node_provider.py)
 - [python/ray/autoscaler/kuberay/ray-cluster.complete.yaml](https://github.com/ray-project/ray/blob/bf129559/python/ray/autoscaler/kuberay/ray-cluster.complete.yaml)
 - [python/ray/autoscaler/ray-schema.json](https://github.com/ray-project/ray/blob/bf129559/python/ray/autoscaler/ray-schema.json)
 - [python/ray/autoscaler/tags.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/autoscaler/tags.py)
 - [python/ray/autoscaler/v2/BUILD.bazel](https://github.com/ray-project/ray/blob/bf129559/python/ray/autoscaler/v2/BUILD.bazel)
 - [python/ray/autoscaler/v2/instance_manager/cloud_providers/kuberay/cloud_provider.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/autoscaler/v2/instance_manager/cloud_providers/kuberay/cloud_provider.py)
 - [python/ray/autoscaler/v2/instance_manager/cloud_providers/kuberay/ippr_provider.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/autoscaler/v2/instance_manager/cloud_providers/kuberay/ippr_provider.py)
 - [python/ray/autoscaler/v2/instance_manager/subscribers/cloud_resource_monitor.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/autoscaler/v2/instance_manager/subscribers/cloud_resource_monitor.py)
 - [python/ray/autoscaler/v2/tests/test_ippr_provider.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/autoscaler/v2/tests/test_ippr_provider.py)
 - [python/ray/autoscaler/v2/tests/test_node_provider.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/autoscaler/v2/tests/test_node_provider.py)
 - [python/ray/autoscaler/v2/tests/test_priority_selection.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/autoscaler/v2/tests/test_priority_selection.py)
 - [python/ray/tests/kuberay/test_autoscaling_config.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/kuberay/test_autoscaling_config.py)
 - [python/ray/tests/kuberay/test_files/podlist2.yaml](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/kuberay/test_files/podlist2.yaml)
 - [python/ray/tests/kuberay/test_kuberay_node_provider.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/kuberay/test_kuberay_node_provider.py)
 - [python/ray/tests/test_batch_node_provider_unit.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_batch_node_provider_unit.py)
 - [release/k8s_tests/ray_v1alpha1_rayservice_template.yaml](https://github.com/ray-project/ray/blob/bf129559/release/k8s_tests/ray_v1alpha1_rayservice_template.yaml)
 
  This page provides an overview of deploying Ray clusters on Kubernetes using the KubeRay operator, as well as general cluster management concepts. Ray is designed to run seamlessly on Kubernetes, providing cloud-native abstractions for distributed computing.

 
## KubeRay: Ray on Kubernetes

 KubeRay is the recommended way to deploy Ray on Kubernetes. It provides a Kubernetes operator that manages the lifecycle of Ray clusters, jobs, and services through Custom Resource Definitions (CRDs).

 
### Core Custom Resources

 KubeRay defines three primary resources to manage different workload types:

 
| Resource | Purpose | Key Features |
|---|---|---|
| RayCluster | Foundation | Manages a head Pod and a set of worker Pods. doc/source/cluster/kubernetes/getting-started/rayjob-quick-start.md15 |
| RayJob | Batch Workloads | Automatically creates a RayCluster, submits a job via ray job submit, and optionally cleans up resources upon completion. doc/source/cluster/kubernetes/getting-started/rayjob-quick-start.md13-20 |
| RayService | Model Serving | Manages a RayCluster and Ray Serve applications with support for zero-downtime upgrades and high availability. doc/source/cluster/kubernetes/user-guides/rayservice.md9-21 |

 
### System Interaction

 The following diagram shows how KubeRay components interact within a Kubernetes namespace.

 **KubeRay Resource Orchestration**

 
```

```

 Sources: [doc/source/cluster/kubernetes/user-guides/configuring-autoscaling.md24-50](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/user-guides/configuring-autoscaling.md?plain=1#L24-L50) [doc/source/cluster/kubernetes/getting-started/rayjob-quick-start.md13-16](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/getting-started/rayjob-quick-start.md?plain=1#L13-L16)

 For details on resource configuration and operator usage, see [KubeRay and Kubernetes Integration](https://deepwiki.com/ray-project/ray/9.1-kuberay-and-kubernetes-integration).

 
---

 
## Cluster Management and Autoscaling

 Ray clusters can scale dynamically based on the resource requirements of the workload (tasks, actors, and placement groups).

 
### Ray Autoscaler

 On Kubernetes, the Ray Autoscaler typically runs as a sidecar container within the Ray head Pod [doc/source/cluster/kubernetes/user-guides/configuring-autoscaling.md24-25](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/user-guides/configuring-autoscaling.md?plain=1#L24-L25) It monitors the resource demands of the cluster and adjusts the `replicas` field in the `RayCluster` CR. The KubeRay operator then reconciles this change by creating or deleting worker Pods [doc/source/cluster/kubernetes/user-guides/configuring-autoscaling.md40-50](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/user-guides/configuring-autoscaling.md?plain=1#L40-L50)

 The autoscaler configuration is derived from the Ray CR by the `AutoscalingConfigProducer` [python/ray/autoscaler/_private/kuberay/autoscaling_config.py43-56](https://github.com/ray-project/ray/blob/bf129559/python/ray/autoscaler/_private/kuberay/autoscaling_config.py#L43-L56) This producer fetches the CR from the K8s API and generates an internal `autoscaling_config` [python/ray/autoscaler/_private/kuberay/autoscaling_config.py64-67](https://github.com/ray-project/ray/blob/bf129559/python/ray/autoscaler/_private/kuberay/autoscaling_config.py#L64-L67)

 **Autoscaling Logic to Code Mapping**

 
```

```

 Sources: [python/ray/autoscaler/_private/kuberay/autoscaling_config.py58-67](https://github.com/ray-project/ray/blob/bf129559/python/ray/autoscaler/_private/kuberay/autoscaling_config.py#L58-L67) [python/ray/autoscaler/v2/instance_manager/cloud_providers/kuberay/cloud_provider.py52-83](https://github.com/ray-project/ray/blob/bf129559/python/ray/autoscaler/v2/instance_manager/cloud_providers/kuberay/cloud_provider.py#L52-L83) [python/ray/autoscaler/_private/kuberay/node_provider.py158-161](https://github.com/ray-project/ray/blob/bf129559/python/ray/autoscaler/_private/kuberay/node_provider.py#L158-L161)

 
### Fault Tolerance

 The Global Control Service (GCS) is a critical component of the Ray head node. KubeRay supports GCS fault tolerance by using external storage to persist cluster metadata, allowing the GCS process to recover state upon Pod restart [doc/source/cluster/kubernetes/user-guides/kuberay-gcs-ft.md4-8](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/user-guides/kuberay-gcs-ft.md?plain=1#L4-L8)

 
---

 
## Ecosystem Integration

 Ray on Kubernetes integrates with several cloud-native tools to provide a production-ready environment:

 
 - **Observability:** Integration with **Prometheus** and **Grafana**. KubeRay exposes metrics on port `8080` by default [doc/source/cluster/kubernetes/k8s-ecosystem/prometheus-grafana.md93-101](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/k8s-ecosystem/prometheus-grafana.md?plain=1#L93-L101)
 - **Service Mesh:** Support for **Istio** and **Ingress** for traffic management [doc/source/cluster/kubernetes/k8s-ecosystem/istio.md2-4](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/k8s-ecosystem/istio.md?plain=1#L2-L4)
 - **Scheduling:** Integration with batch schedulers like **Volcano**, **Yunikorn**, and **Kueue** [doc/source/cluster/kubernetes/getting-started/rayjob-quick-start.md72](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/getting-started/rayjob-quick-start.md?plain=1#L72-L72)
 
 
---

 
## Tooling and Development

 Deploying and managing Ray clusters is supported by various CLI tools:

 
 - **kubectl ray:** A plugin for `kubectl` that simplifies RayCluster management, allowing users to create, get, and scale clusters without manual YAML manipulation [doc/source/cluster/kubernetes/user-guides/kubectl-plugin.md3-9](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/user-guides/kubectl-plugin.md?plain=1#L3-L9)
 - **Ray Job CLI:** Used by `RayJob` to submit applications via `ray job submit` [doc/source/cluster/kubernetes/getting-started/rayjob-quick-start.md33](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/kubernetes/getting-started/rayjob-quick-start.md?plain=1#L33-L33)
 
 For security-related configurations, including RBAC and TLS, see [Logging, Tracing, and Security](https://deepwiki.com/ray-project/ray/9.2-logging-tracing-and-security).

 
---

 
## Child Pages

 
 - [KubeRay and Kubernetes Integration](https://deepwiki.com/ray-project/ray/9.1-kuberay-and-kubernetes-integration) — Detailed documentation on KubeRay CRDs (`RayCluster`, `RayJob`, `RayService`), autoscaling v2, GCS fault tolerance, and ecosystem integrations.
 - [Logging, Tracing, and Security](https://deepwiki.com/ray-project/ray/9.2-logging-tracing-and-security) — Covers Ray's logging infrastructure, distributed tracing with OpenTelemetry, and security models including Kubernetes RBAC and token-based authentication.
