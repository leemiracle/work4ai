<!-- source: DeepWiki mcp.deepwiki.com · repo termux/termux-core-package · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [README.md](README.md)
- [packaging/debian/termux-core-package.json.in](packaging/debian/termux-core-package.json.in)
- [site/pages/en/projects/releases/0/v0.3.0.md](site/pages/en/projects/releases/0/v0.3.0.md)
- [site/pages/en/projects/releases/index.md](site/pages/en/projects/releases/index.md)

</details>



## Purpose and Scope

Termux Core Package (`termux-core-package`) provides essential utilities and libraries for the Termux core functionality. This package contains components that must exist in all Termux execution environments, including forks, and serves as a foundation for other Termux packages and third-party applications. The current version is 0.3.0.

This document provides a high-level overview of the termux-core-package architecture, its core components, and how they interact with each other. For detailed information about the build system, see [Build System](#2). For core libraries documentation, see [Core Libraries](#3).

Sources: [README.md:1-3](), [Makefile:1]()

## System Architecture

The termux-core-package is organized into several key components that work together to provide core functionality.

```mermaid
graph TD
    subgraph "termux-core-package"
        CoreLibs["Core Libraries"]
        Utils["Utilities"]
        Tests["Testing Framework"]
        Build["Build System"]
    end
    
    subgraph "External Systems"
        TermuxApp["Termux App"]
        TermuxPlugins["Termux Plugins"]
        TermuxForks["Termux Forks"]
        ThirdParty["Third-Party Apps"]
    end
    
    CoreLibs -- "provides APIs" --> Utils
    CoreLibs -- "validated by" --> Tests
    Utils -- "validated by" --> Tests
    Build -- "compiles" --> CoreLibs
    Build -- "compiles" --> Utils
    Build -- "runs" --> Tests
    
    CoreLibs -- "used by" --> TermuxApp
    CoreLibs -- "used by" --> TermuxPlugins
    CoreLibs -- "used by" --> TermuxForks
    CoreLibs -- "used by" --> ThirdParty
    
    Utils -- "used by" --> TermuxApp
    Utils -- "used by" --> TermuxPlugins
    Utils -- "used by" --> TermuxForks
    Utils -- "used by" --> ThirdParty
```

Sources: [Makefile:181-227](), [README.md:1-3]()

## Core Libraries

The termux-core-package provides two primary libraries that form the foundation of its functionality:

### libtermux-core_nos_c_tre (C Library)

This library contains core C utilities for file operations, process management, and shell environments. Key components include:

- `UnixFileUtils`: Handles file system operations and path manipulation
- `UnixForkUtils`: Manages process creation and child process handling
- `UnixShellEnvironment`: Provides shell environment interaction utilities
- `TermuxFile`: Termux-specific file operations

### libtermux-core_nos_cxx_tre (C++ Library)

This library provides C++ wrappers around the C library components.

```mermaid
graph TD
    subgraph "C Library (libtermux-core_nos_c_tre)"
        UnixFile["UnixFileUtils"]
        UnixFork["UnixForkUtils"]
        UnixShell["UnixShellEnvironment"]
        TermuxFile["TermuxFile"]
        FileLogger["FileLoggerImpl"]
        StdLogger["StandardLoggerImpl"]
        Logger["Logger"]
        DataUtils["DataUtils"]
        AssertUtils["AssertUtils"]
        SecurityUtils["SecurityUtils"]
        SeLinuxUtils["UnixSeLinuxUtils"]
        SignalUtils["UnixSignalUtils"]
        SafeStrerror["UnixSafeStrerror"]
    end
    
    subgraph "C++ Library (libtermux-core_nos_cxx_tre)"
        CXXWrappers["C++ Wrappers"]
    end
    
    UnixFile --> TermuxFile
    Logger --> FileLogger
    Logger --> StdLogger
    
    CXXWrappers -- "wraps" --> UnixFile
    CXXWrappers -- "wraps" --> UnixFork
    CXXWrappers -- "wraps" --> UnixShell
    
    UnixFork -- "uses" --> SignalUtils
    UnixFork -- "uses" --> SafeStrerror
    SecurityUtils -- "uses" --> SeLinuxUtils
    
    subgraph "API Usage"
        Apps["Applications"]
        Scripts["Shell Scripts"]
    end
    
    Apps -- "use" --> CXXWrappers
    Apps -- "use" --> UnixFile
    Apps -- "use" --> UnixFork
    Apps -- "use" --> UnixShell
    Apps -- "use" --> TermuxFile
    
    Scripts -- "use" --> UnixFile
    Scripts -- "use" --> UnixFork
    Scripts -- "use" --> UnixShell
    Scripts -- "use" --> TermuxFile
```

Sources: [Makefile:232-249](), [Makefile:259-264]()

## Environment Variable Utilities

Termux Core Package includes a system for managing environment variables, which is critical for application integration and context-aware operations.

```mermaid
graph TD
    subgraph "Environment Variable Management"
        TSEV["termux-scoped-env-variable"]
        TAIEV["termux-apps-info-env-variable"]
        TAAVN["termux-apps-info-app-version-name"]
    end
    
    subgraph "Implementation Types"
        Bash["Bash Implementation"]
        POSIX["POSIX Shell Implementation"]
    end
    
    subgraph "Primary Operations"
        GetName["get-name"]
        GetValue["get-value"]
        SetValue["set-value"]
        UnsetValue["unset-value"]
        SourceEnv["source-env"]
    end
    
    TSEV --> Bash
    TSEV --> POSIX
    TAIEV --> Bash
    TAIEV --> POSIX
    TAAVN --> Bash
    TAAVN --> POSIX
    
    TAIEV -- "depends on" --> TSEV
    TAAVN -- "depends on" --> TAIEV
    
    Bash -- "implements" --> GetName
    Bash -- "implements" --> GetValue
    Bash -- "implements" --> SetValue
    Bash -- "implements" --> UnsetValue
    Bash -- "implements" --> SourceEnv
    
    POSIX -- "implements" --> GetName
    POSIX -- "implements" --> GetValue
    POSIX -- "implements" --> SetValue
    POSIX -- "implements" --> UnsetValue
    POSIX -- "implements" --> SourceEnv
    
    subgraph "Environment Variables"
        TERMUX_ENV["TERMUX_ENV__S_ROOT"]
        APP_ENV["TERMUX_APP__*"]
        PLUGIN_ENV["TERMUX_*_APP__*"]
        EXTERNAL_ENV["*_APP__*"]
    end
    
    TSEV -- "manages" --> TERMUX_ENV
    TSEV -- "manages" --> APP_ENV
    TSEV -- "manages" --> PLUGIN_ENV
    TSEV -- "manages" --> EXTERNAL_ENV
```

Sources: [Makefile:23-37](), [Makefile:322-328]()

## Build System

The package uses a well-structured build system to compile, test, and package its components. The build system handles architecture detection, environment setup, and ensures proper compilation flags are used.

### Key Build Targets

| Target | Description |
|--------|-------------|
| `all` | Builds all components |
| `pre-build` | Prepares build environment |
| `build-termux-core-main-app` | Builds the main application scripts |
| `build-libtermux-core_nos_c_tre` | Builds the C library |
| `build-libtermux-core_nos_cxx_tre` | Builds the C++ library |
| `clean` | Removes build artifacts |
| `install` | Installs the package into the specified prefix |
| `uninstall` | Uninstalls the package |
| `packaging-debian-build` | Creates a Debian package |
| `test` | Runs all tests |
| `test-unit` | Runs unit tests only |
| `test-runtime` | Runs runtime tests only |

Sources: [Makefile:299-513]()

## Testing Framework

The package includes a comprehensive testing framework for ensuring functionality and reliability.

```mermaid
graph TD
    subgraph "Testing Framework"
        TCT["termux-core-tests"]
        RunTime["Runtime Tests"]
        UnitTests["Unit Tests"]
    end
    
    subgraph "Test Types"
        CoreTests["Core Tests"]
        ExternalTests["External Package Tests"]
        AppTests["App Tests"]
    end
    
    subgraph "Testing Features"
        Sanitizer["AddressSanitizer"]
        Leak["LeakSanitizer"]
        LogLevel["Log Levels"]
        Filter["Test Filters"]
    end
    
    TCT -- "runs" --> RunTime
    TCT -- "runs" --> UnitTests
    
    RunTime -- "includes" --> CoreTests
    RunTime -- "includes" --> ExternalTests
    RunTime -- "includes" --> AppTests
    UnitTests -- "includes" --> CoreTests
    
    TCT -- "uses" --> Sanitizer
    Sanitizer -- "includes" --> Leak
    TCT -- "supports" --> LogLevel
    TCT -- "supports" --> Filter
    
    subgraph "Test Components"
        ShellCmdEnv["Shell Command Environment Tests"]
        ScopedEnvVar["Scoped Environment Variable Tests"]
        AppInfoEnvVar["App Info Environment Variable Tests"]
        AppVersionName["App Version Name Tests"]
    end
    
    CoreTests -- "contains" --> ShellCmdEnv
    ShellCmdEnv -- "contains" --> ScopedEnvVar
    ShellCmdEnv -- "contains" --> AppInfoEnvVar
    ShellCmdEnv -- "contains" --> AppVersionName
```

The `termux-core-tests` utility serves as the main entry point for running tests, supporting various options for test selection, logging verbosity, and sanitizer usage.

Sources: [Makefile:374-394](), [Makefile:487-512]()

## Installation and Configuration

The termux-core-package installs components into the following directories:

| Component | Installation Path |
|-----------|------------------|
| Binaries | `$(TERMUX__PREFIX)/bin` |
| Headers | `$(TERMUX__PREFIX)/include/termux-core` |
| Libraries | `$(TERMUX__PREFIX)/lib` |
| Tests | `$(TERMUX__PREFIX)/libexec/installed-tests/termux-core` |

The package automatically detects architecture and configures builds accordingly, supporting `aarch64`, `arm`, `i686`, `x86_64`, and `riscv64` architectures.

Sources: [Makefile:66-88](), [Makefile:428-457]()

## Release History

The termux-core-package is currently at version 0.3.0. For detailed release notes and changelogs, see the [Release History](#6) page.

Sources: [site/pages/en/projects/releases/index.md:5-41](), [site/pages/en/projects/releases/0/v0.3.0.md:5-48]()

---

