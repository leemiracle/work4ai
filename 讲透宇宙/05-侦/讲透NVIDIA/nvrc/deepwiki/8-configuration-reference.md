<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvrc · page 8 Configuration Reference · fetched 2026-10-26 -->

# Configuration Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Cargo.lock](Cargo.lock)
- [Cargo.toml](Cargo.toml)
- [src/coreutils.rs](src/coreutils.rs)

</details>



This document provides comprehensive reference documentation for NVRC project configuration files, dependency specifications, and low-level utility modules. It covers the build configuration defined in `Cargo.toml`, the locked dependency tree in `Cargo.lock`, and core system utility functions used throughout the codebase.

For information about system initialization and runtime configuration processing, see [Configuration Processing](#3.2). For details about the development build pipeline and testing configuration, see [Development and CI/CD](#7).

## Project Configuration

The NVRC project is configured as a Rust binary package with specialized dependencies for low-level system operations and GPU management.

### Package Metadata

| Property | Value | Purpose |
|----------|-------|---------|
| `name` | `NVRC` | Binary package identifier |
| `version` | `0.1.0` | Current release version |
| `edition` | `2021` | Rust language edition |

### Feature Flags

```mermaid
graph TD
    Package["NVRC Package"]
    Default["Default Build"]
    Confidential["confidential Feature"]
    
    Package --> Default
    Package --> Confidential
    
    Confidential --> CCMode["query_cc_mode.rs functionality"]
    Default --> CoreOps["Core GPU operations"]
```

The project defines a single feature flag:

- **`confidential`**: Enables confidential computing support for GPU architectures that support hardware-based confidentiality modes

Sources: [Cargo.toml:30-31]()

### Release Profile Optimization

The release build profile is optimized for minimal binary size and maximum security:

```mermaid
graph LR
    ReleaseProfile["Release Profile"]
    OptLevel["opt-level = 's'"]
    LTO["lto = true"]
    Strip["strip = true"] 
    Panic["panic = 'abort'"]
    
    ReleaseProfile --> OptLevel
    ReleaseProfile --> LTO
    ReleaseProfile --> Strip
    ReleaseProfile --> Panic
    
    OptLevel --> SizeOpt["Size optimization"]
    LTO --> LinkOpt["Link-time optimization"]
    Strip --> BinaryOpt["Debug symbol removal"]
    Panic --> SecurityOpt["Abort on panic"]
```

Sources: [Cargo.toml:19-23]()

## Runtime Dependencies

The project's runtime dependencies provide system-level functionality required for GPU management and container integration.

### Core System Dependencies

| Crate | Version | Features | Purpose |
|-------|---------|----------|---------|
| `anyhow` | 1.0.44 | - | Error handling and context |
| `nix` | 0.30.1 | `fs`, `mount`, `user`, `process`, `reboot`, `signal`, `mman`, `poll` | Unix system calls |
| `libc` | 0.2 | - | C library bindings |
| `log` | 0.4 | - | Logging framework |
| `kernlog` | 0.3 | - | Kernel message logging |

### Device and Network Communication

| Crate | Version | Purpose |
|-------|---------|---------|
| `kobject-uevent` | 0.2.0 | Device hotplug event monitoring |
| `netlink-sys` | 0.8.6 | Netlink socket communication |
| `sysinfo` | 0.36.1 | System information queries |

### Utility Dependencies

| Crate | Version | Purpose |
|-------|---------|---------|
| `lazy_static` | 1.4.0 | Static variable initialization |
| `rand` | 0.9.0 | Random number generation |
| `rlimit` | 0.10.2 | Resource limit management |

Sources: [Cargo.toml:6-17]()

### Development Dependencies

Test-specific dependencies used for development and CI:

| Crate | Version | Purpose |
|-------|---------|---------|
| `mktemp` | 0.5.1 | Temporary directory creation |
| `tempfile` | 3.2.0 | Temporary file management |
| `serial_test` | 3.2.0 | Sequential test execution |

Sources: [Cargo.toml:25-28]()

## Dependency Resolution Tree

The complete dependency graph shows how system-level crates interconnect:

```mermaid
graph TD
    NVRC["NVRC v0.1.0"]
    
    subgraph "Error Handling"
        anyhow["anyhow v1.0.95"]
    end
    
    subgraph "System Interface"
        nix["nix v0.30.1"]
        libc["libc v0.2.174"]
        kernlog["kernlog v0.3.1"]
        rlimit["rlimit v0.10.2"]
        sysinfo["sysinfo v0.36.1"]
    end
    
    subgraph "Device Communication"
        kobject["kobject-uevent v0.2.0"]
        netlink["netlink-sys v0.8.7"]
    end
    
    subgraph "Utilities"
        lazy_static["lazy_static v1.5.0"]
        rand["rand v0.9.0"]
        log["log v0.4.25"]
    end
    
    subgraph "Testing"
        mktemp["mktemp v0.5.1"]
        tempfile["tempfile v3.16.0"]
        serial_test["serial_test v3.2.0"]
    end
    
    NVRC --> anyhow
    NVRC --> nix
    NVRC --> libc
    NVRC --> kernlog
    NVRC --> kobject
    NVRC --> netlink
    NVRC --> lazy_static
    NVRC --> rand
    NVRC --> rlimit
    NVRC --> sysinfo
    NVRC --> log
    NVRC --> mktemp
    NVRC --> tempfile
    NVRC --> serial_test
    
    nix --> libc
    kernlog --> libc
    kernlog --> log
    rlimit --> libc
    netlink --> libc
    netlink --> log
```

Sources: [Cargo.lock:1-836]()

## Core Utility Modules

The `coreutils` module provides essential system-level operations used throughout NVRC for device management and filesystem setup.

### Filesystem Operations

```mermaid
graph LR
    coreutils["src/coreutils.rs"]
    
    ln_func["ln()"]
    mknod_func["mknod()"]
    
    coreutils --> ln_func
    coreutils --> mknod_func
    
    ln_func --> symlinkat["nix::unistd::symlinkat"]
    mknod_func --> stat_mknod["nix::sys::stat::mknod"]
    mknod_func --> makedev["nix::sys::stat::makedev"]
    
    ln_func --> LinkCreation["Symbolic link creation"]
    mknod_func --> DeviceCreation["Device node creation"]
```

### Function Specifications

#### `ln(target: &str, linkpath: &str) -> Result<()>`

Creates symbolic links for device nodes and configuration files:

- **Parameters**: 
  - `target`: Path to link target
  - `linkpath`: Path where link will be created
- **Implementation**: Uses `nix::unistd::symlinkat` with `AT_FDCWD`
- **Error Handling**: Returns contextualized error on failure

#### `mknod(path: &str, kind: SFlag, major: u64, minor: u64) -> Result<()>`

Creates device nodes with proper permissions and device numbers:

- **Parameters**:
  - `path`: Device node path
  - `kind`: Device type (`SFlag`)
  - `major`: Major device number
  - `minor`: Minor device number
- **Behavior**: Skips creation if device already exists
- **Permissions**: Sets mode `0o666` for device access
- **Implementation**: Uses `nix::sys::stat::mknod` and `makedev`

### Integration with System Components

```mermaid
graph TD
    DeviceSetup["Device Setup Operations"]
    
    GetDevices["get_devices.rs"]
    Mount["mount.rs"]
    ContainerTK["container_toolkit.rs"]
    
    DeviceSetup --> ln_usage["ln() for device links"]
    DeviceSetup --> mknod_usage["mknod() for device nodes"]
    
    GetDevices --> DeviceSetup
    Mount --> DeviceSetup  
    ContainerTK --> DeviceSetup
    
    ln_usage --> GPULinks["GPU device symlinks"]
    mknod_usage --> DeviceNodes["Device file creation"]
```

Sources: [src/coreutils.rs:1-26]()

The utility functions in `coreutils.rs` serve as foundational building blocks for device management operations throughout the NVRC system, providing safe wrappers around low-level Unix system calls with proper error handling and logging integration.

---

