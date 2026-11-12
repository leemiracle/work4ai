<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/maro · page 7 Development and Deployment · fetched 2026-10-26 -->

# Development and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/build_wheel.yml](.github/workflows/build_wheel.yml)
- [.github/workflows/deploy_docker_image.yml](.github/workflows/deploy_docker_image.yml)
- [.github/workflows/deploy_gh_pages.yml](.github/workflows/deploy_gh_pages.yml)
- [.github/workflows/test.yml](.github/workflows/test.yml)
- [.github/workflows/vulnerability_scan.yml](.github/workflows/vulnerability_scan.yml)
- [maro/cli/maro_real_time_vis/back_end/vis_app/requirements.txt](maro/cli/maro_real_time_vis/back_end/vis_app/requirements.txt)
- [maro/requirements.build.txt](maro/requirements.build.txt)
- [notebooks/requirements.nb.txt](notebooks/requirements.nb.txt)
- [pyproject.toml](pyproject.toml)
- [requirements.dev.txt](requirements.dev.txt)
- [scripts/compile_cython.bat](scripts/compile_cython.bat)
- [scripts/compile_cython.sh](scripts/compile_cython.sh)
- [tests/requirements.test.txt](tests/requirements.test.txt)

</details>



This page provides a comprehensive guide for developers working on the MARO platform and deploying MARO-based applications. It covers development environment setup, the build system, CI/CD pipelines, testing practices, and deployment processes. For specific environment configuration details, see [Environment Setup](#7.1). For CI/CD pipeline specifics, see [CI/CD Pipeline](#7.2). For code quality standards, see [Code Quality and Testing](#7.3).

## Overview

MARO's development and deployment infrastructure is built around a multi-stage pipeline that handles cross-platform compilation, testing, and distribution. The system supports Python 3.7-3.9 across Linux, Windows, and macOS platforms, with specialized handling for Cython-based high-performance components.

## Development Environment Architecture

### Dependency Management

MARO uses a hierarchical dependency structure with specialized requirements files for different use cases:

| Requirements File | Purpose | Key Dependencies |
|------------------|---------|------------------|
| `maro/requirements.build.txt` | Core build dependencies | Cython, NumPy, PyJWT |
| `requirements.dev.txt` | Full development environment | Azure SDK, Flask, Kubernetes client, Testing tools |
| `tests/requirements.test.txt` | Testing-specific dependencies | pytest, coverage, Redis |
| `notebooks/requirements.nb.txt` | Jupyter notebook environment | IPython, JupyterLab, visualization tools |

```mermaid
graph TB
    subgraph "Development Dependencies"
        BUILD["maro/requirements.build.txt<br/>Cython==0.29.14<br/>numpy>=1.19.0<br/>PyJWT>=2.4.0"]
        DEV["requirements.dev.txt<br/>Azure SDK<br/>Kubernetes client<br/>Flask ecosystem<br/>Testing tools"]
        TEST["tests/requirements.test.txt<br/>pytest>=7.1.2<br/>coverage>=6.4.1<br/>Redis client"]
        NB["notebooks/requirements.nb.txt<br/>JupyterLab<br/>Visualization tools"]
    end
    
    subgraph "Build Process"
        CYTHON["Cython Compilation<br/>backend.pyx<br/>np_backend.pyx<br/>raw_backend.pyx<br/>frame.pyx"]
        SETUP["setup.py<br/>Build Configuration"]
        WHEEL["Wheel Generation<br/>Cross-platform"]
    end
    
    BUILD --> CYTHON
    DEV --> CYTHON
    CYTHON --> SETUP
    SETUP --> WHEEL
    
    TEST --> WHEEL
```

**Sources:** [maro/requirements.build.txt:1-7](), [requirements.dev.txt:1-59](), [tests/requirements.test.txt:1-18](), [notebooks/requirements.nb.txt:1-18]()

### Cython Compilation System

The core performance components in MARO are implemented in Cython and require compilation before use. The compilation process is standardized across platforms:

```mermaid
graph LR
    subgraph "Cython Sources"
        BACKEND["backend.pyx<br/>Core Backend Interface"]
        NP_BACKEND["np_backend.pyx<br/>NumPy Backend"]
        RAW_BACKEND["raw_backend.pyx<br/>Raw C++ Backend"]
        FRAME["frame.pyx<br/>Frame Management"]
    end
    
    subgraph "Compilation Scripts"
        UNIX["scripts/compile_cython.sh<br/>Unix/Linux/macOS"]
        WIN["scripts/compile_cython.bat<br/>Windows"]
    end
    
    subgraph "Compilation Process"
        CYTHON_CMD["cython --cplus -3<br/>-E NODES_MEMORY_LAYOUT=ONE_BLOCK<br/>-X embedsignature=True"]
        CPP_FILES["Generated C++ Files<br/>backend.cpp<br/>np_backend.cpp<br/>raw_backend.cpp<br/>frame.cpp"]
    end
    
    BACKEND --> CYTHON_CMD
    NP_BACKEND --> CYTHON_CMD
    RAW_BACKEND --> CYTHON_CMD
    FRAME --> CYTHON_CMD
    
    UNIX --> CYTHON_CMD
    WIN --> CYTHON_CMD
    
    CYTHON_CMD --> CPP_FILES
```

**Sources:** [scripts/compile_cython.sh:16-18](), [scripts/compile_cython.bat:14-16](), [.github/workflows/test.yml:30-32]()

## CI/CD Pipeline Architecture

### GitHub Actions Workflow System

MARO employs a comprehensive CI/CD system using GitHub Actions with specialized workflows for different aspects of development and deployment:

```mermaid
graph TB
    subgraph "Trigger Events"
        PUSH["Push to master/branches"]
        PR["Pull Requests"]
        TAG["Version Tags<br/>maro-X.Y.Z"]
        MANUAL["workflow_dispatch"]
    end
    
    subgraph "Core Workflows"
        TEST[".github/workflows/test.yml<br/>Cross-platform Testing<br/>Python 3.7-3.9<br/>Ubuntu/Windows/macOS"]
        BUILD[".github/workflows/build_wheel.yml<br/>PyPI Wheel Building<br/>Manylinux Support"]
        DOCKER[".github/workflows/deploy_docker_image.yml<br/>Docker Image Publishing"]
        DOCS[".github/workflows/deploy_gh_pages.yml<br/>Documentation Deployment"]
        VULN[".github/workflows/vulnerability_scan.yml<br/>Security Scanning"]
    end
    
    subgraph "Deployment Targets"
        PYPI["PyPI Package Registry"]
        DOCKERHUB["Docker Hub Registry"]
        GHPAGES["GitHub Pages Documentation"]
        CODECOV["Codecov Coverage Reports"]
    end
    
    PUSH --> TEST
    PR --> TEST
    PR --> VULN
    TAG --> BUILD
    TAG --> DOCKER
    MANUAL --> DOCS
    
    TEST --> CODECOV
    BUILD --> PYPI
    DOCKER --> DOCKERHUB
    DOCS --> GHPAGES
```

**Sources:** [.github/workflows/test.yml:1-82](), [.github/workflows/build_wheel.yml:1-82](), [.github/workflows/deploy_docker_image.yml:1-42](), [.github/workflows/deploy_gh_pages.yml:1-68]()

### Cross-Platform Build Matrix

The testing and build system supports multiple platform and Python version combinations:

| Platform | Python Versions | Special Considerations |
|----------|----------------|----------------------|
| `ubuntu-18.04` / `ubuntu-latest` | 3.7, 3.8, 3.9 | Manylinux wheel building, CodeCov reporting |
| `windows-latest` | 3.7, 3.8, 3.9 | PyTorch installation, PYTHONPATH handling |
| `macos-latest` | 3.7, 3.8, 3.9 | Standard wheel building |

```mermaid
graph TB
    subgraph "Build Matrix Strategy"
        STRATEGY["strategy.matrix<br/>os: [ubuntu-18.04, windows-latest, macos-latest]<br/>python-version: [3.7, 3.8, 3.9]"]
    end
    
    subgraph "Platform-Specific Steps"
        LINUX["Linux Steps<br/>Manylinux wheel building<br/>RalfG/python-wheels-manylinux-build@v0.3.1<br/>CodeCov upload"]
        WINDOWS["Windows Steps<br/>PyTorch installation<br/>PYTHONPATH: .;./tests<br/>Standard wheel building"]
        MACOS["macOS Steps<br/>Standard wheel building<br/>PYTHONPATH: .:./tests"]
    end
    
    subgraph "Common Steps"
        CHECKOUT["actions/checkout@v2"]
        PYTHON_SETUP["actions/setup-python@v2"]
        DEPS["Install dependencies<br/>requirements.build.txt"]
        CYTHON_COMPILE["Cython compilation"]
        BUILD_INPLACE["python setup.py build_ext -i"]
    end
    
    STRATEGY --> LINUX
    STRATEGY --> WINDOWS
    STRATEGY --> MACOS
    
    CHECKOUT --> PYTHON_SETUP
    PYTHON_SETUP --> DEPS
    DEPS --> CYTHON_COMPILE
    CYTHON_COMPILE --> BUILD_INPLACE
```

**Sources:** [.github/workflows/test.yml:12-17](), [.github/workflows/build_wheel.yml:12-17](), [.github/workflows/test.yml:38-42](), [.github/workflows/build_wheel.yml:49-60]()

## Testing and Quality Assurance

### Testing Pipeline

The testing system includes code quality checks, unit testing, and coverage reporting:

```mermaid
graph LR
    subgraph "Code Quality"
        FLAKE8["flake8 Linting<br/>Syntax errors: E9,F63,F7,F82<br/>Complexity check: max 10"]
        FORMAT["Code Formatting<br/>black==22.3.0<br/>editorconfig-checker"]
    end
    
    subgraph "Testing Execution"
        COVERAGE["coverage run<br/>--rcfile=./tests/.coveragerc"]
        PYTEST["Test Discovery<br/>PYTHONPATH configuration"]
        REPORT["coverage report/xml<br/>Platform-specific output"]
    end
    
    subgraph "External Services"
        CODECOV["Codecov Upload<br/>Linux only<br/>codecov/codecov-action@v1"]
        SECURITY["CodeQL Analysis<br/>Vulnerability scanning"]
    end
    
    FLAKE8 --> COVERAGE
    FORMAT --> COVERAGE
    COVERAGE --> PYTEST
    PYTEST --> REPORT
    REPORT --> CODECOV
    SECURITY --> CODECOV
```

**Sources:** [.github/workflows/test.yml:49-54](), [.github/workflows/test.yml:61-81](), [requirements.dev.txt:9](), [requirements.dev.txt:15-16]()

### Coverage Configuration

Testing uses a centralized coverage configuration in `.coveragerc` with platform-specific PYTHONPATH settings:

- **Windows**: `PYTHONPATH: .;./tests`
- **Linux/macOS**: `PYTHONPATH: .:./tests`

**Sources:** [.github/workflows/test.yml:58-70]()

## Deployment Processes

### PyPI Package Distribution

The wheel building process creates cross-platform distributions with special handling for Linux manylinux wheels:

```mermaid
graph TB
    subgraph "Wheel Building Process"
        TAG_TRIGGER["Version Tag<br/>maro-[0-9]+\\.[0-9]+\\.*"]
        
        subgraph "Platform Builds"
            WIN_MAC["Windows/macOS<br/>python setup.py bdist_wheel"]
            LINUX["Linux Manylinux<br/>RalfG/python-wheels-manylinux-build<br/>cp37-cp37m cp38-cp38 cp39-cp39"]
            SOURCE["Source Distribution<br/>python setup.py sdist<br/>Windows Python 3.7 only"]
        end
        
        subgraph "Publication"
            ARTIFACT["GitHub Artifacts<br/>local-wheels"]
            TWINE["Twine Upload<br/>TWINE_USERNAME: __token__<br/>TWINE_PASSWORD: PyPI token"]
        end
    end
    
    TAG_TRIGGER --> WIN_MAC
    TAG_TRIGGER --> LINUX
    TAG_TRIGGER --> SOURCE
    
    WIN_MAC --> ARTIFACT
    LINUX --> ARTIFACT
    SOURCE --> ARTIFACT
    
    ARTIFACT --> TWINE
```

**Sources:** [.github/workflows/build_wheel.yml:5-7](), [.github/workflows/build_wheel.yml:39-47](), [.github/workflows/build_wheel.yml:49-66](), [.github/workflows/build_wheel.yml:75-81]()

### Docker Image Publishing

Docker images are built and published for tagged releases with version-specific tagging:

```mermaid
graph LR
    subgraph "Docker Build Process"
        VERSION_EXTRACT["Version Extraction<br/>grep __version__ maro/__misc__.py<br/>egrep -o [0-9].[0-9].[0-9,a-z]+"]
        
        subgraph "Image Building"
            DOCKERFILE["docker_files/cpu.playground.df<br/>CPU playground image"]
            TAGS["Image Tags<br/>maro:cpu<br/>maro:latest<br/>maro:cpu-$version"]
        end
        
        subgraph "Publication"
            LOGIN["Docker Hub Login<br/>DOCKER_HUB_USERNAME<br/>DOCKER_HUB_PASSWORD"]
            PUSH["docker push<br/>All tagged variants"]
        end
    end
    
    VERSION_EXTRACT --> DOCKERFILE
    DOCKERFILE --> TAGS
    TAGS --> LOGIN
    LOGIN --> PUSH
```

**Sources:** [.github/workflows/deploy_docker_image.yml:29-34](), [.github/workflows/deploy_docker_image.yml:35-41]()

### Documentation Deployment

Documentation is built using Sphinx and deployed to GitHub Pages:

```mermaid
graph LR
    subgraph "Documentation Build"
        SPHINX_DEPS["Sphinx Dependencies<br/>docs/requirements.docs.txt"]
        APIDOC["sphinx-apidoc -f -o ./source/apidoc ../maro/"]
        MAKE_HTML["make html<br/>PYTHONPATH: ."]
    end
    
    subgraph "Deployment"
        PAGES_ACTION["JamesIves/github-pages-deploy-action@3.6.1<br/>BRANCH: gh-pages<br/>FOLDER: docs/_build/html/"]
    end
    
    SPHINX_DEPS --> APIDOC
    APIDOC --> MAKE_HTML
    MAKE_HTML --> PAGES_ACTION
```

**Sources:** [.github/workflows/deploy_gh_pages.yml:24-47](), [.github/workflows/deploy_gh_pages.yml:49-55]()

## Build System Configuration

### Core Build Components

The build system is configured through several key files that define dependencies and build behavior:

| File | Purpose | Key Configuration |
|------|---------|------------------|
| `pyproject.toml` | Modern Python build configuration | Build system requirements, NumPy version constraints |
| `setup.py` | Legacy build configuration | Extension compilation, package metadata |
| Cython compilation scripts | Platform-specific compilation | Compiler flags, memory layout options |

**Sources:** [pyproject.toml:1-3]()

The build process consistently uses the `NODES_MEMORY_LAYOUT=ONE_BLOCK` configuration for optimal memory performance in the C++ backends, and enables embedsignature for better debugging support.

**Sources:** [.github/workflows/build_wheel.yml:37](), [.github/workflows/test.yml:32](), [scripts/compile_cython.sh:18]()

---

