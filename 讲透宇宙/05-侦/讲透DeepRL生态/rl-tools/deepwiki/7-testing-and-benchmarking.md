> 来源: [https://deepwiki.com/rl-tools/rl-tools/7-testing-and-benchmarking](https://deepwiki.com/rl-tools/rl-tools/7-testing-and-benchmarking)
> DeepWiki rl-tools/rl-tools | Last indexed: 2 February 2026 (a0aef4

# Testing and Benchmarking

  Relevant source files 
 - [src/rl/environments/mujoco/ant/td3/parameters.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/mujoco/ant/td3/parameters.h)
 - [tests/CMakeLists.txt](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/CMakeLists.txt)
 - [tests/src/nn/benchmark.cpp](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/benchmark.cpp)
 - [tests/src/nn/cuda/CMakeLists.txt](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/cuda/CMakeLists.txt)
 - [tests/src/nn/cuda/cuda_basics.cu](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/cuda/cuda_basics.cu)
 - [tests/src/nn/cuda/main.cu](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/cuda/main.cu)
 - [tests/src/rl/components/off_policy_runner.cpp](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/rl/components/off_policy_runner.cpp)
 - [tests/src/rl/cuda/CMakeLists.txt](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/rl/cuda/CMakeLists.txt)
 - [tests/src/rl/cuda/rl.cu](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/rl/cuda/rl.cu)
 - [tests/src/rl/cuda/td3_full_training.cu](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/rl/cuda/td3_full_training.cu)
 - [tests/src/rl/cuda/td3_full_training_parameters_pendulum.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/rl/cuda/td3_full_training_parameters_pendulum.h)
 
  This page documents the testing infrastructure and performance benchmarking systems in rl_tools. It covers the GoogleTest-based test suite, backend-specific tests (CPU/CUDA/MKL), performance benchmarking utilities, and code coverage reporting. For information about the CI/CD pipeline that executes these tests, see [CI/CD Pipeline](https://deepwiki.com/rl-tools/rl-tools/7.3-cicd-pipeline). For details on build configuration options that affect testing, see [CMake Options](https://deepwiki.com/rl-tools/rl-tools/6.1-cmake-options).

 
---

 
## Test Infrastructure Overview

 The rl_tools test suite is built on GoogleTest and organized hierarchically by component and backend. Tests verify correctness across device abstractions (CPU, CUDA, MKL), neural network operations, RL algorithms, and full training pipelines.

 
```

```

 **Test Infrastructure Architecture**: The test system integrates GoogleTest with CMake, organizing tests by component (unit/NN/RL/full) and backend (CPU/MKL/CUDA), with dedicated benchmarking for performance measurement.

 Sources: [tests/CMakeLists.txt1-48](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/CMakeLists.txt#L1-L48) [tests/src/nn/cuda/CMakeLists.txt1-36](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/cuda/CMakeLists.txt#L1-L36) [tests/src/rl/cuda/CMakeLists.txt1-49](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/rl/cuda/CMakeLists.txt#L1-L49)

 
---

 
## CMake Test Configuration

 The root test configuration defines options and integrates GoogleTest. Test targets are discovered automatically using `gtest_discover_tests()`.

 
### Configuration Options

 
| Option | Default | Purpose |
|---|---|---|
| RL_TOOLS_DOWNLOAD_GTEST | OFF | Download GoogleTest automatically |
| RL_TOOLS_TEST_LOCAL | OFF | Enable local development features |
| RL_TOOLS_TEST_RL_ENVIRONMENTS_PENDULUM_EVALUATE_VISUALLY | OFF | Visual evaluation of Pendulum environment |
| RL_TOOLS_TEST_RL_ALGORITHMS_TD3_SECOND_STAGE_OUTPUT_PLOTS | OFF | Generate plots for TD3 second stage |
| RL_TOOLS_TEST_RL_ALGORITHMS_TD3_FULL_TRAINING_OUTPUT_PLOTS | OFF | Generate plots for full TD3 training |
| RL_TOOLS_TESTS_RL_ENVIRONMENTS_MULTIROTOR_UI_ENABLE | OFF | Enable multirotor UI for testing |
| RL_TOOLS_TESTS_CODE_COVERAGE | OFF | Enable code coverage instrumentation |

 
### Code Coverage Instrumentation

 When `RL_TOOLS_TESTS_CODE_COVERAGE` is enabled, tests are compiled with coverage flags:

 
```

```

 The `--coverage` flag enables gcov instrumentation, `-g` adds debug symbols, and `-O0` disables optimizations to ensure accurate line coverage. Coverage data is collected as `.gcda` files during test execution and processed by Codecov in CI.

 Sources: [tests/CMakeLists.txt19-25](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/CMakeLists.txt#L19-L25) [tests/CMakeLists.txt31-34](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/CMakeLists.txt#L31-L34)

 
---

 
## Test Organization by Component

 
### Unit Tests: Container and Device Operations

 Unit tests verify basic operations on containers (Matrix, Tensor) and device abstractions. These tests ensure that data can be correctly copied between CPU and CUDA, views work properly, and memory alignment is handled correctly.

 
```

```

 **Container Copy Test Pattern**: Tests verify round-trip copying between devices with various matrix dimensions, alignments, and offsets to ensure data integrity across all configurations.

 The `COPY_CONTAINER` template function tests copying matrices between CPU and CUDA with different specifications. It uses fuzz testing with randomized parameters generated via Julia code (see comments in [tests/src/nn/cuda/cuda_basics.cu134-140](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/cuda/cuda_basics.cu#L134-L140)):

 
```

```

 Sources: [tests/src/nn/cuda/cuda_basics.cu25-191](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/cuda/cuda_basics.cu#L25-L191)

 
### Neural Network Tests: Forward and Backward Passes

 Neural network tests verify the correctness of forward passes, backward passes (gradient computation), and weight updates across different backends. Tests compare CPU and CUDA implementations to ensure numerical equivalence.

 
```

```

 **Neural Network Test Hierarchy**: Tests progressively verify GEMM operations, forward passes, backward passes, and optimizer updates, ensuring correctness at each level before proceeding to the next.

 The `FORWARD` test template verifies that neural network forward passes produce identical results on CPU and CUDA:

 
```

```

 Sources: [tests/src/nn/cuda/cuda_basics.cu353-462](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/cuda/cuda_basics.cu#L353-L462) [tests/src/nn/cuda/cuda_basics.cu465-627](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/cuda/cuda_basics.cu#L465-L627) [tests/src/nn/cuda/cuda_basics.cu629-815](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/cuda/cuda_basics.cu#L629-L815)

 
### RL Algorithm Tests: Step-by-Step Verification

 RL algorithm tests verify each step of the training process individually, ensuring that critic training, actor training, target updates, and batch gathering work correctly on CUDA.

 
```

```

 **RL Algorithm Step-by-Step Testing**: Each component of TD3 training is tested individually to isolate issues, starting from batch gathering through critic training, actor training, and target network updates.

 The `TRAIN_CRITIC_STEP_BY_STEP` test verifies each operation in the critic training loop:

 
```

```

 Sources: [tests/src/rl/cuda/rl.cu230-376](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/rl/cuda/rl.cu#L230-L376) [tests/src/rl/cuda/rl.cu378-443](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/rl/cuda/rl.cu#L378-L443)

 
### Full Training Tests

 Full training tests execute complete training loops to verify the end-to-end pipeline, including environment interaction, experience collection, and multiple training steps.

 
```

```

 **Full Training Loop Structure**: The complete training pipeline includes environment interaction (prologue/interlude/epilogue), training steps with appropriate intervals, and periodic evaluation.

 The full training test runs 20,000 steps of TD3 training on CUDA:

 
```

```

 Sources: [tests/src/rl/cuda/td3_full_training.cu48-213](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/rl/cuda/td3_full_training.cu#L48-L213) [tests/src/rl/cuda/td3_full_training_parameters_pendulum.h1-57](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/rl/cuda/td3_full_training_parameters_pendulum.h#L1-L57)

 
---

 
## Performance Benchmarking

 Performance benchmarks measure execution time for critical operations across different backends. Benchmarks use `std::chrono::high_resolution_clock` to measure timing with microsecond precision.

 
### GEMM Benchmarks

 GEMM (General Matrix Multiply) benchmarks compare matrix multiplication performance across CPU (generic), Intel MKL, and CUDA cuBLAS implementations.

 
```

```

 **GEMM Benchmark Flow**: Benchmarks compare generic CPU, Intel MKL, and CUDA cuBLAS implementations, measuring time per iteration after synchronization to ensure accurate GPU timing.

 The MKL benchmark directly calls `cblas_sgemm`/`cblas_dgemm`:

 
```

```

 Sources: [tests/src/nn/benchmark.cpp181-231](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/benchmark.cpp#L181-L231)

 
### Layer and Network Benchmarks

 Benchmarks measure complete layer evaluations and full network forward/backward passes:

 
| Benchmark | Description | Code Location |
|---|---|---|
| MKL_LAYER | Layer evaluation with MKL backend | tests/src/nn/benchmark.cpp237-263 |
| MKL_LAYER_FORWARD | Layer forward pass with state | tests/src/nn/benchmark.cpp265-292 |
| MKL_MODEL_FORWARD | Full model forward pass | tests/src/nn/benchmark.cpp294-317 |
| MKL_MODEL_BACKWARD | Full model forward + backward | tests/src/nn/benchmark.cpp319-360 |

 The backward pass benchmark measures gradient computation time:

 
```

```

 Sources: [tests/src/nn/benchmark.cpp237-360](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/benchmark.cpp#L237-L360)

 
### CUDA Benchmarks

 CUDA benchmarks measure GPU kernel execution time with proper synchronization:

 
```

```

 The `cudaDeviceSynchronize()` call is critical for accurate timing, as CUDA operations are asynchronous by default. Without synchronization, timing would only measure kernel launch overhead, not actual execution time.

 Sources: [tests/src/nn/cuda/cuda_basics.cu437-446](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/cuda/cuda_basics.cu#L437-L446) [tests/src/nn/cuda/cuda_basics.cu602-611](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/cuda/cuda_basics.cu#L602-L611)

 
---

 
## Code Coverage

 Code coverage is enabled via the `RL_TOOLS_TESTS_CODE_COVERAGE` CMake option, which adds instrumentation to measure which lines of code are executed during testing.

 
### Coverage Workflow

 
```

```

 **Coverage Collection and Reporting**: Tests compile with instrumentation, generate `.gcda` files during execution, and are processed by lcov/gcov for upload to Codecov.

 The coverage instrumentation is configured in CMake:

 
```

```

 The `-g` flag adds debug symbols for line number mapping, `-O0` disables optimizations to prevent line merging, and `--coverage` enables gcov instrumentation. During test execution, each executed line increments a counter in `.gcda` files. These files are processed by gcov and lcov to generate line coverage percentages, which are uploaded to Codecov for visualization.

 Sources: [tests/CMakeLists.txt19-25](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/CMakeLists.txt#L19-L25)

 
---

 
## Debug Definitions

 Test executables can be compiled with debug definitions to enable additional runtime checks. These are typically enabled in Debug build configurations.

 
```

```

 **Debug Definition Categories**: Debug flags enable bounds checking, initialization tracking, and device-specific checks to catch errors early during development.

 Debug definitions are conditionally added in CMake:

 
```

```

 These definitions enable runtime assertions that check for:

 
 - **Bounds checking**: Verify array indices are within valid ranges
 - **Initialization checking**: Ensure data structures are properly initialized before use
 - **Memory initialization**: Fill allocations with NaN to detect use of uninitialized values
 - **CUDA error checking**: Check for CUDA errors after synchronization operations
 
 Sources: [tests/src/nn/cuda/CMakeLists.txt8-16](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/cuda/CMakeLists.txt#L8-L16) [tests/src/rl/cuda/CMakeLists.txt8-19](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/rl/cuda/CMakeLists.txt#L8-L19)

 
---

 
## Running Tests

 
### Building Tests

 Tests are built when the `RL_TOOLS_ENABLE_TESTS` option is enabled:

 
```

```

 Individual test targets can be built:

 
```

```

 
### Executing Tests

 Tests can be run using CTest or directly:

 
```

```

 
### Test Filtering

 GoogleTest provides filtering capabilities:

 
```

```

 Sources: [tests/src/nn/cuda/CMakeLists.txt18-36](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/cuda/CMakeLists.txt#L18-L36) [tests/src/rl/cuda/CMakeLists.txt21-49](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/rl/cuda/CMakeLists.txt#L21-L49)

 
---

 
## Test Naming Conventions

 Test executables and test cases follow consistent naming conventions:

 
| Pattern | Example | Purpose |
|---|---|---|
| test_<component>_<backend> | test_nn_cuda_basics | Backend-specific component tests |
| test_<algorithm>_<component> | test_rl_cuda_td3_full_training | Algorithm-specific tests |
| <COMPONENT>_<OPERATION> | RL_TOOLS_NN_CUDA.FORWARD | Test case naming |
| <ALGORITHM>_<PHASE> | TRAIN_CRITIC_STEP_BY_STEP | RL algorithm phase tests |

 
### Test Fixture Classes

 Test fixtures provide reusable setup and teardown logic:

 
```

```

 Test fixtures reduce code duplication and ensure proper resource cleanup after test failure.

 Sources: [tests/src/rl/cuda/rl.cu41-183](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/rl/cuda/rl.cu#L41-L183)

 
---

 
## Integration with CI/CD

 The testing infrastructure integrates with GitHub Actions CI/CD. For details on the CI workflows, test matrices, and automated test execution, see [CI/CD Pipeline](https://deepwiki.com/rl-tools/rl-tools/7.3-cicd-pipeline). The coverage data generated by tests with `RL_TOOLS_TESTS_CODE_COVERAGE` enabled is automatically uploaded to Codecov for tracking coverage trends over time.

 Sources: [tests/CMakeLists.txt19-25](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/CMakeLists.txt#L19-L25)
