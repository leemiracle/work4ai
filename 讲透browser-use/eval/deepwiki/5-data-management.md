<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/eval · page 5 Data Management · fetched 2026-10-30 -->

# Data Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [data/WebVoyagerImpossibleTasks.json](data/WebVoyagerImpossibleTasks.json)
- [data/WebVoyager_data.jsonl](data/WebVoyager_data.jsonl)
- [data/reference_answer.json](data/reference_answer.json)

</details>



This document provides an overview of how task datasets, reference answers, and evaluation results are structured, stored, and processed throughout the browser-use evaluation pipeline. It covers the data formats used for WebVoyager tasks, the filtering mechanisms for impossible tasks, and the organization of results generated during evaluation runs.

For information about the core execution engine that processes this data, see [Core Execution Engine](#2). For details about the evaluation system that consumes task data and generates results, see [Evaluation System](#3). For analysis tools that process the stored results, see [Result Analysis and Scoring](#4).

## Data Sources and Input Formats

The evaluation system operates on structured datasets that define web automation tasks and validation criteria. The primary data sources include task definitions, exclusion lists, and reference answers that guide the evaluation process.

```mermaid
graph TB
    subgraph "Input Data Sources"
        WVD["WebVoyager_data.jsonl<br/>812 task definitions"]
        WIT["WebVoyagerImpossibleTasks.json<br/>54 excluded task IDs"]
        TTJ["tasks_test.jsonl<br/>Test dataset subset"]
        REF["reference_answer.json<br/>Expected answers"]
    end
    
    subgraph "Data Processing"
        LOADER["Task Loader<br/>run_browser_use.py"]
        FILTER["Task Filter<br/>Impossible task exclusion"]
        VALIDATOR["Answer Validator<br/>auto_eval_browser_use.py"]
    end
    
    subgraph "Runtime Data"
        ACTIVE["Active Task Queue<br/>Filtered task list"]
        ANSWERS["Reference Answers<br/>Validation criteria"]
    end
    
    WVD --> LOADER
    WIT --> FILTER
    TTJ --> LOADER
    REF --> VALIDATOR
    
    LOADER --> FILTER
    FILTER --> ACTIVE
    REF --> ANSWERS
    
    ACTIVE --> VALIDATOR
    ANSWERS --> VALIDATOR
```

**Sources:** [data/WebVoyager_data.jsonl:1-812](), [data/WebVoyagerImpossibleTasks.json:1-57]()

## Task Data Structure

Each task in the WebVoyager dataset follows a standardized JSON format that defines the target website, task description, and unique identifier. The task structure maps directly to the execution parameters used by the browser automation system.

### WebVoyager Task Schema

```mermaid
graph LR
    subgraph "Task Record Format"
        RECORD["Task Record"]
        WEB_NAME["web_name<br/>Site category"]
        ID["id<br/>Unique identifier"]
        QUES["ques<br/>Task description"]
        WEB_URL["web<br/>Target URL"]
    end
    
    subgraph "Code Mapping"
        TASK_ID["task_id variable"]
        TASK_DESC["task_description"]
        START_URL["starting_url"]
        SITE_CAT["website_category"]
    end
    
    WEB_NAME --> SITE_CAT
    ID --> TASK_ID
    QUES --> TASK_DESC
    WEB_URL --> START_URL
    
    RECORD --> WEB_NAME
    RECORD --> ID
    RECORD --> QUES
    RECORD --> WEB_URL
```

Example task structure from the dataset:

| Field | Description | Example Value |
|-------|-------------|---------------|
| `web_name` | Website category | "Allrecipes" |
| `id` | Unique task identifier | "Allrecipes--0" |
| `ques` | Natural language task description | "Provide a recipe for vegetarian lasagna with more than 100 reviews and a rating of at least 4.5 stars suitable for 6 people." |
| `web` | Target website URL | "https://www.allrecipes.com/" |

**Sources:** [data/WebVoyager_data.jsonl:1-10]()

### Task Filtering and Exclusion

The system maintains a separate file for tasks that are deemed impossible or problematic for automated execution. This filtering prevents wasted computation resources and improves evaluation accuracy.

```mermaid
graph TB
    subgraph "Task Filtering Process"
        ALL_TASKS["All WebVoyager Tasks<br/>812 total tasks"]
        IMPOSSIBLE["WebVoyagerImpossibleTasks.json<br/>54 excluded task IDs"]
        FILTER_LOGIC["Filtering Logic<br/>ID-based exclusion"]
        EXECUTABLE["Executable Tasks<br/>758 valid tasks"]
    end
    
    subgraph "Exclusion Categories"
        ALLRECIPES["Allrecipes: 7 tasks<br/>Complex recipe searches"]
        AMAZON["Amazon: 3 tasks<br/>Account-dependent features"]
        APPLE["Apple: 10 tasks<br/>Product availability issues"]
        BBC["BBC News: 8 tasks<br/>Dynamic content problems"]
        BOOKING["Booking: 4 tasks<br/>Real-time availability"]
        OTHER["Other categories<br/>22 additional tasks"]
    end
    
    ALL_TASKS --> FILTER_LOGIC
    IMPOSSIBLE --> FILTER_LOGIC
    FILTER_LOGIC --> EXECUTABLE
    
    IMPOSSIBLE --> ALLRECIPES
    IMPOSSIBLE --> AMAZON
    IMPOSSIBLE --> APPLE
    IMPOSSIBLE --> BBC
    IMPOSSIBLE --> BOOKING
    IMPOSSIBLE --> OTHER
```

**Sources:** [data/WebVoyagerImpossibleTasks.json:1-57]()

## Data Flow Pipeline

The data management system orchestrates the flow of task definitions from static files through processing stages to final result storage. This pipeline ensures consistent data handling and maintains traceability throughout the evaluation process.

```mermaid
flowchart TD
    subgraph "Data Ingestion"
        JSONL_LOAD["JSONL Task Loading<br/>Line-by-line parsing"]
        JSON_LOAD["JSON Filter Loading<br/>Exclusion list parsing"]
        MERGE["Task Merging<br/>Combine data sources"]
    end
    
    subgraph "Data Processing"
        VALIDATE["Task Validation<br/>Schema checking"]
        FILTER_APPLY["Filter Application<br/>Remove impossible tasks"]
        QUEUE_BUILD["Queue Building<br/>Execution order"]
    end
    
    subgraph "Runtime Execution"
        TASK_EXEC["Task Execution<br/>run_browser_use.py"]
        STATE_TRACK["State Tracking<br/>Progress monitoring"]
        RESULT_GEN["Result Generation<br/>Output formatting"]
    end
    
    subgraph "Data Persistence"
        RESULT_STORE["Result Storage<br/>results/ directory"]
        META_STORE["Metadata Storage<br/>experiment_results.json"]
        HISTORY_STORE["History Storage<br/>Interaction logs"]
    end
    
    JSONL_LOAD --> MERGE
    JSON_LOAD --> MERGE
    MERGE --> VALIDATE
    VALIDATE --> FILTER_APPLY
    FILTER_APPLY --> QUEUE_BUILD
    
    QUEUE_BUILD --> TASK_EXEC
    TASK_EXEC --> STATE_TRACK
    STATE_TRACK --> RESULT_GEN
    
    RESULT_GEN --> RESULT_STORE
    RESULT_GEN --> META_STORE
    RESULT_GEN --> HISTORY_STORE
```

**Sources:** [data/WebVoyager_data.jsonl:1-812](), [data/WebVoyagerImpossibleTasks.json:1-57]()

## Data Transformation and Validation

The system transforms raw task data into structured formats suitable for browser automation and evaluation. This includes parsing natural language descriptions into executable parameters and maintaining data integrity throughout the process.

### Task ID Format Analysis

The task identification system uses a hierarchical naming convention that encodes both the target website and the task sequence number:

```mermaid
graph LR
    subgraph "Task ID Structure"
        FULL_ID["Task ID Format"]
        WEBSITE["Website Category<br/>e.g., 'Allrecipes'"]
        SEPARATOR["Separator<br/>'--'"]
        NUMBER["Task Number<br/>e.g., '0'"]
    end
    
    subgraph "ID Components"
        WEB_CAT["web_name mapping"]
        TASK_SEQ["Sequential numbering"]
        UNIQUE_KEY["Unique identifier"]
    end
    
    FULL_ID --> WEBSITE
    FULL_ID --> SEPARATOR  
    FULL_ID --> NUMBER
    
    WEBSITE --> WEB_CAT
    NUMBER --> TASK_SEQ
    FULL_ID --> UNIQUE_KEY
```

Common website categories and their task distributions:

| Website Category | Task Count Range | Example IDs |
|------------------|------------------|-------------|
| Allrecipes | 0-44 (45 tasks) | "Allrecipes--0", "Allrecipes--44" |
| Amazon | 0-40 (41 tasks) | "Amazon--0", "Amazon--40" |
| Apple | 0-42 (43 tasks) | "Apple--0", "Apple--42" |
| ArXiv | 0-42 (43 tasks) | "ArXiv--0", "ArXiv--42" |
| BBC News | 0-41 (42 tasks) | "BBC News--0", "BBC News--41" |

**Sources:** [data/WebVoyager_data.jsonl:1-100]()

## Result Data Organization

The evaluation system generates structured output data that maintains relationships between input tasks, execution traces, and evaluation outcomes. This organization supports both automated analysis and manual review of evaluation results.

```mermaid
graph TB
    subgraph "Result Directory Structure"
        RESULTS_ROOT["results/<br/>Root directory"]
        EXP_DIR["results/{experiment_id}/<br/>Experiment-specific folder"]
        TASK_DIR["results/{experiment_id}/{task_id}/<br/>Task-specific results"]
        
        TASK_RESULT["task_result.json<br/>Execution outcome"]
        HISTORY["history/<br/>Interaction trace"]
        SCREENSHOTS["screenshots/<br/>Visual evidence"]
        LOGS["logs/<br/>Debug information"]
    end
    
    subgraph "Result File Contents"
        EXEC_STATUS["Execution Status<br/>Success/Failure"]
        EVAL_RESULT["Evaluation Result<br/>GPT-4o assessment"]
        TIMESTAMPS["Timing Data<br/>Duration metrics"]
        ERROR_INFO["Error Information<br/>Exception details"]
    end
    
    RESULTS_ROOT --> EXP_DIR
    EXP_DIR --> TASK_DIR
    TASK_DIR --> TASK_RESULT
    TASK_DIR --> HISTORY
    TASK_DIR --> SCREENSHOTS
    TASK_DIR --> LOGS
    
    TASK_RESULT --> EXEC_STATUS
    TASK_RESULT --> EVAL_RESULT
    TASK_RESULT --> TIMESTAMPS
    TASK_RESULT --> ERROR_INFO
```

The result organization enables efficient retrieval of evaluation data for aggregate analysis and supports the scoring calculations performed by downstream analysis tools.

**Sources:** [data/WebVoyager_data.jsonl:1-812](), [data/WebVoyagerImpossibleTasks.json:1-57]()

---

