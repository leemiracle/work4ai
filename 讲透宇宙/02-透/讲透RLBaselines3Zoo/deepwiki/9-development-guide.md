<!-- source: DeepWiki mcp.deepwiki.com · repo DLR-RM/rl-baselines3-zoo · page 9 Development Guide · fetched 2026-10-14 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [Makefile](Makefile)
- [pyproject.toml](pyproject.toml)
- [setup.py](setup.py)

</details>



This guide provides information for developers who want to contribute to the RL-Baselines3-Zoo project. It covers the development environment setup, code quality standards, testing procedures, and contribution workflow.

For information about using the framework for training agents, see [Training System](#3), and for evaluating trained agents, see [Evaluation and Benchmarking](#5).

## Development Environment Setup

Setting up a development environment for RL-Baselines3-Zoo requires Python 3.9 or newer.

```mermaid
flowchart TD
    subgraph "Development Setup"
        A["Clone Repository"] --> B["Install Dependencies"]
        B --> C["Install in Development Mode"]
        C --> D["Run Tests to Verify Setup"]
    end
    
    A --> |"git clone https://github.com/DLR-RM/rl-baselines3-zoo.git"| A1["Local Repository"]
    B --> |"pip install -r requirements.txt"| B1["Core Dependencies"]
    B --> |"pip install -e .[plots,tests]"| B2["Dev Dependencies"]
    C --> |"make pytest"| D1["Test Suite"]
```

### Installation for Development

1. Clone the repository and change to the project directory
2. Install the package in development mode with test and plotting dependencies:

```bash
pip install -r requirements.txt
pip install -e .[plots,tests]
```

Sources: [setup.py:17-34](), [Makefile:4-5]()

## Code Style and Quality Standards

RL-Baselines3-Zoo uses several tools to maintain code quality and consistency:

```mermaid
flowchart LR
    subgraph "Code Quality Tools"
        A["black"] --> |"Code Formatting"| A1["PEP 8 Compliance"]
        B["ruff"] --> |"Linting"| B1["Error Detection"]
        C["mypy"] --> |"Type Checking"| C1["Type Annotations"]
    end
    
    subgraph "Development Commands"
        M1["make format"] --> A
        M2["make lint"] --> B
        M3["make type"] --> C
        M4["make commit-checks"] --> M1 & M2 & M3
    end
```

### Code Formatting

The project uses Black for code formatting with a line length of 127 characters:

```bash
make format    # Format code
make check-codestyle    # Check code style without modifying files
```

### Linting

Linting is performed using ruff:

```bash
make lint    # Run linter
```

### Type Checking

The project uses mypy for static type checking:

```bash
make type    # Run type checker
```

Sources: [Makefile:11-36](), [pyproject.toml:1-31]()

## Testing Framework

RL-Baselines3-Zoo has a comprehensive testing suite to ensure functionality and prevent regressions.

```mermaid
flowchart TD
    subgraph "Testing Framework"
        A["pytest"] --> B["Unit Tests"]
        A --> C["Integration Tests"]
        A --> D["Trained Agent Tests"]
        
        B --> E["Test Coverage"]
        C --> E
        D --> E
    end
    
    subgraph "Test Commands"
        M1["make pytest"] --> A
        M2["make check-trained-agents"] --> D
    end
```

### Running Tests

To run the test suite:

```bash
make pytest    # Run all tests
make check-trained-agents    # Test all trained agents (slow)
```

The `run_tests.sh` script is used to execute the tests with proper environment variables and coverage reporting.

### Test Coverage

Test coverage is tracked using the coverage tool, with configuration in pyproject.toml that excludes certain files from coverage reporting.

Sources: [Makefile:4-9](), [pyproject.toml:49-61]()

## Documentation

Documentation is built using Sphinx and is an essential part of the project.

```mermaid
flowchart LR
    subgraph "Documentation System"
        A["Sphinx"] --> B["HTML Docs"]
        A --> C["API Reference"]
        D["Spelling Check"] --> A
    end
    
    subgraph "Documentation Commands"
        M1["make doc"] --> A
        M2["make spelling"] --> D
        M3["make clean"] --> |"Clean Docs"| A
    end
```

### Building Documentation

To build the documentation:

```bash
make doc    # Build HTML documentation
make spelling    # Check documentation spelling
make clean    # Clean documentation build files
```

Sources: [Makefile:37-44]()

## Continuous Integration

The project uses GitHub Actions for continuous integration to ensure code quality and compatibility.

```mermaid
flowchart TD
    subgraph "CI Pipeline"
        A["GitHub Actions"] --> B["Multiple Python Versions"]
        B --> C["Install Dependencies"]
        C --> D["Lint"]
        D --> E["Check Code Style"]
        E --> F["Build Documentation"]
        F --> G["Type Check"]
        G --> H["Run Tests"]
    end
    
    B --> B1["Python 3.9"]
    B --> B2["Python 3.10"]
    B --> B3["Python 3.11"]
    B --> B4["Python 3.12"]
    B --> B5["Python 3.10 with Gymnasium 0.29.1"]
```

The CI workflow:
1. Runs on push to master and pull requests
2. Tests on multiple Python versions (3.9, 3.10, 3.11, 3.12)
3. Tests with different Gymnasium versions
4. Performs linting, code style checks, documentation building, type checking, and testing

Sources: [.github/workflows/ci.yml:1-74]()

## Docker Development

For containerized development, Docker images are provided:

```mermaid
flowchart LR
    subgraph "Docker Images"
        A["CPU Image"] --> C["Development Environment"]
        B["GPU Image"] --> C
    end
    
    subgraph "Docker Commands"
        M1["make docker-cpu"] --> A
        M2["make docker-gpu"] --> B
        M3["make docker"] --> M1 & M2
    end
```

### Building Docker Images

To build Docker images:

```bash
make docker-cpu    # Build CPU Docker image
make docker-gpu    # Build GPU Docker image
make docker        # Build both images
```

Sources: [Makefile:46-52]()

## Package Release Process

The project provides commands for building and releasing packages:

```mermaid
flowchart TD
    subgraph "Release Process"
        A["Build Package"] --> B["Source Distribution"]
        A --> C["Wheel Distribution"]
        B & C --> D["Upload to PyPI"]
        B & C --> E["Upload to Test PyPI"]
    end
    
    subgraph "Release Commands"
        M1["make release"] --> D
        M2["make test-release"] --> E
    end
```

### Creating Releases

To create a package release:

```bash
make release        # Build and upload to PyPI
make test-release   # Build and upload to Test PyPI
```

Sources: [Makefile:54-66]()

## Project Organization

The project is structured as follows:

```mermaid
graph TD
    subgraph "Project Structure"
        A["rl_zoo3/"] --> A1["Core Package"]
        B["hyperparams/"] --> B1["Algorithm Configurations"]
        C["tests/"] --> C1["Test Suite"]
        D["scripts/"] --> D1["Utility Scripts"]
        E["docs/"] --> E1["Documentation"]
    end
    
    A --> A2["version.txt"]
    A --> A3["plots/"]
    B --> B2["*.yml Files"]
    B --> B3["python/*.py"]
```

### Key Files and Directories

- `rl_zoo3/`: The main package directory
- `hyperparams/`: YAML configuration files for algorithms
- `tests/`: Test suite
- `scripts/`: Utility scripts for development and testing
- `docs/`: Documentation source files

Sources: [setup.py:9-10](), [setup.py:36-45]()

## Contributing Workflow

When contributing to RL-Baselines3-Zoo, follow this workflow:

```mermaid
flowchart LR
    A["Fork Repository"] --> B["Create Branch"]
    B --> C["Make Changes"]
    C --> D["Run Commit-Checks"]
    D --> E["Push Changes"]
    E --> F["Create Pull Request"]
    
    D --> |"make commit-checks"| D1["Format, Lint, Type Check"]
```

### Before Submitting a Pull Request

1. Ensure code passes all checks:
   ```bash
   make commit-checks   # Runs format, lint, and type checks
   make pytest          # Runs tests
   ```
2. Update documentation if necessary
3. Add tests for new functionality
4. Follow the code style guidelines

Sources: [Makefile:35]()

## Dependencies Management

Dependencies are managed in several files:

1. Core dependencies in `setup.py`
2. Additional dependencies for plots and tests
3. Development dependencies in `requirements.txt`

The project uses specific versions of dependencies to ensure compatibility:

- Stable Baselines3 Contributors (sb3_contrib): >=2.6.0,<3.0
- Gymnasium: >=0.29.1,<1.2.0
- Python: >=3.9

Sources: [setup.py:17-34](), [.github/workflows/ci.yml:39-57]()

---

