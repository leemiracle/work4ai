<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/xet-core · page 2 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [data/src/bin/example.rs](data/src/bin/example.rs)
- [data/src/data_client.rs](data/src/data_client.rs)
- [data/src/file_upload_session.rs](data/src/file_upload_session.rs)
- [data/src/lib.rs](data/src/lib.rs)
- [data/tests/test_clean_smudge.rs](data/tests/test_clean_smudge.rs)
- [mdb_shard/Cargo.toml](mdb_shard/Cargo.toml)
- [mdb_shard/src/file_structs.rs](mdb_shard/src/file_structs.rs)
- [mdb_shard/src/lib.rs](mdb_shard/src/lib.rs)
- [mdb_shard/src/set_operations.rs](mdb_shard/src/set_operations.rs)
- [mdb_shard/src/shard_format.rs](mdb_shard/src/shard_format.rs)
- [mdb_shard/src/shard_in_memory.rs](mdb_shard/src/shard_in_memory.rs)
- [mdb_shard/src/streaming_shard.rs](mdb_shard/src/streaming_shard.rs)
- [utils/src/async_read.rs](utils/src/async_read.rs)

</details>



This document describes the high-level architectural patterns and design principles of xet-core. It provides an overview of the major subsystems, their relationships, and the foundational design decisions that shape the codebase.

For details on the content-addressable storage format (XORBs, shards, chunks), see [Content-Addressable Storage Design](#2.1). For information about upload and download flows, see [Data Flow and Processing](#2.2). For the deduplication system, see [Deduplication Architecture](#2.3).

## Layered Architecture

xet-core follows a strict layered architecture where each layer has a well-defined responsibility and interacts only with adjacent layers.

```mermaid
graph TD
    subgraph "Layer 1: User Interfaces"
        PyAPI["Python API<br/>hf_xet module"]
        CLI["Command Line Tools<br/>xtool, git-xet"]
        WASM["WASM Bindings<br/>hf_xet_wasm"]
    end
    
    subgraph "Layer 2: Data Operations"
        DataClient["data_client module<br/>upload_async, download_async"]
        FUS["FileUploadSession"]
        FDS["FileDownloadSession"]
    end
    
    subgraph "Layer 3: CAS Client Abstraction"
        ClientTrait["Client trait"]
        RemoteClient["RemoteClient<br/>HTTP to CAS server"]
        LocalClient["LocalClient<br/>Filesystem simulation"]
        MemClient["MemoryClient<br/>In-memory testing"]
    end
    
    subgraph "Layer 4: Storage Abstraction"
        ShardMgr["ShardFileManager"]
        SessionInterface["SessionShardInterface"]
        ChunkCache["DiskCache"]
    end
    
    subgraph "Layer 5: Core Storage Primitives"
        XORBs["XORB Objects<br/>SerializedXorbObject"]
        Shards["MDB Shards<br/>MDBInMemoryShard, MDBShardFile"]
        Chunks["Content Chunks<br/>MerkleHash-addressed"]
    end
    
    subgraph "Infrastructure"
        Runtime["XetRuntime<br/>Tokio async executor"]
        Config["XetConfig<br/>Environment-based config"]
        Dedup["Deduplication<br/>Chunker, DataAggregator"]
    end
    
    PyAPI --> DataClient
    CLI --> DataClient
    WASM --> DataClient
    
    DataClient --> FUS
    DataClient --> FDS
    
    FUS --> ClientTrait
    FDS --> ClientTrait
    FUS --> SessionInterface
    
    ClientTrait --> RemoteClient
    ClientTrait --> LocalClient
    ClientTrait --> MemClient
    
    RemoteClient --> ChunkCache
    SessionInterface --> ShardMgr
    
    RemoteClient --> XORBs
    ShardMgr --> Shards
    ChunkCache --> Chunks
    
    DataClient --> Runtime
    FUS --> Dedup
    
    style ClientTrait fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Sources:** [data/src/data_client.rs:1-410](), [data/src/file_upload_session.rs:1-648](), [data/src/file_download_session.rs]()

### Layer Responsibilities

| Layer | Components | Responsibility |
|-------|------------|----------------|
| **User Interfaces** | Python API, CLI tools, WASM | Present user-facing APIs, handle authentication, convert to internal types |
| **Data Operations** | `FileUploadSession`, `FileDownloadSession`, `data_client` | Orchestrate multi-file operations, manage sessions, coordinate progress tracking |
| **CAS Client** | `RemoteClient`, `LocalClient`, `MemoryClient` | Abstract storage backend, handle HTTP/network operations, implement retry logic |
| **Storage Abstraction** | `ShardFileManager`, `SessionShardInterface`, `DiskCache` | Manage metadata and caching, provide query interfaces, coordinate shard lifecycle |
| **Storage Primitives** | XORB, MDB Shard, Chunk | Define on-disk formats, implement serialization, provide reconstruction data |

**Sources:** [data/src/lib.rs:1-25](), [mdb_shard/src/lib.rs:1-29]()

## Key Architectural Principles

### 1. Content-Addressable Everything

All data is identified by its content hash (`MerkleHash`). This applies at multiple levels:

```mermaid
graph LR
    File["File<br/>MerkleHash of chunk hashes"]
    Chunks["Chunks<br/>MerkleHash of content"]
    XORB["XORB<br/>MerkleHash of compressed data"]
    Shard["Shard<br/>MerkleHash of entire file"]
    
    File --> Chunks
    Chunks --> XORB
    File -.metadata.-> Shard
    XORB -.metadata.-> Shard
    
    style File fill:#f9f9f9
    style Chunks fill:#f9f9f9
    style XORB fill:#f9f9f9
    style Shard fill:#f9f9f9
```

- **Files** are identified by the aggregated hash of their constituent chunk hashes (computed via `merklehash::file_hash`)
- **Chunks** are identified by the hash of their decompressed content
- **XORBs** are identified by the hash of their compressed payload
- **Shards** are identified by the hash of the entire shard file

This enables:
- Automatic deduplication at the chunk level
- Verification of data integrity at every level
- Location-independent addressing

**Sources:** [data/src/data_client.rs:312-364](), [mdb_shard/src/file_structs.rs:1-634]()

### 2. Separation of Data and Metadata

The architecture strictly separates data storage from metadata storage:

```mermaid
graph TB
    subgraph "Data Path"
        Chunks["Content Chunks"]
        XORB["XORB Objects<br/>Compressed chunk collections"]
        CAS["CAS Server<br/>/v1/xorbs/:hash"]
        
        Chunks --> XORB
        XORB --> CAS
    end
    
    subgraph "Metadata Path"
        FileInfo["MDBFileInfo<br/>File reconstruction data"]
        XorbInfo["MDBXorbInfo<br/>Chunk composition"]
        Shard["MDB Shard<br/>Serialized metadata"]
        ShardCache["Shard Cache<br/>Local filesystem"]
        
        FileInfo --> Shard
        XorbInfo --> Shard
        Shard --> ShardCache
    end
    
    FileInfo -.references.-> XORB
    XorbInfo -.describes.-> XORB
    
    style XORB fill:#f9f9f9
    style Shard fill:#f9f9f9
```

- **Data objects (XORBs)** contain only compressed chunks
- **Metadata objects (Shards)** contain reconstruction information, lookup tables, and statistics
- This separation allows efficient queries without downloading data

**Sources:** [mdb_shard/src/shard_format.rs:1-800](), [mdb_shard/src/file_structs.rs:349-471]()

### 3. Asynchronous and Concurrent Design

All I/O operations use async/await with Tokio for efficient concurrency:

```mermaid
graph TB
    subgraph "XetRuntime"
        TokioRT["Tokio Runtime<br/>Multi-threaded executor"]
        FileSem["file_ingestion_semaphore<br/>Default: 8, HP: 100"]
        DownloadSem["file_download_semaphore<br/>Controls concurrent downloads"]
    end
    
    subgraph "Upload Concurrency"
        UploadSession["FileUploadSession"]
        CleanTasks["Parallel file cleaning tasks"]
        XorbUpload["Parallel XORB upload tasks<br/>JoinSet"]
        ACC["AdaptiveConcurrencyController<br/>Dynamic HTTP concurrency"]
        
        UploadSession --> CleanTasks
        CleanTasks --> FileSem
        UploadSession --> XorbUpload
        XorbUpload --> ACC
    end
    
    subgraph "Download Concurrency"
        DownloadSession["FileDownloadSession"]
        ReconMgr["ReconstructionTermManager<br/>Prefetch strategy"]
        BufferSem["Global buffer semaphore<br/>Memory control"]
        
        DownloadSession --> ReconMgr
        ReconMgr --> BufferSem
        DownloadSession --> DownloadSem
    end
    
    TokioRT --> UploadSession
    TokioRT --> DownloadSession
    
    style ACC fill:#f9f9f9
```

Key concurrency mechanisms:
- **Semaphores** limit resource usage (`file_ingestion_semaphore`, buffer limits)
- **AdaptiveConcurrencyController** adjusts HTTP parallelism based on RTT and success rates
- **JoinSet** manages parallel upload tasks
- **Spawn blocking** offloads CPU-intensive work (compression, hashing)

**Sources:** [data/src/file_upload_session.rs:165-235](), [xet_runtime/src/lib.rs](), [cas_client/src/adaptive_concurrency.rs]()

### 4. Pluggable Storage Backends

The `Client` trait abstracts the storage backend, enabling multiple implementations:

```mermaid
graph TD
    ClientTrait["trait Client<br/>upload_xorb, download_xorb, query_shards"]
    
    RemoteClient["RemoteClient<br/>HTTP/HTTPS to CAS server"]
    LocalClient["LocalClient<br/>Filesystem simulation"]
    MemClient["MemoryClient<br/>In-memory HashMap"]
    
    ClientTrait --> RemoteClient
    ClientTrait --> LocalClient
    ClientTrait --> MemClient
    
    RemoteClient --> HTTPClient["reqwest::Client<br/>Retry middleware"]
    RemoteClient --> AuthRefresh["Token refresh callbacks"]
    
    LocalClient --> FSManager["ShardFileManager<br/>Local directory"]
    
    MemClient --> InMemory["HashMap storage<br/>Testing only"]
    
    style ClientTrait fill:#f9f9f9,stroke:#333,stroke-width:2px
```

The abstraction enables:
- **Production**: `RemoteClient` with HTTP retry and authentication
- **Local testing**: `LocalClient` using filesystem paths prefixed with `local://`
- **Unit tests**: `MemoryClient` for fast in-memory operations

**Sources:** [cas_client/src/interface.rs](), [cas_client/src/remote_client.rs](), [cas_client/src/local_client.rs]()

## Component Interaction Patterns

### Upload Session Lifecycle

```mermaid
sequenceDiagram
    participant User
    participant DataClient as "data_client::upload_async"
    participant FUS as "FileUploadSession"
    participant Cleaner as "SingleFileCleaner"
    participant Agg as "DataAggregator"
    participant Interface as "SessionShardInterface"
    participant Client as "Client trait impl"
    
    User->>DataClient: upload_async(paths)
    DataClient->>FUS: new(config)
    
    loop For each file
        DataClient->>Cleaner: start_clean()
        Cleaner->>Agg: Add chunks to aggregator
        
        alt Aggregator exceeds MAX_XORB_BYTES
            Agg->>FUS: Cut XORB
            FUS->>Interface: add_xorb_block(metadata)
            FUS->>Client: upload_xorb(data)
        end
        
        Cleaner->>FUS: register_completion()
    end
    
    FUS->>FUS: finalize()
    FUS->>Interface: upload_and_register_session_shards()
    Interface->>Client: upload_shard(shard_data)
    FUS->>DataClient: DeduplicationMetrics
    DataClient->>User: Vec<XetFileInfo>
```

**Sources:** [data/src/data_client.rs:140-197](), [data/src/file_upload_session.rs:143-245](), [data/src/file_upload_session.rs:450-505]()

### Download Session Lifecycle

```mermaid
sequenceDiagram
    participant User
    participant DataClient as "data_client::download_async"
    participant FDS as "FileDownloadSession"
    participant ShardMgr as "ShardFileManager"
    participant Client as "Client trait impl"
    participant Reconstructor as "FileReconstructor"
    participant Writer as "SequentialWriter"
    
    User->>DataClient: download_async(file_infos)
    DataClient->>FDS: new(config)
    
    loop For each file
        FDS->>ShardMgr: query_file_reconstruction_info(hash)
        ShardMgr->>Client: query_shards(file_hash)
        Client->>ShardMgr: MDBFileInfo
        
        FDS->>Reconstructor: new(file_info)
        Reconstructor->>Client: Fetch XORBs with prefetching
        Reconstructor->>Writer: write_chunk_in_order()
        Writer->>FDS: Completed file
    end
    
    FDS->>DataClient: Success
    DataClient->>User: Vec<String> (paths)
```

**Sources:** [data/src/data_client.rs:199-257](), [file_reconstruction/src/lib.rs]()

## Configuration and Runtime Management

Configuration follows a hierarchical model with environment variable overrides:

```mermaid
graph TB
    subgraph "Configuration Hierarchy"
        Env["Environment Variables<br/>HF_XET_*, HF_HOME"]
        HP["HF_XET_HIGH_PERFORMANCE<br/>Multiplies limits"]
        
        Env --> XetConfig["XetConfig<br/>Global singleton"]
        HP --> XetConfig
        
        XetConfig --> DataConfig["data:<br/>max_concurrent_file_ingestion<br/>ingestion_block_size"]
        XetConfig --> ClientConfig["client:<br/>ac_max_upload_concurrency<br/>retry_config"]
        XetConfig --> ReconConfig["reconstruction:<br/>download_buffer_limit<br/>prefetch_window"]
        XetConfig --> ShardConfig["mdb_shard:<br/>cache_directory<br/>session_directory"]
        XetConfig --> DedupConfig["deduplication:<br/>target_chunk_size<br/>max_xorb_bytes"]
        XetConfig --> CacheConfig["chunk_cache:<br/>cache_size<br/>eviction_policy"]
    end
    
    subgraph "Runtime Execution"
        DataConfig --> Runtime["XetRuntime<br/>Tokio-based executor"]
        ClientConfig --> Runtime
        
        Runtime --> ThreadPool["Thread Pool<br/>async + blocking"]
        Runtime --> Semaphores["Semaphores<br/>file_ingestion, file_download"]
        Runtime --> SIGINT["SIGINT Handler<br/>Graceful shutdown"]
    end
    
    style XetConfig fill:#f9f9f9,stroke:#333,stroke-width:2px
    style Runtime fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**High-Performance Mode** multiplies concurrency limits:
- File ingestion: 8 → 100
- Upload concurrency: 32 → 124
- Download buffer: 4GB → 64GB

**Sources:** [xet_runtime/src/config.rs](), [xet_runtime/src/runtime.rs](), [data/src/configurations.rs]()

## Error Handling and Resilience

The architecture implements multiple layers of error handling:

| Layer | Mechanism | Implementation |
|-------|-----------|----------------|
| **HTTP** | Exponential backoff retry | `RetryClientMiddleware` in `cas_client` |
| **Network** | Adaptive concurrency | `AdaptiveConcurrencyController` adjusts based on failures |
| **Data** | Content verification | All objects verified against `MerkleHash` |
| **Session** | Transactional upload | XORBs uploaded before shards; atomic shard registration |
| **Cache** | LRU eviction | `DiskCache` with configurable size limits |
| **Runtime** | SIGINT handling | Graceful task cancellation via `check_sigint_shutdown()` |

**Sources:** [cas_client/src/retry_client.rs](), [cas_client/src/adaptive_concurrency.rs](), [chunk_cache/src/lib.rs]()

## Storage Format Versioning

Shards include versioned headers and footers to support backward compatibility:

```rust
// From shard_format.rs
const MDB_SHARD_HEADER_VERSION: u64 = 2;
const MDB_SHARD_FOOTER_VERSION: u64 = 1;
const MDB_SHARD_HEADER_TAG: [u8; 32] = [
    b'H', b'F', b'R', b'e', b'p', b'o', ...
];
```

- **Header** contains magic number and version
- **Footer** contains offsets and metadata
- Version checks prevent incompatible format usage

**Sources:** [mdb_shard/src/shard_format.rs:36-100]()

## Memory Management

Memory usage is controlled through several mechanisms:

```mermaid
graph TD
    subgraph "Upload Memory Control"
        Ingestion["Ingestion semaphore<br/>Limits concurrent files"]
        BlockSize["ingestion_block_size<br/>Per-file buffer size"]
        Aggregator["DataAggregator<br/>MAX_XORB_BYTES cutoff"]
    end
    
    subgraph "Download Memory Control"
        GlobalBuf["Global buffer semaphore<br/>Scales with active downloads"]
        PerFile["Per-file buffer permits<br/>Backpressure control"]
        Prefetch["Prefetch window<br/>Limits outstanding requests"]
    end
    
    subgraph "Cache Memory Control"
        DiskCache["DiskCache<br/>LRU eviction"]
        CacheSize["cache_size config<br/>Maximum cache bytes"]
    end
    
    style GlobalBuf fill:#f9f9f9
```

- **Upload**: Limited by file concurrency × block size × 2 (double buffering)
- **Download**: Dynamically scaled buffer semaphore prevents runaway memory
- **Cache**: LRU eviction maintains configured size limit

**Sources:** [data/src/file_upload_session.rs:194-216](), [file_reconstruction/src/buffer_manager.rs](), [chunk_cache/src/disk_cache.rs]()

---

