> 来源: [https://deepwiki.com/sgl-project/sglang/16-release-and-deployment-automation](https://deepwiki.com/sgl-project/sglang/16-release-and-deployment-automation)
> DeepWiki sgl-project/sglang | Last indexed: 27 Aug 2026 (94183a)

# Release and Deployment Automation

  Relevant source files 
 - [.github/workflows/_docker-build-and-publish.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/_docker-build-and-publish.yml)
 - [.github/workflows/_docker-cleanup-nightly.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/_docker-cleanup-nightly.yml)
 - [.github/workflows/nightly-72-gpu-gb200.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/nightly-72-gpu-gb200.yml)
 - [.github/workflows/nightly-test-musa.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/nightly-test-musa.yml)
 - [.github/workflows/patch-docker-dev.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/patch-docker-dev.yml)
 - [.github/workflows/pr-test-musa.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/pr-test-musa.yml)
 - [.github/workflows/release-docker-dev.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-docker-dev.yml)
 - [.github/workflows/release-docker-runtime.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-docker-runtime.yml)
 - [.github/workflows/release-docker.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-docker.yml)
 - [.github/workflows/release-whl-kernel-xpu.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-whl-kernel-xpu.yml)
 - [.github/workflows/release-whl-kernel.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-whl-kernel.yml)
 - [.github/workflows/trivy-scan-dev.yml](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/trivy-scan-dev.yml)
 - [python/sglang/multimodal_gen/test/server/musa/perf_baselines_musa.json](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/test/server/musa/perf_baselines_musa.json)
 - [python/sglang/multimodal_gen/test/server/musa/test_server_1_gpu_musa.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/test/server/musa/test_server_1_gpu_musa.py)
 - [python/sglang/multimodal_gen/test/server/musa/test_server_1_gpu_musa_nightly.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/test/server/musa/test_server_1_gpu_musa_nightly.py)
 - [python/sglang/multimodal_gen/test/server/musa/test_server_2_gpu_musa.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/test/server/musa/test_server_2_gpu_musa.py)
 - [python/sglang/multimodal_gen/test/server/musa/testcase_configs_musa.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/test/server/musa/testcase_configs_musa.py)
 - [scripts/ci/musa/musa_install_dependency.sh](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/musa/musa_install_dependency.sh)
 - [scripts/ci/musa/musa_python_stack.py](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/musa/musa_python_stack.py)
 - [scripts/ci/musa/rename_wheels_musa.sh](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/musa/rename_wheels_musa.sh)
 - [scripts/ci/musa/test_musa_python_stack.py](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/musa/test_musa_python_stack.py)
 - [scripts/ci/slurm/analyze_logs_with_modal.py](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/slurm/analyze_logs_with_modal.py)
 - [scripts/ci/slurm/launch_gb200.sh](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/slurm/launch_gb200.sh)
 - [scripts/ci/slurm/log_analysis_prompt.md](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/slurm/log_analysis_prompt.md?plain=1)
 - [scripts/ci/utils/docker_build_metadata_args.py](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/utils/docker_build_metadata_args.py)
 - [scripts/update_kernel_whl_index.py](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/update_kernel_whl_index.py)
 - [test/registered/musa/test_llm_server_smoke_musa.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/musa/test_llm_server_smoke_musa.py)
 - [test/registered/unit/tools/test_docker_build_metadata_args.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/tools/test_docker_build_metadata_args.py)
 
  This page describes the automated pipelines that build, version, and publish SGLang artifacts: Python wheels (PyPI and custom index) and Docker images. It covers the GitHub Actions workflows, version numbering conventions, and the multi-platform build matrix.

 For information about how to *use* these artifacts once they are published, see page [Installation and Deployment](https://deepwiki.com/sgl-project/sglang/2-installation-and-deployment). For Docker image contents and how to run containers, see page [Docker Deployment](https://deepwiki.com/sgl-project/sglang/2.3-docker-deployment).

 
---

 
## Overview

 SGLang distributes two primary packages:

 
| Package | Distribution channel | Build toolchain |
|---|---|---|
| sglang | PyPI, sgl-project/whl GitHub index | setuptools-scm, python3 -m build |
| sgl-kernel | PyPI, sgl-project/whl GitHub index | scikit-build-core + CMake |

 Docker images are published to `lmsysorg/sglang` on Docker Hub.

 The overall trigger chain is:

 **Release pipeline diagram: trigger events to published artifacts**

 
```

```

 Sources: [.github/workflows/release-docker.yml7-16](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-docker.yml#L7-L16) [.github/workflows/release-docker-dev.yml3-36](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-docker-dev.yml#L3-L36)

 
---

 
## Version Management

 
### sglang Version

 `sglang` uses `setuptools-scm` for dynamic versioning derived from git tags. Stable releases are resolved from the GitHub ref name or manual input in `release-docker.yml` [.github/workflows/release-docker.yml31-40](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-docker.yml#L31-L40) Nightly versions are calculated by incrementing the patch version and appending a date-based dev string to ensure correct chronological sorting per PEP 440.

 
### sgl-kernel Version

 The `sgl-kernel` version is defined in `python/sglang/kernels/aot/python/sgl_kernel/version.py` [.github/workflows/release-whl-kernel.yml8](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-whl-kernel.yml#L8-L8) Release workflows extract this version (e.g., stripping `+cu130` local version suffixes for PyPI compliance) to create tags and manage repository releases [.github/workflows/release-whl-kernel.yml105-113](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-whl-kernel.yml#L105-L113) [.github/workflows/release-whl-kernel.yml185-198](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-whl-kernel.yml#L185-L198)

 
### Release Coordination

 Stable releases are triggered by pushing version tags matching `v[0-9]+.*` [.github/workflows/release-docker.yml9-10](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-docker.yml#L9-L10) PR-specific wheels can also be built manually to facilitate testing by specifying a `pr_number` in the workflow dispatch [.github/workflows/release-whl-kernel.yml27-30](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-whl-kernel.yml#L27-L30)

 For details, see [Version Management](https://deepwiki.com/sgl-project/sglang/16.3-version-management).

 Sources: [.github/workflows/release-whl-kernel.yml105-113](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-whl-kernel.yml#L105-L113) [.github/workflows/release-docker.yml9-10](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-docker.yml#L9-L10)

 
---

 
## Wheel Build and Release Pipeline

 
### sgl-kernel Wheels

 The `sgl-kernel` package requires specialized compilation for different hardware backends. The `release-whl-kernel.yml` workflow manages a matrix of Python 3.10, CUDA (12.9, 13.0), ROCm (7.0, 7.2), and MUSA (4.3) across `x86_64` and `aarch64` architectures [.github/workflows/release-whl-kernel.yml10-22](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-whl-kernel.yml#L10-L22) [.github/workflows/release-whl-kernel.yml44-54](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-whl-kernel.yml#L44-L54)

 
### Build and Indexing

 
 - **Build Scripts**: Builds utilize platform-specific scripts such as `python/sglang/kernels/aot/build.sh` [.github/workflows/release-whl-kernel.yml78-79](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-whl-kernel.yml#L78-L79)
 - **Wheel Indexing**: The `scripts/update_kernel_whl_index.py` script manages the `sgl-project/whl` repository, generating PEP 503 compliant HTML indices for different CUDA, ROCm, and MUSA versions [scripts/update_kernel_whl_index.py32-77](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/update_kernel_whl_index.py#L32-L77) It uses SHA256 hashing to ensure artifact integrity [scripts/update_kernel_whl_index.py41-46](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/update_kernel_whl_index.py#L41-L46)
 
 
### Distribution

 
 - **PyPI**: Stable wheels for CUDA 13.0 are uploaded to PyPI after stripping local version suffixes [.github/workflows/release-whl-kernel.yml185-198](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-whl-kernel.yml#L185-L198)
 - **Custom Index**: Wheels for specific variants (like CUDA 12.9 or ROCm) are pushed to the `sgl-project/whl` repository to be consumed via `--extra-index-url` [.github/workflows/release-whl-kernel.yml115-123](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-whl-kernel.yml#L115-L123)
 
 For details, see [Wheel Build and Release Pipeline](https://deepwiki.com/sgl-project/sglang/16.1-wheel-build-and-release-pipeline).

 Sources: [.github/workflows/release-whl-kernel.yml1-198](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-whl-kernel.yml#L1-L198) [scripts/update_kernel_whl_index.py1-95](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/update_kernel_whl_index.py#L1-L95)

 
---

 
## Docker Build and Release Pipeline

 
### Image Variants and Matrix

 SGLang maintains a matrix of Docker images:

 
 - **Nightly/Dev**: Daily builds for CUDA 12.9 and 13.0 [.github/workflows/release-docker-dev.yml84-92](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-docker-dev.yml#L84-L92)
 - **Stable Release**: Triggered by version tags, publishing `framework_final` (full environment) and `runtime` (optimized size) images [.github/workflows/release-docker.yml50-54](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-docker.yml#L50-L54) [.github/workflows/release-docker-runtime.yml50-54](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-docker-runtime.yml#L50-L54)
 - **Overlay Builds**: The development pipeline supports "overlay" images, allowing additional layers (e.g., custom pip installs) to be built on top of base images via `overlay_dockerfile` inputs [.github/workflows/release-docker-dev.yml23-34](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-docker-dev.yml#L23-L34)
 
 
### Multi-Stage and Multi-Arch

 The build process uses `_docker-build-and-publish.yml` as a reusable workflow [.github/workflows/release-docker.yml44-49](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-docker.yml#L44-L49) It builds for both `linux/amd64` and `linux/arm64` (specifically for GB200/ARM environments) [.github/workflows/release-docker-dev.yml156](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-docker-dev.yml#L156-L156)

 
### Maintenance and Patching

 
 - **Trivy Scanning**: Images are scanned daily for vulnerabilities using Trivy, with results uploaded to GitHub Security [.github/workflows/trivy-scan-dev.yml33-49](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/trivy-scan-dev.yml#L33-L49)
 - **Patching**: A `patch-docker-dev.yml` workflow allows developers to apply specific PR diffs to existing images without a full rebuild by merging `pr_numbers` onto the base image commit [.github/workflows/patch-docker-dev.yml4-9](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/patch-docker-dev.yml#L4-L9) [.github/workflows/patch-docker-dev.yml142-175](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/patch-docker-dev.yml#L142-L175)
 
 
### Automated Failure Analysis

 For large-scale nightly tests (e.g., GB200 72GPU clusters), SGLang uses an automated analysis pipeline [.github/workflows/nightly-72-gpu-gb200.yml1-26](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/nightly-72-gpu-gb200.yml#L1-L26) The `analyze_logs_with_modal.py` script [scripts/ci/slurm/analyze_logs_with_modal.py1-15](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/slurm/analyze_logs_with_modal.py#L1-L15) uploads Slurm logs to a Modal sandbox where an LLM agent (`opencode`) analyzes the root cause based on a detailed prompt [scripts/ci/slurm/log_analysis_prompt.md1-213](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/slurm/log_analysis_prompt.md?plain=1#L1-L213) and files GitHub issues automatically [.scripts/ci/slurm/log_analysis_prompt.md152-202](https://github.com/sgl-project/sglang/blob/94183a8d/.scripts/ci/slurm/log_analysis_prompt.md?plain=1#L152-L202)

 **Build and Release Architecture Mapping**

 
```

```

 **Version and Release Component Association**

 
```

```

 For details, see [Docker Build and Release Pipeline](https://deepwiki.com/sgl-project/sglang/16.2-docker-build-and-release-pipeline).

 Sources: [.github/workflows/release-docker.yml1-55](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-docker.yml#L1-L55) [.github/workflows/release-docker-dev.yml1-154](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-docker-dev.yml#L1-L154) [.github/workflows/patch-docker-dev.yml1-119](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/patch-docker-dev.yml#L1-L119) [.github/workflows/trivy-scan-dev.yml1-88](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/trivy-scan-dev.yml#L1-L88) [scripts/ci/slurm/analyze_logs_with_modal.py1-15](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/slurm/analyze_logs_with_modal.py#L1-L15) [scripts/ci/slurm/log_analysis_prompt.md1-213](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/slurm/log_analysis_prompt.md?plain=1#L1-L213) [.github/workflows/nightly-72-gpu-gb200.yml1-87](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/nightly-72-gpu-gb200.yml#L1-L87)
