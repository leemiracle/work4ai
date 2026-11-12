<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cluster-readiness-engine · page 2 API and Custom Resources · fetched 2026-10-26 -->

# API and Custom Resources

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/v1alpha1/certification_types.go](api/v1alpha1/certification_types.go)
- [api/v1alpha1/workflow_types.go](api/v1alpha1/workflow_types.go)
- [cmd/integration/testdata/validation/certification-maxbytes-documented-value/expected.json](cmd/integration/testdata/validation/certification-maxbytes-documented-value/expected.json)
- [cmd/integration/testdata/validation/certification-maxbytes-documented-value/input.yaml](cmd/integration/testdata/validation/certification-maxbytes-documented-value/input.yaml)
- [cmd/integration/testdata/validation/certification-maxbytes-invalid-unit/expected.json](cmd/integration/testdata/validation/certification-maxbytes-invalid-unit/expected.json)
- [cmd/integration/testdata/validation/certification-maxbytes-invalid-unit/input.yaml](cmd/integration/testdata/validation/certification-maxbytes-invalid-unit/input.yaml)
- [cmd/integration/testdata/validation/certification-maxbytes-spec-level/expected.json](cmd/integration/testdata/validation/certification-maxbytes-spec-level/expected.json)
- [cmd/integration/testdata/validation/certification-maxbytes-spec-level/input.yaml](cmd/integration/testdata/validation/certification-maxbytes-spec-level/input.yaml)
- [cmd/integration/validation_test.go](cmd/integration/validation_test.go)
- [helm/cluster-readiness-engine/crds/nvcre.nvidia.com_certifications.yaml](helm/cluster-readiness-engine/crds/nvcre.nvidia.com_certifications.yaml)
- [helm/cluster-readiness-engine/crds/nvcre.nvidia.com_workflows.yaml](helm/cluster-readiness-engine/crds/nvcre.nvidia.com_workflows.yaml)
- [helm/cluster-readiness-engine/crds/nvcre.nvidia.com_workloadruns.yaml](helm/cluster-readiness-engine/crds/nvcre.nvidia.com_workloadruns.yaml)

</details>



The `nvcre.nvidia.com` API group (`api/v1alpha1`) and its generated Custom Resource Definitions (CRDs) define the core domain objects for the NVIDIA Cluster Readiness Engine (NVCRE) [api/v1alpha1/certification_types.go:1-12](). These resources orchestrate GPU cluster validation, run distributed training and communication workloads, evaluate performance goodput and bandwidth metrics, and manage hardware fault isolation. 

The API design separates high-level user intent—expressed through `Certification` and `WorkloadRun`—from low-level execution machinery handled by `Workflow` and `Job` CRDs. All primary specs are immutable after creation to maintain deterministic reconciliation boundaries [helm/cluster-readiness-engine/crds/nvcre.nvidia.com_certifications.yaml:39-45]().

```mermaid
graph TD
    sub5[""API Group: nvcre.nvidia.com v1alpha1""]
    sub5 --> node1[""Certification Struct [api/v1alpha1/certification_types.go]""]
    sub5 --> node2[""WorkloadRun Struct [helm/cluster-readiness-engine/crds/nvcre.nvidia.com_workloadruns.yaml]""]
    sub5 --> node3[""Workflow Struct [api/v1alpha1/workflow_types.go]""]
    sub5 --> node4[""GoodputMeasurement & BandwidthMeasurement""]
    
    node1 -->|Generates| node3
    node2 -->|Generates| node3
    node3 -->|Creates| node6[""Job Custom Resources""]
```
*Sources: `api/v1alpha1/certification_types.go:1-12`, `helm/cluster-readiness-engine/crds/nvcre.nvidia.com_certifications.yaml:39-45`, `api/v1alpha1/workflow_types.go:1-30`*

## High-Level Architecture and Child Resources

The API surface spans user-facing intent wrappers, execution coordinators, and telemetry monitors. For detailed specifications, validation rules, and immutability guarantees, refer to the following child pages:

- **Certification and WorkloadRun Types** ([Certification and WorkloadRun Types](#2.1)) — Covers `Certification` targets, category matrices, orchestration options, taint selectors, and the simplified `WorkloadRun` API.
- **Workflow and Job Types** ([Workflow and Job Types](#2.2)) — Covers `Workflow` specifications, node groups, iterations, dependency management, overrides, and discriminated `Job` specs.
- **Measurement and LogProfile Types** ([Measurement and LogProfile Types](#2.3)) — Covers `GoodputMeasurement`, `BandwidthMeasurement`, and cluster-scoped `LogProfile` CRDs for threshold evaluations and regex log parsing.

```mermaid
graph LR
    sub6[""User Input Space""] -->|"Submits"| sub7[""Controller Reconciliation Space""]
    sub7 -->|"Validates via CEL"| sub8[""API Server Admission [cmd/integration/validation_test.go]""]
    sub8 -->|"Persists"| sub9[""CRD Schemas [helm/cluster-readiness-engine/crds/]""]
```
*Sources: `cmd/integration/validation_test.go:33-52`, `helm/cluster-readiness-engine/crds/nvcre.nvidia.com_certifications.yaml:1-25`*

---
*Sources: `api/v1alpha1/certification_types.go:1-12`, `helm/cluster-readiness-engine/crds/nvcre.nvidia.com_certifications.yaml:39-45`, `api/v1alpha1/workflow_types.go:1-30`, `cmd/integration/validation_test.go:33-52`*

---

