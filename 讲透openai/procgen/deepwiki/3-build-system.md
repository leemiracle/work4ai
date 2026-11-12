<!-- source: DeepWiki mcp.deepwiki.com · repo openai/procgen · page 3 Build System · fetched 2026-10-26 -->

# Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [procgen-build/procgen_build/build_package.py](procgen-build/procgen_build/build_package.py)
- [procgen-build/procgen_build/build_qt.py](procgen-build/procgen_build/build_qt.py)
- [procgen/CMakeLists.txt](procgen/CMakeLists.txt)
- [procgen/builder.py](procgen/builder.py)

</details>



The Procgen build system is a multi-layered architecture that orchestrates the compilation of C++ game environments, Qt5 framework dependencies, and Python package distribution across multiple platforms. This system combines Python packaging tools (`cibuildwheel`), Qt5 static compilation, and CMake-based C++ library building to produce platform-specific wheels for distribution.

For information about development environment setup, see [Development Environment](#5.1). For details about the CI/CD pipeline automation, see [CI/CD Pipeline](#5.3).

## Build Architecture Overview

The build system operates in three distinct layers that execute sequentially during package creation. Each layer has specific responsibilities and dependencies on the previous layer's outputs.

**Build Pipeline Flow**
```mermaid
graph TD
    trigger["GitHub Actions Trigger"] --> cibw["cibuildwheel"]
    cibw --> qt_build["build_qt.py"]
    qt_build --> cmake_build["CMake + builder.py"]
    cmake_build --> test["pytest"]
    test --> wheel["Wheel Artifacts"]
    
    subgraph "Layer 1: Package Orchestration"
        cibw
        matrix["Build Matrix:<br/>Python 3.7-3.10<br/>macOS/Linux/Windows"]
        cibw --> matrix
    end
    
    subgraph "Layer 2: Qt5 Framework"
        qt_build
        qt_cache["Qt Build Cache"]
        qt_static["Static Qt5 Libraries"]
        qt_build --> qt_cache
        qt_build --> qt_static
    end
    
    subgraph "Layer 3: C++ Library"
        cmake_build
        env_lib["libenv.so/dll"]
        games["16 Game Implementations"]
        cmake_build --> env_lib
        cmake_build --> games
    end
    
    qt_static --> cmake_build
    env_lib --> test
```

Sources: [procgen-build/procgen_build/build_package.py:10-44](), [procgen-build/procgen_build/build_qt.py:56-166](), [procgen/builder.py:95-148]()

## Component Dependencies

The build system's components have specific dependencies and interfaces that must be maintained across all supported platforms.

**Component Interaction Diagram**
```mermaid
graph TB
    subgraph "build_package.py"
        CIBW_BUILD["CIBW_BUILD<br/>Platform Matrix"]
        CIBW_BEFORE_BUILD["CIBW_BEFORE_BUILD<br/>Qt5 + CMake Setup"]
        CIBW_TEST_COMMAND["CIBW_TEST_COMMAND<br/>pytest execution"]
        PROCGEN_CMAKE_PREFIX_PATH["PROCGEN_CMAKE_PREFIX_PATH<br/>/tmp/qt5/qt/build/qtbase/lib/cmake/Qt5"]
    end
    
    subgraph "build_qt.py"
        cache_folder["cache_folder()"]
        download_source["download_source()"]
        compile_qt["compile_qt()"]
        qt_options["qt_options[]<br/>-static -release -qtnamespace ProcGenQt"]
    end
    
    subgraph "CMakeLists.txt"
        find_package_Qt5["find_package(Qt5 COMPONENTS Gui REQUIRED)"]
        add_library_env["add_library(env SHARED ...)"]
        target_link_libraries["target_link_libraries(env Qt5::Gui)"]
        games_sources["16 Game Source Files<br/>dodgeball.cpp, coinrun.cpp, etc."]
    end
    
    subgraph "builder.py"
        _attempt_configure["_attempt_configure()"]
        build_function["build()"]
        cmake_prefix_paths["cmake_prefix_paths[]"]
        LIBENV_DIR["LIBENV_DIR<br/>gym3.libenv.get_header_dir()"]
    end
    
    CIBW_BEFORE_BUILD --> cache_folder
    cache_folder --> download_source
    cache_folder --> compile_qt
    compile_qt --> qt_options
    
    PROCGEN_CMAKE_PREFIX_PATH --> cmake_prefix_paths
    cmake_prefix_paths --> _attempt_configure
    _attempt_configure --> find_package_Qt5
    
    find_package_Qt5 --> add_library_env
    add_library_env --> games_sources
    add_library_env --> target_link_libraries
    
    build_function --> _attempt_configure
    LIBENV_DIR --> _attempt_configure
    
    CIBW_TEST_COMMAND --> build_function
```

Sources: [procgen-build/procgen_build/build_package.py:11-24](), [procgen-build/procgen_build/build_qt.py:18-46](), [procgen/CMakeLists.txt:40-78](), [procgen/builder.py:52-93]()

## Build Artifacts and Outputs

The build system produces several key artifacts that are used in different contexts:

| Artifact | Location | Purpose | Created By |
|----------|----------|---------|------------|
| `qt5/` source cache | `/tmp/qt5/qt/` or `CACHE_DIR` | Cached Qt5 source to avoid repeated git clones | `build_qt.py:cache_folder()` |
| Static Qt5 libraries | `/tmp/qt5/qt/build/qtbase/lib/` | Platform-specific Qt5 static libraries | `build_qt.py:compile_qt()` |
| `libenv` shared library | `.build/{build_type}/` | C++ game environments compiled library | `builder.py:build()` |
| Platform wheels | `wheelhouse/` | Distributable Python packages | `build_package.py:cibuildwheel` |

**Build Type Configuration**
```mermaid
graph LR
    subgraph "Build Types"
        debug["debug<br/>CMAKE_BUILD_TYPE=debug"]
        relwithdebinfo["relwithdebinfo<br/>CMAKE_BUILD_TYPE=relwithdebinfo"]
    end
    
    subgraph "Platform Specifics"
        windows["Windows<br/>Visual Studio 16 2019<br/>-A x64"]
        macos["macOS<br/>Unix Makefiles<br/>QMAKE_MACOSX_DEPLOYMENT_TARGET=10.13"]
        linux["Linux<br/>Unix Makefiles<br/>-march=ivybridge"]
    end
    
    subgraph "Compiler Flags"
        package_flags["-march=ivybridge<br/>PROCGEN_PACKAGE=ON"]
        dev_flags["-march=native<br/>debug symbols"]
    end
    
    debug --> windows
    debug --> macos
    debug --> linux
    
    relwithdebinfo --> windows
    relwithdebinfo --> macos
    relwithdebinfo --> linux
    
    windows --> package_flags
    macos --> package_flags
    linux --> package_flags
    
    windows --> dev_flags
    macos --> dev_flags
    linux --> dev_flags
```

Sources: [procgen/builder.py:102-147](), [procgen/CMakeLists.txt:15-37](), [procgen-build/procgen_build/build_qt.py:109-164]()

## Cache Management System

The build system implements a sophisticated caching mechanism to avoid rebuilding expensive components like Qt5 across multiple builds.

**Cache Strategy**
```mermaid
graph TD
    cache_check["cache_folder() checks existence"]
    local_exists{"Local cache exists?"}
    options_hash["Generate MD5 hash from options"]
    remote_cache{"Remote cache exists?"}
    download["Extract from tar cache"]
    build_fresh["build_fn() - Fresh build"]
    upload["Create tar and upload"]
    
    cache_check --> local_exists
    local_exists -->|Yes| done["Use existing cache"]
    local_exists -->|No| options_hash
    options_hash --> remote_cache
    remote_cache -->|Yes| download
    remote_cache -->|No| build_fresh
    download --> done
    build_fresh --> upload
    upload --> done
    
    subgraph "Cache Locations"
        cache_dir["CACHE_DIR environment variable"]
        cache_path["cache_dir/name-hash.tar"]
        local_path["Local build directory"]
    end
    
    options_hash --> cache_path
    cache_path --> download
    cache_path --> upload
```

Sources: [procgen-build/procgen_build/build_qt.py:18-46]()

## Platform-Specific Build Configuration

Each platform requires specific configuration to ensure consistent builds across the supported matrix.

| Platform | Generator | Qt Configuration | Special Handling |
|----------|-----------|------------------|------------------|
| **Windows** | `Visual Studio 16 2019 -A x64` | `-mp` for parallel build | `nmake` instead of `make` |
| **macOS** | `Unix Makefiles` | Custom `qmake.conf` with deployment target 10.13 | X11 library paths |
| **Linux** | `Unix Makefiles` | Standard Unix configuration | `manylinux` wheel compatibility |

**Platform Detection Logic**
```mermaid
graph TD
    platform_check["platform.system()"]
    
    windows{"Windows?"}
    macos{"Darwin?"}
    linux["Linux (default)"]
    
    windows_config["Visual Studio generator<br/>nmake build<br/>-mp parallel flag"]
    macos_config["Custom qmake.conf<br/>MACOSX_DEPLOYMENT_TARGET<br/>X11 library paths"]
    linux_config["Unix Makefiles<br/>make -j build<br/>manylinux compatibility"]
    
    platform_check --> windows
    platform_check --> macos
    platform_check --> linux
    
    windows -->|Yes| windows_config
    macos -->|Yes| macos_config
    linux --> linux_config
```

Sources: [procgen/builder.py:66-76](), [procgen-build/procgen_build/build_qt.py:109-164](), [procgen/CMakeLists.txt:22-37]()

## Process Safety and Concurrency

The build system implements multiple layers of process safety to handle concurrent builds and avoid race conditions.

- **File Locking**: `filelock.FileLock(".build-lock")` prevents multiple processes from building simultaneously
- **Global Build Tracking**: `global_builds` set tracks completed builds within a single process
- **Thread Safety**: `global_build_lock` threading lock for process-level coordination
- **Build Directory Isolation**: Each build type gets its own directory (`.build/debug`, `.build/relwithdebinfo`)

Sources: [procgen/builder.py:16-17](), [procgen/builder.py:106-117]()

---

