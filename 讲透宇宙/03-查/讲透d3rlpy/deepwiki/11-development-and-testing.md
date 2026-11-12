<!-- source: DeepWiki mcp.deepwiki.com · repo takuseno/d3rlpy · page 11 Development and Testing · fetched 2026-10-30 -->

# Development and Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.coveragerc](.coveragerc)
- [.github/workflows/format_check.yml](.github/workflows/format_check.yml)
- [.github/workflows/test.yml](.github/workflows/test.yml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [dev.requirements.txt](dev.requirements.txt)
- [scripts/test](scripts/test)
- [tests/base_test.py](tests/base_test.py)

</details>



## Purpose and Scope

This document covers the development and testing infrastructure of d3rlpy, including continuous integration pipelines, testing frameworks, code quality tools, and development workflows. This system ensures code reliability, maintains consistent formatting, and provides tools for contributors to develop and test the library effectively.

For information about algorithm-specific testing patterns, see the individual algorithm documentation in [Algorithm System](#5). For CLI testing tools, see [CLI and Utilities](#9).

## CI/CD Pipeline Architecture

The d3rlpy project uses GitHub Actions to automate testing and quality assurance across multiple platforms and Python versions.

### Continuous Integration Workflows

```mermaid
graph TD
    subgraph "GitHub Actions Triggers"
        PUSH["Push Events"]
        PR["Pull Request Events"]
    end
    
    subgraph "Test Workflow (.github/workflows/test.yml)"
        TEST_JOB["test job"]
        SETUP_PY["Setup Python 3.10"]
        CACHE_PIP["Cache pip dependencies"]  
        INSTALL_DEPS["Install Dependencies"]
        UNIT_TESTS["pytest Unit Tests"]
        UPLOAD_COV["Upload Coverage to Codecov"]
    end
    
    subgraph "Format Check Workflow (.github/workflows/format_check.yml)"
        FORMAT_JOB["format check job"]
        SETUP_PY2["Setup Python 3.9"]
        CACHE_PIP2["Cache pip dependencies"]
        INSTALL_DEPS2["Install Dependencies"] 
        STATIC_ANALYSIS["./scripts/lint"]
    end
    
    subgraph "Matrix Strategy"
        UBUNTU["ubuntu-22.04"]
        MACOS["macos-latest"]
    end
    
    subgraph "Dependencies"
        TORCH_CPU["torch CPU (Windows)"]
        LIBOMP["libomp (macOS)"]
        DEV_REQS["dev.requirements.txt"]
        PACKAGE_INSTALL["pip install -e ."]
    end
    
    PUSH --> TEST_JOB
    PUSH --> FORMAT_JOB
    PR --> TEST_JOB  
    PR --> FORMAT_JOB
    
    TEST_JOB --> SETUP_PY
    SETUP_PY --> CACHE_PIP
    CACHE_PIP --> INSTALL_DEPS
    INSTALL_DEPS --> UNIT_TESTS
    UNIT_TESTS --> UPLOAD_COV
    
    FORMAT_JOB --> SETUP_PY2
    SETUP_PY2 --> CACHE_PIP2
    CACHE_PIP2 --> INSTALL_DEPS2
    INSTALL_DEPS2 --> STATIC_ANALYSIS
    
    TEST_JOB --> UBUNTU
    TEST_JOB --> MACOS
    
    INSTALL_DEPS --> TORCH_CPU
    INSTALL_DEPS --> LIBOMP
    INSTALL_DEPS --> DEV_REQS
    INSTALL_DEPS --> PACKAGE_INSTALL
```

The CI system runs two main workflows on every push and pull request:

**Test Workflow**: Executes comprehensive unit tests across Ubuntu and macOS platforms, generating coverage reports and uploading them to Codecov. The workflow includes platform-specific dependency handling, such as installing `libomp` for macOS compatibility.

**Format Check Workflow**: Runs static analysis and format checking using the `./scripts/lint` script to ensure code quality standards.

Sources: [.github/workflows/test.yml:1-55](), [.github/workflows/format_check.yml:1-35]()

### Test Execution Pipeline

```mermaid
graph LR
    subgraph "Test Script (scripts/test)"
        TEST_SCRIPT["./scripts/test"]
        CREATE_DIR["mkdir -p test_data"]
        SET_FLAGS["TEST_PERFORMANCE flag"]
        PYTEST_CMD["pytest with coverage"]
        CLEANUP["rm -r test_data"]
    end
    
    subgraph "pytest Configuration"
        COV_REPORT["--cov-report=xml"]
        COV_TARGET["--cov=d3rlpy"]
        COV_CONFIG["--cov-config=.coveragerc"]
        TEST_DIR["tests directory"]
        NO_WARNINGS["-p no:warnings"]
        VERBOSE["-v"]
    end
    
    subgraph "Coverage Configuration (.coveragerc)"
        OMIT_CLI["omit = d3rlpy/cli.py"]
    end
    
    TEST_SCRIPT --> CREATE_DIR
    CREATE_DIR --> SET_FLAGS
    SET_FLAGS --> PYTEST_CMD
    PYTEST_CMD --> CLEANUP
    
    PYTEST_CMD --> COV_REPORT
    PYTEST_CMD --> COV_TARGET
    PYTEST_CMD --> COV_CONFIG
    PYTEST_CMD --> TEST_DIR
    PYTEST_CMD --> NO_WARNINGS
    PYTEST_CMD --> VERBOSE
    
    COV_CONFIG --> OMIT_CLI
```

The test execution follows a structured pipeline that creates temporary directories, configures coverage reporting, and executes pytest with comprehensive coverage analysis while excluding CLI components from coverage requirements.

Sources: [scripts/test:1-34](), [.coveragerc:1-3]()

## Testing Framework

### Core Testing Dependencies

The testing framework is built on pytest with additional tools for coverage, type checking, and code quality:

| Tool | Purpose | Configuration |
|------|---------|---------------|
| `pytest` | Test runner and framework | Command-line flags in test script |
| `pytest-cov` | Coverage reporting | `.coveragerc` configuration |
| `mypy` | Static type checking | Used in lint script |
| `ruff` | Linting and formatting | Used in lint script |
| `black` | Code formatting | Used in lint script |
| `docformatter` | Docstring formatting | Used in lint script |

Sources: [dev.requirements.txt:1-15]()

### Test Utility Framework

```mermaid
graph TD
    subgraph "Base Test Utilities (tests/base_test.py)"
        CHECK_RECONST["_check_reconst_algo()"]
        FROM_JSON_TEST["from_json_tester()"]
        LOAD_LEARNABLE_TEST["load_learnable_tester()"]
    end
    
    subgraph "Algorithm Reconstruction Testing"
        COMPARE_TYPES["Compare algorithm types"]
        CHECK_SHAPES["Check observation shapes"]  
        CHECK_ACTION_SIZE["Check action sizes"]
        CHECK_SCALERS["Check scaler types"]
    end
    
    subgraph "JSON Serialization Testing"
        CREATE_IMPL["algo.create_impl()"]
        SAVE_CONFIG["save_config()"]
        LOAD_FROM_JSON["algo.from_json()"]
        VALIDATE_RECONST["_check_reconst_algo()"]
    end
    
    subgraph "D3 File Testing"
        SAVE_D3["algo.save(.d3)"]
        LOAD_D3["load_learnable()"]
        COMPARE_WEIGHTS["Compare model weights"]
    end
    
    subgraph "Dependencies"
        D3RLPY_BASE["d3rlpy.base classes"]
        D3RLPY_LOGGING["d3rlpy.logging"]
        FILE_ADAPTER["FileAdapterFactory"]
    end
    
    FROM_JSON_TEST --> CREATE_IMPL
    CREATE_IMPL --> SAVE_CONFIG
    SAVE_CONFIG --> LOAD_FROM_JSON
    LOAD_FROM_JSON --> VALIDATE_RECONST
    
    LOAD_LEARNABLE_TEST --> SAVE_D3
    SAVE_D3 --> LOAD_D3
    LOAD_D3 --> COMPARE_WEIGHTS
    
    CHECK_RECONST --> COMPARE_TYPES
    CHECK_RECONST --> CHECK_SHAPES
    CHECK_RECONST --> CHECK_ACTION_SIZE
    CHECK_RECONST --> CHECK_SCALERS
    
    FROM_JSON_TEST --> D3RLPY_LOGGING
    FROM_JSON_TEST --> FILE_ADAPTER
    LOAD_LEARNABLE_TEST --> D3RLPY_BASE
```

The test utility framework provides standardized patterns for testing algorithm serialization, deserialization, and reconstruction. The `_check_reconst_algo` function validates that reconstructed algorithms maintain identical properties including observation shapes, action sizes, and scaler configurations.

Sources: [tests/base_test.py:17-102]()

### Algorithm Testing Patterns

The framework defines two primary testing patterns for algorithm persistence:

**JSON Configuration Testing**: The `from_json_tester` function validates that algorithms can be saved as JSON configuration files and reconstructed with identical properties. This pattern uses the `FileAdapterFactory` and `D3RLPyLogger` to simulate the standard logging workflow.

**Binary Model Testing**: The `load_learnable_tester` function tests the complete save/load cycle for `.d3` files, including neural network weights. It compares the binary representation of model parameters to ensure exact reconstruction.

Sources: [tests/base_test.py:55-102]()

## Development Workflow

### Local Development Setup

The development workflow follows these standardized steps:

```mermaid
graph TD
    subgraph "Initial Setup"
        CLONE["git clone d3rlpy"]
        INSTALL_EDITABLE["pip install -e ."]
        INSTALL_DEV_DEPS["pip install -r dev.requirements.txt"]
    end
    
    subgraph "Development Scripts"
        TEST_SCRIPT["./scripts/test"]
        LINT_SCRIPT["./scripts/lint"]
    end
    
    subgraph "Code Quality Tools"
        RUFF_TOOL["ruff (linting & formatting)"]
        BLACK_TOOL["black (code formatting)"]
        DOCFORMATTER_TOOL["docformatter (docstring formatting)"]
        MYPY_TOOL["mypy (type checking)"]
    end
    
    subgraph "Testing Options"
        BASIC_TEST["./scripts/test"]
        PERF_TEST["./scripts/test -p"]
        CREATE_TESTDATA["mkdir -p test_data"]
        PYTEST_RUN["pytest with coverage"]
        CLEANUP_TESTDATA["rm -r test_data"]
    end
    
    CLONE --> INSTALL_EDITABLE
    INSTALL_EDITABLE --> INSTALL_DEV_DEPS
    INSTALL_DEV_DEPS --> TEST_SCRIPT
    INSTALL_DEV_DEPS --> LINT_SCRIPT
    
    LINT_SCRIPT --> RUFF_TOOL
    LINT_SCRIPT --> BLACK_TOOL  
    LINT_SCRIPT --> DOCFORMATTER_TOOL
    LINT_SCRIPT --> MYPY_TOOL
    
    TEST_SCRIPT --> BASIC_TEST
    TEST_SCRIPT --> PERF_TEST
    BASIC_TEST --> CREATE_TESTDATA
    CREATE_TESTDATA --> PYTEST_RUN
    PYTEST_RUN --> CLEANUP_TESTDATA
```

The development setup emphasizes editable installation to enable rapid iteration, comprehensive dependency management through `dev.requirements.txt`, and standardized scripts for testing and quality assurance.

Sources: [CONTRIBUTING.md:10-39](), [scripts/test:1-34]()

### Code Quality Standards

The project enforces strict code quality standards through automated tools:

**Formatting**: `ruff` and `black` ensure consistent code style across the codebase, while `docformatter` standardizes docstring formatting.

**Type Safety**: Full type annotation coverage is enforced and validated by `mypy` static analysis.

**Testing**: Comprehensive test coverage is required, with coverage reports generated automatically and uploaded to external services for tracking.

The `./scripts/lint` command executes all quality checks locally before submission, mirroring the CI/CD format check workflow.

Sources: [CONTRIBUTING.md:32-38](), [.github/workflows/format_check.yml:28-30]()

## Performance Testing

The testing framework includes optional performance testing capabilities controlled by the `TEST_PERFORMANCE` environment variable. When enabled via the `-p` flag in the test script, additional performance benchmarks are executed to validate algorithmic efficiency and resource usage.

```bash
# Standard testing
./scripts/test

# With performance testing  
./scripts/test -p
```

Sources: [scripts/test:17-30]()

---

