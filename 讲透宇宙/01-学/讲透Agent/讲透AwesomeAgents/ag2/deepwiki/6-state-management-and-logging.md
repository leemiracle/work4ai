<!-- source: DeepWiki mcp.deepwiki.com · repo ag2ai/ag2 · page 6 State Management and Logging · fetched 2026-10-26 -->

# State Management and Logging

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [autogen/agentchat/contrib/swarm_agent.py](autogen/agentchat/contrib/swarm_agent.py)
- [autogen/logger/base_logger.py](autogen/logger/base_logger.py)
- [autogen/logger/file_logger.py](autogen/logger/file_logger.py)
- [autogen/logger/logger_factory.py](autogen/logger/logger_factory.py)
- [autogen/logger/logger_utils.py](autogen/logger/logger_utils.py)
- [autogen/logger/sqlite_logger.py](autogen/logger/sqlite_logger.py)
- [autogen/runtime_logging.py](autogen/runtime_logging.py)
- [autogen/tools/dependency_injection.py](autogen/tools/dependency_injection.py)
- [autogen/tools/function_utils.py](autogen/tools/function_utils.py)
- [notebook/agentchat_logging.ipynb](notebook/agentchat_logging.ipynb)
- [scripts/pre-commit-mypy-run.sh](scripts/pre-commit-mypy-run.sh)
- [test/agentchat/contrib/test_swarm.py](test/agentchat/contrib/test_swarm.py)
- [test/agentchat/test_agent_file_logging.py](test/agentchat/test_agent_file_logging.py)
- [test/logger/__init__.py](test/logger/__init__.py)
- [test/logger/test_file_logger_redaction.py](test/logger/test_file_logger_redaction.py)
- [test/test_logging.py](test/test_logging.py)
- [test/tools/test_dependency_injection.py](test/tools/test_dependency_injection.py)
- [test/tools/test_function_utils.py](test/tools/test_function_utils.py)

</details>



This page provides an overview of AG2's systems for managing agent state, tracking runtime behavior, and responding to lifecycle events. These capabilities enable agents to share contextual information, persist execution history for analysis, and react to changes in their environment.

For details on specific state management patterns in SwarmAgent, see [ContextVariables and Shared State](#6.1). For comprehensive logging system documentation, see [Runtime Logging System](#6.2). For hook registration and lifecycle events, see [Hooks and Lifecycle Management](#6.3).

## Core State and Logging Systems

AG2 provides three interconnected systems for managing agent state and tracking execution:

**System Architecture Overview**
```mermaid
graph TB
    subgraph "State Management"
        CV["ContextVariables<br/>Shared state dictionary"]
        SWARM["SwarmAgent<br/>context_variables attribute"]
        TOOLS["Tool Functions<br/>Depends injection"]
    end
    
    subgraph "Runtime Logging"
        RL_MODULE["runtime_logging module<br/>start/stop/log_* functions"]
        LOGGER_FACTORY["LoggerFactory<br/>get_logger"]
        SQLITE["SqliteLogger<br/>logs.db tables"]
        FILE["FileLogger<br/>runtime.log"]
    end
    
    subgraph "Lifecycle Hooks"
        REGISTER["ConversableAgent.register_hook"]
        HOOKS["Hook Functions<br/>update_agent_state<br/>process_all_messages_before_reply"]
        UPDATE["UpdateSystemMessage<br/>Dynamic system message"]
    end
    
    CV -->|injected into| TOOLS
    SWARM -->|maintains| CV
    TOOLS -->|update| CV
    
    RL_MODULE -->|creates| LOGGER_FACTORY
    LOGGER_FACTORY -->|sqlite type| SQLITE
    LOGGER_FACTORY -->|file type| FILE
    
    REGISTER -->|registers| HOOKS
    HOOKS -->|triggered by| SWARM
    UPDATE -->|uses| CV
    
    SWARM -->|logs to| RL_MODULE
    HOOKS -->|logs to| RL_MODULE
```

**ContextVariables**: A dictionary-like container for sharing state across agents in a swarm. Tools can read and modify context variables through dependency injection, enabling stateful multi-agent workflows. Defined in [autogen/agentchat/group/context_variables.py]().

**Runtime Logging**: A pluggable logging system that captures chat completions, agent creation, function calls, and custom events. Supports SQLite and file-based backends for post-execution analysis. Managed via [autogen/runtime_logging.py:1-162]().

**Lifecycle Hooks**: Callback functions registered to execute at specific points in an agent's lifecycle, such as before generating a reply or when the agent state updates.

Sources: [autogen/agentchat/contrib/swarm_agent.py:1-100](), [autogen/runtime_logging.py:1-162](), [autogen/logger/base_logger.py:1-130]()

## ContextVariables in SwarmAgent

`ContextVariables` provides a shared state mechanism for `SwarmAgent` workflows. Each agent in a swarm maintains a reference to the same `ContextVariables` instance, enabling state coordination across agent transitions.

**Context Flow in SwarmChat**
```mermaid
graph LR
    INIT["initiate_swarm_chat"]
    CV_PARAM["ContextVariables instance"]
    AGENT1["SwarmAgent 1<br/>agent.context_variables"]
    AGENT2["SwarmAgent 2<br/>agent.context_variables"]
    TOOL_EXEC["Tool Executor<br/>_Swarm_Tool_Executor"]
    MANAGER["GroupChatManager<br/>manager.context_variables"]
    
    TOOL1["Tool Function<br/>with context_variables param"]
    INJECT["Depends injection<br/>on context_variables"]
    
    INIT -->|creates or receives| CV_PARAM
    CV_PARAM -->|assigned to| AGENT1
    CV_PARAM -->|assigned to| AGENT2
    CV_PARAM -->|assigned to| TOOL_EXEC
    CV_PARAM -->|assigned to| MANAGER
    
    TOOL1 -->|modified with| INJECT
    INJECT -->|injects| CV_PARAM
    TOOL1 -->|updates| CV_PARAM
```

Key implementation details:

- **Initialization**: Created at swarm startup in `_setup_context_variables` [autogen/agentchat/contrib/swarm_agent.py:2901-2917]().
- **Assignment**: All agents receive the same reference during swarm preparation [autogen/agentchat/contrib/swarm_agent.py:2915-2916]().
- **Tool Integration**: Functions with `context_variables` parameters get dependency injection via `_change_tool_context_variables_to_depends` [autogen/agentchat/contrib/swarm_agent.py:2661-2689]().
- **Parameter Hiding**: The `context_variables` parameter is removed from tool schemas sent to LLMs to prevent agents from attempting to pass it manually [autogen/agentchat/contrib/swarm_agent.py:2691-2712]().

Sources: [autogen/agentchat/contrib/swarm_agent.py:2661-2917](), [test/agentchat/contrib/test_swarm.py:370-498]()

## Runtime Logging Architecture

The runtime logging system provides a unified interface for capturing agent interactions and LLM calls. The system uses a factory pattern to support multiple backend implementations.

**Logging Data Flow**
```mermaid
graph TB
    subgraph "Public API"
        START["runtime_logging.start()<br/>logger_type, config"]
        STOP["runtime_logging.stop()"]
        LOG_CHAT["runtime_logging.log_chat_completion()"]
        LOG_AGENT["runtime_logging.log_new_agent()"]
        LOG_EVENT["runtime_logging.log_event()"]
        LOG_FUNC["runtime_logging.log_function_use()"]
    end
    
    subgraph "Logger Factory"
        FACTORY["LoggerFactory.get_logger()<br/>Returns BaseLogger"]
    end
    
    subgraph "Logger Implementations"
        BASE["BaseLogger<br/>Abstract interface"]
        SQLITE_IMPL["SqliteLogger<br/>session_id, con, cur"]
        FILE_IMPL["FileLogger<br/>session_id, log_file"]
    end
    
    subgraph "Storage Backends"
        SQLITE_DB["SQLite Database<br/>logs.db<br/>Tables: chat_completions<br/>agents, oai_wrappers<br/>oai_clients, events<br/>function_calls"]
        LOG_FILE["Log File<br/>runtime.log<br/>JSON lines format"]
    end
    
    START -->|creates| FACTORY
    FACTORY -->|implements| BASE
    BASE -.->|extends| SQLITE_IMPL
    BASE -.->|extends| FILE_IMPL
    
    LOG_CHAT -->|delegates to| SQLITE_IMPL
    LOG_CHAT -->|delegates to| FILE_IMPL
    LOG_AGENT -->|delegates to| SQLITE_IMPL
    LOG_EVENT -->|delegates to| SQLITE_IMPL
    LOG_FUNC -->|delegates to| SQLITE_IMPL
    
    SQLITE_IMPL -->|writes to| SQLITE_DB
    FILE_IMPL -->|writes to| LOG_FILE
    
    STOP -->|closes| SQLITE_IMPL
    STOP -->|closes| FILE_IMPL
```

### Logging Workflow

| Step | Function | Purpose |
|------|----------|---------|
| 1 | `runtime_logging.start()` | Initialize logger, create session_id, set up storage [autogen/runtime_logging.py:41-66]() |
| 2 | Agent operations | Framework automatically logs via wrapper methods |
| 3 | `runtime_logging.log_*()` | Manual logging of custom events or function calls [autogen/runtime_logging.py:97-110]() |
| 4 | `runtime_logging.stop()` | Close connections, flush buffers [autogen/runtime_logging.py:145-150]() |
| 5 | Query logs | Use `get_connection()` to access the underlying SQLite connection [autogen/runtime_logging.py:152-158]() |

### Logged Information

The logging system captures:

- **Chat Completions**: Every LLM call with request, response, cost, and caching status [autogen/logger/base_logger.py:37-66]().
- **Agent Creation**: Agent initialization with configuration (excluding API keys) [autogen/logger/base_logger.py:68-76]().
- **Events**: Custom events with arbitrary key-value data [autogen/logger/base_logger.py:78-87]().
- **Function Calls**: Tool/function executions with arguments and return values [autogen/logger/base_logger.py:110-120]().
- **Wrappers and Clients**: `OpenAIWrapper` and LLM client instantiation [autogen/logger/base_logger.py:89-108]().

Sources: [autogen/runtime_logging.py:1-162](), [autogen/logger/base_logger.py:1-130](), [autogen/logger/sqlite_logger.py:1-525](), [autogen/logger/file_logger.py:1-263]()

## SQLite Logger Schema

The `SqliteLogger` stores data in a relational schema designed for traceability across sessions.

**Database Schema (SqliteLogger)**
```mermaid
erDiagram
    chat_completions {
        INTEGER id PK
        TEXT invocation_id
        INTEGER client_id
        INTEGER wrapper_id
        TEXT session_id
        TEXT source_name
        TEXT request
        TEXT response
        INTEGER is_cached
        REAL cost
        DATETIME start_time
        DATETIME end_time
    }
    
    agents {
        INTEGER id PK
        INTEGER agent_id
        INTEGER wrapper_id
        TEXT session_id
        TEXT name
        TEXT class
        TEXT init_args
        DATETIME timestamp
    }
    
    oai_wrappers {
        INTEGER id PK
        INTEGER wrapper_id
        TEXT session_id
        TEXT init_args
        DATETIME timestamp
    }
    
    oai_clients {
        INTEGER id PK
        INTEGER client_id
        INTEGER wrapper_id
        TEXT session_id
        TEXT class
        TEXT init_args
        DATETIME timestamp
    }
    
    events {
        INTEGER id PK
        TEXT event_name
        INTEGER source_id
        TEXT source_name
        TEXT agent_module
        TEXT agent_class_name
        TEXT json_state
        DATETIME timestamp
    }
    
    function_calls {
        INTEGER source_id
        TEXT source_name
        TEXT function_name
        TEXT args
        TEXT returns
        DATETIME timestamp
    }
    
    version {
        INTEGER id PK
        INTEGER version_number
    }
    
    chat_completions }o--|| agents : "source_name"
    chat_completions }o--|| oai_wrappers : "wrapper_id"
    chat_completions }o--|| oai_clients : "client_id"
    agents }o--|| oai_wrappers : "wrapper_id"
    oai_clients }o--|| oai_wrappers : "wrapper_id"
```

**Key Fields:**
- `session_id`: UUID linking all records from a single `start()` call [autogen/logger/sqlite_logger.py:82]().
- `invocation_id`: UUID for a single `OpenAIWrapper.create()` invocation [autogen/logger/sqlite_logger.py:91]().
- `is_cached`: 1 if response came from cache, 0 otherwise [autogen/logger/sqlite_logger.py:98]().
- `cost`: Calculated token cost for the completion [autogen/logger/sqlite_logger.py:99]().

The schema includes a versioning system to manage database migrations [autogen/logger/sqlite_logger.py:144-150]().

Sources: [autogen/logger/sqlite_logger.py:86-176](), [test/test_logging.py:88-243]()

## Hook System Integration

Hooks enable custom logic at specific agent lifecycle points. SwarmAgent uses hooks for conditional transitions and state updates.

**Hook Execution Sequence**
```mermaid
sequenceDiagram
    participant Agent as ConversableAgent
    participant Hook as Registered Hook
    participant State as Context/State
    
    Note over Agent: register_hook("update_agent_state", func)
    
    Agent->>Agent: generate_reply() called
    Agent->>Hook: Trigger "update_agent_state"
    Hook->>State: Read context_variables
    Hook->>Hook: Execute conditional logic
    Hook->>Agent: Update function map
    Agent->>Agent: Continue reply generation
    
    Note over Agent: Hook can modify:<br/>- agent._function_map<br/>- tool availability<br/>- state variables
```

### SwarmAgent Hook Usage

SwarmAgent registers two key hooks during initialization:

1. **`update_agent_state` Hook**: Updates conditional function availability based on the current context [autogen/agentchat/contrib/swarm_agent.py:251]().
   - Implementation: `_update_conditional_functions` [autogen/agentchat/contrib/swarm_agent.py:1843-1859]().
2. **Context Condition Reply Function**: Evaluates `OnContextCondition` transitions before standard LLM reply generation [autogen/agentchat/contrib/swarm_agent.py:257]().
   - Implementation: `_run_oncontextconditions` [autogen/agentchat/contrib/swarm_agent.py:277-312]().

### UpdateSystemMessage Hook

`UpdateSystemMessage` is a specialized hook for dynamically updating agent system messages based on context. It can be a string template or a callable [autogen/agentchat/conversable_agent.py]().

| Property | Description |
|----------|-------------|
| Creation | `UpdateSystemMessage(message_or_callable)` |
| Execution Time | Before each reply generation |
| Variable Substitution | Uses `context_variables` for template rendering |

Sources: [autogen/agentchat/contrib/swarm_agent.py:229-312](), [autogen/agentchat/contrib/swarm_agent.py:1843-1859](), [test/agentchat/contrib/test_swarm.py:632-716]()

## Integration: State, Logging, and Hooks

The three systems work together in agent workflows:

**Integrated Execution Flow**
```mermaid
graph TB
    subgraph "Agent Lifecycle Event"
        EVENT["Agent generates reply"]
    end
    
    subgraph "Hook Execution"
        HOOK1["update_agent_state hook"]
        HOOK2["UpdateSystemMessage hook"]
        READ_CV["Read ContextVariables"]
        UPDATE_AGENT["Modify agent state"]
    end
    
    subgraph "State Management"
        CV_UPDATE["Update ContextVariables<br/>via tool execution"]
        CV_EVAL["Evaluate OnContextCondition"]
    end
    
    subgraph "Logging Capture"
        LOG1["log_new_agent on creation"]
        LOG2["log_chat_completion on LLM call"]
        LOG3["log_function_use on tool call"]
        LOG4["log_event for custom events"]
    end
    
    subgraph "Storage"
        PERSIST["Persist to SQLite/File"]
    end
    
    EVENT -->|triggers| HOOK1
    EVENT -->|triggers| HOOK2
    
    HOOK1 -->|reads| READ_CV
    HOOK2 -->|reads| READ_CV
    READ_CV -->|provides| CV_EVAL
    READ_CV -->|provides| UPDATE_AGENT
    
    UPDATE_AGENT -->|modifies| CV_UPDATE
    CV_EVAL -->|controls| CV_UPDATE
    
    EVENT -->|logs| LOG1
    EVENT -->|logs| LOG2
    CV_UPDATE -->|logs| LOG3
    HOOK1 -->|logs| LOG4
    
    LOG1 -->|writes| PERSIST
    LOG2 -->|writes| PERSIST
    LOG3 -->|writes| PERSIST
    LOG4 -->|writes| PERSIST
```

This integration enables:
- **Stateful multi-agent workflows** with shared context via `ContextVariables`.
- **Complete execution traces** for debugging and analysis via `runtime_logging`.
- **Dynamic agent behavior** based on runtime state using lifecycle hooks.

Sources: [autogen/agentchat/contrib/swarm_agent.py:229-570](), [autogen/runtime_logging.py:41-162](), [autogen/logger/logger_utils.py:1-163]()

---

