> 来源: [https://deepwiki.com/kscalelabs/ksim-gym/5-development-environment](https://deepwiki.com/kscalelabs/ksim-gym/5-development-environment)
> DeepWiki kscalelabs/ksim-gym | Last indexed: 18 May 2025 (3e92db

# Development Environment

  Relevant source files 
 - [Makefile](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/Makefile)
 - [pyproject.toml](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/pyproject.toml)
 - [requirements.txt](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/requirements.txt)
 - [train.py](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/train.py)
 
  This document provides a guide to setting up and working with the development environment for K-Sim Gym. It covers dependency installation, development tools, code quality checks, and common development workflows. For information about using the training system itself, see [Training System](https://deepwiki.com/kscalelabs/ksim-gym/2-training-system), and for details about model conversion and deployment, see [Model Conversion and Deployment](https://deepwiki.com/kscalelabs/ksim-gym/3-model-conversion-and-deployment).

 
## Environment Setup

 K-Sim Gym requires several dependencies for training, inference, and development. The project uses a standard Python environment with additional libraries for reinforcement learning, simulation, and model deployment.

 
### Required Dependencies

 The project's dependencies are specified in `requirements.txt` and can be categorized as follows:

 
| Category | Dependencies |
|---|---|
| Training | ksim, xax, mujoco-scenes |
| Inference | kinfer[jax] |
| Development | jupyter, ipykernel, pre-commit |

 Sources: [requirements.txt1-14](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/requirements.txt#L1-L14)

 
### Installation

 The installation process is simplified through Make commands:

 
```

```

 These commands will install all the necessary packages to run and develop the codebase.

 Sources: [Makefile5-11](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/Makefile#L5-L11)

 
## Development Tools and Configuration

 K-Sim Gym uses several tools to ensure code quality and maintainability.

 
### Code Quality Tools

 
```

```

 Sources: [Makefile13-22](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/Makefile#L13-L22) [pyproject.toml10-83](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/pyproject.toml#L10-L83)

 
### Tool Configuration

 The project uses `pyproject.toml` to configure code quality tools:

 
 - **MyPy** - Strict type checking with the following settings:

 
 - Disallow untyped definitions
 - Strict equality checking
 - Show error context and codes
 - **Ruff** - All-in-one linting and formatting tool:

 
 - Line length: 120 characters
 - Python target version: 3.10
 - Selected rule sets: ANN, D, E, F, G, I, N, PGH, PLC, PLE, PLR, PLW, W
 - Format with double quotes and Google-style docstrings
 - **Pytest** - Testing framework:

 
 - Configured to show test summary
 - Has markers for slow tests
 
 Sources: [pyproject.toml1-82](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/pyproject.toml#L1-L82)

 
## Development Workflow

 The development workflow for K-Sim Gym involves several common tasks that are streamlined using Make commands.

 
```

```

 Sources: [Makefile5-26](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/Makefile#L5-L26)

 
### Common Development Tasks

 
| Task | Command | Description |
|---|---|---|
| Install dependencies | make install | Installs runtime dependencies |
| Install dev tools | make install-dev | Installs development dependencies |
| Format code | make format | Formats Python files using ruff |
| Run static checks | make static-checks | Runs ruff and mypy on Python files |
| Run Jupyter notebook | make notebook | Starts a Jupyter notebook server |

 Sources: [Makefile5-26](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/Makefile#L5-L26)

 
## Component Integration

 The following diagram shows how the development environment components integrate with the K-Sim Gym system components:

 
```

```

 Sources: [Makefile1-26](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/Makefile#L1-L26) [requirements.txt1-14](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/requirements.txt#L1-L14) [train.py1-680](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/train.py#L1-L680)

 
## Code Structure and Tooling Relationships

 The following diagram illustrates how the tools in the development environment interact with different parts of the codebase:

 
```

```

 Sources: [Makefile1-26](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/Makefile#L1-L26) [pyproject.toml1-82](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/pyproject.toml#L1-L82)

 
## Common Development Scenarios

 
### Setting Up a New Development Environment

 To set up a new development environment:

 
 - Clone the repository
 - Install dependencies with `make install`
 - Install development tools with `make install-dev`
 - Install pre-commit hooks (recommended for automatic checks)
 
 
### Making Code Changes

 When making code changes:

 
 - Format your code with `make format`
 - Run static checks with `make static-checks`
 - Fix any issues identified by the tools
 - Run tests to ensure functionality works correctly
 
 
### Using Jupyter Notebooks

 For interactive development and experimentation:

 
 - Run `make notebook` to start a Jupyter server
 - Open the notebook interface in your browser
 - Navigate to the notebook you want to work with
 
 See [Using Jupyter Notebooks](https://deepwiki.com/kscalelabs/ksim-gym/5.2-using-jupyter-notebooks) for more details on working with notebooks.

 
### Type Safety

 K-Sim Gym uses type annotations extensively. The MyPy configuration in `pyproject.toml` is set to enforce strict type checking, which helps catch type-related errors early.

 Sources: [pyproject.toml10-42](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/pyproject.toml#L10-L42)

 
### Formatting and Style Guidelines

 The code follows a consistent style enforced by Ruff:

 
 - 120 character line length
 - Double quotes for strings
 - Google-style docstrings
 - Organized imports
 
 Sources: [pyproject.toml43-83](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/pyproject.toml#L43-L83)

 
## Continuous Integration

 The pre-commit hooks configuration helps ensure that code meets quality standards before being committed. These hooks automatically run the formatting and linting tools on changed files.

 For more details on development tools and configuration, see [Development Tools and Configuration](https://deepwiki.com/kscalelabs/ksim-gym/5.1-development-tools-and-configuration).

 Sources: [requirements.txt12-14](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/requirements.txt#L12-L14)
