<!-- source: DeepWiki mcp.deepwiki.com · repo termux/game-packages · page 2 Repository Architecture · fetched 2026-10-26 -->

# Repository Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitmodules](.gitmodules)

</details>



## Purpose and Scope

This document explains the structural organization of the termux-game-packages repository and its integration with the broader Termux ecosystem. It covers the Git submodule architecture, directory structure, and integration patterns that enable automated package building and distribution.

For information about the CI/CD pipeline and build automation, see [CI/CD and Build System](#3). For details about individual package structure and development, see [Package Development Guide](#4).

## Git Submodule Architecture

The termux-game-packages repository is architecturally built around a Git submodule pattern that integrates with the main termux-packages repository. This design allows the game packages to leverage the full build infrastructure and tooling from the main Termux package system.

### Submodule Configuration

```mermaid
graph TB
    subgraph "termux-game-packages Repository"
        ROOT["termux-game-packages<br/>(Root Repository)"]
        GITMODULES[".gitmodules<br/>Submodule Config"]
        PACKAGES["packages/<br/>Game Package Definitions"]
        SCRIPTS["scripts/<br/>Build Tools"]
        WORKFLOWS[".github/workflows/<br/>CI/CD Pipeline"]
    end
    
    subgraph "Integrated termux-packages"
        SUBMODULE["termux-packages/<br/>(Git Submodule)"]
        BUILD_COMMON["build-package.sh<br/>Core Build Logic"]
        COMMON_SCRIPTS["scripts/<br/>Common Utilities"]
        DOCKER_SETUP["Dockerfile<br/>Build Environment"]
    end
    
    subgraph "External Dependencies"
        UPSTREAM["https://github.com/termux/termux-packages<br/>Upstream Repository"]
        DOCKER_HUB["termux/package-builder<br/>Docker Image"]
    end
    
    ROOT --> GITMODULES
    GITMODULES --> SUBMODULE
    SUBMODULE --> UPSTREAM
    SCRIPTS --> BUILD_COMMON
    WORKFLOWS --> DOCKER_SETUP
    DOCKER_SETUP --> DOCKER_HUB
    
    PACKAGES --> BUILD_COMMON
    WORKFLOWS --> COMMON_SCRIPTS
```

**Git Submodule Integration**

The repository uses a single Git submodule to integrate the entire termux-packages infrastructure:

| Component | Path | Purpose |
|-----------|------|---------|
| Submodule Definition | `.gitmodules` | Defines the termux-packages submodule |
| Submodule Directory | `termux-packages/` | Contains the full termux-packages repository |
| Integration Point | `termux-packages/build-package.sh` | Core build script used by game packages |

Sources: [.gitmodules:1-4]()

### Submodule Integration Pattern

```mermaid
graph LR
    subgraph "Repository Root"
        GAME_PKG["packages/game/build.sh<br/>Game Package Script"]
        START_BUILDER["start-builder.sh<br/>Build Entry Point"]
    end
    
    subgraph "termux-packages Submodule"
        BUILD_PKG["build-package.sh<br/>Core Build Engine"]
        COMMON_FUNCS["scripts/build/setup/termux_*.sh<br/>Build Functions"]
        DOCKER_ENV["Dockerfile<br/>Build Environment"]
    end
    
    subgraph "Build Process Flow"
        INVOKE["./start-builder.sh game<br/>Build Invocation"]
        DELEGATE["Delegate to build-package.sh<br/>With game package path"]
        EXECUTE["Execute termux_step_* functions<br/>From build.sh"]
    end
    
    START_BUILDER --> BUILD_PKG
    BUILD_PKG --> COMMON_FUNCS
    GAME_PKG --> BUILD_PKG
    
    INVOKE --> DELEGATE
    DELEGATE --> EXECUTE
    EXECUTE --> COMMON_FUNCS
```

**Integration Benefits**

This submodule architecture provides several key advantages:

- **Shared Infrastructure**: Game packages use the same build system, dependency resolution, and packaging logic as main Termux packages
- **Consistent Environment**: All packages build in the same Docker environment with identical toolchains
- **Unified CI/CD**: The CI/CD pipeline leverages termux-packages workflows and publishing mechanisms
- **Automatic Updates**: The submodule can be updated to pull in improvements from the main repository

Sources: [.gitmodules:1-4]()

## Directory Structure and Organization

The repository follows a standardized directory structure that separates game packages from build infrastructure:

```mermaid
graph TB
    subgraph "Repository Root Structure"
        ROOT["/"]
        PACKAGES["packages/<br/>Game Package Definitions"]
        SCRIPTS["scripts/<br/>Build & Utility Scripts"]
        WORKFLOWS[".github/workflows/<br/>CI/CD Automation"]
        SUBMODULE["termux-packages/<br/>Git Submodule"]
        CONFIG[".gitmodules<br/>Submodule Configuration"]
    end
    
    subgraph "Package Directory Structure"
        GAME_DIRS["packages/game-name/<br/>Individual Game Packages"]
        BUILD_SCRIPT["build.sh<br/>Package Build Definition"]
        PATCHES["*.patch<br/>Source Code Patches"]
        METADATA["metadata.json<br/>Package Information"]
    end
    
    subgraph "Scripts Directory"
        LINTER["lint-packages.sh<br/>Package Validation"]
        DISPATCHER["cirrus-ci_dispatcher.sh<br/>CI Coordination"]
        UTILS["Various utility scripts"]
    end
    
    ROOT --> PACKAGES
    ROOT --> SCRIPTS
    ROOT --> WORKFLOWS
    ROOT --> SUBMODULE
    ROOT --> CONFIG
    
    PACKAGES --> GAME_DIRS
    GAME_DIRS --> BUILD_SCRIPT
    GAME_DIRS --> PATCHES
    GAME_DIRS --> METADATA
    
    SCRIPTS --> LINTER
    SCRIPTS --> DISPATCHER
    SCRIPTS --> UTILS
```

**Directory Structure Overview**

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `packages/` | Game package definitions | `*/build.sh`, `*.patch` files |
| `scripts/` | Build and utility scripts | `lint-packages.sh`, `cirrus-ci_dispatcher.sh` |
| `.github/workflows/` | CI/CD pipeline definitions | `packages.yml`, workflow files |
| `termux-packages/` | Git submodule with core build system | `build-package.sh`, `Dockerfile` |

Sources: [.gitmodules:1-4]()

## Integration with Termux Ecosystem

The repository integrates with multiple components of the Termux ecosystem to provide a complete package management solution:

### Ecosystem Integration Points

```mermaid
graph TB
    subgraph "termux-game-packages"
        REPO["Repository<br/>Game Package Definitions"]
        BUILD_SYSTEM["Build System<br/>Docker + Scripts"]
        CI_CD["CI/CD Pipeline<br/>GitHub Actions"]
    end
    
    subgraph "termux-packages Ecosystem"
        MAIN_REPO["termux-packages<br/>Main Repository"]
        BUILD_INFRA["Build Infrastructure<br/>Docker Images & Scripts"]
        PACKAGE_SERVER["packages.termux.org<br/>Aptly Package Server"]
    end
    
    subgraph "External Systems"
        GITHUB["GitHub<br/>Source Code Hosting"]
        DOCKER_HUB["Docker Hub<br/>termux/package-builder"]
        GAME_SOURCES["Upstream Game Sources<br/>Various Git/Archive Sources"]
    end
    
    subgraph "End User Systems"
        TERMUX_APP["Termux App<br/>Android Terminal"]
        APT_CLIENT["apt/pkg commands<br/>Package Installation"]
    end
    
    REPO --> MAIN_REPO
    BUILD_SYSTEM --> BUILD_INFRA
    CI_CD --> PACKAGE_SERVER
    
    MAIN_REPO --> DOCKER_HUB
    BUILD_INFRA --> DOCKER_HUB
    PACKAGE_SERVER --> APT_CLIENT
    
    GITHUB --> REPO
    GAME_SOURCES --> BUILD_SYSTEM
    APT_CLIENT --> TERMUX_APP
```

**Integration Components**

The repository integrates with the Termux ecosystem through several key mechanisms:

1. **Build System Integration**: Uses `termux-packages/build-package.sh` for consistent package building
2. **Infrastructure Sharing**: Leverages Docker images and build environments from the main repository
3. **Package Distribution**: Publishes packages to the same APT repository used by main Termux packages
4. **CI/CD Integration**: Uses similar GitHub Actions workflows as the main repository

Sources: [.gitmodules:1-4]()

## Build Environment Architecture

The build environment architecture demonstrates how the repository integrates with containerized build systems:

### Build Environment Flow

```mermaid
graph LR
    subgraph "Local Development"
        DEV_ENV["Developer Environment"]
        START_BUILDER["start-builder.sh<br/>Local Build Script"]
    end
    
    subgraph "Docker Build Environment"
        DOCKER_IMAGE["termux/package-builder<br/>Docker Image"]
        BUILD_CONTAINER["Build Container<br/>Ubuntu-based Environment"]
        TOOLCHAIN["Cross-compilation Toolchain<br/>NDK + Build Tools"]
    end
    
    subgraph "Build Process"
        PACKAGE_SCRIPT["packages/game/build.sh<br/>Package Definition"]
        BUILD_ENGINE["termux-packages/build-package.sh<br/>Build Engine"]
        OUTPUT_DEBS["*.deb Package Files<br/>Architecture-specific"]
    end
    
    DEV_ENV --> START_BUILDER
    START_BUILDER --> DOCKER_IMAGE
    DOCKER_IMAGE --> BUILD_CONTAINER
    BUILD_CONTAINER --> TOOLCHAIN
    
    PACKAGE_SCRIPT --> BUILD_ENGINE
    BUILD_ENGINE --> TOOLCHAIN
    TOOLCHAIN --> OUTPUT_DEBS
```

**Build Environment Integration**

The build environment demonstrates several architectural patterns:

- **Containerization**: All builds occur in standardized Docker containers to ensure reproducibility
- **Cross-compilation**: The build system supports multiple target architectures (aarch64, arm, i686, x86_64)
- **Toolchain Management**: The termux-packages submodule provides consistent toolchain configuration
- **Artifact Management**: Built packages are collected and published through the CI/CD pipeline

Sources: [.gitmodules:1-4]()

## Data Flow and Integration Patterns

The repository implements several data flow patterns that demonstrate its integration with the broader Termux ecosystem:

### Package Build and Distribution Flow

```mermaid
graph TD
    subgraph "Source Control"
        COMMIT["Git Commit<br/>Package Changes"]
        TRIGGER["GitHub Actions<br/>Workflow Trigger"]
    end
    
    subgraph "Build Matrix"
        DETECT["Change Detection<br/>git diff analysis"]
        BUILD_ARCH1["Build: aarch64<br/>Docker Container"]
        BUILD_ARCH2["Build: arm<br/>Docker Container"]
        BUILD_ARCH3["Build: i686<br/>Docker Container"]
        BUILD_ARCH4["Build: x86_64<br/>Docker Container"]
    end
    
    subgraph "Package Publishing"
        COLLECT["Collect Artifacts<br/>*.deb files"]
        UPLOAD["Upload to Aptly<br/>packages.termux.org"]
        PUBLISH["Publish Repository<br/>Update package indices"]
    end
    
    subgraph "Distribution"
        APT_REPO["APT Repository<br/>packages.termux.org"]
        USER_INSTALL["User Installation<br/>pkg install game"]
    end
    
    COMMIT --> TRIGGER
    TRIGGER --> DETECT
    DETECT --> BUILD_ARCH1
    DETECT --> BUILD_ARCH2
    DETECT --> BUILD_ARCH3
    DETECT --> BUILD_ARCH4
    
    BUILD_ARCH1 --> COLLECT
    BUILD_ARCH2 --> COLLECT
    BUILD_ARCH3 --> COLLECT
    BUILD_ARCH4 --> COLLECT
    
    COLLECT --> UPLOAD
    UPLOAD --> PUBLISH
    PUBLISH --> APT_REPO
    APT_REPO --> USER_INSTALL
```

**Data Flow Characteristics**

The repository's data flow demonstrates several important architectural characteristics:

- **Event-Driven**: Package builds are triggered by Git commits and pull requests
- **Parallel Processing**: Multiple architecture builds occur simultaneously
- **Artifact Management**: Built packages are collected and distributed through a centralized system
- **Integration Points**: The system integrates with external package repositories and user installations

Sources: [.gitmodules:1-4]()

This architecture enables the termux-game-packages repository to function as a specialized extension of the main Termux package system while maintaining consistency and leveraging shared infrastructure.

---

