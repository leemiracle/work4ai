> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/8.2-file-processing-pipeline](https://deepwiki.com/thinkinaixyz/deepchat/8.2-file-processing-pipeline)（Wayback 快照 2026-04-11 RSC payload 提取）
> DeepWiki thinkinaixyz/deepchat · 世代: 2026-04

# File Processing Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/main/presenter/filePresenter/BaseFileAdapter.ts](src/main/presenter/filePresenter/BaseFileAdapter.ts)
- [src/main/presenter/filePresenter/FileAdapterConstructor.ts](src/main/presenter/filePresenter/FileAdapterConstructor.ts)
- [src/main/presenter/filePresenter/FilePresenter.ts](src/main/presenter/filePresenter/FilePresenter.ts)
- [src/main/presenter/filePresenter/FileValidationService.ts](src/main/presenter/filePresenter/FileValidationService.ts)
- [src/main/presenter/filePresenter/ImageFileAdapter.ts](src/main/presenter/filePresenter/ImageFileAdapter.ts)
- [src/main/presenter/filePresenter/mime.ts](src/main/presenter/filePresenter/mime.ts)
- [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts](src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts)
- [src/main/presenter/knowledgePresenter/index.ts](src/main/presenter/knowledgePresenter/index.ts)
- [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts](src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts)
- [src/main/presenter/knowledgePresenter/knowledgeTaskPresenter.ts](src/main/presenter/knowledgePresenter/knowledgeTaskPresenter.ts)
- [src/main/utils/vector.ts](src/main/utils/vector.ts)
- [src/renderer/src/components/editor/mention/PromptParamsDialog.vue](src/renderer/src/components/editor/mention/PromptParamsDialog.vue)
- [src/renderer/src/components/editor/mention/mention.ts](src/renderer/src/components/editor/mention/mention.ts)
- [src/shared/dialog.ts](src/shared/dialog.ts)

</details>



This document describes the file processing pipeline within the Knowledge Base system that transforms raw files into searchable vector embeddings. The pipeline handles validation, content extraction, text chunking, and asynchronous embedding generation.

For general file handling and adapter patterns, see [File Adapter Architecture](#9.1). For vector database operations, see [Vector Database & DuckDB](#10.3). For task scheduling details, see [Task Scheduling & Concurrency](#10.4).

---

## Pipeline Overview

The file processing pipeline executes in two phases:

1. **Synchronous Phase**: File validation → metadata insertion → content extraction → text chunking → chunk record creation
2. **Asynchronous Phase**: Chunk embedding generation → vector insertion (managed by task queue)

The pipeline is designed to provide immediate feedback to users while processing chunks in the background with controlled concurrency (max 16 concurrent tasks).

**Key Design Principles:**
- Files are immediately visible in the UI with `processing` status
- Chunk processing is fully asynchronous to prevent UI blocking
- Thread-safe operations via file-level queue (`enqueueFileTask`)
- Progress tracking at both file and chunk level
- Graceful error handling with per-chunk status tracking

Sources: [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts:1-463]()

---

## Pipeline Architecture

```mermaid
graph TB
    subgraph "Entry Points"
        API_addFile["KnowledgePresenter.addFile()"]
        API_reAddFile["KnowledgePresenter.reAddFile()"]
    end
    
    subgraph "Synchronous Phase"
        Validate["FileValidationService<br/>validateFile()"]
        CheckDup["Check Duplicates<br/>queryFiles()"]
        CreateMeta["Create KnowledgeFileMessage<br/>status: 'processing'"]
        InsertDB["Insert to DuckDB<br/>file table"]
        ExtractContent["FilePresenter<br/>prepareFileCompletely()"]
        SplitText["RecursiveCharacterTextSplitter<br/>splitText()"]
        CreateChunks["Create KnowledgeChunkMessage[]<br/>insertChunks()"]
        InitProgress["Initialize fileProgressMap<br/>{completed: 0, error: 0, total: N}"]
    end
    
    subgraph "Asynchronous Phase"
        TaskQueue["KnowledgeTaskPresenter<br/>addTask()"]
        ProcessChunk["processChunkTask()<br/>Per-chunk execution"]
        GenEmbedding["LLMProviderPresenter<br/>getEmbeddings()"]
        UpdateChunk["Update chunk status<br/>updateChunkStatus()"]
        InsertVector["Insert vector<br/>insertVector()"]
    end
    
    subgraph "Completion"
        TrackProgress["fileProgressMap<br/>Update progress"]
        CheckComplete["All chunks processed?"]
        FinalizeFile["Update file status<br/>status: 'completed'"]
        EventBus["EventBus<br/>RAG_EVENTS.FILE_UPDATED"]
    end
    
    API_addFile --> Validate
    API_reAddFile --> Validate
    Validate --> CheckDup
    CheckDup --> CreateMeta
    CreateMeta --> InsertDB
    InsertDB --> ExtractContent
    ExtractContent --> SplitText
    SplitText --> CreateChunks
    CreateChunks --> InitProgress
    InitProgress --> TaskQueue
    
    TaskQueue --> ProcessChunk
    ProcessChunk --> GenEmbedding
    GenEmbedding --> UpdateChunk
    UpdateChunk --> InsertVector
    InsertVector --> TrackProgress
    TrackProgress --> CheckComplete
    CheckComplete -->|Yes| FinalizeFile
    CheckComplete -->|No| ProcessChunk
    FinalizeFile --> EventBus
```

**Sources:** [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts:60-320](), [src/main/presenter/knowledgePresenter/index.ts:279-288]()

---

## File Validation

Before processing begins, files are validated by `FileValidationService` to ensure they are suitable for knowledge base ingestion. The validation system excludes certain file types that are not processable for text-based RAG.

### Validation Logic

```mermaid
graph TB
    Start["validateFile(filePath)"]
    DetectMime["detectMimeType(filePath)<br/>MIME detection"]
    GetAdapter["getMimeTypeAdapterMap()<br/>Find adapter"]
    CheckExcluded["Is adapter excluded?<br/>AudioFileAdapter<br/>ImageFileAdapter<br/>UnsupportFileAdapter<br/>DirectoryAdapter"]
    ReturnSupported["Return:<br/>isSupported: true<br/>mimeType, adapterType"]
    ReturnUnsupported["Return:<br/>isSupported: false<br/>error, suggestedExtensions"]
    
    Start --> DetectMime
    DetectMime --> GetAdapter
    GetAdapter --> CheckExcluded
    CheckExcluded -->|Not Excluded| ReturnSupported
    CheckExcluded -->|Excluded| ReturnUnsupported
```

### Excluded Adapters

The following adapters are excluded from knowledge base processing:

| Adapter | Reason |
|---------|--------|
| `AudioFileAdapter` | Cannot extract text content from audio files |
| `ImageFileAdapter` | Images require vision models, not text-based RAG |
| `UnsupportFileAdapter` | Unsupported file format |
| `DirectoryAdapter` | Directories are not files |

### Supported File Types

The validation service returns supported extensions by examining the MIME type adapter map and filtering out excluded adapters. Common supported types include:

- **Text**: txt, md, markdown
- **Documents**: pdf, docx, pptx, xlsx
- **Data**: csv, json, yaml, yml, xml
- **Code**: js, ts, py, java, cpp, c, h, css, html

**Sources:** [src/main/presenter/filePresenter/FileValidationService.ts:20-227](), [src/main/presenter/knowledgePresenter/index.ts:392-460]()

---

## Synchronous Processing Phase

The synchronous phase executes immediately when a file is added and prepares all metadata and chunks before returning control to the caller.

### Step 1: File Metadata Creation

```mermaid
sequenceDiagram
    participant User
    participant KP as KnowledgePresenter
    participant KSP as KnowledgeStorePresenter
    participant FP as FilePresenter
    participant DB as DuckDBPresenter
    
    User->>KP: addFile(id, filePath)
    KP->>FP: getMimeType(filePath)
    FP-->>KP: mimeType
    KP->>KSP: addFile(filePath, fileId?)
    
    KSP->>DB: queryFiles({path: filePath})
    DB-->>KSP: existingFile[]
    
    alt File already exists
        KSP-->>KP: {data: existingFile[0]}
    else New file
        KSP->>KSP: Create KnowledgeFileMessage<br/>{id, name, path, mimeType,<br/>status: 'processing',<br/>metadata: {size: -1, totalChunks: 0}}
        KSP->>DB: insertFile(fileMessage)
        KSP->>KSP: processFileAsync(fileMessage)
        KSP-->>KP: {data: fileMessage}
    end
```

**Data Structure: KnowledgeFileMessage**

```typescript
{
  id: string              // Unique file identifier (nanoid)
  name: string            // File basename
  path: string            // Absolute file path
  mimeType: string        // Detected MIME type
  status: 'processing' | 'completed' | 'error' | 'paused'
  uploadedAt: number      // Timestamp
  metadata: {
    size: number          // File size in bytes
    totalChunks: number   // Number of text chunks
    errorReason?: string  // Error message if status is 'error'
  }
}
```

**Sources:** [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts:60-103]()

### Step 2: Content Extraction

Content extraction delegates to `FilePresenter.prepareFileCompletely()` with `contentType: 'origin'` to retrieve raw text content without LLM-specific formatting.

```mermaid
graph LR
    Start["processFileAsync()"]
    PrepFile["FilePresenter<br/>prepareFileCompletely()<br/>contentType: 'origin'"]
    CreateAdapter["createFileAdapter(path, mimeType)"]
    ProcessFile["adapter.processFile()"]
    GetContent["adapter.getContent()"]
    ValidateContent["Content empty?"]
    
    Start --> PrepFile
    PrepFile --> CreateAdapter
    CreateAdapter --> ProcessFile
    ProcessFile --> GetContent
    GetContent --> ValidateContent
    
    ValidateContent -->|Yes| ErrorState["Set file status: 'error'<br/>errorReason: '无法读取文件...'"]
    ValidateContent -->|No| Continue["Continue to chunking"]
```

If content extraction fails or returns empty content, the file status is immediately set to `error` with an appropriate error message, and processing halts.

**Sources:** [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts:108-129](), [src/main/presenter/filePresenter/FilePresenter.ts:121-174]()

### Step 3: Text Chunking

Text is split into overlapping chunks using `RecursiveCharacterTextSplitter` from `@/lib/textsplitters`. Chunking parameters are configured per-knowledge-base.

**Chunking Configuration:**

| Parameter | Description | Source |
|-----------|-------------|--------|
| `chunkSize` | Maximum characters per chunk | `config.chunkSize` |
| `chunkOverlap` | Overlapping characters between chunks | `config.chunkOverlap` |
| `separators` | Split priority: paragraph → sentence → word → character | `config.separators` |

**Text Preprocessing:**

Before chunking, text is sanitized using `sanitizeText()` utility to:
- Normalize whitespace
- Remove control characters
- Ensure consistent line endings

**Sources:** [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts:133-143]()

### Step 4: Chunk Record Creation

After splitting, chunk records are created and inserted into the database. Each chunk is assigned a sequential index and an ID combining the file ID and chunk index.

```mermaid
graph TB
    Chunks["Text chunks<br/>string[]"]
    MapChunks["Map to KnowledgeChunkMessage[]"]
    InsertDB["DuckDB.insertChunks()"]
    InitProgress["Initialize fileProgressMap<br/>{completed: 0, error: 0, total: N}"]
    CreateTasks["Create chunk tasks"]
    
    Chunks --> MapChunks
    MapChunks --> InsertDB
    InsertDB --> InitProgress
    InitProgress --> CreateTasks
```

**Data Structure: KnowledgeChunkMessage**

```typescript
{
  id: string              // `${fileId}_${chunkIndex}`
  fileId: string          // Parent file ID
  chunkIndex: number      // Sequential chunk number (0-based)
  content: string         // Text content of chunk
  status: 'processing' | 'completed' | 'error' | 'paused'
  error?: string          // Error message if status is 'error'
}
```

**Sources:** [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts:148-165]()

---

## Asynchronous Processing Phase

After synchronous setup completes, individual chunks are processed asynchronously via the task queue system. Each chunk is an independent task that can be retried, paused, or cancelled.

### Task Creation and Scheduling

```mermaid
graph TB
    subgraph "Task Structure"
        TaskDef["KnowledgeChunkTask {<br/>id: 'chunk_' + chunkId<br/>payload: {<br/>  knowledgeBaseId<br/>  fileId<br/>  chunkId<br/>  taskType: 'chunk_processing'<br/>  metadata: {content, chunkIndex}<br/>}<br/>run: processChunkTask<br/>onSuccess: handleChunkCompletion<br/>onError: handleChunkError<br/>onTerminate: cleanup<br/>}"]
    end
    
    subgraph "Task Queue"
        Queue["KnowledgeTaskPresenter<br/>queue: KnowledgeChunkTask[]<br/>maxConcurrency: 16"]
        AddTask["addTask(chunkTask)"]
        ProcessQueue["processQueue()"]
    end
    
    subgraph "Execution"
        RunTask["task.run({signal})"]
        Callbacks["onSuccess / onError / onTerminate"]
    end
    
    TaskDef --> AddTask
    AddTask --> Queue
    Queue --> ProcessQueue
    ProcessQueue --> RunTask
    RunTask --> Callbacks
```

The task queue maintains two data structures:
- `queue: KnowledgeChunkTask[]` - pending tasks
- `runningTasks: Map<string, KnowledgeChunkTask>` - currently executing tasks

Tasks are executed with `AbortController` signals to support cancellation.

**Sources:** [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts:163-185](), [src/main/presenter/knowledgePresenter/knowledgeTaskPresenter.ts:22-27]()

### Chunk Task Execution

The core processing function `processChunkTask()` generates embeddings and inserts vectors:

```mermaid
sequenceDiagram
    participant Queue as KnowledgeTaskPresenter
    participant Task as processChunkTask
    participant LLM as LLMProviderPresenter
    participant DB as DuckDBPresenter
    participant Progress as fileProgressMap
    
    Queue->>Task: run({signal})
    
    Task->>LLM: getEmbeddings(providerId, modelId, [content])
    LLM-->>Task: vectors: number[][]
    
    alt Embeddings generated
        Task->>Task: Check signal.aborted
        
        alt Not aborted
            Task->>DB: enqueueFileTask(() => {<br/>  updateChunkStatus('completed')<br/>  insertVector({vector, fileId, chunkId})<br/>})
            DB-->>Task: Success
            Task-->>Queue: onSuccess()
            Queue->>Progress: Increment completed count
        else Aborted
            Task-->>Queue: throw AbortError
            Queue->>Task: onTerminate()
        end
    else Embedding failed
        Task-->>Queue: throw Error
        Queue->>Task: onError(error)
        Queue->>Progress: Increment error count
        Queue->>DB: updateChunkStatus('error', errorMessage)
    end
```

**Thread Safety:**

All database operations are wrapped in `enqueueFileTask(fileId, operation)` which maintains a per-file queue to ensure serialized access to DuckDB for the same file. This prevents race conditions when multiple chunks from the same file are processed concurrently.

**Sources:** [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts:192-229]()

### Progress Tracking

Progress is tracked at two levels:

1. **File-Level Progress:** `fileProgressMap` tracks overall file processing status
2. **UI Events:** Real-time updates sent via EventBus

```mermaid
graph TB
    Complete["Chunk completes"]
    Error["Chunk errors"]
    UpdateMap["Update fileProgressMap<br/>{completed++, error++, total}"]
    SendEvent["EventBus.sendToRenderer<br/>RAG_EVENTS.FILE_PROGRESS<br/>{fileId, completed, error, total}"]
    CheckDone["completed + error == total?"]
    FinalizeFile["onFileFinish()<br/>Update file status to 'completed'<br/>Send FILE_UPDATED event"]
    
    Complete --> UpdateMap
    Error --> UpdateMap
    UpdateMap --> SendEvent
    SendEvent --> CheckDone
    CheckDone -->|Yes| FinalizeFile
    CheckDone -->|No| Continue["Continue processing"]
```

**Progress Data Structure:**

```typescript
{
  fileId: string
  completed: number   // Successfully embedded chunks
  error: number       // Failed chunks
  total: number       // Total chunks
}
```

When all chunks are processed (success or error), the file status is updated to `completed`, and a final `FILE_UPDATED` event is sent.

**Sources:** [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts:232-302]()

---

## Error Handling

The pipeline implements multi-level error handling to isolate failures and provide actionable feedback.

### Error Isolation Strategy

| Level | Scope | Behavior |
|-------|-------|----------|
| **File Level** | Content extraction failure | Mark file as `error`, halt all processing |
| **Chunk Level** | Individual chunk embedding failure | Mark chunk as `error`, continue processing other chunks |
| **Task Level** | Task cancellation/abortion | Call `onTerminate`, clean up resources |

### Error States

**File Error State:**

```typescript
{
  status: 'error',
  metadata: {
    errorReason: string  // Human-readable error message
  }
}
```

**Chunk Error State:**

```typescript
{
  status: 'error',
  error: string  // Error message from embedding generation
}
```

### Error Recovery

Files in `error` state can be retried using `reAddFile()`:

```mermaid
graph LR
    ReAdd["reAddFile(fileId)"]
    QueryFile["queryFile(fileId)"]
    DeleteChunks["deleteChunksByFile(fileId)"]
    DeleteVectors["deleteVectorsByFile(fileId)"]
    AddFile["addFile(file.path, fileId)"]
    
    ReAdd --> QueryFile
    QueryFile --> DeleteChunks
    DeleteChunks --> DeleteVectors
    DeleteVectors --> AddFile
```

This clears all existing chunks and vectors, then re-processes the file from scratch while preserving the original file ID and database record.

**Sources:** [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts:361-369](), [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts:256-286]()

---

## Concurrency and Thread Safety

### File Queue Mechanism

The `enqueueFileTask()` method ensures thread-safe database operations for a single file:

```mermaid
graph TB
    Op1["Operation 1<br/>updateFile()"]
    Op2["Operation 2<br/>insertChunks()"]
    Op3["Operation 3<br/>updateChunkStatus()"]
    Op4["Operation 4<br/>insertVector()"]
    
    Queue["fileQueueMap.get(fileId)<br/>Promise chain"]
    
    Op1 --> Queue
    Queue --> Op2
    Op2 --> Queue
    Queue --> Op3
    Op3 --> Queue
    Queue --> Op4
```

**Implementation:**

```typescript
private fileQueueMap = new Map<string, Promise<void>>()

private async enqueueFileTask(fileId: string, task: () => Promise<void>): Promise<void> {
  const last = this.fileQueueMap.get(fileId) ?? Promise.resolve()
  const next = last.then(task).catch((err) => {
    console.error(`[RAG] Error in queued task for file ${fileId}:`, err)
  })
  this.fileQueueMap.set(fileId, next)
  await next
}
```

This creates a sequential promise chain per file, ensuring operations execute in order even when multiple chunks are processed concurrently.

**Sources:** [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts:28-37]()

### Task Queue Concurrency

The `KnowledgeTaskPresenter` enforces a maximum concurrency limit:

```mermaid
graph TB
    Queue["Task Queue<br/>queue: Task[]<br/>runningTasks: Map<br/>maxConcurrency: 16"]
    
    Check{"runningTasks.size<br/>< maxConcurrency?"}
    Shift["queue.shift()"]
    Execute["Execute task async"]
    Wait["Wait for completion"]
    
    Queue --> Check
    Check -->|Yes| Shift
    Shift --> Execute
    Execute --> Wait
    Wait --> Queue
    Check -->|No| Blocked["Block until task completes"]
```

This prevents resource exhaustion while maintaining high throughput. The default concurrency of 16 balances between parallel processing efficiency and system resource constraints.

**Sources:** [src/main/presenter/knowledgePresenter/knowledgeTaskPresenter.ts:141-170]()

---

## Task Lifecycle Management

### Task Cancellation

Tasks can be cancelled at different granularities:

| Method | Scope | Use Case |
|--------|-------|----------|
| `cancelTasksByKnowledgeBase(id)` | All tasks for a KB | KB disabled or deleted |
| `cancelTasksByFile(fileId)` | All tasks for a file | File deleted by user |
| `removeTasks(filter)` | Custom filter | Fine-grained control |

When cancelled, tasks receive an `AbortError` and execute their `onTerminate` callback.

**Sources:** [src/main/presenter/knowledgePresenter/knowledgeTaskPresenter.ts:29-57]()

### Task Pause and Resume

Tasks in `processing` state can be paused (e.g., on application quit):

```mermaid
sequenceDiagram
    participant User
    participant KSP as KnowledgeStorePresenter
    participant Queue as TaskPresenter
    participant DB as DuckDB
    
    User->>KSP: pauseAllRunningTasks()
    KSP->>Queue: cancelTasksByKnowledgeBase(kbId)
    Queue->>Queue: Abort all running tasks<br/>Clear queue
    KSP->>DB: UPDATE chunk SET status='paused'<br/>WHERE status='processing'
    KSP->>DB: UPDATE file SET status='paused'<br/>WHERE status='processing'
    
    Note over User,DB: Application restarts
    
    User->>KSP: resumeAllPausedTasks()
    KSP->>DB: SELECT * FROM chunk<br/>WHERE status='paused'
    DB-->>KSP: pausedChunks[]
    KSP->>KSP: Restore fileProgressMap
    KSP->>DB: UPDATE chunk/file<br/>SET status='processing'
    KSP->>Queue: Re-add each chunk task
```

This allows the pipeline to gracefully handle application shutdown and resume processing on restart without losing progress.

**Sources:** [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts:391-436](), [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts:622-650]()

---

## Integration with Vector Database

### Vector Insertion

After successful embedding generation, vectors are inserted into DuckDB:

```typescript
await this.vectorP.insertVector({
  vector: vectors[0],      // float[] of length dimensions
  fileId: chunkMsg.fileId,
  chunkId: chunkMsg.id
})
```

**Vector Table Schema:**

```sql
CREATE TABLE vector (
  id VARCHAR PRIMARY KEY,           -- nanoid
  embedding FLOAT[dimensions],      -- Fixed-dimension array
  file_id VARCHAR,                  -- Foreign key to file table
  chunk_id VARCHAR                  -- Foreign key to chunk table
)
```

Vectors are indexed using HNSW (Hierarchical Navigable Small World) for efficient similarity search.

**Sources:** [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts:214-220](), [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts:364-378]()

### Transaction Management

DuckDB operations use a transaction queue to ensure ACID properties:

```mermaid
graph TB
    Op["Database operation"]
    Queue["transactionQueue<br/>Array<{operation, resolve, reject}>"]
    Process["processTransactionQueue()"]
    Begin["BEGIN TRANSACTION"]
    Execute["Execute all queued operations"]
    Commit["COMMIT"]
    Rollback["ROLLBACK on error"]
    
    Op --> Queue
    Queue --> Process
    Process --> Begin
    Begin --> Execute
    Execute -->|Success| Commit
    Execute -->|Error| Rollback
```

All operations within a transaction batch succeed or fail together. If any operation fails, the entire transaction is rolled back, and all operations in the batch are rejected.

**Sources:** [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts:468-606]()

---

## Configuration Parameters

The pipeline behavior is controlled by per-knowledge-base configuration:

### Configuration Schema

```typescript
interface BuiltinKnowledgeConfig {
  id: string                    // Knowledge base ID
  enabled: boolean              // Enable/disable processing
  
  // Chunking parameters
  chunkSize: number             // Default: 1000 characters
  chunkOverlap: number          // Default: 200 characters
  separators: string[]          // Default: ['\n\n', '\n', ' ', '']
  
  // Embedding configuration
  embedding: {
    providerId: string          // LLM provider ID
    modelId: string             // Embedding model ID
  }
  
  // Vector database configuration
  dimensions: number            // Embedding dimensions (e.g., 1536 for OpenAI)
  normalized: boolean           // Whether embeddings are normalized
  fragmentsNumber: number       // Top-K results for queries (default: 5)
}
```

### Language-Specific Separators

The `RecursiveCharacterTextSplitter` supports language-specific separators via `getSeparatorsForLanguage()`. This optimizes chunking for different programming languages and natural languages.

**Supported Languages:**

The system supports language-specific splitting for code files (Python, JavaScript, Java, etc.) and natural languages. See `SupportedTextSplitterLanguages` for the complete list.

**Sources:** [src/main/presenter/knowledgePresenter/index.ts:371-385]()

---

## Summary

The file processing pipeline transforms raw files into searchable vector embeddings through a multi-stage process:

1. **Validation** ensures files are suitable for text-based RAG
2. **Synchronous processing** extracts content, chunks text, and creates database records
3. **Asynchronous processing** generates embeddings and inserts vectors with controlled concurrency
4. **Progress tracking** provides real-time feedback via EventBus
5. **Error handling** isolates failures at chunk-level while maintaining pipeline integrity
6. **Thread safety** is ensured through file-level queuing and transaction management

The pipeline is designed for reliability, observability, and graceful degradation, making it suitable for production knowledge base management.

**Sources:** [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts:1-463](), [src/main/presenter/knowledgePresenter/index.ts:1-462](), [src/main/presenter/knowledgePresenter/knowledgeTaskPresenter.ts:1-172]()
4b:T71c4,
