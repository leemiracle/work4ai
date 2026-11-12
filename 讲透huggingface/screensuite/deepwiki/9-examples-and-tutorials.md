<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/screensuite · page 9 Examples and Tutorials · fetched 2026-10-26 -->

# Examples and Tutorials

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/GAIAweb_benchmark/GAIA_web.jsonl](examples/GAIAweb_benchmark/GAIA_web.jsonl)
- [examples/GAIAweb_benchmark/reformulator.py](examples/GAIAweb_benchmark/reformulator.py)
- [examples/GAIAweb_benchmark/run.py](examples/GAIAweb_benchmark/run.py)
- [examples/GAIAweb_benchmark/score.ipynb](examples/GAIAweb_benchmark/score.ipynb)
- [examples/example_use_benchmarks.py](examples/example_use_benchmarks.py)
- [examples/generate_traces/score_and_upload.ipynb](examples/generate_traces/score_and_upload.ipynb)

</details>



This page provides practical examples and step-by-step tutorials for using the screensuite benchmarking framework. It covers basic registry interactions, comprehensive benchmark implementations, data processing workflows, and result analysis patterns.

For information about core framework concepts, see [Core Framework](#3). For detailed benchmark descriptions, see [Benchmark Categories](#4). For model integration patterns, see [Model Integration](#6).

## Basic Registry Usage

The simplest way to interact with screensuite is through the benchmark registry, which provides discovery and execution capabilities for all available benchmarks.

### Registry Discovery Pattern

```mermaid
flowchart TD
    A["`registry.list_all()`"] --> B["`List[BaseBenchmark]`"]
    C["`registry.get_by_tags(['demo'])`"] --> D["`Filtered Benchmarks`"]
    E["`registry.get('example')`"] --> F["`Specific Benchmark`"]
    
    B --> G["`benchmark.name`"]
    D --> G
    F --> G
    
    G --> H["`benchmark.evaluate(model, config)`"]
    H --> I["`EvaluationResults`"]
    
    subgraph "Registry Methods"
        A
        C
        E
    end
    
    subgraph "Benchmark Operations"
        G
        H
        I
    end
```

**Registry Discovery and Execution Flow**

The registry provides three primary discovery methods: `list_all()` returns all available benchmarks, `get_by_tags()` filters by metadata tags, and `get()` retrieves specific benchmarks by name. All methods return `BaseBenchmark` instances that expose a common `evaluate()` interface.

Sources: [examples/example_use_benchmarks.py:12-46]()

### Dummy Model Implementation

```mermaid
classDiagram
    class Model {
        <<abstract>>
        +model_id: str
        +__call__(messages: list[dict]) str
    }
    
    class DummyModel {
        +model_id: "qwen_futuristic"
        +__call__(messages: list[dict]) str
    }
    
    class InferenceConfig {
        +max_tokens: int
        +temperature: float
    }
    
    Model <|-- DummyModel
    DummyModel --> InferenceConfig : "used with"
```

**Model Interface Implementation**

Custom models must inherit from `Model` and implement the `__call__` method to process message lists. The `DummyModel` demonstrates pattern matching on message content to return appropriate responses.

Sources: [examples/example_use_benchmarks.py:32-46]()

## GAIA-web Benchmark Tutorial

The GAIA-web benchmark provides a comprehensive example of complex benchmark execution with web agents, demonstrating parallel processing, response reformulation, and result collection patterns.

### Architecture Overview

```mermaid
graph TB
    subgraph "GAIA-web Execution Pipeline"
        A["`run.py`"] --> B["`parse_arguments()`"]
        B --> C["`datasets.load_dataset()`"]
        C --> D["`ThreadPoolExecutor`"]
        
        D --> E["`answer_single_question()`"]
        E --> F["`DesktopAgent`"]
        E --> G["`E2BVisionAgent`"]
        
        F --> H["`agent.run()`"]
        G --> H
        
        H --> I["`prepare_response()`"]
        I --> J["`append_answer()`"]
        J --> K["`output/*.jsonl`"]
    end
    
    subgraph "Agent Types"
        F
        G
        L["`GoogleSearchTool`"]
        F --> L
        G --> L
    end
    
    subgraph "Response Processing"
        I
        M["`reformulator.py`"]
        I --> M
    end
```

**GAIA-web Pipeline Architecture**

The pipeline processes GAIA-web tasks using either `DesktopAgent` or `E2BVisionAgent`, both configured with `GoogleSearchTool`. Results are reformulated using `prepare_response()` and stored as JSONL files.

Sources: [examples/GAIAweb_benchmark/run.py:1-193]()

### Agent Configuration

```mermaid
flowchart LR
    A["`HfApiModel`"] --> B["`DesktopAgent`"]
    A --> C["`E2BVisionAgent`"]
    
    D["`GoogleSearchTool`"] --> B
    D --> C
    
    B --> E["`max_steps=50`"]
    C --> E
    
    B --> F["`resolution=(1024,768)`"]
    C --> F
    
    B --> G["`additional_authorized_imports`"]
    C --> G
    
    G --> H["[`'numpy'`, `'sympy'`]"]
```

**Agent Configuration Pattern**

Both agent types accept the same configuration parameters: model instance, tools list, step limits, screen resolution, and authorized imports. The `E2BVisionAgent` additionally requires an API key.

Sources: [examples/GAIAweb_benchmark/run.py:69-89]()

### Parallel Processing Implementation

The benchmark implements two-level parallelization: task-level parallelization using `ThreadPoolExecutor` and model-level parallelization within each task execution.

```python
# Task-level parallelization
with ThreadPoolExecutor(max_workers=parallel_workers) as exe:
    futures = [exe.submit(answer_single_question, example, model, file_name) 
               for example in examples_todo]
    for f in tqdm(as_completed(futures), total=len(examples_todo)):
        f.result()
```

Sources: [examples/GAIAweb_benchmark/run.py:157-161]()

### Response Reformulation

```mermaid
sequenceDiagram
    participant Task as "Original Task"
    participant Agent as "Agent Memory"
    participant Reformulator as "prepare_response()"
    participant Model as "Reformulation Model"
    participant Output as "Final Answer"
    
    Task->>Agent: "Execute task"
    Agent->>Reformulator: "inner_messages"
    Reformulator->>Model: "Structured prompt"
    Model->>Reformulator: "Raw response"
    Reformulator->>Output: "FINAL ANSWER: [answer]"
```

**Response Reformulation Sequence**

The reformulation process converts agent execution traces into structured final answers using a specialized prompt template that emphasizes formatting requirements and answer extraction.

Sources: [examples/GAIAweb_benchmark/reformulator.py:9-64]()

## Data Processing Workflows

The framework includes comprehensive data processing workflows for result analysis and benchmark evaluation.

### Scoring and Analysis Pipeline

```mermaid
flowchart TD
    A["`glob.glob('../../output/*.jsonl')`"] --> B["`pd.read_json()`"]
    B --> C["`pd.concat()`"]
    C --> D["`result_df`"]
    
    D --> E["`get_question_score_gaia()`"]
    E --> F["`is_correct column`"]
    
    F --> G["`result_df.groupby('model_id')`"]
    G --> H["`value_counts()`"]
    G --> I["`mean()`"]
    
    H --> J["Accuracy Metrics"]
    I --> J
    
    subgraph "Scoring Functions"
        E
        K["`normalize_number_str()`"]
        L["`normalize_str()`"]
        M["`split_string()`"]
        E --> K
        E --> L
        E --> M
    end
```

**Result Processing Pipeline**

The scoring pipeline aggregates JSONL output files, applies task-specific scoring functions, and generates accuracy metrics grouped by model. The `get_question_score_gaia()` function handles different answer types including numbers, strings, and comma-separated lists.

Sources: [examples/GAIAweb_benchmark/score.ipynb:321-420](), [examples/generate_traces/score_and_upload.ipynb:52-62]()

### Answer Type Normalization

```mermaid
graph TD
    A["`model_answer`"] --> B{"`is_float(ground_truth)`"}
    
    B -->|True| C["`normalize_number_str()`"]
    C --> D["`normalized_answer == float(ground_truth)`"]
    
    B -->|False| E{"`',' or ';' in ground_truth`"}
    
    E -->|True| F["`split_string(ground_truth)`"]
    F --> G["`split_string(model_answer)`"]
    G --> H["`zip(ma_elems, gt_elems)`"]
    H --> I["`element-wise comparison`"]
    
    E -->|False| J["`normalize_str(model_answer)`"]
    J --> K["`normalize_str(ground_truth)`"]
    K --> L["`string comparison`"]
    
    D --> M["`Boolean Result`"]
    I --> M
    L --> M
```

**Answer Normalization Logic**

The scoring system handles three answer types: numeric values (normalized and compared as floats), comma-separated lists (split and compared element-wise), and strings (normalized by removing punctuation and whitespace).

Sources: [examples/GAIAweb_benchmark/score.ipynb:48-141]()

## Development Patterns

### File Structure Convention

```mermaid
graph TD
    A["examples/"] --> B["GAIAweb_benchmark/"]
    A --> C["generate_traces/"]
    A --> D["example_use_benchmarks.py"]
    
    B --> E["run.py"]
    B --> F["reformulator.py"]
    B --> G["score.ipynb"]
    B --> H["GAIA_web.jsonl"]
    
    C --> I["score_and_upload.ipynb"]
    
    subgraph "Benchmark Package"
        E
        F
        G
        H
    end
    
    subgraph "Data Processing"
        I
    end
```

**Example Directory Structure**

Each benchmark example follows a consistent pattern: main execution script (`run.py`), specialized utilities (`reformulator.py`), analysis notebooks (`score.ipynb`), and sample data files (`GAIA_web.jsonl`).

Sources: [examples/GAIAweb_benchmark/](), [examples/generate_traces/](), [examples/example_use_benchmarks.py]()

### Configuration Management

```python
# Environment variable handling
load_dotenv(override=True)
assert os.getenv("HF_TOKEN") is not None, "Need to set HF_TOKEN"

# Argument parsing pattern
parser = argparse.ArgumentParser(description="Runs an agent powered by the given model")
parser.add_argument("--model-id", type=str, default="Qwen/Qwen2.5-VL-7B-Instruct")
parser.add_argument("--parallel-workers", type=int, default=4)
```

The framework uses environment variables for API keys and command-line arguments for runtime configuration. Thread limits are enforced based on provider constraints (e.g., E2B free tier limit of 20 workers).

Sources: [examples/GAIAweb_benchmark/run.py:19-23](), [examples/GAIAweb_benchmark/run.py:27-59](), [examples/GAIAweb_benchmark/run.py:173-174]()

### Error Handling and Serialization

```python
def serialize_agent_error(obj):
    if isinstance(obj, AgentError):
        return {"error_type": obj.__class__.__name__, "message": obj.message}
    else:
        return str(obj)
```

Agent errors are serialized with type information and error messages to facilitate debugging and result analysis. The framework includes proper cleanup procedures with `agent.close()` calls in finally blocks.

Sources: [examples/GAIAweb_benchmark/run.py:62-66](), [examples/GAIAweb_benchmark/run.py:126-130]()