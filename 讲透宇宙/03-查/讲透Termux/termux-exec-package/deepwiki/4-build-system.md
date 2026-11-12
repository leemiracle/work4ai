<!-- source: DeepWiki mcp.deepwiki.com · repo termux/termux-exec-package · page 4 Build System · fetched 2026-10-26 -->

# Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.clang-tidy](.clang-tidy)
- [.gitignore](.gitignore)
- [Makefile](Makefile)
- [README.md](README.md)
- [app/main/tests/termux-exec-tests.in](app/main/tests/termux-exec-tests.in)

</details>



This page documents the build system for the termux-exec-package, including its directory structure, configuration options, build targets, and architecture support. For information about the overall system architecture and components, see [System Architecture](#3).

The build system uses GNU Make and is designed to support cross-compilation for multiple architectures, different Android versions, and various execution modes necessary for Termux's environment.

## Directory Structure

The build system organizes output files into a predictable directory structure, separating temporary files, libraries, executables, and packaging artifacts.

```mermaid
flowchart TD
    subgraph "Build Directory Structure"
        BD["build/"] --> OD["output/"]
        BD --> ID["install/"]
        
        OD --> TOD["tmp/"]
        OD --> POD["usr/"]
        OD --> PKG["packaging/"]
        
        TOD --> OTMP["Library Objects (.o files)"]
        
        POD --> BIN["bin/"]
        POD --> LIB["lib/"]
        POD --> LIBEXEC["libexec/"]
        
        BIN --> SCRIPTS["Scripts"]
        LIB --> SHAREDLIBS["Shared Libraries (.so)"]
        LIB --> STATICLIBS["Static Libraries (.a)"]
        LIBEXEC --> TESTS["installed-tests/termux-exec/"]
        
        PKG --> DEBIAN["debian/"]
        
        ID --> INSTPRE["usr/"]
    end
```

Sources: [Makefile:63-76](), [Makefile:80-81]()

## Environment Configuration

The build system defines a comprehensive set of environment variables that control build behavior, paths, and constants. These variables ensure consistent building across different environments.

### Main Configuration Variables

| Variable | Purpose | Default Value |
|----------|---------|---------------|
| `TERMUX_EXEC_PKG__VERSION` | Package version | 2.4.0 |
| `TERMUX_EXEC_PKG__ARCH` | Target architecture | Auto-detected |
| `TERMUX_EXEC_PKG__INSTALL_PREFIX` | Installation prefix | `TERMUX__PREFIX` or `$(DESTDIR)$(PREFIX)` |
| `TERMUX__PREFIX` | Termux installation path | `/data/data/com.termux/files/usr` |
| `TERMUX__PREFIX__BIN_DIR` | Bin directory | `$(TERMUX__PREFIX)/bin` |
| `TERMUX__PREFIX__LIB_DIR` | Library directory | `$(TERMUX__PREFIX)/lib` |

Sources: [Makefile:1-31](), [Makefile:83-90]()

### Architecture Detection

The build system automatically detects the target architecture by examining compiler predefined macros:

```mermaid
flowchart TD
    START["Architecture Detection"] --> CHECK{"Is TERMUX_EXEC_PKG__ARCH set?"}
    CHECK -- No --> MACROS["Get compiler predefined macros"]
    MACROS --> ARM64{"{Check for __aarch64__}"}
    MACROS --> ARM{"{Check for __arm__}"}
    MACROS --> X86{"{Check for __i686__}"}
    MACROS --> X64{"{Check for __x86_64__}"}
    MACROS --> RISCV{"{Check for __riscv}"}
    
    ARM64 -- Found --> SETARM64["Set ARCH=aarch64"]
    ARM -- Found --> SETARM["Set ARCH=arm"]
    X86 -- Found --> SETX86["Set ARCH=i686"]
    X64 -- Found --> SETX64["Set ARCH=x86_64"]
    RISCV -- Found --> SETRISCV["Set ARCH=riscv64"]
    
    MACROS -- None match --> ERROR["Error: Unsupported arch"]
    
    CHECK -- Yes --> DONE["Use provided ARCH"]
    
    SETARM64 --> FINISH["Continue build with detected ARCH"]
    SETARM --> FINISH
    SETX86 --> FINISH
    SETX64 --> FINISH
    SETRISCV --> FINISH
    DONE --> FINISH
```

Sources: [Makefile:34-56]()

### Compiler Flag Configuration

The build system sets appropriate compiler flags based on the target architecture and build requirements:

| Architecture | Special Flags |
|--------------|--------------|
| arm | `-march=armv7-a -mfpu=neon -mfloat-abi=softfp -mthumb` |
| i686 | `-march=i686 -msse3 -mstackrealign -mfpmath=sse -fPIC` |
| All | `-Wall -Wextra -Werror -Wshadow -O2 -D_FORTIFY_SOURCE=2 -fstack-protector-strong` |

For sanitizer builds: `-fsanitize=address -fsanitize-recover=address -fno-omit-frame-pointer`

Sources: [Makefile:130-191]()

## Build Targets

The build system defines several make targets that handle different aspects of building the package:

```mermaid
flowchart TD
    ALL["all"] --> PRE["pre-build (clean)"]
    ALL --> LIBTRE["build-libtermux-exec_nos_c_tre"]
    ALL --> DIRECT["build-libtermux-exec-direct-ld-preload"]
    ALL --> LINKER["build-libtermux-exec-linker-ld-preload"]
    ALL --> MAINAPP["build-termux-exec-main-app"]
    ALL --> DEBPKG["packaging/debian/*"]
    
    INSTALL["install"] --> COPY["Copy libs, headers, scripts, tests to target"]
    
    TEST["test"] --> INSTALL
    TEST --> RUNTESTS["Run termux-exec-tests"]
    
    TESTUNIT["test-unit"] --> INSTALL
    TESTUNIT --> RUNUNIT["Run unit tests"]
    
    TESTRUNTIME["test-runtime"] --> INSTALL
    TESTRUNTIME --> RUNRUNTIME["Run runtime tests"]
    
    DEBIANPKG["packaging-debian-build"] --> ALL
    DEBIANPKG --> CREATEPKG["termux-create-package"]
    
    CLEAN["clean"] --> RMOUT["Remove build/output"]
```

Sources: [Makefile:251-265](), [Makefile:446-532]()

## Core Library Build Process

The build system compiles the base libraries that provide the core termux-exec functionality:

```mermaid
flowchart LR
    subgraph "libtermux-exec_nos_c_tre Build"
        SRCFILES["Source Files"] --> OBJFILES["Object Files (.o)"]
        OBJFILES --> SHAREDLIB["libtermux-exec_nos_c_tre.so"]
        OBJFILES --> STATICLIB["libtermux-exec_nos_c_tre.a"]
    end
    
    subgraph "Source Files"
        direction TB
        SRC1["TermuxExecLibraryConfig.c"]
        SRC2["TermuxExecLDPreload.c"]
        SRC3["ExecIntercept.c"]
        SRC4["ExecVariantsIntercept.c"]
        SRC5["TermuxExecProcess.c"]
        SRC6["TermuxExecShellEnvironment.c"]
    end
    
    SRCFILES --- SRC1
    SRCFILES --- SRC2
    SRCFILES --- SRC3
    SRCFILES --- SRC4
    SRCFILES --- SRC5
    SRCFILES --- SRC6
```

Sources: [Makefile:194-202](), [Makefile:289-316]()

## LD_PRELOAD Variants Build

The build system compiles two variants of the LD_PRELOAD library to support different Android versions and execution modes:

```mermaid
flowchart TD
    DIRECT["Direct Execution Variant
    libtermux-exec-direct-ld-preload.so"] --> LDSO["ld-preload symlink
    libtermux-exec-ld-preload.so"]
    
    LINKER["System Linker Execution Variant
    libtermux-exec-linker-ld-preload.so"] -.-> LDSO
    
    LDSO --> COMPAT["Compatibility Symlink
    libtermux-exec.so"]
    
    CORE["Core Library
    libtermux-exec_nos_c_tre.a"] --> DIRECT
    CORE --> LINKER
```

Sources: [Makefile:386-438]()

## Test Build Process

The build system compiles separate test binaries for unit testing and runtime testing:

```mermaid
flowchart LR
    subgraph "Unit Tests"
        UTESTFSANITIZE["libtermux-exec_nos_c_tre_unit-binary-tests-fsanitize"]
        UTESTNO["libtermux-exec_nos_c_tre_unit-binary-tests-nofsanitize"]
    end
    
    subgraph "Runtime Tests"
        RTESTFSANITIZE["libtermux-exec_nos_c_tre_runtime-binary-tests-fsanitize"]
        RTESTNO["libtermux-exec_nos_c_tre_runtime-binary-tests-nofsanitize"]
    end
    
    TESTSRC["Test Source Files"] --> UTESTFSANITIZE
    TESTSRC --> UTESTNO
    TESTSRC --> RTESTFSANITIZE
    TESTSRC --> RTESTNO
    
    CORE["libtermux-exec_nos_c_tre.a"] --> UTESTFSANITIZE
    CORE --> UTESTNO
    CORE --> RTESTFSANITIZE
    CORE --> RTESTNO
```

Sources: [Makefile:323-355](), [Makefile:372-383]()

## Installation Process

The `install` target places built files into the target installation directory:

| Source | Destination |
|--------|-------------|
| `$(BIN_BUILD_OUTPUT_DIR)/*` | `$(TERMUX_EXEC_PKG__INSTALL_PREFIX)/bin/` |
| `lib/termux-exec_nos_c/tre/include/termux/termux_exec__nos__c` | `$(TERMUX_EXEC_PKG__INSTALL_PREFIX)/include/termux-exec/termux/termux_exec__nos__c` |
| `$(LIB_BUILD_OUTPUT_DIR)/libtermux-exec_nos_c_tre.so` | `$(TERMUX_EXEC_PKG__INSTALL_PREFIX)/lib/` |
| `$(LIB_BUILD_OUTPUT_DIR)/libtermux-exec-*.so` | `$(TERMUX_EXEC_PKG__INSTALL_PREFIX)/lib/` |
| `$(TESTS_BUILD_OUTPUT_DIR)/*` | `$(TERMUX_EXEC_PKG__INSTALL_PREFIX)/libexec/installed-tests/termux-exec/` |

Sources: [Makefile:446-475]()

## Debian Packaging

The build system supports creating Debian packages with properly formatted control files:

```mermaid
flowchart LR
    ALL["all target"] --> DEBFILES["Generate debian/* files"]
    DEBFILES --> SUBSTVAR["Replace variables"]
    SUBSTVAR --> SETPERM["Set permissions"]
    ALL --> PACKDEB["packaging-debian-build target"]
    PACKDEB --> CREATE["termux-create-package"]
```

Sources: [Makefile:251-261](), [Makefile:502-503]()

## Testing Framework Integration

The build system integrates with the testing framework through the `test`, `test-unit`, and `test-runtime` targets. Tests are executed using the `termux-exec-tests` script.

```mermaid
flowchart TD
    TEST["test target"] --> INSTALL["install to build/install"]
    TEST --> EXEC["Execute termux-exec-tests"]
    
    UNIT["test-unit target"] --> INSTALL
    UNIT --> EXECUNIT["Execute unit tests"]
    
    RUNTIME["test-runtime target"] --> INSTALL
    RUNTIME --> EXECRUNTIME["Execute runtime tests"]
    
    EXEC --> SCRIPT["termux-exec-tests script"]
    EXECUNIT --> SCRIPT
    EXECRUNTIME --> SCRIPT
    
    SCRIPT --> ARGS["--tests-path, --ld-preload-dir"]
    SCRIPT --> VERB["Verbosity -vvv"]
    SCRIPT --> TYPE["Test type (all, unit, runtime)"]
```

Sources: [Makefile:507-531](), [app/main/tests/termux-exec-tests.in:90-227]()

## Cross-Compilation Support

The build system automatically detects the architecture and applies appropriate compiler flags, making it suitable for cross-compilation. It also distinguishes between on-device builds and cross-compiled builds.

```mermaid
flowchart TD
    START["Build Start"] --> DETECT["Architecture Detection"]
    DETECT --> FLAGS["Apply Architecture-Specific Flags"]
    FLAGS --> DEVICE{"Is On-Device Build?"}
    
    DEVICE -- Yes --> DIRECT["Direct Build"]
    DEVICE -- No --> CROSS["Cross-Compilation"]
    CROSS --> RPATH["Add -Wl,-rpath flag"]
    
    DIRECT --> BUILD["Compile Libraries and Executables"]
    RPATH --> BUILD
```

Sources: [Makefile:34-56](), [Makefile:59](), [Makefile:150-166]()

## Code Style and Quality Tools

The build system includes targets for code formatting and static analysis:

| Tool | Purpose | Command |
|------|---------|---------|
| clang-format | Code formatting | `make format` |
| clang-format (check) | Code style verification | `make check` |
| clang-tidy | Static analysis | `make check` |

Sources: [Makefile:243-542](), [.clang-tidy:1-3]()

---

