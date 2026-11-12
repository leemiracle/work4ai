<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/envlogger · extra page Riegeli C++ Implementation · fetched 2026-10-26 -->

# Riegeli C++ Implementation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [envlogger/backends/cc/BUILD.bazel](envlogger/backends/cc/BUILD.bazel)
- [envlogger/backends/cc/riegeli_dataset_reader.cc](envlogger/backends/cc/riegeli_dataset_reader.cc)
- [envlogger/backends/cc/riegeli_dataset_writer.cc](envlogger/backends/cc/riegeli_dataset_writer.cc)
- [envlogger/backends/cc/riegeli_dataset_writer.h](envlogger/backends/cc/riegeli_dataset_writer.h)
- [envlogger/backends/cc/riegeli_shard_io_test.cc](envlogger/backends/cc/riegeli_shard_io_test.cc)

</details>



## Purpose and Scope

This document covers the C++ implementation of the Riegeli dataset storage system, specifically the high-level dataset reader and writer classes that manage multiple shards and coordinate I/O operations. The implementation provides efficient, parallel access to trajectory data stored in Riegeli format.

For information about the underlying shard-level I/O operations, see [Riegeli Shard System](#3.2.2). For the Python-facing dataset APIs, see [Riegeli Dataset APIs](#3.2.3). For C++ data serialization, see [C++ XTensor Codec](#4.2).

## Architecture Overview

The Riegeli C++ implementation consists of two primary classes that manage collections of shards, each containing trajectory data organized by episodes and steps.

### Dataset Management Architecture

```mermaid
graph TB
    subgraph "RiegeliDatasetReader"
        RDR_Init["Init(data_dir)"]
        RDR_Clone["Clone()"]
        RDR_Episode["Episode(episode_index)"]
        RDR_GetShard["GetShard(episode_index)"]
        RDR_FindShard["FindShard(global_index)"]
    end
    
    subgraph "RiegeliDatasetWriter"
        RDW_Init["Init(data_dir, metadata)"]
        RDW_AddStep["AddStep(data, is_new_episode)"]
        RDW_SetEpisodeMetadata["SetEpisodeMetadata(data)"]
        RDW_Flush["Flush()"]
    end
    
    subgraph "Shard Management"
        Shard_Struct["Shard struct"]
        RiegeliShardReader_Instance["RiegeliShardReader index"]
        RiegeliShardWriter_Instance["RiegeliShardWriter writer_"]
    end
    
    subgraph "File System"
        DataDir["data_dir/"]
        MetadataFile["metadata.riegeli"]
        TimestampDirs["YYYYMMDDTHHMMSS*/"]
        ShardFiles["steps.riegeli<br/>step_offsets.riegeli<br/>episode_metadata.riegeli<br/>episode_index.riegeli"]
    end
    
    RDR_Init --> DataDir
    RDR_Init --> MetadataFile
    RDR_Init --> TimestampDirs
    RDR_Clone --> Shard_Struct
    RDR_Episode --> RDR_FindShard
    RDR_GetShard --> RiegeliShardReader_Instance
    
    RDW_Init --> DataDir
    RDW_Init --> MetadataFile
    RDW_AddStep --> RiegeliShardWriter_Instance
    RDW_SetEpisodeMetadata --> RiegeliShardWriter_Instance
    
    Shard_Struct --> RiegeliShardReader_Instance
    TimestampDirs --> ShardFiles
    
    RiegeliShardReader_Instance -.-> ShardFiles
    RiegeliShardWriter_Instance -.-> ShardFiles
```

**Sources:** [envlogger/backends/cc/riegeli_dataset_reader.cc:94-167](), [envlogger/backends/cc/riegeli_dataset_writer.cc:86-110](), [envlogger/backends/cc/riegeli_dataset_writer.h:35-84]()

## Core Components

### RiegeliDatasetReader

The `RiegeliDatasetReader` class provides read access to multi-shard Riegeli datasets with support for parallel initialization and efficient episode/step lookups.

#### Key Data Structures

| Component | Purpose | Location |
|-----------|---------|----------|
| `Shard` struct | Manages individual shard metadata and reader | [riegeli_dataset_reader.cc:75-86]() |
| `shards_` vector | Collection of all dataset shards | [riegeli_dataset_reader.cc:105]() |
| `total_num_steps_` | Cumulative step count across shards | [riegeli_dataset_reader.cc:153]() |
| `total_num_episodes_` | Cumulative episode count across shards | [riegeli_dataset_reader.cc:154]() |

#### Parallel Initialization

The reader uses `thread::Bundle` to parallelize shard initialization:

```mermaid
graph LR
    subgraph "Init Process"
        GetSubdirectories["file::GetSubdirectories()"]
        ThreadBundle["thread::Bundle"]
        InitializeShard["initialize_shard lambda"]
        ReadMetadata["ReadFirstRiegeliRecord()"]
    end
    
    subgraph "Per-Shard Tasks"
        ShardInit["shard->index.Init()"]
        StepsFile["steps.riegeli"]
        StepOffsetsFile["step_offsets.riegeli"]
        EpisodeMetadataFile["episode_metadata.riegeli"]
        EpisodeIndexFile["episode_index.riegeli"]
    end
    
    GetSubdirectories --> ThreadBundle
    ThreadBundle --> InitializeShard
    ThreadBundle --> ReadMetadata
    
    InitializeShard --> ShardInit
    ShardInit --> StepsFile
    ShardInit --> StepOffsetsFile
    ShardInit --> EpisodeMetadataFile
    ShardInit --> EpisodeIndexFile
```

**Sources:** [envlogger/backends/cc/riegeli_dataset_reader.cc:126-151](), [envlogger/backends/cc/riegeli_dataset_reader.cc:111-124]()

### RiegeliDatasetWriter

The `RiegeliDatasetWriter` class manages writing trajectory data across multiple shards with automatic shard creation based on episode limits.

#### Shard Management Strategy

The writer creates new shards when episode limits are reached:

| Parameter | Purpose | Default Value |
|-----------|---------|---------------|
| `max_episodes_per_shard_` | Maximum episodes per shard | 0 (unlimited) |
| `episode_counter_` | Current episode counter | 0 |
| `writer_options_` | Riegeli writer options | "transpose,brotli:6,chunk_size:1M" |

**Sources:** [envlogger/backends/cc/riegeli_dataset_writer.h:41-53](), [envlogger/backends/cc/riegeli_dataset_writer.cc:112-122]()

## File Organization and Constants

### Directory Structure

The implementation uses a specific directory structure defined in `riegeli_dataset_io_constants.h`:

```mermaid
graph TB
    subgraph "Dataset Directory Structure"
        DataDir["data_dir/"]
        MetadataFile["metadata.riegeli"]
        TimestampDir1["20231201T143052123456/"]
        TimestampDir2["20231201T143152789012/"]
        TimestampDirN["..."]
        
        subgraph "Shard Files"
            StepsFile["steps.riegeli"]
            StepOffsetsFile["step_offsets.riegeli"]
            EpisodeMetadataFile["episode_metadata.riegeli"]
            EpisodeIndexFile["episode_index.riegeli"]
        end
    end
    
    DataDir --> MetadataFile
    DataDir --> TimestampDir1
    DataDir --> TimestampDir2
    DataDir --> TimestampDirN
    
    TimestampDir1 --> StepsFile
    TimestampDir1 --> StepOffsetsFile
    TimestampDir1 --> EpisodeMetadataFile
    TimestampDir1 --> EpisodeIndexFile
```

### File Constants

The system uses predefined filename constants:

- `kStepsFilename`: Main trajectory data
- `kStepOffsetsFilename`: Step position indices
- `kEpisodeMetadataFilename`: Episode-level metadata
- `kEpisodeIndexFilename`: Episode boundary indices
- `kMetadataFilename`: Dataset-level metadata

**Sources:** [envlogger/backends/cc/riegeli_dataset_reader.cc:98](), [envlogger/backends/cc/riegeli_dataset_reader.cc:114-121](), [envlogger/backends/cc/riegeli_dataset_writer.cc:95-96]()

## Threading and Parallelization

### Parallel Shard Initialization

The reader implements parallel initialization using `thread::Bundle`:

```mermaid
sequenceDiagram
    participant Main as "Main Thread"
    participant Bundle as "thread::Bundle"
    participant Worker1 as "Worker Thread 1"
    participant Worker2 as "Worker Thread 2"
    participant WorkerN as "Worker Thread N"
    
    Main->>Bundle: Add shard initialization tasks
    Main->>Bundle: Add metadata reading task
    Bundle->>Worker1: Initialize shard 1
    Bundle->>Worker2: Initialize shard 2
    Bundle->>WorkerN: Read metadata
    
    Worker1->>Worker1: RiegeliShardReader.Init()
    Worker2->>Worker2: RiegeliShardReader.Init()
    WorkerN->>WorkerN: ReadFirstRiegeliRecord()
    
    Bundle->>Main: JoinAll()
    Main->>Main: Process initialization results
```

**Sources:** [envlogger/backends/cc/riegeli_dataset_reader.cc:126-151]()

### Cumulative Index Building

After parallel initialization, the reader builds cumulative indices for efficient lookups:

- `global_step_index`: Global step offset for each shard
- `cumulative_steps`: Running total of steps up to each shard
- `cumulative_episodes`: Running total of episodes up to each shard

**Sources:** [envlogger/backends/cc/riegeli_dataset_reader.cc:152-161]()

## Integration with Lower-Level Components

### Shard Reader Integration

The dataset reader manages multiple `RiegeliShardReader` instances and provides global indexing:

```mermaid
graph TB
    subgraph "Global Access Pattern"
        GlobalEpisodeIndex["episode_index (global)"]
        GlobalStepIndex["step_index (global)"]
    end
    
    subgraph "Shard Resolution"
        FindShard["FindShard(global_index, extractor)"]
        BinarySearch["std::lower_bound()"]
        LocalIndex["local_index calculation"]
    end
    
    subgraph "Shard Access"
        ShardReader["RiegeliShardReader"]
        LocalEpisode["Episode(local_episode_index)"]
        LocalStep["Step(local_step_index)"]
    end
    
    GlobalEpisodeIndex --> FindShard
    GlobalStepIndex --> FindShard
    FindShard --> BinarySearch
    BinarySearch --> LocalIndex
    LocalIndex --> ShardReader
    ShardReader --> LocalEpisode
    ShardReader --> LocalStep
```

**Sources:** [envlogger/backends/cc/riegeli_dataset_reader.cc:212-223](), [envlogger/backends/cc/riegeli_dataset_reader.cc:177-193]()

### Writer Integration

The dataset writer coordinates with `RiegeliShardWriter` for automatic shard management:

- Creates new shards based on episode limits
- Manages timestamp-based directory naming
- Handles metadata persistence
- Coordinates flushing and closing operations

**Sources:** [envlogger/backends/cc/riegeli_dataset_writer.cc:64-82](), [envlogger/backends/cc/riegeli_dataset_writer.cc:112-122]()

---

