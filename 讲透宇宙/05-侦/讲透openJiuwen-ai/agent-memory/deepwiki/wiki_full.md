# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README.zh.md](README.zh.md)
- [docs/en/API Docs/long_term_memory.md](docs/en/API Docs/long_term_memory.md)

</details>



## Purpose and Scope
This page serves as the parent overview of **JiuwenMemory** (`agent-memory`), an open-source AutoGenetic memory system designed for AI agents [README.md:1-8](). This document outlines the core concepts, the L0–L3 layered memory architecture, and the overall repository layout. 

As a parent page, this overview provides a high-level summary. For detailed instructions on installation, configuration, and entrypoints, see [Getting Started and Configuration](#1.1). For an in-depth breakdown of module interactions and data flows, see [Architecture Map](#1.2).

Sources: `README.md:1-8`

---

## AutoGenetic Memory System and L0-L3 Architecture
JiuwenMemory rearchitects AI memory from passive storage into an autonomous, self-evolving data asset [README.md:13-26](). Treating memory pieces as "gene segments," the system focuses on precision, efficiency, and cross-organism replication [README.md:7-8](). 

The core architecture relies on a progressive four-tier model (**L0–L3**):
- **L0 (Raw Information)**: Captures raw conversational messages and context.
- **L1 (Summary Memory)**: Compresses dialogs into thematic summaries via background processing [README.md:19-23]().
- **L2 (Structured Memory)**: Extracts semantic, episodic, and variable records [README.md:19]().
- **L3 (User Profile)**: Maintains persistent long-term user characteristics and preferences [README.md:19]().

```mermaid
graph TD
    subgraph Natural_Language_Space
        NL_Auto["AutoGeneticMemorySystem"] --> NL_Layers["LayeredMemoryL0toL3"]
    end
    subgraph Code_Entity_Space
        NL_Auto --> Code_Engine["jiuwen_memory.memory_core.long_term_memory:LongTermMemory"]
        NL_Layers --> Code_Config["jiuwen_memory.memory_core.config.config:AgentMemoryConfig"]
    end
```

Sources: `README.md:5-26`, `docs/en/API Docs/long_term_memory.md:1-10`

---

## Repository Layout
The codebase is organized into a modular structure separating the Python core engine, the Java/Vue enterprise management console, plugins, documentation, and test suites [README.md:35-40]().

- `jiuwen_memory/`: The core Python engine containing memory management, storage foundations, retrieval mechanisms, and server interfaces.
- `agent-memory-platform/`: A Java Spring Boot and Vue 3 console for multi-tenant management, configuration control, and operational logging.
- `plugins/`: Integration modules such as OpenClaw lifecycle hooks and agent extensions [README.md:37-39]().
- `docs/`: Comprehensive bilingual API and user documentation.
- `tests/`: Unit and integration test suites covering the engine and REST endpoints.

```mermaid
graph LR
    subgraph Natural_Language_Space
        Repo_Python["PythonEngine"] --> Repo_Platform["ManagementConsole"]
        Repo_Python --> Repo_Plugins["EcosystemPlugins"]
    end
    subgraph Code_Entity_Space
        Repo_Python --> Code_Jiwen["jiuwen_memory/"]
        Repo_Platform --> Code_Platform["agent-memory-platform/"]
        Repo_Plugins --> Code_Plugins["plugins/"]
    end
```

Sources: `README.md:35-40`

---

## Child Pages Navigation
For deeper technical specifications, refer to the following child pages:
- [Getting Started and Configuration](#1.1) — Covers pyproject extras, environment variables, CLI entrypoints, and scope configurations.
- [Architecture Map](#1.2) — Covers internal module coupling (`memory_core`, `foundation`, `server`, `retrieval`) and data flow trajectories.

Sources: `README.md:49-110`

---

# Page: Getting Started and Configuration

# Getting Started and Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/en/API Docs/config.md](docs/en/API Docs/config.md)
- [docs/en/API Docs/graph_memory.md](docs/en/API Docs/graph_memory.md)
- [jiuwen_memory/memory_core/config/config.py](jiuwen_memory/memory_core/config/config.py)
- [jiuwen_memory/memory_core/manage/mem_model/memory_unit.py](jiuwen_memory/memory_core/manage/mem_model/memory_unit.py)
- [jiuwen_memory/memory_core/process/dreaming/store.py](jiuwen_memory/memory_core/process/dreaming/store.py)
- [jiuwen_memory/memory_core/process/dreaming/sweeper.py](jiuwen_memory/memory_core/process/dreaming/sweeper.py)
- [jiuwen_memory/memory_core/process/extract/generation.py](jiuwen_memory/memory_core/process/extract/generation.py)
- [jiuwen_memory/server/.env.example](jiuwen_memory/server/.env.example)
- [pyproject.toml](pyproject.toml)
- [tests/unit_tests/core/memory/graph/graph_memory/test_base.py](tests/unit_tests/core/memory/graph/graph_memory/test_base.py)
- [uv.lock](uv.lock)

</details>



## Purpose and Scope

This section covers the foundational setup, installation, environment variables, CLI entrypoints, and core configuration constructs of JiuwenMemory (`agent-memory`). It details how dependencies and optional backends are managed via `pyproject.toml` and `uv.lock`, how runtime parameters are defined through `.env` configurations, and how engine behavior is controlled programmatically via `MemoryEngineConfig`, `MemoryScopeConfig`, `AgentMemoryConfig`, and `DreamingConfig`.

Sources: `pyproject.toml:1-156` [pyproject.toml](), `jiuwen_memory/server/.env.example:1-134` [jiuwen_memory/server/.env.example](), `jiuwen_memory/memory_core/config/config.py:1-126` [jiuwen_memory/memory_core/config/config.py]()

---

## Package Installation and Dependency Extras

JiuwenMemory utilizes a modern packaging setup based on `setuptools` and `uv` dependency locking [pyproject.toml:1-83](). The core library is constrained to Python `>=3.11,<3.14` [pyproject.toml:10](). 

Optional capabilities and backend integrations are exposed via project optional-dependencies extras [pyproject.toml:54-70]():

| Extra Name | Dependencies | Purpose |
| :--- | :--- | :--- |
| `server` | `uvicorn`, `fastapi`, `python-dotenv`, `mcp` | Enables REST and MCP memory server entrypoints [pyproject.toml:65]() |
| `file-index` | `sqlite-vec`, `watchdog`, `jieba` | Enables SQLite/Markdown hybrid file-index backend [pyproject.toml:68]() |
| `chromadb` / `milvus` / `elasticsearch` / `gaussvector` | Varies by vector DB client | Vector store backends [pyproject.toml:55-57]() |
| `sqlite` / `postgres` / `mysql` / `gaussdb` / `redis` | Varies by SQL/KV driver | Persistent KV and relational database stores [pyproject.toml:58-62]() |
| `all` | Union of all storage, vector, server, and file extras | Full installation profile [pyproject.toml:70]() |

```mermaid
title "PackageExtrasAndModuleMapping"
graph TD
    sub-graph-pyproject["pyproject.toml Extras"]
    sub-graph-modules["Code Modules & Entrypoints"]

    ExtraServer["server"] --> FastAPIApp["jiuwen_memory.server.memory_server:main"]
    ExtraServer --> MCPServer["jiuwen_memory.server.mcp_server:main"]
    ExtraFile["file-index"] --> FileIndex["jiuwen_memory.foundation.index.file_memory_index"]
    ExtraStorage["all-storage"] --> DBStores["SqlDbStore / DbBasedKVStore"]
    ExtraVector["all-vector"] --> VectorStores["Chroma / Milvus / ES Stores"]

    sub-graph-pyproject --> sub-graph-modules
```

Sources: `pyproject.toml:1-83` [pyproject.toml]()

---

## Environment Configuration (.env)

The server and storage components load runtime parameters from environment variables or a `.env` file (modeled after `jiuwen_memory/server/.env.example`) [jiuwen_memory/server/.env.example:1-133](). Key configuration blocks include:

- **LLM Configuration**: `MODEL_PROVIDER`, `API_BASE`, `API_KEY`, `MODEL_NAME`, `MODEL_SSL_VERIFY`, `TEMPERATURE` [jiuwen_memory/server/.env.example:1-18]()
- **Embedding Configuration**: `EMBED_MODEL_NAME`, `EMBED_API_BASE`, `EMBED_API_KEY` [jiuwen_memory/server/.env.example:20-29]()
- **Server Configuration**: `MEMORY_DATA_DIR`, `IP`, `PORT`, `MEMORY_API_KEY` [jiuwen_memory/server/.env.example:30-41]()
- **MCP Configuration**: `MCP_DEFAULT_USER_ID`, `MCP_DEFAULT_SCOPE_ID`, `MCP_TRANSPORT`, `MCP_HOST`, `MCP_PORT` [jiuwen_memory/server/.env.example:43-53]()
- **Store & Index Backend**: `DB_URL`, `KV_STORE_TYPE`, `DB_STORE_TYPE`, `INDEX_BACKEND`, `FILE_MEMORY_DATA_DIR`, `VECTOR_STORE_TYPE` [jiuwen_memory/server/.env.example:55-84]()
- **Encryption Configuration**: `MEMORY_CODEC`, `SM4_KEY`, `AES_KEY` [jiuwen_memory/server/.env.example:120-133]()

Sources: `jiuwen_memory/server/.env.example:1-134` [jiuwen_memory/server/.env.example]()

---

## CLI Entrypoints

JiuwenMemory defines standard script entrypoints in `pyproject.toml` [pyproject.toml:72-74]() that map directly to server initialization routines:

```ini
[project.scripts]
memory-server = "jiuwen_memory.server.memory_server:main"
memory-mcp = "jiuwen_memory.server.mcp_server:main"
```

```mermaid
title "CLIEntrypointExecutionFlow"
graph LR
    CLI1["memory-server CLI"] --> MainServer["jiuwen_memory.server.memory_server:main"]
    CLI2["memory-mcp CLI"] --> MainMCP["jiuwen_memory.server.mcp_server:main"]

    MainServer --> FastAPIApp["FastAPI REST Application"]
    MainMCP --> MCPServer["Model Context Protocol Server"]
```

Sources: `pyproject.toml:72-74` [pyproject.toml]()

---

## Configuration Classes and Scopes

Programmatic configuration of the memory engine is managed through Pydantic models defined in `jiuwen_memory.memory_core.config.config` [jiuwen_memory/memory_core/config/config.py:1-125]():

```mermaid
title "ConfigurationHierarchy"
graph TD
    EngineConfig["MemoryEngineConfig"] --> ScopeConfig["MemoryScopeConfig"]
    EngineConfig --> AgentConfig["AgentMemoryConfig"]
    EngineConfig --> DreamingCfg["DreamingConfig"]
    DreamingCfg --> ForgettingCfg["ForgettingConfig"]

    EngineConfig -->|"crypto_key & codec"| CodecInjection["AesStorageCodec / Registered Codecs"]
    ScopeConfig -->|"model_cfg / embedding_cfg"| ScopeIsolation["Multi-Tenant Scope Isolation"]
```

### MemoryEngineConfig
Defines global engine-level parameters [docs/en/API Docs/config.md:11-30]():
- `default_model_cfg`: Default `ModelRequestConfig` for memory extraction [jiuwen_memory/memory_core/config/config.py:19]()
- `default_model_client_cfg`: Default `ModelClientConfig` for LLM client connectivity [jiuwen_memory/memory_core/config/config.py:20]()
- `forbidden_variables`: Comma-separated variable names excluded from extraction [jiuwen_memory/memory_core/config/config.py:21]()
- `crypto_key`: `bytes` (must be empty or exactly 32 bytes for AES-256-GCM encryption) [jiuwen_memory/memory_core/config/config.py:23,33-47]()
- `codec`: Registered third-party encryption codec name (e.g., `"sm4"`) [jiuwen_memory/memory_core/config/config.py:31]()

### MemoryScopeConfig
Defines isolated model, vector, and extraction prompt definitions per `scope_id` [jiuwen_memory/memory_core/config/config.py:49-68]():
- `model_cfg` & `model_client_cfg`: Scope-specific LLM settings [jiuwen_memory/memory_core/config/config.py:50-51]()
- `embedding_cfg`: Scope-specific embedding parameters [jiuwen_memory/memory_core/config/config.py:52]()
- Extraction definitions (`user_profile_definition`, `semantic_memory_definition`, `episodic_memory_definition`, `important_memory_definition`) [jiuwen_memory/memory_core/config/config.py:53-65]()

### AgentMemoryConfig and DreamingConfig
- `AgentMemoryConfig`: Toggles long-term memory categories (`enable_long_term_mem`, `enable_user_profile`, `enable_semantic_memory`, `enable_episodic_memory`, `enable_summary_memory`) and variables [jiuwen_memory/memory_core/config/config.py:70-76]().
- `DreamingConfig`: Orchestrates offline memory consolidation intervals, compression budgets, and Ebbinghaus forgetting thresholds via `ForgettingConfig` [jiuwen_memory/memory_core/config/config.py:79-125]().

Sources: `docs/en/API Docs/config.md:1-102` [docs/en/API Docs/config.md](), `jiuwen_memory/memory_core/config/config.py:1-126` [jiuwen_memory/memory_core/config/config.py]()

---

# Page: Architecture Map

# Architecture Map

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README.zh.md](README.zh.md)
- [jiuwen_memory/memory_core/long_term_memory.py](jiuwen_memory/memory_core/long_term_memory.py)
- [jiuwen_memory/server/memory_server.py](jiuwen_memory/server/memory_server.py)

</details>



## Purpose and Scope
This page details the macro-architecture of the `jiuwen_memory` (agent-memory) codebase. It maps the logical subsystems—`memory_core`, `foundation`, `server`, `retrieval`, `plugins`, and the Java/Vue management console (`agent-memory-platform`)—to their underlying Python and Java code entities. It outlines the complete execution lifecycle and data flow for core operations, focusing specifically on the write path (from `add_messages` to extraction and storage) and the search path (from user queries to vector/hybrid retrieval and ranking).

Sources: `README.md`, `README.zh.md`, `jiuwen_memory/memory_core/long_term_memory.py`, `jiuwen_memory/server/memory_server.py`

---

## 1. Subsystem Decomposition and Code Mapping

The JiuwenMemory engine is structured into modular layers that decouple high-level agent memory workflows from low-level storage backends, cryptographic codecs, and communication interfaces.

```mermaid
graph TD
    subgraph NaturalLanguageSpace ["Natural Language Space"]
        Agent[("AI Agent / Client")] -->|"HTTP / MCP / SDK"| REST["REST API / MCP Server"]
        Agent -->|"Python Call"| Core["Long-Term Memory Engine"]
    end

    subgraph CodeEntitySpace ["Code Entity Space"]
        REST -->|"FastAPI App"| Srv["jiuwen_memory.server.memory_server:FastAPI"]
        Core -->|"Singleton Engine"| LTM["jiuwen_memory.memory_core.long_term_memory:LongTermMemory"]
        LTM -->|"Manages"| WM["jiuwen_memory.memory_core.manage.index.write_manager:WriteManager"]
        LTM -->|"Manages"| SM["jiuwen_memory.memory_core.manage.search.search_manager:SearchManager"]
        WM -->|Persists| IDX["jiuwen_memory.foundation.store.index.simple_memory_index:SimpleMemoryIndex"]
        IDX -->|Vector ops| VS["jiuwen_memory.foundation.store.base_vector_store:BaseVectorStore"]
        IDX -->|KV ops| KV["jiuwen_memory.foundation.store.base_kv_store:BaseKVStore"]
    end

    Srv --> LTM
```
*Figure 1: Subsystem Mapping from Natural Language Space to Code Entity Space.*

### Subsystem Directory Layout & Responsibilities
* **`jiuwen_memory/memory_core/`**: Contains the core cognitive engine, including `LongTermMemory` [jiuwen_memory/memory_core/long_term_memory.py:112-122] singleton, memory managers (`WriteManager`, `SearchManager`, `FragmentMemoryManager`, `SummaryManager`, `VariableManager`) [jiuwen_memory/memory_core/long_term_memory.py:38-45], and background processes like the Auto-Dreaming orchestrator and Ebbinghaus forgetting evaluator.
* **`jiuwen_memory/foundation/`**: Implements foundational infrastructure abstractions, including storage contracts (`BaseKVStore`, `BaseDbStore`, `BaseVectorStore`, `BaseMessageStore`, `BaseMemoryIndex`) [jiuwen_memory/memory_core/long_term_memory.py:37-56], the Filter DSL, storage codecs (`AesStorageCodec`) [jiuwen_memory/memory_core/long_term_memory.py:65-69], and LLM client abstractions.
* **`jiuwen_memory/retrieval/`**: Houses vector embedding clients (`APIEmbedding`) [jiuwen_memory/memory_core/long_term_memory.py:54] and search ranking utilities.
* **`jiuwen_memory/server/`**: Provides FastAPI endpoints (`memory_server.py`) [jiuwen_memory/server/memory_server.py:8], store factories (`store_factory.py`) [jiuwen_memory/server/memory_server.py:26-32], config centers, and Model Context Protocol (MCP) servers.
* **`agent-memory-plugin/`**: Contains agent integration lifecycle scripts (e.g., OpenClaw bindings).
* **`agent-memory-platform/`**: Spring Boot backend and Vue 3 frontend console managing tenants, scopes, configs, logs, and operational telemetry.

Sources: `README.md`, `jiuwen_memory/memory_core/long_term_memory.py`, `jiuwen_memory/server/memory_server.py`

---

## 2. Write Path: Data Flow from `add_messages` to Storage

When an agent calls `add_messages(...)`, the engine processes raw conversation chunks through extraction pipelines, conflict detection checks, and persistent indexing.

```mermaid
sequenceDiagram
    autonumber
    participant Agent as "AI Agent"
    participant LTM as "LongTermMemory"
    participant WM as "WriteManager"
    participant Ext as "Generator / Extractor"
    participant Chk as "MemUpdateChecker"
    participant IDX as "SimpleMemoryIndex"
    participant KV as "BaseKVStore"

    Agent->>LTM: "add_messages(messages, user_id, scope_id, agent_config)"
    LTM->>WM: "write(messages, scope_id, user_id)"
    WM->>Ext: "Extract memory units (UserProfile, Semantic, Episodic)"
    Ext-->>WM: "Raw extracted MemoryUnits"
    WM->>Chk: "Check semantic conflicts (ADD / UPDATE / DELETE)"
    Chk-->>WM: "Validated delta operations"
    WM->>IDX: "Upsert MemoryDocs into index"
    IDX->>KV: "Persist metadata and KV chunks"
    IDX-->>WM: "Commit confirmation"
    WM-->>LTM: "AddMemResult"
    LTM-->>Agent: "Return structured extraction result"
```
*Figure 2: Write Path Data Flow for `add_messages`.*

### Step-by-Step Write Lifecycle
1. **Entry Point**: The agent invokes `LongTermMemory.add_messages(...)`, supplying user messages, assistant responses, scope identifiers, and `AgentMemoryConfig`.
2. **Routing**: `LongTermMemory` delegates conversation persistence and memory extraction to `WriteManager`.
3. **Extraction**: The extraction pipeline processes the dialogue context, categorizing extracted insights into L0–L3 memory tiers (e.g., `FragmentMemoryUnit`, `SummaryUnit`, `VariableUnit`) [jiuwen_memory/memory_core/long_term_memory.py:43-44].
4. **Conflict Resolution**: `MemUpdateChecker` evaluates newly extracted memories against existing records using LLM analysis to determine whether to `ADD`, `UPDATE`, or `DELETE`.
5. Data Indexing & Persistence: `SimpleMemoryIndex` [jiuwen_memory/memory_core/long_term_memory.py:57] or `FileMemoryIndex` coordinates vector embedding generation via `APIEmbedding` [jiuwen_memory/memory_core/long_term_memory.py:54] and persists payloads across `BaseVectorStore` and `BaseKVStore` [jiuwen_memory/memory_core/long_term_memory.py:134-135].

Sources: `README.md`, `README.zh.md`, `jiuwen_memory/memory_core/long_term_memory.py`

---

## 3. Search Path: Retrieval and Ranking Flow

When an agent needs context for a user prompt, it queries the memory engine using semantic search parameters handled by `SearchManager`.

```mermaid
sequenceDiagram
    autonumber
    participant Agent as "AI Agent"
    participant LTM as "LongTermMemory"
    participant SM as "SearchManager"
    participant Emb as "APIEmbedding"
    participant IDX as "BaseMemoryIndex"
    participant KV as "BaseKVStore"

    Agent->>LTM: "search(query, user_id, scope_id, search_params)"
    LTM->>SM: "search_memory(query, scope_id, user_id, params)"
    SM->>Emb: "Embed query text into vector"
    Emb-->>SM: "Query vector embedding"
    SM->>IDX: "Hybrid search (Vector KNN + Filter DSL pushdown)"
    IDX-->>SM: "Matching MemoryDocs & scores"
    SM->>KV: "Append retrieval history (retrieve_history FIFO window)"
    SM-->>LTM: "Sorted list of MemResult"
    LTM-->>Agent: "Return relevant memories"
```
*Figure 3: Search Path Data Flow and Retrieval Pipeline.*

### Step-by-Step Search Lifecycle
1. **Query Dispatch**: `LongTermMemory.search(...)` passes the query string and filtering criteria to `SearchManager` [jiuwen_memory/memory_core/long_term_memory.py:45].
2. **Vectorization**: The query string is transformed into a dense vector via the configured embedding model (`APIEmbedding`) [jiuwen_memory/memory_core/long_term_memory.py:54].
3. **Hybrid Search & Filtering**: `BaseMemoryIndex` executes similarity search against `BaseVectorStore` while applying filter conditions via the Filter DSL.
4. **Retrieval History Logging**: `SearchManager` records the retrieval event in a FIFO rolling window (`retrieve_history` prefix, bounded by `_RETRIEVAL_HISTORY_MAX_LEN = 20`) [jiuwen_memory/memory_core/long_term_memory.py:74-88], which feeds recency reinforcement for the Ebbinghaus forgetting scoring mechanism.

Sources: `README.md`, `jiuwen_memory/memory_core/long_term_memory.py`, `jiuwen_memory/server/memory_server.py`

---

# Page: Memory Core Engine

# Memory Core Engine

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/en/API Docs/long_term_memory.md](docs/en/API Docs/long_term_memory.md)
- [jiuwen_memory/memory_core/long_term_memory.py](jiuwen_memory/memory_core/long_term_memory.py)
- [jiuwen_memory/server/memory_server.py](jiuwen_memory/server/memory_server.py)

</details>



The Memory Core Engine (`jiuwen_memory/memory_core/`) serves as the central orchestrator for JiuwenMemory's AutoGenetic memory system [jiuwen_memory/memory_core/long_term_memory.py:112-140]. It manages storage integration, memory extraction pipelines, middle-term caching (`MemoryTurbo`), background cognitive loops (dreaming and Ebbinghaus forgetting), and graph-based memory structures. 

For implementation details, refer to the individual child sections below.

---

## 2.1 LongTermMemory API and Lifecycle

The `LongTermMemory` class is implemented as a singleton engine that coordinates all memory management functions [jiuwen_memory/memory_core/long_term_memory.py:112-140]. It uses a parameterless constructor combined with step-by-step initialization via `register_store`, `set_config`, and `set_scope_config` [docs/en/API Docs/long_term_memory.md:18-24]. It exposes public APIs for message ingestion (`add_messages`), semantic search (`search`), paginated queries, and conditional deletion.

For details, see [LongTermMemory API and Lifecycle](#2.1).

Sources:
- `jiuwen_memory/memory_core/long_term_memory.py:112-140`
- `docs/en/API Docs/long_term_memory.md:1-121`

---

## 2.2 Memory Managers (Write and Search Paths)

Memory routing, persistence, and retrieval are handled by specialized managers. The ingestion path utilizes `WriteManager` [jiuwen_memory/memory_core/long_term_memory.py:40], `FragmentMemoryManager` [jiuwen_memory/memory_core/long_term_memory.py:38], `SummaryManager` [jiuwen_memory/memory_core/long_term_memory.py:41], and `VariableManager` [jiuwen_memory/memory_core/long_term_memory.py:39] to parse and store incoming messages into structured units. The retrieval path uses `SearchManager` [jiuwen_memory/memory_core/long_term_memory.py:45] combined with filter DSL expressions to query indexes.

```mermaid
Title: "Write and Search Routing Pipeline"
graph TD
    UserMessageSpace["User Message Input"] --> LongTermMemoryClass["jiuwen_memory/memory_core/long_term_memory.py:LongTermMemory"]
    LongTermMemoryClass --> WriteMgr["jiuwen_memory/memory_core/manage/index/write_manager.py:WriteManager"]
    LongTermMemoryClass --> SearchMgr["jiuwen_memory/memory_core/manage/search/search_manager.py:SearchManager"]
    WriteMgr --> FragMgr["jiuwen_memory/memory_core/manage/index/fragment_memory_manager.py:FragmentMemoryManager"]
    WriteMgr --> SumMgr["jiuwen_memory/memory_core/manage/index/summary_manager.py:SummaryManager"]
    WriteMgr --> VarMgr["jiuwen_memory/memory_core/manage/index/variable_manager.py:VariableManager"]
    SearchMgr --> MemIndex["jiuwen_memory/foundation/store/base_memory_index.py:BaseMemoryIndex"]
```

For details, see [Memory Managers (Write and Search Paths)](#2.2).

Sources:
- `jiuwen_memory/memory_core/long_term_memory.py:35-45`

---

## 2.3 Middle-Term Memory (MemoryTurbo)

Middle-term memory provides a caching layer (`MiddleTermMemoryManager`) that buffers recent interactions and conversational state before promotion to long-term storage [jiuwen_memory/memory_core/long_term_memory.py:42]. It integrates with `SemanticStore` [jiuwen_memory/memory_core/long_term_memory.py:70] and executes the `middle_mem_to_long` promotion loop to consolidate units.

For details, see [Middle-Term Memory (MemoryTurbo)](#2.3).

Sources:
- `jiuwen_memory/memory_core/long_term_memory.py:42-70`

---

## 2.4 Extraction and Generation Pipeline

The extraction subsystem translates raw dialog messages into structured memory units (user profiles, semantic facts, and episodic fragments) via `Generator` [jiuwen_memory/memory_core/long_term_memory.py:24], prompt templates, and update checkers executing ADD, UPDATE, and DELETE strategies.

For details, see [Extraction and Generation Pipeline](#2.4).

Sources:
- `jiuwen_memory/memory_core/long_term_memory.py:24-34`

---

## 2.5 Dreaming and Ebbinghaus Forgetting

To manage memory hygiene and mimic human cognitive consolidation, the engine runs background loops. `DreamingOrchestrator` uses `MessageStoreSessionSource` [jiuwen_memory/memory_core/long_term_memory.py:28], `MemoryUnitKnowledgeStore` [jiuwen_memory/memory_core/long_term_memory.py:27], and `Sweeper` [jiuwen_memory/memory_core/long_term_memory.py:29], while `EbbinghausEvaluator` calculates forgetting curves, reinforcement scores, and blacklisting policies [jiuwen_memory/memory_core/long_term_memory.py:31-34].

For details, see [Dreaming and Ebbinghaus Forgetting](#2.5).

Sources:
- `jiuwen_memory/memory_core/long_term_memory.py:25-34`

---

## 2.6 Graph Memory

The knowledge graph subsystem handles relational memory entities. It provides specialized extraction models for entity and relation recognition, graph store abstractions, and multi-hop graph retrieval capabilities integrated with the core engine.

For details, see [Graph Memory](#2.6).

Sources:
- `jiuwen_memory/memory_core/long_term_memory.py:112-140`

---

## 2.7 Memory Metadata and Migrations

Metadata tracking and schema evolution are handled by metadata managers and migration runners [jiuwen_memory/memory_core/long_term_memory.py:63-64]. These utilities ensure backward compatibility across KV stores, SQL databases, and index configurations during engine startup and updates.

```mermaid
Title: "Metadata and Migration Architecture"
graph TD
    SystemStartup["Engine Startup Pipeline"] --> MigrationRunner["jiuwen_memory/memory_core/migration/run_migrations.py:run_kv_migrations"]
    MigrationRunner --> SqlMigrate["jiuwen_memory/memory_core/migration/run_migrations.py:run_sql_migrations"]
    MigrationRunner --> VecMigrate["jiuwen_memory/memory_core/migration/run_migrations.py:run_vector_migrations"]
    SqlMigrate --> DbStoreInstance["jiuwen_memory/memory_core/manage/mem_model/sql_db_store.py:SqlDbStore"]
    VecMigrate --> VectorStoreInstance["jiuwen_memory/foundation/store/base_vector_store.py:BaseVectorStore"]
```

For details, see [Memory Metadata and Migrations](#2.7).

Sources:
- `jiuwen_memory/memory_core/long_term_memory.py:63-64`

---

# Page: LongTermMemory API and Lifecycle

# LongTermMemory API and Lifecycle

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/en/API Docs/long_term_memory.md](docs/en/API Docs/long_term_memory.md)
- [jiuwen_memory/memory_core/long_term_memory.py](jiuwen_memory/memory_core/long_term_memory.py)
- [jiuwen_memory/server/memory_server.py](jiuwen_memory/server/memory_server.py)
- [tests/unit_tests/core/memory/test_long_term_memory_register_plugin.py](tests/unit_tests/core/memory/test_long_term_memory_register_plugin.py)

</details>



## Purpose and Scope

`LongTermMemory` serves as the core unified long-term memory management engine within the JiuwenMemory system [docs/en/API Docs/long_term_memory.md:1-10](). It coordinates memory persistence, multi-tenant isolation via `scope_id`, variable extraction, vector retrieval, and lifecycle management [docs/en/API Docs/long_term_memory.md:3-9](). 

This page details the singleton lifecycle, initialization phases, storage registration (`register_store`), plugin registration (`register_plugin`), configuration injection (`set_config`, `set_scope_config`), message ingestion (`add_messages`), semantic and structured search (`search`), pagination, and deletion APIs.

---

## Singleton Lifecycle and Initialization

`LongTermMemory` adopts the `Singleton` metaclass pattern to ensure a single, globally shared engine instance per process [jiuwen_memory/memory_core/long_term_memory.py:112-112](), [docs/en/API Docs/long_term_memory.md:15-18](). 

The initialization workflow uses a parameterless constructor followed by step-by-step assembly [docs/en/API Docs/long_term_memory.md:20-24]():
1. **Instantiation**: `LongTermMemory()` initializes internal fields to `None` (such as `kv_store`, `vector_store`, `db_store`, `message_store`, `memory_index`, and manager references) [docs/en/API Docs/long_term_memory.md:29-38]().
2. **Storage Registration**: `await register_store(...)` connects underlying persistence layers [docs/en/API Docs/long_term_memory.md:21-21]().
3. **Configuration**: `set_config(MemoryEngineConfig(...))` establishes global model request configs and database parameters [docs/en/API Docs/long_term_memory.md:22-23]().
4. **Scope Configuration**: Optional `set_scope_config(scope_id, MemoryScopeConfig(...))` configures tenant-specific parameters [docs/en/API Docs/long_term_memory.md:23-24]().

```mermaid
graph TD
    sub5["Natural Language Space: Client Boot"]
    sub6["Code Entity Space: LongTermMemory Initialization"]

    sub5 -->| "1. Parameterless Construct" | sub6
    sub6 -->| "LongTermMemory()" | A["Singleton Instance Creation"]
    A -->| "2. Bind Storage" | B["await register_store(...)"]
    B -->| "3. Set Global Config" | C["set_config(MemoryEngineConfig)"]
    C -->| "4. Set Tenant Scope" | D["set_scope_config(scope_id, MemoryScopeConfig)"]

    style A fill:#fff,stroke:#333,stroke-width:2px
    style B fill:#fff,stroke:#333,stroke-width:2px
    style C fill:#fff,stroke:#333,stroke-width:2px
    style D fill:#fff,stroke:#333,stroke-width:2px
```
*Sources: `jiuwen_memory/memory_core/long_term_memory.py:112-140`, `docs/en/API Docs/long_term_memory.md:12-40`*

---

## Core APIs and Lifecycle Methods

### Storage Registration (`register_store`)
The `register_store` method configures the storage backend drivers and initializes automatic table structures and memory indices [docs/en/API Docs/long_term_memory.md:41-75]():

```python
async def register_store(
    self,
    kv_store: BaseKVStore,
    vector_store: BaseVectorStore | None = None,
    db_store: BaseDbStore | None = None,
    embedding_model: Embedding | None = None,
    message_store: BaseMessageStore | None = None,
    *,
    index_backend: str = "simple",
    file_root_dir: str | None = None,
) -> None
```
- **`kv_store`**: Required key-value store (`BaseKVStore`) for config and structured data [docs/en/API Docs/long_term_memory.md:60-61]().
- **`vector_store`**: Optional vector store (`BaseVectorStore`) for semantic similarity indexing [docs/en/API Docs/long_term_memory.md:61-62]().
- **`db_store`**: Optional relational database store (`BaseDbStore`) for messages and scope mappings [docs/en/API Docs/long_term_memory.md:62-63]().
- **`index_backend`**: Determines memory indexing strategy (`"simple"` registers `SimpleMemoryIndex`; `"file"` registers `FileMemoryIndex` backed by Markdown and SQLite) [docs/en/API Docs/long_term_memory.md:65-67](). When `index_backend="file"`, `register_store` automatically activates the watchdog file watcher via `start_watcher()` [tests/unit_tests/core/memory/test_long_term_memory_register_plugin.py:110-142]().

### Plugin Registration (`register_plugin`)
`register_plugin` allows dynamic injection of custom `BaseMemoryIndex` implementations or auxiliary storage extensions [tests/unit_tests/core/memory/test_long_term_memory_register_plugin.py:24-42](). The first registered plugin is assigned as the default `memory_index` [tests/unit_tests/core/memory/test_long_term_memory_register_plugin.py:39-42]().

### Configuration APIs (`set_config` and `set_scope_config`)
- **`set_config(config: MemoryEngineConfig)`**: Injects global execution limits, default LLM model parameters, and encryption options.
- **`set_scope_config(scope_id: str, scope_config: MemoryScopeConfig)`**: Overrides tenant-specific retrieval thresholds, embedding instances, and memory promotion rules for a given `scope_id`.

```mermaid
graph TD
    sub7["Natural Language Space: Engine Routing"]
    sub8["Code Entity Space: LongTermMemory Methods"]

    sub7 -->| "Ingest Conversation" | sub8
    sub8 -->| "Write Path" | A["add_messages()"]
    sub8 -->| "Retrieve Knowledge" | B["search()"]
    sub8 -->| "Paginate Results" | C["pagination()"]
    sub8 -->| "Purge Records" | D["delete_mem_by_id() / delete_scope()"]

    style A fill:#fff,stroke:#333,stroke-width:2px
    style B fill:#fff,stroke:#333,stroke-width:2px
    style C fill:#fff,stroke:#333,stroke-width:2px
    style D fill:#fff,stroke:#333,stroke-width:2px
```
*Sources: `jiuwen_memory/memory_core/long_term_memory.py:112-140`, `docs/en/API Docs/long_term_memory.md:1-120`*

### Ingestion, Search, Pagination, and Deletion APIs
- **`add_messages`**: Ingests new chat turns (`UserMessage`, `AssistantMessage`), triggering the write pipeline (`WriteManager`, extraction, and index updates).
- **`search`**: Executes hybrid or semantic lookups through `SearchManager`, supporting filter DSL constraints (`FilterGroup`).
- **`pagination`**: Retrieves paginated memory lists across tenants or scopes.
- **`deletion`**: Purges specific memory entries by ID or removes complete scope namespaces (`delete_mem_by_id`, `delete_scope`).

---
Sources: 
- `jiuwen_memory/memory_core/long_term_memory.py:1-140`
- `jiuwen_memory/server/memory_server.py:103-176`
- `docs/en/API Docs/long_term_memory.md:1-120`
- `tests/unit_tests/core/memory/test_long_term_memory_register_plugin.py:1-145`

---

# Page: Memory Managers (Write and Search Paths)

# Memory Managers (Write and Search Paths)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jiuwen_memory/foundation/store/base_memory_index.py](jiuwen_memory/foundation/store/base_memory_index.py)
- [jiuwen_memory/memory_core/manage/index/middle_mem_manager.py](jiuwen_memory/memory_core/manage/index/middle_mem_manager.py)
- [jiuwen_memory/memory_core/manage/index/variable_manager.py](jiuwen_memory/memory_core/manage/index/variable_manager.py)
- [jiuwen_memory/memory_core/manage/index/write_manager.py](jiuwen_memory/memory_core/manage/index/write_manager.py)
- [jiuwen_memory/memory_core/manage/mem_meta/__init__.py](jiuwen_memory/memory_core/manage/mem_meta/__init__.py)
- [jiuwen_memory/memory_core/manage/search/search_manager.py](jiuwen_memory/memory_core/manage/search/search_manager.py)
- [jiuwen_memory/server/config_center_api.py](jiuwen_memory/server/config_center_api.py)
- [jiuwen_memory/server/log_center_api.py](jiuwen_memory/server/log_center_api.py)
- [tests/unit_tests/core/memory/manage/index/test_manage.py](tests/unit_tests/core/memory/manage/index/test_manage.py)
- [tests/unit_tests/core/memory/process/forgetting/test_delete_mem_cleanup.py](tests/unit_tests/core/memory/process/forgetting/test_delete_mem_cleanup.py)
- [tests/unit_tests/core/memory/test_long_term_memory_middle_mutations.py](tests/unit_tests/core/memory/test_long_term_memory_middle_mutations.py)

</details>



## Purpose and Scope
This page details the implementation, routing logic, and execution pathways of memory managers within the `jiuwen_memory` engine (`jiuwen_memory/memory_core/manage/`). It covers the architectural division of labor between `WriteManager`, `SearchManager`, and concrete subclass managers (`FragmentMemoryManager`, `SummaryManager`, `VariableManager`, and `MiddleTermMemoryManager`), alongside filter DSL normalization and retrieval history tracking.

---

## 1. Memory Manager Architecture & Component Hierarchy

The memory management subsystem coordinates persistence, retrieval, updates, and deletions across heterogeneous storage backends (vector indices, relational/KV stores). The engine delegates operations through centralized coordinator classes (`WriteManager` and `SearchManager`) to specific memory domain managers implementing `BaseMemoryManager`.

```mermaid
graph TD
    A["LongTermMemory"] --> B["WriteManager"]
    A --> C["SearchManager"]
    B --> D["FragmentMemoryManager"]
    B --> E["SummaryManager"]
    B --> F["VariableManager"]
    B --> G["MiddleTermMemoryManager"]
    C --> H["BaseMemoryIndex"]
    C --> I["BaseKVStore"]
```
*Sources: `[jiuwen_memory/memory_core/manage/index/write_manager.py:12-26]`, `[jiuwen_memory/memory_core/manage/search/search_manager.py:59-77]()`*

---

## 2. The Write Path (`WriteManager`)

`WriteManager` acts as the entry router for ingesting, modifying, and purging memory units. It inspects memory types, routes payloads to corresponding managers, and handles fallback or cross-tier cleanup between long-term and middle-term memory stores.

### Key Write Operations
* **`add_memories`**: Iterates through registered managers in `self.managers`, invoking their respective batch insertion methods `[jiuwen_memory/memory_core/manage/index/write_manager.py:27-46]()`.
* **`update_mem_by_id`**: Resolves memory type via index lookup (`__get_mem_type_from_index`). If absent from long-term storage, it optionally checks middle-term storage (`_enable_middle_memory`) before delegating to `middle_manager.update` or rejecting `[jiuwen_memory/memory_core/manage/index/write_manager.py:58-106]()`.
* **`delete_mem_by_id`**: Identifies memory type from index or middle-term cache and routes the deletion request to the appropriate manager `[jiuwen_memory/memory_core/manage/index/write_manager.py:108-155]()`.

```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        A["UserMemoryPayload"]
    end
    subgraph "CodeEntitySpace"
        A --> B["LongTermMemory.add_messages"]
        B --> C["WriteManager.add_memories"]
        C --> D["FragmentMemoryManager.add_memories"]
        C --> E["SummaryManager.add_memories"]
        C --> F["VariableManager.add_memories"]
        D --> G["BaseMemoryIndex.add_memories"]
        E --> G
        F --> H["BaseKVStore.set"]
    end
```
*Sources: `[jiuwen_memory/memory_core/manage/index/write_manager.py:27-160]`, `[jiuwen_memory/memory_core/manage/index/variable_manager.py:39-75]()`*

---

## 3. Concrete Memory Managers

### FragmentMemoryManager & SummaryManager
These managers handle unstructured and semi-structured text units (e.g., user profiles, conversational chunks). They interface directly with `BaseMemoryIndex` to persist embedded documents with scalar metadata (`is_important`, `blacklisted`).

### VariableManager
`VariableManager` manages scoped key-value variables (`user_var` and `session_var`) directly inside `BaseKVStore` using prefixed namespace keys separated by `VariableManager.SEPARATOR` (`/`) `[jiuwen_memory/memory_core/manage/index/variable_manager.py:16-34]()`. It supports upsert semantics via `update_user_variable` and prefix-based batch purges via `delete_by_user_id` `[jiuwen_memory/memory_core/manage/index/variable_manager.py:87-132]()`.

### MiddleTermMemoryManager
`MiddleTermMemoryManager` handles middle-term cache persistence and vector storage synchronization (`SemanticStore`). It supports atomic updates by deleting existing vector documents before inserting updated `MiddleTermUnit` instances `[jiuwen_memory/memory_core/manage/index/middle_mem_manager.py:18-95]()`.

*Sources: `[jiuwen_memory/memory_core/manage/index/variable_manager.py:16-145]`, `[jiuwen_memory/memory_core/manage/index/middle_mem_manager.py:18-126]()`*

---

## 4. The Search Path & Ebbinghaus Reinforcement (`SearchManager`)

`SearchManager` coordinates execution across underlying index backends while maintaining background trace logs for the Ebbinghaus forgetting curve reinforcement model (`retrieve_history`).

### Search Data Flow
1. **Parameter Packaging**: Input queries are encapsulated in `SearchParams`, which accept optional `FilterGroup` filters `[jiuwen_memory/memory_core/manage/search/search_manager.py:42-56]()`.
2. **Filter Normalization**: Applies automatic exclusion rules (`ensure_blacklisted_ne`) to filter out forgotten memories unless explicitly overridden by caller DSL conditions `[jiuwen_memory/memory_core/manage/search/search_manager.py:49-56]()`.
3. **Index Execution**: Queries the underlying `BaseMemoryIndex` for top-k semantic matches.
4. **Background Trace Recording**: Fires a non-blocking `asyncio.Task` (`_append_retrieve_history`) protected by a `DistributedLock` to update the FIFO rolling-window retrieve history (`_RETRIEVE_HISTORY_MAX_LEN = 20`) in `BaseKVStore` `[jiuwen_memory/memory_core/manage/search/search_manager.py:84-154]()`.

```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        A["SearchQueryPrompt"]
    end
    subgraph "CodeEntitySpace"
        A --> B["SearchManager.search"]
        B --> C["normalize_filters"]
        C --> D["ensure_blacklisted_ne"]
        D --> E["BaseMemoryIndex.search"]
        E --> F["AsyncioTask._append_retrieve_history"]
        F --> G["DistributedLock"]
        G --> H["BaseKVStore.set"]
    end
```
*Sources: `[jiuwen_memory/memory_core/manage/search/search_manager.py:42-154]`, `[jiuwen_memory/foundation/store/base_memory_index.py:162-186]()`*

---

## 5. Filter DSL Usage

The memory managers rely on a backend-neutral `FilterGroup` and condition DSL defined in the foundation layer (`[jiuwen_memory/foundation/store/filter_dsl.py]()`). 

* **Default-Injected Filters**: By default, `SearchManager` ensures that any search filter without an explicit `blacklisted` condition receives a `NE("blacklisted", True)` predicate injected via `ensure_blacklisted_ne` `[jiuwen_memory/memory_core/manage/search/search_manager.py:49-56]()`.
* **Explicit Overrides**: Callers requiring access to blacklisted or forgotten memories must explicitly supply filter expressions targeting the `blacklisted` field (e.g., `EQ("blacklisted", True)`).

*Sources: `[jiuwen_memory/memory_core/manage/search/search_manager.py:42-56]`, `[jiuwen_memory/foundation/store/base_memory_index.py:162-186]()`*

---

## 6. Summary of Key Classes and Roles

| Class Name | File Path | Primary Role |
| :--- | :--- | :--- |
| `WriteManager` | `jiuwen_memory/memory_core/manage/index/write_manager.py` | Routes add, update, and delete requests across memory managers and index stores. |
| `SearchManager` | `jiuwen_memory/memory_core/manage/search/search_manager.py` | Coordinates search requests, applies filter DSL rules, and logs hit traces for Ebbinghaus forgetting. |
| `VariableManager` | `jiuwen_memory/memory_core/manage/index/variable_manager.py` | Manages user and session key-value variables in `BaseKVStore` with namespaced prefixes. |
| `MiddleTermMemoryManager` | `jiuwen_memory/memory_core/manage/index/middle_mem_manager.py` | Manages middle-term cache units and vector store synchronization. |
| `SearchParams` | `jiuwen_memory/memory_core/manage/search/search_manager.py` | Pydantic data model encapsulating query parameters and custom `FilterGroup` rules. |

*Sources: `[jiuwen_memory/memory_core/manage/index/write_manager.py:12-26]`, `[jiuwen_memory/memory_core/manage/search/search_manager.py:42-77]`, `[jiuwen_memory/memory_core/manage/index/variable_manager.py:16-34]`, `[jiuwen_memory/memory_core/manage/index/middle_mem_manager.py:18-27]()`*

---

# Page: Middle-Term Memory (MemoryTurbo)

# Middle-Term Memory (MemoryTurbo)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/en/API Docs/middle_term_memory.md](docs/en/API Docs/middle_term_memory.md)
- [jiuwen_memory/memory_core/manage/index/middle_mem_manager.py](jiuwen_memory/memory_core/manage/index/middle_mem_manager.py)
- [jiuwen_memory/memory_core/manage/index/write_manager.py](jiuwen_memory/memory_core/manage/index/write_manager.py)
- [jiuwen_memory/memory_core/manage/mem_model/semantic_store.py](jiuwen_memory/memory_core/manage/mem_model/semantic_store.py)
- [tests/unit_tests/core/memory/manage/index/test_middle_mem_manager.py](tests/unit_tests/core/memory/manage/index/test_middle_mem_manager.py)
- [tests/unit_tests/core/memory/manage/mem_model/test_semantic_store.py](tests/unit_tests/core/memory/manage/mem_model/test_semantic_store.py)
- [tests/unit_tests/core/memory/process/forgetting/test_delete_mem_cleanup.py](tests/unit_tests/core/memory/process/forgetting/test_delete_mem_cleanup.py)
- [tests/unit_tests/core/memory/test_long_term_memory_middle_conversion.py](tests/unit_tests/core/memory/test_long_term_memory_middle_conversion.py)
- [tests/unit_tests/core/memory/test_long_term_memory_middle_mutations.py](tests/unit_tests/core/memory/test_long_term_memory_middle_mutations.py)

</details>



## 1. Purpose and Scope

The **Middle-Term Memory** subsystem (internally referred to as **MemoryTurbo**) serves as an intelligent, vector-backed buffer layer situated between real-time session message stores and long-term structured memory (`LongTermMemory`). Its primary objectives are to mitigate token consumption and API call frequencies by accumulating conversation fragments, performing **conversation continuity detection**, and executing asynchronous batch promotions (`middle_mem_to_long`) into long-term memory.

Sources: `jiuwen_memory/memory_core/manage/index/middle_mem_manager.py:18-27`(), `docs/en/API Docs/middle_term_memory.md:3-10`()

---

## 2. Core Components and Classes

### MiddleTermMemoryManager

`MiddleTermMemoryManager` manages middle-term memory CRUD operations, coordinating with `SemanticStore` for vector indexing and applying encryption where configured.

* **Class Definition**: Defined in `jiuwen_memory/memory_core/manage/index/middle_mem_manager.py` [jiuwen_memory/memory_core/manage/index/middle_mem_manager.py:18-27]().
* **Key Methods**:
  * `add_memories(...)`: Filters incoming memory units matching `MemoryType.MIDDLE_TERM_MEMORY.value`, validating and forwarding them to vector storage via `_add_middle_term_memories_to_vector` [jiuwen_memory/memory_core/manage/index/middle_mem_manager.py:28-63]().
  * `update(...)`: Replaces an existing middle-term memory vector document by deleting the old entry and inserting an updated `MiddleTermUnit` [jiuwen_memory/memory_core/manage/index/middle_mem_manager.py:65-94]().
  * `delete(...)` / `delete_by_user_id(...)`: Removes individual entries or clears entire scope/user vector tables [jiuwen_memory/memory_core/manage/index/middle_mem_manager.py:96-114]().
  * `search(...)`: Performs vector similarity recall to find relevant middle-term units [jiuwen_memory/memory_core/manage/index/middle_mem_manager.py:120-125]().

Sources: `jiuwen_memory/memory_core/manage/index/middle_mem_manager.py:18-126`()

### SemanticStore

`SemanticStore` abstracts vector store operations, embedding text payloads, managing dynamic collection creation, and applying schema versions.

* **Class Definition**: Defined in `jiuwen_memory/memory_core/manage/mem_model/semantic_store.py` [jiuwen_memory/memory_core/manage/mem_model/semantic_store.py:20-28]().
* **Key Methods**:
  * `initialize_embedding_model(...)`: Binds or updates the active text embedding model [jiuwen_memory/memory_core/manage/mem_model/semantic_store.py:43-50]().
  * `_create_collection_if_not_exists(...)`: Initializes vector collections with primary `id`, `embedding`, `content`, and `timestamp` fields if absent [jiuwen_memory/memory_core/manage/mem_model/semantic_store.py:52-106]().
  * `add_docs(...)`: Computes document embeddings and writes batch structured records to the underlying vector store [jiuwen_memory/memory_core/manage/mem_model/semantic_store.py:107-166]().

Sources: `jiuwen_memory/memory_core/manage/mem_model/semantic_store.py:20-166`()

---

## 3. Data Flow & Write/Search Architecture

When writing or searching memories, `WriteManager` coordinates interactions across long-term and middle-term indices. If a target memory ID is absent from long-term indices, `WriteManager` falls back to verify and modify middle-term units through `MiddleTermMemoryManager` [jiuwen_memory/memory_core/manage/index/write_manager.py:48-156]().

```mermaid
graph TD
    A["Client Request"] --> B["WriteManager.update_mem_by_id"]
    B --> C{"Check Long-Term Index"}
    C -->|Found| D["LongTermManager.update"]
    C -->|NotFound| E{"enable_middle_memory?"}
    E -->|Yes| F["MiddleTermMemoryManager.update"]
    E -->|No| G["Return False / Warning"]
    F --> H["SemanticStore.delete_docs & add_docs"]

    Sources: "jiuwen_memory/memory_core/manage/index/write_manager.py:48-106", "jiuwen_memory/memory_core/manage/index/middle_mem_manager.py:65-94"
```

Sources: `jiuwen_memory/memory_core/manage/index/write_manager.py:48-106`(), `jiuwen_memory/memory_core/manage/index/middle_mem_manager.py:65-94`()

---

## 4. Promotion Loop (`middle_mem_to_long`)

The background promotion loop (`middle_mem_to_long`) periodically scans stored dialogue messages, evaluates conversation boundaries, and batches multi-turn dialogues for long-term extraction.

```mermaid
graph TD
    A["LongTermMemory Background Task"] -->|Interval Timer| B["middle_mem_to_long"]
    B --> C["MessageManager.get"]
    C --> D{"Dialogue Count > 1?"}
    D -->|Yes| E["check_dialogue_continuity"]
    E -->|Continuous| F["Merge Dialogue Batch"]
    D -->|No or Topic Shift| G["Process Single/Independent Batch"]
    F --> H["_process_dialogue_batch_to_long_term_safe"]
    G --> H
    H --> I["Batch Delete Middle Memories & Messages"]

    Sources: "tests/unit_tests/core/memory/test_long_term_memory_middle_conversion.py:84-156"
```

* **Continuity Analysis**: `check_dialogue_continuity` evaluates whether adjacent dialogue messages belong to an ongoing topic or a new session boundary [tests/unit_tests/core/memory/test_long_term_memory_middle_conversion.py:117-156]().
* **Batch Conversion**: Messages retain their exact roles (`UserMessage`, `AssistantMessage`) rather than relying on content prefix heuristics during conversion [tests/unit_tests/core/memory/test_long_term_memory_middle_conversion.py:47-81]().

Sources: `tests/unit_tests/core/memory/test_long_term_memory_middle_conversion.py:47-156`()

---

## 5. Conversion and Unit Testing

Middle-term memory logic and its conversion pathways are validated through dedicated unit suites:
* `test_process_dialogue_batch_converts_messages_by_role_not_content`: Confirms role preservation during batch conversion [tests/unit_tests/core/memory/test_long_term_memory_middle_conversion.py:47-81]().
* `test_middle_mem_to_long_keeps_dialogue_object_and_skips_initial_continuity_check`: Validates single-item and continuity execution flows [tests/unit_tests/core/memory/test_long_term_memory_middle_conversion.py:84-115]().
* `test_add_middle_term_memory_success`: Tests payload structural mapping and vector store dispatching inside `MiddleTermMemoryManager` [tests/unit_tests/core/memory/manage/index/test_middle_mem_manager.py:14-65]().

Sources: `tests/unit_tests/core/memory/test_long_term_memory_middle_conversion.py:47-156`(), `tests/unit_tests/core/memory/manage/index/test_middle_mem_manager.py:14-65`()

---

# Page: Extraction and Generation Pipeline

# Extraction and Generation Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jiuwen_memory/memory_core/config/config.py](jiuwen_memory/memory_core/config/config.py)
- [jiuwen_memory/memory_core/manage/mem_model/memory_unit.py](jiuwen_memory/memory_core/manage/mem_model/memory_unit.py)
- [jiuwen_memory/memory_core/process/dreaming/store.py](jiuwen_memory/memory_core/process/dreaming/store.py)
- [jiuwen_memory/memory_core/process/dreaming/sweeper.py](jiuwen_memory/memory_core/process/dreaming/sweeper.py)
- [jiuwen_memory/memory_core/process/extract/generation.py](jiuwen_memory/memory_core/process/extract/generation.py)
- [tests/unit_tests/core/memory/test_add_messages_result_and_proactive_memory.py](tests/unit_tests/core/memory/test_add_messages_result_and_proactive_memory.py)

</details>



## Purpose and Scope
This page details the implementation of the memory extraction and generation pipeline in `jiuwen_memory.memory_core`. The pipeline processes incoming dialogue messages, analyzes conversation content for summary and variables, extracts long-term memory fragments (`user_profile`, `semantic_memory`, `episodic_memory`), and routes them through update verification strategies (`MemUpdateChecker`) to perform `ADD`, `UPDATE`, or `DELETE` operations on persistent memory stores.

Sources: [jiuwen_memory/memory_core/process/extract/generation.py:1-481](), [jiuwen_memory/memory_core/manage/mem_model/memory_unit.py:1-68]()

---

## 1. Memory Analyzer and Variable Extraction (`MemoryAnalyzer`)
The `MemoryAnalyzer` inspects conversational history and incoming messages to determine if key information is present, extracts runtime variables, and generates conversation summaries.

- **`MemoryAnalyzer.analyze()`**: Coordinates LLM-based analysis using schema prompts to return a structured evaluation containing `has_key_information`, `variables`, and `summary`.
- **Variable Extraction**: Captures key-value pairs (`VariableResult`) from user input, filtering out forbidden variables defined in `MemoryEngineConfig.forbidden_variables`.
- **Summary Generation**: Produces a concise summary of the dialogue turn bounded by `summary_max_token`.

```mermaid
graph TD
    Input["InputMessages"] --> Analyzer["MemoryAnalyzer.analyze()"]
    Analyzer --> LLM["BaseChatModelInvocation"]
    LLM --> Parse["JsonOutputParser"]
    Parse --> Res["MemoryAnalyzeResult"]
    Res --> Var["VariableResults"]
    Res --> Sum["SummaryUnit"]

    sub5["Code Entity Space"]
    Analyzer --- code1["jiuwen_memory.memory_core.process.extract.memory_analyzer.MemoryAnalyzer"]
    Parse --- code2["jiuwen_memory.foundation.llm.JsonOutputParser"]
```
*Figure 1: Memory Analyzer Workflow bridging natural language ingestion to structured memory outputs.*

Sources: [jiuwen_memory/memory_core/process/extract/generation.py:65-73]()

---

## 2. Long-Term Memory Extractor (`LongTermMemoryExtractor`)
When key information is detected by the analyzer, `LongTermMemoryExtractor` processes the dialogue to extract granular long-term memory categories.

- **Categories Extracted**:
  - `user_profile`: Facts regarding user identity, preferences, relationships, and asset status.
  - `semantic_memory`: Time-independent factual statements or concepts.
  - `episodic_memory`: Time-dependent episodic events or occurrences.
- **Explicit Instructions**: Detects explicit user instructions (`instruct_memories`) requiring immediate procedural updates.
- **Configurable Definitions**: Customizes extraction behavior using scope-specific settings defined in `MemoryScopeConfig` (e.g., `user_profile_definition`, `semantic_memory_definition`, `episodic_memory_definition`).

Sources: [jiuwen_memory/memory_core/config/config.py:49-68](), [jiuwen_memory/memory_core/process/extract/long_term_memory_extractor.py:1-123]()

---

## 3. Generation Coordinator (`Generator`)
The `Generator` class orchestrates the complete extraction workflow. Its primary entry point, `Generator.gen_all_memory()`, coordinates analyzer and extractor tasks.

```mermaid
graph TD
    Start["gen_all_memory()"] --> Analyze["MemoryAnalyzer.analyze()"]
    Analyze --> ProcessVars["_process_extracted_data()"]
    ProcessVars --> CheckLongTerm["Config.enable_long_term_mem"]
    CheckLongTerm -->|Enabled| CheckSummary["Config.enable_summary_memory"]
    CheckSummary --> SummaryStep["_process_summary_data()"]
    CheckLongTerm -->|HasKeyInfo| ExtractFragments["_categories_to_memory_unit()"]
    ExtractFragments --> MergeUnits["FragmentEnable Filtering"]
    MergeUnits --> ReturnDict["Return Dict of Memory Units"]

    subgraph "Code Entity Space"
    Start --- codeGen["jiuwen_memory.memory_core.process.extract.generation.Generator.gen_all_memory"]
    Analyze --- codeAn["jiuwen_memory.memory_core.process.extract.memory_analyzer.MemoryAnalyzer.analyze"]
    ExtractFragments --- codeEx["LongTermMemoryExtractor"]
    end
```
*Figure 2: Generator pipeline sequence and method execution flow.*

- **Parameters Required**: `messages`, `config`, `user_id`, `scope_id`, and `base_chat_model` [jiuwen_memory/memory_core/process/extract/generation.py:33-54]().
- **Error Handling**: Catches `AttributeError`, `ValueError`, and general exceptions during conflict resolution, logging failures via `memory_logger` without failing the entire message ingestion flow [jiuwen_memory/memory_core/process/extract/generation.py:120-146]().

Sources: [jiuwen_memory/memory_core/process/extract/generation.py:33-160]()

---

## 4. Prompt Management and Templating (`PromptApplier`)
The extraction and generation pipeline relies on template-driven prompts managed by `PromptApplier`.

- **Template Resolution**: Fetches base system prompts and injects dynamic context placeholders (e.g., dialogue history, token budgets, custom domain definitions from `MemoryScopeConfig`).
- **JSON Parsing**: Integrates with `JsonOutputParser` to ensure LLM responses conform to expected dictionary or list schemas before unit instantiation.

Sources: [jiuwen_memory/memory_core/prompts/prompt_applier.py:1-100](), [jiuwen_memory/memory_core/process/dreaming/sweeper.py:103-157]()

---

## 5. Memory Update Checker and ADD/UPDATE/DELETE Strategy (`MemUpdateChecker`)
Extracted memory units undergo conflict resolution and deduplication via the memory update checking mechanism before being committed to storage.

- **Operation Types (`OperationType`)**:
  - `ADD`: Inserts a brand new memory unit when no overlapping semantic matches exist.
  - `UPDATE`: Modifies an existing memory unit if new information refines or supersedes previous records.
  - `DELETE`: Removes obsolete or explicitly contradicted memory units.
- **Conflict Validation**: Evaluates incoming fragment memory units against existing vector index entries to maintain coherence and prevent redundancy.

Sources: [jiuwen_memory/memory_core/manage/mem_model/memory_unit.py:19-23](), [tests/unit_tests/core/memory/test_add_messages_result_and_proactive_memory.py:1-200]()

---

# Page: Dreaming and Ebbinghaus Forgetting

# Dreaming and Ebbinghaus Forgetting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jiuwen_memory/memory_core/long_term_memory.py](jiuwen_memory/memory_core/long_term_memory.py)
- [jiuwen_memory/server/memory_server.py](jiuwen_memory/server/memory_server.py)
- [tests/unit_tests/core/memory/process/dreaming/test_source.py](tests/unit_tests/core/memory/process/dreaming/test_source.py)
- [tests/unit_tests/core/memory/process/dreaming/test_start_stop_dreaming.py](tests/unit_tests/core/memory/process/dreaming/test_start_stop_dreaming.py)
- [tests/unit_tests/core/memory/process/dreaming/test_store.py](tests/unit_tests/core/memory/process/dreaming/test_store.py)
- [tests/unit_tests/core/memory/process/dreaming/test_sweeper.py](tests/unit_tests/core/memory/process/dreaming/test_sweeper.py)

</details>



## Purpose and Scope
This section covers the background memory consolidation subsystem (Dreaming) and the Ebbinghaus forgetting mechanism in the `jiuwen_memory` engine. The dreaming engine asynchronously extracts higher-level semantic and episodic knowledge from conversation message logs and promotes them into long-term storage. The Ebbinghaus forgetting subsystem computes memory decay and reinforcement based on retrieval history, applying decay evaluations, pruning, and blacklisting to keep the memory space relevant and bounded.

Sources:
- [jiuwen_memory/memory_core/long_term_memory.py:25-34]()

---

## Dreaming Subsystem Architecture

The dreaming pipeline mimics human memory consolidation during sleep. It reads unprocessed session logs from message stores, compresses dialogue events, prompts an LLM to extract durable knowledge items, and writes them back through the write manager.

The subsystem consists of four core components:
1. `DreamingOrchestrator`: Coordinates background looping, lifecycle startup, and shutdown per user/scope `[tests/unit_tests/core/memory/process/dreaming/test_start_stop_dreaming.py:28-36]()`.
2. `MessageStoreSessionSource`: Fetches conversation sessions from `BaseMessageStore` matching minimum round thresholds and filtering out already-scanned sessions `[tests/unit_tests/core/memory/process/dreaming/test_source.py:44-56]()`.
3. `Sweeper`: Manages token compression (`_compress`), LLM extraction invocation, session checkpoint persistence, and error isolation `[tests/unit_tests/core/memory/process/dreaming/test_sweeper.py:75-94]()`.
4. `MemoryUnitKnowledgeStore`: Validates and groups extracted knowledge items, acquiring user-level distributed locks (`_lock/user/{user_id}`) before invoking `WriteManager.add_memories()` `[tests/unit_tests/core/memory/process/dreaming/test_store.py:49-70]()`.

```mermaid
graph TD
    subgraph "Code Entity Space"
        A["MessageStoreSessionSource"] -->|"iter_new_sessions()"| B["Sweeper"]
        B -->|"_compress()"| C["LLM"]
        C -->|"extraction JSON"| B
        B -->|"promote()"| D["MemoryUnitKnowledgeStore"]
        D -->|"exclusive_set()"| E["BaseKVStore"]
        D -->|"add_memories()"| F["WriteManager"]
    end
```

Sources:
- [jiuwen_memory/memory_core/long_term_memory.py:25-30]()
- [tests/unit_tests/core/memory/process/dreaming/test_store.py:49-121]()
- [tests/unit_tests/core/memory/process/dreaming/test_source.py:44-67]()
- [tests/unit_tests/core/memory/process/dreaming/test_sweeper.py:75-94]()

---

## Checkpointing and Concurrency Control

To guarantee idempotency across dreaming sweeps, the `Sweeper` maintains scanned session checkpoints in the key-value store under the prefix key `dreaming/checkpoint/{scope_id}/{user_id}` [tests/unit_tests/core/memory/process/dreaming/test_sweeper.py:91-93](). 

If an extraction or promotion fails for a specific session, its state is not written to the checkpoint, allowing subsequent sweeps to retry safely [tests/unit_tests/core/memory/process/dreaming/test_sweeper.py:124-163](). Concurrency across multiple workers or simultaneous writes is governed by `DistributedLock` utilizing `BaseKVStore.exclusive_set()` with automatic cleanup via `delete()` [tests/unit_tests/core/memory/process/dreaming/test_store.py:111-120]().

```mermaid
graph TD
    subgraph "Code Entity Space"
        OS["DreamingOrchestrator"] --> SW["Sweeper.run_sweep()"]
        SW --> KV["BaseKVStore.get(dreaming/checkpoint/scope/user)"]
        SW --> SRC["MessageStoreSessionSource.iter_new_sessions()"]
        SW --> ST["MemoryUnitKnowledgeStore.promote()"]
        ST --> LK["BaseKVStore.exclusive_set(_lock/user/id)"]
        ST --> WM["WriteManager.add_memories()"]
        SW --> CK["BaseKVStore.set(dreaming/checkpoint/scope/user)"]
    end
```

Sources:
- [tests/unit_tests/core/memory/process/dreaming/test_store.py:111-120]()
- [tests/unit_tests/core/memory/process/dreaming/test_sweeper.py:91-148]()

---

## Ebbinghaus Forgetting and Evaluator

Memory units degrade over time following the Ebbinghaus forgetting curve. The subsystem relies on `EbbinghausEvaluator` and `ForgetContext` [jiuwen_memory/memory_core/long_term_memory.py:31-34]().

Retrieval events are logged into a FIFO rolling window (`RETRIEVE_HISTORY_PREFIX`, bounded by `_RETRIEVE_HISTORY_MAX_LEN = 20`) stored inside the KV backend [jiuwen_memory/memory_core/long_term_memory.py:74-88](). The recency reinforcement term computes decay based on access frequency and time deltas, ensuring frequently or recently accessed memories resist pruning.

```mermaid
graph TD
    subgraph "Code Entity Space"
        SM["SearchManager"] -->|"_append_retrieve_history()"| KV["BaseKVStore"]
        EE["EbbinghausEvaluator"] -->|"evaluate()"| FC["ForgetContext"]
        FC -->|"retrieve_history"| KV
        EE -->|"compute score"| PR["Pruning / Decay Decision"]
    end
```

Sources:
- [jiuwen_memory/memory_core/long_term_memory.py:31-34]()
- [jiuwen_memory/memory_core/long_term_memory.py:74-89]()

---

## Blacklisting and Recall

When memories drop below the retention threshold determined by the `EbbinghausEvaluator`, or are explicitly deleted via public APIs, they enter a blacklisted state. Blacklisting prevents pruned or deleted memory IDs from resurfacing during vector similarity searches or keyword retrievals. The underlying KV records and retrieve history (`retrieve_history{SEP}{user_id}{SEP}{scope_id}{SEP}{mem_id}`) are cleaned up during batch maintenance operations [jiuwen_memory/memory_core/long_term_memory.py:74-80]().

Sources:
- [jiuwen_memory/memory_core/long_term_memory.py:74-81]()

---

# Page: Graph Memory

# Graph Memory

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/en/API Docs/config.md](docs/en/API Docs/config.md)
- [docs/en/API Docs/graph_memory.md](docs/en/API Docs/graph_memory.md)
- [jiuwen_memory/foundation/store/graph/milvus/milvus_support.py](jiuwen_memory/foundation/store/graph/milvus/milvus_support.py)
- [tests/unit_tests/core/memory/graph/graph_memory/test_base.py](tests/unit_tests/core/memory/graph/graph_memory/test_base.py)

</details>



## Purpose and Scope

The **Graph Memory** subsystem (`jiuwen_memory.memory_core.graph` and `jiuwen_memory.foundation.store.graph`) provides relational memory capabilities for AI agents. Unlike flat text or vector stores, Graph Memory extracts structured entities, inter-entity relations, and source episodes from raw text or multi-turn conversations, storing them in a graph database backend with hybrid search support.

Scope includes:
- Graph data structures (`Entity`, `Relation`, `Episode`).
- LLM-powered extraction and state merging pipelines via `GraphMemory`.
- Graph storage backends (`MilvusGraphStore`).
- Hybrid retrieval strategies and cross-encoder re-ranking.

Sources: `[docs/en/API Docs/graph_memory.md:1-128]()`, `[jiuwen_memory/foundation/store/graph/milvus/milvus_support.py:1-65]()`

---

## Core Data Models and Architecture

Graph Memory organizes information into three primary graph objects defined in `jiuwen_memory.foundation.store.graph.graph_object`:

- `Entity`: Represents a distinct entity node (e.g., person, organization, concept). Contains fields like `name`, `content`, `attributes`, and linked episode references `[tests/unit_tests/core/memory/graph/graph_memory/test_base.py:19-23]()`.
- `Relation`: Represents a directed edge between two entities (`lhs` and `rhs`). Contains `name`, `content`, and temporal bounds (`valid_since`, `valid_until`) `[tests/unit_tests/core/memory/graph/graph_memory/test_base.py:19-23]()`.
- `Episode`: Represents the raw ingestion unit (conversation turn, document, or JSON string) that serves as the provenance evidence for extracted entities and relations `[tests/unit_tests/core/memory/graph/graph_memory/test_base.py:19-23]()`.

The following diagram bridges the **Natural Language Space** (unstructured conversations and documents) to the **Code Entity Space** (`GraphMemory`, `MilvusGraphStore`, and collection classes).

```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        NL_Text[""RawUserConversationOrDocument""]
    end

    subgraph "CodeEntitySpace"
        GM[""GraphMemory (jiuwen_memory.memory_core.graph.graph_memory.base)""]
        Store[""MilvusGraphStore (jiuwen_memory.foundation.store.graph.milvus.milvus_support)""]
        
        EntityObj[""Entity (jiuwen_memory.foundation.store.graph.graph_object)""]
        RelationObj[""Relation (jiuwen_memory.foundation.store.graph.graph_object)""]
        EpisodeObj[""Episode (jiuwen_memory.foundation.store.graph.graph_object)""]

        GM -->|"extracts"| EntityObj
        GM -->|"extracts"| RelationObj
        GM -->|"wraps"| EpisodeObj
        
        EntityObj -->|"persistsTo"| Store
        RelationObj -->|"persistsTo"| Store
        EpisodeObj -->|"persistsTo"| Store
    end

    NL_Text -->|"input to add_memory()"| GM
```
Sources: `[docs/en/API Docs/graph_memory.md:16-30](), [tests/unit_tests/core/memory/graph/graph_memory/test_base.py:19-23](), [jiuwen_memory/foundation/store/graph/milvus/milvus_support.py:34-65]()`

---

## Extraction and Update Pipeline

The ingestion pipeline is controlled by the `GraphMemory` class. When `add_memory()` is called, the input text undergoes LLM-driven parsing according to an `AddMemStrategy` (which specifies prompt language, entity types, and extraction depth) `[docs/en/API Docs/graph_memory.md:86-90]()`.

The pipeline executes the following stages:
1. **Episode Creation**: The input source is wrapped into an `Episode` object.
2. **Entity & Relation Extraction**: The LLM parses text into structured declarations (`EntityDeclaration`) and relations.
3. **Merging & Deduplication**: Newly extracted nodes and edges are merged against existing graph entries to prevent duplication and resolve aliases.
4. **State Commit**: Changes are committed to the underlying graph store, returning a `GraphMemUpdate` structure containing added, updated, or removed objects `[docs/en/API Docs/graph_memory.md:24-30]()`.

```mermaid
graph TD
    subgraph "CodeExecutionFlow"
        Input[""GraphMemory.add_memory(src_type, user_id, content)""] --> Strategy[""AddMemStrategy & LLM Extraction""]
        Strategy --> Parse[""EntityDeclaration & Relation Parsing""]
        Parse --> Merge[""Entity Merge & Deduplication""]
        Merge --> Commit[""MilvusGraphStore Commit Operations""]
        Commit --> Update[""GraphMemUpdate (added/updated entities, relations, episodes)""]
    end
```
Sources: `[docs/en/API Docs/graph_memory.md:86-104](), [tests/unit_tests/core/memory/graph/graph_memory/test_base.py:28-32]()`

---

## Graph Store Subsystem

Graph persistence is abstracted via the `GraphStore` interface, with `MilvusGraphStore` serving as the primary reference implementation (`[jiuwen_memory/foundation/store/graph/milvus/milvus_support.py:34-38]()`).

### Database Initialization and Collections
`MilvusGraphStore` manages three independent collections corresponding to the core data models, mapped via `ENTITY_COLLECTION`, `RELATION_COLLECTION`, and `EPISODE_COLLECTION` `[jiuwen_memory/foundation/store/graph/milvus/milvus_support.py:59-64]`:

- **Connection Setup**: Establishes a connection using `MilvusClient` based on `GraphConfig` parameters (`uri`, `token`, `timeout`, and custom extras) `[jiuwen_memory/foundation/store/graph/milvus/milvus_support.py:40-53]()`.
- **Embedder Attachment**: Embeddings are required for vector similarity search across graph nodes. The `attach_embedder()` method verifies that the embedding dimension matches `GraphConfig.embed_dim` before binding `[jiuwen_memory/foundation/store/graph/milvus/milvus_support.py:117-134]()`.

Sources: `[jiuwen_memory/foundation/store/graph/milvus/milvus_support.py:34-147]()`

---

## Retrieval and Search Engine

Graph Memory supports hybrid search (combining dense vector search, sparse full-text BM25 search, and graph traversal) via the `search()` API on `GraphMemory` `[docs/en/API Docs/graph_memory.md:93-100]()`.

Key components of retrieval:
- **Search Strategies**: Configured via `SearchConfig` and registered with `register_search_strategy()`, allowing customized ranking weights (`WeightedRankConfig`) for entities, relations, and episodes.
- **Cross-Encoder Re-ranking**: When a `Reranker` instance is attached via `attach_reranker()`, retrieved candidate pools are re-scored using cross-encoder models to improve relevance before results are returned to the caller `[tests/unit_tests/core/memory/graph/graph_memory/test_base.py:130-151](), [jiuwen_memory/foundation/store/graph/milvus/milvus_support.py:86-102]()`.

Sources: `[docs/en/API Docs/graph_memory.md:151-166](), [tests/unit_tests/core/memory/graph/graph_memory/test_base.py:130-151](), [jiuwen_memory/foundation/store/graph/milvus/milvus_support.py:86-102]()`

---

# Page: Memory Metadata and Migrations

# Memory Metadata and Migrations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jiuwen_memory/memory_core/manage/mem_meta/manager.py](jiuwen_memory/memory_core/manage/mem_meta/manager.py)
- [jiuwen_memory/server/mem_meta_api.py](jiuwen_memory/server/mem_meta_api.py)
- [tests/unit_tests/core/memory/migration/migrator/test_index_migration_integration.py](tests/unit_tests/core/memory/migration/migrator/test_index_migration_integration.py)
- [tests/unit_tests/core/memory/migration/migrator/test_memory_meta_manager.py](tests/unit_tests/core/memory/migration/migrator/test_memory_meta_manager.py)
- [tests/unit_tests/core/memory/migration/test_run_migrations.py](tests/unit_tests/core/memory/migration/test_run_migrations.py)

</details>



## Purpose and Scope
This page details the metadata management subsystems, user statistics tracking, and schema migration engines within `agent-memory`. It covers the `MemMetaManager` for administrative cleanup and statistics, the associated database schemas (`av_user_stats` and `mem_meta_task`), the `MemoryMetaManager` for version tracking, and the modular KV, SQL, and vector index migration framework.

---

## 1. MemMeta Manager & Admin API

The `MemMetaManager` (`jiuwen_memory/memory_core/manage/mem_meta/manager.py`) coordinates asynchronous metadata refreshing, user memory expiration analysis, and batch deletion workflows. It is exposed via FastAPI administration endpoints in `jiuwen_memory/server/mem_meta_api.py`.

### Endpoints and Routing
- `POST /admin/mem_meta/refresh`: Submits an asynchronous task to scan collection stores and rebuild user statistics in `av_user_stats`. Supports a `force` flag to bypass cooldown periods [jiuwen_memory/server/mem_meta_api.py:35-40]().
- `POST /admin/mem_meta/expired_memorys`: Synchronously queries top inactive users exceeding an inactivity threshold [jiuwen_memory/server/mem_meta_api.py:42-49]().
- `POST /admin/mem_meta/batch_delete`: Executes or dry-runs batch deletions for expired or specified user scopes [jiuwen_memory/server/mem_meta_api.py:51-62]().
- `GET /admin/mem_meta/task_status`: Queries execution status and metrics for background tasks [jiuwen_memory/server/mem_meta_api.py:146-155]().

```mermaid
graph TD
    Client["ClientRequest"] --> API["router (/admin/mem_meta)"]
    API -->|"/refresh"| M1["MemMetaManager.submit_refresh"]
    API -->|"/expired_memorys"| M2["MemMetaManager.get_expired_memorys"]
    API -->|"/batch_delete"| M3["MemMetaManager.submit_batch_delete"]
    API -->|"/task_status"| M4["MemMetaManager.get_task_status"]
    M1 --> DB["BaseDbStore / AsyncEngine"]
    M2 --> DB
    M3 --> DB
    M4 --> DB

    sub: "Sources: jiuwen_memory/server/mem_meta_api.py:68-155, jiuwen_memory/memory_core/manage/mem_meta/manager.py:117-201"
```

Sources: `jiuwen_memory/server/mem_meta_api.py:68-155()`, `jiuwen_memory/memory_core/manage/mem_meta/manager.py:117-201()`

---

## 2. Metadata and Stats Schemas

The metadata persistence layer utilizes SQLAlchemy `MetaData` to manage two core relational tables across SQLite, GaussDB, and PostgreSQL backends via `BaseDbStore`.

### `av_user_stats` Table
Tracks aggregated metrics per scope-user combination:
- `scope_user`: `String(255)`, Primary Key.
- `total_count`, `active_count`, `superseded_count`: `Integer` counters for document states.
- `expired_30d_count`, `expired_all_count`: `Integer` counters tracking blacklisted and aged records.
- `tier_episodic`, `tier_semantic`, `tier_other`: `Integer` counts categorized by memory tier.
- `created_at`, `updated_at`: `String(32)` local timestamp strings [jiuwen_memory/memory_core/manage/mem_meta/manager.py:78-91]().

### `mem_meta_task` Table
Tracks asynchronous background task execution states:
- `task_id`: `String(64)`, Primary Key.
- `task_type`: `String(32)` (e.g., `refresh`, `batch_delete`).
- `status`: `String(32)` (`pending`, `running`, `completed`, `failed`).
- `request_params`, `result_summary`, `error_message`: `Text` payloads storing JSON-serialized execution metadata.
- Progress counters: `total_users`, `processed_users`, `deleted_count`, `failed_count`.
- Indexes: `idx_task_status` on `status`, `idx_task_type_created` on `task_type` [jiuwen_memory/memory_core/manage/mem_meta/manager.py:93-111]().

Sources: `jiuwen_memory/memory_core/manage/mem_meta/manager.py:78-111()`

---

## 3. Memory Meta Version Manager (`MemoryMetaManager`)

Distinct from the administrative `MemMetaManager`, the core migration subsystem utilizes `MemoryMetaManager` (`jiuwen_memory/memory_core/migration/migrator/memory_meta_manager.py`) to track schema versions for relational tables using `SqlDbStore` [tests/unit_tests/core/memory/migration/migrator/test_memory_meta_manager.py:8-23]().

- **Schema Tracking**: Maintains the `memory_meta` table mapping `table_name` to `schema_version`.
- **Atomic Upserts**: Employs `SqlDbStore.insert_or_update` to record or increment version definitions without incurring race conditions [tests/unit_tests/core/memory/migration/migrator/test_memory_meta_manager.py:26-60]().

```mermaid
graph TD
    Caller["MigrationRunner"] --> MM["MemoryMetaManager.add"]
    MM --> Check["Validate table_name and schema_version"]
    Check -->|Valid| DB["SqlDbStore.insert_or_update"]
    DB --> Table["memory_meta table"]

    sub: "Sources: jiuwen_memory/memory_core/migration/migrator/memory_meta_manager.py, tests/unit_tests/core/memory/migration/migrator/test_memory_meta_manager.py:26-60"
```

Sources: `jiuwen_memory/memory_core/migration/migrator/memory_meta_manager.py()`, `tests/unit_tests/core/memory/migration/migrator/test_memory_meta_manager.py:26-60()`

---

## 4. KV, SQL, and Index Schema Migrations

The engine provides dedicated migration pipelines for Key-Value stores (`run_kv_migrations`), relational databases (`run_sql_migrations`), and vector index collections (`run_vector_migrations`) [tests/unit_tests/core/memory/migration/test_run_migrations.py:21-25]().

### Registries and Operations
- **Registries**: Operations are organized via global registries (`kv_registry`, `sql_registry`, `vector_registry`) [tests/unit_tests/core/memory/migration/test_run_migrations.py:14]().
- **Operations**: Includes structural changes such as `AddColumnOperation`, `RenameScalarFieldOperation`, `UpdateKVOperation`, `RenameMemoryDocFieldOperation`, and `TransformMemoryDocFieldOperation` [tests/unit_tests/core/memory/migration/test_run_migrations.py:16-20](), [tests/unit_tests/core/memory/migration/migrator/test_index_migration_integration.py:15-19]().

```mermaid
graph TD
    Start["Migration Execution Trigger"] --> Router{"Target Store Type"}
    Router -->|KV Store| KV["run_kv_migrations"]
    Router -->|SQL Store| SQL["run_sql_migrations"]
    Router -->|Vector Store| Vec["run_vector_migrations"]

    KV --> RegKV["kv_registry"]
    SQL --> RegSQL["sql_registry"]
    Vec --> RegVec["vector_registry"]

    RegKV --> Op1["UpdateKVOperation"]
    RegSQL --> Op2["AddColumnOperation"]
    RegVec --> Op3["RenameMemoryDocFieldOperation"]

    sub: "Sources: tests/unit_tests/core/memory/migration/test_run_migrations.py:21-25, jiuwen_memory/memory_core/migration/operation/operations.py"
```

Sources: `tests/unit_tests/core/memory/migration/test_run_migrations.py:21-25()`, `tests/unit_tests/core/memory/migration/migrator/test_index_migration_integration.py:15-19()`

---

# Page: Foundation Layer

# Foundation Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jiuwen_memory/foundation/store/index/simple_memory_index.py](jiuwen_memory/foundation/store/index/simple_memory_index.py)
- [jiuwen_memory/foundation/store/kv/db_based_kv_store.py](jiuwen_memory/foundation/store/kv/db_based_kv_store.py)
- [jiuwen_memory/memory_core/manage/index/fragment_memory_manager.py](jiuwen_memory/memory_core/manage/index/fragment_memory_manager.py)
- [jiuwen_memory/memory_core/manage/index/summary_manager.py](jiuwen_memory/memory_core/manage/index/summary_manager.py)
- [jiuwen_memory/memory_core/manage/mem_model/sql_message_store.py](jiuwen_memory/memory_core/manage/mem_model/sql_message_store.py)

</details>



The Foundation Layer provides unified data access, storage abstraction, cryptographic security, and model invocation interfaces for the `jiuwen_memory` engine. It decouples high-level memory managers from concrete physical storage backends (such as KV databases, vector engines, and relational SQL stores) and abstracts AI model providers through pluggable clients.

Sources: `jiuwen_memory/foundation/store/index/simple_memory_index.py:1-40` [], `jiuwen_memory/foundation/store/kv/db_based_kv_store.py:1-55` []

---

## Storage Abstractions and Index Backends

### Memory Index Backends
The index layer defines the `BaseMemoryIndex` contract for compound memory storage operations. Legacy architectures are supported via `SimpleMemoryIndex`, which coordinates `BaseKVStore` and `BaseVectorStore` instances for hybrid retrieval. For details, see [Memory Index Backends](#3.1).

Sources: `jiuwen_memory/foundation/store/index/simple_memory_index.py:40-69` []

### Vector Stores
Vector retrieval is abstracted through `BaseVectorStore`, offering uniform collection management and similarity search capabilities across physical backends including Milvus, Chroma, Elasticsearch, and GaussDB. For details, see [Vector Stores](#3.2).

Sources: `jiuwen_memory/foundation/store/index/simple_memory_index.py:31-36` []

### KV, DB and Message Stores
Persistence of raw metadata, state flags, and conversational logs is managed by components such as `DbBasedKVStore` (backed by SQLAlchemy engines supporting SQLite, MySQL, and GaussDB) and `SqlMessageStore`. For details, see [KV, DB and Message Stores](#3.3).

Sources: `jiuwen_memory/foundation/store/kv/db_based_kv_store.py:51-62` [], `jiuwen_memory/memory_core/manage/mem_model/sql_message_store.py:25-53` []

### Filter DSL
Complex conditional queries are decoupled from database dialects using the `FilterGroup` and `FilterCondition` domain-specific language. Filters are parsed and rendered dynamically per backend. For details, see [Filter DSL](#3.4).

Sources: `jiuwen_memory/foundation/store/filter_dsl` [jiuwen_memory/foundation/store/index/simple_memory_index.py:37-37]()

---

Diagram: Foundation Storage Abstractions Map
```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        A["MemoryIndexContract"] --> B["SimpleMemoryIndex"]
        B --> C["KeyValueStore"]
        B --> D["VectorStore"]
    end
    subgraph "CodeEntitySpace"
        E["BaseMemoryIndex"] --> F["SimpleMemoryIndex"]
        F --> G["BaseKVStore"]
        F --> H["BaseVectorStore"]
        G --> I["DbBasedKVStore"]
        H --> J["BaseVectorStoreImpls"]
    end
    A -.-> E
    B -.-> F
    C -.-> G
    D -.-> H
```
Sources: `jiuwen_memory/foundation/store/index/simple_memory_index.py:28-69` [], `jiuwen_memory/foundation/store/kv/db_based_kv_store.py:51-62` []

---

## Security, Codecs, and Model Infrastructure

### Storage Codecs and Security
Data encryption and serialization are handled via the `StorageCodec` interface. Implementations include AES-256-GCM (`AesStorageCodec`) and SM4 codecs registered via a central cryptographic registry. For details, see [Storage Codecs and Security](#3.5).

Sources: `jiuwen_memory/memory_core/manage/mem_model/sql_message_store.py:18-49` []

### LLM, Embedding and Prompt Layer
Model interactions use a unified `Model` abstraction alongside intelligent routers (`intelli router`), message chunk parsers, prompt templates, and retrieval embedding wrappers. For details, see [LLM, Embedding and Prompt Layer](#3.6).

Sources: `jiuwen_memory/memory_core/manage/index/fragment_memory_manager.py:7-8` []

---

Diagram: LLM and Codec Abstractions Map
```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        K["StorageEncryptionCodec"] --> L["AESCodec"]
        M["ModelAbstractionLayer"] --> N["IntelliRouterClient"]
    end
    subgraph "CodeEntitySpace"
        O["StorageCodec"] --> P["AesStorageCodec"]
        Q["Model"] --> R["ModelClients"]
        S["SqlMessageStore"] --> P
    end
    K -.-> O
    L -.-> P
    M -.-> Q
    N -.-> R
```
Sources: `jiuwen_memory/memory_core/manage/mem_model/sql_message_store.py:18-49` [], `jiuwen_memory/memory_core/manage/index/fragment_memory_manager.py:7-8` []

---

# Page: Memory Index Backends

# Memory Index Backends

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jiuwen_memory/foundation/store/base_memory_index.py](jiuwen_memory/foundation/store/base_memory_index.py)
- [jiuwen_memory/foundation/store/index/simple_memory_index.py](jiuwen_memory/foundation/store/index/simple_memory_index.py)
- [jiuwen_memory/foundation/store/kv/db_based_kv_store.py](jiuwen_memory/foundation/store/kv/db_based_kv_store.py)
- [jiuwen_memory/memory_core/manage/index/fragment_memory_manager.py](jiuwen_memory/memory_core/manage/index/fragment_memory_manager.py)
- [jiuwen_memory/memory_core/manage/index/summary_manager.py](jiuwen_memory/memory_core/manage/index/summary_manager.py)
- [jiuwen_memory/memory_core/manage/mem_meta/__init__.py](jiuwen_memory/memory_core/manage/mem_meta/__init__.py)
- [jiuwen_memory/memory_core/manage/mem_model/sql_message_store.py](jiuwen_memory/memory_core/manage/mem_model/sql_message_store.py)
- [jiuwen_memory/memory_core/manage/search/search_manager.py](jiuwen_memory/memory_core/manage/search/search_manager.py)
- [jiuwen_memory/server/config_center_api.py](jiuwen_memory/server/config_center_api.py)
- [jiuwen_memory/server/log_center_api.py](jiuwen_memory/server/log_center_api.py)

</details>



## Purpose and Scope

Section 3.1 covers the storage indexing abstractions and hybrid backends within the JiuwenMemory foundation layer (`jiuwen_memory/foundation/store/`). Memory index backends manage the persistence, retrieval, and scalar filtering of memory documents across multi-tenant scopes (`user_id` and `scope_id`). 

This page outlines the core `BaseMemoryIndex` contract and the legacy hybrid `SimpleMemoryIndex` design. For file-based markdown and SQLite indexing backends, see [File Memory Index (Markdown + SQLite)](#3.1.1).

---

## 1. BaseMemoryIndex Contract and Data Model

The `BaseMemoryIndex` abstract base class defines the contract for memory storage, updates, deletion, and semantic search operations. Concrete implementations bind storage providers (such as key-value stores and vector databases) to handle tenant-scoped memory operations.

```mermaid
graph TD
  subgraph Natural_Language_Space ["Natural Language Space"]
    A["MemoryDocumentLifecycle"] --> B["MultiTenantScopedRetrieval"]
  end
  subgraph Code_Entity_Space ["Code Entity Space"]
    C["BaseMemoryIndex"] --> D["MemoryDoc"]
    C --> E["add_memories"]
    C --> F["update_memories"]
    C --> G["update_mem_by_id"]
    C --> H["search"]
  end
  A --> C
```
*Sources: [jiuwen_memory/foundation/store/base_memory_index.py:24-186]()*

Memory documents are represented by the `MemoryDoc` Pydantic model, which encapsulates unique identifiers, text content, memory types, importance flags, blacklisting states (forgetting), and extensible metadata fields.

Sources: [jiuwen_memory/foundation/store/base_memory_index.py:24-42]()

---

## 2. SimpleMemoryIndex (KV + Vector Hybrid) Design

`SimpleMemoryIndex` provides a backward-compatible hybrid index over legacy key-value stores and vector collections (`[jiuwen_memory/foundation/store/index/simple_memory_index.py:40-48]()`). It pairs a `BaseKVStore` for raw JSON document persistence with a `BaseVectorStore` for dense vector search and scalar filtering.

```mermaid
graph TD
  subgraph SimpleMemoryIndex_Layout ["SimpleMemoryIndex Layout"]
    A["SimpleMemoryIndex"] --> B["KVStore: UMD/user_id/scope_id/mem_id"]
    A --> C["VectorStore: uid_user_id_gid_scope_id_mtype_mem_type"]
    A --> D["TrackingIDs: UMD/user_id/scope_id/ids"]
  end
```
*Sources: [jiuwen_memory/foundation/store/index/simple_memory_index.py:13-17](), [jiuwen_memory/foundation/store/index/simple_memory_index.py:50-98]()*

### Key Layout and Tracking

The key layout utilizes specific hierarchical prefixes to partition data per tenant and scope:
- **KV Document Key:** `UMD/{user_id}/{scope_id}/{mem_id}` storing the JSON serialization of memory attributes `[jiuwen_memory/foundation/store/index/simple_memory_index.py:13-14]`, `[jiuwen_memory/foundation/store/index/simple_memory_index.py:90-91]()`.
- **Vector Collection Naming:** `uid_{user_id}_gid_{scope_id}_mtype_{mem_type}` isolating collections by type and scope `[jiuwen_memory/foundation/store/index/simple_memory_index.py:15-16]()`.
- **ID Tracking Keys:** `UMD/{user_id}/{scope_id}/ids` and type-specific tracking keys used to maintain consistency across storage backends `[jiuwen_memory/foundation/store/index/simple_memory_index.py:52-98]()`.

Sources: [jiuwen_memory/foundation/store/index/simple_memory_index.py:11-98]()

### Filter Pushdown and Scalar Filtering

`SimpleMemoryIndex` translates backend-neutral scalar filter expressions (`FilterGroup`) into native vector store query filters and post-processes results against the KV store when necessary. Top-level scalar fields such as `is_important` and `blacklisted` are pushed directly into the vector store schema for efficient pruning during similarity search.

Sources: [jiuwen_memory/foundation/store/index/simple_memory_index.py:161-167](), [jiuwen_memory/foundation/store/base_memory_index.py:110-115]()

---

## 3. Child Indexing Backends

For modern local-first and file-oriented deployments, JiuwenMemory provides file-based markdown and SQLite indexing strategies.

- For implementation details on parsing markdown chunks, FTS5 full-text search, `sqlite-vec` vector integration, and background file watching, see [File Memory Index (Markdown + SQLite)](#3.1.1).

Sources: [jiuwen_memory/foundation/store/index/simple_memory_index.py:40-48]()

---

# Page: File Memory Index (Markdown + SQLite)

# File Memory Index (Markdown + SQLite)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jiuwen_memory/foundation/store/index/file_index/__init__.py](jiuwen_memory/foundation/store/index/file_index/__init__.py)
- [jiuwen_memory/foundation/store/index/file_index/_chunk_parser.py](jiuwen_memory/foundation/store/index/file_index/_chunk_parser.py)
- [jiuwen_memory/foundation/store/index/file_index/_file_watcher.py](jiuwen_memory/foundation/store/index/file_index/_file_watcher.py)
- [jiuwen_memory/foundation/store/index/file_index/_md_store.py](jiuwen_memory/foundation/store/index/file_index/_md_store.py)
- [jiuwen_memory/foundation/store/index/file_index/_vector_index.py](jiuwen_memory/foundation/store/index/file_index/_vector_index.py)
- [jiuwen_memory/foundation/store/index/file_index/file_memory_index.py](jiuwen_memory/foundation/store/index/file_index/file_memory_index.py)
- [tests/unit_tests/core/foundation/store/index/test_file_memory_index.py](tests/unit_tests/core/foundation/store/index/test_file_memory_index.py)

</details>



## Purpose and Scope
The `FileMemoryIndex` implements the `BaseMemoryIndex` contract by combining human-readable Markdown files grouped by memory type with a SQLite-backed hybrid vector and keyword index. It provides per-type file partitioning under user and scope namespaces, robust frontmatter parsing with tolerance for malformed or unclosed blocks, atomic file operations, incremental re-indexing based on file hashing, and background change detection via an optional watchdog file watcher.

Sources:
- `jiuwen_memory/foundation/store/index/file_index/file_memory_index.py:1-89`
- `jiuwen_memory/foundation/store/index/file_index/_vector_index.py:1-28`

---

## 1. Architecture and Component Decomposition

`FileMemoryIndex` acts as an orchestrator across four specialized sub-modules:
- `MarkdownStore`: Manages multi-memory markdown files with YAML frontmatter under `memories/{user_id}/{scope_id}/{type_name}.md` [jiuwen_memory/foundation/store/index/file_index/_md_store.py:68-82] and applies optional `StorageCodec` encryption to body texts [jiuwen_memory/foundation/store/index/file_index/_md_store.py:10-11].
- `VectorIndex`: Maintains the SQLite database (`memory.db`) containing schema tables for files, chunks, sqlite-vec vectors (`chunks_vec`), FTS5 full-text indices (`chunks_fts`), and embedding caches [jiuwen_memory/foundation/store/index/file_index/_vector_index.py:7-15].
- `MemoryFileWatcher`: Uses the `watchdog` library to monitor memory directories recursively with a debounce timer and thread-safe event handoff [jiuwen_memory/foundation/store/index/file_index/_file_watcher.py:44-61].
- `_chunk_parser`: Parses `.md` files into structured `Block` objects and serializes blocks back to markdown [jiuwen_memory/foundation/store/index/file_index/_chunk_parser.py:36-71].

```mermaid
graph TD
    subgraph "Natural Language Space: File Memory Index Orchestration"
        Client["Agent or MemoryEngine"] --> FMI["FileMemoryIndex"]
        FMI --> MDS["MarkdownStore"]
        FMI --> VI["VectorIndex"]
        FMI --> MFW["MemoryFileWatcher"]
        MDS --> CP["_chunk_parser"]
        VI --> DB["SQLite (memory.db)"]
    end
```
Sources:
- `jiuwen_memory/foundation/store/index/file_index/file_memory_index.py:55-88`
- `jiuwen_memory/foundation/store/index/file_index/_md_store.py:68-82`
- `jiuwen_memory/foundation/store/index/file_index/_vector_index.py:7-15`
- `jiuwen_memory/foundation/store/index/file_index/_file_watcher.py:44-61`

---

## 2. Chunk Parsing and Markdown Persistence

The underlying files store multiple memories in a single `{Type}.md` file separated by YAML frontmatter blocks [jiuwen_memory/foundation/store/index/file_index/_chunk_parser.py:5-26]. Each block maps to a `Block` dataclass containing memory identification, type, line-number tracking (`start_line`, `end_line`), timestamps, and text hashes [jiuwen_memory/foundation/store/index/file_index/_chunk_parser.py:36-67].

### Chunk Parser Robustness
- **Unclosed Frontmatter Handling**: If a frontmatter block lacks a closing `---`, the parser recovers remaining lines as body content rather than dropping the block [jiuwen_memory/foundation/store/index/file_index/_chunk_parser.py:119-127].
- **Malformed YAML Fallback**: If `yaml.safe_load()` raises an exception, the parser performs a line-by-line fallback scan to extract known keys (`id`, `type`) and recover text contents [jiuwen_memory/foundation/store/index/file_index/_chunk_parser.py:153-194].

### MarkdownStore Atomic Writes
`MarkdownStore.write_file()` prevents partial-write corruption during system crashes by writing to a temporary file (`{path}.tmp`) and replacing the destination atomically via `os.replace()` [jiuwen_memory/foundation/store/index/file_index/_md_store.py:161-174]. Path traversal attempts are blocked via `_validate_path_segment()` checks [jiuwen_memory/foundation/store/index/file_index/_md_store.py:43-65, 115-131].

```mermaid
graph TD
    subgraph "Code Entity Space: Markdown Persistence Pipeline"
        WriteCall["MarkdownStore.write_file"] --> LockCheck["Asyncio.Lock (per path)"]
        LockCheck --> TempWrite["Write to {path}.tmp"]
        TempWrite --> AtomicReplace["os.replace(tmp, path)"]
        AtomicReplace --> DiskStorage["Atomically Updated {Type}.md"]
    end
```
Sources:
- `jiuwen_memory/foundation/store/index/file_index/_chunk_parser.py:36-194`
- `jiuwen_memory/foundation/store/index/file_index/_md_store.py:43-182`

---

## 3. SQLite Vector Index and Hybrid Retrieval

`VectorIndex` manages the SQLite database backend [jiuwen_memory/foundation/store/index/file_index/_vector_index.py:150-174].

### Database Schema
- `files`: Tracks per-file hashes, mtimes, and sizes for dirty checking [jiuwen_memory/foundation/store/index/file_index/_vector_index.py:9-10].
- `chunks`: Stores per-memory metadata, text, embedding BLOBs, and physical line coordinates (`path`, `start_line`, `end_line`) [jiuwen_memory/foundation/store/index/file_index/_vector_index.py:11-12].
- `chunks_vec`: Vector search table utilizing `vec0` with cosine distance and partition keys (`user_id \x1f scope_id`) [jiuwen_memory/foundation/store/index/file_index/_vector_index.py:13, 113-120].
- `chunks_fts`: FTS5 full-text search table with `jieba` CJK segmentation (`_segment_chinese`) [jiuwen_memory/foundation/store/index/file_index/_vector_index.py:14, 123-147].
- `embedding_cache`: Caches embedding results to prevent redundant API calls [jiuwen_memory/foundation/store/index/file_index/_vector_index.py:15].

### Hybrid Search Execution
Searches combine vector KNN (`VECTOR_WEIGHT = 0.9`) and FTS5 keyword matching (`FTS_WEIGHT = 0.1`) using weighted score fusion [jiuwen_memory/foundation/store/index/file_index/_vector_index.py:58-59]. If `sqlite-vec` is unavailable, the system falls back to pure-Python cosine similarity [jiuwen_memory/foundation/store/index/file_index/_vector_index.py:22-23].

```mermaid
graph TD
    subgraph "Code Entity Space: VectorIndex Hybrid Retrieval Flow"
        SearchReq["VectorIndex.search"] --> PartKey["_partition_key(user_id, scope_id)"]
        PartKey --> KNNQuery["sqlite-vec KNN Search (chunks_vec)"]
        PartKey --> FTSQuery["FTS5 Full-Text Search (chunks_fts)"]
        KNNQuery --> Fusion["Weighted Score Fusion (0.9 / 0.1)"]
        FTSQuery --> Fusion
        Fusion --> RankedDocs["Return Ranked MemoryDoc List"]
    end
```
Sources:
- `jiuwen_memory/foundation/store/index/file_index/_vector_index.py:7-148, 150-174`

---

## 4. Incremental Re-indexing and File Watcher

When external editors modify `.md` files or programmatic updates occur, `FileMemoryIndex` synchronizes state without unnecessary embedding overhead.

### Incremental Re-Index Logic (`sync_file`)
1. Computes the hash of the target file and checks the `files` table for modifications.
2. Parses blocks from the updated content using `parse_blocks()` [jiuwen_memory/foundation/store/index/file_index/_vector_index.py:48-51].
3. Compares block hashes against existing database records:
   - **Unchanged text with drifted line numbers**: Executes a cheap `UPDATE` to adjust `start_line` and `end_line` without re-embedding [jiuwen_memory/foundation/store/index/file_index/_vector_index.py:17-20].
   - **New or modified text**: Generates embeddings and upserts records.
   - **Deleted blocks**: Removes corresponding chunks from vector and FTS tables [jiuwen_memory/foundation/store/index/file_index/_vector_index.py:17-18].

### Background File Watcher (`MemoryFileWatcher`)
`MemoryFileWatcher` wraps the `watchdog` library, running recursively on `{root_dir}/memories/` [jiuwen_memory/foundation/store/index/file_index/_file_watcher.py:44-52]. Events pass through a 2-second debounce timer before invoking `_on_file_changed()` on the main event loop via thread-safe task scheduling (`call_soon_threadsafe`) [jiuwen_memory/foundation/store/index/file_index/_file_watcher.py:47-48, 178-189]. If `watchdog` is uninstalled, the watcher gracefully degrades to a no-op, falling back to lazy synchronization during searches [jiuwen_memory/foundation/store/index/file_index/_file_watcher.py:10-11, 117-119].

Sources:
- `jiuwen_memory/foundation/store/index/file_index/file_memory_index.py:127-161`
- `jiuwen_memory/foundation/store/index/file_index/_file_watcher.py:44-189`
- `jiuwen_memory/foundation/store/index/file_index/_vector_index.py:17-20`

---

# Page: Vector Stores

# Vector Stores

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jiuwen_memory/common/exception/codes.py](jiuwen_memory/common/exception/codes.py)
- [jiuwen_memory/foundation/store/base_vector_store.py](jiuwen_memory/foundation/store/base_vector_store.py)
- [jiuwen_memory/foundation/store/filter_dsl.py](jiuwen_memory/foundation/store/filter_dsl.py)
- [jiuwen_memory/foundation/store/vector/chroma_vector_store.py](jiuwen_memory/foundation/store/vector/chroma_vector_store.py)
- [jiuwen_memory/foundation/store/vector/es_vector_store.py](jiuwen_memory/foundation/store/vector/es_vector_store.py)
- [jiuwen_memory/foundation/store/vector/milvus_vector_store.py](jiuwen_memory/foundation/store/vector/milvus_vector_store.py)
- [jiuwen_memory/memory_core/manage/mem_model/message_manager.py](jiuwen_memory/memory_core/manage/mem_model/message_manager.py)
- [jiuwen_memory/memory_core/manage/search/filter_dsl.py](jiuwen_memory/memory_core/manage/search/filter_dsl.py)
- [tests/unit_tests/server/test_server_endpoints.py](tests/unit_tests/server/test_server_endpoints.py)

</details>



## Purpose and Scope
This page details the vector storage abstraction and backend implementations within the JiuwenMemory foundation layer (`jiuwen_memory/foundation/store/`). The vector store subsystem provides a unified, backend-agnostic interface (`BaseVectorStore`) for managing high-dimensional vector collections, inserting multi-field documents, executing similarity searches (Cosine, L2, Inner Product), and translating declarative filter DSL expressions (`FilterGroup`) into native database queries across supported backends: Milvus, ChromaDB, and Elasticsearch.

Sources: `[jiuwen_memory/foundation/store/base_vector_store.py:1-15]()`, `[jiuwen_memory/foundation/store/vector/milvus_vector_store.py:39-44]()`, `[jiuwen_memory/foundation/store/vector/chroma_vector_store.py:38-43]()`, `[jiuwen_memory/foundation/store/vector/es_vector_store.py:41-43]()`

---

## 1. The `BaseVectorStore` Abstraction and Data Models

The foundation contract is defined by `BaseVectorStore` alongside strict Pydantic data schemas that normalize collection definitions and data types across distinct vector database engines.

### Key Classes & Schemas
- `BaseVectorStore`: The abstract base class defining core lifecycle and data operation signatures (`create_collection`, `insert`, `search`, `delete`, `update`, `list_docs`) `[jiuwen_memory/foundation/store/base_vector_store.py:4-15]()`.
- `VectorDataType`: An enum supporting types such as `VARCHAR`, `FLOAT_VECTOR`, `INT64`, `INT32`, `FLOAT`, `DOUBLE`, `BOOL`, and `JSON` `[jiuwen_memory/foundation/store/base_vector_store.py:17-31]()`.
- `FieldSchema`: Defines individual collection field properties, validating constraints like vector dimension (`dim`) for `FLOAT_VECTOR` types `[jiuwen_memory/foundation/store/base_vector_store.py:33-65]()`.
- `CollectionSchema`: Manages collection-level field lists, single primary key constraints, and dynamic field toggles (`enable_dynamic_field`) `[jiuwen_memory/foundation/store/base_vector_store.py:109-135]()`.

Sources: `[jiuwen_memory/foundation/store/base_vector_store.py:1-175]()`

---

## 2. Backend Implementations

### 2.1 Milvus Vector Store
`MilvusVectorStore` integrates with PyMilvus using `MilvusClient`. Connections and database namespaces are initialized lazily on the first operation to support fault-tolerant startup sequences `[jiuwen_memory/foundation/store/vector/milvus_vector_store.py:39-128]`.

```mermaid
graph TD
    A["ClientAccess[_client]"] --> B["MilvusClientInit"]
    B --> C["DatabaseSelection"]
    C --> D["CollectionSchemaMapping"]
    D --> E["FilterDSLToMilvusExpr"]

    style A fill:#ffffff,stroke:#000000,stroke-width:1px
    style B fill:#ffffff,stroke:#000000,stroke-width:1px
    style C fill:#ffffff,stroke:#000000,stroke-width:1px
    style D fill:#ffffff,stroke:#000000,stroke-width:1px
    style E fill:#ffffff,stroke:#000000,stroke-width:1px
```
*Figure 1: MilvusVectorStore Initialization and Execution Pipeline*

Sources: `[jiuwen_memory/foundation/store/vector/milvus_vector_store.py:39-183]()`

### 2.2 Chroma Vector Store
`ChromaVectorStore` wraps `chromadb.PersistentClient` (or in-memory clients if no persistence path is provided) `[jiuwen_memory/foundation/store/vector/chroma_vector_store.py:38-55]`. It maps user-defined collection schemas onto Chroma's internal metadata model, serializing field definitions and distance configurations (`cosine`, `l2`, `ip`) into collection metadata attributes `[jiuwen_memory/foundation/store/vector/chroma_vector_store.py:76-147]`.

Sources: `[jiuwen_memory/foundation/store/vector/chroma_vector_store.py:38-161]()`

### 2.3 Elasticsearch Vector Store
`ElasticsearchVectorStore` utilizes `AsyncElasticsearch` to manage vector indices prefixed by `index_prefix` `[jiuwen_memory/foundation/store/vector/es_vector_store.py:41-64]`. It maps `FLOAT_VECTOR` fields to Elasticsearch `dense_vector` mappings with configured dimensions and similarity functions (`cosine`, `l2_norm`, `dot_product`), while maintaining collection metadata within a dedicated metadata document (`_METADATA_DOC_ID`) `[jiuwen_memory/foundation/store/vector/es_vector_store.py:67-141]`.

Sources: `[jiuwen_memory/foundation/store/vector/es_vector_store.py:41-130]()`

---

## 3. Filter DSL and Backend Rendering

The filter subsystem uses a backend-neutral AST (`FilterGroup` and `FilterCondition`) supporting scalar operations (`eq`, `ne`) and logical grouping (`and`, `or`) up to a maximum nesting depth (`MAX_NESTING_DEPTH = 16`) `[jiuwen_memory/foundation/store/filter_dsl.py:1-105]()`.

```mermaid
graph TD
    A["FilterGroupAST"] --> B["FilterNormalizer"]
    B --> C["MilvusRenderer"]
    B --> D["ElasticsearchRenderer"]
    B --> E["ChromaRenderer"]

    style A fill:#ffffff,stroke:#000000,stroke-width:1px
    style B fill:#ffffff,stroke:#000000,stroke-width:1px
    style C fill:#ffffff,stroke:#000000,stroke-width:1px
    style D fill:#ffffff,stroke:#000000,stroke-width:1px
    style E fill:#ffffff,stroke:#000000,stroke-width:1px
```
*Figure 2: Filter DSL Normalization and Translation Flow*

Sources: `[jiuwen_memory/foundation/store/filter_dsl.py:1-105]()`

---

## 4. Architecture: Natural Language Space to Code Entity Space

The following diagrams bridge conceptual memory retrieval terms with concrete Python classes and methods in the codebase.

```mermaid
graph TB
    subgraph NaturalLanguageSpace["Natural Language Space"]
        A["Vector Storage Abstraction"]
        B["High-Performance Vector Engine"]
        C["Embedded SQLite/Local DB Vector Store"]
        D["Distributed Search Store"]
    end

    subgraph CodeEntitySpace["Code Entity Space"]
        E["BaseVectorStore (jiuwen_memory/foundation/store/base_vector_store.py)"]
        F["MilvusVectorStore (jiuwen_memory/foundation/store/vector/milvus_vector_store.py)"]
        G["ChromaVectorStore (jiuwen_memory/foundation/store/vector/chroma_vector_store.py)"]
        H["ElasticsearchVectorStore (jiuwen_memory/foundation/store/vector/es_vector_store.py)"]
    end

    A --> E
    B --> F
    C --> G
    D --> H

    style NaturalLanguageSpace fill:#ffffff,stroke:#000000,stroke-width:1px
    style CodeEntitySpace fill:#ffffff,stroke:#000000,stroke-width:1px
    style A fill:#ffffff,stroke:#000000,stroke-width:1px
    style B fill:#ffffff,stroke:#000000,stroke-width:1px
    style C fill:#ffffff,stroke:#000000,stroke-width:1px
    style D fill:#ffffff,stroke:#000000,stroke-width:1px
    style E fill:#ffffff,stroke:#000000,stroke-width:1px
    style F fill:#ffffff,stroke:#000000,stroke-width:1px
    style G fill:#ffffff,stroke:#000000,stroke-width:1px
    style H fill:#ffffff,stroke:#000000,stroke-width:1px
```
*Figure 3: System-to-Code Mapping for Vector Store Backends*

Sources: `[jiuwen_memory/foundation/store/base_vector_store.py:4-15]`, `[jiuwen_memory/foundation/store/vector/milvus_vector_store.py:39-44]`, `[jiuwen_memory/foundation/store/vector/chroma_vector_store.py:38-43]`, `[jiuwen_memory/foundation/store/vector/es_vector_store.py:41-43]`

```mermaid
graph TB
    subgraph NaturalLanguageSpace["Natural Language Space"]
        I["Collection Schema Definition"]
        J["Scalar Filter Condition DSL"]
        K["Vector Similarity Search"]
    end

    subgraph CodeEntitySpace["Code Entity Space"]
        L["CollectionSchema & FieldSchema (jiuwen_memory/foundation/store/base_vector_store.py)"]
        M["FilterGroup & FilterCondition (jiuwen_memory/foundation/store/filter_dsl.py)"]
        N["BaseVectorStore.search() (jiuwen_memory/foundation/store/base_vector_store.py)"]
    end

    I --> L
    J --> M
    K --> N

    style NaturalLanguageSpace fill:#ffffff,stroke:#000000,stroke-width:1px
    style CodeEntitySpace fill:#ffffff,stroke:#000000,stroke-width:1px
    style I fill:#ffffff,stroke:#000000,stroke-width:1px
    style J fill:#ffffff,stroke:#000000,stroke-width:1px
    style K fill:#ffffff,stroke:#000000,stroke-width:1px
    style L fill:#ffffff,stroke:#000000,stroke-width:1px
    style M fill:#ffffff,stroke:#000000,stroke-width:1px
    style N fill:#ffffff,stroke:#000000,stroke-width:1px
```
*Figure 4: Schema and Filtering Components Mapping*

Sources: `[jiuwen_memory/foundation/store/base_vector_store.py:33-135]`, `[jiuwen_memory/foundation/store/filter_dsl.py:42-105]`

---

# Page: KV, DB and Message Stores

# KV, DB and Message Stores

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jiuwen_memory/foundation/store/base_kv_store.py](jiuwen_memory/foundation/store/base_kv_store.py)
- [jiuwen_memory/foundation/store/index/simple_memory_index.py](jiuwen_memory/foundation/store/index/simple_memory_index.py)
- [jiuwen_memory/foundation/store/kv/db_based_kv_store.py](jiuwen_memory/foundation/store/kv/db_based_kv_store.py)
- [jiuwen_memory/foundation/store/kv/in_memory_kv_store.py](jiuwen_memory/foundation/store/kv/in_memory_kv_store.py)
- [jiuwen_memory/foundation/store/kv/shelve_store.py](jiuwen_memory/foundation/store/kv/shelve_store.py)
- [jiuwen_memory/foundation/store/vector/milvus_vector_store.py](jiuwen_memory/foundation/store/vector/milvus_vector_store.py)
- [jiuwen_memory/memory_core/common/distributed_lock.py](jiuwen_memory/memory_core/common/distributed_lock.py)
- [jiuwen_memory/memory_core/manage/index/fragment_memory_manager.py](jiuwen_memory/memory_core/manage/index/fragment_memory_manager.py)
- [jiuwen_memory/memory_core/manage/index/summary_manager.py](jiuwen_memory/memory_core/manage/index/summary_manager.py)
- [jiuwen_memory/memory_core/manage/mem_model/message_manager.py](jiuwen_memory/memory_core/manage/mem_model/message_manager.py)
- [jiuwen_memory/memory_core/manage/mem_model/scope_user_mapping_manager.py](jiuwen_memory/memory_core/manage/mem_model/scope_user_mapping_manager.py)
- [jiuwen_memory/memory_core/manage/mem_model/sql_db_store.py](jiuwen_memory/memory_core/manage/mem_model/sql_db_store.py)
- [jiuwen_memory/memory_core/manage/mem_model/sql_message_store.py](jiuwen_memory/memory_core/manage/mem_model/sql_message_store.py)
- [jiuwen_memory/memory_core/migration/migrator/memory_meta_manager.py](jiuwen_memory/memory_core/migration/migrator/memory_meta_manager.py)
- [tests/unit_tests/core/memory/manage/mem_model/test_sql_db_store.py](tests/unit_tests/core/memory/manage/mem_model/test_sql_db_store.py)
- [tests/unit_tests/server/test_server_endpoints.py](tests/unit_tests/server/test_server_endpoints.py)

</details>



This section details the persistence layer and storage abstractions within the `jiuwen_memory` engine. It covers Key-Value storage backends (`DbBasedKVStore`, `InMemoryKVStore`, `ShelveStore`), relational database wrappers (`SqlDbStore`), message persistence subsystems (`SqlMessageStore` and `MessageManager`), distributed concurrency control via `DistributedLock`, and multi-tenant user-scope mappings via `ScopeUserMappingManager`.

Sources: [jiuwen_memory/foundation/store/base_kv_store.py:16-190](), [jiuwen_memory/foundation/store/kv/db_based_kv_store.py:51-173]()

---

## 1. Key-Value Store Abstractions (`BaseKVStore` & Implementations)

The foundation of the key-value subsystem is the `BaseKVStore` abstract base class, which specifies asynchronous operations for key-value manipulation, including batch operations, prefix querying, and atomic exclusive locking `[jiuwen_memory/foundation/store/base_kv_store.py:16-190]()`.

### `DbBasedKVStore` Implementation
`DbBasedKVStore` implements `BaseKVStore` using an asynchronous SQLAlchemy engine `[jiuwen_memory/foundation/store/kv/db_based_kv_store.py:51-62]`. It handles differences across SQL dialects (MySQL, SQLite, and GaussDB):
* **Upsert Statements**: Generates dialect-specific upserts via `_get_upsert_stmt()` (`mysql_insert` for MySQL, `sqlite_insert` for SQLite) `[jiuwen_memory/foundation/store/kv/db_based_kv_store.py:63-86]`.
* **GaussDB Manual Upsert**: Since GaussDB lacks standard native upsert syntax in certain driver configurations, `_manual_upsert()` executes an explicit `SELECT` followed by an `UPDATE` or `INSERT` protected by application-level guards `[jiuwen_memory/foundation/store/kv/db_based_kv_store.py:88-111]`.
* **Binary Handling**: Encodes arbitrary `bytes` payloads using a `__BYTES__:` string prefix and Base64 encoding via `_encode_value()` and `_decode_value()` `[jiuwen_memory/foundation/store/kv/db_based_kv_store.py:112-123]`.
* **Atomic Locking**: Provides `exclusive_set()` and `renew_exclusive()` to support atomic locks with expiration timestamps `[jiuwen_memory/foundation/store/kv/db_based_kv_store.py:136-189]`.

### In-Memory and Shelve KV Stores
For lightweight or embedded scenarios, `InMemoryKVStore` and `ShelveStore` provide in-memory dictionary backing and Python `shelve`-based disk persistence respectively, adhering to the same asynchronous contract.

```mermaid
graph TD
    A["BaseKVStore"] --> B["DbBasedKVStore"]
    A --> C["InMemoryKVStore"]
    A --> D["ShelveStore"]
    B --> E["AsyncEngine (SQLAlchemy)"]
    E --> F["MySQL / SQLite / GaussDB"]
```
*Sources: [jiuwen_memory/foundation/store/base_kv_store.py:16-190](), [jiuwen_memory/foundation/store/kv/db_based_kv_store.py:51-189]()*

---

## 2. Relational Database Abstractions (`SqlDbStore`)

`SqlDbStore` wraps `BaseDbStore` to provide table-level relational database operations for structured models and metadata `[jiuwen_memory/memory_core/manage/mem_model/sql_db_store.py:21-29]`.

Key functions include:
* `write(table, data)`: Inserts rows into the target table, propagating `IntegrityError` upon primary key or unique constraint violations so callers can distinguish between successful operations and conflicts `[jiuwen_memory/memory_core/manage/mem_model/sql_db_store.py:30-49]`.
* `insert_or_update(...)`: Executes atomic upserts (`INSERT ... ON CONFLICT DO UPDATE` or MySQL equivalents, with manual `UPDATE`/`INSERT` fallback for GaussDB) to prevent race conditions during concurrent updates `[jiuwen_memory/memory_core/manage/mem_model/sql_db_store.py:59-165]`.

Sources: [jiuwen_memory/memory_core/manage/mem_model/sql_db_store.py:21-165]()

---

## 3. Message Stores and Message Management (`SqlMessageStore` & `MessageManager`)

### `SqlMessageStore`
`SqlMessageStore` extends `BaseMessageStore` to persist conversational turns and agent messages in relational tables `[jiuwen_memory/memory_core/manage/mem_model/sql_message_store.py:25-48]`.
* **Encryption**: Uses `AesStorageCodec` (or an injected `StorageCodec`) to encode and decode message content securely `[jiuwen_memory/memory_core/manage/mem_model/sql_message_store.py:48-52]`.
* **Unique ID Generation**: `_generate_message_id()` combines a SHA-256 hash of the message content, timestamp, and a random hex nonce (`uuid.uuid4().hex[:8]`) to guarantee unique IDs even during concurrent batch writes of identical messages `[jiuwen_memory/memory_core/manage/mem_model/sql_message_store.py:54-66]`.

### `MessageManager`
`MessageManager` provides a high-level orchestration API over `BaseMessageStore` `[jiuwen_memory/memory_core/manage/mem_model/message_manager.py:24-31]`:
* `add(req, msg_id)`: Validates required request fields (`user_id`, `scope_id`, `content`), wraps content into a `BaseMessage`, and persists it `[jiuwen_memory/memory_core/manage/mem_model/message_manager.py:32-61]`.
* `get(...)` and `get_with_metadata(...)`: Retrieve message history ordered chronologically, with or without auxiliary metadata `[jiuwen_memory/memory_core/manage/mem_model/message_manager.py:62-114]`.
* Deletion APIs: `delete_by_user_and_scope()` and `delete_by_id()` clean up stored records `[jiuwen_memory/memory_core/manage/mem_model/message_manager.py:146-157]`.

```mermaid
graph TD
    A["MessageManager"] -->|Calls add/get| B["SqlMessageStore"]
    B -->|Encodes content| C["AesStorageCodec"]
    B -->|Persists rows| D["SqlDbStore"]
    D -->|Executes SQL| E["Database Tables"]
```
*Sources: [jiuwen_memory/memory_core/manage/mem_model/sql_message_store.py:25-115](), [jiuwen_memory/memory_core/manage/mem_model/message_manager.py:24-157]()*

---

## 4. Distributed Concurrency Control (`DistributedLock`)

`DistributedLock` provides multiprocess-safe distributed locking backed by any KV store implementing `exclusive_set()` and `renew_exclusive()` `[jiuwen_memory/memory_core/common/distributed_lock.py:9-24]`.
* **Watchdog Loop**: Once a lock is acquired (`acquire()`), a background coroutine (`_watchdog()`) automatically renews the lock every `RENEW_INTERVAL_SEC` (3 seconds) with a TTL of 10 seconds `[jiuwen_memory/memory_core/common/distributed_lock.py:30-49]`. This ensures that long-running tasks (such as LLM extraction workflows) do not experience lock expiration.
* **Deadlock Prevention**: If the holding process crashes, the watchdog halts and the lock automatically expires after 10 seconds.
* **Context Manager**: Supports asynchronous context management via `__aenter__` and `__aexit__` `[jiuwen_memory/memory_core/common/distributed_lock.py:104-109]`.

Sources: [jiuwen_memory/memory_core/common/distributed_lock.py:9-109]()

---

## 5. Scope and User Mapping (`ScopeUserMappingManager`)

`ScopeUserMappingManager` manages the relationship between execution scopes and user identities within the memory engine, facilitating tenant isolation and scope resolution across memory subsystems `[jiuwen_memory/memory_core/manage/mem_model/scope_user_mapping_manager.py]`.

Sources: [jiuwen_memory/memory_core/manage/mem_model/scope_user_mapping_manager.py]()

---

# Page: Filter DSL

# Filter DSL

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jiuwen_memory/common/exception/codes.py](jiuwen_memory/common/exception/codes.py)
- [jiuwen_memory/foundation/store/base_vector_store.py](jiuwen_memory/foundation/store/base_vector_store.py)
- [jiuwen_memory/foundation/store/filter_dsl.py](jiuwen_memory/foundation/store/filter_dsl.py)
- [jiuwen_memory/foundation/store/vector/chroma_vector_store.py](jiuwen_memory/foundation/store/vector/chroma_vector_store.py)
- [jiuwen_memory/foundation/store/vector/es_vector_store.py](jiuwen_memory/foundation/store/vector/es_vector_store.py)
- [jiuwen_memory/foundation/store/vector/gauss_vector_store.py](jiuwen_memory/foundation/store/vector/gauss_vector_store.py)
- [jiuwen_memory/memory_core/manage/search/filter_dsl.py](jiuwen_memory/memory_core/manage/search/filter_dsl.py)
- [tests/unit_tests/core/foundation/store/filter/test_filter_dsl.py](tests/unit_tests/core/foundation/store/filter/test_filter_dsl.py)
- [tests/unit_tests/core/foundation/store/filter/test_filter_normalizer.py](tests/unit_tests/core/foundation/store/filter/test_filter_normalizer.py)
- [tests/unit_tests/core/foundation/store/filter/test_render_filters.py](tests/unit_tests/core/foundation/store/filter/test_render_filters.py)

</details>



## Purpose and Scope

This page documents section 3.4 of the `agent-memory` engine, focusing on the backend-neutral `FilterGroup` and `FilterCondition` Domain Specific Language (DSL). It covers the data models, strict validation rules (such as scalar type restrictions and nesting depth caps), the single-entry normalization pipeline, default filter injection (`ensure_blacklisted_ne`), and per-backend rendering logic targeting Milvus, ChromaDB, Elasticsearch, and GaussVector stores.

Sources: `jiuwen_memory/foundation/store/filter_dsl.py`, `jiuwen_memory/memory_core/manage/search/filter_normalizer.py`

---

## 1. Filter DSL Core Architecture & Data Models

The filter DSL is implemented as a set of Pydantic models designed to express backend-agnostic structured queries. It decouples the memory engine's search and retrieval logic from underlying vector store query syntaxes.

### Key Classes and Enums

*   `FilterOperator`: Defines supported scalar comparison operators (`EQ` for equality, `NE` for inequality). Future operators (like GT, LT, IN, CONTAINS) are intentionally excluded from the initial scope [jiuwen_memory/foundation/store/filter_dsl.py:23-29]().
*   `FilterLogic`: Defines logical combiners (`AND`, `OR`) for grouping multiple conditions [jiuwen_memory/foundation/store/filter_dsl.py:31-36]().
*   `MAX_NESTING_DEPTH`: Hard integer cap set to `16` to prevent stack overflow or deep recursion during rendering and validation [jiuwen_memory/foundation/store/filter_dsl.py:38-39]().
*   `FilterCondition`: Represents a single scalar comparison node (`field <op> value`). It validates that field names are non-empty strings and that values for `EQ` and `NE` are strictly scalar types (`str`, `int`, `float`, `bool`, `None`), rejecting lists and dictionaries [jiuwen_memory/foundation/store/filter_dsl.py:42-67]().
*   `FilterGroup`: Represents a logical container holding a `logic` operator and a list of child conditions or nested `FilterGroup` instances. It enforces recursive depth validation up to `MAX_NESTING_DEPTH` [jiuwen_memory/foundation/store/filter_dsl.py:69-94]().

```mermaid
graph TD
    sub5["Code Entity Space"]
    sub5 --> A["FilterGroup"]
    sub5 --> B["FilterCondition"]
    sub5 --> C["FilterOperator"]
    sub5 --> D["FilterLogic"]

    A -->|"contains list of"| A
    A -->|"contains list of"| B
    B -->|"uses"| C
    A -->|"uses"| D

    A -->|"validated by _check_depth()"| E["MAX_NESTING_DEPTH=16"]
    B -->|"validated by _check_value_scalar()"| F["Scalar Values Only"]
    B -->|"validated by _check_field_non_empty()"| G["Non-empty Field Name"]

    style A fill:#none,stroke:#333,stroke-width:2px
    style B fill:#none,stroke:#333,stroke-width:2px
```
*Figure 1: Architectural mapping of the Filter DSL data structures and their validation boundaries.*

Sources: `jiuwen_memory/foundation/store/filter_dsl.py`, `tests/unit_tests/core/foundation/store/filter/test_filter_dsl.py`

---

## 2. Normalization and Default Filter Injection

Before queries reach storage backends, user-supplied filter payloads undergo preprocessing via the filter normalizer module.

### Normalization Pipeline

The normalization workflow handles raw inputs through two primary functions:
1. `normalize_filters(filters)`: Accepts `FilterGroup` instances directly or `None`. Passing raw dictionaries or unsupported types raises a `StatusCode.MEMORY_FILTER_FORMAT_ERROR` [jiuwen_memory/common/exception/codes.py:7-12](), [jiuwen_memory/memory_core/manage/search/filter_normalizer.py:14-48]().
2. `ensure_blacklisted_ne(filters)`: Automatically injects a safety filter ensuring soft-deleted or blacklisted records (`blacklisted != true`) are excluded from search results unless an explicit `blacklisted` condition is already present in the AST [jiuwen_memory/memory_core/manage/search/filter_normalizer.py:50-94]().

```mermaid
graph TD
    sub6["Code Entity Space"]
    sub6 --> Input["Raw Filter Input"]
    Input --> NF["normalize_filters()"]
    NF -->|"Validate Type & Structure"| Check{{"Is FilterGroup or None?"}}
    Check -->|"Dict or Invalid"| Err["Raise MEMORY_FILTER_FORMAT_ERROR"]
    Check -->|"Valid FilterGroup"| EBN["ensure_blacklisted_ne()"]
    EBN -->|"Has blacklisted field?"| HasField{{"Yes / No"}}
    HasField -->|"Yes"| Pass["Return FilterGroup As-Is"]
    HasField -->|"No"| Inject["Wrap in AND Group with blacklisted != True"]

    style NF fill:#none,stroke:#333,stroke-width:2px
    style EBN fill:#none,stroke:#333,stroke-width:2px
```
*Figure 2: Data flow and execution path of the filter normalization and blacklisted-exclusion injection pipeline.*

Sources: `jiuwen_memory/memory_core/manage/search/filter_normalizer.py`, `tests/unit_tests/core/foundation/store/filter/test_filter_normalizer.py`

---

## 3. Per-Backend Renderer Implementations

Each vector and index storage backend implements a `_render_filters` method to translate the `FilterGroup` abstract syntax tree into backend-native query expressions.

### Backend-Specific Rendering Strategies

*   **MilvusVectorStore**: Renders expressions into string-based relational snippets, such as `category == "work" && blacklisted != true`, using boolean operators (`&&`, `||`, `==`, `!=`) [tests/unit_tests/core/foundation/store/filter/test_render_filters.py:32-110]().
*   **ChromaVectorStore**: Translates conditions into nested dictionary structures compatible with ChromaDB's `where` clauses, utilizing operators such as `$eq`, `$nin`, `$and`, and `$or` [tests/unit_tests/core/foundation/store/filter/test_render_filters.py:115-180]().
*   **GaussVectorStore**: Renders filters into SQL `WHERE` clauses. It incorporates strict identifier sanitization (`_validate_identifier`) against a Postgres identifier regex `^[A-Za-z_][A-Za-z0-9_]*$` to prevent SQL injection during dynamic column interpolation [jiuwen_memory/foundation/store/vector/gauss_vector_store.py:155-188]().
*   **ElasticsearchVectorStore**: Translates the filter tree into Elasticsearch query DSL query objects.

Sources: `jiuwen_memory/foundation/store/vector/gauss_vector_store.py`, `tests/unit_tests/core/foundation/store/filter/test_render_filters.py`, `jiuwen_memory/foundation/store/vector/es_vector_store.py`

---

# Page: Storage Codecs and Security

# Storage Codecs and Security

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jiuwen_memory/foundation/codec/__init__.py](jiuwen_memory/foundation/codec/__init__.py)
- [jiuwen_memory/foundation/codec/aes_storage_codec.py](jiuwen_memory/foundation/codec/aes_storage_codec.py)
- [jiuwen_memory/foundation/codec/codec_registry.py](jiuwen_memory/foundation/codec/codec_registry.py)
- [jiuwen_memory/foundation/codec/sm4_storage_codec.py](jiuwen_memory/foundation/codec/sm4_storage_codec.py)
- [jiuwen_memory/foundation/codec/storage_codec.py](jiuwen_memory/foundation/codec/storage_codec.py)
- [jiuwen_memory/foundation/store/base_message_store.py](jiuwen_memory/foundation/store/base_message_store.py)
- [tests/unit_tests/core/memory/codec/test_sm4_storage_codec.py](tests/unit_tests/core/memory/codec/test_sm4_storage_codec.py)

</details>



The storage codec framework provides a pluggable, transparent encryption layer for sensitive memory contents within the `jiuwen_memory.foundation.codec` package. It decouples cryptographic algorithms from core memory operations, allowing engines to securely persist memory document texts, variable values, and message payloads using either industry-standard AES-256-GCM or Chinese National Standard SM4-128-CBC encryption.

---

## 1. The `StorageCodec` Protocol Contract

To prevent circular import dependencies between storage modules and the heavy `memory_core` engine lifecycle, the encryption interface contract is defined in `[jiuwen_memory/foundation/codec/storage_codec.py]()`. 

`StorageCodec` is a runtime-checkable protocol (`@runtime_checkable`) requiring two primary methods: `encode(text)` and `decode(data)`. Conforming implementations must satisfy key architectural invariants:
- **Pass-through behavior**: Passing `None`, empty strings, or operating with an empty encryption key returns the payload unmodified.
- **Roundtrip consistency**: `decode(encode(x)) == x` must hold true for any string payload.
- **Payload encapsulation**: Encrypted output strings combine initialization vectors (IV) and ciphertexts into a self-contained string format.

```mermaid
graph TD
    A["MemoryEngineConfig"] -->|references codec name| B["CodecRegistry"]
    B -->|get storage codec| C["StorageCodec"]
    C -->|implemented by| D["AesStorageCodec"]
    C -->|implemented by| E["SM4StorageCodec"]
    D -->|encrypts via| F["CryptUtils"]
    E -->|encrypts via| G["CryptSM4"]

    sub-graph NaturalLanguageSpace
        H["EncryptionContract"] -->|realized by| C
    end
```

**Sources:**
- `[jiuwen_memory/foundation/codec/storage_codec.py:25-65]()`
- `[jiuwen_memory/foundation/codec/__init__.py:1-53]()`

---

## 2. Codec Registry Architecture

The engine manages available codecs through `CodecRegistry`, defined in `[jiuwen_memory/foundation/codec/codec_registry.py]`. Unlike factories that require deferred instantiation signatures, the registry stores **pre-built instances**. This design allows complex, multi-parameter initialization (such as Hardware Security Modules requiring certificates, slots, and PINs) to be handled entirely by the caller prior to registration.

```mermaid
graph TD
    A["CallerCode"] -->|instantiates with arbitrary args| B["CustomCodecInstance"]
    B -->|register_storage_codec name, instance| C["CodecRegistry"]
    C -->|lookup by name| D["EngineRuntime"]
    D -->|injects codec into index| E["BaseMemoryIndex"]
```

Key functions provided by the registry module include:
- `register_storage_codec(name, codec)`: Registers a pre-built codec instance onto the process-default registry [jiuwen_memory/foundation/codec/codec_registry.py:69-90]().
- `unregister_storage_codec(name)`: Removes a codec binding [jiuwen_memory/foundation/codec/codec_registry.py:93-94]().
- `CodecRegistry`: An isolated registry container class that can be instantiated independently during unit testing to avoid global state contamination [jiuwen_memory/foundation/codec/codec_registry.py:24-53]().

**Sources:**
- `[jiuwen_memory/foundation/codec/codec_registry.py:1-94]()`
- `[jiuwen_memory/foundation/codec/__init__.py:1-53]()`

---

## 3. Built-in Codecs: AES-256-GCM and SM4

Two built-in encryption codecs ship with the framework, supporting international and national cryptographic standards respectively.

### AES-256-GCM Codec
`AesStorageCodec` acts as a wrapper around the engine's internal cryptographic utility `CryptUtils` [jiuwen_memory/foundation/codec/aes_storage_codec.py:9-57](). It expects a 32-byte AES key and delegates encryption and decryption operations directly to the AES-GCM implementation.

### SM4-128-CBC Codec
`SM4StorageCodec` implements the Chinese National Standard SM4 algorithm using CBC mode and PKCS7 padding [jiuwen_memory/foundation/codec/sm4_storage_codec.py:30-177]().

```mermaid
graph LR
    P["PlaintextString"] -->|utf-8 encode| B["RawBytes"]
    B -->|_pkcs7_pad block_size_16| K["PaddedBytes"]
    I["SecretsTokenBytes16"] -->|CryptSM4 cbc encrypt| E["CiphertextBytes"]
    I -->|hex conversion| H1["IVHex"]
    E -->|hex conversion| H2["CiphertextHex"]
    H1 -->|concatenation| S["IVHexPlusCiphertextHex"]
    H2 --> S
```

Important implementation details for `SM4StorageCodec`:
- **Key Validation**: The initialization key `key` must be precisely 16 bytes (128 bits); otherwise, a `ValueError` is raised [jiuwen_memory/foundation/codec/sm4_storage_codec.py:45-58]().
- **Padding**: Explicit `_pkcs7_pad` and `_pkcs7_unpad` methods handle block alignment [jiuwen_memory/foundation/codec/sm4_storage_codec.py:60-95]().
- **Serialization Format**: Ciphertexts are stored as a concatenated hex string consisting of a 16-byte random initialization vector (IV) followed by the encrypted payload (`IV_hex + ciphertext_hex`) [jiuwen_memory/foundation/codec/sm4_storage_codec.py:40-43]().
- **Error Resilience**: Decryption failures or invalid ciphertexts log warnings via `memory_logger` and safely fall back to returning the raw input string [jiuwen_memory/foundation/codec/sm4_storage_codec.py:126-132, 171-177]().

Unit tests verifying roundtrip compliance, invalid key lengths, and padding edge cases are located at `[tests/unit_tests/core/memory/codec/test_sm4_storage_codec.py:10-166]()`.

**Sources:**
- `[jiuwen_memory/foundation/codec/aes_storage_codec.py:1-57]()`
- `[jiuwen_memory/foundation/codec/sm4_storage_codec.py:1-177]()`
- `[tests/unit_tests/core/memory/codec/test_sm4_storage_codec.py:1-166]()`

---

## 4. Store Injection and Lifecycle

Once registered, storage codecs are injected into underlying persistence stores (such as message stores, vector indexes, and markdown file stores) during engine initialization. 

Abstract base classes like `BaseMessageStore` define an optional injection hook `set_codec()` [jiuwen_memory/foundation/store/base_message_store.py:177-193](). Stores requiring encryption override this method to assign the codec to their internal persistence handlers, while unencrypted stores safely inherit a pass-through default.

**Sources:**
- `[jiuwen_memory/foundation/store/base_message_store.py:177-193]()`

---

# Page: LLM, Embedding and Prompt Layer

# LLM, Embedding and Prompt Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jiuwen_memory/common/utils/schema_utils.py](jiuwen_memory/common/utils/schema_utils.py)
- [jiuwen_memory/foundation/llm/model_clients/intelli_router_model_client.py](jiuwen_memory/foundation/llm/model_clients/intelli_router_model_client.py)
- [jiuwen_memory/foundation/llm/schema/config.py](jiuwen_memory/foundation/llm/schema/config.py)
- [jiuwen_memory/foundation/llm/schema/message_chunk.py](jiuwen_memory/foundation/llm/schema/message_chunk.py)

</details>



## Purpose and Scope
The LLM, Embedding and Prompt Layer provides the foundational abstraction, configuration schemas, resilient client wrappers (including multi-deployment load balancing via `intelli_router`), and streaming data chunk mechanisms for all language model interactions within the JiuwenMemory engine. This layer abstracts vendor-specific APIs (such as OpenAI, DashScope, DeepSeek, and SiliconFlow) into unified interfaces, manages streaming accumulation for chat completions and tool calls, and handles JSON schema to Pydantic validation transformations.

Sources:
- `jiuwen_memory/foundation/llm/schema/config.py:1-87`
- `jiuwen_memory/foundation/llm/model_clients/intelli_router_model_client.py:1-159`

---

## Model Abstraction and Configuration Schemas
The LLM foundation defines configuration and request options using Pydantic models. The `ProviderType` enumeration defines supported model providers and aggregation backends [jiuwen_memory/foundation/llm/schema/config.py:13-22] (`OpenAI`, `OpenRouter`, `SiliconFlow`, `DashScope`, `DeepSeek`, `InferenceAffinity`, `IntelliRouter`).

`ModelClientConfig` holds client-level parameters including `client_id`, `client_provider`, `api_key`, `api_base`, `timeout`, `max_retries`, and `verify_ssl` [jiuwen_memory/foundation/llm/schema/config.py:24-43]. A model validator `validate_client_provider` normalizes lowercase or mixed-case provider strings and verifies registration against built-in types or dynamic client registries [jiuwen_memory/foundation/llm/schema/config.py:45-78].

`ModelRequestConfig` manages runtime execution options such as `model_name` (aliased to `model`), `temperature`, `top_p`, `max_tokens`, and `stop` sequences [jiuwen_memory/foundation/llm/schema/config.py:80-87].

Sources:
- `jiuwen_memory/foundation/llm/schema/config.py:1-87`

---

## IntelliRouter Model Client and Resilient Routing
`IntelliRouterModelClient` extends `BaseModelClient` to wrap `intelli_router`'s `ReliableRouter` implementation [jiuwen_memory/foundation/llm/model_clients/intelli_router_model_client.py:12-79]. It supports API pooling where a single model name maps across multiple deployment endpoints, automated retries with fallback across deployments, and deployment health tracking.

Configurations are structured via `IntelliRouterClientConfig`, which extracts deployment lists, routing strategies (e.g., `simple-shuffle`), request timeouts, and health check intervals from extra fields in `ModelClientConfig` [jiuwen_memory/foundation/llm/model_clients/intelli_router_model_client.py:33-58].

To prevent redundant router instantiations, a module-level cache `_router_cache` maps an MD5 hash of the router configuration parameters to a shared `ReliableRouter` instance using a thread lock `_router_cache_lock` [jiuwen_memory/foundation/llm/model_clients/intelli_router_model_client.py:61-125].

```mermaid
title "IntelliRouter Initialization and Deployment Pooling"
graph TD
    A["ModelClientConfig"] --> B["IntelliRouterClientConfig.from_model_client_config"]
    B --> C["IntelliRouterModelClient._make_router_key"]
    C --> D{"_router_cache contains key?"}
    D -- "No" --> E["IntelliRouterModelClient._create_router"]
    E --> F["Deployment instances initialization"]
    F --> G["ReliableRouter instantiation"]
    G --> H["Store in _router_cache"]
    D -- "Yes" --> I["Retrieve cached ReliableRouter"]
    H --> J["IntelliRouterModelClient ready"]
    I --> J
```

Sources:
- `jiuwen_memory/foundation/llm/model_clients/intelli_router_model_client.py:1-159`

---

## Schema Utilities and Validation Framework
The `SchemaUtils` class handles bidirectional conversion between JSON Schema dictionaries and Pydantic models, data formatting, and schema validation [jiuwen_memory/common/utils/schema_utils.py:14-21].

Key functions include:
- `SchemaUtils.format_with_schema`: Cleans, validates, and formats input data against a JSON Schema or Pydantic `BaseModel` class [jiuwen_memory/common/utils/schema_utils.py:24-64].
- `SchemaUtils.remove_none_values`: Recursively strips `None` values from dictionaries and lists to ensure compliance with strict schemas [jiuwen_memory/common/utils/schema_utils.py:66-114].
- `SchemaUtils.validate_with_schema`: Performs validation using `jsonschema` or fallback Pydantic validation [jiuwen_memory/common/utils/schema_utils.py:116-142].
- `SchemaUtils.get_schema_dict` and `SchemaUtils.get_schema_class`: Convert back and forth between Pydantic models and JSON Schema dictionaries [jiuwen_memory/common/utils/schema_utils.py:144-178].

Sources:
- `jiuwen_memory/common/utils/schema_utils.py:1-178`

---

## Streaming Message Chunks and Accumulation
During streaming chat completions, token fragments and tool calls arrive incrementally. The foundation layer provides chunk abstractions and merging functions in `jiuwen_memory/foundation/llm/schema/message_chunk.py`.

`BaseMessageChunk` inherits from `BaseMessage` and implements the `__add__` operator to accumulate text or list contents between chunks [jiuwen_memory/foundation/llm/schema/message_chunk.py:132-149].

`AssistantMessageChunk` extends `AssistantMessage` and `BaseMessageChunk` to intelligently merge streaming tool calls (`ToolCall` objects), ensuring fragments of the same tool call index or matching IDs are concatenated correctly rather than appended as new separate calls [jiuwen_memory/foundation/llm/schema/message_chunk.py:151-181].

Helper merging utilities include:
- `merge_parser_content`: Intelligently merges parser contents based on types (concatenating strings/lists, recursively merging dictionaries or Pydantic models) [jiuwen_memory/foundation/llm/schema/message_chunk.py:12-61].
- `merge_dicts`: Recursively merges dictionary keys [jiuwen_memory/foundation/llm/schema/message_chunk.py:63-92].
- `merge_pydantic_models`: Merges two Pydantic model instances field by field [jiuwen_memory/foundation/llm/schema/message_chunk.py:95-130].

```mermaid
title "Streaming Chunk Accumulation Flow"
graph TD
    A["Incoming Stream Token Chunk"] --> B["BaseMessageChunk.__add__"]
    B --> C{"Content Type Check"}
    C -- "String/List" --> D["Concatenate content fragments"]
    C -- "Tool Call Fragment" --> E["AssistantMessageChunk.__add__"]
    E --> F["Match existing tool call ID or index"]
    F --> G["merge_parser_content / ToolCall arguments concatenation"]
    D --> H["Return combined chunk instance"]
    G --> H
```

Sources:
- `jiuwen_memory/foundation/llm/schema/message_chunk.py:1-181`

---

# Page: Servers and Interfaces

# Servers and Interfaces

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/en/API Docs/memory_server.md](docs/en/API Docs/memory_server.md)

</details>



## Purpose and Scope

The **Servers and Interfaces** subsystem (`jiuwen_memory.server`) bridges external consumers, AI agents, and platforms with the core memory engine. It provides standardized access channels so that HTTP clients, Model Context Protocol (MCP) compliant environments, and agent frameworks can ingest messages, execute semantic searches, manage variables, and perform administrative tasks. 

This parent page outlines the high-level architecture of the HTTP REST server, the MCP server, and the agent integration plugins. For comprehensive technical details, implementation steps, and endpoint references, refer to the child pages:
- For REST API routing, startup sequence, and configuration, see [REST Memory Server](#4.1).
- For Model Context Protocol tools and transports, see [MCP Server](#4.2).
- For agent lifecycle hooks and platform plugins, see [Agent Memory Plugins](#4.3).

---

## 4.1 REST Memory Server

The REST Memory Server is a FastAPI-based web service that exposes the core `LongTermMemory` capabilities over HTTP [docs/en/API Docs/memory_server.md:1-3](). It handles environment-driven backend assembly through `server.store_factory` [docs/en/API Docs/memory_server.md:96-98](), registers embedding models, and manages optional Bearer Token authentication via `MEMORY_API_KEY` [docs/en/API Docs/memory_server.md:5-11]().

The application can be booted via the entrypoint script `memory-server` defined in project metadata or directly as a Python module [docs/en/API Docs/memory_server.md:16-39]().

```mermaid
graph TD
    UserReq[""HTTP Request (Client)""] -->|"POST /messages, GET /search"| FastApiApp[""jiuwen_memory.server.memory_server:main""]
    FastApiApp -->|"Assembles Backends"| StoreFactory[""server.store_factory""]
    FastApiApp -->|"Invokes Engine"| LongTermMemory[""LongTermMemory API""]
    StoreFactory -->|"Initializes"| Storage[""KV / DB / Vector Backends""]

    subgraph CodeEntitySpace
        FastApiApp
        StoreFactory
        LongTermMemory
        Storage
    end

    subgraph NaturalLanguageSpace
        UserReq
    end
```
*Figure 1: REST Memory Server request and initialization flow.*

For detailed information on startup pipelines, security middleware, environment variable priorities (`~/.jiuwenmemory/.env`), and admin/reload endpoints, see [REST Memory Server](#4.1).

Sources: `docs/en/API Docs/memory_server.md:1-44`

---

## 4.2 MCP Server

The Model Context Protocol (MCP) server enables LLM applications and MCP-compatible agent frameworks to interact natively with the JiuwenMemory engine. It exposes standardized tools for storing conversations, retrieving context, and searching long-term memories without requiring custom REST integration code.

The MCP server relies on standard environment variables to configure default users, scopes, and transport mechanisms (such as Stdio or SSE).

For detailed information on exposed tools, transport implementations, and environment configuration, see [MCP Server](#4.2).

```mermaid
graph TD
    McpClient[""MCP Host / LLM Client""] -->|"Stdio / SSE Transport"| McpServer[""jiuwen_memory.server.memory_mcp""]
    McpServer -->|"Executes Tool Calls"| Engine[""LongTermMemory Engine""]

    subgraph CodeEntitySpace
        McpServer
        Engine
    end

    subgraph NaturalLanguageSpace
        McpClient
    end
```
*Figure 2: MCP Server communication and tool execution flow.*

Sources: `docs/en/API Docs/memory_server.md:1-25`

---

## 4.3 Agent Memory Plugins

The `agent-memory-plugin` directory contains integration packages and skill scripts designed to embed JiuwenMemory directly into popular agent runtimes and development frameworks. These plugins hook into agent lifecycles (such as initialization, message pre-processing, and post-execution summary generation) to provide automated memory persistence and retrieval.

Key integrations include:
- OpenClaw lifecycle hooks for session state management.
- Hermes plugin bindings for conversational context injection.
- Code agent utility scripts and skill extensions.

For detailed instructions on installing, configuring, and extending these plugins, see [Agent Memory Plugins](#4.3).

```mermaid
graph TD
    AgentRuntime[""Agent Runtime (OpenClaw / Hermes)""] -->|"Lifecycle Hook"| Plugin[""agent-memory-plugin""]
    Plugin -->|"API / SDK Call"| MemoryEngine[""LongTermMemory / Server""]

    subgraph CodeEntitySpace
        Plugin
        MemoryEngine
    end

    subgraph NaturalLanguageSpace
        AgentRuntime
    end
```
*Figure 3: Agent lifecycle plugin integration architecture.*

Sources: `docs/en/API Docs/memory_server.md:1-12`

---

# Page: REST Memory Server

# REST Memory Server

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/en/API Docs/memory_server.md](docs/en/API Docs/memory_server.md)
- [jiuwen_memory/memory_core/long_term_memory.py](jiuwen_memory/memory_core/long_term_memory.py)
- [jiuwen_memory/server/memory_server.py](jiuwen_memory/server/memory_server.py)

</details>



## Purpose and Scope

The `REST Memory Server` component (`server.memory_server`) serves as the primary HTTP service gateway for JiuwenMemory. Built on top of FastAPI, it exposes the capabilities of the core `LongTermMemory` engine via standard RESTful endpoints, allowing external services and agents to perform message ingestion, semantic search, variable management, and memory maintenance over HTTP [docs/en/API Docs/memory_server.md:1-12](). 

This page provides a high-level parent overview of the FastAPI application structure, its startup pipeline, environment configuration, authentication middleware, and administrative control flows. For specific subsystem details, refer to the child pages:
- For backend initialization and store creation, see [Store Factory and Backend Selection](#4.1.1).
- For administrative, configuration center, and logging endpoints, see [Admin, Config Center and Log Center APIs](#4.1.2).

Sources: `jiuwen_memory/server/memory_server.py`, `docs/en/API Docs/memory_server.md`

---

## Startup Pipeline and Environment Configuration

The server initializes by locating and loading environment variables from a tiered fallback sequence: first checking `~/.jiuwenmemory/.env`, and second checking the current working directory `.env` [jiuwen_memory/server/memory_server.py:39-64](). If neither exists, the application automatically provisions the `~/.jiuwenmemory/` directory [jiuwen_memory/server/memory_server.py:55-63]().

```mermaid
graph TD
    Start(["Start Application"]) --> LoadEnv["_load_env()"]
    LoadEnv --> CheckHome{"~/.jiuwenmemory/.env exists?"}
    CheckHome -- Yes --> ReadHome["load_dotenv(home_env)"]
    CheckHome -- No --> CheckCwd{"CWD/.env exists?"}
    CheckCwd -- Yes --> ReadCwd["load_dotenv(cwd_env)"]
    CheckCwd -- No --> CreateDir["Create ~/.jiuwenmemory/"]
    ReadHome --> ValidateIP["Validate Bind IP & MEMORY_API_KEY"]
    ReadCwd --> ValidateIP
    CreateDir --> ValidateIP
    ValidateIP --> BuildStores["create_async_engine_from_env()"]
    BuildStores --> RunFastAPI["FastAPI App Startup"]

    classDef default fill:#fff,stroke:#333,stroke-width:2px;
```
*Figure 1: Startup and Environment Loading Pipeline.*

Sources: `jiuwen_memory/server/memory_server.py:39-76`, `docs/en/API Docs/memory_server.md:64-72`

---

## Authentication and Security Middleware

Security enforcement is handled at startup and via request-level dependency checks. When binding to a non-local network address (i.e., any IP other than `127.0.0.1` or `localhost`), the server enforces that `MEMORY_API_KEY` is explicitly configured [docs/en/API Docs/memory_server.md:61-62](). If omitted, the initialization sequence aborts immediately to prevent unauthenticated network exposure.

Requests entering protected endpoints undergo Bearer token validation against the active `MEMORY_API_KEY`. If authentication is left unconfigured (empty string), token checks are bypassed for local development convenience [docs/en/API Docs/memory_server.md:79-81]().

```mermaid
graph TD
    Req["Incoming HTTP Request"] --> AuthCheck{"Is MEMORY_API_KEY Configured?"}
    AuthCheck -- No --> Allow["Bypass Auth (Local Dev)"]
    AuthCheck -- Yes --> ExtractToken["Extract Authorization: Bearer Token"]
    ExtractToken --> Match{"Token matches MEMORY_API_KEY?"}
    Match -- Yes --> Pass["Proceed to Endpoint Handler"]
    Match -- No --> Reject["HTTP 401 Unauthorized"]

    classDef default fill:#fff,stroke:#333,stroke-width:2px;
```
*Figure 2: Request Authentication Flow.*

Sources: `jiuwen_memory/server/memory_server.py:117-120`, `docs/en/API Docs/memory_server.md:61-81`

---

## Core REST Endpoints and Routing

The FastAPI application maps incoming HTTP routes to core memory engine operations. The service handles data mutations such as message addition and unit extraction, alongside search retrieval tasks [docs/en/API Docs/memory_server.md:5-10]().

```mermaid
graph LR
    Client["HTTP Client"] -->|"/api/v1/messages/add"| AddMsg["Add Messages Endpoint"]
    Client -->|"/api/v1/memory/search"| SearchMem["Search Manager Endpoint"]
    Client -->|"/api/v1/memory/update"| UpdateMem["Update Memory Endpoint"]
    Client -->|"/api/v1/variables"| Vars["Variable Management"]

    AddMsg --> LTM["LongTermMemory Engine"]
    SearchMem --> LTM
    UpdateMem --> LTM
    Vars --> LTM

    classDef default fill:#fff,stroke:#333,stroke-width:2px;
```
*Figure 3: Core API Routing to `LongTermMemory`.*

Sources: `jiuwen_memory/server/memory_server.py:1-176`, `docs/en/API Docs/memory_server.md:1-12`

---

## Admin, Reload, and Restart Operations

To support dynamic configuration adjustments without process termination, the server implements a concurrency-safe reload mechanism managed via an asynchronous lock (`_reload_lock`) [jiuwen_memory/server/memory_server.py:36-118](). 

The `_reload_memory_engine` function follows a safe-swap protocol:
1. Instantiates new storage backends and configurations from the updated `.env` state while the current engine continues processing active requests [jiuwen_memory/server/memory_server.py:103-162]().
2. Atomically swaps the global singletons and stops outdated background file watchers to prevent thread leaks [jiuwen_memory/server/memory_server.py:117-127]().

Sources: `jiuwen_memory/server/memory_server.py:36-176`

---

## Sub-Topics and Child Pages

For more granular technical information, please refer to the following child documentation pages:
- **Store Factory and Backend Selection**: Detailed breakdown of environment-driven engine assembly, SQLite WAL configurations, lazy imports, and vector/KV store bindings. See [Store Factory and Backend Selection](#4.1.1).
- **Admin, Config Center and Log Center APIs**: Comprehensive coverage of metadata management, configuration center integrations, and log monitoring endpoints. See [Admin, Config Center and Log Center APIs](#4.1.2).

---

# Page: Store Factory and Backend Selection

# Store Factory and Backend Selection

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jiuwen_memory/foundation/store/base_kv_store.py](jiuwen_memory/foundation/store/base_kv_store.py)
- [jiuwen_memory/foundation/store/kv/in_memory_kv_store.py](jiuwen_memory/foundation/store/kv/in_memory_kv_store.py)
- [jiuwen_memory/foundation/store/kv/shelve_store.py](jiuwen_memory/foundation/store/kv/shelve_store.py)
- [jiuwen_memory/memory_core/common/distributed_lock.py](jiuwen_memory/memory_core/common/distributed_lock.py)
- [jiuwen_memory/memory_core/manage/mem_model/scope_user_mapping_manager.py](jiuwen_memory/memory_core/manage/mem_model/scope_user_mapping_manager.py)
- [jiuwen_memory/memory_core/manage/mem_model/sql_db_store.py](jiuwen_memory/memory_core/manage/mem_model/sql_db_store.py)
- [jiuwen_memory/memory_core/migration/migrator/memory_meta_manager.py](jiuwen_memory/memory_core/migration/migrator/memory_meta_manager.py)
- [jiuwen_memory/server/store_factory.py](jiuwen_memory/server/store_factory.py)
- [tests/unit_tests/core/memory/manage/mem_model/test_sql_db_store.py](tests/unit_tests/core/memory/manage/mem_model/test_sql_db_store.py)

</details>



The purpose of this page is to detail the environment-driven creation of engines, Key-Value (KV) stores, relational database (DB) stores, and vector stores within `jiuwen_memory`. It covers SQLite WAL tuning strategies for high concurrency, directory resolution rules, and lazy-import mechanisms that isolate optional third-party vector store dependencies.

---

## 1. Environment-Driven Engine Creation and SQLite WAL Tuning

The server initialization process relies on environment variables to construct the underlying SQLAlchemy asynchronous database engine. This is handled centrally by `create_async_engine_from_env()`, which sets up connection pooling and configures database dialects [jiuwen_memory/server/store_factory.py:48-115]().

Directories for memory data are resolved via `_data_dir()` (defaulting to `~/.jiuwenmemory/memory_data`) and `create_file_root_dir()` (defaulting to `~/.jiuwenmemory/file_memory_data`), ensuring explicit directory creation even if environment variables are left blank [jiuwen_memory/server/store_factory.py:20-45]().

When operating on SQLite, standard asynchronous configurations are insufficient for high-concurrency workloads. `create_async_engine_from_env()` applies critical SQLite configurations:
- Uses `poolclass = pool.NullPool` with aiosqlite [jiuwen_memory/server/store_factory.py:86-87]().
- Sets `connect_args={"timeout": 30, "check_same_thread": False}` to expand the writer lock wait threshold and bypass thread safety checks [jiuwen_memory/server/store_factory.py:83-85]().
- Registers a connection-level SQLite event listener that enforces `PRAGMA journal_mode=WAL`, `PRAGMA synchronous=NORMAL`, and `PRAGMA busy_timeout=30000` on every new connection [jiuwen_memory/server/store_factory.py:101-114]().

```mermaid
graph TD
    Env["Env: DB_URL / MEMORY_DATA_DIR"] --> EngineFunc["create_async_engine_from_env()"]
    EngineFunc --> CheckSqlite{"Is SQLite?"}
    CheckSqlite -->|Yes| SqliteSetup["NullPool + connect_args(timeout=30)"]
    CheckSqlite -->|No| GaussSetup["QueuePool (pool_size=20, max_overflow=40)"]
    SqliteSetup --> EventListener["event.listens_for(sync_engine, 'connect')"]
    EventListener --> Pragmas["PRAGMA journal_mode=WAL \n PRAGMA synchronous=NORMAL \n PRAGMA busy_timeout=30000"]
    Pragmas --> FinalEngine["AsyncEngine Instance"]
    GaussSetup --> FinalEngine
```
*Sources: [jiuwen_memory/server/store_factory.py:20-115]()*

---

## 2. KV Store and DB Store Factories

The system abstracts storage instantiation behind factory functions that parse environment configurations.

- **KV Store Factory**: `create_kv_store(engine)` reads `KV_STORE_TYPE` (supporting `db`, `in_memory`, and `shelve`) [jiuwen_memory/server/store_factory.py:118-144](). The `db` type instantiates `DbBasedKVStore` bound to the shared `AsyncEngine`, `in_memory` uses `InMemoryKVStore` [jiuwen_memory/foundation/store/kv/in_memory_kv_store.py:18](), and `shelve` instantiates `ShelveStore` [jiuwen_memory/foundation/store/kv/shelve_store.py:30]() with `KV_SHELVE_PATH`.
- **DB Store Factory**: `create_db_store(engine)` reads `DB_STORE_TYPE` (supporting `default` and `gauss`) [jiuwen_memory/server/store_factory.py:147-168](). It returns either `DefaultDbStore` or `GaussDbStore`.

```mermaid
graph TD
    EnvKV["Env: KV_STORE_TYPE"] --> KVFactory["create_kv_store(engine)"]
    KVFactory -->|db| DbKV["DbBasedKVStore"]
    KVFactory -->|in_memory| MemKV["InMemoryKVStore"]
    KVFactory -->|shelve| ShelveKV["ShelveStore"]

    EnvDB["Env: DB_STORE_TYPE"] --> DBFactory["create_db_store(engine)"]
    DBFactory -->|default| DefaultDB["DefaultDbStore"]
    DBFactory -->|gauss| GaussDB["GaussDbStore"]
```
*Sources: [jiuwen_memory/server/store_factory.py:118-168](), [jiuwen_memory/foundation/store/kv/in_memory_kv_store.py:18-21](), [jiuwen_memory/foundation/store/kv/shelve_store.py:30-48]()*

---

## 3. Lazy Imports and Vector Store Backend Selection

To prevent third-party dependency bloat (such as `pymilvus` or `elasticsearch`) from breaking core startup when unused, `create_vector_store()` uses lazy imports [jiuwen_memory/server/store_factory.py:170-184](). 

The function inspects `VECTOR_STORE_TYPE` and imports the specific vector store module on demand. If a package is missing, only the selected execution branch fails, ensuring default deployments using `chroma` start cleanly.

```mermaid
graph TD
    EnvVec["Env: VECTOR_STORE_TYPE"] --> VecFactory["create_vector_store()"]
    VecFactory -->|chroma| ChromaBranch["import ChromaVectorStore \n Return ChromaVectorStore"]
    VecFactory -->|milvus| MilvusBranch["import pymilvus \n Return MilvusVectorStore"]
    VecFactory -->|elasticsearch| ESBranch["import elasticsearch \n Return ElasticsearchVectorStore"]
    VecFactory -->|gauss| GaussBranch["import gauss vector dialect \n Return GaussVectorStore"]
```
*Sources: [jiuwen_memory/server/store_factory.py:170-184]()*

---

## 4. Execution Integration with SqlDbStore

Once the database engine and store abstractions are generated by the factory methods, they are wrapped by high-level data managers such as `SqlDbStore`, which handles dialect-specific upserts and atomic operations for metadata and scope mappings [jiuwen_memory/memory_core/manage/mem_model/sql_db_store.py:21-68]().

| Component | Code Entity | Role |
| :--- | :--- | :--- |
| Store Factory | `jiuwen_memory.server.store_factory` | Parses environment variables to provision engines, KV, DB, and vector stores [jiuwen_memory/server/store_factory.py:1-184]() |
| Database Abstraction | `jiuwen_memory.foundation.store.base_db_store.BaseDbStore` | Base contract for relational storage backends [jiuwen_memory/foundation/store/base_db_store.py:1](). |
| SQL Wrapper | `jiuwen_memory.memory_core.manage.mem_model.sql_db_store.SqlDbStore` | Provides dialect-aware `write()` and `insert_or_update()` operations [jiuwen_memory/memory_core/manage/mem_model/sql_db_store.py:21-168]() |
| Metadata Manager | `jiuwen_memory.memory_core.migration.migrator.memory_meta_manager.MemoryMetaManager` | Manages schema version tracking tables using `SqlDbStore` [jiuwen_memory/memory_core/migration/migrator/memory_meta_manager.py:7-46]() |

*Sources: [jiuwen_memory/server/store_factory.py:1-184](), [jiuwen_memory/memory_core/manage/mem_model/sql_db_store.py:21-168](), [jiuwen_memory/memory_core/migration/migrator/memory_meta_manager.py:7-46]()*

---

# Page: Admin, Config Center and Log Center APIs

# Admin, Config Center and Log Center APIs

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jiuwen_memory/foundation/store/base_memory_index.py](jiuwen_memory/foundation/store/base_memory_index.py)
- [jiuwen_memory/memory_core/manage/mem_meta/__init__.py](jiuwen_memory/memory_core/manage/mem_meta/__init__.py)
- [jiuwen_memory/memory_core/manage/mem_meta/manager.py](jiuwen_memory/memory_core/manage/mem_meta/manager.py)
- [jiuwen_memory/memory_core/manage/search/search_manager.py](jiuwen_memory/memory_core/manage/search/search_manager.py)
- [jiuwen_memory/server/config_center_api.py](jiuwen_memory/server/config_center_api.py)
- [jiuwen_memory/server/log_center_api.py](jiuwen_memory/server/log_center_api.py)
- [jiuwen_memory/server/mem_meta_api.py](jiuwen_memory/server/mem_meta_api.py)
- [tests/unit_tests/server/test_mem_meta_endpoints.py](tests/unit_tests/server/test_mem_meta_endpoints.py)

</details>



## Purpose and Scope
This page details the implementation, routing logic, and data flows of the administrative, configuration, and logging subsystems within the JiuwenMemory REST server. These modules—`mem_meta_api`, `config_center_api`, and `log_center_api`—expose administrative control planes that bridge the agent platform console with the Python memory engine (`LongTermMemory`) [jiuwen_memory/server/mem_meta_api.py:1-12](), [jiuwen_memory/server/config_center_api.py:1-13](), [jiuwen_memory/server/log_center_api.py:1-12]().

---

## 1. Memory Metadata & Batch Deletion Administration (`mem_meta_api`)

The `mem_meta_api` module provides asynchronous governance tools for tracking user memory statistics and executing bulk purges of expired or blacklisted memories [jiuwen_memory/server/mem_meta_api.py:1-12](). All endpoints are prefixed with `/admin/mem_meta` and rely on `MemMetaManager` [jiuwen_memory/server/mem_meta_api.py:28-85]().

### Core Endpoints and Pydantic Models

| Endpoint | Method | Request Model | Response Code | Description |
| :--- | :--- | :--- | :--- | :--- |
| `/admin/mem_meta/refresh` | `POST` | `RefreshRequest` | `202 Accepted` / `200 OK` | Asynchronously refreshes user metadata and stats tables [jiuwen_memory/server/mem_meta_api.py:35-40, 95-105](). |
| `/admin/mem_meta/expired_memorys` | `POST` | `ExpiredMemorysRequest` | `200 OK` | Synchronously queries Top $N$ users exceeding inactivity thresholds [jiuwen_memory/server/mem_meta_api.py:42-49, 108-114](). |
| `/admin/mem_meta/batch_delete` | `POST` | `BatchDeleteRequest` | `202 Accepted` | Submits an asynchronous batch deletion task for expired user data [jiuwen_memory/server/mem_meta_api.py:51-62, 117-143](). |
| `/admin/mem_meta/task_status` | `GET` | Query Parameter (`task_id`) | `200 OK` / `404 Not Found` | Queries progress, status, and summaries of background tasks [jiuwen_memory/server/mem_meta_api.py:146-155](). |

### `MemMetaManager` Persistence Schema
`MemMetaManager` interacts with two primary SQLAlchemy tables managed via an abstract `BaseDbStore` layer supporting SQLite, GaussDB, and PostgreSQL [jiuwen_memory/memory_core/manage/mem_meta/manager.py:9-11, 78-111]():
1. **`av_user_stats`**: Stores aggregated counts per `scope_user`, tracking `total_count`, `active_count`, `superseded_count`, `expired_30d_count`, and memory tiers (`tier_episodic`, `tier_semantic`) [jiuwen_memory/memory_core/manage/mem_meta/manager.py:78-91]().
2. **`mem_meta_task`**: Tracks asynchronous background tasks with state machines (`pending`, `running`, `completed`, `failed`), holding execution parameters and deleted counts [jiuwen_memory/memory_core/manage/mem_meta/manager.py:93-111]().

### Diagram: Metadata Refresh and Batch Deletion Data Flow
```mermaid
sequenceDiagram
    autonumber
    participant Client as "Platform Console"
    participant API as "mem_meta_api.router"
    participant Manager as "MemMetaManager"
    participant DB as "BaseDbStore / AsyncEngine"

    Client->>API: POST /admin/mem_meta/refresh (force=False)
    API->>Manager: submit_refresh(force=False)
    Manager->>Manager: Check COOLDOWN_SECONDS & active locks
    alt Cooldown Active or Task Running
        Manager-->>API: {"status": "skipped"}
        API-->>Client: 200 OK (Skipped)
    else Accepted
        Manager-->>API: {"status": "accepted", "task_id": "tid-001"}
        API-->>Client: 202 Accepted
        Note over Manager,DB: Background Task Execution
        Manager->>DB: Scan collection & aggregate av_user_stats
    end
```
*Sources: [jiuwen_memory/server/mem_meta_api.py:95-105](), [jiuwen_memory/memory_core/manage/mem_meta/manager.py:33-187]()*, [tests/unit_tests/server/test_mem_meta_endpoints.py:33-48]()

---

## 2. Configuration Center & Dynamic Engine Control (`config_center_api`)

The `config_center_api` module exposes dynamic inspection and mutation capabilities for server architecture, engine parameters, scope configurations, and Dreaming workflows [jiuwen_memory/server/config_center_api.py:1-13]().

### Configuration Taxonomy
Parameters are categorized to prevent unsafe mutations of core architectural bindings while allowing operational tuning:
* **`ARCHITECTURE_PARAMS`**: Immutable runtime bindings such as `IP`, `PORT`, `MEMORY_DATA_DIR`, and store type selectors (`KV_STORE_TYPE`, `DB_STORE_TYPE`, `VECTOR_STORE_TYPE`) [jiuwen_memory/server/config_center_api.py:33-42]().
* **`EDITABLE_ENV_PARAMS`**: Hot-reloadable parameters including LLM providers (`MODEL_PROVIDER`, `API_KEY`, `MODEL_NAME`), embedding models, vector store URIs, and forgetting/dreaming intervals [jiuwen_memory/server/config_center_api.py:44-88]().
* **`SENSITIVE_KEYS`**: Fields masked during retrieval queries (e.g., API keys, passwords, bearer tokens) [jiuwen_memory/server/config_center_api.py:90-100]().

### CONFIG_SCHEMA Layout
The `CONFIG_SCHEMA` dictionary maps configuration categories to metadata schemas utilized by frontend consoles to render dynamic form controls [jiuwen_memory/server/config_center_api.py:113-162]():

```python
CONFIG_SCHEMA = {
    "runtime": { "ip": ..., "port": ..., "memory_api_key": ... },
    "storage": { "kv_store_type": ..., "db_url": ..., "index_backend": ... },
    "vector_engine": { "milvus_uri": ..., "es_hosts": ..., "gauss_host": ... },
    "engine": { "model_provider": ..., "embed_model_name": ..., "rerank_threshold": ... },
    ...
}
```
*Sources: [jiuwen_memory/server/config_center_api.py:113-162]()*

---

## 3. Log Center & Message Audit APIs (`log_center_api`)

The `log_center_api` module implements administrative monitoring and audit endpoints for both file-based execution logs and structured user messages stored in relational message stores [jiuwen_memory/server/log_center_api.py:1-12]().

### Structured Message Query and Export APIs
Users and administrators can query conversation memory logs via structured models [jiuwen_memory/server/log_center_api.py:38-62]():
* **`AdminMessageQueryRequest`**: Supports filtering by `scope_id`, `user_id`, `session_id`, time windows (`start_time`, `end_time`), offset pagination (`page_idx`, `page_size`), and scope blacklisting (`exclude_scopes`) [jiuwen_memory/server/log_center_api.py:38-47]().
* **`MessageExportParams`**: Consolidates parameters for bulk export operations [jiuwen_memory/server/log_center_api.py:49-62]().
* **Message Back-Reference (`/get_message_by_id/`)**: Allows downstream components to trace memory sources back to original dialogue chunks using `GetMessageByIdRequest` [jiuwen_memory/server/log_center_api.py:34-36, 130-146]().

### Diagram: Log Center and Message Audit Data Flow
```mermaid
sequenceDiagram
    autonumber
    participant UI as "Platform Web UI"
    participant Router as "log_center_api"
    participant Engine as "LongTermMemory"
    participant Store as "SqlMessageStore"

    UI->>Router: POST /admin/messages/query (AdminMessageQueryRequest)
    Router->>Engine: _message_store()
    Engine-->>Router: Returns SqlMessageStore instance
    Router->>Store: count_messages(message_filter)
    Store-->>Router: total count int
    Router->>Store: get_messages(filter, limit, offset)
    Store-->>Router: list[tuple[Message, Metadata]]
    Router->>Router: _message_to_dict() formatting
    Router-->>UI: 200 OK (total, page_idx, items)
```
*Sources: [jiuwen_memory/server/log_center_api.py:75-183]*

---

## Summary of Integration Interfaces

| Module File Path | Router Prefix | Primary Manager / Store | Key Responsibilities |
| :--- | :--- | :--- | :--- |
| `jiuwen_memory/server/mem_meta_api.py` [jiuwen_memory/server/mem_meta_api.py:1-155]() | `/admin/mem_meta` | `MemMetaManager` [jiuwen_memory/memory_core/manage/mem_meta/manager.py:117-122]() | Metadata sync, expiration analytics, asynchronous batch deletion tasks. |
| `jiuwen_memory/server/config_center_api.py` [jiuwen_memory/server/config_center_api.py:1-162]() | `/admin/config` (injected) | `MemoryScopeConfig`, Env variables [jiuwen_memory/server/config_center_api.py:27-88]() | Scope config hot-loading, Dreaming lifecycle control, environment variable mutation. |
| `jiuwen_memory/server/log_center_api.py` [jiuwen_memory/server/log_center_api.py:1-186]() | `/`, `/admin/messages` | `SqlMessageStore`, File I/O [jiuwen_memory/server/log_center_api.py:75-118]() | Execution log tailing/downloading, structured message query/stats/export, message back-reference. |

*Sources: [jiuwen_memory/server/mem_meta_api.py:1-155](), [jiuwen_memory/server/config_center_api.py:1-162](), [jiuwen_memory/server/log_center_api.py:1-186]()*

---

# Page: MCP Server

# MCP Server

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/en/API Docs/mcp_server.md](docs/en/API Docs/mcp_server.md)
- [jiuwen_memory/server/mcp_server.py](jiuwen_memory/server/mcp_server.py)
- [tests/unit_tests/server/test_mcp_server.py](tests/unit_tests/server/test_mcp_server.py)

</details>



## Purpose and Scope

The `jiuwen_memory.server.mcp_server` module provides a Model Context Protocol (MCP) server dedicated to long-term memory operations (`profile`, `semantic`, `episodic`, and `summary` CRUD) [jiuwen_memory/server/mcp_server.py:3-7](). It exposes tools directly to MCP-compatible clients (such as Claude Code, Codex, Cursor, and VS Code) [jiuwen_memory/server/mcp_server.py:9-10]() without requiring a separate HTTP gateway service [jiuwen_memory/server/mcp_server.py:12-15](). 

Unlike the REST memory server, the MCP server assembles a local `LongTermMemory` engine **in-process** via the SDK using the same KV, DB, Vector, and Embedding store assembly configuration [jiuwen_memory/server/mcp_server.py:12-15](). It is scoped strictly to long-term memory and does **not** expose variable management tools [jiuwen_memory/server/mcp_server.py:6-7]().

Sources: `jiuwen_memory/server/mcp_server.py:3-20`, `docs/en/API Docs/mcp_server.md:3-8`

---

## Environment Configuration and Default Scope/User

The MCP server initializes its configuration by loading environment files through a priority chain identical to the REST memory server [jiuwen_memory/server/mcp_server.py:35-36](). The environment loading sequence is managed by `_load_env()` [jiuwen_memory/server/mcp_server.py:62-80]():

1. `~/.jiuwenmemory/.env` (User-level configuration) [jiuwen_memory/server/mcp_server.py:59-67]()
2. `./.env` (Current working directory configuration) [jiuwen_memory/server/mcp_server.py:68-71]()

If neither environment file exists, the server creates the `~/.jiuwenmemory` directory and logs a warning [jiuwen_memory/server/mcp_server.py:72-77]().

### Configuration Variables

| Variable | Default | Description |
| --- | --- | --- |
| `MCP_TRANSPORT` | `http` | Transport protocol (`http`/`streamable-http` or `sse`) [docs/en/API Docs/mcp_server.md:81]() |
| `MCP_HOST` | `127.0.0.1` | Bind address for the MCP server [jiuwen_memory/server/mcp_server.py:32](), [docs/en/API Docs/mcp_server.md:82]() |
| `MCP_PORT` | `8765` | Port number for the MCP server [jiuwen_memory/server/mcp_server.py:32](), [docs/en/API Docs/mcp_server.md:83]() |
| `MCP_DEFAULT_USER_ID` | `__default__` | Default user identity context (`_DEFAULT_ID`) [jiuwen_memory/server/mcp_server.py:53-83]() |
| `MCP_DEFAULT_SCOPE_ID` | `__default__` | Default scope identity context (`_DEFAULT_ID`) [jiuwen_memory/server/mcp_server.py:53-84]() |

Identity values passed to tool invocations are sanitized via `_sanitize_id()` to ensure they contain no path traversal tokens (`/`, `\`) and conform to length constraints [jiuwen_memory/server/mcp_server.py:87-91]().

Sources: `jiuwen_memory/server/mcp_server.py:35-91`, `docs/en/API Docs/mcp_server.md:66-86`

---

## Transports and Startup Architecture

The MCP server supports two transport layers selected via the `MCP_TRANSPORT` environment variable [jiuwen_memory/server/mcp_server.py:22-33]():
- **Streamable HTTP** (`http` / `streamable-http`): Implements the persistent Streamable HTTP service spec at endpoint `/mcp` [jiuwen_memory/server/mcp_server.py:24-28]().
- **Server-Sent Events** (`sse`): Implements the persistent SSE service at endpoint `/sse` [jiuwen_memory/server/mcp_server.py:30]()

### Architecture Map: Transport to Code Entities

```mermaid
graph TD
    Client["MCPClient"] -->|"HTTP / SSE Request"| FastMCPInstance["FastMCPInstance"]
    subgraph "Code Entity Space"
        FastMCPInstance -->|"Invokes Entrypoint"| MainFunc["main() in mcp_server.py"]
        MainFunc -->|"Reads Env Config"| LoadEnv["_load_env()"]
        LoadEnv -->|"Configures Bind Address"| ServerTransport["MCP_TRANSPORT / MCP_HOST / MCP_PORT"]
        ServerTransport -->|"Lazy Instantiation"| EngineClass["_Engine"]
    end
```
Sources: `jiuwen_memory/server/mcp_server.py:22-37`, `docs/en/API Docs/mcp_server.md:18-64`, `tests/unit_tests/server/test_mcp_server.py:18-24`

---

## Lazy Initialization and Resilient Error Handling

To prevent startup blockage or crashes when storage backends or model credentials are misconfigured, the MCP server employs lazy initialization [jiuwen_memory/server/mcp_server.py:17-20](). 

The `_Engine` class manages the lifecycle of the in-process `LongTermMemory` instance [jiuwen_memory/server/mcp_server.py:120-128](). On the first tool invocation, `_Engine.initialize()` executes [jiuwen_memory/server/mcp_server.py:140-172]():
1. Constructs the async database engine via `create_async_engine_from_env()` [jiuwen_memory/server/mcp_server.py:156]()
2. Instantiates `kv_store`, `db_store`, and `vector_store` using storage factory methods [jiuwen_memory/server/mcp_server.py:157-159]()
3. Configures the embedding client using `APIEmbedding` and `EmbeddingConfig` [jiuwen_memory/server/mcp_server.py:160-166]()
4. Registers stores with `LongTermMemory` [jiuwen_memory/server/mcp_server.py:168-172]()

If initialization fails, the server remains running, and individual tool wrappers catch exceptions to return readable error dictionaries rather than crashing [jiuwen_memory/server/mcp_server.py:17-20]().

Sources: `jiuwen_memory/server/mcp_server.py:120-172`, `docs/en/API Docs/mcp_server.md:106-117`

---

## Exposed Tools API

The MCP server exposes seven core long-term memory tools through `FastMCP` [docs/en/API Docs/mcp_server.md:3-13](). Each tool wraps corresponding asynchronous methods on the `LongTermMemory` engine [tests/unit_tests/server/test_mcp_server.py:31-39]() with parameter sanitization, default identity fallback (`DEFAULT_USER_ID`, `DEFAULT_SCOPE_ID`), and JSON serialization [jiuwen_memory/server/mcp_server.py:83-114]().

### Tool Summary Table

| Tool Function | Engine Method Called | Description |
| --- | --- | --- |
| `add_messages` | `add_messages` | Ingests dialogue turns and extracts long-term profiles, semantic memories, and summaries [tests/unit_tests/server/test_mcp_server.py:35](), [tests/unit_tests/server/test_mcp_server.py:67-86]() |
| `search_memories` | `search_memories` | Performs vector and keyword search across long-term memory units [tests/unit_tests/server/test_mcp_server.py:35](), [tests/unit_tests/server/test_mcp_server.py:114-127]() |
| `search_history_summaries` | `search_history_summaries` | Searches conversation history summaries [tests/unit_tests/server/test_mcp_server.py:35](), [tests/unit_tests/server/test_mcp_server.py:140-151]() |
| `get_memories` | `get_memories` | Paginates and retrieves stored memory records by type and scope [tests/unit_tests/server/test_mcp_server.py:36](), [tests/unit_tests/server/test_mcp_server.py:157-169]() |
| `update_memory` | `update_memory` | Updates an existing memory record by `mem_id` [tests/unit_tests/server/test_mcp_server.py:36](), [tests/unit_tests/server/test_mcp_server.py:175-184]() |
| `delete_memory` | `delete_memory` | Deletes a specific memory record by `mem_id` [tests/unit_tests/server/test_mcp_server.py:36]() |
| `delete_all_memories` | `delete_all_memories` | Clears all memory records, protected by a confirmation flag guard [tests/unit_tests/server/test_mcp_server.py:5]() |

### Architecture Map: Natural Language Tool Space to Code Entities

```mermaid
graph TD
    NLSpace["Natural Language Tool Request"] -->|"Calls Tool"| ToolWrapper["mcp_server.add_messages / search_memories"]
    subgraph "Code Entity Space"
        ToolWrapper -->|"Validates IDs"| Sanitize["_sanitize_id()"]
        Sanitize -->|"Ensures Engine Ready"| EngineCheck["_get_engine()"]
        EngineCheck -->|"Delegates Call"| LTMInstance["LongTermMemory Instance"]
        LTMInstance -->|"Executes Core Operation"| EngineMethods["add_messages() / search_memories() / update_memory()"]
        EngineMethods -->|"Serializes Results"| DumpHelper["_dump() / _json()"]
    end
    DumpHelper -->|"JSON Response"| NLSpace
```
Sources: `jiuwen_memory/server/mcp_server.py:83-115`, `tests/unit_tests/server/test_mcp_server.py:31-184`, `docs/en/API Docs/mcp_server.md:3-13`

---

## Serialization and Data Flow

Result objects returned from the `LongTermMemory` engine are serialized via helper functions before being transmitted to MCP clients [jiuwen_memory/server/mcp_server.py:97-114]():
- `_dump(obj)`: Performs recursive JSON-friendly conversions [jiuwen_memory/server/mcp_server.py:97-110](). It inspects objects for a `.model_dump(mode="json")` method to seamlessly support Pydantic v2 models (such as `MemInfo`, `MemResult`, and memory units) [jiuwen_memory/server/mcp_server.py:105-109]().
- `_json(value)`: Serializes dictionary and list structures using `json.dumps` with `ensure_ascii=False` and a `str` fallback for unhandled types [jiuwen_memory/server/mcp_server.py:113-114]().

Sources: `jiuwen_memory/server/mcp_server.py:97-114`, `tests/unit_tests/server/test_mcp_server.py:27-30`

---

# Page: Agent Memory Plugins

# Agent Memory Plugins

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jiuwen_memory/agent-memory-plugin/JiuwenMemory-OpenClaw/README.md](jiuwen_memory/agent-memory-plugin/JiuwenMemory-OpenClaw/README.md)
- [jiuwen_memory/agent-memory-plugin/agent-memory1.0_skill/SKILL.md](jiuwen_memory/agent-memory-plugin/agent-memory1.0_skill/SKILL.md)
- [jiuwen_memory/agent-memory-plugin/agent-memory1.0_skill/scripts/run_memory_operation.py](jiuwen_memory/agent-memory-plugin/agent-memory1.0_skill/scripts/run_memory_operation.py)
- [jiuwen_memory/agent-memory-plugin/jiuwen_memory_hermes/README.md](jiuwen_memory/agent-memory-plugin/jiuwen_memory_hermes/README.md)
- [jiuwen_memory/agent-memory-plugin/jiuwen_memory_hermes/__init__.py](jiuwen_memory/agent-memory-plugin/jiuwen_memory_hermes/__init__.py)
- [jiuwen_memory/agent-memory-plugin/jiuwen_memory_hermes/_compat.py](jiuwen_memory/agent-memory-plugin/jiuwen_memory_hermes/_compat.py)
- [jiuwen_memory/agent-memory-plugin/jiuwen_memory_hermes/plugin.yaml](jiuwen_memory/agent-memory-plugin/jiuwen_memory_hermes/plugin.yaml)

</details>



The `agent-memory-plugin` directory contains lightweight, decoupled integrations that connect external AI agent frameworks—such as OpenClaw and Hermes Agent—as well as standalone skill scripts to the core `jiuwen_memory` server (`memory_server`). These plugins communicate via HTTP APIs, operating independently without requiring direct in-process SDK dependencies or complex event loop bindings in the host agent runtime.

Sources: [jiuwen_memory/agent-memory-plugin/jiuwen_memory_hermes/__init__.py:13-18](), [jiuwen_memory/agent-memory-plugin/agent-memory1.0_skill/SKILL.md:16-17]()

---

## 1. OpenClaw Lifecycle Plugin

The OpenClaw lifecycle plugin (`JiuwenMemory-OpenClaw`) integrates with OpenClaw via conversational hooks declared in `openclaw.json`. It intercepts the agent execution loop at conversation boundaries to inject recalled context prior to generation and capture conversation turns upon completion.

### Configuration and Conversation Access
To ensure both memory recall and memory writing function correctly, the OpenClaw configuration requires `hooks.allowConversationAccess` to be set to `true`. Without this setting, OpenClaw restricts access to conversation-end hooks, rendering the `add_messages` capture mechanism inactive while allowing `search_memory` to execute.

Key configuration fields managed in `openclaw.json` include:
- `baseUrl`: The target `memory_server` HTTP endpoint (default `http://127.0.0.1:8000`).
- `userId` and `scopeId`: Identifiers used for tenant and user-level memory isolation.
- `captureStrategy`: Determines how message turns are batched (e.g., `last_turn`).
- `threshold` and `num`: Controls vector similarity cutoff limits and top-k retrieval bounds.

```json
{
  "plugins": {
    "entries": {
      "openjiuwen-memory-index": {
        "enabled": true,
        "hooks": {
          "allowConversationAccess": true
        },
        "config": {
          "baseUrl": "http://127.0.0.1:8000",
          "userId": "openclaw-user",
          "scopeId": "openclaw-scope"
        }
      }
    }
  }
}
```

Sources: [jiuwen_memory/agent-memory-plugin/JiuwenMemory-OpenClaw/README.md:4-92]()

---

## 2. Hermes Agent Plugin (`jiuwen_memory_hermes`)

The `jiuwen_memory_hermes` package provides a deep integration for Hermes Agent, mirroring lifecycle events and injecting long-term memory into the agent context.

### Compatibility Layer and ABC (`_compat.py`)
The plugin isolates framework glue code in `jiuwen_memory_hermes/_compat.py`. It inspects the host runtime using `importlib.util.find_spec("agent.memory_provider")` to locate the native `MemoryProvider` base class. If the host environment is absent, it dynamically constructs a `MemoryProvider` ABC stub containing mandatory hooks (`name`, `is_available`, `initialize`, `get_tool_schemas`, `handle_tool_call`) and optional hook defaults (`prefetch`, `sync_turn`, `on_session_end`, `on_pre_compress`, `on_memory_write`) via `_build_abc()` [jiuwen_memory/agent-memory-plugin/jiuwen_memory_hermes/_compat.py:36-94].

Environment bootstrapping is handled by `preload_env()`, which reads configuration variables from `~/.jiuwenmemory/.env` and populates `os.environ` using `os.environ.setdefault()` so that shell-level overrides take precedence [jiuwen_memory/agent-memory-plugin/jiuwen_memory_hermes/_compat.py:103-121]. An `AuthGuard` class verifies secure transmission of bearer tokens across plaintext connections [jiuwen_memory/agent-memory-plugin/jiuwen_memory_hermes/_compat.py:161-163].

Sources: [jiuwen_memory/agent-memory-plugin/jiuwen_memory_hermes/_compat.py:36-163]()

### Hook Architecture and Tool Routing (`__init__.py`)
The main entry point `jiuwen_memory_hermes/__init__.py` implements the `MemoryProvider` interface, mapping Hermes agent events to `memory_server` endpoints using standard library `urllib` and background daemon threads to prevent blocking the LLM generation loop [jiuwen_memory/agent-memory-plugin/jiuwen_memory_hermes/__init__.py:13-18].

```mermaid
graph TD
    A[HermesAgentLoop] -->|prefetch/sync_turn| B[jiuwen_memory_hermes.__init__.py]
    B -->|HTTP POST add_messages/| C[memory_server.py]
    B -->|HTTP POST search_memory/| C
    B -->|HTTP POST search_user_history_summary/| C
    C -->|Vector/SQL Query| D[SimpleMemoryIndex]
```
*Figure 1: Hermes Plugin Integration Architecture mapping agent lifecycle hooks to `memory_server` endpoints.*

Sources: [jiuwen_memory/agent-memory-plugin/jiuwen_memory_hermes/__init__.py:10-84](), [jiuwen_memory/agent-memory-plugin/jiuwen_memory_hermes/README.md:10-84]()

Sources: [jiuwen_memory/agent-memory-plugin/jiuwen_memory_hermes/__init__.py:10-84](), [jiuwen_memory/agent-memory-plugin/jiuwen_memory_hermes/README.md:10-84]()

---

## 3. Skill Scripts and Standalone Operations (`agent-memory1.0_skill`)

The `agent-memory1.0_skill` directory implements standalone skill scripts executed via `call_mcp` tool commands. These scripts interface directly with the `agent-memory1.0` HTTP container (port `8517`) without relying on the `MemoryRail` framework.

### Circuit Breaker & File Persistence (`run_memory_operation.py`)
`run_memory_operation.py` implements robust failure handling through a file-backed circuit breaker and batch write buffer stored in `MEM1_STATE_DIR` (default `/tmp/mem1_skill_state`) [jiuwen_memory/agent-memory-plugin/agent-memory1.0_skill/scripts/run_memory_operation.py:23-75].

- **Circuit Breaker**: Tracks consecutive failures via `_record_failure()`. When failures meet or exceed `MEM1_CIRCUIT_BREAKER_THRESHOLD`, the breaker trips open until `MEM1_CIRCUIT_BREAKER_COOLDOWN` elapses, after which it automatically resets [jiuwen_memory/agent-memory-plugin/agent-memory1.0_skill/scripts/run_memory_operation.py:104-128].
- **Batch Write Buffer**: Appends messages to local JSONL files via `_buffer_append()`. When character counts exceed `MEM1_BUFFER_CHARS_THRESHOLD`, messages are automatically flushed to the server [jiuwen_memory/agent-memory-plugin/agent-memory1.0_skill/scripts/run_memory_operation.py:139-159].

```mermaid
graph TD
    A[AgentCallMCP] -->|run_memory_operation.py| B{_is_breaker_open}
    B -->|Open| C[Fail-Open Fallback]
    B -->|Closed| D[_buffer_append]
    D -->|Exceeds Threshold| E[Flush Buffer to Server]
    D -->|Direct API Call| F[urllib.request.urlopen]
    F -->|HTTP Error| G[_record_failure]
    F -->|Success| H[_record_success]
```
*Figure 2: Skill Operation & Resiliency Pipeline illustrating circuit breaker checks and buffer flushing logic.*

Sources: [jiuwen_memory/agent-memory-plugin/agent-memory1.0_skill/scripts/run_memory_operation.py:23-189]()

Sources: [jiuwen_memory/agent-memory-plugin/agent-memory1.0_skill/scripts/run_memory_operation.py:23-189]()

---

# Page: Agent Memory Platform (Management Console)

# Agent Memory Platform (Management Console)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [agent-memory-platform/platform/pom.xml](agent-memory-platform/platform/pom.xml)
- [agent-memory-platform/platform/src/main/resources/application.yml](agent-memory-platform/platform/src/main/resources/application.yml)

</details>



The Agent Memory Platform provides a centralized administrative and management console for the `agent-memory` system. Built as a modular Java Spring Boot application paired with a Vue 3 single-page application frontend, it offers comprehensive control over tenants, operational scopes, dynamic configurations, run-time logs, system audits, and engine operations. It acts as the orchestration layer between operators, developers, and the underlying Python-based `jiuwen_memory` engine [agent-memory-platform/platform/pom.xml:18]().

For detailed breakdowns of the underlying platform subsystems, refer to the child pages:
- [Platform Backend Services](#5.1)
- [Platform Web UI (Vue)](#5.2)

---

## 5.1 Platform Backend Services

The backend of the management console is built on Spring Boot 3.3.5 and structured as a modular monolith [agent-memory-platform/platform/pom.xml:10-18](). It aggregates several functional centers—including authentication, tenant management, scope handling, dynamic configuration, logging, and operational telemetry—under a unified server running on port `9000` [agent-memory-platform/platform/src/main/resources/application.yml:18](). 

Communication with the core Python memory service (defaulting to `http://127.0.0.1:8000`) is mediated by internal HTTP clients such as `MemoryEngineClient`, mapping Java control operations into REST calls [agent-memory-platform/platform/src/main/resources/application.yml:34-35](). Persistence is handled via MyBatis-Plus supporting multiple relational databases (SQLite, MySQL, GaussDB) configured through Spring active profiles [agent-memory-platform/platform/pom.xml:43-72](), [agent-memory-platform/platform/src/main/resources/application.yml:7]().

```mermaid
graph TD
    Client["VueFrontend(:5173)"] -->|HTTPS/REST| SecurityFilter["SpringSecurityFilter"]
    SecurityFilter -->|JWTValid| SpringRouter["SpringMVCController"]
    SpringRouter --> TenantSvc["TenantCenterModule"]
    SpringRouter --> ConfigSvc["ConfigCenterModule"]
    SpringRouter --> OpsSvc["OpsCenterModule"]
    OpsSvc --> EngineClient["MemoryEngineClient"]
    EngineClient -->|HTTP:8516| PythonEngine["MemoryServer(Python)"]

    sub: "Code Entity Space"
    classDef default stroke:#333,fill:none;
```
*Figure 5.1.1: High-level platform backend architecture mapping incoming requests from the frontend through security filters and service modules down to the Python engine client.*

For detailed implementations, security configurations, JWT validation filters, database migrations, and telemetry services, see [Platform Backend Services](#5.1).

Sources: 
- `agent-memory-platform/platform/pom.xml`
- `agent-memory-platform/platform/src/main/resources/application.yml`

---

## 5.2 Platform Web UI (Vue)

The management console frontend is a Vue 3 application that provides operators with graphical dashboards to manage system states. It includes dedicated views for configuration centers, tenant allocations, runtime log inspection, and operational commands. 

The UI communicates with the Spring Boot backend via typed API clients and state stores, backed on the server side by aggregator services that simplify cross-module data retrieval. 

```mermaid
graph TD
    User["Operator"] -->|Browser| VueRouter["VueRouter(:5173)"]
    VueRouter --> ConfigView["ConfigCenterView"]
    VueRouter --> TenantView["TenantManagerView"]
    VueRouter --> OpsView["OpsConsoleView"]
    ConfigView --> ApiClient["PlatformApiClient"]
    TenantView --> ApiClient
    OpsView --> ApiClient
    ApiClient -->|RESTAPI| SpringBoot["PlatformApplication(:9000)"]

    sub: "Code Entity Space"
    classDef default stroke:#333,fill:none;
```
*Figure 5.2.1: Frontend UI routing and API communication paths connecting Vue views via API clients to the platform backend.*

For detailed frontend architecture, component structures, state stores, and layout designs, see [Platform Web UI (Vue)](#5.2).

Sources: 
- `agent-memory-platform/platform/src/main/resources/application.yml`

---

# Page: Platform Backend Services

# Platform Backend Services

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/common/client/DefaultMemoryEngineClient.java](agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/common/client/DefaultMemoryEngineClient.java)
- [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/common/client/MemoryEngineClient.java](agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/common/client/MemoryEngineClient.java)
- [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/configcenter/service/impl/ConfigTemplateServiceImpl.java](agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/configcenter/service/impl/ConfigTemplateServiceImpl.java)
- [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/logcenter/service/LogCollectAsyncService.java](agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/logcenter/service/LogCollectAsyncService.java)
- [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/controller/FeatureFlagController.java](agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/controller/FeatureFlagController.java)
- [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/controller/OpsCommandController.java](agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/controller/OpsCommandController.java)
- [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/service/impl/GovernanceServiceImpl.java](agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/service/impl/GovernanceServiceImpl.java)
- [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/scopecenter/controller/ScopeRegistryController.java](agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/scopecenter/controller/ScopeRegistryController.java)
- [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/tenantcenter/controller/TenantController.java](agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/tenantcenter/controller/TenantController.java)
- [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/webui/service/impl/UiAggregatorServiceImpl.java](agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/webui/service/impl/UiAggregatorServiceImpl.java)

</details>



## Purpose and Scope

The `agent-memory-platform` backend services layer provides an enterprise-grade Java Spring Boot management console and API gateway for the JiuwenMemory system. It orchestrates multi-tenant environments, manages dynamic configurations, monitors runtime operations, collects logs, and securely bridges administrative interfaces to the Python-based Long-Term Memory core engine through a unified client abstraction.

Sources: 
- `agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/common/client/MemoryEngineClient.java:20-26`

---

## Core Spring Boot Modules & Engine Bridge

The platform backend is organized into specialized functional modules operating under a unified Spring Boot application context:

- **`authcenter`**: Manages authentication, JSON Web Tokens (JWT), security configuration, auth filters, token blacklists, and user services. For details, see [Auth Center and Security](#5.1.1).
- **`tenantcenter`**: Implements multi-tenant registration, lifecycle management, and tenant-to-scope mapping bindings via `TenantController` [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/tenantcenter/controller/TenantController.java:34-36] and `TenantService`.
- **`scopecenter`**: Handles namespace isolation registries, resource quotas, and scope validators via `ScopeRegistryController` [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/scopecenter/controller/ScopeRegistryController.java:19-21].
- **`configcenter`**: Provides hierarchical configuration templates (`ConfigTemplateServiceImpl`), instance-level singletons, and kernel synchronization models (`ConfigTemplateServiceImpl` [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/configcenter/service/impl/ConfigTemplateServiceImpl.java:64-65]).
- **`logcenter` & `opscenter`**: Collects runtime logs, audit logs, message logs, and processes administrative operations/governance workflows. For details, see [Log Center and Ops Center](#5.1.2).
- **`MemoryEngineClient` Bridge**: The HTTP communication layer (`DefaultMemoryEngineClient` [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/common/client/DefaultMemoryEngineClient.java:40-40]) that wraps REST calls over `RestClient` to connect the Java platform to the Python core engine endpoints (`:8516`) [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/common/client/DefaultMemoryEngineClient.java:28-28].

### Architecture Overview Diagram

```mermaid
graph TD
    subgraph "PlatformBackend"
        TC["TenantController"]
        SC["ScopeRegistryController"]
        CC["ConfigTemplateServiceImpl"]
        OG["GovernanceServiceImpl"]
        MEC["DefaultMemoryEngineClient"]
    end
    subgraph "PythonEngine"
        PY["MemoryServer(:8516)"]
    end
    TC --> MEC
    SC --> MEC
    CC --> MEC
    OG --> MEC
    MEC ==>|"RestClient HTTP POST/GET"| PY
```
Sources: 
- `agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/tenantcenter/controller/TenantController.java:34-36`
- `agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/scopecenter/controller/ScopeRegistryController.java:19-21`
- `agent-memory-platform/platform/src/main/java/com/openjiuwen.memory/common/client/DefaultMemoryEngineClient.java:28-44`

---

## Natural Language Space to Code Entity Space Mapping

The following diagram bridges high-level administrative concepts to their concrete Spring Boot controllers, services, and client communication interfaces within the codebase.

```mermaid
graph LR
    subgraph "NaturalLanguageSpace"
        A["TenantManagement"]
        B["ScopeIsolation"]
        C["ConfigTemplates"]
        D["EngineCommunication"]
    end
    subgraph "CodeEntitySpace"
        A1["TenantController"]
        B1["ScopeRegistryController"]
        C1["ConfigTemplateServiceImpl"]
        D1["DefaultMemoryEngineClient"]
    end
    A --> A1
    B --> B1
    C --> C1
    D --> D1
```
Sources:
- `agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/tenantcenter/controller/TenantController.java:34-36`
- `agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/scopecenter/controller/ScopeRegistryController.java:19-21`
- `agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/configcenter/service/impl/ConfigTemplateServiceImpl.java:64-65`
- `agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/common/client/DefaultMemoryEngineClient.java:40-44`

---

## Sub-Topics and Child Pages

### 5.1.1 Auth Center and Security
The `authcenter` module provides security infrastructure including JWT authentication providers, Spring Security filter chains, token blacklists, user management services, and request path/scope validators.
- For details, see [Auth Center and Security](#5.1.1).

### 5.1.2 Log Center and Ops Center
The `logcenter` and `opscenter` modules handle system diagnostics, asynchronous log packaging (`LogCollectAsyncService` [agent-memory-platform/platform/src/main/java/com/openjiuwen/logcenter/service/LogCollectAsyncService.java:40-41]), governance rule evaluations (`GovernanceServiceImpl` [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/service/impl/GovernanceServiceImpl.java:40-41]), remote command dispatching (`OpsCommandController` [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/controller/OpsCommandController.java:14-16]), and feature flag rollouts (`FeatureFlagController` [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/controller/FeatureFlagController.java:12-14]).
- For details, see [Log Center and Ops Center](#5.1.2).

### 5.1.3 Platform Persistence and Migrations
Platform persistence relies on Flyway schema migration scripts targeting MySQL, GaussDB, and SQLite, alongside multi-profile configuration application properties, schema compatibility initializers, and mock engine clients for testing.
- For details, see [Platform Persistence and Migrations](#5.1.3).

Sources:
- `agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/common/client/DefaultMemoryEngineClient.java:28-44`
- `agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/service/impl/GovernanceServiceImpl.java:40-41`
- `agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/controller/OpsCommandController.java:14-16`
- `agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/controller/FeatureFlagController.java:12-14`

---

# Page: Auth Center and Security

# Auth Center and Security

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/config/JwtTokenProvider.java](agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/config/JwtTokenProvider.java)
- [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/config/SecurityConfig.java](agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/config/SecurityConfig.java)
- [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/mapper/TokenBlacklistMapper.java](agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/mapper/TokenBlacklistMapper.java)
- [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/service/TokenBlacklistService.java](agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/service/TokenBlacklistService.java)
- [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/common/util/ScopeIdValidator.java](agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/common/util/ScopeIdValidator.java)

</details>



The **Auth Center and Security** module is a core subsystem of the `agent-memory-platform` management console. It provides stateless authentication via JSON Web Tokens (JWT), role-based and permission-based authorization filters, a token revocation blacklist with scheduled cleanup, and security configuration rules for public and protected endpoints. Additionally, it provides structural validators like `ScopeIdValidator` to ensure that parameters such as `scope_id` conform strictly to kernel specifications.

---

## 1. JWT Provider and Token Lifecycle

The `JwtTokenProvider` component handles the creation, parsing, validation, and claim extraction of JWT tokens [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/config/JwtTokenProvider.java:17-125](). It uses an HMAC-SHA signing key (`SECRET_KEY`) that requires a minimum of 256 bits [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/config/JwtTokenProvider.java:22-24]().

### Key Methods and Claims
- **`generateToken(String userId, String username, String role)`**: Constructs a JWT containing custom claims (`userId`, `username`, `role`), a unique JWT ID (`jti`) via `UUID.randomUUID()`, an issuance timestamp, and a 30-minute expiration window [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/config/JwtTokenProvider.java:36-50]().
- **Claim Extractors**: Methods like `getUserIdFromToken()`, `getUsernameFromToken()`, `getRoleFromToken()`, and `getJtiFromToken()` extract payloads safely through `getClaimsFromToken()` [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/config/JwtTokenProvider.java:53-90]().
- **`validateToken(String token)`**: Parses the token signature and verifies whether the token has expired [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/config/JwtTokenProvider.java:95-102]().

```mermaid
graph TD
    sub511_NaturalLanguage ["Client Authentication Request"] --> sub511_JwtProvider["JwtTokenProvider.generateToken()"]
    sub511_JwtProvider --> sub511_Token["JWT Token with jti, userId, role"]
    sub511_Token --> sub511_Parser["JwtTokenProvider.getClaimsFromToken()"]
    sub511_Parser --> sub511_Validation["JwtTokenProvider.validateToken()"]
    
    classDef default fill:#fff,stroke:#333,stroke-width:1px;
```
*Figure 5.1.1-1: JWT token generation and validation flow linking natural language steps to `JwtTokenProvider` methods.*

Sources: `agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/config/JwtTokenProvider.java`

---

## 2. Security Configuration and Filter Chain

The `SecurityConfig` class configures Spring Security to operate in a stateless, sessionless architecture appropriate for REST APIs [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/config/SecurityConfig.java:36-79](). 

### Configuration Highlights
- **Session Management**: Configured as `SessionCreationPolicy.STATELESS` [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/config/SecurityConfig.java:68-69]().
- **CSRF**: Disabled since authentication relies entirely on bearer tokens [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/config/SecurityConfig.java:67]().
- **Public Paths**: Dynamic parsing of comma-separated paths from the configuration property `platform.security.public-paths` (defaulting to login, register, info, logout, and refresh endpoints) [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/config/SecurityConfig.java:53-62]().
- **Filter Chain Ordering**:
  1. `JwtAuthenticationFilter` executes before `UsernamePasswordAuthenticationFilter` to extract credentials and populate the `SecurityContextHolder` [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/config/SecurityConfig.java:75]().
  2. `PermissionFilter` executes after `JwtAuthenticationFilter` for fine-grained authorization checks [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/config/SecurityConfig.java:76]().
- **Authentication Entry Point**: Returns an explicit HTTP `401 Unauthorized` status with a JSON error body when authentication fails, adhering to REST semantics [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/config/SecurityConfig.java:86-98]().

```mermaid
graph TD
    sub511_HttpRequest["HTTP Request"] --> sub511_SecurityConfig["SecurityConfig.securityFilterChain()"]
    sub511_SecurityConfig --> sub511_JwtFilter["JwtAuthenticationFilter"]
    sub511_JwtFilter --> sub511_PermFilter["PermissionFilter"]
    sub511_PermFilter --> sub511_Controller["Protected REST Controllers"]
    sub511_SecurityConfig --> sub511_EntryPoint["AuthenticationEntryPoint returns 401"]
    
    classDef default fill:#fff,stroke:#333,stroke-width:1px;
```
*Figure 5.1.1-2: Security filter chain execution routing from `SecurityConfig` to individual filter beans.*

Sources: `agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/config/SecurityConfig.java`

---

## 3. Token Blacklist and Logout Management

To handle user logouts and prevent token reuse before natural expiration, `TokenBlacklistService` manages a database-backed blacklist [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/service/TokenBlacklistService.java:18-77]().

### Mechanism
- **Revocation (`addToBlacklist`)**: Records the token's unique `jti`, full token string, username, and expiration timestamp into the repository via `TokenBlacklistMapper` [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/service/TokenBlacklistService.java:34-49](). It is idempotent and skips insertion if the `jti` already exists [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/service/TokenBlacklistService.java:38-41]().
- **Lookup (`isBlacklisted`)**: Checked during JWT validation filters to reject logged-out sessions [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/service/TokenBlacklistService.java:57-62]().
- **Scheduled Cleanup (`cleanExpiredTokens`)**: A Spring `@Scheduled` task executes every 30 minutes to purge expired token rows from the blacklist table where `expires_at` is older than the current time [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/service/TokenBlacklistService.java:68-76]().

Sources: `agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/service/TokenBlacklistService.java`, `agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/authcenter/mapper/TokenBlacklistMapper.java`

---

## 4. Scope and Path Validation

The `ScopeIdValidator` class validates scope identifiers to maintain consistency with the underlying Python memory engine's `_validate_id` rules [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/common/util/ScopeIdValidator.java:7-15]().

### Validation Rules
- **Non-Blank Constraint**: Throws a `BizException` with `ResultCode.BAD_REQUEST` if `scope_id` is null or blank [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/common/util/ScopeIdValidator.java:28-31]().
- **Slash Restriction**: Prohibits the forward slash character (`/`) because the kernel uses `/` as a delimiter for nested scope paths [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/common/util/ScopeIdValidator.java:32-34]().
- **Length Limit**: Enforces a strict maximum length of 128 characters [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/common/util/ScopeIdValidator.java:20,35-37]().

Sources: `agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/common/util/ScopeIdValidator.java`

---

# Page: Log Center and Ops Center

# Log Center and Ops Center

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/logcenter/controller/RuntimeLogController.java](agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/logcenter/controller/RuntimeLogController.java)
- [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/logcenter/service/impl/LogStatsServiceImpl.java](agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/logcenter/service/impl/LogStatsServiceImpl.java)
- [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/service/impl/MemoryManageServiceImpl.java](agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/service/impl/MemoryManageServiceImpl.java)
- [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/websocket/HeartbeatHandler.java](agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/websocket/HeartbeatHandler.java)

</details>



This page covers the architecture, controller implementations, and services for the **Log Center** and **Ops Center** within the `agent-memory-platform` Java Spring Boot backend. These modules handle runtime log streaming, file log management, log statistics, WebSocket heartbeat health monitoring, operational commands, and memory management services bridging the platform to the Python core engine.

---

## 1. Runtime and Message Log Controllers

The `agent-memory-platform` exposes log management through `RuntimeLogController`, bypassing local DB storage for runtime logs and instead querying the Python kernel engine directly via HTTP.

### Runtime Log Controller Implementation
`RuntimeLogController` provides endpoints for tailing runtime logs and listing or downloading log files from the kernel or platform storage [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/logcenter/controller/RuntimeLogController.java:37-152]().

*   `GET /api/v1/logs/runtime/tail`: Treads recent lines (`lines`, `level`, `event_type`, `source`). For `source=kernel`, it invokes `MemoryEngineClient.tailKernelLogs(...)`; for `source=platform`, it reads the local platform log via `PlatformLogReader` [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/logcenter/controller/RuntimeLogController.java:64-88]().
*   `GET /api/v1/logs/runtime/files`: Enumerates kernel or platform log files available for download, with optional date filtering (`start_date`, `end_date`) [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/logcenter/controller/RuntimeLogController.java:98-152]().

```mermaid
graph TD
    Client["Platform UI Client"] -->| "GET /api/v1/logs/runtime/tail" | RTC[RuntimeLogController]
    RTC -->| "source=kernel" | MEC[MemoryEngineClient]
    RTC -->| "source=platform" | PLR[PlatformLogReader]
    MEC -->| "HTTP /logs/tail" | PythonKernel["Python Memory Engine"]
    
    style RTC fill:none,stroke:#000,stroke-width:2px
    style MEC fill:none,stroke:#000,stroke-width:2px
    style PythonKernel fill:none,stroke:#000,stroke-width:2px
```
*Sources: [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/logcenter/controller/RuntimeLogController.java:37-152]()*.

---

## 2. Log Statistics Dashboard and Audit Filtering

The log statistics layer routes aggregate statistics based on log types via `LogStatsServiceImpl`.

### Log Stats Service
`LogStatsServiceImpl` implements `LogStatsService`, branching requests for `operations` and `messages` logs while explicitly rejecting `runtime` logs from database queries since runtime logs are transient and not stored in the relational database [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/logcenter/service/impl/LogStatsServiceImpl.java:19-81]().

```mermaid
graph TD
    LSS[LogStatsServiceImpl] -->| "logType=operations" | OLS[OperationLogService]
    LSS -->| "logType=messages" | MLS[MessageLogService]
    LSS -->| "logType=runtime" | Err[Throw IllegalArgumentException]
    
    style LSS fill:none,stroke:#000,stroke-width:2px
    style OLS fill:none,stroke:#000,stroke-width:2px
    style MLS fill:none,stroke:#000,stroke-width:2px
```
*Sources: [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/logcenter/service/impl/LogStatsServiceImpl.java:19-81]()*.

---

## 3. WebSocket Heartbeat Health Monitoring

Real-time connection monitoring and session maintenance are managed by `HeartbeatHandler`.

### Heartbeat Handler
`HeartbeatHandler` extends `TextWebSocketHandler` to maintain active client sessions, scheduling periodic heartbeats and cleaning up disconnected sessions [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/websocket/HeartbeatHandler.java:36-175]().

*   **Scheduled Execution**: Uses a single-threaded scheduled executor to broadcast heartbeat JSON frames every 5,000 milliseconds (`HEARTBEAT_INTERVAL_MS`) [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/websocket/HeartbeatHandler.java:40-57]().
*   **Session Lifecycle**: `afterConnectionEstablished` registers sessions and triggers an immediate heartbeat; `afterConnectionClosed` and IO exceptions remove stale sessions [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/websocket/HeartbeatHandler.java:60-108]().

```mermaid
sequenceDiagram
    participant UI as Vue Frontend
    participant HH as HeartbeatHandler
    participant SES as ScheduledExecutorService

    SES->>HH: "broadcastHeartbeat() (every 5s)"
    HH->>UI: "TextMessage (heartbeat json)"
    UI->>HH: "TextMessage ('ping') [optional]"
    HH->>UI: "sendHeartbeat() (unicast)"
    UI-xHH: "Connection Closed / Timeout"
    HH->>HH: "sessions.remove(sessionId)"
```
*Sources: [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/websocket/HeartbeatHandler.java:36-175]()*.

---

## 4. Ops Commands and Memory Management Service

The `MemoryManageServiceImpl` bridges platform administrative interfaces to the underlying memory engine via `MemoryEngineClient`.

### Memory Management Service
`MemoryManageServiceImpl` implements `MemoryManageService`, performing permission checks (`permissionChecker.check(...)`), scope validations (`validateScopeAccess(...)`), and forwarding operations to the Python engine [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/service/impl/MemoryManageServiceImpl.java:37-147]().

*   `list(...)`: Retrieves a paginated list of user memories, handling default scope fallback and null memory-type sanitization [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/service/impl/MemoryManageServiceImpl.java:69-97]().
*   `detail(...)`: Locates specific memory items via page-based scanning [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/service/impl/MemoryManageServiceImpl.java:99-127]().
*   `create(...)`: Injects messages and variables through `MemoryEngineClient.addMessages(...)` with feature-flag resolution [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/service/impl/MemoryManageServiceImpl.java:129-147]().

```mermaid
graph TD
    MMS[MemoryManageServiceImpl] -->| "check permissions & scope" | PC[PermissionChecker]
    MMS -->| "resolve feature flags" | FFS[FeatureFlagService]
    MMS -->| "invoke client API" | MEC[MemoryEngineClient]
    MMS -->| "record change snapshot" | CML[MemoryChangeLogSnapshotMapper]
    
    style MMS fill:none,stroke:#000,stroke-width:2px
    style MEC fill:none,stroke:#000,stroke-width:2px
```
*Sources: [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/opscenter/service/impl/MemoryManageServiceImpl.java:37-147]().*

---

# Page: Platform Persistence and Migrations

# Platform Persistence and Migrations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/common/client/mock/MockMemoryEngineClient.java](agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/common/client/mock/MockMemoryEngineClient.java)
- [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/common/config/SqliteSchemaCompatInitializer.java](agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/common/config/SqliteSchemaCompatInitializer.java)
- [agent-memory-platform/platform/src/main/resources/application-gaussdb.yml](agent-memory-platform/platform/src/main/resources/application-gaussdb.yml)
- [agent-memory-platform/platform/src/main/resources/application-mysql.yml](agent-memory-platform/platform/src/main/resources/application-mysql.yml)
- [agent-memory-platform/platform/src/main/resources/application-sqlite.yml](agent-memory-platform/platform/src/main/resources/application-sqlite.yml)
- [agent-memory-platform/platform/src/main/resources/db/migration/V11__token_blacklist_init_mysql.sql](agent-memory-platform/platform/src/main/resources/db/migration/V11__token_blacklist_init_mysql.sql)

</details>



## Purpose and Scope
Section 5.1.3 covers the persistence infrastructure of the `agent-memory-platform` Java Spring Boot console. It manages database connections across multiple database dialects (MySQL, GaussDB, and SQLite), applies schema versioning and initialization scripts (simulating Flyway-style migrations via Spring SQL initialization), handles legacy SQLite schema upgrades dynamically through `SqliteSchemaCompatInitializer`, and offers an isolated fallback development engine via `MockMemoryEngineClient`.

---

## 1. Multi-Profile Database Configuration Architecture
The platform isolates environment-specific persistence configurations using Spring profiles (`mysql`, `gaussdb`, `sqlite`). Each profile specifies its own JDBC URL, driver class name, pool settings (HikariCP), and a ordered list of schema initialization scripts (`spring.sql.init.schema-locations`).

- **MySQL Profile**: Uses `com.mysql.cj.jdbc.Driver` with environment variable overrides for URL, user, and password [agent-memory-platform/platform/src/main/resources/application-mysql.yml:3-8]().
- **GaussDB Profile**: Uses `com.huawei.gaussdb.jdbc.Driver` with custom HikariCP sizing configurations [agent-memory-platform/platform/src/main/resources/application-gaussdb.yml:4-30]().
- **SQLite Profile**: Uses `org.sqlite.JDBC` targeting a local file database at `./data/platform.db` [agent-memory-platform/platform/src/main/resources/application-sqlite.yml:2-7]().

```mermaid
graph TD
    sub513["Platform Configuration Space"]
    sub513 -->|"-Dspring.profiles.active=mysql"| MySQLYaml["application-mysql.yml"]
    sub513 -->|"-Dspring.profiles.active=gaussdb"| GaussYaml["application-gaussdb.yml"]
    sub513 -->|"-Dspring.profiles.active=sqlite"| SqliteYaml["application-sqlite.yml"]

    MySQLYaml --> InitMySQL["spring.sql.init.mode=always"]
    GaussYaml --> InitGauss["spring.sql.init.mode=always"]
    SqliteYaml --> InitSqlite["spring.sql.init.mode=always"]

    InitMySQL --> ScriptsMySQL["V1..V11__*_mysql.sql"]
    InitGauss --> ScriptsGauss["V1..V11__*_gaussdb.sql"]
    InitSqlite --> ScriptsSqlite["V1..V11__*_sqlite.sql"]
```
*Sources: [agent-memory-platform/platform/src/main/resources/application-mysql.yml:1-23](), [agent-memory-platform/platform/src/main/resources/application-gaussdb.yml:1-46](), [agent-memory-platform/platform/src/main/resources/application-sqlite.yml:1-22]()*

---

## 2. Database Migration Scripts and Versioning
Schema scripts are split by database dialect under `db/migration/`. Versioned scripts cover operational logs, task registries, governance, configuration centers, tenants, users, scope registries, and token blacklists. 

For instance, the token blacklist feature is initialized across dialects:
- MySQL script: `V11__token_blacklist_init_mysql.sql` [agent-memory-platform/platform/src/main/resources/db/migration/V11__token_blacklist_init_mysql.sql:1-15]()
- Equivalent scripts exist for SQLite and GaussDB.

All scripts adhere to idempotent DDL principles using `CREATE TABLE IF NOT EXISTS` clauses, allowing `spring.sql.init.mode=always` to safely run startup scripts repeatedly.

```mermaid
graph LR
    subgraph "Migration Registry"
        V1["V1__ops_center"]
        V3["V3__config_center"]
        V6["V6__tenant_user"]
        V11["V11__token_blacklist"]
    end
    
    subgraph "Target Dialects"
        MySQL["MySQL Database"]
        GaussDB["GaussDB Database"]
        SQLite["SQLite Database"]
    end

    V1 --> MySQL
    V3 --> MySQL
    V6 --> MySQL
    V11 --> MySQL

    V1 --> GaussDB
    V3 --> GaussDB
    V6 --> GaussDB
    V11 --> GaussDB

    V1 --> SQLite
    V3 --> SQLite
    V6 --> SQLite
    V11 --> SQLite
```
*Sources: [agent-memory-platform/platform/src/main/resources/application-mysql.yml:9-23](), [agent-memory-platform/platform/src/main/resources/application-gaussdb.yml:32-46](), [agent-memory-platform/platform/src/main/resources/application-sqlite.yml:8-22](), [agent-memory-platform/platform/src/main/resources/db/migration/V11__token_blacklist_init_mysql.sql:1-15]()*

---

## 3. SQLite Schema Compatibility Initializer
To support schema migrations on legacy SQLite databases without native full alter-table support in older schema iterations, `SqliteSchemaCompatInitializer` runs prior to Spring's SQL initialization phase.

### Key Components & Data Flow
- **Lifecycle Hook**: Implements `BeanFactoryPostProcessor` and `EnvironmentAware` [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/common/config/SqliteSchemaCompatInitializer.java:21]().
- **URL Check**: Intercepts initialization only if `spring.datasource.url` starts with `jdbc:sqlite:` [agent-memory-platform/platform/src/main/java/com/openjiuwen.memory.common.config/SqliteSchemaCompatInitializer.java:31-35]().
- **Table Patches**: Updates tables (`tenants`, `users`, `config_templates`, `config_audit_logs`) by invoking `addColumnIfMissing()` to append missing columns and backfill historical data [agent-memory-platform/platform/src/main/java/com/openjiuwen.memory.common.config/SqliteSchemaCompatInitializer.java:36-87]().
- **SQL Injection Defense**: Validates table and column identifiers against a strict regex pattern `IDENT_PATTERN` before executing DDL statements [agent-memory-platform/platform/src/main/java/com/openjiuwen.memory.common.config/SqliteSchemaCompatInitializer.java:103-134]().

```mermaid
graph TD
    Start["Spring BeanFactory Post-Processing"] --> CheckURL["Check spring.datasource.url"]
    CheckURL -->|"Is jdbc:sqlite:"| OpenConn["Open JDBC Connection"]
    CheckURL -->|"Other DB"| Skip["Skip Initializer"]
    
    OpenConn --> CompatTenants["compatTenants()"]
    CompatTenants --> CompatUsers["compatUsers()"]
    CompatUsers --> CompatTemplates["compatConfigTemplates()"]
    CompatTemplates --> CompatAudit["compatConfigAuditLogs()"]
    
    CompatAudit --> ValidateIdent["Validate SQL Identifier via IDENT_PATTERN"]
    ValidateIdent --> CheckCol["Check columnExists()"]
    CheckCol -->|"Missing"| ExecAlter["Execute ALTER TABLE ADD COLUMN"]
    ExecAlter --> Backfill["Update column data from legacy fields"]
```
*Sources: [agent-memory-platform/platform/src/main/java/com/openjiuwen.memory.common.config/SqliteSchemaCompatInitializer.java:20-134]()*

---

## 4. Mock Memory Engine Client
When the platform is operated in offline or decoupled testing modes, `MockMemoryEngineClient` replaces the remote Python memory service engine.

### Implementation Details
- **Conditional Activation**: Enabled via `@ConditionalOnProperty(prefix = "platform.memory-service", name = "mode", havingValue = "mock")` [agent-memory-platform/platform/src/main/java/com/openjiuwen.memory.common.client.mock/MockMemoryEngineClient.java:44-46]().
- **In-Memory State**: Maintains memory items and variables inside concurrent hash maps (`ConcurrentHashMap`) instead of binding to external ports or databases [agent-memory-platform/platform/src/main/java/com/openjiuwen.memory.common.client.mock/MockMemoryEngineClient.java:50-51]().
- **Seed Initialization**: Automatically seeds default records (`__default__` scope and user profiles) on instantiation to mirror real Python engine responses [agent-memory-platform/platform/src/main/java/com/openjiuwen.memory.common.client.mock/MockMemoryEngineClient.java:53-58]().
- **Interface Conformance**: Implements all methods defined in the `MemoryEngineClient` contract (such as `getUserMemByPage`, `searchMemory`, `addMessages`, and scoped deletion endpoints) to ensure zero frontend disruption when switching between real and mock modes [agent-memory-platform/platform/src/main/java/com/openjiuwen.memory.common.client.mock/MockMemoryEngineClient.java:46-162]().

```mermaid
graph TD
    ClientInterface["MemoryEngineClient Contract"] --> MockImpl["MockMemoryEngineClient"]
    MockImpl --> Cond["@ConditionalOnProperty mode=mock"]
    MockImpl --> Store["ConcurrentHashMap store"]
    MockImpl --> Vars["ConcurrentHashMap variables"]
    
    Store --> Seed["Seed Default Messages & Profiles"]
    MockImpl --> Methods["getUserMemByPage / searchMemory / addMessages / deleteMemByScope"]
```
*Sources: [agent-memory-platform/platform/src/main/java/com/openjiuwen.memory.common.client.mock/MockMemoryEngineClient.java:44-162]()*

---

# Page: Platform Web UI (Vue)

# Platform Web UI (Vue)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/webui/UiController.java](agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/webui/UiController.java)
- [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/webui/service/UiAggregatorService.java](agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/webui/service/UiAggregatorService.java)
- [agent-memory-platform/platform/src/main/resources/db/migration/V3__config_center_init_gaussdb.sql](agent-memory-platform/platform/src/main/resources/db/migration/V3__config_center_init_gaussdb.sql)
- [agent-memory-platform/platform/src/main/resources/db/migration/V3__config_center_init_mysql.sql](agent-memory-platform/platform/src/main/resources/db/migration/V3__config_center_init_mysql.sql)
- [agent-memory-platform/platform/src/main/resources/db/migration/V3__config_center_init_sqlite.sql](agent-memory-platform/platform/src/main/resources/db/migration/V3__config_center_init_sqlite.sql)
- [agent-memory-platform/server/src/views/config-center/TemplateDetailPage.vue](agent-memory-platform/server/src/views/config-center/TemplateDetailPage.vue)

</details>



## Purpose and Scope
This section covers the Vue 3 frontend architecture of the `agent-memory-platform`. The Platform Web UI provides administrative consoles for managing configuration centers, multi-tenant scopes, runtime logs, and operational workflows. It communicates with the backend Spring Boot application via aggregated REST endpoints routed through `UiController` [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/webui/UiController.java:23-84]() and processed by `UiAggregatorService` [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/webui/service/UiAggregatorService.java:11-39]().

---

## 1. Frontend Architecture & Layouts
The frontend is built using Vue 3, utilizing Pinia for state management, Vue Router for view navigation, and Element Plus for UI component styling. The application architecture separates views into functional modules:
- **Config Center**: Manages scope configurations, template versioning, and draft/published states (`TemplateDetailPage.vue`) [agent-memory-platform/server/src/views/config-center/TemplateDetailPage.vue:1-172]().
- **Tenant Management**: Oversees tenant-to-scope mappings and isolation properties.
- **Log Center**: Aggregates operation logs, audit events, and message traces.
- **Ops Center**: Provides runtime engine control and health telemetry.

```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
      A["UserBrowser"] --> B["VueRouter"]
    end
    subgraph "CodeEntitySpace"
      B --> C["TemplateDetailPage.vue"]
      C --> D["PiniaStores"]
      D --> E["ApiClient"]
    end
    E --> F["UiController.java"]

    style A fill:#fff,stroke:#000,stroke-width:1px
    style B fill:#fff,stroke:#000,stroke-width:1px
    style C fill:#fff,stroke:#000,stroke-width:1px
    style D fill:#fff,stroke:#000,stroke-width:1px
    style E fill:#fff,stroke:#000,stroke-width:1px
    style F fill:#fff,stroke:#000,stroke-width:1px
```
*Figure 1: Frontend Client-Side Routing and Architecture Mapping.*

Sources: 
- `agent-memory-platform/server/src/views/config-center/TemplateDetailPage.vue:1-172`
- `agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/webui/UiController.java:23-84`

---

## 2. Backend Aggregator Layer (`UiController` and `UiAggregatorService`)
To minimize round-trips between the Vue frontend and the Spring Boot backend, the platform employs a thin controller and aggregator service design pattern.

`UiController` [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/webui/UiController.java:23-84] exposes HTTP GET endpoints under `/api/v1/ui`:
- `memoryBrowse`: Retrieves paginated memory items filtered by `scope_id`, `user_id`, and `memory_type` [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/webui/UiController.java:35-43].
- `configPage`: Aggregates configuration center metadata and scope states [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/webui/UiController.java:47-52].
- `logsPage`: Gathers operational and audit logs with pagination and tab separation [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/webui/UiController.java:57-63].
- `opsPage`: Provides operational states for engines and scopes [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/webui/UiController.java:67-73].
- `tracePage`: Tracks lineage and debugging info for individual memories (`mem_id`) [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/webui/UiController.java:77-83].

These methods delegate all business logic assembly to `UiAggregatorService` [agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/webui/service/UiAggregatorService.java:11-39].

```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
      G["UIRequests"] --> H["UiController"]
    end
    subgraph "CodeEntitySpace"
      H --> I["UiAggregatorService.java"]
      I --> J["UiAggregatorServiceImpl.java"]
      J --> K["TenantScopeConfigsRepository"]
      J --> L["ConfigTemplatesRepository"]
    end

    style G fill:#fff,stroke:#000,stroke-width:1px
    style H fill:#fff,stroke:#000,stroke-width:1px
    style I fill:#fff,stroke:#000,stroke-width:1px
    style J fill:#fff,stroke:#000,stroke-width:1px
    style K fill:#fff,stroke:#000,stroke-width:1px
    style L fill:#fff,stroke:#000,stroke-width:1px
```
*Figure 2: Backend Aggregation Data Flow from Controller to Services.*

Sources:
- `agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/webui/UiController.java:23-84`
- `agent-memory-platform/platform/src/main/java/com/openjiuwen/memory/webui/service/UiAggregatorService.java:11-39`

---

## 3. Configuration Center Views (`TemplateDetailPage.vue`)
The `TemplateDetailPage.vue` view handles configuration templates (`SCOPE` and `INSTANCE` types) [agent-memory-platform/server/src/views/config-center/TemplateDetailPage.vue:88-97]. Key features implemented in this view include:
- **Draft vs. Published Status**: Visual indicators showing whether a template draft has been synced to the memory kernel [agent-memory-platform/server/src/views/config-center/TemplateDetailPage.vue:13-18].
- **Dynamic Configuration Table**: An interactive key-value editor (`configItems`) allowing administrators to modify parameters like `model_cfg.model`, `temperature`, and memory definitions [agent-memory-platform/server/src/views/config-center/TemplateDetailPage.vue:131-159].
- **Template Inheritance**: Support for cloning existing source templates (`selectedSourceTemplateId`) to bootstrap new configurations [agent-memory-platform/server/src/views/config-center/TemplateDetailPage.vue:62-77].

Sources:
- `agent-memory-platform/server/src/views/config-center/TemplateDetailPage.vue:1-172`

---

## 4. Persistence and Database Schemas for the UI
The UI configuration views are backed by relational database tables defined across MySQL, GaussDB, and SQLite migrations. 

The core tables supporting the Config Center and Tenant management include:
- `tenant_scope_configs`: Stores 1:1 tenant-to-scope configuration snapshots (`config_json`), linking templates with versioning for drift detection (`template_version` vs `current_version`) [agent-memory-platform/platform/src/main/resources/db/migration/V3__config_center_init_mysql.sql:11-23], [agent-memory-platform/platform/src/main/resources/db/migration/V3__config_center_init_sqlite.sql:31-41].
- `config_templates`: Manages `SCOPE` and `INSTANCE` templates, tracking status (`published`/`draft`), parent inheritance (`parent_id`), and JSON configurations [agent-memory-platform/platform/src/main/resources/db/migration/V3__config_center_init_mysql.sql:25-44], [agent-memory-platform/platform/src/main/resources/db/migration/V3__config_center_init_sqlite.sql:52-67].
- `config_audit_logs`: Records operator actions, before/after JSON states, and success indicators for audit compliance [agent-memory-platform/platform/src/main/resources/db/migration/V3__config_center_init_mysql.sql:75-90], [agent-memory-platform/platform/src/main/resources/db/migration/V3__config_center_init_sqlite.sql:92-105].

Sources:
- `agent-memory-platform/platform/src/main/resources/db/migration/V3__config_center_init_mysql.sql:11-90`
- `agent-memory-platform/platform/src/main/resources/db/migration/V3__config_center_init_sqlite.sql:31-105`

---

# Page: Operations, Deployment and Testing

# Operations, Deployment and Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deploy/.env.example](deploy/.env.example)
- [deploy/Dockerfile](deploy/Dockerfile)
- [deploy/deploy.sh](deploy/deploy.sh)
- [deploy/docker-compose.yml](deploy/docker-compose.yml)

</details>



This page covers the operations, deployment assets, documentation framework, and test infrastructure for the JiuwenMemory (`agent-memory`) codebase. As a parent page, it provides a high-level overview of how the service is packaged, containerized, configured, and validated, while delegating deep technical specifics to dedicated child pages.

```
+-------------------------------------------------------------------------------------------------+
|                               6. Operations, Deployment and Testing                              |
+-------------------------------------------------------------------------------------------------+
         |                                           |                                   |
         v                                           v                                   v
+-----------------------------+             +-------------------------------+   +-----------------------------+
| 6.1 Deployment              |             | 6.2 Testing Strategy          |   | 6.3 Documentation & License |
| (deploy/Dockerfile,         |             | (tests/unit_tests/,           |   | (docs/en, docs/zh,          |
|  deploy/docker-compose.yml, |             |  conftest fixtures,           |   |  README bilingual pair,     |
|  deploy/deploy.sh,          |             |  store integration tests)     |   |  open-source notice)        |
|  deploy/.env.example)       |             |                               |   |                             |
+-----------------------------+             +-------------------------------+   +-----------------------------+
```

Sources:
- `deploy/Dockerfile`
- `deploy/docker-compose.yml`
- `deploy/deploy.sh`
- `deploy/env.example`

---

## 6.1 Deployment

The deployment framework is centered around containerization assets located in the `deploy/` directory [deploy/Dockerfile:1-60](). It supports deploying the Python FastAPI memory engine as an independent microservice that can communicate with Java management platforms (such as `spring-ai-ascend`) over a shared Docker bridge network [deploy/docker-compose.yml:1-70]().

Key components of the deployment architecture include:
- **`Dockerfile`**: A multi-stage Python 3.11 slim image definition that installs optional extras (`[chromadb,sqlite,gaussdb,elasticsearch,server]`), configures a non-root `app` user, and exposes the `memory-server` entry point on port `8000` [deploy/Dockerfile:11-60]().
- **`docker-compose.yml`**: Defines the `agent-memory` service configuration, volume mapping for persistent data (`memory_data`), environment variables for model providers and storage adapters, and the `agent-memory-net` bridge network [deploy/docker-compose.yml:1-70]().
- **`deploy.sh`**: An automated shell script that handles pre-flight `.env` checks, container teardown, image building using Docker BuildKit, container startup with port mapping, and health check validation via `/health` [deploy/deploy.sh:1-83]().
- **`.env.example`**: A comprehensive configuration template covering service bindings, embedding and LLM provider parameters, API authentication tokens, and storage backend types (`KV_STORE_TYPE`, `DB_STORE_TYPE`, `VECTOR_STORE_TYPE`) [deploy/.env.example:1-62]().

For detailed configuration variables, step-by-step startup instructions, and environment templates for both the engine and platform, see [Deployment](#6.1).

Sources:
- `deploy/Dockerfile:1-61`
- `deploy/docker-compose.yml:1-71`
- `deploy/deploy.sh:1-84`
- `deploy/.env.example:1-63`

---

## 6.2 Testing Strategy

The test suite validates correctness across storage abstractions, server endpoints, and core engine lifecycles. It is organized under the `tests/` directory and relies heavily on modular fixtures and configuration mocks.

Testing layers include:
- **Server Endpoint Tests**: FastAPI routing and middleware tests verifying authentication, payload validation, and error handling.
- **Conftest Fixtures**: Shared pytest fixtures providing isolated database instances, mock LLM clients, and temporary storage directories.
- **Core Engine Tests**: Verification of the `LongTermMemory` singleton lifecycle, memory managers, and extraction/generation pipelines.
- **Store Integration Tests**: End-to-end validation of vector indices, relational database backends, and simple key-value stores.

For details on test layouts, fixture definitions, and execution commands, see [Testing Strategy](#6.2).

Sources:
- `deploy/Dockerfile:1-61`

---

## 6.3 Documentation and Licensing

The project maintains a bilingual documentation and licensing footprint to support global developers and enterprise deployments.

The documentation assets comprise:
- **API Documentation (`docs/en` and `docs/zh`)**: Comprehensive guides and reference documentation translated into English and Chinese.
- **Bilingual README Pair**: Project root documentation providing quick-start instructions, architecture summaries, and contribution guidelines in both languages.
- **Open-Source Notice and License**: Licensing headers and legal terms governing the usage and redistribution of the codebase.

For details on documentation structure, API spec locations, and licensing terms, see [Documentation and Licensing](#6.3).

Sources:
- `deploy/Dockerfile:31-31`

---

# Page: Deployment

# Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deploy/.env.example](deploy/.env.example)
- [deploy/Dockerfile](deploy/Dockerfile)
- [deploy/deploy.sh](deploy/deploy.sh)
- [deploy/docker-compose.yml](deploy/docker-compose.yml)
- [jiuwen_memory/server/.env.example](jiuwen_memory/server/.env.example)
- [pyproject.toml](pyproject.toml)
- [uv.lock](uv.lock)

</details>



The deployment module provides containerization assets, automated shell deployment scripts, multi-service orchestration configurations, and environment profile templates for the JiuwenMemory Python long-term memory engine (`jiuwen_memory`). It facilitates running the FastAPI memory server (`memory-server`) [pyproject.toml:73-73]() inside isolated container environments with persistent storage and network linkages for downstream consumers such as Java platforms (`spring-ai-ascend`).

---

## 1. Containerization Architecture

The memory engine is packaged into an immutable container image using a multi-stage Python slim base. The container sets up system compilers for native vector extensions, installs pinned dependencies from `pyproject.toml`, configures non-root execution permissions, and binds the FastAPI entrypoint script.

```mermaid
graph TD
    sub5[""Natural Language Space: Base Image Setup""]
    sub6[""Code Entity Space: Dockerfile Layers""]

    sub5 -->|Base OS| sub6
    sub1[""Python 3.11 Slim Image""] -->|FROM| C1[""deploy/Dockerfile:11""]
    sub2[""Package Metadata""] -->|COPY| C2[""deploy/Dockerfile:31""]
    sub3[""C-Extensions & Server Dependencies""] -->|RUN pip install| C3[""deploy/Dockerfile:34""]
    sub4[""Engine Entrypoint Script""] -->|ENTRYPOINT| C4[""jiuwen_memory.server.memory_server:main""]

    C1 --> C2 --> C3 --> C4

    style sub5 fill:none,stroke:none
    style sub6 fill:none,stroke:none
```
*Figure 1: Container build stages mapping natural language requirements to `deploy/Dockerfile` and `pyproject.toml` symbols.*

Key implementation details of the Dockerfile:
- **Base Environment**: Uses `python:3.11-slim` with debian package mirrors [deploy/Dockerfile:11-14]().
- **System Dependencies**: Installs `build-essential` (required for compiling vector index C-extensions like `hnswlib` or `sqlite-vec`) and `curl` (used by container health checks) [deploy/Dockerfile:19-21]().
- **Python Dependencies**: Installs project extras for chromadb, sqlite, gaussdb, elasticsearch, and the FastAPI server [deploy/Dockerfile:34](), matching the optional groups defined in [pyproject.toml:55-70]().
- **Security Context**: Creates a dedicated non-root user `app` with a writable home directory at `/home/app/.jiuwenmemory` and mounts data volumes at `/app/memory_data` [deploy/Dockerfile:43-47]().
- **Health Check**: Periodically pokes `http://localhost:8000/health` every 30 seconds [deploy/Dockerfile:55-56]().
- **Entrypoint**: Executes the console script `memory-server` [deploy/Dockerfile:60](), which maps to `jiuwen_memory.server.memory_server:main` [pyproject.toml:73-73]().

Sources: `deploy/Dockerfile`, `pyproject.toml`

---

## 2. Orchestration and Multi-Service Networking

To coordinate the Python memory engine alongside external storage systems and agent frameworks (such as Java Spring Boot runtimes), Docker Compose defines a shared bridge network (`agent-memory-net`) and persistent volumes.

```mermaid
graph TD
    sub3[""Natural Language Space: Orchestration Topology""]
    sub4[""Code Entity Space: Docker Compose Services""]

    sub3 -->|Service Definition| sub4
    sub1[""Python Memory Engine""] -->|Service| S1[""deploy/docker-compose.yml:16""]
    sub2[""Bridge Network""] -->|Network| S2[""deploy/docker-compose.yml:64""]
    sub5[""Persistent Storage""] -->|Volume| S3[""deploy/docker-compose.yml:68""]

    S1 -->|Connects to| S2
    S1 -->|Mounts| S3

    style sub3 fill:none,stroke:none
    style sub4 fill:none,stroke:none
```
*Figure 2: Multi-service composition mapping architectural components to `deploy/docker-compose.yml` configurations.*

Key orchestration parameters in `deploy/docker-compose.yml`:
- **Service Identifier**: Defined under service name `agent-memory` with image tag `agent-memory:latest` [deploy/docker-compose.yml:16-20]().
- **Port Mapping**: Exposes container port `8000` to host port `8001` (configurable via `${HOST_PORT:-8001}`) [deploy/docker-compose.yml:25]().
- **Environment Passthrough**: Propagates LLM credentials, store types (`KV_STORE_TYPE`, `DB_STORE_TYPE`, `VECTOR_STORE_TYPE`), and connection strings (`DB_URL`, `VECTOR_ES_HOSTS`) directly into the container environment [deploy/docker-compose.yml:26-53]().
- **Network Isolation**: Attaches to an explicitly named bridge network `agent-memory-net`, enabling discovery by other services via service name resolution (`http://agent-memory:8000`) [deploy/docker-compose.yml:64-66]().
- **Volume Persistence**: Mounts the `memory_data` volume to `/app/memory_data` to preserve SQLite databases and Chroma vector files across container restarts [deploy/docker-compose.yml:68-70]().

Sources: `deploy/docker-compose.yml`

---

## 3. Deployment Automation

The `deploy.sh` script automates the complete container lifecycle, performing validation, environment loading, image compilation, container replacement, and health verification.

```mermaid
graph TD
    sub3[""Natural Language Space: Execution Pipeline""]
    sub4[""Code Entity Space: deploy.sh Operations""]

    sub3 -->|Script Step| sub4
    S1[""Check .env File Presence""] -->|Validation| P1[""deploy/deploy.sh:9""]
    S2[""Stop & Remove Old Container""] -->|Cleanup| P2[""deploy/deploy.sh:34""]
    S3[""Build Docker Image via BuildKit""] -->|Build| P3[""deploy/deploy.sh:42""]
    S4[""Run Container with Port Bindings""] -->|Startup| P4[""deploy/deploy.sh:50""]
    S5[""Poll /health HTTP Endpoint""] -->|Verification| P5[""deploy/deploy.sh:61""]

    P1 --> P2 --> P3 --> P4 --> P5

    style sub3 fill:none,stroke:none
    style sub4 fill:none,stroke:none
```
*Figure 3: Deployment script pipeline mapping operational phases to `deploy/deploy.sh` routines.*

Detailed script logic:
- **Prerequisite Validation**: Verifies the presence of `deploy/.env`. If missing, execution halts with an error instruction [deploy/deploy.sh:9-12]().
- **Environment Loading**: Sources configuration variables into the shell environment [deploy/deploy.sh:14]().
- **Container Lifecycle Management**: Safely stops and deletes any existing container matching `CONTAINER_NAME` (`agent-memory`) and ensures the Docker network `agent-memory-net` exists [deploy/deploy.sh:34-38]().
- **Image Compilation**: Triggers `docker build` using the repository root (`..`) as the build context and `deploy/Dockerfile` as the recipe, with `DOCKER_BUILDKIT=1` enabled [deploy/deploy.sh:42-45]().
- **Container Execution**: Runs the container in detached mode, mounting the `.env` file and publishing ports [deploy/deploy.sh:50-56]().
- **Health Polling**: Executes a retry loop (up to 30 attempts, sleeping 2 seconds between checks) executing `curl -fsS http://localhost:${MEMORY_PORT}/health` to confirm successful initialization before marking deployment complete [deploy/deploy.sh:61-68]().

Sources: `deploy/deploy.sh`

---

## 4. Environment Template Configuration

Environment configuration is managed via template files that define variables for LLM connectivity, storage backends, indexing strategies, and server bindings.

### Configuration Template Reference Table

| Category | Variable Name | Default / Example | Description |
| :--- | :--- | :--- | :--- |
| **Server** | `IP` / `HOST_IP` | `0.0.0.0` / `127.0.0.1` | Binding address for the FastAPI server or host port mapper [deploy/.env.example:6-8]() |
| **Server** | `PORT` / `HOST_PORT` | `8000` / `8001` | Service listening port inside and outside the container [deploy/.env.example:9-14]() |
| **Server** | `MEMORY_API_KEY` | *(empty)* | Optional Bearer token required for write and delete operations [jiuwen_memory/server/.env.example:40-41]() |
| **LLM** | `MODEL_PROVIDER` | `SiliconFlow`, `OpenAI` | LLM service provider identifier [jiuwen_memory/server/.env.example:3-3]() |
| **LLM** | `MODEL_NAME` | `your-llm-model-name` | Name of the primary generation model [deploy/.env.example:34-34]() |
| **LLM** | `API_BASE` / `API_KEY` | *(URL/Secret)* | Endpoint URL and authentication key for the LLM API [deploy/.env.example:36-37]() |
| **Embedding** | `EMBED_MODEL_NAME` | `your-embedding-model-name` | Model name used for text vectorization [deploy/.env.example:29-29]() |
| **Stores** | `KV_STORE_TYPE` | `in_memory`, `db`, `shelve` | Key-value store backend selection [jiuwen_memory/server/.env.example:61-62]() |
| **Stores** | `DB_STORE_TYPE` | `default`, `gauss` | Relational database store type [jiuwen_memory/server/.env.example:67-68]() |
| **Stores** | `DB_URL` | `gaussdb://user:pass@host:port/db` | SQLAlchemy asynchronous connection URL [deploy/.env.example:49-49]() |
| **Vector** | `VECTOR_STORE_TYPE` | `chroma`, `milvus`, `elasticsearch`, `gauss` | Vector index storage implementation [jiuwen_memory/server/.env.example:82-82]() |
| **Index** | `INDEX_BACKEND` | `simple`, `file` | Memory index strategy (hybrid vs Markdown/SQLite file index) [jiuwen_memory/server/.env.example:71-77]() |
| **Security** | `MEMORY_CODEC` | *(empty)*, `aes`, `sm4` | Storage encryption codec selection (AES-256-GCM or SM4) [jiuwen_memory/server/.env.example:121-125]() |

Sources: `deploy/.env.example`, `jiuwen_memory/server/.env.example`

---

# Page: Testing Strategy

# Testing Strategy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tests/unit_tests/core/foundation/store/filter/test_simple_index_filters.py](tests/unit_tests/core/foundation/store/filter/test_simple_index_filters.py)
- [tests/unit_tests/core/foundation/store/index/__init__.py](tests/unit_tests/core/foundation/store/index/__init__.py)
- [tests/unit_tests/core/foundation/store/vector/test_chroma_vector_store_integration.py](tests/unit_tests/core/foundation/store/vector/test_chroma_vector_store_integration.py)
- [tests/unit_tests/core/foundation/store/vector/test_elasticsearch_vector_store_integration.py](tests/unit_tests/core/foundation/store/vector/test_elasticsearch_vector_store_integration.py)
- [tests/unit_tests/core/memory/manage/search/test_search_manager.py](tests/unit_tests/core/memory/manage/search/test_search_manager.py)
- [tests/unit_tests/core/memory/process/dreaming/test_dreaming_integration.py](tests/unit_tests/core/memory/process/dreaming/test_dreaming_integration.py)
- [tests/unit_tests/server/__init__.py](tests/unit_tests/server/__init__.py)
- [tests/unit_tests/server/conftest.py](tests/unit_tests/server/conftest.py)
- [tests/unit_tests/server/test_mem_mutation_endpoints.py](tests/unit_tests/server/test_mem_mutation_endpoints.py)
- [tests/unit_tests/server/test_mem_variables_validation.py](tests/unit_tests/server/test_mem_variables_validation.py)
- [tests/unit_tests/server/test_search_endpoints.py](tests/unit_tests/server/test_search_endpoints.py)
- [tests/unit_tests/server/test_server_auth.py](tests/unit_tests/server/test_server_auth.py)
- [tests/unit_tests/server/test_variables_endpoints.py](tests/unit_tests/server/test_variables_endpoints.py)

</details>



## Purpose and Scope
This page details the testing infrastructure and unit test layout located under `tests/unit_tests/` in the codebase. The testing framework is structured into distinct tiers to isolate system components: FastAPI server endpoint tests utilizing `ASGITransport` and `AsyncMock` fixtures, core memory engine validation tests, and real-backend store integration tests for vector indexes (Chroma and Elasticsearch).

---

## 1. Server Endpoint Tests and Conftest Isolation
The server test suite (`tests/unit_tests/server/`) validates FastAPI routing, request validation via Pydantic models, authentication middleware, and error translation without requiring network port binding or external LLM calls. 

Isolation is achieved through `httpx.ASGITransport` bound directly to the FastAPI `app` object and `pytest-asyncio` fixtures defined in `tests/unit_tests/server/conftest.py`.

```mermaid
graph TD
    subgraph "NaturalLanguageSpace: Server Test Infrastructure"
        A["Unauthenticated Client"] --> B["ASGITransport ASGI Client"]
        C["Authenticated Bearer Client"] --> B
        D["Engine Mock Framework"] --> E["AsyncMock Memory Engine"]
    end

    subgraph "CodeEntitySpace: Test Modules & Fixtures"
        B --> F["tests/unit_tests/server/conftest.py:client"]
        B --> G["tests/unit_tests/server/conftest.py:auth_client"]
        E --> H["tests/unit_tests/server/conftest.py:mock_engine"]
        H --> I["tests/unit_tests/server/test_search_endpoints.py"]
        H --> J["tests/unit_tests/server/test_mem_mutation_endpoints.py"]
        H --> K["tests/unit_tests/server/test_variables_endpoints.py"]
        F --> L["tests/unit_tests/server/test_server_auth.py"]
        F --> M["tests/unit_tests/server/test_mem_variables_validation.py"]
    end

    classDef default stroke:#000,fill:#fff;
```
*Sources: `tests/unit_tests/server/conftest.py:1-90`*, `tests/unit_tests/server/test_search_endpoints.py:1-88`*, `tests/unit_tests/server/test_server_auth.py:1-81`*

### Key Test Categories in `tests/unit_tests/server/`
- **Search Endpoints (`test_search_endpoints.py`)**: Tests parameter passthrough (`query`, `num`, `threshold`, `user_id`, `scope_id`), enum serialization for `MemoryType`, and `500` error translation on engine exceptions [tests/unit_tests/server/test_search_endpoints.py:1-87]().
- **Mutation & Variables Endpoints (`test_mem_mutation_endpoints.py`, `test_variables_endpoints.py`)**: Verifies `/update_mem_by_id/`, `/delete_mem_by_scope/`, and variable state operations [tests/unit_tests/server/test_mem_mutation_endpoints.py:1-119](), [tests/unit_tests/server/test_variables_endpoints.py:1-163]().
- **Authentication & Security Guard (`test_server_auth.py`)**: Validates the Bearer token middleware, health check bypasses, and the startup security guard function `is_host_exposed_without_key` [tests/unit_tests/server/test_server_auth.py:1-153]().
- **Narrow Model Validation (`test_mem_variables_validation.py`)**: Tests strict Pydantic deserialization of `MemVariable` models under `AddMessagesRequest`, ensuring malformed types or missing required fields raise `422 Unprocessable Entity` before touching the engine [tests/unit_tests/server/test_mem_variables_validation.py:1-105]().

Sources: `tests/unit_tests/server/conftest.py:1-90`, `tests/unit_tests/server/test_search_endpoints.py:1-88`, `tests/unit_tests/server/test_server_auth.py:1-153`, `tests/unit_tests/server/test_mem_variables_validation.py:1-105`

---

## 2. Core Engine and Dreaming Integration Tests
Core engine tests validate internal memory pipelines, including message processing, multi-term synchronization, and background routines such as dreaming.

### Dreaming End-to-End Flow
Integration tests like `test_dreaming_end_to_end` verify the complete chain: ingesting raw session messages via `add_messages`, triggering consolidation through `LongTermMemory.start_dreaming`, deduplicating via `MemUpdateChecker`, and retrieving consolidated memories [tests/unit_tests/core/memory/process/dreaming/test_dreaming_integration.py:1-168](). Because real LLM outputs are mocked using deterministic fixtures (`_smart_llm` and `_InMemoryIndex`), tests execute reliably in CI environments without external API overhead [tests/unit_tests/core/memory/process/dreaming/test_dreaming_integration.py:36-157]().

Sources: `tests/unit_tests/core/memory/process/dreaming/test_dreaming_integration.py:1-168`

---

## 3. Store Integration and Vector Index Tests
The foundation layer features integration tests for vector backends (`ChromaVectorStore`, `ElasticsearchVectorStore`) and hybrid search indices (`SimpleMemoryIndex`) [tests/unit_tests/core/foundation/store/vector/test_chroma_vector_store_integration.py:1-79](), [tests/unit_tests/core/foundation/store/vector/test_elasticsearch_vector_store_integration.py:1-64](), [tests/unit_tests/core/foundation/store/filter/test_simple_index_filters.py:1-153]().

```mermaid
graph TD
    subgraph "NaturalLanguageSpace: Vector and Index Store Tests"
        A["Embedded Chroma Database"] --> B["ChromaVectorStore Integration"]
        C["External Elasticsearch Service"] --> D["ElasticsearchVectorStore Integration"]
        E["In-Memory Stub Vector Store"] --> F["SimpleMemoryIndex Filter Pushdown Tests"]
    end

    subgraph "CodeEntitySpace: Store Test Modules"
        B --> G["tests/unit_tests/core/foundation/store/vector/test_chroma_vector_store_integration.py"]
        D --> H["tests/unit_tests/core/foundation/store/vector/test_elasticsearch_vector_store_integration.py"]
        F --> I["tests/unit_tests/core/foundation/store/filter/test_simple_index_filters.py"]
    end

    classDef default stroke:#000,fill:#fff;
```
*Sources: `tests/unit_tests/core/foundation/store/vector/test_chroma_vector_store_integration.py:1-79`*, `tests/unit_tests/core/foundation/store/vector/test_elasticsearch_vector_store_integration.py:1-64`*, `tests/unit_tests/core/foundation/store/filter/test_simple_index_filters.py:1-153`*

### Backend-Specific Validation Strategies
- **ChromaVectorStore (`test_chroma_vector_store_integration.py`)**: Runs against a local, ephemeral directory via `chromadb.PersistentClient`. Validates schema creation with Ebbinghaus boolean scalar fields (`blacklisted`, `is_important`), filter pushdown to Chroma's `where` clause, and partial field updates [tests/unit_tests/core/foundation/store/vector/test_chroma_vector_store_integration.py:52-132]().
- **ElasticsearchVectorStore (`test_elasticsearch_vector_store_integration.py`)**: Conditionally executed when `ES_HOSTS` environment variables are present (`pytest.importorskip`). Validates index mapping, vector similarity searches, and filter query generation [tests/unit_tests/core/foundation/store/vector/test_elasticsearch_vector_store_integration.py:18-135]().
- **SimpleMemoryIndex Filters (`test_simple_index_filters.py`)**: Uses `_StubVectorStore` and `_DummyEmbedding` collaborators to verify filter clause evaluation, blacklisted memory exclusion, and metadata retention during `update_mem_by_id` calls without invoking external services [tests/unit_tests/core/foundation/store/filter/test_simple_index_filters.py:30-153]().

Sources: `tests/unit_tests/core/foundation/store/vector/test_chroma_vector_store_integration.py:1-132`, `tests/unit_tests/core/foundation/store/vector/test_elasticsearch_vector_store_integration.py:1-135`, `tests/unit_tests/core/foundation/store/filter/test_simple_index_filters.py:1-153`

---

# Page: Documentation and Licensing

# Documentation and Licensing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [Open_Source_Software_Notice.txt](Open_Source_Software_Notice.txt)
- [README.md](README.md)
- [README.zh.md](README.zh.md)
- [docs/en/API Docs/config.md](docs/en/API Docs/config.md)
- [docs/en/API Docs/graph_memory.md](docs/en/API Docs/graph_memory.md)
- [tests/unit_tests/core/memory/graph/graph_memory/test_base.py](tests/unit_tests/core/memory/graph/graph_memory/test_base.py)

</details>



## Purpose and Scope

Section 6.3 covers the comprehensive documentation architecture, bilingual entry points, and open-source compliance framework of the `agent-memory` repository (`JiuwenMemory`). This includes the English and Chinese API documentation sets under `docs/en/` and `docs/zh/`, the bilingual README pair (`README.md` and `README.zh.md`), and the legal governance assets (`LICENSE` and `Open_Source_Software_Notice.txt`).

Sources: `README.md:1-109` [README.md:1-109](), `LICENSE:1-126` [LICENSE:1-126](), `Open_Source_Software_Notice.txt:1-35` [Open_Source_Software_Notice.txt:1-35]()

---

## Documentation Architecture and API Doc Set

The documentation subsystem provides technical references for configuring engines, orchestrating memory layers, and integrating specialized subsystems such as graph memory. The API documentation set maps user-facing parameters directly to underlying Python classes and configuration schemas.

### Configuration Reference Documentation
The configuration documentation defined in `docs/en/API Docs/config.md` outlines engine-level and scope-level parameters [docs/en/API Docs/config.md:1-41]`:
- `MemoryEngineConfig`: Manages global parameters including `default_model_cfg`, `default_model_client_cfg`, `input_msg_max_len`, `crypto_key`, and third-party cryptographic extension registries via `codec` [docs/en/API Docs/config.md:11-28]().
- `MemoryScopeConfig`: Manages namespace isolation, overriding model requests, embedding configurations (`embedding_cfg`), and profile definitions per `scope_id` [docs/en/API Docs/config.md:92-102]().

### Graph Memory Documentation
The graph memory reference in `docs/en/API Docs/graph_memory.md` specifies the usage patterns for extracting entities, relations, and episodes using `GraphMemory` [docs/en/API Docs/graph_memory.md:1-139]():
- `GraphMemory`: Orchestrates Milvus or alternative graph backends, parsing input streams (`EpisodeType`) into structured `Entity` and `Relation` nodes [docs/en/API Docs/graph_memory.md:108-139]().
- Attachment APIs: `attach_embedder(embedder: Embedding)` and `attach_reranker(reranker: Reranker)` inject retrieval dependencies required prior to invoking `add_memory` or `search` [docs/en/API Docs/graph_memory.md:140-166]().

### Diagram: Documentation Set to Code Entity Mapping

```mermaid
graph TD
    DocConfig["docs/en/API Docs/config.md"] --> EngineConfig["jiuwen_memory.memory_core.config.MemoryEngineConfig"]
    DocConfig --> ScopeConfig["jiuwen_memory.memory_core.config.MemoryScopeConfig"]
    DocGraph["docs/en/API Docs/graph_memory.md"] --> GraphMemClass["jiuwen_memory.memory_core.graph.GraphMemory"]
    DocGraph --> GraphCfg["jiuwen_memory.foundation.store.graph.GraphConfig"]
    DocGraph --> AddStrat["jiuwen_memory.memory_core.config.graph.AddMemStrategy"]
```

Sources: `docs/en/API Docs/config.md:1-102` [docs/en/API Docs/config.md:1-102](), `docs/en/API Docs/graph_memory.md:1-166` [docs/en/API Docs/graph_memory.md:1-166]()

---

## Bilingual README Pair

The project provides an entry point via a synchronized bilingual README structure:
- `README.md`: English documentation detailing the AutoGenetic memory philosophy (L0-L3 architecture), installation extras (`pip install JiuwenMemory[all]`), and code examples [README.md:1-109]().
- `README.zh.md`: Chinese localization of the core architecture descriptions, installation guides, and complete programmatic examples using `LongTermMemory` [README.zh.md:1-211]().

Both documents cover the four-tier progressive architecture (L0 Raw Information, L1 Summary Memory, L2 Structured Memory, L3 User Profile), Auto Dreaming, MemoryTurbo acceleration, and AES-256-GCM encryption hardening [README.md:17-48](), [README.zh.md:19-48]().

Sources: `README.md:1-109` [README.md:1-109](), `README.zh.md:1-211` [README.zh.md:1-211]()

---

## Open-Source Licensing and Notice Framework

JiuwenMemory is distributed under open-source governance terms defined by the Apache License Version 2.0, alongside explicit third-party attribution notices.

### Apache License v2.0 (`LICENSE`)
The repository includes the standard Apache 2.0 license text (`LICENSE`), granting users:
- Perpetual, worldwide, non-exclusive, royalty-free copyright and patent licenses to reproduce, prepare derivative works of, publicly display, and distribute the work [LICENSE:67-88]().
- Conditions requiring prominent notices of file modifications, retention of copyright/patent notices, and distribution of a copy of the license with any derivative works [LICENSE:90-126]().

### Third-Party Software Notices (`Open_Source_Software_Notice.txt`)
The `Open_Source_Software_Notice.txt` file compiles attribution notices, warranty disclaimers, and license texts for dependencies embedded or distributed alongside the product (such as `aiofiles` under Apache 2.0) [Open_Source_Software_Notice.txt:1-35](). It asserts that open-source licenses prevail over other terms while disclaiming implied warranties of merchantability or fitness for a particular purpose [Open_Source_Software_Notice.txt:1-7]().

### Diagram: Licensing and Compliance Data Flow

```mermaid
graph TD
    RepoRoot["agent-memory Repository"] --> LicenseFile["LICENSE (Apache 2.0)"]
    RepoRoot --> NoticeFile["Open_Source_Software_Notice.txt"]
    LicenseFile --> GrantRights["Perpetual Royalty-Free Grant"]
    LicenseFile --> RedistRules["Redistribution & Modification Terms"]
    NoticeFile --> ThirdPartyDeps["Third-Party Component Attributions"]
    NoticeFile --> WarrantyDisclaim["Warranty Disclaimer & Liability Limit"]
```

Sources: `LICENSE:1-126` [LICENSE:1-126](), `Open_Source_Software_Notice.txt:1-35` [Open_Source_Software_Notice.txt:1-35]()

---

# Page: Glossary

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README.zh.md](README.zh.md)
- [docs/en/API Docs/long_term_memory.md](docs/en/API Docs/long_term_memory.md)
- [jiuwen_memory/foundation/store/index/simple_memory_index.py](jiuwen_memory/foundation/store/index/simple_memory_index.py)
- [jiuwen_memory/foundation/store/kv/db_based_kv_store.py](jiuwen_memory/foundation/store/kv/db_based_kv_store.py)
- [jiuwen_memory/memory_core/long_term_memory.py](jiuwen_memory/memory_core/long_term_memory.py)
- [jiuwen_memory/memory_core/manage/index/fragment_memory_manager.py](jiuwen_memory/memory_core/manage/index/fragment_memory_manager.py)
- [jiuwen_memory/memory_core/manage/index/summary_manager.py](jiuwen_memory/memory_core/manage/index/summary_manager.py)
- [jiuwen_memory/memory_core/manage/mem_model/sql_message_store.py](jiuwen_memory/memory_core/manage/mem_model/sql_message_store.py)
- [jiuwen_memory/server/memory_server.py](jiuwen_memory/server/memory_server.py)

</details>



## Purpose and Scope

This wiki page defines codebase-specific terms, architectural concepts, data structures, and core classes implemented in the `agent-memory` (`jiuwen_memory`) repository. It serves as an authoritative technical reference mapping natural language domain concepts to their exact Python implementations, classes, and file paths.

---

## 1. Core Architectural & Conceptual Terms

### AutoGenetic Memory
The overarching paradigm of JiuwenMemory where memory operates as a self-evolving, gene-like digital asset rather than static logs. Memories replicate, mutate (via extraction/deduplication), and consolidate autonomously.
- **Source Files**: [README.md:5-15](), [README.zh.md:5-15]()

### L0–L3 Layered Memory
The four progressive tiers of memory abstraction:
- **L0 (Raw Information)**: Unprocessed chat messages stored via `SqlMessageStore`.
- **L1 (Summary Memory)**: Chunked/topic-level conversation summaries managed by `SummaryManager`.
- **L2 (Structured Memory)**: Granular entries like semantic and episodic memory units.
- **L3 (User Profile)**: Long-term traits and preferences extracted into `FragmentMemoryUnit`.
- **Source Files**: [README.md:17-21](), [jiuwen_memory/memory_core/long_term_memory.py:36-44]()

### scope_id
A tenant/application isolation boundary string used to namespace configurations, keys, vector collections, and SQL filters, ensuring multi-tenant security separation.
- **Source Files**: [README.md:46-48](), [jiuwen_memory/memory_core/long_term_memory.py:124-124]()

### MemoryTurbo
An asynchronous middle-term caching and acceleration mechanism where incoming conversation turns are written immediately to cache (`MiddleTermMemoryManager`), while heavy extraction runs asynchronously in the background.
- **Source Files**: [README.md:21-25](), [jiuwen_memory/memory_core/long_term_memory.py:42-42]()

### Dreaming
A background sleep-time memory consolidation pipeline inspired by cognitive neuroscience (light sleep filtering, REM extraction, deep sleep deduplication and conflict resolution) orchestrated by `DreamingOrchestrator`.
- **Source Files**: [README.md:21-23](), [jiuwen_memory/memory_core/long_term_memory.py:25-30]()

### Ebbinghaus forgetting
A memory decay and reinforcement evaluation mechanism using an Ebbinghaus curve evaluator (`EbbinghausEvaluator`) combined with retrieval history scoring to prune or retain memory documents.
- **Source Files**: [README.md:21-23](), [jiuwen_memory/memory_core/long_term_memory.py:31-34]()

### blacklisted
A boolean flag on memory documents indicating that a specific memory unit has been excluded from active retrieval recall due to administrative actions or conflict resolution.
- **Source Files**: [README.md:27-30](), [jiuwen_memory/foundation/store/base_memory_index.py:56-56]()

### MCP (Model Context Protocol)
The Model Context Protocol server interface exposing memory tools and transports for agent integration.
- **Source Files**: [README.md:35-41](), [jiuwen_memory/server/memory_server.py:1-35]()

### mem_meta
A metadata manager and statistics tracking subsystem (`MemoryMetaManager`) handling versioned KV, SQL, and index schema migrations.
- **Source Files**: [README.md:31-35](), [jiuwen_memory/memory_core/migration/migrator/memory_meta_manager.py:1-46]()

Sources: [README.md:1-523](), [jiuwen_memory/memory_core/long_term_memory.py:1-140]()

---

## 2. Data Models & Units

### MemoryDoc
The unified internal document schema used by `BaseMemoryIndex` implementations, containing fields such as `id`, `text`, `type`, `timestamp`, and extensible metadata dictionaries.
- **Source Files**: [jiuwen_memory/foundation/store/base_memory_index.py:56-65]()

### MemoryType
An enumeration defining categorical memory classifications including `USER_PROFILE`, `SEMANTIC_MEMORY`, `EPISODIC_MEMORY`, `SUMMARY`, and `VARIABLE`.
- **Source Files**: [jiuwen_memory/memory_core/manage/mem_model/memory_unit.py:10-20](), [jiuwen_memory/memory_core/long_term_memory.py:42-44]()

### MiddleTermUnit
A middle-term cache unit processed inside `MiddleTermMemoryManager` prior to promotion into long-term storage via `middle_mem_to_long`.
- **Source Files**: [jiuwen_memory/memory_core/manage/index/middle_mem_manager.py:1-50]()

### FilterGroup
A composite filtering DSL structure used for conditional query building across relational stores and vector indexes.
- **Source Files**: [jiuwen_memory/foundation/store/filter_dsl.py:1-50](), [jiuwen_memory/memory_core/long_term_memory.py:11-13]()

Sources: [jiuwen_memory/foundation/store/base_memory_index.py:30-70](), [jiuwen_memory/memory_core/long_term_memory.py:40-50]()

---

## 3. Storage, Index & Security Foundations

### SimpleMemoryIndex
A backward-compatible hybrid memory index combining KV storage (`DbBasedKVStore`) and a vector store collection for legacy data layouts (`UMD/{user_id}/{scope_id}/{mem_id}`).
- **Source Files**: [jiuwen_memory/foundation/store/index/simple_memory_index.py:40-70]()

### FileMemoryIndex
A file-system-based memory index storing long-term memories as Markdown files paired with SQLite and `sqlite-vec` full-text/vector indexing.
- **Source Files**: [README.md:83-86](), [docs/en/API Docs/long_term_memory.md:113-121]()

### StorageCodec
An interface for transparent cryptographic encoding and decoding of stored data, concretely implemented by `AesStorageCodec` (AES-256-GCM) and SM4 codecs.
- **Source Files**: [README.md:41-45](), [jiuwen_memory/foundation/codec/__init__.py:1-30](), [jiuwen_memory/memory_core/long_term_memory.py:65-69]()

### DistributedLock
A concurrency control primitive built on top of `DbBasedKVStore` (using `exclusive_set`) to guarantee atomic user-level data operations across multi-instance deployments.
- **Source Files**: [README.md:43-47](), [jiuwen_memory/memory_core/common/distributed_lock.py:1-40](), [jiuwen_memory/foundation/store/kv/db_based_kv_store.py:136-173]()

Sources: [jiuwen_memory/foundation/store/index/simple_memory_index.py:40-70](), [jiuwen_memory/foundation/store/kv/db_based_kv_store.py:136-173]()

---

## 4. Memory Managers & Routing

### WriteManager
The high-level orchestration component that routes incoming messages and extracted memory units to their respective managers (`FragmentMemoryManager`, `SummaryManager`, `VariableManager`).
- **Source Files**: [jiuwen_memory/memory_core/long_term_memory.py:40-41](), [jiuwen_memory/memory_core/manage/index/write_manager.py:1-40]()

### SearchManager
The query routing and execution component responsible for vector similarity searches, keyword filtering, and appending retrieve history records.
- **Source Files**: [jiuwen_memory/memory_core/long_term_memory.py:45-45](), [jiuwen_memory/memory_core/manage/search/search_manager.py:1-50]()

### TenantScope
The configuration and scoping container linking user identifiers and execution parameters to isolated `MemoryScopeConfig` instances within the singleton engine.
- **Source Files**: [README.md:46-48](), [jiuwen_memory/memory_core/long_term_memory.py:17-23]()

Sources: [jiuwen_memory/memory_core/long_term_memory.py:40-45](), [jiuwen_memory/memory_core/manage/index/write_manager.py:1-40]()

---

## 5. Architectural Space Mappings

### Diagram 1: Natural Language Concepts to Core Engine Code Entities
```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        NL_Engine[""LongTermMemoryEngine""]
        NL_Write[""WritePathManager""]
        NL_Search[""SearchPathManager""]
        NL_Fragment[""FragmentMemory""]
        NL_Summary[""SummaryMemory""]
    end

    subgraph "CodeEntitySpace"
        CE_Engine["LongTermMemory jiuwen_memory/memory_core/long_term_memory.py"]
        CE_Write["WriteManager jiuwen_memory/memory_core/manage/index/write_manager.py"]
        CE_Search["SearchManager jiuwen_memory/memory_core/manage/search/search_manager.py"]
        CE_Fragment["FragmentMemoryManager jiuwen_memory/memory_core/manage/index/fragment_memory_manager.py"]
        CE_Summary["SummaryManager jiuwen_memory/memory_core/manage/index/summary_manager.py"]
    end

    NL_Engine --> CE_Engine
    NL_Write --> CE_Write
    NL_Search --> CE_Search
    NL_Fragment --> CE_Fragment
    NL_Summary --> CE_Summary
```
Sources: [jiuwen_memory/memory_core/long_term_memory.py:35-45](), [jiuwen_memory/memory_core/manage/index/fragment_memory_manager.py:53-60]()

### Diagram 2: Storage & Index Terminology to Code Artifacts
```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        NL_SimpleIndex[""SimpleMemoryIndex""]
        NL_FileIndex[""FileMemoryIndex""]
        NL_KVStore[""DatabaseKVStore""]
        NL_Codec[""StorageCodec""]
        NL_Lock[""DistributedLock""]
    end

    subgraph "CodeEntitySpace"
        CE_SimpleIndex["SimpleMemoryIndex jiuwen_memory/foundation/store/index/simple_memory_index.py"]
        CE_FileIndex["FileMemoryIndex jiuwen_memory/foundation/store/index/file_memory_index.py"]
        CE_KVStore["DbBasedKVStore jiuwen_memory/foundation/store/kv/db_based_kv_store.py"]
        CE_Codec["AesStorageCodec jiuwen_memory/foundation/codec/"]
        CE_Lock["DistributedLock jiuwen_memory/memory_core/common/distributed_lock.py"]
    end

    NL_SimpleIndex --> CE_SimpleIndex
    NL_FileIndex --> CE_FileIndex
    NL_KVStore --> CE_KVStore
    NL_Codec --> CE_Codec
    NL_Lock --> CE_Lock
```
Sources: [jiuwen_memory/foundation/store/index/simple_memory_index.py:40-70](), [jiuwen_memory/foundation/store/kv/db_based_kv_store.py:51-62]()