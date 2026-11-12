> 来源: [https://deepwiki.com/ray-project/ray/8-build-and-development-infrastructure](https://deepwiki.com/ray-project/ray/8-build-and-development-infrastructure)
> DeepWiki ray-project/ray | Last indexed: 25 June 2026 (bf1295

# Build and Development Infrastructure

  Relevant source files 
 - [.bazelrc](https://github.com/ray-project/ray/blob/bf129559/.bazelrc)
 - [.bazelversion](https://github.com/ray-project/ray/blob/bf129559/.bazelversion)
 - [BUILD.bazel](https://github.com/ray-project/ray/blob/bf129559/BUILD.bazel)
 - [WORKSPACE](https://github.com/ray-project/ray/blob/bf129559/WORKSPACE)
 - [bazel/BUILD.bazel](https://github.com/ray-project/ray/blob/bf129559/bazel/BUILD.bazel)
 - [bazel/gen_extract.py](https://github.com/ray-project/ray/blob/bf129559/bazel/gen_extract.py)
 - [bazel/jemalloc.BUILD](https://github.com/ray-project/ray/blob/bf129559/bazel/jemalloc.BUILD)
 - [bazel/ray.bzl](https://github.com/ray-project/ray/blob/bf129559/bazel/ray.bzl)
 - [bazel/ray_deps_build_all.bzl](https://github.com/ray-project/ray/blob/bf129559/bazel/ray_deps_build_all.bzl)
 - [bazel/ray_deps_setup.bzl](https://github.com/ray-project/ray/blob/bf129559/bazel/ray_deps_setup.bzl)
 - [ci/ci_tags_from_change.sh](https://github.com/ray-project/ray/blob/bf129559/ci/ci_tags_from_change.sh)
 - [ci/docker/llm.build.Dockerfile](https://github.com/ray-project/ray/blob/bf129559/ci/docker/llm.build.Dockerfile)
 - [ci/docker/llm.build.wanda.yaml](https://github.com/ray-project/ray/blob/bf129559/ci/docker/llm.build.wanda.yaml)
 - [ci/lint/BUILD.bazel](https://github.com/ray-project/ray/blob/bf129559/ci/lint/BUILD.bazel)
 - [ci/pipeline/BUILD.bazel](https://github.com/ray-project/ray/blob/bf129559/ci/pipeline/BUILD.bazel)
 - [ci/pipeline/determine_tests_to_run.py](https://github.com/ray-project/ray/blob/bf129559/ci/pipeline/determine_tests_to_run.py)
 - [ci/ray_ci/BUILD.bazel](https://github.com/ray-project/ray/blob/bf129559/ci/ray_ci/BUILD.bazel)
 - [ci/ray_ci/bazel_sharding.py](https://github.com/ray-project/ray/blob/bf129559/ci/ray_ci/bazel_sharding.py)
 - [ci/ray_ci/bisect/BUILD.bazel](https://github.com/ray-project/ray/blob/bf129559/ci/ray_ci/bisect/BUILD.bazel)
 - [ci/ray_ci/doc/BUILD.bazel](https://github.com/ray-project/ray/blob/bf129559/ci/ray_ci/doc/BUILD.bazel)
 - [ci/ray_ci/doc/build_cache.py](https://github.com/ray-project/ray/blob/bf129559/ci/ray_ci/doc/build_cache.py)
 - [ci/ray_ci/doc/cmd_build.py](https://github.com/ray-project/ray/blob/bf129559/ci/ray_ci/doc/cmd_build.py)
 - [ci/ray_ci/doc/test_build_cache.py](https://github.com/ray-project/ray/blob/bf129559/ci/ray_ci/doc/test_build_cache.py)
 - [ci/ray_ci/pipeline/BUILD.bazel](https://github.com/ray-project/ray/blob/bf129559/ci/ray_ci/pipeline/BUILD.bazel)
 - [ci/ray_ci/test_bazel_sharding.py](https://github.com/ray-project/ray/blob/bf129559/ci/ray_ci/test_bazel_sharding.py)
 - [doc/external/test_hashes.py](https://github.com/ray-project/ray/blob/bf129559/doc/external/test_hashes.py)
 - [docker/ray-llm/Dockerfile](https://github.com/ray-project/ray/blob/bf129559/docker/ray-llm/Dockerfile)
 - [docker/ray-llm/cuda.wanda.yaml](https://github.com/ray-project/ray/blob/bf129559/docker/ray-llm/cuda.wanda.yaml)
 - [gen_py_proto.py](https://github.com/ray-project/ray/blob/bf129559/gen_py_proto.py)
 - [java/BUILD.bazel](https://github.com/ray-project/ray/blob/bf129559/java/BUILD.bazel)
 - [java/build-jar-multiplatform.sh](https://github.com/ray-project/ray/blob/bf129559/java/build-jar-multiplatform.sh)
 - [java/gen_maven_deps.py](https://github.com/ray-project/ray/blob/bf129559/java/gen_maven_deps.py)
 - [java/gen_pom_files.py](https://github.com/ray-project/ray/blob/bf129559/java/gen_pom_files.py)
 - [java/gen_proto_files.py](https://github.com/ray-project/ray/blob/bf129559/java/gen_proto_files.py)
 - [java/generate_jni_header_files.sh](https://github.com/ray-project/ray/blob/bf129559/java/generate_jni_header_files.sh)
 - [java/test.sh](https://github.com/ray-project/ray/blob/bf129559/java/test.sh)
 - [python/deplocks/llm/rayllm_py312_cpu.lock](https://github.com/ray-project/ray/blob/bf129559/python/deplocks/llm/rayllm_py312_cpu.lock)
 - [python/deplocks/llm/rayllm_py312_cu130.lock](https://github.com/ray-project/ray/blob/bf129559/python/deplocks/llm/rayllm_py312_cu130.lock)
 - [python/deplocks/llm/rayllm_test_py312_cpu.lock](https://github.com/ray-project/ray/blob/bf129559/python/deplocks/llm/rayllm_test_py312_cpu.lock)
 - [python/deplocks/llm/rayllm_test_py312_cu130.lock](https://github.com/ray-project/ray/blob/bf129559/python/deplocks/llm/rayllm_test_py312_cu130.lock)
 - [python/ray/tests/test_protobuf_compatibility.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_protobuf_compatibility.py)
 - [python/requirements.txt](https://github.com/ray-project/ray/blob/bf129559/python/requirements.txt)
 - [python/requirements/llm/llm-requirements.txt](https://github.com/ray-project/ray/blob/bf129559/python/requirements/llm/llm-requirements.txt)
 - [python/requirements/test-requirements.txt](https://github.com/ray-project/ray/blob/bf129559/python/requirements/test-requirements.txt)
 - [python/requirements_compiled.txt](https://github.com/ray-project/ray/blob/bf129559/python/requirements_compiled.txt)
 - [python/setup.py](https://github.com/ray-project/ray/blob/bf129559/python/setup.py)
 - [release/BUILD.bazel](https://github.com/ray-project/ray/blob/bf129559/release/BUILD.bazel)
 - [release/requirements-doc.txt](https://github.com/ray-project/ray/blob/bf129559/release/requirements-doc.txt)
 - [thirdparty/patches/build-bazel-apple-support-xcode.patch](https://github.com/ray-project/ray/blob/bf129559/thirdparty/patches/build-bazel-apple-support-xcode.patch)
 - [thirdparty/patches/cython.patch](https://github.com/ray-project/ray/blob/bf129559/thirdparty/patches/cython.patch)
 - [thirdparty/patches/org_lzma_lzma.BUILD.bazel](https://github.com/ray-project/ray/blob/bf129559/thirdparty/patches/org_lzma_lzma.BUILD.bazel)
 - [thirdparty/patches/protobuf-bazel7.patch](https://github.com/ray-project/ray/blob/bf129559/thirdparty/patches/protobuf-bazel7.patch)
 - [thirdparty/patches/spdlog-rotation-file-format.patch](https://github.com/ray-project/ray/blob/bf129559/thirdparty/patches/spdlog-rotation-file-format.patch)
 
  This document describes Ray's build system, continuous integration/continuous deployment (CI/CD) pipelines, testing infrastructure, and release processes. For details on package dependencies and installation modes, see [Package Management and Dependencies](https://deepwiki.com/ray-project/ray/8.1-package-management-and-dependencies). For CI/CD implementation details, see [CI/CD Pipeline and Test Orchestration](https://deepwiki.com/ray-project/ray/8.2-cicd-pipeline-and-test-orchestration). For release testing specifics, see [Release Testing and Benchmarks](https://deepwiki.com/ray-project/ray/8.3-release-testing-and-benchmarks).

 
## Architecture Overview

 Ray's development infrastructure consists of three main layers: a **Buildkite-based CI/CD system** that orchestrates all builds and tests, an **intelligent test selection system** that minimizes test execution time, and a **containerized build and test environment** (utilizing the `wanda` build system) that ensures reproducibility across multiple platforms and configurations.

 
### CI/CD System Architecture

 
```

```

 **Sources:** [ci/pipeline/determine_tests_to_run.py1-229](https://github.com/ray-project/ray/blob/bf129559/ci/pipeline/determine_tests_to_run.py#L1-L229) [BUILD.bazel1-213](https://github.com/ray-project/ray/blob/bf129559/BUILD.bazel#L1-L213) [release/BUILD.bazel266-290](https://github.com/ray-project/ray/blob/bf129559/release/BUILD.bazel#L266-L290)

 
## Buildkite Pipeline Organization

 Ray uses **Buildkite** as its CI/CD platform, with pipeline definitions stored in `.buildkite/*.rayci.yml` files. The system heavily leverages the `wanda` build tool for containerized builds.

 
### Pipeline Dependency Graph

 
```

```

 **Sources:** [BUILD.bazel23-26](https://github.com/ray-project/ray/blob/bf129559/BUILD.bazel#L23-L26) [WORKSPACE1-172](https://github.com/ray-project/ray/blob/bf129559/WORKSPACE#L1-L172) [python/setup.py30-41](https://github.com/ray-project/ray/blob/bf129559/python/setup.py#L30-L41)

 
## Build Artifact Creation

 
### Build and Dependency Orchestration

 Ray's build process is orchestrated via `setup.py`, which triggers **Bazel** for C++ and Cython compilation.

 
 - **Bazel Integration**: `setup.py` calls Bazel to build the `_raylet` extension and other binary components [python/setup.py145-154](https://github.com/ray-project/ray/blob/bf129559/python/setup.py#L145-L154)
 - **Dependency Management**: Dependencies are defined in `python/requirements.txt` and specialized requirement files for ML, Data, and LLM workloads [python/requirements_compiled.txt1-281](https://github.com/ray-project/ray/blob/bf129559/python/requirements_compiled.txt#L1-L281)
 - **Dependency Pinning**: The project uses `raydepsets` and `deplocks` (e.g., for LLM) to ensure deterministic environments [docker/ray-llm/Dockerfile6-7](https://github.com/ray-project/ray/blob/bf129559/docker/ray-llm/Dockerfile#L6-L7)
 - **Packaging**: The system produces `manylinux` wheels and specialized Docker images (CPU, CUDA, TPU) [python/setup.py121-137](https://github.com/ray-project/ray/blob/bf129559/python/setup.py#L121-L137)
 
 For details, see [Package Management and Dependencies](https://deepwiki.com/ray-project/ray/8.1-package-management-and-dependencies).

 **Sources:** [python/setup.py1-154](https://github.com/ray-project/ray/blob/bf129559/python/setup.py#L1-L154) [BUILD.bazel161-196](https://github.com/ray-project/ray/blob/bf129559/BUILD.bazel#L161-L196) [python/requirements_compiled.txt1-281](https://github.com/ray-project/ray/blob/bf129559/python/requirements_compiled.txt#L1-L281) [bazel/ray_deps_setup.bzl86-157](https://github.com/ray-project/ray/blob/bf129559/bazel/ray_deps_setup.bzl#L86-L157)

 
## Test Orchestration

 Ray uses an intelligent test selection mechanism to optimize CI turnaround time.

 
### Test Selection Logic

 The `determine_tests_to_run.py` script identifies changed files and maps them to CI tags based on a set of `TagRule` objects [ci/pipeline/determine_tests_to_run.py60-91](https://github.com/ray-project/ray/blob/bf129559/ci/pipeline/determine_tests_to_run.py#L60-L91) This ensures that a change in `ray/serve/` only triggers Serve-related pipelines.

 
```

```

 For details, see [CI/CD Pipeline and Test Orchestration](https://deepwiki.com/ray-project/ray/8.2-cicd-pipeline-and-test-orchestration).

 **Sources:** [ci/pipeline/determine_tests_to_run.py12-47](https://github.com/ray-project/ray/blob/bf129559/ci/pipeline/determine_tests_to_run.py#L12-L47) [ci/pipeline/determine_tests_to_run.py93-164](https://github.com/ray-project/ray/blob/bf129559/ci/pipeline/determine_tests_to_run.py#L93-L164) [BUILD.bazel67-73](https://github.com/ray-project/ray/blob/bf129559/BUILD.bazel#L67-L73)

 
## Release Testing and Benchmarks

 The release process involves heavy validation across multiple cloud providers and architectures, managed via the `ray_release` framework.

 
### Release Build and Test Configuration

 Ray maintains a comprehensive set of release tests defined in YAML configurations. These include smoke tests for core libraries and high-performance benchmarks for LLM and ML workloads.

 
| Component | Test Target Example | Tag |
|---|---|---|
| Serve | serve_failure_smoke_test | team:serve |
| ML/Train | xgboost_train_batch_inference_benchmark_smoke_test | team:ml |
| Data | air_benchmark_gpu_batch_inference_parquet_smoke_test | team:data |
| Release Infra | run_release_test | team:ci |

 **Sources:** [release/BUILD.bazel66-82](https://github.com/ray-project/ray/blob/bf129559/release/BUILD.bazel#L66-L82) [release/BUILD.bazel106-124](https://github.com/ray-project/ray/blob/bf129559/release/BUILD.bazel#L106-L124) [release/BUILD.bazel126-145](https://github.com/ray-project/ray/blob/bf129559/release/BUILD.bazel#L126-L145) [release/BUILD.bazel276-290](https://github.com/ray-project/ray/blob/bf129559/release/BUILD.bazel#L276-L290)

 
### LLM Release Infrastructure

 The `ray-llm` Docker image represents the cutting edge of Ray's release infrastructure, incorporating specialized CUDA 13.0 environments and vLLM kernel optimizations [docker/ray-llm/Dockerfile13-38](https://github.com/ray-project/ray/blob/bf129559/docker/ray-llm/Dockerfile#L13-L38) It utilizes `uv` for high-speed dependency resolution and `nixl` for advanced KV cache management [python/requirements/llm/llm-requirements.txt1-19](https://github.com/ray-project/ray/blob/bf129559/python/requirements/llm/llm-requirements.txt#L1-L19)

 For details, see [Release Testing and Benchmarks](https://deepwiki.com/ray-project/ray/8.3-release-testing-and-benchmarks).

 **Sources:** [docker/ray-llm/Dockerfile69-84](https://github.com/ray-project/ray/blob/bf129559/docker/ray-llm/Dockerfile#L69-L84) [python/requirements/llm/llm-requirements.txt1-19](https://github.com/ray-project/ray/blob/bf129559/python/requirements/llm/llm-requirements.txt#L1-L19) [python/requirements_compiled.txt21-22](https://github.com/ray-project/ray/blob/bf129559/python/requirements_compiled.txt#L21-L22)
