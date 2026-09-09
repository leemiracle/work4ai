> 来源: [https://deepwiki.com/xorbitsai/inference/9-development-and-testing](https://deepwiki.com/xorbitsai/inference/9-development-and-testing)
> DeepWiki xorbitsai/inference | Last indexed: 30 July 2026 (d97e09

# Development and Testing

  Relevant source files 
 - [.gitattributes](https://github.com/xorbitsai/inference/blob/d97e0970/.gitattributes)
 - [.github/actions/check-release-permission/action.yaml](https://github.com/xorbitsai/inference/blob/d97e0970/.github/actions/check-release-permission/action.yaml)
 - [.github/workflows/docker-cd.yaml](https://github.com/xorbitsai/inference/blob/d97e0970/.github/workflows/docker-cd.yaml)
 - [.github/workflows/python.yaml](https://github.com/xorbitsai/inference/blob/d97e0970/.github/workflows/python.yaml)
 - [.github/workflows/release.yaml](https://github.com/xorbitsai/inference/blob/d97e0970/.github/workflows/release.yaml)
 - [.pre-commit-config.yaml](https://github.com/xorbitsai/inference/blob/d97e0970/.pre-commit-config.yaml)
 - [MANIFEST.in](https://github.com/xorbitsai/inference/blob/d97e0970/MANIFEST.in)
 - [pyproject.toml](https://github.com/xorbitsai/inference/blob/d97e0970/pyproject.toml)
 - [xinference/__init__.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/__init__.py)
 - [xinference/deploy/docker/requirements_cpu/requirements_cpu-ml.txt](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/docker/requirements_cpu/requirements_cpu-ml.txt)
 - [xinference/model/__init__.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/__init__.py)
 - [xinference/model/llm/__init__.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/__init__.py)
 - [xinference/model/llm/llm_family.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/llm_family.py)
 - [xinference/model/llm/tests/test_llm_family.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/tests/test_llm_family.py)
 
  This document provides comprehensive information for developers contributing to Xinference, including development environment setup, testing infrastructure, CI/CD pipelines, and code quality standards.

 
## Purpose and Scope

 This page covers:

 
 - **Development environment setup**: Installing dependencies and optional features for local development.
 - **Testing framework**: `pytest` configuration, test organization, and platform-specific testing.
 - **CI/CD pipelines**: GitHub Actions workflows for linting, testing, and multi-platform validation.
 - **Code quality tools**: ruff, black, isort, mypy, and codespell configurations.
 - **Benchmarking**: Tools for measuring system performance.
 - **Code Organization**: Overview of the package structure.
 
 For detailed guides, see the following child pages:

 
 - [Development Setup](https://deepwiki.com/xorbitsai/inference/9.1-development-setup) — Installation, dependencies, and build process.
 - [Testing and CI/CD](https://deepwiki.com/xorbitsai/inference/9.2-testing-and-cicd) — Pytest structure, fixtures, and GitHub Actions.
 - [Benchmarking](https://deepwiki.com/xorbitsai/inference/9.3-benchmarking) — Tools for latency and throughput measurement.
 - [Code Organization](https://deepwiki.com/xorbitsai/inference/9.4-code-organization) — Package structure and architectural patterns.
 
 
## Development Environment Setup

 Xinference uses `pyproject.toml` to define core dependencies and optional feature sets. The system supports multiple "extras" for different capabilities.

 
### Installation Options

 
| Extra Group | Purpose | Key Dependencies |
|---|---|---|
| dev | Development & Testing | pytest, ruff, black, mypy, langchain |
| all | Full Feature Set | Includes all model type extras (LLM, Image, Audio, etc.) |
| vllm | vLLM Engine (Linux) | vllm>=0.2.6, xxhash |
| mlx | MLX Engine (macOS ARM) | mlx-lm, mlx-vlm, mlx-whisper |
| transformers | HF Transformers | transformers>=4.53.3, accelerate, peft |
| llama_cpp | llama.cpp Backend | xllamacpp>=0.2.0 |

 **Sources:** [pyproject.toml81-228](https://github.com/xorbitsai/inference/blob/d97e0970/pyproject.toml#L81-L228)

 
### Core Dependencies

 Critical dependencies for the system include:

 
 - `xoscar`: Actor framework for distributed execution [pyproject.toml35](https://github.com/xorbitsai/inference/blob/d97e0970/pyproject.toml#L35-L35)
 - `fastapi`: RESTful API layer [pyproject.toml44](https://github.com/xorbitsai/inference/blob/d97e0970/pyproject.toml#L44-L44)
 - `torch`: Deep learning framework [pyproject.toml36](https://github.com/xorbitsai/inference/blob/d97e0970/pyproject.toml#L36-L36)
 - `huggingface-hub` & `modelscope`: Model download utilities [pyproject.toml48-50](https://github.com/xorbitsai/inference/blob/d97e0970/pyproject.toml#L48-L50)
 
 
## Testing Infrastructure

 
### Test Organization and Structure

 The codebase follows a modular test structure where tests reside within their respective package directories.

 
```

```

 **Sources:** [.github/workflows/python.yaml103-147](https://github.com/xorbitsai/inference/blob/d97e0970/.github/workflows/python.yaml#L103-L147) [xinference/model/llm/tests/test_llm_family.py1-35](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/tests/test_llm_family.py#L1-L35)

 
### CI/CD Pipeline

 The CI pipeline in `.github/workflows/python.yaml` is triggered on pushes and pull requests [python.yaml3-8](https://github.com/xorbitsai/inference/blob/d97e0970/python.yaml#L3-L8) It includes a sophisticated "Detect GPU CI changes" step that maps changed files to specific test groups (`llm`, `embedding`, `image`, `audio`) to optimize resource usage [python.yaml73-165](https://github.com/xorbitsai/inference/blob/d97e0970/python.yaml#L73-L165)

 **Linting Pipeline:**

 
 - **Pre-commit**: Runs `black`, `ruff`, `isort`, `mypy`, and `codespell` [python.yaml32-35](https://github.com/xorbitsai/inference/blob/d97e0970/python.yaml#L32-L35) [.pre-commit-config.yaml1-38](https://github.com/xorbitsai/inference/blob/d97e0970/.pre-commit-config.yaml#L1-L38)
 - **Frontend**: Builds the React UI and verifies static exports [python.yaml41-58](https://github.com/xorbitsai/inference/blob/d97e0970/python.yaml#L41-L58)
 
 
## Benchmarking

 Xinference provides a suite of benchmarking scripts located in the `benchmark/` directory (not shown in provided snippets but referenced in `MANIFEST.in`). These tools are used to measure:

 
 - **Serving Performance**: Throughput and concurrency using `benchmark_serving.py`.
 - **Latency**: Time-to-first-token (TTFT) and inter-token latency using `benchmark_latency.py`.
 - **Model Specifics**: Rerank and long-context performance.
 
 For details, see [Benchmarking](https://deepwiki.com/xorbitsai/inference/9.3-benchmarking). **Sources:** [MANIFEST.in36](https://github.com/xorbitsai/inference/blob/d97e0970/MANIFEST.in#L36-L36)

 
## Code Quality Standards

 Xinference enforces strict code quality through automated tools:

 
| Tool | Role | Configuration |
|---|---|---|
| Black | Code Formatting | pyproject.toml96 .pre-commit-config.yaml3-7 |
| Ruff | Linting & Fast Checks | pyproject.toml95 .pre-commit-config.yaml15-19 |
| Mypy | Static Type Checking | .pre-commit-config.yaml25-31 |
| Isort | Import Sorting | .pre-commit-config.yaml20-24 |

 
## Docker and CD

 Xinference maintains multiple Docker variants (GPU, CPU, aarch64) [docker-cd.yaml25-138](https://github.com/xorbitsai/inference/blob/d97e0970/docker-cd.yaml#L25-L138)

 
 - **Release Process**: Automated builds and uploads to PyPI occur on tag pushes [release.yaml1-69](https://github.com/xorbitsai/inference/blob/d97e0970/release.yaml#L1-L69)
 - **Docker Hub**: Nightly and versioned images are pushed to Docker Hub [docker-cd.yaml39-100](https://github.com/xorbitsai/inference/blob/d97e0970/docker-cd.yaml#L39-L100)
 
 
```

```

 **Sources:** [.github/workflows/release.yaml1-7](https://github.com/xorbitsai/inference/blob/d97e0970/.github/workflows/release.yaml#L1-L7) [.github/workflows/docker-cd.yaml1-172](https://github.com/xorbitsai/inference/blob/d97e0970/.github/workflows/docker-cd.yaml#L1-L172)

 For details on project structure, see [Code Organization](https://deepwiki.com/xorbitsai/inference/9.4-code-organization).
