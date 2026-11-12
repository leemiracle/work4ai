<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/agent-eval · page 6 Reference · fetched 2026-10-26 -->

# Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sample-config-hf-readme-metadata.yml](sample-config-hf-readme-metadata.yml)
- [sample-config.yml](sample-config.yml)

</details>



This page provides reference documentation for the agent-eval toolkit's configuration files, data schemas, and core structures. It serves as a technical reference for users who need to understand the precise format and structure of configuration files, dataset schemas, and integration points.

For step-by-step examples of creating configurations, see [Configuration Examples](#6.1). For detailed information about dataset schema generation and HuggingFace integration, see [Dataset Schema Reference](#6.2). For understanding the Python package organization, see [Package Structure](#6.3).

## Configuration File Schema

The agent-eval toolkit uses YAML configuration files to define evaluation suites. The configuration schema defines how tasks are organized, executed, and published.

### Suite Configuration Structure

```mermaid
graph TB
    subgraph "YAML Configuration"
        ROOT["Suite Config"]
        META["Metadata"]
        SPLITS["splits[]"]
        SPLIT["Split"]
        TASKS["tasks[]"]
        TASK["Task"]
    end
    
    subgraph "Required Fields"
        NAME["name: string"]
        VERSION["version: string"]
        SPLIT_NAME["name: string"]
        TASK_NAME["name: string"]
        TASK_PATH["path: string"]
        PRIMARY_METRIC["primary_metric: string"]
    end
    
    subgraph "Optional Fields"
        TAGS["tags: string[]"]
        DESCRIPTION["description: string"]
    end
    
    ROOT --> META
    ROOT --> SPLITS
    META --> NAME
    META --> VERSION
    SPLITS --> SPLIT
    SPLIT --> SPLIT_NAME
    SPLIT --> TASKS
    TASKS --> TASK
    TASK --> TASK_NAME
    TASK --> TASK_PATH
    TASK --> PRIMARY_METRIC
    TASK --> TAGS
    TASK --> DESCRIPTION
```

**Sources:** [sample-config.yml:1-21]()

### Configuration Field Definitions

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `name` | string | Yes | Unique identifier for the evaluation suite | `"agent-eval-sample"` |
| `version` | string | Yes | Version identifier for the suite | `"0.1-dev"` |
| `splits` | array | Yes | List of evaluation splits (validation, test, etc.) | See splits schema below |

#### Splits Schema

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `name` | string | Yes | Split identifier | `"validation"`, `"test"` |
| `tasks` | array | Yes | List of tasks in this split | See tasks schema below |

#### Tasks Schema

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `name` | string | Yes | Task identifier | `"first_task"` |
| `path` | string | Yes | Relative path to task implementation | `"tasks/first_task"` |
| `primary_metric` | string | Yes | Primary metric for scoring | `"my_scorer/my_metric"` |
| `tags` | array | No | Categorical tags for the task | `["task1", "nlp"]` |
| `description` | string | No | Human-readable task description | `"Evaluates reasoning"` |

**Sources:** [sample-config.yml:1-21]()

## HuggingFace Integration Schema

Agent-eval publishes evaluation results to HuggingFace Hub using a specific metadata format that defines dataset structure and features.

### HuggingFace README Metadata Structure

```mermaid
graph TB
    subgraph "HF Dataset Metadata"
        HF_ROOT["HuggingFace Metadata"]
        CONFIGS["configs[]"]
        CONFIG["Config Entry"]
        DATA_FILES["data_files[]"]
        FEATURES["features"]
    end
    
    subgraph "Config Fields"
        CONFIG_NAME["config_name: string"]
        SPLIT_DATA["Split Data Files"]
        FEATURE_SCHEMA["Feature Schema"]
    end
    
    subgraph "Data File Structure"
        SPLIT_NAME["split: string"]
        PATH_PATTERN["path: string"]
    end
    
    HF_ROOT --> CONFIGS
    CONFIGS --> CONFIG
    CONFIG --> CONFIG_NAME
    CONFIG --> DATA_FILES
    CONFIG --> FEATURES
    DATA_FILES --> SPLIT_DATA
    SPLIT_DATA --> SPLIT_NAME
    SPLIT_DATA --> PATH_PATTERN
    FEATURES --> FEATURE_SCHEMA
```

**Sources:** [sample-config-hf-readme-metadata.yml:1-12]()

### HuggingFace Metadata Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `config_name` | string | Version identifier matching suite config | `"0.1-dev"` |
| `data_files` | array | File path patterns for each split | See data files schema |
| `features` | object | Dataset schema (generated from `dataset_features.yml`) | Auto-generated |

#### Data Files Schema

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `split` | string | Split name matching configuration | `"validation"`, `"test"` |
| `path` | string | Glob pattern for data files | `"0.1-dev/validation/*.json"` |

**Sources:** [sample-config-hf-readme-metadata.yml:3-8]()

## Configuration to Code Entity Mapping

This diagram shows how YAML configuration elements map to internal Python data structures and processing components.

```mermaid
graph LR
    subgraph "YAML Config Space"
        YAML_SUITE["Suite Config YAML"]
        YAML_SPLIT["splits[]"]
        YAML_TASK["tasks[]"]
        YAML_METRIC["primary_metric"]
    end
    
    subgraph "Python Model Space"
        CONFIG_MODEL["config.py models"]
        TASK_RESULT["TaskResult"]
        EVAL_RESULT["EvalResult"]
        SUMMARY_STATS["SummaryStatistics"]
    end
    
    subgraph "Processing Components"
        SCORE_MODULE["score.py"]
        LOG_PARSER["log.py"]
        SUMMARY_MODULE["summary.py"]
        UPLOAD_MODULE["upload.py"]
    end
    
    YAML_SUITE --> CONFIG_MODEL
    YAML_SPLIT --> TASK_RESULT
    YAML_TASK --> SCORE_MODULE
    YAML_METRIC --> LOG_PARSER
    
    CONFIG_MODEL --> UPLOAD_MODULE
    TASK_RESULT --> SUMMARY_MODULE
    EVAL_RESULT --> UPLOAD_MODULE
    SUMMARY_STATS --> UPLOAD_MODULE
    
    SCORE_MODULE --> TASK_RESULT
    LOG_PARSER --> TASK_RESULT
    SUMMARY_MODULE --> SUMMARY_STATS
```

**Sources:** [sample-config.yml:1-21](), system architecture diagrams

## Data Flow Schema

This diagram illustrates how configuration data flows through the system from YAML files to published HuggingFace datasets.

```mermaid
graph TD
    subgraph "Input Layer"
        SUITE_YAML["suite_config.yml"]
        AGENT_CODE["Agent Implementation"]
    end
    
    subgraph "Processing Layer"
        EVAL_CMD["agenteval eval"]
        SCORE_CMD["agenteval score"] 
        PUBLISH_CMD["agenteval publish"]
    end
    
    subgraph "Data Transformation"
        RAW_LOGS["inspect_ai logs"]
        TASK_RESULTS["TaskResult objects"]
        EVAL_RESULTS["EvalResult object"]
        HF_DATASET["HuggingFace Dataset"]
    end
    
    subgraph "Schema Generation"
        PYDANTIC_MODELS["Pydantic Models"]
        DATASET_FEATURES["dataset_features.yml"]
        HF_METADATA["HF README metadata"]
    end
    
    SUITE_YAML --> EVAL_CMD
    AGENT_CODE --> EVAL_CMD
    EVAL_CMD --> RAW_LOGS
    
    RAW_LOGS --> SCORE_CMD
    SCORE_CMD --> TASK_RESULTS
    TASK_RESULTS --> EVAL_RESULTS
    
    EVAL_RESULTS --> PUBLISH_CMD
    PUBLISH_CMD --> HF_DATASET
    
    PYDANTIC_MODELS --> DATASET_FEATURES
    DATASET_FEATURES --> HF_METADATA
    HF_METADATA --> HF_DATASET
```

**Sources:** [sample-config.yml:1-21](), [sample-config-hf-readme-metadata.yml:1-12](), system architecture diagrams

## File Organization Patterns

The agent-eval toolkit follows consistent patterns for organizing configuration files, task implementations, and output data.

### Standard Directory Structure

```
evaluation-suite/
├── suite_config.yml           # Main configuration file
├── tasks/                     # Task implementation directory
│   ├── task_name/            # Individual task directory
│   │   ├── task.py           # Task implementation
│   │   └── data/             # Task-specific data
├── outputs/                   # Generated outputs
│   ├── logs/                 # Raw evaluation logs
│   ├── results/              # Processed results
│   └── summaries/            # Summary statistics
└── hf_metadata/              # HuggingFace publication files
    ├── README.md             # Dataset README with metadata
    └── dataset_features.yml  # Feature schema
```

### Configuration File Naming

| File Type | Naming Pattern | Example |
|-----------|---------------|---------|
| Suite Config | `{suite-name}-config.yml` | `agent-eval-sample-config.yml` |
| HF Metadata | `{suite-name}-hf-readme-metadata.yml` | `sample-config-hf-readme-metadata.yml` |
| Task Directory | `{task_name}/` | `tasks/first_task/` |
| Output Files | `{version}/{split}/` | `0.1-dev/validation/` |

**Sources:** [sample-config.yml:8,17](), [sample-config-hf-readme-metadata.yml:6,8]()

---

