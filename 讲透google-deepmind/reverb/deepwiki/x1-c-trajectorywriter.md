<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/reverb · extra page C++ TrajectoryWriter · fetched 2026-10-26 -->

# C++ TrajectoryWriter

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [reverb/cc/trajectory_writer.cc](reverb/cc/trajectory_writer.cc)
- [reverb/cc/trajectory_writer.h](reverb/cc/trajectory_writer.h)
- [reverb/cc/trajectory_writer_test.cc](reverb/cc/trajectory_writer_test.cc)

</details>



## Purpose and Scope

The `TrajectoryWriter` is a C++ implementation of the `ColumnWriter` interface that enables efficient writing of sparse, non-contiguous trajectory data to Reverb tables. Unlike the traditional `Writer` (see [3.2.1](#3.2.1)), which requires dense timestep data where all columns must be specified, `TrajectoryWriter` allows:

- **Sparse column specification**: Write data to only a subset of columns at each timestep
- **Partial step construction**: Build timesteps incrementally using `AppendPartial()`
- **Non-contiguous trajectories**: Create items that reference arbitrary cells across timesteps, not just continuous ranges
- **Asynchronous operation**: All network I/O occurs on a background thread with automatic retry on transient failures

This class is particularly useful for complex RL scenarios where different data types (observations, hidden states, metrics) have different temporal frequencies.

**Related pages**: For the Python API wrapper, see [4.2](#4.2). For low-level chunking details, see [3.2.3](#3.2.3).

Sources: [reverb/cc/trajectory_writer.h:47-145]()

## Class Architecture

### Inheritance and Core Structure

```mermaid
classDiagram
    class ColumnWriter {
        <<interface>>
        +Append(data, refs)*
        +AppendPartial(data, refs)*
        +CreateItem(table, priority, trajectory)*
        +Flush(ignore_last_num_items, timeout)*
        +EndEpisode(clear_buffers, timeout)*
    }
    
    class ClientBidiReactor {
        <<grpc>>
        +OnReadDone(ok)*
        +OnWriteDone(ok)*
        +OnDone(status)*
        +StartCall()*
        +StartRead()*
        +StartWrite()*
    }
    
    class TrajectoryWriter {
        -stub_: ReverbService::StubInterface
        -options_: Options
        -chunkers_: flat_hash_map~int,Chunker~
        -write_queue_: deque~ItemAndRefs~
        -in_flight_items_: flat_hash_map~uint64,ItemAndRefs~
        -stream_worker_: Thread
        -episode_id_: uint64
        -episode_step_: int
        +Append(data, refs)
        +AppendPartial(data, refs)
        +CreateItem(table, priority, trajectory)
        +Flush(ignore_last_num_items, timeout)
        +EndEpisode(clear_buffers, timeout)
        +ConfigureChunker(column, options)
        -RunStreamWorker()
        -SendNotAlreadySentChunks()
        -WaitForPendingItems()
    }
    
    class Chunker {
        +Append(tensor, episode_info, ref)
        +Flush()
        +OnItemFinalized(item, refs)
        +GetKeepKeys()
    }
    
    class TrajectoryColumn {
        -refs_: vector~weak_ptr~CellRef~~
        -squeeze_: bool
        +Validate()
        +LockReferences(locked_refs)
        +ToProto(proto)
    }
    
    ColumnWriter <|-- TrajectoryWriter
    ClientBidiReactor <|-- TrajectoryWriter
    TrajectoryWriter --> Chunker : manages per column
    TrajectoryWriter --> TrajectoryColumn : creates items with
    Chunker --> CellRef : creates
```

Sources: [reverb/cc/trajectory_writer.h:146-229](), [reverb/cc/trajectory_writer.h:231-465](), [reverb/cc/trajectory_writer.h:467-503]()

### Key Data Structures

**ItemAndRefs**

Represents a pending item with its data references:

```mermaid
graph LR
    ItemAndRefs["ItemAndRefs"] --> PrioritizedItem["item: PrioritizedItem<br/>(key, table, priority, trajectory)"]
    ItemAndRefs --> refs["refs: vector&lt;shared_ptr&lt;CellRef&gt;&gt;<br/>(keeps data alive)"]
    
    refs --> CellRef1["CellRef 1<br/>(chunk_key, offset)"]
    refs --> CellRef2["CellRef 2<br/>(chunk_key, offset)"]
    refs --> CellRefN["CellRef N<br/>(chunk_key, offset)"]
```

Sources: [reverb/cc/trajectory_writer.h:255-267]()

**Options**

Configuration for TrajectoryWriter behavior:

| Field | Type | Purpose |
|-------|------|---------|
| `chunker_options` | `shared_ptr<ChunkerOptions>` | Default chunking configuration (max_chunk_length, num_keep_alive_refs, delta_encode, compression) |
| `flat_signature_map` | `optional<FlatSignatureMap>` | Optional table signatures for validation |

Sources: [reverb/cc/trajectory_writer.h:240-253]()

## Data Model: Sparse Trajectories

### Conceptual Model

The TrajectoryWriter treats episodes as sparse tables where:
- **Rows** = timesteps (identified by episode_step)
- **Columns** = tensor streams (e.g., observations, actions, rewards)
- **Cells** = individual tensor values

```mermaid
graph TB
    subgraph "Sparse Trajectory Table"
        direction TB
        R0["Step 0: {C0, C1, C4}"]
        R1["Step 1: {C0, C1, C2, C3, C4}"]
        R2["Step 2: {C0, C1}"]
        R3["Step 3: {C0, C1, C3}"]
    end
    
    subgraph "Item Example"
        direction TB
        I["Item 'trajectory'"]
        Col0["Column 0: [Step0.C0, Step1.C0]"]
        Col1["Column 1: [Step1.C4]"]
        Col2["Column 2: [Step3.C3]"]
    end
    
    R0 -.-> Col0
    R1 -.-> Col0
    R1 -.-> Col1
    R3 -.-> Col2
```

Unlike dense trajectories where all columns must be present at every step, sparse trajectories allow:
- Missing columns in a step (not all tensors need to be written)
- Items that reference non-contiguous steps
- Items where different columns have different lengths

Sources: [reverb/cc/trajectory_writer.h:47-144]()

### Column Management with Chunkers

Each column is managed by a `Chunker` object:

```mermaid
graph LR
    subgraph "TrajectoryWriter State"
        chunkers["chunkers_<br/>flat_hash_map&lt;int, shared_ptr&lt;Chunker&gt;&gt;"]
        override["options_override_<br/>flat_hash_map&lt;int, ChunkerOptions&gt;"]
    end
    
    subgraph "Column 0"
        C0["Chunker 0<br/>(observations)"]
        C0_spec["TensorSpec<br/>(dtype, shape)"]
        C0_opts["ChunkerOptions<br/>(max_chunk_length=10)"]
    end
    
    subgraph "Column 1"
        C1["Chunker 1<br/>(actions)"]
        C1_spec["TensorSpec<br/>(dtype, shape)"]
        C1_opts["ChunkerOptions<br/>(max_chunk_length=20)"]
    end
    
    chunkers --> C0
    chunkers --> C1
    override --> C1_opts
    C0 --> C0_spec
    C0 --> C0_opts
    C1 --> C1_spec
    C1 --> C1_opts
```

Sources: [reverb/cc/trajectory_writer.h:401-408](), [reverb/cc/trajectory_writer.cc:373-386]()

## Core Operations

### Append: Adding Data to Columns

The `Append()` method adds data to column chunkers and increments the episode step:

```mermaid
sequenceDiagram
    participant User
    participant TrajectoryWriter
    participant Chunker0
    participant Chunker1
    
    User->>TrajectoryWriter: Append({tensor0, nullopt, tensor2})
    
    Note over TrajectoryWriter: Check unrecoverable_status_
    Note over TrajectoryWriter: Get episode_info (id, step)
    
    TrajectoryWriter->>TrajectoryWriter: Create Chunker0 if first time
    TrajectoryWriter->>Chunker0: Append(tensor0, episode_info)
    Chunker0-->>TrajectoryWriter: weak_ptr<CellRef>
    
    Note over TrajectoryWriter: Skip index 1 (nullopt)
    
    TrajectoryWriter->>TrajectoryWriter: Create Chunker2 if first time
    TrajectoryWriter->>TrajectoryWriter: Append(tensor2, episode_info)
    TrajectoryWriter-->>User: {ref0, nullopt, ref2}
    
    Note over TrajectoryWriter: Increment episode_step_
    Note over TrajectoryWriter: Signal data_cv_
```

Key behaviors:
- Creates chunkers on-demand when a column is first seen
- Uses `options_override_` if `ConfigureChunker()` was called for that column
- Returns weak_ptr references that must be used in `CreateItem()`
- Thread-safe: acquires mutex for episode_step management

Sources: [reverb/cc/trajectory_writer.cc:347-424]()

### AppendPartial: Incremental Step Construction

`AppendPartial()` enables building steps across multiple calls without incrementing episode_step:

```mermaid
graph TD
    A["User: AppendPartial({obs})"] --> B["episode_step = 5<br/>Column 0: obs"]
    B --> C["User: AppendPartial({nullopt, action})"]
    C --> D["episode_step = 5<br/>Column 1: action"]
    D --> E["User: Append({nullopt, nullopt, reward})"]
    E --> F["episode_step = 6<br/>Column 2: reward"]
    
    style B fill:#f9f9f9
    style D fill:#f9f9f9
    style F fill:#e0e0e0
```

**Validation**: The implementation prevents writing to the same column twice in a partial step sequence:

Sources: [reverb/cc/trajectory_writer.cc:353-424](), [reverb/cc/trajectory_writer_test.cc:519-606]()

### CreateItem: Defining Trajectories

`CreateItem()` constructs a `PrioritizedItem` from trajectory columns:

```mermaid
flowchart TD
    Start["CreateItem(table, priority, trajectory)"] --> Validate1["Validate: trajectory not empty"]
    Validate1 --> Validate2["Validate: priority not NaN"]
    Validate2 --> Lock["Lock all CellRefs<br/>(converts weak_ptr to shared_ptr)"]
    Lock --> Build["Build ItemAndRefs"]
    Build --> Generate["Generate item key"]
    Generate --> Proto["Convert TrajectoryColumns to proto"]
    Proto --> SigCheck["Validate against table signature<br/>(if flat_signature_map provided)"]
    SigCheck --> Enqueue["Enqueue to write_queue_"]
    Enqueue --> Signal["Return immediately<br/>(async processing)"]
    
    Lock --> Expired{{"Any CellRef<br/>expired?"}}
    Expired -->|Yes| Error1["Return InvalidArgumentError"]
    
    SigCheck --> Invalid{{"Signature<br/>mismatch?"}}
    Invalid -->|Yes| Error2["Return InvalidArgumentError<br/>(wrong dtype/shape/num columns)"]
```

Sources: [reverb/cc/trajectory_writer.cc:426-475](), [reverb/cc/trajectory_writer.cc:219-276]()

**TrajectoryColumn Validation**:

Each `TrajectoryColumn` must satisfy:
- No expired CellRefs
- All CellRefs have compatible dtypes and shapes
- If `squeeze=true`, exactly one row

Sources: [reverb/cc/trajectory_writer.cc:813-846]()

### Flush: Synchronization

`Flush()` blocks until pending items are confirmed by the server:

```mermaid
stateDiagram-v2
    [*] --> AcquireLock
    AcquireLock --> ForceChunks: FlushLocked()
    ForceChunks --> SignalWorker: data_cv_.Signal()
    SignalWorker --> Wait: AwaitWithTimeout()
    
    Wait --> CheckCondition
    CheckCondition --> Success: write_queue + in_flight ≤ ignore_last_num_items
    CheckCondition --> Wait: condition not met
    CheckCondition --> Timeout: timeout expired
    
    Success --> [*]: return unrecoverable_status_
    Timeout --> [*]: return DeadlineExceededError
```

**Parameters**:
- `ignore_last_num_items`: Allows "run-ahead" by not blocking on the last N items
- `timeout`: Maximum time to wait (default: infinite)

**Force Flush**: For each non-ignored item, if any referenced CellRef is not ready (chunk incomplete), calls `Chunker::Flush()` to finalize the chunk prematurely.

Sources: [reverb/cc/trajectory_writer.cc:702-750]()

### EndEpisode: Episode Lifecycle

`EndEpisode()` finalizes the current episode and resets state:

```mermaid
sequenceDiagram
    participant User
    participant TrajectoryWriter
    participant Chunkers
    
    User->>TrajectoryWriter: EndEpisode(clear_buffers=false)
    TrajectoryWriter->>TrajectoryWriter: FlushLocked(0, timeout)
    Note over TrajectoryWriter: Wait for all items confirmed
    
    loop For each chunker
        alt clear_buffers = true
            TrajectoryWriter->>Chunkers: Reset()
            Note over Chunkers: Delete all data
        else clear_buffers = false
            TrajectoryWriter->>Chunkers: Flush()
            Note over Chunkers: Finalize incomplete chunks
        end
    end
    
    Note over TrajectoryWriter: Generate new episode_id_
    Note over TrajectoryWriter: Reset episode_step_ = 0
    TrajectoryWriter-->>User: OkStatus
```

Sources: [reverb/cc/trajectory_writer.cc:752-773]()

## Asynchronous Processing

### Background Thread Architecture

TrajectoryWriter uses a dedicated `stream_worker_` thread to handle all gRPC communication:

```mermaid
graph TB
    subgraph "Main Thread (User)"
        Append["Append()"]
        CreateItem["CreateItem()"]
        Flush["Flush()"]
    end
    
    subgraph "Mutex Protected State"
        write_queue["write_queue_<br/>deque&lt;ItemAndRefs&gt;"]
        in_flight["in_flight_items_<br/>map&lt;key, ItemAndRefs&gt;"]
        data_cv["data_cv_<br/>CondVar"]
    end
    
    subgraph "Background Thread (stream_worker_)"
        RunStreamWorker["RunStreamWorker()"]
        WaitForPending["WaitForPendingItems()"]
        SendChunks["SendNotAlreadySentChunks()"]
        WriteItem["Write Item to Stream"]
        HandleConfirm["OnReadDone(): Remove from in_flight_items_"]
    end
    
    Append --> write_queue
    CreateItem --> write_queue
    CreateItem --> data_cv
    Flush --> data_cv
    
    write_queue --> WaitForPending
    WaitForPending --> SendChunks
    SendChunks --> WriteItem
    WriteItem --> in_flight
    HandleConfirm --> in_flight
    in_flight -.-> Flush
```

Sources: [reverb/cc/trajectory_writer.cc:278-328](), [reverb/cc/trajectory_writer.h:446-449]()

### Item State Machine

Items progress through three states:

```mermaid
stateDiagram-v2
    [*] --> write_queue: CreateItem()
    write_queue --> CheckChunks: stream_worker processes
    
    CheckChunks --> WaitForChunks: chunks not ready
    WaitForChunks --> CheckChunks: data_cv_ signaled
    
    CheckChunks --> SendChunks: all chunks ready
    SendChunks --> in_flight_items: WriteIfNotEmpty()
    
    in_flight_items --> Confirmed: server response
    Confirmed --> [*]: removed from map
    
    in_flight_items --> write_queue: connection lost (retry)
    
    note right of write_queue
        Waiting to be sent
        Mutex: write_queue_
    end note
    
    note right of in_flight_items
        Sent but not confirmed
        Mutex: in_flight_items_
    end note
```

Sources: [reverb/cc/trajectory_writer.cc:595-700]()

### Stream Worker Main Loop

The `RunStreamWorker()` function implements the core processing logic:

```mermaid
flowchart TD
    Start["RunStreamWorker()"] --> CreateStream["SetContextAndCreateStream()"]
    CreateStream --> InitVars["streamed_chunk_keys = {}<br/>add_items_to_batch = 0"]
    
    InitVars --> WaitLoop["WaitForPendingItems()"]
    WaitLoop --> CheckExit{{"closed_ or<br/>!stream_ok_?"}}
    CheckExit -->|Yes| FinishStream["Finish()"]
    
    CheckExit -->|No| GetItem["Get front item from write_queue_"]
    GetItem --> SendNewChunks["SendNotAlreadySentChunks()"]
    
    SendNewChunks --> CheckReady{{"All chunks in<br/>streamed_chunk_keys?"}}
    CheckReady -->|No| WaitChunks["Write ready data<br/>data_cv_.Wait()"]
    WaitChunks --> WaitLoop
    
    CheckReady -->|Yes| MoveToInflight["Move to in_flight_items_"]
    MoveToInflight --> NotifyChunkers["Call OnItemFinalized() on chunkers"]
    NotifyChunkers --> AddToRequest["request.AddItem()"]
    AddToRequest --> DecBatch["Decrement add_items_to_batch"]
    
    DecBatch --> CheckBatch{{"add_items_to_batch<br/>== 0?"}}
    CheckBatch -->|Yes| WriteRequest["WriteIfNotEmpty()"]
    WriteRequest --> WaitLoop
    CheckBatch -->|No| WaitLoop
    
    FinishStream --> Return["Return stream_status_"]
```

**Key optimizations**:
- Batches multiple items into single gRPC message (up to `kMaxRequestSizeBytes` = 40MB)
- Tracks `streamed_chunk_keys` to avoid resending chunks
- Sends `keep_chunk_keys` to tell server which chunks are still needed

Sources: [reverb/cc/trajectory_writer.cc:595-700]()

### Retry Logic

The outer loop in `stream_worker_` handles transient failures:

```mermaid
flowchart TD
    ThreadStart["stream_worker_ thread starts"] --> RetryLoop["while(true)"]
    RetryLoop --> RunWorker["RunStreamWorker()"]
    RunWorker --> CheckClosed{{"closed_?"}}
    
    CheckClosed -->|Yes| SetCancel["unrecoverable_status_ = CancelledError"]
    SetCancel --> ThreadExit["Thread exits"]
    
    CheckClosed -->|No| CheckError{{"Is error<br/>Unavailable or<br/>Cancelled?"}}
    
    CheckError -->|No| SetUnrecoverable["unrecoverable_status_ = status"]
    SetUnrecoverable --> ThreadExit
    
    CheckError -->|Yes| RequeueItems["Move in_flight_items_ to<br/>front of write_queue_"]
    RequeueItems --> AdjustBackoff["Adjust retry_backoff<br/>(exponential backoff)"]
    AdjustBackoff --> Sleep["Sleep(retry_backoff)"]
    Sleep --> RetryLoop
```

**Backoff strategy**:
- If stream lasted < 2 seconds: double backoff (up to 1 second max)
- If stream lasted ≥ 2 seconds: reset backoff to 1ms

Sources: [reverb/cc/trajectory_writer.cc:288-327]()

### gRPC Callbacks

TrajectoryWriter implements `ClientBidiReactor` callbacks:

| Callback | Purpose | Actions |
|----------|---------|---------|
| `OnReadDone(bool ok)` | Server sent confirmation | Remove confirmed keys from `in_flight_items_`, start next read, set `stream_ok_=false` if not ok |
| `OnWriteDone(bool ok)` | Write completed | Clear `write_inflight_` flag, set `stream_ok_=false` if not ok |
| `OnDone(Status s)` | Stream terminated | Set `stream_done_=true`, store `stream_status_` |

Sources: [reverb/cc/trajectory_writer.cc:501-528]()

## Memory Management

### Chunk Lifecycle and Keep-Alive

The TrajectoryWriter manages chunk memory through a keep-alive mechanism:

```mermaid
graph TB
    subgraph "Chunker Buffer"
        direction LR
        OldChunk["Chunk 1<br/>(expired)"]
        MidChunk["Chunk 2<br/>(alive)"]
        NewChunk["Chunk 3<br/>(alive)"]
    end
    
    subgraph "CellRef Ownership"
        direction TB
        WeakRef1["weak_ptr<br/>(user has this)"]
        SharedRef2["shared_ptr<br/>(in ItemAndRefs)"]
        SharedRef3["shared_ptr<br/>(in ItemAndRefs)"]
    end
    
    subgraph "Server State"
        ServerChunk2["ChunkData 2"]
        ServerChunk3["ChunkData 3"]
    end
    
    OldChunk -.expired.-> WeakRef1
    MidChunk --> SharedRef2
    NewChunk --> SharedRef3
    
    SharedRef2 --> ServerChunk2
    SharedRef3 --> ServerChunk3
    
    Note1["num_keep_alive_refs<br/>determines how many<br/>recent chunks stay alive"]
```

**Keep Keys**: After each item is written, TrajectoryWriter sends `keep_chunk_keys` to tell the server which chunks to retain in memory:

```mermaid
sequenceDiagram
    participant TW as TrajectoryWriter
    participant Server
    
    Note over TW: Item 1 references chunks {A, B}
    TW->>Server: InsertStreamRequest<br/>{chunks: [A, B], item: 1, keep_keys: [A, B]}
    
    Note over TW: Item 2 references chunks {B, C}
    TW->>Server: InsertStreamRequest<br/>{chunks: [C], item: 2, keep_keys: [B, C]}
    Note over Server: Can delete chunk A now
    
    Note over TW: Item 3 references chunk {C}
    Note over TW: Chunk B expired locally
    TW->>Server: InsertStreamRequest<br/>{item: 3, keep_keys: [C]}
    Note over Server: Can delete chunk B now
```

Sources: [reverb/cc/trajectory_writer.cc:568-593](), [reverb/cc/trajectory_writer.h:383-390]()

### Progressive Cleanup

To prevent unbounded memory growth, TrajectoryWriter periodically cleans up tracking state:

```mermaid
flowchart LR
    A["After each item written"] --> B["GetKeepKeys(streamed_chunk_keys)"]
    B --> C["Filter to only live chunks"]
    C --> D["streamed_chunk_keys = result"]
    D --> E["Expired chunks removed from tracking"]
```

The `GetKeepKeys()` method:
1. Collects chunk keys from all chunkers' keep-alive windows
2. Collects chunk keys from pending items (except front item)
3. Filters both by presence in `streamed_chunk_keys`

Sources: [reverb/cc/trajectory_writer.cc:664-667]()

### Arena-Allocated Requests

To avoid memory fragmentation, `ArenaOwnedRequest` manages protobuf objects efficiently:

```mermaid
classDiagram
    class ArenaOwnedRequest {
        -r_: InsertStreamRequest
        -request_size_bytes_: int64_t
        +AddAllocatedChunks(ChunkData*)
        +AddItem(PrioritizedItem&)
        +AddKeepChunkKeys(uint64_t)
        +Clear()
        +RequestSize() int64_t
    }
    
    note for ArenaOwnedRequest "Uses UnsafeArenaAddAllocated<br/>to avoid copies and minimize<br/>allocation overhead"
```

Sources: [reverb/cc/trajectory_writer.cc:54-91]()

## Error Handling and Validation

### Input Validation

TrajectoryWriter validates inputs at multiple stages:

**Append/AppendPartial Validation**:

```mermaid
flowchart TD
    Append["Append(data)"] --> CheckStatus["Check unrecoverable_status_"]
    CheckStatus --> CheckDtype{{"Column exists?"}}
    CheckDtype -->|Yes| ValidateDtype{{"Dtype matches?"}}
    CheckDtype -->|No| CreateChunker["Create new Chunker"]
    
    ValidateDtype -->|No| ErrorDtype["InvalidArgumentError:<br/>wrong dtype"]
    ValidateDtype -->|Yes| ValidateShape{{"Shape compatible?"}}
    ValidateShape -->|No| ErrorShape["InvalidArgumentError:<br/>incompatible shape"]
    ValidateShape -->|Yes| AppendToChunker["Chunker.Append()"]
```

Sources: [reverb/cc/trajectory_writer_test.cc:449-496]()

**CreateItem Validation**:

| Check | Error Condition | Error Message |
|-------|----------------|---------------|
| Empty trajectory | All columns empty or no columns | "trajectory must not be empty" |
| NaN priority | `std::isnan(priority)` | "`priority` must not be nan" |
| Expired CellRef | Any `weak_ptr` cannot be locked | "Column contains expired CellRef" |
| Column dtype mismatch | CellRefs in same column have different dtypes | "Column references tensors with different dtypes" |
| Column shape mismatch | CellRefs in same column have incompatible shapes | "Column references tensors with incompatible shapes" |
| Squeeze with multiple rows | `squeeze=true` but column has != 1 rows | "TrajectoryColumn must contain exactly one row when squeeze is set" |

Sources: [reverb/cc/trajectory_writer.cc:426-475](), [reverb/cc/trajectory_writer.cc:813-846]()

### Signature Validation

If `Options.flat_signature_map` is provided, CreateItem validates against table signatures:

```mermaid
flowchart TD
    CreateItem["CreateItem(table, ...)"] --> LookupTable{{"Table in<br/>signature_map?"}}
    LookupTable -->|No| ErrorNotFound["InvalidArgumentError:<br/>table not found"]
    LookupTable -->|Yes| CheckSig{{"Signature<br/>provided?"}}
    
    CheckSig -->|No| AllowAny["Allow any trajectory"]
    CheckSig -->|Yes| CheckNumCols{{"Num columns<br/>matches?"}}
    
    CheckNumCols -->|No| ErrorNumCols["InvalidArgumentError:<br/>wrong number of columns"]
    CheckNumCols -->|Yes| LoopCols["For each column"]
    
    LoopCols --> CheckDtype{{"Dtype<br/>matches?"}}
    CheckDtype -->|No| ErrorDtype["InvalidArgumentError:<br/>dtype mismatch"]
    CheckDtype -->|Yes| CheckShape{{"Shape<br/>compatible?"}}
    
    CheckShape -->|No| ErrorShape["InvalidArgumentError:<br/>shape incompatible"]
    CheckShape -->|Yes| NextCol{{"More<br/>columns?"}}
    
    NextCol -->|Yes| LoopCols
    NextCol -->|No| Success["Validation passed"]
```

Sources: [reverb/cc/trajectory_writer.cc:219-276]()

### Unrecoverable Errors

Certain errors cause the TrajectoryWriter to enter a failed state:

```mermaid
stateDiagram-v2
    [*] --> Operational: Constructor
    Operational --> Operational: Transient errors<br/>(Unavailable, Cancelled)
    Operational --> Failed: Non-transient error<br/>(Internal, InvalidArgument, etc)
    Operational --> Failed: Close() called
    Failed --> [*]
    
    note right of Failed
        unrecoverable_status_ set
        All methods return error
        stream_worker_ exits
    end note
```

All public methods check `unrecoverable_status_` before proceeding.

Sources: [reverb/cc/trajectory_writer.cc:367-368](), [reverb/cc/trajectory_writer.h:421-424]()

## Configuration and Tuning

### ChunkerOptions Per Column

Use `ConfigureChunker()` to customize behavior for specific columns:

```mermaid
flowchart LR
    User["User"] --> ConfigureChunker["ConfigureChunker(column, options)"]
    
    ConfigureChunker --> CheckExists{{"Chunker<br/>exists?"}}
    CheckExists -->|Yes| ApplyNow["Chunker.ApplyConfig(options)"]
    CheckExists -->|No| StoreOverride["options_override_[column] = options"]
    
    StoreOverride --> FutureAppend["Future Append()"]
    FutureAppend --> CreateWithOptions["Create Chunker with overridden options"]
```

**Common use cases**:
- Large observations: increase `max_chunk_length` to reduce overhead
- Frequent sampling: increase `num_keep_alive_refs` to prevent premature expiration
- High-frequency columns: enable `delta_encode` for better compression

Sources: [reverb/cc/trajectory_writer.cc:780-790](), [reverb/cc/trajectory_writer.h:309-314]()

### Request Size Limit

TrajectoryWriter splits large requests to avoid gRPC message size limits:

```cpp
// reverb/cc/trajectory_writer.h:238
static constexpr int64_t kMaxRequestSizeBytes = 40 * 1024 * 1024;  // 40MB
```

When `request.RequestSize() >= kMaxRequestSizeBytes`:
1. Send current request with accumulated chunks
2. Continue with remaining chunks in next request

Sources: [reverb/cc/trajectory_writer.h:235-238](), [reverb/cc/trajectory_writer.cc:199-209]()

### Pending Items Warning

If `in_flight_items_.size() + write_queue_.size() >= 50`, the writer logs warnings:

> "The number of pending items is alarmingly high, did you forget to call Flush?"

This indicates the user should call `Flush()` more frequently to avoid OOM.

Sources: [reverb/cc/trajectory_writer.cc:52-52](), [reverb/cc/trajectory_writer.cc:653-662]()

## Integration Points

### Relationship with Chunker

```mermaid
graph LR
    TW["TrajectoryWriter"] -->|"manages"| Chunkers["flat_hash_map<br/>&lt;int, shared_ptr&lt;Chunker&gt;&gt;"]
    
    Chunkers --> C0["Chunker 0"]
    Chunkers --> C1["Chunker 1"]
    Chunkers --> CN["Chunker N"]
    
    C0 -->|"creates"| Chunks0["ChunkData objects"]
    C1 -->|"creates"| Chunks1["ChunkData objects"]
    CN -->|"creates"| ChunksN["ChunkData objects"]
    
    Chunks0 -->|"sent via"| Stream["gRPC InsertStream"]
    Chunks1 -->|"sent via"| Stream
    ChunksN -->|"sent via"| Stream
```

Each `Chunker`:
- Manages a circular buffer of data for one column
- Creates `CellRef` objects that point into chunks
- Notified via `OnItemFinalized()` when items using its data are written
- Can adapt chunking strategy based on usage patterns

Sources: [reverb/cc/trajectory_writer.h:401-408](), [reverb/cc/trajectory_writer.cc:671-687]()

### Relationship with gRPC Service

```mermaid
sequenceDiagram
    participant TW as TrajectoryWriter
    participant Stub as ReverbService::Stub
    participant Server as ReverbServiceImpl
    
    TW->>Stub: async()->InsertStream(context, reactor)
    Stub->>TW: SetReactor()
    TW->>TW: StartCall()
    TW->>TW: StartRead(&response_)
    
    loop Until closed or error
        TW->>TW: StartWrite(&request)
        Note over TW,Stub: Async write
        Stub-->>TW: OnWriteDone(true)
        
        Server-->>Stub: InsertStreamResponse
        Stub-->>TW: OnReadDone(true)
        TW->>TW: StartRead(&response_)
    end
    
    Note over TW: Close() or error
    TW->>TW: context_->TryCancel()
    Stub-->>TW: OnDone(status)
```

The bidirectional stream enables:
- Async writes of chunks and items
- Async reads of confirmation messages
- Parallel processing: writer can send next item while waiting for previous confirmations

Sources: [reverb/cc/trajectory_writer.cc:541-558](), [reverb/cc/trajectory_writer.cc:501-528]()

---

This completes the documentation for the C++ TrajectoryWriter. For information about the Python wrapper around this class, see [4.2](#4.2). For details about the underlying chunking mechanism, see [3.2.3](#3.2.3).

---

