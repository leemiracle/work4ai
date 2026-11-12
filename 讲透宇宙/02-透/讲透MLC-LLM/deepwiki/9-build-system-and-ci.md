> 来源: [https://deepwiki.com/mlc-ai/mlc-llm/9-build-system-and-ci](https://deepwiki.com/mlc-ai/mlc-llm/9-build-system-and-ci)
> DeepWiki mlc-ai/mlc-llm | Last indexed: 30 March 2026 (fcce2c

# Build System and CI

  Relevant source files 
 - [.github/workflows/documentation.yaml](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/.github/workflows/documentation.yaml)
 - [.github/workflows/update-relax.yaml](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/.github/workflows/update-relax.yaml)
 - [.github/workflows/windows-build.yaml](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/.github/workflows/windows-build.yaml)
 - [.gitmodules](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/.gitmodules)
 - [CMakeLists.txt](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/CMakeLists.txt)
 - [CONTRIBUTORS.md](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/CONTRIBUTORS.md?plain=1)
 - [android/mlc4j/CMakeLists.txt](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/android/mlc4j/CMakeLists.txt)
 - [android/mlc4j/src/cpp/tvm_runtime.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/android/mlc4j/src/cpp/tvm_runtime.h)
 - [ci/bash.sh](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/bash.sh)
 - [ci/build-environment.yaml](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/build-environment.yaml)
 - [ci/jenkinsfile.groovy](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/jenkinsfile.groovy)
 - [ci/task/black.sh](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/task/black.sh)
 - [ci/task/build_clean.sh](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/task/build_clean.sh)
 - [ci/task/build_lib.sh](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/task/build_lib.sh)
 - [ci/task/build_win.bat](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/task/build_win.bat)
 - [ci/task/clang-format.sh](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/task/clang-format.sh)
 - [ci/task/isort.sh](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/task/isort.sh)
 - [ci/task/mypy.sh](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/task/mypy.sh)
 - [ci/task/pylint.sh](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/task/pylint.sh)
 - [ci/task/test_model_compile.sh](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/task/test_model_compile.sh)
 - [ci/task/test_unittest.sh](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/task/test_unittest.sh)
 - [cmake/gen_cmake_config.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cmake/gen_cmake_config.py)
 - [docs/.gitignore](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/.gitignore)
 - [docs/Makefile](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/Makefile)
 - [docs/README.md](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/README.md?plain=1)
 - [docs/_static/img/mlc-logo-with-text-landscape.svg](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/_static/img/mlc-logo-with-text-landscape.svg)
 - [docs/conf.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/conf.py)
 - [docs/make.bat](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/make.bat)
 - [docs/requirements.txt](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/requirements.txt)
 - [ios/MLCSwift/Package.swift](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ios/MLCSwift/Package.swift)
 - [ios/MLCSwift/Sources/ObjC/LLMEngine.mm](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ios/MLCSwift/Sources/ObjC/LLMEngine.mm)
 - [pyproject.toml](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/pyproject.toml)
 - [python/requirements.txt](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/requirements.txt)
 - [scripts/build_mlc_for_docs.sh](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/scripts/build_mlc_for_docs.sh)
 - [scripts/build_site.sh](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/scripts/build_site.sh)
 - [scripts/gh_deploy_site.sh](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/scripts/gh_deploy_site.sh)
 - [tests/python/integration/test_model_compile.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/tests/python/integration/test_model_compile.py)
 - [tests/python/serve/test_radix_tree.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/tests/python/serve/test_radix_tree.py)
 - [web/Makefile](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/web/Makefile)
 - [web/emcc/mlc_wasm_runtime.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/web/emcc/mlc_wasm_runtime.cc)
 
  This page documents how MLC LLM is built and tested. It covers the CMake build system, third-party submodule dependencies, Python package configuration via `scikit-build-core`, the interactive backend configuration helper, and the Jenkins and GitHub Actions CI pipelines.

 For information about how compiled artifacts are consumed at runtime, see [Compilation System](https://deepwiki.com/mlc-ai/mlc-llm/4-compilation-system). For packaging for mobile platforms, see [Packaging and Distribution](https://deepwiki.com/mlc-ai/mlc-llm/4.5-packaging-and-distribution).

 
---

 
## CMake Build System

 The root [CMakeLists.txt](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/CMakeLists.txt) drives all C++ compilation. The minimum required CMake version is 3.18, and the project requires C++17 [CMakeLists.txt1-46](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/CMakeLists.txt#L1-L46)

 
### Build Targets

 **Target diagram: CMake libraries and their relationships**

 
```

```

 Sources: [CMakeLists.txt74-147](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/CMakeLists.txt#L74-L147)

 
| Target | Type | Purpose |
|---|---|---|
| mlc_llm_objs | OBJECT | Compiled object files shared across all output targets CMakeLists.txt78 |
| mlc_llm | SHARED | Main shared library, links tvm_runtime CMakeLists.txt96-102 |
| mlc_llm_static | STATIC | Static library variant; links tokenizers_cpp, sentencepiece-static, tvm_runtime CMakeLists.txt97-99 |
| mlc_llm_module | SHARED | TVM module variant, links against the full tvm target (not just runtime) CMakeLists.txt142-143 |
| mlc_llm_cpp_tests | Executable | C++ unit test binary, enabled by BUILD_CPP_TEST=ON CMakeLists.txt123-134 |

 Sources: [CMakeLists.txt78-143](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/CMakeLists.txt#L78-L143)

 
### CMake Options

 
| Option | Default | Description |
|---|---|---|
| MLC_HIDE_PRIVATE_SYMBOLS | ON | Passes -fvisibility=hidden on non-MSVC CMakeLists.txt26-41 |
| MLC_LLM_BUILD_PYTHON_MODULE | OFF | Configures install paths for Python wheel packaging CMakeLists.txt27-28 |
| BUILD_CPP_TEST | OFF | Builds mlc_llm_cpp_tests against GoogleTest CMakeLists.txt43 |
| MLC_LLM_INSTALL_STATIC_LIB | (unset) | When set, installs only static libraries and Rust-built libtokenizers_c CMakeLists.txt30-173 |

 Sources: [CMakeLists.txt26-43](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/CMakeLists.txt#L26-L43) [CMakeLists.txt162-173](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/CMakeLists.txt#L162-L173)

 
### TVM Runtime Minimization

 To keep the binary size small, MLC LLM disables unnecessary TVM runtime components by default:

 
```

```

 Sources: [CMakeLists.txt50-58](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/CMakeLists.txt#L50-L58)

 
### Compile Definitions

 The object library `mlc_llm_objs` is built with the following compile definitions:

 
| Definition | Value | Effect |
|---|---|---|
| __STDC_FORMAT_MACROS | 1 | Enables standard integer format macros CMakeLists.txt82 |
| XGRAMMAR_ENABLE_LOG_DEBUG | 0 | Disables XGrammar debug logging CMakeLists.txt83 |
| MLC_LLM_EXPORTS | (defined) | Marks symbols for export CMakeLists.txt86 |
| TVM_LOG_DEBUG | (defined in Debug) | Enables verbose TVM logging when CMAKE_BUILD_TYPE is Debug CMakeLists.txt117-121 |
| MLC_SINGLE_GPU_ONLY | (defined in Android) | Defined when building for Android android/mlc4j/CMakeLists.txt87 |

 Sources: [CMakeLists.txt82-121](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/CMakeLists.txt#L82-L121) [android/mlc4j/CMakeLists.txt87](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/android/mlc4j/CMakeLists.txt#L87-L87)

 
---

 
## Third-Party Submodules

 MLC LLM relies on several submodules located in `3rdparty/`.

 
| Submodule | Path | Role |
|---|---|---|
| tvm | 3rdparty/tvm | Core compiler and runtime backend CMakeLists.txt63 |
| tokenizers-cpp | 3rdparty/tokenizers-cpp | C++ bindings for HuggingFace tokenizers CMakeLists.txt70 |
| xgrammar | 3rdparty/xgrammar | Structured output generation CMakeLists.txt73 |
| googletest | 3rdparty/googletest | C++ unit testing CMakeLists.txt125 |
| stb | 3rdparty/stb | Image loading for multimodal models CMakeLists.txt88 |

 Sources: [CMakeLists.txt63-125](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/CMakeLists.txt#L63-L125)

 The `TVM_SOURCE_DIR` can be overridden via environment variables or CMake variables; it defaults to `3rdparty/tvm` [CMakeLists.txt59-66](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/CMakeLists.txt#L59-L66)

 
---

 
## Python Package: `pyproject.toml` and `scikit-build-core`

 The Python package is built using `scikit-build-core`, which provides a modern interface between `pip` and CMake.

 
```

```

 Sources: [pyproject.toml65-84](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/pyproject.toml#L65-L84)

 
### Python Runtime Dependencies

 Key dependencies include:

 
 - `apache-tvm-ffi`: TVM Foreign Function Interface.
 - `flashinfer-python`: High-performance kernels (Linux only).
 - `torch`, `transformers`, `safetensors`: For model weight conversion and loading.
 - `fastapi`, `uvicorn`: For the REST API server.
 
 Sources: [pyproject.toml37-55](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/pyproject.toml#L37-L55) [python/requirements.txt1-17](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/requirements.txt#L1-L17)

 
---

 
## Interactive CMake Configuration: `gen_cmake_config.py`

 [cmake/gen_cmake_config.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cmake/gen_cmake_config.py) provides an interactive CLI to generate `config.cmake`. It prompts the user for the `TVM_SOURCE_DIR` and various hardware backends.

 **Interactive Configuration Flow**

 
```

```

 Sources: [cmake/gen_cmake_config.py1-60](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/cmake/gen_cmake_config.py#L1-L60)

 
---

 
## CI Pipeline

 MLC LLM uses **Jenkins** as the primary CI engine, with **GitHub Actions** for documentation and Windows builds.

 
### Infrastructure: Docker Runner (`ci/bash.sh`)

 Jenkins tasks run inside specialized Docker containers managed by [ci/bash.sh](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/bash.sh) It handles environment variable passthrough and GPU device mapping [ci/bash.sh1-103](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/bash.sh#L1-L103)

 **Docker images used in CI:**

 
 - `mlcaidev/ci-cpu`: General linting and CPU tasks [ci/jenkinsfile.groovy20](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/jenkinsfile.groovy#L20-L20)
 - `mlcaidev/package-cu128`: CUDA 12.8 packaging [ci/jenkinsfile.groovy25](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/jenkinsfile.groovy#L25-L25)
 - `mlcaidev/package-rocm61`: ROCm 6.1 packaging [ci/jenkinsfile.groovy26](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/jenkinsfile.groovy#L26-L26)
 
 
### Jenkins Pipeline Stages

 **CI Pipeline Overview**

 
```

```

 Sources: [ci/jenkinsfile.groovy64-272](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/jenkinsfile.groovy#L64-L272)

 
#### Stage: Build (`build_lib.sh`)

 The script `ci/task/build_lib.sh` prepares the environment, writes `config.cmake` for the target GPU, and builds the Python wheel.

 
 - **CUDA**: Sets `USE_CUDA`, `USE_CUBLAS`, and `USE_NCCL` [ci/task/build_lib.sh33-35](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/task/build_lib.sh#L33-L35)
 - **ROCm**: Sets `USE_ROCM` and `USE_RCCL` [ci/task/build_lib.sh26-27](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/task/build_lib.sh#L26-L27)
 - **Metal**: Sets `USE_METAL` [ci/task/build_lib.sh38](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/task/build_lib.sh#L38-L38)
 
 On Linux, `auditwheel repair` is used to bundle dependencies into the wheel, excluding system libraries like `libcuda` or `libvulkan` [ci/task/build_lib.sh45-60](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/task/build_lib.sh#L45-L60)

 
#### Stage: Model Compilation (`test_model_compile.sh`)

 This stage validates that the engine can compile models for various targets. It installs the nightly wheels and runs `tests/python/integration/test_model_compile.py` [ci/task/test_model_compile.sh8-42](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/task/test_model_compile.sh#L8-L42)

 
### GitHub Actions

 
 - **Windows Build**: Uses `ci/task/build_win.bat` on `windows-latest` [.github/workflows/windows-build.yaml](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/.github/workflows/windows-build.yaml)
 - **Documentation**: Generates and deploys the site using `scripts/build_site.sh` [.github/workflows/documentation.yaml](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/.github/workflows/documentation.yaml)
 
 
---

 
## Build Flow Summary

 **End-to-end build flow**

 
```

```

 Sources: [pyproject.toml65-86](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/pyproject.toml#L65-L86) [CMakeLists.txt67-217](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/CMakeLists.txt#L67-L217) [ci/task/build_lib.sh53-65](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ci/task/build_lib.sh#L53-L65)
