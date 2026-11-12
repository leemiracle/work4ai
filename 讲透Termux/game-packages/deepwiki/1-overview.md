<!-- source: DeepWiki mcp.deepwiki.com · repo termux/game-packages · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/static/powered-by-fosshost.png](.github/static/powered-by-fosshost.png)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)

</details>



This document introduces the termux-game-packages repository, its original purpose as a collection of game packages for Termux, and its current status as a merged component of the main termux-packages repository. It covers the high-level architecture, key systems, and integration points within the broader Termux ecosystem.

For detailed information about CI/CD and build processes, see [CI/CD and Build System](#3). For package development workflows, see [Package Development Guide](#4). For specific game package examples, see [Game Package Examples](#5).

## Repository Status and Integration

The termux-game-packages repository has been **merged into the main termux-packages repository** as stated in [README.md:3](). This means that while the repository still exists for historical purposes, all active development and issue tracking now occurs in the primary termux-packages repository.

### Current Integration Architecture

```mermaid
graph TB
    subgraph "Historical Repository"
        GP["termux-game-packages<br/>github.com/termux/game-packages"]
        README["README.md<br/>Merge Notice"]
        LEGACY["Legacy CI/CD<br/>.github/workflows/"]
    end
    
    subgraph "Active Development"
        TP["termux-packages<br/>Main Repository"]
        GAMES["games/<br/>Game Package Directory"]
        MAIN_CI["Main CI/CD Pipeline"]
    end
    
    subgraph "Package Distribution"
        GAME_REPO["game-repo<br/>Package Repository"]
        PKG_INSTALL["pkg install game-repo"]
        APTLY["Aptly Package Server<br/>packages.termux.org"]
    end
    
    GP -.->|"MERGED INTO"| TP
    README --> GP
    LEGACY --> GP
    
    TP --> GAMES
    TP --> MAIN_CI
    MAIN_CI --> APTLY
    APTLY --> GAME_REPO
    GAME_REPO --> PKG_INSTALL
    
    style GP fill:#f9f,stroke:#333,stroke-width:2px
    style TP fill:#9f9,stroke:#333,stroke-width:2px
    style GAME_REPO fill:#bbf,stroke:#333,stroke-width:2px
```

**Sources:** [README.md:3](), [README.md:34-38]()

## Package Management System

The termux-game-packages ecosystem provides a standardized approach to packaging and distributing games for the Termux Android terminal environment. The system handles cross-compilation, dependency management, and platform-specific adaptations.

### Core Package Structure

```mermaid
graph TB
    subgraph "Package Definition"
        BUILD_SH["build.sh<br/>Package Script"]
        PKG_VARS["TERMUX_PKG_*<br/>Configuration Variables"]
        PATCHES["*.patch<br/>Source Modifications"]
    end
    
    subgraph "Package Metadata"
        VERSION["TERMUX_PKG_VERSION"]
        REVISION["TERMUX_PKG_REVISION"]
        SRCURL["TERMUX_PKG_SRCURL"]
        SHA256["TERMUX_PKG_SHA256"]
        DEPENDS["TERMUX_PKG_DEPENDS"]
    end
    
    subgraph "Build Process"
        DOCKER["Docker Container<br/>termux/package-builder"]
        BUILD_SCRIPT["build-package.sh"]
        START_BUILDER["start-builder.sh"]
    end
    
    BUILD_SH --> PKG_VARS
    PKG_VARS --> VERSION
    PKG_VARS --> REVISION
    PKG_VARS --> SRCURL
    PKG_VARS --> SHA256
    PKG_VARS --> DEPENDS
    
    BUILD_SH --> DOCKER
    START_BUILDER --> DOCKER
    BUILD_SCRIPT --> DOCKER
    
    PATCHES --> BUILD_SH
```

**Sources:** [README.md:21-31](), [CONTRIBUTING.md:47-66]()

## Development Workflow

The repository provides a comprehensive development environment with Docker-based builds and standardized contribution processes.

### Build System Components

```mermaid
graph LR
    subgraph "Local Development"
        CLONE["git clone<br/>termux/game-packages"]
        DOCKER_BUILD["./start-builder.sh<br/>./build-package.sh"]
        NATIVE_BUILD["./termux-packages/<br/>build-package.sh"]
    end
    
    subgraph "Package Updates"
        FORK["Fork Repository"]
        BRANCH["git checkout -b<br/>package-name-update"]
        UPDATE["Update build.sh<br/>TERMUX_PKG_VERSION<br/>TERMUX_PKG_SHA256"]
        COMMIT["git commit -m<br/>package-name: update to X.Y.Z"]
    end
    
    subgraph "Quality Assurance"
        REPOLOGY["Repology<br/>Package Version Tracking"]
        SHA_CALC["sha256sum<br/>Source Verification"]
        CI_BUILD["GitHub Actions<br/>CI/CD Pipeline"]
    end
    
    CLONE --> DOCKER_BUILD
    CLONE --> NATIVE_BUILD
    
    FORK --> BRANCH
    BRANCH --> UPDATE
    UPDATE --> COMMIT
    
    REPOLOGY --> UPDATE
    SHA_CALC --> UPDATE
    COMMIT --> CI_BUILD
```

**Sources:** [README.md:16-31](), [CONTRIBUTING.md:8-103]()

## Package Ecosystem Integration

The game packages integrate with the broader Termux ecosystem through standardized interfaces and dependency management.

### Distribution and Installation Flow

```mermaid
graph TD
    subgraph "Package Creation"
        SOURCE["Upstream Source<br/>GitHub/SourceForge"]
        PACKAGE_DEF["packages/game-name/<br/>build.sh"]
        BUILD_HOOKS["termux_step_*<br/>Build Lifecycle"]
    end
    
    subgraph "CI/CD Pipeline"
        GITHUB_ACTIONS["GitHub Actions<br/>.github/workflows/"]
        MATRIX_BUILD["Matrix Build<br/>aarch64, arm, i686, x86_64"]
        ARTIFACT_UPLOAD["Artifact Upload<br/>debs-{arch}-{sha}.tar"]
    end
    
    subgraph "Package Distribution"
        APTLY_SERVER["Aptly Package Server<br/>packages.termux.org"]
        GAME_REPO_PKG["game-repo<br/>Repository Package"]
        PKG_MANAGER["pkg install<br/>Package Manager"]
    end
    
    subgraph "User Installation"
        TERMUX_DEVICE["Termux Android App"]
        INSTALLED_GAMES["$PREFIX/bin/<br/>Game Executables"]
        GAME_DATA["$PREFIX/share/games/<br/>Game Data Files"]
    end
    
    SOURCE --> PACKAGE_DEF
    PACKAGE_DEF --> BUILD_HOOKS
    BUILD_HOOKS --> GITHUB_ACTIONS
    
    GITHUB_ACTIONS --> MATRIX_BUILD
    MATRIX_BUILD --> ARTIFACT_UPLOAD
    ARTIFACT_UPLOAD --> APTLY_SERVER
    
    APTLY_SERVER --> GAME_REPO_PKG
    GAME_REPO_PKG --> PKG_MANAGER
    PKG_MANAGER --> TERMUX_DEVICE
    
    TERMUX_DEVICE --> INSTALLED_GAMES
    TERMUX_DEVICE --> GAME_DATA
```

**Sources:** [README.md:33-38](), [CONTRIBUTING.md:101-102]()

## Key System Components

The termux-game-packages system consists of several interconnected components that handle different aspects of the package lifecycle:

| Component | Purpose | Key Files |
|-----------|---------|-----------|
| **Package Definitions** | Game-specific build scripts and metadata | `packages/*/build.sh` |
| **Build System** | Docker-based cross-compilation environment | `start-builder.sh`, `build-package.sh` |
| **CI/CD Pipeline** | Automated building and publishing | `.github/workflows/` |
| **Contribution Tools** | Developer workflow support | `CONTRIBUTING.md` guidelines |
| **Package Repository** | Distribution mechanism | `game-repo` package |

### Package Variable Standards

The system uses standardized `TERMUX_PKG_*` variables for consistent package definitions:

- `TERMUX_PKG_VERSION`: Upstream version number
- `TERMUX_PKG_REVISION`: Termux-specific revision (reset on version updates)
- `TERMUX_PKG_SRCURL`: Source code download URL
- `TERMUX_PKG_SHA256`: Source archive integrity hash
- `TERMUX_PKG_DEPENDS`: Runtime dependencies

**Sources:** [CONTRIBUTING.md:47-76]()

## Current Status and Future Development

With the merger into termux-packages, the game packages are now part of the main Termux package ecosystem. Users should:

1. **Install packages** using `pkg install game-repo` as described in [README.md:34-38]()
2. **Report issues** to the main termux-packages repository
3. **Submit contributions** following the workflow in [CONTRIBUTING.md:8-103]()

The repository remains available for historical reference and to maintain existing CI/CD badges and documentation links.

**Sources:** [README.md:3](), [README.md:5]()

---

