<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/langmem · page 7 Storage · fetched 2026-10-26 -->

# Storage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/guides/extract_semantic_memories.md](docs/docs/guides/extract_semantic_memories.md)
- [src/langmem/knowledge/extraction.py](src/langmem/knowledge/extraction.py)

</details>



LangMem's storage system provides persistent, searchable memory management built on LangGraph's BaseStore abstraction. This system supports both development and production deployments with various storage backends, namespace organization patterns, and embedding-based search capabilities.

For detailed comparisons of specific storage implementations, see [Storage Types](#7.1). For namespace design patterns and templating, see [Namespace Organization](#7.2).

## Storage Architecture

LangMem integrates with LangGraph's storage layer through the BaseStore interface, providing a unified API for memory persistence across different storage backends:

### LangMem Storage Integration

```mermaid
graph TB
    subgraph "LangMem Components"
        MSM["MemoryStoreManager"]
        MM["MemoryManager"] 
        MT["Memory Tools"]
        MSE["create_memory_searcher"]
    end
    
    subgraph "LangGraph Storage Layer"
        BS["BaseStore Interface"]
        subgraph "Storage Implementations"
            IMS["InMemoryStore"]
            PGS["AsyncPostgresStore"]
            CS["Custom Stores"]
        end
    end
    
    subgraph "Storage Operations"
        PUT["put()"]
        GET["get()"]
        SEARCH["search()"]
        DELETE["delete()"]
    end
    
    subgraph "Data Organization"
        NS["Namespace Patterns"]
        IDX["Vector Indexing"]
        TTL["TTL Management"]
    end
    
    MSM --> BS
    MT --> BS
    MSE --> BS
    BS --> IMS
    BS --> PGS
    BS --> CS
    BS --> PUT
    BS --> GET
    BS --> SEARCH
    BS --> DELETE
    BS --> NS
    BS --> IDX
    BS --> TTL
```

Sources: [src/langmem/knowledge/extraction.py:12-23](), [src/langmem/knowledge/extraction.py:898-913]()

### Storage Flow Architecture

```mermaid
sequenceDiagram
    participant App as "Application"
    participant MSM as "MemoryStoreManager"
    participant BS as "BaseStore"
    participant EMB as "Embedding Service"
    participant DB as "Storage Backend"
    
    Note over App,DB: Memory Search & Retrieval
    App->>MSM: "search(query='user preferences')"
    MSM->>BS: "asearch(namespace, query)"
    BS->>EMB: "embed(query)"
    EMB-->>BS: "query_vector"
    BS->>DB: "vector_search()"
    DB-->>BS: "search_results"
    BS-->>MSM: "SearchItem[]"
    MSM-->>App: "coerced_results"
    
    Note over App,DB: Memory Storage
    App->>MSM: "ainvoke(messages)"
    MSM->>BS: "asearch() # find existing"
    BS-->>MSM: "existing_memories"
    MSM->>MSM: "memory_manager.ainvoke()"
    MSM->>BS: "aput(namespace, key, value)"
    BS->>EMB: "embed(content)"
    EMB-->>BS: "content_vector"
    BS->>DB: "insert/update"
    DB-->>BS: "success"
    BS-->>MSM: "success"
    MSM-->>App: "final_puts"
```

Sources: [src/langmem/knowledge/extraction.py:1006-1137](), [src/langmem/knowledge/extraction.py:1513-1578]()

## Storage Patterns

LangMem uses three main storage patterns for organizing different types of memories:

| Pattern | Use Case | Namespace Example | enable_inserts | Description |
|---------|----------|-------------------|----------------|-------------|
| **Collection** | Semantic memories, episodic memories | `("memories", "{user_id}")` | `True` | Multiple documents, searchable and updateable |
| **Profile** | User profiles, system preferences | `("profile", "{user_id}")` | `False` | Single document, in-place updates only |
| **Rules** | System instructions, behavioral guidelines | `("rules", "system")` | `False` | Static configuration, minimal updates |

Sources: [src/langmem/knowledge/extraction.py:844-846](), [src/langmem/knowledge/extraction.py:224-235]()

### Collection Pattern Example

```python
# Semantic memories - multiple facts per user
manager = create_memory_store_manager(
    "anthropic:claude-3-5-sonnet-latest",
    namespace=("memories", "{langgraph_user_id}"),
    enable_inserts=True,  # Allow new memories
    enable_deletes=True   # Allow removing outdated memories
)
```

### Profile Pattern Example

```python
# User profile - single document per user
manager = create_memory_store_manager(
    "anthropic:claude-3-5-sonnet-latest", 
    namespace=("profile", "{langgraph_user_id}"),
    enable_inserts=False,  # Only update existing profile
    enable_deletes=False   # Never delete profile
)
```

Sources: [src/langmem/knowledge/extraction.py:1666-1680](), [docs/docs/guides/extract_semantic_memories.md:138-145]()

## Namespace Organization

Namespaces provide hierarchical organization of memories using tuple-based paths:

### Namespace Template System

```mermaid
graph LR
    subgraph "Namespace Templates"
        UT["('memories', '{user_id}')"]
        TT["('team', '{team_id}', '{user_id}')"] 
        GT["('global', 'system')"]
        DT["('domain', '{project}', '{user_id}')"]
    end
    
    subgraph "Runtime Resolution"
        subgraph "User Context"
            U1["('memories', 'user-123')"]
            U2["('memories', 'user-456')"]
        end
        subgraph "Team Context" 
            T1["('team', 'eng', 'user-123')"]
            T2["('team', 'eng', 'user-456')"]
        end
        subgraph "Global Context"
            G1["('global', 'system')"]
        end
    end
    
    UT --> U1
    UT --> U2
    TT --> T1
    TT --> T2
    GT --> G1
```

### NamespaceTemplate Resolution

```python
# Template definition with placeholders
namespace_template = NamespaceTemplate(("memories", "{langgraph_user_id}"))

# Runtime resolution from config
config = {"configurable": {"langgraph_user_id": "user-123"}}
resolved = namespace_template(config)
# Result: ("memories", "user-123")
```

Sources: [src/langmem/knowledge/extraction.py:877](), [src/langmem/knowledge/extraction.py:1013](), [src/langmem/knowledge/extraction.py:1660-1663]()

## Storage Configuration

### Development Setup

```python
from langgraph.store.memory import InMemoryStore

# Development store with embedding support
store = InMemoryStore(
    index={
        "dims": 1536,  # OpenAI text-embedding-3-small
        "embed": "openai:text-embedding-3-small",
    }
)
```

### Production Setup

```python
from langgraph.store.postgres import AsyncPostgresStore

# Production store with persistent storage
store = AsyncPostgresStore(
    connection_string="postgresql://user:pass@host:5432/db",
    index={
        "dims": 1536,
        "embed": "openai:text-embedding-3-small", 
    }
)
```

Sources: [docs/docs/guides/extract_semantic_memories.md:132-137]()

## Memory Store Manager Integration

The `MemoryStoreManager` provides the primary interface for storage operations, automatically handling search, enrichment, and persistence:

### Store Access Pattern

```mermaid
graph LR
    subgraph "Store Resolution"
        MSM["MemoryStoreManager"]
        PROP["_store property"]
        CTX["LangGraph Context"]
        DIRECT["Direct Store Instance"]
    end
    
    MSM --> PROP
    PROP --> |"if self._store"| DIRECT
    PROP --> |"else get_store()"| CTX
    CTX --> |"RuntimeError if not configured"| ERR["ValueError"]
```

```python
@property
def store(self) -> BaseStore:
    """Get the store to use for memory storage.
    
    Returns the store provided during initialization if available,
    otherwise falls back to the store configured in the LangGraph context.
    """
    if self._store is not None:
        return self._store
    try:
        self._store = get_store()
    except RuntimeError as e:
        raise ValueError(
            "Memory Manager's store not configured in LangGraph context. "
            "First use in the graph before calling, or initialize with an instance of the store."
        ) from e
    return self._store
```

Sources: [src/langmem/knowledge/extraction.py:897-913]()

## Key Storage Operations

### Memory Enrichment Flow

1. **Search Phase**: Query existing memories by embedding similarity or direct lookup
2. **Enrichment Phase**: Process new information with LLM using existing context
3. **Persistence Phase**: Apply updates, insertions, and deletions to store
4. **Coercion Phase**: Convert stored values to appropriate Pydantic models

### Search and Retrieval

```python
# Vector search with query generation
search_results_lists = await asyncio.gather(
    *[
        store.asearch(
            namespace, **({**tc["args"], "limit": self.query_limit})
        )
        for tc in query_req.tool_calls
    ]
)
```

### Batch Operations

```python
# Parallel puts and deletes
await asyncio.gather(
    *(store.aput(**put) for put in final_puts),
    *(store.adelete(ns, key) for (ns, key) in final_deletes),
)
```

Sources: [src/langmem/knowledge/extraction.py:1022-1029](), [src/langmem/knowledge/extraction.py:1132-1135]()

The storage system provides a flexible foundation for memory management, supporting both simple development workflows and complex production deployments with proper isolation, search capabilities, and data persistence.

---

