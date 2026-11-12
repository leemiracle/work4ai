<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/multimodalqa · page 6 Running Inference · fetched 2026-10-26 -->

# Running Inference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [baselines/README.md](baselines/README.md)
- [baselines/pipeline.py](baselines/pipeline.py)
- [baselines/scripts/run_pipeline.sh](baselines/scripts/run_pipeline.sh)

</details>



## Purpose and Scope

This page provides a practical guide to running inference on the MultiModalQA dataset using the baseline models. It covers the command-line interface, the pipeline orchestration logic, and how to execute evaluations on the dev or test sets.

For detailed information about individual modality-specific QA models, see [Baseline Models](#5). For training these models, see [Training Models](#7). For understanding the evaluation metrics, see [Evaluation](#8). For implementation details of the pipeline orchestrator, see [Pipeline Implementation](#6.1), and for running baseline evaluations in parallel, see [Running Baseline Evaluations](#6.2).

---

## Overview

The inference system in MultiModalQA is centered around the `pipeline.py` script, which orchestrates the complete question-answering workflow. The pipeline loads all modality-specific models, classifies incoming questions by type, routes them to appropriate models, and optionally performs multi-hop reasoning with bridge entity extraction.

The system supports three distinct inference methods, each corresponding to a different baseline approach described in the ICLR 2021 paper:

| Method | Description | Dev F1 / EM |
|--------|-------------|-------------|
| `implicit_decomp` | Multi-hop reasoning with explicit hop modeling | 48.79 / 55.48 |
| `auto_routing` | Direct routing to final answer modality | 44.65 / 51.13 |
| `context_only` | Context-only baseline (ignores question) | 7.41 / 10.03 |

**Sources:** [baselines/README.md:1-53](), [baselines/scripts/run_pipeline.sh:1-50]()

---

## Basic Inference Command

The simplest way to run inference is to execute `pipeline.py` with the required arguments. Here is the command structure for evaluating the `implicit_decomp` method on the dev set:

```bash
python pipeline.py \
  --qtype_model_dir downloads/checkpoints/qtype_clf_models/ \
  --text_qa_model_dir downloads/checkpoints/text_qa_models/implicit_decomp/ \
  --table_qa_model_dir downloads/checkpoints/table_qa_models/implicit_decomp/ \
  --image_qa_model_path downloads/checkpoints/image_qa_models/implicit_decomp/model.pt \
  --image_qa_vocab downloads/checkpoints/image_qa_models/vocab.pickle \
  --image_features_dir downloads/checkpoints/img_features/ \
  --data_dir downloads/MMQA/ \
  --test_file MMQA_dev.jsonl \
  --output_dir output/results/implicit_decomp_dev/ \
  --do_lower_case \
  --method implicit_decomp
```

**Sources:** [baselines/README.md:19-35](), [baselines/pipeline.py:1-360]()

---

## Pipeline Architecture

The following diagram illustrates the complete architecture of the inference pipeline, showing how code components interact:

```mermaid
graph TB
    subgraph "Entry Point"
        MAIN["main()<br/>[pipeline.py:220-359]"]
    end
    
    subgraph "Argument Parsing"
        PARSER["argparse.ArgumentParser"]
        MAIN --> PARSER
        PARSER --> INF_ARGS["add_inference_args()<br/>[pipeline.py:73-159]"]
        PARSER --> QTYPE_ARGS["add_qtype_clf_args()<br/>[pipeline.py:27-31]"]
        PARSER --> TEXT_ARGS["add_text_qa_args()<br/>[pipeline.py:34-38]"]
        PARSER --> TABLE_ARGS["add_table_qa_args()<br/>[pipeline.py:41-45]"]
        PARSER --> IMAGE_ARGS["add_image_qa_args()<br/>[pipeline.py:48-71]"]
    end
    
    subgraph "Model Loading"
        QTYPE_MODEL["QuestionTypePredictor<br/>[qtype_clf/inference.py]"]
        TEXT_MODEL["TextQAPredictor<br/>[text_qa/inferece.py]"]
        TABLE_MODEL["TableQAPredictor<br/>[table_qa/inference.py]"]
        IMAGE_MODEL["ImageQAPredictor<br/>[image_qa/inference.py]"]
        
        MAIN --> QTYPE_MODEL
        MAIN --> TEXT_MODEL
        MAIN --> TABLE_MODEL
        MAIN --> IMAGE_MODEL
    end
    
    subgraph "Context Loading"
        TEXT_DOCS["text_docs dict<br/>read_jsonl(MMQA_texts.jsonl)"]
        TABLE_DOCS["table_docs dict<br/>read_jsonl(MMQA_tables.jsonl)"]
        
        MAIN --> TEXT_DOCS
        MAIN --> TABLE_DOCS
    end
    
    subgraph "Inference Loop"
        EXAMPLES["all_examples<br/>read_jsonl(test_file)"]
        PREDICT["predict()<br/>[pipeline.py:161-217]"]
        
        MAIN --> EXAMPLES
        EXAMPLES --> PREDICT
        QTYPE_MODEL --> PREDICT
        TEXT_MODEL --> PREDICT
        TABLE_MODEL --> PREDICT
        IMAGE_MODEL --> PREDICT
    end
    
    subgraph "Output Generation"
        ALL_RESULTS["all_results dict"]
        PRED_FILE["predictions_.json"]
        INFO_FILE["all_prediction_info.json"]
        
        PREDICT --> ALL_RESULTS
        ALL_RESULTS --> PRED_FILE
        ALL_RESULTS --> INFO_FILE
    end
    
    subgraph "Evaluation"
        EVAL["evaluate_prediction_file()<br/>[evaluate.py]"]
        PRED_FILE --> EVAL
    end
```

**Sources:** [baselines/pipeline.py:220-359]()

---

## Command-Line Arguments

The `pipeline.py` script accepts numerous command-line arguments organized into several categories:

### Model Checkpoint Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `--qtype_model_dir` | Directory containing question type classifier checkpoint | Yes |
| `--text_qa_model_dir` | Directory containing text QA model checkpoint | Yes |
| `--table_qa_model_dir` | Directory containing table QA model checkpoint | Yes |
| `--image_qa_model_path` | Path to image QA model checkpoint file | Yes |
| `--image_qa_vocab` | Path to vocabulary file for image QA answer generation | Yes |
| `--image_features_dir` | Directory containing pre-extracted image features | Conditional* |
| `--raw_image_dir` | Directory containing raw images (if features not pre-extracted) | Conditional* |
| `--vilbert_dir` | Directory containing VilBERT pre-trained weights and config | No (default: `downloads/vilbert/`) |

*Either `--image_features_dir` or `--raw_image_dir` must be provided.

### Data and Output Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `--data_dir` | Directory containing MMQA dataset files | Yes |
| `--test_file` | Which file to evaluate (e.g., `MMQA_dev.jsonl` or `MMQA_test.jsonl`) | No (default: `MMQA_dev.jsonl`) |
| `--output_dir` | Directory to save predictions and results | Yes |

### Inference Configuration Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--method` | Inference method: `auto_routing` or `implicit_decomp` | `implicit_decomp` |
| `--use_oracle_qtype` | Use gold question type (for oracle experiments) | False |
| `--context_only` | Ignore question text (for context-only baseline) | False |
| `--predict_only` | Skip evaluation (for test set prediction) | False |
| `--do_lower_case` | Lowercase input text (for uncased models) | False |

### Text/Table QA Parameters

| Argument | Description | Default |
|----------|-------------|---------|
| `--max_seq_length` | Maximum sequence length after tokenization | 384 |
| `--doc_stride` | Stride for splitting long documents | 128 |
| `--max_query_length` | Maximum question length in tokens | 100 |
| `--n_best_size` | Number of n-best predictions to consider | 20 |
| `--max_answer_length` | Maximum answer length | 30 |

### Hardware Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--no_cuda` | Disable CUDA even if available | False |

**Sources:** [baselines/pipeline.py:73-159](), [baselines/README.md:19-36]()

---

## Model Initialization

The pipeline initializes four distinct models during startup. The initialization sequence is shown in the following diagram:

```mermaid
graph LR
    subgraph "Initialization Sequence"
        START["args.parse_args()"]
        DEVICE["torch.device()"]
        
        START --> DEVICE
        
        DEVICE --> QTYPE["QuestionTypePredictor<br/>args.qtype_model_dir<br/>device"]
        DEVICE --> TEXT["TextQAPredictor<br/>args.text_qa_model_dir<br/>args.do_lower_case<br/>device<br/>mode"]
        DEVICE --> TABLE["TableQAPredictor<br/>args.table_qa_model_dir<br/>device<br/>mode"]
        DEVICE --> IMAGE["ImageQAPredictor<br/>checkpoint_path<br/>vilbert_dir<br/>img_info_path<br/>vocab_path<br/>device<br/>mode<br/>img_features_dir"]
    end
    
    subgraph "Mode Selection"
        METHOD_CHECK{"args.method == 'implicit_decomp'?"}
        CONTEXT_CHECK{"args.context_only?"}
        
        START --> METHOD_CHECK
        METHOD_CHECK -->|Yes| MODE_IMPL["mode='implicit_decomp'"]
        METHOD_CHECK -->|No| MODE_BASE["mode='base'"]
        
        START --> CONTEXT_CHECK
        CONTEXT_CHECK -->|Yes| MODE_CTX["mode='context_only'"]
        CONTEXT_CHECK -->|No| MODE_METHOD["mode=args.method"]
        
        MODE_IMPL --> TEXT
        MODE_BASE --> TEXT
        MODE_IMPL --> TABLE
        MODE_BASE --> TABLE
        MODE_CTX --> IMAGE
        MODE_METHOD --> IMAGE
    end
```

Each predictor is instantiated with method-specific configuration:

1. **QuestionTypePredictor**: Loads from `qtype_model_dir` without method-specific configuration
2. **TextQAPredictor**: Mode is `"implicit_decomp"` if `args.method == "implicit_decomp"`, otherwise `"base"`
3. **TableQAPredictor**: Mode selection follows the same logic as TextQAPredictor
4. **ImageQAPredictor**: Mode is `"context_only"` if `args.context_only` is True, otherwise uses `args.method`

The `mode` parameter controls how each model processes questions, particularly for multi-hop reasoning scenarios where bridge entities need to be incorporated.

**Sources:** [baselines/pipeline.py:233-252]()

---

## Prediction Workflow

The core prediction logic is implemented in the `predict()` function at [baselines/pipeline.py:161-217](). The workflow differs based on the selected inference method:

### Prediction Flow Diagram

```mermaid
graph TD
    START["predict(args, input, predictors)"]
    
    subgraph "Question Type Classification"
        ORACLE{"args.use_oracle_qtype<br/>or args.context_only?"}
        ORACLE -->|Yes| GOLD["question_type =<br/>input['gold_question_type']"]
        ORACLE -->|No| PRED["question_type =<br/>qtype_predictor.predict()"]
    end
    
    START --> ORACLE
    
    subgraph "Method Routing"
        METHOD{"args.method?"}
        GOLD --> METHOD
        PRED --> METHOD
    end
    
    subgraph "Auto Routing Method"
        AR_ROUTE{"question_type in<br/>TEXT/TABLE/IMAGE<br/>_SINGLE_HOP +<br/>_AS_SECOND_HOP?"}
        
        METHOD -->|"auto_routing"| AR_ROUTE
        
        AR_ROUTE -->|Text types| TEXT_PRED["text_qa_predictor.predict()"]
        AR_ROUTE -->|Table types| TABLE_PRED["table_qa_predictor.predict()"]
        AR_ROUTE -->|Image types| IMAGE_PRED["image_qa_predictor.predict()"]
        
        TEXT_PRED --> AR_RESULT["result['pred_answer']"]
        TABLE_PRED --> AR_RESULT
        IMAGE_PRED --> AR_RESULT
    end
    
    subgraph "Implicit Decomp Method"
        ID_FIRST{"First hop routing<br/>by question_type"}
        
        METHOD -->|"implicit_decomp"| ID_FIRST
        
        ID_FIRST -->|"TEXT_SINGLE_HOP +<br/>TEXT_AS_FIRST_HOP"| TEXT_HOP1["text_qa_predictor.predict()<br/>hop=0, bridge_entity=''"]
        ID_FIRST -->|"TABLE_SINGLE_HOP +<br/>TABLE_AS_FIRST_HOP"| TABLE_HOP1["table_qa_predictor.predict()<br/>hop=0, bridge_entity=''"]
        ID_FIRST -->|"IMAGE_SINGLE_HOP +<br/>IMAGE_AS_FIRST_HOP"| IMAGE_HOP1["image_qa_predictor.predict()"]
        
        TEXT_HOP1 --> CONVERT["first_hop_ans =<br/>list(first_hop_ans)<br/>if str"]
        TABLE_HOP1 --> CONVERT
        IMAGE_HOP1 --> CONVERT
        
        CONVERT --> ID_SECOND{"question_type in<br/>_AS_SECOND_HOP?"}
        
        ID_SECOND -->|"TEXT_AS_SECOND_HOP"| TEXT_HOP2["text_qa_predictor.predict()<br/>hop=1, bridge_entity=first_hop_ans"]
        ID_SECOND -->|"TABLE_AS_SECOND_HOP"| TABLE_HOP2["table_qa_predictor.predict()<br/>hop=1, bridge_entity=first_hop_ans"]
        ID_SECOND -->|"IMAGE_AS_SECOND_HOP"| IMAGE_HOP2["image_qa_predictor.predict()<br/>bridge_entities=first_hop_ans"]
        ID_SECOND -->|No| NO_SECOND["second_hop_ans = None"]
        
        TEXT_HOP2 --> ID_RESULT["result['pred_answer'] =<br/>second_hop_ans if not None<br/>else first_hop_ans"]
        TABLE_HOP2 --> ID_RESULT
        IMAGE_HOP2 --> ID_RESULT
        NO_SECOND --> ID_RESULT
    end
    
    AR_RESULT --> RETURN["return result"]
    ID_RESULT --> RETURN
```

### Auto Routing Method

In the `auto_routing` method, the question is routed directly to the modality that will produce the final answer:

1. Question type is predicted or loaded from gold labels
2. Type is checked against `TEXT_SINGLE_HOP_QUESTION_TYPES + TEXT_AS_SECOND_HOP_QUESTION_TYPES`, `TABLE_SINGLE_HOP_QUESTION_TYPES + TABLE_AS_SECOND_HOP_QUESTION_TYPES`, or `IMAGE_SINGLE_HOP_QUESTION_TYPES + IMAGE_AS_SECOND_HOP_QUESTION_TYPES`
3. Appropriate predictor's `predict()` method is called with the question and context
4. Result includes `pred_answer` and `pred_question_type`

**Sources:** [baselines/pipeline.py:169-180]()

### Implicit Decomposition Method

In the `implicit_decomp` method, multi-hop questions are decomposed into sequential reasoning steps:

1. **First Hop**: Question type determines which modality handles the first hop
   - Text, table, or image predictor is called with `hop=0` and `bridge_entity=""`
   - Result is converted to a list if it's a string
2. **Second Hop** (if applicable): If question type is in `*_AS_SECOND_HOP_QUESTION_TYPES`:
   - Appropriate second-hop predictor is called with `hop=1` and `bridge_entity=first_hop_ans`
   - For image QA, the parameter is `bridge_entities` instead of `bridge_entity`
3. **Final Answer**: `second_hop_ans` if it exists, otherwise `first_hop_ans`
4. Result includes `pred_first_hop_answer`, `pred_second_hop_answer`, `pred_answer`, and `pred_question_type`

**Sources:** [baselines/pipeline.py:181-216]()

---

## Input Preparation

Before calling the `predict()` function, the main loop prepares an input dictionary for each example:

```python
input = {
    "qid": example["qid"],
    "question": example["question"] if not args.context_only else "",
    "text_context": [text_docs[doc_id]["text"] for doc_id in example["metadata"]["text_doc_ids"]],
    "table_context": table_docs[example["metadata"]["table_id"]]["table"],
    "image_context": example["metadata"]["image_doc_ids"],
    "gold_question_type": example["metadata"]["type"] if args.use_oracle_qtype or args.context_only else None
}
```

Key aspects:
- **Question blanking**: If `context_only` is True, question is set to empty string
- **Text context**: List of text paragraphs retrieved by IDs
- **Table context**: Single table retrieved by ID
- **Image context**: List of image document IDs (not the actual images)
- **Gold question type**: Only included for oracle or context-only modes

**Sources:** [baselines/pipeline.py:267-274]()

---

## Output Files

The pipeline generates two JSON files in the specified output directory:

### 1. all_prediction_info.json

Comprehensive per-example results containing:

| Field | Description | Present When |
|-------|-------------|--------------|
| `qid` | Question ID | Always |
| `question` | Question text | Always |
| `pred_answer` | Predicted answer | Always |
| `pred_question_type` | Predicted question type | Always |
| `pred_first_hop_answer` | First hop prediction | `implicit_decomp` only |
| `pred_second_hop_answer` | Second hop prediction | `implicit_decomp` only |
| `gold_question_type` | Ground truth question type | If not `predict_only` |
| `gold_first_hop_modality` | Gold first hop modality | If not `predict_only` |
| `gold_first_hop_answer` | Gold first hop answer | If not `predict_only` |
| `gold_answer` | Ground truth answer | If not `predict_only` |
| `first_hop_em_score` | First hop exact match | If not `predict_only` |
| `first_hop_f1_score` | First hop F1 score | If not `predict_only` |
| `em_score` | Final answer exact match | If not `predict_only` |
| `f1_score` | Final answer F1 score | If not `predict_only` |

**Sources:** [baselines/pipeline.py:294-339](), [baselines/pipeline.py:344-345]()

### 2. predictions_.json

Simple mapping of question IDs to predicted answers:

```json
{
  "qid1": "answer1",
  "qid2": ["answer2a", "answer2b"],
  ...
}
```

This file is used for evaluation with the `evaluate_prediction_file()` function.

**Sources:** [baselines/pipeline.py:346-348]()

---

## Evaluation During Inference

If `--predict_only` is not specified, the pipeline computes evaluation metrics for each example during inference:

```mermaid
graph LR
    subgraph "Per-Example Scoring"
        EXAMPLE["example from all_examples"]
        GOLD["gold_answer =<br/>[str(it['answer'])<br/>for it in example['answers']]"]
        
        EXAMPLE --> GOLD
        
        PRED["pred_result['pred_answer']"]
        
        GOLD --> EM["list_em(pred, gold)"]
        GOLD --> F1["list_f1(pred, gold)"]
        PRED --> EM
        PRED --> F1
        
        EM --> STORE["all_results[qid]['em_score']"]
        F1 --> STORE
    end
    
    subgraph "First Hop Scoring"
        GOLD_HOP["gold_first_hop_answer =<br/>[str(it['answer'])<br/>for it in intermediate_answers[0]]"]
        PRED_HOP["pred_result['pred_first_hop_answer']"]
        
        GOLD_HOP --> HOP_EM["list_em(pred_hop, gold_hop)"]
        GOLD_HOP --> HOP_F1["list_f1(pred_hop, gold_hop)"]
        PRED_HOP --> HOP_EM
        PRED_HOP --> HOP_F1
        
        HOP_EM --> STORE_HOP["all_results[qid]['first_hop_em_score']"]
        HOP_F1 --> STORE_HOP
    end
    
    subgraph "Final Evaluation"
        STORE --> PRED_FILE["predictions_.json"]
        PRED_FILE --> EVAL["evaluate_prediction_file()"]
        EVAL --> AGGREGATE["Aggregated metrics by<br/>modality, hop type, question type"]
    end
```

The `list_em()` and `list_f1()` functions handle list-based answers with proper normalization. After all examples are processed, `evaluate_prediction_file()` aggregates the results and prints detailed breakdowns.

**Sources:** [baselines/pipeline.py:300-339](), [baselines/pipeline.py:350-355]()

---

## Error Handling

The pipeline includes exception handling to ensure that prediction failures for individual examples don't crash the entire run:

```python
try:
    pred_result = predict(...)
except Exception as e:
    print("==" * 10)
    print("Error message:")
    print(e)
    print(f"Question id: {qid}")
    pred_result = {
        "pred_answer": "Error in prediction",
        "pred_question_type": None
    }
```

Errors are logged to stdout with the question ID, and a default error result is stored. This allows the pipeline to continue processing remaining examples.

**Sources:** [baselines/pipeline.py:275-292]()

---

## Running Predictions on Test Set

To generate predictions for the test set without evaluation metrics (since test labels are not publicly available), use the `--predict_only` flag:

```bash
python pipeline.py \
  --qtype_model_dir downloads/checkpoints/qtype_clf_models/ \
  --text_qa_model_dir downloads/checkpoints/text_qa_models/implicit_decomp/ \
  --table_qa_model_dir downloads/checkpoints/table_qa_models/implicit_decomp/ \
  --image_qa_model_path downloads/checkpoints/image_qa_models/implicit_decomp/model.pt \
  --image_qa_vocab downloads/checkpoints/image_qa_models/vocab.pickle \
  --image_features_dir downloads/checkpoints/img_features/ \
  --data_dir downloads/MMQA/ \
  --test_file MMQA_test.jsonl \
  --output_dir output/results/implicit_decomp_test/ \
  --do_lower_case \
  --method implicit_decomp \
  --predict_only
```

With this flag, the pipeline will:
1. Skip all metric computation logic
2. Only generate `predictions_.json` and `all_prediction_info.json`
3. Omit gold labels and scores from output files
4. Not call `evaluate_prediction_file()`

**Sources:** [baselines/README.md:36](), [baselines/pipeline.py:113-115](), [baselines/pipeline.py:300-355]()

---

## Oracle Experiments

For diagnostic purposes, you can run the pipeline with oracle question types using `--use_oracle_qtype`:

```bash
python pipeline.py \
  ... \
  --use_oracle_qtype
```

This bypasses the question type classifier and uses ground truth types from `example["metadata"]["type"]`. This is useful for:
- Measuring the upper bound performance if question type classification were perfect
- Debugging individual modality-specific QA models
- Understanding the impact of question type classification errors

**Sources:** [baselines/pipeline.py:102-105](), [baselines/pipeline.py:164-167]()

---

## Context-Only Baseline

The context-only baseline is a special mode that ignores the question entirely:

```bash
python pipeline.py \
  ... \
  --context_only \
  --method auto_routing
```

When `--context_only` is True:
1. Questions are replaced with empty strings in the input
2. Gold question types are always used (oracle mode is forced)
3. Image QA predictor is initialized with `mode="context_only"`

This baseline measures how much can be answered from context alone without reading the question, serving as a lower bound for model performance.

**Sources:** [baselines/pipeline.py:107-110](), [baselines/pipeline.py:269](), [baselines/pipeline.py:249](), [baselines/scripts/run_pipeline.sh:35-49]()

---

