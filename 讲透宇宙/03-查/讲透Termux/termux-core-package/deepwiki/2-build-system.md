<!-- source: DeepWiki mcp.deepwiki.com · repo termux/termux-core-package · page 2 Build System · fetched 2026-10-26 -->

# Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [Makefile](Makefile)
- [licenses/termux__termux-core-package__MIT.md](licenses/termux__termux-core-package__MIT.md)
- [packaging/debian/termux-core-package.json.in](packaging/debian/termux-core-package.json.in)

</details>



## Purpose and Scope

This document describes the build system used by the termux-core-package repository. It explains the build process, configuration mechanisms, compilation parameters, installation procedures, and package generation. The build system uses GNU Make as its foundation and provides a comprehensive set of targets for building, testing, installing, and packaging the termux-core components.

For information about the testing framework that integrates with this build system, see [Testing Framework](#5).

## Build System Overview

The termux-core-package build system is designed to compile, test, and package various components including C and C++ libraries, shell scripts, and test utilities. It supports both on-device builds and cross-compilation.

### Build System Architecture

```mermaid
graph TD
    subgraph "Build Process"
        A["make all"] --> B["pre-build"]
        B --> C["build-termux-core-main-app"]
        B --> D["build-libtermux-core_nos_c_tre"]
        B --> E["build-libtermux-core_nos_cxx_tre"]
        C --> F["Generate Debian Packaging"]
        D --> F
        E --> F
    end

    subgraph "Additional Targets"
        G["make clean"] --> H["Remove build outputs"]
        I["make install"] --> J["Install to prefix"]
        K["make test"] --> L["Run tests"]
        M["make packaging-debian-build"] --> N["Create .deb package"]
    end

    subgraph "Build Outputs"
        C --> O["Scripts in bin/"]
        D --> P["C library (.so/.a)"]
        E --> Q["C++ library (.so/.a)"]
        D --> R["Header files"]
        E --> R
        C --> S["Test scripts"]
        D --> T["Test binaries"]
    end
```

Sources: [Makefile:298-517]()

### Build Directory Structure

```mermaid
graph TD
    subgraph "Build Directories"
        A["build/"] --> B["build/output/"]
        B --> C["build/output/usr/"]
        C --> D["build/output/usr/bin/"]
        C --> E["build/output/usr/lib/"]
        C --> F["build/output/usr/libexec/"]
        F --> G["build/output/usr/libexec/installed-tests/termux-core/"]
        B --> H["build/output/tmp/"]
        B --> I["build/output/packaging/"]
        I --> J["build/output/packaging/debian/"]
    end
    
    subgraph "Installation Directories"
        K["PREFIX/"] --> L["PREFIX/bin/"]
        K --> M["PREFIX/include/"]
        M --> N["PREFIX/include/termux-core/"]
        K --> O["PREFIX/lib/"]
        K --> P["PREFIX/libexec/"]
        P --> Q["PREFIX/libexec/installed-tests/termux-core/"]
    end
```

Sources: [Makefile:94-108](), [Makefile:111-123]()

## Configuration and Environment Variables

The build system defines numerous environment variables to configure paths, package names, version numbers, and architecture-specific settings. These variables are used throughout the build process to ensure consistency.

### Key Configuration Variables

```mermaid
graph TD
    subgraph "Version and Architecture"
        A1["TERMUX_CORE_PKG__VERSION"] --> A2["Package version"]
        B1["TERMUX_CORE_PKG__ARCH"] --> B2["Target architecture"]
    end
    
    subgraph "Installation Paths"
        C1["TERMUX__PREFIX"] --> C2["Default installation prefix"]
        D1["TERMUX_CORE_PKG__INSTALL_PREFIX"] --> D2["Custom installation prefix"]
        D2 -->|"Fallback"| C2
    end
    
    subgraph "Termux Paths"
        E1["TERMUX_APP__DATA_DIR"] --> E2["App data directory"]
        F1["TERMUX__ROOTFS"] --> F2["Root filesystem"]
        G1["TERMUX__HOME"] --> G2["Home directory"]
    end
    
    subgraph "Environment Variable Prefixes"
        H1["TERMUX_ENV__S_ROOT"] --> H2["TERMUX_"]
        I1["TERMUX_ENV__S_TERMUX"] --> I2["TERMUX__"]
        J1["TERMUX_ENV__S_TERMUX_APP"] --> J2["TERMUX_APP__"]
    end
```

Sources: [Makefile:1-44]()

### Architecture Detection

The build system can automatically detect the target architecture if not specified. It examines predefined macros from the C compiler to determine whether the target is:

- i686
- x86_64
- aarch64
- arm
- riscv64

This allows the build to adapt to different architectures without manual configuration.

Sources: [Makefile:66-88]()

## Compilation Process

### Compiler Flags and Optimization

The build system sets up compiler flags for both C and C++ compilation:

| Flag Category | Purpose | Example Flags |
|---------------|---------|---------------|
| Default Flags | Platform compatibility | `-march=armv7-a` (for ARM) |
| Optimization | Performance | `-O2` |
| Hardening | Security | `-D_FORTIFY_SOURCE=2`, `-fstack-protector-strong` |
| Warning Control | Code quality | `-Wall`, `-Wextra`, `-Werror`, `-Wshadow` |
| Linking | Library handling | `-Wl,--as-needed`, `-Wl,--enable-new-dtags` |
| Sanitization (tests) | Bug detection | `-fsanitize=address` |

For architecture-specific compilation, specialized flags are used. For example, ARM builds use `-march=armv7-a -mfpu=neon -mfloat-abi=softfp -mthumb`.

Sources: [Makefile:180-228]()

### Library Compilation Process

The build system compiles two main libraries:

1. **libtermux-core_nos_c_tre**: A C library providing core functionality
2. **libtermux-core_nos_cxx_tre**: A C++ library that wraps the C library

For each library, both shared (`.so`) and static (`.a`) versions are created. The compilation process involves:

1. Compiling individual source files to object files
2. Linking object files into shared libraries
3. Creating static archives

The libraries are built with visibility controls to carefully manage the exported symbols, using `-fvisibility=hidden` by default and explicitly marking exported functions with `-fvisibility=default`.

```mermaid
flowchart TD
    subgraph "C Library Build"
        A1["C Source Files"] --> B1["Compile to Object Files"]
        B1 --> C1["Link Shared Library\nlibtermux-core_nos_c_tre.so"]
        B1 --> D1["Create Static Library\nlibtermux-core_nos_c_tre.a"]
    end
    
    subgraph "C++ Library Build"
        A2["C++ Source Files"] --> B2["Compile to Object Files"]
        B2 --> C2["Link Shared Library\nlibtermux-core_nos_cxx_tre.so"]
        B2 --> D2["Create Static Library\nlibtermux-core_nos_cxx_tre.a"]
        C1 --> C2
    end
    
    subgraph "Test Binaries"
        C1 --> E1["Compile Test Binaries"]
        E1 --> F1["Standard Test Binary"]
        E1 --> G1["Sanitizer-enabled Test Binary"]
    end
```

Sources: [Makefile:232-421]()

## Build Targets

The build system provides several primary targets for different operations:

| Target | Description |
|--------|-------------|
| `all` | Builds all components and packaging |
| `pre-build` | Prepares build directories and runs clean |
| `build-termux-core-main-app` | Builds main application scripts and tests |
| `build-libtermux-core_nos_c_tre` | Builds the C library |
| `build-libtermux-core_nos_cxx_tre` | Builds the C++ library |
| `clean` | Removes build outputs |
| `install` | Installs built components to the target prefix |
| `uninstall` | Removes installed components |
| `packaging-debian-build` | Creates a Debian package |
| `test` | Runs all tests |
| `test-unit` | Runs unit tests only |
| `test-runtime` | Runs runtime tests only |

These targets are defined as phony targets in the Makefile to ensure they run regardless of file timestamps.

Sources: [Makefile:298-516]()

## Installation Process

The installation process copies built components to their destination directories under the specified prefix (`TERMUX_CORE_PKG__INSTALL_PREFIX`):

### Installed Components

```mermaid
graph TD
    subgraph "Installation"
        A["make install"] --> B["Create Directories"]
        B --> C["Install Binaries"]
        B --> D["Install Headers"]
        B --> E["Install Libraries"]
        B --> F["Install Tests"]
        
        C --> C1["PREFIX/bin/"]
        D --> D1["PREFIX/include/termux-core/"]
        E --> E1["PREFIX/lib/"]
        F --> F1["PREFIX/libexec/installed-tests/termux-core/"]
    end
    
    subgraph "File Types"
        C1 --> G["Scripts and Executables"]
        D1 --> H["C and C++ Headers"]
        E1 --> I["Shared Libraries (.so)"]
        E1 --> J["Static Libraries (.a)"]
        F1 --> K["Test Scripts and Binaries"]
    end
```

The installation process also sets appropriate permissions for installed files:
- Executable files (700): Binaries, scripts, test runners
- Non-executable files (600): Headers

Sources: [Makefile:428-458]()

## Packaging System

The build system can generate Debian packages for distribution. This is done through the `packaging-debian-build` target.

### Debian Package Generation

```mermaid
flowchart TD
    A["make all"] --> B["Build Components"]
    B --> C["Generate Debian Control Files"]
    C --> D["termux-create-package"]
    D --> E[".deb Package"]
    
    subgraph "Debian Package Contents"
        F["Control Files"] --> G["Package Metadata"]
        H["Data Files"] --> I["Binaries, Libraries, Headers"]
    end
```

The packaging process:
1. Uses templates in `packaging/debian/` directory
2. Substitutes variables in these templates
3. Creates package control files (metadata)
4. Packages built components (binaries, libraries, headers)
5. Runs `termux-create-package` to generate the final .deb file

Sources: [Makefile:480-484](), [packaging/debian/termux-core-package.json.in:1-22]()

## Testing Integration

The build system integrates with the testing framework to validate built components:

### Test Execution Process

```mermaid
flowchart TD
    A["make test"] --> B["make install to temporary location"]
    B --> C["Run termux-core-tests"]
    C --> D["Test Results"]
    
    subgraph "Test Types"
        E["Unit Tests"] --> F["Test individual components"]
        G["Runtime Tests"] --> H["Test system integration"]
    end
    
    subgraph "Test Options"
        I["--tests-path"] --> J["Location of test files"]
        K["--only-termux-core-tests"] --> L["Restrict to core tests"]
        M["-vvv"] --> N["Verbosity level"]
    end
```

The build system provides three test-related targets:
- `test`: Runs all tests
- `test-unit`: Runs only unit tests
- `test-runtime`: Runs only runtime tests

Tests are executed via the `termux-core-tests` script with appropriate parameters.

Sources: [Makefile:486-513]()

## License Information

The termux-core-package, including its build system, is released under the MIT License unless specified otherwise for specific files.

Sources: [LICENSE:1-11](), [licenses/termux__termux-core-package__MIT.md:1-24]()

---

