<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/multimodalqa · extra page Table QA Prediction Logic · fetched 2026-10-26 -->

# Table QA Prediction Logic

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [baselines/table_qa/table_qa_utils.py](baselines/table_qa/table_qa_utils.py)

</details>



## Purpose and Scope

This document explains the prediction logic used by the Table QA model to convert raw model outputs (cell scores and answer type logits) into final answers. It covers the `compute_predictions_with_cell_logits` function and associated logic in [baselines/table_qa/table_qa_utils.py]().

For information about the Table QA model's inference interface and operational modes, see [Table QA Inference](#5.2.1). For the broader context of how Table QA fits into the system, see [Baseline Models](#5).

**Sources:** [baselines/table_qa/table_qa_utils.py:1-104]()

---

## Overview

The Table QA prediction logic transforms model outputs into structured answers through a multi-stage process:

1. **Answer Type Selection**: Determine whether the answer is yes/no, count, sum, mean, or cell selection
2. **Cell Selection**: Identify relevant table cells based on probability thresholds
3. **Answer Construction**: Apply answer-type-specific logic to produce the final answer
4. **Output Generation**: Write predictions and diagnostic information to JSON files

```mermaid
graph TD
    ModelOutputs["Model Outputs<br/>(cell_scores, answer_type_logits)"]
    
    ModelOutputs --> AnswerType["Answer Type Selection<br/>ans_id2type_map"]
    AnswerType --> YesNo{"Answer Type?"}
    
    YesNo -->|"yes/no"| Direct["Direct Answer<br/>Return 'yes' or 'no'"]
    YesNo -->|"Other"| CellSelect["Cell Selection<br/>cell_selection_thresh"]
    
    CellSelect --> CellFilter["Filter cells by threshold<br/>or select top cell"]
    CellFilter --> AnsTypeLogic{"Answer Type?"}
    
    AnsTypeLogic -->|"count"| Count["Count Logic<br/>len(selected_cells)"]
    AnsTypeLogic -->|"sum"| Sum["Sum Logic<br/>sum(numbers from cells)"]
    AnsTypeLogic -->|"mean"| Mean["Mean Logic<br/>sum/count"]
    AnsTypeLogic -->|"cell"| CellList["Cell List<br/>selected_cell_strings"]
    
    Count --> FinalAnswer["Final Answer"]
    Sum --> FinalAnswer
    Mean --> FinalAnswer
    CellList --> FinalAnswer
    Direct --> FinalAnswer
    
    FinalAnswer --> OutputFiles["Output Files<br/>predictions.json<br/>predictions.json.info.json"]
```

**Diagram: Table QA Prediction Pipeline**

**Sources:** [baselines/table_qa/table_qa_utils.py:17-104]()

---

## Data Structures

### PredictionResultForCells

The `PredictionResultForCells` class encapsulates the raw outputs from the Table QA model for a single example.

| Field | Type | Description |
|-------|------|-------------|
| `unique_id` | int | Identifier linking result to feature/example |
| `cell_scores` | list[float] | Probability scores for each table cell |
| `answer_type_logits` | list[float] | Logits for each answer type |

This class serves as an intermediate representation between model outputs and final predictions. It is instantiated during inference and passed to `compute_predictions_with_cell_logits`.

**Sources:** [baselines/table_qa/table_qa_utils.py:10-14]()

---

## Main Prediction Function

### Function Signature

```python
compute_predictions_with_cell_logits(
    all_examples,
    all_features,
    all_results,
    output_prediction_file=None,
    cell_selection_thresh=0.5
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `all_examples` | list | Required | Dataset examples with table cells and metadata |
| `all_features` | list | Required | Tokenized features with cell position mappings |
| `all_results` | list[PredictionResultForCells] | Required | Model outputs (cell scores, answer type logits) |
| `output_prediction_file` | str | None | Path to write predictions JSON |
| `cell_selection_thresh` | float | 0.5 | Threshold for cell selection (probability cutoff) |

### Return Value

Returns an `OrderedDict` mapping `qas_id` to final answer strings or lists.

**Sources:** [baselines/table_qa/table_qa_utils.py:17-23]()

---

## Prediction Processing Flow

### Index Mapping Construction

The function begins by constructing lookup structures to efficiently access features and results:

```mermaid
graph LR
    AllFeatures["all_features<br/>(list)"] --> BuildMap["Build Mappings<br/>(lines 28-34)"]
    AllResults["all_results<br/>(list)"] --> BuildMap
    
    BuildMap --> ExampleToFeatures["example_index_to_features<br/>(defaultdict)"]
    BuildMap --> UniqueToResult["unique_id_to_result<br/>(dict)"]
    
    ExampleToFeatures --> Iteration["Per-Example Iteration<br/>(line 39)"]
    UniqueToResult --> Iteration
```

**Diagram: Index Mapping Construction**

These mappings enable efficient lookup during the per-example processing loop:
- `example_index_to_features`: Maps example indices to their associated features (handles cases where one example maps to multiple features)
- `unique_id_to_result`: Maps feature unique IDs to their prediction results

**Sources:** [baselines/table_qa/table_qa_utils.py:28-34]()

---

## Answer Type Determination

For each example, the system first determines the predicted answer type by aggregating logits across all features:

```mermaid
graph TD
    Example["Example<br/>(with features)"] --> Iterate["Iterate Features<br/>(line 44)"]
    Iterate --> ExtractLogits["Extract answer_type_logits<br/>(line 46)"]
    
    ExtractLogits --> Convert["Convert to (type, logit) pairs<br/>using ans_id2type_map<br/>(line 47)"]
    Convert --> Sort["Sort by logit descending<br/>(line 48)"]
    Sort --> Select["Select highest logit<br/>pred_ans_type = ans_type_logits[0][0]<br/>(line 49)"]
    
    Select --> Store["Store answer_type_preds<br/>in prediction_info<br/>(line 51)"]
```

**Diagram: Answer Type Selection Process**

The `ans_id2type_map` (defined at [baselines/table_qa/table_qa_utils.py:7]()) maps integer indices to answer type strings from the `data_reader` module. Supported types include:
- `"yes"` - Binary affirmative
- `"no"` - Binary negative  
- `"count"` - Count of matching cells
- `"sum"` - Sum of numeric values
- `"mean"` - Average of numeric values
- Cell selection (implicit default)

**Sources:** [baselines/table_qa/table_qa_utils.py:43-51](), [baselines/table_qa/table_qa_utils.py:7]()

---

## Cell Selection Logic

For non-yes/no answers, the system selects relevant table cells based on their probability scores:

```mermaid
graph TD
    PredAnsType{"pred_ans_type"}
    PredAnsType -->|"yes or no"| DirectReturn["Return answer directly<br/>(lines 53-54)"]
    PredAnsType -->|"Other types"| CollectCells["Collect Cell Scores<br/>(lines 56-65)"]
    
    CollectCells --> MapToOrig["Map cell_idx to orig_cell_pos<br/>using cell_to_orig_pos_map"]
    MapToOrig --> SkipPadding["Skip padding cells<br/>orig_cell_pos == (-1, -1)<br/>(line 61)"]
    MapToOrig --> GetString["Get cell string from<br/>example.table_cells[row][col]<br/>(line 64)"]
    
    GetString --> StorePairs["Store (cell_string, cell_prob)<br/>(line 65)"]
    StorePairs --> SortProbs["Sort by prob descending<br/>(line 67)"]
    
    SortProbs --> ApplyThresh["Apply cell_selection_thresh<br/>(line 70)"]
    ApplyThresh --> HasCells{"Has cells >= thresh?"}
    
    HasCells -->|"Yes"| UseFilteerd["Use filtered cells<br/>(line 70)"]
    HasCells -->|"No"| UseTop["Use top cell only<br/>(lines 72-73)"]
```

**Diagram: Cell Selection and Filtering Process**

### Cell Selection Threshold

The `cell_selection_thresh` parameter (default 0.5) acts as a probability cutoff:
- Cells with `prob >= cell_selection_thresh` are selected
- If no cells meet the threshold, the single highest-probability cell is selected as a fallback

This threshold provides a tunable trade-off between precision (high threshold) and recall (low threshold).

**Sources:** [baselines/table_qa/table_qa_utils.py:53-74]()

---

## Answer Type-Specific Processing

After cell selection, the final answer is constructed based on the predicted answer type:

### Yes/No Answers

```python
if pred_ans_type in ["yes", "no"]:
    final_answer = pred_ans_type
```

These answers bypass cell selection entirely and return the type name directly.

### Count Answers

```python
if pred_ans_type == "count":
    final_answer = str(len(selected_cell_strings))
```

Count answers return the number of selected cells as a string.

### Sum and Mean Answers

```mermaid
graph TD
    SelectedCells["selected_cell_strings"] --> ExtractNums["Extract numbers from each cell<br/>extract_numbers_from_str<br/>(lines 79-80)"]
    
    ExtractNums --> FilterSingle["Keep only cells with<br/>exactly 1 number<br/>(line 81)"]
    FilterSingle --> HasNums{"answer_numbers<br/>non-empty?"}
    
    HasNums -->|"Yes"| ComputeSum["Compute sum<br/>sum(answer_numbers)<br/>(line 84)"]
    HasNums -->|"No"| Fallback["Fallback to cell strings<br/>(line 87)"]
    
    ComputeSum --> CheckType{"Answer Type?"}
    CheckType -->|"sum"| ReturnSum["Return str(sum_answer)<br/>(line 85)"]
    CheckType -->|"mean"| ReturnMean["Return str(sum/count)<br/>(line 85)"]
    
    ReturnSum --> FinalAnswer["final_answer"]
    ReturnMean --> FinalAnswer
    Fallback --> FinalAnswer
```

**Diagram: Sum and Mean Answer Processing**

The `extract_numbers_from_str` function (from `common_utils`) extracts numeric values from cell text. Key behaviors:
- Only cells with exactly one number are included (avoids ambiguity)
- If no valid numbers are found, falls back to returning the cell strings
- Mean is computed as `sum / len(answer_numbers)`

### Cell List Answers (Default)

```python
else:
    final_answer = selected_cell_strings
```

When the answer type is not recognized or indicates direct cell selection, the list of selected cell strings is returned.

**Sources:** [baselines/table_qa/table_qa_utils.py:75-90]()

---

## Output Format

### Predictions File

The main predictions file (`output_prediction_file`) contains a JSON mapping of question IDs to answers:

```json
{
    "qid_12345": "yes",
    "qid_12346": "42",
    "qid_12347": ["New York", "Los Angeles"],
    "qid_12348": "125.5"
}
```

Answers may be:
- Strings (for yes/no, count, sum, mean)
- Lists of strings (for cell selection)

### Prediction Info File

A companion file (`output_prediction_file + ".info.json"`) stores detailed diagnostic information:

```json
{
    "qid_12345": {
        "answer_type_preds": [
            ["yes", 4.23],
            ["no", -1.45],
            ["count", -2.78],
            ...
        ],
        "cell_probs": [
            ["Cell Value A", 0.85],
            ["Cell Value B", 0.72],
            ...
        ],
        "final_answer": "yes"
    }
}
```

| Field | Description |
|-------|-------------|
| `answer_type_preds` | Sorted list of (type, logit) pairs |
| `cell_probs` | Sorted list of (cell_string, probability) pairs |
| `final_answer` | The computed final answer |

This information is valuable for error analysis and debugging model predictions.

**Sources:** [baselines/table_qa/table_qa_utils.py:91-102]()

---

## Integration with Inference Pipeline

The `compute_predictions_with_cell_logits` function is called from the Table QA inference pipeline after model forward passes are complete. The typical call flow is:

```mermaid
graph LR
    InferenceModel["TableInferenceModel<br/>(from 5.2.1)"] --> ForwardPass["Model Forward Passes<br/>Generate cell_scores<br/>and answer_type_logits"]
    
    ForwardPass --> CollectResults["Collect PredictionResultForCells<br/>objects"]
    
    CollectResults --> ComputePreds["compute_predictions_with_cell_logits<br/>(table_qa_utils.py)"]
    
    ComputePreds --> PredictionsDict["Predictions Dict<br/>(qas_id -> answer)"]
    
    PredictionsDict --> Evaluation["Evaluation<br/>(evaluate.py)"]
```

**Diagram: Integration with Inference Pipeline**

The function decouples model architecture from answer construction logic, allowing the same prediction logic to be used across different model variants or training configurations.

**Sources:** [baselines/table_qa/table_qa_utils.py:17-104]()

---

## Key Design Decisions

### Threshold-Based Cell Selection

The `cell_selection_thresh` parameter enables flexible cell selection strategies:
- **Higher thresholds (0.7-0.9)**: More precise, fewer cells selected
- **Default threshold (0.5)**: Balanced precision/recall
- **Lower thresholds (0.2-0.4)**: Higher recall, more cells selected

The fallback to the top cell ensures the system always produces an answer.

### Answer Type Hierarchy

The answer type determination uses a strict priority order based on model logits, not heuristics. This ensures:
- Consistent behavior across examples
- Model-driven decisions (the model learns when to use each type)
- Explicit type prediction in training data guides the model

### Number Extraction Strictness

The sum/mean logic only considers cells with exactly one number to avoid ambiguity. For example:
- `"42"` → Valid, extracts 42
- `"42.5 million"` → Valid if extractor handles it
- `"42 and 43"` → Invalid, skipped (ambiguous)

This conservative approach prioritizes correctness over recall.

**Sources:** [baselines/table_qa/table_qa_utils.py:17-90]()

---

