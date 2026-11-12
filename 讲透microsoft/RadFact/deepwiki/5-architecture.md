<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/RadFact · page 5 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [src/radfact/llm_utils/engine/engine.py](src/radfact/llm_utils/engine/engine.py)

</details>



This document provides a technical overview of RadFact's internal architecture, focusing on the major components, their relationships, and how data flows through the system. This page covers the high-level structure and design patterns. For detailed information about specific subsystems, see:

- [System Overview](#5.1) - Visual representation of component interactions
- [LLM Engine](#5.2) - Details on parallel processing orchestration
- [Structured Processor](#5.3) - LLM interaction and prompt handling
- [Caching System](#5.4) - Redis and SQLite caching implementation
- [Parallel Processing](#5.5) - Data sharding and worker management
- [Azure Integration](#5.6) - Azure service integration patterns

## Architectural Principles

RadFact is designed around three core principles:

1. **Parallel Processing**: Data is sharded across multiple LLM endpoints based on throughput, enabling efficient processing of large datasets
2. **Fault Tolerance**: Incremental progress tracking and caching ensure that failed runs can be resumed without losing work
3. **Configuration-Driven**: Hydra-based configuration management allows flexible deployment across different LLM providers and environments

**Sources**: [README.md:1-275](), [src/radfact/llm_utils/engine/engine.py:50-362]()

## Layered Architecture

The system is organized into five distinct architectural layers:

```mermaid
graph TB
    subgraph Layer1["User Interface Layer"]
        CLI1["run_radfact<br/>(CLI entry point)"]
        CLI2["run_report_to_phrases<br/>(CLI entry point)"]
    end
    
    subgraph Layer2["Application Layer"]
        RF["RadFact Metrics<br/>Computation"]
        RTP["Report to Phrases<br/>Conversion"]
    end
    
    subgraph Layer3["Processing Infrastructure"]
        ENGINE["LLMEngine<br/>(engine.py)"]
        PROC["BaseProcessor /<br/>StructuredProcessor"]
        SUBSET["DataSubset<br/>(data_subset.py)"]
    end
    
    subgraph Layer4["Configuration & Caching"]
        HYDRA["Hydra ConfigStore"]
        CACHE["Redis / SQLite<br/>LangChain Cache"]
        ARGS["LLMEngineArguments<br/>LLMAPIArguments"]
    end
    
    subgraph Layer5["External Services"]
        AZURE["Azure OpenAI"]
        OPENAI["ChatOpenAI"]
        REDIS_SVC["Azure Redis Cache"]
    end
    
    CLI1 --> RF
    CLI2 --> RTP
    RF --> ENGINE
    RTP --> ENGINE
    
    ENGINE --> PROC
    ENGINE --> SUBSET
    PROC --> CACHE
    
    HYDRA --> ARGS
    ARGS --> ENGINE
    ENGINE --> CACHE
    
    PROC --> AZURE
    PROC --> OPENAI
    CACHE --> REDIS_SVC
```

**Layer 1 - User Interface**: Command-line entry points that parse arguments and initialize the application. Implemented in [src/radfact/cli/run_radfact.py]() and [src/radfact/cli/run_report_to_phrases.py]().

**Layer 2 - Application Logic**: Task-specific business logic for computing RadFact metrics or converting reports to phrases. These modules orchestrate the overall evaluation workflow.

**Layer 3 - Processing Infrastructure**: Core execution engine that handles parallel processing, data sharding, and batch management. The `LLMEngine` class coordinates multiple workers, each processing a `DataSubset`.

**Layer 4 - Configuration & Caching**: Configuration management via Hydra and response caching via LangChain. The `LLMEngineArguments` and `LLMAPIArguments` classes encapsulate processing parameters.

**Layer 5 - External Services**: LLM providers and caching infrastructure. Supports both Azure OpenAI and standard OpenAI-compatible endpoints.

**Sources**: [README.md:1-275](), [src/radfact/llm_utils/engine/engine.py:1-362]()

## Core Component Architecture

The following diagram maps the major classes and their relationships:

```mermaid
graph TB
    subgraph CLI["CLI Layer"]
        run_radfact["run_radfact.py"]
        run_phrases["run_report_to_phrases.py"]
    end
    
    subgraph Engine["LLMEngine (engine.py:50)"]
        engine_init["__init__()"]
        shard["shard_dataset()"]
        run_worker["run_worker()"]
        aggregate["post_run_aggregation()"]
    end
    
    subgraph Processor["Processing Layer"]
        base_proc["BaseProcessor<br/>(base_processor.py)"]
        struct_proc["StructuredProcessor<br/>(structured_processor.py)"]
    end
    
    subgraph Data["Data Management"]
        data_subset["DataSubset<br/>(data_subset.py)"]
        progress["processed_ids: set"]
        skipped["skipped_ids: set"]
    end
    
    subgraph Config["Configuration"]
        endpoint["Endpoint<br/>(endpoint.py)"]
        llm_engine_args["LLMEngineArguments<br/>(arguments.py)"]
        llm_api_args["LLMAPIArguments<br/>(arguments.py)"]
    end
    
    subgraph Cache["Caching"]
        redis_cache["RedisCache<br/>(redis_cache.py)"]
        sqlite_cache["SQLiteCache<br/>(langchain)"]
    end
    
    run_radfact --> engine_init
    run_phrases --> engine_init
    
    engine_init --> llm_engine_args
    engine_init --> llm_api_args
    engine_init --> base_proc
    
    shard --> data_subset
    run_worker --> struct_proc
    run_worker --> data_subset
    
    data_subset --> progress
    data_subset --> skipped
    
    struct_proc --> redis_cache
    struct_proc --> sqlite_cache
    
    llm_api_args --> endpoint
    endpoint --> redis_cache
```

| Component | File Path | Key Responsibilities |
|-----------|-----------|---------------------|
| `LLMEngine` | [src/radfact/llm_utils/engine/engine.py:50-362]() | Orchestrates parallel processing, manages workers, aggregates results |
| `BaseProcessor` | [src/radfact/llm_utils/processor/base_processor.py]() | Abstract interface for LLM query processing |
| `StructuredProcessor` | [src/radfact/llm_utils/processor/structured_processor.py]() | Concrete processor with prompt templates and output parsing |
| `DataSubset` | [src/radfact/llm_utils/engine/data_subset.py]() | Manages a shard of data with progress tracking |
| `Endpoint` | [src/radfact/llm_utils/endpoint.py]() | Encapsulates LLM endpoint configuration and authentication |
| `LLMEngineArguments` | [src/radfact/llm_utils/engine/arguments.py]() | Processing parameters (batch size, output file, etc.) |
| `LLMAPIArguments` | [src/radfact/llm_utils/engine/arguments.py]() | LLM-specific parameters (temperature, max_tokens, etc.) |

**Sources**: [src/radfact/llm_utils/engine/engine.py:1-362](), [README.md:48-130]()

## Data Flow Architecture

The following sequence shows how data flows from user input to final metrics output:

```mermaid
sequenceDiagram
    participant User
    participant CLI as "run_radfact CLI"
    participant Hydra as "Hydra ConfigStore"
    participant Engine as "LLMEngine"
    participant Shard as "DataSubset"
    participant Worker as "run_worker()"
    participant Proc as "StructuredProcessor"
    participant Cache as "Redis/SQLite Cache"
    participant LLM as "Azure OpenAI / ChatOpenAI"
    participant FS as "File System"
    
    User->>CLI: Execute with input CSV/JSON
    CLI->>Hydra: Load configs (radfact.yaml)
    Hydra-->>CLI: DictConfig object
    
    CLI->>Engine: Initialize with cfg + DataFrame
    Engine->>Engine: get_weighted_splits()
    Engine->>Engine: shard_dataset()
    
    par Worker 1
        Engine->>Worker: spawn Process 1
        Worker->>Shard: Load DataSubset 1
        loop Batch Processing
            Worker->>Proc: run(query, query_id)
            Proc->>Cache: Check cache
            alt Cache Hit
                Cache-->>Proc: Return cached response
            else Cache Miss
                Proc->>LLM: Send prompt
                LLM-->>Proc: LLM response
                Proc->>Cache: Store response
            end
            Proc-->>Worker: Parsed output
            Worker->>Shard: Update processed_ids
            Worker->>FS: Write batch_outputs/*.json
        end
        Worker->>FS: Save progress.csv
        Worker->>FS: Save skipped.csv
    and Worker 2
        Engine->>Worker: spawn Process 2
        Note over Worker: Similar processing
    and Worker N
        Engine->>Worker: spawn Process N
        Note over Worker: Similar processing
    end
    
    Engine->>Engine: post_run_aggregation()
    Engine->>FS: Write outputs.json
    Engine-->>CLI: Return aggregated outputs
    CLI-->>User: Display metrics
```

**Key Data Flow Stages**:

1. **Configuration Loading** ([line 67-91](src/radfact/llm_utils/engine/engine.py:67-91)): Hydra loads task-specific config and endpoint definitions
2. **Dataset Sharding** ([line 193-216](src/radfact/llm_utils/engine/engine.py:193-216)): Dataset split proportionally based on endpoint `speed_factor`
3. **Parallel Worker Execution** ([line 262-296](src/radfact/llm_utils/engine/engine.py:262-296)): Each worker processes its assigned `DataSubset`
4. **Cache-Aware Processing**: LLM queries check cache first to avoid redundant API calls
5. **Incremental Persistence**: Results written to `batch_outputs/` after each batch
6. **Progress Tracking**: `processed_ids` and `skipped_ids` tracked per worker
7. **Final Aggregation** ([line 298-334](src/radfact/llm_utils/engine/engine.py:298-334)): All batch outputs merged into single `outputs.json`

**Sources**: [src/radfact/llm_utils/engine/engine.py:262-362](), [README.md:100-130]()

## Parallel Processing Model

RadFact uses a multi-process architecture for parallel execution:

```mermaid
graph TB
    subgraph Main["Main Process"]
        DF["DataFrame<br/>(N rows)"]
        SHARD_LOGIC["get_weighted_splits()<br/>engine.py:162"]
    end
    
    subgraph Sharding["Data Sharding"]
        SHARD1["DataSubset 1<br/>(indices 0-500)"]
        SHARD2["DataSubset 2<br/>(indices 501-800)"]
        SHARD3["DataSubset 3<br/>(indices 801-1000)"]
    end
    
    subgraph Workers["Worker Processes (multiprocessing.Process)"]
        W1["Worker 1<br/>PID: 12345"]
        W2["Worker 2<br/>PID: 12346"]
        W3["Worker 3<br/>PID: 12347"]
    end
    
    subgraph Endpoints["LLM Endpoints"]
        EP1["Azure OpenAI East<br/>speed_factor: 2.0"]
        EP2["Azure OpenAI West<br/>speed_factor: 1.5"]
        EP3["Custom Llama-3<br/>speed_factor: 1.0"]
    end
    
    subgraph Output["Output Files"]
        BATCH1["batch_outputs/<br/>outputs_0_500.json"]
        BATCH2["batch_outputs/<br/>outputs_501_800.json"]
        BATCH3["batch_outputs/<br/>outputs_801_1000.json"]
        PROGRESS["progress.csv<br/>(aggregated)"]
        FINAL["outputs.json<br/>(final)"]
    end
    
    DF --> SHARD_LOGIC
    SHARD_LOGIC -->|"500 rows<br/>(2.0/4.5 * 1000)"| SHARD1
    SHARD_LOGIC -->|"333 rows<br/>(1.5/4.5 * 1000)"| SHARD2
    SHARD_LOGIC -->|"167 rows<br/>(1.0/4.5 * 1000)"| SHARD3
    
    SHARD1 --> W1
    SHARD2 --> W2
    SHARD3 --> W3
    
    W1 --> EP1
    W2 --> EP2
    W3 --> EP3
    
    W1 --> BATCH1
    W2 --> BATCH2
    W3 --> BATCH3
    
    BATCH1 --> FINAL
    BATCH2 --> FINAL
    BATCH3 --> FINAL
    
    W1 --> PROGRESS
    W2 --> PROGRESS
    W3 --> PROGRESS
```

**Parallel Processing Implementation Details**:

- **Process Spawning** ([line 349-358](src/radfact/llm_utils/engine/engine.py:349-358)): Uses `multiprocessing.Process` for true parallelism
- **Data Sharding Algorithm** ([line 162-178](src/radfact/llm_utils/engine/engine.py:162-178)): Proportional assignment based on `speed_factor` with remainder distribution
- **Worker Isolation**: Each worker has its own `DataSubset`, preventing race conditions
- **Shared State**: `multiprocessing.Manager.dict()` used for returning results ([line 103-106](src/radfact/llm_utils/engine/engine.py:103-106))
- **Progress Tracking**: Per-worker CSV files aggregated at end ([line 324-328](src/radfact/llm_utils/engine/engine.py:324-328))
- **Batch Processing** ([line 269-292](src/radfact/llm_utils/engine/engine.py:269-292)): Reduces memory footprint and enables incremental saves

**Sources**: [src/radfact/llm_utils/engine/engine.py:162-362](), [README.md:100-130]()

## Configuration Architecture

RadFact uses Hydra for hierarchical configuration management:

```mermaid
graph TB
    subgraph Hydra["Hydra Framework"]
        CONFIG_DIR["configs/"]
        DEFAULT["default.yaml"]
    end
    
    subgraph Task["Task Configs"]
        RADFACT["radfact.yaml<br/>(entailment verification)"]
        PHRASES["report_to_phrases.yaml<br/>(report conversion)"]
    end
    
    subgraph Endpoints["Endpoint Configs (configs/endpoints/)"]
        AZURE1["azure_chat_openai.yaml<br/>type: AZURE_CHAT_OPENAI"]
        OPENAI1["chat_openai.yaml<br/>type: CHAT_OPENAI"]
    end
    
    subgraph Runtime["Runtime Objects"]
        DICT_CFG["DictConfig<br/>(OmegaConf)"]
        ENGINE_ARGS["LLMEngineArguments<br/>(processing params)"]
        API_ARGS["LLMAPIArguments<br/>(LLM params)"]
        ENDPOINT_OBJ["Endpoint objects<br/>(url, auth, speed_factor)"]
    end
    
    subgraph Auth["Authentication"]
        ENV["Environment Variables<br/>(API_KEY)"]
        KEYVAULT["Azure Key Vault<br/>(key_vault_secret_name)"]
        TOKEN["Azure AD Token<br/>(azure_ad_token_provider)"]
    end
    
    CONFIG_DIR --> DEFAULT
    DEFAULT --> RADFACT
    DEFAULT --> PHRASES
    
    RADFACT --> AZURE1
    RADFACT --> OPENAI1
    PHRASES --> AZURE1
    
    RADFACT --> DICT_CFG
    PHRASES --> DICT_CFG
    
    DICT_CFG --> ENGINE_ARGS
    DICT_CFG --> API_ARGS
    DICT_CFG --> ENDPOINT_OBJ
    
    ENDPOINT_OBJ --> ENV
    ENDPOINT_OBJ --> KEYVAULT
    ENDPOINT_OBJ --> TOKEN
```

**Configuration Hierarchy**:

| Level | Files | Purpose |
|-------|-------|---------|
| Base | [configs/default.yaml]() | Shared defaults for all tasks |
| Task | [configs/radfact.yaml](), [configs/report_to_phrases.yaml]() | Task-specific overrides (which endpoint, output files) |
| Endpoint | [configs/endpoints/*.yaml]() | LLM endpoint definitions (URL, auth, throughput) |

**Key Configuration Classes**:

- `LLMEngineArguments` ([src/radfact/llm_utils/engine/arguments.py]()):
  - `batch_size`: Number of rows processed before saving
  - `start_index` / `end_index`: Dataset slice to process
  - `output_filename`: Final output file name
  
- `LLMAPIArguments` ([src/radfact/llm_utils/engine/arguments.py]()):
  - `temperature`: LLM temperature parameter
  - `max_tokens`: Maximum response length
  - `model_name`: Specific model deployment

- `Endpoint` ([src/radfact/llm_utils/endpoint.py:38]()):
  - `url`: Base URL for API
  - `deployment_name`: Model deployment identifier
  - `speed_factor`: Relative throughput for sharding
  - `num_parallel_processes`: Endpoint-specific parallelism
  - `redis_cache`: Redis cache name for this endpoint

**Sources**: [README.md:48-93](), [src/radfact/llm_utils/engine/arguments.py](), [src/radfact/llm_utils/endpoint.py]()

## File System Organization

The system produces a structured output directory hierarchy:

```
outputs/radfact/
└── run_20240814_075225/          # Run ID with timestamp
    ├── batch_outputs/             # Incremental batch results
    │   ├── outputs_0_100.json
    │   ├── outputs_100_200.json
    │   └── outputs_200_300.json
    ├── progress/                  # Per-worker progress files
    │   ├── subset_0_150.csv       # Worker 1 progress
    │   ├── subset_150_250.csv     # Worker 2 progress
    │   └── subset_250_300.csv     # Worker 3 progress
    ├── skipped/                   # Per-worker skipped IDs
    │   ├── subset_0_150.csv
    │   ├── subset_150_250.csv
    │   └── subset_250_300.csv
    ├── outputs.json               # Final aggregated results
    ├── progress.csv               # Aggregated progress
    └── skipped.csv                # Aggregated skipped IDs
```

**File Generation Logic**:

- **Run ID** ([line 158-160](src/radfact/llm_utils/engine/engine.py:158-160)): Timestamp-based unique identifier
- **Batch Outputs** ([line 245-255](src/radfact/llm_utils/engine/engine.py:245-255)): Written after each batch completes
- **Progress Tracking** ([line 229-233](src/radfact/llm_utils/engine/engine.py:229-233)): Per-worker CSV files with processed IDs
- **Final Aggregation** ([line 298-311](src/radfact/llm_utils/engine/engine.py:298-311)): All batch files merged into `outputs.json`

**Sources**: [README.md:100-130](), [src/radfact/llm_utils/engine/engine.py:38-127]()

## Extension Points

The architecture provides several extension points for customization:

1. **Custom Processors**: Implement `BaseProcessor` interface for new LLM interaction patterns
2. **Endpoint Types**: Add new endpoint types by extending `Endpoint` class and updating configuration schema
3. **Cache Backends**: Switch between Redis, SQLite, or implement custom cache via LangChain interface
4. **Output Formats**: Override `on_batch_end()` and `aggregate_outputs()` for custom output handling
5. **Progress Callbacks**: Implement custom logging by overriding `on_processing_step()` and `on_skip_step()`

For implementation details of each subsystem, refer to the relevant sub-pages listed at the beginning of this document.

**Sources**: [src/radfact/llm_utils/engine/engine.py:50-362](), [src/radfact/llm_utils/processor/base_processor.py]()

---

