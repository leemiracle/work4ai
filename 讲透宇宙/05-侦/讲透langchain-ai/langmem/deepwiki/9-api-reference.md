<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/langmem · page 9 API Reference · fetched 2026-10-26 -->

# API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/reference/index.md](docs/docs/reference/index.md)
- [src/langmem/__init__.py](src/langmem/__init__.py)
- [src/langmem/prompts/optimization.py](src/langmem/prompts/optimization.py)
- [src/langmem/prompts/types.py](src/langmem/prompts/types.py)

</details>



This page provides complete API documentation for all LangMem functions, classes, and utilities. It covers the Core API layer (stateless functions) and Stateful Integration layer (persistent memory management), along with supporting data types and utilities.

For detailed usage examples and integration patterns, see [Memory Management](#2), [Memory Tools](#5), and [Integration](#4). For background on the system architecture, see [Key Concepts](#1.2).

## Core API Structure

LangMem's API is organized around key functional areas, each providing specific capabilities for memory-enabled LLM applications:

#### LangMem API Organization

```mermaid
graph TB
    subgraph "Core API Exports"
        subgraph "Memory Management"
            CMM["create_memory_manager()"]
            CMSM["create_memory_store_manager()"]
            CTE["create_thread_extractor()"]
            CMS["create_memory_searcher()"]
        end
        
        subgraph "Memory Tools"
            CMMT["create_manage_memory_tool()"]
            CSMT["create_search_memory_tool()"]
        end
        
        subgraph "Prompt Optimization"  
            CPO["create_prompt_optimizer()"]
            CMPO["create_multi_prompt_optimizer()"]
        end
        
        subgraph "Background Processing"
            RE["ReflectionExecutor"]
        end
        
        subgraph "Data Types"
            P["Prompt"]
            AT["AnnotatedTrajectory"] 
            OI["OptimizerInput"]
            MPOI["MultiPromptOptimizerInput"]
        end
        
        subgraph "Utilities"
            NT["NamespaceTemplate"]
            FS["format_sessions()"]
        end
    end
    
    subgraph "LangGraph Integration"
        BS["BaseStore"]
        CRA["create_react_agent()"]
    end
    
    subgraph "LLM Providers"
        BCM["BaseChatModel"]
        MS["Model Strings"]
    end
    
    %% Memory Management connections
    CMM --> BCM
    CMSM --> BS
    CMSM --> CMM
    CTE --> CMM
    
    %% Tool connections  
    CMMT --> CMSM
    CSMT --> CMSM
    CMMT --> CRA
    CSMT --> CRA
    
    %% Optimization connections
    CPO --> BCM
    CPO --> MS
    CMPO --> CPO
    
    %% Data type usage
    P --> CPO
    P --> CMPO
    AT --> CPO
    AT --> CMPO
    OI --> CPO
    MPOI --> CMPO
    
    %% Utility usage
    NT --> CMSM
    FS --> CMPO
    
    %% Background processing
    RE --> CMSM
```

**Sources:** [src/langmem/__init__.py:1-28](), [docs/docs/reference/index.md:1-34]()

## Memory Management APIs

The memory management layer provides both stateless (`create_memory_manager`) and stateful (`create_memory_store_manager`) approaches to extracting, storing, and retrieving memories from conversations.

#### Memory Manager Architecture

```mermaid
graph LR
    subgraph "Stateless Layer"
        CMM["create_memory_manager()"]
        CTE["create_thread_extractor()"] 
        CMS["create_memory_searcher()"]
    end
    
    subgraph "Stateful Layer"
        CMSM["create_memory_store_manager()"]
        MSM["MemoryStoreManager"]
    end
    
    subgraph "Memory Types"
        SM["Semantic Memory"]
        EM["Episodic Memory"]  
        PM["Procedural Memory"]
        STM["Short-term Memory"]
    end
    
    subgraph "Storage Patterns"
        CP["Collection Pattern"]
        PP["Profile Pattern"] 
        RP["Rule Pattern"]
    end
    
    %% API relationships
    CMM --> SM
    CMM --> EM
    CMM --> PM
    CTE --> STM
    
    CMSM --> CMM
    CMSM --> MSM
    
    %% Storage pattern mapping
    SM --> CP
    SM --> PP
    EM --> CP
    PM --> RP
    STM --> PP
```

The `create_memory_manager` function creates stateless memory extractors that analyze conversations and return structured memory objects. The `create_memory_store_manager` function wraps this with persistent storage capabilities using LangGraph's `BaseStore`.

The `create_thread_extractor` specializes in conversation summarization and context management, while `create_memory_searcher` provides semantic search across stored memories.

**Sources:** [src/langmem/__init__.py:1-8](), [docs/docs/reference/index.md:10-16]()

## Memory Tools APIs

Memory tools enable agents to actively manage their own memory through structured tool calls during conversations. These tools provide the "hot path" memory formation capabilities.

#### Memory Tools Integration

```mermaid
graph TB
    subgraph "Agent Tools"
        CMMT["create_manage_memory_tool()"]
        CSMT["create_search_memory_tool()"]
    end
    
    subgraph "Tool Actions"
        subgraph "Management Actions"
            CREATE["create"]
            UPDATE["update"]
            DELETE["delete"]
        end
        
        subgraph "Search Actions"
            SEARCH["search"]
            RETRIEVE["retrieve"]
        end
    end
    
    subgraph "Agent Frameworks"
        CRA["create_react_agent()"]
        CA["Custom Agents"]
        CREW["CrewAI"]
    end
    
    subgraph "Storage Layer"
        BS["BaseStore"]
        IMS["InMemoryStore"]
        PGS["AsyncPostgresStore"]
    end
    
    %% Tool to action mapping
    CMMT --> CREATE
    CMMT --> UPDATE  
    CMMT --> DELETE
    CSMT --> SEARCH
    CSMT --> RETRIEVE
    
    %% Agent integration
    CMMT --> CRA
    CSMT --> CRA
    CMMT --> CA
    CSMT --> CA
    CMMT --> CREW
    CSMT --> CREW
    
    %% Storage integration
    CMMT --> BS
    CSMT --> BS
    BS --> IMS
    BS --> PGS
```

The `create_manage_memory_tool` creates a tool that agents can use to store, update, and delete memories with configurable `actions_permitted` parameters. The `create_search_memory_tool` creates a tool for semantic search and retrieval of relevant memories based on queries.

**Sources:** [src/langmem/__init__.py:2-3,19-20](), [docs/docs/reference/index.md:17-23]()

## Prompt Optimization APIs

The prompt optimization system provides iterative improvement of prompts based on conversation feedback and performance analysis.

#### Prompt Optimization Strategies

```mermaid
graph TB
    subgraph "Single Prompt Optimization"
        CPO["create_prompt_optimizer()"]
        
        subgraph "Optimization Strategies"
            GRAD["gradient"]
            META["metaprompt"]
            PMEM["prompt_memory"]
        end
    end
    
    subgraph "Multi-Prompt Optimization"
        CMPO["create_multi_prompt_optimizer()"]
        MPO["MultiPromptOptimizer"]
        
        subgraph "Credit Assignment"
            CLASS["Classify"]
            REASON["reasoning"]
            WHICH["which"]
        end
    end
    
    subgraph "Input Types"
        OI["OptimizerInput"]
        MPOI["MultiPromptOptimizerInput"]
        AT["AnnotatedTrajectory"]
        P["Prompt"]
    end
    
    subgraph "Optimization Configs"
        GOC["GradientOptimizerConfig"]
        MOC["MetapromptOptimizerConfig"]
    end
    
    %% Strategy connections
    CPO --> GRAD
    CPO --> META
    CPO --> PMEM
    
    %% Multi-prompt connections
    CMPO --> MPO
    MPO --> CPO
    MPO --> CLASS
    CLASS --> REASON
    CLASS --> WHICH
    
    %% Input type usage
    CPO --> OI
    CMPO --> MPOI
    OI --> AT
    OI --> P
    MPOI --> AT
    MPOI --> P
    
    %% Config usage
    CPO --> GOC
    CPO --> MOC
```

The `create_prompt_optimizer` function supports three optimization strategies with different trade-offs between speed and thoroughness. The `create_multi_prompt_optimizer` function extends this to handle multiple prompts simultaneously with credit assignment to determine which prompts need updates.

**Sources:** [src/langmem/prompts/optimization.py:50-269](), [src/langmem/prompts/optimization.py:471-616](), [src/langmem/__init__.py:9-13,22-23]()

## Background Processing APIs

The `ReflectionExecutor` enables deferred memory processing and analysis separate from real-time conversation flow.

#### Reflection Processing Architecture

```mermaid
graph LR
    subgraph "Conversation Layer"
        CONV["Conversation"]
        USER["User Interaction"]
    end
    
    subgraph "Background Processing"
        RE["ReflectionExecutor"]
        
        subgraph "Processing Tasks"
            EXTRACT["Memory Extraction"]
            CONSOLIDATE["Memory Consolidation"]
            UPDATE["Memory Updates"]
            ANALYZE["Conversation Analysis"]
        end
    end
    
    subgraph "Storage Integration"
        CMSM["create_memory_store_manager()"]
        BS["BaseStore"]
    end
    
    subgraph "LangGraph Services"
        LGS["LangGraph Services"]
        SCHED["Task Scheduling"]
    end
    
    %% Flow connections
    CONV --> RE
    USER --> RE
    
    RE --> EXTRACT
    RE --> CONSOLIDATE  
    RE --> UPDATE
    RE --> ANALYZE
    
    %% Storage integration
    RE --> CMSM
    CMSM --> BS
    
    %% Service integration
    RE --> LGS
    LGS --> SCHED
```

The `ReflectionExecutor` processes conversations asynchronously to extract insights, consolidate related memories, and perform deeper analysis without blocking real-time interactions.

**Sources:** [src/langmem/__init__.py:14,25](), [docs/docs/reference/index.md:31-34]()

## Data Types and Schemas

LangMem defines several key data types for structured memory management and prompt optimization.

#### Core Data Type Relationships

```mermaid
graph TB
    subgraph "Prompt Types"
        P["Prompt"]
        PN["name: str"]
        PP["prompt: str"]  
        UI["update_instructions: str | None"]
        WTU["when_to_update: str | None"]
    end
    
    subgraph "Trajectory Types"
        AT["AnnotatedTrajectory"]
        MSG["messages: Sequence[AnyMessage]"]
        FB["feedback: dict | str | None"]
    end
    
    subgraph "Input Types"
        OI["OptimizerInput"]
        MPOI["MultiPromptOptimizerInput"]
        TRAJ["trajectories"]
        PROMPT["prompt"]
        PROMPTS["prompts"]
    end
    
    subgraph "Memory Types"
        EM["ExtractedMemory"]
        RS["RunningSummary"]
        TRIP["Triple"]
        EP["Episode"]
    end
    
    %% Prompt structure
    P --> PN
    P --> PP
    P --> UI
    P --> WTU
    
    %% Trajectory structure
    AT --> MSG
    AT --> FB
    
    %% Input type composition
    OI --> TRAJ
    OI --> PROMPT
    MPOI --> TRAJ
    MPOI --> PROMPTS
    
    %% Usage relationships
    TRAJ --> AT
    PROMPT --> P
    PROMPTS --> P
```

The `Prompt` type provides structured prompt management with optimization metadata. The `AnnotatedTrajectory` type pairs conversation history with feedback for optimization. Input types like `OptimizerInput` and `MultiPromptOptimizerInput` structure the data flow for optimization functions.

**Sources:** [src/langmem/prompts/types.py:7-136](), [src/langmem/__init__.py:26]()

## Function Signature Reference

| Function | Parameters | Returns | Purpose |
|----------|------------|---------|---------|
| `create_memory_manager` | `model`, `memory_types`, `config` | Memory extractor | Stateless memory extraction |
| `create_memory_store_manager` | `model`, `store`, `namespace_template` | `MemoryStoreManager` | Persistent memory management |
| `create_manage_memory_tool` | `memory_store_manager`, `actions_permitted` | Agent tool | Memory management tool |
| `create_search_memory_tool` | `memory_store_manager`, `query_config` | Agent tool | Memory search tool |
| `create_prompt_optimizer` | `model`, `kind`, `config` | Prompt optimizer | Single prompt optimization |
| `create_multi_prompt_optimizer` | `model`, `kind`, `config` | Multi-prompt optimizer | Multiple prompt optimization |
| `create_thread_extractor` | `model`, `config` | Thread extractor | Conversation summarization |
| `create_memory_searcher` | `store`, `config` | Memory searcher | Semantic memory search |

**Sources:** [src/langmem/__init__.py:16-27](), [docs/docs/reference/index.md:8-34]()

---

