<!-- source: DeepWiki mcp.deepwiki.com · repo bytedance/deer-flow · extra page Projects and Document Shelf · fetched 2026-10-29 -->

# Projects and Document Shelf

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/CLAUDE.md](backend/CLAUDE.md)
- [backend/README.md](backend/README.md)
- [backend/docs/API.md](backend/docs/API.md)
- [backend/docs/ARCHITECTURE.md](backend/docs/ARCHITECTURE.md)
- [backend/docs/README.md](backend/docs/README.md)
- [backend/docs/SANDBOX_MEMORY_PROFILING.md](backend/docs/SANDBOX_MEMORY_PROFILING.md)
- [backend/docs/TODO.md](backend/docs/TODO.md)
- [backend/packages/harness/deerflow/persistence/AGENTS.md](backend/packages/harness/deerflow/persistence/AGENTS.md)
- [backend/packages/harness/deerflow/persistence/bootstrap.py](backend/packages/harness/deerflow/persistence/bootstrap.py)
- [backend/packages/harness/deerflow/persistence/channel_connections/sql.py](backend/packages/harness/deerflow/persistence/channel_connections/sql.py)
- [backend/packages/harness/deerflow/persistence/feedback/sql.py](backend/packages/harness/deerflow/persistence/feedback/sql.py)
- [backend/tests/_repository_race_helpers.py](backend/tests/_repository_race_helpers.py)
- [backend/tests/blocking_io/test_persistence_bootstrap.py](backend/tests/blocking_io/test_persistence_bootstrap.py)
- [backend/tests/test_channel_connections_repository.py](backend/tests/test_channel_connections_repository.py)
- [backend/tests/test_feedback.py](backend/tests/test_feedback.py)
- [backend/tests/test_feedback_router.py](backend/tests/test_feedback_router.py)
- [backend/tests/test_migration_0021_batch_acceptance.py](backend/tests/test_migration_0021_batch_acceptance.py)
- [backend/tests/test_persistence_bootstrap_pg_lock.py](backend/tests/test_persistence_bootstrap_pg_lock.py)
- [backend/tests/test_persistence_forward_revision_compat.py](backend/tests/test_persistence_forward_revision_compat.py)
- [backend/tests/test_sandbox_memory_profile_script.py](backend/tests/test_sandbox_memory_profile_script.py)
- [backend/tests/test_thread_runs_internal_scope.py](backend/tests/test_thread_runs_internal_scope.py)
- [scripts/sandbox_memory_profile.py](scripts/sandbox_memory_profile.py)

</details>



## Purpose and Scope

This document details the architecture and implementation of DeerFlow's **Projects and Document Shelf** subsystem. This subsystem manages grouped user resources, content-addressed storage with deduplication, lazy document conversion pipelines, a robust trash tier with automated retention sweeps, and zero-persistence run-start project context injection.

Sources: `backend/docs/ARCHITECTURE.md()`, `backend/tests/blocking_io/test_project_documents.py()`

---

## 1. Core Data Repositories and Schema

Projects and their associated document shelves are backed by SQLAlchemy models controlled via dedicated repository classes: `ProjectRepository` and `ProjectDocumentRepository`.

### `ProjectRepository` and `ProjectDocumentRepository`
* **`ProjectRepository`**: Manages project metadata, active/archived lifecycle status, ownership scoping (`user_id`), and associated thread references via `threads_meta.project_id`.
* **`ProjectDocumentRepository`**: Manages individual file metadata, content hashes, derivation statuses, and soft-deletion (trash) tiers within a given project namespace.

```
┌────────────────────────────────────────────────────────┐
│                   ProjectRepository                    │
│  - create(name, user_id)                               │
│  - archive / restore                                   │
└──────────────────────────┬─────────────────────────────┘
                           │ 1 : N
                           ▼
┌────────────────────────────────────────────────────────┐
│               ProjectDocumentRepository                │
│  - add_staged_document()                               │
│  - trash(document_id, user_id)                         │
│  - purge(document_id, ...)                             │
│  - restore_document()                                  │
└────────────────────────────────────────────────────────┘
```

> **Diagram 1: Repository Architecture and Data Flow**
> ```mermaid
> graph TD
>     "ClientAPI[Client API Router]" -->|"Project CRUD"| "ProjectRepository[ProjectRepository]"
>     "ClientAPI" -->|"Document Shelf"| "ProjectDocumentRepository[ProjectDocumentRepository]"
>     "ProjectRepository" -->|"SQL Session"| "DB[(Database Engine)]"
>     "ProjectDocumentRepository" -->|"SQL Session"| "DB"
>     "ProjectDocumentRepository" -->|"FS Staging / Rename"| "FileSystem[Host File System Storage]"
> ```

Sources: `backend/docs/ARCHITECTURE.md()`, `backend/tests/blocking_io/test_project_documents.py()`

---

## 2. Content-Addressed Storage and Deduplication

To optimize storage and prevent redundant copies of identical files, document ingestion uses content-addressed storage coupled with SHA-256 hashing.

### Staging and Hashing Pipeline
1. **Spooling**: Incoming file bytes are spooled into a temporary staging location via `stage_document_bytes()` [backend/tests/blocking_io/test_project_documents.py()].
2. **Hashing**: A SHA-256 content hash is computed over the payload chunks.
3. **Deduplication**: When `add_staged_document()` is called, the repository checks for existing records with matching content hashes under the user's scope.
   * **Dedup Hit**: If an identical file exists, the staged temporary file is discarded via `_remove_staging()` through offloaded file I/O, and the existing document record is linked or referenced.
   * **Dedup Miss**: The staged file undergoes an atomic rename (`_place_staging()`) into the canonical content-addressed storage hierarchy.

```
┌─────────────────────────┐
│ Incoming Document Bytes │
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ stage_document_bytes()  │ ──► Compute SHA-256 Hash
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ add_staged_document()   │
└────────────┬────────────┘
             ├─── [Hash Exists]  ──► Discard Staged File (Dedup Hit)
             └─── [New Hash]     ──► Atomic Rename to Storage (Dedup Miss)
```

Sources: `backend/docs/ARCHITECTURE.md()`, `backend/tests/blocking_io/test_project_documents.py()`

---

## 3. Lazy Conversion Pipeline

Documents uploaded to the project shelf can be converted to markdown for agent consumption. DeerFlow handles this via a **lazy conversion pipeline**:
* Conversion outputs are stored in a `.staging/` scratch directory before an atomic rename publishes them into `derived/converted.md`.
* Integrity checks (`_content_intact_batch`) verify that original files remain untouched on disk, offloading blocking filesystem access via `run_file_io()` to keep the async event loop unblocked.

Sources: `backend/docs/TODO.md()`, `backend/tests/blocking_io/test_project_documents.py()`

---

## 4. Trash Tier and Retention Sweeps

Deleted documents are not immediately expunged; instead, they enter a transitional **Trash Tier** managed via the `/api/trash` router endpoints.

### Lifecycle Operations
* **Soft Delete (`trash`)**: Sets document status to trashed and hides it from standard project listings while retaining underlying files.
* **Purge (`purge` / `purge_all_trashed`)**: Atomically removes database rows and unlinks associated storage files (`_unlink_document_files`) within a row-locked transaction.
* **Restore (`restore_document`)**: Recovers documents from the trash tier. If a name collision occurs in the target project upon restoration, a **merge** strategy handles name clashes and cleans up redundant namespace trees (`_remove_namespace_tree`).
* **Automated Retention Sweeps (`run_trash_retention_sweep`)**: Background sweeps reconcile active database rows against physical storage directories, automatically purging items that exceed the configured retention window (e.g., 30 days).

Sources: `backend/docs/ARCHITECTURE.md()`, `backend/tests/blocking_io/test_project_trash.py()`

---

## 5. Project Context Injection

At run admission, the Gateway injects active project configuration and document shelf metadata into the agent execution context without persisting project details into state checkpoints.

### Run-Start Pinning and Middleware Rendering
1. **Resolution**: The Gateway resolves the thread's project membership once via `threads_meta.project_id`, fetching active/archived project details and a bounded shelf snapshot.
2. **Context Injection**: The snapshot is stored under the server-owned `PROJECT_CONTEXT_KEY` runtime context key, which is blocked from client-supplied configuration payloads.
3. **Model Call Formatting**: `DynamicContextMiddleware.wrap_model_call` renders a transient, request-only `HumanMessage` block before model invocation:
   * A `<project>` identity and instructions block.
   * A bounded `<documents>` shelf index containing file counts, byte caps, and entry summaries.
4. **Security & Sanitization**: User-authored project instructions and document names are treated as untrusted text, neutralized, and denylisted (`project`, `documents` in `_BLOCKED_TAG_NAMES`) to prevent prompt injection or tag spoofing. Revision hashes (`project_context_revision`, `project_shelf_revision`) are logged to the run journal via `context:memory` events.

```
┌───────────────────────────┐      ┌──────────────────────────────┐
│  Gateway Run Admission    │ ---> │   PROJECT_CONTEXT_KEY        │
└───────────────────────────┘      └──────────────┬───────────────┘
                                                  ▼
┌───────────────────────────┐      ┌──────────────────────────────┐
│ DynamicContextMiddleware  │ <--- │ Render Transient HumanMessage│
└─────────────┬─────────────┘      └──────────────────────────────┘
              ▼
┌───────────────────────────┐
│ LLM Model Invocation      │ ──► Includes Sanitized <project> & <documents> Blocks
└───────────────────────────┘
```

> **Diagram 2: Project Context Injection Pipeline**
> ```mermaid
> graph TD
>     "RunAdmission[Gateway Run Admission]" -->|"Resolve Membership"| "ProjectRepo[ProjectRepository]"
>     "ProjectRepo" -->|"Project Row & Shelf Snapshot"| "ContextKey[PROJECT_CONTEXT_KEY]"
>     "ContextKey" -->|"Inject Runtime State"| "Middleware[DynamicContextMiddleware.wrap_model_call]"
>     "Middleware" -->|"Sanitize & Render Blocks"| "HumanMsg[Transient HumanMessage]"
>     "HumanMsg" -->|"Prompt Stream"| "LLM[Model Execution Engine]"
> ```

Sources: `backend/docs/ARCHITECTURE.md()`, `backend/tests/blocking_io/test_project_documents.py()`

---

