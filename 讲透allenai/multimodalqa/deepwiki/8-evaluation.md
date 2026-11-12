<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/multimodalqa · page 8 Evaluation · fetched 2026-10-26 -->

# Evaluation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [baselines/README.md](baselines/README.md)
- [baselines/evaluate.py](baselines/evaluate.py)

</details>



## Purpose and Scope

This page provides a comprehensive overview of the evaluation system used in the MultiModalQA framework. It covers the evaluation pipeline, metrics computation, answer normalization, and results analysis. The evaluation system compares model predictions against gold answers and produces detailed performance metrics broken down by modality, hop type, and question type.

For detailed information about specific evaluation metrics and their implementation, see [Evaluation Metrics](#8.1). For guidance on interpreting and analyzing evaluation results, see [Results Analysis](#8.2). For information about running the inference pipeline that produces predictions, see [Running Inference](#6).

## Evaluation Pipeline Overview

The evaluation system is implemented in [baselines/evaluate.py]() and can be invoked either as a standalone script or programmatically from the inference pipeline. The following diagram shows how evaluation integrates with the broader system:

**Diagram: Evaluation System Integration**

```mermaid
graph TB
    subgraph "Inference Pipeline"
        PIPELINE["pipeline.py<br/>run_inference()"]
        PRED_OUTPUT["predictions.json<br/>{qas_id: answer}"]
    end
    
    subgraph "Gold Data"
        TEST_FILE["MMQA_dev.jsonl<br/>or MMQA_test.jsonl"]
        GOLD_EXTRACT["Extract gold answers<br/>qid → answers list"]
        METADATA["Extract metadata<br/>modality, hop_type, qtype"]
    end
    
    subgraph "Evaluation Module (evaluate.py)"
        NORMALIZE["_normalize_answer()<br/>Text normalization"]
        BAGS["_answer_to_bags()<br/>Convert to token sets"]
        ALIGN["_align_bags()<br/>Optimal alignment"]
        COMPUTE["_compute_f1()<br/>F1 calculation"]
        MATCH["_match_numbers_if_present()<br/>Number validation"]
        
        METRICS["evaluate_predictions()<br/>list_em, list_f1"]
    end
    
    subgraph "Results Output"
        OVERALL["Overall Scores<br/>EM, F1"]
        BY_MOD["By Modality<br/>text/table/image"]
        BY_HOP["By Hop Type<br/>single/multi-hop"]
        BY_QTYPE["By Question Type<br/>16 categories"]
    end
    
    PIPELINE --> PRED_OUTPUT
    TEST_FILE --> GOLD_EXTRACT
    TEST_FILE --> METADATA
    
    PRED_OUTPUT --> METRICS
    GOLD_EXTRACT --> METRICS
    
    METRICS --> NORMALIZE
    NORMALIZE --> BAGS
    BAGS --> ALIGN
    ALIGN --> COMPUTE
    COMPUTE --> MATCH
    
    METRICS --> OVERALL
    METADATA --> BY_MOD
    METADATA --> BY_HOP
    METADATA --> BY_QTYPE
    
    OVERALL --> BY_MOD
    OVERALL --> BY_HOP
    OVERALL --> BY_QTYPE
```

**Sources:** [baselines/evaluate.py:1-263](), [baselines/pipeline.py]()

## Core Evaluation Metrics

The MultiModalQA evaluation system uses two primary metrics, both adapted from the DROP dataset evaluation protocol:

| Metric | Function | Description | Use Case |
|--------|----------|-------------|----------|
| **Exact Match (EM)** | `list_em()` | Checks if predicted and gold answer sets are identical | Strict correctness |
| **F1 Score** | `list_f1()` | Token-level F1 with optimal alignment | Partial credit |

Both metrics support:
- **List-valued answers**: Answers can be lists of strings (e.g., multiple entities)
- **Multiple gold references**: Each question can have multiple valid answer sets
- **Normalized comparison**: All text is normalized before comparison

The system computes the maximum score across all gold references for each prediction using the `metric_max_over_ground_truths()` function at [baselines/evaluate.py:165-170]().

For detailed information about metric computation, normalization procedures, and alignment algorithms, see [Evaluation Metrics](#8.1).

**Sources:** [baselines/evaluate.py:147-163](), [baselines/evaluate.py:165-170]()

## Evaluation Workflow

The following diagram shows the detailed workflow of how predictions are evaluated:

**Diagram: Evaluation Workflow with Code Functions**

```mermaid
graph TD
    subgraph "Input Processing"
        PRED["predictions dict<br/>{qid: pred_answer}"]
        GOLD["gold_answers dict<br/>{qid: [gold_answer1, ...]}"]
    end
    
    subgraph "Per-Question Evaluation"
        LOOP["for qid in gold_answers"]
        GET_PRED["predictions.get(qid)"]
        GET_REFS["gold_answers[qid]"]
        
        MAX_METRIC["metric_max_over_ground_truths()<br/>evaluate.py:165-170"]
        
        subgraph "For Each Gold Reference"
            CALL_EM["list_em(pred, gold)<br/>evaluate.py:147-153"]
            CALL_F1["list_f1(pred, gold)<br/>evaluate.py:156-162"]
            
            TO_BAGS["_answer_to_bags()<br/>evaluate.py:80-93"]
            CHECK_SET["Check set equality<br/>(for EM)"]
            ALIGN["_align_bags()<br/>evaluate.py:96-111"]
            SCORE_F1["np.mean(f1_per_bag)"]
        end
    end
    
    subgraph "Aggregation"
        INST_RESULTS["instance_eval_results<br/>{qid: {metric: score}}"]
        AVG["np.mean() * 100<br/>evaluate.py:202-203"]
        OVERALL_SCORES["eval_scores<br/>{metric: avg_score}"]
    end
    
    PRED --> LOOP
    GOLD --> LOOP
    LOOP --> GET_PRED
    LOOP --> GET_REFS
    
    GET_PRED --> MAX_METRIC
    GET_REFS --> MAX_METRIC
    
    MAX_METRIC --> CALL_EM
    MAX_METRIC --> CALL_F1
    
    CALL_EM --> TO_BAGS
    TO_BAGS --> CHECK_SET
    
    CALL_F1 --> TO_BAGS
    TO_BAGS --> ALIGN
    ALIGN --> SCORE_F1
    
    CHECK_SET --> INST_RESULTS
    SCORE_F1 --> INST_RESULTS
    
    INST_RESULTS --> AVG
    AVG --> OVERALL_SCORES
```

**Sources:** [baselines/evaluate.py:173-213]()

## Answer Normalization Pipeline

Before computing metrics, all answers undergo normalization to ensure fair comparison. The normalization pipeline consists of the following steps:

**Diagram: Answer Normalization Pipeline**

```mermaid
graph LR
    INPUT["Raw answer string"]
    
    TOKENIZE["_tokenize()<br/>Split on space and hyphen<br/>evaluate.py:38-39"]
    
    subgraph "Per-Token Processing"
        LOWER["_lower()<br/>Lowercase<br/>evaluate.py:34-35"]
        REMOVE_PUNC["_remove_punc()<br/>Strip punctuation<br/>evaluate.py:27-31"]
        NORM_NUM["_normalize_number()<br/>Convert to float<br/>evaluate.py:70-77"]
        REMOVE_ART["_remove_articles()<br/>Remove a/an/the<br/>evaluate.py:15-17"]
        WHITESPACE["_white_space_fix()<br/>Normalize spaces<br/>evaluate.py:20-21"]
    end
    
    JOIN["Join tokens with spaces<br/>evaluate.py:50"]
    OUTPUT["Normalized answer"]
    
    INPUT --> TOKENIZE
    TOKENIZE --> LOWER
    LOWER --> REMOVE_PUNC
    REMOVE_PUNC --> NORM_NUM
    NORM_NUM --> REMOVE_ART
    REMOVE_ART --> WHITESPACE
    WHITESPACE --> JOIN
    JOIN --> OUTPUT
```

Key normalization behaviors:
- **Numbers**: Converted to float strings (e.g., "5" → "5.0")
- **Word numbers**: Converted to numeric form (e.g., "five" → "5.0")
- **Articles**: "a", "an", "the" are removed
- **Punctuation**: Removed from non-numeric tokens
- **Case**: All text lowercased

The complete normalization function is `_normalize_answer()` at [baselines/evaluate.py:42-51](). For more details on answer normalization, see [Answer Normalization](#9.2).

**Sources:** [baselines/evaluate.py:15-77]()

## Multi-Reference and Multi-Answer Evaluation

The evaluation system handles two types of multiple answers:

### List-Valued Answers

A single answer can be a list of strings (e.g., ["Paris", "London", "Berlin"]). The system:

1. Converts each answer to a list of normalized token sets via `_answer_to_bags()` at [baselines/evaluate.py:80-93]()
2. Uses the Hungarian algorithm (`linear_sum_assignment`) to find optimal alignment at [baselines/evaluate.py:106]()
3. Computes per-bag F1 scores and averages them

### Multiple Gold References

Each question can have multiple valid gold answer sets. The system:

1. Evaluates the prediction against each gold reference
2. Takes the maximum score across all references via `metric_max_over_ground_truths()` at [baselines/evaluate.py:165-170]()

This is particularly important for questions with multiple valid formulations.

**Sources:** [baselines/evaluate.py:80-111](), [baselines/evaluate.py:165-170]()

## Results Categorization

The `evaluate_prediction_file()` function at [baselines/evaluate.py:216-263]() produces results broken down by multiple dimensions:

**Diagram: Results Categorization Structure**

```mermaid
graph TD
    subgraph "Input Data Extraction"
        EXAMPLES["Read MMQA_*.jsonl"]
        EXTRACT_GOLD["Extract gold_answers<br/>evaluate.py:226-227"]
        EXTRACT_MOD["Extract answer_modalities<br/>evaluate.py:228-230"]
        EXTRACT_HOP["Extract hop_types<br/>evaluate.py:232"]
        EXTRACT_QTYPE["Extract question_types<br/>evaluate.py:231"]
    end
    
    subgraph "Evaluation Calls"
        EVAL_OVERALL["evaluate_predictions()<br/>overall scores"]
        EVAL_BY_MOD["evaluate_predictions()<br/>by modality<br/>evaluate.py:240-241"]
        EVAL_BY_HOP["evaluate_predictions()<br/>by hop type<br/>evaluate.py:251"]
        EVAL_BY_QTYPE["evaluate_predictions()<br/>by question type<br/>evaluate.py:258"]
    end
    
    subgraph "Output Reports"
        PRINT_OVERALL["Overall EM/F1<br/>evaluate.py:235-237"]
        PRINT_MOD["Per-modality breakdown<br/>text/table/image<br/>evaluate.py:242-248"]
        PRINT_HOP["Per-hop breakdown<br/>single/multi-hop<br/>evaluate.py:252-255"]
        PRINT_QTYPE["Per-qtype breakdown<br/>16 categories<br/>evaluate.py:259-262"]
    end
    
    EXAMPLES --> EXTRACT_GOLD
    EXAMPLES --> EXTRACT_MOD
    EXAMPLES --> EXTRACT_HOP
    EXAMPLES --> EXTRACT_QTYPE
    
    EXTRACT_GOLD --> EVAL_OVERALL
    EXTRACT_GOLD --> EVAL_BY_MOD
    EXTRACT_GOLD --> EVAL_BY_HOP
    EXTRACT_GOLD --> EVAL_BY_QTYPE
    
    EXTRACT_MOD --> EVAL_BY_MOD
    EXTRACT_HOP --> EVAL_BY_HOP
    EXTRACT_QTYPE --> EVAL_BY_QTYPE
    
    EVAL_OVERALL --> PRINT_OVERALL
    EVAL_BY_MOD --> PRINT_MOD
    EVAL_BY_HOP --> PRINT_HOP
    EVAL_BY_QTYPE --> PRINT_QTYPE
```

**Sources:** [baselines/evaluate.py:216-263]()

### Result Categories

| Category | Source | Examples | Purpose |
|----------|--------|----------|---------|
| **Overall** | All examples | Single aggregate score | Top-level performance |
| **By Modality** | `answer_modalities` dict | text, table, image | Modality-specific performance |
| **By Hop Type** | Derived from question type | Single-hop, Multi-hop | Reasoning complexity |
| **By Question Type** | `metadata.type` | TextQ, ComposeText→Table, etc. | Fine-grained analysis |

The hop type is derived from the question type using the `MULTI_HOP_QUESTION_TYPES` constant from `common_utils.py`, as shown at [baselines/evaluate.py:232]().

For detailed guidance on interpreting these results, see [Results Analysis](#8.2).

**Sources:** [baselines/evaluate.py:239-262]()

## Baseline Performance Results

The repository includes baseline results for three inference methods on the development set. These can be reproduced using `run_pipeline.sh` at [baselines/scripts/run_pipeline.sh]().

**Table: Development Set Performance (F1 / EM)**

| Method | Single-Modality | Multi-Modality | All |
|--------|-----------------|----------------|-----|
| **Context-only** | 7.94 / 10.73 | 6.63 / 9.00 | 7.41 / 10.03 |
| **AutoRouting** | 51.68 / 58.48 | 34.18 / 40.18 | 44.65 / 51.13 |
| **ImplicitDecomp** | 51.60 / 58.35 | 44.59 / 51.19 | 48.79 / 55.48 |

Key observations:
- **ImplicitDecomp** achieves the best overall performance (48.79 F1), particularly on multi-modality questions
- **AutoRouting** performs comparably on single-modality but degrades on multi-hop reasoning
- **Context-only** serves as a lower-bound baseline, demonstrating the necessity of question understanding

These results are documented at [baselines/README.md:42-48]().

**Sources:** [baselines/README.md:42-48]()

## Running Evaluation

### Standalone Evaluation

To evaluate a prediction file against gold answers:

```bash
python evaluate.py \
  --prediction_path predictions.json \
  --gold_path downloads/MMQA/MMQA_dev.jsonl
```

This invokes the `evaluate_prediction_file()` function at [baselines/evaluate.py:216-263]() and prints:
- Overall EM and F1 scores
- Breakdown by modality with example counts
- Breakdown by hop type
- Breakdown by question type

### Integrated with Inference Pipeline

The inference pipeline at [baselines/pipeline.py]() calls `evaluate_predictions()` directly when not in `--predict_only` mode. This enables end-to-end evaluation during inference runs.

### Parallel Evaluation

For comprehensive baseline evaluation, use:

```bash
./scripts/run_pipeline.sh
```

This script runs evaluation for all three methods (implicit_decomp, auto_routing, context_only) in parallel across multiple GPUs, as documented at [baselines/README.md:38-48]().

**Sources:** [baselines/evaluate.py:266-281](), [baselines/README.md:19-48]()

## Implementation Details

### Key Functions

| Function | Location | Purpose |
|----------|----------|---------|
| `evaluate_prediction_file()` | [evaluate.py:216-263]() | Main entry point for file-based evaluation |
| `evaluate_predictions()` | [evaluate.py:173-213]() | Core evaluation logic with categorization |
| `metric_max_over_ground_truths()` | [evaluate.py:165-170]() | Multi-reference scoring |
| `list_em()` | [evaluate.py:147-153]() | Exact match metric |
| `list_f1()` | [evaluate.py:156-162]() | F1 score metric |
| `_align_bags()` | [evaluate.py:96-111]() | Optimal alignment using Hungarian algorithm |
| `_compute_f1()` | [evaluate.py:114-129]() | Token-level F1 computation |
| `_normalize_answer()` | [evaluate.py:42-51]() | Answer normalization pipeline |

### External Dependencies

The evaluation system uses:
- `scipy.optimize.linear_sum_assignment` for optimal bag alignment at [baselines/evaluate.py:8]() and [baselines/evaluate.py:106]()
- `word2number.w2n.word_to_num` for word number conversion at [baselines/evaluate.py:9]() and [baselines/evaluate.py:74]()
- NumPy for score aggregation at [baselines/evaluate.py:6]()

**Sources:** [baselines/evaluate.py:1-11](), [baselines/evaluate.py:96-129]()

## Error Handling

The evaluation system handles missing predictions gracefully:

```python
if qas_id not in predictions:
    print(f"Missing prediction for question {qas_id}, ...")
    instance_eval_results[qas_id] = {
        metric: 0.0 for metric in eval_funcs.keys()
    }
```

This occurs at [baselines/evaluate.py:184-188]() and ensures that evaluation continues even when predictions are incomplete, with missing predictions receiving a score of 0.0 for all metrics.

**Sources:** [baselines/evaluate.py:182-188]()

---

