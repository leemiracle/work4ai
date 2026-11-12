<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/decon · page 5 Data Pipeline · fetched 2026-10-26 -->

# Data Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [config/evals.yaml](config/evals.yaml)
- [python/evals.py](python/evals.py)

</details>



## Purpose and Scope

This page describes how data flows through the decon system, covering both evaluation/reference datasets and training data. It explains the overall pipeline architecture, data sources, and transformations that occur before contamination detection begins.

For detailed information about specific configuration syntax, see [Evaluation Dataset Configuration](#5.1). For implementation details of the normalization process, see [Dataset Normalization Process](#5.2). For complete specifications of data formats, see [Data Formats and Structures](#5.3).

## Overview

The decon system processes two distinct types of data:

1. **Reference/Evaluation Data**: Benchmark datasets (MMLU, GSM8K, HumanEval, etc.) that are normalized into a unified format and indexed for contamination detection
2. **Training Data**: Large-scale datasets being checked for contamination, processed in parallel during detection

These data streams are independent until the detection phase, where the reference index is queried against training data to identify contamination.

```mermaid
graph TB
    subgraph "Reference Data Path"
        A["HuggingFace Datasets<br/>~150 benchmarks"]
        B["Local JSONL Files"]
        C["Bundled Pre-processed<br/>bundled-evals/"]
        
        A --> D["python/evals.py<br/>Dataset Normalization"]
        B --> D
        C --> E["Output Directory<br/>~/.local/share/decon/references/"]
        
        D --> E
        E --> F["Normalized JSONL<br/>eval_key_split-N.jsonl.gz"]
    end
    
    subgraph "Training Data Path"
        G["Training Corpus<br/>*.jsonl.gz files"]
        G --> H["Direct Input<br/>No preprocessing required"]
    end
    
    subgraph "Detection Phase"
        F --> I["reference_index.rs<br/>build_simple_index()"]
        I --> J["SimpleReferenceIndex<br/>N-gram lookup structure"]
        
        H --> K["detection.rs<br/>contamination_detect()"]
        
        J -.->|"Query during detection"| K
        K --> L["Contamination Reports<br/>matches.jsonl"]
    end
    
    style D fill:#f9f9f9
    style I fill:#f9f9f9
    style K fill:#f9f9f9
```

**Sources**: High-level system architecture diagrams, [python/evals.py:1-994](), [config/evals.yaml:1-2176]()

## Evaluation Data Pipeline

The evaluation data pipeline transforms diverse benchmark datasets into a standardized format suitable for indexing and contamination detection.

### Data Sources

Evaluation datasets are sourced from three types of locations:

| Source Type | Configuration | Example | Processing |
|------------|---------------|---------|------------|
| HuggingFace | `hf_path` + optional `hf_config` | `allenai/ai2_arc` with config `ARC-Challenge` | Downloaded via HuggingFace `datasets` library |
| Local Files | `local_path` | `path/to/dataset.jsonl` | Loaded directly from filesystem |
| Bundled Pre-processed | `local_path` with `bundled_evals/` prefix | `bundled_evals/agi_eval_` | Copied directly to output directory |

**Sources**: [config/evals.yaml:7-9](), [python/evals.py:711-782]()

### Normalization Architecture

```mermaid
graph LR
    subgraph "Input Processing"
        A["Raw Dataset Example<br/>{...arbitrary fields...}"]
        A --> B["process_answers()<br/>python/evals.py:188-528"]
    end
    
    subgraph "Field Extraction"
        B --> C["extract_prompt()<br/>python/evals.py:578-637"]
        B --> D["extract_passage()<br/>python/evals.py:555-575"]
        B --> E["extract_answer()<br/>python/evals.py:640-705"]
        
        C --> F["get_nested_field()<br/>python/evals.py:531-552"]
        D --> F
        E --> F
    end
    
    subgraph "Record Creation"
        C --> G["Unified Record<br/>{eval_key, question, answer, passage, ...}"]
        D --> G
        E --> G
        
        G --> H["ChunkedFileWriter.write()<br/>python/evals.py:81-96"]
        H --> I["Add Fingerprint<br/>SHA256 hash for deduplication<br/>python/evals.py:138-157"]
    end
    
    subgraph "Output"
        I --> J["JSONL Output<br/>~/.local/share/decon/references/<br/>eval_key_split-N.jsonl.gz"]
    end
    
    style B fill:#f9f9f9
    style F fill:#f9f9f9
    style H fill:#f9f9f9
```

**Sources**: [python/evals.py:188-528](), [python/evals.py:531-705](), [python/evals.py:56-157]()

### Processing Flow

The main processing function `process_eval_dataset()` orchestrates the normalization:

```mermaid
graph TB
    A["process_eval_dataset()<br/>python/evals.py:708-879"] --> B{"Source Type?"}
    
    B -->|"Bundled"| C["Copy Pre-processed Files<br/>bundled-evals/ → output/"]
    B -->|"HuggingFace"| D["load_dataset()<br/>datasets library"]
    B -->|"Local"| E["load_local_jsonl()<br/>python/evals.py:160-166"]
    
    C --> F["Done"]
    D --> G["Iterate Splits<br/>train, test, validation, etc."]
    E --> G
    
    G --> H["For Each Example"]
    H --> I["process_answers()<br/>Expand to multiple records if needed"]
    
    I --> J["Extract Fields:<br/>prompt, passage, answer"]
    J --> K["Create Record with Metadata:<br/>eval_key, doc_id, split, fingerprint"]
    
    K --> L["ChunkedFileWriter.write()<br/>Buffer and write to 5MB chunks"]
    
    L --> M{"More Examples?"}
    M -->|"Yes"| H
    M -->|"No"| N["Close Writer<br/>Flush buffers"]
    
    N --> F
    
    style A fill:#f9f9f9
    style I fill:#f9f9f9
    style L fill:#f9f9f9
```

**Sources**: [python/evals.py:708-879]()

### Answer Expansion

A key feature of the normalization process is **answer expansion**, where a single dataset example may generate multiple output records. This is implemented in `process_answers()` which handles several expansion patterns:

| Expansion Method | Configuration Key | Purpose | Example |
|-----------------|-------------------|---------|---------|
| Multiple Choice | `expand_choices` | Create one record per answer choice | MMLU: 4 records per question (A/B/C/D) |
| Prefix Pattern | `expand_prefix` | Expand fields matching prefix | PIQA: `sol1`, `sol2` → 2 records |
| Parallel Arrays | `array` in prompts/answers | One record per array element | CoQA: multiple Q&A pairs per passage |
| Indexed Access | `indexed` | Select answer using key field | Direct single answer extraction |

**Sources**: [python/evals.py:188-528](), [config/evals.yaml:20-68]()

## Training Data Pipeline

Training data flows through a simpler pipeline as it requires no preprocessing:

```mermaid
graph LR
    A["Training Corpus<br/>Large JSONL files<br/>*.jsonl.gz"] --> B["detection.rs<br/>process_simple_training_file()"]
    
    B --> C["Read Line-by-Line<br/>Each line = document"]
    
    C --> D["Extract 'text' Field<br/>or use entire line"]
    
    D --> E["Tokenize<br/>Using configured tokenizer"]
    
    E --> F["Sample Every M Tokens<br/>Extract N-grams"]
    
    F --> G["Query Reference Index<br/>Check for matches"]
    
    G --> H{"Match Found?"}
    H -->|"Yes"| I["Cluster Expansion<br/>Exhaustive analysis"]
    H -->|"No"| F
    
    I --> J["Contamination Report"]
    
    style B fill:#f9f9f9
    style G fill:#f9f9f9
    style I fill:#f9f9f9
```

Training data files must be in JSONL format (optionally gzipped) with one document per line. Each line should either:
- Be a JSON object with a `"text"` field containing the document content
- Be a plain string (treated as the document text)

**Sources**: Algorithm design from high-level diagrams, implementation in Rust `src/detect/detection.rs`

## Data Format Transformations

### Input Format Diversity

Evaluation datasets arrive in highly diverse formats. Here are examples of how different dataset structures are normalized:

**Multiple Choice (MMLU)**:
```json
// Input from HuggingFace
{
  "question": "What is the capital of France?",
  "choices": ["London", "Paris", "Berlin", "Madrid"],
  "answer": 1,
  "subject": "geography"
}

// Output: 4 records (one per choice)
{"eval_key": "mmlu", "question": "What is the capital of France?", 
 "answer": "London", "is_correct": false, "fingerprint": "a1b2c3..."}
{"eval_key": "mmlu", "question": "What is the capital of France?", 
 "answer": "Paris", "is_correct": true, "fingerprint": "d4e5f6..."}
// ... 2 more records
```

**Parallel Arrays (CoQA)**:
```json
// Input
{
  "story": "The cat sat on the mat...",
  "questions": {"input_text": ["Where was the cat?", "What did it sit on?"]},
  "answers": {"input_text": ["on the mat", "the mat"]}
}

// Output: 2 records (one per Q&A pair)
{"eval_key": "coqa", "passage": "The cat sat on the mat...",
 "question": "Where was the cat?", "answer": "on the mat", "sub_index": 0}
{"eval_key": "coqa", "passage": "The cat sat on the mat...",
 "question": "What did it sit on?", "answer": "the mat", "sub_index": 1}
```

**Sources**: [config/evals.yaml:926-940](), [config/evals.yaml:508-517]()

### Output Format Standardization

All evaluation datasets are normalized to a consistent JSONL format with these fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `eval_key` | string | Yes | Dataset identifier (e.g., "mmlu", "gsm8k") |
| `eval_instance_index` | integer | Yes | Index within the source split |
| `split` | string | Yes | Dataset split ("train", "test", "validation") |
| `question` | string | Yes | The prompt/question text |
| `doc_id` | integer | Yes | Global unique document ID |
| `config` | string | No | HuggingFace config name if applicable |
| `fingerprint` | string | Yes | SHA256 hash (first 16 chars) for deduplication |
| `passage` | string | No | Supporting context or reference text |
| `answer` | string | No | Expected response (omitted for some test splits) |
| `sub_index` | integer | No | Index when multiple records from one example |
| `is_correct` | boolean | No | For multiple choice: marks correct option |

**Sources**: [python/evals.py:3-39](), [python/evals.py:836-865]()

### Chunked Output

The `ChunkedFileWriter` class automatically splits large datasets into 5MB chunks to avoid creating very large files:

```mermaid
graph TB
    A["ChunkedFileWriter<br/>python/evals.py:56-157"] --> B["Initialize<br/>base_path, chunk_number=0"]
    
    B --> C["write(record)"]
    C --> D["Add Fingerprint<br/>SHA256 of passage+question+answer"]
    
    D --> E{"Current Chunk<br/>+ Record Size<br/>> 5MB?"}
    
    E -->|"Yes"| F["_start_new_chunk()<br/>Close current, open new file<br/>Increment chunk_number"]
    E -->|"No"| G["Add to Buffer"]
    
    F --> G
    
    G --> H{"Buffer Size<br/>>= 1000 records?"}
    
    H -->|"Yes"| I["_flush_buffer()<br/>Write to disk"]
    H -->|"No"| J["Continue"]
    
    I --> J
    J --> C
    
    K["close()"] --> L["Flush Remaining Buffer"]
    L --> M["Close Current File"]
    
    style A fill:#f9f9f9
    style D fill:#f9f9f9
    style F fill:#f9f9f9
```

Output files follow the naming pattern: `{eval_key}_{split}-{chunk_number}.jsonl` (optionally gzipped).

Example: `mmlu_test-1.jsonl.gz`, `mmlu_test-2.jsonl.gz`, ...

**Sources**: [python/evals.py:56-157]()

## Configuration-Driven Processing

The entire normalization pipeline is driven by `config/evals.yaml`, which defines ~150 evaluation datasets. Each dataset configuration specifies:

- **Data source**: `hf_path` (HuggingFace) or `local_path` (local file)
- **Splits to process**: List of split names
- **Field extraction rules**: How to find prompts, passages, and answers in the source format
- **Special processing**: Expansion methods, transformations, filtering

The configuration supports a rich extraction DSL with operations like:
- `expand_choices`: Create multiple records from multiple-choice options
- `expand_prefix`: Match fields by prefix pattern (e.g., `answer1`, `answer2`)
- `indexed`: Access array elements using a key field
- `concat_messages`: Concatenate conversation history
- `array`: Process parallel arrays of prompts and answers

This design allows adding new datasets without modifying code—only configuration changes are needed.

**Sources**: [config/evals.yaml:1-68](), [python/evals.py:188-528]()

## Relationship to Detection Phase

The normalized evaluation data serves as input to the reference index construction phase:

```mermaid
graph LR
    A["Normalized JSONL Files<br/>~/.local/share/decon/references/"] --> B["reference_index.rs<br/>build_simple_index()"]
    
    B --> C["For Each Record:<br/>Tokenize question, answer, passage"]
    
    C --> D["Extract N-grams<br/>Default: 5-grams"]
    
    D --> E["Build Index Structures:<br/>• N-gram hash → ID<br/>• ID → Doc IDs list<br/>• IDF weights"]
    
    E --> F["SimpleReferenceIndex<br/>Ready for contamination queries"]
    
    F -.->|"Used during detection"| G["detection.rs<br/>contamination_detect()"]
    
    style B fill:#f9f9f9
    style F fill:#f9f9f9
    style G fill:#f9f9f9
```

The three text components (question, answer, passage) are indexed separately, allowing component-specific matching and scoring during detection. See [Reference Index Construction](#4.2) for implementation details and [Detection and Cluster Expansion](#4.3) for how the index is queried.

**Sources**: High-level system architecture diagrams, Rust implementation in `src/detect/reference_index.rs` and `src/detect/detection.rs`

---

