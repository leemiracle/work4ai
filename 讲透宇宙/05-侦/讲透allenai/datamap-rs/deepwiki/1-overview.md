<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/datamap-rs · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Cargo.toml](Cargo.toml)
- [README.md](README.md)
- [src/main.rs](src/main.rs)

</details>



This document introduces datamap-rs, its purpose, architecture, and when to use it. For installation instructions and environment setup, see [Installation and Setup](#1.1). For hands-on examples, see [Quick Start Guide](#1.2).

## Purpose and Scope

datamap-rs is a high-performance Rust toolkit for processing, filtering, and transforming large-scale text datasets stored in JSONL format. It provides nine specialized commands that operate on terabyte-scale data using parallel processing and a local-first storage architecture.

The system is designed for batch processing workflows where data is downloaded to local NVMe storage, processed using multiple CPU cores, and uploaded back to cloud storage. This approach prioritizes reliability and performance over streaming-based architectures.

**Sources:** [README.md:1-21](), [src/main.rs:1-50]()

## What Problems Does datamap-rs Solve?

datamap-rs addresses the challenges of large-scale data curation and processing:

| Problem | Solution in datamap-rs |
|---------|----------------------|
| **Quality filtering at scale** | Configurable pipeline with 31+ processors (filters, modifiers, annotators) |
| **Uneven file sizes** | `Reshard` command normalizes to 256MB chunks |
| **Categorical organization** | `DiscretePartition` splits by discrete fields (language, domain) |
| **Numeric organization** | `RangePartition` splits by continuous values with quantile support |
| **Deduplication** | Two-stage `Group` → `GroupFilter` workflow |
| **Statistical sampling** | `ReservoirSample` with optional token-weighting |
| **Dataset statistics** | `Count` command for documents, sizes, and text bytes |
| **Data mixing** | `Shuffle` command for random redistribution |

All operations are **embarrassingly parallel at the file level**, processing hundreds of files simultaneously while maintaining deterministic per-document semantics.

**Sources:** [README.md:22-69](), [src/main.rs:59-224]()

## System Architecture

datamap-rs follows a three-layer architecture: Python utilities for cloud I/O, Rust core for data processing, and local NVMe storage as the processing substrate.

```mermaid
graph TB
    subgraph External["External Systems"]
        S3["Cloud Storage<br/>(S3/Weka/GCS)"]
        HF["HuggingFace Hub<br/>(Models & Datasets)"]
    end
    
    subgraph Python["Python Utilities Layer"]
        S5CMD["s5cmd.py<br/>Cloud transfer wrapper"]
        HFDown["dl_hf_model.py<br/>dl_hf_data.py<br/>Model downloaders"]
        Verify["map_verifiers.py<br/>Pre-flight validation"]
    end
    
    subgraph Rust["Rust Binary: datamap-rs"]
        Main["main.rs<br/>ArgParser struct<br/>Commands enum"]
        
        subgraph Transform["Transformation"]
            MapCmd["Map command<br/>gen_map()"]
            Pipeline["map_fxn.rs<br/>PipelineProcessor"]
            Processors["31+ DataProcessor<br/>implementations"]
        end
        
        subgraph Organize["Organization"]
            Reshard["reshard.rs<br/>reshard()"]
            DiscPart["partition.rs<br/>discrete_partition()"]
            RangePart["partition.rs<br/>range_partition()"]
            Group["groupfilter.rs<br/>group()"]
            GroupFilter["groupfilter.rs<br/>group_filter()"]
            Shuffle["shuffle.rs<br/>shuffle()"]
        end
        
        subgraph Analyze["Analysis"]
            ResSample["reservoir_sample.rs<br/>reservoir_sample()"]
            Count["main.rs<br/>count()"]
        end
        
        GenWriter["GenWriter struct<br/>Parallel compressed I/O"]
    end
    
    subgraph Storage["Storage Layer"]
        NVMe["Local NVMe Storage<br/>(AWS i4i/i7i Nitro Drives)"]
    end
    
    S3 -->|"s5cmd sync"| S5CMD
    HF -->|"download"| HFDown
    S5CMD --> NVMe
    HFDown --> NVMe
    
    Verify -.->|"validates"| Pipeline
    
    Main --> Transform
    Main --> Organize
    Main --> Analyze
    
    MapCmd --> Pipeline
    Pipeline --> Processors
    
    Organize --> GenWriter
    
    Transform --> NVMe
    Organize --> NVMe
    Analyze --> NVMe
    
    NVMe -->|"s5cmd sync"| S5CMD
    S5CMD --> S3
```

**Architecture Diagram: Three-Layer System**

The Python layer handles unreliable network I/O, the Rust core performs deterministic data processing, and local NVMe storage provides the performance substrate. The boundary between Python and Rust is the filesystem.

**Sources:** [src/main.rs:1-50](), [README.md:113-128](), [Cargo.toml:1-45]()

## Command Structure

The CLI is implemented using the `clap` framework with a `Commands` enum defining nine subcommands. All commands accept `--threads N` to control parallelism (defaults to all available cores).

```mermaid
graph TB
    CLI["datamap CLI<br/>ArgParser struct<br/>--threads flag"]
    
    CLI --> Transform["Transformation Commands"]
    CLI --> Organize["Organization Commands"]
    CLI --> Analyze["Analysis Commands"]
    
    Transform --> Map["Commands::Map<br/>gen_map()<br/>input_dir, output_dir, config"]
    
    Organize --> Reshard["Commands::Reshard<br/>reshard()<br/>max_size: 256MB default"]
    Organize --> DiscPart["Commands::DiscretePartition<br/>discrete_partition()<br/>partition_key, choices"]
    Organize --> RangePart["Commands::RangePartition<br/>range_partition()<br/>range_groups or quantiles"]
    Organize --> Group["Commands::Group<br/>group()<br/>group_id co-location"]
    Organize --> GroupFilter["Commands::GroupFilter<br/>group_filter()<br/>keep_idx selection"]
    Organize --> Shuffle["Commands::Shuffle<br/>shuffle()<br/>num_outputs buckets"]
    
    Analyze --> ResSample["Commands::ReservoirSample<br/>reservoir_sample()<br/>reservoir_size, token_weighted"]
    Analyze --> Count["Commands::Count<br/>count()<br/>count_bytes optional"]
    
    style Map fill:#f9f9f9
    style CLI fill:#f9f9f9
```

**Command Hierarchy Diagram**

Each command corresponds to a variant in the `Commands` enum at [src/main.rs:59-224]() and dispatches to a dedicated function. The `Map` command is the most complex, supporting arbitrary transformation pipelines.

**Sources:** [src/main.rs:49-224](), [src/main.rs:506-584]()

## Key Design Principles

### Local-First Architecture

datamap-rs **requires** local storage and does not support streaming from cloud storage. This is not a limitation but an architectural decision for reliability and performance.

**Workflow pattern:**
```
1. Download:  s5cmd sync s3://bucket/input ./local/input
2. Process:   datamap map --input-dir ./local/input --output-dir ./local/output
3. Upload:    s5cmd sync ./local/output s3://bucket/output
```

The system assumes fast NVMe drives (AWS i4i/i7i instances with Nitro Drives are recommended). Processing directly from S3 is "finnicky and unreliable" per design documentation.

**Sources:** [README.md:20-21](), [README.md:113-128]()

### File-Level Parallelism

The system uses Rayon's parallel iterators to process files concurrently. Each file is processed by a single thread from start to finish. This means:

- **Parallelism scales with number of files**, not file size
- Documents within a file are processed sequentially through the pipeline
- The 256MB target file size balances parallelism (more files = more parallel work) with memory usage (larger files = more RAM per thread)

```mermaid
graph LR
    Files["Input Files<br/>(JSONL)"]
    
    subgraph Rayon["Rayon Thread Pool<br/>all_files.par_iter()"]
        T1["Thread 1<br/>file_001.jsonl"]
        T2["Thread 2<br/>file_002.jsonl"]
        TN["Thread N<br/>file_NNN.jsonl"]
    end
    
    subgraph Sequential["Per-File Processing<br/>(Sequential)"]
        Doc1["Doc 1"]
        Doc2["Doc 2"]
        DocN["Doc N"]
        
        Doc1 --> Doc2
        Doc2 --> DocN
    end
    
    Files --> Rayon
    T1 -.->|"processes"| Sequential
```

**Parallelism Model Diagram**

At [src/main.rs:359](), the code uses `all_files.par_iter().for_each()` to distribute files across threads. Within each file, documents are processed sequentially at [src/main.rs:407-411]().

**Sources:** [src/main.rs:359-382](), [README.md:104-112]()

### JSONL Format and Compression

All input and output uses **JSONL** (newline-delimited JSON) with **Zstandard compression** (level 3). Files follow the naming pattern `*.jsonl.zst`. This format enables:

- Line-by-line streaming (memory-efficient)
- Parallel processing (each line is independent)
- Fast compression/decompression
- Human-readable when uncompressed

**Sources:** [README.md:10-19](), [Cargo.toml:32]()

## When to Use datamap-rs

Use datamap-rs when you need to:

| Scenario | Recommended Commands |
|----------|---------------------|
| **Filter low-quality documents** | `map` with filter processors |
| **Add metadata annotations** | `map` with annotator processors |
| **Normalize file sizes** | `reshard` to 256MB chunks |
| **Organize by language/domain** | `discrete-partition` by category field |
| **Organize by quality score** | `range-partition` with quantiles |
| **Deduplicate by ID** | `group` then `group-filter` |
| **Create training samples** | `reservoir-sample` with token-weighting |
| **Mix datasets** | `shuffle` for random redistribution |
| **Audit dataset statistics** | `count` for docs/bytes totals |

**Do not use datamap-rs for:**
- Real-time streaming processing (designed for batch)
- Small datasets (<10GB) where overhead isn't worth it
- Non-JSONL formats without conversion
- Processing without local NVMe storage

**Sources:** [README.md:22-69](), [README.md:104-112]()

## Core Components Map

The following table maps system concepts to code entities:

| Concept | Code Entity | Location |
|---------|-------------|----------|
| CLI entry point | `fn main()` | [src/main.rs:506-584]() |
| Command definitions | `enum Commands` | [src/main.rs:59-224]() |
| Argument parsing | `struct ArgParser` | [src/main.rs:49-57]() |
| Pipeline orchestration | `struct PipelineProcessor` | [src/map_fxn.rs]() |
| Individual processors | `trait DataProcessor` | [src/map_fxn.rs]() |
| Parallel file writing | `struct GenWriter` | Referenced in multiple modules |
| Configuration parsing | `fn parse_config()` | [src/main.rs:230-248]() |
| Statistics collection | `DashMap<usize, AtomicUsize>` | [src/main.rs:348-354]() |
| File discovery | `expand_dirs()` | From `mj_io` crate |
| Progress tracking | `build_pbar()` | From `mj_io` crate |

**Sources:** [src/main.rs:1-584](), [Cargo.toml:10-40]()

## Typical Data Flow

A complete processing workflow involves three stages:

```mermaid
graph LR
    S3_In["S3 Storage<br/>s3://bucket/input"]
    
    subgraph Stage1["Stage 1: Download"]
        Download["s5cmd sync<br/>Python wrapper"]
        Local_In["Local NVMe<br/>./local/input"]
    end
    
    subgraph Stage2["Stage 2: Process"]
        Verify["map_verifiers.py<br/>Pre-flight checks"]
        DataMap["datamap binary<br/>Commands::Map or<br/>Commands::Reshard etc"]
        Local_Out["Local NVMe<br/>./local/output"]
    end
    
    subgraph Stage3["Stage 3: Upload"]
        Upload["s5cmd sync<br/>Python wrapper"]
        S3_Out["S3 Storage<br/>s3://bucket/output"]
    end
    
    S3_In --> Download
    Download --> Local_In
    Local_In --> Verify
    Verify --> DataMap
    DataMap --> Local_Out
    Local_Out --> Upload
    Upload --> S3_Out
```

**Complete Workflow Diagram**

The verification step (optional but recommended) checks that required models and banlists exist before processing begins. For complex workflows involving multiple commands, see [Common Workflow Patterns](#1.3).

**Sources:** [README.md:113-137](), [README.md:139-151]()

## Technology Stack Summary

datamap-rs leverages specialized Rust libraries for performance:

| Category | Libraries | Purpose |
|----------|-----------|---------|
| **Concurrency** | `rayon`, `dashmap` | File-level parallelism, lock-free maps |
| **JSON** | `serde_json`, `sonic-rs`, `simd-json`, `gjson` | Parsing, serialization, path queries |
| **Text Processing** | `fasttext`, `tiktoken-rs`, `aho-corasick`, `regex` | ML models, tokenization, pattern matching |
| **Hashing** | `fxhash`, `xxhash-rust`, `ahash` | Fast hashing for grouping/shuffling |
| **Compression** | `zstd` | Level 3 compression for all output |
| **CLI** | `clap` | Command-line argument parsing |

For detailed information on each library and when it's used, see [Technology Stack](#9).

**Sources:** [Cargo.toml:10-40]()

---

**Navigation:**
- Next: [Installation and Setup](#1.1)
- Related: [System Architecture](#2) for deep architectural details
- Related: [Map Command (Pipeline Processing)](#3) for the most complex subsystem

---

