<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-knowledge-retrieval · page 4 Backend Components · fetched 2026-10-26 -->

# Backend Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/backend/app/assistant_agent.py](app/backend/app/assistant_agent.py)
- [app/backend/app/documents.py](app/backend/app/documents.py)
- [app/backend/app/main.py](app/backend/app/main.py)
- [app/backend/app/memory_store.py](app/backend/app/memory_store.py)

</details>



## Purpose and Scope

This document provides a detailed technical reference for the Python backend components that power the Knowledge Retrieval system. The backend is built on FastAPI and implements a ChatKit-compatible conversational AI server with document retrieval, citation extraction, and thread management capabilities.

The backend components covered here include:
- The FastAPI application and HTTP endpoints ([app/backend/app/main.py:1-647]())
- The assistant agent system with tool building ([app/backend/app/assistant_agent.py:1-128]())
- Document metadata management ([app/backend/app/documents.py:1-43]())
- In-memory thread storage ([app/backend/app/memory_store.py:1-177]())

For frontend components and UI integration, see [Frontend Components](#5). For CLI tools and data ingestion workflows, see [CLI Tools](#6). For RAG pipeline details, see [RAG Pipeline](#3.4).

---

## Core Component Architecture

The backend is organized around four primary components that work together to handle conversational retrieval requests:

```mermaid
graph TB
    subgraph "HTTP Layer"
        FastAPI["FastAPI Application<br/>app/backend/app/main.py"]
        EP1["/knowledge/chatkit"]
        EP2["/knowledge/documents"]
        EP3["/knowledge/documents/:id/file"]
        EP4["/knowledge/threads/:id/citations"]
        EP5["/knowledge/health"]
    end
    
    subgraph "Core Service Classes"
        Server["KnowledgeAssistantServer<br/>main.py:131-545"]
        MemStore["MemoryStore<br/>memory_store.py:22-177"]
        AgentMod["assistant_agent module<br/>assistant_agent.py"]
        DocMod["documents module<br/>documents.py"]
    end
    
    subgraph "Agent System"
        AgentInstance["assistant_agent<br/>Agent instance<br/>assistant_agent.py:121-127"]
        BuildTools["_build_tools()<br/>assistant_agent.py:67-115"]
        FileSearchTool["FileSearchTool<br/>OpenAI backend"]
        RetrieveTool["_retrieve_tool<br/>Custom backend"]
    end
    
    subgraph "Document System"
        DocMeta["DocumentMetadata<br/>documents.py:16-26"]
        ScanDocs["_scan_documents<br/>main.py:153-222"]
        LookupDoc["_lookup_document<br/>main.py:224-242"]
        ResolvePath["_resolve_document_path<br/>main.py:244-245"]
    end
    
    subgraph "Thread Management"
        ThreadState["_ThreadState<br/>memory_store.py:16-19"]
        LoadThread["load_thread<br/>load_thread_items"]
        SaveThread["save_thread<br/>add_thread_item"]
    end
    
    FastAPI --> EP1
    FastAPI --> EP2
    FastAPI --> EP3
    FastAPI --> EP4
    FastAPI --> EP5
    
    EP1 --> Server
    EP2 --> Server
    EP3 --> Server
    EP4 --> Server
    
    Server --> MemStore
    Server --> AgentMod
    Server --> DocMod
    Server --> ScanDocs
    Server --> LookupDoc
    Server --> ResolvePath
    
    AgentMod --> AgentInstance
    AgentInstance --> BuildTools
    BuildTools --> FileSearchTool
    BuildTools --> RetrieveTool
    
    Server --> AgentInstance
    
    DocMod --> DocMeta
    ScanDocs --> DocMeta
    
    MemStore --> ThreadState
    MemStore --> LoadThread
    MemStore --> SaveThread
```

**Sources:** [app/backend/app/main.py:1-647](), [app/backend/app/assistant_agent.py:1-128](), [app/backend/app/memory_store.py:1-177](), [app/backend/app/documents.py:1-43]()

---

## Key Classes and Modules

| Component | File | Primary Class/Function | Responsibility |
|-----------|------|----------------------|----------------|
| FastAPI Server | `main.py` | `KnowledgeAssistantServer` | Orchestrates all backend operations, handles HTTP endpoints |
| Agent System | `assistant_agent.py` | `assistant_agent`, `_build_tools()` | Manages AI agent, tools, and retrieval caching |
| Document Metadata | `documents.py` | `DocumentMetadata` | Represents document metadata structure |
| Thread Storage | `memory_store.py` | `MemoryStore` | In-memory persistence for threads and messages |

**Sources:** [app/backend/app/main.py:131-545](), [app/backend/app/assistant_agent.py:121-127](), [app/backend/app/documents.py:16-26](), [app/backend/app/memory_store.py:22-177]()

---

## HTTP API Endpoints

The FastAPI application exposes five endpoints for client interaction:

```mermaid
graph LR
    subgraph "Client Requests"
        Client["Web Browser<br/>Frontend App"]
    end
    
    subgraph "FastAPI Routes"
        R1["POST /knowledge/chatkit<br/>main.py:580-590"]
        R2["GET /knowledge/documents<br/>main.py:593-600"]
        R3["GET /knowledge/documents/:id/file<br/>main.py:603-623"]
        R4["GET /knowledge/threads/:id/citations<br/>main.py:626-641"]
        R5["GET /knowledge/health<br/>main.py:644-646"]
    end
    
    subgraph "Handler Methods"
        Process["server.process()<br/>ChatKit protocol"]
        ScanDocs["_scan_documents()<br/>_load_cfg()"]
        LookupDoc["_lookup_document()<br/>_resolve_document_path()"]
        LatestCite["latest_citations()<br/>_extract_citations()"]
        Health["Health status dict"]
    end
    
    Client --> R1
    Client --> R2
    Client --> R3
    Client --> R4
    Client --> R5
    
    R1 --> Process
    R2 --> ScanDocs
    R3 --> LookupDoc
    R4 --> LatestCite
    R5 --> Health
```

**Sources:** [app/backend/app/main.py:580-646]()

### Endpoint Reference Table

| Method | Path | Handler | Response Type | Purpose |
|--------|------|---------|---------------|---------|
| `POST` | `/knowledge/chatkit` | `chatkit_endpoint` | SSE stream or JSON | ChatKit protocol processing, agent responses |
| `GET` | `/knowledge/documents` | `list_documents` | JSON | List all available documents |
| `GET` | `/knowledge/documents/{document_id}/file` | `document_file` | File | Download/preview document file |
| `GET` | `/knowledge/threads/{thread_id}/citations` | `thread_citations` | JSON | Retrieve citations for a thread |
| `GET` | `/knowledge/health` | `health_check` | JSON | Service health status |

**Sources:** [app/backend/app/main.py:580-646]()

---

## KnowledgeAssistantServer Class

The `KnowledgeAssistantServer` class ([main.py:131-545]()) extends `ChatKitServer` and serves as the main orchestrator for all backend functionality.

### Class Structure

```mermaid
classDiagram
    class KnowledgeAssistantServer {
        +MemoryStore store
        +Agent assistant
        +Dict~str,RootConfig~ _cfg_cache
        +str _cfg_path
        +Dict~str,list~ _documents_cache
        +Dict~str,Dict~ _document_path_cache
        +str vector_store_backend
        
        +__init__(agent)
        +respond(thread, item, context) AsyncIterator
        +latest_citations(thread_id, context) list
        
        -_load_cfg(path) RootConfig
        -_scan_documents(cfg_path, cfg) list
        -_lookup_document(cfg_path, cfg, identifier) DocumentMetadata
        -_resolve_document_path(cfg_path, doc_id) Path
        -_extract_citations(item, cfg, thread_id) list
        -_citations_from_annotations(item, cfg) list
        -_apply_cached_citations_to_item(thread_id, item, cfg) list
        -_build_citations_from_chunks(thread_id, item, cfg) tuple
        -_build_history_prompt(thread_id, base_text, context) str
    }
    
    class ChatKitServer {
        <<interface>>
        +process(payload, context)
    }
    
    class MemoryStore {
        +load_thread(thread_id, context)
        +save_thread(thread, context)
        +load_thread_items(thread_id, after, limit, order, context)
        +add_thread_item(thread_id, item, context)
    }
    
    class Agent {
        +model str
        +name str
        +instructions str
        +tools list
    }
    
    KnowledgeAssistantServer --|> ChatKitServer
    KnowledgeAssistantServer --> MemoryStore
    KnowledgeAssistantServer --> Agent
```

**Sources:** [app/backend/app/main.py:131-545]()

### Instance Initialization

The server initializes with several caches and loads the RAG configuration:

- `store`: `MemoryStore` instance for thread persistence ([main.py:133]())
- `_cfg_cache`: Caches loaded `RootConfig` objects by path ([main.py:136]())
- `_cfg_path`: Resolved from `RAG_CONFIG` environment variable or defaults to `configs/default.openai.yaml` ([main.py:137]())
- `_documents_cache`: Caches scanned `DocumentMetadata` lists by config path ([main.py:138]())
- `_document_path_cache`: Maps document IDs to filesystem paths ([main.py:139]())
- `vector_store_backend`: Extracted from config to determine tool behavior ([main.py:142]())

**Sources:** [app/backend/app/main.py:132-143]()

---

## Assistant Agent System

The agent system ([assistant_agent.py:1-128]()) creates an OpenAI Agent instance with dynamically configured tools based on the vector store backend.

### Agent Initialization

```mermaid
graph TB
    subgraph "Module-Level Initialization"
        LoadInst["Load system instructions<br/>assistant_agent.py:25-30"]
        BuildTools["_build_tools()<br/>assistant_agent.py:67-115"]
        CreateAgent["Create assistant_agent<br/>assistant_agent.py:121-127"]
    end
    
    subgraph "Tool Building Logic"
        ResolveCfg["_resolve_cfg_path()<br/>assistant_agent.py:33-38"]
        LoadCfg["load_config(cfg_path)<br/>assistant_agent.py:69"]
        CheckBackend["Check vector_store.backend<br/>assistant_agent.py:70"]
    end
    
    subgraph "Backend: openai_file_search"
        GetVSID["Get VECTOR_STORE_ID<br/>from env or config<br/>assistant_agent.py:72-76"]
        CreateFST["FileSearchTool<br/>with vector_store_ids<br/>assistant_agent.py:78-83"]
    end
    
    subgraph "Backend: custom"
        MakeStore["make_store_from_config(cfg)<br/>assistant_agent.py:85"]
        DefineFunc["Define _retrieve_tool<br/>function_tool decorator<br/>assistant_agent.py:87-111"]
        ReturnTool["Return _retrieve_tool<br/>assistant_agent.py:113"]
    end
    
    LoadInst --> CreateAgent
    BuildTools --> CreateAgent
    
    BuildTools --> ResolveCfg
    ResolveCfg --> LoadCfg
    LoadCfg --> CheckBackend
    
    CheckBackend -->|"openai_file_search"| GetVSID
    CheckBackend -->|"custom"| MakeStore
    
    GetVSID --> CreateFST
    MakeStore --> DefineFunc
    DefineFunc --> ReturnTool
```

**Sources:** [app/backend/app/assistant_agent.py:25-127]()

### Retrieval Caching Mechanism

The agent system maintains a thread-local cache of retrieved chunks to enable citation derivation after the assistant responds:

- `_RETRIEVAL_CACHE`: Dictionary mapping thread IDs to lists of retrieved chunks ([assistant_agent.py:19]())
- `_THREAD_ID_CTX`: `ContextVar` storing the current thread ID ([assistant_agent.py:20-22]())
- `record_retrieved_chunks()`: Stores chunks for a thread ([assistant_agent.py:41-47]())
- `get_last_retrieved_chunks()`: Retrieves cached chunks ([assistant_agent.py:50-52]())
- `clear_last_retrieved_chunks()`: Clears cache after citation extraction ([assistant_agent.py:55-56]())
- `set_current_thread()`: Sets context variable ([assistant_agent.py:59-60]())
- `reset_current_thread()`: Resets context variable ([assistant_agent.py:63-64]())

**Sources:** [app/backend/app/assistant_agent.py:19-64]()

### Tool Building: Custom Retrieve Tool

When `vector_store.backend` is set to `"custom"`, the system builds a `_retrieve_tool` function tool:

```python
@function_tool(name_override="retrieve_context")
def _retrieve_tool(query: str) -> Dict[str, Any]:
    # Validates query, calls retrieve_custom_chunks, 
    # records chunks, returns payload
```

This tool:
1. Validates the query is non-empty ([assistant_agent.py:89-91]())
2. Calls `retrieve_custom_chunks` from the retrieval pipeline ([assistant_agent.py:92-97]())
3. Constructs payload chunks with metadata ([assistant_agent.py:98-109]())
4. Records chunks to `_RETRIEVAL_CACHE` via thread context ([assistant_agent.py:110]())
5. Returns chunk data to the agent ([assistant_agent.py:111]())

**Sources:** [app/backend/app/assistant_agent.py:87-113]()

---

## Document Management

The document management system scans configured data paths, builds metadata objects, and serves files to clients.

### DocumentMetadata Class

```python
@dataclass(frozen=True, slots=True)
class DocumentMetadata:
    id: str              # SHA1 hash of file path
    filename: str        # File name (e.g., "report.pdf")
    title: str           # Human-readable title
    description: str | None = None
    
    @property
    def stem(self) -> str:
        return Path(self.filename).stem
```

**Sources:** [app/backend/app/documents.py:16-26]()

### Document Scanning Workflow

```mermaid
flowchart TD
    Start["_scan_documents(cfg_path, cfg)<br/>main.py:153"]
    CheckCache["Check _documents_cache<br/>main.py:155-157"]
    
    ExtractConfig["Extract include_extensions<br/>exclude_globs<br/>main.py:159-165"]
    
    GetPaths["Get data.paths from config<br/>main.py:168-169"]
    ExpandPaths["Expand env vars, resolve relative paths<br/>main.py:171-177"]
    Fallback["Fallback to PROJECT_ROOT/../data<br/>main.py:178-179"]
    
    IterateFiles["Iterate root.rglob('*')<br/>main.py:187-188"]
    FilterExt["Filter by extension<br/>main.py:190-192"]
    FilterGlob["Apply exclude_globs<br/>main.py:194-200"]
    
    CreateMeta["Create DocumentMetadata<br/>id = SHA1(path)<br/>main.py:201-209"]
    StoreMapping["Store in id_to_path<br/>main.py:209"]
    
    Dedupe["Deduplicate by id<br/>main.py:212-218"]
    Cache["Cache results<br/>main.py:220-221"]
    Return["Return list<br/>main.py:222"]
    
    Start --> CheckCache
    CheckCache -->|Hit| Return
    CheckCache -->|Miss| ExtractConfig
    
    ExtractConfig --> GetPaths
    GetPaths --> ExpandPaths
    ExpandPaths --> Fallback
    
    Fallback --> IterateFiles
    IterateFiles --> FilterExt
    FilterExt --> FilterGlob
    FilterGlob --> CreateMeta
    CreateMeta --> StoreMapping
    
    StoreMapping --> Dedupe
    Dedupe --> Cache
    Cache --> Return
```

**Sources:** [app/backend/app/main.py:153-222]()

### Document Lookup Methods

The server provides three methods for document resolution:

| Method | Purpose | Search Strategy |
|--------|---------|-----------------|
| `_scan_documents` | Scan filesystem and build metadata | Recursive glob with filters |
| `_lookup_document` | Find document by ID, filename, or title | Sequential search with normalization |
| `_resolve_document_path` | Get filesystem path for document ID | Direct dictionary lookup |

**`_lookup_document` Resolution Order:**
1. Exact match on `document.id` ([main.py:231-232]())
2. Match on normalized filename or stem ([main.py:234-237]())
3. Match on slugified title ([main.py:238-241]())

**Sources:** [app/backend/app/main.py:224-245]()

---

## Memory Store Implementation

`MemoryStore` ([memory_store.py:22-177]()) provides an in-memory implementation of the `ChatKit Store` interface for thread and message persistence.

### Internal Data Structure

```mermaid
classDiagram
    class MemoryStore {
        -Dict~str,_ThreadState~ _threads
        
        +load_thread(thread_id, context) ThreadMetadata
        +save_thread(thread, context)
        +load_threads(limit, after, order, context) Page
        +delete_thread(thread_id, context)
        
        +load_thread_items(thread_id, after, limit, order, context) Page
        +add_thread_item(thread_id, item, context)
        +save_item(thread_id, item, context)
        +load_item(thread_id, item_id, context) ThreadItem
        +delete_thread_item(thread_id, item_id, context)
        
        -_items(thread_id) List
    }
    
    class _ThreadState {
        +ThreadMetadata thread
        +List~ThreadItem~ items
    }
    
    class ThreadMetadata {
        +str id
        +datetime created_at
        +dict metadata
    }
    
    class ThreadItem {
        +str id
        +str type
        +datetime created_at
    }
    
    MemoryStore --> _ThreadState
    _ThreadState --> ThreadMetadata
    _ThreadState --> ThreadItem
```

**Sources:** [app/backend/app/memory_store.py:16-177]()

### Thread Operations

**Thread Metadata CRUD:**

- `load_thread`: Retrieves thread metadata, raises `NotFoundError` if missing ([memory_store.py:30-36]())
- `save_thread`: Creates or updates thread metadata with deep copy ([memory_store.py:38-48]())
- `load_threads`: Returns paginated list with sorting and pagination ([memory_store.py:50-77]())
- `delete_thread`: Removes thread and all items ([memory_store.py:79-80]())

**Thread Items CRUD:**

- `load_thread_items`: Returns paginated items with sorting ([memory_store.py:93-117]())
- `add_thread_item`: Appends item to thread's item list ([memory_store.py:119-122]())
- `save_item`: Updates existing item or appends if new ([memory_store.py:124-132]())
- `load_item`: Retrieves specific item by ID ([memory_store.py:134-140]())
- `delete_thread_item`: Removes item from thread ([memory_store.py:142-146]())

**Sources:** [app/backend/app/memory_store.py:30-146]()

### Pagination Strategy

Both `load_threads` and `load_thread_items` implement cursor-based pagination:

1. Sort items by `created_at` with configurable order ([memory_store.py:103-105]())
2. Find starting index based on `after` cursor ([memory_store.py:107-111]())
3. Slice items with `limit + 1` to detect more pages ([memory_store.py:113]())
4. Set `has_more` flag and compute `next_after` cursor ([memory_store.py:114-116]())

**Sources:** [app/backend/app/memory_store.py:93-117]()

---

## Citation Extraction System

The citation system employs a three-tier fallback strategy to derive document citations from assistant responses.

### Citation Extraction Flow

```mermaid
flowchart TD
    Start["_extract_citations(item, cfg, thread_id)<br/>main.py:318-348"]
    
    Tier1["Tier 1: _citations_from_annotations<br/>main.py:324-326"]
    Check1{Has<br/>citations?}
    Return1["Return citations"]
    
    Tier2["Tier 2: _apply_cached_citations_to_item<br/>main.py:328-330"]
    Check2{Has<br/>citations?}
    Return2["Return derived citations"]
    
    Tier3["Tier 3: Parse text for document references<br/>main.py:332-348"]
    Return3["Return text-based citations"]
    
    Start --> Tier1
    Tier1 --> Check1
    Check1 -->|Yes| Return1
    Check1 -->|No| Tier2
    
    Tier2 --> Check2
    Check2 -->|Yes| Return2
    Check2 -->|No| Tier3
    
    Tier3 --> Return3
```

**Sources:** [app/backend/app/main.py:318-348]()

### Tier 1: Annotations-Based Citations

Extracts citations from `Annotation` objects attached to assistant message content:

1. Iterate through `item.content` and `content.annotations` ([main.py:356-359]())
2. Resolve document via `_resolve_document()` helper ([main.py:360]())
3. Fallback to `_lookup_document()` if needed ([main.py:362-366]())
4. Extract metadata fields (id, filename, title, description) ([main.py:367-386]())
5. Build citation dictionary with `annotation_index` ([main.py:387-395]())

**Sources:** [app/backend/app/main.py:350-396]()

### Tier 2: Chunk-Based Citation Derivation

When annotations are unavailable (custom backend), derives citations from cached retrieval chunks:

```mermaid
flowchart TD
    Start["_apply_cached_citations_to_item<br/>main.py:398-411"]
    Build["_build_citations_from_chunks<br/>main.py:413-502"]
    
    GetChunks["get_last_retrieved_chunks(thread_id)<br/>main.py:419-421"]
    ExtractText["Extract answer_text from item<br/>main.py:423-432"]
    
    ExtractSpans["extract_spans(answer_text, chunks)<br/>retrieval/citations.py<br/>main.py:434-440"]
    
    IterSpans["Iterate spans<br/>main.py:453-499"]
    LookupDoc["_lookup_document for doc_id<br/>main.py:458-459"]
    GetChunkMeta["Get metadata from chunk_lookup<br/>main.py:460-471"]
    
    BuildSource["Create FileSource with metadata<br/>main.py:483-488"]
    CreateAnnotation["Create Annotation with index<br/>main.py:489"]
    BuildCitation["Build citation dict<br/>main.py:491-499"]
    
    AttachAnnotations["Attach annotations to item.content<br/>main.py:406-410"]
    ClearCache["clear_last_retrieved_chunks<br/>main.py:501"]
    
    Start --> Build
    Build --> GetChunks
    GetChunks --> ExtractText
    ExtractText --> ExtractSpans
    
    ExtractSpans --> IterSpans
    IterSpans --> LookupDoc
    LookupDoc --> GetChunkMeta
    GetChunkMeta --> BuildSource
    BuildSource --> CreateAnnotation
    CreateAnnotation --> BuildCitation
    
    BuildCitation --> AttachAnnotations
    AttachAnnotations --> ClearCache
```

**Sources:** [app/backend/app/main.py:398-502]()

**Key Functions:**
- `extract_spans()`: Performs fuzzy text matching between answer and chunks ([main.py:434]())
- `get_last_retrieved_chunks()`: Retrieves cached chunks from assistant agent ([main.py:419]())
- `clear_last_retrieved_chunks()`: Removes cache after processing ([main.py:501]())

### Tier 3: Text-Based Fallback

If both annotation and chunk-based methods fail, parses assistant response text for document references. This is a legacy fallback and typically unused ([main.py:332-348]()).

**Sources:** [app/backend/app/main.py:332-348]()

---

## Configuration Management

The server loads and caches RAG configuration files to determine vector store backend, retrieval parameters, and data paths.

### Configuration Loading

```mermaid
graph TB
    subgraph "Configuration Resolution"
        EnvVar["RAG_CONFIG env var<br/>or default<br/>main.py:137"]
        Resolve["Resolve to absolute path<br/>main.py:146-148"]
        CheckCache["Check _cfg_cache<br/>main.py:149"]
        LoadCfg["load_config(resolved)<br/>main.py:150"]
        Store["Store in _cfg_cache<br/>main.py:149-150"]
    end
    
    subgraph "Configuration Usage"
        VectorBackend["Extract vector_store.backend<br/>main.py:141-142"]
        DataPaths["Extract data.paths<br/>main.py:168-169"]
        IncludeExt["Extract data.include_extensions<br/>main.py:159-162"]
        ExcludeGlob["Extract data.exclude_globs<br/>main.py:163-165"]
        TopK["Extract query.top_k<br/>assistant_agent.py:81"]
        MaxPerSource["Extract query.citations.max_per_source<br/>main.py:437-439"]
    end
    
    EnvVar --> Resolve
    Resolve --> CheckCache
    CheckCache -->|Miss| LoadCfg
    LoadCfg --> Store
    CheckCache -->|Hit| VectorBackend
    
    Store --> VectorBackend
    Store --> DataPaths
    Store --> IncludeExt
    Store --> ExcludeGlob
    Store --> TopK
    Store --> MaxPerSource
```

**Sources:** [app/backend/app/main.py:136-151](), [app/backend/app/assistant_agent.py:81]()

### Cache Structure

The `_cfg_cache` dictionary maps resolved absolute paths to `RootConfig` objects, ensuring each configuration file is parsed only once:

```python
self._cfg_cache: Dict[str, RootConfig] = {}
```

**Sources:** [app/backend/app/main.py:136]()

---

## Response Streaming

The `respond()` method ([main.py:247-294]()) handles the core conversational loop:

```mermaid
sequenceDiagram
    participant Client
    participant Server as KnowledgeAssistantServer
    participant Agent as assistant_agent
    participant Runner as Runner.run_streamed
    participant Stream as stream_agent_response
    
    Client->>Server: UserMessageItem
    Server->>Server: _user_message_text(item)
    Server->>Server: _build_history_prompt()
    Server->>Server: set_current_thread(thread_id)
    
    Server->>Runner: run_streamed(agent, text, context)
    Runner-->>Agent: Execute agent with tools
    
    Agent-->>Runner: Stream events
    Runner->>Stream: Forward events
    
    loop For each event
        Stream->>Server: ThreadStreamEvent
        alt ThreadItemDoneEvent + AssistantMessageItem
            Server->>Server: _apply_cached_citations_to_item()
        end
        Server->>Client: Yield event
    end
    
    Server->>Server: reset_current_thread(token)
```

**Sources:** [app/backend/app/main.py:247-294]()

### History Enrichment

Before sending to the agent, the server enriches the user message with conversation history via `_build_history_prompt()` ([main.py:504-544]()):

1. Load recent thread items (up to `max_turns * 2`) ([main.py:515-523]())
2. Extract text from `UserMessageItem` and `AssistantMessageItem` ([main.py:526-534]())
3. Format as "User: ..." and "Assistant: ..." lines ([main.py:528-534]())
4. Prepend history block to current message ([main.py:540-544]())

This provides the agent with context for multi-turn conversations without modifying the agent's native conversation history.

**Sources:** [app/backend/app/main.py:504-544]()

---

## CORS Configuration

The FastAPI application configures CORS middleware to allow frontend access:

```python
cors_allow_origins = _parse_cors_allow_origins(
    os.getenv("KNOWLEDGE_CORS_ALLOW_ORIGINS")
) or [
    "http://localhost:5172",
    "http://127.0.0.1:5172",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_allow_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Accept", "Content-Type", "Authorization"],
    expose_headers=["Content-Disposition"],
)
```

The `KNOWLEDGE_CORS_ALLOW_ORIGINS` environment variable accepts a comma-separated list of allowed origins. If unset, defaults to local development ports.

**Sources:** [app/backend/app/main.py:551-573]()

---

## Dependency Injection

The server uses FastAPI's dependency injection to provide the `KnowledgeAssistantServer` instance to endpoint handlers:

```python
def get_server() -> KnowledgeAssistantServer:
    return knowledge_server

@app.post("/knowledge/chatkit")
async def chatkit_endpoint(
    request: Request, 
    server: KnowledgeAssistantServer = Depends(get_server)
) -> Response:
    # Handler implementation
```

This pattern allows for cleaner testing and potential future support for multiple server instances.

**Sources:** [app/backend/app/main.py:576-590]()

---

## Summary of Key Backend Patterns

| Pattern | Implementation | Purpose |
|---------|---------------|---------|
| **Caching** | `_cfg_cache`, `_documents_cache`, `_document_path_cache` | Avoid re-parsing configs and re-scanning filesystem |
| **Fallback Strategy** | Three-tier citation extraction | Robustly derive citations across different backends |
| **Context Variables** | `_THREAD_ID_CTX` in assistant_agent.py | Thread-safe retrieval cache access |
| **Dependency Injection** | `Depends(get_server)` | Clean separation of concerns in endpoints |
| **Deep Copying** | `model_copy(deep=True)` throughout MemoryStore | Prevent accidental mutations of stored data |
| **Dynamic Tool Building** | `_build_tools()` based on config | Support multiple vector store backends |
| **History Enrichment** | `_build_history_prompt()` | Multi-turn conversation without agent history mutation |

**Sources:** [app/backend/app/main.py:1-647](), [app/backend/app/assistant_agent.py:1-128](), [app/backend/app/memory_store.py:1-177]()

---

