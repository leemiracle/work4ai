<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/olmo-cookbook · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [pyproject.toml](pyproject.toml)

</details>



## Purpose and Scope

The `olmo-cookbook` repository is a comprehensive toolkit for managing the complete lifecycle of OLMo (Open Language Model) experiments, from training through evaluation and deployment. It serves as an orchestration layer that abstracts complex interactions with cloud platforms, compute resources, and machine learning infrastructure while providing a unified command-line interface for researchers and engineers.

This document provides an architectural overview of the entire system. For detailed information about specific subsystems, see [Configuration and Constants System](#2) for the central configuration management, [Evaluation System](#4) for comprehensive model evaluation workflows, [Training System](#5) for model training orchestration, and [Infrastructure Management](#6) for compute resource management.

## System Architecture

The olmo-cookbook system is built around four primary CLI interfaces that coordinate different aspects of the model development workflow:

```mermaid
graph TB
    subgraph "CLI_Layer" ["Command Line Interface Layer"]
        MAIN["olmo-cookbook<br/>(Main Training CLI)"]
        EVAL["olmo-cookbook-eval<br/>(Evaluation CLI)"]
        CORE["olmo-cookbook-core<br/>(OLMo-core Training)"]
        PMR["poormanray<br/>(Infrastructure Management)"]
    end
    
    subgraph "Core_Systems" ["Core Systems"]
        CONFIG["Configuration Management<br/>(constants.py)"]
        TASK_REGISTRY["NamedTasksGroupRegistry<br/>(Task Management)"]
        CONFIG_BUILDER["TransformerConfigBuilder<br/>(Training Config)"]
        EVALUATION_ENGINE["evaluate_checkpoint<br/>(Evaluation Engine)"]
    end
    
    subgraph "Execution_Platforms" ["Execution Platforms"]
        BEAKER["Beaker Platform<br/>(Remote Clusters)"]
        EC2["AWS EC2<br/>(Distributed Processing)"]
        LOCAL["Local Environment<br/>(PythonEnv)"]
    end
    
    subgraph "External_Services" ["External Services"]
        STORAGE["Cloud Storage<br/>(S3/GCS/Weka)"]
        WANDB["Weights & Biases<br/>(Experiment Tracking)"]
        HF["Hugging Face<br/>(Model Hub)"]
        DATALAKE["oe-eval-datalake<br/>(Results Storage)"]
    end
    
    MAIN --> CONFIG_BUILDER
    EVAL --> TASK_REGISTRY
    EVAL --> EVALUATION_ENGINE
    CORE --> CONFIG_BUILDER
    PMR --> EC2
    
    CONFIG_BUILDER --> BEAKER
    CONFIG_BUILDER --> LOCAL
    EVALUATION_ENGINE --> BEAKER
    EVALUATION_ENGINE --> LOCAL
    TASK_REGISTRY --> EVALUATION_ENGINE
    
    BEAKER --> STORAGE
    BEAKER --> WANDB
    EC2 --> STORAGE
    LOCAL --> STORAGE
    
    EVALUATION_ENGINE --> DATALAKE
    CONFIG_BUILDER --> HF
```

**Sources:** [pyproject.toml:57-61](), [README.md:1-318]()

## Core Components and Code Structure

The system's architecture maps directly to specific code entities and modules:

```mermaid
graph TB
    subgraph "CLI_Entry_Points" ["CLI Entry Points (pyproject.toml)"]
        CLI_MAIN["olmo-cookbook<br/>cookbook.cli:cli.cli"]
        CLI_EVAL["olmo-cookbook-eval<br/>cookbook.cli:eval.cli"]
        CLI_CORE["olmo-cookbook-core<br/>cookbook.cli:core.cli"]
        CLI_PMR["poormanray<br/>cookbook.cli:pmr.cli"]
    end
    
    subgraph "Configuration_Layer" ["Configuration Layer"]
        CONSTANTS["constants.py<br/>• MODEL_REPOS<br/>• TASK_SETS<br/>• BEAKER_CONFIG"]
        YAML_CONFIGS["YAML Configuration Files<br/>• Training recipes<br/>• Data mixes<br/>• Experiment configs"]
    end
    
    subgraph "Evaluation_System" ["Evaluation System"]
        NAMED_TASKS["NamedTasksGroupRegistry<br/>• Task expansion<br/>• Group resolution"]
        CONVERT["conversion.py<br/>• Model format conversion<br/>• OLMo ↔ HuggingFace"]
        EVAL_FUNC["evaluate_checkpoint<br/>• Job orchestration<br/>• Results collection"]
        MINIFRAME["MiniFrame<br/>• Results processing<br/>• Data aggregation"]
    end
    
    subgraph "Training_System" ["Training System"]
        TRANSFORMER_CONFIG["TransformerConfigBuilder<br/>• Beaker job configuration<br/>• Environment setup"]
        TRAIN_SCRIPT["train.py<br/>• OLMo-core integration<br/>• Training execution"]
    end
    
    subgraph "Infrastructure" ["Infrastructure Management"]
        PMR_CORE["PMR Core<br/>• EC2 instance management<br/>• SSH coordination<br/>• Task distribution"]
    end
    
    CLI_MAIN --> TRANSFORMER_CONFIG
    CLI_EVAL --> NAMED_TASKS
    CLI_EVAL --> CONVERT
    CLI_EVAL --> EVAL_FUNC
    CLI_CORE --> TRAIN_SCRIPT
    CLI_PMR --> PMR_CORE
    
    CONSTANTS --> NAMED_TASKS
    CONSTANTS --> TRANSFORMER_CONFIG
    YAML_CONFIGS --> TRANSFORMER_CONFIG
    
    EVAL_FUNC --> MINIFRAME
    TRANSFORMER_CONFIG --> TRAIN_SCRIPT
```

**Sources:** [pyproject.toml:57-61](), [README.md:46-56](), [README.md:140-171](), [README.md:173-227](), [README.md:228-318]()

## Key Workflows

The olmo-cookbook supports three primary workflows, each accessible through dedicated CLI interfaces:

### Training Workflow
The training workflow uses configuration-driven job submission to cloud platforms:

1. **Configuration Building**: The `TransformerConfigBuilder` processes YAML recipe files ([README.md:48]()) and system constants to generate Beaker job specifications
2. **Job Launch**: The `olmo-cookbook launch` command ([README.md:54]()) submits configured training jobs to Beaker clusters
3. **Monitoring**: Integration with Weights & Biases provides real-time training metrics ([README.md:56]())

### Evaluation Workflow  
The evaluation system provides comprehensive model assessment capabilities:

1. **Model Conversion**: The `olmo-cookbook-eval convert` command ([README.md:64-89]()) transforms checkpoints between OLMo and HuggingFace formats
2. **Task Execution**: The `olmo-cookbook-eval evaluate` command ([README.md:101-123]()) runs evaluation tasks using the `NamedTasksGroupRegistry` system
3. **Results Retrieval**: The `olmo-cookbook-eval results` command ([README.md:127-137]()) queries the datalake for formatted results

### Infrastructure Workflow
The infrastructure management system enables distributed processing on EC2:

1. **Cluster Creation**: The `poormanray create` command ([README.md:242-258]()) provisions EC2 instance clusters
2. **Task Distribution**: The `poormanray map` command ([README.md:280-286]()) distributes processing tasks across instances  
3. **Resource Cleanup**: The `poormanray terminate` command ([README.md:289-294]()) manages resource lifecycle

**Sources:** [README.md:5-57](), [README.md:58-137](), [README.md:173-318]()

## Dependencies and Integration Points

The system integrates with multiple external platforms and frameworks through well-defined interfaces:

| Integration | Purpose | Configuration Source |
|-------------|---------|---------------------|
| **OLMo-core** | Training framework | [pyproject.toml:51]() |
| **Beaker Platform** | Remote job orchestration | [pyproject.toml:39-42]() |
| **Weights & Biases** | Experiment tracking | [pyproject.toml:43-45]() |
| **AWS/GCP** | Cloud storage and compute | [pyproject.toml:46-49]() |
| **HuggingFace** | Model distribution | Core dependencies |

The system requires Python 3.10-3.13 ([pyproject.toml:13]()) and supports optional dependency groups for different use cases, including development tools ([pyproject.toml:34-38]()), Beaker integration ([pyproject.toml:39-42]()), and checkpoint management ([pyproject.toml:46-49]()).

**Sources:** [pyproject.toml:15-55](), [README.md:17-29](), [README.md:32-44]()

---

