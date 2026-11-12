<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuEquivariance · page 6 Development · fetched 2026-10-26 -->

# Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/tests.yml](.github/workflows/tests.yml)
- [cuequivariance/pyproject.toml](cuequivariance/pyproject.toml)
- [cuequivariance_jax/pyproject.toml](cuequivariance_jax/pyproject.toml)
- [cuequivariance_torch/pyproject.toml](cuequivariance_torch/pyproject.toml)

</details>



This document covers the development workflows, testing infrastructure, and contribution guidelines for the cuEquivariance library. It provides an overview of the multi-package repository structure, continuous integration pipelines, and development best practices.

For detailed information about specific development processes, see:
- Testing infrastructure and CI/CD pipelines: [Testing](#6.1)
- Documentation build process: [Documentation](#6.2)  
- Package publishing and release workflow: [Release Process](#6.3)

## Repository Architecture

The cuEquivariance library is organized as a multi-package repository with distinct components for core functionality and framework-specific implementations.

### Package Structure

```mermaid
graph TD
    subgraph "Repository Root"
        ROOT["."]
        
        subgraph "Core Package"
            CORE_DIR["cuequivariance/"]
            CORE_PROJ["cuequivariance/pyproject.toml"]
            CORE_VER["cuequivariance/VERSION"]
        end
        
        subgraph "JAX Integration"
            JAX_DIR["cuequivariance_jax/"]
            JAX_PROJ["cuequivariance_jax/pyproject.toml"]
            JAX_VER["cuequivariance_jax/VERSION"]
        end
        
        subgraph "PyTorch Integration"
            TORCH_DIR["cuequivariance_torch/"]
            TORCH_PROJ["cuequivariance_torch/pyproject.toml"]
            TORCH_VER["cuequivariance_torch/VERSION"]
        end
        
        subgraph "CI/CD Infrastructure"
            WORKFLOWS[".github/workflows/"]
            TESTS_YML[".github/workflows/tests.yml"]
        end
    end
    
    ROOT --> CORE_DIR
    ROOT --> JAX_DIR
    ROOT --> TORCH_DIR
    ROOT --> WORKFLOWS
    
    CORE_DIR --> CORE_PROJ
    CORE_DIR --> CORE_VER
    JAX_DIR --> JAX_PROJ
    JAX_DIR --> JAX_VER
    TORCH_DIR --> TORCH_PROJ
    TORCH_DIR --> TORCH_VER
    WORKFLOWS --> TESTS_YML
```

Sources: [cuequivariance/pyproject.toml](), [cuequivariance_jax/pyproject.toml](), [cuequivariance_torch/pyproject.toml](), [.github/workflows/tests.yml]()

### Build System Configuration

Each package uses `hatchling` as the build backend and follows a consistent structure:

| Package | Name | Dependencies | Python Support |
|---------|------|--------------|----------------|
| `cuequivariance` | Core mathematical library | `numpy`, `scipy`, `opt_einsum`, `sympy`, `networkx` | 3.10+ |
| `cuequivariance-jax` | JAX integration | `cuequivariance`, `jax`, `packaging` | 3.10+ |
| `cuequivariance-torch` | PyTorch integration | `cuequivariance` | 3.10+ |

The build configuration is defined in [cuequivariance/pyproject.toml:16-18](), [cuequivariance_jax/pyproject.toml:16-18](), and [cuequivariance_torch/pyproject.toml:16-18]().

Sources: [cuequivariance/pyproject.toml:20-41](), [cuequivariance_jax/pyproject.toml:20-39](), [cuequivariance_torch/pyproject.toml:20-37]()

## Continuous Integration Pipeline

The CI system runs comprehensive tests across multiple Python versions and execution environments using GitHub Actions.

### CI Workflow Structure

```mermaid
graph TD
    subgraph "GitHub Actions Triggers"
        PUSH["push: main, release"]
        PR["pull_request: main, release"]
    end
    
    subgraph "Test Jobs"
        JOB_CORE["cuequivariance"]
        JOB_JAX["cuequivariance-jax"]
        JOB_TORCH["cuequivariance-torch"]
    end
    
    subgraph "Test Matrix"
        UBUNTU["ubuntu-latest"]
        SELF_HOSTED["self-hosted"]
        PY310["Python 3.10"]
        PY312["Python 3.12"]
    end
    
    subgraph "Test Execution"
        INSTALL["Install Dependencies"]
        PYTEST["pytest --doctest-modules -x -m \"not slow\""]
        NUMPY_COMPAT["Test numpy 1.26 compatibility"]
    end
    
    PUSH --> JOB_CORE
    PUSH --> JOB_JAX
    PUSH --> JOB_TORCH
    PR --> JOB_CORE
    PR --> JOB_JAX
    PR --> JOB_TORCH
    
    JOB_CORE --> UBUNTU
    JOB_CORE --> PY310
    JOB_CORE --> PY312
    
    JOB_JAX --> UBUNTU
    JOB_JAX --> SELF_HOSTED
    JOB_TORCH --> UBUNTU
    JOB_TORCH --> SELF_HOSTED
    
    JOB_CORE --> INSTALL
    JOB_JAX --> INSTALL
    JOB_TORCH --> INSTALL
    
    INSTALL --> PYTEST
    PYTEST --> NUMPY_COMPAT
```

Sources: [.github/workflows/tests.yml:1-8](), [.github/workflows/tests.yml:10-17]()

### Package-Specific Testing

#### Core Package Testing
The `cuequivariance` job tests the core mathematical library on Ubuntu with Python 3.10 and 3.12:

```bash
# Install process from CI
python -m uv pip install -e ./cuequivariance 
pytest --doctest-modules -x -m "not slow" cuequivariance
```

The workflow also includes compatibility testing with older numpy versions [.github/workflows/tests.yml:34-39]().

Sources: [.github/workflows/tests.yml:11-40]()

#### JAX Package Testing  
The `cuequivariance-jax` job includes CUDA dependencies and GPU testing capabilities:

```bash
# JAX-specific dependencies
python -m uv pip install -U pytest "jax[cuda12]"
python -m uv pip install nvidia-cusolver-cu12==11.7.3.90
python -m uv pip install jax-triton triton==3.3.1
```

Testing runs with memory preallocation disabled: `XLA_PYTHON_CLIENT_PREALLOCATE=false`.

Sources: [.github/workflows/tests.yml:43-76]()

#### PyTorch Package Testing
The `cuequivariance-torch` job installs PyTorch and e3nn dependencies:

```bash
# PyTorch-specific dependencies  
python -m uv pip install -U pytest torch e3nn
```

Sources: [.github/workflows/tests.yml:77-108]()

## Development Environment Setup

### Local Development Installation

For local development, install packages in editable mode:

```bash
# Install core package
python -m pip install -e ./cuequivariance

# Install framework packages  
python -m pip install -e ./cuequivariance_jax
python -m pip install -e ./cuequivariance_torch
```

### Test Configuration

All packages use pytest with consistent configuration defined in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
]
```

The `slow` marker allows excluding computationally expensive tests during development.

Sources: [cuequivariance/pyproject.toml:49-52](), [cuequivariance_jax/pyproject.toml:49-52](), [cuequivariance_torch/pyproject.toml:47-50]()

## Version Management

### Version Synchronization

```mermaid
graph LR
    subgraph "Version Files"
        CORE_V["cuequivariance/VERSION"]
        JAX_V["cuequivariance_jax/VERSION"]  
        TORCH_V["cuequivariance_torch/VERSION"]
    end
    
    subgraph "Package Metadata"
        CORE_META["cuequivariance package"]
        JAX_META["cuequivariance-jax package"]
        TORCH_META["cuequivariance-torch package"]
    end
    
    CORE_V --> CORE_META
    JAX_V --> JAX_META
    TORCH_V --> TORCH_META
    
    CORE_META -.-> JAX_META
    CORE_META -.-> TORCH_META
```

Each package maintains its version in a dedicated `VERSION` file, referenced by the hatch build system via the pattern `(?P<version>\\d+\\.\\d+\\.\\d+(?:[a-z]+\\d+)?)`.

Sources: [cuequivariance/pyproject.toml:43-44](), [cuequivariance_jax/pyproject.toml:41-43](), [cuequivariance_torch/pyproject.toml:39-41]()

## Development Best Practices

### Code Quality Standards
- All tests must pass before merging
- Doctests are executed as part of the test suite
- Both framework packages depend on the core package for consistency
- Python 3.10+ compatibility is maintained across all packages

### Testing Strategy
- Fast tests run on every push/PR
- Slow tests are marked and can be excluded during development
- GPU tests run on self-hosted runners for JAX and PyTorch packages
- Compatibility testing includes multiple numpy versions

### Dependency Management
The dependency chain ensures proper separation of concerns:
- Core package contains mathematical primitives
- Framework packages add integration layers
- Optional CUDA packages provide performance optimizations

Sources: [.github/workflows/tests.yml](), [cuequivariance/pyproject.toml](), [cuequivariance_jax/pyproject.toml](), [cuequivariance_torch/pyproject.toml]()

---

