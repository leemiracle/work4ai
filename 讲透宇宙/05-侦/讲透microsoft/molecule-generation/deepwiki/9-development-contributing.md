<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/molecule-generation · page 9 Development & Contributing · fetched 2026-10-26 -->

# Development & Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [molecule_generation/test/conftest.py](molecule_generation/test/conftest.py)

</details>



This page provides guidance for developers who want to contribute to or extend the molecule-generation system. It covers the development workflow, code organization, testing framework, and contribution guidelines. For specific setup instructions for a development environment, see [Development Environment](#9.1). For detailed information about running and writing tests, see [Testing Framework](#9.2).

## Overview

The molecule-generation repository follows modern software engineering practices with comprehensive testing, continuous integration, and multi-version compatibility. The project supports Python 3.8-3.10 with multiple TensorFlow and RDKit versions to ensure broad compatibility across different computational environments.

## Development Workflow

### CI/CD Pipeline Architecture

The project uses GitHub Actions for continuous integration with a comprehensive build matrix that tests across multiple Python and dependency versions.

```mermaid
flowchart TD
    TRIGGER["Push/PR to main"] --> MATRIX["Build Matrix"]
    
    MATRIX --> PY38["Python 3.8.16<br/>TF 2.6.2<br/>RDKit 2021.09.1"]
    MATRIX --> PY39["Python 3.9.16<br/>TF 2.9.1<br/>RDKit 2022.09.1"] 
    MATRIX --> PY310["Python 3.10<br/>TF 2.9.*<br/>RDKit latest"]
    
    PY38 --> SETUP38["setup-miniconda"]
    PY39 --> SETUP39["setup-miniconda"]
    PY310 --> SETUP310["setup-miniconda"]
    
    SETUP38 --> INSTALL["pip install .<br/>black flake8 pytest"]
    SETUP39 --> INSTALL
    SETUP310 --> INSTALL
    
    INSTALL --> BLACK["black --check --diff"]
    BLACK --> FLAKE8["flake8"]
    FLAKE8 --> UNIT["pytest unit tests"]
    UNIT --> INTEGRATION["pytest integration tests"]
    
    INTEGRATION --> SUCCESS["Build Success"]
    
    subgraph "Environment Files"
        ENV38["environment-py38.yml"]
        ENV39["environment-py39.yml"] 
        ENV310["environment.yml"]
    end
    
    PY38 -.-> ENV38
    PY39 -.-> ENV39
    PY310 -.-> ENV310
```

**CI/CD Pipeline Structure**

Sources: [.github/workflows/ci.yml:1-51]()

### Code Quality Standards

The project enforces strict code quality standards through automated tooling:

| Tool | Purpose | Configuration |
|------|---------|---------------|
| `black==23.1.0` | Code formatting | Enforces consistent Python style |
| `flake8` | Linting | Catches syntax errors and style violations |
| `pytest` | Testing | Unit and integration test execution |

The CI pipeline runs these tools in sequence, failing the build if any violations are detected.

Sources: [.github/workflows/ci.yml:38-44]()

## Project Structure and Code Organization

### Core Module Architecture

The codebase is organized into logical modules that correspond to different aspects of the molecule generation pipeline:

```mermaid
graph TD
    ROOT["molecule_generation/"] --> CLI["cli/"]
    ROOT --> MODELS["models/"]
    ROOT --> LAYERS["layers/"]
    ROOT --> CHEM["chem/"]
    ROOT --> UTILS["utils/"]
    ROOT --> VIS["visualisation/"]
    ROOT --> TEST["test/"]
    
    CLI --> PREPROCESS["preprocess.py"]
    CLI --> TRAIN["train.py"]
    CLI --> SAMPLE["sample.py"]
    CLI --> ENCODE["encode.py"]
    CLI --> VISUALISE["visualise.py"]
    
    MODELS --> CGVAE["cgvae/"]
    MODELS --> MOLER["moler/"]
    
    MOLER --> VAE["moler_vae.py"]
    MOLER --> GEN["moler_generator.py"]
    MOLER --> DEC["moler_decoder.py"]
    MOLER --> WRAP["molecule_generation_utils.py"]
    
    TEST --> UNIT["unit/"]
    TEST --> INTEGRATION["integration/"]
    TEST --> CONFTEST["conftest.py"]
    TEST --> DATASETS["test_datasets/"]
    
    DATASETS --> SMILES["10_test_smiles.smiles"]
```

**Module Organization and Key Components**

Sources: Inferred from repository structure and [molecule_generation/test/conftest.py:1-17]()

### Testing Infrastructure

The testing framework uses `pytest` with a clear separation between unit and integration tests:

```mermaid
graph LR
    CONFTEST["conftest.py"] --> FIXTURES["Test Fixtures"]
    
    FIXTURES --> SMILES_PATH["test_smiles_path"]
    FIXTURES --> SMILES_DATA["test_smiles"]
    
    SMILES_PATH --> TESTDATA["test_datasets/<br/>10_test_smiles.smiles"]
    SMILES_DATA --> MOLLIST["List[str] of SMILES"]
    
    UNIT["unit/"] --> CONFTEST
    INTEGRATION["integration/"] --> CONFTEST
    
    subgraph "Test Execution"
        PYTEST["pytest command"]
        PYTEST --> UNIT_RUN["pytest --ignore=integration/"]
        PYTEST --> INT_RUN["pytest integration/"]
    end
    
    CONFTEST -.-> PYTEST
```

**Test Fixture Architecture**

The `conftest.py` file provides reusable test fixtures:
- `test_smiles_path`: Path to test SMILES dataset
- `test_smiles`: Loaded list of SMILES strings for testing

Sources: [molecule_generation/test/conftest.py:7-16]()

## Environment Management

### Multi-Version Support Matrix

The project maintains compatibility across multiple Python and dependency versions using conda environment files:

| Environment File | Python Version | TensorFlow | RDKit | Purpose |
|------------------|----------------|------------|-------|---------|
| `environment-py38.yml` | 3.8.16 | 2.6.2 | 2021.09.1 | Legacy compatibility |
| `environment-py39.yml` | 3.9.16 | 2.9.1 | 2022.09.1 | Stable production |
| `environment.yml` | 3.10 | 2.9.* | latest | Latest features |

This matrix ensures the system works across different computational environments and dependency constraints.

Sources: [.github/workflows/ci.yml:17-22]()

## Contributing Guidelines

### Development Setup

1. **Environment Setup**: Choose the appropriate conda environment file based on your Python version requirements
2. **Installation**: Install the package in development mode using `pip install .`
3. **Development Dependencies**: Install additional tools with `pip install black==23.1.0 flake8 pytest`

### Code Standards

- **Formatting**: All code must pass `black --check --diff`
- **Linting**: Code must be free of `flake8` violations
- **Testing**: New features require corresponding unit tests
- **Integration Testing**: Complex features should include integration tests

### Pull Request Process

1. **Code Quality**: Ensure all CI checks pass
2. **Test Coverage**: Include appropriate test coverage for new functionality
3. **Documentation**: Update relevant documentation for API changes
4. **Multi-Version Testing**: Changes are tested across the full build matrix

### Testing Strategy

The project uses a two-tier testing approach:

- **Unit Tests**: Fast, isolated tests for individual components
- **Integration Tests**: End-to-end tests that verify the complete pipeline

Test isolation is achieved through the fixture system in `conftest.py`, which provides consistent test data across different test modules.

Sources: [.github/workflows/ci.yml:46-50](), [molecule_generation/test/conftest.py:1-17]()

## Development Best Practices

### Code Organization Principles

- **Modular Design**: Each module has a clear, single responsibility
- **CLI Separation**: Command-line interfaces are separated from core logic
- **Model Abstraction**: Different model architectures share common interfaces
- **Test Data Management**: Test datasets are centrally managed and reusable

### Dependency Management

The project uses conda for environment management to handle complex scientific computing dependencies like RDKit and TensorFlow. The multi-environment approach ensures compatibility across different deployment scenarios while maintaining reproducible builds.

For detailed information about setting up a local development environment, see [Development Environment](#9.1). For comprehensive testing procedures and writing new tests, see [Testing Framework](#9.2).

---

