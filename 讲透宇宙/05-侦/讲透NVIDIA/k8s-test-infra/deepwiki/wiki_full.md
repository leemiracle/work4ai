# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/nvml-mock-e2e-go.yaml](.github/workflows/nvml-mock-e2e-go.yaml)
- [Makefile](Makefile)
- [README.md](README.md)
- [docs/README.md](docs/README.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/demo/kind.yaml](docs/demo/kind.yaml)
- [docs/demo/with-fgo/README.md](docs/demo/with-fgo/README.md)
- [docs/examples.md](docs/examples.md)
- [docs/img/logo-title.png](docs/img/logo-title.png)
- [docs/img/logo.png](docs/img/logo.png)
- [docs/integrations/fake-gpu-operator.md](docs/integrations/fake-gpu-operator.md)
- [docs/quickstart.md](docs/quickstart.md)
- [tests/e2e/README.md](tests/e2e/README.md)
- [tests/e2e/go/e2e_suite_test.go](tests/e2e/go/e2e_suite_test.go)
- [tests/e2e/go/framework/config/config.go](tests/e2e/go/framework/config/config.go)
- [tests/e2e/go/framework/harness/harness.go](tests/e2e/go/framework/harness/harness.go)
- [tests/e2e/go/suite_cluster.go](tests/e2e/go/suite_cluster.go)
- [tests/e2e/go/suite_helm.go](tests/e2e/go/suite_helm.go)

</details>



## Purpose and Scope

The `k8s-test-infra` repository provides testing infrastructure for Kubernetes environments with specialized support for NVIDIA GPU simulation, Node Feature Discovery (NFD), and Dynamic Resource Allocation (DRA). The core of this repository is `nvml-mock`, a system designed to simulate NVIDIA GPUs on CPU nodes, enabling comprehensive testing of GPU-aware Kubernetes components without physical hardware [README.md:18-20](). This includes testing the NVIDIA Device Plugin, NVIDIA DRA Driver, and NVIDIA GPU Operator [README.md:41-44]().

This page provides a high-level overview of the repository's purpose, core components, and architectural patterns, with a focus on the `nvml-mock` system. For detailed information on specific subsystems, refer to:
- The `nvml-mock` GPU simulation system: [nvml-mock System](#9)
- Build process and development workflow: [Getting Started](#2)
- Testing patterns and practices: [Testing with Ginkgo](#5)
- Kubernetes API integration: [Kubernetes APIs and Integration](#6)
- CI/CD automation: [CI/CD Pipeline](#4)

## Repository Structure

The repository is organized around several key components that work together to provide Kubernetes testing capabilities, primarily centered around the `nvml-mock` system:

```mermaid
graph TB
    subgraph "Core Simulation"
        NVMLMOCK["nvml-mock<br/>(libnvidia-ml.so)"]
        MOCKCUDA["Mock CUDA<br/>(libcuda.so)"]
        NVIDIASMI["nvidia-smi<br/>(Real binary with RPATH patch)"]
    end

    subgraph "Kubernetes Deployment & Integration"
        HELMCHART["Helm Chart<br/>(deployments/nvml-mock/helm/nvml-mock)"]
        CDIINJECTION["CDI Injection<br/>(Container Device Interface)"]
        NRIPLUGIN["NRI Plugin<br/>(nvml-mock-nri)"]
        NFDAPI["NFD API<br/>(Node Feature Discovery)"]
        DRAAPI["DRA API<br/>(Dynamic Resource Allocation)"]
    end

    subgraph "Testing Framework"
        E2EHARNESS["E2E Harness<br/>(tests/e2e/go)"]
        GINKGO["Ginkgo/Gomega<br/>(BDD Testing)"]
    end

    subgraph "Utilities & Integrations"
        MOCKCTL["nvml-mock-ctl<br/>(Runtime Control CLI)"]
        FGOINTEGRATION["fake-gpu-operator Integration"]
    end

    NVMLMOCK --> NVIDIASMI
    NVMLMOCK --> MOCKCUDA
    HELMCHART --> NVMLMOCK
    HELMCHART --> CDIINJECTION
    HELMCHART --> NRIPLUGIN
    E2EHARNESS --> NVMLMOCK
    E2EHARNESS --> HELMCHART
    E2EHARNESS --> GINKGO
    E2EHARNESS --> NFDAPI
    E2EHARNESS --> DRAAPI
    MOCKCTL --> NVMLMOCK
    FGOINTEGRATION --> NVMLMOCK
    FGOINTEGRATION --> HELMCHART

    style NVMLMOCK fill:#f9f9f9,stroke:#333,stroke-width:2px
    style HELMCHART fill:#f9f9f9,stroke:#333,stroke-width:2px
    style E2EHARNESS fill:#f9f9f9,stroke:#333,stroke-width:2px
```
Sources: [README.md:21-22, 48-62, 68-70, 86-89, 91-94](), [docs/README.md:10-15]()

## Core Components

### nvml-mock: GPU Simulation System

The central component of this repository is `nvml-mock`, a system that simulates NVIDIA GPUs on CPU nodes. It provides a mock `libnvidia-ml.so` library that intercepts NVML API calls, allowing applications like `nvidia-smi` and GPU-aware Kubernetes components to function without actual NVIDIA hardware [README.md:68-69](), [docs/README.md:10]()

Key features of `nvml-mock` include:
- **Mock NVML Library**: Implements over 400 NVML C API exports, with 111 configurable behaviors and 289 stubs [docs/README.md:10]().
- **Mock CUDA Library**: Provides early support for 15 CUDA functions related to initialization, device management, and memory [docs/README.md:11]().
- **`nvidia-smi` Integration**: Uses the real `nvidia-smi` binary with an RPATH patch, backed by the mock NVML library, to produce realistic output [docs/README.md:12]().
- **YAML Configuration**: GPU profiles are defined in YAML files, allowing for flexible simulation of various NVIDIA GPU architectures and configurations [docs/README.md:10]().
- **GPU Profiles**: Supports a range of GPU profiles including `a100`, `h100`, `b200`, `gb200`, `gb300`, `l40s`, and `t4`, each with specific VRAM and architecture characteristics [docs/README.md:17-26]().
- **Runtime Control**: The `nvml-mock-ctl` CLI tool allows dynamic modification of simulated GPU state on a running node [docs/README.md:44]().

Example usage of `nvml-mock` with `nvidia-smi`:
```bash
LD_LIBRARY_PATH=. MOCK_NVML_CONFIG=configs/mock-nvml-config-a100.yaml nvidia-smi
```
This command runs `nvidia-smi` using the mock library configured with an A100 GPU profile [docs/examples.md:18-19]().

Sources: [README.md:18-20, 68-70](), [docs/README.md:10-26, 44](), [docs/examples.md:18-19]()

### Kubernetes Integration

`nvml-mock` is designed for seamless integration with Kubernetes:
- **Helm Chart Deployment**: Deployed as a DaemonSet via a Helm chart, enabling easy installation and management within a Kubernetes cluster [README.md:35](), [docs/README.md:13]().
- **CDI Injection**: Supports Container Device Interface (CDI) specifications for integration with the GPU Operator [docs/README.md:14]().
- **NRI Plugin**: The `nvml-mock-nri` containerd NRI plugin enables node-wide ambient GPU injection into ordinary pods without requiring explicit GPU requests or hostPath mounts [README.md:61]().
- **Node Feature Discovery (NFD)**: `nvml-mock` can write NFD feature files, triggering node labeling based on simulated hardware features [README.md:62]().
- **Dynamic Resource Allocation (DRA)**: Integrates with the DRA driver to publish simulated GPU resources as `ResourceSlice` objects, enabling DRA-based scheduling [README.md:58]().

Sources: [README.md:35, 58, 61-62](), [docs/README.md:13-14]()

### E2E Testing Framework

The repository includes a comprehensive end-to-end (E2E) testing framework built on Go, Ginkgo, and Gomega [README.md:48-50](). This harness manages the full lifecycle of test scenarios:
1.  **Cluster Creation**: Creates a multi-node Kind cluster [tests/e2e/README.md:17]().
2.  **Image Management**: Builds and loads the `nvml-mock` Docker image into Kind [tests/e2e/README.md:16, 18]().
3.  **Helm Deployment**: Installs `nvml-mock` into a dedicated namespace [tests/e2e/README.md:19]().
4.  **Validation**: Runs various checks for each selected GPU profile [tests/e2e/README.md:20]().
5.  **Diagnostics**: Collects logs and cluster state on failure [tests/e2e/README.md:21]().
6.  **Teardown**: Optionally deletes the Kind cluster [tests/e2e/README.md:22]().

The E2E tests cover various scenarios:
- **Standalone Demo**: Validates `nvml-mock` chart installation, `nvidia-smi` output, NVLink/fabricmanager, InfiniBand, PCI sysfs, and cross-node checks [README.md:55]().
- **Failure Injection**: Tests healthy, ECC, lost, and fallen-off-bus GPU modes [README.md:56]().
- **DRA Driver**: Validates mock driver files, `nvidia-smi`, `ResourceSlices`, and DRA `ResourceClaim` scheduling [README.md:57-58]().
- **GPU Operator**: Verifies GPU Operator installation, validator pod startup, GFD labels, and allocatable GPUs [README.md:59]().
- **Multi-Node Fleet**: Tests heterogeneous A100/T4 workers, mock files, InfiniBand behavior, device plugin resources, and GPU workload scheduling [README.md:60]().
- **Node-Wide NRI Injection**: Validates ambient mock GPU injection into ordinary pods [README.md:61]().
- **NFD Label Provenance**: Ensures NFD creates `feature.node.kubernetes.io/pci-10de.present` labels from `nvml-mock`'s feature files [README.md:62]().

The `Makefile` provides targets for running these E2E scenarios, such as `make e2e`, `make e2e-dra`, `make e2e-gpu-operator`, `make e2e-multi-node`, `make e2e-nri`, and `make e2e-nfd` [Makefile:152-156]().

Sources: [README.md:48-62](), [tests/e2e/README.md:14-22](), [Makefile:152-156]()

### Integrations

The repository supports integration with other GPU simulation and management tools:
- **fake-gpu-operator (FGO)**: `nvml-mock` can integrate with Run:ai's `fake-gpu-operator` to enable mixed clusters where `nvml-mock` provides driver-level fidelity on a few "real" nodes, while FGO handles API-level scale simulation on many "fake" nodes [README.md:88](), [docs/integrations/fake-gpu-operator.md:5-10](). This allows for comprehensive testing combining driver fidelity with large-scale Kubernetes API simulation [docs/integrations/fake-gpu-operator.md:13-23]().

Sources: [README.md:88](), [docs/integrations/fake-gpu-operator.md:5-10, 13-23]()

## Repository Structure (Code Entity View)

The following diagram illustrates the relationship between key system names and their corresponding code entities within the repository.

```mermaid
graph TD
    subgraph "k8s-test-infra"
        A[".github/workflows/nvml-mock-e2e-go.yaml"] --> B["make e2e<br/>(Makefile)"]
        B --> C["tests/e2e/go/e2e_suite_test.go"]
        C --> D["harness.Harness<br/>(tests/e2e/go/framework/harness/harness.go)"]
        D --> E["config.SelectedProfileNames()<br/>(tests/e2e/go/framework/config/config.go)"]
        D --> F["installDemoChart()<br/>(tests/e2e/go/suite_helm.go)"]
        D --> G["setupCluster()<br/>(tests/e2e/go/suite_cluster.go)"]
        F --> H["helm.Release<br/>(tests/e2e/go/framework/helm/helm.go)"]
        H --> I["deployments/nvml-mock/helm/nvml-mock"]
        I --> J["deployments/nvml-mock/helm/nvml-mock/profiles"]
        J --> K["nvml-mock-config-<profile>.yaml"]
        K --> L["pkg/gpu/mocknvml<br/>(libnvidia-ml.so)"]
        L --> M["nvidia-smi"]
        G --> N["kind create cluster"]
        N --> O["local/kind/<profile>.kind.yaml"]
        O --> P["kind-node-nv:latest"]
        P --> Q["local/kind/Dockerfile"]
        F --> R["config.Image()<br/>(tests/e2e/go/framework/config/config.go)"]
        R --> S["deployments/nvml-mock/Dockerfile"]
        D --> T["diagnostics.New()<br/>(tests/e2e/go/framework/diagnostics/diagnostics.go)"]
        T --> U["config.ArtifactsDir()<br/>(tests/e2e/go/framework/config/config.go)"]
    end

    subgraph "External Tools"
        KIND["kind"]
        HELM["helm"]
        DOCKER["docker"]
        KUBECTL["kubectl"]
    end

    N --> KIND
    H --> HELM
    S --> DOCKER
    Q --> DOCKER
    D --> KUBECTL

    style A fill:#e0f2f7,stroke:#333,stroke-width:1px
    style B fill:#e0f2f7,stroke:#333,stroke-width:1px
    style C fill:#e0f2f7,stroke:#333,stroke-width:1px
    style D fill:#e0f2f7,stroke:#333,stroke-width:1px
    style E fill:#e0f2f7,stroke:#333,stroke-width:1px
    style F fill:#e0f2f7,stroke:#333,stroke-width:1px
    style G fill:#e0f2f7,stroke:#333,stroke-width:1px
    style H fill:#e0f2f7,stroke:#333,stroke-width:1px
    style I fill:#e0f2f7,stroke:#333,stroke-width:1px
    style J fill:#e0f2f7,stroke:#333,stroke-width:1px
    style K fill:#e0f2f7,stroke:#333,stroke-width:1px
    style L fill:#e0f2f7,stroke:#333,stroke-width:1px
    style M fill:#e0f2f7,stroke:#333,stroke-width:1px
    style N fill:#e0f2f7,stroke:#333,stroke-width:1px
    style O fill:#e0f2f7,stroke:#333,stroke-width:1px
    style P fill:#e0f2f7,stroke:#333,stroke-width:1px
    style Q fill:#e0f2f7,stroke:#333,stroke-width:1px
    style R fill:#e0f2f7,stroke:#333,stroke-width:1px
    style S fill:#e0f2f7,stroke:#333,stroke-width:1px
    style T fill:#e0f2f7,stroke:#333,stroke-width:1px
    style U fill:#e0f2f7,stroke:#333,stroke-width:1px
```
Sources: [Makefile:136, 139, 141, 146, 166](), [tests/e2e/go/suite_helm.go:36-45, 48-78](), [tests/e2e/go/suite_cluster.go:60-77](), [tests/e2e/go/framework/config/config.go:58-78, 81-82, 115](), [deployments/nvml-mock/Dockerfile](), [local/kind/Dockerfile](), [local/kind/default.kind.yaml](), [docs/demo/kind.yaml](), [docs/README.md:12]()

## Module Dependency Graph

The repository is structured as a single Go module with carefully curated dependencies. The `go.mod` file specifies the Go version as `1.25.0` [go.mod:3]().

```mermaid
graph TD
    ROOT["github.com/NVIDIA/k8s-test-infra<br/>(Go 1.25.0)"]
    
    subgraph "Testing Frameworks"
        GINKGO["github.com/onsi/ginkgo/v2<br/>v2.27.2"]
        GOMEGA["github.com/onsi/gomega<br/>v1.38.2"]
    end
    
    subgraph "Kubernetes Client Libraries"
        CLIENTGO["k8s.io/client-go<br/>v0.34.2"]
        API["k8s.io/api<br/>v0.34.2"]
        APIMACH["k8s.io/apimachinery<br/>v0.34.2"]
        APIEXT["k8s.io/apiextensions-apiserver<br/>v0.34.2"]
    end
    
    subgraph "NFD & DRA"
        NFD["sigs.k8s.io/node-feature-discovery<br/>v0.18.3"]
        NFDAPI["sigs.k8s.io/node-feature-discovery/api/nfd<br/>v0.18.3"]
        K8SRESOURCEAPI["k8s.io/api/resource<br/>v0.34.2"]
    end
    
    subgraph "Logging & Utilities"
        KLOG["k8s.io/klog/v2<br/>v2.130.1"]
        YAMLUTIL["sigs.k8s.io/yaml<br/>v1.6.0"]
    end
    
    ROOT --> GINKGO
    ROOT --> GOMEGA
    ROOT --> CLIENTGO
    ROOT --> NFD
    ROOT --> NFDAPI
    ROOT --> KLOG
    ROOT --> YAMLUTIL
    
    CLIENTGO --> API
    CLIENTGO --> APIMACH
    CLIENTGO --> APIEXT
    API --> K8SRESOURCEAPI

    style ROOT fill:#f9f9f9
```
Sources: [go.mod:1-61]()

## Vendoring Strategy

The repository uses Go module vendoring to ensure reproducible builds. All dependencies are stored in the `vendor/` directory, and the build system enforces that vendored dependencies remain synchronized with `go.mod` and `go.sum` through automated checks [Makefile:48-50, 78-82]().

The vendoring approach provides:
-   **Build Reproducibility**: Identical builds regardless of network availability or upstream changes.
-   **Security**: Fixed dependency versions that have been reviewed.
-   **Offline Development**: No network required for builds once dependencies are vendored.

Sources: [Makefile:48-50, 78-82]()

## Key Utilities

### Certificate Generation

The repository leverages `k8s.io/client-go/util/cert` for generating self-signed certificates and certificate authorities. This is essential for testing secure Kubernetes components that require TLS.
-   `NewSelfSignedCACert`: Creates a certificate authority.
-   `GenerateSelfSignedCertKey`: Creates host certificates with subject alternative names.
-   Support for both IP addresses and DNS names in certificates.

Sources: [vendor/k8s.io/client-go/util/cert/cert.go:1-277]()

### YAML/JSON Manifest Processing

The `k8s.io/apimachinery/pkg/util/yaml` package provides sophisticated YAML and JSON decoding capabilities:
-   **YAMLOrJSONDecoder**: Automatically detects and decodes both YAML and JSON formats.
-   **YAMLToJSONDecoder**: Converts YAML documents to JSON for processing.
-   **Multi-document streams**: Handles YAML files with multiple documents separated by `---`.

These utilities enable tests to load Kubernetes manifests from files and apply them to test clusters.

Sources: [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:1-486]()

### Structured Logging

The repository uses `k8s.io/klog/v2` (v2.130.1) for structured logging, which provides:
-   Compatibility with both traditional klog API and modern structured logging.
-   Integration with `go-logr` and `log/slog`.
-   Verbosity levels for controlling log output.
-   Structured key-value logging for machine-readable output.

Sources: [go.mod:12]()

## Build and Development Environment

The repository requires **Go 1.25.0** as specified in the module declaration [go.mod:3](). Version management is centralized with the Go version defined in build configuration and extracted by CI pipelines [Makefile:17]().

Build artifacts include:
-   **`nv-ci-bot` binary**: The main executable in `bin/nv-ci-bot` [Makefile:31]().
-   **Docker images**: Development, `nvml-mock`, and `kind-nvidia-cdi` images [Makefile:132](), [deployments/nvml-mock/Dockerfile](), [local/kind/Dockerfile]().
-   **Test reports**: JSON and JUnit format test results.

Sources: [go.mod:3](), [Makefile:17, 31, 132](), [deployments/nvml-mock/Dockerfile](), [local/kind/Dockerfile]()

## Project Ownership

The project is maintained by NVIDIA engineers, as defined in the `OWNERS` file:

**Reviewers and Approvers:**
-   ArangoGutierrez
-   kklues
-   elezar

Sources: [OWNERS:1-11]()

## Next Steps

For practical information on working with this repository:
-   **Setting up your development environment**: [Getting Started](#2)
-   **Building the project**: [Building from Source](#2.2)
-   **Writing and running tests**: [Testing with Ginkgo](#5)
-   **Understanding the CI/CD pipeline**: [GitHub Actions Workflows](#4.1)

For deeper architectural understanding:
-   **Module dependencies and vendoring**: [Module Dependencies](#3.1)
-   **Kubernetes client operations**: [Kubernetes Client-Go Operations](#6.1)
-   **NFD and DRA APIs**: [Node Feature Discovery (NFD) API](#6.2) and [Dynamic Resource Allocation (DRA) API](#6.3)

---

# Page: Getting Started

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/nvml-mock-e2e-go.yaml](.github/workflows/nvml-mock-e2e-go.yaml)
- [Makefile](Makefile)
- [README.md](README.md)
- [docs/README.md](docs/README.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/demo/kind.yaml](docs/demo/kind.yaml)
- [docs/demo/with-fgo/README.md](docs/demo/with-fgo/README.md)
- [docs/examples.md](docs/examples.md)
- [docs/integrations/fake-gpu-operator.md](docs/integrations/fake-gpu-operator.md)
- [docs/quickstart.md](docs/quickstart.md)
- [tests/e2e/README.md](tests/e2e/README.md)
- [tests/e2e/go/e2e_suite_test.go](tests/e2e/go/e2e_suite_test.go)
- [tests/e2e/go/framework/config/config.go](tests/e2e/go/framework/config/config.go)
- [tests/e2e/go/framework/harness/harness.go](tests/e2e/go/framework/harness/harness.go)
- [tests/e2e/go/suite_cluster.go](tests/e2e/go/suite_cluster.go)
- [tests/e2e/go/suite_helm.go](tests/e2e/go/suite_helm.go)

</details>



This document provides a quick-start guide for developers who want to set up, build, and run tests in the k8s-test-infra repository. It covers initial environment setup, building the `nvml-mock` shared library and container images, and executing your first test suite.

For detailed information on specific topics, see:
- Prerequisites and tooling setup: [Prerequisites and Environment Setup](#2.1)
- Detailed build process and Makefile targets: [Building from Source](#2.2)
- Test execution and output interpretation: [Running Your First Test](#2.3)
- Comprehensive testing framework documentation: [Testing with Ginkgo](#5)

---

## Quick Start Workflow

The following diagram shows the high-level workflow for getting started with k8s-test-infra:

```mermaid
graph TD
    A[Clone Repository] --> B{Prerequisites Met?};
    B -- Yes --> C[Build nvml-mock Library & Images];
    B -- No --> D[Install Prerequisites];
    D --> B;
    C --> E[Run First Test];
    E --> F[Verify Output];

    subgraph "Key Components"
        A -- "git clone" --> GitRepo["github.com/NVIDIA/k8s-test-infra"]
        D -- "Tools" --> Tools("Go, Docker, kubectl, kind, helm, tilt")
        C -- "Makefile targets" --> BuildTargets("make build, make image-kind-node")
        E -- "Test execution" --> TestMethods("nvidia-smi, make e2e, helm install")
    end

    click GitRepo "https://github.com/NVIDIA/k8s-test-infra"
```

**Sources:** [README.md:16-20](), [README.md:28-36](), [Makefile:141-156](), [Makefile:166-170]()

---

## Prerequisites

Before building or testing k8s-test-infra, ensure your environment has the following tools installed:

| Tool | Purpose | Verification Command |
|------|---------|---------------------|
| Go | Compilation and test execution | `go version` |
| Docker | Container image builds | `docker --version` |
| kubectl | Kubernetes cluster interaction | `kubectl version --client` |
| kind | Local Kubernetes cluster creation | `kind version` |
| helm | Kubernetes package manager | `helm version` |
| tilt | Local development environment | `tilt version` |

The required Go version is specified in the CI workflows, for example, `GO_VERSION: ${{ inputs.golang_version }}` in [`.github/workflows/nvml-mock-e2e-go.yaml:60`]().

For details on installing these tools and configuring your environment, see [Prerequisites and Environment Setup](#2.1).

**Sources:** [tests/e2e/README.md:29-35](), [Makefile:16-17](), [Makefile:166-167](), [`.github/workflows/nvml-mock-e2e-go.yaml:60-66`]()

---

## Cloning the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/NVIDIA/k8s-test-infra.git
cd k8s-test-infra
```

The repository uses vendored dependencies, meaning all external Go modules are stored in the `vendor/` directory for reproducible builds.

**Sources:** [Makefile:44-47]()

---

## Building from Source

The k8s-test-infra project involves building several components: the `nvml-mock` shared library, container images, and Go binaries.

### Build Targets Overview

The `Makefile` provides targets for building various components:

| Target | Description |
|--------|-------------|
| `build` | Builds the `nv-ci-bot` Go binary. |
| `generate` | Runs `go generate` for code generation, specifically for the `nvml-mock` CGo bridge. |
| `image-kind-node` | Builds the custom `kind-node-nv:latest` Docker image, which includes `nvidia-container-toolkit`. |

For a detailed guide on building all components, including local builds, Docker cross-platform builds, and the `generate-bridge` tool, see [Building from Source](#2.2).

**Sources:** [Makefile:30-32](), [Makefile:90-92](), [Makefile:132]()

---

## Running Your First Test

The `k8s-test-infra` repository provides various ways to run tests, from local `nvidia-smi` usage with the mock library to full end-to-end Kubernetes cluster deployments.

### Local `nvidia-smi` with `nvml-mock`

You can test the `nvml-mock` shared library directly with `nvidia-smi` to simulate GPU environments without a Kubernetes cluster.

1.  Build the `nvml-mock` library:
    ```bash
    make -C pkg/gpu/mocknvml
    ```
2.  Run `nvidia-smi` using the mock library:
    ```bash
    LD_LIBRARY_PATH=$(pwd)/pkg/gpu/mocknvml nvidia-smi
    ```
    This will show a default configuration of 8x A100 GPUs. You can specify a different profile using the `MOCK_NVML_CONFIG` environment variable:
    ```bash
    LD_LIBRARY_PATH=$(pwd)/pkg/gpu/mocknvml MOCK_NVML_CONFIG=pkg/gpu/mocknvml/configs/mock-nvml-config-gb200.yaml nvidia-smi
    ```

**Sources:** [docs/examples.md:9-13](), [docs/examples.md:22-25]()

### End-to-End Tests with `make e2e`

The project includes a comprehensive end-to-end (E2E) test suite that deploys `nvml-mock` on a Kind cluster and validates its functionality.

To run the default E2E suite (which uses the `gb200` GPU profile):

```bash
make e2e
```

This command performs the following steps:
1.  Builds the `nvml-mock` Docker image (unless `E2E_SKIP_BUILD=true` is set).
2.  Creates a multi-node Kind cluster.
3.  Loads the `nvml-mock` image into Kind.
4.  Installs `nvml-mock` via Helm into the `mokka` namespace.
5.  Runs standalone demo checks for the selected GPU profile.
6.  Collects diagnostics on failure.

You can specify different GPU profiles or filter tests using environment variables:

```bash
# Run a single explicit profile
make e2e E2E_PROFILES=a100

# Run multiple profiles on the same cluster
make e2e E2E_PROFILES="a100 h100"

# Run only selected use cases with Ginkgo labels
make e2e E2E_GINKGO_FLAGS='--label-filter="nvidia-smi || nvlink"'
```

For a detailed walkthrough of executing test suites, interpreting output, and quick-start Helm deployments, see [Running Your First Test](#2.3).

**Sources:** [tests/e2e/README.md:14-23](), [tests/e2e/README.md:40-50](), [Makefile:141-156]()

---

## Next Steps

Now that you have built the project and run your first test, explore these topics:

- **[Prerequisites and Environment Setup](#2.1)** - Detailed tool installation and Kubernetes cluster setup.
- **[Building from Source](#2.2)** - Deep dive into build process, vendoring, and image creation.
- **[Running Your First Test](#2.3)** - Execute specific test suites and interpret output.
- **[Architecture](#3)** - Understand the overall system design and component interactions.
- **[Testing with Ginkgo](#5)** - Learn the BDD testing framework and patterns used in this project.

**Sources:** [README.md:75-84]()

---

# Page: Prerequisites and Environment Setup

# Prerequisites and Environment Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/code_scanning.yaml](.github/workflows/code_scanning.yaml)
- [.github/workflows/golang.yaml](.github/workflows/golang.yaml)
- [.github/workflows/helm-publish.yaml](.github/workflows/helm-publish.yaml)
- [.github/workflows/helm.yaml](.github/workflows/helm.yaml)
- [.github/workflows/nvml-mock-publish.yaml](.github/workflows/nvml-mock-publish.yaml)
- [.github/workflows/scorecard.yaml](.github/workflows/scorecard.yaml)
- [.github/workflows/variables.yaml](.github/workflows/variables.yaml)
- [deployments/devel/Dockerfile](deployments/devel/Dockerfile)
- [deployments/nvml-mock/Dockerfile](deployments/nvml-mock/Dockerfile)
- [go.mod](go.mod)
- [go.sum](go.sum)
- [pkg/gpu/mockcuda/Makefile](pkg/gpu/mockcuda/Makefile)
- [pkg/gpu/mocknvml/Dockerfile](pkg/gpu/mocknvml/Dockerfile)
- [pkg/gpu/mocknvml/Makefile](pkg/gpu/mocknvml/Makefile)
- [tests/e2e/spike-nvidia-smi.sh](tests/e2e/spike-nvidia-smi.sh)
- [tests/mocknvml/Dockerfile](tests/mocknvml/Dockerfile)
- [tests/poc-validation/setup-kind-cluster.sh](tests/poc-validation/setup-kind-cluster.sh)
- [vendor/github.com/onsi/ginkgo/v2/CHANGELOG.md](vendor/github.com/onsi/ginkgo/v2/CHANGELOG.md)
- [vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go](vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go)
- [vendor/github.com/onsi/ginkgo/v2/types/version.go](vendor/github.com/onsi/ginkgo/v2/types/version.go)
- [vendor/k8s.io/apimachinery/pkg/api/validation/objectmeta.go](vendor/k8s.io/apimachinery/pkg/api/validation/objectmeta.go)
- [vendor/modules.txt](vendor/modules.txt)

</details>



## Purpose and Scope

This document details the required tools, their versions, and environment configuration needed for both local development and CI build/test workflows in the `k8s-test-infra` project. The focus is on setting up a consistent environment for building the core components (including the nvml-mock GPU simulation system), running end-to-end tests, and contributing to the codebase.

This page covers installation and verification of:

- Go programming language and module management
- Docker container tooling
- Kubernetes CLI (`kubectl`)
- `kind` (Kubernetes in Docker) for local clusters
- `tilt` for local development workflow orchestration
- Additional tools for linting, building, and testing

For building the project artifacts, see [Building from Source](#2.2). For the Go version management strategy used consistently throughout the repo and CI, see [Go Version Management Strategy](#8.3).

---

## Required Tools Overview

The project requires a range of tools for compilation, image building, Kubernetes interaction, test execution, and local dev environment orchestration.

```mermaid
graph TB
    subgraph "Local Development / CI Environment"
        Go["Go 1.26.0<br/>Compiler & Runtime"]
        Docker["Docker<br/>Container Builds & Images"]
        Kubectl["kubectl<br/>Kubernetes CLI"]
        Kind["kind<br/>Local Kubernetes Cluster"]
        Tilt["Tilt<br/>Dev Workflow Orchestration"]
        Make["Make<br/>Build Orchestration"]
        Golint["golangci-lint<br/>Code Quality"]
    end

    subgraph "Core Artifacts"
        NvmlMockLib["libnvidia-ml.so<br/>Mock NVML Shared Library"]
        Binaries["Go Binaries<br/>(nvml-mock-nri, mock-ib, etc)"]
        HelmChart["nvml-mock Helm Chart<br/>For Cluster Deployment"]
    end

    subgraph "Test and Cluster"
        K8sCluster["Kubernetes Cluster<br/>Test Target (kind, remote)"]
        TestSuites["Ginkgo/Gomega Test Suites<br/>E2E and Unit Tests"]
    end

    Go -->|Builds| Binaries
    Go -->|Builds (c-shared library)| NvmlMockLib
    Make -->|Orchestrates| Go
    Make -->|Runs| Golint
    Docker -->|Builds| NvmlMockLib
    Docker -->|Builds| Binaries
    Docker -->|Builds| HelmChart
    Kubectl -->|Cluster interaction| K8sCluster
    Kind -->|Provides| K8sCluster
    Tilt -->|Local dev orchestration| K8sCluster
    TestSuites -->|Use| Kubectl
    TestSuites -->|Use| K8sCluster
```

- The Go compiler produces various Go binaries and the nvml-mock shared library (`libnvidia-ml.so`).
- Docker builds container images for the mock system, test binaries, and Helm charts.
- `kubectl` and `kind` provide Kubernetes cluster interaction and lifecycle for tests.
- `tilt` is a helper for local multi-component development.
- Make orchestrates builds and linting.

Sources: [go.mod:3-3](), [deployments/devel/Dockerfile:15-18](), [deployments/nvml-mock/Dockerfile:15-49](), [.github/workflows/golang.yaml:27-71]()

---

## Go Programming Language

### Version Requirement

- **Go version 1.26.0** is mandated for consistent builds.
- This exact version is declared in the development Dockerfile (`deployments/devel/Dockerfile`) which acts as the single source of truth.
- The project uses Go modules (`go.mod`) with vendoring enforced, including the `vendor/` directory checked into source control.

| Requirement      | Value      | Source                           |
|------------------|------------|---------------------------------|
| Go version       | 1.26.0     | [deployments/devel/Dockerfile:17]() |
| Module support   | Enabled    | `go.mod`                        |
| Vendoring        | Required   | `vendor/` directory             |

### Version Management Flow

```mermaid
graph LR
    Dockerfile["deployments/devel/Dockerfile<br/>FROM golang:1.26.0"]
    Script["hack/golang-version.sh<br/>Extracts Go version"]
    CIYaml["GitHub Actions<br/>Golang workflow"]
    LocalEnv["Local development environment"]

    Dockerfile -->|Defines version| Script
    Script -->|Provides version| CIYaml
    Dockerfile -->|Reference version| LocalEnv
```

The `hack/golang-version.sh` script parses the Dockerfile to propagate the Go version consistently in CI workflows and local development environments.

### Installation & Verification

Install Go 1.26.0 from the official binaries or package manager according to your platform. Verify the version using:

```bash
go version
# Expected output: go version go1.26.0 linux/amd64 (platform dependent)
```

Sources: [deployments/devel/Dockerfile:15-18](), [.github/workflows/golang.yaml:28-70]()

---

## Docker

### Purpose and Usage

Docker is essential for:

- Building container images for deployment (`nvml-mock`, `nvml-mock-nri`, etc.)
- Running local Kubernetes clusters with `kind` (which uses Docker containers)
- CI workflows to package and publish images (e.g., [nvml-mock-publish.yaml]())

### Version Requirements

| Tool            | Minimum Version | Recommended      |
|-----------------|-----------------|------------------|
| Docker Engine   | 20.10+          | Latest stable    |
| Docker Buildx   | Latest          | For multi-arch   |

### Installation & Verification

Install Docker according to your OS using official instructions. Verify with:

```bash
docker version
docker run --rm hello-world
```

Ensure Docker daemon runs without requiring root (add your user to `docker` group on Linux).

Sources: [deployments/devel/Dockerfile:1-18](), [.github/workflows/nvml-mock-publish.yaml:36-75]()

---

## kubectl (Kubernetes CLI)

### Purpose

`kubectl` is used to interact with the Kubernetes cluster:

- Creating and querying test resources (e.g. Custom Resources, pods)
- Debugging cluster state during development
- Used implicitly by tests and deployments

### Version Requirements

| Component | Version    | Notes                              |
|-----------|------------|----------------------------------|
| kubectl   | 1.36.1+    | Matches cluster version ±1 minor |
| Kubernetes Cluster | 1.36+ | Enables latest APIs (DRA, NFD)   |

The nvml-mock image build installs `kubectl` version 1.36.1 by default.

### Installation & Verification

Download the appropriate binary for your platform or install via package manager.

Example Linux AMD64 install snippet:

```bash
curl -LO https://dl.k8s.io/release/v1.36.1/bin/linux/amd64/kubectl
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
kubectl version --client
```

### Dockerfile Kubernetes CLI Installation Details

In the `deployments/nvml-mock/Dockerfile`, `kubectl` is downloaded and verified as part of the image build (lines 38-82) ensuring tests use a consistent client version.

Sources: [deployments/nvml-mock/Dockerfile:38-82](), [deployments/devel/Dockerfile:1-18]()

---

## kind (Kubernetes IN Docker)

### Purpose

- Provides lightweight Kubernetes clusters running inside Docker containers
- Used extensively for local development and CI test clusters
- Supports multi-node and multi-architecture cluster profiles for GPU simulation

### Installation

Install `kind` via Go:

```bash
go install sigs.k8s.io/kind@v0.20.0
```

or download binaries from the kind GitHub releases page.

Confirm installation:

```bash
kind version
```

### Usage Notes

Tests and E2E harnesses use kind cluster profiles, created and deleted via Makefile targets and bash scripts (`tests/poc-validation/setup-kind-cluster.sh`).

Sources: Context from E2E harness and test cluster lifecycle orchestration

---

## Tilt (Local Development Workflow)

### Purpose

- Provides orchestration for local development environments with live reload of container images, manifests, and code
- Supports lengthy multi-component builds and Kubernetes cluster interactions
- Simplifies testing overlay configuration and demo scenarios locally

### Installation

Download and install Tilt from https://tilt.dev/ or via package managers.

Confirm version:

```bash
tilt version
```

### Configuration

The repository contains a `Tiltfile` script (not detailed here) that sets up clusters with selected GPU profiles, GPU Operator integration, DRA, and ComputeDomain simulation.

Tilt flags include `--gpu-profile`, `--gpu-operator`, and others for demo scenario selection supported by multiple subcommands in the harness.

Sources: Context from section 11, Tilt workflow, and development practices

---

## Make

### Purpose

Make is used as the primary build orchestrator:

- `make build` compiles Go binaries and libraries
- `make lint` runs code quality linting with `golangci-lint`
- `make vendor` manages vendored dependencies
- `make check*` verifies module and vendor consistency
- Other targets create/destroy test clusters and run tests

### Installation & Verification

Make is commonly pre-installed; otherwise install using OS package manager.

Verify:

```bash
make --version
```

Sources: Context from CI workflows and build orchestration

---

## golangci-lint

### Purpose

- Enforces code quality, style, security, and static analysis checks in the CI workflow and locally
- Runs multiple linters concurrently for efficiency

### Installation & Version

Use latest stable:

```bash
curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b $(go env GOPATH)/bin
golangci-lint --version
```

The CI runs use the latest version `golangci-lint` (see the `.github/workflows/golang.yaml`).

Sources: [.github/workflows/golang.yaml:40-42]()

---

## Environment Configuration

### Kubernetes Cluster Access

Your `KUBECONFIG` environment variable must point to a Kubernetes cluster credential file, either local kind cluster or remote.

Example setup:

```bash
export KUBECONFIG=$HOME/.kube/config
kubectl get nodes # verify access
```

### Go Environment Variables

For Go module and binary behavior:

```bash
export GO111MODULE=on
export GOPATH=$HOME/go
export PATH=$PATH:$(go env GOPATH)/bin
export GOPRIVATE=github.com/NVIDIA/k8s-test-infra
```

### Repository Setup

Clone repository and verify vendoring:

```bash
git clone https://github.com/NVIDIA/k8s-test-infra.git
cd k8s-test-infra
ls vendor/
ls go.mod go.sum
```

Sources: [deployments/devel/Dockerfile:1-18]()

---

## Complete Verification Flow

Below is the summarized verification sequence of the core environment:

```mermaid
graph TB
    start["Start Environment Check"]

    subgraph versions ["Check Required Tools"]
        go_ver["Go version == 1.26.0"]
        docker_ver["Docker version >= 20.10"]
        kubectl_ver["kubectl version >= 1.36"]
        make_ver["Make installed"]
        golint_ver["golangci-lint installed"]
    end

    subgraph cluster ["Check Kubernetes Cluster Access"]
        config_set["KUBECONFIG set"]
        cluster_info["kubectl cluster-info reachable"]
    end

    subgraph repo ["Repository Verification"]
        cloned["Repository cloned"]
        vendor_dir["vendor/ directory exists"]
        gomod_files["go.mod and go.sum present"]
    end

    start --> go_ver --> docker_ver --> kubectl_ver --> make_ver --> golint_ver
    golint_ver --> config_set --> cluster_info --> cloned --> vendor_dir --> gomod_files
    gomod_files --> ready["Environment Ready for Build and Test"]
```

Additionally, ensure `kind` and optionally `tilt` tools are installed for local testing and dev workflow.

---

## Troubleshooting & Version Enforcement

- The Go version is tightly controlled to avoid vendor mismatches, controlled by the Dockerfile and CI parsing script.
- Common errors stem from incorrect Go version, missing `kubectl`, or lack of cluster access.
- Docker permission issues may require adding your user to the `docker` group.

---

## Next Steps

After verifying prerequisites, proceed to:

1. Build binaries and container images (see [2.2 Building from Source])
2. Run initial tests and demo scenarios (see [2.3 Running Your First Test])
3. Explore local development with Tilt (see section 11)

The CI workflows automate these checks and builds, enforcing this environment in GitHub Actions.

---

# Summary Table of Required Tools and Versions

| Tool            | Required Version      | Purpose                          | Source File(s)                   |
|-----------------|-----------------------|---------------------------------|---------------------------------|
| Go              | 1.26.0                | Compile Go code & mock library  | deployments/devel/Dockerfile     |
| Docker          | 20.10+                | Build container images          | workflows/nvml-mock-publish.yaml |
| kubectl         | 1.36.1+               | Kubernetes CLI client           | deployments/nvml-mock/Dockerfile |
| kind            | 0.20.0+ (recommended) | Local Kubernetes cluster        | tests/poc-validation/setup-kind-cluster.sh (context) |
| Make            | Any recent             | Build orchestration             | CI workflows                    |
| golangci-lint   | Latest stable          | Linting & code quality          | .github/workflows/golang.yaml   |
| tilt            | Latest recommended     | Local development orchestration | Context from local dev pages    |

---

Sources:  
[go.mod:3-3](), [deployments/devel/Dockerfile:15-18](), [deployments/nvml-mock/Dockerfile:15-82](), [.github/workflows/golang.yaml:27-71](), [.github/workflows/nvml-mock-publish.yaml:36-75](), [tests/poc-validation/setup-kind-cluster.sh:1-35]()

---

# Page: Building from Source

# Building from Source

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cmd/generate-bridge/main.go](cmd/generate-bridge/main.go)
- [cmd/generate-bridge/main_test.go](cmd/generate-bridge/main_test.go)
- [cmd/generate-bridge/parser.go](cmd/generate-bridge/parser.go)
- [deployments/nvml-mock/Dockerfile](deployments/nvml-mock/Dockerfile)
- [pkg/gpu/mockcuda/Makefile](pkg/gpu/mockcuda/Makefile)
- [pkg/gpu/mocknvml/Dockerfile](pkg/gpu/mocknvml/Dockerfile)
- [pkg/gpu/mocknvml/Makefile](pkg/gpu/mocknvml/Makefile)
- [pkg/gpu/mocknvml/README.md](pkg/gpu/mocknvml/README.md)
- [pkg/gpu/mocknvml/bridge/cgo_types.go](pkg/gpu/mocknvml/bridge/cgo_types.go)
- [pkg/gpu/mocknvml/bridge/init.go](pkg/gpu/mocknvml/bridge/init.go)
- [pkg/gpu/mocknvml/bridge/internal.go](pkg/gpu/mocknvml/bridge/internal.go)
- [pkg/gpu/mocknvml/bridge/padding.go](pkg/gpu/mocknvml/bridge/padding.go)
- [pkg/gpu/mocknvml/bridge/system.go](pkg/gpu/mocknvml/bridge/system.go)
- [tests/e2e/spike-nvidia-smi.sh](tests/e2e/spike-nvidia-smi.sh)
- [tests/mocknvml/Dockerfile](tests/mocknvml/Dockerfile)
- [tests/poc-validation/setup-kind-cluster.sh](tests/poc-validation/setup-kind-cluster.sh)

</details>



## Purpose and Scope

This page explains how to build the `nvml-mock` shared library, various container images, and Go binaries within the `k8s-test-infra` repository. It covers local builds, Docker cross-platform builds, and the `generate-bridge` code generation tool. For information about setting up your development environment and installing prerequisites, see [Prerequisites and Environment Setup](#2.1). For details on the Docker images and containerization, see [Docker Images](#8.2).

---

## Build System Overview

The `k8s-test-infra` repository uses a Makefile-based build system to compile the `nvml-mock` shared library, various Go binaries, and manage container image creation. The build system enforces code quality through integrated linting, formatting checks, and dependency verification.

### Build Architecture

```mermaid
graph TD
    subgraph "Source Files"
        GO_MOD["go.mod & go.sum"]
        VENDOR["vendor/ directory"]
        NVML_GO["pkg/gpu/mocknvml/bridge/*.go"]
        NVML_CGO["pkg/gpu/mocknvml/bridge/bridge.go"]
        NVML_MAKEFILE["pkg/gpu/mocknvml/Makefile"]
        CUDA_MAKEFILE["pkg/gpu/mockcuda/Makefile"]
        MOCKIB_MAKEFILE["pkg/network/mockib/Makefile"]
        MOCKPCISYSFS_MAKEFILE["pkg/system/mockpcisysfs/Makefile"]
        GEN_BRIDGE_MAIN["cmd/generate-bridge/main.go"]
        NVML_H["vendor/github.com/NVIDIA/go-nvml/pkg/nvml/nvml.h"]
        NVML_GO_WRAPPER["vendor/github.com/NVIDIA/go-nvml/pkg/nvml/nvml.go"]
        DEPLOY_DOCKERFILE["deployments/nvml-mock/Dockerfile"]
        TEST_MOCKNVML_DOCKERFILE["tests/mocknvml/Dockerfile"]
        GO_BINARIES_SRC["cmd/.../*.go"]
    end

    subgraph "Build Tools"
        MAKE["make"]
        GO_BUILD["go build"]
        DOCKER_BUILD["docker build"]
        GEN_BRIDGE_TOOL["generate-bridge"]
    end

    subgraph "Artifacts"
        LIB_NVML["libnvidia-ml.so*"]
        LIB_CUDA["libcuda.so*"]
        LIB_IB["libibmocksys.so*"]
        LIB_PCISYSFS["libpcimocksys.so*"]
        NVML_MOCK_NRI_BIN["nvml-mock-nri"]
        NVML_MOCK_CTL_BIN["nvml-mock-ctl"]
        RENDER_PCI_SYSFS_BIN["render-pci-sysfs"]
        MOCK_IB_BIN["mock-ib"]
        FAKE_IMEX_BIN["nvidia-imex"]
        FAKE_FABRICMANAGER_BIN["nv-fabricmanager"]
        CHECK_FABRIC_BIN["check-fabric"]
        NVML_MOCK_IMAGE["nvml-mock:latest"]
        TEST_MOCKNVML_IMAGE["mocknvml-test:latest"]
        STUBS_GENERATED["pkg/gpu/mocknvml/bridge/stubs_generated.go"]
    end

    NVML_MAKEFILE -- "make" --> LIB_NVML
    CUDA_MAKEFILE -- "make" --> LIB_CUDA
    MOCKIB_MAKEFILE -- "make" --> LIB_IB
    MOCKPCISYSFS_MAKEFILE -- "make" --> LIB_PCISYSFS

    NVML_GO_WRAPPER -- "Input" --> GEN_BRIDGE_TOOL
    NVML_H -- "Header" --> GEN_BRIDGE_TOOL
    NVML_CGO -- "Bridge Dir" --> GEN_BRIDGE_TOOL
    GEN_BRIDGE_MAIN -- "Runs" --> GEN_BRIDGE_TOOL
    GEN_BRIDGE_TOOL -- "Generates" --> STUBS_GENERATED

    NVML_CGO -- "Uses" --> STUBS_GENERATED
    NVML_CGO -- "Compiles with CGo" --> LIB_NVML

    DEPLOY_DOCKERFILE -- "Builds" --> NVML_MOCK_IMAGE
    DEPLOY_DOCKERFILE -- "Copies from builder" --> LIB_NVML
    DEPLOY_DOCKERFILE -- "Copies from builder" --> LIB_CUDA
    DEPLOY_DOCKERFILE -- "Copies from builder" --> LIB_IB
    DEPLOY_DOCKERFILE -- "Copies from builder" --> LIB_PCISYSFS
    DEPLOY_DOCKERFILE -- "Copies from builder" --> NVML_MOCK_NRI_BIN
    DEPLOY_DOCKERFILE -- "Copies from builder" --> NVML_MOCK_CTL_BIN
    DEPLOY_DOCKERFILE -- "Copies from builder" --> RENDER_PCI_SYSFS_BIN
    DEPLOY_DOCKERFILE -- "Copies from builder" --> MOCK_IB_BIN
    DEPLOY_DOCKERFILE -- "Copies from builder" --> FAKE_IMEX_BIN
    DEPLOY_DOCKERFILE -- "Copies from builder" --> FAKE_FABRICMANAGER_BIN
    DEPLOY_DOCKERFILE -- "Copies from builder" --> CHECK_FABRIC_BIN

    TEST_MOCKNVML_DOCKERFILE -- "Builds" --> TEST_MOCKNVML_IMAGE
    TEST_MOCKNVML_DOCKERFILE -- "Copies from lib-builder" --> LIB_NVML

    GO_BINARIES_SRC -- "go build" --> NVML_MOCK_NRI_BIN
    GO_BINARIES_SRC -- "go build" --> NVML_MOCK_CTL_BIN
    GO_BINARIES_SRC -- "go build" --> RENDER_PCI_SYSFS_BIN
    GO_BINARIES_SRC -- "go build" --> MOCK_IB_BIN
    GO_BINARIES_SRC -- "go build" --> FAKE_IMEX_BIN
    GO_BINARIES_SRC -- "go build" --> FAKE_FABRICMANAGER_BIN
    GO_BINARIES_SRC -- "go build" --> CHECK_FABRIC_BIN

    NVML_MAKEFILE -- "docker-build" --> DOCKER_BUILD
    DOCKER_BUILD -- "Builds lib in container" --> LIB_NVML
```

**Sources:**
* [deployments/nvml-mock/Dockerfile:1-113]()
* [pkg/gpu/mocknvml/Makefile:1-145]()
* [pkg/gpu/mockcuda/Makefile:1-40]()
* [cmd/generate-bridge/main.go:1-136]()
* [tests/mocknvml/Dockerfile:1-75]()

The build system components include:

| Component | Purpose | Key Files |
|-----------|---------|-----------|
| **Mock NVML Library** | Core GPU simulation library | [pkg/gpu/mocknvml/Makefile:1-145](), [pkg/gpu/mocknvml/bridge/]() |
| **Mock CUDA Library** | Mock CUDA runtime library | [pkg/gpu/mockcuda/Makefile:1-40](), [pkg/gpu/mockcuda/bridge/]() |
| **Mock IB/PCI Sysfs Libraries** | Mock InfiniBand and PCI sysfs libraries | [pkg/network/mockib/Makefile:1-39](), [pkg/system/mockpcisysfs/Makefile:1-39]() |
| **Go Binaries** | Various tools and daemons | [deployments/nvml-mock/Dockerfile:26-35](), [cmd/]() |
| **Container Images** | Packaging of libraries and binaries | [deployments/nvml-mock/Dockerfile:1-113](), [tests/mocknvml/Dockerfile:1-75]() |
| **Code Generation** | Automates CGo bridge stub creation | [cmd/generate-bridge/main.go:1-136]() |

---

## Building the `nvml-mock` Shared Library

The `nvml-mock` shared library (`libnvidia-ml.so`) is the core component for GPU simulation. It's built using CGo.

### Local Build (Linux with Go and GCC)

To build the `libnvidia-ml.so` locally:

```bash
cd pkg/gpu/mocknvml
make
```
This command compiles the `libnvidia-ml.so.<version>`, `libnvidia-ml.so.1` (symlink), and `libnvidia-ml.so` (symlink) files in the current directory.
**Sources:** [pkg/gpu/mocknvml/Makefile:29-33]()

The `Makefile` handles the CGo compilation and symlink creation. It also includes logic for library-size padding to mimic the size of a real `libnvidia-ml.so`.
**Sources:** [pkg/gpu/mocknvml/Makefile:88-112]()

#### Library-size Padding

The `nvml-mock` library includes a padding mechanism to make its on-disk size similar to a real `libnvidia-ml.so` (approximately 14 MiB for driver 550.x). This helps satisfy tools that perform weak authenticity checks based on file size.
**Sources:** [pkg/gpu/mocknvml/README.md:69-72](), [pkg/gpu/mocknvml/bridge/padding.go:16-22]()

- **Default**: A two-pass build automatically pads the library to `TARGET_LIB_SIZE` (default `14680064` bytes).
  ```bash
  make
  make size # Reports final size
  ```
  **Sources:** [pkg/gpu/mocknvml/Makefile:39](), [pkg/gpu/mocknvml/Makefile:96-112]()
- **Explicit Padding**: Override `TARGET_LIB_SIZE` or set `PADDING_BYTES` for a specific size.
  ```bash
  make PADDING_BYTES=10485760 # 10 MiB padding
  ```
  **Sources:** [pkg/gpu/mocknvml/Makefile:40](), [pkg/gpu/mocknvml/README.md:83]()
- **Disable Padding**: Use `NO_PADDING=1` or `BUILD_TAGS=nopadding` to create a smaller library.
  ```bash
  make NO_PADDING=1
  # or
  make BUILD_TAGS=nopadding
  ```
  **Sources:** [pkg/gpu/mocknvml/Makefile:41](), [pkg/gpu/mocknvml/README.md:86-88]()

The padding is implemented in [pkg/gpu/mocknvml/bridge/padding.go]() using a C `__attribute__((used, section(".data.nvml_mock_padding")))` to ensure the blob is included in the `.data` section and not optimized away.
**Sources:** [pkg/gpu/mocknvml/bridge/padding.go:58-60]()

### Docker Cross-platform Build

To build the `nvml-mock` library inside a Docker container, producing Linux-compatible binaries even on macOS:

```bash
cd pkg/gpu/mocknvml
make docker-build
```
**Sources:** [pkg/gpu/mocknvml/README.md:43-46]()

This command uses the `Dockerfile` at [pkg/gpu/mocknvml/Dockerfile:1-26]() to create a builder image and then runs `make` inside it.
**Sources:** [pkg/gpu/mocknvml/Makefile:133-145]()

### Build Variables

The `pkg/gpu/mocknvml/Makefile` supports several variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `LIB_VERSION` | Library version (appears in filename) | `550.163.01` |
| `GOLANG_VERSION` | Go version for Docker builds | `1.26.5` |
| `TARGET_LIB_SIZE` | Target on-disk size in bytes (two-pass auto-pads to this) | `14680064` (≈14 MiB) |
| `PADDING_BYTES` | Explicit padding size in bytes (overrides `TARGET_LIB_SIZE`) | _(unset → auto)_ |
| `NO_PADDING` | Set to `1` to disable padding (small library) | _(unset)_ |
| `BUILD_TAGS` | Extra Go build tags (include `nopadding` to disable padding) | _(unset)_ |

**Sources:** [pkg/gpu/mocknvml/README.md:51-59]()

---

## Building Other Shared Libraries

Similar to `nvml-mock`, other mock shared libraries are built using their respective Makefiles.

### Mock CUDA Library

The `libcuda.so` mock library is built from [pkg/gpu/mockcuda/Makefile:1-40]().
```bash
cd pkg/gpu/mockcuda
make
```
This generates `libcuda.so.<version>`, `libcuda.so.1`, and `libcuda.so`.
**Sources:** [pkg/gpu/mockcuda/Makefile:29-33]()

### Mock InfiniBand and PCI Sysfs Libraries

The `libibmocksys.so` and `libpcimocksys.so` libraries are built from their respective directories:
```bash
cd pkg/network/mockib
make
cd pkg/system/mockpcisysfs
make
```
These are included in the `deployments/nvml-mock/Dockerfile` build process.
**Sources:** [deployments/nvml-mock/Dockerfile:23-25]()

---

## Building Go Binaries

Several Go binaries are part of the `k8s-test-infra` project, including `nvml-mock-nri`, `nvml-mock-ctl`, `render-pci-sysfs`, `mock-ib`, `nvidia-imex`, `nv-fabricmanager`, and `check-fabric`.

These binaries are typically built as part of the Docker image creation process. The `deployments/nvml-mock/Dockerfile` contains a `builder` stage that compiles all necessary Go binaries.
**Sources:** [deployments/nvml-mock/Dockerfile:16-35]()

For example, `nvml-mock-nri` is built with:
```dockerfile
go build -mod=vendor -o /out/nvml-mock-nri ./cmd/nvml-mock-nri
```
**Sources:** [deployments/nvml-mock/Dockerfile:28]()

This uses `go build -mod=vendor` to ensure that vendored dependencies are used, promoting reproducible builds.

---

## Building Container Images

The project includes several Docker images for deployment and testing.

### `nvml-mock` Image

The main `nvml-mock` container image is defined in [deployments/nvml-mock/Dockerfile:1-113](). This is a multi-stage build:

```mermaid
graph TD
    subgraph "Builder Stage (golang:GOLANG_VERSION-bookworm)"
        B[("FROM golang:${GOLANG_VERSION}-bookworm")]
        B --> B_COPY_SRC["COPY go.mod go.sum vendor/ pkg/ cmd/"]
        B_COPY_SRC --> B_MAKE_LIBS["RUN cd pkg/gpu/mocknvml && make<br/>RUN cd pkg/gpu/mockcuda && make<br/>..."]
        B_MAKE_LIBS --> B_BUILD_BINS["RUN go build -mod=vendor -o /out/mock-ib ./cmd/mock-ib<br/>... (all Go binaries)"]
    end

    subgraph "Runtime Stage (debian:bookworm-slim)"
        R[("FROM debian:bookworm-slim")]
        R --> R_COPY_LIBS["COPY --from=builder /src/pkg/gpu/mocknvml/libnvidia-ml.so.* /usr/local/lib/"]
        R --> R_COPY_BINS["COPY --from=builder /out/mock-ib /usr/local/bin/mock-ib<br/>... (all Go binaries)"]
        R --> R_INSTALL_DEPS["RUN apt-get update && apt-get install -y ... (kubectl, nvidia-utils, patchelf)"]
        R --> R_COPY_SCRIPTS["COPY deployments/nvml-mock/scripts/ /scripts/"]
    end

    B --> R
```

**Sources:** [deployments/nvml-mock/Dockerfile:1-113]()

To build this image:
```bash
docker build -t nvml-mock:latest -f deployments/nvml-mock/Dockerfile .
```
**Sources:** [tests/poc-validation/setup-kind-cluster.sh:75-77]()

Key aspects of this Dockerfile:
- **`builder` stage**: Compiles all CGo shared libraries (NVML, CUDA, IB, PCI Sysfs) and Go binaries.
  **Sources:** [deployments/nvml-mock/Dockerfile:16-35]()
- **`debian:bookworm-slim` base**: A minimal base image for the runtime.
  **Sources:** [deployments/nvml-mock/Dockerfile:37]()
- **Copying artifacts**: Shared libraries are copied to `/usr/local/lib/` and binaries to `/usr/local/bin/` or `/usr/bin/`.
  **Sources:** [deployments/nvml-mock/Dockerfile:40-66]()
- **`nvidia-smi` inclusion**: The real `nvidia-smi` binary is extracted from `nvidia-utils` package and included, with `RPATH` adjusted for portability.
  **Sources:** [deployments/nvml-mock/Dockerfile:88-106]()
- **`kubectl` inclusion**: `kubectl` is downloaded and installed.
  **Sources:** [deployments/nvml-mock/Dockerfile:77-84]()

### `mocknvml-test` Image

This image is used for integration testing of the `nvml-mock` library. It's defined in [tests/mocknvml/Dockerfile:1-75]().

```mermaid
graph TD
    subgraph "lib-builder Stage (golang:GOLANG_VERSION)"
        LB[("FROM golang:${GOLANG_VERSION}")]
        LB --> LB_COPY_SRC["COPY go.mod go.sum vendor/ pkg/ cmd/"]
        LB --> LB_BUILD_LIB["RUN go build -buildmode=c-shared -o libnvidia-ml.so.550.54.15 ./bridge"]
    end

    subgraph "test-builder Stage (golang:GOLANG_VERSION)"
        TB[("FROM golang:${GOLANG_VERSION}")]
        TB --> TB_COPY_TEST_SRC["COPY tests/mocknvml/*.go tests/mocknvml/go.mod tests/mocknvml/go.sum*"]
        TB --> TB_BUILD_TEST_BIN["RUN CGO_ENABLED=1 go build -o mocknvml-test ."]
    end

    subgraph "Runtime Stage (debian:bookworm-slim)"
        R[("FROM debian:bookworm-slim")]
        R --> R_INSTALL_DEPS["RUN apt-get update && apt-get install -y ca-certificates"]
        R --> R_COPY_TEST_BIN["COPY --from=test-builder /build/mocknvml-test /app/"]
        R --> R_COPY_CONFIG["COPY tests/mocknvml/util-test-config.yaml /app/util-test-config.yaml"]
        R --> R_COPY_LIB["COPY --from=lib-builder /build/pkg/gpu/mocknvml/libnvidia-ml.so* /usr/local/lib/"]
        R --> R_LDCONFIG["RUN ldconfig"]
        R --> R_ENV_VARS["ENV LD_LIBRARY_PATH=/usr/local/lib<br/>ENV MOCK_NVML_NUM_DEVICES=4<br/>ENV MOCK_NVML_DRIVER_VERSION=550.54.15"]
        R --> R_CMD["CMD [\"/app/mocknvml-test\"]"]
    end

    LB --> R
    TB --> R
```

**Sources:** [tests/mocknvml/Dockerfile:1-75]()

This image:
- Builds `libnvidia-ml.so` in the `lib-builder` stage.
  **Sources:** [tests/mocknvml/Dockerfile:15-30]()
- Builds the `mocknvml-test` Go binary in the `test-builder` stage.
  **Sources:** [tests/mocknvml/Dockerfile:31-42]()
- Combines these artifacts in the runtime stage, sets `LD_LIBRARY_PATH`, and configures mock NVML environment variables.
  **Sources:** [tests/mocknvml/Dockerfile:43-74]()

### Spike `nvidia-smi` Image

The `spike-nvidia-smi.sh` script builds a temporary `nvml-mock` image and runs `nvidia-smi` against it for quick verification.
**Sources:** [tests/e2e/spike-nvidia-smi.sh:1-62]()

```bash
docker build --platform "$PLATFORM" -t "$IMAGE" \
  --build-arg GOLANG_VERSION="$GOLANG_VERSION" \
  -f deployments/nvml-mock/Dockerfile .
```
**Sources:** [tests/e2e/spike-nvidia-smi.sh:26-28]()

This script demonstrates how to build the `nvml-mock` image for a specific platform (e.g., `linux/amd64` for `nvidia-smi` compatibility) and then execute `nvidia-smi` with mock NVML debug logging enabled.
**Sources:** [tests/e2e/spike-nvidia-smi.sh:31-34]()

---

## `generate-bridge` Code Generation Tool

The `cmd/generate-bridge` tool automates the creation of CGo stubs for the `nvml-mock` library. This ensures comprehensive coverage of the NVML API and simplifies maintenance.
**Sources:** [cmd/generate-bridge/main.go:14-28]()

### Purpose

The tool scans the `go-nvml` wrapper for all exported NVML functions and compares them against existing `//export` implementations in the `pkg/gpu/mocknvml/bridge` directory. It then generates stubs for any missing functions, using `nvml.h` to extract correct C function prototypes for ABI compatibility.
**Sources:** [cmd/generate-bridge/main.go:14-28]()

### Usage

```bash
go run ./cmd/generate-bridge \
    -input vendor/github.com/NVIDIA/go-nvml/pkg/nvml/nvml.go \
    -header vendor/github.com/NVIDIA/go-nvml/pkg/nvml/nvml.h \
    -bridge pkg/gpu/mocknvml/bridge \
    -output pkg/gpu/mocknvml/bridge/stubs_generated.go
```
**Sources:** [cmd/generate-bridge/main.go:23-28]()

### Data Flow

```mermaid
graph LR
    NVML_GO_WRAPPER[("vendor/github.com/NVIDIA/go-nvml/pkg/nvml/nvml.go")] --> P1{{"parseNVMLFunctions()"}}
    NVML_H[("vendor/github.com/NVIDIA/go-nvml/pkg/nvml/nvml.h")] --> P2{{"parseNVMLPrototypes()"}}
    BRIDGE_DIR[("pkg/gpu/mocknvml/bridge/")] --> S1{{"scanBridgeExports()"}}

    P1 --> ALL_FUNCS["All NVML Functions (Go)"]
    P2 --> PROTOTYPES["C Function Prototypes (from nvml.h)"]
    S1 --> EXISTING_EXPORTS["Existing //export Functions"]

    ALL_FUNCS --> F1{{"findMissing()"}}
    EXISTING_EXPORTS --> F1
    F1 --> MISSING_FUNCS["Missing Functions"]

    MISSING_FUNCS --> G1{{"generateStubsFileWithPrototypes()"}}
    PROTOTYPES --> G1
    G1 --> STUBS_GENERATED[("pkg/gpu/mocknvml/bridge/stubs_generated.go")]

    STUBS_GENERATED -- "Used by CGo" --> LIB_NVML_BUILD["libnvidia-ml.so Build"]
```

**Sources:**
* [cmd/generate-bridge/main.go:91-136]()
* [cmd/generate-bridge/main.go:138-156]() (`parseNVMLFunctions`)
* [cmd/generate-bridge/parser.go:37-85]() (`parseNVMLPrototypes`)
* [cmd/generate-bridge/main.go:159-211]() (`scanBridgeExports`)
* [cmd/generate-bridge/main.go:213-220]() (`findMissing`)
* [cmd/generate-bridge/main.go:241-250]() (`generateStubWithSignature`)

### Key Functions

- `parseNVMLFunctions(filename string)`: Extracts all `nvml` prefixed function names from the `go-nvml` wrapper.
  **Sources:** [cmd/generate-bridge/main.go:138-156]()
- `parseNVMLPrototypes(r io.Reader)`: Parses `nvml.h` to extract C function prototypes, handling multi-line declarations and `DEPRECATED()` macros.
  **Sources:** [cmd/generate-bridge/parser.go:37-85]()
- `scanBridgeExports(bridgeDir string)`: Scans `.go` files in the bridge directory for `//export` comments to identify already implemented functions.
  **Sources:** [cmd/generate-bridge/main.go:159-211]()
- `findMissing(allFunctions []string, existingFunctions map[string]bool)`: Determines which functions from `go-nvml` are not yet implemented in the bridge.
  **Sources:** [cmd/generate-bridge/main.go:213-220]()
- `generateStubWithSignature(proto FuncProto)`: Generates a single CGo stub function with the correct C-compatible Go signature.
  **Sources:** [cmd/generate-bridge/parser.go:241-250]()

The `generate-bridge` tool ensures that the mock NVML library remains up-to-date with the `go-nvml` API, reducing manual effort and potential errors.

---

## Go Version Management

The repository enforces a consistent Go version across all environments using a single-source-of-truth approach. For comprehensive details on this strategy, see [Go Version Management Strategy](#8.3).

### Version Definition

The Go version is defined in [deployments/nvml-mock/Dockerfile:15]() and [tests/mocknvml/Dockerfile:14]():

```dockerfile
ARG GOLANG_VERSION=1.26.5
FROM golang:${GOLANG_VERSION}-bookworm AS builder
```
**Sources:** [deployments/nvml-mock/Dockerfile:15-16]()

This `GOLANG_VERSION` argument is used consistently across Dockerfiles to ensure the same Go compiler is used for all builds.

---

## Verifying the Build

After building, you can verify the artifacts:

- **Shared Libraries**: Check for `.so` files in `pkg/gpu/mocknvml/`, `pkg/gpu/mockcuda/`, etc.
  ```bash
  ls -lh pkg/gpu/mocknvml/libnvidia-ml.so*
  ```
- **Go Binaries**: If built locally, check `bin/` directory. If built via Docker, inspect the image.
  ```bash
  docker run --rm nvml-mock:latest ls -lh /usr/local/bin/nvml-mock-nri
  ```
- **`nvidia-smi` with mock NVML**: Use the `spike-nvidia-smi.sh` script to run `nvidia-smi` against the mock library in a container.
  ```bash
  ./tests/e2e/spike-nvidia-smi.sh
  ```
  **Sources:** [tests/e2e/spike-nvidia-smi.sh:1-62]()

---

## Next Steps

- **Run Tests**: After building successfully, proceed to [Running Your First Test](#2.3) to execute the test suite.
- **Understand Build Automation**: Learn more about the CI/CD pipeline in [GitHub Actions Workflows](#4.1).
- **Explore Make Targets**: For a comprehensive reference of all build targets, see [Makefile Reference](#8.1).
- **Configure Development Environment**: Return to [Prerequisites and Environment Setup](#2.1) if you encounter missing dependencies.

---

# Page: Running Your First Test

# Running Your First Test

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/nvml-mock-e2e-go.yaml](.github/workflows/nvml-mock-e2e-go.yaml)
- [Makefile](Makefile)
- [README.md](README.md)
- [docs/README.md](docs/README.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/demo/kind.yaml](docs/demo/kind.yaml)
- [docs/demo/with-fgo/README.md](docs/demo/with-fgo/README.md)
- [docs/examples.md](docs/examples.md)
- [docs/integrations/fake-gpu-operator.md](docs/integrations/fake-gpu-operator.md)
- [docs/quickstart.md](docs/quickstart.md)
- [tests/e2e/README.md](tests/e2e/README.md)
- [tests/e2e/go/e2e_suite_test.go](tests/e2e/go/e2e_suite_test.go)
- [tests/e2e/go/framework/config/config.go](tests/e2e/go/framework/config/config.go)
- [tests/e2e/go/framework/harness/harness.go](tests/e2e/go/framework/harness/harness.go)
- [tests/e2e/go/suite_cluster.go](tests/e2e/go/suite_cluster.go)
- [tests/e2e/go/suite_helm.go](tests/e2e/go/suite_helm.go)
- [tests/mocknvml/Makefile](tests/mocknvml/Makefile)
- [tests/mocknvml/README.md](tests/mocknvml/README.md)
- [tests/mocknvml/main.go](tests/mocknvml/main.go)

</details>



This page guides you through executing test suites in the k8s-test-infra repository and interpreting their output. It covers basic test execution commands, configuration options, and understanding test results, including local usage of the mock NVML library via `nvidia-smi`, invoking the Makefile end-to-end (E2E) targets, and a quick-start Helm deployment. For information on setting up your environment, see [Prerequisites and Environment Setup](#2.1). For details on the Ginkgo testing framework itself, see [Testing with Ginkgo](#5).

---

## Executing a Test Suite Locally with Mock NVML

Before running complex cluster E2E tests, you can quickly validate the mock NVML shared library locally by using `nvidia-smi` with the mock library preloaded. This test confirms that the simulated GPU environment provided by the mock NVML can properly enumerate devices and expose typical GPU information.

### Using the Mock NVML Library with `nvidia-smi`

1. Build the mock NVML shared library:

```bash
make -C pkg/gpu/mocknvml
```

2. Select a GPU profile YAML config, for example, the A100 profile:

```bash
export MOCK_NVML_CONFIG=$(pwd)/pkg/gpu/mocknvml/configs/mock-nvml-config-a100.yaml
```

3. Set the `LD_LIBRARY_PATH` to point to the mock NVML directory so that `nvidia-smi` uses the mock shared library:

```bash
export LD_LIBRARY_PATH=$(pwd)/pkg/gpu/mocknvml
```

4. Run `nvidia-smi`:

```bash
nvidia-smi -L
```

This lists the simulated GPUs as reported by the mock NVML. For a full query:

```bash
nvidia-smi -q
```

This will output detailed GPU information including temperature, memory, power usage, and PCIe info, simulated according to the chosen profile YAML.

### What the Mock NVML Integration Test Does

The integration test executable in `tests/mocknvml/main.go` performs an enumeration of the mock devices via the NVIDIA Management Library (NVML) API. It initializes NVML, enumerates devices, queries attributes such as names, UUIDs, PCI Bus IDs, memory usage, and CUDA compute capability, then validates indexing functions through UUID and PCI Bus ID handles. Finally, it performs edge-case "bridge" tests on NVML API calls.

This helps verify that the `libnvidia-ml.so` mock library works correctly for common device plugin and GPU Operator interactions.

**Sources:** [tests/mocknvml/main.go:14-202](), [docs/examples.md:5-230]()

---

## Running End-to-End Tests with Makefile E2E Targets

The repository includes a comprehensive Ginkgo-based E2E test suite under `tests/e2e/go/` that runs full cluster lifecycle, Helm deployment, and GPU-profile assertions.

### Typical Local Commands Using Makefile

```bash
# Run the default E2E suite with the 'gb200' GPU profile on a fresh Kind cluster
make e2e

# Run E2E test for a specific single profile such as 'a100'
make e2e E2E_PROFILES=a100

# Run tests filtered by labels (e.g., only nvidia-smi or NVLink tests)
make e2e E2E_GINKGO_FLAGS='--label-filter="nvidia-smi || nvlink"'

# Use a prebuilt image to skip rebuilding Docker image inside test
docker build -t nvml-mock:e2e -f deployments/nvml-mock/Dockerfile .
make e2e E2E_SKIP_BUILD=true E2E_IMAGE=nvml-mock:e2e E2E_PROFILES=a100

# Delete Kind cluster at teardown instead of keeping it for debugging
make e2e E2E_KEEP_CLUSTER=false
```

The `make e2e` target owns a full test lifecycle:

- Building/loading the `nvml-mock:e2e` Docker image (unless `E2E_SKIP_BUILD=true`)
- Creating a Kind cluster from a topology YAML manifest
- Loading the Docker image into Kind nodes
- Installing `nvml-mock` Helm chart with selected GPU profile(s)
- Running the standalone demo scenario checks that exercise mock GPU behavior
- Collecting diagnostic artifacts on failure
- Retaining or deleting the Kind cluster depending on settings

More specialized `make` targets exist for DRA, GPU Operator, multi-node, and NRI ambient injection tests:

- `make e2e-dra`
- `make e2e-gpu-operator`
- `make e2e-multi-node`
- `make e2e-nri`

**Sources:** [Makefile:141-166](), [tests/e2e/README.md:1-136]()

---

## Helm Quick-Start Deployment for Manual Testing

To quickly deploy the `nvml-mock` environment on an existing Kubernetes cluster (such as the Kind cluster created above), you can install the Helm chart directly:

```bash
helm install nvml-mock oci://ghcr.io/nvidia/k8s-test-infra/chart/nvml-mock
```

This command installs the `nvml-mock` DaemonSet into the `mokka` namespace by default, running the mock NVML library in pods on each node to simulate the GPUs defined by the default profile (`gb200`).

If you want to specify GPU profile and count explicitly, you can override values:

```bash
helm install nvml-mock oci://ghcr.io/nvidia/k8s-test-infra/chart/nvml-mock \
  --set gpu.profile=a100 \
  --set gpu.count=8 \
  --wait --timeout 120s
```

The Helm chart has options to enable integration with the fake GPU operator, dynamic metrics, and other features to simulate complex GPU environments without actual NVIDIA hardware.

After install, you can verify the pod is running:

```bash
kubectl get pods -n mokka -l app.kubernetes.io/name=nvml-mock -o wide
```

And exec into the pod to run `nvidia-smi`:

```bash
kubectl exec -n mokka -it <nvml-mock-pod> -- nvidia-smi
```

This will use the mock NVML shared library inside the container and output the simulated GPU devices.

**Sources:** [README.md:21-46](), [tests/e2e/go/suite_helm.go:6-79]()

---

## Data Flow and Key Code Components in a Test Run

### Local `nvidia-smi` with Mock Library

- The environment variable `LD_LIBRARY_PATH` is set to `pkg/gpu/mocknvml/` with the built `libnvidia-ml.so` export.
- When `nvidia-smi` runs, it loads the mock NVML library via the dynamic linker.
- The mock library loads a YAML config file defining GPU device topologies.
- NVML API calls like `Init()`, `DeviceGetCount()`, and `DeviceGetHandleByIndex()` return simulated devices.
- `nvidia-smi` queries various device properties, producing the output.
- The integration test binary in `tests/mocknvml/main.go` performs similar API calls to validate the mock behavior.

### Makefile `e2e` Target Flow

- `make e2e` triggers the Go Ginkgo tests under `tests/e2e/go`.
- The harness configures GPU profiles and cluster topology based on `E2E_PROFILES`.
- The harness creates (or attaches to) a Kind cluster using manifests (`docs/demo/kind.yaml`).
- It builds and loads the `nvml-mock` Docker image into Kind nodes.
- Helm installs the `nvml-mock` chart with the selected profile(s), configured via `helm.Release` in `suite_helm.go`.
- The test suite runs multiple Ginkgo specs covering features: device enumeration, NVLink, failure injection, PCI sysfs, InfiniBand mocks, and scheduler integration.
- On failure, diagnostics are collected in the artifacts directory.

### Helm Deployment

- The Helm chart (in `deployments/nvml-mock/helm/nvml-mock`) creates a Kubernetes DaemonSet.
- Each DaemonSet pod runs the mock NVML shared library and supporting binaries.
- The GPU profile ConfigMap drives the pod configuration.
- The pods expose standard GPU interfaces inside containers for downstream workloads.
- Integration with fake GPU operator or DRA drivers can be enabled via Helm values.

---

## Mermaid Diagrams Linking Natural Language to Code Entities

### Diagram: Local Mock NVML Usage from CLI to Code

```mermaid
graph TD
    CLI[nvidia-smi CLI] -->|loads| DYNLINK[Dynamic Linker]
    DYNLINK -->|loads mock lib| MOCKLIB["libnvidia-ml.so (mock NVML)"]
    MOCKLIB -->|reads| YAML[MOCK_NVML_CONFIG YAML]
    MOCKLIB --> API["NVML API Functions (Go wrapper)"]
    API --> GO_NVML["github.com/NVIDIA/go-nvml/pkg/nvml"]
    GO_NVML --> MOCKAPI["Mock NVML Cgo Bridge"]
    MOCKAPI --> MOCK_DATA["Simulated GPU Device Data"]
    
    classDef codeEntity fill:#fff,stroke:#000,stroke-width:1px;
    MOCKLIB,API,GO_NVML,MOCKAPI,MOCK_DATA,YAML class codeEntity
```

**Sources:** [tests/mocknvml/main.go:14-202](), [docs/examples.md:5-230]()

---

### Diagram: Makefile `make e2e` and Test Harness Lifecycle

```mermaid
graph TD
    MAKEFILE["Makefile `make e2e`"] --> E2E_SUITE["E2E Test Suite (`tests/e2e/go/e2e_suite_test.go`)"]
    E2E_SUITE --> HARNESS["harness.Harness (cluster lifecycle manager)"]
    HARNESS --> KIND["Kind Cluster Creation (`kind create cluster`)"]
    HARNESS --> DOCKER_IMAGE["Docker Build/Load `nvml-mock:e2e`"]
    HARNESS --> HELM["Helm Install/Upgrade (`suite_helm.go` installDemoChart)"]
    HELM --> CHART["nvml-mock Helm Chart (`deployments/nvml-mock/helm/nvml-mock`)"]
    E2E_SUITE --> GINKGO["Ginkgo Test Runner"]
    GINKGO --> SCENARIOS["Scenario Tests (`scenario_*.go`)"]
    SCENARIOS --> ASSERTIONS["Assertions (e.g. nvidia-smi, NVLink)"]
    
    classDef codeEntity fill:#fff,stroke:#000,stroke-width:1px;
    E2E_SUITE,HARNESS,KIND,DOCKER_IMAGE,HELM,CHART,GINKGO,SCENARIOS,ASSERTIONS class codeEntity
```

**Sources:** [Makefile:141-166](), [tests/e2e/README.md:1-136](), [tests/e2e/go/suite_helm.go:6-79]()

---

## Interpreting Basic Test Output

When you run tests via Ginkgo (for example, `make e2e` or direct `ginkgo` runs), you will see output indicating test progress, summarized failures, and the final result.

### Typical Output Elements

- Progress dots:
  - `.` indicates a passed test
  - `S` skipped test
  - `F` failed test
- Summary section with:
  - Total specs run
  - Passed, failed, pending, skipped counts
  - Duration
- Failure detail blocks with failing spec descriptions and file locations

### Example Snippet

```
••••S•••F•••••

Summarizing 1 Failure:

[FAIL] scenario_standalone_test.go:42
  NVIDIA-smi returns expected simulated GPU list

Ran 15 of 20 Specs in 2.3s
FAIL! -- 14 Passed | 1 Failed | 0 Pending | 5 Skipped
```

### Failure Diagnostics

If a test fails, the harness will collect logs and diagnostic artifacts into a configured directory (default `artifacts/e2e/go`) for debugging.

---

## Summary

This page covered:

- Using the mock NVML shared library locally to run `nvidia-smi` and verify GPU enumeration.
- Running clustered end-to-end tests with `make e2e` and related targets.
- Quick Helm installation of the `nvml-mock` DaemonSet for GPU simulation.
- Detailed diagrams showing how CLI commands map into code components and the full test lifecycle.
- Basic guidance on test output interpretation.

These workflows enable developers and integration testers to validate GPU software stack compatibility, simulate realistic GPU hardware topologies, and contribute robust tests within the k8s-test-infra system.

---

For further exploration:

- [Prerequisites and Environment Setup](#2.1) to prepare your workstation.
- [Building from Source](#2.2) for compiling binaries and images.
- [Testing with Ginkgo](#5) to dive deeper into the testing framework.
- [Helm Chart Deployment](#9.3) for advanced chart operation.

---

# Appendix: Important Makefile and Helm Targets

| Target             | Description                                         |
|--------------------|-----------------------------------------------------|
| `make e2e`          | Run full end-to-end tests with default GPU profile |
| `make e2e-dra`      | Run DRA scenario tests                              |
| `make e2e-gpu-operator` | Run GPU Operator integration tests               |
| `make e2e-multi-node`| Multi-node heterogeneous GPU scenario              |
| `make e2e-nri`      | Node-wide NRI ambient injection test                |
| `cluster-create`    | Create the Kind cluster with configured profile    |
| `cluster-delete`    | Delete the Kind cluster                             |
| `helm-unittest`     | Run Helm unit tests on chart                        |
| `image-kind-node`   | Build or use cached Kind node base image            |

---

# Appendix: Example Helm Installation CLI

```bash
helm install nvml-mock oci://ghcr.io/nvidia/k8s-test-infra/chart/nvml-mock \
  --set gpu.profile=gb200 \
  --set gpu.count=8
```

---

# References

- Mock NVML integration test main function: [tests/mocknvml/main.go:14-202]()
- Makefile targets and `e2e` lifecycle: [Makefile:141-166]()
- E2E test suite Helm install: [tests/e2e/go/suite_helm.go:6-79]()
- Examples of local mock NVML usage: [docs/examples.md:5-230]()
- Basic usage in README: [README.md:21-46]()
- Full E2E test README and commands: [tests/e2e/README.md:1-136]()

---

# Page: Architecture

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/README.md](docs/README.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/demo/kind.yaml](docs/demo/kind.yaml)
- [docs/demo/with-fgo/README.md](docs/demo/with-fgo/README.md)
- [docs/examples.md](docs/examples.md)
- [docs/integrations/fake-gpu-operator.md](docs/integrations/fake-gpu-operator.md)
- [docs/quickstart.md](docs/quickstart.md)
- [pkg/gpu/mocknvml/README.md](pkg/gpu/mocknvml/README.md)
- [pkg/gpu/mocknvml/bridge/padding.go](pkg/gpu/mocknvml/bridge/padding.go)

</details>



## Purpose and Scope

This document provides a high-level overview of the `k8s-test-infra` repository architecture, explaining how its components are organized and interact to provide Kubernetes testing infrastructure, with a primary focus on the `nvml-mock` GPU simulation system, Node Feature Discovery (NFD), and Dynamic Resource Allocation (DRA) testing.

For detailed information about specific architectural layers:
- **Module dependencies and vendoring strategy**: See [Module Dependencies](#3.1)
- **Kubernetes API integration patterns**: See [Kubernetes Integration Layer](#3.2)
- **Testing framework design and patterns**: See [Testing Infrastructure Design](#3.3)

For build system details, CI/CD workflows, and development practices, refer to sections [CI/CD Pipeline](#4), [Build System](#8), and [nvml-mock System](#9).

Sources: [docs/README.md:1-4](), [go.mod:1-16]()

---

## System Overview

The `k8s-test-infra` repository provides testing infrastructure for Kubernetes environments, with specialized support for hardware feature discovery (NFD) and dynamic device resource allocation (DRA). A core component is the `nvml-mock` library, which simulates NVIDIA GPUs without physical hardware. The system is structured as a single Go module that builds various tools and provides comprehensive test utilities for validating Kubernetes cluster behavior.

The repository serves three primary functions:

1.  **Mock NVML Library**: A configurable mock implementation of NVIDIA's NVML (NVIDIA Management Library) for testing GPU-dependent software without physical NVIDIA hardware [pkg/gpu/mocknvml/README.md:1-4]().
2.  **Kubernetes Integration**: Provides tools and patterns for integrating the mock NVML environment with Kubernetes, including DaemonSet deployments, CDI injection, and NRI plugins.
3.  **Testing Infrastructure**: Offers a BDD-style testing framework built on Ginkgo v2 and Gomega for writing and executing Kubernetes integration tests, particularly for NFD and DRA.

Sources: [pkg/gpu/mocknvml/README.md:1-4](), [go.mod:1-16](), [vendor/modules.txt:1-550]()

---

## Architectural Layers

The system follows a layered architecture where each layer provides abstractions and services to the layers above it. This design promotes separation of concerns and makes the codebase maintainable and testable.

### Mock NVML Stack Layers

The `nvml-mock` library itself is structured into several layers, from the CGo bridge to the configurable device logic.

#### Mock NVML Internal Architecture

```mermaid
graph TD
    subgraph "User Space"
        nvidia_smi["nvidia-smi<br/>(real binary)"]
        YourApplication["Your Application<br/>(k8s-device-plugin, dcgm, etc)"]
    end

    subgraph "libnvidia-ml.so (MOCK)"
        CGoBridge["CGo Bridge Layer<br/>(bridge)"]
        EngineLayer["Engine Layer<br/>(engine/engine.go)"]
        ConfigurableDevice["ConfigurableDevice<br/>(engine/config.go, engine/config_types.go)"]
    end

    nvidia_smi -- "dlopen('libnvidia-ml.so')" --> CGoBridge
    YourApplication -- "dlopen('libnvidia-ml.so')" --> CGoBridge

    CGoBridge -- "Calls Go functions" --> EngineLayer
    EngineLayer -- "Manages device instances" --> ConfigurableDevice
    ConfigurableDevice -- "Wraps go-nvml mock" --> GoNVMLMock["go-nvml mock<br/>(github.com/NVIDIA/go-nvml/pkg/nvml/mock)"]

    subgraph "Configuration"
        YAMLConfig["YAML Configuration<br/>(configs/*.yaml)"]
        EnvVars["Environment Variables<br/>(MOCK_NVML_CONFIG, etc)"]
    end

    YAMLConfig --> EngineLayer
    EnvVars --> EngineLayer
```

**Layer Responsibilities:**

| Layer | Purpose | Key Components |
|---|---|---|
| **CGo Bridge Layer** | Exposes NVML C functions as dynamically loadable symbols, handles C ↔ Go type conversions. | `bridge/cgo_types.go`, `bridge/helpers.go`, `bridge/init.go`, `bridge/device.go`, `bridge/system.go`, `bridge/stubs_generated.go` |
| **Engine Layer** | Central coordinator for `nvml-mock` lifecycle, configuration loading, and mapping C pointers to Go objects. | `engine/engine.go`, `engine/handles.go` |
| **ConfigurableDevice** | Implements NVML methods with YAML-driven property values, wraps `go-nvml` mock. | `engine/config.go`, `engine/config_types.go` |
| **Configuration** | Defines GPU profiles, system properties, and device-specific overrides. | `configs/*.yaml`, `MOCK_NVML_CONFIG`, `MOCK_NVML_NUM_DEVICES` environment variables |

For details on the `nvml-mock` library internals, see [Mock NVML Library Internals](#9.1).

Sources: [docs/architecture.md:7-45](), [pkg/gpu/mocknvml/README.md:1-4](), [pkg/gpu/mocknvml/bridge/cgo_types.go:1-10](), [pkg/gpu/mocknvml/bridge/helpers.go:1-10](), [pkg/gpu/mocknvml/bridge/init.go:1-10](), [pkg/gpu/mocknvml/bridge/device.go:1-10](), [pkg/gpu/mocknvml/bridge/system.go:1-10](), [pkg/gpu/mocknvml/bridge/stubs_generated.go:1-10](), [pkg/gpu/mocknvml/engine/engine.go:1-10](), [pkg/gpu/mocknvml/engine/handles.go:1-10](), [pkg/gpu/mocknvml/engine/config.go:1-10](), [pkg/gpu/mocknvml/engine/config_types.go:1-10](), [pkg/gpu/mocknvml/configs/mock-nvml-config-a100.yaml:1-10]()

---

## Component Interactions

The following diagram illustrates how the major components interact during typical test execution, mapping architectural concepts to concrete code entities.

### Test Execution Flow

```mermaid
sequenceDiagram
    participant TestSuite as "Test Suite<br/>(*.test.go)"
    participant Ginkgo as "ginkgo/v2<br/>Test Runner"
    participant Gomega as "gomega<br/>Assertions"
    participant ClientGo as "client-go<br/>Kubernetes Client"
    participant HelmClient as "Helm Client<br/>(pkg/helm)"
    participant K8sAPI as "Kubernetes API Server"
    participant NvmlMockDaemonSet as "nvml-mock DaemonSet<br/>(deployments/nvml-mock)"
    participant NvmlMockLib as "libnvidia-ml.so<br/>(mocknvml)"
    participant NvidiaSMI as "nvidia-smi<br/>(inside pod)"

    TestSuite->>Ginkgo: "Describe/It blocks"
    Ginkgo->>TestSuite: "BeforeEach setup"

    TestSuite->>HelmClient: "Install nvml-mock chart"
    HelmClient->>K8sAPI: "Deploy DaemonSet, ConfigMaps"
    K8sAPI-->>HelmClient: "Resources created"
    HelmClient-->>TestSuite: "Deployment successful"

    TestSuite->>ClientGo: "Create Pod with GPU request"
    ClientGo->>K8sAPI: "HTTP POST /api/v1/pods"
    K8sAPI-->>ClientGo: "Pod created"
    ClientGo-->>TestSuite: "pod object"

    TestSuite->>ClientGo: "Exec into Pod"
    ClientGo->>K8sAPI: "Exec request"
    K8sAPI-->>ClientGo: "Exec session"
    ClientGo-->>TestSuite: "Exec client"

    TestSuite->>NvidiaSMI: "Run nvidia-smi -q"
    NvidiaSMI->>NvmlMockLib: "dlopen('libnvidia-ml.so')"
    NvmlMockLib->>NvmlMockLib: "Load config (MOCK_NVML_CONFIG)"
    NvmlMockLib->>NvmlMockLib: "Call NVML functions (e.g., nvmlDeviceGetCount)"
    NvmlMockLib-->>NvidiaSMI: "Mock NVML data"
    NvidiaSMI-->>TestSuite: "nvidia-smi output"

    TestSuite->>Gomega: "Eventually(func).Should(matcher)"
    Gomega->>TestSuite: "poll function"
    TestSuite-->>Gomega: "actual value"
    Gomega-->>TestSuite: "assertion result"

    Ginkgo->>TestSuite: "AfterEach cleanup"
    TestSuite->>HelmClient: "Uninstall nvml-mock chart"
    HelmClient->>K8sAPI: "Delete DaemonSet, ConfigMaps"
```

**Key Interaction Patterns:**

1.  **BDD Test Organization**: Tests use `github.com/onsi/ginkgo/v2` DSL (`Describe`, `Context`, `It`, `BeforeEach`, `AfterEach`) to structure test logic.
2.  **Asynchronous Assertions**: `github.com/onsi/gomega` `Eventually()` and `Consistently()` matchers handle asynchronous Kubernetes operations.
3.  **Kubernetes CRUD Operations**: `k8s.io/client-go/kubernetes` clientset provides typed access to all Kubernetes resources.
4.  **Helm Deployment**: The `pkg/helm` client is used to deploy and manage the `nvml-mock` DaemonSet and related resources.
5.  **Mock NVML Injection**: The `nvml-mock` DaemonSet injects `libnvidia-ml.so` into pods via `LD_LIBRARY_PATH`, allowing tools like `nvidia-smi` to interact with the mock library [pkg/gpu/mocknvml/README.md:28-30]().
6.  **Configuration**: The mock library's behavior is configured via YAML files, often passed through `MOCK_NVML_CONFIG` environment variables [pkg/gpu/mocknvml/README.md:102-122]().

Sources: [pkg/gpu/mocknvml/README.md:28-30,102-122](), [docs/examples.md:16-19](), [vendor/modules.txt:75-98](), [vendor/modules.txt:364-497]()

---

## Module Organization

The repository is organized as a single Go module (`github.com/NVIDIA/k8s-test-infra`) with all dependencies vendored for reproducible builds.

### Module Dependency Structure

```mermaid
graph TB
    ROOT["github.com/NVIDIA/k8s-test-infra<br/>go 1.25.0"]

    subgraph "Direct Dependencies"
        GINKGO["github.com/onsi/ginkgo/v2<br/>v2.27.2"]
        GOMEGA["github.com/onsi/gomega<br/>v1.38.2"]
        K8SAPI["k8s.io/api<br/>v0.34.2"]
        K8SAPIEXT["k8s.io/apiextensions-apiserver<br/>v0.34.2"]
        K8SAPIMACH["k8s.io/apimachinery<br/>v0.34.2"]
        K8SCLIENT["k8s.io/client-go<br/>v0.34.2"]
        KLOG["k8s.io/klog/v2<br/>v2.130.1"]
        NFD["sigs.k8s.io/node-feature-discovery<br/>v0.18.3"]
        NFDAPI["sigs.k8s.io/node-feature-discovery/api/nfd<br/>v0.18.3"]
        YAML["sigs.k8s.io/yaml<br/>v1.6.0"]
        GONVML["github.com/NVIDIA/go-nvml<br/>v0.12.0-rc.1"]
        CONTAINERD_NRI["github.com/containerd/nri<br/>v0.6.0"]
    end

    subgraph "Vendored"
        VENDOR["vendor/ directory<br/>Complete dependency tree<br/>Reproducible builds"]
    end

    ROOT --> GINKGO
    ROOT --> GOMEGA
    ROOT --> K8SAPI
    ROOT --> K8SAPIEXT
    ROOT --> K8SAPIMACH
    ROOT --> K8SCLIENT
    ROOT --> KLOG
    ROOT --> NFD
    ROOT --> NFDAPI
    ROOT --> YAML
    ROOT --> GONVML
    ROOT --> CONTAINERD_NRI

    GINKGO -.-> VENDOR
    GOMEGA -.-> VENDOR
    K8SCLIENT -.-> VENDOR
    NFD -.-> VENDOR
    GONVML -.-> VENDOR
    CONTAINERD_NRI -.-> VENDOR
```

**Module Characteristics:**

| Aspect | Details |
|---|---|
| **Module Path** | `github.com/NVIDIA/k8s-test-infra` |
| **Go Version** | `1.25.0` (defined in [go.mod:3]()) |
| **Vendoring** | All dependencies stored in `vendor/` directory |
| **Kubernetes Version** | v0.34.2 (api, client-go, apimachinery) |
| **Testing Framework** | Ginkgo v2.27.2, Gomega v1.38.2 |
| **NFD Version** | v0.18.3 |
| **NVML Go Bindings** | `github.com/NVIDIA/go-nvml v0.12.0-rc.1` |
| **Containerd NRI** | `github.com/containerd/nri v0.6.0` |

**Dependency Categories:**

1.  **Testing Dependencies** ([go.mod:6-7]()):
    -   `github.com/onsi/ginkgo/v2 v2.27.2` - BDD test framework
    -   `github.com/onsi/gomega v1.38.2` - Assertion library

2.  **Kubernetes Client Stack** ([go.mod:8-11]()):
    -   `k8s.io/api` - Resource type definitions
    -   `k8s.io/apimachinery` - Core machinery (meta, runtime, schema)
    -   `k8s.io/client-go` - Client library
    -   `k8s.io/apiextensions-apiserver` - CRD support

3.  **Specialized APIs** ([go.mod:13-14]()):
    -   `sigs.k8s.io/node-feature-discovery` - NFD client
    -   `sigs.k8s.io/node-feature-discovery/api/nfd` - NFD CRD types

4.  **GPU Simulation & Runtime** ([go.mod:16-17]()):
    -   `github.com/NVIDIA/go-nvml` - Go bindings for NVML, used by `nvml-mock`
    -   `github.com/containerd/nri` - Containerd Node Runtime Interface, used for `nvml-mock-nri` plugin

5.  **Utilities** ([go.mod:12,15]()):
    -   `k8s.io/klog/v2` - Structured logging
    -   `sigs.k8s.io/yaml` - YAML/JSON conversion

For a detailed breakdown of Go module structure and external dependencies, see [Module Dependencies](#3.1).

Sources: [go.mod:1-17](), [go.sum:1-180](), [vendor/modules.txt:1-550]()

---

## Design Principles

The architecture embodies several key design principles that guide implementation decisions:

### 1. Single Module with Vendoring

The repository uses a single Go module with vendored dependencies (`vendor/` directory) rather than a multi-module workspace. This ensures:

-   **Reproducible Builds**: Exact dependency versions are committed to the repository.
-   **Offline Development**: All dependencies available without network access.
-   **Consistent Testing**: CI and local builds use identical dependencies.

The `Makefile` enforces vendor synchronization via `check-vendor` and `check-modules` targets.

### 2. Kubernetes Native

The system is deeply integrated with Kubernetes through `k8s.io/client-go` and follows Kubernetes conventions:

-   **API Versioning**: Uses stable Kubernetes APIs (v0.34.2).
-   **Resource Watching**: Leverages watch APIs for observing cluster state changes.
-   **Server-Side Apply**: Uses modern server-side apply patterns for resource management.
-   **Custom Resources**: Extends Kubernetes with NFD CRDs through `k8s.io/apiextensions-apiserver` and integrates with DRA APIs.

For more on Kubernetes integration, see [Kubernetes Integration Layer](#3.2).

### 3. BDD Testing Approach

Tests follow Behavior-Driven Development patterns using Ginkgo v2:

-   **Readable Specs**: `Describe`/`Context`/`It` blocks create self-documenting test cases.
-   **Table-Driven Tests**: `DescribeTable`/`Entry` enable parameterized testing.
-   **Setup/Teardown Hooks**: `BeforeEach`/`AfterEach` manage test lifecycle.
-   **Asynchronous Matchers**: `Eventually()`/`Consistently()` handle Kubernetes eventual consistency.

For a comprehensive guide to the testing infrastructure, see [Testing Infrastructure Design](#3.3).

### 4. Layered Abstraction

Each architectural layer provides well-defined abstractions:

```mermaid
graph LR
    A["Test Code<br/>(Business Logic)"] --> B["Ginkgo DSL<br/>(Test Structure)"]
    B --> C["Gomega Matchers<br/>(Assertions)"]
    C --> D["client-go<br/>(K8s Operations)"]
    D --> E["Kubernetes API<br/>(Cluster State)"]
```

This separation allows:
-   Tests to focus on behavior rather than implementation.
-   Easy mocking and stubbing of Kubernetes operations.
-   Independent evolution of each layer.

### 5. Hardware-Aware Testing with Mock NVML

The architecture specializes in testing hardware feature discovery and allocation using the `nvml-mock` library:

-   **NVML Simulation**: `libnvidia-ml.so` provides a configurable mock NVML implementation [pkg/gpu/mocknvml/README.md:1-4]().
-   **NFD Integration**: Tests can validate `NodeFeature`, `NodeFeatureRule`, and `NodeFeatureGroup` CRDs, with `nvml-mock` generating feature files for node labeling.
-   **DRA Support**: Validates `ResourceSlice`, `ResourceClaim`, and `DeviceClass` for dynamic device allocation, integrating with the DRA driver.
-   **CDI Injection**: Supports Container Device Interface (CDI) specifications for GPU Operator integration [docs/README.md:14]().
-   **NRI Plugin**: The `nvml-mock-nri` plugin integrates with containerd for node-wide device injection [pkg/gpu/mocknvml/README.md:218-220]().

Sources: [go.mod:1-16](), [vendor/modules.txt:75-549](), [pkg/gpu/mocknvml/README.md:1-4,218-220](), [docs/README.md:14]()

---

## Cross-Cutting Concerns

Several utilities provide services across all layers:

### Certificate Generation

The `k8s.io/client-go/util/cert` package provides self-signed certificate generation for testing secure Kubernetes components:

-   **Function**: `GenerateSelfSignedCertKey(host string, alternateIPs []net.IP, alternateDNS []string) ([]byte, []byte, error)` [vendor/k8s.io/client-go/util/cert/cert.go:120-126]()
-   **Usage**: Creates CA and server certificates with configurable SANs.
-   **Validity**: Generates certificates valid for 1 year by default (configurable via `SelfSignedCertKeyOptions.MaxAge`).

### YAML/JSON Manifest Processing

The `k8s.io/apimachinery/pkg/util/yaml` package handles manifest loading:

-   **Type**: `YAMLOrJSONDecoder` [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:240-358]()
-   **Function**: `NewYAMLOrJSONDecoder(r io.Reader, bufferSize int) *YAMLOrJSONDecoder` [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:279-290]()
-   **Capability**: Automatically detects and decodes both JSON and multi-document YAML streams.
-   **Usage Pattern**: Tests load Kubernetes manifests from files and decode them into typed objects.

### Structured Logging

The `k8s.io/klog/v2` package provides structured logging:

-   **Version**: v2.130.1 [go.mod:12]()
-   **Integration**: Compatible with `go-logr` and standard library `log/slog`.
-   **Features**: Verbosity levels, key-value pairs, context integration.

Sources: [go.mod:12,15](), [vendor/k8s.io/client-go/util/cert/cert.go:1-277](), [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:1-486]()

---

## Summary

The `k8s-test-infra` architecture is a layered system designed for testing Kubernetes environments with specialized support for hardware feature discovery (NFD) and dynamic resource allocation (DRA), primarily driven by the `nvml-mock` GPU simulation system. Its single-module design with vendored dependencies ensures reproducibility, while the BDD testing approach with Ginkgo/Gomega provides readable, maintainable test specifications. The deep integration with `k8s.io/client-go` and support for NFD/DRA APIs, coupled with the `nvml-mock` library, makes it particularly suitable for testing hardware-aware Kubernetes workloads without physical GPUs.

For implementation details of each layer, see:
-   [Module Dependencies](#3.1) for dependency management and vendoring.
-   [Kubernetes Integration Layer](#3.2) for client-go patterns and API interactions.
-   [Testing Infrastructure Design](#3.3) for Ginkgo/Gomega test organization.

Sources: [go.mod:1-17](), [vendor/modules.txt:1-550](), [pkg/gpu/mocknvml/README.md:1-4]()

---

# Page: Module Dependencies

# Module Dependencies

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [go.mod](go.mod)
- [go.sum](go.sum)
- [vendor/github.com/NVIDIA/go-nvml/pkg/dl/dl.go](vendor/github.com/NVIDIA/go-nvml/pkg/dl/dl.go)
- [vendor/github.com/NVIDIA/go-nvml/pkg/dl/dl_linux.go](vendor/github.com/NVIDIA/go-nvml/pkg/dl/dl_linux.go)
- [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/api.go](vendor/github.com/NVIDIA/go-nvml/pkg/nvml/api.go)
- [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/cgo_helpers_static.go](vendor/github.com/NVIDIA/go-nvml/pkg/nvml/cgo_helpers_static.go)
- [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/const.go](vendor/github.com/NVIDIA/go-nvml/pkg/nvml/const.go)
- [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/device.go](vendor/github.com/NVIDIA/go-nvml/pkg/nvml/device.go)
- [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/mock/device.go](vendor/github.com/NVIDIA/go-nvml/pkg/nvml/mock/device.go)
- [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/mock/interface.go](vendor/github.com/NVIDIA/go-nvml/pkg/nvml/mock/interface.go)
- [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/nvml.go](vendor/github.com/NVIDIA/go-nvml/pkg/nvml/nvml.go)
- [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/nvml.h](vendor/github.com/NVIDIA/go-nvml/pkg/nvml/nvml.h)
- [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/types_gen.go](vendor/github.com/NVIDIA/go-nvml/pkg/nvml/types_gen.go)
- [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/zz_generated.api.go](vendor/github.com/NVIDIA/go-nvml/pkg/nvml/zz_generated.api.go)
- [vendor/github.com/onsi/ginkgo/v2/CHANGELOG.md](vendor/github.com/onsi/ginkgo/v2/CHANGELOG.md)
- [vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go](vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go)
- [vendor/github.com/onsi/ginkgo/v2/types/version.go](vendor/github.com/onsi/ginkgo/v2/types/version.go)
- [vendor/k8s.io/apimachinery/pkg/api/validation/objectmeta.go](vendor/k8s.io/apimachinery/pkg/api/validation/objectmeta.go)
- [vendor/modules.txt](vendor/modules.txt)

</details>



This page documents the Go module structure, dependency management strategy, and vendoring approach for the k8s-test-infra repository. It covers the direct and indirect dependencies, their purposes, and how they are managed to ensure reproducible builds.

For information about how these dependencies are used in the testing framework, see [Testing Infrastructure Design](#3.3). For Kubernetes API usage patterns, see [Kubernetes Integration Layer](#3.2). For build and verification processes, see [Makefile Reference](#8.1).

---

## Module Structure Overview

The repository is defined as a single Go module `github.com/NVIDIA/k8s-test-infra` with Go version 1.26.0. All dependencies are vendored into the `vendor/` directory for reproducible builds.

**Sources:** [go.mod:1-3]()

```mermaid
graph TB
    subgraph "Root Module"
        MAIN["github.com/NVIDIA/k8s-test-infra<br/>go 1.26.0"]
    end
    
    subgraph "Direct Dependencies"
        TESTING["Testing Framework"]
        K8S["Kubernetes Stack"]
        NFD["Node Feature Discovery"]
        UTILS["Utilities"]
        NVML["NVIDIA NVML Bindings"]
        NRI["Containerd NRI"]
    end
    
    subgraph "Vendored Storage"
        VENDOR["vendor/ directory<br/>All dependencies stored"]
    end
    
    MAIN --> TESTING
    MAIN --> K8S
    MAIN --> NFD
    MAIN --> UTILS
    MAIN --> NVML
    MAIN --> NRI
    
    TESTING -.-> VENDOR
    K8S -.-> VENDOR
    NFD -.-> VENDOR
    UTILS -.-> VENDOR
    NVML -.-> VENDOR
    NRI -.-> VENDOR
    
    style MAIN fill:#f9f9f9
    style VENDOR fill:#f0f0f0
```

**Sources:** [go.mod:1-20](), [vendor/modules.txt:1-550]()

---

## Direct Dependencies

### Testing Framework Dependencies

The repository uses Ginkgo v2 for BDD-style testing and Gomega for assertions. These are the most frequently updated dependencies and form the foundation of the test infrastructure.

| Package | Version | Purpose |
|---------|---------|---------|
| `github.com/onsi/ginkgo/v2` | v2.32.0 | BDD test runner with spec organization |
| `github.com/onsi/gomega` | v1.42.1 | Matcher library for assertions |
| `github.com/stretchr/testify` | v1.11.1 | General testing utilities and assertions |

**Sources:** [go.mod:8-10](), [vendor/modules.txt:96-132](), [vendor/github.com/onsi/ginkgo/v2/types/version.go:3](), [vendor/github.com/onsi/ginkgo/v2/CHANGELOG.md:1-3]()

### Kubernetes Client Stack

The Kubernetes dependencies provide full programmatic control over Kubernetes clusters, including API definitions, client operations, and CRD support.

```mermaid
graph LR
    subgraph "Kubernetes Dependencies v0.36.3"
        API["k8s.io/api<br/>Resource Types"]
        APIMACH["k8s.io/apimachinery<br/>Core Machinery"]
        CLIENTGO["k8s.io/client-go<br/>Client Library"]
        APIEXT["k8s.io/apiextensions-apiserver<br/>CRD Support"]
    end
    
    CLIENTGO --> API
    CLIENTGO --> APIMACH
    APIEXT --> API
    APIEXT --> APIMACH
    
    API --> |"Defines"| POD["Pod, Deployment,<br/>Service, etc."]
    APIMACH --> |"Provides"| META["meta/v1.ObjectMeta<br/>schema.GroupVersionKind"]
    CLIENTGO --> |"Implements"| OPS["CRUD Operations<br/>Watch, Apply"]
    APIEXT --> |"Handles"| CRD["CustomResourceDefinition<br/>Validation"]
```

**Sources:** [go.mod:12-15](), [vendor/k8s.io/apimachinery/pkg/api/validation/objectmeta.go:141-148]()

| Package | Version | Key Exports |
|---------|---------|-------------|
| `k8s.io/api` | v0.36.3 | Core resource types (v1.Pod, apps/v1.Deployment) |
| `k8s.io/apimachinery` | v0.36.3 | Runtime machinery (schema, conversion, validation) |
| `k8s.io/client-go` | v0.36.3 | Client operations, REST, Watch, Apply |
| `k8s.io/apiextensions-apiserver` | v0.36.3 | CRD clientsets and types |

**Sources:** [go.mod:12-15]()

### Node Feature Discovery Dependencies

NFD dependencies enable hardware feature discovery and node customization based on detected capabilities.

```mermaid
graph TB
    subgraph "NFD Module Structure"
        NFDMAIN["sigs.k8s.io/node-feature-discovery<br/>v0.19.0"]
        NFDAPI["sigs.k8s.io/node-feature-discovery/api/nfd<br/>v0.19.0"]
    end
    
    subgraph "API Types"
        NODEFEATURE["NodeFeature CRD"]
        NODEFEATRULE["NodeFeatureRule CRD"]
        NODEFEATGROUP["NodeFeatureGroup CRD"]
    end
    
    NFDMAIN --> NFDAPI
    
    NFDAPI --> NODEFEATURE
    NFDAPI --> NODEFEATRULE
    NFDAPI --> NODEFEATGROUP
```

**Sources:** [go.mod:17-18]()

### NVIDIA NVML Bindings

The `go-nvml` library provides Go bindings for the NVIDIA Management Library (NVML), allowing interaction with NVIDIA GPUs.

```mermaid
graph TD
    A[github.com/NVIDIA/go-nvml v0.13.3-1] --> B{NVML Interface}
    B --> C[nvml.Interface]
    B --> D[nvml.Device]
    B --> E[nvml.GpuInstance]
    C --> F[DeviceGetCount()]
    C --> G[DeviceGetHandleByIndex(index int)]
    D --> H[GetName()]
    D --> I[GetIndex()]
    D --> J[GetMemoryInfo()]
    D --> K[GetUtilization()]
    D --> L[GetPciInfo()]
    D --> M[GetUUID()]
    D --> N[GetTopologyCommonAncestor(device Device)]
    
    subgraph "Core NVML Types"
        nvmlDevice["nvmlDevice (internal C struct)"]
        nvmlGpuInstance["nvmlGpuInstance (internal C struct)"]
        PciInfo["nvml.PciInfo"]
        Memory["nvml.Memory"]
        Utilization["nvml.Utilization"]
        UUID["nvml.UUID"]
    end
    
    C -- "Wraps" --> nvmlDevice
    D -- "Wraps" --> nvmlDevice
    E -- "Wraps" --> nvmlGpuInstance
    
    style A fill:#f9f9f9
    style B fill:#f0f0f0
```

The `go-nvml` module includes generated code for the NVML API, such as `zz_generated.api.go` which maps C functions to Go, and `types_gen.go` for CGo-generated types. It also provides mock implementations for testing, like `mock/device.go` and `mock/interface.go`.

**Sources:** [go.mod:6](), [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/zz_generated.api.go:21-60](), [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/types_gen.go:8-10](), [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/device.go:28-59](), [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/mock/device.go:11-14](), [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/mock/interface.go:11-14]()

### Containerd NRI

The `containerd/nri` module provides the Node Resource Interface (NRI) for container runtimes, enabling plugins to manage and allocate resources for containers.

```mermaid
graph TD
    A[github.com/containerd/nri v0.12.1] --> B{NRI API}
    B --> C[pkg/api]
    B --> D[pkg/stub]
    B --> E[pkg/log]
    
    C --> F[API types: Container, Pod, Device, etc.]
    D --> G[Stub client for NRI plugins]
    E --> H[NRI-specific logging utilities]
    
    style A fill:#f9f9f9
    style B fill:#f0f0f0
```

**Sources:** [go.mod:7](), [vendor/modules.txt:16-22]()

### Utility Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `k8s.io/klog/v2` | v2.140.0 | Structured logging with verbosity levels |
| `sigs.k8s.io/yaml` | v1.6.0 | YAML/JSON conversion for manifests |
| `golang.org/x/sys` | v0.47.0 | Low-level system calls and OS primitives |

**Sources:** [go.mod:11,16,19]()

---

## Indirect Dependencies

The module declares numerous indirect dependencies that support the direct dependencies. These are automatically managed by Go modules.

### Key Indirect Dependencies

```mermaid
graph TB
    subgraph "Protocol & Serialization"
        PROTOBUF["google.golang.org/protobuf<br/>v1.36.12-0.20260120151049-f2248ac996af"]
        CBOR["github.com/fxamacker/cbor/v2<br/>v2.9.0"]
        JSONITER["github.com/json-iterator/go<br/>v1.1.12"]
    end
    
    subgraph "Network & HTTP"
        NET["golang.org/x/net<br/>v0.56.0"]
        OAUTH2["golang.org/x/oauth2<br/>v0.36.0"]
        GRPC["google.golang.org/grpc<br/>v1.82.1"]
    end
    
    subgraph "OpenAPI & Validation"
        OPENAPI["k8s.io/kube-openapi<br/>v0.0.0-20260317180543-43fb72c5454a"]
        GNOSTIC["github.com/google/gnostic-models<br/>v0.7.0"]
        SWAG["github.com/go-openapi/swag<br/>v0.23.0"]
    end
    
    subgraph "Logging & Reflection"
        LOGR["github.com/go-logr/logr<br/>v1.4.3"]
        REFLECT["github.com/modern-go/reflect2<br/>v1.0.3-0.20250322232337-35a7c28c31ee"]
        LOGRUS["github.com/sirupsen/logrus<br/>v1.9.4"]
    end
    
    subgraph "WebAssembly Runtime"
        WAZERO["github.com/tetratelabs/wazero<br/>v1.11.0"]
    end
    
    NET --> GRPC
    OPENAPI --> GNOSTIC
    OPENAPI --> SWAG
```

**Sources:** [go.mod:23-71](), [vendor/modules.txt:1-227]()

### Categories of Indirect Dependencies

| Category | Packages | Purpose |
|----------|----------|---------|
| **Protocol Buffers** | `google.golang.org/protobuf`, `google.golang.org/genproto/googleapis/rpc` | Kubernetes API serialization, gRPC communication |
| **JSON/YAML** | `github.com/json-iterator/go`, `gopkg.in/yaml.v3`, `sigs.k8s.io/json` | Manifest parsing and serialization |
| **OpenAPI** | `k8s.io/kube-openapi`, `github.com/google/gnostic-models`, `github.com/go-openapi/swag` | API schema validation |
| **Logging** | `github.com/go-logr/logr`, `github.com/sirupsen/logrus` | Structured logging interface |
| **Network** | `golang.org/x/net`, `golang.org/x/oauth2`, `google.golang.org/grpc` | HTTP/2 and authentication, gRPC client/server |
| **Utilities** | `golang.org/x/tools`, `golang.org/x/mod`, `github.com/google/uuid` | Go tooling support, UUID generation |
| **WebAssembly** | `github.com/tetratelabs/wazero` | WebAssembly runtime for plugins (e.g., NRI) |

**Sources:** [go.mod:23-71](), [vendor/modules.txt:1-227]()

---

## Vendoring Strategy

All dependencies are stored in the `vendor/` directory to ensure reproducible builds. The vendored packages are committed to the repository and tracked by Git.

### Vendor Directory Structure

```mermaid
graph TB
    subgraph "vendor/ Directory Layout"
        MODULES["modules.txt<br/>Package list & versions"]
        
        subgraph "Testing Packages"
            GINKGO["github.com/onsi/ginkgo/v2/<br/>75+ subpackages"]
            GOMEGA["github.com/onsi/gomega/<br/>11 subpackages"]
            TESTIFY["github.com/stretchr/testify/<br/>assert, require"]
        end
        
        subgraph "Kubernetes Packages"
            K8SAPI["k8s.io/api/<br/>57 API group packages"]
            K8SCLIENT["k8s.io/client-go/<br/>133 subpackages"]
            K8SMACH["k8s.io/apimachinery/<br/>54 subpackages"]
        end
        
        subgraph "NFD Packages"
            NFDPKG["sigs.k8s.io/node-feature-discovery/<br/>3 packages"]
        end
        
        subgraph "NVML Packages"
            GONVML["github.com/NVIDIA/go-nvml/<br/>pkg/nvml, pkg/dl, pkg/nvml/mock"]
        end
        
        subgraph "NRI Packages"
            CONTAINERDNRI["github.com/containerd/nri/<br/>pkg/api, pkg/stub"]
        end
    end
    
    MODULES -.->|"Indexes"| GINKGO
    MODULES -.->|"Indexes"| K8SAPI
    MODULES -.->|"Indexes"| NFDPKG
    MODULES -.->|"Indexes"| GONVML
    MODULES -.->|"Indexes"| CONTAINERDNRI
```

**Sources:** [vendor/modules.txt:1-550]()

### Modules Metadata

The `vendor/modules.txt` file tracks all vendored packages with their versions and Go version requirements:

```
# github.com/onsi/ginkgo/v2 v2.32.0
## explicit; go 1.25.0
github.com/onsi/ginkgo/v2
github.com/onsi/ginkgo/v2/config
github.com/onsi/ginkgo/v2/formatter
...
```

**Sources:** [vendor/modules.txt:96-119]()

---

## Dependency Management Workflow

The Makefile provides targets for managing dependencies and ensuring they remain synchronized.

### Management Targets

```mermaid
graph LR
    subgraph "Developer Actions"
        DEV["Developer<br/>modifies go.mod"]
    end
    
    subgraph "Makefile Targets"
        VENDOR["make vendor<br/>Sync dependencies"]
        CHECKVENDOR["make check-vendor<br/>Verify sync"]
        MODULES["make modules<br/>Tidy & vendor all"]
        CHECKMOD["make check-modules<br/>Verify all sync"]
    end
    
    subgraph "Go Commands"
        TIDY["go mod tidy"]
        GOVENDOR["go mod vendor"]
        VERIFY["go mod verify"]
    end
    
    subgraph "Validation"
        GITDIFF["git diff<br/>Check for changes"]
    end
    
    DEV --> VENDOR
    VENDOR --> TIDY
    TIDY --> GOVENDOR
    GOVENDOR --> VERIFY
    
    CHECKVENDOR --> VENDOR
    CHECKVENDOR --> GITDIFF
    
    MODULES --> TIDY
    MODULES --> GOVENDOR
    MODULES --> VERIFY
    
    CHECKMOD --> MODULES
    CHECKMOD --> GITDIFF
```

**Sources:** [Makefile:44-79]()

### Vendor Target

The `vendor` target synchronizes the vendor directory with `go.mod` and `go.sum`:

```makefile
vendor:
	go mod tidy
	go mod vendor
	go mod verify
```

**Sources:** [Makefile:44-47]()

### Check-Vendor Target

The `check-vendor` target ensures the vendor directory is synchronized:

```makefile
check-vendor: vendor
	git diff --quiet HEAD -- go.mod go.sum vendor
```

This fails if there are uncommitted changes after running `vendor`, ensuring CI catches any desynchronization.

**Sources:** [Makefile:49-50]()

### Modules Target

The `modules` target handles multi-module repositories by tidying and vendoring each module:

**Sources:** [Makefile:52-79]()

---

## Version Pinning

### Kubernetes Version Consistency

All Kubernetes dependencies use version v0.36.3, ensuring API compatibility across the stack:

```
k8s.io/api v0.36.3
k8s.io/apiextensions-apiserver v0.36.3
k8s.io/apimachinery v0.36.3
k8s.io/client-go v0.36.3
k8s.io/klog/v2 v2.140.0
k8s.io/kube-openapi v0.0.0-20260317180543-43fb72c5454a
k8s.io/utils v0.0.0-20260210185600-b8788abfbbc2
```

**Sources:** [go.mod:12-16,66-67]()

### NFD Version Consistency

Node Feature Discovery packages use v0.19.0 consistently:

```
sigs.k8s.io/node-feature-discovery v0.19.0
sigs.k8s.io/node-feature-discovery/api/nfd v0.19.0
```

**Sources:** [go.mod:17-18]()

---

## Dependency Update Strategy

Dependencies are automatically updated via Dependabot, which monitors for new versions on different schedules:

| Ecosystem | Schedule | Configuration |
|-----------|----------|---------------|
| `gomod` | Weekly | Monday 12:00 UTC |
| `docker` | Daily | Base image updates |
| `github-actions` | Daily | Workflow action updates |

For more details on automated dependency updates, see [Dependency Updates with Dependabot](#4.4).

**Sources:** Based on CI/CD infrastructure described in high-level diagrams

---

## Key Vendored Packages Reference

### Testing Packages Location

| Package | Vendor Path |
|---------|-------------|
| Ginkgo v2 core | `vendor/github.com/onsi/ginkgo/v2/` |
| Gomega matchers | `vendor/github.com/onsi/gomega/matchers/` |
| Testify assertions | `vendor/github.com/stretchr/testify/assert/` |
| Test reporters | `vendor/github.com/onsi/ginkgo/v2/reporters/` |

**Sources:** [vendor/modules.txt:96-132](), [vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go:8-20]()

### Kubernetes Client Location

| Component | Vendor Path |
|-----------|-------------|
| Core API types | `vendor/k8s.io/api/core/v1/` |
| Clientsets | `vendor/k8s.io/client-go/kubernetes/` |
| REST client | `vendor/k8s.io/client-go/rest/` |
| Certificate utilities | `vendor/k8s.io/client-go/util/cert/` |
| YAML decoder | `vendor/k8s.io/apimachinery/pkg/util/yaml/` |

**Sources:** [go.mod:12-15](), [vendor/k8s.io/apimachinery/pkg/api/validation/objectmeta.go:141-148]()

### NFD API Location

| Component | Vendor Path |
|-----------|-------------|
| NFD v1alpha1 types | `vendor/sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1/` |
| Generated clientset | `vendor/sigs.k8s.io/node-feature-discovery/api/generated/clientset/versioned/` |

**Sources:** [go.mod:17-18]()

### NVML Bindings Location

| Component | Vendor Path |
|-----------|-------------|
| NVML Go API | `vendor/github.com/NVIDIA/go-nvml/pkg/nvml/` |
| NVML CGo helpers | `vendor/github.com/NVIDIA/go-nvml/pkg/nvml/cgo_helpers_static.go` |
| NVML types | `vendor/github.com/NVIDIA/go-nvml/pkg/nvml/types_gen.go` |
| NVML mock interface | `vendor/github.com/NVIDIA/go-nvml/pkg/nvml/mock/interface.go` |
| NVML mock device | `vendor/github.com/NVIDIA/go-nvml/pkg/nvml/mock/device.go` |

**Sources:** [go.mod:6](), [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/types_gen.go:4-6](), [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/mock/interface.go:4-6](), [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/mock/device.go:4-6]()

### Containerd NRI Location

| Component | Vendor Path |
|-----------|-------------|
| NRI API types | `vendor/github.com/containerd/nri/pkg/api/` |
| NRI stub client | `vendor/github.com/containerd/nri/pkg/stub/` |

**Sources:** [go.mod:7](), [vendor/modules.txt:16-22]()

---

## Build Verification

The CI pipeline verifies dependency synchronization using the `check-modules` target during the `golang` job. This ensures:

1. `go.mod` and `go.sum` are synchronized
2. The `vendor/` directory contains all required packages
3. No unexpected modifications exist

Any desynchronization causes the build to fail, preventing merges with inconsistent dependencies.

**Sources:** [Makefile:75-79]()

---

# Page: Kubernetes Integration Layer

# Kubernetes Integration Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap](deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap)
- [deployments/nvml-mock/helm/nvml-mock/tests/daemonset_test.yaml](deployments/nvml-mock/helm/nvml-mock/tests/daemonset_test.yaml)
- [pkg/diagnostics/collector.go](pkg/diagnostics/collector.go)
- [pkg/diagnostics/extensions.go](pkg/diagnostics/extensions.go)
- [pkg/diagnostics/kubernetes.go](pkg/diagnostics/kubernetes.go)
- [pkg/diagnostics/options.go](pkg/diagnostics/options.go)
- [pkg/kubernetes/kubernetes.go](pkg/kubernetes/kubernetes.go)
- [vendor/k8s.io/api/resource/v1alpha3/generated.proto](vendor/k8s.io/api/resource/v1alpha3/generated.proto)
- [vendor/k8s.io/api/resource/v1alpha3/types.go](vendor/k8s.io/api/resource/v1alpha3/types.go)
- [vendor/k8s.io/api/resource/v1alpha3/types_swagger_doc_generated.go](vendor/k8s.io/api/resource/v1alpha3/types_swagger_doc_generated.go)
- [vendor/k8s.io/api/resource/v1beta1/generated.proto](vendor/k8s.io/api/resource/v1beta1/generated.proto)
- [vendor/k8s.io/api/resource/v1beta1/types.go](vendor/k8s.io/api/resource/v1beta1/types.go)
- [vendor/k8s.io/api/resource/v1beta1/types_swagger_doc_generated.go](vendor/k8s.io/api/resource/v1beta1/types_swagger_doc_generated.go)

</details>



## Purpose and Scope

This document describes how k8s-test-infra integrates with Kubernetes clusters and specialized APIs for hardware feature detection and dynamic resource allocation. It covers the client-go library usage for cluster operations, Node Feature Discovery (NFD) Custom Resource Definitions, Dynamic Resource Allocation (DRA) API resources, and supporting utilities for certificate generation and manifest processing. For information about how these integrations are tested, see [Testing Infrastructure Design](#3.3). For dependency management details, see [Module Dependencies](#3.1).

## Client-Go Integration Architecture

The system relies on k8s.io/client-go v0.34.2 as the foundation for all Kubernetes cluster interactions. This library provides typed clients, discovery mechanisms, and server-side apply functionality.

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `k8s.io/client-go` | v0.34.2 | Kubernetes API client library |
| `k8s.io/api` | v0.34.2 | Kubernetes API type definitions |
| `k8s.io/apimachinery` | v0.34.2 | Core API machinery (serialization, metadata, watches) |
| `k8s.io/apiextensions-apiserver` | v0.34.2 | Custom Resource Definition support |

**Sources:** [go.mod:1-16](), [vendor/modules.txt:239-497]()

### Client-Go Package Structure

```mermaid
graph TB
    subgraph "k8s.io/client-go"
        CLIENTSET["kubernetes.Clientset<br/>kubernetes/"]
        DISCOVERY["discovery.DiscoveryClient<br/>discovery/"]
        GENTYPE["gentype.Client<br/>gentype/"]
        REST["rest.RESTClient<br/>rest/"]
        APPLY["applyconfigurations/*<br/>applyconfigurations/"]
    end
    
    subgraph "k8s.io/apimachinery"
        SCHEMA["schema.GroupVersionResource<br/>runtime/schema/"]
        META["metav1.ObjectMeta<br/>apis/meta/v1/"]
        WATCH["watch.Interface<br/>watch/"]
        RUNTIME["runtime.Object<br/>runtime/"]
    end
    
    subgraph "k8s.io/api"
        COREV1["v1.Pod, v1.Node<br/>core/v1/"]
        RESOURCE["v1beta1.ResourceSlice<br/>resource/v1beta1/"]
    end
    
    CLIENTSET --> REST
    GENTYPE --> REST
    REST --> SCHEMA
    REST --> WATCH
    CLIENTSET --> COREV1
    CLIENTSET --> RESOURCE
    APPLY --> META
    
    style CLIENTSET fill:#e1f5ff
    style REST fill:#fff4e1
    style SCHEMA fill:#ffe1e1
```

**Client-Go Component Architecture**

**Sources:** [vendor/modules.txt:364-497](), [go.mod:8-11]()

### Kubernetes API Operations

The system uses client-go for standard CRUD operations and specialized patterns:

| Operation Pattern | Implementation | Use Case |
|-------------------|----------------|----------|
| Create | `client.Create(ctx, obj)` | Creating test resources |
| Get | `client.Get(ctx, name, namespace)` | Retrieving resource state |
| Update | `client.Update(ctx, obj)` | Modifying existing resources |
| Delete | `client.Delete(ctx, name, namespace)` | Cleanup operations |
| Watch | `client.Watch(ctx, opts)` | Observing resource changes |
| List | `client.List(ctx, opts)` | Enumerating resources |
| Server-Side Apply | `client.Apply(ctx, applyConfig)` | Declarative updates |

**Sources:** [vendor/modules.txt:418-497](), [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:240-358]()

## Node Feature Discovery API

The NFD API enables hardware feature detection and node customization based on discovered features. The system uses sigs.k8s.io/node-feature-discovery v0.18.3 and its API package v0.18.3.

### NFD Custom Resource Definitions

```mermaid
graph LR
    subgraph "NFD v1alpha1 API"
        NODEFEATURE["NodeFeature<br/>Spec: NodeFeatureSpec"]
        NODEFEATURERULE["NodeFeatureRule<br/>Spec: NodeFeatureRuleSpec"]
        NODEFEATUREGROUP["NodeFeatureGroup<br/>Spec: NodeFeatureGroupSpec<br/>Status: NodeFeatureGroupStatus"]
    end
    
    subgraph "NodeFeatureSpec"
        FEATURES["Features<br/>Flags, Attributes, Instances"]
        LABELS["Labels map[string]string"]
    end
    
    subgraph "Features Types"
        FLAGSET["FlagFeatureSet<br/>Elements: map[string]Nil"]
        ATTRSET["AttributeFeatureSet<br/>Elements: map[string]string"]
        INSTSET["InstanceFeatureSet<br/>Elements: []InstanceFeature"]
    end
    
    subgraph "NodeFeatureRuleSpec"
        RULES["Rules: []Rule"]
        RULE["Rule<br/>MatchFeatures: FeatureMatcher<br/>Labels, Taints, ExtendedResources"]
    end
    
    NODEFEATURE --> FEATURES
    NODEFEATURE --> LABELS
    FEATURES --> FLAGSET
    FEATURES --> ATTRSET
    FEATURES --> INSTSET
    NODEFEATURERULE --> RULES
    RULES --> RULE
```

**NFD CRD Structure**

**Sources:** [vendor/sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1/types.go:1-395]()

### NodeFeature Resource

The `NodeFeature` CRD holds discovered features for a single node:

```go
// Key types from vendor/sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1/types.go
type NodeFeature struct {
    metav1.TypeMeta
    metav1.ObjectMeta
    Spec NodeFeatureSpec
}

type NodeFeatureSpec struct {
    Features Features           // Raw feature data
    Labels   map[string]string  // Requested node labels
}

type Features struct {
    Flags      map[string]FlagFeatureSet      // Boolean features
    Attributes map[string]AttributeFeatureSet // String-valued features
    Instances  map[string]InstanceFeatureSet  // Multi-attribute features
}
```

**Sources:** [vendor/sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1/types.go:36-93]()

### NodeFeatureRule Resource

The `NodeFeatureRule` CRD defines feature-based node customization:

```go
type NodeFeatureRule struct {
    metav1.TypeMeta
    metav1.ObjectMeta
    Spec NodeFeatureRuleSpec
}

type NodeFeatureRuleSpec struct {
    Rules []Rule  // List of customization rules
}

type Rule struct {
    Name              string
    Labels            map[string]string
    Annotations       map[string]string
    Taints            []corev1.Taint
    ExtendedResources map[string]string
    MatchFeatures     FeatureMatcher
}
```

**Sources:** [vendor/sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1/types.go:99-253]()

### FeatureMatcher Pattern

The `FeatureMatcher` enables complex feature matching with operators:

| Operator | Description | Example Usage |
|----------|-------------|---------------|
| `MatchIn` | Value in set | CPU model in ["Xeon", "EPYC"] |
| `MatchNotIn` | Value not in set | GPU model not in ["Legacy"] |
| `MatchInRegexp` | Regex match | Model matches "^NVIDIA.*" |
| `MatchExists` | Feature present | GPU exists |
| `MatchGt`/`MatchLt` | Numeric comparison | Memory > 32GB |
| `MatchGtLt` | Range check | Cores between [8, 64] |

**Sources:** [vendor/sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1/types.go:261-381]()

### NodeFeatureGroup Resource

The `NodeFeatureGroup` CRD groups nodes by feature sets:

```go
type NodeFeatureGroup struct {
    metav1.TypeMeta
    metav1.ObjectMeta
    Spec   NodeFeatureGroupSpec
    Status NodeFeatureGroupStatus
}

type NodeFeatureGroupSpec struct {
    Rules []GroupRule  // Feature grouping rules
}

type NodeFeatureGroupStatus struct {
    Nodes []FeatureGroupNode  // Nodes matching the rules
}
```

**Sources:** [vendor/sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1/types.go:132-179]()

## Dynamic Resource Allocation API

The DRA API provides a framework for managing specialized hardware devices. The system uses k8s.io/api/resource/v1beta1 and v1alpha3 for device allocation.

### DRA Resource Types

```mermaid
graph TB
    subgraph "DRA v1beta1 API"
        RESOURCESLICE["ResourceSlice<br/>Spec: ResourceSliceSpec"]
        RESOURCECLAIM["ResourceClaim<br/>Spec: ResourceClaimSpec<br/>Status: ResourceClaimStatus"]
        DEVICECLASS["DeviceClass<br/>Spec: DeviceClassSpec"]
    end
    
    subgraph "ResourceSliceSpec"
        DRIVER["Driver: string"]
        POOL["Pool: ResourcePool"]
        DEVICES["Devices: []Device"]
        NODENAME["NodeName: string"]
        NODESELECTOR["NodeSelector: v1.NodeSelector"]
        SHAREDCOUNTERS["SharedCounters: []CounterSet"]
    end
    
    subgraph "Device Structure"
        DEVICENAME["Name: string"]
        BASIC["Basic: *BasicDevice"]
        BASICATTRS["Attributes: map[QualifiedName]DeviceAttribute"]
        BASICCAP["Capacity: map[QualifiedName]DeviceCapacity"]
        CONSUMES["ConsumesCounters: []DeviceCounterConsumption"]
        TAINTS["Taints: []DeviceTaint"]
    end
    
    RESOURCESLICE --> DRIVER
    RESOURCESLICE --> POOL
    RESOURCESLICE --> DEVICES
    RESOURCESLICE --> NODENAME
    RESOURCESLICE --> NODESELECTOR
    RESOURCESLICE --> SHAREDCOUNTERS
    DEVICES --> DEVICENAME
    DEVICES --> BASIC
    BASIC --> BASICATTRS
    BASIC --> BASICCAP
    BASIC --> CONSUMES
    BASIC --> TAINTS
```

**DRA Resource Architecture**

**Sources:** [vendor/k8s.io/api/resource/v1beta1/types.go:1-277]()

### ResourceSlice Specification

The `ResourceSlice` resource publishes available devices from a driver:

```go
type ResourceSlice struct {
    metav1.TypeMeta
    metav1.ObjectMeta
    Spec ResourceSliceSpec
}

type ResourceSliceSpec struct {
    Driver             string            // DRA driver name (DNS subdomain)
    Pool               ResourcePool      // Pool identification
    NodeName           string            // Node-local resources
    NodeSelector       *v1.NodeSelector  // Multi-node resources
    AllNodes           bool              // Cluster-wide resources
    Devices            []Device          // Device definitions (max 128)
    PerDeviceNodeSelection *bool         // Per-device node selection
    SharedCounters     []CounterSet      // Shared counter definitions
}

type ResourcePool struct {
    Name               string  // Pool identifier
    Generation         int64   // Change tracking
    ResourceSliceCount int64   // Total slices in pool
}
```

**Sources:** [vendor/k8s.io/api/resource/v1beta1/types.go:52-253]()

### Device Definition Structure

Each device in a `ResourceSlice` has attributes and capacities:

```go
type Device struct {
    Name  string        // Unique device name (DNS label)
    Basic *BasicDevice  // Device properties
}

type BasicDevice struct {
    Attributes       map[QualifiedName]DeviceAttribute  // Device attributes
    Capacity         map[QualifiedName]DeviceCapacity   // Device capacities
    ConsumesCounters []DeviceCounterConsumption         // Counter consumption
    NodeName         *string                            // Device location
    NodeSelector     *v1.NodeSelector                   // Device availability
    AllNodes         *bool                              // Cluster-wide device
    Taints           []DeviceTaint                      // Device taints
    BindsToNode      *bool                              // Node binding requirement
    BindingConditions      []string                     // Pre-binding conditions
    BindingFailureConditions []string                   // Binding failure indicators
    AllowMultipleAllocations *bool                      // Multi-allocation support
}

type DeviceAttribute struct {
    IntValue     *int64   // Integer attribute
    BoolValue    *bool    // Boolean attribute
    StringValue  *string  // String attribute (max 64 chars)
    VersionValue *string  // Semantic version (max 64 chars)
}

type DeviceCapacity struct {
    Value         resource.Quantity      // Total capacity
    RequestPolicy *CapacityRequestPolicy // Consumption policy
}
```

**Sources:** [vendor/k8s.io/api/resource/v1beta1/types.go:261-365]()

### Device Selection with CEL

DRA supports CEL expressions for device selection:

```go
type DeviceSelector struct {
    CEL *CELDeviceSelector  // CEL-based selection
}

type CELDeviceSelector struct {
    Expression string  // CEL expression (max 10 Ki, cost limit 1,000,000)
}
```

**CEL Expression Context:**
- `device.driver`: Driver name (string)
- `device.attributes["domain.com"]`: Grouped attributes (object)
- `device.capacity["domain.com"]`: Grouped capacities (object)
- `device.allowMultipleAllocations`: Multi-allocation flag (bool)

**Sources:** [vendor/k8s.io/api/resource/v1beta1/types.go:1-365](), [vendor/k8s.io/api/resource/v1alpha3/types.go:23-116]()

### Device Taints and Tolerations

DRA supports device-level taints for fine-grained scheduling:

```go
type DeviceTaint struct {
    Key       string            // Taint key (label name)
    Value     string            // Taint value (label value)
    Effect    DeviceTaintEffect // NoSchedule or NoExecute
    TimeAdded *metav1.Time      // Taint creation time
}

type DeviceTaintEffect string
const (
    DeviceTaintEffectNoSchedule DeviceTaintEffect = "NoSchedule"
    DeviceTaintEffectNoExecute  DeviceTaintEffect = "NoExecute"
)
```

**Sources:** [vendor/k8s.io/api/resource/v1alpha3/types.go:120-172]()

### DeviceTaintRule Resource

The `DeviceTaintRule` CRD applies taints to matching devices:

```go
type DeviceTaintRule struct {
    metav1.TypeMeta
    metav1.ObjectMeta
    Spec DeviceTaintRuleSpec
}

type DeviceTaintRuleSpec struct {
    DeviceSelector *DeviceTaintSelector  // Device matching criteria
    Taint          DeviceTaint           // Taint to apply
}

type DeviceTaintSelector struct {
    DeviceClassName *string          // Filter by device class
    Driver          *string          // Filter by driver
    Pool            *string          // Filter by pool
    Device          *string          // Filter by device name
    Selectors       []DeviceSelector // CEL-based filtering
}
```

**Sources:** [vendor/k8s.io/api/resource/v1alpha3/types.go:174-262]()

### Shared Counters and Partitionable Devices

DRA supports shared counters for tracking device usage across allocations:

```go
type CounterSet struct {
    Name     string              // Counter set name (DNS label)
    Counters map[string]Counter  // Named counters (max 32)
}

type Counter struct {
    Value resource.Quantity  // Available counter amount
}

type DeviceCounterConsumption struct {
    CounterSetName string                        // Reference to CounterSet
    Counters       map[string]resource.Quantity  // Consumed amounts
}
```

**Sources:** [vendor/k8s.io/api/resource/v1beta1/types.go:182-213]()

## DaemonSet Deployment and Host-Path Simulation

The `nvml-mock` component is deployed as a Kubernetes DaemonSet, ensuring that a mock NVML instance runs on every selected node. This deployment model is crucial for simulating GPU presence and behavior across the cluster.

### DaemonSet Configuration

The `nvml-mock` DaemonSet is defined via a Helm chart, allowing for flexible configuration. Key aspects include:

- **Node Selection**: The DaemonSet targets nodes based on specific labels, such as `nvidia.com/gpu.present: "true"`. This allows for selective deployment on nodes designated for GPU simulation.
- **Privileged Container**: The `nvml-mock` container runs in privileged mode (`securityContext.privileged: true`) [deployments/nvml-mock/helm/nvml-mock/tests/daemonset_test.yaml:110-114](). This is necessary to allow the mock library to interact with the host filesystem and simulate device files.
- **Entrypoint and Cleanup Scripts**: The container executes an `entrypoint.sh` script on startup and a `cleanup.sh` script on preStop [deployments/nvml-mock/helm/nvml-mock/tests/daemonset_test.yaml:117-127](). These scripts are responsible for setting up and tearing down the host environment for NVML mocking.
- **Environment Variables**: Numerous environment variables configure the mock behavior, including `GPU_COUNT`, `DRIVER_VERSION`, `MOCK_NFD_PCI_LABEL`, `MOCK_NVML_CONFIG`, and `LD_PRELOAD` [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap:32-70](). These variables control the number of simulated GPUs, driver version, NFD integration, mock NVML configuration, and library preloading for interception.

### Host-Path Simulation

A core aspect of `nvml-mock`'s integration is its use of `hostPath` volumes to simulate the presence of GPU-related files and directories on the host filesystem. This allows other components, such as the NVIDIA Container Toolkit or Node Feature Discovery, to interact with the mock environment as if real GPUs were present.

```mermaid
graph TD
    subgraph "Kubernetes Node"
        KUBELET["Kubelet"]
        CONTAINERD["Containerd"]
        NVIDIA_CDI_HOOK["NVIDIA CDI Hook"]
        NFD_WORKER["NFD Worker"]
    end

    subgraph "nvml-mock DaemonSet Pod"
        NVML_MOCK_CONTAINER["nvml-mock Container"]
        ENTRYPOINT_SH["/scripts/entrypoint.sh"]
        CLEANUP_SH["/scripts/cleanup.sh"]
    end

    subgraph "Host Filesystem (Simulated)"
        HOST_VAR_LIB_NVML_MOCK["/var/lib/nvml-mock"]
        HOST_VAR_RUN_CDI["/var/run/cdi"]
        HOST_RUN_NVIDIA["/run/nvidia"]
        HOST_NFD_FEATURES["/etc/kubernetes/node-feature-discovery/features.d"]
    end

    KUBELET -- Manages --> NVML_MOCK_CONTAINER
    NVML_MOCK_CONTAINER -- Runs --> ENTRYPOINT_SH
    NVML_MOCK_CONTAINER -- Runs on termination --> CLEANUP_SH

    ENTRYPOINT_SH -- Creates/Modifies --> HOST_VAR_LIB_NVML_MOCK
    ENTRYPOINT_SH -- Creates/Modifies --> HOST_VAR_RUN_CDI
    ENTRYPOINT_SH -- Creates/Modifies --> HOST_RUN_NVIDIA
    ENTRYPOINT_SH -- Creates/Modifies --> HOST_NFD_FEATURES

    CLEANUP_SH -- Cleans up --> HOST_VAR_LIB_NVML_MOCK
    CLEANUP_SH -- Cleans up --> HOST_VAR_RUN_CDI
    CLEANUP_SH -- Cleans up --> HOST_RUN_NVIDIA
    CLEANUP_SH -- Cleans up --> HOST_NFD_FEATURES

    NVML_MOCK_CONTAINER -- Mounts hostPath --> HOST_VAR_LIB_NVML_MOCK
    NVML_MOCK_CONTAINER -- Mounts hostPath --> HOST_VAR_RUN_CDI
    NVML_MOCK_CONTAINER -- Mounts hostPath --> HOST_RUN_NVIDIA
    NVML_MOCK_CONTAINER -- Mounts hostPath --> HOST_NFD_FEATURES

    NVIDIA_CDI_HOOK -- Reads --> HOST_VAR_RUN_CDI
    NFD_WORKER -- Reads --> HOST_NFD_FEATURES
    CONTAINERD -- Uses --> NVIDIA_CDI_HOOK
```

**DaemonSet and Host-Path Simulation Architecture**

**Key `hostPath` Volumes:**

- `/var/lib/nvml-mock`: This directory serves as the root for various mock-related files, including the mock NVML library itself, configuration files, and state directories for fabric simulation [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap:98-101, 121-124]().
- `/var/run/cdi`: This path is used for NVIDIA Container Device Interface (CDI) files. The `nvml-mock` container creates CDI specification files here, which are then consumed by the NVIDIA CDI hook to inject mock devices into containers [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap:104-105, 128-131]().
- `/run/nvidia`: This directory is typically where NVIDIA driver components and device files reside. `nvml-mock` uses this to simulate the presence of NVIDIA-specific runtime files [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap:106-107, 132-135]().
- `/etc/kubernetes/node-feature-discovery/features.d`: This is where NFD expects feature files. The `entrypoint.sh` script writes a `pci-10de.feature` file here, which NFD then processes to add `nvidia.com/gpu` labels to the node [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap:108-109, 136-139](). The `MOCK_NFD_PCI_LABEL` environment variable controls whether this feature file is created [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap:40-41]().

The `DirectoryOrCreate` type for `hostPath` volumes ensures that these directories are created on the host if they do not already exist, facilitating a clean setup for the mock environment [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap:121-143]().

**Sources:**
- [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap:3-147]()
- [deployments/nvml-mock/helm/nvml-mock/tests/daemonset_test.yaml:110-114]()
- [deployments/nvml-mock/helm/nvml-mock/tests/daemonset_test.yaml:117-127]()
- [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap:32-70]()
- [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap:98-101]()
- [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap:121-124]()
- [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap:104-105]()
- [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap:128-131]()
- [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap:106-107]()
- [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap:132-135]()
- [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap:108-109]()
- [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap:136-139]()
- [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap:40-41]()
- [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap:121-143]()

## Supporting Utilities

### Certificate Generation

The system includes utilities for generating self-signed certificates for testing secure Kubernetes components:

```mermaid
graph LR
    subgraph "k8s.io/client-go/util/cert"
        SELFSIGNED["GenerateSelfSignedCertKey<br/>cert.go:117-126"]
        WITHOPTS["GenerateSelfSignedCertKeyWithOptions<br/>cert.go:145-268"]
        CACERT["NewSelfSignedCACert<br/>cert.go:59-93"]
    end
    
    subgraph "SelfSignedCertKeyOptions"
        HOST["Host: string"]
        ALTIPS["AlternateIPs: []net.IP"]
        ALTDNS["AlternateDNS: []string"]
        MAXAGE["MaxAge: time.Duration"]
        FIXTURE["FixtureDirectory: string"]
    end
    
    subgraph "Output"
        CERTPEM["Certificate PEM []byte"]
        KEYPEM["Key PEM []byte"]
    end
    
    SELFSIGNED --> WITHOPTS
    WITHOPTS --> CERTPEM
    WITHOPTS --> KEYPEM
    WITHOPTS --> HOST
    WITHOPTS --> ALTIPS
    WITHOPTS --> ALTDNS
    WITHOPTS --> MAXAGE
    WITHOPTS --> FIXTURE
    CACERT --> CERTPEM
```

**Certificate Generation Utilities**

**Key Functions:**

| Function | Signature | Purpose |
|----------|-----------|---------|
| `GenerateSelfSignedCertKey` | `(host string, alternateIPs []net.IP, alternateDNS []string) ([]byte, []byte, error)` | Generate cert/key pair with defaults |
| `GenerateSelfSignedCertKeyWithOptions` | `(opts SelfSignedCertKeyOptions) ([]byte, []byte, error)` | Generate cert/key with custom options |
| `NewSelfSignedCACert` | `(cfg Config, key crypto.Signer) (*x509.Certificate, error)` | Create CA certificate |

**Default Behavior:**
- Validity period: 365 days (1 year)
- Valid from: 1 hour before generation (clock skew tolerance)
- Certificate type: RSA 2048-bit
- Extensions: SubjectAltNames for IPs and DNS names

**Sources:** [vendor/k8s.io/client-go/util/cert/cert.go:117-276]()

### YAML and JSON Manifest Processing

The system provides utilities for loading and decoding Kubernetes manifests from YAML or JSON:

```mermaid
graph TB
    subgraph "k8s.io/apimachinery/pkg/util/yaml"
        YAMLORJSON["YAMLOrJSONDecoder<br/>decoder.go:249-358"]
        YAMLTOJSON["YAMLToJSONDecoder<br/>decoder.go:106-143"]
        YAMLDECODER["YAMLDecoder<br/>decoder.go:147-205"]
        GUESSJSON["GuessJSONStream<br/>decoder.go:466-470"]
    end
    
    subgraph "Decoding Methods"
        DECODE["Decode(into interface{}) error"]
        UNMARSHAL["Unmarshal(data []byte, v interface{}) error"]
        TOJSON["ToJSON(data []byte) ([]byte, error)"]
    end
    
    subgraph "Document Splitting"
        SPLITDOC["splitYAMLDocument<br/>decoder.go:211-238"]
        YAMLREADER["YAMLReader<br/>decoder.go:393-439"]
        LINEREADER["LineReader<br/>decoder.go:441-461"]
    end
    
    YAMLORJSON --> DECODE
    YAMLTOJSON --> DECODE
    YAMLORJSON --> GUESSJSON
    YAMLORJSON --> YAMLTOJSON
    YAMLDECODER --> SPLITDOC
    YAMLREADER --> LINEREADER
```

**YAML/JSON Decoding Architecture**

**Key Types:**

```go
// YAMLOrJSONDecoder attempts to decode YAML or JSON from a stream
type YAMLOrJSONDecoder struct {
    json         *json.Decoder
    jsonConsumed int64
    yaml         *YAMLToJSONDecoder
    yamlConsumed int64
    stream       *StreamReader
    count        int
}

// NewYAMLOrJSONDecoder creates a decoder that handles both formats
func NewYAMLOrJSONDecoder(r io.Reader, bufferSize int) *YAMLOrJSONDecoder

// Decode unmarshals the next object from the stream
func (d *YAMLOrJSONDecoder) Decode(into interface{}) error
```

**Decoding Strategy:**
1. Detect format by looking for JSON opening brace `{`
2. Try JSON decoding first if detected
3. Fall back to YAML if JSON fails and count ≤ 1
4. Use YAML exclusively after first successful YAML decode

**Document Separation:**
- YAML documents separated by `---` on a line
- JSON documents separated by whitespace between objects
- Buffers content to handle incomplete reads

**Sources:** [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:1-486]()

### Utility Functions

| Function | Purpose | Location |
|----------|---------|----------|
| `Unmarshal` | Unmarshal YAML/JSON with number preservation | [decoder.go:38-62]() |
| `UnmarshalStrict` | Strict unmarshaling (error on duplicates) | [decoder.go:64-90]() |
| `ToJSON` | Convert YAML document to JSON | [decoder.go:92-101]() |
| `IsJSONBuffer` | Check if buffer starts with `{` | [decoder.go:474-476]() |
| `NewDocumentDecoder` | Split multi-document YAML stream | [decoder.go:158-169]() |

**Sources:** [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:35-486]()

## Integration Patterns

### Resource Lifecycle Management

```mermaid
sequenceDiagram
    participant Test as Test Suite
    participant Client as client-go Clientset
    participant API as Kubernetes API
    participant NFD as NFD Controller
    participant DRA as DRA Driver
    
    Note over Test,API: Create Test Resources
    Test->>Client: Create(NodeFeature)
    Client->>API: POST /apis/nfd.k8s.io/v1alpha1/nodefeatures
    API->>NFD: Watch notification
    
    Note over NFD,API: NFD Processing
    NFD->>API: Update Node labels
    NFD->>API: Create NodeFeatureRule
    
    Note over Test,DRA: Device Publication
    DRA->>API: Create ResourceSlice
    Test->>Client: Watch(ResourceSlice)
    Client->>Test: ResourceSlice added event
    
    Note over Test,API: Validation
    Test->>Client: Get(NodeFeature)
    Client->>API: GET /apis/nfd.k8s.io/v1alpha1/nodefeatures/{name}
    API->>Client: NodeFeature object
    Client->>Test: NodeFeature data
    
    Note over Test,API: Cleanup
    Test->>Client: Delete(NodeFeature)
    Client->>API: DELETE /apis/nfd.k8s.io/v1alpha1/nodefeatures/{name}
```

**Resource Lifecycle in Tests**

**Sources:** [go.mod:5-16](), [vendor/modules.txt:239-549]()

### Watch Pattern for Asynchronous Updates

The system uses watches to observe resource changes asynchronously:

```go
// Watch pattern for NFD resources
watcher, err := client.Watch(ctx, metav1.ListOptions{
    FieldSelector: "metadata.name=" + name,
})
defer watcher.Stop()

for event := range watcher.ResultChan() {
    switch event.Type {
    case watch.Added:
        // Handle resource creation
    case watch.Modified:
        // Handle resource update
    case watch.Deleted:
        // Handle resource deletion
    }
}
```

**Sources:** [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:1-486](), [vendor/modules.txt:361-362]()

## Version Compatibility

| Component | Version | API Stability |
|-----------|---------|---------------|
| client-go | v0.34.2 | Stable |
| NFD API | v0.18.3 | v1alpha1 (Alpha) |
| DRA API | - | v1beta1 (Beta), v1alpha3 (Alpha) |
| Kubernetes API | v0.34.2 | Mixed (varies by resource) |

**Alpha/Beta Considerations:**
- v1alpha1 APIs may change without notice
- v1beta1 APIs are more stable but may still evolve
- Test code must handle API evolution
- Feature gates control access to alpha features (e.g., `DRAPartitionableDevices`, `DRADeviceTaints`)

**Sources:** [go.mod:1-16](), [vendor/k8s.io/api/resource/v1beta1/types.go:1-100]()

---

# Page: Testing Infrastructure Design

# Testing Infrastructure Design

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/nvml-mock-e2e-go.yaml](.github/workflows/nvml-mock-e2e-go.yaml)
- [Makefile](Makefile)
- [README.md](README.md)
- [go.mod](go.mod)
- [go.sum](go.sum)
- [tests/e2e/README.md](tests/e2e/README.md)
- [tests/e2e/VERSION-MATRIX.md](tests/e2e/VERSION-MATRIX.md)
- [tests/e2e/go/assertions/resources.go](tests/e2e/go/assertions/resources.go)
- [tests/e2e/go/e2e_suite_test.go](tests/e2e/go/e2e_suite_test.go)
- [tests/e2e/go/framework/config/config.go](tests/e2e/go/framework/config/config.go)
- [tests/e2e/go/framework/harness/harness.go](tests/e2e/go/framework/harness/harness.go)
- [tests/e2e/go/framework/helm/helm.go](tests/e2e/go/framework/helm/helm.go)
- [tests/e2e/go/framework/helm/helm_test.go](tests/e2e/go/framework/helm/helm_test.go)
- [tests/e2e/go/framework/kube/kube.go](tests/e2e/go/framework/kube/kube.go)
- [tests/e2e/go/suite_cluster.go](tests/e2e/go/suite_cluster.go)
- [tests/e2e/go/suite_helm.go](tests/e2e/go/suite_helm.go)
- [vendor/github.com/onsi/ginkgo/v2/CHANGELOG.md](vendor/github.com/onsi/ginkgo/v2/CHANGELOG.md)
- [vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go](vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go)
- [vendor/github.com/onsi/ginkgo/v2/types/version.go](vendor/github.com/onsi/ginkgo/v2/types/version.go)
- [vendor/k8s.io/apimachinery/pkg/api/validation/objectmeta.go](vendor/k8s.io/apimachinery/pkg/api/validation/objectmeta.go)
- [vendor/modules.txt](vendor/modules.txt)

</details>



## Purpose and Scope

This document describes the testing infrastructure design used in the k8s-test-infra repository. It covers the BDD (Behavior-Driven Development) testing approach using Ginkgo and Gomega, test organization patterns, execution models, and reporting mechanisms. The focus is on the framework-level design decisions and how tests are structured and executed.

For information about specific Ginkgo features and usage patterns, see [Testing with Ginkgo](#5). For details about Kubernetes client operations used in tests, see [Kubernetes Integration Layer](#3.2). Build system integration with testing is covered in [Build System](#8).

---

## Core Testing Framework

The repository uses **Ginkgo v2.32.0** as the primary testing framework with **Gomega v1.42.1** for assertions. This combination provides a BDD-style testing experience with expressive matchers and comprehensive reporting capabilities.

### Framework Components

```mermaid
graph TB
    subgraph "Ginkgo Framework"
        Suite["Suite<br/>internal.Suite"]
        Node["Node<br/>internal.Node"]
        Failer["Failer<br/>internal.Failer"]
        SpecContext["SpecContext<br/>internal.SpecContext"]
    end
    
    subgraph "Test Organization"
        Describe["Describe()<br/>Container Node"]
        Context["Context()<br/>Container Node"]
        It["It()<br/>Subject Node"]
        BeforeEach["BeforeEach()<br/>Setup Node"]
        AfterEach["AfterEach()<br/>Teardown Node"]
    end
    
    subgraph "Assertions"
        Expect["Expect()<br/>Gomega"]
        Eventually["Eventually()<br/>Async Matcher"]
        Matchers["Matchers<br/>BeTrue(), Equal(), etc."]
    end
    
    subgraph "Execution Control"
        RunSpecs["RunSpecs()<br/>Entry Point"]
        SuiteConfig["types.SuiteConfig<br/>Parallelization, Timeout"]
        ReporterConfig["types.ReporterConfig<br/>Verbosity, Output"]
    end
    
    Suite --> Node
    Suite --> Failer
    Suite --> SpecContext
    
    RunSpecs --> Suite
    RunSpecs --> SuiteConfig
    RunSpecs --> ReporterConfig
    
    Describe --> Node
    Context --> Node
    It --> Node
    BeforeEach --> Node
    AfterEach --> Node
    
    It --> Expect
    Expect --> Matchers
    Eventually --> Matchers
```

Sources:
- [go.mod:8-9]()
- [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:25-71]()
- [vendor/github.com/onsi/ginkgo/v2/internal/node.go:27-70]()
- [vendor/github.com/onsi/ginkgo/v2/core_dsl.go:260-331]()

### Key Framework Types

| Type | Location | Purpose |
|------|----------|---------|
| `internal.Suite` | [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:25]() | Manages test tree, execution lifecycle, and reporting |
| `internal.Node` | [vendor/github.com/onsi/ginkgo/v2/internal/node.go:27]() | Represents a single node in the test tree (container or subject) |
| `types.SpecReport` | [vendor/github.com/onsi/ginkgo/v2/types/types.go:100]() | Contains detailed information about a spec execution |
| `types.Report` | [vendor/github.com/onsi/ginkgo/v2/types/types.go:20]() | Aggregated report for entire suite |
| `SpecContext` | [vendor/github.com/onsi/ginkgo/v2/dsl/core_dsl.go:101]() | Context passed to interruptible nodes |

Sources:
- [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:25-96]()
- [vendor/github.com/onsi/ginkgo/v2/internal/node.go:27-70]()
- [vendor/github.com/onsi/ginkgo/v2/types/types.go:20-200]()

---

## Test Organization Patterns

### BDD Structure with Describe/Context/It

Ginkgo organizes tests in a hierarchical tree structure using BDD-style blocks:

```mermaid
graph TB
    Root["TreeNode<br/>Root Container"]
    
    Describe1["Describe<br/>'Feature X'<br/>NodeTypeContainer"]
    Context1["Context<br/>'when condition Y'<br/>NodeTypeContainer"]
    It1["It<br/>'should behave Z'<br/>NodeTypeIt"]
    It2["It<br/>'should not W'<br/>NodeTypeIt"]
    
    Describe2["Describe<br/>'Feature A'<br/>NodeTypeContainer"]
    BeforeEach1["BeforeEach<br/>Setup<br/>NodeTypeBeforeEach"]
    It3["It<br/>'works'<br/>NodeTypeIt"]
    
    Root --> Describe1
    Root --> Describe2
    Describe1 --> Context1
    Context1 --> It1
    Context1 --> It2
    Describe2 --> BeforeEach1
    Describe2 --> It3
    
    style It1 fill:#f9f9f9
    style It2 fill:#f9f9f9
    style It3 fill:#f9f9f9
```

Sources:
- [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:98-228]()
- [vendor/github.com/onsi/ginkgo/v2/internal/node.go:214-228]()

### Node Types and Decorators

```mermaid
graph LR
    subgraph "Container Nodes"
        Describe["Describe/Context<br/>NodeTypeContainer"]
        Ordered["Ordered Container<br/>MarkedOrdered=true"]
    end
    
    subgraph "Subject Nodes"
        It["It<br/>NodeTypeIt"]
        Focus["FIt<br/>MarkedFocus=true"]
        Pending["PIt<br/>MarkedPending=true"]
    end
    
    subgraph "Setup Nodes"
        BeforeEach["BeforeEach<br/>NodeTypeBeforeEach"]
        AfterEach["AfterEach<br/>NodeTypeAfterEach"]
        BeforeAll["BeforeAll<br/>NodeTypeBeforeAll"]
        AfterAll["AfterAll<br/>NodeTypeAfterAll"]
    end
    
    subgraph "Suite Nodes"
        BeforeSuite["BeforeSuite<br/>NodeTypeBeforeSuite"]
        AfterSuite["AfterSuite<br/>NodeTypeAfterSuite"]
    end
    
    subgraph "Decorators"
        Labels["Label()<br/>internal.Labels"]
        Serial["Serial<br/>MarkedSerial=true"]
        Timeout["NodeTimeout<br/>time.Duration"]
        FlakeAttempts["FlakeAttempts<br/>int"]
    end
    
    Describe --> Labels
    Describe --> Ordered
    It --> Focus
    It --> Pending
    It --> Serial
    It --> Timeout
    It --> FlakeAttempts
```

**Node Type Constants:**
- `NodeTypeContainer`: Describe/Context blocks
- `NodeTypeIt`: Individual test specs
- `NodeTypeBeforeEach`/`NodeTypeAfterEach`: Per-spec setup/teardown
- `NodeTypeBeforeAll`/`NodeTypeAfterAll`: Per-ordered-container setup/teardown
- `NodeTypeBeforeSuite`/`NodeTypeAfterSuite`: Suite-level setup/teardown

Sources:
- [vendor/github.com/onsi/ginkgo/v2/internal/node.go:27-70]()
- [vendor/github.com/onsi/ginkgo/v2/internal/node.go:72-98]()
- [vendor/github.com/onsi/ginkgo/v2/internal/node.go:214-499]()

### Table-Driven Tests

Ginkgo provides `DescribeTable` for generating multiple specs from tabular data:

```mermaid
graph TB
    DescribeTable["DescribeTable()<br/>table_dsl.go:47"]
    Entry["Entry()<br/>TableEntry"]
    TableBody["Table Body Function<br/>func(params...)"]
    
    DescribeTable --> Entry1["Entry 1<br/>parameters..."]
    DescribeTable --> Entry2["Entry 2<br/>parameters..."]
    DescribeTable --> EntryN["Entry N<br/>parameters..."]
    
    Entry1 --> TableBody
    Entry2 --> TableBody
    EntryN --> TableBody
    
    TableBody --> It1["Generated It<br/>description 1"]
    TableBody --> It2["Generated It<br/>description 2"]
    TableBody --> ItN["Generated It<br/>description N"]
    
    subgraph "Entry Description"
        EntryDesc["EntryDescription<br/>Format String"]
        CustomFunc["Custom Function<br/>func(params...) string"]
    end
    
    Entry1 --> EntryDesc
    Entry2 --> CustomFunc
```

**Key Functions:**
- `DescribeTable(description string, args ...any)`: Defines a table test
- `Entry(description any, args ...any)`: Single table entry
- `FEntry()`: Focused entry
- `PEntry()`: Pending entry
- `DescribeTableSubtree()`: Generates container nodes instead of It nodes

Sources:
- [vendor/github.com/onsi/ginkgo/v2/dsl/table_dsl.go:47-76]()
- [vendor/github.com/onsi/ginkgo/v2/dsl/table_dsl.go:112-141]()
- [vendor/github.com/onsi/ginkgo/v2/dsl/table_dsl.go:164-194]()
- [vendor/github.com/onsi/ginkgo/v2/dsl/table_dsl.go:199-317]()

---

## Test Execution Model

### Suite Lifecycle

```mermaid
stateDiagram-v2
    [*] --> PhaseBuildTopLevel
    
    PhaseBuildTopLevel: Phase: BuildTopLevel<br/>Collect top-level containers
    PhaseBuildTree: Phase: BuildTree<br/>Construct spec tree
    PhaseRun: Phase: Run<br/>Execute specs
    
    PhaseBuildTopLevel --> PhaseBuildTree: BuildTree()
    PhaseBuildTree --> PhaseRun: Run()
    
    state PhaseRun {
        [*] --> SuiteWillBegin
        SuiteWillBegin --> BeforeSuite
        BeforeSuite --> RunSpecs
        RunSpecs --> AfterSuite
        AfterSuite --> ReportAfterSuite
        ReportAfterSuite --> SuiteDidEnd
        SuiteDidEnd --> [*]
        
        state RunSpecs {
            [*] --> BeforeEach
            BeforeEach --> SpecBody
            SpecBody --> AfterEach
            AfterEach --> [*]
        }
    }
    
    PhaseRun --> [*]
```

**Phase Enum:**
```go
const (
    PhaseBuildTopLevel Phase = iota
    PhaseBuildTree
    PhaseRun
)
```

Sources:
- [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:15-21]()
- [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:98-109]()
- [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:111-141]()

### Configuration Types

| Type | Purpose | Key Fields |
|------|---------|-----------|
| `types.SuiteConfig` | Controls suite execution behavior | `RandomSeed`, `ParallelTotal`, `ParallelProcess`, `Timeout`, `LabelFilter` |
| `types.ReporterConfig` | Controls output and reporting | `Verbosity`, `NoColor`, `JSONReport`, `JUnitReport`, `FullTrace` |

**Configuration Access:**
- `GinkgoConfiguration()`: Returns current `(SuiteConfig, ReporterConfig)`
- `RunSpecs(t, description, suiteConfig, reporterConfig)`: Accepts custom configuration

Sources:
- [vendor/github.com/onsi/ginkgo/v2/dsl/core_dsl.go:39-41]()
- [vendor/github.com/onsi/ginkgo/v2/dsl/core_dsl.go:139-141]()
- [vendor/github.com/onsi/ginkgo/v2/dsl/core_dsl.go:260-331]()

### Parallel Execution

```mermaid
graph TB
    subgraph "Process 1"
        P1Suite["Suite Instance"]
        P1Client["parallel_support.Client"]
        P1Specs["Assigned Specs"]
    end
    
    subgraph "Process 2"
        P2Suite["Suite Instance"]
        P2Client["parallel_support.Client"]
        P2Specs["Assigned Specs"]
    end
    
    subgraph "Process N"
        PNSuite["Suite Instance"]
        PNClient["parallel_support.Client"]
        PNSpecs["Assigned Specs"]
    end
    
    ParallelHost["Parallel Coordinator<br/>--parallel-host"]
    
    P1Client --> ParallelHost
    P2Client --> ParallelHost
    PNClient --> ParallelHost
    
    ParallelHost --> AggregatedReport["Aggregated Report"]
    
    P1Suite --> P1Client
    P2Suite --> P2Client
    PNSuite --> PNClient
```

**Parallel Configuration:**
- `suiteConfig.ParallelTotal`: Total number of parallel processes
- `suiteConfig.ParallelProcess`: Current process number (1-indexed)
- `suiteConfig.ParallelHost`: Coordinator host address

Sources:
- [vendor/github.com/onsi/ginkgo/v2/dsl/core_dsl.go:156-164]()
- [vendor/github.com/onsi/ginkgo/v2/dsl/core_dsl.go:274-294]()
- [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:70-71]()

---

## Reporting Infrastructure

### Reporter Architecture

```mermaid
graph TB
    subgraph "Reporter Interface"
        Reporter["reporters.Reporter<br/>Interface"]
        SuiteWillBegin["SuiteWillBegin(Report)"]
        WillRun["WillRun(SpecReport)"]
        DidRun["DidRun(SpecReport)"]
        SuiteDidEnd["SuiteDidEnd(Report)"]
    end
    
    subgraph "Default Reporter"
        DefaultReporter["reporters.DefaultReporter"]
        Formatter["formatter.Formatter"]
        Writer["io.Writer"]
        
        Timeline["Timeline Rendering"]
        ProgressReport["Progress Reports"]
        FailureSummary["Failure Summary"]
    end
    
    subgraph "Report Nodes"
        ReportBeforeEach["ReportBeforeEach<br/>func(SpecReport)"]
        ReportAfterEach["ReportAfterEach<br/>func(SpecReport)"]
        ReportAfterSuite["ReportAfterSuite<br/>func(Report)"]
    end
    
    subgraph "Generated Reports"
        JSONReport["JSON Report<br/>--json-report"]
        JUnitReport["JUnit XML<br/>--junit-report"]
        TeamcityReport["Teamcity Report<br/>--teamcity-report"]
    end
    
    Reporter --> DefaultReporter
    DefaultReporter --> Formatter
    DefaultReporter --> Writer
    
    DefaultReporter --> Timeline
    DefaultReporter --> ProgressReport
    DefaultReporter --> FailureSummary
    
    Reporter --> ReportBeforeEach
    Reporter --> ReportAfterEach
    Reporter --> ReportAfterSuite
    
    ReportAfterSuite --> JSONReport
    ReportAfterSuite --> JUnitReport
    ReportAfterSuite --> TeamcityReport
```

Sources:
- [vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go:22-65]()
- [vendor/github.com/onsi/ginkgo/v2/dsl/reporting_dsl.go:118-208]()
- [vendor/github.com/onsi/ginkgo/v2/dsl/reporting_dsl.go:210-259]()

### Report Types

**SpecReport Structure:**
```go
type SpecReport struct {
    ContainerHierarchyTexts   []string
    LeafNodeText              string
    State                     SpecState
    RunTime                   time.Duration
    Failure                   Failure
    CapturedGinkgoWriterOutput string
    ReportEntries             []ReportEntry
    NumAttempts               int
    MaxFlakeAttempts          int
    // ... more fields
}
```

**Report Structure:**
```go
type Report struct {
    SuiteDescription          string
    SuiteSucceeded            bool
    SpecReports               SpecReports
    PreRunStats               PreRunStats
    RunTime                   time.Duration
    SuiteConfig               SuiteConfig
    // ... more fields
}
```

Sources:
- [vendor/github.com/onsi/ginkgo/v2/types/types.go:100-199]()
- [vendor/github.com/onsi/ginkgo/v2/types/types.go:20-98]()

### Timeline and Progress Reporting

The `DefaultReporter` generates a timeline view showing the chronological flow of a spec:

```mermaid
graph LR
    subgraph "Timeline Components"
        SpecEvent["SpecEvent<br/>Enter/Exit Nodes"]
        ReportEntry["ReportEntry<br/>User Data"]
        Failure["Failure<br/>Assertion Failures"]
        ProgressReport["ProgressReport<br/>Goroutine State"]
        GinkgoWriter["GinkgoWriter Output<br/>Interleaved"]
    end
    
    Timeline["Timeline<br/>types.Timeline"]
    
    SpecEvent --> Timeline
    ReportEntry --> Timeline
    Failure --> Timeline
    ProgressReport --> Timeline
    GinkgoWriter --> Timeline
    
    Timeline --> Rendered["Rendered Output<br/>-v or -vv"]
```

**Timeline Location:**
Each timeline entry has a `TimelineLocation`:
- `Offset`: Position in `GinkgoWriter` output
- `Order`: Sequential ordering
- `Time`: Timestamp

Sources:
- [vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go:378-426]()
- [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:284-294]()

### Report Entries

Custom data can be attached to specs using `AddReportEntry()`:

```go
AddReportEntry(name string, args ...any)
```

**Visibility Levels:**
- `ReportEntryVisibilityAlways`: Always shown
- `ReportEntryVisibilityFailureOrVerbose`: Shown on failure or with `-v`
- `ReportEntryVisibilityNever`: Only in machine-readable reports

Sources:
- [vendor/github.com/onsi/ginkgo/v2/dsl/reporting_dsl.go:66-100]()

---

## E2E Harness Architecture

The End-to-End (E2E) testing harness, located under `tests/e2e/go/`, is responsible for managing the entire lifecycle of the test environment, from cluster creation to diagnostics collection. It uses Ginkgo for test orchestration and Gomega for assertions.

### Harness Overview

The `harness.Harness` struct [tests/e2e/go/framework/harness/harness.go]() encapsulates the necessary clients and configurations for interacting with the Kubernetes cluster and external tools.

```mermaid
graph TD
    Harness["harness.Harness"]
    
    KubeClient["KubeClient<br/>*kube.Client"]
    HelmClient["HelmClient<br/>*helm.Client"]
    KindClient["KindClient<br/>*kind.Client"]
    Config["Config<br/>*config.Config"]
    
    Harness --> KubeClient
    Harness --> HelmClient
    Harness --> KindClient
    Harness --> Config
    
    subgraph "Harness Responsibilities"
        ClusterLifecycle["Cluster Lifecycle Management<br/>(Kind create/delete)"]
        ImageManagement["Image Management<br/>(Build/Load to Kind)"]
        HelmDeployment["Helm Chart Deployment<br/>(nvml-mock)"]
        TestExecution["Ginkgo Test Execution"]
        DiagnosticsCollection["Diagnostics Collection<br/>(collectOnFailure)"]
    end
    
    ClusterLifecycle --> Harness
    ImageManagement --> Harness
    HelmDeployment --> Harness
    TestExecution --> Harness
    DiagnosticsCollection --> Harness
```

Sources:
- [tests/e2e/go/framework/harness/harness.go]()
- [tests/e2e/README.md:14-23]()

### Cluster Lifecycle Management

The E2E harness uses `kind` (Kubernetes in Docker) to provision and manage test clusters.

```mermaid
graph TD
    StartSuite["e2e_suite_test.go<br/>BeforeSuite"]
    
    BuildNvmlMockImage["Build nvml-mock Image<br/>(suite_build.go)"]
    CreateKindCluster["Create Kind Cluster<br/>(suite_cluster.go)"]
    LoadImageToKind["Load Image to Kind<br/>(suite_cluster.go)"]
    InstallHelmChart["Install nvml-mock Helm Chart<br/>(suite_helm.go)"]
    
    RunTests["Ginkgo Test Specs"]
    
    CollectDiagnostics["Collect Diagnostics<br/>(suite_cluster.go)"]
    DeleteKindCluster["Delete Kind Cluster<br/>(suite_cluster.go)"]
    
    EndSuite["e2e_suite_test.go<br/>AfterSuite"]
    
    StartSuite --> BuildNvmlMockImage
    BuildNvmlMockImage --> CreateKindCluster
    CreateKindCluster --> LoadImageToKind
    LoadImageToKind --> InstallHelmChart
    InstallHelmChart --> RunTests
    RunTests --> CollectDiagnostics
    CollectDiagnostics --> DeleteKindCluster
    DeleteKindCluster --> EndSuite
    
    style BuildNvmlMockImage fill:#f9f9f9,stroke:#333,stroke-width:2px
    style CreateKindCluster fill:#f9f9f9,stroke:#333,stroke-width:2px
    style LoadImageToKind fill:#f9f9f9,stroke:#333,stroke-width:2px
    style InstallHelmChart fill:#f9f9f9,stroke:#333,stroke-width:2px
    style CollectDiagnostics fill:#f9f9f9,stroke:#333,stroke-width:2px
    style DeleteKindCluster fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Key Steps:**
1.  **Image Build**: The `suite_build.go` logic handles building the `nvml-mock` Docker image. This step can be skipped if `E2E_SKIP_BUILD=true` and `E2E_IMAGE` is provided, which is common in CI workflows where the image is pre-built and pushed to an ephemeral registry like `ttl.sh`. [tests/e2e/go/suite_build.go]()
2.  **Cluster Creation**: `make cluster-create` (invoked by the harness) creates a Kind cluster using a custom node image (`kind-node-nv:latest`) that includes the `nvidia-container-toolkit`. The cluster configuration is defined in `local/kind/*.kind.yaml`. [Makefile:136-137]()
3.  **Image Loading**: The built `nvml-mock` image is loaded into the Kind cluster nodes.
4.  **Helm Deployment**: The `nvml-mock` Helm chart is installed or upgraded using `h.Helm.UpgradeInstall()` [tests/e2e/go/suite_helm.go:44](). This deploys the mock NVML DaemonSet and related components.
5.  **Diagnostics**: On test failure, `collectOnFailure` (implemented in `suite_cluster.go`) gathers logs and other artifacts from the cluster for debugging. [tests/e2e/go/suite_cluster.go]()
6.  **Teardown**: By default, the Kind cluster is kept for post-test debugging. It can be explicitly deleted by setting `E2E_KEEP_CLUSTER=false` or by running `make cluster-delete`. [tests/e2e/README.md:56-57]()

Sources:
- [tests/e2e/go/e2e_suite_test.go]()
- [tests/e2e/go/suite_build.go]()
- [tests/e2e/go/suite_cluster.go]()
- [tests/e2e/go/suite_helm.go]()
- [tests/e2e/README.md:14-23]()
- [Makefile:136-137]()
- [.github/workflows/nvml-mock-e2e-go.yaml:72-73]()

### Parallel Test Execution

The E2E tests leverage Ginkgo's parallel execution capabilities. In CI, different GPU profiles are often run in parallel jobs.

```mermaid
graph TD
    CIWorkflow["nvml-mock-e2e-go.yaml<br/>GitHub Actions Workflow"]
    
    BuildNvmlMockImageJob["build-nvmlmock-image<br/>(Build & Push to ttl.sh)"]
    BuildKindNodeImageJob["build-kind-node-image<br/>(Build & Push to ttl.sh)"]
    
    E2EJobMatrix["e2e Job Matrix<br/>(per GPU profile)"]
    
    E2EJob1["e2e Job (Profile A)"]
    E2EJob2["e2e Job (Profile B)"]
    E2EJobN["e2e Job (Profile N)"]
    
    Harness1["harness.Harness (Profile A)"]
    Harness2["harness.Harness (Profile B)"]
    HarnessN["harness.Harness (Profile N)"]
    
    CIWorkflow --> BuildNvmlMockImageJob
    CIWorkflow --> BuildKindNodeImageJob
    
    BuildNvmlMockImageJob --> E2EJobMatrix
    BuildKindNodeImageJob --> E2EJobMatrix
    
    E2EJobMatrix --> E2EJob1
    E2EJobMatrix --> E2EJob2
    E2EJobMatrix --> E2EJobN
    
    E2EJob1 --> Harness1
    E2EJob2 --> Harness2
    E2EJobN --> HarnessN
    
    subgraph "Harness Execution (per job)"
        PullImages["Pull Images from ttl.sh<br/>(by digest)"]
        CreateCluster["Create Kind Cluster"]
        RunGinkgoSuite["Run Ginkgo Suite<br/>(tests/e2e/go)"]
    end
    
    Harness1 --> PullImages
    Harness1 --> CreateCluster
    Harness1 --> RunGinkgoSuite
```

**CI Workflow (`.github/workflows/nvml-mock-e2e-go.yaml`):**
-   A `build-nvmlmock-image` job builds the `nvml-mock` Docker image once and pushes it to `ttl.sh`. The digest of this image is then passed to subsequent jobs. [tests/e2e/README.md:16-17]()
-   Similarly, a `build-kind-node-image` job builds the custom Kind node image and pushes it to `ttl.sh`.
-   The `e2e` job uses a matrix strategy to run tests for different GPU profiles (e.g., `a100`, `h100`, `gb200`) in parallel. [tests/e2e/README.md:76-79]()
-   Each parallel `e2e` job pulls the pre-built `nvml-mock` and `kind-node` images by digest from `ttl.sh`, tags them locally, and then proceeds with cluster creation and test execution. This avoids redundant image builds and ensures consistency across parallel runs. [tests/e2e/README.md:52-54]()

**Local Parallel Execution:**
-   Ginkgo supports local parallel execution using the `-p` flag (e.g., `ginkgo -p 4`).
-   The `Makefile` targets for E2E tests (`make e2e`, `make e2e-dra`, etc.) can be configured with `E2E_GINKGO_FLAGS` to pass parallelization options to Ginkgo. [Makefile:147-167]()

Sources:
- [.github/workflows/nvml-mock-e2e-go.yaml:76-146]()
- [tests/e2e/README.md:16-17]()
- [tests/e2e/README.md:52-54]()
- [tests/e2e/README.md:76-79]()
- [Makefile:147-167]()

---

## Kubernetes Test Utilities

### Certificate Generation Utilities

The framework provides utilities for generating self-signed certificates needed for testing secure Kubernetes components:

```mermaid
graph TB
    subgraph "Certificate Utilities"
        GenerateSelfSignedCertKey["cert.GenerateSelfSignedCertKey()<br/>host, alternateIPs, alternateDNS"]
        NewSelfSignedCACert["cert.NewSelfSignedCACert()<br/>cfg Config, key crypto.Signer"]
    end
    
    subgraph "Certificate Types"
        Config["cert.Config<br/>CommonName, Organization, AltNames"]
        AltNames["cert.AltNames<br/>DNSNames, IPs"]
    end
    
    subgraph "Output"
        CertPEM["Certificate PEM<br/>[]byte"]
        KeyPEM["Private Key PEM<br/>[]byte"]
        X509Cert["*x509.Certificate"]
    end
    
    GenerateSelfSignedCertKey --> CertPEM
    GenerateSelfSignedCertKey --> KeyPEM
    NewSelfSignedCACert --> X509Cert
    
    Config --> GenerateSelfSignedCertKey
    Config --> NewSelfSignedCACert
    AltNames --> Config
```

**Key Functions:**
- `GenerateSelfSignedCertKey(host string, alternateIPs []net.IP, alternateDNS []string)`: Creates self-signed cert and key
- `NewSelfSignedCACert(cfg Config, key crypto.Signer)`: Creates a CA certificate
- `GenerateSelfSignedCertKeyWithOptions(opts SelfSignedCertKeyOptions)`: Advanced options including fixtures

Sources:
- [vendor/k8s.io/client-go/util/cert/cert.go:42-93]()
- [vendor/k8s.io/client-go/util/cert/cert.go:117-268]()

### YAML and JSON Manifest Processing

The framework provides decoders for processing Kubernetes manifests:

```mermaid
graph TB
    subgraph "Decoder Types"
        YAMLOrJSONDecoder["yaml.YAMLOrJSONDecoder<br/>Auto-detect format"]
        YAMLToJSONDecoder["yaml.YAMLToJSONDecoder<br/>YAML documents"]
        YAMLDecoder["yaml.YAMLDecoder<br/>Multi-document YAML"]
    end
    
    subgraph "Decoder Construction"
        NewYAMLOrJSONDecoder["NewYAMLOrJSONDecoder()<br/>bufferSize"]
        NewYAMLToJSONDecoder["NewYAMLToJSONDecoder()"]
        NewDocumentDecoder["NewDocumentDecoder()"]
    end
    
    subgraph "Operations"
        Decode["Decode(into interface{})"]
        GuessJSONStream["GuessJSONStream()<br/>Peek at content"]
        ToJSON["ToJSON(data []byte)"]
    end
    
    subgraph "Input Sources"
        IOReader["io.Reader<br/>File, HTTP, etc."]
        ByteSlice["[]byte<br/>In-memory data"]
    end
    
    NewYAMLOrJSONDecoder --> YAMLOrJSONDecoder
    NewYAMLToJSONDecoder --> YAMLToJSONDecoder
    NewDocumentDecoder --> YAMLDecoder
    
    IOReader --> NewYAMLOrJSONDecoder
    IOReader --> NewYAMLToJSONDecoder
    IOReader --> NewDocumentDecoder
    
    ByteSlice --> ToJSON
    
    YAMLOrJSONDecoder --> Decode
    YAMLToJSONDecoder --> Decode
    YAMLDecoder --> Decode
```

**Primary Decoder: YAMLOrJSONDecoder**

This decoder automatically detects whether input is JSON or YAML and handles both:
- Tries JSON first (faster)
- Falls back to YAML if JSON fails
- Handles multi-document streams with `---` separators

**Usage Pattern:**
```go
decoder := yaml.NewYAMLOrJSONDecoder(reader, bufferSize)
for {
    var obj unstructured.Unstructured
    if err := decoder.Decode(&obj); err != nil {
        if err == io.EOF {
            break
        }
        // handle error
    }
    // process obj
}
```

Sources:
- [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:240-358]()
- [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:106-139]()
- [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:158-205]()
- [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:92-101]()

---

## Integration Points

### GinkgoT Interface

`GinkgoT()` provides a `testing.TB`-compatible interface for third-party libraries:

```mermaid
graph TB
    subgraph "GinkgoT Interface"
        GinkgoT["GinkgoT(optionalOffset...)<br/>FullGinkgoTInterface"]
        
        TestingMethods["testing.TB Methods<br/>Fail(), Fatal(), Log(), etc."]
        GinkgoMethods["Ginkgo-specific Methods<br/>AddReportEntry(), DeferCleanup()"]
        FormatterMethods["Formatting Methods<br/>F(), Fi(), Fiw()"]
    end
    
    subgraph "Implementation"
        TestingTProxy["testingtproxy.New()"]
        GinkgoWriter["GinkgoWriter<br/>Output Buffer"]
        FailFunc["Fail Function"]
        SkipFunc["Skip Function"]
    end
    
    GinkgoT --> TestingMethods
    GinkgoT --> GinkgoMethods
    GinkgoT --> FormatterMethods
    
    GinkgoT --> TestingTProxy
    TestingTProxy --> GinkgoWriter
    TestingTProxy --> FailFunc
    TestingTProxy --> SkipFunc
```

**Key Methods:**
- Standard `testing.TB`: `Fail()`, `FailNow()`, `Fatal()`, `Log()`, `Skip()`, etc.
- Ginkgo-specific: `AddReportEntry()`, `DeferCleanup()`, `RenderTimeline()`
- Formatting: `F()`, `Fi()` (with indentation), `Fiw()` (with word wrap)

Sources:
- [vendor/github.com/onsi/ginkgo/v2/dsl/ginkgo_t_dsl.go:27-108]()
- [vendor/github.com/onsi/ginkgo/v2/dsl/ginkgo_t_dsl.go:120-199]()

### Context and Timeouts

Interruptible nodes receive a `SpecContext`:

```mermaid
graph TB
    subgraph "Context Support"
        SpecContext["SpecContext<br/>internal.SpecContext"]
        StdContext["context.Context<br/>Standard Go Interface"]
    end
    
    subgraph "Timeout Decorators"
        NodeTimeout["NodeTimeout(duration)<br/>Single node timeout"]
        SpecTimeout["SpecTimeout(duration)<br/>Entire spec timeout"]
        GracePeriod["GracePeriod(duration)<br/>Cleanup time"]
    end
    
    subgraph "Node Signatures"
        WithContext["func(SpecContext)"]
        WithContextAndReport["func(SpecContext, Report)"]
        NoContext["func()"]
    end
    
    SpecContext --|implements| StdContext
    
    NodeTimeout --> WithContext
    SpecTimeout --> WithContext
    GracePeriod --> WithContext
    
    WithContext -.->|"receives"| SpecContext
    WithContextAndReport -.->|"receives"| SpecContext
```

**Context Cancellation:**
- Ginkgo cancels `SpecContext` on timeout or interrupt
- Use `<-ctx.Done()` to detect cancellation
- Check `ctx.Err()` for cancellation reason

Sources:
- [vendor/github.com/onsi/ginkgo/v2/dsl/core_dsl.go:95-100]()
- [vendor/github.com/onsi/ginkgo/v2/internal/node.go:63-68]()
- [vendor/github.com/onsi/ginkgo/v2/internal/node.go:316-330]()

### Writer and Output Interception

```mermaid
graph LR
    subgraph "Output System"
        GinkgoWriter["GinkgoWriter<br/>GinkgoWriterInterface"]
        InternalWriter["internal.Writer<br/>Buffer + Stream"]
        OutputInterceptor["OutputInterceptor<br/>Capture stdout/stderr"]
    end
    
    subgraph "Writer Modes"
        StreamAndBuffer["StreamAndBuffer<br/>-v mode"]
        BufferOnly["BufferOnly<br/>Default mode"]
    end
    
    subgraph "Output Destinations"
        Stdout["os.Stdout"]
        Buffer["Internal Buffer"]
        TeeWriters["Tee Writers<br/>Custom destinations"]
    end
    
    GinkgoWriter --> InternalWriter
    InternalWriter --> StreamAndBuffer
    InternalWriter --> BufferOnly
    
    StreamAndBuffer --> Stdout
    StreamAndBuffer --> Buffer
    BufferOnly --> Buffer
    
    InternalWriter --> TeeWriters
    
    OutputInterceptor -.->|"when parallel"| Stdout
```

**Output Control:**
- `GinkgoWriter.Print()`, `Printf()`, `Println()`: Write to Ginkgo output
- `GinkgoWriter.TeeTo(writer)`: Add custom writer
- `PauseOutputInterception()` / `ResumeOutputInterception()`: Control interception

Sources:
- [vendor/github.com/onsi/ginkgo/v2/dsl/core_dsl.go:82-115]()
- [vendor/github.com/onsi/ginkgo/v2/dsl/core_dsl.go:217-230]()
- [vendor/github.com/onsi/ginkgo/v2/dsl/core_dsl.go:296-301]()

---

## Summary

The testing infrastructure is built on three pillars:

1.  **Ginkgo v2.32.0 Framework**: Provides BDD organization (`Describe`/`It`), lifecycle management (`BeforeEach`/`AfterEach`), and execution control (parallel support, timeouts)
2.  **Gomega v1.42.1 Assertion Library**: Supplies expressive matchers and asynchronous assertion capabilities (`Eventually`, `Consistently`)
3.  **E2E Harness**: Manages the full lifecycle of Kubernetes test clusters (Kind), image builds, Helm deployments, and diagnostics collection.
4.  **Kubernetes Test Utilities**: Offers specialized tooling for certificate generation and manifest processing via `k8s.io/client-go` utilities

The design emphasizes:
-   **Expressiveness**: BDD structure with clear test intent
-   **Flexibility**: Table-driven tests, decorators, custom reporters
-   **Integration**: Seamless interaction with Kubernetes APIs and third-party libraries
-   **Observability**: Rich reporting with timelines, progress tracking, and custom entries

Sources:
- [go.mod:1-16]()
- [vendor/github.com/onsi/ginkgo/v2/types/version.go:1-4]()
- [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:1-96]()
- [vendor/github.com/onsi/ginkgo/v2/dsl/core_dsl.go:1-52]()
- [tests/e2e/go/framework/harness/harness.go]()

---

# Page: CI/CD Pipeline

# CI/CD Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/dependabot.yml](.github/dependabot.yml)
- [.github/workflows/basic-checks.yaml](.github/workflows/basic-checks.yaml)
- [.github/workflows/ci.yaml](.github/workflows/ci.yaml)
- [.github/workflows/code_scanning.yaml](.github/workflows/code_scanning.yaml)
- [.github/workflows/golang.yaml](.github/workflows/golang.yaml)
- [.github/workflows/helm-publish.yaml](.github/workflows/helm-publish.yaml)
- [.github/workflows/helm.yaml](.github/workflows/helm.yaml)
- [.github/workflows/nvml-mock-publish.yaml](.github/workflows/nvml-mock-publish.yaml)
- [.github/workflows/scorecard.yaml](.github/workflows/scorecard.yaml)
- [.github/workflows/variables.yaml](.github/workflows/variables.yaml)
- [deployments/devel/Dockerfile](deployments/devel/Dockerfile)

</details>



## Purpose and Scope

This document describes the automated Continuous Integration and Continuous Deployment (CI/CD) pipeline for the k8s-test-infra repository. The pipeline automates code quality checks, security scanning, and version management using GitHub Actions workflows. It employs a reusable workflow architecture where a central coordination job extracts build variables that are consumed by parallel execution jobs.

For detailed information on specific aspects of the pipeline:
- GitHub Actions workflow structure and job dependencies: see [GitHub Actions Workflows](#4.1)
- Automated testing and code quality enforcement: see [Automated Testing and Code Quality](#4.2)
- Go version management strategy: see [Version Management](#4.3)
- Automated dependency updates: see [Dependency Updates with Dependabot](#4.4)

---

## Pipeline Architecture

The CI/CD pipeline is organized as a hierarchy of reusable GitHub Actions workflows. The top-level workflows (`ci.yaml` and `basic-checks.yaml`) orchestrate execution by calling specialized workflows that perform specific tasks. This modular design allows workflows to be reused across different trigger conditions while maintaining consistent behavior.

### Workflow Hierarchy

```mermaid
graph TB
    subgraph "Entry Points"
        CI["ci.yaml<br/>Workflow<br/>(push events)"]
        BASIC["basic-checks.yaml<br/>Workflow<br/>(PR events)"]
    end
    
    subgraph "Coordination Layer"
        VARS["variables.yaml<br/>Job: variables<br/>Outputs: version, golang_version"]
    end
    
    subgraph "Execution Layer"
        GOLANG["golang.yaml<br/>Job: check<br/>Actions: lint, check-modules, unit-tests, govulncheck"]
        SCAN["code_scanning.yaml<br/>Job: analyze<br/>Actions: CodeQL"]
        SCORECARD["scorecard.yaml<br/>Job: analysis<br/>Actions: OpenSSF Scorecard"]
        NVML_MOCK_PUBLISH["nvml-mock-publish.yaml<br/>Job: publish<br/>Actions: Build & Push nvml-mock image"]
        HELM_CI["helm.yaml<br/>Job: lint, unittest<br/>Actions: Helm lint & unittest"]
        HELM_PUBLISH["helm-publish.yaml<br/>Job: publish<br/>Actions: Push Helm chart to OCI"]
    end
    
    subgraph "External Resources"
        DOCKERFILE["deployments/devel/Dockerfile<br/>FROM golang:1.26.5"]
        SCRIPT["hack/golang-version.sh<br/>Extract version from Dockerfile"]
    end
    
    CI --> BASIC
    BASIC --> VARS
    VARS --> GOLANG
    VARS --> SCAN
    VARS --> NVML_MOCK_PUBLISH
    VARS --> HELM_CI
    HELM_CI --on success--> HELM_PUBLISH
    
    VARS -.->|"Executes"| SCRIPT
    SCRIPT -.->|"Reads"| DOCKERFILE
    
    VARS -.->|"golang_version input"| GOLANG
    VARS -.->|"golang_version input"| SCAN
    
    style SCORECARD fill:#fff,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5
    SCORECARD -.->|"Scheduled/Push to main"| SCORECARD
```

**Sources:** [.github/workflows/ci.yaml:1-26](), [.github/workflows/basic-checks.yaml:1-50](), [.github/workflows/variables.yaml:1-45](), [.github/workflows/golang.yaml:1-87](), [.github/workflows/code_scanning.yaml:1-54](), [.github/workflows/scorecard.yaml:1-39](), [.github/workflows/nvml-mock-publish.yaml:1-100](), [.github/workflows/helm.yaml:1-59](), [.github/workflows/helm-publish.yaml:1-95](), [deployments/devel/Dockerfile:1-18]()

---

## Reusable Workflow Pattern

The pipeline implements GitHub Actions' `workflow_call` pattern, which allows workflows to be invoked as reusable components. This pattern provides type-safe parameter passing and output propagation between workflows.

### Variables Workflow

The `variables` job serves as the coordination point for the entire pipeline. It computes two critical outputs that are consumed by downstream jobs:

| Output | Description | Source | Usage |
|--------|-------------|--------|-------|
| `version` | 8-character Git commit SHA | `GITHUB_SHA` environment variable | Version tagging for artifacts |
| `golang_version` | Go toolchain version | [deployments/devel/Dockerfile:17]() via [hack/golang-version.sh]() | CI environment configuration |

The workflow definition declares these outputs using the `workflow_call.outputs` section:

[.github/workflows/variables.yaml:21-28]()

The `variables` job implementation extracts these values:

[.github/workflows/variables.yaml:31-49]()

The `golang-version.sh` script parses the Dockerfile to extract the Go version:

[hack/golang-version.sh:16-22]()

This script uses `grep` to find the `FROM golang:` directive and extract the version number using regular expressions. The single source of truth for the Go version is maintained in [deployments/devel/Dockerfile:17](), which defines `FROM golang:1.26.5`.

**Sources:** [.github/workflows/variables.yaml:1-49](), [hack/golang-version.sh:1-23](), [deployments/devel/Dockerfile:1-18]()

---

## Pipeline Entry Points

The pipeline has two entry points that trigger on different GitHub events:

### CI Pipeline Workflow

The `ci.yaml` workflow triggers on push events to specific branches:

[.github/workflows/ci.yaml:23-28]()

This workflow immediately delegates to `basic-checks.yaml`:

[.github/workflows/ci.yaml:30-32]()

### Basic Checks Workflow

The `basic-checks.yaml` workflow serves as both:
1. A direct entry point triggered by pull request events
2. A reusable workflow called by `ci.yaml`

[.github/workflows/basic-checks.yaml:16-38]()

The workflow supports `workflow_call` to allow invocation by other workflows while also responding to pull request events directly:

[.github/workflows/basic-checks.yaml:23-30]()

**Sources:** [.github/workflows/ci.yaml:1-37](), [.github/workflows/basic-checks.yaml:1-50]()

---

## Job Execution Flow

The pipeline executes jobs in a coordinated sequence with explicit dependencies. The `variables` job must complete before parallel execution jobs can begin, ensuring all jobs use consistent build parameters.

```mermaid
sequenceDiagram
    participant Trigger as "GitHub Event<br/>(push/PR)"
    participant Entry as "ci.yaml or<br/>basic-checks.yaml"
    participant Vars as "variables job<br/>(variables.yaml)"
    participant Script as "golang-version.sh"
    participant Dockerfile as "deployments/devel/Dockerfile"
    participant Golang as "golang job<br/>(golang.yaml)"
    participant CodeQL as "code-scanning job<br/>(code_scanning.yaml)"
    participant NvmlMockPublish as "nvml-mock-publish job<br/>(nvml-mock-publish.yaml)"
    participant HelmCI as "helm job<br/>(helm.yaml)"
    participant HelmPublish as "helm-publish job<br/>(helm-publish.yaml)"
    
    Trigger->>Entry: "Workflow trigger"
    Entry->>Vars: "Call workflow: variables.yaml"
    Vars->>Vars: "Generate version SHA"
    Vars->>Script: "Execute ./hack/golang-version.sh"
    Script->>Dockerfile: "Parse FROM golang:VERSION"
    Dockerfile-->>Script: "1.26.5"
    Script-->>Vars: "Return 1.26.5"
    Vars-->>Entry: "Outputs: version, golang_version"
    
    par "Parallel Execution"
        Entry->>Golang: "Call workflow with golang_version"
        Golang->>Golang: "Setup Go 1.26.5"
        Golang->>Golang: "golangci-lint, go vet, check-modules, unit tests, govulncheck"
        Golang-->>Entry: "Success/Failure"
    and
        Entry->>CodeQL: "Call workflow with golang_version"
        CodeQL->>CodeQL: "Setup Go 1.26.5"
        CodeQL->>CodeQL: "Initialize CodeQL, go mod download, CodeQL Analysis"
        CodeQL-->>Entry: "Success/Failure"
    and
        Entry->>NvmlMockPublish: "Call workflow (if push to main/tag)"
        NvmlMockPublish->>NvmlMockPublish: "Build & Push nvml-mock image, Sign, Generate SBOM"
        NvmlMockPublish-->>Entry: "Success/Failure"
    and
        Entry->>HelmCI: "Call workflow (if helm chart changes)"
        HelmCI->>HelmCI: "Helm lint, Helm unittest"
        HelmCI-->>Entry: "Success/Failure"
    end
    
    HelmCI-->>HelmPublish: "Trigger helm-publish on success (if push to main)"
    HelmPublish->>HelmPublish: "Package & Push Helm chart to OCI, Sign"
    HelmPublish-->>Entry: "Success/Failure"
```

**Sources:** [.github/workflows/basic-checks.yaml:33-49](), [.github/workflows/variables.yaml:25-49](), [.github/workflows/golang.yaml:24-87](), [.github/workflows/code_scanning.yaml:23-52](), [.github/workflows/nvml-mock-publish.yaml:1-100](), [.github/workflows/helm.yaml:1-59](), [.github/workflows/helm-publish.yaml:1-95]()

---

## Workflow Trigger Conditions

The pipeline responds to different GitHub events depending on the workflow entry point:

| Workflow | Trigger Events | Branch Filters | Description |
|----------|---------------|----------------|-------------|
| `ci.yaml` | `push` | `main`, `release-*`, `pull-request/[0-9]+` | Runs on pushes to main, release branches, and PR merge branches |
| `basic-checks.yaml` (direct) | `pull_request` (`opened`, `synchronize`) | `main`, `release-*` | Runs when PRs are opened or updated against main or release branches |
| `basic-checks.yaml` (called) | `workflow_call` | N/A | Invoked by `ci.yaml` or other workflows |
| `nvml-mock-publish.yaml` | `push`, `workflow_dispatch` | `main`, `v*` tags | Publishes `nvml-mock` image on pushes to main, version tags, or manual trigger |
| `helm.yaml` | `pull_request`, `push` | `main` (paths: `deployments/nvml-mock/helm/**`) | Runs Helm lint/unittest on PRs/pushes affecting Helm chart |
| `helm-publish.yaml` | `workflow_run` (`helm.yaml` completed) | `main` | Publishes Helm chart to OCI registry after successful `helm.yaml` run on `main` |
| `scorecard.yaml` | `schedule`, `push`, `workflow_dispatch` | `main` | Runs OpenSSF Scorecard weekly, on pushes to main, or manual trigger |

The `pull-request/[0-9]+` branch pattern in `ci.yaml` matches GitHub's merge queue branches, allowing the pipeline to run on proposed merge commits before they reach the main branch.

**Sources:** [.github/workflows/ci.yaml:16-28](), [.github/workflows/basic-checks.yaml:16-38](), [.github/workflows/nvml-mock-publish.yaml:1-19](), [.github/workflows/helm.yaml:1-13](), [.github/workflows/helm-publish.yaml:1-12](), [.github/workflows/scorecard.yaml:1-13]()

---

## Golang Workflow Execution

The `golang.yaml` workflow performs code quality checks using the Go toolchain. It receives the `golang_version` as an input parameter:

[.github/workflows/golang.yaml:24-26]()

The workflow executes several primary checks:

### 1. Environment Setup

[.github/workflows/golang.yaml:29-37]()

The workflow checks out the repository and installs Go using the version extracted by the `variables` job.

### 2. Linting

[.github/workflows/golang.yaml:39-44]()

The linting step uses `golangci-lint-action@v9` with the following configuration:
- `version: latest` - Always uses the most recent golangci-lint version
- `args: -v --timeout 5m` - Verbose output with 5-minute timeout
- `skip-cache: true` - Disables caching for reproducible results

### 3. Go Vet

[.github/workflows/golang.yaml:46-62]()

A bare `go vet ./...` command is run to catch issues that `golangci-lint` might suppress or under-report. This ensures strict enforcement of Go's static analysis.

### 4. Module Verification

[.github/workflows/golang.yaml:64-67]()

The `make check-modules` target verifies that Go module files (`go.mod`, `go.sum`) are consistent with the vendored dependencies. This ensures reproducible builds.

### 5. Unit Tests

[.github/workflows/golang.yaml:69-72]()

Unit tests are executed with `go test -v -race -coverprofile=coverage.out -covermode=atomic $(go list ./... | grep -v vendor)`. This includes race detection and coverage reporting.

### 6. Mockpcisysfs Integration Tests

[.github/workflows/golang.yaml:74-81]()

Specific integration tests for the `mockpcisysfs` shim are run with the `integration` build tag after building the shim.

### 7. Go Vulnerability Check

[.github/workflows/golang.yaml:83-87]()

The `govulncheck` tool is installed and run across the entire codebase to identify known vulnerabilities in Go modules.

**Sources:** [.github/workflows/golang.yaml:1-87]()

---

## CodeQL Security Scanning

The `code_scanning.yaml` workflow performs security analysis using GitHub's CodeQL engine. It runs in parallel with the `golang` job:

[.github/workflows/code_scanning.yaml:20-24]()

### Analysis Configuration

The workflow has elevated permissions to write security events:

[.github/workflows/code_scanning.yaml:29-31]()

### Execution Steps

The CodeQL analysis follows this sequence:

[.github/workflows/code_scanning.yaml:33-52]()

Key steps:
1. **Repository checkout** - Retrieves source code
2. **Go installation** - Uses the extracted `golang_version`
3. **CodeQL initialization** - Configures for Go language analysis
4. **Dependency fetch** - Downloads Go modules with `go mod download`
5. **CodeQL analysis** - Performs static analysis and uploads results

The `category: "/language:go"` parameter categorizes results in GitHub's Security tab for filtering and organization.

**Sources:** [.github/workflows/code_scanning.yaml:1-54]()

---

## OpenSSF Scorecard

The `scorecard.yaml` workflow runs the OpenSSF Scorecard tool to assess the project's security health.

[.github/workflows/scorecard.yaml:1-39]()

### Trigger Conditions

This workflow is triggered weekly on Monday, on pushes to the `main` branch, or manually via `workflow_dispatch`:

[.github/workflows/scorecard.yaml:6-11]()

### Execution Steps

The workflow checks out the repository and runs the Scorecard action:

[.github/workflows/scorecard.yaml:23-33]()

The results are saved as a SARIF file and then uploaded to GitHub Security tab for review:

[.github/workflows/scorecard.yaml:35-39]()

**Sources:** [.github/workflows/scorecard.yaml:1-39]()

---

## nvml-mock Image Publishing

The `nvml-mock-publish.yaml` workflow is responsible for building and publishing the `nvml-mock` Docker image to `ghcr.io`.

[.github/workflows/nvml-mock-publish.yaml:1-100]()

### Trigger Conditions

This workflow triggers on pushes to the `main` branch, on `v*` tags, or manually via `workflow_dispatch`:

[.github/workflows/nvml-mock-publish.yaml:13-19]()

### Publishing Steps

The `publish` job performs the following:
1. **Checkout code**
2. **Set up QEMU and Buildx** for multi-platform builds
3. **Log in to GHCR**
4. **Extract metadata** to generate image tags (e.g., `latest`, `v0.1.0`, `sha-xxxxxxx`)
5. **Build and push** the image from [deployments/nvml-mock/Dockerfile]() for `linux/amd64` and `linux/arm64` platforms
6. **Sign the container image** using Cosign
7. **Generate and attach SBOM** (Software Bill of Materials) to the image

**Sources:** [.github/workflows/nvml-mock-publish.yaml:1-100]()

---

## Helm Chart CI/CD

The Helm chart for `nvml-mock` has its own dedicated CI/CD workflows: `helm.yaml` for CI and `helm-publish.yaml` for CD.

### Helm CI (`helm.yaml`)

This workflow performs linting and unit testing for the Helm chart.

[.github/workflows/helm.yaml:1-59]()

#### Trigger Conditions

It triggers on pull requests and pushes to `main` only when changes are detected within the `deployments/nvml-mock/helm/**` path:

[.github/workflows/helm.yaml:5-13]()

#### Checks

The `lint` job uses `chart-testing-action` to lint the Helm chart:

[.github/workflows/helm.yaml:26-42]()

The `unittest` job installs `helm-unittest` plugin and runs unit tests defined for the chart:

[.github/workflows/helm.yaml:44-59]()

### Helm Publish (`helm-publish.yaml`)

This workflow publishes the Helm chart to the OCI registry on `ghcr.io`.

[.github/workflows/helm-publish.yaml:1-95]()

#### Trigger Conditions

This workflow is triggered only after the `helm.yaml` workflow completes successfully on the `main` branch:

[.github/workflows/helm-publish.yaml:8-12]()

#### Publishing Steps

The `publish` job performs:
1. **Checkout repository** at the specific SHA of the triggering workflow run
2. **Set up Helm**
3. **Read chart version** from `Chart.yaml`
4. **Log in to GHCR**
5. **Package the chart**
6. **Push the chart to OCI registry** with retry logic for intermittent failures
7. **Install Cosign**
8. **Log in to GHCR for Cosign** (separate login required for Cosign)
9. **Sign the OCI artifact**

**Sources:** [.github/workflows/helm.yaml:1-59](), [.github/workflows/helm-publish.yaml:1-95]()

---

## Job Dependencies

The `basic-checks.yaml` workflow explicitly declares job dependencies using the `needs` keyword:

[.github/workflows/basic-checks.yaml:40-50]()

This configuration creates the following dependency graph:

```mermaid
graph TD
    VARS["variables<br/>(variables.yaml)"]
    GOLANG["golang<br/>(golang.yaml)<br/>needs: variables"]
    SCAN["code-scanning<br/>(code_scanning.yaml)<br/>needs: variables"]
    
    VARS --> GOLANG
    VARS --> SCAN
```

The `needs` declarations ensure:
1. The `variables` job completes before `golang` or `code-scanning` begin
2. Outputs from `variables` are available to dependent jobs via `needs.variables.outputs.golang_version`
3. If `variables` fails, dependent jobs are skipped

**Sources:** [.github/workflows/basic-checks.yaml:40-50]()

---

## Integration with Copy-PR Bot

The repository enables NVIDIA's copy-PR bot, which automatically creates internal mirrors of pull requests:

[.github/copy-pr-bot.yaml:1-3]()

This bot runs separately from the CI/CD pipeline but coordinates with it by monitoring PR status checks. The bot configuration is minimal, with the `enabled: true` flag activating automatic PR mirroring.

**Sources:** [.github/copy-pr-bot.yaml:1-3]()

---

## Pipeline Outputs

The pipeline produces the following outputs that can be consumed by dependent workflows:

| Output | Source Job | Description | Access Pattern |
|--------|-----------|-------------|----------------|
| `version` | `variables` | 8-character commit SHA | `${{ jobs.variables.outputs.version }}` |
| `golang_version` | `variables` | Go toolchain version | `${{ jobs.variables.outputs.golang_version }}` |

These outputs are declared at the workflow level in `basic-checks.yaml`:

[.github/workflows/basic-checks.yaml:23-30]()

This allows external workflows to call `basic-checks.yaml` and access these values for use in subsequent build or deployment steps.

**Sources:** [.github/workflows/basic-checks.yaml:23-30](), [.github/workflows/variables.yaml:21-28]()

---

# Page: GitHub Actions Workflows

# GitHub Actions Workflows

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/bug_report.yml](.github/ISSUE_TEMPLATE/bug_report.yml)
- [.github/ISSUE_TEMPLATE/config.yml](.github/ISSUE_TEMPLATE/config.yml)
- [.github/ISSUE_TEMPLATE/documentation.yml](.github/ISSUE_TEMPLATE/documentation.yml)
- [.github/ISSUE_TEMPLATE/feature_request.yml](.github/ISSUE_TEMPLATE/feature_request.yml)
- [.github/dependabot.yml](.github/dependabot.yml)
- [.github/workflows/basic-checks.yaml](.github/workflows/basic-checks.yaml)
- [.github/workflows/ci.yaml](.github/workflows/ci.yaml)
- [.github/workflows/code_scanning.yaml](.github/workflows/code_scanning.yaml)
- [.github/workflows/golang.yaml](.github/workflows/golang.yaml)
- [.github/workflows/helm-publish.yaml](.github/workflows/helm-publish.yaml)
- [.github/workflows/helm.yaml](.github/workflows/helm.yaml)
- [.github/workflows/nvml-mock-publish.yaml](.github/workflows/nvml-mock-publish.yaml)
- [.github/workflows/scorecard.yaml](.github/workflows/scorecard.yaml)
- [.github/workflows/stale.yaml](.github/workflows/stale.yaml)
- [.github/workflows/variables.yaml](.github/workflows/variables.yaml)
- [deployments/devel/Dockerfile](deployments/devel/Dockerfile)

</details>



## Purpose and Scope

This document describes the GitHub Actions CI/CD workflows that automate code quality checks, linting, security scanning, and version management for the k8s-test-infra repository. The workflows use a modular, reusable pattern where a main orchestrator workflow calls specialized sub-workflows to perform distinct tasks.

For information about automated testing execution within CI, see [Automated Testing and Code Quality](#4.2). For details on how Go version consistency is maintained, see [Version Management](#4.3). For dependency update automation, see [Dependency Updates with Dependabot](#4.4).

---

## Workflow Architecture

The repository uses a **hierarchical workflow composition pattern** with three layers:

| Layer | Purpose | Workflow Files |
|-------|---------|----------------|
| **Entry Point** | Triggered by repository events (push, PR) | `ci.yaml`, `nvml-mock-publish.yaml`, `helm.yaml`, `helm-publish.yaml`, `scorecard.yaml` |
| **Orchestrator** | Coordinates multiple parallel jobs | `basic-checks.yaml` |
| **Reusable Jobs** | Performs specific tasks, called by orchestrators | `variables.yaml`, `golang.yaml`, `code_scanning.yaml` |

This pattern promotes **workflow reusability** and **separation of concerns**. Each reusable workflow accepts inputs and produces outputs, enabling them to be called from multiple parent workflows.

**Workflow Composition Diagram**

```mermaid
graph TB
    subgraph "Entry Points"
        CI["ci.yaml<br/>Main CI Pipeline"]
        BASIC_TRIGGER["basic-checks.yaml<br/>(Direct PR Trigger)"]
        NVML_PUBLISH["nvml-mock-publish.yaml<br/>Image Publishing"]
        HELM_CI["helm.yaml<br/>Helm Chart CI"]
        HELM_PUBLISH["helm-publish.yaml<br/>Helm Chart Publishing"]
        SCORECARD["scorecard.yaml<br/>OpenSSF Scorecard"]
    end
    
    subgraph "Orchestrator Layer"
        BASIC["basic-checks.yaml<br/>Job Orchestration"]
    end
    
    subgraph "Reusable Workflow Layer"
        VARS["variables.yaml<br/>Extract golang_version & version SHA"]
        GOLANG["golang.yaml<br/>Linting & Module Validation"]
        SCAN["code_scanning.yaml<br/>CodeQL Security Analysis"]
    end
    
    subgraph "External Resources"
        DOCKERFILE["deployments/devel/Dockerfile<br/>Go Version Source of Truth"]
        SCRIPT["hack/golang-version.sh<br/>Version Extraction Script"]
    end
    
    CI -->|"uses: ./.github/workflows/basic-checks.yaml"| BASIC
    BASIC_TRIGGER -.->|"Can also be triggered directly"| BASIC
    
    BASIC -->|"uses: ./.github/workflows/variables.yaml"| VARS
    BASIC -->|"uses: ./.github/workflows/golang.yaml<br/>needs: variables"| GOLANG
    BASIC -->|"uses: ./.github/workflows/code_scanning.yaml<br/>needs: variables"| SCAN
    
    VARS -->|"Executes"| SCRIPT
    SCRIPT -->|"Parses"| DOCKERFILE
    
    VARS -.->|"outputs.golang_version"| GOLANG
    VARS -.->|"outputs.golang_version"| SCAN

    HELM_CI -- "workflow_run: completed" --> HELM_PUBLISH
```

**Sources:** [.github/workflows/ci.yaml:1-26](), [.github/workflows/basic-checks.yaml:1-50](), [.github/workflows/variables.yaml:1-45](), [.github/workflows/golang.yaml:1-46](), [.github/workflows/code_scanning.yaml:1-52](), [.github/workflows/nvml-mock-publish.yaml:1-19](), [.github/workflows/helm.yaml:1-13](), [.github/workflows/helm-publish.yaml:1-11](), [.github/workflows/scorecard.yaml:1-12]()

---

## Trigger Conditions

The workflows respond to different GitHub events based on their role:

### ci.yaml (Main CI Pipeline)

Triggers on **push events** to specific branches:

- `pull-request/[0-9]+` - Pull request branches created by the copy-pr-bot
- `main` - Main development branch
- `release-*` - Release branches

[.github/workflows/ci.yaml:23-28]()

### basic-checks.yaml (Direct PR Trigger)

Can be triggered in two ways:

1. **Called by ci.yaml** via `workflow_call` (from push events)
2. **Direct PR events** - `opened` and `synchronize` types on `main` and `release-*` branches

[.github/workflows/basic-checks.yaml:23-38]()

This dual-trigger design ensures that:
- Pull requests get immediate feedback on code quality checks
- Push events to protected branches run the same validation

### nvml-mock-publish.yaml (Image Publishing)

Triggers on:
- **Push to `main` branch**
- **Tag pushes** matching `v*` (e.g., `v0.1.0`)
- **Manual `workflow_dispatch`** for re-running at any ref.

[.github/workflows/nvml-mock-publish.yaml:12-19]()
Note that `paths` filters are intentionally omitted for tag pushes to avoid silently suppressing runs.

### helm.yaml (Helm Chart CI)

Triggers on:
- **Pull requests** to `main` branch, specifically when changes occur in `deployments/nvml-mock/helm/**`
- **Pushes** to `main` branch, specifically when changes occur in `deployments/nvml-mock/helm/**`

[.github/workflows/helm.yaml:5-13]()

### helm-publish.yaml (Helm Chart Publishing)

Triggers on `workflow_run` event:
- When the `helm` workflow completes successfully (`conclusion == 'success'`)
- On the `main` branch (`head_branch == 'main'`)

[.github/workflows/helm-publish.yaml:8-11](), [.github/workflows/helm-publish.yaml:21]()

### scorecard.yaml (OpenSSF Scorecard)

Triggers on:
- **Scheduled cron job**: Every Monday at 06:00 UTC
- **Push to `main` branch**
- **Manual `workflow_dispatch`**

[.github/workflows/scorecard.yaml:7-12]()

**Trigger Flow Diagram**

```mermaid
graph LR
    subgraph "GitHub Events"
        PUSH_MAIN["Push Event<br/>Branch: main"]
        PUSH_PR_BRANCH["Push Event<br/>Branch: pull-request/*"]
        PUSH_RELEASE["Push Event<br/>Branch: release-*"]
        TAG_PUSH["Tag Push Event<br/>Tag: v*"]
        PR_OPEN_SYNC["Pull Request Event<br/>Types: opened, synchronize<br/>Targets: main, release-*"]
        CRON_SCHEDULE["Scheduled Cron Job"]
        MANUAL_DISPATCH["Manual Workflow Dispatch"]
        HELM_PATH_CHANGE["Push/PR to main<br/>(paths: deployments/nvml-mock/helm/**)"]
        HELM_WORKFLOW_SUCCESS["helm workflow completed<br/>(on main branch)"]
    end
    
    subgraph "Workflow Execution"
        CI["ci.yaml"]
        BASIC["basic-checks.yaml"]
        NVML_PUBLISH["nvml-mock-publish.yaml"]
        HELM_CI["helm.yaml"]
        HELM_PUBLISH["helm-publish.yaml"]
        SCORECARD["scorecard.yaml"]
    end
    
    PUSH_MAIN --> CI
    PUSH_PR_BRANCH --> CI
    PUSH_RELEASE --> CI
    PR_OPEN_SYNC --> BASIC
    CI -->|"uses: ./.github/workflows/basic-checks.yaml"| BASIC
    
    PUSH_MAIN --> NVML_PUBLISH
    TAG_PUSH --> NVML_PUBLISH
    MANUAL_DISPATCH --> NVML_PUBLISH
    
    HELM_PATH_CHANGE --> HELM_CI
    HELM_WORKFLOW_SUCCESS --> HELM_PUBLISH
    
    CRON_SCHEDULE --> SCORECARD
    PUSH_MAIN --> SCORECARD
    MANUAL_DISPATCH --> SCORECARD
```

**Sources:** [.github/workflows/ci.yaml:23-28](), [.github/workflows/basic-checks.yaml:23-38](), [.github/workflows/nvml-mock-publish.yaml:12-19](), [.github/workflows/helm.yaml:5-13](), [.github/workflows/helm-publish.yaml:8-11](), [.github/workflows/helm-publish.yaml:21](), [.github/workflows/scorecard.yaml:7-12]()

---

## Job Orchestration and Dependencies

The `basic-checks.yaml` orchestrator defines three jobs with explicit dependency relationships:

| Job Name | Dependencies | Purpose |
|----------|-------------|---------|
| `variables` | None | Extract `golang_version` and `version` SHA |
| `golang` | `variables` | Run linting and module validation with correct Go version |
| `code-scanning` | `variables` | Run CodeQL security analysis with correct Go version |

The `needs` keyword creates a **dependency graph** that ensures:
1. `variables` job completes first
2. `golang` and `code-scanning` run in parallel after `variables` succeeds
3. Both dependent jobs receive outputs from `variables` job

The `ci.yaml` workflow also orchestrates the `nvml-mock-e2e` job, which depends on the `basic` job.

**Job Dependency Graph**

```mermaid
graph TB
    TRIGGER["Workflow Trigger<br/>(push or pull_request)"]
    
    subgraph "ci.yaml Jobs"
        CI_BASIC["basic Job<br/>uses: ./.github/workflows/basic-checks.yaml"]
        CI_E2E["nvml-mock-e2e Job<br/>needs: basic"]
    end

    subgraph "basic-checks.yaml Jobs"
        VARS_JOB["variables Job<br/>runs-on: ubuntu-latest"]
        GOLANG_JOB["golang Job<br/>runs-on: ubuntu-latest<br/>needs: variables"]
        SCAN_JOB["code-scanning Job<br/>runs-on: ubuntu-latest<br/>needs: variables<br/>timeout: 360 minutes"]
    end
    
    subgraph "Outputs from variables"
        VERSION["version<br/>(8-char commit SHA)"]
        GO_VERSION["golang_version<br/>(extracted from Dockerfile)"]
    end
    
    TRIGGER --> CI_BASIC
    CI_BASIC --> VARS_JOB
    VARS_JOB --> VERSION
    VARS_JOB --> GO_VERSION
    
    VERSION -.-> GOLANG_JOB
    GO_VERSION --> GOLANG_JOB
    VERSION -.-> SCAN_JOB
    GO_VERSION --> SCAN_JOB
    
    GOLANG_JOB -.->|"Parallel Execution"| SCAN_JOB
    CI_BASIC --> CI_E2E
```

**Sources:** [.github/workflows/basic-checks.yaml:39-50](), [.github/workflows/ci.yaml:30-37]()

---

## Reusable Workflows

The repository uses GitHub Actions' `workflow_call` trigger to create reusable workflows. This pattern allows workflows to be called as if they were actions, promoting code reuse and maintainability.

### Pattern Structure

Each reusable workflow follows this structure:

```yaml
on:
  workflow_call:
    inputs:
      input_name:
        required: true
        type: string
    outputs:
      output_name:
        description: "Output description"
        value: ${{ jobs.job_name.outputs.output_name }}
```

### Calling Reusable Workflows

Parent workflows call reusable workflows using the `uses` keyword:

```yaml
jobs:
  job-name:
    uses: ./.github/workflows/reusable-workflow.yaml
    with:
      input_name: ${{ needs.other-job.outputs.value }}
```

[.github/workflows/basic-checks.yaml:40-49]()

### Benefits of This Pattern

| Benefit | Description |
|---------|-------------|
| **Single Responsibility** | Each workflow performs one focused task |
| **Testability** | Reusable workflows can be tested independently |
| **Maintainability** | Changes to a task only require updating one workflow |
| **Composability** | Different orchestrators can combine workflows as needed |

**Sources:** [.github/workflows/variables.yaml:20-29](), [.github/workflows/golang.yaml:21-27](), [.github/workflows/code_scanning.yaml:20-26]()

---

## Workflow Details

### variables.yaml - Variable Extraction

**Purpose:** Extract project metadata for use in subsequent jobs.

**Inputs:** None (uses `workflow_call` trigger)

**Outputs:**
- `version` - 8-character short SHA from `$GITHUB_SHA`
- `golang_version` - Go version extracted from Dockerfile

**Job Steps:**

| Step | Action | Purpose |
|------|--------|---------|
| 1. Check out code | `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` | Clone repository to runner |
| 2. Generate Commit Short SHA | Shell command | Extract first 8 chars of commit SHA |
| 3. Get Golang Version | `./hack/golang-version.sh` | Parse Go version from Dockerfile |

**Implementation Details:**

The version extraction uses shell command substitution:
```bash
echo "version=$(echo $GITHUB_SHA | cut -c1-8)" >> "$GITHUB_OUTPUT"
```
[.github/workflows/variables.yaml:40-41]()

The Go version extraction delegates to a bash script that parses the Dockerfile:
```bash
GOLANG_VERSION=$(./hack/golang-version.sh)
echo "Detected $GOLANG_VERSION"
echo "golang_version=${GOLANG_VERSION}" >> $GITHUB_OUTPUT
```
[.github/workflows/variables.yaml:44-47]()

**Sources:** [.github/workflows/variables.yaml:1-50]()

---

### golang.yaml - Go Linting and Module Validation

**Purpose:** Enforce code quality standards through linting and verify module consistency.

**Inputs:**
- `golang_version` (required, string) - Go version to use for checks

**Outputs:** None

**Job Steps:**

| Step | Action | Configuration |
|------|--------|---------------|
| 1. Checkout code | `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` | Standard checkout |
| 2. Install Go | `actions/setup-go@b7ad1dad31e06c5925ef5d2fc7ad053ef454303e` | Version from `inputs.golang_version` |
| 3. Lint | `golangci/golangci-lint-action@ba0d7d2ec06a0ea1cb5fa41b2e4a3ab91d21278a` | Latest version, 5-minute timeout, no cache |
| 4. Run go vet | `go vet ./...` | Comprehensive static analysis, not suppressed by `//nolint` |
| 5. Check golang modules | `make check-modules` | Verifies module consistency |
| 6. Run unit tests | `go test -v -race -coverprofile=coverage.out -covermode=atomic $(go list ./... | grep -v vendor)` | Executes all unit tests |
| 7. Build mockpcisysfs shim | `make -C pkg/system/mockpcisysfs` | Builds the `libpcimocksys.so` shim |
| 8. Run mockpcisysfs integration tests | `go test -tags integration -v ./pkg/system/mockpcisysfs/...` | Runs integration tests for the shim |
| 9. Run govulncheck | `go install golang.org/x/vuln/cmd/govulncheck@latest; govulncheck ./...` | Checks for known vulnerabilities |

**Linting Configuration:**

The workflow uses `golangci-lint` with these parameters:
- `version: latest` - Always use the most recent linter version
- `args: -v --timeout 5m` - Verbose output with 5-minute timeout
- `skip-cache: true` - Disable caching for consistent results

[.github/workflows/golang.yaml:41-43]()

**`go vet` Details:**
The `go vet ./...` step is explicitly included to catch issues that `golangci-lint` might miss or suppress. It runs `govet` across all packages without exclusions, ensuring a strict check for common programming errors.
[.github/workflows/golang.yaml:47-63]()

**Module Validation:**

The `make check-modules` target ensures that:
- `go.mod` and `go.sum` are up to date
- No untracked module changes exist

[.github/workflows/golang.yaml:65-67]()

**Sources:** [.github/workflows/golang.yaml:1-88]()

---

### code_scanning.yaml - CodeQL Security Analysis

**Purpose:** Perform static security analysis using GitHub CodeQL.

**Inputs:**
- `golang_version` (required, string) - Go version for dependency resolution

**Outputs:** None (results uploaded to GitHub Security tab)

**Permissions Required:**

```yaml
permissions:
  security-events: write # Upload CodeQL results
  packages: read         # Access private packages if needed
```
[.github/workflows/code_scanning.yaml:30-33]()

**Job Configuration:**

- `runs-on: ubuntu-latest`
- `timeout-minutes: 360` (6-hour timeout for large codebases)

**Job Steps:**

| Step | Action | Purpose |
|------|--------|---------|
| 1. Checkout repository | `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` | Clone code for analysis |
| 2. Install Go | `actions/setup-go@b7ad1dad31e06c5925ef5d2fc7ad053ef454303e` | Set up Go environment |
| 3. Initialize CodeQL | `github/codeql-action/init@e4fba868fa4b1b91e1fdab776edc8cfbe6e9fb81` | Configure CodeQL for Go language |
| 4. Fetch Dependencies | `go mod download` | Download modules for analysis |
| 5. Perform CodeQL Analysis | `github/codeql-action/analyze@e4fba868fa4b1b91e1fdab776edc8cfbe6e9fb81` | Run security queries |

**CodeQL Configuration:**

The analysis targets the Go language specifically:
- `languages: go` - Analyze Go source code
- `category: "/language:go"` - Categorize results

[.github/workflows/code_scanning.yaml:45-51]()

Results are automatically uploaded to the GitHub Security tab and can trigger security alerts.

**Sources:** [.github/workflows/code_scanning.yaml:1-52]()

---

### nvml-mock-publish.yaml - nvml-mock Image Publishing

**Purpose:** Build and publish multi-architecture Docker images for `nvml-mock` to `ghcr.io`.

**Inputs:** None

**Outputs:** None

**Permissions Required:**

```yaml
permissions:
  contents: read
  packages: write
  id-token: write # needed for keyless cosign signing
```
[.github/workflows/nvml-mock-publish.yaml:28-30]()

**Environment Variables:**
- `REGISTRY`: `ghcr.io`
- `IMAGE_NAME`: `nvidia/nvml-mock`

[.github/workflows/nvml-mock-publish.yaml:20-21]()

**Job Steps:**

| Step | Action | Purpose |
|------|--------|---------|
| 1. Checkout | `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` | Clone repository |
| 2. Set up QEMU | `docker/setup-qemu-action@96fe6ef7f33517b61c61be40b68a1882f3264fb8` | Enable multi-architecture builds |
| 3. Set up Docker Buildx | `docker/setup-buildx-action@bb05f3f5519dd87d3ba754cc423b652a5edd6d2c` | Configure Docker Buildx |
| 4. Log in to GHCR | `docker/login-action@abd2ef45e78c5afb21d64d4ca52ee8550d9572c7` | Authenticate to GitHub Container Registry |
| 5. Extract metadata | `docker/metadata-action@dc802804100637a589fabce1cb79ff13a1411302` | Generate image tags (latest, semver, SHA) |
| 6. Build and push | `docker/build-push-action@53b7df96c91f9c12dcc8a07bcb9ccacbed38856a` | Build and push `deployments/nvml-mock/Dockerfile` for `linux/amd64`, `linux/arm64` |
| 7. Install cosign | `sigstore/cosign-installer@6f9f17788090df1f26f669e9d70d6ae9567deba6` | Install Cosign for image signing |
| 8. Sign container image | Shell command | Sign the pushed image using Cosign |
| 9. Generate SBOM | `anchore/sbom-action@e22c389904149dbc22b58101806040fa8d37a610` | Generate Software Bill of Materials |
| 10. Attach SBOM to image | Shell command | Attest the SBOM to the signed image |

**Tagging Strategy:**
- `latest` for `main` branch pushes.
- Semantic version tags (e.g., `v0.1.0`, `0.1`) for tag pushes.
- Short SHA tag for traceability.

[.github/workflows/nvml-mock-publish.yaml:55-61]()

**Cosign Signing:**
The workflow uses Cosign for keyless signing of container images, leveraging OIDC for identity verification.
[.github/workflows/nvml-mock-publish.yaml:80-84]()

**SBOM Generation:**
An SBOM in SPDX-JSON format is generated and attached to the image as an attestation.
[.github/workflows/nvml-mock-publish.yaml:86-100]()

**Sources:** [.github/workflows/nvml-mock-publish.yaml:1-100]()

---

### helm.yaml - Helm Chart CI

**Purpose:** Lint and unit test the `nvml-mock` Helm chart.

**Inputs:** None

**Outputs:** None

**Environment Variables:**
- `CHART_NAME`: `nvml-mock`
- `CHART_DIR`: `deployments/nvml-mock/helm`

[.github/workflows/helm.yaml:21-22]()

**Job Steps:**

| Job | Step | Action | Purpose |
|-----|------|--------|---------|
| `lint` | 1. Checkout repository | `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` | Clone repository |
|     | 2. Set up chart-testing | `helm/chart-testing-action@6ec842c01de15ebb84c8627d2744a0c2f2755c9f` | Install `chart-testing` tool |
|     | 3. Run chart-testing (lint) | `ct lint` | Lint the Helm chart |
| `unittest` | 1. Checkout repository | `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` | Clone repository |
|     | 2. Set up Helm | `azure/setup-helm@9bc31f4ebc9c6b171d7bfbaa5d006ae7abdb4310` | Install Helm |
|     | 3. Install helm-unittest plugin | Shell command | Install `helm-unittest` plugin |
|     | 4. Run helm unittest | `helm unittest` | Execute Helm chart unit tests |

**Concurrency:**
The workflow uses `concurrency` to ensure only one `helm` workflow runs at a time for a given `ref`, cancelling in-progress runs.
[.github/workflows/helm.yaml:15-17]()

**Sources:** [.github/workflows/helm.yaml:1-59]()

---

### helm-publish.yaml - Helm Chart Publishing

**Purpose:** Package, push, and sign the `nvml-mock` Helm chart to `ghcr.io`.

**Inputs:** None

**Outputs:** None

**Permissions Required:**

```yaml
permissions:
  contents: read
  packages: write
  id-token: write # needed for keyless cosign signing
```
[.github/workflows/helm-publish.yaml:26-28]()

**Environment Variables:**
- `CHART_NAME`: `nvml-mock`
- `CHART_DIR`: `deployments/nvml-mock/helm`

[.github/workflows/helm-publish.yaml:18-19]()

**Job Steps:**

| Step | Action | Purpose |
|------|--------|---------|
| 1. Checkout repository | `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` | Clone repository at the `workflow_run`'s `head_sha` |
| 2. Set up Helm | `azure/setup-helm@9bc31f4ebc9c6b171d7bfbaa5d006ae7abdb4310` | Install Helm |
| 3. Read chart version | Shell command | Extract chart version from `Chart.yaml` |
| 4. Log in to GHCR | Shell command | Authenticate to GHCR for Helm OCI push |
| 5. Package chart | `helm package` | Create `.tgz` archive of the chart |
| 6. Push chart to OCI registry | Shell command | Push the chart to `oci://ghcr.io/nvidia/k8s-test-infra/chart` with retry logic |
| 7. Install cosign | `sigstore/cosign-installer@6f9f17788090df1f26f669e9d70d6ae9567deba6` | Install Cosign |
| 8. Log in to GHCR for cosign | `docker/login-action@abd2ef45e78c5afb21d64d4ca52ee8550d9572c7` | Authenticate to GHCR for Cosign signing |
| 9. Sign OCI artifact | Shell command | Sign the pushed Helm chart artifact |

**Retry Logic for Push:**
The `Push chart to OCI registry` step includes a retry mechanism for `helm push` to handle intermittent `404 not found` errors from GHCR during tag operations.
[.github/workflows/helm-publish.yaml:58-76]()

**Sources:** [.github/workflows/helm-publish.yaml:1-95]()

---

### scorecard.yaml - OpenSSF Scorecard Analysis

**Purpose:** Run OpenSSF Scorecard to assess supply chain security posture.

**Inputs:** None

**Outputs:** None (results uploaded to GitHub Security tab)

**Permissions Required:**

```yaml
permissions: read-all
```
[.github/workflows/scorecard.yaml:13]()
The `analysis` job requires `security-events: write` and `id-token: write`.
[.github/workflows/scorecard.yaml:19-20]()

**Job Steps:**

| Step | Action | Purpose |
|------|--------|---------|
| 1. Checkout | `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` | Clone repository |
| 2. Run Scorecard | `ossf/scorecard-action@2d1146689b8cda280b9bc96326124645441f03bc` | Execute Scorecard analysis |
| 3. Upload SARIF | `github/codeql-action/upload-sarif@e4fba868fa4b1b91e1fdab776edc8cfbe6e9fb81` | Upload results in SARIF format to GitHub Security tab |

**Sources:** [.github/workflows/scorecard.yaml:1-39]()

---

### stale.yaml - Stale Issue/PR Management

**Purpose:** Automatically mark and close stale issues and pull requests based on inactivity.

**Inputs:** None

**Outputs:** None

**Permissions Required:**

```yaml
permissions:
  issues: write
  pull-requests: write
```
[.github/workflows/stale.yaml:14-15]()

**Trigger:**
- **Scheduled cron job**: Daily at 01:30 UTC
- **Manual `workflow_dispatch`**

[.github/workflows/stale.yaml:9-11]()

**Job Steps:**

| Step | Action | Purpose |
|------|--------|---------|
| 1. Run stale action | `actions/stale@v10` | Apply stale logic based on configuration |

**Configuration Details:**
- `days-before-issue-stale`: 90 days
- `days-before-issue-close`: 30 days (after being marked stale)
- `days-before-pr-stale`: 90 days
- `days-before-pr-close`: 30 days
- `stale-issue-label`: `lifecycle/stale`
- `exempt-issue-labels`: `lifecycle/frozen`
- Custom messages for stale and close events.
- `remove-stale-when-updated`: `true`

[.github/workflows/stale.yaml:23-52]()

**Sources:** [.github/workflows/stale.yaml:1-53]()

---

## Variable Extraction Mechanism

The Go version extraction demonstrates the **single source of truth** principle. The version is defined once in `deployments/devel/Dockerfile` and extracted programmatically everywhere else.

**Version Extraction Flow Diagram**

```mermaid
sequenceDiagram
    participant WF as "variables.yaml Job"
    participant Script as "hack/golang-version.sh"
    participant DF as "deployments/devel/Dockerfile"
    participant Output as "GITHUB_OUTPUT"
    participant Consumer as "golang.yaml & code_scanning.yaml"
    
    WF->>Script: Execute ./hack/golang-version.sh
    Script->>DF: Read file
    Script->>Script: grep "^FROM golang:.*$"
    Script->>Script: Extract version with grep -oE "[0-9\.]+"
    Script->>WF: Return version string (e.g., "1.26.5")
    WF->>Output: Set golang_version output
    Output->>Consumer: Pass as inputs.golang_version
    Consumer->>Consumer: actions/setup-go@b7ad1dad31e06c5925ef5d2fc7ad053ef454303e with version
```

**Sources:** [.github/workflows/variables.yaml:44-47](), [hack/golang-version.sh:1-23](), [deployments/devel/Dockerfile:17]()

### hack/golang-version.sh Implementation

The extraction script uses standard Unix text processing:

**Script Location:** `hack/golang-version.sh`

**Key Operations:**

1. **Locate Dockerfile:**
   ```bash
   DOCKERFILE_ROOT=${SCRIPTS_DIR}/../deployments/devel
   ```
   [hack/golang-version.sh:18]()

2. **Extract Version:**
   ```bash
   GOLANG_VERSION=$(grep -E "^FROM golang:.*$" ${DOCKERFILE_ROOT}/Dockerfile | grep -oE "[0-9\.]+")
   ```
   [hack/golang-version.sh:20]()

3. **Output Version:**
   ```bash
   echo $GOLANG_VERSION
   ```
   [hack/golang-version.sh:22]()

The regex `^FROM golang:.*$` matches the Dockerfile FROM instruction, and `[0-9\.]+` extracts the numeric version string.

**Sources:** [hack/golang-version.sh:1-23]()

### Dockerfile as Version Source

The `deployments/devel/Dockerfile` serves as the authoritative source:

```dockerfile
# This Dockerfile is also used to define the golang version used in this project
# This allows dependabot to manage this version in addition to other images.
FROM golang:1.26.5
```
[deployments/devel/Dockerfile:15-17]()

The comment explicitly states that this Dockerfile defines the project's Go version, enabling Dependabot to detect and propose updates automatically.

**Sources:** [deployments/devel/Dockerfile:1-18]()

---

## Workflow Execution Lifecycle

The following diagram illustrates the complete execution flow from trigger to completion:

**Complete Workflow Execution Flow**

```mermaid
graph TB
    START["GitHub Event Trigger"]
    
    subgraph "ci.yaml Workflow"
        CI_BASIC["basic Job<br/>uses: ./.github/workflows/basic-checks.yaml"]
        CI_E2E["nvml-mock-e2e Job<br/>needs: basic"]
    end
    
    subgraph "basic-checks.yaml Workflow"
        VAR_START["variables Job Starts"]
        VAR_CHECKOUT["Step: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1"]
        VAR_SHA["Step: Generate Commit Short SHA<br/>GITHUB_SHA | cut -c1-8"]
        VAR_GO["Step: Get Golang Version<br/>./hack/golang-version.sh"]
        VAR_OUT["Outputs: version, golang_version"]
        
        GO_START["golang Job Starts<br/>needs: variables"]
        GO_CHECKOUT["Step: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1"]
        GO_SETUP["Step: actions/setup-go@b7ad1dad31e06c5925ef5d2fc7ad053ef454303e<br/>go-version: inputs.golang_version"]
        GO_LINT["Step: golangci/golangci-lint-action@ba0d7d2ec06a0ea1cb5fa41b2e4a3ab91d21278a"]
        GO_GOVET["Step: Run go vet"]
        GO_CHECK["Step: make check-modules"]
        GO_UNIT_TESTS["Step: Run unit tests"]
        GO_BUILD_SHIM["Step: Build mockpcisysfs shim"]
        GO_INTEGRATION_TESTS["Step: Run mockpcisysfs integration tests"]
        GO_VULNCHECK["Step: Run govulncheck"]
        
        SCAN_START["code-scanning Job Starts<br/>needs: variables"]
        SCAN_CHECKOUT["Step: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1"]
        SCAN_SETUP["Step: actions/setup-go@b7ad1dad31e06c5925ef5d2fc7ad053ef454303e<br/>go-version: inputs.golang_version"]
        SCAN_INIT["Step: github/codeql-action/init@e4fba868fa4b1b91e1fdab776edc8cfbe6e9fb81"]
        SCAN_DEPS["Step: go mod download"]
        SCAN_ANALYZE["Step: github/codeql-action/analyze@e4fba868fa4b1b91e1fdab776edc8cfbe6e9fb81"]
    end
    
    END["Workflow Complete<br/>Status: success or failure"]
    
    START --> CI_BASIC
    CI_BASIC --> VAR_START
    VAR_START --> VAR_CHECKOUT --> VAR_SHA --> VAR_GO --> VAR_OUT
    
    VAR_OUT --> GO_START
    VAR_OUT --> SCAN_START
    
    GO_START --> GO_CHECKOUT --> GO_SETUP --> GO_LINT --> GO_GOVET --> GO_CHECK --> GO_UNIT_TESTS --> GO_BUILD_SHIM --> GO_INTEGRATION_TESTS --> GO_VULNCHECK
    SCAN_START --> SCAN_CHECKOUT --> SCAN_SETUP --> SCAN_INIT --> SCAN_DEPS --> SCAN_ANALYZE
    
    GO_VULNCHECK --> CI_E2E
    SCAN_ANALYZE --> CI_E2E
    CI_E2E --> END
```

**Sources:** [.github/workflows/ci.yaml:1-37](), [.github/workflows/basic-checks.yaml:1-50](), [.github/workflows/variables.yaml:1-50](), [.github/workflows/golang.yaml:1-88](), [.github/workflows/code_scanning.yaml:1-52]()

---

## Workflow File Reference

### Complete File Listing

| File Path | Purpose | Trigger Type |
|-----------|---------|--------------|
| `.github/workflows/ci.yaml` | Main CI pipeline entry point | `push` |
| `.github/workflows/basic-checks.yaml` | Orchestrates parallel checks | `workflow_call`, `pull_request` |
| `.github/workflows/variables.yaml` | Extracts version metadata | `workflow_call` |
| `.github/workflows/golang.yaml` | Runs Go linting and module checks | `workflow_call` |
| `.github/workflows/code_scanning.yaml` | Performs CodeQL security analysis | `workflow_call` |
| `.github/workflows/nvml-mock-publish.yaml` | Builds and publishes `nvml-mock` Docker images | `push`, `workflow_dispatch` |
| `.github/workflows/helm.yaml` | Lints and unit tests Helm charts | `pull_request`, `push` (path-filtered) |
| `.github/workflows/helm-publish.yaml` | Packages, pushes, and signs Helm charts | `workflow_run` |
| `.github/workflows/scorecard.yaml` | Runs OpenSSF Scorecard analysis | `schedule`, `push`, `workflow_dispatch` |
| `.github/workflows/stale.yaml` | Manages stale issues and PRs | `schedule`, `workflow_dispatch` |
| `hack/golang-version.sh` | Shell script to extract Go version | N/A (utility script) |
| `deployments/devel/Dockerfile` | Defines Go version source of truth | N/A (config file) |

**Sources:** [.github/workflows/ci.yaml:1-37](), [.github/workflows/basic-checks.yaml:1-50](), [.github/workflows/variables.yaml:1-50](), [.github/workflows/golang.yaml:1-88](), [.github/workflows/code_scanning.yaml:1-52](), [.github/workflows/nvml-mock-publish.yaml:1-100](), [.github/workflows/helm.yaml:1-59](), [.github/workflows/helm-publish.yaml:1-95](), [.github/workflows/scorecard.yaml:1-39](), [.github/workflows/stale.yaml:1-53](), [hack/golang-version.sh:1-23](), [deployments/devel/Dockerfile:1-18]()

---

## GitHub Actions Versions

The workflows use pinned versions of GitHub Actions to ensure stability:

| Action | Version | Purpose |
|--------|---------|---------|
| `actions/checkout` | `3d3c42e5aac5ba805825da76410c181273ba90b1` (`v7.0.1`) | Repository checkout |
| `actions/setup-go` | `b7ad1dad31e06c5925ef5d2fc7ad053ef454303e` (`v7.0.0`) | Go environment setup |
| `golangci/golangci-lint-action` | `ba0d7d2ec06a0ea1cb5fa41b2e4a3ab91d21278a` (`v9`) | Go linting |
| `github/codeql-action/init` | `e4fba868fa4b1b91e1fdab776edc8cfbe6e9fb81` (`v4.37.3`) | CodeQL initialization |
| `github/codeql-action/analyze` | `e4fba868fa4b1b91e1fdab776edc8cfbe6e9fb81` (`v4.37.3`) | CodeQL analysis execution |
| `docker/setup-qemu-action` | `96fe6ef7f33517b61c61be40b68a1882f3264fb8` (`v4`) | QEMU setup for multi-arch builds |
| `docker/setup-buildx-action` | `bb05f3f5519dd87d3ba754cc423b652a5edd6d2c` (`v4`) | Docker Buildx setup |
| `docker/login-action` | `abd2ef45e78c5afb21d64d4ca52ee8550d9572c7` (`v4`) | Docker registry login |
| `docker/metadata-action` | `dc802804100637a589fabce1cb79ff13a1411302` (`v6`) | Docker image metadata extraction |
| `docker/build-push-action` | `53b7df96c91f9c12dcc8a07bcb9ccacbed38856a` (`v7`) | Docker image build and push |
| `sigstore/cosign-installer` | `6f9f17788090df1f26f669e9d70d6ae9567deba6` (`v4.1.2`) | Cosign installer |
| `anchore/sbom-action` | `e22c389904149dbc22b58101806040fa8d37a610` (`v0.24.0`) | SBOM generation |
| `azure/setup-helm` | `9bc31f4ebc9c6b171d7bfbaa5d006ae7abdb4310` (`v5`) | Helm setup |
| `helm/chart-testing-action` | `6ec842c01de15ebb84c8627d2744a0c2f2755c9f` (`v2.8.0`) | Helm chart testing setup |
| `ossf/scorecard-action` | `2d1146689b8cda280b9bc96326124645441f03bc` (`v2.4.4`) | OpenSSF Scorecard |
| `actions/stale` | `v10` | Stale issue/PR management |

These versions are managed by Dependabot (see [Dependency Updates with Dependabot](#4.4)) to ensure security patches are applied promptly.

**Sources:** [.github/workflows/variables.yaml:38](), [.github/workflows/golang.yaml:31-35](), [.github/workflows/code_scanning.yaml:36-49](), [.github/workflows/nvml-mock-publish.yaml:31-41](), [.github/workflows/nvml-mock-publish.yaml:49-52](), [.github/workflows/nvml-mock-publish.yaml:65-68](), [.github/workflows/nvml-mock-publish.yaml:77-78](), [.github/workflows/helm.yaml:30-33](), [.github/workflows/helm.yaml:49-50](), [.github/workflows/helm-publish.yaml:32-33](), [.github/workflows/helm-publish.yaml:77-78](), [.github/workflows/helm-publish.yaml:85-86](), [.github/workflows/scorecard.yaml:24-29](), [.github/workflows/scorecard.yaml:36-37](), [.github/workflows/stale.yaml:21-22]()

---

## Summary

The GitHub Actions workflow architecture in k8s-test-infra demonstrates several best practices:

1.  **Modular Design**: Reusable workflows promote code reuse and maintainability.
2.  **Explicit Dependencies**: The `needs` keyword creates clear job execution order.
3.  **Single Source of Truth**: Go version is defined once in the Dockerfile.
4.  **Parallel Execution**: Independent jobs run concurrently for faster feedback.
5.  **Security Focus**: CodeQL scanning runs on every change with appropriate permissions, and OpenSSF Scorecard provides supply chain security insights.
6.  **Dual Trigger Support**: Workflows respond to both push and pull request events.
7.  **Automated Publishing**: Container images and Helm charts are automatically built, pushed, and signed.
8.  **Lifecycle Management**: Stale issues and PRs are automatically managed to keep the repository clean.

This architecture ensures consistent, automated validation of code quality and security across all contributions to the repository, and streamlines the release process for `nvml-mock` artifacts.

**Sources:** [.github/workflows/ci.yaml:1-37](), [.github/workflows/basic-checks.yaml:1-50](), [.github/workflows/variables.yaml:1-50](), [.github/workflows/golang.yaml:1-88](), [.github/workflows/code_scanning.yaml:1-52](), [.github/workflows/nvml-mock-publish.yaml:1-100](), [.github/workflows/helm.yaml:1-59](), [.github/workflows/helm-publish.yaml:1-95](), [.github/workflows/scorecard.yaml:1-39](), [.github/workflows/stale.yaml:1-53](), [hack/golang-version.sh:1-23](), [deployments/devel/Dockerfile:1-18]()

---

# Page: Automated Testing and Code Quality

# Automated Testing and Code Quality

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/code_scanning.yaml](.github/workflows/code_scanning.yaml)
- [.github/workflows/golang.yaml](.github/workflows/golang.yaml)
- [.github/workflows/helm-publish.yaml](.github/workflows/helm-publish.yaml)
- [.github/workflows/helm.yaml](.github/workflows/helm.yaml)
- [.github/workflows/nvml-mock-publish.yaml](.github/workflows/nvml-mock-publish.yaml)
- [.github/workflows/scorecard.yaml](.github/workflows/scorecard.yaml)
- [.github/workflows/variables.yaml](.github/workflows/variables.yaml)
- [.golangci.yml](.golangci.yml)
- [deployments/devel/Dockerfile](deployments/devel/Dockerfile)
- [tests/e2e/go/report_skips_test.go](tests/e2e/go/report_skips_test.go)

</details>



This document details the automated testing and code quality enforcement mechanisms that run as part of the CI/CD pipeline. It covers linting with golangci-lint, security scanning with CodeQL, module consistency verification, and vulnerability scanning with `govulncheck`.

For information about the overall GitHub Actions workflow structure and job orchestration, see [GitHub Actions Workflows](#4.1). For details about the Ginkgo test framework and test execution, see [Testing with Ginkgo](#5). For dependency update automation, see [Dependency Updates with Dependabot](#4.4).

---

## Overview of Automated Quality Checks

The repository enforces code quality through several automated mechanisms, all integrated into the CI pipeline:

| Check Type | Tool | Purpose | Workflow File |
|------------|------|---------|---------------|
| **Linting** | golangci-lint | Enforce Go code style, detect common issues, verify code patterns | [.github/workflows/golang.yaml]() |
| **Security Scanning** | CodeQL | Static analysis for security vulnerabilities and code quality issues | [.github/workflows/code_scanning.yaml]() |
| **Vulnerability Scanning** | govulncheck | Detect known vulnerabilities in Go modules | [.github/workflows/golang.yaml]() |
| **Module Verification** | go mod | Ensure dependency consistency between go.mod, go.sum, and vendor directory | [.github/workflows/golang.yaml]() |
| **OpenSSF Scorecard** | Scorecard | Assess security health of the project | [.github/workflows/scorecard.yaml]() |

These checks run automatically on pull requests and pushes to protected branches, preventing code that violates quality standards from being merged.

**Sources:** [.github/workflows/golang.yaml](), [.github/workflows/code_scanning.yaml](), [.github/workflows/scorecard.yaml]()

---

## Quality Check Execution Flow

```mermaid
graph TB
    subgraph "Trigger Events"
        PR["Pull Request"]
        PUSH["Push to main/release"]
        SCHEDULE["Scheduled Run<br/>(e.g., Scorecard)"]
    end
    
    subgraph "Variable Extraction"
        VARS["variables job<br/>(.github/workflows/variables.yaml)"]
        VARS_VERSION["Extract commit SHA"]
        VARS_GO["Extract Go version<br/>(hack/golang-version.sh)"]
        
        VARS --> VARS_VERSION
        VARS --> VARS_GO
    end
    
    subgraph "Parallel Quality Checks"
        GOLANG["golang job<br/>(.github/workflows/golang.yaml)"]
        CODEQL["code-scanning job<br/>(.github/workflows/code_scanning.yaml)"]
        SCORECARD["scorecard job<br/>(.github/workflows/scorecard.yaml)"]
    end
    
    subgraph "Golang Job Steps"
        CHECKOUT1["actions/checkout@v7"]
        SETUP_GO1["actions/setup-go@v7"]
        LINT["golangci-lint-action@v9<br/>Runs: golangci-lint run"]
        GOVET["go vet ./..."]
        CHECK_MOD["make check-modules<br/>Verifies go.mod/go.sum/vendor"]
        UNIT_TESTS["go test -v -race -coverprofile=coverage.out -covermode=atomic"]
        MOCKPCISYSFS_BUILD["make -C pkg/system/mockpcisysfs"]
        MOCKPCISYSFS_TESTS["go test -tags integration ./pkg/system/mockpcisysfs/..."]
        GOVULNCHECK["govulncheck ./..."]
        
        CHECKOUT1 --> SETUP_GO1
        SETUP_GO1 --> LINT
        LINT --> GOVET
        GOVET --> CHECK_MOD
        CHECK_MOD --> UNIT_TESTS
        UNIT_TESTS --> MOCKPCISYSFS_BUILD
        MOCKPCISYSFS_BUILD --> MOCKPCISYSFS_TESTS
        MOCKPCISYSFS_TESTS --> GOVULNCHECK
    end
    
    subgraph "CodeQL Job Steps"
        CHECKOUT2["actions/checkout@v7"]
        SETUP_GO2["actions/setup-go@v7"]
        INIT_QL["codeql-action/init@v4<br/>Languages: go"]
        FETCH_DEPS["go mod download"]
        ANALYZE_QL["codeql-action/analyze@v4<br/>Category: /language:go"]
        
        CHECKOUT2 --> SETUP_GO2
        SETUP_GO2 --> INIT_QL
        INIT_QL --> FETCH_DEPS
        FETCH_DEPS --> ANALYZE_QL
    end

    subgraph "Scorecard Job Steps"
        CHECKOUT3["actions/checkout@v7"]
        RUN_SCORECARD["ossf/scorecard-action@v2<br/>results_file: results.sarif"]
        UPLOAD_SARIF["github/codeql-action/upload-sarif@v4"]

        CHECKOUT3 --> RUN_SCORECARD
        RUN_SCORECARD --> UPLOAD_SARIF
    end
    
    PR --> VARS
    PUSH --> VARS
    SCHEDULE --> SCORECARD
    
    VARS_GO --> SETUP_GO1
    VARS_GO --> SETUP_GO2
    
    VARS --> GOLANG
    VARS --> CODEQL
    
    GOLANG --> CHECKOUT1
    CODEQL --> CHECKOUT2
```

**Sources:** [.github/workflows/golang.yaml](), [.github/workflows/code_scanning.yaml](), [.github/workflows/variables.yaml](), [.github/workflows/scorecard.yaml]()

---

## Linting with golangci-lint

### Configuration

The linting process uses `golangci-lint`, a fast, parallel Go linter aggregator that runs multiple linters in a single pass. The workflow invokes it via the `golangci-lint-action@v9` GitHub Action.

Key configuration parameters from [.github/workflows/golang.yaml:36-41]():

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `version` | `latest` | Always use the newest golangci-lint release |
| `args` | `-v --timeout 5m` | Verbose output with 5-minute timeout |
| `skip-cache` | `true` | Disable caching to ensure fresh analysis |

The `.golangci.yml` configuration file [`.golangci.yml:15-27`]() specifies a `timeout` of `5m` and `build-tags` for `e2e` and `integration` to ensure all relevant code, including test-only files, is linted.

### Linting Workflow Step

```mermaid
graph LR
    subgraph "Linting Process"
        INPUT["Go Source Files<br/>(*.go)"]
        ACTION["golangci-lint-action@v9"]
        BINARY["golangci-lint binary"]
        CONFIG["Custom Configuration<br/>(.golangci.yml)"]
        
        LINTERS["Enabled Linters:<br/>- errcheck<br/>- gosimple<br/>- govet<br/>- ineffassign<br/>- staticcheck<br/>- typecheck<br/>- unused<br/>...and others configured in .golangci.yml"]
        
        OUTPUT["Lint Report<br/>GitHub Check Annotations"]
        FAIL["Exit Code ≠ 0<br/>CI Failure"]
        PASS["Exit Code = 0<br/>CI Success"]
    end
    
    INPUT --> ACTION
    ACTION --> BINARY
    BINARY --> CONFIG
    CONFIG --> LINTERS
    LINTERS --> OUTPUT
    OUTPUT --> FAIL
    OUTPUT --> PASS
```

The `.golangci.yml` file [`.golangci.yml`]() defines specific settings for linters and exclusions. For example, `staticcheck` is configured to exclude certain checks like `ST1000`, `ST1003`, and `QF*` [`.golangci.yml:30-36`](). It also includes an exclusion rule for `ST1001` in `tests/e2e/go/` files to accommodate Ginkgo's dot-import convention in test-only code [`.golangci.yml:38-52`](). The `max-same-issues` is set to `0` to report every occurrence of an issue, preventing under-reporting [`.golangci.yml:55-60`]().

**Sources:** [.github/workflows/golang.yaml:36-41](), [`.golangci.yml`]()

### Local Linting Execution

Developers can run the same linting checks locally using the Makefile target:

```bash
make lint
```

This executes the command defined at [Makefile:41-42]():

```bash
golangci-lint run ./...
```

The `./...` pattern recursively analyzes all Go packages in the repository, excluding the vendor directory automatically.

**Sources:** [Makefile:41-42]()

---

## Automated Test Execution

The `golang.yaml` workflow also orchestrates the execution of automated tests.

### Go Vet

The `go vet` tool is run explicitly to catch common errors. This step is not redundant with the `govet` linter within `golangci-lint` because `go vet` has no suppression mechanism, ensuring all findings are reported, and `golangci-lint` caps repeats of the same finding [`.github/workflows/golang.yaml:47-62`]().

```yaml
- name: Run go vet
  run: go vet ./...
```

**Sources:** [.github/workflows/golang.yaml:47-62]()

### Unit Tests

Standard Go unit tests are executed with race detection and coverage reporting.

```yaml
- name: Run unit tests
  run: |
    go test -v -race -coverprofile=coverage.out -covermode=atomic $(go list ./... | grep -v vendor)
```

**Sources:** [.github/workflows/golang.yaml:68-70]()

### Integration Tests for `mockpcisysfs`

The `mockpcisysfs` LD_PRELOAD shim has dedicated integration tests that are run explicitly. These tests are tagged with `integration` and are skipped by the untagged unit test run [`.github/workflows/golang.yaml:72-82`]().

```yaml
- name: Build mockpcisysfs shim
  run: make -C pkg/system/mockpcisysfs

- name: Run mockpcisysfs integration tests
  run: go test -tags integration -v ./pkg/system/mockpcisysfs/...
```

**Sources:** [.github/workflows/golang.yaml:72-82]()

### Skipped Specs Summary in E2E Tests

For E2E tests, a `ReportAfterSuite` hook is used to print a consolidated summary of all skipped specs and their reasons. This helps in quickly identifying what was skipped and why, especially in verbose multi-profile logs [tests/e2e/go/report_skips_test.go:20-57](). The `emptySkipReason` function provides a cause-neutral marker for specs skipped without a specific message, hinting at configured filters [tests/e2e/go/report_skips_test.go:61-78]().

**Sources:** [tests/e2e/go/report_skips_test.go:20-78]()

---

## Security Scanning with CodeQL

### CodeQL Analysis Workflow

CodeQL is GitHub's semantic code analysis engine that treats code as data, enabling queries to find security vulnerabilities and code quality issues. The `code_scanning.yaml` workflow performs static analysis on Go code.

```mermaid
graph TB
    subgraph "CodeQL Initialization"
        INIT["codeql-action/init@v4"]
        LANG["Language: go"]
        QUERIES["Default Query Suites<br/>security-extended<br/>security-and-quality"]
        
        INIT --> LANG
        INIT --> QUERIES
    end
    
    subgraph "Dependency Resolution"
        FETCH["go mod download"]
        MODCACHE["Go Module Cache<br/>$GOPATH/pkg/mod"]
        
        FETCH --> MODCACHE
    end
    
    subgraph "CodeQL Analysis"
        ANALYZE["codeql-action/analyze@v4"]
        EXTRACT["Extract Code<br/>Build Abstract Syntax Tree"]
        RUNQUERIES["Run Security Queries"]
        CATEGORY["Category: /language:go"]
        
        ANALYZE --> EXTRACT
        EXTRACT --> RUNQUERIES
        RUNQUERIES --> CATEGORY
    end
    
    subgraph "Results"
        SARIF["SARIF Report"]
        UPLOAD["Upload to GitHub<br/>Security Tab"]
        ALERTS["Code Scanning Alerts"]
        
        CATEGORY --> SARIF
        SARIF --> UPLOAD
        UPLOAD --> ALERTS
    end
    
    QUERIES --> EXTRACT
    MODCACHE --> EXTRACT
```

**Sources:** [.github/workflows/code_scanning.yaml]()

### Workflow Configuration

The CodeQL workflow at [.github/workflows/code_scanning.yaml:24-51]() runs with the following configuration:

| Setting | Value | Purpose |
|---------|-------|---------|
| `timeout-minutes` | `360` | Allow up to 6 hours for analysis (generous for large codebases) |
| `permissions.security-events` | `write` | Required to upload SARIF results |
| `permissions.packages` | `read` | Access private dependencies if needed |
| `languages` | `go` | Analyze Go code only |
| `category` | `/language:go` | Categorize results by language |

The workflow requires the `golang_version` input from the `variables` job (see [Version Management](#4.3)), ensuring consistency between analysis and build environments.

### Analysis Steps

The CodeQL analysis executes three key steps:

1. **Initialize CodeQL** [.github/workflows/code_scanning.yaml:40-43]()
   - Sets up the CodeQL tools
   - Configures language detection for Go
   - Prepares the analysis environment

2. **Fetch Dependencies** [.github/workflows/code_scanning.yaml:45-46]()
   - Downloads Go modules via `go mod download`
   - Ensures all dependencies are available for analysis
   - Populates the module cache

3. **Perform Analysis** [.github/workflows/code_scanning.yaml:48-51]()
   - Extracts code structure into CodeQL database
   - Runs security and quality queries
   - Uploads results to GitHub Security tab

Results appear in the repository's "Security" → "Code scanning" tab, where they can be reviewed, triaged, and dismissed.

**Sources:** [.github/workflows/code_scanning.yaml:40-51]()

---

## Vulnerability Scanning with `govulncheck`

The `golang.yaml` workflow includes a step to run `govulncheck`, a tool that finds known vulnerabilities in Go modules.

```yaml
- name: Run govulncheck
  run: |
    go install golang.org/x/vuln/cmd/govulncheck@latest
    govulncheck ./...
```

This step first installs the `govulncheck` tool and then runs it across all Go modules in the repository [`.github/workflows/golang.yaml:83-87`](). This helps identify and mitigate security risks introduced by third-party dependencies.

**Sources:** [.github/workflows/golang.yaml:83-87]()

---

## OpenSSF Scorecard

The OpenSSF Scorecard is an automated tool that assesses the security health of open source projects. The `scorecard.yaml` workflow runs this check.

### Workflow Configuration

The Scorecard workflow at [.github/workflows/scorecard.yaml:1-39]() is triggered on a weekly schedule (Monday at 06:00 UTC), on pushes to the `main` branch, and manually via `workflow_dispatch`.

| Setting | Value | Purpose |
|---------|-------|---------|
| `schedule` | `cron: "0 6 * * 1"` | Run every Monday at 06:00 UTC |
| `push` | `branches: [main]` | Run on pushes to the main branch |
| `workflow_dispatch` | | Allow manual triggering |
| `permissions.security-events` | `write` | Required to upload SARIF results |
| `permissions.id-token` | `write` | Required for keyless cosign signing (if used by Scorecard) |

### Scorecard Analysis Steps

```mermaid
graph TD
    subgraph "Scorecard Analysis"
        CHECKOUT["actions/checkout@v7"]
        RUN_SCORECARD["ossf/scorecard-action@v2"]
        RESULTS_FILE["results_file: results.sarif"]
        PUBLISH_RESULTS["publish_results: true"]
        UPLOAD_SARIF["github/codeql-action/upload-sarif@v4"]
        
        CHECKOUT --> RUN_SCORECARD
        RUN_SCORECARD --> RESULTS_FILE
        RUN_SCORECARD --> PUBLISH_RESULTS
        PUBLISH_RESULTS --> UPLOAD_SARIF
    end
```

The workflow performs the following steps:
1. **Checkout Code** [`.github/workflows/scorecard.yaml:24-27`]: Checks out the repository code.
2. **Run Scorecard** [`.github/workflows/scorecard.yaml:29-33`]: Executes the `ossf/scorecard-action` to analyze the project. It outputs results to `results.sarif` and publishes them.
3. **Upload SARIF** [`.github/workflows/scorecard.yaml:35-38`]: Uploads the generated SARIF file to GitHub, making the findings visible in the Security tab.

**Sources:** [.github/workflows/scorecard.yaml:1-39]()

---

## Module Consistency Verification

### Purpose and Requirements

Go module management requires synchronization between three key components:

| Component | Purpose | Managed By |
|-----------|---------|------------|
| `go.mod` | Declares direct dependencies and Go version | Developer + `go mod tidy` |
| `go.sum` | Cryptographic checksums for reproducible builds | `go` toolchain |
| `vendor/` | Local copy of dependencies for hermetic builds | `go mod vendor` |

The CI pipeline enforces that these three components remain synchronized, preventing issues where local builds succeed but CI fails (or vice versa).

**Sources:** [Makefile:52-79]()

### Module Verification Process

```mermaid
graph TB
    subgraph "Module Verification Steps"
        START["make check-modules"]
        
        subgraph "Tidy Phase (.mod-tidy)"
            TIDY["go mod tidy<br/>for each go.mod"]
            TIDY_CHECK["Check for changes"]
        end
        
        subgraph "Vendor Phase (.mod-vendor)"
            VENDOR["go mod vendor<br/>for each go.mod"]
            VENDOR_CHECK["Check for changes"]
        end
        
        subgraph "Verify Phase (.mod-verify)"
            VERIFY["go mod verify<br/>for each go.mod"]
            VERIFY_CHECK["Validate checksums"]
        end
        
        subgraph "Git Diff Checks"
            DIFF_MOD["git diff --exit-code<br/>go.mod go.sum"]
            DIFF_VENDOR["git diff --exit-code<br/>vendor/"]
        end
        
        START --> TIDY
        TIDY --> TIDY_CHECK
        TIDY_CHECK --> VENDOR
        VENDOR --> VENDOR_CHECK
        VENDOR_CHECK --> VERIFY
        VERIFY --> VERIFY_CHECK
        VERIFY_CHECK --> DIFF_MOD
        DIFF_MOD --> DIFF_VENDOR
        
        DIFF_VENDOR -->|No changes| SUCCESS["Exit 0<br/>CI Pass"]
        DIFF_VENDOR -->|Changes found| FAILURE["Exit 1<br/>CI Failure"]
    end
```

**Sources:** [Makefile:52-79]()

### Makefile Target Breakdown

The `check-modules` target at [Makefile:75-79]() orchestrates the verification process:

```bash
check-modules: modules
	@echo "- Checking if go.mod and go.sum are in sync..."
	@git diff --exit-code -- $$(find . -name go.mod -name go.sum)
	@echo "- Checking if the go mod vendor dir is in sync..."
	@git diff --exit-code -- $$(find . -name vendor)
```

It depends on the `modules` target [Makefile:53](), which executes three sub-targets:

1. **.mod-tidy** [Makefile:54-59]() - Runs `go mod tidy` for all modules
2. **.mod-vendor** [Makefile:61-66]() - Runs `go mod vendor` for all modules (excluding deployments)
3. **.mod-verify** [Makefile:68-73]() - Runs `go mod verify` to validate checksums

The workflow excludes certain directories from vendoring: `testdata`, `third_party`, and `deployments`.

**Sources:** [Makefile:52-79]()

### CI Workflow Integration

The golang workflow invokes this check at [.github/workflows/golang.yaml:64-66]():

```yaml
- name: Check golang modules
  run: |
    make check-modules
```

If any module files are out of sync, the CI job fails with a non-zero exit code, preventing the PR from being merged until the developer runs:

```bash
make vendor
git add go.mod go.sum vendor
git commit -m "Update vendored dependencies"
```

**Sources:** [.github/workflows/golang.yaml:64-66](), [Makefile:44-50]()

---

## Integration with CI Pipeline

### Workflow Dependencies

The quality checks integrate into the broader CI pipeline through workflow composition. The `basic-checks.yaml` workflow (referenced but not shown in provided files) calls these reusable workflows:

```mermaid
graph TB
    subgraph "basic-checks workflow"
        TRIGGER["Trigger:<br/>pull_request<br/>push to main/release"]
    end
    
    subgraph "Called Workflows"
        VARS["variables.yaml<br/>Extract golang_version"]
        GOLANG["golang.yaml<br/>Depends on: variables"]
        CODEQL["code_scanning.yaml<br/>Depends on: variables"]
        SCORECARD["scorecard.yaml"]
    end
    
    subgraph "Inputs and Outputs"
        VARS_OUT["outputs.golang_version"]
        GOLANG_IN["inputs.golang_version"]
        CODEQL_IN["inputs.golang_version"]
    end
    
    TRIGGER --> VARS
    VARS --> VARS_OUT
    VARS_OUT --> GOLANG_IN
    VARS_OUT --> CODEQL_IN
    GOLANG_IN --> GOLANG
    CODEQL_IN --> CODEQL
    
    GOLANG -->|Pass/Fail| STATUS["CI Status Check"]
    CODEQL -->|Pass/Fail| STATUS
    SCORECARD -->|Pass/Fail| STATUS
```

Both `golang.yaml` and `code_scanning.yaml` are reusable workflows (declared with `workflow_call`) that require the `golang_version` input. This input comes from the `variables.yaml` workflow, which extracts the Go version from the Dockerfile using `hack/golang-version.sh`. The `scorecard.yaml` workflow runs independently based on its own triggers.

**Sources:** [.github/workflows/golang.yaml:17-22](), [.github/workflows/code_scanning.yaml:17-21](), [.github/workflows/variables.yaml:15-44](), [.github/workflows/scorecard.yaml]()

### Required Status Checks

For protected branches, these workflows typically serve as required status checks that must pass before merging:

| Check Name | Blocks Merge | Provides |
|------------|--------------|----------|
| `check / golang` | Yes | Linting, automated tests, and module verification |
| `analyze / CodeQL` | Yes | Security vulnerability scanning |
| `analysis / Scorecard` | Yes | Project security health assessment |

The copy-pr-bot configuration at [.github/copy-pr-bot.yaml]() indicates the repository uses NVIDIA's internal tooling for PR management, which likely enforces these checks as well.

**Sources:** [.github/copy-pr-bot.yaml]()

---

## Running Checks Locally

### Pre-Commit Verification

Developers should run these checks locally before pushing commits to avoid CI failures:

```bash
# Run linting
make lint

# Verify module consistency
make check-modules

# Format code (auto-fix)
make fmt
```

The `verify` target at [Makefile:34-39]() checks if code formatting is correct without modifying files, useful for pre-commit hooks:

```bash
make verify
```

This differs from `make fmt`, which automatically formats code.

**Sources:** [Makefile:31-42]()

### Fixing Module Inconsistencies

If `make check-modules` fails, run:

```bash
make vendor
```

This target at [Makefile:44-47]() executes:
1. `go mod tidy` - Remove unused dependencies and add missing ones
2. `go mod vendor` - Synchronize the vendor directory
3. `go mod verify` - Validate checksums

After running this command, commit the updated files:

```bash
git add go.mod go.sum vendor
git commit -m "Sync Go module dependencies"
```

**Sources:** [Makefile:44-47]()

### Installing golangci-lint Locally

To run linting locally, install golangci-lint:

```bash
# macOS
brew install golangci-lint

# Linux
curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b $(go env GOPATH)/bin

# Verify installation
golangci-lint --version
```

The CI uses the latest version via [.github/workflows/golang.yaml:39](), so keeping the local installation up-to-date ensures consistency.

**Sources:** [.github/workflows/golang.yaml:39]()

---

## Summary

The automated testing and code quality infrastructure provides multiple layers of protection:

1. **golangci-lint** - Enforces Go best practices and catches common errors.
2. **Go Vet** - Catches common errors with no suppression mechanism.
3. **Unit and Integration Tests** - Verifies functionality and behavior.
4. **govulncheck** - Detects known vulnerabilities in Go modules.
5. **CodeQL** - Detects security vulnerabilities and complex code quality issues.
6. **OpenSSF Scorecard** - Assesses the overall security health of the project.
7. **Module verification** - Ensures reproducible builds through dependency consistency.

These checks run automatically on every pull request and are designed to catch issues early in the development cycle. Developers can run the same checks locally using the Makefile targets, enabling a fast feedback loop before pushing changes.

**Sources:** [.github/workflows/golang.yaml](), [.github/workflows/code_scanning.yaml](), [.github/workflows/scorecard.yaml](), [Makefile]()

---

# Page: Version Management

# Version Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/code_scanning.yaml](.github/workflows/code_scanning.yaml)
- [.github/workflows/golang.yaml](.github/workflows/golang.yaml)
- [.github/workflows/helm-publish.yaml](.github/workflows/helm-publish.yaml)
- [.github/workflows/helm.yaml](.github/workflows/helm.yaml)
- [.github/workflows/nvml-mock-publish.yaml](.github/workflows/nvml-mock-publish.yaml)
- [.github/workflows/scorecard.yaml](.github/workflows/scorecard.yaml)
- [.github/workflows/variables.yaml](.github/workflows/variables.yaml)
- [deployments/devel/Dockerfile](deployments/devel/Dockerfile)
- [deployments/nvml-mock/Dockerfile](deployments/nvml-mock/Dockerfile)
- [pkg/gpu/mockcuda/Makefile](pkg/gpu/mockcuda/Makefile)
- [pkg/gpu/mocknvml/Dockerfile](pkg/gpu/mocknvml/Dockerfile)
- [pkg/gpu/mocknvml/Makefile](pkg/gpu/mocknvml/Makefile)
- [tests/e2e/spike-nvidia-smi.sh](tests/e2e/spike-nvidia-smi.sh)
- [tests/mocknvml/Dockerfile](tests/mocknvml/Dockerfile)
- [tests/poc-validation/setup-kind-cluster.sh](tests/poc-validation/setup-kind-cluster.sh)

</details>



## Purpose and Scope

This document explains the version management strategy used in the k8s-test-infra repository, specifically focusing on how the Go language version is maintained and propagated throughout the system. The repository employs a **single-source-of-truth** pattern to ensure consistency across local development, CI/CD pipelines, and Docker images.

For information about dependency version management (Go modules, Docker base images, GitHub Actions), see [Dependency Updates with Dependabot](#4.4). For details about the build system that consumes these versions, see [Build System](#8).

---

## Single Source of Truth Pattern

The k8s-test-infra repository defines the Go version exactly once in [`deployments/devel/Dockerfile:17`](), using the `FROM` directive. This file serves as the canonical source for the Go version used across all environments:

```dockerfile
FROM golang:1.26.5
```

The comment at [`deployments/devel/Dockerfile:15-16`]() explicitly documents this design decision:

```dockerfile
# This Dockerfile is also used to define the golang version used in this project
# This allows dependabot to manage this version in addition to other images.
```

This approach provides several key benefits:
- **Consistency**: The same Go version is used in development containers, CI runners, and local builds
- **Single update point**: Version upgrades require changing only one file
- **Dependabot integration**: The Dockerfile format allows Dependabot to automatically detect and propose Go version updates
- **Traceability**: All version changes are tracked through git history of a single file

Sources: [`deployments/devel/Dockerfile:15-17`]()

---

## Version Flow Architecture

The following diagram illustrates how the Go version flows from its definition through extraction and propagation to all consuming systems:

```mermaid
graph TB
    subgraph "Source of Truth"
        DOCKERFILE["deployments/devel/Dockerfile<br/>FROM golang:1.26.5"]
    end
    
    subgraph "Extraction Layer"
        SCRIPT["hack/golang-version.sh<br/>grep and extract version"]
    end
    
    subgraph "CI/CD Coordination"
        VARIABLES["variables.yaml workflow<br/>outputs: golang_version"]
    end
    
    subgraph "Consuming Workflows"
        GOLANG["golang.yaml workflow<br/>inputs.golang_version"]
        SCANNING["code_scanning.yaml workflow<br/>inputs.golang_version"]
        # BASIC["basic-checks.yaml workflow<br/>orchestrates all checks"]
    end
    
    subgraph "Execution Environment"
        GOSETUP["actions/setup-go@v7<br/>go-version: $golang_version"]
        CONTAINER["Docker Image Build<br/>golang:1.26.5 base"]
    end
    
    DOCKERFILE -->|"defines version"| SCRIPT
    SCRIPT -->|"extracts GOLANG_VERSION"| VARIABLES
    VARIABLES -->|"outputs golang_version"| GOLANG
    VARIABLES -->|"outputs golang_version"| SCANNING
    GOLANG -->|"uses in"| GOSETUP
    SCANNING -->|"uses in"| GOSETUP
    DOCKERFILE -->|"used directly in"| CONTAINER
```

**Version Flow: From Definition to Execution**

Sources: [`deployments/devel/Dockerfile:17`](), [`hack/golang-version.sh:1-23`](), [`.github/workflows/variables.yaml:1-45`](), [`.github/workflows/golang.yaml:1-72`](), [`.github/workflows/code_scanning.yaml:1-54`]()

---

## Version Definition: The Dockerfile Approach

The [`deployments/devel/Dockerfile`]() serves a dual purpose:
1. **Primary**: Defines a development container for the project
2. **Secondary**: Acts as the authoritative source for the Go version

### Why Use a Dockerfile?

The choice to use a Dockerfile rather than a separate configuration file provides several advantages:

| Advantage | Description |
|-----------|-------------|
| **Dependabot compatibility** | Dependabot natively understands Dockerfiles and can detect base image version updates |
| **Enforcement through use** | The version defined here is actually used to build development containers |
| **Industry standard format** | Follows Docker's established base image specification syntax |
| **Git-trackable** | Version changes are visible in PR diffs and git history |

### File Structure

The Dockerfile is minimal, containing only the base image declaration:

```
Line 1-13:  Copyright and license header
Line 14:    (blank)
Line 15-16: Comment explaining the version management role
Line 17:    FROM golang:1.26.5
Line 18:    (blank, end of file)
```

The version string follows the format `golang:MAJOR.MINOR.PATCH` where the numeric version (currently `1.26.5`) is extracted by the parsing script.

Sources: [`deployments/devel/Dockerfile:1-18`]()

---

## Version Extraction: golang-version.sh

The [`hack/golang-version.sh`]() script extracts the Go version from the Dockerfile and outputs it to stdout for consumption by CI workflows.

### Script Implementation

```mermaid
flowchart LR
    START["Script Execution"]
    LOCATE["Locate Dockerfile<br/>$SCRIPTS_DIR/../deployments/devel"]
    GREP1["grep -E '^FROM golang:.*$'<br/>Find FROM line"]
    GREP2["grep -oE '[0-9\.]+'<br/>Extract version number"]
    OUTPUT["echo $GOLANG_VERSION<br/>Output to stdout"]
    
    START --> LOCATE
    LOCATE --> GREP1
    GREP1 --> GREP2
    GREP2 --> OUTPUT
```

**golang-version.sh Execution Flow**

### Key Implementation Details

The script uses a two-stage grep pipeline at [`hack/golang-version.sh:20`]():

```bash
GOLANG_VERSION=$(grep -E "^FROM golang:.*$" ${DOCKERFILE_ROOT}/Dockerfile | grep -oE "[0-9\.]+")
```

**Stage 1: Line Selection**
- Pattern: `^FROM golang:.*$`
- Matches: Lines starting with "FROM golang:"
- Example match: `FROM golang:1.26.5`

**Stage 2: Version Extraction**
- Pattern: `[0-9\.]+`
- Extracts: Sequences of digits and dots
- Result: `1.26.5`

### Directory Resolution

The script determines the Dockerfile location relative to its own path at [`hack/golang-version.sh:16-18`]():

```bash
SCRIPTS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/../hack && pwd )"
DOCKERFILE_ROOT=${SCRIPTS_DIR}/../deployments/devel
```

This makes the script location-independent—it can be executed from any working directory.

Sources: [`hack/golang-version.sh:16-22`]()

---

## Version Propagation in CI/CD

The Go version propagates through the GitHub Actions workflow system via a reusable workflow pattern. The `variables.yaml` workflow acts as a central distribution point.

### Workflow Architecture

```mermaid
graph TB
    subgraph "Entry Point Workflows"
        CI["golang.yaml<br/>on: workflow_call"]
        SCANNING_WF["code_scanning.yaml<br/>on: workflow_call"]
        # BASIC["basic-checks.yaml<br/>on: pull_request"]
    end
    
    subgraph "Variables Workflow"
        VARS_JOB["variables job<br/>runs-on: ubuntu-latest"]
        VERSION_STEP["version step<br/>Generate commit SHA"]
        GOLANG_STEP["golang_version step<br/>./hack/golang-version.sh"]
        OUTPUTS["outputs:<br/>- version<br/>- golang_version"]
    end
    
    subgraph "Consumer Workflows"
        GOLANG_WF["golang.yaml<br/>inputs.golang_version"]
        SCAN_WF["code_scanning.yaml<br/>inputs.golang_version"]
    end
    
    subgraph "Setup Actions"
        SETUP_GO_1["actions/setup-go@v7<br/>go-version: $golang_version"]
        SETUP_GO_2["actions/setup-go@v7<br/>go-version: $golang_version"]
    end
    
    VARS_JOB --> VERSION_STEP
    VARS_JOB --> GOLANG_STEP
    VERSION_STEP --> OUTPUTS
    GOLANG_STEP --> OUTPUTS
    
    OUTPUTS -->|"outputs.golang_version"| GOLANG_WF
    OUTPUTS -->|"outputs.golang_version"| SCAN_WF
    
    GOLANG_WF -->|"inputs.golang_version"| SETUP_GO_1
    SCAN_WF -->|"inputs.golang_version"| SETUP_GO_2
```

**GitHub Actions Workflow Dependency Chain**

### variables.yaml Workflow

The [`variables.yaml`]() workflow is designed as a reusable workflow (`workflow_call`) that extracts and exposes the Go version.

**Workflow Outputs** ([`.github/workflows/variables.yaml:22-23`]()):

| Output Name | Description | Source |
|-------------|-------------|--------|
| `version` | Short commit SHA (8 characters) | Git commit hash |
| `golang_version` | Go language version | `golang-version.sh` script |

**Job Structure** ([`.github/workflows/variables.yaml:31-35`]()):

```yaml
jobs:
  variables:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.version }}
      golang_version: ${{ steps.golang_version.outputs.golang_version }}
```

The `golang_version` step executes the extraction script:

```yaml
- name: Get Golang Version
  id: golang_version
  run: |
    GOLANG_VERSION=$(./hack/golang-version.sh)
    echo "Detected $GOLANG_VERSION"
    echo "golang_version=${GOLANG_VERSION}" >> $GITHUB_OUTPUT
```

The script output is captured in the `GOLANG_VERSION` shell variable, logged for debugging, and then written to `$GITHUB_OUTPUT` using the `key=value` format required by GitHub Actions.

Sources: [`.github/workflows/variables.yaml:39-49`]()

### Consumer Workflows

#### golang.yaml Workflow

The [`golang.yaml`]() workflow is a reusable workflow that performs linting and module checks. It declares `golang_version` as a required input:

```yaml
on:
  workflow_call:
    inputs:
      golang_version:
        required: true
        type: string
```

The input is consumed by the `actions/setup-go` action at [`.github/workflows/golang.yaml:35-37`]():

```yaml
    - name: Install Go
      uses: actions/setup-go@b7ad1dad31e06c5925ef5d2fc7ad053ef454303e # v7.0.0
      with:
        go-version: ${{ inputs.golang_version }}
```

Sources: [`.github/workflows/golang.yaml:21-26`](), [`.github/workflows/golang.yaml:35-37`]()

#### code_scanning.yaml Workflow

The [`code_scanning.yaml`]() workflow performs CodeQL security analysis. It follows the same pattern, accepting `golang_version` as input and using it in the Go setup step:

```yaml
      - name: Install Go
        uses: actions/setup-go@b7ad1dad31e06c5925ef5d2fc7ad053ef454303e # v7.0.0
        with:
          go-version: ${{ inputs.golang_version }}
```

Sources: [`.github/workflows/code_scanning.yaml:21-24`](), [`.github/workflows/code_scanning.yaml:37-40`]()

### Workflow Orchestration

The `golang.yaml` and `code_scanning.yaml` workflows are typically called by other workflows (e.g., a `basic-checks.yaml` or `ci.yaml` workflow, though not fully provided here) that first call `variables.yaml` to get the `golang_version` and then pass it as an input.

For example, a calling workflow would look like this:

```yaml
jobs:
  call-variables:
    uses: ./.github/workflows/variables.yaml
  call-golang:
    needs: call-variables
    uses: ./.github/workflows/golang.yaml
    with:
      golang_version: ${{ needs.call-variables.outputs.golang_version }}
  call-code-scanning:
    needs: call-variables
    uses: ./.github/workflows/code_scanning.yaml
    with:
      golang_version: ${{ needs.call-variables.outputs.golang_version }}
```

Sources: [`.github/workflows/golang.yaml:21-26`](), [`.github/workflows/code_scanning.yaml:21-24`]()

---

## Implementation Details

### Variable Naming Conventions

The system uses consistent naming across different contexts:

| Context | Variable Name | Format |
|---------|--------------|--------|
| Dockerfile | (implicit) | `golang:1.26.5` |
| Shell script | `GOLANG_VERSION` | `1.26.5` |
| Workflow output | `golang_version` | `1.26.5` |
| Workflow input | `golang_version` | `1.26.5` |
| GitHub Action parameter | `go-version` | `1.26.5` |

The naming follows each ecosystem's conventions: uppercase with underscores in shell scripts, lowercase with underscores in GitHub Actions, and kebab-case in action parameters.

### Error Handling

The `golang-version.sh` script has minimal error handling—it relies on:
1. **grep's behavior**: Returns empty string if no match found
2. **Shell variable**: `GOLANG_VERSION` will be empty if extraction fails
3. **Echo always succeeds**: Even if variable is empty

In practice, if the script fails to extract a version:
- The workflow step will output an empty string
- GitHub Actions will pass an empty string to consumer workflows
- The `actions/setup-go` action will fail with a clear error about invalid version

This fail-fast approach ensures version extraction problems are immediately visible in CI.

Sources: [`hack/golang-version.sh:20-22`]()

---

## Version Update Process

### Manual Updates

To update the Go version manually:

1. **Edit the Dockerfile** ([`deployments/devel/Dockerfile:17`]()):
   ```dockerfile
   FROM golang:1.26.5
   ```

2. **Verify extraction** (local testing):
   ```bash
   ./hack/golang-version.sh
   # Output: 1.26.5
   ```

3. **Commit and push**:
   ```bash
   git add deployments/devel/Dockerfile
   git commit -m "Update Go version to 1.26.5"
   git push
   ```

4. **Automatic propagation**: The CI workflows will automatically use the new version

### Dependabot Updates

Dependabot monitors the Dockerfile and automatically creates PRs when new Go versions are released. The `.github/dependabot.yml` configuration (not shown in provided files) specifies Docker base image monitoring.

When Dependabot detects `golang:1.26.5` is available, it will:
1. Create a PR updating [`deployments/devel/Dockerfile:17`]()
2. The PR's CI run will automatically use the new version via the extraction pipeline
3. Reviewers can verify the version change in the Dockerfile diff

Sources: [`deployments/devel/Dockerfile:15-17`]()

---

## Benefits and Design Rationale

### Single Point of Maintenance

**Problem**: Multiple files defining Go versions can become inconsistent.

**Solution**: One canonical definition eliminates synchronization issues.

**Example**: Without this pattern, the following files might each declare different versions:
- CI workflow files (`.github/workflows/*.yaml`)
- Makefile or build scripts
- Documentation
- Docker images

With the single-source-of-truth pattern, all these consumers reference the same extracted value.

### Dependabot Integration

**Problem**: Manual version updates are tedious and easy to forget.

**Solution**: Dependabot's native Dockerfile support enables automatic update PRs.

Dependabot can parse `FROM golang:X.Y.Z` directives and:
- Detect when new Go versions are published
- Create PRs with the version bump
- Include release notes and changelog links

This would not work if the version were in a custom YAML or JSON file.

### CI/CD Efficiency

**Problem**: Hardcoding versions in multiple workflows creates maintenance burden.

**Solution**: The `variables.yaml` workflow acts as a central distribution point.

**Workflow reusability**: The `golang.yaml` and `code_scanning.yaml` workflows accept `golang_version` as an input, making them reusable across different repositories or branches that might use different Go versions.

### Audit Trail

**Problem**: Understanding when and why version changes occurred.

**Solution**: Git history of the Dockerfile provides complete change tracking.

Example git log:
```
commit abc123: Update Go version to 1.26.5 (Dependabot)
commit def456: Update Go version to 1.26.4 (Dependabot)
commit ghi789: Update Go version to 1.26.3 (manual)
```

Each change includes:
- Who made the change (author)
- When it was made (commit date)
- Why it was made (commit message, linked issues/PRs)
- What else changed in that commit

Sources: [`deployments/devel/Dockerfile:15-17`](), [`.github/workflows/variables.yaml:39-49`]()

---

## Integration with Build System

The version management system integrates with the build system described in [Build System](#8). Specifically:

### Docker Image Builds

The `deployments/nvml-mock/Dockerfile` uses an `ARG GOLANG_VERSION` which defaults to `1.26.5` and is then used in its `FROM` instruction: `FROM golang:${GOLANG_VERSION}-bookworm AS builder` ([`deployments/nvml-mock/Dockerfile:15-16`]). This ensures that the `nvml-mock` image is built with the specified Go version. Similarly, `tests/mocknvml/Dockerfile` also uses `ARG GOLANG_VERSION` and `FROM golang:${GOLANG_VERSION}` ([`tests/mocknvml/Dockerfile:14-15`]).

### Local Development

Developers can extract the project's Go version for local setup:

```bash
# Get the project's Go version
GO_VERSION=$(./hack/golang-version.sh)

# Use it to install the correct Go version (example with version managers)
asdf install golang $GO_VERSION
# or
gvm install go$GO_VERSION
```

This ensures local development environments match CI.

### Makefile Integration

The `pkg/gpu/mocknvml/Makefile` defines `GOLANG_VERSION ?= 1.26.5` ([`pkg/gpu/mocknvml/Makefile:17`]). This variable is then passed as a build argument to Docker when building the `mock-nvml-builder` image ([`pkg/gpu/mocknvml/Makefile:129-130`]). This ensures that the mock NVML library is built with the correct Go version in a Dockerized environment.

Sources: [`deployments/devel/Dockerfile:17`](), [`hack/golang-version.sh:20-22`](), [`deployments/nvml-mock/Dockerfile:15-16`](), [`tests/mocknvml/Dockerfile:14-15`](), [`pkg/gpu/mocknvml/Makefile:17`](), [`pkg/gpu/mocknvml/Makefile:129-130`]()

---

## Related Pages

- **[Dependency Updates with Dependabot](#4.4)**: How Dependabot monitors and updates dependencies
- **[GitHub Actions Workflows](#4.1)**: Overall workflow structure and job dependencies
- **[Go Version Management Strategy](#8.3)**: Build system perspective on version management
- **[Docker Images](#8.2)**: How the Dockerfile is used to build images
- **[Makefile Reference](#8.1)**: Build targets that may use version information

---

# Page: Dependency Updates with Dependabot

# Dependency Updates with Dependabot

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/dependabot.yml](.github/dependabot.yml)
- [.github/workflows/basic-checks.yaml](.github/workflows/basic-checks.yaml)
- [.github/workflows/ci.yaml](.github/workflows/ci.yaml)

</details>



## Purpose and Scope

This document details the automated dependency update strategy used in k8s-test-infra through GitHub Dependabot. It covers how Go module dependencies, GitHub Actions workflow versions, and Docker base images are automatically monitored and updated.

For information about the overall CI/CD pipeline structure, see [CI/CD Pipeline](#4). For details about version management strategy, see [Version Management](#4.3).

---

## Dependabot Configuration Overview

The repository uses Dependabot to automate dependency updates across three package ecosystems, each with different update frequencies and strategies. The configuration file [.github/dependabot.yml:1-36]() defines all monitoring rules.

```mermaid
graph TB
    subgraph "Dependabot Configuration"
        CONFIG[".github/dependabot.yml"]
    end
    
    subgraph "Package Ecosystems"
        GOMOD["gomod<br/>Weekly (Sunday)"]
        GHACTIONS["github-actions<br/>Daily"]
        DOCKER["docker<br/>Daily"]
    end
    
    subgraph "Monitoring Targets"
        GOMOD_TARGET["Directory: /<br/>Target: main branch<br/>Labels: dependencies"]
        GHACTIONS_TARGET["Directory: /<br/>Target: main branch"]
        DOCKER_TARGET["Directory: /deployments/devel<br/>Target: main branch<br/>Labels: dependencies"]
    end
    
    subgraph "Dependency Grouping"
        K8SIO_GROUP["k8sio group<br/>Patterns: k8s.io/*<br/>Exclude: k8s.io/klog/*"]
    end
    
    CONFIG --> GOMOD
    CONFIG --> GHACTIONS
    CONFIG --> DOCKER
    
    GOMOD --> GOMOD_TARGET
    GHACTIONS --> GHACTIONS_TARGET
    DOCKER --> DOCKER_TARGET
    
    GOMOD --> K8SIO_GROUP
```

**Sources:** [.github/dependabot.yml:1-36]()

---

## Go Module Dependency Updates

### Update Schedule and Strategy

Go module dependencies are checked **weekly on Sundays** [.github/dependabot.yml:9-11](). This cadence balances staying current with dependencies against the overhead of reviewing and merging updates.

| Configuration | Value |
|---------------|-------|
| Package Ecosystem | `gomod` |
| Target Branch | `main` |
| Directory | `/` |
| Schedule | Weekly on Sunday |
| Labels | `dependencies` |

**Sources:** [.github/dependabot.yml:6-13]()

### Kubernetes Dependency Grouping

The repository implements a grouping strategy for Kubernetes-related dependencies to reduce the number of individual pull requests. All `k8s.io/*` packages (excluding `k8s.io/klog/*`) are grouped together under the `k8sio` group name [.github/dependabot.yml:14-19]().

```mermaid
graph LR
    subgraph "k8sio Group Strategy"
        PATTERN["Pattern: k8s.io/*"]
        EXCLUDE["Exclude: k8s.io/klog/*"]
        
        PATTERN --> GROUPED["Grouped Updates"]
        EXCLUDE --> SEPARATE["Separate Updates"]
    end
    
    subgraph "Grouped Packages"
        K8SAPI["k8s.io/api"]
        K8SAPIMACH["k8s.io/apimachinery"]
        K8SCLIENT["k8s.io/client-go"]
        K8SAPIEXT["k8s.io/apiextensions-apiserver"]
    end
    
    subgraph "Excluded Packages"
        KLOG["k8s.io/klog/v2"]
    end
    
    GROUPED --> K8SAPI
    GROUPED --> K8SAPIMACH
    GROUPED --> K8SCLIENT
    GROUPED --> K8SAPIEXT
    
    SEPARATE --> KLOG
```

This grouping approach means that when new versions of Kubernetes client libraries are released, Dependabot creates a single pull request updating all related packages together, rather than creating separate PRs for each package. The `k8s.io/klog` package is excluded from grouping because it follows an independent release cycle.

**Sources:** [.github/dependabot.yml:14-19]()

### Vendor Directory Synchronization

When Dependabot updates Go modules, the CI pipeline must verify that the vendor directory remains synchronized with `go.mod` and `go.sum`. The repository uses Go module vendoring for reproducible builds.

```mermaid
flowchart TD
    DEPENDABOT["Dependabot<br/>Updates go.mod/go.sum"]
    
    subgraph "CI Validation"
        MODULES["make modules"]
        TIDY["go mod tidy"]
        VENDOR["go mod vendor"]
        VERIFY["go mod verify"]
        CHECK["git diff check"]
    end
    
    subgraph "Makefile Targets"
        MODTIDY[".mod-tidy<br/>Makefile:54-59"]
        MODVENDOR[".mod-vendor<br/>Makefile:61-66"]
        MODVERIFY[".mod-verify<br/>Makefile:68-73"]
        CHECKMODULES["check-modules<br/>Makefile:75-79"]
    end
    
    DEPENDABOT --> MODULES
    MODULES --> MODTIDY
    MODULES --> MODVENDOR
    MODULES --> MODVERIFY
    MODTIDY --> TIDY
    MODVENDOR --> VENDOR
    MODVERIFY --> VERIFY
    MODULES --> CHECKMODULES
    CHECKMODULES --> CHECK
```

The `check-modules` target [Makefile:75-79]() validates that:
1. All `go.mod` files are tidied
2. All modules are vendored
3. No uncommitted changes exist in `go.mod`, `go.sum`, or `vendor/` directories

**Sources:** [Makefile:52-79]()

---

## GitHub Actions Workflow Updates

### Update Schedule

GitHub Actions workflow dependencies are checked **daily** [.github/dependabot.yml:24-25](). This frequent schedule ensures the repository uses the latest workflow action versions, which often include security fixes and bug patches.

| Configuration | Value |
|---------------|-------|
| Package Ecosystem | `github-actions` |
| Target Branch | `main` |
| Directory | `/` |
| Schedule | Daily |

```mermaid
graph TB
    DEPENDABOT["Dependabot Scanner"]
    
    subgraph "Monitored Workflow Files"
        BASICCHECKS[".github/workflows/basic-checks.yaml"]
        OTHERFLOWS[".github/workflows/*.yaml"]
    end
    
    subgraph "Action Dependencies"
        CHECKOUT["actions/checkout"]
        SETUP["actions/setup-go"]
        CODEQL["github/codeql-action"]
        CUSTOM["Custom actions"]
    end
    
    DEPENDABOT --> BASICCHECKS
    DEPENDABOT --> OTHERFLOWS
    
    BASICCHECKS --> CHECKOUT
    BASICCHECKS --> SETUP
    BASICCHECKS --> CODEQL
    OTHERFLOWS --> CUSTOM
```

Dependabot monitors all workflow files in `.github/workflows/` and creates pull requests when new versions of actions are available. This includes both GitHub-provided actions (like `actions/checkout`, `actions/setup-go`) and third-party actions.

**Sources:** [.github/dependabot.yml:21-25]()

---

## Docker Base Image Updates

### Update Schedule and Target

Docker base image updates are checked **daily** [.github/dependabot.yml:32-33](), focusing specifically on the Golang version used in the development container.

| Configuration | Value |
|---------------|-------|
| Package Ecosystem | `docker` |
| Target Branch | `main` |
| Directory | `/deployments/devel` |
| Schedule | Daily |
| Labels | `dependencies` |

```mermaid
graph TB
    DEPENDABOT["Dependabot Scanner"]
    
    subgraph "Monitored Dockerfile"
        DOCKERFILE["deployments/devel/Dockerfile"]
        FROMLINE["FROM golang:1.25.4"]
    end
    
    subgraph "Version Propagation"
        EXTRACT["hack/golang-version.sh"]
        CIVAR["CI: golang_version variable"]
        CIJOBS["CI: golang and other jobs"]
    end
    
    subgraph "Update Flow"
        NEWVERSION["New golang:<VERSION>"]
        PR["Dependabot PR"]
        MERGE["Merge to main"]
    end
    
    DEPENDABOT --> DOCKERFILE
    DOCKERFILE --> FROMLINE
    
    NEWVERSION --> PR
    PR --> MERGE
    MERGE --> DOCKERFILE
    
    DOCKERFILE --> EXTRACT
    EXTRACT --> CIVAR
    CIVAR --> CIJOBS
```

The Docker configuration specifically monitors `/deployments/devel` [.github/dependabot.yml:31]() because this directory contains the `Dockerfile` that defines the canonical Go version for the project. The comment "Golang version" [.github/dependabot.yml:30]() indicates this is the single source of truth for Go version management.

When Dependabot detects a new Golang Docker image version, it creates a pull request updating the `FROM` line in the Dockerfile. This triggers the version extraction mechanism documented in [Version Management](#4.3), ensuring the new version propagates throughout the CI pipeline.

**Sources:** [.github/dependabot.yml:27-36]()

---

## Dependency Update Workflow

### Pull Request Creation and Validation

```mermaid
sequenceDiagram
    participant D as Dependabot
    participant GH as GitHub
    participant CI as CI Pipeline
    participant R as Reviewers
    
    Note over D: Daily/Weekly Scan
    D->>D: Detect new versions
    D->>GH: Create PR
    GH->>GH: Apply labels
    
    Note over CI: Automated Checks
    GH->>CI: Trigger workflows
    CI->>CI: make check-modules
    CI->>CI: make check-vendor
    CI->>CI: golangci-lint
    CI->>CI: code-scanning
    CI->>GH: Report status
    
    Note over R: Manual Review
    R->>GH: Review changes
    R->>GH: Approve
    GH->>GH: Merge to main
    
    Note over GH: Post-Merge
    GH->>CI: Trigger main branch CI
```

**Sources:** [.github/dependabot.yml:1-36](), [Makefile:49-79]()

### Validation Requirements

When Dependabot creates a pull request, the CI pipeline performs several validation checks:

| Check Type | Makefile Target | Purpose |
|------------|----------------|---------|
| Module Synchronization | `check-modules` [Makefile:75-79]() | Verifies `go.mod`, `go.sum`, and `vendor/` are in sync |
| Vendor Validation | `check-vendor` [Makefile:49-50]() | Ensures vendor directory matches module files |
| Code Linting | `lint` [Makefile:41-42]() | Runs golangci-lint on all code |
| Code Formatting | `verify` [Makefile:34-39]() | Checks gofmt compliance |

For **Go module updates**, the most critical validation is `check-modules`, which iterates through all `go.mod` files in the repository:

```mermaid
graph TD
    CHECKMOD["check-modules target"]
    
    subgraph "Module Operations"
        FINDMODS["Find all go.mod files<br/>Exclude: testdata, third_party"]
        TIDY["For each: go mod tidy"]
        VENDOR["For each: go mod vendor"]
        VERIFY["For each: go mod verify"]
    end
    
    subgraph "Git Validation"
        DIFFMOD["git diff go.mod go.sum"]
        DIFFVENDOR["git diff vendor/"]
        FAIL["Exit 1 if changes"]
    end
    
    CHECKMOD --> FINDMODS
    FINDMODS --> TIDY
    TIDY --> VENDOR
    VENDOR --> VERIFY
    VERIFY --> DIFFMOD
    DIFFMOD --> DIFFVENDOR
    DIFFVENDOR --> FAIL
```

The validation ensures that when Dependabot updates dependencies, all derived artifacts (vendor directory, verified checksums) are also updated in the same commit.

**Sources:** [Makefile:52-79]()

---

## Labeling and Organization

Dependabot automatically applies labels to pull requests based on the configuration:

| Package Ecosystem | Applied Labels |
|-------------------|----------------|
| `gomod` | `dependencies` [.github/dependabot.yml:12-13]() |
| `github-actions` | *(none specified)* |
| `docker` | `dependencies` [.github/dependabot.yml:34-35]() |

These labels help maintainers filter and prioritize dependency updates. The `dependencies` label groups Go module and Docker updates together, while GitHub Actions updates remain unlabeled for separate tracking.

**Sources:** [.github/dependabot.yml:12-13,34-35]()

---

## Configuration File Structure

The complete Dependabot configuration follows this structure:

```mermaid
graph TB
    ROOT["dependabot.yml<br/>version: 2"]
    
    subgraph "updates array"
        GOMOD_BLOCK["gomod update block"]
        GHA_BLOCK["github-actions block"]
        DOCKER_BLOCK["docker update block"]
    end
    
    subgraph "gomod block fields"
        GOMOD_PKG["package-ecosystem: gomod"]
        GOMOD_DIR["directory: /"]
        GOMOD_BRANCH["target-branch: main"]
        GOMOD_SCHED["schedule: weekly (sunday)"]
        GOMOD_LABELS["labels: dependencies"]
        GOMOD_GROUPS["groups: k8sio"]
    end
    
    subgraph "github-actions block fields"
        GHA_PKG["package-ecosystem: github-actions"]
        GHA_DIR["directory: /"]
        GHA_BRANCH["target-branch: main"]
        GHA_SCHED["schedule: daily"]
    end
    
    subgraph "docker block fields"
        DOCKER_PKG["package-ecosystem: docker"]
        DOCKER_DIR["directories: /deployments/devel"]
        DOCKER_BRANCH["target-branch: main"]
        DOCKER_SCHED["schedule: daily"]
        DOCKER_LABELS["labels: dependencies"]
    end
    
    ROOT --> GOMOD_BLOCK
    ROOT --> GHA_BLOCK
    ROOT --> DOCKER_BLOCK
    
    GOMOD_BLOCK --> GOMOD_PKG
    GOMOD_BLOCK --> GOMOD_DIR
    GOMOD_BLOCK --> GOMOD_BRANCH
    GOMOD_BLOCK --> GOMOD_SCHED
    GOMOD_BLOCK --> GOMOD_LABELS
    GOMOD_BLOCK --> GOMOD_GROUPS
    
    GHA_BLOCK --> GHA_PKG
    GHA_BLOCK --> GHA_DIR
    GHA_BLOCK --> GHA_BRANCH
    GHA_BLOCK --> GHA_SCHED
    
    DOCKER_BLOCK --> DOCKER_PKG
    DOCKER_BLOCK --> DOCKER_DIR
    DOCKER_BLOCK --> DOCKER_BRANCH
    DOCKER_BLOCK --> DOCKER_SCHED
    DOCKER_BLOCK --> DOCKER_LABELS
```

Each update block in the `updates` array [.github/dependabot.yml:5]() defines a separate dependency monitoring configuration. The three blocks operate independently with their own schedules and rules.

**Sources:** [.github/dependabot.yml:1-36]()

---

## Best Practices and Rationale

### Update Frequency Strategy

The repository employs a tiered update frequency based on risk and change velocity:

| Frequency | Ecosystems | Rationale |
|-----------|-----------|-----------|
| Daily | `github-actions`, `docker` | Security-critical; low merge overhead |
| Weekly | `gomod` | Higher review effort; batching reduces noise |

**Daily updates** for GitHub Actions and Docker base images ensure rapid adoption of security patches with minimal merge conflicts, as these updates typically don't require code changes.

**Weekly updates** for Go modules provide time to batch multiple dependency updates together, especially when the `k8sio` group combines multiple Kubernetes library updates into a single PR.

### Vendoring and Reproducibility

The repository mandates vendoring for all Go dependencies [Makefile:44-47](). This strategy ensures:

1. **Build Reproducibility**: Builds use the exact dependency versions committed to the repository
2. **Offline Builds**: No external network access required during compilation
3. **Dependency Auditing**: All dependency source code is visible in the repository
4. **CI Validation**: The `check-modules` target [Makefile:75-79]() ensures vendor directory stays synchronized

When Dependabot updates Go modules, the CI pipeline automatically validates that the vendor directory is updated accordingly. This prevents situations where `go.mod` references new versions but `vendor/` contains stale code.

**Sources:** [Makefile:44-50](), [Makefile:52-79](), [.github/dependabot.yml:6-19]()

---

# Page: Testing with Ginkgo

# Testing with Ginkgo

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [go.mod](go.mod)
- [go.sum](go.sum)
- [vendor/github.com/onsi/ginkgo/v2/CHANGELOG.md](vendor/github.com/onsi/ginkgo/v2/CHANGELOG.md)
- [vendor/github.com/onsi/ginkgo/v2/README.md](vendor/github.com/onsi/ginkgo/v2/README.md)
- [vendor/github.com/onsi/ginkgo/v2/core_dsl.go](vendor/github.com/onsi/ginkgo/v2/core_dsl.go)
- [vendor/github.com/onsi/ginkgo/v2/internal/global/init.go](vendor/github.com/onsi/ginkgo/v2/internal/global/init.go)
- [vendor/github.com/onsi/ginkgo/v2/internal/node.go](vendor/github.com/onsi/ginkgo/v2/internal/node.go)
- [vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go](vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go)
- [vendor/github.com/onsi/ginkgo/v2/reporting_dsl.go](vendor/github.com/onsi/ginkgo/v2/reporting_dsl.go)
- [vendor/github.com/onsi/ginkgo/v2/table_dsl.go](vendor/github.com/onsi/ginkgo/v2/table_dsl.go)
- [vendor/github.com/onsi/ginkgo/v2/types/version.go](vendor/github.com/onsi/ginkgo/v2/types/version.go)
- [vendor/k8s.io/apimachinery/pkg/api/validation/objectmeta.go](vendor/k8s.io/apimachinery/pkg/api/validation/objectmeta.go)
- [vendor/modules.txt](vendor/modules.txt)

</details>



## Purpose and Scope

This page provides a comprehensive high-level guide to using the Ginkgo BDD testing framework within the `k8s-test-infra` project. Ginkgo version 2.32.0 is used extensively across all test suites to provide expressive behavior-driven development (BDD) style testing with powerful test organization, configuration, parallel execution, and reporting capabilities.

This page serves as a parent overview linking to four child pages that cover essential subtopics in detail:

- [Ginkgo Framework Overview](#5.1) — Introduces Ginkgo’s core concepts, execution model, and framework architecture as applied here.
- [Test Structure and DSL](#5.2) — Documents the usage of Describe/Context/It blocks, hooks like BeforeEach and AfterEach, and table-driven tests.
- [Configuration and Parallel Execution](#5.3) — Explains suite and reporter configurations, test parallelization, randomization, and synchronization patterns.
- [Test Reporting and Output](#5.4) — Details console output, JSON/JUnit reports, progress reporting, and diagnostic artifact collection.

For more details on the testing system architecture and CI/CD usage, see the [Architecture](#3) and [CI/CD Pipeline](#4) pages.

---

## Ginkgo Framework Overview

At its core, Ginkgo organizes tests into suites that contain hierarchical nodes representing test containers, tests, and setup/teardown steps. The suite runs via the `RunSpecs` function that orchestrates execution, applies configuration, and triggers reporting.

```mermaid
graph TB
  subgraph "Ginkgo Core"
    Suite["Suite (internal.Suite)"]
    Runner["RunSpecs() Runner"]
    Reporter["DefaultReporter"]
    Config["SuiteConfig & ReporterConfig"]
  end

  subgraph "Test Tree Structure"
    Container["Container Nodes<br/>(Describe/Context/When)"]
    Subject["Subject Nodes<br/>(It/Specify)"]
    Setup["Setup Nodes<br/>(BeforeEach/AfterEach)"]
    Table["Table-Driven Tests<br/>(DescribeTable/Entry)"]
  end

  subgraph "Execution Controls"
    Parallel["Parallel Execution & Coordination"]
    Random["Spec Randomization"]
    Focus["Focus & Pending Specs"]
    Timeout["Timeouts & Interrupt Handling"]
  end

  subgraph "Reporting & Output"
    Timeline["Timeline View"]
    Progress["Progress Reporting (Signals, Polling)"]
    JSON["JSON/JUnit Reports"]
    Console["Console Output"]
  end

  Runner --> Suite
  Suite --> Container
  Suite --> Subject
  Suite --> Setup
  Suite --> Table
  Suite --> Parallel
  Suite --> Random
  Suite --> Focus
  Suite --> Timeout
  Suite --> Reporter
  Config --> Runner
  Config --> Parallel
  Config --> Random

  Reporter --> Timeline
  Reporter --> Progress
  Reporter --> JSON
  Reporter --> Console
```

This framework supports natural language-style test descriptions and hierarchies, as well as advanced features like interruptible specs using context, table-driven specs with multiple parameterizations, and sophisticated parallel execution.

**Sources:**  
[vendor/github.com/onsi/ginkgo/v2/internal/suite.go:25-71](),  
[vendor/github.com/onsi/ginkgo/v2/core_dsl.go:1-53]()

---

## Test Structure and Domain-Specific Language (DSL)

### Node Types and Hierarchy

Ginkgo structures tests as a tree of nodes, each serving a distinct role:

| Node Type     | DSL Functions                              | Purpose                                      | Can Contain                    |
|---------------|-------------------------------------------|----------------------------------------------|-------------------------------|
| Container     | `Describe`, `Context`, `When`             | Group related specs                           | Other Containers, Setup, Subject Nodes |
| Subject       | `It`, `Specify`                           | Define individual test cases                  | Test logic and assertions      |
| Setup/Teardown| `BeforeEach`, `AfterEach`, `JustBeforeEach`, `JustAfterEach`, `DeferCleanup` | Setup and teardown logic executed around specs | Setup and teardown functions   |
| Suite Setup   | `BeforeSuite`, `AfterSuite`                | Initialization and cleanup for entire suite | Suite-wide initialization      |
| Table-Driven  | `DescribeTable`, `Entry`, `DescribeTableSubtree` | Parameterized tests generating multiple specs | Generates many Subject/Container nodes |

**Sources:**  
[vendor/github.com/onsi/ginkgo/v2/core_dsl.go:536-654](),  
[vendor/github.com/onsi/ginkgo/v2/internal/node.go:27-70]()

### Basic Test Structure

Tests begin with a `RunSpecs` call, invoking hierarchical containers grouping specs.

```mermaid
graph TB
  Suite["Test Suite"]
  BS["BeforeSuite"]
  AS["AfterSuite"]
  D1["Describe('Feature X')"]
  D2["Describe('Feature Y')"]

  BE1["BeforeEach"]
  BE2["BeforeEach"]

  IT1["It('does A')"]
  IT2["It('does B')"]
  IT3["It('does C')"]

  AE1["AfterEach"]
  AE2["AfterEach"]

  Suite --> BS
  Suite --> D1
  Suite --> D2
  Suite --> AS

  D1 --> BE1
  D1 --> IT1
  D1 --> IT2
  D1 --> AE1

  D2 --> BE2
  D2 --> IT3
  D2 --> AE2
```

The setup and teardown nodes run before and after each spec to manage state and side effects.

**Sources:**  
[vendor/github.com/onsi/ginkgo/v2/core_dsl.go:546-653]()

### Container Nodes: Describe, Context, When

These nodes provide hierarchical grouping:

- `Describe` – Primary grouping for behavior or type
- `Context` – Synonym for `Describe`, used for scenario differentiation
- `When` – Like `Context` but prefixes description with "when "

Focus and Pending variants control execution:

- Focused: `FDescribe`, `FContext`, `FWhen`
- Pending/Skipped: `PDescribe`, `PContext`, `PWhen`, `XDescribe`, `XContext`, `XWhen`

Example:

```go
Describe("NodeFeature CRD", func() {
  Context("when creating a new resource", func() {
    When("labels are valid", func() {
      It("creates successfully", func() {
        // test code
      })
    })
  })
})
```

**Sources:**  
[vendor/github.com/onsi/ginkgo/v2/core_dsl.go:546-593]()

### Subject Nodes: It and Specify

These nodes hold the actual test logic and assertions.

- Can be passed a simple `func()` or context-aware `func(ctx SpecContext)`
- Context-aware functions support timeouts and interrupt handling
- Cannot nest other Ginkgo nodes inside
- Have Focus and Pending variants: `FIt`, `PIt`, `XIt`, etc.

Example:

```go
It("validates resource allocation", func(ctx SpecContext) {
  // assertions here
}, NodeTimeout(time.Second*30))
```

**Sources:**  
[vendor/github.com/onsi/ginkgo/v2/core_dsl.go:596-635](),  
[vendor/github.com/onsi/ginkgo/v2/internal/node.go:503-525]()

### Setup and Teardown Nodes

Setup and teardown nodes provide controlled execution around specs:

| Node          | Run Time                             | Purpose                        |
|---------------|------------------------------------|--------------------------------|
| `BeforeEach`  | Before each `It`                   | Standard setup                 |
| `AfterEach`   | After each `It`                    | Standard teardown             |
| `JustBeforeEach` | After all `BeforeEach`, before `It` | Setup that depends on other setup |
| `JustAfterEach` | Immediately after `It`, before other `AfterEach` | Immediate cleanup             |
| `BeforeAll`   | Once before specs in ordered container | Expensive suite setup        |
| `AfterAll`    | Once after specs in ordered container | Suite cleanup                  |
| `DeferCleanup`| During cleanup phase (LIFO order)  | Deferred cleanup functions    |

Execution ordering for a spec:

```mermaid
graph LR
  BE["BeforeEach"] --> JBE["JustBeforeEach"] --> IT["It"] --> JAE["JustAfterEach"] --> AE["AfterEach"] --> DC["DeferCleanup"]
```

**Sources:**  
[vendor/github.com/onsi/ginkgo/v2/core_dsl.go:656-827](),  
[vendor/github.com/onsi/ginkgo/v2/internal/node.go:588-652]()

---

## Table-Driven Tests

Table-driven tests allow single test logic to run against multiple inputs.

```mermaid
graph TB
  DT["DescribeTable"] --> Body["Test Function"]
  DT --> E1["Entry #1"]
  DT --> E2["Entry #2"]
  DT --> E3["Entry #3"]
  E1 --> IT1["It #1 (generated)"]
  E2 --> IT2["It #2 (generated)"]
  E3 --> IT3["It #3 (generated)"]
```

### DescribeTable and Entry

Each `Entry` generates an individual `It` spec with parameters:

```go
DescribeTable("resource allocation",
  func(deviceType string, count int, shouldSucceed bool) {
    result := allocate(deviceType, count)
    Expect(result.Success).To(Equal(shouldSucceed))
  },
  Entry("single GPU", "nvidia.com/gpu", 1, true),
  Entry("multiple GPUs", "nvidia.com/gpu", 4, true),
  Entry("invalid input", "nvidia.com/gpu", -1, false),
)
```

- Entries can be decorated with labels, timeouts, etc.
- Variants include `FDescribeTable`, `PDescribeTable`, etc.

**Sources:**  
[vendor/github.com/onsi/ginkgo/v2/table_dsl.go:47-194]()

### DescribeTableSubtree

Generates a subtree of tests per entry, allowing multiple `It` specs and setup within each generated container:

```go
DescribeTableSubtree("device allocation tests",
  func(deviceClass string) {
    var claim *ResourceClaim
    BeforeEach(func() {
      claim = createResourceClaim(deviceClass)
    })
    It("allocates device", func() { /* test */ })
    It("releases device", func() { /* test */ })
  },
  Entry("GPU devices", "gpu.example.com"),
  Entry("RDMA devices", "rdma.example.com"),
)
```

- Each entry creates container and nested subjects setup anew.

**Sources:**  
[vendor/github.com/onsi/ginkgo/v2/table_dsl.go:112-141](),  
[vendor/github.com/onsi/ginkgo/v2/table_dsl.go:199-317]()

---

## Configuration and Parallel Execution

### SuiteConfig and ReporterConfig

Ginkgo is configured via two primary structs:

```mermaid
graph TB
  subgraph SuiteConfig
    RS["RandomSeed"]
    RA["RandomizeAllSpecs"]
    PT["ParallelTotal"]
    PP["ParallelProcess"]
    LF["LabelFilter"]
    SVF["SemVerFilter"]
    TO["Timeout"]
    FF["FailFast"]
  end

  subgraph ReporterConfig
    VB["Verbosity"]
    NC["NoColor"]
    JR["JSONReport"]
    JUR["JUnitReport"]
    SN["ShowNodeEvents"]
    FT["FullTrace"]
  end

  Config["RunSpecs() accepts SuiteConfig & ReporterConfig"]
  Config --> SuiteConfig
  Config --> ReporterConfig
```

**SuiteConfig** controls execution behaviors: randomization, parallelism, filtering, timeouts, and failure modes.

**ReporterConfig** controls output verbosity, color usage, and artifact reports generation (JSON, JUnit).

**Sources:**  
[vendor/github.com/onsi/ginkgo/v2/core_dsl.go:37-41](),  
[vendor/github.com/onsi/ginkgo/v2/core_dsl.go:127-141]()

### Running Tests with RunSpecs

Tests start with a function like:

```go
func TestMySuite(t *testing.T) {
  RegisterFailHandler(Fail)
  RunSpecs(t, "My Test Suite")
}
```

`RunSpecs` can optionally accept customized SuiteConfig and ReporterConfig for tuning.

**Sources:**  
[vendor/github.com/onsi/ginkgo/v2/core_dsl.go:232-331]()

### Spec Decorators

Decorators modify the behavior or metadata of specs and containers:

| Decorator             | Description                                 |
|-----------------------|---------------------------------------------|
| `Label("integration")`| Tag specs for filtering                       |
| `Focus`               | Run only these specs                          |
| `Pending`             | Mark specs skipped or in-progress            |
| `Serial`              | Run this spec serially, not in parallel      |
| `Ordered`             | Run specs in a container sequentially        |
| `FlakeAttempts(n)`    | Retry flaky specs up to `n` times             |
| `MustPassRepeatedly(n)`| Must pass spec `n` times consecutively       |
| `NodeTimeout(d)`      | Timeout for individual node execution         |
| `SpecTimeout(d)`      | Timeout for entire spec                        |
| `GracePeriod(d)`      | Time allowed to cleanup after timeout         |
| `SpecPriority(n)`     | Execution priority, higher runs earlier       |

Example usage:

```go
Describe("NFD Integration", Label("integration"), func() {
  It("discovers GPUs",
    FlakeAttempts(3),
    NodeTimeout(30*time.Second),
    func(ctx SpecContext) {
      // test logic
    })
})
```

**Sources:**  
[vendor/github.com/onsi/ginkgo/v2/internal/node.go:73-98](),  
[vendor/github.com/onsi/ginkgo/v2/internal/node.go:214-499]()

### Parallel Execution

Ginkgo can execute specs in parallel processes coordinated by a parallel server:

```mermaid
graph TB
  CLI["ginkgo CLI or orchestrator"]

  subgraph Processes
    P1["Proc 1 (ParallelProcess=1)"]
    P2["Proc 2 (ParallelProcess=2)"]
    P3["Proc 3 (ParallelProcess=3)"]
  end

  Server["Parallel Server (coordination)"]
  Counter["Shared Spec Counter (work distribution)"]

  CLI --> Server
  CLI --> P1
  CLI --> P2
  CLI --> P3

  P1 --> Server
  P2 --> Server
  P3 --> Server

  Server --> Counter

  P1 -.->|Fetch spec index| Counter
  P2 -.->|Fetch spec index| Counter
  P3 -.->|Fetch spec index| Counter
```

- Specs are fetched and run dynamically per process.
- Output is captured per-process to prevent interleaving.
- `Serial` decorator disables parallelism for selected specs.
- Reports from parallel runs are combined.

Configuration includes:

- `ParallelTotal` — total parallel processes
- `ParallelProcess` — current process number (1-indexed)
- `ParallelHost` — address of parallel server (if any)

**Sources:**  
[vendor/github.com/onsi/ginkgo/v2/core_dsl.go:274-294](),  
[vendor/github.com/onsi/ginkgo/v2/internal/suite.go:434-516]()

### SynchronizedBeforeSuite Pattern

For shared setup work required once across parallel nodes (e.g. building container images), Ginkgo offers the `SynchronizedBeforeSuite` pattern, allowing a single initialization to run before distributed tests start.

**Sources:**  
[vendor/github.com/onsi/ginkgo/v2/core_dsl.go:758-782]() (implied from knowledge; exact lines not provided but known pattern)

---

## Test Reporting and Output

### Timeline-Based Output

Ginkgo’s default reporter presents test execution as an event timeline interleaved with captured output for rich diagnostics.

```mermaid
graph TB
  T0["Spec Start"]
  T1["BeforeEach Start"]
  T2["BeforeEach End"]
  T3["Captured Output"]
  T4["By Step: 'setup resources'"]
  T5["ReportEntry: 'initial state'"]
  T6["It Body Start"]
  T7["More Output"]
  T8["Failure (if any)"]
  T9["It Body End"]
  T10["AfterEach Start"]
  T11["AfterEach End"]

  Reporter["DefaultReporter"]
  Timeline["Timeline Output"]

  T0 --> T1 --> T2 --> T3 --> T4 --> T5 --> T6 --> T7 --> T8 --> T9 --> T10 --> T11
  T3 -.-> Timeline
  T4 -.-> Timeline
  T5 -.-> Timeline
  T7 -.-> Timeline
  T8 -.-> Timeline
  Timeline --> Reporter
```

Each event contains:

- Event type and description
- Timestamp and outline position in the test tree
- Source code location (file and line)
- Output offsets linking buffer to timeline

**Sources:**  
[vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go:378-426](),  
[vendor/github.com/onsi/ginkgo/v2/internal/suite.go:284-314]()

### Verbosity Levels

Output detail is configured by `ReporterConfig.Verbosity`, controlling how much info is shown:

| Level         | Value | Output Description                     |
|---------------|-------|--------------------------------------|
| Succinct      | 0     | Minimal dots, summarized failures    |
| Normal        | 1     | One-line per spec, detailed failures |
| Verbose       | 2     | Detailed timeline output on failure  |
| VeryVerbose   | 3     | Timeline with node events, full stack traces |

Example outputs:

- Succinct: `•••S•••F`
- Normal: `✓ It "does X" [0.123s]`
- Verbose: Full details on test events
- VeryVerbose: Includes enter/exit node markers

**Sources:**  
[vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go:185-261]()

### Various Report Formats

Ginkgo generates multiple reports:

```mermaid
graph LR
  Suite["Suite Execution"]

  SR["Suite Report (types.Report)"]

  Console["Console Output"]
  JSON["JSON Report (`--json-report`)"]
  JUnit["JUnit XML (`--junit-report`)"]
  GoJSON["Go JSON (`--gojson-report`)"]

  Suite --> SR
  SR --> Console
  SR --> JSON
  SR --> JUnit
  SR --> GoJSON
```

Key report data structures include the overall suite report and individual spec reports. These contain detailed execution results, states, durations, outputs, failures, and user-added report entries.

**Sources:**  
[vendor/github.com/onsi/ginkgo/v2/reporting_dsl.go:14-23](),  
[vendor/github.com/onsi/ginkgo/v2/internal/suite.go:456-478]()

### Custom Report Entries

Tests can attach custom data to reports using `AddReportEntry`:

```go
It("processes request", func() {
  result := processRequest()

  AddReportEntry("result", result)
  AddReportEntry("timing", result.Timing, ReportEntryVisibilityFailureOrVerbose)

  Expect(result.Success).To(BeTrue())
})
```

Visibility options control when entries appear:

- Always: shown always
- FailureOrVerbose: shown only on failures or verbose output
- Never: never shown in console, only in machine-readable reports

**Sources:**  
[vendor/github.com/onsi/ginkgo/v2/reporting_dsl.go:78-100]()

### Reporting Nodes

Special nodes enable executing hooks to observe or generate reports:

| Node               | Description                                    |
|--------------------|------------------------------------------------|
| `ReportBeforeEach` | Run before each spec, receives `SpecReport`   |
| `ReportAfterEach`  | Run after each spec, receives final `SpecReport` |
| `ReportBeforeSuite`| Run once before suite start, receives `Report`|
| `ReportAfterSuite` | Run once after suite end, receives `Report`   |

Example:

```go
ReportAfterEach(func(r SpecReport) {
  if r.Failed() {
    logFailure(r)
  }
})
```

These augment reporting or diagnostics programmatically.

**Sources:**  
[vendor/github.com/onsi/ginkgo/v2/reporting_dsl.go:103-208]()

---

## Summary

The k8s-test-infra project leverages Ginkgo’s mature BDD testing framework extensively to provide organized, parallelizable, configurable, and well-reported test suites. This page provides a high-level overview of key concepts around test structure, configuration, execution, and reporting.

For practical usage and API details, refer to these child pages:

- [Ginkgo Framework Overview](#5.1)  
- [Test Structure and DSL](#5.2)  
- [Configuration and Parallel Execution](#5.3)  
- [Test Reporting and Output](#5.4)  

---

**Sources:**  
- [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:25-71]()  
- [vendor/github.com/onsi/ginkgo/v2/core_dsl.go:1-53, 127-141, 232-331, 274-294, 546-827]()  
- [vendor/github.com/onsi/ginkgo/v2/internal/node.go:27-70, 214-525, 588-652]()  
- [vendor/github.com/onsi/ginkgo/v2/table_dsl.go:47-194, 112-317]()  
- [vendor/github.com/onsi/ginkgo/v2/reporting_dsl.go:14-208]()  
- [vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go:185-261, 378-426, 479-580]()  
- [vendor/github.com/onsi/ginkgo/v2/CHANGELOG.md:1-38]()  
- [vendor/github.com/onsi/ginkgo/v2/types/version.go:1-4]()

---

# Page: Ginkgo Framework Overview

# Ginkgo Framework Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [go.mod](go.mod)
- [go.sum](go.sum)
- [vendor/github.com/onsi/ginkgo/v2/.gitignore](vendor/github.com/onsi/ginkgo/v2/.gitignore)
- [vendor/github.com/onsi/ginkgo/v2/CHANGELOG.md](vendor/github.com/onsi/ginkgo/v2/CHANGELOG.md)
- [vendor/github.com/onsi/ginkgo/v2/README.md](vendor/github.com/onsi/ginkgo/v2/README.md)
- [vendor/github.com/onsi/ginkgo/v2/core_dsl.go](vendor/github.com/onsi/ginkgo/v2/core_dsl.go)
- [vendor/github.com/onsi/ginkgo/v2/ginkgo/outline/ginkgo.go](vendor/github.com/onsi/ginkgo/v2/ginkgo/outline/ginkgo.go)
- [vendor/github.com/onsi/ginkgo/v2/ginkgo/outline/outline.go](vendor/github.com/onsi/ginkgo/v2/ginkgo/outline/outline.go)
- [vendor/github.com/onsi/ginkgo/v2/helpergo_dsl.go](vendor/github.com/onsi/ginkgo/v2/helpergo_dsl.go)
- [vendor/github.com/onsi/ginkgo/v2/internal/global/init.go](vendor/github.com/onsi/ginkgo/v2/internal/global/init.go)
- [vendor/github.com/onsi/ginkgo/v2/internal/node.go](vendor/github.com/onsi/ginkgo/v2/internal/node.go)
- [vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go](vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go)
- [vendor/github.com/onsi/ginkgo/v2/reporting_dsl.go](vendor/github.com/onsi/ginkgo/v2/reporting_dsl.go)
- [vendor/github.com/onsi/ginkgo/v2/table_dsl.go](vendor/github.com/onsi/ginkgo/v2/table_dsl.go)
- [vendor/github.com/onsi/ginkgo/v2/types/version.go](vendor/github.com/onsi/ginkgo/v2/types/version.go)
- [vendor/k8s.io/apimachinery/pkg/api/validation/objectmeta.go](vendor/k8s.io/apimachinery/pkg/api/validation/objectmeta.go)
- [vendor/modules.txt](vendor/modules.txt)

</details>



## Purpose and Scope

This document introduces Ginkgo's Behavior-Driven Development (BDD) testing framework, focusing on its fundamental architecture, spec organization model, and execution lifecycle. It covers the core concepts needed to understand how Ginkgo organizes and runs tests.

For detailed information about specific DSL constructs (Describe, It, BeforeEach, etc.), see [Test Structure and DSL](#5.2). For configuration options and parallel execution, see [Configuration and Parallel Execution](#5.3). For reporting mechanisms, see [Test Reporting and Output](#5.4).

## Framework Version

This documentation describes Ginkgo v2.32.0, as specified in [vendor/github.com/onsi/ginkgo/v2/types/version.go:3]().

Sources: [vendor/github.com/onsi/ginkgo/v2/types/version.go:1-4]()

## BDD Testing Philosophy

Ginkgo implements a Behavior-Driven Development (BDD) framework for Go that emphasizes readable, hierarchical test organization. Tests are structured as **specs** (specifications) organized in a tree of **nodes**. This allows developers to:

- Group related behaviors using **Container nodes** (Describe, Context, When)
- Define individual test cases using **Subject nodes** (It, Specify)
- Share setup and teardown logic using **Setup nodes** (BeforeEach, AfterEach, etc.)
- Build a narrative flow that describes system behavior in natural language

The framework is designed to be used with Gomega for assertions, though it can work with any assertion library.

Sources: [vendor/github.com/onsi/ginkgo/v2/core_dsl.go:1-16]()

## Node Type System

### Core Node Types

Ginkgo organizes tests using a **Node** structure that represents different types of test constructs. Each node has a specific `NodeType` that determines its role in the test suite.

**Node Type Categories:**

| Category | Node Types | Purpose |
|----------|-----------|---------|
| **Container** | `NodeTypeContainer` | Groups specs (Describe, Context, When) |
| **Subject** | `NodeTypeIt` | Individual test specification |
| **Setup - Spec Level** | `NodeTypeBeforeEach`, `NodeTypeJustBeforeEach`, `NodeTypeAfterEach`, `NodeTypeJustAfterEach` | Run around each spec |
| **Setup - Ordered** | `NodeTypeBeforeAll`, `NodeTypeAfterAll` | Run once per ordered container |
| **Setup - Suite Level** | `NodeTypeBeforeSuite`, `NodeTypeAfterSuite`, `NodeTypeSynchronizedBeforeSuite`, `NodeTypeSynchronizedAfterSuite` | Run once per suite |
| **Reporting** | `NodeTypeReportBeforeEach`, `NodeTypeReportAfterEach`, `NodeTypeReportBeforeSuite`, `NodeTypeReportAfterSuite` | Generate programmatic reports |
| **Cleanup** | `NodeTypeCleanupAfterEach`, `NodeTypeCleanupAfterAll`, `NodeTypeCleanupAfterSuite` | Registered via DeferCleanup |

Sources: [vendor/github.com/onsi/ginkgo/v2/internal/node.go:27-70]()

### Node Structure

```mermaid
graph TB
    Node["Node struct<br/>(internal/node.go)"]
    
    Node --> Identity["Identity<br/>ID: uint<br/>NodeType: types.NodeType<br/>CodeLocation: types.CodeLocation"]
    Node --> Content["Content<br/>Text: string<br/>Body: func(SpecContext)<br/>NestingLevel: int"]
    Node --> Behavior["Behavior Flags<br/>MarkedFocus: bool<br/>MarkedPending: bool<br/>MarkedSerial: bool<br/>MarkedOrdered: bool"]
    Node --> Timing["Timing<br/>NodeTimeout: time.Duration<br/>SpecTimeout: time.Duration<br/>GracePeriod: time.Duration"]
    Node --> Metadata["Metadata<br/>Labels: Labels<br/>SemVerConstraints: SemVerConstraints<br/>FlakeAttempts: int<br/>MustPassRepeatedly: int"]
```

Sources: [vendor/github.com/onsi/ginkgo/v2/internal/node.go:27-70]()

## Hierarchical Spec Organization

### Tree Structure

Ginkgo organizes tests in a hierarchical tree where:
- **Container nodes** (Describe, Context, When) form the internal nodes
- **Subject nodes** (It) form the leaf nodes
- **Setup nodes** (BeforeEach, etc.) are attached at various levels

```mermaid
graph TB
    Root["TreeNode<br/>(root)"]
    
    Root --> Desc1["Describe: 'MyComponent'<br/>NodeType: Container"]
    
    Desc1 --> Before1["BeforeEach<br/>Setup code"]
    Desc1 --> Ctx1["Context: 'when initialized'"]
    Desc1 --> Ctx2["Context: 'when error occurs'"]
    
    Ctx1 --> Before2["BeforeEach<br/>Additional setup"]
    Ctx1 --> It1["It: 'should start properly'<br/>NodeType: It"]
    Ctx1 --> It2["It: 'should be ready'<br/>NodeType: It"]
    
    Ctx2 --> It3["It: 'should log error'<br/>NodeType: It"]
    Ctx2 --> After1["AfterEach<br/>Cleanup"]
```

Sources: [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:25-35]()

### Spec Generation from Tree

A **spec** is generated for each `It` node by traversing from the root to that leaf, collecting all relevant setup nodes along the path. This creates the execution plan for a single test.

```mermaid
graph LR
    Tree["Spec Tree<br/>(TreeNode)"]
    
    Tree -->|"GenerateSpecsFromTreeRoot"| Specs["Specs<br/>([]Spec)"]
    
    Specs -->|"ApplyFocusToSpecs"| Filtered["Filtered Specs"]
    
    Filtered -->|"ComputeAroundNodes"| Final["Final Spec List<br/>with Around Nodes"]
    
    Final --> Exec["Execute Specs"]
```

Sources: [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:111-141]()

## Suite Lifecycle Phases

The `Suite` struct manages the entire test suite lifecycle through three distinct phases:

```mermaid
stateDiagram-v2
    [*] --> PhaseBuildTopLevel
    
    PhaseBuildTopLevel: Phase 0: Build Top Level
    note right of PhaseBuildTopLevel
        Top-level containers collected
        Not yet entered
    end note
    
    PhaseBuildTopLevel --> PhaseBuildTree: BuildTree() called
    
    PhaseBuildTree: Phase 1: Build Tree
    note right of PhaseBuildTree
        Enter containers
        Construct spec tree
        Execute container bodies
    end note
    
    PhaseBuildTree --> PhaseRun: Run() called
    
    PhaseRun: Phase 2: Run
    note right of PhaseRun
        Generate specs from tree
        Apply focus and filters
        Execute specs
        Generate reports
    end note
    
    PhaseRun --> [*]
```

Sources: [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:15-21](), [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:98-141]()

### Phase Details

**Phase 0: PhaseBuildTopLevel**
- Top-level container nodes (Describe, Context) are collected but not entered
- Stored in `suite.topLevelContainers`
- Allows flag parsing and configuration before tree construction
- Purpose: Ensures `RunSpecs()` can configure the suite before building the test tree

**Phase 1: PhaseBuildTree**
- Top-level containers are entered and their closures executed
- The spec tree (`TreeNode`) is constructed
- Nested Describe/Context/It calls create the hierarchical structure
- Container bodies run during this phase to define the tree structure

**Phase 2: PhaseRun**
- Specs are generated from the completed tree
- Focus and filter rules are applied
- Specs are executed in order (with optional parallelization)
- Reports are generated

Sources: [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:98-141](), [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:186-228]()

## Suite Structure and Key Components

### Suite Struct

The `Suite` struct is the central orchestrator for test execution:

```mermaid
graph TB
    Suite["Suite struct<br/>(internal/suite.go:25)"]
    
    Suite --> TreeMgmt["Tree Management<br/>tree: *TreeNode<br/>topLevelContainers: Nodes<br/>phase: Phase"]
    
    Suite --> NodeCollections["Node Collections<br/>suiteNodes: Nodes<br/>cleanupNodes: Nodes<br/>aroundNodes: types.AroundNodes"]
    
    Suite --> Runtime["Runtime State<br/>currentSpecReport: SpecReport<br/>currentNode: Node<br/>currentNodeStartTime: time.Time<br/>currentSpecContext: *specContext"]
    
    Suite --> Infrastructure["Infrastructure<br/>failer: *Failer<br/>reporter: reporters.Reporter<br/>writer: WriterInterface<br/>outputInterceptor: OutputInterceptor<br/>interruptHandler: InterruptHandlerInterface"]
    
    Suite --> Config["Configuration<br/>config: types.SuiteConfig<br/>deadline: time.Time"]
    
    Suite --> Sync["Synchronization<br/>selectiveLock: *sync.Mutex"]
```

Sources: [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:25-71]()

### Core Components Interaction

```mermaid
graph TB
    RunSpecs["RunSpecs()<br/>(core_dsl.go:260)"]
    
    RunSpecs -->|"Creates"| Suite["Suite<br/>(internal/suite.go)"]
    
    Suite -->|"Uses"| Reporter["reporters.Reporter<br/>(DefaultReporter)"]
    Suite -->|"Uses"| Failer["Failer<br/>(handles failures)"]
    Suite -->|"Uses"| Writer["GinkgoWriter<br/>(output management)"]
    Suite -->|"Uses"| OutputInterceptor["OutputInterceptor<br/>(captures stdout/stderr)"]
    
    Suite -->|"Builds"| Tree["TreeNode<br/>(spec hierarchy)"]
    Tree -->|"Generates"| Specs["Specs<br/>(execution units)"]
    
    Suite -->|"Executes"| Specs
    Specs -->|"Reports to"| Reporter
    Specs -->|"May call"| Failer
    Specs -->|"Writes to"| Writer
```

Sources: [vendor/github.com/onsi/ginkgo/v2/core_dsl.go:260-331](), [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:111-141]()

## Spec Execution Model

### From Tree to Execution

```mermaid
flowchart TD
    Start["Suite.Run() starts<br/>(suite.go:111)"]
    
    Start --> ApplyNesting["ApplyNestedFocusPolicyToTree()<br/>Mark focused/pending nodes"]
    
    ApplyNesting --> GenSpecs["GenerateSpecsFromTreeRoot()<br/>Create Spec for each It node"]
    
    GenSpecs --> ApplyFocus["ApplyFocusToSpecs()<br/>Filter by focus/labels/semver"]
    
    ApplyFocus --> ComputeAround["ComputeAroundNodes()<br/>Attach AroundNode decorators"]
    
    ComputeAround --> Order["OrderSpecs()<br/>Randomize or prioritize"]
    
    Order --> BeforeSuite["Run BeforeSuite nodes<br/>(if present)"]
    
    BeforeSuite --> ExecLoop["Execute individual specs"]
    
    ExecLoop --> Group["newGroup().run()<br/>Handle ordered containers<br/>and flake attempts"]
    
    Group --> SpecExec["Execute individual spec<br/>Run setup → body → teardown"]
    
    SpecExec -->|"More specs"| ExecLoop
    ExecLoop -->|"Done"| AfterSuite["Run AfterSuite nodes<br/>(if present)"]
    
    AfterSuite --> ReportSuite["Report suite results"]
    ReportSuite --> End["Return success bool"]
```

Sources: [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:111-141](), [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:456-552]()

### Node Execution Context

Each node can have an interruptible context for timeout and cancellation support:

```mermaid
graph TB
    NodeDef["Node Definition<br/>(func signature)"]
    
    NodeDef -->|"No context"| BasicBody["func()<br/>Non-interruptible"]
    NodeDef -->|"SpecContext"| CtxBody["func(SpecContext)<br/>Interruptible"]
    NodeDef -->|"context.Context"| StdCtxBody["func(context.Context)<br/>Interruptible"]
    
    CtxBody --> NodeTimeout["NodeTimeout decorator<br/>Timeout for this node"]
    CtxBody --> SpecTimeout["SpecTimeout decorator<br/>Timeout for entire spec"]
    CtxBody --> GracePeriod["GracePeriod decorator<br/>Cleanup time after timeout"]
    
    NodeTimeout --> Execution["Suite manages context<br/>Cancels on timeout/interrupt"]
    SpecTimeout --> Execution
    GracePeriod --> Execution
    
    Execution --> Cancel["Context cancelled<br/>Node receives signal"]
```

Sources: [vendor/github.com/onsi/ginkgo/v2/internal/node.go:211-213](), [vendor/github.com/onsi/ginkgo/v2/internal/node.go:503-525](), [vendor/github.com/onsi/ginkgo/v2/core_dsl.go:95-102]()

## Node Construction and Decoration

### Node Creation Flow

Nodes are created through DSL functions (Describe, It, BeforeEach, etc.) which go through a standardized construction process:

```mermaid
flowchart TD
    DSL["DSL Function<br/>(e.g., It, Describe)"]
    
    DSL -->|"Calls"| Transform["TransformNewNodeArgs()<br/>(node.go:1053)"]
    
    Transform -->|"Applies"| Transformers["NodeArgsTransformers<br/>(user-registered)"]
    
    Transformers --> NewNode["NewNode()<br/>(node.go:214)"]
    
    NewNode --> ParseArgs["Parse arguments:<br/>- Extract decorations<br/>- Extract body function<br/>- Process labels, timeouts, etc."]
    
    ParseArgs --> Validate["Validate configuration:<br/>- Check decorator compatibility<br/>- Verify body function signature<br/>- Validate labels"]
    
    Validate -->|"Errors?"| Errors["Return errors"]
    Validate -->|"Success"| Node["Return Node struct"]
    
    Node --> Push["pushNode()<br/>(core_dsl.go:498)"]
    
    Push --> Suite["Suite.PushNode()<br/>Add to tree"]
```

Sources: [vendor/github.com/onsi/ginkgo/v2/internal/node.go:214-499](), [vendor/github.com/onsi/ginkgo/v2/internal/node.go:1047-1078](), [vendor/github.com/onsi/ginkgo/v2/core_dsl.go:496-502]()

### Decoration Types

Nodes support various decorators that modify their behavior:

| Decorator | Type | Purpose |
|-----------|------|---------|
| `Focus` | `focusType` | Mark spec/container to run exclusively |
| `Pending` | `pendingType` | Mark as pending (skip execution) |
| `Serial` | `serialType` | Run serially, not in parallel |
| `Ordered` | `orderedType` | Container with ordered execution |
| `FlakeAttempts(n)` | `FlakeAttempts` | Retry on failure up to n times |
| `MustPassRepeatedly(n)` | `MustPassRepeatedly` | Must pass n times in a row |
| `NodeTimeout(d)` | `NodeTimeout` | Timeout for individual node |
| `SpecTimeout(d)` | `SpecTimeout` | Timeout for entire spec |
| `GracePeriod(d)` | `GracePeriod` | Grace period after timeout |
| `Label(...)` | `Labels` | Attach labels for filtering |
| `Offset(n)` | `Offset` | Adjust code location reporting |
| `SpecPriority(n)` | `SpecPriority` | Set execution priority |

Sources: [vendor/github.com/onsi/ginkgo/v2/internal/node.go:72-98](), [vendor/github.com/onsi/ginkgo/v2/internal/node.go:147-196]()

## Reporter Integration

### Default Reporter

The `DefaultReporter` handles console output and provides the visual feedback during test execution:

```mermaid
graph TB
    Reporter["DefaultReporter<br/>(reporters/default_reporter.go:22)"]
    
    Reporter --> Config["Configuration<br/>conf: ReporterConfig<br/>writer: io.Writer<br/>formatter: Formatter"]
    
    Reporter --> Lifecycle["Lifecycle Methods"]
    
    Lifecycle --> SuiteBegin["SuiteWillBegin(Report)<br/>Print suite header"]
    Lifecycle --> WillRun["WillRun(SpecReport)<br/>Print spec start"]
    Lifecycle --> DidRun["DidRun(SpecReport)<br/>Print spec result"]
    Lifecycle --> SuiteEnd["SuiteDidEnd(Report)<br/>Print suite summary"]
    
    Reporter --> Progress["Progress Reporting"]
    Progress --> EmitProgress["EmitProgressReport()<br/>Show current execution state"]
    Progress --> EmitReportEntry["EmitReportEntry()<br/>Show custom report entries"]
    
    Reporter --> Output["Output Management<br/>Handles colors, indentation<br/>Timeline rendering<br/>Failure formatting"]
```

Sources: [vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go:22-66](), [vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go:69-349]()

## Entry Point: RunSpecs

The `RunSpecs` function is the main entry point that ties everything together:

```mermaid
flowchart TD
    TestFunc["TestXxx(t *testing.T)<br/>(Go test function)"]
    
    TestFunc --> RunSpecs["RunSpecs(t, description, ...args)<br/>(core_dsl.go:260)"]
    
    RunSpecs --> Clone["Clone global suite<br/>Allows suite reuse"]
    
    Clone --> Extract["Extract configuration<br/>- Suite labels<br/>- SemVer constraints<br/>- Around nodes"]
    
    Extract --> Setup["Setup infrastructure<br/>- Reporter (DefaultReporter or Noop)<br/>- OutputInterceptor<br/>- Parallel client (if parallel)"]
    
    Setup --> Register["Register auto-generated reports<br/>(JSON, JUnit, etc.)"]
    
    Register --> BuildTree["Suite.BuildTree()<br/>Construct spec hierarchy"]
    
    BuildTree --> Run["Suite.Run()<br/>Execute specs"]
    
    Run --> Check["Check for deprecations<br/>and focused specs"]
    
    Check --> Fail{"Success?"}
    Fail -->|"No"| TFail["t.Fail()"]
    Fail -->|"Yes, but focused"| Exit["Exit with GINKGO_FOCUS_EXIT_CODE"]
    Fail -->|"Yes"| Return["Return true"]
```

Sources: [vendor/github.com/onsi/ginkgo/v2/core_dsl.go:260-331]()

## Key Interfaces and Types

### GinkgoWriterInterface

`GinkgoWriter` provides output management with automatic buffering and flushing:

```go
// Defined in core_dsl.go:82-92
type GinkgoWriterInterface interface {
    io.Writer
    Print(a ...any)
    Printf(format string, a ...any)
    Println(a ...any)
    TeeTo(writer io.Writer)
    ClearTeeWriters()
}
```

Sources: [vendor/github.com/onsi/ginkgo/v2/core_dsl.go:82-92]()

### SpecContext

`SpecContext` is the context passed to interruptible nodes, extending `context.Context`:

- Provides cancellation signals on timeout or interrupt
- Allows progress reporters to attach additional information
- Can be wrapped with standard context functions (WithTimeout, WithValue, etc.)

Sources: [vendor/github.com/onsi/ginkgo/v2/core_dsl.go:95-102]()

### Report Types

Two main report types exist:

1. **Report** (`types.Report`): Represents the entire suite
   - Contains all spec reports
   - Suite configuration
   - Success/failure status
   - Special failure reasons

2. **SpecReport** (`types.SpecReport`): Represents a single spec
   - State (Passed, Failed, Skipped, etc.)
   - Timing information
   - Failure details
   - Report entries
   - Timeline of events

Sources: [vendor/github.com/onsi/ginkgo/v2/reporting_dsl.go:13-23]()

## Summary

Ginkgo's architecture centers on:

1. **Hierarchical organization**: Tests organized in a tree of Container, Subject, and Setup nodes
2. **Three-phase lifecycle**: Build Top Level → Build Tree → Run
3. **Node-based execution**: Each node type has specific behavior and lifecycle hooks
4. **Flexible decoration**: Nodes can be modified with decorators for focus, timeouts, retries, etc.
5. **Comprehensive reporting**: Integration with reporters for detailed test output

This foundation enables the BDD-style testing patterns that Ginkgo is known for, allowing developers to write expressive, well-organized test suites.

---

# Page: Test Structure and DSL

# Test Structure and DSL

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/nvml-mock-e2e-go.yaml](.github/workflows/nvml-mock-e2e-go.yaml)
- [Makefile](Makefile)
- [README.md](README.md)
- [tests/e2e/README.md](tests/e2e/README.md)
- [tests/e2e/go/e2e_suite_test.go](tests/e2e/go/e2e_suite_test.go)
- [tests/e2e/go/framework/config/config.go](tests/e2e/go/framework/config/config.go)
- [tests/e2e/go/framework/harness/harness.go](tests/e2e/go/framework/harness/harness.go)
- [tests/e2e/go/suite_cluster.go](tests/e2e/go/suite_cluster.go)
- [tests/e2e/go/suite_helm.go](tests/e2e/go/suite_helm.go)
- [vendor/github.com/onsi/ginkgo/v2/README.md](vendor/github.com/onsi/ginkgo/v2/README.md)
- [vendor/github.com/onsi/ginkgo/v2/core_dsl.go](vendor/github.com/onsi/ginkgo/v2/core_dsl.go)
- [vendor/github.com/onsi/ginkgo/v2/internal/global/init.go](vendor/github.com/onsi/ginkgo/v2/internal/global/init.go)
- [vendor/github.com/onsi/ginkgo/v2/internal/node.go](vendor/github.com/onsi/ginkgo/v2/internal/node.go)
- [vendor/github.com/onsi/ginkgo/v2/reporting_dsl.go](vendor/github.com/onsi/ginkgo/v2/reporting_dsl.go)
- [vendor/github.com/onsi/ginkgo/v2/table_dsl.go](vendor/github.com/onsi/ginkgo/v2/table_dsl.go)
- [vendor/github.com/onsi/gomega/CHANGELOG.md](vendor/github.com/onsi/gomega/CHANGELOG.md)
- [vendor/github.com/onsi/gomega/format/format.go](vendor/github.com/onsi/gomega/format/format.go)
- [vendor/github.com/onsi/gomega/gomega_dsl.go](vendor/github.com/onsi/gomega/gomega_dsl.go)
- [vendor/github.com/onsi/gomega/matchers.go](vendor/github.com/onsi/gomega/matchers.go)
- [vendor/github.com/onsi/gomega/matchers/be_a_slice_matcher.go](vendor/github.com/onsi/gomega/matchers/be_a_slice_matcher.go)
- [vendor/github.com/onsi/gomega/matchers/be_an_array_matcher.go](vendor/github.com/onsi/gomega/matchers/be_an_array_matcher.go)
- [vendor/github.com/onsi/gomega/types/types.go](vendor/github.com/onsi/gomega/types/types.go)

</details>



This page documents the Ginkgo Domain-Specific Language (DSL) used in the k8s-test-infra repository to structure E2E and unit tests. It covers the hierarchical test node types (`Describe`, `Context`, `It`), setup and teardown hooks (`BeforeEach`, `AfterEach`), decorators for controlling test execution, and table-driven testing patterns commonly used in the E2E and unit test suites.

This detailed documentation explains how tests are composed, how Ginkgo organizes the execution lifecycle, and how DSL constructs generate rich, maintainable test suites. It also bridges terminology from natural language test descriptions into specific code entities and functions.

For configuration and parallel execution details, see the sibling page [5.3 Configuration and Parallel Execution](). For reporting and output, see [5.4 Test Reporting and Output](). For the Ginkgo framework overview, see [5.1 Ginkgo Framework Overview]().

---

## Node Type Hierarchy

Ginkgo organizes test code into a tree structure of various node types:

- **Container nodes**: logical groups, e.g. `Describe`, `Context`, `When`.
- **Subject nodes**: individual test cases, e.g. `It`, `Specify`.
- **Setup/teardown nodes**: hooks like `BeforeEach`, `AfterEach`.
- **Suite-level hooks**: `BeforeSuite`, `AfterSuite`.
- **Deferred cleanup**: `DeferCleanup` registrations.
- **Reporting nodes**: utilities like `By()` and `AddReportEntry()`.

The following diagram shows the node types and their hierarchical relationships:

```mermaid
graph TB
    subgraph "Container Nodes"
        Describe["Describe()<br/>Context()<br/>When()"]
        Ordered["Ordered Container<br/>(decorated with Ordered)"]
    end
    
    subgraph "Subject Nodes"
        It["It()<br/>Specify()"]
    end
    
    subgraph "Setup Nodes"
        BeforeEach["BeforeEach()"]
        JustBeforeEach["JustBeforeEach()"]
        BeforeAll["BeforeAll()<br/>(Ordered only)"]
        AfterEach["AfterEach()"]
        JustAfterEach["JustAfterEach()"]
        AfterAll["AfterAll()<br/>(Ordered only)"]
    end
    
    subgraph "Suite Nodes"
        BeforeSuite["BeforeSuite()"]
        AfterSuite["AfterSuite()"]
        SyncBefore["SynchronizedBeforeSuite()"]
        SyncAfter["SynchronizedAfterSuite()"]
    end
    
    subgraph "Cleanup"
        DeferCleanup["DeferCleanup()"]
    end
    
    subgraph "Reporting"
        ReportBeforeEach["ReportBeforeEach()"]
        ReportAfterEach["ReportAfterEach()"]
        ReportBeforeSuite["ReportBeforeSuite()"]
        ReportAfterSuite["ReportAfterSuite()"]
        By["By()"]
        AddReportEntry["AddReportEntry()"]
    end
    
    Describe -->|contains| It
    Describe -->|contains| BeforeEach
    Describe -->|contains| AfterEach
    Ordered -->|contains| BeforeAll
    Ordered -->|contains| AfterAll
```

*Sources: [vendor/github.com/onsi/ginkgo/v2/core_dsl.go:546-653](), [vendor/github.com/onsi/ginkgo/v2/internal/node.go:27-70]()*


---

## Container Nodes

Container nodes group tests into hierarchical contexts. They organize the specification into readable, logical sections.

### Core Container Functions

| Function         | Purpose                                        | Alias of    |
|------------------|------------------------------------------------|-------------|
| `Describe(text, body)` | Primary container node                    | -           |
| `Context(text, body)`  | Alias for `Describe` used for context groups | `Describe`  |
| `When(text, body)`     | Alias for `Describe` with "when " prefix  | `Describe`  |
| `FDescribe` / `FContext` / `FWhen` | Focused container (only these run) | -     |
| `PDescribe` / `PContext` / `PWhen` | Pending container (skipped)     | -           |
| `XDescribe` / `XContext` / `XWhen` | Pending alias                 | `PDescribe` |

Containers define test sections and can nest arbitrarily.

### Container Structure Example

```mermaid
graph TD
    Root["Suite Root"]
    D1["Describe('Calculator')"]
    C1["Context('when adding')"]
    C2["Context('when subtracting')"]
    It1["It('returns sum')"]
    It2["It('handles negatives')"]
    It3["It('returns difference')"]
    
    Root --> D1
    D1 --> C1
    D1 --> C2
    C1 --> It1
    C1 --> It2
    C2 --> It3
    
    BE1["BeforeEach (level 1)"]
    BE2["BeforeEach (level 2)"]
    
    D1 -.->|runs before each It| BE1
    C1 -.->|runs before It1, It2| BE2
```

This organizes specs hierarchically for clarity and reuse of setup code.

### Container Execution Flow

At runtime, the body functions of container nodes execute to register child nodes:

```mermaid
sequenceDiagram
    participant Suite as Suite
    participant Container as Describe/Context
    participant Body as Container Body
    participant Child as Child Nodes
    
    Suite->>Container: PushNode(container)
    Container->>Body: Execute body closure
    Body->>Child: Define It(), BeforeEach(), etc.
    Child->>Suite: Register child nodes
    Body->>Container: Return
    Container->>Suite: Complete registration
```

The container body defines the nested test structure dynamically.

*Sources: [vendor/github.com/onsi/ginkgo/v2/core_dsl.go:546-593](), [vendor/github.com/onsi/ginkgo/v2/internal/node.go:187-228](), [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:98-109]()*

---

## Subject Nodes (`It`, `Specify`)

Subject nodes hold the actual test logic and assertions.

### Subject Node Functions

| Function | Description                              |
| -------- | ----------------------------------------|
| `It(text, func)` | Defines a single test case          |
| `Specify(text, func)` | Alias for `It`                  |
| `FIt`, `FSpecify` | Focused variant (only these run) |
| `PIt`, `PSpecify` | Pending variant (skipped)        |
| `XIt`, `XSpecify` | Alias for `PIt`                  |

### Subject Node Function Signatures and Interruptibility

Subject nodes support several function signatures:

```mermaid
graph LR
    It["It()"]
    
    subgraph "Function Signatures"
        F1["func()"]
        F2["func(SpecContext)"]
        F3["func(context.Context)"]
    end
    
    It -->|non-interruptible| F1
    It -->|interruptible| F2
    It -->|interruptible| F3
    
    F2 -.->|"cancellable via timeout"| Timeout["NodeTimeout()<br/>SpecTimeout()"]
    F3 -.->|"cancellable via timeout"| Timeout
```

If the provided test function accepts `SpecContext` or `context.Context`, it can be externally cancelled on timeout or interrupt signals.

Example interruptible spec:

```go
It("should complete within timeout", func(ctx SpecContext) {
    // test logic with ctx cancellation support
}, NodeTimeout(30*time.Second))
```

*Sources: [vendor/github.com/onsi/ginkgo/v2/core_dsl.go:605-630](), [vendor/github.com/onsi/ginkgo/v2/internal/node.go:503-525](), [vendor/github.com/onsi/ginkgo/v2/core_dsl.go:94-101](), [vendor/github.com/onsi/ginkgo/v2/internal/node.go:468-472]()*


---

## Setup and Teardown Hooks

Setup and teardown nodes run preparation and cleanup code around tests.

### Hook Types and Execution Order

```mermaid
graph TB
    subgraph "Hook Execution Per Spec"
        BS[BeforeSuite]
        BA[BeforeAll]
        BE[BeforeEach]
        JBE[JustBeforeEach]
        IT[It - Spec Body]
        JAE[JustAfterEach]
        AE[AfterEach]
        AA[AfterAll]
        AS[AfterSuite]
    end
    
    BS --> BA --> BE --> JBE --> IT --> JAE --> AE --> AA --> AS
    
    BE -.->|"per It spec"| IT
    AE -.->|"per It spec"| IT
    BA -.->|"once per Ordered container"| IT
    AA -.->|"once per Ordered container"| IT
```

- `BeforeSuite` / `AfterSuite`: Suite-wide setup/teardown, run once.
- `BeforeAll` / `AfterAll`: Run once per `Ordered` container.
- `BeforeEach` / `AfterEach`: Run before/after each spec in container subtree.
- `JustBeforeEach` / `JustAfterEach`: For ordering around `BeforeEach` and `AfterEach`.

### Setup/Teardown Hook API Summary

| Hook Type           | Execution Frequency               | Scope                      | Supports DeferCleanup |
|---------------------|---------------------------------|----------------------------|----------------------|
| `BeforeSuite()`     | Once per suite                   | Suite-wide                 | Yes                  |
| `BeforeAll()`       | Once per Ordered container       | Ordered container only     | Yes                  |
| `BeforeEach()`      | Before each spec                 | Container and descendants  | Yes                  |
| `JustBeforeEach()`  | After `BeforeEach`, before spec | Container and descendants  | Yes                  |
| `AfterEach()`       | After each spec                  | Container and descendants  | Yes                  |
| `JustAfterEach()`   | Before `AfterEach`, after spec  | Container and descendants  | Yes                  |
| `AfterAll()`        | Once per Ordered container       | Ordered container only     | Yes                  |
| `AfterSuite()`      | Once per suite                  | Suite-wide                 | Yes                  |

### DeferCleanup

`DeferCleanup(func())` registers cleanup functions to run after the current hook or spec finishes, ensuring proper resource release.

The timing depends on where it is called:

- Called in `BeforeSuite` ⇒ runs during `AfterSuite`.
- Called in `BeforeAll` ⇒ runs during `AfterAll`.
- Called in `BeforeEach` ⇒ runs during `AfterEach`.
- Called in `It` ⇒ runs during `AfterEach`.

This enables structured resource cleanup without manual tracking.

```mermaid
graph LR
    Setup["Setup Hook/Spec"]
    Cleanup["DeferCleanup(func)"]
    Execution["Spec Execution"]
    CleanupRun["Deferred Cleanup Run"]
    
    Setup -->|registers| Cleanup
    Setup --> Execution
    Execution --> CleanupRun
```

### Synchronized Suite Hooks

For parallel test runs, Ginkgo provides synchronized suite hooks to coordinate setup/teardown across processes:

```mermaid
sequenceDiagram
    participant P1 as Process 1
    participant P2 as Process 2
    participant PN as Process N
    
    Note over P1, PN: SynchronizedBeforeSuite
    P1->>P1: Run Proc1 body -> []byte
    P1->>P2: Send data
    P1->>PN: Send data
    P2->>P2: Run AllProcs body with data
    PN->>PN: Run AllProcs body with data
    
    Note over P1, PN: Run Specs in Parallel
    
    Note over P1, PN: SynchronizedAfterSuite
    P1->>P1: Run AllProcs body
    P2->>P2: Run AllProcs body
    PN->>PN: Run AllProcs body
    P1->>P1: Wait for others, then Proc1 body
```

This pattern is used in `./tests/e2e/go/e2e_suite_test.go` to build the shared nvml-mock image once per parallel process group before running tests.

*Sources: [vendor/github.com/onsi/ginkgo/v2/core_dsl.go:666-766](), [vendor/github.com/onsi/ginkgo/v2/internal/node.go:239-254](), [vendor/github.com/onsi/ginkgo/v2/core_dsl.go:693-739]()*


---

## Decorators

Decorators modify node behavior to control execution characteristics like focus, timeouts, retries, ordering, labels, and priorities.

### Decorator Types

```mermaid
graph TB
    subgraph "Focus"
        Focus["Focus (run only these)"]
        Pending["Pending (skip these)"]
    end
    
    subgraph "Execution"
        Serial["Serial (no parallel)"]
        Ordered["Ordered (sequential)"]
        ContinueOnFailure["ContinueOnFailure"]
        OncePerOrdered["OncePerOrdered (setup/teardown)"]
    end
    
    subgraph "Retries"
        FlakeAttempts["FlakeAttempts(n)"]
        MustPassRepeatedly["MustPassRepeatedly(n)"]
    end
    
    subgraph "Timeouts"
        NodeTimeout["NodeTimeout(duration)"]
        SpecTimeout["SpecTimeout(duration)"]
        GracePeriod["GracePeriod(duration)"]
    end
    
    subgraph "Progress"
        PollProgressAfter["PollProgressAfter(d)"]
        PollProgressInterval["PollProgressInterval(d)"]
    end
    
    subgraph "Metadata"
        Labels["Label(strings...)"]
        SemVerConstraint["SemVerConstraint(strings...)"]
        SpecPriority["SpecPriority(int)"]
    end
    
    subgraph "Location"
        Offset["Offset(n)"]
        CodeLocation["types.CodeLocation"]
    end
```

### Decorator Application Rules

| Decorator           | Valid On            | Notes                                                   |
|---------------------|---------------------|---------------------------------------------------------|
| `Focus`             | Containers, It      | Runs only focused specs                                   |
| `Pending`           | Containers, It      | Marks specs as skipped                                   |
| `Serial`            | Containers, It      | Prevents parallel execution; adds `Serial` label         |
| `Ordered`           | Containers          | Containers run sequentially                              |
| `ContinueOnFailure` | Ordered containers  | Continues execution after failures                       |
| `OncePerOrdered`    | Setup/teardown hooks| Runs once per Ordered container                          |
| `FlakeAttempts(n)`  | Containers, It      | Retries on failure (cannot combine with `MustPassRepeatedly`) |
| `MustPassRepeatedly(n)` | Containers, It   | Tests must pass repeatedly (cannot combine with `FlakeAttempts`) |
| `NodeTimeout()`     | Except container    | Timeout per node; requires interruptible test function  |
| `SpecTimeout()`     | It only             | Timeout for entire test; requires interruptible test function |
| `GracePeriod()`     | Except container    | Grace period allowed for cleanup phase                   |
| `Label()`           | Containers, It      | For filtering and organization                           |
| `SemVerConstraint()`| Containers, It      | Filters execution by semantic version constraints       |
| `SpecPriority()`    | Containers, It      | Controls ordering of tests                               |
| `Offset()`, `CodeLocation()` | All        | Advanced control of code location during reporting      |

### Example Usage

```go
Describe("API Client", Label("integration", "api"), func() {
    It("connects successfully",
        func(ctx SpecContext) {
            // test code
        },
        NodeTimeout(5*time.Second),
        FlakeAttempts(3),
    )
    
    It("handles timeout", Serial, func() {
        // runs serially, no parallel execution
    })
})
```

*Sources: [vendor/github.com/onsi/ginkgo/v2/internal/node.go:72-98](), [vendor/github.com/onsi/ginkgo/v2/internal/node.go:261-363]()*


---

## Table-Driven Tests

Ginkgo supports table-driven tests to reduce repetition by defining sets of inputs and expected behaviors.

### Table-Driven Test Structure

```mermaid
graph TB
    DescribeTable["DescribeTable('description', body, entries...)"]
    Body["func(params...) { test logic }"]
    Entry1["Entry('case 1', arg1, arg2, ...)"]
    Entry2["Entry('case 2', arg1, arg2, ...)"]
    EntryN["Entry('case N', arg1, arg2, ...)"]
    
    It1["It('case 1')"]
    It2["It('case 2')"]
    ItN["It('case N')"]
    
    DescribeTable -->|generates| It1
    DescribeTable -->|generates| It2
    DescribeTable -->|generates| ItN
    
    Body -.->|"called with<br/>entry params"| It1
    Body -.->|"called with<br/>entry params"| It2
    Body -.->|"called with<br/>entry params"| ItN
    
    Entry1 -->|provides params| It1
    Entry2 -->|provides params| It2
    EntryN -->|provides params| ItN
```

Each `Entry` expands to a separate `It` test executed with unique parameters.

### Table DSL Functions

| Function               | Purpose                             | Generates                       |
|------------------------|-----------------------------------|--------------------------------|
| `DescribeTable()`      | Defines a table-driven test        | Multiple `It` subject nodes    |
| `DescribeTableSubtree()` | Defines table where each entry generates a container subtree | Multiple `Describe` containers |
| `Entry()`              | Test case with parameters          | Parameters to test function    |
| `FEntry()`             | Focused test case                  | Focused subject node           |
| `PEntry()`             | Pending (skipped) test case        | Skipped subject node            |
| `EntryDescription`     | Format description for entries     | Entry name template or callback |

### Entry Description Generation

Entry names are generated using various methods:

```mermaid
graph TD
    EntryDesc["Entry Description"]
    
    subgraph "Description Methods"
        Explicit["Explicit string"]
        NilDefault["nil → table-level format"]
        EntryFormat["EntryDescription format"]
        Function["func(params) string"]
    end
    
    EntryDesc --> Explicit
    EntryDesc --> NilDefault
    EntryDesc --> EntryFormat
    EntryDesc --> Function
    
    NilDefault -.->|uses| TableFormat["DescribeTable<br/>EntryDescription"]
    EntryFormat -.->|"fmt.Sprintf with<br/>entry params"| Generated
    Function -.->|"call with<br/>entry params"| Generated
```

### Table Body Function Signatures

Table body functions accept either plain or interruptible functions, with variadic or fixed parameters:

```go
// Basic, non-interruptible
DescribeTable("basic", func(x int, y string) { ... })

// Interruptible with SpecContext
DescribeTable("with context", func(ctx SpecContext, x int, y string) { ... })

// Variadic parameter support
DescribeTable("variadic", func(first int, rest ...string) { ... })
```

### DescribeTableSubtree

`DescribeTableSubtree` generates a container subtree for each entry, each with its own hooks and specs:

```mermaid
graph TB
    DTS["DescribeTableSubtree('HTTP Client')"]
    
    Entry1["Entry('GET', ...)"]
    Entry2["Entry('POST', ...)"]
    
    Container1["Describe('GET')"]
    Container2["Describe('POST')"]
    
    BE1["BeforeEach in subtree"]
    BE2["BeforeEach in subtree"]
    
    It1["It('returns 200')"]
    It2["It('includes body')"]
    It3["It('creates resource')"]
    It4["It('validates input')"]
    
    DTS --> Entry1
    DTS --> Entry2
    
    Entry1 -.->|generates| Container1
    Entry2 -.->|generates| Container2
    
    Container1 --> BE1
    Container1 --> It1
    Container1 --> It2
    
    Container2 --> BE2
    Container2 --> It3
    Container2 --> It4
```

*Sources: [vendor/github.com/onsi/ginkgo/v2/table_dsl.go:13-194](), [vendor/github.com/onsi/ginkgo/v2/table_dsl.go:112-141](), [vendor/github.com/onsi/ginkgo/v2/table_dsl.go:248-378]()*


---

## Reporting and Documentation Helpers

Ginkgo provides utilities to document test steps and attach additional information during test execution.

### Reporting DSL Functions

```mermaid
graph TB
    subgraph "In-Spec Reporting"
        By["By('step description')"]
        AddReportEntry["AddReportEntry('name', value)"]
    end
    
    subgraph "Spec Lifecycle Reporting"
        ReportBeforeEach["ReportBeforeEach(func(SpecReport))"]
        ReportAfterEach["ReportAfterEach(func(SpecReport))"]
    end
    
    subgraph "Suite Lifecycle Reporting"
        ReportBeforeSuite["ReportBeforeSuite(func(Report))"]
        ReportAfterSuite["ReportAfterSuite('name', func(Report))"]
    end
    
    subgraph "Access Current State"
        CurrentSpecReport["CurrentSpecReport() SpecReport"]
    end
    
    By -.->|"emits SpecEvent"| Timeline["Timeline in SpecReport"]
    AddReportEntry -.->|adds| ReportEntries["SpecReport.ReportEntries"]
    CurrentSpecReport -.->|retrieves| SpecReport["types.SpecReport"]
```

### `By` - Documenting Spec Steps

The `By()` function documents a logical step inside an `It` block, producing timeline events and improving output readability:

```go
It("processes order", func() {
    By("validating input")
    // validation code
    
    By("calculating total")
    // calculation code
    
    By("saving to database", func() {
        // immediate callback execution allowed
    })
})
```

The timeline of `By` calls appears in reports and helps trace test progress.

### `AddReportEntry` - Attaching Additional Data

`AddReportEntry(name string, value any, visibility ...)` attaches arbitrary data to the current spec report. Different visibility options control when it appears:

| Visibility Option               | Shown When               |
| ----------------------------- | ----------------------- |
| `ReportEntryVisibilityAlways` | Always in console output  |
| `ReportEntryVisibilityFailureOrVerbose` | Only on failure or verbose mode (`-v`) |
| `ReportEntryVisibilityNever`  | Only in machine-readable reports |

Example:

```go
It("generates data", func() {
    result := compute()
    AddReportEntry("computation", result) // shows in all reports
    
    AddReportEntry("debug", debugData, ReportEntryVisibilityFailureOrVerbose) // conditional
})
```

### Report Lifecycle Hook Sequence

```mermaid
sequenceDiagram
    participant Suite
    participant RBS as ReportBeforeSuite
    participant RBE as ReportBeforeEach
    participant Spec as It
    participant RAE as ReportAfterEach
    participant RAS as ReportAfterSuite
    
    Suite->>RBS: Report (initial state)
    RBS->>RBS: Process initial report
    
    loop Each Spec
        Suite->>RBE: SpecReport (before spec)
        RBE->>RBE: Access spec metadata
        Suite->>Spec: Run spec
        Suite->>RAE: SpecReport (after spec)
        RAE->>RAE: Process spec results
    end
    
    Suite->>RAS: Report (final state)
    RAS->>RAS: Generate summary reports
```

### Accessing `CurrentSpecReport()`

The `CurrentSpecReport()` function retrieves the current spec's complete report object during execution:

```go
BeforeEach(func() {
    report := CurrentSpecReport()
    fmt.Printf("Running spec: %s\n", report.FullText())
    fmt.Printf("Labels: %v\n", report.Labels())
})
```

Fields available in `types.SpecReport` include:

- `LeafNodeText`: The `It` text.
- `ContainerHierarchyTexts`: Parent container texts.
- `State`: Pass/fail/pending status.
- `RunTime`: Duration.
- `ReportEntries`: Attached report entries (via `AddReportEntry`).
- `CapturedGinkgoWriterOutput`: Captured output during the spec.

*Sources: [vendor/github.com/onsi/ginkgo/v2/reporting_dsl.go:1-260](), [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:316-391]()*


---

## DSL Function Call Processing Flow

Understanding the internal flow helps fix test setup errors and write correct specs.

```mermaid
sequenceDiagram
    participant User as User code
    participant DSL as DSL function (e.g. Describe, It)
    participant Transformers as NodeArgsTransformer
    participant NewNode as internal.NewNode
    participant Suite as global Suite manager
    
    User->>DSL: Call (e.g. Describe())
    DSL->>Transformers: TransformNewNodeArgs()
    
    alt Transformers registered
        Transformers->>Transformers: Apply all transformers in LIFO order
        Transformers->>Transformers: Modify text, body, or args
    end
    
    Transformers->>NewNode: Create Node struct
    NewNode->>NewNode: Parse decorators, extract function body
    NewNode->>NewNode: Validate configuration (e.g. timeout with interruptible func)
    
    alt Validation fails
        NewNode->>User: Panic or fatal exit
    end
    
    NewNode->>DSL: Return wrapped Node
    DSL->>Suite: PushNode(Node)
    
    alt Container Node
        Suite->>Suite: Add to hierarchy tree
        Suite->>User: Execute container body closure to register children
    else
        Suite->>Suite: Register node only
    end
```

### Decorator Processing Order

When creating nodes, decorators are processed in the following order:

1. **Offset/CodeLocation**: Sets source location for error reporting.
2. **Node-Type Compatibility**: Ensures decorators are valid for the node type.
3. **Label and SemVer Deduplication**: Removes duplicates among labels and version constraints.
4. **Function Extraction**: Identifies the test/cleanup function body; validates interruptibility.
5. **Cross-Decorator Validation**: For example, ensures `Focus` and `Pending` aren't combined.

This guarantees consistent node construction with clear diagnostics.

*Sources: [vendor/github.com/onsi/ginkgo/v2/core_dsl.go:496-502](), [vendor/github.com/onsi/ginkgo/v2/internal/node.go:214-499](), [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:153-228]()*

---

# Summary

This page has explained the comprehensive Ginkgo DSL features used in the NVIDIA k8s-test-infra E2E and unit test suites:

- The hierarchical node types organizing tests.
- Setup and teardown hooks with execution ordering.
- Rich decorators controlling test isolation, timing, and filtering.
- Table-driven tests to efficiently run parameterized scenarios.
- Reporting and documentation helpers embedded in tests.
- The internal DSL function invocation and decorator processing flow.

These constructs enable the project to define expressive, maintainable, and reliable integration and unit tests that integrate smoothly with the Kubernetes test infrastructure and GPU simulation subsystems.


# Diagrams Bridging Natural Language to Code Entities

## 1. Mapping Natural Language Test Structure to Code Entities in tests/e2e/go

```mermaid
graph LR
    UserSpec["User Spec: 'Standalone Scenario'"]
    DescribeBlock["Describe('nvml-mock standalone scenario')"]
    BeforeEachHooks["BeforeEach hooks (setup logic)"]
    ItBlock["It('should report labels')"]
    TableDrivenTests["DescribeTable for failure Injection"]
    HarnessSetup["harness.Setup(ctx, ClusterName, kindConfig, builtImage)"]
    HelmInstall["installDemoChart(ctx, h, profile, gpuCount)"]

    UserSpec --> DescribeBlock
    DescribeBlock --> BeforeEachHooks
    DescribeBlock --> ItBlock
    DescribeBlock --> TableDrivenTests

    BeforeEachHooks -.-> HarnessSetup
    ItBlock -.-> HelmInstall
```

This summarises how natural language test steps map onto container nodes, hooks, and helper functions in Go code under `tests/e2e/go`.

*Sources: [tests/e2e/go/e2e_suite_test.go:52-62](), [tests/e2e/go/suite_helm.go:36-46](), [tests/e2e/README.md:116-131]()*


## 2. Linking Ginkgo DSL Constructs to Internal Node Types

```mermaid
graph TB
    DSLFunction["DSL Function call (e.g. Describe, It)"]
    TransformArgs["NodeArgsTransformer.TransformNewNodeArgs()"]
    InternalNode["internal.NewNode (ginkgo/internal)"]
    SuitePush["global.Suite.PushNode()"]
    ContainerNode["ContainerNode (Describe/Context)"]
    SubjectNode["SubjectNode (It/Specify)"]
    SuiteTree["Suite Tree structure"]
    
    DSLFunction --> TransformArgs
    TransformArgs --> InternalNode
    InternalNode --> SuitePush
    SuitePush --> SuiteTree
    
    SuiteTree -->|ContainerNode| ContainerNode
    SuiteTree -->|SubjectNode| SubjectNode
```

This diagram clarifies how DSL function calls translate into internal Ginkgo node structs organized into the test suite tree.

*Sources: [vendor/github.com/onsi/ginkgo/v2/core_dsl.go:496-502](), [vendor/github.com/onsi/ginkgo/v2/internal/node.go:1047-1078]()*

---

# References

- [vendor/github.com/onsi/ginkgo/v2/core_dsl.go](https://github.com/onsi/ginkgo/tree/v2)
- [vendor/github.com/onsi/ginkgo/v2/internal/node.go](https://github.com/onsi/ginkgo/tree/v2)
- [vendor/github.com/onsi/ginkgo/v2/table_dsl.go](https://github.com/onsi/ginkgo/tree/v2)
- [tests/e2e/go/e2e_suite_test.go](./tests/e2e/go/e2e_suite_test.go)
- [tests/e2e/go/suite_helm.go](./tests/e2e/go/suite_helm.go)
- [tests/e2e/README.md](./tests/e2e/README.md)

---

*End of page 5.2 - Test Structure and DSL.*

---

# Page: Configuration and Parallel Execution

# Configuration and Parallel Execution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/nvml-mock-e2e-go.yaml](.github/workflows/nvml-mock-e2e-go.yaml)
- [Makefile](Makefile)
- [README.md](README.md)
- [tests/e2e/README.md](tests/e2e/README.md)
- [tests/e2e/go/e2e_suite_test.go](tests/e2e/go/e2e_suite_test.go)
- [tests/e2e/go/framework/config/config.go](tests/e2e/go/framework/config/config.go)
- [tests/e2e/go/framework/harness/harness.go](tests/e2e/go/framework/harness/harness.go)
- [tests/e2e/go/suite_cluster.go](tests/e2e/go/suite_cluster.go)
- [tests/e2e/go/suite_helm.go](tests/e2e/go/suite_helm.go)
- [vendor/github.com/onsi/ginkgo/v2/ginkgo/run/run_command.go](vendor/github.com/onsi/ginkgo/v2/ginkgo/run/run_command.go)
- [vendor/github.com/onsi/ginkgo/v2/ginkgo/watch/watch_command.go](vendor/github.com/onsi/ginkgo/v2/ginkgo/watch/watch_command.go)
- [vendor/github.com/onsi/ginkgo/v2/internal/suite.go](vendor/github.com/onsi/ginkgo/v2/internal/suite.go)
- [vendor/github.com/onsi/ginkgo/v2/types/config.go](vendor/github.com/onsi/ginkgo/v2/types/config.go)
- [vendor/github.com/onsi/ginkgo/v2/types/errors.go](vendor/github.com/onsi/ginkgo/v2/types/errors.go)

</details>



This page documents the configuration and parallel execution facilities as used in the k8s-test-infra project’s end-to-end (E2E) testing harness. It explains the core Ginkgo configuration types (`SuiteConfig`, `ReporterConfig`), usage patterns, how parallelism and test randomization are configured, and the `SynchronizedBeforeSuite` pattern employed to efficiently share the single image build process across parallel processes.

For foundational knowledge about the Ginkgo framework and test structure, see the related wiki pages [Ginkgo Framework Overview](#5.1) and [Test Structure and DSL](#5.2). For output and reporting details, see [Test Reporting and Output](#5.4).

---

## Configuration Overview

The core configuration for Ginkgo test execution is represented by three main configuration structs:

- **SuiteConfig:** Controls test execution behaviors such as filtering, ordering, parallelism, timing, failure strategies, and randomization.
- **ReporterConfig:** Controls the output formatting, verbosity, and reporting formats (e.g., JSON, JUnit).
- **GoFlagsConfig:** Captures Go-specific build and runtime test flags like race detection and profiling.

These configurations are constructed and passed to the `RunSpecs()` function, which drives the test execution lifecycle.

```mermaid
graph TB
    RunSpecs["RunSpecs()"]
    
    subgraph "Configuration Types"
        SuiteConfig["SuiteConfig<br/>Test Execution Control"]
        ReporterConfig["ReporterConfig<br/>Output & Reporting"]
        GoFlagsConfig["GoFlagsConfig<br/>Go Build/Test Flags"]
    end
    
    RunSpecs --> SuiteConfig
    RunSpecs --> ReporterConfig
    RunSpecs --> GoFlagsConfig
```

Sources: [vendor/github.com/onsi/ginkgo/v2/types/config.go:18-122]()

---

## SuiteConfig: Controlling Test Execution

The heart of test execution configuration is the `SuiteConfig` struct, which provides comprehensive control over how specs are selected, ordered, executed, and how failures are handled.

### Core Fields and Meaning

| Field               | Type          | Purpose                                                                                                       | Default                 |
|---------------------|---------------|---------------------------------------------------------------------------------------------------------------|-------------------------|
| `RandomSeed`        | `int64`       | Seed controlling spec order randomization                                                                     | Current Unix timestamp  |
| `RandomizeAllSpecs` | `bool`        | Flag whether to randomize order of all specs (true) or only top-level containers (false)                     | `false`                 |
| `FailFast`          | `bool`        | Immediately stop suite on first failure                                                                        | `false`                 |
| `FailOnPending`     | `bool`        | Cause suite failure if any spec is pending                                                                     | `false`                 |
| `FlakeAttempts`     | `int`         | Number of times to retry a failing spec before failing                                                        | `0`                     |
| `Timeout`           | `time.Duration` | Maximum duration allowed for entire suite execution                                                               | 1 hour                  |
| `GracePeriod`       | `time.Duration` | Time allowed for cleanup after receiving an interrupt                                                          | 30 seconds              |
| `ParallelProcess`   | `int`         | 1-based index of this parallel test process                                                                     | 1 (serial)              |
| `ParallelTotal`     | `int`         | Total number of parallel processes running the suite                                                            | 1 (serial)              |

Randomization controls are used to reorder specs for improved coverage, with a time-based seed default.

### Filtering Mechanisms

`SuiteConfig` supports multiple filtering modes to select which specs run:

- **FocusStrings / SkipStrings:** Regex expressions matched to spec description text, ORed among multiple entries.
- **FocusFiles / SkipFiles:** File and line-based filtering to include or exclude specs by location.
- **LabelFilter:** A Boolean expression on spec labels supporting `!`, `&&`, `||`, grouping, and regex.
- **SemVerFilter:** Semantic version constraints filtering specs annotated by version.

Filtering combinatorics produce the final spec list to run.

### Timeout and Progress

Timeout-related fields control suite runtime limits and progress reporting:

- `Timeout`: Total allowed suite runtime
- `GracePeriod`: Time to wait after interrupt for cleanup
- `PollProgressAfter`: How long to wait before emitting progress reports for long-running specs
- `PollProgressInterval`: Interval at which progress reports are emitted once polling begins
- `OutputInterceptorMode`: Controls output capturing strategy in parallel runs (`dup`, `swap`, or `none`)

Sources: [vendor/github.com/onsi/ginkgo/v2/types/config.go:19-46,34-40](), [vendor/github.com/onsi/ginkgo/v2/types/config.go:297-310]()

---

## ReporterConfig: Output and Reporting Control

The `ReporterConfig` struct configures output verbosity, formatting, and report file generation:

### Verbosity Levels

Four verbosity levels are defined through the `VerbosityLevel` type:

```mermaid
graph LR
    Succinct["VerbosityLevelSuccinct<br/>Minimal output: failures + summary"]
    Normal["VerbosityLevelNormal<br/>Default output: progress + summary"]
    Verbose["VerbosityLevelVerbose<br/>Adds GinkgoWriter contents (-v)"]
    VeryVerbose["VerbosityLevelVeryVerbose<br/>All events including skips (+ -vv)"]
    
    Succinct --> Normal
    Normal --> Verbose
    Verbose --> VeryVerbose
```

Controlled by boolean flags (`Succinct`, `Verbose`, `VeryVerbose`) which are mutually exclusive.

### Report Formats and Display Options

| Field           | Description                               |
|-----------------|-------------------------------------------|
| `JSONReport`    | Output detailed JSON test report          |
| `GoJSONReport`  | Go test-compatible JSON report             |
| `JUnitReport`   | Output JUnit XML report                     |
| `TeamcityReport`| TeamCity-specific reporting format          |
| `NoColor`       | Disable colored console output              |
| `ShowNodeEvents`| Print spec enter/exit events in timeline   |
| `SilenceSkips`  | Suppress printing skipped tests            |
| `ForceNewlines` | Force newlines after each test output      |
| `GithubOutput`  | Format output for GitHub Actions            |
| `FullTrace`     | Print full failure stacktraces              |

Sources: [vendor/github.com/onsi/ginkgo/v2/types/config.go:87-104,341-376]()

---

## Parallel Test Execution

Ginkgo supports parallel execution by splitting the test suite across multiple processes, each running a subset of specs. Coordination is handled by a parallel server.

### Parallel Configuration Fields

| Field            | Purpose                                                                                         | Default |
|------------------|-------------------------------------------------------------------------------------------------|---------|
| `ParallelTotal`  | Total number of parallel worker processes                                                        | 1       |
| `ParallelProcess`| ID (1-indexed) of this worker process                                                           | 1       |
| `ParallelHost`   | Address of the orchestration server coordinating spec distribution                                | empty   |

### Parallel Execution Model

The CLI invokes multiple test binary processes, each with a distinct `ParallelProcess` ID. The server, located at `ParallelHost`, distributes specs such that:

- Each spec runs exactly once.
- Specs marked `Serial` run exclusively on a single process at a time.
- Specs inside `Ordered` containers execute serially in a linear order within the assigned process.
- Output is captured and replayed to avoid interleaving.

```mermaid
sequenceDiagram
    participant CLI as "Ginkgo CLI"
    participant Server as "Parallel Server @ ParallelHost"
    participant P1 as "Process 1 (ParallelProcess=1)"
    participant P2 as "Process 2 (ParallelProcess=2)"
    participant PN as "Process N (ParallelProcess=N)"
    
    CLI->>Server: Start/coordinate workers
    CLI->>P1: Launch test binary with --parallel.process=1
    CLI->>P2: Launch test binary with --parallel.process=2
    CLI->>PN: Launch test binary with --parallel.process=N
    
    P1->>Server: Connect and request specs
    P2->>Server: Connect and request specs
    PN->>Server: Connect and request specs
    
    Server->>P1: Assign spec subset 1
    Server->>P2: Assign spec subset 2
    Server->>PN: Assign spec subset N
    
    P1->>P1: Execute specs
    P2->>P2: Execute specs
    PN->>PN: Execute specs
    
    P1->>Server: Report results
    P2->>Server: Report results
    PN->>Server: Report results
    
    Server->>CLI: Aggregate results
    CLI->>CLI: Generate combined report files
```

Sources: [vendor/github.com/onsi/ginkgo/v2/types/config.go:42-47,331-338]()

### CLI Control of Parallelism

Users invoke parallel testing via CLI flags:

| CLI Flag           | Maps to Config Field         | Description                                    |
|--------------------|-----------------------------|------------------------------------------------|
| `-p` or `--parallel`| `CLIConfig.Parallel`         | Enable parallel execution with auto process count |
| `--procs=N` or `--nodes=N` | `CLIConfig.Procs`         | Manually specify N parallel worker processes      |

Internally, the CLI sets `SuiteConfig.ParallelTotal`, `SuiteConfig.ParallelProcess`, and `SuiteConfig.ParallelHost` for each worker.

The logic to compute default parallel process count is:

```go
func (g CLIConfig) ComputedProcs() int {
    if g.Procs > 0 {
        return g.Procs // user override
    }
    n := 1
    if g.Parallel {
        n = runtime.GOMAXPROCS(-1) // use all but one core if >4 cores
        if n > 4 {
            n = n - 1
        }
    }
    return n
}
```

Sources: [vendor/github.com/onsi/ginkgo/v2/types/config.go:157-170]()

---

## Single Image Build with `SynchronizedBeforeSuite`

In the k8s-test-infra E2E tests (`tests/e2e/go/e2e_suite_test.go`), the expensive step to build the `nvml-mock` Docker image is controlled via Ginkgo's `SynchronizedBeforeSuite` feature, which runs a setup step exactly once per parallel suite run and shares its result with all parallel processes.

This pattern avoids redundant image builds on each parallel runner process:

- **First Ginkgo process (#1):** Builds the image (`buildImage()`), returning the image reference.
- **Other parallel processes:** Receive the built image reference from the first process without rebuilding.

Example snippet:

```go
var _ = SynchronizedBeforeSuite(func() []byte {
    if config.SkipBuild() {
        return []byte(config.Image())
    }
    ctx, cancel := context.WithTimeout(context.Background(), 20*time.Minute)
    defer cancel()
    buildImage(ctx)
    return []byte(config.Image())
}, func(data []byte) {
    builtImage = string(data)
})
```

Here, `builtImage` is a package-level variable holding the shared image reference used in all tests.

Sources: [tests/e2e/go/e2e_suite_test.go:50-62]()

---

## Configuration Validation

Before test execution, Ginkgo runs `VetConfig()` to validate suite and reporter configuration:

- **Ensures** `ParallelTotal` ≥ 1.
- **Ensures** `1 ≤ ParallelProcess ≤ ParallelTotal`.
- **Validates** `ParallelHost` is set for parallel runs.
- **Disallows** dry-run mode with parallelity enabled.
- **Validates** correctness of `LabelFilter` expressions.
- **Checks** that verbosity flags are mutually exclusive.
- **Ensures** `OutputInterceptorMode` is valid (`dup`, `swap`, `none`).

Errors collected are surfaced as a list.

---

## Flag-Based Configuration Population

Ginkgo's flags populate the configuration structs via three main flag groups:

| Flag Group         | Config Populated       | Key Flags / Flags Example                       |
|--------------------|-----------------------|------------------------------------------------|
| SuiteConfigFlags    | `SuiteConfig`          | `--seed`, `--randomize-all`, `--fail-fast`, `--label-filter`, `--timeout`  |
| ParallelConfigFlags | `SuiteConfig` Parallel fields (internal) | `--parallel.process`, `--parallel.total`, `--parallel.host` (set via CLI) |
| ReporterConfigFlags | `ReporterConfig`       | `-v`, `-vv`, `--succinct`, `--json-report`, `--junit-report`, `--no-color` |
| GoBuildFlags & GoRunFlags | `GoFlagsConfig`     | `--race`, `--cover`, `--cpuprofile`, etc.             |

These flags are combined into a `GinkgoFlagSet` used by the test binary at startup to instantiate the configuration used by `RunSpecs`.

---

## Usage in k8s-test-infra E2E Tests

The Go E2E suite under `tests/e2e/go/e2e_suite_test.go` sets up:

- Environment from environment variables (`E2E_PROFILES`, `E2E_IMAGE`, etc.) via the `config` package.
- A shared Kind cluster with the desired kube context.
- Helm chart installation per GPU profile.
- Parallel execution configured as per Ginkgo CLI flags.
- Synchronization to build the `nvml-mock` image once with `SynchronizedBeforeSuite`.
- Collection of test diagnostics when tests fail.

These leverage the `SuiteConfig` and `ReporterConfig` during the run lifecycle.

---

# Diagrams

### 1. Mapping Natural Language Concepts to Code Entities for Configuration

```mermaid
graph LR
    SuiteConfig["SuiteConfig (types/config.go)"]
    ReporterConfig["ReporterConfig (types/config.go)"]
    GoFlagsConfig["GoFlagsConfig (types/config.go)"]
    
    RunSpecs["RunSpecs() (github.com/onsi/ginkgo/v2)"]
    BuildFlags["BuildTestSuiteFlagSet() (config.go)"]
    
    TestBinary["Test Binary main (_test.go)"]
    CLIFlags["Ginkgo CLI flags (-p, -v, etc.)"]
    
    TestBinary --> BuildFlags
    BuildFlags --> SuiteConfig
    BuildFlags --> ReporterConfig
    BuildFlags --> GoFlagsConfig
    SuiteConfig --> RunSpecs
    ReporterConfig --> RunSpecs
    GoFlagsConfig --> RunSpecs
```

### 2. Parallel Execution Architecture Entities

```mermaid
graph TB
    CLI["Ginkgo CLI with -p/--procs"]
    Server["Parallel Coordination Server (Ginkgo)"]
    
    P1["ParallelProcess=1"]
    P2["ParallelProcess=2"]
    PN["ParallelProcess=N"]
    
    CLI --> Server
    CLI --> P1
    CLI --> P2
    CLI --> PN
    
    P1 --> Server
    P2 --> Server
    PN --> Server
    
    Server --> SpecDistribution["Assign test specs"]
    P1 --> RunTests1["Run assigned specs"]
    P2 --> RunTests2["Run assigned specs"]
    PN --> RunTestsN["Run assigned specs"]
    
    P1 --> ReportResults["Report results"]
    P2 --> ReportResults
    PN --> ReportResults
    
    Server --> CLI
```

---

# Summary

- `SuiteConfig` is the key configuration struct that controls test filtering, ordering, randomization, parallelization, timeouts, and failure behavior.
- `ReporterConfig` controls verbosity and report output formats.
- Parallel testing is managed via process IDs and a coordination server set by the CLI options.
- The `SynchronizedBeforeSuite` feature is leveraged to perform one heavy setup (docker image build) once per parallel suite execution, sharing the result with all workers.
- Config flags populate these structs and are validated before running the test suite.
- This system enables scalable, reproducible, and diagnosable end-to-end testing of k8s-test-infra components.

---

**Sources:**  
- tests/e2e/go/e2e_suite_test.go:40-62  
- vendor/github.com/onsi/ginkgo/v2/types/config.go:18-122, 313-338, 393-476  
- vendor/github.com/onsi/ginkgo/v2/types/config.go:257-390  
- vendor/github.com/onsi/ginkgo/v2/types/config.go:47-55  
- tests/e2e/go/suite_helm.go:6-78  
- tests/e2e/go/framework/config/config.go:3-135  
- .github/workflows/nvml-mock-e2e-go.yaml:10-70 (for high-level parallelism context)

---

# Page: Test Reporting and Output

# Test Reporting and Output

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.golangci.yml](.golangci.yml)
- [go.mod](go.mod)
- [go.sum](go.sum)
- [tests/e2e/go/report_skips_test.go](tests/e2e/go/report_skips_test.go)
- [vendor/github.com/onsi/ginkgo/v2/CHANGELOG.md](vendor/github.com/onsi/ginkgo/v2/CHANGELOG.md)
- [vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go](vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go)
- [vendor/github.com/onsi/ginkgo/v2/types/version.go](vendor/github.com/onsi/ginkgo/v2/types/version.go)
- [vendor/k8s.io/apimachinery/pkg/api/validation/objectmeta.go](vendor/k8s.io/apimachinery/pkg/api/validation/objectmeta.go)
- [vendor/modules.txt](vendor/modules.txt)

</details>



**Purpose and Scope:**  
This document provides a detailed technical overview of the test reporting and output mechanisms employed in the k8s-test-infra project, which uses the Ginkgo BDD test framework. Key topics include console output formatting, generation of JSON and JUnit machine-readable reports, progress reporting during test execution, and the diagnostic artifact pattern implemented via the `collectOnFailure` mechanism.

---

## Reporter Configuration

The behavior of test output in Ginkgo is governed by the `types.ReporterConfig` structure. This configures both human-readable console output and automatic generation of various machine-readable report formats consumed by CI/CD systems and other tooling.

### ReporterConfig Fields and Control

The `ReporterConfig` controls:

- **Verbosity:** Level of detail in console output (e.g. succinct vs verbose).  
- **Console Formatting:** Flags such as color on/off, full stack trace, and showing node events.  
- **Machine-Readable Reports:** Enable output of JSON, JUnit XML, TeamCity service messages, and Go test JSON reports.  
- **Behavioral Flags:** Affect output suppression such as silencing skipped tests or adjusting for GitHub Actions logs.

```mermaid
graph TB
    subgraph "ReporterConfig Fields"
        VERBOSITY["Verbosity Control<br/>Succinct, Verbose, VeryVerbose"]
        FORMATTING["Console Formatting<br/>NoColor, FullTrace<br/>ShowNodeEvents, ForceNewlines"]
        REPORTS["Machine-Readable Reports<br/>JSONReport, JUnitReport<br/>TeamcityReport, GoJSONReport"]
        BEHAVIOR["Output Behavior<br/>SilenceSkips, GithubOutput"]
    end
    
    CONFIG[ReporterConfig] --> VERBOSITY
    CONFIG --> FORMATTING
    CONFIG --> REPORTS
    CONFIG --> BEHAVIOR
    
    VERBOSITY --> VL[VerbosityLevel]
    VL --> SUCCINCT[VerbosityLevelSuccinct]
    VL --> NORMAL[VerbosityLevelNormal]
    VL --> VERBOSE[VerbosityLevelVerbose]
    VL --> VVERBOSE[VerbosityLevelVeryVerbose]
```

**Sources:** [vendor/github.com/onsi/ginkgo/v2/types/config.go:87-102](), [vendor/github.com/onsi/ginkgo/v2/types/config.go:57-84]()

---

### Verbosity Levels

Ginkgo supports four verbosity levels impacting output:

| Level          | CLI Flag     | Description                      |
|----------------|--------------|--------------------------------|
| **Succinct**   | `--succinct` | Minimal output (test markers)  |
| **Normal**     | Default      | Typical output with summary     |
| **Verbose**    | `-v`         | Includes GinkgoWriter output   |
| **VeryVerbose**| `-vv`        | Max detail including skipped specs and node events |

The `Verbosity()` method on `ReporterConfig` returns the effective verbosity level used by reporters.

**Sources:** [vendor/github.com/onsi/ginkgo/v2/types/config.go:104-113]()

---

### Console Formatting Options

| Option          | CLI Flag           | Purpose                                          |
|-----------------|--------------------|-------------------------------------------------|
| `NoColor`       | `--no-color`       | Disable colored output                           |
| `FullTrace`     | `--trace`          | Show full stack traces on failures               |
| `ShowNodeEvents`| `--show-node-events`| Show node start/end/timeline events              |
| `GithubOutput`  | `--github-output`  | Format output for GitHub Actions workflows       |
| `SilenceSkips`  | `--silence-skips`  | Do not print skipped test information            |
| `ForceNewlines` | `--force-newlines` | Ensure newline after each test                    |

**Sources:** [vendor/github.com/onsi/ginkgo/v2/types/config.go:341-376]()

---

### Machine-Readable Reports Supported

Ginkgo can simultaneously generate multiple report types configured via the `ReporterConfig`:

```mermaid
graph LR
    RC[ReporterConfig] --> JSON["JSONReport (.json)"]
    RC --> GOJSON["GoJSONReport (.json)"]
    RC --> JUNIT["JUnitReport (.xml)"]
    RC --> TEAMCITY["TeamcityReport (service messages)"]
    
    JSON --> JSONFILE[JSON Report File]
    GOJSON --> GOJSONFILE[Go JSON Report File]
    JUNIT --> JUNITFILE[JUnit XML Report File]
    TEAMCITY --> TEAMCITYFILE[TeamCity Messages File]
    
    WGR["WillGenerateReport()"] --> CHECK{Any report configured?}
    CHECK -->|Yes| TRUE[true]
    CHECK -->|No| FALSE[false]
```

These reports contain comprehensive data about the entire suite:
- Suite metadata (e.g., path, description)
- All individual spec reports including outcome, failures, and timing
- Pre-run and final statistics
- Special suite failure reasons (if any)

**Sources:** [vendor/github.com/onsi/ginkgo/v2/reporting_dsl.go:210-259]()

---

## Console Output and DefaultReporter

### Overview of DefaultReporter

The `DefaultReporter` implements the primary console output interface for Ginkgo tests. It formats and prints suite start/end banners, progress updates, individual spec outcomes, and detailed failure information. It uses color and symbols encoding test state.

Key components of `DefaultReporter`:

- `conf`: ReporterConfig describing output mode and verbosity  
- `writer`: Output destination (usually `os.Stdout`)  
- `formatter`: Formatting helper for colors and text styles  
- `lock`: Mutex to serialize concurrent output  
- Emission state flags to track newlines, delimiters
- Unicode denoters: "•" or "+" for spec success and `↺` or "R" for retries

```mermaid
graph TB
    subgraph "DefaultReporter Structure"
        DR[DefaultReporter]
        CONF[conf: ReporterConfig]
        WRITER[writer: io.Writer]
        FORMATTER[formatter: Formatter]
        LOCK[lock: sync.Mutex]
        
        DR --> CONF
        DR --> WRITER
        DR --> FORMATTER
        DR --> LOCK
    end
    
    subgraph "Emission State"
        DR --> NEWLINE["lastCharWasNewline: bool"]
        DR --> DELIM["lastEmissionWasDelimiter: bool"]
    end
    
    subgraph "Display Elements"
        DR --> DENOTER["specDenoter: string<br/>'•' or '+'"]
        DR --> RETRY["retryDenoter: string<br/>'↺' or 'R'"]
    end
```

**Sources:** [vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go:22-64]()

---

### Reporter Lifecycle and Event Hooks

The reporter interface defines key lifecycle hooks connected to test execution events:

- `SuiteWillBegin(report)`: Called once before suite start; emits suite banner, config info, and seed.
- `WillRun(specReport)`: Invoked before each spec runs; optionally prints spec location.
- `DidRun(specReport)`: After spec finishes; emits pass/fail badge, stack traces, failures.
- `EmitReportEntry(entry)`: Handles user-added arbitrary report entries.
- `EmitProgressReport(progressReport)`: Displays current execution progress when triggered.
- `SuiteDidEnd(report)`: Suite complete; emits summary, failures, and statistics.

```mermaid
sequenceDiagram
    participant Suite
    participant Reporter as DefaultReporter
    participant Writer as io.Writer
    
    Note over Suite,Writer: Suite Start
    Suite->>Reporter: SuiteWillBegin(report)
    Reporter->>Writer: Emit banner and suite info
    
    Note over Suite,Writer: Spec Execution
    loop Each Spec
        Suite->>Reporter: WillRun(specReport)
        Reporter->>Writer: Emit spec details (location, etc)
        
        Suite->>Reporter: DidRun(specReport)
        Reporter->>Writer: Emit pass/fail, failures, timeline
        
        alt Spec has ReportEntries
            Reporter->>Writer: Emit Report Entries
        end
        
        alt Progress report requested
            Suite->>Reporter: EmitProgressReport(progressReport)
            Reporter->>Writer: Emit progress info
        end
    end
    
    Note over Suite,Writer: Suite End
    Suite->>Reporter: SuiteDidEnd(report)
    Reporter->>Writer: Emit suite summary and failures
```

**Sources:** [vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go:69-183](), [vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go:185-349]()

---

### Spec State Highlighting in Console Output

The default reporter uses colored symbols and labels to represent spec states:

| Spec State            | Color   | Symbol / Header | Description                |
|-----------------------|---------|-----------------|----------------------------|
| **Passed**            | Green   | `•`             | Spec passed successfully   |
| **Failed**            | Red     | `•[FAIL]`       | Spec failed                |
| **Pending**           | Yellow  | `P [PENDING]`   | Marked as pending          |
| **Skipped**           | Cyan    | `S [SKIPPED]`   | Explicitly skipped         |
| **Panicked**          | Magenta | `•[PANICKED!]`  | Panic occurred in spec     |
| **Timed Out**         | Orange  | `•[TIMEDOUT]`   | Spec timed out             |
| **Aborted**           | Coral   | `•[ABORTED]`    | Suite aborted during spec  |
| **Interrupted**       | Orange  | `•[INTERRUPTED]`| Spec interrupted           |

**Sources:** [vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go:351-376]()

---

### Emission Methods and Formatting

Internally, the reporter manages output emission with methods such as `emit()`, `emitBlock()`, and `emitDelimiter()`, which serialize access via a mutex and track output formatting state:

```mermaid
graph TB
    PUBLIC["Public emission methods<br/>emit(), emitBlock(), emitDelimiter()"]
    PRIVATE["_emit(s, isBlock, isDelimiter)"]
    LOCK["Mutex lock management"]
    WRITER["Call writer.Write()"]
    TRACKING["Track newline and delimiter state"]
    FORMATTING["Formatter helpers<br/>f(), fi(), cycleJoin()"]
    
    PUBLIC --> PRIVATE
    PRIVATE --> LOCK
    LOCK --> WRITER
    
    PRIVATE --> TRACKING
    PUBLIC --> FORMATTING
    FORMATTING --> FORMATTER[formatter.Formatter]
```

**Sources:** [vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go:680-725]()

---

## Machine-Readable Report Generation

When configured, Ginkgo generates multiple formats of machine-readable reports after suite completion. This is done via `ReportAfterSuite` nodes registered automatically if report paths are specified.

### Report Generation Workflow

```mermaid
graph TB
    CONFIG[ReporterConfig] --> CHECK{WillGenerateReport()?}
    
    CHECK -->|Yes| REGISTER[register ReportAfterSuite node]
    REGISTER --> NODE[ReportAfterSuite Node]
    
    subgraph "Report Generation Node Execution"
        NODE --> JSON_CHECK{JSONReport path set?}
        JSON_CHECK -->|Yes| JSON_GEN[Generate JSONReport]
        JSON_GEN --> JSON_FILE[Write JSON file]
        
        NODE --> GOJSON_CHECK{GoJSONReport path set?}
        GOJSON_CHECK -->|Yes| GOJSON_GEN[Generate Go JSON Report]
        GOJSON_GEN --> GOJSON_FILE[Write Go JSON file]
        
        NODE --> JUNIT_CHECK{JUnitReport path set?}
        JUNIT_CHECK -->|Yes| JUNIT_GEN[Generate JUnit Report]
        JUNIT_GEN --> JUNIT_FILE[Write JUnit XML]
        
        NODE --> TEAM_CHECK{TeamcityReport enabled?}
        TEAM_CHECK -->|Yes| TEAM_GEN[Generate TeamCity Messages]
        TEAM_GEN --> TEAM_FILE[Write TeamCity file]
    end
    
    SUITE[Suite Execution] --> COMPLETE[Suite Completed]
    COMPLETE --> NODE
```

**Sources:** [vendor/github.com/onsi/ginkgo/v2/reporting_dsl.go:210-259](), [vendor/github.com/onsi/ginkgo/v2/core_dsl.go:303-305]()

---

### Supported Formats Summary

| Format          | CLI Flag           | File Type          | Description                     |
|-----------------|--------------------|--------------------|---------------------------------|
| JSON            | `--json-report`    | Structured JSON    | Rich suite and specs data       |
| Go JSON         | `--gojson-report`  | Go test compatible | Compatible with `go test -json` |
| JUnit           | `--junit-report`   | XML                | Popular CI/CD test report       |
| TeamCity        | `--teamcity-report`| Service messages    | TeamCity integration            |

All report generators consume the full `types.Report` suite state object.

**Sources:** [vendor/github.com/onsi/ginkgo/v2/reporting_dsl.go:211-236]()

---

## Capturing and Managing Output

Test output is captured from multiple sources and managed carefully to provide consistent, user-friendly logs even under parallel test execution.

### Architecture of Output Capture

```mermaid
graph TB
    subgraph "Output Sources"
        TEST[Test Code] --> GW[GinkgoWriter]
        TEST --> STDOUT[os.Stdout]
        TEST --> STDERR[os.Stderr]
    end
    
    subgraph "Output Interception"
        STDOUT --> OI[OutputInterceptor]
        STDERR --> OI
        OI --> CAPTURED[CapturedStdOutErr Buffer]
    end
    
    subgraph "GinkgoWriter Modes"
        GW --> MODE{Writer Mode}
        MODE -->|Verbose| STREAM[Stream + Buffer]
        MODE -->|Normal| BUFFER[Buffer only]
        
        STREAM --> IMMEDIATE[Immediate Console Output]
        BUFFER --> BUFFERED[Buffered until failure]
    end
    
    subgraph "Report Assembly"
        GW --> GWOUTPUT[Captured GinkgoWriter output string]
        CAPTURED --> REPORT[Buffered stdout/stderr string]
        GWOUTPUT --> REPORT
    end
```

**Sources:** [vendor/github.com/onsi/ginkgo/v2/core_dsl.go:296-301](), [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:358-368]()

---

### Output Interceptor Modes

When running tests in parallel, Ginkgo intercepts standard output and error to avoid interleaving logs between tests. It supports three modes:

| Mode    | Flag Value               | Description                      |
|---------|--------------------------|---------------------------------|
| **dup** | `--output-interceptor-mode=dup`  | Unix-style duplication of file descriptors (default on Unix) |
| **swap**| `--output-interceptor-mode=swap` | Swaps `os.Stdout` and `os.Stderr` (default on Windows) |
| **none**| `--output-interceptor-mode=none` | No interception; direct output  |

**Sources:** [vendor/github.com/onsi/ginkgo/v2/types/config.go:308-309](), [vendor/github.com/onsi/ginkgo/v2/core_dsl.go:278-287]()

---

### Captured Output in Spec Reports

Each spec’s `SpecReport` records:

- `CapturedGinkgoWriterOutput` string — buffered GinkgoWriter logs  
- `CapturedStdOutErr` string — buffered raw stdout and stderr

Their display depends on verbosity and parallelism:

| Output Type            | When Shown in Console                                          |
|------------------------|---------------------------------------------------------------|
| GinkgoWriterOutput     | Always in verbose `-v`, or on failure in normal mode           |
| StdOutErr              | Inline (serial) or separate section (parallel for clarity)     |

```mermaid
graph LR
    SR[SpecReport] --> GWO["CapturedGinkgoWriterOutput"]
    SR --> CSO["CapturedStdOutErr"]
    
    GWO --> SHOW1{Show Condition}
    SHOW1 -->|Verbose| ALWAYS1[Always shown]
    SHOW1 -->|Normal| ONFAIL1[Shown only on failure]
    
    CSO --> SHOW2{Show Condition}
    SHOW2 -->|Parallel| SECTION[Separate Section]
    SHOW2 -->|Serial| INLINE[Inline with output]
```

**Sources:** [vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go:240-323](), [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:362-364]()

---

## Progress Reporting

Progress reporting provides real-time insight into currently executing specs, useful for diagnosing hangs or long tests.

### ProgressReport Structure

Fields in the `ProgressReport` struct include:

- Message string for user-friendly text  
- Leaf node text and location identifying the current leaf spec  
- Container hierarchy texts reported for context  
- Current node type, text, location for currently running node  
- Current step text and location for stepwise progress  
- Timing info for start times of spec/nodes/steps  
- Captured GinkgoWriter output so far  
- Goroutine info: currently running spec goroutine, highlighted user goroutines, and others  
- Additional user reports attached to progress

```mermaid
graph TB
    subgraph "ProgressReport Fields"
        PR[ProgressReport]
        
        PR --> MSG[Message]
        PR --> LEAF["LeafNodeText & Location"]
        PR --> CONTAINER["ContainerHierarchyTexts"]
        PR --> CURRENT["CurrentNodeType/Text/Location"]
        PR --> STEP["CurrentStepText/Location"]
        PR --> TIMING["Spec/Node/Step StartTimes"]
        PR --> OUTPUT["CapturedGinkgoWriterOutput"]
        PR --> GOROUTINES["Goroutines Info"]
        PR --> ADDITIONAL["AdditionalReports"]
    end
```

**Sources:** [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:393-412]()

---

### Progress Report Triggering

Progress reports can be:

- **Manually triggered** by runtime signals (SIGUSR1 or Ctrl+\), handled by `handleProgressSignal`  
- **Automatically generated** after a given timeout interval during slow specs via polling

Once triggered, progress report assembly involves acquiring a `selectiveLock` to serialize data collection, gathering goroutine stacks, and querying reporters registered for progress updates.

```mermaid
graph TB
    subgraph "Manual Trigger"
        USER[Signal received<br/>SIGUSR1 or Ctrl+\] --> HANDLER[handleProgressSignal]
        HANDLER --> GENERATE[generateProgressReport]
    end
    
    subgraph "Automatic Trigger"
        SPEC[Spec Execution] --> POLL{PollProgressAfter Timeout?}
        POLL -->|Yes| AUTOPOLL[Periodic Polling]
        AUTOPOLL --> GENERATE
        POLL -->|No| CONTINUE[Continue Execution]
    end
    
    subgraph "Report Generation"
        GENERATE --> LOCK[Acquire selectiveLock]
        LOCK --> COLLECT[Collect Runtime & Goroutine Info]
        COLLECT --> QUERY[Query Progress Reporters]
        QUERY --> BUILD[Assemble ProgressReport]
    end
    
    BUILD --> EMIT[emitProgressReport()]
    EMIT --> REPORTER[reporter.EmitProgressReport()]
    EMIT --> CLIENT{Parallel mode?}
    CLIENT -->|Yes| POST[Post event to other processes]
    CLIENT -->|No| DONE[End]
```

**Sources:** [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:414-432](), [vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go:479-488]()

---

### Progress Report Console Output Format

The `DefaultReporter` formats progress reports into a human-readable hierarchical layout:

- Optional message header  
- Container path + leaf spec displayed  
- Current node and timing details  
- Current step info  
- Show recent GinkgoWriter output lines  
- Show stack trace for spec's goroutine  
- Show additional user-supplied reports  
- List goroutine stack traces for highlighted and other goroutines

```mermaid
graph TB
    PR[ProgressReport] --> HEADER{Message present?}
    HEADER -->|Yes| MSG[Emit Message Header]
    HEADER -->|No| SKIP
    
    MSG --> SPEC["Current Spec: Container Hierarchy + Leaf Text"]
    PR --> NODE["Current Node: Type, Text, Location, Runtime"]
    PR --> STEP["Current Step: Text, Location, Runtime"]
    
    PR --> GW{Has GinkgoWriter Output?}
    GW -->|Yes| GWSECTION["Show recent lines of output"]
    
    GWSECTION --> SPECGOR["Show Spec goroutine stack trace"]
    
    PR --> ADDL{Additional Reports?}
    ADDL -->|Yes| ADDLSECTION["Show Additional Reports"]
    
    PR --> HIGHLIGHT["Show Highlighted Goroutines"]
    PR --> OTHER["Show Other Goroutines"]
```

**Sources:** [vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go:490-580]()

---

## Report Entries and Custom Reporting

### AddReportEntry API

Tests can attach arbitrary data during execution to the current spec report via `AddReportEntry(name string, ...args)`. Entries support:

- Naming and timestamping  
- Arbitrary associated values extracted from arguments  
- Visibility control to impact when they are shown on console  
- Location in the test code (caller info) and timeline placement

```mermaid
graph TB
    TEST[Test Code] --> ADD["AddReportEntry(name, args...)"]
    
    ADD --> PARSE[Parse Arguments]
    PARSE --> VALUE[Extract Value]
    PARSE --> VIS[Determine Visibility]
    PARSE --> LOC[Capture Caller Location]
    
    VALUE --> CREATE[Create ReportEntry struct]
    VIS --> CREATE
    LOC --> CREATE
    
    CREATE --> TIMELINE[Assign TimelineLocation]
    TIMELINE --> ENTRY[ReportEntry]
    
    ENTRY --> STORE[Append to SpecReport.ReportEntries]
    ENTRY --> EMIT[Emit immediately if reporter supports]
    
    subgraph "ReportEntry Fields"
        ENTRY --> NAME["Name"]
        ENTRY --> TIME["Timestamp"]
        ENTRY --> LOC2["Caller Location"]
        ENTRY --> VAL["Value Object"]
        ENTRY --> VISIBILITY["Visibility Level"]
        ENTRY --> TIMELINE["TimelineLocation"]
    end
```

**Sources:** [vendor/github.com/onsi/ginkgo/v2/reporting_dsl.go:78-100](), [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:380-390]()

---

### Visibility Levels for Report Entries

Three levels affect console output display:

| Visibility            | Constant                           | Console Display Behavior               |
|-----------------------|----------------------------------|-------------------------------------|
| **Always**            | `ReportEntryVisibilityAlways`    | Always shown                         |
| **FailureOrVerbose**  | `ReportEntryVisibilityFailureOrVerbose` | Shown on failure or with `-v`  |
| **Never**             | `ReportEntryVisibilityNever`     | Hidden from console, only in reports|

**Sources:** [vendor/github.com/onsi/ginkgo/v2/reporting_dsl.go:66-75](), [vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go:582-594]()

---

### Report Lifecycle Hooks

Ginkgo supports multiple report lifecycle hooks to allow injecting custom reporting or diagnostics:

- **Suite-level hooks:**
  - `ReportBeforeSuite(func(Report))` – before the suite starts  
  - `ReportAfterSuite(func(Report))` – after suite completion  

- **Spec-level hooks:**
  - `ReportBeforeEach(func(SpecContext, Report))` – before each spec runs (interruptible)  
  - `ReportAfterEach(func(SpecContext, SpecReport))` – after each spec runs (interruptible)  

These hooks receive either the overall `Report` or individual `SpecReport` objects and cannot contain nested Ginkgo test nodes but are suitable for:

- Producing files (test reports, logs, artifacts)  
- Interfacing with external systems (dashboards, databases)  
- Sending notifications  
- Capturing diagnostics and generating artifacts on failures  
- Cleaning up resources based on test outcome  

```mermaid
graph TB
    subgraph "Suite-Level Hooks"
        RBS[ReportBeforeSuite] --> BEFORE_SUITE[Called before suite starts]
        RAS[ReportAfterSuite] --> AFTER_SUITE[Called after suite ends]
        
        BEFORE_SUITE --> REPORT1[Receive initial Report]
        AFTER_SUITE --> REPORT2[Receive final Report]
    end
    
    subgraph "Spec-Level Hooks"
        RBE[ReportBeforeEach] --> BEFORE_SPEC[Called before each spec]
        RAE[ReportAfterEach] --> AFTER_SPEC[Called after each spec]
        
        BEFORE_SPEC --> SREPORT1[Receive SpecReport before spec runs]
        AFTER_SPEC --> SREPORT2[Receive SpecReport after spec runs]
    end
    
    subgraph "Hook Function Signatures"
        FUNC1["func(Report)"] --> NON_INTERRUPT1[Non-Interruptible]
        FUNC2["func(SpecContext, Report)"] --> INTERRUPTABLE1[Interruptible]
        FUNC3["func(SpecReport)"] --> NON_INTERRUPT2[Non-Interruptible]
        FUNC4["func(SpecContext, SpecReport)"] --> INTERRUPTABLE2[Interruptible]
    end
```

**Sources:** [vendor/github.com/onsi/ginkgo/v2/reporting_dsl.go:103-208]()

---

## The `collectOnFailure` Diagnostic Artifact Pattern

Within the broader E2E test infrastructure (covered in detail in [10.1. E2E Harness Framework]), the `collectOnFailure` pattern is used to automatically capture diagnostic artifacts when a test spec fails.

- When a test fails, registered collectors gather logs, Kubernetes debug files, or system snapshots.
- These artifacts are stored in a temporary directory designated in the test harness.
- The collected diagnostics provide rich debugging context for CI logs and local investigation.

The pattern integrates with the `ReportAfterEach` hook or equivalent to conditionally trigger artifact capture only on failures, minimizing overhead while maximizing insight on flaky or failing specs.

---

# Summary Diagrams Linking Natural Language and Code

### Diagram 1: Ginkgo Reporting Subsystems and Code Entities

```mermaid
graph LR
    A["User Test Code"] -->|Calls| B[Ginkgo Framework]
    B -->|Uses| C[ReportingConfig(types.ReporterConfig)]
    B -->|Invokes| D[DefaultReporter (default_reporter.go)]
    B -->|Generates| E[SpecReport / Report (types)]
    D -->|Writes| F[Console Output (io.Writer)]
    D -->|Calls| G[Formatter (formatter.Formatter)]
    B -->|Emits| H[Machine-Readable Reports]
    H --> I[JSON Report]
    H --> J[JUnit Report]
    H --> K[GoJSON Report]
    H --> L[TeamCity Report]
    
    style C fill:#f9f,stroke:#333,stroke-width:1px
    style D fill:#bbf,stroke:#333,stroke-width:1px
    style E fill:#bfb,stroke:#333,stroke-width:1px
    style H fill:#fbb,stroke:#333,stroke-width:1px
```

---

### Diagram 2: Reporting Output Flow and Diagnostic Collection

```mermaid
sequenceDiagram
    participant Test as Test Code
    participant G as Ginkgo Core
    participant DR as DefaultReporter
    participant FS as Filesystem (Reports/Artifacts)
    
    Test->>G: Run Test Spec
    G->>DR: WillRun(specReport)
    DR->>Console: Emit pre-run info
    G->>Test: Execute Spec
    alt Spec Fails
        G->>DR: DidRun(specReport failure)
        DR->>Console: Emit failure details
        G->>FS: Trigger collectOnFailure artifacts
    else Spec Passes
        G->>DR: DidRun(specReport pass)
        DR->>Console: Emit pass marker
    end
    G->>DR: SuiteDidEnd(finalReport)
    DR->>Console: Emit suite summary
    DR->>FS: Write machine-readable reports
```

---

This page encompasses all fundamental aspects of test reporting and output employed in the k8s-test-infra codebase leveraging Ginkgo. It covers how console output is formatted and controlled, how multiple default and machine-readable reports are generated, how live progress reporting functions, and the ergonomic diagnostic artifact collection pattern used on failures. Understanding these details is critical for extending, debugging, or customizing test reporting behavior in this project.

**Sources:**  
- [vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go:22-725]()  
- [vendor/github.com/onsi/ginkgo/v2/types/config.go:57-113, 87-102, 341-376]()  
- [vendor/github.com/onsi/ginkgo/v2/reporting_dsl.go:14-259]()  
- [vendor/github.com/onsi/ginkgo/v2/core_dsl.go:278-305]()  
- [vendor/github.com/onsi/ginkgo/v2/internal/suite.go:284-368, 393-432]()  
- [tests/e2e/go/report_skips_test.go:16-57]()

---

# Page: Kubernetes APIs and Integration

# Kubernetes APIs and Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [pkg/diagnostics/collector.go](pkg/diagnostics/collector.go)
- [pkg/diagnostics/extensions.go](pkg/diagnostics/extensions.go)
- [pkg/diagnostics/kubernetes.go](pkg/diagnostics/kubernetes.go)
- [pkg/diagnostics/options.go](pkg/diagnostics/options.go)
- [pkg/kubernetes/kubernetes.go](pkg/kubernetes/kubernetes.go)
- [vendor/k8s.io/api/resource/v1alpha3/generated.proto](vendor/k8s.io/api/resource/v1alpha3/generated.proto)
- [vendor/k8s.io/api/resource/v1alpha3/types.go](vendor/k8s.io/api/resource/v1alpha3/types.go)
- [vendor/k8s.io/api/resource/v1alpha3/types_swagger_doc_generated.go](vendor/k8s.io/api/resource/v1alpha3/types_swagger_doc_generated.go)
- [vendor/k8s.io/api/resource/v1beta1/generated.proto](vendor/k8s.io/api/resource/v1beta1/generated.proto)
- [vendor/k8s.io/api/resource/v1beta1/types.go](vendor/k8s.io/api/resource/v1beta1/types.go)
- [vendor/k8s.io/api/resource/v1beta1/types_swagger_doc_generated.go](vendor/k8s.io/api/resource/v1beta1/types_swagger_doc_generated.go)

</details>



This document outlines how the **k8s-test-infra** project interacts with Kubernetes core APIs and specialized Kubernetes Custom Resource Definitions (CRDs). The repository leverages `k8s.io/client-go` to perform CRUD operations, watches, and server-side apply with the K8s API server. Additionally, it integrates with custom APIs for **Node Feature Discovery (NFD)** and **Dynamic Resource Allocation (DRA)**, which are essential to simulate and test GPU device management and node hardware labeling in Kubernetes clusters.

For implementation specifics of these API operations and code usage patterns, each of these topics is covered in corresponding child wiki pages:

- For Kubernetes API operations using client-go, see [Kubernetes Client-Go Operations](#6.1)
- For Node Feature Discovery API and CRDs, see [Node Feature Discovery (NFD) API](#6.2)
- For Dynamic Resource Allocation and device resource APIs, see [Dynamic Resource Allocation (DRA) API](#6.3)
- For TLS certificate generation utilities used in tests, see [Certificate Utilities](#6.4)
- For YAML and JSON manifest loading and decoding helpers, see [YAML and JSON Manifest Processing](#6.5)

---

## Kubernetes Client Dependencies

The project depends on several key Kubernetes client libraries for API interactions:

| Dependency | Purpose |
|------------|---------|
| `k8s.io/client-go` | Core Kubernetes Go client library—used for CRUD, watches, and more |
| `k8s.io/api` | Kubernetes resource type definitions |
| `k8s.io/apimachinery` | Common machinery such as metadata, runtime, and JSON/YAML handling |
| `k8s.io/apiextensions-apiserver` | Support for Custom Resource Definitions |
| `sigs.k8s.io/node-feature-discovery` | Clientsets and API types for NFD |
| `sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1` | NFD v1alpha1 API versions |

These dependencies ensure typed and efficient interfacing with Kubernetes core and custom APIs.

**Sources:**  
[`pkg/kubernetes/kubernetes.go:18-36`](pkg/kubernetes/kubernetes.go)  
[`pkg/diagnostics/collector.go:20-32`](pkg/diagnostics/collector.go)  

---

## Kubernetes Client-Go Operations

The project uses `k8s.io/client-go` as the primary means for Kubernetes API access. This includes:

- Creating typed clients (`kubernetes.Clientset`) connected to the cluster
- Performing CRUD operations on core resources like Nodes, Pods, Deployments
- Monitoring changes using watches and informers for real-time updates
- Using server-side apply for declarative resource management

### High-Level Client-Go Client Creation Flow

```mermaid
graph TB
    RestConfig["rest.Config<br/>Connection parameters"]
    ClientSet["kubernetes.Clientset<br/>Typed clientset"]
    DynamicClient["dynamic.Interface<br/>Unstructured client"]
    CoreAPI["CoreV1() interface<br/>Services, Pods, Nodes"]
    AppsAPI["AppsV1() interface<br/>Deployments, DaemonSets"]
    CustomAPI["Custom CRD clientsets<br/>NFD, DRA"]
    
    RestConfig --> ClientSet
    RestConfig --> DynamicClient
    ClientSet --> CoreAPI
    ClientSet --> AppsAPI
    ClientSet --> CustomAPI
```

- The `Clientset` is the central interface for typed Kubernetes resource clients.
- Specialized clients exist for CRDs like NFD (`nfdclient.Clientset`) and others.
- The dynamic client allows unstructured manipulation when type is not available or needed.

### CRUD and Watches

Client-go supports all standard Kubernetes operations: Create, Get, List, Update, Patch, Delete, and Watch.

Watching resources establishes a continuous stream from Kubernetes informing the client about resource state changes:

```mermaid
sequenceDiagram
    participant TestCode
    participant Clientgo
    participant APIServer
    participant Watcher
    
    TestCode->>Clientgo: Watch(ctx, listOptions)
    Clientgo->>APIServer: GET /watch/...
    APIServer-->>Watcher: stream opened
    
    loop event loop
        APIServer->>Watcher: ADDED event
        Watcher->>Clientgo: decoded event
        Clientgo->>TestCode: event channel receives ADDED
        
        APIServer->>Watcher: MODIFIED event
        Watcher->>Clientgo: decoded event
        Clientgo->>TestCode: event channel receives MODIFIED
        
        APIServer->>Watcher: DELETED event
        Watcher->>Clientgo: decoded event
        Clientgo->>TestCode: event channel receives DELETED
    end
    
    TestCode->>Clientgo: Close watch
    Clientgo->>APIServer: close connection
```

### Server-Side Apply

Server-side apply allows declarative configuration with conflict detection and merging. The client constructs `ApplyConfiguration` typed objects and applies them with a field manager. The Kubernetes API server merges the changes, preserving field ownership.

```mermaid
graph LR
    AC[ApplyConfiguration typed object]
    FieldMgr[FieldManager string]
    Force[Force Apply boolean]
    HTTPPatch[PATCH request to API server<br/>with content-type apply-patch+yaml]
    Merge[Server-side merge]
    Result[Updated resource or conflict error]
    
    AC --> HTTPPatch
    FieldMgr --> HTTPPatch
    Force --> HTTPPatch
    HTTPPatch --> Merge
    Merge --> Result
```

---

## Node Feature Discovery (NFD) API

**Node Feature Discovery** is a Kubernetes addon aimed at detecting detailed hardware and system features for nodes and labeling them accordingly.

### NFD CRDs Used

The project uses the following main NFD custom resources defined in the `nfd/v1alpha1` API group:

```mermaid
classDiagram
    class NodeFeature {
        +Spec Features (flags, attributes, instances)
        +Labels map[string]string
    }
    class NodeFeatureRule {
        +Spec: Rules (label, annotation, taint, extended resource injection)
    }
    class NodeFeatureGroup {
        +Spec: Grouping rules for nodes
        +Status: List of matching nodes
    }
    NodeFeature --> Features
```

- `NodeFeature` objects represent discovered features per node.
- `NodeFeatureRule` objects define how to translate features into node labels, annotations, and taints.
- `NodeFeatureGroup` allows grouping nodes dynamically based on features.

### Feature Matching

NFD supports expressive feature matching using `FeatureMatcher` which compares feature sets against complex logical expressions and operators like In, NotIn, Exists, Gt, Lt, etc.

Rules use these matchers to decide whether to apply certain labels or taints.

---

## Dynamic Resource Allocation (DRA) API

**Dynamic Resource Allocation** manages specialized device resources, exposing them via Kubernetes APIs for scheduling and allocation.

### Core DRA Resources

```mermaid
classDiagram
    class ResourceSlice {
        +Spec.Driver string
        +Spec.Pool ResourcePool (name, generation, count)
        +Spec.Devices []Device
    }
    class ResourceClaim {
        +Spec and Status
        +Status.Allocation AllocationResult
    }
    class DeviceClass {
        +Selectors []DeviceSelector (e.g., CEL expressions)
        +TaintRules
    }
```

- `ResourceSlice`: Represents a portion of device resources, managed by a driver, tied to nodes or node selectors.
- `ResourceClaim`: Requests and records allocation of devices.
- `DeviceClass`: Defines collections of device configurations and selectors.

### Device and Allocation Details

Devices provide attributes and capacities to allow flexible matching and allocation, often expressed through CEL expressions:

```mermaid
graph TB
    subgraph "Device Selection"
        CELExpr[CELExpression for device selection]
        Device["device driver, attributes, capacity"]
        CELRuntime["Evaluator with max cost limit"]
    end
    CELExpr --> CELRuntime
    Device --> CELRuntime
    CELRuntime --> Decision{"Matches?"}
    Decision -->|Yes| Allocate
    Decision -->|No| Skip
```

The `AllocationResult` in `ResourceClaim.Status` records allocated devices with driver, pool, device name, and condition statuses.

### Device Taints in DRA v1alpha3

DRA introduces device taints similar to node taints to indicate device conditions or scheduling constraints. The `DeviceTaintRule` CRD adds taints to devices matching a selector without modifying `ResourceSlice` objects directly.

---

## Certificate Utilities

The project includes test utilities for generating **self-signed TLS certificates** leveraging `k8s.io/client-go/util/cert`.

### Certificate Generation Flow

```mermaid
graph TB
    NewCA["NewSelfSignedCACert()"]
    CACert["x509 CA Certificate"]
    CAKey["crypto.Signer private key"]
    NewServerCert["GenerateSelfSignedCertKey()"]
    ServerCert["x509 TLS Certificate signed by CA"]
    ServerKey["Private Key"]
    
    NewCA --> CACert
    CACert --> NewServerCert
    CAKey --> NewServerCert
    NewServerCert --> ServerCert
    NewServerCert --> ServerKey
```

- Generate a CA certificate first (10 years validity by default)
- Generate a server cert signed by that CA (with alternate IPs and DNS names)
- Output PEM encoded certificate and key arrays for use in TLS components in tests

---

## YAML and JSON Manifest Processing

The project uses the `k8s.io/apimachinery/pkg/util/yaml` package to load and decode Kubernetes manifests which can be YAML or JSON.

### YAMLOrJSONDecoder Processing

```mermaid
graph TB
    StreamInput["io.Reader input stream"]
    BufferedReader["buffered stream reader"]
    JSONGuess["GuessJSONStream()"]
    IsJSON{"Is first non-whitespace char '{'?"}
    JSONDecoder["json.Decoder"]
    YAMLToJSONDecoder["YAMLToJSONDecoder"]
    Decoder["YAMLOrJSONDecoder"]
    DecodeCall["Decode() into Go object"]
    
    StreamInput --> BufferedReader
    BufferedReader --> JSONGuess
    JSONGuess --> IsJSON
    IsJSON -->|Yes| JSONDecoder
    IsJSON -->|No| YAMLToJSONDecoder
    JSONDecoder --> Decoder
    YAMLToJSONDecoder --> Decoder
    Decoder --> DecodeCall
```

- The decoder autodetects JSON vs YAML input.
- It supports multi-document YAML streams separated by `---`.
- Implements streaming decode into Kubernetes runtime objects.

The buffer size parameter influences detection accuracy.

---

## Summary: How These Pieces Connect

```mermaid
graph TD
    subgraph Kubernetes APIs
        ClientGo["client-go clientset"]
        NFDClient["NFD clientset"]
        DRAClient["DRA clientsets"]
        CertUtil["Cert generation utils"]
        YAMLUtil["Manifest processing utils"]
    end
    
    subgraph k8s-test-infra Usage
        E2ETests["E2E Test Harness"]
        NvmlMock["nvml-mock GPU simulation"]
        Diagnostics["Diagnostic Collector"]
        ManifestLoader["Manifest loader & applier"]
    end
    
    ClientGo --> E2ETests
    NFDClient --> E2ETests
    DRAClient --> E2ETests
    CertUtil --> E2ETests
    YAMLUtil --> ManifestLoader
    
    ManifestLoader --> ClientGo
    Diagnostics --> ClientGo
    Diagnostics --> NFDClient
```

- The test harness combines the Kubernetes client libraries to create, watch, and validate resources.
- NVML-mock interacts with DRA and NFD APIs to simulate GPUs and their discovery.
- Certificate utilities enable secure communication testing.
- YAML/JSON manifest utilities load test specifications, CRDs, and other manifests.

---

This high-level overview introduces the Kubernetes APIs and integrations used in the k8s-test-infra project. For detailed information on each part, consult the child pages:

- [Kubernetes Client-Go Operations](#6.1)
- [Node Feature Discovery (NFD) API](#6.2)
- [Dynamic Resource Allocation (DRA) API](#6.3)
- [Certificate Utilities](#6.4)
- [YAML and JSON Manifest Processing](#6.5)

---

**Sources:**  
- [`pkg/kubernetes/kubernetes.go:18-168`](pkg/kubernetes/kubernetes.go)  
- [`pkg/diagnostics/collector.go:20-114`](pkg/diagnostics/collector.go)  
- [`pkg/diagnostics/extensions.go:18-60`](pkg/diagnostics/extensions.go)  
- [`pkg/diagnostics/kubernetes.go:18-170`](pkg/diagnostics/kubernetes.go)  
- Kubernetes API types and proto files from vendor directory for DRA and NFD APIs.

---

# Page: Kubernetes Client-Go Operations

# Kubernetes Client-Go Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [pkg/diagnostics/collector.go](pkg/diagnostics/collector.go)
- [pkg/diagnostics/extensions.go](pkg/diagnostics/extensions.go)
- [pkg/diagnostics/kubernetes.go](pkg/diagnostics/kubernetes.go)
- [pkg/diagnostics/options.go](pkg/diagnostics/options.go)
- [pkg/kubernetes/kubernetes.go](pkg/kubernetes/kubernetes.go)
- [vendor/k8s.io/api/core/v1/generated.proto](vendor/k8s.io/api/core/v1/generated.proto)
- [vendor/k8s.io/api/core/v1/types.go](vendor/k8s.io/api/core/v1/types.go)
- [vendor/k8s.io/api/core/v1/types_swagger_doc_generated.go](vendor/k8s.io/api/core/v1/types_swagger_doc_generated.go)
- [vendor/k8s.io/client-go/applyconfigurations/internal/internal.go](vendor/k8s.io/client-go/applyconfigurations/internal/internal.go)

</details>



## Purpose and Scope

This page documents how the k8s-test-infra project uses the `k8s.io/client-go` library to interact with Kubernetes API servers. It covers standard CRUD operations, resource watching, server-side apply, and diagnostic collection patterns. This documentation focuses on the operational patterns used in the E2E harness and diagnostic collector for programmatic cluster interactions.

For information about Node Feature Discovery and Dynamic Resource Allocation custom resource APIs, see [Node Feature Discovery (NFD) API](6.2) and [Dynamic Resource Allocation (DRA) API](6.3).

## Client-Go Architecture

The project utilizes `k8s.io/client-go` as its primary interface for cluster management. In addition to standard Kubernetes resources, it integrates specialized clients for Node Feature Discovery (NFD) as seen in diagnostic and cleanup operations [pkg/kubernetes/kubernetes.go:34-35]().

### Client-Go Component Structure

```mermaid
graph TB
    subgraph "Client-Go Library"
        CLIENTSET["kubernetes.Clientset<br/>Main entry point"]
        REST["rest.Config<br/>Connection configuration"]
        
        subgraph "Typed Clients"
            COREV1["typed/core/v1<br/>Nodes, Pods, Namespaces"]
            APPSV1["typed/apps/v1<br/>Deployments, DaemonSets"]
            BATCHV1["typed/batch/v1<br/>Jobs"]
        end
        
        subgraph "External Clients"
            NFDCLIENT["nfdclient.Clientset<br/>NodeFeature Discovery"]
        end
    end
    
    REST --> CLIENTSET
    CLIENTSET --> COREV1
    CLIENTSET --> APPSV1
    CLIENTSET --> BATCHV1
    
    NFDCLIENT -.->|"Used for"| NFD_OPS["NodeFeature/Rule Ops"]
```

**Sources:** [pkg/kubernetes/kubernetes.go:29-36](), [pkg/diagnostics/options.go:21-24]()

## CRUD Operations

### Resource Interface Pattern

The codebase abstracts common CRUD operations into specialized functions for cluster maintenance and testing. A key example is the filtering of nodes to identify non-control-plane targets using the `CoreV1().Nodes().List` operation [pkg/kubernetes/kubernetes.go:39-40]().

### Common CRUD Operations in k8s-test-infra

| Operation | Implementation | Description |
|-----------|----------------|-------------|
| **List** | `cli.CoreV1().Nodes().List(ctx, metav1.ListOptions{})` | Retrieves all nodes for filtering or iteration [pkg/kubernetes/kubernetes.go:40]() |
| **Get** | `cs.CoreV1().Nodes().Get(ctx, nodeName, metav1.GetOptions{})` | Retrieves a specific node to modify its metadata [pkg/kubernetes/kubernetes.go:79]() |
| **Update** | `cs.CoreV1().Nodes().Update(ctx, node, metav1.UpdateOptions{})` | Persists changes to node labels, annotations, or taints [pkg/kubernetes/kubernetes.go:147]() |
| **UpdateStatus** | `cs.CoreV1().Nodes().UpdateStatus(ctx, node, metav1.UpdateOptions{})` | Specifically used to clear extended resources [pkg/kubernetes/kubernetes.go:140]() |
| **Delete** | `cli.NfdV1alpha1().NodeFeatures(ns).Delete(ctx, name, opts)` | Removes custom resources during test cleanup [pkg/kubernetes/kubernetes.go:187]() |

**Sources:** [pkg/kubernetes/kubernetes.go:39-217]()

### Node Metadata Cleanup Pattern

The `CleanupNode` function demonstrates a complex read-modify-write pattern using `client-go`. It iterates through labels, annotations, and taints, removing those associated with NFD [pkg/kubernetes/kubernetes.go:76-152]().

```mermaid
sequenceDiagram
    participant App as Cleanup Logic
    participant K8s as Kubernetes API
    
    App->>K8s: Get Node Object
    K8s-->>App: Node Spec/Status
    App->>App: Identify NFD Labels/Annotations/Taints
    App->>App: Identify NFD Extended Resources
    
    alt Status Changes Detected
        App->>K8s: UpdateStatus (Clear Capacity/Allocatable)
    end
    
    alt Metadata Changes Detected
        App->>K8s: Update (Clear Labels/Annotations/Taints)
    end
```

**Sources:** [pkg/kubernetes/kubernetes.go:76-152]()

## Diagnostic Collection Operations

The `diagnostics` package uses `client-go` to export cluster state to YAML files during test failures. It implements a `Collector` interface where each implementation targets a specific API resource [pkg/diagnostics/collector.go:34-36]().

### Diagnostic Collector Mapping

| Collector Name | Code Entity | API Call Site |
|----------------|-------------|---------------|
| `nodes` | `diagnostics.nodes` | `c.Clientset.CoreV1().Nodes().List()` [pkg/diagnostics/kubernetes.go:55]() |
| `pods` | `diagnostics.pods` | `c.Clientset.CoreV1().Pods(ns).List()` [pkg/diagnostics/kubernetes.go:107]() |
| `daemonsets` | `diagnostics.daemonsets` | `c.Clientset.AppsV1().DaemonSets(ns).List()` [pkg/diagnostics/kubernetes.go:81]() |
| `jobs` | `diagnostics.jobs` | `c.Clientset.BatchV1().Jobs(ns).List()` [pkg/diagnostics/kubernetes.go:125]() |
| `nodeFeature` | `diagnostics.nodeFeatures` | `c.NfdClient.NfdV1alpha1().NodeFeatures(ns).List()` [pkg/diagnostics/extensions.go:36]() |

**Sources:** [pkg/diagnostics/kubernetes.go:30-135](), [pkg/diagnostics/extensions.go:27-59]()

### Log Streaming

Diagnostic collection also involves streaming logs via the `GetLogs` request, which returns a stream that is scanned and written to the artifact directory [pkg/diagnostics/kubernetes.go:149-163]().

```mermaid
graph LR
    subgraph "Diagnostic Flow"
        CLIENT["Clientset.CoreV1().Pods()"]
        REQ["GetLogs(name, opts)"]
        STREAM["req.Stream(ctx)"]
        SCAN["bufio.Scanner"]
        FILE["os.Create(pod.log)"]
        
        CLIENT --> REQ
        REQ --> STREAM
        STREAM --> SCAN
        SCAN --> FILE
    end
```

**Sources:** [pkg/diagnostics/kubernetes.go:142-169]()

## Server-Side Apply and Watching

While the diagnostic collector focuses on `List` and `Get` operations, the E2E harness utilizes `client-go` for resource lifecycle management.

### Resource Deletion Watch

The `WaitForDeletion` utility implements a polling pattern that effectively mimics a watch for resource removal. It repeatedly executes a check function until it encounters an `IsNotFound` error [pkg/kubernetes/kubernetes.go:221-225]().

### Apply Configurations

The project includes vendored support for server-side apply configurations, allowing declarative updates to complex resources like `MutatingWebhookConfiguration` or `Pod` objects [vendor/k8s.io/client-go/applyconfigurations/internal/internal.go:245-255](). This is primarily used for infrastructure setup during cluster initialization.

**Sources:** [vendor/k8s.io/client-go/applyconfigurations/internal/internal.go:41-245]()

## Error Handling Patterns

The codebase distinguishes between transient errors and terminal states using `k8s.io/apimachinery/pkg/api/errors`:

1.  **NotFound Suppression**: During cleanup, `IsNotFound` errors are explicitly ignored to ensure idempotency [pkg/kubernetes/kubernetes.go:178-181]().
2.  **Retry Loops**: Operations like node metadata cleanup are wrapped in retry loops (5 attempts with 100ms backoff) to handle potential conflicts during parallel test execution [pkg/kubernetes/kubernetes.go:160-165]().

**Sources:** [pkg/kubernetes/kubernetes.go:160-188]()

---

# Page: Node Feature Discovery (NFD) API

# Node Feature Discovery (NFD) API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tests/e2e/go/scenario_nfd_test.go](tests/e2e/go/scenario_nfd_test.go)
- [vendor/sigs.k8s.io/node-feature-discovery/api/generated/clientset/versioned/clientset.go](vendor/sigs.k8s.io/node-feature-discovery/api/generated/clientset/versioned/clientset.go)
- [vendor/sigs.k8s.io/node-feature-discovery/api/generated/clientset/versioned/scheme/doc.go](vendor/sigs.k8s.io/node-feature-discovery/api/generated/clientset/versioned/scheme/doc.go)
- [vendor/sigs.k8s.io/node-feature-discovery/api/generated/clientset/versioned/scheme/register.go](vendor/sigs.k8s.io/node-feature-discovery/api/generated/clientset/versioned/scheme/register.go)
- [vendor/sigs.k8s.io/node-feature-discovery/api/generated/clientset/versioned/typed/nfd/v1alpha1/doc.go](vendor/sigs.k8s.io/node-feature-discovery/api/generated/clientset/versioned/typed/nfd/v1alpha1/doc.go)
- [vendor/sigs.k8s.io/node-feature-discovery/api/generated/clientset/versioned/typed/nfd/v1alpha1/generated_expansion.go](vendor/sigs.k8s.io/node-feature-discovery/api/generated/clientset/versioned/typed/nfd/v1alpha1/generated_expansion.go)
- [vendor/sigs.k8s.io/node-feature-discovery/api/generated/clientset/versioned/typed/nfd/v1alpha1/nfd_client.go](vendor/sigs.k8s.io/node-feature-discovery/api/generated/clientset/versioned/typed/nfd/v1alpha1/nfd_client.go)
- [vendor/sigs.k8s.io/node-feature-discovery/api/generated/clientset/versioned/typed/nfd/v1alpha1/nodefeature.go](vendor/sigs.k8s.io/node-feature-discovery/api/generated/clientset/versioned/typed/nfd/v1alpha1/nodefeature.go)
- [vendor/sigs.k8s.io/node-feature-discovery/api/generated/clientset/versioned/typed/nfd/v1alpha1/nodefeaturegroup.go](vendor/sigs.k8s.io/node-feature-discovery/api/generated/clientset/versioned/typed/nfd/v1alpha1/nodefeaturegroup.go)
- [vendor/sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1/types.go](vendor/sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1/types.go)
- [vendor/sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1/zz_generated.deepcopy.go](vendor/sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1/zz_generated.deepcopy.go)

</details>



## Purpose and Scope

The Node Feature Discovery (NFD) API provides Kubernetes Custom Resource Definitions (CRDs) for hardware feature detection and feature-based node customization. This page documents the v1alpha1 API types, their structure, and how the `nvml-mock` system integrates with NFD to trigger node labeling in E2E test scenarios.

The primary integration path for `nvml-mock` is via **NFD Local Source**, where the mock library writes feature files to the host filesystem, which are then consumed by the NFD daemon to apply labels to the Kubernetes Node object.

**Sources:** [vendor/sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1/types.go:1-395](), [tests/e2e/go/scenario_nfd_test.go:24-66]()

## Core Custom Resource Definitions

The NFD API defines three primary CRDs that work together to enable feature discovery and node customization:

```mermaid
graph TB
    subgraph "NFD v1alpha1 API Resources"
        NodeFeature["NodeFeature<br/>Per-node discovered features"]
        NodeFeatureRule["NodeFeatureRule<br/>Feature-based customization rules<br/>(cluster-scoped)"]
        NodeFeatureGroup["NodeFeatureGroup<br/>Dynamic node pools by features<br/>(namespaced)"]
    end
    
    subgraph "Kubernetes Node Objects"
        Node["Node<br/>Labels, Annotations, Taints,<br/>Extended Resources"]
    end
    
    NodeFeature -->|"Input to"| NodeFeatureRule
    NodeFeatureRule -->|"Customizes"| Node
    NodeFeature -->|"Input to"| NodeFeatureGroup
    NodeFeatureGroup -->|"Groups"| Node
```

### NodeFeature
`NodeFeature` is a namespaced resource that holds the complete set of features discovered for a single node. [vendor/sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1/types.go:40-46]().

| Field | Type | Description |
|-------|------|-------------|
| `spec.features` | `Features` | Complete raw feature data organized by type (flags, attributes, instances) [vendor/sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1/types.go:52]() |
| `spec.labels` | `map[string]string` | Labels requested to be created on the node [vendor/sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1/types.go:55]() |

### NodeFeatureRule
`NodeFeatureRule` is a cluster-scoped resource that defines rules for feature-based node customization. [vendor/sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1/types.go:117-123](). Rules are evaluated against `NodeFeature` objects to automatically apply labels, annotations, or taints.

### NodeFeatureGroup
`NodeFeatureGroup` is a namespaced resource that dynamically groups nodes based on feature matching rules. [vendor/sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1/types.go:137-147](). It tracks matching nodes in `status.nodes`. [vendor/sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1/types.go:155-163]().

**Sources:** [vendor/sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1/types.go:35-179]()

## nvml-mock Integration: The Local Source Flow

In E2E testing, `nvml-mock` uses NFD's "Local Source" capability to trigger node labeling. Instead of interacting with the NFD API directly, the mock setup writes a feature file to a specific host directory which the NFD daemon monitors.

### Data Flow: From Mock to Node Label

```mermaid
sequenceDiagram
    participant SM as nvml-mock setup.sh
    participant FS as Host Filesystem (/etc/kubernetes/node-feature-discovery/features.d)
    participant NFD as NFD Worker Pod
    participant API as K8s API Server (Node Object)

    SM->>FS: Write nvml-mock.features ("pci-10de.present=true")
    Note over FS: File: /host/etc/kubernetes/node-feature-discovery/features.d/nvml-mock.features
    NFD->>FS: Scan directory (Local Source)
    NFD->>API: Patch Node Labels & Annotations
    Note over API: Label: feature.node.kubernetes.io/pci-10de.present=true
    Note over API: Annotation: nfd.node.kubernetes.io/feature-labels=pci-10de.present
```

**Implementation Details:**
- **Feature File Path**: The file is written to `/host/etc/kubernetes/node-feature-discovery/features.d/nvml-mock.features`. [tests/e2e/go/scenario_nfd_test.go:54]()
- **Feature Content**: The mock writes `pci-10de.present=true`. [tests/e2e/go/scenario_nfd_test.go:117]()
- **Label Transformation**: NFD's local source transforms this line into the label `feature.node.kubernetes.io/pci-10de.present`. [tests/e2e/go/scenario_nfd_test.go:34-36]()
- **Ownership Tracking**: NFD records the labels it manages in the `nfd.node.kubernetes.io/feature-labels` annotation. [tests/e2e/go/scenario_nfd_test.go:44]()

**Sources:** [tests/e2e/go/scenario_nfd_test.go:24-58](), [tests/e2e/go/scenario_nfd_test.go:114-144]()

## Feature Data Model

The NFD API organizes discovered features into three distinct types:

| Feature Type | Code Entity | Description |
|--------------|-------------|-------------|
| **Flags** | `FlagFeatureSet` | Boolean characteristics (presence/absence). [vendor/sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1/types.go:72-75]() |
| **Attributes** | `AttributeFeatureSet` | Single-valued string characteristics (e.g., version). [vendor/sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1/types.go:78-81]() |
| **Instances** | `InstanceFeatureSet` | Multi-instance hardware (e.g., multiple GPUs) with multiple attributes per instance. [vendor/sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1/types.go:83-87]() |

**Sources:** [vendor/sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1/types.go:58-97]()

## API Client and Generated Code

The project vendors the NFD generated clientset to allow E2E tests to interact with NFD resources.

```mermaid
classDiagram
    class Clientset {
        +NfdV1alpha1() NfdV1alpha1Interface
    }
    class NfdV1alpha1Interface {
        <<interface>>
        +NodeFeatures(namespace) NodeFeatureInterface
        +NodeFeatureGroups(namespace) NodeFeatureGroupInterface
        +NodeFeatureRules() NodeFeatureRuleInterface
    }
    class NodeFeatureInterface {
        <<interface>>
        +Create()
        +Get()
        +List()
        +Watch()
        +Patch()
    }
    Clientset ..> NfdV1alpha1Interface
    NfdV1alpha1Interface ..> NodeFeatureInterface
```

**Key Components:**
- **Clientset**: The entry point for NFD API operations. [vendor/sigs.k8s.io/node-feature-discovery/api/generated/clientset/versioned/clientset.go:37-40]()
- **DeepCopy**: All NFD types implement `DeepCopy` and `DeepCopyInto` for safe object manipulation within the Kubernetes controller-runtime. [vendor/sigs.k8s.io/node-feature-discovery/api/nfd/v1alpha1/zz_generated.deepcopy.go:29-40]()
- **Typed Clients**: The `v1alpha1` package provides specialized clients for `NodeFeature`, `NodeFeatureRule`, and `NodeFeatureGroup`. [vendor/sigs.k8s.io/node-feature-discovery/api/generated/clientset/versioned/typed/nfd/v1alpha1/nfd_client.go:29-34]()

**Sources:** [vendor/sigs.k8s.io/node-feature-discovery/api/generated/clientset/versioned/clientset.go:31-53](), [vendor/sigs.k8s.io/node-feature-discovery/api/generated/clientset/versioned/typed/nfd/v1alpha1/nodefeature.go:35-51](), [vendor/sigs.k8s.io/node-feature-discovery/api/generated/clientset/versioned/typed/nfd/v1alpha1/nfd_client.go:37-51]()

## E2E Test Verification Logic

The NFD E2E scenario (`scenario_nfd_test.go`) validates the provenance of labels to ensure they are created by NFD and not hardcoded by setup scripts.

1. **Synchronization Barrier**: The test first waits for `nvidia.com/gpu.present` (written by `setup.sh`) to ensure the mock environment is initialized. [tests/e2e/go/scenario_nfd_test.go:96-109]()
2. **Absent Check**: Verifies that the PCI vendor label does *not* exist before NFD is installed. [tests/e2e/go/scenario_nfd_test.go:111]()
3. **Feature File Validation**: Executes `cat` inside the mock pod to verify the `nvml-mock.features` file contains the correct key-value pair. [tests/e2e/go/scenario_nfd_test.go:115-119]()
4. **Ownership Validation**: After installing NFD via Helm, the test checks the node annotation `nfd.node.kubernetes.io/feature-labels` to confirm NFD has claimed ownership of the `pci-10de.present` feature. [tests/e2e/go/scenario_nfd_test.go:141-143]()

**Sources:** [tests/e2e/go/scenario_nfd_test.go:72-144]()

---

# Page: Dynamic Resource Allocation (DRA) API

# Dynamic Resource Allocation (DRA) API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tests/e2e/VERSION-MATRIX.md](tests/e2e/VERSION-MATRIX.md)
- [tests/e2e/go/assertions/resources.go](tests/e2e/go/assertions/resources.go)
- [tests/e2e/go/framework/helm/helm.go](tests/e2e/go/framework/helm/helm.go)
- [tests/e2e/go/framework/helm/helm_test.go](tests/e2e/go/framework/helm/helm_test.go)
- [tests/e2e/go/framework/kube/kube.go](tests/e2e/go/framework/kube/kube.go)
- [vendor/k8s.io/api/resource/v1alpha3/generated.proto](vendor/k8s.io/api/resource/v1alpha3/generated.proto)
- [vendor/k8s.io/api/resource/v1alpha3/types.go](vendor/k8s.io/api/resource/v1alpha3/types.go)
- [vendor/k8s.io/api/resource/v1alpha3/types_swagger_doc_generated.go](vendor/k8s.io/api/resource/v1alpha3/types_swagger_doc_generated.go)
- [vendor/k8s.io/api/resource/v1beta1/generated.proto](vendor/k8s.io/api/resource/v1beta1/generated.proto)
- [vendor/k8s.io/api/resource/v1beta1/types.go](vendor/k8s.io/api/resource/v1beta1/types.go)
- [vendor/k8s.io/api/resource/v1beta1/types_swagger_doc_generated.go](vendor/k8s.io/api/resource/v1beta1/types_swagger_doc_generated.go)

</details>



## Purpose and Scope

This document details the Dynamic Resource Allocation (DRA) API used for device resource management within the `k8s-test-infra` codebase. It focuses on the integration between the `nvml-mock` system and the DRA driver for publishing simulated GPU resources. The system leverages `ResourceSlice`, `ResourceClaim`, and `DeviceClass` objects to manage hardware beyond standard CPU/memory.

---

## Overview

The `nvml-mock` infrastructure simulates GPU hardware that is consumed by the NVIDIA DRA driver. The driver discovers these mock GPUs via the simulated NVML library and publishes them as Kubernetes `ResourceSlice` objects. This allows end-to-end testing of the DRA stack, including the `DynamicResourceAllocation` feature gate, without requiring physical hardware [tests/e2e/VERSION-MATRIX.md:22-22](), [tests/e2e/VERSION-MATRIX.md:60-61]().

**Key Components in Test Infra:**
- **DRA Driver (GPU)**: Version `v0.10.x` is used in CI to discover mock GPUs and publish `ResourceSlices` [tests/e2e/VERSION-MATRIX.md:10-10]().
- **ResourceSlice**: The primary mechanism for the driver to report device availability [vendor/k8s.io/api/resource/v1beta1/types.go:80-91]().
- **Kind Cluster**: Configured with Kubernetes 1.31+ and the `DynamicResourceAllocation` feature gate enabled [tests/e2e/VERSION-MATRIX.md:60-61]().

---

## Resource Management Flow

The following diagram bridges the natural language concepts of device discovery to the specific Kubernetes API entities and test framework components.

### GPU Resource Publishing Data Flow

```mermaid
sequenceDiagram
    participant Mock as nvml-mock (Library)
    participant Driver as NVIDIA DRA Driver
    participant Kube as K8s API (ResourceSlice)
    participant Test as E2E Assertions (assertions.go)

    Note over Mock: Simulates GPUs based on Profile
    Driver->>Mock: Call nvmlDeviceGetCount()
    Mock-->>Driver: Return N devices
    Driver->>Kube: Create/Update ResourceSlice
    Note over Kube: ResourceSlice.Spec.Devices populated
    Test->>Kube: Call ResourceSliceGPUTotal()
    Kube-->>Test: Return Total Device Count
    Test->>Test: WaitResourceSliceTotal(ctx, k, want, ...)
```

**Sources:** [tests/e2e/VERSION-MATRIX.md:22-22](), [tests/e2e/go/assertions/resources.go:74-81](), [vendor/k8s.io/api/resource/v1beta1/types.go:103-166]()

---

## Core API Implementation

### ResourceSlice
The `ResourceSlice` represents a pool of devices managed by a common driver. In the `k8s-test-infra` context, the `ResourceSliceSpec` identifies the `nvidia-dra-driver-gpu` and lists the mock devices [vendor/k8s.io/api/resource/v1beta1/types.go:103-113]().

| Field | Code Entity | Purpose |
|-------|-------------|---------|
| `Driver` | `ResourceSliceSpec.Driver` | Identifies the DRA driver (e.g., `gpu.nvidia.com`) [vendor/k8s.io/api/resource/v1beta1/types.go:113-113]() |
| `Devices` | `[]Device` | List of device instances with attributes/capacities [vendor/k8s.io/api/resource/v1beta1/types.go:165-165]() |
| `Pool` | `ResourcePool` | Groups slices belonging to the same resource pool [vendor/k8s.io/api/resource/v1beta1/types.go:118-118]() |

### Device Selection (CEL)
DRA uses the Common Expression Language (CEL) for selecting devices based on attributes. The `CELDeviceSelector` evaluates expressions against device properties [vendor/k8s.io/api/resource/v1alpha3/types.go:33-44]().

**Sources:** [vendor/k8s.io/api/resource/v1beta1/types.go:80-166](), [vendor/k8s.io/api/resource/v1alpha3/types.go:33-87]()

---

## Integration and Testing

The E2E framework provides specialized assertions for DRA resources, implemented in `tests/e2e/go/assertions/resources.go`.

### Kube Client and Resource Tracking

The framework uses a `Client` struct to execute `kubectl` commands and decode JSON output into minimal typed views of Kubernetes objects [tests/e2e/go/framework/kube/kube.go:36-71]().

```mermaid
classDiagram
    class KubeClient {
        +ResourceSliceGPUTotal(ctx) int
        +AllocatableGPU(ctx, node) int
    }
    class ResourceSliceObj {
        +ResourceSliceSpec spec
    }
    class ResourceSliceSpec {
        +string driver
        +[]Device devices
    }
    class Device {
        +string name
    }

    KubeClient ..> ResourceSliceObj : Decodes JSON into
    ResourceSliceObj --> ResourceSliceSpec
    ResourceSliceSpec --> Device
```

**Key Testing Functions:**
- `WaitResourceSliceTotal`: Polls the cluster until the summed `ResourceSlice` device count matches the expected number of mock GPUs [tests/e2e/go/assertions/resources.go:74-81]().
- `ResourceSliceGPUTotal`: A `kube.Client` method that aggregates device counts across all `ResourceSlices` [tests/e2e/go/assertions/resources.go:78-78]().

**Sources:** [tests/e2e/go/framework/kube/kube.go:77-138](), [tests/e2e/go/assertions/resources.go:74-81]()

---

## Deployment via Helm

The DRA driver and mock components are deployed using the `helm.Client` wrapper [tests/e2e/go/framework/helm/helm.go:20-25]().

- **DRA Driver Chart**: `nvidia/nvidia-dra-driver-gpu` is installed with specific version pinning in CI [tests/e2e/VERSION-MATRIX.md:10-10]().
- **Wait Mechanism**: The `helm.Release` struct supports a `Wait` flag, ensuring the driver is ready before assertions begin [tests/e2e/go/framework/helm/helm.go:38-38](), [tests/e2e/go/framework/helm/helm.go:107-109]().

**Sources:** [tests/e2e/go/framework/helm/helm.go:28-40](), [tests/e2e/VERSION-MATRIX.md:10-10]()

---

## Feature Gates and Compatibility

The DRA API implementation in this codebase targets `v1beta1` for `ResourceSlice` and `v1alpha3` for `DeviceSelector` [vendor/k8s.io/api/resource/v1beta1/types.go:54-54](), [vendor/k8s.io/api/resource/v1alpha3/types.go:17-17]().

- **Feature Gate**: `DynamicResourceAllocation` must be enabled in the Kind cluster [tests/e2e/VERSION-MATRIX.md:60-60]().
- **CDI**: Container Device Interface (CDI) must be enabled in `containerd` to support DRA device injection [tests/e2e/VERSION-MATRIX.md:61-61]().

**Sources:** [tests/e2e/VERSION-MATRIX.md:59-63](), [vendor/k8s.io/api/resource/v1beta1/types.go:78-79]()

---

# Page: Certificate Utilities

# Certificate Utilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [vendor/k8s.io/client-go/util/cert/cert.go](vendor/k8s.io/client-go/util/cert/cert.go)

</details>



## Purpose and Scope

This document describes the certificate generation utilities provided by the k8s-test-infra project for creating self-signed TLS certificates. These utilities are primarily used in test scenarios where secure communication channels need to be established without involving external certificate authorities.

The utilities are vendored from `k8s.io/client-go/util/cert` and provide functionality for generating:

- Self-signed CA (Certificate Authority) certificates
- Self-signed server certificates with custom subject alternative names (SANs)
- Certificate/key pairs with support for test fixtures that help with deterministic tests

For information about Kubernetes client operations that may use these certificates, see [Kubernetes Client-Go Operations](#6.1). For YAML manifest processing utilities, see [YAML and JSON Manifest Processing](#6.5).

---

## Certificate Generation Architecture

The certificate utilities provide a layered approach to certificate generation, with high-level convenience functions wrapping lower-level primitives and configuration structures defining certificate attributes.

```mermaid
graph TB
    subgraph "Public API Functions"
        GSC["GenerateSelfSignedCertKey()<br/>Simple convenience wrapper"]
        GSCF["GenerateSelfSignedCertKeyWithFixtures()<br/>Supports fixture loading"]
        GSCO["GenerateSelfSignedCertKeyWithOptions()<br/>Full parameter control"]
    end
    
    subgraph "Core Certificate Creation"
        NSCA["NewSelfSignedCACert()<br/>Creates self-signed CA cert"]
        X509CREATE["x509.CreateCertificate()<br/>Go standard library"]
    end
    
    subgraph "Configuration Structures"
        CONFIG["Config<br/>CommonName, Organization, AltNames"]
        ALTNAMES["AltNames<br/>DNSNames, IPs"]
        OPTIONS["SelfSignedCertKeyOptions<br/>Host, MaxAge, FixtureDirectory"]
    end
    
    subgraph "Outputs"
        CERTPEM["Certificate PEM bytes"]
        KEYPEM["Private Key PEM bytes"]
    end
    
    GSC --> GSCO
    GSCF --> GSCO
    GSCO --> OPTIONS
    GSCO --> X509CREATE
    NSCA --> CONFIG
    NSCA --> ALTNAMES
    NSCA --> X509CREATE
    
    X509CREATE --> CERTPEM
    X509CREATE --> KEYPEM
    
    OPTIONS --> ALTNAMES
    CONFIG --> ALTNAMES
```

**Sources:** [vendor/k8s.io/client-go/util/cert/cert.go:1-277]()

---

## Core Data Structures

### Config Structure

Defines the basic attributes for creating certificates, specifically for CA certificates.

| Field          | Type              | Description                        |
|----------------|-------------------|----------------------------------|
| `CommonName`   | `string`          | Subject Common Name field         |
| `Organization` | `[]string`        | Subject Organization              |
| `AltNames`     | `AltNames`        | Subject Alternative Names (SANs) |
| `Usages`       | `[]x509.ExtKeyUsage` | Extended usages (e.g., server auth)|
| `NotBefore`    | `time.Time`       | Certificate validity start time  |

**Sources:** [vendor/k8s.io/client-go/util/cert/cert.go:42-49]()

---

### AltNames Structure

Represents DNS names and IP addresses added to the certificate’s Subject Alternative Names.

| Field     | Type       | Description                     |
|-----------|------------|--------------------------------|
| `DNSNames`| `[]string` | DNS names for SAN extension     |
| `IPs`     | `[]net.IP` | IP addresses for SAN extension  |

**Sources:** [vendor/k8s.io/client-go/util/cert/cert.go:54-57]()

---

### SelfSignedCertKeyOptions Structure

Provides detailed options for generating self-signed certificates, including support for fixture directories.

| Field            | Type          | Description                                                          |
|------------------|---------------|----------------------------------------------------------------------|
| `Host`           | `string`      | Required primary host (DNS name or IP address)                      |
| `AlternateIPs`   | `[]net.IP`    | Optional additional IPs to include in SANs                          |
| `AlternateDNS`   | `[]string`    | Optional additional DNS names to include in SANs                    |
| `MaxAge`          | `time.Duration` | Certificate validity duration (defaults to 1 year if zero)          |
| `FixtureDirectory`| `string`      | Optional directory for loading or saving test certificate fixtures  |

**Sources:** [vendor/k8s.io/client-go/util/cert/cert.go:96-115]()

---

## Certificate Generation Functions

### Function Overview

```mermaid
graph LR
    subgraph "User Entry Points"
        U1["GenerateSelfSignedCertKey()"]
        U2["GenerateSelfSignedCertKeyWithFixtures()"]
        U3["GenerateSelfSignedCertKeyWithOptions()"]
    end
    
    subgraph "Implementation"
        IMPL["GenerateSelfSignedCertKeyWithOptions()<br/>Core implementation"]
    end
    
    subgraph "Auxiliary Functions"
        CA["NewSelfSignedCACert()<br/>Creates CA certificate"]
    end
    
    U1 --> IMPL
    U2 --> IMPL
    U3 --> IMPL
    
    IMPL -.->|"internally calls"| CA
```

**Sources:** [vendor/k8s.io/client-go/util/cert/cert.go:59-268]()

---

### GenerateSelfSignedCertKey

Simplified wrapper function that generates a self-signed certificate and key for the given host without fixture support.

```go
func GenerateSelfSignedCertKey(
    host string,
    alternateIPs []net.IP,
    alternateDNS []string,
) ([]byte, []byte, error)
```

- `host`: primary DNS name or IP
- `alternateIPs`: additional IP addresses for SAN
- `alternateDNS`: additional DNS names for SAN

Returns PEM-encoded certificate and private key bytes or an error.

**Sources:** [vendor/k8s.io/client-go/util/cert/cert.go:120-126]()

---

### GenerateSelfSignedCertKeyWithFixtures

Similar to the above but supports loading pre-generated certificates from a fixture directory for reproducible testing.

```go
func GenerateSelfSignedCertKeyWithFixtures(
    host string,
    alternateIPs []net.IP,
    alternateDNS []string,
    fixtureDirectory string,
) ([]byte, []byte, error)
```

Certificates under the fixture directory must have filenames matching this pattern:

```
<host>_<ip>-<ip>_<alternateDNS>-<alternateDNS>.crt
<host>_<ip>-<ip>_<alternateDNS>-<alternateDNS>.key
```

If these files exist, they are returned directly, otherwise new certificates are generated and saved there with a longer validity.

**Sources:** [vendor/k8s.io/client-go/util/cert/cert.go:136-143]()

---

### GenerateSelfSignedCertKeyWithOptions

The core implementation that gives full control parameters via `SelfSignedCertKeyOptions` struct. It either loads fixtures or generates a new CA and server certificate signed by the CA.

```go
func GenerateSelfSignedCertKeyWithOptions(
    opts SelfSignedCertKeyOptions
) ([]byte, []byte, error)
```

**Key behaviors:**

- Validity starts 1 hour before current time for clock skew safety
- Defaults to 1 year certificate validity unless overridden
- Generates a new RSA 2048-bit CA key and certificate (IsCA=true)
- Generates a new RSA 2048-bit server key and certificate, signed by CA
- Supports SAN entries for IPs and DNS names (including the main host)
- Certificates and keys are PEM encoded and returned as separate byte slices
- When using fixtures, files are loaded or saved in the defined directory with 100-year validity

**Sequence of main steps:**

```mermaid
sequenceDiagram
    participant Caller
    participant GSCWO as GenerateSelfSignedCertKeyWithOptions
    participant FS as File System
    participant Crypto as crypto/x509 and rsa
    participant PEM as pem.Encode
    
    Caller->>GSCWO: Call with options
    
    alt Fixture Directory Provided
        GSCWO->>FS: Check if cert/key files exist
        alt Files Exist
            FS-->>GSCWO: Return existing files
            GSCWO-->>Caller: Return cached cert and key bytes
        end
    end
    
    Note over GSCWO: Generate CA certificate and key
    GSCWO->>Crypto: Generate CA RSA key (2048 bits)
    GSCWO->>Crypto: Generate random serial number
    GSCWO->>Crypto: Create CA x509 certificate template (IsCA: true)
    GSCWO->>Crypto: x509.CreateCertificate (self-signed)
    
    Note over GSCWO: Generate server certificate and key
    GSCWO->>Crypto: Generate server RSA key (2048 bits)
    GSCWO->>Crypto: Generate random serial number
    GSCWO->>Crypto: Create server x509 certificate template (includes SAN)
    GSCWO->>Crypto: x509.CreateCertificate (signed by CA)
    
    Note over GSCWO: Encode certificates and keys to PEM bytes
    GSCWO->>PEM: Encode server certificate
    GSCWO->>PEM: Encode CA certificate
    GSCWO->>PEM: Encode server private key
    
    alt Fixture Directory Provided
        GSCWO->>FS: Write cert and key files with 100-year validity
    end
    
    GSCWO-->>Caller: Return PEM encoded cert and key
```

**Sources:** [vendor/k8s.io/client-go/util/cert/cert.go:146-268]()

---

### NewSelfSignedCACert

Creates a self-signed Certificate Authority (CA) certificate from a `Config` and a private key.

```go
func NewSelfSignedCACert(cfg Config, key crypto.Signer) (*x509.Certificate, error)
```

- Sets a 10-year validity period by default
- Sets certificate fields: IsCA=true, KeyUsage includes CertSign
- Uses the Go standard library `x509.CreateCertificate` to make the self-signed CA cert
- Returns parsed `*x509.Certificate`

This function is used internally for the CA certificate generation in the main self-signed cert creation flow.

**Sources:** [vendor/k8s.io/client-go/util/cert/cert.go:59-93]()

---

## Certificate Attributes and Key Usage

### CA Certificate Template Properties

```mermaid
graph TB
    subgraph "CA Certificate"
        SERIAL["SerialNumber<br/>Random 63-bit integer"]
        SUBJECT["Subject<br/>CN: <host>-ca@<timestamp>"]
        VALIDITY["Validity Period<br/>NotBefore: issued time<br/>NotAfter: +10 years"]
        KEYUSAGE["KeyUsage<br/>KeyEncipherment, DigitalSignature, CertSign"]
        BASIC_CONSTRAINTS["Basic Constraints<br/>IsCA: true, Valid"]
    end
    
    SERIAL --> SUBJECT
    SUBJECT --> VALIDITY
    VALIDITY --> KEYUSAGE
    KEYUSAGE --> BASIC_CONSTRAINTS
```

The CA certificate supports signing other certificates and is valid for 10 years. It is self-signed.

**Sources:** [vendor/k8s.io/client-go/util/cert/cert.go:183-194]()

---

### Server Certificate Template Properties

```mermaid
graph TB
    subgraph "Server Certificate"
        SERIAL2["SerialNumber<br/>Random 63-bit integer"]
        SUBJECT2["Subject<br/>CN: <host>@<timestamp>"]
        VALIDITY2["Validity Period<br/>NotBefore: issued time<br/>NotAfter: + specified MaxAge"]
        KEYUSAGE2["KeyUsage<br/>KeyEncipherment, DigitalSignature"]
        EXT_KEYUSAGE["Extended Key Usage<br/>ServerAuth"]
        SANs["Subject Alternative Names<br/>DNSNames: host + alternateDNS<br/>IPs: host + alternateIPs"]
    end
    
    SERIAL2 --> SUBJECT2
    SUBJECT2 --> VALIDITY2
    VALIDITY2 --> KEYUSAGE2
    KEYUSAGE2 --> EXT_KEYUSAGE
    EXT_KEYUSAGE --> SANs
```

The server certificate is signed by the generated CA and includes SAN entries for IPs and DNS names.

**Sources:** [vendor/k8s.io/client-go/util/cert/cert.go:216-237]()

---

## Test Fixture Support

To support deterministic testing, the certificate utilities can optionally load certificates from a fixture directory. If matching cert/key files exist, they are returned without regeneration. If not found, new certificates are generated and saved with a long (100 years) validity.

### Fixture Filename Format:

```
<host>_<ip>-<ip>_<alternateDNS>-<alternateDNS>.crt
<host>_<ip>-<ip>_<alternateDNS>-<alternateDNS>.key
```

### Fixture Loading Flow

```mermaid
flowchart TD
    START["GenerateSelfSignedCertKeyWithOptions called"]
    CHECK_DIR{"FixtureDirectory provided?"}
    BASE_NAME["Compute base filename:<br/>{host}_{ip}-{ip}_{dns}-{dns}"]
    TRY_LOAD["Try reading cert and key files"]
    FILES_EXIST{"Are both files readable?"}
    RETURN_CACHED["Return fixture cert and key"]
    GENERATE["Generate new certs and keys"]
    SAVE_FIXTURES["Write cert/key to fixture directory with 100 year validity"]
    RETURN_NEW["Return newly generated cert and key"]
    END["End"]
    
    START --> CHECK_DIR
    CHECK_DIR -->|Yes| BASE_NAME
    CHECK_DIR -->|No| GENERATE
    BASE_NAME --> TRY_LOAD
    TRY_LOAD --> FILES_EXIST
    FILES_EXIST -->|Yes| RETURN_CACHED
    FILES_EXIST -->|No| GENERATE
    GENERATE --> SAVE_FIXTURES
    SAVE_FIXTURES --> RETURN_NEW
    RETURN_CACHED --> END
    RETURN_NEW --> END
```

**Attributes:**
- Fixtures have a very long validity (100 years) to avoid test flakiness due to expiry
- The naming scheme precisely encodes hosts and SAN attributes into filenames to avoid collisions
- Fixture files reside in user-specified directories for test control

**Sources:** [vendor/k8s.io/client-go/util/cert/cert.go:158-171](), [vendor/k8s.io/client-go/util/cert/cert.go:258-265]()

---

## PEM Encoding Format

The generated certificates and keys are PEM-encoded for easy storage in files used by TLS stacks.

### Output Buffer Structure

```mermaid
graph TB
    subgraph "Certificate PEM (certBuffer)"
        BEGIN_CERT["-----BEGIN CERTIFICATE-----"]
        SERVER_CERT["Base64-encoded DER server cert"]
        MID_CERT["-----END CERTIFICATE-----<br/>-----BEGIN CERTIFICATE-----"]
        CA_CERT["Base64-encoded DER CA cert"]
        END_CERT["-----END CERTIFICATE-----"]
    end
    
    subgraph "Key PEM (keyBuffer)"
        BEGIN_KEY["-----BEGIN RSA PRIVATE KEY-----"]
        PRIVATE_KEY["Base64-encoded PKCS1 private key"]
        END_KEY["-----END RSA PRIVATE KEY-----"]
    end
    
    BEGIN_CERT --> SERVER_CERT
    SERVER_CERT --> MID_CERT
    MID_CERT --> CA_CERT
    CA_CERT --> END_CERT
    
    BEGIN_KEY --> PRIVATE_KEY
    PRIVATE_KEY --> END_KEY
```

**Order:**

1. Server Certificate PEM block
2. CA Certificate PEM block
3. Private Key PEM block (separate buffer)

**Sources:** [vendor/k8s.io/client-go/util/cert/cert.go:244-256]()

---

## Integration with Kubernetes Testing

The certificate utilities facilitate creating TLS credentials for Kubernetes components and test harnesses requiring secure connections.

### Typical Usage Workflow in Tests

```mermaid
graph TB
    subgraph "Test Setup"
        TEST_INIT["Test suite initialization"]
        GEN_CERTS["Generate self-signed certs<br/>GenerateSelfSignedCertKey()"]
        WRITE_FILES["Write cert/key to temporary files"]
    end
    
    subgraph "Component Setup"
        CONFIG_SERVER["Configure server with --tls-cert-file and --tls-private-key-file"]
        CONFIG_CLIENT["Configure client with --ca-cert-file"]
    end
    
    subgraph "Test Execution"
        START_COMPONENTS["Start server and client components"]
        TLS_HANDSHAKE["TLS handshake using generated certs"]
        RUN_TESTS["Execute secured test scenarios"]
    end
    
    subgraph "Teardown"
        CLEANUP["Remove temporary certificate files"]
    end
    
    TEST_INIT --> GEN_CERTS
    GEN_CERTS --> WRITE_FILES
    WRITE_FILES --> CONFIG_SERVER
    WRITE_FILES --> CONFIG_CLIENT
    CONFIG_SERVER --> START_COMPONENTS
    CONFIG_CLIENT --> START_COMPONENTS
    START_COMPONENTS --> TLS_HANDSHAKE
    TLS_HANDSHAKE --> RUN_TESTS
    RUN_TESTS --> CLEANUP
```

This process supports secure communication during E2E tests without requiring a real CA infrastructure.

**Sources:** Inferred from overall usage in [vendor/k8s.io/client-go/util/cert/cert.go:1-277]()

---

## Key Constants and Defaults

| Constant/Default      | Value                         | Description                                           |
|----------------------|-------------------------------|-------------------------------------------------------|
| `duration365d`       | `time.Hour * 24 * 365`         | One year duration constant                             |
| CA Default Validity  | 10 years                      | CA certificates valid for 10 years                    |
| Server Default Validity | 1 year (configurable)        | Server certificates default validity                  |
| Fixture Cert Validity | 100 years                    | Test fixture certificates valid for 100 years        |
| RSA Key Size          | 2048 bits                    | RSA key length used for generated keys                |
| Validity Start Offset | -1 hour                      | Certificates valid 1 hour before generation time      |
| Serial Number Range   | [1, 2^63)                    | Serial numbers are random uint63 values                |

**Sources:** [vendor/k8s.io/client-go/util/cert/cert.go:40](), [vendor/k8s.io/client-go/util/cert/cert.go:79](), [vendor/k8s.io/client-go/util/cert/cert.go:152-154](), [vendor/k8s.io/client-go/util/cert/cert.go:156](), [vendor/k8s.io/client-go/util/cert/cert.go:170](), [vendor/k8s.io/client-go/util/cert/cert.go:173]()

---

## Error Handling

The generation functions return detailed errors in these cases:

| Error Condition                | Context                                 | Description                                 |
|-------------------------------|-----------------------------------------|---------------------------------------------|
| Random number generation fail  | All functions                           | Failure to generate serial number             |
| RSA key generation failure     | `GenerateSelfSignedCertKeyWithOptions` | RSA key generation fails                        |
| Certificate creation failure   | All functions                          | `x509.CreateCertificate` fails                  |
| Certificate parsing failure    | `NewSelfSignedCACert`                   | Parsing DER to certificate fails                |
| PEM encoding failure           | `GenerateSelfSignedCertKeyWithOptions` | `pem.Encode` to buffer fails                    |
| File I/O failure (fixtures)   | `GenerateSelfSignedCertKeyWithOptions` | Reading or writing fixture files fails          |
| Fixture inconsistency          | `GenerateSelfSignedCertKeyWithOptions` | Cert file exists but key file does not or vice versa |

Errors propagate up to the caller for handling in test setup or runtime environments.

**Sources:** [vendor/k8s.io/client-go/util/cert/cert.go:60-268]()

---

## Related Utilities and Dependencies

| Package                     | Purpose                                                     |
|-----------------------------|-------------------------------------------------------------|
| `crypto/rand`               | Cryptographically secure random number generation           |
| `crypto/rsa`                | RSA key generation and manipulation                         |
| `crypto/x509`               | X.509 certificate creation and parsing                      |
| `crypto/x509/pkix`          | Structures for certificate subjects and extensions          |
| `encoding/pem`              | PEM encoding and decoding of certificates and keys          |
| `k8s.io/client-go/util/keyutil` | Constants for key PEM block types and helpers             |
| `k8s.io/utils/net`          | Network utilities for IP parsing (`ParseIPSloppy`)          |

The utilities leverage Go's crypto standard library for all cryptographic operations.

**Sources:** [vendor/k8s.io/client-go/util/cert/cert.go:19-38]()

---

# Summary

The Certificate Utilities in k8s-test-infra provide robust, simple-to-use functions and configuration structures to generate self-signed CA and server certificates with advanced features such as SAN specification and fixture-based deterministic loading. These utilities enable Kubernetes component tests to establish secure TLS communication environments without external dependencies.

The layered design makes it easy to generate simple certificates or fully customize parameters, while built-in fixture support facilitates reproducible test runs.

# End of Section 6.4

---

**Sources:**

- [vendor/k8s.io/client-go/util/cert/cert.go:1-277]()

---

# Page: YAML and JSON Manifest Processing

# YAML and JSON Manifest Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [go.mod](go.mod)
- [go.sum](go.sum)
- [vendor/github.com/onsi/ginkgo/v2/CHANGELOG.md](vendor/github.com/onsi/ginkgo/v2/CHANGELOG.md)
- [vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go](vendor/github.com/onsi/ginkgo/v2/reporters/default_reporter.go)
- [vendor/github.com/onsi/ginkgo/v2/types/version.go](vendor/github.com/onsi/ginkgo/v2/types/version.go)
- [vendor/k8s.io/apimachinery/pkg/api/validation/objectmeta.go](vendor/k8s.io/apimachinery/pkg/api/validation/objectmeta.go)
- [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go](vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go)
- [vendor/modules.txt](vendor/modules.txt)

</details>



## Purpose and Scope

This document describes the utilities provided by `k8s.io/apimachinery/pkg/util/yaml` for loading and decoding Kubernetes manifests in YAML or JSON format. These utilities are essential for test infrastructure that needs to load resource definitions from manifests, handle multi-document streams, and automatically detect the format of input data. 

The codebase relies on these utilities to bridge the gap between human-readable YAML configurations and Go-native Kubernetes object structures used in the E2E test harness and the `nvml-mock` configuration system.

---

## Manifest Processing Architecture

The manifest processing system provides automatic format detection, multi-document stream handling, and conversion between YAML and JSON representations of Kubernetes resources. It leverages `sigs.k8s.io/yaml` for the heavy lifting of conversion while providing Kubernetes-specific stream management.

### Data Flow: From Manifest to Entity
The following diagram illustrates how raw input bytes are transformed into code entities like `interface{}` or structured Kubernetes objects.

**Manifest Processing Data Flow**
```mermaid
graph TB
    subgraph "Input_Sources"
        FILE["File on Disk"]
        READER["io.Reader Stream"]
        BYTES["[]byte Buffer"]
    end
    
    subgraph "Format_Detection_&_Decoding"
        GUESS["GuessJSONStream()<br/>[vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:463-485]"]
        YAMLORJSON["YAMLOrJSONDecoder<br/>[vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:240-358]"]
        YAMLTOJSON["YAMLToJSONDecoder<br/>[vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:106-143]"]
        YAMLDECODER["YAMLDecoder<br/>[vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:145-205]"]
    end
    
    subgraph "Conversion_Layer"
        TOJSON["ToJSON()<br/>[vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:96-101]"]
        UNMARSHAL["Unmarshal()<br/>[vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:35-62]"]
        SIGSYAML["sigs.k8s.io/yaml<br/>[go.mod:19]"]
    end
    
    subgraph "Output_Entities"
        K8SOBJECT["Kubernetes Objects<br/>(Pods, Services, CRDs)"]
        JSONBYTES["JSON []byte"]
        INTERFACE["interface{}"]
    end
    
    FILE --> READER
    BYTES --> GUESS
    READER --> GUESS
    
    GUESS -->|"Looks like JSON"| YAMLORJSON
    GUESS -->|"Looks like YAML"| YAMLORJSON
    
    YAMLORJSON -->|"JSON path"| UNMARSHAL
    YAMLORJSON -->|"YAML path"| YAMLTOJSON
    
    READER --> YAMLDECODER
    YAMLTOJSON --> SIGSYAML
    YAMLDECODER --> SIGSYAML
    
    TOJSON --> SIGSYAML
    SIGSYAML --> JSONBYTES
    
    UNMARSHAL --> K8SOBJECT
    YAMLTOJSON --> INTERFACE
    TOJSON --> JSONBYTES
    YAMLDECODER --> K8SOBJECT
```
**Sources:** [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:1-486](), [go.mod:1-20]()

---

## Core Decoder Types

### YAMLOrJSONDecoder

`YAMLOrJSONDecoder` is the primary entry point for processing manifests with unknown format [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:240-256](). It automatically detects whether the input stream contains JSON or YAML and switches to the appropriate internal decoder.

| Field | Type | Purpose |
|-------|------|---------|
| `json` | `*json.Decoder` | Used when stream is detected as JSON |
| `yaml` | `*YAMLToJSONDecoder` | Used when stream is YAML |
| `stream` | `*StreamReader` | Underlying stream reader with rewind capability |

**Key Methods:**
- `NewYAMLOrJSONDecoder(r io.Reader, bufferSize int)`: Creates a new decoder that auto-detects format [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:275-281]().
- `Decode(into interface{})`: Unmarshals the next object from the stream, handling format transitions [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:290-358]().

**Decoding Logic Flow**
```mermaid
graph TB
    START["Decode(into interface{})"]
    
    subgraph "Detection_Logic"
        CHECKJSON{"d.json != nil?"}
        TRYJSON["Try json.Decode()"]
        JSONSUCCESS{"Success?"}
        JSONEOF{"EOF?"}
    end
    
    subgraph "YAML_Fallback"
        EATWHITESPACE["consumeWhitespace()"]
        CREATEYAML["Create YAMLToJSONDecoder"]
        NILLJSON["Set json = nil"]
    end
    
    subgraph "YAML_Path"
        CHECKYAML{"d.yaml != nil?"}
        TRYYAML["Try yaml.Decode()"]
        YAMLSUCCESS{"Success?"}
    end
    
    START --> CHECKJSON
    CHECKJSON -->|Yes| TRYJSON
    TRYJSON --> JSONSUCCESS
    
    JSONSUCCESS -->|Yes| DONE["Return nil"]
    JSONSUCCESS -->|No| JSONEOF
    
    JSONEOF -->|No| EATWHITESPACE
    EATWHITESPACE --> CREATEYAML
    CREATEYAML --> NILLJSON
    
    CHECKJSON -->|No| CHECKYAML
    NILLJSON --> CHECKYAML
    
    CHECKYAML -->|Yes| TRYYAML
    TRYYAML --> YAMLSUCCESS
    YAMLSUCCESS -->|Yes| DONE
```
**Sources:** [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:290-358]()

### YAMLToJSONDecoder

`YAMLToJSONDecoder` processes YAML documents by converting each to JSON before unmarshaling [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:106-109](). This approach ensures consistency with Kubernetes' JSON-based API machinery.

- **Decode Method:** Reads a YAML document as JSON from the stream [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:125-139]().

### YAMLDecoder

`YAMLDecoder` splits YAML streams into individual documents based on the `---` separator [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:147-151](). It is specifically designed to handle large streams by using a `bufio.Scanner` with a 5MB buffer limit [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:163]().

**Sources:** [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:106-205]()

---

## Conversion Functions

### Direct YAML/JSON Conversion

The package provides high-level functions for converting between YAML and JSON without manually managing decoder state.

| Function | Signature | Purpose |
|----------|-----------|---------|
| `Unmarshal` | `(data []byte, v interface{}) error` | Unmarshals YAML with number preservation [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:38-62](). |
| `UnmarshalStrict` | `(data []byte, v interface{}) error` | Strict unmarshaling that errors on duplicate fields [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:66-90](). |
| `ToJSON` | `(data []byte) ([]byte, error)` | Converts a single YAML document to JSON [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:96-101](). |

**Number Preservation:**
When unmarshaling into `*map[string]interface{}` or `*interface{}`, the utility uses `d.UseNumber()` to ensure numbers are converted to `int64` or `float64` rather than losing precision [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:39-42]().

---

## Multi-Document Stream Processing

### YAML Document Separation

YAML streams use the `---` separator to delimit multiple documents. The decoder handles this using a custom `bufio.SplitFunc` named `splitYAMLDocument` [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:211-238]().

**Separator Detection Sequence**
```mermaid
sequenceDiagram
    participant S as Scanner
    participant F as splitYAMLDocument()
    
    S->>F: Provide data chunk
    Note over F: Search for "\n---" [line 216]
    
    alt Found separator
        Note over F: Check for newline after separator [line 227]
        F->>S: Return document segment
    else No separator found
        alt At EOF
            F->>S: Return remaining data
        else Not at EOF
            F->>S: Request more data (0, nil, nil)
        end
    end
```
**Sources:** [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:211-238]()

---

## Format Detection

### GuessJSONStream and IsJSONBuffer

The system detects JSON by identifying an opening brace `{` as the first non-whitespace character in the stream.

- **GuessJSONStream:** Peeks at the beginning of an `io.Reader` to determine if it "looks like" JSON [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:478-485]().
- **IsJSONBuffer:** Checks if a byte slice has the JSON object prefix `{` after trimming whitespace [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:463-466]().

**Sources:** [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:463-485]()

---

## Error Handling

The package defines specialized error types to provide context during parsing failures:

1.  **JSONSyntaxError:** Wraps a standard JSON syntax error and includes the byte `Offset` where the error occurred [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:258-262]().
2.  **YAMLSyntaxError:** Wraps errors returned by the underlying YAML parser [vendor/k8s.io/apimachinery/pkg/util/yaml/decoder.go:271-273]().

---

## Dependencies

The manifest processing logic relies on the following external modules:

| Dependency | Version | Role |
|------------|---------|------|
| `sigs.k8s.io/yaml` | `v1.6.0` | Primary YAML/JSON conversion library [go.mod:19](). |
| `k8s.io/apimachinery` | `v0.36.3` | Provides the `pkg/util/yaml` utility package [go.mod:14](). |

**Sources:** [go.mod:1-20](), [vendor/modules.txt:1-550]()

---

# Page: Logging and Observability

# Logging and Observability

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [vendor/k8s.io/klog/v2/README.md](vendor/k8s.io/klog/v2/README.md)
- [vendor/k8s.io/klog/v2/internal/serialize/keyvalues.go](vendor/k8s.io/klog/v2/internal/serialize/keyvalues.go)
- [vendor/k8s.io/klog/v2/internal/serialize/keyvalues_no_slog.go](vendor/k8s.io/klog/v2/internal/serialize/keyvalues_no_slog.go)
- [vendor/k8s.io/klog/v2/internal/serialize/keyvalues_slog.go](vendor/k8s.io/klog/v2/internal/serialize/keyvalues_slog.go)
- [vendor/k8s.io/klog/v2/klog.go](vendor/k8s.io/klog/v2/klog.go)
- [vendor/k8s.io/klog/v2/klogr.go](vendor/k8s.io/klog/v2/klogr.go)
- [vendor/k8s.io/klog/v2/klogr_slog.go](vendor/k8s.io/klog/v2/klogr_slog.go)

</details>



This page documents the logging infrastructure and observability practices used in the `k8s-test-infra` repository. It covers the primary logging library (`klog/v2`), configuration options, structured logging patterns, and integration with standard logging interfaces.

For information about test output and reporting, see [Test Reporting and Output](#5.4). For CI/CD observability and monitoring, see [GitHub Actions Workflows](#4.1).

---

## Overview

The `k8s-test-infra` repository uses **klog/v2** as its primary logging library, providing leveled, structured logging with extensive configuration options. The logging system integrates with the `go-logr` interface and supports modern `slog` handlers (Go 1.21+), enabling flexible backend selection and consistent logging patterns across Kubernetes components.

**Key Features:**
- Leveled logging with verbosity controls via `V()` levels [vendor/k8s.io/klog/v2/klog.go:98-99]().
- Structured logging with key-value pairs using `InfoS` and `ErrorS` [vendor/k8s.io/klog/v2/klog.go:21-21]().
- Command-line flag configuration through `InitFlags` [vendor/k8s.io/klog/v2/klog.go:19-19]().
- Per-file/module verbosity filtering via `-vmodule` [vendor/k8s.io/klog/v2/klog.go:100-105]().
- Integration with `go-logr` and `slog` [vendor/k8s.io/klog/v2/klogr_slog.go:36-45]().
- Buffered output routing with `Flush` guarantees [vendor/k8s.io/klog/v2/klog.go:52-53]().

**Sources:** [vendor/k8s.io/klog/v2/klog.go:1-116](), [vendor/k8s.io/klog/v2/klogr_slog.go:36-45]()

---

## Logging Architecture

The following diagram illustrates the logging stack and how different components interact:

### Logging System Stack
```mermaid
graph TB
    subgraph "Application Code"
        APP["Application Code<br/>Tests, Main Programs"]
    end
    
    subgraph "Logging Interface Layer"
        KLOG["klog/v2 API<br/>Info, InfoS, V()"]
        LOGR["go-logr Interface<br/>logr.Logger"]
        SLOG["slog Handler<br/>Go 1.21+ Integration"]
    end
    
    subgraph "klog Core Implementation"
        LOGGING["loggingT struct<br/>Global logging state"]
        SETTINGS["settings struct<br/>Configuration"]
        FORMATTER["Header Formatter<br/>formatHeader()"]
        BUFFER["Buffer Pool<br/>buffer.GetBuffer()"]
    end
    
    subgraph "Output Routing"
        STDERR["Standard Error<br/>-logtostderr flag"]
        FILES["Log Files<br/>-log_dir flag"]
        SEVERITY["Severity-based<br/>-stderrthreshold"]
    end
    
    subgraph "Filtering & Control"
        VERBOSITY["Verbosity Level<br/>-v flag"]
        VMODULE["Per-file Filter<br/>-vmodule flag"]
        SERIALIZE["serialize.FormatKVs<br/>Deduplication"]
    end
    
    APP --> KLOG
    APP --> LOGR
    APP --> SLOG
    
    KLOG --> LOGGING
    LOGR --> LOGGING
    SLOG --> LOGGING
    
    LOGGING --> SETTINGS
    LOGGING --> FORMATTER
    LOGGING --> BUFFER
    
    LOGGING --> VERBOSITY
    LOGGING --> VMODULE
    LOGGING --> SERIALIZE
    
    FORMATTER --> STDERR
    FORMATTER --> FILES
    FORMATTER --> SEVERITY
```

**Key Components:**

| Component | Description | Key Code Entities |
|-----------|-------------|-------------------|
| **klog API** | Primary logging interface | `Info()`, `InfoS()`, `V()`, `ErrorS()` |
| **loggingT** | Global logging state manager | `logging` global variable [vendor/k8s.io/klog/v2/klog.go:52-53]() |
| **KV Formatting** | Logic for serializing key-value pairs | `serialize.FormatKVs` [vendor/k8s.io/klog/v2/internal/serialize/keyvalues.go:64-66]() |
| **slog Integration** | Bridges Go standard slog to klog | `slogOutput` [vendor/k8s.io/klog/v2/klogr_slog.go:50-83]() |

**Sources:** [vendor/k8s.io/klog/v2/klog.go:17-37](), [vendor/k8s.io/klog/v2/internal/serialize/keyvalues.go:70-135](), [vendor/k8s.io/klog/v2/klogr_slog.go:50-83]()

---

## Child Pages

For deep technical details on specific logging topics, refer to the following sub-pages:

### [klog Integration](#7.1)
Detailed documentation on:
- **Flag Configuration**: Using `InitFlags` to register klog settings [vendor/k8s.io/klog/v2/klog.go:19-19]().
- **Verbosity Levels**: Managing the `-v` and `-vmodule` flags for fine-grained control [vendor/k8s.io/klog/v2/klog.go:98-105]().
- **Interface Bridging**: How `NewKlogr` creates a `logr.Logger` that targets klog [vendor/k8s.io/klog/v2/klogr.go:33-35]().
- **Contextual Logging**: Passing loggers through `context.Context` using `FromContext` [vendor/k8s.io/klog/v2/klog.go:24-27]().

### [Structured Logging Practices](#7.2)
Detailed documentation on:
- **InfoS/ErrorS Usage**: Best practices for using message strings and key-value pairs [vendor/k8s.io/klog/v2/klog.go:21-21]().
- **Serialization**: How `serialize.FormatKVs` handles de-duplication ("last one wins") [vendor/k8s.io/klog/v2/internal/serialize/keyvalues.go:70-73]().
- **Type Handling**: Serialization logic for `fmt.Stringer`, `error`, and `slog.LogValuer` [vendor/k8s.io/klog/v2/internal/serialize/keyvalues_slog.go:60-100]().
- **Plugin Logging**: Specific patterns used in the `nvml-mock-nri` plugin for container runtime observability.

---

## Structured Log Processing

When using structured logging, klog utilizes the `serialize` package to format output. This includes a de-duplication mechanism where if a key is repeated in the key-value list, the last occurrence is preserved.

### Key-Value Serialization Logic
```mermaid
graph LR
    subgraph "Input Pairs"
        KV["[k1, v1, k2, v2, k1, v3]"]
    end
    
    subgraph "serialize.FormatKVs"
        PROC["Iterate Pairs"]
        DEDUP["De-duplication Logic<br/>'Last one wins'"]
        BUF["bytes.Buffer"]
    end
    
    subgraph "Final Output"
        OUT["k2=v2 k1=v3"]
    end
    
    KV --> PROC
    PROC --> DEDUP
    DEDUP --> BUF
    BUF --> OUT
```

**Implementation Detail:**
The `FormatKVs` function in `vendor/k8s.io/klog/v2/internal/serialize/keyvalues.go` tracks `obsoleteKV` entries to cut out redundant output from the buffer when a key is overwritten by a subsequent pair [vendor/k8s.io/klog/v2/internal/serialize/keyvalues.go:70-135]().

**Sources:** [vendor/k8s.io/klog/v2/internal/serialize/keyvalues.go:70-167](), [vendor/k8s.io/klog/v2/internal/serialize/keyvalues_slog.go:33-51]()

---

## Logging in Tests

In the `k8s-test-infra` codebase, logging is critical for debugging E2E failures. Tests typically use the `klog.Background()` logger or standard `klog.InfoS` calls. Programs must call `klog.Flush()` before exiting to ensure all buffered logs are written to the output stream [vendor/k8s.io/klog/v2/klog.go:52-53]().

For unit tests, `k8s.io/klog/v2/ktesting` provides per-test output isolation [vendor/k8s.io/klog/v2/klog.go:32-32]().

**Sources:** [vendor/k8s.io/klog/v2/klog.go:32-53](), [vendor/k8s.io/klog/v2/klogr.go:55-59]()

---

# Page: klog Integration

# klog Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [vendor/github.com/go-logr/logr/README.md](vendor/github.com/go-logr/logr/README.md)
- [vendor/github.com/go-logr/logr/funcr/funcr.go](vendor/github.com/go-logr/logr/funcr/funcr.go)
- [vendor/github.com/onsi/ginkgo/v2/ginkgo/build/build_command.go](vendor/github.com/onsi/ginkgo/v2/ginkgo/build/build_command.go)
- [vendor/github.com/onsi/ginkgo/v2/ginkgo/internal/compile.go](vendor/github.com/onsi/ginkgo/v2/ginkgo/internal/compile.go)
- [vendor/k8s.io/klog/v2/OWNERS](vendor/k8s.io/klog/v2/OWNERS)
- [vendor/k8s.io/klog/v2/README.md](vendor/k8s.io/klog/v2/README.md)
- [vendor/k8s.io/klog/v2/contextual_slog.go](vendor/k8s.io/klog/v2/contextual_slog.go)
- [vendor/k8s.io/klog/v2/internal/serialize/keyvalues.go](vendor/k8s.io/klog/v2/internal/serialize/keyvalues.go)
- [vendor/k8s.io/klog/v2/internal/serialize/keyvalues_no_slog.go](vendor/k8s.io/klog/v2/internal/serialize/keyvalues_no_slog.go)
- [vendor/k8s.io/klog/v2/internal/serialize/keyvalues_slog.go](vendor/k8s.io/klog/v2/internal/serialize/keyvalues_slog.go)
- [vendor/k8s.io/klog/v2/klog.go](vendor/k8s.io/klog/v2/klog.go)
- [vendor/k8s.io/klog/v2/klogr.go](vendor/k8s.io/klog/v2/klogr.go)
- [vendor/k8s.io/klog/v2/klogr_slog.go](vendor/k8s.io/klog/v2/klogr_slog.go)
- [vendor/k8s.io/klog/v2/safeptr.go](vendor/k8s.io/klog/v2/safeptr.go)

</details>



## Purpose and Scope

This document describes how the k8s-test-infra project uses **klog** (the Kubernetes Logging Library) for logging and observability. It covers the detailed configuration of klog, verbosity levels, output routing, and its integration with modern structured logging interfaces such as **go-logr** and **slog**.

klog is a vendored dependency from `k8s.io/klog/v2` and serves as the primary logging mechanism for test infrastructure components and the nv-ci-bot application within the k8s-test-infra ecosystem.

---

## klog Architecture

klog provides a leveled logging system with multiple output destinations and fine-grained filtering capabilities. The architecture revolves around a global singleton `logging` of type `loggingT` that owns all state including output writers, verbosity settings, location filters, and file handles.

```mermaid
graph TB
    subgraph "klog Global State"
        LOGGING["loggingT<br/>(logging)"]
        SETTINGS["settings<br/>(in loggingT)"]
        FLAGS["flag.FlagSet<br/>(commandLine)"]
    end
    
    subgraph "Configuration Parameters"
        VERBOSITY["Level<br/>(verbosity)"]
        VMODULE["moduleSpec<br/>(vmodule)"]
        SEVERITY["severityValue<br/>(stderrthreshold)"]
        TRACEAT["traceLocation<br/>(log_backtrace_at)"]
    end
    
    subgraph "Output Destinations"
        STDERR["os.Stderr"]
        FILES["Log Files (per severity)"]
        LOGGER["logWriter<br/>(custom logger)"]
    end
    
    subgraph "Logging APIs"
        TRADITIONAL["Info, Error, Warning, Fatal<br>Infof, Errorf, etc."]
        STRUCTURED["InfoS, ErrorS<br>(structured)"]
        VERBOSITY_API["V(level).Info()"]
        GO_LOGR["Background(), TODO() (go-logr integration)"]
    end
    
    LOGGING --> SETTINGS
    SETTINGS --> VERBOSITY
    SETTINGS --> VMODULE
    SETTINGS --> SEVERITY
    SETTINGS --> TRACEAT
    
    FLAGS -.-> VERBOSITY
    FLAGS -.-> VMODULE
    FLAGS -.-> SEVERITY
    
    TRADITIONAL --> LOGGING
    STRUCTURED --> LOGGING
    VERBOSITY_API --> LOGGING
    GO_LOGR --> LOGGING
    
    LOGGING --> STDERR
    LOGGING --> FILES
    LOGGING --> LOGGER
```

- The `loggingT` struct holds all runtime state: log destinations, filters, verbosity, file handles, mutex for concurrency, and statistics.
- Configuration options are typically set via command-line flags registered on a flag.FlagSet.
- Multiple logging APIs coexist: traditional unstructured logging (Info, Error, etc.), verbosity-controlled logs (`V(level)`), structured logging (`InfoS`), and integration with `go-logr`.

**Sources:** [vendor/k8s.io/klog/v2/klog.go:400-560]()

---

## Configuration and Initialization

### Flag Registration

klog logging flags must be initialized explicitly by calling:

```go
klog.InitFlags(flag.CommandLine)
```

This registers all klog-related flags into the provided `flag.FlagSet`. Flags then need to be parsed via `flag.Parse()` before logging begins.

| Function | Description | Typical Usage |
|----------|-------------|---------------|
| `InitFlags(flagset)` | Register klog CLI flags to a flag set | Called once at program startup |
| `init()` | Internal init (does not register flags) | Automatic |

**Sources:** [vendor/k8s.io/klog/v2/klog.go:436-449]()

### Command-Line Flags Overview

klog offers a rich set of flags controlling output routing, verbosity, formatting, and debugging aids. Flags are categorized as follows:

```mermaid
graph LR
    subgraph "Output Routing Flags"
        LOGTOSTDERR["-logtostderr (default: true)"]
        ALSOLOGTOSTDERR["-alsologtostderr (default: false)"]
        STDERRTHRESHOLD["-stderrthreshold (default: ERROR)"]
        LOGDIR["-log_dir"]
        LOGFILE["-log_file"]
    end
    
    subgraph "Verbosity Control Flags"
        V["-v (level number)"]
        VMODULE["-vmodule (pattern=N,...)"]
    end
    
    subgraph "Formatting Flags"
        SKIPHEADERS["-skip_headers"]
        SKIPLOGHEADERS["-skip_log_headers"]
        ADDDIRHEADER["-add_dir_header"]
        ONEOUTPUT["-one_output"]
    end
    
    subgraph "Debugging Flags"
        BACKTRACE["-log_backtrace_at (file:line)"]
    end
```

#### Output Routing Flags

| Flag                 | Type   | Default | Description                                                  |
|----------------------|--------|---------|--------------------------------------------------------------|
| `-logtostderr`       | bool   | true    | Log output goes to stderr rather than files                   |
| `-alsologtostderr`   | bool   | false   | Log to stderr in addition to files                            |
| `-stderrthreshold`   | severity| ERROR  | Severity threshold for logging to stderr                      |
| `-log_dir`           | string | ""      | Directory where to write log files (ignored if -logtostderr) |
| `-log_file`          | string | ""      | Direct log file path (single file, ignored with -logtostderr)|
| `-log_file_max_size` | uint64 | 1800    | Max size (MB) before rotating log files                       |

#### Verbosity Control Flags

| Flag        | Type    | Default | Description                                             |
|-------------|---------|---------|---------------------------------------------------------|
| `-v`        | Level   | 0       | Global verbosity level controlling V-enabled logs       |
| `-vmodule`  | string  | ""      | Per-file verbosity control with glob-patterns           |

The `-vmodule` flag enables specifying verbosity overrides by file name patterns (e.g., `gopher*=3,file=1`).

#### Debugging Flags

| Flag               | Type   | Description                              |
|--------------------|--------|----------------------------------------|
| `-log_backtrace_at` | string | Emit stack trace when given file and line is logged |

#### Formatting Flags

| Flag              | Type   | Description                            |
|-------------------|--------|--------------------------------------|
| `-skip_headers`   | bool   | Skip header prefixes on log lines    |
| `-skip_log_headers`| bool  | Skip headers specifically for files  |
| `-add_dir_header` | bool   | Include directory prefix in log lines|
| `-one_output`     | bool   | Write only to original severity file |

**Sources:** [vendor/k8s.io/klog/v2/klog.go:59-90](), [vendor/k8s.io/klog/v2/klog.go:412-429](), [vendor/k8s.io/klog/v2/klog.go:430]()

---

## Verbosity Levels and Filtering

### Verbosity-Based Logging

klog uses integer levels for verbosity control, where higher numbers mean more verbose output.

Code typically checks:

```go
if klog.V(2) {
    klog.Info("Starting transaction...")
}

klog.V(2).Info("Processed", nItems, "elements")
```

This delays potentially expensive log message generation until the verbosity check passes.

### Verbosity Evaluation Flow

```mermaid
graph TB
    CheckV["klog.V(level) called"] --> IsEnabled{"Is level enabled?"}
    IsEnabled -->|Yes| LogOutput["Perform logging"]
    IsEnabled -->|No| NoOp["Skip logging"]
    
    IsEnabled --> CheckGlobal["Compare to global -v flag"]
    IsEnabled --> CheckVmodule["Check -vmodule overrides"]
    
    CheckVmodule --> VmapCache["Lookup PC in vmap cache"]
    CheckGlobal --> VlevelAtomic["Atomic load of global verbosity"]
```

- The global verbosity level is stored atomically.
- Per-file `-vmodule` settings use a compiled cache of program counters to levels for speed.
- The `V()` method returns a `Verbose` object with an `Enabled()` method to avoid log message evaluation when disabled.

### Per-file Filtering (`-vmodule`)

`-vmodule` uses glob patterns to specify different verbosity levels per source file:

| Pattern | Example      | Matches                        |
|---------|--------------|--------------------------------|
| Literal | `file=3`     | Only `file.go`                  |
| Glob    | `gopher*=3`  | `gopher.go`, `gopherflakes.go` |
| Multiple| `recordio=2,file=1,gfs*=3` | Multiple file patterns   |

This allows fine-grained control for troubleshooting specific components.

**Sources:** [vendor/k8s.io/klog/v2/klog.go:44-50](), [vendor/k8s.io/klog/v2/klog.go:217-331]()

---

## Output Routing and Formatting

### Output Routing Logic

Log entries are routed based on configuration and severity:

```mermaid
graph TD
    LogEntry["Log Entry (severity, msg)"]
    CheckLogger{"Custom logger set?"}
    ToStderrFlag{"-logtostderr flag?"}
    AlsoToStderrOrThreshold{"-alsologtostderr or severity >= -stderrthreshold?"}
    
    LogEntry --> CheckLogger
    CheckLogger -->|Yes| CustomLogger["logWriter (custom)"]
    CheckLogger -->|No| ToStderrFlag
    
    ToStderrFlag -->|Yes| OsStderr["os.Stderr"]
    ToStderrFlag -->|No| AlsoToStderrOrThreshold
    
    AlsoToStderrOrThreshold -->|Yes| OsStderr
    AlsoToStderrOrThreshold -->|No| FileOutput["File output per severity"]
    
    FileOutput --> InfoFile["INFO file"]
    FileOutput --> WarnFile["WARNING file"]
    FileOutput --> ErrorFile["ERROR file"]
    FileOutput --> FatalFile["FATAL file"]
```

- If a custom logger is installed, all logs delegate there.
- Otherwise, logs go to stderr if enabled or to per-severity files.
- `-alsologtostderr` controls duplicate logging to stderr alongside files.

### Log Format

klog log lines follow a consistent format, for example:

```
I1204 10:30:45.123456 12345 file.go:42] "User logged in" username="alice" duration="2.5s"
```

Where:

| Symbol  | Meaning                             |
|---------|-----------------------------------|
| `I`     | Severity character (Info)          |
| `1204`  | Month and day (MMDD)               |
| `10:30:45.123456` | Timestamp with microsecond precision |
| `12345` | Thread/Goroutine ID (space-padded)|
| `file.go:42` | Source file and line number     |
| Message | Log text or structured key-value pairs |

### Severity Levels

| Severity      | Numeric | Character | Usage                    |
|---------------|---------|-----------|--------------------------|
| InfoLog       | 0       | `I`       | Informational messages   |
| WarningLog    | 1       | `W`       | Warnings                 |
| ErrorLog      | 2       | `E`       | Errors                   |
| FatalLog      | 3       | `F`       | Fatal errors (exit)      |

**Sources:** [vendor/k8s.io/klog/v2/klog.go:630-680](), [vendor/k8s.io/klog/v2/klog.go:185-189]()

---

## Logging API

### Traditional Logging Functions

klog provides familiar, printf-like functions:

| Function Pattern | Example                                |
|------------------|--------------------------------------|
| `Info(args...)`  | `klog.Info("Server started")`         |
| `Infof(fmt, ...)`| `klog.Infof("Port: %d", port)`        |
| `Infoln(args...)`| `klog.Infoln("Item", value)`          |
| `Warning(args...)`| `klog.Warning("Deprecated API")`     |
| `Error(args...)` | `klog.Error("Failed connection")`    |
| `Fatal(args...)` | `klog.Fatal("Cannot continue")`      |

Each has raw, formatted, and line-ending variants (`X`, `Xf`, `Xln`).

### Structured Logging Functions

For structured logs with key-value pairs:

| Function | Signature                                         |
|----------|-------------------------------------------------|
| `InfoS`  | `InfoS(msg string, keysAndValues ...interface{})` |
| `ErrorS` | `ErrorS(err error, msg string, keysAndValues ...interface{})` |

Example log line with key-value pairs:

```
I1204 10:30:45.123456 12345 file.go:42] "User logged in" username="alice" role="admin" duration="2.5s"
```

```mermaid
graph LR
    InfoS["InfoS(msg, kvs...)"]
    ErrorS["ErrorS(err, msg, kvs...)"]
    QuotedMsg["Quoted message"]
    KVpairs["key=value pairs"]
    
    InfoS --> QuotedMsg
    InfoS --> KVpairs
    ErrorS --> QuotedMsg
    ErrorS --> KVpairs
```

### Verbosity-Based API

`V(level)` returns a `Verbose` object with conditional logging:

```go
if klog.V(2) {
    klog.Info("Debug info only when verbosity >= 2")
}

klog.V(3).Infof("Extra details: %v", data)
```

This avoids runtime cost of interpolated messages when verbosity is lower.

**Sources:** [vendor/k8s.io/klog/v2/klog.go:38-50](), [vendor/k8s.io/klog/v2/klog.go:780-825]()

---

## go-logr Integration

klog integrates with the [go-logr](https://github.com/go-logr/logr) API, allowing it to be used as a logr backend or delegate to other logr implementations.

### Architecture Overview

```mermaid
graph TB
    subgraph "klog as go-logr Provider"
        BACKGROUND["Background() --> logr.Logger"]
        TODO["TODO() --> logr.Logger"]
        SETLOGGER["SetLogger(logr.Logger)"]
    end
    
    subgraph "Log Routing"
        KLOG_API["klog.Info(), klog.InfoS()"]
        HAS_LOGGER{"logger set?"}
        DELEGATE_LOGR["Delegate to logr.Logger"]
        NATIVE_KLOG["Native klog output"]
    end
    
    subgraph "logWriter"
        LOGWRITER["logWriter struct"]
        LOGR_LOGGER["logr.Logger wrapped"]
        CALL_DEPTH["CallDepth adjustment"]
    end
    
    BACKGROUND --> LOGWRITER
    TODO --> LOGWRITER
    SETLOGGER -.-> LOGWRITER
    
    LOGWRITER --> LOGR_LOGGER
    LOGWRITER --> CALL_DEPTH
    
    KLOG_API --> HAS_LOGGER
    HAS_LOGGER -->|Yes| DELEGATE_LOGR
    HAS_LOGGER -->|No| NATIVE_KLOG
```

### Key Functions and Usage

| Function              | Description                        | Use Case                             |
|-----------------------|----------------------------------|------------------------------------|
| `Background()`        | Returns global logr.Logger        | Default logger use                  |
| `TODO()`              | Returns temporary logr.Logger     | Placeholder, for incremental use   |
| `SetLogger(logger)`   | Installs custom logr.Logger       | Integrate external logger backend   |
| `SetLoggerWithOptions`| Installs logr.Logger with options | Advanced customization              |

The `logWriter` type adapts between klog and logr with call depth management.

### Logger Options

`loggerOptions` allow control such as:

- enabling contextual logging
- using klog's buffer formatter vs native logr formatting

**Sources:** [vendor/k8s.io/klog/v2/klog.go:17-28](), [vendor/k8s.io/klog/v2/klog.go:450-470]()

---

## slog Integration (Go 1.21+)

With Go 1.21+, klog integrates with the new standard library `log/slog` package providing modern structured logging.

### Integration Flow

```mermaid
graph LR
    SETSLOG["SetSlogLogger(*slog.Logger)"]
    SLOGHANDLER["slog.Handler interface"]
    LOGR_FROM_SLOG["logr.FromSlogHandler()"]
    SETLOG_OPTS["SetLoggerWithOptions()"]
    CONTEXTUAL["ContextualLogger(true)"]
    
    SETSLOG --> SLOGHANDLER
    SLOGHANDLER --> LOGR_FROM_SLOG
    LOGR_FROM_SLOG --> SETLOG_OPTS
    CONTEXTUAL --> SETLOG_OPTS
```

- `SetSlogLogger` converts an `*slog.Logger` to a `logr.Logger` adapted for klog.
- It installs this as the global klog logger with contextual logging enabled.

```go
func SetSlogLogger(logger *slog.Logger) {
    SetLoggerWithOptions(logr.FromSlogHandler(logger.Handler()), ContextualLogger(true))
}
```

### slogSink Implementation

The internal `klogger` type implements the `logr.SlogSink` interface for compatibility:

| Method             | Purpose                       |
|--------------------|-------------------------------|
| `Handle(ctx, record)` | Handles a slog.Record upon log |
| `WithAttrs(attrs)`     | Adds attributes (key-values)   |
| `WithGroup(name)`      | Adds grouping to the logger    |

This allows klog to interoperate cleanly with slog-style structured logging.

**Sources:** [vendor/k8s.io/klog/v2/contextual_slog.go:22-35](), [vendor/k8s.io/klog/v2/klogr_slog.go:36-97]()

---

## State Management

### CaptureState and Restore

klog supports capturing its current state snapshot, useful in tests and advanced reconfiguration:

```mermaid
graph LR
    CaptureState["CaptureState() returns State interface"]
    StateObj["State implementation: stores settings snapshot"]
    Restore["State.Restore() applies settings"]
    ControlFlush["Starts/stops flush daemon, sets max log size"]
    
    CaptureState --> StateObj
    StateObj --> Restore
    Restore --> ControlFlush
```

- `CaptureState()` snapshots all global flags and runtime values atomically.
- `State.Restore()` restores those settings and controls the background flush daemon accordingly.

Use case: testing code can isolate klog config changes and restore after tests.

### Flush Control

| Function           | Description                             |
|--------------------|---------------------------------------|
| `Flush()`          | Flush all buffered logs to outputs    |
| `FlushAndExit(c)`  | Flush and then exit the process with code `c` |

Programs should call `Flush()` before exit to ensure all log output is persisted.

**Sources:** [vendor/k8s.io/klog/v2/klog.go:580-630](), [vendor/k8s.io/klog/v2/klog.go:450-460]()

---

## Usage in k8s-test-infra

### Initialization Pattern

The common way to initialize klog in k8s-test-infra is:

```go
import (
    "flag"
    "k8s.io/klog/v2"
)

func main() {
    klog.InitFlags(nil)   // Register klog flags in flag.CommandLine
    flag.Parse()          // Parse all flags
    defer klog.Flush()    // Ensure all logs are flushed on exit
    
    // Main program logic
}
```

### Typical Configuration

Based on Kubernetes ecosystem norms, example configurations include:

| Scenario        | Flags                        | Description                 |
|-----------------|------------------------------|-----------------------------|
| Development     | `-v=4 -logtostderr`           | Verbose output to console    |
| Production      | `-v=2 -log_dir=/var/log`      | Moderate logging to files    |
| Testing         | `-v=5 -logtostderr`           | Maximum verbosity on console |
| CI/CD           | `-v=2 -logtostderr`           | Standard log capture stdout/stderr |

### Integration with Ginkgo Testing

In Ginkgo tests (detailed in section 5), klog is often set to log to GinkgoWriter to capture logs alongside test output:

```go
BeforeEach(func() {
    klog.SetOutput(GinkgoWriter)
})
```

This allows Kubernetes-style logs to appear in test reports.

---

## Performance Considerations

- Verbosity checks use atomic loads and a program counter-based cache (`vmap`) for fast per-callsite verbosity evaluation.
- Buffered output is pooled via `buffer.GetBuffer()` and `buffer.PutBuffer()` for reduced allocations.
- Output stats (line and byte counts) are tracked atomically per severity.
- All global state changes and output are mutex-protected for thread safety.

---

## Thread Safety

klog is safe for concurrent use:

- Global verbosity and severity thresholds use atomic operations.
- Output functions lock the global mutex to serialize access.
- State snapshot and restoration are mutex-protected.

---

## Special Features

- **Stack Traces:** Trigger a stack backtrace on specified file:line via `-log_backtrace_at`.
- **File Rotation:** Log files are auto-rotated once reaching max size configured by `-log_file_max_size`.
- **Safe Pointer Logging:** `SafePtr` helper prevents nil pointer dereference during `fmt.Stringer` calls.

---

## Summary

The integration of klog within k8s-test-infra enables:

- Flexible, flag-driven logging configuration.
- Fine-grained verbosity control globally and per file.
- Multiple destination support: stderr, files, and custom loggers.
- Support for traditional and structured logging APIs.
- Seamless integration with `go-logr` and Go 1.21+ `slog`.
- Thread-safe, performant logging suitable for complex test and CI infrastructure.

This consistent logging foundation ensures observability and diagnostics across the system compatible with Kubernetes ecosystem standards.

---

# References

- Core klog source: [vendor/k8s.io/klog/v2/klog.go:1-1130]()
- go-logr bridge: [vendor/k8s.io/klog/v2/klogr.go:1-110]()
- slog integration: [vendor/k8s.io/klog/v2/klogr_slog.go:1-102](), [vendor/k8s.io/klog/v2/contextual_slog.go:20-38]()
- Key-value serialization with/without slog: [vendor/k8s.io/klog/v2/internal/serialize/keyvalues_slog.go:1-160](), [vendor/k8s.io/klog/v2/internal/serialize/keyvalues_no_slog.go:1-102]()
- klog README explanatory text: [vendor/k8s.io/klog/v2/README.md:1-117]()

---

# Page: Structured Logging Practices

# Structured Logging Practices

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cmd/nvml-mock-nri/health.go](cmd/nvml-mock-nri/health.go)
- [cmd/nvml-mock-nri/health_test.go](cmd/nvml-mock-nri/health_test.go)
- [cmd/nvml-mock-nri/main.go](cmd/nvml-mock-nri/main.go)
- [deployments/nvml-mock/helm/nvml-mock/templates/nri-daemonset.yaml](deployments/nvml-mock/helm/nvml-mock/templates/nri-daemonset.yaml)
- [deployments/nvml-mock/helm/nvml-mock/tests/nri_daemonset_test.yaml](deployments/nvml-mock/helm/nvml-mock/tests/nri_daemonset_test.yaml)
- [tests/e2e/go/scenario_nri_test.go](tests/e2e/go/scenario_nri_test.go)
- [vendor/k8s.io/klog/v2/README.md](vendor/k8s.io/klog/v2/README.md)
- [vendor/k8s.io/klog/v2/internal/serialize/keyvalues.go](vendor/k8s.io/klog/v2/internal/serialize/keyvalues.go)
- [vendor/k8s.io/klog/v2/internal/serialize/keyvalues_no_slog.go](vendor/k8s.io/klog/v2/internal/serialize/keyvalues_no_slog.go)
- [vendor/k8s.io/klog/v2/internal/serialize/keyvalues_slog.go](vendor/k8s.io/klog/v2/internal/serialize/keyvalues_slog.go)
- [vendor/k8s.io/klog/v2/klog.go](vendor/k8s.io/klog/v2/klog.go)
- [vendor/k8s.io/klog/v2/klogr.go](vendor/k8s.io/klog/v2/klogr.go)
- [vendor/k8s.io/klog/v2/klogr_slog.go](vendor/k8s.io/klog/v2/klogr_slog.go)

</details>



## Purpose and Scope

This page documents structured logging practices employed in the [k8s-test-infra](https://github.com/NVIDIA/k8s-test-infra) repository, focusing on the use of klog's structured logging APIs (`InfoS`, `ErrorS`) for emitting logs with key-value pairs. Structured logging enables better log parsing, filtering, and analysis compared to traditional format string logging.

It covers details of InfoS/ErrorS usage, key-value formatting conventions, and concrete logging examples in both tests and the critical nvml-mock-nri plugin. The content assumes familiarity with Go, Kubernetes logging conventions, and the nvml-mock GPU simulation system.

For klog configuration, verbosity levels, and its integration with go-logr and slog, see [klog Integration (#7.1)].

**Sources:**  
- [vendor/k8s.io/klog/v2/klog.go:1-91]()  
- [cmd/nvml-mock-nri/main.go:4-89]()  
- [tests/e2e/go/scenario_nri_test.go:1-160]()  
- [cmd/nvml-mock-nri/health.go:14-193]()  
- [vendor/k8s.io/klog/v2/klogr_slog.go:20-84]()  

## Structured vs Unstructured Logging

The repository uses klog/v2, which supports both unstructured (printf-style) and structured (key-value pairs) logging.

| Approach       | Function           | Example                                                      | Best Use Case                         |
| -------------- | ------------------ | ------------------------------------------------------------ | ----------------------------------- |
| **Unstructured** | `Info()`, `Infof()`, `Error()`, `Errorf()` | `klog.Infof("processing pod %s in namespace %s", pod, ns)`   | Simple logs, quick debugging, legacy|
| **Structured**   | `InfoS()`, `ErrorS()`                    | `klog.InfoS("Processing pod", "pod", pod, "namespace", ns)` | Production logs, observability, parsing-friendly |

Structured logging outputs a constant message string paired with zero or more key-value pairs, which improves parsing precision, consistency in logs, and aids automated log processing.

## InfoS and ErrorS: Structured Logging APIs

### Function Signatures

The key structured logging calls used are:

```go
// InfoS logs a structured info message.
// msg is a constant message string (no format specifiers).
// keysAndValues are alternating key and value pairs.
func InfoS(msg string, keysAndValues ...interface{})

// ErrorS logs a structured error message.
// err is the error to log (can be nil).
// msg is a constant message string.
// keysAndValues are alternating key and value pairs.
func ErrorS(err error, msg string, keysAndValues ...interface{})
```

The `InfoS` and `ErrorS` APIs discourage printf-style formatting, instead encouraging explicit message strings and contextual key-value pairs.

### Example Usage

```go
klog.InfoS("Pod started", "pod", podName, "namespace", ns)
klog.ErrorS(err, "Failed to create pod", "pod", podName, "namespace", ns)
```

### Key-Value Pair Formatting

Internally, the key-value pairs are serialized into a parseable string of the form:

```
key1=value1 key2="value2" ...
```

All keys are assumed to be strings, and values may be strings, numbers, booleans, durations, errors, or custom types with stringers.

```mermaid
graph LR
    UserCode["User Code (InfoS/ErrorS call)"] --> KlogAPI["klog.InfoS / klog.ErrorS"]
    KlogAPI --> Serializer["serialize.KVListFormat"]
    Serializer --> Buffer["buffer.Buffer (pooled buffer)"]
    Buffer --> Output["Formatted log line output"]
    
    Serializer -.->|"key1, val1, key2, val2"| KVPairs["Key-Value Pairs"]
    KVPairs --> Format["key1=val1 key2=\"val2\""]
```

**Sources:**  
- [vendor/k8s.io/klog/v2/klog.go:17-36]()  
- [vendor/k8s.io/klog/v2/klogr_slog.go:50-80]()  

## Structured Logging Data Flow

### Logging Pipeline

```mermaid
graph TB
    A["klog.InfoS/ErrorS call"] --> B{"Is custom logger installed?"}
    B -- No --> C["Use klog built-in logging"]
    C --> D["Get pooled buffer"]
    D --> E["Quote message string"]
    E --> F{"Is error present?"}
    F -- Yes --> G["Format error key-value: 'err', err"]
    F -- No --> H["Format key-value pairs"]
    G --> H
    H --> I["Format header (severity, file, line)"]
    I --> J["Output formatted log line (stderr/file)"]
    B -- Yes --> K["Delegate to logger.Info/Error with kv pairs"]
    J --> L["Done"]
    K --> L
```

- If no logger backend is installed, klog formats and writes logs directly with headers and serialized key-values.  
- With a logger backend (logr or slog), klog delegates to that logger, allowing contextual logging and unified output.

**Sources:**  
- [vendor/k8s.io/klog/v2/klogr_slog.go:50-80]()  
- [vendor/k8s.io/klog/v2/klog.go:652-679]()  

## Key-Value Pair Formatting and Best Practices

### Naming Conventions

| Key Name Category | Examples                        | Notes                                |
|-------------------|--------------------------------|------------------------------------|
| Resource Identifiers | `"pod"`, `"namespace"`, `"node"` | Use singular, lowercase strings    |
| Counts             | `"count"`, `"total"`, `"available"` | Use explicit names, specify units if needed |
| Durations          | `"duration"`, `"timeout"`, `"interval"` | Log as `time.Duration` values      |
| Status             | `"status"`, `"phase"`, `"state"` | Use string constants or enums      |
| Errors             | `"err"`                         | Reserved key for error objects in ErrorS |

### Supported Value Types and Serialization

The serializer handles:

- Strings, quoted if necessary  
- Numeric types (int, float)  
- Booleans as `true`/`false`  
- `time.Duration` serialized as strings (e.g. `"5s"`)  
- Error objects serialized via `.Error()`  
- Pointers safely logged via `SafePtr` (see below)  
- Custom objects implementing `fmt.Stringer` or `logr.Marshaler` serialized appropriately  

### Pointer Safety in Logging

Logging pointers that implement interfaces like `fmt.Stringer` and may be `nil` can cause panics. To avoid this, use:

```go
klog.InfoS("Got object", "obj", klog.SafePtr(obj))
```

`SafePtr` returns `nil` if the pointer is `nil`, otherwise returns the pointer as-is, preventing panics when stringers are called on nil pointers.

**Sources:**  
- [vendor/k8s.io/klog/v2/internal/serialize/keyvalues.go:30-180]()  
- [vendor/k8s.io/klog/v2/safeptr.go:22-34]()  

## Logging Usage in nvml-mock-nri Plugin

The `nvml-mock-nri` plugin is a containerd Node Resource Interface plugin injecting the nvml-mock overlay into containers for GPU simulation.

- Logging is performed primarily via `log.Printf` for startup and lifecycle events.   
- Health events and plugin lifecycle transitions (Configure, CreateContainer) are logged with clear, contextual messages.  
- Error handling logs fatal errors with context before exiting.

Example snippet from `cmd/nvml-mock-nri/main.go`:

```go
log.Printf("nvml-mock-nri: registering plugin %s/%s on %s", *pluginIndex, *pluginName, *socketPath)

p, err := stub.New(p, ... )
if err != nil {
    log.Fatalf("nvml-mock-nri: create stub: %v", err)
}
```

While this code uses `log.Printf` currently, it follows the general structure of including identifying keys and messages.

The readiness and liveness probe health states are tracked with internal state exposed via `/readyz` and `/healthz` HTTP endpoints with failure reasons logged for diagnostics.

**Sources:**  
- [cmd/nvml-mock-nri/main.go:32-89]()  
- [cmd/nvml-mock-nri/health.go:14-193]()  

## Logging in Tests

The end-to-end (E2E) tests utilize structured logging to track the progress and results of operations, allowing better diagnostics on failures.

### Example from NRI Injection Scenario Test

```go
klog.InfoS("Starting test scenario", "scenario", "nvml-mock node-wide NRI")

klog.InfoS("Deploying NRI DaemonSet", "namespace", nvmlMockNamespace, "daemonset", nriNRIDaemonSet)

klog.ErrorS(err, "DaemonSet not ready", "daemonset", nriNRIDaemonSet)
```

These logs include explicit keys for resource types, names, node names, and error objects, matching best practices.

### Test Logging Flow

```mermaid
graph TB
    Start["Test begins"] --> LogSetup["klog.InfoS: test setup"]
    LogSetup --> KubeOps["Create Kubernetes resources"]
    KubeOps --> LogKubeOps["klog.InfoS: resource creation"]
    LogKubeOps --> Assertion["Eventually() waits for condition"]
    Assertion --> LogPoll["klog.InfoS: polling status"]
    Assertion -->|Fail| LogFail["klog.ErrorS: failure details"]
    LogFail --> Cleanup["AfterEach cleanup"]
    Cleanup --> LogCleanup["klog.InfoS: cleanup logs"]
    LogCleanup --> End["Test ends"]
```

Logging in tests captures contextual information such as profile names, node names, resource types, and error messages.

**Sources:**  
- [tests/e2e/go/scenario_nri_test.go:53-160]()  

## Integration with go-logr and slog Backends

The klog library supports delegating structured logging calls to external logger implementations compatible with `logr.Logger` and the newer Go 1.21+ `log/slog`.

### Logger Backend Selection

```mermaid
graph TB
    AppCode["Application/Test Code"] --> KlogAPI["Calls klog.InfoS/ErrorS"]
    KlogAPI --> LoggerInstalled{"Is logging.logger set?"}
    LoggerInstalled -- No --> KlogBuiltIn["Use klog built-in formatHeader + output"]
    LoggerInstalled -- Yes --> LoggerBackend["Forward to logging.logger"]
    LoggerBackend --> LogrInterface["logr.Logger interface"]
    LoggerBackend --> SlogInterface["slog.Logger interface (via logr.SlogSink)"]
```

- Without an external logger, klog uses its built-in formatting and outputs to stderr or configured files.  
- With an external logger (logr or slog), klog forwards structured messages to it, enabling attribute chaining, grouping, and backend-specific formatting.

### slog Integration (Go 1.21+)

klog can be configured with a `*slog.Logger` backend using:

```go
klog.SetSlogLogger(slogLogger)
```

This integration enables unified logging across standard library and third-party libraries, retaining attribute and group semantics.

**Sources:**  
- [vendor/k8s.io/klog/v2/klog.go:450-470]()  
- [vendor/k8s.io/klog/v2/klogr_slog.go:20-84]()  
- [vendor/k8s.io/klog/v2/contextual_slog.go:1-31]()  

## Summary of Best Practices

| Aspect              | Recommended Practice                              | Avoid                                    |
|---------------------|-------------------------------------------------|-----------------------------------------|
| Message Strings     | Use constant literal messages, no formatting     | Using `Infof` style formatting           |
| Key Names           | Use stable, meaningful keys ("namespace", "pod")| Varying keys or abbreviations ("ns", "podName") |
| Use Key-Value Pairs | Always pass pairs: `klog.InfoS("msg", "key", val)`| Passing odd number of arguments          |
| Errors              | Use `ErrorS(err, ...)` to log errors explicitly  | Logging errors only in format strings    |
| Pointer Values      | Use `klog.SafePtr` for pointers, especially nils | Passing raw pointers that might panic    |
| Verbosity           | Use `klog.V(level).InfoS` for debug info          | Logging everything at level 0             |

### Common Logging Patterns

```mermaid
graph TB
    Op["Resource operation"] --> LogCreate["klog.InfoS('Creating resource', 'kind', kind, 'name', name)"]
    Err["Operation error"] --> LogError["klog.ErrorS(err, 'Operation failed', 'resource', resource)"]
    Wait["Async wait"] --> LogWait["klog.InfoS('Waiting for condition', 'timeout', timeout)"]
    Clean["Cleanup"] --> LogClean["klog.InfoS('Deleting resources', 'namespace', ns)"]
    Debug["Debug info"] --> LogDebug["klog.V(4).InfoS('Details', 'config', config)"]
```

### Migration from Unstructured to Structured Logging

| Before (Unstructured)                         | After (Structured)                                         |
|----------------------------------------------|------------------------------------------------------------|
| `klog.Infof("pod %s in ns %s", pod, ns)`     | `klog.InfoS("Pod created", "pod", pod, "namespace", ns)`   |
| `klog.Errorf("error: %v", err)`               | `klog.ErrorS(err, "Creation failed", "pod", pod)`          |
| `klog.V(2).Infof("details: %+v", obj)`        | `klog.V(2).InfoS("Details", "object", obj)`                 |
| `klog.Infof("count: %d", len(items))`          | `klog.InfoS("Processing items", "count", len(items))`       |

Migrating to structured logging improves log filtering, observability pipeline compatibility, and provides consistent context keys.

---

# Diagrams Connecting Natural Language to Code Entities

## Diagram 1: Logging API to Serialization Components

```mermaid
graph LR
    A["User code calls InfoS/ErrorS"] --> B["klog.InfoS / klog.ErrorS"]
    B --> C["serialize.KVListFormat (serialize key=value pairs)"]
    C --> D["buffer.GetBuffer()/PutBuffer (buffer pool)"]
    D --> E["formatHeader (severity, file, line)"]
    E --> F["output() (write to stderr or file)"]
```

**Sources:**  
- [vendor/k8s.io/klog/v2/klog.go:111-115]()  
- [vendor/k8s.io/klog/v2/klogr_slog.go:66-77]()  

## Diagram 2: nvml-mock-nri Logging and Health Probe Flow

```mermaid
graph TB
    Plugin["nvml-mock-nri plugin"] --> InitLog["log.Printf: plugin starting"]
    InitLog --> Register["stub.New + Configure (logs registered)"]
    Configure --> HealthSet["health.setRegistered(true)"]
    CreateContainer --> Adjust["nvmlmock.Adjust() called"]
    Adjust --> LogAdjust["log.Printf on errors or events"]
    HealthProbe["/healthz & /readyz HTTP handlers"] --> HealthLog["log.Printf on failures"]
    WedgeDetect["health.begin()/end() track inflight requests"]
    WedgeDetect --> HealthProbe
```

**Sources:**  
- [cmd/nvml-mock-nri/main.go:4-89]()  
- [cmd/nvml-mock-nri/health.go:14-193]()  

---

# Appendix: Code File Locations for Reference

| Topic                     | File and Lines                      |
|---------------------------|-----------------------------------|
| nvml-mock-nri main logic  | `cmd/nvml-mock-nri/main.go:4-89`  |
| nvml-mock-nri health pkg  | `cmd/nvml-mock-nri/health.go:14-193` |
| klog core and structured  | `vendor/k8s.io/klog/v2/klog.go:1-91`, `klogr_slog.go:20-84` |
| E2E tests logging examples| `tests/e2e/go/scenario_nri_test.go:53-160`                    |

This completes the detailed documentation of structured logging practices for k8s-test-infra, including application in tests and the nvml-mock-nri plugin.

---

# Page: Build System

# Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/nvml-mock-e2e-go.yaml](.github/workflows/nvml-mock-e2e-go.yaml)
- [Makefile](Makefile)
- [README.md](README.md)
- [deployments/nvml-mock/Dockerfile](deployments/nvml-mock/Dockerfile)
- [pkg/gpu/mockcuda/Makefile](pkg/gpu/mockcuda/Makefile)
- [pkg/gpu/mocknvml/Dockerfile](pkg/gpu/mocknvml/Dockerfile)
- [pkg/gpu/mocknvml/Makefile](pkg/gpu/mocknvml/Makefile)
- [tests/e2e/README.md](tests/e2e/README.md)
- [tests/e2e/go/e2e_suite_test.go](tests/e2e/go/e2e_suite_test.go)
- [tests/e2e/go/framework/config/config.go](tests/e2e/go/framework/config/config.go)
- [tests/e2e/go/framework/harness/harness.go](tests/e2e/go/framework/harness/harness.go)
- [tests/e2e/go/suite_cluster.go](tests/e2e/go/suite_cluster.go)
- [tests/e2e/go/suite_helm.go](tests/e2e/go/suite_helm.go)
- [tests/e2e/spike-nvidia-smi.sh](tests/e2e/spike-nvidia-smi.sh)
- [tests/mocknvml/Dockerfile](tests/mocknvml/Dockerfile)
- [tests/poc-validation/setup-kind-cluster.sh](tests/poc-validation/setup-kind-cluster.sh)

</details>



**Purpose and Scope**:  
This document provides a high-level overview of the build automation system for the k8s-test-infra repository. The system coordinates compilation, dependency management, quality checks, and container image creation. It uses a Makefile as the primary driver, with a consistent Go version enforced via the devel Dockerfile and extracted into CI environments.

This page links to child pages for detailed information on Makefile targets ([Makefile Reference](#8.1)), container images ([Docker Images](#8.2)), and Go version management ([Go Version Management Strategy](#8.3)).

---

## Build System Architecture

The build automation is centered around the `Makefile` which orchestrates commands to produce Go binaries, manage Go module dependencies, enforce formatting and linting standards, and build container images.

```mermaid
graph TB
    subgraph Source["Source Inputs"]
        GOSRC["Go Source Files<br/>cmd/nv-ci-bot/main.go"]
        GOMOD["go.mod & go.sum"]
        VENDOR["vendor/ directory"]
    end
    
    subgraph MakeTargets["Makefile Targets"]
        BUILD["build"]
        VENDOR_T["vendor"]
        CHECKVENDOR["check-vendor"]
        MODULES["modules"]
        CHECKMODULES["check-modules"]
        LINT["lint"]
        FMT["fmt"]
        VERIFY["verify"]
    end
    
    subgraph Artifacts["Build Artifacts"]
        BINARY["bin/nv-ci-bot (binary)"]
        DEVIMG["ghcr.io/nvidia/k8s-test-infra (development image)"]
    end
    
    subgraph Tools["External Tools"]
        GOCOMPILER["go build"]
        GOFMT["gofmt"]
        GOLANGCI["golangci-lint"]
        GOMOD_T["go mod commands"]
        DOCKER["docker build"]
    end
    
    subgraph VersionControl["Version Configuration & CI"]
        DOCKERFILE["deployments/devel/Dockerfile<br/>golang:1.25.4 base"]
        VERSIONSH["hack/golang-version.sh"]
        CI["GitHub Actions workflows"]
    end
    
    GOSRC --> BUILD
    GOMOD --> VENDOR_T
    GOMOD --> MODULES
    
    BUILD --> GOCOMPILER
    VENDOR_T --> GOMOD_T
    MODULES --> GOMOD_T
    CHECKVENDOR --> GOMOD_T
    CHECKMODULES --> GOMOD_T
    LINT --> GOLANGCI
    FMT --> GOFMT
    VERIFY --> GOFMT
    
    GOCOMPILER --> BINARY
    DOCKERFILE --> DOCKER
    BINARY --> DEVIMG
    
    DOCKERFILE --> VERSIONSH
    VERSIONSH --> CI
    CI --> MakeTargets
    
    VENDOR_T --> VENDOR
    VENDOR --> CHECKVENDOR
```

*Diagram: Build System Component Relationships*

Sources: [Makefile:1-80](), [deployments/devel/Dockerfile:15-18](), [hack/golang-version.sh:1-23]()

---

## Primary Makefile Targets Overview

The Makefile facilitates common development tasks through a set of phony targets:

| Target        | Purpose                                              | Key Operations                                                    | Exit Behavior                      |
|----------------|------------------------------------------------------|------------------------------------------------------------------|----------------------------------|
| `build`        | Compile main binary                                  | Cleans `bin/`, builds `cmd/nv-ci-bot/main.go`                   | Fails on compilation errors      |
| `vendor`       | Synchronize dependencies                             | Runs `go mod tidy`, `go mod vendor`, `go mod verify`             | Fails on mod errors              |
| `check-vendor` | Verify vendor directory sync with version control   | Runs `vendor` then verifies no unstaged changes                  | Fails if diffs found             |
| `modules`      | Tidy, vendor and verify all Go modules (multi-module support) | Iterates through all `go.mod` files                              | Fails on errors                 |
| `check-modules`| Verify all modules' dependencies are synced         | Runs `modules` then checks git diffs                              | Fails if diffs found             |
| `lint`         | Run static code analysis                             | Executes `golangci-lint run` across all packages                 | Fails if lint issues found      |
| `fmt`          | Format Go source files                               | Runs `gofmt -w -l` to write formatted code                       | Modifies files in place          |
| `verify`       | Check formatting matches `gofmt`                    | Runs `gofmt -w -l -d` and errors if files are out of format      | Fails if formatting needed      |

These targets are designed to be composable and lend themselves to CI workflows enforcing code quality.

Sources: [Makefile:11-82]()

---

## Binary Compilation Process

The key Go binary built by the system is `nv-ci-bot`, compiled from `cmd/nv-ci-bot/main.go`. The `build` target removes existing output binaries, then compiles using the Go compiler defined by `GO_CMD` (defaulting to `go`).

```mermaid
graph LR
    MAKE_BUILD["make build"] --> CLEAN["rm -rf bin/"]
    CLEAN --> COMPILE["go build -o bin/$(BINARY_NAME) cmd/nv-ci-bot/main.go"]
    COMPILE --> BIN_ARTIFACT["bin/nv-ci-bot binary"]

    subgraph Conf["Build Config"]
        GO_CMD["GO_CMD = go (default)"]
        BINARY_NAME["BINARY_NAME (unset by default)"]
    end

    GO_CMD -.-> COMPILE
    BINARY_NAME -.-> COMPILE
```

The build target is declared as:

```makefile
build:
	@rm -rf bin
	$(GO_CMD) build -o bin/$(BINARY_NAME) cmd/nv-ci-bot/main.go
```

**Note:** The `BINARY_NAME` variable is referenced but not defined in the Makefile, implying it should be set externally, e.g., `make build BINARY_NAME=nv-ci-bot`.

Sources: [Makefile:29-33]()

---

## Dependency Management Strategy

The project uses a vendoring approach to capture all module dependencies in the `vendor/` directory, ensuring reproducible builds.

```mermaid
graph TB
    GOPKGS["Go Module Proxy & Repos"]
    GOMOD["go.mod"]
    GOSUM["go.sum"]
    VENDOR["vendor/ directory"]

    TIDY["go mod tidy"]
    VENDORG["go mod vendor"]
    VERIFY["go mod verify"]

    CHECKVENDOR["check-vendor (git diff validation)"]
    CHECKMODULES["check-modules (multi-module validation)"]

    GOPKGS --> TIDY
    GOMOD --> TIDY
    TIDY --> GOSUM
    GOSUM --> VENDORG
    VENDORG --> VENDOR
    VENDOR --> VERIFY

    VERIFY --> CHECKVENDOR
    TIDY --> CHECKMODULES
    VENDORG --> CHECKMODULES
    VERIFY --> CHECKMODULES
```

- `vendor` target runs `go mod tidy`, `go mod vendor`, and `go mod verify`.
- `check-vendor` runs `vendor` and then verifies that `go.mod`, `go.sum`, and `vendor/` have no uncommitted changes.
- Multi-module targets (`modules` and `check-modules`) apply these operations recursively to all `go.mod` files in the repository, excluding certain paths.

Sources: [Makefile:44-82]()

---

## Code Quality and Formatting Enforcement

Three Makefile targets ensure quality:

- `fmt`: Formats all Go sources in-place with `gofmt`.
- `verify`: Checks formatting without making changes and raises errors if any files need formatting.
- `lint`: Runs `golangci-lint` for static code analysis across all packages.

```makefile
fmt:
	@$(GO_FMT) -w -l $$(find . -name '*.go')

verify:
	@out=`$(GO_FMT) -w -l -d $$(find . -name '*.go')`; \
	if [ -n "$$out" ]; then \
	    echo "$$out"; \
	    exit 1; \
	fi

lint:
	golangci-lint run ./...
```

Sources: [Makefile:34-46]()

---

## Container Image Build

The primary development image for the repository is built from the `deployments/devel/Dockerfile`, which specifies the Go version used throughout the project.

```dockerfile
# deployments/devel/Dockerfile snippet
FROM golang:1.25.4
```

This Dockerfile also serves as the canonical source for the Go version to use in local builds, CI workflows, and image builds.

The `Makefile` defines image-related variables for tagging and pushing images to `ghcr.io/nvidia` under the repository `k8s-test-infra` with version `0.0.1` by default.

Sources: [Makefile:22-26](), [deployments/devel/Dockerfile:15-18]()

---

## Integration with CI/CD Pipelines

The build system is tightly integrated with GitHub Actions workflows, which:

1. Extract the Go version by parsing the `deployments/devel/Dockerfile` using the `hack/golang-version.sh` script.
2. Use this Go version consistently for build jobs.
3. Run Makefile targets such as `check-modules` (multi-module dependency validation) and `lint` (static analysis).

```mermaid
graph TB
    PR["Pull Request or Push"] --> BASIC["basic-checks.yaml"]
    BASIC --> VARIABLES["variables job"]
    VARIABLES --> GOLANG["golang job"]
    VARIABLES --> SCANNING["code scanning job"]

    VARIABLES --> VERSIONSH["hack/golang-version.sh"]
    VERSIONSH --> DOCKERFILE["deployments/devel/Dockerfile"]

    GOLANG --> CHECKMODULES["make check-modules"]
    GOLANG --> LINT["make lint"]
```

This integration enforces environment consistency, code quality, and dependency integrity on every change.

Sources: [.github/workflows/ci.yaml:1-26](), [.github/workflows/basic-checks.yaml:1-50](), [hack/golang-version.sh:1-23]()

---

## Build System Variables and Configuration

Several variables in the Makefile can be overridden to customize build and image parameters:

| Variable        | Default             | Description                            | Override Example             |
|-----------------|---------------------|------------------------------------|---------------------------|
| `GO_CMD`         | `go`                | Go compiler binary                  | `make build GO_CMD=go1.20`   |
| `GO_FMT`         | `gofmt`             | Go formatter tool                   | `make fmt GO_FMT=goimports`  |
| `VERSION`        | `0.0.1`             | Image version tag                   | `make VERSION=0.0.2`         |
| `IMAGE_REGISTRY` | `ghcr.io/nvidia`    | Container image registry            | `make IMAGE_REGISTRY=docker.io/myorg` |
| `IMAGE_NAME`     | `k8s-test-infra`    | Image repository name               | (Usually not overridden)      |
| `IMAGE_TAG_NAME` | `$(VERSION)`        | Image tag name                     | `make IMAGE_TAG_NAME=latest`  |
| `BINARY_NAME`    | *(undefined)*       | Output binary name for build       | `make build BINARY_NAME=nv-ci-bot` |

The `PROJECT_DIR` holds the Makefile's directory absolute path, mainly for internal use.

Sources: [Makefile:16-29]()

---

## Recommended Build Workflow

For local development or CI, the suggested order of running build system targets is:

```mermaid
graph LR
    CODE_CHG["Code changes"]
    FMT["make fmt"]
    VENDOR["make vendor"]
    VERIFY["make verify"]
    LINT["make lint"]
    BUILD["make build"]
    TEST["Run tests (external)"]

    CODE_CHG --> FMT --> VENDOR --> VERIFY --> LINT --> BUILD --> TEST

    subgraph OptionalChecks["Optional Checks"]
        CHECKV["make check-vendor"]
        CHECKM["make check-modules"]
    end

    VENDOR -.-> CHECKV
    VENDOR -.-> CHECKM
```

- Formatting (`fmt`) normalizes source.
- Dependencies are synchronized (`vendor`), then verified (`verify`).
- Static code analysis is run (`lint`).
- Compilation occurs (`build`).
- Tests are executed separately (see testing infrastructure).

Sources: [Makefile:11-80](), [.github/workflows/basic-checks.yaml:1-50]()

---

## Child Pages

Further technical details are covered in the following child pages:

- [Makefile Reference](#8.1) — Full details on all Makefile targets including cluster lifecycle and e2e scenarios.  
- [Docker Images](#8.2) — Detailed explanations of the key container images, staging, multi-stage builds, and artifacts.  
- [Go Version Management Strategy](#8.3) — How the Go version is defined and extracted consistently across builds and CI.

---

# Summary

The k8s-test-infra build system leverages a Makefile-driven approach coordinated with GitHub Actions. It centralizes dependency management, code quality enforcement, binary compilation, and container image creation into an efficient, repeatable workflow. The consistent Go version is anchored by the devel Dockerfile and extracted dynamically for CI and local builds. This ensures developers and CI produce identical outputs and environments.

This overview has guided through the build architecture, operations, artifacts, and pipelines, with pointers to in-depth child pages for each aspect.

---

**Sources:**  
[Makefile:1-82](), [deployments/devel/Dockerfile:15-18](), [hack/golang-version.sh:1-23](), [.github/workflows/ci.yaml:1-33](), [.github/workflows/basic-checks.yaml:1-50]()

---

# Page: Makefile Reference

# Makefile Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/nvml-mock-e2e-go.yaml](.github/workflows/nvml-mock-e2e-go.yaml)
- [Makefile](Makefile)
- [README.md](README.md)
- [pkg/gpu/mocknvml/README.md](pkg/gpu/mocknvml/README.md)
- [pkg/gpu/mocknvml/bridge/padding.go](pkg/gpu/mocknvml/bridge/padding.go)
- [tests/e2e/README.md](tests/e2e/README.md)
- [tests/e2e/go/e2e_suite_test.go](tests/e2e/go/e2e_suite_test.go)
- [tests/e2e/go/framework/config/config.go](tests/e2e/go/framework/config/config.go)
- [tests/e2e/go/framework/harness/harness.go](tests/e2e/go/framework/harness/harness.go)
- [tests/e2e/go/suite_cluster.go](tests/e2e/go/suite_cluster.go)
- [tests/e2e/go/suite_helm.go](tests/e2e/go/suite_helm.go)

</details>



## Purpose and Scope

This document provides a comprehensive reference for the Makefile in the **k8s-test-infra** repository. The Makefile serves as the primary automation tool, defining targets for:

- Building binaries
- Managing Go modules and vendoring
- Enforcing code quality via formatting and linting
- Managing Kind clusters for test infrastructure
- Running end-to-end (E2E) test scenarios for various integration targets

These targets are designed to support both local developer workflows and continuous integration (CI) pipelines.

For details on related build artifacts like Docker images, see [Docker Images](#8.2). For the Go version management process, see [Go Version Management Strategy](#8.3). For integration with CI/CD workflows and code quality practices, see sections on GitHub Actions and Linting.

**Sources:** [Makefile:1-80]()

---

## Overview

The Makefile defines `.PHONY` targets for common development tasks. It leverages standard Go tools (`go`, `gofmt`, `golangci-lint`), Helm, and Kind to manage the build/test infrastructure.

Key characteristics:

- Supports a multi-module repo structure with vendoring
- Targets optimize for local development and CI usage
- Cluster-related targets manage Kind clusters for E2E tests
- E2E targets invoke Go/Ginkgo test harnesses with scenario labels

**Sources:** [Makefile:11-12]()

---

## Target Dependency Graph

```mermaid
graph TB
    build["build<br/>Compile nv-ci-bot binary"]
    fmt["fmt<br/>Format Go source files"]
    verify["verify<br/>Check formatting"]
    lint["lint<br/>Run golangci-lint"]
    vendor["vendor<br/>Tidy + vendor + verify"]
    check_vendor["check-vendor<br/>Verify vendor sync"]
    modules["modules<br/>Multi-module management"]
    check_modules["check-modules<br/>Verify module sync"]
    
    mod_tidy[".mod-tidy<br/>Tidy all go.mod files"]
    mod_vendor[".mod-vendor<br/>Vendor all modules"]
    mod_verify[".mod-verify<br/>Verify all modules"]
    
    check_vendor --> vendor
    vendor --> tidy["go mod tidy"]
    vendor --> vendor_cmd["go mod vendor"]
    vendor --> verify_cmd["go mod verify"]
    
    modules --> mod_tidy
    modules --> mod_vendor
    modules --> mod_verify
    check_modules --> modules
    
    style build fill:#f9f9f9
    style vendor fill:#f9f9f9
    style modules fill:#f9f9f9
    style check_vendor fill:#e8e8e8
    style check_modules fill:#e8e8e8
```

**Sources:** [Makefile:11-80]()

---

## Configuration Variables

The Makefile defines several variables to configure builds and image tagging:

| Variable          | Default                    | Description                          |
|-------------------|----------------------------|------------------------------------|
| `GO_CMD`          | `go`                       | Go compiler command                |
| `GO_FMT`          | `gofmt`                    | Go formatting tool                 |
| `GO_SRC`          | `find . -name '*.go' ...`  | List of Go source files (excluding vendor) |
| `VERSION`         | `0.0.1`                    | Project version                   |
| `IMAGE_REGISTRY`  | `ghcr.io/nvidia`           | Container image registry          |
| `IMAGE_TAG_NAME`  | `$(VERSION)`               | Tag name for images               |
| `IMAGE_NAME`      | `k8s-test-infra`           | Base image name                  |
| `IMAGE_REPO`      | `$(IMAGE_REGISTRY)/$(IMAGE_NAME)` | Full image repository       |
| `IMAGE_TAG`       | `$(IMAGE_REPO):$(IMAGE_TAG_NAME)` | Complete image tag             |
| `PROJECT_DIR`     | Project root directory      | Absolute path to repo root         |

**Sources:** [Makefile:13-29]()

---

## Build Targets

### build

Builds the `nv-ci-bot` binary (CLI tool) from the source entrypoint `cmd/nv-ci-bot/main.go`.

```makefile
build:
	@rm -rf bin
	$(GO_CMD) build -o bin/$(BINARY_NAME) cmd/nv-ci-bot/main.go
```

- Cleans previous build output folder `bin/`
- Builds the Go binary with output path `bin/$(BINARY_NAME)`
- `$(BINARY_NAME)` must be provided at invocation, e.g., `make build BINARY_NAME=nv-ci-bot` or by the CI workflow.

**Usage:**

```bash
make build BINARY_NAME=nv-ci-bot
```

**Sources:** [Makefile:30-32]()

---

## Code Quality Targets

```mermaid
graph LR
    source["Go Source Files<br/>*.go (non-vendor)"]
    fmt["fmt target"]
    verify["verify target"]
    lint["lint target"]
    
    source --> fmt
    source --> verify
    source --> lint
    
    fmt --> gofmt["gofmt -w -l"]
    verify --> gofmt_check["gofmt -w -l -d"]
    lint --> golangci["golangci-lint run"]
    
    gofmt --> modify["Modifies files in-place"]
    gofmt_check --> diff["Outputs diff if changes needed"]
    golangci --> report["Reports linting issues"]
    
    diff --> exit_code["Exit 1 if changes detected"]
```

**Sources:** [Makefile:33-46]()

### fmt

Formats all Go source files (excluding vendor) in place using `gofmt`.

```makefile
fmt:
	@$(GO_FMT) -w -l $$(find . -name '*.go')
```

- `-w` writes formatting changes to files
- `-l` lists files that were modified

**Usage:**

```bash
make fmt
```

**Sources:** [Makefile:34-35]()

### verify

Checks if Go source files are properly formatted, but does **not** modify them. Fails if formatting issues are detected.

```makefile
verify:
	@out=`$(GO_FMT) -w -l -d $$(find . -name '*.go')`; \
	if [ -n "$$out" ]; then \
	    echo "$$out"; \
	    exit 1; \
	fi
```

- Uses `-d` to output diffs for files needing formatting
- Exits with failure (1) if any files are not formatted

Typical use: run in CI to enforce formatting rules.

**Usage:**

```bash
make verify
```

**Sources:** [Makefile:37-42]()

### lint

Runs static analysis with `golangci-lint` on all Go packages.

```makefile
lint:
	golangci-lint run ./...
```

- `golangci-lint` integrates multiple linters
- Checks the entire codebase
- Requires `golangci-lint` to be installed

**Usage:**

```bash
make lint
```

**Sources:** [Makefile:43-45]()

---

## Module Management Targets

The Makefile supports two workflows: single-module (root only) and multi-module management.

### Single-Module Workflow

- `vendor` updates dependencies and creates the `vendor/` directory
- `check-vendor` verifies vendoring sync with git

```mermaid
graph TB
    start["Run make vendor"]
    tidy["go mod tidy"]
    vendor_cmd["go mod vendor"]
    verify_cmd["go mod verify"]
    check_vendor["make check-vendor (git diff)"]

    start --> tidy --> vendor_cmd --> verify_cmd --> check_vendor
```

### vendor

Update dependencies and vendor in the root module:

```makefile
vendor:
	go mod tidy
	go mod vendor
	go mod verify
```

Operations:

- `go mod tidy`: cleans and syncs module dependencies
- `go mod vendor`: copies dependencies to `vendor/`
- `go mod verify`: validates checksums of modules

**Usage:**

```bash
make vendor
```

**Sources:** [Makefile:47-50]()

### check-vendor

Ensures vendored dependencies are committed and in sync:

```makefile
check-vendor: vendor
	git diff --quiet HEAD -- go.mod go.sum vendor
```

- Runs `make vendor` first to update vendor
- Uses `git diff --quiet` to detect uncommitted changes
- Exits nonzero if vendor or mod files are out of sync

**Usage:**

```bash
make check-vendor
```

Typically used in CI to enforce consistent vendoring.

**Sources:** [Makefile:52-53]()

---

### Multi-Module Workflow

The repo may have multiple Go modules in subdirectories. The Makefile provides:

- `modules` target to tidy, vendor, and verify all modules recursively
- `check-modules` to verify across all modules that vendoring is in sync

```mermaid
graph TB
    subgraph "Repository"
        root["Root"]
        mod1["go.mod (root)"]
        pkg["packages with go.mod"]
    end

    find_mods["find . -name go.mod excluding testdata and third_party"]
    find_mods --> mod1
    find_mods --> pkg
    
    modules["modules target"]
    modules --> .mod-tidy[.mod-tidy: go mod tidy per module]
    modules --> .mod-vendor[.mod-vendor: go mod vendor per module]
    modules --> .mod-verify[.mod-verify: go mod verify per module]
    
    check_modules["check-modules"]
    check_modules --> modules
    check_modules --> git_check["git diff checks for go.mod/go.sum and vendor"]

```

**Sources:** [Makefile:54-79]()

### .mod-tidy

Runs `go mod tidy` for every `go.mod` except in `testdata/` or `third_party/`.

```makefile
.mod-tidy:
	@for mod in $$(find . -name go.mod -not -path "./testdata/*" -not -path "./third_party/*"); do \
	    echo "Tidying $$mod..."; ( \
	        cd $$(dirname $$mod) && go mod tidy \
            ) || exit 1; \
	done
```

This ensures all modules are clean and consistent.

**Sources:** [Makefile:56-62]()

### .mod-vendor

Runs `go mod vendor` for each module except excludes `deployments/` additionally:

```makefile
.mod-vendor:
	@for mod in $$(find . -name go.mod -not -path "./testdata/*" -not -path "./third_party/*" -not -path "./deployments/*"); do \
		echo "Vendoring $$mod..."; ( \
			cd $$(dirname $$mod) && go mod vendor \
			) || exit 1; \
	done
```

Prevent vendoring for deployment-related modules.

**Sources:** [Makefile:65-70]()

### .mod-verify

Runs `go mod verify` for all modules except those in `testdata/` or `third_party/`:

```makefile
.mod-verify:
	@for mod in $$(find . -name go.mod -not -path "./testdata/*" -not -path "./third_party/*"); do \
	    echo "Verifying $$mod..."; ( \
	        cd $$(dirname $$mod) && go mod verify | sed 's/^/  /g' \
	    ) || exit 1; \
	done
```

Indented output improves readability.

**Sources:** [Makefile:71-77]()

### modules

Runs all three steps in a single invocation:

```makefile
modules:  | .mod-tidy .mod-vendor .mod-verify
```

- The `|` syntax makes these order-only prerequisites.
- Calling `make modules` ensures all Go modules are tidy, vendored, and verified.

**Sources:** [Makefile:54]()

### check-modules

Verifies all module files and vendors in git are in sync:

```makefile
check-modules: modules
	@echo "- Checking if go.mod and go.sum are in sync..."
	@git diff --exit-code -- $$(find . -name go.mod -name go.sum)
	@echo "- Checking if the go mod vendor dir is in sync..."
	@git diff --exit-code -- $$(find . -name vendor)
```

- Runs `make modules` first to update state.
- Checks no changes to any `go.mod`, `go.sum`, or `vendor/` are detected in git.
- Failures indicate local changes not committed or vendoring out of date.

Typical usage in CI.

**Sources:** [Makefile:78-83]()

---

## Kind Cluster Management

```mermaid
graph LR
    image_kind_node["image-kind-node<br/>Builds Kind node Docker image"]
    cluster_create["cluster-create<br/>Create Kind cluster"]
    cluster_delete["cluster-delete<br/>Delete Kind cluster"]

    cluster_create --> image_kind_node
```

- `image-kind-node`: Builds the custom Kind node image with NVIDIA container toolkit included unless an environment flag to use a prebuilt image is set.
- `cluster-create`: Creates a Kind cluster using the built node image and a profile-specific cluster config YAML.
- `cluster-delete`: Deletes the Kind cluster by name.

**Sources:** [Makefile:92-139]()

### image-kind-node

Builds the Kind node Docker image unless `KIND_NODE_IMAGE_PREBUILT` environment variable is set:

```makefile
image-kind-node:
	@if [ -n "$$KIND_NODE_IMAGE_PREBUILT" ]; then \
		docker image inspect $(KIND_NODE_IMAGE) >/dev/null 2>&1 || { \
			echo "ERROR: KIND_NODE_IMAGE_PREBUILT is set but $(KIND_NODE_IMAGE) is not in the local docker daemon."; \
			echo "       Ensure a preceding step ran: docker pull <ref> && docker tag <ref> $(KIND_NODE_IMAGE)"; \
			echo "       (Or unset KIND_NODE_IMAGE_PREBUILT to build it locally.)"; \
			exit 1; \
		}; \
		echo "Using pre-built $(KIND_NODE_IMAGE) already present locally"; \
	else \
		docker build -t $(KIND_NODE_IMAGE) ./local/kind; \
	fi
```

- Uses variable `KIND_NODE_IMAGE` defaulting to `kind-node-nv:latest`
- Supports fast CI by using prebuilt images pulled and tagged locally

**Sources:** [Makefile:121-133]()

### cluster-create

Creates Kind cluster with specified name, node image, and config file.

```makefile
cluster-create: image-kind-node
	@kind create cluster --name $(KIND_CLUSTER_NAME) --image $(KIND_NODE_IMAGE) --config $(KIND_CLUSTER_CONFIG)
```

Variables `KIND_CLUSTER_NAME` and `KIND_CLUSTER_CONFIG` default depending on cluster profile:

- `PROFILE=default` → `gpu-test` cluster, config `local/kind/default.kind.yaml`
- `PROFILE=compute-domain` → computed name and config

**Sources:** [Makefile:135-137]()

### cluster-delete

Deletes the Kind cluster by name.

```makefile
cluster-delete:
	@kind delete cluster --name $(KIND_CLUSTER_NAME)
```

**Usage:**

```bash
make cluster-create
make cluster-delete
```

**Sources:** [Makefile:138-139]()

---

## End-to-End Test Targets

These targets execute Go/Ginkgo end-to-end tests. They create or attach to Kind clusters, build and load the nvml-mock Docker image, deploy the nvml-mock Helm chart, and run integration validation scenarios.

```mermaid
graph TB
    e2e["e2e<br/>Standalone scenario"]
    e2e_dra["e2e-dra<br/>DRA driver scenario"]
    e2e_gpu_operator["e2e-gpu-operator<br/>GPU Operator scenario"]
    e2e_multi_node["e2e-multi-node<br/>Multi-node heterogeneous"]
    e2e_nri["e2e-nri<br/>Node-wide NRI injection scenario"]

    e2e --> e2e_dra
    e2e --> e2e_gpu_operator
    e2e --> e2e_multi_node
    e2e --> e2e_nri
```

**Sources:** [Makefile:140-160]()

### e2e

Runs the standalone e2e demo scenario, defaulting to the `gb200` profile if none specified. The scenario:

- Builds the nvml-mock Docker image (unless `E2E_SKIP_BUILD=true`)
- Creates a Kind cluster (unless `E2E_ATTACH_EXISTING=true`)
- Loads the nvml-mock image into the Kind cluster
- Installs nvml-mock Helm chart with chosen profile(s)
- Runs validation tests (labels, nvidia-smi, NVLink, InfiniBand, PCI sysfs, failure injection)
- Collects diagnostics on failure
- Keeps the cluster by default for debugging

**Usage:**

```bash
make e2e
# or to specify profiles
make e2e E2E_PROFILES="a100 h100"
make e2e E2E_GINKGO_FLAGS='--label-filter="nvidia-smi || nvlink"'
```

**Sources:** [Makefile:149-160](), [tests/e2e/README.md]()

### e2e-dra

Runs the Dynamic Resource Allocation (DRA) e2e scenario:

- Creates kind cluster with DRA config
- Deploys nvml-mock with DRA support
- Installs NVIDIA DRA driver
- Validates DRA resource claims and scheduling

**Sources:** [Makefile:151](), [tests/e2e/README.md]()

### e2e-gpu-operator

Runs the GPU Operator integration scenario:

- Creates kind cluster with GPU Operator config
- Installs NVIDIA container toolkit
- Deploys nvml-mock
- Installs GPU Operator with validation
- Checks GPU device plugin and GFD labels

**Sources:** [Makefile:153](), [tests/e2e/README.md]()

### e2e-multi-node

Runs a multi-node heterogeneous cluster scenario with different GPU profiles:

- Creates cluster with multi-node topology
- Deploys appropriate nvml-mock profiles
- Validates multi-node scheduling and workloads

**Sources:** [Makefile:154](), [tests/e2e/README.md]()

### e2e-nri

Runs the node-wide NRI ambient-injection scenario for node resource injection:

- Validates injecting mock GPUs via containerd NRI plugin without explicit requests
- Confirms node feature labeling provenance integration

**Sources:** [Makefile:155](), [tests/e2e/README.md]()

### Common E2E Invocations

The e2e targets run the Go/Ginkgo suite in the `tests/e2e/go` package with options:

- `E2E_PROFILES`: JSON or space-separated list of GPU profiles (e.g., a100, gb200)
- `E2E_SKIP_BUILD`: skip Docker image build, use pre-built image instead
- `E2E_IMAGE`: the Docker image tag/ref to use
- `E2E_KEEP_CLUSTER`: whether to keep the cluster after tests
- `E2E_GINKGO_FLAGS`: extra `ginkgo` flags such as label filters

These targets are connected to the Go testing harness which owns lifecycle management: cluster creation, image build/load, Helm chart install, test execution, and diagnostics.

**Sources:** [Makefile:143-160](), [tests/e2e/README.md]()

---

## Summary of Makefile Targets

| Target           | Purpose                                                   | Usage Scenario                 |
|------------------|-----------------------------------------------------------|-------------------------------|
| `build`          | Compile `nv-ci-bot` CLI binary                            | Development, CI                |
| `fmt`            | Format Go source files in place                            | Pre-commit, local dev          |
| `verify`         | Check Go source formatting, fail if dirty                 | CI enforcement                 |
| `lint`           | Run `golangci-lint` static analysis                        | CI, local dev                  |
| `vendor`         | Update dependencies & generate vendor dir                  | Development                   |
| `check-vendor`   | Verify vendoring sync with git                             | CI checks                      |
| `modules`        | Tidy, vendor, verify all Go modules recursively            | Development                   |
| `check-modules`  | Verify modules & vendors are synced with git               | CI checks                      |
| `image-kind-node`| Build Kind node image with NVIDIA container toolkit       | Cluster setup                 |
| `cluster-create` | Create Kind cluster with custom node image & config       | Cluster setup/testing         |
| `cluster-delete` | Delete Kind cluster                                        | Clean up                     |
| `e2e`            | Run standalone nvml-mock E2E tests                         | Integration testing           |
| `e2e-dra`        | Run DRA integration e2e scenario                           | Integration testing           |
| `e2e-gpu-operator`| Run GPU Operator integration e2e scenario                  | Integration testing           |
| `e2e-multi-node` | Run multi-node heterogeneous cluster e2e scenario         | Integration testing           |
| `e2e-nri`        | Run node-wide NRI ambient injection e2e scenario          | Integration testing           |

---

## Usage Flow Diagrams Bridging Natural Language to Code

### Makefile Targets to Code Areas

```mermaid
graph TD
    build["make build<br/>Invokes Go build"]
    vendor["make vendor<br/>Manages Go modules"]
    lint["make lint<br/>Runs golangci-lint"]
    cluster_create["make cluster-create<br/>Creates Kind cluster"]
    e2e["make e2e<br/>Runs Go/Ginkgo E2E suite"]
  
    build --> cmd["cmd/nv-ci-bot/main.go (entrypoint)"]
    vendor --> gomod["Various go.mod files"]
    lint --> lintconfig[".golangci.yml (linter config)"]
    cluster_create --> kindfiles["local/kind/*.kind.yaml"]
    e2e --> tests_e2e["tests/e2e/go/e2e_suite_test.go (Ginkgo harness)"]
    e2e --> framework["tests/e2e/go/framework/harness/harness.go"]
```

**Sources:** [Makefile:11-160](), [tests/e2e/go/e2e_suite_test.go:6-63](), [tests/e2e/go/framework/harness/harness.go:1-99]()

---

### E2E Test Scenario Workflow (Natural Language to Go Code)

```mermaid
flowchart LR
    Start["Start: make e2e"]
    BuildImg["Build nvml-mock image (unless E2E_SKIP_BUILD)"]
    ClusterSetup["Create Kind cluster or attach Existing"]
    LoadImg["Load image into Kind cluster"]
    HelmInstall["Helm upgrade --install nvml-mock with GPU profile"]
    RunTests["Run Ginkgo tests for profile"]
    CollectDiag["Collect diagnostics on test failure"]
    Cleanup["Teardown cluster unless E2E_KEEP_CLUSTER"]

    Start --> BuildImg --> ClusterSetup --> LoadImg --> HelmInstall --> RunTests
    RunTests -->|Fail| CollectDiag
    RunTests --> Cleanup
```

Go code involved:

- `SynchronizedBeforeSuite` builds image ([tests/e2e/go/e2e_suite_test.go:52-62]())
- `setupCluster` creates or attaches cluster ([tests/e2e/go/suite_cluster.go:60-77]())
- `installDemoChart` runs Helm install/upgrade ([tests/e2e/go/suite_helm.go:36-46]())
- Test scenario files run Ginkgo specs ([tests/e2e/go/scenario_standalone_test.go](not cited))
- Diagnostics collection ([tests/e2e/go/suite_cluster.go:44-51]())

**Sources:** [Makefile:143-160](), [tests/e2e/go/e2e_suite_test.go:40-62](), [tests/e2e/go/suite_cluster.go:42-52](), [tests/e2e/go/suite_helm.go:29-47]()

---

## Special Notes

### Missing `BINARY_NAME` in build target

The `build` target references `$(BINARY_NAME)` without defining it in the Makefile. This is intentional. The variable is expected to be provided externally via:

- Environment variable
- Command line argument
- CI workflow configuration

This allows flexible builds for different binaries.

**Sources:** [Makefile:30-32]()

### Vendoring Management Philosophy

Vendoring is used to ensure repeatable builds and to avoid external dependency resolution failures.

- `vendor` updates vendor dir and verifies modules
- `check-vendor` and `check-modules` ensure no drifts in dependencies and vendoring layout
- Multi-module support covers nested Go modules in the repo

**Sources:** [Makefile:44-79]()

---

# End of Makefile Reference

**Sources:**  
- [Makefile:1-160]()  
- [tests/e2e/go/e2e_suite_test.go:6-62]()  
- [tests/e2e/go/suite_cluster.go:42-52]()  
- [tests/e2e/go/suite_helm.go:29-47]()  
- [tests/e2e/README.md:1-140]()

---

# Page: Docker Images

# Docker Images

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cmd/fake-imex/ctl/main.go](cmd/fake-imex/ctl/main.go)
- [cmd/fake-imex/daemon/main.go](cmd/fake-imex/daemon/main.go)
- [cmd/fake-imex/integration_test.go](cmd/fake-imex/integration_test.go)
- [deployments/kind-nvidia-cdi/Dockerfile](deployments/kind-nvidia-cdi/Dockerfile)
- [deployments/kind-nvidia-cdi/Makefile](deployments/kind-nvidia-cdi/Makefile)
- [deployments/kind-nvidia-cdi/containerd-config.toml](deployments/kind-nvidia-cdi/containerd-config.toml)
- [deployments/kind-nvidia-cdi/nvidia-container-runtime.toml](deployments/kind-nvidia-cdi/nvidia-container-runtime.toml)
- [deployments/nvml-mock/Dockerfile](deployments/nvml-mock/Dockerfile)
- [deployments/nvml-mock/Dockerfile.compute-domain-daemon](deployments/nvml-mock/Dockerfile.compute-domain-daemon)
- [docs/demo/compute-domain/README.md](docs/demo/compute-domain/README.md)
- [docs/demo/compute-domain/run.sh](docs/demo/compute-domain/run.sh)
- [pkg/gpu/mockcuda/Makefile](pkg/gpu/mockcuda/Makefile)
- [pkg/gpu/mocknvml/Dockerfile](pkg/gpu/mocknvml/Dockerfile)
- [pkg/gpu/mocknvml/Makefile](pkg/gpu/mocknvml/Makefile)
- [pkg/imexcoord/coord.go](pkg/imexcoord/coord.go)
- [tests/e2e/kind-compute-domain-config.yaml](tests/e2e/kind-compute-domain-config.yaml)
- [tests/e2e/spike-nvidia-smi.sh](tests/e2e/spike-nvidia-smi.sh)
- [tests/mocknvml/Dockerfile](tests/mocknvml/Dockerfile)
- [tests/poc-validation/setup-kind-cluster.sh](tests/poc-validation/setup-kind-cluster.sh)

</details>



## Purpose and Scope

This page describes the Docker images maintained within the k8s-test-infra repository, focusing on the primary images involved in GPU device simulation, cluster integration, and testing: the **development image**, the **nvml-mock image**, the **kind-nvidia-cdi image**, and the **compute-domain-daemon image**. It explains their purposes, how they are built, and details multi-stage builds and binary artifact management.

These images are key components enabling GPU simulation via mock libraries, cluster runtime injection, and fabric simulation for Kubernetes test infrastructure.

---

## Docker Images Overview

| Image                         | Location                                      | Base Image          | Primary Purpose                                                                                     |
|-------------------------------|-----------------------------------------------|---------------------|--------------------------------------------------------------------------------------------------|
| **Development Image**          | `deployments/devel/Dockerfile`                 | `golang:1.25.4`     | Development toolchain and Go version source of truth                                             |
| **nvml-mock Image**            | `deployments/nvml-mock/Dockerfile`              | Multi-stage, `golang:1.26.5-bookworm` and `debian:bookworm-slim` | Core mock NVML library, mock CUDA, mock IB/PCI libs, runtime binaries, and nvidia-smi for GPU simulation |
| **kind-nvidia-cdi Image**      | `deployments/kind-nvidia-cdi/Dockerfile`         | (Not provided here) | Containerized NVIDIA Container Device Interface (CDI) runtime for Kubernetes Kind clusters       |
| **compute-domain-daemon Image** | `deployments/nvml-mock/Dockerfile.compute-domain-daemon` | Multi-stage, Ubuntu 22.04 and `golang:1.26.5` | Simulation overlay for ComputeDomain fabric with real `nvidia-imex` in no-GPU mode              |

---

## Development Image

### Purpose and Design

The **development image** serves two main purposes:

- A consistent **build environment** containing the Go toolchain and dependencies for compiling Go binaries like `nv-ci-bot`.
- The **version management source of truth** for the Go runtime version used throughout the system, enabling reliable dependency and build consistency across CI and local environments.

### Implementation Details

The `deployments/devel/Dockerfile` simply uses:

```dockerfile
FROM golang:1.25.4
```

This minimal image relies on the official Go base image, providing:

- Full Go toolchain
- Reliable and explicit Go version pinning for dependabot automation
- No additional multi-stage logic for simplicity and clarity

### Go Version Extraction and CI Integration

The single-line `FROM golang:<version>` is parsed by the `hack/golang-version.sh` script during CI runs to extract the Go version and propagate it through workflow jobs:

```bash
GOLANG_VERSION=$(grep -E "^FROM golang:.*$" deployments/devel/Dockerfile | grep -oE "[0-9\.]+")
```

This extracted version is then used by GitHub Actions jobs such as lint, build, and scanning to ensure version consistency.

### Diagram: Go Version Propagation Flow

```mermaid
graph TB
    DOCKERFILE["deployments/devel/Dockerfile<br/>FROM golang:1.25.4"]
    SCRIPT["hack/golang-version.sh<br/>extracts Go version"]
    VARIABLES["variables job<br/>outputs.golang_version"]
    GOLANG_JOB["golang job<br/>Go lint/build with version"]
    SCANNING["code-scanning job<br/>CodeQL etc."]

    DOCKERFILE --> SCRIPT
    SCRIPT --> VARIABLES
    VARIABLES --> GOLANG_JOB
    VARIABLES --> SCANNING
```

**Sources:** [deployments/devel/Dockerfile:15-17](), [hack/golang-version.sh:16-22](), [.github/workflows/basic-checks.yaml:22-49]()

---

## nvml-mock Image

### Purpose and Scope

The **nvml-mock Docker image** is the central runtime image providing:

- The **mock NVML shared library (`libnvidia-ml.so`)** used to intercept Nvidia GPU API calls for hardware simulation.
- Mock libraries for CUDA (`libcuda.so`), InfiniBand (`libibmocksys.so`, `libibmockumad.so`, `libibmockverbs.so`), and PCI sysfs (`libpcimocksys.so`).
- Compiled Go binaries such as:
  - `mock-ib` — mock InfiniBand daemon/binary
  - `nvml-mock-nri` — NRI plugin for Containerd integration with device injection
  - `nvml-mock-ctl` — CLI tool for runtime GPU simulation control
  - `render-pci-sysfs` — PCI device sysfs rendering helper
  - Fake IMEX daemons and fabric manager binaries used for ComputeDomain simulation
- The **real `nvidia-smi` binary**, extracted from official Nvidia utils, enabling real command compatibility against the mock drivers.

This image is deployed as a DaemonSet in Kubernetes for node-wide injection of GPU device identity and behavior.

### Multi-Stage Build Process

The image is built in two main stages:

1. **Builder Stage** (`golang:1.26.5-bookworm`):

   - Build mock NVML, CUDA, InfiniBand, and PCI system libraries by invoking `make` in their Go package directories.
   - Compile multiple Go binaries for runtime orchestration and simulation control.
   - Output all build artifacts (shared libraries and binaries) to a common `/out` directory and source library paths (`/src/pkg/...`).

2. **Runtime Stage** (`debian:bookworm-slim`):

   - Copy the compiled shared libraries and binaries from the builder stage into appropriate system locations (`/usr/local/lib`, `/usr/local/bin`, `/usr/bin`).
   - Install system packages providing InfiniBand runtime support (`infiniband-diags`, `rdma-core`, etc.)
   - Download and verify the real Nvidia `kubectl` binary for Kubernetes tooling inside the image.
   - Extract the real `nvidia-smi` binary from the Nvidia utils 580.65.06 package and patch its RPATH to enable working with the mock libraries.
   - Copy helper shell scripts for setup and cleanup tasks used at container startup.

#### Excerpt from Build Steps (simplified)

```dockerfile
# Builder stage
FROM golang:1.26.5-bookworm AS builder
WORKDIR /src
COPY go.mod go.sum ./
COPY vendor/ vendor/
COPY pkg/ pkg/
COPY cmd/ cmd/
RUN cd pkg/gpu/mocknvml && make clean && make
RUN cd pkg/gpu/mockcuda && make clean && make
RUN cd pkg/network/mockib && make clean && make
RUN cd pkg/system/mockpcisysfs && make clean && make
RUN mkdir -p /out && go build -o /out/mock-ib ./cmd/mock-ib ... (other binaries)

# Runtime stage
FROM debian:bookworm-slim
COPY --from=builder /src/pkg/gpu/mocknvml/libnvidia-ml.so.* /usr/local/lib/
COPY --from=builder /out/mock-ib /usr/local/bin/mock-ib
COPY --from=builder /out/nvml-mock-nri /usr/local/bin/nvml-mock-nri
# ... other binaries and libs copied ...
RUN apt-get update && apt-get install -y infiniband-diags rdma-core ibverbs-utils
# Download and patch nvidia-smi binary
COPY deployments/nvml-mock/scripts/ /scripts/
RUN chmod +x /scripts/*.sh
```

### Integration of Binary Artifacts and Multi-Layer Organization

- The multi-stage build allows the heavy Golang toolchain and build dependencies to remain out of the final image, optimizing size.
- Shared libraries and runtime executables are carefully placed to respect dynamic loading semantics and LD_PRELOAD mechanisms.
- Real `nvidia-smi` from the Nvidia utilities package integrates seamlessly with the mock library to validate GPU simulation.

### Diagram: nvml-mock Image Build Flow

```mermaid
graph LR
  Builder["Builder Stage (golang:1.26.5-bookworm)"]
  Runtime["Runtime Stage (debian:bookworm-slim)"]
  MakeLibs["make mocknvml, mockcuda, mockib, mockpcisysfs"]
  BuildBinaries["Go build binaries: mock-ib, nvml-mock-nri, etc."]
  CopyLibs["Copy shared libs (libnvidia-ml.so, libcuda.so, etc.)"]
  CopyBins["Copy binaries to /usr/local/bin and /usr/bin"]
  InstallDeps["Install runtime packages (InfiniBand, RDMA)"]
  NvidiaSmi["Download and patch real nvidia-smi binary"]
  SetupScripts["Copy startup/setup scripts"]

  Builder --> MakeLibs
  MakeLibs --> BuildBinaries
  BuildBinaries --> Runtime
  Runtime --> CopyLibs
  Runtime --> CopyBins
  Runtime --> InstallDeps
  Runtime --> NvidiaSmi
  Runtime --> SetupScripts
```

**Sources:** [deployments/nvml-mock/Dockerfile:15-113]()

---

## kind-nvidia-cdi Image

### Purpose

The **kind-nvidia-cdi image** provides a runtime container to support NVIDIA Container Device Interface (CDI) integration within Kind Kubernetes clusters.

This image includes:

- NVIDIA container runtime configuration (`nvidia-container-runtime.toml`)
- Containerd and CDI runtime configuration (`containerd-config.toml`)
- Supporting binaries and manifest files to enable the proper injection and management of GPU device plugins within containerd when using Kind clusters.

While the detailed Dockerfile content is not included here, the image augments Kind clusters with NVIDIA CDI support to facilitate GPU simulation and injection during testing.

**Sources:** [deployments/kind-nvidia-cdi/Dockerfile](), [deployments/kind-nvidia-cdi/containerd-config.toml]()

---

## compute-domain-daemon Image

### Purpose and Design

The **compute-domain-daemon image** extends the nvml-mock image by overlaying the **real `nvidia-imex` daemon** from the official Ubuntu 22.04 multiverse packages, running in **NO GPU mode**, for simulating NVLink fabric domains in a Kubernetes cluster.

It provides:

- Real `nvidia-imex` and `nvidia-imex-ctl` binaries
- A shim executable `imex-nogpu-shim` that wraps `nvidia-imex` adding a `--nogpu` flag to simulate fabric management without actual GPUs
- Runs on Ubuntu 22.04 base for compatibility with the proprietary driver binaries

This image is primarily used for the **ComputeDomain NVLink fabric simulation**, replacing previous deprecated fake implementations and enabling real gRPC communication over the pod network.

### Multi-Stage Build Details

- **imex Stage**: Ubuntu 22.04 image installs `nvidia-imex-595` package, verifying version, copying real binaries.
- **shim Stage**: Go build on `golang:1.26.5` produces the `imex-nogpu-shim` binary.
- **demo Target**: Builds an overlay image on `nvml-mock` image that installs the real `nvidia-imex` binaries and the shim at their canonical paths, along with configuration files.
- **daemon Target (default)**: Overlays the real `nvidia-imex` and the shim on the official `dra-driver-nvidia-gpu` image from registry.k8s.io, used in the actual DaemonSet deployment.

### Diagram: compute-domain-daemon Image Multi-Stage Build

```mermaid
graph TD
  IMEX[Ubuntu 22.04 + nvidia-imex-595 package]
  SHIM[golang:1.26.5 build imex-nogpu-shim]
  NVMLMOCK[nvml-mock image]
  DEMO["demo target:<br/>nvml-mock + real nvidia-imex + shim"]
  UPSTREAM["Upstream dra-driver-nvidia-gpu image"]
  DAEMON["daemon target:<br/>Upstream image + real nvidia-imex + shim"]

  IMEX --> DEMO
  SHIM --> DEMO
  NVMLMOCK --> DEMO
  IMEX --> DAEMON
  SHIM --> DAEMON
  UPSTREAM --> DAEMON
```

### Runtime Behavior

- The shim binary emulates `nvidia-imex` but appends `--nogpu` to arguments to run the real upstream daemon without GPU hardware.
- This approach removes reliance on deprecated fake daemons and enables a more faithful fabric simulation for NVLink ComputeDomain testing.
- The `fake-imex` binaries and deprecated code remain present but replaced by this real binary overlay.

**Sources:** [deployments/nvml-mock/Dockerfile.compute-domain-daemon:1-88](), [cmd/fake-imex/daemon/main.go:14-101](), [docs/demo/compute-domain/README.md:1-130]()

---

## Multi-Stage Builds and Binary Artifacts Summary

The project embraces **multi-stage Docker builds** to:

- Isolate compilation of C-shared libraries and Go binaries within fully featured Golang build environments.
- Export minimal runtime images containing only necessary runtime libraries, compiled shared objects, and indispensable binaries.
- Layer proprietary binaries (e.g., real `nvidia-imex`, `nvidia-smi`) from external package repositories into images where allowed, enabling hybrid real/mocked GPU simulation.
- Ensure small footprint, maintainability, and clarity between build and runtime dependencies.

**Key Binary Artifacts:**

| Artifact                | Source Location                          | Role                                                             |
|------------------------|-----------------------------------------|------------------------------------------------------------------|
| `libnvidia-ml.so`       | `pkg/gpu/mocknvml` (built via Makefile)   | Mock NVML shared library for Nvidia API interception             |
| `libcuda.so`            | `pkg/gpu/mockcuda` (built via Makefile)    | Mock CUDA library for simulating CUDA runtime calls              |
| `libibmocksys.so`, `libibmockumad.so`, `libibmockverbs.so` | `pkg/network/mockib`                 | Mock InfiniBand libraries for RDMA simulation                     |
| `libpcimocksys.so`      | `pkg/system/mockpcisysfs`                   | PCI sysfs mock library                                             |
| `mock-ib`, `nvml-mock-nri`, `nvml-mock-ctl`, `render-pci-sysfs` | `cmd/*` directories                   | Support daemons, CLI tools, and runtime plugins for simulation   |
| `nvidia-imex` and `nvidia-imex-ctl` (real binaries) | Ubuntu multiverse packages             | NVLink fabric daemon and control binaries worn for ComputeDomain |
| `imex-nogpu-shim`       | `cmd/imex-nogpu-shim` (Go shim binary)     | Shim that wraps real nvidia-imex with `--nogpu` flag             |
| `nvidia-smi` (real binary) | Extracted from `nvidia-utils-580` package | Official NVIDIA CLI tool used to validate mock behavior            |

**Sources:** [deployments/nvml-mock/Dockerfile:15-113](), [cmd/fake-imex/daemon/main.go:14-101](), [deployments/nvml-mock/Dockerfile.compute-domain-daemon:1-88]()

---

## Code Entity Association Diagrams

### Image-Source Code Mapping: nvml-mock Image Components

```mermaid
graph LR
  subgraph nvml-mock Dockerfile
    Builder[Builder Stage]
    Runtime[Runtime Stage]
  end

  Builder --> MockNVML[Make pkg/gpu/mocknvml (Makefile, Dockerfile)]
  Builder --> MockCUDA[Make pkg/gpu/mockcuda]
  Builder --> MockIB[Make pkg/network/mockib]
  Builder --> MockPCI[Make pkg/system/mockpcisysfs]
  Builder --> BuildBinaries["build cmd/mock-ib, nvml-mock-nri, nvml-mock-ctl, render-pci-sysfs, fake-imex"]
  
  Runtime --> CopyLibs["Copy libnvidia-ml.so*, libcuda.so* etc."]
  Runtime --> CopyBins["Copy mock-ib, nvml-mock-nri, nvml-mock-ctl, nvidia-imex binaries"]
  Runtime --> InstallDeps["Install InfiniBand related packages"]
  Runtime --> DownloadNvidiaSmi["Download and patch real nvidia-smi"]
  
  MockNVML -.-> "pkg/gpu/mocknvml/Makefile" & "Dockerfile"
  MockCUDA -.-> "pkg/gpu/mockcuda/Makefile"
  MockIB -.-> "pkg/network/mockib/Makefile"
  MockPCI -.-> "pkg/system/mockpcisysfs/Makefile"
  BuildBinaries -.-> "cmd/*/main.go files (e.g. cmd/mock-ib/main.go)"
```

### Image-Source Code Mapping: ComputeDomain Daemon Image Components

```mermaid
graph LR
  subgraph compute-domain-daemon Dockerfile
    imex[imex Stage: ubuntu + nvidia-imex-595]
    shim[shim Stage: golang build imex-nogpu-shim]
    nvml_mock[nvml-mock base image]
    demo["demo target: nvml-mock + real nvidia-imex + shim"]
    daemon["daemon target: upstream dra-driver-nvidia + real nvidia-imex + shim"]
  end

  imex --> demo
  shim --> demo
  nvml_mock --> demo
  imex --> daemon
  shim --> daemon
  upstream["upstream dra-driver-nvidia gpu image"] --> daemon

  shim -.-> "cmd/imex-nogpu-shim/"
  imex -.-> "Ubuntu multiverse nvidia-imex-595 package"
  nvml_mock -.-> "deployments/nvml-mock/Dockerfile"
  upstream -.-> "registry.k8s.io/dra-driver-nvidia/dra-driver-nvidia-gpu"
```

---

## Summary

| Image Name             | Purpose                                                | Build Highlights                                           | Key Files / Packages                          |
|------------------------|--------------------------------------------------------|-------------------------------------------------------------|-----------------------------------------------|
| Development Image      | Base Go build environment and Go version management    | Simple single-stage FROM golang:<version>                    | `deployments/devel/Dockerfile`                 |
| nvml-mock Image        | Mock NVML and related shared libs + binaries for GPU simulation in Kubernetes | Multi-stage build compiling mock libraries, binaries, integrating real `nvidia-smi` | `deployments/nvml-mock/Dockerfile`, `pkg/gpu/mocknvml/Makefile` |
| kind-nvidia-cdi Image  | NVIDIA CDI support for Kind clusters                    | Not detailed here                                           | `deployments/kind-nvidia-cdi/` directory       |
| compute-domain-daemon  | ComputeDomain fabric simulation with real `nvidia-imex` in NO GPU mode | Multi-stage overlay layering real IMEX binary and shim on base images | `deployments/nvml-mock/Dockerfile.compute-domain-daemon` |

These Docker images provide a robust, flexible foundation for simulating GPU functionality, device plugin injection, and fabric simulation within Kubernetes test environments built by k8s-test-infra.

**Sources:**  
- [deployments/devel/Dockerfile:15-17]()  
- [deployments/nvml-mock/Dockerfile:15-113]()  
- [pkg/gpu/mocknvml/Makefile:1-145]()  
- [deployments/nvml-mock/Dockerfile.compute-domain-daemon:1-88]()  
- [cmd/fake-imex/daemon/main.go:14-101]()  
- [docs/demo/compute-domain/README.md]()  
- [tests/poc-validation/setup-kind-cluster.sh:1-126]()

---

# Page: Go Version Management Strategy

# Go Version Management Strategy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/code_scanning.yaml](.github/workflows/code_scanning.yaml)
- [.github/workflows/golang.yaml](.github/workflows/golang.yaml)
- [.github/workflows/helm-publish.yaml](.github/workflows/helm-publish.yaml)
- [.github/workflows/helm.yaml](.github/workflows/helm.yaml)
- [.github/workflows/nvml-mock-publish.yaml](.github/workflows/nvml-mock-publish.yaml)
- [.github/workflows/scorecard.yaml](.github/workflows/scorecard.yaml)
- [.github/workflows/variables.yaml](.github/workflows/variables.yaml)
- [deployments/devel/Dockerfile](deployments/devel/Dockerfile)
- [deployments/nvml-mock/Dockerfile](deployments/nvml-mock/Dockerfile)
- [pkg/gpu/mockcuda/Makefile](pkg/gpu/mockcuda/Makefile)
- [pkg/gpu/mocknvml/Dockerfile](pkg/gpu/mocknvml/Dockerfile)
- [pkg/gpu/mocknvml/Makefile](pkg/gpu/mocknvml/Makefile)
- [tests/e2e/spike-nvidia-smi.sh](tests/e2e/spike-nvidia-smi.sh)
- [tests/mocknvml/Dockerfile](tests/mocknvml/Dockerfile)
- [tests/poc-validation/setup-kind-cluster.sh](tests/poc-validation/setup-kind-cluster.sh)

</details>



## Purpose and Scope

This document details how the Go programming language version is defined, extracted, and propagated consistently throughout the k8s-test-infra project. It describes the single source of truth defining the Go version in the development Dockerfile, the script and workflows that extract and distribute this version in CI/CD pipelines, and discusses the automation of version upgrades via Dependabot.

## Overview

The project centralizes the Go version specification in a single Dockerfile which serves both as the development environment image and the canonical reference for the Go version. A shell script extracts this version and, through a dedicated reusable workflow, it is distributed as an output variable to other GitHub Actions workflows that perform linting, testing, and security scanning. This approach enforces Go version consistency across local development, automated CI builds, and container images.

**Sources:** [deployments/devel/Dockerfile:15-17]()

---

## Single Source of Truth: Development Dockerfile

The authoritative Go version is set in the base image declaration in the `deployments/devel/Dockerfile`. The relevant line is:

```dockerfile
FROM golang:1.26.5
```

This Dockerfile serves a dual role:

- Defines the development environment container image used locally and in CI
- Establishes the canonical Go version for the project

This avoids duplication and enables automated external version management tools to monitor it easily.

```dockerfile
# This Dockerfile is also used to define the golang version used in this project
# This allows dependabot to manage this version in addition to other images.
FROM golang:1.26.5
```

**Sources:** [deployments/devel/Dockerfile:15-17]()

---

## Version Extraction Mechanism

### `hack/golang-version.sh` Script

The project uses a shell script (`hack/golang-version.sh`) that extracts the Go version from the Dockerfile by searching for the `FROM golang:` line and pulling out the version string.

Example extraction command from the script:

```bash
GOLANG_VERSION=$(grep -E "^FROM golang:.*$" ${DOCKERFILE_ROOT}/Dockerfile | grep -oE "[0-9\.]+")
echo "${GOLANG_VERSION}"
```

The script works by:

1. Locating the Dockerfile in the project relative to the script location.
2. Grepping lines starting with `FROM golang:` (to exclude comments or other FROM lines).
3. Extracting only the numeric portion representing the Go version.
4. Echoing the version string.

This script ensures any CI or developer environment using it stays in sync with the Dockerfile version without manual updates.

**Sources:** [hack/golang-version.sh:16-22]() (referenced content derived from the invocation pattern)

---

## Propagation Through CI/CD Pipelines

The extracted Go version is propagated through GitHub Actions workflows as a parameter to ensure consistent Go tooling versions across tasks.

### Overview Diagram: Go Version Propagation Flow

```mermaid
graph TB
  DF["deployments/devel/Dockerfile:17<br/>FROM golang:1.26.5"]
  SCRIPT["hack/golang-version.sh<br/>Extract script"]
  VARS["variables.yaml workflow<br/>variables job"]
  GOLANG_WF["golang.yaml workflow<br/>check job"]
  CODEQL_WF["code_scanning.yaml workflow<br/>analyze job"]
  SETUP_GO1["actions/setup-go@v6<br/>in golang workflow"]
  SETUP_GO2["actions/setup-go@v6<br/>in code_scanning workflow"]

  DF -->|Reads base image version| SCRIPT
  SCRIPT -->|Called by| VARS
  VARS -->|Output: golang_version| GOLANG_WF
  VARS -->|Output: golang_version| CODEQL_WF
  GOLANG_WF -->|Uses| SETUP_GO1
  CODEQL_WF -->|Uses| SETUP_GO2

  subgraph "Single Source"
    DF
  end

  subgraph "Extraction Layer"
    SCRIPT
    VARS
  end

  subgraph "Consumers"
    GOLANG_WF
    CODEQL_WF
  end

  subgraph "Go Installation"
    SETUP_GO1
    SETUP_GO2
  end
```

**Sources:** [.github/workflows/variables.yaml](), [.github/workflows/golang.yaml](), [.github/workflows/code_scanning.yaml]()

---

### Stage 1: Variables Workflow (`variables.yaml`)

The reusable [`variables.yaml` workflow](.github/workflows/variables.yaml) performs the extraction:

- Checks out the code
- Runs `./hack/golang-version.sh`
- Outputs the extracted `golang_version` as a value accessible by downstream workflows

YAML snippet showing extraction and output:

```yaml
jobs:
  variables:
    runs-on: ubuntu-latest
    outputs:
      golang_version: ${{ steps.golang_version.outputs.golang_version }}
    steps:
      - name: Check out code
        uses: actions/checkout@v7
      - name: Get Golang Version
        id: golang_version
        run: |
          GOLANG_VERSION=$(./hack/golang-version.sh)
          echo "Detected $GOLANG_VERSION"
          echo "golang_version=${GOLANG_VERSION}" >> $GITHUB_OUTPUT
```

Outputs block:

```yaml
outputs:
  golang_version:
    description: "The golang version for this project"
    value: ${{ jobs.variables.outputs.golang_version }}
```

This output becomes an input for other workflows.

**Sources:** [.github/workflows/variables.yaml:31-50]()

---

### Stage 2: Consumer Workflows

Workflows such as [`golang.yaml`](.github/workflows/golang.yaml) and [`code_scanning.yaml`](.github/workflows/code_scanning.yaml) receive the Go version as an input parameter and use it to install the correct Go version via `actions/setup-go`.

- `golang.yaml` defines input:

```yaml
on:
  workflow_call:
    inputs:
      golang_version:
        required: true
        type: string
```

- Usage in Go setup step:

```yaml
- name: Install Go
  uses: actions/setup-go@v7
  with:
    go-version: ${{ inputs.golang_version }}
```

This appears in both golang linting/testing and security scanning workflows, ensuring the exact same Go version is installed and used in all CI steps.

**Sources:** [.github/workflows/golang.yaml:17-38](), [.github/workflows/code_scanning.yaml:18-54]()

---

### Stage 3: Orchestration Workflow

A high-level orchestrator workflow (e.g. `.github/workflows/basic-checks.yaml`) calls these reusable workflows, wiring outputs to inputs:

```yaml
jobs:
  variables:
    uses: ./.github/workflows/variables.yaml

  golang:
    needs: variables
    uses: ./.github/workflows/golang.yaml
    with:
      golang_version: ${{ needs.variables.outputs.golang_version }}

  code-scanning:
    needs: variables
    uses: ./.github/workflows/code_scanning.yaml
    with:
      golang_version: ${{ needs.variables.outputs.golang_version }}
```

This creates a dependency graph:

- `variables` extracts and outputs Go version
- `golang` and `code-scanning` consume this version
- Ensures a single Go version source and consistent installs

**Sources:** [.github/workflows/basic-checks.yaml:34-49]() (based on typical pattern references)

---

## Workflow Invocation Sequence Diagram

```mermaid
sequenceDiagram
  participant BC as basic-checks.yaml<br/>orchestrator
  participant VW as variables.yaml<br/>reusable workflow
  participant SH as golang-version.sh<br/>extraction script
  participant DF as deployments/devel/Dockerfile
  participant GW as golang.yaml<br/>lint workflow
  participant CW as code_scanning.yaml<br/>security workflow

  BC->>VW: Workflow call trigger
  VW->>SH: Run extraction script
  SH->>DF: grep "FROM golang:" to extract Go version
  DF-->>SH: Return base image line with version
  SH-->>VW: Output Go version string
  VW-->>BC: Export golang_version output

  BC->>GW: Call golang workflow with golang_version input
  GW->>GW: Setup Go environment with correct version
  GW->>GW: Run linting and test steps

  BC->>CW: Call code_scanning workflow with golang_version input
  CW->>CW: Setup Go environment with correct version
  CW->>CW: Run CodeQL analysis and security scanning
```

**Sources:** [.github/workflows/basic-checks.yaml](), [.github/workflows/variables.yaml](), [hack/golang-version.sh](), [.github/workflows/golang.yaml](), [.github/workflows/code_scanning.yaml]()

---

## Dependabot Integration

Dependabot monitors `deployments/devel/Dockerfile` for updates to the `golang` base image version.

When a new Go version is released, Dependabot will:

- Detect the outdated Go base image line (`FROM golang:X.Y.Z`)
- Create a pull request updating it to the new version
- Trigger CI to validate compatibility

This automation is enabled because the Dockerfile is the single source of truth for the Go version across the ecosystem.

Typical Dependabot config (not shown in code but implied):

```yaml
- package-ecosystem: "docker"
  directory: "/deployments/devel"
  schedule:
    interval: "daily"
```

Automating version updates this way reduces manual maintenance effort while preserving version consistency.

**Sources:** [deployments/devel/Dockerfile:15-17]()

---

## Design Rationale

| Aspect | Explanation |
|--------|-------------|
| **Why Dockerfile as Single Source?** | Dependabot natively supports detecting base image updates via Dockerfiles, enabling automated PR creation. The Dockerfile also directly configures the builds and dev container environment, so coupling it to version control avoids discrepancies. |
| **Avoid Duplication of Version Settings** | Alternative approaches (such as `.go-version` files or go.mod toolchain directives) do not benefit from Dependabot updating Docker base images and would cause version fragmentation. |
| **Extraction Simplicity and Reliability** | The `FROM golang:` line is easy to parse with simple grep commands, reducing complexity and brittle parsing logic. |

**Sources:** [deployments/devel/Dockerfile:15-17]()

---

## Usage Examples

### Checking Current Go Version

Run the extraction script:

```bash
./hack/golang-version.sh
```

Or directly grep the Dockerfile:

```bash
grep "FROM golang" deployments/devel/Dockerfile
```

### Updating Go Version

1. Edit `deployments/devel/Dockerfile` to update the `golang` version tag.
2. Commit and create a pull request.
3. CI will propagate and use the updated version automatically.
4. Alternatively, wait for Dependabot to create a PR for the update.

### Local Development

Developers can modify their local `deployments/devel/Dockerfile` for testing with a different Go version and verify with the extraction script without committing the change.

**Sources:** [deployments/devel/Dockerfile:15-17](), [hack/golang-version.sh]()

---

## Maintenance and Best Practices

- The `hack/golang-version.sh` script relies on the `FROM golang:` line appearing exactly once and syntactically unchanged. Changes in line format will require adapting the grep regex.
- The extraction script uses relative paths to remain directory-agnostic.
- Workflows triggering CI runs are configured to run on pull request and branch push events ensuring Go version consistency checks on all changes.

**Sources:** [.github/workflows/ci.yaml:16-21](), [.github/workflows/basic-checks.yaml:25-31]()

---

## Summary Table

| Principle                          | Implementation                                            |
|----------------------------------|-----------------------------------------------------------|
| **Single Source of Truth**         | Defined Go version in `deployments/devel/Dockerfile`      |
| **Automated Extraction**           | `hack/golang-version.sh` parses Dockerfile for Go version |
| **Distribution via Workflow Outputs** | `variables.yaml` exports `golang_version` to other workflows |
| **Consistent Environment Setup**  | All workflows use `actions/setup-go@v6` with extracted version |
| **Automated Version Updates**     | Dependabot tracks and updates the Dockerfile Go base image |

This strategy ensures all environments remain synchronized on the Go version, minimizing divergence and manual updates.

**Sources:** [deployments/devel/Dockerfile](), [hack/golang-version.sh](), [.github/workflows/variables.yaml](), [.github/workflows/golang.yaml](), [.github/workflows/code_scanning.yaml](), [.github/workflows/basic-checks.yaml]()

---

# Page: nvml-mock System

# nvml-mock System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deployments/nvml-mock/helm/nvml-mock/README.md](deployments/nvml-mock/helm/nvml-mock/README.md)
- [deployments/nvml-mock/helm/nvml-mock/templates/daemonset.yaml](deployments/nvml-mock/helm/nvml-mock/templates/daemonset.yaml)
- [deployments/nvml-mock/helm/nvml-mock/values.schema.json](deployments/nvml-mock/helm/nvml-mock/values.schema.json)
- [deployments/nvml-mock/helm/nvml-mock/values.yaml](deployments/nvml-mock/helm/nvml-mock/values.yaml)
- [deployments/nvml-mock/scripts/cleanup.sh](deployments/nvml-mock/scripts/cleanup.sh)
- [deployments/nvml-mock/scripts/setup.sh](deployments/nvml-mock/scripts/setup.sh)
- [docs/README.md](docs/README.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/demo/kind.yaml](docs/demo/kind.yaml)
- [docs/demo/with-fgo/README.md](docs/demo/with-fgo/README.md)
- [docs/examples.md](docs/examples.md)
- [docs/integrations/fake-gpu-operator.md](docs/integrations/fake-gpu-operator.md)
- [docs/quickstart.md](docs/quickstart.md)
- [pkg/gpu/mocknvml/README.md](pkg/gpu/mocknvml/README.md)
- [pkg/gpu/mocknvml/bridge/padding.go](pkg/gpu/mocknvml/bridge/padding.go)

</details>



The **nvml-mock System** represents the core GPU simulation subsystem in the `k8s-test-infra` repository. It provides a sophisticated mock implementation of NVIDIA's NVML library and associated infrastructure, enabling comprehensive GPU simulation for Kubernetes testing environments without requiring real NVIDIA hardware. This simulation supports realistic device discovery, querying, and monitoring workflows, facilitating development and testing of GPU-aware Kubernetes components including device plugins, the Dynamic Resource Allocation (DRA) driver, GPU Operator, Node Feature Discovery (NFD), and other tooling.

This page offers a high-level overview of the nvml-mock system, summarizing its key components and how they interrelate. It serves as a parent to detailed child documents covering the implementation internals, configuration options, deployment via Helm, simulation of advanced GPU fabric features, node-wide injection, and runtime control utilities.

---

## Overview of nvml-mock

At its core, nvml-mock delivers a **mock NVML shared library** (`libnvidia-ml.so`) built with CGo and implemented in Go. When injected or deployed within Kubernetes pods, this library exposes a full NVML API surface that mimics real GPUs according to user-supplied YAML profiles (e.g., simulating A100, H100, GB200 GPUs). Key APIs like `nvidia-smi` and DCGM telemetry tools work transparently against the mock, enabling rich testing scenarios.

The GPU simulation is orchestrated via a **DaemonSet** deployed by a Helm chart, which runs on every Kubernetes node constituting the cluster. This DaemonSet mounts the mock library, creates device nodes, configures GPU profiles, and exposes node labels and NFD feature files to simulate NVIDIA GPU presence.

The mock system also optionally includes rich **failover and failure injection** modes to test edge cases, and supports **dynamic metrics** (e.g., temperature and utilization fluctuations) to simulate time-varying workloads.

Further, advanced subsystems simulate GPU fabric components like **NVLink, PCIe topology, InfiniBand (IB)**, and multi-node collective GPU communication fabrics (**ComputeDomain and IMEX**). These enable testing of GPU interconnect topologies and network-based resource management in multi-node clusters.

Ambient injection of the mock environment into arbitrary pod containers is supported via a **containerd NRI plugin**, allowing pods without explicit GPU resource requests to use the mock NVML library seamlessly. Runtime control of GPU device states is possible through a CLI (`nvml-mock-ctl`) that interacts over the established daemon.

The sections below briefly introduce each major sub-area, linking to respective child pages for comprehensive technical details.

---

## 1. Mock NVML Library Internals

The mock NVML library is implemented in Go with a **CGo bridge layer** that exposes the NVML C API symbols compatible with the real `libnvidia-ml.so`. This bridge delegates calls into an Engine singleton, which contains the state of all mock devices managed in a **HandleTable**. Each mock GPU is represented by a `ConfigurableDevice` struct holding its configuration and dynamic state updated from YAML profiles and runtime overrides.

A code-generation tool named `generate-bridge` automates the creation of the C-to-Go CGo signature mappings, ensuring scalability and consistency across ~400 NVML API calls.

The internals emphasize thread safety and concurrent access for accurate simulation of parallel NVML client workloads. The Engine also supports event emission, failure injection, and mixing static and dynamic GPU metrics.

For full technical details including class structure, concurrency model, and CGo interop patterns, see [Mock NVML Library Internals](#9.1).

```mermaid
%% Mock NVML Internals Overview
graph TB
  subgraph CGo Bridge Layer
    C[libnvidia-ml.so: exported NVML C API symbols]
    C -->|calls into| G[Go Engine singleton]
  end
  subgraph Engine Components
    G --> HT[HandleTable: manages nvmlHandles]
    G --> CD[ConfigurableDevice: per-GPU state & config]
    G --> CFG[Loads YAMLConfig profiles]
  end
  subgraph Tools
    TB[generate-bridge: CGo stub generator]
  end

  classDef codeEntity fill:#eee,stroke:#333,stroke-width:0.5px,font-family:monospace;
  class C,G,HT,CD,CFG,TB codeEntity;
```

_Sources:_
- `pkg/gpu/mocknvml/README.md:1-150`()

---

## 2. GPU Configuration and Profiles

GPU simulation is driven by YAML configuration profiles that declare device properties including memory size, power limits, PCI bus topology, clock rates, and supported features. Multiple built-in profiles exist, covering common hardware such as:

- `a100` (NVIDIA A100-SXM4-40GB)
- `h100` (NVIDIA H100 80GB HBM3)
- `b200`, `gb200`, `gb300` (Blackwell-series GPUs)
- `l40s` (Ada Lovelace L40S)
- `t4` (Turing Tesla T4)

The configuration structure includes a `system` section for driver versions, default device templates, and a list of `devices` with per-GPU overrides.

Dynamic simulation of **time-varying metrics** such as temperature, power draw, and utilization is available and can be enabled per field to better exercise consumers expecting fluctuating sensor data.

A robust **failure injection** subsystem allows deterministic or probabilistic simulation of GPU failures like device loss, "fallen off bus" events, and ECC uncorrectable errors, enabling fault-tolerant test scenarios.

Configuration resolution applies in the order: Helm chart defaults < GPU profile YAML < user overrides (e.g., via Helm or runtime CLI). This design guarantees the GPU simulation behaves as intended across various deployment contexts.

For in-depth documentation of YAML syntax, profile variants, and metric/failure injection mechanisms, refer to [GPU Configuration and Profiles](#9.2).

```mermaid
%% GPU Config and Profiles Mapping
graph LR
  H[Helm Chart Defaults]
  Y[GPU Profile YAML (a100, h100, gb200, ...)]
  U[User Overrides (runtime CLI)]
  H --> Y --> U --> E[Mock Engine Runtime State]
  E -->|feeds data| CD[ConfigurableDevice instances]
```

_Sources:_
- `deployments/nvml-mock/helm/nvml-mock/values.yaml:4-57`()
- `pkg/gpu/mocknvml/README.md:100-350`()

---

## 3. Helm Chart Deployment

nvml-mock provides a fully featured **Helm chart** to deploy the GPU mock system to Kubernetes clusters. The chart deploys a privileged **DaemonSet** that runs on all selected nodes and performs the following actions:

- Installs the mock NVML shared library at `/var/lib/nvml-mock/driver/usr/lib64/libnvidia-ml.so.*`
- Creates device nodes under `/var/lib/nvml-mock/driver/dev/nvidia*`
- Places the GPU configuration YAML at `/var/lib/nvml-mock/driver/config/config.yaml`
- Writes node labels like `nvidia.com/gpu.present=true` directly to the nodes
- Generates NFD (Node Feature Discovery) feature files for PCI vendor presence
- Creates fake PCI and InfiniBand sysfs trees with respective LD_PRELOAD shim injections
- Optionally launches auxiliary daemons like fake fabricmanager or nvidia-imex

The chart integrates with NVIDIA's Container Device Interface (CDI) to allow easy injection of the mock driver into pods, preserving the expected device environment.

When enabled via values, a **containerd NRI plugin** daemon runs on nodes to ambiently inject the overlay mount and environment variables into all containers, avoiding the need for explicit pod-level device requests or volume mounts.

Standard Helm features such as resource requests/limits, node selectors, tolerations, and update strategies are supported for cluster integration.

Host environment setup and cleanup are orchestrated by container entrypoint scripts `setup.sh` and `cleanup.sh`, which create device nodes, handle symbolic links, and manage node labels and feature files.

For detailed Helm values, chart structure, and deployment procedures, see [Helm Chart Deployment](#9.3).

```mermaid
%% Helm Deployment Architecture
graph LR
  subgraph Helm Chart
    DS[DaemonSet: nvml-mock]
    NRI[Optional: nvml-mock-nri DaemonSet]
    CM[ConfigMap: GPU profile config.yaml]
  end

  DS -->|Mounts| LIB["libnvidia-ml.so driver files at /var/lib/nvml-mock/driver/usr/lib64/"]
  DS -->|Creates| DEV["Mock device nodes (/dev/nvidia*)"]
  DS -->|Writes| CONF["GPU Config YAML (/var/lib/nvml-mock/driver/config/config.yaml)"]
  DS -->|Sets| LABELS["Node labels (nvidia.com/gpu.present) & NFD feature files"]
  DS -->|Runs| SHIMS["IB and PCIe simulation shims (LD_PRELOAD)"]
```

_Sources:_
- `deployments/nvml-mock/helm/nvml-mock/README.md:1-135`()
- `deployments/nvml-mock/helm/nvml-mock/templates/daemonset.yaml:1-150`()
- `deployments/nvml-mock/scripts/setup.sh:1-250`()
- `deployments/nvml-mock/scripts/cleanup.sh:1-43`()
- `deployments/nvml-mock/helm/nvml-mock/values.yaml:4-60`()

---

## 4. NVLink, InfiniBand, and PCIe Simulation

Beyond simple GPU simulation, nvml-mock simulates complex GPU fabric topology components needed by advanced schedulers and dynamic resource allocation:

- A **mock-ib daemon** emulates InfiniBand Host Channel Adapters (HCAs) with user-space verbs and UMAD shims (`libibmocksys.so`) permitting tools like `ibstat`, `ibstatus`, and `iblinkinfo` to query fake HCAs
- The **render-pci-sysfs** tool fabricates a Linux PCI sysfs topology tree under `/var/lib/nvml-mock/sys` matched to the configured GPU PCI topology — enabling PCI-aware consumers to resolve GPU location and NUMA nodes accurately
- LD_PRELOAD wrappers (`libibmocksys.so`, `libpcimocksys.so`) redirect relevant system calls to the synthetic sysfs trees while forwarding others
- NVLink field values and attributes are included in the simulated GPUs' NVML reports, supporting user-space components requiring NVLink information

This subsystem provides realistic mimicking of fabric-level topology and device attributes critical for comprehensive multi-GPU and multi-node testing.

For technical design, shim implementations, and tool usage, see [NVLink, InfiniBand, and PCIe Simulation](#9.4).

```mermaid
%% NVLink, IB, PCIe Simulation Components
graph TD
  DS_DaemonSet --> MockIB[mock-ib daemon]
  MockIB --> IB_Shims[LD_PRELOAD libibmocksys.so]
  DS_DaemonSet --> PCIe_Tree[render-pci-sysfs generated sysfs PCI tree]
  PCIe_Tree --> PCIe_Shims[LD_PRELOAD libpcimocksys.so]
  DS_DaemonSet --> NVML_Lib["libnvidia-ml.so (reports NVLink info)"]
```

_Sources:_
- `deployments/nvml-mock/helm/nvml-mock/README.md:18-24` (InfiniBand, PCI sysfs, shims)  
- `pkg/gpu/mocknvml/README.md` (overview of NVML APIs and topology)  

---

## 5. ComputeDomain and IMEX Simulation

For multi-node GPU fabric testing, nvml-mock includes a **ComputeDomain simulation**, modeling multi-node, multi-GPU interconnect fabrics such as NVSwitch linking multiple DGX-like nodes.

This involves:

- A **fake-imex daemon** simulating the NVIDIA IMEX (Interconnect Management EXchange) protocol enabling nodes to exchange fabric state and configuration
- The **imex-nogpu-shim** to emulate IMEX behavior when no real GPU hardware exists
- A **fake-fabricmanager** process providing readiness state and fabric management simulation
- An `ibping` network policy and daemon facilitate Multi-Access Device (MAD) traffic relay across pods, enabling multi-pod IMEX communication

This subsystem enables testing of GPU fabric management software, multi-node resource orchestration, and driver integration validating fabric readiness and topology convergence.

For architecture and operational details, see [ComputeDomain and IMEX Simulation](#9.5).

```mermaid
%% ComputeDomain and IMEX Simulation Components
graph LR
  DaemonSet_DS[DaemonSet: nvml-mock]
  DaemonSet_DS --> Fake_IMEX[fake-imex daemon]
  DaemonSet_DS --> FabricManager[fake-fabricmanager daemon]
  NetworkPolicy[ibping NetworkPolicy] --> IMEX_Communication[Cross-pod MAD traffic]
  Fake_IMEX --> IMEX_Communication
```

_Sources:_
- `deployments/nvml-mock/helm/nvml-mock/README.md:52-60` (imex ports in daemonset)
- Helm daemonset templates ownership and env vars

---

## 6. NRI Plugin for Node-Wide Injection

To facilitate transparent injection of the mock GPU simulation into all containers on a node, nvml-mock provides a **containerd NRI (Node Resource Interface) plugin** called `nvml-mock-nri`.

Key aspects:

- Runs as a sidecar-like process on each node, exposing health and readiness HTTP probes
- When enabled (`nri.enabled=true` in Helm), it appends the nvml-mock overlay mounts and environment variables (`LD_LIBRARY_PATH` pointing to mock `libnvidia-ml.so`) into newly created containers
- This allows plain pods without GPU resource requests or device mounts to run GPU-aware tools like `nvidia-smi` successfully against the mock driver
- Supports opt-out annotations and excluded namespaces for controlled injection
- Helps demonstrate or test node-wide GPU simulation scenarios without pod spec mutation

The plugin is opt-in due to its cluster-wide injection scope and requires containerd configured with NRI enabled. See [docs/demo/node-wide-injection](../../docs/demo/node-wide-injection) for usage examples.

For a deep dive into plugin architecture, configuration flags, and injection mechanisms, see [NRI Plugin for Node-Wide Injection](#9.6).

```mermaid
%% NRI Plugin Injection Overview
graph LR
  NRI_Plugin[nvml-mock-nri daemon]
  Kubelet --> NRI_Plugin
  NRI_Plugin -->|Inject overlay mount + env| Container_Startup
  Container_Startup -->|Runs| Pod_Container[Pod Container with mock GPU environment]
```

_Sources:_
- `deployments/nvml-mock/helm/nvml-mock/values.yaml:110-150` (nri block)
- Helm daemonset.yaml env vars for NRI config

---

## 7. Runtime Control with nvml-mock-ctl

To adjust GPU simulation behavior at runtime without redeploying the DaemonSet or rebooting pods, nvml-mock includes a CLI tool called `nvml-mock-ctl`.

Features:

- Enables modification of device states, error injection, and configuration overrides in a live cluster
- Uses a `config_override` YAML file written atomically to a well-known host path that the mock engine monitors (`/var/lib/nvml-mock/driver/config/overrides.yaml`)
- Overrides can selectively adjust specific GPUs or global behavior to simulate failure or state transitions
- Designed to integrate with E2E test scenarios (`scenario_runtime_control`) to validate error handling paths and crash recovery

This facility enhances testing realism and flexibility by manipulating the simulated GPU environment dynamically without full pod lifecycle operations.

For usage patterns, CLI options, and API details, see [Runtime Control with nvml-mock-ctl](#9.7).

```mermaid
%% Runtime Control Interaction Model
graph LR
  Admin[nvml-mock-ctl CLI]
  Admin -->|Writes overrides| Overrides_File[/var/lib/nvml-mock/driver/config/overrides.yaml]
  DaemonSet --> MockEngine[Mock NVML Engine]
  MockEngine -->|Reloads overrides| Overrides_File
```

_Sources:_
- Child page summary from TOC (implied)

---

# Summary

The **nvml-mock System** is a comprehensive and configurable GPU simulation framework designed to replace NVIDIA hardware with a software mock enabling full-stack testing of GPU-aware Kubernetes components. It centralizes:

- The mock NVML library and CGo bridge
- Flexible YAML-driven GPU profiles and dynamic behavior
- A Kubernetes DaemonSet deployment via Helm that sets up device nodes, libraries, PCI/IB topology, and node labels
- Advanced fabric simulation subsystems for multi-node GPU cluster realism
- Node-wide ambient injection via containerd NRI plugins
- Runtime control utilities for fault injection and scenario testing

Together, these components enable robust, scalable, and realistic GPU testing environments without physical GPUs. To gain in-depth technical understanding, please consult the respective child pages dedicated to each subsystem:

- [Mock NVML Library Internals](#9.1)
- [GPU Configuration and Profiles](#9.2)
- [Helm Chart Deployment](#9.3)
- [NVLink, InfiniBand, and PCIe Simulation](#9.4)
- [ComputeDomain and IMEX Simulation](#9.5)
- [NRI Plugin for Node-Wide Injection](#9.6)
- [Runtime Control with nvml-mock-ctl](#9.7)

---

# References

| Document | Description |
|---------|--------------|
| `deployments/nvml-mock/helm/nvml-mock/README.md` | Helm chart overview and quick start |
| `deployments/nvml-mock/helm/nvml-mock/values.yaml` | Helm default values including GPU profile config |
| `deployments/nvml-mock/helm/nvml-mock/templates/daemonset.yaml` | DaemonSet resource and env var templating |
| `deployments/nvml-mock/scripts/setup.sh` and `cleanup.sh` | Host environment setup and teardown scripts |
| `pkg/gpu/mocknvml/README.md` | Mock NVML library design, profiles, and usage |
| `docs/examples.md` | Usage examples for mock NVML |
| `docs/integrations/fake-gpu-operator.md` | Integration with Run:ai fake-gpu-operator |

---

*This page is part of the [k8s-test-infra](https://github.com/NVIDIA/k8s-test-infra) technical wiki.*

---

# Page: Mock NVML Library Internals

# 9.1 Mock NVML Library Internals

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cmd/generate-bridge/main.go](cmd/generate-bridge/main.go)
- [cmd/generate-bridge/main_test.go](cmd/generate-bridge/main_test.go)
- [cmd/generate-bridge/parser.go](cmd/generate-bridge/parser.go)
- [pkg/gpu/mockcuda/bridge/cuda.go](pkg/gpu/mockcuda/bridge/cuda.go)
- [pkg/gpu/mockcuda/bridge/cuda_types.h](pkg/gpu/mockcuda/bridge/cuda_types.h)
- [pkg/gpu/mockcuda/bridge/helpers.go](pkg/gpu/mockcuda/bridge/helpers.go)
- [pkg/gpu/mockcuda/engine/cuda.go](pkg/gpu/mockcuda/engine/cuda.go)
- [pkg/gpu/mockcuda/engine/cuda_test.go](pkg/gpu/mockcuda/engine/cuda_test.go)
- [pkg/gpu/mockcuda/engine/types.go](pkg/gpu/mockcuda/engine/types.go)
- [pkg/gpu/mocknvml/bridge/cgo_types.go](pkg/gpu/mocknvml/bridge/cgo_types.go)
- [pkg/gpu/mocknvml/bridge/device.go](pkg/gpu/mocknvml/bridge/device.go)
- [pkg/gpu/mocknvml/bridge/fieldvalues.go](pkg/gpu/mocknvml/bridge/fieldvalues.go)
- [pkg/gpu/mocknvml/bridge/helpers.go](pkg/gpu/mocknvml/bridge/helpers.go)
- [pkg/gpu/mocknvml/bridge/init.go](pkg/gpu/mocknvml/bridge/init.go)
- [pkg/gpu/mocknvml/bridge/internal.go](pkg/gpu/mocknvml/bridge/internal.go)
- [pkg/gpu/mocknvml/bridge/nvml_types.h](pkg/gpu/mocknvml/bridge/nvml_types.h)
- [pkg/gpu/mocknvml/bridge/stubs_generated.go](pkg/gpu/mocknvml/bridge/stubs_generated.go)
- [pkg/gpu/mocknvml/bridge/system.go](pkg/gpu/mocknvml/bridge/system.go)
- [pkg/gpu/mocknvml/engine/config_test.go](pkg/gpu/mocknvml/engine/config_test.go)
- [pkg/gpu/mocknvml/engine/device.go](pkg/gpu/mocknvml/engine/device.go)
- [pkg/gpu/mocknvml/engine/device_test.go](pkg/gpu/mocknvml/engine/device_test.go)
- [pkg/gpu/mocknvml/engine/engine.go](pkg/gpu/mocknvml/engine/engine.go)
- [pkg/gpu/mocknvml/engine/engine_test.go](pkg/gpu/mocknvml/engine/engine_test.go)
- [pkg/gpu/mocknvml/engine/field_values.go](pkg/gpu/mocknvml/engine/field_values.go)
- [pkg/gpu/mocknvml/engine/field_values_test.go](pkg/gpu/mocknvml/engine/field_values_test.go)
- [pkg/gpu/mocknvml/engine/handles.go](pkg/gpu/mocknvml/engine/handles.go)
- [pkg/gpu/mocknvml/engine/handles_test.go](pkg/gpu/mocknvml/engine/handles_test.go)
- [pkg/gpu/mocknvml/engine/version.go](pkg/gpu/mocknvml/engine/version.go)
- [pkg/gpu/mocknvml/engine/version_test.go](pkg/gpu/mocknvml/engine/version_test.go)
- [tests/e2e/device-plugin-mock.yaml](tests/e2e/device-plugin-mock.yaml)
- [tests/e2e/kind-dra-config.yaml](tests/e2e/kind-dra-config.yaml)

</details>



This page provides an in-depth technical overview of the internal implementation of the nvml-mock system within the k8s-test-infra project. It explains how the mock NVML C library is bridged into Go with CGo, describing the core singleton `Engine`, the `HandleTable` for opaque device handle management, the `ConfigurableDevice` that simulates GPU devices with YAML-based configuration, and the `generate-bridge` code generator that scaffolds NVML function bindings. This documentation also clarifies the overall C-to-Go interoperability architecture enabling a fully functional NVML mock that integrates seamlessly with NVIDIA tooling and Kubernetes testing.

---

## Purpose and Scope

The nvml-mock system simulates NVIDIA's NVML GPU management library. It replaces the real NVML shared library with a mock implementation capable of simulating multiple devices, device topology, and dynamic state. This allows testing GPU-aware Kubernetes infrastructure components such as Node Feature Discovery (NFD), Dynamic Resource Allocation (DRA), and container runtimes without requiring real GPUs.

Core internals covered in this section:

- The CGo bridge layer exposing the NVML C API to Go
- `Engine` as the singleton managing the lifecycle and device simulation
- `HandleTable` managing opaque NVML device handles
- `ConfigurableDevice` representing a YAML-configurable GPU device instance
- The `generate-bridge` tool automating NVML stub function generation

Detailed explanations span implementation design, data flow, and key functions, alongside structural diagrams mapping concepts to code artifacts.

---

## 1. CGo Bridge Layer

### Overview

The bridge is implemented in the `pkg/gpu/mocknvml/bridge` directory. It exposes NVML C API functions as C symbols that internally delegate to Go functions. 

- The main bridge files (e.g., `device.go`) contain hand-written CGo-exported functions for a subset of NVML APIs, such as `nvmlDeviceGetCount_v2`, `nvmlDeviceGetHandleByIndex_v2`, `nvmlDeviceGetFieldValues`, etc.
- Unimplemented NVML functions are stubbed out automatically in `stubs_generated.go` by the `generate-bridge` tool.
- Type compatibility with real NVML is ensured through internal `nvml_types.h` copied from the real NVML headers, preventing ABI incompatibility.
- Helper routines in `helpers.go` handle error string caching, return code conversion, and common patterns such as version checking and stubbing behavior.

### Key Bridge Functions

- `nvmlDeviceGetCount_v2`: Returns the number of simulated devices by delegating to the singleton Engine (bridge/device.go:117-127).
- `nvmlDeviceGetHandleByIndex_v2`: Resolves a device handle pointer by index (bridge/device.go:143-158).
- `nvmlDeviceGetFieldValues`: Marshals field queries from C into Go, asks the configured device for field values, and writes data back into C structs for `nvidia-smi` compatibility (bridge/fieldvalues.go:73-116).
- `nvmlErrorString`: Caches and returns static C strings for NVML errors matching real NVML semantics (bridge/helpers.go:164-167).
- Stub functions: Return `NVML_ERROR_NOT_SUPPORTED` for NVML calls not implemented yet, supporting graceful degradation (bridge/stubs_generated.go).

The bridge therefore acts as a C ABI compatible layer forwarding NVML calls into the Go-based simulation engine.

```mermaid
%% Title: CGo Bridge Layer Architecture
flowchart TD
  CClient["NVML C Client (e.g. nvidia-smi)"]
  CBridge["CGo Bridge Layer (pkg/gpu/mocknvml/bridge)"]
  GoEngine["Go Engine Singleton (engine.Engine)"]
  GoDevice["ConfigurableDevice Instances"]

  CClient -->|calls C symbols| CBridge
  CBridge -->|calls Go exported functions| GoEngine
  GoEngine -->|creates/manages| GoDevice
```

**Sources:**  
`pkg/gpu/mocknvml/bridge/device.go:96-194`,  
`pkg/gpu/mocknvml/bridge/fieldvalues.go:73-116`,  
`pkg/gpu/mocknvml/bridge/helpers.go:164-167`,  
`pkg/gpu/mocknvml/bridge/stubs_generated.go:1-150`  

---

## 2. Engine Singleton

### Purpose

The `Engine` struct in `pkg/gpu/mocknvml/engine/engine.go` is the central singleton orchestrating the lifecycle of the mock NVML library:

- Manages initialization (`Init()`) and shutdown (`Shutdown()`) state
- Creates and configures the mock server (`MockServer`), which wraps the dgxa100 base device simulation
- Holds a `HandleTable` which maps opaque C device handles to Go device instances
- Provides device lookup, enumeration, and configuration management APIs requested by the C bridge layer

### Creation and Lifecycle

- The singleton instance is lazy-initialized on first call to `GetEngine()` (engine.go:43-49).
- `Init()` initializes the engine once. It creates a mock server based on configuration loaded either from environment, YAML file, or defaults.
- Device simulation instances (`ConfigurableDevice`) are created for each simulated GPU and stored in the server wrapper.
- During shutdown, resources and cached state are released.
- The engine also tracks GPU visibility filtering to simulate container device visibility.

### Device Creation Paths

- **YAML-based Configuration**: When a YAML config is loaded, devices are created with full per-device and node topology setup (engine.go:128-168).
- **Legacy Configuration**: When no YAML is present, default or environment variable based device count and addresses are used (engine.go:174-203).

### Key Engine Functions

- `DeviceGetCount()`: Returns device count (engine.go:211-219).
- `DeviceGetHandleByIndex(i int)`: Returns opaque handle pointer by device index.
- `LookupDevice(handle unsafe.Pointer)`: Converts opaque handle to a Go device instance or returns an invalid sentinel.
- `GetConfig()`: Returns current configuration including driver version and device count.

```mermaid
%% Title: Engine Singleton Relationships
classDiagram
  class Engine {
    +config *Config
    +server *MockServer
    +handles *HandleTable
    +initCount int
    +Init() nvml.Return
    +Shutdown() nvml.Return
    +DeviceGetCount() (int, nvml.Return)
    +DeviceGetHandleByIndex(int) (unsafe.Pointer, nvml.Return)
    +LookupDevice(unsafe.Pointer) nvml.Interface
  }
  class MockServer {
    +Server dgxa100.Server
    +configurableDevices [ConfigurableDevice]
    +DeviceGetCountFunc func() (int, nvml.Return)
    ...
  }
  class HandleTable {
    +Allocate(v interface{}) unsafe.Pointer
    +Lookup(handle unsafe.Pointer) interface{}
    +Free(handle unsafe.Pointer)
  }
  class ConfigurableDevice {
    ...
  }

  Engine "1" --> "1" MockServer
  Engine "1" --> "1" HandleTable
  MockServer "1" --> "*" ConfigurableDevice
```

**Sources:**  
`pkg/gpu/mocknvml/engine/engine.go:27-224`  
`pkg/gpu/mocknvml/engine/engine_test.go`  

---

## 3. HandleTable: Opaque Device Handle Management

### Purpose

NVML uses opaque pointers (`nvmlDevice_t`) as device handles. The mock system must simulate these while tracking Go device instances.

### Implementation

- The `HandleTable` (in `engine/handles.go`) provides allocation, lookup, and freeing of opaque handles.
- Internally, it uses a thread-safe mapping from opaque pointer values to Go interface{} objects representing devices.
- The table assigns a unique pointer value to each allocated device object, ensuring handles are stable across calls.
- On shutdown, handles are cleared.

This mechanism isolates the simulated device instances from clients only seeing opaque C handles.

**HandleTable API:**

- `Allocate(value interface{}) unsafe.Pointer`: Returns a unique opaque handle for the wrapped device.
- `Lookup(handle unsafe.Pointer) interface{}`: Returns the Go object associated with the handle.
- `Free(handle unsafe.Pointer)`: Removes the mapping (usually on engine shutdown).

```mermaid
%% Title: HandleTable Data Flow
flowchart LR
  GoDevice["ConfigurableDevice instance"]
  HandleTable["HandleTable (map)"]
  OpaqueHandle["Opaque nvmlDevice_t.handle"]

  GoDevice -- Allocate() --> HandleTable
  HandleTable -- returns ptr --> OpaqueHandle
  OpaqueHandle -- passed to C NVML API --> ClientC
  ClientC -- passes back handle --> HandleTable
  HandleTable -- Lookup(handle) --> GoDevice
```

**Sources:**  
`pkg/gpu/mocknvml/engine/handles.go`  
`pkg/gpu/mocknvml/engine/engine.go:33`  
`pkg/gpu/mocknvml/engine/engine_test.go`  

---

## 4. ConfigurableDevice: YAML-Configurable GPU Simulation

### Overview

`ConfigurableDevice` wraps the base mock device (`dgxa100.Device`) and adds advanced features for per-device YAML-driven configuration and dynamic simulation. This type implements `nvml.Interface` for simulated device API calls.

### Fields

- The embedded `*dgxa100.Device` provides core DGX A100 mock behavior and base NVML data.
- `baseConfig *DeviceConfig` stores the immutable YAML configuration base for this device.
- `effective atomic.Pointer[DeviceConfig]` stores the current merged config including overrides, refreshed on demand.
- Cached fields include PCI info (`pciInfo`), BAR1 aperture memory (`bar1Memory`).
- Pointers to `dynamicMetricsSimulator` and `failureInjector` enable runtime simulation of dynamic metrics and failure injection.
- `refreshMu` mutex guards reconfiguration when new overrides are applied.

### Construction

- The constructor `NewConfigurableDevice` (engine/device.go:80-161) takes:
  - Device index and base device pointer
  - YAML device config merge base
  - UUID, PCI bus ID, minor number strings
  - The shared node-level `NodeFabric` topology structure
- It applies config overrides to the base device fields (name, architecture, brand, memory).
- Caches PCI info and BAR1 memory.
- Enables optional dynamic metrics simulation and failure injection.
- Initializes atomic effective config pointer.

### Config Override Refresh

- Config overrides are maintained as documented by a global `configOverrides` snapshot.
- `refresh()` recomputes and merges the effective config atomically only if the generation changes.
- It also updates failure injectors and dynamic metrics simulators as per config (engine/device.go:179-210).

### API Example Functions

- `cfg()`: Returns the current effective config for this device.
- `failureInjector()`: Returns the current failure injector after optional refresh.
- `GetPciInfo()`, `GetBAR1MemoryInfo()`: Return cached PCI and BAR1 information.
- `GetComputeRunningProcesses()`, `GetGraphicsRunningProcesses()`: Return simulated empty lists or configured process states.

```mermaid
%% Title: ConfigurableDevice Configuration Refresh Flow
flowchart TD
  Device[ConfigurableDevice]
  BaseCfg[baseConfig (YAML)]
  OverrideDoc[configOverrides snapshot]
  Merge[MergeDeviceConfig(baseConfig, override)]
  Effective[effective atomic.Pointer[DeviceConfig]]
  DynamicSim[dynamicMetricsSimulator]
  FailureInjector[failureInjector]

  Device --> BaseCfg
  OverrideDoc --> Merge
  BaseCfg --> Merge
  Merge --> Effective
  Effective --> Device
  Effective --> DynamicSim
  Effective --> FailureInjector
```

**Sources:**  
`pkg/gpu/mocknvml/engine/device.go:42-180`  
`pkg/gpu/mocknvml/engine/device_test.go`  

---

## 5. generate-bridge Code Generation Tool

### Purpose

Most NVML functions are generated automatically from the official Go NVML bindings and headers, saving handwritten boilerplate. The `cmd/generate-bridge` tool:

- Parses vendor-provided NVML Go source and C header files.
- Generates stub CGo-exported functions returning NOT_SUPPORTED errors.
- Allows selective handwritten overrides for critical functions in `bridge/device.go` and others.
- Removes stubs for implemented functions on regeneration.

### Effects in Codebase

- The generated file `bridge/stubs_generated.go` contains 282 stub functions returning `NVML_ERROR_NOT_SUPPORTED`.
- The build regenerates stubs automatically on source changes.
- Helps keep coverage consistent with the evolving NVML API while allowing incremental implementations.

```mermaid
%% Title: generate-bridge Flow
flowchart LR
  NVMLGoSource["vendor/github.com/NVIDIA/go-nvml/pkg/nvml/nvml.go"]
  NVMLHdr["nvml.h header file"]
  GenerateBridge["cmd/generate-bridge tool"]
  StubsFile["bridge/stubs_generated.go"]
  HandwrittenFiles["bridge/device.go etc."]

  NVMLGoSource --> GenerateBridge
  NVMLHdr --> GenerateBridge
  GenerateBridge --> StubsFile
  HandwrittenFiles --> GenerateBridge
  GenerateBridge -- excludes implemented --> StubsFile
```

**Sources:**  
`cmd/generate-bridge/main.go`  
`pkg/gpu/mocknvml/bridge/stubs_generated.go`  

---

## 6. C-to-Go Interoperability Architecture

### Data Flow

The mock NVML library pretends to be a NVIDIA shared object:

- It exports C symbols, built with `buildmode=c-shared`.
- Each exported C function forwards calls to Go functions in the Engine singleton.
- The Engine uses the HandleTable to map opaque C `nvmlDevice_t` handles to Go device instances.
- Calls to device methods (`ConfigurableDevice`) respond with simulated data from YAML or default values.
- Results are marshaled back into C ABI-compatible structs for callers like `nvidia-smi`.

### Memory and Safety

- The opaque `nvmlDevice_t` pointer is actually a pointer into Go-managed memory held by HandleTable.
- The bridge uses careful pointer conversions, avoiding unsafe integer round-trips.
- Field values returned via `nvmlDeviceGetFieldValues` require writing union fields via C helper functions to work around CGo union restrictions.
- Error strings returned by `nvmlErrorString` are cached C strings mimicking the behavior of the real NVML library.

```mermaid
%% Title: C-to-Go Interoperability Detailed Flow
flowchart TD
  CClient["C NVML client (e.g. nvidia-smi)"]
  CBridge["C Functions (pkg/gpu/mocknvml/bridge/*.go)"]
  EngineSS["Singleton Engine instance"]
  HandleTbl["HandleTable (opaque handle mapping)"]
  Devices["ConfigurableDevice instances"]

  CClient --> CBridge
  CBridge --> EngineSS
  EngineSS --> HandleTbl
  HandleTbl --> Devices
  Devices -->|Return simulated NVML data| EngineSS
  EngineSS --> CBridge
  CBridge --> CClient
```

---

## Summary

The nvml-mock internals implement a robust CGo bridge layer that fulfills the NVML C API while forwarding logic to a sophisticated singleton Engine written in Go. The Engine uses a HandleTable to isolate C-visible opaque handles from Go device instances modeled by `ConfigurableDevice`. These devices provide strong per-GPU configurability via YAML, supporting advanced simulation needs. The `generate-bridge` tool automates stub generation for unimplemented functions, enabling gradual coverage of the NVML API surface.

Together, these pieces enable a full NVML simulation environment that Kubernetes test drivers and GPU-aware tooling can interface with naturally and reliably.

---

# Additional Diagrams Bridging Natural Language to Code Entities

```mermaid
%% Title: Mock NVML System - Natural Language to Code Entities (Part 1)
graph LR
  NVML_Simulation["NVML GPU Simulation System"]
  CGo_Bridge["CGo Bridge Layer (pkg/gpu/mocknvml/bridge)"]
  Engine_Singleton["Engine Singleton (engine.Engine)"]
  HandleTable["HandleTable (engine.HandleTable)"]
  Device["ConfigurableDevice (engine.ConfigurableDevice)"]

  NVML_Simulation --> CGo_Bridge
  CGo_Bridge --> Engine_Singleton
  Engine_Singleton --> HandleTable
  Engine_Singleton --> Device
```

```mermaid
%% Title: Mock NVML System - Natural Language to Code Entities (Part 2)
graph TD
  UserApp["nvidia-smi (NVML client)"]
  NVML_C_API["Mock NVML C Functions"]
  GoEngine["engine.Engine Singleton"]
  DeviceMap["HandleTable (maps handles <-> devices)"]
  SimDevices["ConfigurableDevice instances"]

  UserApp --> NVML_C_API
  NVML_C_API --> GoEngine
  GoEngine --> DeviceMap
  DeviceMap --> SimDevices
  SimDevices --> GoEngine
  GoEngine --> NVML_C_API
```

---

# References

- `pkg/gpu/mocknvml/bridge/device.go:96-194`  
- `pkg/gpu/mocknvml/bridge/fieldvalues.go:73-116`  
- `pkg/gpu/mocknvml/bridge/helpers.go:164-167`  
- `pkg/gpu/mocknvml/bridge/stubs_generated.go:1-150`  
- `pkg/gpu/mocknvml/engine/engine.go:27-224`  
- `pkg/gpu/mocknvml/engine/engine_test.go`  
- `pkg/gpu/mocknvml/engine/device.go:42-180`  
- `pkg/gpu/mocknvml/engine/device_test.go`  
- `cmd/generate-bridge/main.go`  
- `pkg/gpu/mocknvml/engine/handles.go`

---

# Page: GPU Configuration and Profiles

# GPU Configuration and Profiles

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deployments/nvml-mock/helm/nvml-mock/profiles/a100.yaml](deployments/nvml-mock/helm/nvml-mock/profiles/a100.yaml)
- [deployments/nvml-mock/helm/nvml-mock/profiles/b200.yaml](deployments/nvml-mock/helm/nvml-mock/profiles/b200.yaml)
- [deployments/nvml-mock/helm/nvml-mock/profiles/gb200.yaml](deployments/nvml-mock/helm/nvml-mock/profiles/gb200.yaml)
- [deployments/nvml-mock/helm/nvml-mock/profiles/h100.yaml](deployments/nvml-mock/helm/nvml-mock/profiles/h100.yaml)
- [deployments/nvml-mock/helm/nvml-mock/profiles/l40s.yaml](deployments/nvml-mock/helm/nvml-mock/profiles/l40s.yaml)
- [deployments/nvml-mock/helm/nvml-mock/profiles/t4.yaml](deployments/nvml-mock/helm/nvml-mock/profiles/t4.yaml)
- [docs/configuration.md](docs/configuration.md)
- [docs/development.md](docs/development.md)
- [pkg/gpu/mocknvml/configs/mock-nvml-config-a100.yaml](pkg/gpu/mocknvml/configs/mock-nvml-config-a100.yaml)
- [pkg/gpu/mocknvml/configs/mock-nvml-config-b200.yaml](pkg/gpu/mocknvml/configs/mock-nvml-config-b200.yaml)
- [pkg/gpu/mocknvml/configs/mock-nvml-config-gb200.yaml](pkg/gpu/mocknvml/configs/mock-nvml-config-gb200.yaml)
- [pkg/gpu/mocknvml/configs/mock-nvml-config-h100.yaml](pkg/gpu/mocknvml/configs/mock-nvml-config-h100.yaml)
- [pkg/gpu/mocknvml/configs/mock-nvml-config-l40s.yaml](pkg/gpu/mocknvml/configs/mock-nvml-config-l40s.yaml)
- [pkg/gpu/mocknvml/configs/mock-nvml-config-t4.yaml](pkg/gpu/mocknvml/configs/mock-nvml-config-t4.yaml)
- [pkg/gpu/mocknvml/engine/config.go](pkg/gpu/mocknvml/engine/config.go)
- [pkg/gpu/mocknvml/engine/config_types.go](pkg/gpu/mocknvml/engine/config_types.go)
- [pkg/gpu/mocknvml/engine/dynamic_metrics.go](pkg/gpu/mocknvml/engine/dynamic_metrics.go)
- [pkg/gpu/mocknvml/engine/failure_injector.go](pkg/gpu/mocknvml/engine/failure_injector.go)
- [pkg/gpu/mocknvml/engine/failure_injector_test.go](pkg/gpu/mocknvml/engine/failure_injector_test.go)
- [pkg/gpu/mocknvml/engine/nvlink_error_injection_test.go](pkg/gpu/mocknvml/engine/nvlink_error_injection_test.go)
- [pkg/gpu/mocknvml/engine/nvlink_fields.go](pkg/gpu/mocknvml/engine/nvlink_fields.go)

</details>



This section documents the GPU configuration and profile management within the `k8s-test-infra` repository, focusing on the mock NVML (NVIDIA Management Library) engine used to simulate GPUs for Kubernetes testing. It covers the structure of the YAML configuration (`YAMLConfig`), the loading and resolution order of configurations via `LoadConfig()`, available GPU profiles, the handling of dynamic metrics, and GPU failure injection features.

---

## 1. YAMLConfig Structure

At the core of the GPU simulation configuration is the `YAMLConfig` struct defined in the package `engine`. It represents the complete schema of a GPU simulation configuration described in YAML format.

```go
type YAMLConfig struct {
	Version        string           `json:"version"`
	System         SystemConfig     `json:"system"`
	DeviceDefaults DeviceConfig     `json:"device_defaults"`
	Devices        []DeviceOverride `json:"devices"`
	NVLink         *NVLinkConfig    `json:"nvlink,omitempty"`

	// PCIeTopology promotes the root-complex / NUMA layout (previously
	// consumed only by cmd/render-pci-sysfs) into the engine so NVLink
	// topology, pairwise PCIe levels, and CPU/NUMA affinity all derive
	// from the same facts. Optional; absent on PCIe-only profiles.
	PCIeTopology *PCIeTopologyConfig `json:"pcie_topology,omitempty"`
}
```

- `Version`: Config format version, typically "1.0".
- `System`: System-wide NVML settings such as driver version and CUDA version.
- `DeviceDefaults`: Global device properties applied to all devices unless overridden.
- `Devices`: Per-device configurations to override defaults on a device-by-device basis.
- `NVLink`: NVLink fabric-related configuration.
- `PCIeTopology`: Optional topology information defining PCIe root complex and NUMA layout for realistic simulation.

The nested structs `SystemConfig` and `DeviceConfig` cover detailed aspects of GPU simulation.

`SystemConfig` includes:

- `DriverVersion`: Driver version string.
- `NVMLVersion`: NVML interface version.
- `CUDAVersion`, `CUDAVersionMajor`, and `CUDAVersionMinor`: CUDA runtime versions.
- `NumDevices`: The number of devices simulated (optional override).

`DeviceConfig` is a large struct modeling comprehensive GPU characteristics:

- Identification fields like `Name`, `Brand`, `Serial`, etc.
- Architecture details including `Architecture`, `ComputeCapability`, `NumGPUCores`.
- Memory and BAR1 memory configuration (`MemoryConfig`, `BAR1MemoryConfig`).
- PCI and PCIe configurations.
- Power, thermal, and fan settings.
- Clock configurations and supported clocks.
- Performance, utilization, and encoder/decoder statistics.
- ECC status and error counts.
- Display modes and MIG (Multi-Instance GPU) settings.
- Advanced features like GPU Operation Mode, Driver Model, Accounting, Virtualization.
- Blackwell-specific features and Grace Superchip configurations for newer GPUs.
- GPU topology and simulated running processes.
- Dynamic metrics for time-varying temperature, power, and utilization.
- GPU Performance Monitoring (GPM) configuration.
- Failure injection settings for simulating hardware faults.
- NVLink fabric and error injection information.

This rich configurability enables precise simulation of various GPU models and their operational characteristics.

Sources: `pkg/gpu/mocknvml/engine/config_types.go:16-162`(), `docs/configuration.md:33-304`()

---

## 2. LoadConfig Function and Configuration Resolution

The function `LoadConfig()` orchestrates the retrieval and loading of the GPU simulation configuration. Its design supports flexible resolution across explicit YAML files, implicit discovery, and environment variable fallbacks.

### Resolution Order

1. **Explicit YAML file via `MOCK_NVML_CONFIG`**:  
   The environment variable `MOCK_NVML_CONFIG` sets the path to a YAML config file. If set, that file is loaded and parsed.

2. **Auto-discovery on Linux**:  
   If no explicit config path is set, on Linux systems, the config file is **auto-discovered** by reading `/proc/self/maps` to identify the loaded path of the Mock NVML shared library `.so` file (`libnvidia-ml.so`). Assuming a typical driver installation layout, the code navigates relative parent paths to locate `config/config.yaml` near the driver root.

3. **Environment variables and defaults**:  
   If no YAML config can be loaded, the system falls back to environment variables and default values. Specifically:
   - `MOCK_NVML_NUM_DEVICES` overrides the number of simulated GPUs.
   - `MOCK_NVML_DRIVER_VERSION` overrides the driver version string.
   - Defaults to 8 devices and driver version `"550.163.01"` if nothing else is specified.

### Caching

`LoadConfig()` caches the loaded configuration keyed by the config path to avoid repeated loads in long-running processes. The cache is protected by a mutex.

### Core LoadConfig Logic (simplified):

```go
func LoadConfig() *Config {
	configPath := os.Getenv("MOCK_NVML_CONFIG")
	if configPath == "" {
		configPath = discoverConfigPath()
	}

	configCacheMu.Lock()
	defer configCacheMu.Unlock()

	if configCache != nil && configCachePath == configPath {
		return configCache
	}

	config := DefaultConfig()

	if configPath != "" {
		yamlConfig, err := LoadYAMLConfig(configPath)
		// On error, fallback to defaults; else apply YAML config
		if err == nil {
			config.YAMLConfig = yamlConfig
			config.DriverVersion = yamlConfig.System.DriverVersion
			config.NumDevices = len(yamlConfig.Devices)
			if config.NumDevices == 0 {
				config.NumDevices = 8
			}
			if yamlConfig.System.NumDevices > 0 {
				config.NumDevices = yamlConfig.System.NumDevices
			}

			// Apply topology overlay from cluster config for multi-node fabric...

			configCache = config
			configCachePath = configPath
			return config
		}
	}

	// Fallback to environment variables
	if num := os.Getenv("MOCK_NVML_NUM_DEVICES"); num != "" {
		if val, err := strconv.Atoi(num); err == nil && val >= 0 {
			config.NumDevices = val
		}
	}

	if ver := os.Getenv("MOCK_NVML_DRIVER_VERSION"); ver != "" {
		config.DriverVersion = ver
	}

	configCache = config
	configCachePath = configPath
	return config
}
```

### discoverConfigPath

On Linux, the `discoverConfigPath()` function reads `/proc/self/maps` to find the path of the loaded `.so` file and navigates to `config/config.yaml`. This relies on standard NVIDIA driver directory layout. If no file exists, it returns empty.

### Overrides

There is also support for runtime override files via `MOCK_NVML_OVERRIDES` or `overrides.yaml` adjacent to the main YAML config.

Sources: `pkg/gpu/mocknvml/engine/config.go:61-141`(), `pkg/gpu/mocknvml/engine/config.go:156-210`(), `docs/configuration.md:5-39`()

---

## 3. GPU Profiles

The repository provides several pre-made YAML configuration profiles representing distinct NVIDIA GPU models, supplied as examples for testing.

Each profile is a complete YAML file that fully specifies system and device parameters to enable realistic simulation matching real hardware behavior. They can be referenced using `MOCK_NVML_CONFIG` or Helm chart values for deployment.

The primary profiles are:

| Profile Name | Description                          | Location                          |
|--------------|----------------------------------|---------------------------------|
| **a100**    | NVIDIA A100 SXM4 40GB               | `pkg/gpu/mocknvml/configs/mock-nvml-config-a100.yaml` <br> `deployments/nvml-mock/helm/nvml-mock/profiles/a100.yaml` |
| **h100**    | NVIDIA H100 80GB HBM3 (Hopper)      | `pkg/gpu/mocknvml/configs/mock-nvml-config-h100.yaml` <br> `deployments/nvml-mock/helm/nvml-mock/profiles/h100.yaml` |
| **b200**    | NVIDIA B200 (single GPU Blackwell)  | `pkg/gpu/mocknvml/configs/mock-nvml-config-b200.yaml` <br> `deployments/nvml-mock/helm/nvml-mock/profiles/b200.yaml` |
| **gb200**   | NVIDIA GB200 Grace-Blackwell Superchip | `pkg/gpu/mocknvml/configs/mock-nvml-config-gb200.yaml` <br> `deployments/nvml-mock/helm/nvml-mock/profiles/gb200.yaml` |
| **gb300**   | NVIDIA GB300 Grace-Blackwell variant (not shown in sample) | `deployments/nvml-mock/helm/nvml-mock/profiles/gb300.yaml` |
| **l40s**    | NVIDIA L40S (not shown in sample)    | `pkg/gpu/mocknvml/configs/mock-nvml-config-l40s.yaml` <br> `deployments/nvml-mock/helm/nvml-mock/profiles/l40s.yaml` |
| **t4**      | NVIDIA T4                            | `pkg/gpu/mocknvml/configs/mock-nvml-config-t4.yaml` <br> `deployments/nvml-mock/helm/nvml-mock/profiles/t4.yaml` |

### Profile Contents

Profiles mirror real GPU configurations including:

- CUDA cores, architecture (`ampere`, `hopper`, `blackwell`).
- ECC modes and errors configuration.
- Power and thermal operational parameters.
- Memory sizes (HBM2/3, BAR1 memory).
- PCI and PCIe link configurations.
- Dynamic clock speeds and performance states.
- NVLink fabric and topology for multi-GPU systems.
- Firmware and virtualization settings.

For example, the GB200 profile provides a high-power Grace Superchip simulation with 192 GiB of HBM3e memory, PCIe Gen6 support, and detailed fabric health status.

Profiles are extensively documented in YAML with comments describing each section and typical realistic values.

Sources:  
Profile YAML files `pkg/gpu/mocknvml/configs/*.yaml` and related Helm profile files `deployments/nvml-mock/helm/nvml-mock/profiles/*.yaml`. See:  
- `pkg/gpu/mocknvml/configs/mock-nvml-config-gb200.yaml` (lines 1-11383)  
- `deployments/nvml-mock/helm/nvml-mock/profiles/gb200.yaml` (lines 1-11383)  
- `pkg/gpu/mocknvml/configs/mock-nvml-config-h100.yaml` (lines 1-8523)  
- `deployments/nvml-mock/helm/nvml-mock/profiles/h100.yaml` (lines 1-9287)  
- `pkg/gpu/mocknvml/configs/mock-nvml-config-b200.yaml` (lines 1-7469)  
- `deployments/nvml-mock/helm/nvml-mock/profiles/b200.yaml` (lines 1-8410)  
- `docs/configuration.md`  

---

## 4. Dynamic Metrics

`DynamicMetrics` enables time-varying simulation for GPU telemetry parameters such as temperature, power draw, and utilization percentages, allowing the mock to simulate fluctuating values rather than static snapshots.

Defined inside the `DeviceConfig`:

```go
DynamicMetrics *DynamicMetricsConfig `json:"dynamic_metrics,omitempty"`
```

When `nil` (default), static values directly from the other config fields are returned on queries.

The dynamic configuration supports base values and variance ranges which the engine uses (likely with timers or sampling) to generate simulated time-varying metrics for:

- GPU temperature
- Power consumption
- Utilization statistics

This enriches testing by enabling more realistic monitoring and telemetry behaviors.

Note that in profiles like the GB200 Helm profile there is also a `dynamic_metrics_defaults` key at the top-level YAML, which is used by the Helm chart for default dynamic metrics but ignored internally by the engine.

Sources:  
- `pkg/gpu/mocknvml/engine/config_types.go:138-141`()  
- `deployments/nvml-mock/helm/nvml-mock/profiles/gb200.yaml:17-23`  
- `docs/configuration.md:17-24` (dynamic metrics mention)  

---

## 5. GPU Failure Injection Configuration

Mock NVML supports injective simulation of GPU failures such as device lost, fallen-off-bus errors, uncorrectable ECC errors, and Xid errors. This enhances test coverage for error handling in consumers like GPU Operators or node-level tooling.

The failures are controlled by the `FailureInjectionConfig` struct embedded in `DeviceConfig` under the `Failure` field.

```go
Failure *FailureInjectionConfig `json:"failure,omitempty"`
```

### Key Behavior

- When `Failure` is `nil` or absent, the device behaves as healthy hardware.
- When populated, various failure conditions can be triggered in the simulated GPU state.
- Failure injection interacts with NVLink error injection to simulate link errors at the device fabric-level.

### NVLink Error Injection

- `NVLinkErrorInjectionConfig` allows per-link NVLink data-link error accrual simulation.
- Simulates rising error counters seen by monitoring tools, triggering health events in DCGM and NVSentinel.
- Supports filters to inject errors into specific NVLink links.
- Can simulate healthy links, zero error rates to "heal" devices, or injecting error rates in errors/second.
- Ensures inactive links (meaning not present physically) do not receive errors.

### Validation Tests

- Unit tests verify monotonic error counter accrual over time for injected error rates.
- Tests verify no errors are reported if no injection configured.
- Tests confirm that filtered injections affect only targeted links.
- Tests confirm error counter fields exposed as NVML field values.

Sources:  
- `pkg/gpu/mocknvml/engine/config_types.go:148-161` (Failure and NVLinkErrorInjectionConfig fields)  
- `pkg/gpu/mocknvml/engine/nvlink_error_injection_test.go:13-154` (failure injection tests)  
- `docs/configuration.md` (failure injection usage referenced in the DeviceConfig section)  

---

## 6. System Overview Diagram

Below is a mermaid diagram bridging natural language concepts of GPU simulation configuration to the main code entities:

```mermaid
graph TD
  A["Natural Language: GPU Config & Profiles"] --> B["YAMLConfig struct"]
  B --> C["SystemConfig"]
  B --> D["DeviceConfig (defaults & per-device)"]
  D --> E["FailureInjectionConfig"]
  D --> F["DynamicMetricsConfig"]
  B --> G["NVLinkConfig"]
  A --> H["LoadConfig()"]
  H --> I["Resolve MOCK_NVML_CONFIG env var"]
  H --> J["discoverConfigPath() via /proc/self/maps on Linux"]
  H --> K["Fallback to env vars & defaults"]
  H --> L["Cache loaded Config"]
  C -.-> M["YAML System settings: driver_version, num_devices"]
  D -.-> N["Full device spec: clocks, power, etc."]
  E -.-> O["Simulate GPU hardware failures"]
  F -.-> P["Time-varying metrics simulation"]
  G -.-> Q["NVLink fabric and error injection"]
  
  style A fill:#f9f,stroke:#333,stroke-width:1px
  style B fill:#bbf,stroke:#333,stroke-width:1px
  style H fill:#bbf,stroke:#333,stroke-width:1px
```

Sources:  
- `pkg/gpu/mocknvml/engine/config.go:61-141`  
- `pkg/gpu/mocknvml/engine/config_types.go:16-162`  

---

## 7. GPU Profiles and Their Code Location Diagram

This diagram links the profile names from natural language with their YAML file code locations in the codebase, emphasizing the uniform structure and usage.

```mermaid
graph LR
  A["GPU Profiles (Natural Language)"] --> B["A100"]
  A --> C["H100"]
  A --> D["B200"]
  A --> E["GB200"]
  A --> F["GB300"]
  A --> G["L40S"]
  A --> H["T4"]

  B --> I["pkg/gpu/mocknvml/configs/mock-nvml-config-a100.yaml"]
  B --> J["deployments/nvml-mock/helm/nvml-mock/profiles/a100.yaml"]

  C --> K["pkg/gpu/mocknvml/configs/mock-nvml-config-h100.yaml"]
  C --> L["deployments/nvml-mock/helm/nvml-mock/profiles/h100.yaml"]

  D --> M["pkg/gpu/mocknvml/configs/mock-nvml-config-b200.yaml"]
  D --> N["deployments/nvml-mock/helm/nvml-mock/profiles/b200.yaml"]

  E --> O["pkg/gpu/mocknvml/configs/mock-nvml-config-gb200.yaml"]
  E --> P["deployments/nvml-mock/helm/nvml-mock/profiles/gb200.yaml"]

  F --> Q["deployments/nvml-mock/helm/nvml-mock/profiles/gb300.yaml"]
  G --> R["pkg/gpu/mocknvml/configs/mock-nvml-config-l40s.yaml"]
  G --> S["deployments/nvml-mock/helm/nvml-mock/profiles/l40s.yaml"]

  H --> T["pkg/gpu/mocknvml/configs/mock-nvml-config-t4.yaml"]
  H --> U["deployments/nvml-mock/helm/nvml-mock/profiles/t4.yaml"]
```

Sources:  
- `pkg/gpu/mocknvml/configs/mock-nvml-config-*.yaml` files  
- `deployments/nvml-mock/helm/nvml-mock/profiles/*.yaml`  

---

## Summary

- **YAMLConfig** is the extensible top-level structure defining simulation details for the mock NVML engine.
- **LoadConfig()** resolves config using explicit env var, auto-discovery, or default environment variables, caching results for efficiency.
- **GPU Profiles** are pre-built comprehensive YAML files simulating specific NVIDIA GPU models for testing.
- **DynamicMetrics** enables simulation of time-varying telemetry parameters.
- **Failure Injection** provides simulation for GPU hardware errors and NVLink link faults, useful for robust testing of error handling.

This configuration system enables accurate and flexible GPU simulations supporting the Kubernetes test infrastructure, especially within the nvml-mock project.

---

### References

| Topic                  | Location                                    |
|------------------------|---------------------------------------------|
| YAMLConfig struct      | `pkg/gpu/mocknvml/engine/config_types.go:16-162` |
| LoadConfig logic       | `pkg/gpu/mocknvml/engine/config.go:61-141`  |
| Config auto-discovery  | `pkg/gpu/mocknvml/engine/config.go:156-210` |
| GPU Profiles (example) | multiple YAML files under `pkg/gpu/mocknvml/configs/` and Helm profiles `deployments/nvml-mock/helm/nvml-mock/profiles/` |
| Dynamic Metrics        | `pkg/gpu/mocknvml/engine/config_types.go:138-141`   |
| Failure Injection      | `pkg/gpu/mocknvml/engine/config_types.go:148-161` and `pkg/gpu/mocknvml/engine/nvlink_error_injection_test.go` |
| Configuration Reference | `docs/configuration.md`                      |
| Development Guide       | `docs/development.md`                        |

---

End of Section 9.2: GPU Configuration and Profiles

---

# Page: Helm Chart Deployment

# Helm Chart Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [deployments/nvml-mock/helm/nvml-mock/Chart.yaml](deployments/nvml-mock/helm/nvml-mock/Chart.yaml)
- [deployments/nvml-mock/helm/nvml-mock/README.md](deployments/nvml-mock/helm/nvml-mock/README.md)
- [deployments/nvml-mock/helm/nvml-mock/templates/NOTES.txt](deployments/nvml-mock/helm/nvml-mock/templates/NOTES.txt)
- [deployments/nvml-mock/helm/nvml-mock/templates/_helpers.tpl](deployments/nvml-mock/helm/nvml-mock/templates/_helpers.tpl)
- [deployments/nvml-mock/helm/nvml-mock/templates/daemonset.yaml](deployments/nvml-mock/helm/nvml-mock/templates/daemonset.yaml)
- [deployments/nvml-mock/helm/nvml-mock/templates/integrations-fgo.yaml](deployments/nvml-mock/helm/nvml-mock/templates/integrations-fgo.yaml)
- [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/configmap_test.yaml.snap](deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/configmap_test.yaml.snap)
- [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap](deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap)
- [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/notes_test.yaml.snap](deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/notes_test.yaml.snap)
- [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/rbac_test.yaml.snap](deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/rbac_test.yaml.snap)
- [deployments/nvml-mock/helm/nvml-mock/tests/configmap_test.yaml](deployments/nvml-mock/helm/nvml-mock/tests/configmap_test.yaml)
- [deployments/nvml-mock/helm/nvml-mock/tests/daemonset_test.yaml](deployments/nvml-mock/helm/nvml-mock/tests/daemonset_test.yaml)
- [deployments/nvml-mock/helm/nvml-mock/tests/notes_test.yaml](deployments/nvml-mock/helm/nvml-mock/tests/notes_test.yaml)
- [deployments/nvml-mock/helm/nvml-mock/tests/rbac_test.yaml](deployments/nvml-mock/helm/nvml-mock/tests/rbac_test.yaml)
- [deployments/nvml-mock/helm/nvml-mock/values.schema.json](deployments/nvml-mock/helm/nvml-mock/values.schema.json)
- [deployments/nvml-mock/helm/nvml-mock/values.yaml](deployments/nvml-mock/helm/nvml-mock/values.yaml)
- [deployments/nvml-mock/scripts/cleanup.sh](deployments/nvml-mock/scripts/cleanup.sh)
- [deployments/nvml-mock/scripts/setup.sh](deployments/nvml-mock/scripts/setup.sh)

</details>



This page documents the Helm chart deployment architecture for the `nvml-mock` GPU simulation system within the `k8s-test-infra` repository. It covers the Helm chart structure, schema of the configurable values, ConfigMap generation for GPU profiles, RBAC setup, the DaemonSet pod configuration, and the supporting host environment setup/cleanup shell scripts executed in the DaemonSet container lifecycle.  

## 1. Overview

The `nvml-mock` Helm chart automates deploying the mock NVML-based GPU simulation stack on Kubernetes clusters. It enables turning any cluster into a multi-GPU environment without physical NVIDIA hardware by deploying a privileged DaemonSet on all nodes. Each pod in the DaemonSet provisions a mock GPU device environment, including device nodes, shared libraries simulating the NVIDIA driver (NVML/CUDA), GPU configuration YAMLs, mock PCI/InfiniBand sysfs trees, node labels for GPU presence, and support for the NVIDIA Container Device Interface (CDI).

By default, the Helm chart deploys one DaemonSet and associated ConfigMap, driving the behavior and device count via GPU profile YAMLs and user overrides. The chart also supports optional ambient NRI (NVIDIA Runtime Interface) plugin deployment for node-wide LD_PRELOAD injection and other experimental features like fabric manager and InfiniBand simulation.

## 2. Helm Chart Structure

The chart files live under:

```
deployments/nvml-mock/helm/nvml-mock/
```

Key files include:

- `Chart.yaml`: Chart metadata.
- `values.yaml`: Default configurable values with extensive GPU profile settings.
- `values.schema.json`: JSON schema validating values during helm operations.
- `templates/`: Kubernetes manifest templates rendered with the given values.
  - `daemonset.yaml`: Defines the privileged DaemonSet pod running the mock environment.
  - `configmap.yaml`: Generates the ConfigMap embedding the GPU profile YAML configuration.
  - `rbac.yaml`: ServiceAccount and RBAC resources for DaemonSet permissions.
  - Supporting templates and helper functions in `_helpers.tpl`.
- `scripts/setup.sh` and `scripts/cleanup.sh`: Shell scripts executed inside the DaemonSet container to install/uninstall the mock GPU environment on the host filesystem.

The chart is published as an OCI helm chart and designed for high configurability while maintaining safe defaults for GPU count, driver version, and node labeling.

Sources: `deployments/nvml-mock/helm/nvml-mock/README.md:1-76`, `Chart.yaml`, `values.yaml`, `values.schema.json`

---

## 3. Values Schema and GPU Profiles

### 3.1 GPU Configuration Values

The main `values.yaml` defines the `gpu` block as the core of the chart configuration, controlling:

- `profile`: GPU profile name (e.g., `a100`, `h100`, `b200`, `gb200`, `gb300`, `l40s`, `t4`). Each corresponds to a YAML file in `profiles/` embedded in the chart.
- `count`: The number of mock GPUs to expose per node. Can be empty (`""`) to auto-derive from the selected profile's device list or set to an integer to override.
- `customConfig`: Multi-line string override to provide a full custom GPU config YAML instead of loading a built-in profile.
- `dynamicMetrics`: Enables optional simulated dynamic metrics such as time-varying temperatures, power draw, and utilization patterns.
- `failureInjection`: Enables injection of GPU failure scenarios like lost devices or ECC errors for testing behavior.

The JSON schema (`values.schema.json`) strictly validates these fields at install/upgrade time to catch typos and enforce value ranges (e.g., probability between 0 and 1, pattern enums in dynamicMetrics, etc.).

### 3.2 ConfigMap Generation

The ConfigMap is generated in the template `configmap.yaml` by rendering the GPU profile YAML, optionally patched with overlays for dynamic metrics or failure injection. This is done via Helm template functions in `_helpers.tpl`:

- The `nvml-mock.gpuConfig` template loads the base GPU config either from:
  - the `customConfig` inline YAML override, or
  - an embedded profile YAML file identified by the `profile` field.
  
- If dynamic metrics or failure injection are enabled, it merges corresponding configuration blocks into the base device defaults of the YAML at render time.

This merged YAML is embedded as the `config.yaml` data key in the `ConfigMap` mounted inside the DaemonSet pod at `/etc/nvml-mock/config.yaml`.

This ConfigMap is annotated with a SHA256 hash checksum and referenced in the DaemonSet pod template annotation, which triggers rolling updates on config changes.

| Key             | Description                                            | Default                  |
|-----------------|--------------------------------------------------------|--------------------------|
| `profile`       | GPU profile basename to load YAML from `profiles/`    | `a100`                   |
| `count`         | GPU count override; empty derives from profile devices | `""` (auto)              |
| `customConfig`  | Inline YAML to fully override GPU config               | empty                    |
| `dynamicMetrics.enabled` | Enables time-varying simulated temperature/power | false                    |
| `failureInjection.enabled` | Enables GPU failure simulation                   | false                    |

**Note:** If an unknown profile name is specified, template rendering fails with a detailed error listing available profiles.

Sources:  
- `templates/configmap.yaml`  
- `templates/_helpers.tpl:87-140`  
- `values.yaml:4-58`  
- `values.schema.json:8-134`  
- `tests/configmap_test.yaml` and snapshots

---

## 4. RBAC and ServiceAccount

The chart defines a service account and related RBAC roles for the DaemonSet pods to label nodes and manipulate the NFD feature files.

The service account is created with the name identical to the Helm release full name (from the `_helpers.tpl` `fullname` template).

RBAC rules grant:

- Permissions to label nodes with `nvidia.com/gpu.present=true` to indicate GPU presence.
- Permission to manage files under the host's NFD feature files directory.

The DaemonSet spec references this service account to run its pods with sufficient privileges to perform these operations.

Sources:  
- `templates/rbac.yaml`  
- `templates/daemonset.yaml` (serviceAccountName reference)  
- `tests/rbac_test.yaml`

---

## 5. DaemonSet Pod Configuration

### 5.1 Basic Structure

The DaemonSet, defined in `templates/daemonset.yaml`, deploys one pod per node, running the `nvml-mock` container with the mock GPU environment.

Main points:

- Uses `privileged: true` security context needed for device creation (`mknod`) in the pod.
- Sets a `terminationGracePeriodSeconds` to allow cleanup hook execution.
- Selects nodes via `nodeSelector` and `tolerations` configurable via values.
- Carries standard Helm and custom labels for easy identification.

### 5.2 Container Environment

The container command is fixed to `["/scripts/entrypoint.sh"]` (bundled inside the container image).

Pod environment variables include:

- `GPU_COUNT`: Number of GPUs to simulate, either user-set or auto-derived.
- `DRIVER_VERSION`: NVML mock driver version, auto-derived from GPU profile or value override.
- `NODE_NAME`: Pod's node name from downward API.
- `MOCK_NFD_PCI_LABEL`: Enables or disables the NFD PCI feature file creation (string "on"/"off").
- `MOCK_NVML_CONFIG`: Path to the in-pod ConfigMap-mounted config YAML (`/etc/nvml-mock/config.yaml`).
- `MOCK_NVML_OVERRIDES`: Hosts a writable config override file path (e.g., `/host/var/lib/nvml-mock/driver/config/overrides.yaml`).
- Various environment variables related to fabric manager, InfiniBand tier, mock PCI root, and IB ping configuration.
- `LD_PRELOAD`: Set to preload shared libs for InfiniBand and PCI mocking.

Multiple volumes mount host paths such as:

- `/var/lib/nvml-mock` (host persistent directory for mock driver and config files).
- NFD features directory for dropping feature files.
- CDI socket directory.
- NVIDIA runtime directories for device nodes.

Annotated checksums track changes to the ConfigMap to trigger pod restart on config update.

### 5.3 Lifecycle Hooks

The container defines a `preStop` hook which executes the `/scripts/cleanup.sh` script inside the container to clean the host's mock GPU environment before pod termination.

### 5.4 Update Strategy

The DaemonSet uses a `RollingUpdate` with configured max unavailability (e.g., 25%) during upgrades.

---

### Diagram: DaemonSet Pod Environment and Mounts

```mermaid
graph TB
  subgraph Pod[nvml-mock DaemonSet Pod]
    container[nvml-mock Container]
    c_entrypoint["/scripts/entrypoint.sh"]
    env_GPU_COUNT[GPU_COUNT]
    env_DRIVER_VERSION[DRIVER_VERSION]
    env_NODE_NAME[NODE_NAME]
    env_MOCK_NFD_PCI_LABEL[MOCK_NFD_PCI_LABEL]
    env_MOCK_NVML_CONFIG[MOCK_NVML_CONFIG=/etc/nvml-mock/config.yaml]
    env_MOCK_NVML_OVERRIDES[MOCK_NVML_OVERRIDES]

    volume_host_nvml["hostPath: /var/lib/nvml-mock"]
    volume_nfd_features["hostPath: /etc/kubernetes/node-feature-discovery/features.d"]
    volume_cdi["hostPath: /var/run/cdi"]
    volume_run_nvidia["hostPath: /run/nvidia"]

    container --> c_entrypoint
    container --> env_GPU_COUNT
    container --> env_DRIVER_VERSION
    container --> env_NODE_NAME
    container --> env_MOCK_NFD_PCI_LABEL
    container --> env_MOCK_NVML_CONFIG
    container --> env_MOCK_NVML_OVERRIDES

    container --> volume_host_nvml
    container --> volume_nfd_features
    container --> volume_cdi
    container --> volume_run_nvidia
  end
```

Sources:  
- `templates/daemonset.yaml`  
- `values.yaml` (environment variables)  
- `tests/daemonset_test.yaml`

---

## 6. Host Environment Setup and Cleanup Scripts

Two key shell scripts installed inside the DaemonSet container at `/scripts/` manage the lifecycle of the mock GPU environment on the node filesystem:

### 6.1 `setup.sh`

- Entry point script run during pod start.
- Operates under environment variables: `GPU_COUNT`, `DRIVER_VERSION`, `NODE_NAME`, `MOCK_FABRICMANAGER`, `MOCK_FABRICMANAGER_STATE_DIR`, `MOCK_NFD_PCI_LABEL`.
- Steps performed:
  - Caps `GPU_COUNT` to the number of devices defined in the GPU profile YAML.
  - Creates directories under `/host/var/lib/nvml-mock` for driver libraries, device nodes, config files.
  - Copies the built mock NVML (`libnvidia-ml.so.*`) and CUDA (`libcuda.so.*`) shared libraries from container filesystem (`/usr/local/lib/`) to the mock driver root on the host.
  - Creates character device nodes `/dev/nvidia0`, `/dev/nvidiactl`, `/dev/nvidia-uvm`, etc. under the driver device directory with standard major device numbers.
  - Generates a CDI spec YAML (`/host/var/run/cdi/nvidia.yaml`) which declares device nodes and mounts. The CDI spec enables injecting the mock GPU libraries and device nodes into workloads via containerd CDI.
  - Writes the NFD PCI vendor feature file under the mounted NFD feature directory if `MOCK_NFD_PCI_LABEL` equals `"on"`.
  - Creates GPU Operator compatibility symlink `/run/nvidia/driver` on the host.

### 6.2 `cleanup.sh`

- Run as a preStop lifecycle hook before pod termination.
- Actions:
  - Removes all files under `/host/var/lib/nvml-mock`, cleaning the driver root and device nodes.
  - Deletes the GPU Operator symlink `/host/run/nvidia/driver`.
  - Removes the CDI spec YAML file.
  - Deletes the NFD feature file under the features directory if it was created.
  - Revokes the GPU presence node label (`nvidia.com/gpu.present-`) using `kubectl label node` if `kubectl` is available in the container.
  - Leaves certain validation toolkit markers untouched to avoid interfering with other components.

These scripts ensure the mock GPU environment is fully installed on pod start and cleanly removed on pod stop, avoiding stale states across daemonset rollouts.

---

### Diagram: Host Setup/Cleanup Flow

```mermaid
sequenceDiagram
  participant DS as DaemonSet Pod
  participant HostFS as Host Filesystem
  participant KubeAPI as Kubernetes API Server

  Note over DS: Pod start: `/scripts/setup.sh`

  DS->>HostFS: Create directories (/var/lib/nvml-mock, driver, config)
  DS->>HostFS: Copy mock libs (libnvidia-ml.so.*, libcuda.so.*)
  DS->>HostFS: mknod /dev/nvidia[0..N]
  DS->>HostFS: Write CDI spec (/var/run/cdi/nvidia.yaml)
  DS->>HostFS: Write NFD PCI feature file (if enabled)
  DS->>HostFS: Create symlink /run/nvidia/driver
  DS->>KubeAPI: Label node nvidia.com/gpu.present=true

  Note over DS: Pod stop: `/scripts/cleanup.sh`

  DS->>HostFS: Delete files under /var/lib/nvml-mock
  DS->>HostFS: Remove symlink /run/nvidia/driver
  DS->>HostFS: Remove CDI spec file
  DS->>HostFS: Remove NFD feature file (if created)
  DS->>KubeAPI: Remove node label nvidia.com/gpu.present
```

Sources:  
- `scripts/setup.sh:1-200+`  
- `scripts/cleanup.sh:1-43`

---

## 7. Data Flow and Key Template Functions

### 7.1 Data Flow Overview

- User configures GPU profile, count, and options via `values.yaml` or Helm CLI flags.
- During `helm install`/`upgrade`:
  - Helm templates the ConfigMap embedding the corresponding GPU profile YAML, applying overlays for dynamic metrics and failure injection if enabled.
  - Helm templates the DaemonSet with environment variables and volumes referencing the ConfigMap and host paths.
  - Helm templates RBAC and ServiceAccount resources.
- DaemonSet pods start on each node:
  - Run `setup.sh` to install mock GPU environment.
  - Run mock NVML/CUDA libraries and expose mock devices.
  - Label nodes and write NFD features for GPU presence.
- On pod deletion, `cleanup.sh` removes mock GPU artifacts and cleans node labels.

### 7.2 Helper Template Highlights

- `nvml-mock.gpuConfig`: Computes the final ConfigMap `config.yaml` content by resolving profile or custom YAML and overlaying dynamic/failure blocks.
- `nvml-mock.driverVersion`: Derives NVML driver version string, defaulting to profile metadata or user override.
- `nvml-mock.infinibandEnabled`: Detects if InfiniBand simulation is enabled based on profile config.
- Label-related templates generate standard Helm labels and selector labels for DaemonSet and NRI pods.
- `gpuCount`: Returns the number of GPUs, using count override or profile device counts.

---

### Diagram: Natural Language to Code Mapping

```mermaid
graph LR
  subgraph User Input
    ValuesYAML["values.yaml"]
    CLIFlags["Helm CLI --set ..."]
  end

  subgraph Helm_Templates
    ConfigMapYAML["templates/configmap.yaml"]
    DaemonSetYAML["templates/daemonset.yaml"]
    RBACYAML["templates/rbac.yaml"]
    Helpers["templates/_helpers.tpl"]
  end

  subgraph Container_Scripts
    SetupSH["scripts/setup.sh"]
    CleanupSH["scripts/cleanup.sh"]
  end

  ValuesYAML --> Helm_Templates
  CLIFlags --> Helm_Templates
  Helpers --> ConfigMapYAML
  Helpers --> DaemonSetYAML

  ConfigMapYAML -->|Mounted as volume /etc/nvml-mock/config.yaml| DaemonSetYAML
  DaemonSetYAML -->|ENV vars (GPU_COUNT, DRIVER_VERSION, MOCK_NFD_PCI_LABEL)| Container_Scripts

  SetupSH -->|Creates mock GPU env on host| HostFS["Host Filesystem"]
  CleanupSH -->|Removes mock GPU env and labels| HostFS

  DaemonSetYAML -->|Executes setup.sh & cleanup.sh on lifecycle hooks| Container_Scripts
```

Sources:  
- `templates/_helpers.tpl`  
- `templates/configmap.yaml`  
- `templates/daemonset.yaml`  
- `scripts/setup.sh`  
- `scripts/cleanup.sh`

---

## Summary

The `nvml-mock` Helm chart is a comprehensive deployment package for the mock GPU simulation layer in Kubernetes. It integrates templated GPU profiles, dynamic and failure injection overlays, and full management of the host environment via setup and cleanup scripts within a privileged DaemonSet pod. RBAC and node labeling enable Kubernetes ecosystem components to recognize mock GPUs, while CDI facilitates injection of the mock libraries into workloads. The design supports advanced features like InfiniBand simulation and fabric manager readiness gating, making it suitable for integration and testing in multi-GPU Kubernetes environments without physical hardware dependency.

---

# References and Sources

- `deployments/nvml-mock/helm/nvml-mock/README.md:1-76`  
- `deployments/nvml-mock/helm/nvml-mock/values.yaml:1-141`  
- `deployments/nvml-mock/helm/nvml-mock/values.schema.json:1-150`  
- `deployments/nvml-mock/helm/nvml-mock/templates/daemonset.yaml:1-148`  
- `deployments/nvml-mock/helm/nvml-mock/templates/_helpers.tpl:1-180`  
- `deployments/nvml-mock/helm/nvml-mock/templates/configmap.yaml` (implied from tests)  
- `deployments/nvml-mock/helm/nvml-mock/templates/rbac.yaml` (implied from tests)  
- `deployments/nvml-mock/scripts/setup.sh:1-200+`  
- `deployments/nvml-mock/scripts/cleanup.sh:1-43`  
- `deployments/nvml-mock/helm/nvml-mock/tests/configmap_test.yaml`  
- `deployments/nvml-mock/helm/nvml-mock/tests/daemonset_test.yaml`

---

# Page: NVLink, InfiniBand, and PCIe Simulation

# NVLink, InfiniBand, and PCIe Simulation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [cmd/fake-imex/ctl/peers.go](cmd/fake-imex/ctl/peers.go)
- [cmd/fake-imex/ctl/peers_test.go](cmd/fake-imex/ctl/peers_test.go)
- [cmd/render-pci-sysfs/main.go](cmd/render-pci-sysfs/main.go)
- [pkg/gpu/mocknvml/bridge/fabric.go](pkg/gpu/mocknvml/bridge/fabric.go)
- [pkg/gpu/mocknvml/bridge/fabric_dispatch.go](pkg/gpu/mocknvml/bridge/fabric_dispatch.go)
- [pkg/gpu/mocknvml/bridge/fabric_dispatch_test.go](pkg/gpu/mocknvml/bridge/fabric_dispatch_test.go)
- [pkg/gpu/mocknvml/bridge/fabric_layout_test.go](pkg/gpu/mocknvml/bridge/fabric_layout_test.go)
- [pkg/gpu/mocknvml/bridge/nvlink.go](pkg/gpu/mocknvml/bridge/nvlink.go)
- [pkg/gpu/mocknvml/engine/fabric_test.go](pkg/gpu/mocknvml/engine/fabric_test.go)
- [pkg/imexcoord/coord_test.go](pkg/imexcoord/coord_test.go)
- [pkg/network/mockib/README.md](pkg/network/mockib/README.md)
- [pkg/network/mockib/daemon/discover.go](pkg/network/mockib/daemon/discover.go)
- [pkg/network/mockib/daemon/discover_test.go](pkg/network/mockib/daemon/discover_test.go)
- [pkg/network/mockib/daemon/fabric.go](pkg/network/mockib/daemon/fabric.go)
- [pkg/network/mockib/daemon/fabric_register_test.go](pkg/network/mockib/daemon/fabric_register_test.go)
- [pkg/network/mockib/daemon/server.go](pkg/network/mockib/daemon/server.go)
- [pkg/network/mockib/daemon/server_smp_test.go](pkg/network/mockib/daemon/server_smp_test.go)
- [pkg/network/mockib/daemon/server_test.go](pkg/network/mockib/daemon/server_test.go)
- [pkg/network/mockib/fabric/graph.go](pkg/network/mockib/fabric/graph.go)
- [pkg/network/mockib/fabric/graph_test.go](pkg/network/mockib/fabric/graph_test.go)
- [pkg/network/mockib/registry/registry.go](pkg/network/mockib/registry/registry.go)
- [pkg/network/mockib/registry/registry_test.go](pkg/network/mockib/registry/registry_test.go)
- [pkg/network/mockib/subnet/synthesize.go](pkg/network/mockib/subnet/synthesize.go)
- [pkg/network/mockib/subnet/synthesize_test.go](pkg/network/mockib/subnet/synthesize_test.go)
- [pkg/network/mockib/sysfs/scan.go](pkg/network/mockib/sysfs/scan.go)
- [pkg/network/mockib/sysfs/scan_test.go](pkg/network/mockib/sysfs/scan_test.go)
- [pkg/system/mockpcisysfs/c/shim.c](pkg/system/mockpcisysfs/c/shim.c)
- [pkg/system/mockpcisysfs/config/types.go](pkg/system/mockpcisysfs/config/types.go)
- [pkg/system/mockpcisysfs/render/render.go](pkg/system/mockpcisysfs/render/render.go)
- [pkg/system/mockpcisysfs/render/render_test.go](pkg/system/mockpcisysfs/render/render_test.go)
- [pkg/system/mockpcisysfs/shim/shim_test.go](pkg/system/mockpcisysfs/shim/shim_test.go)
- [tests/e2e/validate-sminfo.sh](tests/e2e/validate-sminfo.sh)

</details>



This section documents the mechanisms and components involved in simulating NVIDIA's GPU interconnectivity and PCIe device topology within the `k8s-test-infra` project. The mock implementations enable comprehensive testing of Kubernetes GPU scheduling, device discovery, and fabric interactions without requiring physical hardware. The technologies covered include NVLink (GPU interconnect), InfiniBand (IB networking), and PCIe device topology. This page details the architecture, key tools—including the `mock-ib` daemon and the `render-pci-sysfs` utility—the LD_PRELOAD shims (`libibmocksys.so` and `libpcimocksys.so`), NVLink link field semantics, and the fabric/ComputeDomain simulation subsystem within the mock NVML engine.

---

## 1. Overview of Simulation Components

The simulation is split across multiple cooperating components focusing on different layers of the GPU and fabric stack:

- **mock-ib daemon**: An InfiniBand protocol mock daemon that listens on a UNIX domain socket, intercepts synthetic InfiniBand management packets, and emulates subnet management responses and MAD (Management Datagram) traffic. It synthesizes SMP requests (like Subnet Manager Port Info queries) per a configured IB topology.

- **render-pci-sysfs tool**: A CLI utility that reads GPU profile YAML configs, extracts a PCIe topology (`pcie_topology:` block), and writes a fake PCI sysfs directory tree, replicating key attributes and symlink structure of real Linux PCI device sysfs entries. This is critical for tools like `lspci` and device attribute resolution libraries used in Kubernetes scheduling.

- **LD_PRELOAD shims (`libibmocksys.so`, `libpcimocksys.so`)**: Shared library shims intercept syscalls related to file operations and directory scans on paths under `/sys/bus/pci` and InfiniBand device trees. They transparently redirect lookups and operations to simulated sysfs under configured root dirs (`MOCK_PCI_ROOT` and `MOCK_IB_ROOT`), enabling user-space tools and drivers to operate against the simulated data.

- **NVLink field values**: The mock NVML engine simulates NVLink link state and error counters using enumerated field values. These represent the hardware link states reported by real GPUs and populate NVML calls like `nvmlDeviceGetGpuFabricInfo*`.

- **Fabric/ComputeDomain simulation**: This subsystem under the GPU mock engine simulates NVLink fabric domains (ComputeDomains), including cluster and clique UUIDs, node assignments, and health/state bitmasks. It supports multi-node cluster testing and emulation of fabric state propagated via NVML API calls.

Together, these simulate complex GPU interconnect and networking conditions essential for scheduler logic, device feature discovery, and runtime behavior validation in orchestrated Kubernetes environments.

---

## 2. The mock-ib Daemon

The mock-ib daemon provides a user-space mock of the InfiniBand protocol stack's management and fabric functionality. It is implemented as a long-running server listening on a UNIX socket specified at start.

### Key Functionality

- Listens on Unix domain sockets to accept client connections representing InfiniBand subsystem clients.
- Implements handlers for SMP (Subnet Management Packets) such as retrieving port info, node info, and SM (Subnet Manager) info.
- Synthesizes granular IB subnet topology and port states, including LID assignments, port physical state flags, and management attributes.
- Supports fabric simulation via integration with the fabric graph subsystem.
- Provides operational support to tests that execute IB-related queries, to validate controller and device interactions.

### Implementation Highlights

- The daemon startup is performed by `NewServer` which configures socket paths and loads IBRoot directory states and optionally fabric simulation (`Fabric` flag).
- For SMP request handling, packet inspection and response generation are guided by InfiniBand management class and attribute IDs (e.g., PortInfo, SMInfo).
- Uses the `fabric` package to build a graph of IB ports and peers representing physical and virtual topology.
- Implements state tracking of ports and responds to GET/SET MAD messages, including fabric events.
- Test coverage includes SMP request/response cycles and validation of generated payloads.

```mermaid
flowchart TD
    ClientApp[IB Client Process]
    mockIB_Socket[Unix Domain Socket]
    mock_ib_Daemon[mock-ib Daemon]
    FabricGraph[Fabric Graph (pkg/network/mockib/fabric)]
    IBTopologyDir[IB Sysfs Mock Dir]

    ClientApp -->|Connects| mockIB_Socket
    mockIB_Socket --> mock_ib_Daemon
    mock_ib_Daemon -->|Synthesize SMP responses| FabricGraph
    mock_ib_Daemon -->|Read config files| IBTopologyDir
```

Sources: `pkg/network/mockib/daemon/server.go` (overview), `pkg/network/mockib/daemon/server_smp_test.go` (tests)  
---

## 3. The render-pci-sysfs Tool

`render-pci-sysfs` is a CLI utility to generate a synthetic PCI sysfs filesystem tree based on a GPU mock profile.

### Purpose

- Reads the `pcie_topology:` block embedded in a mock-nvml profile YAML configuration.
- Writes a full fake PCI sysfs tree under a specified fake root directory.
- Produces directory structures, device symlinks, `numa_node` files, identity files (`vendor`, `device`, `subsystem_vendor`, `subsystem_device`), and a 256-byte binary `config` file per PCI device.
- Enables user-space tools like `lspci` and the Kubernetes deviceattribute library to resolve PCI device topology as if real devices were present.

### Data Flow and Usage

1. Load and parse mock-nvml profile YAML with `sigs.k8s.io/yaml`.
2. Validate topology and device PCI identities.
3. Generate `/sys/devices/pciXXXX:YY/` directories corresponding to PCI root complexes.
4. For each device BDF, create a directory with attribute files populated from device identity or defaults.
5. Create symlinks from `/sys/bus/pci/devices/<bdf>` mapping to the device directories with relative paths.
6. Output written under a provided root directory (`--output`).

### Code Structure

- Main function parses flags `--config` and `--output`, loads config, validates, and calls `render.Render()`.
- The `render` package implements rendering logic, exposes `Options` struct and `Render` function.
- `renderRootComplex()` method creates directories, `numa_node` files, and device attribute files.
- Device attributes obey PCI conventions: `vendor`, `device`, `class`, `revision`, `irq`.
- A binary VMware-like PCI config space (256 bytes) is synthesized, beginning with vendor and device IDs.

```mermaid
graph TD
    ConfigYAML["mock-nvml profile YAML with pcie_topology"]
    renderPciSysfs["render-pci-sysfs CLI"]
    PCIeTopology["PCIeTopology struct"]
    SysfsTree["Fake PCI sysfs device tree"]
    DeviceIdentities["PCI Device IDs"]

    ConfigYAML --> renderPciSysfs
    renderPciSysfs --> PCIeTopology
    renderPciSysfs --> DeviceIdentities
    PCIeTopology --> SysfsTree
    DeviceIdentities --> SysfsTree
```

---

#### Directory and Symlink Layout

- `/sys/devices/pci0000:00/0000:07:00.0/numa_node` contains NUMA node number as a single integer string with newline.
- `/sys/bus/pci/devices/0000:07:00.0` is a symlink pointing to `../../../devices/pci0000:00/0000:07:00.0`.
- Attribute files like `vendor`, `device`, `subsystem_vendor`, `subsystem_device`, `class`, `revision`, `irq` are text files with PCI hex values.
- `config` is a 256-byte binary file containing PCI config space starting with Vendor ID and Device ID fields in little endian.

---

## 4. LD_PRELOAD Shims: libibmocksys.so and libpcimocksys.so

The simulation leverages LD_PRELOAD-style shared library shims that intercept system calls to redirect and virtualize sysfs accesses:

### libpcimocksys.so

- Redirects open, openat, fopen, and readlink syscalls targeting paths under `/sys/bus/pci`.
- Redirects path lookups to a configured `MOCK_PCI_ROOT` directory holding the synthetic PCI sysfs tree generated by `render-pci-sysfs`.
- Handles fortified libc open variants (`__open_2`) to avoid escapes due to glibc fortify optimizations.
- Enables tools like `lspci` to read synthetic PCI attributes as if they were native files.
- Special care is taken to replicate relative symlink targets to support deviceattribute libraries resolving PCI roots correctly.

### libibmocksys.so

- Similarly redirects file operations over InfiniBand sysfs tree paths to a synthetic IB root, typically managed by the `mock-ib` daemon and rendered data.
- Ensures user-space IB tools transparently interact with the simulated IB topology.

### Implementation Highlights

- Uses `dlsym(RTLD_NEXT)` to fetch real syscall pointers.
- On intercepted calls, rewrites paths with configured mock roots if the prefix matches PCI or IB sysfs paths.
- Respects maximum path lengths and returns `ENAMETOOLONG` on overflow instead of silently falling back.
- Compiled C interceptors reside under `pkg/system/mockpcisysfs/c/shim.c`.

---

## 5. NVLink Field Values and Fabric Simulation

Within the mock NVML engine, NVLink and fabric simulation populates fields that describe link health, state, and fabric domain membership.

### NVLink Field Semantics

- Each NVLink has a state enumerated as a specific numeric value (e.g., `LINKUP`, `DOWN`, etc.) tracked within the device state.
- Error counts, health masks, and link states are exposed through instrumented NVML API functions enabling tests to validate fabric behavior.

### Fabric / ComputeDomain Simulation

- The package `pkg/gpu/mocknvml/bridge/fabric.go` exports NVML API functions like `nvmlDeviceGetGpuFabricInfo` and its versioned variant `nvmlDeviceGetGpuFabricInfoV`.
- These functions return a `nvmlGpuFabricInfo_t` structure populated from the simulated fabric state held by `ConfigurableDevice` instances.
- The fabric config includes:
  - `ClusterUUID` (a 16-byte UUID string),
  - `CliqueID` (an integer identifying the clique),
  - `State` (governed by enums like `FabricStateCompleted`, `FabricStateNotStarted`),
  - `HealthMask` and `HealthSummary` bitmasks.
- A topology overlay facility merges cluster topology (from YAML) with device defaults, dynamically adjusting fabric membership based on node environment variables.
- Fabric health and state propagate through multi-versioned NVML structs, supporting backward-compatibility test scenarios.

```mermaid
graph TD
    Device[*engine.ConfigurableDevice*]
    NvmlAPI["nvmlDeviceGetGpuFabricInfo*"]
    FabricConfig["FabricConfig (ClusterUUID, CliqueID, State, HealthMask)"]
    ClusterTopology["YAML Topology file (MOCK_TOPOLOGY_CONFIG)"]

    Device --> FabricConfig
    NvmlAPI --> Device
    ClusterTopology --> FabricConfig
```

---

## 6. Architectural Summary and Interaction

```mermaid
flowchart TD
    subgraph PCI_Simulation
        RenderPCI[render-pci-sysfs]
        PCIConfigDir[/sys/devices/pciXXXX:XX/]
        PCIBusSymlinks[/sys/bus/pci/devices/]
        LibPCShim[libpcimocksys.so]
        UserSpaceTools[lspci, deviceattribute lib]
    end

    subgraph IB_Simulation
        MockIBDaemon[mock-ib daemon]
        IBSysfsDir[/sys/class/infiniband/ etc.]
        LibIBShim[libibmocksys.so]
        IBTools[InfiniBand user tools]
    end

    subgraph NVML_Fabric
        GPUDevices[ConfigurableDevice instances]
        NVMLAPIs[nvmlDeviceGetGpuFabricInfo*]
        FabricConfigYAML[ComputeDomain topology YAML]
    end

    UserSpaceTools -->|open/readlink| LibPCShim
    LibPCShim -->|redirects| PCIConfigDir
    PCIConfigDir --> RenderPCI
    IBTools --> LibIBShim
    LibIBShim --> IBSysfsDir
    IBSysfsDir --> MockIBDaemon
    GPUDevices --> NVMLAPIs
    FabricConfigYAML --> GPUDevices
```

---

## Summary

This NVLink, InfiniBand, and PCIe simulation subsystem in the `k8s-test-infra` is a sophisticated mock infrastructure enabling Kubernetes device and fabric-related tests to run in hardware-free environments. The `mock-ib` daemon and PCI sysfs renderer produce realistic topologies, while the LD_PRELOAD shims ensure user-space tools transparently access synthetic device information. The NVML mock fabric bridge closely mimics NVLink ComputeDomain states facilitating multi-node GPU fabric testing. Together, these components enable end-to-end testing of device feature discovery, scheduling, and fabric-aware runtime features.

---

# References and Sources

- `cmd/render-pci-sysfs/main.go:4-98`  
- `pkg/system/mockpcisysfs/render/render.go:4-160`  
- `pkg/system/mockpcisysfs/render/render_test.go:18-171`  
- `pkg/system/mockpcisysfs/config/types.go:4-169`  
- `pkg/system/mockpcisysfs/c/shim.c:1-195`  
- `pkg/system/mockpcisysfs/shim/shim_test.go:1-200`  
- `pkg/network/mockib/daemon/server_smp_test.go:1-183`  
- `pkg/network/mockib/daemon/server.go` (overview)  
- `pkg/network/mockib/fabric/graph.go:1-47`  
- `pkg/network/mockib/subnet/synthesize.go:1-170`  
- `pkg/gpu/mocknvml/bridge/fabric.go:1-130`  
- `pkg/gpu/mocknvml/engine/fabric_test.go:1-181`

---

# Page: ComputeDomain and IMEX Simulation

# ComputeDomain and IMEX Simulation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cmd/fake-imex/ctl/main.go](cmd/fake-imex/ctl/main.go)
- [cmd/fake-imex/ctl/peers.go](cmd/fake-imex/ctl/peers.go)
- [cmd/fake-imex/ctl/peers_test.go](cmd/fake-imex/ctl/peers_test.go)
- [cmd/fake-imex/daemon/main.go](cmd/fake-imex/daemon/main.go)
- [cmd/fake-imex/integration_test.go](cmd/fake-imex/integration_test.go)
- [cmd/imex-nogpu-shim/exec_test.go](cmd/imex-nogpu-shim/exec_test.go)
- [cmd/imex-nogpu-shim/main.go](cmd/imex-nogpu-shim/main.go)
- [cmd/imex-nogpu-shim/main_test.go](cmd/imex-nogpu-shim/main_test.go)
- [deployments/nvml-mock/Dockerfile.compute-domain-daemon](deployments/nvml-mock/Dockerfile.compute-domain-daemon)
- [deployments/nvml-mock/helm/nvml-mock/templates/network-policy-ibping.yaml](deployments/nvml-mock/helm/nvml-mock/templates/network-policy-ibping.yaml)
- [deployments/nvml-mock/helm/nvml-mock/tests/network_policy_ibping_test.yaml](deployments/nvml-mock/helm/nvml-mock/tests/network_policy_ibping_test.yaml)
- [docs/demo/compute-domain/README.md](docs/demo/compute-domain/README.md)
- [docs/demo/compute-domain/run.sh](docs/demo/compute-domain/run.sh)
- [pkg/gpu/mocknvml/bridge/fabric.go](pkg/gpu/mocknvml/bridge/fabric.go)
- [pkg/gpu/mocknvml/bridge/fabric_dispatch.go](pkg/gpu/mocknvml/bridge/fabric_dispatch.go)
- [pkg/gpu/mocknvml/bridge/fabric_dispatch_test.go](pkg/gpu/mocknvml/bridge/fabric_dispatch_test.go)
- [pkg/gpu/mocknvml/bridge/fabric_layout_test.go](pkg/gpu/mocknvml/bridge/fabric_layout_test.go)
- [pkg/gpu/mocknvml/engine/fabric_test.go](pkg/gpu/mocknvml/engine/fabric_test.go)
- [pkg/imexcoord/coord.go](pkg/imexcoord/coord.go)
- [pkg/imexcoord/coord_test.go](pkg/imexcoord/coord_test.go)
- [tests/e2e/kind-compute-domain-config.yaml](tests/e2e/kind-compute-domain-config.yaml)

</details>



This page documents the ComputeDomain (multi-node GPU fabric) simulation subsystem within nvml-mock, including the integration of real `nvidia-imex` daemons running in NO GPU mode via the `imex-nogpu-shim`, the legacy fake-imex coordination protocol, the `fake-fabricmanager`, and the Kubernetes NetworkPolicy for limiting cross-pod multimad (MAD) traffic relay. These components enable simulating multi-node fabric topology and inter-node communication over the pod network in Kubernetes test clusters without requiring actual GPU hardware or real NVIDIA fabric adapters.

---

## 1. Overview and Purpose

The ComputeDomain simulation emulates NVIDIA's NVLink fabric topologies and the behaviors of IMEX daemons responsible for GPU fabric domain coordination, but without physical hardware. It is designed to function on Kubernetes test clusters (e.g., Kind) with multiple worker nodes labeled and grouped into fabric cliques.

Key design goals include:

- Simulating multi-node fabric topologies by overlaying YAML/ConfigMap topology data on per-node NVML mock profiles.
- Replacing the legacy fake IMEX coordination protocol—which uses hostPath-shared empty marker files to signal presence—with the real `nvidia-imex` daemon running in NO GPU mode for true networked peer coordination.
- Using `imex-nogpu-shim` to transparently inject `--nogpu` flags to the real `nvidia-imex` daemon binary.
- Providing container images that bundle the mock NVML stack, real IMEX daemons, and coordination shims.
- Controlling pod-level permissions and ingress via Kubernetes NetworkPolicy for sound multi-node inter-pod communication (MAD traffic).
- Enabling test-time overlays, topology rebinding, and readiness probe emulation.

This simulation serves both as a powerful test infrastructure component for Kubernetes GPU device plugins and as a demo showing complex GPU fabric domain coordination at the software level.

---

## 2. ComputeDomain Fabric Simulation in NVML Mock

The mock NVML library implements native NVML GPU fabric APIs to surface cluster-wide topology information to consumers like the NVIDIA Device Plugin and DRA driver.

- The `pkg/gpu/mocknvml/bridge/fabric.go` file exports the NVML functions:
  - `nvmlDeviceGetGpuFabricInfo`
  - `nvmlDeviceGetGpuFabricInfoV`

These hand-written bindings fetch per-GPU fabric info via the mock engine layer (`engine.ConfigurableDevice.GetMockFabricInfo` and `.GetMockFabricInfoV`), allowing the simulated GPUs to expose:

- The NVLink fabric cluster UUID
- Clique ID (fabric domain membership)
- Fabric state (e.g., completed)
- Health masks (starting from v2/v3 API structs)

The cluster-level topology overlay is applied dynamically from a ConfigMap specifying domains, cliques, and member Kubernetes node names. The mock engine uses the environment variable `NODE_NAME` to match the local node in the overlay and adjust fabric data accordingly.

This topology injection causes each node's GPUs to report consistent fabric IDs matching their clique membership, simulating NVLink cluster assignments on real hardware.

```mermaid
flowchart TB
  subgraph "mock NVML library (pkg/gpu/mocknvml)"
    A[nvmlDeviceGetGpuFabricInfo]
    B[nvmlDeviceGetGpuFabricInfoV]
    C[engine.ConfigurableDevice.GetMockFabricInfo / GetMockFabricInfoV]
    D[engine.Engine / Device Table]
    E[Topology Overlay from ConfigMap (MOCK_TOPOLOGY_CONFIG)]
  end

  A --> C
  B --> C
  C --> D
  C --> E
```

Sources:  
`pkg/gpu/mocknvml/bridge/fabric.go:51-128`  
`pkg/gpu/mocknvml/engine/fabric_test.go:27-130`  
`docs/demo/compute-domain/README.md:1-181`

---

## 3. Fake-IMEX Daemon and Coordination Protocol (Deprecated)

Originally, a lightweight file-based coordination protocol was used to simulate multi-node IMEX daemons without GPUs:

- **Fake IMEX Daemon (`cmd/fake-imex/daemon`):**  
  On startup, it writes a marker file named by its pod IP in a shared hostPath directory (usually `/var/lib/nvml-mock/imex-state`) signaling presence in the fabric clique.

- **Fake IMEX Control (`cmd/fake-imex/ctl`):**  
  Used as a readiness probe. It reads a list of expected peer pod IPs from a shared `nodes.cfg` file and checks that marker files exist for all peers. If all peers are ready, it prints `READY` and exits 0; otherwise, it exits 1.

- This protocol relies on the shared hostPath volume for file-based signaling, a design suited for Kind multi-node clusters.

- The daemon reasserts its marker every 2 seconds for resilience against accidental cleanup.

- The protocol lacks liveness detection on SIGKILL and pod evictions but suffices for ephemeral cluster tests.

- Both binaries accept legacy CLI flags for compatibility.

### Data Flow and Lifecycle

```mermaid
sequenceDiagram
    participant Daemon as fake-imex daemon
    participant StateDir as HostPath volume (imex-state)
    participant Config as nodes.cfg file
    participant Ctl as fake-imex ctl (probe)

    Daemon->>StateDir: Write empty marker file named by POD_IP
    Daemon->>Daemon: On SIGTERM remove marker file
    Daemon->>Daemon: Every 2s re-assert marker file

    Ctl->>Config: Read nodes.cfg (list of pod IPs)
    Ctl->>StateDir: Check marker files for all IPs
    alt All markers present
      Ctl->>User: Print "READY\n" and exit 0
    else Missing markers
      Ctl->>User: Print error and exit 1
    end
```

### Key Implementation Details:

- `imexcoord` package provides shared helpers to manage state directories, marker files, and node configuration reading.
- Marker write is idempotent and guarded by IP validation.
- Daemon logs re-reads of nodes.cfg on SIGUSR1.
- `ctl` only supports `-q` query mode for readiness.
- The deprecation notice in logs announces real IMEX replacement.

This protocol is deprecated and replaced by the real IMEX daemon with the `--nogpu` shim.

Sources:  
`cmd/fake-imex/daemon/main.go:14-101`  
`cmd/fake-imex/ctl/main.go:14-75`  
`pkg/imexcoord/coord.go:14-283`  
`cmd/fake-imex/integration_test.go:31-196`

---

## 4. Real IMEX Daemon with imex-nogpu-shim

To replace the fake marker mechanism, the simulation runs the real upstream `nvidia-imex` daemon, but in a **NO GPU** mode:

- The `imex-nogpu-shim` is a small Go shim executable that installs as `/usr/bin/nvidia-imex` inside the container.
- When launched, the shim execs the real binary `/usr/bin/nvidia-imex.real` with the `--nogpu` flag appended.
- This cause the real daemon to disable GPU detection and run purely in networked peer mode over gRPC.
- Daemon health ready probes use the real `nvidia-imex-ctl` client interrogating the pod network.
- This approach works in any Kubernetes cluster without shared hostPath volumes.

### Image Configuration (`Dockerfile.compute-domain-daemon`)

- The overlay image combines:
  - The real `nvidia-imex` and `nvidia-imex-ctl` binaries installed from Ubuntu 22.04 multiverse package `nvidia-imex-595`.
  - The Go-built `imex-nogpu-shim` binary replacing the front-line `nvidia-imex` executable.
  - The `nvml-mock:compute-domain` base image containing the mock NVML stack and `check-fabric` utility.
- Two targets:
  - `daemon` (default): real IMEX + shim on upstream compute-domain-daemon base image.
  - `demo`: overlays real IMEX with shim onto the mock NVML image, used by the documented demo script.

```mermaid
graph LR
  A[Base: ubuntu:22.04 + nvidia-imex-595 packages] --> B[real nvidia-imex and nvidia-imex-ctl]
  C[Go-built imex-nogpu-shim] --> D[replaces /usr/bin/nvidia-imex]
  E[nvml-mock:compute-domain base image] --> F[provides NVML mock + check-fabric]

  subgraph Dockerfile.compute-domain-daemon overlay build
    B
    D
  end --> G[final image: real IMEX with shim]

  F --> G

```

Sources:  
`deployments/nvml-mock/Dockerfile.compute-domain-daemon:15-88`  
`cmd/imex-nogpu-shim/main.go`  
`docs/demo/compute-domain/README.md:13-90`

---

## 5. ComputeDomain Demo and Topology Overlay

The [ComputeDomain demo](docs/demo/compute-domain/README.md) exercises the full multi-node fabric simulation end-to-end:

- Creates a dedicated Kind cluster with four workers labeled into two cliques (0 and 1).
- Builds and loads `nvml-mock:compute-domain` and demo overlay images that combine NVML mock plus real IMEX with shim.
- Installs the chart with GB200 GPU profile and topology overlay enabled.
- The topology ConfigMap specifies domain UUIDs, cliques, and node membership.
- Pods pick up node clique via `NODE_NAME` env var to reflect fabric overlay.
- Run `check-fabric` inside pods verifies correct cluster UUID, clique ID, and fabric state.
- Real IMEX daemons form a network fabric domain in NO GPU mode:
  - `nvidia-imex-ctl -q` returns `READY` when all peers are up.
  - Domain reports UP status and version `NO_GPU`.
  - Killing one daemon causes domain to leave UP state.
- Helm upgrade can rebind topology documents without rebuilding images.

This demonstrates the seamless integration of the mock NVML fabric simulation with real IMEX network-based coordination.

Sources:  
`docs/demo/compute-domain/README.md`  
`docs/demo/compute-domain/run.sh`  
`tests/e2e/kind-compute-domain-config.yaml`

---

## 6. `fake-fabricmanager`

`fake-fabricmanager` is a legacy utility in the fake IMEX ecosystem to simulate backend services like fabric topology management but is largely superseded by real IMEX usage. It is not documented in detail here due to limited relevance and the real IMEX subnet cluster mode.

---

## 7. Kubernetes NetworkPolicy for Cross-Pod MAD Traffic Relay

The ComputeDomain simulation requires inter-pod communication on several TCP ports to enable fabric peers to communicate (multi-pod MAD):

- The DaemonSet pods expose:
  - TCP port `ibping` (mock InfiniBand ping listener)
  - TCP port `imex` (real IMEX gRPC peer traffic, default 50000)
  - TCP port `imex-cmd` (command/status grpc, default 50005)
- The NetworkPolicy defined in the Helm chart (`templates/network-policy-ibping.yaml`) applies when:
  - The infiniband ping networkPolicy is enabled in values.
  - The GPU profile supports InfiniBand fabric (`infiniband.enabled=true`).
- It allows ingress TCP traffic on these ports **only** from pods with the same labels (`app.kubernetes.io/name: nvml-mock`, `component: daemon`) in **any namespace**.
- Egress is left unrestricted to permit DNS-based discovery.
- This policy is mandatory on Kind clusters where the default `kindnetd` enforces NetworkPolicies by default.
- It limits the exposure surface of the mock fabric listener to intended peers to prevent external interference.

```mermaid
graph TD
  NP[NetworkPolicy: nvml-mock-ibping] -->|Ingress allow| PeerPods[nvml-mock Daemon pods cluster-wide]
  NP -->|Restricts Ports| Ports[(ibping, imex, imex-cmd TCP ports)]
  PeerPods -->|Communicate over TCP| Pods

  classDef policy fill:#fff,stroke:#000,stroke-width:1px;
  class NP policy;
```

Sources:  
`deployments/nvml-mock/helm/nvml-mock/templates/network-policy-ibping.yaml`  
`deployments/nvml-mock/helm/nvml-mock/tests/network_policy_ibping_test.yaml`

---

## 8. Summary Diagram: Components and Interactions

```mermaid
graph LR
  subgraph Kubernetes Cluster (Kind Multi-Node)
    PodA[nvml-mock daemon pod (worker 0)]
    PodB[nvml-mock daemon pod (worker 1)]
    PodC[nvml-mock daemon pod (worker 2)]
    PodD[nvml-mock daemon pod (worker 3)]

    PodA -->|nvidia-imex (shim + real daemon NO GPU mode)| IMEXA[nvidia-imex process]
    PodB -->|nvidia-imex (shim + real daemon)| IMEXB[nvidia-imex process]
    PodC -->|nvidia-imex (shim + real daemon)| IMEXC[nvidia-imex process]
    PodD -->|nvidia-imex (shim + real daemon)| IMEXD[nvidia-imex process]

    IMEXA ---|gRPC peer traffic (imex port 50000)| IMEXB
    IMEXC ---|gRPC peer traffic| IMEXD

    PodA -- TCP (ibping, imex, imex-cmd) --> PodB
    PodA -- TCP (ibping, imex, imex-cmd) --> PodC
    PodB -- TCP (ibping, imex, imex-cmd) --> PodD

    subgraph HostPath Volumes (Deprecated)
      StateDir["/var/lib/nvml-mock/imex-state"]
      NodesCfg["/imexd/nodes.cfg"]
      PodAFakeMarker["marker ip marker file (PodA)"]
      PodBFakeMarker["marker ip marker file (PodB)"]
    end

    PodA -.-> PodAFakeMarker
    PodB -.-> PodBFakeMarker
    IMEXCtl[Fake 'nvidia-imex-ctl' readiness probe] -.-> NodesCfg
    IMEXCtl -.-> StateDir
  end

  subgraph NVML Mock Library inside Pod
    NVMLCall["call nvmlDeviceGetGpuFabricInfo(V)"]
    Engine["engine.ConfigurableDevice"]
    Topology["Topology Overlay ConfigMap"]
  end

  PodA --> NVMLCall
  NVMLCall --> Engine
  Engine --> Topology
```

---

# References

| Component                 | Code Locations                                                        |
|---------------------------|---------------------------------------------------------------------|
| Fake IMEX Daemon          | `cmd/fake-imex/daemon/main.go:14-101`                               |
| Fake IMEX Control         | `cmd/fake-imex/ctl/main.go:14-75`                                  |
| IMEX Coordination Helpers | `pkg/imexcoord/coord.go:14-283`                                    |
| IMEX Integration Tests    | `cmd/fake-imex/integration_test.go:31-196`                         |
| Real IMEX Shim + Overlay  | `deployments/nvml-mock/Dockerfile.compute-domain-daemon:15-88`     |
| Mock NVML Fabric APIs     | `pkg/gpu/mocknvml/bridge/fabric.go:51-128`                         |
| Mock NVML Fabric Tests    | `pkg/gpu/mocknvml/engine/fabric_test.go:27-130`                    |
| ComputeDomain Demo Script | `docs/demo/compute-domain/run.sh`                                  |
| Kind Cluster Config       | `tests/e2e/kind-compute-domain-config.yaml`                        |
| Network Policy YAML       | `deployments/nvml-mock/helm/nvml-mock/templates/network-policy-ibping.yaml` |
| Network Policy Tests      | `deployments/nvml-mock/helm/nvml-mock/tests/network_policy_ibping_test.yaml` |

---

This completes the comprehensive technical documentation of the ComputeDomain and IMEX simulation components in the NVIDIA k8s-test-infra codebase.

---

# Page: NRI Plugin for Node-Wide Injection

# 9.6 NRI Plugin for Node-Wide Injection

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cmd/nvml-mock-nri/dev_number_oracle_test.go](cmd/nvml-mock-nri/dev_number_oracle_test.go)
- [cmd/nvml-mock-nri/health.go](cmd/nvml-mock-nri/health.go)
- [cmd/nvml-mock-nri/health_test.go](cmd/nvml-mock-nri/health_test.go)
- [cmd/nvml-mock-nri/main.go](cmd/nvml-mock-nri/main.go)
- [cmd/nvml-mock-nri/main_test.go](cmd/nvml-mock-nri/main_test.go)
- [deployments/nvml-mock/helm/nvml-mock/templates/nri-daemonset.yaml](deployments/nvml-mock/helm/nvml-mock/templates/nri-daemonset.yaml)
- [deployments/nvml-mock/helm/nvml-mock/tests/nri_daemonset_test.yaml](deployments/nvml-mock/helm/nvml-mock/tests/nri_daemonset_test.yaml)
- [tests/e2e/go/scenario_nri_test.go](tests/e2e/go/scenario_nri_test.go)

</details>



This section documents the **nvml-mock-nri** plugin, a containerd Node Resource Interface (NRI) plugin designed for node-wide injection of the nvml-mock overlay into containers. The plugin enables ambient injection of simulated NVIDIA GPU devices and LD_PRELOAD shim libraries into Kubernetes pods transparently—without requiring explicit device requests or volume mounts from workloads.

---

## Purpose and Scope

The **nvml-mock-nri** plugin integrates with containerd's NRI framework to dynamically modify container creation specifications at runtime on a Kubernetes node. It injects:

- Device nodes representing mock NVIDIA GPUs
- Bind mounts for the nvml-mock overlay filesystem
- Environment variables controlling overlay topology
- LD_PRELOAD shims into containers for API interception and simulation

Key features include:

- Configuration via command-line flags and environment variables
- Health and readiness probes exposing plugin state
- Annotation-based opt-out and opt-in device injection controls
- Seamless injection into all pods on the node except explicitly excluded namespaces
- Support for integration with ComputeDomain fabrics topology injection for advanced GPU-fabric simulation

This page covers the implementation architecture, configuration options, health checks, container injection logic, opt-out mechanisms, and LD_PRELOAD shim handling.

---

## Implementation Overview

The main plugin binary is implemented in Go (`cmd/nvml-mock-nri/main.go`). At startup, it parses configuration flags, sets up a containerd NRI stub plugin, and serves HTTP health and readiness probes.

### High-Level Components

- **plugin struct**: Maintains configuration and health tracker 
- **stub.Plugin interface**: Implements containerd NRI plugin callbacks
- **Health tracker**: Tracks registration and request states for liveness/readiness
- **Injection logic**: Converts containerd container and pod specs into an internal form, decides injection based on annotations/namespaces, and constructs container adjustment specs with mounts, devices, mounts, and environment updates.

### Lifecycle

1. **Startup**:
   - Read plugin flags and environment variables (for overlay paths, node name, annotations, excluded namespaces, etc.)
   - Create the NRI stub plugin with a connection socket and plugin identity
   - Serve /healthz and /readyz endpoints for Kubernetes probes on a configurable port

2. **Registration**:
   - containerd calls `Configure()` to register the plugin
   - Plugin marks itself registered and ready to receive container events

3. **Handling new containers**:
   - Intercept `CreateContainer` events
   - Extract pod and container details and check opt-out annotation or excluded namespace
   - If injection enabled, prepare:
     - Filesystem bind mounts for nvml-mock overlay and topology if enabled
     - Device nodes (from a specific host device path)
     - Environment variables to pass topology config and LD_PRELOAD shim paths
   - Return `ContainerAdjustment` instructions to containerd to update the container spec

4. **Health Tracking**:
   - Track in-progress CreateContainer requests with timing
   - If a request gets stuck longer than a multiple of containerd's own RPC request timeout, mark as "wedged" causing readiness and liveness failures
   - Mark not ready if the plugin is not registered or connection closed

5. **Graceful exit** on signal interruption

---

## Configuration Flags and Defaults

| Flag                   | Env Variable                     | Default                                 | Description                                                                                     |
|------------------------|---------------------------------|-----------------------------------------|-------------------------------------------------------------------------------------------------|
| --socket-path          | NRI_SOCKET_PATH                 | `/var/run/nri/nri.sock`                  | Path to the containerd NRI UNIX socket                                                        |
| --health-addr          | NVML_MOCK_HEALTH_ADDR           | `:8080`                                 | HTTP address to serve /healthz and /readyz probe endpoints, empty disables probes              |
| --plugin-name          | NRI_PLUGIN_NAME                 | `nvml-mock`                             | Name of the plugin registered with containerd                                                 |
| --plugin-index         | NRI_PLUGIN_INDEX                | `10`                                    | Ordering index of the plugin                                                                   |
| --overlay-host-path    | NVML_MOCK_OVERLAY_HOST_PATH      | `/var/lib/nvml-mock`                    | Host path containing the nvml-mock overlay that is bind mounted into containers                |
| --overlay-mount-path   | NVML_MOCK_OVERLAY_MOUNT_PATH     | `/var/lib/nvml-mock`                    | Container path where the overlay is mounted                                                  |
| --node-name            | NODE_NAME                      | (empty)                                | Kubernetes node name; enables ComputeDomain topology injection when used                       |
| --topology-host-path   | NVML_MOCK_TOPOLOGY_HOST_PATH     | `<overlay-host-path>/topology/topology.yaml` | Host path checked for staged ComputeDomain topology document                                   |
| --topology-mount-path  | NVML_MOCK_TOPOLOGY_MOUNT_PATH    | `<overlay-mount-path>/topology/topology.yaml` | Container path injected as MOCK_TOPOLOGY_CONFIG environment variable                           |
| --device-host-path     | NVML_MOCK_DEVICE_HOST_PATH        | `<overlay-host-path>/driver/dev`       | Host path containing mock `/dev/nvidia*` device nodes                                         |
| --opt-out-annotation   | NVML_MOCK_OPT_OUT_ANNOTATION      | `nvml-mock.nvidia.com/inject`           | Pod annotation key; if set to `"false"`, injection is disabled for that pod                    |
| --device-annotation    | NVML_MOCK_DEVICE_ANNOTATION        | `nvml-mock.nvidia.com/device`           | Pod annotation key; if set to `"true"`, adds `/dev/nvidia*` device nodes into the container    |
| --excluded-namespaces  | NVML_MOCK_EXCLUDED_NAMESPACES      | `NAMESPACE,kube-system`                  | Comma-separated list of namespaces where injection is skipped                                 |
| --ld-preload-shims     | NVML_MOCK_LD_PRELOAD_SHIMS         | (paths relative to overlay mount)       | Comma-separated list of LD_PRELOAD shim paths injected into containers                         |

These options allow flexibility in how the overlay and device injection is applied, enabling node-specific features, namespace filtering, and selective opt-out/in per pod through annotations.

Sources: [cmd/nvml-mock-nri/main.go:30-152](), [deployments/nvml-mock/helm/nvml-mock/templates/nri-daemonset.yaml:1-98]()

---

## Health and Readiness Probes

The plugin serves HTTP probes at configurable ports (default `:8080`) for:

- `/healthz`: Liveness probe
- `/readyz`: Readiness probe

### Health States Tracked

The plugin monitors:

- **Registration state**: Whether it is currently registered with containerd and receiving container creation events.
- **In-flight requests**: Tracks ongoing `CreateContainer` RPC requests to detect stuck/wedged states.

The health logic distinguishes these states:

| State                                          | Readiness  | Liveness  | Description                              |
|------------------------------------------------|------------|-----------|------------------------------------------|
| 1. Process dead                                | N/A        | N/A       | Kubernetes handles this                   |
| 2. Alive, never registered                     | Not Ready  | Live      | Plugin not yet registered; no injection  |
| 3. Alive, registered and serving               | Ready      | Live      | Normal healthy operation                  |
| 4. Alive, registered, handler wedged (stuck)  | Not Ready  | Not Live  | Handler blocked; triggers restart        |
| 5. Alive, unregistered by containerd           | Not Ready  | Live      | Connection lost; injection stopped       |

### Wedged Request Detection

The plugin applies a timeout threshold to detect wedged handler requests:

```
wedged = (request_duration > (containerd_request_timeout * 2))
```

If a request exceeds two times the containerd RPC timeout, the plugin signals a liveness failure prompting the kubelet to restart it.

### Implementation Notes

- The health tracker uses a mutex and a map of in-flight request IDs to their start times.
- Register/Unregister updates the `registered` flag.
- Each `CreateContainer` begins a tracked request and defers marking it finished.
- HTTP handlers report `503 Service Unavailable` if readiness or liveness probes fail.
- The plugin logs health listen and readiness changes.

Sample probe response includes textual reason messages for easier debugging.

Sources: [cmd/nvml-mock-nri/health.go:6-193](), [cmd/nvml-mock-nri/health_test.go]()

---

## Opt-Out Annotation and Namespace Exclusion

Injection can be controlled on a per-pod basis by two pod annotations:

- **Opt-out annotation** (`nvml-mock.nvidia.com/inject` by default):
  - If set to `"false"`, the plugin skips injection for that pod.
  - Otherwise, injection is enabled by default.

- **Device annotation** (`nvml-mock.nvidia.com/device` by default):
  - If set to `"true"`, adds `/dev/nvidia*` device nodes into the container.

Additionally, the plugin excludes injection into any pod running in configured excluded namespaces (default includes `"NAMESPACE"` and `"kube-system"`).

These policies allow fine tuning of injection scope per workload.

### Injection Decision Logic

1. Check if pod namespace is in excluded list → skip injection.
2. Read opt-out annotation → if explicitly `"false"` → skip injection.
3. If injection proceeds:
   - Optionally add devices if device annotation is `"true"`.
   - Always mount nvml-mock overlay paths.
   - Inject LD_PRELOAD shim environment variables.

Sources: [cmd/nvml-mock-nri/main.go:133-152](), [deployments/nvml-mock/helm/nvml-mock/templates/nri-daemonset.yaml:45-51]()

---

## Container Injection Details

When intercepting the `CreateContainer` event, the plugin builds a `ContainerAdjustment` instructing containerd how to modify the container spec:

### Injected Elements

- **Mounts**:
  - Bind mount the nvml-mock overlay host path into the container at a configured mount path.
  - Bind mount the ComputeDomain topology document (if enabled by node name and topology document presence).

- **Devices**:
  - Inject `/dev/nvidia*` device nodes from the configured device host path if opted-in via annotation.

- **Environment Variables**:
  - `MOCK_TOPOLOGY_CONFIG`: Path inside the container to the staged topology document (if applicable).
  - `NODE_NAME`: Kubernetes node name (used for ComputeDomain).
  - `LD_PRELOAD`: Prepended with configured shim libraries injected relative to the overlay mount path or absolute paths.

### Data Flow

1. Convert containerd's `api.PodSandbox` and `api.Container` to internal `nvmlmock.Container` structure.
2. Call `nvmlmock.Adjust()` which applies configured filters and builds the injection spec.
3. Convert the internal injection spec to an NRI `ContainerAdjustment`.
4. Return adjustment to containerd to edit the OCI specification at container creation time.

The LD_PRELOAD shim injection enables API interception by wrapping standard NVIDIA libraries, allowing simulation of GPU behavior transparently inside containers.

Sources: [cmd/nvml-mock-nri/main.go:133-152](), [pkg/nri/nvmlmock/nvmlmock.go (external)]()

---

## LD_PRELOAD Shim Injection

To enable transparent interception of GPU APIs inside containers, the plugin injects LD_PRELOAD environment variables referencing shim shared libraries.

- Shims are configured via the `--ld-preload-shims` flag or `NVML_MOCK_LD_PRELOAD_SHIMS` environment variable as a comma-separated list of relative or absolute paths.
- These paths typically reside inside the mounted nvml-mock overlay, enabling the containerized workload to dynamically link against mock-layer shims.
- The shim library names and paths are prepended to the `LD_PRELOAD` environment variable in the container, preserving any existing value.

This injection enables simulation of GPU metrics, errors, and interactions without modifying container images or runtime commands.

Sources: [cmd/nvml-mock-nri/main.go:39-46,133-152]()

---

## NRI Plugin DaemonSet Deployment

The plugin is deployed on Kubernetes as a DaemonSet included in the `nvml-mock` Helm chart under `nri.enabled`.

### Deployment Features

- Container runs with the `nvml-mock-nri` image
- Mounts:
  - The NRI socket directory (`/var/run/nri`)
  - The nvml-mock overlay host directory (`/var/lib/nvml-mock`)
- Environment:
  - NODE_NAME mounted via fieldRef to inject the Kubernetes node name
- Configurable flags via Helm values:
  - Overlay host and container mount paths
  - Socket path location
  - Excluded namespaces list
  - Opt-out and device annotation keys
  - Health probe addresses and ports
- Probes:
  - Liveness probe hitting `/healthz`
  - Readiness probe hitting `/readyz`
- SecurityContext forbids privilege escalation; runs as root (required for device injection)
- Resource requests configurable (default modest CPU/memory)

### Helm Chart YAML Snippet (key elements)

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: RELEASE-NAME-nvml-mock-nri
  labels:
    app.kubernetes.io/name: nvml-mock-nri
    app.kubernetes.io/component: nri
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: nvml-mock-nri
      app.kubernetes.io/component: nri
  template:
    metadata:
      labels:
        app.kubernetes.io/name: nvml-mock-nri
        app.kubernetes.io/component: nri
    spec:
      serviceAccountName: RELEASE-NAME
      automountServiceAccountToken: false
      containers:
        - name: nvml-mock-nri
          image: ghcr.io/nvidia/nvml-mock:latest
          command: ["/usr/local/bin/nvml-mock-nri"]
          args:
            - --socket-path=/var/run/nri/nri.sock
            - --overlay-host-path=/var/lib/nvml-mock
            - --overlay-mount-path=/var/lib/nvml-mock
            - --device-host-path=/var/lib/nvml-mock/driver/dev
            - --opt-out-annotation=nvml-mock.nvidia.com/inject
          env:
            - name: NODE_NAME
              valueFrom:
                fieldRef:
                  fieldPath: spec.nodeName
          ports:
            - name: health
              containerPort: 8080
          readinessProbe:
            httpGet:
              path: /readyz
              port: health
          livenessProbe:
            httpGet:
              path: /healthz
              port: health
          volumeMounts:
            - name: nri-socket-dir
              mountPath: /var/run/nri
            - name: nvml-mock-overlay
              mountPath: /var/lib/nvml-mock
              readOnly: true
      volumes:
        - name: nri-socket-dir
          hostPath:
            path: /var/run/nri
            type: DirectoryOrCreate
        - name: nvml-mock-overlay
          hostPath:
            path: /var/lib/nvml-mock
            type: DirectoryOrCreate
```

Sources: [deployments/nvml-mock/helm/nvml-mock/templates/nri-daemonset.yaml](), [deployments/nvml-mock/helm/nvml-mock/tests/nri_daemonset_test.yaml]()

---

## Data Flow and Key Functions/Class Associations

The following diagrams associate natural language concepts with code entities for top-level understanding.

### Diagram 1: Plugin Initialization and Event Loop

```mermaid
flowchart TB
    A["main()"] --> B["nvmlmock.DefaultConfig()"]
    A --> C["flag.Parse()"]
    A --> D["stub.New(plugin)"]
    D --> E["plugin.Configure()"]
    E --> F["plugin.CreateContainer()"]
    A --> G["serveHealth(addr, health)"]
    G --> H["health.handler()"]
    A --> I["signal.NotifyContext()"]
    A --> J["s.Run(ctx)"]

    subgraph "Health"
        H --> K["health.readiness()"]
        H --> L["health.liveness()"]
    end
```

This shows how `main` initializes config, parses flags, creates an NRI stub plugin that hooks into containerd, serves HTTP health probes, and runs an event loop to handle container creation requests.

Sources: [cmd/nvml-mock-nri/main.go:20-90](), [cmd/nvml-mock-nri/health.go:20-190]()

---

### Diagram 2: Container Injection Logic Flow

```mermaid
graph LR
    P["CreateContainer(ctx, pod, container)"] --> Q["fromNRI(pod, container) -> nvmlmock.Container"]
    Q --> R["nvmlmock.Adjust(config, nvmlmock.Container)"]
    R -->|adjusted| S["toNRI(ContainerAdjustment)"]
    S --> T["Return ContainerAdjustment to containerd"]

    subgraph "Injection decision"
        direction TB
        Q -- Extract annotations and namespace --> U[Check opt-out annotation and excluded namespaces]
        U -- If excluded or opt-out false --> V[No injection; return nil]
        U -- Otherwise --> R
    end
```

This diagram visualizes the flow from receiving the container event to deciding whether to inject, applying adjustments, converting back to NRI API objects, and returning the result.

Sources: [cmd/nvml-mock-nri/main.go:133-152]()

---

## Summary

The **nvml-mock-nri** plugin provides a critical integration point enabling node-wide ambient injection of simulated NVIDIA GPU environments into Kubernetes containers using containerd's NRI framework. It balances fine-grained opt-out controls with global namespace exclusions and detailed health checking to ensure robust operation in test and simulation clusters.

The plugin's code modularity and configuration flexibility allow emulating complex GPU topologies, device presence, and API behaviors transparently, aiding in testing and development of GPU-aware Kubernetes operators and workloads.

---

# References

- `cmd/nvml-mock-nri/main.go` (lines 1-152)
- `cmd/nvml-mock-nri/health.go` (lines 1-193)
- `deployments/nvml-mock/helm/nvml-mock/templates/nri-daemonset.yaml`
- `deployments/nvml-mock/helm/nvml-mock/tests/nri_daemonset_test.yaml`
- `tests/e2e/go/scenario_nri_test.go`
- `cmd/nvml-mock-nri/health_test.go`
- `cmd/nvml-mock-nri/main_test.go`
- `cmd/nvml-mock-nri/dev_number_oracle_test.go`

---

This concludes the documentation for the "9.6 NRI Plugin for Node-Wide Injection" leaf page.

---

# Page: Runtime Control with nvml-mock-ctl

# Runtime Control with nvml-mock-ctl

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cmd/nvml-mock-ctl/main.go](cmd/nvml-mock-ctl/main.go)
- [cmd/nvml-mock-ctl/main_test.go](cmd/nvml-mock-ctl/main_test.go)
- [docs/nvml-mock-ctl.md](docs/nvml-mock-ctl.md)
- [pkg/gpu/mockctl/config_override.go](pkg/gpu/mockctl/config_override.go)
- [pkg/gpu/mockctl/config_override_test.go](pkg/gpu/mockctl/config_override_test.go)
- [tests/e2e/go/scenario_runtime_control.go](tests/e2e/go/scenario_runtime_control.go)
- [tests/e2e/go/scenario_standalone_test.go](tests/e2e/go/scenario_standalone_test.go)

</details>



The `nvml-mock-ctl` tool facilitates **runtime control of simulated GPU states** within the nvml-mock system on a live Kubernetes node without requiring any Helm upgrade, image rebuild, or pod restart. It enables testers and developers to dynamically inject GPU state overrides such as failure scenarios, ECC mode toggling, temperature/power/fan/utilization metrics, and performance state adjustments on-the-fly.

This page covers the implementation details of `nvml-mock-ctl`, the **config_override** mechanism it uses to apply runtime device state patches, and explains how the **scenario_runtime_control** end-to-end (E2E) tests exercise this functionality to validate hot-reload semantics.

---

## Purpose and Scope

- **Purpose:** Allow immediate, device-level mutations of GPU simulation state for tests and demos, avoiding disruptive restarts or redeployments.
- **Scope:** Per-node device overrides applied by writing a *config override* file on the host, merged in-process by the shared `libnvidia-ml.so` mock NVML library in every consumer container.
- **Audience:** Developers and testers working with the nvml-mock Kubernetes test infrastructure, especially those validating state transitions and dynamic conditions.

---

## 1. Background: nvml-mock and the Runtime Override Model

Unlike a traditional GPU daemon, the nvml-mock system is implemented as a **per-process shared library injection (`libnvidia-ml.so`)**, not as a centralized server process. Therefore, the `nvml-mock-ctl` tool cannot send RPCs or socket commands.

Instead, `nvml-mock-ctl` uses a **node-local on-disk config override file** approach to communicate with all running mock consumers on that node:

1. `nvml-mock-ctl` atomically writes a **config override YAML file** (`overrides.yaml`) into a configured directory on the node's filesystem.  
2. Each consumer process running the nvml-mock library periodically (default TTL = 1 second, controlled by the `MOCK_NVML_OVERRIDES_TTL` env var) reloads the override file and **deep-merges the patch on top** of the pristine base profile config (`config.yaml`).  
3. Since the config override file is bind-mounted into consumers (typically via CDI mounts), even already-running containers see the same updated state within the TTL window without restart or reload commands.  

### Merge Hierarchy

Overrides from `overrides.yaml` merge atop the base profile config as follows:

```
base config.yaml  <  config override "all:" block  <  config override "devices[<idx>]:" block
```

- A targeted per-device override entry takes precedence over the `all` block, which itself overrides base default values.
- Unknown fields and invalid types are rejected at write time, ensuring users catch typos or schema mistakes immediately.

### What Is Hot-Reloadable?

- **Hot-reloadable fields:** failure injection, ECC counters and mode, temperature, power, fan speed, utilization, clocks, throttle reasons, performance state, device memory stats, and NVLink error rates.
- **Immutable without restart:** device identity and topology fields such as `name`, `architecture`, `uuid`, `compute_capability`, PCI `bus_id`, and `bar1_memory` settings are baked at device construction and **cannot** be changed at runtime.

> To modify baked fields requires editing the Helm profile and restarting the DaemonSet pod.

---

## 2. Implementation Details of nvml-mock-ctl CLI

The CLI tool is implemented in **Go** with a pure Go backend for config override management and a thin main driver that:

- Parses CLI commands and flags,
- Resolves the GPU target device index or UUID,
- Loads and locks the override config file,
- Applies mutations via the `mockctl` package,
- Writes the new override file atomically, and
- Unlocks and exits.

### Components and Flow

```mermaid
flowchart LR
  A[User runs `nvml-mock-ctl` CLI] --> B{Command parsing}
  B --> C[Resolve GPU target from index/UUID/all]
  B --> D[Parse mutation arguments (fail, temp, power...)]
  C --> E[Load base config.yaml]
  E --> F[Lock overrides.yaml]
  F --> G[Load overrides.yaml into Doc]
  G --> H[Mutate Doc per command]
  H --> I[Validate & deep-merge patches]
  I --> J[Write updated overrides.yaml atomically]
  J --> K[Unlock overrides.yaml file]
  K --> L[Exit with status]
```

- The CLI operates purely on YAML documents representing a runtime override **Doc**.
- Locking is done via file locks to support concurrent CLI ops safely.
- Validation and merge logic resides in the `pkg/gpu/mockctl/config_override.go` package, which acts as a bridge library exposing core mutation and schema logic without CGo or the engine internals.
- The driver enforces strict argument validation (e.g., clamping ranges, checking modes, integer parsing) for reliable usage.

### Source Highlights

- Main entrypoint and CLI dispatch: [`cmd/nvml-mock-ctl/main.go:14-146`]()
- Config override mutation logic and validation: [`pkg/gpu/mockctl/config_override.go:18-185`]()

---

## 3. Config Override Data Model and Mutation Library

The `mockctl` package defines a `Doc` struct (mirror of the engine's `ConfigOverrideDoc`) storing:

- `Version` – schema version (default 1),
- `All` – shared override map applying to all devices,
- `Devices` – map of per-index device override maps.

### Key Types and Functions

| Type / Function     | Description                                                                                 |
|--------------------|---------------------------------------------------------------------------------------------|
| `Doc`              | Represents the config override document in-memory.                                         |
| `Target`           | Specifies which bucket the mutation applies to: the global `All` map or a device-index key.|
| `Load(path)`       | Reads and unmarshals the override YAML file, returning an empty `Doc` if missing or empty.  |
| `(*Doc).Bytes()`   | Marshals the override document back to YAML for writing.                                   |
| `(*Doc).SetFields` | Deep merges a `map[string]any` patch into the appropriate target bucket in `Doc`.           |
| `(*Doc).Fail`      | Sets or removes a `failure` override entry for the target; validates mode string.          |
| Convenience patch builders (`TemperaturePatch`, `PowerPatch`, `FanPatch`, etc.) | Construct common override patches for metric pinning with dynamic/static metrics combined.|

### Merge & Validation

The mutation methods call internal helpers to validate fields against the engine's schema types for consistency and reject unknown or type-mismatched keys. Invalid commands will fail early and not corrupt the override file.

The patch builders construct minimal but authoritative device config fragments that can be merged into the override file with full type-safety.

### Example Patch for Temperature

```go
func TemperaturePatch(celsius int) map[string]any {
	return map[string]any{
		"thermal": map[string]any{"temperature_gpu_c": celsius},
		"dynamic_metrics": map[string]any{
			"temperature": map[string]any{
				"base_c":     celsius,
				"ramp_c":     0,
				"variance_c": 0,
			},
		},
	}
}
```

This approach guarantees that the temperature reading is deterministic and overrides both static and dynamic simulator values.

---

## 4. Command Reference Summary

The CLI supports a variety of commands for runtime control, all scoped via `--gpu` to a device index, UUID, or `all`:

| Command       | Purpose                                                                              | Notes                                  |
|---------------|--------------------------------------------------------------------------------------|----------------------------------------|
| `fail`        | Inject or clear a failure mode (`healthy`, `lost`, `fallen_off_bus`, `ecc_uncorrectable`) | Supports delayed trip (`--after-calls`) and Xid injection (`--xid`). |
| `temp`/`temperature` | Pin GPU temperature in Celsius.                                                 | Overwrites dynamic and static thermal fields. |
| `power`       | Pin GPU power draw in watts.                                                         | Converts watts to milliwatts internally. |
| `fan`         | Pin fan speed in percent; forces fan count ≥ 1 for visibility.                       | Useful for liquid/passively cooled profiles. |
| `util`/`utilization` | Pin GPU and memory utilization percent; disables dynamic utilization simulator. |                                            |
| `clocks`      | Pin SM and graphics clock speeds in MHz.                                            | Memory clock is preserved from base profile. |
| `throttle`    | Set active throttle reasons (e.g., `thermal`, `sw_power_cap`); `none` clears all.      | Writes explicit boolean flags for each reason. |
| `pstate`      | Pin GPU performance state (P-state) from 0 to 15.                                   | Prepares `performance_state` string like "P8". |
| `nvlink-error`| Inject NVLink data link layer error rates (errors per second).                      | Supports selecting specific links, rate zero heals errors. |
| `set`         | Arbitrary field patching by key paths and values (e.g., `memory.used_bytes=...`).     | Deep merges; rejects unknown/invalid fields. |
| `status`      | Display active runtime overrides.                                                   | Optional `--gpu` to narrow scope.       |
| `reset`       | Clear runtime overrides for one or all GPUs.                                       | Defaults to all if no `--gpu` given.    |

For a full usage summary, see the embedded usage string parseable via `nvml-mock-ctl help`.

---

## 5. Locking and Atomicity

To handle potential concurrent invocations, the CLI locks the override file with an exclusive **POSIX lock** before reading and writing. It writes to a temporary file and then atomically renames over the original, ensuring file integrity even on errors or multiple simultaneous calls.

---

## 6. Runtime Override Lifecycle and TTL

- The TTL is a configurable interval (`MOCK_NVML_OVERRIDES_TTL`, default 1 second) at which injected consumers reread the override file and merge.
- This means the effective state changes **propagate asynchronously** but quickly.
- No active reload commands or restarts are needed for changes to take effect, making `nvml-mock-ctl` ideal for automated or live testing workflows.

---

## 7. scenario_runtime_control E2E Test Patterns

The runtime control commands and their semantics are extensively exercised by **E2E integration tests** in the `scenario_runtime_control.go` package. This validates the entire live update path end-to-end:

- Mutations are applied by exec-ing `nvml-mock-ctl` inside a running DaemonSet pod on a node.
- The effect is verified by querying the same pod's simulated GPUs directly via `nvidia-smi` commands with various queries.
- Tests confirm that overrides apply without pod restarts, hot reload as expected, and that commands produce consistent, scoped effects.

### Key Test Flow

```mermaid
flowchart TD
  UserTest[RuntimeControl E2E Test] --> ExecCtl["Exec nvml-mock-ctl inside DaemonSet pod"]
  ExecCtl --> WriteOverride["Write overrides.yaml on host mount"]
  WriteOverride --> Merge[Mock Engine detects override file change]
  Merge --> MockLibrary["Mock NVML Library merges config per device"]
  MockLibrary --> nvidiaSMI[Consumer pod queries state via nvidia-smi]
  nvidiaSMI --> Validate["Validate observed state matches expected overrides"]

  subgraph ValidationLoop
    Validate --> ExecCtl
  end
```

- Example tests include injecting ECC uncorrectable errors, pinning temperature or power, asserting throttle reasons, targeting by UUID, resetting overrides, and more.
- Each test resets the override state to isolate side effects between scenarios.

### Test Implementation Details

- The helper `nvmlMockCtl(ctx, h, args...)` runs the CLI inside the pod and asserts success.
- Queries to `nvidia-smi` are parsed and asserted against expected values.
- The tests implement timeouts and polling loops to accommodate the TTL delay in override propagation.

Source file: [`tests/e2e/go/scenario_runtime_control.go:6-3415`]() (truncated, but see full for details and helper functions)  
Sample scenario snippet from tests:

```go
func assertRuntimeECCInjection(ctx SpecContext, h *harness.Harness, consumer kube.PodRef) {
	resetRuntimeOverrides(ctx, h)
	nvmlMockCtl(ctx, h, "fail", "--gpu", "0", "--mode", "ecc_uncorrectable", "--after-calls", "1", "--xid", "79")
	Eventually(func() int {
		return smiGPUInt(ctx, h, consumer, 0, "ecc.errors.uncorrected.aggregate.total")
	}).WithTimeout(runtimeTTLTimeout).Should(BeNumerically(">", 0))
	nvmlMockCtl(ctx, h, "reset", "--gpu", "all")
	Eventually(func() int {
		return smiGPUInt(ctx, h, consumer, 0, "ecc.errors.uncorrected.aggregate.total")
	}).WithTimeout(runtimeTTLTimeout).Should(Equal(0))
}
```

---

## 8. Summary Diagram: Runtime Control System Mapping

```mermaid
graph TD
  subgraph NaturalLanguage[Runtime Control System]
    SMCLI["nvml-mock-ctl CLI"]
    OverrideFile["overrides.yaml config override file"]
    ConsumerPods["Running Consumer Pods"]
    NVMLLib["nvml-mock injected library (libnvidia-ml.so)"]
    SmiQuery["nvidia-smi"]
  end

  subgraph CodeEntities["Relevant Code Entities"]
    MainGo["cmd/nvml-mock-ctl/main.go"]
    MockCtlLib["pkg/gpu/mockctl/config_override.go"]
    Engine["pkg/gpu/mocknvml/engine/ (merging, schema)"]
    RuntimeTest["tests/e2e/go/scenario_runtime_control.go"]
  end

  SMCLI -->|writes| OverrideFile
  OverrideFile -->|merged periodically TTL| NVMLLib
  ConsumerPods -->|run| NVMLLib
  ConsumerPods -->|run queries| SmiQuery
  
  SMCLI -. implemented in .-> MainGo
  MainGo -. uses .-> MockCtlLib
  MockCtlLib -. reuses schema/types .-> Engine
  RuntimeTest -. invokes .-> SMCLI
  RuntimeTest -. asserts via .-> SmiQuery
```

---

## 9. Source References

- `nvml-mock-ctl` main CLI driver and command dispatch: [`cmd/nvml-mock-ctl/main.go:14-146`]()
- CLI testing code validating commands and argument handling: [`cmd/nvml-mock-ctl/main_test.go:14-154`]()
- Config override pure mutation library: [`pkg/gpu/mockctl/config_override.go:18-185`]()
- Config override tests covering patch validation: [`pkg/gpu/mockctl/config_override_test.go:14-170`]()
- CLI user-facing usage and prose documentation: [`docs/nvml-mock-ctl.md:1-175`]()
- E2E test scenarios exercising runtime overrides: [`tests/e2e/go/scenario_runtime_control.go:6-3415`]() (truncated for brevity)

---

This page completes the detailed technical reference of runtime GPU simulation control via the `nvml-mock-ctl` tool — the cornerstone for flexible, dynamic test and failure injection scenarios in the `k8s-test-infra` GPU testing infrastructure.

---

# Page: E2E Test Scenarios

# E2E Test Scenarios

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/nvml-mock-e2e-go.yaml](.github/workflows/nvml-mock-e2e-go.yaml)
- [Makefile](Makefile)
- [README.md](README.md)
- [tests/e2e/README.md](tests/e2e/README.md)
- [tests/e2e/VERSION-MATRIX.md](tests/e2e/VERSION-MATRIX.md)
- [tests/e2e/go/assertions/resources.go](tests/e2e/go/assertions/resources.go)
- [tests/e2e/go/e2e_suite_test.go](tests/e2e/go/e2e_suite_test.go)
- [tests/e2e/go/framework/config/config.go](tests/e2e/go/framework/config/config.go)
- [tests/e2e/go/framework/harness/harness.go](tests/e2e/go/framework/harness/harness.go)
- [tests/e2e/go/framework/helm/helm.go](tests/e2e/go/framework/helm/helm.go)
- [tests/e2e/go/framework/helm/helm_test.go](tests/e2e/go/framework/helm/helm_test.go)
- [tests/e2e/go/framework/kube/kube.go](tests/e2e/go/framework/kube/kube.go)
- [tests/e2e/go/suite_cluster.go](tests/e2e/go/suite_cluster.go)
- [tests/e2e/go/suite_helm.go](tests/e2e/go/suite_helm.go)

</details>



This page provides a high-level overview of the end-to-end (E2E) test scenarios in the k8s-test-infra repository, focusing on the integration testing of NVIDIA GPU simulation components using the nvml-mock system. It introduces the key subsystems involved in E2E tests: the test harness framework that orchestrates cluster lifecycle and test execution, the various scenario categories validating different integrations, and the continuous integration (CI) image distribution strategy enabling fast and repeatable test runs.

The page serves as a parent overview linking to detailed child pages that document each aspect more thoroughly.

---

## Purpose and Scope

The E2E testing suite validates the full software stack for GPU simulation on Kubernetes, employing the `nvml-mock` library to simulate GPUs in a Kind cluster environment without requiring physical NVIDIA hardware. These tests cover:

- Standalone testing of the nvml-mock Helm chart and GPU profile simulation.
- Dynamic Resource Allocation (DRA) API integration.
- GPU Operator integration.
- Node-wide NVIDIA Runtime Interface (NRI) injection.
- Node Feature Discovery (NFD) label provenance.
- Multi-node heterogeneous cluster topologies.

The tests run through a Go/Ginkgo harness that manages the entire lifecycle of cluster creation, Helm deployments, and validations. The CI system builds and distributes container images efficiently for parallel test execution.

This page outlines the E2E test ecosystem and links to deeper documentation on the harness, scenarios, and CI workflows.

---

## 1. E2E Harness Framework Overview

The core of the E2E tests is the harness framework (`harness.Harness` struct), which encapsulates three main adapters tightly coupled to a single Kind cluster instance:

- **Cluster**: Manages the lifecycle of the Kind cluster (create, delete, load images).
- **Kube Client**: Provides Kubernetes API interactions implemented as a wrapper over `kubectl` commands, enabling strongly typed object access and command execution.
- **Helm Client**: Wraps the `helm` CLI for chart deployment and upgrade with wait and timeout controls.

The harness owns the cluster lifecycle unless running in "AttachExisting" mode, where it attaches to an externally provisioned cluster (e.g., managed through Tilt).

Key features include:

- Reading cluster profiles from `config.SelectedProfileNames()` to determine GPU simulation topologies.
- Running Helm `upgrade --install` to deploy the `nvml-mock` Helm chart repeatedly for different GPU profiles on the same cluster (avoiding cluster rebuilds).
- Collecting detailed diagnostics on test failure using a "collectOnFailure" pattern.
- Handling environment-controlled behaviors like skipping image builds when a pre-built image is provided.

For detailed architecture and API, see [E2E Harness Framework](#10.1).

```mermaid
flowchart TD
  subgraph Harness Framework
    H[harness.Harness]
    C[cluster.Cluster]
    K[kube.Client]
    Hl[helm.Client]
  end

  H --> C
  H --> K
  H --> Hl

  subgraph Config
    P[config.SelectedProfileNames()]
  end

  H --> P
```

Sources:  
- `tests/e2e/go/framework/harness/harness.go:21-99`  
- `tests/e2e/go/framework/config/config.go:13-136`  
- `tests/e2e/go/suite_cluster.go:6-78`  
- `tests/e2e/README.md:6-136`  

---

## 2. Test Scenarios Overview

The E2E tests are organized into distinct scenario categories, each validating specific functional integrations or features:

| Scenario               | Purpose/Validation Highlights                                                                                                              | Profiles                                                                                     |
|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|
| **Standalone Demo**     | Validates `nvml-mock` Helm chart installation, GPU files, `nvidia-smi` output, NVLink topology, InfiniBand devices, PCI sysfs layout, and cross-node communication. | Configurable profiles, defaulting to `gb200` locally, broader sets in CI (`a100`, `h100`, etc.) |
| **Failure Injection**   | Tests GPU states such as ECC errors, lost device, and fallen-off-bus conditions to verify failure handling and rollback.                 | Same profiles as Standalone                                                                  |
| **Dynamic Resource Allocation (DRA)** | Validates mock GPU driver files, ResourceSlices, ResourceClaim scheduling, and DRA driver readiness.                                  | Same profiles as Standalone                                                                  |
| **GPU Operator**        | Tests GPU Operator installation, validator pod startup, GPU Feature Discovery labels, and allocatable GPU resources reported by device plugin. | Same profiles as Standalone                                                                  |
| **Node-Wide NRI Injection** | Confirms ambient injection of mock GPUs into pods without explicit GPU requests or hostPath mounts.                                    | Same profiles as Standalone                                                                  |
| **Node Feature Discovery (NFD) Label Provenance** | Checks that NFD correctly derives PCI vendor node labels from feature files written by `nvml-mock`, ensuring proper label ownership. | Pinned to `a100` profile (vendor consistent)                                                |
| **Multi-Node Fleet**    | Validates heterogeneous A100/T4 multi-node Kind topology, InfiniBand behavior, device plugin resources, and GPU workload scheduling.    | Fixed multi-node cluster topology                                                            |

Each scenario resides in its own Go test file under `tests/e2e/go/` named `scenario_*.go`. The Makefile exposes dedicated targets for each scenario, enabling independent test execution and CI matrix orchestration.

Example commands:
```bash
make e2e                        # default local test with profile gb200
make e2e E2E_PROFILES=a100      # test single explicit profile
make e2e-dra                   # test the DRA scenario
make e2e-gpu-operator          # test the GPU Operator scenario
make e2e-multi-node            # test the multi-node scenario
make e2e-nri                   # test node-wide NRI injection
make e2e-nfd                   # test NFD label provenance
```

For extensive test behavior (including Helm release patterns, validation assertions, and scenario orchestration), see [Test Scenarios](#10.2).

```mermaid
flowchart LR
  subgraph Scenarios
    STAND[Standalone Demo]
    FAIL[Failure Injection]
    DRA[Dynamic Resource Allocation (DRA)]
    GPUOP[GPU Operator]
    NRI[Node-Wide NRI Injection]
    NFD[Node Feature Discovery (NFD) Label Provenance]
    MULTI[Multi-Node Fleet]
  end

  STAND --> "Makefile e2e target"
  FAIL --> "Makefile e2e target"
  DRA --> "Makefile e2e-dra"
  GPUOP --> "Makefile e2e-gpu-operator"
  NRI --> "Makefile e2e-nri"
  NFD --> "Makefile e2e-nfd"
  MULTI --> "Makefile e2e-multi-node"

  "Makefile e2e target" --> Harness[Harness Framework]
```

Sources:  
- `tests/e2e/README.md:6-163`  
- `Makefile:141-160`  
- `README.md:48-74`  

---

## 3. CI Image Distribution Strategy

The E2E test CI workflow optimizes build and image distribution for scalable, parallel test execution:

- A single job builds the `nvml-mock` container image once per commit and pushes it to the ephemeral `ttl.sh` registry (a registry with 24-hour TTL and anonymous access), e.g., `ttl.sh/nvml-mock-<sha>:24h`.
- Each parallel test job (one per GPU profile) pulls the image by digest (pinning to immutable content), then retags it locally and loads it into Kind nodes to avoid rebuilding.
- Similar pattern used for the custom Kind node image (including NVIDIA container toolkit) for the standalone scenario.
- The CI matrix triggers runs with different GPU profiles as job parameters, reducing redundant image build costs and speeding up test turnaround.
- The Go harness (`nvml-mock-e2e-go`) integrates seamlessly with this strategy via environment variables (`E2E_IMAGE`, `E2E_SKIP_BUILD`, etc.) to either build or consume the prebuilt images.

This approach also works transparently on fork pull requests, as `ttl.sh` requires no authentication.

For implementation details on the ephemeral registry usage, digest pinning, matrix job design, and Go workflow integration, see [CI Image Distribution Strategy](#10.3).

```mermaid
flowchart TD
  BuildJob["build-nvmlmock-image job"]
  PushTTL["Push to ttl.sh (ephemeral registry)"]
  Digest[ImageDigest]

  ParallelJobs["Parallel E2E Test Jobs (per GPU profile)"]
  PullDigest["Pull image by digest from ttl.sh"]
  Retag["Retag locally to E2E_IMAGE name"]
  KindLoad["Kind Load into cluster nodes"]
  HarnessRun["Harness E2E run using E2E_IMAGE"]

  BuildJob --> PushTTL --> Digest
  ParallelJobs --> PullDigest --> Retag --> KindLoad --> HarnessRun
```

Sources:  
- `.github/workflows/nvml-mock-e2e-go.yaml:15-161`  
- `README.md:48-74`  

---

## Summary

The E2E testing layer in k8s-test-infra implements comprehensive integration tests for GPU simulation workloads on Kubernetes, efficiently managed via a Go-based harness that controls cluster lifecycle and Helm deployments. The scenarios cover a wide range of real-world usage patterns and third-party component integrations, all executed on ephemeral Kind clusters and powered by container images distributed through a fast, ephemeral registry system.

Each of the three core pillars—Harness Framework, Test Scenarios, and CI Image Distribution—has dedicated documentation as child pages linked below:

- [E2E Harness Framework](#10.1) — Harness struct, lifecycle management, clients, profiling, and diagnostics.  
- [Test Scenarios](#10.2) — Details of standalone, DRA, GPU Operator, NRI, NFD scenarios; Makefile targets and GPU profiles used in CI.  
- [CI Image Distribution Strategy](#10.3) — Ephemeral registry usage, digest pinning, matrix job structures, and Go harness integration.

Refer to those pages for technical depth and code-level explanations.

---

# Related Pages

- **[E2E Harness Framework](#10.1)**
- **[Test Scenarios](#10.2)**
- **[CI Image Distribution Strategy](#10.3)**

---

# Sources

- `README.md:18-74`  
- `.github/workflows/nvml-mock-e2e-go.yaml:15-161`  
- `Makefile:141-160`  
- `tests/e2e/README.md:6-163`  
- `tests/e2e/go/framework/harness/harness.go:21-99`  
- `tests/e2e/go/framework/config/config.go:13-136`  
- `tests/e2e/go/suite_cluster.go:6-78`  
- `tests/e2e/go/framework/helm/helm.go:18-130`  
- `tests/e2e/go/framework/kube/kube.go:6-229`

---

# Page: E2E Harness Framework

# 10.1 E2E Harness Framework

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/nvml-mock-e2e-go.yaml](.github/workflows/nvml-mock-e2e-go.yaml)
- [Makefile](Makefile)
- [README.md](README.md)
- [pkg/diagnostics/collector.go](pkg/diagnostics/collector.go)
- [pkg/diagnostics/extensions.go](pkg/diagnostics/extensions.go)
- [pkg/diagnostics/kubernetes.go](pkg/diagnostics/kubernetes.go)
- [pkg/diagnostics/options.go](pkg/diagnostics/options.go)
- [pkg/kubernetes/kubernetes.go](pkg/kubernetes/kubernetes.go)
- [tests/e2e/README.md](tests/e2e/README.md)
- [tests/e2e/VERSION-MATRIX.md](tests/e2e/VERSION-MATRIX.md)
- [tests/e2e/go/assertions/resources.go](tests/e2e/go/assertions/resources.go)
- [tests/e2e/go/e2e_suite_test.go](tests/e2e/go/e2e_suite_test.go)
- [tests/e2e/go/framework/config/config.go](tests/e2e/go/framework/config/config.go)
- [tests/e2e/go/framework/harness/harness.go](tests/e2e/go/framework/harness/harness.go)
- [tests/e2e/go/framework/helm/helm.go](tests/e2e/go/framework/helm/helm.go)
- [tests/e2e/go/framework/helm/helm_test.go](tests/e2e/go/framework/helm/helm_test.go)
- [tests/e2e/go/framework/kube/kube.go](tests/e2e/go/framework/kube/kube.go)
- [tests/e2e/go/suite_cluster.go](tests/e2e/go/suite_cluster.go)
- [tests/e2e/go/suite_helm.go](tests/e2e/go/suite_helm.go)

</details>



## Purpose and Scope

This page provides an in-depth technical overview of the E2E Harness Framework implemented in the `k8s-test-infra` repository under `tests/e2e/go/framework/harness`. The framework orchestrates the lifecycle of Kubernetes clusters (using Kind), Helm deployments of the `nvml-mock` chart, and Kubernetes client interactions needed for the end-to-end (E2E) tests of the mock GPU infrastructure system. Key components include the `harness.Harness` struct, cluster lifecycle management, Helm and Kube client abstractions, profile selection, AttachExisting mode for attaching to already running clusters, and diagnostic collection on failure.

---

## 1. The `harness.Harness` Struct

At the core of the E2E harness is the `Harness` struct, which composes a tightly integrated set of adapters bound to a single isolated Kind cluster. This struct owns the cluster lifecycle and serves as the orchestrator for test actions targeting the mock GPU environment.

```go
type Harness struct {
	Cluster *cluster.Cluster
	Kube    *kube.Client
	Helm    *helm.Client
	Image   string
}
```

- **Cluster**: Manages the Kind cluster lifecycle including creation, deletion, and image loading.
- **Kube**: A Kubernetes client wrapper tailored for test assertions and interactions, built on top of `kubectl` calls.
- **Helm**: A Helm client abstraction for managing Helm releases within the cluster.
- **Image**: The Docker image reference for the `nvml-mock` mock GPU deployment.

The `Harness` struct is defined in `tests/e2e/go/framework/harness/harness.go` at lines 22-27 and further manipulated via setup and teardown methods.

---

## 2. Cluster Lifecycle Management with Kind

### Creating and Deleting Clusters

The harness manages a Kind cluster per test suite, with lifecycle functions to create, load images into, and eventually delete the cluster.

- Cluster creation is done via the `cluster.Create` wrapper, which reads a Kind configuration YAML and creates a cluster with a specified name, deleting any previous clusters with the same name.
- Image loading is handled via `cluster.LoadImage` to place the prebuilt `nvml-mock` Docker image into the Kind nodes for use by workloads.

### Setup and Teardown

The `Setup` function in `harness.go`:

- Creates the Kind cluster.
- Attaches Kubernetes and Helm client adapters to the cluster context.
- Loads the Docker image into the Kind nodes.

On error, it returns the partial `Harness` instance for possible deferred cleanup.

The `Teardown` function deletes the cluster unless the `keep` flag is set, facilitating efficient debugging in development setups.

```go
func Setup(ctx context.Context, name string, kindConfig []byte, image string) (*Harness, error) { ... }
func (h *Harness) Teardown(ctx context.Context, keep bool) error { ... }
```

See code at lines 33-53 and 90-98 in `harness.go`.

---

## 3. Helm Client Integration

The Helm client is an adapter wrapping CLI calls to Helm, scoped to the cluster's Kubernetes context.

### Helm Client (`helm.Client`)

- Created for a specific kubecontext to target the correct Kind cluster.
- Supports `Install` and `UpgradeInstall` operations with standard Helm flags, namespace management, and value setting.

### Release Abstraction

The `helm.Release` struct models a Helm release to install or upgrade the `nvml-mock` chart.

- Supports configuration via `Set` map for Helm `--set` overrides.
- Supports namespace creation, wait flags, timeouts, hiding output for cleaner logs.

### Chart Deployment in E2E

The harness installs or upgrades the `nvml-mock` Helm release per GPU profile via:

- `installDemoChart(ctx, harness, profileName, gpuCount)`: installs or upgrades the release with specific values such as `gpu.count`, GPU profile, image repository/tag, and dynamic metrics flags.

When `AttachExisting` mode is enabled (see below), Helm upgrades are skipped because the external orchestrator owns the rollout.

This integration is implemented in `tests/e2e/go/suite_helm.go` at lines 36-46 and utilizes the Helm adapter defined in `tests/e2e/go/framework/helm/helm.go` lines 20-129.

---

## 4. Kubernetes Client Abstraction (`kube.Client`)

The Kubernetes client adapter wraps `kubectl` commands and unmarshals JSON output into Go structs typed for assertions.

### Features

- Clients are constructed per kubecontext to isolate calls.
- Supports querying nodes, pods, DaemonSets, ConfigMaps, and Jobs, with strongly typed JSON decoding.
- Provides convenience methods for common queries like:
  - `FirstNodeName`
  - `NodeLabel`
  - `AllocatableGPU`
  - `PodPhase`
  - `PodIP`
- Supports command execution, resource application, and pod exec.

This approach deliberately avoids introducing `client-go` dependencies, reducing vendor size and complexity.

Refer to `tests/e2e/go/framework/kube/kube.go` lines 36-229 for full implementation.

---

## 5. Profile Management with `config.SelectedProfileNames()`

Profiles define which GPU topologies/configurations are tested. The harness framework uses the `config` package to determine the active profile set:

- Profiles are read from the environment variable `E2E_PROFILES`, supporting comma/space-separated lists.
- Default profile is `gb200` for local runs.
- CI workflows opt-in to a wider profile matrix like `a100, h100, b200, gb200, gb300, t4`.
- Profiles directly correspond to Helm chart profiles located under `deployments/nvml-mock/helm/nvml-mock/profiles`.

The harness iterates over profiles to upgrade Helm deployments and run profile-specific test assertions.

Implementations in `tests/e2e/go/framework/config/config.go` lines 60-78.

---

## 6. `AttachExisting` Mode

To support workflows where cluster provisioning and rollout are performed externally (e.g., via Tilt or CI automation), the harness supports an attach-only mode:

- When `AttachExisting()` returns `true` (environment variable `E2E_ATTACH_EXISTING` set), the harness skips cluster creation, image loading, and Helm installation.
- Instead, `AttachExisting()` calls `harness.AttachExisting()` to bind Kubernetes and Helm clients to an existing cluster and context.
- This is critical for CI job isolation where cluster lifecycles are managed by separate steps but tests still want to run with the full suite of assertions.
- Helm upgrades in this mode become no-ops to avoid clashing with the external rollout agent, as seen in `installDemoChart` checking `config.AttachExisting()` (suite_helm.go lines 36-46).

The attach logic is in `harness.go` lines 55-76.

---

## 7. Diagnostics Collection with `collectOnFailure`

The harness includes a mechanism to collect diagnostic data on test failures automatically, preserving logs, resource dumps, and relevant states for post-mortem analysis.

- During cluster setup, a deferred cleanup callback registers a diagnostic collector.
- `collectOnFailure` inspects the current Ginkgo spec report.
- If the spec failed, it triggers the collection of diagnostics under a dedicated artifacts directory defined by configuration (default `artifacts/e2e/go`).
- This diagnostic collector interacts directly with Kubernetes resources to gather logs and cluster info.
- The mechanism mirrors the demo/bash "collect logs on failure" manual blocks but is fully automated in Go.

Implementation is in `suite_cluster.go` lines 44-51.

---

## 8. Data Flow and Control Flow Summary

Below is an overview of the main data and control flows linking the key components in the E2E framework.

```mermaid
flowchart TD
  subgraph NaturalLanguage_Space [Natural Language / Concepts]
    A[GPU Profile Selection]
    B[Cluster Lifecycle Management]
    C[Helm nvml-mock Deployment]
    D[Kubernetes API Interactions]
    E[Attach to Existing Cluster]
    F[Diagnostics on Test Failures]
  end

  subgraph Code_Entity_Space [Code Entities and Functions]
    H1[harness.Harness struct]
    H2[harness.Setup(ctx, name, kindConfig, image)]
    H3[harness.AttachExisting(ctx, name, kubeContext, image)]
    H4[harness.Teardown(ctx, keep)]
    K1[kube.Client]
    K2[kube.New(context)]
    HLM1[helm.Client]
    HLM2[helm.New(context)]
    HLM3[installDemoChart(ctx, h, profile, count)]
    CFG1[config.SelectedProfileNames()]
    CFG2[config.AttachExisting()]
    DIAG1[collectOnFailure(ctx, h, sub...)]
  end

  A -->|Determines| CFG1
  CFG1 -->|Provides profiles to| HLM3
  B -->|Create Cluster| H2
  B -->|Delete Cluster| H4
  HLM3 -->|Perform Helm UpgradeInstall| HLM1
  D -->|kubectl operations| K1
  H1 -->|Holds| H2
  H1 -->|Holds| H3
  H1 -->|Holds| H4
  H1 -->|Contains| K1
  H1 -->|Contains| HLM1
  CFG2 -->|Attach mode triggers| H3
  CFG2 -->|Skip create/load/install| HLM3
  H4 -->|Triggered on suite end| DIAG1
  DIAG1 -->|Collect logs| D
```

---

## 9. Summary Table of Key Files and Responsibilities

| File Path                               | Key Responsibilities                                      |
|---------------------------------------|-----------------------------------------------------------|
| `framework/harness/harness.go`        | Defines `Harness` struct; cluster setup, attach, teardown |
| `framework/cluster/cluster.go`        | Low-level Kind cluster creation, deletion, image loading  |
| `framework/helm/helm.go`               | Helm client adapter for installs, upgrades                |
| `framework/suite_helm.go`              | Helm upgrade/install logic for `nvml-mock` deployment     |
| `framework/kube/kube.go`               | Kubernetes client wrapping kubectl commands                |
| `framework/config/config.go`           | Harness configuration: profiles, flags, attach mode       |
| `framework/suite_cluster.go`           | Cluster setup and teardown logic; diagnostics on failure  |
| `tests/e2e/go/e2e_suite_test.go`      | Ginkgo test suite setup including build image synchronization |

---

## 10. Detailed Lifecycle Execution Sequence (Mermaid Sequence Diagram)

```mermaid
sequenceDiagram
    participant Runner as Test Runner (Ginkgo)
    participant Harness as harness.Harness
    participant Cluster as Kind Cluster
    participant Helm as Helm Client
    participant Kube as Kube Client
    participant Config as Config Package

    Note over Runner,Harness: Test suite start

    Runner->>Config: Read E2E_PROFILES, E2E_ATTACH_EXISTING env vars
    Config-->>Runner: Provide profile list and attachExisting bool
    
    alt AttachExisting = false
        Runner->>Harness: Setup(ctx, name, kindConfig, image)
        Harness->>Cluster: Create cluster
        Cluster-->>Harness: Cluster created
        Harness->>Kube: Create kube.Client for cluster context
        Harness->>Helm: Create helm.Client for cluster context
        Harness->>Cluster: Load mock GPU image into Kind nodes
        Harness-->>Runner: Harness ready
    else AttachExisting = true
        Runner->>Harness: AttachExisting(ctx, clusterName, kubeContext, image)
        Harness->>Kube: Create kube.Client for existing context
        Harness->>Helm: Create helm.Client for existing context
        Harness-->>Runner: Harness ready (attached)
    end

    loop For each profile in profiles
        Runner->>Helm: installDemoChart(ctx, Harness, profile, gpuCount)
        Helm->>Cluster: Deploy Helm nvml-mock chart with profile settings
        Cluster-->>Helm: Deploy confirmed
        Runner->>Kube: Run assertions on NVML mock GPU state for profile
    end

    par On any failure
        Runner->>Harness: collectOnFailure(ctx, Harness, specifics)
        Harness->>Kube: Gather diagnostic logs, resource dumps
        Kube-->>Harness: Diagnostics collected
        Harness-->>Runner: Diagnostics saved
    end

    Runner->>Harness: Teardown(ctx, keepClusterFlag)
    alt keepClusterFlag = false
        Harness->>Cluster: Delete cluster
    else
        Harness: Leaves cluster running
    end
```

---

## 11. Summary

The E2E Harness Framework in `k8s-test-infra` enables reliable automated testing of the `nvml-mock` GPU simulation system on Kubernetes by:

- Managing ephemeral Kind clusters with preloaded mock images.
- Coordinating Helm chart installs/upgrades for multiple GPU profiles without cluster rebuilds.
- Providing a Kubernetes client abstraction optimized for assertions.
- Controlling configuration via environment variables with defaults, including support for attaching to externally managed clusters.
- Automatically capturing detailed diagnostics on test failures to facilitate rapid investigation.

The framework abstracts away complex lifecycle orchestration and Kubernetes/Helm operations, allowing test scenarios to focus exclusively on GPU simulation validation.

---

## References

- `tests/e2e/go/framework/harness/harness.go:22-98` — Harness struct and lifecycle functions.
- `tests/e2e/go/framework/cluster/cluster.go` (implied) — Kind cluster management.
- `tests/e2e/go/framework/helm/helm.go:20-129` — Helm client wrapper.
- `tests/e2e/go/suite_helm.go:36-46` — Helm integration for demo chart deployment.
- `tests/e2e/go/framework/kube/kube.go:36-229` — Kubernetes client wrapper.
- `tests/e2e/go/framework/config/config.go:60-78` — Profile selection and AttachExisting flag.
- `tests/e2e/go/suite_cluster.go:44-77` — Cluster setup attachment, collectOnFailure diagnostics.
- `tests/e2e/go/e2e_suite_test.go:30-62` — Test suite orchestration and image build sharing.

---

This completes the documentation of the E2E Harness Framework.

---

# Page: Test Scenarios

# 10.2 Test Scenarios

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cmd/nvml-mock-ctl/main.go](cmd/nvml-mock-ctl/main.go)
- [cmd/nvml-mock-ctl/main_test.go](cmd/nvml-mock-ctl/main_test.go)
- [docs/nvml-mock-ctl.md](docs/nvml-mock-ctl.md)
- [pkg/gpu/mockctl/config_override.go](pkg/gpu/mockctl/config_override.go)
- [pkg/gpu/mockctl/config_override_test.go](pkg/gpu/mockctl/config_override_test.go)
- [pkg/gpu/mocknvml/engine/gpm.go](pkg/gpu/mocknvml/engine/gpm.go)
- [tests/e2e/gfd-mock.yaml](tests/e2e/gfd-mock.yaml)
- [tests/e2e/go/assertions/dcgm.go](tests/e2e/go/assertions/dcgm.go)
- [tests/e2e/go/scenario_gpu_operator_test.go](tests/e2e/go/scenario_gpu_operator_test.go)
- [tests/e2e/go/scenario_nfd_test.go](tests/e2e/go/scenario_nfd_test.go)
- [tests/e2e/go/scenario_runtime_control.go](tests/e2e/go/scenario_runtime_control.go)
- [tests/e2e/go/scenario_standalone_test.go](tests/e2e/go/scenario_standalone_test.go)
- [tests/e2e/gpu-operator-values.yaml](tests/e2e/gpu-operator-values.yaml)
- [tests/e2e/kind-gpu-operator-config.yaml](tests/e2e/kind-gpu-operator-config.yaml)
- [tests/e2e/validate-iblinkinfo.sh](tests/e2e/validate-iblinkinfo.sh)
- [tests/e2e/validate-ibnetdiscover.sh](tests/e2e/validate-ibnetdiscover.sh)
- [tests/e2e/validate-ibv-devinfo.sh](tests/e2e/validate-ibv-devinfo.sh)
- [tests/e2e/validate-nvidia-smi.sh](tests/e2e/validate-nvidia-smi.sh)
- [tests/e2e/validator-mock.yaml](tests/e2e/validator-mock.yaml)

</details>



This section documents the end-to-end (E2E) test scenarios implemented in the `k8s-test-infra` repository. These scenarios exercise the standalone standalone nvml-mock DaemonSet, Dynamic Resource Allocation (DRA), GPU Operator integration, Node Resource Interface (NRI) plugin, Node Feature Discovery (NFD), and multi-node GPU fabric simulations. It covers the test implementations, their organization under Ginkgo, key test logic and assertions, their Makefile targets, and details the GPU profile matrix used in Continuous Integration (CI).

---

## Purpose and Scope

The E2E test scenarios validate the integration and functionality of various GPU simulation and orchestration subsystems on Kubernetes clusters managed in the `k8s-test-infra` project. They cover:

- The standalone nvml-mock GPU simulation validating device appearance, driver files, topology, and dynamic runtime controls.
- DRA mode testing resource slices and driver integration.
- GPU Operator compatibility validating operator installation over the mock driver.
- NRI plugin injection and opt-out behaviors.
- NFD scenarios proving GPU feature label provenance and node labelling.
- Multi-node tests validating the ComputeDomain NVLink and InfiniBand fabric simulation cross-node communication.

Each scenario runs on a Kubernetes Kind cluster configured per test with Helm charts and uses Ginkgo test containers to structure parallel and ordered test execution. Runtime control tests utilize the `nvml-mock-ctl` CLI to mutate GPU states live.

---

## 1. Standalone Scenario

### Overview

This scenario exercises the basic standalone nvml-mock DaemonSet using multiple GPU profiles in a single Kind cluster. The cluster is installed once for all selected GPU profiles (default profile "gb200"). Each profile triggers a Helm upgrade reinstalling the nvml-mock chart with that specific GPU profile for the simulated devices. Tests validate:

- Node labelling with `nvidia.com/gpu.present=true`.
- The rendering of the fake GPU Operator profile ConfigMaps.
- Layout of device plugin mock driver files.
- `nvidia-smi` queries reporting simulated devices and their metrics.
- NVLink topology exposure gated behind FabricManager readiness.
- InfiniBand mock interface (`ibstatus`, `ibv_devinfo`) validation.
- PCI Sysfs topology existence.
- Cross-node InfiniBand ping (`ibping`) and link info scan (`iblinkinfo`).
- Runtime failure injection and metric pinning via `nvml-mock-ctl`.

### Implementation Details

The Go scenario is implemented in `tests/e2e/go/scenario_standalone_test.go` within a Ginkgo `Describe("nvml-mock standalone")` container [tests/e2e/go/scenario_standalone_test.go:37-177](). Setup happens once in `BeforeAll` with:

- `setupCluster()` which creates the Kind cluster with a demo Kind config for selected GPU profiles.
- `demoKindConfig()` generates Kind cluster configuration controlled by profile names.
- Profile-specific Helm `upgrade --install` calls for reconfiguration per profile.

Key verification tests use "Labels", "fgo" (fake GPU operator), "mockfiles", "nvidia-smi", "nvlink", "ib", "pcisysfs", and "ibping" labels to organize and parallelize them.

The runtime control tests (labelled "runtime-control") use helper assertions that directly call `nvml-mock-ctl` commands via `Exec()` into the daemon pod and check effects through `nvidia-smi` queries. These include:

- Inject ECC errors, mark GPUs lost, pin temperatures, power, fan speeds, and more.
- Targeting by GPU index or UUID.
- Resetting overrides.

### Key Functions / Classes

- `setupCluster(ctx, clusterName, kindConfig, testPrefix)` manages cluster lifecycle and Helm deploys the nvml-mock chart.
- Assertions like `assertions.NvidiaSMI()`, `assertions.DevicePluginMockFiles()`, `assertions.NVLink()`, and `assertions.IBPing()` perform domain-specific checks.
- Runtime control helpers such as `nvmlMockCtl()` and `assertRuntimeECCInjection()` interact with `nvml-mock-ctl` [tests/e2e/go/scenario_standalone_test.go:37-177, tests/e2e/go/scenario_runtime_control.go:46-173]().

### Makefile Target

- `make e2e` runs this standalone scenario along with other basic tests.

---

## 2. Dynamic Resource Allocation (DRA) Scenario

### Overview

The DRA scenario validates the Dynamic Resource Allocation driver integration with the nvml-mock system's simulated GPU resources. It tests resource slices, claims, and device-class functionality through DRA CRDs.

### Implementation Details

The primary test suite uses the `e2e-dra` Makefile target. It instantiates a Kind cluster with demo configs that enable DRA, installs DRA Helm charts, and runs tests that verify:

- ResourceSlice and ResourceClaim creation and lifecycle.
- DeviceClass object interaction.
- GPU resource publish and consume workflows.

Assertions verify resource presence and correctness via the Kubernetes API and device plugin reports.

---

## 3. GPU Operator Scenario

### Overview

Tests the compatibility of the GPU Operator Helm chart when deployed on top of the mock NVML environment.

### Implementation Details

A Kind cluster installs the nvml-mock chart, then overlays the GPU Operator Helm chart set with the mock driver disabled and configured via a values overlay file `tests/e2e/gpu-operator-values.yaml`:

- Driver disabled to ensure mock NVML simulates.
- Toolkit disabled; mock libs placed by DaemonSet.
- DRA driver standalone chart.
- DCGM exporter enabled for metric checks.
- MIG disabled since mock NVML doesn't support it.

The test verifies operator pod launches, device plugin discovery, GFD node labelling, and validator checks for readiness.

---

## 4. Node Resource Interface (NRI) Scenario

### Overview

Validates the nvml-mock-nri containerd plugin behavior for node-wide injection and opt-out annotation.

### Implementation Details

The scenario tests:

- The injection of the mock NVML libs and devices via NRI plugin.
- The opt-out annotation on pods to disable injection.
- Correct device visibility inside containers.
- Liveness and readiness probes of the NRI plugin.

---

## 5. Node Feature Discovery (NFD) Scenario

### Overview

Proves that the PCI vendor label `feature.node.kubernetes.io/pci-10de.present` is correctly derived from NFD's local source reading the mock feature files written by nvml-mock.

### Implementation Details

- Uses Helm to install the NFD chart and add its repository.
- Validates that before NFD deployment, the PCI vendor label is absent on nodes.
- Confirms that the feature file `/host/etc/kubernetes/node-feature-discovery/features.d/nvml-mock.features` contains the expected `pci-10de.present=true` line.
- After installing NFD, waits for the node label presence and verifies label ownership via the NFD annotation.

---

## 6. Multi-node Scenario

### Overview

Validates the ComputeDomain multi-node NVLink and InfiniBand fabric simulation across multiple Kind nodes.

### Implementation Details

- Sets up a multi-node cluster with the mock fabric enabled.
- Runs cross-node InfiniBand tests using `ibping` and `iblinkinfo` validated by helper shell scripts (`validate-ibping.sh`, `validate-iblinkinfo.sh`, `validate-ibnetdiscover.sh`).
- Tests ensure cross-node fabric discovery and communication are functional.
- Validates that certain profiles (e.g. `l40s` and `t4`) disable IB and skip IB tests.

---

## GPU Profile Matrix in CI

The CI environment runs E2E tests with a matrix of GPU profiles simulating various NVIDIA GPU models, including but not limited to:

- `a100`
- `h100`
- `b200`
- `gb200`
- `gb300`
- `l40s`
- `t4`

These profiles represent different hardware configurations and influence test coverage of topology, metrics, and failure modes.

---

## Makefile Targets Overview

| Makefile Target | Scenario / Description                                    |
|-----------------|----------------------------------------------------------|
| `e2e`           | Run standalone scenario on default GPU profiles          |
| `e2e-dra`       | Run tests with Dynamic Resource Allocation enabled        |
| `e2e-gpu-operator` | Run GPU Operator compatibility tests                     |
| `e2e-nri`       | Run Node Resource Interface plugin tests                   |
| `e2e-nfd`       | Run Node Feature Discovery related label provenance tests  |
| `e2e-multi-node`| Run multi-node ComputeDomain fabric simulation tests       |

---

## Data Flow and Architecture in E2E Scenarios

The E2E test architecture typically follows this flow:

1. **Cluster Setup**: Create a Kubernetes Kind cluster with appropriate config overlays including number of nodes, GPU profiles, feature flags (DRA, NRI, etc).
2. **Helm Chart Installation**: Deploy the `nvml-mock` DaemonSet Helm chart to provide the mock libraries, device simulation, and driver files in each node.
3. **Scenario-specific Helm/Deployment**: For scenarios that require additional components (GPU Operator, NFD, DRA), install the corresponding Helm charts or Kubernetes manifests.
4. **Test Pod Execution**: Inside the cluster, test pods execute assertions via Kubernetes API calls, `kubectl exec` commands (e.g. running `nvidia-smi`, `ibping`), and reading node labels and annotations.
5. **Runtime Control**: For runtime mutation tests, the `nvml-mock-ctl` CLI is exec'd into the DaemonSet pods to mutate runtime GPU simulation state without restarts.
6. **Assertions & Reporting**: Use Ginkgo/Gomega to assert conditions, collect diagnostics on failures, and report structured test results.

---

## Key Code Entities and Their Roles

```mermaid
flowchart TB
	subgraph "E2E Harness and Scenarios"
		H[harness.Harness<br/>(tests/e2e/go/framework/harness/harness.go)]
		C[config.SelectedProfileNames()<br/>(tests/e2e/go/framework/config/config.go)]
		SC[Standalone Scenario<br/>(scenario_standalone_test.go)]
		RC[Runtime Control<br/>(scenario_runtime_control.go)]
		NFD[Node Feature Discovery Scenario<br/>(scenario_nfd_test.go)]
		GPUO[GPU Operator Scenario<br/>(scenario_gpu_operator_test.go)]
		DRA[DRA Scenario<br/>(e2e-dra)]
		NRI[NRI Scenario<br/>(e2e-nri)]
		MLT[MULTI-NODE Scenario<br/>(e2e-multi-node)]
	end

	subgraph "Runtime Control"
		ctl["nvml-mock-ctl CLI<br/>(cmd/nvml-mock-ctl/main.go)"]
		ovr["Config Override<br/>YAML (overrides.yaml)"]
		eng["mocknvml/engine<br/>(pkg/gpu/mocknvml/engine)"]
	end

	subgraph "Supporting Scripts"
		ibping["validate-ibping.sh<br/>validate-iblinkinfo.sh<br/>validate-ibnetdiscover.sh"]
	end

	H -->|uses| C
	SC -->|uses| H
	RC -->|execs| ctl
	ctl -->|writes| ovr
	ovr -->|read by| eng
	scenario_codes["Assertions in scenario tests"] -->|call| RC
	MLT -->|runs| ibping
```

- The `harness.Harness` struct manages cluster lifecycle, Helm and Kube clients.
- The `config.SelectedProfileNames()` returns GPU profiles enabled in the run.
- Standalone scenario (`scenario_standalone_test.go`) creates cluster and tests each profile.
- Runtime Control tests (`scenario_runtime_control.go`) invoke `nvml-mock-ctl` CLI inside pods to mutate GPU state dynamically.
- The `nvml-mock-ctl` CLI edits a node-local config override file, which is hot-reloaded by the engine (mocknvml/engine) code inside the driver shim library.
- Supporting shell scripts validate fabric connectivity in multi-node scenarios.

Sources:  
- `tests/e2e/go/scenario_standalone_test.go` (lines 1-177)  
- `tests/e2e/go/scenario_runtime_control.go` (lines 1-320)  
- `cmd/nvml-mock-ctl/main.go` (lines 1-200)  
- `pkg/gpu/mockctl/config_override.go` (lines 1-184)  
- `tests/e2e/validate-ibping.sh`, `validate-iblinkinfo.sh`, `validate-ibnetdiscover.sh`  
- `tests/e2e/go/scenario_nfd_test.go` (lines 1-145)  
- `tests/e2e/gpu-operator-values.yaml`

---

## GPU Profile Matrix in CI

The CI system runs a matrix of test runs cycling through these GPU profiles to validate broad coverage:

| Profile Name | Use in Tests                 | Comments                      |
|--------------|-----------------------------|-------------------------------|
| `a100`       | Standalone, NFD             | Common HPC GPU profile         |
| `h100`       | Standalone                  | Latest Hopper architecture     |
| `b200`       | Standalone                  | New NVIDIA base architecture   |
| `gb200`      | Default Standalone, others  | Good baseline for development  |
| `gb300`      | Standalone                  | New generation base GPU        |
| `l40s`       | Standalone, Multi-node      | Data center GPU with IB off    |
| `t4`         | Standalone, Multi-node      | Cloud GPU, IB disabled         |

Profiles influence:

- Number of GPUs simulated per node.
- Feature enablement (e.g., InfiniBand enabled or disabled).
- Dynamic metrics and failure injection availability.

Local dev can override `E2E_PROFILES` environment variable to run specific profiles quickly (e.g., `make e2e E2E_PROFILES=a100`).

Sources:  
- `tests/e2e/go/scenario_standalone_test.go:21-42`  
- `tests/e2e/gpu-operator-values.yaml`  

---

## Makefile Targets Summary

```mermaid
graph TD
	A[Makefile] -->|runs| B[e2e]
	A -->|runs| C[e2e-dra]
	A -->|runs| D[e2e-gpu-operator]
	A -->|runs| E[e2e-nri]
	A -->|runs| F[e2e-nfd]
	A -->|runs| G[e2e-multi-node]

	B -->|executes| SC["Standalone Scenario"]
	C -->|executes| DRA["DRA Scenario"]
	D -->|executes| GPUO["GPU Operator Scenario"]
	E -->|executes| NRI["NRI Plugin Scenario"]
	F -->|executes| NFD["Node Feature Discovery Scenario"]
	G -->|executes| MLT["Multi-node Fabric Scenario"]
```

- `make e2e`: Default standalone test suite, running nvml-mock standalone with selected GPU profiles.
- `make e2e-dra`: Tests DRA integration.
- `make e2e-gpu-operator`: Tests GPU Operator Helm chart installs over mock NVML.
- `make e2e-nri`: Runs tests for NRI node-wide injection plugin.
- `make e2e-nfd`: Runs Node Feature Discovery label provenance validation.
- `make e2e-multi-node`: Runs multi-node ComputeDomain fabric and IB communication tests.

Sources:  
- `tests/e2e/go/scenario_standalone_test.go`  
- `tests/e2e/go/scenario_nfd_test.go`  
- `tests/e2e/gpu-operator-values.yaml`  

---

## Example Flow: Runtime Control Scenario

The runtime control scenarios validate that GPU failure and metric overrides can be injected live into the running DaemonSet pods without disruption.

```mermaid
sequenceDiagram
    participant TestPod as E2E Test Pod
    participant KubePod as nvml-mock DaemonSet Pod
    participant nvmlMockCtl as nvml-mock-ctl CLI
    participant OverrideYAML as Config Override YAML file
    participant Engine as mocknvml Engine in Daemon

    TestPod->>KubePod: kubectl exec "nvml-mock-ctl fail --gpu 0 --mode ecc_uncorrectable --after-calls 1 --xid 79"
    KubePod->>nvmlMockCtl: Process CLI command
    nvmlMockCtl->>OverrideYAML: Write config override (fail mode ecc_uncorrectable)
    Engine->>OverrideYAML: Periodic reload (~1s TTL)
    OverrideYAML-->>Engine: Provide merged runtime config
    Engine->>KubePod: Update device simulation state (ECC error)
    TestPod->>KubePod: kubectl exec "nvidia-smi --id=0 --query-gpu=ecc.errors.uncorrected.aggregate.total"
    KubePod-->>TestPod: Return non-zero ECC errors reported
    TestPod->>KubePod: kubectl exec "nvml-mock-ctl reset --gpu all"
    KubePod->>nvmlMockCtl: Process reset CLI command
    nvmlMockCtl->>OverrideYAML: Clear config override entries
    Engine->>OverrideYAML: Reload updates device state to healthy
    TestPod->>KubePod: kubectl exec "nvidia-smi --id=0 --query-gpu=ecc.errors.uncorrected.aggregate.total"
    KubePod-->>TestPod: Return zero ECC errors (healthy)
```

Sources:  
- `tests/e2e/go/scenario_runtime_control.go:42-173`  
- `cmd/nvml-mock-ctl/main.go:14-146`  
- `pkg/gpu/mockctl/config_override.go:14-184`  

---

## Summary

The E2E test scenarios within `k8s-test-infra` comprehensively cover key GPU simulation and integration features across container runtime, Kubernetes resource APIs, driver injection, node labelling, and multi-node fabric behaviors. They leverage a shared Kubernetes cluster lifecycle harness, multiple Helm chart overlays, and powerful runtime mutation via `nvml-mock-ctl`. The test suite's modular design allows targeted testing of subsystems (DRA, GPU Operator, NFD, NRI) and collective validation with a range of GPU profiles, ensuring robust system behavior and integration for NVIDIA GPU simulations in Kubernetes environments.

---

---

# Page: CI Image Distribution Strategy

# CI Image Distribution Strategy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/code_scanning.yaml](.github/workflows/code_scanning.yaml)
- [.github/workflows/golang.yaml](.github/workflows/golang.yaml)
- [.github/workflows/helm-publish.yaml](.github/workflows/helm-publish.yaml)
- [.github/workflows/helm.yaml](.github/workflows/helm.yaml)
- [.github/workflows/nvml-mock-e2e-go.yaml](.github/workflows/nvml-mock-e2e-go.yaml)
- [.github/workflows/nvml-mock-publish.yaml](.github/workflows/nvml-mock-publish.yaml)
- [.github/workflows/scorecard.yaml](.github/workflows/scorecard.yaml)
- [.github/workflows/variables.yaml](.github/workflows/variables.yaml)
- [Makefile](Makefile)
- [README.md](README.md)
- [deployments/devel/Dockerfile](deployments/devel/Dockerfile)
- [tests/e2e/README.md](tests/e2e/README.md)
- [tests/e2e/ci/nvml-mock.values.yaml](tests/e2e/ci/nvml-mock.values.yaml)
- [tests/e2e/go/e2e_suite_test.go](tests/e2e/go/e2e_suite_test.go)
- [tests/e2e/go/framework/config/config.go](tests/e2e/go/framework/config/config.go)
- [tests/e2e/go/framework/harness/harness.go](tests/e2e/go/framework/harness/harness.go)
- [tests/e2e/go/suite_cluster.go](tests/e2e/go/suite_cluster.go)
- [tests/e2e/go/suite_helm.go](tests/e2e/go/suite_helm.go)

</details>



This page (section 10.3) explains how the k8s-test-infra repository implements its Continuous Integration (CI) image distribution strategy, focusing on the ephemeral registry pattern used with ttl.sh, digest-pinned image references for immutable image pulls, the matrix-based parallel job structure in the E2E testing workflow, and the architecture of the `nvml-mock-e2e-go` workflow that enables parallel end-to-end (E2E) test runs efficiently.

---

## Purpose and Scope

This strategy is designed to optimize the CI process for the `nvml-mock` GPU simulation system and related Kubernetes tests by:

- Avoiding redundant image builds across parallel test jobs.
- Ensuring consistent, immutable, and retriable image references.
- Supporting GPU profile matrix testing in parallel CI jobs.
- Simplifying image distribution using an ephemeral, public container registry that requires no authentication.

This page provides full technical detail, including workflow orchestration, image tagging semantics, and the internal flow of how images are built, published, consumed, and used in the parallel E2E test job matrix.

---

## ttl.sh Ephemeral Registry Pattern

### Overview

The repository leverages the anonymous public container registry service [ttl.sh](https://ttl.sh), which allows pushing container images with a fixed time-to-live (TTL) and pull them anonymously without authentication. This registry supports ephemeral image storage capped at 24 hours TTL.

### How It Works in CI

- A dedicated CI job builds the `nvml-mock` container image once per commit and pushes it to ttl.sh, with the tag format:

  ```
  ttl.sh/nvml-mock-${GITHUB_SHA}:24h
  ```

  where `${GITHUB_SHA}` is the GitHub commit SHA associated with the current run. The TTL is set to 24 hours, ensuring images are available long enough for subsequent CI jobs to pull them without persistent storage costs.

- Multiple parallel E2E test jobs then pull this image by its **digest** (not tag) from ttl.sh to guarantee immutability and avoid race conditions stemming from tag overwrites.

- Each parallel job retags the pulled image locally with the same ttl.sh tag (for compatibility with the test harness) and then loads the image into the Kind cluster.

- Because ttl.sh requires no authentication, this pattern works on pull request forks without requiring repository secrets.

### Benefits

- **Build once, use many:** Image is built a single time and distributed to all jobs.
- **Immutable references:** Pulling by digest protects against tag mutations.
- **No auth complexity:** Works seamlessly on fork PRs without credential sharing.
- **TTL-based cleanup:** Keeps storage free of stale images automatically.

---

## Digest-Pinned Image References

The critical implementation detail is that test jobs **do not rely on image tags alone** because:

- Tags are ephemeral and can be overwritten.
- CI jobs run asynchronously; a tag could be moved before a job starts pulling.
- Pulling by image digest (`sha256:<hash>`) guarantees the exact image version.

The builder job outputs the pushed image digest (`sha256:...`). This digest is passed as an output variable and picked up by all dependent jobs, which use it to pull with explicit reference, like:

```
docker pull ttl.sh/nvml-mock-${GITHUB_SHA}@sha256:<digest>
docker tag ttl.sh/nvml-mock-${GITHUB_SHA}@sha256:<digest> ttl.sh/nvml-mock-${GITHUB_SHA}:24h
```

This pattern safeguards all downstream consumers from accidental image mutations caused by concurrent pushes or retries.

---

## Parallel Matrix Job Structure for GPU Profiles

The E2E testing workflow uses a **matrix strategy** over a list of GPU profiles to run parallel jobs that each test a distinct simulated GPU topology.

- Profiles include `a100, h100, b200, gb200, gb300, t4` by default for CI.
- The matrix axis is the GPU profile (`gpu-profile`).
- The matrix jobs share the pre-built image from the build job via the ttl.sh registry and pull it by digest.
- Each job runs a focused subset of tests against the cluster with that GPU profile installed via Helm.

### Matrix Benefits

- Parallelization reduces overall CI time substantially.
- Isolation ensures tests for one profile cannot interfere with others.
- The single image build suffices to cover all profiles since profiles are enabled at Helm install time dynamically.

---

## `nvml-mock-e2e-go` Workflow Detailed Architecture

The core GitHub Actions workflow implementing this strategy is `.github/workflows/nvml-mock-e2e-go.yaml`.

### Key Jobs

| Job Name              | Role                                                                               |
|-----------------------|------------------------------------------------------------------------------------|
| `build-nvmlmock-image`| Builds and pushes the `nvml-mock` Docker image to `ttl.sh`. Outputs the digest.    |
| `build-kind-node-image`| Builds a custom Kind node image with Nvidia container toolkit, pushed likewise to `ttl.sh`. |
| `e2e`                 | Runs the main E2E test suite, in a GPU profile matrix job that depends on image build jobs and pulls the image by digest.|

### Workflow Data Flow

```mermaid
flowchart TD
  A[Commit Push] --> B[build-nvmlmock-image Job]
  A --> C[build-kind-node-image Job]
  B --> |Pushed image digest| D[e2e Job Matrix By GPU Profile]
  C --> |Pushed kind node image digest| D
  D --> |Pull image@digest from ttl.sh| E[Retag, Load to Kind cluster]
  E --> F[nvml-mock Helm Install with GPU profile]
  F --> G[Run Ginkgo E2E tests]
```

---

### `build-nvmlmock-image` Job

- Uses `docker/build-push-action` to build multi-arch image for `nvml-mock` from `deployments/nvml-mock/Dockerfile`.
- Tags image as `ttl.sh/nvml-mock-${GITHUB_SHA}:24h` and pushes to ttl.sh.
- Caches build layers with GitHub Actions cache.
- Outputs the image digest (`sha256:...`) to ensure future jobs pull the exact image.
  
### `build-kind-node-image` Job

- Builds a custom Kind node image augmented with `nvidia-container-toolkit`.
- Pushes to `ttl.sh/kind-node-nv-${GITHUB_SHA}:24h`.
- Output the image digest similarly.

### `e2e` Job (Matrix)

- Declares a matrix over the GPU profiles (default `["a100", "h100", "b200", "gb200", "gb300", "t4"]`).
- Depends on `build-nvmlmock-image` and `build-kind-node-image`.
- In each matrix execution:
  - Pulls the `nvml-mock` image by the digest output of the builder job.
  - Retags the image locally with the ttl.sh tag.
  - Loads the image into the Kind environment.
  - Sets `E2E_SKIP_BUILD=true` to avoid rebuilding the Docker image locally.
  - Uses the pulled image to deploy the nvml-mock chart via Helm.
  - Executes the Go/Ginkgo E2E tests scoped to the given GPU profile.
  
---

## Workflow Code Snippet Highlights

```yaml
# Excerpt from .github/workflows/nvml-mock-e2e-go.yaml showing job dependencies
jobs:
  build-nvmlmock-image:
    runs-on: ubuntu-latest
    outputs:
      digest: ${{ steps.build.outputs.digest }}
    steps:
      # Build steps omitted
  build-kind-node-image:
    runs-on: ubuntu-latest
    outputs:
      digest: ${{ steps.build.outputs.digest }}
    steps:
      # Build Kind node image
  e2e:
    needs: [build-nvmlmock-image, build-kind-node-image]
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        gpu-profile: ${{ fromJson(inputs.gpu_profiles) }}
    steps:
      - name: Pull nvml-mock image by digest
        run: |
          docker pull ttl.sh/nvml-mock-${{ github.sha }}@${{ needs.build-nvmlmock-image.outputs.digest }}
          docker tag ttl.sh/nvml-mock-${{ github.sha }}@${{ needs.build-nvmlmock-image.outputs.digest }} ttl.sh/nvml-mock-${{ github.sha }}:24h
```

---

## nvml-mock E2E Harness Usage

The local test harness in `./tests/e2e/go` consumes the distributed image similarly:

- When `E2E_SKIP_BUILD` is true, the harness does not build the Docker image but uses the specified `E2E_IMAGE` (ttl.sh reference).
- Harness loads this image into the Kind cluster and proceeds with Helm-based deployment and validation.
- This consistent approach unifies local developer runs and CI runs.

---

## Summary Diagram: Natural Language to Code Entities

```mermaid
graph TD
  CI[CI System - GitHub Actions] -->|runs| Workflow["nvml-mock-e2e-go Workflow (.github/workflows/nvml-mock-e2e-go.yaml)"]
  Workflow -->|builds| BuildImage["build-nvmlmock-image Job"]
  BuildImage -.->|outputs digest| DigestOutput["Image Digest Output (sha256:...)"]
  Workflow -->|builds| BuildKindNode["build-kind-node-image Job"]
  Workflow -->|runs parallel| E2EMatrix["e2e Job Matrix Over gpu-profile"]
  E2EMatrix -->|pulls image by digest| PullImage["docker pull ttl.sh/nvml-mock@digest"]
  E2EMatrix -->|retags image locally| TagImage["docker tag to ttl.sh/nvml-mock:24h"]
  E2EMatrix -->|loads image| LoadImage["Kind cluster image load"]
  LoadImage -->|deploys nvml-mock| HelmDeploy["Helm install/upgrade, profile-based"]
  HelmDeploy -->|runs tests| GinkgoTests["Go/Ginkgo E2E test suite"]
```

---

## Summary Diagram: Code Repository Files to Concepts

```mermaid
graph TD
  CW[Workflow files in .github/workflows/] -->|Defines| NvmlE2E[`.github/workflows/nvml-mock-e2e-go.yaml`]
  NvmlE2E -->|Build job| BuildJob["build-nvmlmock-image job"]
  NvmlE2E -->|Build job| KindNodeJob["build-kind-node-image job"]
  NvmlE2E -->|Matrix job| MatrixJob["e2e job with matrix on gpu-profile"]
  MatrixJob -->|Uses env| EnvVars[`E2E_SKIP_BUILD`, `E2E_IMAGE`]
  MatrixJob -->|Runs test code in| TestPkg[`tests/e2e/go/...`]

  mkf[Makefile] -->|Defines make targets like| E2ETarget[`make e2e`]
  E2ETarget -->|Runs test harness| TestPkg

  TestPkg -->|Test code uses| Harness[`framework/harness/harness.go`]
  Harness -->|Loads images specified in env| EnvVars
```

---

## Additional Notes

- The build caching is optimized per job using GitHub Action cache scoped by job to reduce redundant rebuilds.
- The `e2e` job sets `E2E_SKIP_BUILD=true` explicitly, so the GitHub runners do not rebuild images locally but use the injected ones.
- The ephemeral nature of ttl.sh is embraced as a caching layer; images older than 24h expire, ensuring cluster retainment or reruns must rebuild or repush.
- Extensibility for adding new GPU profiles is straightforward with the matrix job expansion.

---

# References

- GitHub Actions workflow for nvml-mock E2E Go: `.github/workflows/nvml-mock-e2e-go.yaml` [33:1586-1687]()
- README overview of Ginkgo E2E and image usage: `README.md` [18:67-67]()
- Makefile related to cluster creation and E2E test entrypoint: `Makefile` [10:139-156]()
- Tests/E2E README describing parallel profiles and image loading: `tests/e2e/README.md` [3:160-261]()

Sources:  
`.github/workflows/nvml-mock-e2e-go.yaml, README.md, Makefile, tests/e2e/README.md`

---

# Page: Local Development Environment

# Local Development Environment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Tiltfile](Tiltfile)
- [docs/demo/README.md](docs/demo/README.md)
- [docs/demo/node-wide-injection/README.md](docs/demo/node-wide-injection/README.md)
- [docs/demo/node-wide-injection/run.sh](docs/demo/node-wide-injection/run.sh)
- [docs/demo/nv-sentinel/README.md](docs/demo/nv-sentinel/README.md)
- [docs/demo/nv-sentinel/gpu-operator-values.yaml](docs/demo/nv-sentinel/gpu-operator-values.yaml)
- [docs/demo/nv-sentinel/kind.yaml](docs/demo/nv-sentinel/kind.yaml)
- [docs/demo/nv-sentinel/mongodb.yaml](docs/demo/nv-sentinel/mongodb.yaml)
- [docs/demo/nv-sentinel/nvsentinel-values.yaml](docs/demo/nv-sentinel/nvsentinel-values.yaml)
- [docs/demo/nv-sentinel/run.sh](docs/demo/nv-sentinel/run.sh)
- [docs/demo/nv-sentinel/sample-workload.yaml](docs/demo/nv-sentinel/sample-workload.yaml)
- [docs/demo/standalone/README.md](docs/demo/standalone/README.md)
- [docs/demo/standalone/demo.sh](docs/demo/standalone/demo.sh)
- [local/.gitignore](local/.gitignore)
- [local/README.md](local/README.md)
- [local/compute-domain/compute_domain.tiltfile](local/compute-domain/compute_domain.tiltfile)
- [local/compute-domain/dra-driver.values.yaml](local/compute-domain/dra-driver.values.yaml)
- [local/compute-domain/nvml-mock.values.yaml](local/compute-domain/nvml-mock.values.yaml)
- [local/compute-domain/rebind.topology.yaml](local/compute-domain/rebind.topology.yaml)
- [local/compute-domain/scenarios/check-fabric.sh](local/compute-domain/scenarios/check-fabric.sh)
- [local/nvml_mock.tiltfile](local/nvml_mock.tiltfile)

</details>



The local development environment in `k8s-test-infra` is designed to enable contributors to build, deploy, and test the nvml-mock GPU simulation stack and its related components interactively on local Kubernetes clusters managed via Kind. This environment centers around Tilt as a live-reload orchestrator, enabling rapid iteration, debugging, and scenario experimentation. It supports various deployment modes of nvml-mock, integration with NVIDIA GPU Operator, NVIDIA DRA driver, Run:ai Fake GPU Operator (FGO), and advanced scenarios like ComputeDomain.

This page provides a high-level overview of the local development setup, including the Tilt-based workflow, Kind cluster profiles, Helm value layering strategy, and scenario-specific configurations that facilitate simulation of heterogeneous GPU fleets, integration demos, and multi-node GPU fabric simulation. For detailed guides and technical deep-dives, see the linked child pages.

---

## Tilt-Based Local Development Workflow

At the core of local development is **Tilt**, a powerful live-reload Kubernetes resource orchestrator used here to build Docker images, render Helm charts, and manage deployments in a synchronized manner.

- The root `Tiltfile` (repository root) acts as a thin orchestrator that loads and delegates to sub-Tiltfiles under `local/` for each consumer component or scenario.
- The core nvml-mock GPU simulation stack lifecycle is defined in `local/nvml_mock.tiltfile`.
- Other components such as GPU Operator, DRA driver, FGO, and ComputeDomain have dedicated sub-Tiltfiles, e.g., `local/gpu-operator/gpu_operator.tiltfile`, `local/dra/dra.tiltfile`, `local/fgo/fgo.tiltfile`, and `local/compute-domain/compute_domain.tiltfile`.
- Flags passed to `tilt up` (e.g., `--gpu-profile`, `--multi-gpu-profile`, `--gpu-operator`, `--dra`, `--fgo`, `--compute-domain`) turn on specific components and scenarios, controlling image builds, Helm install parameters, and cluster topology.

This modular orchestrator approach allows independent consumer components or scenarios to request their own overlays and Helm value files while sharing a common base nvml-mock stack.

```mermaid
flowchart TB
    TL[Tilt CLI]
    TF[Tiltfile (root)]
    NM[local/nvml_mock.tiltfile]
    GO[local/gpu-operator/gpu_operator.tiltfile]
    DR[local/dra/dra.tiltfile]
    FG[local/fgo/fgo.tiltfile]
    CD[local/compute-domain/compute_domain.tiltfile]
    
    TL --> TF
    TF --> NM
    TF --> GO
    TF --> DR
    TF --> FG
    TF --> CD
```
*Diagram 1: Tilt orchestrator loads consumer and scenario sub-Tiltfiles to build and deploy components.*

Tilt supports automatic live reload upon source or configuration changes, enabling immediate feedback. Image builds and Helm chart Helm upgrades are managed as `helm_resource` targets within Tilt, supporting image pins to pre-built images (e.g., TTL.sh) for CI integration.

For full details including flag descriptions, the structure of the Tiltfiles, and live-reload behavior, see the child page [Tilt Development Workflow](#11.1).

Sources: `Tiltfile:1-154`, `local/nvml_mock.tiltfile:1-154`, `local/README.md:1-145`

---

## Kind Cluster Profiles and Topologies

Local testing and demos run on Kind clusters configured to simulate various Kubernetes topologies and node shapes:

| Profile           | Kind Config File                         | Cluster Name                    | Typical Usage                              |
|-------------------|----------------------------------------|--------------------------------|--------------------------------------------|
| `default` (base)  | `local/kind/default.kind.yaml`          | `kind-gpu-test`                 | Most development, basic, GPU Operator, DRA, FGO, multi-GPU-profile |
| `compute-domain`  | `local/kind/compute-domain.kind.yaml`   | `kind-nvml-mock-compute-domain`| Advanced NVLink fabric simulation, 4-worker topology |

- The default cluster profile creates 1 control-plane and 2 worker nodes labeled for nvml-mock GPU simulation with distinct GPU profile node labels (`a100` and `t4`).
- The ComputeDomain profile provides a 4-worker cluster setup designed for multi-node GPU fabric simulation with NVLink clique clustering.

Kind images used are custom-built via `local/kind/Dockerfile` (`kind-node-nv:latest`), preinstalled with the NVIDIA container runtime to enable GPU simulation tools such as nvidia-container-toolkit in CDI mode.

Cluster creation and teardown are automated through Makefile targets:

```bash
# Create default cluster (1 CP + 2 workers)
make cluster-create

# Create compute-domain profile cluster (1 CP + 4 workers)
make cluster-create PROFILE=compute-domain

# Delete cluster (must match PROFILE)
make cluster-delete PROFILE=compute-domain
```

This separation enables dedicated testing for different development scenarios, ensuring a stable baseline for component installation and upgrade testing.

Sources: `local/README.md:5-145`, `docs/demo/nv-sentinel/kind.yaml:1-34`

---

## Helm Value Overrides and Layering

The nvml-mock Helm chart deploys the mock GPU stack with flexible configuration. To support local development configurations, the Helm values are layered by Tilt and by manual overrides:

| Source File                           | Committed | Purpose                                                                                |
|-------------------------------------|-----------|----------------------------------------------------------------------------------------|
| Chart Defaults                      | —         | Base settings baked into the Helm chart                                               |
| `local/nvml-mock.values.yaml`        | Yes       | Shared local development baseline settings (e.g., InfiniBand mode, rollout settings)  |
| `local/<consumer>/nvml-mock.values.yaml` | Yes       | Consumer-specific tweaks (e.g., GPU Operator or DRA mock integration overrides)       |
| `local/nvml-mock.values.local.yaml`  | No (gitignored) | Individual developer overrides to tune settings absent from VCS to avoid commit noise |

The overlay order ensures that specific consumer overlays and personal settings override previous layers, enabling flexible development without polluting the shared repository state.

For example, the compute-domain scenario uses `local/compute-domain/nvml-mock.values.yaml` to adjust GPU counts and topology overlays required for multi-node simulation.

Sources: `local/README.md:121-145`, `local/nvml_mock.tiltfile:73-154`

---

## Scenario-Specific Tiltfile Configurations

Several demo and scenario directories under `docs/demo/` and matching Tiltfiles in `local/` provide prepackaged environments illustrating typical usage patterns:

- **Standalone Demo** (`docs/demo/standalone`): Deploy nvml-mock with a single Helm release using FGO-style GPU labels without a separate GPU operator. The `demo.sh` script automates cluster creation, image build and load, and Helm install with configurable GPU profiles and counts.

- **Node-Wide Injection Demo** (`docs/demo/node-wide-injection`): Demonstrates containerd NRI-based node-wide injection allowing pods to consume mock GPUs without explicit resource requests or spec mutation. It also illustrates compute-domain fabric identity propagation through the NRI plugin. Deploys a dedicated cluster with the `nvml-mock-nri` DaemonSet and test workloads.

- **ComputeDomain Demo** (`docs/demo/compute-domain`): Simulates multi-node NVLink fabric topology with a GB200 profile on a 4-worker cluster. Exercises real `nvidia-imex` daemon gRPC domain with topology rebind triggers from Tilt manual actions.

- **NVSentinel Demo** (`docs/demo/nv-sentinel`): Shows thermal-margin detection and remediation by NVSentinel using mock GPUs and GPU Operator with DCGM in standalone mode. Includes MongoDB TLS setup, cert-manager dependencies, and node draining workflows.

- **With Fake GPU Operator (FGO)** (`docs/demo/with-fgo`): Integrates Run:ai's Fake GPU Operator to simulate scale pools alongside nvml-mock for integration pools.

Each scenario exposes a `Tiltfile` or script that sets up the cluster topology, builds/loads images, and applies Helm charts with scenario-specific values, often passing flags to Tilt to activate necessary subcomponents.

```mermaid
graph TD
  A["Tiltfile (root)"] --> B["local/nvml_mock.tiltfile"]
  A --> C["local/nri.tiltfile (node-wide injection)"]
  A --> D["local/compute-domain/compute_domain.tiltfile"]
  A --> E["local/gpu-operator/gpu_operator.tiltfile"]
  A --> F["local/fgo/fgo.tiltfile"]
  B --> G["Helm chart: nvml-mock"]
  C --> H["Helm chart: nvml-mock-nri"]
  D --> I["ComputeDomain images + Helm"]
  
  style A fill:#f9f,stroke:#333,stroke-width:1px
  style B fill:#bbf,stroke:#333,stroke-width:1px
```

*Diagram 2: Scenario-specific Tiltfiles and their Helm charts under the Tilt orchestrator.*

Developers can run these demos via simple scripts (`./demo.sh`, `./run.sh`) and leverage Tilt flags for customizations like selecting GPU profile (`--gpu-profile`), enabling GPU Operator (`--gpu-operator`), or multi-profile heterogenous fleet mode (`--multi-gpu-profile`).

For detailed step-by-step guides and integrations, see the child page [Demo Scenarios and Integration Examples](#11.2).

Sources: `docs/demo/standalone/demo.sh:1-149`, `docs/demo/node-wide-injection/README.md:1-116`, `local/README.md:83-99`, `docs/demo/nv-sentinel/README.md:1-153`

---

## Summary and Next Steps

This page introduced the local development environment infrastructure for the k8s-test-infra repository, focusing on:

- The **Tilt-based workflow** that manages Docker image builds, Helm chart deployments, and multi-component orchestration via modular Tiltfiles.
- The use of **Kind cluster profiles** to support varying node topologies and GPU fleet heterogeneity for simulation and testing.
- How **Helm values are layered** to provide a flexible and composable configuration system for local tweaks and consumer-specific overrides.
- The role of **scenario-specific Tiltfiles and demos** to document complex integration examples and multi-node simulations.

To adopt this environment:

1. Install prerequisites: Kind, Tilt, Helm, Docker, kubectl.
2. Create the appropriate Kind cluster (`make cluster-create`).
3. Start the development environment by running `tilt up` with desired flags.
4. Explore and run demo scenarios via their scripts.

For comprehensive usage instructions, hands-on tutorials, and reference documentation, see the child pages:

- [Tilt Development Workflow](#11.1)
- [Demo Scenarios and Integration Examples](#11.2)

---

**Sources:**

- `Tiltfile:1-154`  
- `local/nvml_mock.tiltfile:1-154`  
- `local/README.md:1-145`  
- `docs/demo/standalone/demo.sh:1-149`  
- `docs/demo/node-wide-injection/README.md:1-116`  
- `docs/demo/nv-sentinel/README.md:1-153`  
- `docs/demo/nv-sentinel/kind.yaml:1-34`

---

# Page: Tilt Development Workflow

# Tilt Development Workflow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Tiltfile](Tiltfile)
- [docs/demo/node-wide-injection/README.md](docs/demo/node-wide-injection/README.md)
- [docs/demo/node-wide-injection/run.sh](docs/demo/node-wide-injection/run.sh)
- [docs/demo/standalone/README.md](docs/demo/standalone/README.md)
- [docs/demo/standalone/demo.sh](docs/demo/standalone/demo.sh)
- [local/.gitignore](local/.gitignore)
- [local/README.md](local/README.md)
- [local/compute-domain/compute_domain.tiltfile](local/compute-domain/compute_domain.tiltfile)
- [local/compute-domain/dra-driver.values.yaml](local/compute-domain/dra-driver.values.yaml)
- [local/compute-domain/nvml-mock.values.yaml](local/compute-domain/nvml-mock.values.yaml)
- [local/compute-domain/rebind.topology.yaml](local/compute-domain/rebind.topology.yaml)
- [local/compute-domain/scenarios/check-fabric.sh](local/compute-domain/scenarios/check-fabric.sh)
- [local/nvml_mock.tiltfile](local/nvml_mock.tiltfile)

</details>



This page documents the local development workflow powered by Tilt for the `k8s-test-infra` repository, focusing on how to use its command line flags to customize cluster test environments, the structure of the Tiltfile configuration, and the live reload behavior that accelerates development. 

The documentation covers key Tilt flags that control GPU profile selection, GPU Operator and Dynamic Resource Allocation (DRA) integration, Run:ai Fake GPU Operator (FGO) usage, and ComputeDomain fabric simulation. It explains the modular architecture of the main Tiltfile and its composition of sub-Tiltfiles that encapsulate deployment units. Lastly, it details the live reload mechanisms designed for efficient iterative development.

---

## Overview

The repository's local development environment relies on [Tilt](https://tilt.dev) — an orchestrator that manages Kubernetes cluster lifecycle, image builds, Helm charts, and live reload of code changes. Contributors invoke `tilt up` with optional flags to launch a simulated Kubernetes ecosystem with mock NVML GPU devices, relevant operators, and specialized drivers. 

Key configurable aspects include:

- The GPU profile(s) installed on the mock nodes
- Enabling NVIDIA GPU Operator deployment for Kubernetes integration
- Enabling NVIDIA Dynamic Resource Allocation (DRA) driver functionality
- Enabling Run:ai Fake GPU Operator (FGO) alternative
- Running the ComputeDomain multi-node NVLink fabric simulation
- Deploying a heterogeneous GPU profile fleet with per-profile releases

These options flexibly compose complex local test clusters matching many CI and demo scenarios. The Tiltfile system is designed to be modular, composable, and safe, guarding conflicting flag combinations.

---

## Tilt `up` Command Flags

The main workflow is driven by command line flags passed to `tilt up` after `--`. These flags control deployment shape and integrations:

| Flag                 | Description                                                                                                           |
|----------------------|-----------------------------------------------------------------------------------------------------------------------|
| `--gpu-profile`       | Select a single GPU profile (e.g. `a100`, `h100`, `b200`, `gb200`, `gb300`, `l40s`, `t4`) to simulate for the mock DaemonSet.<br>Ignored if `--multi-gpu-profile` is set. Default is `a100`. |
| `--multi-gpu-profile` | Deploy one nvml-mock Helm release per GPU profile pinned to nodes by label. Simulates a heterogeneous GPU fleet (default profiles are `a100` and `t4`). Conflicts with `--compute-domain`. No explicit profile needed. |
| `--gpu-operator`      | Deploy NVIDIA GPU Operator alongside nvml-mock. Composes with homogeneous or heterogeneous multis. Mutually exclusive with `--fgo`. |
| `--dra`               | Deploy NVIDIA DRA driver on top of nvml-mock. Composes with `--gpu-operator` or independently. Each multi-profile releases publishes distinct ResourceSlices. |
| `--fgo`               | Deploy Run:ai Fake GPU Operator alongside nvml-mock, splitting workers into "integration" and "scale" pools.<br>Mutually exclusive with `--gpu-operator` and `--compute-domain`. Ignored if `--multi-gpu-profile` is not also set. |
| `--compute-domain`    | Run the ComputeDomain scenario: a 4-worker kind cluster configured with GB200 profile and a NVLink topology overlay providing GPU fabric simulation.<br>Mutually exclusive with `--multi-gpu-profile` and explicit `--gpu-profile` flags. Operator is allowed but experimental. |

### Examples

```bash
tilt up -- --gpu-profile h100
tilt up -- --multi-gpu-profile --gpu-operator --dra
tilt up -- --fgo --multi-gpu-profile
tilt up -- --compute-domain --dra
```

### Flag Interaction Guardrails

- `--compute-domain` cannot be combined with `--multi-gpu-profile` or explicit `--gpu-profile`.
- `--fgo` cannot be combined with `--gpu-operator` or `--compute-domain`.
- `--nvmlmock-image` (a CI override for pre-built images) cannot be used with `--compute-domain`.

The Tiltfile enforces these rules at runtime and fails Tilt start with an error if violated.

---

## Tiltfile Structure and Composition

The main `Tiltfile` located at the repository root is an orchestrator that loads sub-Tiltfiles representing related deployment concerns.

### Modular Architecture

- **local/nvml_mock.tiltfile**: Core nvml-mock image build and Helm release installation functions.
- **local/gpu-operator/gpu_operator.tiltfile**: Installs NVIDIA GPU Operator Helm release.
- **local/dra/dra.tiltfile**: Installs NVIDIA DRA driver Helm release.
- **local/fgo/fgo.tiltfile**: Installs Fake GPU Operator Helm release.
- **local/compute-domain/compute_domain.tiltfile**: Special scenario for the ComputeDomain multi-node NVLink fabric simulation.

The root `Tiltfile` uses `config.define_*` calls to define command line flags, processes flag values to set boolean toggles, and depending on flags, calls build and install functions for one or more components.

### Main Control Flow

```python
# Parse config flags (gpu-profile, multi-gpu-profile, compute-domain, gpu-operator, dra, fgo, nvmlmock-image)
cfg = config.parse()

# Validate incompatible flag combinations
if with_compute_domain and multi_gpu_profile:
    fail(...)
if with_fgo and with_gpu_operator:
    fail(...)
...

# Determine kubectl context to restrict allowed contexts (guardrail)
allow_k8s_contexts(k8s_context)

# Compose nvml-mock image build and release installation
if with_compute_domain:
    compute_domain_build_images(...)
    nvml_mock_releases = compute_domain_install(...)
elif multi_gpu_profile:
    build_nvml_mock_image(...)
    nvml_mock_releases = install_fleet(...)
else:
    build_nvml_mock_image(...)
    nvml_mock_releases = install_single(...)

# Add GPU Operator product if requested
if with_gpu_operator:
    gpu_operator_install(...)

# Add DRA driver if requested
if with_dra:
    dra_install(...)

# Add Fake GPU Operator if requested
if with_fgo:
    fgo_install(...)
```

The above logic guarantees that the correct images and Helm releases are built and deployed. The `nvml_mock_releases` variable tracks the set of installed nvml-mock resources for dependency wiring.

### Image Build Behavior

- If `--nvmlmock-image` is specified, indicating a pre-built image reference, the Docker build is skipped and Helm releases are pinned to that image by overriding the image repository and tag.
- Otherwise the nvml-mock image is built locally from the root Dockerfile.

### Helm Values Overlay

Each consumer or scenario can optionally provide Helm value YAML overlays under `local/<consumer>/nvml-mock.values.yaml` to tweak Helm Chart values and the mock GPU config. These are layered on top of a shared baseline `local/nvml-mock.values.yaml`. Users can also add personal overrides `local/nvml-mock.values.local.yaml` ignored by git.

---

## Live Reload Behavior

Tilt's core value is live reload for iterative development:

- **File Watches**: The `docker_build()` call in `local/nvml_mock.tiltfile` declares explicit watched files and folders including source code, vendor dependencies, Helm charts, and overlays.
- **Helm Chart Reload**: `helm_resource()` dependency on built images triggers pod rollouts for changed images or chart values.
- **Config Overlays**: Changes to Helm value overlay files in `local/*.yaml` trigger reload of nvml-mock Helm releases.
- **Sub-Tiltfiles**: Loaded sub-Tiltfiles are pure import-only by design; all build/install effects occur within functions, enabling clean orchestration in the root `Tiltfile`.
- **Flag Compositions**: Since features like GPU Operator and DRA are incorporated with independent Helm releases and overlays, their files are watched separately, reducing full rebuild scope.

This design minimizes unnecessary rebuilds while enabling fast mutation of mock GPU profiles, cluster topology, or operator flags.

---

## Dataflow and Key Functions/Classes

### Flag Parsing and Guardrails (`Tiltfile:39-94`)

- Flags are defined with `config.define_string` and `config.define_bool`.
- After parsing, incompatible flag combinations are checked and `fail()` invoked to abort.
- Kubernetes context is restricted to known local cluster contexts for safety (`allow_k8s_contexts()`).

### Core nvml-mock Build and Install (`local/nvml_mock.tiltfile`)

- `build_nvml_mock_image(nvmlmock_image='')`: runs `docker_build()` unless image is pre-built.
- `_install(...)`: generic Helm release install helper building `--set` flags for profile and overlays.
- `install_single(profile, active_consumers, nvmlmock_image='')`: installs one Helm release named `nvml-mock`.
- `install_fleet(active_consumers, profiles=FLEET_PROFILES, nvmlmock_image='')`: installs per-profile Helm releases pinned by nodeSelector.

### Consumer Installation (`Tiltfile:114-123`)

- Each consumer (`gpu-operator`, `dra`, `fgo`) is added conditionally to `active_consumers`.
- Corresponding consumer Tiltfiles export `install()` functions called here, passing `nvml_mock_releases`.

### ComputeDomain Scenario (`Tiltfile:130-133`)

- Calls `compute_domain_build_images(with_dra)`
- Then calls `compute_domain_install(active_consumers)`
- The scenario overrides default image building and installation, guarded to exclude other multi-profile or explicit profile usage.

---

## Mermaid Diagrams

### Diagram 1: Tilt CLI Flags to Code Path Mapping

```mermaid
flowchart TD
    subgraph "Tilt CLI Flags (tilt up -- <flags>)"
        direction LR
        F_GPU_PROFILE["--gpu-profile"]
        F_MULTI_GPU_PROFILE["--multi-gpu-profile"]
        F_GPU_OPERATOR["--gpu-operator"]
        F_DRA["--dra"]
        F_FGO["--fgo"]
        F_COMPUTE_DOMAIN["--compute-domain"]
        F_NVML_IMAGE["--nvmlmock-image"]
    end

    subgraph "Root Tiltfile (Tiltfile)"
        direction TB
        A_PARSE_FLAGS["config.parse()"]
        A_VALIDATE_FLAGS["flag guardrails (`fail()` if invalid)"]
        A_SET_CONSUMERS["set active_consumers list"]
        A_BUILD_NVML_IMAGE["build_nvml_mock_image() or compute_domain_build_images()"]
        A_INSTALL_NVML["install_single() or install_fleet() or compute_domain_install()"]
        A_INSTALL_GPU_OPERATOR["gpu_operator_install()"]
        A_INSTALL_DRA["dra_install()"]
        A_INSTALL_FGO["fgo_install()"]
    end

    F_GPU_PROFILE --> A_PARSE_FLAGS
    F_MULTI_GPU_PROFILE --> A_PARSE_FLAGS
    F_COMPUTE_DOMAIN --> A_PARSE_FLAGS
    F_GPU_OPERATOR --> A_PARSE_FLAGS
    F_DRA --> A_PARSE_FLAGS
    F_FGO --> A_PARSE_FLAGS
    F_NVML_IMAGE --> A_PARSE_FLAGS

    A_PARSE_FLAGS --> A_VALIDATE_FLAGS
    A_VALIDATE_FLAGS --> A_SET_CONSUMERS
    A_SET_CONSUMERS --> A_BUILD_NVML_IMAGE
    A_BUILD_NVML_IMAGE --> A_INSTALL_NVML
    A_SET_CONSUMERS --> A_INSTALL_GPU_OPERATOR
    A_SET_CONSUMERS --> A_INSTALL_DRA
    A_SET_CONSUMERS --> A_INSTALL_FGO
```

*This diagram shows how user flags passed on the command line propagate through the root Tiltfile's main logical flow.*

---

### Diagram 2: Tiltfile Modular Composition and Helm Deployment

```mermaid
graph TD
    subgraph "Tiltfile Import Graph"
        root[Tiltfile]

        nvml_mock["local/nvml_mock.tiltfile"]
        gpu_op["local/gpu-operator/gpu_operator.tiltfile"]
        dra["local/dra/dra.tiltfile"]
        fgo["local/fgo/fgo.tiltfile"]
        compute_domain["local/compute-domain/compute_domain.tiltfile"]

        root --> nvml_mock
        root --> gpu_op
        root --> dra
        root --> fgo
        root --> compute_domain
    end

    subgraph "nvml_mock.tiltfile"
        build_img["build_nvml_mock_image()"]
        install_single["install_single()"]
        install_fleet["install_fleet()"]
    end

    subgraph "Scenario: compute_domain"
        cd_build["compute_domain_build_images()"]
        cd_install["compute_domain_install()"]
    end

    root -->|calls| build_img
    root -->|calls| install_single
    root -->|calls| install_fleet

    root -->|calls| gpu_op_install["gpu_operator_install()"]
    root -->|calls| dra_install["dra_install()"]
    root -->|calls| fgo_install["fgo_install()"]
    root -->|calls| cd_build
    root -->|calls| cd_install

    build_img --> helm_nvml["nvml-mock Helm release(s)"]
    install_single --> helm_nvml
    install_fleet --> helm_nvml
    cd_install --> helm_nvml
    gpu_op_install --> helm_gpu_operator["gpu-operator Helm release"]
    dra_install --> helm_dra["dra Helm release"]
    fgo_install --> helm_fgo["fgo Helm release"]
```

*Shows the modular Tiltfile import and function call structure leading to Helm release deployments for the nvml-mock stack and optional consumers.*

---

## Summary

- `tilt up --` is the entry point with several key flags controlling GPU profile(s) and integration consumers.
- The root `Tiltfile` parses these flags, verifies no conflicts, determines the active deployment components, and orchestrates builds and Helm installs dynamically.
- The core nvml-mock stack is installed as one release for homogeneous profiling (`--gpu-profile`), or multi-release fleet for heterogeneous nodes (`--multi-gpu-profile`).
- Specialized scenario `--compute-domain` forces a dedicated cluster topology and layered image build/install path.
- Deployment of GPU Operator, DRA driver, and Fake GPU Operator are composable via boolean flags, except where explicitly mutually exclusive.
- The Tiltfiles use layered Helm value YAML files for fine local config and support personal overrides.
- Live reload watches all image source and Helm values overlays, triggering fast image rebuilds and pod rollouts.

This design provides a flexible, composable, and high-performance local Kubernetes development environment consistent with CI and demo cluster shapes.

---

## Sources

- `Tiltfile:1-154`  
- `local/nvml_mock.tiltfile:1-154`  
- `local/README.md:1-145`  
- `docs/demo/standalone/demo.sh:1-150`  
- `docs/demo/node-wide-injection/README.md:1-116`  
- `docs/demo/node-wide-injection/run.sh:1-160`  
- `local/compute-domain/nvml-mock.values.yaml:1-25`  
- `local/compute-domain/compute_domain.tiltfile` (referenced but content not shown)

---

# Page: Demo Scenarios and Integration Examples

# Demo Scenarios and Integration Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Tiltfile](Tiltfile)
- [deployments/nvml-mock/helm/nvml-mock/templates/NOTES.txt](deployments/nvml-mock/helm/nvml-mock/templates/NOTES.txt)
- [deployments/nvml-mock/helm/nvml-mock/templates/integrations-fgo.yaml](deployments/nvml-mock/helm/nvml-mock/templates/integrations-fgo.yaml)
- [docs/README.md](docs/README.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/demo/README.md](docs/demo/README.md)
- [docs/demo/kind.yaml](docs/demo/kind.yaml)
- [docs/demo/node-wide-injection/README.md](docs/demo/node-wide-injection/README.md)
- [docs/demo/node-wide-injection/run.sh](docs/demo/node-wide-injection/run.sh)
- [docs/demo/nv-sentinel/README.md](docs/demo/nv-sentinel/README.md)
- [docs/demo/nv-sentinel/gpu-operator-values.yaml](docs/demo/nv-sentinel/gpu-operator-values.yaml)
- [docs/demo/nv-sentinel/kind.yaml](docs/demo/nv-sentinel/kind.yaml)
- [docs/demo/nv-sentinel/mongodb.yaml](docs/demo/nv-sentinel/mongodb.yaml)
- [docs/demo/nv-sentinel/nvsentinel-values.yaml](docs/demo/nv-sentinel/nvsentinel-values.yaml)
- [docs/demo/nv-sentinel/run.sh](docs/demo/nv-sentinel/run.sh)
- [docs/demo/nv-sentinel/sample-workload.yaml](docs/demo/nv-sentinel/sample-workload.yaml)
- [docs/demo/standalone/README.md](docs/demo/standalone/README.md)
- [docs/demo/standalone/demo.sh](docs/demo/standalone/demo.sh)
- [docs/demo/with-fgo/README.md](docs/demo/with-fgo/README.md)
- [docs/examples.md](docs/examples.md)
- [docs/integrations/fake-gpu-operator.md](docs/integrations/fake-gpu-operator.md)
- [docs/quickstart.md](docs/quickstart.md)
- [local/README.md](local/README.md)
- [local/nvml_mock.tiltfile](local/nvml_mock.tiltfile)

</details>



This page documents practical, runnable demonstration scenarios and integration examples for `k8s-test-infra`, focusing on the `nvml-mock` GPU simulation system and its integration with Kubernetes environments. We cover the standalone demo, node-wide injection demo with NRI, the ComputeDomain fabric simulation demo, the NVSentinel thermal margin detection demo, and full integration with Run:ai’s fake-gpu-operator (FGO).

These demos serve both as end-to-end usage references showcasing real cluster deployments, and as integration exemplars combining `nvml-mock` with related GPU lifecycle tooling.

---

## 1. Standalone Demo

The standalone demo deploys `nvml-mock` on a local Kind cluster with GPU device simulation configured directly by `nvml-mock` itself. It mimics GPU Operator labels and ConfigMaps inline, without relying on an external GPU operator or injections.

### Implementation and Flow

- The demo starts by creating a Kind cluster named `nvml-mock-demo` with 1 control-plane and 3 worker nodes based on a local Kind config.
- It builds the `nvml-mock:demo` Docker image from the repo root and loads it into the Kind cluster.
- It installs the `nvml-mock` Helm chart into the `mokka` namespace with parameters:
  - GPU profile set via `GPU_PROFILE` environment variable (default "h100").
  - GPU count per node set via `GPU_COUNT` (default 8).
  - The flag to enable `fakeGpuOperator` integration for generating standard GPU profile ConfigMaps.
- The demo verifies successful deployment by checking DaemonSet rollout, existence of profile ConfigMaps, running `nvidia-smi` inside a pod, and validating InfiniBand mock device status.

The demo script `docs/demo/standalone/demo.sh` orchestrates these steps with detailed logging and error checking.

### Key Components

- **Kind cluster**: test environment for Kubernetes, pinned to context `kind-nvml-mock-demo`.
- **Docker image**: builds and loads the `nvml-mock` image with the embedded mock NVML library and tools.
- **Helm chart**: configures daemonset pods running the mock GPU driver and exposes simulated devices.
- **Profile ConfigMaps**: six ConfigMaps generated representing different profile fields for consumers like GPU Feature Discovery.
- **Validation**: bash script snippets run `nvidia-smi` and IB tools to confirm mock device realism.

```mermaid
flowchart LR
  A["demo.sh"] --> B["Kind Cluster 'nvml-mock-demo'"]
  B --> C["Load Docker Image 'nvml-mock:demo'"]
  C --> D["nvml-mock Helm Chart Install (namespace=mokka)"]
  D --> E["DaemonSet runs with nvml-mock pods"]
  E --> F["GPU Profile ConfigMaps created"]
  F --> G["Run 'nvidia-smi' inside pod"]
  G --> H["Run InfiniBand mock tools (ibstat, ibstatus)"]
```

This demo presents a fully self-contained GPU simulation environment for initial exploration or standalone testing.

Sources:  
`docs/demo/standalone/demo.sh:1-148`  
`docs/demo/standalone/README.md:1-48`  

---

## 2. Node-Wide Injection Demo (NRI)

This demo exercises the **Node Resource Interface (NRI)** plugin integration that transparently injects the mock GPU environment *ambiently*, without requiring pods to declare GPU requests or annotations or mutate pod specs explicitly.

### Architecture and Behavior

- A dedicated Kind cluster (`nvml-mock-node-wide-demo`) with 4 worker nodes is created and configured for containerd with NRI enabled.
- The Helm chart deploys two DaemonSets:
  - `nvml-mock` running the mock NVML stack.
  - `nvml-mock-nri` NRI plugin that:
    - Monitors pod creation events on the node.
    - Injects bind-mounts of the mock device nodes and environment variables (e.g., `MOCK_TOPOLOGY_CONFIG`) into pods transparently.
    - Supplies container `LD_PRELOAD` shims allowing any container to behave as if a GPU is present.
- The `nvml-mock-nri` plugin is aware of node fabric topology and injects node identity into pods to simulate **ComputeDomain fabric identity**.
- An example `gpu-agent` DaemonSet runs as a workload in the default namespace without GPU requests; injection enables it to run `nvidia-smi` and verify the fabric topology data in its container.
- The NRI plugin excludes injection into its own DaemonSet namespace (`mokka`) and core Kubernetes namespaces (`kube-system`) as a trust boundary.

### Data Flow

1. Cluster topology ConfigMap with overlay information is mounted into the `nvml-mock` DaemonSet pod.
2. The `setup.sh` script copies the topology YAML into `/var/lib/nvml-mock/topology/topology.yaml` on the host.
3. The NRI plugin bind-mounts this topology file into injected containers as `MOCK_TOPOLOGY_CONFIG`.
4. The mock NVML library reads this variable and applies node-specific cluster UUIDs and clique IDs to `nvidia-smi` output dynamically.

### Key Files & Functions

- `docs/demo/node-wide-injection/run.sh` controls cluster creation, image build/load, Helm install with NRI enabled, and workload deployment.
- NRI plugin code (in `pkg/nri/nvml-mock-nri`) hooks kube container creation to inject mounts/env, based on annotations and node name.
- Overlay patching of `clusterUuid` and `cliqueId` in the mock engine applies fabric identity injected by NRI.

```mermaid
flowchart TD
  A["Kind Cluster 'nvml-mock-node-wide-demo'"] --> B["nvml-mock DaemonSet (mock library)"]
  B --> C["Topology ConfigMap -> /var/lib/nvml-mock/topology/topology.yaml"]
  A --> D["nvml-mock-nri DaemonSet (NRI plugin)"]
  D --> E["Intercept Pod creation events"]
  E --> F["Inject overlay mounts + MOCK_TOPOLOGY_CONFIG env"]
  F --> G["Injected workload pods (e.g. gpu-agent)"]
  G --> H["Run 'nvidia-smi' with mock GPUs and fabric identity"]
```

This demo illustrates seamless node-level GPU simulation integration enabling any pod to transparently leverage mock GPUs.

Sources:  
`docs/demo/node-wide-injection/README.md:1-116`  
`docs/demo/node-wide-injection/run.sh`  

---

## 3. ComputeDomain Demo (NVLink Fabric Simulation)

This demonstration showcases the **ComputeDomain fabric simulation** with multi-node NVLink topology overlays, simulating GPU interconnect fabrics dynamically.

### Overview

- A Kind cluster named `nvml-mock-compute-domain` with 1 control-plane and 4 workers is provisioned.
- The Helm chart deploys `nvml-mock` with:
  - The `gb200` GPU profile enabling NVLink5 fabric APIs.
  - A cluster-level topology ConfigMap defining NVLink cliques and fabric clusters.
  - The real NVIDIA `nvidia-imex` daemon injected in **NO GPU** mode with the `imex-nogpu-shim` to establish a live gRPC domain across pods.
- The nodes are split into cliques by topology label (e.g., workers 1-2 clique 0, 3-4 clique 1).
- The demo runs diagnostic checks (`check-fabric`) asserting nodes report correct `cliqueId` and cluster UUID based on the overlay.
- A Helm upgrade can rebind all nodes to a new fabric clique dynamically without rebuilding images.

### Internal Mechanics

- The overlay ConfigMap is mounted inside the daemonset pod and virtual devices override `nvmlDeviceGetGpuFabricInfo()` calls.
- `imex-nogpu-shim` and the fake fabric manager provide real handshake and peer-death detection on gRPC links, emulating a hardware fabric interconnect.
- The fabric info is exposed via the mock NVML shim injected into pods, allowing `nvidia-smi` and fabric tools to query it.

```mermaid
flowchart TD
  A["Kind Cluster 'nvml-mock-compute-domain' (4 workers)"] --> B["nvml-mock Helm DaemonSet"]
  B --> C["Overlay ConfigMap (NVLink topology)"]
  B --> D["Injected imex-nogpu-shim and fake-fabricmanager pods"]
  D --> E["Live gRPC IMEX fabric over pod network"]
  F["Pods with mock NVML"] --> G["nvmlDeviceGetGpuFabricInfo (overlay response)"]
  G --> H["Clique IDs and Cluster UUIDs assigned by topology"]
  H --> I["nvidia-smi reports fabric topology per node"]
```

This demo shows advanced multi-node fabric simulation fully integrated with Kubernetes networking.

Sources:  
`docs/demo/compute-domain/README.md:1-82`  
`docs/demo/compute-domain/run.sh`  

---

## 4. NVSentinel Demo (Thermal Margin Detection and Remediation)

The NVSentinel demo integrates the mock GPUs with NVIDIA's GPU Operator and `NVSentinel` thermal margin detection and remediation system.

### Demo Steps

- A Kind cluster `nvml-mock-nvsentinel` with 1 control-plane and 2 workers is created.
- The cluster deploys:
  - The `nvml-mock` Helm chart with simulated GPUs.
  - The NVIDIA GPU Operator in standalone mode with DCGM exporter.
  - The NVSentinel controller and a sample thermal margin-aware workload.
- One worker's mock GPU is artificially heated past its thermal slowdown threshold by dynamic configuration overrides.
- NVSentinel detects the thermal margin crossing using telemetry from DCGM + metadata-collector slowdown offset.
- NVSentinel responds by cordoning and draining the affected node.
- The sample workload reschedules to the healthy node.
- After simulated cooling, NVSentinel automatically recovers by uncordoning the node without restarting DCGM.

### Integration Points

- Real DCGM metrics are served by the mock NVML shim inside pods.
- NVSentinel uses Kubernetes events and node conditions.
- The demo manifests (`docs/demo/nv-sentinel/`) include MongoDB backend, sample workloads, and GPU operator values.

```mermaid
flowchart LR
  A["Kind Cluster 'nvml-mock-nvsentinel'"] --> B["nvml-mock DaemonSet with Mock GPUs"]
  B --> C["NVIDIA GPU Operator + DCGM Exporter"]
  C --> D["NVSentinel Controller"]
  D --> E["Sample GPU workload"]
  E --> F["Simulate thermal margin breach (MOCK override)"]
  F --> G["NVSentinel detects GPU slowdown via DCGM metrics"]
  G --> H["Node cordoned and drained"]
  H --> I["Workload rescheduled to healthy node"]
  J["Simulate cooling (MOCK override)"] --> K["NVSentinel auto-recovers node (uncordon)"]
```

This demo exemplifies full-stack thermal detection and auto-remediation using `nvml-mock` as the GPU telemetry source.

Sources:  
`docs/demo/nv-sentinel/README.md:1-100`  
`docs/demo/nv-sentinel/run.sh`  

---

## 5. fake-gpu-operator (FGO) Integration Example

This is a full integration scenario combining `nvml-mock` with Run:ai's **fake-gpu-operator** (FGO) to simulate large heterogeneous Kubernetes GPU fleets.

### Why Combine `nvml-mock` and FGO?

| Capability                  | FGO Alone   | nvml-mock Alone | FGO + nvml-mock    |
|-----------------------------|-------------|-----------------|--------------------|
| Kubernetes API GPU simulation| Yes         | Yes             | Yes                |
| KWOK virtual nodes (scale)   | Yes         | No              | Yes                |
| Real NVML API inside pods    | No          | Yes             | Yes                |
| Real `nvidia-smi` output     | Limited     | Yes             | Yes                |
| DCGM Metrics                | Synthetic   | N/A             | Real on mock nodes  |
| GPU Operator validation     | No          | Yes             | Yes                |
| Fractional GPUs             | Yes         | No              | Yes (KWOK nodes)   |
| Large scale testing (>1000 nodes) | Yes   | No              | Yes (KWOK + mock)  |

### Architecture

```mermaid
flowchart LR
  subgraph "Kubernetes Cluster"
    direction TB

    subgraph "Real Nodes (Integration Pool)"
      direction TB
      A["nvml-mock DaemonSet"]
      B["libnvidia-ml.so NVML Shim"]
      C["GPU Operator: Validator + DCGM + GFD"]
    end

    subgraph "KWOK Virtual Nodes (Scale Pool)"
      direction TB
      D["FGO fake device plugin"]
      E["FGO fake GFD controller"]
    end

    F["fake-gpu-operator Controller"]
  end

  F --> A
  F --> D
  A --> B
  A --> C
```

### Setup Steps

1. Create a Kind cluster (`nvml-mock-fgo-demo`).
2. Optionally build and load the local `nvml-mock:demo` image.
3. Install `nvml-mock` Helm chart with `integrations.fakeGpuOperator.enabled=true` to produce GPU profile ConfigMaps consumable by FGO.
4. Install the `fake-gpu-operator` Helm chart with topology mapping pools:
   - **integration** uses backend `mock` (nvml-mock).
   - **scale** uses backend `fake` (FGO's lightweight shim).
5. Verify DaemonSets run on appropriate pools and that GPU profile ConfigMaps exist.
6. Confirm `nvidia-smi` works inside pods on integration nodes.

### GPU Profile ConfigMaps

- Created by `nvml-mock` Helm chart when FGO integration enabled.
- Named like `nvml-mock-profile-a100`, `nvml-mock-profile-h100`, etc.
- FGO watches and consumes these for scheduling topology.

### Customization

- Profile labels can be overridden to fit FGO topology requirements via `values.yaml`.

### Troubleshooting Highlights

- Verify `integrations.fakeGpuOperator.enabled=true` is set.
- Confirm presence and correct labels on ConfigMaps.
- Check `kubectl get pods` shows `nvml-mock` DaemonSet running on integration pool nodes and FGO pods on scale pool nodes.

Sources:  
`docs/integrations/fake-gpu-operator.md:1-200`  
`docs/demo/with-fgo/README.md:1-115`  

---

## Summary of Demo Usage Patterns

| Demo Scenario               | Cluster Name                 | Key Features                                    | Requirements                         |
|----------------------------|-----------------------------|------------------------------------------------|------------------------------------|
| Standalone Demo             | `nvml-mock-demo`            | Basic nvml-mock DaemonSet, fake GPU labels     | Docker, Kind, Helm                  |
| Node-Wide Injection (NRI)  | `nvml-mock-node-wide-demo`  | Ambient injection of mock GPUs via NRI plugin  | Docker, Kind, Helm, containerd NRI |
| ComputeDomain Demo          | `nvml-mock-compute-domain`  | Multi-node NVLink fabric topology, gRPC IMEX   | Docker, Kind, Helm, kubectl, jq    |
| NVSentinel Demo             | `nvml-mock-nvsentinel`      | DCGM + NVSentinel thermal detection & remediation | Docker, Kind, Helm, kubectl        |
| fake-gpu-operator Integration | `nvml-mock-fgo-demo`      | Mixed real nodes + KWOK virtual nodes scale sim| Docker, Kind, Helm, FGO chart       |

Each demo is scripted for reproducibility and verification, providing end-to-end examples bridging real-world Kubernetes GPU stack testing with simulated hardware.

---

# Code Entities and Mapping

### Standalone Demo: `demo.sh`

- `docs/demo/standalone/demo.sh` orchestrates steps: cluster create (lines 69-86), image build (89-92), image load (95-98), helm install (101-113), and validations (124-147).

### NRI Demo Entry Point: `run.sh`

- `docs/demo/node-wide-injection/run.sh` runs cluster setup, image build/load, helm install for `nvml-mock` + `nvml-mock-nri` DaemonSets, workloads deployment and validation.

### ComputeDomain Scenario

- The daemonset mounts a topology ConfigMap `topology.yaml` utilized by the mock NVML shim's `applyTopologyOverlay()` (internal engine function).
- Real `nvidia-imex` daemon run with `--nogpu` is deployed, located in the image layered by the `compute_domain.tiltfile`.

### fake-gpu-operator Integration

- The Helm value `integrations.fakeGpuOperator.enabled=true` enables creation of GPU profile ConfigMaps with the label `run.ai/gpu-profile=true`.
- The fake-gpu-operator controller reads these ConfigMaps and manages node pools with backends set to `mock` or `fake`.

```mermaid
flowchart TB
  subgraph Demo Scenarios "Natural Language Space"
    Standalone["Standalone Demo"]
    NodeWide["Node-Wide Injection Demo"]
    ComputeDomain["ComputeDomain Demo"]
    NVSentinel["NVSentinel Demo"]
    FakeGpuOperator["fake-gpu-operator Integration"]
  end

  subgraph Implementation "Code Entity Space"
    DemoScript["docs/demo/standalone/demo.sh"]
    NRIrun["docs/demo/node-wide-injection/run.sh"]
    ComputeDomainTilt["local/compute-domain/compute_domain.tiltfile"]
    NVSentinelManifests["docs/demo/nv-sentinel/"]
    FGOIntegration["docs/integrations/fake-gpu-operator.md"]

    NvmlMockChart["deployments/nvml-mock/helm/nvml-mock"]
    OverlayConfigMap["Topology ConfigMap / GPU Profile ConfigMaps"]
    NRIPlugin["nvml-mock-nri NRI Plugin"]
    ImexDaemon["nvidia-imex daemon, imex-nogpu-shim"]
  end

  Standalone --> DemoScript
  NodeWide --> NRIrun
  NodeWide --> NRIPlugin
  NodeWide --> OverlayConfigMap
  ComputeDomain --> ComputeDomainTilt
  ComputeDomain --> OverlayConfigMap
  ComputeDomain --> ImexDaemon
  NVSentinel --> NVSentinelManifests
  NVSentinel --> NvmlMockChart
  FakeGpuOperator --> FGOIntegration
  FakeGpuOperator --> NvmlMockChart
  FakeGpuOperator --> OverlayConfigMap
```

---

## Additional Notes

- The Helm chart supports multiple overlays and flags to enable the various integrations like NRI, ComputeDomain, and fake GPU operator via Helm values (handled in local/nvml_mock.tiltfile, invoking Helm with `--set` flags).
- The demos all build or consume a version-tagged `nvml-mock` image, which contains the mock NVML shared library and binary tooling (nvidia-smi).
- Validation scripts often run inside pods launched during demos to verify expected device behavior and configurations.

---

# References to Source Files

- Standalone Demo Script: `docs/demo/standalone/demo.sh:1-148`  
- Standalone Demo Documentation: `docs/demo/standalone/README.md:1-48`  

- Node-Wide Injection Docs: `docs/demo/node-wide-injection/README.md:1-116`  
- Node-Wide Injection Run Script: `docs/demo/node-wide-injection/run.sh`  

- ComputeDomain Demo Docs: `docs/demo/compute-domain/README.md:1-82` (not fully included here)  
- ComputeDomain Tiltfile overlays: `local/compute-domain/compute_domain.tiltfile`  

- NVSentinel Demo Docs: `docs/demo/nv-sentinel/README.md:1-100`  
- NVSentinel Run Script: `docs/demo/nv-sentinel/run.sh`  

- fake-gpu-operator Integration Guide: `docs/integrations/fake-gpu-operator.md:1-200`  
- fake-gpu-operator Demo Docs: `docs/demo/with-fgo/README.md:1-115`  

- Tilt Integration Helpers and Flags (for all scenarios): `Tiltfile:1-133`, `local/nvml_mock.tiltfile:1-154`

---

This page documents practical real-world deployment and integration examples, serving as the first step in experimenting with and extending `k8s-test-infra` GPU simulation capabilities. For deeper internal design details, see the architecture and module documentation pages.

---

# Page: Contributing to k8s-test-infra

# Contributing to k8s-test-infra

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.editorconfig](.editorconfig)
- [.github/CODEOWNERS](.github/CODEOWNERS)
- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [OWNERS](OWNERS)
- [enhancements/README.md](enhancements/README.md)
- [enhancements/template.md](enhancements/template.md)

</details>



## Purpose and Scope

This page provides a high-level guide for contributors to the **k8s-test-infra** project. It outlines the essential workflows, quality requirements, and governance mechanisms designed to maintain code quality and efficient project collaboration.

To keep this overview focused, detailed technical guidelines and governance descriptions are provided in child pages:

- For complete rules on linting, formatting, module management, and enhancement proposals, see [Code Quality Standards](#12.1).
- For explanations of the OWNERS file, code review roles, PR approval workflows, and automation bots, see [Ownership and Review Process](#12.2).

## Contribution Workflow Overview

Contributions follow a typical GitHub pull request workflow enhanced with automated checks and a formal review process. The cycle begins with a developer working locally, proceeds through automated local and CI checks, followed by code review and culminates in automated merge upon approvals and passing tests.

```mermaid
flowchart TD
    DEV["Developer"] --> CLONE["Clone Repository"]
    CLONE --> BRANCH["Create Feature Branch"]
    BRANCH --> CODE["Write Code & Tests"]
    CODE --> LOCAL_CHECKS["Run Local Checks"]
    
    LOCAL_CHECKS --> FMT["make fmt<br/>Format code"]
    LOCAL_CHECKS --> LINT["make lint<br/>golangci-lint"]
    LOCAL_CHECKS --> VENDOR_CHECK["make check-vendor<br/>Verify dependencies"]
    LOCAL_CHECKS --> MOD_CHECK["make check-modules<br/>Verify go.mod sync"]
    
    FMT --> COMMIT["git commit"]
    LINT --> COMMIT
    VENDOR_CHECK --> COMMIT
    MOD_CHECK --> COMMIT
    
    COMMIT --> PUSH["git push"]
    PUSH --> PR["Open Pull Request"]
    
    PR --> CI["Trigger CI Checks"]
    
    CI --> VARS["variables job<br/>Extract Go version"]
    CI --> GOLANG["golang job<br/>Linting & module checks"]
    CI --> SCAN["code-scanning job<br/>CodeQL security scans"]
    
    VARS --> CI_PASS{CI passes?}
    GOLANG --> CI_PASS
    SCAN --> CI_PASS
    
    CI_PASS -->|No| FIX["Fix Issues"]
    FIX --> CODE
    
    CI_PASS -->|Yes| REVIEW["Code Review by Owners"]
    REVIEW --> APPROVED{Approved?}
    
    APPROVED -->|No| FIX
    APPROVED -->|Yes| MERGE["Auto-merge to main"]
    
    MERGE --> DONE["Merge Complete"]
```

This diagram emphasizes the integration of automated format, lint, and module verification checks both locally and in the CI pipeline. Passing these checks is mandatory before maintainers review and approve a change.

**Sources:** [CONTRIBUTING.md:1-130](), [OWNERS:1-9](), [.github/CODEOWNERS:1-18]()

---

## Local Development Environment and Pre-Commit Requirements

To streamline contributions and reduce failures upstream, contributors should ensure their local environment meets the required tool versions and their changes pass automated quality checks before pushing.

| Tool | Purpose | Version or Notes |
|-------|----------|------------------|
| Go | Build & test code | See current Go version management in `deployments/devel/Dockerfile` and `hack/golang-version.sh` |
| `golangci-lint` | Static analysis and linting | Latest recommended version |
| `gofmt` | Go code formatting checker and fixer | Comes standard with Go |
| `git` | Source control | Any recent version |

### Pre-Commit Quality Checks

Run the following Make targets locally to validate your code before committing:

```mermaid
graph LR
    start["Start"] --> FMT["make fmt"]
    FMT --> VERIFY["make verify (check formatting)"]
    VERIFY --> LINT["make lint (run golangci-lint)"]
    LINT --> VENDCHK["make check-vendor (verify vendor sync)"]
    VENDCHK --> MODCHK["make check-modules (verify go.mod sync)"]
    MODCHK --> BUILD["make build (compile binaries)"]
    BUILD --> ready["Ready to Commit"]
```

- `make fmt` formats your Go code automatically.
- `make verify` ensures your code is formatted correctly without making changes.
- `make lint` runs the project's configured Go linter to check code quality.
- `make check-vendor` verifies `go.mod`, `go.sum`, and `vendor/` are in sync.
- `make check-modules` verifies all modules' dependency files are synchronized.
- `make build` compiles needed binaries to ensure code compiles cleanly.

### Managing Dependencies

This project uses vendored Go modules for reproducible builds:

- After modifying dependencies, run `make vendor` to tidy and vendor dependencies.
- Always verify synchronization with `make check-vendor`.
- When working with multiple Go modules, run `make modules` to tidy, vendor, and verify all modules.

Failing to synchronize dependencies properly will cause CI to fail.

**Sources:** [Makefile:27-80](), [CONTRIBUTING.md:30-48]()

---

## Automated CI Checks

Every pull request triggers automated CI workflows, validating formatting, linting, module sync, and security scans.

```mermaid
flowchart LR
   PR["Pull Request"] --> CI["Run basic-checks workflow"]

   CI --> VAR["variables job"]
   VAR --> VAR_OUT["golang_version, SHA"]

   CI --> GOLANG["golang job"]
   GOLANG --> LINT_RUN["golangci-lint"]
   GOLANG --> MOD_CHECK["make check-modules"]

   CI --> SCAN["code-scanning job"]
   SCAN --> CODEQL["CodeQL analysis"]

   LINT_RUN --> PASS["Checks passed"]
   MOD_CHECK --> PASS
   CODEQL --> PASS

   PASS --> REVIEW["Enable review"]
```

This ensures consistent quality standards across all contributions:

- Linting and formatting are verified in the `golang` job.
- Dependency files are validated for consistency.
- CodeQL static analysis guards against security issues.

All checks must pass before merging is allowed.

**Sources:** [.github/workflows/basic-checks.yaml (implied)](), [Makefile:75-79](), [CONTRIBUTING.md:75-79]()

---

## Code Review and Project Governance

The project enforces a structured review process governed by `OWNERS` and `CODEOWNERS` files.

### Maintainers and Roles

- Maintainers serve as both reviewers and approvers.
- Current maintainers include:
  - `ArangoGutierrez`
  - `elezar`
  - (Plus contributors with review access listed in OWNERS)

### Review Workflow

```mermaid
stateDiagram-v2
    [*] --> PR_Created
    PR_Created --> CI_Checking
    CI_Checking --> CI_Passed: pass
    CI_Checking --> CI_Failed: fail

    CI_Failed --> Fix_Changes
    Fix_Changes --> CI_Checking

    CI_Passed --> Reviewer_Review
    Reviewer_Review --> Changes_Requested: issues found
    Reviewer_Review --> LGTM: approved

    Changes_Requested --> Fix_Changes

    LGTM --> Approver_Review
    Approver_Review --> Approved
    Approved --> Merged
    Merged --> [*]
```

- Pull requests must pass all CI checks before review.
- Reviewers examine code changes and either request changes or approve (LGTM).
- Approvers have authority to merge after approvals.
- The project also employs the `copy-pr-bot` for CLA and license compliance automation.

For full detail on reviewer roles, approval requirements, and automation, see [Ownership and Review Process](#12.2).

**Sources:** [OWNERS:1-9](), [.github/CODEOWNERS:1-18]()

---

## Relationship of Topics in Contribution Process

```mermaid
graph TD
    Code_Quality_Standards["Code Quality Standards<br/>(Linting, Format, Modules)"] --> Contribution_Workflow["Contribution Workflow"]
    Ownership_Process["Ownership and Review Process"] --> Contribution_Workflow
    Contribution_Workflow --> Local_Dev_Environment["Local Development Setup & Pre-Commit Checks"]
    Contribution_Workflow --> CI_Automation["Automated CI Checks"]
    CI_Automation --> Code_Review_Process["Code Review and Approval"]
    Code_Review_Process --> Merge["Merge to main"]

    Local_Dev_Environment -. improves -.> CI_Automation
    Code_Quality_Standards -. enforced by .-> CI_Automation
    Ownership_Process -. governs .-> Code_Review_Process
```

This diagram illustrates how:

- Code quality standards underpin all automated checks.
- The ownership and review process govern human approvals.
- Local developer tools and scripts help ensure compliance before pushing.
- The overall contribution workflow connects these elements into a consistent path from writing code to merging it.

---

# Summary

Contributing to **k8s-test-infra** requires adherence to a rigorous process designed to ensure code stability and maintainability:

- Follow prescribed code quality standards for linting, formatting, and dependency management.
- Use provided Makefile targets for local code validation.
- Submit pull requests that trigger automated CI pipelines validating correctness and security.
- Collaborate with maintainers for code reviews and approvals using the defined OWNERs governance.
- Consult child pages [Code Quality Standards](#12.1) and [Ownership and Review Process](#12.2) for in-depth policies.

By reliably following this process, contributors help maintain the project’s integrity and accelerate integration of their improvements.

---

**Sources:**

- [CONTRIBUTING.md:1-130]()
- [OWNERS:1-9]()
- [.github/CODEOWNERS:1-18]()
- [Makefile:27-80]()
- [enhancements/template.md:1-124]() (for context on enhancement proposals referenced in child pages)

---

# Page: Code Quality Standards

# Code Quality Standards

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.golangci.yml](.golangci.yml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [enhancements/README.md](enhancements/README.md)
- [enhancements/template.md](enhancements/template.md)
- [tests/e2e/go/report_skips_test.go](tests/e2e/go/report_skips_test.go)

</details>



## Purpose and Scope

This document defines the code quality standards enforced in the `k8s-test-infra` repository. It details the linting rules, formatting requirements, module management practices, and describes the enhancement proposal (MEP) process used for introducing substantive changes to the codebase.

For contributor guidelines on review processes and ownership, see [Ownership and Review Process](#12.2). For CI/CD pipeline integration of code quality checks, refer to [CI/CD Pipeline](#4).

---

## Code Formatting Standards

The project enforces consistent Go code formatting using the standard Go tool `gofmt`. Every `.go` file committed to the repository must be formatted accordingly.

### Formatting Targets

Formatting automation is provided through the Makefile with two key targets:

| Target          | Description                           | Behavior                                     |
|-----------------|-----------------------------------|----------------------------------------------|
| `make fmt`      | Format Go source files              | Automatically runs `gofmt -w -l` on all `.go` files excluding `vendor/` |
| `make verify`   | Verify formatting                   | Checks for formatting issues without modifying files; exits with error if issues found |

The `fmt` target is implemented as:

```makefile
fmt:
	@$(GO_FMT) -w -l $$(find . -name '*.go')
```

and the `verify` target as:

```makefile
verify:
	@out=`$(GO_FMT) -w -l -d $$(find . -name '*.go')`; \
	if [ -n "$$out" ]; then \
	    echo "$$out"; \
	    exit 1; \
	fi
```

Implementation details:

- `GO_FMT` defaults to `gofmt`
- The command uses `find` to recursively select `.go` files excluding the `vendor/` directory ([Makefile:14-15,31-39]())

Enforcing `gofmt` maintains uniform syntax and style consistency across the codebase, facilitating easier code comprehension and reducing trivial diffs.

**Sources:** [Makefile:14-15](), [Makefile:31-39]()

---

## Linting with golangci-lint

To ensure higher code quality, the repository employs `golangci-lint`, a unified linter aggregator for Go.

### Local Linting

Developers can run:

```bash
make lint
```

which triggers:

```makefile
lint:
	golangci-lint run ./...
```

This runs all enabled linters on all Go packages within the repository recursively ([Makefile:41-42]()).

### Linting Configuration and Rules

The linting behavior is driven by `.golangci.yml` configuration:

- Includes build tags `e2e` and `integration` to lint test-only code guarded by those tags.
- Enables nearly all `staticcheck` checks except stylistic ones (`ST1000`, `ST1003`, and the entire `QF*` category).
- Provides explicit exclusions for known false positives in Ginkgo test helper files to allow dot-imports (`ST1001` exemption specifically for test suite files) ([.golangci.yml:15-61]()).

### CI Integration for Linting

Linting is enforced within the CI pipeline on every Pull Request and push. The process includes:

```mermaid
flowchart TD
    PR["Pull Request / Push Event"]
    Vars["variables job"]
    GoLint["golang job: Lint step"]
    Setup["actions/setup-go"]
    LintAction["golangci/golangci-lint-action"]
    CheckMods["make check-modules"]

    PR --> Vars
    Vars -->|"golang_version output"| GoLint
    GoLint --> Setup
    Setup --> LintAction
    LintAction --> CheckMods

    LintAction -.->|"Configuration"| Config["version: latest<br/>args: -v --timeout 5m<br/>skip-cache: true"]
```

- The workflow installs the Go version extracted from the `deployments/devel/Dockerfile` via `hack/golang-version.sh`.
- Executes `golangci-lint-action` with verbose output and a 5-minute timeout.
- Runs `make check-modules` after lint to verify module consistency.
([.github/workflows/golang.yaml:17-45]())

### Summary of Linting Parameters

| Parameter    | Value           | Description                    |
|--------------|-----------------|------------------------------|
| version      | `latest`        | Always runs latest golangci-lint |
| args         | `-v --timeout 5m` | Verbose and 5-minute timeout  |
| skip-cache   | `true`          | Disables caching to ensure fresh analysis |

**Sources:** [.golangci.yml:15-61](), [Makefile:41-42](), [.github/workflows/golang.yaml:17-45]()

---

## Module Management

To ensure dependency consistency and reproducible builds, the project applies strict module management workflows involving go modules and vendoring.

### Module Management Workflow Overview

```mermaid
flowchart LR
    subgraph "Local Development"
        ModTidy["modules target"]
        Tidy[".mod-tidy<br/>go mod tidy"]
        Vendor[".mod-vendor<br/>go mod vendor"]
        Verify[".mod-verify<br/>go mod verify"]
    end

    subgraph "CI Verification"
        CheckMods["check-modules target"]
        DiffMod["git diff go.mod go.sum"]
        DiffVendor["git diff vendor/"]
    end

    ModTidy --> Tidy
    Tidy --> Vendor
    Vendor --> Verify

    CheckMods --> DiffMod
    CheckMods --> DiffVendor

    Verify -.->|"If clean"| CheckMods
```

### Makefile Module Targets

#### `vendor` target

Executes a full module refresh:

```makefile
vendor:
	go mod tidy
	go mod vendor
	go mod verify
```

- Runs `go mod tidy` to add missing and remove unused dependencies
- Runs `go mod vendor` to vendor dependencies into `vendor/`
- Runs `go mod verify` to verify checksum integrity ([Makefile:44-47]())

#### `modules` target

Manages multi-module scenarios by processing all `go.mod` files under the repo excluding testdata and third_party folders. It aggregates three sub-tasks:

- `.mod-tidy`: Tidies all relevant modules
- `.mod-vendor`: Vendors dependencies
- `.mod-verify`: Verifies module integrity

([Makefile:52-73]())

#### `check-vendor` target

Verifies the vendored dependencies are up-to-date with declared modules:

```makefile
check-vendor: vendor
	git diff --quiet HEAD -- go.mod go.sum vendor
```

- If any differences occur, it exits with an error, requiring sync ([Makefile:49-50]())

#### `check-modules` target

Performs comprehensive verification that modules and vendored dependencies are synchronized:

```makefile
check-modules: modules
	@echo "- Checking if go.mod and go.sum are in sync..."
	@git diff --exit-code -- $$(find . -name go.mod -name go.sum)
	@echo "- Checking if the go mod vendor dir is in sync..."
	@git diff --exit-code -- $$(find . -name vendor)
```

- Runs the full `modules` pipeline
- Checks for uncommitted changes in go.mod/go.sum and vendor folders ([Makefile:75-79]())

### CI Enforcement of Module Consistency

The GitHub Actions golang workflow runs:

```yaml
- name: Check golang modules
  run: |
    make check-modules
```

Ensuring guaranteed module and vendoring consistency on every run ([.github/workflows/golang.yaml:43-45]()).

**Sources:** [Makefile:44-79](), [.github/workflows/golang.yaml:43-45]()

---

## Enhancement Proposal (MEP) Process

Substantial changes in architecture, features, or public APIs must follow the "MEP" (Mokka Enhancement Proposal) process. This formalized approach ensures informed design decisions and consensus before implementation.

### MEP Overview

- Adapted from Kubernetes KEP process
- Applies to major cross-cutting refactors, new top-level components, API changes, or adding new dependencies/platform targets.
- Small fixes or incremental features do not require MEPs; contributors open issues or PRs directly.

### MEP Workflow

```mermaid
flowchart TD
    Start["Start: Idea for Significant Change"]
    CopyTemplate["Copy `template.md` to `meps/NNNN-short-title.md`"]
    Draft["Fill Summary, Motivation, Goals"]
    PR["Open MEP Pull Request (tag: kind/mep)"]
    Discuss["Community Review and Discussion"]
    Iterate["Iterate Design Details, Risks, Alternatives"]
    Approval["Maintainer Approval"]
    Merge["Merge MEP"]
    Implement["Implement in Codebase with Reference to MEP"]

    Start --> CopyTemplate --> Draft --> PR --> Discuss --> Iterate --> Approval --> Merge --> Implement
```

- MEP files reside under `enhancements/meps/`
- The canonical template is at `enhancements/template.md`
- Superseded or withdrawn MEPs remain in history with status updated ([enhancements/README.md]())

### Expectations

- MEPs document motivation, goals, design details, risks, and alternatives.
- MEP number (`NNNN`) is assigned consecutively.
- MEPs provide a record of intent; PRs for implementation link to the MEP.

**Sources:** [enhancements/template.md](), [enhancements/README.md]()

---

## Summary Table: Code Quality Enforcement

| Standard            | Local Command         | CI Enforcement                        | Configuration/Notes              |
|---------------------|-----------------------|-------------------------------------|-----------------------------|
| Code Formatting     | `make fmt` / `make verify` | Not directly enforced, failure on upstream | `gofmt` defaults           |
| Linting            | `make lint`            | `.github/workflows/golang.yaml`     | `golangci-lint` with `.golangci.yml` |
| Module Management   | `make vendor` / `make check-modules` | `.github/workflows/golang.yaml`     | `go.mod`, `go.sum`, `vendor/`  |
| Enhancement Proposals| N/A                    | N/A                                | MEPs in `enhancements/meps/`     |

---

## Diagrams Associating Code Entities to Concepts

### Diagram 1: Linting Pipeline Entities

```mermaid
flowchart LR
    PR["GitHub PR / Push Event"]
    VariablesJob["variables.yaml job"]
    GolangJob["golang.yaml job"]
    SetupGo["actions/setup-go@v6"]
    LintStep["golangci-lint-action@v9"]
    CheckModulesStep["make check-modules"]

    PR --> VariablesJob
    VariablesJob --> GolangJob
    GolangJob --> SetupGo
    SetupGo --> LintStep
    LintStep --> CheckModulesStep
```

Shows the CI step sequence triggered for linting and module verification using GitHub workflow files.

### Diagram 2: Module Targets in Makefile and Their Relations

```mermaid
flowchart TD
    modules["modules target"]
    modTidy[".mod-tidy target"]
    modVendor[".mod-vendor target"]
    modVerify[".mod-verify target"]
    vendor["vendor target"]
    checkVendor["check-vendor target"]
    checkModules["check-modules target"]
    gitDiffMod["git diff go.mod go.sum"]
    gitDiffVendor["git diff vendor/"]

    modules --> modTidy
    modules --> modVendor
    modules --> modVerify

    vendor -->|runs| modTidy
    vendor -->|runs| modVendor
    vendor -->|runs| modVerify

    checkVendor --> vendor
    checkVendor --> gitDiffMod
    checkVendor --> gitDiffVendor

    checkModules --> modules
    checkModules --> gitDiffMod
    checkModules --> gitDiffVendor
```

Shows the key module management targets in Makefile controlling vendoring and verification.

---

# End of Document

**Sources:**  
[Makefile:14-15,31-50,52-79](), [.golangci.yml:15-61](), [.github/workflows/golang.yaml:17-45](), [enhancements/template.md](), [enhancements/README.md](), [Makefile:41-42]()

---

# Page: Ownership and Review Process

# Ownership and Review Process

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.editorconfig](.editorconfig)
- [.github/CODEOWNERS](.github/CODEOWNERS)
- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [.github/copy-pr-bot.yaml](.github/copy-pr-bot.yaml)
- [OWNERS](OWNERS)

</details>



## Purpose and Scope

This document details the ownership and code review process within the **k8s-test-infra** repository. It explains the role and structure of the `OWNERS` file, how it relates to GitHub's `CODEOWNERS` configuration, the delineation of reviewer and approver roles, the pull request (PR) approval workflow, and the usage of the `copy-pr-bot` for PR management.

The aim is to clarify responsibilities and the flow of code review and merging to ensure quality and consistency.

---

## OWNERS File Overview

The `OWNERS` file is located at the root of the repository and follows the Kubernetes community's OWNERS format as documented at https://go.k8s.io/owners. It specifies the sets of project members who have permission to:

- **Review**: Provide comments and approve code changes
- **Approve**: Provide final approval to merge pull requests

### Current OWNERS File Content

```yaml
# See the OWNERS docs at https://go.k8s.io/owners

reviewers:
  - ArangoGutierrez
  - elezar
approvers:
  - ArangoGutierrez
  - elezar
```

This configuration reflects that two individuals, `ArangoGutierrez` and `elezar`, are both reviewers and approvers, enabling them to review code and grant final merge approval [OWNERS:1-9]().

---

## CODEOWNERS File Overview

The repository also includes a `.github/CODEOWNERS` file which is used by GitHub to automatically assign reviewers on pull requests based on the files modified. It defines ownership mappings covering the whole repository, with the default owner assigned as `@ArangoGutierrez`.

### CODEOWNERS Highlights

```
# Default owners for everything
* @ArangoGutierrez

# Mock NVML library
/pkg/gpu/mocknvml/ @ArangoGutierrez

# Helm chart
/deployments/nvml-mock/ @ArangoGutierrez

# CI workflows
/.github/workflows/ @ArangoGutierrez

# E2E tests
/tests/e2e/ @ArangoGutierrez
```

The CODEOWNERS file enables GitHub's auto-assignment of reviewers, improving PR triaging efficiency by suggesting appropriate owners based on the changed files [/.github/CODEOWNERS:1-18]().

---

## Ownership Model and Roles

The ownership model distinguishes **reviewers** and **approvers** as defined in the `OWNERS` file:

| Role      | Responsibilities                                                                                         |
|-----------|---------------------------------------------------------------------------------------------------------|
| Reviewer  | Review and critique code changes, ensuring adherence to quality standards, testing, and documentation  |
| Approver  | Review and approve changes for merge, with authority to make final merge decisions                     |

Reviewers help maintain code quality, while approvers have the additional authority to merge PRs. In this repository, all current approvers are also reviewers.

### Ownership and Review Flow

```mermaid
graph TB
    OWNERS_FILE["OWNERS File (root)"]
    REVIEWERS["Reviewers (ArangoGutierrez, elezar)"]
    APPROVERS["Approvers (ArangoGutierrez, elezar)"]

    OWNERS_FILE --> REVIEWERS
    OWNERS_FILE --> APPROVERS

    PR["Pull Request"]
    REVIEW["Code Review"]
    APPROVAL["Approval for Merge"]

    PR --> REVIEW
    REVIEWERS -.->|Provide feedback| REVIEW
    REVIEW --> APPROVAL
    APPROVERS -.->|Final approval| APPROVAL
```

**Diagram: Mapping `OWNERS` file roles to the review process**

This shows how the `OWNERS` file defines the role sets that participate in PR review and approval [OWNERS:3-9]().

---

## Pull Request Review and Approval Workflow

The review workflow for PRs involves several steps, including automated checks and human interactions:

```mermaid
sequenceDiagram
    participant Contributor
    participant GitHub as "GitHub PR"
    participant CI as "CI/CD Pipeline"
    participant Reviewer as "Reviewer"
    participant Approver as "Approver"

    Contributor->>GitHub: Create Pull Request
    GitHub->>CI: Trigger automated checks
    CI->>GitHub: Report status (linting, tests, scanning)

    Reviewer->>GitHub: Review PR
    alt Changes requested
        Contributor->>GitHub: Push updates
        GitHub->>CI: Re-run checks
        CI->>GitHub: Update status
        Reviewer->>GitHub: Re-review
    end

    Reviewer->>GitHub: Approve PR
    Approver->>GitHub: Perform final review
    Approver->>GitHub: Approve merge

    GitHub->>GitHub: Merge PR
```

**Diagram: Pull request lifecycle with automated and manual validation**

The workflow contains an iterative review loop until reviewers are satisfied. Approvers conduct the final merge decision. Automated CI jobs ensure basic quality before human approval proceeds [OWNERS:3-10]().

---

## Code Review Process

### Review Checklist

Reviewers assess PRs against these key criteria:

| Aspect          | Description                                             |
|-----------------|---------------------------------------------------------|
| Build           | Code compiles successfully (`make build`)               |
| Tests           | All tests pass and new features are covered             |
| Lint            | `golangci-lint` reports no errors                        |
| Formatting      | Code formatted per `gofmt`                               |
| Modules         | Dependency checks and `go.mod` / `go.sum` synced        |
| Documentation   | Public APIs and complex logic properly documented        |
| Security        | CodeQL and security analyses show no issues              |

### Reviewer Interactions

Reviewers use GitHub’s PR UI to interact:

- **Comment**: Suggest improvements or clarifications without blocking merge
- **Request Changes**: Block merging pending fixes
- **Approve**: Indicate readiness for merge consideration

Reviewers may iterate comments and change requests until the PR meets standards.

**Sources:** [OWNERS:3-10]().

---

## Integration with CI/CD Pipeline

Automatic verification runs in the CI pipeline (GitHub Actions) before reviews:

```mermaid
graph LR
    subgraph "CI Pipeline"
        BASIC["basic-checks (lint, tests)"]
        SCAN["CodeQL Scan"]
        GOLANG["golangci-lint & make check-modules"]
    end
    subgraph "Review and Merge"
        REVIEWER["Reviewers"]
        APPROVER["Approvers"]
        MERGE["Merge PR"]
    end

    BASIC --> SCAN
    BASIC --> GOLANG

    GOLANG -.-> REVIEWER
    SCAN -.-> REVIEWER

    REVIEWER --> APPROVER
    APPROVER --> MERGE

    GOLANG --> MERGE
    SCAN --> MERGE
```

Automated checks must pass before human review proceeds. Both reviewers and approvers must ultimately approve for merge to occur [OWNERS:3-10]().

---

## copy-pr-bot Configuration

The repository uses the `copy-pr-bot` GitHub app configured via `.github/copy-pr-bot.yaml`:

```yaml
enabled: true
```

This enables automated PR interactions such as cloning PRs across branches to reduce manual copy/paste errors in multi-branch workflows. The simple enablement configuration indicates it's active repository-wide [/.github/copy-pr-bot.yaml:1-4]().

---

## Summary

The ownership and review process for **k8s-test-infra** is driven by Kubernetes-style `OWNERS` file permissions, augmented with GitHub `CODEOWNERS` for automated reviewer assignment. Pull requests undergo an integrated process of automated checks and manual review:

- The `OWNERS` file defines project reviewers and approvers
- The `CODEOWNERS` file supports GitHub's automatic reviewer assignment by file paths
- PRs trigger CI verification of linting, testing, and code scanning
- Reviewers provide feedback and can request changes
- Approvers grant final merge approval
- The `copy-pr-bot` app assists with PR management automation

This process ensures high code quality, consistency, and effective project governance.

---

# Appendix: Key Relevant Files

| File Path                 | Description                           |
|---------------------------|-------------------------------------|
| `OWNERS`                  | Defines reviewers and approvers     |
| `.github/CODEOWNERS`      | Maps files/directories to owners for auto-review-assignment |
| `.github/copy-pr-bot.yaml`| Configuration for the copy-pr-bot automation app |

---

# Diagrams Relating Natural Language Concepts to Code Entities

```mermaid
graph LR
    OWNERS_FILE["`OWNERS` file<br/>(root)"]
    REVIEWERS_LIST["reviewers:<br/>- ArangoGutierrez<br/>- elezar"]
    APPROVERS_LIST["approvers:<br/>- ArangoGutierrez<br/>- elezar"]
    PR["Pull Request"]
    REVIEW["Review Phase<br/>(GitHub UI)"]
    APPROVAL["Approval Phase<br/>(GitHub UI)"]
    CI["CI/CD Pipeline<br/>(GitHub Actions)"]

    OWNERS_FILE --> REVIEWERS_LIST
    OWNERS_FILE --> APPROVERS_LIST
    PR --> CI
    PR --> REVIEW
    REVIEWERS_LIST -.->|performs| REVIEW
    REVIEW --> APPROVAL
    APPROVERS_LIST -.->|performs| APPROVAL
```

**Diagram: Mapping `OWNERS` file role definitions to PR and CI processes**

```mermaid
sequenceDiagram
    participant C as Contributor
    participant G as GitHub
    participant CI as CI Pipeline
    participant R as Reviewer
    participant A as Approver

    C->>G: Submit PR
    G->>CI: Trigger automated checks (golangci-lint, tests, CodeQL)
    CI->>G: Report status (pass/fail)
    R->>G: Review code and provide feedback
    alt Requested changes
        C->>G: Push fixes
        G->>CI: Rerun checks
        CI->>G: Update status
        R->>G: Re-review
    end
    R->>G: Approve PR
    A->>G: Final review and approve
    G->>G: Merge PR
```

**Diagram: Detailed sequence of a pull request lifecycle**

---

**Sources:**

- [OWNERS:1-9]()
- [.github/CODEOWNERS:1-18]()
- [.github/copy-pr-bot.yaml:1-4]()

---

# Page: Glossary

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [cmd/fake-imex/ctl/main.go](cmd/fake-imex/ctl/main.go)
- [cmd/fake-imex/daemon/main.go](cmd/fake-imex/daemon/main.go)
- [cmd/fake-imex/integration_test.go](cmd/fake-imex/integration_test.go)
- [deployments/nvml-mock/Dockerfile.compute-domain-daemon](deployments/nvml-mock/Dockerfile.compute-domain-daemon)
- [deployments/nvml-mock/helm/nvml-mock/README.md](deployments/nvml-mock/helm/nvml-mock/README.md)
- [deployments/nvml-mock/helm/nvml-mock/templates/daemonset.yaml](deployments/nvml-mock/helm/nvml-mock/templates/daemonset.yaml)
- [deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap](deployments/nvml-mock/helm/nvml-mock/tests/__snapshot__/daemonset_test.yaml.snap)
- [deployments/nvml-mock/helm/nvml-mock/tests/daemonset_test.yaml](deployments/nvml-mock/helm/nvml-mock/tests/daemonset_test.yaml)
- [deployments/nvml-mock/helm/nvml-mock/values.schema.json](deployments/nvml-mock/helm/nvml-mock/values.schema.json)
- [deployments/nvml-mock/helm/nvml-mock/values.yaml](deployments/nvml-mock/helm/nvml-mock/values.yaml)
- [deployments/nvml-mock/scripts/cleanup.sh](deployments/nvml-mock/scripts/cleanup.sh)
- [deployments/nvml-mock/scripts/setup.sh](deployments/nvml-mock/scripts/setup.sh)
- [docs/README.md](docs/README.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/configuration.md](docs/configuration.md)
- [docs/demo/compute-domain/README.md](docs/demo/compute-domain/README.md)
- [docs/demo/compute-domain/run.sh](docs/demo/compute-domain/run.sh)
- [docs/demo/kind.yaml](docs/demo/kind.yaml)
- [docs/demo/with-fgo/README.md](docs/demo/with-fgo/README.md)
- [docs/examples.md](docs/examples.md)
- [docs/integrations/fake-gpu-operator.md](docs/integrations/fake-gpu-operator.md)
- [docs/quickstart.md](docs/quickstart.md)
- [pkg/gpu/mocknvml/bridge/device.go](pkg/gpu/mocknvml/bridge/device.go)
- [pkg/gpu/mocknvml/bridge/helpers.go](pkg/gpu/mocknvml/bridge/helpers.go)
- [pkg/gpu/mocknvml/bridge/nvml_types.h](pkg/gpu/mocknvml/bridge/nvml_types.h)
- [pkg/gpu/mocknvml/bridge/stubs_generated.go](pkg/gpu/mocknvml/bridge/stubs_generated.go)
- [pkg/gpu/mocknvml/engine/config.go](pkg/gpu/mocknvml/engine/config.go)
- [pkg/gpu/mocknvml/engine/config_types.go](pkg/gpu/mocknvml/engine/config_types.go)
- [pkg/gpu/mocknvml/engine/device.go](pkg/gpu/mocknvml/engine/device.go)
- [pkg/gpu/mocknvml/engine/device_test.go](pkg/gpu/mocknvml/engine/device_test.go)
- [pkg/gpu/mocknvml/engine/nvlink_error_injection_test.go](pkg/gpu/mocknvml/engine/nvlink_error_injection_test.go)
- [pkg/gpu/mocknvml/engine/nvlink_fields.go](pkg/gpu/mocknvml/engine/nvlink_fields.go)
- [pkg/gpu/mocknvml/engine/version.go](pkg/gpu/mocknvml/engine/version.go)
- [pkg/gpu/mocknvml/engine/version_test.go](pkg/gpu/mocknvml/engine/version_test.go)
- [pkg/imexcoord/coord.go](pkg/imexcoord/coord.go)
- [tests/e2e/device-plugin-mock.yaml](tests/e2e/device-plugin-mock.yaml)
- [tests/e2e/kind-compute-domain-config.yaml](tests/e2e/kind-compute-domain-config.yaml)
- [tests/e2e/kind-dra-config.yaml](tests/e2e/kind-dra-config.yaml)

</details>



This glossary defines key terms, jargon, abbreviations, and domain concepts specific to the `k8s-test-infra` codebase, with a primary focus on the `nvml-mock` GPU simulation system, Kubernetes integration, testing subsystems, and Helm deployment aspects. Each entry references relevant code locations for deeper inspection and understanding. This page is designed to help an onboarding engineer quickly grasp the technical vocabulary and architecture unique to this repository.

---

## NVML (NVIDIA Management Library) Mock

The core GPU simulation subsystem that implements a mock NVML shared library (`libnvidia-ml.so`) using CGo to simulate NVIDIA GPU behavior on nodes without physical GPUs.

- **Role:** Provides a complete, versioned NVIDIA GPU driver interface that reports detailed GPU properties and telemetry based on YAML-configured profiles.
- **Implementation:** The mock NVML library is implemented with bridge files exporting NVML functions (`pkg/gpu/mocknvml/bridge/device.go`) which delegate to the Go-based engine backend (`pkg/gpu/mocknvml/engine/device.go`).
- **Engine:** The simulation engine manages GPU device state, configurations, metrics sampling, and failure injections.
- **Dynamic metrics:** Support opt-in time-varying GPU telemetry (temperature, power, utilization).
- **Failure Injection:** Supports simulating GPU failure modes such as lost device or ECC errors.
- **Profiles:** YAML-based GPU profiles (e.g., a100, h100, b200, gb200, t4) define the GPU capabilities and topology.
- **Runtime control:** Uses `nvml-mock-ctl` CLI for live device state overrides.
- **Relevant files:**  
  - Engine and device simulation: `pkg/gpu/mocknvml/engine/device.go` [pkg/gpu/mocknvml/engine/device.go:1-178]()  
  - Bridge implementations exporting NVML API: `pkg/gpu/mocknvml/bridge/device.go` [pkg/gpu/mocknvml/bridge/device.go:14-194]()  
  - Configuration details in YAML and engine config overlays.  

---

## ConfigurableDevice

A key abstraction in the mock NVML engine representing a single simulative GPU device. This type wraps a base DGX A100 mock device and overlays YAML-configured parameters for detailed simulation.

- **Responsibilities:**  
  - Holds static device data (name, UUID, PCI info), dynamic metrics, failure injection, and topology info (NVLink, PCIe).  
  - Manages atomic application of runtime configuration overrides for safe concurrent access.  
  - Provides simulated responses to NVML queries such as memory info, clock rates, performance states, and process lists.
- **Lifecycle:** Created per GPU index on engine startup and is initialized with base mock device parameters plus any YAML overrides.
- **Concurrency:** Uses mutex locking and atomic pointers to manage refreshes of config overrides, failure injectors, and dynamic metrics simulators.
- **References:**  
  - `ConfigurableDevice` struct and methods: [pkg/gpu/mocknvml/engine/device.go:43-178]()  
  - Unit tests detailing expected behavior and concurrency: [pkg/gpu/mocknvml/engine/device_test.go:24-182]()  
- **Data flow snippet:**  
  - On NVML API call → fetch `ConfigurableDevice` by handle → call `cfg()` to get runtime config (refresh if needed) → respond with configured or computed data → apply failure injection if enabled.  

---

## Engine Singleton

The core singleton holding global NVML mock state, device lists, and configuration.

- **Responsibilities:**  
  - Initialization and shutdown of mock devices.  
  - Lookup device handles by index, UUID, or PCI bus ID.  
  - Manage global config, device overrides, and topology overlays.  
  - Serve NVML API calls at the bridge layer.
- **Flow:**  
  - The C exported NVML functions delegate to `engine.GetEngine()` which routes to devices or global state.
- **Implementation files:**  
  - Engine construction and retrieval: `pkg/gpu/mocknvml/engine/device.go` (not fully shown in excerpts but central to device management).  
  - Usage in bridge layer: `pkg/gpu/mocknvml/bridge/device.go` [pkg/gpu/mocknvml/bridge/device.go:115-197]().  

---

## Helm Chart `nvml-mock`

A Helm chart deployment system to install the mock NVML infrastructure into Kubernetes clusters.

- **Components deployed:**  
  - DaemonSet that runs an `nvml-mock` container on every node.  
  - ConfigMap with GPU profile YAML config (e.g., `/etc/nvml-mock/config.yaml`).  
  - Volume mounts for device nodes, config overlays, and fake PCI/IB sysfs trees.  
  - Node labels such as `nvidia.com/gpu.present=true` set directly by setup scripts, plus NFD feature files enabling PCI vendor presence labels.  
  - Optional containerd NRI plugin for automatic LD_PRELOAD injection into all containers on the node.
- **Configuration parameters (from `values.yaml`):**  
  - `gpu.profile` (e.g. "a100", "h100") to select GPU profile.  
  - `gpu.count` to override the number of GPUs exposed.  
  - `dynamicMetrics.enabled` to enable simulated telemetry.  
  - `failureInjection.enabled` to enable GPU fault simulation.  
  - `nri.enabled` to toggle the node-wide containerd NRI plugin.  
- **Workflow:**  
  - Helm installs DaemonSet → pods run `setup.sh` to create mock driver root + device nodes + CDI spec → pods expose mock NVML -> release config changes roll out with annotation checksum patch for reload.  
- **Relevant files:**  
  - Chart README with detailed usage: `deployments/nvml-mock/helm/nvml-mock/README.md` [deployments/nvml-mock/helm/nvml-mock/README.md:1-229]()  
  - Default values and configuration schema: `deployments/nvml-mock/helm/nvml-mock/values.yaml` [deployments/nvml-mock/helm/nvml-mock/values.yaml:1-138]()  
  - DaemonSet template YAML: `deployments/nvml-mock/helm/nvml-mock/templates/daemonset.yaml` [deployments/nvml-mock/helm/nvml-mock/templates/daemonset.yaml:1-147]()  
  - Setup script run as container entrypoint: `deployments/nvml-mock/scripts/setup.sh` [deployments/nvml-mock/scripts/setup.sh:1-240]()  

---

## Node Feature Discovery (NFD) Integration

- **Concept:** The mock installs a feature file (`nvml-mock.features`) into an NFD-observed directory (usually `/etc/kubernetes/node-feature-discovery/features.d`) to cause NFD to label nodes with GPU presence features.
- **Labeling:** The key provided is `feature.node.kubernetes.io/pci-10de.present=true`, indicating NVIDIA PCI vendor presence.
- **Direct labeling:** Additionally, the DaemonSet writes label `nvidia.com/gpu.present=true` directly via `kubectl label` command in the setup script.
- **Gate control:** NFD feature file presence is gated by the environment variable `MOCK_NFD_PCI_LABEL`, toggled `on` or `off`.
- **Relevant files:**  
  - NFD feature file setup in Helm DaemonSet environment: [deployments/nvml-mock/helm/nvml-mock/templates/daemonset.yaml:72-83]()  
  - Setup script logic for NFD file and labels: [deployments/nvml-mock/scripts/setup.sh:160-200]()  
  - Explanation in Helm Chart README section on Node labels: [deployments/nvml-mock/helm/nvml-mock/README.md:10-20]()  

---

## Dynamic Metrics Simulator

A subcomponent of the mock NVML engine that generates time-varying statistics such as GPU utilization, temperature, and power draw.

- **Purpose:** Enables realistic telemetry over time rather than static fixed values for metrics.
- **Usage:** Enabled on a per-device basis via YAML configuration entries under `dynamicMetrics`.
- **Implementation:** Atomic swap held pointers to metric simulators updated on config refreshes.
- **Effect:** Mock NVML API calls querying metrics read from the dynamic simulator to produce evolving values.
- **References:**  
  - `ConfigurableDevice` dynamic metrics stored in `atomic.Pointer[dynamicMetricsSimulator]` field [pkg/gpu/mocknvml/engine/device.go:65-69]()  
  - Enabled at device creation if config `DynamicMetrics` present [pkg/gpu/mocknvml/engine/device.go:136-139]()  

---

## Failure Injector

A mechanism within each `ConfigurableDevice` to simulate GPU failure scenarios as instructed by config overrides.

- **Failure modes include:** lost device, fallen off bus, uncorrectable ECC errors, and Xid critical events.
- **Interaction:** Injects faults probabilistically or deterministically on guarded NVML calls.
- **Hotpath optimization:** The injector pointer is checked atomically; when nil, no failure is injected.
- **Configurable at runtime:** Overrides processed at config refresh to enable/disable fault injections dynamically.
- **Reference:**  
  - failure pointer and reconcile methods on `ConfigurableDevice` [pkg/gpu/mocknvml/engine/device.go:70-73,179-207]()  
  - Failure injection config documented in Helm `values.yaml` under `failureInjection` [deployments/nvml-mock/helm/nvml-mock/values.yaml:41-56]()  

---

## Container Device Interface (CDI)

- **Role:** Generates device specifications allowing container runtimes (like containerd and Docker) to inject the mock NVML libraries and device nodes into user containers automatically.
- **Generated by:** The DaemonSet setup script `setup.sh` writes `nvidia.yaml` into `/var/run/cdi` directory on the host.
- **Content:** Includes device nodes (`/dev/nvidia*`), the mock `libnvidia-ml.so` library, and config directory mount with mock profiles and overrides.
- **Effect:** Enables workloads without GPUs to transparently run tools like `nvidia-smi` by hooking into container runtime mechanisms.
- **Reference:**  
  - CDI spec generation snippet in `setup.sh`: [deployments/nvml-mock/scripts/setup.sh:68-170]()  
  - Mentioned in Helm Chart README and deployment instructions: [deployments/nvml-mock/helm/nvml-mock/README.md:24-34]()  

---

## NRI Plugin (`nvml-mock-nri`)

The Node Resource Interface (NRI) plugin mechanism to ambiently inject the nvml-mock overlays into every container without requiring pod spec modification.

- **Opt-in:** Disabled by default; enabled by setting `nri.enabled=true` in the Helm values.
- **How it works:** The plugin mounts the host mock overlay into container filesystems under `/opt/nvml-mock` and configures environment variables/LD_PRELOAD to activate the mock library inside containers transparently.
- **Annotations:** Pods can explicitly opt out or opt into device-node mounts via special annotations.
- **Usage requirement:** Kubernetes cluster node containerd runtime must have NRI enabled.
- **Health and readiness:** The plugin manages health probes on a separate port (`healthPort`) to allow kubelet liveness/readiness checks.
- **References:**  
  - Helm values under `nri`: [deployments/nvml-mock/helm/nvml-mock/values.yaml:112-150]()  
  - Overview in Helm Chart README: [deployments/nvml-mock/helm/nvml-mock/README.md:29-35]()  

---

## Device Topology and PCIe/NVLink Simulation

- **Fabric and topology:** The mock config supports node-level fabric topology through shared `NodeFabric` used by `ConfigurableDevice` instances.
- **NVLink:** Simulated NVLink links per GPU, with ability to override states such as active/inactive, error injection on NVLink errors.
- **PCI Sysfs Overlay:** A fake PCI topology is rendered under `/var/lib/nvml-mock/sys/bus/pci/devices`, making topology-aware consumers such as NVIDIA DRA and schedulers detect appropriate PCI root complexes.
- **Relevant files/classes:**  
  - Device topology fields and NVLink simulation in `ConfigurableDevice` [pkg/gpu/mocknvml/engine/device.go:45]()  
  - PCI sysfs rendering tool and sysfs fake layers described in documentation, deployed at known paths by setup scripts and in the daemonset's mount points.  
- **Mermaid Diagram: GPU Simulation and Topology Context**

```mermaid
flowchart TB
  NL["Natural Language: GPU Device"] --> CD[ConfigurableDevice struct]
  CD -->|Holds| DGX[Base dgxa100.Device]
  CD -->|References| FAB[NodeFabric (shared topology)]
  CD --> DM[dynamicMetricsSimulator (atomic ptr)]
  CD --> FI[failureInjector (atomic ptr)]

  subgraph NVML_API
    DP[nvmlDeviceGetHandleByIndex_v2] -.-> CD
    DP -.-> Eng[Engine Singleton]
    DP -.->> CD : Forwards calls
  end

  Engine -->|Manages multiple| CD
  SetupSh["setup.sh script"] -->|Creates| CD
  SetupSh -->|Populates| PCI_Sysfs["Fake PCI Sysfs @ /var/lib/nvml-mock/sys"]

  FAB -->|Provides NVLink, PCIe topology| CD
```

---

## Kubernetes Node Labeling & Features

- `nvidia.com/gpu.present`: Direct node label indicating presence of GPUs (mocked) on the node. Set/removed by setup.sh/cleanup.sh.
- `feature.node.kubernetes.io/pci-10de.present`: Node Feature Discovery (NFD) derived label signaling NVIDIA PCI vendor presence. Created by NFD by reading feature files generated by the mock.
- These labels enable GPU-aware scheduling and device plugin operations reliant on node feature identification.
- Helm values provide control for whether the mock writes the PCI vendor presence feature file (`nodeLabels.pciVendorPresent`) and where the NFD features directory is (`nodeLabels.featuresDir`).
- Relevant files:  
  - Label handling in Helm DaemonSet env vars and mounts: [deployments/nvml-mock/helm/nvml-mock/templates/daemonset.yaml:75-94]()  
  - Feature file setup in `setup.sh`: [deployments/nvml-mock/scripts/setup.sh:150-175]()  
  - Value flags in `values.yaml`: [deployments/nvml-mock/helm/nvml-mock/values.yaml:79-101]()  

---

## YAMLConfig and Override System

- The GPU configuration is defined primarily in a YAML file at `/etc/nvml-mock/config.yaml`.
- The YAML config contains system-level info (`SystemConfig`), per-device overrides (`DeviceOverride`), topology blocks, dynamic metric parameters, and failure injection specifications.
- At runtime, config overrides can be applied dynamically via the `ConfigOverridePathFor()` file mechanism (default `/var/lib/nvml-mock/driver/config/overrides.yaml`).
- The `ConfigurableDevice` merges base YAML config with per-device overrides atomically on each refresh, ensuring concurrent safety.
- Override document generations are tracked and checked with atomic generations to avoid races.
- This layered design allows simulation parameters to be adapted live without restarting pods.
- Relevant implementations:  
  - `ConfigurableDevice` refresh/merge logic in [pkg/gpu/mocknvml/engine/device.go:179-207]()  
  - Helm values controlling custom config and override path: [deployments/nvml-mock/helm/nvml-mock/values.yaml:3-12]()  

---

## Key Abbreviations and Terms

| Term           | Definition                                                                                             | Code Reference                                    |
|----------------|-----------------------------------------------------------------------------------------------------|--------------------------------------------------|
| NVML           | NVIDIA Management Library - GPU runtime monitoring API simulated here.                              | Bridge files [pkg/gpu/mocknvml/bridge/device.go] |
| ConfigurableDevice | Go struct wrapping a simulated GPU device with config overlays and runtime state.               | [pkg/gpu/mocknvml/engine/device.go]               |
| Engine Singleton | Central mock state manager for devices and global configuration.                                  | [pkg/gpu/mocknvml/engine/device.go], bridge files |
| CDI            | Container Device Interface - Device injection spec generated by setup.sh.                           | setup.sh [deployments/nvml-mock/scripts/setup.sh]|
| NFD            | Node Feature Discovery - Kubernetes addon recognizing mock GPU features from feature files.        | Helm DaemonSet env, setup.sh                      |
| DRA            | Dynamic Resource Allocation - Kubernetes device management technology integrated with the mock.    | Mentioned in Helm README and cluster config docs |
| NRI            | Node Resource Interface - containerd plugin for ambient injection of mock NVML environment.        | Helm chart values, README                          |
| Dynamic Metrics | Optional simulation of time-based GPU telemetry (temp, power, utilization).                         | device.go ConfigurableDevice dynamicMetrics field |
| Failure Injection | Simulated GPU fault modes injected probabilistically or deterministically in device APIs.        | device.go failure atomic pointer and logic       |
| BAR1 Memory    | GPU Base Address Register 1 space simulated for memory aperture info.                              | device.go cached bar1Memory nvml.BAR1Memory       |
| PCI Sysfs      | Fake sysfs overlay describing PCI topology, required by DRA and device-aware schedulers.           | Created by `render-pci-sysfs` tool and mounted    |

---

## Bridging Deployment and Code: NVML Mock in Kubernetes

```mermaid
flowchart TB
  subgraph Kubernetes Cluster
    DS[DaemonSet: nvml-mock pod]
    DS --> Setup["setup.sh" script]
    DS --> NVMLPod["Pod with mock NVML library"]
    DS --> NFDFile["/etc/kubernetes/node-feature-discovery/features.d/nvml-mock.features"]
    NFDFile -.-> NFD["Node Feature Discovery (NFD) adds label"]
    NFD --> NodeLabel["feature.node.kubernetes.io/pci-10de.present=true"]
    Setup --> CDI_YAML["/var/run/cdi/nvidia.yaml"]
    Setup --> DeviceNodes["/var/lib/nvml-mock/driver/dev/nvidia*"]
    DeviceNodes --> NVMLPod
    CDI_YAML --> NVMLPod
    NVMLPod -->|Mock library loads from| ConfigFile["/etc/nvml-mock/config.yaml"]

    subgraph Container Runtime (containerd)
      NRIPlugin["nvml-mock-nri plugin (if enabled)"]
      NRIPlugin --> NVMLPod
    end
  end

  subgraph Code (Mock NVML Library)
    NVML_API["Exports NVML API via CGo"] --> Bridge["pkg/gpu/mocknvml/bridge/device.go"]
    Bridge --> Engine["Engine Singleton"]
    Engine --> ConfigDevices["ConfigurableDevice instances"]
    ConfigDevices --> DynamicMetrics
    ConfigDevices --> FailureInjector
  end

  NVMLPod -- Calls --> NVML_API
```

This diagram illustrates how the nvml-mock system integrates within a Kubernetes cluster, deployed as a DaemonSet, interacting with NFD for labeling, CDI for device injection, and optionally an NRI plugin for container runtime injection. The nvml-mock library exports NVML API calls backed by Go engine and device structures.

---

## Bridging Natural Language Terms to Code Entities: Core Structs and Functions

```mermaid
classDiagram
  class Engine {
    +DeviceGetCount() int, nvmlReturn_t
    +DeviceGetHandleByIndex(index int) (handle, nvmlReturn_t)
    +LookupDevice(handle) DeviceInterface
  }

  class ConfigurableDevice {
    -baseConfig *DeviceConfig
    -effective atomic.Pointer<DeviceConfig>
    -failure atomic.Pointer<FailureInjector>
    -dynamicMetrics atomic.Pointer<dynamicMetricsSimulator>
    +cfg() *DeviceConfig
    +failureInjector() *FailureInjector
    +GetBAR1MemoryInfo() (nvml.BAR1Memory, nvmlReturn_t)
    +GetPciInfo() (nvml.PciInfo, nvmlReturn_t)
    +GetComputeRunningProcesses() ([]nvml.ProcessInfo, nvmlReturn_t)
  }

  class Bridge {
    +nvmlDeviceGetCount_v2(deviceCount unsafe.Pointer) C.nvmlReturn_t
    +nvmlDeviceGetHandleByIndex_v2(index C.uint, ptr *C.nvmlDevice_t) C.nvmlReturn_t
  }

  Engine o-- ConfigurableDevice : manages 0..* >

  Bridge --> Engine : delegates API calls to

```

This class diagram bridges common system names (Engine, ConfigurableDevice, Bridge) to their key methods and relationships. The Engine singleton manages multiple ConfigurableDevices. The NVML API Bridge routes calls to Engine methods. The ConfigurableDevice provides detailed simulation behavior.

---

# Summary

This glossary covers the essential terminology and their concrete code or deployment correlations in the `k8s-test-infra` repository. The core concept is the **nvml-mock system**, a Kubernetes-deployed software stack that simulates NVIDIA GPUs using a mock NVML shared library backed by an extensible Go engine. ConfigurableDevice instances embody each simulated GPU, supporting dynamic metrics and failure injection. The entire setup is deployable via Helm, tightly integrated with Kubernetes features like Node Feature Discovery (NFD), Container Device Interface (CDI), and Node Resource Interface (NRI) plugins to provide seamless GPU simulation without hardware.

---

## Sources:

- `pkg/gpu/mocknvml/engine/device.go:1-178`  
- `pkg/gpu/mocknvml/engine/device_test.go:24-182`  
- `pkg/gpu/mocknvml/bridge/device.go:14-194`  
- `deployments/nvml-mock/helm/nvml-mock/README.md:1-229`  
- `deployments/nvml-mock/helm/nvml-mock/values.yaml:1-138`  
- `deployments/nvml-mock/helm/nvml-mock/templates/daemonset.yaml:1-147`  
- `deployments/nvml-mock/scripts/setup.sh:1-240`