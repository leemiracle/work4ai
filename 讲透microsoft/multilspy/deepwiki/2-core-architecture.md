<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/multilspy · page 2 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [pyproject.toml](pyproject.toml)
- [src/multilspy/language_server.py](src/multilspy/language_server.py)
- [src/multilspy/lsp_protocol_handler/server.py](src/multilspy/lsp_protocol_handler/server.py)

</details>



This document describes the core architectural design of multilspy, including its layered structure, key classes, and how they interact to provide a language-agnostic LSP client interface. For information about specific language server implementations, see [Language Server Implementations](#3). For details about configuration and setup, see [Configuration System](#1.3).

## Layered Architecture Overview

Multilspy is built using a layered architecture that abstracts LSP protocol complexity and provides both synchronous and asynchronous interfaces for client applications.

### Architecture Layers

```mermaid
graph TB
    subgraph "Application Layer"
        APP[Client Applications]
    end
    
    subgraph "High-Level Interface Layer"
        LS[LanguageServer<br/>Async interface]
        SLS[SyncLanguageServer<br/>Sync wrapper]
        FACTORY[LanguageServer.create<br/>Factory method]
    end
    
    subgraph "Language Implementation Layer"
        KOTLIN[KotlinLanguageServer]
        JAVA[EclipseJDTLS]
        RUST[RustAnalyzer]
        TS[TypeScriptLanguageServer]
        OTHER[Other Language Servers...]
    end
    
    subgraph "Protocol Handler Layer"
        LSH[LanguageServerHandler<br/>JSON-RPC client]
        PLI[ProcessLaunchInfo<br/>Launch configuration]
        BUFFER[LSPFileBuffer<br/>File state management]
    end
    
    subgraph "Process Management Layer"
        PROC[Subprocess management]
        STDIO[stdin/stdout pipes]
        LIFECYCLE[Process lifecycle]
    end
    
    subgraph "External Process Layer"
        EXT[External Language Server Binaries]
    end
    
    APP --> LS
    APP --> SLS
    LS --> FACTORY
    SLS --> LS
    FACTORY --> KOTLIN
    FACTORY --> JAVA
    FACTORY --> RUST
    FACTORY --> TS
    FACTORY --> OTHER
    
    KOTLIN --> LSH
    JAVA --> LSH
    RUST --> LSH
    TS --> LSH
    OTHER --> LSH
    
    LSH --> PLI
    LSH --> BUFFER
    LSH --> PROC
    PROC --> STDIO
    PROC --> LIFECYCLE
    STDIO --> EXT
```

Sources: [src/multilspy/language_server.py:56-198](), [src/multilspy/lsp_protocol_handler/server.py:143-179]()

## Core Classes and Responsibilities

### LanguageServer Class

The `LanguageServer` class serves as the primary asynchronous interface for LSP communication.

| Component | Responsibility | Key Methods |
|-----------|---------------|-------------|
| `LanguageServer` | Main async LSP interface | `create()`, `start_server()`, `request_definition()`, `request_references()` |
| `SyncLanguageServer` | Synchronous wrapper | Same methods as `LanguageServer` but blocking |
| `LanguageServerHandler` | Low-level LSP protocol | `start()`, `stop()`, `send_request()`, `send_notification()` |
| `LSPFileBuffer` | File state tracking | Manages file contents, versions, and reference counts |

Sources: [src/multilspy/language_server.py:56-61](), [src/multilspy/language_server.py:690-694](), [src/multilspy/lsp_protocol_handler/server.py:143-179](), [src/multilspy/language_server.py:34-54]()

### Factory Pattern Implementation

```mermaid
graph TB
    CLIENT[Client Code]
    CONFIG[MultilspyConfig]
    FACTORY[LanguageServer.create]
    
    subgraph "Language Detection"
        PYTHON[Language.PYTHON]
        JAVA[Language.JAVA]
        KOTLIN[Language.KOTLIN]
        RUST[Language.RUST]
        TS[Language.TYPESCRIPT]
        OTHER[Other Languages...]
    end
    
    subgraph "Language Server Instances"
        JEDI[JediServer]
        ECLIPSE[EclipseJDTLS]
        KOTLIN_LS[KotlinLanguageServer]
        RUST_LS[RustAnalyzer]
        TS_LS[TypeScriptLanguageServer]
        OTHER_LS[Other Implementations...]
    end
    
    CLIENT --> CONFIG
    CLIENT --> FACTORY
    CONFIG --> FACTORY
    
    FACTORY --> PYTHON
    FACTORY --> JAVA
    FACTORY --> KOTLIN
    FACTORY --> RUST
    FACTORY --> TS
    FACTORY --> OTHER
    
    PYTHON --> JEDI
    JAVA --> ECLIPSE
    KOTLIN --> KOTLIN_LS
    RUST --> RUST_LS
    TS --> TS_LS
    OTHER --> OTHER_LS
```

The factory method `LanguageServer.create()` examines the `config.code_language` field and instantiates the appropriate language-specific server implementation.

Sources: [src/multilspy/language_server.py:62-127]()

## LSP Protocol Handler Architecture

### LanguageServerHandler Components

```mermaid
graph TB
    subgraph "LanguageServerHandler"
        SEND[LspRequest<br/>send attribute]
        NOTIFY[LspNotification<br/>notify attribute] 
        HANDLERS[Response Handlers<br/>_response_handlers dict]
        PROCESS[Process Management<br/>subprocess.Popen]
    end
    
    subgraph "Communication Flow"
        STDIN[Process stdin]
        STDOUT[Process stdout]
        STDERR[Process stderr]
    end
    
    subgraph "Message Processing"
        JSON_RPC[JSON-RPC 2.0]
        CONTENT_LEN[Content-Length Headers]
        PAYLOAD[Message Payloads]
    end
    
    subgraph "External Language Server"
        EXT_PROC[Language Server Process]
    end
    
    SEND --> JSON_RPC
    NOTIFY --> JSON_RPC
    JSON_RPC --> CONTENT_LEN
    CONTENT_LEN --> PAYLOAD
    PAYLOAD --> STDIN
    STDIN --> EXT_PROC
    
    EXT_PROC --> STDOUT
    EXT_PROC --> STDERR
    STDOUT --> HANDLERS
    STDERR --> HANDLERS
    HANDLERS --> SEND
```

Sources: [src/multilspy/lsp_protocol_handler/server.py:181-209](), [src/multilspy/lsp_protocol_handler/server.py:363-389](), [src/multilspy/lsp_protocol_handler/server.py:99-105]()

### ProcessLaunchInfo Configuration

The `ProcessLaunchInfo` dataclass encapsulates process launch parameters:

```mermaid
graph LR
    PLI[ProcessLaunchInfo]
    CMD[cmd: str<br/>Launch command]
    ENV[env: Dict[str, str]<br/>Environment variables]
    CWD[cwd: str<br/>Working directory]
    
    PLI --> CMD
    PLI --> ENV
    PLI --> CWD
```

Sources: [src/multilspy/lsp_protocol_handler/server.py:47-61]()

## File Buffer Management System

### LSPFileBuffer Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Closed
    Closed --> Opening: open_file() called
    Opening --> Open: File contents loaded
    Open --> Open: Reference count > 0
    Open --> Closing: Reference count = 0
    Closing --> Closed: did_close_text_document sent
    
    Open --> Modified: insert_text_at_position()
    Open --> Modified: delete_text_between_positions()
    Modified --> Open: Change notification sent
```

The `LSPFileBuffer` class tracks file state with reference counting to support nested file operations:

| Field | Purpose |
|-------|---------|
| `uri` | File URI for LSP communication |
| `contents` | Current file contents in memory |
| `version` | Document version for change tracking |
| `language_id` | Language identifier for syntax |
| `ref_count` | Reference count for nested opens |

Sources: [src/multilspy/language_server.py:34-54](), [src/multilspy/language_server.py:202-253]()

## Synchronous Wrapper Architecture

### SyncLanguageServer Implementation

```mermaid
graph TB
    SYNC[SyncLanguageServer]
    ASYNC[LanguageServer]
    LOOP[Event Loop Thread]
    
    subgraph "Threading Model"
        MAIN[Main Thread]
        BG[Background Thread]
    end
    
    subgraph "Async Operations"
        CORO[Coroutines]
        FUTURE[Future Results]
    end
    
    SYNC --> ASYNC
    SYNC --> LOOP
    LOOP --> BG
    MAIN --> SYNC
    
    SYNC --> CORO
    CORO --> FUTURE
    FUTURE --> MAIN
```

The `SyncLanguageServer` uses `asyncio.run_coroutine_threadsafe()` to bridge synchronous and asynchronous interfaces, running the async operations in a dedicated event loop thread.

Sources: [src/multilspy/language_server.py:689-872](), [src/multilspy/language_server.py:762-777]()

## Process Lifecycle Management

### Startup and Shutdown Sequence

```mermaid
sequenceDiagram
    participant Client
    participant LS as LanguageServer
    participant LSH as LanguageServerHandler
    participant Proc as External Process
    
    Client->>LS: start_server()
    LS->>LSH: start()
    LSH->>Proc: create_subprocess_shell()
    LSH->>LSH: create tasks for stdout/stderr
    LSH->>Proc: LSP initialize request
    Proc->>LSH: Server capabilities response
    LSH->>Proc: initialized notification
    LS->>Client: yield ready server
    
    Note over Client,Proc: Normal LSP operations...
    
    Client->>LS: exit context manager
    LS->>LSH: shutdown()
    LSH->>Proc: shutdown request
    LSH->>Proc: exit notification
    LSH->>LSH: _cancel_pending_tasks()
    LSH->>Proc: terminate/kill process
    LSH->>LSH: cleanup pipes and handles
```

The process management includes robust cleanup with timeouts and fallback mechanisms for process termination.

Sources: [src/multilspy/lsp_protocol_handler/server.py:210-232](), [src/multilspy/lsp_protocol_handler/server.py:233-248](), [src/multilspy/lsp_protocol_handler/server.py:265-341](), [src/multilspy/language_server.py:181-198]()

---

