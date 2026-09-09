> 来源: [https://deepwiki.com/triton-lang/triton/6-build-system-and-infrastructure](https://deepwiki.com/triton-lang/triton/6-build-system-and-infrastructure)
> DeepWiki triton-lang/triton | Last indexed: 20 August 2026 (f89384

# Build System and Infrastructure

  Relevant source files 
 - [.github/workflows/llvm-build.yml](https://github.com/triton-lang/triton/blob/f893845b/.github/workflows/llvm-build.yml)
 - [.github/workflows/wheels.yml](https://github.com/triton-lang/triton/blob/f893845b/.github/workflows/wheels.yml)
 - [.gitignore](https://github.com/triton-lang/triton/blob/f893845b/.gitignore)
 - [CMakeLists.txt](https://github.com/triton-lang/triton/blob/f893845b/CMakeLists.txt)
 - [Makefile](https://github.com/triton-lang/triton/blob/f893845b/Makefile)
 - [README.md](https://github.com/triton-lang/triton/blob/f893845b/README.md?plain=1)
 - [bin/CMakeLists.txt](https://github.com/triton-lang/triton/blob/f893845b/bin/CMakeLists.txt)
 - [bin/triton-tensor-layout.cpp](https://github.com/triton-lang/triton/blob/f893845b/bin/triton-tensor-layout.cpp)
 - [cmake/llvm-build-info.json](https://github.com/triton-lang/triton/blob/f893845b/cmake/llvm-build-info.json)
 - [cmake/nvidia-toolchain-version.json](https://github.com/triton-lang/triton/blob/f893845b/cmake/nvidia-toolchain-version.json)
 - [docs/getting-started/installation.rst](https://github.com/triton-lang/triton/blob/f893845b/docs/getting-started/installation.rst)
 - [docs/python-api/triton.language.rst](https://github.com/triton-lang/triton/blob/f893845b/docs/python-api/triton.language.rst)
 - [python/build_helpers.py](https://github.com/triton-lang/triton/blob/f893845b/python/build_helpers.py)
 - [python/src/main.cc](https://github.com/triton-lang/triton/blob/f893845b/python/src/main.cc)
 - [scripts/build-llvm-project.sh](https://github.com/triton-lang/triton/blob/f893845b/scripts/build-llvm-project.sh)
 - [setup.py](https://github.com/triton-lang/triton/blob/f893845b/setup.py)
 - [test/Tools/tensor_layout_print.mlir](https://github.com/triton-lang/triton/blob/f893845b/test/Tools/tensor_layout_print.mlir)
 - [test/TritonGPU/pipeline-loop-nest.mlir](https://github.com/triton-lang/triton/blob/f893845b/test/TritonGPU/pipeline-loop-nest.mlir)
 - [test/lib/CMakeLists.txt](https://github.com/triton-lang/triton/blob/f893845b/test/lib/CMakeLists.txt)
 - [test/lib/Dialect/CMakeLists.txt](https://github.com/triton-lang/triton/blob/f893845b/test/lib/Dialect/CMakeLists.txt)
 - [third_party/f2reduce/f2reduce.cpp](https://github.com/triton-lang/triton/blob/f893845b/third_party/f2reduce/f2reduce.cpp)
 
  
## Purpose and Scope

 This document describes the build system and infrastructure that compiles Triton from source, manages dependencies (particularly LLVM), and produces distributable packages. It covers the CMake-based build configuration, CI/CD workflows for automated building and testing, and the overall architecture that ties together the C++ compiler components, Python bindings, and backend plugins.

 For details on Python package installation and setup, see [Python Package Setup and Installation](https://deepwiki.com/triton-lang/triton/6.1-python-package-setup-and-installation). For CMake configuration specifics and LLVM integration details, see [CMake Build System and LLVM Integration](https://deepwiki.com/triton-lang/triton/6.2-cmake-build-system-and-llvm-integration). For the backend plugin architecture, see [Backend Plugin System](https://deepwiki.com/triton-lang/triton/6.3-backend-plugin-system).

 
## Build System Architecture

 The Triton build system is structured as a multi-layer CMake project that orchestrates the compilation of MLIR dialects, compiler passes, backend implementations, and Python bindings.

 
### Build System Component Structure

 
```

```

 **Sources:** [CMakeLists.txt1-175](https://github.com/triton-lang/triton/blob/f893845b/CMakeLists.txt#L1-L175) [setup.py57-126](https://github.com/triton-lang/triton/blob/f893845b/setup.py#L57-L126) [python/src/main.cc1-10](https://github.com/triton-lang/triton/blob/f893845b/python/src/main.cc#L1-L10) [setup.py23](https://github.com/triton-lang/triton/blob/f893845b/setup.py#L23-L23)

 
### Build Configuration Logic

 Triton uses a Python-based helper system to manage complex CMake variables and third-party dependencies, ensuring that the environment is correctly set up before the C++ compilation begins.

 
| Component | Logic Location | Role |
|---|---|---|
| Build Helpers | python/build_helpers.py | Downloads pinned dependencies (LLVM, JSON) and generates CMake variables |
| Setup Script | setup.py | Orchestrates the build_ext command and manages backend submodule initialization |
| CMake Entry | CMakeLists.txt | Defines targets and integrates Python-generated variable files |

 **Sources:** [python/build_helpers.py24-58](https://github.com/triton-lang/triton/blob/f893845b/python/build_helpers.py#L24-L58) [setup.py195-215](https://github.com/triton-lang/triton/blob/f893845b/setup.py#L195-L215) [CMakeLists.txt121-135](https://github.com/triton-lang/triton/blob/f893845b/CMakeLists.txt#L121-L135)

 
## LLVM Dependency Management

 Triton depends on a specific version of LLVM/MLIR, managed through a pinned hash system. Because LLVM does not have a stable API, Triton must build against a specific revision to ensure compatibility.

 
### LLVM Version Pinning

 The LLVM version is controlled by metadata files in the `cmake/` directory:

 
 - `cmake/llvm-info.json`: Contains the `llvm_hash` for standard builds [README.md83-86](https://github.com/triton-lang/triton/blob/f893845b/README.md?plain=1#L83-L86)
 - `cmake/llvm-build-info.json`: Used by CI to determine the commit for automated builds [.github/workflows/llvm-build.yml7-12](https://github.com/triton-lang/triton/blob/f893845b/.github/workflows/llvm-build.yml#L7-L12)
 
 
### LLVM Build Configuration

 When building LLVM from source, Triton requires specific projects and targets to be enabled:

 
```

```

 **Sources:** [.github/workflows/llvm-build.yml136-153](https://github.com/triton-lang/triton/blob/f893845b/.github/workflows/llvm-build.yml#L136-L153) [README.md94-100](https://github.com/triton-lang/triton/blob/f893845b/README.md?plain=1#L94-L100)

 
## Build Configuration and Options

 
### CMake Build Options

 The root [CMakeLists.txt](https://github.com/triton-lang/triton/blob/f893845b/CMakeLists.txt) defines several build options that control the scope of the compilation:

 
| Option | Default | Purpose |
|---|---|---|
| TRITON_BUILD_PYTHON_MODULE | OFF | Build Python Triton bindings (usually enabled by setup.py) |
| TRITON_BUILD_PROTON | ON | Build the Triton Proton profiler |
| TRITON_STABLE_ABI | OFF | Build with Python Stable ABI (abi3) for Python 3.12+ |
| TRITON_BUILD_UT | ON | Build C++ Triton Unit Tests |
| TRITON_BUILD_WITH_CCACHE | ON | Use ccache to speed up repeated compilations |
| TRITON_OFFLINE_BUILD | OFF | Build without downloading dependencies (requires local syspaths) |

 **Sources:** [CMakeLists.txt20-26](https://github.com/triton-lang/triton/blob/f893845b/CMakeLists.txt#L20-L26)

 
### Environment Variables for Building

 Users can influence the build process via environment variables, particularly for locating dependencies or optimizing build speed:

 
 - `TRITON_BUILD_WITH_CLANG_LLD`: Set to `true` to use `clang` and `lld` for faster builds [README.md119-120](https://github.com/triton-lang/triton/blob/f893845b/README.md?plain=1#L119-L120)
 - `TRITON_HOME`: Changes the location of the `.triton` directory for cache and downloads [README.md124-127](https://github.com/triton-lang/triton/blob/f893845b/README.md?plain=1#L124-L127)
 - `MAX_JOBS`: Limits the number of concurrent compiler processes to prevent OOM [README.md129-131](https://github.com/triton-lang/triton/blob/f893845b/README.md?plain=1#L129-L131)
 - `LLVM_SYSPATH`: Points to a custom LLVM installation [CMakeLists.txt32](https://github.com/triton-lang/triton/blob/f893845b/CMakeLists.txt#L32-L32)
 - `TRITON_PLUGIN_DIRS`: Semicolon-separated list of paths to external backend plugins [setup.py118-121](https://github.com/triton-lang/triton/blob/f893845b/setup.py#L118-L121)
 
 
## CI/CD Infrastructure

 The Triton project uses GitHub Actions for continuous integration, covering documentation, LLVM pre-builds, and Python wheels.

 
### Automated Pipelines

 
 - **LLVM Build Pipeline**: Triggered by changes to `cmake/llvm-build-info.json`. It builds LLVM for Ubuntu (x64/ARM64), AlmaLinux, macOS, and Windows, then uploads the artifacts to Azure Blob Storage [.github/workflows/llvm-build.yml1-41](https://github.com/triton-lang/triton/blob/f893845b/.github/workflows/llvm-build.yml#L1-L41)
 - **Wheels Pipeline**: Builds binary wheels for CPython 3.10-3.14 across x86_64 and aarch64 using `cibuildwheel`. It also supports building `abi3` wheels for Python 3.12+ [.github/workflows/wheels.yml1-114](https://github.com/triton-lang/triton/blob/f893845b/.github/workflows/wheels.yml#L1-L114)
 - **Documentation Pipeline**: Automatically builds and publishes the Sphinx documentation to `gh-pages` [README.md4](https://github.com/triton-lang/triton/blob/f893845b/README.md?plain=1#L4-L4)
 
 
### Hardware Toolchain Management

 Triton tracks specific versions of NVIDIA tools (ptxas, cupti, etc.) in `cmake/nvidia-toolchain-version.json` to ensure consistency across build environments [CMakeLists.txt143-144](https://github.com/triton-lang/triton/blob/f893845b/CMakeLists.txt#L143-L144) The build helper `python/build_helpers.py` uses this information to download and copy the necessary binaries into the build tree [CMakeLists.txt146-153](https://github.com/triton-lang/triton/blob/f893845b/CMakeLists.txt#L146-L153)

 
## Development Workflow

 Triton provides a `Makefile` to simplify common development tasks.

 
| Command | Action |
|---|---|
| make dev-install | Installs build-time dependencies and Triton in editable mode Makefile106-108 |
| make test | Runs lit tests, C++ unit tests, and Python tests Makefile85-86 |
| make test-interpret | Runs language tests using the Triton interpreter (no GPU required) Makefile63-68 |
| make dev-install-llvm | Builds LLVM from source and installs Triton against it Makefile110-117 |
| make triton-opt | Builds the triton-opt tool for IR inspection Makefile21-23 |

 **Sources:** [Makefile1-142](https://github.com/triton-lang/triton/blob/f893845b/Makefile#L1-L142) [README.md155-171](https://github.com/triton-lang/triton/blob/f893845b/README.md?plain=1#L155-L171)
