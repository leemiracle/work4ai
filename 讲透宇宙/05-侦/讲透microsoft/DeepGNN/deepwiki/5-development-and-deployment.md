<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/DeepGNN · page 5 Development and Deployment · fetched 2026-10-26 -->

# Development and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/lint/action.yml](.github/actions/lint/action.yml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [docs/torch/distrib.rst](docs/torch/distrib.rst)
- [examples/tensorflow/requirements.txt](examples/tensorflow/requirements.txt)

</details>



This document provides comprehensive guidance for developers working on the DeepGNN codebase, covering the complete development lifecycle from environment setup to deployment. It includes build system configuration, testing infrastructure, continuous integration workflows, and package distribution processes.

For specific build system details, see [Build System](#5.1). For packaging and distribution specifics, see [Package Distribution](#5.2). For detailed testing procedures, see [Testing and CI/CD](#5.3).

## Development Environment Setup

### Prerequisites by Platform

DeepGNN supports development across Linux, macOS, and Windows platforms with specific toolchain requirements for each:

| Platform | Required Tools | Build Config |
|----------|---------------|--------------|
| Linux | Bazel 6.4.0, g++-12, clang-format | `--config=linux` |
| macOS | XCode CLI tools, Bazel (via Homebrew) | `--config=macos` |
| Windows | Golang, Bazelisk, MSVC compilers | `--config=windows` |

The build system requires Python 3 as the default interpreter and uses Bazel as the primary build tool across all platforms.

**Development Workflow Overview**
```mermaid
graph TB
    subgraph "Development Environment"
        DEV_SETUP["Environment Setup"]
        PREREQ["Prerequisites Installation"]
        CLONE["Repository Clone"]
    end
    
    subgraph "Code Development"
        EDIT["Code Editing"]
        LINT["Code Formatting"]
        BUILD["Bazel Build"]
        TEST["Local Testing"]
    end
    
    subgraph "Quality Assurance"
        PRECOMMIT["pre-commit Hooks"]
        MYPY["Type Checking"]
        CLANG["C++ Formatting"]
        PYTEST["Python Tests"]
    end
    
    subgraph "CI/CD Pipeline"
        GITHUB_CI["GitHub Actions"]
        BUILD_TEST["Build & Test"]
        PACKAGE["Package Creation"]
        DEPLOY["Deployment"]
    end
    
    DEV_SETUP --> PREREQ
    PREREQ --> CLONE
    CLONE --> EDIT
    EDIT --> LINT
    LINT --> BUILD
    BUILD --> TEST
    TEST --> PRECOMMIT
    PRECOMMIT --> MYPY
    PRECOMMIT --> CLANG
    PRECOMMIT --> PYTEST
    MYPY --> GITHUB_CI
    CLANG --> GITHUB_CI
    PYTEST --> GITHUB_CI
    GITHUB_CI --> BUILD_TEST
    BUILD_TEST --> PACKAGE
    PACKAGE --> DEPLOY
```

Sources: [CONTRIBUTING.md:14-41](), [.github/actions/lint/action.yml:1-29]()

### Code Quality Tools

The development environment integrates several code quality tools managed through `pre-commit`:

```mermaid
graph LR
    subgraph "Code Quality Pipeline"
        COMMIT["Git Commit"]
        PRECOMMIT["pre-commit"]
        CLANG_FMT["clang-format"]
        MYPY["mypy Type Checker"]
        LINTERS["Python Linters"]
    end
    
    subgraph "Dependencies"
        WHEEL["wheel"]
        NUMPY["numpy==1.22.4"]
        TORCH["torch==1.13.1"]
        TF["tensorflow==2.13.0"]
        RAY["ray==2.9.1"]
    end
    
    COMMIT --> PRECOMMIT
    PRECOMMIT --> CLANG_FMT
    PRECOMMIT --> MYPY
    PRECOMMIT --> LINTERS
    
    WHEEL --> PRECOMMIT
    NUMPY --> PRECOMMIT
    TORCH --> PRECOMMIT
    TF --> PRECOMMIT
    RAY --> PRECOMMIT
```

Sources: [CONTRIBUTING.md:84-91](), [.github/actions/lint/action.yml:15-28]()

## Build System Architecture

The build system centers around Bazel with platform-specific configurations and targets for both C++ and Python components:

**Build System Components**
```mermaid
graph TB
    subgraph "Build Targets"
        CPP_LIB["//src/cc/lib:*"]
        PYTHON_TESTS["//src/python/deepgnn/...:*"]
        EXAMPLES["//examples/..."]
        DOCS["//docs:*"]
    end
    
    subgraph "Build Configurations"
        OPT_BUILD["-c opt (Optimized)"]
        DBG_BUILD["-c dbg (Debug)"]
        PLATFORM_CFG["Platform Configs"]
    end
    
    subgraph "Platform Targets"
        LINUX_CFG["--config=linux"]
        MACOS_CFG["--config=macos"]  
        WIN_CFG["--config=windows"]
    end
    
    subgraph "Output Artifacts"
        CPP_LIBS["C++ Libraries"]
        PY_WHEELS["Python Wheels"]
        TEST_RESULTS["Test Results"]
    end
    
    CPP_LIB --> OPT_BUILD
    CPP_LIB --> DBG_BUILD
    PYTHON_TESTS --> OPT_BUILD
    EXAMPLES --> OPT_BUILD
    DOCS --> OPT_BUILD
    
    OPT_BUILD --> PLATFORM_CFG
    DBG_BUILD --> PLATFORM_CFG
    
    PLATFORM_CFG --> LINUX_CFG
    PLATFORM_CFG --> MACOS_CFG
    PLATFORM_CFG --> WIN_CFG
    
    LINUX_CFG --> CPP_LIBS
    MACOS_CFG --> CPP_LIBS
    WIN_CFG --> CPP_LIBS
    
    CPP_LIBS --> PY_WHEELS
    PYTHON_TESTS --> TEST_RESULTS
```

Key build commands include:
- Optimized build: `bazel build -c opt //src/cc/lib:* --config=linux`
- Debug build: `bazel build -c dbg //src/cc/lib:* --config=linux`
- Python package: `python setup.py deepgnn-ge bdist_wheel --plat-name manylinux1_x86_64`

Sources: [CONTRIBUTING.md:42-69]()

## Testing Infrastructure

### Test Execution Framework

The testing system operates through Bazel with multiple test categories and timeout configurations:

| Test Category | Command | Timeout | Output |
|---------------|---------|---------|--------|
| C++ Graph Engine | `bazel test //src/cc/tests:*` | 4 seconds | `--test_output=all` |
| Python DeepGNN | `bazel test //src/python/deepgnn/...:*` | 6000 seconds | `--test_output=all` |
| TensorFlow Examples | `bazel run //examples/tensorflow/sage:test_sage` | 6000 seconds | `--test_output=all` |
| PyTorch Examples | `bazel run //examples/pytorch:sage` | 6000 seconds | `--test_output=all` |
| Documentation | `bazel test //docs:*` | 6000 seconds | `--test_output=all` |

**Test Execution Pipeline**
```mermaid
graph LR
    subgraph "Test Categories"
        CPP_TESTS["C++ Tests"]
        PY_TESTS["Python Tests"]
        EXAMPLE_TESTS["Example Tests"]
        DOC_TESTS["Documentation Tests"]
    end
    
    subgraph "Test Execution"
        BAZEL_TEST["bazel test"]
        BAZEL_RUN["bazel run"]
        PYTEST_ARGS["--test_arg parameters"]
    end
    
    subgraph "Test Targets"
        CC_TESTS["//src/cc/tests:*"]
        DEEPGNN_TESTS["//src/python/deepgnn/...:*"]
        TF_SAGE["//examples/tensorflow/sage:test_sage"]
        PT_SAGE["//examples/pytorch:sage"]
        DOCS_TARGET["//docs:*"]
    end
    
    CPP_TESTS --> BAZEL_TEST
    PY_TESTS --> BAZEL_TEST
    EXAMPLE_TESTS --> BAZEL_RUN
    DOC_TESTS --> BAZEL_TEST
    
    BAZEL_TEST --> CC_TESTS
    BAZEL_TEST --> DEEPGNN_TESTS
    BAZEL_RUN --> TF_SAGE
    BAZEL_RUN --> PT_SAGE
    BAZEL_TEST --> DOCS_TARGET
    
    BAZEL_TEST --> PYTEST_ARGS
```

Individual test filtering is supported through pytest arguments: `--test_arg=-k --test_arg='test_sanity_neighbors_index'`

Sources: [CONTRIBUTING.md:94-118]()

## Continuous Integration Workflow

### GitHub Actions Pipeline

The CI/CD system uses GitHub Actions with automated linting, testing, and deployment:

**CI/CD Pipeline Architecture**
```mermaid
graph TB
    subgraph "Source Control"
        FORK["Forked Repository"]
        PR["Pull Request"]
        MAIN["Main Branch"]
    end
    
    subgraph "GitHub Actions"
        LINT_ACTION[".github/actions/lint"]
        CI_WORKFLOW["ci.yml Workflow"]
        BUILD_JOBS["Build Jobs"]
        TEST_JOBS["Test Jobs"]
    end
    
    subgraph "Quality Gates"
        CLANG_FORMAT["clang-format Check"]
        PRECOMMIT_CHECK["pre-commit Validation"]
        MYPY_CHECK["Type Checking"]
        TEST_SUITE["Test Suite Execution"]
    end
    
    subgraph "Deployment"
        PACKAGE_BUILD["Package Building"]
        WHEEL_CREATION["Wheel Creation"]
        ARTIFACT_UPLOAD["Artifact Upload"]
    end
    
    FORK --> PR
    PR --> CI_WORKFLOW
    CI_WORKFLOW --> LINT_ACTION
    LINT_ACTION --> BUILD_JOBS
    BUILD_JOBS --> TEST_JOBS
    
    LINT_ACTION --> CLANG_FORMAT
    LINT_ACTION --> PRECOMMIT_CHECK
    LINT_ACTION --> MYPY_CHECK
    
    TEST_JOBS --> TEST_SUITE
    TEST_SUITE --> PACKAGE_BUILD
    PACKAGE_BUILD --> WHEEL_CREATION
    WHEEL_CREATION --> ARTIFACT_UPLOAD
    
    ARTIFACT_UPLOAD --> MAIN
```

The lint action installs platform-specific dependencies and runs comprehensive code quality checks across all supported platforms.

Sources: [CONTRIBUTING.md:119-131](), [.github/actions/lint/action.yml:1-29]()

## Package Distribution

### Python Package Building

The package distribution system creates platform-specific wheels with manylinux compatibility:

Key distribution commands:
- Set build version: `export BUILD_VERSION=0.1.60`
- Create wheel: `python setup.py deepgnn-ge bdist_wheel --plat-name manylinux1_x86_64 clean --all`
- Install package: `python -m pip install --upgrade --force-reinstall dist/deepgnn_ge-$BUILD_VERSION-py3-none-manylinux1_x86_64.whl`

The packaging system integrates with the C++ library build process and creates distributable wheels for PyPI deployment.

Sources: [CONTRIBUTING.md:61-69]()

## Framework Dependencies

### Machine Learning Framework Integration

The development environment supports multiple ML framework versions with specific compatibility requirements:

| Framework | Version | Additional Components |
|-----------|---------|----------------------|
| PyTorch | 1.13.1 | PyTorch Geometric |
| TensorFlow | 2.13.0 | TensorFlow Addons 0.21.0 |
| Ray | 2.9.1 | Distributed Training |
| Horovod | 0.28.1 | TensorFlow Backend (Linux/macOS only) |

**Framework Dependency Graph**
```mermaid
graph TB
    subgraph "Core ML Frameworks"
        TORCH["torch==1.13.1"]
        TF["tensorflow==2.13.0"]
        RAY["ray==2.9.1"]
    end
    
    subgraph "Framework Extensions"
        TF_ADDONS["tensorflow-addons==0.21.0"]
        HOROVOD["horovod[tensorflow]==0.28.1"]
        PYG["PyTorch Geometric"]
    end
    
    subgraph "Platform Constraints"
        LINUX_ONLY["sys_platform != 'win32'"]
        WIN_COMPAT["Windows Compatible"]
    end
    
    subgraph "Development Tools"
        MYPY["mypy==0.971"]
        NUMPY["numpy==1.22.4"]
        PRECOMMIT["pre-commit==2.17.0"]
    end
    
    TF --> TF_ADDONS
    TF --> HOROVOD
    TORCH --> PYG
    RAY --> TORCH
    RAY --> TF
    
    HOROVOD --> LINUX_ONLY
    TF_ADDONS --> WIN_COMPAT
    
    TORCH --> NUMPY
    TF --> NUMPY
    MYPY --> NUMPY
```

Platform-specific dependency management ensures compatibility across Linux, macOS, and Windows development environments.

Sources: [examples/tensorflow/requirements.txt:1-6](), [.github/actions/lint/action.yml:15-22](), [docs/torch/distrib.rst:248-254]()

---

