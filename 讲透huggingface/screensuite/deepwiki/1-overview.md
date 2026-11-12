<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/screensuite · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [examples/run_benchmarks.py](examples/run_benchmarks.py)
- [pyproject.toml](pyproject.toml)
- [run.py](run.py)
- [src/screensuite/benchmarks/multistep/android_world/benchmark.py](src/screensuite/benchmarks/multistep/android_world/benchmark.py)
- [src/screensuite/benchmarks/multistep/browse_comp/benchmark.py](src/screensuite/benchmarks/multistep/browse_comp/benchmark.py)
- [src/screensuite/benchmarks/multistep/gaia/benchmark.py](src/screensuite/benchmarks/multistep/gaia/benchmark.py)
- [src/screensuite/benchmarks/multistep/mind2web/benchmark.py](src/screensuite/benchmarks/multistep/mind2web/benchmark.py)
- [src/screensuite/benchmarks/multistep/osworld/benchmark.py](src/screensuite/benchmarks/multistep/osworld/benchmark.py)
- [src/screensuite/response_generation.py](src/screensuite/response_generation.py)

</details>



## Purpose and Scope

ScreenSuite is a comprehensive benchmarking framework for evaluating Graphical User Interface (GUI) agents and multimodal large language models (MLLMs) across three distinct areas of capability: perception, single-step agentic behavior, and multi-step agentic behavior. The framework provides standardized evaluation protocols for comparing model performance on GUI interaction tasks rather than agent implementations themselves, utilizing simple agent implementations based on `smolagents`.

For installation instructions and basic usage, see [Getting Started](#2). For detailed information about specific benchmark categories, see [Benchmark Categories](#4). For model configuration and integration details, see [Model Integration](#6).

Sources: [README.md:1-7](), [pyproject.toml:1-11]()

## System Architecture

The ScreenSuite framework follows a modular architecture centered around a registry-based benchmark discovery system, parallel processing pipeline, and standardized evaluation interfaces.

### Core Architecture Components

```mermaid
graph TB
    subgraph "Entry Points"
        A[run_benchmarks.py] 
        B[run.py]
    end
    
    subgraph "Core Framework"
        C[BenchmarkRegistry]
        D[get_registry]
        E[BaseBenchmark]
        F[EvaluationConfig]
    end
    
    subgraph "Processing Pipeline"
        G[get_model_responses]
        H[process_sample]
        I[ThreadPoolExecutor]
    end
    
    subgraph "Model Integration"
        J[InferenceClientModel]
        K[OpenAIServerModel] 
        L[LiteLLMModel]
    end
    
    subgraph "Output System"
        M[BenchmarkResult]
        N[JSONL Files]
    end
    
    A --> C
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    J --> H
    K --> H
    L --> H
    H --> M
    M --> N
```

The architecture separates concerns between benchmark discovery (`BenchmarkRegistry`), execution orchestration (`get_model_responses`), and result collection (`BenchmarkResult`). The system supports multiple entry points for both programmatic and interactive usage.

Sources: [examples/run_benchmarks.py:1-30](), [run.py:1-20](), [src/screensuite/response_generation.py:115-170]()

### Benchmark Type Hierarchy

```mermaid
graph TB
    subgraph "BaseBenchmark Interface"
        A[BaseBenchmark]
        B[load]
        C[evaluate] 
        D[tags]
    end
    
    subgraph "HubBaseBenchmark"
        E[HubBaseBenchmark]
        F[dataset]
        G[config]
    end
    
    subgraph "Multistep Benchmarks"
        H[OSWorldBenchmark]
        I[AndroidWorldBenchmark]
        J[Mind2WebBenchmark]
        K[GaiaBenchmark]
        L[BrowseCompBenchmark]
    end
    
    subgraph "Singlestep & Perception"
        M[MMind2WebBenchmark]
        N[AndroidControlBenchmark]
        O[ScreenSpotBenchmark]
        P[VisualWebBenchBenchmark]
    end
    
    A --> E
    E --> H
    E --> I
    E --> J
    E --> K
    E --> L
    E --> M
    E --> N
    E --> O
    E --> P
    
    A --> B
    A --> C
    A --> D
    E --> F
    E --> G
```

The type hierarchy establishes common interfaces while allowing specialization for different benchmark requirements. `HubBaseBenchmark` provides Hugging Face dataset integration, while direct `BaseBenchmark` implementations handle custom data sources.

Sources: [src/screensuite/benchmarks/multistep/osworld/benchmark.py:25-30](), [src/screensuite/benchmarks/multistep/android_world/benchmark.py:251-257](), [src/screensuite/benchmarks/multistep/mind2web/benchmark.py:33-34]()

## Benchmark Categories

ScreenSuite organizes benchmarks into three primary categories based on interaction complexity and evaluation approach.

| Category | Description | Environment | Evaluation Method |
|----------|-------------|-------------|-------------------|
| **Multistep** | Complex online agent tasks requiring sequential interactions | Live environments (Docker, Android emulators, web) | Task completion scoring |
| **Singlestep** | Offline prediction tasks from screenshots | Static image datasets | Action accuracy metrics |
| **Perception** | Understanding and reasoning without actions | Static datasets | Text matching, QA scoring |

### Multistep Online Benchmarks

```mermaid
graph LR
    subgraph "OSWorld"
        A[DesktopEnv]
        B[PromptAgent]
        C[Docker_Containers]
    end
    
    subgraph "AndroidWorld" 
        D[AndroidEnvClient]
        E[AndroidAgent]
        F[Android_Emulators]
    end
    
    subgraph "Mind2Web"
        G[WebAgent]
        H[Live_Websites]
        I[url_exact_match]
    end
    
    subgraph "GAIA"
        J[get_agent_responses]
        K[get_question_score_gaia]
        L[Tool_Usage]
    end
    
    A --> B
    B --> C
    D --> E
    E --> F
    G --> H
    H --> I
    J --> K
    K --> L
```

Multistep benchmarks require environment setup and sequential interaction capabilities. Each implements specialized evaluation methods: OSWorld uses Docker containers for desktop tasks, AndroidWorld manages Android emulators, Mind2Web validates URL navigation, and GAIA focuses on complex reasoning with tool usage.

Sources: [src/screensuite/benchmarks/multistep/osworld/benchmark.py:142-158](), [src/screensuite/benchmarks/multistep/android_world/benchmark.py:224-230](), [src/screensuite/benchmarks/multistep/mind2web/benchmark.py:35-48](), [src/screensuite/benchmarks/multistep/gaia/benchmark.py:47-54]()

## Processing Pipeline

The evaluation pipeline implements two-level parallelization: model-level concurrency for evaluating multiple models simultaneously, and sample-level concurrency within each model evaluation.

### Response Generation Pipeline

```mermaid
flowchart TD
    A[select_examples_to_test] --> B[ThreadPoolExecutor]
    B --> C[process_sample]
    C --> D[input_annotation_transform]
    D --> E[AnnotatedContent]
    E --> F[process_one_input]
    F --> G[model.generate]
    G --> H[append_answer]
    H --> I[JSONL_Output]
    
    subgraph "Parallel Processing"
        J[parallel_workers_config]
        K[max_samples_to_test]
        L[timeout_config]
    end
    
    J --> B
    K --> A
    L --> F
```

The pipeline transforms raw dataset samples through `input_annotation_transform` functions into `AnnotatedContent` objects containing `ChatMessage` sequences. These are processed through `model.generate()` calls with configurable parallelization and timeout handling.

Sources: [src/screensuite/response_generation.py:115-170](), [src/screensuite/response_generation.py:43-67](), [src/screensuite/response_generation.py:89-113]()

### Evaluation Configuration System

```mermaid
graph TB
    subgraph "EvaluationConfig"
        A[parallel_workers]
        B[max_samples_to_test]
        C[test_mode]
        D[run_name]
        E[timeout]
        F[image_resize_config]
    end
    
    subgraph "ImageResizeConfig"
        G[factor]
        H[min_pixels]
        I[max_pixels]
    end
    
    subgraph "Model-Specific Configs"
        J[use_uitars_action_space]
        K[use_h_action_space]
        L[image_before_text]
    end
    
    A --> A1[ThreadPoolExecutor_max_workers]
    B --> B1[Dataset_sampling]
    C --> C1[Limited_test_execution]
    D --> D1[Output_file_naming]
    E --> E1[Request_timeout]
    F --> G
    F --> H
    F --> I
    
    J --> J1[UI-TARS_prompt_format]
    K --> K1[Holo_JEDI_format]
    L --> L1[Message_ordering]
```

`EvaluationConfig` centralizes execution parameters while supporting model-specific customizations for specialized UI models like UI-TARS, Holo, and JEDI through action space and formatting flags.

Sources: [examples/run_benchmarks.py:105-109](), [examples/run_benchmarks.py:149-156](), [examples/run_benchmarks.py:160-171](), [examples/run_benchmarks.py:180-191]()

## Model Integration Layer

ScreenSuite integrates multiple model types through the `smolagents` framework, supporting both general-purpose and specialized UI models.

### Supported Model Categories

| Model Type | Implementation | Key Models | Configuration |
|------------|----------------|------------|---------------|
| **OpenAI** | `OpenAIServerModel` | `gpt-4o` | Standard API |
| **Anthropic** | `LiteLLMModel` | `claude-sonnet-4` | Via LiteLLM |
| **Qwen Vision** | `InferenceClientModel` | `Qwen2.5-VL-32B/72B` | Fireworks, Nebius |
| **Specialized UI** | `InferenceClientModel` | UI-TARS, JEDI, Holo | Custom endpoints |

The framework automatically handles model-specific prompt formatting, image processing, and response parsing through configuration flags and specialized evaluation configs.

Sources: [examples/run_benchmarks.py:111-119](), [examples/run_benchmarks.py:130-141](), [examples/run_benchmarks.py:144-147](), [examples/run_benchmarks.py:174-196]()

## Output and Results System

All benchmark results are standardized through the `BenchmarkResult` class and persisted in JSONL format for analysis and comparison.

### Result Structure

```mermaid
graph TB
    subgraph "BenchmarkResult"
        A[_metrics]
        B[primary_metric]
    end
    
    subgraph "Standard Metrics"
        C[avg_accuracy]
        D[proportion_missing] 
        E[count_samples]
    end
    
    subgraph "Benchmark-Specific Metrics"
        F[action_accuracy]
        G[click_accuracy]
        H[f1_score]
        I[bbox_iou]
    end
    
    subgraph "Output Files"
        J[answers.jsonl]
        K[results_run_name.jsonl]
        L[output_directory_structure]
    end
    
    A --> C
    A --> D  
    A --> E
    A --> F
    A --> G
    A --> H
    A --> I
    
    B --> C
    
    C --> J
    D --> K
    E --> L
```

Results include both universal metrics (`avg_accuracy`, `proportion_missing`, `count_samples`) and benchmark-specific measures. The output system maintains detailed logs in `answers.jsonl` and summary metrics in `results_{run_name}.jsonl` for comprehensive analysis.

Sources: [examples/run_benchmarks.py:68-73](), [src/screensuite/response_generation.py:129-146](), [src/screensuite/benchmarks/multistep/osworld/benchmark.py:201-208]()

---

