<!-- source: DeepWiki mcp.deepwiki.com · repo open-compass/opencompass · page 1 Introduction to OpenCompass · fetched 2026-10-21 -->

# Introduction to OpenCompass

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README_zh-CN.md](README_zh-CN.md)
- [docs/en/index.rst](docs/en/index.rst)
- [docs/en/notes/news.md](docs/en/notes/news.md)
- [docs/zh_cn/advanced_guides/evaluation_lmdeploy.md](docs/zh_cn/advanced_guides/evaluation_lmdeploy.md)
- [docs/zh_cn/index.rst](docs/zh_cn/index.rst)
- [docs/zh_cn/notes/news.md](docs/zh_cn/notes/news.md)

</details>



## Purpose and Scope

This document provides a high-level introduction to OpenCompass, an open-source platform for evaluating large language models (LLMs). It covers the purpose of OpenCompass, the OpenCompass 2.0 ecosystem, key capabilities, and the fundamental architecture that enables comprehensive model evaluation.

For installation and setup instructions, see [Installation and Setup](#2.1). For running your first evaluation, see [Quick Start Guide](#2.2). For detailed information about specific components, refer to the [Core Architecture](#3) section.

## What is OpenCompass?

OpenCompass is a one-stop platform for large language model evaluation, designed to provide fair, open, and reproducible benchmarks for assessing LLM capabilities. The platform enables researchers and practitioners to systematically evaluate models across multiple dimensions including knowledge, reasoning, coding, and long-context understanding.

The name "OpenCompass" reflects the platform's mission: just as a compass guides navigation, OpenCompass guides users through the complex landscape of LLM evaluation, helping assess model quality and effectiveness with powerful algorithms and an intuitive interface.

**Sources:** [README.md:45-50](), [README_zh-CN.md:45-50](), [README.md:287-297]()

## OpenCompass 2.0 Ecosystem

OpenCompass 2.0 consists of three integrated components that work together to provide a comprehensive evaluation ecosystem:

```mermaid
graph TB
    subgraph "OpenCompass 2.0 Ecosystem"
        CompassKit["CompassKit<br/>Evaluation Toolkits<br/>github.com/open-compass"]
        CompassHub["CompassHub<br/>Benchmark Browser<br/>hub.opencompass.org.cn"]
        CompassRank["CompassRank<br/>Leaderboards<br/>rank.opencompass.org.cn"]
    end
    
    subgraph "Core Platform"
        OpenCompass["OpenCompass<br/>Evaluation Framework<br/>opencompass package"]
    end
    
    subgraph "User Workflows"
        Research["Research & Development"]
        BenchmarkDiscovery["Benchmark Discovery"]
        ResultComparison["Model Comparison"]
    end
    
    Research --> CompassKit
    CompassKit --> OpenCompass
    OpenCompass --> CompassRank
    
    BenchmarkDiscovery --> CompassHub
    CompassHub --> OpenCompass
    
    ResultComparison --> CompassRank
    CompassRank -.provides data.-> Research
    
    CompassHub -.dataset metadata.-> CompassRank
```

### CompassKit

CompassKit is a collection of evaluation toolkits specifically designed for large language models and large vision-language models. It provides specialized evaluation methods including:

- **Inference strategies**: Generation, perplexity scoring, self-consistency, tree-of-thought reasoning
- **Domain-specific evaluators**: Code execution, mathematical verification, symbolic reasoning
- **Subjective evaluation**: LLM-as-judge frameworks for complex assessment scenarios

### CompassHub

CompassHub ([hub.opencompass.org.cn](https://hub.opencompass.org.cn/home)) serves as a benchmark browser interface that simplifies the exploration and utilization of evaluation benchmarks. It provides:

- Searchable catalog of 70+ evaluation datasets
- Benchmark metadata and documentation
- Dataset submission portal for community contributions
- Integration with OpenCompass for seamless evaluation

### CompassRank

CompassRank ([rank.opencompass.org.cn](https://rank.opencompass.org.cn/home)) presents comprehensive leaderboards for model performance comparison. It incorporates both open-source and proprietary benchmarks, enabling industry-wide model assessment.

**Sources:** [README.md:272-282](), [README_zh-CN.md:266-274]()

## Key Capabilities

OpenCompass provides comprehensive features for LLM evaluation:

| Capability | Description |
|------------|-------------|
| **Model Support** | 20+ HuggingFace models, API models (OpenAI, Claude, Gemini, etc.), and custom models |
| **Dataset Coverage** | 70+ datasets with ~400,000 evaluation questions across multiple domains |
| **Evaluation Dimensions** | Knowledge, reasoning, coding, long-context, language understanding |
| **Evaluation Paradigms** | Zero-shot, few-shot, chain-of-thought, self-consistency, tree-of-thought |
| **Inference Backends** | Native HuggingFace, VLLM, LMDeploy/TurboMind acceleration |
| **Distributed Execution** | Local, Slurm HPC, cloud clusters (Alibaba DLC, Volcano) |
| **Result Management** | Persistent storage, result reuse, automated summarization |
| **Extensibility** | Registry-based plugin architecture for custom components |

**Sources:** [README.md:287-297](), [README.md:313-366]()

## High-Level Architecture

OpenCompass follows a modular architecture organized into distinct layers:

### System Components and Code Entities

```mermaid
graph TB
    subgraph "Entry Points"
        CLI["CLI Interface<br/>run.py<br/>opencompass command"]
        ConfigFiles["Configuration Files<br/>configs/models/<br/>configs/datasets/"]
        Examples["Python API<br/>examples/*.py"]
    end
    
    subgraph "Core Orchestration [opencompass/]"
        RunSystem["run.py<br/>get_config_from_arg()<br/>parse_args()"]
        Partitioners["BasePartitioner<br/>NumWorkerPartitioner<br/>SubjectiveNaivePartitioner"]
        Runners["LocalRunner<br/>SlurmRunner<br/>DLCRunner"]
    end
    
    subgraph "Task Execution [opencompass/tasks/]"
        InferTask["OpenICLInferTask<br/>inference execution"]
        EvalTask["OpenICLEvalTask<br/>objective evaluation"]
        SubjTask["SubjectiveEvalTask<br/>subjective evaluation"]
    end
    
    subgraph "Model Layer [opencompass/models/]"
        ModelRegistry["MODELS registry<br/>@MODELS.register_module()"]
        BaseModel["BaseModel<br/>BaseAPIModel"]
        HFModels["HuggingFaceBaseModel<br/>HuggingFacewithChatTemplate"]
        APIModels["OpenAI<br/>Claude<br/>Gemini"]
    end
    
    subgraph "Dataset Layer [opencompass/datasets/]"
        DatasetRegistry["LOAD_DATASET registry<br/>@LOAD_DATASET.register_module()"]
        BaseDataset["BaseDataset.load()"]
        Datasets["MMLU<br/>GSM8K<br/>HumanEval"]
    end
    
    subgraph "Evaluation [opencompass/openicl/]"
        InferencerRegistry["ICL_INFERENCERS registry"]
        EvaluatorRegistry["ICL_EVALUATORS registry"]
        Inferencers["GenInferencer<br/>PPLInferencer<br/>SCInferencer"]
        Evaluators["AccEvaluator<br/>LMEvaluator"]
    end
    
    CLI --> RunSystem
    ConfigFiles --> RunSystem
    Examples --> RunSystem
    
    RunSystem --> Partitioners
    Partitioners --> Runners
    
    Runners --> InferTask
    Runners --> EvalTask
    Runners --> SubjTask
    
    InferTask --> ModelRegistry
    InferTask --> DatasetRegistry
    InferTask --> InferencerRegistry
    
    EvalTask --> EvaluatorRegistry
    SubjTask --> EvaluatorRegistry
    
    ModelRegistry --> BaseModel
    BaseModel --> HFModels
    BaseModel --> APIModels
    
    DatasetRegistry --> BaseDataset
    BaseDataset --> Datasets
    
    InferencerRegistry --> Inferencers
    EvaluatorRegistry --> Evaluators
```

### Architecture Layers

**User Interface Layer**: Provides multiple entry points for initiating evaluations:
- `run.py` - Main CLI entry point
- `opencompass` command - Installed command-line tool
- Configuration files in `configs/` directory
- Python scripts in `examples/` directory

**Core Orchestration Layer**: Manages evaluation workflow:
- `opencompass/utils/run.py` - Configuration parsing and task orchestration via `get_config_from_arg()` and `parse_args()`
- Task partitioners - Split work across workers (`BasePartitioner`, `NumWorkerPartitioner`, `SubjectiveNaivePartitioner`)
- Execution runners - Handle different execution environments (`LocalRunner`, `SlurmRunner`, `DLCRunner`, `VOLCRunner`)

**Task Execution Layer**: Executes evaluation tasks:
- `OpenICLInferTask` - Model inference phase
- `OpenICLEvalTask` - Objective evaluation with rule-based metrics
- `SubjectiveEvalTask` - Subjective evaluation with LLM judges

**Model Integration Layer**: Abstracts model interfaces:
- `MODELS` registry - Enables plugin-based model registration
- `BaseModel` and `BaseAPIModel` - Abstract base classes
- Implementations for HuggingFace models, API models, and accelerated backends

**Dataset Management Layer**: Handles dataset loading and processing:
- `LOAD_DATASET` registry - Plugin-based dataset registration
- `BaseDataset` - Abstract dataset interface with `load()` method
- Pre-configured datasets (MMLU, GSM8K, HumanEval, etc.)

**Evaluation Framework Layer**: Provides evaluation strategies:
- `ICL_INFERENCERS` registry - Inference strategy plugins
- `ICL_EVALUATORS` registry - Evaluator plugins
- Multiple inference strategies (generation, perplexity, self-consistency, etc.)
- Diverse evaluators (accuracy, LLM-based, domain-specific)

**Sources:** [opencompass/utils/run.py:1-100]() (inferred), Architecture Diagram 1

## Evaluation Pipeline Overview

The evaluation process follows a well-defined pipeline from configuration to results:

### End-to-End Evaluation Flow

```mermaid
flowchart TD
    Start["User Input<br/>CLI/Config/Script"] --> Parse["parse_args()<br/>get_config_from_arg()"]
    
    Parse --> FillConfig["fill_infer_cfg()<br/>fill_eval_cfg()"]
    
    FillConfig --> Accel{Accelerator?}
    Accel -->|"--accelerator vllm"| VLLM["change_accelerator()<br/>Transform to VLLM"]
    Accel -->|"--accelerator lmdeploy"| LMDeploy["change_accelerator()<br/>Transform to TurboMind"]
    Accel -->|none| Keep["Keep HuggingFace"]
    
    VLLM --> Partition["Build Partitioner<br/>NumWorkerPartitioner<br/>SubjectiveNaivePartitioner"]
    LMDeploy --> Partition
    Keep --> Partition
    
    Partition --> TaskList["Task Configuration List"]
    
    TaskList --> Runner["Build Runner<br/>LocalRunner/SlurmRunner<br/>DLCRunner/VOLCRunner"]
    
    Runner --> Infer["Inference Phase<br/>OpenICLInferTask"]
    
    Infer --> Reuse{--reuse?}
    Reuse -->|yes| Station["read_from_station()<br/>Load cached results"]
    Reuse -->|no| FullInfer["Execute Inference"]
    Station --> FilterTasks["Filter completed"]
    FilterTasks --> FullInfer
    
    FullInfer --> Strategy{Strategy?}
    Strategy -->|generation| GenInf["GenInferencer"]
    Strategy -->|perplexity| PPLInf["PPLInferencer"]
    Strategy -->|self-consistency| SCInf["SCInferencer"]
    
    GenInf --> SavePred["Save predictions/<br/>model_dataset.json"]
    PPLInf --> SavePred
    SCInf --> SavePred
    
    SavePred --> Eval["Evaluation Phase<br/>OpenICLEvalTask"]
    
    Eval --> EvalType{Type?}
    EvalType -->|objective| ObjEval["Rule-based Evaluators<br/>AccEvaluator"]
    EvalType -->|subjective| SubjEval["SubjectiveEvalTask<br/>LMEvaluator"]
    
    ObjEval --> SaveResults["Save results/<br/>model_dataset.json"]
    SubjEval --> SaveResults
    
    SaveResults --> Summarize["Summarization<br/>DefaultSummarizer"]
    
    Summarize --> Report["Generate Reports<br/>CSV/TXT/JSON"]
    
    Report --> End["Evaluation Complete"]
```

### Pipeline Stages

1. **Configuration Stage**: Parse user input from CLI arguments, configuration files, or Python scripts using `parse_args()` and `get_config_from_arg()`

2. **Setup Stage**: Fill inference and evaluation configurations with `fill_infer_cfg()` and `fill_eval_cfg()`, optionally transform models to accelerated backends via `change_accelerator()`

3. **Partitioning Stage**: Split evaluation tasks across workers using partitioners (`NumWorkerPartitioner` for objective, `SubjectiveNaivePartitioner` for subjective)

4. **Inference Stage**: Execute model inference through `OpenICLInferTask`, applying selected inference strategy (`GenInferencer`, `PPLInferencer`, `SCInferencer`, etc.)

5. **Result Storage**: Save predictions to `predictions/` directory, check for cached results with `read_from_station()` if `--reuse` flag is set

6. **Evaluation Stage**: Score predictions using `OpenICLEvalTask` for objective evaluation or `SubjectiveEvalTask` for LLM-judge evaluation

7. **Summarization Stage**: Aggregate results across datasets and models, generate reports in CSV/TXT/JSON formats

**Sources:** Architecture Diagram 2, [README.md:177-270]()

## Registry System and Plugin Architecture

OpenCompass uses a registry-based plugin architecture that enables easy extension of the platform with new models, datasets, and evaluation strategies.

### Core Registries

| Registry | Purpose | Usage |
|----------|---------|-------|
| `MODELS` | Register model implementations | `@MODELS.register_module()` |
| `LOAD_DATASET` | Register dataset loaders | `@LOAD_DATASET.register_module()` |
| `ICL_INFERENCERS` | Register inference strategies | `@ICL_INFERENCERS.register_module()` |
| `ICL_EVALUATORS` | Register evaluation metrics | `@ICL_EVALUATORS.register_module()` |
| `TEXT_POSTPROCESSORS` | Register output postprocessors | `@TEXT_POSTPROCESSORS.register_module()` |
| `ICL_PROMPT_TEMPLATES` | Register prompt templates | `@ICL_PROMPT_TEMPLATES.register_module()` |

Components self-register by decorating their class definitions with the appropriate registry decorator. Configuration files reference registered components by their string names, which the registry resolves to the actual implementation at runtime.

For detailed information on the registry system, see [Registry System and Plugin Architecture](#3.2). For adding custom components, see [Contributing to OpenCompass](#10.1).

**Sources:** Architecture Diagram 1, Architecture Diagram 3

## Getting Started

To begin using OpenCompass:

1. **Install OpenCompass**: Follow the [Installation and Setup](#2.1) guide to set up the environment and prepare datasets

2. **Run Your First Evaluation**: Use the [Quick Start Guide](#2.2) to execute a simple evaluation with pre-configured models and datasets

3. **Understand Configuration**: Learn about the [Configuration System](#2.3) to customize evaluations for your needs

4. **Explore Models and Datasets**: Browse supported [models](#4) and [datasets](#5) or add your own custom components

5. **Review Results**: Learn about [Result Management and Analysis](#8) to interpret and visualize evaluation outcomes

For troubleshooting common issues, consult the [FAQ and Troubleshooting](#2.4) page.

**Sources:** [README.md:92-270](), [docs/en/index.rst:7-19]()

## Additional Resources

- **Official Website**: [opencompass.org.cn](https://opencompass.org.cn)
- **Documentation**: [opencompass.readthedocs.io](https://opencompass.readthedocs.io/en/latest)
- **GitHub Repository**: [github.com/open-compass/opencompass](https://github.com/open-compass/opencompass)
- **CompassHub**: [hub.opencompass.org.cn](https://hub.opencompass.org.cn/home)
- **CompassRank**: [rank.opencompass.org.cn](https://rank.opencompass.org.cn/home)
- **Discord Community**: Join for discussions and support
- **Issue Tracker**: Report bugs and request features on GitHub

**Sources:** [README.md:16-21](), [README_zh-CN.md:16-21]()

---

