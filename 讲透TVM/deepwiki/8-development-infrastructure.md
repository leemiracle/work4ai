> 来源: [https://deepwiki.com/apache/tvm/8-development-infrastructure](https://deepwiki.com/apache/tvm/8-development-infrastructure)
> DeepWiki apache/tvm | Last indexed: 31 August 2026 (b16cde

# Development Infrastructure

  Relevant source files 
 - [.gitmodules](https://github.com/apache/tvm/blob/b16cdecb/.gitmodules)
 - [CMakeLists.txt](https://github.com/apache/tvm/blob/b16cdecb/CMakeLists.txt)
 - [LICENSE](https://github.com/apache/tvm/blob/b16cdecb/LICENSE)
 - [cmake/config.cmake](https://github.com/apache/tvm/blob/b16cdecb/cmake/config.cmake)
 - [cmake/modules/CUDA.cmake](https://github.com/apache/tvm/blob/b16cdecb/cmake/modules/CUDA.cmake)
 - [cmake/modules/Hexagon.cmake](https://github.com/apache/tvm/blob/b16cdecb/cmake/modules/Hexagon.cmake)
 - [cmake/utils/FindCUDA.cmake](https://github.com/apache/tvm/blob/b16cdecb/cmake/utils/FindCUDA.cmake)
 - [docs/arch/device_target_interactions.rst](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/device_target_interactions.rst)
 - [docs/arch/introduction_to_module_serialization.rst](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/introduction_to_module_serialization.rst)
 - [docs/conf.py](https://github.com/apache/tvm/blob/b16cdecb/docs/conf.py)
 - [docs/deep_dive/relax/tutorials/relax_transformation.py](https://github.com/apache/tvm/blob/b16cdecb/docs/deep_dive/relax/tutorials/relax_transformation.py)
 - [docs/errors.rst](https://github.com/apache/tvm/blob/b16cdecb/docs/errors.rst)
 - [docs/index.rst](https://github.com/apache/tvm/blob/b16cdecb/docs/index.rst)
 - [docs/reference/api/links.rst](https://github.com/apache/tvm/blob/b16cdecb/docs/reference/api/links.rst)
 - [tests/scripts/setup-pytest-env.sh](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/setup-pytest-env.sh)
 - [tests/scripts/task_config_build_arm.sh](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_config_build_arm.sh)
 - [tests/scripts/task_config_build_cpu.sh](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_config_build_cpu.sh)
 - [tests/scripts/task_config_build_gpu.sh](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_config_build_gpu.sh)
 - [tests/scripts/task_config_build_gpu_other.sh](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_config_build_gpu_other.sh)
 - [tests/scripts/task_config_build_wasm.sh](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_config_build_wasm.sh)
 - [tests/scripts/task_python_docs.sh](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_python_docs.sh)
 - [tests/scripts/task_python_unittest.sh](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_python_unittest.sh)
 - [tests/scripts/task_python_unittest_gpuonly.sh](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_python_unittest_gpuonly.sh)
 
  This page documents TVM's development infrastructure including the build system, continuous integration/continuous deployment (CI/CD) pipeline, testing framework, documentation generation, and community governance model. This infrastructure enables contributors to build, test, and deploy TVM across multiple platforms and hardware targets.

 For information about runtime systems, see [Runtime Systems](https://deepwiki.com/apache/tvm/7-runtime-systems). For details about specific build targets and code generation backends, see [Code Generation](https://deepwiki.com/apache/tvm/6-code-generation).

 
---

 
## Build System

 TVM uses CMake as its cross-platform build system. The build is configured through a template file that users customize for their target platform and enabled features.

 
### Build Configuration Flow

 
```

```

 **Sources:** [CMakeLists.txt1-144](https://github.com/apache/tvm/blob/b16cdecb/CMakeLists.txt#L1-L144) [cmake/config.cmake1-37](https://github.com/apache/tvm/blob/b16cdecb/cmake/config.cmake#L1-L37)

 
### Core Build Options

 The build system exposes numerous configuration options through CMake variables defined via the `tvm_option` macro in [CMakeLists.txt43-116](https://github.com/apache/tvm/blob/b16cdecb/CMakeLists.txt#L43-L116) Key categories include:

 
| Category | Options | Description |
|---|---|---|
| Backend Runtimes | USE_CUDA, USE_ROCM, USE_OPENCL, USE_VULKAN, USE_METAL | Enable GPU/accelerator backends CMakeLists.txt43-61 |
| LLVM Support | USE_LLVM, USE_MLIR | Enable LLVM-based code generation CMakeLists.txt71-72 |
| Contrib Libraries | USE_CUDNN, USE_CUBLAS, USE_CUTLASS, USE_DNNL | Enable external library integrations CMakeLists.txt94-98 |
| Build Features | USE_RPC, USE_THREADS, USE_CCACHE | Core build features CMakeLists.txt69-85 |
| Testing | USE_GTEST, USE_HEXAGON_GTEST | Testing framework support CMakeLists.txt66-82 |
| Optimization | HIDE_PRIVATE_SYMBOLS, BUILD_STATIC_RUNTIME | Build optimizations CMakeLists.txt79-81 |

 **Sources:** [CMakeLists.txt43-116](https://github.com/apache/tvm/blob/b16cdecb/CMakeLists.txt#L43-L116) [cmake/config.cmake43-223](https://github.com/apache/tvm/blob/b16cdecb/cmake/config.cmake#L43-L223)

 
### Platform-Specific Build Configurations

 TVM maintains standard build configurations for different platforms and test scenarios via shell scripts that append settings to `config.cmake`:

 
| Configuration Script | Target | Key Features |
|---|---|---|
| task_config_build_cpu.sh | CPU builds | LLVM 17, DNNL, symbol hiding tests/scripts/task_config_build_cpu.sh26-37 |
| task_config_build_gpu.sh | GPU builds | CUDA, cuDNN, cuBLAS, Vulkan, OpenCL, CUTLASS tests/scripts/task_config_build_gpu.sh26-43 |
| task_config_build_arm.sh | ARM builds | LLVM 17, RPC support tests/scripts/task_config_build_arm.sh27-31 |
| task_config_build_wasm.sh | WebAssembly | Emscripten/WASM builds tests/scripts/task_config_build_wasm.sh1-25 |

 Example CPU configuration from [tests/scripts/task_config_build_cpu.sh26-32](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_config_build_cpu.sh#L26-L32):

 
```

```

 **Sources:** [tests/scripts/task_config_build_cpu.sh1-37](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_config_build_cpu.sh#L1-L37) [tests/scripts/task_config_build_gpu.sh1-43](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_config_build_gpu.sh#L1-L43) [tests/scripts/task_config_build_arm.sh1-31](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_config_build_arm.sh#L1-L31)

 
---

 
## CI/CD Pipeline

 TVM uses a Jenkins-based CI/CD system with Docker containers for reproducible builds and tests across multiple platforms.

 
### CI Automation and Docker

 The CI pipeline relies on specialized bash tasks and Python wrappers to manage environment consistency. The `tests/scripts/ci.py` script serves as a local entry point to replicate CI behavior using Docker.

 
```

```

 **Sources:** [tests/scripts/task_config_build_cpu.sh1-37](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_config_build_cpu.sh#L1-L37) [tests/scripts/task_config_build_gpu.sh1-43](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_config_build_gpu.sh#L1-L43) [tests/scripts/setup-pytest-env.sh1-98](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/setup-pytest-env.sh#L1-L98)

 
---

 
## Testing Infrastructure

 TVM's testing infrastructure supports Python, C++, and integration tests with parallel execution and result reporting.

 
### Pytest Environment Setup

 The pytest environment is configured through [tests/scripts/setup-pytest-env.sh1-98](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/setup-pytest-env.sh#L1-L98):

 
```

```

 **Key Features:**

 
 - **`run_pytest()` Function:** [tests/scripts/setup-pytest-env.sh49-98](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/setup-pytest-env.sh#L49-L98)

 
 - Automatically adds `--reruns=3` for flaky test handling if the plugin is available [tests/scripts/setup-pytest-env.sh70-75](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/setup-pytest-env.sh#L70-L75)
 - Sets default parallelism with `-n=1` unless overridden [tests/scripts/setup-pytest-env.sh79-83](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/setup-pytest-env.sh#L79-L83)
 - Produces JUnit XML output for Jenkins integration [tests/scripts/setup-pytest-env.sh87-91](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/setup-pytest-env.sh#L87-L91)
 - **Error Accumulation:** [tests/scripts/setup-pytest-env.sh38-47](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/setup-pytest-env.sh#L38-L47) Uses a bash `trap` on exit to invoke `ci/scripts/jenkins/pytest_wrapper.py` if any tests in the `pytest_errors` array failed.
 
 **Sources:** [tests/scripts/setup-pytest-env.sh1-98](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/setup-pytest-env.sh#L1-L98) [tests/scripts/task_python_unittest.sh1-27](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_python_unittest.sh#L1-L27)

 
---

 
## Documentation System

 TVM uses Sphinx to generate its documentation, combining Python docstrings, tutorials, and multi-language API references.

 
### Sphinx Configuration

 The primary configuration resides in `docs/conf.py`. It includes logic for:

 
 - Versioning based on `tvm.__version__` [docs/conf.py73-74](https://github.com/apache/tvm/blob/b16cdecb/docs/conf.py#L73-L74)
 - Monkey-patching `sphinx_gallery` to support custom headers and Colab buttons [docs/conf.py77-174](https://github.com/apache/tvm/blob/b16cdecb/docs/conf.py#L77-L174)
 - Handling ignored warnings during build to maintain CI stability [tests/scripts/task_python_docs.sh68-100](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_python_docs.sh#L68-L100)
 
 
### Documentation Build Pipeline

 The build process is orchestrated by `tests/scripts/task_python_docs.sh`:

 
 - **Sphinx Precheck:** Runs a fast build without tutorials to catch immediate warnings [tests/scripts/task_python_docs.sh46-58](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_python_docs.sh#L46-L58)
 - **Main HTML Build:** Executes tutorials and generates full documentation [tests/scripts/task_python_docs.sh136-141](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_python_docs.sh#L136-L141)
 - **API References:** 
 - **C++:** Doxygen [tests/scripts/task_python_docs.sh155](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_python_docs.sh#L155-L155)
 - **Java:** Maven Javadoc [tests/scripts/task_python_docs.sh159](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_python_docs.sh#L159-L159)
 - **TypeScript:** TypeDoc [tests/scripts/task_python_docs.sh162-165](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_python_docs.sh#L162-L165)
 
 **Sources:** [docs/conf.py1-180](https://github.com/apache/tvm/blob/b16cdecb/docs/conf.py#L1-L180) [tests/scripts/task_python_docs.sh1-185](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_python_docs.sh#L1-L185)

 
---

 
## Community and Governance

 TVM is an Apache Software Foundation project. For detailed information on the governance model, committership, and contribution guidelines, see [Community and Governance](https://deepwiki.com/apache/tvm/8.4-community-and-governance).

 For details on specific infrastructure components, refer to the child pages:

 
 - [Build System](https://deepwiki.com/apache/tvm/8.1-build-system)
 - [CI/CD Pipeline](https://deepwiki.com/apache/tvm/8.2-cicd-pipeline)
 - [Documentation System](https://deepwiki.com/apache/tvm/8.3-documentation-system)
 - [Community and Governance](https://deepwiki.com/apache/tvm/8.4-community-and-governance)
