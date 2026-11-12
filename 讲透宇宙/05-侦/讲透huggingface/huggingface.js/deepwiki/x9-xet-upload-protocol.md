<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/huggingface.js · extra page Xet Upload Protocol · fetched 2026-10-26 -->

# Xet Upload Protocol

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/hub/.gitignore](packages/hub/.gitignore)
- [packages/hub/scripts/bench.ts](packages/hub/scripts/bench.ts)
- [packages/hub/scripts/debug-xet.ts](packages/hub/scripts/debug-xet.ts)
- [packages/hub/src/lib/commit.ts](packages/hub/src/lib/commit.ts)
- [packages/hub/src/lib/upload-files-with-progress.spec.ts](packages/hub/src/lib/upload-files-with-progress.spec.ts)
- [packages/hub/src/utils/ChunkCache.spec.ts](packages/hub/src/utils/ChunkCache.spec.ts)
- [packages/hub/src/utils/ChunkCache.ts](packages/hub/src/utils/ChunkCache.ts)
- [packages/hub/src/utils/createXorb.spec.ts](packages/hub/src/utils/createXorb.spec.ts)
- [packages/hub/src/utils/createXorbs.ts](packages/hub/src/utils/createXorbs.ts)
- [packages/hub/src/utils/uploadShards.ts](packages/hub/src/utils/uploadShards.ts)
- [packages/hub/src/utils/xetWriteToken.ts](packages/hub/src/utils/xetWriteToken.ts)

</details>



## Purpose and Scope

This document describes the Xet upload protocol, an advanced file upload system used by the `@huggingface/hub` package for efficient large file handling. The Xet protocol uses content-defined chunking, compression, and deduplication to minimize bandwidth usage when uploading files to the Hugging Face Hub.

For general file operations including basic uploads, see [Repository and File Operations](#2.2.1). For authentication details, see [Authentication and Caching](#2.2.3).

The Xet protocol is automatically used for large files (LFS files) when `useXet: true` is set in commit operations. The protocol achieves significant bandwidth savings through:
- Content-defined chunking that enables deduplication across file versions
- LZ4 compression with byte-grouping optimization
- Local and remote chunk deduplication
- Efficient binary file format (xorbs and shards)

Sources: [packages/hub/src/lib/commit.ts:128-129](), [packages/hub/src/utils/createXorbs.ts:1-759](), [packages/hub/src/utils/uploadShards.ts:1-415]()

## Architecture Overview

The Xet protocol operates in three main phases: chunking, xorb creation, and shard packaging. Files are broken into content-defined chunks, chunks are compressed and assembled into xorbs, and xorbs are packaged with metadata into shards for upload.

**Xet Protocol Architecture**

```mermaid
graph TB
    subgraph Input["Input Phase"]
        FILE["File Blob"]
    end
    
    subgraph Chunking["Content-Defined Chunking"]
        CHUNKER["Chunker (WASM)<br/>TARGET_CHUNK_SIZE=64KB"]
        CHUNKS["Chunks<br/>(variable size)"]
    end
    
    subgraph Compression["Compression Phase"]
        LZ4["LZ4 Compression"]
        BG4["ByteGrouping LZ4<br/>(bg4_split_bytes)"]
        BEST["Select Best"]
    end
    
    subgraph Dedup["Deduplication Check"]
        LOCALCACHE["ChunkCache<br/>(local dedup)"]
        REMOTECAS["CAS Backend<br/>(remote dedup)"]
    end
    
    subgraph XorbCreation["Xorb Assembly"]
        XORBDATA["CurrentXorbInfo<br/>XORB_SIZE=64MB<br/>MAX_XORB_CHUNKS=8K"]
        XORBBIN["Xorb Binary<br/>(8-byte headers + compressed chunks)"]
    end
    
    subgraph ShardCreation["Shard Packaging"]
        FILEINFO["File Info Section<br/>(file metadata + representation)"]
        XORBINFO["Xorb Info Section<br/>(xorb metadata + chunk hashes)"]
        SHARDFOOTER["Shard Footer<br/>(offsets + HMAC key)"]
        SHARDBIN["Shard Binary"]
    end
    
    subgraph Upload["Upload Phase"]
        UPLOADXORB["POST /v1/xorbs/default/{hash}"]
        UPLOADSHARD["POST /v1/shards"]
    end
    
    FILE --> CHUNKER
    CHUNKER --> CHUNKS
    CHUNKS --> LZ4
    CHUNKS --> BG4
    LZ4 --> BEST
    BG4 --> BEST
    
    BEST --> LOCALCACHE
    LOCALCACHE -->|"miss"| REMOTECAS
    LOCALCACHE -->|"hit (deduplicated)"| Dedup
    REMOTECAS -->|"hit (deduplicated)"| Dedup
    REMOTECAS -->|"miss"| XORBDATA
    
    XORBDATA -->|"full or max chunks"| XORBBIN
    XORBBIN --> UPLOADXORB
    
    XORBBIN --> XORBINFO
    FILE --> FILEINFO
    FILEINFO --> SHARDBIN
    XORBINFO --> SHARDBIN
    SHARDFOOTER --> SHARDBIN
    SHARDBIN --> UPLOADSHARD
```

Sources: [packages/hub/src/utils/createXorbs.ts:9-22](), [packages/hub/src/utils/uploadShards.ts:7-14]()

## Key Data Structures

The Xet protocol uses three primary binary structures:

| Structure | Size Limit | Purpose | Key Fields |
|-----------|-----------|---------|-----------|
| **Chunk** | ~64KB (variable) | Smallest unit of content | hash (32 bytes), length, compression type |
| **Xorb** | 64MB max, 8K chunks max | Container for compressed chunks | hash, chunk metadata, binary data |
| **Shard** | Variable | Metadata package linking files to xorbs | file info, xorb info, HMAC key, footer |

Sources: [packages/hub/src/utils/createXorbs.ts:9-14](), [packages/hub/src/utils/uploadShards.ts:7-14]()

## Content-Defined Chunking

Files are split into variable-size chunks using a content-defined chunking algorithm (implemented in WebAssembly). This approach ensures that identical content produces identical chunks, even if the content appears at different offsets in different files.

**Chunking Process**

```mermaid
graph LR
    subgraph InputFile["File Stream"]
        STREAM["ReadableStream<br/>Uint8Array chunks"]
    end
    
    subgraph ChunkerWASM["chunker_wasm Module"]
        CHUNKER["Chunker<br/>new Chunker(TARGET_CHUNK_SIZE)"]
        ADDDATA["add_data(data)<br/>yields boundary chunks"]
        FINISH["finish()<br/>yields final chunk"]
    end
    
    subgraph ChunkOutput["Chunk Output"]
        CHUNKDATA["{ hash: string<br/>length: number<br/>dedup: boolean }"]
    end
    
    STREAM --> ADDDATA
    ADDDATA --> CHUNKER
    CHUNKER --> CHUNKDATA
    FINISH --> CHUNKDATA
```

The chunker operates on a stream of data and yields chunks when content boundaries are detected. The target chunk size is 64KB, but actual sizes vary based on content patterns.

**Chunk Characteristics:**
- **Target size**: 64KB (configurable via `TARGET_CHUNK_SIZE`)
- **Max size**: 128KB (2 × target, defined as `MAX_CHUNK_SIZE`)
- **Variable boundaries**: Determined by content, not fixed offsets
- **Hash**: Each chunk is identified by its content hash
- **Dedup flag**: Indicates whether to check remote deduplication

Sources: [packages/hub/src/utils/createXorbs.ts:9-11](), [packages/hub/src/utils/createXorbs.ts:166-340]()

## Xorb Structure and Creation

Xorbs (eXtended Object Repository Blocks) are containers that hold compressed chunks. Each xorb is a binary structure with chunk headers and data.

**Xorb Binary Layout**

```mermaid
graph TB
    subgraph XorbBinary["Xorb Binary Structure"]
        CHUNK1["Chunk 1 Header (8 bytes)<br/>- byte 0: reserved<br/>- bytes 1-3: packed length (24-bit)<br/>- byte 4: compression scheme<br/>- bytes 5-7: unpacked length (24-bit)"]
        DATA1["Chunk 1 Data<br/>(compressed or raw)"]
        CHUNK2["Chunk 2 Header (8 bytes)"]
        DATA2["Chunk 2 Data"]
        DOTS["..."]
        CHUNKN["Chunk N Header"]
        DATAN["Chunk N Data"]
    end
    
    CHUNK1 --> DATA1
    DATA1 --> CHUNK2
    CHUNK2 --> DATA2
    DATA2 --> DOTS
    DOTS --> CHUNKN
    CHUNKN --> DATAN
```

**Xorb Constraints:**
- **Maximum size**: 64MB (`XORB_SIZE`)
- **Maximum chunks**: 8,192 (`MAX_XORB_CHUNKS`)
- **Chunk header**: 8 bytes (`XET_CHUNK_HEADER_BYTES`)

When either limit is reached, the current xorb is finalized and a new one begins.

**Compression Strategy**

The `writeChunk` function implements a two-pass compression approach:

```mermaid
graph TB
    subgraph CompressionSelection["Compression Selection Algorithm"]
        CHUNK["Chunk Data<br/>(uncompressed)"]
        REGULAR["lz4_compress(chunk)"]
        BYTEG["lz4_compress(<br/>bg4_split_bytes(chunk))"]
        
        COMPARE["Compare Sizes"]
        
        SELECTCOMP["Use smaller:<br/>bgCompressed or regularCompressed"]
        SELECTRAW["Use raw if smaller than compressed"]
        
        FINAL["Final Chunk<br/>+ compression type flag"]
    end
    
    CHUNK --> REGULAR
    CHUNK --> BYTEG
    REGULAR --> COMPARE
    BYTEG --> COMPARE
    COMPARE --> SELECTCOMP
    SELECTCOMP --> SELECTRAW
    SELECTRAW --> FINAL
```

**Compression Types:**
- `XetChunkCompressionScheme.None` (0): No compression
- `XetChunkCompressionScheme.LZ4`: Standard LZ4 compression
- `XetChunkCompressionScheme.ByteGroupingLZ4`: LZ4 with byte grouping optimization

The byte grouping optimization (`bg4_split_bytes`) is particularly effective for data with interleaved patterns (e.g., multi-channel image data).

Sources: [packages/hub/src/utils/createXorbs.ts:524-559](), [packages/hub/src/utils/XetBlob.ts]() (referenced)

## Shard Structure and Assembly

Shards are metadata packages that connect files to their xorb representations. Each shard contains file metadata, xorb metadata, and a footer with critical information for reconstruction.

**Shard Binary Layout**

```mermaid
graph TB
    subgraph ShardStructure["Shard Binary Structure"]
        HEADER["Shard Header (48 bytes)<br/>- Magic tag (32 bytes): 'HFRepoMetaData...'<br/>- Version (8 bytes): SHARD_HEADER_VERSION=2<br/>- Footer size (8 bytes)"]
        
        FILEINFO["File Info Section (variable)<br/>For each file:<br/>- File hash (32 bytes)<br/>- Flags (4 bytes)<br/>- Representation length (4 bytes)<br/>- Reserved (8 bytes)<br/>- Representation items<br/>- Verification hashes<br/>- SHA256 (32 bytes)"]
        
        FILEBOOKEND["File Bookend (48 bytes)<br/>- 0xFF × 32<br/>- 0x00 × 16"]
        
        XORBINFO["Xorb Info Section (variable)<br/>For each xorb:<br/>- Xorb hash (32 bytes)<br/>- Flags (4 bytes)<br/>- Chunk count (4 bytes)<br/>- Unpacked size (4 bytes)<br/>- Packed size (4 bytes)<br/>For each chunk:<br/>- Chunk hash (32 bytes)<br/>- Start offset (4 bytes)<br/>- Length (4 bytes)<br/>- Reserved (8 bytes)"]
        
        XORBBOOKEND["Xorb Bookend (48 bytes)<br/>- 0xFF × 32<br/>- 0x00 × 16"]
        
        FOOTER["Shard Footer (200 bytes)<br/>- Version (8 bytes): SHARD_FOOTER_VERSION=1<br/>- File info offset (8 bytes)<br/>- CAS info offset (8 bytes)<br/>- Reserved (48 bytes)<br/>- HMAC key (32 bytes)<br/>- Creation timestamp (8 bytes)<br/>- Key expiry (8 bytes)<br/>- Reserved (48 bytes)<br/>- Stored bytes (8 bytes)<br/>- Materialized bytes (8 bytes)<br/>- Unpacked bytes (8 bytes)<br/>- Footer offset (8 bytes)"]
    end
    
    HEADER --> FILEINFO
    FILEINFO --> FILEBOOKEND
    FILEBOOKEND --> XORBINFO
    XORBINFO --> XORBBOOKEND
    XORBBOOKEND --> FOOTER
```

**File Representation Format**

Each file in the shard is described by a representation that maps byte ranges to xorb chunks:

```mermaid
graph LR
    subgraph FileRep["File Representation"]
        ITEM1["Rep Item 1<br/>- Xorb hash<br/>- Index start/end<br/>- Length<br/>- Range hash"]
        ITEM2["Rep Item 2"]
        ITEM3["Rep Item 3"]
    end
    
    subgraph FileBytes["File Content"]
        RANGE1["Bytes 0-65535<br/>(from Xorb A, chunks 0-1)"]
        RANGE2["Bytes 65536-131071<br/>(from Xorb A, chunks 2-3)"]
        RANGE3["Bytes 131072-196607<br/>(from Xorb B, chunks 0-1)"]
    end
    
    ITEM1 -.describes.-> RANGE1
    ITEM2 -.describes.-> RANGE2
    ITEM3 -.describes.-> RANGE3
```

Each representation item specifies:
- **xorbId**: Which xorb contains the chunks (converted to hash in final shard)
- **indexStart/indexEnd**: Chunk index range within the xorb
- **length**: Total unpacked byte length of this range
- **rangeHash**: Verification hash computed from chunk hashes

Sources: [packages/hub/src/utils/uploadShards.ts:19-52](), [packages/hub/src/utils/uploadShards.ts:231-343](), [packages/hub/src/utils/createXorbs.ts:562-633]()

## Deduplication Strategy

The Xet protocol implements a two-tier deduplication system to minimize uploads: local cache deduplication and remote CAS deduplication.

**Deduplication Flow**

```mermaid
graph TB
    subgraph Process["Deduplication Process"]
        NEWCHUNK["New Chunk Generated<br/>(hash + content)"]
        
        LOCALCHECK["Check ChunkCache.getChunk(hash)"]
        
        LOCALHIT["Local Cache Hit<br/>- Reuse xorbIndex/chunkIndex<br/>- Mark as deduplicated"]
        
        REMOTECOND["Remote Check Conditions:<br/>1. chunk.dedup = true<br/>2. bytesSinceRemoteDedup >= 4MB"]
        
        REMOTECHECK["Fetch CAS:<br/>GET /v1/chunks/default/{hash}"]
        
        REMOTEHIT["Remote Hit:<br/>- Parse shard data<br/>- Add chunks to cache<br/>- Backtrack previous chunks"]
        
        REMOTEMISS["Remote Miss"]
        
        WRITEXORB["Write to Current Xorb<br/>- Compress chunk<br/>- Add to CurrentXorbInfo.data<br/>- Add to ChunkCache"]
    end
    
    NEWCHUNK --> LOCALCHECK
    LOCALCHECK -->|hit| LOCALHIT
    LOCALCHECK -->|miss| REMOTECOND
    REMOTECOND -->|"conditions met"| REMOTECHECK
    REMOTECOND -->|"not met"| WRITEXORB
    REMOTECHECK -->|"200 OK"| REMOTEHIT
    REMOTECHECK -->|"404"| REMOTEMISS
    REMOTEMISS --> WRITEXORB
    REMOTEHIT --> LOCALHIT
```

**ChunkCache Implementation**

The `ChunkCache` class maintains a circular buffer for efficient local deduplication:

| Component | Type | Purpose |
|-----------|------|---------|
| `map` | `Map<string, number>` | Maps chunk hash to cache index |
| `xorbIndices` | `Int32Array` | Stores xorb index for each cached chunk |
| `chunkIndices` | `Uint16Array` | Stores chunk index within xorb |
| `hmacs` | `Set<string>` | HMAC keys for remote chunk lookups |

**Cache Behavior:**
- **Initial size**: 10,000 entries
- **Growth factor**: 1.5×
- **Maximum size**: 1,000,000 entries (default)
- **Eviction**: FIFO (First In, First Out) when full
- **Negative indices**: Indicate remote xorbs (e.g., -1 = first remote xorb)

**Remote Deduplication Details:**

When a remote dedup check succeeds:
1. The CAS returns a shard containing matching chunk information
2. All chunks in the shard are added to the local cache with negative xorb IDs
3. The `backtrackDedup` function reviews recently added chunks in the current xorb
4. Chunks that match remote chunks are removed from the current xorb
5. File representations are updated to reference remote chunks

The backtracking optimization can significantly reduce xorb size by retroactively applying remote deduplication.

Sources: [packages/hub/src/utils/createXorbs.ts:216-257](), [packages/hub/src/utils/ChunkCache.ts:1-100](), [packages/hub/src/utils/createXorbs.ts:380-486]()

## Upload Flow

The complete Xet upload flow spans three main functions: `commitIter`, `createXorbs`, and `uploadShards`.

**Complete Upload Pipeline**

```mermaid
graph TB
    subgraph CommitPhase["commit.ts: commitIter"]
        OPERATIONS["CommitOperation[]"]
        PREUPLOAD["POST /api/.../preupload<br/>(determine LFS files)"]
        LFSBATCH["POST /.../info/lfs/objects/batch<br/>(get Xet session tokens)"]
        XETPARAMS["XetTokenParams<br/>- sessionId<br/>- casUrl<br/>- accessToken"]
    end
    
    subgraph CreatePhase["createXorbs.ts: createXorbs"]
        FILESOURCE["AsyncGenerator<br/>{ content, path, sha256 }"]
        CHUNKER2["Content-Defined Chunking"]
        COMPRESS2["Compression"]
        DEDUP2["Deduplication"]
        XORBEVENT["XorbEvent<br/>{ xorb, hash, chunks }"]
        FILEEVENT["FileEvent<br/>{ hash, sha256, representation }"]
    end
    
    subgraph UploadPhase["uploadShards.ts: uploadShards"]
        XORBUP["uploadXorb<br/>POST /v1/xorbs/default/{hash}"]
        BUILDINFO["Build File/Xorb Info Sections"]
        SHARDBUILD["createShard()<br/>Assemble binary structure"]
        SHARDUP["uploadShard<br/>POST /v1/shards"]
    end
    
    subgraph FinalizePhase["commit.ts: commitIter"]
        COMMITAPI["POST /api/.../commit<br/>(finalize with LFS metadata)"]
    end
    
    OPERATIONS --> PREUPLOAD
    PREUPLOAD --> LFSBATCH
    LFSBATCH --> XETPARAMS
    XETPARAMS --> FILESOURCE
    
    FILESOURCE --> CHUNKER2
    CHUNKER2 --> COMPRESS2
    COMPRESS2 --> DEDUP2
    DEDUP2 --> XORBEVENT
    DEDUP2 --> FILEEVENT
    
    XORBEVENT --> XORBUP
    XORBEVENT --> BUILDINFO
    FILEEVENT --> BUILDINFO
    BUILDINFO --> SHARDBUILD
    SHARDBUILD --> SHARDUP
    
    SHARDUP --> COMMITAPI
```

**Key Functions and Their Roles:**

| Function | File | Purpose | Key Operations |
|----------|------|---------|----------------|
| `commitIter` | commit.ts | Main entry point | Preupload check, LFS batch request, call uploadShards |
| `createXorbs` | createXorbs.ts | Chunking and xorb assembly | Content chunking, compression, deduplication, xorb creation |
| `uploadShards` | uploadShards.ts | Shard packaging and upload | Assemble file/xorb info, create shards, upload xorbs and shards |
| `xetWriteToken` | xetWriteToken.ts | Token management | Fetch and cache write tokens for CAS uploads |

**Progress Events:**

The upload flow yields progress events at multiple stages:

```mermaid
graph LR
    subgraph ProgressEvents["Progress Event Types"]
        PHASE["phase event<br/>- preuploading<br/>- uploadingLargeFiles<br/>- committing"]
        
        FILEPROG["fileProgress event<br/>- path<br/>- progress (0-1)<br/>- state (hashing/uploading)"]
    end
    
    subgraph Processing["Progress Calculation"]
        LOCAL["Local Processing:<br/>10% of total"]
        UPLOAD["Upload:<br/>90% of total"]
    end
    
    FILEPROG --> LOCAL
    FILEPROG --> UPLOAD
```

Progress is split between local processing (chunking, compression, deduplication) and network upload. The `PROCESSING_PROGRESS_RATIO` constant (0.1) controls this split, allocating 10% to processing and 90% to upload.

Sources: [packages/hub/src/lib/commit.ts:169-713](), [packages/hub/src/utils/createXorbs.ts:85-378](), [packages/hub/src/utils/uploadShards.ts:76-349]()

## Token Management

Xet uploads require authentication via write tokens obtained from the Hub backend. The `xetWriteToken` function manages token lifecycle.

**Token Flow**

```mermaid
graph TB
    subgraph TokenMgmt["xetWriteToken Function"]
        CHECKLOCAL["Check local params:<br/>xetParams.expiresAt<br/>xetParams.accessToken<br/>xetParams.casUrl"]
        
        CHECKCACHE["Check JWT cache:<br/>jwts.get(refreshWriteTokenUrl)"]
        
        FETCH["POST refreshWriteTokenUrl<br/>Headers:<br/>- Authorization: Bearer {token}<br/>- X-Xet-Session-Id: {sessionId}"]
        
        RESPONSE["Response:<br/>{ accessToken, casUrl, exp }"]
        
        CACHE["Cache token:<br/>jwts.set(key, jwt)<br/>Evict old tokens"]
        
        RETURN["Return:<br/>{ accessToken, casUrl }"]
    end
    
    CHECKLOCAL -->|"valid and not expiring soon"| RETURN
    CHECKLOCAL -->|"invalid or expiring"| CHECKCACHE
    CHECKCACHE -->|"hit and valid"| RETURN
    CHECKCACHE -->|"miss or expiring"| FETCH
    FETCH --> RESPONSE
    RESPONSE --> CACHE
    CACHE --> RETURN
```

**Token Caching Strategy:**
- **Safety period**: 60 seconds (`JWT_SAFETY_PERIOD`) - tokens expiring within this window are refreshed
- **Cache size**: 1,000 entries (`JWT_CACHE_SIZE`)
- **Deduplication**: Concurrent requests for the same token share a promise
- **Eviction**: Expired tokens are pruned, oldest tokens removed when cache is full

Sources: [packages/hub/src/utils/xetWriteToken.ts:1-99]()

## Key Classes and Functions

### Core Classes

**CurrentXorbInfo**

Manages state for the xorb being assembled:

```typescript
class CurrentXorbInfo {
    id: number;                              // Xorb identifier
    offset: number;                          // Current write position in data buffer
    chunks: Array<{                          // Chunks in this xorb
        hash: string;
        length: number;
        offset: number;
    }>;
    fileProcessedBytes: Record<string, number>;  // Per-file processing progress
    fileUploadedBytes: Record<string, number>;   // Per-file upload progress
    fileSize: Record<string, number>;            // Per-file total size
    data: Uint8Array;                            // Binary buffer (XORB_SIZE)
    immutableData: {                             // Checkpoint for backtracking
        chunkIndex: number;
        offset: number;
    } | null;
}
```

Sources: [packages/hub/src/utils/createXorbs.ts:36-83]()

**ChunkCache**

Maintains local deduplication state:

```typescript
class ChunkCache {
    index: number;                           // Current write position (circular)
    xorbIndices: Int32Array;                 // Xorb ID for each cached chunk
    chunkIndices: Uint16Array;               // Chunk index within xorb
    map: Map<string, number>;                // Hash to cache index
    hmacs: Set<string>;                      // HMAC keys for remote lookups
    maxSize: number;                         // Maximum cache entries
}
```

Sources: [packages/hub/src/utils/ChunkCache.ts:5-99]()

### Core Functions

**createXorbs**

Main generator function for chunking and xorb creation:

```typescript
async function* createXorbs(
    fileSources: AsyncGenerator<{ content: Blob; path: string; sha256: string }>,
    params: XetWriteTokenParams & { yieldCallback?: ... }
): AsyncGenerator<XorbEvent | FileEvent>
```

Key responsibilities:
- Initialize WASM chunker
- Stream file content through chunker
- Check local and remote deduplication
- Compress chunks with LZ4
- Assemble xorbs
- Build file representations
- Yield xorb and file events

Sources: [packages/hub/src/utils/createXorbs.ts:85-378]()

**uploadShards**

Generator function for shard assembly and upload:

```typescript
async function* uploadShards(
    source: AsyncGenerator<{ content: Blob; path: string; sha256: string }>,
    params: UploadShardsParams
): AsyncGenerator<FileEvent | FileProgressEvent>
```

Key responsibilities:
- Consume xorb events from createXorbs
- Build file info and xorb info sections
- Assemble shard binary format
- Upload xorbs to CAS
- Upload shards to Hub
- Yield file completion events

Sources: [packages/hub/src/utils/uploadShards.ts:76-349]()

**backtrackDedup**

Retroactively applies remote deduplication to current xorb:

```typescript
function backtrackDedup(
    xorb: CurrentXorbInfo,
    computeHmac: (hash: string, key: string) => string,
    shardData: ShardData,
    chunkCache: ChunkCache,
    chunkMetadata: Array<...>,
    dedupedBytes: number
): number
```

Key responsibilities:
- Find chunks in current xorb that match remote shard
- Remove matched chunks from xorb.data
- Update xorb.chunks array
- Update chunk metadata references
- Update ChunkCache indices
- Return updated deduplication byte count

Sources: [packages/hub/src/utils/createXorbs.ts:380-486]()

**writeChunk**

Writes a compressed chunk to the xorb buffer:

```typescript
function writeChunk(
    xorb: CurrentXorbInfo,
    chunk: Uint8Array,
    hash: string
): boolean
```

Key responsibilities:
- Compress chunk with standard LZ4
- Compress chunk with byte-grouping LZ4
- Select best compression (or raw)
- Write 8-byte chunk header
- Write chunk data
- Return false if xorb is full

Sources: [packages/hub/src/utils/createXorbs.ts:529-559]()

### Integration with Commit Flow

The Xet protocol integrates into the commit flow at the LFS upload stage:

**commit.ts integration points:**

```typescript
// Line 313: Request xet transfer protocol
transfers: ["basic", "multipart", ...(useXet ? ["xet" as const] : [])]

// Line 351-353: Detect if backend supports xet
if (useXet && json.transfer !== "xet") {
    useXet = false;
}

// Line 356-393: Extract xet parameters from response headers
xetParams = {
    sessionId: headers.get("X-Xet-Session-Id") ?? undefined,
    casUrl: headers.get("X-Xet-Cas-Url") ?? undefined,
    accessToken: headers.get("X-Xet-Access-Token") ?? undefined,
    expiresAt: ...,
    refreshWriteTokenUrl: obj.actions.upload.href,
}

// Line 404-439: Call uploadShards with xet parameters
for await (const event of uploadShards(source, { ...params, xetParams }))
```

Sources: [packages/hub/src/lib/commit.ts:313](), [packages/hub/src/lib/commit.ts:351-393](), [packages/hub/src/lib/commit.ts:404-439]()

## Performance Characteristics

The Xet protocol achieves significant bandwidth savings through its deduplication and compression strategy:

**Deduplication Effectiveness:**
- **Similar files**: 80-99% deduplication when uploading model checkpoints or file versions with small changes
- **Content-defined chunking**: Enables deduplication even when content is shifted (e.g., adding a header)
- **Remote deduplication**: Leverages existing Hub content, reducing uploads for popular models

**Compression Ratios:**
- **Byte-grouping LZ4**: Particularly effective for model weights (interleaved floating-point data)
- **Standard LZ4**: Better for text and structured data
- **Adaptive selection**: Automatically chooses best compression or raw based on size

**Overhead:**
- **Shard metadata**: ~200 bytes per file + ~48 bytes per xorb + ~48 bytes per chunk
- **Remote dedup checks**: One HTTP request per 4MB of processed data (configurable via `INTERVAL_BETWEEN_REMOTE_DEDUP`)
- **Local processing**: 10% of progress bar allocated to chunking and compression

Sources: [packages/hub/src/utils/createXorbs.ts:14](), [packages/hub/src/utils/createXorbs.ts:19-21](), [packages/hub/scripts/bench.ts:1-459]()

---

