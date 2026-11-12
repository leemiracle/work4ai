<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-gpio-status-handler · page 3 Building the Project · fetched 2026-10-26 -->

# Building the Project

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [meson.build](meson.build)
- [meson_options.txt](meson_options.txt)

</details>



This page provides comprehensive guidance on compiling the `nvidia-gpio-status-handler` daemon from source using the Meson build system. It covers the build process overview, dependency management, compilation options, and the steps required to produce executable binaries for different deployment targets.

For detailed build system internals, see [Build System Overview](#3.1). For dependency documentation, see [Dependencies](#3.2). For configuration options, see [Build Options](#3.3). For step-by-step compilation instructions, see [Compilation Guide](#3.4).

## Build Process Overview

The `nvidia-gpio-status-handler` project uses the **Meson build system** with **Ninja** as the backend. The build is defined in [meson.build:1-106]() and produces a single executable named `gpio-status-handlerd`.

The build process follows this general workflow:

```mermaid
graph LR
    A["Source Files<br/>*.cpp"] --> B["meson builddir"]
    C["meson.build"] --> B
    D["meson_options.txt"] --> B
    B --> E["Build Configuration<br/>builddir/"]
    E --> F["ninja -C builddir"]
    F --> G["gpio-status-handlerd<br/>executable"]
    G --> H["ninja -C builddir install"]
    H --> I["/usr/bin/gpio-status-handlerd"]
    
    style B fill:#f9f9f9
    style F fill:#f9f9f9
    style H fill:#f9f9f9
```

**Sources:** [meson.build:1-106](), [README.md:22-28]()

## Build System Components

The build system consists of the following key files:

| File | Purpose | Key Content |
|------|---------|-------------|
| `meson.build` | Main build definition | Project metadata, dependencies, compilation rules |
| `meson_options.txt` | Configurable build options | `debug_log`, `sandbox_mode`, `log_elapsed_time` |
| `subprojects/` | Fallback dependencies | `sdbusplus.wrap`, `phosphor-logging.wrap` |

The project requires C++23 standard ([meson.build:7-8](), [meson.build:26-28]()) and enforces this requirement during configuration.

**Sources:** [meson.build:1-8](), [meson.build:26-28](), [meson_options.txt:1-21]()

## Compilation Targets

The build produces a single executable with different configurations depending on build options:

```mermaid
graph TD
    SRC["Source Files<br/>gpio_status_handler.cpp<br/>gpio_chips.cpp<br/>gpio_lines.cpp<br/>gpio_json_config.cpp<br/>gpio_utils.cpp"]
    
    SRC --> COMPILE["Compilation Process"]
    
    OPTS["Build Options<br/>-Ddebug_log<br/>-Dsandbox_mode<br/>-Dapi_stubs<br/>-Dlog_elapsed_time"]
    
    OPTS --> COMPILE
    
    DEPS["Dependencies<br/>sdbusplus<br/>libgpiod<br/>phosphor-logging<br/>threads<br/>systemd"]
    
    DEPS --> COMPILE
    
    COMPILE --> EXE["gpio-status-handlerd"]
    
    EXE --> DEV["Development Binary<br/>x86-64 host<br/>-Dsandbox_mode=enabled<br/>-Dapi_stubs=enabled<br/>-Ddebug_log=3"]
    
    EXE --> PROD["Production Binary<br/>ARM BMC target<br/>Real hardware APIs<br/>-Ddebug_log=1"]
```

**Sources:** [meson.build:94-105](), [README.md:34-38]()

## Build Configuration

Build behavior is controlled through three mechanisms:

### 1. Project Metadata
Defined in [meson.build:1-8]():
- **Project name:** `c++ nvidia-gpio-status-handler`
- **Language:** C++ (cpp)
- **Version:** 0.1
- **License:** MIT
- **Meson version requirement:** ≥1.1.1
- **C++ standard:** C++23

### 2. Compile-Time Options
Defined in [meson_options.txt:1-21]():

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `debug_log` | integer (0-4) | 0 | Default logging verbosity level |
| `sandbox_mode` | feature | auto | Enable host development mode |
| `log_elapsed_time` | feature | disabled | Enable performance instrumentation |

These options are processed in [meson.build:30-44]() and converted to preprocessor definitions.

### 3. Compiler Arguments
Global and project-specific arguments are set in [meson.build:22-44]():

```mermaid
graph TD
    OPT_DEBUG["debug_log option<br/>meson_options.txt:2-8"]
    OPT_SANDBOX["sandbox_mode option<br/>meson_options.txt:10-14"]
    OPT_TIME["log_elapsed_time option<br/>meson_options.txt:16-20"]
    
    OPT_DEBUG --> |"if != 0"| ARG_DEBUG["-DDEF_DBG_LEVEL=X<br/>meson.build:33-36"]
    OPT_SANDBOX --> |"if enabled"| ARG_SANDBOX["-DSANDBOX_MODE<br/>meson.build:38-40"]
    OPT_TIME --> |"if enabled"| ARG_TIME["-DLOG_ELAPSED_TIME<br/>meson.build:42-44"]
    
    ARG_DEBUG --> COMPILER["C++ Compiler"]
    ARG_SANDBOX --> COMPILER
    ARG_TIME --> COMPILER
    
    GLOBAL["-DSOME_TOKEN=value<br/>meson.build:23"] --> COMPILER
```

**Sources:** [meson.build:22-44](), [meson_options.txt:1-21]()

## Dependency Resolution

The build system uses a sophisticated dependency resolution mechanism that supports both system-installed libraries and fallback subprojects:

```mermaid
graph TD
    START["Build Process"] --> CHECK_SDBUS["Check for sdbusplus<br/>meson.build:64"]
    
    CHECK_SDBUS --> |"found"| SYSTEM_SDBUS["Use system sdbusplus"]
    CHECK_SDBUS --> |"not found"| SUBPROJ_SDBUS["Build from subproject<br/>meson.build:67"]
    
    SUBPROJ_SDBUS --> GET_VAR["Get sdbusplus_dep<br/>meson.build:70"]
    
    START --> CHECK_PLOG["Check for phosphor-logging<br/>meson.build:84-87"]
    CHECK_PLOG --> |"not found"| FALLBACK_PLOG["Use fallback subproject"]
    CHECK_PLOG --> |"found"| SYSTEM_PLOG["Use system phosphor-logging"]
    
    START --> CHECK_GPIO["Check for libgpiod<br/>meson.build:91"]
    CHECK_GPIO --> GPIO_DEP["gpio_device dependency"]
    
    START --> CHECK_THREADS["Check for threads<br/>meson.build:92"]
    CHECK_THREADS --> THREADS_DEP["threads dependency"]
    
    START --> CHECK_SYSTEMD["Check for systemd<br/>meson.build:62"]
    CHECK_SYSTEMD --> SYSTEMD_DEP["systemd_dep dependency"]
    
    SYSTEM_SDBUS --> LINK["Link executable<br/>meson.build:94-105"]
    GET_VAR --> LINK
    SYSTEM_PLOG --> LINK
    FALLBACK_PLOG --> LINK
    GPIO_DEP --> LINK
    THREADS_DEP --> LINK
    SYSTEMD_DEP --> LINK
```

**Sources:** [meson.build:62-92]()

## Executable Definition

The final executable is defined in [meson.build:94-105]():

```mermaid
graph LR
    subgraph "Source Files"
        SRC1["gpio_status_handler.cpp"]
        SRC2["gpio_chips.cpp"]
        SRC3["gpio_lines.cpp"]
        SRC4["gpio_json_config.cpp"]
        SRC5["gpio_utils.cpp"]
    end
    
    subgraph "Dependencies"
        DEP1["sdbusplus"]
        DEP2["gpio_device"]
        DEP3["phosphor_logging_dep"]
        DEP4["threads"]
    end
    
    SRC1 --> EXE["executable()<br/>gpio-status-handlerd"]
    SRC2 --> EXE
    SRC3 --> EXE
    SRC4 --> EXE
    SRC5 --> EXE
    
    DEP1 --> EXE
    DEP2 --> EXE
    DEP3 --> EXE
    DEP4 --> EXE
    
    EXE --> INSTALL["Install to bindir<br/>default: /usr/bin"]
```

**Sources:** [meson.build:94-105]()

## Quick Start Commands

Basic build commands for common scenarios:

| Scenario | Commands |
|----------|----------|
| **Standard build** | `meson builddir`<br/>`ninja -C builddir` |
| **Development build** | `meson builddir -Dsandbox_mode=enabled -Dapi_stubs=enabled -Ddebug_log=3`<br/>`ninja -C builddir` |
| **Production build** | `meson builddir -Ddebug_log=1`<br/>`ninja -C builddir`<br/>`ninja -C builddir install` |
| **Clean build** | `ninja -C builddir clean` |
| **Reconfigure** | `cd builddir && meson configure -Ddebug_log=2` |
| **Complete rebuild** | `rm -rf builddir`<br/>`meson builddir`<br/>`ninja -C builddir` |

**Sources:** [README.md:22-50](), [README.md:75-96]()

## Build Output

A successful build produces:

1. **Executable:** `builddir/gpio-status-handlerd`
2. **Installation path:** Determined by `get_option('prefix') + '/' + get_option('bindir')` ([meson.build:20]()), typically `/usr/bin/gpio-status-handlerd`

The binary size and behavior vary significantly based on build options:

| Configuration | Binary Characteristics |
|---------------|------------------------|
| Debug (level 3-4) | Larger binary, verbose logging, performance instrumentation available |
| Production (level 0-1) | Smaller binary, minimal logging, optimized for deployment |
| Sandbox mode | x86-64 target, no hardware dependencies |
| Hardware mode | ARM target, real GPIO/D-Bus APIs |

**Sources:** [meson.build:94-105](), [README.md:98-121]()

## Next Steps

- For build system architecture details, see [Build System Overview](#3.1)
- For dependency documentation and fallback mechanisms, see [Dependencies](#3.2)
- For comprehensive build option explanations, see [Build Options](#3.3)
- For step-by-step compilation instructions, see [Compilation Guide](#3.4)
- For runtime configuration after building, see [Configuration](#4)

---

