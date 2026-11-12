<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-installer · page 8 Specialized Components · fetched 2026-10-26 -->

# Specialized Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [command-list.h](command-list.h)
- [conflicting-kernel-modules.c](conflicting-kernel-modules.c)
- [mkprecompiled.c](mkprecompiled.c)
- [precompiled.c](precompiled.c)
- [precompiled.h](precompiled.h)

</details>



This document covers specialized subsystems within the nvidia-installer that handle specific aspects of driver installation but operate independently from the main installation workflow. These components provide critical support functions including conflict detection, precompiled package management, and command execution infrastructure.

For information about the core installation workflow, see [Installation Process](#3). For details about the main kernel module management system, see [Kernel Module Management](#3.3).

## Conflicting Kernel Modules Management

The installer maintains a comprehensive system for detecting and managing kernel modules that conflict with NVIDIA driver installation. This system ensures clean installation by identifying modules that must be unloaded before proceeding.

### Module Conflict Detection

The conflict detection system relies on a statically defined list of known conflicting modules organized in reverse dependency order to enable safe unloading.

```mermaid
graph TB
    subgraph "Conflict Detection System"
        ModuleList["conflicting_kernel_modules[]<br/>Static module list"]
        NumModules["num_conflicting_kernel_modules<br/>Array length"]
        
        ModuleList --> CheckProcess["Module Check Process"]
        NumModules --> CheckProcess
        
        CheckProcess --> UnloadOrder["Reverse Dependency Order<br/>Safe unloading sequence"]
    end
    
    subgraph "Conflicting Modules"
        PeerMem["nv_peer_mem<br/>nvidia-peermem"]
        VGPU["nvidia-vgpu-vfio"]
        UVM["nvidia-uvm"]
        Display["nvidia-drm<br/>nvidia-modeset"]
        Core["nvidia<br/>nvidia0-7"]
        Legacy["nvidia-frontend<br/>nvidia-kutils"]
        Coverage["libcov-lkm<br/>(BULLSEYE_BUILD only)"]
        
        PeerMem --> VGPU
        VGPU --> UVM
        UVM --> Display
        Display --> Core
        Core --> Legacy
        Legacy --> Coverage
    end
    
    UnloadOrder --> PeerMem
```

**Sources:** [conflicting-kernel-modules.c:29-46]()

### Module List Structure

The conflicting modules are organized in a specific order that allows safe sequential unloading:

| Module Category | Modules | Purpose |
|----------------|---------|---------|
| Peer Memory | `nv_peer_mem`, `nvidia-peermem` | GPU peer-to-peer memory access |
| Virtualization | `nvidia-vgpu-vfio` | Virtual GPU support |
| Unified Memory | `nvidia-uvm` | CUDA Unified Virtual Memory |
| Display Stack | `nvidia-drm`, `nvidia-modeset` | Display and modesetting |
| Core Driver | `nvidia`, `nvidia0-7` | Primary driver modules |
| Legacy Components | `nvidia-frontend`, `nvidia-kutils` | Older interface components |
| Debug Coverage | `libcov-lkm` | Code coverage (debug builds only) |

**Sources:** [conflicting-kernel-modules.c:29-44]()

## Precompiled Package System

The precompiled package system manages kernel interfaces and modules that have been pre-built for specific kernel versions, eliminating the need for on-target compilation in many cases.

### Package Format Architecture

```mermaid
graph TB
    subgraph "PrecompiledInfo Structure"
        Info["PrecompiledInfo"]
        Info --> PackageSize["package_size<br/>Total package bytes"]
        Info --> Version["version<br/>Driver version string"]
        Info --> ProcVersion["proc_version_string<br/>Kernel version"]
        Info --> Description["description<br/>Human readable info"]
        Info --> NumFiles["num_files<br/>File count"]
        Info --> Files["files[]<br/>PrecompiledFileInfo array"]
    end
    
    subgraph "PrecompiledFileInfo Structure"
        FileInfo["PrecompiledFileInfo"]
        FileInfo --> Type["type<br/>INTERFACE/MODULE"]
        FileInfo --> Attributes["attributes<br/>Signature flags"]
        FileInfo --> Name["name<br/>Filename"]
        FileInfo --> LinkedModule["linked_module_name<br/>Target module"]
        FileInfo --> CoreObject["core_object_name<br/>Core object file"]
        FileInfo --> TargetDir["target_directory<br/>Install path"]
        FileInfo --> CRC["crc<br/>File checksum"]
        FileInfo --> Size["size<br/>File size in bytes"]
        FileInfo --> Data["data<br/>Raw file content"]
        FileInfo --> Signature["signature<br/>Detached signature"]
    end
    
    Files --> FileInfo
```

**Sources:** [precompiled.h:151-160](), [precompiled.h:136-149]()

### Package Processing Pipeline

The precompiled system implements a complete pipeline for reading, validating, and extracting precompiled packages:

```mermaid
flowchart TD
    PackageFile["Package File<br/>.run format"] --> GetInfo["get_precompiled_info()"]
    
    GetInfo --> ValidateHeader["Validate Package Header<br/>PRECOMPILED_PKG_HEADER"]
    ValidateHeader --> CheckVersion["Check Format Version<br/>PRECOMPILED_PKG_VERSION"]
    CheckVersion --> ReadMetadata["Read Package Metadata<br/>version, description, proc_version"]
    
    ReadMetadata --> VersionMatch{"Kernel Version<br/>Match?"}
    VersionMatch -->|No| Reject["Package Rejected"]
    VersionMatch -->|Yes| ReadFiles["Read File Entries<br/>precompiled_read_fileinfo()"]
    
    ReadFiles --> ValidateCRC["Validate File CRCs<br/>compute_crc_from_buffer()"]
    ValidateCRC --> UnpackFiles["Unpack Files<br/>precompiled_file_unpack()"]
    
    UnpackFiles --> InstallTarget["Target Installation<br/>Directory"]
```

**Sources:** [precompiled.c:152-360](), [precompiled.c:367-419](), [precompiled.c:760-879]()

### File Type Management

The system supports two primary file types with different handling requirements:

| File Type | Constant | Description | Required Metadata |
|-----------|----------|-------------|-------------------|
| Interface | `PRECOMPILED_FILE_TYPE_INTERFACE` | Kernel interface objects requiring linking | `linked_module_name`, `core_object_name` |
| Module | `PRECOMPILED_FILE_TYPE_MODULE` | Complete kernel modules | None (self-contained) |

**Sources:** [precompiled.h:123-126]()

### Signature and Validation System

```mermaid
graph LR
    subgraph "File Attributes"
        DetachedSig["PRECOMPILED_ATTR<br/>(DETACHED_SIGNATURE)"]
        LinkedCRC["PRECOMPILED_ATTR<br/>(LINKED_MODULE_CRC)"]
        EmbeddedSig["PRECOMPILED_ATTR<br/>(EMBEDDED_SIGNATURE)"]
    end
    
    subgraph "Validation Process"
        CRCCheck["CRC Validation<br/>compute_crc_from_buffer()"]
        SigVerify["Signature Verification<br/>detached/embedded"]
        LinkedCheck["Linked Module Check<br/>linked_module_crc"]
    end
    
    DetachedSig --> SigVerify
    LinkedCRC --> LinkedCheck
    EmbeddedSig --> SigVerify
    
    CRCCheck --> ValidationResult["Validation Result"]
    SigVerify --> ValidationResult
    LinkedCheck --> ValidationResult
```

**Sources:** [precompiled.h:128-134](), [precompiled.c:826-851]()

## Command List Infrastructure

The command list system provides a structured approach to batching and executing installation operations with proper error handling and rollback capabilities.

### Command List Structure

```mermaid
graph TB
    subgraph "CommandList Structure"
        CmdList["CommandList"]
        CmdList --> NumCommands["num<br/>Command count"]
        CmdList --> Descriptions["descriptions[]<br/>Human readable descriptions"]
        CmdList --> Commands["cmds[]<br/>Opaque command structures"]
    end
    
    subgraph "FileList Structure"
        FileList["FileList"]
        FileList --> NumFiles["num<br/>File count"]
        FileList --> Filenames["filename[]<br/>File path array"]
    end
    
    subgraph "Command Processing"
        BuildList["build_command_list()<br/>Package → CommandList"]
        ExecuteList["execute_command_list()<br/>CommandList → System"]
        FreeList["free_command_list()<br/>Cleanup"]
        
        BuildList --> ExecuteList
        ExecuteList --> FreeList
    end
    
    CmdList --> BuildList
    FileList --> BuildList
```

**Sources:** [command-list.h:29-44](), [command-list.h:46-49]()

## Precompiled Package Utilities

The `mkprecompiled` utility provides comprehensive tools for creating, inspecting, and manipulating precompiled kernel interface packages outside of the main installer.

### Utility Operations

```mermaid
flowchart TD
    subgraph "mkprecompiled Actions"
        Pack["--pack<br/>Create/update packages"]
        Unpack["--unpack<br/>Extract package contents"]
        Info["--info<br/>Display package metadata"]
        Match["--match<br/>Check kernel compatibility"]
    end
    
    subgraph "Pack Operation Pipeline"
        PackFiles["File Input<br/>--kernel-interface<br/>--kernel-module"]
        PackMeta["Metadata<br/>--driver-version<br/>--description<br/>--proc-version-string"]
        PackProcess["precompiled_pack()<br/>Binary package creation"]
        
        PackFiles --> PackProcess
        PackMeta --> PackProcess
    end
    
    subgraph "Unpack Operation Pipeline"
        UnpackInput["Package File"]
        UnpackOutput["--output-directory<br/>Target extraction path"]
        UnpackProcess["precompiled_unpack()<br/>File extraction"]
        
        UnpackInput --> UnpackProcess
        UnpackOutput --> UnpackProcess
    end
    
    Pack --> PackProcess
    Unpack --> UnpackProcess
    Info --> InfoDisplay["Package Information<br/>version, files, checksums"]
    Match --> VersionCheck["Kernel Version Check<br/>read_proc_version()"]
```

**Sources:** [mkprecompiled.c:48-54](), [mkprecompiled.c:429-433](), [mkprecompiled.c:604-702]()

### Package Creation Workflow

The utility supports creating packages with both kernel interfaces and complete modules:

| Component Type | Required Options | Optional Features |
|----------------|------------------|-------------------|
| Kernel Interface | `--kernel-interface`, `--linked-module-name`, `--core-object-name` | `--linked-module`, `--signed-module` (for detached signatures) |
| Kernel Module | `--kernel-module` | `--signed` (for embedded signatures) |

**Sources:** [mkprecompiled.c:150-187](), [mkprecompiled.c:320-343]()

### Version and Compatibility Management

```mermaid
graph LR
    subgraph "Version Information Sources"
        DriverVersion["--driver-version<br/>Package version"]
        ProcVersion["--proc-version-string<br/>Kernel version"]
        ProcMount["--proc-mount-point<br/>Proc filesystem location"]
        Description["--description<br/>Human readable info"]
    end
    
    subgraph "Compatibility Checking"
        CurrentKernel["read_proc_version()<br/>Current system kernel"]
        PackageKernel["Package proc_version_string"]
        MatchCheck["check_match()<br/>String comparison"]
        
        CurrentKernel --> MatchCheck
        PackageKernel --> MatchCheck
    end
    
    ProcVersion --> PackageKernel
    ProcMount --> CurrentKernel
    MatchCheck --> Result["Match Result<br/>Compatible/Incompatible"]
```

**Sources:** [mkprecompiled.c:82-142](), [mkprecompiled.c:568-585]()