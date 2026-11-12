<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/xet-core · extra page Session Shard Interface · fetched 2026-10-26 -->

# Session Shard Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cas_client/src/interface.rs](cas_client/src/interface.rs)
- [cas_client/src/lib.rs](cas_client/src/lib.rs)
- [data/src/shard_interface.rs](data/src/shard_interface.rs)
- [hf_xet_wasm/src/wasm_file_upload_session.rs](hf_xet_wasm/src/wasm_file_upload_session.rs)

</details>



## Purpose and Scope

The `SessionShardInterface` manages the lifecycle of MDB shards during file upload sessions. It coordinates deduplication queries across multiple shard sources, stages XORB metadata for session resumability, and handles the finalization and upload of session shards to the CAS server.

This interface is the bridge between the upload workflow and the shard management system. For details on the underlying shard file format and operations, see [Shard Binary Format](#3.5.3). For the higher-level file upload orchestration that uses this interface, see [Upload Workflow](#5.1).

**Sources:** [data/src/shard_interface.rs:1-50]()

## Core Components

The `SessionShardInterface` struct maintains three distinct `ShardFileManager` instances and coordinates their interaction during an upload session.

```mermaid
graph TB
    SSI["SessionShardInterface"]
    
    subgraph "Shard Managers"
        Session["session_shard_manager<br/>ShardFileManager<br/>(current session)"]
        Cache["cache_shard_manager<br/>ShardFileManager<br/>(cached/uploaded)"]
        Resumed["resumed_session_shard_manager<br/>Option&lt;ShardFileManager&gt;<br/>(previous session)"]
    end
    
    subgraph "External Dependencies"
        Client["client: Arc&lt;dyn Client&gt;<br/>(CAS upload/query)"]
        Config["config: Arc&lt;TranslatorConfig&gt;<br/>(shard_config)"]
    end
    
    subgraph "Staging"
        MetadataStaging["xorb_metadata_staging<br/>Mutex&lt;SystemTime, MDBInMemoryShard&gt;<br/>(periodic flush)"]
        StagingDir["xorb_metadata_staging_dir<br/>PathBuf<br/>(resume directory)"]
    end
    
    subgraph "Temporary Storage"
        TempDir["_shard_session_dir<br/>TempDir<br/>(auto-cleanup)"]
    end
    
    SSI --> Session
    SSI --> Cache
    SSI --> Resumed
    SSI --> Client
    SSI --> Config
    SSI --> MetadataStaging
    SSI --> StagingDir
    SSI --> TempDir
```

**Sources:** [data/src/shard_interface.rs:26-50]()

### Key Fields

| Field | Type | Purpose |
|-------|------|---------|
| `session_shard_manager` | `Arc<ShardFileManager>` | Manages shards being built during current session |
| `cache_shard_manager` | `Arc<ShardFileManager>` | Manages cached shards from previous uploads |
| `resumed_session_shard_manager` | `Option<Arc<ShardFileManager>>` | Manages shards from resumed previous session |
| `client` | `Arc<dyn Client + Send + Sync>` | CAS client for uploads and global dedup queries |
| `xorb_metadata_staging_dir` | `PathBuf` | Directory for staging XORB metadata for resume |
| `xorb_metadata_staging` | `Mutex<(SystemTime, MDBInMemoryShard)>` | In-memory accumulator flushed periodically |
| `dry_run` | `bool` | If true, skip uploads and staging operations |

**Sources:** [data/src/shard_interface.rs:26-50]()

## Session Initialization and Resume

The `SessionShardInterface::new()` method sets up the session with support for resuming from previous interrupted uploads.

```mermaid
sequenceDiagram
    participant Caller
    participant New as "SessionShardInterface::new()"
    participant Merge as "merge_shards_background()"
    participant SessionMgr as "session_shard_manager"
    participant CacheMgr as "cache_shard_manager"
    participant ResumedMgr as "resumed_session_shard_manager"
    
    Caller->>New: new(config, client, dry_run)
    
    New->>New: Create TempDir in session_directory
    New->>New: Create xorb_metadata_staging_dir
    
    alt not dry_run
        New->>Merge: merge_shards_background(<br/>xorb_metadata_staging_dir,<br/>session_dir)
        Note over Merge: Background task merges<br/>shards from previous session
    end
    
    New->>CacheMgr: new_in_cache_directory()
    New->>SessionMgr: new_in_session_directory()
    
    New->>Merge: await merge result
    Merge-->>New: ShardMergeResult
    
    alt merged_shards not empty
        New->>ResumedMgr: new_in_session_directory()
        New->>ResumedMgr: register_shards(merged_shards)
        Note over ResumedMgr: Track XORBs already uploaded<br/>from previous session
    end
    
    New->>New: Track obsolete_shards<br/>for deletion on success
    
    New-->>Caller: SessionShardInterface
```

**Sources:** [data/src/shard_interface.rs:53-133]()

### Directory Structure

```mermaid
graph TB
    subgraph "Configuration Directories"
        SessionDir["shard_config.session_directory<br/>(persistent across sessions)"]
        CacheDir["shard_config.cache_directory<br/>(shared cache)"]
    end
    
    subgraph "Session-Specific"
        TempSession["TempDir in session_directory<br/>(auto-deleted)"]
        MetadataStaging["xorb_metadata_staging/<br/>(for resume)"]
    end
    
    subgraph "Shard Sources"
        SessionShards["Session shards<br/>(in TempDir)"]
        CachedShards["Cached shards<br/>(in cache_directory)"]
        ResumedShards["Resumed shards<br/>(merged from staging)"]
    end
    
    SessionDir --> TempSession
    SessionDir --> MetadataStaging
    CacheDir --> CachedShards
    
    TempSession --> SessionShards
    MetadataStaging --> ResumedShards
```

**Sources:** [data/src/shard_interface.rs:59-86]()

## Deduplication Query Hierarchy

The `chunk_hash_dedup_query()` method implements a three-tier query hierarchy to check if chunk sequences have already been uploaded.

```mermaid
graph TD
    Query["chunk_hash_dedup_query(query_hashes)"]
    
    Resumed["resumed_session_shard_manager?<br/>chunk_hash_dedup_query()"]
    Session["session_shard_manager<br/>chunk_hash_dedup_query()"]
    Cache["cache_shard_manager<br/>chunk_hash_dedup_query()"]
    
    ReturnResumed["Return (n_entries, fse, true)<br/>(already uploaded)"]
    ReturnSession["Return (n_entries, fse, false)<br/>(this session only)"]
    ReturnCache["Return (n_entries, fse, true)<br/>(from cache)"]
    ReturnNone["Return None"]
    
    Query --> Resumed
    Resumed -->|Found| ReturnResumed
    Resumed -->|Not found| Session
    
    Session -->|Found| ReturnSession
    Session -->|Not found| Cache
    
    Cache -->|Found| ReturnCache
    Cache -->|Not found| ReturnNone
    
    style ReturnResumed fill:#e8f5e9
    style ReturnSession fill:#fff3e0
    style ReturnCache fill:#e8f5e9
```

**Query Priority:**
1. **Resumed session shards** - XORBs from previous upload attempts (already on server)
2. **Current session shards** - XORBs created in this session (not yet uploaded)
3. **Cache shards** - XORBs from previous successful uploads (on server)

The boolean return value indicates whether the referenced XORB is already uploaded, which affects how the upload workflow tracks completion.

**Sources:** [data/src/shard_interface.rs:154-180]()

### Global Deduplication Query

For chunks not found locally, the system can query the remote CAS server for global deduplication.

```mermaid
sequenceDiagram
    participant Caller
    participant SSI as "SessionShardInterface"
    participant Client as "CAS Client"
    participant Cache as "cache_shard_manager"
    
    Caller->>SSI: query_dedup_shard_by_chunk(chunk_hash)
    SSI->>Client: query_for_global_dedup_shard(prefix, chunk_hash)
    
    alt Shard found on server
        Client-->>SSI: Some(shard_bytes)
        SSI->>Cache: import_shard_from_bytes(shard_bytes)
        Note over Cache: Shard now available<br/>for local queries
        SSI-->>Caller: Ok(true)
    else Not found or error
        Client-->>SSI: None or Error
        SSI-->>Caller: Ok(false)
    end
```

**Sources:** [data/src/shard_interface.rs:136-151]()

## XORB Metadata Management

The interface tracks XORB metadata through two mechanisms: immediate session tracking and staged metadata for resume.

### Adding XORB Blocks

```mermaid
graph LR
    subgraph "Immediate Tracking"
        AddXorb["add_xorb_block(xorb_info)"]
        SessionShard["session_shard_manager<br/>add_xorb_block()"]
    end
    
    subgraph "Upload Success Tracking"
        AddUploaded["add_uploaded_xorb_block(xorb_info)"]
        InMemory["xorb_metadata_staging<br/>MDBInMemoryShard"]
        CheckFlush{"Flush needed?<br/>(time or count)"}
        FlushToDisk["write_to_directory(<br/>xorb_metadata_staging_dir)"]
    end
    
    AddXorb --> SessionShard
    AddUploaded --> InMemory
    InMemory --> CheckFlush
    CheckFlush -->|Yes| FlushToDisk
    CheckFlush -->|No| InMemory
```

**Sources:** [data/src/shard_interface.rs:183-215]()

### Staging Flush Triggers

XORB metadata is flushed to the staging directory when either condition is met:

| Condition | Configuration | Purpose |
|-----------|---------------|---------|
| Time interval | `session_xorb_metadata_flush_interval` | Periodic persistence (default from config) |
| Entry count | `session_xorb_metadata_flush_max_count` | Limit memory usage (default from config) |

After flushing, the expiration time is set to `MDB_SHARD_LOCAL_CACHE_EXPIRATION` to allow cleanup of old resume files.

**Sources:** [data/src/shard_interface.rs:190-215]()

## File Reconstruction Tracking

File reconstruction information is added to the session shard manager as files complete processing.

```mermaid
graph LR
    AddFile["add_file_reconstruction_info(file_info)"]
    SessionMgr["session_shard_manager<br/>add_file_reconstruction_info()"]
    GetList["session_file_info_list()"]
    AllFiles["session_shard_manager<br/>all_file_info()"]
    
    AddFile --> SessionMgr
    GetList --> AllFiles
    
    note1["Must be called before<br/>upload_and_register_session_shards()"]
    GetList -.-> note1
```

The `MDBFileInfo` structures contain the reconstruction terms (XORB references and chunk ranges) needed to rebuild each file.

**Sources:** [data/src/shard_interface.rs:218-228]()

## Session Finalization and Upload

The `upload_and_register_session_shards()` method consolidates all session shards, uploads them to the CAS server, and moves them to the cache directory.

```mermaid
sequenceDiagram
    participant Caller
    participant SSI as "SessionShardInterface"
    participant SessionMgr as "session_shard_manager"
    participant Consolidate as "consolidate_shards_in_directory()"
    participant Upload as "Upload Tasks (JoinSet)"
    participant Client as "CAS Client"
    participant Cache as "cache_shard_manager"
    
    Caller->>SSI: upload_and_register_session_shards()
    
    SSI->>SessionMgr: flush()
    Note over SessionMgr: Write all in-memory<br/>shards to disk
    
    SSI->>Consolidate: consolidate_shards_in_directory(<br/>session_dir, max_target_size)
    Consolidate-->>SSI: Vec&lt;ShardInfo&gt;
    Note over Consolidate: Merge and optimize<br/>shard files
    
    loop For each shard
        SSI->>Client: acquire_upload_permit()
        Client-->>SSI: ConnectionPermit
        
        SSI->>Upload: spawn upload task
        
        par Upload Task
            Upload->>Upload: read_shard_to_bytes_remove_footer()
            Note over Upload: Strip footer/lookup tables<br/>Set footer_size=0
            
            alt not dry_run
                Upload->>Client: upload_shard(data, permit)
                Note over Client: POST to /shards endpoint
                
                Upload->>Upload: export_with_expiration(<br/>cache_directory)
                Upload->>Cache: register_shards([shard_path])
                Note over Cache: Move to cache,<br/>add expiration
            end
        end
    end
    
    SSI->>Upload: await all tasks
    
    SSI->>SSI: Remove obsolete staged shards
    Note over SSI: Clean up shards from<br/>previous resume attempts
    
    SSI-->>Caller: total_bytes_uploaded
```

**Sources:** [data/src/shard_interface.rs:232-311]()

### Shard Footer Removal

Before upload, the footer and lookup tables are stripped from shard files to reduce transfer size. The server reconstructs these sections from the shard content.

```mermaid
graph LR
    Full["Full Shard File<br/>(on disk)"]
    Read["read_shard_to_bytes_remove_footer()"]
    Split["Split at file_lookup_offset"]
    Header["Rewrite header<br/>footer_size = 0"]
    Upload["Upload truncated shard"]
    
    Full --> Read
    Read --> Split
    Split --> Header
    Header --> Upload
```

The `read_shard_to_bytes_remove_footer()` helper:
1. Reads up to `file_lookup_offset` (excludes footer and lookup tables)
2. Rewrites the header with `footer_size = 0`
3. Returns the truncated bytes for upload

**Sources:** [data/src/shard_interface.rs:314-332]()

## Parallel Upload Coordination

Shard uploads are executed in parallel with concurrency control via the CAS client's upload permits.

```mermaid
graph TB
    JoinSet["JoinSet&lt;Result&lt;()&gt;&gt;<br/>(parallel task pool)"]
    
    subgraph "Per-Shard Flow"
        Acquire["acquire_upload_permit()"]
        Spawn["Spawn task with permit"]
        Read["read_shard_to_bytes_remove_footer()"]
        Upload["upload_shard(data, permit)"]
        Export["export_with_expiration()"]
        Register["cache_shard_manager<br/>register_shards()"]
    end
    
    Complete["join_next().await<br/>(collect results)"]
    
    JoinSet --> Spawn
    Acquire --> Spawn
    Spawn --> Read
    Read --> Upload
    Upload --> Export
    Export --> Register
    Register --> Complete
    Complete --> JoinSet
```

The upload permit acquisition happens **before** spawning each task to prevent unbounded task creation and memory exhaustion.

**Sources:** [data/src/shard_interface.rs:246-301]()

## WASM Implementation Differences

The WASM implementation (`hf_xet_wasm/src/wasm_file_upload_session.rs`) uses a simplified approach without the full `SessionShardInterface`.

| Feature | Native (`SessionShardInterface`) | WASM (`FileUploadSession`) |
|---------|----------------------------------|----------------------------|
| Shard managers | Three separate managers | Single `MDBInMemoryShard` |
| Session resume | Supported via staging directory | Not supported |
| Cache shards | Separate cache directory | No cache |
| Dedup hierarchy | Three-tier query | Single in-memory shard |
| Footer removal | Strips footer before upload | Uploads without footer |

The WASM version maintains all metadata in a single `session_shard: Mutex<MDBInMemoryShard>` and uploads it directly without consolidation or caching.

**Sources:** [hf_xet_wasm/src/wasm_file_upload_session.rs:28-38](), [hf_xet_wasm/src/wasm_file_upload_session.rs:161-180]()

## Error Handling and Dry Run Mode

The `dry_run` flag allows testing the upload workflow without actual uploads or staging operations.

**Dry Run Behavior:**

| Operation | Normal Mode | Dry Run Mode |
|-----------|-------------|---------------|
| Session resume | Merge previous shards | Skip merge |
| XORB metadata staging | Write to disk periodically | Skip all writes |
| Shard upload | Upload to CAS server | Skip upload |
| Cache registration | Move shards to cache | Skip registration |
| Cleanup | Remove obsolete shards | Skip removal |

**Sources:** [data/src/shard_interface.rs:76-84](), [data/src/shard_interface.rs:191-194](), [data/src/shard_interface.rs:272-275]()

## Integration with Upload Workflow

The `SessionShardInterface` is created at the start of a `FileUploadSession` and used throughout the upload process.

```mermaid
graph TB
    FUS["FileUploadSession::new()"]
    SSI["SessionShardInterface::new()"]
    
    Process["Process files<br/>(SingleFileCleaner)"]
    
    subgraph "Per-XORB"
        AddXorb["add_xorb_block()"]
        Upload["Upload XORB"]
        AddUploaded["add_uploaded_xorb_block()"]
    end
    
    subgraph "Per-File"
        Dedup["chunk_hash_dedup_query()"]
        AddFile["add_file_reconstruction_info()"]
    end
    
    Finalize["upload_and_register_session_shards()"]
    
    FUS --> SSI
    SSI --> Process
    Process --> Dedup
    Process --> AddXorb
    AddXorb --> Upload
    Upload --> AddUploaded
    Process --> AddFile
    AddFile --> Finalize
```

**Sources:** [data/src/shard_interface.rs:26-50]()

---

