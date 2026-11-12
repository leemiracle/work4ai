# Page: Overview of Trivy

# Overview of Trivy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.release-please-manifest.json](.release-please-manifest.json)
- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [docs/build/Dockerfile](docs/build/Dockerfile)
- [docs/build/requirements.txt](docs/build/requirements.txt)
- [docs/commercial/compare.md](docs/commercial/compare.md)
- [docs/commercial/contact.md](docs/commercial/contact.md)
- [docs/community/principles.md](docs/community/principles.md)
- [docs/getting-started/faq.md](docs/getting-started/faq.md)
- [docs/getting-started/installation.md](docs/getting-started/installation.md)
- [docs/imgs/excalidraw/image.excalidraw](docs/imgs/excalidraw/image.excalidraw)
- [docs/imgs/secret-demo.gif](docs/imgs/secret-demo.gif)
- [docs/imgs/trivy-k8s.png](docs/imgs/trivy-k8s.png)
- [docs/index.md](docs/index.md)
- [docs/tutorials/kubernetes/cluster-scanning.md](docs/tutorials/kubernetes/cluster-scanning.md)
- [go.mod](go.mod)
- [go.sum](go.sum)
- [integration/client_server_test.go](integration/client_server_test.go)
- [integration/docker_engine_test.go](integration/docker_engine_test.go)
- [integration/integration_test.go](integration/integration_test.go)
- [integration/registry_test.go](integration/registry_test.go)
- [integration/repo_test.go](integration/repo_test.go)
- [integration/sbom_test.go](integration/sbom_test.go)
- [integration/standalone_tar_test.go](integration/standalone_tar_test.go)
- [integration/testdata/fixtures/db/vulnerability.yaml](integration/testdata/fixtures/db/vulnerability.yaml)
- [integration/testdata/fluentd-multiple-lockfiles.json.golden](integration/testdata/fluentd-multiple-lockfiles.json.golden)
- [mkdocs.yml](mkdocs.yml)
- [pkg/commands/app.go](pkg/commands/app.go)
- [pkg/commands/app_test.go](pkg/commands/app_test.go)
- [pkg/commands/artifact/run.go](pkg/commands/artifact/run.go)
- [pkg/commands/testdata/java-db/metadata.json](pkg/commands/testdata/java-db/metadata.json)
- [pkg/commands/testdata/policy/metadata.json](pkg/commands/testdata/policy/metadata.json)
- [pkg/flag/options.go](pkg/flag/options.go)
- [release-please-config.json](release-please-config.json)

</details>



Trivy is a comprehensive, all-in-one security scanner designed to find vulnerabilities, misconfigurations, secrets, and license issues across diverse software artifacts. It is implemented in Go as a single, self-contained binary that requires no external dependencies beyond the vulnerability databases it automatically downloads.

This page provides a high-level introduction to Trivy's purpose, key features, and architecture. For more details:
- **Installation and configuration**: See [Installation and Setup](#1.1)
- **Detailed architecture and component design**: See [Core Architecture and Components](#1.2)
- **Database and resource management**: See [Database and Resource Management](#1.3)
- **CLI usage and commands**: See [CLI Reference](#2)
- **Scanning workflows by target type**: See [Target Types and Scanning Workflows](#5)

**Sources:** [README.md:14-36](), [go.mod:1-4]()

## What Trivy Does

Trivy performs security scanning across multiple dimensions, operating as a unified tool that replaces the need for separate scanners for different security concerns.

### Supported Scan Targets

Trivy can analyze the following artifact types:

| Target Type | Command | Primary Use Case |
|-------------|---------|------------------|
| Container Images | `trivy image` | Scan images from registries or tar archives |
| Filesystems | `trivy filesystem` | Scan local directories and projects |
| Rootfs | `trivy rootfs` | Scan unpacked container filesystems |
| Git Repositories | `trivy repository` | Scan source code repositories |
| Virtual Machines | `trivy vm` | Scan VM disk images (VMDK, AMI, etc.) |
| Kubernetes | `trivy kubernetes` | Scan running Kubernetes clusters |
| SBOM Files | `trivy sbom` | Scan existing SBOM files (CycloneDX, SPDX) |

### Security Scanners

Trivy includes independent scanner types that can be enabled or disabled via the `--scanners` flag:

1. **Vulnerability Scanner** (`vuln`): Detects known CVEs in OS packages and application dependencies using the `trivy-db` vulnerability database. Supports 20+ package ecosystems and operating systems.
2. **Misconfiguration Scanner** (`misconfig`): Identifies security issues in Infrastructure as Code (IaC) files including Terraform, Kubernetes manifests, Dockerfiles, CloudFormation, Helm charts, and Ansible playbooks. Uses Rego policies from the `trivy-checks` bundle.
3. **Secret Scanner** (`secret`): Finds hard-coded credentials, API keys, tokens, and other sensitive data in source code and configuration files.
4. **License Scanner** (`license`): Identifies software licenses in dependencies and classifies them (MIT, Apache, GPL, etc.) using SPDX identifiers.

**Sources:** [README.md:17-32](), [pkg/commands/app.go:88-106](), [pkg/commands/artifact/run.go:49-57]()

## High-Level Architecture

Trivy is organized into primary layers that handle different aspects of the scanning pipeline, from user interface to data access. This design enables modularity, allowing different scanner types to share common infrastructure while maintaining specialized detection logic.

### Architectural Layers

**System Architecture Overview**

```mermaid
graph TB
    subgraph "1. User Interface Layer"
        CLI["CLI Entry Point<br/>cobra.Command"]
        NewApp["NewApp()<br/>pkg/commands/app.go"]
        Flags["Flag System<br/>pkg/flag/options.go"]
    end
    
    subgraph "2. Orchestration Layer"
        Runner["Runner Interface<br/>pkg/commands/artifact/run.go"]
        NewRunner["NewRunner()<br/>pkg/commands/artifact/run.go"]
        InitDB["initDB()<br/>pkg/commands/artifact/run.go"]
    end
    
    subgraph "3. Scanning Layer"
        ScanService["scan.Service<br/>pkg/scan/service.go"]
        Analyzers["Analyzers<br/>pkg/fanal/analyzer"]
    end
    
    subgraph "4. Data Layer"
        TrivyDB["trivy-db<br/>BoltDB"]
        JavaDB["trivy-java-db<br/>SQLite"]
        ChecksBundle["trivy-checks<br/>Rego Policies"]
    end
    
    subgraph "5. Output Layer"
        ReportWriter["pkg/report/write.go"]
        Formatters["JSON, SARIF, Table,<br/>CycloneDX, SPDX"]
    end
    
    NewApp --> Flags
    NewApp --> NewRunner
    NewRunner --> InitDB
    NewRunner --> ScanService
    ScanService --> Analyzers
    Analyzers --> TrivyDB
    Analyzers --> JavaDB
    Runner --> ReportWriter
    ReportWriter --> Formatters
```

**Sources:** [pkg/commands/app.go:67-117](), [pkg/commands/artifact/run.go:79-174](), [pkg/flag/options.go:36-85]()

### Key Components

The following table maps high-level components to their code locations:

| Layer | Component | File Location | Primary Responsibility |
|-------|-----------|---------------|------------------------|
| User Interface | `NewApp()` | [pkg/commands/app.go:68-117]() | Cobra command tree construction with grouped commands |
| User Interface | `Flag[T]` | [pkg/flag/options.go:36-85]() | Generic flag parsing with Viper integration |
| Orchestration | `Runner` interface | [pkg/commands/artifact/run.go:79-98]() | Defines scanning methods for each target type |
| Orchestration | `NewRunner()` | [pkg/commands/artifact/run.go:121-174]() | Initializes DB, WASM modules, and version checker |
| Data | `db.Init()` | [pkg/db/db.go]() | Manages vulnerability database initialization |
| Output | `pkgReport.Write()` | [pkg/report/write.go]() | Dispatches results to specific format writers |

For detailed architecture information including service initialization patterns and analyzer chains, see [Core Architecture and Components](#1.2).

**Sources:** [pkg/commands/app.go:68-117](), [pkg/commands/artifact/run.go:79-174](), [pkg/flag/options.go:36-85]()

## Scanning Workflow

Trivy follows a consistent three-phase workflow regardless of the target type being scanned: scan, filter, and report.

### Standard Scan Pipeline

**Main Execution Flow**

```mermaid
graph TB
    subgraph "Phase 1: Scan"
        ExecuteScan["Execute scan:<br/>ScanImage()<br/>ScanFilesystem()<br/>ScanRepository()"]
        InitializeScan["InitializeScanService()<br/>pkg/commands/artifact/run.go"]
    end
    
    subgraph "Phase 2: Filter"
        FilterResults["Runner.Filter()<br/>pkg/commands/artifact/run.go"]
        ApplyVEX["VEX Filtering<br/>pkg/vex/repo"]
    end
    
    subgraph "Phase 3: Report"
        RunnerReport["Runner.Report()<br/>pkg/commands/artifact/run.go"]
        WriteReport["pkgReport.Write()"]
    end
    
    ExecuteScan --> InitializeScan
    InitializeScan --> FilterResults
    FilterResults --> ApplyVEX
    ApplyVEX --> RunnerReport
    RunnerReport --> WriteReport
```

**Sources:** [pkg/commands/artifact/run.go:199-296](), [pkg/commands/artifact/run.go:79-98]()

### Target Type Dispatch

Trivy maps each CLI command to a specific `TargetKind` constant and corresponding runner method:

| CLI Command | `TargetKind` Constant | Runner Method |
|-------------|----------------------|---------------|
| `trivy image` | `TargetContainerImage` | `runner.ScanImage()` |
| `trivy fs` | `TargetFilesystem` | `runner.ScanFilesystem()` |
| `trivy rootfs` | `TargetRootfs` | `runner.ScanRootfs()` |
| `trivy repo` | `TargetRepository` | `runner.ScanRepository()` |
| `trivy sbom` | `TargetSBOM` | `runner.ScanSBOM()` |
| `trivy vm` | `TargetVM` | `runner.ScanVM()` |
| `trivy k8s` | `TargetK8s` | Kubernetes workflow |

The `TargetKind` type is defined in [pkg/commands/artifact/run.go:47-57]() and determines which analyzers are active and how the artifact is processed. For detailed workflows specific to each target type, see [Target Types and Scanning Workflows](#5).

**Sources:** [pkg/commands/artifact/run.go:47-57](), [pkg/commands/artifact/run.go:199-220]()

## Key Features

### Multiple Deployment Modes

Trivy supports two operational modes:

**Standalone Mode** (default): All scanning occurs locally. Trivy downloads and maintains its own copy of vulnerability databases and policy bundles in a local cache directory.

**Client/Server Mode**: Scanning is distributed between a client and server. The server maintains shared vulnerability databases. Mode selection is determined by the `--server` flag. When specified, Trivy connects to the remote server using the Twirp RPC protocol.

For detailed information on deployment configurations, see [Deployment Models](#8).

**Sources:** [pkg/commands/artifact/run.go:204-217](), [pkg/commands/app.go:93-94]()

### Automatic Resource Management

Trivy automatically manages several types of external resources:

1. **Vulnerability Database** (`trivy-db`): BoltDB file containing CVE data for OS packages and language ecosystems.
2. **Java Database** (`trivy-java-db`): SQLite database containing vulnerability information for Java artifacts.
3. **Policy Bundle** (`trivy-checks`): OCI artifact containing Rego policies for misconfiguration detection.

The `NewRunner()` function [pkg/commands/artifact/run.go:121-174]() triggers database initialization via `initDB()` and downloads VEX repositories if configured. For detailed database management, see [Database and Resource Management](#1.3).

**Sources:** [pkg/commands/artifact/run.go:146-153](), [pkg/commands/artifact/run.go:30]()

### Extensibility

Trivy provides several extension mechanisms:
- **WASM Modules**: Custom analyzers written in languages that compile to WebAssembly. Loaded by the `module.Manager` [pkg/commands/artifact/run.go:156-164]().
- **Plugins**: External executables that extend Trivy's capabilities. Loaded by `loadPluginCommands()` [pkg/commands/app.go:119-147]().
- **Custom Policies**: User-defined Rego policies for misconfiguration detection.

**Sources:** [pkg/commands/artifact/run.go:156-164](), [pkg/commands/app.go:119-147]()

## CLI Structure

Trivy's command-line interface is built using the Cobra framework and organized into functional groups.

| Group ID | Title | Purpose |
|----------|-------|---------|
| `groupScanning` | "Scanning Commands" | Primary scan operations (`image`, `fs`, `repo`, etc.) |
| `groupManagement` | "Management Commands" | Resource and server management (`server`, `module`, `plugin`) |
| `groupUtility` | "Utility Commands" | Helper tools (`version`, `convert`, `clean`) |

The command structure is defined in `NewApp()` [pkg/commands/app.go:68-117](). Each command is implemented as a factory function that returns a `*cobra.Command`. For comprehensive CLI documentation, see [CLI Reference](#2).

**Sources:** [pkg/commands/app.go:61-106]()

## Configuration System

Trivy uses a tiered configuration system that merges settings from CLI flags, environment variables, and configuration files.

- **Config File**: Loaded from `trivy.yaml` by default using `initConfig()` [pkg/commands/app.go:149-164]().
- **Environment Variables**: Prefixed with `TRIVY_`.
- **CLI Flags**: Defined using the generic `Flag[T]` struct [pkg/flag/options.go:36-85]().

For complete configuration documentation, see [Configuration Files and Environment Variables](#2.4).

**Sources:** [pkg/commands/app.go:149-164](), [pkg/flag/options.go:36-85]()

---

# Page: Installation and Setup

# Installation and Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [.github/DISCUSSION_TEMPLATE/adopters.yml](.github/DISCUSSION_TEMPLATE/adopters.yml)
- [.github/DISCUSSION_TEMPLATE/bugs.yml](.github/DISCUSSION_TEMPLATE/bugs.yml)
- [.github/DISCUSSION_TEMPLATE/documentation.yml](.github/DISCUSSION_TEMPLATE/documentation.yml)
- [.github/DISCUSSION_TEMPLATE/false-detection.yml](.github/DISCUSSION_TEMPLATE/false-detection.yml)
- [.github/DISCUSSION_TEMPLATE/ideas.yml](.github/DISCUSSION_TEMPLATE/ideas.yml)
- [.github/DISCUSSION_TEMPLATE/q-a.yml](.github/DISCUSSION_TEMPLATE/q-a.yml)
- [.github/ISSUE_TEMPLATE/config.yml](.github/ISSUE_TEMPLATE/config.yml)
- [.github/pull_request_template.md](.github/pull_request_template.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [Dockerfile](Dockerfile)
- [Dockerfile.canary](Dockerfile.canary)
- [ci/deploy-deb.sh](ci/deploy-deb.sh)
- [ci/deploy-rpm.sh](ci/deploy-rpm.sh)
- [contrib/Trivy.gitlab-ci.yml](contrib/Trivy.gitlab-ci.yml)
- [docs/build/Dockerfile](docs/build/Dockerfile)
- [docs/build/requirements.txt](docs/build/requirements.txt)
- [docs/commercial/compare.md](docs/commercial/compare.md)
- [docs/commercial/contact.md](docs/commercial/contact.md)
- [docs/community/contribute/discussion.md](docs/community/contribute/discussion.md)
- [docs/community/contribute/issue.md](docs/community/contribute/issue.md)
- [docs/community/maintainer/help-wanted.md](docs/community/maintainer/help-wanted.md)
- [docs/community/principles.md](docs/community/principles.md)
- [docs/getting-started/faq.md](docs/getting-started/faq.md)
- [docs/getting-started/installation.md](docs/getting-started/installation.md)
- [docs/guide/configuration/filtering.md](docs/guide/configuration/filtering.md)
- [docs/guide/supply-chain/attestation/rekor.md](docs/guide/supply-chain/attestation/rekor.md)
- [docs/guide/target/container_image.md](docs/guide/target/container_image.md)
- [docs/imgs/secret-demo.gif](docs/imgs/secret-demo.gif)
- [docs/imgs/trivy-k8s.png](docs/imgs/trivy-k8s.png)
- [docs/index.md](docs/index.md)
- [docs/tutorials/kubernetes/cluster-scanning.md](docs/tutorials/kubernetes/cluster-scanning.md)
- [goreleaser-canary.yml](goreleaser-canary.yml)
- [goreleaser.yml](goreleaser.yml)

</details>



## Purpose and Scope

This page guides users through installing Trivy via various distribution methods and performing initial setup. It covers binary installation, package managers, container images, and basic configuration needed to start scanning. Trivy is designed to be platform-agnostic, supporting a wide range of operating systems and architectures.

For information about deploying Trivy in production environments, see [8.1 Standalone Mode](), [8.2 Client-Server Architecture](), or [8.3 Kubernetes Deployment with Helm](). For details on configuration files and environment variables, see [2.4 Configuration Files and Environment Variables]().

---

## Platform and Architecture Support

Trivy provides multi-platform support through a GoReleaser-based build pipeline, compiling native binaries for various operating systems and architectures. The build process ensures that binaries are statically linked and optimized for containerized environments.

### Supported Platforms

| Platform | Architectures | Build ID | Configuration Reference |
|----------|--------------|----------|-------------------------|
| Linux | amd64, arm64, 386, arm (v7), s390x, ppc64le | `build-linux` | [goreleaser.yml:5-25]() |
| macOS (Darwin) | amd64, arm64 | `build-macos` | [goreleaser.yml:43-59]() |
| Windows | amd64 | `build-windows` | [goreleaser.yml:60-76]() |
| FreeBSD | amd64 | `build-bsd` | [goreleaser.yml:26-42]() |

All official builds are compiled with `CGO_ENABLED=0` [goreleaser.yml:13]() and use `GOEXPERIMENT=jsonv2` [goreleaser.yml:14]() for high-performance JSON processing. The version information is injected into the binary at build time via `ldflags` targeting `github.com/aquasecurity/trivy/pkg/version/app.ver` [goreleaser.yml:11]().

**Sources:** [goreleaser.yml:1-76]()

---

## Distribution Architecture

The following diagram bridges the release automation logic to the resulting distribution entities.

**Release Pipeline to Artifact Mapping**
```mermaid
graph TD
    subgraph "Build System (GoReleaser)"
        GR["goreleaser.yml"]
        BL["build-linux"]
        BM["build-macos"]
        BW["build-windows"]
        BBSD["build-bsd"]
    end

    subgraph "Package Generators (NFPM)"
        DEB["DEB Package"]
        RPM["RPM Package"]
    end

    subgraph "Distribution Points"
        GH["GitHub Releases"]
        DH["Docker Hub"]
        GHCR["GHCR.io"]
        ECR["Public ECR"]
        APT["APT Repo"]
        YUM["YUM Repo"]
    end

    GR --> BL & BM & BW & BBSD
    BL --> DEB & RPM
    BL --> DH & GHCR & ECR
    
    DEB --> APT
    RPM --> YUM
    
    BM & BW & BBSD --> GH
    BL --> GH

    subgraph "Code Entities"
        Entry["cmd/trivy/main.go"]
        VerPkg["pkg/version/app"]
    end

    BL -- "compiles" --> Entry
    GR -- "sets version in" --> VerPkg
```

The release process is defined in `goreleaser.yml` [goreleaser.yml:1-3](). It orchestrates the creation of archives [goreleaser.yml:114-139](), Linux packages via NFPM [goreleaser.yml:83-112](), and container images [goreleaser.yml:152-252]().

**Sources:** [goreleaser.yml:1-252](), [Dockerfile:1-6]()

---

## Installation Methods

### Method 1: Official Container Images

Trivy is distributed as a minimal container image based on Alpine Linux [Dockerfile:1](). This is the recommended method for CI/CD environments.

**Available Registries:** [docs/getting-started/installation.md:12-16]()
* **Docker Hub:** `docker.io/aquasec/trivy`
* **GitHub Container Registry:** `ghcr.io/aquasecurity/trivy`
* **AWS ECR Public:** `public.ecr.aws/aquasecurity/trivy`

**Usage Example:**
```bash
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  -v $HOME/Library/Caches:/root/.cache/ \
  aquasec/trivy:latest image python:3.4-alpine
```
*Note: Mounting the Docker socket is required for scanning local images, and mounting a cache directory is recommended for performance [docs/getting-started/installation.md:19-22]().*

**Sources:** [Dockerfile:1-6](), [docs/getting-started/installation.md:8-29]()

### Method 2: Package Managers (Official)

#### Debian/Ubuntu (APT)
Trivy maintains an official APT repository. Packages are generated for `amd64`, `i386`, and `arm64` [ci/deploy-deb.sh:10-12]().

```bash
sudo apt-get install wget gnupg
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | sudo tee /usr/share/keyrings/trivy.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy
```
**Sources:** [docs/getting-started/installation.md:68-79](), [ci/deploy-deb.sh:1-25]()

#### RHEL/CentOS (YUM/RPM)
The RPM repository supports major RHEL versions 5 through 9 [ci/deploy-rpm.sh:43-47]().

```bash
cat << EOF | sudo tee -a /etc/yum.repos.d/trivy.repo
[trivy]
name=Trivy repository
baseurl=https://aquasecurity.github.io/trivy-repo/rpm/releases/\$basearch/
gpgcheck=1
enabled=1
gpgkey=https://aquasecurity.github.io/trivy-repo/rpm/public.key
EOF
sudo yum -y update
sudo yum -y install trivy
```
**Sources:** [docs/getting-started/installation.md:44-60](), [ci/deploy-rpm.sh:1-52]()

#### Homebrew (macOS/Linux)
The official Homebrew tap is maintained at `aquasecurity/homebrew-trivy` [goreleaser.yml:144-145]().
```bash
brew install trivy
```
**Sources:** [docs/getting-started/installation.md:88-94](), [goreleaser.yml:141-150]()

### Method 3: Installation Scripts and Binaries

For environments without package managers, Trivy provides a convenience script:
```bash
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sudo sh -s -- -b /usr/local/bin
```
**Sources:** [docs/getting-started/installation.md:36-42]()

---

## Initial Setup and Resource Flow

Once installed, Trivy requires several external resources (databases and policies) to function. These are automatically managed during the first execution.

**Data Flow: Initialization to Scan**
```mermaid
graph LR
    subgraph "Remote Registries (GHCR)"
        VDB["trivy-db<br/>(Vulnerabilities)"]
        JDB["trivy-java-db<br/>(Java Index)"]
        PB["trivy-checks<br/>(Rego Policies)"]
    end

    subgraph "Local Cache (~/.cache/trivy)"
        LDB["db/trivy.db"]
        LJDB["java-db/trivy-java.db"]
        LPB["policy/content/"]
    end

    subgraph "Trivy CLI"
        Cmd["trivy image/fs/k8s"]
    end

    VDB -- "OCI Pull" --> LDB
    JDB -- "OCI Pull" --> LJDB
    PB -- "OCI Pull" --> LPB

    LDB & LJDB & LPB --> Cmd
```

### Resource Management Components

| Resource | Default Repository | Cache Subdirectory |
|----------|--------------------|--------------------|
| Vulnerability DB | `ghcr.io/aquasecurity/trivy-db` | `db/` |
| Java Database | `ghcr.io/aquasecurity/trivy-java-db` | `java-db/` |
| Policies/Checks | `ghcr.io/aquasecurity/trivy-checks` | `policy/` |

**Sources:** [docs/getting-started/installation.md:19](), [goreleaser.yml:108-109]() (Templates path)

---

## Verification

After installation, verify the setup by checking the version and running a test scan.

1. **Check Version:**
   ```bash
   trivy --version
   ```
   This verifies the binary is in the `PATH` and displays the version injected during the build [goreleaser.yml:11]().

2. **Test Scan:**
   ```bash
   trivy image alpine:latest
   ```
   This will trigger the initial download of the vulnerability database to the default cache directory [docs/getting-started/installation.md:19]().

3. **Kubernetes Environment (Optional):**
   If using Trivy in a cluster, verify connectivity:
   ```bash
   trivy k8s --report summary
   ```
   **Sources:** [docs/tutorials/kubernetes/cluster-scanning.md:14-18]()

---

## Community Installations

Trivy is also available through various community-maintained channels:
* **Arch Linux:** `pacman -S trivy` [docs/getting-started/installation.md:106]()
* **Nix/NixOS:** `nix-env --install -A nixpkgs.trivy` [docs/getting-started/installation.md:142]()
* **OpenSUSE:** `zypper install trivy` [docs/getting-started/installation.md:119]()
* **asdf/mise:** via the `asdf-trivy` plugin [docs/getting-started/installation.md:174-214]()

**Sources:** [docs/getting-started/installation.md:101-215]()

---

# Page: Core Architecture and Components

# Core Architecture and Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [cmd/trivy/main.go](cmd/trivy/main.go)
- [docs/guide/coverage/others/activestate.md](docs/guide/coverage/others/activestate.md)
- [docs/guide/coverage/others/index.md](docs/guide/coverage/others/index.md)
- [go.mod](go.mod)
- [go.sum](go.sum)
- [internal/dbtest/db.go](internal/dbtest/db.go)
- [mkdocs.yml](mkdocs.yml)
- [pkg/commands/app.go](pkg/commands/app.go)
- [pkg/commands/app_test.go](pkg/commands/app_test.go)
- [pkg/commands/artifact/run.go](pkg/commands/artifact/run.go)
- [pkg/commands/artifact/scanner.go](pkg/commands/artifact/scanner.go)
- [pkg/commands/testdata/java-db/metadata.json](pkg/commands/testdata/java-db/metadata.json)
- [pkg/commands/testdata/policy/metadata.json](pkg/commands/testdata/policy/metadata.json)
- [pkg/db/db.go](pkg/db/db.go)
- [pkg/db/db_test.go](pkg/db/db_test.go)
- [pkg/fanal/analyzer/os/release/testdata/activestate](pkg/fanal/analyzer/os/release/testdata/activestate)
- [pkg/fanal/image/image.go](pkg/fanal/image/image.go)
- [pkg/flag/options.go](pkg/flag/options.go)
- [pkg/scan/local/service.go](pkg/scan/local/service.go)
- [pkg/scan/local/service_test.go](pkg/scan/local/service_test.go)

</details>



This document explains Trivy's architectural design, covering the major subsystems and how they interact. Trivy is organized into several distinct layers: a CLI orchestration layer, a core scanning engine with analyzers and detectors, an RPC layer for client/server deployments, and a reporting system for output generation.

---

## Architectural Overview

Trivy's architecture consists of five major layers that work together to perform security scanning:

**Major System Layers**

```mermaid
graph TB
    subgraph "1. CLI Layer"
        CLI["commands.NewApp()<br/>Cobra Commands"]
        Flags["flag.Flags<br/>Viper Configuration"]
    end
    
    subgraph "2. Orchestration Layer"
        ArtifactRun["artifact.Run()<br/>Main Entry Point"]
        Runner["artifact.Runner<br/>Interface"]
    end
    
    subgraph "3. Core Scanning Engine"
        Service["scan.Service<br/>(local/remote)"]
        Applier["applier.Applier<br/>Layer Analysis"]
        Analyzer["analyzer.AnalyzerGroup<br/>Package Extraction"]
        Driver["detector/library.Driver<br/>Vulnerability Detection"]
    end
    
    subgraph "4. RPC Layer (Optional)"
        RPCClient["client.Service<br/>Twirp Client"]
        RPCServer["server.ScanServer<br/>Twirp Server"]
        Convert["rpc.Convert*<br/>Protobuf Conversion"]
    end
    
    subgraph "5. Report Generation"
        Filter["result.Filter<br/>Apply Policies"]
        Writer["report.Write<br/>Format Output"]
    end
    
    CLI --> Flags
    Flags --> ArtifactRun
    ArtifactRun --> Runner
    Runner --> Service
    Service --> Applier
    Applier --> Analyzer
    Service --> Driver
    Runner --> Filter
    Filter --> Writer
    
    Service -.Client Mode.-> RPCClient
    RPCClient --> Convert
    Convert --> RPCServer
    RPCServer --> Service
```

**System Components by Layer**

| Layer | Key Components | Primary Files | Purpose |
|-------|----------------|---------------|---------|
| CLI | `commands.NewApp()`, `flag.GlobalFlagGroup` | `pkg/commands/app.go`, `pkg/flag/` | Parse commands and configuration |
| Orchestration | `artifact.Run()`, `artifact.Runner` | `pkg/commands/artifact/run.go` | Coordinate scan lifecycle |
| Scanning Engine | `scan.Service`, `applier.Applier`, `analyzer.*` | `pkg/scan/`, `pkg/fanal/` | Analyze artifacts and detect issues |
| RPC Layer | `client.Service`, `server.ScanServer` | `pkg/rpc/` | Enable distributed scanning |
| Reporting | `result.Filter`, `report.Write` | `pkg/result/`, `pkg/report/` | Filter and format results |

Sources: [pkg/commands/app.go:68-117](), [pkg/commands/artifact/run.go:79-98](), [pkg/scan/local/service.go:36-52]()

---

## CLI Layer

Trivy's command-line interface is built using Cobra for command management and Viper for configuration. The `commands.NewApp()` function constructs the command hierarchy.

### Command Structure

Each subcommand is created by a factory function that configures flags and prepares the execution context. The root command uses `PersistentPreRunE` to bind flags and initialize the logger.

**CLI Command Flow**

```mermaid
graph LR
    User["User Execution"]
    
    subgraph "Command Dispatch"
        Image["trivy image<br/>NewImageCommand()"]
        FS["trivy fs<br/>NewFilesystemCommand()"]
        Rootfs["trivy rootfs<br/>NewRootfsCommand()"]
        Repo["trivy repo<br/>NewRepositoryCommand()"]
    end
    
    subgraph "Configuration"
        Bind["PersistentPreRunE:<br/>globalFlags.Bind()"]
        Viper["viper.ReadInConfig()<br/>Config Resolution"]
        ToOpts["flags.ToOptions()"]
    end
    
    subgraph "Orchestration"
        Run["RunE:<br/>artifact.Run()"]
        NewRunner["artifact.NewRunner()"]
    end
    
    User --> Image
    User --> FS
    User --> Rootfs
    User --> Repo
    
    Image --> Bind
    FS --> Bind
    Rootfs --> Bind
    Repo --> Bind
    
    Bind --> Viper
    Viper --> ToOpts
    ToOpts --> Run
    Run --> NewRunner
```

**Target Type Mapping**

| Command | Factory Function | Target Kind | Special Behavior |
|---------|------------------|-------------|------------------|
| `trivy image` | `NewImageCommand()` | `TargetContainerImage` | Disables lock file analyzers [pkg/commands/artifact/run.go:201-202]() |
| `trivy fs` | `NewFilesystemCommand()` | `TargetFilesystem` | Disables individual package analyzers [pkg/commands/artifact/run.go:223-225]() |
| `trivy rootfs` | `NewRootfsCommand()` | `TargetRootfs` | Scans expanded rootfs directories |
| `trivy repo` | `NewRepositoryCommand()` | `TargetRepository` | Scans remote git repositories |

Sources: [pkg/commands/app.go:68-117](), [pkg/commands/app.go:184-213](), [pkg/commands/artifact/run.go:49-57]()

### Configuration System

Trivy uses a generic flag system defined in `pkg/flag/options.go`. Configuration follows this precedence: CLI flags > environment variables > config file > defaults.

**Key Code Entities in Configuration**

| Entity | Path | Purpose |
|--------|------|---------|
| `Flag[T]` | [pkg/flag/options.go:36-85]() | Generic struct for CLI flags with Viper integration |
| `GlobalFlagGroup` | [pkg/flag/global_flag.go]() | Universal options like `--cache-dir`, `--quiet`, `--debug` |
| `initConfig()` | [pkg/commands/app.go:149-164]() | Loads YAML configuration via `viper.ReadInConfig()` |
| `ToOptions()` | [pkg/flag/options.go:206-209]() | Converts parsed flags into a unified `flag.Options` struct |

Sources: [pkg/flag/options.go:101-137](), [pkg/commands/app.go:191-203]()

---

## Orchestration Layer

The `artifact.Run()` function orchestrates the complete scan lifecycle. It initializes a `Runner` which manages the vulnerability database, VEX repositories, and WASM modules.

### Scan Lifecycle

**Runner Initialization**

The `artifact.NewRunner` function performs critical setup tasks:
1. **DB Initialization**: Calls `r.initDB()` to update the vulnerability database [pkg/commands/artifact/run.go:146-148]().
2. **VEX Download**: Calls `operation.DownloadVEXRepositories()` [pkg/commands/artifact/run.go:151-153]().
3. **WASM Modules**: Initializes the `module.Manager` to load plugins [pkg/commands/artifact/run.go:156-163]().

**Runner Execution Flow**

```mermaid
graph TB
    subgraph "artifact.NewRunner()"
        InitDB["db.Init()<br/>pkg/db/db.go"]
        InitWASM["module.NewManager()<br/>pkg/module/manager.go"]
    end

    subgraph "Scan Dispatch"
        ScanImage["ScanImage()<br/>pkg/commands/artifact/run.go"]
        ScanFS["ScanFilesystem()<br/>pkg/commands/artifact/run.go"]
    end

    subgraph "Scan Service"
        ServiceScan["Service.Scan()<br/>pkg/scan/local/service.go"]
        ApplyLayers["applier.ApplyLayers()<br/>pkg/fanal/applier/applier.go"]
        ScanTarget["Service.ScanTarget()<br/>pkg/scan/local/service.go"]
    end

    InitDB --> InitWASM
    InitWASM --> ScanImage
    ScanImage --> ServiceScan
    ServiceScan --> ApplyLayers
    ApplyLayers --> ScanTarget
```

Sources: [pkg/commands/artifact/run.go:121-174](), [pkg/commands/artifact/run.go:199-220]()

### Runner Interface

The `Runner` interface defines the contract for all scanning operations:

```go
type Runner interface {
	ScanImage(ctx context.Context, opts flag.Options) (types.Report, error)
	ScanFilesystem(ctx context.Context, opts flag.Options) (types.Report, error)
	ScanRootfs(ctx context.Context, opts flag.Options) (types.Report, error)
	ScanRepository(ctx context.Context, opts flag.Options) (types.Report, error)
	ScanSBOM(ctx context.Context, opts flag.Options) (types.Report, error)
	ScanVM(ctx context.Context, opts flag.Options) (types.Report, error)
	Filter(ctx context.Context, opts flag.Options, report types.Report) (types.Report, error)
	Report(ctx context.Context, opts flag.Options, report types.Report) error
	Close(ctx context.Context) error
}
```

Sources: [pkg/commands/artifact/run.go:79-98]()

---

## Core Scanning Engine

The core engine handles the transition from raw artifact data (layers, files) to structured security findings.

### Local Scan Service

The `local.Service` struct implements the logic for standalone scanning. It uses an `applier.Applier` to merge artifact layers and various scanners for detection.

**Scan Execution Logic**

1. **Layer Application**: `s.applier.ApplyLayers` combines filesystem layers into a single view [pkg/scan/local/service.go:57]().
2. **OS Detection**: Identifies the operating system and handles cases where OS is missing or overridden [pkg/scan/local/service.go:58-92]().
3. **Target Scanning**: `s.ScanTarget` executes the specific scanners (vulnerability, misconfig, secret, license) [pkg/scan/local/service.go:117-164]().

### Subsystem Interaction

| Subsystem | Key Component | Purpose |
|-----------|---------------|---------|
| **Vulnerability** | `osPkgScanner`, `langPkgScanner` | Detects CVEs in OS and language packages [pkg/scan/local/service.go:175-194]() |
| **Misconfiguration** | `misconf.Scanner` | Evaluates Rego policies against config files [pkg/scan/local/service.go:199-206]() |
| **Secrets** | `secret.Scanner` | Searches for hardcoded credentials |
| **Licenses** | `licensing.Scanner` | Identifies software licenses [pkg/scan/local/service.go:142-143]() |

Sources: [pkg/scan/local/service.go:36-52](), [pkg/scan/local/service.go:166-197]()

---

## Data Flow: Artifact to Report

The following diagram illustrates the lifecycle of a scan request, bridging natural language concepts to specific code entities.

**Trivy Scan Pipeline**

```mermaid
graph TB
    subgraph "Natural Language: Input"
        Input["'trivy image alpine'"]
    end

    subgraph "Code: CLI & Orchestration"
        App["commands.NewApp()"]
        RunFunc["artifact.Run()"]
        RunnerObj["artifact.runner"]
    end

    subgraph "Code: Core Engine"
        ScanService["local.Service"]
        Applier["applier.Applier"]
        VulnDetector["vulnerability.Client"]
    end

    subgraph "Code: Data & Output"
        TrivyDB["db.Client<br/>pkg/db/db.go"]
        ReportObj["types.Report<br/>pkg/types/report.go"]
        Writer["pkgReport.Write()"]
    end

    Input --> App
    App --> RunFunc
    RunFunc --> RunnerObj
    RunnerObj --> ScanService
    ScanService --> Applier
    ScanService --> VulnDetector
    VulnDetector --> TrivyDB
    ScanService --> ReportObj
    ReportObj --> Writer
```

Sources: [pkg/commands/app.go:68](), [pkg/commands/artifact/run.go:121](), [pkg/scan/local/service.go:55](), [pkg/db/db.go:71]()

### Database Management

The `db.Client` manages the lifecycle of the vulnerability database. It checks for updates by comparing local metadata with remote versions.

**Database Logic**
- **NeedsUpdate**: Checks if the schema version matches and if the database is stale [pkg/db/db.go:105-161]().
- **Download**: Fetches the database as an OCI artifact [pkg/db/db.go:187-196]().
- **Schema Validation**: Ensures the local `trivy.db` is compatible with the current CLI version [pkg/db/db.go:163-170]().

Sources: [pkg/db/db.go:71-102](), [pkg/db/db.go:205-222]()

---

# Page: Database and Resource Management

# Database and Resource Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cmd/trivy/main.go](cmd/trivy/main.go)
- [integration/module_test.go](integration/module_test.go)
- [internal/dbtest/db.go](internal/dbtest/db.go)
- [internal/hooktest/hook.go](internal/hooktest/hook.go)
- [internal/registrytest/registrytest.go](internal/registrytest/registrytest.go)
- [pkg/attestation/attestation.go](pkg/attestation/attestation.go)
- [pkg/db/db.go](pkg/db/db.go)
- [pkg/db/db_test.go](pkg/db/db_test.go)
- [pkg/extension/hook.go](pkg/extension/hook.go)
- [pkg/extension/hook_test.go](pkg/extension/hook_test.go)
- [pkg/fanal/analyzer/language/java/jar/jar.go](pkg/fanal/analyzer/language/java/jar/jar.go)
- [pkg/fanal/analyzer/language/java/jar/jar_test.go](pkg/fanal/analyzer/language/java/jar/jar_test.go)
- [pkg/fanal/artifact/image/remote_sbom.go](pkg/fanal/artifact/image/remote_sbom.go)
- [pkg/fanal/artifact/image/remote_sbom_test.go](pkg/fanal/artifact/image/remote_sbom_test.go)
- [pkg/fanal/artifact/image/testdata/sigstore-bundle.json](pkg/fanal/artifact/image/testdata/sigstore-bundle.json)
- [pkg/flag/db_flags.go](pkg/flag/db_flags.go)
- [pkg/flag/db_flags_test.go](pkg/flag/db_flags_test.go)
- [pkg/flag/module_flags.go](pkg/flag/module_flags.go)
- [pkg/javadb/client.go](pkg/javadb/client.go)
- [pkg/module/command.go](pkg/module/command.go)
- [pkg/module/module.go](pkg/module/module.go)
- [pkg/module/module_test.go](pkg/module/module_test.go)
- [pkg/oci/artifact.go](pkg/oci/artifact.go)
- [pkg/oci/artifact_test.go](pkg/oci/artifact_test.go)

</details>



This document details Trivy's database and resource management system, which handles the lifecycle of vulnerability databases, Java databases, WASM modules, and caching mechanisms. The system manages multiple resource types: vulnerability databases containing CVE information, Java-specific vulnerability data, and WASM modules for extensibility.

For information about how databases are used during scanning operations, see page 4.1. For details about policy execution, see page 4.2. For WASM module extensibility, see page 3.3.

## Overview

Trivy's resource management is built primarily around OCI (Open Container Initiative) artifacts stored in container registries. The system automatically downloads, updates, and caches databases from remote repositories, with built-in fallback mechanisms and schema version compatibility checking.

## Resource Types

### Vulnerability Database (trivy-db)

The vulnerability database contains CVE data, package vulnerability mappings, and security advisories. It is managed by `db.Client` and stored as a BoltDB database file named `trivy.db` [pkg/db/db.go:71-77]().

**Key characteristics:**
- **Schema Versioning**: Uses `db.SchemaVersion` to ensure compatibility [pkg/db/db.go:24-27]().
- **Storage**: Located in `{cacheDir}/db/` [pkg/db/db.go:79-81]().
- **Backend**: Utilizes `bbolt` for a key-value store, typically opened in read-only mode [pkg/db/db.go:13-16](), [pkg/db/db.go:42-46]().
- **Metadata**: Tracks `DownloadedAt`, `NextUpdate`, and `Version` in `metadata.json` [pkg/db/db.go:104-121]().

**Default repositories:**
- Primary: `mirror.gcr.io/aquasec/trivy-db` [pkg/db/db.go:35-36]().
- Secondary: `ghcr.io/aquasecurity/trivy-db` [pkg/db/db.go:31-32]().

### Java Database (trivy-java-db)

The Java database provides an index for mapping Java ARchive (JAR) SHA-1 hashes to Maven coordinates (GroupId, ArtifactId, Version). It is stored in `{cacheDir}/java-db/` [pkg/javadb/client.go:142-144]().

**Key characteristics:**
- **Schema Versioning**: Managed via `javadb.SchemaVersion` [pkg/javadb/client.go:24-25]().
- **Backend**: SQLite database (requires `modernc.org/sqlite` driver) [cmd/trivy/main.go:15-16]().
- **Update Cycle**: Cached for 3 days by default, but checks for updates every 24 hours [pkg/javadb/client.go:80-82](), [pkg/javadb/client.go:94-97]().
- **Lookup Support**: Supports searching by SHA-1 hash or ArtifactID [pkg/javadb/client.go:171-184]().

Sources: [pkg/db/db.go:24-46](), [pkg/javadb/client.go:24-35](), [pkg/javadb/client.go:142-144](), [cmd/trivy/main.go:15-16]()

### Module System (WASM)

Trivy supports extensibility via WebAssembly (WASM) modules. These modules can implement custom analyzers or post-scanning hooks. They are managed by `module.Manager` [pkg/module/module.go:89-94]().

**Key characteristics:**
- **Runtime**: Powered by `wazero` for high-performance, zero-dependency WASM execution [pkg/module/module.go:15-17]().
- **Discovery**: Scans the configured module directory for `.wasm` files [pkg/module/module.go:120-126]().
- **Isolation**: Modules operate in a restricted environment with specific host functions for logging and memory management [pkg/module/module.go:29-36]().
- **Registration**: Modules register themselves as `analyzer.Analyzer` or `extension.Hook` [pkg/module/module.go:162-166]().

Sources: [pkg/module/module.go:89-111](), [pkg/module/module.go:120-153]()

## Resource Management Architecture

The following diagram bridges the high-level resource concepts to the specific code entities responsible for managing them.

**Database and Resource Management Architecture**

```mermaid
graph TB
    subgraph "Logic Layer (Code Entities)"
        dbClient["pkg/db.Client"]
        javaUpdater["pkg/javadb.Updater"]
        modManager["pkg/module.Manager"]
        ociArt["pkg/oci.Artifact"]
    end
    
    subgraph "Storage Layer (Filesystem)"
        cacheDir["Cache Directory"]
        dbFile["db/trivy.db (BoltDB)"]
        javaFile["java-db/trivy-java.db (SQLite)"]
        modFiles["modules/*.wasm"]
        metaDB["db/metadata.json"]
    end
    
    subgraph "Remote Layer (OCI Registries)"
        ghcrDB["ghcr.io/aquasecurity/trivy-db"]
        gcrJava["mirror.gcr.io/aquasec/trivy-java-db"]
    end

    dbClient --> ociArt
    javaUpdater --> ociArt
    ociArt --> ghcrDB
    ociArt --> gcrJava
    
    dbClient --> dbFile
    dbClient --> metaDB
    javaUpdater --> javaFile
    modManager --> modFiles
    
    cacheDir --> dbFile
    cacheDir --> javaFile
    cacheDir --> modFiles
```

Sources: [pkg/db/db.go:71-102](), [pkg/javadb/client.go:39-46](), [pkg/module/module.go:89-94](), [pkg/oci/artifact.go:59-68]()

## Update Decision Logic

Trivy evaluates whether a database update is required based on file existence, schema version, and time-based thresholds.

```mermaid
flowchart TD
    A["db.Client.NeedsUpdate()"] --> B{"Files Exist?"}
    B -- "No" --> C["Return true (Update Required)"]
    B -- "Yes" --> D{"--skip-db-update?"}
    
    D -- "Yes" --> E["Validate Schema Version"]
    E -- "Mismatch" --> F["Return Error"]
    E -- "Match" --> G["Return false (Skip)"]
    
    D -- "No" --> H{"Schema Version Match?"}
    H -- "No" --> I["Return true"]
    H -- "Yes" --> J{"Within Update Window?"}
    
    J -- "Yes (Local is Latest)" --> K["Return false"]
    J -- "No" --> L{"Downloaded in last hour?"}
    L -- "Yes" --> K
    L -- "No" --> C
```

**Key Update Thresholds:**
- **Vulnerability DB**: Skips update if the local DB was downloaded within the last hour [pkg/db/db.go:179-183]().
- **Java DB**: Skips update if the local DB was downloaded within the last 24 hours [pkg/javadb/client.go:94-97]().
- **Schema Mismatch**: If the local schema version is older than `db.SchemaVersion`, an update is forced [pkg/db/db.go:154-158](). If it is newer, the CLI requires an update [pkg/db/db.go:139-143]().

Sources: [pkg/db/db.go:105-161](), [pkg/db/db.go:172-184](), [pkg/javadb/client.go:87-99]()

## OCI Artifact Download Process

Trivy treats databases as single-layer OCI artifacts. The `pkg/oci` package provides the underlying mechanism for fetching these layers.

**Artifact Download Sequence**

```mermaid
sequenceDiagram
    participant Client as "db.Client / javadb.Updater"
    participant OCI as "oci.Artifacts"
    participant Registry as "OCI Registry (GHCR/GCR)"
    participant FS as "Local Filesystem"

    Client->>OCI: Download(ctx, dstDir, opt)
    Note over OCI: Iterate through prioritized repositories
    OCI->>Registry: Fetch Manifest
    Registry-->>OCI: Manifest (Layer Digest)
    OCI->>Registry: Download Layer (Compressed Tarball)
    Registry-->>OCI: stream
    OCI->>FS: Save to Temp File
    Note over OCI: Decompress and Extract
    FS->>FS: Move to destination (dbDir)
    OCI-->>Client: Success
```

**Implementation Details:**
- **Single Layer**: Trivy expects the artifact to consist of exactly one layer [pkg/oci/artifact.go:130-132]().
- **Progress Bar**: Downloads show a progress bar unless the `Quiet` option is set [pkg/oci/artifact.go:174-179]().
- **Media Types**: Validates layers against specific media types like `application/vnd.aquasec.trivy.db.layer.v1.tar+gzip` [pkg/db/db.go:26-27](), [pkg/oci/artifact.go:147-152]().

Sources: [pkg/oci/artifact.go:114-159](), [pkg/oci/artifact.go:246-258](), [pkg/db/db.go:187-196]()

## Java Database Specifics

The Java DB is essential for analyzing JAR/WAR/EAR files where `pom.properties` or `MANIFEST.MF` might be missing.

- **Initialization**: `javadb.Init` sets up the global updater with registry options and repositories [pkg/javadb/client.go:116-124]().
- **Lazy Update**: `javadb.NewClient()` triggers an update check only once per run using `sync.Once` [pkg/javadb/client.go:132-135](), [pkg/javadb/client.go:150-161]().
- **Post-Analysis**: The `javaLibraryAnalyzer` (registered as `analyzer.TypeJar`) uses the Java DB to resolve package identities during the post-analysis phase [pkg/fanal/analyzer/language/java/jar/jar.go:45-62]().

Sources: [pkg/javadb/client.go:116-161](), [pkg/fanal/analyzer/language/java/jar/jar.go:45-56]()

## Cache Management and Flags

Users control database behavior via CLI flags defined in `pkg/flag/db_flags.go`.

| Flag | Option Field | Description |
|------|--------------|-------------|
| `--skip-db-update` | `SkipDBUpdate` | Skips vulnerability DB update check [pkg/flag/db_flags.go:27-37](). |
| `--skip-java-db-update` | `SkipJavaDBUpdate` | Skips Java index DB update check [pkg/flag/db_flags.go:43-47](). |
| `--db-repository` | `DBRepositories` | List of OCI repos for vulnerability DB [pkg/flag/db_flags.go:53-58](). |
| `--java-db-repository` | `JavaDBRepositories` | List of OCI repos for Java DB [pkg/flag/db_flags.go:59-64](). |
| `--download-db-only` | `DownloadDBOnly` | Exits after downloading DB [pkg/flag/db_flags.go:22-26](). |

**Cleanup**:
The command `trivy clean` (managed by `pkg/commands/operation`) calls:
- `db.Client.Clear()` to remove the vulnerability database [pkg/db/db.go:198-203]().
- `javadb.Clear()` to remove the Java index [pkg/javadb/client.go:138-140]().

Sources: [pkg/flag/db_flags.go:14-110](), [pkg/db/db.go:198-203](), [pkg/javadb/client.go:138-140]()

---

# Page: CLI Reference

# CLI Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [go.mod](go.mod)
- [go.sum](go.sum)
- [mkdocs.yml](mkdocs.yml)
- [pkg/commands/app.go](pkg/commands/app.go)
- [pkg/commands/app_test.go](pkg/commands/app_test.go)
- [pkg/commands/artifact/run.go](pkg/commands/artifact/run.go)
- [pkg/commands/testdata/java-db/metadata.json](pkg/commands/testdata/java-db/metadata.json)
- [pkg/commands/testdata/policy/metadata.json](pkg/commands/testdata/policy/metadata.json)
- [pkg/dependency/parser/gradle/lockfile/parse.go](pkg/dependency/parser/gradle/lockfile/parse.go)
- [pkg/dependency/parser/gradle/lockfile/parse_test.go](pkg/dependency/parser/gradle/lockfile/parse_test.go)
- [pkg/dependency/parser/gradle/lockfile/testdata/happy.lockfile](pkg/dependency/parser/gradle/lockfile/testdata/happy.lockfile)
- [pkg/dependency/parser/ruby/gemspec/parse.go](pkg/dependency/parser/ruby/gemspec/parse.go)
- [pkg/fanal/analyzer/language/java/gradle/lockfile.go](pkg/fanal/analyzer/language/java/gradle/lockfile.go)
- [pkg/fanal/analyzer/language/java/gradle/lockfile_test.go](pkg/fanal/analyzer/language/java/gradle/lockfile_test.go)
- [pkg/fanal/analyzer/language/java/gradle/pom.go](pkg/fanal/analyzer/language/java/gradle/pom.go)
- [pkg/fanal/analyzer/language/java/gradle/pom_test.go](pkg/fanal/analyzer/language/java/gradle/pom_test.go)
- [pkg/fanal/analyzer/language/java/gradle/testdata/cache/caches/modules-2/files-2.1/junit/junit/4.13/5c17760663fae422643fc859fd352c68a1d91bfc/junit-4.13.pom](pkg/fanal/analyzer/language/java/gradle/testdata/cache/caches/modules-2/files-2.1/junit/junit/4.13/5c17760663fae422643fc859fd352c68a1d91bfc/junit-4.13.pom)
- [pkg/fanal/analyzer/language/java/gradle/testdata/cache/caches/modules-2/files-2.1/org.hamcrest/hamcrest-core/1.3/872e413497b906e7c9fa85ccc96046c5d1ef7ece/hamcrest-core-1.3.pom](pkg/fanal/analyzer/language/java/gradle/testdata/cache/caches/modules-2/files-2.1/org.hamcrest/hamcrest-core/1.3/872e413497b906e7c9fa85ccc96046c5d1ef7ece/hamcrest-core-1.3.pom)
- [pkg/flag/misconf_flags.go](pkg/flag/misconf_flags.go)
- [pkg/flag/options.go](pkg/flag/options.go)
- [pkg/flag/options_test.go](pkg/flag/options_test.go)
- [pkg/flag/report_flags.go](pkg/flag/report_flags.go)
- [pkg/flag/report_flags_test.go](pkg/flag/report_flags_test.go)
- [pkg/flag/scan_flags.go](pkg/flag/scan_flags.go)
- [pkg/flag/scan_flags_test.go](pkg/flag/scan_flags_test.go)
- [pkg/flag/vulnerability_flags.go](pkg/flag/vulnerability_flags.go)
- [pkg/iac/scanners/cloudformation/parser/fn_split.go](pkg/iac/scanners/cloudformation/parser/fn_split.go)
- [pkg/x/strings/strings.go](pkg/x/strings/strings.go)

</details>



This document provides a comprehensive reference for Trivy's command-line interface. It explains how Trivy's commands are organized, the overall command execution flow, and how the CLI integrates with the core scanning engine.

For detailed information on command structure and global flags, see [Command Structure and Global Flags](#2.1). For specifics on individual scan commands, see [Scan Commands and Target Options](#2.2). For misconfiguration-specific options, see [Misconfiguration Scanning Configuration](#2.3). For details on configuration files and environment variables, see [Configuration Files and Environment Variables](#2.4).

## Application Architecture

Trivy's CLI is built using the `spf13/cobra` framework and organized into logical command groups. The `NewApp()` function in [pkg/commands/app.go:68-117]() constructs the application by creating the root command and registering all subcommands.

**Command Registration in NewApp()**

```mermaid
graph TB
    NewApp["NewApp()"]
    NewApp --> rootCmd["NewRootCommand(globalFlags)"]
    NewApp --> AddGroup["rootCmd.AddGroup()"]
    
    AddGroup --> scanGroup["groupScanning"]
    AddGroup --> mgmtGroup["groupManagement"]
    AddGroup --> utilGroup["groupUtility"]
    
    NewApp --> AddCommand["rootCmd.AddCommand()"]
    
    AddCommand --> scanCmds["Scanning Commands"]
    AddCommand --> mgmtCmds["Management Commands"]
    AddCommand --> utilCmds["Utility Commands"]
    AddCommand --> pluginCmds["Plugin Commands"]
    
    scanCmds --> NewImageCommand["NewImageCommand()"]
    scanCmds --> NewFilesystemCommand["NewFilesystemCommand()"]
    scanCmds --> NewRootfsCommand["NewRootfsCommand()"]
    scanCmds --> NewRepositoryCommand["NewRepositoryCommand()"]
    scanCmds --> NewConfigCommand["NewConfigCommand()"]
    scanCmds --> NewKubernetesCommand["NewKubernetesCommand()"]
    scanCmds --> NewSBOMCommand["NewSBOMCommand()"]
    scanCmds --> NewVMCommand["NewVMCommand()"]
    
    mgmtCmds --> NewServerCommand["NewServerCommand()"]
    mgmtCmds --> NewModuleCommand["NewModuleCommand()"]
    mgmtCmds --> NewPluginCommand["NewPluginCommand()"]
    mgmtCmds --> NewRegistryCommand["NewRegistryCommand()"]
    mgmtCmds --> NewVEXCommand["NewVEXCommand()"]
    
    utilCmds --> NewConvertCommand["NewConvertCommand()"]
    utilCmds --> NewCleanCommand["NewCleanCommand()"]
    utilCmds --> NewVersionCommand["NewVersionCommand()"]
    
    pluginCmds --> loadPluginCommands["loadPluginCommands()"]
```

**Command Groups and Organization**

Commands are organized into four primary groups defined in [pkg/commands/app.go:61-65]():

| Group | ID | Purpose | Commands |
|-------|-------|---------|----------|
| Scanning | `groupScanning` | Artifact and environment scanning | `image`, `fs`, `rootfs`, `repo`, `config`, `k8s`, `sbom`, `vm` |
| Management | `groupManagement` | Database and service management | `server`, `module`, `plugin`, `registry`, `vex` |
| Utility | `groupUtility` | Helper and conversion tools | `convert`, `clean`, `version`, `completion` |
| Plugin | `groupPlugin` | External plugin commands | Loaded dynamically via `loadPluginCommands` |

Sources: [pkg/commands/app.go:61-117](), [pkg/commands/app.go:119-147]()

## Command Execution Flow

Each scanning command follows a consistent execution pattern from command invocation through result reporting. The flow uses the `artifact.Runner` interface and its implementations in [pkg/commands/artifact/run.go:79-98]() as the primary orchestrator.

**Typical Scan Command Execution Flow**

```mermaid
sequenceDiagram
    participant User
    participant Cobra as "Cobra Command"
    participant PreRunE as "PersistentPreRunE"
    participant RunE as "RunE"
    participant FlagOpts as "flag.Flags.ToOptions()"
    participant Runner as "artifact.NewRunner()"
    participant Scanner as "r.ScanImage/FS/etc."
    
    User->>Cobra: trivy image python:3.4
    Cobra->>PreRunE: Execute Root PreRun
    PreRunE->>PreRunE: Bind flags (viper) [pkg/commands/app.go:191]
    PreRunE->>PreRunE: initConfig() [pkg/commands/app.go:201]
    PreRunE->>PreRunE: log.InitLogger() [pkg/commands/app.go:211]
    
    Cobra->>RunE: Execute Command Run
    RunE->>FlagOpts: Convert flags to Options [pkg/flag/options.go:457]
    FlagOpts->>RunE: flag.Options
    
    RunE->>Runner: NewRunner(ctx, opts, TargetKind) [pkg/commands/artifact/run.go:121]
    Runner->>Runner: initDB() / Download VEX / WASM [pkg/commands/artifact/run.go:146-163]
    
    RunE->>Scanner: r.ScanImage(ctx, opts) [pkg/commands/artifact/run.go:199]
    Scanner->>User: types.Report
```

**Command Lifecycle Hooks**

Trivy commands use Cobra's lifecycle hooks defined in [pkg/commands/app.go:166-227]():

1. **PersistentPreRunE**: Executed before any command runs.
   - Binds CLI flags to `viper` configuration.
   - Initializes configuration file (default or `--config`).
   - Initializes the logger with `debug` and `quiet` settings.

2. **RunE**: Main command execution.
   - Converts flags to the unified `flag.Options` struct.
   - Customizes version output if `--version` is passed.
   - Calls the underlying scanning service via `artifact.Runner`.

Sources: [pkg/commands/app.go:184-227](), [pkg/commands/artifact/run.go:121-174]()

## Flag System Architecture

Trivy's flag system provides a type-safe, flexible mechanism for configuration. The system is built around the `Flag[T]` struct [pkg/flag/options.go:36-85]() and organized into `FlagGroups`.

**Flag Processing Architecture**

```mermaid
graph TB
    subgraph "Configuration Sources"
        CLI["CLI Flags"]
        ENV["TRIVY_* Env Vars"]
        Config["trivy.yaml"]
    end
    
    subgraph "Logic Entities"
        Viper["viper.Viper"]
        FlagT["flag.Flag[T]"]
        Group["flag.ScanFlagGroup"]
        Opts["flag.Options"]
    end

    CLI --> Viper
    ENV --> Viper
    Config --> Viper
    
    Viper --> FlagT
    FlagT --> Group
    Group --> Opts
```

**Flag Group Implementation**

Each command constructs its flag set by combining relevant flag groups. For example, `NewImageCommand` includes `ScanFlagGroup`, `ReportFlagGroup`, `VulnerabilityFlagGroup`, and more.

The `Flag[T]` struct handles:
- **Parsing**: Resolving values from CLI, Env, or Config [pkg/flag/options.go:101-137]().
- **Validation**: Checking against `Values` list [pkg/flag/options.go:203-218]().
- **Deprecation**: Warning users about outdated flags [pkg/flag/options.go:127-129]().

Sources: [pkg/flag/options.go:36-85](), [pkg/flag/options.go:167-192]()

## Major Flag Groups

### Report Flag Group
Controls output formatting, filtering, and compliance reporting. Defined in [pkg/flag/report_flags.go:133-149]().

| Flag | Shorthand | Default | Purpose |
|------|-----------|---------|---------|
| `--format` | `-f` | `table` | Output format (json, sarif, cyclonedx, etc.) |
| `--severity` | `-s` | All | Filter by severity levels (CRITICAL, HIGH, etc.) |
| `--output` | `-o` | stdout | Write results to a file |
| `--template` | `-t` | - | Go template for custom formatting |

Sources: [pkg/flag/report_flags.go:29-129]()

### Scan Flag Group
Controls scanning behavior and performance. Defined in [pkg/flag/scan_flags.go:140-154]().

- `--scanners`: Comma-separated list of security issues to detect (`vuln`, `misconf`, `secret`, `license`).
- `--skip-dirs`: Directories or glob patterns to skip.
- `--parallel`: Number of goroutines for parallel scanning (default 5).
- `--offline-scan`: Do not issue API requests for dependency identification.

Sources: [pkg/flag/scan_flags.go:17-138]()

### Misconfiguration Flag Group
Handles IaC-specific settings for Terraform, Helm, CloudFormation, and Ansible. Defined in [pkg/flag/misconf_flags.go:147-170]().

- `--helm-values`: Override Helm `values.yaml` files.
- `--tf-vars`: Override Terraform `tfvars` files.
- `--include-non-failures`: Include successful checks in the report.
- `--checks-bundle-repository`: OCI registry URL for the checks bundle.

Sources: [pkg/flag/misconf_flags.go:22-144]()

## Configuration Resolution Priority

Trivy resolves configuration from multiple sources with a defined precedence order:

1. **CLI Flags** (Highest Priority)
2. **Environment Variables** (e.g., `TRIVY_FORMAT=json`)
3. **Configuration File** (`trivy.yaml`)
4. **Default Values** (Lowest Priority)

Environment variables are automatically mapped from flag names by converting to uppercase and replacing hyphens with underscores (e.g., `--cache-dir` becomes `TRIVY_CACHE_DIR`).

Sources: [pkg/flag/options.go:139-164](), [pkg/commands/app.go:149-164]()

---

# Page: Command Structure and Global Flags

# Command Structure and Global Flags

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [go.mod](go.mod)
- [go.sum](go.sum)
- [magefiles/config_schema.go](magefiles/config_schema.go)
- [magefiles/docs.go](magefiles/docs.go)
- [mkdocs.yml](mkdocs.yml)
- [pkg/commands/app.go](pkg/commands/app.go)
- [pkg/commands/app_test.go](pkg/commands/app_test.go)
- [pkg/commands/artifact/run.go](pkg/commands/artifact/run.go)
- [pkg/commands/testdata/java-db/metadata.json](pkg/commands/testdata/java-db/metadata.json)
- [pkg/commands/testdata/policy/metadata.json](pkg/commands/testdata/policy/metadata.json)
- [pkg/dependency/parser/gradle/lockfile/parse.go](pkg/dependency/parser/gradle/lockfile/parse.go)
- [pkg/dependency/parser/gradle/lockfile/parse_test.go](pkg/dependency/parser/gradle/lockfile/parse_test.go)
- [pkg/dependency/parser/gradle/lockfile/testdata/happy.lockfile](pkg/dependency/parser/gradle/lockfile/testdata/happy.lockfile)
- [pkg/dependency/parser/ruby/gemspec/parse.go](pkg/dependency/parser/ruby/gemspec/parse.go)
- [pkg/fanal/analyzer/language/java/gradle/lockfile.go](pkg/fanal/analyzer/language/java/gradle/lockfile.go)
- [pkg/fanal/analyzer/language/java/gradle/lockfile_test.go](pkg/fanal/analyzer/language/java/gradle/lockfile_test.go)
- [pkg/fanal/analyzer/language/java/gradle/pom.go](pkg/fanal/analyzer/language/java/gradle/pom.go)
- [pkg/fanal/analyzer/language/java/gradle/pom_test.go](pkg/fanal/analyzer/language/java/gradle/pom_test.go)
- [pkg/fanal/analyzer/language/java/gradle/testdata/cache/caches/modules-2/files-2.1/junit/junit/4.13/5c17760663fae422643fc859fd352c68a1d91bfc/junit-4.13.pom](pkg/fanal/analyzer/language/java/gradle/testdata/cache/caches/modules-2/files-2.1/junit/junit/4.13/5c17760663fae422643fc859fd352c68a1d91bfc/junit-4.13.pom)
- [pkg/fanal/analyzer/language/java/gradle/testdata/cache/caches/modules-2/files-2.1/org.hamcrest/hamcrest-core/1.3/872e413497b906e7c9fa85ccc96046c5d1ef7ece/hamcrest-core-1.3.pom](pkg/fanal/analyzer/language/java/gradle/testdata/cache/caches/modules-2/files-2.1/org.hamcrest/hamcrest-core/1.3/872e413497b906e7c9fa85ccc96046c5d1ef7ece/hamcrest-core-1.3.pom)
- [pkg/flag/global_flags.go](pkg/flag/global_flags.go)
- [pkg/flag/options.go](pkg/flag/options.go)
- [pkg/flag/options_test.go](pkg/flag/options_test.go)
- [pkg/flag/report_flags.go](pkg/flag/report_flags.go)
- [pkg/flag/report_flags_test.go](pkg/flag/report_flags_test.go)
- [pkg/flag/scan_flags.go](pkg/flag/scan_flags.go)
- [pkg/flag/scan_flags_test.go](pkg/flag/scan_flags_test.go)
- [pkg/flag/vulnerability_flags.go](pkg/flag/vulnerability_flags.go)
- [pkg/iac/scanners/cloudformation/parser/fn_split.go](pkg/iac/scanners/cloudformation/parser/fn_split.go)
- [pkg/x/strings/strings.go](pkg/x/strings/strings.go)
- [schema/trivy-config.json](schema/trivy-config.json)

</details>



This page documents Trivy's command-line interface structure, including the root command, command groups, and global flags that apply across all operations. For details on individual scan commands and their specific options, see [Scan Commands and Target Options](2.2). For configuration file and environment variable handling, see [Configuration Files and Environment Variables](2.4).

## Overview

Trivy's CLI is built using the `spf13/cobra` library and follows a hierarchical command structure with a root command, multiple subcommands organized into logical groups, and a comprehensive flag system. The application supports both CLI flags and configuration files through `spf13/viper` integration.

**Sources:** [pkg/commands/app.go:66-116](), [README.md:60-99](), [go.mod:104-106]()

## Command Hierarchy

The command structure is defined in `NewApp()` which creates the root command and adds subcommands organized into groups: scanning, management, utility, and plugin commands.

### Logical Command Mapping

The following diagram bridges the CLI command space to the internal Go functions that initialize them.

| Diagram Title: CLI Command to Function Mapping |
| :--- |
```mermaid
graph TD
    subgraph "CLI Entry Point"
        Root["trivy (Root)"]
    end

    subgraph "Scanning Group (groupScanning)"
        Image["image"] --> f1["NewImageCommand()"]
        FS["fs / filesystem"] --> f2["NewFilesystemCommand()"]
        Repo["repo / repository"] --> f3["NewRepositoryCommand()"]
        K8s["k8s / kubernetes"] --> f4["NewKubernetesCommand()"]
        SBOM["sbom"] --> f5["NewSBOMCommand()"]
        Conf["config"] --> f6["NewConfigCommand()"]
    end

    subgraph "Management Group (groupManagement)"
        Server["server"] --> f7["NewServerCommand()"]
        Plugin["plugin"] --> f8["NewPluginCommand()"]
        Module["module"] --> f9["NewModuleCommand()"]
    end

    subgraph "Utility Group (groupUtility)"
        Clean["clean"] --> f10["NewCleanCommand()"]
        Conv["convert"] --> f11["NewConvertCommand()"]
        Ver["version"] --> f12["NewVersionCommand()"]
    end

    Root --> Scanning
    Root --> Management
    Root --> Utility
```
**Sources:** [pkg/commands/app.go:68-106](), [pkg/commands/app.go:60-64]()

## Root Command

The root command is created by `NewRootCommand()` and serves as the entry point for all Trivy operations.

| Attribute | Value |
|-----------|-------|
| **Use** | `trivy [global flags] command [flags] target` |
| **Short** | `Unified security scanner` |
| **Long** | Scanner for vulnerabilities in container images, file systems, and Git repositories, as well as for configuration issues and hard-coded secrets |

### Root Command Lifecycle

The root command includes a `PersistentPreRunE` hook that executes before any subcommand and performs critical initialization:

1. **Version Injection**: Sets the version from `app.Version()` [pkg/commands/app.go:186]().
2. **Flag Binding**: Binds `GlobalFlagGroup` to Viper via `globalFlags.Bind(cmd)` [pkg/commands/app.go:191]().
3. **Config Initialization**: Loads the YAML config file via `initConfig()` [pkg/commands/app.go:201]().
4. **Logger Setup**: Initializes the global logger using parsed options [pkg/commands/app.go:211]().

**Sources:** [pkg/commands/app.go:165-234](), [pkg/commands/app.go:184-213]()

## Global Flags

Global flags are defined in `flag.GlobalFlagGroup` and apply to all commands. They are inherited by all subcommands because they are registered as `PersistentFlags` [pkg/flag/options.go:271-272]().

### Key Global Flags

| Flag | Config Name | Default | Description |
|------|-------------|---------|-------------|
| `--quiet, -q` | `quiet` | `false` | Suppress progress bar and log output |
| `--debug, -d` | `debug` | `false` | Enable debug mode |
| `--cache-dir` | `cache-dir` | OS-specific | Cache directory for vulnerability database |
| `--config` | `config` | `trivy.yaml` | Path to configuration file |
| `--version, -v` | `version` | `false` | Show version information |
| `--timeout` | `timeout` | `5m` | Timeout for scanning |
| `--insecure` | `insecure` | `false` | Allow insecure server connections |

**Sources:** [pkg/flag/options.go:401-438](), [pkg/commands/app.go:69-70]()

## Flag System Architecture

Trivy uses a custom type-safe flag system defined in `pkg/flag`. Each flag is an instance of the generic `Flag[T]` struct.

### Data Flow: From Input to Options

| Diagram Title: Configuration Data Flow and Normalization |
| :--- |
```mermaid
flowchart TD
    subgraph "Input Sources"
        CLI["CLI Flags (--scanners)"]
        ENV["Env Vars (TRIVY_SCANNERS)"]
        YAML["trivy.yaml (scan.scanners)"]
    end

    subgraph "Viper Orchestration"
        VBind["viper.BindPFlag()"]
        VGet["viper.Get()"]
    end

    subgraph "Flag[T] Logic"
        Parse["Flag.Parse()"]
        Norm["ValueNormalize()"]
        Validate["allowedValue()"]
    end

    subgraph "Final Object"
        Opts["flag.Options struct"]
    end

    CLI --> VBind
    ENV --> VBind
    YAML --> VBind
    VBind --> VGet
    VGet --> Parse
    Parse --> Norm
    Norm --> Validate
    Validate --> Opts
```

### Type-Safe Flag Handling
The `Flag[T]` struct (where `T` is `int`, `string`, `bool`, etc.) handles:
- **Normalization**: Converting aliases (e.g., `config` to `misconfig`) via `ValueNormalize` [pkg/flag/scan_flags.go:48-61]().
- **Validation**: Checking against `Values` slice [pkg/flag/options.go:203-218]().
- **Deprecation**: Logging warnings if a deprecated flag is used [pkg/flag/options.go:127-129]().

**Sources:** [pkg/flag/options.go:32-85](), [pkg/flag/options.go:101-137]()

## Flag Groups

Flags are organized into groups that implement the `Flagger` interface. Commands compose these groups to build their specific flag sets.

| Flag Group | Implementation | Key Responsibility |
|------------|----------------|--------------------|
| `ScanFlagGroup` | `NewScanFlagGroup()` | Handles `--scanners`, `--parallel`, `--skip-dirs` |
| `ReportFlagGroup` | `NewReportFlagGroup()` | Handles `--format`, `--output`, `--severity` |
| `DBFlagGroup` | `NewDBFlagGroup()` | Handles `--skip-db-update`, `--db-repository` |
| `CacheFlagGroup` | `NewCacheFlagGroup()` | Handles `--cache-backend`, `--redis-ca-cert` |

**Sources:** [pkg/flag/scan_flags.go:172-188](), [pkg/flag/report_flags.go:169-187](), [pkg/commands/app.go:254-270]()

## Plugin Command Integration

Trivy dynamically loads plugins and registers them as subcommands.

1. `loadPluginCommands()` calls `plugin.NewManager().LoadAll(ctx)` [pkg/commands/app.go:123]().
2. For each discovered plugin, a new `cobra.Command` is created [pkg/commands/app.go:129]().
3. These commands have `DisableFlagParsing: true` [pkg/commands/app.go:140](), allowing the plugin to handle its own flags.
4. Execution is delegated to `p.Run(ctx, plugin.Options{Args: args})` [pkg/commands/app.go:135]().

**Sources:** [pkg/commands/app.go:119-147]()

## Configuration Priority

The `Flag.Parse()` method relies on `viper.Get(f.ConfigName)` [pkg/flag/options.go:154](). Viper enforces the following precedence:
1. CLI Flags (via `BindPFlag`)
2. Environment Variables (via `BindEnv`)
3. Config File (via `ReadInConfig`)
4. Defaults (via `Flag.Default`)

**Sources:** [pkg/flag/options.go:139-164](), [pkg/commands/app.go:149-164]()

---

# Page: Scan Commands and Target Options

# Scan Commands and Target Options

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/guide/configuration/reporting.md](docs/guide/configuration/reporting.md)
- [docs/guide/references/configuration/cli/trivy_config.md](docs/guide/references/configuration/cli/trivy_config.md)
- [docs/guide/references/configuration/cli/trivy_convert.md](docs/guide/references/configuration/cli/trivy_convert.md)
- [docs/guide/references/configuration/cli/trivy_filesystem.md](docs/guide/references/configuration/cli/trivy_filesystem.md)
- [docs/guide/references/configuration/cli/trivy_image.md](docs/guide/references/configuration/cli/trivy_image.md)
- [docs/guide/references/configuration/cli/trivy_kubernetes.md](docs/guide/references/configuration/cli/trivy_kubernetes.md)
- [docs/guide/references/configuration/cli/trivy_repository.md](docs/guide/references/configuration/cli/trivy_repository.md)
- [docs/guide/references/configuration/cli/trivy_rootfs.md](docs/guide/references/configuration/cli/trivy_rootfs.md)
- [docs/guide/references/configuration/cli/trivy_sbom.md](docs/guide/references/configuration/cli/trivy_sbom.md)
- [docs/guide/references/configuration/cli/trivy_vm.md](docs/guide/references/configuration/cli/trivy_vm.md)
- [go.mod](go.mod)
- [go.sum](go.sum)
- [mkdocs.yml](mkdocs.yml)
- [pkg/commands/app.go](pkg/commands/app.go)
- [pkg/commands/app_test.go](pkg/commands/app_test.go)
- [pkg/commands/artifact/run.go](pkg/commands/artifact/run.go)
- [pkg/commands/testdata/java-db/metadata.json](pkg/commands/testdata/java-db/metadata.json)
- [pkg/commands/testdata/policy/metadata.json](pkg/commands/testdata/policy/metadata.json)
- [pkg/dependency/parser/gradle/lockfile/parse.go](pkg/dependency/parser/gradle/lockfile/parse.go)
- [pkg/dependency/parser/gradle/lockfile/parse_test.go](pkg/dependency/parser/gradle/lockfile/parse_test.go)
- [pkg/dependency/parser/gradle/lockfile/testdata/happy.lockfile](pkg/dependency/parser/gradle/lockfile/testdata/happy.lockfile)
- [pkg/dependency/parser/ruby/gemspec/parse.go](pkg/dependency/parser/ruby/gemspec/parse.go)
- [pkg/fanal/analyzer/language/java/gradle/lockfile.go](pkg/fanal/analyzer/language/java/gradle/lockfile.go)
- [pkg/fanal/analyzer/language/java/gradle/lockfile_test.go](pkg/fanal/analyzer/language/java/gradle/lockfile_test.go)
- [pkg/fanal/analyzer/language/java/gradle/pom.go](pkg/fanal/analyzer/language/java/gradle/pom.go)
- [pkg/fanal/analyzer/language/java/gradle/pom_test.go](pkg/fanal/analyzer/language/java/gradle/pom_test.go)
- [pkg/fanal/analyzer/language/java/gradle/testdata/cache/caches/modules-2/files-2.1/junit/junit/4.13/5c17760663fae422643fc859fd352c68a1d91bfc/junit-4.13.pom](pkg/fanal/analyzer/language/java/gradle/testdata/cache/caches/modules-2/files-2.1/junit/junit/4.13/5c17760663fae422643fc859fd352c68a1d91bfc/junit-4.13.pom)
- [pkg/fanal/analyzer/language/java/gradle/testdata/cache/caches/modules-2/files-2.1/org.hamcrest/hamcrest-core/1.3/872e413497b906e7c9fa85ccc96046c5d1ef7ece/hamcrest-core-1.3.pom](pkg/fanal/analyzer/language/java/gradle/testdata/cache/caches/modules-2/files-2.1/org.hamcrest/hamcrest-core/1.3/872e413497b906e7c9fa85ccc96046c5d1ef7ece/hamcrest-core-1.3.pom)
- [pkg/flag/options.go](pkg/flag/options.go)
- [pkg/flag/options_test.go](pkg/flag/options_test.go)
- [pkg/flag/report_flags.go](pkg/flag/report_flags.go)
- [pkg/flag/report_flags_test.go](pkg/flag/report_flags_test.go)
- [pkg/flag/scan_flags.go](pkg/flag/scan_flags.go)
- [pkg/flag/scan_flags_test.go](pkg/flag/scan_flags_test.go)
- [pkg/flag/vulnerability_flags.go](pkg/flag/vulnerability_flags.go)
- [pkg/iac/scanners/cloudformation/parser/fn_split.go](pkg/iac/scanners/cloudformation/parser/fn_split.go)
- [pkg/x/strings/strings.go](pkg/x/strings/strings.go)

</details>



This page details Trivy's scan commands and their specific target options. Each scan command is designed for a specific artifact type and comes with its own set of flags and configuration options.

## Overview

Trivy provides multiple scan commands implemented as Cobra commands in [pkg/commands/app.go](). Each command is tailored for a specific artifact type and maps to a `TargetKind` constant that drives the scanning workflow through the `Runner` interface defined in [pkg/commands/artifact/run.go:79-98]().

**Command Functions and Target Mapping**

```mermaid
graph TB
    subgraph "Command Functions (pkg/commands/app.go)"
        NewImageCommand["NewImageCommand()"]
        NewFilesystemCommand["NewFilesystemCommand()"]
        NewRootfsCommand["NewRootfsCommand()"]
        NewRepositoryCommand["NewRepositoryCommand()"]
        NewSBOMCommand["NewSBOMCommand()"]
        NewVMCommand["NewVMCommand()"]
        NewConfigCommand["NewConfigCommand()"]
        NewKubernetesCommand["NewKubernetesCommand()"]
    end
    
    subgraph "TargetKind Constants (artifact/run.go:49-57)"
        TargetContainerImage["TargetContainerImage"]
        TargetFilesystem["TargetFilesystem"]
        TargetRootfs["TargetRootfs"]
        TargetRepository["TargetRepository"]
        TargetSBOM["TargetSBOM"]
        TargetVM["TargetVM"]
        TargetK8s["TargetK8s"]
    end
    
    subgraph "Execution Path"
        artifactRun["artifact.NewRunner()"]
        RunnerScan["Runner.ScanImage()<br/>Runner.ScanFilesystem()<br/>Runner.ScanRootfs()<br/>..."]
    end
    
    NewImageCommand --> TargetContainerImage
    NewFilesystemCommand --> TargetFilesystem
    NewRootfsCommand --> TargetRootfs
    NewRepositoryCommand --> TargetRepository
    NewSBOMCommand --> TargetSBOM
    NewVMCommand --> TargetVM
    NewConfigCommand --> TargetFilesystem
    NewKubernetesCommand --> TargetK8s
    
    TargetContainerImage --> artifactRun
    TargetFilesystem --> artifactRun
    TargetRootfs --> artifactRun
    TargetRepository --> artifactRun
    TargetSBOM --> artifactRun
    TargetVM --> artifactRun
    TargetK8s --> artifactRun
    
    artifactRun --> RunnerScan
```

**TargetKind Constants:**
Each `TargetKind` constant determines which `Runner` method is invoked. For example, `TargetContainerImage` leads to `ScanImage` [pkg/commands/artifact/run.go:199-220]().

Sources: [pkg/commands/app.go:88-106](), [pkg/commands/artifact/run.go:49-57](), [pkg/commands/artifact/run.go:121-174](), [pkg/commands/artifact/run.go:199-220]()

## Command Structure

### Command Creation Pattern

All scan commands follow a consistent creation pattern using Cobra commands with flag groups tailored to their specific needs. The `NewApp` function in [pkg/commands/app.go:68-117]() registers these commands.

```mermaid
graph TB
    subgraph "Command Function"
        NEWFUNC["NewXCommand(globalFlags)"]
        FLAGGROUPS["Flag Groups Assembly"]
        FLAGS["flag.Flags collection"]
    end
    
    subgraph "Cobra Command"
        CMD["cobra.Command"]
        PRERUN["PersistentPreRunE:<br/>Bind & Validate"]
        RUN["RunE:<br/>ToOptions & Run"]
    end
    
    subgraph "Execution Flow"
        OPTS["flag.Options"]
        RUNNER["artifact.NewRunner()"]
        SCAN["Runner.ScanXXX()"]
    end
    
    NEWFUNC --> FLAGGROUPS
    FLAGGROUPS --> FLAGS
    FLAGS --> CMD
    CMD --> PRERUN
    PRERUN --> RUN
    RUN --> OPTS
    OPTS --> RUNNER
    RUNNER --> SCAN
```

**Command Lifecycle:**
1. `NewXCommand()` creates the command with appropriate flag groups (e.g., `ScanFlagGroup`, `ReportFlagGroup`).
2. `PersistentPreRunE` in the root command binds flags and initializes the logger [pkg/commands/app.go:184-213]().
3. `RunE` converts flags to options via `flags.ToOptions(args)` [pkg/commands/app.go:214-227]().
4. `artifact.NewRunner()` initializes the scanning service, including the vulnerability database [pkg/commands/artifact/run.go:121-174]().

Sources: [pkg/commands/app.go:68-117](), [pkg/commands/app.go:184-213](), [pkg/commands/artifact/run.go:121-174]()

### Flag Groups by Command

Different commands instantiate different combinations of `FlagGroup` implementations from the `pkg/flag/` package. The configuration is often managed via `viper` [pkg/flag/options.go:101-137]().

| Command | Key Flag Groups | Common Global Flags |
|---------|-----------------|---------------------|
| `image` | `ImageFlagGroup`, `ScanFlagGroup`, `VulnerabilityFlagGroup` | `CacheDir`, `Quiet`, `Debug` |
| `fs` | `ScanFlagGroup`, `MisconfFlagGroup`, `SecretFlagGroup` | `CacheDir`, `Quiet`, `Debug` |
| `repo` | `RepoFlagGroup`, `ScanFlagGroup`, `VulnerabilityFlagGroup` | `CacheDir`, `Quiet`, `Debug` |
| `k8s` | `K8sFlagGroup`, `MisconfFlagGroup`, `ReportFlagGroup` | `CacheDir`, `Quiet`, `Debug` |

**Flag Group Structure:**
Each `FlagGroup` (e.g., `ScanFlagGroup` [pkg/flag/scan_flags.go:140-154]()) defines the flags available to that command and how they map to `Options`.

Sources: [pkg/flag/scan_flags.go:140-154](), [pkg/flag/report_flags.go:133-149](), [pkg/flag/options.go:101-137]()

## Image Command

The `trivy image` command scans container images. It disables lock file scanning by default to focus on installed OS packages [pkg/commands/artifact/run.go:201-202]().

```mermaid
graph LR
    subgraph "Image Scan Modes (artifact/run.go:204-217)"
        STANDALONE["imageStandaloneScanService"]
        REMOTE["imageRemoteScanService"]
        ARCH_STAND["archiveStandaloneScanService"]
        ARCH_REMOTE["archiveRemoteScanService"]
    end
    
    subgraph "Runner Execution"
        SCANIMAGE["Runner.ScanImage()"]
        DIS_ANALYZER["DisabledAnalyzers: analyzer.TypeLockfiles"]
    end
    
    STANDALONE --> SCANIMAGE
    REMOTE --> SCANIMAGE
    ARCH_STAND --> SCANIMAGE
    ARCH_REMOTE --> SCANIMAGE
    SCANIMAGE --> DIS_ANALYZER
```

**Image-Specific Logic:**
- If `--input` is provided, Trivy scans an image tarball instead of pulling from a registry [pkg/commands/artifact/run.go:205-210]().
- If `--server-addr` is set, Trivy operates in client mode, delegating analysis to a remote server [pkg/commands/artifact/run.go:214-217]().

Sources: [pkg/commands/artifact/run.go:199-220](), [pkg/flag/scan_flags.go:35-71]()

## Filesystem and Rootfs Commands

These commands scan local directories or extracted filesystems.

- **Filesystem (`fs`)**: Disables scanning of individual package files and SBOM files to avoid redundant findings [pkg/commands/artifact/run.go:224-225]().
- **Rootfs**: Similar to `fs`, but specifically targets unpacked filesystem trees, often disabling lock file analyzers [pkg/commands/artifact/run.go:230-235]().

Sources: [pkg/commands/artifact/run.go:222-228](), [pkg/commands/artifact/run.go:230-235]()

## Repository Command

The `trivy repo` command targets remote Git repositories.

**Repository Scan Logic**
- It disables OS-level analyzers (`analyzer.TypeOSes`) and individual package analyzers [pkg/commands/artifact/run.go:253-254]().
- It restricts package types to libraries only [pkg/commands/artifact/run.go:255]().

Sources: [pkg/commands/artifact/run.go:250-267]()

## Kubernetes Command

The `trivy k8s` command scans Kubernetes clusters. It uses a specialized `K8sFlagGroup` to handle cluster contexts and namespaces.

**Example Summary Report:**
```bash
trivy k8s --report summary cluster
```
The summary report provides a high-level overview of vulnerabilities and misconfigurations across the cluster [README.md:91-99]().

Sources: [pkg/commands/app.go:99](), [README.md:91-99]()

## Common Scanner Options

Trivy uses a unified flag system where flags like `--scanners` determine what security issues to detect.

### Scanners Flag
The `ScannersFlag` [pkg/flag/scan_flags.go:35-71]() allows users to select:
- `vulnerability` (default)
- `misconfig`
- `secret` (default)
- `license`

It includes value normalization, such as mapping `config` or `misconf` to `misconfig` [pkg/flag/scan_flags.go:48-61]().

### Vulnerability Options
The `VulnerabilityFlagGroup` [pkg/flag/vulnerability_flags.go:51-57]() manages flags like:
- `--ignore-unfixed`: Displays only fixed vulnerabilities [pkg/flag/vulnerability_flags.go:15-20]().
- `--ignore-status`: Ignores vulnerabilities based on their status (e.g., `will_not_fix`) [pkg/flag/vulnerability_flags.go:21-27]().
- `--vex`: Specifies VEX (Vulnerability Exploitability eXchange) sources [pkg/flag/vulnerability_flags.go:28-32]().

Sources: [pkg/flag/scan_flags.go:35-71](), [pkg/flag/vulnerability_flags.go:15-32]()

## Reporting and Output Options

The `ReportFlagGroup` [pkg/flag/report_flags.go:133-149]() defines how results are presented.

| Flag | Purpose | Default |
|------|---------|---------|
| `--format` | Output format (table, json, sarif, cyclonedx, spdx) | `table` |
| `--severity` | Filter by severity (UNKNOWN, LOW, MEDIUM, HIGH, CRITICAL) | All |
| `--output` | Write results to a file | Stdout |
| `--exit-code` | Exit with a non-zero code if issues are found | 0 |
| `--template` | Use a Go template for custom formatting | None |

**Template Validation:**
If `--template` is used, the file must have a `.tpl` extension [pkg/flag/report_flags.go:227-229]().

Sources: [pkg/flag/report_flags.go:29-129](), [pkg/flag/report_flags.go:220-233]()

---

# Page: Misconfiguration Scanning Configuration

# Misconfiguration Scanning Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [pkg/dependency/parser/gradle/lockfile/parse.go](pkg/dependency/parser/gradle/lockfile/parse.go)
- [pkg/dependency/parser/gradle/lockfile/parse_test.go](pkg/dependency/parser/gradle/lockfile/parse_test.go)
- [pkg/dependency/parser/gradle/lockfile/testdata/happy.lockfile](pkg/dependency/parser/gradle/lockfile/testdata/happy.lockfile)
- [pkg/dependency/parser/ruby/gemspec/parse.go](pkg/dependency/parser/ruby/gemspec/parse.go)
- [pkg/fanal/analyzer/language/java/gradle/lockfile.go](pkg/fanal/analyzer/language/java/gradle/lockfile.go)
- [pkg/fanal/analyzer/language/java/gradle/lockfile_test.go](pkg/fanal/analyzer/language/java/gradle/lockfile_test.go)
- [pkg/fanal/analyzer/language/java/gradle/pom.go](pkg/fanal/analyzer/language/java/gradle/pom.go)
- [pkg/fanal/analyzer/language/java/gradle/pom_test.go](pkg/fanal/analyzer/language/java/gradle/pom_test.go)
- [pkg/fanal/analyzer/language/java/gradle/testdata/cache/caches/modules-2/files-2.1/junit/junit/4.13/5c17760663fae422643fc859fd352c68a1d91bfc/junit-4.13.pom](pkg/fanal/analyzer/language/java/gradle/testdata/cache/caches/modules-2/files-2.1/junit/junit/4.13/5c17760663fae422643fc859fd352c68a1d91bfc/junit-4.13.pom)
- [pkg/fanal/analyzer/language/java/gradle/testdata/cache/caches/modules-2/files-2.1/org.hamcrest/hamcrest-core/1.3/872e413497b906e7c9fa85ccc96046c5d1ef7ece/hamcrest-core-1.3.pom](pkg/fanal/analyzer/language/java/gradle/testdata/cache/caches/modules-2/files-2.1/org.hamcrest/hamcrest-core/1.3/872e413497b906e7c9fa85ccc96046c5d1ef7ece/hamcrest-core-1.3.pom)
- [pkg/flag/misconf_flags.go](pkg/flag/misconf_flags.go)
- [pkg/flag/options_test.go](pkg/flag/options_test.go)
- [pkg/flag/report_flags.go](pkg/flag/report_flags.go)
- [pkg/flag/report_flags_test.go](pkg/flag/report_flags_test.go)
- [pkg/flag/scan_flags.go](pkg/flag/scan_flags.go)
- [pkg/flag/scan_flags_test.go](pkg/flag/scan_flags_test.go)
- [pkg/flag/vulnerability_flags.go](pkg/flag/vulnerability_flags.go)
- [pkg/iac/scanners/cloudformation/parser/fn_split.go](pkg/iac/scanners/cloudformation/parser/fn_split.go)
- [pkg/x/strings/strings.go](pkg/x/strings/strings.go)

</details>



This document provides a comprehensive reference for Trivy's misconfiguration scanning configuration flags. These flags control how Trivy scans Infrastructure as Code (IaC) files, Kubernetes manifests, and other configuration formats for security issues and misconfigurations.

For information about how misconfiguration scanning is implemented and executed, see [Misconfiguration Scanning](#4.2). For general command structure and global flags, see [Command Structure and Global Flags](#2.1). For specific scan commands that use these flags, see [Scan Commands and Target Options](#2.2).

## Flag Organization and Structure

All misconfiguration-related flags are defined in `MisconfFlagGroup`, which provides a cohesive set of configuration options for IaC scanning. The flag group follows Trivy's standard flag pattern, where each flag is defined with a name, config file key, default value, and usage description.

### Code Entity Mapping: MisconfFlagGroup
The following diagram maps the Natural Language configuration categories to the specific `Flag` entities defined in the `pkg/flag` package.

```mermaid
graph TB
    MisconfFlagGroup["MisconfFlagGroup (pkg/flag/misconf_flags.go)"]
    
    subgraph "Core Scan Options"
        IncludeNonFailures["IncludeNonFailuresFlag<br/>--include-non-failures"]
        ChecksBundle["ChecksBundleRepositoryFlag<br/>--checks-bundle-repository"]
        MisconfigScanners["MisconfigScannersFlag<br/>--misconfig-scanners"]
    end
    
    subgraph "Helm Configuration"
        HelmValues["HelmValuesFileFlag<br/>--helm-values"]
        HelmSet["HelmSetFlag<br/>--helm-set"]
        HelmSetFile["HelmSetFileFlag<br/>--helm-set-file"]
        HelmSetString["HelmSetStringFlag<br/>--helm-set-string"]
        HelmAPIVersions["HelmAPIVersionsFlag<br/>--helm-api-versions"]
        HelmKubeVersion["HelmKubeVersionFlag<br/>--helm-kube-version"]
    end
    
    subgraph "Terraform & CloudFormation"
        TfVars["TfVarsFlag<br/>--tf-vars"]
        TfExcludeDownloaded["TerraformExcludeDownloaded<br/>--tf-exclude-downloaded-modules"]
        CfParams["CfParamsFlag<br/>--cf-params"]
    end
    
    subgraph "Ansible Configuration"
        AnsiblePlaybooks["AnsiblePlaybooks<br/>--ansible-playbook"]
        AnsibleInventories["AnsibleInventories<br/>--ansible-inventory"]
        AnsibleExtraVars["AnsibleExtraVars<br/>--ansible-extra-vars"]
    end
    
    MisconfFlagGroup --> IncludeNonFailures
    MisconfFlagGroup --> ChecksBundle
    MisconfFlagGroup --> MisconfigScanners
    MisconfFlagGroup --> HelmValues
    MisconfFlagGroup --> HelmSet
    MisconfFlagGroup --> HelmSetFile
    MisconfFlagGroup --> HelmSetString
    MisconfFlagGroup --> HelmAPIVersions
    MisconfFlagGroup --> HelmKubeVersion
    MisconfFlagGroup --> TfVars
    MisconfFlagGroup --> TfExcludeDownloaded
    MisconfFlagGroup --> CfParams
    MisconfFlagGroup --> AnsiblePlaybooks
    MisconfFlagGroup --> AnsibleInventories
    MisconfFlagGroup --> AnsibleExtraVars
```

**Sources:** [pkg/flag/misconf_flags.go:147-170](), [pkg/flag/misconf_flags.go:21-143]()

The `MisconfFlagGroup` structure is instantiated via `NewMisconfFlagGroup()` and converted to `MisconfOptions` through the `ToOptions()` method [pkg/flag/misconf_flags.go:251-274](). This conversion transforms string slice flags into strongly-typed enums where appropriate, such as `analyzer.Type` for scanner selection or `types.ConfigType` for rendering options.

## Core Misconfiguration Flags

### Include Non-Failures Flag

**Flag:** `--include-non-failures`  
**Config Key:** `misconfiguration.include-non-failures`  
**Type:** Boolean  
**Default:** `false`

Controls whether to include successful checks in the output. When enabled, Trivy reports not only failed checks but also checks that passed. This is useful for compliance reporting and understanding the full security posture.

**Sources:** [pkg/flag/misconf_flags.go:35-40]()

### Checks Bundle Repository Flag

**Flag:** `--checks-bundle-repository`  
**Config Key:** `misconfiguration.checks-bundle-repository`  
**Type:** String  
**Default:** `ghcr.io/aquasecurity/trivy-checks:<version>`

Specifies the OCI registry URL from which to retrieve the checks bundle containing Rego policies. The default is constructed using `policy.BundleRepository` and `policy.BundleVersion` [pkg/flag/misconf_flags.go:88-100]().

**Aliases:** `--policy-bundle-repository` (deprecated)

### Misconfiguration Scanners Flag

**Flag:** `--misconfig-scanners`  
**Config Key:** `misconfiguration.scanners`  
**Type:** String slice  
**Default:** All config file types except YAML and JSON [pkg/flag/misconf_flags.go:101-109]().

Controls which configuration file types are scanned. Trivy uses the `analyzer.TypeConfigFiles` list but excludes generic formats by default using `lo.Without(analyzer.TypeConfigFiles, analyzer.TypeYAML, analyzer.TypeJSON)` [pkg/flag/misconf_flags.go:104-106]().

## Helm Configuration Flags

Helm charts require specific context to be rendered correctly before scanning. Trivy implements flags that mirror the standard `helm template` command behavior.

### Helm Flag Implementation Data Flow
The following diagram illustrates how Helm-specific flags are processed into the scanning engine.

```mermaid
graph LR
    subgraph "Input Flags (pkg/flag/misconf_flags.go)"
        ValuesFile["HelmValuesFileFlag<br/>--helm-values"]
        SetValues["HelmSetFlag<br/>--helm-set"]
        SetFile["HelmSetFileFlag<br/>--helm-set-file"]
        SetString["HelmSetStringFlag<br/>--helm-set-string"]
    end
    
    subgraph "Environment Context"
        APIVersions["HelmAPIVersionsFlag<br/>--helm-api-versions"]
        KubeVersion["HelmKubeVersionFlag<br/>--helm-kube-version"]
    end
    
    Options["MisconfOptions (pkg/flag/misconf_flags.go)"]
    
    ValuesFile --> Options
    SetValues --> Options
    SetFile --> Options
    SetString --> Options
    APIVersions --> Options
    KubeVersion --> Options
    
    Options --> Scanner["Misconfig Scanner Engine"]
```

**Sources:** [pkg/flag/misconf_flags.go:41-70](), [pkg/flag/misconf_flags.go:172-195]()

*   **`--helm-values`**: Paths to override the default `values.yaml` [pkg/flag/misconf_flags.go:41-45]().
*   **`--helm-set`**: Individual values specified as `key1=val1,key2=val2` [pkg/flag/misconf_flags.go:46-50]().
*   **`--helm-set-file`**: Values where the value is the content of a file, specified as `key1=path1` [pkg/flag/misconf_flags.go:51-55]().
*   **`--helm-set-string`**: Forces values to be treated as strings [pkg/flag/misconf_flags.go:56-60]().
*   **`--helm-api-versions`**: Simulates `Capabilities.APIVersions` for conditional template rendering [pkg/flag/misconf_flags.go:61-65]().
*   **`--helm-kube-version`**: Simulates `Capabilities.KubeVersion` [pkg/flag/misconf_flags.go:66-70]().

## Terraform and CloudFormation Flags

### Terraform Variables and Modules
*   **`--tf-vars`**: Paths to override Terraform `.tfvars` files [pkg/flag/misconf_flags.go:71-75]().
*   **`--tf-exclude-downloaded-modules`**: Excludes misconfigurations for modules downloaded into the `.terraform` directory [pkg/flag/misconf_flags.go:82-87]().

### CloudFormation Parameters
*   **`--cf-params`**: Paths to CloudFormation parameter files [pkg/flag/misconf_flags.go:76-81]().

## Ansible Configuration Flags

Trivy supports scanning Ansible playbooks and inventories.

*   **`--ansible-playbook`**: Paths to playbook files [pkg/flag/misconf_flags.go:129-133]().
*   **`--ansible-inventory`**: Host paths or comma-separated host lists [pkg/flag/misconf_flags.go:134-138]().
*   **`--ansible-extra-vars`**: Additional variables specified as `key=value` or `@file` [pkg/flag/misconf_flags.go:139-143]().

## Advanced Scanning Options

### Configuration File Schemas
**Flag:** `--config-file-schemas`  
**Config Key:** `misconfiguration.config-file-schemas`

Specifies paths to JSON configuration file schemas. These schemas allow Trivy to determine if a file matches a specific configuration type and provide type-checking information to Rego checks [pkg/flag/misconf_flags.go:110-114]().

### Render Cause and Raw Scanners
*   **`--render-cause`**: Displays the rendered cause (e.g., evaluated variables) in the table report for specific types like `Terraform` or `Ansible` [pkg/flag/misconf_flags.go:115-121]().
*   **`--raw-config-scanners`**: Scanners that will also process raw (non-adapted) configurations into a shared state, currently supporting `Terraform` [pkg/flag/misconf_flags.go:122-128]().

## Flag-to-Options Conversion Logic

The `ToOptions` method in `pkg/flag/misconf_flags.go` performs the critical task of mapping CLI/Viper inputs into the `MisconfOptions` struct used by the scanner.

| Code Entity | Target Option | Logic |
| :--- | :--- | :--- |
| `MisconfigScannersFlag` | `MisconfigScanners` | Maps string names to `analyzer.Type` [pkg/flag/misconf_flags.go:254-256]() |
| `RenderCauseFlag` | `RenderCause` | Maps strings to `types.ConfigType` [pkg/flag/misconf_flags.go:261-263]() |
| `RawConfigScanners` | `RawConfigScanners` | Maps strings to `types.ConfigType` [pkg/flag/misconf_flags.go:264-266]() |

**Sources:** [pkg/flag/misconf_flags.go:251-274]()

---

# Page: Configuration Files and Environment Variables

# Configuration Files and Environment Variables

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [go.mod](go.mod)
- [go.sum](go.sum)
- [mkdocs.yml](mkdocs.yml)
- [pkg/commands/app.go](pkg/commands/app.go)
- [pkg/commands/app_test.go](pkg/commands/app_test.go)
- [pkg/commands/artifact/run.go](pkg/commands/artifact/run.go)
- [pkg/commands/testdata/java-db/metadata.json](pkg/commands/testdata/java-db/metadata.json)
- [pkg/commands/testdata/policy/metadata.json](pkg/commands/testdata/policy/metadata.json)
- [pkg/dependency/parser/gradle/lockfile/parse.go](pkg/dependency/parser/gradle/lockfile/parse.go)
- [pkg/dependency/parser/gradle/lockfile/parse_test.go](pkg/dependency/parser/gradle/lockfile/parse_test.go)
- [pkg/dependency/parser/gradle/lockfile/testdata/happy.lockfile](pkg/dependency/parser/gradle/lockfile/testdata/happy.lockfile)
- [pkg/dependency/parser/ruby/gemspec/parse.go](pkg/dependency/parser/ruby/gemspec/parse.go)
- [pkg/fanal/analyzer/language/java/gradle/lockfile.go](pkg/fanal/analyzer/language/java/gradle/lockfile.go)
- [pkg/fanal/analyzer/language/java/gradle/lockfile_test.go](pkg/fanal/analyzer/language/java/gradle/lockfile_test.go)
- [pkg/fanal/analyzer/language/java/gradle/pom.go](pkg/fanal/analyzer/language/java/gradle/pom.go)
- [pkg/fanal/analyzer/language/java/gradle/pom_test.go](pkg/fanal/analyzer/language/java/gradle/pom_test.go)
- [pkg/fanal/analyzer/language/java/gradle/testdata/cache/caches/modules-2/files-2.1/junit/junit/4.13/5c17760663fae422643fc859fd352c68a1d91bfc/junit-4.13.pom](pkg/fanal/analyzer/language/java/gradle/testdata/cache/caches/modules-2/files-2.1/junit/junit/4.13/5c17760663fae422643fc859fd352c68a1d91bfc/junit-4.13.pom)
- [pkg/fanal/analyzer/language/java/gradle/testdata/cache/caches/modules-2/files-2.1/org.hamcrest/hamcrest-core/1.3/872e413497b906e7c9fa85ccc96046c5d1ef7ece/hamcrest-core-1.3.pom](pkg/fanal/analyzer/language/java/gradle/testdata/cache/caches/modules-2/files-2.1/org.hamcrest/hamcrest-core/1.3/872e413497b906e7c9fa85ccc96046c5d1ef7ece/hamcrest-core-1.3.pom)
- [pkg/flag/options.go](pkg/flag/options.go)
- [pkg/flag/options_test.go](pkg/flag/options_test.go)
- [pkg/flag/report_flags.go](pkg/flag/report_flags.go)
- [pkg/flag/report_flags_test.go](pkg/flag/report_flags_test.go)
- [pkg/flag/scan_flags.go](pkg/flag/scan_flags.go)
- [pkg/flag/scan_flags_test.go](pkg/flag/scan_flags_test.go)
- [pkg/flag/vulnerability_flags.go](pkg/flag/vulnerability_flags.go)
- [pkg/iac/scanners/cloudformation/parser/fn_split.go](pkg/iac/scanners/cloudformation/parser/fn_split.go)
- [pkg/x/strings/strings.go](pkg/x/strings/strings.go)

</details>



## Purpose and Scope

This document explains how to configure Trivy using YAML configuration files and environment variables as alternatives or supplements to command-line flags. Trivy uses the [Viper](https://github.com/spf13/viper) configuration library to provide a flexible, hierarchical configuration system that supports multiple configuration sources with a defined precedence order [go.mod:106]().

For information about available CLI flags and their usage, see **2.1 Command Structure and Global Flags** and **2.2 Scan Commands and Target Options**.

---

## Configuration Sources and Precedence

Trivy accepts configuration from three sources, evaluated in the following precedence order (highest to lowest):

1.  **Command-line flags** - Explicitly passed flags (e.g., `--severity CRITICAL`) [pkg/commands/app.go:191-193]()
2.  **Environment variables** - Variables with the `TRIVY_` prefix [pkg/flag/options.go:355-360]()
3.  **Configuration file** - YAML file specified via `--config` flag or default location [pkg/commands/app.go:149-164]()

When the same option is specified in multiple sources, the higher precedence source takes effect. This allows you to set baseline configurations in a file while overriding specific values via environment variables or flags.

### Configuration Loading Flow

```mermaid
flowchart TD
    Start["Command Execution"]
    LoadFlags["Bind CLI Flags<br/>(cobra.Command)"]
    GetConfigPath["Get Config File Path<br/>(flag.ConfigFileFlag)"]
    InitConfig["initConfig()<br/>[pkg/commands/app.go:149-164]"]
    CheckExists{"Config File<br/>Exists?"}
    ReadConfig["viper.ReadInConfig()<br/>(YAML format)"]
    BindEnv["Bind Environment Variables<br/>(Flag.BindEnv)"]
    ParseFlags["Parse All Flags<br/>(Flag.Parse)"]
    ToOptions["Convert to Options Struct<br/>(Flags.ToOptions)"]
    Execute["Execute Command"]
    
    Start --> LoadFlags
    LoadFlags --> GetConfigPath
    GetConfigPath --> InitConfig
    InitConfig --> CheckExists
    CheckExists -->|No| BindEnv
    CheckExists -->|Yes| ReadConfig
    ReadConfig --> BindEnv
    BindEnv --> ParseFlags
    ParseFlags --> ToOptions
    ToOptions --> Execute
```

**Sources:** [pkg/commands/app.go:149-164](), [pkg/commands/app.go:184-213](), [pkg/flag/options.go:329-353]()

---

## Configuration File Format

Trivy configuration files use YAML format [pkg/commands/app.go:152]() with a hierarchical structure that mirrors the CLI flag organization. The configuration file is typically named `trivy.yaml` and can be specified explicitly via the `--config` flag.

### File Location and Loading

The default configuration file is loaded from the current working directory if not specified. The loading process is implemented in `initConfig`:

```mermaid
flowchart LR
    SetFile["viper.SetConfigFile(configFile)"]
    SetType["viper.SetConfigType('yaml')"]
    ReadConfig["viper.ReadInConfig()"]
    CheckError{"Error?"}
    NotExist{"os.ErrNotExist?"}
    PathChanged{"Custom<br/>Path?"}
    LogDebug["Log: Using built-in values"]
    LogLoaded["Log: Loaded config"]
    Error["Return Error"]
    Success["Return nil"]
    
    SetFile --> SetType
    SetType --> ReadConfig
    ReadConfig --> CheckError
    CheckError -->|Yes| NotExist
    CheckError -->|No| LogLoaded
    NotExist -->|Yes| PathChanged
    NotExist -->|No| Error
    PathChanged -->|No| LogDebug
    PathChanged -->|Yes| Error
    LogDebug --> Success
    LogLoaded --> Success
```

**Sources:** [pkg/commands/app.go:149-164]()

### Hierarchical Structure

Configuration keys use dot notation to represent nested structures. For example, the `--scanners` flag maps to the `scan.scanners` configuration key [pkg/flag/scan_flags.go:35-37]().

| CLI Flag | Config Key | Description |
|----------|-----------|-------------|
| `--severity` | `severity` | Severities to include [pkg/flag/report_flags.go:102-104]() |
| `--skip-dirs` | `scan.skip-dirs` | Directories to skip [pkg/flag/scan_flags.go:18-20]() |
| `--scanners` | `scan.scanners` | Scanners to enable [pkg/flag/scan_flags.go:35-37]() |
| `--ignore-unfixed` | `vulnerability.ignore-unfixed` | Display only fixed vulnerabilities [pkg/flag/vulnerability_flags.go:15-17]() |
| `--format` | `format` | Output format [pkg/flag/report_flags.go:29-31]() |

### Example Configuration File

```yaml
# Scanning configuration
scan:
  severity:
    - CRITICAL
    - HIGH
  skip-dirs:
    - node_modules
    - vendor
  scanners:
    - vuln
    - secret

# Vulnerability specific
vulnerability:
  ignore-unfixed: true

# Report configuration
format: json
output: result.json
```

**Sources:** [pkg/flag/scan_flags.go:18-138](), [pkg/flag/report_flags.go:29-129](), [pkg/flag/vulnerability_flags.go:15-49]()

---

## Environment Variables

Trivy supports environment variables for all configuration options. The naming convention transforms CLI flag names to uppercase with underscores and adds a `TRIVY_` prefix.

### Naming Convention

The transformation follows these rules:

```mermaid
flowchart LR
    FlagName["CLI Flag Name<br/>(e.g., 'skip-dirs')"]
    Replace["Replace hyphens<br/>with underscores"]
    Upper["Convert to<br/>UPPERCASE"]
    Prefix["Add 'TRIVY_' prefix"]
    EnvVar["Environment Variable<br/>(e.g., 'TRIVY_SKIP_DIRS')"]
    
    FlagName --> Replace
    Replace --> Upper
    Upper --> Prefix
    Prefix --> EnvVar
```

**Implementation:**
The environment variable name is generated by joining the prefix and the flag name transformed to uppercase with underscores [pkg/flag/options.go:355-356]().

**Sources:** [pkg/flag/options.go:355-360]()

### List-Type Values

For flags that accept multiple values (string slices), environment variables use comma-separated values. The `cast` logic handles splitting these strings back into slices [pkg/flag/options.go:182-188]().

```bash
export TRIVY_SEVERITY=CRITICAL,HIGH
export TRIVY_SKIP_DIRS=node_modules,vendor
```

**Sources:** [pkg/flag/options.go:182-189]()

---

## Flag to Configuration Mapping System

Trivy uses a generic `Flag[T]` structure to define all configuration options. Each flag contains metadata about its CLI name, configuration key, and default value [pkg/flag/options.go:36-85]().

### Flag Structure

The `Flag[T]` struct defines how each option is represented across configuration sources:

```mermaid
classDiagram
    class Flag~T~ {
        +Name string
        +ConfigName string
        +Shorthand string
        +Default T
        +Values []string
        +Usage string
        +Persistent bool
        +Deprecated string
        +Removed string
        +Aliases []Alias
        +value T
        +Parse() error
        +Bind(cmd) error
        +BindEnv() error
    }
    
    class Alias {
        +Name string
        +ConfigName string
        +Deprecated bool
    }
    
    Flag~T~ --> Alias : contains
```

**Sources:** [pkg/flag/options.go:36-91]()

### Parse Process

When configuration is parsed, Trivy checks multiple sources in a specific order within the `Flag.parse()` method [pkg/flag/options.go:139-164]():

1.  **Check Aliases**: Looks for deprecated configuration keys in the config file [pkg/flag/options.go:143-152]().
2.  **Primary Key**: Retrieves the value using `viper.Get(f.ConfigName)` [pkg/flag/options.go:154]().
3.  **Manual Default**: For config-only flags (no CLI name), manually handles defaults [pkg/flag/options.go:159-161]().

**Sources:** [pkg/flag/options.go:139-164]()

---

## Deprecated and Removed Flags

Trivy maintains backward compatibility while evolving its configuration system by supporting deprecated aliases and marking removed flags.

### Handling Deprecated Options

When a deprecated flag is used, Trivy logs a warning [pkg/flag/options.go:127-129](). If a deprecated configuration key (alias) is used in the config file, a warning is also logged [pkg/flag/options.go:149]().

Example of a deprecated flag with an alias:
```go
ScannersFlag = Flag[[]string]{
    Name:       "scanners",
    ConfigName: "scan.scanners",
    Aliases: []Alias{
        {
            Name:       "security-checks",
            ConfigName: "scan.security-checks",
            Deprecated: true,
        },
    },
}
```
**Sources:** [pkg/flag/scan_flags.go:35-71](), [pkg/flag/options.go:127-129](), [pkg/flag/options.go:149]()

### Removed Flags

Removed flags generate an error and halt execution [pkg/flag/options.go:130-133]().

```go
if f.Removed != "" && f.isSet() {
    log.Errorf(`"--%s" was removed. %s`, f.Name, f.Removed)
    return xerrors.Errorf(`removed flag ("--%s")`, f.Name)
}
```
**Sources:** [pkg/flag/options.go:130-133]()

---

## Configuration Resolution Architecture

The complete binding process connects CLI flags, configuration files, and environment variables through Viper:

```mermaid
flowchart TD
    subgraph "Configuration Sources"
        CLI["CLI Flags<br/>(cobra.Command)"]
        Config["Config File<br/>(trivy.yaml)"]
        Env["Environment Variables<br/>(TRIVY_*)"]
    end
    
    subgraph "Viper Binding Layer"
        BindFlag["viper.BindPFlag()<br/>[pkg/flag/options.go:347-349]"]
        BindEnvVar["viper.BindEnv()<br/>[pkg/flag/options.go:358-360]"]
        ViperGet["viper.Get(configName)<br/>[pkg/flag/options.go:154]"]
    end
    
    subgraph "Flag Processing"
        FlagStruct["Flag[T] struct"]
        ParseMethod["Flag.Parse()<br/>[pkg/flag/options.go:101-137]"]
        CastMethod["Flag.cast()<br/>[pkg/flag/options.go:167-192]"]
    end
    
    subgraph "Output"
        Options["Options struct"]
    end
    
    CLI --> BindFlag
    Env --> BindEnvVar
    Config --> ViperGet
    
    BindFlag --> FlagStruct
    BindEnvVar --> FlagStruct
    ViperGet --> FlagStruct
    
    FlagStruct --> ParseMethod
    ParseMethod --> CastMethod
    CastMethod --> Options
```

**Sources:** [pkg/flag/options.go:101-218](), [pkg/flag/options.go:329-375]()

---

# Page: Artifact Analysis System

# Artifact Analysis System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [pkg/fanal/analyzer/analyzer.go](pkg/fanal/analyzer/analyzer.go)
- [pkg/fanal/analyzer/analyzer_test.go](pkg/fanal/analyzer/analyzer_test.go)
- [pkg/fanal/analyzer/pkg/apk/apk.go](pkg/fanal/analyzer/pkg/apk/apk.go)
- [pkg/fanal/analyzer/pkg/apk/apk_test.go](pkg/fanal/analyzer/pkg/apk/apk_test.go)
- [pkg/fanal/analyzer/pkg/apk/testdata/apk](pkg/fanal/analyzer/pkg/apk/testdata/apk)
- [pkg/fanal/applier/applier.go](pkg/fanal/applier/applier.go)
- [pkg/fanal/applier/applier_test.go](pkg/fanal/applier/applier_test.go)
- [pkg/fanal/artifact/artifact.go](pkg/fanal/artifact/artifact.go)
- [pkg/fanal/artifact/image/image.go](pkg/fanal/artifact/image/image.go)
- [pkg/fanal/artifact/image/image_test.go](pkg/fanal/artifact/image/image_test.go)
- [pkg/fanal/artifact/local/fs.go](pkg/fanal/artifact/local/fs.go)
- [pkg/fanal/artifact/local/fs_test.go](pkg/fanal/artifact/local/fs_test.go)
- [pkg/fanal/artifact/sbom/sbom_test.go](pkg/fanal/artifact/sbom/sbom_test.go)
- [pkg/fanal/artifact/vm/vm_test.go](pkg/fanal/artifact/vm/vm_test.go)
- [pkg/fanal/test/integration/testdata/goldens/packages/alpine-310.json.golden](pkg/fanal/test/integration/testdata/goldens/packages/alpine-310.json.golden)
- [pkg/fanal/test/integration/testdata/goldens/packages/vulnimage.json.golden](pkg/fanal/test/integration/testdata/goldens/packages/vulnimage.json.golden)
- [pkg/fanal/test/integration/testdata/goldens/vuln-image1.2.3.expectedlibs.golden](pkg/fanal/test/integration/testdata/goldens/vuln-image1.2.3.expectedlibs.golden)
- [pkg/fanal/types/artifact.go](pkg/fanal/types/artifact.go)
- [pkg/fanal/walker/fs.go](pkg/fanal/walker/fs.go)
- [pkg/fanal/walker/fs_test.go](pkg/fanal/walker/fs_test.go)
- [pkg/fanal/walker/tar.go](pkg/fanal/walker/tar.go)
- [pkg/fanal/walker/tar_test.go](pkg/fanal/walker/tar_test.go)
- [pkg/fanal/walker/vm.go](pkg/fanal/walker/vm.go)
- [pkg/fanal/walker/walk.go](pkg/fanal/walker/walk.go)
- [pkg/fanal/walker/walk_test.go](pkg/fanal/walker/walk_test.go)

</details>



## Purpose and Scope

The Artifact Analysis System is the core engine responsible for decomposing various artifact types—including container images, local filesystems, virtual machine images, and Git repositories—into a structured inventory of components. It extracts operating system information, installed packages, application dependencies, and configuration metadata. This system provides the foundational data used by the vulnerability, misconfiguration, and secret scanning engines.

For details on specific subsystems, see the following child pages:
- [Layer Processing and Package Extraction](#3.1) — Detailed mechanics of container layer merging and package provenance.
- [Package URL (PURL) System](#3.2) — Standardized identification of components across ecosystems.
- [Analyzer Types and Language Support](#3.3) — Technical details on individual language and OS scanners.

## High-Level Architecture

The analysis process is orchestrated by the `Artifact` interface [pkg/fanal/artifact/artifact.go:84-87](). Depending on the scan target, Trivy instantiates a specific implementation:
- **Container Images**: `image.Artifact` [pkg/fanal/artifact/image/image.go:39-51]()
- **Filesystems/Repositories**: `local.Artifact` [pkg/fanal/artifact/local/fs.go:42-54]()
- **Virtual Machines**: `vm.Artifact` (supporting EBS snapshots and raw disk images) [pkg/fanal/artifact/vm/vm_test.go:19-20]()

### Analysis Workflow

The system follows a standardized execution flow to transform raw bytes into a `Reference` [pkg/fanal/artifact/artifact.go:90-100]():

```mermaid
graph TD
    subgraph Initialization["1. Initialization"]
        NewArt["NewArtifact()"]
        InitAnlz["Initialize AnalyzerGroup"]
        InitHndl["Initialize HandlerManager"]
    end

    subgraph Discovery["2. Discovery & Walking"]
        Walker["walker.Walk()"]
        StaticPaths["StaticPathAnalyzer.StaticPaths()"]
    end

    subgraph Extraction["3. Component Extraction"]
        Analyze["analyzer.Analyze()"]
        PostAnalyze["analyzer.PostAnalyze()"]
        Handle["handler.Handle()"]
    end

    subgraph Consolidation["4. Consolidation"]
        Cache["cache.PutBlob()"]
        Applier["applier.ApplyLayers()"]
        Ref["Generate artifact.Reference"]
    end

    NewArt --> InitAnlz
    InitAnlz --> Walker
    Walker --> Analyze
    Analyze --> Handle
    Handle --> Cache
    Cache --> Applier
    Applier --> Ref
```
Sources: [pkg/fanal/artifact/image/image.go:53-87](), [pkg/fanal/artifact/local/fs.go:56-98](), [pkg/fanal/artifact/artifact.go:84-100]()

## Analyzer Subsystem

The `analyzer` package is the heart of the extraction logic. It defines how specific files (like `Gemfile.lock` or `/lib/apk/db/installed`) are parsed.

### Analyzer Interface
Every analyzer must implement the `analyzer` interface [pkg/fanal/analyzer/analyzer.go:75-80](), which defines:
- `Type()`: A unique identifier (e.g., `TypeApk`, `TypePip`) [pkg/fanal/analyzer/const.go:156-274]().
- `Required()`: Logic to determine if a file should be processed by this analyzer based on its path or metadata.
- `Analyze()`: The actual parsing logic that returns an `AnalysisResult`.

### Analyzer Grouping and Dispatch
Trivy uses an `AnalyzerGroup` [pkg/fanal/analyzer/analyzer.go:133-139]() to manage multiple analyzers. To optimize performance, it supports:
- **Parallelism**: Running multiple analyzers concurrently [pkg/fanal/analyzer/analyzer.go:47]().
- **Static Paths**: If an analyzer only looks for specific files (e.g., `/etc/os-release`), Trivy can skip full directory traversal [pkg/fanal/analyzer/analyzer.go:126-129]().

### Analysis Result Structure
The output of the analyzer subsystem is an `AnalysisResult` [pkg/fanal/analyzer/analyzer.go:176-197](), which aggregates:
- **OS**: Detected operating system family and version [pkg/fanal/types/artifact.go:23-30]().
- **PackageInfos**: OS-level packages (apk, dpkg, rpm) [pkg/fanal/types/artifact.go:106-109]().
- **Applications**: Language-specific dependencies (npm, pypi, cargo, etc.) [pkg/fanal/types/artifact.go:111-121]().

Sources: [pkg/fanal/analyzer/analyzer.go:75-139](), [pkg/fanal/analyzer/const.go:156-274](), [pkg/fanal/types/artifact.go:106-121]()

## Artifact Processing Models

Trivy adapts its analysis strategy based on the nature of the artifact:

### Container Images
For images, the `image.Artifact` handles layer-aware analysis. It identifies "diff IDs" for each layer [pkg/fanal/artifact/image/image.go:101](), checks the cache for existing results [pkg/fanal/artifact/image/image.go:135](), and uses the `applier` to merge results from multiple layers into a final view [pkg/fanal/applier/applier_test.go:21-32]().
For details, see [Layer Processing and Package Extraction](#3.1).

### Filesystems and Repositories
The `local.Artifact` processes local directories. If a `.git` directory is found, it extracts `RepoMetadata` (commit hash, branch, tags) [pkg/fanal/artifact/local/fs.go:103-167](). This metadata is used to generate stable cache keys for repositories [pkg/fanal/artifact/local/fs.go:87-92]().

### Virtual Machine Images
The `vm.Artifact` supports scanning disk images and cloud snapshots (EBS). It utilizes specialized walkers to navigate partition tables and filesystems within the disk image [pkg/fanal/artifact/vm/vm_test.go:38-60]().

| Artifact Type | Code Entity | Identification Mechanism |
| :--- | :--- | :--- |
| **Container Image** | `types.TypeContainerImage` | Image ID & Layer Diff IDs |
| **Filesystem** | `types.TypeFilesystem` | File path & directory hash |
| **Repository** | `types.TypeRepository` | Git Commit Hash |
| **VM Image** | `types.TypeVM` | EBS Snapshot ID or File Digest |

Sources: [pkg/fanal/artifact/image/image.go:89-169](), [pkg/fanal/artifact/local/fs.go:103-167](), [pkg/fanal/types/artifact.go:13-21](), [pkg/fanal/artifact/vm/vm_test.go:102-152]()

## Identification and Metadata

Standardization is key to interoperability with vulnerability databases and SBOM formats.

- **PURLs**: Every extracted package is assigned a Package URL (PURL) for cross-ecosystem identification. For details, see [Package URL (PURL) System](#3.2).
- **UIDs**: Trivy generates unique identifiers for packages to track them across layers and different scan targets [pkg/fanal/applier/applier_test.go:147-161]().
- **Licenses**: Analyzers also extract license information from package metadata (e.g., APK `installed` file or `package.json`) [pkg/fanal/artifact/local/fs_test.go:68]().

Sources: [pkg/fanal/applier/applier_test.go:141-214](), [pkg/fanal/artifact/local/fs_test.go:44-92]()

---

# Page: Layer Processing and Package Extraction

# Layer Processing and Package Extraction

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [integration/testdata/conda-cyclonedx.json.golden](integration/testdata/conda-cyclonedx.json.golden)
- [integration/testdata/conda-environment-cyclonedx.json.golden](integration/testdata/conda-environment-cyclonedx.json.golden)
- [integration/testdata/fixtures/sbom/fluentd-multiple-lockfiles-cyclonedx.json](integration/testdata/fixtures/sbom/fluentd-multiple-lockfiles-cyclonedx.json)
- [integration/testdata/fluentd-multiple-lockfiles-short.cdx.json.golden](integration/testdata/fluentd-multiple-lockfiles-short.cdx.json.golden)
- [integration/testdata/fluentd-multiple-lockfiles.cdx.json.golden](integration/testdata/fluentd-multiple-lockfiles.cdx.json.golden)
- [integration/testdata/npm-cyclonedx.json.golden](integration/testdata/npm-cyclonedx.json.golden)
- [integration/testdata/pom-cyclonedx.json.golden](integration/testdata/pom-cyclonedx.json.golden)
- [pkg/fanal/analyzer/analyzer.go](pkg/fanal/analyzer/analyzer.go)
- [pkg/fanal/analyzer/analyzer_test.go](pkg/fanal/analyzer/analyzer_test.go)
- [pkg/fanal/analyzer/pkg/apk/apk.go](pkg/fanal/analyzer/pkg/apk/apk.go)
- [pkg/fanal/analyzer/pkg/apk/apk_test.go](pkg/fanal/analyzer/pkg/apk/apk_test.go)
- [pkg/fanal/analyzer/pkg/apk/testdata/apk](pkg/fanal/analyzer/pkg/apk/testdata/apk)
- [pkg/fanal/analyzer/pkg/dpkg/dpkg.go](pkg/fanal/analyzer/pkg/dpkg/dpkg.go)
- [pkg/fanal/analyzer/pkg/dpkg/dpkg_test.go](pkg/fanal/analyzer/pkg/dpkg/dpkg_test.go)
- [pkg/fanal/analyzer/pkg/dpkg/testdata/corrupsed.txtar](pkg/fanal/analyzer/pkg/dpkg/testdata/corrupsed.txtar)
- [pkg/fanal/analyzer/pkg/dpkg/testdata/digest.txtar](pkg/fanal/analyzer/pkg/dpkg/testdata/digest.txtar)
- [pkg/fanal/analyzer/pkg/dpkg/testdata/md5sums.txtar](pkg/fanal/analyzer/pkg/dpkg/testdata/md5sums.txtar)
- [pkg/fanal/analyzer/pkg/dpkg/testdata/only-apt.txtar](pkg/fanal/analyzer/pkg/dpkg/testdata/only-apt.txtar)
- [pkg/fanal/analyzer/pkg/dpkg/testdata/third-party.txtar](pkg/fanal/analyzer/pkg/dpkg/testdata/third-party.txtar)
- [pkg/fanal/analyzer/pkg/dpkg/testdata/valid.txtar](pkg/fanal/analyzer/pkg/dpkg/testdata/valid.txtar)
- [pkg/fanal/analyzer/pkg/rpm/rpm.go](pkg/fanal/analyzer/pkg/rpm/rpm.go)
- [pkg/fanal/analyzer/pkg/rpm/rpm_test.go](pkg/fanal/analyzer/pkg/rpm/rpm_test.go)
- [pkg/fanal/applier/applier.go](pkg/fanal/applier/applier.go)
- [pkg/fanal/applier/applier_test.go](pkg/fanal/applier/applier_test.go)
- [pkg/fanal/applier/docker.go](pkg/fanal/applier/docker.go)
- [pkg/fanal/applier/docker_test.go](pkg/fanal/applier/docker_test.go)
- [pkg/fanal/artifact/artifact.go](pkg/fanal/artifact/artifact.go)
- [pkg/fanal/artifact/image/image.go](pkg/fanal/artifact/image/image.go)
- [pkg/fanal/artifact/image/image_test.go](pkg/fanal/artifact/image/image_test.go)
- [pkg/fanal/artifact/local/fs.go](pkg/fanal/artifact/local/fs.go)
- [pkg/fanal/artifact/local/fs_test.go](pkg/fanal/artifact/local/fs_test.go)
- [pkg/fanal/artifact/sbom/sbom.go](pkg/fanal/artifact/sbom/sbom.go)
- [pkg/fanal/artifact/sbom/sbom_test.go](pkg/fanal/artifact/sbom/sbom_test.go)
- [pkg/fanal/artifact/vm/vm_test.go](pkg/fanal/artifact/vm/vm_test.go)
- [pkg/fanal/test/integration/testdata/goldens/packages/alpine-310.json.golden](pkg/fanal/test/integration/testdata/goldens/packages/alpine-310.json.golden)
- [pkg/fanal/test/integration/testdata/goldens/packages/vulnimage.json.golden](pkg/fanal/test/integration/testdata/goldens/packages/vulnimage.json.golden)
- [pkg/fanal/test/integration/testdata/goldens/vuln-image1.2.3.expectedlibs.golden](pkg/fanal/test/integration/testdata/goldens/vuln-image1.2.3.expectedlibs.golden)
- [pkg/fanal/types/artifact.go](pkg/fanal/types/artifact.go)
- [pkg/fanal/walker/fs.go](pkg/fanal/walker/fs.go)
- [pkg/fanal/walker/fs_test.go](pkg/fanal/walker/fs_test.go)
- [pkg/fanal/walker/tar.go](pkg/fanal/walker/tar.go)
- [pkg/fanal/walker/tar_test.go](pkg/fanal/walker/tar_test.go)
- [pkg/fanal/walker/vm.go](pkg/fanal/walker/vm.go)
- [pkg/fanal/walker/walk.go](pkg/fanal/walker/walk.go)
- [pkg/fanal/walker/walk_test.go](pkg/fanal/walker/walk_test.go)
- [pkg/sbom/cyclonedx/marshal.go](pkg/sbom/cyclonedx/marshal.go)
- [pkg/sbom/cyclonedx/marshal_test.go](pkg/sbom/cyclonedx/marshal_test.go)
- [pkg/sbom/cyclonedx/testdata/happy/bom.json](pkg/sbom/cyclonedx/testdata/happy/bom.json)
- [pkg/sbom/cyclonedx/testdata/happy/infinite-loop-bom.json](pkg/sbom/cyclonedx/testdata/happy/infinite-loop-bom.json)
- [pkg/sbom/cyclonedx/testdata/happy/third-party-bom-no-os.json](pkg/sbom/cyclonedx/testdata/happy/third-party-bom-no-os.json)
- [pkg/sbom/cyclonedx/testdata/happy/third-party-bom.json](pkg/sbom/cyclonedx/testdata/happy/third-party-bom.json)
- [pkg/sbom/cyclonedx/unmarshal.go](pkg/sbom/cyclonedx/unmarshal.go)
- [pkg/sbom/cyclonedx/unmarshal_test.go](pkg/sbom/cyclonedx/unmarshal_test.go)
- [pkg/sbom/sbom.go](pkg/sbom/sbom.go)
- [pkg/sbom/sbom_test.go](pkg/sbom/sbom_test.go)
- [pkg/x/slices/slices.go](pkg/x/slices/slices.go)

</details>



This document details how Trivy processes container image layers, extracts package information, and tracks layer provenance. This system is a core part of the Artifact Analysis pipeline, ensuring that every detected vulnerability or package can be traced back to the specific layer that introduced it.

## Layer Analysis Pipeline

Trivy processes container images by decomposing them into individual layers. Each layer is treated as a discrete "blob" of data that is analyzed independently and cached.

### Container Image Processing Flow

The `image.Artifact` type in `pkg/fanal/artifact/image/image.go` coordinates the inspection of container images. It retrieves the image configuration, identifies layers (diff IDs), and executes a parallel analysis pipeline.

```mermaid
graph TB
    subgraph "Image Metadata Extraction"
        ImageRef["image.Artifact.Inspect()"]
        GetConfig["image.ConfigFile()"]
        GetDiffIDs["image.diffIDs()"]
    end
    
    subgraph "Optimization Logic"
        BaseLayerDet["image.guessBaseLayers()"]
        CacheLookup["cache.MissingBlobs()"]
    end
    
    subgraph "Layer Processing Pipeline"
        ParallelPipe["parallel.Pipeline"]
        Opener["image.uncompressedLayer()"]
        Walker["walker.LayerTar.Walk()"]
    end
    
    subgraph "Extraction & Analysis"
        Handler["handler.Manager.PostHandle()"]
        Analyzer["analyzer.AnalyzeFile()"]
        BlobInfo["types.BlobInfo"]
    end

    ImageRef --> GetConfig
    GetConfig --> GetDiffIDs
    GetDiffIDs --> BaseLayerDet
    BaseLayerDet --> CacheLookup
    CacheLookup --> ParallelPipe
    ParallelPipe --> Opener
    Opener --> Walker
    Walker --> Analyzer
    Analyzer --> Handler
    Handler --> BlobInfo
```

**Key Implementation Details:**
*   **Parallelism**: Trivy uses a parallel pipeline to process multiple layers simultaneously, governed by `artifact.Option.Parallel` [pkg/fanal/artifact/image/image.go:275-296]().
*   **Cache Efficiency**: Before processing, Trivy checks the `ArtifactCache` for existing `BlobInfo` using keys derived from DiffIDs. Only missing layers are extracted and analyzed [pkg/fanal/artifact/image/image.go:135-138]().
*   **Base Layer Detection**: Trivy attempts to identify which layers belong to the base image (e.g., `alpine`, `ubuntu`) to optimize scanning and provide better context [pkg/fanal/artifact/image/image.go:123-124]().

Sources: [pkg/fanal/artifact/image/image.go:89-169](), [pkg/fanal/artifact/image/image.go:275-296]()

## Package Extraction and Provenance

After layers are analyzed individually, the `Applier` merges the results to create a final view of the artifact. During this phase, Trivy performs "Layer Provenance Tracking" to associate packages with their originating layers.

### The Applier Mechanism

The `ApplyLayers` function in `pkg/fanal/applier/docker.go` iterates through all layers (from bottom to top) and calculates the final state of the filesystem, handling file whiteouts and opaque directories [pkg/fanal/applier/docker.go:98-170]().

**Entity Association Diagram**
```mermaid
graph LR
    subgraph "Code Entity Space"
        BlobInfo["types.BlobInfo"]
        Pkg["ftypes.Package"]
        AppDetail["ftypes.ArtifactDetail"]
        ApplyFn["applier.ApplyLayers()"]
        LookupFn["applier.lookupOriginLayerForPkg()"]
    end

    subgraph "Data Attributes"
        Digest["Layer Digest"]
        DiffID["Layer DiffID"]
        CreatedBy["History / CreatedBy"]
    end

    BlobInfo -- "contains" --> Pkg
    ApplyFn -- "processes" --> BlobInfo
    ApplyFn -- "calls" --> LookupFn
    LookupFn -- "finds" --> Digest
    LookupFn -- "finds" --> DiffID
    Pkg -- "updates" --> AppDetail
```

### Layer Provenance Logic

Trivy tracks where a package came from using the following logic:
1.  **OS Packages**: The `lookupOriginLayerForPkg` function searches through the `BlobInfo` of each layer. It identifies the first layer (bottom-up) where the package appears in the `PackageInfos` [pkg/fanal/applier/docker.go:46-55]().
2.  **Language Dependencies**: For libraries (e.g., npm, PyPI), `lookupOriginLayerForLib` matches the file path and package name across layers to find the origin [pkg/fanal/applier/docker.go:82-94]().
3.  **Metadata Enrichment**:
    *   **Installed Files**: For Debian/Ubuntu, Trivy tracks which layer contains the actual installed files for a package [pkg/fanal/applier/docker.go:226-227]().
    *   **Build Info**: For Red Hat images, Trivy propagates `BuildInfo` (content sets/CPEs) from parent layers to packages [pkg/fanal/applier/docker.go:58-80]().

Sources: [pkg/fanal/applier/docker.go:46-94](), [pkg/fanal/applier/docker.go:214-228]()

## SBOM Processing and Unmarshalling

Trivy can also "process" layers by consuming SBOMs (Software Bill of Materials). When an SBOM is provided as an artifact, Trivy unmarshals it into the same internal structures used during container scanning.

### CycloneDX Unmarshalling

Trivy supports unmarshalling CycloneDX JSON into its core BOM representation.

| Component Type | Trivy Internal Type | Source |
| :--- | :--- | :--- |
| `container` | `TypeContainerImage` | [pkg/sbom/cyclonedx/unmarshal.go:213-214]() |
| `application` | `TypeApplication` | [pkg/sbom/cyclonedx/unmarshal.go:215-216]() |
| `library` / `framework` | `TypeLibrary` | [pkg/sbom/cyclonedx/unmarshal.go:220-221]() |
| `operating-system` | `TypeOS` | [pkg/sbom/cyclonedx/unmarshal.go:222-223]() |

**Dependency Graph Reconstruction:**
Trivy reconstructs the dependency tree by parsing the `Dependencies` section of the CycloneDX BOM and mapping `BOMRef` identifiers to internal `Component` objects [pkg/sbom/cyclonedx/unmarshal.go:78-98]().

Sources: [pkg/sbom/cyclonedx/unmarshal.go:38-63](), [pkg/sbom/cyclonedx/unmarshal.go:172-208]()

## Data Structures

The primary data structures involved in layer processing are defined in `pkg/fanal/types/artifact.go`.

### BlobInfo
`BlobInfo` represents the result of analyzing a single layer. It is the unit of caching.
*   **OS**: Detected Operating System in this layer.
*   **PackageInfos**: OS packages found in this layer.
*   **Applications**: Language-specific files (lockfiles, binaries).
*   **OpaqueDirs/WhiteoutFiles**: Metadata for reconstructing the stacked filesystem.

### ArtifactDetail
`ArtifactDetail` represents the final, merged result after all layers have been applied.
*   **Packages**: Flattened list of all OS packages with layer provenance attached.
*   **Applications**: Consolidated list of all language-specific dependencies.

Sources: [pkg/fanal/types/artifact.go:168-196](), [pkg/fanal/types/artifact.go:208-225]()

---

# Page: Package URL (PURL) System

# Package URL (PURL) System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [pkg/detector/library/driver.go](pkg/detector/library/driver.go)
- [pkg/detector/library/driver_test.go](pkg/detector/library/driver_test.go)
- [pkg/detector/library/testdata/fixtures/data-source.yaml](pkg/detector/library/testdata/fixtures/data-source.yaml)
- [pkg/detector/library/testdata/fixtures/go.yaml](pkg/detector/library/testdata/fixtures/go.yaml)
- [pkg/fanal/analyzer/all/import.go](pkg/fanal/analyzer/all/import.go)
- [pkg/fanal/analyzer/const.go](pkg/fanal/analyzer/const.go)
- [pkg/fanal/types/const.go](pkg/fanal/types/const.go)
- [pkg/purl/purl.go](pkg/purl/purl.go)
- [pkg/purl/purl_test.go](pkg/purl/purl_test.go)

</details>



## Purpose and Scope

The Package URL (PURL) System provides standardized package identification across all supported ecosystems in Trivy. PURLs serve as a universal identifier format that allows consistent package representation regardless of whether the package comes from OS repositories, language-specific package managers, or container registries. This system is central to vulnerability matching, SBOM generation, VEX statement application, and policy enforcement.

This document covers PURL creation, conversion, matching, and ecosystem-specific handling.

## PURL Structure and Components

PURLs follow the specification defined by the Package URL project. Each PURL consists of standardized components that uniquely identify a software package:

Title: PURL Component Hierarchy
```mermaid
graph LR
    PURL["PURL String"]
    Type["Type<br/>(e.g., maven, npm, apk)"]
    Namespace["Namespace<br/>(optional)"]
    Name["Name<br/>(required)"]
    Version["Version<br/>(optional)"]
    Qualifiers["Qualifiers<br/>(key-value pairs)"]
    Subpath["Subpath<br/>(optional)"]
    
    PURL --> Type
    PURL --> Namespace
    PURL --> Name
    PURL --> Version
    PURL --> Qualifiers
    PURL --> Subpath
    
    Qualifiers --> Arch["arch"]
    Qualifiers --> Epoch["epoch"]
    Qualifiers --> Distro["distro"]
    Qualifiers --> Modularitylabel["modularitylabel"]
    Qualifiers --> RepositoryURL["repository_url"]
```

**PURL Component Examples:**

| Component | Example | Description |
|-----------|---------|-------------|
| Type | `maven`, `npm`, `rpm`, `apk` | Package ecosystem identifier |
| Namespace | `org.springframework`, `@angular` | Package grouping (org, scope) |
| Name | `spring-core`, `express` | Package identifier within namespace |
| Version | `5.3.14`, `1.2.0-r16` | Package version (optional for constraints) |
| Qualifiers | `?arch=amd64&distro=debian-11` | Additional metadata |
| Subpath | `#Analytics` | Component subpath (e.g., CocoaPods subspecs) |

Sources: [pkg/purl/purl.go:20-49](), [pkg/purl/purl_test.go:17-542]()

## PackageURL Type and Core Operations

Trivy wraps the standard `packageurl.PackageURL` type to provide ecosystem-specific functionality and integration with Trivy's internal types:

Title: PackageURL Type Architecture
```mermaid
graph TB
    subgraph "External Library"
        PkgURL["packageurl.PackageURL<br/>(github.com/package-url/packageurl-go)"]
    end
    
    subgraph "Trivy Wrapper (pkg/purl/purl.go)"
        TrivyPURL["purl.PackageURL<br/>(wrapper type)"]
        New["New(type, metadata, pkg)"]
        FromString["FromString(s)"]
        Unwrap["Unwrap()"]
        LangType["LangType()"]
        Class["Class()"]
        Package["Package()"]
        Match["Match(target)"]
    end
    
    subgraph "Trivy Types (pkg/fanal/types)"
        FanalPkg["ftypes.Package"]
        FanalType["ftypes.TargetType<br/>ftypes.LangType<br/>ftypes.OSType"]
        Metadata["types.Metadata"]
    end
    
    subgraph "Result Classes"
        ClassOSPkg["types.ClassOSPkg"]
        ClassLangPkg["types.ClassLangPkg"]
    end
    
    PkgURL -.wraps.- TrivyPURL
    TrivyPURL --> Unwrap
    Unwrap --> PkgURL
    
    FanalType --> New
    Metadata --> New
    FanalPkg --> New
    New --> TrivyPURL
    
    FromString --> TrivyPURL
    
    TrivyPURL --> LangType
    LangType --> FanalType
    
    TrivyPURL --> Class
    Class --> ClassOSPkg
    Class --> ClassLangPkg
    
    TrivyPURL --> Package
    Package --> FanalPkg
```

**Core Type Definition:**

The wrapper type at [pkg/purl/purl.go:51]() is a simple type alias that provides Trivy-specific methods:

```go
type PackageURL packageurl.PackageURL
```

Sources: [pkg/purl/purl.go:51-64](), [pkg/purl/purl.go:137-146]()

## Creating PURLs from Packages

The `New()` function at [pkg/purl/purl.go:67-135]() orchestrates PURL creation by dispatching to ecosystem-specific parsers based on the target type:

Title: PURL Generation Flow
```mermaid
graph TB
    Input["Input:<br/>TargetType<br/>Metadata<br/>Package"]
    New["purl.New()"]
    PurlType["purlType()<br/>Map TargetType to PURL type"]
    
    ParseQualifier["parseQualifier()<br/>Extract arch, epoch"]
    
    Decision{Package<br/>Type?}
    
    ParseRPM["parseRPM()<br/>namespace, qualifiers"]
    ParseDeb["parseDeb()<br/>qualifiers"]
    ParseApk["parseApk()<br/>lowercase name, namespace"]
    ParseMaven["parseMaven()<br/>split on ':'"]
    ParsePyPI["parsePyPI()<br/>lowercase, replace _"]
    ParseComposer["parseComposer()<br/>namespace/name"]
    ParseGolang["parseGolang()<br/>lowercase path"]
    ParseNpm["parseNpm()<br/>lowercase, split @scope"]
    ParseSwift["parseSwift()<br/>namespace/name"]
    ParseCocoapods["parseCocoapods()<br/>name, subpath"]
    ParseOCI["parseOCI()<br/>from RepoDigests"]
    ParseJulia["parseJulia()<br/>uuid qualifier"]
    
    Output["packageurl.NewPackageURL()<br/>Construct PURL"]
    
    Input --> New
    New --> PurlType
    New --> ParseQualifier
    New --> Decision
    
    Decision -->|rpm| ParseRPM
    Decision -->|deb| ParseDeb
    Decision -->|apk| ParseApk
    Decision -->|maven/gradle/sbt| ParseMaven
    Decision -->|pypi/pip| ParsePyPI
    Decision -->|composer| ParseComposer
    Decision -->|golang| ParseGolang
    Decision -->|npm/yarn/pnpm| ParseNpm
    Decision -->|swift| ParseSwift
    Decision -->|cocoapods| ParseCocoapods
    Decision -->|oci| ParseOCI
    Decision -->|julia| ParseJulia
    
    ParseRPM --> Output
    ParseDeb --> Output
    ParseApk --> Output
    ParseMaven --> Output
    ParsePyPI --> Output
    ParseComposer --> Output
    ParseGolang --> Output
    ParseNpm --> Output
    ParseSwift --> Output
    ParseCocoapods --> Output
    ParseOCI --> Output
    ParseJulia --> Output
```

**Type Mapping:**

The `purlType()` function at [pkg/purl/purl.go:454-501]() maps Trivy's internal types to PURL types:

| Trivy Type | PURL Type | Notes |
|------------|-----------|-------|
| `ftypes.Jar`, `ftypes.Pom`, `ftypes.Gradle`, `ftypes.Sbt` | `packageurl.TypeMaven` | Java packages use Maven PURL type |
| `ftypes.Npm`, `ftypes.Yarn`, `ftypes.Pnpm`, `ftypes.Bun` | `packageurl.TypeNPM` | All Node.js package managers |
| `ftypes.Alpine`, `ftypes.Chainguard`, `ftypes.Wolfi` | `packageurl.TypeApk` | Alpine-based distributions |
| `ftypes.Debian`, `ftypes.Ubuntu` | `packageurl.TypeDebian` | Debian-based distributions |
| `ftypes.RedHat`, `ftypes.CentOS`, `ftypes.Rocky`, etc. | `packageurl.TypeRPM` | RPM-based distributions |
| `ftypes.Bottlerocket` | `packageurlTypeBottlerocket` | Custom type (not yet in purl-spec) |

Sources: [pkg/purl/purl.go:67-135](), [pkg/purl/purl.go:454-501]()

## Ecosystem-Specific PURL Generation

Different package ecosystems have unique naming conventions and metadata requirements. Trivy implements specialized parsing for each:

### OS Package PURLs

Title: OS Ecosystem Mapping to PURL
```mermaid
graph TB
    subgraph "RPM Packages (parseRPM)"
        RPMInput["OS Info:<br/>Family, Name<br/>Modularitylabel"]
        RPMNamespace["Namespace:<br/>OS.Family.PurlNamespace()"]
        RPMQualifiers["Qualifiers:<br/>distro=family-name<br/>modularitylabel (if present)"]
        RPMOutput["Example:<br/>pkg:rpm/redhat/acl@2.2.53-1.el8?<br/>arch=aarch64&epoch=1&<br/>distro=redhat-8"]
    end
    
    subgraph "APK Packages (parseApk)"
        APKInput["Package Name<br/>OS Info"]
        APKLower["Lowercase name"]
        APKNamespace["Namespace:<br/>lowercase(OS.Family)"]
        APKQualifiers["Qualifiers:<br/>distro=OS.Name"]
        APKOutput["Example:<br/>pkg:apk/alpine/alpine-baselayout@<br/>3.2.0-r16?distro=3.14.2"]
    end
    
    subgraph "Debian Packages (parseDeb)"
        DebInput["OS Info:<br/>Family, Name"]
        DebNamespace["Namespace:<br/>OS.Family (debian, ubuntu)"]
        DebQualifiers["Qualifiers:<br/>distro=family-name"]
        DebOutput["Example:<br/>pkg:deb/ubuntu/libc6@2.31-0ubuntu9?<br/>distro=ubuntu-20.04"]
    end
```

The `PurlNamespace()` method at [pkg/fanal/types/const.go:67-77]() normalizes OS family names for PURL namespaces:

- SLES and SLE Micro → `"suse"`
- OpenSUSE variants → `"opensuse"`
- All others → string value of `OSType`

**Qualifiers for OS Packages:**

At [pkg/purl/purl.go:503-519](), base qualifiers are extracted:
- `arch`: Package architecture (e.g., `x86_64`, `arm64`)
- `epoch`: RPM epoch value (if non-zero)

At [pkg/purl/purl.go:78-103](), OS-specific qualifiers are added:
- `distro`: Distribution identifier (e.g., `redhat-8`, `debian-11`)
- `modularitylabel`: RPM modularity metadata (e.g., `nodejs:10:8020020200707141642:6a468ee4`)

Sources: [pkg/purl/purl.go:372-391](), [pkg/purl/purl.go:335-353](), [pkg/purl/purl.go:356-369](), [pkg/fanal/types/const.go:63-77]()

### Language Package PURLs

Title: Language Package PURL Parsing
```mermaid
graph TB
    subgraph "Maven/Gradle/SBT (parseMaven)"
        MavenInput["Name:<br/>'org.springframework:spring-core'"]
        MavenSplit["Split on ':'"]
        MavenNamespace["Namespace: 'org.springframework'"]
        MavenName["Name: 'spring-core'"]
        MavenOutput["pkg:maven/org.springframework/<br/>spring-core@5.3.14"]
    end
    
    subgraph "NPM/Yarn/Pnpm (parseNpm)"
        NPMInput["Name: '@angular/core'<br/>or 'lodash'"]
        NPMLower["Lowercase name"]
        NPMSplit["Split on last '/'"]
        NPMNamespace["Namespace: '@angular'<br/>or empty"]
        NPMName["Name: 'core' or 'lodash'"]
        NPMOutput["pkg:npm/%40angular/core@12.0.0<br/>or pkg:npm/lodash@4.17.21"]
    end
    
    subgraph "PyPI (parsePyPI)"
        PyPIInput["Name: 'Django_test'"]
        PyPILower["Lowercase"]
        PyPIReplace["Replace _ with -"]
        PyPIOutput["pkg:pypi/django-test@1.2.0"]
    end
    
    subgraph "Golang (parseGolang)"
        GoInput["Name: 'github.com/aquasecurity/trivy'"]
        GoLower["Lowercase"]
        GoCheck{"Local<br/>path?"}
        GoSplit["Split on last '/'"]
        GoNamespace["Namespace: 'github.com/aquasecurity'"]
        GoName["Name: 'trivy'"]
        GoOutput["pkg:golang/github.com/aquasecurity/<br/>trivy@v0.49.0"]
        GoSkip["Return nil<br/>(skip local paths)"]
        
        GoInput --> GoLower
        GoLower --> GoCheck
        GoCheck -->|"./" or "../"| GoSkip
        GoCheck -->|else| GoSplit
    end
    
    subgraph "CocoaPods (parseCocoapods)"
        CocoaInput["Name: 'GoogleUtilities/NSData+zlib'"]
        CocoaSplit["Split on '/'"]
        CocoaName["Name: 'GoogleUtilities'"]
        CocoaSubpath["Subpath: 'NSData+zlib'"]
        CocoaOutput["pkg:cocoapods/GoogleUtilities@7.5.2<br/>#NSData+zlib"]
    end
    
    subgraph "Julia (parseJulia)"
        JuliaInput["Name: 'Dates'<br/>ID (UUID): 'ade2ca70-...'"]
        JuliaQualifiers["Qualifiers:<br/>uuid=ade2ca70-..."]
        JuliaOutput["pkg:julia/Dates@1.9.0?<br/>uuid=ade2ca70-3891-5945-98fb-dc099432e06a"]
    end
```

Sources: [pkg/purl/purl.go:393-398](), [pkg/purl/purl.go:434-439](), [pkg/purl/purl.go:410-415](), [pkg/purl/purl.go:400-408](), [pkg/purl/purl.go:427-432](), [pkg/purl/purl.go:442-451]()

### Container Image PURLs

The `parseOCI()` function at [pkg/purl/purl.go:301-332]() creates OCI-type PURLs from container metadata:

Title: OCI PURL Extraction
```mermaid
graph TB
    Input["Metadata.RepoDigests"]
    Check{Has<br/>RepoDigests?}
    ParseDigest["Parse first RepoDigest<br/>using go-containerregistry"]
    ExtractName["Extract repository name<br/>(last path segment)"]
    ExtractRepo["Extract repository URL<br/>(full path)"]
    ExtractArch["Extract architecture<br/>from ImageConfig"]
    
    QualRepo["Qualifier:<br/>repository_url"]
    QualArch["Qualifier:<br/>arch"]
    
    Output["pkg:oci/core@sha256:8fe1727132b...?<br/>repository_url=cblmariner2preview.azurecr.io/base/core&<br/>arch=amd64"]
    
    Skip["Return nil<br/>(local image)"]
    
    Input --> Check
    Check -->|No| Skip
    Check -->|Yes| ParseDigest
    ParseDigest --> ExtractName
    ParseDigest --> ExtractRepo
    ParseDigest --> ExtractArch
    ExtractRepo --> QualRepo
    ExtractArch --> QualArch
    QualRepo --> Output
    QualArch --> Output
```

**OCI PURL Structure:**
- **Type:** `oci`
- **Name:** Last segment of repository path (lowercased)
- **Version:** Full SHA256 digest (e.g., `sha256:8fe1727132b...`)
- **Qualifiers:**
  - `repository_url`: Full repository path
  - `arch`: Image architecture

Sources: [pkg/purl/purl.go:301-332](), [pkg/purl/purl_test.go:346-422]()

## Converting PURLs to Packages

The `Package()` method at [pkg/purl/purl.go:215-264]() reconstructs `ftypes.Package` from a PURL:

Title: PURL to Package Reconstruction
```mermaid
graph TB
    PURL["PackageURL"]
    
    CheckClass{Class()}
    
    ReconstructName["Reconstruct Name"]
    NamespaceLogic{Has<br/>Namespace?}
    OSPkg["OS Package:<br/>name only"]
    MavenPkg["Maven/Gradle:<br/>namespace:name"]
    OtherPkg["Other Lang:<br/>namespace/name"]
    CocoaPods["CocoaPods:<br/>name/subpath"]
    
    ExtractQualifiers["Extract Qualifiers"]
    ArchQual["arch qualifier → Package.Arch"]
    EpochQual["epoch qualifier → Package.Epoch"]
    ModQual["modularitylabel → Package.Modularitylabel"]
    
    RPMVersion{Type ==<br/>RPM?}
    SplitVersion["Split version into<br/>Version + Release"]
    KeepVersion["Keep version as-is"]
    
    CreateID["Generate Package.ID<br/>dependency.ID(LangType, name, version)"]
    
    Output["ftypes.Package<br/>with PURL in Identifier"]
    
    PURL --> CheckClass
    CheckClass --> ReconstructName
    
    ReconstructName --> NamespaceLogic
    NamespaceLogic -->|ClassOSPkg| OSPkg
    NamespaceLogic -->|Maven| MavenPkg
    NamespaceLogic -->|Other| OtherPkg
    ReconstructName -->|CocoaPods| CocoaPods
    
    OSPkg --> ExtractQualifiers
    MavenPkg --> ExtractQualifiers
    OtherPkg --> ExtractQualifiers
    CocoaPods --> ExtractQualifiers
    
    ExtractQualifiers --> ArchQual
    ExtractQualifiers --> EpochQual
    ExtractQualifiers --> ModQual
    
    ArchQual --> RPMVersion
    EpochQual --> RPMVersion
    ModQual --> RPMVersion
    
    RPMVersion -->|Yes| SplitVersion
    RPMVersion -->|No| KeepVersion
    
    SplitVersion --> CreateID
    KeepVersion --> CreateID
    
    CreateID --> Output
```

**Name Reconstruction Logic:**

At [pkg/purl/purl.go:216-233](), package names are reconstructed based on ecosystem conventions:

| Ecosystem | Namespace Present? | Reconstructed Name |
|-----------|-------------------|-------------------|
| OS Packages | Any | `name` (namespace ignored) |
| Maven/Gradle | Yes | `namespace:name` |
| Other Languages | Yes | `namespace/name` |
| CocoaPods | Subpath present | `name/subpath` |

**RPM Version Splitting:**

At [pkg/purl/purl.go:257-261](), RPM packages require special handling:
- PURL version contains combined `version-release`
- Must split using `version.NewVersion()` from `github.com/knqyf263/go-rpm-version`
- Separate into `Package.Version` and `Package.Release` fields

Sources: [pkg/purl/purl.go:215-264](), [pkg/purl/purl_test.go:662-926]()

## PURL Matching and Comparison

The `Match()` method at [pkg/purl/purl.go:269-294]() implements constraint-based matching for VEX statements and ignore policies:

Title: PURL Matching Logic
```mermaid
graph TB
    Constraint["Constraint PURL<br/>(from policy/VEX)"]
    Target["Target PURL<br/>(from scan result)"]
    
    CheckType{Type<br/>matches?}
    CheckNamespace{Namespace<br/>matches?}
    CheckName{Name<br/>matches?}
    CheckVersion{Version<br/>check}
    VersionEmpty{Constraint<br/>version<br/>empty?}
    VersionMatch{Versions<br/>match?}
    CheckSubpath{Subpath<br/>check}
    SubpathEmpty{Constraint<br/>subpath<br/>empty?}
    SubpathMatch{Subpaths<br/>match?}
    CheckQualifiers["Check Qualifiers"]
    QualMatch{All constraint<br/>qualifiers in<br/>target?}
    
    Match["Return true"]
    NoMatch["Return false"]
    
    Constraint --> CheckType
    Target --> CheckType
    
    CheckType -->|Different| NoMatch
    CheckType -->|Same| CheckNamespace
    
    CheckNamespace -->|Different| NoMatch
    CheckNamespace -->|Same| CheckName
    
    CheckName -->|Different| NoMatch
    CheckName -->|Same| CheckVersion
    
    CheckVersion --> VersionEmpty
    VersionEmpty -->|Yes| CheckSubpath
    VersionEmpty -->|No| VersionMatch
    VersionMatch -->|Different| NoMatch
    VersionMatch -->|Same| CheckSubpath
    
    CheckSubpath --> SubpathEmpty
    SubpathEmpty -->|Yes| CheckQualifiers
    SubpathEmpty -->|No| SubpathMatch
    SubpathMatch -->|Different| NoMatch
    SubpathMatch -->|Same| CheckQualifiers
    
    CheckQualifiers --> QualMatch
    QualMatch -->|No| NoMatch
    QualMatch -->|Yes| Match
```

**Matching Rules:**

1. **Type, Namespace, Name:** Must match exactly
2. **Version:** 
   - If constraint has empty version → matches any target version (wildcard)
   - If constraint has version → must match target version exactly
3. **Subpath:**
   - If constraint has empty subpath → matches any target subpath
   - If constraint has subpath → must match target subpath exactly
4. **Qualifiers:**
   - All qualifiers in constraint must be present in target with same values
   - Target may have additional qualifiers not in constraint

Sources: [pkg/purl/purl.go:266-294](), [pkg/purl/purl_test.go:972-1039]()

## Integration with Vulnerability Detection

The PURL system integrates with vulnerability detection through language type mapping and normalized package names:

Title: PURL Integration in Scanning Pipeline
```mermaid
graph TB
    subgraph "Scan Result"
        Package["ftypes.Package<br/>Name, Version<br/>Identifier.PURL"]
    end
    
    subgraph "PURL System (pkg/purl)"
        GetLangType["PackageURL.LangType()"]
        PURLType["PURL Type"]
        MapToLangType["Map to ftypes.LangType"]
    end
    
    subgraph "Library Detector (pkg/detector/library)"
        NewDriver["library.NewDriver(langType)"]
        DriverMap{Language<br/>Type?}
        Ecosystem["Map to ecosystem.Type"]
        Comparer["Select compare.Comparer"]
        Driver["library.Driver"]
        DetectVulns["DetectVulnerabilities(pkgID, name, ver)"]
        QueryDB["Query DB with prefix<br/>'ecosystem::'"]
        NormalizeName["vulnerability.NormalizePkgName()"]
        GetAdvisories["dbc.GetAdvisories(prefix, normalizedName)"]
        CompareVersions["comparer.IsVulnerable(version, advisory)"]
    end
    
    subgraph "Vulnerability Database"
        DBBucket["Bucket: 'npm::GitLab Advisory Database'"]
        NormalizedKey["Key: normalized package name"]
        Advisory["Advisory with version ranges"]
    end
    
    Package --> GetLangType
    GetLangType --> PURLType
    PURLType --> MapToLangType
    MapToLangType --> NewDriver
    
    NewDriver --> DriverMap
    DriverMap --> Ecosystem
    DriverMap --> Comparer
    Ecosystem --> Driver
    Comparer --> Driver
    
    Driver --> DetectVulns
    DetectVulns --> QueryDB
    QueryDB --> NormalizeName
    NormalizeName --> GetAdvisories
    GetAdvisories --> DBBucket
    DBBucket --> NormalizedKey
    NormalizedKey --> Advisory
    Advisory --> CompareVersions
```

**LangType Mapping:**

The `LangType()` method at [pkg/purl/purl.go:150-199]() maps PURL types back to Trivy's language types:

| PURL Type | Trivy LangType | Used For |
|-----------|----------------|----------|
| `maven` | `ftypes.Jar` | Maven packages in JARs |
| `npm` | `ftypes.NodePkg` | Node.js packages |
| `pypi` | `ftypes.PythonPkg` | Python packages |
| `golang` | `ftypes.GoBinary` | Go binaries |
| `gem` | `ftypes.GemSpec` | Ruby gems |
| `cargo` | `ftypes.Cargo` | Rust crates |
| `composer` | `ftypes.Composer` | PHP packages |
| `nuget` | `ftypes.NuGet` | .NET packages |
| `k8s` (with namespace) | `ftypes.EKS`, `ftypes.GKE`, `ftypes.AKS`, `ftypes.OCP` | Kubernetes components |
| `k8s` (no namespace) | `ftypes.K8sUpstream` | Upstream K8s |

**Ecosystem-Based Detection:**

At [pkg/detector/library/driver.go:26-98](), the driver maps language types to ecosystems:

```go
// Example mappings from NewDriver()
case ftypes.Npm, ftypes.Yarn, ftypes.Pnpm, ftypes.Bun, ftypes.NodePkg:
    eco = ecosystem.Npm
case ftypes.Pip, ftypes.Pipenv, ftypes.Poetry, ftypes.PythonPkg:
    eco = ecosystem.Pip
case ftypes.GoBinary, ftypes.GoModule:
    eco = ecosystem.Go
```

At [pkg/detector/library/driver.go:116-144](), vulnerability detection queries the database using ecosystem prefixes (e.g., `pip::`, `npm::`).

Sources: [pkg/purl/purl.go:148-213](), [pkg/detector/library/driver.go:26-98](), [pkg/detector/library/driver.go:112-167]()

## Custom PURL Types

Trivy defines custom PURL types not yet standardized in the purl-spec:

### TypeK8s

At [pkg/purl/purl.go:23-42](), Trivy defines `TypeK8s` for Kubernetes components:

**Structure:**
- **Type:** `k8s`
- **Namespace:** Service provider (empty for upstream, `eks`, `aks`, `gke`, `rke`, `ocp`)
- **Name:** Component name (e.g., `k8s.io%2Fapiserver`)
- **Version:** Combined version and release (e.g., `1.24.1`)

### TypeBottlerocket

At [pkg/purl/purl.go:48](), the constant `packageurlTypeBottlerocket` provides support for Bottlerocket OS packages:

**Structure:**
- **Type:** `bottlerocket` 
- **Qualifiers:** `distro=bottlerocket-<OS.Name>`

Sources: [pkg/purl/purl.go:20-49](), [pkg/purl/purl_test.go:456-491]()

## String Parsing and Serialization

### FromString()

The `FromString()` function at [pkg/purl/purl.go:53-64]() parses PURL strings and normalizes empty qualifiers to `nil`.

### String()

The `String()` method at [pkg/purl/purl.go:296-298]() serializes PURLs by delegating to the underlying `packageurl.PackageURL.String()` method.

Sources: [pkg/purl/purl.go:53-64](), [pkg/purl/purl.go:296-298](), [pkg/purl/purl_test.go:544-660]()

## PURL Type Constants and Mapping

The complete type mapping is implemented in `purlType()` at [pkg/purl/purl.go:454-501]():

| Trivy Types | PURL Type |
|-------------|-----------|
| `Jar`, `Pom`, `Gradle`, `Sbt` | `maven` |
| `Bundler`, `GemSpec` | `gem` |
| `NuGet`, `DotNetCore`, `PackagesProps` | `nuget` |
| `Composer`, `ComposerVendor` | `composer` |
| `PythonPkg`, `Pip`, `Pipenv`, `Poetry`, `Uv` | `pypi` |
| `GoBinary`, `GoModule` | `golang` |
| `Npm`, `NodePkg`, `Yarn`, `Pnpm`, `Bun` | `npm` |
| `Julia` | `julia` |

Sources: [pkg/purl/purl.go:454-501](), [pkg/fanal/types/const.go:23-136]()

---

# Page: Analyzer Types and Language Support

# Analyzer Types and Language Support

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/guide/coverage/language/golang.md](docs/guide/coverage/language/golang.md)
- [docs/guide/coverage/language/nodejs.md](docs/guide/coverage/language/nodejs.md)
- [pkg/dependency/parser/golang/binary/elf.go](pkg/dependency/parser/golang/binary/elf.go)
- [pkg/dependency/parser/golang/binary/export_test.go](pkg/dependency/parser/golang/binary/export_test.go)
- [pkg/dependency/parser/golang/binary/parse.go](pkg/dependency/parser/golang/binary/parse.go)
- [pkg/dependency/parser/golang/binary/parse_internal_test.go](pkg/dependency/parser/golang/binary/parse_internal_test.go)
- [pkg/dependency/parser/golang/binary/parse_test.go](pkg/dependency/parser/golang/binary/parse_test.go)
- [pkg/dependency/parser/golang/binary/testdata/goexperiment](pkg/dependency/parser/golang/binary/testdata/goexperiment)
- [pkg/dependency/parser/golang/binary/testdata/main-version-via-ldflags.elf](pkg/dependency/parser/golang/binary/testdata/main-version-via-ldflags.elf)
- [pkg/dependency/parser/golang/binary/testdata/semver-main-module-version.macho](pkg/dependency/parser/golang/binary/testdata/semver-main-module-version.macho)
- [pkg/dependency/parser/golang/mod/testdata/replaced-with-local-path-and-version-mismatch/go.sum](pkg/dependency/parser/golang/mod/testdata/replaced-with-local-path-and-version-mismatch/go.sum)
- [pkg/dependency/parser/java/pom/artifact.go](pkg/dependency/parser/java/pom/artifact.go)
- [pkg/dependency/parser/java/pom/parse.go](pkg/dependency/parser/java/pom/parse.go)
- [pkg/dependency/parser/java/pom/parse_test.go](pkg/dependency/parser/java/pom/parse_test.go)
- [pkg/dependency/parser/java/pom/pom.go](pkg/dependency/parser/java/pom/pom.go)
- [pkg/dependency/parser/java/pom/repository.go](pkg/dependency/parser/java/pom/repository.go)
- [pkg/dependency/parser/java/pom/settings.go](pkg/dependency/parser/java/pom/settings.go)
- [pkg/dependency/parser/java/pom/settings_test.go](pkg/dependency/parser/java/pom/settings_test.go)
- [pkg/dependency/parser/java/pom/testdata/exclusions-parent-dependency-management/child/pom.xml](pkg/dependency/parser/java/pom/testdata/exclusions-parent-dependency-management/child/pom.xml)
- [pkg/dependency/parser/java/pom/testdata/exclusions-parent-dependency-management/pom.xml](pkg/dependency/parser/java/pom/testdata/exclusions-parent-dependency-management/pom.xml)
- [pkg/dependency/parser/java/pom/testdata/happy/pom.xml](pkg/dependency/parser/java/pom/testdata/happy/pom.xml)
- [pkg/dependency/parser/java/pom/testdata/repository-for-settings-repo/org/example/example-api/1.7.30/example-api-1.7.30.pom](pkg/dependency/parser/java/pom/testdata/repository-for-settings-repo/org/example/example-api/1.7.30/example-api-1.7.30.pom)
- [pkg/dependency/parser/java/pom/testdata/repository/org/example/example-exclusions/3.0.0/example-exclusions-3.0.0.pom](pkg/dependency/parser/java/pom/testdata/repository/org/example/example-exclusions/3.0.0/example-exclusions-3.0.0.pom)
- [pkg/dependency/parser/java/pom/testdata/repository/org/example/example-nested/3.3.5/example-nested-3.3.5.pom](pkg/dependency/parser/java/pom/testdata/repository/org/example/example-nested/3.3.5/example-nested-3.3.5.pom)
- [pkg/dependency/parser/java/pom/testdata/settings/global-with-proxy/conf/settings.xml](pkg/dependency/parser/java/pom/testdata/settings/global-with-proxy/conf/settings.xml)
- [pkg/dependency/parser/java/pom/testdata/settings/global/conf/settings.xml](pkg/dependency/parser/java/pom/testdata/settings/global/conf/settings.xml)
- [pkg/dependency/parser/java/pom/testdata/settings/user-settings-with-env-placeholders/.m2/settings.xml](pkg/dependency/parser/java/pom/testdata/settings/user-settings-with-env-placeholders/.m2/settings.xml)
- [pkg/dependency/parser/java/pom/testdata/settings/user-with-proxy/.m2/settings.xml](pkg/dependency/parser/java/pom/testdata/settings/user-with-proxy/.m2/settings.xml)
- [pkg/dependency/parser/java/pom/testdata/settings/user/.m2/settings.xml](pkg/dependency/parser/java/pom/testdata/settings/user/.m2/settings.xml)
- [pkg/dependency/parser/nodejs/npm/parse.go](pkg/dependency/parser/nodejs/npm/parse.go)
- [pkg/dependency/parser/nodejs/npm/parse_test.go](pkg/dependency/parser/nodejs/npm/parse_test.go)
- [pkg/dependency/parser/nodejs/npm/parse_testcase.go](pkg/dependency/parser/nodejs/npm/parse_testcase.go)
- [pkg/dependency/parser/nodejs/npm/testdata/package-lock_v3_broken_link.json](pkg/dependency/parser/nodejs/npm/testdata/package-lock_v3_broken_link.json)
- [pkg/dependency/parser/nodejs/npm/testdata/package-lock_v3_with-same-dev-and-non-dev.json](pkg/dependency/parser/nodejs/npm/testdata/package-lock_v3_with-same-dev-and-non-dev.json)
- [pkg/dependency/parser/nodejs/npm/testdata/package-lock_v3_with_peer.json](pkg/dependency/parser/nodejs/npm/testdata/package-lock_v3_with_peer.json)
- [pkg/dependency/parser/nodejs/npm/testdata/package-lock_v3_with_workspace_as_object.json](pkg/dependency/parser/nodejs/npm/testdata/package-lock_v3_with_workspace_as_object.json)
- [pkg/dependency/parser/nodejs/packagejson/parse.go](pkg/dependency/parser/nodejs/packagejson/parse.go)
- [pkg/dependency/parser/nodejs/packagejson/parse_test.go](pkg/dependency/parser/nodejs/packagejson/parse_test.go)
- [pkg/dependency/parser/nodejs/packagejson/testdata/invalid_name.json](pkg/dependency/parser/nodejs/packagejson/testdata/invalid_name.json)
- [pkg/dependency/parser/nodejs/packagejson/testdata/workspace_as_map_package.json](pkg/dependency/parser/nodejs/packagejson/testdata/workspace_as_map_package.json)
- [pkg/dependency/parser/nuget/lock/parse_test.go](pkg/dependency/parser/nuget/lock/parse_test.go)
- [pkg/dependency/parser/python/pip/parse.go](pkg/dependency/parser/python/pip/parse.go)
- [pkg/dependency/parser/python/pip/parse_test.go](pkg/dependency/parser/python/pip/parse_test.go)
- [pkg/dependency/parser/python/pip/parse_testcase.go](pkg/dependency/parser/python/pip/parse_testcase.go)
- [pkg/dependency/parser/python/pip/testdata/requirements_compatible.txt](pkg/dependency/parser/python/pip/testdata/requirements_compatible.txt)
- [pkg/dependency/parser/python/pip/testdata/requirements_no_version.txt](pkg/dependency/parser/python/pip/testdata/requirements_no_version.txt)
- [pkg/dependency/parser/python/pip/testdata/requirements_operator.txt](pkg/dependency/parser/python/pip/testdata/requirements_operator.txt)
- [pkg/dependency/parser/python/pip/testdata/requirements_with_templating_engine.txt](pkg/dependency/parser/python/pip/testdata/requirements_with_templating_engine.txt)
- [pkg/dependency/parser/python/poetry/parse.go](pkg/dependency/parser/python/poetry/parse.go)
- [pkg/dependency/parser/python/pyproject/pyproject.go](pkg/dependency/parser/python/pyproject/pyproject.go)
- [pkg/dependency/parser/python/pyproject/pyproject_test.go](pkg/dependency/parser/python/pyproject/pyproject_test.go)
- [pkg/dependency/parser/python/pyproject/testdata/happy_with_optional_only.toml](pkg/dependency/parser/python/pyproject/testdata/happy_with_optional_only.toml)
- [pkg/dependency/parser/python/python.go](pkg/dependency/parser/python/python.go)
- [pkg/dependency/parser/python/python_test.go](pkg/dependency/parser/python/python_test.go)
- [pkg/detector/ospkg/seal/provider.go](pkg/detector/ospkg/seal/provider.go)
- [pkg/detector/ospkg/seal/provider_test.go](pkg/detector/ospkg/seal/provider_test.go)
- [pkg/detector/ospkg/version/compare.go](pkg/detector/ospkg/version/compare.go)
- [pkg/fanal/analyzer/analyzer.go](pkg/fanal/analyzer/analyzer.go)
- [pkg/fanal/analyzer/analyzer_test.go](pkg/fanal/analyzer/analyzer_test.go)
- [pkg/fanal/analyzer/language/golang/binary/binary_test.go](pkg/fanal/analyzer/language/golang/binary/binary_test.go)
- [pkg/fanal/analyzer/language/java/pom/pom_test.go](pkg/fanal/analyzer/language/java/pom/pom_test.go)
- [pkg/fanal/analyzer/language/nodejs/npm/npm.go](pkg/fanal/analyzer/language/nodejs/npm/npm.go)
- [pkg/fanal/analyzer/language/nodejs/npm/npm_test.go](pkg/fanal/analyzer/language/nodejs/npm/npm_test.go)
- [pkg/fanal/analyzer/language/nodejs/npm/testdata/happy/node_modules/@babel/parser/package.json](pkg/fanal/analyzer/language/nodejs/npm/testdata/happy/node_modules/@babel/parser/package.json)
- [pkg/fanal/analyzer/language/nodejs/npm/testdata/happy/package-lock.json](pkg/fanal/analyzer/language/nodejs/npm/testdata/happy/package-lock.json)
- [pkg/fanal/analyzer/language/python/packaging/egg_test.go](pkg/fanal/analyzer/language/python/packaging/egg_test.go)
- [pkg/fanal/analyzer/language/python/packaging/packaging.go](pkg/fanal/analyzer/language/python/packaging/packaging.go)
- [pkg/fanal/analyzer/language/python/packaging/packaging_test.go](pkg/fanal/analyzer/language/python/packaging/packaging_test.go)
- [pkg/fanal/analyzer/language/python/pip/pip.go](pkg/fanal/analyzer/language/python/pip/pip.go)
- [pkg/fanal/analyzer/language/python/pip/pip_test.go](pkg/fanal/analyzer/language/python/pip/pip_test.go)
- [pkg/fanal/analyzer/language/python/pip/testdata/happy/requirements.txt](pkg/fanal/analyzer/language/python/pip/testdata/happy/requirements.txt)
- [pkg/fanal/analyzer/language/python/pip/testdata/libs/common-dir/lib/site-packages/annotated_types-0.7.0.dist-info/METADATA](pkg/fanal/analyzer/language/python/pip/testdata/libs/common-dir/lib/site-packages/annotated_types-0.7.0.dist-info/METADATA)
- [pkg/fanal/analyzer/language/python/pip/testdata/libs/python-dir/lib/python3.10/site-packages/annotated_types-0.7.0.dist-info/METADATA](pkg/fanal/analyzer/language/python/pip/testdata/libs/python-dir/lib/python3.10/site-packages/annotated_types-0.7.0.dist-info/METADATA)
- [pkg/fanal/analyzer/language/python/poetry/poetry.go](pkg/fanal/analyzer/language/python/poetry/poetry.go)
- [pkg/fanal/analyzer/language/python/poetry/poetry_test.go](pkg/fanal/analyzer/language/python/poetry/poetry_test.go)
- [pkg/fanal/analyzer/language/python/poetry/testdata/happy/poetry.lock](pkg/fanal/analyzer/language/python/poetry/testdata/happy/poetry.lock)
- [pkg/fanal/analyzer/language/python/poetry/testdata/happy/pyproject.toml](pkg/fanal/analyzer/language/python/poetry/testdata/happy/pyproject.toml)
- [pkg/fanal/analyzer/language/python/poetry/testdata/no-pyproject/poetry.lock](pkg/fanal/analyzer/language/python/poetry/testdata/no-pyproject/poetry.lock)
- [pkg/fanal/analyzer/language/python/poetry/testdata/optional-groups/poetry.lock](pkg/fanal/analyzer/language/python/poetry/testdata/optional-groups/poetry.lock)
- [pkg/fanal/analyzer/language/python/poetry/testdata/optional-groups/pyproject.toml](pkg/fanal/analyzer/language/python/poetry/testdata/optional-groups/pyproject.toml)
- [pkg/fanal/analyzer/language/rust/cargo/cargo.go](pkg/fanal/analyzer/language/rust/cargo/cargo.go)
- [pkg/fanal/analyzer/language/rust/cargo/cargo_test.go](pkg/fanal/analyzer/language/rust/cargo/cargo_test.go)
- [pkg/fanal/analyzer/pkg/apk/apk.go](pkg/fanal/analyzer/pkg/apk/apk.go)
- [pkg/fanal/analyzer/pkg/apk/apk_test.go](pkg/fanal/analyzer/pkg/apk/apk_test.go)
- [pkg/fanal/analyzer/pkg/apk/testdata/apk](pkg/fanal/analyzer/pkg/apk/testdata/apk)
- [pkg/fanal/applier/applier.go](pkg/fanal/applier/applier.go)
- [pkg/fanal/applier/applier_test.go](pkg/fanal/applier/applier_test.go)
- [pkg/fanal/artifact/artifact.go](pkg/fanal/artifact/artifact.go)
- [pkg/fanal/artifact/image/image.go](pkg/fanal/artifact/image/image.go)
- [pkg/fanal/artifact/image/image_test.go](pkg/fanal/artifact/image/image_test.go)
- [pkg/fanal/artifact/local/fs.go](pkg/fanal/artifact/local/fs.go)
- [pkg/fanal/artifact/local/fs_test.go](pkg/fanal/artifact/local/fs_test.go)
- [pkg/fanal/artifact/sbom/sbom_test.go](pkg/fanal/artifact/sbom/sbom_test.go)
- [pkg/fanal/artifact/vm/vm_test.go](pkg/fanal/artifact/vm/vm_test.go)
- [pkg/fanal/test/integration/testdata/goldens/packages/alpine-310.json.golden](pkg/fanal/test/integration/testdata/goldens/packages/alpine-310.json.golden)
- [pkg/fanal/test/integration/testdata/goldens/packages/vulnimage.json.golden](pkg/fanal/test/integration/testdata/goldens/packages/vulnimage.json.golden)
- [pkg/fanal/test/integration/testdata/goldens/vuln-image1.2.3.expectedlibs.golden](pkg/fanal/test/integration/testdata/goldens/vuln-image1.2.3.expectedlibs.golden)
- [pkg/fanal/types/artifact.go](pkg/fanal/types/artifact.go)
- [pkg/x/http/transport.go](pkg/x/http/transport.go)
- [pkg/x/path/path.go](pkg/x/path/path.go)
- [pkg/x/path/path_test.go](pkg/x/path/path_test.go)

</details>



## Purpose and Scope

This page documents Trivy's analyzer system, which extracts packages, dependencies, and metadata from various artifact types. Analyzers are specialized components that understand specific file formats, package managers, and operating systems. This page covers the different analyzer categories, supported languages and ecosystems, and how analyzers map to vulnerability detection systems.

For information about how analyzers process container layers and extract packages, see [3.1 Layer Processing and Package Extraction](). For details on how extracted packages are standardized using PURLs, see [3.2 Package URL (PURL) System]().

## Analyzer Architecture

Trivy's analyzer system is organized into distinct categories based on what they analyze. Each analyzer is registered globally and activated based on the scan target and enabled scanners. The analyzer type (`analyzer.Type`) serves as a unique identifier for each analyzer and determines its behavior during artifact scanning.

### Core Data Flow and Entity Mapping

The following diagram bridges the gap between the conceptual scanning process and the specific code entities that handle artifact analysis.

**Title: Analyzer Orchestration and Result Flow**
```mermaid
graph TD
    subgraph "Natural Language Space"
        Target["Scan Target (Image/FS/Repo)"]
        Res["Analysis Result"]
        Cache["Local/Remote Cache"]
    end

    subgraph "Code Entity Space (pkg/fanal/artifact)"
        NewArt["NewArtifact()"]
        Inspect["Artifact.Inspect(ctx)"]
        AGroup["analyzer.AnalyzerGroup"]
        HManager["handler.Manager"]
    end

    subgraph "Analysis Logic (pkg/fanal/analyzer)"
        Register["RegisterAnalyzer(analyzer)"]
        Analyze["analyzer.Analyze(ctx, input)"]
        AResult["AnalysisResult struct"]
    end

    Target --> NewArt
    NewArt --> Inspect
    Inspect --> AGroup
    Inspect --> HManager
    AGroup --> Analyze
    Analyze --> AResult
    AResult --> Res
    Inspect -.-> Cache
```
Sources: [pkg/fanal/artifact/image/image.go:53-87](), [pkg/fanal/artifact/local/fs.go:56-99](), [pkg/fanal/analyzer/analyzer.go:176-197]()

## Analyzer Type Hierarchy

Trivy defines analyzer types as constants that identify specific analyzers. These types are organized into logical groupings for different purposes.

### OS Package Analyzers

OS analyzers detect and extract information about operating system packages and distributions. The analysis typically involves parsing package manager databases like `apk` (Alpine), `dpkg` (Debian/Ubuntu), or `rpm` (RHEL/CentOS).

| Analyzer Type | Implementation File | Purpose | Target Files |
|--------------|---------------------|---------|--------------|
| `TypeApk` | `pkg/fanal/analyzer/pkg/apk/apk.go` | Alpine package manager | `lib/apk/db/installed` |
| `TypeDpkg` | `pkg/fanal/analyzer/pkg/dpkg/dpkg.go` | Debian package manager | `var/lib/dpkg/status` |
| `TypeRpm` | `pkg/fanal/analyzer/pkg/rpm/rpm.go` | Red Hat package manager | RPM database |
| `TypeAlpine` | `pkg/fanal/analyzer/os/alpine/alpine.go` | Detects Alpine OS version | `/etc/alpine-release` |

Sources: [pkg/fanal/artifact/local/fs_test.go:60-77](), [pkg/fanal/analyzer/pkg/apk/apk.go:1-50]()

### Language-Specific Analyzers

Language analyzers extract dependency information from various programming language ecosystems. They are split into two main categories: **Lockfile Analyzers** (source code) and **Installed Package Analyzers** (binaries/runtimes).

**Title: Language Support and Parser Mapping**
```mermaid
graph LR
    subgraph "Language Ecosystems"
        Go["Go"]
        Java["Java"]
        Python["Python"]
        Node["Node.js"]
    end

    subgraph "Parsers (pkg/dependency/parser)"
        GoParser["golang/binary.Parser"]
        PomParser["java/pom.Parser"]
        PipParser["python/pip.Parser"]
        NpmParser["nodejs/npm.Parser"]
    end

    subgraph "Analyzers (pkg/fanal/analyzer/language)"
        GoAn["golang/binary.go"]
        JavaAn["java/pom.go"]
        PythonAn["python/pip.go"]
        NodeAn["nodejs/npm.go"]
    end

    Go --> GoParser --> GoAn
    Java --> PomParser --> JavaAn
    Python --> PipParser --> PythonAn
    Node --> NpmParser --> NodeAn
```
Sources: [pkg/dependency/parser/golang/binary/parse.go:47-55](), [pkg/dependency/parser/java/pom/parse.go:74-83](), [pkg/fanal/analyzer/language/python/pip/pip.go:1-30]()

#### Key Language Implementation Details

*   **Go Binary Analysis**: Extracts standard library and module versions directly from compiled ELF, PE, or Mach-O binaries using `debug/buildinfo`. It prioritizes real SemVer versions over pseudo-versions or `(devel)` stamps.
    *   Sources: [pkg/dependency/parser/golang/binary/parse.go:71-149](), [pkg/dependency/parser/golang/binary/parse.go:173-184]()
*   **Java (Maven) Analysis**: Parses `pom.xml` files. It supports parent POM inheritance, property evaluation, and remote repository resolution (e.g., Maven Central) to build a complete dependency graph.
    *   Sources: [pkg/dependency/parser/java/pom/parse.go:149-175](), [pkg/dependency/parser/java/pom/pom.go:29-47]()
*   **Python Analysis**: Supports `requirements.txt`, `Pipfile.lock`, `poetry.lock`, and `uv.lock`. It uses PEP 440 compliant version comparers.
    *   Sources: [pkg/fanal/analyzer/language/python/poetry/poetry.go:1-40](), [pkg/fanal/artifact/local/fs_test.go:152-170]()

## Analyzer Groups and Activation

Trivy organizes analyzers into logical groups for selective activation and disabling during scans.

| Target Type | Logic |
|-------------|-------|
| **Container Image** | Uses `Image.Inspect()`. It prioritizes installed packages (`TypeIndividualPkgs`) over lockfiles, as images represent a runtime state. |
| **Filesystem** | Uses `local.Artifact.Inspect()`. It can use `StaticPathAnalyzer` to skip full directory traversal if only specific files (like `pom.xml` or `go.mod`) are relevant. |
| **Repository** | Detects Git metadata (commit hash, branch) and focuses on source-level lockfiles. |

Sources: [pkg/fanal/artifact/image/image.go:89-169](), [pkg/fanal/artifact/local/fs.go:169-215](), [pkg/fanal/artifact/local/fs.go:83-96]()

## Special-Purpose Analyzers

### Secret and License Scanning
*   **Secret Analyzer**: Scans file content for sensitive patterns (API keys, tokens).
*   **License Analyzer**: Classifies licenses found in packages or standalone license files.
Sources: [pkg/fanal/analyzer/analyzer.go:56-64](), [pkg/fanal/artifact/local/fs_test.go:24-25]()

### Config and Misconfiguration Analyzers
These analyzers process IaC files (Terraform, Dockerfile, Kubernetes YAML) and are managed via `analyzer.ConfigAnalyzerGroup`.
Sources: [pkg/fanal/artifact/image/image.go:45-68]()

## Implementation of Analysis Results

The `AnalysisResult` struct is the primary data structure returned by all analyzers. It aggregates detected OS, packages, applications, and security findings.

```go
type AnalysisResult struct {
	m                    sync.Mutex
	OS                   types.OS
	Repository           *types.Repository
	PackageInfos         []types.PackageInfo
	Applications         []types.Application
	Misconfigurations    []types.Misconfiguration
	Secrets              []types.Secret
	Licenses             []types.LicenseFile
	SystemInstalledFiles []string 
    // ...
}
```
Sources: [pkg/fanal/analyzer/analyzer.go:176-197]()

### Result Merging and Normalization
Trivy implements logic to merge results from multiple layers or files. For example, if an OS is detected as `RedHat` in one layer but `Oracle` in another (due to file overlaps), the more specific detection wins.
Sources: [pkg/fanal/types/artifact.go:51-82](), [pkg/fanal/analyzer/analyzer_test.go:35-157]()

## Summary of Language Support Matrix

| Ecosystem | Analyzer Type | Primary Parser | Key Implementation |
|-----------|---------------|----------------|-------------------|
| **Go** | `TypeGoBinary` | `golang/binary` | Extracts from ELF/PE/Mach-O |
| **Java** | `TypePom` | `java/pom` | Resolves inheritance/properties |
| **Python** | `TypePoetry` | `python/poetry` | Parses `poetry.lock` |
| **Node.js** | `TypeNpmPkgLock` | `nodejs/npm` | Parses `package-lock.json` |
| **Rust** | `TypeCargo` | `rust/cargo` | Parses `Cargo.lock` |

Sources: [pkg/dependency/parser/golang/binary/parse.go:1-50](), [pkg/dependency/parser/java/pom/parse.go:1-50](), [pkg/fanal/analyzer/language/python/poetry/poetry.go:1-20](), [pkg/fanal/analyzer/language/nodejs/npm/npm.go:1-20]()

---

# Page: Scanning Capabilities

# Scanning Capabilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/guide/coverage/os/photon.md](docs/guide/coverage/os/photon.md)
- [docs/guide/scanner/vulnerability.md](docs/guide/scanner/vulnerability.md)
- [integration/testdata/fixtures/db/data-source.yaml](integration/testdata/fixtures/db/data-source.yaml)
- [integration/testdata/fixtures/db/go.yaml](integration/testdata/fixtures/db/go.yaml)
- [integration/testdata/fixtures/db/oracle.yaml](integration/testdata/fixtures/db/oracle.yaml)
- [integration/testdata/fixtures/db/redhat.yaml](integration/testdata/fixtures/db/redhat.yaml)
- [pkg/dependency/parser/java/pom/var.go](pkg/dependency/parser/java/pom/var.go)
- [pkg/detector/ospkg/alpine/alpine.go](pkg/detector/ospkg/alpine/alpine.go)
- [pkg/detector/ospkg/alpine/alpine_test.go](pkg/detector/ospkg/alpine/alpine_test.go)
- [pkg/detector/ospkg/alpine/testdata/fixtures/alpine.yaml](pkg/detector/ospkg/alpine/testdata/fixtures/alpine.yaml)
- [pkg/detector/ospkg/amazon/amazon.go](pkg/detector/ospkg/amazon/amazon.go)
- [pkg/detector/ospkg/amazon/amazon_test.go](pkg/detector/ospkg/amazon/amazon_test.go)
- [pkg/detector/ospkg/debian/debian.go](pkg/detector/ospkg/debian/debian.go)
- [pkg/detector/ospkg/debian/debian_test.go](pkg/detector/ospkg/debian/debian_test.go)
- [pkg/detector/ospkg/detect_test.go](pkg/detector/ospkg/detect_test.go)
- [pkg/detector/ospkg/export_test.go](pkg/detector/ospkg/export_test.go)
- [pkg/detector/ospkg/oracle/oracle.go](pkg/detector/ospkg/oracle/oracle.go)
- [pkg/detector/ospkg/oracle/oracle_test.go](pkg/detector/ospkg/oracle/oracle_test.go)
- [pkg/detector/ospkg/oracle/testdata/fixtures/invalid-type.yaml](pkg/detector/ospkg/oracle/testdata/fixtures/invalid-type.yaml)
- [pkg/detector/ospkg/oracle/testdata/fixtures/oracle7.yaml](pkg/detector/ospkg/oracle/testdata/fixtures/oracle7.yaml)
- [pkg/detector/ospkg/photon/photon.go](pkg/detector/ospkg/photon/photon.go)
- [pkg/detector/ospkg/photon/photon_test.go](pkg/detector/ospkg/photon/photon_test.go)
- [pkg/detector/ospkg/photon/testdata/fixtures/data-source.yaml](pkg/detector/ospkg/photon/testdata/fixtures/data-source.yaml)
- [pkg/detector/ospkg/redhat/redhat.go](pkg/detector/ospkg/redhat/redhat.go)
- [pkg/detector/ospkg/redhat/redhat_test.go](pkg/detector/ospkg/redhat/redhat_test.go)
- [pkg/detector/ospkg/redhat/testdata/fixtures/redhat.yaml](pkg/detector/ospkg/redhat/testdata/fixtures/redhat.yaml)
- [pkg/detector/ospkg/suse/suse.go](pkg/detector/ospkg/suse/suse.go)
- [pkg/detector/ospkg/suse/suse_test.go](pkg/detector/ospkg/suse/suse_test.go)
- [pkg/detector/ospkg/ubuntu/ubuntu.go](pkg/detector/ospkg/ubuntu/ubuntu.go)
- [pkg/detector/ospkg/ubuntu/ubuntu_test.go](pkg/detector/ospkg/ubuntu/ubuntu_test.go)
- [pkg/fanal/analyzer/imgconf/apk/apk.go](pkg/fanal/analyzer/imgconf/apk/apk.go)
- [pkg/fanal/analyzer/imgconf/secret/secret.go](pkg/fanal/analyzer/imgconf/secret/secret.go)
- [pkg/fanal/analyzer/imgconf/secret/secret_test.go](pkg/fanal/analyzer/imgconf/secret/secret_test.go)
- [pkg/fanal/analyzer/language/analyze.go](pkg/fanal/analyzer/language/analyze.go)
- [pkg/fanal/analyzer/licensing/license.go](pkg/fanal/analyzer/licensing/license.go)
- [pkg/fanal/analyzer/pkg/dpkg/copyright.go](pkg/fanal/analyzer/pkg/dpkg/copyright.go)
- [pkg/fanal/analyzer/secret/secret.go](pkg/fanal/analyzer/secret/secret.go)
- [pkg/fanal/analyzer/secret/secret_test.go](pkg/fanal/analyzer/secret/secret_test.go)
- [pkg/fanal/secret/builtin-rules.go](pkg/fanal/secret/builtin-rules.go)
- [pkg/fanal/secret/scanner.go](pkg/fanal/secret/scanner.go)
- [pkg/fanal/secret/scanner_test.go](pkg/fanal/secret/scanner_test.go)
- [pkg/fanal/secret/testdata/alibaba-access-key-id.txt](pkg/fanal/secret/testdata/alibaba-access-key-id.txt)
- [pkg/fanal/secret/testdata/asymmetric-private-key.txt](pkg/fanal/secret/testdata/asymmetric-private-key.txt)
- [pkg/fanal/secret/testdata/aws-secrets.txt](pkg/fanal/secret/testdata/aws-secrets.txt)
- [pkg/fanal/secret/testdata/crlf-line-endings.txt](pkg/fanal/secret/testdata/crlf-line-endings.txt)
- [pkg/fanal/secret/testdata/github-token.txt](pkg/fanal/secret/testdata/github-token.txt)
- [pkg/fanal/secret/testdata/grafana-env.txt](pkg/fanal/secret/testdata/grafana-env.txt)
- [pkg/fanal/secret/testdata/hugging-face-secret.txt](pkg/fanal/secret/testdata/hugging-face-secret.txt)
- [pkg/fanal/secret/testdata/invalid-utf8.txt](pkg/fanal/secret/testdata/invalid-utf8.txt)
- [pkg/fanal/secret/testdata/jwt-secret.txt](pkg/fanal/secret/testdata/jwt-secret.txt)
- [pkg/fanal/secret/testdata/private-packagist.txt](pkg/fanal/secret/testdata/private-packagist.txt)
- [pkg/fanal/secret/testdata/symfony-secret.yaml](pkg/fanal/secret/testdata/symfony-secret.yaml)
- [pkg/iac/rego/build.go](pkg/iac/rego/build.go)
- [pkg/iac/rego/custom.go](pkg/iac/rego/custom.go)
- [pkg/iac/rego/embed.go](pkg/iac/rego/embed.go)
- [pkg/iac/rego/embed_test.go](pkg/iac/rego/embed_test.go)
- [pkg/iac/rego/load.go](pkg/iac/rego/load.go)
- [pkg/iac/rego/load_test.go](pkg/iac/rego/load_test.go)
- [pkg/iac/rego/metadata.go](pkg/iac/rego/metadata.go)
- [pkg/iac/rego/metadata_test.go](pkg/iac/rego/metadata_test.go)
- [pkg/iac/rego/options.go](pkg/iac/rego/options.go)
- [pkg/iac/rego/result.go](pkg/iac/rego/result.go)
- [pkg/iac/rego/runtime.go](pkg/iac/rego/runtime.go)
- [pkg/iac/rego/scanner.go](pkg/iac/rego/scanner.go)
- [pkg/iac/rego/scanner_test.go](pkg/iac/rego/scanner_test.go)
- [pkg/iac/rego/store.go](pkg/iac/rego/store.go)
- [pkg/iac/rego/store_test.go](pkg/iac/rego/store_test.go)
- [pkg/iac/scan/rule.go](pkg/iac/scan/rule.go)
- [pkg/iac/scanners/cloudformation/scanner_test.go](pkg/iac/scanners/cloudformation/scanner_test.go)
- [pkg/iac/scanners/dockerfile/scanner_test.go](pkg/iac/scanners/dockerfile/scanner_test.go)
- [pkg/iac/scanners/generic/scanner_test.go](pkg/iac/scanners/generic/scanner_test.go)
- [pkg/iac/scanners/terraform/scanner_test.go](pkg/iac/scanners/terraform/scanner_test.go)
- [pkg/iac/scanners/terraform/setup_test.go](pkg/iac/scanners/terraform/setup_test.go)
- [pkg/iac/scanners/terraformplan/snapshot/scanner_test.go](pkg/iac/scanners/terraformplan/snapshot/scanner_test.go)
- [pkg/licensing/classifier.go](pkg/licensing/classifier.go)
- [pkg/licensing/classifier_test.go](pkg/licensing/classifier_test.go)
- [pkg/licensing/expression/expression.go](pkg/licensing/expression/expression.go)
- [pkg/licensing/expression/expression_test.go](pkg/licensing/expression/expression_test.go)
- [pkg/licensing/expression/types.go](pkg/licensing/expression/types.go)
- [pkg/licensing/normalize.go](pkg/licensing/normalize.go)
- [pkg/licensing/normalize_test.go](pkg/licensing/normalize_test.go)
- [pkg/licensing/scanner.go](pkg/licensing/scanner.go)
- [pkg/licensing/scanner_test.go](pkg/licensing/scanner_test.go)
- [pkg/log/logger.go](pkg/log/logger.go)
- [pkg/misconf/scanner.go](pkg/misconf/scanner.go)
- [pkg/scan/ospkg/scan.go](pkg/scan/ospkg/scan.go)

</details>



This page describes Trivy's core scanning capabilities: vulnerability detection, misconfiguration scanning, secret detection, and license scanning. It covers how these scanners are orchestrated, configured, and integrated into the scanning pipeline.

For information about specific scan targets (container images, filesystems, etc.), see [Target Types and Scanning Workflows](#5).

## Overview

Trivy provides four specialized security scanners that can be enabled individually or in combination. The scanner selection is controlled via the `--scanners` flag or `scanners` configuration option, which accepts a comma-separated list of scanner types.

| Scanner Type | Purpose | Key Implementation |
|-------------|---------|-----------------|
| Vulnerability Scanner | Detects known CVEs in OS packages and application dependencies | `ospkg.Scanner`, `library.Driver` |
| Misconfiguration Scanner | Identifies security misconfigurations in IaC files and Kubernetes manifests | `misconf.Scanner`, `rego.Scanner` |
| Secret Scanner | Finds hardcoded secrets, API keys, and credentials | `secret.Scanner` |
| License Scanner | Detects and classifies software licenses | `licensing.Scanner` |

Sources: [pkg/misconf/scanner.go:99-104](), [pkg/fanal/secret/scanner.go:45-50](), [pkg/detector/ospkg/ubuntu/ubuntu.go:84-87]()

## Scanner Pipeline Architecture

All scanners are orchestrated through a unified pipeline. For a detailed breakdown of how vulnerability detection is implemented for different ecosystems, see [Vulnerability Detection](#4.1).

### Scanning Orchestration
The following diagram bridges the high-level scanning logic to the specific code entities responsible for execution.

```mermaid
graph TB
    subgraph "Scanner Orchestration"
        NewScanner["misconf.NewScanner()"]
        SecretScanner["secret.Scanner"]
        OSScanner["ospkg.Scanner"]
    end
    
    subgraph "Logic Implementation"
        ScanFS["Scanner.ScanFS()"]
        Detect["Scanner.Detect()"]
        FindLocations["Scanner.FindLocations()"]
    end
    
    subgraph "Data Sources"
        TrivyDB["trivy-db (BoltDB)"]
        RegoPolicies["Rego Policies (*.rego)"]
        SecretRules["builtinRules ([]Rule)"]
    end
    
    NewScanner --> ScanFS
    ScanFS --> RegoPolicies
    
    OSScanner --> Detect
    Detect --> TrivyDB
    
    SecretScanner --> FindLocations
    FindLocations --> SecretRules
```
**Figure 1: Mapping Scanning Logic to Code Entities**

Sources: [pkg/misconf/scanner.go:106-146](), [pkg/fanal/secret/scanner.go:130-154](), [pkg/detector/ospkg/ubuntu/ubuntu.go:103-155]()

## Vulnerability Detection

The vulnerability scanner detects known CVEs in OS packages (e.g., Ubuntu, Alpine, RHEL) and application dependencies (e.g., Maven, NPM, Pip).

Trivy uses specialized detectors for different OS families to handle specific advisory formats and versioning schemes:
- **Ubuntu**: Uses `ubuntu.VulnSrc` and handles ESM (Extended Security Maintenance) versions [pkg/detector/ospkg/ubuntu/ubuntu.go:84-100]().
- **Alpine**: Handles version streams including `edge` and handles repository-specific releases [pkg/detector/ospkg/alpine/alpine.go:70-85]().
- **Red Hat/CentOS**: Uses OVAL v2 data and handles modular namespaces and content sets [pkg/detector/ospkg/redhat/redhat.go:77-112]().
- **SUSE**: Supports Enterprise Linux, OpenSUSE, and Tumbleweed using CVRF data [pkg/detector/ospkg/suse/suse.go:93-118]().

For details on ecosystem-specific comparers and the driver system, see [Vulnerability Detection](#4.1).

Sources: [pkg/detector/ospkg/ubuntu/ubuntu.go:22-71](), [pkg/detector/ospkg/alpine/alpine.go:21-55](), [pkg/detector/ospkg/redhat/redhat.go:25-62](), [pkg/detector/ospkg/suse/suse.go:20-77]()

## Misconfiguration Scanning

The misconfiguration scanner analyzes Infrastructure-as-Code (IaC) files and Kubernetes manifests using Rego-based policies.

### Misconfiguration Scanner Architecture

```mermaid
graph TD
    subgraph "Scanner Initialization"
        NewScanner["misconf.NewScanner(detection.FileType, ScannerOption)"]
        ScannerOpts["misconf.ScannerOption"]
    end

    subgraph "Engine Components"
        RegoScanner["rego.Scanner"]
        Compiler["ast.Compiler"]
        Store["storage.Store"]
    end

    subgraph "Execution"
        Scan["Scanner.Scan(context.Context, fs.FS)"]
        ScanInput["rego.Scanner.ScanInput()"]
    end

    NewScanner --> RegoScanner
    RegoScanner --> Compiler
    RegoScanner --> Store
    Scan --> ScanInput
```
**Figure 2: Misconfiguration Scanning Code Flow**

The scanner supports multiple file types defined in `detection.FileType` including `Terraform`, `CloudFormation`, `Dockerfile`, `Kubernetes`, `Ansible`, and `Helm` [pkg/misconf/scanner.go:44-56](). It uses an OPA/Rego engine to evaluate policies against parsed configurations. For detail on Rego evaluation and policy bundles, see [Misconfiguration Scanning](#4.2).

Sources: [pkg/misconf/scanner.go:106-146](), [pkg/iac/rego/scanner.go:50-80](), [pkg/iac/rego/load.go:80-142]()

## Secret Detection

The secret scanner identifies sensitive information like API keys and passwords using regex patterns and keyword filtering.

Trivy includes a comprehensive set of `builtinRules` for various services:
- **Cloud Providers**: AWS Access Keys, Google Cloud API Keys [pkg/fanal/secret/builtin-rules.go:102-120]().
- **VCS**: GitHub PATs (Personal Access Tokens), GitLab tokens [pkg/fanal/secret/builtin-rules.go:122-156]().
- **Generic**: Asymmetric Private Keys, Slack Webhooks, etc [pkg/fanal/secret/builtin-rules.go:15-25]().

The scanner uses a `SecretGroupName` (often named "secret") to extract the specific sensitive part of a regex match [pkg/fanal/secret/scanner.go:156-176](). For details on how Trivy detects secrets and sensitive information, see [Secret Detection](#4.3).

Sources: [pkg/fanal/secret/builtin-rules.go:12-74](), [pkg/fanal/secret/scanner.go:116-128]()

## License Scanning and Classification

The license scanner identifies software licenses and classifies them based on their legal implications.

- **Normalization**: Trivy maps various license strings (e.g., "ASL-2.0", "APACHE-2") to standardized SPDX identifiers like `Apache-2.0` [pkg/licensing/normalize.go:17-66]().
- **Classification**: Licenses are categorized into groups such as `Forbidden`, `Restricted`, or `Permissive` to help organizations enforce compliance policies.

For details on license detection and SPDX identifier handling, see [License Scanning and Classification](#4.4).

Sources: [pkg/licensing/normalize.go:1-15]()

---

# Page: Vulnerability Detection

# Vulnerability Detection

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/guide/configuration/cache.md](docs/guide/configuration/cache.md)
- [docs/guide/coverage/os/photon.md](docs/guide/coverage/os/photon.md)
- [docs/guide/scanner/vulnerability.md](docs/guide/scanner/vulnerability.md)
- [integration/testdata/fixtures/db/data-source.yaml](integration/testdata/fixtures/db/data-source.yaml)
- [integration/testdata/fixtures/db/go.yaml](integration/testdata/fixtures/db/go.yaml)
- [integration/testdata/fixtures/db/oracle.yaml](integration/testdata/fixtures/db/oracle.yaml)
- [integration/testdata/fixtures/db/redhat.yaml](integration/testdata/fixtures/db/redhat.yaml)
- [pkg/commands/run.go](pkg/commands/run.go)
- [pkg/detector/library/driver.go](pkg/detector/library/driver.go)
- [pkg/detector/library/driver_test.go](pkg/detector/library/driver_test.go)
- [pkg/detector/library/testdata/fixtures/data-source.yaml](pkg/detector/library/testdata/fixtures/data-source.yaml)
- [pkg/detector/library/testdata/fixtures/go.yaml](pkg/detector/library/testdata/fixtures/go.yaml)
- [pkg/detector/ospkg/alma/alma.go](pkg/detector/ospkg/alma/alma.go)
- [pkg/detector/ospkg/alma/alma_test.go](pkg/detector/ospkg/alma/alma_test.go)
- [pkg/detector/ospkg/alma/testdata/fixtures/modular.yaml](pkg/detector/ospkg/alma/testdata/fixtures/modular.yaml)
- [pkg/detector/ospkg/alpine/alpine.go](pkg/detector/ospkg/alpine/alpine.go)
- [pkg/detector/ospkg/alpine/alpine_test.go](pkg/detector/ospkg/alpine/alpine_test.go)
- [pkg/detector/ospkg/alpine/testdata/fixtures/alpine.yaml](pkg/detector/ospkg/alpine/testdata/fixtures/alpine.yaml)
- [pkg/detector/ospkg/amazon/amazon.go](pkg/detector/ospkg/amazon/amazon.go)
- [pkg/detector/ospkg/amazon/amazon_test.go](pkg/detector/ospkg/amazon/amazon_test.go)
- [pkg/detector/ospkg/debian/debian.go](pkg/detector/ospkg/debian/debian.go)
- [pkg/detector/ospkg/debian/debian_test.go](pkg/detector/ospkg/debian/debian_test.go)
- [pkg/detector/ospkg/detect_test.go](pkg/detector/ospkg/detect_test.go)
- [pkg/detector/ospkg/export_test.go](pkg/detector/ospkg/export_test.go)
- [pkg/detector/ospkg/oracle/oracle.go](pkg/detector/ospkg/oracle/oracle.go)
- [pkg/detector/ospkg/oracle/oracle_test.go](pkg/detector/ospkg/oracle/oracle_test.go)
- [pkg/detector/ospkg/oracle/testdata/fixtures/invalid-type.yaml](pkg/detector/ospkg/oracle/testdata/fixtures/invalid-type.yaml)
- [pkg/detector/ospkg/oracle/testdata/fixtures/oracle7.yaml](pkg/detector/ospkg/oracle/testdata/fixtures/oracle7.yaml)
- [pkg/detector/ospkg/photon/photon.go](pkg/detector/ospkg/photon/photon.go)
- [pkg/detector/ospkg/photon/photon_test.go](pkg/detector/ospkg/photon/photon_test.go)
- [pkg/detector/ospkg/photon/testdata/fixtures/data-source.yaml](pkg/detector/ospkg/photon/testdata/fixtures/data-source.yaml)
- [pkg/detector/ospkg/redhat/redhat.go](pkg/detector/ospkg/redhat/redhat.go)
- [pkg/detector/ospkg/redhat/redhat_test.go](pkg/detector/ospkg/redhat/redhat_test.go)
- [pkg/detector/ospkg/redhat/testdata/fixtures/redhat.yaml](pkg/detector/ospkg/redhat/testdata/fixtures/redhat.yaml)
- [pkg/detector/ospkg/rocky/rocky.go](pkg/detector/ospkg/rocky/rocky.go)
- [pkg/detector/ospkg/rocky/rocky_test.go](pkg/detector/ospkg/rocky/rocky_test.go)
- [pkg/detector/ospkg/rocky/testdata/fixtures/modular.yaml](pkg/detector/ospkg/rocky/testdata/fixtures/modular.yaml)
- [pkg/detector/ospkg/rootio/export_test.go](pkg/detector/ospkg/rootio/export_test.go)
- [pkg/detector/ospkg/rootio/rootio.go](pkg/detector/ospkg/rootio/rootio.go)
- [pkg/detector/ospkg/rootio/rootio_test.go](pkg/detector/ospkg/rootio/rootio_test.go)
- [pkg/detector/ospkg/rootio/testdata/fixtures/data-source.yaml](pkg/detector/ospkg/rootio/testdata/fixtures/data-source.yaml)
- [pkg/detector/ospkg/rootio/testdata/fixtures/rootio.yaml](pkg/detector/ospkg/rootio/testdata/fixtures/rootio.yaml)
- [pkg/detector/ospkg/suse/suse.go](pkg/detector/ospkg/suse/suse.go)
- [pkg/detector/ospkg/suse/suse_test.go](pkg/detector/ospkg/suse/suse_test.go)
- [pkg/detector/ospkg/ubuntu/ubuntu.go](pkg/detector/ospkg/ubuntu/ubuntu.go)
- [pkg/detector/ospkg/ubuntu/ubuntu_test.go](pkg/detector/ospkg/ubuntu/ubuntu_test.go)
- [pkg/fanal/analyzer/all/import.go](pkg/fanal/analyzer/all/import.go)
- [pkg/fanal/analyzer/const.go](pkg/fanal/analyzer/const.go)
- [pkg/fanal/analyzer/language/conda/environment/environment.go](pkg/fanal/analyzer/language/conda/environment/environment.go)
- [pkg/fanal/image/daemon/context_unix_test.go](pkg/fanal/image/daemon/context_unix_test.go)
- [pkg/fanal/image/daemon/context_windows_test.go](pkg/fanal/image/daemon/context_windows_test.go)
- [pkg/fanal/image/daemon/export_test.go](pkg/fanal/image/daemon/export_test.go)
- [pkg/fanal/types/const.go](pkg/fanal/types/const.go)
- [pkg/fanal/types/misconf.go](pkg/fanal/types/misconf.go)
- [pkg/purl/purl.go](pkg/purl/purl.go)
- [pkg/purl/purl_test.go](pkg/purl/purl_test.go)
- [pkg/result/filter.go](pkg/result/filter.go)
- [pkg/result/filter_test.go](pkg/result/filter_test.go)
- [pkg/result/ignore.go](pkg/result/ignore.go)
- [pkg/result/ignore_test.go](pkg/result/ignore_test.go)
- [pkg/result/testdata/.trivyignore](pkg/result/testdata/.trivyignore)
- [pkg/result/testdata/.trivyignore.yaml](pkg/result/testdata/.trivyignore.yaml)
- [pkg/result/testdata/test-ignore-policy-licenses-and-secrets.rego](pkg/result/testdata/test-ignore-policy-licenses-and-secrets.rego)
- [pkg/scan/ospkg/scan.go](pkg/scan/ospkg/scan.go)
- [pkg/types/misconfiguration.go](pkg/types/misconfiguration.go)
- [pkg/types/vulnerability.go](pkg/types/vulnerability.go)
- [pkg/version/doc/doc.go](pkg/version/doc/doc.go)
- [pkg/version/doc/doc_test.go](pkg/version/doc/doc_test.go)
- [pkg/vulnerability/testdata/fixtures/vulnerability.yaml](pkg/vulnerability/testdata/fixtures/vulnerability.yaml)
- [pkg/vulnerability/vulnerability.go](pkg/vulnerability/vulnerability.go)
- [pkg/vulnerability/vulnerability_test.go](pkg/vulnerability/vulnerability_test.go)

</details>



## Purpose and Scope

This document explains how Trivy detects vulnerabilities in packages and libraries. The vulnerability detection system operates on two primary tracks: **library/application dependencies** (npm, pip, maven, etc.) and **OS-level packages** (apk, dpkg, rpm). This page focuses on the architecture and mechanisms for vulnerability detection, particularly the driver system, ecosystem-specific comparers, and the logic for filling vulnerability metadata.

For information about how packages are initially identified and extracted from artifacts, see [Artifact Analysis System](#3). For details on the vulnerability database management and updates, see [Database and Resource Management](#1.3).

## Architecture Overview

The vulnerability detection system consists of several key components that work together to identify security vulnerabilities:

**Vulnerability Detection Architecture**

```mermaid
graph TB
    subgraph "Input: Analyzed Packages"
        Packages["ftypes.Package<br/>Name, Version, Type"]
        PURL["PackageURL<br/>(PURL representation)"]
    end
    
    subgraph "Detection Dispatch"
        Scanner["scanner.local.Scanner"]
        Detector["Vulnerability Detector"]
    end
    
    subgraph "Library Detection (pkg/detector/library)"
        DriverFactory["library.NewDriver()"]
        Driver["library.Driver<br/>ecosystem + comparer"]
        DetectMethod["Driver.DetectVulnerabilities()"]
    end
    
    subgraph "OS Package Detection (pkg/detector/ospkg)"
        OSDetector["OS-specific Detectors<br/>(Ubuntu, Alpine, RedHat, etc.)"]
    end
    
    subgraph "Comparison Logic (pkg/detector/library/compare)"
        GenericComparer["compare.GenericComparer<br/>(semver)"]
        MavenComparer["maven.Comparer"]
        NpmComparer["npm.Comparer"]
        PEP440Comparer["pep440.Comparer"]
        RubyGemsComparer["rubygems.Comparer"]
        BitnamiComparer["bitnami.Comparer"]
    end
    
    subgraph "Metadata Enrichment (pkg/vulnerability)"
        VulnClient["vulnerability.Client"]
        FillInfo["FillInfo()"]
        SeverityLogic["Severity Selection Logic"]
    end
    
    subgraph "Database Layer (trivy-db)"
        DBConfig["db.Config"]
        Advisories["dbTypes.Advisory"]
        Vulnerabilities["dbTypes.Vulnerability"]
    end
    
    Packages --> Scanner
    Scanner --> Detector
    
    Detector --> DriverFactory
    DriverFactory --> Driver
    Driver --> DetectMethod
    
    Detector --> OSDetector
    
    DetectMethod --> DBConfig
    OSDetector --> DBConfig
    
    Driver --> GenericComparer
    Driver --> MavenComparer
    Driver --> NpmComparer
    
    DetectMethod --> VulnClient
    OSDetector --> VulnClient
    VulnClient --> FillInfo
    FillInfo --> Vulnerabilities
```

Sources: [pkg/detector/library/driver.go:1-105](), [pkg/vulnerability/vulnerability.go:54-61]()

## Library Detection Driver System

### Driver Architecture

The library detection system uses a factory pattern with ecosystem-specific drivers. The `NewDriver` function creates a `Driver` instance configured for a specific language ecosystem based on the `LangType`.

**Driver Creation and Ecosystem Mapping**

```mermaid
graph TB
    subgraph "Driver Factory (driver.go:26-98)"
        NewDriver["library.NewDriver(libType)"]
        Decision{"LangType?"}
    end
    
    subgraph "Ecosystem Assignment"
        RubyGems["ecosystem.RubyGems<br/>rubygems.Comparer"]
        Cargo["ecosystem.Cargo<br/>GenericComparer"]
        Composer["ecosystem.Composer<br/>GenericComparer"]
        Go["ecosystem.Go<br/>GenericComparer"]
        Maven["ecosystem.Maven<br/>maven.Comparer"]
        Npm["ecosystem.Npm<br/>npm.Comparer"]
        NuGet["ecosystem.NuGet<br/>GenericComparer"]
        Pip["ecosystem.Pip<br/>pep440.Comparer"]
        Pub["ecosystem.Pub<br/>GenericComparer"]
        K8s["ecosystem.Kubernetes<br/>GenericComparer"]
        Julia["ecosystem.Julia<br/>GenericComparer"]
        NotSupported["Log Warning<br/>Return (Driver{}, false)"]
    end
    
    subgraph "Driver Components"
        DriverStruct["Driver{<br/>  ecosystem: ecosystem.Type<br/>  comparer: compare.Comparer<br/>  dbc: db.Config<br/>}"]
    end
    
    NewDriver --> Decision
    
    Decision -->|"Bundler, GemSpec"| RubyGems
    Decision -->|"RustBinary, Cargo"| Cargo
    Decision -->|"Composer, ComposerVendor"| Composer
    Decision -->|"GoBinary, GoModule"| Go
    Decision -->|"Jar, Pom, Gradle, Sbt"| Maven
    Decision -->|"Npm, Yarn, Pnpm, Bun, NodePkg, JavaScript"| Npm
    Decision -->|"NuGet, DotNetCore, PackagesProps"| NuGet
    Decision -->|"Pipenv, Poetry, Pip, PythonPkg, Uv"| Pip
    Decision -->|"Pub"| Pub
    Decision -->|"K8sUpstream"| K8s
    Decision -->|"Julia"| Julia
    Decision -->|"CondaPkg, CondaEnv"| NotSupported
    
    RubyGems --> DriverStruct
    Cargo --> DriverStruct
    Composer --> DriverStruct
    Go --> DriverStruct
    Maven --> DriverStruct
    Npm --> DriverStruct
    NuGet --> DriverStruct
    Pip --> DriverStruct
    Pub --> DriverStruct
    K8s --> DriverStruct
    Julia --> DriverStruct
```

Sources: [pkg/detector/library/driver.go:26-98](), [pkg/fanal/types/const.go:93-137]()

### Version Comparison System

Each ecosystem uses a specific `compare.Comparer` implementation to determine if an installed package version is vulnerable according to advisory constraints.

| Language/Package Manager | Trivy LangType | DB Ecosystem | Comparer |
|--------------------------|----------------|--------------|----------|
| Ruby (Bundler, Gemspec) | `Bundler`, `GemSpec` | `rubygems` | `rubygems.Comparer` |
| Rust (Cargo) | `RustBinary`, `Cargo` | `cargo` | `GenericComparer` |
| PHP (Composer) | `Composer`, `ComposerVendor` | `composer` | `GenericComparer` |
| Go | `GoBinary`, `GoModule` | `go` | `GenericComparer` |
| Java/JVM | `Jar`, `Pom`, `Gradle`, `Sbt` | `maven` | `maven.Comparer` |
| JavaScript/Node.js | `Npm`, `Yarn`, `Pnpm`, `Bun`, `NodePkg`, `JavaScript` | `npm` | `npm.Comparer` |
| .NET | `NuGet`, `DotNetCore`, `PackagesProps` | `nuget` | `GenericComparer` |
| Python | `Pipenv`, `Poetry`, `Pip`, `PythonPkg`, `Uv` | `pip` | `pep440.Comparer` |
| Dart/Flutter | `Pub` | `pub` | `GenericComparer` |
| Elixir | `Hex` | `erlang` | `GenericComparer` |
| C/C++ (Conan) | `Conan` | `conan` | `GenericComparer` |
| Swift | `Swift` | `swift` | `GenericComparer` |
| CocoaPods | `Cocoapods` | `cocoapods` | `rubygems.Comparer` |
| Bitnami | `Bitnami` | `bitnami` | `bitnami.Comparer` |
| Kubernetes | `K8sUpstream` | `kubernetes` | `GenericComparer` |
| Julia | `Julia` | `julia` | `GenericComparer` |

Sources: [pkg/detector/library/driver.go:30-92]()

## OS Package Detection

OS detection is handled by distribution-specific scanners that implement a common `Detect` method.

### Distribution Scanners

#### Ubuntu
The Ubuntu scanner uses `eolDates` to verify if a version is still supported and maps `ESM` (Extended Security Maintenance) versions back to base versions if they are not yet outdated [pkg/detector/ospkg/ubuntu/ubuntu.go:22-71, 164-179](). It retrieves advisories using `PkgName: pkg.SrcName` [pkg/detector/ospkg/ubuntu/ubuntu.go:110-113]().

#### Alpine
The Alpine scanner prefers the repository release over the OS version when they differ [pkg/detector/ospkg/alpine/alpine.go:78-85](). It handles both fixed and unfixed vulnerabilities (though the public Trivy DB primarily contains fixed advisories to reduce false positives) [pkg/detector/ospkg/alpine/alpine.go:127-160]().

#### Red Hat / CentOS
The Red Hat scanner cleans "content sets" from generic build suffixes (e.g., `repo__8` -> `repo`) before querying advisories [pkg/detector/ospkg/redhat/redhat.go:107, 193-207](). It also handles modular package namespaces [pkg/detector/ospkg/redhat/redhat.go:175-187]().

#### SUSE
The SUSE scanner handles SLES, SLE Micro, and openSUSE (including rolling release Tumbleweed) [pkg/detector/ospkg/suse/suse.go:82-90]().

Sources: [pkg/detector/ospkg/ubuntu/ubuntu.go:103-155](), [pkg/detector/ospkg/alpine/alpine.go:70-125](), [pkg/detector/ospkg/redhat/redhat.go:77-163](), [pkg/detector/ospkg/suse/suse.go:121-156]()

## Metadata Enrichment (FillInfo)

After initial detection, Trivy enriches the results with detailed vulnerability information from the database using `vulnerability.Client.FillInfo` [pkg/vulnerability/vulnerability.go:64-124]().

### Severity Selection Logic

Trivy follows a prioritized logic to determine which severity to display when multiple sources provide conflicting data.

**Severity Auto-Detection Flow**

```mermaid
graph TD
    Start["FillInfo() calls getSeverity()"]
    CheckSource["Is source 'auto'?"]
    
    subgraph "Auto-Detection Strategy (autoDetectSeverity)"
        TargetSource["1. Use Severity from Target Data Source<br/>(e.g. Red Hat for RHEL)"]
        GHSACheck["2. If GHSA-ID, check GitHub Advisory DB"]
        NVDCheck["3. Fallback to NVD"]
        OtherCheck["4. Fallback to other vendors<br/>(with warning)"]
        Unknown["5. Return SeverityUnknown"]
    end
    
    Start --> CheckSource
    CheckSource -->|Yes| TargetSource
    TargetSource -->|Found| Return
    TargetSource -->|Not Found| GHSACheck
    GHSACheck -->|Found| Return
    GHSACheck -->|Not Found| NVDCheck
    NVDCheck -->|Found| Return
    NVDCheck -->|Not Found| OtherCheck
    OtherCheck -->|Found| Return
    OtherCheck -->|Not Found| Unknown
```

Sources: [pkg/vulnerability/vulnerability.go:126-171]()

### Primary URL Determination

Trivy identifies a "Primary URL" for each vulnerability based on the ID prefix or the data source [pkg/vulnerability/vulnerability.go:173-194]().

| ID Prefix | Primary URL Source |
|-----------|--------------------|
| `CVE-` | Aqua Vulnerability Database (AVD) |
| `RUSTSEC-` | OSV.dev |
| `GHSA-` | GitHub Advisories |
| `TEMP-` | Debian Security Tracker |

Sources: [pkg/vulnerability/vulnerability.go:173-194]()

## Package URL (PURL) Integration

Trivy uses PURLs to standardize package identification across different ecosystems. This is critical for vulnerability matching and SBOM generation.

**PURL Code Entity Mapping**

```mermaid
graph LR
    subgraph "Code Entities"
        PURLType["purl.PackageURL (pkg/purl/purl.go)"]
        NewPURL["purl.New()"]
        LangType["purl.LangType()"]
        Class["purl.Class()"]
    end

    subgraph "Ecosystem Mapping"
        RPM["packageurl.TypeRPM"]
        Debian["packageurl.TypeDebian"]
        Maven["packageurl.TypeMaven"]
        Golang["packageurl.TypeGolang"]
        NPM["packageurl.TypeNPM"]
    end

    NewPURL --> RPM
    NewPURL --> Debian
    NewPURL --> Maven
    NewPURL --> Golang
    NewPURL --> NPM

    LangType --> Jar["ftypes.Jar"]
    LangType --> Go["ftypes.GoBinary"]
    LangType --> Node["ftypes.NodePkg"]
    
    Class --> OSPkg["types.ClassOSPkg"]
    Class --> LangPkg["types.ClassLangPkg"]
```

Sources: [pkg/purl/purl.go:67-135](), [pkg/purl/purl.go:150-199](), [pkg/purl/purl.go:201-213]()

## Filtering Results

Vulnerabilities can be filtered out post-detection based on user configuration, including severities, statuses, and ignore files.

- **Status Filtering**: Filters by `FixedVersion` (Fixed) or `Affected` [pkg/vulnerability/vulnerability.go:70-74]().
- **Ignore Files**: Uses `.trivyignore` or VEX (Vulnerability Exploitability eXchange) documents to suppress specific findings [pkg/result/filter.go:22-60]().
- **Duplicate Handling**: If a vulnerability is detected multiple times (e.g., in different layers or via different paths), `filterVulnerabilities` ensures only the most relevant instance is kept based on a unique key: `VulnerabilityID/PkgID/PkgName/InstalledVersion/PkgPath` [pkg/result/filter.go:107-111]().

Sources: [pkg/result/filter.go:83-119]()

---

# Page: Misconfiguration Scanning

# Misconfiguration Scanning

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/guide/coverage/iac/ansible.md](docs/guide/coverage/iac/ansible.md)
- [docs/guide/coverage/iac/index.md](docs/guide/coverage/iac/index.md)
- [internal/testutil/error.go](internal/testutil/error.go)
- [pkg/dependency/parser/c/conan/parse.go](pkg/dependency/parser/c/conan/parse.go)
- [pkg/fanal/analyzer/config/all/import.go](pkg/fanal/analyzer/config/all/import.go)
- [pkg/fanal/analyzer/config/azurearm/azurearm.go](pkg/fanal/analyzer/config/azurearm/azurearm.go)
- [pkg/fanal/analyzer/config/azurearm/azurearm_test.go](pkg/fanal/analyzer/config/azurearm/azurearm_test.go)
- [pkg/fanal/analyzer/config/cloudformation/cloudformation.go](pkg/fanal/analyzer/config/cloudformation/cloudformation.go)
- [pkg/fanal/analyzer/config/k8s/k8s.go](pkg/fanal/analyzer/config/k8s/k8s.go)
- [pkg/iac/adapters/arm/appservice/adapt.go](pkg/iac/adapters/arm/appservice/adapt.go)
- [pkg/iac/adapters/arm/appservice/adapt_test.go](pkg/iac/adapters/arm/appservice/adapt_test.go)
- [pkg/iac/adapters/terraform/azure/appservice/adapt.go](pkg/iac/adapters/terraform/azure/appservice/adapt.go)
- [pkg/iac/adapters/terraform/azure/appservice/adapt_test.go](pkg/iac/adapters/terraform/azure/appservice/adapt_test.go)
- [pkg/iac/adapters/terraform/azure/container/adapt.go](pkg/iac/adapters/terraform/azure/container/adapt.go)
- [pkg/iac/adapters/terraform/azure/container/adapt_test.go](pkg/iac/adapters/terraform/azure/container/adapt_test.go)
- [pkg/iac/detection/detect.go](pkg/iac/detection/detect.go)
- [pkg/iac/detection/detect_test.go](pkg/iac/detection/detect_test.go)
- [pkg/iac/providers/azure/appservice/appservice.go](pkg/iac/providers/azure/appservice/appservice.go)
- [pkg/iac/providers/azure/container/container.go](pkg/iac/providers/azure/container/container.go)
- [pkg/iac/rego/build.go](pkg/iac/rego/build.go)
- [pkg/iac/rego/custom.go](pkg/iac/rego/custom.go)
- [pkg/iac/rego/embed.go](pkg/iac/rego/embed.go)
- [pkg/iac/rego/embed_test.go](pkg/iac/rego/embed_test.go)
- [pkg/iac/rego/load.go](pkg/iac/rego/load.go)
- [pkg/iac/rego/load_test.go](pkg/iac/rego/load_test.go)
- [pkg/iac/rego/metadata.go](pkg/iac/rego/metadata.go)
- [pkg/iac/rego/metadata_test.go](pkg/iac/rego/metadata_test.go)
- [pkg/iac/rego/options.go](pkg/iac/rego/options.go)
- [pkg/iac/rego/result.go](pkg/iac/rego/result.go)
- [pkg/iac/rego/runtime.go](pkg/iac/rego/runtime.go)
- [pkg/iac/rego/scanner.go](pkg/iac/rego/scanner.go)
- [pkg/iac/rego/scanner_test.go](pkg/iac/rego/scanner_test.go)
- [pkg/iac/rego/schemas/cloud.json](pkg/iac/rego/schemas/cloud.json)
- [pkg/iac/scan/rule.go](pkg/iac/scan/rule.go)
- [pkg/iac/scanners/azure/arm/parser/parser.go](pkg/iac/scanners/azure/arm/parser/parser.go)
- [pkg/iac/scanners/azure/arm/parser/parser_test.go](pkg/iac/scanners/azure/arm/parser/parser_test.go)
- [pkg/iac/scanners/azure/arm/parser/template.go](pkg/iac/scanners/azure/arm/parser/template.go)
- [pkg/iac/scanners/azure/arm/parser/template_test.go](pkg/iac/scanners/azure/arm/parser/template_test.go)
- [pkg/iac/scanners/azure/value.go](pkg/iac/scanners/azure/value.go)
- [pkg/iac/scanners/azure/value_test.go](pkg/iac/scanners/azure/value_test.go)
- [pkg/iac/scanners/cloudformation/scanner_test.go](pkg/iac/scanners/cloudformation/scanner_test.go)
- [pkg/iac/scanners/dockerfile/scanner_test.go](pkg/iac/scanners/dockerfile/scanner_test.go)
- [pkg/iac/scanners/generic/scanner_test.go](pkg/iac/scanners/generic/scanner_test.go)
- [pkg/iac/scanners/terraform/scanner_test.go](pkg/iac/scanners/terraform/scanner_test.go)
- [pkg/iac/scanners/terraform/setup_test.go](pkg/iac/scanners/terraform/setup_test.go)
- [pkg/iac/scanners/terraformplan/snapshot/scanner_test.go](pkg/iac/scanners/terraformplan/snapshot/scanner_test.go)
- [pkg/mapfs/file.go](pkg/mapfs/file.go)
- [pkg/mapfs/fs.go](pkg/mapfs/fs.go)
- [pkg/mapfs/fs_test.go](pkg/mapfs/fs_test.go)
- [pkg/mapfs/testdata/subdir/..foo.txt](pkg/mapfs/testdata/subdir/..foo.txt)
- [pkg/mapfs/testdata/subdir/foo.txt](pkg/mapfs/testdata/subdir/foo.txt)
- [pkg/misconf/scanner.go](pkg/misconf/scanner.go)
- [pkg/misconf/scanner_test.go](pkg/misconf/scanner_test.go)
- [pkg/module/memfs.go](pkg/module/memfs.go)
- [pkg/module/memfs_test.go](pkg/module/memfs_test.go)
- [pkg/x/json/json.go](pkg/x/json/json.go)
- [pkg/x/json/json_test.go](pkg/x/json/json_test.go)

</details>



## Purpose and Scope

This document details Trivy's misconfiguration scanning system, which detects security issues and policy violations in Infrastructure as Code (IaC) configurations. The system parses configuration files (Terraform, CloudFormation, Kubernetes YAML, Helm, Ansible, etc.), evaluates them with user-provided values, and applies Rego-based policies to identify misconfigurations.

The misconfiguration scanner is built on a modular architecture where specific scanners for different technologies (e.g., Terraform, Dockerfile) are orchestrated by a central `Scanner` that manages filesystem filtering and results aggregation.

Sources: [pkg/misconf/scanner.go:1-56](), [pkg/iac/rego/scanner.go:50-80]()

---

## Core Scanning Architecture

The misconfiguration scanning process follows a pipeline from file detection to policy evaluation.

```mermaid
graph TD
    subgraph "Orchestration [pkg/misconf]"
        NewScanner["NewScanner(FileType, ScannerOption)"]
        ScanFS["Scanner.Scan(ctx, fs.FS)"]
        FilterFS["filterFS(fsys)"]
    end

    subgraph "Technology Scanners [pkg/iac/scanners]"
        TF["terraform.New()"]
        K8s["kubernetes.NewScanner()"]
        DF["dockerfile.NewScanner()"]
        Helm["helm.New()"]
        CF["cloudformation.New()"]
    end

    subgraph "Policy Engine [pkg/iac/rego]"
        RegoScanner["rego.NewScanner()"]
        LoadPolicies["LoadPolicies(srcFS)"]
        ScanInput["ScanInput(sourceType, inputs)"]
        OPA["Open Policy Agent (OPA)"]
    end

    NewScanner --> TF
    NewScanner --> K8s
    ScanFS --> FilterFS
    FilterFS --> TF
    TF --> RegoScanner
    RegoScanner --> LoadPolicies
    LoadPolicies --> OPA
    ScanInput --> OPA
```

**Misconfiguration Scanning Pipeline**: Orchestration of technology-specific scanners and the Rego engine.

Sources: [pkg/misconf/scanner.go:106-146](), [pkg/misconf/scanner.go:148-180](), [pkg/iac/rego/scanner.go:101-124]()

### File Detection and Filtering
Trivy uses a detection system to identify relevant files before passing them to specific scanners. The `filterFS` function uses `detection.IsType` to ensure only files matching the expected `FileType` are processed.

| FileType | Detection Logic | Code Reference |
| :--- | :--- | :--- |
| `terraform` | Matches `.tf`, `.tf.json`, `.tfvars` | [pkg/iac/detection/detect.go:100-102]() |
| `cloudformation` | Sniffs for `Resources` key in YAML/JSON | [pkg/iac/detection/detect.go:131-156]() |
| `dockerfile` | Matches `Dockerfile`, `Containerfile` or `.Dockerfile` ext | [pkg/iac/detection/detect.go:203-216]() |
| `kubernetes` | Checks for `apiVersion`, `kind`, `metadata` | [pkg/iac/detection/detect.go:218-282]() |
| `azure-arm` | Validates `$schema` prefix and `resources` | [pkg/iac/detection/detect.go:158-201]() |

Sources: [pkg/iac/detection/detect.go:39-52](), [pkg/misconf/scanner.go:182-225]()

---

## Rego Policy Engine

The heart of the misconfiguration system is the Rego scanner, which evaluates parsed configuration data against OPA policies.

### Policy Loading and Compilation
The `rego.Scanner` loads policies from multiple sources, including embedded policies (from `aquasecurity/trivy-checks`), local directories, and OPA bundles.

```mermaid
graph LR
    subgraph "Loading Logic [pkg/iac/rego/load.go]"
        LoadEmb["loadEmbedded()"]
        LoadDirs["LoadPoliciesFromDirs()"]
        Compile["compilePolicies()"]
    end

    subgraph "Embedded Assets"
        Checks["trivy-checks/EmbeddedPolicyFileSystem"]
        Libs["trivy-checks/EmbeddedLibraryFileSystem"]
    end

    LoadEmb --> Checks
    LoadEmb --> Libs
    LoadDirs --> Compile
    Compile --> SchemaSet["BuildSchemaSetFromPolicies"]
    SchemaSet --> OPAComp["ast.Compiler"]
```

**Policy Loading Workflow**: How Rego modules are gathered and prepared for evaluation.

Sources: [pkg/iac/rego/load.go:62-78](), [pkg/iac/rego/load.go:80-142](), [pkg/iac/rego/embed.go:71-77]()

### Metadata and Annotations
Trivy uses OPA annotations to define rule metadata (ID, Title, Severity). The `StaticMetadata` struct captures these attributes from Rego `# METADATA` blocks.

| Attribute | Description | Code Reference |
| :--- | :--- | :--- |
| `id` | Unique check identifier (e.g., AVD-AWS-0001) | [pkg/iac/rego/metadata.go:76]() |
| `severity` | Critical, High, Medium, Low | [pkg/iac/rego/metadata.go:99-101]() |
| `frameworks` | Mapping to compliance frameworks (CIS, NSA) | [pkg/iac/rego/metadata.go:143-173]() |
| `input` | Selectors to filter which checks apply to which data | [pkg/iac/rego/metadata.go:253-270]() |

Sources: [pkg/iac/rego/metadata.go:25-49](), [pkg/iac/rego/metadata.go:196-218]()

---

## Data Flow: Configuration to Rego Input

Configuration data is adapted into a standard JSON structure before being passed to OPA as `input`.

### Cloud Provider Schema
For cloud-based IaC (Terraform, CloudFormation), Trivy maps resources to a unified provider schema defined in `cloud.json`.

```mermaid
classDiagram
    class Input {
        +String Path
        +Object Contents
        +ast.Value parsed
    }
    class CloudSchema {
        +AWS aws
        +Azure azure
        +Google google
        +Kubernetes kubernetes
    }
    class AWS {
        +S3 s3
        +EC2 ec2
        +Lambda lambda
    }
    Input --> CloudSchema : Adapted To
    CloudSchema --> AWS
```

**Data Adaptation**: Mapping heterogeneous IaC formats to a unified Rego input schema.

Sources: [pkg/iac/rego/schemas/cloud.json:1-44](), [pkg/iac/rego/scanner.go:164-171]()

### Rule Evaluation Process
The `ScanInput` function iterates through loaded policies and applies rules to the provided inputs.

1.  **Filter**: Checks if the policy is applicable to the `sourceType` and `input` using metadata selectors [pkg/iac/rego/scanner.go:226-228]().
2.  **Query**: Executes Rego queries (usually `deny` or `allow`) [pkg/iac/rego/scanner.go:239-251]().
3.  **Result Embellishment**: Combines OPA output with static metadata to create `scan.Results` [pkg/iac/rego/scanner.go:250]().

Sources: [pkg/iac/rego/scanner.go:181-257]()

---

## Advanced Rego Features

### Schema Validation
Trivy supports type-checking Rego policies using JSON schemas. This prevents policies from referencing non-existent fields in the input data.

Sources: [pkg/iac/rego/load.go:247-255](), [pkg/iac/rego/load_test.go:55-71]()

### Runtime Values
The scanner provides runtime information to Rego policies via `opa.runtime()`, including environment variables prefixed with `DEFSEC_`.

Sources: [pkg/iac/rego/scanner.go:134](), [pkg/iac/rego/scanner_test.go:159-184]()

### Fallback Mechanism
If a user-provided policy fails to compile (e.g., due to syntax changes in newer OPA versions), Trivy can fallback to an embedded version of the check if the namespace or ID matches.

Sources: [pkg/iac/rego/load.go:144-190](), [pkg/iac/rego/load_test.go:112-134]()

---

## Implementation Details: Technology Specifics

### Terraform Scanning
Terraform scanning involves complex HCL evaluation before Rego analysis.
- **Plan Scanning**: Supports both JSON plan files (`terraformplan-json`) and binary snapshots (`terraformplan-snapshot`).
- **Module Support**: Resolves and evaluates remote and local modules.

Sources: [pkg/iac/detection/detect.go:104-129](), [pkg/iac/scanners/terraform/scanner_test.go:19-52]()

### Kubernetes and Helm
- **Helm**: Renders templates using provided value files before scanning the resulting manifests.
- **RBAC**: Specialized detection for Role-Based Access Control misconfigurations.

Sources: [pkg/iac/detection/detect.go:78-93](), [pkg/iac/detection/detect.go:218-282]()

### Misconfiguration Results Structure
Results are categorized into `Successes`, `Warnings`, and `Failures`.

```go
type Misconfiguration struct {
    FileType   ConfigType
    Scanner    string
    Successes  MisconfResults
    Warnings   MisconfResults
    Failures   MisconfResults
}
```

Sources: [pkg/misconf/scanner.go:169-177](), [pkg/iac/rego/result.go:1-20]()

---

# Page: Secret Detection

# Secret Detection

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [pkg/fanal/analyzer/imgconf/secret/secret.go](pkg/fanal/analyzer/imgconf/secret/secret.go)
- [pkg/fanal/analyzer/imgconf/secret/secret_test.go](pkg/fanal/analyzer/imgconf/secret/secret_test.go)
- [pkg/fanal/analyzer/secret/secret.go](pkg/fanal/analyzer/secret/secret.go)
- [pkg/fanal/analyzer/secret/secret_test.go](pkg/fanal/analyzer/secret/secret_test.go)
- [pkg/fanal/secret/builtin-rules.go](pkg/fanal/secret/builtin-rules.go)
- [pkg/fanal/secret/scanner.go](pkg/fanal/secret/scanner.go)
- [pkg/fanal/secret/scanner_test.go](pkg/fanal/secret/scanner_test.go)
- [pkg/fanal/secret/testdata/alibaba-access-key-id.txt](pkg/fanal/secret/testdata/alibaba-access-key-id.txt)
- [pkg/fanal/secret/testdata/asymmetric-private-key.txt](pkg/fanal/secret/testdata/asymmetric-private-key.txt)
- [pkg/fanal/secret/testdata/aws-secrets.txt](pkg/fanal/secret/testdata/aws-secrets.txt)
- [pkg/fanal/secret/testdata/crlf-line-endings.txt](pkg/fanal/secret/testdata/crlf-line-endings.txt)
- [pkg/fanal/secret/testdata/github-token.txt](pkg/fanal/secret/testdata/github-token.txt)
- [pkg/fanal/secret/testdata/grafana-env.txt](pkg/fanal/secret/testdata/grafana-env.txt)
- [pkg/fanal/secret/testdata/hugging-face-secret.txt](pkg/fanal/secret/testdata/hugging-face-secret.txt)
- [pkg/fanal/secret/testdata/invalid-utf8.txt](pkg/fanal/secret/testdata/invalid-utf8.txt)
- [pkg/fanal/secret/testdata/jwt-secret.txt](pkg/fanal/secret/testdata/jwt-secret.txt)
- [pkg/fanal/secret/testdata/private-packagist.txt](pkg/fanal/secret/testdata/private-packagist.txt)
- [pkg/fanal/secret/testdata/symfony-secret.yaml](pkg/fanal/secret/testdata/symfony-secret.yaml)
- [pkg/fanal/types/misconf.go](pkg/fanal/types/misconf.go)
- [pkg/result/filter.go](pkg/result/filter.go)
- [pkg/result/filter_test.go](pkg/result/filter_test.go)
- [pkg/result/ignore.go](pkg/result/ignore.go)
- [pkg/result/ignore_test.go](pkg/result/ignore_test.go)
- [pkg/result/testdata/.trivyignore](pkg/result/testdata/.trivyignore)
- [pkg/result/testdata/.trivyignore.yaml](pkg/result/testdata/.trivyignore.yaml)
- [pkg/result/testdata/test-ignore-policy-licenses-and-secrets.rego](pkg/result/testdata/test-ignore-policy-licenses-and-secrets.rego)
- [pkg/types/misconfiguration.go](pkg/types/misconfiguration.go)
- [pkg/types/vulnerability.go](pkg/types/vulnerability.go)

</details>



This page explains Trivy's secret detection system, which identifies sensitive information and credentials embedded in code, configuration files, and container images. Secret detection uses pattern-based matching to find API keys, passwords, tokens, private keys, and other sensitive data.

For vulnerability detection, see [4.1](). For misconfiguration scanning, see [4.2](). For license scanning, see [4.4]().

## Overview

Secret detection in Trivy is implemented as a specialized analyzer within the `fanal` library. It operates during the artifact analysis phase by scanning file contents against a set of rules defined by regular expressions and keywords. Unlike vulnerability detection, secret scanning is entirely signature-based and does not require an external vulnerability database.

The system supports:
- **Built-in Rules**: Over 70 categories of secrets including AWS, GitHub, Slack, and Stripe [pkg/fanal/secret/builtin-rules.go:11-74]().
- **Custom Rules**: User-defined patterns via configuration files [pkg/fanal/secret/scanner.go:63]().
- **Allow Rules**: Mechanisms to whitelist specific patterns or file paths [pkg/fanal/secret/scanner.go:224-231]().
- **Binary Filtering**: Intelligent skipping of non-text files while allowing specific binary formats like `.pyc` [pkg/fanal/analyzer/secret/secret.go:41-60]().

Sources: [pkg/fanal/secret/builtin-rules.go:11-100](), [pkg/fanal/analyzer/secret/secret.go:102-143]()

## Secret Detection Architecture

The following diagram maps the natural language concepts of "Scanning" and "Detection" to the specific code entities in the `pkg/fanal/secret` and `pkg/fanal/analyzer/secret` packages.

### Code Entity Map: Detection Pipeline

```mermaid
graph TD
    subgraph "Analysis Layer [pkg/fanal/analyzer/secret]"
        SA["SecretAnalyzer (struct)<br/>secret.go:73"]
        SA_Init["Init()<br/>secret.go:86"]
        SA_Analyze["Analyze()<br/>secret.go:102"]
        SA_Req["Required()<br/>secret.go:145"]
    end

    subgraph "Core Engine [pkg/fanal/secret]"
        Scanner["Scanner (struct)<br/>scanner.go:45"]
        S_Scan["Scan()<br/>scanner.go:303"]
        S_FL["FindLocations()<br/>scanner.go:130"]
        Rules["Rule (struct)<br/>scanner.go:116"]
        Builtin["builtinRules (var)<br/>builtin-rules.go:102"]
    end

    subgraph "Data Structures [pkg/fanal/types]"
        SecretFinding["SecretFinding (struct)<br/>pkg/fanal/types/secret.go"]
        Secret["Secret (struct)<br/>pkg/fanal/types/secret.go"]
    end

    SA_Init -->|Parses Config| Scanner
    SA_Analyze -->|Calls| S_Scan
    S_Scan -->|Iterates| Rules
    Rules -->|Uses| Builtin
    S_Scan -->|Executes| S_FL
    S_FL -->|Produces| SecretFinding
    SA_Analyze -->|Returns| Secret
```

Sources: [pkg/fanal/analyzer/secret/secret.go:73-143](), [pkg/fanal/secret/scanner.go:45-154](), [pkg/fanal/secret/builtin-rules.go:102]()

## Implementation Details

### The Scanning Engine
The `Scanner` struct [pkg/fanal/secret/scanner.go:45]() is the heart of the detection logic. It processes content in chunks to balance memory usage and performance.

- **Buffering**: Uses a `DefaultBufferSize` of 64KB [pkg/fanal/secret/scanner.go:36]().
- **Overlap**: Implements a `DefaultOverlap` of 4KB [pkg/fanal/secret/scanner.go:42]() to ensure secrets spanning across buffer boundaries (like long RSA keys) are not missed.
- **Keyword Pre-filtering**: To optimize performance, rules can define `Keywords` [pkg/fanal/secret/scanner.go:122](). The scanner first checks if a line contains these keywords before executing expensive regex matching [pkg/fanal/secret/scanner.go:202-214]().

### Rule Definition
A `Rule` [pkg/fanal/secret/scanner.go:116]() consists of:
- **Regex**: The pattern to match.
- **SecretGroupName**: If the regex contains multiple capture groups, this specifies which group contains the actual secret [pkg/fanal/secret/scanner.go:126]().
- **Severity**: The impact level (e.g., CRITICAL, HIGH).
- **AllowRules**: Rule-specific exclusions [pkg/fanal/secret/scanner.go:124]().

### Built-in Rules Examples
| ID | Category | Keywords | Regex Source |
|----|----------|----------|--------------|
| `aws-access-key-id` | AWS | `AKIA`, `AGPA`, etc. | [pkg/fanal/secret/builtin-rules.go:104-111]() |
| `github-pat` | GitHub | `ghp_` | [pkg/fanal/secret/builtin-rules.go:122-129]() |
| `slack-access-token` | Slack | `xoxp-` | [pkg/fanal/secret/builtin-rules.go:245-252]() |

Sources: [pkg/fanal/secret/scanner.go:31-43](), [pkg/fanal/secret/scanner.go:116-128](), [pkg/fanal/secret/builtin-rules.go:102-252]()

## Analysis Workflow

The `SecretAnalyzer` determines which files to scan and how to handle their content.

```mermaid
sequenceDiagram
    participant W as Walker
    participant SA as SecretAnalyzer
    participant U as Utils (IsBinary)
    participant S as Scanner

    W->>SA: Required(filePath)
    Note over SA: Checks skipDirs (.git, node_modules)<br/>Checks skipFiles (lockfiles)<br/>Checks skipExts (.jpg, .pdf, .zip)
    SA-->>W: true/false

    W->>SA: Analyze(ctx, input)
    SA->>U: IsBinary(content)
    alt is binary and not .pyc
        SA-->>W: skip
    else is text or allowed binary
        SA->>S: Scan(ScanArgs)
        S->>S: Match Rules & Keywords
        S-->>SA: SecretFindings
    end
    SA-->>W: AnalysisResult
```

### File Filtering Logic
The `Required()` function [pkg/fanal/analyzer/secret/secret.go:145]() optimizes the scan by skipping:
- **Small files**: Files smaller than 10 bytes [pkg/fanal/analyzer/secret/secret.go:147]().
- **Dependency lockfiles**: `go.sum`, `package-lock.json`, etc. [pkg/fanal/analyzer/secret/secret.go:28-36]().
- **SCM directories**: `.git` [pkg/fanal/analyzer/secret/secret.go:38]().
- **Media/Binaries**: `.jpg`, `.pdf`, `.zip`, `.deb` [pkg/fanal/analyzer/secret/secret.go:41-56]().

Sources: [pkg/fanal/analyzer/secret/secret.go:28-61](), [pkg/fanal/analyzer/secret/secret.go:145-183]()

## Result Filtering and Exclusions

Once secrets are detected, they pass through a filtering layer in `pkg/result/filter.go`.

### Global and Local Ignores
1. **.trivyignore**: Users can suppress specific findings by Rule ID [pkg/result/filter.go:165-174]().
2. **Inline Allow Rules**: The `Scanner` config allows defining `AllowRules` based on regex or path [pkg/fanal/secret/scanner.go:224-231]().
3. **Exclude Blocks**: Allows excluding specific blocks of text from scanning [pkg/fanal/secret/scanner.go:251-254]().

### Filtering Logic
The `filterSecrets` function [pkg/result/filter.go:159]() performs the following:
- **Severity Filtering**: Removes findings that don't match the user-requested severity levels [pkg/result/filter.go:162-164]().
- **Ignore File Matching**: Checks findings against `.trivyignore` entries [pkg/result/filter.go:165-170]().

Sources: [pkg/result/filter.go:159-174](), [pkg/fanal/secret/scanner.go:224-254](), [pkg/result/ignore.go:143-150]()

## Configuration

Secret scanning can be customized via a YAML configuration file.

```yaml
# Example Secret Config
enable-builtin-rules:
  - aws-access-key-id
disable-rules:
  - generic-unwanted-rule
rules:
  - id: custom-api-key
    title: My Custom API Key
    regex: 'my-key-[a-z0-9]{32}'
    severity: CRITICAL
allow-rules:
  - id: sample-data
    regex: 'AKIAEXAMPLE123456789'
```

The `Config` struct [pkg/fanal/secret/scanner.go:52-66]() maps these fields:
- `EnableBuiltinRuleIDs`: Whitelist of built-in rules [pkg/fanal/secret/scanner.go:55]().
- `CustomRules`: List of user-defined `Rule` objects [pkg/fanal/secret/scanner.go:63]().
- `CustomAllowRules`: Global exclusions for the scanner [pkg/fanal/secret/scanner.go:64]().

Sources: [pkg/fanal/secret/scanner.go:52-72]()

---

# Page: License Scanning and Classification

# License Scanning and Classification

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/guide/coverage/others/activestate.md](docs/guide/coverage/others/activestate.md)
- [docs/guide/coverage/others/index.md](docs/guide/coverage/others/index.md)
- [pkg/dependency/parser/java/pom/var.go](pkg/dependency/parser/java/pom/var.go)
- [pkg/fanal/analyzer/imgconf/apk/apk.go](pkg/fanal/analyzer/imgconf/apk/apk.go)
- [pkg/fanal/analyzer/language/analyze.go](pkg/fanal/analyzer/language/analyze.go)
- [pkg/fanal/analyzer/licensing/license.go](pkg/fanal/analyzer/licensing/license.go)
- [pkg/fanal/analyzer/os/release/testdata/activestate](pkg/fanal/analyzer/os/release/testdata/activestate)
- [pkg/fanal/analyzer/pkg/dpkg/copyright.go](pkg/fanal/analyzer/pkg/dpkg/copyright.go)
- [pkg/iac/rego/store.go](pkg/iac/rego/store.go)
- [pkg/iac/rego/store_test.go](pkg/iac/rego/store_test.go)
- [pkg/licensing/classifier.go](pkg/licensing/classifier.go)
- [pkg/licensing/classifier_test.go](pkg/licensing/classifier_test.go)
- [pkg/licensing/expression/expression.go](pkg/licensing/expression/expression.go)
- [pkg/licensing/expression/expression_test.go](pkg/licensing/expression/expression_test.go)
- [pkg/licensing/expression/types.go](pkg/licensing/expression/types.go)
- [pkg/licensing/normalize.go](pkg/licensing/normalize.go)
- [pkg/licensing/normalize_test.go](pkg/licensing/normalize_test.go)
- [pkg/licensing/scanner.go](pkg/licensing/scanner.go)
- [pkg/licensing/scanner_test.go](pkg/licensing/scanner_test.go)
- [pkg/log/logger.go](pkg/log/logger.go)
- [pkg/scan/local/service.go](pkg/scan/local/service.go)
- [pkg/scan/local/service_test.go](pkg/scan/local/service_test.go)

</details>



## Purpose and Scope

This document describes Trivy's license scanning and classification system, which identifies and categorizes software licenses found in OS packages, application dependencies, and container images. License scanning is one of Trivy's core scanning capabilities, alongside vulnerability detection ([4.1]()), misconfiguration scanning ([4.2]()), and secret detection ([4.3]()).

License scanning operates across all target types, including container images, filesystems, repositories, and SBOMs. The system detects licenses from package metadata and file headers, classifies them according to SPDX standards, and supports filtering by license category (forbidden, restricted, etc.).

---

## System Architecture

### License Scanning in the Detection Pipeline

The license scanning process is integrated into the `Service.ScanTarget` workflow, where licenses are detected, classified, and filtered before being included in the final `types.Report`.

[pkg/scan/local/service.go:142-143]()
[pkg/scan/local/service.go:210-234]()

#### High-Level Data Flow

```mermaid
graph TB
    subgraph "Artifact Analysis (Fanal)"
        [Analyzer] --> [ExtractMetadata]
        [ExtractMetadata] --> [Licenses]
    end
    
    subgraph "License Processing (licensing)"
        [Scanner.Scan] --> [expression.Normalize]
        [expression.Normalize] --> [Scanner.detectCategory]
        [Scanner.detectCategory] --> [CategoryToSeverity]
    end
    
    subgraph "Storage & Representation"
        [ftypes.Package.Licenses] --> [types.ScanTarget.Licenses]
        [types.ScanTarget.Licenses] --> [types.Result.Licenses]
    end
    
    subgraph "Output & Classification"
        [types.LicenseCategory] --> [SeverityMapping]
        [SeverityMapping] --> [FinalReport]
    end
```

**Sources:** [pkg/scan/local/service.go:117-164](), [pkg/licensing/scanner.go:28-36]()

---

## License Detection and Extraction

### Package-Level License Detection
Licenses are primarily detected during the artifact analysis phase by Fanal's package analyzers. Each package manager analyzer extracts license information from package metadata.

#### OS Package Detection (Dpkg Example)
The `dpkgLicenseAnalyzer` parses `/usr/share/doc/*/copyright` files. It uses regex to find common license references and machine-readable "License:" fields.

[pkg/fanal/analyzer/pkg/dpkg/copyright.go:33-75]()
[pkg/fanal/analyzer/pkg/dpkg/copyright.go:78-108]()

#### License File and Header Detection
The `licenseFileAnalyzer` scans for files named `LICENSE`, `COPYRIGHT`, or specific extensions (e.g., `.c`, `.py`, `.go`). It uses a classification engine to identify license text.

[pkg/fanal/analyzer/licensing/license.go:73-78]()
[pkg/fanal/analyzer/licensing/license.go:93-112]()

### License Classification Engine
Trivy provides a `Classify` function that takes raw content and returns identified licenses. This is used as a fallback when metadata is missing.

[pkg/licensing/classifier.go:1-50]()
[pkg/fanal/analyzer/pkg/dpkg/copyright.go:51-54]()

---

## License Expression Parsing and Normalization

### SPDX Normalization
Trivy maps various license strings (e.g., "AL-2", "ASL", "BSD-STYLE") to standardized SPDX identifiers using a comprehensive mapping table.

[pkg/licensing/normalize.go:17-126]()

### Expression Handling
Trivy uses the `pkg/licensing/expression` package to handle complex license expressions (AND, OR, WITH).

[pkg/licensing/expression/expression.go:1-50]()

```mermaid
graph LR
    subgraph "Input Strings"
        [A1] --> ["GPL-2.0+"]
        [A2] --> ["Apache-2.0 OR MIT"]
    end
    
    subgraph "Normalization Logic"
        [A1] --> [StandardizeKeyAndSuffix]
        [A2] --> [expression.Normalize]
    end
    
    subgraph "Resulting Entity"
        [StandardizeKeyAndSuffix] --> [expression.SimpleExpr]
        [expression.Normalize] --> [expression.CompoundExpr]
    end
```

**Sources:** [pkg/licensing/normalize.go:13-15](), [pkg/licensing/scanner.go:29-32]()

---

## License Classification and Severity

### License Categories
Licenses are classified into categories defined in `types.LicenseCategory`. The `Scanner` determines the category by looking up normalized names in a provided category map.

[pkg/licensing/scanner.go:16-18]()
[pkg/licensing/scanner.go:113-124]()

| Category | Severity | Example |
| :--- | :--- | :--- |
| `CategoryForbidden` | `CRITICAL` | AGPL-3.0 |
| `CategoryRestricted` | `HIGH` | GPL-3.0 |
| `CategoryReciprocal` | `MEDIUM` | MPL-2.0 |
| `CategoryNotice` | `LOW` | MIT |

[pkg/licensing/scanner.go:99-111]()

### Compound Expression Logic
For complex expressions, the `Scanner.detectCategory` function applies recursive logic:
- **AND**: Uses the category with the **maximum** severity (most restrictive).
- **OR**: Uses the category with the **minimum** severity (least restrictive).
- **WITH**: Treated as a simple expression including the exception.

[pkg/licensing/scanner.go:38-75]()

---

## Implementation Details

### The Scanner Class
The `Scanner` is the core component responsible for matching detected licenses against user-defined categories.

[pkg/licensing/scanner.go:16-26]()

### Text-Based Matching
Trivy also supports matching license text patterns using a `text://` prefix. This allows the scanner to identify licenses based on specific substrings or regex in the license body.

[pkg/licensing/scanner.go:79-97]()
[pkg/licensing/normalize_test.go:102-107]()

### Service Integration
The `local.Service` orchestrates the scanning process. It calls `scanLicenses` which initializes a `licensing.NewScanner` with categories from the scan options.

[pkg/scan/local/service.go:143]()
[pkg/scan/local/service.go:210-234]()

```mermaid
graph TD
    subgraph "Service.scanLicenses"
        [Service] --> [licensing.NewScanner]
        [licensing.NewScanner] --> [Scanner.Scan]
        [Scanner.Scan] --> [expression.Normalize]
    end
    
    subgraph "Scanner Logic"
        [expression.Normalize] --> [Scanner.detectCategory]
        [Scanner.detectCategory] --> [Scanner.licenseToCategory]
    end
    
    subgraph "Final Result"
        [Scanner.licenseToCategory] --> [types.LicenseFinding]
    end
```

**Sources:** [pkg/scan/local/service.go:210-234](), [pkg/licensing/scanner.go:28-36]()

---

## Summary of Key Functions

| Function | File | Purpose |
| :--- | :--- | :--- |
| `NewScanner` | [pkg/licensing/scanner.go:20-26]() | Initializes scanner with category maps. |
| `Scan` | [pkg/licensing/scanner.go:28-36]() | Normalizes license name and detects its category. |
| `detectCategory` | [pkg/licensing/scanner.go:44-75]() | Recursive logic for AND/OR/WITH expressions. |
| `Normalize` | [pkg/licensing/expression/expression.go:1-100]() | Parses and normalizes license strings. |
| `Classify` | [pkg/licensing/classifier.go:1-50]() | Identifies licenses from raw file content. |

**Sources:** [pkg/licensing/scanner.go:1-125](), [pkg/scan/local/service.go:210-234]()

---

# Page: Target Types and Scanning Workflows

# Target Types and Scanning Workflows

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [go.mod](go.mod)
- [go.sum](go.sum)
- [mkdocs.yml](mkdocs.yml)
- [pkg/commands/app.go](pkg/commands/app.go)
- [pkg/commands/app_test.go](pkg/commands/app_test.go)
- [pkg/commands/artifact/run.go](pkg/commands/artifact/run.go)
- [pkg/commands/testdata/java-db/metadata.json](pkg/commands/testdata/java-db/metadata.json)
- [pkg/commands/testdata/policy/metadata.json](pkg/commands/testdata/policy/metadata.json)
- [pkg/fanal/analyzer/analyzer.go](pkg/fanal/analyzer/analyzer.go)
- [pkg/fanal/analyzer/analyzer_test.go](pkg/fanal/analyzer/analyzer_test.go)
- [pkg/fanal/analyzer/pkg/apk/apk.go](pkg/fanal/analyzer/pkg/apk/apk.go)
- [pkg/fanal/analyzer/pkg/apk/apk_test.go](pkg/fanal/analyzer/pkg/apk/apk_test.go)
- [pkg/fanal/analyzer/pkg/apk/testdata/apk](pkg/fanal/analyzer/pkg/apk/testdata/apk)
- [pkg/fanal/applier/applier.go](pkg/fanal/applier/applier.go)
- [pkg/fanal/applier/applier_test.go](pkg/fanal/applier/applier_test.go)
- [pkg/fanal/artifact/artifact.go](pkg/fanal/artifact/artifact.go)
- [pkg/fanal/artifact/image/image.go](pkg/fanal/artifact/image/image.go)
- [pkg/fanal/artifact/image/image_test.go](pkg/fanal/artifact/image/image_test.go)
- [pkg/fanal/artifact/local/fs.go](pkg/fanal/artifact/local/fs.go)
- [pkg/fanal/artifact/local/fs_test.go](pkg/fanal/artifact/local/fs_test.go)
- [pkg/fanal/artifact/sbom/sbom_test.go](pkg/fanal/artifact/sbom/sbom_test.go)
- [pkg/fanal/artifact/vm/vm_test.go](pkg/fanal/artifact/vm/vm_test.go)
- [pkg/fanal/test/integration/testdata/goldens/packages/alpine-310.json.golden](pkg/fanal/test/integration/testdata/goldens/packages/alpine-310.json.golden)
- [pkg/fanal/test/integration/testdata/goldens/packages/vulnimage.json.golden](pkg/fanal/test/integration/testdata/goldens/packages/vulnimage.json.golden)
- [pkg/fanal/test/integration/testdata/goldens/vuln-image1.2.3.expectedlibs.golden](pkg/fanal/test/integration/testdata/goldens/vuln-image1.2.3.expectedlibs.golden)
- [pkg/fanal/types/artifact.go](pkg/fanal/types/artifact.go)
- [pkg/flag/kubernetes_flags.go](pkg/flag/kubernetes_flags.go)
- [pkg/flag/options.go](pkg/flag/options.go)
- [pkg/k8s/commands/cluster.go](pkg/k8s/commands/cluster.go)
- [pkg/k8s/commands/run.go](pkg/k8s/commands/run.go)
- [pkg/k8s/report/report.go](pkg/k8s/report/report.go)
- [pkg/k8s/report/report_test.go](pkg/k8s/report/report_test.go)
- [pkg/k8s/report/summary.go](pkg/k8s/report/summary.go)
- [pkg/k8s/report/summary_test.go](pkg/k8s/report/summary_test.go)
- [pkg/k8s/report/table.go](pkg/k8s/report/table.go)
- [pkg/k8s/scanner/scanner.go](pkg/k8s/scanner/scanner.go)
- [pkg/k8s/writer_test.go](pkg/k8s/writer_test.go)

</details>



## Purpose and Scope

This document explains how Trivy scans different artifact types using target-specific workflows. Each target type (container image, filesystem, repository, Kubernetes, etc.) follows a distinct processing path optimized for its characteristics. The page covers:

- Target type constants and their CLI command mappings.
- How the `Runner` interface orchestrates the scanning pipeline in [pkg/commands/artifact/run.go:79-98]().
- Target-specific analyzer configurations and service initialization.
- Processing differences between standalone and client/server modes.
- Kubernetes-specific scanning workflows and resource collection.

For details about individual scanning capabilities, see page 4. For deployment architecture patterns, see page 8.

Sources: [pkg/commands/artifact/run.go:1-100](), [pkg/commands/app.go:88-102]()

## Scanning Workflow Overview

### High-Level Scanning Pipeline

All target types flow through a unified scanning pipeline orchestrated by the `Runner` in [pkg/commands/artifact/run.go:79-98](). The pipeline consists of three main phases:

1.  **Runner Initialization**: Performed by `NewRunner` in [pkg/commands/artifact/run.go:121-174](). This handles DB initialization via `r.initDB`, VEX repository downloads, and WASM module loading via `module.NewManager`.
2.  **Target Scanning**: Execution of target-specific methods like `ScanImage`, `ScanFilesystem`, or `ScanK8sVulns`.
3.  **Output Generation**: Result filtering via `runner.Filter` and report writing via `runner.Report`.

**Workflow: Runner Orchestration Flow**

```mermaid
graph TD
    NewRunner["NewRunner(ctx, opts, targetKind)"]
    InitDB["r.initDB(ctx, opts)"]
    ModuleInit["module.NewManager()"]
    
    ScanMethod["Runner.Scan*(ctx, opts)"]
    Filter["Runner.Filter(ctx, opts, report)"]
    Report["Runner.Report(ctx, opts, report)"]
    
    NewRunner --> InitDB
    NewRunner --> ModuleInit
    InitDB --> ScanMethod
    
    ScanMethod --> ScanImage["ScanImage()"]
    ScanMethod --> ScanFS["ScanFilesystem()"]
    ScanMethod --> ScanRepo["ScanRepository()"]
    ScanMethod --> ScanK8s["Scan (K8s Scanner)"]
    
    ScanImage --> Filter
    ScanFS --> Filter
    ScanRepo --> Filter
    ScanK8s --> Filter
    
    Filter --> Report
```

Sources: [pkg/commands/artifact/run.go:121-174](), [pkg/commands/artifact/run.go:199-296](), [pkg/k8s/scanner/scanner.go:55-148]()

### Target Type Constants and Command Mapping

Trivy defines `TargetKind` constants in [pkg/commands/artifact/run.go:49-57]() to route CLI commands to the correct scanning logic.

| CLI Command | TargetKind Constant | Runner Method |
| :--- | :--- | :--- |
| `trivy image` | `TargetContainerImage` | `ScanImage()` |
| `trivy fs` | `TargetFilesystem` | `ScanFilesystem()` |
| `trivy rootfs` | `TargetRootfs` | `ScanRootfs()` |
| `trivy repo` | `TargetRepository` | `ScanRepository()` |
| `trivy sbom` | `TargetSBOM` | `ScanSBOM()` |
| `trivy vm` | `TargetVM` | `ScanVM()` |
| `trivy k8s` | `TargetK8s` | `k8s/scanner.Scan()` |

Sources: [pkg/commands/artifact/run.go:49-57](), [pkg/commands/app.go:88-106]()

## Scan Service Initialization

### Standalone vs Client/Server Mode

Each target type selects an appropriate `InitializeScanService` based on the presence of a server address or input flags.

**Service Selection Logic (Image Example)**

```mermaid
graph TD
    CheckServer{"opts.ServerAddr == ''?"}
    CheckInput{"opts.Input != ''?"}
    
    ImageStandalone["imageStandaloneScanService"]
    ImageRemote["imageRemoteScanService"]
    ArchiveStandalone["archiveStandaloneScanService"]
    ArchiveRemote["archiveRemoteScanService"]

    CheckServer -->|Yes| CheckInput
    CheckServer -->|No| CheckInputRemote["Check Input (Remote)"]
    
    CheckInput -->|No| ImageStandalone
    CheckInput -->|Yes| ArchiveStandalone
    
    CheckInputRemote -->|No| ImageRemote
    CheckInputRemote -->|Yes| ArchiveRemote
```

Sources: [pkg/commands/artifact/run.go:204-217]()

### InitializeScanService Function Signature

All scan services implement the `InitializeScanService` function type defined in [pkg/commands/artifact/run.go:62]():

`type InitializeScanService func(context.Context, ScannerConfig) (scan.Service, func(), error)`

The `ScannerConfig` in [pkg/commands/artifact/run.go:64-77]() encapsulates target identifiers, cache options, and artifact options used to configure the underlying `fanal` analyzers.

## Target-Specific Workflows

### Container Image Scanning
Detailed in **[Container Image Scanning](#5.1)**.
- **Analyzers**: Disables `analyzer.TypeLockfiles` [pkg/commands/artifact/run.go:201]() as images are scanned via layer analysis.
- **Workflow**: Processes image IDs and diff IDs to calculate cache keys in [pkg/fanal/artifact/image/image.go:127]().

### Filesystem and Rootfs Scanning
Detailed in **[Filesystem and Rootfs Scanning](#5.2)**.
- **Filesystem**: Disables `analyzer.TypeIndividualPkgs` and `analyzer.TypeSBOM` [pkg/commands/artifact/run.go:224-225]() to focus on source code dependencies.
- **Rootfs**: Disables `analyzer.TypeLockfiles` [pkg/commands/artifact/run.go:232]() to treat the directory like an unpacked container.

### Repository Scanning
Detailed in **[Repository and SBOM Scanning](#5.4)**.
- **Logic**: Specifically sets `PkgTypes` to `PkgTypeLibrary` [pkg/commands/artifact/run.go:252]() and disables OS analyzers [pkg/commands/artifact/run.go:255]().
- **Git Integration**: Automatically detects Git metadata (commit hash, branch) to use as cache keys in [pkg/fanal/artifact/local/fs.go:84-92]().

### Kubernetes Scanning
Detailed in **[Kubernetes Cluster Scanning](#5.3)**.
- **Workflow**: Uses `trivy-kubernetes` to list artifacts [pkg/k8s/commands/run.go:10-11]().
- **Parallelism**: Scans images within the cluster in parallel using `parallel.NewPipeline` [pkg/k8s/scanner/scanner.go:129]().
- **Core Components**: Separates "Resource" artifacts from "Core" components (e.g., etcd, apiserver) to apply specific vulnerability checks [pkg/k8s/scanner/scanner.go:74-82]().

### Infrastructure as Code (IaC) Scanning
Detailed in **[Infrastructure as Code Scanning](#5.5)**.
- **Integration**: Handled primarily through the `ScanFilesystem` workflow when misconfiguration scanners are enabled.
- **Policy**: Utilizes Rego-based checks and specific analyzers for Terraform, CloudFormation, and Helm.

Sources: [pkg/commands/artifact/run.go:200-296](), [pkg/k8s/scanner/scanner.go:74-133](), [pkg/fanal/artifact/local/fs.go:84-92]()

## Result Processing and Filtering

Regardless of the target, all results are filtered through `Runner.Filter` [pkg/commands/artifact/run.go:93](). This applies:
1.  **Severity Filtering**: Based on `--severity` flags.
2.  **Vulnerability Status**: Ignoring unfixed issues via `--ignore-unfixed`.
3.  **VEX**: Applying Vulnerability Exploitability eXchange data.
4.  **Policy**: Custom Rego policies for ignoring specific findings.

Sources: [pkg/commands/artifact/run.go:310-323](), [pkg/k8s/scanner/scanner.go:225]()

---

# Page: Container Image Scanning

# Container Image Scanning

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal/testutil/docker.go](internal/testutil/docker.go)
- [pkg/fanal/analyzer/analyzer.go](pkg/fanal/analyzer/analyzer.go)
- [pkg/fanal/analyzer/analyzer_test.go](pkg/fanal/analyzer/analyzer_test.go)
- [pkg/fanal/analyzer/imgconf/dockerfile/dockerfile.go](pkg/fanal/analyzer/imgconf/dockerfile/dockerfile.go)
- [pkg/fanal/analyzer/imgconf/dockerfile/dockerfile_test.go](pkg/fanal/analyzer/imgconf/dockerfile/dockerfile_test.go)
- [pkg/fanal/analyzer/pkg/apk/apk.go](pkg/fanal/analyzer/pkg/apk/apk.go)
- [pkg/fanal/analyzer/pkg/apk/apk_test.go](pkg/fanal/analyzer/pkg/apk/apk_test.go)
- [pkg/fanal/analyzer/pkg/apk/testdata/apk](pkg/fanal/analyzer/pkg/apk/testdata/apk)
- [pkg/fanal/applier/applier.go](pkg/fanal/applier/applier.go)
- [pkg/fanal/applier/applier_test.go](pkg/fanal/applier/applier_test.go)
- [pkg/fanal/artifact/artifact.go](pkg/fanal/artifact/artifact.go)
- [pkg/fanal/artifact/image/image.go](pkg/fanal/artifact/image/image.go)
- [pkg/fanal/artifact/image/image_test.go](pkg/fanal/artifact/image/image_test.go)
- [pkg/fanal/artifact/local/fs.go](pkg/fanal/artifact/local/fs.go)
- [pkg/fanal/artifact/local/fs_test.go](pkg/fanal/artifact/local/fs_test.go)
- [pkg/fanal/artifact/sbom/sbom_test.go](pkg/fanal/artifact/sbom/sbom_test.go)
- [pkg/fanal/artifact/vm/vm_test.go](pkg/fanal/artifact/vm/vm_test.go)
- [pkg/fanal/image/daemon/containerd.go](pkg/fanal/image/daemon/containerd.go)
- [pkg/fanal/image/daemon/context_test.go](pkg/fanal/image/daemon/context_test.go)
- [pkg/fanal/image/daemon/docker.go](pkg/fanal/image/daemon/docker.go)
- [pkg/fanal/image/daemon/image.go](pkg/fanal/image/daemon/image.go)
- [pkg/fanal/image/daemon/image_test.go](pkg/fanal/image/daemon/image_test.go)
- [pkg/fanal/image/daemon/podman.go](pkg/fanal/image/daemon/podman.go)
- [pkg/fanal/image/daemon/podman_test.go](pkg/fanal/image/daemon/podman_test.go)
- [pkg/fanal/image/image_test.go](pkg/fanal/image/image_test.go)
- [pkg/fanal/image/registry/azure/azure.go](pkg/fanal/image/registry/azure/azure.go)
- [pkg/fanal/image/registry/azure/azure_test.go](pkg/fanal/image/registry/azure/azure_test.go)
- [pkg/fanal/image/registry/ecr/ecr.go](pkg/fanal/image/registry/ecr/ecr.go)
- [pkg/fanal/image/registry/ecr/ecr_test.go](pkg/fanal/image/registry/ecr/ecr_test.go)
- [pkg/fanal/image/registry/google/google.go](pkg/fanal/image/registry/google/google.go)
- [pkg/fanal/image/registry/google/google_test.go](pkg/fanal/image/registry/google/google_test.go)
- [pkg/fanal/image/registry/intf/registry.go](pkg/fanal/image/registry/intf/registry.go)
- [pkg/fanal/image/registry/token.go](pkg/fanal/image/registry/token.go)
- [pkg/fanal/test/integration/containerd_test.go](pkg/fanal/test/integration/containerd_test.go)
- [pkg/fanal/test/integration/docker/docker.go](pkg/fanal/test/integration/docker/docker.go)
- [pkg/fanal/test/integration/library_test.go](pkg/fanal/test/integration/library_test.go)
- [pkg/fanal/test/integration/registry_test.go](pkg/fanal/test/integration/registry_test.go)
- [pkg/fanal/test/integration/testdata/goldens/packages/alpine-310.json.golden](pkg/fanal/test/integration/testdata/goldens/packages/alpine-310.json.golden)
- [pkg/fanal/test/integration/testdata/goldens/packages/vulnimage.json.golden](pkg/fanal/test/integration/testdata/goldens/packages/vulnimage.json.golden)
- [pkg/fanal/test/integration/testdata/goldens/vuln-image1.2.3.expectedlibs.golden](pkg/fanal/test/integration/testdata/goldens/vuln-image1.2.3.expectedlibs.golden)
- [pkg/fanal/types/artifact.go](pkg/fanal/types/artifact.go)
- [pkg/vex/repo/manager.go](pkg/vex/repo/manager.go)

</details>



## Purpose and Scope

Container image scanning is a core capability of Trivy, enabling the analysis of OCI-compliant container images to identify security vulnerabilities, misconfigurations, and secrets. This process involves deep inspection of image layers, detection of the operating system, and extraction of application-level dependencies from package manager artifacts.

This page details the technical implementation of image scanning, from artifact initialization to layer merging and package extraction.

## Overview

Trivy analyzes container images by processing individual layers as blobs and then applying them in sequence to reconstruct the final filesystem state. The scanning pipeline supports images from various sources:
- Local Docker/Podman daemons
- Remote container registries
- Containerd/CRI-O runtimes
- Exported tar archives

**Sources:** [pkg/fanal/artifact/image/image.go:53-87](), [pkg/fanal/types/artifact.go:14-21]()

## Core Architecture

The image scanning workflow is orchestrated by the `Artifact` struct, which coordinates image metadata retrieval, layer walking, and analysis.

```mermaid
graph TD
    subgraph "Artifact Initialization"
        NewArt["image.NewArtifact()<br/>image.go:53"]
        ImgIntf["types.Image Interface"]
    end

    subgraph "Inspection Pipeline"
        Inspect["Artifact.Inspect()<br/>image.go:89"]
        CacheCheck["cache.MissingBlobs()<br/>image.go:135"]
        WalkLayer["walker.LayerTar.Walk()<br/>walker/layertar.go"]
    end

    subgraph "Analysis Engine"
        Analyzer["analyzer.AnalyzerGroup<br/>analyzer.go:133"]
        ConfigAnalyzer["analyzer.ConfigAnalyzerGroup<br/>imgconf/dockerfile"]
        PostAnalyzer["analyzer.PostAnalyzer"]
    end

    subgraph "Reconstruction"
        Applier["applier.Applier<br/>applier/applier.go"]
        ApplyLayers["Applier.ApplyLayers()<br/>applier/docker.go"]
    end

    NewArt --> ImgIntf
    ImgIntf --> Inspect
    Inspect --> CacheCheck
    CacheCheck --> WalkLayer
    WalkLayer --> Analyzer
    Inspect --> ConfigAnalyzer
    Analyzer --> Applier
    Applier --> ApplyLayers
```

**Sources:** [pkg/fanal/artifact/image/image.go:39-87](), [pkg/fanal/artifact/image/image.go:89-169](), [pkg/fanal/analyzer/analyzer.go:133-140]()

## Layer Analysis and OS Detection

Trivy processes each layer independently. During the `Inspect` phase, it calculates cache keys based on layer DiffIDs to avoid redundant analysis of shared layers.

### Operating System Detection
OS detection occurs within specific analyzers (e.g., `alpine`, `debian`, `redhat`) that look for release files like `/etc/os-release` or `/etc/alpine-release`. 

- **Merging Logic:** Since images are layered, OS information can span multiple layers. The `OS.Merge` function handles conflicts, such as when an image contains both `/etc/redhat-release` and `/etc/oracle-release`, prioritizing the more specific distribution [pkg/fanal/types/artifact.go:52-82]().
- **Extended Security:** Trivy detects if an OS version is under extended support (e.g., Ubuntu ESM) via the `Extended` field [pkg/fanal/types/artifact.go:23-30]().

### Package Extraction
Analyzers extract packages from two primary sources:
1. **OS Package Databases:** Files like `/lib/apk/db/installed` (Alpine), `/var/lib/dpkg/status` (Debian), or RPM databases [pkg/fanal/artifact/local/fs_test.go:58-81]().
2. **Application Dependencies:** Language-specific lockfiles (e.g., `Gemfile.lock`, `package-lock.json`, `requirements.txt`) [pkg/fanal/artifact/local/fs_test.go:152-171]().

**Sources:** [pkg/fanal/artifact/image/image.go:127-149](), [pkg/fanal/types/artifact.go:52-82](), [pkg/fanal/analyzer/imgconf/dockerfile/dockerfile.go:35-47]()

## Image Configuration Analysis

Beyond the filesystem, Trivy analyzes the container image configuration (JSON metadata). The `historyAnalyzer` reconstructs a "virtual" Dockerfile from the image's history to check for misconfigurations.

```mermaid
graph LR
    subgraph "Image Config Space"
        V1Config["v1.ConfigFile<br/>google/go-containerregistry"]
        History["History[]<br/>CreatedBy strings"]
    end

    subgraph "Logic Space"
        GuessBase["image.GuessBaseImageIndex()"]
        ToDockerfile["imageConfigToDockerfile()<br/>dockerfile.go:77"]
        StripMeta["stripBuildMetadata()<br/>dockerfile.go:137"]
    end

    subgraph "Entity Space"
        MisconfScanner["misconf.Scanner<br/>dockerfile.go:36"]
        ScanResult["analyzer.ConfigAnalysisResult"]
    end

    V1Config --> History
    History --> ToDockerfile
    ToDockerfile --> StripMeta
    StripMeta --> MisconfScanner
    MisconfScanner --> ScanResult
```

**Key Implementation Details:**
- **Base Image Guessing:** Trivy attempts to identify where the base image ends and user layers begin using `image.GuessBaseImageIndex` [pkg/fanal/analyzer/imgconf/dockerfile/dockerfile.go:79]().
- **Instruction Reconstruction:** It normalizes `CreatedBy` strings from history, handling differences between legacy Docker, BuildKit, and Buildah [pkg/fanal/analyzer/imgconf/dockerfile/dockerfile.go:80-119]().
- **Security Checks:** The reconstructed Dockerfile is passed to the `misconf.Scanner` to detect issues like `ADD` instead of `COPY` or running as `root` [pkg/fanal/analyzer/imgconf/dockerfile/dockerfile_test.go:94-136]().

**Sources:** [pkg/fanal/analyzer/imgconf/dockerfile/dockerfile.go:49-75](), [pkg/fanal/analyzer/imgconf/dockerfile/dockerfile.go:77-128]()

## Layer Merging (Applier)

After individual layers are analyzed and stored in the cache as `BlobInfo`, the `Applier` component merges them into a final `ArtifactDetail`.

| Concept | Description | Code Reference |
| :--- | :--- | :--- |
| **Whiteout Files** | Files starting with `.wh.` that indicate a file was deleted in a subsequent layer. | [pkg/fanal/types/artifact.go:177]() |
| **Opaque Dirs** | Directories containing a `.wh..wh..opq` marker, indicating the entire directory from lower layers should be hidden. | [pkg/fanal/types/artifact.go:176]() |
| **Layer Provenance** | Tracking which specific layer (Digest/DiffID) introduced a package. | [pkg/fanal/types/artifact.go:89-94]() |

**Sources:** [pkg/fanal/applier/applier.go:20-21](), [pkg/fanal/types/artifact.go:168-196]()

## Integration and Data Flow

The following sequence describes the end-to-end data flow for a container image scan:

1.  **Artifact Initialization:** `NewArtifact` is called with a `types.Image` implementation (e.g., Docker, Containerd, or Archive) [pkg/fanal/artifact/image/image.go:53]().
2.  **Metadata Extraction:** The scanner retrieves the Image ID and Config File [pkg/fanal/artifact/image/image.go:89-99]().
3.  **Cache Lookup:** Missing layers are identified via `a.cache.MissingBlobs` [pkg/fanal/artifact/image/image.go:135]().
4.  **Parallel Analysis:** New layers are walked and analyzed in parallel using `errgroup` and semaphores to limit concurrency [pkg/fanal/artifact/local/fs.go:198-204]().
5.  **Result Aggregation:** `AnalysisResult.Merge` combines findings from different layers, ensuring OS and Package information is correctly consolidated [pkg/fanal/analyzer/analyzer_test.go:35-157]().
6.  **Final Application:** The `Applier` merges the `BlobInfo` into a single `ArtifactDetail` containing the flattened package list and vulnerabilities [pkg/fanal/test/integration/library_test.go:216-222]().

**Sources:** [pkg/fanal/artifact/image/image.go:89-169](), [pkg/fanal/analyzer/analyzer.go:176-197](), [pkg/fanal/test/integration/library_test.go:216-222]()

---

# Page: Filesystem and Rootfs Scanning

# Filesystem and Rootfs Scanning

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [pkg/fanal/analyzer/analyzer.go](pkg/fanal/analyzer/analyzer.go)
- [pkg/fanal/analyzer/analyzer_test.go](pkg/fanal/analyzer/analyzer_test.go)
- [pkg/fanal/analyzer/language/c/conan/conan.go](pkg/fanal/analyzer/language/c/conan/conan.go)
- [pkg/fanal/analyzer/language/c/conan/conan_test.go](pkg/fanal/analyzer/language/c/conan/conan_test.go)
- [pkg/fanal/analyzer/language/c/conan/testdata/cacheDir/.conan/data/openssl/3.0.5/_/_/export/conanfile.py](pkg/fanal/analyzer/language/c/conan/testdata/cacheDir/.conan/data/openssl/3.0.5/_/_/export/conanfile.py)
- [pkg/fanal/analyzer/language/c/conan/testdata/cacheDir/.conan/data/zlib/1.2.13/_/_/export/conanfile.py](pkg/fanal/analyzer/language/c/conan/testdata/cacheDir/.conan/data/zlib/1.2.13/_/_/export/conanfile.py)
- [pkg/fanal/analyzer/language/c/conan/testdata/cacheDir_v2/p/opens464b5c427ce9d/e/conanfile.py](pkg/fanal/analyzer/language/c/conan/testdata/cacheDir_v2/p/opens464b5c427ce9d/e/conanfile.py)
- [pkg/fanal/analyzer/language/c/conan/testdata/cacheDir_v2/p/zlib41bd3946e7341/e/conanfile.py](pkg/fanal/analyzer/language/c/conan/testdata/cacheDir_v2/p/zlib41bd3946e7341/e/conanfile.py)
- [pkg/fanal/analyzer/language/c/conan/testdata/empty/conan.lock](pkg/fanal/analyzer/language/c/conan/testdata/empty/conan.lock)
- [pkg/fanal/analyzer/language/c/conan/testdata/happy/conan.lock](pkg/fanal/analyzer/language/c/conan/testdata/happy/conan.lock)
- [pkg/fanal/analyzer/language/c/conan/testdata/happy_v2/release.lock](pkg/fanal/analyzer/language/c/conan/testdata/happy_v2/release.lock)
- [pkg/fanal/analyzer/pkg/apk/apk.go](pkg/fanal/analyzer/pkg/apk/apk.go)
- [pkg/fanal/analyzer/pkg/apk/apk_test.go](pkg/fanal/analyzer/pkg/apk/apk_test.go)
- [pkg/fanal/analyzer/pkg/apk/testdata/apk](pkg/fanal/analyzer/pkg/apk/testdata/apk)
- [pkg/fanal/applier/applier.go](pkg/fanal/applier/applier.go)
- [pkg/fanal/applier/applier_test.go](pkg/fanal/applier/applier_test.go)
- [pkg/fanal/artifact/artifact.go](pkg/fanal/artifact/artifact.go)
- [pkg/fanal/artifact/image/image.go](pkg/fanal/artifact/image/image.go)
- [pkg/fanal/artifact/image/image_test.go](pkg/fanal/artifact/image/image_test.go)
- [pkg/fanal/artifact/local/fs.go](pkg/fanal/artifact/local/fs.go)
- [pkg/fanal/artifact/local/fs_test.go](pkg/fanal/artifact/local/fs_test.go)
- [pkg/fanal/artifact/sbom/sbom_test.go](pkg/fanal/artifact/sbom/sbom_test.go)
- [pkg/fanal/artifact/vm/vm_test.go](pkg/fanal/artifact/vm/vm_test.go)
- [pkg/fanal/test/integration/testdata/goldens/packages/alpine-310.json.golden](pkg/fanal/test/integration/testdata/goldens/packages/alpine-310.json.golden)
- [pkg/fanal/test/integration/testdata/goldens/packages/vulnimage.json.golden](pkg/fanal/test/integration/testdata/goldens/packages/vulnimage.json.golden)
- [pkg/fanal/test/integration/testdata/goldens/vuln-image1.2.3.expectedlibs.golden](pkg/fanal/test/integration/testdata/goldens/vuln-image1.2.3.expectedlibs.golden)
- [pkg/fanal/types/artifact.go](pkg/fanal/types/artifact.go)
- [pkg/fanal/walker/fs.go](pkg/fanal/walker/fs.go)
- [pkg/fanal/walker/fs_test.go](pkg/fanal/walker/fs_test.go)
- [pkg/fanal/walker/tar.go](pkg/fanal/walker/tar.go)
- [pkg/fanal/walker/tar_test.go](pkg/fanal/walker/tar_test.go)
- [pkg/fanal/walker/vm.go](pkg/fanal/walker/vm.go)
- [pkg/fanal/walker/walk.go](pkg/fanal/walker/walk.go)
- [pkg/fanal/walker/walk_test.go](pkg/fanal/walker/walk_test.go)

</details>



Trivy provides two distinct modes for scanning local filesystem structures: `filesystem` (or `fs`) and `rootfs`. While both analyze local directories, they differ in their intended use cases and analyzer configurations.

- **Filesystem (`fs`)**: Designed for scanning project directories, application code, and individual files. Focuses on language-specific dependencies and configurations.
- **Rootfs**: Designed for scanning unpacked root filesystems, such as extracted container images or VM filesystems. Focuses on OS packages and system-level analysis.

This page explains both modes, their differences, and the underlying technical implementation.

## Command Interface

Trivy provides two commands for local filesystem scanning, both defined in `pkg/commands/app.go`.

### Filesystem Command

The `filesystem` command (alias `fs`) scans project directories and individual files:

```bash
# Scan a project directory
trivy fs /path/to/your_project

# Scan a single file
trivy fs ./trivy-ci-test/Pipfile.lock
```

The `NewFilesystemCommand` function at [pkg/commands/app.go:329-389]() creates this command with specific characteristics:

- Memory cache is the default backend (`cache.TypeMemory`) - see [pkg/commands/app.go:331]()
- Individual package analyzers (`analyzer.TypeIndividualPkgs`) and SBOM analyzer (`analyzer.TypeSBOM`) are disabled.
- Both standalone and client/server modes are supported via `filesystemStandaloneScanService` and `filesystemRemoteScanService`.

### Rootfs Command

The `rootfs` command scans unpacked root filesystem structures:

```bash
# Export and scan a container filesystem
docker export $(docker create alpine:3.10.2) | tar -C /tmp/rootfs -xvf -
trivy rootfs /tmp/rootfs
```

The `NewRootfsCommand` function at [pkg/commands/app.go:391-456]() creates this command with these characteristics:

- Lock file analyzers (`analyzer.TypeLockfiles`) are disabled to match image scanning behavior [pkg/commands/app.go:397]().
- Compliance flags and report format flags are restricted or disabled [pkg/commands/app.go:394-395]().

**Sources:** [pkg/commands/app.go:329-456]()

## Scanning Process Architecture

Both filesystem and rootfs scanning share a common pipeline but configure analyzers differently based on their target use case.

### Unified Scanning Pipeline

```mermaid
graph TD
    FSCommand["NewFilesystemCommand<br/>app.go:329"] --> FSRunE["RunE handler<br/>app.go:370"]
    RootfsCommand["NewRootfsCommand<br/>app.go:391"] --> RootfsRunE["RunE handler<br/>app.go:438"]
    
    FSRunE --> ScanFilesystem["runner.ScanFilesystem()<br/>run.go:222"]
    RootfsRunE --> ScanRootfs["runner.ScanRootfs()<br/>run.go:230"]
    
    ScanFilesystem --> DisableFSAnalyzers["opts.DisabledAnalyzers append<br/>TypeIndividualPkgs + TypeSBOM"]
    ScanRootfs --> DisableRootfsAnalyzers["opts.DisabledAnalyzers append<br/>TypeLockfiles"]
    
    DisableFSAnalyzers --> ScanFS["runner.scanFS()"]
    DisableRootfsAnalyzers --> ScanFS
    
    ScanFS --> ModeCheck{"opts.ServerAddr == ''?"}
    ModeCheck -->|Yes| StandaloneService["filesystemStandaloneScanService"]
    ModeCheck -->|No| RemoteService["filesystemRemoteScanService"]
    
    StandaloneService --> ScanArtifact["runner.scanArtifact()"]
    RemoteService --> ScanArtifact
```

### Analyzer Selection Logic

The core difference between the two modes is the exclusion of specific analyzers.

| Mode | Disabled Analyzers | Reason |
| :--- | :--- | :--- |
| **Filesystem** | `TypeIndividualPkgs`, `TypeSBOM` | Focuses on source code and project lockfiles rather than installed artifacts. |
| **Rootfs** | `TypeLockfiles` | Focuses on OS-level packages (dpkg, rpm, apk) rather than application-level source dependencies. |

**Sources:** [pkg/fanal/artifact/local/fs.go:56-99](), [pkg/fanal/artifact/artifact.go:18-53]()

## Technical Implementation: `local.Artifact`

The `local.Artifact` struct handles the actual inspection of files on disk.

### Artifact Initialization
When `local.NewArtifact` is called, it initializes an `AnalyzerGroup` and a `handler.Manager` based on the provided options [pkg/fanal/artifact/local/fs.go:56-65]().

### Git Repository Detection
Trivy automatically detects if the target directory is a Git repository. If it is a clean repository, Trivy uses the latest commit hash to calculate the cache key, significantly improving performance for repeated scans [pkg/fanal/artifact/local/fs.go:84-92]().

```mermaid
graph TD
    subgraph "local.NewArtifact (fs.go:56)"
        InitHandlers["handler.NewManager(opt)"]
        InitAnalyzers["analyzer.NewAnalyzerGroup(opt.AnalyzerOptions())"]
        GitCheck["extractGitInfo(rootPath)"]
        
        GitCheck -->|Is Repo| SetTypeRepo["Set types.TypeRepository"]
        GitCheck -->|Clean| UseCommitHash["CacheKey = CommitHash"]
        GitCheck -->|Dirty/No Repo| UseRandomKey["CacheKey = Random/UUID"]
    end
```

### The `Inspect` Workflow
The `Inspect` function [pkg/fanal/artifact/local/fs.go:169-254]() follows these steps:
1. **Cache Key Calculation**: Based on Git status or random generation [pkg/fanal/artifact/local/fs.go:171]().
2. **Cache Lookup**: If the repository is clean, it checks the `ArtifactCache` for existing results [pkg/fanal/artifact/local/fs.go:177-183]().
3. **Filesystem Traversal**: 
    - If analyzers support `StaticPathAnalyzer`, Trivy only reads specific files [pkg/fanal/artifact/local/fs.go:215-220]().
    - Otherwise, it performs a full walk using `walker.FS` [pkg/fanal/artifact/local/fs.go:222-225]().
4. **Analysis**: Files are passed to the `AnalyzerGroup`. Each analyzer checks if it is `Required` for a given path [pkg/fanal/analyzer/analyzer.go:79]().

**Sources:** [pkg/fanal/artifact/local/fs.go:169-254](), [pkg/fanal/analyzer/analyzer.go:75-80]()

## Analyzer Processing Pipeline

The `AnalyzerGroup` coordinates multiple specialized analyzers.

### Analysis Result Merging
As files are processed, results are collected into an `AnalysisResult` struct [pkg/fanal/analyzer/analyzer.go:176-197](). Results from different layers or files are merged using the `Merge` logic, which handles OS family normalization (e.g., ensuring Oracle Linux overrides RedHat detection if both release files are present) [pkg/fanal/types/artifact.go:52-82]().

### Result Sorting
To ensure deterministic output, results are sorted by file path and package name before being returned [pkg/fanal/analyzer/analyzer.go:210-250]().

| Entity | Code Reference | Purpose |
| :--- | :--- | :--- |
| `AnalysisInput` | [pkg/fanal/analyzer/analyzer.go:145-152]() | Data passed to each analyzer (Content, Path, Info). |
| `AnalysisResult` | [pkg/fanal/analyzer/analyzer.go:176-197]() | Container for OS, Packages, Apps, Secrets, and Licenses. |
| `StaticPathAnalyzer` | [pkg/fanal/analyzer/analyzer.go:126-129]() | Optimization for analyzers that know exactly which files they need. |

**Sources:** [pkg/fanal/analyzer/analyzer.go:176-250](), [pkg/fanal/types/artifact.go:52-82](), [pkg/fanal/artifact/local/fs.go:215-220]()

## File Discovery and Discovery (Walker)

Trivy uses a `Walker` interface to abstract filesystem traversal.

- **`walker.FS`**: Used for standard local directories [pkg/fanal/walker/fs.go]().
- **Filtering**: The walker respects `SkipFiles` and `SkipDirs` options [pkg/fanal/walker/walk.go:18-21](). By default, it skips directories like `.git`, `proc`, `sys`, and `dev` [pkg/fanal/walker/walk.go:11-16]().

```mermaid
graph LR
    Walker["walker.FS.Walk()"] --> Filter{"Should Skip?"}
    Filter -->|No| Opener["analyzer.Opener"]
    Opener --> Analyze["Analyzer.Analyze()"]
    Filter -->|Yes| Next["Skip File/Dir"]
```

**Sources:** [pkg/fanal/walker/walk.go:11-21](), [pkg/fanal/artifact/local/fs.go:38-40]()

## Differences from Image Scanning

While `rootfs` scanning is similar to container image scanning, the implementation differs in how data is accessed:

1. **Image Scanning**: Uses `walker.LayerTar` to process OCI/Docker layers [pkg/fanal/artifact/image/image.go:79](). It must handle whiteout files and opaque directories to reconstruct the final state [pkg/fanal/types/artifact.go:176-177]().
2. **Rootfs/FS Scanning**: Uses `walker.FS` to read directly from the host filesystem [pkg/fanal/artifact/local/fs.go:74](). It does not need to handle layer merging or whiteouts because the filesystem is already "flattened."

**Sources:** [pkg/fanal/artifact/image/image.go:75-87](), [pkg/fanal/artifact/local/fs.go:70-78](), [pkg/fanal/types/artifact.go:168-196]()

---

# Page: Kubernetes Cluster Scanning

# Kubernetes Cluster Scanning

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [pkg/fanal/analyzer/imgconf/dockerfile/dockerfile.go](pkg/fanal/analyzer/imgconf/dockerfile/dockerfile.go)
- [pkg/fanal/analyzer/imgconf/dockerfile/dockerfile_test.go](pkg/fanal/analyzer/imgconf/dockerfile/dockerfile_test.go)
- [pkg/flag/kubernetes_flags.go](pkg/flag/kubernetes_flags.go)
- [pkg/k8s/commands/cluster.go](pkg/k8s/commands/cluster.go)
- [pkg/k8s/commands/run.go](pkg/k8s/commands/run.go)
- [pkg/k8s/report/report.go](pkg/k8s/report/report.go)
- [pkg/k8s/report/report_test.go](pkg/k8s/report/report_test.go)
- [pkg/k8s/report/summary.go](pkg/k8s/report/summary.go)
- [pkg/k8s/report/summary_test.go](pkg/k8s/report/summary_test.go)
- [pkg/k8s/report/table.go](pkg/k8s/report/table.go)
- [pkg/k8s/scanner/scanner.go](pkg/k8s/scanner/scanner.go)
- [pkg/k8s/writer_test.go](pkg/k8s/writer_test.go)
- [pkg/vex/repo/manager.go](pkg/vex/repo/manager.go)

</details>



Trivy scans live Kubernetes clusters for security issues including vulnerabilities in container images and core components, misconfigurations in resource manifests, exposed secrets, and RBAC policy issues. The system connects to a Kubernetes cluster via its API server and performs comprehensive security analysis of both workload resources (pods, deployments, services) and infrastructure components (control plane, nodes).

This page documents the cluster scanning functionality. For scanning Kubernetes manifest files (IaC), see Infrastructure as Code Scanning (5.5). For general container image scanning, see Container Image Scanning (5.1).

## System Architecture

Kubernetes cluster scanning is invoked via the `trivy kubernetes` command and flows through several layers: command execution, cluster resource collection, scanning, and report generation.

### Command and Scanning Flow

```mermaid
graph TB
    subgraph "CLI Entry Point"
        K8sCmd["NewKubernetesCommand()<br/>pkg/commands/app.go"]
        RunFunc["Run(ctx, args, opts)<br/>pkg/k8s/commands/run.go:24"]
    end
    
    subgraph "Cluster Connection"
        GetCluster["k8s.GetCluster(clusterOptions)<br/>pkg/k8s/commands/run.go:33"]
        KubeConfig["KubeConfigFlag<br/>pkg/flag/kubernetes_flags.go:14"]
        K8sContext["WithContext(args[0])<br/>pkg/k8s/commands/run.go:31"]
    end
    
    subgraph "Resource Collection"
        ClusterRun["clusterRun(ctx, opts, cluster)<br/>pkg/k8s/commands/cluster.go:20"]
        TrivyK8s["trivyk8s.New(cluster)"]
        ListArtifacts["ListArtifacts(ctx)<br/>pkg/k8s/commands/cluster.go:46"]
        NodeInfo["ListArtifactAndNodeInfo(ctx)<br/>pkg/k8s/commands/cluster.go:41"]
    end
    
    subgraph "Scanner Initialization"
        NewRunner["cmd.NewRunner(ctx, opts, TargetK8s)<br/>pkg/k8s/commands/run.go:56"]
        ScannerNew["scanner.NewScanner(cluster, runner, opts)<br/>pkg/k8s/scanner/scanner.go:47"]
    end
    
    subgraph "Scanning Execution"
        ScanMethod["Scanner.Scan(ctx, artifactsData)<br/>pkg/k8s/scanner/scanner.go:55"]
        ScanVulns["scanVulns(ctx, artifact, opts)<br/>pkg/k8s/scanner/scanner.go:112"]
        ScanMisconfigs["scanMisconfigs(ctx, resourceArtifacts)<br/>pkg/k8s/scanner/scanner.go:88"]
        ScanK8sVulns["scanK8sVulns(ctx, k8sCoreArtifacts)<br/>pkg/k8s/scanner/scanner.go:136"]
    end
    
    K8sCmd --> RunFunc
    RunFunc --> GetCluster
    GetCluster --> KubeConfig
    GetCluster --> K8sContext
    
    RunFunc --> ClusterRun
    ClusterRun --> TrivyK8s
    TrivyK8s --> ListArtifacts
    TrivyK8s --> NodeInfo
    
    ClusterRun --> NewRunner
    NewRunner --> ScannerNew
    ScannerNew --> ScanMethod
    
    ScanMethod --> ScanVulns
    ScanMethod --> ScanMisconfigs
    ScanMethod --> ScanK8sVulns
```

The command flow begins at `NewKubernetesCommand()` in `pkg/commands/app.go`, which creates a Cobra command that invokes `commands.Run()` from [pkg/k8s/commands/run.go:24](). This function establishes the cluster connection using `k8s.GetCluster()` [pkg/k8s/commands/run.go:33]() with options from flags like `--kubeconfig` [pkg/flag/kubernetes_flags.go:14]() and context arguments.

The `clusterRun()` function in [pkg/k8s/commands/cluster.go:20]() orchestrates resource collection and scanning. It uses the `trivy-kubernetes` library to enumerate cluster resources based on format and filter options. The scanner is initialized via `cmd.NewRunner()` which creates an artifact runner with the `TargetK8s` type [pkg/k8s/commands/run.go:56]().

Sources: [pkg/k8s/commands/run.go:24-41](), [pkg/k8s/commands/cluster.go:20-61](), [pkg/k8s/scanner/scanner.go:41-53](), [pkg/flag/kubernetes_flags.go:14-18]()

### Artifact Processing and Scanning Data Flow

```mermaid
graph TB
    subgraph "Artifact Collection"
        Artifacts["[]*artifacts.Artifact<br/>from trivy-kubernetes"]
        WorkloadArtifacts["resourceArtifacts<br/>pkg/k8s/scanner/scanner.go:81"]
        K8sCoreArtifacts["k8sCoreArtifacts<br/>pkg/k8s/scanner/scanner.go:78"]
    end
    
    subgraph "Scanner.Scan() Method"
        ScanEntry["Scanner.Scan(ctx, artifactsData)<br/>pkg/k8s/scanner/scanner.go:55"]
        ArtifactSplit["Split by Kind suffix:<br/>'Components' or 'Cluster'<br/>pkg/k8s/scanner/scanner.go:77"]
        FormatCheck["if Format == CycloneDX<br/>pkg/k8s/scanner/scanner.go:64"]
    end
    
    subgraph "Vulnerability Scanning Path"
        ImageCheck["if VulnerabilityScanner enabled<br/>pkg/k8s/scanner/scanner.go:96"]
        ParallelPipeline["parallel.NewPipeline(workers)<br/>pkg/k8s/scanner/scanner.go:129"]
        OnItem["onItem: scanVulns(ctx, artifact, opts)<br/>pkg/k8s/scanner/scanner.go:112"]
        RunnerScanImage["runner.ScanImage(ctx, opts)<br/>pkg/k8s/scanner/scanner.go:157"]
    end
    
    subgraph "Misconfiguration Scanning Path"
        MisconfigCheck["if ShouldScanMisconfigOrRbac<br/>pkg/k8s/scanner/scanner.go:87"]
        GenTempDir["generateTempDir(k8sArtifacts)<br/>pkg/k8s/scanner/scanner.go:176"]
        RunnerScanFS["runner.ScanFilesystem(ctx, opts)<br/>pkg/k8s/scanner/scanner.go:194"]
        CacheMemory["opts.CacheBackend = TypeMemory<br/>pkg/k8s/scanner/scanner.go:185"]
    end
    
    subgraph "Report Assembly"
        Resources["[]report.Resource"]
        ReportStruct["report.Report{<br/>ClusterName: s.cluster,<br/>Resources: resources<br/>}<br/>pkg/k8s/scanner/scanner.go:142"]
    end
    
    Artifacts --> ScanEntry
    ScanEntry --> FormatCheck
    ScanEntry --> ArtifactSplit
    ArtifactSplit --> WorkloadArtifacts
    ArtifactSplit --> K8sCoreArtifacts
    
    ScanEntry --> MisconfigCheck
    MisconfigCheck --> GenTempDir
    GenTempDir --> CacheMemory
    GenTempDir --> RunnerScanFS
    RunnerScanFS --> Resources
    
    ScanEntry --> ImageCheck
    ImageCheck --> ParallelPipeline
    ParallelPipeline --> OnItem
    OnItem --> RunnerScanImage
    RunnerScanImage --> Resources
    
    Resources --> ReportStruct
```

The `Scanner.Scan()` method in [pkg/k8s/scanner/scanner.go:55-148]() implements the core scanning logic. It first splits artifacts based on their `Kind` field—artifacts ending with "Components" or "Cluster" are treated as core infrastructure components, while others are workload resources [pkg/k8s/scanner/scanner.go:76-82]().

For workload resources with images, scanning uses `parallel.NewPipeline()` to process multiple artifacts concurrently [pkg/k8s/scanner/scanner.go:129](). The `workers` parameter is set to `opts.Parallel` unless `CacheBackend` is `TypeFS`, in which case it is limited to 1 to avoid bbolt lock contention [pkg/k8s/scanner/scanner.go:124-127]().

Misconfiguration scanning uses `generateTempDir()` to create temporary YAML files from artifact manifests [pkg/k8s/scanner/scanner.go:176](), then scans them as a filesystem. The cache backend is explicitly set to `TypeMemory` [pkg/k8s/scanner/scanner.go:185]() for this phase.

Sources: [pkg/k8s/scanner/scanner.go:55-148](), [pkg/k8s/scanner/scanner.go:150-173](), [pkg/k8s/scanner/scanner.go:175-221]()

## Core Components

### Scanner Type

The `scanner.Scanner` type in [pkg/k8s/scanner/scanner.go:41-45]() orchestrates Kubernetes cluster scanning:

```go
type Scanner struct {
	cluster string
	runner  cmd.Runner
	opts    flag.Options
}
```

The scanner is initialized via `NewScanner(cluster, runner, opts)` [pkg/k8s/scanner/scanner.go:47-53]() which stores the cluster name, a pre-configured artifact runner, and scanning options.

### Resource Collection System

Resource collection is handled by the `trivy-kubernetes` library through the `trivyk8s` package in `clusterRun` [pkg/k8s/commands/cluster.go:20]():

| Method | Purpose | Format Trigger |
|--------|---------|----------------|
| `ListClusterBomInfo(ctx)` | Collect resources for SBOM/BOM generation | `FormatCycloneDX` [pkg/k8s/commands/cluster.go:28]() |
| `ListArtifactAndNodeInfo(ctx)` | Collect workloads + deploy node-collector for infra scanning | `FormatJSON`/`Table` + Misconfig enabled [pkg/k8s/commands/cluster.go:41]() |
| `ListArtifacts(ctx)` | Collect workload resources without node-collector | Default fallback [pkg/k8s/commands/cluster.go:46]() |

Resource filtering is controlled through `K8sOptions` configured via CLI flags in `pkg/flag/kubernetes_flags.go`:
- `WithExcludeNamespaces(opts.ExcludeNamespaces)` [pkg/k8s/commands/cluster.go:34]()
- `WithIncludeNamespaces(opts.IncludeNamespaces)` [pkg/k8s/commands/cluster.go:35]()
- `WithExcludeKinds(opts.ExcludeKinds)` [pkg/k8s/commands/cluster.go:36]()
- `WithExcludeOwned(opts.ExcludeOwned)` [pkg/k8s/commands/cluster.go:38]()

Sources: [pkg/k8s/commands/cluster.go:20-61](), [pkg/flag/kubernetes_flags.go:46-81]()

### Scanning Workflows

#### Image Vulnerability Scanning

The `scanVulns()` method in [pkg/k8s/scanner/scanner.go:150-173]() scans container images found in Kubernetes resources:

1. **Image Extraction**: Iterates through `artifact.Images` slice.
2. **Registry Credentials**: Detects private registry credentials from workload `imagePullSecrets` or `serviceAccount` [pkg/k8s/scanner/scanner.go:101-111]().
3. **Image Scanning**: Calls `runner.ScanImage(ctx, opts)` for each image [pkg/k8s/scanner/scanner.go:157]().
4. **Result Transformation**: Converts the `types.Report` into a `report.Resource` via `report.CreateResource()` [pkg/k8s/scanner/scanner.go:160]().

#### Misconfiguration Scanning  

The `scanMisconfigs()` method in [pkg/k8s/scanner/scanner.go:175-221]() analyzes Kubernetes manifests:

1. **Temp Dir Creation**: `generateTempDir(k8sArtifacts)` creates temporary YAML files [pkg/k8s/scanner/scanner.go:176]().
2. **In-Memory Cache**: Temporarily sets `opts.CacheBackend = cache.TypeMemory` [pkg/k8s/scanner/scanner.go:185]().
3. **Filesystem Scan**: Calls `runner.ScanFilesystem(ctx, s.opts)` on the temporary directory [pkg/k8s/scanner/scanner.go:194]().
4. **Mapping**: Maps filesystem results back to original Kubernetes artifacts via `artifactsByFilename` [pkg/k8s/scanner/scanner.go:202]().

Sources: [pkg/k8s/scanner/scanner.go:150-173](), [pkg/k8s/scanner/scanner.go:175-221]()

## Configuration

Kubernetes scanning is configured through flags defined in [pkg/flag/kubernetes_flags.go]() and the `K8sFlagGroup` struct [pkg/flag/kubernetes_flags.go:96-112]().

### Connection and Performance Flags

| Flag | Config Name | Default | Description |
|------|-------------|---------|-------------|
| `--kubeconfig` | `kubernetes.kubeconfig` | (none) | Path to kubeconfig file [pkg/flag/kubernetes_flags.go:14]() |
| `--qps` | `kubernetes.qps` | `5.0` | Max QPS to API server [pkg/flag/kubernetes_flags.go:82]() |
| `--burst` | `kubernetes.burst` | `10` | Max burst for throttle [pkg/flag/kubernetes_flags.go:88]() |

### Node Collector Configuration

| Flag | Config Name | Default | Description |
|------|-------------|---------|-------------|
| `--disable-node-collector` | `kubernetes.disableNodeCollector` | `false` | Skip misconfig findings on node [pkg/flag/kubernetes_flags.go:29]() |
| `--node-collector-namespace` | `kubernetes.node-collector.namespace` | `trivy-temp` | Namespace for collector job [pkg/flag/kubernetes_flags.go:34]() |
| `--node-collector-imageref` | `kubernetes.node-collector.imageref` | `ghcr.io/aquasecurity/node-collector:0.3.1` | Collector image [pkg/flag/kubernetes_flags.go:40]() |
| `--tolerations` | `kubernetes.tolerations` | (none) | Node-collector job tolerations [pkg/flag/kubernetes_flags.go:24]() |

Sources: [pkg/flag/kubernetes_flags.go:14-94]()

## Report Generation

### Report Structure

The Kubernetes scanning system generates a `report.Report` [pkg/k8s/report/report.go:40-46]() containing multiple `Resource` entries:

```go
type Resource struct {
	Namespace string `json:",omitempty"`
	Kind      string
	Name      string
	Metadata  []types.Metadata `json:",omitempty"`
	Results   types.Results    `json:",omitempty"`
	Error     string           `json:",omitempty"`
}
```

### Report Separation

The `SeparateMisconfigReports` function [pkg/k8s/report/report.go:145-208]() categorizes findings into three assessment types:
1. **Workload Assessment**: General workload vulnerabilities and misconfigurations.
2. **Infra Assessment**: Infrastructure components and `kube-system` resources [pkg/k8s/report/report.go:221]().
3. **RBAC Assessment**: Specifically targets `Role`, `RoleBinding`, `ClusterRole`, and `ClusterRoleBinding` [pkg/k8s/report/report.go:210-217]().

### Table Output and Summary

The `TableWriter` [pkg/k8s/report/table.go:16-23]() supports two modes:
- `summary`: Uses `SummaryWriter` [pkg/k8s/report/summary.go:19-24]() to provide a high-level overview of vulnerabilities, misconfigurations, and secrets across namespaces.
- `all`: Outputs detailed tables for every resource found [pkg/k8s/report/table.go:56]().

The `SummaryWriter.Write()` method [pkg/k8s/report/summary.go:66-126]() aggregates severity counts for each finding using `accumulateSeverityCounts()` [pkg/k8s/report/summary.go:164-183]().

Sources: [pkg/k8s/report/report.go:40-66](), [pkg/k8s/report/report.go:145-208](), [pkg/k8s/report/table.go:54-82](), [pkg/k8s/report/summary.go:66-126]()

---

# Page: Repository and SBOM Scanning

# Repository and SBOM Scanning

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [integration/testdata/fixtures/sbom/minikube-kbom.json](integration/testdata/fixtures/sbom/minikube-kbom.json)
- [internal/gittest/server.go](internal/gittest/server.go)
- [internal/gittest/testdata/fixture.go](internal/gittest/testdata/fixture.go)
- [pkg/cache/client.go](pkg/cache/client.go)
- [pkg/cache/client_test.go](pkg/cache/client_test.go)
- [pkg/cache/dir.go](pkg/cache/dir.go)
- [pkg/downloader/downloader_test.go](pkg/downloader/downloader_test.go)
- [pkg/fanal/analyzer/sbom/sbom.go](pkg/fanal/analyzer/sbom/sbom.go)
- [pkg/fanal/analyzer/sbom/sbom_test.go](pkg/fanal/analyzer/sbom/sbom_test.go)
- [pkg/fanal/analyzer/sbom/testdata/ca-certificates.spdx.json](pkg/fanal/analyzer/sbom/testdata/ca-certificates.spdx.json)
- [pkg/fanal/analyzer/sbom/testdata/sbom-without-app-component.spdx.json](pkg/fanal/analyzer/sbom/testdata/sbom-without-app-component.spdx.json)
- [pkg/fanal/artifact/repo/git.go](pkg/fanal/artifact/repo/git.go)
- [pkg/fanal/artifact/repo/git_test.go](pkg/fanal/artifact/repo/git_test.go)
- [pkg/fanal/handler/unpackaged/unpackaged.go](pkg/fanal/handler/unpackaged/unpackaged.go)
- [pkg/k8s/k8s.go](pkg/k8s/k8s.go)
- [pkg/k8s/scanner/scanner_test.go](pkg/k8s/scanner/scanner_test.go)
- [pkg/plugin/index_test.go](pkg/plugin/index_test.go)
- [pkg/plugin/manager.go](pkg/plugin/manager.go)
- [pkg/plugin/manager_unix_test.go](pkg/plugin/manager_unix_test.go)
- [pkg/result/testdata/openvex.json](pkg/result/testdata/openvex.json)
- [pkg/sbom/core/bom.go](pkg/sbom/core/bom.go)
- [pkg/sbom/cyclonedx/testdata/happy/kbom.json](pkg/sbom/cyclonedx/testdata/happy/kbom.json)
- [pkg/sbom/cyclonedx/testdata/happy/nested-packages-bom.json](pkg/sbom/cyclonedx/testdata/happy/nested-packages-bom.json)
- [pkg/sbom/io/decode.go](pkg/sbom/io/decode.go)
- [pkg/sbom/io/decode_test.go](pkg/sbom/io/decode_test.go)
- [pkg/sbom/io/encode.go](pkg/sbom/io/encode.go)
- [pkg/sbom/io/encode_test.go](pkg/sbom/io/encode_test.go)
- [pkg/vex/csaf.go](pkg/vex/csaf.go)
- [pkg/vex/cyclonedx.go](pkg/vex/cyclonedx.go)
- [pkg/vex/openvex.go](pkg/vex/openvex.go)
- [pkg/vex/testdata/openvex-multiple.json](pkg/vex/testdata/openvex-multiple.json)
- [pkg/vex/testdata/openvex-oci.json](pkg/vex/testdata/openvex-oci.json)
- [pkg/vex/testdata/openvex.json](pkg/vex/testdata/openvex.json)
- [pkg/vex/testdata/unknown.json](pkg/vex/testdata/unknown.json)
- [pkg/vex/vex.go](pkg/vex/vex.go)
- [pkg/vex/vex_test.go](pkg/vex/vex_test.go)

</details>



This page describes how Trivy scans Git repositories and consumes SBOM (Software Bill of Materials) files for vulnerability analysis. Repository scanning analyzes source code for language-specific dependencies, while SBOM scanning imports existing documents (CycloneDX or SPDX) to perform vulnerability detection on the components they describe.

---

## Repository Scanning

### Overview
Repository scanning targets Git repositories (local or remote) to identify security issues in application dependencies. Unlike filesystem scanning, repository scanning focuses on application-level packages (libraries) found in lockfiles and manifests.

Trivy supports scanning remote repositories by cloning them to a temporary directory before analysis.

**Sources:** [pkg/fanal/artifact/repo/git.go:27-49](), [pkg/fanal/artifact/repo/git.go:63-85]()

### Git Repository Handling
Trivy uses the `go-git` library to handle repository operations. It supports various authentication methods and specific reference checkouts.

| Feature | Implementation Detail |
| :--- | :--- |
| **Remote Cloning** | Clones to a temporary directory using `xos.MkdirTemp`. |
| **Authentication** | Supports `GITHUB_TOKEN` and `GITLAB_TOKEN` environment variables via `BasicAuth`. |
| **References** | Can checkout specific branches (`--repo-branch`), tags (`--repo-tag`), or commit hashes (`--repo-commit`). |
| **Local Scanning** | If the target is a local path, Trivy skips cloning and uses the filesystem directly. |

**Sources:** [pkg/fanal/artifact/repo/git.go:87-139](), [pkg/fanal/artifact/repo/git.go:157-183](), [pkg/fanal/artifact/repo/git.go:51-61]()

### Repository Scan Workflow

```mermaid
sequenceDiagram
    participant CLI as "trivy repo"
    participant Artifact as "repo.NewArtifact"
    participant Git as "go-git.PlainClone"
    participant Walker as "walker.FS"
    participant Analyzer as "fanal/analyzer"

    CLI->>Artifact: Initialize with Target URL
    Artifact->>Git: cloneRepo (if remote)
    Git-->>Artifact: Temp Directory Path
    Artifact->>Walker: Walk(tempDir)
    Walker->>Analyzer: Analyze Lockfiles (Gemfile.lock, package-lock.json, etc.)
    Analyzer-->>Artifact: Return Package List
    Artifact-->>CLI: Return Reference
```

**Sources:** [pkg/fanal/artifact/repo/git.go:27-49](), [pkg/fanal/artifact/repo/git.go:87-139](), [pkg/fanal/artifact/repo/git_test.go:183-199]()

---

## SBOM Scanning

### Overview
SBOM scanning allows Trivy to consume existing SBOM files. This is used to re-scan components for new vulnerabilities or to convert between SBOM formats. Trivy acts as a "consumer" by decoding the SBOM into an internal representation.

**Sources:** [pkg/sbom/io/decode.go:51-86](), [pkg/fanal/analyzer/sbom/sbom.go:33-44]()

### The SBOM Analyzer
Trivy includes a dedicated `sbomAnalyzer` that automatically detects the format of an SBOM file (CycloneDX or SPDX) and decodes it.

- **Format Detection:** Uses `sbom.DetectFormat` on the file content.
- **Path Normalization:** To prevent overwriting packages when merging results, Trivy joins the SBOM internal package paths with the actual SBOM file path.
- **Bitnami Support:** Special handling is included for Bitnami-style SPDX files found in `/opt/bitnami/`.

**Sources:** [pkg/fanal/analyzer/sbom/sbom.go:33-58](), [pkg/fanal/analyzer/sbom/sbom.go:102-120]()

### Internal Data Flow: Decode to Core BOM
The `Decoder` class converts various SBOM formats into a unified `core.BOM` structure, which is then used for vulnerability matching.

```mermaid
graph TD
    subgraph "Input Space"
        InputFile["SBOM File (JSON/XML)"]
    end

    subgraph "Code Entity Space"
        SbomAnalyzer["sbom.sbomAnalyzer (pkg/fanal/analyzer/sbom/sbom.go)"]
        Decoder["io.Decoder (pkg/sbom/io/decode.go)"]
        CoreBOM["core.BOM (pkg/sbom/core/bom.go)"]
        PkgStruct["ftypes.Package (pkg/fanal/types/package.go)"]
    end

    InputFile --> SbomAnalyzer
    SbomAnalyzer -->|calls| Decoder
    Decoder -->|populates| CoreBOM
    CoreBOM -->|extracts| PkgStruct
    PkgStruct -->|used by| VulnDetector["Vulnerability Detector"]
```

**Sources:** [pkg/fanal/analyzer/sbom/sbom.go:33-44](), [pkg/sbom/io/decode.go:42-49](), [pkg/sbom/io/decode.go:123-156]()

### Dependency Graph Reconstruction
During decoding, Trivy reconstructs the dependency tree using PURLs and internal IDs.

1. **decodeComponents:** Iterates through all components in the SBOM.
2. **decodePackage:** Converts components to `ftypes.Package`, extracting PURLs and licenses.
3. **buildDependencyGraph:** Uses the relationships defined in the SBOM to populate the `DependsOn` field in the package structure.

**Sources:** [pkg/sbom/io/decode.go:118-156](), [pkg/sbom/io/decode.go:159-174]()

---

## VEX (Vulnerability Exploitability eXchange)
Trivy supports filtering scan results using VEX documents (OpenVEX, CSAF, or CycloneDX VEX). This allows users to suppress vulnerabilities that are not exploitable in their specific context.

### VEX Filtering Logic
When a VEX source is provided, Trivy performs the following:
1. **Encoding:** Encodes the current scan report into a `core.BOM` to build a parent-child relationship map.
2. **Filtering:** Iterates through detected vulnerabilities.
3. **Reachability Check:** Uses a Depth-First Search (`reachRoot`) to determine if a vulnerability statement in the VEX applies to the component path from the root.

```mermaid
graph TD
    subgraph "VEX Processing"
        VexFilter["vex.Filter (pkg/vex/vex.go)"]
        ReachRoot["vex.reachRoot (pkg/vex/vex.go)"]
        NotAffected["vex.NotAffected (pkg/vex/vex.go)"]
    end

    Report["types.Report"] --> VexFilter
    VexFilter -->|Builds Tree| CoreBOM["core.BOM"]
    VexFilter --> ReachRoot
    ReachRoot -->|Consults| NotAffected
    NotAffected -->|Checks Statement| VexDoc["VEX Document (OpenVEX/CSAF)"]
```

**Sources:** [pkg/vex/vex.go:69-91](), [pkg/vex/vex.go:148-175](), [pkg/vex/vex.go:178-219]()

### Supported VEX Sources
Trivy can retrieve VEX information from:
- **Local Files:** `--vex testdata/openvex.json`
- **OCI Registries:** Attached as OCI artifacts.
- **Git Repositories:** Remote VEX repositories.
- **SBOM References:** External references embedded within the scanned SBOM.

**Sources:** [pkg/vex/vex.go:18-23](), [pkg/vex/vex.go:93-137]()

---

## Technical Reference: Component Properties
When encoding or decoding SBOMs, Trivy uses standardized properties to preserve metadata.

| Property Name | Purpose |
| :--- | :--- |
| `ImageID` | The SHA256 ID of the container image. |
| `PkgID` | Unique identifier for a package (e.g., `name@version`). |
| `PkgType` | The ecosystem (e.g., `npm`, `maven`, `gobinary`). |
| `FilePath` | Location of the package or manifest within the artifact. |
| `LayerDiffID` | The specific image layer containing the package. |

**Sources:** [pkg/sbom/core/bom.go:26-56](), [pkg/sbom/io/encode.go:91-140]()

---

# Page: Infrastructure as Code Scanning

# Infrastructure as Code Scanning

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal/testutil/util.go](internal/testutil/util.go)
- [pkg/iac/adapters/cloudformation/aws/s3/bucket.go](pkg/iac/adapters/cloudformation/aws/s3/bucket.go)
- [pkg/iac/adapters/cloudformation/aws/s3/s3_test.go](pkg/iac/adapters/cloudformation/aws/s3/s3_test.go)
- [pkg/iac/adapters/terraform/aws/codebuild/adapt.go](pkg/iac/adapters/terraform/aws/codebuild/adapt.go)
- [pkg/iac/adapters/terraform/aws/ec2/adapt.go](pkg/iac/adapters/terraform/aws/ec2/adapt.go)
- [pkg/iac/adapters/terraform/aws/ec2/ami.go](pkg/iac/adapters/terraform/aws/ec2/ami.go)
- [pkg/iac/adapters/terraform/aws/ec2/ami_test.go](pkg/iac/adapters/terraform/aws/ec2/ami_test.go)
- [pkg/iac/adapters/terraform/aws/ec2/autoscaling.go](pkg/iac/adapters/terraform/aws/ec2/autoscaling.go)
- [pkg/iac/adapters/terraform/aws/ecr/adapt_test.go](pkg/iac/adapters/terraform/aws/ecr/adapt_test.go)
- [pkg/iac/adapters/terraform/aws/iam/convert.go](pkg/iac/adapters/terraform/aws/iam/convert.go)
- [pkg/iac/adapters/terraform/aws/iam/policies.go](pkg/iac/adapters/terraform/aws/iam/policies.go)
- [pkg/iac/adapters/terraform/aws/iam/policies_test.go](pkg/iac/adapters/terraform/aws/iam/policies_test.go)
- [pkg/iac/adapters/terraform/aws/iam/roles_test.go](pkg/iac/adapters/terraform/aws/iam/roles_test.go)
- [pkg/iac/adapters/terraform/aws/lambda/adapt.go](pkg/iac/adapters/terraform/aws/lambda/adapt.go)
- [pkg/iac/adapters/terraform/aws/s3/adapt_test.go](pkg/iac/adapters/terraform/aws/s3/adapt_test.go)
- [pkg/iac/adapters/terraform/aws/s3/bucket.go](pkg/iac/adapters/terraform/aws/s3/bucket.go)
- [pkg/iac/adapters/terraform/aws/sqs/adapt_test.go](pkg/iac/adapters/terraform/aws/sqs/adapt_test.go)
- [pkg/iac/adapters/terraform/tftestutil/testutil.go](pkg/iac/adapters/terraform/tftestutil/testutil.go)
- [pkg/iac/providers/aws/ec2/ami.go](pkg/iac/providers/aws/ec2/ami.go)
- [pkg/iac/providers/aws/ec2/ec2.go](pkg/iac/providers/aws/ec2/ec2.go)
- [pkg/iac/scanners/azure/arm/scanner.go](pkg/iac/scanners/azure/arm/scanner.go)
- [pkg/iac/scanners/azure/functions/intersection.go](pkg/iac/scanners/azure/functions/intersection.go)
- [pkg/iac/scanners/cloudformation/cftypes/types.go](pkg/iac/scanners/cloudformation/cftypes/types.go)
- [pkg/iac/scanners/cloudformation/parser/file_context.go](pkg/iac/scanners/cloudformation/parser/file_context.go)
- [pkg/iac/scanners/cloudformation/parser/fn_find_in_map.go](pkg/iac/scanners/cloudformation/parser/fn_find_in_map.go)
- [pkg/iac/scanners/cloudformation/parser/fn_find_in_map_test.go](pkg/iac/scanners/cloudformation/parser/fn_find_in_map_test.go)
- [pkg/iac/scanners/cloudformation/parser/fn_ref.go](pkg/iac/scanners/cloudformation/parser/fn_ref.go)
- [pkg/iac/scanners/cloudformation/parser/intrinsics.go](pkg/iac/scanners/cloudformation/parser/intrinsics.go)
- [pkg/iac/scanners/cloudformation/parser/parameter.go](pkg/iac/scanners/cloudformation/parser/parameter.go)
- [pkg/iac/scanners/cloudformation/parser/parser.go](pkg/iac/scanners/cloudformation/parser/parser.go)
- [pkg/iac/scanners/cloudformation/parser/parser_test.go](pkg/iac/scanners/cloudformation/parser/parser_test.go)
- [pkg/iac/scanners/cloudformation/parser/property.go](pkg/iac/scanners/cloudformation/parser/property.go)
- [pkg/iac/scanners/cloudformation/parser/resource.go](pkg/iac/scanners/cloudformation/parser/resource.go)
- [pkg/iac/scanners/cloudformation/parser/util.go](pkg/iac/scanners/cloudformation/parser/util.go)
- [pkg/iac/scanners/cloudformation/scanner.go](pkg/iac/scanners/cloudformation/scanner.go)
- [pkg/iac/scanners/dockerfile/parser/parser.go](pkg/iac/scanners/dockerfile/parser/parser.go)
- [pkg/iac/scanners/dockerfile/parser/parser_test.go](pkg/iac/scanners/dockerfile/parser/parser_test.go)
- [pkg/iac/scanners/dockerfile/scanner.go](pkg/iac/scanners/dockerfile/scanner.go)
- [pkg/iac/scanners/generic/scanner.go](pkg/iac/scanners/generic/scanner.go)
- [pkg/iac/scanners/helm/scanner.go](pkg/iac/scanners/helm/scanner.go)
- [pkg/iac/scanners/helm/test/option_test.go](pkg/iac/scanners/helm/test/option_test.go)
- [pkg/iac/scanners/helm/test/scanner_test.go](pkg/iac/scanners/helm/test/scanner_test.go)
- [pkg/iac/scanners/kubernetes/parser/manifest.go](pkg/iac/scanners/kubernetes/parser/manifest.go)
- [pkg/iac/scanners/kubernetes/parser/manifest_node.go](pkg/iac/scanners/kubernetes/parser/manifest_node.go)
- [pkg/iac/scanners/kubernetes/parser/manifest_test.go](pkg/iac/scanners/kubernetes/parser/manifest_test.go)
- [pkg/iac/scanners/kubernetes/parser/parser.go](pkg/iac/scanners/kubernetes/parser/parser.go)
- [pkg/iac/scanners/kubernetes/parser/parser_test.go](pkg/iac/scanners/kubernetes/parser/parser_test.go)
- [pkg/iac/scanners/kubernetes/scanner.go](pkg/iac/scanners/kubernetes/scanner.go)
- [pkg/iac/scanners/kubernetes/scanner_test.go](pkg/iac/scanners/kubernetes/scanner_test.go)
- [pkg/iac/scanners/terraform/count_test.go](pkg/iac/scanners/terraform/count_test.go)
- [pkg/iac/scanners/terraform/deterministic_test.go](pkg/iac/scanners/terraform/deterministic_test.go)
- [pkg/iac/scanners/terraform/executor/executor.go](pkg/iac/scanners/terraform/executor/executor.go)
- [pkg/iac/scanners/terraform/executor/option.go](pkg/iac/scanners/terraform/executor/option.go)
- [pkg/iac/scanners/terraform/ignore_test.go](pkg/iac/scanners/terraform/ignore_test.go)
- [pkg/iac/scanners/terraform/json_test.go](pkg/iac/scanners/terraform/json_test.go)
- [pkg/iac/scanners/terraform/module_test.go](pkg/iac/scanners/terraform/module_test.go)
- [pkg/iac/scanners/terraform/options.go](pkg/iac/scanners/terraform/options.go)
- [pkg/iac/scanners/terraform/parser/ctylist.go](pkg/iac/scanners/terraform/parser/ctylist.go)
- [pkg/iac/scanners/terraform/parser/ctylist_test.go](pkg/iac/scanners/terraform/parser/ctylist_test.go)
- [pkg/iac/scanners/terraform/parser/evaluator.go](pkg/iac/scanners/terraform/parser/evaluator.go)
- [pkg/iac/scanners/terraform/parser/load_module.go](pkg/iac/scanners/terraform/parser/load_module.go)
- [pkg/iac/scanners/terraform/parser/module_retrieval.go](pkg/iac/scanners/terraform/parser/module_retrieval.go)
- [pkg/iac/scanners/terraform/parser/option.go](pkg/iac/scanners/terraform/parser/option.go)
- [pkg/iac/scanners/terraform/parser/parser.go](pkg/iac/scanners/terraform/parser/parser.go)
- [pkg/iac/scanners/terraform/parser/parser_test.go](pkg/iac/scanners/terraform/parser/parser_test.go)
- [pkg/iac/scanners/terraform/parser/resolvers/cache.go](pkg/iac/scanners/terraform/parser/resolvers/cache.go)
- [pkg/iac/scanners/terraform/parser/resolvers/local.go](pkg/iac/scanners/terraform/parser/resolvers/local.go)
- [pkg/iac/scanners/terraform/parser/resolvers/options.go](pkg/iac/scanners/terraform/parser/resolvers/options.go)
- [pkg/iac/scanners/terraform/parser/resolvers/registry.go](pkg/iac/scanners/terraform/parser/resolvers/registry.go)
- [pkg/iac/scanners/terraform/parser/resolvers/registry_test.go](pkg/iac/scanners/terraform/parser/resolvers/registry_test.go)
- [pkg/iac/scanners/terraform/parser/resolvers/remote.go](pkg/iac/scanners/terraform/parser/resolvers/remote.go)
- [pkg/iac/scanners/terraform/parser/resolvers/source.go](pkg/iac/scanners/terraform/parser/resolvers/source.go)
- [pkg/iac/scanners/terraform/parser/resolvers/source_test.go](pkg/iac/scanners/terraform/parser/resolvers/source_test.go)
- [pkg/iac/scanners/terraform/parser/resolvers/testdata/terraform-aws-s3-bucket/README.md](pkg/iac/scanners/terraform/parser/resolvers/testdata/terraform-aws-s3-bucket/README.md)
- [pkg/iac/scanners/terraform/parser/resolvers/testdata/terraform-aws-s3-bucket/modules/notification/README.md](pkg/iac/scanners/terraform/parser/resolvers/testdata/terraform-aws-s3-bucket/modules/notification/README.md)
- [pkg/iac/scanners/terraform/parser/resolvers/testdata/terraform-aws-s3-bucket/modules/object/README.md](pkg/iac/scanners/terraform/parser/resolvers/testdata/terraform-aws-s3-bucket/modules/object/README.md)
- [pkg/iac/scanners/terraform/scanner.go](pkg/iac/scanners/terraform/scanner.go)
- [pkg/iac/scanners/terraformplan/tfjson/parser/block.go](pkg/iac/scanners/terraformplan/tfjson/parser/block.go)
- [pkg/iac/scanners/terraformplan/tfjson/parser/block_test.go](pkg/iac/scanners/terraformplan/tfjson/parser/block_test.go)
- [pkg/iac/scanners/terraformplan/tfjson/parser/parser.go](pkg/iac/scanners/terraformplan/tfjson/parser/parser.go)
- [pkg/iac/scanners/terraformplan/tfjson/parser/parser_test.go](pkg/iac/scanners/terraformplan/tfjson/parser/parser_test.go)
- [pkg/iac/scanners/terraformplan/tfjson/parser/plan_file.go](pkg/iac/scanners/terraformplan/tfjson/parser/plan_file.go)
- [pkg/iac/scanners/terraformplan/tfjson/scanner.go](pkg/iac/scanners/terraformplan/tfjson/scanner.go)
- [pkg/iac/scanners/terraformplan/tfjson/scanner_test.go](pkg/iac/scanners/terraformplan/tfjson/scanner_test.go)
- [pkg/iac/scanners/terraformplan/tfjson/testdata/arbitrary_name.json](pkg/iac/scanners/terraformplan/tfjson/testdata/arbitrary_name.json)
- [pkg/iac/scanners/terraformplan/tfjson/testdata/module_call.json](pkg/iac/scanners/terraformplan/tfjson/testdata/module_call.json)
- [pkg/iac/terraform/attribute.go](pkg/iac/terraform/attribute.go)
- [pkg/iac/terraform/attribute_test.go](pkg/iac/terraform/attribute_test.go)
- [pkg/iac/terraform/block.go](pkg/iac/terraform/block.go)
- [pkg/iac/terraform/context/context.go](pkg/iac/terraform/context/context.go)
- [pkg/iac/terraform/context/context_test.go](pkg/iac/terraform/context/context_test.go)
- [pkg/iac/terraform/module.go](pkg/iac/terraform/module.go)
- [pkg/iac/terraform/schema.go](pkg/iac/terraform/schema.go)

</details>



## Purpose and Scope

This page documents Trivy's standalone Infrastructure as Code (IaC) scanning capabilities, focusing on how Trivy parses, analyzes, and evaluates IaC configuration files. The primary focus is on Terraform/OpenTofu parsing and evaluation, which represents the most complex IaC scanning implementation.

For information about misconfiguration detection using policy engines, see [Misconfiguration Scanning](#4.2). For scanning IaC files as part of filesystem or repository scans, see [Filesystem and Rootfs Scanning](#5.2) and [Repository and SBOM Scanning](#5.4). For Kubernetes cluster analysis, see [Kubernetes Cluster Scanning](#5.3).

## Overview

Infrastructure as Code scanning in Trivy analyzes configuration files to identify security issues, compliance violations, and best practice deviations before infrastructure is deployed. The scanner supports multiple IaC formats, each with varying levels of parsing sophistication:

### Supported IaC Formats

| Format | File Extensions | Parsing Approach |
|--------|----------------|------------------|
| **Terraform/OpenTofu** | `.tf`, `.tf.json`, `.tofu`, `.tofu.json` | Full HCL parsing with module resolution, variable evaluation, and dynamic block expansion |
| **CloudFormation** | `.yaml`, `.yml`, `.json` (templates) | YAML/JSON parsing with parameter substitution via `--cf-params` |
| **Kubernetes Manifests** | `.yaml`, `.yml` | YAML parsing for resource definitions |
| **Helm Charts** | `Chart.yaml`, `values.yaml`, templates | Template rendering with `--helm-values`, `--helm-set` overrides |
| **Ansible Playbooks** | `.yaml`, `.yml` (playbooks) | YAML parsing with inventory and variable support via `--ansible-playbook`, `--ansible-inventory` |
| **Dockerfiles** | `Dockerfile`, `*.dockerfile` | Dockerfile instruction parsing |
| **Azure ARM Templates** | `.json` (ARM templates) | JSON template parsing |

### IaC Scanning Pipeline

The IaC scanning system operates in three main phases:

```mermaid
graph LR
    Input["IaC Files"]
    Parse["Parsing Phase<br/>parser.ParseFS()"]
    Eval["Evaluation Phase<br/>evaluator.EvaluateAll()"]
    Detect["Detection Phase<br/>(Rego policies)"]
    Output["Results"]
    
    Input --> Parse
    Parse --> Eval
    Eval --> Detect
    Detect --> Output
```

1. **Parsing Phase**: Reads configuration files from filesystem, parses syntax into blocks and attributes.
2. **Evaluation Phase**: Resolves variables, expands meta-arguments (`count`, `for_each`, `dynamic`), evaluates expressions, and loads child modules.
3. **Detection Phase**: Applies Rego policies to evaluated configuration (see [Misconfiguration Scanning](#4.2)).

Sources: [pkg/iac/scanners/terraform/parser/parser.go:156-210](), [pkg/iac/scanners/terraform/parser/evaluator.go:127-163](), [pkg/iac/scanners/terraform/executor/executor.go:41-105]()

## Terraform Parser Architecture

The Terraform parser is the core component responsible for parsing HCL (HashiCorp Configuration Language) and evaluating Terraform configurations.

### Parser Structure

```mermaid
graph TB
    Parser["parser.Parser"]
    HCLParser["hclparse.Parser"]
    Evaluator["parser.evaluator"]
    Context["tfcontext.Context"]
    Blocks["terraform.Blocks"]
    
    Parser -->|"underlying"| HCLParser
    Parser -->|"Load() creates"| Evaluator
    Evaluator -->|"ctx"| Context
    Evaluator -->|"blocks"| Blocks
    
    subgraph "Block Expansion"
        Count["evaluator.expandBlockCounts()"]
        ForEach["evaluator.expandBlockForEaches()"]
        Dynamic["Block.expandDynamic()"]
    end
    
    Evaluator --> Count
    Evaluator --> ForEach
    Evaluator --> Dynamic
```

The `parser.Parser` struct coordinates the overall parsing process:
- Uses `Parser.underlying` (`*hclparse.Parser`) for HCL syntax analysis [pkg/iac/scanners/terraform/parser/parser.go:46]().
- Creates `parser.evaluator` for semantic evaluation via `Parser.Load()` [pkg/iac/scanners/terraform/parser/parser.go:254-284]().
- Manages child modules in `Parser.children` [pkg/iac/scanners/terraform/parser/parser.go:47]().

Sources: [pkg/iac/scanners/terraform/parser/parser.go:34-58](), [pkg/iac/scanners/terraform/parser/evaluator.go:28-42]()

## File Parsing Workflow

### ParseFS: Directory Scanning

The `Parser.ParseFS()` method implements directory scanning:
1. Reads directory entries via `fs.ReadDir(p.moduleFS, dir)` [pkg/iac/scanners/terraform/parser/parser.go:170]().
2. Filters files by extension and skips directories [pkg/iac/scanners/terraform/parser/parser.go:176-180]().
3. Applies skip patterns via `utils.SkipPath` [pkg/iac/scanners/terraform/parser/parser.go:181-184]().
4. Invokes `Parser.ParseFile()` for each file [pkg/iac/scanners/terraform/parser/parser.go:190]().

Sources: [pkg/iac/scanners/terraform/parser/parser.go:156-210]()

### ParseFile: Individual File Parsing

The `Parser.ParseFile()` method processes individual Terraform files:
- Validates extensions (`.tf`, `.tf.json`, `.tofu`, `.tofu.json`) [pkg/iac/scanners/terraform/parser/parser.go:111-115]().
- Uses `p.underlying.ParseHCL` or `p.underlying.ParseJSON` [pkg/iac/scanners/terraform/parser/parser.go:139-142]().
- Appends successful results to `p.files` [pkg/iac/scanners/terraform/parser/parser.go:146-149]().

Sources: [pkg/iac/scanners/terraform/parser/parser.go:109-153]()

## Block and Attribute Representation

### Block Structure

The `Block` type represents a Terraform block with full context and metadata.

```mermaid
graph LR
    Block["terraform.Block"]
    Context["context.Context"]
    Metadata["types.Metadata"]
    Attribute["terraform.Attribute"]
    
    Block -->|"context"| Context
    Block -->|"metadata"| Metadata
    Block -->|"attributes"| Attribute
    Block -->|"childBlocks"| Block
```

Each block maintains its own evaluation context [pkg/iac/terraform/block.go:25](), metadata for location tracking [pkg/iac/terraform/block.go:32](), and a list of attributes [pkg/iac/terraform/block.go:31]().

Sources: [pkg/iac/terraform/block.go:22-36](), [pkg/iac/terraform/block.go:38-126]()

### Attribute Evaluation

Attributes wrap HCL expressions and provide methods to resolve values into Go types or `cty.Value`.

| Method | Return Type | Purpose |
|--------|-------------|---------|
| `Value()` | `cty.Value` | Evaluates the HCL expression in the block's context |
| `AsStringValueOrDefault()` | `types.StringValue` | Returns value as string or a default if nil/unresolvable |
| `AsBoolValueOrDefault()` | `types.BoolValue` | Returns value as boolean or a default |
| `IsLiteral()` | `bool` | Returns true if the expression contains no variables |

Sources: [pkg/iac/terraform/attribute.go:23-29](), [pkg/iac/terraform/attribute.go:132-143](), [pkg/iac/terraform/attribute.go:163-174](), [pkg/iac/terraform/attribute.go:190-195]()

## Module Resolution

### Module Loading Process

The evaluator loads modules defined in `module` blocks:
1. **Source Extraction**: Retrieves the `source` attribute [pkg/iac/scanners/terraform/parser/load_module.go:66-74]().
2. **Cache Check**: Attempts to resolve from `.terraform/modules/modules.json` if metadata is available [pkg/iac/scanners/terraform/parser/load_module.go:76-89]().
3. **External Resolution**: Uses `resolveModule` to download or locate modules from registry/git/local paths [pkg/iac/scanners/terraform/parser/load_module.go:131-152]().
4. **Parser Creation**: Creates a `newModuleParser` for the child module [pkg/iac/scanners/terraform/parser/load_module.go:160]().

Sources: [pkg/iac/scanners/terraform/parser/load_module.go:36-58](), [pkg/iac/scanners/terraform/parser/load_module.go:61-93]()

## Evaluation System

### Evaluation Context

The `evaluator` manages a `tfcontext.Context` which stores all variables, locals, and resources.

```mermaid
graph TB
    Evaluator["parser.evaluator"]
    Context["tfcontext.Context"]
    
    Evaluator -->|"ctx"| Context
    Context -->|"SetByDot"| PathVars["path.root, path.module, path.cwd"]
    Context -->|"Set"| BlockVars["var, local, provider, resource, data, module"]
```

The context is initialized with special variables like `path.module` and `path.root` [pkg/iac/scanners/terraform/parser/evaluator.go:68-70](). During `evaluateStep()`, it populates variables, locals, and resources into the context [pkg/iac/scanners/terraform/parser/evaluator.go:94-107]().

Sources: [pkg/iac/scanners/terraform/parser/evaluator.go:44-92](), [pkg/iac/scanners/terraform/parser/evaluator.go:94-107]()

### Iterative Evaluation

Evaluation is performed iteratively until values stabilize or `maxContextIterations` (32) is reached [pkg/iac/scanners/terraform/parser/evaluator.go:25]().

1. **Initial Evaluation**: Iteratively calls `evaluateStep()` [pkg/iac/scanners/terraform/parser/evaluator.go:136]().
2. **Expansion**: Expands `count`, `for_each`, and `dynamic` blocks [pkg/iac/scanners/terraform/parser/evaluator.go:142-143]().
3. **Submodule Evaluation**: Recursively evaluates child modules [pkg/iac/scanners/terraform/parser/evaluator.go:156]().
4. **Post-Evaluation**: Final evaluation pass to propagate module outputs [pkg/iac/scanners/terraform/parser/evaluator.go:159]().

Sources: [pkg/iac/scanners/terraform/parser/evaluator.go:127-163](), [pkg/iac/scanners/terraform/parser/evaluator.go:174-183]()

## Helm Chart Scanning

The Helm scanner renders charts into Kubernetes manifests before scanning them with the Rego engine.

```mermaid
graph LR
    Scanner["helm.Scanner"]
    Parser["helm/parser.Parser"]
    K8sParser["kubernetes/parser.Parse"]
    Rego["rego.Scanner"]
    
    Scanner -->|"ParseFS"| Parser
    Parser -->|"RenderedChartFiles"| Manifests["Manifest Content"]
    Manifests --> K8sParser
    K8sParser -->|"ToRego"| Rego
```

1. **Rendering**: `helmParser.RenderedChartFiles()` renders templates using provided values [pkg/iac/scanners/helm/scanner.go:109]().
2. **K8s Parsing**: Rendered manifests are parsed into `Manifest` objects [pkg/iac/scanners/helm/scanner.go:127]().
3. **Rego Scan**: Manifests are converted to Rego-compatible maps via `ToRego()` and scanned [pkg/iac/scanners/helm/scanner.go:141-145]().

Sources: [pkg/iac/scanners/helm/scanner.go:58-97](), [pkg/iac/scanners/helm/scanner.go:99-157](), [pkg/iac/scanners/kubernetes/parser/manifest_node.go:40-69]()

## Result Generation and Filtering

The `Executor` runs the final scan and applies filters/ignores.

- **Adaptation**: Terraform modules are adapted into a state representation for Rego [pkg/iac/scanners/terraform/executor/executor.go:44]().
- **Ignore Rules**: `results.Ignore(ignores, ignorers)` applies inline `#trivy:ignore` or `tfsec:ignore` rules [pkg/iac/scanners/terraform/executor/executor.go:84]().
- **Rendered Cause**: For failed results, `renderCause` extracts the relevant HCL snippet for the report [pkg/iac/scanners/terraform/executor/executor.go:100]().

Sources: [pkg/iac/scanners/terraform/executor/executor.go:41-105](), [pkg/iac/scanners/terraform/executor/executor.go:107-127]()

---

# Page: SBOM Generation and Consumption

# SBOM Generation and Consumption

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [integration/testdata/conda-cyclonedx.json.golden](integration/testdata/conda-cyclonedx.json.golden)
- [integration/testdata/conda-environment-cyclonedx.json.golden](integration/testdata/conda-environment-cyclonedx.json.golden)
- [integration/testdata/conda-spdx.json.golden](integration/testdata/conda-spdx.json.golden)
- [integration/testdata/fixtures/sbom/fluentd-multiple-lockfiles-cyclonedx.json](integration/testdata/fixtures/sbom/fluentd-multiple-lockfiles-cyclonedx.json)
- [integration/testdata/fixtures/sbom/minikube-kbom.json](integration/testdata/fixtures/sbom/minikube-kbom.json)
- [integration/testdata/fluentd-multiple-lockfiles-short.cdx.json.golden](integration/testdata/fluentd-multiple-lockfiles-short.cdx.json.golden)
- [integration/testdata/fluentd-multiple-lockfiles.cdx.json.golden](integration/testdata/fluentd-multiple-lockfiles.cdx.json.golden)
- [integration/testdata/julia-spdx.json.golden](integration/testdata/julia-spdx.json.golden)
- [integration/testdata/npm-cyclonedx.json.golden](integration/testdata/npm-cyclonedx.json.golden)
- [integration/testdata/pom-cyclonedx.json.golden](integration/testdata/pom-cyclonedx.json.golden)
- [pkg/fanal/analyzer/language/dart/pub/pubspec.go](pkg/fanal/analyzer/language/dart/pub/pubspec.go)
- [pkg/fanal/analyzer/language/julia/pkg/pkg.go](pkg/fanal/analyzer/language/julia/pkg/pkg.go)
- [pkg/fanal/analyzer/language/julia/pkg/pkg_test.go](pkg/fanal/analyzer/language/julia/pkg/pkg_test.go)
- [pkg/fanal/applier/docker.go](pkg/fanal/applier/docker.go)
- [pkg/fanal/applier/docker_test.go](pkg/fanal/applier/docker_test.go)
- [pkg/fanal/artifact/sbom/sbom.go](pkg/fanal/artifact/sbom/sbom.go)
- [pkg/k8s/scanner/scanner_test.go](pkg/k8s/scanner/scanner_test.go)
- [pkg/report/spdx/spdx.go](pkg/report/spdx/spdx.go)
- [pkg/result/testdata/openvex.json](pkg/result/testdata/openvex.json)
- [pkg/sbom/core/bom.go](pkg/sbom/core/bom.go)
- [pkg/sbom/cyclonedx/marshal.go](pkg/sbom/cyclonedx/marshal.go)
- [pkg/sbom/cyclonedx/marshal_test.go](pkg/sbom/cyclonedx/marshal_test.go)
- [pkg/sbom/cyclonedx/testdata/happy/bom.json](pkg/sbom/cyclonedx/testdata/happy/bom.json)
- [pkg/sbom/cyclonedx/testdata/happy/infinite-loop-bom.json](pkg/sbom/cyclonedx/testdata/happy/infinite-loop-bom.json)
- [pkg/sbom/cyclonedx/testdata/happy/kbom.json](pkg/sbom/cyclonedx/testdata/happy/kbom.json)
- [pkg/sbom/cyclonedx/testdata/happy/third-party-bom-no-os.json](pkg/sbom/cyclonedx/testdata/happy/third-party-bom-no-os.json)
- [pkg/sbom/cyclonedx/testdata/happy/third-party-bom.json](pkg/sbom/cyclonedx/testdata/happy/third-party-bom.json)
- [pkg/sbom/cyclonedx/unmarshal.go](pkg/sbom/cyclonedx/unmarshal.go)
- [pkg/sbom/cyclonedx/unmarshal_test.go](pkg/sbom/cyclonedx/unmarshal_test.go)
- [pkg/sbom/io/encode.go](pkg/sbom/io/encode.go)
- [pkg/sbom/io/encode_test.go](pkg/sbom/io/encode_test.go)
- [pkg/sbom/sbom.go](pkg/sbom/sbom.go)
- [pkg/sbom/sbom_test.go](pkg/sbom/sbom_test.go)
- [pkg/sbom/spdx/marshal.go](pkg/sbom/spdx/marshal.go)
- [pkg/sbom/spdx/marshal_test.go](pkg/sbom/spdx/marshal_test.go)
- [pkg/sbom/spdx/testdata/happy/with-file-as-relationship-parent.json](pkg/sbom/spdx/testdata/happy/with-file-as-relationship-parent.json)
- [pkg/sbom/spdx/unmarshal.go](pkg/sbom/spdx/unmarshal.go)
- [pkg/sbom/spdx/unmarshal_test.go](pkg/sbom/spdx/unmarshal_test.go)
- [pkg/vex/csaf.go](pkg/vex/csaf.go)
- [pkg/vex/cyclonedx.go](pkg/vex/cyclonedx.go)
- [pkg/vex/openvex.go](pkg/vex/openvex.go)
- [pkg/vex/testdata/openvex-multiple.json](pkg/vex/testdata/openvex-multiple.json)
- [pkg/vex/testdata/openvex-oci.json](pkg/vex/testdata/openvex-oci.json)
- [pkg/vex/testdata/openvex.json](pkg/vex/testdata/openvex.json)
- [pkg/vex/testdata/unknown.json](pkg/vex/testdata/unknown.json)
- [pkg/vex/vex.go](pkg/vex/vex.go)
- [pkg/vex/vex_test.go](pkg/vex/vex_test.go)
- [pkg/x/slices/slices.go](pkg/x/slices/slices.go)

</details>



This page explains how Trivy generates and consumes Software Bill of Materials (SBOM) documents. Trivy supports both generating SBOMs from scan results and consuming external SBOMs for vulnerability scanning.

For information about scanning specific targets like container images or filesystems, see [Target Types and Scanning Workflows](#5). For details about vulnerability detection after SBOM consumption, see [Vulnerability Detection](#4.1).

## Overview

Trivy implements bidirectional SBOM functionality:

- **Generation**: Converts scan results into standardized SBOM formats (CycloneDX, SPDX).
- **Consumption**: Reads external SBOMs and performs vulnerability scanning on the components.

All SBOM operations use an internal canonical representation (`core.BOM`) as an intermediate format, which provides a consistent data model regardless of the external format.

**Key Components:**
- `pkg/sbom/core/bom.go` — Canonical SBOM representation [pkg/sbom/core/bom.go:1-122]().
- `pkg/sbom/io/encode.go` — Report to `core.BOM` encoder [pkg/sbom/io/encode.go:45-57]().
- `pkg/sbom/cyclonedx/marshal.go` — CycloneDX marshaler [pkg/sbom/cyclonedx/marshal.go:42-55]().
- `pkg/sbom/cyclonedx/unmarshal.go` — CycloneDX unmarshaler [pkg/sbom/cyclonedx/unmarshal.go:25-27]().
- `pkg/sbom/spdx/marshal.go` — SPDX marshaler [pkg/sbom/spdx/marshal.go:102-115]().

## SBOM Generation and Consumption Flow

The following diagram illustrates the lifecycle of an SBOM within Trivy, showing the transformation from a scan report to standardized output and vice versa.

### Data Transformation Pipeline

```mermaid
graph TB
    subgraph "Generation Path"
        ScanResult["types.Report<br/>(Scan Results)"]
        Encoder["sbomio.Encoder.Encode()"]
        CoreBOM1["core.BOM<br/>(Canonical)"]
        Marshaler["Format Marshaler<br/>(CycloneDX/SPDX)"]
        OutputSBOM["External SBOM<br/>(JSON/XML)"]
        
        ScanResult --> Encoder
        Encoder --> CoreBOM1
        CoreBOM1 --> Marshaler
        Marshaler --> OutputSBOM
    end
    
    subgraph "Consumption Path"
        InputSBOM["External SBOM<br/>(JSON/XML)"]
        Unmarshaler["Format Unmarshaler<br/>(CycloneDX/SPDX)"]
        CoreBOM2["core.BOM<br/>(Canonical)"]
        TrivySBOM["types.SBOM"]
        VulnScan["Vulnerability Scanner"]
        
        InputSBOM --> Unmarshaler
        Unmarshaler --> CoreBOM2
        CoreBOM2 --> TrivySBOM
        TrivySBOM --> VulnScan
    end
```

**Sources:** [pkg/sbom/cyclonedx/marshal.go:58-90](), [pkg/sbom/cyclonedx/unmarshal.go:38-63](), [pkg/sbom/spdx/marshal.go:117-125]()

## Canonical BOM Representation

The `core.BOM` structure serves as the internal canonical format. This abstraction allows Trivy to support multiple SBOM formats without duplicating logic.

### Core BOM Structure

```mermaid
graph TD
    BOM["core.BOM"]
    Components["Components Map<br/>uuid.UUID → *Component"]
    Relationships["Relationships Map<br/>uuid.UUID → []Relationship"]
    Vulnerabilities["Vulnerabilities Map<br/>uuid.UUID → []Vulnerability"]
    
    BOM --> Components
    BOM --> Relationships
    BOM --> Vulnerabilities
    
    Component["core.Component<br/>- Name, Version<br/>- Type (Library/OS/App)<br/>- PURL<br/>- Properties"]
    
    Relationship["core.Relationship<br/>- Type (DependsOn/Contains)<br/>- Dependency uuid.UUID"]
    
    Vulnerability["core.Vulnerability<br/>- ID, Severity<br/>- InstalledVersion<br/>- FixedVersion"]
    
    Components --> Component
    Relationships --> Relationship
    Vulnerabilities --> Vulnerability
```

**Sources:** [pkg/sbom/core/bom.go:1-122](), [pkg/sbom/io/encode.go:232-234]()

## Generation Process

### From Scan Results to SBOM

The generation process converts a `types.Report` into an SBOM. The `sbomio.Encoder` extracts metadata, packages, and vulnerabilities into the `core.BOM` structure [pkg/sbom/io/encode.go:59-89]().

**Encoder Steps:**
1. **Create Root Component**: Maps `ArtifactType` to `core.ComponentType` (e.g., `ftypes.TypeContainerImage` to `core.TypeContainerImage`) [pkg/sbom/io/encode.go:91-140]().
2. **Process Results**: Iterates through `report.Results` to encode OS and Language packages [pkg/sbom/io/encode.go:182-219]().
3. **Build Relationships**: Establishes dependency links between the root component, application components, and individual packages [pkg/sbom/io/encode.go:221-250]().

**Sources:** [pkg/sbom/io/encode.go:59-250]()

### CycloneDX Marshaler

The `cyclonedx.Marshaler` converts the `core.BOM` into a CycloneDX compliant document. It handles the mapping of Trivy-specific attributes to CycloneDX properties using the `aquasecurity:trivy:` namespace [pkg/sbom/cyclonedx/marshal.go:69-90]().

For details, see [CycloneDX Format](#6.1).

### SPDX Marshaler

The `spdx.Marshaler` generates SPDX 2.3 documents. It maps Trivy artifacts to SPDX Packages and Files, using `NOASSERTION` for unknown licenses [pkg/sbom/spdx/marshal.go:127-202]().

For details, see [SPDX Format](#6.2).

## Consumption Process

### From SBOM to Scan Results

Trivy can consume external SBOMs for vulnerability scanning. The process involves unmarshaling the external format into `core.BOM` and then converting it into a format suitable for the scanner.

**Unmarshal Steps:**
1. **Parse BOM**: Decodes JSON/XML into format-specific structures (e.g., `cdx.BOM`) [pkg/sbom/cyclonedx/unmarshal.go:29-36]().
2. **Identify Origin**: `IsTrivySBOM()` checks if the document was generated by Trivy to ensure metadata completeness [pkg/sbom/cyclonedx/unmarshal.go:311-330]().
3. **Map Components**: Converts external components to `core.Component`, parsing PURLs and licenses [pkg/sbom/cyclonedx/unmarshal.go:172-208]().

**Sources:** [pkg/sbom/cyclonedx/unmarshal.go:38-105](), [pkg/sbom/cyclonedx/unmarshal.go:153-170]()

### Third-Party SBOM Detection

If a third-party SBOM is detected (one not containing Trivy's tool metadata), Trivy issues a warning as vulnerability detection may be less accurate without Trivy's internal identifiers [pkg/sbom/cyclonedx/unmarshal.go:49-52]().

## Package URL (PURL) Handling

PURLs are used as stable identifiers throughout the SBOM lifecycle.

### PURL Generation

During scanning, PURLs are generated for each package based on its ecosystem. In container images, `applier.ApplyLayers` ensures packages have correct layer metadata before PURL generation [pkg/fanal/applier/docker.go:214-225]().

**PURL as BOMRef:**
In CycloneDX output, the `bom-ref` (BOM reference) typically uses the PURL string for components with valid PURLs to ensure interoperability [pkg/sbom/cyclonedx/marshal.go:131-137]().

**Sources:** [pkg/fanal/applier/docker.go:214-229](), [pkg/sbom/cyclonedx/marshal.go:131-137]()

## Dependency Relationships

### Relationship Types

The `core.BOM` supports different relationship types defined in `pkg/sbom/core/bom.go`:

| Relationship | Description |
|--------------|-------------|
| `RelationshipContains` | Parent contains child (e.g., Image contains OS) [pkg/sbom/spdx/marshal.go:57](). |
| `RelationshipDependsOn` | Component depends on another (e.g., Library A depends on B) [pkg/sbom/spdx/marshal.go:59](). |
| `RelationshipDescribe` | Document describes the root component [pkg/sbom/spdx/marshal.go:58](). |

**Sources:** [pkg/sbom/spdx/marshal.go:57-59](), [pkg/sbom/cyclonedx/marshal.go:167-185]()

## VEX (Vulnerability Exploitability eXchange)

Trivy supports VEX to filter vulnerabilities based on exploitability statements. VEX information can be embedded in SBOMs or provided as external files (OpenVEX, CSAF, CycloneDX VEX) [pkg/vex/vex.go:34-45]().

**VEX Filtering Flow:**
- `vex.Filter()` uses VEX sources to modify the `types.Report` [pkg/vex/vex_test.go:184-210]().
- Vulnerabilities are moved to `ModifiedFindings` if a VEX statement indicates they are not affected [pkg/vex/vex_test.go:221-226]().

**Sources:** [pkg/vex/vex.go](), [pkg/vex/vex_test.go:221-226]()

---

# Page: CycloneDX Format

# CycloneDX Format

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [integration/testdata/conda-cyclonedx.json.golden](integration/testdata/conda-cyclonedx.json.golden)
- [integration/testdata/conda-environment-cyclonedx.json.golden](integration/testdata/conda-environment-cyclonedx.json.golden)
- [integration/testdata/fixtures/sbom/fluentd-multiple-lockfiles-cyclonedx.json](integration/testdata/fixtures/sbom/fluentd-multiple-lockfiles-cyclonedx.json)
- [integration/testdata/fixtures/sbom/minikube-kbom.json](integration/testdata/fixtures/sbom/minikube-kbom.json)
- [integration/testdata/fluentd-multiple-lockfiles-short.cdx.json.golden](integration/testdata/fluentd-multiple-lockfiles-short.cdx.json.golden)
- [integration/testdata/fluentd-multiple-lockfiles.cdx.json.golden](integration/testdata/fluentd-multiple-lockfiles.cdx.json.golden)
- [integration/testdata/npm-cyclonedx.json.golden](integration/testdata/npm-cyclonedx.json.golden)
- [integration/testdata/pom-cyclonedx.json.golden](integration/testdata/pom-cyclonedx.json.golden)
- [pkg/fanal/applier/docker.go](pkg/fanal/applier/docker.go)
- [pkg/fanal/applier/docker_test.go](pkg/fanal/applier/docker_test.go)
- [pkg/fanal/artifact/sbom/sbom.go](pkg/fanal/artifact/sbom/sbom.go)
- [pkg/k8s/report/cyclonedx.go](pkg/k8s/report/cyclonedx.go)
- [pkg/k8s/scanner/scanner_test.go](pkg/k8s/scanner/scanner_test.go)
- [pkg/report/cyclonedx/cyclonedx.go](pkg/report/cyclonedx/cyclonedx.go)
- [pkg/result/testdata/openvex.json](pkg/result/testdata/openvex.json)
- [pkg/sbom/core/bom.go](pkg/sbom/core/bom.go)
- [pkg/sbom/cyclonedx/marshal.go](pkg/sbom/cyclonedx/marshal.go)
- [pkg/sbom/cyclonedx/marshal_test.go](pkg/sbom/cyclonedx/marshal_test.go)
- [pkg/sbom/cyclonedx/testdata/happy/bom.json](pkg/sbom/cyclonedx/testdata/happy/bom.json)
- [pkg/sbom/cyclonedx/testdata/happy/infinite-loop-bom.json](pkg/sbom/cyclonedx/testdata/happy/infinite-loop-bom.json)
- [pkg/sbom/cyclonedx/testdata/happy/kbom.json](pkg/sbom/cyclonedx/testdata/happy/kbom.json)
- [pkg/sbom/cyclonedx/testdata/happy/third-party-bom-no-os.json](pkg/sbom/cyclonedx/testdata/happy/third-party-bom-no-os.json)
- [pkg/sbom/cyclonedx/testdata/happy/third-party-bom.json](pkg/sbom/cyclonedx/testdata/happy/third-party-bom.json)
- [pkg/sbom/cyclonedx/unmarshal.go](pkg/sbom/cyclonedx/unmarshal.go)
- [pkg/sbom/cyclonedx/unmarshal_test.go](pkg/sbom/cyclonedx/unmarshal_test.go)
- [pkg/sbom/io/encode.go](pkg/sbom/io/encode.go)
- [pkg/sbom/io/encode_test.go](pkg/sbom/io/encode_test.go)
- [pkg/sbom/sbom.go](pkg/sbom/sbom.go)
- [pkg/sbom/sbom_test.go](pkg/sbom/sbom_test.go)
- [pkg/vex/csaf.go](pkg/vex/csaf.go)
- [pkg/vex/cyclonedx.go](pkg/vex/cyclonedx.go)
- [pkg/vex/openvex.go](pkg/vex/openvex.go)
- [pkg/vex/testdata/openvex-multiple.json](pkg/vex/testdata/openvex-multiple.json)
- [pkg/vex/testdata/openvex-oci.json](pkg/vex/testdata/openvex-oci.json)
- [pkg/vex/testdata/openvex.json](pkg/vex/testdata/openvex.json)
- [pkg/vex/testdata/unknown.json](pkg/vex/testdata/unknown.json)
- [pkg/vex/vex.go](pkg/vex/vex.go)
- [pkg/vex/vex_test.go](pkg/vex/vex_test.go)
- [pkg/x/slices/slices.go](pkg/x/slices/slices.go)

</details>



## Purpose and Scope

This document describes Trivy's implementation of the CycloneDX SBOM format for both generation and consumption. CycloneDX is a standardized format for Software Bill of Materials (SBOM) that enables vulnerability tracking, license compliance, and dependency management across the software supply chain. Trivy supports the CycloneDX version 1.6 specification.

For information about SPDX format (the alternative SBOM format), see [SPDX Format](6.2). For general SBOM generation and consumption workflows, see [SBOM Generation and Consumption](6).

## Architecture Overview

Trivy's CycloneDX implementation consists of two primary components: marshaling (generating CycloneDX from scan results) and unmarshaling (consuming external CycloneDX SBOMs).

Trivy uses an intermediate representation `*core.BOM` [pkg/sbom/core/bom.go]() to bridge between the internal `types.Report` and the final `cdx.BOM` structure provided by the `github.com/CycloneDX/cyclonedx-go` library.

Title: CycloneDX Data Flow
```mermaid
graph TB
    subgraph "Input Sources"
        Report["types.Report"]
        ExternalBOM["External CycloneDX JSON"]
    end
    
    subgraph "Core BOM System"
        CoreBOM["*core.BOM"]
        Encoder["sbomio.Encoder"]
    end
    
    subgraph "pkg/sbom/cyclonedx"
        Marshaler["Marshaler struct<br/>appVersion string<br/>bom *core.BOM<br/>componentIDs map"]
        UnmarshalJSON["BOM.UnmarshalJSON()"]
        DecodeJSON["DecodeJSON()"]
        CDXMarshaler["NewMarshaler()"]
    end
    
    subgraph "CycloneDX Library"
        CDXBOMStruct["cdx.BOM"]
        BOMEncoder["cdx.BOMEncoder"]
        BOMDecoder["cdx.BOMDecoder"]
    end
    
    subgraph "Output"
        CDXOutput["CycloneDX JSON/XML"]
        InternalSBOM["types.SBOM"]
    end
    
    Report --> Encoder
    Encoder --> CoreBOM
    CoreBOM --> CDXMarshaler
    CDXMarshaler --> Marshaler
    Marshaler --> CDXBOMStruct
    CDXBOMStruct --> BOMEncoder
    BOMEncoder --> CDXOutput
    
    ExternalBOM --> DecodeJSON
    DecodeJSON --> BOMDecoder
    BOMDecoder --> UnmarshalJSON
    UnmarshalJSON --> CoreBOM
    CoreBOM --> InternalSBOM
```
Sources: [pkg/sbom/cyclonedx/marshal.go:42-90](), [pkg/sbom/cyclonedx/unmarshal.go:29-63](), [pkg/sbom/io/encode.go:59-89]()

## Marshaling Process

### Core Marshaling Flow

The `Marshaler` struct converts Trivy's internal representation to CycloneDX format. It maintains a `componentIDs` map to track `uuid.UUID` to `BOM-Ref` mappings for dependency graph consistency.

Title: Marshaler Logic Space
```mermaid
graph TB
    subgraph "Marshaler struct"
        M["Marshaler<br/>appVersion string<br/>bom *core.BOM<br/>componentIDs map[uuid.UUID]string<br/>logger *log.Logger"]
    end
    
    subgraph "Entry Points"
        MarshalReport["MarshalReport(ctx, report)<br/>lines 58-66"]
        Marshal["Marshal(ctx, bom)<br/>lines 69-90"]
    end
    
    subgraph "Component Processing"
        MarshalRoot["MarshalRoot()<br/>lines 109-117"]
        MarshalComponent["MarshalComponent()<br/>lines 119-140"]
        marshalComponents["marshalComponents()<br/>lines 142-165"]
    end
    
    subgraph "Relationship Processing"
        marshalDependencies["marshalDependencies()<br/>lines 167-192"]
        marshalVulnerabilities["marshalVulnerabilities()<br/>lines 194-232"]
    end
    
    subgraph "Helper Methods"
        Metadata["Metadata()<br/>lines 92-107"]
        componentType["componentType()<br/>lines 234-249"]
        PackageURL["PackageURL()<br/>lines 251-256"]
        Licenses["Licenses()<br/>lines 300-306"]
        Properties["Properties()<br/>lines 361-381"]
    end
    
    MarshalReport --> Marshal
    Marshal --> Metadata
    Marshal --> MarshalRoot
    Marshal --> marshalComponents
    Marshal --> marshalDependencies
    Marshal --> marshalVulnerabilities
    
    marshalComponents --> MarshalComponent
    MarshalComponent --> componentType
    MarshalComponent --> PackageURL
    MarshalComponent --> Licenses
    MarshalComponent --> Properties
```
Sources: [pkg/sbom/cyclonedx/marshal.go:42-381]()

### Component Type Mapping

Trivy's internal `core.ComponentType` is mapped to CycloneDX `cdx.ComponentType` via the `componentType()` function:

| Core Component Type | CycloneDX Type |
|---------------------|----------------|
| `core.TypeContainerImage` | `cdx.ComponentTypeContainer` |
| `core.TypeVM` | `cdx.ComponentTypeContainer` |
| `core.TypeApplication` | `cdx.ComponentTypeApplication` |
| `core.TypeFilesystem` | `cdx.ComponentTypeApplication` |
| `core.TypeRepository` | `cdx.ComponentTypeApplication` |
| `core.TypeLibrary` | `cdx.ComponentTypeLibrary` |
| `core.TypeOS` | `cdx.ComponentTypeOS` |
| `core.TypePlatform` | `cdx.ComponentTypePlatform` |

Sources: [pkg/sbom/cyclonedx/marshal.go:234-249]()

### Metadata Generation

The `Metadata()` method populates the CycloneDX metadata block, identifying Trivy as the generating tool. It uses constants defined in [pkg/sbom/cyclonedx/marshal.go:32-37]():
- `ToolVendor`: "aquasecurity"
- `ToolName`: "trivy"
- `ToolManufacturer`: "Aqua Security Software Ltd."

Sources: [pkg/sbom/cyclonedx/marshal.go:92-107]()

### License Normalization

Trivy normalizes license strings into CycloneDX `LicenseChoice` objects. It handles both individual SPDX identifiers and complex compound expressions.

Title: License Processing Pipeline
```mermaid
graph TB
    Licenses["Licenses(licenses []string)<br/>lines 300-306"]
    normalizeLicenses["normalizeLicenses(licenses []string)<br/>lines 308-337"]
    normalizeLicense["normalizeLicense(license string)<br/>lines 339-359"]
    
    subgraph "Per-License Processing"
        CheckPrefix["Check licensing.LicenseTextPrefix<br/>line 341"]
        SimpleExpr["Return SimpleExpr{License: after}"]
        ReplaceWith["Replace '-with-' → ' WITH '<br/>lines 348-349"]
        Normalize["expression.Normalize()<br/>licensing.NormalizeLicenseExpression<br/>expression.NormalizeForSPDX<br/>lines 351"]
    end
    
    subgraph "Aggregation Logic"
        MapExprs["xslices.Map to expression.Expression<br/>line 309"]
        CheckAllValidSPDX["lo.EveryBy(expr.IsSPDXExpression())<br/>lines 311-313"]
        CheckCompound["lo.ContainsBy(is CompoundExpr)<br/>lines 316-319"]
        BothTrue{"AllValidSPDX AND<br/>HasCompoundExpr?"}
        JoinExpression["Single Expression<br/>Join with ' AND '<br/>line 324"]
        IndividualChoices["Individual LicenseChoice<br/>Use ID if valid SPDX<br/>else Name<br/>lines 328-336"]
    end
    
    Licenses --> normalizeLicenses
    normalizeLicenses --> normalizeLicense
    normalizeLicense --> CheckPrefix
    CheckPrefix -->|Has prefix| SimpleExpr
    CheckPrefix -->|No prefix| ReplaceWith
    ReplaceWith --> Normalize
    
    MapExprs --> CheckAllValidSPDX
    MapExprs --> CheckCompound
    CheckAllValidSPDX --> BothTrue
    CheckCompound --> BothTrue
    BothTrue -->|Yes| JoinExpression
    BothTrue -->|No| IndividualChoices
```
Sources: [pkg/sbom/cyclonedx/marshal.go:300-359]()

### Vulnerability Aggregation

Trivy aggregates vulnerabilities by ID. If multiple components (packages) are affected by the same CVE, they are grouped under a single `cdx.Vulnerability` entry using the `Affects` field.

Title: Vulnerability Aggregation Flow
```mermaid
graph TB
    marshalVulnerabilities["marshalVulnerabilities()<br/>lines 194-232"]
    
    subgraph "Aggregation Logic"
        vulnMap["vulns := make(map[string]*cdx.Vulnerability)<br/>line 195"]
        CheckExists{"vuln, ok := vulns[v.ID]"}
        AppendAffects["*vuln.Affects = append(...)<br/>line 204"]
        UpdateRec["Update Recommendation<br/>(concatenate upgrade strings)<br/>lines 205-214"]
        CreateNew["marshalVulnerability(bomRef, v)<br/>lines 427-449"]
    end
    
    marshalVulnerabilities --> Iterate["Iterate bom.Vulnerabilities()"]
    Iterate --> CheckExists
    CheckExists -->|Yes| AppendAffects
    AppendAffects --> UpdateRec
    CheckExists -->|No| CreateNew
```
Sources: [pkg/sbom/cyclonedx/marshal.go:194-232](), [pkg/sbom/cyclonedx/marshal.go:427-449]()

## Unmarshaling Process

### Decoding and Parsing Flow

Unmarshaling converts CycloneDX JSON back into Trivy's `core.BOM`. This is used when scanning an existing SBOM file for vulnerabilities.

Title: Unmarshaler Code Entity Space
```mermaid
graph TB
    UnmarshalJSON["BOM.UnmarshalJSON(data []byte)<br/>lines 38-63"]
    DecodeJSON["DecodeJSON(r io.Reader)<br/>lines 29-36"]
    parseBOM["parseBOM(bom *cdx.BOM)<br/>lines 65-105"]
    
    subgraph "Component Parsing"
        parseComponents["parseComponents(bom.Components)<br/>lines 153-170"]
        parseMetadataComponent["parseMetadataComponent(bom)<br/>lines 107-118"]
        parseComponent["parseComponent(c cdx.Component)<br/>lines 172-208"]
    end
    
    subgraph "Relationship Building"
        IterateDeps["Iterate bom.Dependencies<br/>lines 78-98"]
        AddRel["b.BOM.AddRelationship()<br/>lines 87, 95"]
    end
    
    UnmarshalJSON --> DecodeJSON
    DecodeJSON --> parseBOM
    parseBOM --> parseComponents
    parseBOM --> parseMetadataComponent
    parseComponents --> parseComponent
    parseMetadataComponent --> parseComponent
    parseBOM --> IterateDeps
    IterateDeps --> AddRel
```
Sources: [pkg/sbom/cyclonedx/unmarshal.go:29-105]()

### Third-Party SBOM Detection

Trivy checks the metadata tools section to see if the SBOM was generated by Trivy. If not, it logs a warning that detection might be less accurate.

Title: IsTrivySBOM Validation
```mermaid
graph TD
    IsTrivySBOM["IsTrivySBOM(c *cdx.BOM) bool<br/>lines 311-330"]
    
    subgraph "Validation"
        CheckTools["Check c.Metadata.Tools.Components<br/>(v1.5+ style)"]
        CheckLegacy["Check c.Metadata.Tools.Tools<br/>(Deprecated style)"]
    end
    
    IsTrivySBOM --> CheckTools
    CheckTools -->|Not Found| CheckLegacy
```
Sources: [pkg/sbom/cyclonedx/unmarshal.go:311-330]()

## Property Handling

Trivy uses CycloneDX properties to store additional metadata (e.g., Image ID, Layer DiffID). Properties are namespaced with `aquasecurity:trivy:` to avoid collisions with other tools.

- **Marshaling**: Prepends the namespace to internal property names unless `External` is true [pkg/sbom/cyclonedx/marshal.go:361-381]().
- **Unmarshaling**: Strips the namespace if present to restore the internal name and sets `External: false` [pkg/sbom/cyclonedx/unmarshal.go:289-309]().

Sources: [pkg/sbom/cyclonedx/marshal.go:36-37](), [pkg/sbom/cyclonedx/marshal.go:361-381](), [pkg/sbom/cyclonedx/unmarshal.go:289-309]()

## Dependency Graph

CycloneDX uses a separate `dependencies` array where each element contains a `ref` (pointing to a component's `bom-ref`) and a list of `dependsOn` refs.

- **Marshaling**: `marshalDependencies()` iterates over `bom.Relationships()` and maps internal IDs to `bom-ref` strings [pkg/sbom/cyclonedx/marshal.go:167-192]().
- **Unmarshaling**: `parseBOM()` iterates over the `Dependencies` array. If a component has an empty `dependsOn` list, Trivy creates a relationship to `nil` to explicitly mark it as having no dependencies [pkg/sbom/cyclonedx/unmarshal.go:78-98]().

Sources: [pkg/sbom/cyclonedx/marshal.go:167-192](), [pkg/sbom/cyclonedx/unmarshal.go:78-98]()

---

# Page: SPDX Format

# SPDX Format

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [integration/testdata/conda-spdx.json.golden](integration/testdata/conda-spdx.json.golden)
- [integration/testdata/julia-spdx.json.golden](integration/testdata/julia-spdx.json.golden)
- [pkg/fanal/analyzer/language/dart/pub/pubspec.go](pkg/fanal/analyzer/language/dart/pub/pubspec.go)
- [pkg/fanal/analyzer/language/julia/pkg/pkg.go](pkg/fanal/analyzer/language/julia/pkg/pkg.go)
- [pkg/fanal/analyzer/language/julia/pkg/pkg_test.go](pkg/fanal/analyzer/language/julia/pkg/pkg_test.go)
- [pkg/fanal/analyzer/sbom/sbom.go](pkg/fanal/analyzer/sbom/sbom.go)
- [pkg/fanal/analyzer/sbom/sbom_test.go](pkg/fanal/analyzer/sbom/sbom_test.go)
- [pkg/fanal/analyzer/sbom/testdata/ca-certificates.spdx.json](pkg/fanal/analyzer/sbom/testdata/ca-certificates.spdx.json)
- [pkg/fanal/analyzer/sbom/testdata/sbom-without-app-component.spdx.json](pkg/fanal/analyzer/sbom/testdata/sbom-without-app-component.spdx.json)
- [pkg/fanal/handler/unpackaged/unpackaged.go](pkg/fanal/handler/unpackaged/unpackaged.go)
- [pkg/report/spdx/spdx.go](pkg/report/spdx/spdx.go)
- [pkg/sbom/cyclonedx/testdata/happy/nested-packages-bom.json](pkg/sbom/cyclonedx/testdata/happy/nested-packages-bom.json)
- [pkg/sbom/io/decode.go](pkg/sbom/io/decode.go)
- [pkg/sbom/io/decode_test.go](pkg/sbom/io/decode_test.go)
- [pkg/sbom/spdx/marshal.go](pkg/sbom/spdx/marshal.go)
- [pkg/sbom/spdx/marshal_test.go](pkg/sbom/spdx/marshal_test.go)
- [pkg/sbom/spdx/testdata/happy/with-file-as-relationship-parent.json](pkg/sbom/spdx/testdata/happy/with-file-as-relationship-parent.json)
- [pkg/sbom/spdx/unmarshal.go](pkg/sbom/spdx/unmarshal.go)
- [pkg/sbom/spdx/unmarshal_test.go](pkg/sbom/spdx/unmarshal_test.go)

</details>



## Purpose and Scope

This document details Trivy's SPDX (Software Package Data Exchange) format support for SBOM generation and consumption. SPDX is an ISO/IEC standard format for communicating software bill of materials and associated information. For information about CycloneDX SBOM format, see [CycloneDX Format](6.1). For the overall report generation system, see [Report Generation and Output](7).

Trivy supports SPDX as both an **output** format for generating SBOMs and an **input** format for vulnerability scanning. It supports SPDX 2.3 in both JSON and Tag-Value serializations.

---

## SPDX in the Report Writer System

The SPDX writer is integrated into Trivy's report generation pipeline. It transforms a `types.Report` into an SPDX document by first encoding it into an intermediate `core.BOM` representation.

### Format Selection and Generation Flow

```mermaid
graph TD
    subgraph "Report Generation [pkg/report/spdx/spdx.go]"
        Writer["Writer.Write(ctx, report)"]
        NewMarshaler["spdx.NewMarshaler(version)"]
        MarshalReport["Marshaler.MarshalReport(ctx, report)"]
    end

    subgraph "Intermediate Representation [pkg/sbom/io/marshal.go]"
        Encoder["io.NewEncoder().Encode(report)"]
        CoreBOM["core.BOM struct"]
    end

    subgraph "SPDX Transformation [pkg/sbom/spdx/marshal.go]"
        Marshal["Marshaler.Marshal(ctx, bom)"]
        RootPkg["m.rootSPDXPackage()"]
        SPDXPkg["m.spdxPackage()"]
        SPDXDoc["spdx.Document (tools-golang)"]
    end

    Writer --> NewMarshaler
    Writer --> MarshalReport
    MarshalReport --> Encoder
    Encoder --> CoreBOM
    MarshalReport --> Marshal
    Marshal --> RootPkg
    Marshal --> SPDXPkg
    RootPkg --> SPDXDoc
    SPDXPkg --> SPDXDoc
```

**Sources:** [pkg/report/spdx/spdx.go:32-49](), [pkg/sbom/spdx/marshal.go:117-125](), [pkg/sbom/spdx/marshal.go:127-152]()

---

## SPDX Consumption (Decoding)

Trivy can consume SPDX files to perform vulnerability scans on the components listed within them. This is handled by the `sbomAnalyzer` which detects the format and uses the SPDX decoder.

### SPDX Decoding Architecture

The decoding process converts an SPDX document back into Trivy's internal `types.SBOM` structure.

```mermaid
graph TB
    subgraph "Analyzer Layer [pkg/fanal/analyzer/sbom/sbom.go]"
        Analyze["sbomAnalyzer.Analyze()"]
        Detect["sbom.DetectFormat()"]
        DecodeCall["sbom.Decode()"]
    end

    subgraph "SPDX Unmarshaling [pkg/sbom/spdx/unmarshal.go]"
        SPDXStruct["spdx.SPDX struct"]
        Unmarshal["SPDX.unmarshal(spdxDocument)"]
        ParsePackages["SPDX.parsePackages()"]
        ParseRels["SPDX.parseRelationships()"]
    end

    subgraph "Internal Conversion [pkg/sbom/io/decode.go]"
        Decoder["io.Decoder.Decode()"]
        DecodeComp["Decoder.decodeComponents()"]
        BuildGraph["Decoder.buildDependencyGraph()"]
    end

    Analyze --> Detect
    Analyze --> DecodeCall
    DecodeCall --> Unmarshal
    Unmarshal --> ParsePackages
    Unmarshal --> ParseRels
    DecodeCall --> Decoder
    Decoder --> DecodeComp
    Decoder --> BuildGraph
```

**Sources:** [pkg/fanal/analyzer/sbom/sbom.go:33-44](), [pkg/sbom/spdx/unmarshal.go:68-105](), [pkg/sbom/io/decode.go:51-86]()

### Package Identification and Metadata
During unmarshaling, Trivy maps SPDX fields to its internal component model:
- **PURL**: Extracted from `ExternalRef` with category `PACKAGE-MANAGER` and type `purl` [pkg/sbom/spdx/unmarshal.go:171-173]().
- **Properties**: Recovered from SPDX `Annotations` or `AttributionTexts` to maintain backward compatibility [pkg/sbom/spdx/unmarshal.go:202-220]().
- **Relationships**: Maps `CONTAINS` and `DEPENDS_ON` to build the internal dependency graph [pkg/sbom/spdx/unmarshal.go:85-102]().

---

## Data Mapping and Constants

Trivy uses specific constants to ensure consistency when generating SPDX documents.

| SPDX Field | Trivy Constant / Source | Value / Description |
|-----------|-------------------------|---------------------|
| `DocumentNamespace` | `DocumentNamespace` | `http://trivy.dev` [pkg/sbom/spdx/marshal.go:34]() |
| `Creator Organization`| `CreatorOrganization` | `aquasecurity` [pkg/sbom/spdx/marshal.go:35]() |
| `Creator Tool` | `CreatorTool` | `trivy` [pkg/sbom/spdx/marshal.go:36]() |
| `Package Purpose` | `PackagePurposeOS` | `OPERATING-SYSTEM` [pkg/sbom/spdx/marshal.go:46]() |
| `Package Purpose` | `PackagePurposeLibrary` | `LIBRARY` [pkg/sbom/spdx/marshal.go:50]() |
| `Relationship` | `RelationShipContains` | `CONTAINS` [pkg/sbom/spdx/marshal.go:57]() |

**Sources:** [pkg/sbom/spdx/marshal.go:32-67]()

---

## Implementation Details

### Marshaling Packages
The `Marshaler` iterates through components in a `core.BOM` to create `spdx.Package` entries. It includes:
1. **Vulnerability Advisories**: If vulnerabilities are present in the BOM, they are added as `PackageExternalReferences` using the primary URL [pkg/sbom/spdx/marshal.go:166-170]().
2. **License Handling**: Both `PackageLicenseConcluded` and `PackageLicenseDeclared` are populated from the component's license data [pkg/sbom/spdx/marshal.go:176-180]().
3. **Verification Codes**: For packages with files, Trivy calculates an SPDX Verification Code [pkg/sbom/spdx/marshal.go:196-201]().

### Unmarshaling Logic
The `SPDX` struct in `pkg/sbom/spdx/unmarshal.go` handles the conversion from the `tools-golang` document model to Trivy's `core.BOM`.
- **Root Identification**: It identifies the root package by looking for the `DESCRIBES` relationship from the `DOCUMENT` identifier [pkg/sbom/spdx/unmarshal.go:137-143]().
- **File Paths**: It tracks file-to-package associations via `CONTAINS` relationships to populate component file paths [pkg/sbom/spdx/unmarshal.go:108-133]().

---

## Comparison of Formats

Trivy supports two SPDX output variants:

| Format | Writer Logic | Serialization |
|--------|--------------|---------------|
| `spdx-json` | `writeSPDXJson` | `json.MarshalIndent` [pkg/report/spdx/spdx.go:53-65]() |
| `spdx` | `tagvalue.Write` | SPDX Tag-Value format [pkg/report/spdx/spdx.go:43-45]() |

---

## CLI Usage

### Generating SPDX SBOMs
```bash
# Generate SPDX JSON
trivy image --format spdx-json --output result.spdx.json alpine:latest

# Generate SPDX Tag-Value
trivy image --format spdx --output result.spdx alpine:latest
```

### Scanning SPDX SBOMs
```bash
# Scan an existing SPDX file for vulnerabilities
trivy sbom result.spdx.json
```

When scanning an SBOM, the `sbomAnalyzer` automatically detects if the file is SPDX or CycloneDX based on the content [pkg/fanal/analyzer/sbom/sbom.go:35]().

**Sources:** [pkg/fanal/analyzer/sbom/sbom.go:18-30](), [pkg/report/spdx/spdx.go:23-30]()

---

# Page: Report Generation and Output

# Report Generation and Output

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [contrib/junit.tpl](contrib/junit.tpl)
- [integration/testdata/alpine-310.junit.golden](integration/testdata/alpine-310.junit.golden)
- [integration/testdata/alpine-310.sarif.golden](integration/testdata/alpine-310.sarif.golden)
- [integration/testdata/dockerfile-custom-policies.json.golden](integration/testdata/dockerfile-custom-policies.json.golden)
- [integration/testdata/dockerfile.json.golden](integration/testdata/dockerfile.json.golden)
- [integration/testdata/dockerfile_file_pattern.json.golden](integration/testdata/dockerfile_file_pattern.json.golden)
- [integration/testdata/helm.json.golden](integration/testdata/helm.json.golden)
- [integration/testdata/helm_testchart.json.golden](integration/testdata/helm_testchart.json.golden)
- [integration/testdata/helm_testchart.overridden.json.golden](integration/testdata/helm_testchart.overridden.json.golden)
- [integration/testdata/secrets.json.golden](integration/testdata/secrets.json.golden)
- [pkg/commands/convert/run.go](pkg/commands/convert/run.go)
- [pkg/fanal/types/package.go](pkg/fanal/types/package.go)
- [pkg/fanal/types/secret.go](pkg/fanal/types/secret.go)
- [pkg/report/export_test.go](pkg/report/export_test.go)
- [pkg/report/json.go](pkg/report/json.go)
- [pkg/report/json_test.go](pkg/report/json_test.go)
- [pkg/report/sarif.go](pkg/report/sarif.go)
- [pkg/report/sarif_test.go](pkg/report/sarif_test.go)
- [pkg/report/table/licensing.go](pkg/report/table/licensing.go)
- [pkg/report/table/misconfig.go](pkg/report/table/misconfig.go)
- [pkg/report/table/misconfig_test.go](pkg/report/table/misconfig_test.go)
- [pkg/report/table/secret.go](pkg/report/table/secret.go)
- [pkg/report/table/secret_test.go](pkg/report/table/secret_test.go)
- [pkg/report/table/table.go](pkg/report/table/table.go)
- [pkg/report/table/table_test.go](pkg/report/table/table_test.go)
- [pkg/report/table/vulnerability.go](pkg/report/table/vulnerability.go)
- [pkg/report/table/vulnerability_test.go](pkg/report/table/vulnerability_test.go)
- [pkg/report/template.go](pkg/report/template.go)
- [pkg/report/template_test.go](pkg/report/template_test.go)
- [pkg/report/writer.go](pkg/report/writer.go)
- [pkg/report/writer_test.go](pkg/report/writer_test.go)
- [pkg/rpc/client/export_test.go](pkg/rpc/client/export_test.go)
- [pkg/scan/service.go](pkg/scan/service.go)
- [pkg/types/report.go](pkg/types/report.go)
- [pkg/types/scan.go](pkg/types/scan.go)
- [pkg/types/version.go](pkg/types/version.go)

</details>



Trivy's report generation system transforms scan results from the internal `types.Report` structure into various output formats. The system is built around the `Writer` interface pattern, allowing pluggable output formatters while maintaining a consistent API. The main orchestration happens in [pkg/report/writer.go:29-121]() through the `Write` function, which routes to format-specific writers.

The report generation process occurs after scanning is complete and results are available in the `types.Report` structure. For information about how scan results are generated, see [Scanning Capabilities](#4). For SBOM generation as output, see [SBOM Generation and Consumption](#6).

## Report Generation Pipeline

The report generation pipeline starts after scanning completes and consists of three main phases: pre-processing hooks, format-specific writing, and post-processing hooks.

### Overall Report Generation Flow

```mermaid
graph TD
    ScanComplete["Scan Complete<br/>types.Report populated"] --> WriteFunc["report.Write()<br/>pkg/report/writer.go:29"]
    
    WriteFunc --> PreHook["extension.PreReport()<br/>line 31"]
    PreHook --> OutputWriter["option.OutputWriter()<br/>line 35"]
    OutputWriter --> ComplianceCheck{"Compliance<br/>Report?<br/>line 46"}
    
    ComplianceCheck -->|"Yes<br/>option.Compliance.Spec.ID != ''"| ComplianceWriter["complianceWrite()<br/>line 123"]
    ComplianceCheck -->|No| FormatSwitch["Format Switch<br/>lines 51-109"]
    
    FormatSwitch --> Writers["Format-Specific Writers"]
    Writers --> WriterWrite["writer.Write(ctx, report)<br/>line 111"]
    
    WriterWrite --> PostHook["extension.PostReport()<br/>line 116"]
    PostHook --> CleanupDefer["cleanup() deferred<br/>lines 39-43"]
    CleanupDefer --> OutputFile["Output File/Stream"]
```

**Sources:** [pkg/report/writer.go:29-121]()

### Writer Interface and Implementations

The `Writer` interface defined at [pkg/report/writer.go:137-139]() provides a uniform API for all output formats:

```mermaid
graph TB
    WriterInterface["Writer Interface<br/>pkg/report/writer.go:137-139"] --> WriteMethod["Write(context.Context, types.Report) error"]
    
    subgraph CoreWriters["Core Writers"]
        JSONWriter["JSONWriter<br/>pkg/report/json.go"]
        SarifWriter["SarifWriter<br/>pkg/report/sarif.go:45-51"]
        TemplateWriter["TemplateWriter<br/>pkg/report/template.go"]
    end
    
    subgraph SBOMWriters["SBOM Writers"]
        CycloneDXWriter["cyclonedx.Writer<br/>pkg/report/cyclonedx"]
        SPDXWriter["spdx.Writer<br/>pkg/report/spdx"]
    end
    
    subgraph IntegrationWriters["Integration Writers"]
        GitHubWriter["github.Writer<br/>pkg/report/github"]
        PredicateWriter["predicate.VulnWriter<br/>pkg/report/predicate"]
        TableWriter["table.Writer<br/>pkg/report/table"]
    end
    
    WriteMethod -.implements.-> JSONWriter
    WriteMethod -.implements.-> SarifWriter
    WriteMethod -.implements.-> TemplateWriter
    WriteMethod -.implements.-> CycloneDXWriter
    WriteMethod -.implements.-> SPDXWriter
    WriteMethod -.implements.-> GitHubWriter
    WriteMethod -.implements.-> PredicateWriter
    WriteMethod -.implements.-> TableWriter
```

**Sources:** [pkg/report/writer.go:137-139](), [pkg/report/sarif.go:45-51]()

## Format Dispatch Mechanism

The `Write` function at [pkg/report/writer.go:29-121]() implements the format dispatch logic through a switch statement that routes to the appropriate writer based on `option.Format`:

```mermaid
graph TD
    WriteFunc["report.Write()"] --> FormatSwitch["switch option.Format<br/>line 51"]
    
    FormatSwitch -->|"types.FormatTable"| TableCase["table.NewWriter()<br/>lines 52-65"]
    FormatSwitch -->|"types.FormatJSON"| JSONCase["JSONWriter{}<br/>lines 66-71"]
    FormatSwitch -->|"types.FormatGitHub"| GitHubCase["github.Writer{}<br/>lines 72-76"]
    FormatSwitch -->|"types.FormatCycloneDX"| CycloneDXCase["cyclonedx.NewWriter()<br/>lines 77-79"]
    FormatSwitch -->|"types.FormatSPDX<br/>types.FormatSPDXJSON"| SPDXCase["spdx.NewWriter()<br/>lines 80-81"]
    FormatSwitch -->|"types.FormatTemplate"| TemplateCase["NewTemplateWriter()<br/>lines 82-94"]
    FormatSwitch -->|"types.FormatSarif"| SarifCase["SarifWriter{}<br/>lines 95-104"]
    FormatSwitch -->|"types.FormatCosignVuln"| CosignCase["predicate.NewVulnWriter()<br/>lines 105-106"]
    FormatSwitch -->|default| ErrorCase["xerrors.Errorf<br/>line 108"]
    
    TableCase --> WriterWrite["writer.Write(ctx, report)<br/>line 111"]
    JSONCase --> WriterWrite
    GitHubCase --> WriterWrite
    CycloneDXCase --> WriterWrite
    SPDXCase --> WriterWrite
    TemplateCase --> WriterWrite
    SarifCase --> WriterWrite
    CosignCase --> WriterWrite
```

**Sources:** [pkg/report/writer.go:50-109]()

## Supported Output Formats

Trivy supports multiple output formats defined as constants in [pkg/types/report.go:93-102](). Each format is handled by a dedicated writer implementation:

| Format Constant | CLI Flag Value | Writer Implementation | Primary Use Case | Details |
|----------------|----------------|----------------------|------------------|---------|
| `FormatTable` | `table` | `table.Writer` | Human-readable console output | See [Report Writers and Format Selection](#7.1) |
| `FormatJSON` | `json` | `JSONWriter` | Machine processing, API integration | See [Report Writers and Format Selection](#7.1) |
| `FormatSarif` | `sarif` | `SarifWriter` | Security tool integration (GitHub, IDEs) | See [SARIF Output for Security Tools](#7.2) |
| `FormatTemplate` | `template` | `TemplateWriter` | Custom output formats | See [Template-Based Custom Reports](#7.3) |
| `FormatCycloneDX` | `cyclonedx` | `cyclonedx.Writer` | CycloneDX SBOM generation | See [CycloneDX Format](#6.1) |
| `FormatSPDX` | `spdx` | `spdx.Writer` | SPDX SBOM generation | See [SPDX Format](#6.2) |
| `FormatSPDXJSON` | `spdx-json` | `spdx.Writer` | SPDX JSON SBOM generation | See [SPDX Format](#6.2) |
| `FormatGitHub` | `github` | `github.Writer` | GitHub dependency snapshots | See [Report Writers and Format Selection](#7.1) |
| `FormatCosignVuln` | `cosign-vuln` | `predicate.VulnWriter` | Cosign vulnerability attestations | See [Report Writers and Format Selection](#7.1) |

**Sources:** [pkg/types/report.go:93-102](), [pkg/report/writer.go:50-109]()

## Core Report Data Structure

All writers receive the same input: a `types.Report` structure defined at [pkg/types/report.go:20-40](). This structure contains the complete scan results and metadata:

### types.Report Structure

| Field | Type | Description |
|-------|------|-------------|
| `SchemaVersion` | `int` | Report schema version (currently 2) |
| `ArtifactName` | `string` | Name/identifier of scanned artifact |
| `ArtifactType` | `ftypes.ArtifactType` | Type (container image, filesystem, etc.) |
| `Metadata` | `Metadata` | Image metadata (tags, digests, OS info) |
| `Results` | `Results` | Array of scan results by target |
| `BOM` | `*core.BOM` | Software Bill of Materials (if requested) |

### types.Result Structure

Each element in `Results` contains findings for a specific target as defined in [pkg/types/report.go:157-173]():

| Field | Type | Description |
|-------|------|-------------|
| `Target` | `string` | Target identifier (file path, image layer, etc.) |
| `Class` | `ResultClass` | Result class (OS packages, language packages, config, secrets, licenses) |
| `Type` | `ftypes.TargetType` | Specific type (alpine, npm, terraform, etc.) |
| `Vulnerabilities` | `[]DetectedVulnerability` | Detected vulnerabilities |
| `Misconfigurations` | `[]DetectedMisconfiguration` | IaC/config issues |
| `Secrets` | `[]DetectedSecret` | Detected secrets |
| `Licenses` | `[]DetectedLicense` | License findings |
| `Packages` | `[]ftypes.Package` | All packages (if `--list-all-pkgs`) |

**Sources:** [pkg/types/report.go:20-40](), [pkg/types/report.go:157-173]()

## Compliance Reporting

When `option.Compliance.Spec.ID` is set (line 46 in [pkg/report/writer.go:46-48]()), the report generation takes a special path through `complianceWrite()` at [pkg/report/writer.go:123-134](). This function:

1. Calls `cr.BuildComplianceReport()` to transform scan results according to a compliance specification [pkg/report/writer.go:124]().
2. Routes to `cr.Write()` with compliance-specific options [pkg/report/writer.go:128-133]().

Compliance reporting supports multiple standards (e.g., `k8s-nsa-1.0`, `aws-cis-1.4`) defined in [pkg/types/report.go:83-91](). For details, see [Compliance and Summary Reports](#7.4).

**Sources:** [pkg/report/writer.go:46-48](), [pkg/report/writer.go:123-134](), [pkg/types/report.go:83-91]()

## Extension and Customization

The reporting system supports extension through:

1. **Template System**: Custom output formats via Go templates with helper functions and Sprig functions [pkg/report/writer.go:92]().
2. **Hook System**: Pre and post-report processing hooks for custom modifications [pkg/report/writer.go:31-33](), [pkg/report/writer.go:116-118]().
3. **Writer Interface**: New output formats can be added by implementing the `Writer` interface [pkg/report/writer.go:137-139]().

**Sources:** [pkg/report/writer.go:31-33](), [pkg/report/writer.go:92](), [pkg/report/writer.go:116-118](), [pkg/report/writer.go:137-139]()

---

# Page: Report Writers and Format Selection

# Report Writers and Format Selection

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [contrib/junit.tpl](contrib/junit.tpl)
- [integration/testdata/alpine-310.junit.golden](integration/testdata/alpine-310.junit.golden)
- [integration/testdata/alpine-310.sarif.golden](integration/testdata/alpine-310.sarif.golden)
- [integration/testdata/dockerfile-custom-policies.json.golden](integration/testdata/dockerfile-custom-policies.json.golden)
- [integration/testdata/dockerfile.json.golden](integration/testdata/dockerfile.json.golden)
- [integration/testdata/dockerfile_file_pattern.json.golden](integration/testdata/dockerfile_file_pattern.json.golden)
- [integration/testdata/helm.json.golden](integration/testdata/helm.json.golden)
- [integration/testdata/helm_testchart.json.golden](integration/testdata/helm_testchart.json.golden)
- [integration/testdata/helm_testchart.overridden.json.golden](integration/testdata/helm_testchart.overridden.json.golden)
- [integration/testdata/secrets.json.golden](integration/testdata/secrets.json.golden)
- [pkg/commands/convert/run.go](pkg/commands/convert/run.go)
- [pkg/fanal/types/misconf.go](pkg/fanal/types/misconf.go)
- [pkg/fanal/types/package.go](pkg/fanal/types/package.go)
- [pkg/fanal/types/secret.go](pkg/fanal/types/secret.go)
- [pkg/report/export_test.go](pkg/report/export_test.go)
- [pkg/report/json.go](pkg/report/json.go)
- [pkg/report/json_test.go](pkg/report/json_test.go)
- [pkg/report/sarif.go](pkg/report/sarif.go)
- [pkg/report/sarif_test.go](pkg/report/sarif_test.go)
- [pkg/report/table/licensing.go](pkg/report/table/licensing.go)
- [pkg/report/table/misconfig.go](pkg/report/table/misconfig.go)
- [pkg/report/table/misconfig_test.go](pkg/report/table/misconfig_test.go)
- [pkg/report/table/secret.go](pkg/report/table/secret.go)
- [pkg/report/table/secret_test.go](pkg/report/table/secret_test.go)
- [pkg/report/table/table.go](pkg/report/table/table.go)
- [pkg/report/table/table_test.go](pkg/report/table/table_test.go)
- [pkg/report/table/vulnerability.go](pkg/report/table/vulnerability.go)
- [pkg/report/table/vulnerability_test.go](pkg/report/table/vulnerability_test.go)
- [pkg/report/template.go](pkg/report/template.go)
- [pkg/report/template_test.go](pkg/report/template_test.go)
- [pkg/report/writer.go](pkg/report/writer.go)
- [pkg/report/writer_test.go](pkg/report/writer_test.go)
- [pkg/result/filter.go](pkg/result/filter.go)
- [pkg/result/filter_test.go](pkg/result/filter_test.go)
- [pkg/result/ignore.go](pkg/result/ignore.go)
- [pkg/result/ignore_test.go](pkg/result/ignore_test.go)
- [pkg/result/testdata/.trivyignore](pkg/result/testdata/.trivyignore)
- [pkg/result/testdata/.trivyignore.yaml](pkg/result/testdata/.trivyignore.yaml)
- [pkg/result/testdata/test-ignore-policy-licenses-and-secrets.rego](pkg/result/testdata/test-ignore-policy-licenses-and-secrets.rego)
- [pkg/rpc/client/export_test.go](pkg/rpc/client/export_test.go)
- [pkg/scan/service.go](pkg/scan/service.go)
- [pkg/types/misconfiguration.go](pkg/types/misconfiguration.go)
- [pkg/types/report.go](pkg/types/report.go)
- [pkg/types/scan.go](pkg/types/scan.go)
- [pkg/types/version.go](pkg/types/version.go)
- [pkg/types/vulnerability.go](pkg/types/vulnerability.go)

</details>



## Purpose and Scope

This document explains Trivy's report generation system, specifically the `Writer` interface pattern and the format dispatch mechanism that routes scan results to different output formats. It covers how the `Write` function in `pkg/report/writer.go` selects and instantiates format-specific writers based on user configuration and the internal filtering pipeline that prepares results for output.

For details on specific output formats, see:
- SARIF format implementation → [7.2 SARIF Output for Security Tools]()
- Custom template-based reports → [7.3 Template-Based Custom Reports]()
- Compliance and summary reports → [7.4 Compliance and Summary Reports]()

For information about SBOM output formats, see [6.1 CycloneDX Format]() and [6.2 SPDX Format]().

---

## Report Generation Architecture

The report generation system in Trivy follows a strategy pattern where a central `Write` function dispatches to format-specific writer implementations. All writers implement a common `Writer` interface, enabling polymorphic handling of different output formats.

### High-Level Flow

```mermaid
graph TB
    ScanComplete["Scan Complete<br/>types.Report"]
    WriteEntry["report.Write()<br/>[pkg/report/writer.go:29]"]
    PreHooks["extension.PreReport()<br/>Hook Execution"]
    OutputWriter["option.OutputWriter()<br/>Create io.Writer"]
    ComplianceCheck{"Compliance<br/>Report?"}
    FormatSwitch{"Switch on<br/>option.Format"}
    WriterImpl["Writer Implementation<br/>Write(ctx, report)"]
    PostHooks["extension.PostReport()<br/>Hook Execution"]
    Output["Output File/Stream"]
    
    ScanComplete --> WriteEntry
    WriteEntry --> PreHooks
    PreHooks --> OutputWriter
    OutputWriter --> ComplianceCheck
    ComplianceCheck -->|Yes| ComplianceWrite["complianceWrite()"]
    ComplianceCheck -->|No| FormatSwitch
    FormatSwitch --> WriterImpl
    WriterImpl --> PostHooks
    PostHooks --> Output
    ComplianceWrite --> Output
```
**Sources:** [pkg/report/writer.go:29-121]()

---

## The Writer Interface

All format-specific writers implement the `Writer` interface, which defines a single method:

```go
type Writer interface {
	Write(context.Context, types.Report) error
}
```
**Sources:** [pkg/report/writer.go:137-139]()

### Writer Interface Implementations

| Writer Type | Package | Description |
|------------|---------|-------------|
| `JSONWriter` | `pkg/report` | Outputs JSON format with optional package listing |
| `SarifWriter` | `pkg/report` | Generates SARIF 2.1.0 format for security tools |
| `TemplateWriter` | `pkg/report` | User-defined templates with Sprig functions |
| `table.Writer` | `pkg/report/table` | Human-readable table output with tree view |
| `github.Writer` | `pkg/report/github` | GitHub Dependency Snapshot format |
| `cyclonedx.Writer` | `pkg/report/cyclonedx` | CycloneDX SBOM format |
| `spdx.Writer` | `pkg/report/spdx` | SPDX SBOM format (JSON or Tag-Value) |
| `predicate.VulnWriter` | `pkg/report/predicate` | Cosign vulnerability attestation format |

**Sources:** [pkg/report/writer.go:50-109](), [pkg/report/json.go:15-20](), [pkg/report/sarif.go:45-51](), [pkg/report/template.go:25-29]()

---

## Result Filtering Pipeline

Before results are passed to the `Writer`, they are processed through a filtering pipeline in `pkg/result/filter.go`. This system removes findings based on severity, status, and ignore rules.

### Filtering Logic
The `Filter` function orchestrates several specialized filters:
1.  **Severity Filter:** Compares finding severity against `opt.Severities` [pkg/result/filter.go:92-93]().
2.  **Status Filter:** For vulnerabilities, checks `ignoreStatuses` [pkg/result/filter.go:95-96]().
3.  **Ignore File (.trivyignore):** Matches findings against patterns in ignore files [pkg/result/filter.go:100-104]().
4.  **VEX Filter:** Applies Vulnerability Exploitability eXchange (VEX) data to suppress or modify findings [pkg/result/filter.go:52-57]().
5.  **Policy Filter:** Applies OPA Rego policies to the results if a policy file is provided [pkg/result/filter.go:72-77]().

### Modified Findings
When a finding is filtered out (ignored), it is often moved to `ModifiedFindings` rather than being deleted entirely, allowing the report to track what was suppressed and why [pkg/result/filter.go:100-104]().

**Sources:** [pkg/result/filter.go:39-81](), [pkg/result/filter.go:83-119](), [pkg/types/report.go:169-173]()

---

## Format Dispatch Mechanism

The `Write` function at [pkg/report/writer.go:29-121]() orchestrates the entire report generation process.

### Dispatch Flow Diagram

```mermaid
graph TB
    subgraph "Entry Point"
        Write["report.Write(ctx, report, option)"]
    end
    
    subgraph "Pre-Processing"
        PreHook["extension.PreReport(ctx, &report, option)"]
        CreateOutput["option.OutputWriter(ctx)"]
    end
    
    subgraph "Format Selection [pkg/report/writer.go:51-109]"
        CompCheck{"option.Compliance.Spec.ID != ''"}
        FormatSwitch{"switch option.Format"}
        
        CompCheck -->|true| ComplianceWrite["complianceWrite()"]
        CompCheck -->|false| FormatSwitch
        
        FormatSwitch -->|"FormatTable"| TableWriter["table.NewWriter()"]
        FormatSwitch -->|"FormatJSON"| JSONWriter["JSONWriter{}"]
        FormatSwitch -->|"FormatGitHub"| GitHubWriter["github.Writer{}"]
        FormatSwitch -->|"FormatCycloneDX"| CycloneDXWriter["cyclonedx.NewWriter()"]
        FormatSwitch -->|"FormatSPDX<br/>FormatSPDXJSON"| SPDXWriter["spdx.NewWriter()"]
        FormatSwitch -->|"FormatTemplate"| TemplateWriter["NewTemplateWriter()"]
        FormatSwitch -->|"FormatSarif"| SarifWriter["SarifWriter{}"]
        FormatSwitch -->|"FormatCosignVuln"| CosignWriter["predicate.NewVulnWriter()"]
    end
    
    subgraph "Execution"
        WriteMethod["writer.Write(ctx, report)"]
    end
    
    subgraph "Post-Processing"
        PostHook["extension.PostReport(ctx, &report, option)"]
        Cleanup["cleanup()"]
    end
    
    Write --> PreHook
    PreHook --> CreateOutput
    CreateOutput --> CompCheck
    
    TableWriter --> WriteMethod
    JSONWriter --> WriteMethod
    GitHubWriter --> WriteMethod
    CycloneDXWriter --> WriteMethod
    SPDXWriter --> WriteMethod
    TemplateWriter --> WriteMethod
    SarifWriter --> WriteMethod
    CosignWriter --> WriteMethod
    
    WriteMethod --> PostHook
    PostHook --> Cleanup
    ComplianceWrite --> Cleanup
```
**Sources:** [pkg/report/writer.go:29-121]()

### Stage Breakdown

1.  **Pre-Report Hook:** `extension.PreReport` is called, allowing external modules to modify the report object before formatting [pkg/report/writer.go:31-33]().
2.  **Output Writer:** `option.OutputWriter` is invoked to create the target `io.Writer` (e.g., a file or stdout) [pkg/report/writer.go:35-38]().
3.  **Compliance Check:** If a compliance ID is set, the flow redirects to `complianceWrite` which builds a specialized `ComplianceReport` [pkg/report/writer.go:46-48](), [pkg/report/writer.go:123-134]().
4.  **Format Switch:** The core logic selects a `Writer` implementation based on the `types.Format` enum [pkg/report/writer.go:51-109]().
5.  **Execution:** The selected writer's `Write` method is called [pkg/report/writer.go:111-113]().
6.  **Post-Report Hook:** `extension.PostReport` is called after writing [pkg/report/writer.go:116-118]().

---

## Writer Implementations

### JSONWriter
The `JSONWriter` serializes the `types.Report` structure into JSON. It supports pretty-printing and can optionally include all discovered packages (even those without vulnerabilities) [pkg/report/json.go:15-20]().

**Instantiation:** [pkg/report/writer.go:66-71]()

### SarifWriter
The `SarifWriter` converts findings into the Static Analysis Results Interchange Format (SARIF). It maps Trivy findings to SARIF `rules` and `results` [pkg/report/sarif.go:45-51]().

*   **Rule Mapping:** Vulnerabilities are categorized as `OsPackageVulnerability` or `LanguageSpecificPackageVulnerability` [pkg/report/sarif.go:22-23]().
*   **Location Handling:** For filesystem scans, it uses the target path to calculate `ROOTPATH` in the SARIF output [pkg/report/writer.go:97-104]().
*   **Severity Mapping:** Trivy severities (CRITICAL, HIGH, etc.) are converted to SARIF levels (error, warning, note) [pkg/report/sarif.go:311-322]().

**Sources:** [pkg/report/sarif.go:128-212](), [pkg/report/writer.go:95-104]()

### TemplateWriter
The `TemplateWriter` uses Go's `text/template` engine. It provides custom functions like `escapeXML`, `sourceID`, and `appVersion` to assist in generating various text-based formats (e.g., JUnit, HTML) [pkg/report/template.go:25-29](), [pkg/report/template.go:40-64]().

**Sources:** [pkg/report/template.go:72-84](), [pkg/report/writer.go:82-94]()

---

## Data Structures and Types

The reporting system relies on the `types.Report` struct which aggregates all scan findings.

| Entity | Code Identifier | Description |
| :--- | :--- | :--- |
| **Root Report** | `types.Report` | Contains metadata and a list of `Results` [pkg/types/report.go:20-40]() |
| **Scan Result** | `types.Result` | Findings for a specific target (e.g., a file or image layer) [pkg/types/report.go:157-173]() |
| **Vulnerability** | `types.DetectedVulnerability` | Details of a detected CVE [pkg/types/vulnerability.go:11-47]() |
| **Misconfiguration** | `types.DetectedMisconfiguration` | Details of a failed policy check [pkg/types/misconfiguration.go:34-63]() |
| **Secret** | `types.DetectedSecret` | Details of a detected sensitive string [pkg/fanal/types/secret.go:12-21]() |

**Sources:** [pkg/types/report.go:1-173](), [pkg/types/vulnerability.go:11-47]()

---

## Implementation Details: Compliance Writing

When compliance mode is active, the system uses `complianceWrite`. This function bridges the standard `types.Report` to the compliance reporting system.

```mermaid
graph LR
    Report["types.Report"]
    Build["cr.BuildComplianceReport()<br/>[pkg/compliance/report/build.go]"]
    Write["cr.Write()<br/>[pkg/compliance/report/writer.go]"]
    Output["io.Writer"]

    Report --> Build
    Build --> Write
    Write --> Output
```
**Sources:** [pkg/report/writer.go:123-134]()

The `complianceWrite` function:
1.  Extracts results from the report.
2.  Calls `cr.BuildComplianceReport` with the specified compliance options [pkg/report/writer.go:124]().
3.  Calls the compliance-specific `Write` function to output the final report in the requested format (Table, JSON, etc.) [pkg/report/writer.go:128-133]().

---

# Page: SARIF Output for Security Tools

# SARIF Output for Security Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [contrib/asff.tpl](contrib/asff.tpl)
- [contrib/junit.tpl](contrib/junit.tpl)
- [integration/testdata/alpine-310.asff.golden](integration/testdata/alpine-310.asff.golden)
- [integration/testdata/alpine-310.junit.golden](integration/testdata/alpine-310.junit.golden)
- [integration/testdata/alpine-310.sarif.golden](integration/testdata/alpine-310.sarif.golden)
- [integration/testdata/secrets.asff.golden](integration/testdata/secrets.asff.golden)
- [pkg/commands/convert/run.go](pkg/commands/convert/run.go)
- [pkg/fanal/types/package.go](pkg/fanal/types/package.go)
- [pkg/report/export_test.go](pkg/report/export_test.go)
- [pkg/report/json.go](pkg/report/json.go)
- [pkg/report/json_test.go](pkg/report/json_test.go)
- [pkg/report/sarif.go](pkg/report/sarif.go)
- [pkg/report/sarif_test.go](pkg/report/sarif_test.go)
- [pkg/report/template.go](pkg/report/template.go)
- [pkg/report/template_test.go](pkg/report/template_test.go)
- [pkg/report/writer.go](pkg/report/writer.go)
- [pkg/report/writer_test.go](pkg/report/writer_test.go)

</details>



SARIF (Static Analysis Results Interchange Format) version 2.1.0 is an industry-standard format for representing static analysis results. Trivy generates SARIF reports to enable integration with security-focused IDEs, CI/CD systems like GitHub Advanced Security, and compliance platforms. The SARIF format provides a structured representation of vulnerabilities, misconfigurations, secrets, and license issues with precise location information and severity metadata.

## SARIF Report Structure

Trivy generates SARIF reports conforming to the OASIS SARIF 2.1.0 specification. The report consists of a single run containing tool metadata, rule definitions, and result instances.

**SARIF Report Components**
```mermaid
flowchart TD
    Report["sarif.Report"] --> Version["version: 2.1.0"]
    Report --> Schema["$schema: SARIF 2.1.0 spec URL"]
    Report --> Runs["runs: [sarif.Run]"]
    
    Runs --> Tool["tool.driver"]
    Runs --> Results["results: [sarif.Result]"]
    Runs --> Properties["properties: metadata"]
    
    Tool --> DriverName["name: Trivy"]
    Tool --> DriverVersion["version: app version"]
    Tool --> DriverRules["rules: [sarif.ReportingDescriptor]"]
    
    DriverRules --> RuleID["id: CVE/KSV/rule ID"]
    DriverRules --> RuleName["name: vulnerability type"]
    DriverRules --> RuleProps["properties: CVSS data"]
    
    Results --> ResultRuleID["ruleId: matches rule"]
    Results --> ResultLevel["level: error/warning/note"]
    Results --> ResultLocations["locations: physical locations"]
```

Sources: [pkg/report/sarif.go:129-144](), [integration/testdata/alpine-310.sarif.golden:1-204]()

The SARIF writer is invoked when `types.FormatSarif` is specified. The format selection occurs in the `Write` function, which instantiates a `SarifWriter` and sets the target for filesystem or repository scans to enable proper URI base paths.

| SARIF Component | Trivy Implementation | Location |
|-----------------|---------------------|----------|
| Schema Version | `sarif.Version210` | [pkg/report/sarif.go:129]() |
| Tool Driver | `"Trivy Vulnerability Scanner"` | [pkg/report/sarif.go:135]() |
| Column Kind | `"utf16CodeUnits"` | [pkg/report/sarif.go:34]() |
| URI Base ID | `"ROOTPATH"` | [pkg/report/sarif.go:283]() |

Sources: [pkg/report/writer.go:95-104](), [pkg/report/sarif.go:129-135]()

## SarifWriter Implementation

The `SarifWriter` struct implements the report `Writer` interface to generate SARIF output. The writer maintains a location cache to optimize repeated package location lookups and tracks rule indexes to deduplicate rules across multiple findings.

**SarifWriter Data Flow**
```mermaid
flowchart TD
    Write["SarifWriter.Write()"] --> NewReport["sarif.New(Version210)"]
    NewReport --> InitRun["Initialize run with tool metadata"]
    InitRun --> SetProperties["Set container image properties"]
    
    SetProperties --> IterateResults["Iterate report.Results"]
    IterateResults --> ProcessVulns["Process Vulnerabilities"]
    IterateResults --> ProcessMisconfigs["Process Misconfigurations"]
    IterateResults --> ProcessSecrets["Process Secrets"]
    IterateResults --> ProcessLicenses["Process Licenses"]
    
    ProcessVulns --> BuildSarifData1["Build sarifData struct"]
    ProcessMisconfigs --> BuildSarifData2["Build sarifData struct"]
    ProcessSecrets --> BuildSarifData3["Build sarifData struct"]
    ProcessLicenses --> BuildSarifData4["Build sarifData struct"]
    
    BuildSarifData1 --> AddSarifResult["addSarifResult()"]
    BuildSarifData2 --> AddSarifResult
    BuildSarifData3 --> AddSarifResult
    BuildSarifData4 --> AddSarifResult
    
    AddSarifResult --> AddRule["addSarifRule()"]
    AddRule --> AddResult["run.AddResult()"]
```

Sources: [pkg/report/sarif.go:128-262]()

The `SarifWriter` struct is defined in [pkg/report/sarif.go:45-51]():

| Field | Type | Purpose |
|-------|------|---------|
| `Output` | `io.Writer` | Destination for SARIF JSON output |
| `Version` | `string` | Trivy version for tool metadata |
| `run` | `*sarif.Run` | SARIF run object being constructed |
| `locationCache` | `map[string][]location` | Cache of package locations by ID |
| `Target` | `string` | Target path for filesystem scans |

The `sarifData` struct encapsulates all information needed to generate a SARIF rule and result:

```go
type sarifData struct {
	title            string
	vulnerabilityId  string
	shortDescription string
	fullDescription  string
	helpText         string
	helpMarkdown     string
	resourceClass    types.ResultClass
	severity         string
	url              *url.URL
	resultIndex      int
	artifactLocation *url.URL
	locationMessage  string
	message          string
	cvssScore        string
	cvssData         map[string]any
	locations        []location
}
```

Sources: [pkg/report/sarif.go:53-70]()

## Rule Generation

Each unique vulnerability, misconfiguration, secret, or license issue generates a SARIF rule via the `addSarifRule` method. Rules are deduplicated using the `getRuleIndex` function which maintains a map of rule IDs to their array indices.

**Rule Generation Process**
```mermaid
flowchart TD
    AddSarifRule["SarifWriter.addSarifRule(sarifData)"] --> CreateRule["sw.run.AddRule(vulnerabilityId)"]
    CreateRule --> SetName["WithName(toSarifRuleName)"]
    SetName --> SetDescriptions["WithShortDescription / WithFullDescription"]
    SetDescriptions --> SetHelp["WithHelp"]
    SetHelp --> SetConfig["WithDefaultConfiguration"]
    SetConfig --> SetProperties["WithProperties(toProperties)"]
    SetProperties --> SetHelpURI["WithHelpURI(url)"]
```

Sources: [pkg/report/sarif.go:77-94](), [pkg/report/sarif.go:107-115]()

### Rule Name Mapping

The `toSarifRuleName` function maps Trivy's result classes to SARIF rule names:

| Result Class | SARIF Rule Name | Description |
|--------------|-----------------|-------------|
| `types.ClassOSPkg` | `OsPackageVulnerability` | Operating system package vulnerabilities |
| `types.ClassLangPkg` | `LanguageSpecificPackageVulnerability` | Language dependency vulnerabilities |
| `types.ClassConfig` | `Misconfiguration` | IaC and configuration issues |
| `types.ClassSecret` | `Secret` | Hardcoded secrets and credentials |
| `types.ClassLicense` | `License` | License compliance issues |

Sources: [pkg/report/sarif.go:21-27](), [pkg/report/sarif.go:294-309]()

### Severity Level Mapping

The `toSarifErrorLevel` function converts Trivy severities to SARIF reporting levels:

| Trivy Severity | SARIF Level | Usage |
|----------------|-------------|-------|
| `CRITICAL`, `HIGH` | `error` | Critical security issues |
| `MEDIUM` | `warning` | Moderate security issues |
| `LOW`, `UNKNOWN` | `note` | Minor issues or informational findings |

Sources: [pkg/report/sarif.go:29-32](), [pkg/report/sarif.go:311-322]()

## CVSS Data Mapping

SARIF rule properties include CVSS data extracted from vulnerability information. The `toCVSSData` function extracts CVSS vectors and scores from the vulnerability's severity source.

**CVSS Data Extraction**
```mermaid
flowchart TD
    ToCVSSData["toCVSSData(types.DetectedVulnerability)"] --> CheckSource{"vuln.SeveritySource exists?"}
    CheckSource -->|Yes| ExtractCVSS["Extract CVSS from vuln.CVSS[source]"]
    CheckSource -->|No| UseFallback["severityToScore(vuln.Severity)"]
    
    ExtractCVSS --> V2Data["cvssv2_vector, cvssv2_score"]
    ExtractCVSS --> V3Data["cvssv3_vector, cvssv3_baseScore"]
    ExtractCVSS --> V40Data["cvssv40_vector, cvssv40_baseScore"]
```

Sources: [pkg/report/sarif.go:412-449]()

The CVSS data is extracted from the vulnerability's `CVSS` map using the `SeveritySource` as the key.

| CVSS Property | Source Field | Type |
|---------------|--------------|------|
| `cvssv2_vector` | `V2Vector` | `string` |
| `cvssv2_score` | `V2Score` | `float64` |
| `cvssv3_vector` | `V3Vector` | `string` |
| `cvssv3_baseScore` | `V3Score` | `float64` |

Sources: [pkg/report/sarif.go:418-426](), [pkg/report/sarif_test.go:84-93]()

### Properties Generation

The `toProperties` function generates the SARIF properties object that includes tags, precision, and security severity.

```go
func toProperties(title, severity, cvssScore string, cvssData map[string]any) sarif.Properties {
	props := sarif.Properties{
		"tags": []string{
			title,
			"security",
			severity,
		},
		"precision":         "very-high",
		"security-severity": cvssScore,
	}
    // ... adds cvssData
}
```

Sources: [pkg/report/sarif.go:451-477]()

## Result Generation

The `addSarifResult` method creates a SARIF result for each finding. Results reference rules by ID and index, include a descriptive message, and specify one or more physical locations.

**Result Generation Components**
```mermaid
flowchart TD
    AddSarifResult["SarifWriter.addSarifResult(sarifData)"] --> CreateResult["sarif.NewRuleResult(vulnerabilityId)"]
    CreateResult --> SetRuleIndex["WithRuleIndex(resultIndex)"]
    SetRuleIndex --> SetMessage["WithMessage(message)"]
    SetMessage --> SetLevel["WithLevel(toSarifErrorLevel)"]
    SetLevel --> SetLocations["WithLocations(toSarifLocations)"]
    SetLocations --> AddToRun["sw.run.AddResult(result)"]
```

Sources: [pkg/report/sarif.go:96-105]()

### Message Formatting

SARIF result messages are formatted based on finding type:

- **Vulnerability messages**: Include package name, installed version, and fixed version [pkg/report/sarif.go:178-179]().
- **Misconfiguration messages**: Include artifact URI, type, and cause message [pkg/report/sarif.go:201-202]().
- **Secret messages**: Include artifact target, secret type, and match details [pkg/report/sarif.go:228-229]().

## Location Mapping

SARIF physical locations map findings to specific line ranges in files or packages.

**Location Processing Flow**
```mermaid
flowchart TD
    LocationData["Finding Location Data"] --> VulnCheck{"Vulnerability?"}
    VulnCheck -->|Yes| GetLocations["sw.getLocations()"]
    VulnCheck -->|No| DirectMetadata["Use CauseMetadata lines"]
    
    GetLocations --> IteratePackages["Iterate res.Packages"]
    IteratePackages --> MatchPackage{"Name/Version Match?"}
    MatchPackage -->|Yes| ExtractPkgLocs["Extract pkg.Locations"]
    
    ExtractPkgLocs --> ToSarifLocs["toSarifLocations()"]
    DirectMetadata --> ToSarifLocs
```

Sources: [pkg/report/sarif.go:170](), [pkg/report/sarif.go:193-198](), [pkg/report/sarif.go:391-410]()

### Package Location Caching

The `getLocations` method maintains a cache of package locations to avoid repeated package list traversals. The cache key is formed as `{path}@{name}@{version}`.

```go
func (sw *SarifWriter) getLocations(name, version, path string, pkgs []ftypes.Package) []location {
	id := fmt.Sprintf("%s@%s@%s", path, name, version)
	locs, ok := sw.locationCache[id]
    // ... lookup in pkgs if not in cache
}
```

Sources: [pkg/report/sarif.go:391-410]()

### Physical Location Structure

The `toSarifLocations` function converts internal location structures to SARIF physical locations:

| SARIF Element | Value |
|---------------|-------|
| `artifactLocation.uri` | File path (URL-encoded) |
| `artifactLocation.uriBaseId` | `"ROOTPATH"` |
| `region.startLine` | Line number |
| `region.endLine` | Line number |

Sources: [pkg/report/sarif.go:264-292]()

## Integration Report Formats

Beyond SARIF, Trivy supports several integration formats via the template system.

### Template-Based Integration

The template system allows custom output formats using Go templates with additional helper functions.

**Template Processing Flow**
```mermaid
flowchart TD
    TemplateOption["option.Template"] --> NewTemplateWriter["NewTemplateWriter()"]
    NewTemplateWriter --> ParseTemplate["template.Parse()"]
    
    ParseTemplate --> FuncMap["Add template functions"]
    FuncMap --> EscapeXML["escapeXML"]
    FuncMap --> EndWithPeriod["endWithPeriod"] 
    FuncMap --> AppVersion["appVersion"]
    
    Execute["TemplateWriter.Write()"] --> ExecuteTmpl["tw.Template.Execute(tw.Output, report.Results)"]
```

Sources: [pkg/report/template.go:32-74](), [pkg/report/template.go:77-83]()

### Supported Template Functions

| Function | Purpose |
|----------|---------|
| `escapeXML` | XML entity escaping for formats like JUnit [pkg/report/template.go:41-48]() |
| `endWithPeriod` | Ensure string ends with period [pkg/report/template.go:49-54]() |
| `escapeString` | HTML entity escaping [pkg/report/template.go:55]() |
| `appVersion` | Get current Trivy version [pkg/report/template.go:59-61]() |

Sources: [pkg/report/template.go:40-62]()

---

# Page: Template-Based Custom Reports

# Template-Based Custom Reports

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [contrib/asff.tpl](contrib/asff.tpl)
- [contrib/gitlab-codequality.tpl](contrib/gitlab-codequality.tpl)
- [contrib/gitlab.tpl](contrib/gitlab.tpl)
- [contrib/junit.tpl](contrib/junit.tpl)
- [docs/imgs/gitlab-codequality.png](docs/imgs/gitlab-codequality.png)
- [integration/testdata/alpine-310.asff.golden](integration/testdata/alpine-310.asff.golden)
- [integration/testdata/alpine-310.gitlab-codequality.golden](integration/testdata/alpine-310.gitlab-codequality.golden)
- [integration/testdata/alpine-310.gitlab.golden](integration/testdata/alpine-310.gitlab.golden)
- [integration/testdata/alpine-310.junit.golden](integration/testdata/alpine-310.junit.golden)
- [integration/testdata/alpine-310.sarif.golden](integration/testdata/alpine-310.sarif.golden)
- [integration/testdata/npm.gitlab.golden](integration/testdata/npm.gitlab.golden)
- [integration/testdata/secrets.asff.golden](integration/testdata/secrets.asff.golden)
- [pkg/commands/convert/run.go](pkg/commands/convert/run.go)
- [pkg/fanal/types/package.go](pkg/fanal/types/package.go)
- [pkg/report/export_test.go](pkg/report/export_test.go)
- [pkg/report/json.go](pkg/report/json.go)
- [pkg/report/json_test.go](pkg/report/json_test.go)
- [pkg/report/sarif.go](pkg/report/sarif.go)
- [pkg/report/sarif_test.go](pkg/report/sarif_test.go)
- [pkg/report/template.go](pkg/report/template.go)
- [pkg/report/template_test.go](pkg/report/template_test.go)
- [pkg/report/writer.go](pkg/report/writer.go)
- [pkg/report/writer_test.go](pkg/report/writer_test.go)

</details>



## Purpose and Scope

This document covers Trivy's template-based report generation system, which allows users to define custom output formats using Go templates. Templates provide flexibility to generate reports in any text-based format (XML, HTML, custom JSON structures, etc.) that is not covered by Trivy's built-in formats.

For built-in report formats like JSON and table output, see [Report Writers and Format Selection](7.1). For SARIF-specific output, see [SARIF Output for Security Tools](7.2).

---

## Template System Overview

The template system in Trivy allows users to specify custom output formats through Go's `text/template` package, enhanced with the Sprig function library. Templates receive scan results and can iterate over vulnerabilities, misconfigurations, secrets, and licenses to produce formatted output.

**Template Writer Architecture**

```mermaid
graph TB
    subgraph "Natural Language Space"
        UserTemplate["User Custom Template"]
        ScanResults["Scan Results"]
    end

    subgraph "Code Entity Space"
        Write["Write()<br/>[pkg/report/writer.go:29]"]
        FormatCheck{"Format Type"}
        TemplateWriter["TemplateWriter struct<br/>[pkg/report/template.go:26]"]
        NewTemplateWriter["NewTemplateWriter()<br/>[pkg/report/template.go:32]"]
        
        TemplateInput["Template Input<br/>--template flag"]
        FileRead["os.ReadFile()<br/>[pkg/report/template.go:34]"]
        InlineTemplate["Inline Template String"]
        
        FuncMap["template.FuncMap<br/>[pkg/report/template.go:40]"]
        SprigFuncs["sprig.GenericFuncMap()"]
        CustomFuncs["Custom Functions<br/>escapeXML, endWithPeriod, etc."]
        
        TemplateExec["tw.Template.Execute()<br/>[pkg/report/template.go:78]"]
        ResultsData["types.Report.Results<br/>[pkg/types/report.go]"]
        Output["io.Writer Output"]
    end
    
    UserTemplate -.-> TemplateInput
    ScanResults -.-> ResultsData
    
    Write --> FormatCheck
    FormatCheck -->|"types.FormatTemplate"| NewTemplateWriter
    
    TemplateInput --> FileRead
    TemplateInput --> InlineTemplate
    
    FileRead --> NewTemplateWriter
    InlineTemplate --> NewTemplateWriter
    
    NewTemplateWriter --> FuncMap
    FuncMap --> SprigFuncs
    FuncMap --> CustomFuncs
    
    NewTemplateWriter --> TemplateWriter
    TemplateWriter --> TemplateExec
    
    ResultsData --> TemplateExec
    TemplateExec --> Output
```

**Sources:** [pkg/report/writer.go:29-109](), [pkg/report/template.go:26-83]()

---

## Template Specification

### Inline Templates

Templates can be specified directly on the command line using the `--template` flag. The CLI orchestration passes this string to the `NewTemplateWriter`.

```bash
trivy image --format template --template '{{ range . }}{{ .Target }}{{ end }}' alpine:3.14
```

### File-Based Templates

Templates can be loaded from files by prefixing the path with `@`. The `NewTemplateWriter` function handles this by stripping the prefix and reading the file from disk.

```bash
trivy image --format template --template @/path/to/template.tpl alpine:3.14
```

The `@` prefix triggers file reading at [pkg/report/template.go:33-39](), where the template content is loaded using `os.ReadFile()`.

**Sources:** [pkg/report/template.go:32-39]()

---

## Data Model Available to Templates

Templates receive `types.Report.Results` (type `types.Results`), which is a slice of `types.Result` structures. Each result contains scan findings for a specific target.

**Template Data Mapping**

```mermaid
graph LR
    subgraph "Natural Language Space"
        ReportTarget["Scan Target"]
        Findings["Security Findings"]
    end

    subgraph "Code Entity Space"
        Results["types.Results<br/>[]types.Result"]
        Result["types.Result struct"]
        
        Target["Target: string"]
        Type["Type: string"]
        Class["Class: ResultClass"]
        
        Vulnerabilities["Vulnerabilities<br/>[]DetectedVulnerability"]
        Misconfigurations["Misconfigurations<br/>[]DetectedMisconfiguration"]
        Secrets["Secrets<br/>[]DetectedSecret"]
        Licenses["Licenses<br/>[]DetectedLicense"]
        Packages["Packages<br/>[]Package"]
        
        VulnFields["VulnerabilityID<br/>PkgName<br/>InstalledVersion<br/>Severity"]
        MisconfigFields["ID<br/>Title<br/>Message<br/>CauseMetadata"]
    end
    
    ReportTarget -.-> Target
    Findings -.-> Vulnerabilities
    Findings -.-> Misconfigurations
    
    Results --> Result
    Result --> Target
    Result --> Type
    Result --> Class
    Result --> Vulnerabilities
    Result --> Misconfigurations
    Result --> Secrets
    Result --> Licenses
    Result --> Packages
    
    Vulnerabilities --> VulnFields
    Misconfigurations --> MisconfigFields
```

**Sources:** [pkg/report/template.go:77-78](), [pkg/types/report.go](), [pkg/fanal/types/package.go]()

### Result Structure Fields

| Field | Type | Description |
|-------|------|-------------|
| `Target` | `string` | The target being scanned (e.g., image name, file path) [pkg/types/report.go]() |
| `Type` | `string` | Type of target (e.g., "alpine", "terraform") |
| `Class` | `ResultClass` | Classification: OSPkg, LangPkg, Config, Secret, License |
| `Vulnerabilities` | `[]DetectedVulnerability` | List of vulnerabilities found [pkg/types/report.go]() |
| `Misconfigurations` | `[]DetectedMisconfiguration` | List of misconfigurations found |
| `Secrets` | `[]DetectedSecret` | List of secrets found |
| `Licenses` | `[]DetectedLicense` | List of license findings |
| `Packages` | `[]Package` | All packages in the artifact [pkg/fanal/types/package.go]() |

**Sources:** [pkg/report/template.go:77-82](), [pkg/report/writer_test.go:20-93]()

---

## Template Functions

Templates have access to all Sprig functions plus custom Trivy-specific functions defined in the `templateFuncMap`.

### Custom Trivy Functions

| Function | Implementation | Purpose | Definition |
|----------|----------------|---------|------------|
| `escapeXML` | `xml.EscapeText` | Escapes XML special characters | [pkg/report/template.go:41-48]() |
| `endWithPeriod` | `strings.HasSuffix` | Ensures string ends with a period | [pkg/report/template.go:49-54]() |
| `escapeString` | `html.EscapeString` | HTML escapes string | [pkg/report/template.go:55]() |
| `sourceID` | `dbTypes.SourceID` | Casts string to SourceID type | [pkg/report/template.go:56-58]() |
| `appVersion` | `func() string` | Returns Trivy version string | [pkg/report/template.go:59-61]() |

**Sources:** [pkg/report/template.go:40-61]()

---

## Built-in Contrib Templates

Trivy provides several reference templates in the `contrib/` directory that demonstrate advanced usage.

### ASFF (AWS Security Finding Format)
The ASFF template converts Trivy findings into JSON compatible with AWS Security Hub. It uses `regexFind` to truncate image names and `escapeString` for descriptions.
- **Vulnerabilities:** Maps CVEs to `Software and Configuration Checks/Vulnerabilities/CVE`.
- **Misconfigurations:** Maps findings to `Software and Configuration Checks`.
- **Secrets:** Maps to `Sensitive Data Identifications`.

**Sources:** [contrib/asff.tpl:1-161]()

### GitLab Templates
Trivy supports GitLab's security dashboard through custom templates:
- **GitLab Container Scanning:** Maps vulnerabilities to the GitLab schema version 15.0.7 [contrib/gitlab.tpl:1-113]().
- **GitLab Code Quality:** Converts findings into a JSON array of issues with fingerprints [contrib/gitlab-codequality.tpl:1-104]().

### JUnit XML
Used for CI/CD integration, this template creates `<testsuite>` entries for each scan target and `<testcase>` entries for each finding.
- **Vulnerabilities:** [contrib/junit.tpl:11-15]()
- **Misconfigurations:** Includes `CauseMetadata` like line numbers and code snippets [contrib/junit.tpl:29-51]().

---

## Integration and Dispatch

The `report.Write` function acts as the entry point for all report generation.

```mermaid
graph TB
    Write["report.Write()<br/>[pkg/report/writer.go:29]"]
    FormatSwitch{"option.Format"}
    
    Template["types.FormatTemplate"]
    NewTW["NewTemplateWriter()<br/>[pkg/report/template.go:32]"]
    TW_Write["TemplateWriter.Write()<br/>[pkg/report/template.go:77]"]
    
    SarifCheck{"Is sarif.tpl?"}
    SarifWriter["SarifWriter<br/>[pkg/report/sarif.go:45]"]
    
    Write --> FormatSwitch
    FormatSwitch --> Template
    Template --> SarifCheck
    
    SarifCheck -->|"Yes (Deprecated)"| SarifWriter
    SarifCheck -->|"No"| NewTW
    
    NewTW --> TW_Write
```

**Sources:** [pkg/report/writer.go:82-94](), [pkg/report/sarif.go:128-181]()

### Backward Compatibility
Trivy maintains a special check for the legacy `sarif.tpl` template. If a user provides `--template @sarif.tpl`, Trivy logs a warning and redirects execution to the dedicated `SarifWriter` instead of the generic `TemplateWriter`.

**Sources:** [pkg/report/writer.go:84-91]()

---

## Template Execution Flow

1. **Initialization:** `NewTemplateWriter` reads the template source (inline or file) [pkg/report/template.go:32]().
2. **Function Mapping:** Sprig functions and custom functions (`escapeXML`, etc.) are registered [pkg/report/template.go:40-61]().
3. **Parsing:** The template is parsed into a `text/template.Template` object [pkg/report/template.go:66]().
4. **Execution:** The `Write` method executes the template against `report.Results` [pkg/report/template.go:78]().

**Sources:** [pkg/report/template.go:26-83]()

---

# Page: Compliance and Summary Reports

# Compliance and Summary Reports

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [pkg/compliance/report/report_test.go](pkg/compliance/report/report_test.go)
- [pkg/compliance/spec/compliance.go](pkg/compliance/spec/compliance.go)
- [pkg/compliance/spec/compliance_test.go](pkg/compliance/spec/compliance_test.go)
- [pkg/compliance/spec/custom.go](pkg/compliance/spec/custom.go)
- [pkg/compliance/spec/mapper.go](pkg/compliance/spec/mapper.go)
- [pkg/compliance/spec/mapper_test.go](pkg/compliance/spec/mapper_test.go)
- [pkg/compliance/spec/testdata/testcache/policy/content/specs/compliance/invalid.yaml](pkg/compliance/spec/testdata/testcache/policy/content/specs/compliance/invalid.yaml)
- [pkg/compliance/spec/testdata/testcache/policy/content/specs/compliance/testspec.yaml](pkg/compliance/spec/testdata/testcache/policy/content/specs/compliance/testspec.yaml)
- [pkg/compliance/spec/testdata/testcache/policy/metadata.json](pkg/compliance/spec/testdata/testcache/policy/metadata.json)
- [pkg/flag/kubernetes_flags.go](pkg/flag/kubernetes_flags.go)
- [pkg/k8s/commands/cluster.go](pkg/k8s/commands/cluster.go)
- [pkg/k8s/commands/run.go](pkg/k8s/commands/run.go)
- [pkg/k8s/report/report.go](pkg/k8s/report/report.go)
- [pkg/k8s/report/report_test.go](pkg/k8s/report/report_test.go)
- [pkg/k8s/report/summary.go](pkg/k8s/report/summary.go)
- [pkg/k8s/report/summary_test.go](pkg/k8s/report/summary_test.go)
- [pkg/k8s/report/table.go](pkg/k8s/report/table.go)
- [pkg/k8s/scanner/scanner.go](pkg/k8s/scanner/scanner.go)
- [pkg/k8s/writer_test.go](pkg/k8s/writer_test.go)

</details>



## Purpose and Scope

This document covers two specialized reporting mechanisms in Trivy:

1.  **Compliance Reports**: Reports generated against compliance specifications (e.g., CIS benchmarks, NSA guidelines) that map security findings to compliance controls.
2.  **Summary Reports**: Consolidated and simplified views of scan results, particularly for Kubernetes cluster scans that aggregate findings across multiple resources.

For information about basic report formats (JSON, SARIF, table, etc.), see [Report Writers and Format Selection](7.1). For custom template-based reports, see [Template-Based Custom Reports](7.3).

## Compliance Report Generation

### Activation and Dispatch

Compliance reporting is activated when `option.Compliance.Spec.ID` is non-empty. In Kubernetes scans, the `runner.run` function checks if a compliance spec is provided. If so, it extracts the required scanners from the specification and overrides the default scan options [pkg/k8s/commands/run.go:72-78]().

The `runner` then executes the scan and processes the results into a compliance-specific report:

```go
pkg/k8s/commands/run.go:92-106
	if r.flagOpts.Compliance.Spec.ID != "" {
		var scanResults []types.Results
		for _, rss := range rpt.Resources {
			scanResults = append(scanResults, rss.Results)
		}
		complianceReport, err := cr.BuildComplianceReport(scanResults, r.flagOpts.Compliance)
		if err != nil {
			return xerrors.Errorf("compliance report build error: %w", err)
		}
		return cr.Write(ctx, complianceReport, cr.Option{
			Format: r.flagOpts.Format,
			Report: r.flagOpts.ReportFormat,
			Output: output,
		})
	}
```

**Diagram: Compliance Report Flow**

```mermaid
graph TB
    subgraph "Natural Language Space"
    UserReq["User requests CIS Benchmark report"]
    end

    subgraph "Code Entity Space"
    RunFunc["commands.Run()"]
    GetSpec["spec.GetComplianceSpec()"]
    ScannerNew["scanner.NewScanner()"]
    BuildReport["cr.BuildComplianceReport()"]
    CompWrite["cr.Write()"]
    
    RunFunc --> GetSpec
    GetSpec --> ScannerNew
    ScannerNew -->|"Scan Results"| BuildReport
    BuildReport --> CompWrite
    end
    
    UserReq -.-> RunFunc
```

Sources: [pkg/k8s/commands/run.go:72-106](), [pkg/compliance/spec/compliance.go:98-132]()

### Scanner Selection for Compliance

The `ComplianceSpec` determines which scanners are necessary by inspecting the prefixes of the check IDs defined in the controls [pkg/compliance/spec/compliance.go:33-45]().

| Check ID Prefix | Resulting Scanner |
| :--- | :--- |
| `cve-`, `dla-`, `vuln-` | `types.VulnerabilityScanner` |
| `secret-` | `types.SecretScanner` |
| `avd-`, `ksv-`, `kcv-`, `kube-` | `types.MisconfigScanner` |

Sources: [pkg/compliance/spec/compliance.go:59-74](), [pkg/compliance/spec/compliance.go:76-80]()

## Summary Reports for Kubernetes

### Report Types

Kubernetes reports support two primary modes via the `--report` flag [pkg/k8s/report/report.go:21-22]():

| Report Type | Constant | Description |
| :--- | :--- | :--- |
| `summary` | `SummaryReport` | Consolidated table with severity counts per resource. |
| `all` | `AllReport` | Detailed findings for every resource scanned. |

The `TableWriter` dispatches to the appropriate logic based on this selection [pkg/k8s/report/table.go:54-82]().

### Report Consolidation

The `consolidate()` method merges findings from multiple resources with the same namespace, kind, and name. This is essential in Kubernetes where a single workload (e.g., a Deployment) might yield multiple `Resource` objects (one for misconfigurations and one for each container image vulnerability) [pkg/k8s/report/report.go:82-129]().

**Diagram: K8s Report Consolidation Logic**

```mermaid
graph LR
    subgraph "Input Resources"
    R1["Resource: nginx (Misconfig)"]
    R2["Resource: nginx (Vulns)"]
    end

    subgraph "Logic: report.consolidate()"
    Fullname["r.fullname() -> 'default/deploy/nginx'"]
    Index["map[string]Resource"]
    Merge["Combine Results & Metadata"]
    end

    subgraph "Output"
    Consolidated["ConsolidatedReport.Findings"]
    end

    R1 --> Fullname
    R2 --> Fullname
    Fullname --> Index
    Index --> Merge
    Merge --> Consolidated
```

Sources: [pkg/k8s/report/report.go:82-129](), [pkg/k8s/report/report.go:68-70]()

### Summary Writer Implementation

The `SummaryWriter` generates a table with severity counts. It uses `accumulateSeverityCounts` to traverse the results and tally vulnerabilities, misconfigurations, and secrets by their severity level [pkg/k8s/report/summary.go:164-183]().

The writer configures headers dynamically based on the enabled scanners and required severities [pkg/k8s/report/summary.go:185-213]().

Sources: [pkg/k8s/report/summary.go:19-36](), [pkg/k8s/report/summary.go:66-126]()

## Report Separation by Component Type

Trivy categorizes Kubernetes findings into three distinct assessments to improve readability [pkg/k8s/report/report.go:145-208]():

1.  **Workload Assessment**: General applications and services.
2.  **Infra Assessment**: Core components in the `kube-system` namespace or node-level findings (e.g., `NodeInfo`, `NodeComponents`) [pkg/k8s/report/report.go:219-221]().
3.  **RBAC Assessment**: Security checks for `Role`, `ClusterRole`, and their respective bindings [pkg/k8s/report/report.go:210-217]().

### Column Configuration

Each assessment type uses a specific set of columns for the summary table [pkg/k8s/report/table.go:34-52]():

| Assessment | Columns |
| :--- | :--- |
| Workload | Vulnerabilities, Misconfigurations, Secrets |
| Infra | Vulnerabilities, Misconfigurations, Secrets |
| RBAC | RBAC Assessment |

Sources: [pkg/k8s/report/report.go:145-208](), [pkg/k8s/report/table.go:25-32]()

## Validation and Requirements

### Report Format Validation

To prevent terminal "flooding," Trivy enforces a validation rule: full-cluster scanning with `--format table` requires an explicit `--report all` flag. If not set, it defaults to a warning suggesting the summary report [pkg/k8s/commands/run.go:132-143]().

```go
pkg/k8s/commands/run.go:132-140
func validateReportArguments(opts flag.Options) error {
	if opts.ReportFormat == "all" &&
		!viper.IsSet("report") &&
		opts.Format == "table" {

		m := "All the results in the table format can mess up your terminal. Use \"--report all\" to tell Trivy to output it to your terminal anyway, or consider \"--report summary\" to show the summary output."

		return xerrors.New(m)
	}
```

Sources: [pkg/k8s/commands/run.go:132-143]()

---

# Page: Deployment Models

# Deployment Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [helm/trivy/.helmignore](helm/trivy/.helmignore)
- [helm/trivy/Chart.yaml](helm/trivy/Chart.yaml)
- [helm/trivy/README.md](helm/trivy/README.md)
- [helm/trivy/templates/NOTES.txt](helm/trivy/templates/NOTES.txt)
- [helm/trivy/templates/_helpers.tpl](helm/trivy/templates/_helpers.tpl)
- [helm/trivy/templates/configmap.yaml](helm/trivy/templates/configmap.yaml)
- [helm/trivy/templates/ingress.yaml](helm/trivy/templates/ingress.yaml)
- [helm/trivy/templates/podsecuritypolicy.yaml](helm/trivy/templates/podsecuritypolicy.yaml)
- [helm/trivy/templates/role.yaml](helm/trivy/templates/role.yaml)
- [helm/trivy/templates/rolebinding.yaml](helm/trivy/templates/rolebinding.yaml)
- [helm/trivy/templates/secret.yaml](helm/trivy/templates/secret.yaml)
- [helm/trivy/templates/service.yaml](helm/trivy/templates/service.yaml)
- [helm/trivy/templates/serviceaccount.yaml](helm/trivy/templates/serviceaccount.yaml)
- [helm/trivy/templates/statefulset.yaml](helm/trivy/templates/statefulset.yaml)
- [helm/trivy/values.yaml](helm/trivy/values.yaml)
- [integration/client_server_test.go](integration/client_server_test.go)
- [integration/docker_engine_test.go](integration/docker_engine_test.go)
- [integration/integration_test.go](integration/integration_test.go)
- [integration/registry_test.go](integration/registry_test.go)
- [integration/repo_test.go](integration/repo_test.go)
- [integration/sbom_test.go](integration/sbom_test.go)
- [integration/standalone_tar_test.go](integration/standalone_tar_test.go)
- [integration/testdata/fixtures/db/vulnerability.yaml](integration/testdata/fixtures/db/vulnerability.yaml)
- [integration/testdata/fluentd-multiple-lockfiles.json.golden](integration/testdata/fluentd-multiple-lockfiles.json.golden)
- [pkg/cache/remote.go](pkg/cache/remote.go)
- [pkg/cache/remote_test.go](pkg/cache/remote_test.go)
- [pkg/rpc/client/client.go](pkg/rpc/client/client.go)
- [pkg/rpc/client/client_test.go](pkg/rpc/client/client_test.go)
- [pkg/rpc/convert.go](pkg/rpc/convert.go)
- [pkg/rpc/convert_test.go](pkg/rpc/convert_test.go)
- [pkg/rpc/server/server.go](pkg/rpc/server/server.go)
- [pkg/rpc/server/server_test.go](pkg/rpc/server/server_test.go)
- [rpc/cache/service.pb.go](rpc/cache/service.pb.go)
- [rpc/cache/service.proto](rpc/cache/service.proto)
- [rpc/cache/service.twirp.go](rpc/cache/service.twirp.go)
- [rpc/common/service.pb.go](rpc/common/service.pb.go)
- [rpc/common/service.proto](rpc/common/service.proto)
- [rpc/scanner/service.pb.go](rpc/scanner/service.pb.go)
- [rpc/scanner/service.proto](rpc/scanner/service.proto)
- [rpc/scanner/service.twirp.go](rpc/scanner/service.twirp.go)

</details>



This document covers the different ways Trivy can be deployed and operated in various environments. It focuses on the architectural patterns, configuration options, and code structures that enable each deployment model.

For information about specific target types and scanning capabilities, see [Scanning Capabilities](#4). For detailed CLI command reference, see [CLI Reference](#2).

## Overview

Trivy supports multiple deployment models that affect how scanning services are initialized and executed. The deployment model determines whether scanning occurs locally or remotely, how databases are managed, and which service implementations are used.

### Core Service Selection Logic

The deployment model is primarily determined by the `ServerAddr` configuration option, which controls service initialization throughout the scanning pipeline.

**Diagram: Command Flow and Service Selection**

```mermaid
graph TD
    subgraph "CLI_Entry_Points"
        NewApp["NewApp()<br/>pkg/commands/app.go:67"]
        ImageCmd["NewImageCommand<br/>pkg/commands/app.go:236"]
        FilesystemCmd["NewFilesystemCommand<br/>pkg/commands/app.go:329"]
        ServerCmd["NewServerCommand<br/>pkg/commands/server/server.go"]
    end
    
    subgraph "Artifact_Runner"
        ArtifactRun["artifact.Run()<br/>pkg/commands/artifact/run.go:379"]
        NewRunner["NewRunner()<br/>pkg/commands/artifact/run.go:121"]
        ScannerConfig["ScannerConfig<br/>pkg/commands/artifact/run.go:64"]
    end
    
    subgraph "Service_Implementations"
        StandaloneInit["InitializeScanService<br/>standalone functions"]
        RemoteInit["InitializeScanService<br/>remote functions"]
        ServerImpl["ScanServer<br/>pkg/rpc/server/server.go:21"]
    end
    
    NewApp --> ImageCmd
    NewApp --> FilesystemCmd  
    NewApp --> ServerCmd
    
    ImageCmd --> ArtifactRun
    FilesystemCmd --> ArtifactRun
    ArtifactRun --> NewRunner
    NewRunner --> ScannerConfig
    
    ScannerConfig --> StandaloneInit
    ScannerConfig --> RemoteInit
    ServerCmd --> ServerImpl
```

**Sources:** [pkg/commands/app.go:67-115](), [pkg/commands/artifact/run.go:64-77](), [pkg/commands/artifact/run.go:121-174](), [pkg/rpc/server/server.go:21-48]()

### Deployment Mode Detection

The deployment mode is determined by examining the `opts.ServerAddr` and `opts.Listen` fields during service initialization:

| Condition | Service Type | Implementation |
|-----------|-------------|----------------|
| `opts.ServerAddr == ""` | Standalone | Local scanning with embedded database |
| `opts.ServerAddr != ""` | Client | Remote scanning via RPC using `client.Scanner` |
| `opts.Listen != ""` | Server | RPC server hosting scan services via `server.ScanServer` |

**Sources:** [pkg/commands/artifact/run.go:199-220](), [pkg/commands/artifact/run.go:222-248]()

## Standalone Mode

Standalone mode operates as a single binary with embedded scanning services and local database management. It is the default mode of operation where Trivy performs analysis, vulnerability matching, and reporting on the same machine.

For details, see [Standalone Mode](#8.1).

### Service Initialization Architecture

The standalone mode uses target-specific service initializers that embed all scanning functionality, including database initialization through `r.initDB()` [pkg/commands/artifact/run.go:325]().

**Diagram: Standalone Service Initialization Flow**

```mermaid
graph TB
    subgraph "Command_Layer"
        ImageCommand["NewImageCommand<br/>pkg/commands/app.go:236"]
        ArtifactRun["artifact.Run<br/>pkg/commands/app.go:316"]
    end
    
    subgraph "Runner_Setup"
        NewRunner["NewRunner()<br/>pkg/commands/artifact/run.go:121"]
        InitDB["r.initDB()<br/>pkg/commands/artifact/run.go:325"]
        InitJavaDB["r.initJavaDB()<br/>pkg/commands/artifact/run.go:353"]
    end
    
    subgraph "Scan_Execution"
        ScanImage["r.ScanImage()<br/>pkg/commands/artifact/run.go:199"]
        ServiceCheck{"opts.ServerAddr check"}
        StandaloneService["imageStandaloneScanService<br/>pkg/commands/artifact/run.go:213"]
    end
    
    ImageCommand --> ArtifactRun
    ArtifactRun --> NewRunner
    NewRunner --> InitDB
    NewRunner --> InitJavaDB
    NewRunner --> ScanImage
    ScanImage --> ServiceCheck
    ServiceCheck -->|"ServerAddr empty"| StandaloneService
```

**Sources:** [pkg/commands/artifact/run.go:121-174](), [pkg/commands/artifact/run.go:199-220](), [pkg/commands/artifact/run.go:325-376]()

## Client-Server Architecture

The client-server model splits scanning into a centralized `ScanServer` and lightweight clients. This model is useful for CI/CD environments where you want to avoid downloading the vulnerability database on every build agent.

For details, see [Client-Server Architecture](#8.2).

### Server Implementation

The server is implemented through the `ScanServer` struct [pkg/rpc/server/server.go:21]() which wraps a local scanning backend and exposes it via RPC. It supports authentication via `serverToken` [helm/trivy/values.yaml:125]().

**Diagram: RPC Server Architecture**

```mermaid
graph TB
    subgraph "RPC_Server_Core"
        ScanServer["ScanServer struct<br/>pkg/rpc/server/server.go:21"]
        LocalBackend["s.local scan.Service<br/>pkg/scan/local/local.go"]
        ScanMethod["Scan() method<br/>pkg/rpc/server/server.go:39"]
    end
    
    subgraph "Protocol_Layer"
        TwirpHandler["Twirp HTTP Handler<br/>rpc/scanner/service.twirp.go"]
        ScanRequest["ScanRequest message<br/>rpc/scanner/service.proto"]
        ScanResponse["ScanResponse message<br/>rpc/scanner/service.proto"]
    end
    
    TwirpHandler --> ScanServer
    ScanServer --> ScanMethod
    ScanMethod --> LocalBackend
    TwirpHandler --> ScanRequest
    ScanServer --> ScanResponse
```

**Sources:** [pkg/rpc/server/server.go:21-56](), [rpc/scanner/service.proto:1-50](), [integration/client_server_test.go:43-100]()

### RPC Protocol Structure

The RPC protocol uses Protocol Buffers (protobuf) for message serialization and Twirp for HTTP-based RPC. The conversion layer in `pkg/rpc/convert.go` translates between internal Trivy types and protobuf messages.

| Internal Type | RPC Message | Conversion Function |
|---------------|-------------|---------------------|
| `ftypes.Package` | `common.Package` | `ConvertToRPCPkgs` [pkg/rpc/convert.go:54]() |
| `ftypes.Secret` | `common.Secret` | `ConvertToRPCSecrets` [pkg/rpc/convert.go:151]() |
| `ftypes.Location` | `common.Location` | `ConvertToRPCLocations` [pkg/rpc/convert.go:101]() |

**Sources:** [pkg/rpc/convert.go:54-160](), [rpc/common/service.proto:33-71]()

## Kubernetes Deployment with Helm

Trivy can be deployed as a managed service within Kubernetes using the official Helm chart. This deployment typically runs Trivy in **Server Mode**.

For details, see [Kubernetes Deployment with Helm](#8.3).

### Helm Chart Resources

The Helm chart [helm/trivy/Chart.yaml]() bootstraps a `StatefulSet` [helm/trivy/templates/statefulset.yaml:2]() to provide persistent storage for the vulnerability database.

**Diagram: Kubernetes Deployment Components**

```mermaid
graph TB
    subgraph "Kubernetes_Cluster"
        StatefulSet["StatefulSet<br/>trivy-server"]
        Service["Service<br/>trivy-http:4954"]
        PVC["PersistentVolumeClaim<br/>trivy-db-storage"]
        Secret["Secret<br/>trivy-credentials"]
    end
    
    subgraph "Trivy_Pod"
        MainContainer["Main Container<br/>aquasec/trivy:latest"]
        HealthCheck["Liveness/Readiness<br/>/healthz"]
    end
    
    StatefulSet --> MainContainer
    MainContainer --> PVC
    MainContainer --> Secret
    Service --> StatefulSet
    MainContainer --> HealthCheck
```

**Sources:** [helm/trivy/values.yaml:15-59](), [helm/trivy/templates/statefulset.yaml:100-120](), [helm/trivy/templates/service.yaml:1-10]()

### Configuration Parameters

Key configuration options in `values.yaml` include:
* `trivy.cache.redis`: Support for Redis as a distributed caching backend [helm/trivy/values.yaml:113]().
* `persistence.enabled`: Enables `PersistentVolumeClaim` to reduce DB downloads [helm/trivy/values.yaml:16]().
* `podSecurityContext`: Configures non-root execution (default UID 65534) [helm/trivy/values.yaml:34]().

**Sources:** [helm/trivy/values.yaml:15-133](), [helm/trivy/README.md:105-112]()

---

# Page: Standalone Mode

# Standalone Mode

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cmd/trivy/main.go](cmd/trivy/main.go)
- [integration/client_server_test.go](integration/client_server_test.go)
- [integration/docker_engine_test.go](integration/docker_engine_test.go)
- [integration/integration_test.go](integration/integration_test.go)
- [integration/registry_test.go](integration/registry_test.go)
- [integration/repo_test.go](integration/repo_test.go)
- [integration/sbom_test.go](integration/sbom_test.go)
- [integration/standalone_tar_test.go](integration/standalone_tar_test.go)
- [integration/testdata/fixtures/db/vulnerability.yaml](integration/testdata/fixtures/db/vulnerability.yaml)
- [integration/testdata/fluentd-multiple-lockfiles.json.golden](integration/testdata/fluentd-multiple-lockfiles.json.golden)
- [internal/dbtest/db.go](internal/dbtest/db.go)
- [pkg/commands/operation/operation.go](pkg/commands/operation/operation.go)
- [pkg/commands/server/run.go](pkg/commands/server/run.go)
- [pkg/db/db.go](pkg/db/db.go)
- [pkg/db/db_test.go](pkg/db/db_test.go)
- [pkg/policy/policy.go](pkg/policy/policy.go)
- [pkg/policy/policy_test.go](pkg/policy/policy_test.go)
- [pkg/rpc/server/listen.go](pkg/rpc/server/listen.go)
- [pkg/rpc/server/listen_test.go](pkg/rpc/server/listen_test.go)
- [pkg/version/version.go](pkg/version/version.go)
- [pkg/version/version_test.go](pkg/version/version_test.go)

</details>



Standalone mode is Trivy's default deployment model where all scanning operations, vulnerability detection, and analysis occur within a single local process. This page explains how standalone mode operates, including database management, caching mechanisms, and the complete scanning workflow.

For information about distributed scanning using a remote Trivy server, see [Client/Server Architecture](8.2). For Kubernetes deployment with persistent services, see [Kubernetes Deployment with Helm](8.3).

## Overview

Standalone mode is Trivy's default deployment model where a single process executes all scanning operations locally. When `opts.ServerAddr` is empty (no `--server` flag provided), Trivy initializes the vulnerability database, artifact cache, and WASM modules within the local process, performs all analysis, and outputs results.

### Key Characteristics

| Aspect | Implementation |
|--------|---------------|
| **Mode Detection** | `opts.ServerAddr == ""` in service selection logic |
| **Database Location** | `<cacheDir>/db/trivy.db` (typically `~/.cache/trivy/db/`) |
| **Database Format** | BoltDB opened in read-only mode via `db.Init()` |
| **Database Updates** | Checked via `db.Client.NeedsUpdate()`, skipped with `--skip-db-update` |
| **Cache Backend** | `cache.TypeFS` (default), `cache.TypeRedis`, or `cache.TypeMemory` |
| **Process Lifecycle** | Created in `NewRunner()`, closed in `runner.Close()` |
| **Network Dependencies** | OCI registry for DB download, container registry for image pulls |
| **Scanner Execution** | All scanners execute via `local.Scanner` within the process |

Sources: [pkg/db/db.go:42-46](), [pkg/db/db.go:79-81](), [pkg/commands/operation/operation.go:31-33]()

## Architecture

### Standalone Mode Component Initialization

The following diagram shows how standalone mode initializes its components, mapping natural language concepts to actual code entities:

```mermaid
graph TB
    subgraph "Entry Point"
        CLICommand["main.run()"]
        ArtifactRun["commands.Run(ctx)"]
    end
    
    subgraph "Database Layer"
        OperationDownloadDB["operation.DownloadDB"]
        DBClient["db.Client{}<br/>dir: cacheDir/db"]
        DBClientNeedsUpdate["db.Client.NeedsUpdate()"]
        DBClientDownload["db.Client.Download()"]
        DBInit["db.Init(db.Dir(cacheDir))"]
        BoltDBOpen["db.Init(dbDir, opts...)<br/>ReadOnly: true"]
    end
    
    subgraph "Server Mode Check"
        ServerRun["server.Run(ctx, opts)"]
        ServerListen["rpcServer.ListenAndServe"]
        DBWorker["server.newDBWorker"]
    end
    
    CLICommand --> ArtifactRun
    ArtifactRun --> OperationDownloadDB
    ArtifactRun --> ServerRun
    
    ServerRun --> DBInit
    ServerRun --> ServerListen
    ServerListen --> DBWorker
    
    OperationDownloadDB --> DBClient
    DBClient --> DBClientNeedsUpdate
    DBClientNeedsUpdate --> DBClientDownload
    DBClientDownload --> DBInit
    DBInit --> BoltDBOpen
```

Sources: [cmd/trivy/main.go:34-51](), [pkg/commands/operation/operation.go:25-50](), [pkg/db/db.go:42-46](), [pkg/commands/server/run.go:19-63]()

### Service Selection and Workflow

Trivy uses `db.Client` to manage the local state of the vulnerability database. In standalone mode, this client is responsible for both checking the update status and performing the actual download from OCI registries.

```mermaid
graph TD
    subgraph "Vulnerability DB Orchestration"
        NeedsUpdate["db.Client.NeedsUpdate"]
        Download["db.Client.Download"]
        Init["db.Init"]
    end

    subgraph "Metadata Handling"
        MetaGet["metadata.Client.Get()"]
        MetaUpdate["metadata.Client.Update()"]
    end

    NeedsUpdate --> MetaGet
    Download --> MetaUpdate
    Download --> Init
```

Sources: [pkg/db/db.go:105-117](), [pkg/db/db.go:187-196](), [pkg/db/db.go:205-222]()

## Database Management

### Database Initialization Flow

Standalone mode ensures the vulnerability database is present and up-to-date before any scanning occurs. The logic is centralized in `pkg/db/db.go`.

```mermaid
graph TB
    Start["operation.DownloadDB"]
    CheckNeedsUpdate["db.Client.NeedsUpdate"]
    
    CheckFirstRun{"First Run?<br/>(No trivy.db or<br/>metadata.json)"}
    CheckSkipFlag{"--skip-db-update<br/>flag set?"}
    CheckSchema{"DB Schema<br/>Version<br/>Match?"}
    CheckNextUpdate{"Now < NextUpdate<br/>&&<br/>DownloadedAt recent?"}
    
    ErrorFirstRun["Error: Cannot skip<br/>on first run"]
    ErrorOldSchema["Error: Update Trivy<br/>or use compatible DB"]
    SkipUpdate["Skip DB Update"]
    DownloadFromOCI["db.Client.Download"]
    
    DBInit["db.Init<br/>(Read-only BoltDB)"]
    Complete["Continue to Scanning"]
    
    Start --> CheckNeedsUpdate
    CheckNeedsUpdate --> CheckFirstRun
    
    CheckFirstRun -->|Yes| CheckSkipFlag
    CheckSkipFlag -->|Yes| ErrorFirstRun
    CheckSkipFlag -->|No| DownloadFromOCI
    
    CheckFirstRun -->|No| CheckSchema
    CheckSchema -->|Newer Local DB| ErrorOldSchema
    CheckSchema -->|Match| CheckSkipFlag
    
    CheckSkipFlag -->|Yes| SkipUpdate
    CheckSkipFlag -->|No| CheckNextUpdate
    
    CheckNextUpdate -->|Yes| SkipUpdate
    CheckNextUpdate -->|No| DownloadFromOCI
    
    DownloadFromOCI --> DBInit
    SkipUpdate --> DBInit
    DBInit --> Complete
```

Sources: [pkg/db/db.go:105-161](), [pkg/commands/operation/operation.go:25-50]()

### Local Database File Structure

Standalone mode stores all databases and caches in the local filesystem at `cacheDir`:

| Path | Purpose | Access Pattern |
|------|---------|---------------|
| `<cacheDir>/db/trivy.db` | Main vulnerability database (BoltDB) | Opened read-only via `db.Init()` |
| `<cacheDir>/db/metadata.json` | DB version, update times, next update schedule | Read by `metadata.NewClient()` |
| `<cacheDir>/fanal/` | Artifact analysis cache (layers, packages, configs) | Managed by cache system |
| `<cacheDir>/policy/` | Rego policy bundles | Managed by `policy.Client` |

Sources: [pkg/db/db.go:79-81](), [pkg/db/db.go:99](), [pkg/db/db.go:42-46](), [pkg/commands/operation/operation.go:31-33]()

### Database Update Logic

The `db.Client.NeedsUpdate` method determines if a database update is required by checking the local `metadata.json` against the expected `SchemaVersion`.

| Condition | Action | Logic Source |
|-----------|--------|--------------|
| `trivy.db` missing | Return `true` | [pkg/db/db.go:107-110]() |
| `metadata.json` missing | Return `true` | [pkg/db/db.go:111-117]() |
| `SchemaVersion` mismatch | Return `true` (if local is old) | [pkg/db/db.go:154-158]() |
| `NextUpdate` not reached | Return `false` | [pkg/db/db.go:173-177]() |
| Downloaded within 1 hour | Return `false` | [pkg/db/db.go:179-183]() |

Sources: [pkg/db/db.go:105-184]()

### Database Download Process

When an update is needed, Trivy downloads the database from OCI registries. The client defaults to GHCR and GCR mirrors.

**Default Repositories:**
- Primary: `mirror.gcr.io/aquasec/trivy-db:2`
- Fallback: `ghcr.io/aquasecurity/trivy-db:2`

Sources: [pkg/db/db.go:31-36](), [pkg/db/db.go:85-90](), [pkg/db/db.go:187-196]()

## Artifact Cache Management

### Cache Initialization

In standalone mode, the cache is initialized during command execution. While the CLI handles the setup, the underlying implementation can be Filesystem, Redis, or Memory based.

```mermaid
graph TD
    CacheNew["cache.New(opts)"]
    CacheCleanup["cleanup()"]
    
    subgraph "Backend Options"
        FS["FSCache"]
        Redis["RedisCache"]
    end
    
    CacheNew --> FS
    CacheNew --> Redis
```

Sources: [pkg/commands/server/run.go:30-34](), [pkg/rpc/server/listen.go:63-69]()

## Server Mode DB Maintenance

Even when running as a server (which is technically a long-running standalone-like process for DB management), Trivy performs "hot updates" to ensure the database remains current without interrupting active requests.

```mermaid
sequenceDiagram
    participant Worker as dbWorker
    participant Client as db.Client
    participant FS as Filesystem
    
    loop Every 1 Hour
        Worker->>Client: NeedsUpdate()
        alt Update Required
            Worker->>Client: Download(tmpDir)
            Worker->>FS: Suspend Requests (WaitGroups)
            Worker->>Client: Close()
            Worker->>FS: Copy trivy.db from tmpDir
            Worker->>Client: Init(dbDir)
            Worker->>FS: Resume Requests
        end
    end
```

Sources: [pkg/rpc/server/listen.go:74-97](), [pkg/rpc/server/listen.go:175-190](), [pkg/rpc/server/listen.go:192-227]()

## Configuration and Usage

### Standalone Command Execution
The main entry point for standalone operations is through the subcommands (image, fs, repo) which eventually call into `operation` and `db` packages.

```go
// Example of DB initialization in standalone/server startup
if err = db.Init(db.Dir(opts.CacheDir)); err != nil {
    return xerrors.Errorf("error in vulnerability DB initialize: %w", err)
}
```
Sources: [pkg/commands/server/run.go:46-48]()

### DB Update Functional Options
The `db.Client` can be configured using functional options to override default repositories or provide a pre-configured OCI artifact.

| Option | Function | Source |
|--------|----------|--------|
| `WithOCIArtifact` | Use a specific OCI artifact for download | [pkg/db/db.go:57-61]() |
| `WithDBRepository` | Override default OCI repositories | [pkg/db/db.go:64-68]() |

Sources: [pkg/db/db.go:53-68]()

---

# Page: Client-Server Architecture

# Client-Server Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [integration/client_server_test.go](integration/client_server_test.go)
- [integration/docker_engine_test.go](integration/docker_engine_test.go)
- [integration/integration_test.go](integration/integration_test.go)
- [integration/registry_test.go](integration/registry_test.go)
- [integration/repo_test.go](integration/repo_test.go)
- [integration/sbom_test.go](integration/sbom_test.go)
- [integration/standalone_tar_test.go](integration/standalone_tar_test.go)
- [integration/testdata/fixtures/db/vulnerability.yaml](integration/testdata/fixtures/db/vulnerability.yaml)
- [integration/testdata/fluentd-multiple-lockfiles.json.golden](integration/testdata/fluentd-multiple-lockfiles.json.golden)
- [pkg/cache/remote.go](pkg/cache/remote.go)
- [pkg/cache/remote_test.go](pkg/cache/remote_test.go)
- [pkg/commands/operation/operation.go](pkg/commands/operation/operation.go)
- [pkg/commands/server/run.go](pkg/commands/server/run.go)
- [pkg/policy/policy.go](pkg/policy/policy.go)
- [pkg/policy/policy_test.go](pkg/policy/policy_test.go)
- [pkg/rpc/client/client.go](pkg/rpc/client/client.go)
- [pkg/rpc/client/client_test.go](pkg/rpc/client/client_test.go)
- [pkg/rpc/convert.go](pkg/rpc/convert.go)
- [pkg/rpc/convert_test.go](pkg/rpc/convert_test.go)
- [pkg/rpc/server/listen.go](pkg/rpc/server/listen.go)
- [pkg/rpc/server/listen_test.go](pkg/rpc/server/listen_test.go)
- [pkg/rpc/server/server.go](pkg/rpc/server/server.go)
- [pkg/rpc/server/server_test.go](pkg/rpc/server/server_test.go)
- [pkg/version/version.go](pkg/version/version.go)
- [pkg/version/version_test.go](pkg/version/version_test.go)
- [rpc/cache/service.pb.go](rpc/cache/service.pb.go)
- [rpc/cache/service.proto](rpc/cache/service.proto)
- [rpc/cache/service.twirp.go](rpc/cache/service.twirp.go)
- [rpc/common/service.pb.go](rpc/common/service.pb.go)
- [rpc/common/service.proto](rpc/common/service.proto)
- [rpc/scanner/service.pb.go](rpc/scanner/service.pb.go)
- [rpc/scanner/service.proto](rpc/scanner/service.proto)
- [rpc/scanner/service.twirp.go](rpc/scanner/service.twirp.go)

</details>



Trivy supports a client-server deployment model using RPC over HTTP. The server (`pkg/rpc/server`) maintains the vulnerability database and performs scans, while clients (`pkg/rpc/client`) submit scan requests and receive results. This architecture enables centralized database management, shared caching, and reduced client resource usage.

## Architecture Overview

Trivy's client-server mode separates concerns between two components:

**Server Component (`server.Server`)**
- Runs via `trivy server` command.
- Maintains local vulnerability database in `dbDir` [pkg/rpc/server/listen.go:37]().
- Exposes two RPC services: `Scanner` and `Cache` [pkg/rpc/server/listen.go:132-138]().
- Performs hot database updates every hour via `dbWorker` [pkg/rpc/server/listen.go:74-97]().
- Supports filesystem or Redis cache backends.

**Client Component (`client.Service`)**
- Runs via `trivy image --server <url>` or similar commands.
- Sends RPC requests to remote server via a Twirp-generated client [pkg/rpc/client/client.go:54]().
- Receives scan results over HTTP/Protobuf.
- Optionally uses `RemoteCache` for distributed caching [pkg/cache/remote.go:17]().

### Code Entity Map: Client-Server Interaction

The following diagram maps high-level architectural components to their specific implementation classes and functions.

```mermaid
flowchart TD
    subgraph "Client Space"
        CLI["CLI Command"]
        ClientSvc["pkg/rpc/client:Service"]
        TwirpClient["rpc/scanner:ScannerProtobufClient"]
        RemCache["pkg/cache:RemoteCache"]
    end
    
    subgraph "Server Space"
        Mux["pkg/rpc/server:NewServeMux"]
        ScanSrv["pkg/rpc/server:ScanServer"]
        CacheSrv["pkg/rpc/server:CacheServer"]
        DBW["pkg/rpc/server:dbWorker"]
        LocalSvc["pkg/scan/local:Service"]
    end
    
    CLI --> ClientSvc
    ClientSvc -- "Scan()" --> TwirpClient
    ClientSvc -- "MissingBlobs()" --> RemCache
    
    TwirpClient -- "POST /twirp/trivy.scanner.v1.Scanner/Scan" --> Mux
    RemCache -- "POST /twirp/trivy.cache.v1.Cache/..." --> Mux
    
    Mux --> ScanSrv
    Mux --> CacheSrv
    
    ScanSrv -- "Scan()" --> LocalSvc
    DBW -- "update()" --> DBW
```

Sources:
- [pkg/rpc/client/client.go:42-65]()
- [pkg/rpc/server/listen.go:32-60]()
- [pkg/rpc/server/server.go:29-48]()
- [pkg/commands/server/run.go:19-63]()

## Server Architecture

### Server Initialization

The server is initialized in `pkg/commands/server/run.go`. The logic involves downloading the DB via `operation.DownloadDB` [pkg/commands/operation/operation.go:25-50]() and initializing the server instance with `server.NewServer` [pkg/rpc/server/listen.go:48-60]().

### Server Struct and HTTP Endpoints

The `Server` struct [pkg/rpc/server/listen.go:32-45]() holds configuration and starts the HTTP server via `ListenAndServe`. It manages a `dbWorker` that triggers updates every `updateInterval` (1 hour) [pkg/rpc/server/listen.go:30]().

The HTTP server exposes multiple endpoints via `NewServeMux` [pkg/rpc/server/listen.go:109-155]():

| Endpoint | Handler | Purpose |
|----------|---------|---------|
| `/twirp/trivy.scanner.v1.Scanner/Scan` | `ScanServer` | Execute scans using `local.Service` |
| `/twirp/trivy.cache.v1.Cache/*` | `CacheServer` | Cache operations (PutArtifact, PutBlob, etc.) |
| `/healthz` | Inline Handler | Returns "ok" [pkg/rpc/server/listen.go:140-144]() |
| `/version` | Inline Handler | Returns `types.VersionInfo` [pkg/rpc/server/listen.go:146-152]() |

### Database Hot Update Worker

The `dbWorker` [pkg/rpc/server/listen.go:167-169]() ensures the server's vulnerability database stays current without downtime.

```mermaid
sequenceDiagram
    participant T as "Ticker (1h)"
    participant W as "dbWorker"
    participant C as "db.Client"
    participant WG as "sync.WaitGroup (dbUpdateWg)"
    
    T->>W: Trigger Update
    W->>C: NeedsUpdate()
    alt Update Required
        W->>W: hotUpdate()
        W->>C: Download(tmpDir)
        W->>WG: Add(1) [Block New Requests]
        Note over WG: Wait for active requests (requestWg.Wait())
        W->>C: Close()
        W->>W: fsutils.CopyFile(tmp, current)
        W->>C: Init(dbDir) [Reopen]
        W->>WG: Done() [Resume Requests]
    end
```

Sources:
- [pkg/rpc/server/listen.go:62-107]()
- [pkg/rpc/server/listen.go:109-155]()
- [pkg/rpc/server/listen.go:167-230]()
- [pkg/rpc/server/server.go:29-113]()

## Client Architecture

### Client Service Structure

The `client.Service` [pkg/rpc/client/client.go:42-47]() encapsulates the RPC communication. It uses `rpc.Scanner`, which is an interface generated by Twirp [rpc/scanner/service.twirp.go:34-40]().

### Scan Request Flow

When a client initiates a scan, it performs complex type conversion to bridge the internal domain models with the Protobuf definitions.

```mermaid
flowchart LR
    subgraph "Internal Types"
        IOpts["types.ScanOptions"]
        IRes["types.ScanResponse"]
    end
    
    subgraph "RPC Conversion (pkg/rpc/convert.go)"
        C1["ConvertToRPCPkgs"]
        C2["ConvertToRPCVulns"]
        C3["ConvertFromRPCResults"]
    end
    
    subgraph "Protobuf Types (rpc/common/service.pb.go)"
        RPkgs["common.Package"]
        RVulns["common.Vulnerability"]
    end
    
    IOpts --> C1 --> RPkgs
    IOpts --> C2 --> RVulns
    RVulns --> C3 --> IRes
```

**Key Steps**:
1. **Option Mapping**: `client.Scan` maps severity sources and relationships [pkg/rpc/client/client.go:73-85]().
2. **RPC Call**: The request is sent via `s.client.Scan(ctx, in)` [pkg/rpc/client/client.go:90]().
3. **Response Processing**: The result is converted back using `rpc.ConvertFromRPCResults` [pkg/rpc/client/client.go:99]().

Sources:
- [pkg/rpc/client/client.go:42-113]()
- [pkg/rpc/convert.go:54-82]()
- [pkg/rpc/convert.go:1017-1041]()

## RPC Protocol and Message Definitions

### Twirp and Protobuf

Trivy uses Protobuf to define its service contracts. The `Scanner` service [rpc/scanner/service.proto:9-11]() and `Cache` service [rpc/cache/service.proto:11-16]() are the primary interfaces.

**Message Structures**:
- **Package**: Includes `id`, `name`, `version`, `purl`, and `locations` [rpc/common/service.proto:33-60]().
- **Vulnerability**: Includes `vulnerability_id`, `severity`, `cvss` maps, and `fixed_version` [rpc/common/service.proto:128-153]().
- **Misconfiguration**: Tracks `successes`, `warnings`, and `failures` with `cause_metadata` [rpc/common/service.proto:79-87]().

Sources:
- [rpc/scanner/service.proto:9-43]()
- [rpc/cache/service.proto:11-75]()
- [rpc/common/service.proto:33-153]()

## Authentication

Authentication is implemented via a shared secret (token) passed in an HTTP header.

### Server-Side Validation
The server uses `withToken` middleware [pkg/rpc/server/listen.go:157-165]() to intercept requests. If a `token` is configured, it compares the value in `r.Header.Get(tokenHeader)` with the expected secret. If they do not match, it returns a `twirp.Unauthenticated` error.

### Client-Side Injection
The client injects the token using `twirp.WithHTTPRequestHeaders` [pkg/rpc/client/client.go:111](). This is managed via `ServiceOption.CustomHeaders` passed during initialization.

Sources:
- [pkg/rpc/server/listen.go:157-165]()
- [pkg/rpc/client/client.go:105-113]()

## Distributed Caching

In client-server mode, the client does not usually store results locally. Instead, it interacts with a `RemoteCache`.

### RemoteCache Operations
The `RemoteCache` [pkg/cache/remote.go:17-21]() delegates calls to the server's `Cache` service:
- **MissingBlobs**: The client sends a list of layer digests to the server to determine which ones need to be uploaded [pkg/cache/remote.go:88-111]().
- **PutBlob**: Uploads analyzed layer information (packages, OS, etc.) to the server [pkg/cache/remote.go:75-86]().

### Server Cache Backend
The `CacheServer` [pkg/rpc/server/server.go:115-121]() stores this data in the server's local cache (either FS-based or Redis). This allows multiple clients to benefit from layers already analyzed by other clients.

Sources:
- [pkg/cache/remote.go:17-141]()
- [pkg/rpc/server/server.go:115-169]()
- [rpc/cache/service.proto:11-16]()

---

# Page: Kubernetes Deployment with Helm

# Kubernetes Deployment with Helm

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [helm/trivy/.helmignore](helm/trivy/.helmignore)
- [helm/trivy/Chart.yaml](helm/trivy/Chart.yaml)
- [helm/trivy/README.md](helm/trivy/README.md)
- [helm/trivy/templates/NOTES.txt](helm/trivy/templates/NOTES.txt)
- [helm/trivy/templates/_helpers.tpl](helm/trivy/templates/_helpers.tpl)
- [helm/trivy/templates/configmap.yaml](helm/trivy/templates/configmap.yaml)
- [helm/trivy/templates/ingress.yaml](helm/trivy/templates/ingress.yaml)
- [helm/trivy/templates/podsecuritypolicy.yaml](helm/trivy/templates/podsecuritypolicy.yaml)
- [helm/trivy/templates/role.yaml](helm/trivy/templates/role.yaml)
- [helm/trivy/templates/rolebinding.yaml](helm/trivy/templates/rolebinding.yaml)
- [helm/trivy/templates/secret.yaml](helm/trivy/templates/secret.yaml)
- [helm/trivy/templates/service.yaml](helm/trivy/templates/service.yaml)
- [helm/trivy/templates/serviceaccount.yaml](helm/trivy/templates/serviceaccount.yaml)
- [helm/trivy/templates/statefulset.yaml](helm/trivy/templates/statefulset.yaml)
- [helm/trivy/values.yaml](helm/trivy/values.yaml)

</details>



This document describes the Helm chart for deploying Trivy as a server in Kubernetes clusters. The chart creates a StatefulSet that runs Trivy in server mode, enabling remote scanning via RPC protocol. For information about the client-server architecture itself and RPC protocol details, see [Client-Server Architecture](#8.2). For information about scanning Kubernetes clusters from the CLI, see [Kubernetes Cluster Scanning](#5.3).

## Purpose and Scope

The Trivy Helm chart bootstraps a Trivy deployment on a Kubernetes cluster using the Helm package manager. It deploys a centralized Trivy server that can be accessed by multiple Trivy clients for remote vulnerability scanning. This deployment model centralizes database management and reduces the overhead of database downloads across multiple scanning instances. The chart provisions persistent storage for the vulnerability database, configures security contexts, manages secrets, and optionally integrates with Redis for distributed caching.

Sources: [helm/trivy/README.md:1-113](), [helm/trivy/Chart.yaml:1-12]()

## Deployed Kubernetes Resources

The Helm chart creates the following Kubernetes resources to support a centralized Trivy server deployment:

```mermaid
graph TB
    subgraph "Helm Chart Resources"
        StatefulSet["StatefulSet<br/>trivy"]
        Service["Service<br/>ClusterIP:4954"]
        Ingress["Ingress<br/>(optional)"]
        ConfigMap["ConfigMap<br/>Environment Variables"]
        Secret["Secret<br/>Credentials"]
        ServiceAccount["ServiceAccount<br/>trivy"]
        Role["Role<br/>PSP Permissions"]
        RoleBinding["RoleBinding"]
        PVC["PersistentVolumeClaim<br/>data (5Gi)"]
        PSP["PodSecurityPolicy<br/>(optional)"]
    end
    
    subgraph "Pod Configuration"
        Container["Container: main (trivy server)<br/>Port: 4954"]
        TmpVolume["Volume: tmp-data<br/>emptyDir"]
        DataVolume["Volume: data<br/>PVC mount at /home/scanner/.cache"]
        SSLVolume["Volume: ssl-cert-dir<br/>hostPath (optional)"]
    end
    
    StatefulSet --> PVC
    StatefulSet --> Container
    StatefulSet --> ServiceAccount
    Container --> TmpVolume
    Container --> DataVolume
    Container --> SSLVolume
    Container --> ConfigMap
    Container --> Secret
    Service --> Container
    Ingress --> Service
    RoleBinding --> Role
    RoleBinding --> ServiceAccount
    Role --> PSP
```

**Deployment Resource Hierarchy**: The `StatefulSet` manages pods running `trivy server`, with persistent storage for the vulnerability database. The `Service` exposes the server on port 4954, and an optional `Ingress` provides external access.

Sources: [helm/trivy/templates/statefulset.yaml:1-149](), [helm/trivy/templates/service.yaml:1-18](), [helm/trivy/templates/ingress.yaml:1-54]()

## StatefulSet Configuration

The core deployment uses a `StatefulSet` rather than a `Deployment` to maintain stable persistent storage across pod restarts and updates.

### StatefulSet Specification

The StatefulSet is defined in [helm/trivy/templates/statefulset.yaml:1-149]() with the following key characteristics:

| Configuration | Value/Description |
|--------------|-------------------|
| **Pod Management Policy** | `Parallel` [statefulset.yaml:11]() |
| **Replica Count** | Configurable via `replicaCount` (default: 1) [statefulset.yaml:13]() |
| **Service Name** | `{{ include "trivy.fullname" . }}` [statefulset.yaml:12]() |
| **Container Image** | `docker.io/aquasec/trivy:{appVersion}` [statefulset.yaml:70]() |
| **Container Args** | `["server"]` [statefulset.yaml:76-77]() |
| **Container Port** | `4954` [statefulset.yaml:102]() |

The StatefulSet runs the Trivy binary with the `server` argument, which starts Trivy in server mode listening on port 4954. The server exposes an RPC interface for remote scanning operations.

Sources: [helm/trivy/templates/statefulset.yaml:1-149](), [helm/trivy/values.yaml:13]()

### Image Configuration

Image settings are templated using the `trivy.imageRef` helper function defined in [helm/trivy/templates/_helpers.tpl:50-55]():

```
{{- define "trivy.imageRef" -}}
{{- $registryName := .Values.image.registry -}}
{{- $repositoryName := .Values.image.repository -}}
{{- $tag := .Values.image.tag | default .Chart.AppVersion | toString -}}
{{- printf "%s/%s:%s" $registryName $repositoryName $tag -}}
{{- end -}}
```

Default image values from [helm/trivy/values.yaml:4-11]():

| Parameter | Default Value | Purpose |
|-----------|--------------|---------|
| `image.registry` | `docker.io` | Container registry |
| `image.repository` | `aquasec/trivy` | Image repository |
| `image.tag` | `""` (uses `appVersion` from `Chart.yaml`) | Image version |
| `image.pullPolicy` | `IfNotPresent` | Pull policy |
| `image.pullSecret` | `""` | `imagePullSecret` name |

Sources: [helm/trivy/templates/_helpers.tpl:50-55](), [helm/trivy/values.yaml:4-11]()

## Persistent Storage Configuration

The chart uses a `PersistentVolumeClaim` to store the vulnerability database and cache, reducing database download frequency across pod restarts and updates.

```mermaid
graph LR
    subgraph "Storage Flow"
        PVC["PersistentVolumeClaim<br/>name: data<br/>size: 5Gi<br/>accessMode: ReadWriteOnce"]
        Volume["Pod Volume Mount<br/>/home/scanner/.cache"]
        CacheDir["TRIVY_CACHE_DIR<br/>/home/scanner/.cache/trivy"]
        DBLocation["trivy.db Location<br/>/home/scanner/.cache/trivy/db/trivy.db"]
    end
    
    PVC --> Volume
    Volume --> CacheDir
    CacheDir --> DBLocation
```

**Persistent Storage Architecture**: The PVC is mounted at `/home/scanner/.cache` where Trivy stores its vulnerability database (`trivy.db`) and Java database (`trivy-java-db`).

### Volume Claim Template

The StatefulSet includes a `volumeClaimTemplates` when persistence is enabled [statefulset.yaml:18-31]():

| Parameter | Default | Description |
|-----------|---------|-------------|
| `persistence.enabled` | `true` | Enable PVC creation |
| `persistence.size` | `5Gi` | Storage size |
| `persistence.accessMode` | `ReadWriteOnce` | Access mode |
| `persistence.storageClass` | `""` | Storage class (uses cluster default) |

The chart documentation recommends using a `storageClass` with `Retain` reclaim policy to prevent data loss during chart uninstallation [helm/trivy/README.md:107]().

### Volume Mounts

Three volumes are mounted in the container [statefulset.yaml:121-132]():

1. **tmp-data**: `emptyDir` volume at `/tmp` for temporary files [statefulset.yaml:122-124]()
2. **data**: PVC or `emptyDir` at `/home/scanner/.cache` for database storage [statefulset.yaml:125-127]()
3. **ssl-cert-dir**: Optional `hostPath` mount for custom SSL certificates [statefulset.yaml:128-132]()

When `persistence.enabled` is false, the `data` volume uses an `emptyDir` instead of a PVC [statefulset.yaml:140-143]().

Sources: [helm/trivy/templates/statefulset.yaml:18-31, 121-149](), [helm/trivy/values.yaml:15-19](), [helm/trivy/README.md:105-108]()

## Configuration Management

Trivy server configuration is managed through `ConfigMaps` for non-sensitive settings and `Secrets` for credentials.

### ConfigMap Structure

The ConfigMap [helm/trivy/templates/configmap.yaml:1-33]() provides environment variables to the Trivy server:

```mermaid
graph TB
    subgraph "Configuration Sources"
        ValuesYAML["values.yaml"]
    end
    
    subgraph "ConfigMap Environment Variables"
        Listen["TRIVY_LISTEN<br/>0.0.0.0:4954"]
        CacheDir["TRIVY_CACHE_DIR<br/>/home/scanner/.cache/trivy"]
        CacheBackend["TRIVY_CACHE_BACKEND<br/>(Redis URL if enabled)"]
        CacheTTL["TRIVY_CACHE_TTL"]
        Debug["TRIVY_DEBUG"]
        SkipDB["TRIVY_SKIP_DB_UPDATE"]
        DBRepo["TRIVY_DB_REPOSITORY<br/>ghcr.io/aquasecurity/trivy-db"]
        Proxy["HTTP_PROXY / HTTPS_PROXY / NO_PROXY"]
        SSLDir["SSL_CERT_DIR"]
        Extra["extraEnvVars<br/>(user-defined)"]
    end
    
    subgraph "Container"
        EnvFrom["envFrom: configMapRef"]
    end
    
    ValuesYAML --> Listen
    ValuesYAML --> CacheDir
    ValuesYAML --> CacheBackend
    ValuesYAML --> CacheTTL
    ValuesYAML --> Debug
    ValuesYAML --> SkipDB
    ValuesYAML --> DBRepo
    ValuesYAML --> Proxy
    ValuesYAML --> SSLDir
    ValuesYAML --> Extra
    
    Listen --> EnvFrom
    CacheDir --> EnvFrom
    CacheBackend --> EnvFrom
    CacheTTL --> EnvFrom
    Debug --> EnvFrom
    SkipDB --> EnvFrom
    DBRepo --> EnvFrom
    Proxy --> EnvFrom
    SSLDir --> EnvFrom
    Extra --> EnvFrom
```

**Configuration Flow**: Values from `values.yaml` are templated into the `ConfigMap`, which is injected into the container via `envFrom: configMapRef`.

Key configuration parameters:

| Environment Variable | Source | Purpose |
|---------------------|--------|---------|
| `TRIVY_LISTEN` | `service.port` | Server listen address [configmap.yaml:8]() |
| `TRIVY_CACHE_DIR` | Fixed | Cache directory path [configmap.yaml:9]() |
| `TRIVY_CACHE_BACKEND` | `trivy.cache.redis.url` | Redis cache URL [configmap.yaml:11]() |
| `TRIVY_DEBUG` | `trivy.debugMode` | Enable debug logging [configmap.yaml:15]() |
| `TRIVY_SKIP_DB_UPDATE` | `trivy.skipDBUpdate` | Skip automatic DB updates [configmap.yaml:16]() |
| `TRIVY_DB_REPOSITORY` | `trivy.dbRepository` | OCI repository for DB [configmap.yaml:17]() |

Sources: [helm/trivy/templates/configmap.yaml:1-33](), [helm/trivy/templates/statefulset.yaml:91-93]()

### Secret Management

The Secret [helm/trivy/templates/secret.yaml:1-17]() stores sensitive credentials:

| Secret Key | Source Value | Purpose |
|-----------|--------------|---------|
| `GITHUB_TOKEN` | `trivy.gitHubToken` | GitHub token for rate limit increase [secret.yaml:10]() |
| `TRIVY_TOKEN` | `trivy.serverToken` | Server authentication token [secret.yaml:11]() |
| `TRIVY_USERNAME` | `trivy.registryUsername` | Container registry username [secret.yaml:13]() |
| `TRIVY_PASSWORD` | `trivy.registryPassword` | Container registry password [secret.yaml:14]() |

Alternatively, users can reference an existing secret via `trivy.existingSecret` [values.yaml:128](), which overrides the chart-generated secret [statefulset.yaml:95-99]().

For registry credentials, a separate existing secret can be specified via `trivy.registryCredentialsExistingSecret` [values.yaml:96](), which injects `TRIVY_USERNAME` and `TRIVY_PASSWORD` as environment variables using `secretKeyRef` [statefulset.yaml:78-90]().

Sources: [helm/trivy/templates/secret.yaml:1-17](), [helm/trivy/templates/statefulset.yaml:78-99](), [helm/trivy/values.yaml:96, 128]()

## Service and Network Exposure

### Service Configuration

The `Service` resource [helm/trivy/templates/service.yaml:1-18]() exposes the Trivy server within the cluster:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `service.type` | `ClusterIP` | Service type [service.yaml:8]() |
| `service.port` | `4954` | Service port [service.yaml:15]() |
| `service.sessionAffinity` | `ClientIP` | Session affinity [service.yaml:17]() |
| `service.name` | `{{ include "trivy.fullname" . }}` | Service name [service.yaml:4]() |

The Service uses `ClientIP` session affinity to ensure clients connect to the same pod during a session, which can improve caching efficiency.

Sources: [helm/trivy/templates/service.yaml:1-18](), [helm/trivy/values.yaml:134-143]()

### Ingress Configuration

The optional `Ingress` resource [helm/trivy/templates/ingress.yaml:1-54]() provides external access to the Trivy server:

```yaml
# Example Ingress configuration in values.yaml
ingress:
  enabled: true
  ingressClassName: nginx
  hosts:
    - host: trivy.example.com
  path: "/"
  pathType: Prefix
  tls:
    - secretName: trivy-example-tls
      hosts:
        - trivy.example.com
```

The Ingress template includes version detection logic [ingress.yaml:3-9]() to support multiple Kubernetes API versions:
- `networking.k8s.io/v1` (Kubernetes 1.19+)
- `networking.k8s.io/v1beta1` (Kubernetes 1.14-1.21)
- `extensions/v1beta1` (legacy)

Sources: [helm/trivy/templates/ingress.yaml:1-54](), [helm/trivy/values.yaml:144-158]()

## RBAC and Security Configuration

The chart implements comprehensive security controls including RBAC, security contexts, and optional `PodSecurityPolicy`.

### RBAC Resources

When `rbac.create` is enabled [values.yaml:29-30](), the chart creates:

1. **ServiceAccount** [helm/trivy/templates/serviceaccount.yaml:1-11]()
   - Name: `{{ include "trivy.fullname" . }}`
   - Supports custom annotations via `trivy.serviceAccount.annotations` [values.yaml:120-121]()

2. **Role** [helm/trivy/templates/role.yaml:1-19]()
   - Grants permissions to use `PodSecurityPolicy` (if enabled)
   - API groups: `['policy']`
   - Resources: `['podsecuritypolicies']`
   - Verbs: `['use']` [role.yaml:11-15]()

3. **RoleBinding** [helm/trivy/templates/rolebinding.yaml]()
   - Binds the Role to the ServiceAccount.

The StatefulSet references the ServiceAccount with `automountServiceAccountToken: false` [statefulset.yaml:47]() to limit token exposure.

Sources: [helm/trivy/templates/serviceaccount.yaml:1-11](), [helm/trivy/templates/role.yaml:1-19](), [helm/trivy/templates/statefulset.yaml:47](), [helm/trivy/values.yaml:29-32]()

### Security Contexts

The chart enforces security best practices through two levels of security contexts:

#### Pod Security Context

Applied at the pod level [statefulset.yaml:48-51](), defaults from [values.yaml:34-37]():

| Parameter | Default | Security Benefit |
|-----------|---------|------------------|
| `runAsUser` | `65534` | Non-root execution |
| `runAsNonRoot` | `true` | Enforces non-root |
| `fsGroup` | `65534` | Volume permission management |

#### Container Security Context

Applied at the container level [statefulset.yaml:72-75](), defaults from [values.yaml:39-41]():

| Parameter | Default | Security Benefit |
|-----------|---------|------------------|
| `privileged` | `false` | Disables privileged mode |
| `readOnlyRootFilesystem` | `true` | Immutable root filesystem |

With `readOnlyRootFilesystem: true`, the chart mounts writable volumes only where necessary:
- `/tmp` as `emptyDir` for temporary files [statefulset.yaml:122-124]()
- `/home/scanner/.cache` for database storage [statefulset.yaml:125-127]()

Sources: [helm/trivy/templates/statefulset.yaml:48-51, 72-75, 122-127](), [helm/trivy/values.yaml:34-41]()

### PodSecurityPolicy

When `rbac.pspEnabled` is true [values.yaml:31](), the chart creates a `PodSecurityPolicy` [helm/trivy/templates/podsecuritypolicy.yaml:1-45]() with restrictive settings:

| Policy | Value | Description |
|--------|-------|-------------|
| `privileged` | `false` | Disallows privileged containers [podsecuritypolicy.yaml:14]() |
| `allowPrivilegeEscalation` | `false` | Prevents privilege escalation [podsecuritypolicy.yaml:15]() |
| `runAsUser.rule` | `MustRunAsNonRoot` | Enforces non-root [podsecuritypolicy.yaml:27]() |
| `readOnlyRootFilesystem` | `true` | Immutable root filesystem [podsecuritypolicy.yaml:40]() |
| `requiredDropCapabilities` | `ALL` | Drops all Linux capabilities [podsecuritypolicy.yaml:41-42]() |

Allowed volume types [podsecuritypolicy.yaml:16-22]():
- `configMap`, `emptyDir`, `persistentVolumeClaim`, `secret`, `projected`, `downwardAPI`

Sources: [helm/trivy/templates/podsecuritypolicy.yaml:1-45](), [helm/trivy/values.yaml:31-32]()

## Caching Configuration

The chart supports both filesystem-based and Redis-based caching for scan results.

### Filesystem Cache (Default)

By default, Trivy uses filesystem caching with the cache directory at `/home/scanner/.cache/trivy` [configmap.yaml:9](). This directory is backed by the persistent volume, ensuring cache persistence across pod restarts.

### Redis Cache Integration

Redis caching can be enabled for distributed caching across multiple Trivy instances [values.yaml:113-118]():

```mermaid
graph LR
    subgraph "Trivy Server Pods"
        Pod1["trivy-0"]
        Pod2["trivy-1"]
        PodN["trivy-N"]
    end
    
    subgraph "Shared Cache"
        Redis["Redis Server<br/>(external)"]
    end
    
    Pod1 --> Redis
    Pod2 --> Redis
    PodN --> Redis
```

**Redis Cache Architecture**: Multiple Trivy server instances share a common Redis cache, improving scan performance when multiple replicas are deployed.

Redis configuration parameters:

| Parameter | Description | Example Value |
|-----------|-------------|---------------|
| `trivy.cache.redis.enabled` | Enable Redis cache | `true` |
| `trivy.cache.redis.url` | Redis connection URL | `redis://redis.redis.svc:6379` |
| `trivy.cache.redis.ttl` | Cache time-to-live | `3600s` or `24h` |
| `trivy.cache.redis.tls` | Enable TLS for Redis | `false` |

When Redis is enabled, the ConfigMap sets:
- `TRIVY_CACHE_BACKEND`: Set to the Redis URL [configmap.yaml:11]()
- `TRIVY_CACHE_TTL`: Set to the configured TTL [configmap.yaml:12]()
- `TRIVY_REDIS_TLS`: TLS setting [configmap.yaml:13]()

**Note**: The Redis server must be deployed separately. The Helm chart documentation suggests using the [Bitnami Redis Helm chart](https://bitnami.com/stack/redis/helm) [README.md:111]().

Sources: [helm/trivy/templates/configmap.yaml:10-14](), [helm/trivy/values.yaml:113-118](), [helm/trivy/README.md:109-112]()

## Resource Management and Scaling

### Resource Limits and Requests

The chart specifies default CPU and memory constraints [values.yaml:21-27]():

| Resource Type | Default | Purpose |
|--------------|---------|---------|
| `requests.cpu` | `200m` | Minimum CPU allocation |
| `requests.memory` | `512Mi` | Minimum memory allocation |
| `limits.cpu` | `1` | Maximum CPU usage |
| `limits.memory` | `1Gi` | Maximum memory usage |

These resources are applied to the container [statefulset.yaml:133-136]():

```yaml
resources:
  requests:
    cpu: 200m
    memory: 512Mi
  limits:
    cpu: 1
    memory: 1Gi
```

Sources: [helm/trivy/values.yaml:21-27](), [helm/trivy/templates/statefulset.yaml:133-136]()

### Replica Count and Scaling

The StatefulSet supports horizontal scaling via `replicaCount` [values.yaml:13]():

```yaml
replicaCount: 1  # Can be increased for high availability
```

When scaling to multiple replicas:
1. Each pod gets its own `PersistentVolumeClaim` (via `volumeClaimTemplates`) [statefulset.yaml:19-31]().
2. All pods share the same database (downloaded independently or via Redis cache).
3. The Service distributes requests with `ClientIP` session affinity [service.yaml:17]().
4. Redis cache is recommended for multi-replica deployments to share scan cache.

The StatefulSet uses `podManagementPolicy: Parallel` [statefulset.yaml:11](), which allows all pods to start simultaneously rather than sequentially.

Sources: [helm/trivy/values.yaml:13](), [helm/trivy/templates/statefulset.yaml:11, 13, 19-31](), [helm/trivy/templates/service.yaml:17]()

### Pod Placement Configuration

The chart supports standard Kubernetes pod placement controls:

| Parameter | Values File | Purpose |
|-----------|------------|---------|
| `nodeSelector` | [values.yaml:45]() | Select nodes by labels |
| `affinity` | [values.yaml:49]() | Advanced placement rules |
| `tolerations` | [values.yaml:53]() | Tolerate node taints |

These are rendered in the StatefulSet [statefulset.yaml:56-67]() when configured.

Sources: [helm/trivy/values.yaml:45, 49, 53](), [helm/trivy/templates/statefulset.yaml:56-67]()

## Health Checks and Probes

The container includes liveness and readiness probes that query the `/healthz` endpoint:

### Liveness Probe

Configured in [statefulset.yaml:103-111]():

| Parameter | Value |
|-----------|-------|
| **Path** | `/healthz` |
| **Port** | `trivy-http` (4954) |
| **Initial Delay** | 5 seconds |
| **Period** | 10 seconds |
| **Success Threshold** | 1 |
| **Failure Threshold** | 10 |

### Readiness Probe

Configured in [statefulset.yaml:112-120]():

| Parameter | Value |
|-----------|-------|
| **Path** | `/healthz` |
| **Port** | `trivy-http` (4954) |
| **Initial Delay** | 5 seconds |
| **Period** | 10 seconds |
| **Success Threshold** | 1 |
| **Failure Threshold** | 3 |

Sources: [helm/trivy/templates/statefulset.yaml:103-120]()

## Installation and Configuration Examples

### Basic Installation

Install from the local chart directory [README.md:7-9]():

```bash
helm install trivy . --namespace trivy --create-namespace
```

### Installation from Aqua Chart Repository

Install from the published Helm repository [README.md:21-28]():

```bash
helm repo add aquasecurity https://aquasecurity.github.io/helm-charts/
helm repo update
helm search repo trivy
helm install my-trivy aquasecurity/trivy
```

### Database Update Configuration

By default, Trivy automatically downloads and updates the vulnerability database from `ghcr.io/aquasecurity/trivy-db` [values.yaml:104](). For CI/CD environments or to avoid GitHub rate limiting:

```yaml
trivy:
  # Skip automatic DB updates
  skipDBUpdate: true
  
  # Use alternative DB repository
  dbRepository: mirror.gcr.io/aquasec/trivy-db
  
  # Provide GitHub token for higher rate limits
  gitHubToken: "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

When `skipDBUpdate: true`, the database must be manually placed at `/home/scanner/.cache/trivy/db/trivy.db` [README.md:99-101]().

Sources: [helm/trivy/values.yaml:97-104](), [helm/trivy/README.md:98-101]()

## Chart Metadata and Versioning

The chart metadata is defined in [helm/trivy/Chart.yaml:1-12]():

| Field | Value | Description |
|-------|-------|-------------|
| `apiVersion` | `v2` | Helm 3 chart format |
| `name` | `trivy` | Chart name |
| `version` | `0.21.3` | Chart version |
| `appVersion` | `0.69.3` | Trivy application version |
| `description` | `Trivy helm chart` | Chart description |
| `sources` | `https://github.com/aquasecurity/trivy` | Source code location |

The `appVersion` field is used as the default image tag when `image.tag` is not specified [_helpers.tpl:53]().

Sources: [helm/trivy/Chart.yaml:1-12](), [helm/trivy/templates/_helpers.tpl:50-55]()

---

# Page: Development and Contributing

# Development and Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/DISCUSSION_TEMPLATE/adopters.yml](.github/DISCUSSION_TEMPLATE/adopters.yml)
- [.github/DISCUSSION_TEMPLATE/bugs.yml](.github/DISCUSSION_TEMPLATE/bugs.yml)
- [.github/DISCUSSION_TEMPLATE/documentation.yml](.github/DISCUSSION_TEMPLATE/documentation.yml)
- [.github/DISCUSSION_TEMPLATE/false-detection.yml](.github/DISCUSSION_TEMPLATE/false-detection.yml)
- [.github/DISCUSSION_TEMPLATE/ideas.yml](.github/DISCUSSION_TEMPLATE/ideas.yml)
- [.github/DISCUSSION_TEMPLATE/q-a.yml](.github/DISCUSSION_TEMPLATE/q-a.yml)
- [.github/ISSUE_TEMPLATE/config.yml](.github/ISSUE_TEMPLATE/config.yml)
- [.github/pull_request_template.md](.github/pull_request_template.md)
- [.github/workflows/auto-update-labels.yaml](.github/workflows/auto-update-labels.yaml)
- [.github/workflows/backport.yaml](.github/workflows/backport.yaml)
- [.github/workflows/cache-test-assets.yaml](.github/workflows/cache-test-assets.yaml)
- [.github/workflows/canary.yaml](.github/workflows/canary.yaml)
- [.github/workflows/mkdocs-dev.yaml](.github/workflows/mkdocs-dev.yaml)
- [.github/workflows/mkdocs-latest.yaml](.github/workflows/mkdocs-latest.yaml)
- [.github/workflows/publish-chart.yaml](.github/workflows/publish-chart.yaml)
- [.github/workflows/release.yaml](.github/workflows/release.yaml)
- [.github/workflows/reusable-release.yaml](.github/workflows/reusable-release.yaml)
- [.github/workflows/scan.yaml](.github/workflows/scan.yaml)
- [.github/workflows/spdx-cron.yaml](.github/workflows/spdx-cron.yaml)
- [.github/workflows/stale-issues.yaml](.github/workflows/stale-issues.yaml)
- [.github/workflows/test-docs.yaml](.github/workflows/test-docs.yaml)
- [.github/workflows/test.yaml](.github/workflows/test.yaml)
- [.github/workflows/triage.yaml](.github/workflows/triage.yaml)
- [.golangci.yaml](.golangci.yaml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [docs/community/contribute/discussion.md](docs/community/contribute/discussion.md)
- [docs/community/contribute/issue.md](docs/community/contribute/issue.md)
- [docs/community/maintainer/help-wanted.md](docs/community/maintainer/help-wanted.md)
- [docs/guide/configuration/filtering.md](docs/guide/configuration/filtering.md)
- [docs/guide/supply-chain/attestation/rekor.md](docs/guide/supply-chain/attestation/rekor.md)
- [docs/guide/target/container_image.md](docs/guide/target/container_image.md)
- [integration/k8s_test.go](integration/k8s_test.go)
- [integration/testdata/fixtures/k8s/summary-ids.json.golden](integration/testdata/fixtures/k8s/summary-ids.json.golden)
- [integration/testimages.ini](integration/testimages.ini)
- [internal/testutil/image.go](internal/testutil/image.go)
- [magefiles/fixture.go](magefiles/fixture.go)
- [magefiles/magefile.go](magefiles/magefile.go)
- [pkg/attestation/attestation_test.go](pkg/attestation/attestation_test.go)
- [pkg/fanal/artifact/sbom/testdata/sbom.cdx.intoto.jsonl](pkg/fanal/artifact/sbom/testdata/sbom.cdx.intoto.jsonl)
- [pkg/plugin/index.go](pkg/plugin/index.go)

</details>



This page provides an overview of the Trivy development process and guidelines for contributors. It covers the essential information needed to get started with Trivy development, including setup, workflow, and contribution guidelines.

For detailed information on specific topics, refer to the following pages:
- **[Build System and Mage Automation](#9.1)**: Details on the Mage build system, available targets, and local development setup.
- **[Testing Strategy and Infrastructure](#9.2)**: Comprehensive coverage of test types, fixtures, and testing practices.
- **[Release Process and Distribution](#9.3)**: Information on the release workflow, multi-platform builds, and distribution channels.

## Getting Started

### Prerequisites

Trivy development requires the following tools:

| Tool | Purpose | Version | Notes |
|------|---------|---------|-------|
| **Go** | Primary development language | 1.25+ | Required (defined in `go.mod` and CI) |
| **Mage** | Build automation via `magefile.go` | Latest | Installed via `go install tool` |
| **Docker** | Container image testing | v29.2.1+ | Required for integration tests |
| **Git** | Version control | Latest | Required |

Optional tools for specific development tasks:
- **golangci-lint**: Linting via `.golangci.yaml` configuration (v2.10.0) [magefiles/magefile.go:78-78]()
- **buf**: Protocol Buffer code generation for RPC layer [magefiles/magefile.go:120-123]()
- **kind**: Kubernetes cluster for `mage test:k8s` [magefiles/magefile.go:231-231]()
- **python**: Documentation with MkDocs Material theme [docs/build/requirements.txt]()
- **skopeo**: Downloading and inspecting test container images [integration/testimages.ini]()
- **npm**: Installing Sass for documentation styling [magefiles/magefile.go:61-66]()

The `go install tool` command installs all Go-based tools defined in the codebase, including Mage, buf, and golangci-lint. [magefiles/magefile.go:111-114]()

Sources: [.github/workflows/test.yaml:26-31](), [.github/workflows/test.yaml:84-88](), [magefiles/magefile.go:27-35](), [magefiles/magefile.go:78-87](), [magefiles/magefile.go:111-114]()

### Quick Setup

**Clone and Install Tools**

```bash
# Clone the repository
git clone https://github.com/aquasecurity/trivy.git
cd trivy

# Install development tools (requires Go)
go install tool  # Installs mage and other required tools
```

**Build Trivy**

```bash
# Build the binary (output: ./trivy)
mage build

# Install to $GOBIN
mage install
```

The build process uses `ldflags` to inject version information from `git describe` into the application binary. [magefiles/magefile.go:50-56]()

**Run Tests**

```bash
# Run unit tests
mage test:unit

# Run integration tests (requires Docker)
mage test:integration

# Run Kubernetes tests (creates kind cluster)
mage test:k8s
```

Sources: [magefiles/magefile.go:217-231](), [magefiles/magefile.go:377-407](), [.github/workflows/test.yaml:55-56]()

### Repository Structure

**Codebase Mapping: Core Systems**

```mermaid
graph TB
    subgraph "CLI & Entrypoint"
        Main["cmd/trivy/main.go"]
        Plugin["pkg/plugin/index.go"]
    end
    
    subgraph "Build & Automation"
        Mage["magefiles/magefile.go"]
        Fixture["magefiles/fixture.go"]
        Linter[".golangci.yaml"]
    end
    
    subgraph "Testing Infrastructure"
        Integ["integration/*_test.go"]
        K8sInteg["integration/k8s_test.go"]
        TestImages["integration/testimages.ini"]
        TestUtil["internal/testutil/image.go"]
    end
    
    subgraph "CI/CD Workflows"
        TestWF[".github/workflows/test.yaml"]
        RelWF[".github/workflows/release.yaml"]
        ReuseRel[".github/workflows/reusable-release.yaml"]
        Canary[".github/workflows/canary.yaml"]
    end

    Mage --> TestWF
    Fixture --> Integ
    TestImages --> Integ
    RelWF --> ReuseRel
```

Sources: [magefiles/magefile.go:1-25](), [.github/workflows/test.yaml:1-15](), [integration/k8s_test.go:1-20](), [integration/testimages.ini]()

## Development Workflow Overview

**Development Lifecycle: From Code to Release**

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Mage as Mage/Local
    participant CI as GitHub Actions (test.yaml)
    participant Rel as Release Pipeline (release.yaml)

    Dev->>Mage: mage build / mage test:unit
    Dev->>Mage: mage lint:run
    Dev->>CI: Push Pull Request
    CI->>CI: go mod tidy check
    CI->>CI: golangci-lint
    CI->>CI: mage test:integration
    CI->>CI: mage test:k8s
    Note over CI: All checks pass
    Dev->>Rel: Push Version Tag (v*)
    Rel->>Rel: GoReleaser (reusable-release.yaml)
    Rel->>Rel: Generate SBOM & Attestations
    Rel->>Rel: mage helm:updateVersion
```

### CI Job Matrix Strategy

The test workflow uses matrix builds to ensure cross-platform compatibility: [ .github/workflows/test.yaml:18-20 ]()

| Job | Platforms | Purpose |
|-----|-----------|---------|
| `test` | `ubuntu-latest`, `windows-latest`, `macos-latest` | Unit tests and linting. |
| `integration` | `ubuntu-latest` | System tests with Docker v29. [ .github/workflows/test.yaml:70-88 ]() |
| `k8s-integration` | `ubuntu-latest` | Kubernetes cluster scanning via KIND. [ .github/workflows/test.yaml:113-130 ]() |
| `module-test` | `ubuntu-latest` | WASM module integration tests. [ .github/workflows/test.yaml:131-164 ]() |
| `vm-test` | `ubuntu-latest` | Virtual Machine image scanning tests. [ .github/workflows/test.yaml:165-197 ]() |

Sources: [.github/workflows/test.yaml:15-197](), [.github/workflows/reusable-release.yaml:34-44]()

## Common Development Tasks

### Mage Task Reference

Trivy uses Mage for task automation. Key namespaces include:

| Namespace | Task | Description |
|-----------|------|-------------|
| `test` | `unit` | Runs unit tests with `-short` flag and coverage. [magefiles/magefile.go:217-220]() |
| `test` | `integration` | Runs integration tests with `integration` build tag. [magefiles/magefile.go:223-226]() |
| `test` | `k8s` | Creates a KIND cluster and runs K8s tests. [magefiles/magefile.go:229-272]() |
| `test` | `updateGolden` | Updates golden files for integration tests. [magefiles/magefile.go:186-188]() |
| `lint` | `run` | Runs `golangci-lint` and `modernize`. [magefiles/magefile.go:349-355]() |
| `docs` | `generate` | Regenerates CLI reference documentation. [magefiles/magefile.go:467-469]() |
| `protoc` | `generate` | Generates Go code from Protobuf files. [magefiles/magefile.go:119-124]() |

Sources: [magefiles/magefile.go:111-511]()

### Code Quality Standards

Trivy enforces strict linting via `golangci-lint` with a specific set of enabled linters including `gosec`, `revive`, `staticcheck`, and `modernize`. [.golangci.yaml:149-169]()

**Dependency Management Rules**
The project uses `depguard` and `gomodguard` to prevent the use of deprecated or non-standard packages:
- **Block `io/ioutil`**: Recommends `io` or `os` instead. [.golangci.yaml:17-18]()
- **Block `hashicorp/go-version`**: Recommends `aquasecurity/go-version`. [.golangci.yaml:55-58]()
- **Experimental Slices/Maps**: Recommends standard library `slices` and `maps`. [.golangci.yaml:12-16]()

Sources: [.golangci.yaml:1-230](), [magefiles/magefile.go:349-364]()

## Release and Distribution Overview

The release process is automated via GoReleaser and GitHub Actions.

1. **Canary Builds**: Triggered on every push to `main`, producing snapshot binaries and `canary` container images. [.github/workflows/canary.yaml:1-12](), [.github/workflows/reusable-release.yaml:125-137]()
2. **Official Releases**: Triggered by version tags (`v*`). [.github/workflows/release.yaml:1-5]()
3. **Artifacts**: Generates binaries, RPM/Deb packages, SBOMs (CycloneDX), and build provenance attestations. [.github/workflows/reusable-release.yaml:89-93](), [.github/workflows/reusable-release.yaml:138-143]()
4. **Downstream Updates**: Automatically triggers version updates in `trivy-telemetry`, `trivy-downloads`, `trivy-chocolatey`, and `trivy-action`. [.github/workflows/release.yaml:67-120]()

For details, see [Release Process and Distribution](#9.3).

Sources: [.github/workflows/release.yaml:1-120](), [.github/workflows/reusable-release.yaml:1-156](), [.github/workflows/canary.yaml:1-76]()

---

# Page: Build System and Mage Automation

# Build System and Mage Automation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [.golangci.yaml](.golangci.yaml)
- [LICENSE](LICENSE)
- [NOTICE](NOTICE)
- [integration/k8s_test.go](integration/k8s_test.go)
- [integration/testdata/fixtures/k8s/summary-ids.json.golden](integration/testdata/fixtures/k8s/summary-ids.json.golden)
- [integration/testimages.ini](integration/testimages.ini)
- [internal/testutil/image.go](internal/testutil/image.go)
- [magefiles/config_schema.go](magefiles/config_schema.go)
- [magefiles/docs.go](magefiles/docs.go)
- [magefiles/fixture.go](magefiles/fixture.go)
- [magefiles/magefile.go](magefiles/magefile.go)
- [misc/triage/labels.yaml](misc/triage/labels.yaml)
- [pkg/attestation/attestation_test.go](pkg/attestation/attestation_test.go)
- [pkg/fanal/artifact/sbom/testdata/sbom.cdx.intoto.jsonl](pkg/fanal/artifact/sbom/testdata/sbom.cdx.intoto.jsonl)
- [pkg/flag/global_flags.go](pkg/flag/global_flags.go)
- [pkg/plugin/index.go](pkg/plugin/index.go)
- [schema/trivy-config.json](schema/trivy-config.json)

</details>



This page documents the Mage-based build system used in Trivy. Mage is a make-like build tool that uses Go, allowing for type-safe and portable automation tasks for building, testing, and code generation.

## Overview

Trivy uses [Mage](https://magefile.org) to orchestrate complex development workflows. Unlike standard Makefiles, Magefiles are written in Go, which allows the build system to share logic and packages with the main codebase. The primary automation logic resides in the `magefiles/` directory [magefiles/magefile.go:1-25]().

### Environment Configuration
The build system enforces specific Go environment variables to ensure build reproducibility and to enable experimental features:
*   `CGO_ENABLED=0`: Ensures static binaries for maximum portability [magefiles/magefile.go:32]().
*   `GOEXPERIMENT=jsonv2`: Enables the next-generation JSON reflection-free serialization [magefiles/magefile.go:33]().

## Build Targets and Logic

The build system manages versioning by extracting information from Git tags using `git describe --tags --always` [magefiles/magefile.go:42](). This version is then injected into the binary via linker flags (`ldflags`) at `github.com/aquasecurity/trivy/pkg/version/app.ver` [magefiles/magefile.go:55]().

### Automation Namespaces
Mage tasks are organized into namespaces to categorize functionality:

| Namespace | Purpose | Key Functions |
|-----------|---------|---------------|
| `Tool` | Dependency management | `GolangciLint`, `Sass`, `Install` |
| `Protoc` | Protobuf orchestration | `Generate`, `Lint`, `Breaking` |
| `Test` | Test execution and fixtures | `Unit`, `Integration`, `K8s`, `UpdateGolden` |

Sources: [magefiles/magefile.go:58-59](), [magefiles/magefile.go:116](), [magefiles/magefile.go:156]()

## Code Generation and Tooling

Trivy relies on several code generation steps to handle API protocols, licensing expressions, and documentation.

### Protobuf and RPC
The `Protoc` namespace manages the generation of Go code for Trivy's client/server mode using `buf`.
*   **Generate**: Runs `buf generate` to create Twirp and Protobuf bindings [magefiles/magefile.go:123]().
*   **Breaking**: Validates that changes to `.proto` files do not introduce breaking changes against the `main` branch [magefiles/magefile.go:147]().

### Parser Generation
The `Yacc` task handles the generation of the licensing expression parser located in `./pkg/licensing/expression/...` [magefiles/magefile.go:151-154]().

### Documentation Generation
A specialized tool in `magefiles/docs.go` automates the creation of CLI references and configuration schemas.
*   **CLI Reference**: Uses `spf13/cobra/doc` to generate Markdown trees for all commands [magefiles/docs.go:42]().
*   **Config Schema**: Generates `schema/trivy-config.json` by introspecting all defined `FlagGroup` entities [magefiles/docs.go:51](), [magefiles/docs.go:166-198]().

Sources: [magefiles/magefile.go:116-154](), [magefiles/docs.go:29-54]()

## Testing and Fixture Automation

The build system manages the lifecycle of test data, including container images, VM images, and WebAssembly modules.

### Fixture Management
To ensure integration tests are fast and reproducible, Mage provides tasks to pre-download and package image fixtures:
*   **Container Images**: Downloads images defined in `testutil.ImageName` and saves them as `.tar.gz` in `integration/testdata/fixtures/images/` [magefiles/fixture.go:19-42]().
*   **VM Images**: Pulls OCI artifacts containing VM images and extracts layers based on the `org.opencontainers.image.title` annotation [magefiles/fixture.go:68-112]().

### WASM Module Compilation
Trivy supports WASM modules for extensibility. The build system compiles Go-based modules into WASM using the `wasip1` target [magefiles/magefile.go:205-208](). It uses `target.Path` to perform incremental builds, only recompiling if the source `.go` file is newer than the `.wasm` output [magefiles/magefile.go:200-204]().

### Test Execution Flow
The following diagram illustrates the dependency flow for running the full test suite:

```mermaid
graph TD
    subgraph "Setup Phase"
        T1["Tool:Install"] --> P1["Protoc:Generate"]
        T1 --> Y1["Yacc"]
    end

    subgraph "Fixture Phase"
        F1["Test:FixtureContainerImages"]
        F2["Test:FixtureVMImages"]
        F3["Test:GenerateModules"]
    end

    subgraph "Execution Phase"
        F3 --> Unit["Test:Unit"]
        RPM["rpm:Fixtures"] --> Unit
        Git["gittest:Fixtures"] --> Unit
        
        F1 --> Integration["Test:Integration"]
        
        T1 --> K8s["Test:K8s"]
    end

    Unit --> Coverage["coverage.txt"]
    K8s --> Kind["kind cluster"]
```

Sources: [magefiles/magefile.go:156-231](), [magefiles/fixture.go:1-131]()

## Kubernetes Integration Testing

The `Test:K8s` task automates the creation of a local Kubernetes environment for scanning tests.
1.  **Cluster Creation**: Uses `kind` (Kubernetes in Docker) to spin up a cluster using a specific node image (`kindest/node:v1.27.1`) [magefiles/magefile.go:231]().
2.  **Execution**: Runs tests with the `k8s_integration` build tag [integration/k8s_test.go:1]().
3.  **Cleanup**: Defer-calls `kind delete cluster` to ensure the environment is wiped after tests complete [magefiles/magefile.go:236]().

The `TestK8s` function validates both vulnerability/misconfiguration scanning and KBOM (Kubernetes BOM) generation in CycloneDX format [integration/k8s_test.go:27-149]().

Sources: [magefiles/magefile.go:229-238](), [integration/k8s_test.go:27-202]()

## Linting and Quality Control

Trivy uses `golangci-lint` with a highly customized configuration. The `Tool:GolangciLint` task ensures the correct version (`v2.10.0`) is installed in `GOBIN` [magefiles/magefile.go:77-87]().

### Linter Configuration
The `.golangci.yaml` file defines strict rules, including:
*   **Depguard**: Blocks deprecated packages like `io/ioutil` and enforces the use of internal wrappers like `github.com/aquasecurity/trivy/pkg/mapfs` [ .golangci.yaml:7-65]().
*   **Custom Rules**: Loads site-specific Rego or Go rules from `misc/lint/rules.go` [ .golangci.yaml:48]().
*   **Complexity**: Sets a `gocyclo` threshold of 20 to maintain maintainability [ .golangci.yaml:51]().

Sources: [magefiles/magefile.go:77-109](), [ .golangci.yaml:1-230]()

## Summary of Mage Commands

| Command | Implementation | Description |
|---------|----------------|-------------|
| `mage test:unit` | `(Test) Unit()` | Runs short unit tests with coverage and WASM generation [magefiles/magefile.go:217-220]() |
| `mage test:integration` | `(Test) Integration()` | Runs integration tests requiring container fixtures [magefiles/magefile.go:223-226]() |
| `mage test:k8s` | `(Test) K8s()` | Provisions a Kind cluster and runs K8s-specific tests [magefiles/magefile.go:229-238]() |
| `mage protoc:generate` | `(Protoc) Generate()` | Rebuilds Protobuf and Twirp Go code [magefiles/magefile.go:119-124]() |
| `mage test:updategolden` | `(Test) UpdateGolden()` | Updates integration test golden files [magefiles/magefile.go:186-188]() |

Sources: [magefiles/magefile.go:1-240]()

---

# Page: Testing Strategy and Infrastructure

# Testing Strategy and Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/auto-update-labels.yaml](.github/workflows/auto-update-labels.yaml)
- [.github/workflows/backport.yaml](.github/workflows/backport.yaml)
- [.github/workflows/cache-test-assets.yaml](.github/workflows/cache-test-assets.yaml)
- [.github/workflows/canary.yaml](.github/workflows/canary.yaml)
- [.github/workflows/mkdocs-dev.yaml](.github/workflows/mkdocs-dev.yaml)
- [.github/workflows/mkdocs-latest.yaml](.github/workflows/mkdocs-latest.yaml)
- [.github/workflows/publish-chart.yaml](.github/workflows/publish-chart.yaml)
- [.github/workflows/release.yaml](.github/workflows/release.yaml)
- [.github/workflows/reusable-release.yaml](.github/workflows/reusable-release.yaml)
- [.github/workflows/scan.yaml](.github/workflows/scan.yaml)
- [.github/workflows/spdx-cron.yaml](.github/workflows/spdx-cron.yaml)
- [.github/workflows/stale-issues.yaml](.github/workflows/stale-issues.yaml)
- [.github/workflows/test-docs.yaml](.github/workflows/test-docs.yaml)
- [.github/workflows/test.yaml](.github/workflows/test.yaml)
- [.github/workflows/triage.yaml](.github/workflows/triage.yaml)
- [.golangci.yaml](.golangci.yaml)
- [integration/client_server_test.go](integration/client_server_test.go)
- [integration/docker_engine_test.go](integration/docker_engine_test.go)
- [integration/integration_test.go](integration/integration_test.go)
- [integration/k8s_test.go](integration/k8s_test.go)
- [integration/registry_test.go](integration/registry_test.go)
- [integration/repo_test.go](integration/repo_test.go)
- [integration/sbom_test.go](integration/sbom_test.go)
- [integration/standalone_tar_test.go](integration/standalone_tar_test.go)
- [integration/testdata/fixtures/db/vulnerability.yaml](integration/testdata/fixtures/db/vulnerability.yaml)
- [integration/testdata/fixtures/k8s/summary-ids.json.golden](integration/testdata/fixtures/k8s/summary-ids.json.golden)
- [integration/testdata/fluentd-multiple-lockfiles.json.golden](integration/testdata/fluentd-multiple-lockfiles.json.golden)
- [integration/testimages.ini](integration/testimages.ini)
- [internal/testutil/docker.go](internal/testutil/docker.go)
- [internal/testutil/image.go](internal/testutil/image.go)
- [magefiles/fixture.go](magefiles/fixture.go)
- [magefiles/magefile.go](magefiles/magefile.go)
- [pkg/attestation/attestation_test.go](pkg/attestation/attestation_test.go)
- [pkg/fanal/artifact/sbom/testdata/sbom.cdx.intoto.jsonl](pkg/fanal/artifact/sbom/testdata/sbom.cdx.intoto.jsonl)
- [pkg/fanal/image/daemon/containerd.go](pkg/fanal/image/daemon/containerd.go)
- [pkg/fanal/image/daemon/context_test.go](pkg/fanal/image/daemon/context_test.go)
- [pkg/fanal/image/daemon/docker.go](pkg/fanal/image/daemon/docker.go)
- [pkg/fanal/image/daemon/image.go](pkg/fanal/image/daemon/image.go)
- [pkg/fanal/image/daemon/image_test.go](pkg/fanal/image/daemon/image_test.go)
- [pkg/fanal/image/daemon/podman.go](pkg/fanal/image/daemon/podman.go)
- [pkg/fanal/image/daemon/podman_test.go](pkg/fanal/image/daemon/podman_test.go)
- [pkg/fanal/image/image_test.go](pkg/fanal/image/image_test.go)
- [pkg/fanal/test/integration/containerd_test.go](pkg/fanal/test/integration/containerd_test.go)
- [pkg/fanal/test/integration/docker/docker.go](pkg/fanal/test/integration/docker/docker.go)
- [pkg/fanal/test/integration/library_test.go](pkg/fanal/test/integration/library_test.go)
- [pkg/fanal/test/integration/registry_test.go](pkg/fanal/test/integration/registry_test.go)
- [pkg/plugin/index.go](pkg/plugin/index.go)

</details>



This document describes Trivy's comprehensive testing infrastructure, including unit tests, integration tests, K8s tests, and fixture management. The testing system ensures reliability across multiple platforms and deployment scenarios, covering everything from basic functionality to complex integration scenarios with external services.

## Test Architecture Overview

Trivy employs a multi-layered testing strategy that validates functionality at different levels of the system:

```mermaid
graph TB
    subgraph "Test Types"
        UnitTests["mage test:unit"]
        IntegrationTests["mage test:integration"]
        K8sTests["mage test:k8s"]
        ModuleTests["mage test:module"]
        VMTests["mage test:vm"]
    end
    
    subgraph "Test Infrastructure"
        Mage["Magefiles"]
        TestContainers["testcontainers-go"]
        GoldenFiles["Golden File System"]
        Fixtures["Fixture Management"]
    end
    
    subgraph "CI/CD Pipeline"
        GitHubActions[".github/workflows/test.yaml"]
        MultiPlatform["OS Matrix (Ubuntu, Windows, macOS)"]
        Caching["actions/cache (Images/Fixtures)"]
    end
    
    UnitTests --> Mage
    IntegrationTests --> TestContainers
    IntegrationTests --> GoldenFiles
    Fixtures --> UnitTests
    Fixtures --> IntegrationTests
    
    GitHubActions --> UnitTests
    GitHubActions --> IntegrationTests
    GitHubActions --> K8sTests
    
    GitHubActions --> MultiPlatform
    GitHubActions --> Caching
```

**Test Framework Components**
- **Mage-based Orchestration**: The `magefiles/magefile.go` defines the primary entry points for all test types, ensuring consistent execution locally and in CI `[magefiles/magefile.go:156-250]()`.
- **Golden File System**: Used in integration tests to compare actual scan results against expected "golden" outputs `[magefiles/magefile.go:186-189]()`.
- **Fixture Management**: Automated downloading and extraction of container images, VM images, and WASM modules required for testing `[magefiles/magefile.go:158-183]()`.

Sources: `[magefiles/magefile.go]()`, `[.github/workflows/test.yaml]()`

## CI/CD Test Pipeline

The primary test pipeline runs on GitHub Actions and validates Trivy across multiple platforms.

### Workflow Structure
The `test.yaml` workflow is triggered on pull requests and merges, excluding documentation-only changes `[.github/workflows/test.yaml:1-12]()`. It utilizes a matrix strategy to run unit tests on `ubuntu-latest`, `windows-latest`, and `macos-latest` `[.github/workflows/test.yaml:17-20]()`.

### Specialized Integration Jobs
Beyond unit tests, the pipeline executes specialized integration suites:
- **Integration**: Standard integration tests including container and repository scanning `[.github/workflows/test.yaml:70-112]()`.
- **K8s Integration**: Validates Kubernetes cluster scanning using `kind` (Kubernetes in Docker) `[.github/workflows/test.yaml:113-130]()`.
- **Module Test**: Tests WASM-based modules `[.github/workflows/test.yaml:131-164]()`.
- **VM Test**: Validates VM image scanning `[.github/workflows/test.yaml:165-197]()`.

Sources: `[.github/workflows/test.yaml:1-200]()`

## Unit Tests

Unit tests provide fast feedback on individual components and are executed via `mage test:unit`.

**Key Characteristics**
- **Dependency Management**: Before running, Mage ensures that WASM modules, RPM fixtures, and Git test data are prepared `[magefiles/magefile.go:218]()`.
- **Coverage**: Uses `-coverprofile=coverage.txt` and `-covermode=atomic` for quality tracking `[magefiles/magefile.go:219]()`.
- **Short Mode**: Supports `-short` flag to skip long-running unit tests during rapid development `[magefiles/magefile.go:219]()`.

Sources: `[magefiles/magefile.go:217-220]()`

## Integration Tests

Integration tests validate Trivy's functionality in realistic scenarios. They are identified by the `//go:build integration` build tag `[integration/client_server_test.go:1]()`.

### Client-Server Testing
The `TestClientServer` function validates the RPC-based architecture `[integration/client_server_test.go:46]()`. It uses `csArgs` to define test parameters:

| Field | Description |
| :--- | :--- |
| `RemoteAddrOption` | Specifies the server address (e.g., `--server`) `[integration/client_server_test.go:26]()` |
| `ClientToken` | Tests authentication between client and server `[integration/client_server_test.go:33]()` |
| `Input` | Path to the target artifact (e.g., image tarball) `[integration/client_server_test.go:32]()` |

### Docker Engine and Registry Testing
Integration tests interact with live Docker engines and registries. Due to runner environment variations, the CI explicitly installs Docker Engine `v29.2.1` to ensure consistent Image IDs and behavior `[.github/workflows/test.yaml:84-89]()`.

```mermaid
sequenceDiagram
    participant Mage as mage test:integration
    participant Docker as Docker Engine (v29)
    participant Registry as Test Registry (testcontainers)
    participant Trivy as Trivy CLI
    
    Mage->>Docker: Load Fixture Images
    Mage->>Registry: Start Secure Registry
    Mage->>Trivy: Run Scan Command
    Trivy->>Registry: Pull Layers
    Trivy->>Trivy: Analyze & Compare Golden
```

Sources: `[integration/client_server_test.go:24-41]()`, `[.github/workflows/test.yaml:79-89]()`

## Kubernetes Integration Tests

The Kubernetes test suite validates Trivy's ability to scan cluster resources and RBAC.

**Infrastructure Setup**
- **Cluster Creation**: Mage uses `kind` to create a local cluster named `kind-test` `[magefiles/magefile.go:231]()`.
- **Image Versioning**: Specifically uses `kindest/node:v1.27.1` to ensure predictable API responses `[magefiles/magefile.go:231]()`.
- **Cleanup**: Implements a `defer` block to delete the cluster regardless of test outcome `[magefiles/magefile.go:235-237]()`.

Sources: `[magefiles/magefile.go:229-245]()`, `[.github/workflows/test.yaml:113-130]()`

## Fixture and Asset Management

Trivy uses a sophisticated system to manage test data and prevent CI slowdowns.

### Image Fixtures
Test images are defined in `integration/testimages.ini`. In CI, a digest of this file is generated to use as a cache key `[.github/workflows/test.yaml:96-103]()`. If the digest matches, images are restored from `actions/cache` rather than being re-downloaded `[.github/workflows/test.yaml:104-109]()`.

### WASM Modules
Unit and integration tests for modules require compiled WASM binaries. Mage automates this via `compileWasmModules`, which looks for `.go` files in `testdata` and compiles them using `GOOS=wasip1` and `GOARCH=wasm` `[magefiles/magefile.go:190-214]()`.

### Golden Files
Golden files store the expected JSON/Table output of scans. When underlying logic changes, developers run `mage test:updateGolden` to refresh these files across the `integration/` and `pkg/fanal/test/integration/` directories `[magefiles/magefile.go:186-189]()`.

Sources: `[magefiles/magefile.go:158-214]()`, `[.github/workflows/test.yaml:96-109]()`

## Linting and Documentation Checks

Testing includes code quality and documentation consistency:
- **Golangci-lint**: Configured in `.golangci.yaml`, it enforces style, security (gosec), and complexity (gocyclo) rules `[.golangci.yaml:1-230]()`.
- **CLI Reference Check**: Mage task `docs:generate` is run in CI to ensure that the auto-generated CLI documentation matches the current code state `[.github/workflows/test.yaml:58-65]()`.

Sources: `[.golangci.yaml]()`, `[.github/workflows/test.yaml:38-65]()`

---

# Page: Release Process and Distribution

# Release Process and Distribution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [.github/workflows/auto-close-issue.yaml](.github/workflows/auto-close-issue.yaml)
- [.github/workflows/auto-ready-for-review.yaml](.github/workflows/auto-ready-for-review.yaml)
- [.github/workflows/auto-update-labels.yaml](.github/workflows/auto-update-labels.yaml)
- [.github/workflows/backport.yaml](.github/workflows/backport.yaml)
- [.github/workflows/cache-test-assets.yaml](.github/workflows/cache-test-assets.yaml)
- [.github/workflows/canary.yaml](.github/workflows/canary.yaml)
- [.github/workflows/mkdocs-dev.yaml](.github/workflows/mkdocs-dev.yaml)
- [.github/workflows/mkdocs-latest.yaml](.github/workflows/mkdocs-latest.yaml)
- [.github/workflows/publish-chart.yaml](.github/workflows/publish-chart.yaml)
- [.github/workflows/release-please.yaml](.github/workflows/release-please.yaml)
- [.github/workflows/release.yaml](.github/workflows/release.yaml)
- [.github/workflows/reusable-release.yaml](.github/workflows/reusable-release.yaml)
- [.github/workflows/scan.yaml](.github/workflows/scan.yaml)
- [.github/workflows/spdx-cron.yaml](.github/workflows/spdx-cron.yaml)
- [.github/workflows/stale-issues.yaml](.github/workflows/stale-issues.yaml)
- [.github/workflows/test-docs.yaml](.github/workflows/test-docs.yaml)
- [.github/workflows/test.yaml](.github/workflows/test.yaml)
- [.github/workflows/triage.yaml](.github/workflows/triage.yaml)
- [Dockerfile](Dockerfile)
- [Dockerfile.canary](Dockerfile.canary)
- [ci/deploy-deb.sh](ci/deploy-deb.sh)
- [ci/deploy-rpm.sh](ci/deploy-rpm.sh)
- [contrib/Trivy.gitlab-ci.yml](contrib/Trivy.gitlab-ci.yml)
- [docs/community/maintainer/release-flow.md](docs/community/maintainer/release-flow.md)
- [docs/community/maintainer/triage.md](docs/community/maintainer/triage.md)
- [goreleaser-canary.yml](goreleaser-canary.yml)
- [goreleaser.yml](goreleaser.yml)

</details>



This document details Trivy's release process and distribution system, covering how releases are triggered, built with GoReleaser, signed with Cosign, and distributed across multiple platforms and package repositories. The process handles multi-architecture binary builds, native package generation (DEB/RPM), container image publishing, and automated downstream updates.

## Release Process Overview

Trivy's release process is triggered by pushing a Git tag matching the pattern `v*` (e.g., `v0.58.0`) [[.github/workflows/release.yaml:2-5]](). The workflow uses a reusable release definition to orchestrate GoReleaser, CycloneDX SBOM generation, and multi-registry container pushes [[.github/workflows/release.yaml:8-21]]().

### Release Workflow Architecture

```mermaid
graph TD
    subgraph "Triggers"
        TagPush["git push v*"]
        CanaryPush["push to main"]
    end
    
    subgraph "Orchestration"
        ReleaseWork["release.yaml"]
        ReusableRelease["reusable-release.yaml"]
        CanaryWork["canary.yaml"]
    end
    
    subgraph "Build Engine"
        GoReleaser["GoReleaser v2.1.0"]
        MageHelm["mage helm:updateVersion"]
    end
    
    subgraph "Artifacts & Distribution"
        Binaries["GitHub Release Assets"]
        Containers["DockerHub / GHCR / ECR"]
        NativePkgs["DEB / RPM (trivy-repo)"]
        HelmPR["Helm Chart PR"]
        Downstream["trivy-action / trivy-chocolatey"]
    end

    TagPush --> ReleaseWork
    CanaryPush --> CanaryWork
    ReleaseWork --> ReusableRelease
    CanaryWork --> ReusableRelease
    
    ReusableRelease --> GoReleaser
    GoReleaser --> Binaries
    GoReleaser --> Containers
    
    ReleaseWork --> MageHelm
    MageHelm --> HelmPR
    
    ReleaseWork --> Downstream
```

**Sources:** [[.github/workflows/release.yaml:1-120]](), [[.github/workflows/reusable-release.yaml:1-156]](), [[.github/workflows/canary.yaml:1-28]]()

## GoReleaser Configuration

Trivy utilizes GoReleaser v2 to manage the build matrix and artifact generation [[goreleaser.yml:1]]().

### Build Matrix and Targets

The configuration defines four primary build IDs to handle different OS/Architecture constraints, specifically addressing limitations in the `modernc.org/sqlite` driver [[goreleaser.yml:39-41,73]]().

| Build ID | OS | Arch | Flags/Env |
| :--- | :--- | :--- | :--- |
| `build-linux` | linux | 386, arm, amd64, arm64, s390x, ppc64le | `CGO_ENABLED=0`, `GOEXPERIMENT=jsonv2` |
| `build-bsd` | freebsd | amd64 | `CGO_ENABLED=0` |
| `build-macos` | darwin | amd64, arm64 | `CGO_ENABLED=0` |
| `build-windows` | windows | amd64 | `CGO_ENABLED=0` |

All builds inject the version string into `github.com/aquasecurity/trivy/pkg/version/app.ver` using linker flags [[goreleaser.yml:11,32,49,66]]().

**Sources:** [[goreleaser.yml:4-76]]()

## Package Generation and Signing

### Native Packages (NFPM)
GoReleaser uses NFPM to generate `.deb` and `.rpm` packages [[goreleaser.yml:83-87]](). 
- **Templates:** Contrib templates are installed to `/usr/local/share/trivy/templates` [[goreleaser.yml:108-109]]().
- **RPM Signing:** Packages are signed using GPG keys provided via the `GPG_FILE` environment variable [[goreleaser.yml:111-112]]().

### Artifact Attestation and Provenance
The release pipeline integrates GitHub's artifact attestation to provide build provenance [[.github/workflows/reusable-release.yaml:138-143]]().
- **Cosign:** The `sigstore/cosign-installer` is used to set up signing capabilities [[.github/workflows/reusable-release.yaml:45-46]]().
- **Checksums:** Attestations are linked to the `checksums.txt` generated by GoReleaser [[.github/workflows/reusable-release.yaml:142]]().

**Sources:** [[goreleaser.yml:83-112]](), [[.github/workflows/reusable-release.yaml:138-143]]()

## Multi-Platform Distribution

### Container Registries
Trivy images are published to three major registries using Docker Buildx for multi-architecture support [[goreleaser.yml:160,185,210]]():
1. **Docker Hub:** `docker.io/aquasec/trivy` [[goreleaser.yml:154]]()
2. **GitHub Container Registry:** `ghcr.io/aquasecurity/trivy` [[goreleaser.yml:156]]()
3. **AWS ECR Public:** `public.ecr.aws/aquasecurity/trivy` [[goreleaser.yml:158]]()

### Homebrew
GoReleaser automatically updates the Homebrew formula in the `aquasecurity/homebrew-trivy` repository [[goreleaser.yml:141-145]](). It uses a custom `url_template` that points to `get.trivy.dev` [[goreleaser.yml:148]]().

### Native Repositories
After the main release job, the `deploy-packages` job triggers a workflow in the `trivy-repo` repository to update the APT and YUM repositories with the new version [[.github/workflows/release.yaml:23-35]]().

**Sources:** [[goreleaser.yml:141-210]](), [[.github/workflows/release.yaml:23-35]]()

## Post-Release Automation

Once a release is finalized, Trivy triggers several downstream automation tasks:

1.  **Helm Chart Update:** The `update-chart-version` job runs `mage helm:updateVersion`, which creates a PR in the Trivy repository to bump the chart's `appVersion` [[.github/workflows/release.yaml:38-64]]().
2.  **Downstream Triggers:** The `trigger-version-update` job dispatches workflows to update Trivy versions in:
    -   `trivy-telemetry` [[.github/workflows/release.yaml:71-81]]()
    -   `trivy-downloads` [[.github/workflows/release.yaml:83-95]]()
    -   `trivy-chocolatey` [[.github/workflows/release.yaml:96-106]]()
    -   `trivy-action` [[.github/workflows/release.yaml:108-120]]()

**Sources:** [[.github/workflows/release.yaml:38-120]]()

## Canary Builds

For every push to the `main` branch involving Go files or the Dockerfile, a "Canary" build is triggered [[.github/workflows/canary.yaml:1-11]]().

- **Configuration:** Uses `goreleaser-canary.yml` with the `--snapshot` flag to prevent a formal GitHub release [[.github/workflows/canary.yaml:18-19]]().
- **Docker Strategy:** Since GoReleaser Free does not push snapshot images, a custom `Dockerfile.canary` and `docker/build-push-action` are used to push images tagged as `:canary` [[.github/workflows/reusable-release.yaml:125-136]]().
- **Artifact Access:** Binaries are cached using a unique key based on `github.sha` and then uploaded as GitHub Action artifacts for manual testing [[.github/workflows/canary.yaml:36-70]]().

**Sources:** [[.github/workflows/canary.yaml:1-76]](), [[.github/workflows/reusable-release.yaml:122-137]](), [[Dockerfile.canary:1-12]]()

---

# Page: Glossary

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [cmd/trivy/main.go](cmd/trivy/main.go)
- [go.mod](go.mod)
- [go.sum](go.sum)
- [integration/testdata/conda-cyclonedx.json.golden](integration/testdata/conda-cyclonedx.json.golden)
- [integration/testdata/conda-environment-cyclonedx.json.golden](integration/testdata/conda-environment-cyclonedx.json.golden)
- [integration/testdata/fixtures/sbom/fluentd-multiple-lockfiles-cyclonedx.json](integration/testdata/fixtures/sbom/fluentd-multiple-lockfiles-cyclonedx.json)
- [integration/testdata/fixtures/sbom/minikube-kbom.json](integration/testdata/fixtures/sbom/minikube-kbom.json)
- [integration/testdata/fluentd-multiple-lockfiles-short.cdx.json.golden](integration/testdata/fluentd-multiple-lockfiles-short.cdx.json.golden)
- [integration/testdata/fluentd-multiple-lockfiles.cdx.json.golden](integration/testdata/fluentd-multiple-lockfiles.cdx.json.golden)
- [integration/testdata/npm-cyclonedx.json.golden](integration/testdata/npm-cyclonedx.json.golden)
- [integration/testdata/pom-cyclonedx.json.golden](integration/testdata/pom-cyclonedx.json.golden)
- [internal/dbtest/db.go](internal/dbtest/db.go)
- [mkdocs.yml](mkdocs.yml)
- [pkg/cache/remote.go](pkg/cache/remote.go)
- [pkg/cache/remote_test.go](pkg/cache/remote_test.go)
- [pkg/commands/app.go](pkg/commands/app.go)
- [pkg/commands/app_test.go](pkg/commands/app_test.go)
- [pkg/commands/artifact/run.go](pkg/commands/artifact/run.go)
- [pkg/commands/testdata/java-db/metadata.json](pkg/commands/testdata/java-db/metadata.json)
- [pkg/commands/testdata/policy/metadata.json](pkg/commands/testdata/policy/metadata.json)
- [pkg/compliance/report/report_test.go](pkg/compliance/report/report_test.go)
- [pkg/compliance/spec/compliance.go](pkg/compliance/spec/compliance.go)
- [pkg/compliance/spec/compliance_test.go](pkg/compliance/spec/compliance_test.go)
- [pkg/compliance/spec/custom.go](pkg/compliance/spec/custom.go)
- [pkg/compliance/spec/mapper.go](pkg/compliance/spec/mapper.go)
- [pkg/compliance/spec/mapper_test.go](pkg/compliance/spec/mapper_test.go)
- [pkg/compliance/spec/testdata/testcache/policy/content/specs/compliance/invalid.yaml](pkg/compliance/spec/testdata/testcache/policy/content/specs/compliance/invalid.yaml)
- [pkg/compliance/spec/testdata/testcache/policy/content/specs/compliance/testspec.yaml](pkg/compliance/spec/testdata/testcache/policy/content/specs/compliance/testspec.yaml)
- [pkg/compliance/spec/testdata/testcache/policy/metadata.json](pkg/compliance/spec/testdata/testcache/policy/metadata.json)
- [pkg/db/db.go](pkg/db/db.go)
- [pkg/db/db_test.go](pkg/db/db_test.go)
- [pkg/dependency/parser/java/pom/var.go](pkg/dependency/parser/java/pom/var.go)
- [pkg/detector/library/driver.go](pkg/detector/library/driver.go)
- [pkg/detector/library/driver_test.go](pkg/detector/library/driver_test.go)
- [pkg/detector/library/testdata/fixtures/data-source.yaml](pkg/detector/library/testdata/fixtures/data-source.yaml)
- [pkg/detector/library/testdata/fixtures/go.yaml](pkg/detector/library/testdata/fixtures/go.yaml)
- [pkg/fanal/analyzer/all/import.go](pkg/fanal/analyzer/all/import.go)
- [pkg/fanal/analyzer/const.go](pkg/fanal/analyzer/const.go)
- [pkg/fanal/analyzer/imgconf/apk/apk.go](pkg/fanal/analyzer/imgconf/apk/apk.go)
- [pkg/fanal/analyzer/imgconf/secret/secret.go](pkg/fanal/analyzer/imgconf/secret/secret.go)
- [pkg/fanal/analyzer/imgconf/secret/secret_test.go](pkg/fanal/analyzer/imgconf/secret/secret_test.go)
- [pkg/fanal/analyzer/language/analyze.go](pkg/fanal/analyzer/language/analyze.go)
- [pkg/fanal/analyzer/licensing/license.go](pkg/fanal/analyzer/licensing/license.go)
- [pkg/fanal/analyzer/pkg/dpkg/copyright.go](pkg/fanal/analyzer/pkg/dpkg/copyright.go)
- [pkg/fanal/analyzer/secret/secret.go](pkg/fanal/analyzer/secret/secret.go)
- [pkg/fanal/analyzer/secret/secret_test.go](pkg/fanal/analyzer/secret/secret_test.go)
- [pkg/fanal/applier/docker.go](pkg/fanal/applier/docker.go)
- [pkg/fanal/applier/docker_test.go](pkg/fanal/applier/docker_test.go)
- [pkg/fanal/artifact/sbom/sbom.go](pkg/fanal/artifact/sbom/sbom.go)
- [pkg/fanal/secret/builtin-rules.go](pkg/fanal/secret/builtin-rules.go)
- [pkg/fanal/secret/scanner.go](pkg/fanal/secret/scanner.go)
- [pkg/fanal/secret/scanner_test.go](pkg/fanal/secret/scanner_test.go)
- [pkg/fanal/secret/testdata/alibaba-access-key-id.txt](pkg/fanal/secret/testdata/alibaba-access-key-id.txt)
- [pkg/fanal/secret/testdata/asymmetric-private-key.txt](pkg/fanal/secret/testdata/asymmetric-private-key.txt)
- [pkg/fanal/secret/testdata/aws-secrets.txt](pkg/fanal/secret/testdata/aws-secrets.txt)
- [pkg/fanal/secret/testdata/crlf-line-endings.txt](pkg/fanal/secret/testdata/crlf-line-endings.txt)
- [pkg/fanal/secret/testdata/github-token.txt](pkg/fanal/secret/testdata/github-token.txt)
- [pkg/fanal/secret/testdata/grafana-env.txt](pkg/fanal/secret/testdata/grafana-env.txt)
- [pkg/fanal/secret/testdata/hugging-face-secret.txt](pkg/fanal/secret/testdata/hugging-face-secret.txt)
- [pkg/fanal/secret/testdata/invalid-utf8.txt](pkg/fanal/secret/testdata/invalid-utf8.txt)
- [pkg/fanal/secret/testdata/jwt-secret.txt](pkg/fanal/secret/testdata/jwt-secret.txt)
- [pkg/fanal/secret/testdata/private-packagist.txt](pkg/fanal/secret/testdata/private-packagist.txt)
- [pkg/fanal/secret/testdata/symfony-secret.yaml](pkg/fanal/secret/testdata/symfony-secret.yaml)
- [pkg/fanal/types/const.go](pkg/fanal/types/const.go)
- [pkg/flag/options.go](pkg/flag/options.go)
- [pkg/iac/rego/build.go](pkg/iac/rego/build.go)
- [pkg/iac/rego/custom.go](pkg/iac/rego/custom.go)
- [pkg/iac/rego/embed.go](pkg/iac/rego/embed.go)
- [pkg/iac/rego/embed_test.go](pkg/iac/rego/embed_test.go)
- [pkg/iac/rego/load.go](pkg/iac/rego/load.go)
- [pkg/iac/rego/load_test.go](pkg/iac/rego/load_test.go)
- [pkg/iac/rego/metadata.go](pkg/iac/rego/metadata.go)
- [pkg/iac/rego/metadata_test.go](pkg/iac/rego/metadata_test.go)
- [pkg/iac/rego/options.go](pkg/iac/rego/options.go)
- [pkg/iac/rego/result.go](pkg/iac/rego/result.go)
- [pkg/iac/rego/runtime.go](pkg/iac/rego/runtime.go)
- [pkg/iac/rego/scanner.go](pkg/iac/rego/scanner.go)
- [pkg/iac/rego/scanner_test.go](pkg/iac/rego/scanner_test.go)
- [pkg/iac/rego/store.go](pkg/iac/rego/store.go)
- [pkg/iac/rego/store_test.go](pkg/iac/rego/store_test.go)
- [pkg/iac/scan/rule.go](pkg/iac/scan/rule.go)
- [pkg/iac/scanners/cloudformation/scanner_test.go](pkg/iac/scanners/cloudformation/scanner_test.go)
- [pkg/iac/scanners/dockerfile/scanner_test.go](pkg/iac/scanners/dockerfile/scanner_test.go)
- [pkg/iac/scanners/generic/scanner_test.go](pkg/iac/scanners/generic/scanner_test.go)
- [pkg/iac/scanners/terraform/scanner_test.go](pkg/iac/scanners/terraform/scanner_test.go)
- [pkg/iac/scanners/terraform/setup_test.go](pkg/iac/scanners/terraform/setup_test.go)
- [pkg/iac/scanners/terraformplan/snapshot/scanner_test.go](pkg/iac/scanners/terraformplan/snapshot/scanner_test.go)
- [pkg/k8s/scanner/scanner_test.go](pkg/k8s/scanner/scanner_test.go)
- [pkg/licensing/classifier.go](pkg/licensing/classifier.go)
- [pkg/licensing/classifier_test.go](pkg/licensing/classifier_test.go)
- [pkg/licensing/expression/expression.go](pkg/licensing/expression/expression.go)
- [pkg/licensing/expression/expression_test.go](pkg/licensing/expression/expression_test.go)
- [pkg/licensing/expression/types.go](pkg/licensing/expression/types.go)
- [pkg/licensing/normalize.go](pkg/licensing/normalize.go)
- [pkg/licensing/normalize_test.go](pkg/licensing/normalize_test.go)
- [pkg/licensing/scanner.go](pkg/licensing/scanner.go)
- [pkg/licensing/scanner_test.go](pkg/licensing/scanner_test.go)
- [pkg/log/logger.go](pkg/log/logger.go)
- [pkg/misconf/scanner.go](pkg/misconf/scanner.go)
- [pkg/purl/purl.go](pkg/purl/purl.go)
- [pkg/purl/purl_test.go](pkg/purl/purl_test.go)
- [pkg/result/testdata/openvex.json](pkg/result/testdata/openvex.json)
- [pkg/rpc/client/client.go](pkg/rpc/client/client.go)
- [pkg/rpc/client/client_test.go](pkg/rpc/client/client_test.go)
- [pkg/rpc/convert.go](pkg/rpc/convert.go)
- [pkg/rpc/convert_test.go](pkg/rpc/convert_test.go)
- [pkg/rpc/server/server.go](pkg/rpc/server/server.go)
- [pkg/rpc/server/server_test.go](pkg/rpc/server/server_test.go)
- [pkg/sbom/core/bom.go](pkg/sbom/core/bom.go)
- [pkg/sbom/cyclonedx/marshal.go](pkg/sbom/cyclonedx/marshal.go)
- [pkg/sbom/cyclonedx/marshal_test.go](pkg/sbom/cyclonedx/marshal_test.go)
- [pkg/sbom/cyclonedx/testdata/happy/bom.json](pkg/sbom/cyclonedx/testdata/happy/bom.json)
- [pkg/sbom/cyclonedx/testdata/happy/infinite-loop-bom.json](pkg/sbom/cyclonedx/testdata/happy/infinite-loop-bom.json)
- [pkg/sbom/cyclonedx/testdata/happy/kbom.json](pkg/sbom/cyclonedx/testdata/happy/kbom.json)
- [pkg/sbom/cyclonedx/testdata/happy/third-party-bom-no-os.json](pkg/sbom/cyclonedx/testdata/happy/third-party-bom-no-os.json)
- [pkg/sbom/cyclonedx/testdata/happy/third-party-bom.json](pkg/sbom/cyclonedx/testdata/happy/third-party-bom.json)
- [pkg/sbom/cyclonedx/unmarshal.go](pkg/sbom/cyclonedx/unmarshal.go)
- [pkg/sbom/cyclonedx/unmarshal_test.go](pkg/sbom/cyclonedx/unmarshal_test.go)
- [pkg/sbom/io/encode.go](pkg/sbom/io/encode.go)
- [pkg/sbom/io/encode_test.go](pkg/sbom/io/encode_test.go)
- [pkg/sbom/sbom.go](pkg/sbom/sbom.go)
- [pkg/sbom/sbom_test.go](pkg/sbom/sbom_test.go)
- [pkg/vex/csaf.go](pkg/vex/csaf.go)
- [pkg/vex/cyclonedx.go](pkg/vex/cyclonedx.go)
- [pkg/vex/openvex.go](pkg/vex/openvex.go)
- [pkg/vex/testdata/openvex-multiple.json](pkg/vex/testdata/openvex-multiple.json)
- [pkg/vex/testdata/openvex-oci.json](pkg/vex/testdata/openvex-oci.json)
- [pkg/vex/testdata/openvex.json](pkg/vex/testdata/openvex.json)
- [pkg/vex/testdata/unknown.json](pkg/vex/testdata/unknown.json)
- [pkg/vex/vex.go](pkg/vex/vex.go)
- [pkg/vex/vex_test.go](pkg/vex/vex_test.go)
- [pkg/x/slices/slices.go](pkg/x/slices/slices.go)
- [rpc/cache/service.pb.go](rpc/cache/service.pb.go)
- [rpc/cache/service.proto](rpc/cache/service.proto)
- [rpc/cache/service.twirp.go](rpc/cache/service.twirp.go)
- [rpc/common/service.pb.go](rpc/common/service.pb.go)
- [rpc/common/service.proto](rpc/common/service.proto)
- [rpc/scanner/service.pb.go](rpc/scanner/service.pb.go)
- [rpc/scanner/service.proto](rpc/scanner/service.proto)
- [rpc/scanner/service.twirp.go](rpc/scanner/service.twirp.go)

</details>



This glossary defines codebase-specific terms, jargon, and domain concepts used within the Trivy project. It is intended to help onboarding engineers navigate the architectural layers and data models.

## Core System Terms

### Artifact
A target that Trivy can scan for security issues. Artifacts are abstracted to allow uniform scanning of different sources.
*   **Implementation**: Defined as `TargetKind` in [pkg/commands/artifact/run.go:47-57](). Supported types include `image`, `fs` (filesystem), `repo`, `sbom`, `vm`, and `k8s`.
*   **Data Flow**: The `Runner` interface handles the lifecycle of an artifact scan [pkg/commands/artifact/run.go:79-98]().

### Analyzer
A component responsible for extracting specific information (packages, secrets, or configurations) from an artifact's files.
*   **Types**: Analyzers are categorized into groups like `TypeLockfiles`, `TypeIndividualPkgs`, and `TypeConfig` [pkg/fanal/analyzer/const.go]().
*   **Control**: Analyzers can be disabled via CLI flags to optimize performance or narrow scope [pkg/commands/artifact/run.go:201-202]().

### Driver
A specialized component used in vulnerability detection to map extracted package information to known vulnerabilities for a specific ecosystem (e.g., Alpine, Debian, or Python).
*   **Location**: Logic resides in [pkg/detector/library/driver.go]().

### Secret Rule
A definition used by the secret scanner to identify sensitive information (like API keys) using regular expressions and keyword filtering.
*   **Implementation**: Defined as a `Rule` struct. Built-in rules cover services like AWS, GitHub, and Slack [pkg/fanal/secret/builtin-rules.go:102-160]().
*   **Categories**: Rules are grouped by `SecretRuleCategory` [pkg/fanal/secret/builtin-rules.go:12-74]().

---

## Data Structures & Identifiers

### PURL (Package URL)
A standard for identifying software packages across different ecosystems (Maven, npm, PyPI, etc.). Trivy uses PURLs to ensure interoperability with SBOM formats.
*   **Implementation**: Handled in [pkg/purl/purl.go]().
*   **Usage**: Embedded in package identifiers during scanning and reporting [pkg/sbom/cyclonedx/marshal_test.go:28-43]().

### BOM-Ref
A unique identifier used within an SBOM (Software Bill of Materials) to link components and their relationships.
*   **Implementation**: Generated during the encoding process [pkg/sbom/io/encode.go]() and used in CycloneDX marshaling [pkg/sbom/cyclonedx/marshal.go:126-138]().

### Blob
In Trivy's cache and Fanal (the analyzer library) context, a blob represents the processed result of a single layer or a filesystem partition.

---

## Infrastructure & Database

### Trivy DB
The primary vulnerability database. It is a Key-Value store (BoltDB) containing aggregated vulnerability data from various sources.
*   **Schema**: Managed via `SchemaVersion` [pkg/db/db.go:25]().
*   **Distribution**: Distributed as an OCI artifact [pkg/db/db.go:26-36]().
*   **Update Logic**: The `Client` checks if the local DB is stale based on `DownloadedAt` and `NextUpdate` metadata [pkg/db/db.go:105-161]().

### Java DB
A specialized database used for identifying Java dependencies by mapping JAR SHA-1 hashes to Maven coordinates.
*   **Pointer**: [pkg/javadb/]() (referenced in [pkg/commands/artifact/run.go:30]()).

---

## Architectural Diagrams

### From CLI Command to Code Entities
This diagram illustrates how a user command like `trivy image` traverses the internal command structure and initializes the scanning runner.

```mermaid
graph TD
    User["User: 'trivy image ...'"] -- "Calls" --> RootCmd["RootCommand (pkg/commands/app.go)"]
    RootCmd -- "PersistentPreRunE" --> BindFlags["flag.GlobalFlagGroup.Bind()"]
    BindFlags -- "Initializes" --> Viper["viper (Config Management)"]
    RootCmd -- "Subcommand" --> ImageCmd["NewImageCommand (pkg/commands/app.go)"]
    ImageCmd -- "Invokes" --> Runner["NewRunner (pkg/commands/artifact/run.go)"]
    Runner -- "Initializes" --> DBClient["db.NewClient (pkg/db/db.go)"]
    Runner -- "Loads" --> WASM["module.NewManager (pkg/module)"]
    Runner -- "Dispatches" --> ScanImage["runner.ScanImage()"]
```
**Sources**: [pkg/commands/app.go:68-117](), [pkg/commands/artifact/run.go:121-174](), [pkg/db/db.go:84-102]()

### SBOM Generation Data Flow
This diagram shows how a raw `types.Report` is transformed into a standardized CycloneDX SBOM.

```mermaid
graph LR
    subgraph "Natural Language Space"
        ScanResult["Vulnerability Report"]
        Standard["CycloneDX Standard"]
    end

    subgraph "Code Entity Space"
        Report["types.Report (pkg/types/report.go)"]
        Encoder["sbomio.NewEncoder (pkg/sbom/io/encode.go)"]
        BOM["core.BOM (Intermediate Representation)"]
        Marshaler["cyclonedx.Marshaler (pkg/sbom/cyclonedx/marshal.go)"]
        Output["cdx.BOM (External Library Type)"]

        Report --> Encoder
        Encoder --> BOM
        BOM --> Marshaler
        Marshaler --> Output
    end
```
**Sources**: [pkg/sbom/cyclonedx/marshal.go:58-90](), [pkg/sbom/io/encode.go]()

---

## Technical Jargon Table

| Term | Definition | Code Pointer |
| :--- | :--- | :--- |
| **Fanal** | The core library used by Trivy for artifact analysis and metadata extraction. | `pkg/fanal/` |
| **Misconf** | Shorthand for "Misconfiguration". Refers to the subsystem scanning IaC files (Terraform, Dockerfile). | [pkg/misconf/scanner.go]() |
| **VEX** | Vulnerability Exploitability eXchange. A format to provide status updates on vulnerabilities (e.g., "not affected"). | [pkg/vex/vex.go]() |
| **Rootfs** | A directory representing the root filesystem of an OS, scanned without container-specific metadata. | [pkg/commands/artifact/run.go:52]() |
| **Twirp** | The RPC framework used for communication between Trivy Client and Trivy Server. | [rpc/cache/service.twirp.go]() |

**Sources**: [pkg/commands/artifact/run.go:47-57](), [pkg/vex/vex.go](), [rpc/cache/service.twirp.go]()