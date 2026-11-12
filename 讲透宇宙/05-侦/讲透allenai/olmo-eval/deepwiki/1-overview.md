<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/olmo-eval · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [DEVELOPMENT.md](DEVELOPMENT.md)
- [README.md](README.md)
- [pyproject.toml](pyproject.toml)
- [src/olmo_eval/__init__.py](src/olmo_eval/__init__.py)
- [src/olmo_eval/cli/beaker/group.py](src/olmo_eval/cli/beaker/group.py)
- [src/olmo_eval/cli/beaker/watch.py](src/olmo_eval/cli/beaker/watch.py)
- [src/olmo_eval/launch/config.py](src/olmo_eval/launch/config.py)
- [src/olmo_eval/storage/__init__.py](src/olmo_eval/storage/__init__.py)
- [uv.lock](uv.lock)

</details>



This project, `olmo-eval`, provides a unified workbench for evaluating large language models (LLMs) throughout their development lifecycle [pyproject.toml:2-4](). It offers a flexible and extensible framework for running evaluations, managing benchmarks, and analyzing results.

**Note**: OLMo-Eval has been superseded by the OLMES repository (Open Language Model Evaluation System) available at https://github.com/allenai/olmes.

Sources: [pyproject.toml:2-4]()

## Purpose and Scope

`olmo-eval` is designed to streamline the process of evaluating language models. Its key features include:

*   A registry of benchmark tasks and composable suites, supporting named variants for different settings like few-shot learning, prompt formatting, and scoring [README.md:11-12]().
*   Support for various inference providers, including `vLLM` for local inference, `LiteLLM` for commercial APIs, and a `mock` provider for testing and dry runs [README.md:13-14]().
*   A `Harness` abstraction that decouples execution policy from task definition, enabling tasks to be run with or without tool augmentation [README.md:15-16]().
*   Capabilities for multi-turn agentic evaluation, tool calling, and sandboxed environments (Docker, Podman, Modal) [README.md:17-18]().
*   `LLM-as-judge` scoring, allowing auxiliary models to evaluate responses [README.md:19]().
*   Storage for aggregate and instance-level predictions [README.md:20]().
*   Inspection tools for viewing instances, formatted prompts, token arrays, and model responses [README.md:21]().

For details on installation and initial setup, see [Installation and Setup](#1.1). For a deeper dive into the core terminology and concepts, refer to [Key Concepts](#1.2).

Sources: [README.md:7-21]()

## System Architecture

### High-Level Architecture Overview

The `olmo-eval` framework orchestrates evaluations by defining tasks and suites, executing them through various inference providers and harnesses, and storing the results.

```mermaid
graph TD
    A[User CLI Interaction] --> B{olmo-eval CLI}
    B --> C[Run Configuration]
    C --> D[AsyncEvalRunner]
    D --> E[Inference Workers]
    E --> F[InferenceProvider]
    F --> G[LLM (vLLM, LiteLLM, HF)]
    G --> E
    E --> H[Harness]
    H --> I[Task]
    I --> J[Scorer]
    J --> K[Metric]
    K --> L[Result Storage]
    L --> M[Results Query/Viewer]

    subgraph Core Components
        I
        J
        K
        F
        H
    end

    subgraph Evaluation Flow
        D
        E
        G
    end

    subgraph Data Flow
        C
        L
        M
    end
```
This diagram illustrates the overall flow from user interaction to result storage. The `olmo-eval` CLI [pyproject.toml:98]() initiates runs based on a `Run Configuration` [src/olmo_eval/launch/config.py:114-128](). The `AsyncEvalRunner` [src/olmo_eval/evaluator/runner.py]() manages `Inference Workers` [src/olmo_eval/evaluator/worker.py]() which interact with `InferenceProvider` implementations [src/olmo_eval/inference/provider.py]() to query LLMs. The `Harness` [src/olmo_eval/harness/harness.py]() wraps the provider and applies execution policies. `Task` definitions [src/olmo_eval/evals/tasks/common.py]() specify data loading, prompt formatting, and scoring logic using `Scorer` [src/olmo_eval/common/scorers/scorer.py]() and `Metric` [src/olmo_eval/common/metrics/metric.py]() components. Finally, results are persisted in `Result Storage` [src/olmo_eval/storage/__init__.py]() and can be queried or viewed.

Sources: [pyproject.toml:98](), [src/olmo_eval/launch/config.py:114-128](), [src/olmo_eval/evaluator/runner.py](), [src/olmo_eval/evaluator/worker.py](), [src/olmo_eval/inference/provider.py](), [src/olmo_eval/harness/harness.py](), [src/olmo_eval/evals/tasks/common.py](), [src/olmo_eval/common/scorers/scorer.py](), [src/olmo_eval/common/metrics/metric.py](), [src/olmo_eval/storage/__init__.py]()

### Evaluation Workbench Concept

The `olmo-eval` framework functions as an evaluation workbench, providing a structured environment for defining, executing, and analyzing LLM evaluations. It emphasizes composability and extensibility, allowing users to combine different tasks, models, and evaluation strategies.

```mermaid
graph TD
    subgraph "OLMo-Eval Workbench"
        A[Task Definitions] --> B[Suite Definitions]
        C[Inference Providers] --> D[Harnesses]
        B --> E[Evaluation Runner]
        D --> E
        E --> F[Scorers & Metrics]
        F --> G[Result Storage]
        G --> H[Analysis & Viewer]
    end

    A -- "Data, Formatting, Scoring" --> I[Task (e.g., humaneval)]
    B -- "Groups Tasks" --> J[Suite (e.g., olmobase:code)]
    C -- "Model Access" --> K[VLLMProvider]
    C -- "Model Access" --> L[LiteLLMProvider]
    D -- "Execution Policy" --> M[BaselineHarness]
    D -- "Execution Policy" --> N[AgenticHarness]
    E -- "Orchestrates Runs" --> O[AsyncEvalRunner]
    F -- "Evaluates Outputs" --> P[ExactMatchScorer]
    F -- "Aggregates Scores" --> Q[AccuracyMetric]
    G -- "Persists Data" --> R[PostgresBackend]
    H -- "Interprets Results" --> S[CLI Query/Plot]
    H -- "Interprets Results" --> T[Pairwise Viewer]

    style I fill:#ace,stroke:#333,stroke-width:2px
    style J fill:#ace,stroke:#333,stroke-width:2px
    style K fill:#ace,stroke:#333,stroke-width:2px
    style L fill:#ace,stroke:#333,stroke-width:2px
    style M fill:#ace,stroke:#333,stroke-width:2px
    style N fill:#ace,stroke:#333,stroke-width:2px
    style O fill:#ace,stroke:#333,stroke-width:2px
    style P fill:#ace,stroke:#333,stroke-width:2px
    style Q fill:#ace,stroke:#333,stroke-width:2px
    style R fill:#ace,stroke:#333,stroke-width:2px
    style S fill:#ace,stroke:#333,stroke-width:2px
    style T fill:#ace,stroke:#333,stroke-width:2px
```
This diagram illustrates how different components of the `olmo-eval` framework interact to form a complete evaluation workbench. `Task` definitions [README.md:78-80]() and `Suite` definitions [README.md:119-123]() are central to specifying what to evaluate. `Inference Providers` [src/olmo_eval/inference/provider.py]() like `VLLMProvider` [src/olmo_eval/inference/vllm_provider.py]() or `LiteLLMProvider` [src/olmo_eval/inference/litellm_provider.py]() handle model communication. `Harnesses` [src/olmo_eval/harness/harness.py]() (e.g., `BaselineHarness` or `AgenticHarness`) define how models interact with tasks. The `AsyncEvalRunner` [src/olmo_eval/evaluator/runner.py]() orchestrates the execution, feeding outputs to `Scorers` [src/olmo_eval/common/scorers/scorer.py]() and `Metrics` [src/olmo_eval/common/metrics/metric.py](). Results are stored in a `StorageBackend` [src/olmo_eval/storage/__init__.py]() (e.g., `PostgresBackend` [src/olmo_eval/storage/backends/postgres.py]()) and can be accessed via CLI tools or a `Pairwise Viewer` [src/olmo_eval/analysis/pairwise_viewer/__init__.py]().

Sources: [README.md:78-80](), [README.md:119-123](), [src/olmo_eval/inference/provider.py](), [src/olmo_eval/inference/vllm_provider.py](), [src/olmo_eval/inference/litellm_provider.py](), [src/olmo_eval/harness/harness.py](), [src/olmo_eval/evaluator/runner.py](), [src/olmo_eval/common/scorers/scorer.py](), [src/olmo_eval/common/metrics/metric.py](), [src/olmo_eval/storage/__init__.py](), [src/olmo_eval/storage/backends/postgres.py](), [src/olmo_eval/analysis/pairwise_viewer/__init__.py]()

## Core Components

### Tasks and Suites

`Tasks` define the specifics of an evaluation, including how to load data, format prompts, and score model outputs [README.md:78-80](). They are registered using the `@register` decorator [README.md:83](). `Variants` can be registered for a task to define specific evaluation presets, such as few-shot settings [README.md:96-98]().

`Suites` are collections that group multiple tasks or nested suites for batch evaluation [README.md:119-123](). They also define strategies for aggregating results from their constituent tasks [README.md:126-134]().

For more details, see [Key Concepts](#1.2).

Sources: [README.md:78-80](), [README.md:83](), [README.md:96-98](), [README.md:119-123](), [README.md:126-134]()

### Inference Providers

`Inference Providers` are responsible for interacting with language models to generate predictions. The framework supports various backends:

*   **`VLLMProvider`**: For local inference using `vLLM` [pyproject.toml:49-55]().
*   **`LiteLLMProvider`**: For accessing commercial APIs like OpenAI, Anthropic, etc., via `LiteLLM` [pyproject.toml:56-58]().
*   **`HuggingFaceProvider`**: For models hosted on Hugging Face [pyproject.toml:46-48]().
*   **`MockProvider`**: A dummy provider for dry runs and debugging [README.md:13-14]().

For more details, see [Key Concepts](#1.2).

Sources: [pyproject.toml:46-48](), [pyproject.toml:49-55](), [pyproject.toml:56-58](), [README.md:13-14]()

### Harnesses

A `Harness` defines the execution policy around an `InferenceProvider`, including tools, scaffolds, and system prompts [README.md:15-16](). This abstraction allows tasks to be run with different execution strategies (e.g., baseline vs. tool-augmented) without modification.

For more details, see [Key Concepts](#1.2).

Sources: [README.md:15-16]()

### Scorers and Metrics

`Scorers` compute a score for each individual instance/output pair [README.md:183](). `Metrics` then aggregate these per-example scores across a dataset to provide overall evaluation results [README.md:198]().

For more details, see [Key Concepts](#1.2).

Sources: [README.md:183](), [README.md:198]()

### Result Storage and Analysis

`olmo-eval` supports storing evaluation results, including aggregate metrics and instance-level predictions [README.md:20](). The `PostgresBackend` [src/olmo_eval/storage/__init__.py:36-44]() is available for persistent storage. The framework also provides tooling for querying results and a pairwise comparison viewer for analysis [src/olmo_eval/analysis/pairwise_viewer/__init__.py]().

Sources: [README.md:20](), [src/olmo_eval/storage/__init__.py:36-44](), [src/olmo_eval/analysis/pairwise_viewer/__init__.py]()

## Installation and Setup

`olmo-eval` uses `uv` for reproducible builds and dependency management [README.md:20]().

To get started:

1.  **Install `uv`**:
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
2.  **Install Python 3.12**:
    ```bash
    uv python install 3.12
    ```
3.  **Install dependencies**:
    ```bash
    uv sync --frozen
    ```
    This command installs default dependency groups (`dev` and `vllm`) [pyproject.toml:107](). Optional dependency groups can be added using `--extra` (e.g., `agents`, `litellm`) [README.md:46](). Some groups, like `openhands` and `vllm`, have conflicting transitive dependencies and cannot be installed together [pyproject.toml:109-122]().

For detailed instructions, see [Installation and Setup](#1.1).

Sources: [README.md:20](), [README.md:28-32](), [README.md:35-39](), [README.md:46](), [README.md:49-50](), [pyproject.toml:107](), [pyproject.toml:109-122]()

## Workflow

A typical workflow involves:

1.  **Browsing Tasks and Suites**: Use `uv run olmo-eval suite inspect <suite_name>` to explore available benchmarks [README.md:53-55]().
2.  **Previewing a Run**: Use `uv run olmo-eval run -m mock -t <task_name> --dry-run` to test configurations without loading a model [README.md:58-61]().
3.  **Running Evaluations**: Execute evaluations with a specified model and task(s).
4.  **Analyzing Results**: Query and view results using CLI tools or the pairwise viewer.

Sources: [README.md:53-55](), [README.md:58-61]()

### Beaker Integration

`olmo-eval` integrates with Beaker for launching distributed evaluation jobs [pyproject.toml:75-77](). This allows for running evaluations on cloud infrastructure. Commands are available for managing Beaker groups, including `group info` [src/olmo_eval/cli/beaker/group.py:50]() and `watch` [src/olmo_eval/cli/beaker/watch.py:8]().

For more details, see [Beaker Integration](#7).

Sources: [pyproject.toml:75-77](), [src/olmo_eval/cli/beaker/group.py:50](), [src/olmo_eval/cli/beaker/watch.py:8]()

---

