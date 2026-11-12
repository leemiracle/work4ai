<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/tilus · page 7 Development Infrastructure · fetched 2026-10-26 -->

# Development Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/setup-environment/action.yaml](.github/actions/setup-environment/action.yaml)
- [.github/copy-pr-bot.yaml](.github/copy-pr-bot.yaml)
- [.github/workflows/deploy-docs.yaml](.github/workflows/deploy-docs.yaml)
- [.github/workflows/deploy-wheel-to-pypi.yaml](.github/workflows/deploy-wheel-to-pypi.yaml)
- [.github/workflows/format-and-lint.yaml](.github/workflows/format-and-lint.yaml)
- [.github/workflows/tests.yaml](.github/workflows/tests.yaml)

</details>



This document covers the development infrastructure for contributors and maintainers of the Tilus project. It includes the continuous integration and deployment (CI/CD) systems, build processes, testing frameworks, and development tools that support the Tilus codebase.

For information about using Tilus as an end-user, see [Getting Started](#2). For details on the testing and CI/CD workflows specifically, see [Testing and CI/CD](#7.1). For the documentation build system, see [Documentation System](#7.2).

## CI/CD Pipeline Architecture

The Tilus project uses GitHub Actions for continuous integration and deployment. The CI/CD system is designed around GPU-enabled runners and includes smart change detection to optimize build times.

### CI/CD Workflow Overview

```mermaid
flowchart TD
    subgraph "Trigger Events"
        A["`Push to pull-request/*`"]
        B["`Manual Workflow Dispatch`"]
        C["`Release Published`"]
    end
    
    subgraph "Change Detection"
        D["`check-changes Job`"]
        E["`changed-files Action`"]
        F["`should_run_tests Output`"]
        G["`should_run_examples Output`"]
        H["`should_run_docs Output`"]
    end
    
    subgraph "Parallel Jobs"
        I["`tests Job`"]
        J["`examples Job`"]
        K["`docs Job`"]
        L["`format-and-lint Job`"]
    end
    
    subgraph "Deployment"
        M["`deploy-docs Workflow`"]
        N["`deploy-wheel-to-pypi Workflow`"]
    end
    
    A --> D
    B --> M
    C --> N
    A --> L
    D --> E
    E --> F
    E --> G
    E --> H
    F --> I
    G --> J
    H --> K
    
    I --> O["`all-functional-tests`"]
    J --> O
    K --> O
```

The system uses the `step-security/changed-files` action to detect changes in specific directories and only run relevant jobs when files have changed.

Sources: [.github/workflows/tests.yaml:1-157](), [.github/workflows/format-and-lint.yaml:1-30]()

### Environment Setup and Infrastructure

```mermaid
flowchart TD
    subgraph "Container Infrastructure"
        A["`nvidia/cuda:12.6.2-devel-ubuntu22.04`"]
        B["`GPU Runners`"]
        C["`linux-amd64-gpu-l4-latest-1`"]
    end
    
    subgraph "Setup Environment Action"
        D["`setup-environment Action`"]
        E["`install-tilus Action`"]
        F["`Python 3.10 Setup`"]
        G["`Git and CMake Install`"]
    end
    
    subgraph "Development Tools"
        H["`ruff Formatter/Linter`"]
        I["`mypy Type Checker`"]
        J["`pytest Test Runner`"]
        K["`sphinx Documentation`"]
    end
    
    subgraph "Dependencies"
        L["`hidet Package`"]
        M["`torch Package`"]
        N["`cuda-python Package`"]
        O["`flash-attn Package`"]
    end
    
    A --> D
    B --> A
    C --> B
    D --> E
    D --> F
    D --> G
    E --> L
    E --> M
    E --> N
    F --> H
    F --> I
    F --> J
    F --> K
    J --> O
```

The `setup-environment` action provides a reusable workflow component that standardizes the build environment across all jobs.

Sources: [.github/actions/setup-environment/action.yaml:1-56](), [.github/workflows/tests.yaml:74-79]()

## Build and Deployment System

### PyPI Deployment Pipeline

```mermaid
flowchart TD
    subgraph "Build Process"
        A["`build-wheel Job`"]
        B["`pyproject.toml Configuration`"]
        C["`Wheel Artifact Upload`"]
    end
    
    subgraph "Deployment Triggers"
        D["`Release Published Event`"]
        E["`workflow_dispatch Event`"]
    end
    
    subgraph "Deployment Pipeline"
        F["`deploy-to-pypi Job`"]
        G["`Trusted Publishing`"]
        H["`PyPI Environment`"]
    end
    
    subgraph "Artifacts"
        I["`tilus-wheel Artifact`"]
        J["`dist/*.whl Files`"]
    end
    
    D --> A
    E --> A
    A --> B
    A --> C
    C --> I
    I --> J
    A --> F
    F --> G
    G --> H
```

The deployment system uses GitHub's trusted publishing feature to securely deploy to PyPI without storing API tokens.

Sources: [.github/workflows/deploy-wheel-to-pypi.yaml:1-59]()

### Documentation Deployment

```mermaid
flowchart TD
    subgraph "Documentation Build"
        A["`make html Command`"]
        B["`sphinx Build System`"]
        C["`docs/build/html Output`"]
    end
    
    subgraph "GitHub Pages"
        D["`upload-pages-artifact Action`"]
        E["`deploy-pages Action`"]
        F["`GitHub Pages Environment`"]
    end
    
    subgraph "Infrastructure"
        G["`yaoyao-centml Runner`"]
        H["`GPU Container Access`"]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    G --> H
    H --> A
```

Documentation builds require GPU access to execute example code and generate dynamic content.

Sources: [.github/workflows/deploy-docs.yaml:1-53]()

## Testing Infrastructure

### Test Execution Framework

The testing system is designed around GPU-specific requirements and includes comprehensive validation of examples and documentation.

| Test Category | Purpose | Runner Requirements | Key Files |
|---------------|---------|-------------------|-----------|
| Unit Tests | Core functionality validation | GPU-enabled containers | `tests/**` |
| Examples | Tutorial and example validation | GPU with flash-attn | `examples/**` |
| Documentation | Sphinx build validation | GPU for code execution | `docs/**` |
| Format/Lint | Code quality checks | Standard runners | `python/**` |

### Test Job Dependencies

```mermaid
flowchart TD
    subgraph "Test Dependencies"
        A["`pytest Framework`"]
        B["`GPU Requirements`"]
        C["`CUDA 12.6.2 Environment`"]
    end
    
    subgraph "Example Dependencies"
        D["`flash-attn Package`"]
        E["`--no-build-isolation Flag`"]
        F["`run-examples.sh Script`"]
    end
    
    subgraph "Format/Lint Tools"
        G["`ruff Formatter`"]
        H["`mypy Type Checker`"]
        I["`check-format-and-lint.sh Script`"]
    end
    
    subgraph "Execution Flow"
        J["`tests Job`"]
        K["`examples Job`"]
        L["`format-and-lint Job`"]
        M["`all-functional-tests Job`"]
    end
    
    A --> J
    B --> J
    C --> J
    D --> K
    E --> K
    F --> K
    G --> L
    H --> L
    I --> L
    J --> M
    K --> M
    L --> M
```

The `all-functional-tests` job aggregates results from all test categories and provides a single pass/fail status for the entire pipeline.

Sources: [.github/workflows/tests.yaml:56-156](), [.github/workflows/format-and-lint.yaml:12-30]()

## Development Tools and Quality Assurance

### Code Quality Pipeline

```mermaid
flowchart TD
    subgraph "Static Analysis"
        A["`ruff check`"]
        B["`ruff format`"]
        C["`mypy Type Checking`"]
    end
    
    subgraph "Configuration Files"
        D["`pyproject.toml`"]
        E["`ruff Configuration`"]
        F["`mypy Configuration`"]
    end
    
    subgraph "Execution"
        G["`check-format-and-lint.sh`"]
        H["`Version Display`"]
        I["`Error Reporting`"]
    end
    
    D --> E
    D --> F
    E --> A
    E --> B
    F --> C
    G --> H
    G --> A
    G --> B
    G --> C
    A --> I
    B --> I
    C --> I
```

The quality assurance system enforces consistent code formatting and type safety across the entire codebase.

Sources: [.github/workflows/format-and-lint.yaml:26-29]()

### Repository Configuration

| Component | Configuration File | Purpose |
|-----------|-------------------|---------|
| CI/CD Workflows | `.github/workflows/*.yaml` | Define automated build and test processes |
| Environment Setup | `.github/actions/setup-environment/action.yaml` | Standardize build environment |
| PR Bot | `.github/copy-pr-bot.yaml` | Automated PR synchronization |
| Package Config | `pyproject.toml` | Python package metadata and tool configuration |

The development infrastructure supports both internal NVIDIA development workflows and external open-source contributions through standardized tooling and comprehensive automation.

Sources: [.github/copy-pr-bot.yaml:1-5]()

---

