<!-- source: DeepWiki mcp.deepwiki.com · repo agno-agi/agno · extra page Published Pages and Page Filesystem · fetched 2026-10-26 -->

# Published Pages and Page Filesystem

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/test.yml](.github/workflows/test.yml)
- [cookbook/05_agent_os/27_public_pages/README.md](cookbook/05_agent_os/27_public_pages/README.md)
- [cookbook/05_agent_os/27_public_pages/TEST_LOG.md](cookbook/05_agent_os/27_public_pages/TEST_LOG.md)
- [cookbook/05_agent_os/27_public_pages/documentation_markdown.py](cookbook/05_agent_os/27_public_pages/documentation_markdown.py)
- [cookbook/05_agent_os/27_public_pages/implementation.md](cookbook/05_agent_os/27_public_pages/implementation.md)
- [cookbook/05_agent_os/27_public_pages/migrate_page_source.py](cookbook/05_agent_os/27_public_pages/migrate_page_source.py)
- [cookbook/05_agent_os/27_public_pages/page_tool_results.py](cookbook/05_agent_os/27_public_pages/page_tool_results.py)
- [cookbook/05_agent_os/27_public_pages/public_control_plane.py](cookbook/05_agent_os/27_public_pages/public_control_plane.py)
- [cookbook/05_agent_os/27_public_pages/public_pages.py](cookbook/05_agent_os/27_public_pages/public_pages.py)
- [libs/agno/agno/db/postgres/_bounded.py](libs/agno/agno/db/postgres/_bounded.py)
- [libs/agno/agno/knowledge/knowledge.py](libs/agno/agno/knowledge/knowledge.py)
- [libs/agno/agno/knowledge/page/__init__.py](libs/agno/agno/knowledge/page/__init__.py)
- [libs/agno/agno/knowledge/page/_commands.py](libs/agno/agno/knowledge/page/_commands.py)
- [libs/agno/agno/knowledge/page/_coordinator.py](libs/agno/agno/knowledge/page/_coordinator.py)
- [libs/agno/agno/knowledge/page/_source.py](libs/agno/agno/knowledge/page/_source.py)
- [libs/agno/agno/knowledge/page/filesystem.py](libs/agno/agno/knowledge/page/filesystem.py)
- [libs/agno/agno/knowledge/page/tools.py](libs/agno/agno/knowledge/page/tools.py)
- [libs/agno/agno/knowledge/page/types.py](libs/agno/agno/knowledge/page/types.py)
- [libs/agno/agno/knowledge/reader/utils/mdx.py](libs/agno/agno/knowledge/reader/utils/mdx.py)
- [libs/agno/agno/os/public/__init__.py](libs/agno/agno/os/public/__init__.py)
- [libs/agno/agno/os/public/_limits.py](libs/agno/agno/os/public/_limits.py)
- [libs/agno/agno/os/public/_middleware.py](libs/agno/agno/os/public/_middleware.py)
- [libs/agno/agno/os/public/_policy.py](libs/agno/agno/os/public/_policy.py)
- [libs/agno/tests/integration/knowledge/conftest.py](libs/agno/tests/integration/knowledge/conftest.py)
- [libs/agno/tests/integration/knowledge/test_page_storage.py](libs/agno/tests/integration/knowledge/test_page_storage.py)
- [libs/agno/tests/unit/knowledge/test_page_contract.py](libs/agno/tests/unit/knowledge/test_page_contract.py)
- [libs/agno/tests/unit/knowledge/test_page_tool_results.py](libs/agno/tests/unit/knowledge/test_page_tool_results.py)
- [libs/agno/tests/unit/os/test_public_mcp_config.py](libs/agno/tests/unit/os/test_public_mcp_config.py)
- [libs/agno/tests/unit/reader/test_mdx_normalize.py](libs/agno/tests/unit/reader/test_mdx_normalize.py)

</details>



### Purpose and Scope
This document covers the technical architecture and implementation details of Agno's page subsystem (`agno.knowledge.page`). It details the transactional publication mechanism managed by `PageCoordinator` across catalog, database filesystem (`DbFileSystem`), and vector indexes (`PgVector`), the data models and error types defined in `types.py`, shell-like interactive commands via `PageFileSystem`, agent tool integration across chat and Model Context Protocol (MCP) modes, and administrative source migration.

Sources: [libs/agno/agno/knowledge/page/__init__.py:1-54](), [libs/agno/agno/knowledge/knowledge.py:23-32]()

---

### 1. Page Subsystem Overview & Architecture
The page subsystem provides durable, version-coherent storage, chunked vector indexing, and read-only shell access for documentation corpora (such as `llms.txt` indexes and markdown sites). It is integrated directly into the core `Knowledge` class via `page_store` and `page_search` configuration parameters [libs/agno/agno/knowledge/knowledge.py:70-94]().

The subsystem binds three distinct PostgreSQL-backed storage layers under a single transactional coordinator (`PageCoordinator`):
1. **Catalog Table**: Tracks page revisions, digests, and metadata.
2. **FileSystem (`DbFileSystem`)**: Stores complete normalized page bodies and raw document chunks.
3. **Vector Database (`PgVector`)**: Maintains HNSW-indexed vector embeddings for hybrid/vector search over page chunks.

#### Diagram: Natural Language Space to Code Entity Space — Page Subsystem Architecture
```mermaid
graph TD
    subgraph NaturalLanguageSpace["Natural Language Space"]
        DocCorpus["Documentation Corpus / llms.txt"] --> SyncAgent["Synchronized Page Ingestion"]
        AgentQuery["Agent Query / Search"] --> ToolInv["Page Tool Execution"]
        ShellCmd["Virtual Shell (ls, cat, rg)"] --> FileSys["Read-Only CLI Commands"]
    end

    subgraph CodeEntitySpace["Code Entity Space"]
        DocCorpus -->|"Knowledge.sync_pages()"| KnowledgeClass["agno.knowledge.knowledge.Knowledge"]
        KnowledgeClass -->|"Coordinates"| PageCoord["agno.knowledge.page._coordinator.PageCoordinator"]
        PageCoord -->|"Syncs & Writes"| PostgresTables["PostgreSQL Storage Adapters"]
        
        PostgresTables --> DBTable["BaseDb / KnowledgeRow"]
        PostgresTables --> FSStore["agno.fs.FileSystem / DbFileSystem"]
        PostgresTables --> VectorStore["agno.vectordb.pgvector.PgVector"]

        ToolInv --> PageFS["agno.knowledge.page.filesystem.PageFileSystem"]
        FileSys --> PageFS
        PageFS -->|"run_command()"| CommandRunner["agno.knowledge.page._commands.run_command"]
    end
```
Sources: [libs/agno/agno/knowledge/knowledge.py:70-149](), [libs/agno/agno/knowledge/page/_coordinator.py:105-173](), [libs/agno/agno/knowledge/page/filesystem.py:22-88]()

---

### 2. PageCoordinator Transactional Publication
`PageCoordinator` orchestrates the synchronization of a documentation source into the three-layer store [libs/agno/agno/knowledge/page/_coordinator.py:105-173]().

#### Publication Flow and Data Consistency
When `Knowledge.sync_pages()` or `Knowledge.async_sync_pages()` is invoked, `PageCoordinator` executes the following sequence:
1. **Advisory Locking**: Acquires a namespace-scoped PostgreSQL advisory lock (`pg_advisory_xact_lock`) using a hash of the namespace identifier to prevent concurrent publication collisions [libs/agno/agno/knowledge/page/_coordinator.py:166-170]().
2. **Discovery & Fetching**: Parses the entry point (e.g., `llms.txt`), discovers page URLs, and fetches content via `PageSource` [libs/agno/agno/knowledge/page/_source.py:47-47](). Optional discovery validation callbacks (`validate_discovery`) verify that indexes have not unexpectedly shrunk [cookbook/05_agent_os/27_public_pages/README.md:81-90]().
3. **Normalization & Chunking**: Applies optional markdown transforms (such as `DocumentationMarkdown`) and chunks content using `PageMarkdownChunking` [libs/agno/agno/knowledge/page/_coordinator.py:45-47]() [libs/agno/tests/integration/knowledge/test_page_storage.py:100-110]().
4. **Transactional Write**: Commits updates atomically across the catalog, `DbFileSystem`, and `PgVector` table. If any step fails, the transaction rolls back entirely, ensuring readers never observe partial revisions.

Sources: [libs/agno/agno/knowledge/knowledge.py:102-149](), [libs/agno/agno/knowledge/page/_coordinator.py:105-173](), [libs/agno/tests/integration/knowledge/test_page_storage.py:93-116]()

---

### 3. Page Types and Error Handling
The subsystem exposes a frozen Pydantic model hierarchy and specialized exception types in `agno.knowledge.page.types` [libs/agno/agno/knowledge/page/types.py:1-192]().

#### Core Data Models
* `Page`: Represents a published page entity containing metadata like `content_id`, `namespace`, `path`, `url`, `title`, `revision`, and `digest` [libs/agno/agno/knowledge/page/types.py:110-121]().
* `SearchResult` & `SearchHit`: Encapsulates vector/hybrid search matches with chunk text, scores, and ranking [libs/agno/agno/knowledge/page/types.py:123-141]().
* `PageRead`: Returns paginated or full text reads for specific documentation paths [libs/agno/agno/knowledge/page/types.py:142-152]().
* `PageCommandResult`: Output wrapper for shell-like commands with support for UTF-8 byte bounding via `bounded(max_bytes)` [libs/agno/agno/knowledge/page/types.py:80-108]().
* `SyncReport`: Summarizes reconciliation outcomes (`discovered`, `updated`, `deleted`, `failed`) [libs/agno/agno/knowledge/page/types.py:174-182]().

#### Error Hierarchy
All custom errors inherit from `PageError` (default error code: `"page_unavailable"`):
* `PageNotFound` (`"page_not_found"`): Raised when a requested path does not exist [libs/agno/agno/knowledge/page/types.py:38-39]().
* `PageChanged` (`"page_changed"`): Raised when a page revision mismatch is detected [libs/agno/agno/knowledge/page/types.py:42-43]().
* `SearchUnavailable` (`"search_unavailable"`): Raised when vector search infrastructure fails [libs/agno/agno/knowledge/page/types.py:46-48]().
* `SyncFailed` (`"sync_failed"`): Raised on publication failure [libs/agno/agno/knowledge/page/types.py:50-52]().
* `PageSourceBusy` (`"page_source_busy"`): Raised when a source or namespace is locked by another operation [libs/agno/agno/knowledge/page/types.py:76-78]().

Sources: [libs/agno/agno/knowledge/page/types.py:1-192]()

---

### 4. PageFileSystem Shell-like Commands (`ls`/`cat`/`rg`)
`PageFileSystem` provides a read-only shell adapter that allows agents or developers to interact with a knowledge namespace using familiar UNIX command semantics [libs/agno/agno/knowledge/page/filesystem.py:22-30]().

#### Supported Commands
The underlying command runner (`_commands.py`) parses and executes:
* `ls [path]`: Lists pages and directories.
* `tree [path]`: Renders a hierarchical directory tree.
* `cat <path>`: Outputs the full content of a page.
* `head` / `tail`: Inspects content boundaries.
* `wc`: Counts words, lines, and characters.
* `rg` / `grep <pattern>`: Performs regular expression searching across pages using bounded regex matching (`regex_match_timeout`) [libs/agno/agno/knowledge/page/filesystem.py:37-40]().

#### Execution and Bounding
Commands are dispatched within worker pools (`_COMMAND_WORKERS`) and bounded by execution timeouts (`command_seconds`) [libs/agno/agno/knowledge/page/filesystem.py:19-90](). Output strings are strictly constrained to `max_output_chars` with automatic truncation safeguards [libs/agno/agno/knowledge/page/filesystem.py:36-75]().

Sources: [libs/agno/agno/knowledge/page/filesystem.py:22-123]()

---

### 5. Page Search Tools in Chat and MCP Modes
Agents access the page filesystem through toolkits generated by `PageFileSystem.tools()` [libs/agno/agno/knowledge/page/filesystem.py:124-141]().

#### Tool Configuration and Transports
* **Chat Mode (`transport="chat"`)**: Exposes a natural language command tool (default name: `query_pages`) that catches `PageError` exceptions and formats them as human/agent-readable strings using `tool_error()` [libs/agno/agno/knowledge/page/filesystem.py:129-152]().
* **MCP Mode (`transport="mcp"`)**: Exposes typed command metadata, JSON schemas, and structured error boundaries suitable for Model Context Protocol servers [libs/agno/agno/knowledge/page/filesystem.py:129-138]().

#### Diagram: Page Tool Execution Flow (Chat & MCP Modes)
```mermaid
graph TD
    subgraph AgentRuntime["Agent Runtime"]
        AgentModel["LLM Model Context"] -->|"Calls tool: query_pages(command='ls /')"| ToolkitInvoke["Toolkit.query_pages()"]
    end

    subgraph PageFilesystemLayer["Page Filesystem Layer"]
        ToolkitInvoke -->|"run_command(command)"| PageFS["PageFileSystem"]
        PageFS -->|"Acquires worker"| CommandWorkers["_COMMAND_WORKERS"]
        CommandWorkers -->|"Executes"| CommandRunner["run_command() / run_command_result()"]
        
        CommandRunner -->|"Queries Knowledge Namespace"| DatabaseStore["PostgreSQL DbFileSystem / Catalog"]
    end

    subgraph ResponseHandling["Response Handling"]
        DatabaseStore -->|"Success"| PlainText["Formatted Command Output"]
        DatabaseStore -->|"PageError / Timeout"| ErrorHandler["tool_error(exc) -> JSON / String"]
        PlainText --> AgentModel
        ErrorHandler --> AgentModel
    end
```
Sources: [libs/agno/agno/knowledge/page/filesystem.py:124-154](), [libs/agno/agno/knowledge/page/types.py:188-192]()

---

### 6. Source Migration and Version Management
When documentation sources are relocated (e.g., changing an `llms.txt` URL from an old domain to a new domain), Agno provides transactional source binding and migration tooling.

#### Data Structures
* `PageSourceBinding`: Records the exact binding state across namespace, filesystem, catalog, vectors, source URL, and revision number [libs/agno/agno/knowledge/page/types.py:59-66]().
* `PageSourceMigration`: Encapsulates a migration plan (`before`, `after`, `target_source`, `dry_run`, `changed`) [libs/agno/agno/knowledge/page/types.py:68-74]().

#### Migration Workflow
Administrators execute migrations via scripts or CLI commands. A dry run verifies target validity without mutating bindings, while an applied migration updates the stored `PageSourceBinding` atomically in the catalog database [libs/agno/tests/unit/knowledge/test_page_contract.py:88-130]().

Sources: [libs/agno/agno/knowledge/page/types.py:59-74](), [libs/agno/tests/unit/knowledge/test_page_contract.py:88-130]()

---

