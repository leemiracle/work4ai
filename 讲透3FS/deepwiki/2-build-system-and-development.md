> 来源: [https://deepwiki.com/deepseek-ai/3FS/2-build-system-and-development](https://deepwiki.com/deepseek-ai/3FS/2-build-system-and-development)
> DeepWiki deepseek-ai/3FS

# Build System and Development

  Relevant source files 
 - [.github/workflows/build.yml](https://github.com/deepseek-ai/3FS/blob/22fca045/.github/workflows/build.yml)
 - [CMakeLists.txt](https://github.com/deepseek-ai/3FS/blob/22fca045/CMakeLists.txt)
 - [Cargo.lock](https://github.com/deepseek-ai/3FS/blob/22fca045/Cargo.lock)
 - [Cargo.toml](https://github.com/deepseek-ai/3FS/blob/22fca045/Cargo.toml)
 - [src/common/utils/Shuffle.h](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/utils/Shuffle.h)
 - [src/fbs/meta/Schema.cc](https://github.com/deepseek-ai/3FS/blob/22fca045/src/fbs/meta/Schema.cc)
 - [src/lib/api/CMakeLists.txt](https://github.com/deepseek-ai/3FS/blob/22fca045/src/lib/api/CMakeLists.txt)
 - [src/lib/rs/hf3fs-usrbio-sys/lib/.dummy](https://github.com/deepseek-ai/3FS/blob/22fca045/src/lib/rs/hf3fs-usrbio-sys/lib/.dummy)
 - [src/meta/components/ChainAllocator.h](https://github.com/deepseek-ai/3FS/blob/22fca045/src/meta/components/ChainAllocator.h)
 - [tests/common/utils/TestShuffle.cc](https://github.com/deepseek-ai/3FS/blob/22fca045/tests/common/utils/TestShuffle.cc)
 
  This document provides a comprehensive guide to building, developing, and contributing to the 3FS (Fire-Flyer File System) codebase. It covers the multi-language build system, development workflows, code quality tools, and environment setup procedures.

 For information about specific Rust components, see [Rust Components](https://deepwiki.com/deepseek-ai/3FS/2.2-rust-components). For details about C++ build targets and configuration, see [C++ Build Configuration](https://deepwiki.com/deepseek-ai/3FS/2.3-c++-build-configuration). For CI/CD workflows and automation, see [CI/CD Pipeline](https://deepwiki.com/deepseek-ai/3FS/2.5-cicd-pipeline).

 
## Build System Architecture

 The 3FS build system integrates both Rust and C++ components through a sophisticated CMake-based approach with Rust workspace management. The system supports multiple build configurations and cross-language interoperability.

 
### Multi-Language Build Integration

 
```

```

 Sources: [CMakeLists.txt1-183](https://github.com/deepseek-ai/3FS/blob/22fca045/CMakeLists.txt#L1-L183) [Cargo.toml1-23](https://github.com/deepseek-ai/3FS/blob/22fca045/Cargo.toml#L1-L23)

 
## CMake Configuration

 The primary build configuration is managed through CMake with extensive compiler and platform support. The build system supports multiple configurations and cross-platform development.

 
### Project Configuration

 The CMake project is configured with the following key settings:

 
| Setting | Value | Purpose |
|---|---|---|
| Project Name | 3FS | Main project identifier |
| Version | 0.1.5 | Current project version |
| Languages | C CXX | Supported languages |
| C++ Standard | 20 | Modern C++ features |
| C Standard | 11 | Standard C compatibility |

 The build system defines four primary build types configured in [CMakeLists.txt4](https://github.com/deepseek-ai/3FS/blob/22fca045/CMakeLists.txt#L4-L4):

 
 - `RelWithDebInfo` (default): Optimized with debug information
 - `Debug`: Unoptimized with full debugging support
 - `Release`: Fully optimized production build
 - `MinSizeRel`: Size-optimized build
 
 
### Compiler Support and Flags

 The system supports both Clang and GCC compilers with specific optimizations:

 
#### Compiler Support and Flag Configuration

 
```

```

 
#### Compiler-Specific Configuration

 **Clang Configuration** [CMakeLists.txt83-88](https://github.com/deepseek-ai/3FS/blob/22fca045/CMakeLists.txt#L83-L88):

 
 - Coroutines support: `-fcoroutines-ts`
 - Atomic operations linking: `-latomic`
 - Linker: `-fuse-ld=lld` (LLVM linker)
 - FoundationDB compatibility: `USE_LIBCXX OFF` (do not use libc++)
 
 **GCC Configuration** [CMakeLists.txt89-91](https://github.com/deepseek-ai/3FS/blob/22fca045/CMakeLists.txt#L89-L91):

 
 - Coroutines support: `-fcoroutines`
 
 
#### Platform-Specific Optimizations

 **x86_64 Architecture** [CMakeLists.txt96-97](https://github.com/deepseek-ai/3FS/blob/22fca045/CMakeLists.txt#L96-L97):

 
 - SSE 4.2 instructions: `-msse4.2`
 - AVX2 instructions: `-mavx2`
 
 **ARM Architecture** [CMakeLists.txt98-106](https://github.com/deepseek-ai/3FS/blob/22fca045/CMakeLists.txt#L98-L106):

 
 - ARM v8-A with CRC: `-march=armv8-a+crc`
 - Compiler runtime library: `-rtlib=compiler-rt` (provides `__muloti4` symbol)
 - Exception unwinding: `-unwindlib=libgcc`
 
 
#### Common Build Configuration

 All builds include [CMakeLists.txt74-81](https://github.com/deepseek-ai/3FS/blob/22fca045/CMakeLists.txt#L74-L81):

 
 - C++20 standard enforcement: `CMAKE_CXX_STANDARD 20`, `CMAKE_CXX_STANDARD_REQUIRED ON`
 - C11 standard: `CMAKE_C_STANDARD 11`
 - Position-independent code: `CMAKE_POSITION_INDEPENDENT_CODE ON`
 - Compile commands export: `CMAKE_EXPORT_COMPILE_COMMANDS ON` (for IDE integration)
 - Source path mapping: `-fmacro-prefix-map=${CMAKE_SOURCE_DIR}=.` (cleaner `__FILE__` output)
 
 
#### Warning Configuration

 Strict warning flags [CMakeLists.txt174](https://github.com/deepseek-ai/3FS/blob/22fca045/CMakeLists.txt#L174-L174) applied after third-party dependencies:

 
 - All warnings: `-Wall`
 - Extra warnings: `-Wextra`
 - Warnings as errors: `-Werror`
 - Pedantic mode: `-Wpedantic`
 
 Sources: [CMakeLists.txt74-106](https://github.com/deepseek-ai/3FS/blob/22fca045/CMakeLists.txt#L74-L106) [CMakeLists.txt174](https://github.com/deepseek-ai/3FS/blob/22fca045/CMakeLists.txt#L174-L174)

 
### Third-Party Dependencies

 The build system integrates numerous third-party libraries through CMake subdirectories. All third-party libraries use `EXCLUDE_FROM_ALL` to prevent installation and use the `store_compile_flags()` / `restore_compile_flags()` pattern to isolate their build flags from 3FS strict warnings [CMakeLists.txt112-172](https://github.com/deepseek-ai/3FS/blob/22fca045/CMakeLists.txt#L112-L172)

 
| Library | Location | Purpose | Key Configuration |
|---|---|---|---|
| fmt | third_party/fmt | String formatting | Standard build |
| zstd | third_party/zstd/build/cmake | Compression | ZSTD_BUILD_STATIC ON |
| googletest | third_party/googletest | Testing framework | Standard build |
| folly | third_party/folly | Facebook utilities | FOLLY_NO_EXCEPTION_TRACER ON |
| leveldb | third_party/leveldb | Basic key-value storage | LEVELDB_BUILD_TESTS OFF, LEVELDB_BUILD_BENCHMARKS OFF, LEVELDB_INSTALL OFF |
| rocksdb | third_party/rocksdb | Advanced storage engine | WITH_LZ4 ON, WITH_ZSTD ON, USE_RTTI ON, tests/tools disabled, ROCKSDB_NAMESPACE=rocksdb_internal |
| scnlib | third_party/scnlib | Input scanning | All optional components disabled |
| pybind11 | third_party/pybind11 | Python bindings | Standard build |
| toml11 | third_party/toml11 | TOML parsing | Standard build |
| mimalloc | third_party/mimalloc | Memory allocator | MI_OVERRIDE OFF |
| clickhouse-cpp | third_party/clickhouse-cpp | ClickHouse client | Custom include directories for clickhouse-cpp-lib and absl-lib |
| liburing | third_party/liburing-cmake | Async I/O (io_uring) | Linux kernel interface |

 
#### Dependency Build Isolation

 The `store_compile_flags()` and `restore_compile_flags()` macros (defined in [cmake/CompileFlags.cmake](https://github.com/deepseek-ai/3FS/blob/22fca045/cmake/CompileFlags.cmake)) are used before and after each third-party dependency to:

 
 - Save current compiler flags before building third-party code
 - Allow third-party libraries to build without 3FS's strict `-Werror` requirements
 - Restore strict flags for 3FS code
 
 
#### RocksDB Configuration

 RocksDB receives special namespace isolation [CMakeLists.txt107](https://github.com/deepseek-ai/3FS/blob/22fca045/CMakeLists.txt#L107-L107):

 
```

```

 This prevents symbol conflicts with other RocksDB installations on the system.

 Sources: [CMakeLists.txt107](https://github.com/deepseek-ai/3FS/blob/22fca045/CMakeLists.txt#L107-L107) [CMakeLists.txt112-172](https://github.com/deepseek-ai/3FS/blob/22fca045/CMakeLists.txt#L112-L172)

 
## Rust Workspace Configuration

 The Rust components are organized as a Cargo workspace with three primary crates and specific build profiles for CMake integration.

 
### Workspace Structure

 The workspace is defined in [Cargo.toml1-11](https://github.com/deepseek-ai/3FS/blob/22fca045/Cargo.toml#L1-L11) with the following members:

 
```

```

 
### Build Profile Configuration

 The workspace defines a special `release-cmake` profile optimized for CMake integration:

 
| Setting | Value | Purpose |
|---|---|---|
| inherits | "release" | Based on release configuration |
| debug | true | Include debug symbols |
| lto | true | Enable link-time optimization |

 This profile ensures Rust components built through CMake maintain compatibility with C++ debug workflows while preserving optimization.

 Sources: [Cargo.toml13-23](https://github.com/deepseek-ai/3FS/blob/22fca045/Cargo.toml#L13-L23)

 
## Multi-Language Integration

 The integration between Rust and C++ components is facilitated through the `AddCrate.cmake` module and cxxbridge for type-safe interoperability.

 
### Development Workflow

 
```

```

 
### Build Configuration Options

 The build system provides several configuration options through CMake variables:

 
| Option | Type | Default | Description |
|---|---|---|---|
| SHUFFLE_METHOD | Required | None | Shuffle algorithm selection: g++10, g++11, or stdshuffle |
| ENABLE_ASSERTIONS | Optional | ON (Debug), OFF (others) | Enable runtime assertions with _DEBUG definition |
| OVERRIDE_CXX_NEW_DELETE | Optional | OFF | Override global new/delete operators (disabled with sanitizers) |
| SAVE_ALLOCATE_SIZE | Optional | OFF | Track allocation sizes (requires OVERRIDE_CXX_NEW_DELETE) |
| ENABLE_FUSE_APPLICATION | Optional | ON | Build FUSE integration components |

 
#### Required Configuration: SHUFFLE_METHOD

 The `SHUFFLE_METHOD` parameter is mandatory and controls the shuffle algorithm used in sorting operations. The build will fail with an error if not specified:

 
```

```

 The three available methods defined in [CMakeLists.txt30](https://github.com/deepseek-ai/3FS/blob/22fca045/CMakeLists.txt#L30-L30) are:

 
 - `g++10`: Uses GCC 10 shuffle implementation with `USE_GCC10_SHUFFLE` definition
 - `g++11`: Uses GCC 11 shuffle implementation with `USE_GCC11_SHUFFLE` definition
 - `stdshuffle`: Uses standard C++ `std::shuffle` with `USE_STD_SHUFFLE` definition
 
 The choice of shuffle method is critical because different GCC versions (and `std::shuffle`) can produce different shuffle sequences for the same seed [src/common/utils/Shuffle.h174-194](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/utils/Shuffle.h#L174-L194) The `safe_shuffle_seed` function [src/common/utils/Shuffle.h174](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/utils/Shuffle.h#L174-L174) is used to verify that a given seed produces consistent results across `std::shuffle`, `gcc_shuffle<true>` (GCC 11), and `gcc_shuffle<false>` (GCC 10) implementations. This is particularly important for `Layout::ChainRange` [src/fbs/meta/Schema.h122](https://github.com/deepseek-ai/3FS/blob/22fca045/src/fbs/meta/Schema.h#L122-L122) which uses `hf3fs_shuffle` [src/common/utils/Shuffle.h162](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/utils/Shuffle.h#L162-L162) to determine chain distribution. The `find_safe_seed` function [src/common/utils/Shuffle.h196](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/utils/Shuffle.h#L196-L196) attempts to find a seed that is safe across these implementations.

 Sources: [CMakeLists.txt30-72](https://github.com/deepseek-ai/3FS/blob/22fca045/CMakeLists.txt#L30-L72) [src/common/utils/Shuffle.h174-194](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/utils/Shuffle.h#L174-L194) [src/common/utils/Shuffle.h174](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/utils/Shuffle.h#L174-L174) [src/common/utils/Shuffle.h196](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/utils/Shuffle.h#L196-L196) [src/fbs/meta/Schema.h122](https://github.com/deepseek-ai/3FS/blob/22fca045/src/fbs/meta/Schema.h#L122-L122) [src/common/utils/Shuffle.h162](https://github.com/deepseek-ai/3FS/blob/22fca045/src/common/utils/Shuffle.h#L162-L162)

 
#### Memory Management Options

 The `OVERRIDE_CXX_NEW_DELETE` option [CMakeLists.txt56-71](https://github.com/deepseek-ai/3FS/blob/22fca045/CMakeLists.txt#L56-L71) enables custom memory allocation tracking:

 
 - Automatically disabled when `SANITIZER` is enabled to prevent conflicts
 - When enabled with `SAVE_ALLOCATE_SIZE`, allocates additional memory to track allocation sizes
 - Adds `OVERRIDE_CXX_NEW_DELETE` and optionally `SAVE_ALLOCATE_SIZE` preprocessor definitions
 
 Sources: [CMakeLists.txt30-72](https://github.com/deepseek-ai/3FS/blob/22fca045/CMakeLists.txt#L30-L72)

 
## Build Targets and Subdirectories

 The build system organizes code into three primary subdirectories, each serving distinct purposes:

 
| Directory | Purpose | Content |
|---|---|---|
| src/ | Core implementation | Main 3FS components and libraries |
| tests/ | Testing infrastructure | Unit tests and integration tests |
| benchmarks/ | Performance measurement | Benchmarking tools and frameworks |

 The modular CMake structure allows for selective building and testing of individual components while maintaining dependency resolution across the multi-language codebase.

 Sources: [CMakeLists.txt180-182](https://github.com/deepseek-ai/3FS/blob/22fca045/CMakeLists.txt#L180-L182)
