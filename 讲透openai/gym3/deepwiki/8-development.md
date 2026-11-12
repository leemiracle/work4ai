<!-- source: DeepWiki mcp.deepwiki.com · repo openai/gym3 · page 8 Development · fetched 2026-10-26 -->

# Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yaml](.github/workflows/ci.yaml)
- [CONTRIBUTING.md](CONTRIBUTING.md)

</details>



This document covers the development infrastructure, testing setup, and contribution guidelines for the gym3 project. It includes information about the continuous integration pipeline, testing frameworks, and how to contribute to the codebase.

For information about using gym3's testing utilities in your own projects, see [Testing and CI](#8.1). For specific contribution guidelines and project policies, see [Contributing](#8.2).

## Development Workflow

The gym3 project follows a standard GitHub-based development workflow with automated testing and cross-platform validation. The development process emphasizes compatibility across multiple operating systems and integration with the broader RL ecosystem.

```mermaid
graph TD
    DEV["Developer"] --> BRANCH["Feature Branch"]
    BRANCH --> COMMIT["Local Commits"]
    COMMIT --> PUSH["Push to GitHub"]
    PUSH --> CI["GitHub Actions CI"]
    
    subgraph "CI Pipeline"
        CI --> MATRIX["Test Matrix"]
        MATRIX --> UBUNTU["Ubuntu 18.04"]
        MATRIX --> MACOS["macOS 10.15"] 
        MATRIX --> WINDOWS["Windows 2019"]
        
        UBUNTU --> CONDA_U["conda environment"]
        MACOS --> CONDA_M["conda environment"]
        WINDOWS --> CONDA_W["conda environment"]
        
        CONDA_U --> MPI_U["mpi4py install"]
        CONDA_M --> MPI_M["mpi4py install"]
        CONDA_W --> SKIP_MPI["skip mpi4py"]
        
        MPI_U --> BASELINES_U["baselines install"]
        MPI_M --> BASELINES_M["baselines install"] 
        SKIP_MPI --> BASELINES_W["baselines install"]
        
        BASELINES_U --> PYTEST_U["pytest execution"]
        BASELINES_M --> PYTEST_M["pytest execution"]
        BASELINES_W --> PYTEST_W["pytest execution"]
    end
    
    PYTEST_U --> RESULTS["Test Results"]
    PYTEST_M --> RESULTS
    PYTEST_W --> RESULTS
    
    RESULTS --> PASS["Tests Pass"]
    RESULTS --> FAIL["Tests Fail"]
    
    PASS --> MERGE["Ready for Merge"]
    FAIL --> DEBUG["Debug & Fix"]
    DEBUG --> COMMIT
```

The development workflow ensures cross-platform compatibility by testing on Ubuntu, macOS, and Windows environments using Python 3.6. Each platform follows the same basic steps but with platform-specific adaptations for dependency installation.

Sources: [.github/workflows/ci.yaml:1-40]()

## Continuous Integration Pipeline

The project uses GitHub Actions for continuous integration, with a comprehensive test matrix that validates functionality across different operating systems and dependency configurations.

```mermaid
graph TB
    subgraph "Trigger Events"
        PUSH["git push"] --> WORKFLOW["ci.yaml workflow"]
    end
    
    subgraph "Environment Setup"
        WORKFLOW --> CHECKOUT["actions/checkout@v2"]
        CHECKOUT --> MINICONDA["goanpeca/setup-miniconda@v1.5.0"]
        MINICONDA --> ENV_FILE["environment.yml"]
    end
    
    subgraph "Dependency Installation"
        ENV_FILE --> MPI_CHECK{"OS != Windows?"}
        MPI_CHECK -->|Yes| MPI_INSTALL["conda install mpi4py=3.0.3"]
        MPI_CHECK -->|No| SKIP_MPI["Skip mpi4py"]
        MPI_INSTALL --> BASELINES_INSTALL["pip install baselines"]
        SKIP_MPI --> BASELINES_INSTALL
    end
    
    subgraph "Test Execution"
        BASELINES_INSTALL --> PYTEST_RUN["pytest"]
        PYTEST_RUN --> TEST_RESULTS["Test Results"]
    end
    
    subgraph "Platform Matrix"
        UBUNTU_1804["ubuntu-18.04"]
        MACOS_1015["macos-10.15"]
        WINDOWS_2019["windows-2019"]
        PYTHON_36["Python 3.6"]
    end
    
    WORKFLOW -.-> UBUNTU_1804
    WORKFLOW -.-> MACOS_1015  
    WORKFLOW -.-> WINDOWS_2019
    WORKFLOW -.-> PYTHON_36
```

The CI pipeline includes several key components:

| Component | Purpose | Platform Support |
|-----------|---------|------------------|
| `actions/checkout@v2` | Source code retrieval | All platforms |
| `goanpeca/setup-miniconda@v1.5.0` | Conda environment setup | All platforms |
| `environment.yml` | Base dependencies | All platforms |
| `mpi4py=3.0.3` | Parallel processing support | Unix-like only |
| `baselines` | RL framework integration | All platforms |
| `pytest` | Test execution | All platforms |

The configuration specifically handles Windows compatibility by skipping `mpi4py` installation, as noted in the comment at [.github/workflows/ci.yaml:25](). The baselines dependency is installed from a specific GitHub commit to ensure reproducible builds.

Sources: [.github/workflows/ci.yaml:1-32]()

## Testing Infrastructure

The project uses `pytest` as the primary testing framework, executed through the CI pipeline after environment setup and dependency installation. The testing strategy focuses on cross-platform validation and integration testing with external RL frameworks.

```mermaid
graph LR
    subgraph "Test Dependencies"
        CONDA_ENV["conda environment"]
        MPI4PY["mpi4py"] 
        BASELINES["baselines@9ee399f"]
        PYTEST["pytest"]
    end
    
    subgraph "Test Execution"
        PYTEST_CMD["pytest command"]
        TEST_DISCOVERY["Test Discovery"]
        TEST_RUN["Test Execution"]
    end
    
    subgraph "Platform Validation"
        UBUNTU_TESTS["Ubuntu Tests"]
        MACOS_TESTS["macOS Tests"] 
        WINDOWS_TESTS["Windows Tests"]
    end
    
    CONDA_ENV --> PYTEST_CMD
    MPI4PY --> PYTEST_CMD
    BASELINES --> PYTEST_CMD
    PYTEST --> PYTEST_CMD
    
    PYTEST_CMD --> TEST_DISCOVERY
    TEST_DISCOVERY --> TEST_RUN
    
    TEST_RUN --> UBUNTU_TESTS
    TEST_RUN --> MACOS_TESTS
    TEST_RUN --> WINDOWS_TESTS
```

The testing setup includes integration with external dependencies, particularly the OpenAI baselines library installed from a specific commit (`9ee399f5b20cd70ac0a871927a6cf043b478193f`) to ensure consistent behavior across test runs.

Sources: [.github/workflows/ci.yaml:28-32]()

## Project Contribution Policy

The gym3 project maintains a focused scope with specific guidelines for contributions and feature additions.

| Contribution Type | Policy | Reporting Method |
|-------------------|--------|------------------|
| Bug Reports | Welcomed | GitHub issue tracker |
| Installation Issues | Welcomed | GitHub issue tracker |
| Platform Support Issues | Welcomed | GitHub issue tracker |
| New Features | Not currently accepted | N/A |
| New Wrappers | Not currently accepted | N/A |

The project explicitly states that it is "not currently looking to add new features or wrappers to `gym3`", indicating a focus on stability and maintenance rather than feature expansion.

Sources: [CONTRIBUTING.md:1-4]()

## Release and Deployment

The CI configuration includes commented-out sections for automated package building and PyPI deployment, suggesting that releases are currently handled manually rather than through automated CI/CD.

```mermaid
graph TD
    MANUAL_RELEASE["Manual Release Process"]
    BUILD_STEP["python setup.py sdist bdist_wheel"]
    PYPI_UPLOAD["twine upload dist/*"]
    
    MANUAL_RELEASE --> BUILD_STEP
    BUILD_STEP --> PYPI_UPLOAD
    
    subgraph "Commented CI Deployment"
        AUTO_BUILD["Automated Build"]
        AUTO_UPLOAD["Automated Upload"]
        SECRETS["PyPI Credentials"]
    end
    
    AUTO_BUILD -.->|"Currently Disabled"| AUTO_UPLOAD
    SECRETS -.->|"Not Active"| AUTO_UPLOAD
```

The presence of commented-out deployment code at [.github/workflows/ci.yaml:33-39]() indicates that automated deployment infrastructure exists but is not currently active, likely requiring manual intervention for releases.

Sources: [.github/workflows/ci.yaml:33-39]()

---

