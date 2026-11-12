<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvnmos · page 6 Build System · fetched 2026-10-26 -->

# Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/CMakeLists.txt](src/CMakeLists.txt)
- [src/cmake/NvNmosCommon.cmake](src/cmake/NvNmosCommon.cmake)
- [src/cmake/NvNmosExports.cmake](src/cmake/NvNmosExports.cmake)

</details>



## Purpose and Scope

This document provides a comprehensive overview of the nvnmos build system, covering the CMake-based build configuration, dependency management, build targets, and integration with continuous integration pipelines. It explains how the library and example application are compiled, linked, and packaged for distribution.

For detailed information about specific build system components, see:
- CMake configuration details: [CMake Configuration](#6.1)
- Package export mechanisms: [Package Configuration and Exports](#6.2)
- Conan dependency management: [Dependency Management with Conan](#6.3)
- Docker containerization: [Docker Build Process](#6.4)

---

## Build System Overview

The nvnmos build system uses CMake as the primary build orchestrator, Conan for C++ dependency management, and supports both native and containerized builds. The system is designed to produce shared or static libraries, example applications, and distribution packages.

**Build Technology Stack**

```mermaid
flowchart TB
    subgraph "Build Tools"
        CMAKE["CMake 3.17+<br/>(3.24+ for conan integration)"]
        CONAN["Conan Package Manager<br/>C++ Dependencies"]
        NINJA["Ninja / Make<br/>Build Backend"]
    end
    
    subgraph "Build Configuration Files"
        CMAKELISTS["src/CMakeLists.txt<br/>Main build configuration"]
        COMMON["src/cmake/NvNmosCommon.cmake<br/>Common settings"]
        EXPORTS["src/cmake/NvNmosExports.cmake<br/>Package exports"]
        CONANFILE["conanfile.py<br/>Dependency specification"]
        CONANLOCK["conan.lock<br/>Version lockfile"]
    end
    
    subgraph "Build Targets"
        NVNMOS_LIB["nvnmos library<br/>Shared or Static"]
        EXAMPLE["nvnmos-example<br/>Executable"]
    end
    
    subgraph "Dependencies"
        NMOS_CPP["nmos-cpp::nmos-cpp<br/>Core NMOS implementation"]
        COMPILE_SETTINGS["nmos-cpp::compile-settings<br/>Compiler flags"]
        TRANSITIVE["Transitive Dependencies<br/>Boost, cpprestsdk, etc."]
    end
    
    subgraph "Build Artifacts"
        SO["libnvnmos.so / nvnmos.dll"]
        EXE["nvnmos-example binary"]
        HEADERS["nvnmos.h header"]
        CMAKE_PKG["nvnmos-config.cmake<br/>nvnmos-targets.cmake"]
    end
    
    CMAKE --> CMAKELISTS
    CONAN --> CONANFILE
    CONANFILE --> CONANLOCK
    
    CMAKELISTS --> COMMON
    CMAKELISTS --> EXPORTS
    CMAKELISTS --> NVNMOS_LIB
    CMAKELISTS --> EXAMPLE
    
    NVNMOS_LIB --> NMOS_CPP
    NVNMOS_LIB --> COMPILE_SETTINGS
    NMOS_CPP --> TRANSITIVE
    
    NVNMOS_LIB --> SO
    NVNMOS_LIB --> HEADERS
    EXAMPLE --> EXE
    EXPORTS --> CMAKE_PKG
    
    NINJA --> SO
    NINJA --> EXE
```

**Sources:** [src/CMakeLists.txt:1-145](), [src/cmake/NvNmosCommon.cmake:1-65](), [src/cmake/NvNmosExports.cmake:1-39]()

---

## Build Targets

The build system defines two primary targets:

| Target | Type | Description | Build Option |
|--------|------|-------------|--------------|
| `nvnmos` | Library | Core NMOS control plane library (shared or static) | `BUILD_SHARED_LIBS` |
| `nvnmos-example` | Executable | Example application demonstrating library usage | `NVNMOS_BUILD_EXAMPLES` |

**nvnmos Library Target**

The `nvnmos` library target is created at [src/CMakeLists.txt:71-110]() and includes:

- **Source Files**: `nvnmos.cpp`, `nvnmos_impl.cpp` [src/CMakeLists.txt:56-59]()
- **Public Headers**: `nvnmos.h` [src/CMakeLists.txt:60-62]()
- **Private Headers**: `nvnmos_impl.h` [src/CMakeLists.txt:63-65]()
- **Link Dependencies**: `nmos-cpp::nmos-cpp`, `nmos-cpp::compile-settings` [src/CMakeLists.txt:85-99]()
- **Compile Definitions**: `NVNMOS_EXPORTS` (shared), `NVNMOS_STATIC` (static) [src/CMakeLists.txt:80-100]()
- **Installed Headers**: Only public interface headers are installed [src/CMakeLists.txt:107]()

The library can be referenced by consumers as `nvnmos::nvnmos` via the namespace alias [src/CMakeLists.txt:110]().

**nvnmos-example Target**

The example executable is created at [src/CMakeLists.txt:121-133]() when `NVNMOS_BUILD_EXAMPLES` is enabled:

- **Source Files**: `main.c` [src/CMakeLists.txt:115-117]()
- **Link Dependencies**: `nvnmos` library [src/CMakeLists.txt:130-133]()
- **Language**: Pure C application demonstrating C API usage

**Sources:** [src/CMakeLists.txt:56-140]()

---

## Build Options and Configuration

**CMake Options**

| Option | Default | Description |
|--------|---------|-------------|
| `BUILD_SHARED_LIBS` | `ON` | Build nvnmos as shared library (`.so`/`.dll`) instead of static (`.a`/`.lib`) |
| `NVNMOS_BUILD_EXAMPLES` | `ON` | Build the nvnmos-example application |
| `USE_ADD_SUBDIRECTORY` | `OFF` | Use nmos-cpp as subdirectory instead of via `find_package()` |
| `NMOS_CPP_DIRECTORY` | `../../nmos-cpp/Development` | Path to nmos-cpp when using subdirectory mode |

**CMake Version Requirements**

The build system supports two CMake usage patterns [src/CMakeLists.txt:16-24]():

- **Standard Mode**: CMake 3.17+ required, must run `conan install` separately
- **Injection Point Mode**: CMake 3.24+ required, can use `CMAKE_PROJECT_TOP_LEVEL_INCLUDES` for automatic Conan integration

**C++ Standard Requirements**

The build enforces C++11 or higher [src/cmake/NvNmosCommon.cmake:28-39]():
- Rejects C++98 with fatal error
- Sets `CMAKE_CXX_STANDARD_REQUIRED` to `ON`
- Sets `CMAKE_CXX_EXTENSIONS` to `OFF` (disable compiler-specific extensions)

**Sources:** [src/CMakeLists.txt:20-52](), [src/cmake/NvNmosCommon.cmake:28-39]()

---

## File Organization

**CMake Module Structure**

```mermaid
graph TB
    subgraph "Source Root: src/"
        MAIN["CMakeLists.txt<br/>Main build configuration"]
        
        subgraph "cmake/ Module Directory"
            COMMON_FILE["NvNmosCommon.cmake<br/>Build settings"]
            EXPORTS_FILE["NvNmosExports.cmake<br/>Package exports"]
            CONFIG_IN["nvnmos-config.cmake.in<br/>Package template"]
        end
        
        subgraph "Source Files"
            NVNMOS_CPP["nvnmos.cpp<br/>C API implementation"]
            IMPL_CPP["nvnmos_impl.cpp<br/>NMOS logic"]
            MAIN_C["main.c<br/>Example application"]
        end
        
        subgraph "Header Files"
            NVNMOS_H["nvnmos.h<br/>Public C API"]
            IMPL_H["nvnmos_impl.h<br/>Private interface"]
        end
    end
    
    subgraph "Build Directory: build/"
        CMAKE_CACHE["CMakeCache.txt"]
        NVNMOS_BIN["libnvnmos.so"]
        EXAMPLE_BIN["nvnmos-example"]
        
        subgraph "cmake/ Generated"
            CONFIG_GEN["nvnmos-config.cmake<br/>Generated package config"]
        end
    end
    
    subgraph "Install Directory"
        INSTALL_INCLUDE["include/<br/>nvnmos.h"]
        INSTALL_LIB["lib/<br/>libnvnmos.so"]
        INSTALL_BIN["bin/<br/>nvnmos-example"]
        
        subgraph "lib/cmake/nvnmos/"
            INSTALL_CONFIG["nvnmos-config.cmake"]
            INSTALL_TARGETS["nvnmos-targets.cmake"]
        end
    end
    
    MAIN --> COMMON_FILE
    MAIN --> EXPORTS_FILE
    EXPORTS_FILE --> CONFIG_IN
    
    MAIN --> NVNMOS_CPP
    MAIN --> IMPL_CPP
    MAIN --> MAIN_C
    
    MAIN --> NVNMOS_H
    MAIN --> IMPL_H
    
    CONFIG_IN --> CONFIG_GEN
    
    NVNMOS_BIN --> INSTALL_LIB
    EXAMPLE_BIN --> INSTALL_BIN
    NVNMOS_H --> INSTALL_INCLUDE
    
    CONFIG_GEN --> INSTALL_CONFIG
    EXPORTS_FILE --> INSTALL_TARGETS
```

**Install Directory Layout**

The build uses platform-specific install paths via `GNUInstallDirs` [src/cmake/NvNmosCommon.cmake:16]():

- **Headers**: `${CMAKE_INSTALL_INCLUDEDIR}/${NVNMOS_INCLUDE_PREFIX}` [src/cmake/NvNmosCommon.cmake:19]()
- **Libraries**: `${CMAKE_INSTALL_LIBDIR}` with Debug/Release subdirs on Windows [src/cmake/NvNmosCommon.cmake:21-26]()
- **Binaries**: `${CMAKE_INSTALL_BINDIR}` with Debug/Release subdirs on Windows [src/cmake/NvNmosCommon.cmake:22-26]()
- **CMake Package**: `${CMAKE_INSTALL_LIBDIR}/cmake/nvnmos` [src/cmake/NvNmosExports.cmake:28]()

**Sources:** [src/CMakeLists.txt:1-145](), [src/cmake/NvNmosCommon.cmake:16-26]()

---

## Dependency Resolution

**nmos-cpp Dependency**

The build supports two methods for resolving the nmos-cpp dependency:

**Method 1: find_package() (Default)**

```mermaid
flowchart LR
    CMAKELISTS["CMakeLists.txt<br/>find_package(nmos-cpp REQUIRED)"]
    
    subgraph "Package Discovery"
        CONAN_PKG["Conan-installed package<br/>nmos-cppConfig.cmake"]
        SYSTEM_PKG["System-installed package<br/>/usr/lib/cmake/nmos-cpp"]
    end
    
    TARGET["nmos-cpp::nmos-cpp target<br/>+ transitive dependencies"]
    
    CMAKELISTS --> CONAN_PKG
    CMAKELISTS --> SYSTEM_PKG
    CONAN_PKG --> TARGET
    SYSTEM_PKG --> TARGET
```

This method requires nmos-cpp and all its dependencies (Boost, cpprestsdk, WebSocket++, OpenSSL, etc.) to be pre-installed and discoverable via CMake's package mechanism. Conan handles this automatically when `conan install` is run [src/CMakeLists.txt:40-46]().

**Method 2: add_subdirectory() (Optional)**

When `USE_ADD_SUBDIRECTORY` is enabled, nmos-cpp is built as part of the nvnmos build [src/CMakeLists.txt:47-52](). The path is specified via `NMOS_CPP_DIRECTORY`, defaulting to `../../nmos-cpp/Development`. The subdirectory is excluded from installation via `EXCLUDE_FROM_ALL`.

**Sources:** [src/CMakeLists.txt:36-52]()

---

## Build Process Flow

**Complete Build Workflow**

```mermaid
flowchart TB
    START[["Developer invokes build"]]
    
    subgraph "Phase 1: Dependency Resolution"
        CONAN_INSTALL["conan install . --build=missing<br/>Install nmos-cpp + dependencies"]
        CONAN_GENERATE["Generate CMake toolchain<br/>conan_toolchain.cmake"]
    end
    
    subgraph "Phase 2: CMake Configuration"
        CMAKE_CONFIG["cmake -B build -S src<br/>Configure build system"]
        LOAD_COMMON["Load NvNmosCommon.cmake<br/>Set compiler flags<br/>Configure install paths"]
        FIND_NMOS["find_package(nmos-cpp)<br/>or add_subdirectory()"]
        DEFINE_TARGETS["Define nvnmos library<br/>Define nvnmos-example"]
        LOAD_EXPORTS["Load NvNmosExports.cmake<br/>Configure package exports"]
    end
    
    subgraph "Phase 3: Build Execution"
        CMAKE_BUILD["cmake --build build<br/>Compile source files"]
        COMPILE_LIB["Compile nvnmos.cpp<br/>Compile nvnmos_impl.cpp"]
        LINK_LIB["Link libnvnmos.so<br/>with nmos-cpp::nmos-cpp"]
        COMPILE_EXAMPLE["Compile main.c"]
        LINK_EXAMPLE["Link nvnmos-example<br/>with nvnmos"]
    end
    
    subgraph "Phase 4: Installation"
        CMAKE_INSTALL["cmake --install build<br/>Install artifacts"]
        INSTALL_HEADERS["Install nvnmos.h<br/>to include/"]
        INSTALL_LIB_BIN["Install library/binary<br/>to lib/ and bin/"]
        INSTALL_CMAKE["Install nvnmos-config.cmake<br/>and nvnmos-targets.cmake"]
    end
    
    subgraph "Phase 5: Package Generation"
        CPACK["cpack -G TGZ<br/>Create distribution package"]
        TARBALL["nvnmos-*.tar.gz"]
    end
    
    START --> CONAN_INSTALL
    CONAN_INSTALL --> CONAN_GENERATE
    CONAN_GENERATE --> CMAKE_CONFIG
    
    CMAKE_CONFIG --> LOAD_COMMON
    LOAD_COMMON --> FIND_NMOS
    FIND_NMOS --> DEFINE_TARGETS
    DEFINE_TARGETS --> LOAD_EXPORTS
    
    LOAD_EXPORTS --> CMAKE_BUILD
    CMAKE_BUILD --> COMPILE_LIB
    COMPILE_LIB --> LINK_LIB
    CMAKE_BUILD --> COMPILE_EXAMPLE
    LINK_LIB --> LINK_EXAMPLE
    COMPILE_EXAMPLE --> LINK_EXAMPLE
    
    LINK_LIB --> CMAKE_INSTALL
    LINK_EXAMPLE --> CMAKE_INSTALL
    CMAKE_INSTALL --> INSTALL_HEADERS
    CMAKE_INSTALL --> INSTALL_LIB_BIN
    CMAKE_INSTALL --> INSTALL_CMAKE
    
    CMAKE_INSTALL --> CPACK
    CPACK --> TARBALL
```

**Sources:** [src/CMakeLists.txt:1-145](), [src/cmake/NvNmosCommon.cmake:1-65](), [src/cmake/NvNmosExports.cmake:1-39]()

---

## Build Configuration Details

**Shared vs Static Library Configuration**

The `BUILD_SHARED_LIBS` option controls library type and affects linking behavior:

**Shared Library Mode** (`BUILD_SHARED_LIBS=ON`, default) [src/CMakeLists.txt:80-89]():
- Defines `NVNMOS_EXPORTS` as private compile definition
- Links nmos-cpp dependencies as `PRIVATE` (not exposed to consumers)
- Produces platform-specific shared library (`.so`, `.dll`, `.dylib`)

**Static Library Mode** (`BUILD_SHARED_LIBS=OFF`) [src/CMakeLists.txt:90-100]():
- Defines `NVNMOS_STATIC` as public compile definition
- Links nmos-cpp dependencies as `PUBLIC` (exposed to consumers)
- Produces static library (`.a`, `.lib`)
- Consumers must link against nmos-cpp transitively

**Build Type Validation**

The build system validates `CMAKE_BUILD_TYPE` and provides a default [src/cmake/NvNmosCommon.cmake:46-64]():

- **Default**: `Debug` if not specified
- **Allowed Values**: `Debug`, `Release`, `RelWithDebInfo`, `MinSizeRel` (case-insensitive)
- **Fatal Error**: Triggered for any other value

**Build Safeguards**

Additional build safety checks [src/cmake/NvNmosCommon.cmake:52-54]():
- **Warning**: In-source builds are discouraged but not fatal
- Build directory should be separate from source directory

**Sources:** [src/CMakeLists.txt:80-100](), [src/cmake/NvNmosCommon.cmake:46-64]()

---

## Target Export Configuration

The build system exports CMake targets for consumption by downstream projects via the modern config-file package mechanism.

**Export Workflow**

```mermaid
flowchart TB
    subgraph "Build-Time Configuration"
        TARGETS["NVNMOS_TARGETS list<br/>nvnmos, nvnmos-example"]
        EXPORT_CMD["install(TARGETS ... EXPORT nvnmos-targets)"]
    end
    
    subgraph "Installation"
        INSTALL_TARGETS["install(EXPORT nvnmos-targets)"]
        TARGETS_FILE["lib/cmake/nvnmos/<br/>nvnmos-targets.cmake"]
        
        CONFIG_TEMPLATE["cmake/nvnmos-config.cmake.in"]
        CONFIGURE_PKG["configure_package_config_file()"]
        CONFIG_FILE["lib/cmake/nvnmos/<br/>nvnmos-config.cmake"]
    end
    
    subgraph "Consumer Project"
        FIND["find_package(nvnmos REQUIRED)"]
        USE_TARGET["target_link_libraries(app<br/>PRIVATE nvnmos::nvnmos)"]
    end
    
    TARGETS --> EXPORT_CMD
    EXPORT_CMD --> INSTALL_TARGETS
    INSTALL_TARGETS --> TARGETS_FILE
    
    CONFIG_TEMPLATE --> CONFIGURE_PKG
    CONFIGURE_PKG --> CONFIG_FILE
    
    TARGETS_FILE --> FIND
    CONFIG_FILE --> FIND
    FIND --> USE_TARGET
```

**Installation Specification** [src/cmake/NvNmosExports.cmake:18-29]():

- Targets are installed to platform-specific directories (`NVNMOS_INSTALL_LIBDIR`, `NVNMOS_INSTALL_BINDIR`)
- Export name: `nvnmos-targets`
- Target namespace: `nvnmos::`
- CMake package location: `${CMAKE_INSTALL_LIBDIR}/cmake/nvnmos`

**Generated Files**:

- `nvnmos-targets.cmake`: Contains imported target definitions with full paths
- `nvnmos-config.cmake`: Package configuration file for `find_package()` [src/cmake/NvNmosExports.cmake:31-38]()

**Sources:** [src/cmake/NvNmosExports.cmake:16-39]()

---

## Integration with CI/CD

The build system integrates with GitHub Actions for continuous integration. The CI pipeline executes the build on multiple platforms (Ubuntu, Windows) and configurations (Release). Build artifacts are validated, and the system ensures reproducible builds via locked Conan dependencies.

For detailed CI/CD workflow information, see [CI/CD Pipeline](#8.1).

**Sources:** [src/CMakeLists.txt:1-145]()

---

