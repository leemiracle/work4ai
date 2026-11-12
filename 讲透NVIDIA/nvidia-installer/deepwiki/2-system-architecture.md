<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-installer · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backup.c](backup.c)
- [command-list.c](command-list.c)
- [install-from-cwd.c](install-from-cwd.c)
- [misc.c](misc.c)
- [nvidia-installer.h](nvidia-installer.h)

</details>



This document describes the overall architectural design of nvidia-installer, detailing how the major subsystems interact and how data flows through the system during installation operations. For specific implementation details of individual subsystems, see their respective dedicated pages such as [Installation Process](#3) and [User Interface System](#4).

## Overview

The nvidia-installer follows a modular, command-driven architecture centered around a comprehensive `Options` structure that carries configuration and state throughout the system. The architecture separates concerns into distinct subsystems: command-line processing, installation orchestration, system operations, user interface abstraction, and backup/recovery management.

## Core Data Structures

The architecture is built around several key data structures defined in [nvidia-installer.h:185-472]():

```mermaid
classDiagram
    class Options {
        +int expert
        +int uninstall
        +int no_kernel_modules
        +char* utils[MAX_UTILS]
        +char* kernel_name
        +char* log_file_name
        +ui struct
        +pci_devices struct
    }
    
    class Package {
        +char* description
        +char* version
        +PackageEntry* entries
        +int num_entries
        +KernelModuleInfo* kernel_modules
        +int num_kernel_modules
    }
    
    class PackageEntry {
        +char* file
        +char* path
        +char* dst
        +PackageEntryFileType type
        +PackageEntryFileCompatArch compat_arch
        +mode_t mode
        +PackageEntryFileCapabilities caps
    }
    
    class CommandList {
        +Command* cmds
        +char** descriptions
        +int num
    }
    
    Options --> Package : "processes"
    Package --> PackageEntry : "contains"
    Options --> CommandList : "generates"
```

Sources: [nvidia-installer.h:185-342](), [nvidia-installer.h:457-471](), [nvidia-installer.h:371-418](), [command-list.c:99-106]()

## System Architecture Overview

The system is organized into distinct functional layers that interact through well-defined interfaces:

```mermaid
flowchart TB
    subgraph "Entry Layer"
        main["nvidia-installer.c<br/>main()"]
        options["option_table.h<br/>CLI parsing"]
    end
    
    subgraph "Installation Engine"
        install_core["install-from-cwd.c<br/>install_from_cwd()"]
        manifest["manifest parsing<br/>parse_manifest()"]
        cmdlist["command-list.c<br/>build_command_list()"]
    end
    
    subgraph "System Operations"
        kernel_ops["kernel.c<br/>kernel module mgmt"]
        file_ops["files.c<br/>file operations"]
        misc_ops["misc.c<br/>system validation"]
        backup_ops["backup.c<br/>backup/restore"]
    end
    
    subgraph "User Interface"
        ui_core["user-interface.c<br/>UI abstraction"]
        stream_ui["stream-ui.c<br/>console output"]
        ncurses_ui["ncurses-ui.c<br/>interactive UI"]
    end
    
    main --> options
    main --> install_core
    install_core --> manifest
    install_core --> cmdlist
    cmdlist --> kernel_ops
    cmdlist --> file_ops
    cmdlist --> backup_ops
    install_core --> misc_ops
    install_core --> ui_core
    ui_core --> stream_ui
    ui_core --> ncurses_ui
```

Sources: [nvidia-installer.c](), [install-from-cwd.c:96-454](), [command-list.c:255-519](), [misc.c:548-890]()

## Installation Flow Architecture

The installation process follows a structured flow with multiple validation and decision points:

```mermaid
sequenceDiagram
    participant M as main()
    participant I as install_from_cwd()
    participant P as parse_manifest()
    participant V as Validation
    participant C as build_command_list()
    participant E as execute_command_list()
    participant B as Backup System
    
    M->>I: Options struct
    I->>P: Parse .manifest file
    P-->>I: Package struct
    I->>V: System validation
    V->>V: check_euid()
    V->>V: find_system_utils()
    V->>V: check_for_running_x()
    I->>C: Build installation commands
    C->>B: Generate backup commands
    C-->>I: CommandList
    I->>E: Execute commands
    E->>B: Backup existing files
    E->>E: Install new files
    E->>E: Create symlinks
    E->>E: Run post-install commands
```

Sources: [install-from-cwd.c:96-454](), [install-from-cwd.c:726-1047](), [misc.c:100-113](), [misc.c:548-589](), [command-list.c:255-519](), [command-list.c:614-731]()

## Component Interaction Patterns

### Command List Pattern

The installer uses a command list pattern where all installation operations are first collected into a `CommandList` structure, then validated and executed atomically:

```mermaid
flowchart LR
    subgraph "Command Generation"
        files["Package Files"] --> backup_cmds["BACKUP_CMD"]
        files --> install_cmds["INSTALL_CMD"]
        files --> symlink_cmds["SYMLINK_CMD"]
        system["System Ops"] --> run_cmds["RUN_CMD"]
    end
    
    subgraph "Command Execution"
        backup_cmds --> executor["execute_command_list()"]
        install_cmds --> executor
        symlink_cmds --> executor
        run_cmds --> executor
    end
    
    subgraph "Command Types"
        executor --> backup_op["do_backup()"]
        executor --> install_op["install_file()"]
        executor --> symlink_op["install_symlink()"]
        executor --> run_op["run_command()"]
    end
```

Sources: [command-list.c:77-87](), [command-list.c:255-519](), [command-list.c:614-731]()

### Options Structure Flow

The `Options` structure serves as the central configuration and state container that flows through all major subsystems:

```mermaid
flowchart TD
    parse["parse_commandline()"] --> opts["Options struct"]
    opts --> install["install_from_cwd()"]
    opts --> utils["find_system_utils()"]
    opts --> kernel["kernel operations"]
    opts --> files["file operations"]
    opts --> ui["user interface"]
    opts --> backup["backup system"]
    
    opts --> validation["System validation"]
    validation --> check_euid["check_euid()"]
    validation --> check_tools["check_development_tools()"]
    validation --> check_nouveau["check_for_nouveau()"]
```

Sources: [nvidia-installer.h:185-342](), [misc.c:100-113](), [misc.c:548-589](), [misc.c:778-827]()

## Subsystem Responsibilities

| Subsystem | Primary Functions | Key Files |
|-----------|------------------|-----------|
| Installation Engine | Orchestrates entire installation process, manifest parsing | `install-from-cwd.c` |
| Command List | Builds and executes atomic installation operations | `command-list.c` |
| System Operations | Kernel module management, file operations, validation | `kernel.c`, `files.c`, `misc.c` |
| Backup System | Safe backup/restore for rollback capability | `backup.c` |
| User Interface | Abstracted UI with multiple implementations | `user-interface.c`, `stream-ui.c`, `ncurses-ui.c` |

## Error Handling and Recovery

The architecture implements comprehensive error handling through several mechanisms:

1. **Backup System**: All operations are logged in `/var/lib/nvidia/log` allowing complete rollback via [backup.c:137-198]()
2. **Validation Gates**: Multiple validation points prevent installation on incompatible systems via [misc.c:100-113](), [misc.c:778-827]()
3. **Command List Validation**: User approval required before execution via [command-list.c:614-731]()
4. **Graceful Degradation**: Continue-after-error prompts for non-critical failures via [misc.c:905-924]()

Sources: [backup.c:137-198](), [backup.c:631-889](), [misc.c:905-924](), [command-list.c:614-731]()

## Data Flow Summary

The system follows a clear data flow pattern:

1. **Input Processing**: CLI arguments → `Options` structure
2. **Package Analysis**: `.manifest` file → `Package` structure  
3. **Command Generation**: `Package` + `Options` → `CommandList`
4. **Execution**: `CommandList` → System operations with backup logging
5. **Validation**: Post-install verification and cleanup

This architecture provides modularity, testability, and robust error recovery while maintaining clear separation of concerns between user interface, business logic, and system operations.

Sources: [nvidia-installer.h:185-342](), [install-from-cwd.c:96-454](), [command-list.c:255-519](), [backup.c:137-198]()

---

