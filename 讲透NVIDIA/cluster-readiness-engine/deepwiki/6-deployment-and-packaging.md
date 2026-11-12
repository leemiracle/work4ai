<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cluster-readiness-engine · page 6 Deployment and Packaging · fetched 2026-10-26 -->

# Deployment and Packaging

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/docs-verify.yml](.github/workflows/docs-verify.yml)
- [.golangci.yml](.golangci.yml)
- [Dockerfile](Dockerfile)
- [docs/index.yml](docs/index.yml)
- [docs/operations/deployment.md](docs/operations/deployment.md)
- [go.mod](go.mod)
- [go.sum](go.sum)
- [helm/cluster-readiness-engine/templates/deployment.yaml](helm/cluster-readiness-engine/templates/deployment.yaml)
- [helm/cluster-readiness-engine/templates/metrics-monitor.yaml](helm/cluster-readiness-engine/templates/metrics-monitor.yaml)
- [helm/cluster-readiness-engine/templates/pdb.yaml](helm/cluster-readiness-engine/templates/pdb.yaml)
- [helm/cluster-readiness-engine/values.yaml](helm/cluster-readiness-engine/values.yaml)
- [test/helm/pdb_test.go](test/helm/pdb_test.go)
- [test/helm/render_test.go](test/helm/render_test.go)

</details>



## Purpose and Scope
This page provides a high-level overview of how the NVIDIA Cluster Readiness Engine (NVCRE) is packaged, distributed, and deployed into Kubernetes clusters. NVCRE uses a multi-stage distroless container image and a Helm chart to provision the core controller manager, Custom Resource Definitions (CRDs), role-based access control (RBAC), PodDisruptionBudgets (PDBs), and monitoring endpoints.

For deeper technical details, refer to the child pages:
- [Helm Chart](#6.1) — Detailed coverage of `helm/cluster-readiness-engine` templates, configuration values, RBAC, PDBs, ServiceMonitors, and chart render tests.
- [Container Image and Build](#6.2) — Detailed coverage of the multi-stage distroless `Dockerfile`, `Makefile` build targets, version stamping, and dependency management policies.

Sources:
- `Dockerfile:1-38`
- `docs/operations/deployment.md:1-48`
- `helm/cluster-readiness-engine/values.yaml:1-52`

---

## Deployment Architecture and Component Overview

The deployment pipeline packages the manager binary into a secure, minimal container image and provisions it via a Helm chart or the `nvcrectl setup init` command. The deployment configures leader election, resource requests and limits, anti-affinity rules, and monitoring hooks.

```mermaid
graph TD
    sub0["Source Code & Go Modules"] -->| "Makefile / Dockerfile" | sub1["Container Image: manager"]
    sub2["Helm Chart Templates"] -->| "helm/cluster-readiness-engine" | sub3["Kubernetes Cluster Objects"]
    sub1 --> sub3
    sub3 --> sub4["Deployment: manager"]
    sub3 --> sub5["ServiceMonitor: metrics-monitor"]
    sub3 --> sub6["PodDisruptionBudget: pdb"]

    classDef default stroke:#000,fill:#fff;
```
*Figure 1: NVCRE deployment and packaging artifact pipeline.*

Sources:
- `Dockerfile:1-38`
- `helm/cluster-readiness-engine/templates/deployment.yaml:1-99`
- `helm/cluster-readiness-engine/templates/metrics-monitor.yaml:1-27`
- `helm/cluster-readiness-engine/templates/pdb.yaml:1-18`

---

## 6.1 Helm Chart

The NVCRE Helm chart (`helm/cluster-readiness-engine`) manages the deployment lifecycle of the controller. It provisions the core Kubernetes `Deployment` (`helm/cluster-readiness-engine/templates/deployment.yaml`), RBAC permissions, optional `PodDisruptionBudget` (`helm/cluster-readiness-engine/templates/pdb.yaml`), and `ServiceMonitor` resources (`helm/cluster-readiness-engine/templates/metrics-monitor.yaml`).

Values in `helm/cluster-readiness-engine/values.yaml` control resource sizing, replica counts, concurrent reconciler limits, and container image references. Digest-based image pinning (`manager.image.digest`) is supported to ensure exact byte verification in production environments, taking precedence over mutable tags. Automated chart rendering and validation tests are implemented in Go (`test/helm/render_test.go` and `test/helm/pdb_test.go`).

For comprehensive information on template options, values, CRD lifecycle management, and test suites, see [Helm Chart](#6.1).

Sources:
- `helm/cluster-readiness-engine/values.yaml:1-52`
- `helm/cluster-readiness-engine/templates/deployment.yaml:1-99`
- `helm/cluster-readiness-engine/templates/pdb.yaml:1-18`
- `helm/cluster-readiness-engine/templates/metrics-monitor.yaml:1-27`
- `test/helm/render_test.go:32-64`
- `test/helm/pdb_test.go:20-57`

---

## 6.2 Container Image and Build

NVCRE builds its manager binary using a multi-stage `Dockerfile`. The builder stage utilizes a pinned Golang image (`public.ecr.aws/docker/library/golang:1.27.1-trixie`) to compile the source code with stripped debug symbols and injected version flags (`-ldflags "-s -w -X main.version=${VERSION}"`). 

The runtime environment is packaged on a secure distroless static base image (`nvcr.io/nvidia/distroless/static`) running under a non-root security context (`USER 65532:65532`) with a read-only root filesystem and dropped capabilities. Go module dependencies and container base image digests are tracked and updated via Dependabot policies.

For details on build targets, multi-architecture buildx configurations, and version stamping, see [Container Image and Build](#6.2).

```mermaid
graph TD
    sub0["Golang Builder Stage: Dockerfile"] -->| "go build -ldflags" | sub1["Compiled Binary: manager"]
    sub1 --> sub2["Distroless Runtime: nvcr.io/nvidia/distroless/static"]
    sub2 --> sub3["Final Container Image: ghcr.io/nvidia/cluster-readiness-engine/manager"]

    classDef default stroke:#000,fill:#fff;
```
*Figure 2: Container image multi-stage build flow.*

Sources:
- `Dockerfile:1-38`
- `go.mod:1-21`

---

