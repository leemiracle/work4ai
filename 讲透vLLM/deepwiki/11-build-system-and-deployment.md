# Build System and Deployment

> 来源: https://deepwiki.com/vllm-project/vllm/11-build-system-and-deployment 抓取日期: 2026-09-02
> 章节: 第 11 章 构建系统与部署

---

Relevant source files

  * [.buildkite/ci_config_rocm.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/ci_config_rocm.yaml)
  * [.buildkite/hardware_tests/amd.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/hardware_tests/amd.yaml)
  * [.buildkite/image_build/image_build_arm64.sh](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/image_build/image_build_arm64.sh)
  * [.buildkite/image_build/image_build_torch_nightly.sh](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/image_build/image_build_torch_nightly.sh)
  * [.buildkite/release-pipeline.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/release-pipeline.yaml)
  * [.buildkite/scripts/build-macos-wheel.sh](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/scripts/build-macos-wheel.sh)
  * [.buildkite/scripts/ci-bake-rocm.sh](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/scripts/ci-bake-rocm.sh)
  * [.buildkite/scripts/generate-nightly-index.py](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/scripts/generate-nightly-index.py)
  * [.buildkite/scripts/hardware_ci/run-amd-test.sh](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/scripts/hardware_ci/run-amd-test.sh)
  * [.buildkite/scripts/hardware_ci/run-gh200-test.sh](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/scripts/hardware_ci/run-gh200-test.sh)
  * [.buildkite/scripts/rocm/build-ci-base.sh](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/scripts/rocm/build-ci-base.sh)
  * [.buildkite/scripts/rocm/build-test-image.sh](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/scripts/rocm/build-test-image.sh)
  * [.buildkite/scripts/rocm/refresh-base-image.sh](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/scripts/rocm/refresh-base-image.sh)
  * [.buildkite/scripts/rocm/smoke-test-image.sh](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/scripts/rocm/smoke-test-image.sh)
  * [.buildkite/scripts/run-rust-frontend-cargo-ci.sh](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/scripts/run-rust-frontend-cargo-ci.sh)
  * [README.md](https://github.com/vllm-project/vllm/blob/185cada3/README.md?plain=1)
  * [docker/Dockerfile](https://github.com/vllm-project/vllm/blob/185cada3/docker/Dockerfile)
  * [docker/Dockerfile.cpu](https://github.com/vllm-project/vllm/blob/185cada3/docker/Dockerfile.cpu)
  * [docker/Dockerfile.rocm](https://github.com/vllm-project/vllm/blob/185cada3/docker/Dockerfile.rocm)
  * [docker/Dockerfile.rocm_gfx1250](https://github.com/vllm-project/vllm/blob/185cada3/docker/Dockerfile.rocm_gfx1250)
  * [docker/Dockerfile.xpu](https://github.com/vllm-project/vllm/blob/185cada3/docker/Dockerfile.xpu)
  * [docker/ci-rocm.hcl](https://github.com/vllm-project/vllm/blob/185cada3/docker/ci-rocm.hcl)
  * [docker/docker-bake-rocm.hcl](https://github.com/vllm-project/vllm/blob/185cada3/docker/docker-bake-rocm.hcl)
  * [docker/versions.json](https://github.com/vllm-project/vllm/blob/185cada3/docker/versions.json)
  * [docs/README.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/README.md?plain=1)
  * [docs/assets/contributing/dockerfile-stages-dependency.png](https://github.com/vllm-project/vllm/blob/185cada3/docs/assets/contributing/dockerfile-stages-dependency.png)
  * [docs/community/meetups.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/community/meetups.md?plain=1)
  * [docs/community/sponsors.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/community/sponsors.md?plain=1)
  * [docs/contributing/dockerfile/dockerfile.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/contributing/dockerfile/dockerfile.md?plain=1)
  * [docs/contributing/model/basic.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/contributing/model/basic.md?plain=1)
  * [docs/deployment/docker.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/deployment/docker.md?plain=1)
  * [docs/getting_started/installation/.nav.yml](https://github.com/vllm-project/vllm/blob/185cada3/docs/getting_started/installation/.nav.yml)
  * [docs/getting_started/installation/README.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/getting_started/installation/README.md?plain=1)
  * [docs/getting_started/installation/gpu.apple.inc.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/getting_started/installation/gpu.apple.inc.md?plain=1)
  * [docs/getting_started/installation/gpu.cuda.inc.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/getting_started/installation/gpu.cuda.inc.md?plain=1)
  * [docs/getting_started/installation/gpu.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/getting_started/installation/gpu.md?plain=1)
  * [docs/getting_started/installation/gpu.rocm.inc.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/getting_started/installation/gpu.rocm.inc.md?plain=1)
  * [docs/getting_started/installation/gpu.xpu.inc.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/getting_started/installation/gpu.xpu.inc.md?plain=1)
  * [docs/getting_started/installation/python_env_setup.inc.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/getting_started/installation/python_env_setup.inc.md?plain=1)
  * [docs/getting_started/quickstart.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/getting_started/quickstart.md?plain=1)
  * [pyproject.toml](https://github.com/vllm-project/vllm/blob/185cada3/pyproject.toml)
  * [requirements/common.txt](https://github.com/vllm-project/vllm/blob/185cada3/requirements/common.txt)
  * [requirements/cpu.txt](https://github.com/vllm-project/vllm/blob/185cada3/requirements/cpu.txt)
  * [requirements/cuda.txt](https://github.com/vllm-project/vllm/blob/185cada3/requirements/cuda.txt)
  * [requirements/rocm.txt](https://github.com/vllm-project/vllm/blob/185cada3/requirements/rocm.txt)
  * [requirements/test/cpu.txt](https://github.com/vllm-project/vllm/blob/185cada3/requirements/test/cpu.txt)
  * [requirements/test/cuda.in](https://github.com/vllm-project/vllm/blob/185cada3/requirements/test/cuda.in)
  * [requirements/test/cuda.txt](https://github.com/vllm-project/vllm/blob/185cada3/requirements/test/cuda.txt)
  * [requirements/test/nightly-torch.txt](https://github.com/vllm-project/vllm/blob/185cada3/requirements/test/nightly-torch.txt)
  * [requirements/test/rocm.in](https://github.com/vllm-project/vllm/blob/185cada3/requirements/test/rocm.in)
  * [requirements/test/rocm.txt](https://github.com/vllm-project/vllm/blob/185cada3/requirements/test/rocm.txt)
  * [requirements/test/xpu.in](https://github.com/vllm-project/vllm/blob/185cada3/requirements/test/xpu.in)
  * [requirements/test/xpu.txt](https://github.com/vllm-project/vllm/blob/185cada3/requirements/test/xpu.txt)
  * [requirements/xpu.txt](https://github.com/vllm-project/vllm/blob/185cada3/requirements/xpu.txt)
  * [setup.py](https://github.com/vllm-project/vllm/blob/185cada3/setup.py)
  * [tests/evals/gpt_oss/configs/gpt-oss-20b-sm120.yaml](https://github.com/vllm-project/vllm/blob/185cada3/tests/evals/gpt_oss/configs/gpt-oss-20b-sm120.yaml)
  * [tests/evals/gpt_oss/configs/models-spark.txt](https://github.com/vllm-project/vllm/blob/185cada3/tests/evals/gpt_oss/configs/models-spark.txt)
  * [tests/standalone_tests/python_only_compile.sh](https://github.com/vllm-project/vllm/blob/185cada3/tests/standalone_tests/python_only_compile.sh)
  * [tests/tools/test_docker_build_metadata_args.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/tools/test_docker_build_metadata_args.py)
  * [tests/v1/kv_connector/unit/test_nixl_rocm_gpu_mem_diag.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/kv_connector/unit/test_nixl_rocm_gpu_mem_diag.py)
  * [tools/pre_commit/update-dockerfile-graph.sh](https://github.com/vllm-project/vllm/blob/185cada3/tools/pre_commit/update-dockerfile-graph.sh)

This page documents how vLLM is built, packaged, and deployed. It covers the Python packaging configuration, the CMake build system for multi-platform extensions (CUDA, ROCm, CPU, XPU), Docker image construction, and dependency management.

For information about environment variables that affect runtime behavior, see [Environment Variables System](/vllm-project/vllm/2.3-environment-variables-system). For information about `torch.compile` integration and compilation modes, see [Compilation Configuration and Optimization Levels](/vllm-project/vllm/2.4-compilation-configuration-and-optimization-levels). For platform-specific runtime details, see [Platform Support](/vllm-project/vllm/10-platform-support).

* * *

## Overview

vLLM has two distinct build phases:

  1. **Native Extension Build** — A CMake-driven compilation of hardware-specific kernels and custom ops into shared libraries (e.g., `_C.so`, `_rocm_C.so`). This handles architecture-specific code generation (e.g., PTX for NVIDIA, GCN for AMD, AVX/AMX for CPU).
  2. **Python Wheel Build** — A standard `setuptools` build that packages the Python source along with the compiled native binaries into a distributable wheel.

The Docker build further separates these phases into parallel stages to minimize rebuild time and optimize image size.

Sources: [setup.py188-210](https://github.com/vllm-project/vllm/blob/185cada3/setup.py#L188-L210) [docker/Dockerfile92-161](https://github.com/vllm-project/vllm/blob/185cada3/docker/Dockerfile#L92-L161)

* * *

## Python Packaging

### setup.py

`setup.py` orchestrates the build by bridging Python's `setuptools` with CMake and Rust build tools. Key classes:

Class| Purpose  
---|---  
`CMakeExtension`| Declares a C++ extension backed by a CMake project [setup.py188-192](https://github.com/vllm-project/vllm/blob/185cada3/setup.py#L188-L192)  
`cmake_build_ext`| Custom `build_ext` command; invokes `cmake` configure and build steps [setup.py194-210](https://github.com/vllm-project/vllm/blob/185cada3/setup.py#L194-L210)  
  
**Target device detection** ([setup.py85-108](https://github.com/vllm-project/vllm/blob/185cada3/setup.py#L85-L108)): The `VLLM_TARGET_DEVICE` environment variable (via `envs.py`) controls what gets compiled. If unset, `setup.py` auto-detects based on `torch.version`:

  * `torch.version.hip is not None` → `"rocm"` [setup.py97-99](https://github.com/vllm-project/vllm/blob/185cada3/setup.py#L97-L99)
  * `torch.version.xpu is not None` → `"xpu"` [setup.py100-102](https://github.com/vllm-project/vllm/blob/185cada3/setup.py#L100-L102)
  * `torch.version.cuda is not None` → `"cuda"` [setup.py103-105](https://github.com/vllm-project/vllm/blob/185cada3/setup.py#L103-L105)
  * macOS or manual override → `"cpu"` [setup.py85-87](https://github.com/vllm-project/vllm/blob/185cada3/setup.py#L85-L87)

**Rust Frontend Integration** : The build system integrates a Rust-based frontend (`vllm-rs`). `setup.py` can use precompiled Rust extensions (e.g., `_rust_*.so`) or trigger a build via `build_rust` [setup.py37-79](https://github.com/vllm-project/vllm/blob/185cada3/setup.py#L37-L79)

**Parallel Compilation Control** : The number of jobs is controlled by `MAX_JOBS` [setup.py201-208](https://github.com/vllm-project/vllm/blob/185cada3/setup.py#L201-L208) For CUDA builds, `NVCC_THREADS` allows further parallelism within a single `nvcc` call [setup.py216-222](https://github.com/vllm-project/vllm/blob/185cada3/setup.py#L216-L222)

Sources: [setup.py1-222](https://github.com/vllm-project/vllm/blob/185cada3/setup.py#L1-L222)

* * *

## CMake Build System

The top-level CMake system builds all native extensions.

### Architecture and ISA Handling

**CUDA architecture sets** : vLLM supports a wide range of compute capabilities. Default architecture list for builds is parameterized via `TORCH_CUDA_ARCH_LIST` [docker/versions.json46-48](https://github.com/vllm-project/vllm/blob/185cada3/docker/versions.json#L46-L48) For release builds, vLLM targets specific SM versions (e.g., 7.5, 8.0, 8.6, 8.9, 9.0, 10.0, 12.0) [.buildkite/release-pipeline.yaml10-18](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/release-pipeline.yaml#L10-L18)

**ROCm architecture sets** : AMD builds target specific GCN architectures and include ROCm-specific dependencies like `amd-quark` and `tilelang` [requirements/rocm.txt24-25](https://github.com/vllm-project/vllm/blob/185cada3/requirements/rocm.txt#L24-L25)

**XPU Support** : Intel GPU builds use a dedicated Dockerfile and requirement set, pinning specific Triton shims and XPU kernels [docker/Dockerfile.xpu135-160](https://github.com/vllm-project/vllm/blob/185cada3/docker/Dockerfile.xpu#L135-L160) [requirements/xpu.txt4-23](https://github.com/vllm-project/vllm/blob/185cada3/requirements/xpu.txt#L4-L23)

### CMake Build Flow Diagram

**Native Extension Build Process**

Sources: [setup.py194-222](https://github.com/vllm-project/vllm/blob/185cada3/setup.py#L194-L222) [docker/versions.json46-57](https://github.com/vllm-project/vllm/blob/185cada3/docker/versions.json#L46-L57) [.buildkite/release-pipeline.yaml10-18](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/release-pipeline.yaml#L10-L18) [requirements/xpu.txt23](https://github.com/vllm-project/vllm/blob/185cada3/requirements/xpu.txt#L23-L23)

* * *

## Dependency Management

vLLM manages its Python dependencies through a structured set of `requirements/*.txt` files. These files are used during both local development and Docker image builds to ensure consistent environments.

For details, see [Dependency Management](/vllm-project/vllm/11.2-dependency-management).

### Requirements File Structure

File| Purpose  
---|---  
`requirements/common.txt`| Shared runtime dependencies including `transformers`, `fastapi`, and `pydantic`.  
`requirements/cuda.txt`| Adds NVIDIA-specific dependencies like `flashinfer-python`, `quack-kernels`, and `torch` [requirements/cuda.txt1-35](https://github.com/vllm-project/vllm/blob/185cada3/requirements/cuda.txt#L1-L35)  
`requirements/rocm.txt`| Adds AMD-specific packages like `amd-quark`, `tilelang`, and `grpcio` [requirements/rocm.txt1-29](https://github.com/vllm-project/vllm/blob/185cada3/requirements/rocm.txt#L1-L29)  
`requirements/xpu.txt`| Adds Intel-specific packages like `vllm_xpu_kernels` and `triton+xpu` [requirements/xpu.txt1-23](https://github.com/vllm-project/vllm/blob/185cada3/requirements/xpu.txt#L1-L23)  
  
### Key Pinned Versions

Package| Pinned Version| Source  
---|---|---  
`torch` (CUDA/XPU)| 2.13.0| [requirements/cuda.txt7](https://github.com/vllm-project/vllm/blob/185cada3/requirements/cuda.txt#L7-L7) [requirements/xpu.txt17](https://github.com/vllm-project/vllm/blob/185cada3/requirements/xpu.txt#L17-L17)  
`flashinfer-python`| 0.6.17| [requirements/cuda.txt17](https://github.com/vllm-project/vllm/blob/185cada3/requirements/cuda.txt#L17-L17) [docker/versions.json71](https://github.com/vllm-project/vllm/blob/185cada3/docker/versions.json#L71-L71)  
`numba`| 0.65.0| [requirements/cuda.txt4](https://github.com/vllm-project/vllm/blob/185cada3/requirements/cuda.txt#L4-L4) [requirements/xpu.txt15](https://github.com/vllm-project/vllm/blob/185cada3/requirements/xpu.txt#L15-L15)  
  
Sources: [requirements/cuda.txt1-35](https://github.com/vllm-project/vllm/blob/185cada3/requirements/cuda.txt#L1-L35) [requirements/xpu.txt1-23](https://github.com/vllm-project/vllm/blob/185cada3/requirements/xpu.txt#L1-L23) [docker/versions.json1-86](https://github.com/vllm-project/vllm/blob/185cada3/docker/versions.json#L1-L86)

* * *

## Docker Multi-Stage Build

vLLM provides Dockerfiles optimized for different hardware platforms.

For details, see [Docker Multi-Stage Build](/vllm-project/vllm/11.1-docker-multi-stage-build).

### Build Strategy

  * **`base` stage**: Sets up the basic environment, installs system dependencies (e.g., `ccache`, `git`), and bootstraps Python with `uv` [docker/Dockerfile94-159](https://github.com/vllm-project/vllm/blob/185cada3/docker/Dockerfile#L94-L159)
  * **`build` stage**: Inherits from `base`, copies source, and compiles native extensions. Uses `sccache` for caching compilation results if enabled [docker/Dockerfile136-152](https://github.com/vllm-project/vllm/blob/185cada3/docker/Dockerfile#L136-L152)
  * **`final` stage**: A minimal image using `nvidia/cuda:*-base` to reduce the deployment footprint while retaining minimal dependencies for JIT compilation [docker/Dockerfile43](https://github.com/vllm-project/vllm/blob/185cada3/docker/Dockerfile#L43-L43)
  * **Rust Isolation** : The CPU and XPU builds use dedicated `rust-build` stages to build `vllm-rs` before copying it to the main image [docker/Dockerfile.cpu132-183](https://github.com/vllm-project/vllm/blob/185cada3/docker/Dockerfile.cpu#L132-L183) [docker/Dockerfile.xpu1-34](https://github.com/vllm-project/vllm/blob/185cada3/docker/Dockerfile.xpu#L1-L34)

Sources: [docker/Dockerfile1-163](https://github.com/vllm-project/vllm/blob/185cada3/docker/Dockerfile#L1-L163) [docker/Dockerfile.xpu1-181](https://github.com/vllm-project/vllm/blob/185cada3/docker/Dockerfile.xpu#L1-L181) [docker/Dockerfile.cpu1-183](https://github.com/vllm-project/vllm/blob/185cada3/docker/Dockerfile.cpu#L1-L183)

* * *

## Build Variants and Configuration

vLLM supports various build configurations to target different hardware.

For details, see [Build Variants and Configuration](/vllm-project/vllm/11.3-build-variants-and-configuration).

  * **Target Devices** : `VLLM_TARGET_DEVICE` environment variable explicitly selects between `cuda`, `rocm`, `xpu`, or `cpu` [setup.py49-108](https://github.com/vllm-project/vllm/blob/185cada3/setup.py#L49-L108)
  * **Precompiled Extensions** : `VLLM_USE_PRECOMPILED` skips native compilation by using existing binaries in the source tree [setup.py50-54](https://github.com/vllm-project/vllm/blob/185cada3/setup.py#L50-L54)
  * **TCMalloc Bundling** : CPU builds on Linux can bundle `tcmalloc` into the wheel for better memory performance [setup.py128-187](https://github.com/vllm-project/vllm/blob/185cada3/setup.py#L128-L187)
  * **Nightly Wheels** : vLLM provides nightly builds for CUDA (12.9, 13.0) via Buildkite automation [.buildkite/release-pipeline.yaml27-57](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/release-pipeline.yaml#L27-L57)

Sources: [setup.py49-108](https://github.com/vllm-project/vllm/blob/185cada3/setup.py#L49-L108) [setup.py171-187](https://github.com/vllm-project/vllm/blob/185cada3/setup.py#L171-L187) [.buildkite/release-pipeline.yaml27-57](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/release-pipeline.yaml#L27-L57)

* * *

## Runtime JIT Compilation

vLLM performs Just-In-Time (JIT) compilation for high-performance kernels.

For details, see [Runtime JIT Compilation](/vllm-project/vllm/11.4-runtime-jit-compilation).

  * **FlashInfer JIT** : Generates specialized attention kernels at runtime. Docker images include minimal CUDA base dependencies specifically to support this [docker/Dockerfile42-43](https://github.com/vllm-project/vllm/blob/185cada3/docker/Dockerfile#L42-L43)
  * **DeepGemm & EP Kernels**: These require a compiler-ready environment in the final image to generate optimized code for specific GPU architectures [docker/Dockerfile42-43](https://github.com/vllm-project/vllm/blob/185cada3/docker/Dockerfile#L42-L43)
  * **Persistent Cache** : Users can persist `torch.compile` and Triton artifacts by managing cache directories like `CCACHE_DIR` [docker/Dockerfile.rocm69-70](https://github.com/vllm-project/vllm/blob/185cada3/docker/Dockerfile.rocm#L69-L70)

Sources: [docker/Dockerfile42-43](https://github.com/vllm-project/vllm/blob/185cada3/docker/Dockerfile#L42-L43) [docker/Dockerfile.rocm69-70](https://github.com/vllm-project/vllm/blob/185cada3/docker/Dockerfile.rocm#L69-L70)

* * *

## Build Artifact Flow

**Artifact flow from source to runtime**

Sources: [setup.py188-210](https://github.com/vllm-project/vllm/blob/185cada3/setup.py#L188-L210) [docker/Dockerfile1-163](https://github.com/vllm-project/vllm/blob/185cada3/docker/Dockerfile#L1-L163) [setup.py45-47](https://github.com/vllm-project/vllm/blob/185cada3/setup.py#L45-L47)
