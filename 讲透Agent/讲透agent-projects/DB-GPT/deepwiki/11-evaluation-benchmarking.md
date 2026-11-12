<!-- source: DeepWiki mcp.deepwiki.com · repo eosphoros-ai/DB-GPT · page 11 Evaluation & Benchmarking · fetched 2026-11-09 -->

# Evaluation & Benchmarking

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/dbgpt-core/src/dbgpt/util/benchmarks/StorageUtil.py](packages/dbgpt-core/src/dbgpt/util/benchmarks/StorageUtil.py)
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/api/schemas.py](packages/dbgpt-serve/src/dbgpt_serve/evaluate/api/schemas.py)
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/__init__.py](packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/__init__.py)
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/benchmark_service.py](packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/benchmark_service.py)
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/ext/__init__.py](packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/ext/__init__.py)
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/ext/excel_file_parse.py](packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/ext/excel_file_parse.py)
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/ext/falcon_file_parse.py](packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/ext/falcon_file_parse.py)
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/file_parse_service.py](packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/file_parse_service.py)
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/models.py](packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/models.py)
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/task/benchmark_agent_task.py](packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/task/benchmark_agent_task.py)
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/user_input_execute_service.py](packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/user_input_execute_service.py)
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/fetchdata/benchmark_data_manager.py](packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/fetchdata/benchmark_data_manager.py)

</details>



The Evaluation & Benchmarking subsystem in DB-GPT provides a robust framework for assessing the performance of Large Language Models (LLMs), retrieval-augmented generation (RAG) systems, and autonomous agents. It encompasses the `BenchmarkService`, benchmark data manager, file parsers for benchmark datasets, agent task benchmarks, and retriever evaluation components.

## System Architecture

The central component is the **`BenchmarkService`**, responsible for orchestrating benchmark task lifecycle management — including data acquisition, multi-round task execution, and results comparison using diverse matching strategies.

### Evaluation Execution Flow & Entity Mapping

```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        "UserRequest"["EvaluateServeRequest"]
        "BenchmarkDatasets"["Falcon/Excel Benchmark Datasets"]
    end

    subgraph "CodeEntitySpace"
        BS["BenchmarkService\n(packages/dbgpt_serve/evaluate/service/benchmark/benchmark_service.py)"]
        BDM["BenchmarkDataManager\n(packages/dbgpt_serve/evaluate/service/fetchdata/benchmark_data_manager.py)"]
        UIES["UserInputExecuteService\n(packages/dbgpt_serve/evaluate/service/benchmark/user_input_execute_service.py)"]
        FPS["FileParseService and extensions\n(ext/falcon_file_parse.py, ext/excel_file_parse.py)"]
        BAT["BenchmarkAgentTask\n(task/benchmark_agent_task.py)"]
        BLT["BenchmarkLLMTask\n(task/benchmark_llm_task.py)"]
    end

    subgraph "StorageSpace"
        SDAO["ServeDao\n(packages/dbgpt_serve/evaluate/service/benchmark/benchmark_service.py)"]
        BDB["BenchmarkResultDao\n(benchmark_result_dao.py)"]
        SQLC["SQLiteConnector\n(packages/dbgpt_ext/datasource/rdbms/conn_sqlite.py)"]
    end

    "UserRequest" --> BS
    BS -- "initialize" --> BDM
    BS -- "dispatch execution" --> UIES
    UIES -- "parse inputs" --> FPS
    UIES -- "execute tasks" --> BAT
    UIES -- "execute tasks" --> BLT
    
    BDM -- "fetch benchmark data" --> "BenchmarkDatasets"
    BDM -- "init DB connector" --> SQLC
    
    BS -- "store metadata & status" --> SDAO
    UIES -- "save results" --> BDB
```

This diagram maps the primary components and their interactions during benchmark execution: from receiving user evaluation requests to producing and storing result reports.

Sources:  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/benchmark_service.py:69-110]()  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/fetchdata/benchmark_data_manager.py:133-181]()  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/user_input_execute_service.py:37-60]()  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/task/benchmark_agent_task.py:91-140]()  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/task/benchmark_llm_task.py:1-27]()  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/file_parse_service.py:25-56]()

### Benchmark Data Lifecycle

```mermaid
graph LR
    subgraph "NaturalLanguageSpace"
        "GitHubRepo"["Falcon Benchmark Repo"]
        "LocalExcel"["Excel Benchmark Files"]
    end

    subgraph "CodeEntitySpace"
        BDM["BenchmarkDataManager\n(packages/dbgpt_serve/evaluate/service/fetchdata/benchmark_data_manager.py)"]
        SU["StorageUtil\n(packages/dbgpt_core/util/benchmarks/StorageUtil.py)"]
        FFPS["FalconFileParseService\n(ext/falcon_file_parse.py)"]
        EFPS["ExcelFileParseService\n(ext/excel_file_parse.py)"]
    end

    subgraph "StorageSpace"
        SQLC["SQLiteConnector\n(packages/dbgpt_ext/datasource/rdbms/conn_sqlite.py)"]
        FStore["File System for Results\n(BENCHMARK_OUTPUT_RESULT_PATH)"]
    end

    "GitHubRepo" --> BDM
    "LocalExcel" --> SU
    SU --> FFPS
    SU --> EFPS
    BDM --> SQLC
    FFPS --> FStore
```

This diagram illustrates the flow of benchmark data from external sources (e.g., GitHub Falcon repo or local Excel files), through parse service selection via `StorageUtil`, to database connector initialization and finally result output storage.

Sources:  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/fetchdata/benchmark_data_manager.py:133-154]()  
- [packages/dbgpt-core/src/dbgpt/util/benchmarks/StorageUtil.py:15-36]()  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/ext/falcon_file_parse.py:183-203]()  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/ext/excel_file_parse.py:22-60]()  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/benchmark_service.py:69-110]()

## Core Components Overview

### BenchmarkService

The `BenchmarkService` acts as the primary interface for benchmark execution. It manages the full lifecycle of benchmark tasks by coordinating with internal services like `RagService`, `PromptService`, and the `UserInputExecuteService`. It creates, persists, and controls benchmark executions while handling concurrency with thread pools.

- Uses `get_file_parse_type` to determine dataset source type for parsing
- Supports generation of benchmark tasks for different scenes and models (LLM or Agent)
- Stores benchmark metadata persistently via `ServeDao`

Implemented in:  
`packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/benchmark_service.py:121-200`

### BenchmarkDataManager

`BenchmarkDataManager` oversees benchmark datasets including fetching from repositories (e.g., Falcon dataset on GitHub), local caching, data transformations, and providing a consistent read interface for downstream consumers.

- Initializes SQLite database connector for managing metadata
- Supports async lifecycle and resource cleanup
- Caches dataset files and manages expiry for freshness

Implemented in:  
`packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/fetchdata/benchmark_data_manager.py:133-199`

### File Parsers

The evaluation system supports multiple input data formats through a polymorphic parsing interface defined by `FileParseService`. Key implementations include:

- **FalconFileParseService**  
  Parses JSONL/JSON formatted benchmark datasets specifically structured for Text-to-SQL tasks using Falcon repo schema. Provides dataset and table DDL parsing with specialized prompt templates.  
  Location: `packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/ext/falcon_file_parse.py`

- **ExcelFileParseService**  
  Supports parsing of benchmark datasets from Excel files in `.xlsx` format, converting rows into structured `AnswerExecuteModel` instances suitable for evaluation and comparison.  
  Location: `packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/ext/excel_file_parse.py`

The abstract base defines methods for reading inputs, LLM outputs, and writing benchmark comparison results.

Sources:  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/file_parse_service.py:25-56]()  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/ext/falcon_file_parse.py:183-203]()  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/ext/excel_file_parse.py:22-85]()

### Evaluation Tasks

- **BenchmarkLLMTask**  
  Designed for benchmarking raw LLM model performance by directly invoking LLM prompts and collecting results.  
  Location: `packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/task/benchmark_llm_task.py`

- **BenchmarkAgentTask**  
  Evaluates agentic behavior by sending requests to remote agent APIs with configurable URL, headers, and parsing strategies. It handles retries, parses JSON responses using JSON path or direct methods, and maps results into benchmark format.  
  Location: `packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/task/benchmark_agent_task.py:91-140`

- **AgentApiConfig**  
  Defines agent API endpoint, HTTP method, headers, parsing strategy, retry configs, and response mapping for flexible remote agent invocation.  
  Location: `packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/models.py:188-228`

Sources:  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/benchmark_service.py:22-28]()  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/task/benchmark_agent_task.py:91-140]()  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/models.py:188-228]()

### Evaluation Metrics & Comparison

The evaluation subsystem supports multiple result comparison strategies customized per benchmark task:

| Strategy       | Description                                                  | Implemented As                      |
|----------------|--------------------------------------------------------------|-----------------------------------|
| EXACT_MATCH    | Strict equality comparison of output or execution results    | `DataCompareStrategyConfig`        |
| CONTAIN_MATCH  | Checks if expected results are contained within outputs      | `DataCompareStrategyConfig`        |
| JSON_PATH      | Extracts specific agent JSON fields via JSON path expressions| `ResponseParseStrategy` enumeration|

Comparison outcomes are classified as `RIGHT`, `WRONG`, `FAILED`, or `EXCEPTION`.

Sources:  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/benchmark_service.py:69-110]()  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/models.py:22-61]()  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/models.py:181-187]()  

### Storage Utilities

- **StorageUtil** detects the appropriate file parser type by inspecting file path prefixes (`github.com/eosphoros-ai/Falcon` for GitHub Falcon repo or default to Excel).  
- **ServeDao** persists benchmark task metadata and evaluation states.
- Benchmark output results are saved under a configured root directory in a confined, safe path naming scheme to secure result file integrity.  
- Results are stored as structured JSON-like `AnswerExecuteModel` objects and optionally exported as Excel.

Sources:  
- [packages/dbgpt-core/src/dbgpt/util/benchmarks/StorageUtil.py:15-36]()  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/benchmark_service.py:69-110]()  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/benchmark_service.py:130-168]()  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/models.py:64-100]()

---

## Child Pages

This page provides a high-level overview of the Evaluation & Benchmarking subsystem. For detailed technical documentation and user guides refer to:

- [LLM & RAG Benchmarks](#11.1) — In-depth coverage of LLM inference benchmarks, RAG retriever evaluation metrics, agent task benchmarking, dataset parsing mechanisms, and how to run and interpret benchmark results.

- [Fine-Tuning & Training (DB-GPT-Hub)](#11.2) — Comprehensive guide on fine-tuning Text2SQL models using the Spider dataset, integration of parameter-efficient fine-tuning methods (LoRA/PEFT), and usage of the external DB-GPT-Hub repository focused on training pipelines.

---

This modular design supports extensibility in evaluation scenarios, covering multiple model types, data formats, and evaluation goals within a unified framework.

Sources:  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/benchmark_service.py]()  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/fetchdata/benchmark_data_manager.py]()  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/user_input_execute_service.py]()  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/file_parse_service.py]()  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/ext/falcon_file_parse.py]()  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/ext/excel_file_parse.py]()  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/task/benchmark_agent_task.py]()  
- [packages/dbgpt-serve/src/dbgpt_serve/evaluate/service/benchmark/models.py]()  
- [packages/dbgpt-core/src/dbgpt/util/benchmarks/StorageUtil.py]()

---

