<!-- source: DeepWiki mcp.deepwiki.com · repo termux/proot · page 3 Core Systems · fetched 2026-10-26 -->

# Core Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/syscall/chain.c](src/syscall/chain.c)
- [src/syscall/syscall.c](src/syscall/syscall.c)
- [src/syscall/syscall.h](src/syscall/syscall.h)
- [src/tracee/event.c](src/tracee/event.c)

</details>



This document provides an overview of the fundamental systems that make PRoot work: the event loop and process management, system call interception and translation, and memory management. These core systems work together to provide PRoot's user-space implementation of chroot, mount, and binfmt_misc functionality.

For detailed information about process lifecycle management, see [Process Management](#3.1). For comprehensive system call handling details, see [System Call Interception](#3.2). For memory access patterns and ptrace operations, see [Memory Management](#3.3). For the modular extension architecture, see [Extension System](#4).

## Architecture Overview

PRoot's core architecture centers around a tracer-tracee model where PRoot acts as the tracer monitoring and controlling one or more traced processes (tracees). The system operates through three primary interconnected systems:

```mermaid
graph TB
    subgraph "Core System Architecture"
        EventLoop["Event Loop System<br/>event_loop()"]
        ProcMgmt["Process Management<br/>launch_process()<br/>handle_tracee_event()"]
        SyscallPipeline["System Call Pipeline<br/>translate_syscall()"]
        MemMgmt["Memory Management<br/>read_path()<br/>write_data()"]
    end
    
    subgraph "Key Data Structures"
        Tracee["Tracee struct<br/>Process state & context"]
        ChainedSyscalls["chained_syscall struct<br/>Queued syscalls"]
        RegState["Register State<br/>ORIGINAL/CURRENT/MODIFIED"]
    end
    
    subgraph "External Interfaces"
        Ptrace["ptrace() system calls"]
        Extensions["Extension System<br/>notify_extensions()"]
        Kernel["Linux Kernel<br/>waitpid(), signals"]
    end
    
    EventLoop --> ProcMgmt
    ProcMgmt --> SyscallPipeline
    SyscallPipeline --> MemMgmt
    
    ProcMgmt --> Tracee
    SyscallPipeline --> ChainedSyscalls
    SyscallPipeline --> RegState
    
    EventLoop --> Kernel
    ProcMgmt --> Ptrace
    SyscallPipeline --> Extensions
    MemMgmt --> Ptrace
```

**Sources:** [src/tracee/event.c:260-363](), [src/syscall/syscall.c:103-274]()

## Event Loop System

The event loop system forms the heart of PRoot's operation, managing the lifecycle of traced processes and dispatching events. The system uses ptrace and waitpid to monitor tracee state changes and coordinates responses across all core systems.

```mermaid
graph TD
    subgraph "Event Loop Components"
        EventLoopMain["event_loop()<br/>[src/tracee/event.c:260]"]
        WaitPid["waitpid(-1, &tracee_status, __WALL)<br/>[src/tracee/event.c:333]"]
        GetTracee["get_tracee(NULL, pid, true)<br/>[src/tracee/event.c:343]"]
        HandleEvent["handle_tracee_event(tracee, tracee_status)<br/>[src/tracee/event.c:358]"]
        RestartTracee["restart_tracee(tracee, signal)<br/>[src/tracee/event.c:359]"]
    end
    
    subgraph "Process States"
        Running["tracee->running = true"]
        Stopped["tracee->running = false"]
        Terminated["terminate_tracee(tracee)"]
    end
    
    subgraph "Event Types"
        SigTrap["SIGTRAP | 0x80<br/>System call entry/exit"]
        SigSeccomp["SIGTRAP | PTRACE_EVENT_SECCOMP<br/>Seccomp filter event"]
        SigSys["SIGSYS<br/>Seccomp blocked syscall"]
        ProcessEvents["PTRACE_EVENT_FORK/CLONE/EXEC"]
    end
    
    EventLoopMain --> WaitPid
    WaitPid --> GetTracee
    GetTracee --> HandleEvent
    HandleEvent --> RestartTracee
    
    HandleEvent --> SigTrap
    HandleEvent --> SigSeccomp  
    HandleEvent --> SigSys
    HandleEvent --> ProcessEvents
    
    RestartTracee --> Running
    WaitPid --> Stopped
    HandleEvent --> Terminated
```

**Sources:** [src/tracee/event.c:323-362](), [src/tracee/event.c:370-689](), [src/tracee/event.c:706-726]()

The event loop manages signal handling, tracee termination cleanup, and coordinates with the extension system through `notify_extensions()` calls. It handles both normal ptrace stops and seccomp-accelerated events when available.

## System Call Processing Pipeline

The system call processing pipeline handles the interception, translation, and execution control of system calls made by traced processes. This pipeline supports both immediate translation and chained syscall execution for complex operations.

```mermaid
graph TB
    subgraph "Syscall Translation Pipeline"
        TranslateSyscall["translate_syscall(tracee)<br/>[src/syscall/syscall.c:103]"]
        IsEnterStage["IS_IN_SYSENTER(tracee)<br/>Check if syscall entry"]
        FetchRegs["fetch_regs(tracee)<br/>Get register state"]
    end
    
    subgraph "Enter Stage Processing"
        SaveOriginal["save_current_regs(tracee, ORIGINAL)"]
        TranslateEnter["translate_syscall_enter(tracee)"]
        SaveModified["save_current_regs(tracee, MODIFIED)"]
        SetVoid["set_sysnum(tracee, PR_void)<br/>Cancel syscall on error"]
    end
    
    subgraph "Exit Stage Processing"  
        TranslateExit["translate_syscall_exit(tracee)"]
        RestoreRegs["restore_original_regs = true"]
    end
    
    subgraph "Syscall Chaining"
        ChainCheck["tracee->chain.syscalls != NULL"]
        RegisterChained["register_chained_syscall()<br/>[src/syscall/chain.c:87]"]
        ChainNext["chain_next_syscall(tracee)<br/>[src/syscall/chain.c:103]"]
        ChainedSyscallStruct["struct chained_syscall<br/>sysnum + sysargs[6]"]
    end
    
    TranslateSyscall --> IsEnterStage
    IsEnterStage --> FetchRegs
    
    FetchRegs --> SaveOriginal
    SaveOriginal --> TranslateEnter
    TranslateEnter --> SaveModified
    SaveModified --> SetVoid
    
    FetchRegs --> TranslateExit
    TranslateExit --> RestoreRegs
    
    TranslateEnter --> ChainCheck
    TranslateExit --> ChainNext
    ChainNext --> ChainedSyscallStruct
    RegisterChained --> ChainedSyscallStruct
```

**Sources:** [src/syscall/syscall.c:103-274](), [src/syscall/chain.c:35-195]()

The pipeline maintains three register snapshots (ORIGINAL, CURRENT, MODIFIED) to support complex syscall transformations and rollback capabilities. The chaining mechanism allows single logical operations to be implemented as sequences of kernel syscalls.

## Memory Management Integration

Memory management provides the foundation for syscall argument translation by enabling PRoot to read from and write to tracee memory space. This system bridges the gap between PRoot's address space and the tracee's address space.

```mermaid
graph LR
    subgraph "Memory Operations"
        GetSysargPath["get_sysarg_path(tracee, path, reg)<br/>[src/syscall/syscall.c:42]"]
        SetSysargPath["set_sysarg_path(tracee, path, reg)<br/>[src/syscall/syscall.c:98]"]
        SetSysargData["set_sysarg_data(tracee, ptr, size, reg)<br/>[src/syscall/syscall.c:72]"]
    end
    
    subgraph "Low-level Memory Access"
        ReadPath["read_path(tracee, path, src)<br/>Read string from tracee"]
        WriteData["write_data(tracee, dest, src, size)<br/>Write data to tracee"]
        AllocMem["alloc_mem(tracee, size)<br/>Allocate tracee memory"]
    end
    
    subgraph "Register Interface"
        PeekReg["peek_reg(tracee, version, reg)<br/>Read tracee register"]
        PokeReg["poke_reg(tracee, reg, value)<br/>Write tracee register"]
        RegVersions["ORIGINAL/CURRENT/MODIFIED<br/>Register state snapshots"]
    end
    
    GetSysargPath --> ReadPath
    SetSysargPath --> WriteData
    SetSysargPath --> AllocMem
    SetSysargData --> WriteData
    SetSysargData --> AllocMem
    
    GetSysargPath --> PeekReg
    SetSysargPath --> PokeReg
    SetSysargData --> PokeReg
    
    PeekReg --> RegVersions
    PokeReg --> RegVersions
```

**Sources:** [src/syscall/syscall.c:42-101](), [src/tracee/reg.h](), [src/tracee/mem.h]()

## Inter-System Communication

The core systems communicate through well-defined interfaces and shared data structures. The `Tracee` structure serves as the central context object that maintains state across all systems.

| System | Primary Interface | Key Data Structures | Communication Pattern |
|--------|------------------|-------------------|---------------------|
| Event Loop | `handle_tracee_event()` | `tracee->status`, `tracee->restart_how` | Event-driven dispatch |
| Syscall Pipeline | `translate_syscall()` | `tracee->chain`, register snapshots | Synchronous processing |
| Memory Management | `get_sysarg_*()`, `set_sysarg_*()` | Memory allocation tracking | On-demand access |
| Extension System | `notify_extensions()` | Extension-specific data | Observer pattern |

The systems coordinate through the tracee's execution state, with the event loop orchestrating the overall flow while syscall processing and memory management handle the detailed transformations required for transparent process virtualization.

**Sources:** [src/tracee/event.c:370-689](), [src/syscall/syscall.c:103-274](), [src/extension/extension.h]()

---

