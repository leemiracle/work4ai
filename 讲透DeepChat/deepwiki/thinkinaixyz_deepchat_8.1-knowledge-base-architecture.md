> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/8.1-knowledge-base-architecture](https://deepwiki.com/thinkinaixyz/deepchat/8.1-knowledge-base-architecture)（Wayback 快照 2026-01-18）
> DeepWiki deepchat/8.1-knowledge-base-architecture

# Knowledge Base Architecture

  Relevant source files 
 - [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts)
 - [src/main/presenter/knowledgePresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/index.ts)
 - [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts)
 - [src/main/presenter/knowledgePresenter/knowledgeTaskPresenter.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeTaskPresenter.ts)
 - [src/main/utils/vector.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/utils/vector.ts)
 - [src/shared/dialog.ts](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/shared/dialog.ts)
 
  
## Purpose and Scope

 This document describes the Knowledge Base (RAG) system architecture in DeepChat, which provides built-in Retrieval-Augmented Generation capabilities. The system manages multiple knowledge bases, each with its own vector database, embedding configuration, and file processing pipeline. It handles file ingestion, text chunking, embedding generation, vector storage, and similarity search.

 For information about how knowledge bases integrate with the chat system, see [Knowledge Base User Interface](https://deepwiki.com/thinkinaixyz/deepchat/8.6-knowledge-base-user-interface). For details about embedding generation and task scheduling, see [Embedding Generation and Task Queue](https://deepwiki.com/thinkinaixyz/deepchat/8.4-embedding-generation-and-task-queue). For similarity search implementation, see [Similarity Search and Retrieval](https://deepwiki.com/thinkinaixyz/deepchat/8.5-similarity-search-and-retrieval).

 
---

 
## System Components Overview

 The knowledge base system consists of four main components that work together to provide RAG functionality:

 **Component Architecture**

 
```

```

 Sources: [src/main/presenter/knowledgePresenter/index.ts29-62](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/index.ts#L29-L62) [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts21-47](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L21-L47)

 
| Component | Responsibility | Lifecycle |
|---|---|---|
| KnowledgePresenter | Orchestrates all knowledge bases, handles configuration changes, manages instance cache | Singleton, created on app start |
| KnowledgeStorePresenter | Manages file processing, chunking, embedding coordination for a single knowledge base | One per enabled knowledge base config |
| DuckDBPresenter | Provides vector database operations, HNSW indexing, transaction management | One per knowledge base, matches KnowledgeStorePresenter |
| KnowledgeTaskPresenter | Global task queue for embedding generation, limits concurrency to 16 tasks | Singleton, shared across all knowledge bases |

 Sources: [src/main/presenter/knowledgePresenter/index.ts29-62](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/index.ts#L29-L62) [src/main/presenter/knowledgePresenter/knowledgeTaskPresenter.ts12-20](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeTaskPresenter.ts#L12-L20)

 
---

 
## KnowledgePresenter: Central Orchestrator

 The `KnowledgePresenter` class serves as the central coordination point for all knowledge base operations. It is instantiated once during application initialization and manages the lifecycle of individual knowledge base instances.

 **Key Responsibilities**

 
```

```

 Sources: [src/main/presenter/knowledgePresenter/index.ts29-117](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/index.ts#L29-L117) [src/main/presenter/knowledgePresenter/index.ts186-252](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/index.ts#L186-L252)

 
### Configuration Change Handling

 The system listens to `MCP_EVENTS.CONFIG_CHANGED` events and processes configuration updates through a diff-based approach:

 
```

```

 Sources: [src/main/presenter/knowledgePresenter/index.ts73-117](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/index.ts#L73-L117)

 
### Storage Directory Structure

 The `KnowledgePresenter` initializes a storage directory at `{dbDir}/KnowledgeBase/` and creates subdirectories for each knowledge base using their configuration IDs:

 
```
dbDir/
└── KnowledgeBase/
    ├── kb_id_1/          # DuckDB database files
    ├── kb_id_1.wal       # Write-Ahead Log (if exists)
    ├── kb_id_2/
    └── kb_id_2.wal
```

 Sources: [src/main/presenter/knowledgePresenter/index.ts56-71](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/index.ts#L56-L71) [src/main/presenter/knowledgePresenter/index.ts172-179](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/index.ts#L172-L179)

 
### Platform Support Check

 The system only supports specific operating systems due to DuckDB native dependency requirements:

 
| Platform | Architecture | Supported |
|---|---|---|
| Windows | x64 | ✓ |
| Linux | x64 | ✓ |
| Linux | arm64 | ✓ |
| macOS | arm64 | ✓ |
| macOS | x64 | ✓ |

 Sources: [src/main/presenter/knowledgePresenter/index.ts122-133](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/index.ts#L122-L133)

 
### File Validation Integration

 The `KnowledgePresenter` delegates to `FilePresenter` for file validation before processing:

 
```

```

 Sources: [src/main/presenter/knowledgePresenter/index.ts392-416](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/index.ts#L392-L416) [src/main/presenter/knowledgePresenter/index.ts422-460](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/index.ts#L422-L460)

 
---

 
## KnowledgeStorePresenter: Per-Knowledge-Base Instance

 Each enabled knowledge base has a dedicated `KnowledgeStorePresenter` instance that manages file processing, chunking, and embedding coordination for that specific knowledge base.

 **Instance Architecture**

 
```

```

 Sources: [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts21-47](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L21-L47)

 
### File Queue Management

 To ensure thread-safe database operations, the `KnowledgeStorePresenter` implements a per-file task queue using `fileQueueMap`. All database operations for a specific file are serialized through this queue:

 
```

```

 This pattern ensures that operations like `insertFile`, `updateFile`, `insertChunks`, and `insertVector` for the same file never execute concurrently, preventing transaction conflicts.

 Sources: [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts27-37](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L27-L37) [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts90-93](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L90-L93)

 
### File Processing Workflow

 **Complete File Ingestion Flow**

 
```

```

 Sources: [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts60-103](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L60-L103) [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts106-190](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L106-L190)

 
### Chunk Processing Task

 Each text chunk is processed as an independent task in the global task queue:

 
```

```

 The `processChunkTask` method:

 
 - Generates embeddings via `llmproviderPresenter.getEmbeddings()`
 - Checks `signal.aborted` for task cancellation
 - Updates chunk status to 'completed'
 - Inserts vector into database
 
 Sources: [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts164-185](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L164-L185) [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts193-229](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L193-L229)

 
### Progress Tracking

 The `fileProgressMap` tracks processing progress for each file:

 
```

```

 Progress events are emitted to the renderer on each chunk completion or error:

 
```

```

 When all chunks complete (`completed + error === total`), the file status is updated to 'completed' and `RAG_EVENTS.FILE_UPDATED` is emitted.

 Sources: [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts26](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L26-L26) [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts232-254](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L232-L254) [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts288-302](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L288-L302)

 
### Task Pause and Resume

 The `KnowledgeStorePresenter` supports pausing and resuming file processing:

 **Pause Flow:**

 
 - Cancel all running tasks via `taskP.cancelTasksByKnowledgeBase()`
 - Clear `fileProgressMap`
 - Update database chunk/file status to 'paused' via `vectorP.pauseAllRunningTasks()`
 
 **Resume Flow:**

 
 - Query all chunks with status='paused' from database
 - Rebuild `fileProgressMap` by counting paused chunks per file
 - Update database status to 'processing' via `vectorP.resumeAllPausedTasks()`
 - Re-add each paused chunk as a task to `taskP`
 
 Sources: [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts391-436](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L391-L436)

 
---

 
## DuckDBPresenter: Vector Database Layer

 The `DuckDBPresenter` implements the `IVectorDatabasePresenter` interface and provides vector storage, HNSW indexing, and similarity search using DuckDB with the VSS extension.

 **Database Schema**

 
```

```

 Sources: [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts66-79](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts#L66-L79) [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts718-799](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts#L718-L799)

 
### Table Definitions

 
| Table | Purpose | Key Columns |
|---|---|---|
| metadata | Stores database version and metadata | key (PK), value |
| file | File metadata and processing status | id (PK), path, status, metadata (JSON) |
| chunk | Text chunks from files | id (PK), file_id (FK), content, status, chunk_index |
| vector | Vector embeddings with HNSW index | id (PK), embedding (FLOAT[dimensions]), file_id (FK), chunk_id (FK) |

 The `file.metadata` JSON field stores:

 
 - `size`: File size in bytes
 - `totalChunks`: Number of chunks generated
 - `errorReason`: Error message if processing failed
 
 Sources: [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts718-799](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts#L718-L799)

 
### Transaction Queue System

 To ensure data consistency, all write operations are serialized through a transaction queue. This prevents concurrent modifications and race conditions:

 
```

```

 Sources: [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts469-606](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts#L469-L606)

 **Transaction Queue Properties:**

 
 - All operations within a batch succeed or fail atomically
 - Operations are processed in FIFO order
 - Maximum transaction timeout: 30 seconds
 - Timeout operations are automatically rejected
 - Queue continues processing until empty
 
 Sources: [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts478-496](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts#L478-L496) [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts519-538](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts#L519-L538)

 
### HNSW Index Configuration

 The vector table uses Hierarchical Navigable Small World (HNSW) indexing for efficient similarity search:

 
```

```

 
| Parameter | Default | Purpose |
|---|---|---|
| metric | 'cosine' | Distance metric: cosine, l2sq (L2 squared), or ip (inner product) |
| M | 16 | Number of bidirectional links per node |
| ef_construction | 200 | Size of dynamic candidate list during construction |

 Sources: [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts759-799](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts#L759-L799)

 
### Similarity Query Implementation

 The `similarityQuery` method performs vector similarity search with configurable metrics:

 
```

```

 **Query Construction:**

 
```

```

 The function name is selected based on `options.metric`:

 
 - `'cosine'` → `array_cosine_distance`
 - `'ip'` → `array_negative_inner_product`
 - `'l2sq'` → `array_distance`
 
 Sources: [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts397-435](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts#L397-L435)

 
### Database Migration System

 The `DuckDBPresenter` includes a migration framework for schema evolution:

 
```

```

 Sources: [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts844-898](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts#L844-L898)

 **Migration Definition Structure:**

 
```

```

 Sources: [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts28-64](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts#L28-L64)

 
### WAL File Recovery

 When the database is opened with a Write-Ahead Log (WAL) file present (indicating abnormal shutdown), the `repairIndex` method performs recovery:

 
 - Creates an in-memory DuckDB instance
 - Loads the VSS extension in memory
 - Attaches to the existing database file
 - Allows automatic checkpoint to proceed
 - Closes temporary connection
 
 This approach works around the issue where DuckDB's automatic checkpoint fails when the VSS extension isn't loaded.

 Sources: [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts673-697](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts#L673-L697) [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts118-126](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts#L118-L126)

 
### Dirty Data Cleanup

 On database open, orphaned records are cleaned up:

 
```

```

 Sources: [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts804-816](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts#L804-L816)

 
---

 
## KnowledgeTaskPresenter: Global Task Queue

 The `KnowledgeTaskPresenter` implements a global task scheduling system shared by all knowledge base instances. It limits concurrent embedding generation to 16 tasks to prevent resource exhaustion.

 **Task Queue Architecture**

 
```

```

 Sources: [src/main/presenter/knowledgePresenter/knowledgeTaskPresenter.ts12-47](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeTaskPresenter.ts#L12-L47)

 
### Task Structure

 Each task added to the queue must implement the `KnowledgeChunkTask` interface:

 
```

```

 Sources: [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts165-182](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L165-L182)

 
### Concurrency Control

 The `processQueue` method ensures that the number of running tasks never exceeds `maxConcurrency`:

 
```

```

 Sources: [src/main/presenter/knowledgePresenter/knowledgeTaskPresenter.ts141-170](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeTaskPresenter.ts#L141-L170)

 
### Task Cancellation

 The system provides multiple cancellation methods:

 
| Method | Filter | Use Case |
|---|---|---|
| removeTasks(filter) | Custom function | Generic task removal based on predicate |
| cancelTasksByKnowledgeBase(id) | task.payload.knowledgeBaseId === id | Remove all tasks for a knowledge base |
| cancelTasksByFile(fileId) | task.payload.fileId === fileId | Remove all tasks for a specific file |

 Cancellation process:

 
 - Filter tasks from queue
 - Abort running tasks via `AbortController`
 - Call `task.onTerminate()` callback
 - Clean up controller and running task references
 
 Sources: [src/main/presenter/knowledgePresenter/knowledgeTaskPresenter.ts29-57](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeTaskPresenter.ts#L29-L57)

 
### Task Status Monitoring

 The `getTaskStatus()` method provides real-time visibility into task execution:

 
```

```

 This status is used for:

 
 - UI progress indicators
 - Preventing application quit while tasks are running (via `beforeDestroy()`)
 - Debugging and monitoring
 
 Sources: [src/main/presenter/knowledgePresenter/knowledgeTaskPresenter.ts60-86](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeTaskPresenter.ts#L60-L86) [src/main/presenter/knowledgePresenter/index.ts326-343](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/index.ts#L326-L343)

 
---

 
## Configuration Management

 Knowledge base configurations are stored within the MCP server configuration system under the special `builtinKnowledge` server entry.

 **Configuration Flow**

 
```

```

 Sources: [src/main/presenter/knowledgePresenter/index.ts73-117](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/index.ts#L73-L117)

 
### BuiltinKnowledgeConfig Structure

 
```

```

 Sources: [src/main/presenter/knowledgePresenter/index.ts4-12](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/index.ts#L4-L12)

 
### Text Splitting Configuration

 The system uses `RecursiveCharacterTextSplitter` with configurable separators. Language-specific separators can be retrieved via:

 
```

```

 Sources: [src/main/presenter/knowledgePresenter/index.ts371-385](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/index.ts#L371-L385)

 
---

 
## Vector Distance Metrics

 The system supports two primary distance metrics for similarity search, selected based on whether embeddings are normalized.

 **Metric Selection Logic**

 
```

```

 
| Metric | DuckDB Function | Used When | Distance Range | Similarity Interpretation |
|---|---|---|---|---|
| cosine | array_cosine_distance | Embeddings are normalized (L2 norm ≈ 1) | [0, 1] | 0 = identical, 1 = orthogonal |
| ip (inner product) | array_negative_inner_product | Embeddings are not normalized | [-∞, +∞] | Negative = similar, Positive = dissimilar |

 Sources: [src/main/utils/vector.ts95-102](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/utils/vector.ts#L95-L102)

 
### Distance Normalization

 Raw distances are normalized to confidence scores in the range [0, 1] using the `normalizeDistance` function:

 **Cosine Distance:**

 
```

```

 **Inner Product Distance:**

 
```

```

 This normalization is applied in `KnowledgeStorePresenter.similarityQuery()` after retrieving results from DuckDB.

 Sources: [src/main/utils/vector.ts66-93](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/utils/vector.ts#L66-L93) [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts340-360](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L340-L360)

 
### Vector Normalization Utilities

 The `vector.ts` module provides utilities for vector normalization:

 
```

```

 Note: Embeddings are not automatically normalized by the system because vector magnitude may carry semantic meaning in certain applications. Normalization must be configured explicitly via the `normalized` field in `BuiltinKnowledgeConfig`.

 Sources: [src/main/utils/vector.ts10-63](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/utils/vector.ts#L10-L63)

 
---

 
## Event-Driven Progress Updates

 The knowledge base system emits events to the renderer process for real-time UI updates:

 
| Event | When Emitted | Payload |
|---|---|---|
| RAG_EVENTS.FILE_UPDATED | File status changes (processing → completed/error) | KnowledgeFileMessage |
| RAG_EVENTS.FILE_PROGRESS | Each chunk completes or errors | { fileId, completed, error, total } |

 These events are broadcast to all windows using `SendTarget.ALL_WINDOWS`:

 
```

```

 This enables multiple windows to display synchronized progress updates for the same knowledge base operations.

 Sources: [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts18-19](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L18-L19) [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts128](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L128-L128) [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts145](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L145-L145) [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts241-246](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L241-L246)

 
---

 
## Integration Points

 The knowledge base system integrates with other DeepChat subsystems:

 
| Integration Point | Component | Purpose |
|---|---|---|
| Configuration | ConfigPresenter | Stores and retrieves BuiltinKnowledgeConfig[], computes diffs |
| File Processing | FilePresenter | Validates files, extracts content, determines MIME types |
| Embedding Generation | LLMProviderPresenter | Generates embeddings via getEmbeddings(providerId, modelId, texts) |
| UI Updates | EventBus | Broadcasts file progress and status changes to renderer |
| Dialog System | DialogPresenter | Shows confirmation dialog before quitting with pending tasks |
| MCP Integration | Built-in MCP server | Exposes knowledge base as an MCP tool for function calling |

 Sources: [src/main/presenter/knowledgePresenter/index.ts35-40](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/index.ts#L35-L40) [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts13-19](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L13-L19) [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts199-203](https://github.com/thinkinaixyz/deepchat/blob/c0de19ee/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L199-L203)
