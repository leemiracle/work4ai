<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/hf-csi-driver · page 5 Build and Release · fetched 2026-10-26 -->

# Build and Release

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [Dockerfile](Dockerfile)
- [LICENSE](LICENSE)
- [Makefile](Makefile)

</details>



This page describes the build system, continuous integration, and release processes for the `hf-csi-driver`. The project utilizes a multi-stage `Dockerfile` for containerization, a `Makefile` for local development tasks, and GitHub Actions to automate testing and OCI artifact distribution.

## Build System Overview

The build process is centered around producing a statically linked Go binary for the CSI driver and packaging it into a minimal runtime environment.

### Dockerfile
The project uses a multi-stage `Dockerfile` [[Dockerfile:1-14]()] to ensure small image sizes and a clean build environment:
1.  **Builder Stage**: Uses `golang:1.25-bookworm` to compile the `hf-csi-driver` binary from `cmd/hf-csi-driver/` [[Dockerfile:2-8]()]. It sets `CGO_ENABLED=0` for portability [[Dockerfile:8-8]()].
2.  **Runtime Stage**: Uses `debian:bookworm-slim` [[Dockerfile:11-11]()]. It installs the `mount` utility, which is required by the driver for performing FUSE mounts via `mount-utils` [[Dockerfile:12-12]()].

### Makefile
The `Makefile` provides a standard interface for local development and CI steps:
*   **`build`**: Compiles the binary locally with version information injected via `LDFLAGS` [[Makefile:9-10]()].
*   **`docker-build`**: Builds the container image using the local `Dockerfile` [[Makefile:15-16]()].
*   **`test`**: Runs Go unit tests across the `pkg/` directory [[Makefile:12-13]()].
*   **`e2e`**: Triggers the full end-to-end test suite, including cluster setup via `kind` [[Makefile:31-43]()].

**Build and Release Flow**
```mermaid
graph TD
    subgraph "Source"
        Code["Go Source Code"]
        Helm["Helm Chart Templates"]
    end

    subgraph "Build Phase"
        DF["Dockerfile Multi-stage"]
        MF["Makefile Targets"]
        Code --> DF
        Code --> MF
    end

    subgraph "Artifacts"
        Bin["hf-csi-driver Binary"]
        Img["Container Image (ghcr.io)"]
        Chart["Helm Chart (OCI)"]
        DF --> Img
        MF --> Bin
    end

    Img --> Chart
    Sources: [Dockerfile:1-14](), [Makefile:1-22](), [.github/workflows/release.yml:11-13]()
```

Sources: [Dockerfile:1-14](), [Makefile:1-43]()

## CI Pipeline

The Continuous Integration (CI) workflow is triggered on every pull request and push to the `main` branch [[.github/workflows/ci.yml:3-6]()]. It ensures code quality through linting and validates functionality via comprehensive E2E tests in a `kind` cluster.

Key components of the CI pipeline include:
*   **Linting & Unit Tests**: Execution of `golangci-lint` and `go test -race` [[.github/workflows/ci.yml:9-32]()].
*   **Dependency Building**: Since the driver depends on `hf-mount-fuse`, the CI clones and builds the `hf-mount` image dynamically to test against the latest changes [[.github/workflows/ci.yml:55-79]()].
*   **E2E Suites**: Separate jobs for `podmount` and `sidecar` modes. These jobs install `kind`, load the freshly built images, and execute a series of shell-based test scripts [[.github/workflows/ci.yml:80-213]()].

For details, see [CI Pipeline](#5.1).

Sources: [.github/workflows/ci.yml:1-214]()

## Release Workflow

The release process is automated via a dedicated GitHub Actions workflow [[.github/workflows/release.yml:1-5]()]. It handles versioning, image distribution, and Helm chart publishing.

The workflow follows these high-level steps:
1.  **Semantic Versioning**: Uses `huggingface/semver-release-action` to determine the next version and create a GitHub release [[.github/workflows/release.yml:16-31]()].
2.  **Image Publishing**: Builds the production Docker image and pushes it to `ghcr.io/huggingface/hf-csi-driver` with both the version tag and `latest` [[.github/workflows/release.yml:32-54]()].
3.  **Helm Chart OCI Publishing**: 
    *   Fetches the latest release tag of the `hf-mount` dependency [[.github/workflows/release.yml:66-72]()].
    *   Uses `yq` and `sed` to update `Chart.yaml` and `values.yaml` with the correct image tags [[.github/workflows/release.yml:74-83]()].
    *   Packages the chart and pushes it to the OCI registry at `oci://ghcr.io/huggingface/charts` [[.github/workflows/release.yml:90-93]()].

For details, see [Release Workflow](#5.2).

**CI/CD Code Entity Mapping**
```mermaid
graph LR
    subgraph "GitHub Actions"
        CI[".github/workflows/ci.yml"]
        REL[".github/workflows/release.yml"]
    end

    subgraph "Build Tools"
        MK["Makefile"]
        DK["Dockerfile"]
    end

    subgraph "External Deps"
        HFM["huggingface/hf-mount"]
    end

    CI --> MK
    CI --> HFM
    REL --> DK
    REL --> HFM
    REL -->|"yq/sed"| Chart["deploy/helm/hf-csi-driver/Chart.yaml"]

    Sources: [.github/workflows/ci.yml:55-72](), [.github/workflows/release.yml:66-83](), [Makefile:1-10]()
```

Sources: [.github/workflows/release.yml:1-94]()

---

