<!-- source: DeepWiki mcp.deepwiki.com · repo termux/proot · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/GNUmakefile](src/GNUmakefile)
- [src/cli/cli.c](src/cli/cli.c)
- [src/extension/mountinfo/mountinfo.c](src/extension/mountinfo/mountinfo.c)
- [src/tracee/event.c](src/tracee/event.c)

</details>



This document provides a high-level overview of PRoot, a user-space implementation of `chroot`, `mount --bind`, and `binfmt_misc`. PRoot enables users to execute programs in a fake root environment without requiring administrator privileges, using Linux's `ptrace` system call to intercept and translate system calls from traced processes.

For detailed information about specific subsystems, see [Architecture](#2) for the overall system design, [Core Systems](#3) for fundamental components like process management and system call interception, and [Extension System](#4) for modular functionality.

## What is PRoot

PRoot is a ptrace-based process virtualization tool that creates an isolated execution environment by intercepting and translating system calls. It allows programs to run with a different view of the filesystem hierarchy, emulated root privileges, and modified system behavior without requiring kernel modifications or root access.

The core functionality includes:
- **Filesystem virtualization**: Redirecting file system paths through binding mechanisms
- **Process tracing**: Using `ptrace` to monitor and modify system call behavior  
- **Privilege emulation**: Simulating root user capabilities for compatibility
- **Binary execution**: Supporting cross-architecture execution through QEMU integration

Sources: [src/cli/cli.c:1-50](), [src/tracee/event.c:1-50]()

## System Architecture

```mermaid
graph TB
    CLI["CLI Interface<br/>cli/cli.c<br/>cli/proot.c"]
    EventLoop["Event Loop<br/>tracee/event.c<br/>event_loop()"]
    Tracee["Process Management<br/>tracee/tracee.c<br/>Tracee struct"]
    
    subgraph "System Call Processing"
        SyscallEnter["Syscall Enter<br/>syscall/enter.c<br/>translate_syscall_enter()"]
        SyscallExit["Syscall Exit<br/>syscall/exit.c<br/>translate_syscall_exit()"]
        Seccomp["Seccomp Filter<br/>syscall/seccomp.c<br/>enable_syscall_filtering()"]
    end
    
    subgraph "Extension Framework"
        ExtCore["Extension Core<br/>extension/extension.c<br/>notify_extensions()"]
        SysVIPC["sysvipc Extension<br/>extension/sysvipc/sysvipc.c"]
        FakeID["fake_id0 Extension<br/>extension/fake_id0/fake_id0.c"]
        Link2Sym["link2symlink Extension<br/>extension/link2symlink/link2symlink.c"]
    end
    
    subgraph "Supporting Systems"
        PathSystem["Path Translation<br/>path/path.c<br/>translate_path()"]
        MemSystem["Memory Access<br/>tracee/mem.c<br/>read_data(), write_data()"]
        LoaderSystem["Loader System<br/>loader/loader.c"]
    end
    
    CLI --> EventLoop
    EventLoop --> Tracee
    Tracee --> SyscallEnter
    SyscallEnter --> SyscallExit
    Seccomp --> SyscallEnter
    
    SyscallEnter --> ExtCore
    SyscallExit --> ExtCore
    ExtCore --> SysVIPC
    ExtCore --> FakeID
    ExtCore --> Link2Sym
    
    SyscallEnter --> PathSystem
    SyscallEnter --> MemSystem
    SyscallExit --> LoaderSystem
```

The architecture follows a tracer-tracee model where PRoot acts as the tracer, monitoring one or more child processes (tracees). The `event_loop()` function in `tracee/event.c` serves as the central dispatcher, handling ptrace events and coordinating between system call interception, extension processing, and tracee management.

Sources: [src/tracee/event.c:260-363](), [src/cli/cli.c:448-506](), [src/GNUmakefile:21-86]()

## Core Components

### Process Launching and Tracing

```mermaid
sequenceDiagram
    participant Main as "main()<br/>cli/cli.c"
    participant Launch as "launch_process()<br/>tracee/event.c"
    participant Child as "Child Process"
    participant Loop as "event_loop()<br/>tracee/event.c"
    
    Main->>Launch: "launch_process(tracee, argv)"
    Launch->>Child: "fork() + ptrace(PTRACE_TRACEME)"
    Child->>Child: "enable_syscall_filtering()"
    Child->>Child: "execvp(tracee->exe, argv)"
    Launch->>Loop: "Start event loop"
    Loop->>Loop: "waitpid() + handle_tracee_event()"
```

The process begins with `main()` parsing command-line arguments and calling `launch_process()` to create the first traced process. The child process enables seccomp filtering for performance and executes the target program, while the parent enters the main event loop.

Sources: [src/cli/cli.c:488-495](), [src/tracee/event.c:59-115](), [src/tracee/event.c:260-363]()

### System Call Interception Flow

PRoot intercepts system calls through multiple mechanisms depending on the available kernel features:

| Method | Performance | Completeness | Code Location |
|--------|-------------|--------------|---------------|
| seccomp + ptrace | High | Complete | [syscall/seccomp.c]() |
| ptrace only | Medium | Complete | [tracee/event.c:465-541]() |

The `handle_tracee_event()` function processes different types of ptrace stops, including `SIGTRAP \| 0x80` for system calls and `SIGTRAP \| PTRACE_EVENT_SECCOMP` for seccomp-filtered calls.

Sources: [src/tracee/event.c:370-689](), [src/syscall/seccomp.c]()

## Extension System

```mermaid
graph LR
    subgraph "Extension Events"
        Init["INITIALIZATION"]
        SysEnter["SYSCALL_ENTER_*"]
        SysExit["SYSCALL_EXIT_*"]
        PathTranslate["TRANSLATED_PATH"]
    end
    
    subgraph "Core Extensions"
        SysVIPC["sysvipc<br/>System V IPC Emulation<br/>36.39 importance score"]
        FakeID["fake_id0<br/>Root Privilege Emulation<br/>29.42 importance score"]  
        Link2Sym["link2symlink<br/>Hard Link Conversion<br/>28.74 importance score"]
        MountInfo["mountinfo<br/>Mount Info Translation<br/>4.00 importance score"]
    end
    
    NotifyExt["notify_extensions()<br/>extension/extension.c"]
    
    Init --> NotifyExt
    SysEnter --> NotifyExt
    SysExit --> NotifyExt
    PathTranslate --> NotifyExt
    
    NotifyExt --> SysVIPC
    NotifyExt --> FakeID
    NotifyExt --> Link2Sym
    NotifyExt --> MountInfo
```

The extension system allows modular functionality through the `notify_extensions()` mechanism. Extensions register callback functions that are invoked at specific points during system call processing, path translation, and process lifecycle events.

Sources: [src/extension/extension.c](), [src/extension/mountinfo/mountinfo.c:126-143](), [src/GNUmakefile:57-86]()

## Build System Architecture

The build system supports multiple architectures and deployment modes through feature detection and conditional compilation:

```mermaid
graph TB
    Make["GNUmakefile<br/>Build Orchestration"]
    
    subgraph "Feature Detection"
        CheckVM["process_vm detection<br/>.check_process_vm"]
        CheckSeccomp["seccomp_filter detection<br/>.check_seccomp_filter"]
        BuildH["build.h generation<br/>Compile-time config"]
    end
    
    subgraph "Architecture Support"
        Arch64["64-bit objects<br/>Default compilation"]
        Arch32["32-bit objects<br/>HAS_LOADER_32BIT"]
    end
    
    subgraph "Loader Modes"
        Bundled["Bundled Mode<br/>loader-wrapped.o<br/>Embedded in proot"]
        Unbundled["Unbundled Mode<br/>PROOT_UNBUNDLE_LOADER<br/>Separate loader files"]
    end
    
    Make --> CheckVM
    Make --> CheckSeccomp
    CheckVM --> BuildH
    CheckSeccomp --> BuildH
    
    Make --> Arch64
    Make --> Arch32
    
    Make --> Bundled
    Make --> Unbundled
    
    BuildH --> Arch64
    BuildH --> Arch32
```

The build system automatically detects available kernel features like `process_vm_readv/writev` and seccomp filtering support, generating a `build.h` header with appropriate preprocessor definitions. It supports both bundled mode (loader embedded in the main executable) and unbundled mode (separate loader binaries).

Sources: [src/GNUmakefile:88-110](), [src/GNUmakefile:137-166](), [src/GNUmakefile:202-235]()

## Key Data Structures

| Structure | Purpose | Location | Key Fields |
|-----------|---------|----------|------------|
| `Tracee` | Process state management | [tracee/tracee.h]() | `pid`, `exe`, `fs`, `seccomp` |
| `Extension` | Extension instance | [extension/extension.h]() | `callback`, `config` |
| `Cli` | Command-line interface | [cli/cli.h]() | `options`, `handlers` |

The `Tracee` structure serves as the central data repository for each traced process, containing filesystem state, extension configurations, and execution context. Extensions maintain their state through the `Extension` structure and receive events through registered callback functions.

Sources: [src/tracee/event.c:342-344](), [src/cli/cli.c:300-444]()

---

