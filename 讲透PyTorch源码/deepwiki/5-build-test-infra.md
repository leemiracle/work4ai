# Build and Test Infrastructure

- .ci/docker/build.sh
- .ci/docker/common/cache_vision_models.sh
- .ci/docker/common/common_utils.sh
- .ci/docker/common/install_cache.sh
- .ci/docker/common/install_conda.sh
- .ci/docker/common/install_executorch.sh
- .ci/docker/common/install_halide.sh
- .ci/docker/common/install_inductor_benchmark_deps.sh
- .ci/docker/common/install_onnx.sh
- .ci/docker/common/install_python.sh
- .ci/docker/common/install_rocm.sh
- .ci/docker/common/install_triton.sh
- .ci/docker/common/patches/sccache-nvcc-13.3-dryrun-parsing.patch
- .ci/docker/ubuntu-rocm/Dockerfile
- .ci/docker/ubuntu-xpu/Dockerfile
- .ci/docker/ubuntu/Dockerfile
- .ci/pytorch/build.sh
- .ci/pytorch/common.sh
- .ci/pytorch/test.sh
- .github/ci_commit_pins/torchcomms.txt
- .github/workflows/_linux-build.yml
- .github/workflows/_linux-test.yml
- .github/workflows/docker-builds.yml
- .github/workflows/nightly.yml
- .github/workflows/pull.yml
- .github/workflows/rocm-preview.yml
- .github/workflows/trunk.yml
- CMakeLists.txt
- aten/src/ATen/CMakeLists.txt
- aten/src/ATen/Context.cpp
- aten/src/ATen/Context.h
- aten/src/ATen/native/transformers/hip/flash_attn/ck/CMakeLists.txt
- aten/src/ATen/native/transformers/hip/flash_attn/ck/launch_kernel_pt.hpp
- benchmarks/dynamo/expected_ci_speedup_inductor_torchbench_cpu.csv
- cmake/Dependencies.cmake
- cmake/EnvVarForwarding.cmake
- cmake/External/nccl_ep.cmake
- cmake/Summary.cmake
- test/distributed/test_token_switch.py
- torch/CMakeLists.txt
- torch/csrc/distributed/c10d/symm_mem/nccl_ep.cu
- torch/csrc/distributed/c10d/symm_mem/nccl_ep.hpp
- torch/csrc/distributed/c10d/symm_mem/nccl_ep_pybind.cpp
- torch/distributed/_token_switch.py

Build System and Code Generation
Testing Infrastructure and OpInfo
CI/CD Workflows and Docker Image Builds
Binary Release Pipeline
External Integration: vLLM CI Pipeline

## System Overview

Build System
`CMakeLists.txt`
`setup.py`

Docker Images
`.ci/docker/`
`.ci/docker/build.sh`

CI/CD Workflows
`.github/workflows/`

Test Runner
`test/run_test.py`
`.ci/pytorch/test.sh`

Binary Release

CI/CD Flow Diagram

```

```

.github/workflows/pull.yml 1-125
.github/workflows/trunk.yml 1-131
.github/workflows/_linux-test.yml 1-135
.ci/pytorch/test.sh 1-75

## Build System

### CMake Configuration

`CMakeLists.txt`
`cmake/EnvVarForwarding.cmake`
CMakeLists.txt 9-16

`cmake/PreBuildSteps.cmake`
`cmake/Dependencies.cmake`
CMakeLists.txt 17-23
`caffe2/CMakeLists.txt`
`cmake/Codegen.cmake`
CMakeLists.txt 24-28

`setup.py`

Key feature flags in CMakeLists.txt and cmake/Dependencies.cmake :

| Flag | Default | Purpose |
|---|---|---|
| USE_CUDA | Configurable | CUDA support cmake/Dependencies.cmake 22-30 |
| USE_ROCM | Configurable | AMD ROCm support cmake/Dependencies.cmake 108-115 |
| USE_XPU | Configurable | Intel XPU/SYCL support cmake/Dependencies.cmake 83-93 |
| USE_MKLDNN | ON (x86) | oneDNN CPU kernels cmake/Dependencies.cmake 168-180 |
| USE_ASAN | OFF | Address Sanitizer cmake/Dependencies.cmake 100-128 |

CMakeLists.txt 1-133
cmake/Dependencies.cmake 1-186
.ci/pytorch/build.sh 1-189

### Build System Code Entity Map

```

```

CMakeLists.txt 1-45
cmake/Dependencies.cmake 21-29
aten/src/ATen/CMakeLists.txt 1-67

## CI/CD Workflows

### Workflow Topology

`.github/workflows/pull.yml`
`.github/workflows/trunk.yml`

- job-filter.yml which determines selective job execution based on labels and PR context pull.yml 41-47
- target_determination.yml for test selection and prioritization pull.yml 53-57
- _linux-build.yml and _linux-test.yml as reusable workflows for building and testing binaries pull.yml 72-130

Workflow dependency graph:

```

```

.github/workflows/pull.yml 39-130
.github/workflows/trunk.yml 36-131
.github/workflows/_linux-test.yml 1-125

### Docker Image Builds

`.ci/docker/`
`.ci/docker/build.sh`
build.sh 17-45

`.github/workflows/docker-builds.yml`
docker-builds.yml 45-81

.ci/docker/build.sh 1-236
.github/workflows/docker-builds.yml 1-168

## Test Orchestration

### .ci/pytorch/test.sh

`.ci/pytorch/test.sh`

- Patching numba for CUDA-13 support .ci/pytorch/test.sh 39-48
- Setting Inductor compile-worker thread limits and timeouts on ROCm .ci/pytorch/test.sh 85-99
- Managing Valgrind suppressions for specific compiler versions .ci/pytorch/test.sh 103-139

### CI/CD + Test Code Entity Map

```

```

.github/workflows/_linux-test.yml 164-170
.ci/pytorch/test.sh 1-100
.ci/docker/build.sh 68-82

## Binary Release Pipeline

`_linux-build.yml`

- VLLM Integration : CI integration for vLLM includes commit pinning and specialized Docker images for testing docker-builds.yml 52 .github/ci_commit_pins/torchcomms.txt 1
- Artifact Management : Build jobs use reuse-old-whl actions to optimize CI time when C++ changes are absent _linux-build.yml 179-188

.github/workflows/_linux-build.yml 1-188
.github/workflows/docker-builds.yml 45-81
.github/ci_commit_pins/torchcomms.txt 1

- Build System and Code Generation
- Testing Infrastructure and OpInfo
- CI/CD Workflows and Docker Image Builds
- Binary Release Pipeline
- External Integration: vLLM CI Pipeline

###
