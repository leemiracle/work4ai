<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/olmo-cookbook · page 2 Configuration and Constants System · fetched 2026-10-26 -->

# Configuration and Constants System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/cookbook/aliases.py](src/cookbook/aliases.py)
- [src/cookbook/constants.py](src/cookbook/constants.py)

</details>



The Configuration and Constants System serves as the central configuration hub for all OLMo Cookbook operations, providing a unified source of truth for model repositories, evaluation benchmarks, platform settings, and experiment configurations. This system ensures consistency across training, evaluation, and infrastructure management workflows.

For information about how these configurations are used in specific workflows, see Training Configuration ([#5.1](#5.1)) and Evaluation Task Management ([#4.1](#4.1)).

## Core Constants Architecture

The system is built around two primary components: a constants module that defines static system-wide values, and a configuration system that handles dynamic experiment and runtime settings.

```mermaid
graph TB
    subgraph "Constants Module"
        CONSTANTS_PY["constants.py"]
        MODEL_REPOS["Model Repository URLs"]
        PLATFORM_CONFIG["Platform Configuration"]
        TASK_DEFS["Task Definitions"]
        INFRA_SETTINGS["Infrastructure Settings"]
    end
    
    subgraph "Configuration System"  
        ALIASES_PY["aliases.py"]
        EXP_CONFIG["ExperimentConfig"]
        DATASET_CONFIG["DatasetConfig"]
        METRICS_CONFIG["MetricsConfig"]
        SOURCE_CONFIG["SourceConfig"]
    end
    
    subgraph "System Consumers"
        EVAL_SYSTEM["Evaluation System"]
        TRAIN_SYSTEM["Training System"] 
        INFRA_SYSTEM["Infrastructure System"]
        CONFIG_BUILDER["TransformerConfigBuilder"]
    end
    
    CONSTANTS_PY --> MODEL_REPOS
    CONSTANTS_PY --> PLATFORM_CONFIG
    CONSTANTS_PY --> TASK_DEFS
    CONSTANTS_PY --> INFRA_SETTINGS
    
    ALIASES_PY --> EXP_CONFIG
    ALIASES_PY --> DATASET_CONFIG
    ALIASES_PY --> METRICS_CONFIG
    ALIASES_PY --> SOURCE_CONFIG
    
    MODEL_REPOS --> EVAL_SYSTEM
    PLATFORM_CONFIG --> TRAIN_SYSTEM
    TASK_DEFS --> EVAL_SYSTEM
    INFRA_SETTINGS --> INFRA_SYSTEM
    
    EXP_CONFIG --> CONFIG_BUILDER
    DATASET_CONFIG --> TRAIN_SYSTEM
    METRICS_CONFIG --> TRAIN_SYSTEM
```

**System Constants Flow**

Sources: [src/cookbook/constants.py:1-1173](), [src/cookbook/aliases.py:1-154]()

## Model and Repository Configuration

The system maintains version-controlled references to all external dependencies, ensuring reproducible builds and conversions across different model formats.

| Constant | Purpose | Example Value |
|----------|---------|---------------|
| `TRANSFORMERS_GIT_URL` | HuggingFace Transformers repository | `https://github.com/huggingface/transformers.git` |
| `TRANSFORMERS_COMMIT_HASH` | Pinned commit for reproducibility | `241c04d36867259cdf11dbb4e9d9a60f9cb65ebc` |
| `AI2_OLMO_GIT_URL` | OLMo main repository | `https://github.com/allenai/OLMo.git` |
| `AI2_OLMO_CORE_GIT_URL` | OLMo Core repository | `https://github.com/allenai/OLMo-core.git` |

```mermaid
graph LR
    subgraph "Model Types"
        OLMO_TYPES["OLMO_TYPES"]
        OLMOE["olmoe"]
        OLMO2["olmo2"] 
        OLMO_CORE["olmo-core"]
        OLMO_CORE_V2["olmo-core-v2"]
    end
    
    subgraph "Conversion Scripts"
        OLMOE_CONV["OLMOE_CONVERSION_SCRIPT"]
        OLMO2_CONV["OLMO2_CONVERSION_SCRIPT"]
        OLMO_CORE_CONV["OLMO_CORE_CONVERT_FROM_HF_SCRIPT"]
    end
    
    subgraph "Default Tokenizers"
        OLMOE_TOK["DEFAULT_OLMOE_TOKENIZER"]
        OLMO2_TOK["DEFAULT_OLMO2_TOKENIZER"]
        OLMO_CORE_TOK["DEFAULT_OLMO_CORE_TOKENIZER"]
    end
    
    OLMO_TYPES --> OLMOE
    OLMO_TYPES --> OLMO2
    OLMO_TYPES --> OLMO_CORE
    OLMO_TYPES --> OLMO_CORE_V2
    
    OLMOE --> OLMOE_CONV
    OLMO2 --> OLMO2_CONV
    OLMO_CORE --> OLMO_CORE_CONV
    
    OLMOE --> OLMOE_TOK
    OLMO2 --> OLMO2_TOK
    OLMO_CORE --> OLMO_CORE_TOK
```

**Model Configuration Mapping**

Sources: [src/cookbook/constants.py:3-26](), [src/cookbook/constants.py:35-35]()

## Platform and Infrastructure Settings

The system defines comprehensive platform configurations for Beaker clusters, AWS infrastructure, and storage systems.

### Beaker Platform Configuration

```mermaid
graph TB
    subgraph "Beaker Settings"
        BEAKER_WORKSPACE["BEAKER_DEFAULT_WORKSPACE<br/>ai2/oe-data"]
        BEAKER_BUDGET["BEAKER_DEFAULT_BUDGET<br/>ai2/oe-base"]
        BEAKER_PRIORITY["BEAKER_DEFAULT_PRIORITY<br/>normal"]
    end
    
    subgraph "Cluster Definitions"
        BEAKER_CLUSTERS["BEAKER_KNOWN_CLUSTERS"]
        AUS["aus<br/>jupiter-cirrascale-2<br/>neptune-cirrascale<br/>saturn-cirrascale<br/>ceres-cirrascale"]
        GOOG["goog<br/>augusta-google-1"]
        H100["h100<br/>augusta-google-1<br/>jupiter-cirrascale-2<br/>ceres-cirrascale"]
        A100["a100<br/>saturn-cirrascale"]
    end
    
    subgraph "Storage Mounts"
        WEKA_MOUNTS["WEKA_MOUNTS"]
        OE_DATA["oe-data-default"]
        OE_EVAL["oe-eval-default"] 
        OE_TRAINING["oe-training-default"]
    end
    
    BEAKER_CLUSTERS --> AUS
    BEAKER_CLUSTERS --> GOOG
    BEAKER_CLUSTERS --> H100
    BEAKER_CLUSTERS --> A100
    
    WEKA_MOUNTS --> OE_DATA
    WEKA_MOUNTS --> OE_EVAL
    WEKA_MOUNTS --> OE_TRAINING
```

**Infrastructure Configuration Hierarchy**

Sources: [src/cookbook/constants.py:28-83](), [src/cookbook/constants.py:37-51](), [src/cookbook/constants.py:53-83]()

## Evaluation Task Definitions

The system provides comprehensive task definitions organized into logical groupings for different evaluation scenarios.

### Core Task Categories

| Task Group | Description | Example Tasks |
|------------|-------------|---------------|
| `ALL_CORE_TASKS` | Fundamental reasoning benchmarks | `arc_easy`, `boolq`, `hellaswag` |
| `MMLU_CATEGORIES` | Massive Multitask Language Understanding | `mmlu_abstract_algebra`, `mmlu_anatomy` |
| `BBH_TASKS` | Big-Bench Hard reasoning tasks | `boolean_expressions`, `logical_deduction` |
| `ALL_CODEX_TASKS` | Code generation benchmarks | `codex_humaneval`, `mbpp`, `bigcodebench` |

### Evaluation Suite Structure

```mermaid
graph TD
    subgraph "Task Suites"
        HELMET_SUITES["HELMET_SUITES"]
        RULER_SUITES["RULER_SUITES"]
        MMLU_SUBCATEGORIES["MMLU_SUBCATEGORIES"]
    end
    
    subgraph "Context Length Categories"
        HELMET_8K["helmet_*__8192::suite"]
        HELMET_16K["helmet_*__16384::suite"]  
        HELMET_32K["helmet_*__32768::suite"]
        HELMET_64K["helmet_*__65536::suite"]
        HELMET_128K["helmet_*__131072::suite"]
    end
    
    subgraph "Task Types"
        CITE["helmet_cite"]
        ICL["helmet_icl"]
        LONGQA["helmet_longqa"]
        NIAH["helmet_niah"]
        RAG["helmet_rag"]
    end
    
    HELMET_SUITES --> HELMET_8K
    HELMET_SUITES --> HELMET_16K
    HELMET_SUITES --> HELMET_32K
    HELMET_SUITES --> HELMET_64K
    HELMET_SUITES --> HELMET_128K
    
    HELMET_8K --> CITE
    HELMET_8K --> ICL
    HELMET_8K --> LONGQA
    HELMET_8K --> NIAH
    HELMET_8K --> RAG
```

**Evaluation Task Hierarchy**

Sources: [src/cookbook/constants.py:85-537](), [src/cookbook/constants.py:230-408](), [src/cookbook/constants.py:410-537]()

## Experiment Configuration System

The configuration system uses Pydantic models to ensure type safety and validation for experiment definitions.

### Configuration Model Hierarchy

```mermaid
graph TB
    subgraph "Core Configuration Models"
        EXP_CONFIG["ExperimentConfig"]
        DATASET_CONFIG["DatasetConfig"] 
        METRICS_CONFIG["MetricsConfig"]
        SOURCE_CONFIG["SourceConfig"]
    end
    
    subgraph "Supporting Types"
        SCHEDULER_TYPE["SchedulerType<br/>COSINE, LINEAR, WSD"]
        METRIC_BACKEND["MetricBackend<br/>wandb, comet"]
        ANNEAL_CONFIG["AnnealConfig"]
    end
    
    subgraph "Instance Models"
        EXP_INSTANCE["ExperimentInstance"]
        SOURCE_INSTANCE["SourceInstance"]
        EXP_GROUP["ExperimentGroup"]
        LAUNCH_GROUP["LaunchGroup"]
    end
    
    EXP_CONFIG --> DATASET_CONFIG
    EXP_CONFIG --> METRICS_CONFIG
    EXP_CONFIG --> ANNEAL_CONFIG
    EXP_CONFIG --> SCHEDULER_TYPE
    
    DATASET_CONFIG --> SOURCE_CONFIG
    METRICS_CONFIG --> METRIC_BACKEND
    
    EXP_GROUP --> EXP_CONFIG
    EXP_GROUP --> EXP_INSTANCE
    EXP_INSTANCE --> SOURCE_INSTANCE
    LAUNCH_GROUP --> EXP_INSTANCE
```

**Configuration Class Relationships**

Sources: [src/cookbook/aliases.py:77-130](), [src/cookbook/aliases.py:23-43](), [src/cookbook/aliases.py:50-55]()

### ExperimentConfig Structure

The `ExperimentConfig` class serves as the primary container for experiment settings:

```mermaid
graph LR
    subgraph "Required Fields"
        NAME["name"]
        DESCRIPTION["description"]
        BUDGET["budget"]
        WORKSPACE["workspace"]
        NODES["nodes"]
        GPUS["gpus"]
    end
    
    subgraph "Training Parameters"
        MAX_TOKENS["max_tokens"]
        SEQ_LENGTH["sequence_length"]
        BATCH_SIZE["global_batch_size"]
        LEARNING_RATE["learning_rate"]
    end
    
    subgraph "Platform Settings"
        CLUSTER["cluster"]
        PRIORITY["priority"]
        PREEMPTIBLE["preemptible"]
        WEKA["weka"]
    end
    
    subgraph "Model Configuration"
        MODEL["model: ModelConfigIdentifier"]
        TOKENIZER["tokenizer"]
        LOAD_PATH["load_path"]
        LOAD_STATE["load_state"]
    end
    
    NAME --> DESCRIPTION
    BUDGET --> WORKSPACE
    NODES --> GPUS
    
    MAX_TOKENS --> SEQ_LENGTH
    SEQ_LENGTH --> BATCH_SIZE
    BATCH_SIZE --> LEARNING_RATE
    
    CLUSTER --> PRIORITY
    PRIORITY --> PREEMPTIBLE
    PREEMPTIBLE --> WEKA
    
    MODEL --> TOKENIZER
    TOKENIZER --> LOAD_PATH
    LOAD_PATH --> LOAD_STATE
```

**ExperimentConfig Field Organization**

Sources: [src/cookbook/aliases.py:77-113]()

## Configuration Flow and Usage

The configuration system integrates with all major components of the OLMo Cookbook, providing a consistent interface for accessing system settings.

```mermaid
graph TB
    subgraph "Configuration Sources"
        CONSTANTS["constants.py<br/>System-wide constants"]
        YAML_CONFIG["YAML Configuration Files<br/>Experiment definitions"]
        CLI_ARGS["CLI Arguments<br/>Runtime overrides"]
    end
    
    subgraph "Configuration Processing"
        VALIDATE_SOURCES["validate_sources()"]
        EXP_CONFIG_BUILDER["ExperimentConfig Builder"]
        MODEL_VALIDATOR["ModelConfigIdentifier Validator"]
    end
    
    subgraph "System Integration Points"
        BEAKER_LAUNCH["BeakerLaunchConfig"]
        TASK_REGISTRY["NamedTasksGroupRegistry"]
        TRANSFORMER_BUILDER["TransformerConfigBuilder"]
        EVAL_ORCHESTRATOR["evaluate_checkpoint"]
    end
    
    CONSTANTS --> EXP_CONFIG_BUILDER
    YAML_CONFIG --> EXP_CONFIG_BUILDER
    CLI_ARGS --> EXP_CONFIG_BUILDER
    
    EXP_CONFIG_BUILDER --> VALIDATE_SOURCES
    EXP_CONFIG_BUILDER --> MODEL_VALIDATOR
    
    VALIDATE_SOURCES --> BEAKER_LAUNCH
    MODEL_VALIDATOR --> TRANSFORMER_BUILDER
    
    CONSTANTS --> TASK_REGISTRY
    EXP_CONFIG_BUILDER --> EVAL_ORCHESTRATOR
    TASK_REGISTRY --> EVAL_ORCHESTRATOR
```

**Configuration Integration Flow**

Sources: [src/cookbook/aliases.py:147-154](), [src/cookbook/aliases.py:115-121](), [src/cookbook/constants.py:919-923]()

The validation system ensures configuration consistency through several mechanisms:
- Source ratio validation ensures all sources in a dataset have consistent `target_ratio` settings
- Model configuration validation converts string identifiers to proper `ModelConfigIdentifier` objects  
- Annealing validation ensures that annealing configurations are only used with appropriate load paths

This centralized configuration approach enables the OLMo Cookbook to maintain consistency across complex multi-system workflows while providing flexibility for different use cases and deployment scenarios.

---

