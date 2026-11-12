<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/SPECTER2 · page 5 Development · fetched 2026-10-26 -->

# Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [pyproject.toml](pyproject.toml)
- [specter2_0/__init__.py](specter2_0/__init__.py)
- [specter2_0/model.py](specter2_0/model.py)
- [specter2_0/timo/__init__.py](specter2_0/timo/__init__.py)

</details>



This page provides comprehensive information for developers working with the SPECTER2 codebase, including environment setup, code organization, development workflows, and contribution guidelines. This covers the technical aspects of maintaining and extending the SPECTER2 system.

For information about using the models, see [Model Usage](#2). For production API details, see [Production API](#3). For installation instructions for end users, see [Installation](#4).

## Development Environment Setup

The SPECTER2 project follows standard Python packaging conventions with a modular structure supporting both local development and production deployment.

### Environment Configuration

The development environment is configured through standard Python tooling:

| Component | Configuration File | Purpose |
|-----------|-------------------|---------|
| Build System | `pyproject.toml` | Defines build backend and requirements |
| Package Structure | `specter2_0/` | Main package directory |
| Dependency Management | `setup.py` | Runtime and development dependencies |
| Version Control | `.gitignore` | Excludes build artifacts and temporary files |

### Development Setup Flow

```mermaid
flowchart TD
    START["Developer Environment Setup"] --> CLONE["git clone repository"]
    CLONE --> VENV["python -m venv venv"]
    VENV --> ACTIVATE["source venv/bin/activate"]
    ACTIVATE --> INSTALL["pip install -e ."]
    
    INSTALL --> DEV_DEPS["Install development dependencies"]
    DEV_DEPS --> TORCH["torch 1.13.1 + CUDA 11.6"]
    DEV_DEPS --> TRANSFORMERS["transformers 4.21.1"]
    DEV_DEPS --> ADAPTERS["adapter-transformers 3.0.1"]
    
    TORCH --> TEST_ENV["Run test suite"]
    TRANSFORMERS --> TEST_ENV
    ADAPTERS --> TEST_ENV
    
    TEST_ENV --> READY["Development environment ready"]
    
    subgraph "Optional Components"
        DOCKER["Docker for TIMO testing"]
        CUDA_DEV["CUDA development tools"]
        HF_CLI["huggingface-hub CLI"]
    end
    
    READY -.-> DOCKER
    READY -.-> CUDA_DEV
    READY -.-> HF_CLI
```

**Sources:** [pyproject.toml:1-4](), [.gitignore:111-118]()

## Code Organization

The codebase follows a hierarchical module structure that separates core functionality, production services, and development utilities.

### Package Structure

```mermaid
graph TB
    ROOT["specter2_0/"] --> INIT["__init__.py"]
    ROOT --> MODEL["model.py"]
    ROOT --> TIMO_DIR["timo/"]
    
    TIMO_DIR --> TIMO_INIT["__init__.py"]
    
    subgraph "Core Components"
        MODEL --> PLACEHOLDER["Model implementation placeholder"]
    end
    
    subgraph "Production Service"
        TIMO_INIT --> PREDICTOR_CLASS["Predictor class implementation"]
        TIMO_INIT --> API_HANDLERS["HTTP API handlers"]
    end
    
    subgraph "Build System"
        BUILD["pyproject.toml"] --> SETUPTOOLS["setuptools backend"]
        BUILD --> WHEEL["wheel building"]
    end
    
    subgraph "Version Control"
        GITIGNORE[".gitignore"] --> PYTHON_ARTIFACTS["Python build artifacts"]
        GITIGNORE --> DEV_TOOLS["IDE and tool configurations"]
        GITIGNORE --> ENV_FILES["Environment and cache files"]
    end
```

**Sources:** [specter2_0/__init__.py:1](), [specter2_0/model.py:1-4](), [specter2_0/timo/__init__.py:1]()

### Module Responsibilities

| Module Path | Primary Responsibility | Development Notes |
|-------------|----------------------|-------------------|
| `specter2_0/` | Main package namespace | Contains core model implementations |
| `specter2_0/model.py` | Model interface definitions | Currently contains placeholder for implementation |
| `specter2_0/timo/` | Production service components | TIMO API predictor and handlers |

## Development Workflow

The development process integrates model training, package building, and production deployment through a structured pipeline.

### Development Lifecycle

```mermaid
sequenceDiagram
    participant DEV as "Developer"
    participant LOCAL as "Local Environment"
    participant BUILD as "Build System"
    participant TEST as "Test Suite"
    participant DIST as "Distribution"
    participant PROD as "Production"
    
    DEV->>LOCAL: "Code changes"
    LOCAL->>BUILD: "python setup.py build"
    BUILD->>TEST: "Run integration tests"
    
    alt Tests Pass
        TEST->>DIST: "Create distribution package"
        DIST->>BUILD: "setuptools + wheel backend"
        BUILD->>DIST: "specter2_0.tar.gz"
        DIST->>PROD: "Deploy to TIMO service"
    else Tests Fail
        TEST->>DEV: "Test failure feedback"
        DEV->>LOCAL: "Fix issues"
    end
    
    PROD->>DEV: "Production metrics & feedback"
```

**Sources:** [pyproject.toml:2-3](), [specter2_0/model.py:2-3]()

## Build and Distribution Process

The project uses modern Python packaging standards with setuptools and wheel for distribution.

### Build Configuration

The build system is configured through `pyproject.toml` using the setuptools backend:

```mermaid
flowchart LR
    SOURCE["Source Code"] --> PYPROJECT["pyproject.toml"]
    PYPROJECT --> SETUPTOOLS["setuptools backend"]
    SETUPTOOLS --> WHEEL["wheel package"]
    
    subgraph "Build Artifacts"
        WHEEL --> DIST_PKG["specter2_0.tar.gz"]
        WHEEL --> WHEEL_FILE["specter2_0.whl"]
    end
    
    subgraph "Distribution Channels"
        DIST_PKG --> S3_DIST["AWS S3 distribution"]
        DIST_PKG --> LOCAL_INSTALL["Local pip install"]
    end
    
    subgraph "Ignored by Git"
        BUILD_DIR["build/"]
        DIST_DIR["dist/"]
        EGG_INFO["*.egg-info/"]
    end
    
    SETUPTOOLS -.-> BUILD_DIR
    SETUPTOOLS -.-> DIST_DIR
    SETUPTOOLS -.-> EGG_INFO
```

**Sources:** [pyproject.toml:1-4](), [.gitignore:15-31]()

### Artifact Management

The `.gitignore` configuration excludes standard Python build artifacts and development files:

| Category | Excluded Files | Purpose |
|----------|----------------|---------|
| Build Artifacts | `build/`, `dist/`, `*.egg-info/` | Generated during package building |
| Python Runtime | `__pycache__/`, `*.py[cod]` | Bytecode and compiled files |
| Development Tools | `.idea/`, `.pytest_cache/` | IDE and testing tool files |
| Virtual Environments | `venv/`, `.env` | Local development environments |

**Sources:** [.gitignore:5-8](), [.gitignore:13-31](), [.gitignore:111-118]()

## Testing and Validation

The development workflow incorporates testing at multiple levels to ensure code quality and production readiness.

### Test Infrastructure

```mermaid
graph TD
    subgraph "Test Categories"
        UNIT["Unit Tests"] --> LOCAL_MODELS["Model component tests"]
        INTEGRATION["Integration Tests"] --> TIMO_TESTS["TIMO service tests"]
        E2E["End-to-End Tests"] --> API_TESTS["HTTP API validation"]
    end
    
    subgraph "Test Execution"
        PYTEST["pytest framework"] --> TEST_DISCOVERY["Automatic test discovery"]
        TEST_DISCOVERY --> TEST_RESULTS["Test results and coverage"]
    end
    
    subgraph "Continuous Integration"
        GIT_HOOKS["Pre-commit hooks"] --> LINTING["Code quality checks"]
        BUILD_TESTS["Build validation"] --> PACKAGE_TESTS["Package installation tests"]
    end
    
    LOCAL_MODELS --> PYTEST
    TIMO_TESTS --> PYTEST
    API_TESTS --> PYTEST
    
    TEST_RESULTS --> GIT_HOOKS
    PACKAGE_TESTS --> BUILD_TESTS
```

**Sources:** [.gitignore:44-56]()

## Development Tools Integration

The project integrates with standard Python development tools and IDE configurations.

### Tool Configuration

```mermaid
flowchart TB
    subgraph "Development Tools"
        IDE["IDEs (.idea)"] --> PYCHARM["PyCharm configuration"]
        LINTING["Code Quality"] --> MYPY[".mypy_cache/"]
        LINTING --> PYTEST[".pytest_cache/"]
        
        JUPYTER["Jupyter Notebooks"] --> CHECKPOINTS[".ipynb_checkpoints"]
        
        VENV_TOOLS["Environment Management"] --> VENV_DIRS["venv/, .venv"]
        VENV_TOOLS --> PYTHON_VER[".python-version"]
    end
    
    subgraph "Excluded from Version Control"
        BUILD_CACHE["Build caches and temp files"]
        USER_CONFIGS["User-specific configurations"]
        RUNTIME_DATA["Runtime generated data"]
    end
    
    IDE -.-> BUILD_CACHE
    LINTING -.-> BUILD_CACHE
    JUPYTER -.-> RUNTIME_DATA
    VENV_TOOLS -.-> USER_CONFIGS
```

**Sources:** [.gitignore:1-143]()

---

