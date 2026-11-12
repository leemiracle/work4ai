<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/SciRIFF · extra page MUP Document Summarization · fetched 2026-10-26 -->

# MUP Document Summarization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sciriff/eval/tasks/mup_single_document_summarization.py](sciriff/eval/tasks/mup_single_document_summarization.py)

</details>



This document covers the MUP (Multi-document Summarization in Biomedical Domain) single document summarization evaluation task implementation. This task evaluates model performance on summarizing scientific documents by comparing generated summaries against reference summaries using both traditional automated metrics and LM judge evaluation.

For information about the overall evaluation system architecture, see [Evaluation System](#3). For details about the LM judge summary comparison implementation, see [Summary Comparison](#3.4.2).

## Purpose and Scope

The MUP evaluation task assesses model capabilities in generating high-quality summaries of scientific documents. It combines traditional metrics (BLEU, ROUGE) with sophisticated LM judge evaluation to provide comprehensive assessment of summary quality, coherence, and factual accuracy.

## Task Architecture

The MUP evaluation task follows the standard evaluation framework while incorporating specialized summary evaluation components.

```mermaid
graph TD
    subgraph "Task Framework"
        EvalTask["EvalTask (Base)"]
        MUPTask["MUP"]
        EvalTask --> MUPTask
    end
    
    subgraph "Input Processing"
        RawPreds["raw_predictions"]
        Predictions["predictions[]"]
        References["references[]"]
        Prompts["prompts[]"]
        
        RawPreds --> Predictions
        RawPreds --> References  
        RawPreds --> Prompts
    end
    
    subgraph "Evaluation Methods"
        BLEUEval["BLEU Scoring"]
        ROUGEEval["ROUGE Scoring"]
        LMJudge["LM Judge Evaluation"]
        
        subgraph "LM Judge Components"
            SummaryComp["SummaryComparison"]
            RefComparison["reference_comparison"]
        end
    end
    
    subgraph "Output Generation"
        FlattenedMetrics["make_flattened_metrics()"]
        SummaryMetrics["make_summary_metrics()"]
        ResultsDump["dump_results()"]
    end
    
    MUPTask --> Predictions
    MUPTask --> References
    MUPTask --> Prompts
    
    Predictions --> BLEUEval
    Predictions --> ROUGEEval
    Predictions --> LMJudge
    References --> ROUGEEval
    References --> LMJudge
    
    LMJudge --> SummaryComp
    SummaryComp --> RefComparison
    
    BLEUEval --> FlattenedMetrics
    ROUGEEval --> FlattenedMetrics
    RefComparison --> FlattenedMetrics
    
    FlattenedMetrics --> SummaryMetrics
    SummaryMetrics --> ResultsDump
```

Sources: [sciriff/eval/tasks/mup_single_document_summarization.py:13-116]()

## Evaluation Pipeline

The MUP evaluation follows a multi-stage pipeline that processes predictions through different evaluation methods.

### Instance Initialization

The `_initiate_instances()` method prepares evaluation data by extracting predictions, references, and prompts from raw prediction files.

```mermaid
flowchart TD
    subgraph "Data Preparation"
        PredFile["pred_file"]
        RawPreds["get_raw_predictions()"]
        JSONLWrite["util.write_jsonl()"]
        
        PredFile --> RawPreds
        RawPreds --> JSONLWrite
    end
    
    subgraph "Data Extraction"
        RawPreds --> Predictions["predictions = [entry['pred']]"]
        RawPreds --> References["references = [entry['ref']]"] 
        RawPreds --> Prompts["prompts = [entry['prompt']]"]
    end
    
    subgraph "Instance Creation"
        Predictions --> Instances["instances[i] = {...}"]
        References --> Instances
        Prompts --> Instances
        
        Instances --> InstanceDict["{'prediction': ..., 'reference': ..., 'prompt': ...}"]
    end
    
    InstanceDict --> ReturnValues["return instances, predictions, references"]
```

Sources: [sciriff/eval/tasks/mup_single_document_summarization.py:34-59]()

### Evaluation Execution

The main `evaluate()` method orchestrates different evaluation approaches:

| Evaluation Type | Method | Purpose |
|----------------|---------|---------|
| BLEU | `get_bleu()` | Lexical similarity to reference |
| ROUGE | `evaluate.load("rouge")` | N-gram and sequence overlap |
| LM Judge | `SummaryComparison` | Quality and coherence assessment |

```mermaid
graph TD
    subgraph "Traditional Metrics"
        BLEUComp["get_bleu()"]
        ROUGELoad["evaluate.load('rouge')"]
        ROUGEComp["rouge_scorer.compute()"]
        
        ROUGELoad --> ROUGEComp
    end
    
    subgraph "LM Judge Setup"
        LMJudgeFiles["lm_judge_raw_results_file<br/>lm_judge_agg_results_file<br/>lm_judge_outputs<br/>lm_judge_mapping"]
        BatchCheck["Check existing results"]
        BatchRetrieve["retrieve_batch_job_results()"]
        
        LMJudgeFiles --> BatchCheck
        BatchCheck --> BatchRetrieve
    end
    
    subgraph "Summary Evaluation"
        SummaryEval["SummaryComparison.evaluate()"]
        EvalParams["eval_type='reference_comparison'<br/>n_sample=100<br/>use_batch_api"]
        
        SummaryEval --> EvalParams
    end
    
    subgraph "Result Processing"
        ResDict["res = {}"]
        BLEUComp --> ResDict
        ROUGEComp --> ResDict
        SummaryEval --> ResDict
        ResDict --> DumpResults["dump_results(res)"]
    end
```

Sources: [sciriff/eval/tasks/mup_single_document_summarization.py:61-116]()

## Implementation Details

### Class Structure

The `MUP` class extends the base `EvalTask` with summarization-specific functionality:

```mermaid
classDiagram
    class EvalTask {
        +get_raw_predictions()
        +get_bleu()
        +dump_results()
    }
    
    class MUP {
        +make_flattened_metrics()$
        +make_summary_metrics()$
        +_initiate_instances()
        +evaluate(use_batch_api)
        -lm_judge_file
    }
    
    class SummaryComparison {
        +evaluate()
    }
    
    EvalTask <|-- MUP
    MUP --> SummaryComparison : uses
```

Sources: [sciriff/eval/tasks/mup_single_document_summarization.py:13-26]()

### Metrics Processing

The task implements two static methods for metrics aggregation:

#### Flattened Metrics
`make_flattened_metrics()` creates a flat dictionary combining all evaluation scores:

```mermaid
graph LR
    subgraph "Input Metrics"
        BLEUScore["res['bleu']"]
        ROUGEScores["res['rouge']"]
        LMJudgeScores["res['lm_judge']"]
    end
    
    subgraph "Processing"
        FlatDict["metrics_flat = {}"]
        BLEUAdd["metrics_flat['bleu'] = ..."]
        ROUGEUpdate["metrics_flat.update(rouge)"]
        LMJudgeLoop["for k,v in lm_judge.items()"]
        KeyFormat["lm_judge_{k}_{sub_k}"]
    end
    
    BLEUScore --> BLEUAdd
    ROUGEScores --> ROUGEUpdate
    LMJudgeScores --> LMJudgeLoop
    LMJudgeLoop --> KeyFormat
    
    BLEUAdd --> FlatDict
    ROUGEUpdate --> FlatDict
    KeyFormat --> FlatDict
```

Sources: [sciriff/eval/tasks/mup_single_document_summarization.py:14-25]()

#### Summary Metrics
`make_summary_metrics()` extracts key metrics for high-level reporting:

| Metric | Source | Purpose |
|--------|--------|---------|
| `lm_judge_reference` | `avg_rating` from reference comparison | Overall quality score |
| `rouge` | `rougeL` score | Sequence-level similarity |

Sources: [sciriff/eval/tasks/mup_single_document_summarization.py:27-32]()

### Batch Processing Integration

The task supports OpenAI batch API for cost-effective LM judge evaluation:

```mermaid
sequenceDiagram
    participant MUP as "MUP.evaluate()"
    participant BatchCheck as "Batch File Check"
    participant BatchAPI as "OpenAI Batch API"
    participant SummComp as "SummaryComparison"
    
    MUP->>BatchCheck: Check lm_judge_mapping.json
    alt Batch exists
        BatchCheck->>BatchAPI: fetch_batch_file()
        BatchAPI->>BatchCheck: Return file_id
        BatchCheck->>MUP: retrieve_batch_job_results()
    else No batch
        MUP->>SummComp: evaluate(use_batch_api=True)
        SummComp->>BatchAPI: Submit batch job
        BatchAPI->>SummComp: Return batch_id
        SummComp->>MUP: Save batch mapping
    end
```

Sources: [sciriff/eval/tasks/mup_single_document_summarization.py:94-113]()

## Output Structure

The evaluation produces structured results combining traditional metrics with LM judge assessments:

```mermaid
graph TD
    subgraph "Result Structure"
        ResRoot["res = {}"]
        BLEURes["res['bleu']"]
        ROUGERes["res['rouge']"]
        LMJudgeRes["res['lm_judge']"]
        
        subgraph "ROUGE Breakdown"
            Rouge1["rouge['rouge1']"]
            Rouge2["rouge['rouge2']"]  
            RougeL["rouge['rougeL']"]
        end
        
        subgraph "LM Judge Breakdown"
            RefComp["lm_judge['reference_comparison']"]
            AvgRating["reference_comparison['avg_rating']"]
        end
        
        ResRoot --> BLEURes
        ResRoot --> ROUGERes
        ResRoot --> LMJudgeRes
        
        ROUGERes --> Rouge1
        ROUGERes --> Rouge2
        ROUGERes --> RougeL
        
        LMJudgeRes --> RefComp
        RefComp --> AvgRating
    end
    
    subgraph "Final Processing"
        FlatMetrics["make_flattened_metrics()"]
        SummMetrics["make_summary_metrics()"]
        DumpResults["dump_results()"]
        
        ResRoot --> FlatMetrics
        FlatMetrics --> SummMetrics
        SummMetrics --> DumpResults
    end
```

Sources: [sciriff/eval/tasks/mup_single_document_summarization.py:64-115]()

---

