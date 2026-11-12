<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/evaluate · page 4 Evaluator System · fetched 2026-10-26 -->

# Evaluator System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/a_quick_tour.mdx](docs/source/a_quick_tour.mdx)
- [docs/source/base_evaluator.mdx](docs/source/base_evaluator.mdx)
- [docs/source/choosing_a_metric.mdx](docs/source/choosing_a_metric.mdx)
- [docs/source/considerations.mdx](docs/source/considerations.mdx)
- [docs/source/index.mdx](docs/source/index.mdx)
- [docs/source/package_reference/evaluator_classes.mdx](docs/source/package_reference/evaluator_classes.mdx)
- [src/evaluate/__init__.py](src/evaluate/__init__.py)
- [src/evaluate/evaluator/__init__.py](src/evaluate/evaluator/__init__.py)
- [src/evaluate/evaluator/audio_classification.py](src/evaluate/evaluator/audio_classification.py)
- [src/evaluate/evaluator/base.py](src/evaluate/evaluator/base.py)
- [src/evaluate/evaluator/image_classification.py](src/evaluate/evaluator/image_classification.py)
- [src/evaluate/evaluator/question_answering.py](src/evaluate/evaluator/question_answering.py)
- [src/evaluate/evaluator/text_classification.py](src/evaluate/evaluator/text_classification.py)
- [src/evaluate/evaluator/token_classification.py](src/evaluate/evaluator/token_classification.py)
- [src/evaluate/evaluator/utils.py](src/evaluate/evaluator/utils.py)
- [src/evaluate/utils/logging.py](src/evaluate/utils/logging.py)
- [tests/test_evaluator.py](tests/test_evaluator.py)

</details>



The Evaluator System provides a high-level abstraction for automated model evaluation that eliminates the need for manual inference loops, preprocessing, and postprocessing. It enables users to evaluate models on datasets with metrics using a simple API that handles the entire evaluation workflow internally.

For information about individual evaluation modules (metrics, comparisons, measurements), see [Evaluation Module Base Classes](#3.2). For multi-task benchmarking across multiple datasets, see [Evaluation Suite](#4.2).

## Overview

The Evaluator System transforms the typical multi-step evaluation process—loading data, initializing pipelines, running inference, processing predictions, computing metrics—into a single `compute()` call. Users specify a task type, model, dataset, and metric, and the evaluator handles all intermediate steps automatically.

The system is implemented as a factory pattern that routes tasks to specialized evaluator implementations. Each task-specific evaluator understands the data format, pipeline requirements, and prediction post-processing needs for its domain.

**Sources:** [src/evaluate/evaluator/__init__.py:113-141](), [docs/source/base_evaluator.mdx:1-17]()

## System Architecture

```mermaid
graph TB
    User["User Code"]
    Factory["evaluator(task)<br/>Factory Function"]
    
    subgraph "Task-Specific Evaluators"
        TC["TextClassificationEvaluator"]
        IC["ImageClassificationEvaluator"]
        QA["QuestionAnsweringEvaluator"]
        TOK["TokenClassificationEvaluator"]
        TG["TextGenerationEvaluator"]
        T2T["Text2TextGenerationEvaluator"]
        SUM["SummarizationEvaluator"]
        TR["TranslationEvaluator"]
        ASR["AutomaticSpeechRecognitionEvaluator"]
        AC["AudioClassificationEvaluator"]
    end
    
    Base["Evaluator<br/>Base Class"]
    
    Pipeline["transformers.Pipeline"]
    Dataset["datasets.Dataset"]
    Metric["EvaluationModule"]
    
    User --> Factory
    Factory --> TC
    Factory --> IC
    Factory --> QA
    Factory --> TOK
    Factory --> TG
    Factory --> T2T
    Factory --> SUM
    Factory --> TR
    Factory --> ASR
    Factory --> AC
    
    TC --> Base
    IC --> Base
    QA --> Base
    TOK --> Base
    TG --> Base
    T2T --> Base
    SUM --> Base
    TR --> Base
    ASR --> Base
    AC --> Base
    
    Base --> Pipeline
    Base --> Dataset
    Base --> Metric
```

The architecture consists of three layers: a factory function that creates evaluators, task-specific evaluator implementations that handle domain-specific logic, and a base class that provides common evaluation infrastructure. All evaluators integrate with `transformers.Pipeline` for inference, `datasets.Dataset` for data handling, and `EvaluationModule` for metric computation.

**Sources:** [src/evaluate/evaluator/__init__.py:38-79](), [src/evaluate/evaluator/base.py:102-108]()

## Factory Pattern and Task Routing

### Task Registration

The evaluator system maintains a registry mapping task names to evaluator implementations and default metrics:

```mermaid
graph LR
    SUPPORTED_EVALUATOR_TASKS["SUPPORTED_EVALUATOR_TASKS<br/>Dictionary"]
    
    TC_Entry["'text-classification':<br/>TextClassificationEvaluator<br/>default: 'accuracy'"]
    IC_Entry["'image-classification':<br/>ImageClassificationEvaluator<br/>default: 'accuracy'"]
    QA_Entry["'question-answering':<br/>QuestionAnsweringEvaluator<br/>default: 'squad'"]
    TOK_Entry["'token-classification':<br/>TokenClassificationEvaluator<br/>default: 'seqeval'"]
    
    SUPPORTED_EVALUATOR_TASKS --> TC_Entry
    SUPPORTED_EVALUATOR_TASKS --> IC_Entry
    SUPPORTED_EVALUATOR_TASKS --> QA_Entry
    SUPPORTED_EVALUATOR_TASKS --> TOK_Entry
```

The `SUPPORTED_EVALUATOR_TASKS` dictionary at [src/evaluate/evaluator/__init__.py:38-79]() defines the mapping between task strings, evaluator implementations, and default metrics. Each entry specifies the class to instantiate and the metric to use if none is provided.

### Factory Function Flow

```mermaid
sequenceDiagram
    participant User
    participant evaluator_func as "evaluator(task)"
    participant check_task
    participant SUPPORTED_EVALUATOR_TASKS
    participant EvaluatorClass as "Task Evaluator Class"
    
    User->>evaluator_func: evaluator("text-classification")
    evaluator_func->>check_task: Validate task string
    check_task->>SUPPORTED_EVALUATOR_TASKS: Lookup task config
    SUPPORTED_EVALUATOR_TASKS-->>check_task: implementation, default_metric_name
    check_task-->>evaluator_func: Task config dict
    evaluator_func->>EvaluatorClass: Instantiate with task + default_metric
    EvaluatorClass-->>User: Return evaluator instance
```

The factory function performs task validation against both `transformers` pipeline tasks and evaluator-supported tasks, retrieves the appropriate implementation class, and instantiates it with the task name and default metric.

**Sources:** [src/evaluate/evaluator/__init__.py:113-141](), [src/evaluate/evaluator/__init__.py:89-111]()

## Execution Pipeline

The `Evaluator.compute()` method orchestrates a seven-stage pipeline that handles the complete evaluation workflow:

```mermaid
graph TB
    Input["User Input:<br/>model, data, metric"]
    
    Stage1["Stage 1: Load Data<br/>load_data()"]
    Stage2["Stage 2: Prepare Data<br/>prepare_data()"]
    Stage3["Stage 3: Initialize Pipeline<br/>prepare_pipeline()"]
    Stage4["Stage 4: Run Inference<br/>call_pipeline()"]
    Stage5["Stage 5: Process Predictions<br/>predictions_processor()"]
    Stage6["Stage 6: Compute Metrics<br/>compute_metric()"]
    Stage7["Stage 7: Return Results<br/>scores + performance stats"]
    
    Input --> Stage1
    Stage1 --> Stage2
    Stage2 --> Stage3
    Stage3 --> Stage4
    Stage4 --> Stage5
    Stage5 --> Stage6
    Stage6 --> Stage7
```

**Sources:** [src/evaluate/evaluator/base.py:218-279]()

### Stage 1: Load Data

The `load_data()` method handles two input formats:

| Input Type | Processing | Output |
|------------|-----------|--------|
| `str` (dataset name) | Calls `datasets.load_dataset()` with automatic split selection via `choose_split()` | `Dataset` object |
| `Dataset` object | Returns as-is (ignores `subset` and `split` parameters) | `Dataset` object |

The `choose_split()` function at [src/evaluate/evaluator/utils.py:21-38]() implements a priority-ordered split selection: `test` > `testing` > `eval` > `evaluation` > `validation` > `val` > `valid` > `dev` > `train` > `training`.

**Sources:** [src/evaluate/evaluator/base.py:350-388](), [src/evaluate/evaluator/utils.py:21-38]()

### Stage 2: Prepare Data

The `prepare_data()` method is abstract in the base class and implemented by each task-specific evaluator. It performs three operations:

1. **Column validation**: Verifies required columns exist using `check_required_columns()`
2. **Reference extraction**: Extracts ground truth labels into a dictionary
3. **Input structuring**: Wraps input columns in `DatasetColumn` or `DatasetColumnPair` objects to avoid loading entire columns into memory

For example, `TextClassificationEvaluator.prepare_data()` at [src/evaluate/evaluator/text_classification.py:65-80]() returns:
- `metric_inputs`: `{"references": data[label_column]}`
- `pipe_inputs`: `DatasetColumnPair(data, input_column, second_input_column, "text", "text_pair")`

**Sources:** [src/evaluate/evaluator/base.py:390-420](), [src/evaluate/evaluator/text_classification.py:65-80]()

### Stage 3: Initialize Pipeline

The `prepare_pipeline()` method creates a `transformers.Pipeline` from various input formats:

```mermaid
graph TB
    Input["model_or_pipeline<br/>+ tokenizer<br/>+ feature_extractor<br/>+ device"]
    
    Check1{"Is str or<br/>PreTrainedModel?"}
    Check2{"Is None?"}
    Check3{"Is Pipeline?"}
    
    Create1["pipeline(task, model=...,<br/>tokenizer=..., device=...)"]
    Create2["pipeline(task, device=...)"]
    Return["Return Pipeline"]
    
    Input --> Check1
    Check1 -->|Yes| Create1
    Check1 -->|No| Check2
    Check2 -->|Yes| Create2
    Check2 -->|No| Check3
    Check3 -->|Yes| Return
    
    Create1 --> Return
    Create2 --> Return
```

Device inference occurs via `_infer_device()` at [src/evaluate/evaluator/base.py:182-209](), which checks for CUDA availability (PyTorch) or GPU devices (TensorFlow), defaulting to CPU if unavailable.

**Sources:** [src/evaluate/evaluator/base.py:422-478](), [src/evaluate/evaluator/base.py:182-209]()

### Stage 4: Run Inference

The `call_pipeline()` method executes the pipeline on input data while tracking performance:

```mermaid
sequenceDiagram
    participant call_pipeline
    participant perf_counter
    participant Pipeline
    participant _compute_time_perf
    
    call_pipeline->>perf_counter: start_time = perf_counter()
    call_pipeline->>Pipeline: pipe(inputs, **PIPELINE_KWARGS)
    Pipeline-->>call_pipeline: predictions
    call_pipeline->>perf_counter: end_time = perf_counter()
    call_pipeline->>_compute_time_perf: Calculate metrics
    _compute_time_perf-->>call_pipeline: {total_time, samples_per_second, latency}
    call_pipeline-->>call_pipeline: Return predictions + perf_results
```

Performance metrics calculated at [src/evaluate/evaluator/base.py:163-179]():
- `total_time_in_seconds`: Total inference time
- `samples_per_second`: Throughput (num_samples / latency)
- `latency_in_seconds`: Per-sample latency (total_time / num_samples)

**Sources:** [src/evaluate/evaluator/base.py:511-515](), [src/evaluate/evaluator/base.py:163-179]()

### Stage 5: Process Predictions

The `predictions_processor()` method is abstract and task-specific. It transforms pipeline outputs into metric-compatible format. Examples:

| Evaluator | Input Format | Processing | Output Format |
|-----------|--------------|------------|---------------|
| `TextClassificationEvaluator` | `[{"label": "POSITIVE"}, ...]` | Map labels via `label_mapping` | `{"predictions": [1, ...]}` |
| `ImageClassificationEvaluator` | `[[{"label": "cat", "score": 0.9}, ...], ...]` | Extract max score label, apply mapping | `{"predictions": [0, ...]}` |
| `QuestionAnsweringEvaluator` | `[{"answer": "text", "score": 0.95}, ...]` | Extract answer text, add no_answer_probability if SQuAD v2 | `{"predictions": [{"prediction_text": "text", "id": "...", ...}]}` |
| `TokenClassificationEvaluator` | `[[{"entity": "B-LOC", "start": 0}, ...], ...]` | Align token predictions to word boundaries | `{"predictions": [["B-LOC", "O", ...], ...]}` |

**Sources:** [src/evaluate/evaluator/text_classification.py:82-87](), [src/evaluate/evaluator/image_classification.py:62-66](), [src/evaluate/evaluator/question_answering.py:135-142](), [src/evaluate/evaluator/token_classification.py:99-136]()

### Stage 6: Compute Metrics

The `compute_metric()` method supports two strategies:

```mermaid
graph TB
    compute_metric["compute_metric()"]
    
    Check{"strategy ==<br/>'bootstrap'?"}
    
    Simple["Call metric.compute()<br/>with metric_inputs"]
    Bootstrap1["Call metric.compute()<br/>with metric_inputs"]
    Bootstrap2["Call _compute_confidence_interval()<br/>using scipy.stats.bootstrap"]
    Combine["Combine score with<br/>confidence_interval + standard_error"]
    
    compute_metric --> Check
    Check -->|"No ('simple')"| Simple
    Check -->|Yes| Bootstrap1
    Bootstrap1 --> Bootstrap2
    Bootstrap2 --> Combine
    
    Simple --> Result["Return metric dict"]
    Combine --> Result
```

Bootstrap strategy (when `strategy="bootstrap"`) uses `scipy.stats.bootstrap` at [src/evaluate/evaluator/base.py:125-160]() to compute confidence intervals via resampling. Each metric key gets wrapped in a dictionary containing:
- `score`: Original metric value
- `confidence_interval`: Tuple of (low, high) bounds
- `standard_error`: Bootstrap standard error

**Sources:** [src/evaluate/evaluator/base.py:517-544](), [src/evaluate/evaluator/base.py:125-160]()

### Stage 7: Return Results

Results combine metric scores with performance statistics:

```python
{
    "accuracy": 0.918,                    # Metric result(s)
    "total_time_in_seconds": 12.676,      # Performance metrics
    "samples_per_second": 78.887,
    "latency_in_seconds": 0.013
}
```

Or with bootstrap:

```python
{
    "accuracy": {
        "score": 0.918,
        "confidence_interval": (0.906, 0.941),
        "standard_error": 0.009
    },
    "total_time_in_seconds": 12.676,
    "samples_per_second": 78.887,
    "latency_in_seconds": 0.013
}
```

**Sources:** [src/evaluate/evaluator/base.py:273-279](), [docs/source/base_evaluator.mdx:76-83]()

## Task-Specific Evaluators

The system provides ten specialized evaluator implementations:

| Task | Evaluator Class | Default Metric | Key Parameters | Special Processing |
|------|----------------|----------------|----------------|-------------------|
| `text-classification` | `TextClassificationEvaluator` | `accuracy` | `input_column`, `second_input_column`, `label_column`, `label_mapping` | Supports two-column input (MNLI-style) via `DatasetColumnPair` |
| `image-classification` | `ImageClassificationEvaluator` | `accuracy` | `input_column`, `label_column`, `label_mapping` | Extracts highest-confidence prediction from multi-class output |
| `question-answering` | `QuestionAnsweringEvaluator` | `squad` | `question_column`, `context_column`, `id_column`, `label_column`, `squad_v2_format` | Auto-detects SQuAD v2 format, handles impossible answers |
| `token-classification` | `TokenClassificationEvaluator` | `seqeval` | `input_column`, `label_column`, `join_by` | Joins tokens with `join_by`, aligns subword predictions to words |
| `text-generation` | `TextGenerationEvaluator` | `word_count` | Standard evaluator params | Flattens multi-sequence outputs from beam search |
| `text2text-generation` | `Text2TextGenerationEvaluator` | `bleu` | Standard evaluator params | Base class for summarization/translation |
| `summarization` | `SummarizationEvaluator` | `rouge` | Standard evaluator params | Alias for `Text2TextGenerationEvaluator` |
| `translation` | `TranslationEvaluator` | `bleu` | Standard evaluator params | Alias for `Text2TextGenerationEvaluator` |
| `automatic-speech-recognition` | `AutomaticSpeechRecognitionEvaluator` | `wer` | `input_column`, `label_column` | Handles audio file paths and raw waveforms |
| `audio-classification` | `AudioClassificationEvaluator` | `accuracy` | `input_column`, `label_column`, `label_mapping` | Handles audio file paths and raw waveforms |

### Specialized Behaviors

**TokenClassificationEvaluator** performs word-to-character offset mapping at [src/evaluate/evaluator/token_classification.py:138-159]() to align subword tokenizer predictions back to original word boundaries. The `words_to_offsets()` method computes start/end character positions for each word, then `predictions_processor()` maps token-level predictions to these positions.

**QuestionAnsweringEvaluator** includes automatic SQuAD format detection at [src/evaluate/evaluator/question_answering.py:121-133]() by checking if any answers have empty text lists. It sets `handle_impossible_answer=True` in pipeline kwargs for SQuAD v2 format, enabling the model to predict "no answer".

**Sources:** [src/evaluate/evaluator/__init__.py:38-79](), [src/evaluate/evaluator/token_classification.py:84-273](), [src/evaluate/evaluator/question_answering.py:75-237]()

## Input Format Flexibility

### Model/Pipeline Input Formats

The evaluator accepts four input formats for the model:

```mermaid
graph TB
    Input["model_or_pipeline parameter"]
    
    Format1["str: Hub model ID<br/>'bert-base-uncased'"]
    Format2["PreTrainedModel/TFPreTrainedModel<br/>model object"]
    Format3["Pipeline object<br/>pre-initialized pipeline"]
    Format4["Callable<br/>custom prediction function"]
    
    Action1["Create pipeline from Hub"]
    Action2["Create pipeline from model"]
    Action3["Use pipeline directly"]
    Action4["Use callable directly"]
    
    Input --> Format1
    Input --> Format2
    Input --> Format3
    Input --> Format4
    
    Format1 --> Action1
    Format2 --> Action2
    Format3 --> Action3
    Format4 --> Action4
    
    Action1 --> Result["Pipeline ready for inference"]
    Action2 --> Result
    Action3 --> Result
    Action4 --> Result
```

Example usage from [docs/source/base_evaluator.mdx:37-69]():

```python
# 1. Pass model name/path
evaluator.compute(model_or_pipeline="lvwerra/distilbert-imdb", data=data)

# 2. Pass model object
model = AutoModelForSequenceClassification.from_pretrained("lvwerra/distilbert-imdb")
evaluator.compute(model_or_pipeline=model, data=data)

# 3. Pass pipeline
pipe = pipeline("text-classification", model="lvwerra/distilbert-imdb")
evaluator.compute(model_or_pipeline=pipe, data=data)

# 4. Pass custom callable (must follow pipeline signature)
def custom_predictor(inputs):
    # Custom inference logic
    return predictions
evaluator.compute(model_or_pipeline=custom_predictor, data=data)
```

**Sources:** [src/evaluate/evaluator/base.py:422-478](), [docs/source/base_evaluator.mdx:37-69]()

### Dataset Input Formats

Two input formats are supported for datasets:

| Input Type | Processing | Use Case |
|------------|-----------|----------|
| `str` | Loads dataset from Hub via `load_dataset(data, name=subset, split=split)` | Evaluate on standard benchmarks |
| `Dataset` | Uses pre-loaded dataset directly | Custom datasets, preprocessed data |

### Metric Input Formats

Three metric input formats are supported:

| Input Type | Processing | Example |
|------------|-----------|---------|
| `None` | Uses `default_metric_name` from evaluator | `evaluator.compute(data=data)` |
| `str` | Loads metric via `load(metric)` | `evaluator.compute(metric="f1", data=data)` |
| `EvaluationModule` | Uses pre-loaded metric directly | `evaluator.compute(metric=load("f1"), data=data)` |
| `CombinedEvaluations` | Evaluates multiple metrics | `evaluator.compute(metric=combine(["accuracy", "f1"]), data=data)` |

**Sources:** [src/evaluate/evaluator/base.py:480-509]()

## Advanced Features

### Bootstrap Confidence Intervals

The bootstrap strategy uses `scipy.stats.bootstrap` to estimate confidence intervals via resampling:

```mermaid
sequenceDiagram
    participant User
    participant compute_metric
    participant metric.compute
    participant _compute_confidence_interval
    participant scipy_bootstrap
    
    User->>compute_metric: strategy="bootstrap", n_resamples=100
    compute_metric->>metric.compute: Compute base score
    metric.compute-->>compute_metric: {accuracy: 0.85}
    compute_metric->>_compute_confidence_interval: metric, metric_inputs, ["accuracy"]
    
    loop For each metric key
        _compute_confidence_interval->>scipy_bootstrap: Resample and compute
        scipy_bootstrap-->>_compute_confidence_interval: confidence_interval, standard_error
    end
    
    _compute_confidence_interval-->>compute_metric: Bootstrap results
    compute_metric-->>User: {accuracy: {score: 0.85, confidence_interval: (0.82, 0.88), standard_error: 0.015}}
```

The bootstrap implementation at [src/evaluate/evaluator/base.py:125-160]() wraps the metric compute function to work with `scipy.stats.bootstrap`, which requires positional arguments. Parameters:
- `n_resamples`: Number of bootstrap samples (default: 9999)
- `confidence_level`: Confidence level for intervals (default: 0.95)
- `random_state`: Random seed for reproducibility

**Sources:** [src/evaluate/evaluator/base.py:125-160](), [docs/source/base_evaluator.mdx:217-255]()

### Device Management

Device selection follows this priority:

```mermaid
graph TB
    Start["Device parameter"]
    
    Check1{"device<br/>specified?"}
    Check2{"PyTorch<br/>available?"}
    Check3{"CUDA<br/>available?"}
    Check4{"TensorFlow<br/>available?"}
    Check5{"GPU<br/>available?"}
    
    Start --> Check1
    Check1 -->|Yes| Use["Use specified device"]
    Check1 -->|No| Check2
    Check2 -->|Yes| Check3
    Check2 -->|No| Check4
    Check3 -->|Yes| GPU["device = 0 (first GPU)"]
    Check3 -->|No| CPU1["device = -1 (CPU)"]
    Check4 -->|Yes| Check5
    Check4 -->|No| CPU2["device = -1 (CPU)"]
    Check5 -->|Yes| GPU
    Check5 -->|No| CPU1
```

The `_infer_device()` method at [src/evaluate/evaluator/base.py:182-209]() attempts to detect GPU availability via PyTorch first, then TensorFlow. It returns `0` for the first GPU or `-1` for CPU.

Device mismatch validation at [src/evaluate/evaluator/base.py:282-293]() raises an error if the user passes a `device` parameter that conflicts with a pre-initialized pipeline's device.

**Sources:** [src/evaluate/evaluator/base.py:182-209](), [src/evaluate/evaluator/base.py:282-293](), [docs/source/base_evaluator.mdx:72-73]()

### Performance Tracking

All evaluations automatically track inference performance:

| Metric | Calculation | Purpose |
|--------|-------------|---------|
| `total_time_in_seconds` | `end_time - start_time` | Overall inference duration |
| `samples_per_second` | `num_samples / total_time` | Throughput measurement |
| `latency_in_seconds` | `total_time / num_samples` | Per-sample latency |

Timing uses `time.perf_counter()` at [src/evaluate/evaluator/base.py:511-515]() for high-resolution measurements. These metrics help identify bottlenecks and compare model efficiency.

**Note:** Performance metrics include all pipeline overhead (tokenization, post-processing) and depend on hardware, so they should be compared under consistent conditions.

**Sources:** [src/evaluate/evaluator/base.py:163-179](), [src/evaluate/evaluator/base.py:511-515](), [docs/source/base_evaluator.mdx:85-89]()

### Label Mapping

The `label_mapping` parameter resolves mismatches between model output labels and dataset labels:

```python
# Dataset has integer labels: 0, 1
# Model outputs string labels: "NEGATIVE", "POSITIVE"
evaluator.compute(
    model_or_pipeline="lvwerra/distilbert-imdb",
    data=data,
    label_mapping={"NEGATIVE": 0, "POSITIVE": 1}
)
```

Each task-specific evaluator applies the mapping in its `predictions_processor()` method before passing predictions to the metric. This enables evaluation of models trained with different label schemes than the evaluation dataset.

**Sources:** [src/evaluate/evaluator/text_classification.py:82-87](), [docs/source/base_evaluator.mdx:46-50]()

## Integration Points

### Transformers Pipeline Integration

The evaluator system relies heavily on `transformers.Pipeline` abstraction:

```mermaid
graph TB
    Evaluator["Evaluator.prepare_pipeline()"]
    
    Check{"Input type?"}
    
    String["str: model identifier"]
    Model["PreTrainedModel object"]
    PipeObj["Pipeline object"]
    Callable["Custom callable"]
    
    Create["pipeline(task, model, tokenizer,<br/>feature_extractor, device)"]
    Validate["Validate task matches"]
    
    Evaluator --> Check
    Check --> String
    Check --> Model
    Check --> PipeObj
    Check --> Callable
    
    String --> Create
    Model --> Create
    Create --> Validate
    PipeObj --> Validate
    Callable --> Validate
    
    Validate --> Ready["Pipeline/Callable ready"]
```

Task validation at [src/evaluate/evaluator/base.py:474-477]() ensures the pipeline's task matches the evaluator's task (with special handling for translation subtasks). Custom pipelines must implement the `__call__` interface expected by the task.

**Sources:** [src/evaluate/evaluator/base.py:422-478]()

### Datasets Integration

The system uses `datasets` library features:

| Feature | Usage | Location |
|---------|-------|----------|
| `load_dataset()` | Load datasets from Hub | [src/evaluate/evaluator/base.py:379]() |
| `get_dataset_split_names()` | Auto-detect available splits | [src/evaluate/evaluator/utils.py:22]() |
| `Dataset.features` | Validate column types | [src/evaluate/evaluator/token_classification.py:164-169]() |
| `DatasetColumn` wrapper | Lazy column access without loading into memory | [src/evaluate/evaluator/utils.py:4-19]() |

The `DatasetColumn` class at [src/evaluate/evaluator/utils.py:4-19]() wraps a dataset column to provide list-like access without loading data into memory—it fetches items on-demand during iteration, which is crucial for large datasets.

**Sources:** [src/evaluate/evaluator/base.py:350-388](), [src/evaluate/evaluator/utils.py:4-19]()

### Metric Loading Integration

Evaluators load metrics via the module loading system (see [Module Loading System](#3.1)):

```python
# In prepare_metric() at base.py:480-509
if metric is None:
    metric = load(self.default_metric_name)
elif isinstance(metric, str):
    metric = load(metric)
# else: metric is already an EvaluationModule
```

This enables seamless use of all Hub metrics, community metrics, and combined metrics via `combine()`.

**Sources:** [src/evaluate/evaluator/base.py:480-509]()

### Common Usage Patterns

**Simple evaluation:**
```python
from evaluate import evaluator
task_evaluator = evaluator("text-classification")
results = task_evaluator.compute(
    model_or_pipeline="distilbert-base-uncased-finetuned-sst-2-english",
    data="sst2",
    split="validation[:100]"
)
```

**Multi-metric evaluation:**
```python
import evaluate
results = task_evaluator.compute(
    model_or_pipeline="distilbert-base-uncased-finetuned-sst-2-english",
    data="sst2",
    metric=evaluate.combine(["accuracy", "f1", "precision", "recall"])
)
```

**Bootstrap confidence intervals:**
```python
results = task_evaluator.compute(
    model_or_pipeline="distilbert-base-uncased-finetuned-sst-2-english",
    data="sst2",
    strategy="bootstrap",
    n_resamples=100,
    confidence_level=0.95
)
```

**Sources:** [docs/source/base_evaluator.mdx:37-118](), [docs/source/a_quick_tour.mdx:244-289]()

---

