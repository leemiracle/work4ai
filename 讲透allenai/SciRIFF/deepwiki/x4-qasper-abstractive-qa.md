<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/SciRIFF · extra page Qasper Abstractive QA · fetched 2026-10-26 -->

# Qasper Abstractive QA

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sciriff/eval/tasks/qasper_abstractive_qa.py](sciriff/eval/tasks/qasper_abstractive_qa.py)

</details>



This page documents the implementation of the Qasper abstractive question answering evaluation task within the SciRIFF evaluation framework. The Qasper task evaluates model performance on generating natural language answers to questions about scientific papers, along with supporting evidence citations.

For information about the overall evaluation task framework, see [Task Framework](#3.3.1). For details about the underlying LM judge evaluation system used by Qasper, see [Attributed QA Evaluation](#3.4.1).

## Task Overview

The Qasper task implements evaluation for abstractive question answering on scientific papers. Unlike extractive QA tasks that select spans from the source text, this task requires models to generate free-form natural language answers while providing supporting evidence from the paper.

The task expects model outputs in JSON format with two key components:
- `answer`: A natural language response to the question
- `evidence`: Supporting citations or evidence from the source paper

**Architecture Integration**

```mermaid
flowchart TD
    subgraph "Input Processing"
        ModelPreds["Model Predictions<br/>(JSON Format)"]
        QasperDataset["Qasper Dataset<br/>(Questions + Papers)"]
    end
    
    subgraph "Qasper Task Implementation"
        QasperClass["Qasper Class<br/>qasper_abstractive_qa.py"]
        JSONTask["JSONTask<br/>(Base Class)"]
        DefaultVals["default = {answer: None, evidence: None}"]
    end
    
    subgraph "Evaluation Components"
        ParsePreds["parse_predictions()<br/>JSONTask method"]
        AttributedQAEval["AttributedQAEval<br/>attributed_qa_eval.py"]
        BLEUMetric["get_bleu()<br/>Standard metric"]
    end
    
    subgraph "LM Judge Integration"
        LMJudgeFile["lm_judge.json"]
        LMJudgeRaw["lm_judge_raw.json"]  
        LMJudgeMapping["lm_judge_mapping.json"]
        BatchAPI["OpenAI Batch API<br/>(Optional)"]
    end
    
    subgraph "Output Metrics"
        ValidJSONResults["results[valid_json]<br/>Successfully parsed only"]
        AllResults["results[all]<br/>All predictions"]
        FlatMetrics["Flattened Metrics<br/>make_flattened_metrics()"]
        SummaryMetrics["Summary Metrics<br/>make_summary_metrics()"]
    end
    
    ModelPreds --> QasperClass
    QasperDataset --> QasperClass
    QasperClass --> JSONTask
    JSONTask --> ParsePreds
    
    QasperClass --> DefaultVals
    ParsePreds --> AttributedQAEval
    QasperClass --> BLEUMetric
    
    AttributedQAEval --> LMJudgeFile
    AttributedQAEval --> LMJudgeRaw
    AttributedQAEval --> LMJudgeMapping
    AttributedQAEval --> BatchAPI
    
    AttributedQAEval --> ValidJSONResults
    AttributedQAEval --> AllResults
    ValidJSONResults --> FlatMetrics
    AllResults --> FlatMetrics
    AllResults --> SummaryMetrics
    
    style QasperClass fill:#f9f9f9
    style AttributedQAEval fill:#f9f9f9
    style BatchAPI fill:#f9f9f9
```

Sources: [sciriff/eval/tasks/qasper_abstractive_qa.py:1-65]()

## Implementation Details

### Class Structure

The `Qasper` class inherits from `JSONTask`, providing automatic JSON parsing capabilities for structured model outputs. The class defines default values for expected output fields:

```python
default = {"answer": None, "evidence": None}
```

This default structure ensures that even when models fail to generate valid JSON, the evaluation can proceed with null values for missing fields.

**Key Methods**

```mermaid
classDiagram
    class JSONTask {
        +parse_predictions()
        +get_bleu()
        +dump_results()
    }
    
    class Qasper {
        +default: dict
        +evaluate(use_batch_api)
        +make_flattened_metrics(res)$ 
        +make_summary_metrics(res)$
    }
    
    class AttributedQAEval {
        +evaluate(predictions, lm_judge_file, lm_judge_raw_file, lm_judge_mapping, use_batch_api)
    }
    
    JSONTask <|-- Qasper
    Qasper ..> AttributedQAEval : uses
    
    note for Qasper : "Static methods for\nmetric aggregation"
    note for AttributedQAEval : "LM judge evaluation\nfor answer quality"
```

Sources: [sciriff/eval/tasks/qasper_abstractive_qa.py:8-10](), [sciriff/eval/tasks/qasper_abstractive_qa.py:40-64]()

### Evaluation Process

The main evaluation workflow occurs in the `evaluate` method, which coordinates multiple evaluation components:

1. **JSON Parsing**: Inherited `parse_predictions()` method processes model outputs
2. **Attributed QA Evaluation**: `AttributedQAEval` assesses answer quality and evidence
3. **Standard Metrics**: BLEU score computation for reference comparison
4. **Results Aggregation**: Combines metrics from different evaluation modes

The evaluation runs on two data subsets:
- `valid_json`: Only predictions that successfully parsed as JSON
- `all`: All predictions, with defaults used for parsing failures

**Evaluation Flow**

```mermaid
flowchart TD
    subgraph "Input Processing"
        EvaluateCall["evaluate(use_batch_api=False)"]
        ParsePreds["predictions, json_counts = parse_predictions()"]
    end
    
    subgraph "File Preparation" 
        LMJudgeFiles["lm_judge.json<br/>lm_judge_raw.json<br/>lm_judge_mapping.json"]
        EvaluatorInit["evaluator = AttributedQAEval()"]
    end
    
    subgraph "Dual Evaluation"
        ValidJSONEval["evaluator.evaluate(predictions[parsed])"]
        AllEval["evaluator.evaluate(predictions[all], lm_judge_file=..., use_batch_api=...)"]
    end
    
    subgraph "Additional Metrics"
        BLEUComp["get_bleu()"]
        JSONCounts["json_counts tracking"]
    end
    
    subgraph "Results Assembly"
        ResultsDict["res[results][valid_json]<br/>res[results][all]<br/>res[bleu]<br/>res[json_counts]"]
        BatchCheck["Check if batch job submitted"]
        DumpResults["dump_results(res)"]
    end
    
    EvaluateCall --> ParsePreds
    ParsePreds --> LMJudgeFiles
    LMJudgeFiles --> EvaluatorInit
    
    EvaluatorInit --> ValidJSONEval
    EvaluatorInit --> AllEval
    ParsePreds --> BLEUComp
    ParsePreds --> JSONCounts
    
    ValidJSONEval --> ResultsDict
    AllEval --> ResultsDict
    BLEUComp --> ResultsDict
    JSONCounts --> ResultsDict
    
    ResultsDict --> BatchCheck
    BatchCheck --> DumpResults
    
    style AllEval fill:#f9f9f9
    style BatchCheck fill:#f9f9f9
```

Sources: [sciriff/eval/tasks/qasper_abstractive_qa.py:40-64]()

## Metrics Computation

### Flattened Metrics

The `make_flattened_metrics` static method transforms nested evaluation results into a flat dictionary structure suitable for tabular reporting. It processes metrics for both evaluation settings (`valid_json` and `all`):

| Metric Category | Examples | Purpose |
|---|---|---|
| Parse Success Rates | `all_answer_frac_parsed`, `valid_json_evidence_frac_parsed` | Track JSON parsing success |
| Performance Scores | `all_f1_answer_all`, `valid_json_lm_judge` | Core evaluation metrics |
| Standard Metrics | `bleu`, `json_parsed` | Traditional NLP metrics |

The flattening process extracts:
- **Parsing Statistics**: Success rates for answer, evidence, and string validation
- **Performance Metrics**: All scores from the AttributedQAEval results  
- **Global Metrics**: BLEU scores and overall JSON parsing success

**Metrics Processing Pipeline**

```mermaid
flowchart LR
    subgraph "Raw Results Structure"
        NestedRes["res[results][setting][scores][metric]<br/>res[results][setting][answer_parse][method]<br/>res[bleu]<br/>res[json_counts]"]
    end
    
    subgraph "Flattening Process"
        SettingLoop["For each setting:<br/>valid_json, all"]
        ParseMetrics["Extract parse fractions:<br/>answer, evidence, answer_entry_is_str"]
        ScoreMetrics["Extract all scores:<br/>f1_answer_all, lm_judge, etc."]
        GlobalMetrics["Add bleu, json_parsed"]
    end
    
    subgraph "Flattened Output" 
        FlatDict["metrics_flat[setting_metric] = value<br/>Example: all_f1_answer_all = 0.75"]
    end
    
    NestedRes --> SettingLoop
    SettingLoop --> ParseMetrics
    SettingLoop --> ScoreMetrics
    NestedRes --> GlobalMetrics
    
    ParseMetrics --> FlatDict
    ScoreMetrics --> FlatDict
    GlobalMetrics --> FlatDict
    
    style FlatDict fill:#f9f9f9
```

Sources: [sciriff/eval/tasks/qasper_abstractive_qa.py:11-30]()

### Summary Metrics

The `make_summary_metrics` method extracts the most important metrics for cross-task comparison, focusing on the `all` setting which includes all predictions:

- **`lm_judge_answer`**: LM judge score for answer quality (may be None if not available)
- **`f1_answer_all`**: F1 score for answer content matching
- **`f1_evidence_all`**: F1 score for evidence citation accuracy

These summary metrics appear in the final evaluation tables and enable comparison across different tasks and models.

Sources: [sciriff/eval/tasks/qasper_abstractive_qa.py:32-38]()

## Batch Processing Support

The Qasper task supports OpenAI's Batch API for cost-effective LM judge evaluation. When `use_batch_api=True` is passed to the `evaluate` method:

1. Evaluation requests are submitted to the batch API
2. The method returns early with a notification message
3. Results must be retrieved later using batch processing utilities

This integration allows large-scale evaluation while reducing API costs, particularly important for the computationally expensive LM judge evaluations that Qasper relies on.

Sources: [sciriff/eval/tasks/qasper_abstractive_qa.py:52-60]()

---

