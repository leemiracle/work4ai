<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/optimum-executorch · page 7 Development and Contributing · fetched 2026-10-26 -->

# Development and Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/test_models.yml](.github/workflows/test_models.yml)
- [install_dev.py](install_dev.py)
- [optimum/executorch/__init__.py](optimum/executorch/__init__.py)
- [optimum/exporters/executorch/tasks/__init__.py](optimum/exporters/executorch/tasks/__init__.py)
- [optimum/exporters/executorch/tasks/asr.py](optimum/exporters/executorch/tasks/asr.py)
- [setup.py](setup.py)
- [tests/models/test_modeling_whisper.py](tests/models/test_modeling_whisper.py)

</details>



This document provides comprehensive guidance for developers who want to contribute to or extend the optimum-executorch project. It covers the development environment setup, testing framework, CI/CD pipeline, and contribution guidelines.

For information about setting up optimum-executorch for regular usage, see [Installation and Setup](#1.1). For details about the specific testing commands and framework structure, see [Testing Framework](#7.2).

## Development Environment Setup

The optimum-executorch project requires a carefully configured development environment with specific versions of PyTorch, ExecuTorch, and related dependencies. The project provides automated tools to ensure consistency across development environments.

### Core Development Dependencies

The development setup is managed through two primary mechanisms: the package setup configuration and the development installation script.

```mermaid
graph TB
    subgraph "Development Setup Process"
        INSTALL_DEV["install_dev.py"]
        SETUP_PY["setup.py"]
        NIGHTLY_DEPS["install_torch_nightly_deps()"]
        SOURCE_DEPS["install_dep_from_source()"]
    end
    
    subgraph "Core Dependencies"
        TORCH_NIGHTLY["torch==2.8.0.dev20250601"]
        ET_NIGHTLY["executorch==0.7.0.dev20250625"]
        TORCHAO_NIGHTLY["torchao==0.12.0.dev20250620"]
        TRANSFORMERS_SOURCE["transformers@896e9cea1ade521b2648f4798218550f6c72190c"]
        TOKENIZERS_SOURCE["pytorch-tokenizers@fc32028858020c4fcafe37aaaeaf5d1b480336a2"]
    end
    
    subgraph "Development Extras"
        DEV_EXTRAS["[dev] extras"]
        TEST_DEPS["TESTS_REQUIRE"]
        QUALITY_DEPS["QUALITY_REQUIRE"]
    end
    
    INSTALL_DEV --> SETUP_PY
    INSTALL_DEV --> NIGHTLY_DEPS
    INSTALL_DEV --> SOURCE_DEPS
    
    NIGHTLY_DEPS --> TORCH_NIGHTLY
    NIGHTLY_DEPS --> ET_NIGHTLY
    NIGHTLY_DEPS --> TORCHAO_NIGHTLY
    
    SOURCE_DEPS --> TRANSFORMERS_SOURCE
    SOURCE_DEPS --> TOKENIZERS_SOURCE
    
    SETUP_PY --> DEV_EXTRAS
    DEV_EXTRAS --> TEST_DEPS
    DEV_EXTRAS --> QUALITY_DEPS
```

**Sources:** [install_dev.py:1-74](), [setup.py:14-42]()

### Development Installation Process

The `install_dev.py` script provides the primary entry point for setting up a development environment. It orchestrates the installation of all required dependencies in the correct order:

| Function | Purpose | Key Dependencies |
|----------|---------|------------------|
| `install_torch_nightly_deps()` | Installs pinned nightly versions of PyTorch ecosystem | torch, executorch, torchvision, torchaudio, torchao |
| `install_dep_from_source()` | Installs dependencies from specific Git commits | transformers, pytorch-tokenizers |
| `main()` | Coordinates the full installation process | Calls pip install .[dev] and dependency functions |

The installation process supports the `--skip_override_torch` flag to allow developers to use their own PyTorch installation for specific testing scenarios.

**Sources:** [install_dev.py:6-73]()

### Package Configuration

The `setup.py` file defines the project structure and dependency requirements:

- **Python Version Support**: 3.10, 3.11, 3.12
- **Core Dependencies**: optimum~=1.24, executorch>=0.6.0, transformers==4.51.3
- **Development Extras**: Includes testing frameworks, quality tools, and specialized libraries

```mermaid
graph LR
    subgraph "setup.py Configuration"
        INSTALL_REQUIRE["INSTALL_REQUIRE"]
        TESTS_REQUIRE["TESTS_REQUIRE"] 
        QUALITY_REQUIRE["QUALITY_REQUIRE"]
        EXTRAS_REQUIRE["EXTRAS_REQUIRE"]
    end
    
    subgraph "Core Runtime"
        OPTIMUM["optimum~=1.24"]
        EXECUTORCH["executorch>=0.6.0"]
        TRANSFORMERS["transformers==4.51.3"]
    end
    
    subgraph "Testing Dependencies"
        PYTEST["pytest"]
        ACCELERATE["accelerate>=0.26.0"]
        DATASETS["datasets"]
        COREML["coremltools>=8.2.0"]
        AUDIO_LIBS["librosa, soundfile"]
    end
    
    subgraph "Quality Tools"
        BLACK["black~=23.1"]
        RUFF["ruff==0.4.4"]
    end
    
    INSTALL_REQUIRE --> OPTIMUM
    INSTALL_REQUIRE --> EXECUTORCH
    INSTALL_REQUIRE --> TRANSFORMERS
    
    TESTS_REQUIRE --> PYTEST
    TESTS_REQUIRE --> ACCELERATE
    TESTS_REQUIRE --> DATASETS
    TESTS_REQUIRE --> COREML
    TESTS_REQUIRE --> AUDIO_LIBS
    
    QUALITY_REQUIRE --> BLACK
    QUALITY_REQUIRE --> RUFF
    
    EXTRAS_REQUIRE --> TESTS_REQUIRE
    EXTRAS_REQUIRE --> QUALITY_REQUIRE
```

**Sources:** [setup.py:14-42]()

## Testing Framework

The optimum-executorch testing framework is designed to validate model export and inference capabilities across different ExecuTorch versions and operating systems. The testing system uses dynamic discovery to automatically detect and test all supported model families.

### Test Structure and Organization

The testing framework follows a consistent pattern where each model family has its own test file:

```mermaid
graph TB
    subgraph "Test File Organization"
        TEST_DIR["tests/models/"]
        TEST_PATTERN["test_modeling_*.py"]
        WHISPER_TEST["test_modeling_whisper.py"]
        OTHER_TESTS["test_modeling_llama.py<br/>test_modeling_gemma.py<br/>test_modeling_qwen.py<br/>..."]
    end
    
    subgraph "Test Class Structure"
        BASE_CLASS["ExecuTorchModelIntegrationTest"]
        EXPORT_METHOD["test_*_export_to_executorch()"]
        INFERENCE_METHOD["test_*_transcription()/_generation()"]
        HELPER_METHOD["_helper_*_method()"]
    end
    
    subgraph "Test Execution Flow"
        CLI_SUBPROCESS["subprocess.run(optimum-cli export executorch)"]
        PTE_VALIDATION["Validate .pte file creation"]
        MODEL_LOADING["ExecuTorchModelForXXX.from_pretrained()"]
        INFERENCE_VALIDATION["Validate inference outputs"]
    end
    
    TEST_DIR --> TEST_PATTERN
    TEST_PATTERN --> WHISPER_TEST
    TEST_PATTERN --> OTHER_TESTS
    
    WHISPER_TEST --> BASE_CLASS
    BASE_CLASS --> EXPORT_METHOD
    BASE_CLASS --> INFERENCE_METHOD
    BASE_CLASS --> HELPER_METHOD
    
    EXPORT_METHOD --> CLI_SUBPROCESS
    CLI_SUBPROCESS --> PTE_VALIDATION
    PTE_VALIDATION --> MODEL_LOADING
    MODEL_LOADING --> INFERENCE_VALIDATION
```

**Sources:** [tests/models/test_modeling_whisper.py:41-107]()

### Test Categories and Execution

The testing framework includes several categories of tests:

| Test Type | Decorator | Purpose | Example |
|-----------|-----------|---------|---------|
| Export Tests | No special decorator | Validate CLI export functionality | `test_whisper_export_to_executorch()` |
| Inference Tests | `@slow`, `@pytest.mark.run_slow` | Validate model inference quality | `test_whisper_transcription()` |
| Backend-Specific Tests | `@pytest.mark.portable` | Test specific ExecuTorch backends | `test_whisper_transcription_portable()` |
| Version-Specific Tests | `@pytest.mark.skipif` | Conditional tests based on versions | ExecuTorch >= 0.7.0 requirements |

**Sources:** [tests/models/test_modeling_whisper.py:93-107]()

### Test Implementation Pattern

Each model test follows a consistent implementation pattern demonstrated in the Whisper test:

1. **Export Test**: Uses `subprocess.run()` to call the CLI export command
2. **File Validation**: Checks for expected `.pte` file creation
3. **Model Loading**: Instantiates the appropriate `ExecuTorchModelForXXX` class
4. **Inference Validation**: Compares outputs against expected results

The test framework also includes environment setup with `os.environ["TOKENIZERS_PARALLELISM"] = "false"` to avoid parallelism issues during testing.

**Sources:** [tests/models/test_modeling_whisper.py:34-86]()

## CI/CD Pipeline

The continuous integration system is built around GitHub Actions and provides comprehensive testing across multiple ExecuTorch versions, Python versions, and operating systems.

### Dynamic Test Discovery

The CI pipeline uses a sophisticated test discovery mechanism to automatically identify and test all model families:

```mermaid
graph TB
    subgraph "Test Discovery Job"
        DISCOVER_JOB["discover-tests"]
        FIND_CMD["find tests/models -name 'test_modeling_*.py'"]
        EXTRACT_NAMES["sed extraction pipeline"]
        SET_MATRIX["Set GitHub output matrix"]
    end
    
    subgraph "Test Matrix Generation"
        MODEL_NAMES["model_names output"]
        JSON_ARRAY["JSON array format"]
        EXAMPLE_OUTPUT["['whisper','llama','gemma',...]"]
    end
    
    subgraph "Matrix Strategy"
        RUN_TESTS_JOB["run-tests job"]
        MATRIX_PARAMS["Matrix parameters"]
        EXECUTORCH_VERSIONS["executorch-version: ['0.6.0', 'nightly']"]
        PYTHON_VERSIONS["python-version: ['3.11']"]
        OS_VERSIONS["os: [macos-15, ubuntu-22.04]"]
    end
    
    DISCOVER_JOB --> FIND_CMD
    FIND_CMD --> EXTRACT_NAMES
    EXTRACT_NAMES --> SET_MATRIX
    
    SET_MATRIX --> MODEL_NAMES
    MODEL_NAMES --> JSON_ARRAY
    JSON_ARRAY --> EXAMPLE_OUTPUT
    
    EXAMPLE_OUTPUT --> RUN_TESTS_JOB
    RUN_TESTS_JOB --> MATRIX_PARAMS
    MATRIX_PARAMS --> EXECUTORCH_VERSIONS
    MATRIX_PARAMS --> PYTHON_VERSIONS
    MATRIX_PARAMS --> OS_VERSIONS
```

**Sources:** [.github/workflows/test_models.yml:14-29](), [.github/workflows/test_models.yml:32-42]()

### Test Execution Matrix

The CI system creates a comprehensive test matrix that ensures compatibility across different environments:

| Dimension | Values | Purpose |
|-----------|--------|---------|
| Model Types | Dynamically discovered from test files | Ensures all supported models are tested |
| ExecuTorch Versions | 0.6.0, nightly | Maintains compatibility across versions |
| Python Versions | 3.11 | Validates Python compatibility |
| Operating Systems | macos-15, ubuntu-22.04 | Cross-platform validation |

Each job in the matrix has a descriptive name format: `{model} (et={executorch-version}, py={python-version}, {os})`

**Sources:** [.github/workflows/test_models.yml:34-42]()

### Environment Setup and Test Execution

The CI pipeline handles environment setup differently based on the ExecuTorch version being tested:

```mermaid
graph TB
    subgraph "Environment Setup Logic"
        VERSION_CHECK["if executorch-version == 'nightly'"]
        NIGHTLY_PATH["python install_dev.py"]
        STABLE_PATH["pip install '[tests]' + executorch version"]
    end
    
    subgraph "Test Execution"
        RUN_SLOW["RUN_SLOW=1 environment variable"]
        PYTEST_CMD["pytest tests/models/test_modeling_*.py"]
        VERBOSE_FLAGS["-s -vvvv --durations=0 --log-cli-level=INFO"]
    end
    
    subgraph "Dependency Management"
        NIGHTLY_DEPS["Nightly: install_dev.py handles all deps"]
        STABLE_DEPS["Stable: specific executorch version + tokenizers"]
        TOKENIZERS_GIT["git+https://github.com/pytorch-labs/tokenizers"]
    end
    
    VERSION_CHECK --> NIGHTLY_PATH
    VERSION_CHECK --> STABLE_PATH
    
    NIGHTLY_PATH --> NIGHTLY_DEPS
    STABLE_PATH --> STABLE_DEPS
    STABLE_DEPS --> TOKENIZERS_GIT
    
    NIGHTLY_DEPS --> RUN_SLOW
    STABLE_DEPS --> RUN_SLOW
    RUN_SLOW --> PYTEST_CMD
    PYTEST_CMD --> VERBOSE_FLAGS
```

**Sources:** [.github/workflows/test_models.yml:52-64]()

The test execution uses comprehensive logging and timing information to help diagnose issues and monitor performance across the test suite.

## Contributing Guidelines

### Code Quality Standards

The project maintains code quality through automated tools defined in the `QUALITY_REQUIRE` section:

- **Black**: Code formatting with version ~23.1
- **Ruff**: Linting with version 0.4.4

### Version Compatibility

The project supports multiple Python versions (3.10, 3.11, 3.12) and maintains compatibility with both stable and nightly ExecuTorch releases. Contributors should test changes against both the stable (0.6.0) and nightly ExecuTorch versions.

### Testing Requirements

All contributions must include appropriate tests following the established patterns:
- Export tests for new model families
- Inference validation tests
- Backend-specific tests where applicable
- Version compatibility checks using `@pytest.mark.skipif`

**Sources:** [setup.py:35-42](), [.github/workflows/test_models.yml:37-38]()

---

