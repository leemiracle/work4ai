<!-- source: DeepWiki mcp.deepwiki.com · repo TissueImageAnalytics/tiatoolbox · page 8 Development and Contributing · fetched 2026-10-21 -->

# Development and Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/python-package.yml](.github/workflows/python-package.yml)
- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [CONTRIBUTING.rst](CONTRIBUTING.rst)
- [benchmarks/annotation_store.ipynb](benchmarks/annotation_store.ipynb)
- [benchmarks/annotation_store_alloc.py](benchmarks/annotation_store_alloc.py)
- [pyproject.toml](pyproject.toml)
- [requirements/requirements_dev.txt](requirements/requirements_dev.txt)
- [tiatoolbox/utils/env_detection.py](tiatoolbox/utils/env_detection.py)

</details>



This document provides comprehensive information for developers who want to contribute to TIAToolbox, including development workflow, code quality tools, testing infrastructure, and CI/CD processes. This covers the technical aspects of contributing code, running tests, and maintaining code quality.

For information about using TIAToolbox's features and APIs, see [Core Concepts](#1.2) and [Examples and Tutorials](#6). For CI/CD and development infrastructure details, see [CI/CD and Development Infrastructure](#8.3).

## Development Workflow Overview

TIAToolbox follows a structured development workflow that emphasizes code quality, automated testing, and collaborative development through GitHub. The development process integrates multiple tools and stages to ensure code reliability and maintainability.

### Development Process Flow

```mermaid
flowchart TD
    A["Developer Fork & Clone"] --> B["Local Development"]
    B --> C["pre-commit Hooks"]
    C --> D["Local Testing"]
    D --> E["Git Commit & Push"]
    E --> F["GitHub Pull Request"]
    F --> G["GitHub Actions CI"]
    G --> H["Code Review"]
    H --> I["Merge to develop"]
    I --> J["Release Pipeline"]
    
    C --> K["ruff Linting"]
    C --> L["mdformat"]
    C --> M["pytest Changed Files"]
    
    G --> N["Matrix Testing"]
    G --> O["Coverage Report"]
    G --> P["Docker Build"]
    
    J --> Q["Test PyPI"]
    J --> R["Production PyPI"]
    
    subgraph "Local Quality Checks"
        K
        L
        M
    end
    
    subgraph "CI Pipeline"
        N
        O
        P
    end
    
    subgraph "Release Process"
        Q
        R
    end
```

Sources: [.pre-commit-config.yaml:1-71](), [.github/workflows/python-package.yml:1-118](), [CONTRIBUTING.rst:52-93]()

## Code Quality Infrastructure

TIAToolbox employs a comprehensive code quality infrastructure built around modern Python tooling. The system uses `ruff` as the primary linter and formatter, `pytest` for testing, and `pre-commit` for automated quality checks.

### Code Quality Tools Architecture

```mermaid
graph TB
    subgraph "Pre-commit Framework"
        PreCommit["pre-commit"] --> LocalHooks["Local Hooks"]
        PreCommit --> ExternalRepos["External Repos"]
        
        LocalHooks --> PytestChanged["pytest-changed-files"]
        LocalHooks --> NotebookFormat["notebook-markdown-format"]
        
        ExternalRepos --> RuffCheck["ruff check"]
        ExternalRepos --> RuffFormat["ruff format"]
        ExternalRepos --> MdFormat["mdformat"]
        ExternalRepos --> PreCommitHooks["pre-commit-hooks"]
    end
    
    subgraph "Ruff Configuration"
        RuffConfig["pyproject.toml"] --> RuffRules["Lint Rules (A,B,D,E,F,...)"]
        RuffConfig --> RuffSettings["Line Length: 88"]
        RuffConfig --> RuffTarget["Target: py39"]
    end
    
    subgraph "Testing Framework"
        PytestConfig["pytest.ini_options"] --> Coverage["coverage.run"]
        PytestConfig --> TestCollection["collect_ignore"]
        Coverage --> CoverageReport["coverage.report"]
    end
    
    RuffCheck --> RuffConfig
    RuffFormat --> RuffConfig
    PytestChanged --> PytestConfig
```

The code quality system is configured through several key files:

- **Pre-commit Configuration**: [.pre-commit-config.yaml:1-71]() defines all automated checks
- **Ruff Settings**: [pyproject.toml:52-178]() configures linting rules and formatting
- **Test Configuration**: [pyproject.toml:1-17]() sets up pytest and coverage

### Linting and Formatting Rules

TIAToolbox uses an extensive set of linting rules through `ruff`, covering code style, security, performance, and documentation standards:

| Category | Rules | Purpose |
|----------|-------|---------|
| Core | A, B, E, F, W | flake8-builtins, bugbear, pycodestyle, pyflakes |
| Documentation | D | pydocstyle with Google convention |
| Security | S | flake8-bandit security checks |
| Performance | PERF | Performance optimizations |
| Modern Python | UP | pyupgrade compatibility |

Sources: [pyproject.toml:53-106](), [pyproject.toml:147-149]()

## Testing Framework

The testing infrastructure uses `pytest` with comprehensive coverage reporting and parallel execution capabilities. Tests are automatically triggered by pre-commit hooks for changed files and run in full during CI.

### Testing Architecture

```mermaid
graph TB
    subgraph "Test Execution"
        PytestRunner["pytest"] --> TestDiscovery["Test Discovery"]
        TestDiscovery --> UnitTests["Unit Tests"]
        TestDiscovery --> IntegrationTests["Integration Tests"]
        TestDiscovery --> BenchmarkTests["Benchmark Tests"]
    end
    
    subgraph "Coverage Analysis"
        CoverageRun["coverage.run"] --> SourceTracking["Source: tiatoolbox"]
        CoverageRun --> OmitFiles["Omit: tests/*, __main__.py"]
        SourceTracking --> CoverageReport["coverage.report"]
        OmitFiles --> CoverageReport
    end
    
    subgraph "Test Categories"
        UnitTests --> CoreTests["Core Algorithm Tests"]
        UnitTests --> ModelTests["Model Tests"]
        UnitTests --> IOTests["I/O Tests"]
        
        IntegrationTests --> WSITests["WSI Processing Tests"]
        IntegrationTests --> PipelineTests["Pipeline Tests"]
        
        BenchmarkTests --> AnnotationBench["annotation_store.ipynb"]
        BenchmarkTests --> AllocBench["annotation_store_alloc.py"]
    end
    
    subgraph "CI Integration"
        GithubActions["GitHub Actions"] --> MatrixTesting["Python 3.9-3.12"]
        MatrixTesting --> CoverageUpload["Codecov & DeepSource"]
    end
    
    PytestRunner --> CoverageRun
    CoverageReport --> CoverageUpload
```

### Test Configuration

The test system is configured with specific collection and coverage rules:

- **Test Collection**: [pyproject.toml:2]() excludes setup files and benchmarks
- **Coverage Tracking**: [pyproject.toml:4-7]() monitors source code with branch coverage
- **Excluded Files**: [pyproject.toml:7]() omits tests, main modules, and typing files

Sources: [pyproject.toml:1-17](), [.github/workflows/python-package.yml:56-62]()

## CI/CD Pipeline

The CI/CD system uses GitHub Actions to provide automated testing, building, and deployment across multiple Python versions and platforms. The pipeline ensures code quality and compatibility before merging changes.

### GitHub Actions Workflow

```mermaid
flowchart TD
    subgraph "Trigger Events"
        PushTrigger["Push to develop/main"]
        PRTrigger["Pull Request"]
        TagTrigger["Tag v*"]
    end
    
    subgraph "Build Job"
        MatrixSetup["Matrix: Python 3.9-3.12"] --> DepInstall["Install Dependencies"]
        DepInstall --> SystemDeps["System Dependencies"]
        SystemDeps --> VersionInfo["Print Version Info"]
        VersionInfo --> RuffLint["Ruff Linting"]
        RuffLint --> PytestRun["pytest with Coverage"]
        PytestRun --> CoverageUpload["Upload Coverage"]
    end
    
    subgraph "Release Job"
        BuildSuccess["Build Success"] --> ReleaseCondition["Check Branch/Tag"]
        ReleaseCondition --> PackageBuild["Build Package"]
        PackageBuild --> TestPyPI["Publish to Test PyPI"]
        TestPyPI --> ProductionPyPI["Publish to PyPI (tags only)"]
    end
    
    subgraph "Dependencies"
        SystemDeps --> OpenJPEG["libopenjp2-7"]
        SystemDeps --> OpenSlide["libopenslide-dev"]
        DepInstall --> Requirements["requirements.txt"]
        DepInstall --> TestDeps["pytest, ruff, coverage"]
    end
    
    PushTrigger --> MatrixSetup
    PRTrigger --> MatrixSetup
    TagTrigger --> MatrixSetup
    
    PytestRun --> BuildSuccess
    ReleaseCondition --> TestPyPI
```

### CI Configuration Details

The CI pipeline configuration includes:

- **Platform Support**: [.github/workflows/python-package.yml:16]() runs on ubuntu-24.04
- **Python Matrix**: [.github/workflows/python-package.yml:20]() tests Python 3.9, 3.10, 3.11, 3.12
- **System Dependencies**: [.github/workflows/python-package.yml:30-31]() installs OpenJPEG and OpenSlide
- **Coverage Reporting**: [.github/workflows/python-package.yml:63-78]() uploads to Codecov and DeepSource

Sources: [.github/workflows/python-package.yml:1-118]()

## Development Dependencies

TIAToolbox maintains separate dependency sets for development and production environments. Development dependencies include testing tools, documentation generators, and code quality utilities.

### Development Dependency Structure

```mermaid
graph TB
    subgraph "Development Dependencies"
        DevReqs["requirements_dev.txt"] --> BaseReqs["requirements.txt"]
        DevReqs --> DocsReqs["docs/requirements.txt"]
        
        DevReqs --> TestingTools["Testing Tools"]
        DevReqs --> QualityTools["Quality Tools"]
        DevReqs --> BuildTools["Build Tools"]
    end
    
    subgraph "Testing Tools"
        TestingTools --> Pytest["pytest>=7.2.0"]
        TestingTools --> Coverage["coverage>=7.0.0"]
        TestingTools --> PytestCov["pytest-cov>=4.0.0"]
        TestingTools --> PytestXdist["pytest-xdist[psutil]"]
    end
    
    subgraph "Quality Tools"
        QualityTools --> PreCommit["pre-commit>=2.20.0"]
        QualityTools --> Ruff["ruff==0.11.8"]
        QualityTools --> MyPy["mypy>=1.6.1"]
    end
    
    subgraph "Build Tools"
        BuildTools --> Poetry["poetry-bumpversion>=0.3.1"]
        BuildTools --> Twine["twine>=4.0.1"]
        BuildTools --> Wheel["wheel>=0.37.1"]
    end
```

Key development dependencies include:

- **Testing**: `pytest` with coverage and parallel execution support
- **Linting**: `ruff` for comprehensive code analysis
- **Type Checking**: `mypy` for static type analysis
- **Documentation**: Sphinx and related tools
- **Build**: Poetry and wheel building tools

Sources: [requirements/requirements_dev.txt:1-17]()

## Contributing Process

The contribution process follows GitHub's fork-and-pull-request model with additional quality gates and review requirements. Contributors must follow coding standards and pass all automated checks.

### Contribution Workflow

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Fork as "Forked Repo"
    participant Origin as "Origin Repo"
    participant CI as "GitHub Actions"
    participant Review as "Code Review"
    
    Dev->>Fork: 1. Fork Repository
    Dev->>Fork: 2. Clone & Setup
    Dev->>Fork: 3. Create Feature Branch
    Dev->>Fork: 4. Make Changes
    Dev->>Fork: 5. Run pre-commit
    Fork->>Dev: 6. Local Quality Checks
    Dev->>Fork: 7. Commit & Push
    Fork->>Origin: 8. Create Pull Request
    Origin->>CI: 9. Trigger CI Pipeline
    CI->>Origin: 10. Report Results
    Origin->>Review: 11. Request Review
    Review->>Origin: 12. Approve/Request Changes
    Origin->>Origin: 13. Merge to develop
```

### Setup Instructions

To set up a development environment:

1. **Fork and Clone**: [CONTRIBUTING.rst:56-59]() describes the initial setup
2. **Virtual Environment**: [CONTRIBUTING.rst:61-65]() shows environment creation
3. **Install Dependencies**: Install from `requirements_dev.txt`
4. **Pre-commit Setup**: [CONTRIBUTING.rst:78-84]() configures git hooks

### Pull Request Requirements

All pull requests must meet these requirements:

- **Tests**: [CONTRIBUTING.rst:99]() requires test coverage for new functionality
- **Documentation**: [CONTRIBUTING.rst:100]() requires documentation updates
- **Python Compatibility**: [CONTRIBUTING.rst:101]() must work on Python 3.9-3.12
- **Quality Checks**: All pre-commit hooks and CI checks must pass

Sources: [CONTRIBUTING.rst:94-102]()

## Development Environment Detection

TIAToolbox includes sophisticated environment detection capabilities to adapt behavior based on the runtime context. This helps optimize performance and user experience across different platforms and environments.

### Environment Detection System

```mermaid
graph TB
    subgraph "Environment Detection"
        EnvDetection["env_detection.py"] --> InteractiveCheck["is_interactive()"]
        EnvDetection --> NotebookCheck["is_notebook()"]
        EnvDetection --> CondaCheck["in_conda_env()"]
        EnvDetection --> CICheck["running_on_ci()"]
        EnvDetection --> GPUCheck["has_gpu()"]
        EnvDetection --> NetworkCheck["has_network()"]
    end
    
    subgraph "CI Platform Detection"
        CICheck --> TravisCheck["running_on_travis()"]
        CICheck --> GitHubCheck["running_on_github()"]
        CICheck --> CircleCICheck["running_on_circleci()"]
        CICheck --> KaggleCheck["running_on_kaggle()"]
        CICheck --> ColabCheck["running_on_colab()"]
    end
    
    subgraph "System Analysis"
        GPUCheck --> TorchCUDA["torch.cuda.is_available()"]
        NetworkCheck --> SocketTest["Socket Connection Test"]
        CondaCheck --> EnvVars["CONDA_DEFAULT_ENV, CONDA_PREFIX"]
    end
    
    subgraph "Dependency Checking"
        EnvDetection --> PixmanCheck["pixman_versions()"]
        PixmanCheck --> CondaPixman["check_pixman_using_anaconda()"]
        PixmanCheck --> DpkgPixman["check_pixman_using_dpkg()"]
        PixmanCheck --> BrewPixman["check_pixman_using_brew()"]
    end
```

The environment detection system provides:

- **Interactive Detection**: [tiatoolbox/utils/env_detection.py:50-81]() detects REPL and notebook environments
- **CI Platform Detection**: [tiatoolbox/utils/env_detection.py:125-177]() identifies various CI services
- **Hardware Detection**: [tiatoolbox/utils/env_detection.py:34-47]() checks for GPU availability
- **Dependency Verification**: [tiatoolbox/utils/env_detection.py:249-380]() validates system libraries

Sources: [tiatoolbox/utils/env_detection.py:1-452]()

---

