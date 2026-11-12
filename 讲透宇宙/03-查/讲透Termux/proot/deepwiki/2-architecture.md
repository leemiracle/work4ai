<!-- source: DeepWiki mcp.deepwiki.com · repo termux/proot · page 2 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/extension/extension.h](src/extension/extension.h)
- [src/tracee/event.c](src/tracee/event.c)
- [src/tracee/tracee.h](src/tracee/tracee.h)

</details>



This document explains PRoot's overall system architecture, including the tracer-tracee model, event-driven processing, and modular extension system. It covers the fundamental design patterns and core components that enable PRoot to provide user-space process virtualization.

For details on specific core systems like process management and syscall interception, see [Core Systems](#3). For information about individual extensions, see [Extension System](#4).

## Overview

PRoot implements a user-space process virtualization system using a tracer-tracee architecture where PRoot acts as the tracer and monitored processes are tracees. The system intercepts system calls using ptrace and optional seccomp filters, translates them as needed, and manages a hierarchy of traced processes through an event-driven main loop.

### Core Architecture Components

```mermaid
graph TB
    subgraph "User Interface Layer"
        CLI["CLI Parser<br/>main()"]
        Config["Configuration<br/>parse_args()"]
    end
    
    subgraph "Core Engine"
        EventLoop["Event Loop<br/>event_loop()"]
        TraceeManager["Tracee Management<br/>get_tracee(), new_child()"]
        EventHandler["Event Handler<br/>handle_tracee_event()"]
    end
    
    subgraph "System Call Pipeline"
        SyscallTranslator["Syscall Translator<br/>translate_syscall()"]
        SeccompFilter["Seccomp Filter<br/>enable_syscall_filtering()"]
        ChainedSyscalls["Chained Syscalls<br/>struct chained_syscalls"]
    end
    
    subgraph "Extension Framework"
        ExtensionManager["Extension Manager<br/>notify_extensions()"]
        ExtensionCallbacks["Extension Callbacks<br/>extension_callback_t"]
        FilteredSysnums["Filtered Sysnums<br/>FilteredSysnum"]
    end
    
    subgraph "Memory & Process Control"
        ProcessLauncher["Process Launcher<br/>launch_process()"]
        MemoryAccess["Memory Access<br/>tracee/mem.h"]
        PtraceControl["Ptrace Control<br/>restart_tracee()"]
    end
    
    CLI --> Config
    Config --> EventLoop
    EventLoop --> TraceeManager
    EventLoop --> EventHandler
    
    EventHandler --> SyscallTranslator
    EventHandler --> SeccompFilter
    SyscallTranslator --> ChainedSyscalls
    
    EventHandler --> ExtensionManager
    ExtensionManager --> ExtensionCallbacks
    ExtensionCallbacks --> FilteredSysnums
    
    EventLoop --> ProcessLauncher
    EventHandler --> MemoryAccess
    EventHandler --> PtraceControl
```

Sources: [src/tracee/event.c:260-363](), [src/tracee/tracee.h:74-296](), [src/extension/extension.h:154-174]()

## Tracer-Tracee Model

PRoot operates on a fundamental tracer-tracee relationship where PRoot serves as the tracer for all monitored processes (tracees). Each tracee is represented by the `Tracee` struct, which maintains comprehensive process state.

### Tracee Structure and Lifecycle

```mermaid
graph LR
    subgraph "Tracee Lifecycle"
        CreateTracee["new_child()<br/>get_tracee()"]
        LaunchProcess["launch_process()<br/>fork() + PTRACE_TRACEME"]
        MonitorEvents["Event Loop<br/>waitpid() + handle_tracee_event()"]
        TerminateTracee["terminate_tracee()<br/>free_terminated_tracees()"]
    end
    
    subgraph "Tracee State Management"
        TraceeStruct["struct tracee<br/>pid, vpid, status"]
        ProcessRelations["Parent/Child Relations<br/>parent, clone, as_ptracer"]
        PtraceState["Ptrace State<br/>restart_how, running"]
        RegisterState["Register State<br/>user_regs_struct _regs[]"]
    end
    
    subgraph "Tracee Resources"
        FileSystem["FileSystemNameSpace *fs<br/>bindings, cwd"]
        VirtualHeap["Heap *heap<br/>base, size"]
        Extensions["Extensions *extensions<br/>LIST_HEAD"]
        MemoryContext["TALLOC_CTX<br/>ctx, life_context"]
    end
    
    CreateTracee --> LaunchProcess
    LaunchProcess --> MonitorEvents
    MonitorEvents --> TerminateTracee
    
    MonitorEvents --> TraceeStruct
    TraceeStruct --> ProcessRelations
    TraceeStruct --> PtraceState
    TraceeStruct --> RegisterState
    
    TraceeStruct --> FileSystem
    TraceeStruct --> VirtualHeap
    TraceeStruct --> Extensions
    TraceeStruct --> MemoryContext
```

The `Tracee` struct contains several categories of resources:
- **Private resources**: `pid`, `vpid`, `running`, `terminated`
- **Inherited resources**: `verbose`, `seccomp` state
- **Shared resources**: `fs` (file system namespace), `heap` (virtual heap)
- **Process relations**: `parent`, `clone`, ptrace emulation support

Sources: [src/tracee/tracee.h:74-296](), [src/tracee/event.c:59-115]()

## Event-Driven Processing

The core of PRoot's operation is the `event_loop()` function, which continuously monitors all tracees and dispatches events to appropriate handlers.

### Event Loop Flow

```mermaid
sequenceDiagram
    participant EventLoop as "event_loop()"
    participant System as "Linux Kernel"
    participant TraceeManager as "get_tracee()"
    participant EventHandler as "handle_tracee_event()"
    participant Extensions as "notify_extensions()"
    participant PtraceControl as "restart_tracee()"
    
    loop "Main Event Loop"
        EventLoop->>System: "waitpid(-1, &status, __WALL)"
        System-->>EventLoop: "pid + tracee_status"
        
        EventLoop->>TraceeManager: "get_tracee(NULL, pid, true)"
        TraceeManager-->>EventLoop: "Tracee *tracee"
        
        EventLoop->>Extensions: "notify_extensions(tracee, NEW_STATUS, status, 0)"
        Extensions-->>EventLoop: "status"
        
        EventLoop->>EventHandler: "handle_tracee_event(tracee, status)"
        EventHandler-->>EventLoop: "signal"
        
        EventLoop->>PtraceControl: "restart_tracee(tracee, signal)"
        PtraceControl-->>EventLoop: "success/failure"
    end
```

The event loop handles several types of events:
- **Process termination**: `WIFEXITED`, `WIFSIGNALED`
- **Signal stops**: `WIFSTOPPED` with various signals
- **Syscall traps**: `SIGTRAP | 0x80`, `PTRACE_EVENT_SECCOMP`
- **Process events**: `PTRACE_EVENT_FORK`, `PTRACE_EVENT_EXEC`, etc.

Sources: [src/tracee/event.c:260-363](), [src/tracee/event.c:370-689]()

## Extension Architecture

PRoot uses a modular extension system where extensions register callbacks for specific events and syscalls. Extensions can intercept and modify syscall processing at multiple stages.

### Extension System Structure

```mermaid
graph TB
    subgraph "Extension Registration"
        ExtensionStruct["struct extension<br/>callback, config, filtered_sysnums"]
        CallbackFunction["extension_callback_t<br/>callback(extension, event, data1, data2)"]
        FilteredSysnums["FilteredSysnum<br/>syscall numbers handled"]
    end
    
    subgraph "Extension Events"
        PathEvents["Path Events<br/>GUEST_PATH, HOST_PATH, TRANSLATED_PATH"]
        SyscallEvents["Syscall Events<br/>SYSCALL_ENTER_START/END<br/>SYSCALL_EXIT_START/END"]
        ProcessEvents["Process Events<br/>INHERIT_PARENT/CHILD<br/>NEW_STATUS"]
        SpecialEvents["Special Events<br/>SIGSYS_OCC, INITIALIZATION"]
    end
    
    subgraph "Extension Dispatch"
        NotifyExtensions["notify_extensions()<br/>LIST_FOREACH iteration"]
        EventRouter["Event Routing<br/>Per-extension callback"]
        ResultHandling["Result Handling<br/>status return codes"]
    end
    
    ExtensionStruct --> CallbackFunction
    ExtensionStruct --> FilteredSysnums
    
    CallbackFunction --> PathEvents
    CallbackFunction --> SyscallEvents
    CallbackFunction --> ProcessEvents
    CallbackFunction --> SpecialEvents
    
    NotifyExtensions --> EventRouter
    EventRouter --> ResultHandling
```

Extensions can return specific status codes to control PRoot's behavior:
- **< 0**: Report errno to tracee
- **== 0**: Continue normal processing  
- **> 0**: Skip PRoot's default handling

Key extension events include:
- `SYSCALL_ENTER_START`/`SYSCALL_ENTER_END`: Before/after syscall entry processing
- `SYSCALL_EXIT_START`/`SYSCALL_EXIT_END`: Before/after syscall exit processing
- `GUEST_PATH`/`HOST_PATH`/`TRANSLATED_PATH`: Path translation stages
- `SIGSYS_OCC`: Seccomp SIGSYS signal handling

Sources: [src/extension/extension.h:32-150](), [src/extension/extension.h:184-199]()

## System Call Interception

PRoot intercepts system calls using a combination of ptrace and seccomp filtering. The interception process varies depending on whether seccomp acceleration is enabled.

### Syscall Processing States

```mermaid
stateDiagram-v2
    [*] --> SysEnter: "SIGTRAP|0x80 or PTRACE_EVENT_SECCOMP"
    
    SysEnter --> TranslateSyscall: "translate_syscall()"
    TranslateSyscall --> HandleExtensions: "notify_extensions(SYSCALL_ENTER_*)"
    
    HandleExtensions --> SysExit: "Normal path"
    HandleExtensions --> ChainedSyscall: "Extension requests chaining"
    HandleExtensions --> SkipSyscall: "Extension handles completely"
    
    ChainedSyscall --> SysExit: "Chain complete"
    SysExit --> HandleExitExtensions: "notify_extensions(SYSCALL_EXIT_*)"
    
    HandleExitExtensions --> RestartTracee: "restart_tracee()"
    RestartTracee --> [*]: "PTRACE_CONT or PTRACE_SYSCALL"
    
    SkipSyscall --> RestartTracee: "Extension handled"
    
    state SysEnter {
        [*] --> CheckSeccomp
        CheckSeccomp --> SeccompEnabled: "seccomp == ENABLED"
        CheckSeccomp --> PtraceOnly: "seccomp == DISABLED"
        
        SeccompEnabled --> FastPath: "Can skip sysexit"
        SeccompEnabled --> SlowPath: "Must handle sysexit"
        
        FastPath --> [*]: "PTRACE_CONT"
        SlowPath --> [*]: "PTRACE_SYSCALL"
        PtraceOnly --> [*]: "PTRACE_SYSCALL"
    }
```

The syscall interception process involves:
1. **Entry detection**: Via `SIGTRAP | 0x80` or `PTRACE_EVENT_SECCOMP`
2. **Translation**: `translate_syscall()` modifies arguments if needed
3. **Extension notification**: Extensions can intercept and modify behavior
4. **Exit handling**: Process syscall results and notify extensions
5. **Restart**: Continue tracee with `PTRACE_CONT` or `PTRACE_SYSCALL`

Sources: [src/tracee/event.c:465-608](), [src/tracee/event.c:543-607]()

## Key Data Structures

The architecture relies on several key data structures that maintain system state:

| Structure | Purpose | Key Fields | Source File |
|-----------|---------|------------|-------------|
| `Tracee` | Process state | `pid`, `status`, `_regs[]`, `extensions` | [src/tracee/tracee.h:74-296]() |
| `Extension` | Extension definition | `callback`, `config`, `filtered_sysnums` | [src/extension/extension.h:158-172]() |
| `FileSystemNameSpace` | Path bindings | `bindings.{pending,guest,host}`, `cwd` | [src/tracee/tracee.h:50-65]() |
| `Heap` | Virtual heap | `base`, `size`, `disabled` | [src/tracee/tracee.h:67-72]() |

The `Tracee` struct uses a sophisticated resource management system with different sharing semantics:
- **Private resources**: Unique to each tracee
- **Inherited resources**: Copied from parent during fork/clone
- **Shared resources**: Shared between related tracees (CLONE_FS, CLONE_VM)
- **Read-only resources**: Immutable configuration data

Sources: [src/tracee/tracee.h:74-296](), [src/extension/extension.h:158-172]()

---

