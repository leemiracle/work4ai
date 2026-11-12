<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-modprobe · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [modprobe-utils/nvidia-modprobe-utils.c](modprobe-utils/nvidia-modprobe-utils.c)
- [nvidia-modprobe.c](nvidia-modprobe.c)
- [version.mk](version.mk)

</details>



## Purpose and Scope

The nvidia-modprobe repository provides a setuid utility for loading NVIDIA kernel modules and creating device files in a Linux distribution-independent manner. This utility serves as a bridge between user-space NVIDIA driver components that lack sufficient privileges and the privileged operations required for kernel module loading and device file creation.

The system handles automatic loading of various NVIDIA kernel modules (`nvidia`, `nvidia-uvm`, `nvidia-modeset`, `nvidia-nvlink`, `nvidia-nvswitch`) and creates the corresponding device files under `/dev/`. It is designed to work across different Linux distributions that handle module loading and device management differently.

For detailed information about the main executable implementation, see [Main Executable](#2.1). For the core library functionality, see [Core Library Implementation](#2.2). For build system details, see [Build System](#3).

## System Architecture

The nvidia-modprobe system follows a layered architecture with clear separation between the user interface, core business logic, and system integration layers.

### High-Level Component Structure

```mermaid
graph TB
    subgraph "User Interface Layer"
        main_exec["`nvidia-modprobe.c`<br/>Main Executable"]
        cli_opts["`option-table.h`<br/>CLI Options"]
        arg_parser["`nvgetopt.c`<br/>Argument Parser"]
    end
    
    subgraph "Core Business Logic"
        api_header["`nvidia-modprobe-utils.h`<br/>Public API"]
        core_impl["`nvidia-modprobe-utils.c`<br/>Core Implementation"]
    end
    
    subgraph "System Integration"
        pci_enum["`pci-sysfs.c`<br/>PCI Enumeration"]
        kernel_interface["`Linux Kernel`<br/>Module & Device APIs"]
    end
    
    subgraph "Support Systems"
        common_utils["`common-utils.c`<br/>Utility Functions"]
        msg_system["`msg.c`<br/>Message Handling"]
        version_mgmt["`version.mk`<br/>Version Management"]
    end
    
    main_exec --> cli_opts
    main_exec --> arg_parser
    main_exec --> api_header
    api_header --> core_impl
    core_impl --> pci_enum
    core_impl --> kernel_interface
    main_exec --> common_utils
    core_impl --> common_utils
    main_exec --> msg_system
    core_impl --> msg_system
    version_mgmt --> main_exec
    version_mgmt --> core_impl
```

**Sources:** [nvidia-modprobe.c:1-290](), [modprobe-utils/nvidia-modprobe-utils.c:1-1167](), [version.mk:1-12](), [Makefile:1-163]()

### Code Entity Mapping

```mermaid
graph LR
    subgraph "Module Loading Functions"
        nvidia_modprobe["`nvidia_modprobe()`<br/>Load nvidia module"]
        nvidia_uvm_modprobe["`nvidia_uvm_modprobe()`<br/>Load nvidia-uvm module"]
        nvidia_modeset_modprobe["`nvidia_modeset_modprobe()`<br/>Load nvidia-modeset module"]
        modprobe_helper["`modprobe_helper()`<br/>Core loading logic"]
    end
    
    subgraph "Device Creation Functions"
        nvidia_mknod["`nvidia_mknod()`<br/>Create /dev/nvidia*"]
        nvidia_uvm_mknod["`nvidia_uvm_mknod()`<br/>Create /dev/nvidia-uvm*"]
        nvidia_nvlink_mknod["`nvidia_nvlink_mknod()`<br/>Create /dev/nvidia-nvlink*"]
        nvidia_nvswitch_mknod["`nvidia_nvswitch_mknod()`<br/>Create /dev/nvidia-nvswitch*"]
        mknod_helper["`mknod_helper()`<br/>Core creation logic"]
    end
    
    subgraph "Hardware Detection"
        pci_enum_match_id["`pci_enum_match_id()`<br/>Find NVIDIA PCI devices"]
        is_kernel_module_loaded["`is_kernel_module_loaded()`<br/>Check module status"]
        nvidia_get_chardev_major["`nvidia_get_chardev_major()`<br/>Get device major number"]
    end
    
    subgraph "Main Entry Point"
        main_func["`main()`<br/>Command processing"]
        nvgetopt_parse["`nvgetopt()`<br/>Argument parsing"]
    end
    
    main_func --> nvidia_modprobe
    main_func --> nvidia_uvm_modprobe
    main_func --> nvidia_modeset_modprobe
    main_func --> nvidia_mknod
    main_func --> nvidia_uvm_mknod
    main_func --> nvidia_nvlink_mknod
    main_func --> nvidia_nvswitch_mknod
    
    nvidia_modprobe --> modprobe_helper
    nvidia_uvm_modprobe --> modprobe_helper
    nvidia_modeset_modprobe --> modprobe_helper
    
    nvidia_mknod --> mknod_helper
    nvidia_uvm_mknod --> mknod_helper
    nvidia_nvlink_mknod --> mknod_helper
    nvidia_nvswitch_mknod --> mknod_helper
    
    modprobe_helper --> pci_enum_match_id
    modprobe_helper --> is_kernel_module_loaded
    mknod_helper --> nvidia_get_chardev_major
    
    main_func --> nvgetopt_parse
```

**Sources:** [nvidia-modprobe.c:89-289](), [modprobe-utils/nvidia-modprobe-utils.c:354-357](), [modprobe-utils/nvidia-modprobe-utils.c:820-823](), [modprobe-utils/nvidia-modprobe-utils.c:836-839](), [modprobe-utils/nvidia-modprobe-utils.c:642-649](), [modprobe-utils/nvidia-modprobe-utils.c:803-814]()

## Key Components

The system consists of several key components that work together to provide kernel module loading and device file creation capabilities:

| Component | Primary Files | Purpose |
|-----------|---------------|---------|
| **Main Executable** | `nvidia-modprobe.c` | Command-line interface and operation orchestration |
| **Core Library** | `nvidia-modprobe-utils.c/h` | Module loading and device creation implementation |
| **PCI Integration** | `pci-sysfs.c` | Hardware detection and PCI device enumeration |
| **Build System** | `version.mk`, `utils.mk`, `Makefile` | Version management and cross-platform compilation |
| **Common Utilities** | `common-utils.c/h` | Shared utility functions and memory management |
| **Message System** | `msg.c` | Formatted output and error reporting |
| **CLI Processing** | `nvgetopt.c`, `option-table.h` | Command-line argument parsing |

The main executable handles command-line processing and delegates actual work to the core library, which implements the low-level operations for interacting with the Linux kernel module system and device filesystem.

**Sources:** [nvidia-modprobe.c:17-30](), [modprobe-utils/nvidia-modprobe-utils.c:24-26](), [Makefile:29-34]()

## Integration Context

The nvidia-modprobe utility operates as a critical component in the NVIDIA driver ecosystem, serving as a privilege escalation mechanism for user-space components. It is designed to be installed as a setuid binary, allowing unprivileged processes to perform privileged operations.

### Operational Flow

```mermaid
graph TD
    user_app["`User Application`<br/>(e.g., CUDA program)"]
    driver_lib["`NVIDIA Driver Library`<br/>(user-space)"]
    modprobe_util["`nvidia-modprobe`<br/>(setuid binary)"]
    kernel_mod["`NVIDIA Kernel Module`<br/>(nvidia.ko)"]
    dev_files["`Device Files`<br/>(/dev/nvidia*)"]
    
    user_app --> driver_lib
    driver_lib --> modprobe_util
    modprobe_util --> kernel_mod
    modprobe_util --> dev_files
    driver_lib --> dev_files
    
    user_app -.-> dev_files
```

The utility supports multiple NVIDIA kernel modules and their corresponding device files:

- **nvidia module**: Primary graphics driver (`/dev/nvidia*`)
- **nvidia-uvm module**: Unified Virtual Memory (`/dev/nvidia-uvm`, `/dev/nvidia-uvm-tools`)
- **nvidia-modeset module**: Display/KMS functionality (`/dev/nvidia-modeset`)
- **nvidia-nvlink module**: High-speed interconnect (`/dev/nvidia-nvlink`)
- **nvidia-nvswitch module**: Switch fabric (`/dev/nvidia-nvswitch*`)

The system includes hardware detection to verify NVIDIA PCI devices are present before attempting module loading, preventing unnecessary error messages on systems without NVIDIA hardware.

**Sources:** [nvidia-modprobe.c:18-29](), [modprobe-utils/nvidia-modprobe-utils.c:56-81](), [modprobe-utils/nvidia-modprobe-utils.c:234-252]()

---

