<!-- source: DeepWiki mcp.deepwiki.com · repo termux/termux-api-package · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CMakeLists.txt](CMakeLists.txt)
- [termux-api-broadcast.c](termux-api-broadcast.c)
- [termux-api.c](termux-api.c)
- [termux-api.h](termux-api.h)
- [termux-callback.in](termux-callback.in)

</details>



This document explains the high-level architecture of the termux-api-package, showing how shell scripts, C libraries, and Android components work together to provide command-line access to Android APIs within the Termux environment. The architecture implements a sophisticated inter-process communication (IPC) system that bridges the gap between C programs and Android's Java-based API layer.

For detailed information about the IPC mechanisms, see [Core IPC Mechanism](#2.1). For the C library interface documentation, see [C Library API](#2.2). For build system details, see [Build System](#3).

## System Overview

The termux-api-package implements a multi-layer architecture that transforms user commands into Android API calls through a series of well-defined components. The system consists of generated shell scripts, a core C library, and integration with Android's broadcast mechanism.

### High-Level Component Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        Scripts["~50 Generated Scripts<br/>(termux-camera-photo, termux-battery-status, etc.)"]
        User["Command Line User"]
    end
    
    subgraph "Core Processing Layer"
        Broadcast["termux-api-broadcast<br/>Main Executable"]
        CoreLib["libtermux-api.so/.a<br/>Core IPC Library"]
        RunAPI["run_api_command()"]
    end
    
    subgraph "IPC Communication Layer"
        ContactPlugin["contact_plugin()"]
        ExecAM["exec_am_broadcast()"]
        Sockets["Unix Domain Sockets<br/>(Abstract Namespace)"]
        AmBroadcast["am broadcast Command"]
    end
    
    subgraph "Android Integration Layer"
        Receiver["com.termux.api/.TermuxApiReceiver"]
        AndroidAPIs["Android System APIs"]
    end
    
    User --> Scripts
    Scripts --> Broadcast
    Broadcast --> RunAPI
    RunAPI --> ContactPlugin
    ContactPlugin --> Sockets
    ContactPlugin --> ExecAM
    ExecAM --> AmBroadcast
    Sockets --> Receiver
    AmBroadcast --> Receiver
    Receiver --> AndroidAPIs
```

Sources: [termux-api.c:380-465](), [termux-api-broadcast.c:16-23](), [CMakeLists.txt:15-73]()

## Core Components

### Main Executable: termux-api-broadcast

The `termux-api-broadcast` executable serves as the primary entry point for all API operations. It implements a minimal wrapper around the core library functionality.

| Component | Purpose | Key Function |
|-----------|---------|--------------|
| `main()` | Entry point and file descriptor handling | [termux-api-broadcast.c:16-23]() |
| `run_api_command()` | Core orchestration logic | [termux-api.c:380-465]() |
| `exec_callback()` | Handle file descriptor callbacks | [termux-api.c:294-316]() |

### Core IPC Library: termux-api.c

The heart of the system is the IPC library that manages communication between C programs and Android components. This library implements a dual-strategy approach for maximum compatibility across Android versions.

### IPC Strategy Decision Flow

```mermaid
flowchart TD
    Start["run_api_command() Called"]
    GenUUID["generate_uuid()<br/>Create socket addresses"]
    CreateSockets["Create Unix Domain Sockets<br/>(Abstract namespace)"]
    Fork["fork() Process"]
    
    subgraph "Child Process Path"
        ContactPlugin["contact_plugin()"]
        CheckAPI["Android API Level < 34?"]
        TrySocket["Try Unix Socket Connection<br/>LISTEN_SOCKET_ADDRESS"]
        SocketSuccess{"Socket Connection<br/>Successful?"}
        UseSocket["Use Socket Communication"]
        FallbackAM["exec_am_broadcast()"]
    end
    
    subgraph "Parent Process Path"
        AcceptConnections["Accept Socket Connections"]
        StartThreads["Start I/O Threads<br/>transmit_stdin_to_socket()"]
        HandleOutput["transmit_socket_to_stdout()"]
    end
    
    Start --> GenUUID
    GenUUID --> CreateSockets
    CreateSockets --> Fork
    Fork --> ContactPlugin
    Fork --> AcceptConnections
    
    ContactPlugin --> CheckAPI
    CheckAPI -->|Yes| TrySocket
    CheckAPI -->|No| FallbackAM
    TrySocket --> SocketSuccess
    SocketSuccess -->|Yes| UseSocket
    SocketSuccess -->|No| FallbackAM
    
    AcceptConnections --> StartThreads
    StartThreads --> HandleOutput
```

Sources: [termux-api.c:36-236](), [termux-api.c:238-292](), [termux-api.c:380-465]()

## Communication Architecture

### Socket Communication System

The system uses abstract Unix domain sockets for efficient bidirectional communication. Each API call generates unique socket addresses using UUIDs to prevent conflicts.

| Function | Purpose | Key Operations |
|----------|---------|----------------|
| `generate_uuid()` | Create unique socket addresses | [termux-api.c:318-330]() |
| `transmit_stdin_to_socket()` | Forward stdin to Android component | [termux-api.c:332-349]() |
| `transmit_socket_to_stdout()` | Forward Android output to stdout | [termux-api.c:351-378]() |

### Broadcast Fallback Mechanism

When socket communication fails (typically on Android API ≥ 34), the system automatically falls back to using Android's `am broadcast` command.

```mermaid
sequenceDiagram
    participant User
    participant Script as "termux-* script"
    participant Broadcast as "termux-api-broadcast"
    participant Core as "run_api_command()"
    participant Child as "contact_plugin()"
    participant Android as "TermuxApiReceiver"
    
    User->>Script: "Execute command"
    Script->>Broadcast: "Call with API method"
    Broadcast->>Core: "run_api_command(argc, argv)"
    Core->>Core: "generate_uuid() for sockets"
    Core->>Core: "Create & bind sockets"
    Core->>Child: "fork() -> contact_plugin()"
    
    alt "Android API < 34 & Socket Available"
        Child->>Android: "Unix socket connection"
        Android-->>Child: "Bidirectional data"
    else "Socket fails or API >= 34"
        Child->>Child: "exec_am_broadcast()"
        Child->>Android: "am broadcast command"
        Android-->>Core: "Socket communication"
    end
    
    Core->>Core: "transmit_socket_to_stdout()"
    Core->>Broadcast: "Return file descriptor or data"
    Broadcast->>Script: "Output results"
    Script->>User: "Display output"
```

Sources: [termux-api.c:53-65](), [termux-api.c:238-292](), [termux-api.c:444-465]()

## Build System Integration

The build system generates all user-facing scripts from templates and creates the necessary library artifacts.

### Component Generation Process

```mermaid
graph LR
    subgraph "Source Files"
        SourceC["termux-api.c"]
        Header["termux-api.h"]
        BroadcastC["termux-api-broadcast.c"]
        Templates["Script Templates<br/>(*.in files)"]
    end
    
    subgraph "CMake Processing"
        CMakeBuild["CMakeLists.txt"]
        ConfigureFile["configure_file()"]
    end
    
    subgraph "Generated Artifacts"
        SharedLib["libtermux-api.so"]
        StaticLib["libtermux-api.a"]
        Executable["termux-api-broadcast"]
        Scripts["50+ termux-* scripts"]
        Callback["termux-callback"]
    end
    
    subgraph "Installation Structure"
        BinDir["/bin/<br/>User Commands"]
        LibDir["/lib/<br/>Libraries"]
        LibexecDir["/libexec/<br/>Internal Executables"]
        IncludeDir["/include/<br/>Headers"]
    end
    
    SourceC --> CMakeBuild
    BroadcastC --> CMakeBuild
    Header --> CMakeBuild
    Templates --> ConfigureFile
    
    CMakeBuild --> SharedLib
    CMakeBuild --> StaticLib
    CMakeBuild --> Executable
    ConfigureFile --> Scripts
    ConfigureFile --> Callback
    
    Scripts --> BinDir
    SharedLib --> LibDir
    StaticLib --> LibDir
    Executable --> LibexecDir
    Callback --> LibexecDir
    Header --> IncludeDir
```

### Script Generation Details

The build system processes 50+ script templates to create user-facing commands:

| Script Category | Examples | Template Processing |
|-----------------|----------|-------------------|
| Communication | `termux-sms-send`, `termux-call-log` | [CMakeLists.txt:54-59]() |
| Hardware | `termux-camera-photo`, `termux-sensor` | [CMakeLists.txt:22-23, 52]() |
| System | `termux-battery-status`, `termux-volume` | [CMakeLists.txt:19, 68]() |
| Storage | `termux-saf-*` family | [CMakeLists.txt:43-51]() |

Sources: [CMakeLists.txt:15-81](), [CMakeLists.txt:117-123]()

## Key Constants and Addresses

The system relies on several critical constants for proper operation:

| Constant | Value | Purpose |
|----------|-------|---------|
| `LISTEN_SOCKET_ADDRESS` | `"com.termux.api://listen"` | Primary socket address for Android communication |
| `TERMUX_API_PACKAGE_VERSION` | `"0.59.1"` | Version identification |
| Android Target | `"com.termux.api/.TermuxApiReceiver"` | Broadcast receiver component |

Sources: [termux-api.c:25](), [termux-api.c:31](), [termux-api.c:268]()

---

