<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/decon · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [doc/simple.md](doc/simple.md)

</details>



This document provides a high-level introduction to the **decon** contamination detection system. It covers the system's purpose, architecture, key components, and operational modes. For installation and usage instructions, see [Getting Started](#2). For algorithm details, see [The SIMPLE Algorithm](#4). For configuration options, see [Configuration Guide](#3.3).

## Purpose

**Decon** identifies contamination between training datasets and evaluation datasets. Contamination occurs when evaluation data (test questions, answers, passages) leaks into training data, invalidating benchmark results. Decon uses deterministic, token-based sampling and counting methods to detect such contamination at scale.

The system produces:
- **Contamination reports**: JSONL files identifying which training documents contain which evaluation instances
- **Purified datasets**: Cleaned training data with contaminated documents removed
- **Statistical summaries**: Breakdown of contamination by evaluation suite

Decon is designed for large-scale datasets (billions of tokens) and emphasizes reproducibility through configuration files and deterministic algorithms.

**Sources:** [README.md:1-8](), [README.md:10-23]()

## System Architecture

Decon uses a **two-stage architecture** separating data preparation from detection:

```mermaid
graph TB
    subgraph Stage1["Stage 1: Evaluation Data Preparation (Python)"]
        EvalConfig["config/evals.yaml<br/>~150 dataset definitions"]
        EvalsPy["python/evals.py<br/>normalize_dataset()"]
        BundledEvals["bundled-evals/<br/>Normalized JSONL files"]
        
        EvalConfig --> EvalsPy
        EvalsPy --> BundledEvals
    end
    
    subgraph Stage2["Stage 2: Contamination Detection (Rust)"]
        RefIndexBuild["src/detect/reference_index.rs<br/>build_simple_reference_index()"]
        Detection["src/detect/detection.rs<br/>contamination_detect()"]
        ClusterExpand["src/detect/cluster.rs<br/>expand_bidirectional()"]
        
        BundledEvals --> RefIndexBuild
        RefIndexBuild --> Detection
        Detection --> ClusterExpand
    end
    
    subgraph Inputs["Inputs"]
        TrainingData["Training data<br/>JSONL files"]
        DefaultConfig["config/default.yaml<br/>Algorithm parameters"]
    end
    
    subgraph Outputs["Outputs"]
        Reports["Contamination reports<br/>output-dir/reports.jsonl"]
        PurifiedData["Purified datasets<br/>output-dir/purified/"]
        Stats["Statistical summaries<br/>decon review --stats"]
    end
    
    TrainingData --> Detection
    DefaultConfig --> RefIndexBuild
    DefaultConfig --> Detection
    
    Detection --> Reports
    Detection --> PurifiedData
    Reports --> Stats
```

**Sources:** [README.md:1-23](), [doc/simple.md:1-11]()

## Key Components

### CLI Interface

The main entry point is `src/main.rs`, which provides five primary commands:

| Command | Purpose | Key Implementation |
|---------|---------|-------------------|
| `detect` | Run contamination detection | [src/detect/detection.rs:contamination_detect()]() |
| `review` | Analyze detection results | [src/detect/display.rs:print_highlighted_output()]() |
| `evals` | Manage evaluation datasets | [python/evals.py:download_and_normalize()]() |
| `compare` | Compare detection runs | [src/detect/display.rs:compare_reports()]() |
| `server` | Launch HTTP API server | [src/server.rs:run_server()]() |

**Sources:** [README.md:62-82](), [README.md:124-129]()

### Detection Pipeline

The detection pipeline follows this workflow:

```mermaid
graph LR
    Main["src/main.rs<br/>main()"]
    DetectCmd["src/main.rs<br/>Commands::Detect"]
    LoadConfig["src/common/config.rs<br/>load_config()"]
    BuildIndex["src/detect/reference_index.rs<br/>build_simple_reference_index()"]
    ProcessFiles["src/detect/detection.rs<br/>process_simple_training_file()"]
    ExpandCluster["src/detect/cluster.rs<br/>expand_bidirectional()"]
    ScoreEntry["src/detect/contamination_entry.rs<br/>ContaminationEntry::new()"]
    WriteOutput["src/detect/detection.rs<br/>write reports & purified data"]
    
    Main --> DetectCmd
    DetectCmd --> LoadConfig
    DetectCmd --> BuildIndex
    BuildIndex --> ProcessFiles
    ProcessFiles --> ExpandCluster
    ExpandCluster --> ScoreEntry
    ScoreEntry --> WriteOutput
```

**Sources:** [doc/simple.md:7-10](), [README.md:24-57]()

### Reference Index Structure

The `SimpleReferenceIndex` in [src/detect/reference_index.rs]() implements a two-tier lookup structure:

```mermaid
graph TB
    EvalDocs["Evaluation documents<br/>Questions, Answers, Passages"]
    Tokenize["Tokenization<br/>(cl100k_base by default)"]
    NGrams["N-gram extraction<br/>(5-grams by default)"]
    
    subgraph Index["SimpleReferenceIndex"]
        NGramMap["ngram_id_to_doc_ids<br/>HashMap&lt;NGramId, Vec&lt;DocId&gt;&gt;"]
        HashToId["ngram_hash_to_id<br/>HashMap&lt;u64, NGramId&gt;"]
        IDFWeights["idf_weights<br/>HashMap&lt;NGramId, f32&gt;"]
        HotBucket["hot_bucket_ngram_id<br/>Sentinel for high-frequency n-grams"]
    end
    
    EvalDocs --> Tokenize
    Tokenize --> NGrams
    NGrams --> HashToId
    HashToId --> NGramMap
    NGrams --> IDFWeights
    NGrams --> HotBucket
```

The two-tier design optimizes for the sparsity of initial matches: most n-grams from training data won't match anything, so the first hash lookup quickly filters non-matches before accessing document sets.

**Sources:** [doc/simple.md:12-19]()

## Data Flow

### Evaluation Data Pipeline

Evaluation datasets flow through a normalization pipeline to produce a unified format:

| Source Format | Examples | Normalization | Output Format |
|--------------|----------|---------------|---------------|
| Multiple choice | MMLU (57 domains) | `expand_choices` | Q/A/P JSONL |
| Math reasoning | GSM8K | Field extraction | Q/A/P JSONL |
| Code generation | HumanEval | `concat_messages` | Q/A/P JSONL |
| Extractive QA | SQuAD | Field mapping | Q/A/P JSONL |

All datasets are normalized to include:
- `question`: String
- `answer`: String
- `passage`: Optional string
- `fingerprint`: SHA256 hash for deduplication
- `metadata`: Dataset-specific information

**Sources:** [README.md:88-120]()

### Training Data Processing

Training data is processed in parallel using sampling and cluster expansion:

```mermaid
graph LR
    TrainingFiles["Training files<br/>*.jsonl.gz"]
    SampleTokens["Sample every M tokens<br/>(M=10 by default)"]
    CheckIndex["Check SimpleReferenceIndex<br/>n-gram lookup"]
    
    subgraph NoMatch["No Match Path"]
        ContinueSampling["Continue sampling"]
    end
    
    subgraph Match["Match Path"]
        InitCluster["Initialize cluster<br/>Track matching doc IDs"]
        ExpandBi["expand_bidirectional()<br/>src/detect/cluster.rs"]
        ScoreOverlap["Score IDF-weighted overlap<br/>ContaminationEntry"]
        CheckThreshold["Score ≥ threshold?"]
    end
    
    TrainingFiles --> SampleTokens
    SampleTokens --> CheckIndex
    CheckIndex -->|"No match"| ContinueSampling
    CheckIndex -->|"Match found"| InitCluster
    ContinueSampling --> SampleTokens
    InitCluster --> ExpandBi
    ExpandBi --> ScoreOverlap
    ScoreOverlap --> CheckThreshold
    CheckThreshold -->|"Yes"| ContaminationReport["Write to reports.jsonl"]
    CheckThreshold -->|"No"| ContinueSampling
```

**Sources:** [doc/simple.md:21-33](), [README.md:10-23]()

## Execution Modes

Decon supports two operational modes:

### Single-Machine CLI Mode

The CLI mode is a sequential workflow for processing datasets on a single machine:

```mermaid
graph TB
    User["User"]
    EvalsCmd["decon evals --download<br/>Download & normalize eval datasets"]
    DetectCmd["decon detect --training-dir<br/>Run contamination detection"]
    ReviewCmd["decon review output-dir<br/>Analyze results"]
    CompareCmd["decon compare dir-a dir-b<br/>Compare runs"]
    
    User --> EvalsCmd
    EvalsCmd --> DetectCmd
    DetectCmd --> ReviewCmd
    ReviewCmd --> CompareCmd
```

**Sources:** [README.md:59-82]()

### Distributed Server Mode

The server mode enables horizontal scaling for large training datasets:

```mermaid
graph TB
    Orchestrator["Orchestration script<br/>(user-provided)"]
    
    subgraph Workers["Decon Server Workers"]
        Server1["decon server --port 8080<br/>Worker 1"]
        Server2["decon server --port 8081<br/>Worker 2"]
        ServerN["decon server --port 808N<br/>Worker N"]
    end
    
    SharedIndex["Shared SimpleReferenceIndex<br/>(read-only, built once)"]
    
    Orchestrator -->|"POST /submit-documents"| Server1
    Orchestrator -->|"POST /submit-documents"| Server2
    Orchestrator -->|"POST /submit-documents"| ServerN
    
    Orchestrator -->|"GET /status"| Server1
    Orchestrator -->|"GET /status"| Server2
    Orchestrator -->|"GET /status"| ServerN
    
    Server1 -.->|"Reads"| SharedIndex
    Server2 -.->|"Reads"| SharedIndex
    ServerN -.->|"Reads"| SharedIndex
    
    Server1 -->|"Results"| ResultStorage["Result storage<br/>(S3, filesystem, etc.)"]
    Server2 -->|"Results"| ResultStorage
    ServerN -->|"Results"| ResultStorage
```

The server exposes HTTP endpoints implemented in [src/server.rs](). Each worker processes batches independently, with the reference index built once and shared read-only across all workers.

**Sources:** [README.md:122-133]()

## Technology Stack

### Languages and Frameworks

| Component | Language | Key Dependencies |
|-----------|----------|-----------------|
| Detection engine | Rust 1.88+ | `rayon` (parallelism), `tokio` (async), `axum` (HTTP) |
| Data normalization | Python 3 | `datasets` (HuggingFace), `PyYAML` |
| Configuration | YAML | `serde_yaml` parser |

### File Structure

```mermaid
graph TB
    subgraph Rust["Rust Implementation (src/)"]
        MainRS["src/main.rs<br/>CLI entry point"]
        CommonRS["src/common/<br/>config.rs, tokenizer.rs, utils.rs"]
        DetectRS["src/detect/<br/>detection.rs, reference_index.rs<br/>cluster.rs, contamination_entry.rs"]
        ServerRS["src/server.rs<br/>HTTP API"]
    end
    
    subgraph Python["Python Scripts (python/)"]
        EvalsPy["python/evals.py<br/>Dataset normalization"]
    end
    
    subgraph Config["Configuration (config/)"]
        DefaultYAML["config/default.yaml<br/>Algorithm parameters"]
        EvalsYAML["config/evals.yaml<br/>~150 dataset definitions"]
    end
    
    subgraph Data["Data Directories"]
        BundledEvals["bundled-evals/<br/>Normalized eval datasets"]
        TestData["tests/fixtures/<br/>Test training data"]
    end
    
    subgraph Docs["Documentation (doc/)"]
        SimpleMD["doc/simple.md<br/>Algorithm overview"]
        ReproYAML["doc/repro/*.yaml<br/>Historical run configs"]
    end
    
    MainRS --> CommonRS
    MainRS --> DetectRS
    MainRS --> ServerRS
    MainRS --> DefaultYAML
    
    EvalsPy --> EvalsYAML
    EvalsPy --> BundledEvals
    
    DetectRS --> BundledEvals
    DetectRS --> DefaultYAML
```

**Sources:** [README.md:1-154]()

## Configuration System

Decon's behavior is controlled entirely through YAML configuration files:

| Configuration File | Purpose | Key Parameters |
|-------------------|---------|----------------|
| `config/default.yaml` | Detection algorithm parameters | `ngram_size`, `sample_every_m_tokens`, `contamination_score_threshold` |
| `config/evals.yaml` | Evaluation dataset definitions | `dataset_name`, `field_extractions`, `split` |
| `doc/repro/*.yaml` | Historical run configurations | Complete parameter sets for reproducing published results |

Parameters in `config/default.yaml` control every aspect of the SIMPLE algorithm, from index construction through scoring thresholds. See [Configuration Guide](#3.3) for detailed parameter documentation.

**Sources:** [README.md:84](), [README.md:102-118]()

## Output Formats

Decon produces structured outputs for both machine and human consumption:

### Contamination Reports

Reports are written as JSONL files in the output directory. Each line represents one contaminated match:

```jsonl
{
  "training_line": 42,
  "eval_key": "mmlu:abstract_algebra:test:0",
  "contamination_score": 0.95,
  "idf_overlap": 0.87,
  "question_cluster": {"start": 100, "end": 150},
  "answer_cluster": {"start": 160, "end": 175}
}
```

### Purified Datasets

When `--purify` flag is used, decon creates cleaned versions of training data with contaminated documents removed, preserving directory structure and compression formats.

### Statistical Summaries

The `decon review --stats` command aggregates reports by evaluation suite, showing counts of contaminated documents per benchmark.

**Sources:** [README.md:135-154](), [README.md:24-57]()

## Key Design Principles

1. **Deterministic**: Same input always produces same output; no randomness in detection
2. **Interpretable**: Every contamination match includes highlighted text snippets showing overlap
3. **Scalable**: Sampling and parallel processing enable billion-token dataset analysis
4. **Configurable**: All algorithm parameters exposed through YAML for reproducibility
5. **Language-separated**: Python handles messy data wrangling; Rust handles performance-critical detection

**Sources:** [README.md:3-8](), [doc/simple.md:1-3]()

---

