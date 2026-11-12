<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/datamap-rs · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Cargo.toml](Cargo.toml)
- [README.md](README.md)
- [src/main.rs](src/main.rs)

</details>



## Purpose and Scope

This page explains the high-level architecture of datamap-rs, including its command-based design, local-first processing model, parallel execution strategy, and how the major components interact. It provides an overview of the system's structure without diving into the implementation details of specific commands or processors.

For detailed information about specific commands, see:
- Map command and pipeline processing: [#3](#3)
- Data organization commands (reshard, partition, group, shuffle): [#4](#4)
- Analysis commands (reservoir sample, count): [#5](#5)
- Shared infrastructure components: [#6](#6)

## High-Level Architecture Overview

datamap-rs is built as a **command-line binary** with a **command-based architecture**. Each command implements a specific data processing operation on JSONL files. The system is designed around three core principles:

1. **Local-first processing**: All data must reside on local NVMe storage before processing
2. **File-level parallelism**: Files are processed independently in parallel using Rayon
3. **Streaming I/O**: Documents are processed line-by-line to maintain memory efficiency

The architecture can be visualized in three layers:

| Layer | Components | Responsibility |
|-------|-----------|----------------|
| **CLI Layer** | `clap` argument parser, `Commands` enum | Parse user input and dispatch to appropriate handler |
| **Processing Layer** | Command implementations (`gen_map`, `reshard`, `group`, etc.) | Execute data transformations and operations |
| **Infrastructure Layer** | `GenWriter`, `mj_io`, utility functions | Provide shared I/O, compression, and helper functionality |

**Sources:** [README.md:1-151](), [src/main.rs:49-224]()

### Command Dispatch Architecture

```mermaid
graph TB
    subgraph "Entry Point [main.rs:506-584]"
        Main["main()"]
        ArgParser["ArgParser::parse()"]
        ThreadConfig["Set RAYON_NUM_THREADS"]
    end
    
    subgraph "Commands Enum [main.rs:59-224]"
        Commands["Commands enum"]
        Map["Map { input_dir, output_dir, config, err_dir, delete_after_read }"]
        Reshard["Reshard { input_dir, output_dir, max_lines, max_size, subsample, keep_dirs, delete_after_read }"]
        ReservoirSample["ReservoirSample { input_dir, output_file, key, reservoir_size, token_weighted, text_key }"]
        DiscPart["DiscretePartition { input_dir, output_dir, config, partition_key }"]
        RangePart["RangePartition { input_dir, output_dir, config, value, default_value, range_groups, reservoir_path, num_buckets, max_file_size, bucket_name }"]
        Group["Group { input_dir, group_dir, config, subext }"]
        GroupFilter["GroupFilter { input_dir, output_dir, config }"]
        Shuffle["Shuffle { input_dir, output_dir, num_outputs, max_len, delete_after_read }"]
        Count["Count { input_dir, output_file, count_bytes }"]
    end
    
    subgraph "Command Handlers [main.rs & modules]"
        GenMap["gen_map()"]
        ReshardFn["reshard()"]
        ResSampleFn["reservoir_sample()"]
        DiscPartFn["discrete_partition()"]
        RangePartFn["range_partition()"]
        GroupFn["group()"]
        GroupFilterFn["group_filter()"]
        ShuffleFn["shuffle()"]
        CountFn["count()"]
    end
    
    Main --> ArgParser
    ArgParser --> ThreadConfig
    ThreadConfig --> Commands
    
    Commands --> Map
    Commands --> Reshard
    Commands --> ReservoirSample
    Commands --> DiscPart
    Commands --> RangePart
    Commands --> Group
    Commands --> GroupFilter
    Commands --> Shuffle
    Commands --> Count
    
    Map --> GenMap
    Reshard --> ReshardFn
    ReservoirSample --> ResSampleFn
    DiscPart --> DiscPartFn
    RangePart --> RangePartFn
    Group --> GroupFn
    GroupFilter --> GroupFilterFn
    Shuffle --> ShuffleFn
    Count --> CountFn
```

The `main()` function uses `clap` to parse command-line arguments into the `Commands` enum. Each enum variant contains the specific arguments for that command. The match expression at [main.rs:513-582]() dispatches to the appropriate handler function.

**Sources:** [src/main.rs:49-584]()

## Local-First Architecture and Data Lifecycle

datamap-rs assumes a **local-first workflow** where all input and output data resides on fast local storage (typically AWS Nitro NVMe drives on i4i/i7i instances). This is not just a recommendation but an **architectural requirement** for achieving acceptable performance.

### Typical Data Lifecycle

```mermaid
graph LR
    subgraph "Cloud Storage"
        S3["S3/Weka/GCS<br/>Source Data"]
        S3Out["S3/Weka/GCS<br/>Processed Data"]
    end
    
    subgraph "Local NVMe Storage"
        InputDir["input_dir/<br/>*.jsonl.zst"]
        OutputDir["output_dir/<br/>*.jsonl.zst"]
        TempFiles["Temporary Files<br/>Processing State"]
    end
    
    subgraph "datamap-rs Processing"
        DatamapBin["datamap binary<br/>Command Execution"]
    end
    
    subgraph "Python Utilities"
        S5CMDDown["s5cmd wrapper<br/>Download"]
        S5CMDUp["s5cmd wrapper<br/>Upload"]
    end
    
    S3 --> S5CMDDown
    S5CMDDown --> InputDir
    InputDir --> DatamapBin
    DatamapBin --> OutputDir
    DatamapBin -.temporary.-> TempFiles
    OutputDir --> S5CMDUp
    S5CMDUp --> S3Out
```

The system **never streams from cloud storage**. All commands operate on the assumption that:
1. Input files are available locally before processing begins
2. Output files are written locally during processing
3. Upload to cloud storage happens after processing completes

This design decision provides:
- **Reliability**: No network timeouts or retries during processing
- **Performance**: NVMe drives provide ~10-100x better throughput than S3 streaming
- **Simplicity**: Commands don't need to handle network errors or partial downloads

**Sources:** [README.md:20-21](), [README.md:113-129]()

## Module Organization and Code Structure

The codebase is organized into focused modules, each responsible for specific functionality:

### Module Structure Diagram

```mermaid
graph TB
    subgraph "Main Binary [src/main.rs]"
        MainRs["main.rs<br/>• main() entry point<br/>• Commands enum<br/>• ArgParser<br/>• gen_map() & gen_map_single()<br/>• count()<br/>• parse_config()<br/>• print_global_stats_stuff()"]
    end
    
    subgraph "Map Processing [src/map_fxn.rs]"
        MapFxn["map_fxn.rs<br/>• DataProcessor trait<br/>• PipelineProcessor struct<br/>• process_lines() implementation<br/>• PROCESSOR_CONSTRUCTORS registry<br/>• 31+ processor implementations"]
    end
    
    subgraph "Partitioning [src/partition.rs]"
        Partition["partition.rs<br/>• discrete_partition()<br/>• range_partition()<br/>• PartitionConfig structs<br/>• quantile calculation"]
    end
    
    subgraph "Grouping [src/groupfilter.rs]"
        GroupFilter["groupfilter.rs<br/>• group()<br/>• group_filter()<br/>• GroupConfig structs<br/>• hash-based distribution"]
    end
    
    subgraph "Sampling [src/reservoir_sample.rs]"
        ResSample["reservoir_sample.rs<br/>• reservoir_sample()<br/>• token-weighted sampling<br/>• statistical aggregation"]
    end
    
    subgraph "Utilities [src/utils.rs]"
        Utils["utils.rs<br/>• JSON manipulation<br/>• URL parsing<br/>• helper functions"]
    end
    
    subgraph "Resharding [src/reshard.rs]"
        Reshard["reshard.rs<br/>• reshard()<br/>• file size normalization<br/>• directory preservation"]
    end
    
    subgraph "Shuffling [src/shuffle.rs]"
        Shuffle["shuffle.rs<br/>• shuffle()<br/>• random redistribution"]
    end
    
    subgraph "Shared Infrastructure"
        GenWriter["GenWriter<br/>Defined inline in modules<br/>• Concurrent file writing<br/>• Zstd compression<br/>• File rotation"]
        MjIO["mj_io crate<br/>• expand_dirs()<br/>• read_pathbuf_to_mem()<br/>• write_mem_to_pathbuf()<br/>• get_output_filename()"]
    end
    
    MainRs --> MapFxn
    MainRs --> Partition
    MainRs --> GroupFilter
    MainRs --> ResSample
    MainRs --> Utils
    MainRs --> Reshard
    MainRs --> Shuffle
    
    MapFxn --> Utils
    Partition --> GenWriter
    GroupFilter --> GenWriter
    Shuffle --> GenWriter
    
    MainRs --> MjIO
    MapFxn --> MjIO
    Partition --> MjIO
    GroupFilter --> MjIO
    ResSample --> MjIO
    Reshard --> MjIO
    Shuffle --> MjIO
```

**Key Design Patterns:**

1. **Module per Command**: Each major command has its own module (except Map and Count which live in `main.rs`)
2. **Shared Infrastructure**: `GenWriter` pattern is replicated across modules that need concurrent file writing
3. **External I/O Library**: `mj_io` crate handles all file operations, compression detection, and directory traversal
4. **Trait-based Extensibility**: Map command uses `DataProcessor` trait for pluggable processors

**Sources:** [src/main.rs:24-36](), [Cargo.toml:1-45]()

## Parallel Processing Model

datamap-rs achieves high performance through **file-level parallelism** using Rayon. This design has important implications:

### Parallelism Architecture

```mermaid
graph TB
    subgraph "Main Thread"
        ExpandDirs["expand_dirs()<br/>Collect all input files"]
        BuildPbar["build_pbar()<br/>Progress tracking"]
        RayonSetup["Rayon Thread Pool<br/>Default: num_cpus<br/>Override: --threads N"]
    end
    
    subgraph "Parallel Execution [Rayon]"
        ParIter["all_files.par_iter()"]
        
        subgraph "Thread 1"
            File1["Process file_000.jsonl.zst"]
            Lines1["Read & parse lines"]
            Process1["Process each line sequentially"]
        end
        
        subgraph "Thread 2"
            File2["Process file_001.jsonl.zst"]
            Lines2["Read & parse lines"]
            Process2["Process each line sequentially"]
        end
        
        subgraph "Thread N"
            FileN["Process file_NNN.jsonl.zst"]
            LinesN["Read & parse lines"]
            ProcessN["Process each line sequentially"]
        end
    end
    
    subgraph "Shared State"
        DashMap["DashMap<K, V><br/>Lock-free concurrent map<br/>Used for: GenWriter registry,<br/>statistics aggregation"]
        Atomic["AtomicUsize counters<br/>Thread-safe aggregation<br/>Used for: doc counts,<br/>file sizes, timing"]
    end
    
    ExpandDirs --> BuildPbar
    BuildPbar --> RayonSetup
    RayonSetup --> ParIter
    
    ParIter --> File1
    ParIter --> File2
    ParIter --> FileN
    
    File1 --> Lines1
    Lines1 --> Process1
    
    File2 --> Lines2
    Lines2 --> Process2
    
    FileN --> LinesN
    LinesN --> ProcessN
    
    Process1 -.update.-> DashMap
    Process2 -.update.-> DashMap
    ProcessN -.update.-> DashMap
    
    Process1 -.update.-> Atomic
    Process2 -.update.-> Atomic
    ProcessN -.update.-> Atomic
```

**Key Characteristics:**

| Aspect | Implementation | Rationale |
|--------|---------------|-----------|
| **Parallelism Level** | File-level only | Documents must be processed sequentially through pipelines |
| **Thread Pool** | Rayon with default or `--threads` override | Automatic work stealing, efficient CPU utilization |
| **Shared State** | `DashMap` for registries, `AtomicUsize` for counters | Lock-free concurrency, minimal contention |
| **Memory Usage** | Scales with thread count × file size | Each thread loads entire file into memory |
| **I/O Pattern** | Streaming line-by-line | Memory-efficient document processing |

The parallelism is **embarrassingly parallel** at the file level - each file is processed completely independently. This means:
- No inter-file coordination required during processing
- No locks on data structures (except `GenWriter` output streams)
- Linear scaling with CPU cores (up to I/O limits)

**Sources:** [src/main.rs:359-382](), [README.md:104-112](), [Cargo.toml:14-20]()

## Shared Infrastructure Components

Several infrastructure components are used across multiple commands:

### GenWriter Pattern

The `GenWriter` component provides concurrent, compressed file writing with automatic rotation. While not defined in a single shared location, the pattern is consistently implemented across modules:

**Core Capabilities:**
- **Concurrent writing**: Uses `DashMap<String, Arc<Mutex<BufWriter>>>` to maintain per-stream file handles
- **Zstd compression**: Automatic level-3 compression on all output
- **File rotation**: When files exceed `max_len`, creates new numbered chunks
- **Thread-safe**: Multiple threads can write to different streams simultaneously

**Usage Pattern:**
```rust
// From various modules
let writer_map: DashMap<String, Arc<Mutex<BufWriter<ZstdEncoder>>>> = DashMap::new();
// Each thread writes: writer_map.entry(key).or_insert_with(|| create_writer())
```

**Sources:** [src/partition.rs](), [src/groupfilter.rs](), [src/shuffle.rs]()

### mj_io Library Functions

All file I/O operations use the `mj_io` crate, which provides:

| Function | Purpose | Used By |
|----------|---------|---------|
| `expand_dirs()` | Recursively find all JSONL files in directories | All commands |
| `read_pathbuf_to_mem()` | Read file to memory, auto-detecting compression | All commands |
| `write_mem_to_pathbuf()` | Write bytes to file with Zstd compression | Map, Count commands |
| `get_output_filename()` | Compute output path preserving directory structure | All commands |
| `build_pbar()` | Create progress bar with consistent styling | All commands |

**Sources:** [src/main.rs:21-23](), [Cargo.toml:16]()

### Configuration Parsing

The `parse_config()` function handles both YAML and JSON configuration files:

```rust
// From src/main.rs:230-248
fn parse_config(config: &PathBuf) -> Result<serde_json::Value, Error>
```

This function:
1. Detects file extension (`.yaml`, `.yml`, or `.json`)
2. Parses using appropriate deserializer (`serde_yaml` or `serde_json`)
3. Converts YAML to JSON representation for uniform handling
4. Returns `serde_json::Value` for dynamic processing

**Sources:** [src/main.rs:230-248]()

## Design Principles and Trade-offs

The architecture embodies several key design decisions:

### 1. File-Level Parallelism Only

**Decision:** Process entire files in parallel, but documents sequentially within each file.

**Rationale:**
- Map pipelines require sequential document processing (filters can drop documents)
- File boundaries provide natural parallelization points
- Avoids complex synchronization between pipeline stages

**Trade-off:** Cannot parallelize processing of a single large file

**Sources:** [src/main.rs:359-382]()

### 2. Local Storage Requirement

**Decision:** All data must be on local NVMe before processing.

**Rationale:**
- Network streaming is unreliable (timeouts, partial reads)
- Local NVMe provides 10-100x better throughput
- Simplifies error handling (no network retries)

**Trade-off:** Requires downloading data upfront, storage capacity limits

**Sources:** [README.md:20-21]()

### 3. Memory-Mapped vs. Streaming I/O

**Decision:** Stream line-by-line rather than memory-mapping entire files.

**Rationale:**
- Documents can be arbitrarily large (some datasets have multi-MB documents)
- Memory usage is predictable and bounded
- Allows processing datasets larger than available RAM

**Trade-off:** Slightly slower than memory-mapping for small documents

**Sources:** [src/main.rs:405-411]()

### 4. 256MB Target File Size

**Decision:** Default target file size of ~256MB before compression (reshard command).

**Rationale:**
- Balances parallelism (more files = more parallel work) with overhead
- Fits comfortably in memory for line-by-line processing
- Optimizes S3 upload/download performance

**Trade-off:** May be suboptimal for extreme cases (very small or very large documents)

**Sources:** [README.md:32-33](), [src/main.rs:86-90]()

### 5. Duplicate Infrastructure (GenWriter)

**Decision:** Replicate `GenWriter` pattern in multiple modules rather than sharing.

**Rationale:**
- Each command has slightly different requirements (file naming, rotation logic)
- Avoids coupling between independent commands
- Simpler module structure (no complex shared dependencies)

**Trade-off:** Code duplication, inconsistency risk

**Sources:** Various module implementations

## Thread Control and Resource Management

The system provides explicit control over parallel execution:

**Thread Configuration:**
- **Default behavior**: Use all available CPU cores (`rayon` default)
- **Override with `--threads N`**: Limit parallelism to N threads
- **Implementation**: Sets `RAYON_NUM_THREADS` environment variable at startup

```rust
// From src/main.rs:508-511
let threads = args.threads;
if threads != 0 {
    std::env::set_var("RAYON_NUM_THREADS", threads.to_string());
}
```

**When to Limit Threads:**
- Memory-constrained environments (each thread holds a file in memory)
- Very large files (limit threads to avoid OOM)
- Shared compute resources (respect quotas)

**Sources:** [src/main.rs:49-57](), [src/main.rs:508-511](), [README.md:107]()

## Output Organization Patterns

Different commands organize output in different ways:

| Command | Output Pattern | Example |
|---------|---------------|---------|
| **Map** | `step_{XX}/` directories + `step_final/` | `output_dir/step_00/`, `output_dir/step_final/` |
| **Reshard** | Flat structure or preserved directories | `output_dir/shard_*.jsonl.zst` |
| **DiscretePartition** | Category subdirectories | `output_dir/lang_en/`, `output_dir/lang_es/` |
| **RangePartition** | Numbered bucket subdirectories | `output_dir/bucket_0000/`, `output_dir/bucket_0001/` |
| **Group** | Flat structure with numbered chunks | `group_dir/chunk_*.jsonl.zst` |
| **GroupFilter** | Flat structure | `output_dir/*.jsonl.zst` |
| **Shuffle** | Flat structure with numbered chunks | `output_dir/chunk_*.jsonl.zst` |
| **Count** | Single JSON file | `output_file.json` |
| **ReservoirSample** | Single JSONL file | `output_file.jsonl` |

**Sources:** [src/main.rs:414-422](), [README.md:22-69]()

## Statistics and Monitoring

The Map command provides detailed statistics through shared concurrent state:

**Statistics Collection:**
- **Timing information**: Per-step timing using `DashMap<usize, AtomicUsize>`
- **Filtering information**: Documents removed at each step using `DashMap<usize, usize>`
- **Error counting**: Total errors using `AtomicUsize`
- **Progress tracking**: File-level progress bar via `indicatif`

**Output Format:**
```
Finishing map in X seconds
Processed Y total documents
-------------------------------------------
Step 0 | ProcessorName
     Spent Z% of processing time in this step
     Removed N docs | A% of remaining | B% of pool
...
FINAL:
     M docs survived | P% of pool
```

**Sources:** [src/main.rs:264-321](), [src/main.rs:348-356]()

---

