<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/vgpu-device-manager · page 4 Build System & Development · fetched 2026-10-26 -->

# Build System & Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [.golangci.yml](.golangci.yml)
- [Makefile](Makefile)
- [docker/Dockerfile.devel](docker/Dockerfile.devel)

</details>



This document covers the build system, development environment setup, and development workflows for the NVIDIA vGPU Device Manager project. It explains the Make-based build system, Go compilation process, code quality tools, and development container setup.

For information about container image builds and deployment, see [Container Images](#4.1). For CI/CD pipeline details, see [CI/CD Pipelines](#5).

## Overview

The NVIDIA vGPU Device Manager uses a comprehensive build system built around Go's native tooling, Make, and Docker. The system supports cross-compilation, code quality enforcement, testing, and development environment containerization.

### Build System Architecture

```mermaid
graph TB
    subgraph "Build Entry Points"
        MAKEFILE["Makefile"]
        VERSIONS["versions.mk"]
        GITIGNORE[".gitignore"]
    end
    
    subgraph "Go Build Process"
        MODULE["MODULE := github.com/NVIDIA/vgpu-device-manager"]
        CMD_TARGETS["CMD_TARGETS"]
        VERSION_PKG["VERSION_PKG := internal/info"]
        GOOS["GOOS := linux"]
    end
    
    subgraph "Code Quality"
        GOLANGCI_YML[".golangci.yml"]
        LINTERS["contextcheck, gocritic, gosec, misspell, unconvert"]
        FORMATTERS["gofmt, goimports"]
    end
    
    subgraph "Development Environment"
        DOCKERFILE_DEVEL["docker/Dockerfile.devel"]
        BUILDIMAGE["BUILDIMAGE := vgpu-device-manager-build"]
        GO_TOOLS["golint, moq, ineffassign, misspell"]
    end
    
    subgraph "Build Outputs"
        BINARIES["Binary Executables"]
        COVERAGE_FILE["coverage.out"]
        DOCKER_TARGETS["docker-* targets"]
    end
    
    MAKEFILE --> MODULE
    MAKEFILE --> CMD_TARGETS
    MAKEFILE --> VERSION_PKG
    MAKEFILE --> GOOS
    
    GOLANGCI_YML --> LINTERS
    GOLANGCI_YML --> FORMATTERS
    
    DOCKERFILE_DEVEL --> BUILDIMAGE
    DOCKERFILE_DEVEL --> GO_TOOLS
    
    MODULE --> BINARIES
    CMD_TARGETS --> BINARIES
    BUILDIMAGE --> DOCKER_TARGETS
    LINTERS --> COVERAGE_FILE
```

**Sources:** [Makefile:1-106](), [.golangci.yml:1-43](), [docker/Dockerfile.devel:1-21]()

## Go Build Configuration

The project is configured as a Go module with specific build settings for cross-compilation and version injection.

### Module and Build Settings

| Setting | Value | Purpose |
|---------|-------|---------|
| `MODULE` | `github.com/NVIDIA/vgpu-device-manager` | Go module identifier |
| `GOOS` | `linux` | Target operating system |
| `VERSION_PKG` | `internal/info` | Package for version injection |
| `BUILDIMAGE_TAG` | `golang$(GOLANG_VERSION)` | Development container tag |

**Sources:** [Makefile:15](), [Makefile:35](), [Makefile:36]()

### Command Build Process

```mermaid
graph LR
    subgraph "Command Discovery"
        WILDCARD["wildcard ./cmd/*/"]
        CMDS["CMDS := patsubst"]
        CMD_TARGETS["CMD_TARGETS := cmd-%"]
    end
    
    subgraph "Build Execution"
        GO_BUILD["go build"]
        LDFLAGS["-ldflags with version injection"]
        COMMAND_BUILD_OPTIONS["PREFIX support"]
    end
    
    subgraph "Version Injection"
        GIT_COMMIT["gitCommit=$(GIT_COMMIT)"]
        VERSION["version=$(VERSION)"]
        VERSION_PKG_REF["$(VERSION_PKG).gitCommit"]
    end
    
    subgraph "Output Binaries"
        NVIDIA_VGPU_DM["nvidia-vgpu-dm"]
        NVIDIA_K8S_VGPU_DM["nvidia-k8s-vgpu-dm"]
    end
    
    WILDCARD --> CMDS
    CMDS --> CMD_TARGETS
    CMD_TARGETS --> GO_BUILD
    
    GO_BUILD --> LDFLAGS
    LDFLAGS --> GIT_COMMIT
    LDFLAGS --> VERSION
    LDFLAGS --> VERSION_PKG_REF
    
    GO_BUILD --> NVIDIA_VGPU_DM
    GO_BUILD --> NVIDIA_K8S_VGPU_DM
```

**Sources:** [Makefile:24-25](), [Makefile:42-44]()

## Code Quality and Linting

The project enforces code quality through golangci-lint with specific linter configurations and formatting rules.

### Linter Configuration

The `.golangci.yml` file configures multiple linters with specific exclusions:

| Linter | Purpose |
|--------|---------|
| `contextcheck` | Context usage validation |
| `gocritic` | Go code criticism |
| `gosec` | Security vulnerability detection |
| `misspell` | Spelling error detection |
| `unconvert` | Unnecessary type conversions |

**Exclusions:**
- Test files (`.*_test.go`) for specific gosec rules
- Third-party code (`third_party$`, `builtin$`, `examples$`)
- Generated code with lax enforcement

**Sources:** [.golangci.yml:3-8](), [.golangci.yml:17-24](), [.golangci.yml:26-28]()

### Formatting Configuration

```mermaid
graph TB
    subgraph "Formatter Settings"
        GOFMT["gofmt"]
        GOIMPORTS["goimports"]
        LOCAL_PREFIXES["local-prefixes: github.com/NVIDIA/vgpu-device-manager"]
    end
    
    subgraph "Make Targets"
        FMT_TARGET["fmt target"]
        ASSERT_FMT["assert-fmt target"]
        LINT_TARGET["lint target"]
    end
    
    subgraph "Execution"
        GO_LIST["go list -f '{{.Dir}}'"]
        XARGS_GOFMT["xargs gofmt -s -l -w"]
        GOLANGCI_LINT["golangci-lint run ./..."]
    end
    
    GOFMT --> FMT_TARGET
    GOIMPORTS --> FMT_TARGET
    LOCAL_PREFIXES --> GOIMPORTS
    
    FMT_TARGET --> GO_LIST
    ASSERT_FMT --> GO_LIST
    LINT_TARGET --> GOLANGCI_LINT
    
    GO_LIST --> XARGS_GOFMT
```

**Sources:** [.golangci.yml:29-36](), [Makefile:49-52](), [Makefile:66-68]()

## Development Environment

### Docker Development Container

The development environment is containerized using a custom Docker image that extends the official Go image with additional development tools.

```mermaid
graph TB
    subgraph "Base Image"
        GOLANG_IMAGE["golang:${GOLANG_VERSION}"]
    end
    
    subgraph "Development Tools Installation"
        GOLINT["golang.org/x/lint/golint@latest"]
        MOQ["github.com/matryer/moq@latest"]
        INEFFASSIGN["github.com/gordonklaus/ineffassign@latest"]
        MISSPELL["github.com/client9/misspell/cmd/misspell@latest"]
    end
    
    subgraph "Build Image Configuration"
        BUILDIMAGE_TAG["BUILDIMAGE_TAG ?= golang$(GOLANG_VERSION)"]
        BUILDIMAGE["BUILDIMAGE ?= vgpu-device-manager-build"]
        DOCKERFILE_PATH["docker/Dockerfile.devel"]
    end
    
    GOLANG_IMAGE --> GOLINT
    GOLANG_IMAGE --> MOQ
    GOLANG_IMAGE --> INEFFASSIGN
    GOLANG_IMAGE --> MISSPELL
    
    BUILDIMAGE_TAG --> BUILDIMAGE
    DOCKERFILE_PATH --> BUILDIMAGE
```

**Sources:** [docker/Dockerfile.devel:14-21](), [Makefile:21-22]()

### Docker Build Targets

The Makefile provides Docker-wrapped versions of all build targets for consistent development environments:

**Docker Target Execution Pattern:**
```bash
docker run --rm -e GOCACHE=/tmp/.cache -v $(PWD):$(PWD) -w $(PWD) --user $(id -u):$(id -g) $(BUILDIMAGE) make $(TARGET)
```

**Sources:** [Makefile:96-105]()

## Build Targets

### Primary Build Targets

| Target | Purpose | Dependencies |
|--------|---------|--------------|
| `cmds` | Build all command binaries | `$(CMD_TARGETS)` |
| `build` | Compile all packages | None |
| `test` | Run tests with coverage | `build` |
| `lint` | Run linting checks | None |
| `fmt` | Format code | None |
| `coverage` | Generate coverage report | `test` |

**Sources:** [Makefile:27-28](), [Makefile:42-76]()

### Check Targets

```mermaid
graph LR
    subgraph "Code Quality Checks"
        ASSERT_FMT["assert-fmt"]
        VET["vet"]
        LINT["lint"]
        INEFFASSIGN["ineffassign"]
        MISSPELL["misspell"]
    end
    
    subgraph "Check Process"
        CHECK_TARGETS["CHECK_TARGETS"]
        FMT_OUT["fmt.out file"]
        GOLANGCI_RUN["golangci-lint run"]
    end
    
    CHECK_TARGETS --> ASSERT_FMT
    CHECK_TARGETS --> VET
    CHECK_TARGETS --> LINT
    CHECK_TARGETS --> INEFFASSIGN
    CHECK_TARGETS --> MISSPELL
    
    ASSERT_FMT --> FMT_OUT
    LINT --> GOLANGCI_RUN
```

**Sources:** [Makefile:27](), [Makefile:54-64]()

## Testing and Coverage

### Test Execution

The testing system uses Go's built-in testing framework with coverage reporting:

**Test Command:**
```bash
go test -v -coverprofile=$(COVERAGE_FILE) $(MODULE)/...
```

**Coverage Processing:**
- Excludes mock files (`_mock.go`) from coverage calculations
- Generates both raw and filtered coverage reports
- Uses `go tool cover` for coverage analysis

**Sources:** [Makefile:70-76]()

### Coverage Configuration

| Variable | Value | Purpose |
|----------|-------|---------|
| `COVERAGE_FILE` | `coverage.out` | Primary coverage output |
| `$(COVERAGE_FILE).no-mocks` | `coverage.out.no-mocks` | Filtered coverage without mocks |

**Sources:** [Makefile:70](), [Makefile:75]()

## Version Management

The build system supports version injection through ldflags during compilation:

```mermaid
graph LR
    subgraph "Version Sources"
        GIT_COMMIT["$(GIT_COMMIT)"]
        VERSION["$(VERSION)"]
        VERSIONS_MK["versions.mk"]
    end
    
    subgraph "Injection Target"
        VERSION_PKG_PATH["$(VERSION_PKG)"]
        INTERNAL_INFO["internal/info package"]
    end
    
    subgraph "Build Flags"
        LDFLAGS["-ldflags"]
        GIT_COMMIT_FLAG["-X $(VERSION_PKG).gitCommit=$(GIT_COMMIT)"]
        VERSION_FLAG["-X $(VERSION_PKG).version=$(VERSION)"]
    end
    
    GIT_COMMIT --> GIT_COMMIT_FLAG
    VERSION --> VERSION_FLAG
    VERSIONS_MK --> VERSION
    
    VERSION_PKG_PATH --> INTERNAL_INFO
    GIT_COMMIT_FLAG --> LDFLAGS
    VERSION_FLAG --> LDFLAGS
```

**Sources:** [Makefile:19](), [Makefile:36](), [Makefile:44]()

---

