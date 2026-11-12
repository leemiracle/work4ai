<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/langmem · page 2 Memory Management · fetched 2026-10-26 -->

# Memory Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/concepts/conceptual_guide.md](docs/docs/concepts/conceptual_guide.md)
- [src/langmem/knowledge/extraction.py](src/langmem/knowledge/extraction.py)

</details>



This document covers LangMem's core memory management capabilities, focusing on the two primary factory functions `create_memory_manager` and `create_memory_store_manager` and their respective implementations. These functions provide the foundation for extracting, processing, and managing conversation memories in LLM applications.

For information about specific memory types (semantic, episodic, procedural), see [Semantic Memory](#2.1), [Episodic Memory](#2.2), and [User Profiles](#2.4). For short-term memory and conversation summarization, see [Short-Term Memory and Summarization](#2.3). For hot path versus background processing approaches, see [Processing Approaches](#3).

## Core Memory Management Functions

LangMem provides two main factory functions that handle memory management at different levels of integration:

| Function | Purpose | Storage Integration | Use Case |
|----------|---------|-------------------|-----------|
| `create_memory_manager` | Stateless memory processing | None - returns extracted memories | Standalone memory extraction, custom storage |
| `create_memory_store_manager` | Stateful memory processing | LangGraph BaseStore | Automatic persistence, full memory lifecycle |

Both functions return `Runnable` instances that can be invoked with conversation messages to process memories, but they differ significantly in their integration patterns and capabilities.

**Sources:** [src/langmem/knowledge/extraction.py:536-692](), [src/langmem/knowledge/extraction.py:1666-2105]()

## Memory Manager Architecture

The `MemoryManager` class provides the core stateless memory processing functionality. It analyzes conversation messages against existing memories to extract, update, consolidate, or remove memory entries.

```mermaid
graph TB
    subgraph "MemoryManager Core"
        MM["MemoryManager"]
        TE["trustcall extractor"]
        INST["_MEMORY_INSTRUCTIONS"]
    end
    
    subgraph "Input Processing"
        MS["MemoryState"]
        PM["_prepare_messages()"]
        PE["_prepare_existing()"]
    end
    
    subgraph "Processing Loop"
        ML["max_steps loop"]
        TC["tool calling"]
        DONE["Done tool"]
    end
    
    subgraph "Output"
        EM["ExtractedMemory[]"]
        FR["_filter_response()"]
    end
    
    MS --> PM
    MS --> PE
    PM --> MM
    PE --> MM
    MM --> TE
    TE --> ML
    ML --> TC
    TC --> DONE
    ML --> FR
    FR --> EM
    
    INST --> MM
```

The `MemoryManager` supports configurable memory operations through boolean flags:

- `enable_inserts`: Allow creation of new memories
- `enable_updates`: Allow modification of existing memories  
- `enable_deletes`: Allow removal of outdated memories

**Sources:** [src/langmem/knowledge/extraction.py:217-533](), [src/langmem/knowledge/extraction.py:185-207]()

## Memory Store Manager Architecture  

The `MemoryStoreManager` extends memory management with full storage integration, automatic memory search, and lifecycle management. It combines memory processing with LangGraph's `BaseStore` for persistence.

```mermaid
graph TB
    subgraph "MemoryStoreManager"
        MSM["MemoryStoreManager"]
        MM2["MemoryManager"]
        ST["search_tool"]
        QG["query_gen"]
    end
    
    subgraph "Storage Layer"
        BS["BaseStore"]
        NS["namespace()"]
        SM["store_map"]
    end
    
    subgraph "Processing Pipeline"
        QS["query search"]
        ER["enrich memories"]
        PH["phases processing"]
        AU["apply updates"]
    end
    
    subgraph "Memory Lifecycle"
        SR["search & retrieve"]
        EX["extract & update"]  
        CO["consolidate"]
        PS["persist to store"]
    end
    
    MSM --> MM2
    MSM --> ST
    MSM --> QG
    MSM --> BS
    BS --> NS
    BS --> SM
    
    MSM --> QS
    QS --> ER
    ER --> PH
    PH --> AU
    
    SR --> EX
    EX --> CO
    CO --> PS
    
    style MSM fill:#f9f9f9
    style MM2 fill:#e8f5e8
    style BS fill:#fff3e0
```

The `MemoryStoreManager` includes several advanced features:
- **Query Generation**: Uses a separate LLM to generate optimized search queries
- **Default Factory**: Provides fallback memories when no existing memories are found
- **Multi-Phase Processing**: Supports multiple rounds of memory enrichment
- **Namespace Templating**: Dynamic namespace configuration with runtime variables

**Sources:** [src/langmem/knowledge/extraction.py:832-1665](), [src/langmem/knowledge/extraction.py:877-914]()

## Memory Processing Data Flow

The following diagram shows how conversation messages flow through the memory processing pipeline from input to persistent storage:

```mermaid
sequenceDiagram
    participant C as "Client"
    participant MSM as "MemoryStoreManager"  
    participant QM as "query_model"
    participant BS as "BaseStore"
    participant MM as "MemoryManager"
    participant LLM as "Language Model"
    
    C->>MSM: "MemoryStoreManagerInput"
    MSM->>MSM: "namespace(config)"
    
    alt query_model configured
        MSM->>QM: "generate search queries"
        QM-->>MSM: "tool_calls[]"
        MSM->>BS: "asearch(namespace, queries)"
    else no query_model
        MSM->>MSM: "get_dilated_windows()"
        MSM->>BS: "asearch(namespace, windows)"
    end
    
    BS-->>MSM: "search_results[]"
    MSM->>MSM: "_sort_results()"
    
    MSM->>MM: "ainvoke(messages, existing)"
    MM->>LLM: "extract & consolidate"
    LLM-->>MM: "tool_calls[]"
    MM-->>MSM: "ExtractedMemory[]"
    
    loop for each phase
        MSM->>MM: "_build_phase_manager()"
        MM->>LLM: "phase processing"
        LLM-->>MM: "phase results"
        MM-->>MSM: "phase memories"
    end
    
    MSM->>MSM: "_apply_manager_output()"
    MSM->>BS: "aput() / adelete()"
    BS-->>MSM: "persistence confirmation"
    MSM-->>C: "final_puts[]"
```

**Sources:** [src/langmem/knowledge/extraction.py:1006-1137](), [src/langmem/knowledge/extraction.py:977-989]()

## Memory State and Schemas

Both memory managers work with structured memory representations using Pydantic models. The base `Memory` class provides a simple content-based memory, while custom schemas enable structured memory types.

| Class | Purpose | Key Fields | Usage |
|-------|---------|------------|--------|
| `Memory` | Default unstructured memory | `content: str` | Basic memory storage |
| `ExtractedMemory` | Processed memory result | `id: str`, `content: BaseModel` | Memory manager output |
| `MemoryState` | Input state container | `messages: list`, `existing: list`, `max_steps: int` | Processing input |
| `MemoryStoreManagerInput` | Store manager input | `messages: list`, `max_steps: int` | Store processing input |

The memory processing supports multi-step extraction with a configurable `max_steps` parameter. When `max_steps > 1`, the system adds a `Done` tool to allow the LLM to signal completion of memory formation.

**Sources:** [src/langmem/knowledge/extraction.py:64-94](), [src/langmem/knowledge/extraction.py:78-81](), [src/langmem/knowledge/extraction.py:209-215]()

## Memory Operations and Filtering

The memory processing pipeline handles three core operations on existing memories:

```mermaid
graph LR
    subgraph "Memory Operations"
        INS["Insert New"]
        UPD["Update Existing"] 
        DEL["Delete Outdated"]
    end
    
    subgraph "Processing Flags"
        EI["enable_inserts"]
        EU["enable_updates"]
        ED["enable_deletes"]
    end
    
    subgraph "Filtering Logic"
        FR["_filter_response()"]
        ER["exclude_removals"]
        EXT["external_ids"]
    end
    
    EI --> INS
    EU --> UPD
    ED --> DEL
    
    INS --> FR
    UPD --> FR
    DEL --> FR
    
    FR --> ER
    FR --> EXT
    
    style FR fill:#f9f9f9
```

The `_filter_response()` method handles complex memory ID tracking to distinguish between externally-provided memories (that can be deleted) and internally-generated memories (that should not appear as deletions in the final output).

**Sources:** [src/langmem/knowledge/extraction.py:509-533](), [src/langmem/knowledge/extraction.py:940-975]()

## Integration with LangGraph Store

The `MemoryStoreManager` provides a complete storage interface through delegation to LangGraph's `BaseStore`. Key storage methods include:

| Method | Purpose | Async Version | Key Features |
|--------|---------|---------------|--------------|
| `get()` | Retrieve single item | `aget()` | TTL refresh, default factory |
| `search()` | Find multiple items | `asearch()` | Query + filter, pagination |
| `put()` | Store/update item | `aput()` | Indexing control, TTL |
| `delete()` | Remove item | `adelete()` | Namespace-aware deletion |

All storage operations use the configured namespace template, supporting dynamic runtime configuration through `RunnableConfig`.

**Sources:** [src/langmem/knowledge/extraction.py:1318-1658](), [src/langmem/knowledge/extraction.py:877-914]()

---

