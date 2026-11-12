<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/reverb · extra page C++ Writer Implementation · fetched 2026-10-26 -->

# C++ Writer Implementation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [reverb/cc/writer.cc](reverb/cc/writer.cc)
- [reverb/cc/writer.h](reverb/cc/writer.h)
- [reverb/cc/writer_test.cc](reverb/cc/writer_test.cc)

</details>



## Purpose and Scope

This document details the C++ `Writer` class, which is the low-level implementation for writing data to Reverb tables. The `Writer` handles buffering timesteps, chunking data, compressing and streaming chunks via gRPC, and confirming item insertions asynchronously.

For the Python wrapper around this class, see [Python Client API](#4). For the higher-level trajectory writing abstraction, see [C++ TrajectoryWriter](#3.2.2). For details on compression and delta encoding, see [Chunking and Compression](#3.2.3).

**Sources:** [reverb/cc/writer.h:1-254](), [reverb/cc/writer.cc:1-644]()

## Overview

The `Writer` class provides a low-level interface for streaming timestep data to a Reverb server and creating items that reference sequences of timesteps. It operates in a batched, chunked manner to optimize network transmission and memory usage.

```mermaid
graph TB
    subgraph "Writer Components"
        Buffer["buffer_<br/>(vector of timestep vectors)"]
        Chunks["chunks_<br/>(list of ChunkData)"]
        PendingItems["pending_items_<br/>(list of PrioritizedItem)"]
        Stream["stream_<br/>(gRPC InsertStream)"]
        Worker["ItemConfirmationWorker<br/>(background thread)"]
    end
    
    subgraph "External"
        App["Application Code"]
        Server["ReverbService"]
    end
    
    App -->|"Append()"| Buffer
    App -->|"CreateItem()"| PendingItems
    
    Buffer -->|"Finish() when full"| Chunks
    Chunks -->|"WritePendingData()"| Stream
    PendingItems -->|"WritePendingData()"| Stream
    
    Stream -->|"InsertStreamRequest"| Server
    Server -->|"InsertStreamResponse"| Stream
    
    Stream -->|"Read()"| Worker
    Worker -->|"updates num_items_in_flight_"| App
```

**Sources:** [reverb/cc/writer.h:42-249](), [reverb/cc/writer.cc:73-90]()

## Core Architecture

### Key Data Structures

The `Writer` maintains several internal buffers and queues:

| Member | Type | Purpose |
|--------|------|---------|
| `buffer_` | `vector<vector<Tensor>>` | Unbatched timesteps awaiting chunking |
| `chunks_` | `list<ChunkData>` | Batched and compressed chunks that can be referenced |
| `pending_items_` | `list<PrioritizedItem>` | Items awaiting transmission to server |
| `streamed_chunk_keys_` | `flat_hash_set<uint64_t>` | Keys of chunks already sent to server |
| `inserted_dtypes_and_shapes_` | `vector<DtypesAndShapes>` | Circular buffer of signatures for validation |

**Sources:** [reverb/cc/writer.h:214-240]()

### Configuration Parameters

```mermaid
graph LR
    subgraph "Writer Constructor Parameters"
        stub["stub<br/>(gRPC stub)"]
        chunk_length["chunk_length<br/>(timesteps per chunk)"]
        max_timesteps["max_timesteps<br/>(max history retained)"]
        delta_encoded["delta_encoded<br/>(compression flag)"]
        signatures["signatures<br/>(table schemas)"]
        max_in_flight["max_in_flight_items<br/>(backpressure limit)"]
    end
    
    chunk_length -->|"controls"| Batching["Batching Frequency"]
    max_timesteps -->|"controls"| History["History Window Size"]
    delta_encoded -->|"enables"| Compression["Delta Encoding"]
    max_in_flight -->|"controls"| Backpressure["Flow Control"]
    signatures -->|"enables"| Validation["Type Validation"]
```

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `chunk_length` | User-defined | Number of timesteps batched per chunk |
| `max_timesteps` | User-defined | Maximum history window for item references |
| `delta_encoded` | `false` | Enable delta encoding before compression |
| `max_in_flight_items` | `25` | Maximum unconfirmed items for backpressure |

**Sources:** [reverb/cc/writer.h:45-52](), [reverb/cc/writer.cc:73-90]()

## Buffering and Chunking

### Append Operation Flow

The `Append()` method buffers timesteps and triggers chunking when the buffer reaches `chunk_length_`:

```mermaid
graph TD
    A["Append(data)"] --> B{"closed_?"}
    B -->|Yes| C["Return FailedPreconditionError"]
    B -->|No| D{"buffer_ size matches?"}
    D -->|No| E["Return InvalidArgumentError"]
    D -->|Yes| F["Store dtypes/shapes"]
    F --> G["buffer_.push_back(data)"]
    G --> H{"buffer_.size() >= chunk_length_?"}
    H -->|No| I["Return OK"]
    H -->|Yes| J["Finish(retry=true)"]
    J --> K{"Success?"}
    K -->|No| L["Undo buffer_.push_back()"]
    K -->|Yes| M["Return OK"]
    L --> N["Return error"]
```

**Sources:** [reverb/cc/writer.cc:96-133]()

### Chunk Creation

The `Finish()` method converts buffered timesteps into a `ChunkData`:

```mermaid
graph TB
    subgraph "Finish() Process"
        A["buffer_<br/>(timesteps)"] --> B["Batch tensors<br/>by column"]
        B --> C{"delta_encoded_?"}
        C -->|Yes| D["DeltaEncodeList()"]
        C -->|No| E["Skip encoding"]
        D --> F["CompressTensorAsProto()"]
        E --> F
        F --> G["Create ChunkData"]
        G --> H["Set sequence_range<br/>(episode_id, start, end)"]
        H --> I["chunks_.push_back()"]
        I --> J["WriteWithRetries()"]
        J --> K{"Success?"}
        K -->|Yes| L["Clear buffer_<br/>Increment index_within_episode_<br/>Remove old chunks"]
        K -->|No| M["Pop chunk from chunks_"]
    end
```

The batching process at line [reverb/cc/writer.cc:421-443]() concatenates tensors column-wise:

1. For each column index `i` in `[0, num_columns)`:
   - Extract tensor at column `i` from each timestep in `buffer_`
   - Insert a dimension at position 0 with size 1
   - Concatenate all tensors along dimension 0

**Sources:** [reverb/cc/writer.cc:420-485]()

### Sequence Range Tracking

Each chunk is tagged with a `SequenceRange` that identifies its position within an episode:

```cpp
chunk_data.mutable_sequence_range()->set_episode_id(episode_id_);
chunk_data.mutable_sequence_range()->set_start(index_within_episode_);
chunk_data.mutable_sequence_range()->set_end(index_within_episode_ + buffer_.size() - 1);
```

This enables the server to track temporal relationships and detect sequence gaps.

**Sources:** [reverb/cc/writer.cc:447-450]()

## gRPC Streaming Protocol

### Stream Lifecycle

```mermaid
stateDiagram-v2
    [*] --> NoStream: Writer created
    NoStream --> StreamActive: WritePendingData() called
    StreamActive --> NoStream: Stream error / Close()
    StreamActive --> StreamActive: Write chunks/items
    NoStream --> [*]: Close() with no pending data
    
    note right of StreamActive
        - InsertStream bidirectional stream
        - ItemConfirmationWorker active
        - Reads responses async
    end note
```

The stream is lazily initialized on first write at [reverb/cc/writer.cc:514-519]():

```cpp
if (!stream_) {
  streamed_chunk_keys_.clear();
  context_ = std::make_unique<grpc::ClientContext>();
  stream_ = stub_->InsertStream(context_.get());
  StartItemConfirmationWorker();
}
```

**Sources:** [reverb/cc/writer.cc:500-575](), [reverb/cc/writer.h:153-157]()

### Write Protocol

The `WritePendingData()` method implements the write protocol:

```mermaid
graph TB
    A["WritePendingData()"] --> B["Collect chunk keys<br/>referenced by pending_items_"]
    B --> C["For each chunk in chunks_"]
    C --> D{"chunk referenced<br/>AND not streamed?"}
    D -->|Yes| E["Add to request.chunks"]
    D -->|No| F["Skip or add to keep_keys"]
    E --> G{"request.ByteSizeLong()<br/>>= 40MB?"}
    G -->|Yes| H["stream_->Write(request)"]
    G -->|No| C
    H --> C
    F --> C
    C --> I["For each pending_item"]
    I --> J["ConfirmItems(max_in_flight - 1)"]
    J --> K["Add item to request"]
    K --> L["Add keep_chunk_keys to request"]
    L --> M["stream_->Write(request)"]
    M --> N["Increment num_items_in_flight_"]
    N --> I
```

Key aspects:
- **Chunk deduplication**: Only sends chunks not yet streamed (tracked in `streamed_chunk_keys_`)
- **Size limiting**: Splits large requests at 40MB boundary ([reverb/cc/writer.cc:543]())
- **Keep-alive**: Sends `keep_chunk_keys` to prevent server from garbage collecting chunks
- **No compression**: Uses `WriteOptions.set_no_compression()` since data is already compressed

**Sources:** [reverb/cc/writer.cc:500-575]()

### Keep-Alive Protocol

The `keep_chunk_keys` field in `InsertStreamRequest` tells the server which chunks to retain:

```mermaid
sequenceDiagram
    participant W as Writer
    participant S as Server
    
    Note over W: buffer_=[t0,t1], creates chunk0
    W->>S: InsertStreamRequest<br/>{chunks: [chunk0], keep_keys: [chunk0.key]}
    
    Note over W: buffer_=[t2,t3], creates chunk1
    W->>S: InsertStreamRequest<br/>{chunks: [chunk1], keep_keys: [chunk0.key, chunk1.key]}
    
    Note over W: chunk0 goes out of scope<br/>(> max_timesteps)
    W->>S: InsertStreamRequest<br/>{chunks: [chunk2], keep_keys: [chunk1.key, chunk2.key]}
    
    Note over S: Garbage collects chunk0
```

**Sources:** [reverb/cc/writer.cc:535-562]()

## Item Creation and Confirmation

### CreateItem Operation

The `CreateItem()` method builds a `PrioritizedItem` that references a trajectory of timesteps:

```mermaid
graph TB
    A["CreateItem(table, num_timesteps, priority)"] --> B["Validate num_timesteps <= buffered"]
    B --> C["GetFlatSignature(table)"]
    C --> D{"Has signature?"}
    D -->|Yes| E["Validate each timestep<br/>against signature"]
    E --> F{"Valid?"}
    F -->|No| G["Return InvalidArgumentError"]
    D -->|No| H["Skip validation"]
    F -->|Yes| I["Create PrioritizedItem"]
    H --> I
    I --> J["Build FlatTimestepTrajectory"]
    J --> K["Calculate chunk_keys and chunk_lengths"]
    K --> L["pending_items_.push_back(item)"]
    L --> M{"buffer_.empty()?"}
    M -->|Yes| N["WriteWithRetries(true)"]
    M -->|No| O["Return OK (item pending)"]
```

The trajectory construction at [reverb/cc/writer.cc:266-296]() works backwards from the most recent timestep:

1. If `buffer_` is not empty, include it as the last chunk
2. Traverse `chunks_` in reverse until `num_timesteps` is satisfied
3. Reverse the order to get chronological ordering
4. Create `FlatTimestepTrajectory` with offset to handle partial chunk inclusion

**Sources:** [reverb/cc/writer.cc:168-307]()

### Signature Validation

When table signatures are provided, `CreateItem()` validates each timestep against the expected schema:

```mermaid
graph TB
    A["For each timestep offset t"] --> B["Get dtypes_and_shapes_t from<br/>inserted_dtypes_and_shapes_"]
    B --> C{"Size matches signature?"}
    C -->|No| D["Return InvalidArgumentError"]
    C -->|Yes| E["For each column c"]
    E --> F{"Dtype matches?"}
    F -->|No| G["Return InvalidArgumentError"]
    F -->|Yes| H{"Shape compatible with<br/>signature OR trajectory?"}
    H -->|No| I["Return InvalidArgumentError"]
    H -->|Yes| J{"More columns?"}
    J -->|Yes| E
    J -->|No| K{"More timesteps?"}
    K -->|Yes| A
    K -->|No| L["Validation passed"]
```

The validation supports two modes:
- **Per-timestep**: Shape matches signature directly
- **Per-trajectory**: Shape matches `[num_timesteps] + signature_shape`

This flexibility allows the writer to work with tables that expect either individual timesteps or full trajectories.

**Sources:** [reverb/cc/writer.cc:186-259]()

## Asynchronous Item Confirmation

### Confirmation Worker Thread

The `ItemConfirmationWorker` thread reads `InsertStreamResponse` messages asynchronously:

```mermaid
graph TB
    subgraph "Main Thread"
        A["WritePendingData()"] --> B["stream_->Write(item)"]
        B --> C["num_items_in_flight_++"]
        C --> D["ConfirmItems(limit)"]
        D --> E{"num_items_in_flight_<br/><= limit?"}
        E -->|No| F["mu_.Await()"]
        E -->|Yes| G["Continue"]
        F --> E
    end
    
    subgraph "ItemConfirmationWorker Thread"
        H["mu_.Await(num_items_in_flight_ > 0)"] --> I["stream_->Read(&response)"]
        I --> J{"Read successful?"}
        J -->|Yes| K["num_items_in_flight_ -= response.keys_size()"]
        J -->|No| L["item_confirmation_worker_running_ = false"]
        K --> M["Wake waiting threads"]
        M --> H
        L --> N["Thread exits"]
    end
    
    M -.notifies.-> F
```

The worker provides **backpressure control**: when `num_items_in_flight_` reaches `max_in_flight_items_`, the main thread blocks in `ConfirmItems()` until the worker decrements the count.

**Sources:** [reverb/cc/writer.cc:615-641](), [reverb/cc/writer.h:124-148]()

### Thread Lifecycle

```mermaid
sequenceDiagram
    participant M as Main Thread
    participant W as Worker Thread
    participant S as Stream
    
    Note over M: First WritePendingData()
    M->>M: Create stream
    M->>W: StartItemConfirmationWorker()
    activate W
    W->>W: item_confirmation_worker_running_ = true
    W->>M: Notify started
    
    loop While items in flight
        M->>S: Write(item)
        M->>M: num_items_in_flight_++
        W->>S: Read(response)
        S-->>W: Response
        W->>W: num_items_in_flight_ -= N
    end
    
    Note over M: Close() or error
    M->>W: item_confirmation_worker_stop_requested_ = true
    W->>W: item_confirmation_worker_running_ = false
    deactivate W
    M->>M: Join worker thread
```

**Sources:** [reverb/cc/writer.cc:357-374](), [reverb/cc/writer.cc:335-355]()

## Error Handling and Retry Logic

### Retry Strategy

The `WriteWithRetries()` method implements retry logic for transient errors:

```mermaid
graph TD
    A["WriteWithRetries(retry_on_unavailable)"] --> B["WritePendingData()"]
    B --> C{"Success?"}
    C -->|Yes| D["Return OK"]
    C -->|No| E["stream_->WritesDone()"]
    E --> F["StopItemConfirmationWorker()"]
    F --> G["status = stream_->Finish()"]
    G --> H["stream_ = nullptr"]
    H --> I{"IsUnavailable(status)<br/>AND retry_on_unavailable?"}
    I -->|Yes| J["Loop: retry"]
    I -->|No| K["Return error"]
    J --> B
```

Only `UNAVAILABLE` errors are retried, indicating transient server issues. Other errors (e.g., `INVALID_ARGUMENT`) are permanent and returned immediately.

**Sources:** [reverb/cc/writer.cc:487-498]()

### Error Recovery on Append

When `Append()` triggers `Finish()` and an error occurs, the operation is **fully rolled back**:

```cpp
auto status = Finish(/*retry_on_unavailable=*/true);
if (!status.ok()) {
  // Undo adding stuff to the buffer and undo the dtypes_and_shapes_ changes.
  buffer_.pop_back();
  insert_dtypes_and_shapes_location_ =
      PositiveModulo(insert_dtypes_and_shapes_location_ - 1, max_timesteps_);
  std::swap(dtypes_and_shapes_t,
            inserted_dtypes_and_shapes_[insert_dtypes_and_shapes_location_]);
}
```

This ensures that `buffer_` and `inserted_dtypes_and_shapes_` remain consistent even if network errors occur.

**Sources:** [reverb/cc/writer.cc:123-132]()

### Close Error Handling

The `Close()` method has special handling for unavailable servers:

```mermaid
graph TD
    A["Close(retry_on_unavailable)"] --> B{"pending_items_ empty?"}
    B -->|No| C["Finish(retry_on_unavailable)"]
    C --> D{"Success?"}
    D -->|Yes| E["Continue"]
    D -->|No| F{"IsUnavailable AND<br/>!retry_on_unavailable?"}
    F -->|Yes| G["Log warning,<br/>set server_unavailable=true"]
    F -->|No| H["Return error"]
    B -->|Yes| E
    G --> E
    E --> I{"stream_ exists?"}
    I -->|Yes| J{"server_unavailable?"}
    J -->|No| K["stream_->WritesDone()"]
    K --> L["ConfirmItems(0)"]
    J -->|Yes| M["Skip WritesDone"]
    L --> N["StopItemConfirmationWorker()"]
    M --> N
    N --> O["stream_->Finish()"]
    O --> P["closed_ = true"]
    I -->|No| P
```

When `retry_on_unavailable=false` and the server is unavailable, the writer logs a warning but still closes successfully, preventing hangs when the server is down.

**Sources:** [reverb/cc/writer.cc:376-418]()

## State Management

### Episode and Index Tracking

```mermaid
graph LR
    subgraph "Writer State"
        episode_id["episode_id_<br/>(random uint64)"]
        index["index_within_episode_<br/>(int32)"]
        next_key["next_chunk_key_<br/>(random uint64)"]
    end
    
    episode_id -->|"identifies"| Episode["Episode boundary"]
    index -->|"tracks"| Position["Position in episode"]
    next_key -->|"identifies"| Buffer["Current buffer"]
    
    Finish["Finish()"] -->|"increments"| index
    Finish -->|"generates new"| next_key
```

Each `ChunkData` is tagged with:
- `episode_id_`: A randomly generated ID that persists for the lifetime of the writer
- `start`/`end`: Indices within the episode (from `index_within_episode_`)

This enables the server to detect episode boundaries and sequence continuity.

**Sources:** [reverb/cc/writer.cc:84-86](), [reverb/cc/writer.cc:447-450](), [reverb/cc/writer.cc:474]()

### Circular Buffer for Signature Validation

The `inserted_dtypes_and_shapes_` circular buffer stores signatures of recently appended timesteps:

```mermaid
graph TB
    A["Append(data)"] --> B["Store dtypes/shapes<br/>at insert_dtypes_and_shapes_location_"]
    B --> C["insert_dtypes_and_shapes_location_ =<br/>(location + 1) % max_timesteps_"]
    
    D["CreateItem(table, num_timesteps)"] --> E["For timestep offset t"]
    E --> F["check_offset = (location - 1 - t) % max_timesteps_"]
    F --> G["Validate inserted_dtypes_and_shapes_[check_offset]"]
    G --> H{"More timesteps?"}
    H -->|Yes| E
    H -->|No| I["Validation complete"]
```

This design allows validation of any trajectory within the last `max_timesteps_` without storing full tensors.

**Sources:** [reverb/cc/writer.cc:108-118](), [reverb/cc/writer.cc:191-218](), [reverb/cc/writer.h:235-240]()

## Usage Pattern

### Typical Usage Flow

```mermaid
sequenceDiagram
    participant App
    participant Writer
    participant Buffer
    participant Chunks
    participant Server
    
    App->>Writer: Writer(stub, chunk_length=3, max_timesteps=10)
    
    loop Episode
        App->>Writer: Append(timestep_0)
        Writer->>Buffer: Store timestep
        App->>Writer: Append(timestep_1)
        Writer->>Buffer: Store timestep
        App->>Writer: Append(timestep_2)
        Writer->>Buffer: Store timestep
        Note over Writer: buffer_.size() == chunk_length
        Writer->>Chunks: Create chunk_0
        Writer->>Server: Write chunk_0
        
        App->>Writer: CreateItem("table", num_timesteps=3, priority=1.0)
        Writer->>Server: Write item referencing chunk_0
        
        App->>Writer: Append(timestep_3)
        Writer->>Buffer: Store timestep
        App->>Writer: CreateItem("table", num_timesteps=1, priority=2.0)
        Note over Writer: Item pending (buffer not full)
        
        App->>Writer: Flush()
        Writer->>Chunks: Create chunk_1
        Writer->>Server: Write chunk_1 + pending item
    end
    
    App->>Writer: Close()
    Writer->>Server: WritesDone()
    Note over Writer: Wait for confirmations
    Writer->>Server: Finish()
```

**Sources:** [reverb/cc/writer_test.cc:275-433]()

## Memory Management

### Chunk Lifecycle

Chunks are retained in `chunks_` only while they may be referenced:

```cpp
while ((chunks_.size() - 1) * chunk_length_ >= max_timesteps_) {
  streamed_chunk_keys_.erase(chunks_.front().chunk_key());
  chunks_.pop_front();
}
```

This ensures memory usage is bounded by `(max_timesteps_ / chunk_length_ + 1) * chunk_size`.

**Sources:** [reverb/cc/writer.cc:477-480]()

### Arena-Owned Requests

To avoid memory leaks from protobuf arena allocation, `WritePendingData()` uses a custom `ArenaOwnedRequest` wrapper:

```cpp
class ArenaOwnedRequest {
 public:
  ~ArenaOwnedRequest() { Clear(); }
  void Clear() {
    while (!r.chunks().empty()) {
      r.mutable_chunks()->UnsafeArenaReleaseLast();
    }
  }
  InsertStreamRequest r;
};
```

This ensures chunks added to the request via `UnsafeArenaAddAllocated()` are properly released.

**Sources:** [reverb/cc/writer.cc:501-513]()

## Key Implementation Details

### Random ID Generation

```cpp
uint64_t Writer::NewID() {
  return absl::Uniform<uint64_t>(bit_gen_, 0, UINT64_MAX);
}
```

Uses Abseil's high-quality random number generator to generate unique IDs for episodes, chunks, and items.

**Sources:** [reverb/cc/writer.cc:577-579]()

### Positive Modulo Helper

```cpp
int PositiveModulo(int value, int divisor) {
  if (divisor == 0) return value;
  if ((value > 0) == (divisor > 0)) {
    return value % divisor;
  } else {
    return (value % divisor + divisor) % divisor;
  }
}
```

Ensures modulo operations always return non-negative results, critical for circular buffer indexing.

**Sources:** [reverb/cc/writer.cc:59-69]()

### AppendSequence Batching

`AppendSequence()` efficiently appends batched timesteps by slicing along the batch dimension:

```cpp
for (int i = 0; i < sequence[0].dim_size(0); i++) {
  std::vector<tensorflow::Tensor> step;
  step.reserve(sequence.size());
  for (const auto& column : sequence) {
    auto slice = column.SubSlice(i);
    if (!slice.IsAligned()) {
      slice = tensorflow::tensor::DeepCopy(slice);
    }
    step.push_back(std::move(slice));
  }
  REVERB_RETURN_IF_ERROR(Append(std::move(step)));
}
```

This allows batch-first data formats common in ML to be efficiently written without manual unbatching.

**Sources:** [reverb/cc/writer.cc:135-166]()

---

