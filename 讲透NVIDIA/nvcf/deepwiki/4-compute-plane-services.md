<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvcf · page 4 Compute Plane Services · fetched 2026-10-26 -->

# Compute Plane Services

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deploy/helm/nvca-operator/Makefile](deploy/helm/nvca-operator/Makefile)
- [deploy/helm/nvca-operator/nvca-operator/README.md](deploy/helm/nvca-operator/nvca-operator/README.md)
- [deploy/helm/nvca-operator/nvca-operator/templates/_helpers.tpl](deploy/helm/nvca-operator/nvca-operator/templates/_helpers.tpl)
- [deploy/helm/nvca-operator/nvca-operator/templates/deployment.yaml](deploy/helm/nvca-operator/nvca-operator/templates/deployment.yaml)
- [deploy/helm/nvca-operator/nvca-operator/values.schema.json](deploy/helm/nvca-operator/nvca-operator/values.schema.json)
- [deploy/helm/nvca-operator/nvca-operator/values.yaml](deploy/helm/nvca-operator/nvca-operator/values.yaml)
- [deploy/helm/nvca-operator/scripts/ci_vendor_nvca_operator_chart](deploy/helm/nvca-operator/scripts/ci_vendor_nvca_operator_chart)
- [deploy/helm/nvca-operator/scripts/render_release_supplemental_images.sh](deploy/helm/nvca-operator/scripts/render_release_supplemental_images.sh)
- [deploy/helm/nvca-operator/tests/image_pull_secret_defaults_test.sh](deploy/helm/nvca-operator/tests/image_pull_secret_defaults_test.sh)
- [deploy/helm/nvca-operator/tests/release_image_manifest_test.sh](deploy/helm/nvca-operator/tests/release_image_manifest_test.sh)
- [deploy/helm/nvca-operator/tests/self_managed_nvca_image_reference_test.sh](deploy/helm/nvca-operator/tests/self_managed_nvca_image_reference_test.sh)
- [deploy/stacks/nvcf-compute-plane/Makefile](deploy/stacks/nvcf-compute-plane/Makefile)
- [deploy/stacks/nvcf-compute-plane/README.md](deploy/stacks/nvcf-compute-plane/README.md)
- [deploy/stacks/nvcf-compute-plane/environments/base.yaml](deploy/stacks/nvcf-compute-plane/environments/base.yaml)
- [deploy/stacks/nvcf-compute-plane/helmfile.d/02-nvca.yaml.gotmpl](deploy/stacks/nvcf-compute-plane/helmfile.d/02-nvca.yaml.gotmpl)
- [deploy/stacks/nvcf-compute-plane/testdata/golden/local/02-nvca.yaml-nvca-operator/helm-nvca-operator/templates/agent-config-merge-cm.yaml](deploy/stacks/nvcf-compute-plane/testdata/golden/local/02-nvca.yaml-nvca-operator/helm-nvca-operator/templates/agent-config-merge-cm.yaml)
- [deploy/stacks/nvcf-compute-plane/testdata/golden/local/02-nvca.yaml-nvca-operator/helm-nvca-operator/templates/rbac_allowed_extra_types.yaml](deploy/stacks/nvcf-compute-plane/testdata/golden/local/02-nvca.yaml-nvca-operator/helm-nvca-operator/templates/rbac_allowed_extra_types.yaml)
- [deploy/stacks/nvcf-compute-plane/testdata/golden/local/02-nvca.yaml-nvca-operator/helm-nvca-operator/templates/self-managed-nvcfbackend-cm.yaml](deploy/stacks/nvcf-compute-plane/testdata/golden/local/02-nvca.yaml-nvca-operator/helm-nvca-operator/templates/self-managed-nvcfbackend-cm.yaml)
- [deploy/stacks/nvcf-compute-plane/tests/observability-profile.sh](deploy/stacks/nvcf-compute-plane/tests/observability-profile.sh)
- [src/compute-plane-services/nvca/deployments/nvca-operator/README.md](src/compute-plane-services/nvca/deployments/nvca-operator/README.md)
- [src/compute-plane-services/nvca/deployments/nvca-operator/templates/_helpers.tpl](src/compute-plane-services/nvca/deployments/nvca-operator/templates/_helpers.tpl)
- [src/compute-plane-services/nvca/deployments/nvca-operator/templates/deployment.yaml](src/compute-plane-services/nvca/deployments/nvca-operator/templates/deployment.yaml)
- [src/compute-plane-services/nvca/deployments/nvca-operator/values.schema.json](src/compute-plane-services/nvca/deployments/nvca-operator/values.schema.json)
- [src/compute-plane-services/nvca/deployments/nvca-operator/values.yaml](src/compute-plane-services/nvca/deployments/nvca-operator/values.yaml)

</details>



The **Compute Plane** is the execution layer of NVIDIA Cloud Functions (NVCF). It consists of GPU-enabled Kubernetes clusters that host the physical workloads. Services in this plane are responsible for cluster registration, workload lifecycle management (MiniServices), worker sidecar injection, observability, and specialized caching.

## Architecture Overview

The Compute Plane interacts with the Control Plane via the **NVIDIA Cluster Agent (NVCA)**. It receives workload definitions, pulls necessary container images and models, and provides execution environments for both containerized and Helm-packaged functions.

### Component Relationship

The following diagram illustrates how the compute plane components interact to prepare and execute a workload pod.

**Workload Execution Flow**
```mermaid
graph TD
    subgraph "Kubernetes Cluster (Compute Plane)"
        [NVCA-Operator] --> |"Deploys"| [NVCA-Agent]
        [NVCA-Agent] --> |"Watches"| [NVCFBackend-CRD]
        [MiniService-Controller] --> |"Manages"| [Function-Pods]
        
        subgraph "Function Pod"
            [worker-init] --> |"Downloads"| [Model-Cache]
            [ESS-Agent] --> |"Fetches"| [Secrets]
            [worker-task] --> |"Executes"| [User-Container]
            [BYOO-OTel] --> |"Exports"| [Telemetry]
        end
    end

    [Control-Plane] <--> |"NATS / ICMS"| [NVCA-Agent]
```
**Sources:** [deploy/helm/nvca-operator/nvca-operator/values.yaml:68-75](), [deploy/stacks/nvcf-compute-plane/helmfile.d/02-nvca.yaml.gotmpl:3-5]()

---

## 4.1 NVIDIA Cluster Agent (NVCA) and Operator

The **NVCA Operator** is the primary entry point for a GPU cluster into the NVCF ecosystem. It manages the lifecycle of the **NVCA Agent**, which handles the actual registration and communication with the Control Plane.

*   **Cluster Source Modes:** Supports `ngc-managed`, `helm-managed`, and `self-managed` modes for registration [deploy/helm/nvca-operator/nvca-operator/values.yaml:74-80]().
*   **NVCFBackend CRD:** The operator watches this Custom Resource to configure the cluster's connection to the Control Plane.
*   **Cluster Validator:** An init container that ensures the cluster meets hardware and software requirements before the agent starts [deploy/helm/nvca-operator/nvca-operator/templates/deployment.yaml:69-101]().
*   **Graceful Shutdown:** Implements a `terminationGracePeriodSeconds` (default 600s) to allow active workloads to complete before agent exit [deploy/helm/nvca-operator/nvca-operator/templates/deployment.yaml:60-60]().

For details, see [NVIDIA Cluster Agent (NVCA) and Operator](#4.1).

**Sources:** [deploy/helm/nvca-operator/nvca-operator/values.yaml:1-100](), [deploy/helm/nvca-operator/nvca-operator/templates/deployment.yaml:16-163]()

---

## 4.2 MiniService Controller and Helm Function Lifecycle

The **MiniService Controller** manages complex workloads defined as Helm charts. Unlike standard container functions, MiniServices allow for multi-pod deployments, custom sidecars, and advanced Kubernetes resources (like `PodGroups` or `PodCliques`).

*   **Reconcile Loop:** Monitors `MiniService` objects and ensures the desired Helm release state is maintained.
*   **Feature Gates:** Supports specialized scheduling and operators like `KAIScheduler` and `DynamoOperatorSupport` [deploy/stacks/nvcf-compute-plane/helmfile.d/02-nvca.yaml.gotmpl:31-56]().
*   **Validation Policy:** Enforces restrictions on which Kubernetes types can be deployed within a function's Helm chart [deploy/stacks/nvcf-compute-plane/helmfile.d/02-nvca.yaml.gotmpl:108-130]().

For details, see [MiniService Controller and Helm Function Lifecycle](#4.2).

**Sources:** [deploy/stacks/nvcf-compute-plane/helmfile.d/02-nvca.yaml.gotmpl:95-130]()

---

## 4.3 Worker Sidecars: Init, Utils, Task, and ESS Agent

Every function pod is injected with a suite of sidecars that handle infrastructure concerns, allowing the user container to focus solely on the compute logic.

*   **worker-init:** Responsible for downloading large model assets and resources before the main container starts.
*   **ESS Agent:** Renders secrets from the Encrypted Secret Store (ESS) into the pod's environment or filesystem.
*   **worker-task:** The async task worker (NVCT) that pulls jobs from the messaging backbone.
*   **worker-utils:** Provides a local NATS proxy and other utility services.

For details, see [Worker Sidecars: Init, Utils, Task, and ESS Agent](#4.3).

---

## 4.4 BYOO OpenTelemetry Collector

The **Bring-Your-Own-OTel (BYOO)** collector allows tenants to export logs, metrics, and traces to their own observability backends.

*   **Deployment Shapes:** Can be deployed as a sidecar within the function pod or as a standalone utility pod in the cluster [deploy/helm/nvca-operator/nvca-operator/values.yaml:30-40]().
*   **Config Rendering:** The `otelconfig` pipeline dynamically generates collector configurations based on the tenant's requirements.
*   **Sampling:** Supports configurable log and trace sampling percentages to manage data volume [deploy/helm/nvca-operator/nvca-operator/values.yaml:118-128]().

For details, see [BYOO OpenTelemetry Collector](#4.4).

**Sources:** [deploy/helm/nvca-operator/nvca-operator/values.yaml:37-47](), [deploy/helm/nvca-operator/nvca-operator/templates/deployment.yaml:151-162]()

---

## 4.5 Container Cache, Image Credential Helper, and NvSnap

These services optimize workload startup times and provide secure access to private registries.

*   **Container Cache:** An Nginx-based OCI proxy that caches images from registries like NGC and HuggingFace to reduce external bandwidth and speed up pod scheduling.
*   **Image Credential Helper:** A Kubernetes credential provider that handles authentication for private registries automatically [deploy/helm/nvca-operator/nvca-operator/templates/_helpers.tpl:130-142]().
*   **NvSnap:** Provides GPU checkpoint/restore capabilities using CRIU, enabling "warm starts" for models with massive memory footprints.

For details, see [Container Cache, Image Credential Helper, and NvSnap](#4.5).

**Sources:** [deploy/helm/nvca-operator/nvca-operator/templates/_helpers.tpl:130-142]()

---

## Code Entity Mapping

| System Name | Code Entity / CRD | Primary Configuration |
| :--- | :--- | :--- |
| **NVCA Operator** | `nvca-operator` | [deploy/helm/nvca-operator/nvca-operator/values.yaml]() |
| **Cluster Agent** | `nvca` | `agentConfig.mergeConfig` |
| **Registration State** | `NVCFBackend` | `systemNamespace` [deploy/helm/nvca-operator/nvca-operator/values.yaml:69]() |
| **Helm Workload** | `MiniService` | `featureGateValues` [deploy/stacks/nvcf-compute-plane/helmfile.d/02-nvca.yaml.gotmpl:31]() |
| **Credential Helper** | `nvcf-image-credential-helper` | [deploy/helm/nvca-operator/nvca-operator/templates/_helpers.tpl:138]() |
| **OTel Sidecar** | `nvcf-otel-collector` | [deploy/helm/nvca-operator/nvca-operator/templates/_helpers.tpl:153]() |

**Sources:** [deploy/helm/nvca-operator/nvca-operator/values.yaml:20-69](), [deploy/stacks/nvcf-compute-plane/helmfile.d/02-nvca.yaml.gotmpl:31-55](), [deploy/helm/nvca-operator/nvca-operator/templates/_helpers.tpl:130-157]()

---

