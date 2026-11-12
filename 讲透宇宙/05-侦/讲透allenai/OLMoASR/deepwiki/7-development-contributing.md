<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/OLMoASR · page 7 Development & Contributing · fetched 2026-10-26 -->

# Development & Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/dependabot.yml](.github/dependabot.yml)
- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [HISTORY.md](HISTORY.md)
- [LICENSE](LICENSE)
- [Makefile](Makefile)
- [mypy.ini](mypy.ini)

</details>



This document provides an overview of the development workflow and contribution guidelines for the OLMoASR system. It covers the essential tools, processes, and standards that developers need to understand when contributing to the project.

For detailed development environment setup instructions, see [Development Setup & Tools](#7.1). For understanding the codebase organization, see [Project Structure & Organization](#7.2).

## Development Workflow Overview

The OLMoASR project follows standard open-source development practices with automated quality checks and continuous integration. The development workflow is built around several key tools and processes that ensure code quality and system reliability.

### Development Environment Architecture

```mermaid
graph TB
    subgraph "Local Development"
        DEV_ENV["Development Environment"]
        MAKEFILE["Makefile<br/>Development Commands"]
        VENV[".env<br/>Python Virtual Environment"]
        DEPS["requirements-test.txt<br/>Development Dependencies"]
    end
    
    subgraph "Code Quality Tools"
        MYPY["mypy<br/>Type Checking"]
        BLACK["black<br/>Code Formatting"]
        PYTEST["pytest<br/>Unit Testing"]
        LINT["make lint<br/>Quality Checks"]
    end
    
    subgraph "CI/CD Pipeline"
        GH_ACTIONS[".github/workflows/ci.yml<br/>GitHub Actions"]
        LINT_JOB["Lint Job<br/>Python 3.8"]
        TEST_JOB["Test Job<br/>Python 3.8, 3.10"]
        DEPENDABOT[".github/dependabot.yml<br/>Dependency Updates"]
    end
    
    DEV_ENV --> MAKEFILE
    MAKEFILE --> VENV
    MAKEFILE --> DEPS
    MAKEFILE --> LINT
    
    LINT --> MYPY
    LINT --> BLACK
    MAKEFILE --> PYTEST
    
    GH_ACTIONS --> LINT_JOB
    GH_ACTIONS --> TEST_JOB
    LINT_JOB --> MYPY
    LINT_JOB --> BLACK
    TEST_JOB --> PYTEST
```

Sources: [Makefile:1-27](), [.github/workflows/ci.yml:1-53](), [mypy.ini:1-6]()

## Development Commands

The project uses a `Makefile` to standardize common development tasks. Key commands include:

| Command | Purpose | Description |
|---------|---------|-------------|
| `make install` | Package Installation | Upgrades pip and installs package in development mode |
| `make install-dev` | Development Dependencies | Installs testing and development requirements |
| `make lint` | Code Quality | Runs `mypy` type checking and `black` format checking |
| `make black` | Code Formatting | Auto-formats Python code using `black` with 120 character line limit |
| `make test` | Unit Testing | Runs the full test suite using `pytest` |
| `make help` | Command Reference | Shows all available make commands with descriptions |

Sources: [Makefile:1-27]()

### Code Quality Standards

The project enforces several code quality standards through automated tools:

```mermaid
graph LR
    subgraph "Quality Checks"
        TYPE_CHECK["mypy<br/>Type Checking"]
        FORMAT_CHECK["black --check<br/>Format Validation"]
        FORMAT_AUTO["black<br/>Auto-formatting"]
    end
    
    subgraph "Configuration"
        MYPY_CONFIG["mypy.ini<br/>Python 3.8<br/>ignore_missing_imports"]
        BLACK_CONFIG["Line Length: 120<br/>Auto-format: Yes"]
    end
    
    subgraph "Testing Framework"
        PYTEST_CONFIG["pytest<br/>-x -s -v flags"]
        TEST_DIR["tests/<br/>Unit Test Directory"]
    end
    
    TYPE_CHECK --> MYPY_CONFIG
    FORMAT_CHECK --> BLACK_CONFIG
    FORMAT_AUTO --> BLACK_CONFIG
    PYTEST_CONFIG --> TEST_DIR
```

Sources: [Makefile:8-23](), [mypy.ini:1-6]()

## Continuous Integration Pipeline

The project uses GitHub Actions for continuous integration with two main job types:

### CI Job Configuration

```mermaid
graph TB
    subgraph "Trigger Events"
        PUSH_MAIN["push: main branch"]
        PR_MAIN["pull_request: main branch"]
    end
    
    subgraph "Lint Job"
        UBUNTU_LINT["runs-on: ubuntu-latest"]
        PYTHON38_LINT["Python 3.8"]
        SETUP_LINT["Setup & Install"]
        RUN_LINT["make lint"]
    end
    
    subgraph "Test Job"
        UBUNTU_TEST["runs-on: ubuntu-latest"]
        PYTHON_MATRIX["Python 3.8, 3.10"]
        SETUP_TEST["Setup & Install"]
        RUN_TEST["make test"]
    end
    
    subgraph "Dependency Management"
        DEPENDABOT["dependabot.yml<br/>Daily pip updates"]
    end
    
    PUSH_MAIN --> UBUNTU_LINT
    PR_MAIN --> UBUNTU_LINT
    PUSH_MAIN --> UBUNTU_TEST
    PR_MAIN --> UBUNTU_TEST
    
    UBUNTU_LINT --> PYTHON38_LINT
    PYTHON38_LINT --> SETUP_LINT
    SETUP_LINT --> RUN_LINT
    
    UBUNTU_TEST --> PYTHON_MATRIX
    PYTHON_MATRIX --> SETUP_TEST
    SETUP_TEST --> RUN_TEST
```

Sources: [.github/workflows/ci.yml:1-53](), [.github/dependabot.yml:1-7]()

## Licensing and Legal

The project is licensed under the MIT License, providing broad permissions for use, modification, and distribution. Contributors should ensure their contributions are compatible with this license.

Key license characteristics:
- **Permissions**: Commercial use, modification, distribution, private use
- **Limitations**: No liability, no warranty
- **Conditions**: Include license and copyright notice

Sources: [LICENSE:1-22]()

## Version Management

The project maintains version history through semantic versioning practices. Current version information is tracked in the `HISTORY.md` file, which follows a changelog format for documenting releases and changes.

Sources: [HISTORY.md:1-3]()

## Getting Started as a Contributor

To begin contributing to OLMoASR:

1. **Environment Setup**: Follow the development setup process detailed in [Development Setup & Tools](#7.1)
2. **Code Organization**: Understand the project structure covered in [Project Structure & Organization](#7.2)  
3. **Quality Standards**: Ensure all code passes `make lint` and `make test` before submitting
4. **CI Requirements**: Verify that changes pass all GitHub Actions workflows

The development workflow emphasizes automation and consistency, with most quality checks handled through the `Makefile` commands and CI pipeline. This ensures that all contributors work within the same standards and that the codebase maintains high quality across all contributions.

---

