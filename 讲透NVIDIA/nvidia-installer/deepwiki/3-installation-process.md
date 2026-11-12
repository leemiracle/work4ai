<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-installer · page 3 Installation Process · fetched 2026-10-26 -->

# Installation Process

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backup.c](backup.c)
- [command-list.c](command-list.c)
- [install-from-cwd.c](install-from-cwd.c)
- [misc.c](misc.c)

</details>



This document describes the comprehensive installation workflow implemented by nvidia-installer, covering all major phases from startup through completion. The installation process orchestrates manifest parsing, system validation, kernel module management, file operations, and recovery systems to safely install NVIDIA drivers.

For information about the command-line interface and option parsing, see [Command Line Interface](#3.1). For details about the core installation engine implementation, see [Installation Engine](#3.2). For kernel module-specific operations, see [Kernel Module Management](#3.3).

## Installation Workflow Overview

The nvidia-installer follows a multi-phase installation process designed to safely replace existing drivers while maintaining system stability through comprehensive backup and validation mechanisms.

### High-Level Installation Flow

```mermaid
flowchart TD
    Start["install_from_cwd()"] --> ParseManifest["parse_manifest()"]
    ParseManifest --> SystemChecks["System Validation"]
    SystemChecks --> ExistingDriver["check_for_existing_driver()"]
    ExistingDriver --> PreHooks["run_distro_hook('pre-install')"]
    
    PreHooks --> KernelModules{"Kernel Modules Needed?"}
    KernelModules -->|Yes| InstallKernel["install_kernel_modules()"]
    KernelModules -->|No| ProcessFiles["Process File Types"]
    InstallKernel --> ProcessFiles
    
    ProcessFiles --> SetDestinations["set_destinations()"]
    SetDestinations --> UninstallExisting["run_existing_uninstaller()"]
    UninstallExisting --> InitBackup["init_backup()"]
    
    InitBackup --> BuildCommands["build_command_list()"]
    BuildCommands --> UserApproval["ui_approve_command_list()"]
    UserApproval -->|Approved| ExecuteCommands["execute_command_list()"]
    UserApproval -->|Rejected| Exit["Exit Installation"]
    
    ExecuteCommands --> LoadModules["load_kernel_module()"]
    LoadModules --> PostHooks["run_distro_hook('post-install')"]
    PostHooks --> SanityCheck["check_installed_files_from_package()"]
    SanityCheck --> Complete["Installation Complete"]
    
    Exit --> Cleanup["Cleanup and Exit"]
    Complete --> Success["Success"]
```

Sources: [install-from-cwd.c:96-454]()

### Core Installation Phases

The installation process consists of six distinct phases, each with specific responsibilities and error handling:

| Phase | Primary Functions | Purpose |
|-------|------------------|---------|
| **Initialization** | `parse_manifest()`, `ui_set_title()` | Parse package data and initialize UI |
| **Validation** | `check_for_nvidia_graphics_devices()`, `check_for_running_x()` | System compatibility checks |
| **Kernel Processing** | `install_kernel_modules()`, `assisted_module_signing()` | Handle kernel module building/linking |
| **File Processing** | `set_destinations()`, `process_dot_desktop_files()` | Prepare files for installation |
| **Command Execution** | `build_command_list()`, `execute_command_list()` | Execute installation operations |
| **Finalization** | `check_installed_files_from_package()`, `run_nvidia_xconfig()` | Verify and complete installation |

Sources: [install-from-cwd.c:96-454]()

## Manifest Processing and Package Structure

The installation begins by parsing a `.manifest` file that describes all components to be installed. This process builds the internal `Package` structure that drives the entire installation.

### Manifest Parsing Flow

```mermaid
flowchart TD
    OpenManifest["open('.manifest')"] --> ReadHeader["Read Package Header"]
    ReadHeader --> ParseModules["parse_kernel_modules_list()"]
    ParseModules --> ParseEntries["Parse File Entries"]
    
    ParseEntries --> ProcessEntry["Process Each Entry"]
    ProcessEntry --> CheckType["Determine File Type"]
    CheckType --> SetCapabilities["Set File Capabilities"]
    SetCapabilities --> AddToPackage["add_package_entry()"]
    
    AddToPackage --> MoreEntries{"More Entries?"}
    MoreEntries -->|Yes| ProcessEntry
    MoreEntries -->|No| CompletePackage["Complete Package Structure"]
    
    CompletePackage --> ValidatePackage["Validate Package"]
    ValidatePackage --> ReturnPackage["Return Package*"]
```

The manifest file structure includes:
- **Line 1**: Package description string
- **Line 2**: Version string  
- **Line 4**: Whitespace-separated list of kernel module names
- **Remaining lines**: File entries with permissions, types, and paths

Sources: [install-from-cwd.c:726-1047]()

### Package Entry Processing

Each file in the manifest becomes a `PackageEntry` with specific capabilities and installation behavior:

```mermaid
flowchart LR
    FileEntry["File Entry from Manifest"] --> ParseFields["Parse Fields"]
    ParseFields --> DetermineType["parse_manifest_file_type()"]
    DetermineType --> SetCapabilities["get_file_type_capabilities()"]
    
    SetCapabilities --> CheckArch{"Has Architecture?"}
    CheckArch -->|Yes| SetCompat["Set Compatibility Architecture"]
    CheckArch -->|No| CheckPath{"Has Path?"}
    SetCompat --> CheckPath
    
    CheckPath -->|Yes| SetPath["Set Installation Path"]
    CheckPath -->|No| CheckSymlink{"Is Symlink?"}
    SetPath --> CheckSymlink
    
    CheckSymlink -->|Yes| SetTarget["Set Symlink Target"]
    CheckSymlink -->|No| AddEntry["add_package_entry()"]
    SetTarget --> AddEntry
```

Sources: [install-from-cwd.c:838-1016](), [install-from-cwd.c:1056-1096]()

## Command List Building and Execution

The installation process builds a comprehensive list of operations to perform, allowing for user review and atomic execution with rollback capabilities.

### Command List Construction

```mermaid
flowchart TD
    StartBuild["build_command_list()"] --> FindConflicts["Find Conflicting Files"]
    FindConflicts --> ConflictingKernel["find_conflicting_kernel_modules()"]
    ConflictingKernel --> ConflictingLibs["find_conflicting_files()"]
    ConflictingLibs --> ExistingFiles["find_existing_files()"]
    
    ExistingFiles --> CondenseList["condense_file_list()"]
    CondenseList --> AddBackups["Add BACKUP_CMD for conflicts"]
    AddBackups --> AddInitramfs["Add update_initramfs FUNCTION_CMD"]
    
    AddInitramfs --> AddInstalls["Add INSTALL_CMD for each file"]
    AddInstalls --> AddSymlinks["Add SYMLINK_CMD for links"]
    AddSymlinks --> AddPostProcessing["Add Post-processing Commands"]
    
    AddPostProcessing --> AddSystemCmds["Add ldconfig/depmod RUN_CMD"]
    AddSystemCmds --> ReturnList["Return CommandList*"]
```

Sources: [command-list.c:255-519]()

### Command Execution Engine

The command execution system processes each operation with progress tracking and error handling:

```mermaid
flowchart TD
    ExecuteStart["execute_command_list()"] --> BeginStatus["ui_status_begin()"]
    BeginStatus --> ProcessCmd["Process Each Command"]
    
    ProcessCmd --> CheckType{"Command Type?"}
    CheckType -->|INSTALL_CMD| InstallFile["install_file() + log_install_file()"]
    CheckType -->|BACKUP_CMD| BackupFile["do_backup()"]
    CheckType -->|RUN_CMD| RunCommand["execute_run_command()"]
    CheckType -->|SYMLINK_CMD| CreateSymlink["install_symlink() + log_create_symlink()"]
    CheckType -->|DELETE_CMD| DeleteFile["unlink()"]
    CheckType -->|TOUCH_CMD| TouchFile["utime()"]
    CheckType -->|FUNCTION_CMD| CallFunction["Execute function pointer"]
    
    InstallFile --> CheckError{"Error Occurred?"}
    BackupFile --> CheckError
    RunCommand --> CheckError
    CreateSymlink --> CheckError
    DeleteFile --> CheckError
    TouchFile --> CheckError
    CallFunction --> CheckError
    
    CheckError -->|Yes| ContinuePrompt["continue_after_error()"]
    CheckError -->|No| NextCommand{"More Commands?"}
    ContinuePrompt -->|Continue| NextCommand
    ContinuePrompt -->|Abort| ExecutionFailed["Return FALSE"]
    NextCommand -->|Yes| ProcessCmd
    NextCommand -->|No| ExecutionComplete["ui_status_end('done')"]
```

Sources: [command-list.c:614-731]()

## Integration with Backup System

The installation process is tightly integrated with the backup system to enable safe uninstallation and recovery from failed installations.

### Backup Integration Points

```mermaid
flowchart LR
    PreInstall["Pre-Installation"] --> InitBackup["init_backup()"]
    InitBackup --> CreateLog["Create backup log with version/description"]
    
    During["During Installation"] --> BackupConflicts["Backup conflicting files"]
    BackupConflicts --> LogInstalls["log_install_file() for new files"]
    LogInstalls --> LogSymlinks["log_create_symlink() for new links"]
    
    PostInstall["Post-Installation"] --> SanityCheck["check_installed_files_from_package()"]
    SanityCheck --> ValidateBackups["Verify backup integrity"]
    
    Uninstall["Uninstallation"] --> ReadBackupLog["read_backup_log_file()"]
    ReadBackupLog --> ValidateEntries["check_backup_log_entries()"]
    ValidateEntries --> RestoreFiles["Restore backed up files"]
    RestoreFiles --> RemoveInstalled["Remove installed files"]
```

Sources: [backup.c:137-198](), [backup.c:302-332](), [backup.c:336-362]()

### Command Types and Operations

The installer supports multiple command types for different installation operations:

| Command Type | Purpose | Key Functions |
|--------------|---------|---------------|
| `INSTALL_CMD` | Install files with permissions | `install_file()`, `log_install_file()` |
| `BACKUP_CMD` | Backup existing files | `do_backup()` |
| `RUN_CMD` | Execute system commands | `run_command()` |
| `SYMLINK_CMD` | Create symbolic links | `install_symlink()`, `log_create_symlink()` |
| `DELETE_CMD` | Delete temporary files | `unlink()` |
| `FUNCTION_CMD` | Execute internal functions | Function pointer calls |

Sources: [command-list.c:77-87](), [command-list.c:626-724]()

## Error Handling and Recovery

The installation process includes comprehensive error handling with user interaction for recovery decisions:

### Error Recovery Flow

```mermaid
flowchart TD
    ErrorOccurs["Error During Operation"] --> LogError["Log error details"]
    LogError --> ContinueCheck["continue_after_error()"]
    
    ContinueCheck --> UserChoice["ui_multiple_choice()"]
    UserChoice -->|Continue| ResumeInstall["Resume Installation"]
    UserChoice -->|Abort| CleanupFail["Cleanup and Fail"]
    
    ResumeInstall --> NextOperation["Continue with next operation"]
    CleanupFail --> RunFailedHook["run_distro_hook('failed-install')"]
    RunFailedHook --> ExitInstall["Exit with failure"]
    
    NextOperation --> CheckComplete{"Installation Complete?"}
    CheckComplete -->|Yes| Success["Installation Success"]
    CheckComplete -->|No| NextOperation
```

Sources: [misc.c:905-924](), [install-from-cwd.c:418-452]()

The installation process maintains transactional integrity through the backup system, allowing complete rollback of partial installations and providing detailed logging for troubleshooting failed installations.

---

