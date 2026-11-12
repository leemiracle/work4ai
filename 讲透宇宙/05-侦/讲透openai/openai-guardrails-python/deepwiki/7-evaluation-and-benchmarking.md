<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-guardrails-python · page 7 Evaluation and Benchmarking · fetched 2026-10-26 -->

# Evaluation and Benchmarking

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/assets/images/guardrails-python-config-screenshot-100pct-q70.webp](docs/assets/images/guardrails-python-config-screenshot-100pct-q70.webp)
- [docs/evals.md](docs/evals.md)
- [src/guardrails/evals/guardrail_evals.py](src/guardrails/evals/guardrail_evals.py)
- [tests/unit/evals/test_guardrail_evals.py](tests/unit/evals/test_guardrail_evals.py)

</details>



This document provides comprehensive documentation for the guardrail evaluation framework, which enables data-driven testing and optimization of guardrail performance. The evaluation system supports basic metrics calculation (precision, recall, F1) and advanced benchmarking workflows (ROC curves, model comparison, latency analysis).

For information about specific guardrail implementations being evaluated, see [Built-in Guardrails](#6). For runtime execution details, see [Runtime Execution](#3.5).

## Overview

The evaluation framework provides tools for measuring guardrail accuracy and performance against labeled datasets. The system supports two primary modes:

- **Evaluation Mode**: Calculate basic metrics (precision, recall, F1) for a single guardrail configuration
- **Benchmark Mode**: Compare multiple models with advanced metrics (ROC AUC, precision-at-recall), latency testing, and visualization

The framework is designed to work with any OpenAI-compatible API, including OpenAI, Azure OpenAI, Ollama, and vLLM.

**Core Components:**

| Component | File Path | Purpose |
|-----------|-----------|---------|
| CLI Entrypoint | [src/guardrails/evals/guardrail_evals.py]() | Main command-line interface and orchestration |
| Evaluation Engine | [src/guardrails/evals/core/async_engine.py]() | Asynchronous batch processing across pipeline stages |
| Basic Metrics | [src/guardrails/evals/core/calculator.py]() | Precision, recall, F1 calculation |
| Benchmark Metrics | [src/guardrails/evals/core/benchmark_calculator.py]() | ROC AUC, precision-at-recall thresholds |
| Latency Testing | [src/guardrails/evals/core/latency_tester.py]() | End-to-end performance measurement |
| Visualization | [src/guardrails/evals/core/visualizer.py]() | Chart and graph generation |
| Reporting | [src/guardrails/evals/core/benchmark_reporter.py]() | Summary tables and formatted output |

Sources: [README.md:95-145](), [docs/evals.md:1-201](), [src/guardrails/evals/README.md:1-222]()

## Evaluation Architecture

The evaluation system follows a modular architecture where the CLI orchestrates dataset loading, guardrail execution via the async engine, metrics calculation, and reporting.

### System Architecture Diagram

```mermaid
graph TB
    subgraph "CLI Interface"
        CLI["guardrail_evals.py<br/>GuardrailEval class"]
        Args["CLI Arguments:<br/>--config-path<br/>--dataset-path<br/>--mode<br/>--models<br/>--batch-size"]
    end
    
    subgraph "Data Layer"
        Config["guardrails_config.json<br/>PipelineBundles"]
        Dataset["data.jsonl<br/>id, data, expected_triggers"]
    end
    
    subgraph "Execution Engine"
        AsyncEngine["async_engine.py<br/>AsyncGuardrailEngine"]
        Runtime["runtime.py<br/>run_guardrails()<br/>instantiate_guardrails()"]
    end
    
    subgraph "Metrics Calculation"
        BasicCalc["calculator.py<br/>MetricsCalculator"]
        BenchCalc["benchmark_calculator.py<br/>BenchmarkMetricsCalculator"]
        LatencyTest["latency_tester.py<br/>LatencyTester"]
    end
    
    subgraph "Output Generation"
        Reporter["benchmark_reporter.py<br/>BenchmarkReporter"]
        Visualizer["visualizer.py<br/>PerformanceVisualizer"]
        JSONOut["*.jsonl, *.json"]
        Charts["*.png graphs"]
    end
    
    Args --> CLI
    Config --> CLI
    Dataset --> CLI
    
    CLI --> AsyncEngine
    AsyncEngine --> Runtime
    
    CLI --> BasicCalc
    CLI --> BenchCalc
    CLI --> LatencyTest
    
    BasicCalc --> JSONOut
    BenchCalc --> Reporter
    BenchCalc --> Visualizer
    LatencyTest --> Visualizer
    
    Reporter --> JSONOut
    Visualizer --> Charts
    
    Runtime -.uses.-> Config
```

**Architecture Details:**

1. **CLI Layer** ([src/guardrails/evals/guardrail_evals.py]()): Parses arguments, loads configuration and dataset, coordinates execution
2. **Data Layer**: Configuration from Guardrails Wizard and JSONL datasets with expected trigger values
3. **Execution Engine** ([src/guardrails/evals/core/async_engine.py]()): Processes dataset in batches, executes guardrails asynchronously
4. **Metrics Layer**: Calculates performance metrics based on predicted vs expected triggers
5. **Output Layer**: Generates machine-readable (JSON/JSONL) and human-readable (tables, charts) results

Sources: [docs/evals.md:44-59](), [src/guardrails/evals/README.md:39-49]()

### Evaluation Pipeline Flow

```mermaid
flowchart LR
    subgraph "Input"
        JSONL["Dataset Entry<br/>{id, data, expected_triggers}"]
    end
    
    subgraph "Processing"
        Stage["Stage Detection<br/>pre_flight/input/output"]
        Batch["Batch Processor<br/>asyncio.gather()"]
        Exec["run_guardrails()<br/>execution"]
    end
    
    subgraph "Result Collection"
        Pred["Predicted Triggers<br/>GuardrailResult.tripwire_triggered"]
        Expected["Expected Triggers<br/>from dataset"]
        Compare["Compare<br/>TP/FP/TN/FN"]
    end
    
    subgraph "Output"
        Metrics["Metrics:<br/>Precision, Recall, F1<br/>ROC AUC (benchmark)"]
    end
    
    JSONL --> Stage
    Stage --> Batch
    Batch --> Exec
    Exec --> Pred
    JSONL --> Expected
    Pred --> Compare
    Expected --> Compare
    Compare --> Metrics
```

**Pipeline Stages:**

1. **Input Parsing**: Load JSONL dataset entries with `id`, `data`, and `expected_triggers` fields
2. **Stage Detection**: Automatically identify which pipeline stages (pre_flight, input, output) are configured
3. **Batch Processing**: Execute guardrails in parallel batches (default size: 32) using `asyncio.gather()`
4. **Result Collection**: Compare `GuardrailResult.tripwire_triggered` against `expected_triggers`
5. **Metrics Calculation**: Compute confusion matrix elements (TP/FP/TN/FN) and derive metrics

Sources: [src/guardrails/evals/README.md:54-64]()

## CLI Interface

The `guardrail_evals.py` script provides the command-line interface for both evaluation and benchmark modes.

### Basic Usage

**Evaluation Mode** (single configuration):
```bash
python -m guardrails.evals.guardrail_evals \
  --config-path guardrails_config.json \
  --dataset-path data.jsonl
```

**Benchmark Mode** (model comparison):
```bash
python -m guardrails.evals.guardrail_evals \
  --config-path guardrails_config.json \
  --dataset-path data.jsonl \
  --mode benchmark \
  --models gpt-5 gpt-5-mini gpt-4.1-mini
```

Sources: [README.md:99-113](), [docs/evals.md:7-21]()

### CLI Arguments Reference

| Argument | Required | Type | Description |
|----------|----------|------|-------------|
| `--config-path` | ✅ | Path | Pipeline configuration file (JSON) exported from Guardrails Wizard |
| `--dataset-path` | ✅ | Path | Evaluation dataset in JSONL format |
| `--mode` | ❌ | String | `evaluate` (default) or `benchmark` |
| `--stages` | ❌ | List[String] | Specific stages to evaluate (e.g., `pre_flight input output`) |
| `--batch-size` | ❌ | Integer | Parallel processing batch size (default: 32) |
| `--output-dir` | ❌ | Path | Results directory (default: `results/`) |
| `--api-key` | ❌ | String | API key for OpenAI, Azure OpenAI, or compatible API |
| `--base-url` | ❌ | String | Base URL for OpenAI-compatible API (e.g., Ollama, vLLM) |
| `--azure-endpoint` | ❌ | String | Azure OpenAI endpoint URL |
| `--azure-api-version` | ❌ | String | Azure OpenAI API version (default: `2025-01-01-preview`) |
| `--models` | ❌ | List[String] | Models for benchmark mode (benchmark only) |
| `--latency-iterations` | ❌ | Integer | Number of latency test samples (default: 50, benchmark only) |

**Configuration Source**: The `--config-path` should point to a JSON file exported from the [Guardrails Wizard UI](https://guardrails.openai.com). The configuration follows the `PipelineBundles` schema documented in [Configuration Schema](#10.4).

Sources: [docs/evals.md:43-59](), [src/guardrails/evals/README.md:66-77]()

### Programmatic Usage

The evaluation framework can be invoked programmatically via the `GuardrailEval` class:

```python
from pathlib import Path
from guardrails.evals.guardrail_evals import GuardrailEval
import asyncio

eval = GuardrailEval(
    config_path=Path("guardrails_config.json"),
    dataset_path=Path("data.jsonl"),
    batch_size=32,
    output_dir=Path("results"),
)

asyncio.run(eval.run())
```

**Class Location**: [src/guardrails/evals/guardrail_evals.py]()

Sources: [README.md:130-145]()

## Dataset Format

Datasets must be in JSONL (JSON Lines) format, where each line contains a complete JSON object representing a single test case.

### Standard Guardrails Dataset

```json
{
  "id": "sample-001",
  "data": "My email is john.doe@example.com",
  "expected_triggers": {
    "Contains PII": true,
    "Moderation": false
  }
}
```

**Field Specifications:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | String | ✅ | Unique identifier for the test case |
| `data` | String | ✅ | Text content to evaluate (single string for most guardrails) |
| `expected_triggers` | Dict[String, Boolean] | ✅ | Mapping of guardrail names to expected trigger values |

**Guardrail Name Matching**: The keys in `expected_triggers` must exactly match the guardrail names as they appear in the configuration file. Common names include:
- `"Moderation"`
- `"Contains PII"`
- `"Hallucination Detection"`
- `"Jailbreak"`
- `"NSFW Text"`
- `"Off Topic Prompts"`
- `"Custom Prompt Check"`

Sources: [docs/evals.md:73-91](), [src/guardrails/evals/README.md:109-126]()

### Multi-Turn Conversation Format

For guardrails that require conversation context (e.g., Prompt Injection Detection), the `data` field contains a JSON-serialized array representing conversation history with function calls.

```json
{
  "id": "prompt_injection_detection_001",
  "expected_triggers": {
    "Prompt Injection Detection": true
  },
  "data": "[{'role': 'user', 'content': [{'type': 'input_text', 'text': 'What is the weather?'}]}, {'type': 'function_call', 'name': 'get_weather', 'arguments': '{\"location\": \"Tokyo\"}', 'call_id': 'call1'}, {'type': 'function_call_output', 'call_id': 'call1', 'output': '{\"temperature\": 22}'}]"
}
```

**Conversation Turn Types:**

1. **User Message**: `{"role": "user", "content": [{"type": "input_text", "text": "..."}]}`
2. **Function Calls**: `{"type": "function_call", "name": "function_name", "arguments": "json_string", "call_id": "unique_id"}`
3. **Function Outputs**: `{"type": "function_call_output", "call_id": "matching_call_id", "output": "result_json"}`
4. **Assistant Text**: `{"type": "assistant_text", "text": "response text"}`

This format simulates the complete conversation flow including tool invocations, enabling detection of prompt injection attempts that manipulate function calls.

Sources: [docs/evals.md:93-121](), [src/guardrails/evals/README.md:128-191]()

## Evaluation Modes

The framework supports two distinct modes with different capabilities and outputs.

### Evaluation Mode

**Purpose**: Calculate basic performance metrics for a single guardrail configuration.

**Metrics Calculated**:
- Precision: `TP / (TP + FP)`
- Recall: `TP / (TP + FN)`
- F1 Score: `2 * (Precision * Recall) / (Precision + Recall)`
- Accuracy: `(TP + TN) / (TP + TN + FP + FN)`

**Output Structure**:
```
results/
└── eval_run_YYYYMMDD_HHMMSS/
    ├── eval_results_pre_flight.jsonl
    ├── eval_results_input.jsonl
    ├── eval_results_output.jsonl
    ├── eval_metrics.json
    └── run_summary.txt
```

**Metrics Calculator**: [src/guardrails/evals/core/calculator.py]()

Sources: [docs/evals.md:123-132](), [src/guardrails/evals/README.md:53-58]()

### Benchmark Mode

**Purpose**: Compare multiple models with advanced metrics, latency analysis, and visualizations.

**Additional Metrics**:
- **ROC AUC**: Area under the Receiver Operating Characteristic curve
- **Precision at Recall Thresholds**: Precision values at specific recall levels (e.g., 0.8, 0.9, 0.95)
- **Latency P50/P95**: Median and 95th percentile end-to-end latency

**Requirements**: Benchmark mode requires additional dependencies:
```bash
pip install "openai-guardrails[benchmark]"
```

This installs: `numpy`, `scikit-learn`, `matplotlib`, `seaborn`, `pandas`

**Output Structure**:
```
results/
└── benchmark_{guardrail}_YYYYMMDD_HHMMSS/
    ├── results/
    │   ├── eval_results_{guardrail}_{model}.jsonl
    │   ├── performance_metrics.json
    │   ├── latency_results.json
    │   └── benchmark_summary_tables.txt
    ├── graphs/
    │   ├── {guardrail}_roc_curves.png
    │   ├── {guardrail}_basic_metrics.png
    │   ├── {guardrail}_advanced_metrics.png
    │   └── latency_comparison.png
    └── benchmark_summary.txt
```

**Benchmark Calculator**: [src/guardrails/evals/core/benchmark_calculator.py]()

Sources: [docs/evals.md:26-42](), [docs/evals.md:134-149](), [src/guardrails/evals/README.md:59-65]()

### Mode Comparison Table

| Feature | Evaluation Mode | Benchmark Mode |
|---------|-----------------|----------------|
| Basic Metrics (P/R/F1) | ✅ | ✅ |
| ROC AUC | ❌ | ✅ |
| Precision at Recall | ❌ | ✅ |
| Latency Testing | ❌ | ✅ |
| Multi-Model Comparison | ❌ | ✅ |
| Visualizations | ❌ | ✅ |
| Dependencies | Base package only | Requires `[benchmark]` extra |

Sources: [docs/evals.md:26-42](), [src/guardrails/evals/README.md:53-65]()

## Metrics and Calculations

### Basic Metrics (Evaluation Mode)

The `MetricsCalculator` class computes standard classification metrics based on confusion matrix elements.

**Confusion Matrix Elements**:
```mermaid
graph LR
    subgraph "Predicted vs Expected"
        TP["True Positive<br/>Predicted: True<br/>Expected: True"]
        FP["False Positive<br/>Predicted: True<br/>Expected: False"]
        TN["True Negative<br/>Predicted: False<br/>Expected: False"]
        FN["False Negative<br/>Predicted: False<br/>Expected: True"]
    end
    
    subgraph "Metrics"
        Precision["Precision = TP/(TP+FP)<br/>Accuracy of positive predictions"]
        Recall["Recall = TP/(TP+FN)<br/>Coverage of actual positives"]
        F1["F1 = 2·P·R/(P+R)<br/>Harmonic mean of P and R"]
        Accuracy["Accuracy = (TP+TN)/Total<br/>Overall correctness"]
    end
    
    TP --> Precision
    FP --> Precision
    TP --> Recall
    FN --> Recall
    Precision --> F1
    Recall --> F1
    TP --> Accuracy
    TN --> Accuracy
```

**Implementation**: The metrics are calculated per guardrail and per stage, with aggregate metrics computed across all test cases.

Sources: [src/guardrails/evals/core/calculator.py]()

### Advanced Metrics (Benchmark Mode)

The `BenchmarkMetricsCalculator` extends basic metrics with threshold-based analysis.

**ROC Curve Generation**:
1. Sort predictions by confidence score
2. For each threshold, calculate TPR (True Positive Rate) and FPR (False Positive Rate)
3. Plot TPR vs FPR curve
4. Calculate Area Under Curve (AUC) as overall performance metric

**Precision at Recall Thresholds**:
- Calculate precision values at specific recall levels (0.8, 0.9, 0.95)
- Enables evaluation of high-recall scenarios where missing violations is costly

**Implementation**: [src/guardrails/evals/core/benchmark_calculator.py]()

Sources: [docs/evals.md:193-196](), [src/guardrails/evals/README.md:59-64]()

### Latency Testing

The `LatencyTester` measures end-to-end guardrail performance by executing guardrails on dataset samples and collecting timing metrics.

**Measured Metrics**:
- **P50 (Median)**: 50th percentile latency
- **P95**: 95th percentile latency
- **Mean**: Average latency
- **Min/Max**: Extreme values

**Test Methodology**:
1. Sample N entries from dataset (default: 50)
2. Execute guardrails with timing instrumentation
3. Collect execution times
4. Calculate percentile statistics

**Implementation**: [src/guardrails/evals/core/latency_tester.py]()

Sources: [docs/evals.md:58](), [src/guardrails/evals/README.md:62]()

## Visualization and Reporting

### Performance Visualizer

The `PerformanceVisualizer` class generates charts for benchmark mode.

**Generated Charts**:

1. **ROC Curves** (`{guardrail}_roc_curves.png`): Comparative ROC curves for all models
2. **Basic Metrics** (`{guardrail}_basic_metrics.png`): Bar charts for precision, recall, F1
3. **Advanced Metrics** (`{guardrail}_advanced_metrics.png`): ROC AUC and precision-at-recall comparisons
4. **Latency Comparison** (`latency_comparison.png`): P50/P95 latency across models

**Implementation**: [src/guardrails/evals/core/visualizer.py]()

Sources: [docs/evals.md:145-148](), [src/guardrails/evals/README.md:100-104]()

### Benchmark Reporter

The `BenchmarkReporter` class generates formatted summary tables for benchmark results.

**Generated Reports**:

1. **Performance Metrics Table**: Precision, Recall, F1, ROC AUC per model
2. **Latency Results Table**: P50, P95, Mean latency per model
3. **Summary Text**: Human-readable overview of findings

**Output File**: `benchmark_summary_tables.txt`

**Implementation**: [src/guardrails/evals/core/benchmark_reporter.py]()

Sources: [docs/evals.md:143](), [src/guardrails/evals/README.md:98]()

## Third-Party Provider Support

The evaluation framework supports any OpenAI-compatible API through flexible configuration options.

### Provider Configuration Diagram

```mermaid
graph TB
    subgraph "CLI Arguments"
        APIKey["--api-key"]
        BaseURL["--base-url"]
        AzureEP["--azure-endpoint"]
        AzureVer["--azure-api-version"]
    end
    
    subgraph "Provider Types"
        OpenAI["OpenAI<br/>api-key only"]
        Azure["Azure OpenAI<br/>azure-endpoint + api-key"]
        Ollama["Ollama<br/>base-url + fake-key"]
        vLLM["vLLM / Other<br/>base-url + api-key"]
    end
    
    subgraph "Client Construction"
        GuardrailLLM["guardrail_llm<br/>OpenAI() or AzureOpenAI()"]
    end
    
    APIKey --> OpenAI
    APIKey --> Azure
    APIKey --> Ollama
    APIKey --> vLLM
    
    BaseURL --> Ollama
    BaseURL --> vLLM
    
    AzureEP --> Azure
    AzureVer --> Azure
    
    OpenAI --> GuardrailLLM
    Azure --> GuardrailLLM
    Ollama --> GuardrailLLM
    vLLM --> GuardrailLLM
```

### Provider Examples

**OpenAI (Default)**:
```bash
python -m guardrails.evals.guardrail_evals \
  --config-path config.json \
  --dataset-path data.jsonl \
  --api-key sk-...
```

**Azure OpenAI**:
```bash
python -m guardrails.evals.guardrail_evals \
  --config-path config.json \
  --dataset-path data.jsonl \
  --azure-endpoint https://your-resource.openai.azure.com \
  --api-key your-azure-key \
  --azure-api-version 2025-01-01-preview \
  --mode benchmark \
  --models gpt-4o gpt-4o-mini
```

**Ollama (Local Models)**:
```bash
python -m guardrails.evals.guardrail_evals \
  --config-path config.json \
  --dataset-path data.jsonl \
  --base-url http://localhost:11434/v1 \
  --api-key fake-key \
  --mode benchmark \
  --models llama3 mistral
```

**vLLM or Other Compatible APIs**: Use `--base-url` to specify the endpoint and provide the appropriate `--api-key`.

Sources: [docs/evals.md:151-186]()

## Async Execution Engine

The `AsyncGuardrailEngine` class orchestrates parallel guardrail execution across dataset entries.

### Engine Architecture

```mermaid
graph TB
    subgraph "AsyncGuardrailEngine"
        Load["load_dataset()<br/>Parse JSONL"]
        Detect["detect_stages()<br/>Identify configured stages"]
        Process["process_batch()<br/>asyncio.gather()"]
    end
    
    subgraph "Batch Processing"
        Entry1["Dataset Entry 1"]
        Entry2["Dataset Entry 2"]
        EntryN["Dataset Entry N"]
        Gather["asyncio.gather(*tasks)<br/>Parallel execution"]
    end
    
    subgraph "Guardrail Execution"
        Runtime["run_guardrails()<br/>Stage-specific execution"]
        Result["GuardrailResult<br/>tripwire_triggered"]
    end
    
    Load --> Detect
    Detect --> Process
    Process --> Entry1
    Process --> Entry2
    Process --> EntryN
    
    Entry1 --> Gather
    Entry2 --> Gather
    EntryN --> Gather
    
    Gather --> Runtime
    Runtime --> Result
```

**Key Methods**:

| Method | Purpose |
|--------|---------|
| `load_dataset()` | Parse JSONL file into dataset entries |
| `detect_stages()` | Identify which pipeline stages are configured |
| `process_batch()` | Execute guardrails in parallel batches using `asyncio.gather()` |
| `collect_results()` | Aggregate execution results with expected triggers |

**Batch Size Configuration**: The `--batch-size` argument (default: 32) controls parallelism. Higher values increase throughput but consume more memory.

**Implementation**: [src/guardrails/evals/core/async_engine.py]()

Sources: [src/guardrails/evals/README.md:43]()

## Output Structure and Files

### Evaluation Mode Output

**Directory Structure**:
```
results/eval_run_20240115_143022/
├── eval_results_pre_flight.jsonl    # Per-entry results for pre_flight stage
├── eval_results_input.jsonl         # Per-entry results for input stage
├── eval_results_output.jsonl        # Per-entry results for output stage
├── eval_metrics.json                # Aggregate metrics per guardrail
└── run_summary.txt                  # Human-readable summary
```

**File Formats**:

1. **`eval_results_{stage}.jsonl`**: One JSON object per line containing:
   ```json
   {
     "id": "sample-001",
     "guardrail_name": "Contains PII",
     "predicted": true,
     "expected": true,
     "correct": true,
     "execution_time_ms": 45.2
   }
   ```

2. **`eval_metrics.json`**: Aggregate metrics per guardrail:
   ```json
   {
     "Contains PII": {
       "precision": 0.95,
       "recall": 0.92,
       "f1": 0.935,
       "accuracy": 0.94,
       "total_samples": 100
     }
   }
   ```

Sources: [docs/evals.md:123-132](), [src/guardrails/evals/README.md:80-88]()

### Benchmark Mode Output

**Directory Structure**:
```
results/benchmark_Contains_PII_20240115_143022/
├── results/
│   ├── eval_results_Contains_PII_gpt-5.jsonl
│   ├── eval_results_Contains_PII_gpt-5-mini.jsonl
│   ├── performance_metrics.json
│   ├── latency_results.json
│   └── benchmark_summary_tables.txt
├── graphs/
│   ├── Contains_PII_roc_curves.png
│   ├── Contains_PII_basic_metrics.png
│   ├── Contains_PII_advanced_metrics.png
│   └── latency_comparison.png
└── benchmark_summary.txt
```

**File Formats**:

1. **`performance_metrics.json`**: Per-model metrics including ROC AUC and precision-at-recall:
   ```json
   {
     "gpt-5": {
       "precision": 0.95,
       "recall": 0.92,
       "f1": 0.935,
       "roc_auc": 0.97,
       "precision_at_recall_80": 0.93,
       "precision_at_recall_90": 0.89,
       "precision_at_recall_95": 0.85
     }
   }
   ```

2. **`latency_results.json`**: Per-model latency statistics:
   ```json
   {
     "gpt-5": {
       "p50_ms": 120.5,
       "p95_ms": 245.8,
       "mean_ms": 135.2,
       "min_ms": 85.3,
       "max_ms": 310.7
     }
   }
   ```

3. **`benchmark_summary_tables.txt`**: Formatted tables comparing models across all metrics.

Sources: [docs/evals.md:134-149](), [src/guardrails/evals/README.md:90-105]()

## Demo Files

The evaluation framework includes demo files for testing the system without creating custom datasets.

**Demo Location**: [src/guardrails/evals/eval_demo/]()

**Files**:
- `demo_config.json`: Sample guardrail configuration with multiple stages
- `demo_data.jsonl`: Sample dataset with expected trigger labels

**Running Demo**:
```bash
# Evaluation mode
python -m guardrails.evals.guardrail_evals \
  --config-path src/guardrails/evals/eval_demo/demo_config.json \
  --dataset-path src/guardrails/evals/eval_demo/demo_data.jsonl

# Benchmark mode
python -m guardrails.evals.guardrail_evals \
  --config-path src/guardrails/evals/eval_demo/demo_config.json \
  --dataset-path src/guardrails/evals/eval_demo/demo_data.jsonl \
  --mode benchmark \
  --models gpt-5 gpt-5-mini gpt-5-nano
```

Sources: [docs/evals.md:23](), [src/guardrails/evals/README.md:7-21]()

## Best Practices

### Dataset Preparation

1. **Balanced Datasets**: Include roughly equal numbers of positive and negative examples to avoid metric bias
2. **Representative Samples**: Cover edge cases, boundary conditions, and typical production scenarios
3. **Consistent Labeling**: Use precise guardrail names matching configuration exactly
4. **Multi-Stage Datasets**: When evaluating multiple stages, ensure each entry has expected triggers for all relevant guardrails

### Evaluation Workflow

1. **Single Stage at a Time**: Evaluate one pipeline stage per run for clearer results
2. **Start with Evaluation Mode**: Use basic mode first to verify configuration correctness
3. **Progress to Benchmarking**: Use benchmark mode for model selection and optimization
4. **Iterate on Configuration**: Adjust `confidence_threshold` and other parameters based on metrics

### Model Selection

1. **Latency vs Accuracy Tradeoff**: Smaller models (e.g., `gpt-5-mini`, `gpt-5-nano`) offer lower latency but may sacrifice accuracy
2. **ROC AUC Comparison**: Use ROC AUC to compare models holistically across all threshold values
3. **Recall Priority**: For safety-critical guardrails, prioritize high recall (minimize false negatives)
4. **Precision Priority**: For user experience, prioritize high precision (minimize false positives)

Sources: [docs/evals.md:69](), [src/guardrails/evals/README.md:216-221]()

---

