<!-- source: DeepWiki mcp.deepwiki.com · repo kyegomez/swarms · page 2 Core Agent System · fetched 2026-10-26 -->

# Core Agent System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [README.md](README.md)
- [docs/mkdocs.yml](docs/mkdocs.yml)
- [example.py](example.py)
- [pyproject.toml](pyproject.toml)
- [requirements.txt](requirements.txt)
- [swarms/__init__.py](swarms/__init__.py)
- [swarms/agents/__init__.py](swarms/agents/__init__.py)
- [swarms/prompts/logistics.py](swarms/prompts/logistics.py)
- [swarms/prompts/sop_generator_agent_prompt.py](swarms/prompts/sop_generator_agent_prompt.py)
- [swarms/structs/__init__.py](swarms/structs/__init__.py)
- [swarms/structs/agent.py](swarms/structs/agent.py)
- [swarms/structs/concurrent_workflow.py](swarms/structs/concurrent_workflow.py)
- [swarms/structs/rearrange.py](swarms/structs/rearrange.py)
- [swarms/structs/sequential_workflow.py](swarms/structs/sequential_workflow.py)
- [swarms/structs/swarm_router.py](swarms/structs/swarm_router.py)
- [swarms/utils/__init__.py](swarms/utils/__init__.py)

</details>



## Purpose and Scope

The Core Agent System provides the foundational infrastructure for creating, configuring, and orchestrating intelligent agents within the Swarms framework. This system encompasses the primary `Agent` class, the `SwarmRouter` factory pattern, and core orchestration mechanisms that enable both single-agent and multi-agent workflows.

This document covers the architectural overview and integration patterns of the core system. For detailed implementation specifics of individual agents, see [Agent Class](#2.1). For comprehensive SwarmRouter configuration and usage, see [SwarmRouter](#2.2). For multi-agent collaboration patterns, see [Multi-Agent Orchestration](#3).

## System Architecture Overview

The Core Agent System operates as a layered architecture where individual agents serve as the fundamental building blocks, orchestrated through various workflow patterns via the SwarmRouter factory system.

```mermaid
graph TB
    subgraph "Core Agent Foundation"
        Agent["Agent"]
        LiteLLM["LiteLLM"]
        BaseTool["BaseTool"]
        Conversation["Conversation"]
    end
    
    subgraph "Orchestration Layer"
        SwarmRouter["SwarmRouter"]
        SwarmType["SwarmType"]
    end
    
    subgraph "Workflow Implementations"
        SequentialWorkflow["SequentialWorkflow"]
        ConcurrentWorkflow["ConcurrentWorkflow"]
        AgentRearrange["AgentRearrange"]
        HierarchicalSwarm["HierarchicalSwarm"]
        GroupChat["GroupChat"]
    end
    
    subgraph "Integration Systems"
        MCPConnection["MCPConnection"]
        RAGHandler["AgentRAGHandler"]
        SafeStateManager["SafeStateManager"]
    end
    
    Agent --> LiteLLM
    Agent --> BaseTool
    Agent --> Conversation
    Agent --> MCPConnection
    Agent --> RAGHandler
    Agent --> SafeStateManager
    
    SwarmRouter --> SwarmType
    SwarmRouter --> SequentialWorkflow
    SwarmRouter --> ConcurrentWorkflow
    SwarmRouter --> AgentRearrange
    SwarmRouter --> HierarchicalSwarm
    SwarmRouter --> GroupChat
    
    SequentialWorkflow --> Agent
    ConcurrentWorkflow --> Agent
    AgentRearrange --> Agent
    HierarchicalSwarm --> Agent
    GroupChat --> Agent
```

**Sources:** [swarms/structs/agent.py:163-301](), [swarms/structs/swarm_router.py:106-173](), [swarms/structs/__init__.py:1-172]()

## Agent Class Foundation

The `Agent` class serves as the core building block, integrating language models, tools, memory systems, and conversation management into a unified interface. The class provides extensive configuration options for production deployments.

```mermaid
graph LR
    subgraph "Agent Initialization"
        agent_init["__init__"]
        setup_config["setup_config"]
        reliability_check["reliability_check"]
    end
    
    subgraph "Core Dependencies"
        llm_handling["llm_handling"]
        tool_handling["tool_handling"]
        short_memory_init["short_memory_init"]
        rag_setup_handling["rag_setup_handling"]
    end
    
    subgraph "Runtime Components"
        run["run"]
        _run["_run"]
        streaming["streaming"]
        tool_struct["BaseTool"]
        conversation["Conversation"]
    end
    
    subgraph "Integration Points"
        mcp_config["MCPConnection"]
        rag_handler["AgentRAGHandler"]
        litellm["LiteLLM"]
        artifacts["Artifact"]
    end
    
    agent_init --> setup_config
    setup_config --> reliability_check
    setup_config --> llm_handling
    setup_config --> tool_handling
    setup_config --> short_memory_init
    setup_config --> rag_setup_handling
    
    run --> _run
    _run --> streaming
    _run --> tool_struct
    _run --> conversation
    
    tool_handling --> tool_struct
    short_memory_init --> conversation
    rag_setup_handling --> rag_handler
    llm_handling --> litellm
```

**Sources:** [swarms/structs/agent.py:303-624](), [swarms/structs/agent.py:625-690](), [swarms/structs/conversation.py]()

## SwarmRouter Factory System

The `SwarmRouter` implements a factory pattern that provides dynamic selection and instantiation of different swarm types based on task requirements or explicit configuration. This system enables seamless switching between orchestration strategies.

```mermaid
graph TB
    subgraph "SwarmRouter Core"
        SwarmRouter["SwarmRouter"]
        swarm_factory["_swarm_factory"]
        swarm_cache["_swarm_cache"]
        reliability_check["reliability_check"]
    end
    
    subgraph "Factory Methods"
        create_sequential["_create_sequential_workflow"]
        create_concurrent["_create_concurrent_workflow"]
        create_rearrange["_create_agent_rearrange"]
        create_hierarchical["_create_hierarchical_swarm"]
        create_groupchat["_create_group_chat"]
        create_heavy["_create_heavy_swarm"]
    end
    
    subgraph "Swarm Implementations"
        SequentialWorkflow["SequentialWorkflow"]
        ConcurrentWorkflow["ConcurrentWorkflow"]
        AgentRearrange["AgentRearrange"]
        HierarchicalSwarm["HierarchicalSwarm"]
        GroupChat["GroupChat"]
        HeavySwarm["HeavySwarm"]
    end
    
    SwarmRouter --> swarm_factory
    SwarmRouter --> swarm_cache
    SwarmRouter --> reliability_check
    
    swarm_factory --> create_sequential
    swarm_factory --> create_concurrent
    swarm_factory --> create_rearrange
    swarm_factory --> create_hierarchical
    swarm_factory --> create_groupchat
    swarm_factory --> create_heavy
    
    create_sequential --> SequentialWorkflow
    create_concurrent --> ConcurrentWorkflow
    create_rearrange --> AgentRearrange
    create_hierarchical --> HierarchicalSwarm
    create_groupchat --> GroupChat
    create_heavy --> HeavySwarm
```

**Sources:** [swarms/structs/swarm_router.py:175-249](), [swarms/structs/swarm_router.py:380-450](), [swarms/structs/swarm_router.py:37-54]()

## Core Integration Patterns

### Agent Configuration System

The Agent class utilizes several key integration patterns for production readiness:

| Integration Point | Implementation | Purpose |
|------------------|----------------|---------|
| `llm_handling()` | [swarms/structs/agent.py:2640-2672]() | LLM provider abstraction via LiteLLM |
| `tool_handling()` | [swarms/structs/agent.py:633-651]() | Function calling and tool integration |
| `short_memory_init()` | [swarms/structs/agent.py:652-693]() | Conversation history management |
| `rag_setup_handling()` | [swarms/structs/agent.py:625-631]() | Long-term memory and RAG integration |

### Orchestration Factory Pattern

The SwarmRouter employs a factory pattern with O(1) lookup performance for swarm type selection:

```mermaid
graph LR
    subgraph "Request Flow"
        task["Task Input"]
        router_run["SwarmRouter.run"]
        factory_lookup["_swarm_factory[swarm_type]"]
        swarm_instance["Swarm Instance"]
        execution["Task Execution"]
    end
    
    task --> router_run
    router_run --> factory_lookup
    factory_lookup --> swarm_instance
    swarm_instance --> execution
    
    subgraph "Factory Dictionary"
        factory_dict["_initialize_swarm_factory()"]
        sequential_factory["'SequentialWorkflow': _create_sequential_workflow"]
        concurrent_factory["'ConcurrentWorkflow': _create_concurrent_workflow"]
        rearrange_factory["'AgentRearrange': _create_agent_rearrange"]
    end
    
    factory_lookup --> factory_dict
    factory_dict --> sequential_factory
    factory_dict --> concurrent_factory
    factory_dict --> rearrange_factory
```

**Sources:** [swarms/structs/swarm_router.py:380-402](), [swarms/structs/swarm_router.py:658-715]()

### Memory and State Management

The core system provides multiple layers of memory and state persistence:

- **Short-term Memory**: `Conversation` class manages interaction history
- **Long-term Memory**: `AgentRAGHandler` integrates vector databases
- **State Persistence**: `SafeStateManager` handles agent state serialization
- **Distributed Memory**: Shared memory systems across agent swarms

**Sources:** [swarms/structs/conversation.py](), [swarms/structs/agent_rag_handler.py](), [swarms/structs/safe_loading.py]()

## Execution Models

The Core Agent System supports multiple execution paradigms:

### Single Agent Execution
Direct agent instantiation and task execution via `Agent.run()` method with support for:
- Synchronous and asynchronous execution
- Streaming output generation
- Tool integration and function calling
- Memory persistence and state management

### Multi-Agent Orchestration
Factory-based swarm creation through `SwarmRouter` supporting:
- Sequential task processing via `SequentialWorkflow`
- Parallel execution via `ConcurrentWorkflow`
- Dynamic agent arrangement via `AgentRearrange`
- Hierarchical coordination via `HierarchicalSwarm`
- Conversational coordination via `GroupChat`

**Sources:** [swarms/structs/agent.py:1549-1900](), [swarms/structs/swarm_router.py:658-800]()

## Configuration and Initialization

The system provides comprehensive configuration management through:

- **Environment Variables**: API keys and workspace configuration
- **YAML/JSON Configuration**: Agent and swarm parameter specification
- **Dynamic Configuration**: Runtime parameter adjustment
- **Validation Systems**: Configuration reliability checks and error handling

Key configuration classes include `SwarmRouterConfig`, `ConversationSchema`, and `RAGConfig` for structured parameter management.

**Sources:** [swarms/structs/swarm_router.py:62-92](), [swarms/schemas/conversation_schema.py](), [swarms/structs/agent_rag_handler.py]()

---

