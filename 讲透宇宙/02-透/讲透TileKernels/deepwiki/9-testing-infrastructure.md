> 来源: [https://deepwiki.com/deepseek-ai/TileKernels/9-testing-infrastructure](https://deepwiki.com/deepseek-ai/TileKernels/9-testing-infrastructure)
> DeepWiki deepseek-ai/TileKernels

# Testing Infrastructure

  Relevant source files 
 - [tests/__init__.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tests/__init__.py)
 - [tests/conftest.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tests/conftest.py)
 - [tests/pytest_benchmark_plugin.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tests/pytest_benchmark_plugin.py)
 - [tests/pytest_random_plugin.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tests/pytest_random_plugin.py)
 
  The **TileKernels** testing infrastructure is designed to ensure the correctness and performance of high-performance GPU kernels. It leverages `pytest` as the primary test runner, supplemented by custom plugins for benchmarking and deterministic randomization. The infrastructure handles everything from unit-level correctness checks against PyTorch reference implementations to regression detection for kernel execution times.

 
## Test Suite Structure

 The test suite is organized into subdirectories that mirror the kernel categories in the `tile_kernels/` package. Most tests follow a standardized pattern:

 
 - **Parameter Generation**: Using utility functions to create diverse input shapes and configurations.
 - **Data Initialization**: Generating random tensors (often with specific seeds for reproducibility).
 - **Kernel Execution**: Launching the TileLang-compiled kernel.
 - **Reference Comparison**: Running a PyTorch-native implementation of the same operation.
 - **Validation**: Using numeric utilities to assert equality within specified tolerances.
 
 For a detailed breakdown of specific test files and the environment variables used for pressure testing (like `TK_FULL_TEST`), see [Kernel Test Suites](https://deepwiki.com/deepseek-ai/TileKernels/9.2-kernel-test-suites).

 
## Pytest Plugins

 The repository includes two specialized `pytest` plugins located in the `tests/` directory to manage the complexities of GPU kernel testing.

 
### Benchmark Plugin

 The `pytest_benchmark_plugin.py` provides a robust framework for profiling kernel execution time and GPU memory usage.

 
 - **CLI Options**: Adds flags such as `--run-benchmark` to enable performance tests, and `--benchmark-regression-threshold` to set the sensitivity for slowdown alerts [tests/pytest_benchmark_plugin.py:33-56].
 - **Regression Detection**: Compares current runtimes against a `benchmark_baselines.jsonl` file. If a kernel slows down beyond the threshold, the test suite exits with a non-zero code [tests/pytest_benchmark_plugin.py:112-164].
 - **Xdist Integration**: When running tests in parallel with `pytest-xdist`, the plugin automatically binds each worker to a specific GPU and restricts per-process memory fractions to prevent Out-of-Memory (OOM) errors during concurrent execution [tests/pytest_benchmark_plugin.py:63-83].
 
 
### Randomization Plugin

 The `pytest_random_plugin.py` ensures that tests are deterministic yet diverse. It provides a `seed` fixture that is automatically applied to every test. The seed is derived from a combination of a global `--seed` (defaulting to 0) and a hash of the specific test node ID, ensuring that `torch.manual_seed` is set consistently for every test run [tests/pytest_random_plugin.py:7-18].

 
### Plugin Architecture

 
```

```

 Sources: [tests/conftest.py7-10](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tests/conftest.py#L7-L10) [tests/pytest_benchmark_plugin.py1-22](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tests/pytest_benchmark_plugin.py#L1-L22) [tests/pytest_random_plugin.py1-19](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tests/pytest_random_plugin.py#L1-L19)

 
## Testing Utilities

 The project maintains a dedicated library of testing helpers in `tile_kernels/testing/` to standardize data generation and validation across different kernel families.

 
| Module | Primary Purpose | Key Entities |
|---|---|---|
| numeric.py | Accuracy validation | assert_equal, calc_diff |
| generator.py | Input data creation | generate_num_tokens, generate_moe_params |
| bench.py | Profiling helpers | print_average_perf, make_param_key |
| quant.py | Quantization specific | clear_unused_sf |

 For details on the implementation of these helpers, see [Testing Utilities (tile_kernels/testing)](https://deepwiki.com/deepseek-ai/TileKernels/9.1-testing-utilities-(tile_kernelstesting)).

 
## Component Interaction

 The following diagram illustrates how the testing infrastructure bridges the gap between high-level test definitions and the underlying TileLang kernels.

 
```

```

 Sources: [tests/pytest_benchmark_plugin.py1-10](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tests/pytest_benchmark_plugin.py#L1-L10) [tile_kernels/testing/bench.py1-20](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/testing/bench.py#L1-L20) [tile_kernels/testing/numeric.py1-15](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/testing/numeric.py#L1-L15)

 
## Child Pages

 
 - **[Testing Utilities (tile_kernels/testing)](https://deepwiki.com/deepseek-ai/TileKernels/9.1-testing-utilities-(tile_kernelstesting))**: Deep dive into the `numeric`, `generator`, `bench`, and `quant` modules.
 - **[Kernel Test Suites](https://deepwiki.com/deepseek-ai/TileKernels/9.2-kernel-test-suites)**: Details on directory layout, the `TK_FULL_TEST` variable, and benchmark fixtures.
