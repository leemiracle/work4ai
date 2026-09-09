> 来源: [https://deepwiki.com/deepseek-ai/LPLB/6-build-system](https://deepwiki.com/deepseek-ai/LPLB/6-build-system)
> DeepWiki deepseek-ai/LPLB

# Build System

  Relevant source files 
 - [csrc/plugin.cpp](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp)
 - [pyproject.toml](https://github.com/deepseek-ai/LPLB/blob/0490f794/pyproject.toml)
 - [setup.py](https://github.com/deepseek-ai/LPLB/blob/0490f794/setup.py)
 
  This page provides an overview of LPLB's build system, which uses a sophisticated two-stage compilation strategy to combine build-time C++ extension compilation with runtime CUDA kernel specialization. This approach enables LPLB to adapt to different problem sizes and hardware configurations without requiring recompilation of the entire package.

 For detailed information about:

 
 - Build configuration files and extension builder setup, see [Build Configuration](https://deepwiki.com/deepseek-ai/LPLB/6.1-build-configuration)
 - Dependency acquisition and resource file management, see [Dependency Management](https://deepwiki.com/deepseek-ai/LPLB/6.2-dependency-management)
 - NVRTC-based runtime compilation and kernel caching, see [Runtime Compilation and Caching](https://deepwiki.com/deepseek-ai/LPLB/6.3-runtime-compilation-and-caching)
 - Development tools and code quality standards, see [Code Quality Standards](https://deepwiki.com/deepseek-ai/LPLB/7.2-code-quality-standards)
 
 
## Two-Stage Compilation Architecture

 LPLB employs a two-stage compilation model that separates generic infrastructure from problem-specific optimizations:

 
```

```

 **Sources:** [setup.py1-51](https://github.com/deepseek-ai/LPLB/blob/0490f794/setup.py#L1-L51) [csrc/plugin.cpp149-327](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L149-L327) [pyproject.toml1-39](https://github.com/deepseek-ai/LPLB/blob/0490f794/pyproject.toml#L1-L39)

 
### Stage 1: Build-Time C++ Extension Compilation

 During package installation, `setup.py` compiles the C++ plugin into a Python extension module (`lplb._cpp.so`). This module provides the `CompiledSolver` class, which manages CUDA kernel compilation and execution.

 Key characteristics:

 
 - **One-time compilation** during `pip install`
 - **Generic infrastructure** that works for any problem size
 - **Links with system libraries**: NVRTC, NVJitLink, CUDA runtime
 - **Optional NVSHMEM integration** detected at build time
 
 The build process uses PyTorch's `CUDAExtension` builder, which handles CUDA include paths, library linking, and compilation flags automatically. The extension links against three critical NVIDIA libraries: `nvrtc` for runtime compilation, `nvJitLink` for linking, and `cuda` for driver API access.

 **Sources:** [setup.py14-50](https://github.com/deepseek-ai/LPLB/blob/0490f794/setup.py#L14-L50) [csrc/plugin.cpp18-21](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L18-L21)

 
### Stage 2: Runtime CUDA Kernel Specialization

 When `CompiledSolver` is first instantiated with specific parameters (e.g., `group_size=8`, `dup_per_rank=2`), it compiles specialized CUDA kernels using NVRTC. This compilation happens at runtime and produces a `cubin` file that is cached for reuse.

 Key characteristics:

 
 - **Deferred compilation** until first use with specific parameters
 - **Problem-specific optimization** based on `group_size`, `dup_per_rank`, `block_dim`
 - **Cache reuse** for identical parameter combinations
 - **Automatic specialization** without user intervention
 
 The runtime compilation process reads the CUDA template from `resources/csrc-tmpl/minilp.cu`, applies compile-time constants (e.g., `GROUP_SIZE`, `DUP_PER_RANK`), compiles to LTO IR, links with cuSolverDx's pre-compiled library, and produces a cubin file. Hash-based caching ensures that identical configurations reuse cached binaries.

 **Sources:** [csrc/plugin.cpp149-327](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L149-L327)

 
## Build Components

 
### Extension Module Structure

 The `lplb._cpp` extension module exposes the `CompiledSolver` class to Python via pybind11:

 
| Method | Purpose | Stage |
|---|---|---|
| __init__ | Initialize solver, trigger kernel compilation | Build-time + Runtime |
| init_comm | Initialize distributed communication buffers | Runtime |
| solve | Launch LP solver kernel | Runtime |
| count_idx | Launch workload counting kernel | Runtime |
| map_idx | Launch index mapping kernel | Runtime |

 The constructor signature specifies problem dimensions that determine kernel specialization:

 
```

```

 **Sources:** [csrc/plugin.cpp663-679](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L663-L679) [csrc/plugin.cpp459-470](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L459-L470)

 
### Resource Files

 The package installation includes several resource files that are essential for runtime compilation:

 
```

```

 These resources are specified in `pyproject.toml` under `[tool.setuptools.package-data]` and are included in the wheel during build. The `resource_path` parameter passed to `CompiledSolver` must point to this directory.

 **Sources:** [pyproject.toml32-38](https://github.com/deepseek-ai/LPLB/blob/0490f794/pyproject.toml#L32-L38)

 
## Conditional Feature Compilation

 LPLB supports optional NVSHMEM integration for optimized distributed communication. The build system detects NVSHMEM availability at build time and conditionally compiles features:

 
```

```

 The detection logic in `setup.py`:

 
```

```

 When `deep_ep_cpp` is available, the build system:

 
 - Defines `-DUSE_NVSHMEM` preprocessor macro
 - Adds `-DNVSHMEM_DIR` and `-DDEEP_EP_SO` path definitions
 - Includes NVSHMEM headers from `$NVSHMEM_DIR/include`
 - Links against the DeepEP shared object with proper rpath settings
 
 This enables `#ifdef USE_NVSHMEM` blocks in `plugin.cpp` to compile NVSHMEM-specific code paths, including the `init_comm` method and RDMA buffer management.

 **Sources:** [setup.py9-46](https://github.com/deepseek-ai/LPLB/blob/0490f794/setup.py#L9-L46) [csrc/plugin.cpp38-40](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L38-L40) [csrc/plugin.cpp90-106](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L90-L106)

 
## Compilation Flow

 The complete build and execution flow follows this sequence:

 
```

```

 **Sources:** [setup.py1-51](https://github.com/deepseek-ai/LPLB/blob/0490f794/setup.py#L1-L51) [csrc/plugin.cpp149-327](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L149-L327) [csrc/plugin.cpp329-352](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L329-L352)

 
## Build Outputs

 After successful installation, the package structure is:

 
```
site-packages/lplb/
├── __init__.py                    # Python API
├── planner.py                     # Planner class
├── eplb.py                        # EPLB functions
├── _cpp.so                        # Compiled extension (build-time)
└── resources/
    ├── csrc-tmpl/
    │   └── minilp.cu              # CUDA kernel template
    └── mathdx/
        ├── lib/
        │   └── libcusolverdx.fatbin  # Pre-compiled library
        ├── include/                  # cuSolverDx headers
        └── external/                 # CUTLASS dependencies

~/.lplb/cache/                     # Runtime compilation cache
├── minilp_solve_8x2.cu_<hash>/
│   ├── cubin                      # Compiled kernel binary
│   ├── cu                         # Source snapshot
│   └── options                    # Compilation options
└── minilp_solve_16x4.cu_<hash>/
    └── ...
```

 The cache directory stores compiled kernels organized by parameter hash. Each cached kernel includes the source snapshot and compilation options to detect hash collisions.

 **Sources:** [pyproject.toml32-38](https://github.com/deepseek-ai/LPLB/blob/0490f794/pyproject.toml#L32-L38) [csrc/plugin.cpp207-244](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L207-L244)

 
## Build Requirements

 The build system requires:

 
| Component | Purpose | Detected By |
|---|---|---|
| CUDA Toolkit | C++ compilation, NVRTC, NVJitLink | PyTorch CUDA extension |
| PyTorch | Extension builder, tensor operations | setup.py imports |
| setuptools | Build backend | pyproject.toml |
| cuSolverDx | Math library (runtime linking) | Included in resources |
| NVSHMEM | Optional distributed communication | importlib.util.find_spec |
| DeepEP | Optional optimized buffer sync | importlib.util.find_spec |

 The CUDA Toolkit version must support the target GPU architecture. The plugin automatically detects the compute capability at runtime using `cudaGetDeviceProperties` and compiles for the appropriate `sm_XX` architecture.

 **Sources:** [setup.py1-51](https://github.com/deepseek-ai/LPLB/blob/0490f794/setup.py#L1-L51) [csrc/plugin.cpp150-154](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L150-L154) [pyproject.toml1-3](https://github.com/deepseek-ai/LPLB/blob/0490f794/pyproject.toml#L1-L3)

 
## Cache Management

 Compiled kernels are cached with a hash-based naming scheme to enable reuse across runs and processes:

 
```

```

 The hash collision detection ensures correctness by comparing the cached source and options against the current compilation request. If a collision is detected (hash matches but content differs), the build fails with an assertion error.

 The atomic move from temporary to cache directory handles concurrent compilation from multiple processes. If the cache directory already exists when attempting to rename, it means another process completed compilation first, so the temporary directory is simply removed.

 **Sources:** [csrc/plugin.cpp108-118](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L108-L118) [csrc/plugin.cpp207-327](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L207-L327)
