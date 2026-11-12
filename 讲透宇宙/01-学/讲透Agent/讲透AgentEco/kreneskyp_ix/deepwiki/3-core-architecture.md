<!-- source: DeepWiki mcp.deepwiki.com · repo kreneskyp/ix · page 3 Core Architecture · fetched 2026-10-27 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ix/agents/history.py](ix/agents/history.py)
- [ix/agents/process.py](ix/agents/process.py)
- [ix/agents/tests/test_history.py](ix/agents/tests/test_history.py)
- [ix/agents/tests/test_process.py](ix/agents/tests/test_process.py)
- [ix/api/components/types.py](ix/api/components/types.py)
- [ix/chains/loaders/__init__.py](ix/chains/loaders/__init__.py)
- [ix/chains/loaders/core.py](ix/chains/loaders/core.py)
- [ix/chains/loaders/memory.py](ix/chains/loaders/memory.py)
- [ix/chains/migrations/0005_refine_node_type.py](ix/chains/migrations/0005_refine_node_type.py)
- [ix/chains/models.py](ix/chains/models.py)
- [ix/conftest.py](ix/conftest.py)
- [ix/pg_vector/tests/models.py](ix/pg_vector/tests/models.py)
- [ix/task_log/models.py](ix/task_log/models.py)
- [ix/task_log/tasks/agent_runner.py](ix/task_log/tasks/agent_runner.py)
- [ix/task_log/tests/fake.py](ix/task_log/tests/fake.py)

</details>



This document provides a comprehensive overview of the IX AI agent platform's core architecture, focusing on the fundamental systems that enable visual chain building, agent execution, and LangChain integration. The architecture consists of four primary subsystems: the Chain System for workflow definition and execution, the Agent Execution System for runtime processing, the Component Integration layer for LangChain components, and the supporting data models and context management.

For specific implementation details of individual subsystems, see [Chain System](#3.1), [Agent Execution System](#3.2), and [Component Integration](#3.3).

## System Overview

The IX platform is built around a modular architecture that separates workflow definition from execution, enabling visual chain building while maintaining full compatibility with LangChain's ecosystem.

### Core System Architecture

```mermaid
graph TB
    subgraph "Database Layer"
        Chain[Chain]
        ChainNode[ChainNode]
        ChainEdge[ChainEdge]
        NodeType[NodeType]
        Task[Task]
        TaskLogMessage[TaskLogMessage]
        Agent[Agent]
    end
    
    subgraph "Chain Loading System"
        CoreLoader["ix.chains.loaders.core"]
        FlowPlaceholder[FlowPlaceholder]
        IxContext[IxContext]
        ChainLoader["Chain.load_chain()"]
    end
    
    subgraph "Agent Execution System"
        AgentProcess["ix.agents.process.AgentProcess"]
        IxHandler["ix.chains.callbacks.IxHandler"]
        TaskHistory["ix.agents.history.TaskHistory"]
    end
    
    subgraph "Component Integration"
        NodeTypeManager["NodeType.objects"]
        ComponentLoaders["get_node_loader()"]
        PropertyLoaders["get_property_loader()"]
        NodeInitializers["get_node_initializer()"]
    end
    
    subgraph "LangChain Runtime"
        Runnable["langchain.schema.runnable.Runnable"]
        RunnableSequence["RunnableSequence"]
        RunnableParallel["RunnableParallel"]
        IxNode["ix.runnable.ix.IxNode"]
    end
    
    Chain --> ChainLoader
    ChainNode --> CoreLoader
    ChainEdge --> CoreLoader
    NodeType --> ComponentLoaders
    
    ChainLoader --> FlowPlaceholder
    CoreLoader --> IxContext
    CoreLoader --> Runnable
    
    Task --> AgentProcess
    Agent --> AgentProcess
    AgentProcess --> IxHandler
    AgentProcess --> ChainLoader
    
    IxHandler --> TaskLogMessage
    ComponentLoaders --> Runnable
    Runnable --> IxNode
```

Sources: [ix/chains/models.py:288-362](), [ix/agents/process.py:29-79](), [ix/chains/loaders/core.py:1-968](), [ix/task_log/models.py:13-239]()

## Chain System Architecture

The Chain System provides the foundation for visual workflow definition and execution, converting graph-based representations into executable LangChain runnables.

### Chain Data Model

```mermaid
erDiagram
    Chain ||--o{ ChainNode : contains
    Chain ||--o{ ChainEdge : contains
    ChainNode ||--o{ ChainEdge : "source/target"
    ChainNode }o--|| NodeType : "defines type"
    
    Chain {
        uuid id
        string name
        text description
        boolean is_agent
    }
    
    ChainNode {
        uuid id
        string class_path
        json config
        string name
        boolean root
        json position
    }
    
    ChainEdge {
        uuid id
        string source_key
        string target_key
        string relation
        json input_map
    }
    
    NodeType {
        uuid id
        string name
        string class_path
        string type
        json connectors
        json fields
        json config_schema
    }
```

Sources: [ix/chains/models.py:288-362](), [ix/chains/models.py:230-287](), [ix/chains/models.py:263-287](), [ix/chains/models.py:45-104]()

### Chain Loading Process

The chain loading system transforms database representations into executable LangChain components through a multi-phase process:

```mermaid
sequenceDiagram
    participant Client
    participant ChainModel as "Chain"
    participant CoreLoader as "chains.loaders.core"
    participant FlowSystem as "Flow Placeholders"
    participant LangChain as "LangChain Runnables"
    
    Client->>ChainModel: "load_chain(context)"
    ChainModel->>CoreLoader: "init_chain_flow()"
    CoreLoader->>CoreLoader: "load_chain_flow()"
    CoreLoader->>FlowSystem: "load_flow_node()"
    FlowSystem->>FlowSystem: "load_flow_sequence()"
    FlowSystem-->>CoreLoader: "FlowPlaceholder"
    CoreLoader->>CoreLoader: "init_flow_node()"
    CoreLoader->>LangChain: "Create Runnables"
    LangChain-->>CoreLoader: "Runnable"
    CoreLoader-->>ChainModel: "Executable Chain"
    ChainModel-->>Client: "Runnable"
```

Sources: [ix/chains/models.py:316-324](), [ix/chains/loaders/core.py:512-534](), [ix/chains/loaders/core.py:564-578](), [ix/chains/loaders/core.py:895-968]()

## Agent Execution Architecture

The Agent Execution System manages the runtime execution of AI agents, handling task lifecycle, message logging, and callback management.

### Agent Process Lifecycle

```mermaid
stateDiagram-v2
    [*] --> AgentProcess_Created
    AgentProcess_Created --> Task_Started : "start(inputs)"
    Task_Started --> Chain_Loading : "chat_with_ai()"
    Chain_Loading --> Context_Creation : "IxContext.afrom_task()"
    Context_Creation --> Chain_Execution : "chain.ainvoke()"
    Chain_Execution --> Callback_Handling : "IxHandler callbacks"
    Callback_Handling --> Message_Logging : "TaskLogMessage"
    Message_Logging --> Task_Complete : "return response"
    Task_Complete --> [*]
    
    Chain_Execution --> Error_Handling : "Exception"
    Error_Handling --> Message_Logging : "handler.send_error_msg()"
```

Sources: [ix/agents/process.py:29-79](), [ix/chains/callbacks.py:1-500](), [ix/task_log/models.py:80-151]()

### Task and Message Management

```mermaid
graph LR
    subgraph "Task Management"
        Task["Task"]
        TaskTree["Task Hierarchy"]
        TaskDelegation["adelegate_to_agent()"]
    end
    
    subgraph "Message Logging"
        TaskLogMessage["TaskLogMessage"]
        MessageTypes["SYSTEM/ASSISTANT/USER"]
        MessageContent["JSON Content"]
    end
    
    subgraph "Agent History"
        TaskHistory["TaskHistory"]
        MessageHistory["history[]"]
        AutonomousMode["autonomous flag"]
    end
    
    Task --> TaskLogMessage
    Task --> TaskHistory
    TaskLogMessage --> MessageTypes
    TaskLogMessage --> MessageContent
    TaskHistory --> MessageHistory
    TaskHistory --> AutonomousMode
    
    Task --> TaskDelegation
    TaskDelegation --> Task
```

Sources: [ix/task_log/models.py:13-71](), [ix/task_log/models.py:80-151](), [ix/agents/history.py:11-157]()

## Component Integration Architecture

The Component Integration layer provides a bridge between IX's visual interface and LangChain's component ecosystem, enabling seamless integration of AI components.

### NodeType System

```mermaid
graph TB
    subgraph "Component Definition"
        NodeType_Model["NodeType Model"]
        Fields["NodeTypeField[]"]
        Connectors["Connector[]"]
        ConfigSchema["config_schema"]
    end
    
    subgraph "Loading System"
        NodeLoaders["get_node_loader()"]
        PropertyLoaders["get_property_loader()"]
        NodeInitializers["get_node_initializer()"]
    end
    
    subgraph "Runtime Creation"
        LoadNode["load_node()"]
        ImportClass["import_node_class()"]
        ComponentInstance["LangChain Component"]
    end
    
    NodeType_Model --> Fields
    NodeType_Model --> Connectors
    NodeType_Model --> ConfigSchema
    
    NodeType_Model --> NodeLoaders
    NodeLoaders --> LoadNode
    PropertyLoaders --> LoadNode
    NodeInitializers --> LoadNode
    
    LoadNode --> ImportClass
    ImportClass --> ComponentInstance
```

Sources: [ix/api/components/types.py:484-630](), [ix/chains/loaders/core.py:40-87](), [ix/chains/loaders/core.py:154-323]()

### Component Loading Flow

The component loading system handles the instantiation and configuration of LangChain components from IX node definitions:

```mermaid
flowchart TD
    Start["load_node(ChainNode)"] --> LoadType["Get NodeType"]
    LoadType --> ValidateConfig["Validate Config"]
    ValidateConfig --> LoadSecrets["load_secrets()"]
    LoadSecrets --> LoadProperties["Load Properties"]
    LoadProperties --> LoadFlowProps["load_flow_props()"]
    LoadFlowProps --> GroupFields["Group Fields"]
    GroupFields --> ImportClass["import_node_class()"]
    ImportClass --> CheckInitializer{"Node Initializer?"}
    CheckInitializer -->|Yes| CustomInit["Custom Initializer"]
    CheckInitializer -->|No| StandardInit["Standard __init__"]
    CustomInit --> Instance["Component Instance"]
    StandardInit --> Instance
    Instance --> Return["Return Component"]
```

Sources: [ix/chains/loaders/core.py:154-323](), [ix/chains/loaders/core.py:89-119](), [ix/chains/loaders/core.py:121-152]()

## Context and Memory Management

The platform provides sophisticated context management for maintaining state across agent executions and chain invocations.

### IxContext System

```mermaid
graph LR
    subgraph "Context Creation"
        TaskContext["IxContext.from_task()"]
        ContextData["task_id, agent_id, chat_id, user_id"]
        MemoryAccess["Memory Access"]
    end
    
    subgraph "Memory Management"
        MemoryLoaders["load_memory_config()"]
        SessionScoping["Session Scoping"]
        MemoryBackends["Memory Backends"]
    end
    
    subgraph "Secret Management"
        SecretLoading["load_secrets()"]
        VaultAccess["Vault Access"]
        ConfigSecurity["Secure Config"]
    end
    
    TaskContext --> ContextData
    ContextData --> MemoryAccess
    MemoryAccess --> MemoryLoaders
    MemoryLoaders --> SessionScoping
    SessionScoping --> MemoryBackends
    
    TaskContext --> SecretLoading
    SecretLoading --> VaultAccess
    VaultAccess --> ConfigSecurity
```

Sources: [ix/chains/loaders/context.py:1-200](), [ix/chains/loaders/memory.py:48-171](), [ix/chains/loaders/core.py:89-119]()

## Flow Execution System

The Flow Execution System handles the complex task of converting visual node graphs into executable LangChain flows, managing parallel execution, branching, and data flow.

### Flow Placeholder Architecture

```mermaid
graph TB
    subgraph "Flow Placeholders"
        FlowPlaceholder["FlowPlaceholder Union"]
        SequencePlaceholder["SequencePlaceholder"]
        MapPlaceholder["MapPlaceholder"]
        BranchPlaceholder["BranchPlaceholder"]
        AggPlaceholder["AggPlaceholder"]
        ImplicitJoin["ImplicitJoin"]
    end
    
    subgraph "Flow Processing"
        LoadFlowNode["load_flow_node()"]
        LoadFlowSequence["load_flow_sequence()"]
        LoadFlowMap["load_flow_map()"]
        LoadFlowBranch["load_flow_branch()"]
    end
    
    subgraph "Runtime Conversion"
        InitFlowNode["init_flow_node()"]
        RunnableSequence["RunnableSequence"]
        RunnableParallel["RunnableParallel"]
        InitBranch["init_branch()"]
    end
    
    FlowPlaceholder --> SequencePlaceholder
    FlowPlaceholder --> MapPlaceholder
    FlowPlaceholder --> BranchPlaceholder
    FlowPlaceholder --> AggPlaceholder
    FlowPlaceholder --> ImplicitJoin
    
    LoadFlowNode --> LoadFlowSequence
    LoadFlowNode --> LoadFlowMap
    LoadFlowNode --> LoadFlowBranch
    
    InitFlowNode --> RunnableSequence
    InitFlowNode --> RunnableParallel
    InitFlowNode --> InitBranch
```

Sources: [ix/chains/loaders/core.py:348-464](), [ix/chains/loaders/core.py:580-644](), [ix/chains/loaders/core.py:706-874](), [ix/chains/loaders/core.py:895-968]()

This architecture enables IX to provide a powerful visual interface for building AI agents while maintaining full compatibility with LangChain's extensive ecosystem of components and tools.

---

