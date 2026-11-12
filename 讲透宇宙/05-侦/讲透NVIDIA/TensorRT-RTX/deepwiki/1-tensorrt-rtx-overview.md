<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/TensorRT-RTX · page 1 TensorRT-RTX Overview · fetched 2026-10-26 -->

# TensorRT-RTX Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yaml](.github/workflows/ci.yaml)
- [demo/README.md](demo/README.md)
- [demo/setup.py](demo/setup.py)

</details>



## Purpose and Scope

This document provides a high-level introduction to the TensorRT-RTX repository structure, explaining its purpose as a framework for optimizing deep learning inference on NVIDIA RTX GPUs. It covers the major subsystems—CI/CD infrastructure, demonstration applications, sample code, and core utilities—and how they relate to each other.

For detailed setup instructions, see [Installation](#2.1). For step-by-step tutorials, see [Quick Start Guide](#2.2). For deep dives into specific demonstrations, see [Flux.1 Text-to-Image Demo](#4.1). For API reference and framework internals, see [Core Framework](#5).

**Sources:** [demo/README.md:1-10]()

## What is TensorRT-RTX

TensorRT-RTX is NVIDIA's framework for accelerating deep learning inference on RTX GPUs, with specialized support for Ada and Blackwell architectures. The framework provides:

- **Advanced Precision Support**: FP8 and FP4 quantization for Ada/Blackwell GPUs, with BF16 support for Ampere and newer architectures
- **Runtime Optimization**: JIT compilation with persistent kernel caching to reduce subsequent compilation times
- **Dynamic Shape Support**: Flexible input dimensions without engine recompilation
- **Memory Management**: Low-VRAM modes for memory-constrained environments

The repository packages TensorRT-RTX as a binary release (`TensorRT-RTX-1.3.0.35-Linux-x86_64-cuda-12.9-Release-external.tar.gz`) with both C++ and Python APIs, accompanied by demonstration pipelines and sample applications.

**Sources:** [.github/workflows/ci.yaml:7-8](), [demo/README.md:38-158]()

## Repository Structure

The repository is organized into five major directories, each serving a distinct purpose:

| Directory | Purpose | Key Components |
|-----------|---------|----------------|
| `.github/workflows/` | CI/CD automation | `ci.yaml` workflow, build/test/utils Python scripts |
| `demo/` | Demonstration pipelines | Flux.1 text-to-image demo, utility modules, test suite |
| `samples/` | Minimal API examples | C++ and Python helloWorld and apiUsage samples |
| `.pre-commit-config.yaml` | Code quality enforcement | Formatting, linting, spell checking hooks |
| Root configuration files | Project setup | `CONTRIBUTING.md`, `LICENSE`, issue templates |

```mermaid
graph TB
    subgraph "Repository Root"
        CI[".github/workflows/<br/>ci.yaml<br/>build.py<br/>test.py<br/>utils.py"]
        DEMO["demo/<br/>flux1.dev/<br/>utils/<br/>tests/"]
        SAMPLES["samples/<br/>C++/<br/>Python/"]
        CONFIG[".pre-commit-config.yaml<br/>CONTRIBUTING.md<br/>LICENSE"]
    end
    
    subgraph "External Binary"
        TRTRTX["TensorRT-RTX Binary<br/>TensorRT-RTX-1.3.0.35-...-external.tar.gz<br/>Installed to: /opt/tensorrt_rtx"]
    end
    
    CI -->|"builds & tests"| SAMPLES
    CI -->|"downloads & caches"| TRTRTX
    CI -->|"validates"| DEMO
    
    DEMO -->|"imports from"| TRTRTX
    SAMPLES -->|"links with"| TRTRTX
    
    CONFIG -->|"enforces quality on"| DEMO
    CONFIG -->|"enforces quality on"| SAMPLES
```

**Sources:** [.github/workflows/ci.yaml:1-92](), [demo/README.md:1-10]()

## Core Components

### CI/CD Infrastructure

The continuous integration system orchestrates building, testing, and validation through three GitHub Actions jobs defined in `.github/workflows/ci.yaml`:

- **`build-linux`**: Compiles C++ samples using CMake, runs on Ubuntu 24.04 with CUDA 12.9 development container
- **`lint`**: Validates code formatting and style using pre-commit hooks
- **`test-linux`**: Executes C++ binaries and Python tests on RTX 4090 GPU hardware

The workflow caches the TensorRT-RTX binary at `/opt/tensorrt_rtx` to avoid redundant downloads across jobs.

**Sources:** [.github/workflows/ci.yaml:12-92]()

### Demonstration System

The `demo/` directory contains the Flux.1 text-to-image generation pipeline, showcasing TensorRT-RTX capabilities:

```mermaid
graph LR
    subgraph "demo/"
        FLUX["flux1.dev/<br/>flux_demo.py<br/>flux_demo.ipynb<br/>flux_pipeline.py<br/>requirements.txt"]
        UTILS["utils/<br/>engine.py<br/>pipeline.py<br/>cache_manager.py"]
        TESTS["tests/<br/>test_flux.py"]
    end
    
    FLUX -->|"uses"| UTILS
    TESTS -->|"validates"| FLUX
    
    UTILS -->|"class: Engine"| ENGINE_CLASS["Engine class:<br/>build_engine()<br/>load_engine()<br/>activate()<br/>infer()"]
    UTILS -->|"class: Pipeline"| PIPELINE_CLASS["Pipeline class:<br/>Abstract base<br/>for pipelines"]
    FLUX -->|"class: FluxPipeline"| FLUX_CLASS["FluxPipeline class:<br/>load_engines()<br/>encode_prompt()<br/>generate()"]
```

The `flux_demo.py` script provides command-line access while `flux_demo.ipynb` offers an interactive tutorial environment.

**Sources:** [demo/README.md:24-32](), [demo/README.md:34-110]()

### Sample Applications

Minimal examples demonstrating core API patterns:

| Sample Type | Location | Purpose |
|-------------|----------|---------|
| C++ helloWorld | `samples/C++/helloWorld/` | Basic TensorRT-RTX initialization |
| C++ apiUsage | `samples/C++/apiUsage/` | Engine building and inference |
| Python helloWorld | `samples/Python/helloWorld/` | Python API basics |
| Python apiUsage | `samples/Python/apiUsage/` | Python engine management |

These samples are built by the CI system and executed during the `test-linux` job to validate the TensorRT-RTX installation.

**Sources:** [.github/workflows/ci.yaml:34-44](), [.github/workflows/ci.yaml:81-91]()

## System Architecture: Code Entity Mapping

The following diagram maps high-level concepts to specific code entities in the repository:

```mermaid
graph TB
    subgraph "User Entry Points"
        CLI["flux_demo.py<br/>--hf-token TOKEN<br/>--prompt TEXT<br/>--precision fp8"]
        NOTEBOOK["flux_demo.ipynb<br/>Interactive cells"]
        CPP_SAMPLE["samples/C++/apiUsage/<br/>CMakeLists.txt<br/>main.cpp"]
    end
    
    subgraph "Application Layer"
        FLUX_PIPELINE["demo/flux1.dev/flux_pipeline.py<br/>class FluxPipeline"]
        PIPELINE_BASE["demo/utils/pipeline.py<br/>class Pipeline (abstract)"]
    end
    
    subgraph "Engine Management"
        ENGINE["demo/utils/engine.py<br/>class Engine"]
        ENGINE_BUILD["Engine.build_engine()<br/>ONNX → TensorRT"]
        ENGINE_LOAD["Engine.load_engine()<br/>Load from disk"]
        ENGINE_INFER["Engine.infer()<br/>Execute inference"]
    end
    
    subgraph "TensorRT-RTX Runtime"
        BINARY["/opt/tensorrt_rtx/<br/>lib/libtensorrt_rtx.so<br/>python/tensorrt_rtx/*.whl"]
        CACHE["demo_cache/<br/>shared/onnx/<br/>shared/engines/<br/>runtime.cache"]
    end
    
    CLI --> FLUX_PIPELINE
    NOTEBOOK --> FLUX_PIPELINE
    FLUX_PIPELINE -.implements.-> PIPELINE_BASE
    
    FLUX_PIPELINE --> ENGINE
    ENGINE --> ENGINE_BUILD
    ENGINE --> ENGINE_LOAD
    ENGINE --> ENGINE_INFER
    
    ENGINE_BUILD --> BINARY
    ENGINE_LOAD --> CACHE
    ENGINE_INFER --> BINARY
    
    CPP_SAMPLE -.links with.-> BINARY
```

**Sources:** [demo/README.md:27-31](), [.github/workflows/ci.yaml:7-8](), [demo/README.md:189-200]()

## Dependency Chain and Installation

The repository requires external dependencies managed through multiple systems:

```mermaid
graph TD
    subgraph "Development Environment"
        PYTHON["Python 3.9-3.12<br/>python_requires='>=3.9'"]
    end
    
    subgraph "Core Dependencies"
        TRTRTX_WHEEL["tensorrt-rtx>=1.3.0<br/>Wheel from tarball"]
        CUDA["CUDA 12.9<br/>cuda-python<13.0.0"]
        TORCH["torch>=2.7.0"]
        TRANSFORMERS["transformers>=4.52.4"]
        DIFFUSERS["diffusers>=0.33.1"]
        POLYGRAPHY["polygraphy>=0.49.24"]
    end
    
    subgraph "Optional Dependencies"
        DEV["extras_require: dev<br/>pre-commit<br/>ruff<br/>flake8"]
        JUPYTER["extras_require: jupyter<br/>jupyter<br/>notebook<br/>ipywidgets"]
    end
    
    PYTHON --> TRTRTX_WHEEL
    TRTRTX_WHEEL --> CUDA
    TRTRTX_WHEEL --> TORCH
    TRTRTX_WHEEL --> TRANSFORMERS
    TRTRTX_WHEEL --> DIFFUSERS
    TRTRTX_WHEEL --> POLYGRAPHY
    
    TRTRTX_WHEEL -.optional.-> DEV
    TRTRTX_WHEEL -.optional.-> JUPYTER
```

The package is installed via pip from the wheel file included in the TensorRT-RTX tarball:

```bash
python -m pip install path/to/tensorrt_rtx-1.3.0.35-cp312-none-linux_x86_64.whl
python -m pip install -r demo/flux1.dev/requirements.txt
```

**Sources:** [demo/setup.py:18-55](), [demo/README.md:15-22]()

## Quick Start Paths

The repository provides multiple entry points depending on user goals:

| User Goal | Entry Point | Next Steps |
|-----------|-------------|------------|
| **Try the demo** | `demo/flux1.dev/flux_demo.py` | See [Quick Start Guide](#2.2) |
| **Learn interactively** | `demo/flux1.dev/flux_demo.ipynb` | Open in Jupyter |
| **Study minimal examples** | `samples/C++/helloWorld/` or `samples/Python/helloWorld/` | See [Sample Applications](#4.2) |
| **Build custom pipelines** | `demo/utils/pipeline.py` | See [Pipeline Architecture](#5.2) |
| **Contribute code** | `CONTRIBUTING.md` | See [Contributing to TensorRT-RTX](#6.1) |

### Typical First-Time User Flow

```mermaid
flowchart TD
    START["New User"]
    
    DOWNLOAD["Download TensorRT-RTX tarball<br/>from developer.nvidia.com"]
    
    INSTALL["Install wheel:<br/>pip install tensorrt_rtx-*.whl<br/>pip install -r requirements.txt"]
    
    TOKEN["Obtain HuggingFace token<br/>for Flux.1 model access"]
    
    RUN["Run demo:<br/>python flux_demo.py --hf-token TOKEN"]
    
    FIRST_RUN["First Run:<br/>Download models (~40GB)<br/>Build TensorRT engines (~10min)<br/>Generate image"]
    
    CACHED_RUN["Subsequent Runs:<br/>Load cached engines<br/>Generate image (~30s)"]
    
    START --> DOWNLOAD
    DOWNLOAD --> INSTALL
    INSTALL --> TOKEN
    TOKEN --> RUN
    RUN --> FIRST_RUN
    FIRST_RUN --> CACHED_RUN
```

**Sources:** [demo/README.md:7-32](), [demo/README.md:42-46]()

## CI/CD Workflow

The automated build and test pipeline ensures code quality before merging:

```mermaid
graph LR
    subgraph "CI Jobs"
        BUILD["build-linux<br/>Ubuntu 24.04<br/>CUDA 12.9 devel"]
        LINT["lint<br/>Ubuntu 22.04<br/>pre-commit hooks"]
        TEST["test-linux<br/>RTX 4090 GPU<br/>CUDA 12.9 runtime"]
    end
    
    subgraph "Build Artifacts"
        CPP_BIN["C++ binaries<br/>build/"]
    end
    
    subgraph "Scripts"
        BUILD_PY[".github/workflows/build.py<br/>Downloads TensorRT-RTX<br/>Runs CMake"]
        TEST_PY[".github/workflows/test.py<br/>Runs C++ samples<br/>Runs pytest"]
        UTILS_PY[".github/workflows/utils.py<br/>Helper functions"]
    end
    
    BUILD -->|"executes"| BUILD_PY
    BUILD_PY -->|"produces"| CPP_BIN
    BUILD -->|"uploads"| CPP_BIN
    
    CPP_BIN -->|"downloads"| TEST
    TEST -->|"executes"| TEST_PY
    TEST_PY -->|"runs"| CPP_BIN
    
    LINT -->|"validates"| ALL["All source files"]
    
    BUILD -.->|"must complete"| TEST
```

The `build-linux` job runs independently, while `test-linux` depends on its completion to download artifacts. The `lint` job runs in parallel to provide fast feedback on code style issues.

**Sources:** [.github/workflows/ci.yaml:12-54](), [.github/workflows/ci.yaml:56-92]()

## Precision and GPU Architecture Support

TensorRT-RTX supports multiple precision modes tailored to specific GPU architectures:

| Precision | GPU Architecture | VRAM Usage (Default) | VRAM Usage (Low-VRAM) | Code Reference |
|-----------|------------------|----------------------|-----------------------|----------------|
| BF16 | Ampere, Ada, Blackwell | 32.1 GB | 23.1 GB | `--precision bf16` |
| FP8 | Ada, Blackwell | 21.6 GB | 12.0 GB | `--precision fp8` (default) |
| FP4 | Blackwell | 20.5 GB | 11.0 GB | `--precision fp4` |

The precision is configured at engine load time via the `transformer_precision` parameter in `FluxPipeline.load_engines()` or through the `--precision` command-line flag in `flux_demo.py`.

**Sources:** [demo/README.md:120-163]()

## Cache Management Strategy

The demonstration system implements a two-level caching strategy:

1. **Disk Cache** (`demo_cache/`): Stores ONNX models and compiled TensorRT engines, organized by model ID and precision
2. **Runtime Cache** (`runtime.cache`): Stores JIT-compiled CUDA kernels for faster subsequent runs

Cache modes control disk space usage:
- **`full`** (default): Retains all cached models and engines
- **`lean`**: Automatically removes unused models to save disk space

The cache directory structure is defined in the `CacheManager` class and tracked via `.cache_state.json`.

**Sources:** [demo/README.md:70-75](), [demo/README.md:189-200](), [demo/README.md:217-220]()

---

