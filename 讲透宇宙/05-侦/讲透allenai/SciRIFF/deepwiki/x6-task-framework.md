<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/SciRIFF · extra page Task Framework · fetched 2026-10-26 -->

# Task Framework

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sciriff/eval/tasks/_base.py](sciriff/eval/tasks/_base.py)

</details>



This document covers the base classes and common functionality that underpin all evaluation tasks in the SciRIFF evaluation system. The Task Framework provides standardized interfaces for loading predictions, computing metrics, and handling JSON parsing across different scientific evaluation tasks.

For implementation details of specific evaluation tasks like Qasper or MUP, see [Qasper Abstractive QA](#3.3.2) and [MUP Document Summarization](#3.3.3). For the broader evaluation pipeline context, see [Evaluation System](#3).

## Architecture Overview

The Task Framework is built around two main base classes that provide common functionality for all evaluation tasks in the system.

### Class Hierarchy

```mermaid
classDiagram
    class EvalTask {
        +Path pred_dir
        +Path eval_dir
        +baseline_dir
        +max_instances
        +Path pred_file
        +__init__(pred_dir, eval_dir, baseline_dir, max_instances)
        +get_prediction_file(wkdir) Path
        +load_predictions(fname) list
        +get_raw_predictions(fname) list
        +get_bleu() float
        +evaluate() void
        +dump_results(res) void
        +make_flattened_metrics(res)$ dict
        +make_summary_metrics(res)$ dict
    }
    
    class JSONTask {
        +JSONParser json_parser
        +dict counts
        +default
        +__init__(pred_dir, eval_dir, baseline_dir, max_instances)
        +parse_predictions() tuple
        +_make_pairs(preds, refs, prompts)$ dict
    }
    
    class JSONParser {
        +default
        +task
        +__call__(texts) tuple
    }
    
    EvalTask <|-- JSONTask
    JSONTask --> JSONParser : uses
```

Sources: [sciriff/eval/tasks/_base.py:13-125](), [sciriff/eval/tasks/_base.py:126-180]()

## EvalTask Base Class

The `EvalTask` class provides core functionality that all evaluation tasks inherit, including prediction loading, basic metrics computation, and result storage.

### Core Initialization and Setup

The base class handles standard directory setup and prediction file discovery:

```mermaid
flowchart TD
    init["EvalTask.__init__()"] --> setup_dirs["Setup eval_dir, pred_dir paths"]
    setup_dirs --> find_pred["get_prediction_file()"]
    find_pred --> search_patterns["Search for files matching:<br/>pretrained__, model__, samples_"]
    search_patterns --> check_vllm["Check subdirectories<br/>for VLLM output structure"]
    check_vllm --> validate["Validate single prediction file found"]
    validate --> store_path["Store in self.pred_file"]
```

Sources: [sciriff/eval/tasks/_base.py:14-44]()

### Prediction Loading and Processing

The framework provides standardized methods for loading and processing model predictions:

| Method | Purpose | Return Type |
|--------|---------|-------------|
| `load_predictions()` | Load raw prediction data from JSONL files | `list` |
| `get_raw_predictions()` | Extract and structure predictions with prompts and references | `list[dict]` |
| `get_bleu()` | Compute BLEU scores using HuggingFace evaluate library | `float` |

The `get_raw_predictions()` method standardizes the prediction format across different model outputs:

```mermaid
flowchart LR
    raw_entry["Raw Prediction Entry"] --> extract_prompt["Extract prompt from<br/>arguments.gen_args_0.arg_0"]
    extract_prompt --> extract_ref["Extract reference<br/>from target field"]
    raw_entry --> extract_pred["Extract prediction from<br/>filtered_resps[0]"]
    extract_pred --> clean_pred["Strip '</s>' tokens<br/>from Tulu models"]
    clean_pred --> structured["Structured Output:<br/>{prompt, pred, ref}"]
    extract_ref --> structured
```

Sources: [sciriff/eval/tasks/_base.py:46-61](), [sciriff/eval/tasks/_base.py:98-109]()

### Metrics and Results Management

The base class provides a standardized approach to metrics computation and result storage:

```mermaid
flowchart TD
    evaluate["evaluate() method"] --> compute_bleu["Compute BLEU scores"]
    compute_bleu --> dump_metrics["dump_results()"]
    dump_metrics --> save_raw["Save metrics.json"]
    dump_metrics --> save_flat["Save metrics_flat.json<br/>via make_flattened_metrics()"]
    dump_metrics --> save_summary["Save metrics_summary.json<br/>via make_summary_metrics()"]
    evaluate --> save_predictions["Save raw_predictions.jsonl<br/>via util.write_jsonl()"]
```

Sources: [sciriff/eval/tasks/_base.py:63-75](), [sciriff/eval/tasks/_base.py:87-96](), [sciriff/eval/tasks/_base.py:111-124]()

## JSONTask Extended Framework

The `JSONTask` class extends `EvalTask` to handle evaluation tasks that require JSON parsing of model outputs, which is common in scientific tasks with structured responses.

### JSON Parsing Integration

```mermaid
flowchart TD
    jsontask_init["JSONTask.__init__()"] --> super_init["Call EvalTask.__init__()"]
    super_init --> create_parser["Initialize JSONParser<br/>with default and task name"]
    create_parser --> init_counts["Initialize self.counts = {}"]
    
    parse_call["parse_predictions()"] --> get_raw["Get raw predictions"]
    get_raw --> parse_refs["Parse references with JSONParser"]
    parse_refs --> validate_refs["Validate all refs parse successfully"]
    validate_refs --> parse_preds["Parse predictions with JSONParser"]
    parse_preds --> track_counts["Track parsing success/failure counts"]
    track_counts --> make_pairs["_make_pairs() creates paired data"]
    make_pairs --> return_data["Return {parsed, all, raw} versions"]
```

Sources: [sciriff/eval/tasks/_base.py:130-135](), [sciriff/eval/tasks/_base.py:158-179]()

### Data Pairing Strategy

The `_make_pairs()` static method creates multiple versions of the evaluation data to handle JSON parsing failures gracefully:

| Data Version | Description | Use Case |
|--------------|-------------|----------|
| `parsed` | Only successfully parsed predictions | Primary evaluation metrics |
| `all` | All predictions (failed parses use extracted values) | Fallback evaluation |
| `raw` | Unprocessed predictions for debugging | Error analysis and debugging |

```mermaid
flowchart LR
    input_data["Input: preds, refs, prompts"] --> create_raw["Create raw_pairs<br/>for debugging"]
    input_data --> create_all["Create all_pairs<br/>with extracted values"]
    input_data --> filter_success["Filter successful parses<br/>status != 'extract_failure'"]
    filter_success --> create_parsed["Create successful_pairs<br/>for primary metrics"]
    create_raw --> output["Return dict with<br/>parsed, all, raw versions"]
    create_all --> output
    create_parsed --> output
```

Sources: [sciriff/eval/tasks/_base.py:137-156]()

## Integration with Evaluation Pipeline

The Task Framework integrates with the broader evaluation system through standardized interfaces:

```mermaid
flowchart TD
    subgraph "External Components"
        prediction_gen["predict_eleuther.py<br/>Prediction Generation"]
        metrics_comp["compute_science_metrics.py<br/>Metrics Computation"]
        task_registry["eval_tasks.registry<br/>Task Registration"]
    end
    
    subgraph "Task Framework"
        eval_task["EvalTask"]
        json_task["JSONTask"]
        json_parser["JSONParser"]
    end
    
    subgraph "Concrete Tasks"
        qasper_task["QasperTask"]
        mup_task["MUPTask"]
        bioasq_task["BioASQTask"]
    end
    
    prediction_gen --> eval_task
    metrics_comp --> task_registry
    task_registry --> eval_task
    
    eval_task --> json_task
    json_task --> json_parser
    
    json_task --> qasper_task
    json_task --> mup_task
    eval_task --> bioasq_task
```

Sources: [sciriff/eval/tasks/_base.py:1-180]()

---

