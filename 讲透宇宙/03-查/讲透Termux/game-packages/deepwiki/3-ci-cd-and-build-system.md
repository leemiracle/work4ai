<!-- source: DeepWiki mcp.deepwiki.com · repo termux/game-packages · page 3 CI/CD and Build System · fetched 2026-10-26 -->

# CI/CD and Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/packages.yml](.github/workflows/packages.yml)

</details>



This document covers the automated build and deployment pipeline for the termux-game-packages repository. The CI/CD system automatically detects package changes, builds them across multiple architectures, validates the builds, and publishes them to the Termux package repository. For information about the individual package build process and development tools, see [Package Development Guide](#4) and [Development Tools](#4.3).

## System Overview

The CI/CD system is implemented as a GitHub Actions workflow that provides comprehensive automation for package management. It handles both pull request validation and production deployment through a sophisticated multi-stage pipeline.

### Workflow Architecture

```mermaid
graph TB
    subgraph "Trigger Events"
        PUSH["Push to master<br/>packages/** changes"]
        PR["Pull Request<br/>packages/** changes"]
    end
    
    subgraph "Build Matrix"
        BUILD_AARCH64["build: aarch64"]
        BUILD_ARM["build: arm"] 
        BUILD_I686["build: i686"]
        BUILD_X86_64["build: x86_64"]
    end
    
    subgraph "Core Build Process"
        DETECT["Package Detection<br/>git diff analysis"]
        LINT["Lint Validation<br/>scripts/lint-packages.sh"]
        BUILD_STEP["Package Build<br/>start-builder.sh"]
        ARCHIVE["Artifact Creation<br/>debs-{arch}-{sha}.tar"]
    end
    
    subgraph "Upload Pipeline"
        DOWNLOAD["Download Artifacts<br/>actions/download-artifact"]
        UPLOAD["Upload to Aptly<br/>packages.termux.org"]
        PUBLISH["Publish Repository<br/>GPG signing"]
    end
    
    PUSH --> DETECT
    PR --> DETECT
    
    DETECT --> LINT
    LINT --> BUILD_AARCH64
    LINT --> BUILD_ARM
    LINT --> BUILD_I686
    LINT --> BUILD_X86_64
    
    BUILD_AARCH64 --> BUILD_STEP
    BUILD_ARM --> BUILD_STEP
    BUILD_I686 --> BUILD_STEP
    BUILD_X86_64 --> BUILD_STEP
    
    BUILD_STEP --> ARCHIVE
    ARCHIVE --> DOWNLOAD
    DOWNLOAD --> UPLOAD
    UPLOAD --> PUBLISH
    
    PR -.->|"Skip Upload"| ARCHIVE
```

**Sources:** [.github/workflows/packages.yml:1-257]()

## Build Triggers and Matrix Strategy

The workflow triggers on two primary events with specific path filtering to optimize build performance:

### Event Triggers

| Event Type | Trigger Condition | Behavior |
|------------|-------------------|----------|
| `push` | Branch: `master`, Path: `packages/**` | Full build and publish |
| `pull_request` | Path: `packages/**` | Build validation only |

### Architecture Matrix

The build system targets four Android architectures in parallel:

```mermaid
graph LR
    subgraph "Build Matrix Strategy"
        MATRIX["fail-fast: false"]
        AARCH64["aarch64<br/>64-bit ARM"]
        ARM["arm<br/>32-bit ARM"]
        I686["i686<br/>32-bit x86"]
        X86_64["x86_64<br/>64-bit x86"]
    end
    
    MATRIX --> AARCH64
    MATRIX --> ARM
    MATRIX --> I686
    MATRIX --> X86_64
```

**Sources:** [.github/workflows/packages.yml:19-22]()

## Package Change Detection

The system implements intelligent change detection to build only modified packages, significantly improving build efficiency.

### Change Detection Algorithm

```mermaid
graph TD
    subgraph "Commit Analysis"
        SINGLE["Single Commit<br/>git diff-tree HEAD"]
        MULTI["Multi Commit<br/>git diff-tree OLD~1..HEAD"]
        PR_DIFF["Pull Request<br/>git diff-tree BASE..HEAD"]
    end
    
    subgraph "File Processing"
        FILTER["Filter packages/** files"]
        PARSE["Parse package names<br/>^packages/([a-z0-9-]*)/"]
        SUBPKG["Detect subpackages<br/>*.subpackage.sh"]
    end
    
    subgraph "Package Lists"
        BUILT["built_packages.txt<br/>Packages to build"]
        DELETED["deleted_packages.txt<br/>Packages to remove"]
        SUBBUILT["built_subpackages.txt<br/>Subpackages to build"]
    end
    
    SINGLE --> FILTER
    MULTI --> FILTER
    PR_DIFF --> FILTER
    
    FILTER --> PARSE
    PARSE --> SUBPKG
    SUBPKG --> BUILT
    SUBPKG --> DELETED
    SUBPKG --> SUBBUILT
```

The detection logic handles three commit scenarios:
- **Single commit push**: Uses `git diff-tree` on HEAD commit
- **Multi-commit push**: Compares range from `OLD_COMMIT~1` to `HEAD_COMMIT`
- **Pull request**: Compares base branch to HEAD

**Sources:** [.github/workflows/packages.yml:30-48](), [.github/workflows/packages.yml:61-87]()

## Build Process Flow

### Package Validation and Building

```mermaid
graph TD
    subgraph "Pre-Build Validation"
        NO_BUILD["Check %ci:no-build tag<br/>Force skip build"]
        LINT_STEP["scripts/lint-packages.sh<br/>Validate build scripts"]
    end
    
    subgraph "Build Execution"
        START_BUILDER["start-builder.sh<br/>Docker environment"]
        BUILD_PACKAGE["build-package.sh<br/>Package compilation"]
        MOVE_DEBS["Move built packages<br/>termux-packages/debs/"]
    end
    
    subgraph "Artifact Preparation"
        COLLECT["Collect package lists<br/>built_packages.txt"]
        TAR_CREATE["Create tar archive<br/>debs-{arch}-{sha}.tar"]
        CHECKSUM["Generate SHA256 checksums<br/>Built packages"]
    end
    
    NO_BUILD --> LINT_STEP
    LINT_STEP --> START_BUILDER
    START_BUILDER --> BUILD_PACKAGE
    BUILD_PACKAGE --> MOVE_DEBS
    MOVE_DEBS --> COLLECT
    COLLECT --> TAR_CREATE
    TAR_CREATE --> CHECKSUM
```

### Build Control Features

The system includes several control mechanisms:

1. **Force Skip**: `%ci:no-build` tag in commit message forces successful exit
2. **Incremental Builds**: Only builds packages with detected changes
3. **Dependency Handling**: Processes subpackages automatically
4. **Artifact Management**: Creates compressed archives to handle special characters

**Sources:** [.github/workflows/packages.yml:51-57](), [.github/workflows/packages.yml:103-117]()

## Upload and Publishing Pipeline

### Aptly Integration

The publishing system integrates with the Aptly package repository management system:

```mermaid
graph TD
    subgraph "Artifact Processing"
        DOWNLOAD_ARTIFACTS["Download build artifacts<br/>actions/download-artifact"]
        EXTRACT_TARS["Extract tar archives<br/>for archive in *.tar"]
    end
    
    subgraph "Aptly API Operations"
        UPLOAD_FILES["Upload to temporary directory<br/>aptly-api/files/{repo}-{sha}"]
        ADD_TO_REPO["Add packages to repository<br/>aptly-api/repos/{repo}/file/{dir}"]
        PUBLISH_REPO["Publish repository<br/>aptly-api/publish/{repo}/{dist}"]
    end
    
    subgraph "Cleanup Operations"
        DELETE_TEMP["Delete temporary directory<br/>aptly_delete_dir()"]
        GPG_SIGN["GPG signing<br/>secrets.GPG_PASSPHRASE"]
    end
    
    DOWNLOAD_ARTIFACTS --> EXTRACT_TARS
    EXTRACT_TARS --> UPLOAD_FILES
    UPLOAD_FILES --> ADD_TO_REPO
    ADD_TO_REPO --> PUBLISH_REPO
    PUBLISH_REPO --> DELETE_TEMP
    PUBLISH_REPO --> GPG_SIGN
```

### Repository Configuration

| Configuration | Value |
|---------------|--------|
| `REPOSITORY_NAME` | `termux-games` |
| `REPOSITORY_DISTRIBUTION` | `games` |
| API Endpoint | `https://packages.termux.org/aptly-api` |

### Error Handling and Cleanup

The upload process includes comprehensive error handling:

- **HTTP Status Monitoring**: Validates API responses (200 OK expected)
- **Automatic Cleanup**: Removes temporary directories on failure
- **Graceful Degradation**: Handles long-running publish operations (exit code 52)
- **Warning Processing**: Extracts and displays non-critical warnings

**Sources:** [.github/workflows/packages.yml:138-256](), [.github/workflows/packages.yml:149-166]()

## Environment and Dependencies

### Build Environment

```mermaid
graph LR
    subgraph "GitHub Actions Environment"
        RUNNER["ubuntu-latest<br/>GitHub runner"]
        ANDROID_HOME["/opt/termux/android-sdk<br/>Android SDK"]
        NDK["/opt/termux/android-ndk<br/>Android NDK"]
    end
    
    subgraph "Authentication"
        APTLY_AUTH["secrets.APTLY_API_AUTH<br/>Aptly API credentials"]
        GPG_PASS["secrets.GPG_PASSPHRASE<br/>GPG signing key"]
    end
    
    RUNNER --> ANDROID_HOME
    RUNNER --> NDK
    RUNNER --> APTLY_AUTH
    RUNNER --> GPG_PASS
```

### Key Dependencies

- **Git Operations**: Requires `fetch-depth: 1000` for proper diff analysis
- **JSON Processing**: Uses `jq` for parsing GitHub event data
- **Docker Integration**: Leverages `start-builder.sh` for containerized builds
- **Aptly API**: RESTful API for package repository management

**Sources:** [.github/workflows/packages.yml:16-18](), [.github/workflows/packages.yml:25-27]()

## Conditional Execution Logic

The workflow implements sophisticated conditional logic to optimize resource usage:

### Build vs. Upload Separation

```mermaid
graph TD
    subgraph "Build Job"
        BUILD_ALWAYS["Always runs<br/>PR + Push"]
        BUILD_MATRIX["Matrix: 4 architectures<br/>Parallel execution"]
        BUILD_ARTIFACTS["Upload artifacts<br/>game-packages-{sha}"]
    end
    
    subgraph "Upload Job"
        UPLOAD_CONDITION["if: github.event_name != 'pull_request'<br/>Push only"]
        UPLOAD_NEEDS["needs: build<br/>Depends on build completion"]
        UPLOAD_PUBLISH["Publish to packages.termux.org<br/>Production deployment"]
    end
    
    BUILD_ALWAYS --> BUILD_MATRIX
    BUILD_MATRIX --> BUILD_ARTIFACTS
    BUILD_ARTIFACTS --> UPLOAD_CONDITION
    UPLOAD_CONDITION --> UPLOAD_NEEDS
    UPLOAD_NEEDS --> UPLOAD_PUBLISH
```

This design ensures:
- **Pull requests**: Build validation without deployment
- **Push to master**: Full build and publish pipeline
- **Resource optimization**: Upload job only runs when needed

**Sources:** [.github/workflows/packages.yml:127-128]()

---

