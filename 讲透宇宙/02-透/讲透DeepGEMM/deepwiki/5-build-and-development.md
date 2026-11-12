> 来源: [https://deepwiki.com/deepseek-ai/DeepGEMM/5-build-and-development](https://deepwiki.com/deepseek-ai/DeepGEMM/5-build-and-development)
> DeepWiki deepseek-ai/DeepGEMM

# Build and Development

  Relevant source files 
 - [.github/workflows/publish.yml](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/.github/workflows/publish.yml)
 - [csrc/jit/handle.hpp](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/handle.hpp)
 - [setup.py](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/setup.py)
 
  
## Purpose and Scope

 This section provides a comprehensive guide to building, developing, and extending DeepGEMM. It covers the build system architecture, compilation options, distribution strategy, and development workflows. For detailed instructions on building from source, see [Building from Source](https://deepwiki.com/deepseek-ai/DeepGEMM/5.1-building-from-source). For information about the CI/CD pipeline and wheel distribution, see [Distribution and CI/CD](https://deepwiki.com/deepseek-ai/DeepGEMM/5.2-distribution-and-cicd). For testing and validation strategies, see [Testing Framework](https://deepwiki.com/deepseek-ai/DeepGEMM/5.3-testing-framework). For deep technical details on the JIT compilation internals, see [JIT System Internals](https://deepwiki.com/deepseek-ai/DeepGEMM/5.4-jit-system-internals). For guidance on contributing new features, see [Extending DeepGEMM](https://deepwiki.com/deepseek-ai/DeepGEMM/5.5-extending-deepgemm).

 
---

 
## Build System Architecture

 DeepGEMM employs a dual-layer build strategy: compile-time building of the Python extension module (`_C`) and runtime JIT compilation of CUDA kernels. This design minimizes installation time while maximizing kernel specialization.

 
### Build System Components

 Title: DeepGEMM Build Pipeline

 
```

```

 **Sources**: [setup.py1-191](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/setup.py#L1-L191)

 
### Key Build System Classes

 
| Class | File | Purpose |
|---|---|---|
| CustomBuildPy | setup.py114-166 | Custom build command that prepares include directories, generates environment variables file, and creates Python type stubs |
| CachedWheelsCommand | setup.py168-191 | Custom wheel distribution command that attempts to download pre-built wheels before compiling from source |
| CUDAExtension | setup.py106-111 | PyTorch extension builder that compiles csrc/python_api.cpp with CUDA support |

 The build process executes in three phases:

 
 - **Prepare Phase** ([setup.py149-165](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/setup.py#L149-L165)): Copy CUTLASS/CuTe headers from `third-party/` to `build_lib/deep_gemm/include/`
 - **Generate Phase** ([setup.py128-147](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/setup.py#L128-L147)): Create `envs.py` with persistent environment variables and generate `_C.pyi` type stubs via `generate_pyi_file` ([setup.py19](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/setup.py#L19-L19))
 - **Compile Phase** ([setup.py102-111](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/setup.py#L102-L111)): Compile `csrc/python_api.cpp` into `_C` extension module unless `DG_SKIP_CUDA_BUILD=1`
 
 
---

 
## Build Configuration System

 
### Environment Variables

 DeepGEMM's build and runtime behavior is controlled through environment variables. These fall into two categories: build-time configuration and runtime JIT configuration.

 
#### Build-Time Environment Variables

 
| Variable | Type | Default | Purpose |
|---|---|---|---|
| DG_SKIP_CUDA_BUILD | int | 0 | Skip compilation of CUDA extension module (useful for documentation builds) |
| DG_FORCE_BUILD | int | 0 | Force local compilation even if pre-built wheel is available |
| DG_USE_LOCAL_VERSION | int | 1 | Append Git commit hash to version string for development builds |
| DG_JIT_USE_RUNTIME_API | int | 0 | Use CUDA Runtime API (cudaKernel_t) instead of Driver API (CUfunction) for kernel handles |

 **Sources**: [setup.py22-31](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/setup.py#L22-L31)

 
#### Runtime JIT Environment Variables

 The following variables are embedded into the installed package via [setup.py140-147](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/setup.py#L140-L147) and affect JIT compilation behavior:

 
| Variable | Effect | Default |
|---|---|---|
| DG_JIT_CACHE_DIR | Directory for storing compiled kernel cubins | ~/.deep_gemm |
| DG_JIT_PRINT_COMPILER_COMMAND | Print NVCC/NVRTC commands during compilation | Not set |
| DG_JIT_CPP_STANDARD | C++ standard version for kernel compilation | c++17 |

 These variables are captured at build time and written to `deep_gemm/envs.py` for runtime access.

 
### Compiler Flags

 The C++ compiler flags are configured in [setup.py28-31](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/setup.py#L28-L31):

 
```

```

 The `_GLIBCXX_USE_CXX11_ABI` flag is critical for ABI compatibility with PyTorch's own compilation settings. Mismatched ABI settings cause link failures or runtime crashes.

 **Sources**: [setup.py27-31](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/setup.py#L27-L31)

 
---

 
## Kernel Handle Abstraction

 DeepGEMM abstracts over two CUDA APIs for loading and launching kernels: the CUDA Driver API and the CUDA Runtime API (available since CUDA 12.8). This abstraction enables flexibility in deployment environments.

 
### Handle Type Hierarchy

 Title: DeepGEMM Kernel Handle Abstraction

 
```

```

 **Sources**: [csrc/jit/handle.hpp1-169](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/handle.hpp#L1-L169)

 
### API Selection Logic

 The kernel handle implementation is selected at compile time via preprocessor directives ([csrc/jit/handle.hpp48-54](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/handle.hpp#L48-L54) [csrc/jit/handle.hpp118-122](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/handle.hpp#L118-L122)):

 
```

```

 **Key Implementation Functions**:

 
| Function | Driver API Path | Runtime API Path |
|---|---|---|
| load_kernel() | cuModuleLoad → cuModuleGetFunction | cudaLibraryLoadFromFile → cudaLibraryGetKernel |
| unload_library() | cuModuleUnload | cudaLibraryUnload |
| construct_launch_config() | Populate CUlaunchConfig struct | Populate cudaLaunchConfig_t struct |
| launch_kernel() | cuLaunchKernelEx | cudaLaunchKernelExC |

 **Sources**: [csrc/jit/handle.hpp58-163](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/handle.hpp#L58-L163)

 
### Lazy Symbol Loading

 The Driver API functions are loaded lazily to avoid hard dependencies on `libcuda.so.1` ([csrc/jit/handle.hpp14-21](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/handle.hpp#L14-L21)):

 
```

```

 This design allows the extension module to be imported even when the CUDA driver is not installed, which is useful for documentation generation and CI environments where CUDA is unavailable. The `DECL_LAZY_CUDA_DRIVER_FUNCTION` macro ([csrc/jit/handle.hpp24-34](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/handle.hpp#L24-L34)) handles the dynamic symbol resolution via `dlsym`.

 **Sources**: [csrc/jit/handle.hpp14-45](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/handle.hpp#L14-L45)

 
---

 
## Version Management and Distribution

 DeepGEMM employs a versioning and distribution strategy to minimize installation time while supporting a wide range of environment configurations.

 
### Version String Generation

 The version string format depends on the `DG_USE_LOCAL_VERSION` flag ([setup.py54-73](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/setup.py#L54-L73)):

 
```

```

 **Examples**:

 
 - Release build: `1.0.0`
 - Development build: `1.0.0+a1b2c3d`
 - No Git available: `1.0.0+local`
 
 **Sources**: [setup.py54-73](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/setup.py#L54-L73)

 
### CI/CD and Wheel Distribution

 DeepGEMM uses GitHub Actions for automated building and publishing. The `publish.yml` workflow ([.github/workflows/publish.yml8-15](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/.github/workflows/publish.yml#L8-L15)) triggers on new tags to build a matrix of wheels.

 **Matrix Build Configuration**:

 
 - **Python Versions**: 3.8 to 3.13 ([.github/workflows/publish.yml44](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/.github/workflows/publish.yml#L44-L44))
 - **PyTorch Versions**: 2.4.0 to 2.8.0 ([.github/workflows/publish.yml45](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/.github/workflows/publish.yml#L45-L45))
 - **CUDA Version**: 12.9.1 ([.github/workflows/publish.yml46](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/.github/workflows/publish.yml#L46-L46))
 - **C++11 ABI**: TRUE/FALSE variants to support both standard wheels and NGC images ([.github/workflows/publish.yml51](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/.github/workflows/publish.yml#L51-L51))
 
 The `CachedWheelsCommand` class ([setup.py168-191](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/setup.py#L168-L191)) implements an intelligent wheel selection mechanism that attempts to download these pre-built wheels during installation if `DG_FORCE_BUILD` is not set.

 **Sources**: [.github/workflows/publish.yml35-67](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/.github/workflows/publish.yml#L35-L67) [setup.py168-191](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/setup.py#L168-L191)

 
### Wheel Filename Construction

 The wheel filename encodes compatibility requirements ([setup.py83-99](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/setup.py#L83-L99)):

 
```
deep_gemm-{version}+cu{cuda_major}-torch{torch_version}-cxx11abi{abi}-{python_tag}-{platform}.whl
```

 The URL template is defined at [setup.py51](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/setup.py#L51-L51):

 
```

```

 **Sources**: [setup.py51-99](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/setup.py#L51-L99)

 
---

 
## Development Workflow

 
### Source Tree Structure

 
```
DeepGEMM/
├── setup.py                      # Build orchestration
├── .github/workflows/            # CI/CD pipelines (publish.yml, _build.yml)
├── deep_gemm/
│   ├── __init__.py               # Python package entry point
│   ├── include/                  # Headers (populated during build)
│   └── envs.py                   # Generated environment variables
├── csrc/
│   ├── python_api.cpp            # Python extension entry point
│   └── jit/
│       └── handle.hpp            # Kernel handle abstraction
├── third-party/
│   ├── cutlass/                  # CUTLASS library submodule
│   └── fmt/                      # fmt library submodule
└── scripts/
    └── generate_pyi.py           # Type stub generator
```

 
### Building for Development

 To build DeepGEMM from source for development:

 
```

```

 For builds without CUDA (e.g., documentation generation), the `publish.yml` workflow uses `DG_SKIP_CUDA_BUILD=1` to build the core package sdist ([.github/workflows/publish.yml87-89](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/.github/workflows/publish.yml#L87-L89)).

 **Sources**: [setup.py22-24](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/setup.py#L22-L24) [.github/workflows/publish.yml84-89](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/.github/workflows/publish.yml#L84-L89)

 
---

 
## Build Dependencies

 
### Required Dependencies

 Configured in [setup.py36-48](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/setup.py#L36-L48):

 
| Dependency | Source | Purpose |
|---|---|---|
| cudart | CUDA Toolkit | CUDA Runtime API |
| nvrtc | CUDA Toolkit | Runtime Compilation API |
| torch | PyTorch | Tensor interface and extension framework |
| CUTLASS | third-party/cutlass | Core GEMM templates |
| fmt | third-party/fmt | String formatting |

 **Sources**: [setup.py36-109](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/setup.py#L36-L109)

 
---

 
## Summary

 DeepGEMM's build system provides a seamless experience for both users and developers through:

 
 - **Matrix Distribution**: Comprehensive wheel support for various PyTorch/CUDA/ABI combinations via GitHub Actions.
 - **Handle Abstraction**: Flexible kernel execution via either Driver or Runtime APIs with lazy loading.
 - **Automated Setup**: Custom build commands that handle third-party header aggregation and type stub generation.
 
 For detailed information on specific aspects of the build and development process, refer to the child pages:

 
 - [Building from Source](https://deepwiki.com/deepseek-ai/DeepGEMM/5.1-building-from-source) - Detailed compilation instructions
 - [Distribution and CI/CD](https://deepwiki.com/deepseek-ai/DeepGEMM/5.2-distribution-and-cicd) - Automated wheel building and deployment
 - [Testing Framework](https://deepwiki.com/deepseek-ai/DeepGEMM/5.3-testing-framework) - Test organization and validation
 - [JIT System Internals](https://deepwiki.com/deepseek-ai/DeepGEMM/5.4-jit-system-internals) - Runtime compilation architecture
 - [Extending DeepGEMM](https://deepwiki.com/deepseek-ai/DeepGEMM/5.5-extending-deepgemm) - Adding new features and kernels
