<!-- source: DeepWiki mcp.deepwiki.com · repo termux/proot · page 4 Extension System · fetched 2026-10-26 -->

# Extension System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/extension/extension.h](src/extension/extension.h)

</details>



This document covers PRoot's modular extension architecture, which allows pluggable functionality to be added to PRoot's core system call interception and process management capabilities. The extension system provides a unified event-driven framework for extending PRoot's behavior across path translation, system call handling, and process lifecycle management.

For detailed information about specific extensions, see [System V IPC Extension](#4.1), [fake_id0 Extension](#4.2), [link2symlink Extension](#4.3), and [Other Extensions](#4.4). For information about system call interception mechanics, see [System Call Interception](#3.2).

## Architecture Overview

PRoot's extension system is built around an event-driven architecture where extensions register callback functions to respond to specific system events. The core system dispatches events to all registered extensions, allowing them to modify behavior, intercept operations, or perform additional processing.

### Extension Event Flow

```mermaid
graph TD
    subgraph "Core PRoot Operations"
        SyscallHandler["Syscall Handler"]
        PathTranslator["Path Translation"]
        ProcessManager["Process Management"]
        SeccompFilter["Seccomp Filter"]
    end
    
    subgraph "Extension Framework"
        EventDispatcher["notify_extensions()"]
        ExtensionList["Extension List"]
    end
    
    subgraph "Built-in Extensions"
        FakeID["fake_id0_callback"]
        Link2Sym["link2symlink_callback"]
        SysVIPC["sysvipc_callback"]
        Kompat["kompat_callback"]
        HiddenFiles["hidden_files_callback"]
        PortSwitch["port_switch_callback"]
        AshmemMemfd["ashmem_memfd_callback"]
        Mountinfo["mountinfo_callback"]
    end
    
    SyscallHandler --> EventDispatcher
    PathTranslator --> EventDispatcher
    ProcessManager --> EventDispatcher
    SeccompFilter --> EventDispatcher
    
    EventDispatcher --> ExtensionList
    ExtensionList --> FakeID
    ExtensionList --> Link2Sym
    ExtensionList --> SysVIPC
    ExtensionList --> Kompat
    ExtensionList --> HiddenFiles
    ExtensionList --> PortSwitch
    ExtensionList --> AshmemMemfd
    ExtensionList --> Mountinfo
    
    FakeID --> EventDispatcher
    Link2Sym --> EventDispatcher
    SysVIPC --> EventDispatcher
```

Sources: [src/extension/extension.h:184-199]()

### Extension Data Structure

```mermaid
graph LR
    subgraph "Extension Structure"
        ExtStruct["Extension"]
        Callback["extension_callback_t callback"]
        Config["TALLOC_CTX *config"]
        FilteredSys["FilteredSysnum *filtered_sysnums"]
        ListLink["LIST_ENTRY(extension) link"]
    end
    
    subgraph "Tracee Integration"
        Tracee["Tracee"]
        ExtList["Extensions *extensions"]
    end
    
    ExtStruct --> Callback
    ExtStruct --> Config
    ExtStruct --> FilteredSys
    ExtStruct --> ListLink
    
    Tracee --> ExtList
    ExtList --> ExtStruct
```

Sources: [src/extension/extension.h:158-172](), [src/extension/extension.h:174]()

## Event System

The extension system defines a comprehensive set of events that cover all major PRoot operations. Extensions can selectively respond to relevant events while ignoring others.

### Event Categories

| Event Category | Events | Purpose |
|---|---|---|
| Path Translation | `GUEST_PATH`, `HOST_PATH`, `TRANSLATED_PATH` | Handle path translation and manipulation |
| System Call Entry | `SYSCALL_ENTER_START`, `SYSCALL_ENTER_END` | Process syscall arguments before execution |
| System Call Exit | `SYSCALL_EXIT_START`, `SYSCALL_EXIT_END` | Process syscall results after execution |
| Process Lifecycle | `INHERIT_PARENT`, `INHERIT_CHILD`, `NEW_STATUS` | Manage extension inheritance and process state |
| Special Handling | `SIGSYS_OCC`, `SYSCALL_CHAINED_ENTER`, `SYSCALL_CHAINED_EXIT` | Handle seccomp events and chained syscalls |
| Extension Management | `INITIALIZATION`, `REMOVED`, `PRINT_CONFIG`, `PRINT_USAGE` | Extension lifecycle and configuration |

Sources: [src/extension/extension.h:33-150]()

### Event Processing Flow

```mermaid
sequenceDiagram
    participant Core as "PRoot Core"
    participant Dispatcher as "notify_extensions()"
    participant Ext1 as "Extension 1"
    participant Ext2 as "Extension 2"
    participant ExtN as "Extension N"
    
    Core->>Dispatcher: "notify_extensions(tracee, event, data1, data2)"
    
    Dispatcher->>Ext1: "callback(extension, event, data1, data2)"
    Ext1-->>Dispatcher: "status (0 = continue)"
    
    alt status != 0
        Dispatcher-->>Core: "Return status"
    else status == 0
        Dispatcher->>Ext2: "callback(extension, event, data1, data2)"
        Ext2-->>Dispatcher: "status (0 = continue)"
        
        alt status != 0
            Dispatcher-->>Core: "Return status"
        else status == 0
            Dispatcher->>ExtN: "callback(extension, event, data1, data2)"
            ExtN-->>Dispatcher: "status"
            Dispatcher-->>Core: "Final status"
        end
    end
```

Sources: [src/extension/extension.h:184-199]()

## Extension Lifecycle

Extensions follow a well-defined lifecycle from initialization through inheritance to cleanup.

### Initialization and Configuration

Extensions are initialized through the `INITIALIZATION` event, which provides command-line arguments for configuration. The extension can allocate configuration data using the `config` field, which is managed by the talloc memory management system.

```mermaid
graph TD
    CLI["Command Line Interface"]
    InitExt["initialize_extension()"]
    Callback["extension_callback_t"]
    InitEvent["INITIALIZATION Event"]
    Config["Extension Config"]
    
    CLI --> InitExt
    InitExt --> Callback
    Callback --> InitEvent
    InitEvent --> Config
    
    Config --> |"Success (>= 0)"| Active["Active Extension"]
    Config --> |"Error (< 0)"| Removed["Extension Removed"]
```

Sources: [src/extension/extension.h:117-120](), [src/extension/extension.h:163-164](), [src/extension/extension.h:176]()

### Extension Inheritance

When a tracee creates child processes, extensions must decide how they should be inherited. The inheritance process involves two events:

- `INHERIT_PARENT`: Asked of the parent's extension to determine inheritance behavior
- `INHERIT_CHILD`: Called on the child's extension to set up child-specific configuration

```mermaid
graph TD
    ParentTracee["Parent Tracee"]
    ChildTracee["Child Tracee"]
    
    ParentExt["Parent Extension"]
    ChildExt["Child Extension"]
    
    InheritParent["INHERIT_PARENT Event"]
    InheritChild["INHERIT_CHILD Event"]
    
    ParentTracee --> ParentExt
    ParentExt --> InheritParent
    
    InheritParent --> |"< 0: Not Inheritable"| NoInherit["No Extension in Child"]
    InheritParent --> |"== 0: Shared Config"| SharedConfig["Shared Configuration"]
    InheritParent --> |"> 0: Call INHERIT_CHILD"| CallChildEvent["Call INHERIT_CHILD"]
    
    CallChildEvent --> ChildExt
    ChildExt --> InheritChild
    InheritChild --> ChildConfig["Child-Specific Config"]
    
    SharedConfig --> ChildTracee
    ChildConfig --> ChildTracee
```

Sources: [src/extension/extension.h:89-104](), [src/extension/extension.h:177]()

## Built-in Extensions

PRoot includes several built-in extensions that provide essential functionality:

### Extension Callback Functions

| Extension | Callback Function | Primary Purpose |
|---|---|---|
| Kernel Compatibility | `kompat_callback` | Handle kernel version compatibility issues |
| Fake Root | `fake_id0_callback` | Emulate root privileges and UID/GID manipulation |
| Hidden Files | `hidden_files_callback` | Hide specific files from directory listings |
| Port Switching | `port_switch_callback` | Network port redirection |
| Link to Symlink | `link2symlink_callback` | Convert hard links to symbolic links |
| Symlink Size Fix | `fix_symlink_size_callback` | Fix symbolic link size reporting |
| Android Shared Memory | `ashmem_memfd_callback` | Android ashmem to memfd translation |
| Mount Info | `mountinfo_callback` | Provide custom /proc/mounts information |

Sources: [src/extension/extension.h:202-210]()

### Extension Registration Architecture

```mermaid
graph TD
    subgraph "Extension Registration"
        CLI["Command Line Parsing"]
        ExtCallback["extension_callback_t"]
        FilteredSys["FilteredSysnum List"]
        ExtConfig["Extension Config"]
    end
    
    subgraph "Extension Management"
        TraceeExt["Tracee Extensions List"]
        InitExt["initialize_extension()"]
        GetExt["get_extension()"]
        InheritExt["inherit_extensions()"]
    end
    
    CLI --> ExtCallback
    ExtCallback --> FilteredSys
    ExtCallback --> ExtConfig
    
    ExtCallback --> InitExt
    InitExt --> TraceeExt
    
    TraceeExt --> GetExt
    TraceeExt --> InheritExt
```

Sources: [src/extension/extension.h:166-167](), [src/extension/extension.h:176-178]()

## Implementation Details

### Event Dispatch Mechanism

The central `notify_extensions()` function implements a simple but effective event dispatch mechanism. It iterates through all extensions registered with a tracee and calls their callback functions sequentially. If any extension returns a non-zero status, the dispatch stops and returns that status.

### Extension Configuration Management

Extensions use the talloc memory management system for configuration storage. The `config` field in the `Extension` structure serves as a talloc context, allowing extensions to allocate hierarchical configuration data that is automatically cleaned up when the extension is removed.

### System Call Filtering

Extensions can specify which system calls they're interested in through the `filtered_sysnums` field. This allows the core system to optimize event dispatch by only notifying relevant extensions for specific system calls.

Sources: [src/extension/extension.h:158-172]()

---

