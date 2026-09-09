> 来源: [https://deepwiki.com/rl-tools/rl-tools/6-build-system-and-configuration](https://deepwiki.com/rl-tools/rl-tools/6-build-system-and-configuration)
> DeepWiki rl-tools/rl-tools | Last indexed: 2 February 2026 (a0aef4

# Build System and Configuration

  Relevant source files 
 - [.gitignore](https://github.com/rl-tools/rl-tools/blob/a0aef476/.gitignore)
 - [CMakeLists.txt](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt)
 - [src/rl/environments/mujoco/ant/CMakeLists.txt](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/mujoco/ant/CMakeLists.txt)
 - [src/rl/environments/mujoco/ant/evaluate_actor.cpp](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/mujoco/ant/evaluate_actor.cpp)
 - [src/rl/environments/mujoco/ant/ppo/cpu/CMakeLists.txt](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/mujoco/ant/ppo/cpu/CMakeLists.txt)
 - [src/rl/environments/mujoco/ant/ppo/cpu/training.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/mujoco/ant/ppo/cpu/training.h)
 - [src/rl/environments/mujoco/ant/ppo/cuda/CMakeLists.txt](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/mujoco/ant/ppo/cuda/CMakeLists.txt)
 - [src/rl/environments/mujoco/ant/ppo/cuda/training_ppo.cu](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/mujoco/ant/ppo/cuda/training_ppo.cu)
 - [src/rl/environments/mujoco/ant/ppo/parameters.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/mujoco/ant/ppo/parameters.h)
 - [src/rl/environments/mujoco/ant/td3/CMakeLists.txt](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/mujoco/ant/td3/CMakeLists.txt)
 - [src/rl/environments/mujoco/ant/td3/training.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/mujoco/ant/td3/training.h)
 - [src/rl/environments/pendulum/sac/cuda/cuda_graph_export.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/sac/cuda/cuda_graph_export.h)
 - [src/rl/environments/pendulum/td3/cpu/CMakeLists.txt](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/td3/cpu/CMakeLists.txt)
 - [tests/CMakeLists.txt](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/CMakeLists.txt)
 - [tests/src/rl/algorithms/ppo/parameters_rl.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/rl/algorithms/ppo/parameters_rl.h)
 
  This page documents the CMake-based build system used in RLtools and the various configuration options available. The build system is designed to be flexible, allowing users to enable or disable specific features, choose appropriate backends (CPU, CUDA, etc.), and control optimization settings for different deployment scenarios.

 For information about running tests, see [Testing and Benchmarking](https://deepwiki.com/rl-tools/rl-tools/7-testing-and-benchmarking).

 
## Build System Overview

 The RLtools build system is built on CMake (minimum version 3.19 required for HDF5::HDF5 target support) and provides a header-only library interface through the `rl_tools_core` INTERFACE target. The library can be integrated either as a full-featured build or as a minimal header-only dependency.

 Sources: [CMakeLists.txt3](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L3-L3)

 
### Core CMake Targets

 **CMake Target Structure Diagram**

 
```

```

 Sources: [CMakeLists.txt21-28](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L21-L28)

 The two primary targets are:

 
| Target | Alias | Type | Description |
|---|---|---|---|
| rl_tools_core | RLtools::Core | INTERFACE | Header-only base library, requires C++17, includes include/ directory |
| rl_tools_full | RLtools::RLtools | INTERFACE | Full library linking core + backends + optional features |

 The `rl_tools_core` target is defined at [CMakeLists.txt21-24](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L21-L24) and provides just the header includes and C++17 requirement. The `rl_tools_full` target is defined at [CMakeLists.txt26-28](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L26-L28) and adds backends and dependencies based on enabled options.

 Sources: [CMakeLists.txt21-28](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L21-L28)

 
## CMake Options

 RLtools offers many configuration options to customize the build according to your needs. These options can be set when invoking CMake using the `-D` flag.

 **CMake Options and Compile Definitions Diagram**

 
```

```

 Sources: [CMakeLists.txt10-16](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L10-L16) [CMakeLists.txt31-38](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L31-L38) [CMakeLists.txt83-85](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L83-L85) [CMakeLists.txt91-101](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L91-L101)

 Below is a reference table of important CMake options with their default values and effects:

 
| CMake Option | Default | Compile Definition | Linked Libraries | Description |
|---|---|---|---|---|
| RL_TOOLS_ENABLE_TARGETS | ON | - | - | Enables add_subdirectory(src) to build executables |
| RL_TOOLS_ENABLE_TESTS | OFF | - | GTest::gtest_main | Enables add_subdirectory(tests) |
| RL_TOOLS_OFFLINE_BUILD | OFF | - | - | Sets FETCHCONTENT_FULLY_DISCONNECTED for offline builds |
| RL_TOOLS_WARNINGS_AS_ERRORS | ON | - | - | Adds -Werror -Wall -Wextra compiler flags |
| RL_TOOLS_RL_ENVIRONMENTS_ENABLE_MUJOCO | OFF | - | mujoco::mujoco | Includes cmake/optional/mujoco.cmake |

 Sources: [CMakeLists.txt10-16](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L10-L16) [CMakeLists.txt35-52](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L35-L52) [CMakeLists.txt87-89](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L87-L89) [CMakeLists.txt91-101](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L91-L101)

 
### Backend Configuration

 Backend options are autodetected by `cmake/autodetect/all.cmake` and control which computational libraries are used for matrix operations:

 **Backend Selection and Preprocessor Defines**

 
```

```

 Sources: [CMakeLists.txt81](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L81-L81) [src/rl/environments/mujoco/ant/ppo/cpu/training.h16-23](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/mujoco/ant/ppo/cpu/training.h#L16-L23)

 
| Backend Option | Preprocessor Define | Linked Library | Operations Header |
|---|---|---|---|
| RL_TOOLS_BACKEND_ENABLE_MKL | RL_TOOLS_BACKEND_ENABLE_MKL | BLAS::BLAS (MKL) | operations_cpu_mkl.h |
| RL_TOOLS_BACKEND_ENABLE_ACCELERATE | RL_TOOLS_BACKEND_ENABLE_ACCELERATE | BLAS::BLAS (Accelerate) | operations_cpu_accelerate.h |
| RL_TOOLS_BACKEND_ENABLE_CUDA | RL_TOOLS_BACKEND_ENABLE_CUDA | CUDA::cublas | operations_cuda.h |

 The backend selection affects which operations implementation is included via preprocessor conditionals, as seen in training code:

 
```

```

 Sources: [src/rl/environments/mujoco/ant/ppo/cpu/training.h16-24](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/mujoco/ant/ppo/cpu/training.h#L16-L24)

 
### Compiler Optimization Flags

 The build system applies different compiler flags based on build type and configuration options:

 **Compiler Flag Selection Logic**

 
```

```

 Sources: [CMakeLists.txt31-52](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L31-L52)

 
| Configuration Option | Compiler Flags (GCC/Clang) | Compiler Flags (MSVC) | Effect |
|---|---|---|---|
| Release + defaults | -O3 -ffast-math -march=native | /fp:fast | Maximum performance |
| RL_TOOLS_DISABLE_FAST_MATH | -O3 -march=native (no -ffast-math) | (no /fp:fast) | IEEE 754 compliance |
| RL_TOOLS_DISABLE_CPU_SPECIFIC_OPTIMIZATIONS | -O3 -ffast-math (no -march=native) | /fp:fast | Portable binary |
| RL_TOOLS_WARNINGS_AS_ERRORS=ON | -Werror -Wall -Wextra | /W4 /WX | Strict compilation |
| Debug | -DRL_TOOLS_DEBUG + debug flags | /D RL_TOOLS_DEBUG | Runtime checks enabled |

 Sources: [CMakeLists.txt31-52](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L31-L52)

 
### Debug Build Configuration

 When `CMAKE_BUILD_TYPE=Debug`, several preprocessor defines are automatically added to enable runtime checks:

 **Debug Mode Preprocessor Defines**

 
```

```

 These defines enable runtime checks throughout the codebase. For example, `RL_TOOLS_DEBUG_CONTAINER_CHECK_BOUNDS` enables array bounds checking in container operations, while `RL_TOOLS_DEBUG_CONTAINER_MALLOC_INIT_NAN` initializes all allocated memory with NaN values to help detect uninitialized data usage.

 Additionally, the option `RL_TOOLS_TESTS_CODE_COVERAGE` enables code coverage instrumentation:

 
```

```

 Sources: [tests/CMakeLists.txt19-25](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/CMakeLists.txt#L19-L25)

 
## FetchContent Dependency Management

 RLtools uses CMake's FetchContent to manage external dependencies. The base directory for downloaded dependencies is configurable:

 **FetchContent Base Directory Configuration**

 
```

```

 Sources: [CMakeLists.txt55-78](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L55-L78)

 The FetchContent base directory logic:

 
 - If not explicitly set, RLtools tests if the source directory is writable
 - If writable, dependencies are cached in `.dependencies/` within the source tree (shared across build directories)
 - If not writable, dependencies are stored in the build directory
 - Setting `RL_TOOLS_OFFLINE_BUILD=ON` prevents FetchContent from updating dependencies
 
 This design allows multiple build configurations to share downloaded dependencies while supporting read-only source directories.

 Sources: [CMakeLists.txt55-78](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L55-L78)

 
## Building RLtools

 
### Build Process Diagram

 
```

```

 
### Prerequisites

 Before building RLtools, ensure you have:

 
 - CMake (version 3.16 or higher)
 - A C++17 compliant compiler
 - Dependencies for the backends you want to use: 
 - Intel MKL for `RL_TOOLS_BACKEND_ENABLE_MKL`
 - CUDA toolkit for `RL_TOOLS_BACKEND_ENABLE_CUDA`
 - Apple Accelerate framework for `RL_TOOLS_BACKEND_ENABLE_ACCELERATE`
 - OpenBLAS for `RL_TOOLS_BACKEND_ENABLE_OPENBLAS`
 - Optional dependencies based on enabled features: 
 - HDF5 for model persistence
 - TensorBoard for logging
 - MuJoCo for physics simulation
 - JSON libraries for data serialization
 
 Sources: [CMakeLists.txt226-272](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L226-L272) [CMakeLists.txt168-342](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L168-L342)

 
### Basic Build

 To build RLtools with default settings:

 
```

```

 
### Configuring with Specific Features

 To configure RLtools with specific features, use the `-D` option to set CMake variables:

 
```

```

 Sources: [CMakeLists.txt25-53](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L25-L53)

 
## Cross-Platform Support

 
### Platform Support Diagram

 
```

```

 RLtools supports multiple platforms with specific configurations:

 
 - **Linux**: Tested with GCC and Clang, supports MKL and CUDA backends
 - **Windows**: Tested with MSVC, supports CUDA backend
 - **macOS**: Tested with Apple Clang, supports Accelerate backend
 
 The build system automatically adapts compilation flags and optimization settings based on the platform and compiler being used. Platform-specific optimizations are controlled through CMake options like `RL_TOOLS_DISABLE_CPU_SPECIFIC_OPTIMIZATIONS`.

 Sources: [CMakeLists.txt467-489](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L467-L489) [CMakeLists.txt459-465](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L459-L465)

 
## Executable Targets

 When `RL_TOOLS_ENABLE_TARGETS=ON`, the `src/` directory is included and builds environment-algorithm combinations as executables.

 **Executable Target Naming Convention**

 
```

```

 Sources: [src/rl/environments/pendulum/td3/cpu/CMakeLists.txt16-71](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/td3/cpu/CMakeLists.txt#L16-L71) [src/rl/environments/mujoco/ant/ppo/cpu/CMakeLists.txt3-23](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/mujoco/ant/ppo/cpu/CMakeLists.txt#L3-L23) [src/rl/environments/mujoco/ant/ppo/cuda/CMakeLists.txt23-78](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/mujoco/ant/ppo/cuda/CMakeLists.txt#L23-L78)

 
### Pendulum Targets (TD3)

 Defined in [src/rl/environments/pendulum/td3/cpu/CMakeLists.txt](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/td3/cpu/CMakeLists.txt):

 
| Target Name | Backend | Compile Definitions | Link Libraries |
|---|---|---|---|
| rl_environments_pendulum_td3_bare | None | -nostdlib flag | RLtools::Core |
| rl_environments_pendulum_td3_standalone | Generic CPU | - | RLtools::Core |
| rl_environments_pendulum_td3_blas | MKL/Accelerate | RL_TOOLS_DISABLE_HDF5RL_TOOLS_DISABLE_TENSORBOARD | RLtools::RLtools |
| rl_environments_pendulum_td3_blas_benchmark | MKL/Accelerate | RL_TOOLS_DISABLE_HDF5RL_TOOLS_DISABLE_TENSORBOARDRL_TOOLS_RL_ENVIRONMENTS_PENDULUM_DISABLE_EVALUATIONRL_TOOLS_NN_DISABLE_GENERIC_FORWARD_BACKWARD | RLtools::RLtools |
| rl_environments_pendulum_td3_blas_tensorboard | MKL/Accelerate | - | RLtools::RLtools |

 Sources: [src/rl/environments/pendulum/td3/cpu/CMakeLists.txt2-71](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/td3/cpu/CMakeLists.txt#L2-L71)

 
### MuJoCo Ant Targets (PPO)

 Defined in [src/rl/environments/mujoco/ant/ppo/cpu/CMakeLists.txt](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/mujoco/ant/ppo/cpu/CMakeLists.txt) and [src/rl/environments/mujoco/ant/ppo/cuda/CMakeLists.txt](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/mujoco/ant/ppo/cuda/CMakeLists.txt):

 **CPU Targets:**

 
| Target Name | Backend | Compile Definitions | Link Libraries |
|---|---|---|---|
| rl_environments_mujoco_ant_ppo_standalone | Generic CPU | RL_TOOLS_BACKEND_DISABLE_BLASRL_TOOLS_DISABLE_HDF5RL_TOOLS_DISABLE_TENSORBOARD | RLtools::RLtools, Threads::Threads |
| rl_environments_mujoco_ant_ppo_blas_benchmark | MKL/Accelerate | RL_TOOLS_DISABLE_HDF5RL_TOOLS_DISABLE_TENSORBOARD | RLtools::RLtools, Threads::Threads |
| rl_environments_mujoco_ant_ppo_blas | MKL/Accelerate | - | RLtools::RLtools, mujoco::mujoco, Threads::Threads |

 Sources: [src/rl/environments/mujoco/ant/ppo/cpu/CMakeLists.txt3-23](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/mujoco/ant/ppo/cpu/CMakeLists.txt#L3-L23)

 **CUDA Targets:**

 
| Target Name | Language | Compile Definitions | Link Libraries |
|---|---|---|---|
| rl_environments_mujoco_ant_ppo_cuda_standalone | CUDA | RL_TOOLS_BACKEND_DISABLE_BLASRL_TOOLS_DISABLE_HDF5RL_TOOLS_DISABLE_CLI11RL_TOOLS_DISABLE_TENSORBOARD | RLtools::RLtools, mujoco::mujoco, CLI11::CLI11 |
| rl_environments_mujoco_ant_ppo_cuda_benchmark | CUDA | RL_TOOLS_DISABLE_HDF5RL_TOOLS_DISABLE_TENSORBOARDRL_TOOLS_RL_ENVIRONMENTS_MUJOCO_ANT_DISABLE_EVALUATION | RLtools::RLtools, mujoco::mujoco, CLI11::CLI11 |
| rl_environments_mujoco_ant_ppo_cuda_full | CUDA | - | RLtools::RLtools, mujoco::mujoco, CLI11::CLI11 |

 Sources: [src/rl/environments/mujoco/ant/ppo/cuda/CMakeLists.txt24-78](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/mujoco/ant/ppo/cuda/CMakeLists.txt#L24-L78)

 
### Evaluation Targets

 Defined in [src/rl/environments/mujoco/ant/CMakeLists.txt4-14](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/mujoco/ant/CMakeLists.txt#L4-L14):

 
| Target Name | Algorithm | Compile Definitions | Requirements |
|---|---|---|---|
| rl_environments_mujoco_ant_evaluation_td3 | TD3 | - | RL_TOOLS_ENABLE_HDF5RL_TOOLS_RL_ENVIRONMENTS_MUJOCO_ENABLE_UIRL_TOOLS_ENABLE_CLI11 |
| rl_environments_mujoco_ant_evaluation_ppo | PPO | RL_TOOLS_TEST_RL_ENVIRONMENTS_MUJOCO_ANT_EVALUATE_ACTOR_PPO | RL_TOOLS_ENABLE_HDF5RL_TOOLS_RL_ENVIRONMENTS_MUJOCO_ENABLE_UIRL_TOOLS_ENABLE_CLI11 |

 These executables load trained actors from HDF5 checkpoints and visualize them in the MuJoCo UI.

 Sources: [src/rl/environments/mujoco/ant/CMakeLists.txt4-14](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/mujoco/ant/CMakeLists.txt#L4-L14) [src/rl/environments/mujoco/ant/evaluate_actor.cpp54-175](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/mujoco/ant/evaluate_actor.cpp#L54-L175)

 
## Using RLtools as a Dependency

 RLtools can be consumed as a CMake dependency in three ways:

 **Integration Methods Diagram**

 
```

```

 Sources: [CMakeLists.txt21-28](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L21-L28)

 
### Method 1: FetchContent (Recommended)

 
```

```

 
### Method 2: add_subdirectory

 
```

```

 
### Method 3: Installed Package

 After installing RLtools with `cmake --install`:

 
```

```

 
### Choosing Between RLtools::Core and RLtools::RLtools

 
 - **RLtools::Core**: Header-only, no dependencies, minimal features
 - **RLtools::RLtools**: Full library with backends (MKL/CUDA), HDF5, TensorBoard, etc.
 
 Sources: [CMakeLists.txt21-28](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L21-L28)

 
## Test Configuration

 The test framework is enabled with `RL_TOOLS_ENABLE_TESTS=ON` and configured in [tests/CMakeLists.txt](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/CMakeLists.txt)

 **Test Build Configuration**

 
```

```

 Sources: [CMakeLists.txt91-101](https://github.com/rl-tools/rl-tools/blob/a0aef476/CMakeLists.txt#L91-L101) [tests/CMakeLists.txt1-48](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/CMakeLists.txt#L1-L48)

 The `rl_tools_test` interface target provides common test infrastructure:

 
```

```

 Test executables link against `RLtools::Test` to get GoogleTest and common test utilities.

 Sources: [tests/CMakeLists.txt29-35](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/CMakeLists.txt#L29-L35)

 
### Test-Specific CMake Options

 
| Option | Default | Effect |
|---|---|---|
| RL_TOOLS_TEST_LOCAL | OFF | Enable local development mode |
| RL_TOOLS_TESTS_CODE_COVERAGE | OFF | Add --coverage -g -O0 flags for gcov |
| RL_TOOLS_TEST_RL_ENVIRONMENTS_PENDULUM_EVALUATE_VISUALLY | OFF | Enable visual evaluation of pendulum |
| RL_TOOLS_TEST_RL_ALGORITHMS_TD3_SECOND_STAGE_EVALUATE_VISUALLY | OFF | Enable TD3 visual evaluation |

 Sources: [tests/CMakeLists.txt3-19](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/CMakeLists.txt#L3-L19)

 
## Troubleshooting

 Common build issues and solutions:

 
 - **Missing Dependencies**: RLtools will emit clear error messages if required dependencies are missing. Install the necessary packages or disable the corresponding feature.
 - **Platform-Specific Issues**: For platform-specific issues, check the appropriate GitHub workflow files for examples of correct configuration.
 - **Debugging Compilation**: Use `CMAKE_VERBOSE_MAKEFILE=ON` to see the exact compilation commands:

 
```

```
 - **Compilation Errors**: For complex template errors, enable `RL_TOOLS_DEBUG_COMPILER_OPTIONS` to get more detailed error messages:

 
```

```
 
 For Docker-based builds, see the provided Dockerfile for a minimal setup:

 Sources: [tests/Dockerfile1-12](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/Dockerfile#L1-L12) [tests/README.MD1-19](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/README.MD?plain=1#L1-L19)
