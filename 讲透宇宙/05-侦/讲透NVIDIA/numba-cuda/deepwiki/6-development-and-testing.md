<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/numba-cuda · page 6 Development and Testing · fetched 2026-10-26 -->

# Development and Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [ci/test_conda.sh](ci/test_conda.sh)
- [ci/test_wheel.sh](ci/test_wheel.sh)
- [ci/test_wheel_deps_wheels.sh](ci/test_wheel_deps_wheels.sh)
- [conda/recipes/numba-cuda/meta.yaml](conda/recipes/numba-cuda/meta.yaml)
- [numba_cuda/numba/cuda/testing.py](numba_cuda/numba/cuda/testing.py)
- [numba_cuda/numba/cuda/tests/benchmarks/test_kernel_launch.py](numba_cuda/numba/cuda/tests/benchmarks/test_kernel_launch.py)
- [numba_cuda/numba/cuda/tests/cudadrv/test_managed_alloc.py](numba_cuda/numba/cuda/tests/cudadrv/test_managed_alloc.py)
- [numba_cuda/numba/cuda/tests/cudapy/test_inspect.py](numba_cuda/numba/cuda/tests/cudapy/test_inspect.py)
- [numba_cuda/numba/cuda/tests/cudapy/test_ipc.py](numba_cuda/numba/cuda/tests/cudapy/test_ipc.py)
- [pixi.lock](pixi.lock)
- [pixi.toml](pixi.toml)
- [pyproject.toml](pyproject.toml)
- [scripts/bench-against.py](scripts/bench-against.py)
- [testing/Makefile](testing/Makefile)
- [testing/pytest.ini](testing/pytest.ini)

</details>



This document covers the development workflow, testing infrastructure, and continuous integration pipeline for the numba-cuda project. It explains how tests are organized, executed, and integrated into the development process to ensure code quality and compatibility across different CUDA environments.

For information about the core compilation and runtime systems being tested, see [Core Architecture](#2). For details about debugging and inspection tools used during development, see [Debugging and Inspection](#4).

## Testing Framework Architecture

The numba-cuda testing framework is built around specialized test base classes and utilities that handle CUDA-specific testing requirements including context management, device availability, and environment configuration.

### Core Testing Classes

```mermaid
graph TB
    subgraph "Base Classes"
        A[TestCase] --> B[CUDATestCase]
        B --> C[ContextResettingTestCase]
        D[SerialMixin] --> B
    end
    
    subgraph "Test Utilities"
        E[skip_on_cudasim] --> F["Test Functions"]
        G[skip_unless_cudasim] --> F
        H[skip_unless_cc_50] --> F
        I[skip_if_external_memmgr] --> F
        J[skip_under_cuda_memcheck] --> F
    end
    
    subgraph "Environment Setup"
        K[setUp] --> L["config.CUDA_LOW_OCCUPANCY_WARNINGS"]
        K --> M["config.CUDA_WARN_ON_IMPLICIT_COPY"]
        N[tearDown] --> O["Context Reset"]
        N --> P["Config Restore"]
    end
    
    B --> K
    C --> N
    F --> Q["Test Execution"]
```

**Test Base Classes Architecture**

The `CUDATestCase` class provides the foundation for all CUDA-related tests, handling configuration management and ensuring proper test isolation.

Sources: [numba_cuda/numba/cuda/testing.py:17-37]()

### Skip Decorators System

```mermaid
graph LR
    subgraph "Conditional Execution"
        A[skip_on_cudasim] --> B["config.ENABLE_CUDASIM"]
        C[skip_unless_cudasim] --> B
        D[skip_unless_cc_50] --> E["devices.get_context().device.compute_capability"]
        F[skip_if_external_memmgr] --> G["config.CUDA_MEMORY_MANAGER"]
        H[skip_under_cuda_memcheck] --> I["os.environ.get('CUDA_MEMCHECK')"]
        J[skip_without_nvdisasm] --> K["shutil.which('nvdisasm')"]
        L[skip_if_cuda_includes_missing] --> M["libs.get_cuda_include_dir()"]
    end
    
    subgraph "Hardware Requirements"
        N[skip_unless_cc_53] --> E
        O[skip_unless_cc_60] --> E
        P[skip_unless_cc_75] --> E
        Q[cc_X_or_above] --> E
    end
```

**Skip Decorators for Conditional Test Execution**

The framework provides extensive skip decorators to handle different execution environments, hardware capabilities, and system configurations.

Sources: [numba_cuda/numba/cuda/testing.py:54-190]()

## CI/CD Pipeline Architecture

The continuous integration pipeline consists of multiple testing strategies covering different package distributions, CUDA versions, and execution environments.

### Test Matrix Execution

```mermaid
graph TB
    subgraph "CI Trigger"
        A["Git Push/PR"] --> B["GitHub Actions"]
    end
    
    subgraph "Build Matrix"
        B --> C["test_conda.sh"]
        B --> D["test_wheel.sh"] 
        B --> E["test_simulator.sh"]
        B --> F["test_wheel_deps_wheels.sh"]
        B --> G["build_docs.sh"]
    end
    
    subgraph "Environment Setup"
        C --> H["rapids-mamba-retry create -n test"]
        D --> I["pip install wheel[test]"]
        E --> J["NUMBA_ENABLE_CUDASIM=1"]
        F --> K["pip install wheel[cu12,test-cu12]"]
        G --> L["sphinx + numpydoc"]
    end
    
    subgraph "Test Execution"
        H --> M["python -m numba.runtests numba.cuda.tests"]
        I --> M
        J --> M
        K --> N["NUMBA_CUDA_ENABLE_PYNVJITLINK=1"]
        L --> O["make html"]
    end
```

**CI/CD Pipeline Test Matrix**

The pipeline executes tests across multiple configurations to ensure compatibility with different installation methods and CUDA versions.

Sources: [ci/test_conda.sh:1-84](), [ci/test_wheel.sh:1-50](), [ci/test_simulator.sh:1-44](), [ci/test_wheel_deps_wheels.sh:1-51](), [ci/build_docs.sh:1-44]()

### CUDA Version Handling

```mermaid
graph LR
    subgraph "CUDA 11 Environment"
        A["CUDA_VER=11.x"] --> B["CTK_PACKAGES=cudatoolkit=11"]
        B --> C["Skip Binary Generation Tests"]
    end
    
    subgraph "CUDA 12 Environment"
        D["CUDA_VER=12.x"] --> E["CTK_PACKAGES=cuda-cccl cuda-nvcc-impl cuda-nvrtc"]
        E --> F["apt remove cuda-nvvm cuda-nvrtc"]
        F --> G["Build Binary Tests"]
        G --> H["export NUMBA_CUDA_TEST_BIN_DIR"]
        H --> I["make in test_binary_generation"]
    end
    
    subgraph "Version Detection"
        J["CUDA_VER_MAJOR_MINOR=${CUDA_VER%.*}"] --> K["Version-Specific Logic"]
        K --> A
        K --> D
    end
```

**CUDA Version-Specific Test Configuration**

The testing infrastructure adapts to different CUDA versions, with CUDA 12 requiring additional binary generation tests and package management.

Sources: [ci/test_conda.sh:8-75](), [ci/test_wheel.sh:6-33](), [ci/test_wheel_deps_wheels.sh:6-48]()

## Test Categories and Execution

### Core Test Types

The test suite covers multiple aspects of CUDA functionality through specialized test modules.

```mermaid
graph TB
    subgraph "Test Categories"
        A["numba.cuda.tests"] --> B["test_fastmath.py"]
        A --> C["test_exception.py"]
        A --> D["test_userexc.py"]
        A --> E["test_binary_generation"]
        A --> F["Additional Test Modules"]
    end
    
    subgraph "FastMath Testing"
        B --> G["FastMathCriterion"]
        G --> H["PTX Instruction Validation"]
        H --> I["compile_ptx_for_current_device"]
        I --> J["inspect_asm"]
    end
    
    subgraph "Exception Testing"
        C --> K["TestException"]
        K --> L["ZeroDivisionError Handling"]
        K --> M["Debug Mode Validation"]
        D --> N["TestUserExc"]
        N --> O["Custom Exception Propagation"]
    end
    
    subgraph "Binary Generation"
        E --> P["Makefile-based Compilation"]
        P --> Q["NUMBA_CUDA_TEST_BIN_DIR"]
        Q --> R["External Code Linking"]
    end
```

**Test Module Organization**

Tests are organized by functionality, with each module focusing on specific aspects of CUDA compilation and execution.

Sources: [numba_cuda/numba/cuda/tests/cudapy/test_fastmath.py:1-239](), [numba_cuda/numba/cuda/tests/cudapy/test_exception.py:1-168](), [numba_cuda/numba/cuda/tests/cudapy/test_userexc.py:1-40]()

### FastMath Test Framework

```mermaid
graph LR
    subgraph "FastMath Validation"
        A["FastMathCriterion"] --> B["fast_expected"]
        A --> C["fast_unexpected"]
        A --> D["prec_expected"]
        A --> E["prec_unexpected"]
    end
    
    subgraph "Test Execution"
        F["_test_fast_math_common"] --> G["cuda.jit(fastmath=True)"]
        F --> H["cuda.jit(fastmath=False)"]
        G --> I["inspect_asm"]
        H --> I
        F --> J["compile_ptx_for_current_device"]
    end
    
    subgraph "PTX Analysis"
        I --> K["PTX Instruction Matching"]
        J --> K
        K --> L["cos.approx.ftz.f32"]
        K --> M["div.approx.ftz.f32"]
        K --> N["lg2.approx.ftz.f32"]
    end
```

**FastMath Testing Architecture**

The `FastMathCriterion` class validates that fast math optimizations produce the expected PTX instructions.

Sources: [numba_cuda/numba/cuda/tests/cudapy/test_fastmath.py:12-44]()

## Development Workflow

### Test Environment Setup

```mermaid
graph TB
    subgraph "Environment Preparation"
        A["rapids-mamba-retry create -n test"] --> B["Install Dependencies"]
        B --> C["c-compiler cxx-compiler"]
        B --> D["cuda-python pytest cffi"]
        B --> E["psutil make"]
    end
    
    subgraph "System Information"
        F["nvidia-smi"] --> G["GPU Status Check"]
        H["python -m numba --sysinfo"] --> I["Numba Configuration"]
        G --> J["Test Execution"]
        I --> J
    end
    
    subgraph "Binary Test Preparation"
        K["GET_TEST_BINARY_DIR"] --> L["numba_cuda.__file__"]
        L --> M["test_binary_generation/"]
        M --> N["make"]
        N --> O["NUMBA_CUDA_TEST_BIN_DIR"]
    end
```

**Development Environment Setup Process**

The development workflow includes environment preparation, system validation, and binary test compilation.

Sources: [ci/test_conda.sh:19-84](), [ci/test_wheel.sh:8-50]()

### Exception Testing Framework

```mermaid
graph LR
    subgraph "Exception Handling Tests"
        A["TestException"] --> B["test_exception"]
        A --> C["test_user_raise"]
        A --> D["test_zero_division_error_in_debug"]
        A --> E["test_no_zero_division_error"]
    end
    
    subgraph "Debug Mode Differences"
        F["debug=True, opt=False"] --> G["Exception Propagation"]
        H["debug=False"] --> I["Silent Failure"]
        G --> J["ZeroDivisionError"]
        I --> K["np.inf Result"]
    end
    
    subgraph "Custom Exceptions"
        L["TestUserExc"] --> M["MyError"]
        M --> N["Custom Exception Messages"]
        N --> O["tid=[0, 0, 0] ctaid=[0, 0, 0]"]
    end
```

**Exception Testing Architecture**

The exception testing framework validates proper error handling in both debug and optimized modes.

Sources: [numba_cuda/numba/cuda/tests/cudapy/test_exception.py:8-164](), [numba_cuda/numba/cuda/tests/cudapy/test_userexc.py:15-36]()

## Test Execution Patterns

### Simulator vs Hardware Testing

The testing framework supports both CUDA simulator and hardware execution with appropriate test selection.

| Test Type | Simulator | Hardware | Configuration |
|-----------|-----------|-----------|---------------|
| Basic Functionality | ✓ | ✓ | `NUMBA_ENABLE_CUDASIM=1` |
| PTX Generation | ✗ | ✓ | Hardware required |
| Exception Handling | ✓ | ✓ | Different exception types |
| Binary Generation | ✗ | ✓ | External compilation |
| FastMath Validation | ✗ | ✓ | PTX inspection required |

### Configuration Management

```mermaid
graph TB
    subgraph "Test Configuration"
        A["CUDATestCase.setUp"] --> B["config.CUDA_LOW_OCCUPANCY_WARNINGS = 0"]
        A --> C["config.CUDA_WARN_ON_IMPLICIT_COPY = 0"]
        D["CUDATestCase.tearDown"] --> E["Restore Original Settings"]
    end
    
    subgraph "Context Management"
        F["ContextResettingTestCase"] --> G["devices.reset()"]
        G --> H["Clean Context State"]
    end
    
    subgraph "Environment Variables"
        I["NUMBA_ENABLE_CUDASIM"] --> J["Simulator Mode"]
        K["NUMBA_CUDA_ENABLE_PYNVJITLINK"] --> L["Minor Version Compatibility"]
        M["CUDA_MEMCHECK"] --> N["Memory Debugging"]
    end
```

**Test Configuration Management**

The testing framework manages CUDA-specific configuration settings and context state to ensure test isolation.

Sources: [numba_cuda/numba/cuda/testing.py:25-52]()

This development and testing infrastructure ensures comprehensive validation of numba-cuda functionality across different environments, CUDA versions, and execution modes, providing confidence in the reliability and compatibility of the CUDA compilation pipeline.

---

