<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/RetrievalAttention · page 3 Benchmarking and Evaluation · fetched 2026-10-26 -->

# Benchmarking and Evaluation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [benchmark/LongBench/eval.py](benchmark/LongBench/eval.py)
- [benchmark/ruler/data/prepare.py](benchmark/ruler/data/prepare.py)

</details>



This document covers the comprehensive benchmarking and evaluation system used to assess RetroInfer's performance compared to standard attention mechanisms. The system includes synthetic benchmarks, real-world task evaluations, and throughput measurements to validate both accuracy and efficiency improvements.

For information about the specific attention mechanisms being evaluated, see [Attention Mechanisms](#2). For setup instructions to run these benchmarks, see [Setup and Installation](#4).

## Overview

The RetroInfer benchmarking system consists of three primary evaluation frameworks that assess different aspects of the system's performance:

**Benchmark Architecture**
```mermaid
graph TB
    subgraph "Evaluation Frameworks"
        RULER["RULER Benchmark<br/>Synthetic Tasks"]
        LONGBENCH["LongBench Evaluation<br/>Real-world Tasks"]
        THROUGHPUT["Throughput Testing<br/>Performance Metrics"]
    end
    
    subgraph "Configuration System"
        CONFIG["benchmark/config.py<br/>generate_config()"]
        MODEL2PATH["config/model2path.json"]
        DATASET2PROMPT["config/dataset2prompt.json"]
    end
    
    subgraph "Target Systems"
        RETROINFER["RetroInfer Attention<br/>budget_ratio: 0.018"]
        FLASH_ATTN["Full_Flash_Attn<br/>Baseline"]
    end
    
    subgraph "Evaluation Metrics"
        ACCURACY["Accuracy Metrics<br/>F1, ROUGE, Classification"]
        SPEED["Throughput Metrics<br/>4.5x-10.5x improvement"]
        MEMORY["Memory Usage<br/>GPU/CPU allocation"]
    end
    
    RULER --> CONFIG
    LONGBENCH --> CONFIG
    THROUGHPUT --> CONFIG
    
    CONFIG --> MODEL2PATH
    CONFIG --> DATASET2PROMPT
    
    MODEL2PATH --> RETROINFER
    MODEL2PATH --> FLASH_ATTN
    
    RETROINFER --> ACCURACY
    RETROINFER --> SPEED
    FLASH_ATTN --> ACCURACY
    FLASH_ATTN --> SPEED
    
    ACCURACY --> MEMORY
    SPEED --> MEMORY
```

Sources: [benchmark/LongBench/eval.py:82-122](), [benchmark/ruler/data/prepare.py:67-141]()

## Supported Models and Attention Types

The benchmarking system supports evaluation across multiple model architectures and attention mechanisms:

| Model | Max Length | Attention Types |
|-------|------------|----------------|
| `llama-3-8b-1048k` | 1048576 | RetroInfer, Full_Flash_Attn |
| `llama-3.1-8b` | 131072 | RetroInfer, Full_Flash_Attn |
| `qwen2.5-7b` | 131072 | RetroInfer, Full_Flash_Attn |
| `qwen2.5-72b` | 131072 | RetroInfer, Full_Flash_Attn |

The system compares RetroInfer attention against Full Flash Attention as the baseline across all supported models.

Sources: [benchmark/LongBench/eval.py:44-48]()

## LongBench Evaluation System

LongBench provides real-world task evaluation through the `benchmark/LongBench/eval.py` script, which implements a comprehensive scoring system for various task types:

**Dataset to Metric Mapping**
```mermaid
graph LR
    subgraph "Question Answering Tasks"
        QA_TASKS["narrativeqa<br/>qasper<br/>multifieldqa_en<br/>hotpotqa<br/>2wikimqa<br/>musique<br/>triviaqa"]
        QA_METRIC["qa_f1_score"]
        QA_TASKS --> QA_METRIC
    end
    
    subgraph "Summarization Tasks"
        SUM_TASKS["gov_report<br/>qmsum<br/>multi_news<br/>samsum"]
        SUM_METRIC["rouge_score"]
        SUM_TASKS --> SUM_METRIC
    end
    
    subgraph "Classification Tasks"
        CLASS_TASKS["trec<br/>lsht"]
        CLASS_METRIC["classification_score"]
        CLASS_TASKS --> CLASS_METRIC
    end
    
    subgraph "Code Tasks"
        CODE_TASKS["lcc<br/>repobench-p"]
        CODE_METRIC["code_sim_score"]
        CODE_TASKS --> CODE_METRIC
    end
    
    subgraph "Retrieval Tasks"
        RETR_TASKS["passage_retrieval_en<br/>passage_count"]
        RETR_METRIC["retrieval_score<br/>count_score"]
        RETR_TASKS --> RETR_METRIC
    end
```

The evaluation script processes prediction files from `results/pred/{model}/{attn_type}/` and generates comprehensive scores using the `dataset2metric` mapping defined in [benchmark/LongBench/eval.py:18-40]().

Sources: [benchmark/LongBench/eval.py:18-40](), [benchmark/LongBench/eval.py:82-122]()

## RULER Benchmark System

RULER generates synthetic benchmark data through the `benchmark/ruler/data/prepare.py` script, which supports multiple task types and model templates:

**RULER Data Generation Flow**
```mermaid
graph TD
    subgraph "Template System"
        TEMPLATES["Templates Dictionary<br/>base, meta-chat, vicuna-chat"]
        MODEL_TEMPLATE["model_template_type"]
        TASK_TEMPLATE["task_template"]
    end
    
    subgraph "Task Configuration"
        YAML_CONFIG["synthetic.yaml<br/>Task definitions"]
        CONSTANTS["synthetic/constants.py<br/>TASKS base config"]
        TASK_ARGS["Task-specific args"]
    end
    
    subgraph "Data Generation"
        PREPARE_SCRIPT["prepare.py<br/>main()"]
        TASK_SCRIPTS["synthetic/{task}.py<br/>Individual task generators"]
        SUBPROCESS["subprocess.run()<br/>Execute task script"]
    end
    
    subgraph "Output"
        JSONL_OUTPUT["task/subset.jsonl<br/>Generated samples"]
        SAMPLE_FORMAT["index, input, outputs"]
    end
    
    TEMPLATES --> MODEL_TEMPLATE
    MODEL_TEMPLATE --> PREPARE_SCRIPT
    YAML_CONFIG --> PREPARE_SCRIPT
    CONSTANTS --> PREPARE_SCRIPT
    PREPARE_SCRIPT --> TASK_SCRIPTS
    TASK_SCRIPTS --> SUBPROCESS
    SUBPROCESS --> JSONL_OUTPUT
    JSONL_OUTPUT --> SAMPLE_FORMAT
```

The system uses model-specific templates defined in [benchmark/ruler/data/prepare.py:50-64]() and generates data through task-specific Python scripts executed via subprocess calls.

Sources: [benchmark/ruler/data/prepare.py:50-64](), [benchmark/ruler/data/prepare.py:67-141]()

## Evaluation Metrics and Scoring

The benchmarking system implements multiple evaluation metrics imported from a metrics module:

**Metric Implementation**
```mermaid
graph TB
    subgraph "Scoring Functions"
        QA_F1["qa_f1_score<br/>qa_f1_zh_score"]
        ROUGE["rouge_score<br/>rouge_zh_score"]
        CLASSIFICATION["classification_score"]
        RETRIEVAL["retrieval_score<br/>retrieval_zh_score"]
        CODE_SIM["code_sim_score"]
        COUNT["count_score"]
    end
    
    subgraph "Evaluation Methods"
        SCORER["scorer()<br/>Standard evaluation"]
        SCORER_E["scorer_e()<br/>Length-based evaluation"]
    end
    
    subgraph "Length Categories"
        SHORT["0-4k tokens"]
        MEDIUM["4-8k tokens"]
        LONG["8k+ tokens"]
    end
    
    QA_F1 --> SCORER
    ROUGE --> SCORER
    CLASSIFICATION --> SCORER
    RETRIEVAL --> SCORER
    CODE_SIM --> SCORER
    COUNT --> SCORER
    
    SCORER --> SCORER_E
    SCORER_E --> SHORT
    SCORER_E --> MEDIUM
    SCORER_E --> LONG
```

The `scorer_e()` function in [benchmark/LongBench/eval.py:52-68]() provides length-based evaluation, categorizing performance by input length ranges for LongBench-E evaluation.

Sources: [benchmark/LongBench/eval.py:6-16](), [benchmark/LongBench/eval.py:52-68](), [benchmark/LongBench/eval.py:70-79]()

## Configuration Management

The benchmarking system relies on JSON configuration files to manage model paths, dataset prompts, and evaluation parameters:

**Configuration File Structure**
```mermaid
graph LR
    subgraph "Configuration Files"
        MODEL2PATH["model2path.json<br/>Model path mappings"]
        DATASET2PROMPT["dataset2prompt.json<br/>Task prompt templates"]
        MODEL2MAXLEN["model2maxlen.json<br/>Max sequence lengths"]
        DATASET2MAXLEN["dataset2maxlen.json<br/>Generation limits"]
    end
    
    subgraph "Runtime Configuration"
        ARGS_MODEL["args.model<br/>Model selection"]
        ARGS_ATTN["args.attn_type<br/>Attention method"]
        ARGS_E["args.e<br/>LongBench-E flag"]
    end
    
    subgraph "Result Paths"
        PRED_PATH["results/pred/{model}/{attn_type}/"]
        PRED_E_PATH["results/pred_e/{model}/{attn_type}/"]
        RESULT_JSON["result.json<br/>Final scores"]
    end
    
    MODEL2PATH --> ARGS_MODEL
    ARGS_MODEL --> PRED_PATH
    ARGS_ATTN --> PRED_PATH
    ARGS_E --> PRED_E_PATH
    PRED_PATH --> RESULT_JSON
    PRED_E_PATH --> RESULT_JSON
```

The configuration system loads model paths from JSON files and constructs result paths based on model and attention type selections, as implemented in [benchmark/LongBench/eval.py:87-93]().

Sources: [benchmark/LongBench/eval.py:87-93](), [benchmark/LongBench/eval.py:118-121]()

## Running Evaluations

The evaluation process involves executing the benchmark scripts with appropriate parameters:

**Evaluation Execution Flow**
```mermaid
graph TD
    subgraph "Input Parameters"
        MODEL_ARG["--model<br/>Model selection"]
        ATTN_ARG["--attn_type<br/>RetroInfer or Full_Flash_Attn"]
        E_FLAG["--e<br/>LongBench-E evaluation"]
    end
    
    subgraph "Data Processing"
        LOAD_CONFIG["Load model2path.json"]
        SCAN_FILES["Scan prediction files"]
        PROCESS_JSONL["Process .jsonl files"]
    end
    
    subgraph "Scoring Pipeline"
        EXTRACT_DATA["Extract predictions, answers"]
        APPLY_METRIC["Apply dataset2metric mapping"]
        CALCULATE_SCORE["Calculate final scores"]
    end
    
    subgraph "Output Generation"
        SCORE_DICT["scores dictionary"]
        RESULT_JSON["result.json output"]
        CONSOLE_OUTPUT["Console evaluation results"]
    end
    
    MODEL_ARG --> LOAD_CONFIG
    ATTN_ARG --> LOAD_CONFIG
    E_FLAG --> LOAD_CONFIG
    LOAD_CONFIG --> SCAN_FILES
    SCAN_FILES --> PROCESS_JSONL
    PROCESS_JSONL --> EXTRACT_DATA
    EXTRACT_DATA --> APPLY_METRIC
    APPLY_METRIC --> CALCULATE_SCORE
    CALCULATE_SCORE --> SCORE_DICT
    SCORE_DICT --> RESULT_JSON
    SCORE_DICT --> CONSOLE_OUTPUT
```

The evaluation script processes all `.jsonl` files in the prediction directory, applies appropriate metrics, and outputs comprehensive results as shown in [benchmark/LongBench/eval.py:96-121]().

Sources: [benchmark/LongBench/eval.py:42-50](), [benchmark/LongBench/eval.py:96-121]()

---

