<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/reward-bench · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

RewardBench is a comprehensive evaluation framework for assessing reward models and preference optimization models. It provides standardized benchmarks, inference pipelines, and analysis tools for evaluating different types of models including sequence classification reward models, Direct Preference Optimization (DPO) models, and generative reward models (LLM-as-a-judge).

This document covers the high-level architecture and components of RewardBench. For specific evaluation procedures, see [Model Evaluation](#5). For CLI usage details, see [CLI Reference](#4). For configuration options, see [Configuration](#6).

## System Architecture

RewardBench consists of multiple interconnected systems that handle model evaluation, data processing, and result analysis. The framework supports both local and distributed evaluation workflows.

### Core System Components

```mermaid
graph TB
    subgraph "Entry Points"
        CLI_RB["rewardbench CLI"]
        CLI_GEN["rewardbench-gen CLI"]
        DIRECT_SCRIPTS["Direct Script Execution"]
    end
    
    subgraph "Evaluation Engines"
        RUN_RM["scripts/run_rm.py"]
        RUN_DPO["scripts/run_dpo.py"]
        RUN_GEN["scripts/run_generative.py"]
        RUN_V2["scripts/run_v2.py"]
    end
    
    subgraph "Model Management"
        EVAL_CONFIGS["scripts/configs/eval_configs.yaml"]
        REWARD_CONFIG["REWARD_MODEL_CONFIG"]
        DPO_CONFIG["DPO_MODEL_CONFIG"]
        MODEL_BUILDERS["rewardbench/models/"]
    end
    
    subgraph "Data Pipeline"
        LOAD_EVAL["load_eval_dataset()"]
        PREPARE_DIALOGUE["prepare_dialogue()"]
        DATASET_SOURCES["HuggingFace Datasets"]
    end
    
    subgraph "Infrastructure"
        BEAKER_SUBMIT["scripts/submit_eval_jobs.py"]
        PIPELINE_CLASSES["RewardBenchPipeline<br/>DPOInference<br/>Custom Pipelines"]
    end
    
    CLI_RB --> RUN_RM
    CLI_RB --> RUN_DPO
    CLI_GEN --> RUN_GEN
    DIRECT_SCRIPTS --> RUN_RM
    DIRECT_SCRIPTS --> RUN_DPO
    DIRECT_SCRIPTS --> RUN_GEN
    DIRECT_SCRIPTS --> RUN_V2
    
    RUN_RM --> EVAL_CONFIGS
    RUN_DPO --> EVAL_CONFIGS
    RUN_GEN --> EVAL_CONFIGS
    RUN_V2 --> EVAL_CONFIGS
    
    EVAL_CONFIGS --> REWARD_CONFIG
    EVAL_CONFIGS --> DPO_CONFIG
    REWARD_CONFIG --> MODEL_BUILDERS
    DPO_CONFIG --> MODEL_BUILDERS
    
    RUN_RM --> LOAD_EVAL
    RUN_DPO --> LOAD_EVAL
    RUN_GEN --> LOAD_EVAL
    RUN_V2 --> LOAD_EVAL
    
    LOAD_EVAL --> PREPARE_DIALOGUE
    LOAD_EVAL --> DATASET_SOURCES
    
    BEAKER_SUBMIT --> RUN_RM
    BEAKER_SUBMIT --> RUN_DPO
    BEAKER_SUBMIT --> RUN_GEN
    
    MODEL_BUILDERS --> PIPELINE_CLASSES
```

Sources: [README.md:1-321](), [scripts/run_rm.py](), [scripts/run_dpo.py](), [scripts/run_generative.py](), [scripts/run_v2.py](), [scripts/configs/eval_configs.yaml]()

## Evaluation Paradigms

RewardBench supports three primary evaluation paradigms, each with distinct model loading and inference approaches:

### Model Evaluation Pipeline

```mermaid
graph TD
    subgraph "Model Type Detection"
        MODEL_INPUT["Model Name/Path"]
        TYPE_DETECT{Model Type Detection}
        REF_MODEL_CHECK{Reference Model Provided?}
    end
    
    subgraph "Reward Model Path"
        RM_CONFIG["REWARD_MODEL_CONFIG lookup"]
        RM_BUILDER["Model Builder Function"]
        RM_PIPELINE["RewardBenchPipeline"]
        RM_INFERENCE["Batch Inference"]
        RM_SCORING["Score Comparison<br/>chosen vs rejected"]
    end
    
    subgraph "DPO Model Path"
        DPO_CONFIG["DPO_MODEL_CONFIG lookup"]
        DPO_LOADER["AutoModelForCausalLM"]
        DPO_INFERENCE_CLS["DPOInference"]
        DPO_LOGPROBS["Log Probability Calculation"]
        DPO_RATIOS["Log Ratio Computation"]
    end
    
    subgraph "Generative Model Path"
        GEN_TYPE{API or Local?}
        API_CLIENT["OpenAI/Anthropic/Together API"]
        LOCAL_VLLM["VLLM Local Inference"]
        LLM_JUDGE["LLM-as-a-Judge Prompts"]
        PARSE_JUDGMENTS["Parse Model Judgments"]
    end
    
    subgraph "Common Processing"
        DATASET_LOAD["load_eval_dataset()"]
        DIALOGUE_PREP["prepare_dialogue()"]
        RESULTS_CALC["calculate_scores_per_section()"]
        HF_UPLOAD["Upload to HuggingFace Hub"]
    end
    
    MODEL_INPUT --> TYPE_DETECT
    TYPE_DETECT --> REF_MODEL_CHECK
    
    REF_MODEL_CHECK -->|No Ref Model| RM_CONFIG
    REF_MODEL_CHECK -->|Has Ref Model| DPO_CONFIG
    TYPE_DETECT -->|Generative| GEN_TYPE
    
    RM_CONFIG --> RM_BUILDER
    RM_BUILDER --> RM_PIPELINE
    RM_PIPELINE --> RM_INFERENCE
    RM_INFERENCE --> RM_SCORING
    
    DPO_CONFIG --> DPO_LOADER
    DPO_LOADER --> DPO_INFERENCE_CLS
    DPO_INFERENCE_CLS --> DPO_LOGPROBS
    DPO_LOGPROBS --> DPO_RATIOS
    
    GEN_TYPE -->|API| API_CLIENT
    GEN_TYPE -->|Local| LOCAL_VLLM
    API_CLIENT --> LLM_JUDGE
    LOCAL_VLLM --> LLM_JUDGE
    LLM_JUDGE --> PARSE_JUDGMENTS
    
    RM_SCORING --> RESULTS_CALC
    DPO_RATIOS --> RESULTS_CALC
    PARSE_JUDGMENTS --> RESULTS_CALC
    
    DATASET_LOAD --> DIALOGUE_PREP
    DIALOGUE_PREP --> RM_INFERENCE
    DIALOGUE_PREP --> DPO_LOGPROBS
    DIALOGUE_PREP --> LLM_JUDGE
    
    RESULTS_CALC --> HF_UPLOAD
```

Sources: [scripts/run_rm.py](), [scripts/run_dpo.py](), [scripts/run_generative.py](), [rewardbench/models/](), [rewardbench/utils.py]()

## CLI Interface and Entry Points

RewardBench provides multiple entry points for different use cases:

| Entry Point | Purpose | Primary Script | Model Types Supported |
|-------------|---------|----------------|----------------------|
| `rewardbench` | Standard evaluation | `scripts/run_rm.py`, `scripts/run_dpo.py` | Reward models, DPO models |
| `rewardbench-gen` | Generative evaluation | `scripts/run_generative.py` | API models, local generative models |
| `python scripts/run_v2.py` | RewardBench 2.0 | `scripts/run_v2.py` | Multi-response evaluation |
| `python scripts/run_generative_v2.py` | Generative v2 | `scripts/run_generative_v2.py` | Generative models on RB 2.0 |

### Command Line Arguments Flow

```mermaid
graph LR
    subgraph "CLI Arguments"
        MODEL_ARG["--model"]
        REF_MODEL_ARG["--ref_model"]
        DATASET_ARG["--dataset"]
        BATCH_SIZE["--batch_size"]
        CHAT_TEMPLATE["--chat_template"]
    end
    
    subgraph "Script Routing"
        ROUTE_LOGIC{"Routing Logic"}
        RM_ROUTE["Route to run_rm.py"]
        DPO_ROUTE["Route to run_dpo.py"]
        GEN_ROUTE["Route to run_generative.py"]
    end
    
    subgraph "Core Functions"
        MAIN_RM["main() in run_rm.py"]
        MAIN_DPO["main() in run_dpo.py"]
        MAIN_GEN["main() in run_generative.py"]
    end
    
    MODEL_ARG --> ROUTE_LOGIC
    REF_MODEL_ARG --> ROUTE_LOGIC
    DATASET_ARG --> ROUTE_LOGIC
    BATCH_SIZE --> ROUTE_LOGIC
    CHAT_TEMPLATE --> ROUTE_LOGIC
    
    ROUTE_LOGIC -->|No ref_model| RM_ROUTE
    ROUTE_LOGIC -->|Has ref_model| DPO_ROUTE
    ROUTE_LOGIC -->|Generative CLI| GEN_ROUTE
    
    RM_ROUTE --> MAIN_RM
    DPO_ROUTE --> MAIN_DPO
    GEN_ROUTE --> MAIN_GEN
```

Sources: [README.md:43-93](), [rewardbench/cli.py](), [scripts/run_rm.py](), [scripts/run_dpo.py](), [scripts/run_generative.py]()

## Core Components Overview

### Model Management System

RewardBench uses a configuration-driven approach to manage different model types:

- **`REWARD_MODEL_CONFIG`**: Dictionary mapping model names to builder functions and pipeline classes
- **`DPO_MODEL_CONFIG`**: Configuration for DPO models with reference model specifications
- **`eval_configs.yaml`**: Per-model parameters including chat templates, batch sizes, and special handling flags

### Data Pipeline

The data pipeline handles multiple dataset formats:

- **`load_eval_dataset()`**: Loads datasets from HuggingFace or local files
- **`prepare_dialogue()`**: Formats conversations using chat templates
- **Automatic format detection**: Detects preference pairs vs instruction datasets

### Inference Engines

Different model types use specialized inference approaches:

- **`RewardBenchPipeline`**: Standard pipeline for sequence classification reward models
- **`DPOInference`**: Handles policy and reference model comparison for DPO models
- **Custom pipelines**: Specialized implementations for models like ArmoRM, PairRM, Starling

### Results and Analysis

RewardBench provides comprehensive result processing:

- **`calculate_scores_per_section()`**: Computes weighted scores across evaluation categories
- **HuggingFace Hub integration**: Automatic upload of results and model metadata
- **Visualization tools**: Plot generation and statistical analysis utilities

Sources: [rewardbench/models/](), [rewardbench/utils.py](), [scripts/configs/eval_configs.yaml](), [README.md:219-256]()

## Supported Model Types

RewardBench supports a wide range of model architectures and training paradigms:

| Model Category | Examples | Key Features |
|----------------|----------|--------------|
| **Sequence Classification RMs** | OpenAssistant/oasst-rm-2.1-pythia-1.4b, PKU-Alignment/beaver-7b-v1.0-cost | Direct reward scoring via classification head |
| **DPO Models** | stabilityai/stablelm-zephyr-3b, Qwen/Qwen1.5-0.5B-Chat | Implicit rewards via policy vs reference comparison |
| **Generative RMs** | gpt-3.5-turbo, claude-3-sonnet, meta-llama/Llama-3-70b-chat-hf | LLM-as-a-judge with structured prompts |
| **Custom Architectures** | ArmoRM, PairRM, Starling, UltraRM | Specialized model implementations |

The framework automatically detects model types and routes to appropriate evaluation pipelines based on model configurations and provided arguments.

Sources: [README.md:144-210](), [rewardbench/models/](), [scripts/configs/eval_configs.yaml]()

---

