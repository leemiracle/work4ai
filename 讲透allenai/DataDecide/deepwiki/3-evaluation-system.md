<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/DataDecide · page 3 Evaluation System · fetched 2026-10-26 -->

# Evaluation System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [requirements.txt](requirements.txt)
- [results/readme.md](results/readme.md)
- [single_scale/process_s3_to_csv.py](single_scale/process_s3_to_csv.py)
- [single_scale/readme.md](single_scale/readme.md)
- [single_scale/requirements.txt](single_scale/requirements.txt)
- [viz/pred_error.ipynb](viz/pred_error.ipynb)

</details>



The Evaluation System is responsible for ingesting, processing, and organizing evaluation results from the 30k+ model checkpoints trained across 25 data corpora. It fetches raw predictions from S3 storage, enriches them with training statistics from WandB, computes evaluation metrics, and produces cleaned datasets for downstream analysis.

For information about scaling law analysis using these processed results, see [Scaling Laws Analysis](#4). For details on how results are uploaded to HuggingFace, see [Release and Distribution](#6).

## Overview

The evaluation pipeline transforms raw model predictions into structured, analysis-ready datasets through three primary stages:

1. **Data Ingestion**: Fetch predictions from S3 and training statistics from WandB
2. **Metric Computation**: Calculate task-level performance metrics from predictions
3. **Data Cleaning**: Normalize and validate the processed results

The system processes evaluation data for RC (reading comprehension) tasks across multiple checkpoints, model sizes, and data recipes, producing CSV files that serve as the foundation for all downstream analysis.

```mermaid
graph TB
    subgraph "External Sources"
        S3["S3 Storage<br/>predictions.jsonl<br/>per task/checkpoint"]
        WANDB["WandB API<br/>Training metrics<br/>Loss curves"]
    end
    
    subgraph "Processing Scripts"
        PROCESS["process_s3_to_csv.py<br/>--s3 s3://bucket/prefix<br/>--csv_name results.csv"]
        MAIN["main.py<br/>Single-scale predictions<br/>Per-task analysis"]
        METRICS["util_metrics.py<br/>compute_metrics_from_file<br/>METRICS_RC<br/>METRICS_GENERATE"]
    end
    
    subgraph "Data Transformation"
        CLEAN_NB["data_exploration_and_cleaning.ipynb<br/>DIRTY_OUT flag<br/>Parameter validation"]
        PARSE["Path Parsing<br/>parse_train_name<br/>Extract: group, model, chinchilla, task, step, seed"]
    end
    
    subgraph "Output Storage"
        RAW["results/raw_data/<br/>results_ladder_5xC.csv"]
        PROCESSED["results/processed_data/<br/>*_seeds_cleaned_correct_params.csv<br/>*_seeds_dirty_correct_params.csv"]
        OUTPUTS["results/outputs2/<br/>OLMES outputs"]
        PER_TASK["results/per_task_out/<br/>Task-specific results"]
    end
    
    S3 --> PROCESS
    WANDB --> PROCESS
    PROCESS --> METRICS
    METRICS --> RAW
    
    RAW --> CLEAN_NB
    CLEAN_NB --> PROCESSED
    
    MAIN --> OUTPUTS
    MAIN --> PER_TASK
    
    PARSE --> PROCESS
    
    style PROCESS fill:#f9f9f9
    style CLEAN_NB fill:#f9f9f9
    style PROCESSED fill:#f9f9f9
```

**Sources**: [single_scale/process_s3_to_csv.py](), [single_scale/readme.md:1-39](), [results/readme.md:1-18]()

## Data Ingestion Architecture

### S3 Bucket Organization

The system expects S3 buckets to follow a hierarchical structure where predictions are organized by model configuration and checkpoint:

```
s3://bucket/prefix/
  ├── {group}-{model}-{chinchilla}[-{seed}]/
  │   ├── step{N}/
  │   │   ├── {task}/predictions.jsonl
  │   │   └── ...
  │   └── step{M}/
  │       ├── all_olmes_rc_tasks/
  │       │   ├── task-001-{task_name}-predictions.jsonl
  │       │   └── ...
```

The `get_prediction_paths` function traverses this structure to identify all `predictions.jsonl` files for processing.

**Sources**: [single_scale/process_s3_to_csv.py:64-90]()

### Path Parsing and Metadata Extraction

The `parse_train_name` function extracts critical metadata from S3 paths:

| Component | Pattern | Example | Description |
|-----------|---------|---------|-------------|
| `group` | Data recipe name | `no_math_no_code` | Dataset variant identifier |
| `model` | Size with unit | `150M`, `1B` | Model parameter count |
| `chinchilla` | Multiplier | `5xC` | Training token multiplier |
| `task` | Task name | `mmlu`, `hellaswag` | Evaluation task |
| `step` | Integer | `500` | Training step number |
| `seed` | Integer (optional) | `0`, `1`, `2` | Random seed for training |

The parsing logic handles both formats: with explicit seed (`{group}-{model}-{chinchilla}-{seed}`) and without seed (`{group}-{model}-{chinchilla}`).

**Sources**: [single_scale/process_s3_to_csv.py:177-210]()

### WandB Integration

Training statistics are fetched from WandB projects using the `fetch_wandb_data` function, which queries runs based on display names matching the pattern `{group}-{model}-{chinchilla}`:

```mermaid
graph LR
    subgraph "WandB Projects"
        LADDER_BENB["ai2-llm/olmo-ladder-benb"]
        LADDER["ai2-llm/olmo-ladder"]
        LADDER_IAN["ai2-llm/olmo-ladder-ianm"]
    end
    
    subgraph "Fetched Metrics"
        TRAIN_LOSS["train/CrossEntropyLoss"]
        TOKENS["throughput/total_tokens"]
        VAL_LOSSES["Validation Losses:<br/>c4_en, dolma_common-crawl,<br/>pile, wikitext_103"]
    end
    
    subgraph "Processing"
        FETCH["fetch_wandb_data<br/>project, filters, keys"]
        APPLY["get_stat_from_data<br/>Match by (group, model, chinchilla, step)"]
    end
    
    LADDER_BENB --> FETCH
    LADDER --> FETCH
    LADDER_IAN --> FETCH
    
    FETCH --> TRAIN_LOSS
    FETCH --> TOKENS
    FETCH --> VAL_LOSSES
    
    TRAIN_LOSS --> APPLY
    TOKENS --> APPLY
    VAL_LOSSES --> APPLY
```

The system automatically selects the appropriate WandB project based on the data recipe and chinchilla multiplier, as defined in the conditional logic at [single_scale/process_s3_to_csv.py:569-579]().

**Sources**: [single_scale/process_s3_to_csv.py:36-58](), [single_scale/process_s3_to_csv.py:223-248](), [single_scale/process_s3_to_csv.py:563-587]()

## Metric Computation Pipeline

### Processing Workflow

The `process_prediction_path` function implements the core processing logic for each predictions file:

```mermaid
graph TB
    START["S3 predictions.jsonl"]
    
    PARSE_PATH["parse_train_name<br/>Extract metadata"]
    COMPUTE["compute_metrics_from_file<br/>util_metrics.py"]
    
    PRIMARY["Identify primary_metric<br/>Priority order:<br/>1. TASK_CONFIG_DEFAULTS<br/>2. acc_raw<br/>3. exact_match<br/>4. f1, mc1, pass_at_1, etc."]
    
    AGGREGATE["Aggregate metrics<br/>Compute mean across instances"]
    
    ROW["Build row dict:<br/>group, model, task, chinchilla,<br/>step, seed, metrics"]
    
    START --> PARSE_PATH
    PARSE_PATH --> COMPUTE
    COMPUTE --> PRIMARY
    PRIMARY --> AGGREGATE
    AGGREGATE --> ROW
    
    style COMPUTE fill:#f9f9f9
    style PRIMARY fill:#f9f9f9
```

The `TASK_REGISTRY` from `olmes.tasks.oe_eval_tasks` provides task-specific configuration including the primary metric to use for each task.

**Sources**: [single_scale/process_s3_to_csv.py:92-146]()

### Metric Types

The system computes multiple metric variants from raw predictions:

| Metric | Description | Source |
|--------|-------------|--------|
| `primary_metric` | Task-specific main metric (e.g., accuracy, F1, exact match) | Task config |
| `acc_raw` | Raw accuracy (uncalibrated) | Always computed |
| `acc_per_char` | Character-level accuracy | Always computed |
| `acc_per_token` | Token-level accuracy | Always computed |
| `acc_uncond` | Unconditional accuracy | Always computed |
| Task-specific | `exact_match`, `f1`, `mc1`, `pass_at_1`, etc. | Task-dependent |

These metrics are computed by `compute_metrics_from_file` in `util_metrics.py` and stored in a dictionary that gets packed into the `metrics` column.

**Sources**: [single_scale/process_s3_to_csv.py:98-146]()

### Compute Calculation

The `calc_compute` function calculates FLOPs using the standard formula:

```
compute = 6 × num_parameters × tokens
```

Where:
- `num_parameters` is extracted from the model size string (e.g., "150M" → 150,000,000)
- `tokens` comes from the `throughput/total_tokens` metric in WandB

**Sources**: [single_scale/process_s3_to_csv.py:165-175]()

## Parallel Processing

The system uses `ThreadPoolExecutor` for efficient parallel processing of S3 files:

```mermaid
graph LR
    subgraph "Batch Processing"
        PATHS["new_prediction_paths"]
        BATCH["Batch creation<br/>Size: --batch_size (default 100)"]
    end
    
    subgraph "ThreadPoolExecutor"
        POOL["max_workers = batch_size"]
        FUTURE1["Future 1<br/>process_prediction_path"]
        FUTURE2["Future 2<br/>process_prediction_path"]
        FUTUREN["Future N<br/>process_prediction_path"]
    end
    
    subgraph "Results Collection"
        COMPLETE["as_completed<br/>Collect results"]
        CACHE["temp_new_data.csv<br/>Intermediate cache"]
    end
    
    PATHS --> BATCH
    BATCH --> POOL
    POOL --> FUTURE1
    POOL --> FUTURE2
    POOL --> FUTUREN
    
    FUTURE1 --> COMPLETE
    FUTURE2 --> COMPLETE
    FUTUREN --> COMPLETE
    
    COMPLETE --> CACHE
```

The batch size is configurable via the `--batch_size` argument and is also used to configure the boto3 `max_pool_connections` for optimal S3 throughput.

**Sources**: [single_scale/process_s3_to_csv.py:500-559]()

## Data Cleaning and Validation

### Notebook Workflow

The `data_exploration_and_cleaning.ipynb` notebook performs data validation and produces two output variants:

| Output File | Description | Control Flag |
|-------------|-------------|--------------|
| `*_seeds_cleaned_correct_params.csv` | Validated data with corrected parameters | Default |
| `*_seeds_dirty_correct_params.csv` | Includes problematic data for diagnostics | `DIRTY_OUT = True` |

Both output variants are required: the cleaned version for analysis and the dirty version for certain visualizations that need to show the full data landscape.

**Sources**: [single_scale/readme.md:15-19](), [results/readme.md:11-12]()

### Data Type Schema

The processing pipeline enforces a strict data type schema defined in the `dtypes` dictionary:

```python
dtypes = {
    "group": str,           # Data recipe name
    "model": str,           # Model size
    "task": str,            # Task name
    "chinchilla": str,      # Training multiplier
    "step": int,            # Training step
    "tokens": float,        # Total tokens processed
    "compute": float,       # FLOPs
    "metrics": object,      # Dictionary of metrics
    # WandB statistics (all float)
    "train/CrossEntropyLoss": float,
    "eval/c4_en-validation/CrossEntropyLoss": float,
    # ... additional validation losses
}
```

**Sources**: [single_scale/process_s3_to_csv.py:48-58]()

## Results Directory Structure

The `results/` directory organizes outputs by processing stage:

```mermaid
graph TB
    subgraph "results/ Directory"
        RAW_DIR["raw_data/<br/>Direct S3 processing output<br/>results_ladder_5xC.csv"]
        
        PROC_DIR["processed_data/<br/>Cleaned and validated<br/>*_seeds_cleaned_correct_params.csv<br/>*_seeds_dirty_correct_params.csv"]
        
        OUTPUTS_DIR["outputs2/<br/>OLMES evaluation outputs<br/>From main.py"]
        
        TASK_DIR["per_task_out/<br/>Task-specific analysis<br/>From main.py --config"]
        
        INTERMED_DIR["new_eval_intermediates/<br/>External evaluation data<br/>From new-evals project"]
        
        SL_FILE["cheap_decisions_stacked_rc_pred_all.csv<br/>Scaling law fits"]
    end
    
    RAW_DIR --> PROC_DIR
    OUTPUTS_DIR -.-> TASK_DIR
    
    style PROC_DIR fill:#f9f9f9
```

**Sources**: [results/readme.md:1-18](), [.gitignore:6-13]()

## Single-Scale Prediction Workflow

### Running Evaluations

The `main.py` script executes single-scale predictions and per-task analysis:

```bash
# Basic single-scale predictions
python main.py

# Per-task analysis with generated configs
sh create_per_task_configs.sh config.yaml per_task_configs
ls per_task_configs/*.yaml | parallel --progress python main.py --config {}
```

The workflow generates individual YAML configuration files for each task, then processes them in parallel using GNU Parallel.

**Sources**: [single_scale/readme.md:22-38]()

### Configuration Generation

Per-task configs are created by the `create_per_task_configs.sh` script, which takes a base `config.yaml` and generates task-specific variants in the `per_task_configs/` directory. Each generated config targets a specific evaluation task.

**Sources**: [single_scale/readme.md:29-38]()

## Incremental Update Strategy

The system implements an incremental update mechanism to avoid reprocessing existing results:

```mermaid
graph TB
    CHECK_CSV["Check if csv_name exists"]
    LOAD_EXISTING["Load existing CSV<br/>Build existing_combinations set<br/>(task, group, model, chinchilla, step, seed)"]
    
    FETCH_PATHS["get_prediction_paths<br/>from S3"]
    
    FILTER["Filter to new_prediction_paths<br/>Exclude existing combinations"]
    
    PROCESS["Process only new paths<br/>ThreadPoolExecutor batch processing"]
    
    CONCAT["Concatenate with existing data<br/>Save to csv_name"]
    
    CHECK_CSV -->|Exists| LOAD_EXISTING
    CHECK_CSV -->|Not exists| FETCH_PATHS
    
    LOAD_EXISTING --> FETCH_PATHS
    FETCH_PATHS --> FILTER
    FILTER --> PROCESS
    PROCESS --> CONCAT
```

The `existing_combinations` set tracks which (task, group, model, chinchilla, step, seed) tuples have already been processed, allowing the script to skip redundant S3 fetches.

**Sources**: [single_scale/process_s3_to_csv.py:510-541]()

## Command-Line Interface

The `process_s3_to_csv.py` script accepts the following arguments:

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--s3` | str | Required | Full S3 path (e.g., `s3://bucket/prefix/`) |
| `--csv_name` | str | `results_ladder_5xC.csv` | Output CSV filename |
| `--no_refresh` | flag | False | Skip S3 refresh, use existing data only |
| `--batch_size` | int | 100 | Parallel processing batch size |

Example usage:

```bash
python process_s3_to_csv.py \
    --s3 s3://ai2-llm/eval-results/downstream/eval-for-consistent-ranking-preemption-fixed \
    --csv_name "results_ladder_5xC.csv" \
    --batch_size 200
```

**Sources**: [single_scale/process_s3_to_csv.py:615-624](), [single_scale/readme.md:8-13]()

## Interactive Visualization Output

In addition to CSV output, the processing script generates interactive Plotly HTML visualizations:

- `{s3_name}_olmes_curves_task_filter.html`: Multi-model comparison across all metrics
- `{s3_name}_olmes_curves_last_step_task_filter.html`: Latest checkpoint comparison

These visualizations include dropdown filters for task suite selection and display scaling curves across different model sizes and data recipes.

**Sources**: [single_scale/process_s3_to_csv.py:254-497]()

## Data Flow Summary

```mermaid
graph LR
    subgraph "Input"
        S3_IN["S3 predictions.jsonl"]
        WANDB_IN["WandB statistics"]
    end
    
    subgraph "Processing"
        PROCESS_SCRIPT["process_s3_to_csv.py"]
        METRIC_COMP["Metric computation<br/>util_metrics.py"]
        ENRICHMENT["WandB enrichment<br/>fetch_wandb_data"]
    end
    
    subgraph "Intermediate"
        RAW_CSV["results_ladder_5xC.csv<br/>raw_data/"]
        TEMP["temp_new_data.csv<br/>(cache)"]
    end
    
    subgraph "Cleaning"
        CLEAN_NOTEBOOK["data_exploration_and_cleaning.ipynb"]
    end
    
    subgraph "Output"
        CLEAN_CSV["*_cleaned_correct_params.csv<br/>processed_data/"]
        DIRTY_CSV["*_dirty_correct_params.csv<br/>processed_data/"]
    end
    
    S3_IN --> PROCESS_SCRIPT
    WANDB_IN --> ENRICHMENT
    
    PROCESS_SCRIPT --> METRIC_COMP
    METRIC_COMP --> TEMP
    ENRICHMENT --> TEMP
    TEMP --> RAW_CSV
    
    RAW_CSV --> CLEAN_NOTEBOOK
    CLEAN_NOTEBOOK --> CLEAN_CSV
    CLEAN_NOTEBOOK --> DIRTY_CSV
    
    style PROCESS_SCRIPT fill:#f9f9f9
    style CLEAN_NOTEBOOK fill:#f9f9f9
    style CLEAN_CSV fill:#f9f9f9
```

**Sources**: [single_scale/process_s3_to_csv.py:1-624](), [single_scale/readme.md:1-39](), [results/readme.md:1-18]()

---

