<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/agent-memory · page 2 Memory Core Engine · fetched 2026-11-02 -->

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

