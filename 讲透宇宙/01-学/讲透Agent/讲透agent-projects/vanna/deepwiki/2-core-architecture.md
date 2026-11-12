<!-- source: DeepWiki mcp.deepwiki.com · repo vanna-ai/vanna · page 2 Core Architecture · fetched 2026-10-29 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [pyproject.toml](pyproject.toml)
- [src/vanna/__init__.py](src/vanna/__init__.py)
- [src/vanna/core/__init__.py](src/vanna/core/__init__.py)
- [src/vanna/core/agent/agent.py](src/vanna/core/agent/agent.py)
- [src/vanna/core/workflow/__init__.py](src/vanna/core/workflow/__init__.py)
- [src/vanna/examples/default_workflow_handler_example.py](src/vanna/examples/default_workflow_handler_example.py)
- [src/vanna/integrations/local/__init__.py](src/vanna/integrations/local/__init__.py)
- [src/vanna/integrations/local/file_system_conversation_store.py](src/vanna/integrations/local/file_system_conversation_store.py)
- [src/vanna/tools/agent_memory.py](src/vanna/tools/agent_memory.py)

</details>



This document provides a detailed overview of Vanna's core architectural components and their interactions. It covers the primary classes, interfaces, and data flows that form the foundation of the agent framework. For information about specific integrations (LLM providers, vector databases, SQL databases), see sections [5](#5), [4](#4), and [6](#6) respectively. For information about the security model, see [Security and Access Control](#3).

The Vanna architecture follows a layered design where the `Agent` class serves as the central orchestrator, coordinating between the LLM service, tool execution, conversation management, and extensibility points. All major components are interface-driven, allowing for flexible implementations and easy testing.

## Core Component Overview

The following diagram shows the main architectural components and their relationships:

```mermaid
graph TB
    subgraph "Agent Layer"
        Agent["Agent<br/>[agent.py:56-1177]"]
        AgentConfig["AgentConfig<br/>[config.py]"]
    end
    
    subgraph "Execution Components"
        ToolRegistry["ToolRegistry<br/>[registry.py]"]
        LlmService["LlmService<br/>[llm/base.py]"]
        SystemPromptBuilder["SystemPromptBuilder<br/>[system_prompt/base.py]"]
        WorkflowHandler["WorkflowHandler<br/>[workflow/base.py]"]
    end
    
    subgraph "Storage Layer"
        ConversationStore["ConversationStore<br/>[storage/base.py]"]
        AgentMemory["AgentMemory<br/>[capabilities/agent_memory.py]"]
    end
    
    subgraph "Security & Context"
        UserResolver["UserResolver<br/>[user/resolver.py]"]
        ToolContext["ToolContext<br/>[tool/models.py]"]
        User["User<br/>[user/models.py]"]
    end
    
    subgraph "Extensibility Hooks"
        LifecycleHook["LifecycleHook<br/>[lifecycle.py]"]
        LlmMiddleware["LlmMiddleware<br/>[middleware.py]"]
        ToolContextEnricher["ToolContextEnricher<br/>[enricher.py]"]
        LlmContextEnhancer["LlmContextEnhancer<br/>[enhancer.py]"]
        ConversationFilter["ConversationFilter<br/>[filter.py]"]
        ErrorRecoveryStrategy["ErrorRecoveryStrategy<br/>[recovery.py]"]
    end
    
    Agent --> AgentConfig
    Agent --> LlmService
    Agent --> ToolRegistry
    Agent --> ConversationStore
    Agent --> SystemPromptBuilder
    Agent --> WorkflowHandler
    Agent --> AgentMemory
    Agent --> UserResolver
    Agent --> LifecycleHook
    Agent --> LlmMiddleware
    Agent --> ToolContextEnricher
    Agent --> LlmContextEnhancer
    Agent --> ConversationFilter
    Agent --> ErrorRecoveryStrategy
    
    UserResolver --> User
    ToolRegistry --> ToolContext
    ToolContext --> User
    ToolContext --> AgentMemory
```

**Diagram: Core Component Dependencies**

The `Agent` class integrates all components through constructor dependency injection, making the architecture testable and modular.

**Sources:** [src/vanna/core/agent/agent.py:82-140](), [src/vanna/__init__.py:12-83](), [src/vanna/core/__init__.py:9-32]()

---

## Agent Initialization and Dependencies

The `Agent` constructor defines the complete dependency graph:

```mermaid
graph LR
    subgraph "Required Dependencies"
        llm["llm_service:<br/>LlmService"]
        registry["tool_registry:<br/>ToolRegistry"]
        resolver["user_resolver:<br/>UserResolver"]
        memory["agent_memory:<br/>AgentMemory"]
    end
    
    subgraph "Optional with Defaults"
        store["conversation_store:<br/>ConversationStore<br/>(default: MemoryConversationStore)"]
        config["config:<br/>AgentConfig<br/>(default: AgentConfig())"]
        prompt["system_prompt_builder:<br/>SystemPromptBuilder<br/>(default: DefaultSystemPromptBuilder)"]
        workflow["workflow_handler:<br/>WorkflowHandler<br/>(default: DefaultWorkflowHandler)"]
        enhancer["llm_context_enhancer:<br/>LlmContextEnhancer<br/>(default: DefaultLlmContextEnhancer)"]
    end
    
    subgraph "Extensibility Lists"
        hooks["lifecycle_hooks:<br/>List[LifecycleHook]<br/>(default: [])"]
        middlewares["llm_middlewares:<br/>List[LlmMiddleware]<br/>(default: [])"]
        enrichers["context_enrichers:<br/>List[ToolContextEnricher]<br/>(default: [])"]
        filters["conversation_filters:<br/>List[ConversationFilter]<br/>(default: [])"]
    end
    
    subgraph "Optional Infrastructure"
        recovery["error_recovery_strategy:<br/>ErrorRecoveryStrategy<br/>(default: None)"]
        observability["observability_provider:<br/>ObservabilityProvider<br/>(default: None)"]
        audit["audit_logger:<br/>AuditLogger<br/>(default: None)"]
    end
    
    Agent --> llm
    Agent --> registry
    Agent --> resolver
    Agent --> memory
    Agent --> store
    Agent --> config
    Agent --> prompt
    Agent --> workflow
    Agent --> enhancer
    Agent --> hooks
    Agent --> middlewares
    Agent --> enrichers
    Agent --> filters
    Agent --> recovery
    Agent --> observability
    Agent --> audit
```

**Diagram: Agent Constructor Dependencies**

The agent provides sensible defaults for most components, requiring only the four core dependencies: `llm_service`, `tool_registry`, `user_resolver`, and `agent_memory`.

**Sources:** [src/vanna/core/agent/agent.py:82-140]()

---

## Message Processing Pipeline

The `Agent.send_message()` method orchestrates the complete message processing pipeline:

```mermaid
sequenceDiagram
    participant Client
    participant Agent
    participant UserResolver
    participant WorkflowHandler
    participant LlmService
    participant ToolRegistry
    participant ConversationStore
    participant AgentMemory

    Client->>Agent: send_message(request_context, message)
    
    Note over Agent: Phase 1: User Resolution
    Agent->>UserResolver: resolve_user(request_context)
    UserResolver-->>Agent: User
    
    Note over Agent: Phase 2: Workflow Interception
    Agent->>WorkflowHandler: try_handle(agent, user, conversation, message)
    alt Workflow Handles Message
        WorkflowHandler-->>Agent: WorkflowResult(should_skip_llm=True)
        Agent->>Client: yield UiComponents
        Note over Agent: Exit early (no LLM call)
    end
    
    Note over Agent: Phase 3: Conversation Loading
    Agent->>ConversationStore: get_conversation(conversation_id, user)
    ConversationStore-->>Agent: Conversation
    
    Note over Agent: Phase 4: Context Building
    Agent->>ToolRegistry: get_schemas(user)
    ToolRegistry-->>Agent: List[ToolSchema]
    Agent->>Agent: _build_llm_request(conversation, schemas, user, system_prompt)
    
    Note over Agent: Phase 5: LLM Interaction
    loop Tool Iterations (max: config.max_tool_iterations)
        Agent->>LlmService: stream_request(request) OR send_request(request)
        LlmService-->>Agent: LlmResponse(tool_calls)
        
        alt Has Tool Calls
            loop For each tool_call
                Agent->>ToolRegistry: execute(tool_call, context)
                ToolRegistry-->>Agent: ToolResult
                Agent->>Client: yield ToolResult.ui_component
            end
            Agent->>Agent: Add tool results to conversation
        else No Tool Calls
            Agent->>Client: yield response content
            Note over Agent: Exit loop
        end
    end
    
    Note over Agent: Phase 6: Conversation Persistence
    Agent->>ConversationStore: update_conversation(conversation)
```

**Diagram: Message Processing Flow**

The pipeline consists of six phases, with the workflow handler providing an early exit path for deterministic command handling. The tool execution loop allows the LLM to make multiple tool calls before providing a final response.

**Sources:** [src/vanna/core/agent/agent.py:142-230](), [src/vanna/core/agent/agent.py:231-1177]()

---

## Component Initialization Flow

The following diagram maps initialization to specific code locations:

```mermaid
graph TB
    subgraph "1. Agent Instantiation"
        constructor["Agent.__init__()<br/>[agent.py:82-140]"]
    end
    
    subgraph "2. Store Dependencies"
        store_llm["self.llm_service = llm_service<br/>[agent.py:101]"]
        store_registry["self.tool_registry = tool_registry<br/>[agent.py:102]"]
        store_resolver["self.user_resolver = user_resolver<br/>[agent.py:103]"]
        store_memory["self.agent_memory = agent_memory<br/>[agent.py:104]"]
    end
    
    subgraph "3. Apply Defaults"
        default_store["if conversation_store is None:<br/>  conversation_store = MemoryConversationStore()<br/>[agent.py:107-110]"]
        default_workflow["if workflow_handler is None:<br/>  workflow_handler = DefaultWorkflowHandler()<br/>[agent.py:119-121]"]
        default_enhancer["if llm_context_enhancer is None:<br/>  llm_context_enhancer = DefaultLlmContextEnhancer(agent_memory)<br/>[agent.py:127-129]"]
    end
    
    subgraph "4. Wire Audit Logger"
        audit_wire["if audit_logger and config.audit_config.enabled:<br/>  tool_registry.audit_logger = audit_logger<br/>  tool_registry.audit_config = config.audit_config<br/>[agent.py:136-138]"]
    end
    
    constructor --> store_llm
    constructor --> store_registry
    constructor --> store_resolver
    constructor --> store_memory
    store_llm --> default_store
    store_memory --> default_workflow
    default_workflow --> default_enhancer
    default_enhancer --> audit_wire
```

**Diagram: Initialization Code Flow**

The agent applies sensible defaults for optional components and automatically wires the audit logger into the tool registry if auditing is enabled.

**Sources:** [src/vanna/core/agent/agent.py:82-140]()

---

## Data Flow: Request to Response

The following shows how data flows through core models:

```mermaid
graph LR
    subgraph "Input Models"
        RequestContext["RequestContext<br/>[user/request_context.py]<br/>metadata: Dict"]
        Message_In["Message<br/>[storage/models.py]<br/>role: 'user'<br/>content: str"]
    end
    
    subgraph "Processing Models"
        User_Model["User<br/>[user/models.py]<br/>id, username, email<br/>group_memberships: List[str]"]
        Conversation_Model["Conversation<br/>[storage/models.py]<br/>id, user, messages<br/>created_at, updated_at"]
        ToolContext_Model["ToolContext<br/>[tool/models.py]<br/>user, conversation_id<br/>agent_memory, metadata"]
        LlmRequest_Model["LlmRequest<br/>[llm/models.py]<br/>messages: List[LlmMessage]<br/>tools: List[ToolSchema]<br/>temperature, max_tokens"]
        LlmResponse_Model["LlmResponse<br/>[llm/models.py]<br/>content: str<br/>tool_calls: List[ToolCall]<br/>finish_reason"]
        ToolCall_Model["ToolCall<br/>[tool/models.py]<br/>id, name, arguments"]
        ToolResult_Model["ToolResult<br/>[tool/models.py]<br/>success, result_for_llm<br/>ui_component, error"]
    end
    
    subgraph "Output Models"
        UiComponent_Model["UiComponent<br/>[components.py]<br/>rich_component<br/>simple_component"]
        Message_Out["Message<br/>[storage/models.py]<br/>role: 'assistant'<br/>content: str<br/>tool_calls"]
    end
    
    RequestContext --> User_Model
    Message_In --> Conversation_Model
    User_Model --> ToolContext_Model
    Conversation_Model --> LlmRequest_Model
    User_Model --> LlmRequest_Model
    LlmRequest_Model --> LlmResponse_Model
    LlmResponse_Model --> ToolCall_Model
    ToolCall_Model --> ToolContext_Model
    ToolContext_Model --> ToolResult_Model
    ToolResult_Model --> UiComponent_Model
    LlmResponse_Model --> Message_Out
    Message_Out --> Conversation_Model
```

**Diagram: Data Model Flow**

Data flows through a series of strongly-typed Pydantic models, ensuring type safety and validation at each stage.

**Sources:** [src/vanna/core/tool/models.py](), [src/vanna/core/llm/models.py](), [src/vanna/core/storage/models.py](), [src/vanna/core/user/models.py]()

---

## Component Interfaces

Each core component defines an abstract interface implemented by multiple backends:

| Component | Interface Location | Key Methods | Default Implementation |
|-----------|-------------------|-------------|------------------------|
| **LlmService** | [llm/base.py]() | `send_request()`, `stream_request()`, `validate_tools()` | N/A (must provide) |
| **ConversationStore** | [storage/base.py]() | `get_conversation()`, `update_conversation()`, `list_conversations()` | `MemoryConversationStore` |
| **SystemPromptBuilder** | [system_prompt/base.py]() | `build_system_prompt()` | `DefaultSystemPromptBuilder` |
| **WorkflowHandler** | [workflow/base.py]() | `try_handle()`, `get_starter_ui()` | `DefaultWorkflowHandler` |
| **UserResolver** | [user/resolver.py]() | `resolve_user()` | N/A (must provide) |
| **AgentMemory** | [capabilities/agent_memory.py]() | `save_tool_usage()`, `search_similar_usage()` | N/A (must provide) |

**Table: Core Component Interfaces**

For detailed information about each interface, see the corresponding subsection ([2.1](#2.1) through [2.7](#2.7)).

**Sources:** [src/vanna/core/__init__.py:9-32]()

---

## Extensibility Hooks

The agent provides seven extensibility points for customizing behavior without modifying core code:

```mermaid
graph TB
    subgraph "Lifecycle Hooks"
        before_msg["before_message(user, message)<br/>[lifecycle.py]"]
        before_tool["before_tool(tool, context)<br/>[lifecycle.py]"]
        after_tool["after_tool(tool, context, result)<br/>[lifecycle.py]"]
        after_msg["after_message(user, message, conversation)<br/>[lifecycle.py]"]
    end
    
    subgraph "LLM Middleware"
        before_req["before_request(request)<br/>[middleware.py]"]
        after_resp["after_response(response)<br/>[middleware.py]"]
        after_stream["after_stream_chunk(chunk)<br/>[middleware.py]"]
    end
    
    subgraph "Context Enrichment"
        enrich["enrich_context(context)<br/>[enricher.py]"]
        enhance_sys["enhance_system_prompt(prompt, message, user)<br/>[enhancer.py]"]
        enhance_msgs["enhance_messages(messages, user)<br/>[enhancer.py]"]
    end
    
    subgraph "Filtering & Recovery"
        filter["filter_messages(messages, user)<br/>[filter.py]"]
        recover["handle_error(error, context)<br/>[recovery.py]"]
    end
    
    Agent --> before_msg
    Agent --> before_tool
    Agent --> after_tool
    Agent --> after_msg
    Agent --> before_req
    Agent --> after_resp
    Agent --> after_stream
    Agent --> enrich
    Agent --> enhance_sys
    Agent --> enhance_msgs
    Agent --> filter
    Agent --> recover
```

**Diagram: Extensibility Hook Call Sites**

Each hook is invoked at a specific point in the pipeline, allowing fine-grained control over agent behavior. For complete documentation, see [Extensibility Points](#2.8).

**Sources:** [src/vanna/core/agent/agent.py:363-389](), [src/vanna/core/agent/agent.py:784-814](), [src/vanna/core/agent/agent.py:870-902]()

---

## AgentConfig Structure

The `AgentConfig` class consolidates all configuration options:

```mermaid
graph TB
    subgraph "AgentConfig [config.py]"
        direction TB
        
        subgraph "Execution Control"
            max_iter["max_tool_iterations: int = 5"]
            stream["stream_responses: bool = True"]
            thinking["include_thinking_indicators: bool = False"]
            auto_save["auto_save_conversations: bool = True"]
        end
        
        subgraph "LLM Parameters"
            temp["temperature: float = 0.0"]
            max_tok["max_tokens: Optional[int] = None"]
            model["model: Optional[str] = None"]
        end
        
        subgraph "UI Features"
            ui_feat["ui_features: UiFeatures"]
            feat_map["feature_group_access: Dict[str, List[str]]"]
            can_access["can_user_access_feature(feature_name, user)"]
        end
        
        subgraph "Audit Configuration"
            audit["audit_config: AuditConfig"]
            enabled["enabled: bool = True"]
            log_checks["log_tool_access_checks: bool = True"]
            log_invoke["log_tool_invocations: bool = True"]
            log_ui["log_ui_feature_checks: bool = False"]
        end
    end
    
    max_iter --> Agent
    stream --> Agent
    temp --> Agent
    ui_feat --> Agent
    audit --> Agent
```

**Diagram: AgentConfig Parameters**

Configuration covers execution control, LLM parameters, UI feature gating, and audit logging. For details, see [AgentConfig and Configuration](#2.2).

**Sources:** [src/vanna/core/agent/config.py]()

---

## ToolRegistry and Permission Model

The `ToolRegistry` enforces access control at multiple levels:

```mermaid
sequenceDiagram
    participant Agent
    participant ToolRegistry
    participant Tool
    participant AuditLogger

    Note over Agent: Request to execute tool
    Agent->>ToolRegistry: execute(tool_call, context)
    
    Note over ToolRegistry: Phase 1: Tool Lookup
    ToolRegistry->>ToolRegistry: get_tool(tool_call.name)
    
    Note over ToolRegistry: Phase 2: Access Check
    ToolRegistry->>ToolRegistry: can_user_access_tool(user, tool)
    ToolRegistry->>ToolRegistry: Check user.group_memberships ∩ tool.access_groups
    
    alt Access Denied
        ToolRegistry->>AuditLogger: log_tool_access_check(access_granted=False)
        ToolRegistry-->>Agent: ToolResult(success=False, error="Permission denied")
    end
    
    ToolRegistry->>AuditLogger: log_tool_access_check(access_granted=True)
    
    Note over ToolRegistry: Phase 3: Argument Transformation
    ToolRegistry->>Tool: transform_args(args, context)
    Tool-->>ToolRegistry: transformed_args
    
    Note over ToolRegistry: Phase 4: Validation
    ToolRegistry->>ToolRegistry: Validate with ArgsSchema
    
    Note over ToolRegistry: Phase 5: Execution
    ToolRegistry->>AuditLogger: log_tool_invocation(tool_name, args)
    ToolRegistry->>Tool: execute(context, transformed_args)
    Tool-->>ToolRegistry: ToolResult
    ToolRegistry->>AuditLogger: log_tool_result(tool_name, success)
    
    ToolRegistry-->>Agent: ToolResult
```

**Diagram: ToolRegistry Execution Pipeline**

The registry performs access checks, argument transformation (for row-level security), validation, and execution with comprehensive audit logging. For details, see [ToolRegistry and Execution Pipeline](#2.4).

**Sources:** [src/vanna/core/registry.py]()

---

## WorkflowHandler and Command Routing

The `WorkflowHandler` provides deterministic workflow handling before LLM invocation:

```mermaid
graph TB
    subgraph "Message Arrival"
        msg["User Message"]
    end
    
    subgraph "WorkflowHandler.try_handle() [workflow/base.py]"
        check["Check message pattern"]
        
        subgraph "Built-in Commands"
            help["/help → Show available commands"]
            status["/status → Show system status"]
            memories["/memories → List recent memories"]
            delete["/delete → Delete conversation"]
        end
        
        subgraph "Custom Patterns"
            pattern1["Custom Pattern 1"]
            pattern2["Custom Pattern 2"]
        end
        
        should_skip["WorkflowResult(should_skip_llm=True/False)"]
    end
    
    subgraph "Agent Decision"
        skip["If should_skip_llm=True:<br/>  Yield components, exit"]
        proceed["If should_skip_llm=False:<br/>  Continue to LLM"]
    end
    
    msg --> check
    check --> help
    check --> status
    check --> memories
    check --> delete
    check --> pattern1
    check --> pattern2
    help --> should_skip
    status --> should_skip
    memories --> should_skip
    delete --> should_skip
    pattern1 --> should_skip
    pattern2 --> should_skip
    should_skip --> skip
    should_skip --> proceed
```

**Diagram: WorkflowHandler Command Routing**

The workflow handler enables fast, deterministic responses for commands and patterns without LLM overhead. For details, see [WorkflowHandler System](#2.5).

**Sources:** [src/vanna/core/workflow/base.py](), [src/vanna/core/workflow/default.py](), [src/vanna/core/agent/agent.py:440-509]()

---

## ConversationStore Implementations

Two conversation store implementations are provided:

```mermaid
graph TB
    subgraph "ConversationStore Interface [storage/base.py]"
        interface["get_conversation(conversation_id, user)<br/>update_conversation(conversation)<br/>delete_conversation(conversation_id, user)<br/>list_conversations(user, limit, offset)"]
    end
    
    subgraph "MemoryConversationStore [local/storage.py]"
        mem_data["In-Memory Dictionary<br/>conversations: Dict[str, Conversation]"]
        mem_pros["✓ Fast<br/>✓ No dependencies<br/>✓ Good for testing"]
        mem_cons["✗ Not persistent<br/>✗ Lost on restart"]
    end
    
    subgraph "FileSystemConversationStore [local/file_system_conversation_store.py]"
        fs_structure["Directory Structure:<br/>conversations/{id}/<br/>  metadata.json<br/>  messages/{timestamp}_{index}.json"]
        fs_pros["✓ Persistent<br/>✓ Human-readable<br/>✓ No database required"]
        fs_cons["✗ Slower for large datasets<br/>✗ No query optimization"]
    end
    
    interface --> mem_data
    interface --> fs_structure
    mem_data --> mem_pros
    mem_data --> mem_cons
    fs_structure --> fs_pros
    fs_structure --> fs_cons
```

**Diagram: ConversationStore Implementations**

Choose `MemoryConversationStore` for development/testing and `FileSystemConversationStore` for simple persistent storage. For production, implement a custom store backed by your database. For details, see [ConversationStore and History Management](#2.6).

**Sources:** [src/vanna/integrations/local/storage.py](), [src/vanna/integrations/local/file_system_conversation_store.py:19-256]()

---

## SystemPromptBuilder and Context Enhancement

The system prompt is built and enhanced in multiple stages:

```mermaid
sequenceDiagram
    participant Agent
    participant SystemPromptBuilder
    participant LlmContextEnhancer
    participant AgentMemory

    Note over Agent: Building LLM Request
    Agent->>SystemPromptBuilder: build_system_prompt(user, tool_schemas)
    SystemPromptBuilder-->>Agent: system_prompt (base)
    
    Note over Agent: Enhance with Context
    Agent->>LlmContextEnhancer: enhance_system_prompt(system_prompt, message, user)
    
    LlmContextEnhancer->>AgentMemory: search_similar_usage(question=message)
    AgentMemory-->>LlmContextEnhancer: List[MemorySearchResult]
    
    LlmContextEnhancer->>LlmContextEnhancer: Format memories as examples
    LlmContextEnhancer->>LlmContextEnhancer: Append to system_prompt
    
    LlmContextEnhancer-->>Agent: enhanced_system_prompt
    
    Note over Agent: Use in LLM Request
    Agent->>Agent: LlmRequest(system_prompt=enhanced_system_prompt, ...)
```

**Diagram: System Prompt Building and Enhancement**

The base system prompt includes tool schemas and instructions. The `LlmContextEnhancer` adds relevant memories from past successful interactions, creating a learning feedback loop. For details, see [SystemPromptBuilder](#2.7).

**Sources:** [src/vanna/core/agent/agent.py:592-637](), [src/vanna/core/system_prompt/base.py](), [src/vanna/core/enhancer.py]()

---

## Error Handling and Recovery

The agent provides comprehensive error handling at multiple levels:

```mermaid
graph TB
    subgraph "Agent.send_message() [agent.py:142-230]"
        try_outer["try:<br/>  await _send_message()"]
        catch_outer["except Exception as e:<br/>  Log full stack trace<br/>  Log to observability<br/>  Yield error UiComponent"]
    end
    
    subgraph "Tool Execution [agent.py:816-936]"
        try_tool["try:<br/>  result = await registry.execute()"]
        catch_tool["except ToolExecutionError as e:<br/>  Log error<br/>  Check error_recovery_strategy"]
        
        subgraph "ErrorRecoveryStrategy [recovery.py]"
            retry["RecoveryAction(type=RETRY)"]
            skip["RecoveryAction(type=SKIP)"]
            abort["RecoveryAction(type=ABORT)"]
        end
    end
    
    subgraph "LLM Errors [agent.py:652-656]"
        llm_error["LlmServiceError:<br/>  Log to observability<br/>  Yield error component"]
    end
    
    try_outer --> try_tool
    try_outer --> catch_outer
    try_tool --> catch_tool
    catch_tool --> retry
    catch_tool --> skip
    catch_tool --> abort
    try_outer --> llm_error
```

**Diagram: Error Handling Layers**

Errors are caught at the agent level, tool level, and LLM level. The `ErrorRecoveryStrategy` hook allows custom retry logic. All errors are logged to observability providers and surfaced to users via UI components.

**Sources:** [src/vanna/core/agent/agent.py:142-230](), [src/vanna/core/agent/agent.py:816-936](), [src/vanna/core/recovery.py]()

---

## Observability Integration

The agent integrates observability throughout the pipeline:

```mermaid
graph TB
    subgraph "Observability Points"
        user_res["User Resolution<br/>[agent.py:251-267]"]
        conv_load["Conversation Load<br/>[agent.py:410-437]"]
        schema_fetch["Tool Schema Fetch<br/>[agent.py:565-582]"]
        prompt_build["System Prompt Build<br/>[agent.py:592-637]"]
        llm_call["LLM Request/Stream<br/>[agent.py:646-1090]"]
        tool_exec["Tool Execution<br/>[agent.py:816-936]"]
        hook_exec["Hook Execution<br/>[agent.py:363-389, 784-814]"]
    end
    
    subgraph "Metrics Recorded"
        duration["Duration (ms)"]
        count["Count"]
        error_rate["Error Rate"]
        token_usage["Token Usage"]
    end
    
    subgraph "Spans Created"
        span_user["agent.user_resolution"]
        span_conv["agent.conversation.load"]
        span_schema["agent.tool_schemas.fetch"]
        span_prompt["agent.system_prompt.build"]
        span_llm["agent.llm.request"]
        span_tool["agent.tool.execute"]
        span_hook["agent.hook.before_message<br/>agent.hook.before_tool<br/>agent.hook.after_tool"]
    end
    
    user_res --> span_user
    conv_load --> span_conv
    schema_fetch --> span_schema
    prompt_build --> span_prompt
    llm_call --> span_llm
    tool_exec --> span_tool
    hook_exec --> span_hook
    
    span_user --> duration
    span_tool --> duration
    span_tool --> error_rate
    span_llm --> token_usage
```

**Diagram: Observability Integration Points**

The agent creates spans and records metrics for all major operations, enabling performance monitoring and debugging in production. Observability is optional and controlled by the `observability_provider` parameter.

**Sources:** [src/vanna/core/agent/agent.py:251-267](), [src/vanna/core/agent/agent.py:565-582](), [src/vanna/core/agent/agent.py:816-866]()

---

## Summary

The Vanna core architecture provides:

1. **Central Orchestration**: `Agent` class coordinates all components
2. **Interface-Driven Design**: Swap implementations without changing core code
3. **Comprehensive Security**: Multi-layer access control via `UserResolver`, `ToolRegistry`, and `ToolContext`
4. **Extensibility**: Seven hook points for customization
5. **Observability**: Built-in tracing and metrics
6. **Error Resilience**: Multi-level error handling with recovery strategies
7. **Streaming Support**: Real-time UI updates via `UiComponent` stream
8. **Configuration**: Centralized via `AgentConfig`

For detailed documentation of each component, see the subsections [2.1](#2.1) through [2.8](#2.8).

**Sources:** [src/vanna/core/agent/agent.py](), [src/vanna/core/__init__.py](), [src/vanna/__init__.py]()

---

