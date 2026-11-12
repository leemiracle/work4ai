<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/bsuite · page 7 Development and Testing · fetched 2026-10-26 -->

# Development and Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [test.sh](test.sh)

</details>



This section provides guidance for developers contributing to the bsuite codebase, including development environment setup, testing procedures, and development workflows. It covers the infrastructure and processes needed to maintain code quality and ensure reproducible research results.

For information about running experiments and analysis, see [Experiment Management](#5) and [Data and Analysis](#6). For details about the testing framework implementation, see [Testing Framework](#7.1). For comprehensive development setup instructions, see [Development Setup](#7.2).

## Development Workflow Overview

The bsuite development process follows a systematic approach that ensures code quality through automated testing, type checking, and dependency management. The primary development workflow is encapsulated in the automated testing pipeline.

```mermaid
graph TB
    subgraph "Development Environment Setup"
        VENV["python3 -m venv bsuite_testing"]
        ACTIVATE["source bsuite_testing/bin/activate"]
        UPGRADE["pip install --upgrade pip setuptools"]
    end
    
    subgraph "Dependency Installation"
        BASE_INSTALL["pip install ."]
        JAX_INSTALL["pip install .[baselines_jax]"]
        TF_INSTALL["pip install .[baselines]"]
        TEST_INSTALL["pip install .[testing]"]
    end
    
    subgraph "Quality Assurance"
        TYPE_CHECK["pytype -j N_CPU bsuite"]
        RUN_TESTS["pytest -n N_CPU bsuite"]
        PARALLEL["N_CPU = grep -c ^processor /proc/cpuinfo"]
    end
    
    subgraph "Cleanup"
        DEACTIVATE["deactivate"]
        CLEANUP["rm -rf bsuite_testing/"]
    end
    
    VENV --> ACTIVATE
    ACTIVATE --> UPGRADE
    UPGRADE --> BASE_INSTALL
    BASE_INSTALL --> JAX_INSTALL
    JAX_INSTALL --> TF_INSTALL
    TF_INSTALL --> TEST_INSTALL
    TEST_INSTALL --> PARALLEL
    PARALLEL --> TYPE_CHECK
    TYPE_CHECK --> RUN_TESTS
    RUN_TESTS --> DEACTIVATE
    DEACTIVATE --> CLEANUP
```

**Development Workflow Process**
Sources: [test.sh:1-32]()

## Testing Infrastructure

The bsuite testing infrastructure is designed to ensure code quality across multiple dimensions including type safety, functionality, and integration across different ML frameworks.

```mermaid
graph LR
    subgraph "Testing Tools"
        PYTYPE["pytype<br/>Static Type Checker"]
        PYTEST["pytest<br/>Test Runner"]
        CPU_PARALLEL["Parallel Execution<br/>-j N_CPU / -n N_CPU"]
    end
    
    subgraph "Test Dependencies"
        TESTING_EXTRA["[testing]<br/>Extra Dependencies"]
        BASE_DEPS["Base Package<br/>Core Dependencies"]
        JAX_DEPS["[baselines_jax]<br/>JAX Framework"]
        TF_DEPS["[baselines]<br/>TensorFlow Framework"]
    end
    
    subgraph "Test Execution"
        TYPE_ANALYSIS["Static Analysis<br/>Type checking all modules"]
        UNIT_TESTS["Unit Tests<br/>Individual component testing"]
        INTEGRATION_TESTS["Integration Tests<br/>Cross-component functionality"]
    end
    
    TESTING_EXTRA --> PYTEST
    BASE_DEPS --> PYTYPE
    JAX_DEPS --> PYTEST
    TF_DEPS --> PYTEST
    
    PYTYPE --> TYPE_ANALYSIS
    PYTEST --> UNIT_TESTS
    PYTEST --> INTEGRATION_TESTS
    
    CPU_PARALLEL --> PYTYPE
    CPU_PARALLEL --> PYTEST
```

**Testing Architecture Components**
Sources: [test.sh:18-27]()

## Package Dependencies and Installation

The bsuite package supports multiple installation configurations to accommodate different development and usage scenarios. The testing process validates all supported dependency combinations.

| Dependency Group | Command | Purpose |
|------------------|---------|---------|
| Core Package | `pip install .` | Base bsuite functionality |
| JAX Baselines | `pip install .[baselines_jax]` | JAX-based agent implementations |
| TensorFlow Baselines | `pip install .[baselines]` | TensorFlow/Sonnet agents |
| Testing Dependencies | `pip install .[testing]` | Development and testing tools |

**Installation Dependencies**
Sources: [test.sh:14-19]()

## Automated Testing Pipeline

The automated testing pipeline executes both static analysis and dynamic testing in parallel to maximize efficiency while ensuring comprehensive validation.

### Static Type Checking

The `pytype` tool performs static type analysis across the entire bsuite codebase:

```bash
pytype -j "${N_CPU}" bsuite
```

This command utilizes all available CPU cores for parallel type checking of the `bsuite` module and its submodules.

### Dynamic Testing

The `pytest` framework executes the test suite with parallel processing:

```bash
pytest -n "${N_CPU}" bsuite
```

The `-n` flag enables parallel test execution across multiple CPU cores, significantly reducing test execution time.

**Testing Commands**
Sources: [test.sh:21-27]()

## Environment Management

The development workflow uses isolated virtual environments to ensure reproducible testing conditions and prevent dependency conflicts.

### Virtual Environment Lifecycle

1. **Creation**: `python3 -m venv bsuite_testing`
2. **Activation**: `source bsuite_testing/bin/activate`
3. **Dependency Installation**: Multiple `pip install` commands for different configurations
4. **Testing Execution**: Type checking and test running
5. **Cleanup**: `deactivate` and `rm -rf bsuite_testing/`

This approach ensures that each test run starts with a clean environment and doesn't interfere with the developer's local Python setup.

**Environment Management**
Sources: [test.sh:8-31]()

## Development Setup Requirements

The development environment requires several system-level dependencies and tools:

- **Python 3**: Base Python interpreter
- **Virtual Environment Support**: `python3 -m venv` capability
- **Multi-core Processing**: CPU detection via `/proc/cpuinfo` for parallel execution
- **Package Management**: `pip` with `setuptools` for dependency installation

The testing script automatically detects the number of available CPU cores and configures both `pytype` and `pytest` to utilize parallel processing for optimal performance.

**System Requirements**
Sources: [test.sh:21-27]()

---

