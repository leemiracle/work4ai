> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-VL/5-development](https://deepwiki.com/deepseek-ai/DeepSeek-VL/5-development)
> DeepWiki deepseek-ai/DeepSeek-VL

# Development

  Relevant source files 
 - [.github/workflows/lint.yml](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/.github/workflows/lint.yml)
 - [Makefile](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/Makefile)
 - [pyproject.toml](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/pyproject.toml)
 
  This page provides technical information for developers interested in contributing to or modifying the DeepSeek-VL codebase. It covers the build system, code quality tools, and project configuration. For instructions on installing and using DeepSeek-VL, see [Getting Started](https://deepwiki.com/deepseek-ai/DeepSeek-VL/2-getting-started).

 
## Development Workflow Overview

 The DeepSeek-VL development workflow includes several components to ensure code quality and consistency. The following diagram illustrates the main development processes:

 
```

```

 Sources: [.github/workflows/lint.yml](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/.github/workflows/lint.yml) [Makefile](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/Makefile)

 
## Build System

 DeepSeek-VL uses a Makefile-based build system to streamline development tasks. The build system provides commands for installation, linting, formatting, and cleaning.

 
### Build System Components

 
```

```

 Sources: [Makefile13-99](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/Makefile#L13-L99)

 
### Common Development Commands

 The following table summarizes the key commands available for developers:

 
| Command | Description | Source |
|---|---|---|
| make or make install | Default command to install the project | Makefile13-14 |
| make lint | Run all linting tools (ruff, flake8, py-format, mypy, pylint, addlicense) | Makefile86 |
| make format | Format code with isort, black, and add license headers | Makefile88-91 |
| make clean | Clean Python cache files | Makefile93-99 |
| make pre-commit | Run pre-commit hooks on all files | Makefile81-82 |

 Sources: [Makefile13-99](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/Makefile#L13-L99)

 
## Code Quality

 DeepSeek-VL enforces code quality through a combination of linting, formatting, and static analysis tools. These tools are integrated into the development workflow through the Makefile and GitHub Actions.

 
### Code Quality Tools

 
```

```

 Sources: [.github/workflows/lint.yml](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/.github/workflows/lint.yml) [Makefile21-82](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/Makefile#L21-L82) [pyproject.toml37-50](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/pyproject.toml#L37-L50)

 
### Continuous Integration

 DeepSeek-VL uses GitHub Actions for continuous integration, automatically running linting checks on pull requests and pushes to the main branch.

 
```

```

 Sources: [.github/workflows/lint.yml1-56](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/.github/workflows/lint.yml#L1-L56)

 
### Linting Configuration

 The linting tools are configured through the `pyproject.toml` file and the Makefile. Here's an overview of the linting dependencies:

 
| Tool | Purpose | Configuration |
|---|---|---|
| black | Code formatting | Configured in pyproject.toml |
| isort | Import sorting | Configured via Makefile with project-specific settings |
| flake8 | Style guide enforcement | Multiple plugins for different checks |
| ruff | Fast Python linter | Can fix issues automatically with make ruff-fix |
| mypy | Static type checking | Configured to install missing types |
| pylint | Comprehensive linting | Includes spelling checks |

 Sources: [Makefile21-82](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/Makefile#L21-L82) [pyproject.toml37-50](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/pyproject.toml#L37-L50)

 
## Project Configuration

 DeepSeek-VL uses `pyproject.toml` for project configuration, defining package metadata, dependencies, and build requirements.

 
### Project Structure

 
```

```

 Sources: [pyproject.toml1-53](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/pyproject.toml#L1-L53)

 
### Dependencies

 DeepSeek-VL has core dependencies and optional dependencies for different use cases:

 
#### Core Dependencies

 
```
torch>=2.0.1
transformers>=4.38.2
timm>=0.9.16
accelerate
sentencepiece
attrdict
einops
```

 
#### Optional Dependencies Groups

 
| Group | Purpose | Notable Dependencies |
|---|---|---|
| gradio | Web UI interface | gradio, mdtex2html, tiktoken |
| lint | Development tools | isort, black, pylint, flake8, ruff |

 Sources: [pyproject.toml14-50](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/pyproject.toml#L14-L50)

 
### Build Configuration

 The build configuration is defined in `pyproject.toml` and uses setuptools as the build backend:

 
```
[build-system]
requires = ["setuptools>=40.6.0", "wheel"]
build-backend = "setuptools.build_meta"
```

 The project is configured to exclude the `images` directory from the package:

 
```
[tool.setuptools]
packages = {find = {exclude = ["images"]}}
```

 Sources: [pyproject.toml1-4](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/pyproject.toml#L1-L4) [pyproject.toml52-53](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/pyproject.toml#L52-L53)

 
## License Management

 DeepSeek-VL includes a license management system using the `addlicense` tool to ensure proper license headers are added to source files.

 
```

```

 Sources: [Makefile51-55](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/Makefile#L51-L55) [Makefile88-91](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/Makefile#L88-L91)

 The license headers are set to MIT license with copyright attribution to DeepSeek and the years 2023 to the current year.

 
## Development Setup Guide

 To set up a development environment for DeepSeek-VL:

 
 - Clone the repository:

 
```

```
 - Install in development mode with linting tools:

 
```

```
 - Set up pre-commit hooks:

 
```

```
 - Run code quality checks before submitting changes:

 
```

```
 - Format code:

 
```

```
 
 Sources: [.github/workflows/lint.yml42-48](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/.github/workflows/lint.yml#L42-L48) [Makefile81-86](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/Makefile#L81-L86)
