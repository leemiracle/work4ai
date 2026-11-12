> 来源: [https://deepwiki.com/kscalelabs/ksim/6-development-and-testing](https://deepwiki.com/kscalelabs/ksim/6-development-and-testing)
> DeepWiki kscalelabs/ksim | Last indexed: 18 May 2025 (9d2640

# Development and Testing

  Relevant source files 
 - [.darglint](https://github.com/kscalelabs/ksim/blob/9d26400d/.darglint)
 - [.github/workflows/publish.yml](https://github.com/kscalelabs/ksim/blob/9d26400d/.github/workflows/publish.yml)
 - [.github/workflows/test.yml](https://github.com/kscalelabs/ksim/blob/9d26400d/.github/workflows/test.yml)
 - [LICENSE](https://github.com/kscalelabs/ksim/blob/9d26400d/LICENSE)
 - [MANIFEST.in](https://github.com/kscalelabs/ksim/blob/9d26400d/MANIFEST.in)
 - [Makefile](https://github.com/kscalelabs/ksim/blob/9d26400d/Makefile)
 - [examples/data/scene.mjcf](https://github.com/kscalelabs/ksim/blob/9d26400d/examples/data/scene.mjcf)
 - [ksim/py.typed](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/py.typed)
 - [ksim/requirements-dev.txt](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/requirements-dev.txt)
 - [pyproject.toml](https://github.com/kscalelabs/ksim/blob/9d26400d/pyproject.toml)
 - [tests/assets/humanoid.mjcf](https://github.com/kscalelabs/ksim/blob/9d26400d/tests/assets/humanoid.mjcf)
 - [tests/conftest.py](https://github.com/kscalelabs/ksim/blob/9d26400d/tests/conftest.py)
 
  This document provides a comprehensive overview of the development tools, testing infrastructure, and continuous integration setup for the KSIM framework. It covers how to set up your development environment, run tests, ensure code quality, and understand the automated workflows in place.

 
## 1. Project Setup and Dependencies

 The KSIM framework requires certain tools and dependencies for development work. This section outlines how to set up your development environment.

 
### 1.1 Development Dependencies

 KSIM requires the following development dependencies as specified in the requirements-dev.txt file:

 
```
mypy       # Static type checking
pytest     # Testing framework
ruff       # Fast Python linter and formatter
```

 These tools ensure code quality and facilitate testing during development.

 Sources: [ksim/requirements-dev.txt](https://github.com/kscalelabs/ksim/blob/9d26400d/ksim/requirements-dev.txt)

 
### 1.2 Development Environment Setup

 To set up your development environment for KSIM:

 
 - Clone the repository:

 
```

```
 - Install the package in development mode with development dependencies:

 
```

```
 
 This installs KSIM and its dependencies in development mode, allowing you to modify the code and have changes immediately available.

 
## 2. Testing Framework

 KSIM uses pytest as its primary testing framework. The testing infrastructure is designed to ensure the reliability and correctness of the codebase.

 
### 2.1 Testing Architecture

 
```

```

 Sources: [tests/conftest.py](https://github.com/kscalelabs/ksim/blob/9d26400d/tests/conftest.py) [pyproject.toml1-8](https://github.com/kscalelabs/ksim/blob/9d26400d/pyproject.toml#L1-L8)

 
### 2.2 Test Configuration

 KSIM's test configuration is defined in the `pyproject.toml` file:

 
```

```

 This configuration:

 
 - Enables detailed reporting of xfailed (-rx) and xpassed (-rf) tests
 - Stops at first failure (-x)
 - Runs in quiet mode (-q)
 - Provides full tracebacks for failures (--full-trace)
 - Defines a custom marker for slow tests
 
 Sources: [pyproject.toml1-8](https://github.com/kscalelabs/ksim/blob/9d26400d/pyproject.toml#L1-L8)

 
### 2.3 Test Fixtures

 KSIM defines several useful test fixtures in `conftest.py`:

 
 - `set_random_seed()`: Automatically sets a fixed random seed (1337) for all tests to ensure reproducibility
 - `get_mujoco_humanoid_model()`: Returns a MuJoCo humanoid model for testing
 - `get_mjx_humanoid_model()`: Returns an MJX humanoid model for testing
 - `humanoid_model()`: A parameterized fixture that provides either MuJoCo or MJX humanoid models
 
 The test fixtures are designed to simplify testing of physics-based components by providing standardized models.

 Sources: [tests/conftest.py15-37](https://github.com/kscalelabs/ksim/blob/9d26400d/tests/conftest.py#L15-L37)

 
### 2.4 Running Tests

 Tests can be run using the Makefile command:

 
```

```

 This will execute all tests in the `tests` directory using pytest.

 Sources: [Makefile19-21](https://github.com/kscalelabs/ksim/blob/9d26400d/Makefile#L19-L21)

 
### 2.5 Test Organization

 
```

```

 Sources: [tests/conftest.py](https://github.com/kscalelabs/ksim/blob/9d26400d/tests/conftest.py) [tests/assets/humanoid.mjcf](https://github.com/kscalelabs/ksim/blob/9d26400d/tests/assets/humanoid.mjcf)

 
## 3. Code Quality Tools

 KSIM employs several tools to maintain code quality through static analysis, linting, and formatting.

 
### 3.1 Code Quality Architecture

 
```

```

 Sources: [pyproject.toml10-82](https://github.com/kscalelabs/ksim/blob/9d26400d/pyproject.toml#L10-L82) [Makefile3-17](https://github.com/kscalelabs/ksim/blob/9d26400d/Makefile#L3-L17)

 
### 3.2 Code Formatting with Ruff

 KSIM uses Ruff for code formatting, configured in `pyproject.toml`:

 
```

```

 To format code, run:

 
```

```

 This command formats all Python files in the `ksim`, `tests`, and `examples` directories.

 Sources: [Makefile3-9](https://github.com/kscalelabs/ksim/blob/9d26400d/Makefile#L3-L9) [pyproject.toml50-53](https://github.com/kscalelabs/ksim/blob/9d26400d/pyproject.toml#L50-L53)

 
### 3.3 Static Analysis

 KSIM uses multiple static analysis tools to ensure code quality:

 
 - **Ruff Linting**: Configured to check for a variety of issues including annotations, bugs, style, imports, etc.
 - **MyPy Type Checking**: Enforces strict type checking with settings like `disallow_untyped_defs` and `strict_equality`
 
 To run all static checks:

 
```

```

 Sources: [Makefile11-17](https://github.com/kscalelabs/ksim/blob/9d26400d/Makefile#L11-L17) [pyproject.toml10-44](https://github.com/kscalelabs/ksim/blob/9d26400d/pyproject.toml#L10-L44) [pyproject.toml54-82](https://github.com/kscalelabs/ksim/blob/9d26400d/pyproject.toml#L54-L82)

 
### 3.4 Type Checking with MyPy

 KSIM employs strict type checking with MyPy, configured in `pyproject.toml`:

 
```

```

 The configuration enforces type annotations for all function definitions and includes various settings to make error messages more helpful for developers.

 Sources: [pyproject.toml10-44](https://github.com/kscalelabs/ksim/blob/9d26400d/pyproject.toml#L10-L44)

 
## 4. CI/CD Workflows

 KSIM uses GitHub Actions for continuous integration and continuous deployment.

 
### 4.1 CI/CD Architecture

 
```

```

 Sources: [.github/workflows/test.yml](https://github.com/kscalelabs/ksim/blob/9d26400d/.github/workflows/test.yml) [.github/workflows/publish.yml](https://github.com/kscalelabs/ksim/blob/9d26400d/.github/workflows/publish.yml)

 
### 4.2 Test Workflow

 The test workflow is triggered on pushes to the master branch and on pull requests. It performs the following steps:

 
 - Checks out the repository
 - Sets up Python 3.12
 - Restores cached dependencies (if available)
 - Installs the package with development dependencies
 - Runs static checks using `make static-checks`
 - Runs tests using `make test`
 - Saves the cache for future runs
 
 The workflow has a timeout of 10 minutes and uses concurrency settings to avoid running multiple instances of the same workflow in parallel.

 Sources: [.github/workflows/test.yml1-67](https://github.com/kscalelabs/ksim/blob/9d26400d/.github/workflows/test.yml#L1-L67)

 
### 4.3 Publish Workflow

 The publish workflow is triggered when a new release is created or manually through workflow dispatch. It handles:

 
 - Building platform-specific wheels (optional, based on input)
 - Building source distribution
 - Publishing packages to PyPI
 
 The workflow uses PyPA's GitHub Action for publishing to PyPI, ensuring secure authentication through OIDC tokens.

 Sources: [.github/workflows/publish.yml1-122](https://github.com/kscalelabs/ksim/blob/9d26400d/.github/workflows/publish.yml#L1-L122)

 
## 5. Common Development Tasks

 This section provides quick reference for common development tasks in the KSIM project.

 
### 5.1 Development Task Reference

 
| Task | Command | Description |
|---|---|---|
| Install development environment | pip install -e '.[dev]' | Installs KSIM in development mode with dev dependencies |
| Format code | make format | Formats code using Ruff |
| Run static checks | make static-checks | Runs Ruff linting and MyPy type checking |
| Run tests | make test | Runs all tests using pytest |
| Full quality check | make static-checks && make test | Runs all static checks and tests |

 
### 5.2 Recommended Development Workflow

 
 - Clone the repository
 - Set up your development environment
 - Make changes to the codebase
 - Run `make format` to format your code
 - Run `make static-checks` to ensure code quality
 - Run `make test` to verify your changes don't break existing functionality
 - Submit a pull request
 
 Following this workflow ensures that your contributions maintain the project's quality standards and integrates well with the CI/CD pipeline.

 Sources: [Makefile3-21](https://github.com/kscalelabs/ksim/blob/9d26400d/Makefile#L3-L21)
