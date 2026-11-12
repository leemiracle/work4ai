> 来源: [https://deepwiki.com/sgl-project/sglang/2-installation-and-deployment](https://deepwiki.com/sgl-project/sglang/2-installation-and-deployment)
> DeepWiki sgl-project/sglang | Last indexed: 27 Aug 2026 (94183a)

# Installation and Deployment

  Relevant source files 
 - [.github/workflows/release-docker-amd-nightly.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-docker-amd-nightly.yml)
 - [.github/workflows/release-docker-amd-rocm720-nightly.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-docker-amd-rocm720-nightly.yml)
 - [.github/workflows/release-docker-amd-rocm7_15-nightly.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-docker-amd-rocm7_15-nightly.yml)
 - [.github/workflows/release-docker-amd.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-docker-amd.yml)
 - [3rdparty/amd/wheel/sglang/pyproject.toml](https://github.com/sgl-project/sglang/blob/94183a8d/3rdparty/amd/wheel/sglang/pyproject.toml)
 - [benchmark/deepseek_v3/README.md](https://github.com/sgl-project/sglang/blob/94183a8d/benchmark/deepseek_v3/README.md?plain=1)
 - [docker/Dockerfile](https://github.com/sgl-project/sglang/blob/94183a8d/docker/Dockerfile)
 - [docker/rocm.Dockerfile](https://github.com/sgl-project/sglang/blob/94183a8d/docker/rocm.Dockerfile)
 - [docker/xeon.Dockerfile](https://github.com/sgl-project/sglang/blob/94183a8d/docker/xeon.Dockerfile)
 - [python/pyproject.toml](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject.toml)
 - [python/pyproject_cpu.toml](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject_cpu.toml)
 - [python/pyproject_npu.toml](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject_npu.toml)
 - [python/pyproject_other.toml](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject_other.toml)
 - [python/pyproject_xpu.toml](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject_xpu.toml)
 - [python/sglang/multimodal_gen/__init__.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/__init__.py)
 - [python/sglang/srt/entrypoints/engine.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py)
 - [python/sglang/srt/layers/moe/moe_runner/base.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/moe_runner/base.py)
 - [python/sglang/srt/layers/moe/token_dispatcher/moriep.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/token_dispatcher/moriep.py)
 - [python/sglang/srt/utils/common.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/common.py)
 - [python/sglang/version.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/version.py)
 - [scripts/ci/amd/amd_ci_install_dependency.sh](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/amd/amd_ci_install_dependency.sh)
 - [scripts/ci/amd/amd_ci_start_container.sh](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/amd/amd_ci_start_container.sh)
 - [scripts/ci/amd/amd_ci_start_container_disagg.sh](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/amd/amd_ci_start_container_disagg.sh)
 - [scripts/ci/cuda/ci_download_flashinfer_jit_cache.sh](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/cuda/ci_download_flashinfer_jit_cache.sh)
 - [scripts/ci/cuda/ci_install_dependency.sh](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/cuda/ci_install_dependency.sh)
 - [scripts/ci/utils/install_protoc.sh](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/utils/install_protoc.sh)
 - [scripts/ci/utils/install_rust_protoc.sh](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/utils/install_rust_protoc.sh)
 - [scripts/ci/utils/install_rustup.sh](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/utils/install_rustup.sh)
 - [sgl-model-gateway/rust-toolchain.toml](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/rust-toolchain.toml)
 - [test/registered/unit/tools/test_amd_ci_install_dependency.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/tools/test_amd_ci_install_dependency.py)
 - [test/registered/unit/tools/test_get_version_tag.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/tools/test_get_version_tag.py)
 
  This document provides a high-level overview of the installation methods, platform-specific hardware configuration, Docker-based deployment, and multi-node distributed deployment scenarios for SGLang. It introduces the main package layout, build configurations, and runtime deployment patterns, linking to more detailed child pages for each sub-topic.

 
---

 
## Package Architecture Overview

 SGLang is distributed as two primary components with distinct build systems:

 
 - **Python package**: The core framework, including runtime modules (`sglang.srt.*`), managers (`TokenizerManager`, `Scheduler`, `DetokenizerManager`), HTTP server interfaces, and CLI entrypoints.
 - **Native kernel library** (`sgl-kernel`): Highly optimized C++ and CUDA/ROCm kernels for attention, MoE, quantization, and other performance-sensitive operations, built using CMake and scikit-build-core.
 
 These components have their own dependency sets and build processes. The Python package depends on `torch`, `flashinfer-python`, `sgl-deep-gemm`, and other high-performance libraries [python/pyproject.toml18-94](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject.toml#L18-L94) The native kernel integrates with CUTLASS and similar GPU libs [python/pyproject.toml49-50](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject.toml#L49-L50)

 
### System Component Map

 The following diagram bridges the high-level system names to the specific code entities that implement them.

 
```

```

 **Sources:** [python/pyproject.toml5-94](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject.toml#L5-L94) [python/pyproject.toml202-203](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject.toml#L202-L203) [python/sglang/srt/entrypoints/engine.py207-210](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L207-L210) [python/sglang/srt/managers/tokenizer_manager.py158-160](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L158-L160)

 
---

 
## Installation Method Overview

 SGLang supports various installation paths that target different use cases and hardware platforms. The main methods are:

 
 - **PyPI installation** for standard users on widely supported platforms using `pip install sglang` [python/pyproject.toml6](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject.toml#L6-L6)
 - **Source builds** for development, customization, or less common platforms, often utilizing the `scripts/ci/cuda/ci_install_dependency.sh` script for environment setup.
 - **Docker container images** for simplified deployment in isolated or production environments, managed via `docker/Dockerfile`.
 - **Kubernetes-native deployments** for scaling multi-node fleets with the `llm-d` orchestration system and the `sgl-model-gateway`.
 
 
```

```

 For detailed instructions on each method, see the child page: [Installation Methods](https://deepwiki.com/sgl-project/sglang/2.1-installation-methods).

 **Sources:** [python/pyproject.toml201-203](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject.toml#L201-L203) [scripts/ci/cuda/ci_install_dependency.sh30-76](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/cuda/ci_install_dependency.sh#L30-L76)

 
---

 
## Hardware Platform Configuration

 SGLang features extensive platform detection and configuration support via the `sglang.srt.platforms` and `sglang.srt.utils.common` modules [python/sglang/srt/utils/common.py130-230](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/common.py#L130-L230) Supported hardware backends include:

 
 - **NVIDIA CUDA**: Multi-architecture support (SM90, SM100) with extensive optimization via `cuda-python` and `flashinfer` [python/sglang/srt/utils/common.py149-151](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/common.py#L149-L151)
 - **AMD ROCm**: Support for GPU architectures like `gfx942`, `gfx950` detected through `is_hip()` [python/sglang/srt/utils/common.py132-134](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/common.py#L132-L134)
 - **Huawei NPU**: Detected via `is_npu()` and conditioned on torch_npu availability [python/sglang/srt/utils/common.py180-189](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/common.py#L180-L189)
 - **Intel XPU and Host CPUs**: Support for Intel GPUs and Xeon CPUs with AMX, detected using `is_xpu()` and `is_cpu()` respectively [python/sglang/srt/utils/common.py164-165](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/common.py#L164-L165) [python/sglang/srt/utils/common.py212-214](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/common.py#L212-L214)
 - **Apple Silicon (MPS)**: Support via `is_mps()` and associated platform-specific dependencies for MLX-based accelerators [python/sglang/srt/utils/common.py227-228](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/common.py#L227-L228)
 
 Platform configuration involves detecting device types at runtime and adjusting dependencies and runtime behavior accordingly. The system environment and platform metadata also inform which optional extensions are loaded.

 For deeper explanation of platform-specific dependencies and configuration, see [Hardware Platform Configuration](https://deepwiki.com/sgl-project/sglang/2.2-hardware-platform-configuration).

 **Sources:** [python/sglang/srt/utils/common.py127-229](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/common.py#L127-L229) [python/sglang/srt/server_args.py143-179](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L143-L179)

 
---

 
## Docker Deployment

 SGLang maintains a sophisticated multi-stage Docker build system in `docker/Dockerfile` targeting different hardware platforms and configurations.

 
### Multi-Stage Build Pipeline Overview

 
 - **Base Stage**: Starts from an NVIDIA CUDA image (e.g., `nvidia/cuda:13.0.3-cudnn-devel-ubuntu24.04`) [docker/Dockerfile1-2](https://github.com/sgl-project/sglang/blob/94183a8d/docker/Dockerfile#L1-L2) It installs core system utilities, Python 3.12, and essential tools.
 - **Torch Dependencies Stage**: Installs Rust toolchain for building Rust extensions, and installs pre-built `sgl-kernel` wheels aligned with CUDA version [docker/Dockerfile170-202](https://github.com/sgl-project/sglang/blob/94183a8d/docker/Dockerfile#L170-L202)
 - **Final Framework Stage**: Combines sources and dependencies for the runtime and user entrypoints.
 
 
### Hardware Specific Dockerfiles

 
 - CUDA-based GPU image: `docker/Dockerfile` (the main image supporting NVIDIA GPUs).
 - ROCm (AMD GPUs): Separate ROCm Dockerfiles (`docker/rocm.Dockerfile`) with variants for different ROCm and GPU architectures (e.g., gfx942, gfx950) [docker/rocm.Dockerfile1-140](https://github.com/sgl-project/sglang/blob/94183a8d/docker/rocm.Dockerfile#L1-L140)
 - Other architectures, e.g., NPU or Intel Xeon builds, handled with separate Dockerfiles (`docker/npu.Dockerfile`, `docker/xeon.Dockerfile`), following similar multi-stage patterns.
 
 
### Image Variants and Build Arguments

 Docker builds allow selecting CUDA/ROCm versions, GPU architectures, and enabling optional features such as MoRI (MoE RDMA backend) and NIXL (disaggregation) at build time using build arguments.

 For deployment best practices, image variants, and multi-stage build details, see [Docker Deployment](https://deepwiki.com/sgl-project/sglang/2.3-docker-deployment).

 **Sources:** [docker/Dockerfile1-130](https://github.com/sgl-project/sglang/blob/94183a8d/docker/Dockerfile#L1-L130) [docker/Dockerfile170-202](https://github.com/sgl-project/sglang/blob/94183a8d/docker/Dockerfile#L170-L202) [docker/rocm.Dockerfile1-140](https://github.com/sgl-project/sglang/blob/94183a8d/docker/rocm.Dockerfile#L1-L140)

 
---

 
## Multi-Node and Distributed Deployment

 SGLang supports scalable multi-node serving with advanced distributed execution strategies orchestrated by the `Engine` [python/sglang/srt/entrypoints/engine.py207-210](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L207-L210)

 
### Key Distributed Features

 
 - **Parallelism**: Configurable degrees of Tensor Parallelism (`tp_size`), Pipeline Parallelism (`pp_size`), and Expert Parallelism (`ep_size`) enable scaling model inference across multiple devices and nodes [python/sglang/srt/server_args.py44-49](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L44-L49)
 - **Communication**: Initialization of distributed groups via `torch.distributed.init_process_group` and inter-process communication using ZeroMQ sockets among `TokenizerManager`, `Scheduler`, and `DetokenizerManager` [python/sglang/srt/managers/tokenizer_manager.py124-142](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L124-L142)
 - **Disaggregation**: Supports prefill-decode disaggregation, leveraging backends like `Mooncake` and `NIXL` for remote KV cache transfer during inference [python/sglang/srt/server_args.py53-55](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L53-L55)
 - **Orchestration and Routing**: Kubernetes-native fleet orchestration is supported through the `llm-d` system, which enables prefix-aware request routing and distributed KV-cache management.
 - **Routing Systems**: Rust-based routing components such as `sgl-router` and `sgl-model-gateway` manage request distribution and offer high-performance controls for multi-model serving.
 
 For in-depth description of multi-node setup, initialization protocols, and network configuration, see [Multi-Node and Distributed Deployment](https://deepwiki.com/sgl-project/sglang/2.4-multi-node-and-distributed-deployment).

 **Sources:** [python/sglang/srt/entrypoints/engine.py60-154](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L60-L154) [python/sglang/srt/server_args.py30-101](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L30-L101) [python/sglang/srt/managers/tokenizer_manager.py124-142](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L124-L142)

 
---

 
## Deployment Architecture Overview Diagram

 This diagram illustrates the relationship between natural language system components you interact with and their corresponding code entities within the SGLang runtime and deployment setup.

 
```

```

 **Sources:** [python/sglang/srt/entrypoints/engine.py60-154](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L60-L154) [python/pyproject.toml201-203](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject.toml#L201-L203) [docker/Dockerfile170-202](https://github.com/sgl-project/sglang/blob/94183a8d/docker/Dockerfile#L170-L202)

 
---

 This page serves as a high-level gateway to installation and deployment topics. More technical detail and step-by-step setup instructions are covered on these child pages:

 
 - [Installation Methods](https://deepwiki.com/sgl-project/sglang/2.1-installation-methods) — PyPI install, source builds, and platform-specific install procedures.
 - [Hardware Platform Configuration](https://deepwiki.com/sgl-project/sglang/2.2-hardware-platform-configuration) — Automatic platform detection, CUDA/ROCm/NPU/XPU/MLX support, platform dependencies.
 - [Docker Deployment](https://deepwiki.com/sgl-project/sglang/2.3-docker-deployment) — Docker image variants, multi-stage Docker builds, container runtime deployment.
 - [Multi-Node and Distributed Deployment](https://deepwiki.com/sgl-project/sglang/2.4-multi-node-and-distributed-deployment) — Multi-node setup, distributed initialization, network config, Kubernetes native routing via llm-d.
 
 
---

 **Sources:**

 
 - [python/pyproject.toml5-94](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject.toml#L5-L94)
 - [python/pyproject.toml201-203](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject.toml#L201-L203)
 - [python/sglang/srt/server_args.py30-101](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L30-L101)
 - [python/sglang/srt/server_args.py143-179](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L143-L179)
 - [python/sglang/srt/utils/common.py127-224](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/common.py#L127-L224)
 - [docker/Dockerfile1-130](https://github.com/sgl-project/sglang/blob/94183a8d/docker/Dockerfile#L1-L130)
 - [docker/Dockerfile170-202](https://github.com/sgl-project/sglang/blob/94183a8d/docker/Dockerfile#L170-L202)
 - [python/sglang/srt/entrypoints/engine.py60-154](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L60-L154)
 - [python/sglang/srt/entrypoints/engine.py207-210](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py#L207-L210)
 - [python/sglang/srt/managers/tokenizer_manager.py124-142](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L124-L142)
 - [python/sglang/srt/managers/tokenizer_manager.py158-160](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L158-L160)
