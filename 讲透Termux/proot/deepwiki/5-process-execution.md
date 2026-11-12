<!-- source: DeepWiki mcp.deepwiki.com · repo termux/proot · page 5 Process Execution · fetched 2026-10-26 -->

# Process Execution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/execve/enter.c](src/execve/enter.c)
- [src/execve/exit.c](src/execve/exit.c)

</details>



This document covers how PRoot handles process execution, focusing on the interception and translation of `execve` system calls. This includes ELF binary analysis, cross-architecture execution through QEMU, and the loader system integration.

For detailed information about the loader system implementation, see [Loader System](#5.2). For information about execve-specific handling, see [execve Handling](#5.1). For general system call interception mechanisms, see [System Call Interception](#3.2).

## Overview

Process execution in PRoot involves intercepting `execve` system calls and performing several key transformations:

1. **Path Translation**: Converting guest paths to host paths while validating executability
2. **ELF Analysis**: Parsing executable and interpreter information to understand memory requirements  
3. **Cross-Architecture Support**: Injecting QEMU for foreign binary execution
4. **Loader Injection**: Replacing the target executable with PRoot's custom loader
5. **Load Script Transfer**: Providing the loader with instructions to properly load the original binary

```mermaid
flowchart TD
    ExecveCall["execve() System Call"] --> EnterPhase["translate_execve_enter()"]
    EnterPhase --> PathCheck["translate_and_check_exec()"]
    PathCheck --> ShebangExpand["expand_shebang()"]
    ShebangExpand --> ELFExtract["extract_load_info()"]
    ELFExtract --> QEMUCheck{"QEMU needed?"}
    
    QEMUCheck -->|Yes| ExpandRunner["expand_runner()"]
    QEMUCheck -->|No| LoaderSetup["Setup Loader"]
    ExpandRunner --> LoaderSetup
    
    LoaderSetup --> ExecveExit["Kernel execve()"]
    ExecveExit --> ExitPhase["translate_execve_exit()"]
    ExitPhase --> LoadScript["transfer_load_script()"]
    LoadScript --> AuxVectors["bind_proc_pid_auxv()"]
    AuxVectors --> ProgramStart["Program Execution"]
```

Sources: [src/execve/enter.c:595-721](), [src/execve/exit.c:398-493]()

## execve System Call Interception

The core of process execution handling occurs in two phases during `execve` system call processing:

### Enter Phase Processing

The `translate_execve_enter()` function handles the syscall entry phase:

| Step | Function | Purpose |
|------|----------|---------|
| Path Resolution | `translate_and_check_exec()` | Convert guest path to host path and validate |
| Shebang Processing | `expand_shebang()` | Handle script interpreters and #! lines |
| ELF Analysis | `extract_load_info()` | Parse binary and interpreter information |
| QEMU Integration | `expand_runner()` | Inject QEMU for cross-architecture execution |
| Loader Setup | `get_loader_path()` | Replace target with PRoot loader |

```mermaid
graph LR
    subgraph "Key Functions"
        TranslateExecve["translate_execve_enter()"]
        TranslateCheck["translate_and_check_exec()"]
        ExtractInfo["extract_load_info()"]
        ExpandRunner["expand_runner()"]
        GetLoader["get_loader_path()"]
    end
    
    subgraph "Data Structures"
        LoadInfo["LoadInfo"]
        Tracee["Tracee"]
        Mapping["Mapping[]"]
        ElfHeader["ElfHeader"]
    end
    
    TranslateExecve --> TranslateCheck
    TranslateExecve --> ExtractInfo
    TranslateExecve --> ExpandRunner
    TranslateExecve --> GetLoader
    
    ExtractInfo --> LoadInfo
    LoadInfo --> Mapping
    LoadInfo --> ElfHeader
    ExtractInfo --> Tracee
```

Sources: [src/execve/enter.c:595-721](), [src/execve/enter.c:131-156](), [src/execve/enter.c:272-306]()

### Exit Phase Processing  

The `translate_execve_exit()` function handles post-execution setup:

- **Load Script Transfer**: Converts `LoadInfo` data into executable instructions for the loader
- **Auxiliary Vector Management**: Creates `/proc/pid/auxv` bindings with correct ELF metadata
- **Register State**: Sets up proper register values for program startup
- **Ptrace Coordination**: Handles interactions with external ptrace users (like GDB)

Sources: [src/execve/exit.c:398-493](), [src/execve/exit.c:174-390]()

## ELF Binary Analysis

PRoot performs comprehensive ELF analysis to understand how to load binaries and their interpreters:

### Load Information Extraction

The `extract_load_info()` function parses ELF headers and program headers to build memory mapping requirements:

```mermaid
graph TD
    ELFFile["ELF Binary"] --> OpenELF["open_elf()"]
    OpenELF --> IterateHeaders["iterate_program_headers()"]
    IterateHeaders --> PTLoad["PT_LOAD Segments"]
    IterateHeaders --> PTInterp["PT_INTERP Segments"]
    IterateHeaders --> PTStack["PT_GNU_STACK"]
    
    PTLoad --> AddMapping["add_mapping()"]
    PTInterp --> AddInterp["add_interp()"]
    
    AddMapping --> MappingArray["Mapping[]"]
    AddInterp --> InterpLoadInfo["LoadInfo.interp"]
    
    subgraph "Mapping Structure"
        MappingStruct["fd, offset, addr, length, flags, prot, clear_length"]
    end
    
    MappingArray --> MappingStruct
```

Sources: [src/execve/enter.c:272-306](), [src/execve/enter.c:56-124](), [src/execve/enter.c:163-221]()

### Address Space Layout

The `compute_load_addresses()` function determines final load addresses for position-independent executables:

- **Executable Base**: Uses `EXEC_PIC_ADDRESS` (64-bit) or `EXEC_PIC_ADDRESS_32` (32-bit)
- **Interpreter Base**: Uses `INTERP_PIC_ADDRESS` (64-bit) or `INTERP_PIC_ADDRESS_32` (32-bit)  
- **Fixed Executables**: Load at addresses specified in ELF headers

Sources: [src/execve/enter.c:332-357]()

## Cross-Architecture Execution (QEMU)

When executing foreign binaries, PRoot integrates with QEMU to provide cross-architecture support:

### QEMU Runner Expansion

The `expand_runner()` function transforms the argument vector to inject QEMU:

```mermaid
sequenceDiagram
    participant Original as "Original execve"
    participant PRoot as "PRoot"
    participant QEMU as "QEMU Process"
    participant Target as "Target Binary"
    
    Original->>PRoot: "execve('/bin/true', ['true'], env)"
    PRoot->>PRoot: "Detect foreign binary"
    PRoot->>PRoot: "expand_runner()"
    Note over PRoot: "Transform to QEMU execution"
    PRoot->>QEMU: "execve('/usr/bin/qemu-arm', ['qemu-arm', '-cpu', 'cortex-a9', '-0', 'true', '/bin/true'], env)"
    QEMU->>Target: "Load and execute target"
```

### QEMU Integration Details

| Component | Purpose |
|-----------|---------|
| `tracee->qemu[]` | Array of QEMU command and arguments |
| `-0` option | Sets argv[0] for the emulated program |
| `LD_` passthrough | Prevents host linker variables from affecting QEMU |
| `HOST_ROOTFS` prefix | Provides access to host filesystem for QEMU |

Sources: [src/execve/enter.c:367-468](), [src/execve/enter.c:390-454]()

## Load Script Generation and Transfer

The loader system requires detailed instructions about how to load the original binary. This is accomplished through load scripts:

### Load Script Structure

Load scripts contain a sequence of statements that the loader executes:

```mermaid
graph TD
    subgraph "Load Script Structure"
        OpenStmt["LOAD_ACTION_OPEN<br/>Open main binary"]
        MmapFile["LOAD_ACTION_MMAP_FILE<br/>Map file segments"]
        MmapAnon["LOAD_ACTION_MMAP_ANON<br/>Map anonymous segments"]
        OpenNext["LOAD_ACTION_OPEN_NEXT<br/>Open interpreter"]
        MmapInterp["LOAD_ACTION_MMAP_*<br/>Map interpreter"]
        StackExec["LOAD_ACTION_MAKE_STACK_EXEC<br/>Make stack executable"]
        Start["LOAD_ACTION_START<br/>Begin execution"]
    end
    
    OpenStmt --> MmapFile
    MmapFile --> MmapAnon
    MmapAnon --> OpenNext
    OpenNext --> MmapInterp
    MmapInterp --> StackExec
    StackExec --> Start
```

### Script Transfer Process

The `transfer_load_script()` function:

1. **Calculates sizes** for script statements and string storage
2. **Generates statements** from `LoadInfo` mappings using `transcript_mappings()`
3. **Embeds metadata** including entry points and auxiliary vector data
4. **Transfers to tracee** memory below the stack pointer
5. **Updates registers** to point the loader to the script

Sources: [src/execve/exit.c:174-390](), [src/execve/exit.c:144-168]()

## Auxiliary Vector Management

PRoot maintains proper ELF auxiliary vectors for program startup:

### Auxiliary Vector Binding

The `bind_proc_pid_auxv()` function creates a temporary file containing proper auxiliary vectors and binds it to `/proc/pid/auxv`:

```mermaid
graph LR
    TraceeMemory["Tracee Memory"] --> GetVectors["get_elf_aux_vectors_address()"]
    GetVectors --> FetchVectors["fetch_elf_aux_vectors()"]
    FetchVectors --> TempFile["create_temp_file()"]
    TempFile --> FillFile["fill_file_with_auxv()"]
    FillFile --> CreateBinding["insort_binding3()"]
    CreateBinding --> ProcAuxv["/proc/pid/auxv"]
```

This ensures that programs reading their auxiliary vectors (like GDB or dynamic linkers) receive correct ELF metadata rather than information about PRoot's loader.

Sources: [src/execve/exit.c:89-138](), [src/execve/exit.c:50-83]()

## Process State Management

Process execution involves significant state transitions:

### Loader Coordination

- **`ignore_loader_syscalls`**: Masks loader syscalls from external ptracers during loading
- **`NOTIFICATION_PTRACED_LOAD_DONE`**: Special execve used by loader to signal completion  
- **Register restoration**: Proper startup state for the loaded program

### Memory Management

- **Heap reset**: New processes start with clean heap state  
- **Stack pointer adjustment**: Loader script placed below initial stack
- **Executable path tracking**: Updates `tracee->exe` and `tracee->new_exe`

Sources: [src/execve/exit.c:403-459](), [src/execve/enter.c:604-612](), [src/execve/exit.c:476-484]()

---

