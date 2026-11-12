<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/TensorRT-RTX · page 2 Getting Started · fetched 2026-10-26 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/utils.py](.github/workflows/utils.py)
- [demo/README.md](demo/README.md)
- [demo/tests/README.md](demo/tests/README.md)

</details>



This page provides an overview of how to set up and begin using TensorRT-RTX. It covers prerequisites, system requirements, and the general workflow for getting your first example running. For detailed installation instructions, see [Installation](#2.1). For a step-by-step tutorial on running the Flux.1 demo, see [Quick Start Guide](#2.2).

## Purpose and Scope

This section guides you through:
- Understanding system prerequisites and requirements
- Overview of the installation process
- Understanding the repository structure relevant to getting started
- General workflow from installation to running your first inference

For information about the CI/CD system and automated builds, see [CI/CD System](#3). For detailed API usage and extending the framework, see [Core Framework](#5).

## Prerequisites

### Hardware Requirements

TensorRT-RTX requires an NVIDIA GPU with specific architecture support:

| Component | Requirement |
|-----------|-------------|
| **GPU Architecture** | Ada (RTX 40 series) or Blackwell required for FP8/FP4 precision<br/>Ampere (RTX 30 series) supported for BF16 precision only |
| **CUDA Version** | CUDA 12.9 or compatible |
| **Minimum VRAM** | 11 GB (with `--low-vram` and `--precision fp4` on Blackwell)<br/>12 GB recommended for FP8 precision<br/>23+ GB for BF16 precision |

### Software Requirements

| Component | Requirement |
|-----------|-------------|
| **Python Version** | 3.9, 3.10, 3.11, or 3.12 |
| **Operating System** | Linux (Ubuntu 22.04/24.04 tested)<br/>Windows (supported) |
| **TensorRT-RTX Binary** | Version 1.3.0.35 or later |

Sources: [demo/README.md:9-9](), [demo/README.md:125-157]()

## Installation Overview

The TensorRT-RTX installation process consists of three main steps:

```mermaid
graph TD
    DOWNLOAD["1. Download TensorRT-RTX Binary<br/>from developer.nvidia.com"]
    EXTRACT["2. Extract Archive<br/>Contains: libraries, Python wheels, headers"]
    INSTALL["3. Install Python Wheel<br/>tensorrt_rtx-1.3.0.35-cp3XX-*.whl"]
    DEPS["4. Install Demo Dependencies<br/>requirements.txt"]
    
    DOWNLOAD --> EXTRACT
    EXTRACT --> INSTALL
    INSTALL --> DEPS
    
    EXTRACT -.->|"C++ Development"| HEADERS["Include headers:<br/>/opt/tensorrt_rtx/include"]
    EXTRACT -.->|"C++ Development"| LIBS["Link libraries:<br/>/opt/tensorrt_rtx/lib"]
```

**Installation Workflow**

The binary package available from NVIDIA contains:
- Python wheels for different Python versions and platforms
- C++ headers and shared libraries
- Sample applications
- Documentation

Sources: [.github/workflows/utils.py:26-30](), [demo/README.md:7-22]()

## Repository Structure for Getting Started

After cloning the repository, the key directories for getting started are:

```mermaid
graph TB
    ROOT["TensorRT-RTX/<br/>(Repository Root)"]
    
    DEMO["demo/<br/>Demonstration applications"]
    FLUX["demo/flux1.dev/<br/>Flux.1 text-to-image demo"]
    UTILS["demo/utils/<br/>Core framework utilities"]
    SAMPLES["samples/<br/>Minimal API examples"]
    
    FLUX_SCRIPT["flux_demo.py<br/>CLI entry point"]
    FLUX_NB["flux_demo.ipynb<br/>Interactive notebook"]
    FLUX_PIPE["flux_pipeline.py<br/>FluxPipeline implementation"]
    FLUX_REQ["requirements.txt<br/>Demo dependencies"]
    
    ENGINE["engine.py<br/>Engine class for TRT management"]
    PIPELINE["pipeline.py<br/>Abstract Pipeline base class"]
    
    CPP_SAMPLES["cpp/<br/>C++ samples"]
    PY_SAMPLES["python/<br/>Python samples"]
    
    ROOT --> DEMO
    ROOT --> SAMPLES
    
    DEMO --> FLUX
    DEMO --> UTILS
    
    FLUX --> FLUX_SCRIPT
    FLUX --> FLUX_NB
    FLUX --> FLUX_PIPE
    FLUX --> FLUX_REQ
    
    UTILS --> ENGINE
    UTILS --> PIPELINE
    
    SAMPLES --> CPP_SAMPLES
    SAMPLES --> PY_SAMPLES
```

**Key Components**

| Path | Purpose |
|------|---------|
| `demo/flux1.dev/` | Complete text-to-image generation demo showcasing TensorRT-RTX features |
| `demo/utils/engine.py` | `Engine` class managing TensorRT engine lifecycle |
| `demo/utils/pipeline.py` | `Pipeline` base class for building inference pipelines |
| `samples/cpp/` | Minimal C++ examples demonstrating API usage |
| `samples/python/` | Minimal Python examples demonstrating API usage |

Sources: [demo/README.md:1-3](), [demo/flux1.dev/flux_demo.py](), [demo/utils/engine.py](), [demo/utils/pipeline.py]()

## Getting Started Workflow

The typical workflow for getting started with TensorRT-RTX follows these stages:

```mermaid
sequenceDiagram
    participant User
    participant Install as "Installation Process"
    participant Demo as "flux_demo.py"
    participant Pipeline as "FluxPipeline"
    participant Engine as "Engine Class"
    participant TRT as "TensorRT-RTX Runtime"
    
    User->>Install: 1. Download & install<br/>TensorRT-RTX wheel
    Install-->>User: Python package available
    
    User->>Install: 2. Install demo dependencies<br/>pip install -r requirements.txt
    Install-->>User: Dependencies ready
    
    User->>Demo: 3. Run demo<br/>python flux_demo.py --hf-token TOKEN
    
    Demo->>Pipeline: Initialize FluxPipeline
    Pipeline->>Engine: Load/build TensorRT engines
    Engine->>TRT: Build or load cached engines
    TRT-->>Engine: Engines ready
    Engine-->>Pipeline: All components initialized
    
    Pipeline->>Engine: Execute inference<br/>(text encoding → denoising → decoding)
    Engine->>TRT: Run TensorRT inference
    TRT-->>Engine: Inference results
    Engine-->>Pipeline: Latents/embeddings
    
    Pipeline-->>Demo: Generated image
    Demo-->>User: output.png saved
```

**Workflow Stages**

1. **Installation** ([See Installation](#2.1))
   - Download TensorRT-RTX binary package from `developer.nvidia.com`
   - Install the Python wheel matching your Python version and OS
   - Install demo-specific dependencies

2. **First Run** ([See Quick Start Guide](#2.2))
   - Execute `flux_demo.py` with required Hugging Face token
   - Pipeline downloads model weights from Hugging Face Hub (first run only)
   - TensorRT engines are built and cached (first run only)
   - Image generation occurs

3. **Subsequent Runs**
   - Cached engines are loaded from `demo_cache/`
   - No recompilation needed unless configuration changes
   - Faster startup and inference

Sources: [demo/README.md:7-32](), [.github/workflows/utils.py:44-69]()

## Component Interaction for First Inference

Understanding how the components interact helps clarify the setup requirements:

```mermaid
graph TB
    subgraph "User Environment"
        USER_SCRIPT["flux_demo.py<br/>--hf-token TOKEN<br/>--prompt 'A cat in space'"]
    end
    
    subgraph "TensorRT-RTX Package"
        TRTRTX_MODULE["tensorrt_rtx Python module<br/>(from installed wheel)"]
    end
    
    subgraph "Demo Framework"
        FLUX_PIPELINE["FluxPipeline class<br/>demo/flux1.dev/flux_pipeline.py"]
        ENGINE_MGR["Engine class<br/>demo/utils/engine.py"]
    end
    
    subgraph "External Resources"
        HF_HUB["Hugging Face Hub<br/>black-forest-labs/FLUX.1-dev<br/>(model weights)"]
        CACHE["Local Cache<br/>demo_cache/<br/>(ONNX models + TRT engines)"]
    end
    
    subgraph "Runtime"
        TRT_ENGINE["TensorRT Engine<br/>(GPU execution)"]
        GPU["NVIDIA GPU<br/>(Ada/Blackwell for FP8/FP4)"]
    end
    
    USER_SCRIPT --> FLUX_PIPELINE
    FLUX_PIPELINE --> ENGINE_MGR
    ENGINE_MGR --> TRTRTX_MODULE
    
    FLUX_PIPELINE -.->|"First run:<br/>downloads weights"| HF_HUB
    ENGINE_MGR -.->|"First run:<br/>builds engines"| CACHE
    ENGINE_MGR -->|"Load cached<br/>engines"| CACHE
    
    TRTRTX_MODULE --> TRT_ENGINE
    TRT_ENGINE --> GPU
```

**Component Roles**

| Component | Role | Required for First Run |
|-----------|------|------------------------|
| `tensorrt_rtx` module | Core TensorRT-RTX runtime providing inference APIs | Yes - must be installed |
| `FluxPipeline` | High-level pipeline orchestrating text-to-image generation | Yes - part of demo |
| `Engine` class | Manages TensorRT engine lifecycle (build, load, execute) | Yes - part of demo |
| Hugging Face Hub | Source of pre-trained model weights | Yes - requires `--hf-token` |
| Local cache | Stores ONNX models and compiled TensorRT engines | Created automatically |

Sources: [demo/README.md:7-22](), [demo/flux1.dev/flux_demo.py](), [demo/utils/engine.py](), [demo/utils/pipeline.py]()

## Installation Artifacts and Locations

Understanding where components are installed helps with troubleshooting:

```mermaid
graph TB
    subgraph "TensorRT-RTX Binary Package"
        TAR["TensorRT-RTX-1.3.0.35-Linux-x86_64-cuda-12.9-Release-external.tar.gz<br/>Download from developer.nvidia.com"]
    end
    
    subgraph "Extracted Contents"
        PYTHON_DIR["python/<br/>Python wheels"]
        INCLUDE_DIR["include/<br/>C++ headers"]
        LIB_DIR["lib/<br/>Shared libraries"]
        SAMPLES_DIR["samples/<br/>Example code"]
    end
    
    subgraph "Python Environment"
        SITE_PACKAGES["site-packages/tensorrt_rtx/<br/>Installed Python module"]
    end
    
    subgraph "System Installation (Optional)"
        OPT_DIR["/opt/tensorrt_rtx/<br/>System-wide installation<br/>(CI/CD uses this)"]
    end
    
    subgraph "Demo Cache (Created at Runtime)"
        DEMO_CACHE["demo_cache/<br/>├── shared/onnx/<br/>├── shared/engines/<br/>├── runtime.cache<br/>└── .cache_state.json"]
    end
    
    TAR --> PYTHON_DIR
    TAR --> INCLUDE_DIR
    TAR --> LIB_DIR
    TAR --> SAMPLES_DIR
    
    PYTHON_DIR -.->|"pip install *.whl"| SITE_PACKAGES
    
    TAR -.->|"Optional: extract to"| OPT_DIR
    
    SITE_PACKAGES -.->|"First demo run creates"| DEMO_CACHE
```

**Installation Paths**

| Path | Description | Set By |
|------|-------------|--------|
| `TRT_RTX_BASE_URL` | Download URL for binary package | [.github/workflows/utils.py:26]() |
| `TRTRTX_INSTALL_DIR` | System installation directory (CI default: `/opt/tensorrt_rtx`) | [.github/workflows/utils.py:30]() |
| `site-packages/tensorrt_rtx/` | Python module location after `pip install` | Python package manager |
| `demo_cache/` | Runtime cache for models and engines | [demo/README.md:73]() via `--cache-dir` |

Sources: [.github/workflows/utils.py:26-31](), [demo/README.md:73-74](), [demo/README.md:189-200]()

## Environment Variables

Key environment variables used by TensorRT-RTX:

| Variable | Purpose | Default | Set In |
|----------|---------|---------|--------|
| `TRT_RTX_FILENAME` | Name of TensorRT-RTX archive file | `TensorRT-RTX-1.3.0.35-Linux-x86_64-cuda-12.9-Release-external.tar.gz` | [.github/workflows/utils.py:27-29]() |
| `TRTRTX_INSTALL_DIR` | Installation directory for TensorRT-RTX | `/opt/tensorrt_rtx` | [.github/workflows/utils.py:30]() |
| `BUILD_DIR` | Build output directory for C++ samples | `build` | [.github/workflows/utils.py:31]() |
| `CACHE_TRT_RTX_HIT` | Skip download if cache exists | `false` | [.github/workflows/utils.py:46]() |

Sources: [.github/workflows/utils.py:25-31]()

## Next Steps

Once you understand the prerequisites and architecture:

1. **Install TensorRT-RTX** - Follow detailed instructions in [Installation](#2.1)
   - Download the binary package
   - Install the Python wheel
   - Verify installation

2. **Run Your First Example** - Follow the [Quick Start Guide](#2.2)
   - Set up Hugging Face authentication
   - Run the Flux.1 demo
   - Explore configuration options

3. **Explore Further**
   - Learn about [Flux Demo Configuration](#4.1.1) for advanced options
   - Understand [Engine Management](#5.1) for custom applications
   - Review [Sample Applications](#4.2) for minimal examples

## Common Setup Issues

| Issue | Solution | Reference |
|-------|----------|-----------|
| Python version incompatibility | Use Python 3.9-3.12 | [demo/README.md:9]() |
| GPU architecture mismatch | Verify precision support for your GPU (FP8 requires Ada/Blackwell) | [demo/README.md:125-157]() |
| Missing dependencies | Install demo requirements: `pip install -r demo/flux1.dev/requirements.txt` | [demo/README.md:21]() |
| CUDA version mismatch | Ensure CUDA 12.9 or compatible version is installed | [.github/workflows/utils.py:28]() |
| Insufficient VRAM | Use `--low-vram` flag and lower precision (FP8 or FP4) | [demo/README.md:66](), [demo/README.md:210-215]() |

Sources: [demo/README.md:9-10](), [demo/README.md:38](), [demo/README.md:202-226]()

---

