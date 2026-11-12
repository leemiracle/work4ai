<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/TaskWeaver · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

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
- [website/docs/FAQ.md](website/docs/FAQ.md)
- [website/docs/advanced/observability.md](website/docs/advanced/observability.md)
- [website/docs/code_execution.md](website/docs/code_execution.md)
- [website/docs/llms/Keywords-AI.md](website/docs/llms/Keywords-AI.md)
- [website/sidebars.js](website/sidebars.js)

</details>



## Purpose and Scope

This document provides a comprehensive overview of TaskWeaver's system architecture, including its core components, data flow patterns, and integration points. It covers the fundamental design principles that enable TaskWeaver to function as a code-first agent framework, transforming natural language requests into executable code through a multi-role orchestration system.

For specific implementation details of individual components, see [Core Components](#3). For deployment and infrastructure considerations, see [Deployment and Infrastructure](#12). For user interaction patterns, see [User Interfaces](#7).

## Architectural Overview

TaskWeaver implements a multi-layered architecture centered around a role-based orchestration model. The system transforms user requests through a pipeline involving planning, code generation, execution, and response synthesis.

### High-Level System Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        CLI["Console Interface (chat.py)"]
        WebUI["Web UI (Chainlit)"]
        LibAPI["Library API"]
        Docker["Docker Container"]
    end
    
    subgraph "Session Management Layer"
        SessionManager["Session (session.py)"]
        EventEmitter["SessionEventEmitter"]
        Workspace["Workspace Management"]
    end
    
    subgraph "Orchestration Layer"
        Planner["Planner (planner.py)"]
        RoleRegistry["RoleRegistry"]
        Workers["Worker Instances"]
    end
    
    subgraph "Execution Layer"
        CodeInterpreter["CodeInterpreter Role"]
        CodeExecutor["Code Executor"]
        KernelManager["Jupyter Kernel"]
        Container["Docker Container Execution"]
    end
    
    subgraph "LLM Integration Layer"
        LLMApi["LLMApi (llm)"]
        PostTranslator["PostTranslator"]
        CompletionService["Completion Services"]
    end
    
    subgraph "Memory & Communication"
        Memory["Memory (memory.py)"]
        Posts["Post Objects"]
        Attachments["Attachment System"]
        Rounds["Round Management"]
    end
    
    subgraph "Extension System"
        PluginRegistry["Plugin Registry"]
        PluginSelector["Plugin Selector"]
        ExternalRoles["External Roles"]
    end
    
    %% Interface connections
    CLI --> SessionManager
    WebUI --> SessionManager
    LibAPI --> SessionManager
    Docker --> SessionManager
    
    %% Session layer connections
    SessionManager --> EventEmitter
    SessionManager --> Workspace
    SessionManager --> Planner
    SessionManager --> Workers
    
    %% Orchestration connections
    Planner --> RoleRegistry
    Planner --> Memory
    Planner --> LLMApi
    Workers --> CodeInterpreter
    
    %% Execution connections
    CodeInterpreter --> CodeExecutor
    CodeExecutor --> KernelManager
    KernelManager --> Container
    
    %% LLM connections
    Planner --> PostTranslator
    CodeInterpreter --> LLMApi
    LLMApi --> CompletionService
    
    %% Memory connections
    SessionManager --> Memory
    Memory --> Posts
    Posts --> Attachments
    Memory --> Rounds
    
    %% Extension connections
    CodeInterpreter --> PluginRegistry
    PluginRegistry --> PluginSelector
    SessionManager --> ExternalRoles
```

Sources: [taskweaver/session/session.py:44-127](), [taskweaver/planner/planner.py:46-92](), [taskweaver/module/event_emitter.py:231-300]()

### Core Data Flow Architecture

The following diagram illustrates how data flows through the system during a typical user interaction, showing the actual method calls and data structures used:

```mermaid
sequenceDiagram
    participant User
    participant Session["Session.send_message()"]
    participant Memory["Memory.create_round()"]
    participant Planner["Planner.reply()"]
    participant PostTranslator["PostTranslator"]
    participant LLMApi["LLMApi.chat_completion_stream()"]
    participant CodeInterpreter["CodeInterpreter.reply()"]
    participant CodeExecutor["CodeExecutor.execute_code()"]
    participant Environment["ExecutionEnvironment"]
    
    User->>Session: "send_message(message, files)"
    Session->>Memory: "create_round(user_query)"
    Memory-->>Session: "Round object"
    
    Session->>Planner: "reply(memory, prompt_log_path)"
    Planner->>PostTranslator: "compose_prompt(rounds)"
    Planner->>LLMApi: "chat_completion_stream(chat_history)"
    LLMApi-->>Planner: "Stream[ChatMessageType]"
    Planner->>PostTranslator: "raw_text_to_post(llm_output)"
    PostTranslator-->>Planner: "Post with attachments"
    Planner-->>Session: "Post.send_to='CodeInterpreter'"
    
    Session->>CodeInterpreter: "reply(memory, prompt_log_path)"
    CodeInterpreter->>LLMApi: "chat_completion_stream()"
    LLMApi-->>CodeInterpreter: "Generated code"
    CodeInterpreter->>CodeExecutor: "execute_code(code_blocks)"
    CodeExecutor->>Environment: "start_session() & execute()"
    Environment-->>CodeExecutor: "ExecutionResult"
    CodeExecutor-->>CodeInterpreter: "Formatted results"
    CodeInterpreter-->>Session: "Post.send_to='User'"
    
    Session-->>User: "Round with final response"
```

Sources: [taskweaver/session/session.py:162-276](), [taskweaver/planner/planner.py:237-371](), [taskweaver/memory/memory.py]()

## Component Architecture Details

### Session Management Core

The `Session` class serves as the primary orchestrator, managing the complete lifecycle of user interactions and coordinating between all system components.

| Component | Class/Module | Responsibility |
|-----------|--------------|----------------|
| Session Manager | `Session` | Orchestrates user interactions, manages worker instances |
| Event System | `SessionEventEmitter` | Real-time event broadcasting and handling |
| Workspace | `Workspace.get_session_dir()` | File system isolation per session |
| Memory Management | `Memory(session_id)` | Conversation history and state persistence |

```mermaid
graph LR
    subgraph "Session Initialization Flow"
        SessionInit["Session.__init__()"]
        CreateWorkers["Create worker_instances{}"]
        BindPlanner["Create Planner instance"]
        SetupMemory["Memory(session_id)"]
        ConfigureWS["Setup workspace paths"]
    end
    
    subgraph "Message Processing Flow"
        SendMessage["send_message()"]
        CreateRound["memory.create_round()"]
        ProcessLoop["_send_message() loop"]
        WorkerDispatch["Route to Planner/Workers"]
    end
    
    SessionInit --> CreateWorkers
    CreateWorkers --> BindPlanner
    BindPlanner --> SetupMemory
    SetupMemory --> ConfigureWS
    
    SendMessage --> CreateRound
    CreateRound --> ProcessLoop
    ProcessLoop --> WorkerDispatch
```

Sources: [taskweaver/session/session.py:44-127](), [taskweaver/session/session.py:162-276]()

### Role-Based Orchestration System

TaskWeaver implements a flexible role system where the `Planner` coordinates with specialized worker roles. The system supports dynamic role registration and multi-role conversations.

```mermaid
graph TB
    subgraph "Role Registry System"
        RoleRegistry["RoleRegistry.get_role_name_list()"]
        RoleEntry["RoleEntry objects"]
        RoleInstances["worker_instances{}"]
    end
    
    subgraph "Planner Coordination"
        PlannerRole["Planner(workers=worker_instances)"]
        WorkerIntro["compose_sys_prompt(worker_intro)"]
        RecipientSet["recipient_alias_set"]
    end
    
    subgraph "Worker Roles"
        CodeInterpRole["CodeInterpreter Role"]
        ExternalRoles["External Roles (Recepta, etc.)"]
        CustomRoles["Custom Role Implementations"]
    end
    
    subgraph "Communication Protocol"
        PostRouting["Post.send_to routing"]
        MessageFormat["format_message(role, message)"]
        ResponseValidation["check_post_validity()"]
    end
    
    RoleRegistry --> RoleEntry
    RoleEntry --> RoleInstances
    RoleInstances --> PlannerRole
    PlannerRole --> WorkerIntro
    WorkerIntro --> RecipientSet
    
    PlannerRole --> CodeInterpRole
    PlannerRole --> ExternalRoles
    PlannerRole --> CustomRoles
    
    CodeInterpRole --> PostRouting
    PostRouting --> MessageFormat
    MessageFormat --> ResponseValidation
```

Sources: [taskweaver/planner/planner.py:68-82](), [taskweaver/session/session.py:94-120](), [taskweaver/role/role.py]()

### Memory and Communication Architecture

The memory system manages conversation state through `Round` and `Post` objects, with a sophisticated attachment system for structured data exchange.

```mermaid
graph TD
    subgraph "Memory Structure"
        MemoryClass["Memory class"]
        RoundList["rounds: List[Round]"]
        SharedMem["shared_memory: Dict"]
    end
    
    subgraph "Round Management"
        RoundObj["Round objects"]
        PostList["post_list: List[Post]"]
        RoundState["state: 'created'|'finished'|'failed'"]
        UserQuery["user_query: str"]
    end
    
    subgraph "Post Communication"
        PostObj["Post objects"]
        PostFields["send_from, send_to, message"]
        AttachmentList["attachment_list: List[Attachment]"]
        PostID["id: post-{uuid}"]
    end
    
    subgraph "Attachment System"
        AttachmentType["AttachmentType enum"]
        AttachmentContent["content: str, extra: Any"]
        SpecificTypes["init_plan, plan, code_error, execution_result"]
    end
    
    MemoryClass --> RoundList
    MemoryClass --> SharedMem
    RoundList --> RoundObj
    RoundObj --> PostList
    RoundObj --> RoundState
    RoundObj --> UserQuery
    
    PostList --> PostObj
    PostObj --> PostFields
    PostObj --> AttachmentList
    PostObj --> PostID
    
    AttachmentList --> AttachmentType
    AttachmentType --> AttachmentContent
    AttachmentType --> SpecificTypes
```

Sources: [taskweaver/memory/memory.py](), [taskweaver/memory/post.py](), [taskweaver/memory/attachment.py:10-52]()

### LLM Integration Layer

TaskWeaver abstracts LLM interactions through a unified API that supports multiple providers while maintaining consistent interface patterns.

| Provider Support | Implementation | Configuration Key |
|------------------|----------------|-------------------|
| OpenAI | `OpenAIService` | `llm.api_type="openai"` |
| Azure OpenAI | `AzureOpenAIService` | `llm.api_type="azure"` |
| Local Models | `OllamaService` | `llm.api_type="ollama"` |
| Google | `GoogleGenAIService` | `llm.api_type="google"` |
| QWen | `QwenService` | `llm.api_type="qwen"` |

```mermaid
graph LR
    subgraph "LLM API Facade"
        LLMApi["LLMApi class"]
        CompletionMethod["chat_completion_stream()"]
        EmbeddingMethod["get_embedding()"]
        JSONSchema["json_schema parameter"]
    end
    
    subgraph "Provider Services"
        OpenAI["OpenAIService"]
        Azure["AzureOpenAIService"] 
        Ollama["OllamaService"]
        Google["GoogleGenAIService"]
        QWen["QwenService"]
    end
    
    subgraph "Communication Layer"
        ChatMessageType["ChatMessageType"]
        PostTranslator["PostTranslator.raw_text_to_post()"]
        StreamParser["JSON stream parsing"]
    end
    
    LLMApi --> CompletionMethod
    LLMApi --> EmbeddingMethod
    LLMApi --> JSONSchema
    
    CompletionMethod --> OpenAI
    CompletionMethod --> Azure
    CompletionMethod --> Ollama
    CompletionMethod --> Google
    CompletionMethod --> QWen
    
    CompletionMethod --> ChatMessageType
    ChatMessageType --> PostTranslator
    PostTranslator --> StreamParser
```

Sources: [taskweaver/llm/](), [taskweaver/planner/planner.py:284-325](), [taskweaver/role/post_translator.py]()

### Code Execution Architecture

The execution system provides secure, isolated code execution through Jupyter kernels, with support for both local and containerized environments.

```mermaid
graph TB
    subgraph "Execution Modes"
        LocalMode["Local Mode (kernel_mode='local')"]
        ContainerMode["Container Mode (kernel_mode='container')"]
    end
    
    subgraph "Container Infrastructure"
        DockerImage["taskweavercontainers/taskweaver-executor"]
        Dockerfile["docker/ces_container/Dockerfile"]
        EntryScript["entrypoint.sh"]
        BuildScripts["scripts/build_executor.*"]
    end
    
    subgraph "Kernel Management"
        IPythonKernel["IPython Kernel instances"]
        ConnectionFiles["Connection file management"]
        SessionClient["Session client communication"]
        KernelLauncher["Kernel launcher process"]
    end
    
    subgraph "Execution Flow"
        CodeVerification["Code verification step"]
        CodeExecution["execute_code() method"]
        ResultCapture["ExecutionResult objects"]
        ArtifactHandling["Artifact path management"]
    end
    
    LocalMode --> IPythonKernel
    ContainerMode --> DockerImage
    DockerImage --> IPythonKernel
    
    DockerImage --> Dockerfile
    Dockerfile --> EntryScript
    EntryScript --> BuildScripts
    
    IPythonKernel --> ConnectionFiles
    ConnectionFiles --> SessionClient
    SessionClient --> KernelLauncher
    
    SessionClient --> CodeVerification
    CodeVerification --> CodeExecution
    CodeExecution --> ResultCapture
    ResultCapture --> ArtifactHandling
```

Sources: [website/docs/code_execution.md:13-40](), [taskweaver/code_interpreter/](), [docker/ces_container/]()

### Plugin and Extension System

The plugin system enables extensibility through a registry-based architecture with automatic discovery and selection mechanisms.

```mermaid
graph TD
    subgraph "Plugin Discovery"
        PluginRegistry["PluginRegistry.get_list()"]
        YAMLFiles["*.yaml plugin definitions"]
        PythonImpl["*.py implementations"]
        ComponentRegistry["ComponentRegistry"]
    end
    
    subgraph "Plugin Selection"
        PluginSelector["PluginSelector class"]
        EmbeddingService["LLM embedding service"]
        SimilarityMatch["Semantic similarity matching"]
        AutoSelection["Automatic plugin selection"]
    end
    
    subgraph "Built-in Plugins"
        KlarnaSearch["klarna_search plugin"]
        WebSearch["web_search plugin"]
        SQLPull["sql_pull_data plugin"]
        VisionReader["image_reader plugin"]
        WebExplorer["web_explorer plugin"]
    end
    
    subgraph "External Roles"
        ReceptaRole["Recepta reasoning role"]
        CustomRoles["Custom role implementations"]
        RoleIntegration["Role-based plugin integration"]
    end
    
    PluginRegistry --> YAMLFiles
    YAMLFiles --> PythonImpl
    PythonImpl --> ComponentRegistry
    
    ComponentRegistry --> PluginSelector
    PluginSelector --> EmbeddingService
    EmbeddingService --> SimilarityMatch
    SimilarityMatch --> AutoSelection
    
    AutoSelection --> KlarnaSearch
    AutoSelection --> WebSearch
    AutoSelection --> SQLPull
    AutoSelection --> VisionReader
    AutoSelection --> WebExplorer
    
    PluginSelector --> ReceptaRole
    ReceptaRole --> CustomRoles
    CustomRoles --> RoleIntegration
```

Sources: [taskweaver/plugin/](), [project/plugins/](), [README.md:56-57]()

## Event-Driven Architecture

TaskWeaver implements a comprehensive event system that enables real-time monitoring and reactive programming patterns throughout the application lifecycle.

### Event System Structure

```mermaid
graph LR
    subgraph "Event Hierarchy"
        SessionEvents["SessionEventType: session_start, session_end"]
        RoundEvents["RoundEventType: round_start, round_end, round_error"]
        PostEvents["PostEventType: post_start, post_end, post_attachment_update"]
    end
    
    subgraph "Event Processing"
        EventEmitter["SessionEventEmitter.emit()"]
        EventHandlers["List[SessionEventHandler]"]
        PostProxy["PostEventProxy"]
        EventContext["handle_events_ctx()"]
    end
    
    subgraph "Event Consumers"
        ConsoleUpdater["TaskWeaverRoundUpdater"]
        WebUIHandler["Web UI event handlers"]
        ObservabilityTracing["AgentOps integration"]
        CustomHandlers["Custom event handlers"]
    end
    
    SessionEvents --> EventEmitter
    RoundEvents --> EventEmitter
    PostEvents --> EventEmitter
    
    EventEmitter --> EventHandlers
    EventHandlers --> PostProxy
    PostProxy --> EventContext
    
    EventContext --> ConsoleUpdater
    EventContext --> WebUIHandler
    EventContext --> ObservabilityTracing
    EventContext --> CustomHandlers
```

Sources: [taskweaver/module/event_emitter.py:14-52](), [taskweaver/chat/console/chat.py:68-148](), [website/docs/advanced/observability.md:37-41]()

## Security and Isolation

TaskWeaver implements multiple layers of security through execution isolation, code verification, and containerization:

- **Container Isolation**: Default `container` mode executes code in Docker containers
- **Session Isolation**: Each session has dedicated workspace directories  
- **Code Verification**: Pre-execution code analysis and validation
- **Permission Management**: Restricted file system access within execution environments
- **Network Isolation**: Optional network restriction for Docker containers

Sources: [website/docs/code_execution.md:23-25](), [taskweaver/session/session.py:74-82](), [website/docs/code_execution.md:102-161]()

---

