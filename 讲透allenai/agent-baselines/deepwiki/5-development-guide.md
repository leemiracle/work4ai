<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/agent-baselines · page 5 Development Guide · fetched 2026-10-26 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci-test.yml](.github/workflows/ci-test.yml)
- [Makefile](Makefile)
- [docker/Dockerfile](docker/Dockerfile)
- [setup.cfg](setup.cfg)

</details>



This document provides comprehensive instructions for developers contributing to the agent-baselines project. It covers the development workflow, Docker-based environment setup, continuous integration pipeline, code quality standards, and testing practices. For information about the evaluation pipeline and DVC configuration, see [Evaluation Pipeline](#3). For details about agent implementation and architecture, see [Agent Architecture](#4).

## Docker-Based Development Environment

The project uses a sophisticated Docker-based development environment with multi-stage builds to support different agent types and their dependencies. The development workflow is centered around containerized execution to ensure consistency across different development environments.

### Docker Build Architecture

```mermaid
graph TD
    subgraph "Base Image Build"
        BASE["python:3.11.3"]
        TOOLS["System Tools Installation<br/>apt-get: less, git, curl, cmake, clang"]
        DOCKER_CLI["Docker CLI Installation<br/>docker-27.3.1.tgz"]
        COMPOSE["Docker Compose<br/>v2.29.6"]
        UV["UV Package Manager<br/>astral.sh/uv/install.sh"]
        CARGO["Rust Cargo<br/>rustup.rs"]
    end
    
    subgraph "Base Dependencies"
        PYPROJECT["pyproject.toml"]
        UV_SYNC["uv sync --extra dev"]
        BASE_IMAGE["agent-baselines-base"]
    end
    
    subgraph "Solver-Specific Images"
        REACT_IMG["react<br/>solvers/react/setup.sh"]
        SMOL_IMG["smolagents<br/>solvers/smolagents/setup.sh"]
        STORM_IMG["storm<br/>solvers/storm/setup.sh"]
        SQA_IMG["sqa<br/>solvers/sqa/setup.sh"]
        SUPER_IMG["super<br/>solvers/super/setup.sh"]
        DATA_IMG["datavoyager<br/>solvers/datavoyager/setup.sh"]
        FUTURE_IMG["futurehouse<br/>solvers/futurehouse/setup.sh"]
    end
    
    BASE --> TOOLS
    TOOLS --> DOCKER_CLI
    DOCKER_CLI --> COMPOSE
    COMPOSE --> UV
    UV --> CARGO
    CARGO --> PYPROJECT
    PYPROJECT --> UV_SYNC
    UV_SYNC --> BASE_IMAGE
    
    BASE_IMAGE --> REACT_IMG
    BASE_IMAGE --> SMOL_IMG
    BASE_IMAGE --> STORM_IMG
    BASE_IMAGE --> SQA_IMG
    BASE_IMAGE --> SUPER_IMG
    BASE_IMAGE --> DATA_IMG
    BASE_IMAGE --> FUTURE_IMG
```

The Docker build system supports building both the base image and solver-specific images. The base image `agent-baselines-base` contains all common dependencies, while solver-specific images extend the base with additional requirements.

**Sources:** [docker/Dockerfile:1-63]()

### Makefile Development Interface

The `Makefile` provides a unified interface for all development tasks, automatically handling Docker builds, environment variable injection, and container orchestration.

```mermaid
graph LR
    subgraph "Make Targets"
        BUILD["make build-image<br/>SOLVER=solver_name"]
        SHELL["make shell<br/>Interactive container"]
        TEST["make test<br/>pytest execution"]
        TEST_EXP["make test-expensive<br/>Integration tests"]
        FORMAT["make format<br/>black formatting"]
        MYPY["make mypy<br/>Type checking"]
        FLAKE["make flake<br/>Linting"]
    end
    
    subgraph "Docker Operations"
        BUILD_CMD["docker build --target TARGET<br/>--tag AGENT_BASELINES_TAG"]
        RUN_CMD["docker run --rm ENV_ARGS<br/>LOCAL_MOUNTS"]
        UV_RUN["uv run --extra dev<br/>command execution"]
    end
    
    subgraph "Environment Handling"
        ENV_FILE[".env file loading"]
        API_KEYS["API key injection<br/>OPENAI_API_KEY, HF_TOKEN"]
        SOLVER_ENV["solvers/SOLVER/env"]
        CI_ENV["IS_CI environment detection"]
    end
    
    BUILD --> BUILD_CMD
    SHELL --> RUN_CMD
    TEST --> UV_RUN
    FORMAT --> UV_RUN
    MYPY --> UV_RUN
    FLAKE --> UV_RUN
    
    BUILD_CMD --> ENV_FILE
    RUN_CMD --> API_KEYS
    UV_RUN --> SOLVER_ENV
    ENV_FILE --> CI_ENV
```

Key environment variables and mounting behavior:
- **Local Development**: Mounts source code directories for live editing
- **CI Environment**: Uses read-only container execution
- **Solver-Specific**: Loads `solvers/{SOLVER}/env` files automatically

**Sources:** [Makefile:1-137]()

## CI/CD Pipeline

The continuous integration pipeline uses GitHub Actions with Docker layer caching to ensure fast, reliable builds and comprehensive testing.

### GitHub Actions Workflow

```mermaid
graph TD
    subgraph "Trigger Conditions"
        PR["Pull Request to main"]
        BRANCH["Branch: main"]
    end
    
    subgraph "CI Environment Setup"
        UBUNTU["runs-on: ubuntu-latest"]
        ENV_VARS["Environment Variables<br/>IS_CI=true<br/>OPENAI_API_KEY=Fake<br/>HF_TOKEN"]
        CHECKOUT["actions/checkout@v4"]
    end
    
    subgraph "Docker Build Pipeline"
        BUILDX["docker/setup-buildx-action@v3"]
        BUILD_CACHE["docker/build-push-action@v5<br/>cache-from: type=gha<br/>cache-to: type=gha"]
        IMAGE_TAG["agent-baselines:latest<br/>target: agent-baselines-base"]
    end
    
    subgraph "Test Execution"
        ENV_INJECTION["ENV_ARGS generation<br/>grep -vE '^_'"]
        MAKE_TEST["make test<br/>Containerized pytest"]
    end
    
    PR --> UBUNTU
    UBUNTU --> ENV_VARS
    ENV_VARS --> CHECKOUT
    CHECKOUT --> BUILDX
    BUILDX --> BUILD_CACHE
    BUILD_CACHE --> IMAGE_TAG
    IMAGE_TAG --> ENV_INJECTION
    ENV_INJECTION --> MAKE_TEST
```

The CI pipeline includes several key optimizations:
- **Layer Caching**: Uses GitHub Actions cache (`type=gha`) to speed up Docker builds
- **Environment Isolation**: Filters environment variables to exclude internal ones
- **Fake API Keys**: Provides placeholder values to prevent import-time failures

**Sources:** [.github/workflows/ci-test.yml:1-38]()

## Code Quality Standards

The project enforces code quality through automated tools integrated into both the development workflow and CI pipeline.

### Type Checking with mypy

The mypy configuration in `setup.cfg` provides flexible type checking suitable for a research codebase:

| Configuration | Value | Purpose |
|---------------|-------|---------|
| `python_version` | 3.11 | Target Python version |
| `disallow_untyped_defs` | False | Allow untyped functions for flexibility |
| `check_untyped_defs` | True | Check typed portions thoroughly |
| `no_implicit_optional` | True | Require explicit Optional annotations |
| `follow_untyped_imports` | True | Follow imports even if untyped |

**Ignored Import Modules**: The configuration ignores missing imports for optional dependencies:
- `pyasn1.*`, `langchain_*`, `autogen_*`, `smolagents.*`, `langgraph.*`, `litellm.*`

This approach allows the development image to run type checking without installing all optional solver dependencies.

**Sources:** [setup.cfg:1-49]()

### Code Formatting and Linting

```mermaid
graph LR
    subgraph "Code Quality Tools"
        BLACK["black<br/>Code formatting"]
        MYPY["mypy<br/>Type checking"]
        FLAKE8["flake8<br/>Style linting"]
    end
    
    subgraph "Execution Context"
        DEV_IMG["Development Image<br/>agent-baselines:latest"]
        UV_RUN["uv run<br/>Dependency management"]
        VOLUME_MOUNT["-v pwd:/agent-baselines<br/>Source code mounting"]
    end
    
    subgraph "Target Paths"
        SRC_PATH["agent-baselines/"]
        TEST_PATH["tests/"]
    end
    
    BLACK --> UV_RUN
    MYPY --> UV_RUN
    FLAKE8 --> UV_RUN
    
    UV_RUN --> DEV_IMG
    DEV_IMG --> VOLUME_MOUNT
    VOLUME_MOUNT --> SRC_PATH
    VOLUME_MOUNT --> TEST_PATH
```

All code quality tools run within the Docker container to ensure consistent environments. The `Makefile` provides convenience targets that automatically build the image if needed (in local development) or use the existing image (in CI).

**Sources:** [Makefile:86-121]()

## Testing Framework

The testing system uses pytest with different test categories and execution modes to support both fast development cycles and comprehensive validation.

### Test Execution Modes

| Command | Dependencies | Purpose | Environment |
|---------|-------------|---------|-------------|
| `make test` | `--extra dev --extra smolagents` | Fast unit tests | Standard pytest |
| `make test-expensive` | `--extra dev --extra inspect_evals --extra smolagents` | Integration tests | `-m expensive` marker |

### Environment-Specific Behavior

```mermaid
graph TD
    subgraph "Local Development"
        LOCAL_MOUNTS["Volume Mounts<br/>pyproject.toml (ro)<br/>agent_baselines/<br/>tests/<br/>logs/"]
        CACHE_VOLUME["agent-baselines-cache<br/>Persistent cache"]
        DOCKER_SOCKET["Docker socket mount<br/>Container-in-container"]
    end
    
    subgraph "CI Environment"
        CI_FLAG["IS_CI=true"]
        NO_MOUNTS["No volume mounts<br/>Read-only execution"]
        CI_CACHE["GitHub Actions cache<br/>Docker layers only"]
    end
    
    subgraph "Test Execution"
        PYTEST_ARGS["PYTEST_ARGS variable<br/>Custom test selection"]
        UV_SYNC["uv run --no-sync<br/>Skip dependency sync"]
        TEST_VERBOSE["-vv flag<br/>Verbose output"]
    end
    
    LOCAL_MOUNTS --> PYTEST_ARGS
    CACHE_VOLUME --> UV_SYNC
    DOCKER_SOCKET --> TEST_VERBOSE
    
    CI_FLAG --> NO_MOUNTS
    NO_MOUNTS --> CI_CACHE
    CI_CACHE --> UV_SYNC
```

The testing system automatically detects the execution environment (`IS_CI`) and adjusts mounting and caching behavior accordingly. In local development, live code editing is supported through volume mounts, while CI uses immutable container execution.

**Sources:** [Makefile:44-59](), [Makefile:122-137]()

## Development Workflow

### Quick Start Commands

1. **Build base development image:**
   ```bash
   make build-image
   ```

2. **Enter interactive development shell:**
   ```bash
   make shell
   ```

3. **Run code quality checks:**
   ```bash
   make format mypy flake
   ```

4. **Execute tests:**
   ```bash
   make test
   # Or with specific test selection
   make test PYTEST_ARGS="-k test_name"
   ```

5. **Build solver-specific image:**
   ```bash
   make build-image SOLVER=react
   make shell SOLVER=react
   ```

### Environment Variable Management

The build system supports multiple methods for environment variable injection:

- **`.env` file**: Automatically loaded if present
- **Direct export**: `export OPENAI_API_KEY=...`
- **Solver-specific**: Automatically loads `solvers/{SOLVER}/env`
- **Make variable**: `SOLVER=react make shell`

**Sources:** [Makefile:23-39]()

This development guide provides the foundation for contributing to the agent-baselines project, ensuring consistent development practices and reliable code quality across all contributions.

---

