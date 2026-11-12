<!-- source: DeepWiki mcp.deepwiki.com · repo termux/termux-root-packages · page 3 CI/CD Pipeline · fetched 2026-10-26 -->

# CI/CD Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/static/powered-by-fosshost.png](.github/static/powered-by-fosshost.png)
- [.github/workflows/packages.yml](.github/workflows/packages.yml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [scripts/lint-packages.sh](scripts/lint-packages.sh)
- [start-builder.sh](start-builder.sh)

</details>



This document describes the automated build and distribution system for the termux-root-packages repository. The CI/CD pipeline handles building packages across multiple Android architectures, validates package definitions, and distributes compiled packages to APT repositories.

For information about package definition and build system architecture, see [Build System Architecture](#2). For details about individual package categories, see [Package Categories](#4).

## Pipeline Architecture Overview

The CI/CD system uses GitHub Actions to orchestrate a multi-stage pipeline that detects changes, builds packages, and distributes them to public repositories.

### High-Level Pipeline Flow

```mermaid
graph TD
    subgraph "Triggers"
        A[push_to_master] --> D[GitHub_Actions]
        B[pull_request] --> D
        C[workflow_dispatch] --> D
    end
    
    subgraph "Build Stage"
        D --> E[changed_files_detection]
        E --> F[lint_packages_sh]
        F --> G[build_matrix]
        G --> H[aarch64_build]
        G --> I[arm_build]
        G --> J[i686_build]
        G --> K[x86_64_build]
    end
    
    subgraph "Docker Environment"
        L[termux_package_builder] --> H
        L --> I
        L --> J
        L --> K
    end
    
    subgraph "Upload Stage"
        H --> M[artifact_collection]
        I --> M
        J --> M
        K --> M
        M --> N[aptly_upload_file]
        N --> O[aptly_add_to_repo]
        O --> P[aptly_publish_repo]
    end
    
    subgraph "Distribution"
        P --> Q[packages_termux_org]
        P --> R[grimler_se_mirror]
    end
```

Sources: [.github/workflows/packages.yml:1-237]()

### Build Trigger System

The pipeline activates under three conditions with different file change detection strategies:

| Trigger Type | Condition | File Detection |
|--------------|-----------|----------------|
| `push` | Push to master branch with changes in `packages/**` | Git diff-tree analysis |
| `pull_request` | PR with changes in `packages/**` | Base commit to HEAD comparison |
| `workflow_dispatch` | Manual trigger with package list | User-specified packages |

The change detection logic implements sophisticated git analysis to identify modified, added, and deleted packages:

```mermaid
graph LR
    subgraph "Change Detection Logic"
        A[git_diff_tree] --> B[package_regex_matching]
        B --> C{package_or_subpackage}
        C -->|package| D[check_directory_exists]
        C -->|subpackage| E[check_subpackage_file_exists]
        D -->|exists| F[built_packages_txt]
        D -->|deleted| G[deleted_packages_txt]
        E -->|exists| H[built_subpackages_txt]
        E -->|deleted| G
    end
```

Sources: [.github/workflows/packages.yml:35-103]()

## Build Process Flow

### Package Linting System

Before compilation, all modified packages undergo validation through the `lint-packages.sh` script:

```mermaid
graph TD
    subgraph "Linting Process"
        A[lint_packages_sh] --> B[syntax_check]
        B --> C[termux_pkg_homepage_validation]
        C --> D[termux_pkg_description_length]
        D --> E[termux_pkg_license_validation]
        E --> F[termux_pkg_version_check]
        F --> G[termux_pkg_srcurl_https_validation]
        G --> H[termux_pkg_sha256_validation]
    end
    
    subgraph "License Validation"
        I[check_package_license] --> J[valid_license_list]
        J --> K{license_match}
        K -->|valid| L[pass]
        K -->|invalid| M[fail]
    end
    
    E --> I
```

The linting system validates over 20 different package metadata fields including required fields like `TERMUX_PKG_HOMEPAGE`, `TERMUX_PKG_DESCRIPTION`, and `TERMUX_PKG_LICENSE`.

Sources: [scripts/lint-packages.sh:53-433]()

### Docker Build Environment

The build process utilizes a containerized environment managed by `start-builder.sh`:

```mermaid
graph TD
    subgraph "Docker Build Setup"
        A[start_builder_sh] --> B[termux_package_builder_image]
        B --> C[container_uid_gid_adjustment]
        C --> D[termux_packages_submodule_mount]
        D --> E[package_directory_copy]
        E --> F[build_package_sh_execution]
    end
    
    subgraph "Container Configuration"
        G[CONTAINER_NAME] --> H["termux-package-builder"]
        I[IMAGE_NAME] --> J["termux/package-builder"]
        K[BUILDER_HOME] --> L["/home/builder"]
    end
    
    B --> G
    B --> I
    D --> K
```

The container setup includes automatic UID/GID mapping to prevent permission issues and mounts the termux-packages submodule for build infrastructure access.

Sources: [start-builder.sh:20-98]()

## Architecture Matrix Build System

### Multi-Architecture Support

The pipeline builds packages simultaneously across four Android architectures:

```mermaid
graph TD
    subgraph "Build Matrix Strategy"
        A[strategy_matrix] --> B[aarch64_job]
        A --> C[arm_job]
        A --> D[i686_job]
        A --> E[x86_64_job]
    end
    
    subgraph "Build Environment Variables"
        F[ANDROID_HOME] --> G["/opt/termux/android-sdk"]
        H[NDK] --> I["/opt/termux/android-ndk"]
    end
    
    subgraph "Build Execution"
        J[build_package_sh] --> K[architecture_specific_compilation]
        K --> L[deb_file_generation]
        L --> M[sha256sum_verification]
    end
    
    B --> F
    C --> F
    D --> F
    E --> F
    
    B --> J
    C --> J
    D --> J
    E --> J
```

Each architecture job runs independently with `fail-fast: false` to ensure all architectures attempt building even if one fails.

Sources: [.github/workflows/packages.yml:24-27](), [.github/workflows/packages.yml:119-122]()

## Package Distribution System

### Aptly Repository Management

The upload process uses the Aptly API to manage package repositories:

```mermaid
graph LR
    subgraph "Repository Upload Flow"
        A[artifact_download] --> B[aptly_upload_file]
        B --> C[aptly_add_to_repo]
        C --> D[aptly_delete_dir]
        D --> E[aptly_publish_repo]
    end
    
    subgraph "Repository Configuration"
        F[REPOSITORY_NAME] --> G["termux-root"]
        H[REPOSITORY_DISTRIBUTION] --> I["root"]
        J[packages_termux_org] --> K["https://packages-cf.termux.org/aptly-api"]
        L[grimler_se_mirror] --> M["https://aptly-api.grimler.se"]
    end
    
    B --> F
    C --> H
    E --> J
    E --> L
```

The system uploads to two repository endpoints: the primary `packages.termux.org` and the `grimler.se` mirror, with the primary repository supporting automatic GPG signing.

Sources: [.github/workflows/packages.yml:154-236]()

### Upload Process Implementation

The upload job implements robust error handling and artifact processing:

| Step | Function | Purpose |
|------|----------|---------|
| Artifact Download | `actions/download-artifact@v2` | Collect build artifacts from all architectures |
| File Extraction | `tar xf "$archive"` | Extract .deb files from compressed archives |
| Batch Upload | `aptly_upload_file` | Upload files to temporary directory |
| Repository Integration | `aptly_add_to_repo` | Add packages to repository |
| Publication | `aptly_publish_repo` | Make changes visible in web root |

The process handles both regular packages and static variants using glob patterns: `debs/${package}_*.deb` and `debs/${package}-static_*.deb`.

Sources: [.github/workflows/packages.yml:167-195]()

## Build Optimization Features

### Conditional Build Logic

The pipeline includes several optimization mechanisms:

- **No-build tag**: Commits with `%ci:no-build` in the message skip building
- **Duplicate detection**: Package lists are deduplicated using `uniq`
- **Incremental builds**: Only changed packages are rebuilt
- **Parallel execution**: Architecture builds run concurrently

```mermaid
graph TD
    subgraph "Build Optimization"
        A[commit_message_check] --> B{contains_ci_no_build}
        B -->|yes| C[skip_build_exit_0]
        B -->|no| D[package_change_detection]
        D --> E[duplicate_removal_uniq]
        E --> F[parallel_architecture_builds]
    end
```

Sources: [.github/workflows/packages.yml:59-65](), [.github/workflows/packages.yml:105-117]()

### Artifact Management

Built packages are archived and stored using GitHub Actions artifacts with architecture-specific naming:

- Artifact name pattern: `termux-root-packages-${arch}-${github.sha}`
- Archive format: `debs-${arch}-${github.sha}.tar`
- Checksum generation: SHA256 verification for all `.deb` files

Sources: [.github/workflows/packages.yml:133-141]()

---

