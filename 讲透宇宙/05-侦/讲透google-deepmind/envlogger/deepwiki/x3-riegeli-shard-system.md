<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/envlogger · extra page Riegeli Shard System · fetched 2026-10-26 -->

# Riegeli Shard System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [envlogger/backends/cc/riegeli_shard_reader.cc](envlogger/backends/cc/riegeli_shard_reader.cc)
- [envlogger/backends/cc/riegeli_shard_reader_test.cc](envlogger/backends/cc/riegeli_shard_reader_test.cc)
- [envlogger/backends/cc/riegeli_shard_writer.cc](envlogger/backends/cc/riegeli_shard_writer.cc)
- [envlogger/backends/cc/riegeli_shard_writer.h](envlogger/backends/cc/riegeli_shard_writer.h)
- [envlogger/backends/cc/riegeli_shard_writer_test.cc](envlogger/backends/cc/riegeli_shard_writer_test.cc)

</details>



## Purpose and Scope

The Riegeli Shard System provides a high-performance sharding architecture for storing and retrieving trajectory data using the Riegeli record format. This system implements external indexing to enable O(1) random access to individual steps and episodes within large trajectory datasets.

For the high-level Riegeli backend integration, see [Riegeli Backend](#3.2). For the C++ dataset APIs that use this sharding system, see [Riegeli Dataset APIs](#3.2.3).

## Architecture Overview

The Riegeli Shard System consists of two main components: `RiegeliShardWriter` for data ingestion and `RiegeliShardReader` for data retrieval. The system employs a multi-file architecture where each shard is split into four distinct files to optimize storage and enable efficient random access.

### Core Components

```mermaid
graph TB
    subgraph "Writer System"
        ShardWriter["RiegeliShardWriter"]
        StepsWriter["steps_writer_"]
        StepOffsetsWriter["step_offsets_writer_"]
        EpisodeMetadataWriter["episode_metadata_writer_"]
        EpisodeIndexWriter["episode_index_writer_"]
    end
    
    subgraph "Reader System"
        ShardReader["RiegeliShardReader"]
        StepsReader["steps_reader_"]
        EpisodeMetadataReader["episode_metadata_reader_"]
        ShardData["ShardData"]
    end
    
    subgraph "File System"
        StepsFile["steps.riegeli"]
        StepOffsetsFile["step_offsets.riegeli"]
        EpisodeMetadataFile["episode_metadata.riegeli"]
        EpisodeIndexFile["episode_index.riegeli"]
    end
    
    ShardWriter --> StepsWriter
    ShardWriter --> StepOffsetsWriter
    ShardWriter --> EpisodeMetadataWriter
    ShardWriter --> EpisodeIndexWriter
    
    StepsWriter --> StepsFile
    StepOffsetsWriter --> StepOffsetsFile
    EpisodeMetadataWriter --> EpisodeMetadataFile
    EpisodeIndexWriter --> EpisodeIndexFile
    
    ShardReader --> StepsReader
    ShardReader --> EpisodeMetadataReader
    ShardReader --> ShardData
    
    StepsFile --> StepsReader
    EpisodeMetadataFile --> EpisodeMetadataReader
    StepOffsetsFile --> ShardData
    EpisodeIndexFile --> ShardData
```

**Sources:** [envlogger/backends/cc/riegeli_shard_writer.h:35-116](), [envlogger/backends/cc/riegeli_shard_reader.cc:59-195]()

## File Structure

The sharding system divides trajectory data across four specialized files, each optimized for specific access patterns:

| File Type | Purpose | Content | Access Pattern |
|-----------|---------|---------|----------------|
| **steps** | Trajectory data | `Data` objects containing timesteps, actions, metadata | Sequential/Random via index |
| **step_offsets** | Step index | `Datum` objects with `xt::xarray<int64_t>` offsets | Random access |
| **episode_metadata** | Episode metadata | `Data` objects with episode-level information | Random via episode index |
| **episode_index** | Episode index | `Datum` objects with `(start_step, metadata_offset)` pairs | Random access |

### Index Structure

```mermaid
graph LR
    subgraph "Step Access"
        StepIndex["step_offsets[i]"] --> StepData["steps[offset]"]
    end
    
    subgraph "Episode Access"
        EpisodeIndex["episode_index[j]"] --> EpisodeStart["episode_starts[j]"]
        EpisodeIndex --> MetadataOffset["metadata_offsets[j]"]
        MetadataOffset --> EpisodeMetadata["episode_metadata[offset]"]
    end
    
    subgraph "Data Structures"
        StepOffsets["step_offsets_<br/>vector<int64_t>"]
        EpisodeStarts["episode_starts_<br/>vector<int64_t>"]
        EpisodeOffsets["episode_metadata_offsets<br/>vector<int64_t>"]
    end
    
    StepIndex --> StepOffsets
    EpisodeStart --> EpisodeStarts
    MetadataOffset --> EpisodeOffsets
```

**Sources:** [envlogger/backends/cc/riegeli_shard_writer.h:44-67](), [envlogger/backends/cc/riegeli_shard_reader.cc:72-89]()

## Writer System

The `RiegeliShardWriter` manages the creation and writing of sharded trajectory data through a coordinated multi-file write process.

### Writer Lifecycle

```mermaid
sequenceDiagram
    participant Client
    participant Writer as "RiegeliShardWriter"
    participant StepsWriter as "steps_writer_"
    participant Indexers as "Index Writers"
    
    Client->>Writer: Init(filepaths, options)
    Writer->>StepsWriter: Reset with options
    Writer->>Indexers: Reset with options
    
    loop For each step
        Client->>Writer: AddStep(data, is_new_episode)
        alt is_new_episode
            Writer->>Indexers: Write previous episode metadata
            Writer->>Writer: Update episode_starts_
        end
        Writer->>StepsWriter: WriteRecord(data)
        Writer->>Writer: Record step_offsets_
    end
    
    Client->>Writer: Flush()
    Writer->>StepsWriter: Flush()
    Writer->>Indexers: Write indices and flush
    
    Client->>Writer: Close()
    Writer->>Writer: WriteLastEpisodeIndex()
    Writer->>StepsWriter: Close()
    Writer->>Indexers: Close()
```

**Sources:** [envlogger/backends/cc/riegeli_shard_writer.cc:72-95](), [envlogger/backends/cc/riegeli_shard_writer.cc:179-215]()

### Key Writer Methods

The writer provides several key methods for data ingestion:

- **`Init()`** - Initializes all four file writers with specified options
- **`AddStep()`** - Writes step data and manages episode boundaries
- **`SetEpisodeMetadata()`** - Sets metadata for the current episode
- **`Flush()`** - Writes accumulated indices to disk
- **`Close()`** - Finalizes all files and releases resources

**Sources:** [envlogger/backends/cc/riegeli_shard_writer.h:68-91](), [envlogger/backends/cc/riegeli_shard_writer.cc:99-177]()

## Reader System

The `RiegeliShardReader` provides efficient random access to trajectory data by loading index information at initialization and using it for O(1) lookups.

### Reader Initialization

```mermaid
graph TD
    Init["Init(filepaths)"] --> CreateShardData["Create ShardData"]
    CreateShardData --> ReadStepOffsets["Read step_offsets file"]
    ReadStepOffsets --> ReadEpisodeIndex["Read episode_index file"]
    ReadEpisodeIndex --> CreateReaders["Create steps_reader_ and episode_metadata_reader_"]
    CreateReaders --> Ready["Reader Ready"]
    
    subgraph "ShardData Structure"
        StepOffsets["step_offsets: vector<int64_t>"]
        EpisodeStarts["episode_starts: vector<int64_t>"]
        MetadataOffsets["episode_metadata_offsets: vector<int64_t>"]
        FilePaths["File paths for readers"]
    end
    
    ReadStepOffsets --> StepOffsets
    ReadEpisodeIndex --> EpisodeStarts
    ReadEpisodeIndex --> MetadataOffsets
    CreateReaders --> FilePaths
```

**Sources:** [envlogger/backends/cc/riegeli_shard_reader.cc:61-126](), [envlogger/backends/cc/riegeli_shard_reader.cc:66-67]()

### Reader Operations

The reader supports both step-level and episode-level access:

| Method | Purpose | Time Complexity |
|--------|---------|-----------------|
| `NumSteps()` | Returns total step count | O(1) |
| `NumEpisodes()` | Returns total episode count | O(1) |
| `Step(index)` | Retrieves specific step | O(1) |
| `Episode(index, include_metadata)` | Retrieves episode info | O(1) |
| `Clone()` | Creates independent reader copy | O(1) |

**Sources:** [envlogger/backends/cc/riegeli_shard_reader.cc:140-184]()

## Data Flow Architecture

The system processes trajectory data through a coordinated write-then-read pipeline:

```mermaid
flowchart TD
    subgraph "Write Phase"
        StepData["Step Data<br/>(Data protobuf)"] --> AddStep["AddStep()"]
        EpisodeMetadata["Episode Metadata<br/>(Data protobuf)"] --> SetMetadata["SetEpisodeMetadata()"]
        
        AddStep --> WriteStep["Write to steps_writer_"]
        WriteStep --> RecordOffset["Record step offset"]
        RecordOffset --> CheckEpisode{"New Episode?"}
        CheckEpisode -->|Yes| WriteEpisodeMeta["Write episode metadata"]
        CheckEpisode -->|No| Continue["Continue"]
        WriteEpisodeMeta --> UpdateEpisodeStarts["Update episode_starts_"]
        
        Flush["Flush()"] --> WriteIndices["Write step_offsets and episode_index"]
        WriteIndices --> FlushFiles["Flush all files"]
    end
    
    subgraph "Read Phase"
        LoadIndices["Load indices at Init()"] --> ReadyForAccess["Ready for O(1) access"]
        ReadyForAccess --> StepAccess["Step(i) → steps_reader_.Seek(step_offsets_[i])"]
        ReadyForAccess --> EpisodeAccess["Episode(j) → Calculate from episode_starts_[j]"]
        EpisodeAccess --> MetadataAccess["Load metadata via episode_metadata_offsets[j]"]
    end
    
    FlushFiles --> LoadIndices
```

**Sources:** [envlogger/backends/cc/riegeli_shard_writer.cc:179-215](), [envlogger/backends/cc/riegeli_shard_reader.cc:148-184]()

The shard system's design enables efficient storage and retrieval of large trajectory datasets by separating data from indexing information, allowing for both sequential processing during writes and random access during reads.

---

