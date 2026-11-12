<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/recoma · page 6 Configuration System · fetched 2026-10-26 -->

# Configuration System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [configs/inference/common/default_gemini_pro.libsonnet](configs/inference/common/default_gemini_pro.libsonnet)
- [configs/inference/common/default_gpt_gpt3.5.libsonnet](configs/inference/common/default_gpt_gpt3.5.libsonnet)
- [configs/inference/common/default_togetherai_llama3_70B.libsonnet](configs/inference/common/default_togetherai_llama3_70B.libsonnet)
- [configs/inference/letter_cat/l2m.jsonnet](configs/inference/letter_cat/l2m.jsonnet)

</details>



## Purpose and Scope

The Configuration System in ReComA provides a declarative approach to defining and managing inference setups through JSONNET configuration files. This system orchestrates the entire inference pipeline by specifying models, search algorithms, datasets, and their interconnections. For specific model configurations, see [Language Model Configurations](#6.1). For task-specific examples, see [Task-Specific Configurations](#6.2). For prompt template management, see [Prompt Templates](#6.3).

## Configuration Architecture Overview

The configuration system uses JSONNET files to define inference setups, which are processed by the `build_configurable_systems` function to create a `ConfigurableSystems` dataclass containing all necessary components.

### Configuration Flow Diagram

```mermaid
graph TD
    subgraph "Configuration Files"
        JSONNET["JSONNET Config Files"]
        DEFAULTS["Default LLM Configs<br/>(.libsonnet files)"]
        PROMPTS["Prompt Templates<br/>(.txt files)"]
    end
    
    subgraph "Configuration Processing"
        BUILD["build_configurable_systems"]
        SYSTEMS["ConfigurableSystems<br/>(dataclass)"]
        REGISTRY["Registry Pattern<br/>(@register decorators)"]
    end
    
    subgraph "System Components"
        MODELS["models: Dict[str, BaseModel]"]
        SEARCH["search_algo: SearchAlgo"]
        READER["reader: DatasetReader"]
        RENDERERS["renderers: List[StateRenderer]"]
        ANSWERERS["answerers: List[AnswerFromState]"]
    end
    
    subgraph "Runtime Execution"
        INFERENCE["run_inference main"]
        PREDICT["SearchAlgo.predict"]
        EXECUTE["Model execution"]
    end
    
    JSONNET --> BUILD
    DEFAULTS --> BUILD
    PROMPTS --> BUILD
    
    BUILD --> SYSTEMS
    BUILD --> REGISTRY
    
    SYSTEMS --> MODELS
    SYSTEMS --> SEARCH
    SYSTEMS --> READER
    SYSTEMS --> RENDERERS
    SYSTEMS --> ANSWERERS
    
    SYSTEMS --> INFERENCE
    INFERENCE --> PREDICT
    PREDICT --> EXECUTE
```

Sources: [configs/inference/letter_cat/l2m.jsonnet:1-32](), [configs/inference/common/default_gpt_gpt3.5.libsonnet:1-9]()

## Configuration File Structure

ReComA configurations are structured as JSONNET files that define four main sections: `models`, `search`, `reader`, and optional components like `renderers` and `answerers`.

### Core Configuration Schema

| Section | Purpose | Required | Example |
|---------|---------|----------|---------|
| `models` | Dictionary of model definitions | Yes | `{"model_name": {"type": "openai_chat", ...}}` |
| `search` | Search algorithm configuration | Yes | `{"type": "best_first", "start_model": "model_name"}` |
| `reader` | Dataset reader configuration | Yes | `{"type": "drop"}` |
| `renderers` | State visualization components | No | `[{"type": "html_renderer"}]` |
| `answerers` | Answer extraction components | No | `[{"type": "tail_output"}]` |

### Configuration Hierarchy and Imports

```mermaid
graph TD
    subgraph "Configuration Structure"
        MAIN["Main Config<br/>(task.jsonnet)"]
        DEFAULTS["Default Configs<br/>(.libsonnet files)"]
        PROMPTS["Prompt Files<br/>(.txt files)"]
    end
    
    subgraph "Import Relationships"
        IMPORT["local generator_params = import '../common/default_gpt.libsonnet'"]
        REFERENCE["'prompt_file': 'configs/prompts/task/prompt.txt'"]
        OVERRIDE["generator_params + {'max_tokens': 300}"]
    end
    
    subgraph "Processed Configuration"
        RESOLVED["Fully Resolved Config"]
        VALIDATED["Registry Validation"]
        INSTANTIATED["Component Instantiation"]
    end
    
    MAIN --> IMPORT
    DEFAULTS --> IMPORT
    PROMPTS --> REFERENCE
    
    IMPORT --> RESOLVED
    REFERENCE --> RESOLVED
    OVERRIDE --> RESOLVED
    
    RESOLVED --> VALIDATED
    VALIDATED --> INSTANTIATED
```

Sources: [configs/inference/letter_cat/l2m.jsonnet:1-2](), [configs/inference/letter_cat/l2m.jsonnet:12-13]()

## Model Configuration Patterns

The configuration system supports multiple model types through a registry pattern, where each model type corresponds to a registered class.

### Model Definition Structure

```mermaid
graph LR
    subgraph "Model Configuration"
        TYPE["'type': 'model_type'"]
        PARAMS["Model-specific Parameters"]
        GENERATOR["'generator_params': {...}"]
    end
    
    subgraph "Registry Resolution"
        REGISTRY["@register('model_type')"]
        CLASS["BaseModel Subclass"]
        INIT["Class.__init__(params)"]
    end
    
    subgraph "Common Model Types"
        OPENAI["'openai_chat'<br/>OpenAIChatGenerator"]
        LITELLM["'lite_llm'<br/>LiteLLMGenerator"]
        PROMPTED["'prompted_lm'<br/>PromptedLMModel"]
        L2M["'l2m_control'<br/>LeastToMostController"]
        REGEX["'regex_ext'<br/>RegexExtractor"]
    end
    
    TYPE --> REGISTRY
    PARAMS --> INIT
    GENERATOR --> INIT
    
    REGISTRY --> CLASS
    CLASS --> INIT
    
    REGISTRY --> OPENAI
    REGISTRY --> LITELLM
    REGISTRY --> PROMPTED
    REGISTRY --> L2M
    REGISTRY --> REGEX
```

Sources: [configs/inference/letter_cat/l2m.jsonnet:4-23](), [configs/inference/common/default_gpt_gpt3.5.libsonnet:2]()

## Generator Parameters and Defaults

Default configurations for language models are stored in `.libsonnet` files and can be imported and extended in task-specific configurations.

### Default Configuration Parameters

| Parameter | Purpose | Common Values |
|-----------|---------|---------------|
| `type` | Model implementation class | `"openai_chat"`, `"lite_llm"` |
| `model` | Model identifier | `"gpt-3.5-turbo-0613"`, `"gemini/gemini-1.5-pro-latest"` |
| `max_tokens` | Maximum output tokens | `100`, `300`, `500` |
| `temperature` | Sampling temperature | `0`, `0.7`, `1.0` |
| `top_p` | Nucleus sampling parameter | `1` |
| `use_cache` | Enable response caching | `true`, `false` |
| `stop` | Stop sequences | `["\n"]`, `["<|endoftext|>"]` |

### Configuration Extension Pattern

```mermaid
graph TD
    subgraph "Default Configuration"
        DEFAULT["default_gpt_gpt3.5.libsonnet"]
        BASE_PARAMS["Base generator_params"]
    end
    
    subgraph "Task Configuration"
        TASK["task.jsonnet"]
        IMPORT["local generator_params = import '...'"]
        EXTEND["generator_params + {'max_tokens': 300}"]
    end
    
    subgraph "Final Configuration"
        MERGED["Merged Parameters"]
        OVERRIDES["Override Values"]
        RESOLVED["Final Model Config"]
    end
    
    DEFAULT --> BASE_PARAMS
    TASK --> IMPORT
    IMPORT --> BASE_PARAMS
    
    BASE_PARAMS --> EXTEND
    EXTEND --> MERGED
    MERGED --> OVERRIDES
    OVERRIDES --> RESOLVED
```

Sources: [configs/inference/letter_cat/l2m.jsonnet:1](), [configs/inference/letter_cat/l2m.jsonnet:18]()

## Search Algorithm Configuration

The search configuration defines how the reasoning process explores the search space through model execution.

### Search Configuration Schema

```mermaid
graph LR
    subgraph "Search Configuration"
        SEARCH_TYPE["'type': 'best_first'"]
        START_MODEL["'start_model': 'model_name'"]
        EARLY_STOP["Early Stopping Conditions"]
    end
    
    subgraph "Search Algorithm Classes"
        BFS["BestFirstSearch"]
        REGISTRY_SEARCH["@register('best_first')"]
        SEARCH_ALGO["SearchAlgo base class"]
    end
    
    subgraph "Search State Management"
        SEARCH_STATE["SearchState"]
        TREE_LIB["treelib.Tree"]
        SEARCH_NODE["SearchNode"]
    end
    
    SEARCH_TYPE --> REGISTRY_SEARCH
    START_MODEL --> BFS
    EARLY_STOP --> BFS
    
    REGISTRY_SEARCH --> BFS
    BFS --> SEARCH_ALGO
    
    BFS --> SEARCH_STATE
    SEARCH_STATE --> TREE_LIB
    SEARCH_STATE --> SEARCH_NODE
```

Sources: [configs/inference/letter_cat/l2m.jsonnet:25-28]()

## Configuration Loading and Validation

The configuration system processes JSONNET files through a validation and instantiation pipeline that ensures all components are properly registered and configured.

### Configuration Processing Pipeline

```mermaid
graph TD
    subgraph "Loading Phase"
        JSONNET_FILE["JSONNET Config File"]
        PARSE["JSON Parsing"]
        RESOLVE["Import Resolution"]
    end
    
    subgraph "Validation Phase"
        TYPE_CHECK["Type Validation"]
        REGISTRY_CHECK["Registry Lookup"]
        PARAM_VALIDATE["Parameter Validation"]
    end
    
    subgraph "Instantiation Phase"
        CREATE_MODELS["Model Instantiation"]
        CREATE_SEARCH["Search Algorithm Creation"]
        CREATE_READER["DatasetReader Creation"]
        CONFIGURABLE_SYSTEMS["ConfigurableSystems Assembly"]
    end
    
    subgraph "Error Handling"
        MISSING_TYPE["Missing 'type' field"]
        UNREGISTERED["Unregistered type"]
        INVALID_PARAMS["Invalid parameters"]
    end
    
    JSONNET_FILE --> PARSE
    PARSE --> RESOLVE
    RESOLVE --> TYPE_CHECK
    
    TYPE_CHECK --> REGISTRY_CHECK
    REGISTRY_CHECK --> PARAM_VALIDATE
    
    PARAM_VALIDATE --> CREATE_MODELS
    CREATE_MODELS --> CREATE_SEARCH
    CREATE_SEARCH --> CREATE_READER
    CREATE_READER --> CONFIGURABLE_SYSTEMS
    
    TYPE_CHECK --> MISSING_TYPE
    REGISTRY_CHECK --> UNREGISTERED
    PARAM_VALIDATE --> INVALID_PARAMS
```

Sources: [configs/inference/letter_cat/l2m.jsonnet:1-32](), [configs/inference/common/default_gpt_gpt3.5.libsonnet:1-9]()

---

