<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/TaskWeaver · page 3 Core Components · fetched 2026-10-26 -->

# Core Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [taskweaver/chat/console/chat.py](taskweaver/chat/console/chat.py)
- [taskweaver/memory/attachment.py](taskweaver/memory/attachment.py)
- [taskweaver/module/event_emitter.py](taskweaver/module/event_emitter.py)
- [taskweaver/planner/planner.py](taskweaver/planner/planner.py)
- [taskweaver/planner/planner_prompt.yaml](taskweaver/planner/planner_prompt.yaml)
- [taskweaver/session/session.py](taskweaver/session/session.py)

</details>



This document provides an overview of the essential components that form TaskWeaver's core functionality. These components work together to enable the code-first agent framework's ability to plan, execute, and coordinate data analytics tasks.

For detailed information about specific subsystems, see [Planner](#3.1), [Session Management](#3.2), [Memory and Communication System](#3.3), and [Code Interpreter](#3.4). For LLM integration details, see [LLM Integration](#4). For code execution specifics, see [Code Execution Service](#5).

## Component Architecture Overview

The core of TaskWeaver consists of five primary components that handle different aspects of the agent framework's operation:

```mermaid
graph TB
    subgraph "User Interface Layer"
        ConsoleChat["TaskWeaverChatApp"]
        WebUI["Web UI Interface"]
        LibraryAPI["Library API"]
    end
    
    subgraph "Session Layer"
        Session["Session"]
        SessionEventEmitter["SessionEventEmitter"]
        Memory["Memory"]
    end
    
    subgraph "Role Layer"
        Planner["Planner"]
        CodeInterpreter["CodeInterpreter"]
        ExternalRoles["External Roles"]
    end
    
    subgraph "Communication Layer"
        Post["Post"]
        Attachment["Attachment"]
        PostTranslator["PostTranslator"]
        PostEventProxy["PostEventProxy"]
    end
    
    subgraph "Execution Layer"
        CodeExecutor["CodeExecutor"]
        Environment["Environment"]
        PluginSystem["Plugin System"]
    end
    
    %% User Interface connections
    ConsoleChat --> Session
    WebUI --> Session
    LibraryAPI --> Session
    
    %% Session Layer connections
    Session --> SessionEventEmitter
    Session --> Memory
    Session --> Planner
    Session --> CodeInterpreter
    
    %% Role Layer connections
    Planner --> PostTranslator
    CodeInterpreter --> CodeExecutor
    Planner --> ExternalRoles
    
    %% Communication Layer connections
    SessionEventEmitter --> PostEventProxy
    PostEventProxy --> Post
    Post --> Attachment
    Memory --> Post
    
    %% Execution Layer connections
    CodeExecutor --> Environment
    CodeInterpreter --> PluginSystem
    
    style Session fill:#e8f5e8
    style Planner fill:#fff3e0
    style Memory fill:#f3e5f5
    style SessionEventEmitter fill:#e3f2fd
```

**Core Component Interaction Flow**

```mermaid
sequenceDiagram
    participant UI as "User Interface"
    participant S as "Session"
    participant M as "Memory" 
    participant P as "Planner"
    participant CI as "CodeInterpreter"
    participant EE as "SessionEventEmitter"
    
    UI->>S: "send_message()"
    S->>EE: "start_round()"
    S->>M: "create_round()"
    S->>P: "reply(memory)"
    P->>M: "get_role_rounds()"
    P->>EE: "create_post_proxy()"
    P->>CI: "send task via Post"
    CI->>EE: "update_attachment()"
    CI->>P: "return results"
    P->>S: "final Post"
    S->>EE: "end_round()"
    S->>UI: "response"
```

Sources: [taskweaver/session/session.py:44-364](), [taskweaver/planner/planner.py:46-372](), [taskweaver/module/event_emitter.py:231-300](), [taskweaver/memory/attachment.py:54-130]()

## Session Management

The `Session` class serves as the central coordinator for all TaskWeaver operations, managing the lifecycle of user interactions and orchestrating communication between different roles.

### Session Components

| Component | Class | Purpose |
|-----------|-------|---------|
| Session Core | `Session` | Main session orchestration and state management |
| Configuration | `AppSessionConfig` | Session-level configuration and role management |
| Metadata | `SessionMetadata` | Session information storage |
| Event Handling | `SessionEventEmitter` | Event-driven communication system |

### Session Initialization

The session initialization process involves several key steps handled in the `Session.__init__()` method:

```mermaid
graph LR
    SessionInit["Session.__init__()"] --> WorkspaceSetup["Workspace Setup"]
    WorkspaceSetup --> RoleRegistry["Role Registry"]
    RoleRegistry --> WorkerInstances["Worker Instances"]
    WorkerInstances --> PlannerSetup["Planner Setup"]
    PlannerSetup --> EventEmitter["Event Emitter"]
    EventEmitter --> MemoryInit["Memory Initialization"]
```

The session manages role instances through the `worker_instances` dictionary and validates role configuration in [taskweaver/session/session.py:96-119](). The planner is initialized with access to all worker instances in [taskweaver/session/session.py:111-118]().

Sources: [taskweaver/session/session.py:44-127](), [taskweaver/session/session.py:18-35]()

## Communication System

TaskWeaver's communication system is built around the `Post` and `Attachment` model, enabling structured information exchange between components.

### Communication Architecture

```mermaid
graph TB
    subgraph "Message Flow"
        UserMessage["User Message"]
        Post["Post Object"]
        Attachment["Attachment List"]
        Memory["Memory Storage"]
    end
    
    subgraph "Event System"
        SessionEventEmitter["SessionEventEmitter"]
        PostEventProxy["PostEventProxy"]
        EventHandlers["Event Handlers"]
    end
    
    subgraph "Translation Layer"
        PostTranslator["PostTranslator"]
        ChatMessages["Chat Messages"]
        LLMFormat["LLM Format"]
    end
    
    UserMessage --> Post
    Post --> Attachment
    Post --> Memory
    
    SessionEventEmitter --> PostEventProxy
    PostEventProxy --> Post
    PostEventProxy --> EventHandlers
    
    Post --> PostTranslator
    PostTranslator --> ChatMessages
    ChatMessages --> LLMFormat
```

### Attachment Types

The system uses strongly-typed attachments defined in `AttachmentType` enum to categorize different kinds of content:

| Category | Attachment Types | Purpose |
|----------|------------------|---------|
| Planning | `init_plan`, `plan`, `current_plan_step`, `plan_reasoning` | Planner task decomposition |
| Code Generation | `thought`, `reply_type`, `reply_content` | CodeInterpreter responses |
| Code Execution | `execution_status`, `execution_result`, `artifact_paths` | Execution results |
| Verification | `verification`, `code_error`, `revise_message` | Code validation |
| Shared Memory | `shared_memory_entry` | Cross-component data sharing |

The `PostEventProxy` class provides a streaming interface for building posts incrementally in [taskweaver/module/event_emitter.py:126-229]().

Sources: [taskweaver/memory/attachment.py:10-53](), [taskweaver/module/event_emitter.py:126-229](), [taskweaver/planner/planner.py:71-71]()

## Event-Driven Architecture

TaskWeaver implements a comprehensive event system that enables real-time communication and status updates across all components.

### Event Hierarchy

```mermaid
graph TD
    TaskWeaverEvent["TaskWeaverEvent"] --> SessionScope["Session Scope"]
    TaskWeaverEvent --> RoundScope["Round Scope"] 
    TaskWeaverEvent --> PostScope["Post Scope"]
    
    SessionScope --> SessionStart["session_start"]
    SessionScope --> SessionEnd["session_end"]
    SessionScope --> SessionNewRound["session_new_round"]
    
    RoundScope --> RoundStart["round_start"]
    RoundScope --> RoundEnd["round_end"]
    RoundScope --> RoundError["round_error"]
    RoundScope --> RoundNewPost["round_new_post"]
    
    PostScope --> PostStart["post_start"]
    PostScope --> PostEnd["post_end"]
    PostScope --> PostError["post_error"]
    PostScope --> PostStatusUpdate["post_status_update"]
    PostScope --> PostMessageUpdate["post_message_update"]
    PostScope --> PostAttachmentUpdate["post_attachment_update"]
```

### Event Flow Implementation

The event system is implemented through three main classes:
- `SessionEventEmitter` - Central event dispatcher in [taskweaver/module/event_emitter.py:231-300]()
- `PostEventProxy` - Post-specific event proxy in [taskweaver/module/event_emitter.py:126-229]()
- `SessionEventHandlerBase` - Base class for event handlers in [taskweaver/module/event_emitter.py:61-124]()

The console interface demonstrates event handling implementation in `TaskWeaverRoundUpdater` class [taskweaver/chat/console/chat.py:68-408]().

Sources: [taskweaver/module/event_emitter.py:15-53](), [taskweaver/module/event_emitter.py:231-300](), [taskweaver/chat/console/chat.py:68-148]()

## Role System Integration

The core components integrate with TaskWeaver's role system through standardized interfaces and dependency injection.

### Role Integration Pattern

```mermaid
graph LR
    Session["Session"] --> RoleRegistry["RoleRegistry"]
    RoleRegistry --> RoleEntry["RoleEntry"]
    RoleEntry --> RoleModule["Role Module"]
    RoleModule --> RoleInstance["Role Instance"]
    RoleInstance --> WorkerInstances["worker_instances"]
    
    Planner["Planner"] --> Workers["workers: Dict"]
    Workers --> WorkerInstances
    
    SessionInjector["session_injector"] --> RoleInstance
    SessionInjector --> Planner
```

The session creates and manages role instances through dependency injection in [taskweaver/session/session.py:94-119](), binding each role instance to the session injector for proper lifecycle management.

Role instances are stored in the `worker_instances` dictionary and accessed by alias, enabling the planner to coordinate with different specialized roles based on their capabilities.

Sources: [taskweaver/session/session.py:94-119](), [taskweaver/planner/planner.py:57-69]()

## Memory Integration

The core components integrate closely with TaskWeaver's memory system to maintain conversation state and enable context-aware operations.

### Memory Structure

```mermaid
graph TB
    Memory["Memory"] --> Rounds["List[Round]"]
    Rounds --> Posts["List[Post]"]
    Posts --> Attachments["List[Attachment]"]
    Posts --> SharedMemory["SharedMemoryEntry"]
    
    Session["Session"] --> MemoryInstance["memory: Memory"]
    Planner["Planner"] --> MemoryAccess["memory.get_role_rounds()"]
    CodeInterpreter["CodeInterpreter"] --> MemoryAccess
    
    MemoryInstance --> SessionState["Session State"]
    MemoryInstance --> ConversationHistory["Conversation History"]
```

Memory is initialized in the session constructor [taskweaver/session/session.py:87-87]() and used throughout the conversation flow to maintain state and provide context to roles.

The planner accesses memory through `memory.get_role_rounds(role=self.alias)` in [taskweaver/planner/planner.py:244-244]() to retrieve conversation history for prompt composition.

Sources: [taskweaver/session/session.py:87-87](), [taskweaver/planner/planner.py:244-244](), [taskweaver/memory/attachment.py:47-48]()

---

