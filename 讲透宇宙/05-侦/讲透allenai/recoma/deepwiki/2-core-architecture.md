<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/recoma · page 2 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [recoma/models/README.md](recoma/models/README.md)
- [recoma/models/core/README.md](recoma/models/core/README.md)
- [recoma/models/core/utility_models.py](recoma/models/core/utility_models.py)
- [recoma/run_inference.py](recoma/run_inference.py)

</details>



This document provides an overview of ReComA's fundamental architecture, explaining the main components and their interactions within the reasoning framework. ReComA orchestrates multiple language models through a search-based approach to solve complex reasoning tasks.

For detailed information about specific subsystems, see [Inference Orchestration](#2.1), [Search System](#2.2), [Model System Architecture](#2.3), and [Dataset Reading Pipeline](#2.4).

## System Overview

ReComA's architecture is built around four core components that work together to enable multi-agent reasoning:

1. **Configuration System** - JSONNET-based declarative configuration loading
2. **Model System** - Pluggable language model abstractions with registration
3. **Search System** - Tree-based exploration of reasoning paths
4. **Data Pipeline** - Standardized dataset reading and output generation

## Primary System Components

ReComA's core architecture centers around the `ConfigurableSystems` dataclass, which serves as the primary container for all system components during runtime.

```mermaid
graph TB
    subgraph "Configuration Layer"
        JSONNET["JSONNET Config Files"]
        ENV["Environment Variables"]
        CLI["Command Line Arguments"]
    end
    
    subgraph "ConfigurableSystems Container"
        READER["DatasetReader"]
        SEARCH["SearchAlgo"]
        RENDERERS["List[StateRenderer]"]
        SOURCE["source_json"]
    end
    
    subgraph "Model Registry"
        MODELS["Dict[str, BaseModel]"]
        BASE["BaseModel.register()"]
        PROMPT["PromptedLMModel"]
        UTIL["UtilityModels"]
    end
    
    subgraph "Runtime Execution"
        INFERENCE["inference_mode()"]
        DEMO["demo_mode()"]
        GRADIO["gradio_demo()"]
    end
    
    JSONNET --> READER
    JSONNET --> SEARCH
    JSONNET --> MODELS
    ENV --> JSONNET
    CLI --> INFERENCE
    CLI --> DEMO
    CLI --> GRADIO
    
    READER --> SOURCE
    SEARCH --> SOURCE
    RENDERERS --> SOURCE
    
    MODELS --> BASE
    BASE --> PROMPT
    BASE --> UTIL
    SEARCH --> MODELS
    
    INFERENCE --> READER
    INFERENCE --> SEARCH
    DEMO --> READER
    DEMO --> SEARCH
    GRADIO --> READER
    GRADIO --> SEARCH
```

**Configuration to Runtime System Mapping**

Sources: [recoma/run_inference.py:24-30](), [recoma/run_inference.py:59-77]()

## Core Data Flow

The system follows a clear data flow from configuration through execution to output generation:

```mermaid
flowchart TD
    subgraph "Initialization Phase"
        CONFIG["build_configurable_systems()"]
        PARSE["parse_arguments()"]
        JSONNET_EVAL["_jsonnet.evaluate_file()"]
    end
    
    subgraph "System Assembly"
        READER_INIT["DatasetReader.from_dict()"]
        MODEL_INIT["BaseModel.from_dict()"]
        SEARCH_INIT["SearchAlgo.from_dict()"]
        RENDERER_INIT["StateRenderer.from_dict()"]
    end
    
    subgraph "Execution Loop"
        READ_EX["reader.get_examples()"]
        SEARCH_PRED["search_algo.predict()"]
        STATE_MANAGE["SearchState management"]
        MODEL_EXEC["BaseModel.__call__()"]
    end
    
    subgraph "Output Generation"
        DUMP_PRED["dump_predictions()"]
        JSON_OUT["predictions.json"]
        JSONL_OUT["all_data.jsonl"]
        HTML_OUT["html_dump/"]
    end
    
    PARSE --> CONFIG
    CONFIG --> JSONNET_EVAL
    JSONNET_EVAL --> READER_INIT
    JSONNET_EVAL --> MODEL_INIT
    JSONNET_EVAL --> SEARCH_INIT
    JSONNET_EVAL --> RENDERER_INIT
    
    READER_INIT --> READ_EX
    READ_EX --> SEARCH_PRED
    SEARCH_PRED --> STATE_MANAGE
    STATE_MANAGE --> MODEL_EXEC
    MODEL_EXEC --> STATE_MANAGE
    
    SEARCH_PRED --> DUMP_PRED
    DUMP_PRED --> JSON_OUT
    DUMP_PRED --> JSONL_OUT
    DUMP_PRED --> HTML_OUT
```

**System Data Flow from Configuration to Output**

Sources: [recoma/run_inference.py:49-77](), [recoma/run_inference.py:109-121](), [recoma/run_inference.py:123-169]()

## Component Interactions

### Configuration System

The configuration system uses JSONNET files to declaratively specify system behavior. The `build_configurable_systems()` function processes these configurations and instantiates the required components.

| Configuration Section | Purpose | Component Created |
|----------------------|---------|-------------------|
| `reader` | Dataset specification | `DatasetReader` |
| `models` | Model definitions | `Dict[str, BaseModel]` |
| `search` | Search algorithm config | `SearchAlgo` |
| `renderers` | Output formatting | `List[StateRenderer]` |

Sources: [recoma/run_inference.py:59-77]()

### Model Registration System

ReComA uses a registration-based pattern for models, allowing runtime discovery and instantiation of different model types:

```mermaid
graph LR
    subgraph "Registration Pattern"
        DECORATOR["@BaseModel.register()"]
        REGISTRY["_registry dict"]
        FROM_DICT["from_dict() factory"]
    end
    
    subgraph "Model Implementations"
        PROMPTED["PromptedLMModel"]
        ROUTER["RouterModel"]
        REGEX["RegexExtractor"]
        CUSTOM["Custom Models"]
    end
    
    DECORATOR --> REGISTRY
    REGISTRY --> FROM_DICT
    
    PROMPTED --> DECORATOR
    ROUTER --> DECORATOR
    REGEX --> DECORATOR
    CUSTOM --> DECORATOR
```

**Model Registration and Discovery System**

Sources: [recoma/models/core/base_model.py](), [recoma/models/core/utility_models.py:12-13](), [recoma/models/core/utility_models.py:41-42]()

### Search Coordination

The search system coordinates model execution through a tree-based state management approach. The `SearchAlgo` receives a model dictionary and orchestrates their execution based on the current search state.

```mermaid
graph TD
    subgraph "Search Control Flow"
        PREDICT["SearchAlgo.predict()"]
        STATE_INIT["SearchState initialization"]
        OPEN_NODE["get_open_node()"]
        MODEL_CALL["BaseModel.__call__()"]
        STATE_UPDATE["SearchState update"]
    end
    
    subgraph "Model Execution"
        TARGET_MODEL["target_model identification"]
        GENERATE["generate_output()"]
        NEW_STATES["List[SearchState]"]
    end
    
    PREDICT --> STATE_INIT
    STATE_INIT --> OPEN_NODE
    OPEN_NODE --> TARGET_MODEL
    TARGET_MODEL --> MODEL_CALL
    MODEL_CALL --> GENERATE
    GENERATE --> NEW_STATES
    NEW_STATES --> STATE_UPDATE
    STATE_UPDATE --> OPEN_NODE
```

**Search Algorithm Coordination Flow**

Sources: [recoma/search/search.py](), [recoma/models/core/base_model.py]()

## Runtime Modes

ReComA supports three primary runtime modes, each serving different use cases:

### Inference Mode
Batch processing mode for evaluating datasets. Processes all examples from an input file and generates comprehensive outputs including predictions, correctness scores, and execution traces.

### Demo Mode
Interactive command-line mode for testing individual examples. Allows real-time input of questions and provides immediate feedback with full reasoning traces.

### Gradio Demo Mode
Web-based interface mode that provides a GUI for interactive reasoning. Combines the accessibility of a web interface with the detailed output of demo mode.

Each mode uses the same underlying `ConfigurableSystems` but provides different interaction patterns for different use cases.

Sources: [recoma/run_inference.py:109-121](), [recoma/run_inference.py:80-107](), [recoma/run_inference.py:171-204]()

## Extension Points

The architecture provides several extension points for customization:

1. **Model Extensions** - New reasoning patterns via `BaseModel` inheritance
2. **Dataset Extensions** - New data formats via `DatasetReader` inheritance  
3. **Search Extensions** - New search strategies via `SearchAlgo` inheritance
4. **Rendering Extensions** - New output formats via `StateRenderer` inheritance

Each extension point uses the same registration pattern, allowing runtime discovery without code modification.

Sources: [recoma/models/core/README.md:1-22](), [recoma/run_inference.py:236-238]()

---

