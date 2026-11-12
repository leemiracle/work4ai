<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cluster-readiness-engine · page 9 Documentation and Design Records · fetched 2026-10-26 -->

# Documentation and Design Records

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/designs/000-adr.md](docs/designs/000-adr.md)
- [docs/designs/027-kustomize-override-ux.md](docs/designs/027-kustomize-override-ux.md)
- [docs/designs/031-platform-aware-nccl-config.md](docs/designs/031-platform-aware-nccl-config.md)
- [docs/designs/073-setup-retry-convergence.md](docs/designs/073-setup-retry-convergence.md)
- [docs/designs/079-workload-object-labels.md](docs/designs/079-workload-object-labels.md)
- [docs/designs/README.md](docs/designs/README.md)
- [fern/docs.yml](fern/docs.yml)
- [fern/versions/v0.3.0.yml](fern/versions/v0.3.0.yml)
- [fern/versions/v0.4.0.yml](fern/versions/v0.4.0.yml)
- [fern/versions/v0.5.0.yml](fern/versions/v0.5.0.yml)

</details>



## Purpose and Scope

This page provides a high-level overview of the documentation structure, Architecture Decision Records (ADRs), project governance, and the Fern-based publishing pipeline for the NVIDIA Cluster Readiness Engine (NVCRE) codebase. NVCRE maintains a strict design-first engineering culture: significant architectural and feature changes are preceded by numbered ADRs in `docs/designs/`, and user-facing documentation is automatically built, versioned, and published via Fern configuration pipelines.

For deep technical details, see the child pages:
- [Architecture Decision Records](#9.1)
- [Fern Docs Site Pipeline](#9.2)
- [Project Governance and Contributor Process](#9.3)

---

## Architecture Decision Records (ADRs) Overview

NVCRE uses Architecture Decision Records to capture the context, constraints, implementation details, and trade-offs for all system features before code is written [docs/designs/README.md:1-9]. ADRs are organized numerically in the `docs/designs/` directory [docs/designs/README.md:10-18].

```mermaid
graph TD
    A[""docs/designs/README.md""] --> B[""ADR-000: Architecture""]
    A --> C[""ADR-027: Kustomize UX""]
    A --> D[""ADR-031: NCCL Config""]
    A --> E[""ADR-073: Setup Retry""]
    A --> F[""ADR-079: Workload Labels""]
    
    C --> G["pkg/controller/workflow_controller.go"]
    D --> H["pkg/catalog/entries/"]
    E --> I["pkg/setup/setup.go"]
    F --> J["api/v1alpha1/job_types.go"]

    subclassDef default stroke:#000,fill:#fff;
```
*Figure 1: ADR Lifecycle Mapping to Code Entities*

Sources: `docs/designs/README.md:1-45`, `docs/designs/073-setup-retry-convergence.md:1-20`, `docs/designs/079-workload-object-labels.md:1-40`

### Notable ADRs
- **ADR-027**: Introduces Kustomize-like override UX, standardizing strategic merge patches using `k8s.io/apimachinery/pkg/util/strategicpatch` and RFC 6902 JSON patches [docs/designs/027-kustomize-override-ux.md:25-50].
- **ADR-031**: Establishes platform-aware NCCL communication configurations and environment variable forwarding via MPI `-x` flags [docs/designs/031-platform-aware-nccl-config.md:15-30].
- **ADR-073**: Specifies convergent retry mechanics for `nvcrectl setup init` when encountering partial Kubeflow Trainer installs and cert ownership conflicts [docs/designs/073-setup-retry-convergence.md:1-25].
- **ADR-079**: Adds declarative workload metadata (`workloadMetadata`) to `JobSpec`, `WorkloadRunSpec`, and `CategoryOptions` for integration with schedulers like Kueue [docs/designs/079-workload-object-labels.md:65-90].

For comprehensive descriptions of ADR numbering, templates, and implementation mappings, see [Architecture Decision Records](#9.1).

Sources: `docs/designs/README.md:1-45`, `docs/designs/027-kustomize-override-ux.md:1-55`, `docs/designs/031-platform-aware-nccl-config.md:1-45`, `docs/designs/073-setup-retry-convergence.md:1-37`, `docs/designs/079-workload-object-labels.md:1-100`

---

## Fern Documentation Site Pipeline

The user documentation site is governed by Fern configurations located in the `fern/` directory [fern/docs.yml:1-38]. The site pipeline handles multi-source aggregation, versioned navigation trees, and automated publication to documentation endpoints [fern/docs.yml:6-10].

```mermaid
graph TD
    A[""fern/docs.yml""] --> B[""fern/versions/v0.5.0.yml""]
    A --> C[""fern/versions/v0.4.0.yml""]
    A --> D[""fern/versions/v0.3.0.yml""]
    
    B --> E[""docs/index.yml""]
    C --> E
    D --> E

    subclassDef default stroke:#000,fill:#fff;
```
*Figure 2: Fern Documentation Navigation and Versioning Pipeline*

Sources: `fern/docs.yml:1-38`, `fern/versions/v0.5.0.yml:1-35`

### Key Configuration Elements
- **Global Settings**: Configured in `fern/docs.yml`, defining the documentation domain, global themes, and repository links [fern/docs.yml:1-20].
- **Versioned Navigation**: Individual version manifests under `fern/versions/` (e.g., `v0.5.0.yml`) map documentation pages across sections like Getting Started, Concepts, How-to Guides, CLI Reference, and API Reference [fern/versions/v0.5.0.yml:1-105].

For details on CI preview workflows, version freezing scripts, and link verification gates, see [Fern Docs Site Pipeline](#9.2).

Sources: `fern/docs.yml:1-38`, `fern/versions/v0.5.0.yml:1-35`, `fern/versions/v0.4.0.yml:1-35`, `fern/versions/v0.3.0.yml:1-35`

---

## Project Governance and Contributor Process

NVCRE maintains clear rules for code contributions, ownership, and automated agent assistance:
- **Governance & Ownership**: Defined via `CODEOWNERS`, `MAINTAINERS`, and repository governance policies.
- **Developer Certificate of Origin (DCO)**: Mandatory sign-off on all commits.
- **Automated Reviews**: Configured via CodeRabbit integration and validation scripts.
- **Agent Workflows**: Supported by `.claude` skills and documentation pointers in `CLAUDE.md`.

For details on PR templates, review requirements, and contribution guidelines, see [Project Governance and Contributor Process](#9.3).

Sources: `docs/designs/README.md:1-10`

---

