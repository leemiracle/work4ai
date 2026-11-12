> 来源: [https://deepwiki.com/pytorch/ELF/7-building-and-development](https://deepwiki.com/pytorch/ELF/7-building-and-development)
> DeepWiki pytorch/ELF | Last indexed: 23 April 2025 (e851e7

# Building and Development

  Relevant source files 
 - [CMakeLists.txt](https://github.com/pytorch/ELF/blob/e851e786/CMakeLists.txt)
 - [src_cpp/elf/ai/tree_search/tree_search_node.h](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elf/ai/tree_search/tree_search_node.h)
 - [src_cpp/elfgames/go/CMakeLists.txt](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/CMakeLists.txt)
 - [third_party/CMakeLists.txt](https://github.com/pytorch/ELF/blob/e851e786/third_party/CMakeLists.txt)
 
  This page provides information for developers who want to build and modify the ELF OpenGo platform. It covers the build system configuration, dependencies, compilation process, and development workflow. For information about using ELF OpenGo's various execution modes, see [Execution Modes](https://deepwiki.com/pytorch/ELF/6-execution-modes).

 
## Build System Overview

 ELF OpenGo uses CMake as its build system, with a minimum required version of 3.3. The project follows a modular approach with separate CMakeLists.txt files for different components:

 
```

```

 Sources: [CMakeLists.txt1-82](https://github.com/pytorch/ELF/blob/e851e786/CMakeLists.txt#L1-L82) [third_party/CMakeLists.txt1-56](https://github.com/pytorch/ELF/blob/e851e786/third_party/CMakeLists.txt#L1-L56) [src_cpp/elfgames/go/CMakeLists.txt1-87](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/CMakeLists.txt#L1-L87)

 
## Dependencies

 
### System Requirements

 
 - **C++ Compiler**: GCC 7.1 or later (supports C++17)
 - **CMake**: Version 3.3 or later
 - **ZeroMQ**: Library and development headers
 
 
### Third-party Libraries

 The majority of third-party dependencies are included in the repository and managed by the build system:

 
| Library | Purpose |
|---|---|
| GoogleTest | Unit testing framework |
| JSON | JSON parsing and serialization |
| pybind11 | Python bindings for C++ |
| spdlog | Fast C++ logging library |
| concurrentqueue | Lock-free concurrent queue |
| TBB | Threading Building Blocks for parallelism |
| ZeroMQ | Messaging library for distributed communication |

 Sources: [third_party/CMakeLists.txt1-56](https://github.com/pytorch/ELF/blob/e851e786/third_party/CMakeLists.txt#L1-L56) [CMakeLists.txt3-17](https://github.com/pytorch/ELF/blob/e851e786/CMakeLists.txt#L3-L17)

 
## Build Process

 
### Build Steps

 
 - Clone the repository:
 
 
```

```

 
 - Create and enter a build directory:
 
 
```

```

 
 - Configure the build with CMake:
 
 
```

```

 
 - Compile the project:
 
 
```

```

 
### Build Options

 
| Option | Description | Default |
|---|---|---|
| CMAKE_BUILD_TYPE | Build type (Release/Debug) | Release |
| BOARD9x9 | Use 9x9 board instead of 19x19 | OFF |

 Example setting a build option:

 
```

```

 The following diagram illustrates the CMake configuration process:

 
```

```

 Sources: [CMakeLists.txt20-50](https://github.com/pytorch/ELF/blob/e851e786/CMakeLists.txt#L20-L50) [src_cpp/elfgames/go/CMakeLists.txt33-49](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/CMakeLists.txt#L33-L49)

 
## Development Workflow

 The typical development workflow for ELF OpenGo involves making changes to C++ code, rebuilding, running tests, and using the Python interface for training and evaluation:

 
```

```

 
### Code Organization

 The codebase is organized into several key directories:

 
| Directory | Description |
|---|---|
| src_cpp/elf | Core ELF framework |
| src_cpp/elfgames/go | Go game implementation |
| third_party | Third-party dependencies |
| scripts | Utility scripts |
| train | Training scripts |

 Sources: [CMakeLists.txt67-81](https://github.com/pytorch/ELF/blob/e851e786/CMakeLists.txt#L67-L81)

 
## Testing Framework

 ELF OpenGo uses GoogleTest for unit testing. The build system provides a convenience function `add_cpp_tests` to simplify adding new tests.

 
### Running Tests

 To run all tests:

 
```

```

 To run a specific test:

 
```

```

 
### Adding New Tests

 The root CMakeLists.txt defines a custom function for creating test executables:

 
```

```

 Examples of test files in the Go implementation:

 
 - base/test/coord_test.cc
 - base/test/go_test.cc
 - base/test/board_feature_test.cc
 - base/test/symmetry_test.cc
 - sgf/sgf_test.cc
 
 Sources: [CMakeLists.txt52-65](https://github.com/pytorch/ELF/blob/e851e786/CMakeLists.txt#L52-L65) [src_cpp/elfgames/go/CMakeLists.txt77-86](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/CMakeLists.txt#L77-L86)

 
## Board Size Configuration

 ELF OpenGo supports different Go board sizes, controlled through compile-time options:

 
### Standard Board (19x19)

 This is the default configuration, built as the `elfgames_go` library.

 
### 9x9 Board

 This smaller board size is useful for faster development, testing, and experimentation. To enable:

 
```

```

 The system builds specialized libraries for different board sizes:

 
 - `elfgames_go` - Standard library (19x19 by default, or 9x9 if BOARD9x9 is enabled)
 - `elfgames_go9` - Always 9x9 board (built specifically for testing purposes)
 
 Sources: [src_cpp/elfgames/go/CMakeLists.txt32-57](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/CMakeLists.txt#L32-L57)

 
## Python Bindings

 ELF OpenGo uses pybind11 to create Python bindings for C++ code, enabling integration between low-level game logic (C++) and high-level training (Python).

 Two main Python modules are created:

 
 - `_elfgames_go` - For training
 - `_elfgames_go_inference` - For inference/evaluation
 
 
```

```

 Sources: [src_cpp/elfgames/go/CMakeLists.txt60-71](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/CMakeLists.txt#L60-L71)

 
## Tree Search Development

 The Monte Carlo Tree Search (MCTS) component is a critical part of ELF OpenGo. Developers working on the MCTS implementation should understand these key classes:

 
 - `NodeBaseT<State>` - Base class for tree nodes, manages state storage
 - `NodeT<State, Action>` - Tree node implementation, handles visits, values, and actions
 - `SearchTreeT<State, Action>` - Manages the entire search tree structure
 
 These components form the backbone of the AI's decision-making process and are extensively used throughout the Go game implementation.

 Sources: [src_cpp/elf/ai/tree_search/tree_search_node.h1-567](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elf/ai/tree_search/tree_search_node.h#L1-L567)

 
## Troubleshooting Build Issues

 
### Compiler Version Issues

 If you encounter errors related to C++17 features, ensure your compiler is GCC 7.1 or later:

 
```

```

 
### Missing Dependencies

 If CMake fails to find ZeroMQ, install the development headers:

 
```

```

 
### Build Failure with TBB

 If the build fails with TBB-related errors, you may need to specify the TBB path:

 
```

```

 Sources: [CMakeLists.txt20-26](https://github.com/pytorch/ELF/blob/e851e786/CMakeLists.txt#L20-L26) [third_party/CMakeLists.txt37-49](https://github.com/pytorch/ELF/blob/e851e786/third_party/CMakeLists.txt#L37-L49)
