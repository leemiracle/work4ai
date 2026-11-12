<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-installer · page 7 Data Structures and Configuration · fetched 2026-10-26 -->

# Data Structures and Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [manifest.c](manifest.c)
- [nvidia-installer.h](nvidia-installer.h)

</details>



This document provides a comprehensive reference for the core data structures that drive the nvidia-installer's configuration and package management systems. It covers the primary `Options` structure that holds installation configuration, the `Package` and `PackageEntry` structures that represent the driver package contents, and the file type classification system that determines how different components are handled during installation.

For information about how these structures are populated during command line parsing, see [Command Line Interface](#3.1). For details on how the installation engine uses these structures, see [Installation Engine](#3.2).

## Core Configuration Structure

The `Options` structure serves as the central configuration hub for the entire installation process. It contains all user preferences, system detection results, and runtime state information needed to coordinate the installation.

### Options Structure Overview

```mermaid
graph TB
    subgraph "Options Structure Components"
        A[Options] --> B["Installation Flags<br/>(expert, uninstall, silent, etc.)"]
        A --> C["System Paths<br/>(opengl_prefix, x_prefix, etc.)"]
        A --> D["Module Configuration<br/>(kernel_source_path, dkms, etc.)"]
        A --> E["UI State<br/>(ui.name, ui.priv, etc.)"]
        A --> F["System Detection<br/>(pci_devices, utils[MAX_UTILS])"]
        A --> G["File Type Overrides<br/>(file_type_destination_overrides[])"]
    end
    
    subgraph "Key Configuration Categories"
        H["Boolean Flags<br/>expert, debug, no_questions"]
        I["Path Configuration<br/>opengl_prefix, utility_prefix"]
        J["Optional Features<br/>NVOptionalBool enums"]
        K["Runtime State<br/>loaded_kernel_module_detected"]
    end
    
    B --> H
    C --> I
    D --> J
    F --> K
```

**Options Structure Categories**

The `Options` structure is organized into several logical categories:

| Category | Purpose | Key Fields |
|----------|---------|------------|
| Installation Control | Basic installation behavior | `expert`, `uninstall`, `silent`, `no_questions` |
| Path Configuration | Directory and file locations | `opengl_prefix`, `x_prefix`, `utility_prefix` |
| Module Management | Kernel module handling | `kernel_source_path`, `dkms`, `no_kernel_modules` |
| Feature Toggles | Optional component installation | `install_libglvnd_libraries`, `install_compat32_libs` |
| System Detection | Runtime environment information | `pci_devices`, `utils[]`, `modular_xorg` |
| UI Configuration | User interface state | `ui.name`, `ui.priv`, `ui.status_active` |

**Sources:** [nvidia-installer.h:185-342]()

### Configuration Flow Architecture

```mermaid
flowchart TD
    A["Command Line Parsing<br/>option_table.h"] --> B["Options Structure<br/>nvidia-installer.h:185-342"]
    
    B --> C["System Detection<br/>misc.c utilities"]
    C --> D["Path Resolution<br/>files.c:set_destinations()"]
    D --> E["Package Processing<br/>manifest.c parsing"]
    
    B --> F["UI Initialization<br/>user-interface.c"]
    B --> G["Kernel Module Config<br/>kernel.c"]
    B --> H["File Type Overrides<br/>file_type_destination_overrides[]"]
    
    E --> I["Installation Execution<br/>install-from-cwd.c"]
    F --> I
    G --> I
    H --> I
    
    subgraph "Configuration Categories"
        J["Boolean Flags<br/>(silent, expert, debug)"]
        K["Path Configurations<br/>(prefixes, libdirs)"]
        L["Feature Selections<br/>(NVOptionalBool values)"]
        M["System State<br/>(detected hardware/tools)"]
    end
    
    B --> J
    B --> K  
    B --> L
    B --> M
```

**Sources:** [nvidia-installer.h:185-342](), [option_table.h](), [install-from-cwd.c](), [misc.c]()

## Package Data Structures

The package system uses a hierarchical structure to represent the driver package contents, with the `Package` structure containing metadata and an array of `PackageEntry` structures representing individual files.

### Package Structure Hierarchy

```mermaid
graph TB
    A["Package<br/>nvidia-installer.h:457-471"] --> B["Package Metadata<br/>(description, version)"]
    A --> C["Build Information<br/>(kernel_module_build_directory)"]
    A --> D["PackageEntry Array<br/>(entries[], num_entries)"]
    A --> E["Kernel Module Info<br/>(kernel_modules[], num_kernel_modules)"]
    
    D --> F["PackageEntry<br/>nvidia-installer.h:371-418"]
    E --> G["KernelModuleInfo<br/>nvidia-installer.h:444-454"]
    
    F --> H["File Information<br/>(file, path, name, target)"]
    F --> I["Installation Data<br/>(dst, type, mode)"]
    F --> J["File Capabilities<br/>(PackageEntryFileCapabilities)"]
    F --> K["Architecture Info<br/>(compat_arch, inherit_path_depth)"]
    
    G --> L["Module Properties<br/>(module_name, module_filename)"]
    G --> M["Build Configuration<br/>(interface_filename, core_object_name)"]
    G --> N["Optional Features<br/>(is_optional, disable_option)"]
```

**Package Entry File Lifecycle**

| Field | Purpose | Set By | Used By |
|-------|---------|--------|---------|
| `file` | Source filename in package | Manifest parser | File operations |
| `path` | Template path pattern | Manifest parser | Path resolution |
| `dst` | Final installation destination | `set_destinations()` | Installation execution |
| `type` | File type classification | Manifest parser | Installation logic |
| `caps` | File capabilities/properties | `parse_manifest_file_type()` | Feature decisions |

**Sources:** [nvidia-installer.h:457-471](), [nvidia-installer.h:371-418](), [nvidia-installer.h:444-454]()

## File Type Classification System

The installer uses a comprehensive file type system to determine how different components should be handled during installation. Each file type has associated capabilities that control installation behavior.

### File Type Capabilities Matrix

```mermaid
graph LR
    A["PackageEntryFileType<br/>nvidia-installer.h:101-169"] --> B["packageEntryFileTypeTable<br/>manifest.c:59-138"]
    
    B --> C["File Type Properties"]
    
    subgraph "Capability Flags"
        D["has_arch<br/>(architecture-specific)"]
        E["installable<br/>(should be installed)"]
        F["has_path<br/>(uses path templates)"]
        G["is_symlink<br/>(symbolic link)"]
        H["is_shared_lib<br/>(shared library)"]
        I["is_opengl<br/>(OpenGL component)"]
        J["is_temporary<br/>(temporary file)"]
        K["is_conflicting<br/>(may conflict)"]
        L["inherit_path<br/>(inherit parent path)"]
    end
    
    C --> D
    C --> E
    C --> F
    C --> G
    C --> H
    C --> I
    C --> J
    C --> K
    C --> L
```

**Key File Type Categories**

| Category | File Types | Capabilities | Installation Behavior |
|----------|------------|--------------|----------------------|
| Kernel Components | `KERNEL_MODULE`, `KERNEL_MODULE_SRC` | `installable`, `is_conflicting` | Module building/loading |
| OpenGL Libraries | `OPENGL_LIB`, `TLS_LIB`, `GLVND_LIB` | `has_arch`, `is_shared_lib`, `is_opengl` | Library installation with arch handling |
| Symbolic Links | `OPENGL_SYMLINK`, `CUDA_SYMLINK` | `is_symlink`, `has_arch` | Link creation with architecture paths |
| System Integration | `SYSTEMD_UNIT`, `XORG_OUTPUTCLASS_CONFIG` | `installable` | System service integration |
| Documentation | `DOCUMENTATION`, `MANPAGE` | `installable`, `has_path` | Documentation installation |

**Sources:** [nvidia-installer.h:101-169](), [manifest.c:59-138]()

### File Type Processing Pipeline

```mermaid
flowchart TD
    A["Manifest Parsing<br/>parse_manifest_file_type()"] --> B["File Type Lookup<br/>packageEntryFileTypeTable[]"]
    
    B --> C["Capability Assignment<br/>PackageEntryFileCapabilities"]
    C --> D["Installability Check<br/>get_installable_file_type_list()"]
    
    D --> E{"Installable?"}
    E -->|Yes| F["Path Resolution<br/>set_destinations()"]
    E -->|No| G["Skip File"]
    
    F --> H["Architecture Handling<br/>(if has_arch)"]
    H --> I["Conflict Detection<br/>(if is_conflicting)"]
    I --> J["Installation Execution<br/>command-list.c"]
    
    subgraph "File Type Properties"
        K["OPENGL_LIB<br/>has_arch=T, is_shared_lib=T"]
        L["KERNEL_MODULE<br/>installable=T, is_conflicting=T"]
        M["DOCUMENTATION<br/>installable=T, has_path=T"]
    end
    
    B --> K
    B --> L
    B --> M
```

**Sources:** [manifest.c:165-180](), [manifest.c:185-225](), [files.c]()

## System Utility Management

The installer maintains comprehensive tracking of system utilities required for various operations. These are organized into categorized enumerations that drive system validation and feature availability.

### Utility Classification System

```mermaid
graph TB
    A["System Utilities<br/>nvidia-installer.h:37-95"] --> B["SystemUtils<br/>(LDCONFIG, GREP, DMESG, TAIL)"]
    A --> C["SystemOptionalUtils<br/>(OBJCOPY, CHCON, PKG_CONFIG, etc.)"]
    A --> D["ModuleUtils<br/>(MODPROBE, RMMOD, LSMOD, DEPMOD)"]  
    A --> E["DevelopUtils<br/>(CC, MAKE, LD, TR, SED)"]
    
    F["Options.utils[MAX_UTILS]<br/>nvidia-installer.h:284"] --> G["Utility Path Storage"]
    
    B --> G
    C --> G
    D --> G
    E --> G
    
    H["System Detection<br/>misc.c:find_system_utils()"] --> F
    I["Feature Availability<br/>Based on detected utilities"] --> J["Installation Behavior<br/>Conditional features"]
```

**Utility Categories and Usage**

| Category | Purpose | Key Utilities | Impact on Installation |
|----------|---------|---------------|----------------------|
| SystemUtils | Core system operations | `LDCONFIG`, `GREP`, `DMESG` | Required for basic functionality |
| SystemOptionalUtils | Enhanced features | `OBJCOPY`, `SYSTEMCTL`, `DKMS` | Enable optional capabilities |
| ModuleUtils | Kernel module management | `MODPROBE`, `DEPMOD`, `LSMOD` | Required for module installation |
| DevelopUtils | Kernel compilation | `CC`, `MAKE`, `LD` | Required for building modules |

**Sources:** [nvidia-installer.h:37-95](), [nvidia-installer.h:284](), [misc.c]()

## Configuration State Management

The installer maintains several categories of runtime state that influence installation decisions and track system conditions discovered during execution.

### Runtime State Tracking

```mermaid
graph TB
    subgraph "Detection Results"
        A["pci_devices<br/>nvidia-installer.h:323-329"] --> B["GPU Hardware Detection"]
        C["loaded_kernel_module_detected<br/>nvidia-installer.h:231"] --> D["Driver State"]
        E["running_x_server_detected<br/>nvidia-installer.h:232"] --> F["X11 State"]
    end
    
    subgraph "System Capabilities"
        G["modular_xorg<br/>nvidia-installer.h:275"] --> H["X.Org Architecture"]
        I["xorg_supports_output_class<br/>nvidia-installer.h:276"] --> J["Modern X11 Features"]
        K["selinux_enabled<br/>nvidia-installer.h:208"] --> L["Security Framework"]
    end
    
    subgraph "Installation Decisions"
        M["NVOptionalBool Values<br/>nvidia-installer.h:234-237"] --> N["Feature Installation"]
        O["file_type_destination_overrides<br/>nvidia-installer.h:239"] --> P["Custom Path Mapping"]
    end
    
    B --> Q["Installation Logic<br/>install-from-cwd.c"]
    D --> Q
    F --> Q
    H --> Q
    J --> Q
    L --> Q
    N --> Q
    P --> Q
```

**Configuration Categories**

| State Category | Fields | Purpose |
|----------------|--------|---------|
| Hardware Detection | `pci_devices.found_supported`, `pci_devices.found_vga` | GPU compatibility validation |
| Driver State | `loaded_kernel_module_detected`, `kernel_module_signed` | Existing installation detection |
| System Architecture | `modular_xorg`, `xorg_supports_output_class` | Feature capability determination |
| Optional Features | `install_libglvnd_libraries`, `install_compat32_libs` | User/auto-detected preferences |
| Path Customization | `file_type_destination_overrides[]` | Custom installation locations |

**Sources:** [nvidia-installer.h:323-329](), [nvidia-installer.h:231-232](), [nvidia-installer.h:275-276](), [nvidia-installer.h:234-237](), [nvidia-installer.h:239]()

---

