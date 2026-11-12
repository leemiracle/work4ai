<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/RadFact · page 1 Home · fetched 2026-10-26 -->

# Home

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [pyproject.toml](pyproject.toml)

</details>



## Purpose and Scope

This wiki documents RadFact, an LLM-based evaluation framework for AI-generated radiology reports. RadFact provides a suite of six metrics to evaluate both text-only and grounded (bounding-box annotated) radiology reports against ground-truth references using large language model entailment verification.

For installation and setup instructions, see [Getting Started](#2). For detailed architectural information, see [Architecture](#5). For usage instructions, see [User Guide](#4).

**Sources**: [README.md:1-6]()

## What is RadFact?

RadFact is an automated evaluation metric that measures the quality of AI-generated radiology reports by comparing them to ground-truth references. Unlike traditional lexical metrics (BLEU, ROUGE), RadFact leverages the logical reasoning capabilities of large language models to determine semantic entailment between reports.

### Problem Statement

Evaluating generated medical reports requires understanding whether findings are:
- **Factually correct** (no hallucinations)
- **Complete** (no omissions)  
- **Properly grounded** (bounding boxes correctly localize findings)

Traditional metrics fail at this because they measure surface-level text similarity rather than semantic correctness.

### RadFact Metrics

RadFact provides six metrics organized into three categories:

| Category | Precision Metric | Recall Metric | Evaluates |
|----------|------------------|---------------|-----------|
| **Logical** | Fraction of generated sentences entailed by ground-truth | Fraction of ground-truth sentences entailed by generation | Text-only correctness and completeness |
| **Grounding** | Fraction of correctly-generated findings also correctly grounded | Fraction of correctly-captured findings also correctly grounded | Grounding quality for correct findings |
| **Spatial** | Fraction of all grounded generations both logically and spatially entailed | Fraction of all grounded ground-truths both logically and spatially entailed | Overall grounding performance |

Precision metrics use ground-truth as reference; recall metrics use generation as reference. This bidirectional evaluation captures both hallucinations (low precision) and omissions (low recall).

**Sources**: [README.md:190-222]()

## System Architecture Overview

RadFact is organized into four major layers: user interface, core evaluation logic, LLM processing infrastructure, and external services.

### High-Level Component Structure

```mermaid
graph TB
    subgraph CLI["Command-Line Interface Layer"]
        RF_CLI["run_radfact<br/>src/radfact/cli/run_radfact.py"]
        RTP_CLI["run_report_to_phrases<br/>src/radfact/cli/run_report_to_phrases.py"]
    end
    
    subgraph Core["RadFact Core Logic"]
        RADFACT["RadFact Metrics Computer<br/>src/radfact/metric/radfact.py"]
        NLI["NLI Entailment Verifier<br/>src/radfact/llm_utils/nli/"]
        RTP["Report-to-Phrases Converter<br/>src/radfact/llm_utils/report_to_phrases/"]
    end
    
    subgraph LLM["LLM Processing Infrastructure"]
        ENGINE["LLMEngine<br/>src/radfact/llm_utils/engine/engine.py"]
        PROC["StructuredProcessor<br/>src/radfact/llm_utils/processor/structured_processor.py"]
        CACHE["RedisCache<br/>src/radfact/llm_utils/engine/redis_cache.py"]
        ENDPOINT["Endpoint<br/>src/radfact/llm_utils/endpoint.py"]
    end
    
    subgraph Config["Configuration System"]
        HYDRA["Hydra Config Manager<br/>configs/"]
        RADFACT_CFG["radfact.yaml"]
        RTP_CFG["report_to_phrases.yaml"]
        EP_CFG["endpoints/*.yaml"]
    end
    
    subgraph External["External Services"]
        AZURE_OPENAI["Azure OpenAI"]
        OPENAI["OpenAI API"]
        REDIS_SVC["Azure Redis Cache"]
    end
    
    RF_CLI --> RADFACT
    RTP_CLI --> RTP
    RADFACT --> NLI
    RADFACT --> ENGINE
    RTP --> ENGINE
    NLI --> ENGINE
    
    ENGINE --> PROC
    ENGINE --> CACHE
    ENGINE --> ENDPOINT
    
    PROC --> ENDPOINT
    CACHE --> REDIS_SVC
    ENDPOINT --> AZURE_OPENAI
    ENDPOINT --> OPENAI
    
    HYDRA --> RADFACT_CFG
    HYDRA --> RTP_CFG
    HYDRA --> EP_CFG
    
    RADFACT_CFG --> ENGINE
    RTP_CFG --> ENGINE
    EP_CFG --> ENDPOINT
```

**Description**: This diagram shows how RadFact's major components relate to actual code files. The CLI layer provides two entry points (`run_radfact` and `run_report_to_phrases`) that invoke the core evaluation logic. The `LLMEngine` class orchestrates parallel LLM queries across multiple endpoints, using `StructuredProcessor` for prompt management and `RedisCache` for response caching. Configuration is managed via Hydra with task-specific YAML files.

**Sources**: [README.md:1-100](), [src/radfact/llm_utils/engine/engine.py](), [src/radfact/llm_utils/processor/structured_processor.py](), [src/radfact/llm_utils/engine/redis_cache.py](), [pyproject.toml:86-88]()

### Evaluation Pipeline Data Flow

```mermaid
graph LR
    subgraph Input["Input Data"]
        CSV["Narrative Reports CSV<br/>columns: example_id,<br/>prediction, target"]
        JSON["Grounded Reports JSON<br/>with phrases + bboxes"]
    end
    
    subgraph Stage1["Stage 1: Report Processing"]
        RTP_TASK["Report-to-Phrases Task<br/>llm_utils/report_to_phrases/<br/>report_to_phrases.py"]
        PHRASES["Phrase Lists<br/>List[str] per report"]
    end
    
    subgraph Stage2["Stage 2: Entailment Verification"]
        NLI_TASK["Bidirectional NLI Task<br/>llm_utils/nli/nli.py"]
        PREC_DIR["Precision Direction<br/>reference=ground_truth"]
        REC_DIR["Recall Direction<br/>reference=generation"]
    end
    
    subgraph Stage3["Stage 3: Metrics Computation"]
        COMPUTE["Metric Computer<br/>metric/radfact.py:<br/>compute_radfact_metrics"]
        LOGICAL["logical_precision<br/>logical_recall"]
        GROUNDING["grounding_precision<br/>grounding_recall"]
        SPATIAL["spatial_precision<br/>spatial_recall"]
        BOOTSTRAP["Bootstrap CI<br/>metric/bootstrap.py"]
    end
    
    subgraph Output["Output Files"]
        OUTPUTS["outputs.json<br/>Final aggregated metrics"]
        BATCH["batch_outputs/<br/>Incremental results"]
        PROGRESS["progress.csv<br/>Completed example IDs"]
    end
    
    CSV -->|is_narrative_text=True| RTP_TASK
    JSON --> PHRASES
    RTP_TASK --> PHRASES
    
    PHRASES --> NLI_TASK
    NLI_TASK --> PREC_DIR
    NLI_TASK --> REC_DIR
    
    PREC_DIR --> COMPUTE
    REC_DIR --> COMPUTE
    
    COMPUTE --> LOGICAL
    COMPUTE --> GROUNDING
    COMPUTE --> SPATIAL
    
    LOGICAL --> BOOTSTRAP
    GROUNDING --> BOOTSTRAP
    SPATIAL --> BOOTSTRAP
    
    BOOTSTRAP --> OUTPUTS
    COMPUTE --> BATCH
    COMPUTE --> PROGRESS
```

**Description**: This diagram illustrates the three-stage evaluation pipeline with exact code file locations. Stage 1 converts narrative reports to phrase lists using `report_to_phrases.py`. Stage 2 performs bidirectional entailment verification via `nli.py`, checking both precision (using ground-truth as reference) and recall (using generation as reference). Stage 3 computes the six metrics in `radfact.py` and optionally generates bootstrap confidence intervals. Results are written incrementally to `batch_outputs/` and aggregated into `outputs.json`.

**Sources**: [README.md:131-189](), [README.md:190-222](), [src/radfact/metric/radfact.py](), [src/radfact/llm_utils/nli/nli.py](), [src/radfact/llm_utils/report_to_phrases/report_to_phrases.py]()

## Key Components

### CLI Entry Points

RadFact provides two command-line tools defined in [pyproject.toml:86-88]():

- **`run_radfact`**: Main evaluation command that computes all six RadFact metrics
  - Implementation: [src/radfact/cli/run_radfact.py]()
  - Accepts CSV (narrative reports) or JSON (grounded reports)
  - Supports optional bootstrapping for confidence intervals
  
- **`run_report_to_phrases`**: Standalone report-to-phrases conversion
  - Implementation: [src/radfact/cli/run_report_to_phrases.py]()
  - Useful for pre-processing narrative reports offline

**Sources**: [pyproject.toml:86-88](), [README.md:131-189]()

### Core Evaluation Logic

The `radfact.metric` module implements metric computation:

- **`RadFact` class** [src/radfact/metric/radfact.py](): Main orchestrator that coordinates report-to-phrases conversion and entailment verification
- **`compute_radfact_metrics()` function**: Computes the six metrics from entailment results
- **`bootstrap.py`**: Implements bootstrap resampling for confidence intervals

**Sources**: [src/radfact/metric/radfact.py]()

### LLM Processing Infrastructure

The `radfact.llm_utils` package provides the LLM processing infrastructure:

#### LLMEngine: Parallel Processing Orchestrator

The `LLMEngine` class [src/radfact/llm_utils/engine/engine.py]() manages parallel processing across multiple LLM endpoints:

```mermaid
graph TD
    subgraph LLMEngine["LLMEngine Class"]
        INIT["__init__<br/>Load endpoints from config"]
        SHARD["_shard_dataset<br/>Split data by speed_factor"]
        PROCESS["process_queries<br/>Spawn worker processes"]
        AGGREGATE["_aggregate_results<br/>Combine worker outputs"]
    end
    
    subgraph Workers["Worker Processes"]
        W1["Worker 1<br/>multiprocessing.Process"]
        W2["Worker 2<br/>multiprocessing.Process"]
        WN["Worker N<br/>multiprocessing.Process"]
    end
    
    subgraph Components["Supporting Components"]
        ARGS["LLMEngineArguments<br/>engine/arguments.py"]
        PROC["StructuredProcessor<br/>processor/structured_processor.py"]
        CACHE["RedisCache or SQLiteCache<br/>engine/redis_cache.py<br/>engine/sqlite_cache.py"]
    end
    
    INIT --> ARGS
    INIT --> SHARD
    SHARD --> PROCESS
    
    PROCESS --> W1
    PROCESS --> W2
    PROCESS --> WN
    
    W1 --> PROC
    W2 --> PROC
    WN --> PROC
    
    PROC --> CACHE
    
    W1 --> AGGREGATE
    W2 --> AGGREGATE
    WN --> AGGREGATE
```

**Description**: The `LLMEngine` shards the input dataset across available endpoints based on their `speed_factor` configuration parameter. Each worker process runs independently, using a `StructuredProcessor` instance to query its assigned endpoint. The cache is shared across workers to avoid redundant API calls. Results are incrementally saved and aggregated at completion.

**Sources**: [src/radfact/llm_utils/engine/engine.py](), [src/radfact/llm_utils/engine/arguments.py]()

#### StructuredProcessor: Prompt and Response Handler

The `StructuredProcessor` class [src/radfact/llm_utils/processor/structured_processor.py]() handles:
- **Prompt formatting**: Combines system message, few-shot examples, and query
- **LLM invocation**: Calls LangChain chat models
- **Response parsing**: Extracts structured outputs from LLM responses
- **Retry logic**: Handles transient failures

**Sources**: [src/radfact/llm_utils/processor/structured_processor.py]()

#### Caching System

Two cache implementations are provided:
- **`RedisCache`** [src/radfact/llm_utils/engine/redis_cache.py](): Distributed cache using Azure Redis Cache, suitable for production
- **`SQLiteCache`** [src/radfact/llm_utils/engine/sqlite_cache.py](): Local file-based cache, suitable for development

Both implement endpoint URL normalization to maximize cache hits across different Azure regions.

**Sources**: [src/radfact/llm_utils/engine/redis_cache.py](), [src/radfact/llm_utils/engine/sqlite_cache.py]()

### Configuration System

RadFact uses Hydra for hierarchical configuration management [configs/]():

```mermaid
graph TB
    subgraph Hydra["Hydra Configuration Hierarchy"]
        DEFAULT["default.yaml<br/>Base configuration"]
        TASK_RADFACT["radfact.yaml<br/>RadFact evaluation task"]
        TASK_RTP["report_to_phrases.yaml<br/>Report-to-phrases task"]
    end
    
    subgraph Endpoints["Endpoint Configurations"]
        AZURE["azure_chat_openai.yaml<br/>GPT-4 on Azure OpenAI"]
        OPENAI["chat_openai.yaml<br/>Custom models (e.g., Llama-3)"]
    end
    
    subgraph Auth["Authentication Methods"]
        ENV["Environment Variable<br/>API_KEY"]
        KV["Azure Key Vault<br/>keyvault_secret_name"]
        TOKEN["Azure AD Token Provider<br/>azure_ad_token_provider"]
    end
    
    subgraph Runtime["Runtime Override"]
        CLI_ARGS["Command-line Arguments<br/>--radfact_config_name<br/>--phrases_config_name"]
    end
    
    DEFAULT --> TASK_RADFACT
    DEFAULT --> TASK_RTP
    
    TASK_RADFACT --> AZURE
    TASK_RADFACT --> OPENAI
    TASK_RTP --> AZURE
    TASK_RTP --> OPENAI
    
    AZURE --> ENV
    AZURE --> KV
    AZURE --> TOKEN
    OPENAI --> ENV
    
    CLI_ARGS --> TASK_RADFACT
    CLI_ARGS --> TASK_RTP
```

**Description**: Configuration files are organized hierarchically. Task-specific configs (`radfact.yaml`, `report_to_phrases.yaml`) inherit from `default.yaml` and specify which endpoint configurations to use. Endpoint configs define the LLM URL, deployment name, and authentication method. Users can override any configuration via command-line arguments.

**Sources**: [configs/default.yaml](), [configs/radfact.yaml](), [configs/report_to_phrases.yaml](), [configs/endpoints/](), [README.md:48-93]()

## Execution Flow

The typical execution flow for evaluating a set of reports:

1. **User invokes CLI**: `run_radfact --input_path data.csv --is_narrative_text`
2. **Hydra loads configuration**: Reads `configs/radfact.yaml` and endpoint configs
3. **RadFact initializes**: Creates `RadFact` instance with LLM endpoints
4. **Stage 1 (if narrative)**: Converts reports to phrases using `report_to_phrases` task
5. **Stage 2**: Performs bidirectional entailment verification using `nli` task
   - Precision direction: ground-truth as reference
   - Recall direction: generation as reference
6. **Stage 3**: Computes six metrics from entailment results
7. **Bootstrap (optional)**: Generates confidence intervals via resampling
8. **Output**: Writes `outputs.json` with metrics and CI

Throughout execution, the `LLMEngine`:
- Shards data across endpoints based on `speed_factor`
- Spawns parallel workers (one per endpoint)
- Checks cache before making LLM API calls
- Writes incremental results to `batch_outputs/` and `progress.csv`
- Aggregates worker outputs into final `outputs.json`

**Sources**: [README.md:131-189](), [src/radfact/llm_utils/engine/engine.py]()

## External Dependencies

RadFact integrates with several external services and libraries:

### Azure Services
- **Azure OpenAI**: LLM endpoints for GPT-4 models
- **Azure Redis Cache**: Distributed caching for LLM responses
- **Azure Key Vault**: Secure credential storage
- **Azure ML**: Optional experiment tracking via MLflow

### Key Python Libraries
- **LangChain** (0.2.17): LLM orchestration and chat model abstractions
- **Hydra** (1.3.2): Hierarchical configuration management
- **Pandas/NumPy**: Data manipulation and metrics computation
- **Redis**: Cache client library

**Sources**: [pyproject.toml:41-60](), [README.md:48-93]()

## Output Structure

RadFact produces a structured output directory for each run:

```
outputs/radfact/run_YYYYMMDD_HHMMSS/
├── batch_outputs/           # Incremental results per batch
│   ├── outputs_0_100.json
│   ├── outputs_100_200.json
│   └── ...
├── progress/                # Progress tracking per worker
│   ├── subset_0_500.csv
│   └── ...
├── skipped/                 # Failed queries per worker
│   ├── subset_0_500.csv
│   └── ...
├── outputs.json            # Final aggregated metrics
├── progress.csv            # Aggregated progress
└── skipped.csv             # Aggregated failures
```

The `outputs.json` file contains:
- Six RadFact metrics (with optional bootstrap confidence intervals)
- Per-example entailment results
- `num_llm_failures`: Count of queries that failed

**Sources**: [README.md:100-130]()

## Next Steps

- **To install RadFact**: See [Installation](#2.1)
- **To run your first evaluation**: See [Quick Start](#2.2)
- **To configure LLM endpoints**: See [Configuration Setup](#2.3)
- **To understand the metrics**: See [RadFact Metrics](#3.1)
- **To learn about the architecture**: See [Architecture](#5)

**Sources**: [README.md:1-274]()

---

