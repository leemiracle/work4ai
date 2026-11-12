<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/SciRIFF · extra page Attributed QA Evaluation · fetched 2026-10-26 -->

# Attributed QA Evaluation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sciriff/eval/metrics/attributed_qa_eval.py](sciriff/eval/metrics/attributed_qa_eval.py)

</details>



This document covers the attributed question answering evaluation system, which assesses model performance on tasks requiring both accurate answers and supporting evidence. This evaluation uses Large Language Models as judges to provide nuanced assessment of answer quality beyond traditional metrics.

For information about summary comparison evaluation, see [Summary Comparison](#3.4.2). For the broader LM judge framework and batch processing utilities, see [LM Judge System](#3.4).

## System Overview

The `AttributedQAEval` class provides comprehensive evaluation for attributed question answering tasks, combining traditional token-level metrics with LM judge assessments. The system evaluates both the accuracy of answers and the quality of supporting evidence citations.

```mermaid
flowchart TD
    subgraph "Input Processing"
        instances["Evaluation Instances"]
        pred_dict["instance['pred']"]
        ref_dict["instance['ref']"]
    end
    
    subgraph "AttributedQAEval Class"
        evaluator["AttributedQAEval"]
        normalize["_normalize_answer()"]
        evaluate_one["_evaluate_one()"]
        get_rouge["_get_rouge_scores()"]
    end
    
    subgraph "Scoring Systems"
        f1_scoring["Token F1 Computation"]
        rouge_scoring["ROUGE Evaluation"]
        lm_judge_scoring["LM Judge Assessment"]
    end
    
    subgraph "LM Judge Pipeline"
        make_prompt["make_prompt()"]
        batch_api["batch_lm_judge()"]
        direct_api["call_lm_judge()"]
        extract_rating["extract_rating()"]
    end
    
    subgraph "Output Metrics"
        f1_scores["F1 Scores\n(answer/evidence)"]
        rouge_scores["ROUGE Scores"]
        judge_scores["LM Judge Ratings\n(1-5 scale)"]
        failure_counts["Parse Failure Tracking"]
    end
    
    instances --> evaluator
    pred_dict --> normalize
    ref_dict --> evaluate_one
    evaluator --> evaluate_one
    normalize --> f1_scoring
    
    evaluate_one --> f1_scoring
    evaluate_one --> lm_judge_scoring
    evaluator --> get_rouge
    get_rouge --> rouge_scoring
    
    lm_judge_scoring --> make_prompt
    make_prompt --> batch_api
    make_prompt --> direct_api
    batch_api --> extract_rating
    direct_api --> extract_rating
    
    f1_scoring --> f1_scores
    rouge_scoring --> rouge_scores
    extract_rating --> judge_scores
    evaluator --> failure_counts
    
    style evaluator fill:#f9f9f9
    style batch_api fill:#e8f4fd
```

**Sources:** [sciriff/eval/metrics/attributed_qa_eval.py:190-333]()

## Core Evaluation Metrics

The system computes multiple metrics to provide comprehensive assessment of attributed QA performance:

### Token-Level Metrics

| Metric Type | Variants | Description |
|-------------|----------|-------------|
| **Answer F1** | `f1_answer_all`, `f1_answer_parsed` | Token overlap between predicted and reference answers |
| **Evidence F1** | `f1_evidence_all`, `f1_evidence_parsed` | Token overlap between predicted and reference evidence |
| **ROUGE Scores** | `rouge1`, `rouge2`, `rougeL` | N-gram and longest common subsequence overlap |

The `_all` variants include all instances (assigning 0 to parsing failures), while `_parsed` variants only include successfully parsed responses.

```mermaid
flowchart LR
    subgraph "Answer Processing"
        answer_pred["instance['pred']['answer']"]
        answer_ref["instance['ref']['answer']"]
        normalize_answer["_normalize_answer()"]
        compute_f1["util.compute_token_f1()"]
    end
    
    subgraph "Evidence Processing" 
        evidence_pred["instance['pred']['evidence']"]
        evidence_ref["instance['ref']['evidence']"]
        flatten_evidence["util.flatten()"]
        join_evidence["' '.join()"]
    end
    
    answer_pred --> normalize_answer
    normalize_answer --> compute_f1
    answer_ref --> compute_f1
    
    evidence_pred --> flatten_evidence
    flatten_evidence --> join_evidence
    evidence_ref --> join_evidence
    join_evidence --> compute_f1
    
    style normalize_answer fill:#f9f9f9
    style flatten_evidence fill:#f9f9f9
```

**Sources:** [sciriff/eval/metrics/attributed_qa_eval.py:193-205](), [sciriff/eval/metrics/attributed_qa_eval.py:243-255](), [sciriff/eval/metrics/attributed_qa_eval.py:256-267]()

### LM Judge Assessment

The LM judge provides qualitative assessment using GPT-4o on a 1-5 scale:

- **5**: Model answer includes all important information from the reference
- **3**: Model answer is somewhat similar but not completely accurate  
- **1**: Model answer is totally inaccurate or unrelated

Ratings are normalized to 0-1 scale using `(rating - 1) / 4` for final reporting.

**Sources:** [sciriff/eval/metrics/attributed_qa_eval.py:112-115](), [sciriff/eval/metrics/attributed_qa_eval.py:320-321]()

## LM Judge Implementation

The system supports both synchronous and batch processing for LM judge evaluation:

### Prompt Construction

The `make_prompt()` function constructs evaluation prompts by extracting key elements from the evaluation instance:

```mermaid
flowchart TD
    subgraph "Prompt Components"
        instance_prompt["instance['prompt']"]
        title_extract["Title Extraction"]
        question_extract["Question Regex Matching"]
        evidence_join["Evidence Concatenation"]
    end
    
    subgraph "Structured Prompt"
        paper_title["Paper Title"]
        excerpts["Paper Excerpts"]
        question["Question Text"]
        ref_answer["Reference Answer"]
        pred_answer["Model Answer"]
    end
    
    subgraph "Rating Instructions"
        scale_def["1-5 Rating Scale"]
        format_spec["Response Format Requirements"]
        eval_criteria["Evaluation Criteria"]
    end
    
    instance_prompt --> title_extract
    instance_prompt --> question_extract
    instance_prompt --> evidence_join
    
    title_extract --> paper_title
    question_extract --> question
    evidence_join --> excerpts
    
    paper_title --> structured_prompt["Final LM Judge Prompt"]
    excerpts --> structured_prompt
    question --> structured_prompt
    ref_answer --> structured_prompt
    pred_answer --> structured_prompt
    
    scale_def --> structured_prompt
    format_spec --> structured_prompt
    eval_criteria --> structured_prompt
    
    style structured_prompt fill:#e8f4fd
```

**Sources:** [sciriff/eval/metrics/attributed_qa_eval.py:96-138]()

### Response Processing

The `extract_rating()` function parses LM judge responses using regex pattern matching:

- **Pattern**: `r"Rating:\s*(\d+)"`
- **Validation**: Ensures rating is in [1,2,3,4,5] range
- **Fallback**: Returns rating of 3 for parsing failures

**Sources:** [sciriff/eval/metrics/attributed_qa_eval.py:141-153]()

## Batch Processing System

For cost-effective evaluation at scale, the system supports OpenAI's Batch API:

```mermaid
flowchart TD
    subgraph "Batch Job Creation"
        instances["Evaluation Instances"]
        create_batch_file["create_batch_file()"]
        batch_tasks["JSONL Batch Tasks"]
        submit_batch_job["submit_batch_job()"]
    end
    
    subgraph "OpenAI Batch API"
        upload_file["files.create()"]
        create_batch["batches.create()"]
        batch_job_id["Batch Job ID"]
    end
    
    subgraph "Result Processing"
        get_batch_results["get_batch_results()"]
        batch_lm_judge["batch_lm_judge()"]
        extract_ratings["Rating Extraction"]
    end
    
    subgraph "File Management"
        timestamped_logs["./attributed_qa_eval-logs/"]
        lm_judge_raw_file["Raw Results JSON"]
        lm_judge_mapping["Batch ID Mapping"]
    end
    
    instances --> create_batch_file
    create_batch_file --> batch_tasks
    batch_tasks --> submit_batch_job
    
    submit_batch_job --> upload_file
    upload_file --> create_batch
    create_batch --> batch_job_id
    
    batch_job_id --> get_batch_results
    get_batch_results --> batch_lm_judge
    batch_lm_judge --> extract_ratings
    
    create_batch_file --> timestamped_logs
    batch_lm_judge --> lm_judge_raw_file
    submit_batch_job --> lm_judge_mapping
    
    style create_batch_file fill:#f9f9f9
    style batch_lm_judge fill:#f9f9f9
```

**Sources:** [sciriff/eval/metrics/attributed_qa_eval.py:19-48](), [sciriff/eval/metrics/attributed_qa_eval.py:50-63](), [sciriff/eval/metrics/attributed_qa_eval.py:156-174]()

### Batch Configuration

Each batch task uses the following configuration:
- **Model**: `gpt-4o-2024-08-06`  
- **Endpoint**: `/v1/chat/completions`
- **Completion Window**: 24 hours
- **File Format**: JSONL with custom task IDs

**Sources:** [sciriff/eval/metrics/attributed_qa_eval.py:23-39]()

## Error Handling and Robustness

The evaluation system implements comprehensive error handling:

### Parse Failure Tracking

The system tracks various failure modes using structured counters:

| Failure Type | Tracked Values | Purpose |
|--------------|---------------|---------|
| `answer` | `yes`/`no` | Whether answer field was successfully parsed |
| `evidence` | `yes`/`no` | Whether evidence field was successfully parsed |  
| `answer_entry_is_str` | `yes`/`no` | Whether answer is string vs other types |

**Sources:** [sciriff/eval/metrics/attributed_qa_eval.py:288-292]()

### Data Normalization

The `_normalize_answer()` method handles various response formats:

- **String responses**: Used directly
- **List responses**: Flattened and joined with spaces
- **Dictionary responses**: Converted to string representation
- **Other types**: Raises exception for unexpected formats

**Sources:** [sciriff/eval/metrics/attributed_qa_eval.py:193-205]()

### Graceful Degradation

When parsing fails:
- **F1 scores**: Assigned value of 0
- **LM judge scores**: Assigned minimum rating of 1
- **Failure tracking**: Incremented appropriately
- **Evaluation continues**: Other instances still processed

**Sources:** [sciriff/eval/metrics/attributed_qa_eval.py:222-227](), [sciriff/eval/metrics/attributed_qa_eval.py:244-246]()

## Integration with Evaluation Pipeline

The `AttributedQAEval` class integrates with the broader evaluation system through standardized interfaces:

```mermaid
graph TD
    subgraph "Evaluation Task"
        task_class["Task Implementation"]
        call_evaluator["evaluator = AttributedQAEval()"]
        run_evaluation["evaluator.evaluate()"]
    end
    
    subgraph "File Management" 
        lm_judge_file["LM Judge Scores Cache"]
        lm_judge_raw_file["Raw API Responses"]
        lm_judge_mapping["Batch Job Mapping"]
    end
    
    subgraph "Configuration"
        use_batch_api["Batch API Flag"]
        instances["Evaluation Instances"]
    end
    
    subgraph "Output"
        scores_dict["Aggregated Scores"]
        failure_stats["Parsing Statistics"]
        final_results["Task Results"]
    end
    
    task_class --> call_evaluator
    call_evaluator --> run_evaluation
    
    lm_judge_file --> run_evaluation
    lm_judge_raw_file --> run_evaluation
    lm_judge_mapping --> run_evaluation
    
    use_batch_api --> run_evaluation
    instances --> run_evaluation
    
    run_evaluation --> scores_dict
    run_evaluation --> failure_stats
    scores_dict --> final_results
    failure_stats --> final_results
    
    style run_evaluation fill:#e8f4fd
```

**Sources:** [sciriff/eval/metrics/attributed_qa_eval.py:269-333]()

---

