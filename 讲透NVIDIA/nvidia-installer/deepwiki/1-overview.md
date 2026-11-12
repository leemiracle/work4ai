<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-installer · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [install-from-cwd.c](install-from-cwd.c)
- [nvidia-installer.c](nvidia-installer.c)
- [nvidia-installer.h](nvidia-installer.h)

</details>



The **nvidia-installer** is a comprehensive tool for installing, upgrading, and uninstalling NVIDIA graphics drivers on Unix and Linux systems. This repository contains a sophisticated package installation system that handles kernel module compilation, file deployment, system integration, and recovery mechanisms.

The installer supports multiple installation scenarios including driver upgrades, kernel module-only installations, uninstallation, and integration with distribution package managers. For information about the specific installation workflow phases, see [Installation Process](#3). For details about kernel module building and management, see [Kernel Module Management](#3.3).

## Architecture Overview

The nvidia-installer follows a modular architecture centered around two primary data structures: the `Options` structure that controls installation behavior, and the `Package` structure that represents the driver package being installed.

### Core System Architecture

```mermaid
graph TB
    subgraph "Entry Point Layer"
        main["main()"]
        parse["parse_commandline()"]
        Options["Options Structure"]
    end
    
    subgraph "Installation Engine"
        install_from_cwd["install_from_cwd()"]
        parse_manifest["parse_manifest()"]
        Package["Package Structure"]
    end
    
    subgraph "Core Subsystems"
        kernel["Kernel Module System<br/>kernel.c"]
        files["File Operations<br/>files.c"]
        cmdlist["Command List Builder<br/>command-list.c"]
        backup["Backup System<br/>backup.c"]
    end
    
    subgraph "User Interface Layer"
        ui_core["user-interface.c"]
        stream_ui["stream-ui.c"]
        ncurses_ui["ncurses-ui.c"]
    end
    
    subgraph "System Integration"
        utils["System Utilities<br/>misc.c"]
        validation["System Validation<br/>sanity.c"]
        initramfs["Initramfs Management<br/>initramfs.c"]
    end
    
    main --> parse
    parse --> Options
    main --> install_from_cwd
    install_from_cwd --> parse_manifest
    parse_manifest --> Package
    
    install_from_cwd --> kernel
    install_from_cwd --> files
    install_from_cwd --> cmdlist
    install_from_cwd --> backup
    
    install_from_cwd --> ui_core
    ui_core --> stream_ui
    ui_core --> ncurses_ui
    
    install_from_cwd --> utils
    install_from_cwd --> validation
    install_from_cwd --> initramfs
    
    Options --> install_from_cwd
    Package --> kernel
    Package --> files
    Package --> cmdlist
```

Sources: [nvidia-installer.c:648-761](), [install-from-cwd.c:96-454](), [nvidia-installer.h:185-342](), [nvidia-installer.h:457-471]()

### Data Structure Relationships

```mermaid
graph LR
    subgraph "Configuration Data"
        Options["Options<br/>(nvidia-installer.h:185)"]
        utils["utils[MAX_UTILS]<br/>System tool paths"]
        prefixes["Installation Prefixes<br/>opengl_prefix, x_prefix, etc."]
        flags["Boolean Flags<br/>expert, uninstall, dkms, etc."]
    end
    
    subgraph "Package Data"
        Package["Package<br/>(nvidia-installer.h:457)"]
        entries["PackageEntry[]<br/>entries array"]
        kernel_modules["KernelModuleInfo[]<br/>kernel_modules array"]
        metadata["Metadata<br/>description, version"]
    end
    
    subgraph "File Entry Details"
        PackageEntry["PackageEntry<br/>(nvidia-installer.h:371)"]
        file_info["file, path, name, target"]
        file_type["PackageEntryFileType<br/>(nvidia-installer.h:101)"]
        capabilities["PackageEntryFileCapabilities<br/>(nvidia-installer.h:350)"]
    end
    
    Options --> Package
    Package --> entries
    entries --> PackageEntry
    PackageEntry --> file_type
    PackageEntry --> capabilities
    Package --> kernel_modules
    Options --> utils
    Options --> prefixes
    Options --> flags
```

Sources: [nvidia-installer.h:185-342](), [nvidia-installer.h:457-471](), [nvidia-installer.h:371-418](), [nvidia-installer.h:101-169]()

## Core Components

### Options Structure
The `Options` structure serves as the central configuration hub, containing over 100 configuration parameters that control every aspect of the installation process. Key categories include:

| Category | Examples | Purpose |
|----------|----------|---------|
| Installation Paths | `opengl_prefix`, `x_prefix`, `utility_prefix` | Define where files are installed |
| Boolean Flags | `expert`, `uninstall`, `no_kernel_modules` | Control installation behavior |
| System Tools | `utils[MAX_UTILS]` | Paths to required system utilities |
| Kernel Configuration | `kernel_source_path`, `kernel_name` | Kernel module build settings |
| UI Configuration | `ui.name`, `silent`, `no_questions` | User interface behavior |

Sources: [nvidia-installer.h:185-342]()

### Package Structure
The `Package` structure represents the driver package being installed, containing:

- **Metadata**: Description, version, and build directory information
- **File Entries**: Array of `PackageEntry` structures describing each file to install
- **Kernel Modules**: Array of `KernelModuleInfo` structures for kernel components
- **Build Information**: Paths and configuration for kernel module compilation

Sources: [nvidia-installer.h:457-471]()

### File Type System
The installer uses a comprehensive file type system with over 60 different `PackageEntryFileType` values, including:

- `FILE_TYPE_KERNEL_MODULE` - Compiled kernel modules
- `FILE_TYPE_OPENGL_LIB` - OpenGL library files  
- `FILE_TYPE_UTILITY_BINARY` - NVIDIA utility programs
- `FILE_TYPE_DOCUMENTATION` - Documentation files
- `FILE_TYPE_SYSTEMD_UNIT` - systemd service files

Each file type has associated capabilities defined by `PackageEntryFileCapabilities` that determine how the file should be processed.

Sources: [nvidia-installer.h:101-169](), [nvidia-installer.h:350-360]()

## Installation Workflow

The installation process follows a well-defined sequence orchestrated by `install_from_cwd()`:

```mermaid
flowchart TD
    start["install_from_cwd()"] --> manifest["parse_manifest()<br/>Build Package structure"]
    manifest --> validate["System Validation<br/>check_for_nvidia_graphics_devices()"]
    validate --> unload["check_for_unloaded_kernel_module()"]
    unload --> existing["check_for_existing_driver()"]
    existing --> kernel_build["install_kernel_modules()<br/>Build/install kernel modules"]
    kernel_build --> prefixes["get_prefixes()<br/>Determine installation paths"]
    prefixes --> destinations["set_destinations()<br/>Resolve file destinations"]
    destinations --> uninstall_old["run_existing_uninstaller()"]
    uninstall_old --> command_list["build_command_list()<br/>Create installation commands"]
    command_list --> approve["ui_approve_command_list()<br/>User confirmation"]
    approve --> execute["do_install()<br/>Execute installation"]
    execute --> verify["check_installed_files_from_package()"]
    verify --> complete["Installation Complete"]
```

Sources: [install-from-cwd.c:96-454]()

## System Integration Points

The installer integrates with numerous system components:

### System Utilities
The installer requires and locates various system utilities defined in utility enums:
- **SystemUtils**: `LDCONFIG`, `GREP`, `DMESG`, `TAIL` 
- **ModuleUtils**: `MODPROBE`, `RMMOD`, `LSMOD`, `DEPMOD`
- **DevelopUtils**: `CC`, `MAKE`, `LD` for kernel module compilation

Sources: [nvidia-installer.h:37-95]()

### User Interface Abstraction
The installer supports multiple UI implementations through a common interface:
- **Stream UI**: Console-based output for scripted installations
- **Ncurses UI**: Interactive text-based interface for manual installations
- **None UI**: Silent operation for automated deployments

For detailed information about the UI system architecture, see [User Interface System](#4).

### Build and Packaging Integration
The installer includes sophisticated build system integration for:
- Kernel module compilation from source
- Precompiled kernel interface linking
- Module signing for secure boot systems
- DKMS integration for dynamic kernel support

For comprehensive build system documentation, see [Build System](#5).

Sources: [nvidia-installer.h:316-321](), [install-from-cwd.c:193-237]()

## Key Design Principles

1. **Robustness**: Comprehensive backup and rollback capabilities ensure system recovery
2. **Flexibility**: Extensive configuration options support diverse deployment scenarios  
3. **Modularity**: Clear separation between UI, installation logic, and system operations
4. **Validation**: Multi-layer validation from command-line parsing to post-install verification
5. **Integration**: Deep integration with Linux distribution package management and system services

The nvidia-installer represents a mature, production-ready installation system designed to handle the complexities of graphics driver deployment across diverse Linux environments while maintaining system stability and providing comprehensive error recovery mechanisms.

---

