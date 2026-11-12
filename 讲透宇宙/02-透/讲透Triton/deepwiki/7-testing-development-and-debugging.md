> 来源: [https://deepwiki.com/triton-lang/triton/7-testing-development-and-debugging](https://deepwiki.com/triton-lang/triton/7-testing-development-and-debugging)
> DeepWiki triton-lang/triton | Last indexed: 20 August 2026 (f89384

# Testing, Development, and Debugging

  Relevant source files 
 - [.github/workflows/build-macos.yml](https://github.com/triton-lang/triton/blob/f893845b/.github/workflows/build-macos.yml)
 - [.github/workflows/ci.yml](https://github.com/triton-lang/triton/blob/f893845b/.github/workflows/ci.yml)
 - [.github/workflows/create_release.yml](https://github.com/triton-lang/triton/blob/f893845b/.github/workflows/create_release.yml)
 - [.github/workflows/integration-tests-amd.yml](https://github.com/triton-lang/triton/blob/f893845b/.github/workflows/integration-tests-amd.yml)
 - [.github/workflows/integration-tests-nvidia.yml](https://github.com/triton-lang/triton/blob/f893845b/.github/workflows/integration-tests-nvidia.yml)
 - [.github/workflows/pre-commit.yml](https://github.com/triton-lang/triton/blob/f893845b/.github/workflows/pre-commit.yml)
 - [.github/workflows/runner-preparation.yml](https://github.com/triton-lang/triton/blob/f893845b/.github/workflows/runner-preparation.yml)
 - [MANIFEST.in](https://github.com/triton-lang/triton/blob/f893845b/MANIFEST.in)
 - [docs/requirements.txt](https://github.com/triton-lang/triton/blob/f893845b/docs/requirements.txt)
 - [pytest.ini](https://github.com/triton-lang/triton/blob/f893845b/pytest.ini)
 - [python/test-requirements.txt](https://github.com/triton-lang/triton/blob/f893845b/python/test-requirements.txt)
 - [python/test/conftest.py](https://github.com/triton-lang/triton/blob/f893845b/python/test/conftest.py)
 - [python/test/unit/instrumentation/test_gpuhello.py](https://github.com/triton-lang/triton/blob/f893845b/python/test/unit/instrumentation/test_gpuhello.py)
 - [python/test/unit/runtime/test_build.py](https://github.com/triton-lang/triton/blob/f893845b/python/test/unit/runtime/test_build.py)
 - [python/test/unit/runtime/test_compilation_listener.py](https://github.com/triton-lang/triton/blob/f893845b/python/test/unit/runtime/test_compilation_listener.py)
 - [python/test/unit/test_debug.py](https://github.com/triton-lang/triton/blob/f893845b/python/test/unit/test_debug.py)
 - [python/test/unit/test_knobs.py](https://github.com/triton-lang/triton/blob/f893845b/python/test/unit/test_knobs.py)
 - [python/triton/backends/__init__.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton/backends/__init__.py)
 - [python/triton/knobs.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton/knobs.py)
 - [python/triton_kernels/tests/conftest.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton_kernels/tests/conftest.py)
 - [python/triton_kernels/tests/test_specialize.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton_kernels/tests/test_specialize.py)
 - [python/triton_kernels/triton_kernels/specialize.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton_kernels/triton_kernels/specialize.py)
 
  This page provides an overview of Triton's testing infrastructure, development workflows, debugging capabilities, and configuration system. Triton includes comprehensive testing facilities spanning Python unit tests, MLIR-level IR verification, performance benchmarking, and specialized tools for memory sanitization and profiling.

 For detailed information on specific topics, see:

 
 - [Testing Framework and Test Structure](https://deepwiki.com/triton-lang/triton/7.1-testing-framework-and-test-structure) — Describe the testing organization including unit tests, MLIR lit tests, and integration tests.
 - [CI/CD Pipeline and Integration Tests](https://deepwiki.com/triton-lang/triton/7.2-cicd-pipeline-and-integration-tests) — Document GitHub Actions workflows for building LLVM, creating wheels, and running tests.
 - [Debugging and Profiling Tools](https://deepwiki.com/triton-lang/triton/7.3-debugging-and-profiling-tools) — Explain debugging tools including proton profiler, IR dumping, MIR inspection, kernel override mechanisms, the GSan global memory sanitizer, and the triton-to-gluon translator tool.
 - [Configuration System and Environment Variables](https://deepwiki.com/triton-lang/triton/7.4-configuration-system-and-environment-variables) — Document environment variables for controlling compilation, caching, debugging, and optimization behavior.
 
 
## Testing Infrastructure Overview

 Triton's testing infrastructure operates at multiple abstraction levels: Python unit tests in `python/test/unit/`, regression tests in `python/test/regression/`, and MLIR FileCheck tests in `test/`. The primary test utilities are provided by the `triton._internal_testing` module, while the execution is managed by `pytest` for Python and `lit` for MLIR.

 **Testing Infrastructure Architecture**

 
```

```

 **Sources:** [.github/workflows/integration-tests-amd.yml119-122](https://github.com/triton-lang/triton/blob/f893845b/.github/workflows/integration-tests-amd.yml#L119-L122) [.github/workflows/integration-tests-nvidia.yml92-115](https://github.com/triton-lang/triton/blob/f893845b/.github/workflows/integration-tests-nvidia.yml#L92-L115) [python/test/unit/test_debug.py1-5](https://github.com/triton-lang/triton/blob/f893845b/python/test/unit/test_debug.py#L1-L5)

 
## Development Workflow and Testing Patterns

 The standard Triton development cycle utilizes several testing modes to ensure correctness across backends and compilation stages.

 
### Correctness Testing and Assertions

 Triton supports various assertion mechanisms for debugging. `tl.static_assert` validates conditions during compilation, while `tl.device_assert` inserts runtime checks into the generated kernel code, which can be enabled via `TRITON_DEBUG=1`.

 **Sources:** [python/test/unit/test_debug.py14-16](https://github.com/triton-lang/triton/blob/f893845b/python/test/unit/test_debug.py#L14-L16) [python/test/unit/test_debug.py84-88](https://github.com/triton-lang/triton/blob/f893845b/python/test/unit/test_debug.py#L84-L88) [python/test/unit/test_debug.py57](https://github.com/triton-lang/triton/blob/f893845b/python/test/unit/test_debug.py#L57-L57)

 
### Parameterized Unit Testing

 Triton uses extensive parameterization in `pytest` to test across different data types, shapes, and hardware capabilities. The `triton._internal_testing` module provides helpers like `run_in_process` to isolate test executions.

 **Sources:** [python/test/unit/test_debug.py61-66](https://github.com/triton-lang/triton/blob/f893845b/python/test/unit/test_debug.py#L61-L66) [python/test/unit/test_debug.py146-156](https://github.com/triton-lang/triton/blob/f893845b/python/test/unit/test_debug.py#L146-L156)

 
## Debugging and Profiling Tools

 Triton provides several specialized tools for inspecting the compilation pipeline and runtime behavior.

 
### IR Dumping and Inspection

 Compilation stages can be inspected by dumping IR at various levels (TTIR, TTGIR, LLIR). The `ASTSource` and `IRSource` classes in the compiler manage the generation and hashing of these representations.

 **Compilation Debugging Flow**

 
```

```

 **Sources:** [python/triton/knobs.py21](https://github.com/triton-lang/triton/blob/f893845b/python/triton/knobs.py#L21-L21) [python/triton_kernels/triton_kernels/specialize.py117-129](https://github.com/triton-lang/triton/blob/f893845b/python/triton_kernels/triton_kernels/specialize.py#L117-L129)

 
### Specialized Sanitizers and Profilers

 
 - **GSan (Global Sanitizer):** Detects out-of-bounds global memory accesses.
 - **Proton:** A lightweight profiler for Triton kernels that captures performance metrics and hardware traces.
 - **Interpreter:** Provides a CPU-based execution environment for debugging logic errors without GPU hardware.
 - **Overflow Sanitization:** Triton can detect integer overflows (add, mul, sub) when debug mode is enabled.
 
 **Sources:** [.github/workflows/integration-tests-nvidia.yml107-117](https://github.com/triton-lang/triton/blob/f893845b/.github/workflows/integration-tests-nvidia.yml#L107-L117) [python/test/unit/test_debug.py98-128](https://github.com/triton-lang/triton/blob/f893845b/python/test/unit/test_debug.py#L98-L128)

 
## Configuration System and "Knobs"

 Triton's behavior is heavily influenced by environment variables and the "knobs" system defined in `triton.knobs`. These control caching, optimization levels, and debug output. The `env_base` and its subclasses (e.g., `env_bool`, `env_str`, `env_int`) provide a structured way to interface with environment variables.

 
| Category | Key Variables / Symbols | File Reference |
|---|---|---|
| Caching | TRITON_CACHE_DIR, TRITON_HOME | python/triton/knobs.py109-110 python/test/unit/test_knobs.py109-112 |
| Compilation | TRITON_ALWAYS_COMPILE, TRITON_DEBUG | .github/workflows/integration-tests-amd.yml164 python/test/unit/test_debug.py69 |
| Debugging | TRITON_DISABLE_LINE_INFO, TRITON_USE_ASSERT_ENABLED_LLVM | .github/workflows/integration-tests-amd.yml46-47 |
| Backend Tools | TRITON_PTXAS_PATH, TRITON_LLC_PATH | python/triton/knobs.py194-201 |

 **Sources:** [python/triton/knobs.py24-150](https://github.com/triton-lang/triton/blob/f893845b/python/triton/knobs.py#L24-L150) [python/test/unit/test_knobs.py10-42](https://github.com/triton-lang/triton/blob/f893845b/python/test/unit/test_knobs.py#L10-L42)

 
## Summary of Testing Utilities

 The `Makefile` and GitHub Actions workflows provide a centralized interface for running the various test suites:

 
 - **LIT Tests:** MLIR regression tests using `lit`.
 - **Unit Tests:** Python-based unit tests for core language and runtime.
 - **Integration Tests:** End-to-end tests running on specific hardware (NVIDIA A100/H100/GB200, AMD GFX90a/942/950).
 - **Warmup Runner:** `triton._test_runner` is used to warm up the Triton compile cache to speed up subsequent CI steps.
 
 **Sources:** [.github/workflows/integration-tests-amd.yml119-144](https://github.com/triton-lang/triton/blob/f893845b/.github/workflows/integration-tests-amd.yml#L119-L144) [.github/workflows/integration-tests-nvidia.yml92-121](https://github.com/triton-lang/triton/blob/f893845b/.github/workflows/integration-tests-nvidia.yml#L92-L121)
