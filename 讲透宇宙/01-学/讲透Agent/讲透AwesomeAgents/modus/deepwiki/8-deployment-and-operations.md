<!-- source: DeepWiki mcp.deepwiki.com · repo hypermodeinc/modus · page 8 Deployment and Operations · fetched 2026-10-26 -->

# Deployment and Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci-go-test.yml](.github/workflows/ci-go-test.yml)
- [.github/workflows/ci-runtime-build.yml](.github/workflows/ci-runtime-build.yml)
- [.github/workflows/ci-runtime-integration-tests.yml](.github/workflows/ci-runtime-integration-tests.yml)
- [.github/workflows/ci-sdk-go-build.yml](.github/workflows/ci-sdk-go-build.yml)
- [.github/workflows/codeql.yml](.github/workflows/codeql.yml)
- [.github/workflows/release-runtime.yaml](.github/workflows/release-runtime.yaml)
- [.github/workflows/release-sdk-go.yaml](.github/workflows/release-sdk-go.yaml)
- [.gitignore](.gitignore)
- [Dockerfile](Dockerfile)
- [runtime/.goreleaser.yaml](runtime/.goreleaser.yaml)
- [runtime/Makefile](runtime/Makefile)
- [runtime/integration_tests/testdata/postgresql-example.wasm](runtime/integration_tests/testdata/postgresql-example.wasm)

</details>



This document covers production deployment strategies, operational monitoring, and release management for Modus applications and runtime infrastructure. It focuses on containerized deployments, CI/CD automation, and production operational considerations.

For development environment setup and local debugging workflows, see [Development Environment](#7.1). For Docker-specific deployment configurations, see [Docker Deployment](#8.1). For CI/CD pipeline integration details, see [CI/CD Integration](#8.2).

## Production Deployment Architecture

Modus applications can be deployed using multiple strategies depending on operational requirements. The runtime supports both containerized and binary deployment models with comprehensive health monitoring and operational tooling.

```mermaid
graph TD
    subgraph "Deployment Artifacts"
        SourceCode["Source Code<br/>modus.json + WASM modules"]
        RuntimeBinary["modus_runtime<br/>Multi-platform Binary"]
        DockerImage["modus_runtime:latest<br/>Container Image"]
    end
    
    subgraph "Deployment Targets"
        Kubernetes["Kubernetes Cluster<br/>Pod Orchestration"]
        DockerHost["Docker Host<br/>Container Runtime"]
        BareMetalHost["Bare Metal<br/>Direct Binary Execution"]
        CloudRun["Cloud Run<br/>Serverless Containers"]
    end
    
    subgraph "Operational Monitoring"
        HealthEndpoint["/health<br/>Health Check API"]
        MetricsEndpoint["/metrics<br/>Prometheus Metrics"]
        JSONLogs["--jsonlogs<br/>Structured Logging"]
        ExplorerUI["/explorer<br/>API Explorer UI"]
    end
    
    SourceCode --> RuntimeBinary
    SourceCode --> DockerImage
    
    RuntimeBinary --> BareMetalHost
    DockerImage --> Kubernetes
    DockerImage --> DockerHost
    DockerImage --> CloudRun
    
    Kubernetes --> HealthEndpoint
    DockerHost --> MetricsEndpoint
    BareMetalHost --> JSONLogs
    CloudRun --> ExplorerUI
    
    style SourceCode fill:#f9f9f9
    style RuntimeBinary fill:#f9f9f9
    style DockerImage fill:#f9f9f9
```

Sources: [Dockerfile:1-75](), [runtime/.goreleaser.yaml:13-34](), [runtime/Makefile:89-91]()

## Container Build Pipeline

The Modus runtime uses a multi-stage Docker build process that optimizes for both development tooling and production deployment efficiency.

```mermaid
graph LR
    subgraph "Build Stage 1: Node Builder"
        NodeBase["node:alpine"]
        ExplorerSrc["runtime/explorer/content<br/>package.json + TypeScript"]
        NPMInstall["npm ci<br/>npm run build"]
    end
    
    subgraph "Build Stage 2: Go Builder"
        GoBase["golang:alpine"]
        RuntimeSrc["runtime/*.go<br/>go.mod + go.sum"]
        LibDeps["lib/<br/>Shared Libraries"]
        GoWorkspace["go.work<br/>Workspace Config"]
        GoBuild["go build -o modus_runtime<br/>-ldflags version injection"]
    end
    
    subgraph "Final Runtime Image"
        UbuntuBase["ubuntu:24.04"]
        ModusUser["modus:1234<br/>Non-root User"]
        SystemTools["curl + iputils-ping<br/>jq + less"]
        RuntimeBinary["modus_runtime<br/>Executable Binary"]
        Entrypoint["ENTRYPOINT modus_runtime --jsonlogs<br/>HEALTHCHECK /health"]
    end
    
    NodeBase --> ExplorerSrc
    ExplorerSrc --> NPMInstall
    
    GoBase --> RuntimeSrc
    RuntimeSrc --> LibDeps
    LibDeps --> GoWorkspace
    GoWorkspace --> GoBuild
    NPMInstall --> GoBuild
    
    GoBuild --> UbuntuBase
    UbuntuBase --> ModusUser
    ModusUser --> SystemTools
    SystemTools --> RuntimeBinary
    RuntimeBinary --> Entrypoint
```

Sources: [Dockerfile:1-75](), [runtime/Makefile:22-28]()

## CI/CD Release Pipeline

The automated release system supports multiple artifact types with comprehensive testing and multi-platform distribution.

### Runtime Release Process

```mermaid
graph TD
    subgraph "Trigger Events"
        RuntimeTag["runtime/v*<br/>Git Tag Push"]
        PREvent["Pull Request<br/>Integration Testing"]
    end
    
    subgraph "Build Matrix"
        LinuxBuild["Linux Build<br/>amd64 + arm64"]
        MacOSBuild["macOS Build<br/>amd64 + arm64"] 
        WindowsBuild["Windows Build<br/>amd64 + arm64"]
        DockerBuild["Docker Build<br/>Multi-arch Images"]
    end
    
    subgraph "Testing Pipeline"
        UnitTests["go test -race<br/>All Go Modules"]
        IntegrationTests["PostgreSQL Integration<br/>WASM Module Tests"]
        SDKTests["Go SDK Examples<br/>TinyGo Compilation"]
        ExplorerBuild["npm run build<br/>API Explorer UI"]
    end
    
    subgraph "Release Artifacts"
        GoReleaser["goreleaser-pro<br/>Binary Archives"]
        GitHubRelease["GitHub Releases<br/>Assets + Checksums"]
        DockerRegistry["Container Registry<br/>Tagged Images"]
        EventDispatch["Repository Dispatch<br/>hyp-cluster Trigger"]
    end
    
    RuntimeTag --> LinuxBuild
    RuntimeTag --> MacOSBuild
    RuntimeTag --> WindowsBuild
    RuntimeTag --> DockerBuild
    
    PREvent --> UnitTests
    PREvent --> IntegrationTests
    PREvent --> SDKTests
    PREvent --> ExplorerBuild
    
    LinuxBuild --> GoReleaser
    MacOSBuild --> GoReleaser
    WindowsBuild --> GoReleaser
    GoReleaser --> GitHubRelease
    DockerBuild --> DockerRegistry
    GitHubRelease --> EventDispatch
```

Sources: [.github/workflows/release-runtime.yaml:1-61](), [.github/workflows/ci-runtime-integration-tests.yml:1-42](), [.github/workflows/ci-go-test.yml:1-66]()

### SDK Release Process

The SDK release pipeline supports independent versioning and package distribution for different language targets.

| SDK Type | Version Pattern | Artifacts | Distribution |  
|----------|----------------|-----------|--------------|
| Go SDK | `sdk/go/v*` | `sdk.json`, `templates_go_*.tar.gz` | GitHub Releases |
| AssemblyScript SDK | `sdk/as/v*` | NPM packages | NPM Registry |

Sources: [.github/workflows/release-sdk-go.yaml:1-47]()

## Operational Monitoring

### Health Check System

The runtime provides comprehensive health monitoring through standardized endpoints and structured logging.

```mermaid
graph LR
    subgraph "Health Monitoring"
        HealthEndpoint["/health<br/>HTTP Health Check"]
        HealthStatus["status: ok<br/>JSON Response"]
        DockerHealthCheck["HEALTHCHECK --interval=30s<br/>curl + jq validation"]
    end
    
    subgraph "Metrics Collection"
        MetricsEndpoint["/metrics<br/>Prometheus Format"]
        RuntimeMetrics["Runtime Statistics<br/>WASM Execution Metrics"]
        SystemMetrics["System Resources<br/>Memory + CPU Usage"]
    end
    
    subgraph "Logging Configuration"
        JSONLogs["--jsonlogs<br/>Structured Output"]
        LogLevel["MODUS_ENV=dev<br/>Development Logging"]
        LogFormat["Timestamp + Level<br/>Message + Context"]
    end
    
    HealthEndpoint --> HealthStatus
    HealthStatus --> DockerHealthCheck
    
    MetricsEndpoint --> RuntimeMetrics
    MetricsEndpoint --> SystemMetrics
    
    JSONLogs --> LogLevel
    LogLevel --> LogFormat
```

Sources: [Dockerfile:74-74](), [runtime/Makefile:33-33]()

### Production Configuration

Production deployments require specific configuration for security, performance, and operational requirements.

#### Container Security

- **Non-root execution**: Runtime runs as `modus:1234` user account
- **Minimal base image**: Ubuntu 24.04 with essential tools only
- **Resource isolation**: Container-based process isolation
- **Network security**: Configurable port binding (default `:8686`)

#### Resource Requirements

| Component | Memory | CPU | Storage |
|-----------|--------|-----|---------|
| Runtime Base | 64MB | 0.1 vCPU | 100MB |
| WASM Modules | Variable | Variable | Variable |
| Explorer UI | 32MB | 0.05 vCPU | 50MB |
| Database Connections | 16MB each | Minimal | Minimal |

Sources: [Dockerfile:42-75]()

## Build System Integration

### Makefile Targets

The runtime includes comprehensive build automation through standardized make targets.

```mermaid
graph TD
    subgraph "Development Targets"
        ModusTidy["make tidy<br/>go mod tidy + formatting"]
        ModusBuild["make build<br/>Explorer + Runtime Binary"]
        ModusRun["make run<br/>Development Server"]
        ModusRunApp["make runapp<br/>Application Runner"]
    end
    
    subgraph "Testing Targets"
        ModusTest["make test<br/>Unit Tests + Testdata"]
        ModusTestRace["make test-race<br/>Race Condition Detection"]
        ModusTestIntegration["make test-integration<br/>Database Integration"]
        ModusTestCI["make test-ci<br/>JUnit Report Generation"]
    end
    
    subgraph "Build Dependencies"
        ExplorerBuild["make build-explorer<br/>npm ci + npm run build"]
        TestdataBuild["make build-testdata<br/>AssemblyScript + Go Examples"]
        IntegrationTestdata["make build-integration-testdata<br/>PostgreSQL Example WASM"]
    end
    
    subgraph "Production Targets"
        DockerBuild["make docker-build<br/>Container Image Creation"]
        Clean["make clean<br/>Artifact Cleanup"]
    end
    
    ModusBuild --> ExplorerBuild
    ModusTest --> TestdataBuild
    ModusTestIntegration --> IntegrationTestdata
    ModusTestCI --> TestdataBuild
    DockerBuild --> ExplorerBuild
```

Sources: [runtime/Makefile:1-96]()

### Cross-Platform Build Configuration

The runtime supports native compilation across multiple operating systems and architectures through GoReleaser configuration.

#### Supported Platforms

| OS | Architecture | Binary Format | Archive Format |
|----|-----------|--------------|--------------| 
| Linux | amd64, arm64 | ELF | tar.gz |
| macOS | amd64, arm64 | Mach-O | tar.gz |
| Windows | amd64, arm64 | PE (.exe) | zip |

#### Build Optimization

- **CGO disabled**: Pure Go compilation for portability
- **Link-time optimization**: `-s -w` flags for size reduction  
- **Version injection**: Build-time version embedding
- **Windows compatibility**: `-checklinkname=0` flag for Windows builds

Sources: [runtime/.goreleaser.yaml:13-34](), [runtime/Makefile:9-12]()

---

