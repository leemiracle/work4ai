<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/jeo · page 4 Data Processing · fetched 2026-10-26 -->

# Data Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jeo/pp/pp_builder.py](jeo/pp/pp_builder.py)
- [jeo/pp/pp_utils.py](jeo/pp/pp_utils.py)
- [jeo/tools/bv_optax.py](jeo/tools/bv_optax.py)

</details>



This document covers Jeo's data preprocessing system, which transforms raw data into model-ready formats through a flexible pipeline architecture. The system uses a string-based specification language to define preprocessing operations that are applied sequentially to input data.

For information about specific preprocessing operations, see [Preprocessing Operations](#4.1). For details on configuring and composing preprocessing pipelines, see [Pipeline Configuration](#4.2). For the broader input pipeline system that integrates with datasets, see [Input Pipeline System](#3.1).

## System Overview

Jeo's data preprocessing system is built around a registry-based architecture that allows for flexible composition of preprocessing operations. The system takes inspiration from Google's big_vision library and provides a domain-specific language for specifying preprocessing pipelines as strings.

```mermaid
graph TB
    subgraph "Pipeline Specification"
        ConfigString["Pipeline String<br/>\"decode|resize(224)|flip_lr\""]
        Parser["pp_builder.parse_name<br/>String Parser"]
        Operations["Parsed Operations<br/>[(decode, [], {}), (resize, [224], {})]"]
    end
    
    subgraph "Registry System"
        GlobalRegistry["Registry._GLOBAL_REGISTRY<br/>Global Operation Store"]
        Lookup["Registry.lookup<br/>Operation Retrieval"]
        RegisteredOps["Registered Operations<br/>preprocess_ops.*"]
    end
    
    subgraph "Pipeline Execution"
        PreprocessFn["get_preprocess_fn<br/>Pipeline Constructor"]
        DataDict["Input Data<br/>{\"image\": tensor, ...}"]
        ProcessedData["Processed Data<br/>{\"image\": processed_tensor, ...}"]
    end
    
    subgraph "Utilities"
        PPUtils["pp_utils.py<br/>Helper Functions"]
        InKeyOutKey["InKeyOutKey Decorator<br/>Key Management"]
        Normalization["load_normalization_ranges<br/>Stats Loading"]
    end
    
    ConfigString --> Parser
    Parser --> Operations
    Operations --> Lookup
    GlobalRegistry --> Lookup
    RegisteredOps --> GlobalRegistry
    
    Operations --> PreprocessFn
    Lookup --> PreprocessFn
    PreprocessFn --> ProcessedData
    DataDict --> PreprocessFn
    
    PPUtils --> InKeyOutKey
    PPUtils --> Normalization
    InKeyOutKey -.-> RegisteredOps
    Normalization -.-> RegisteredOps
```

Sources: [jeo/pp/pp_builder.py:1-229](), [jeo/pp/pp_utils.py:1-126]()

## Pipeline Specification Language

The preprocessing system uses a pipe-separated string format to define sequential operations. Each operation can have positional and keyword arguments, following Python function call syntax.

**Basic Format**: `operation1|operation2(arg1, kwarg=value)|operation3`

**Key Components**:

| Component | Description | Example |
|-----------|-------------|---------|
| Operation Name | Registry key for the preprocessing function | `resize`, `decode`, `normalize` |
| Positional Args | Arguments passed to the operation | `resize(224)` |
| Keyword Args | Named parameters | `crop(size=224, method="random")` |
| Pipeline Separator | Pipe character connecting operations | `decode|resize(224)|flip_lr` |

The `get_preprocess_fn` function in [jeo/pp/pp_builder.py:31-95]() parses this specification and returns a preprocessing function that can be applied to data dictionaries.

```mermaid
flowchart LR
    subgraph "String Parsing"
        InputString["\"decode|resize(224)|flip_lr\""]
        Split["Split by '|'<br/>['decode', 'resize(224)', 'flip_lr']"]
        ParseEach["parse_name() for each<br/>Extract name, args, kwargs"]
    end
    
    subgraph "Operation Resolution"
        RegistryLookup["Registry.lookup()<br/>Find operation function"]
        PartialApplication["functools.partial<br/>Apply arguments"]
        OpList["List of Operations<br/>[decode_fn, resize_fn, flip_fn]"]
    end
    
    subgraph "Pipeline Function"
        DataInput["Data Dictionary<br/>{\"image\": raw_tensor}"]
        Sequential["Sequential Application<br/>Apply ops in order"]
        DataOutput["Processed Dictionary<br/>{\"image\": processed_tensor}"]
    end
    
    InputString --> Split
    Split --> ParseEach
    ParseEach --> RegistryLookup
    RegistryLookup --> PartialApplication
    PartialApplication --> OpList
    
    DataInput --> Sequential
    OpList --> Sequential
    Sequential --> DataOutput
```

Sources: [jeo/pp/pp_builder.py:98-151](), [jeo/pp/pp_builder.py:31-95]()

## Registry System

The `Registry` class provides a global registry for preprocessing operations. Operations are registered with string keys and can be looked up and instantiated with parameters.

**Core Registry Operations**:

| Method | Purpose | Usage |
|--------|---------|-------|
| `Registry.register(name)` | Register a new operation | Decorator for operation functions |
| `Registry.lookup(lookup_string)` | Retrieve and configure operation | Used by pipeline builder |
| `Registry.knows(lookup_string)` | Check if operation exists | Validation and error handling |

The registry stores operations with the `preprocess_ops.` prefix, allowing for namespaced organization of different operation types.

```mermaid
graph TB
    subgraph "Registration Process"
        OpFunction["Operation Function<br/>def my_preprocess_op(...)"]
        Decorator["@Registry.register<br/>(\"preprocess_ops.my_op\")"]
        GlobalStore["Registry._GLOBAL_REGISTRY<br/>{\"preprocess_ops.my_op\": function}"]
    end
    
    subgraph "Lookup Process"
        LookupString["\"my_op(param=value)\""]
        ParseName["parse_name()<br/>Extract name, args, kwargs"]
        RetrieveFunction["Retrieve from registry<br/>registry[\"preprocess_ops.my_op\"]"]
        PartialFunc["functools.partial<br/>Apply parameters"]
    end
    
    subgraph "Temporary Operations"
        ContextManager["temporary_ops(**kw)<br/>Temporary registration"]
        WithBlock["with temporary_ops(...):<br/>Limited scope usage"]
        Cleanup["Automatic cleanup<br/>Remove from registry"]
    end
    
    OpFunction --> Decorator
    Decorator --> GlobalStore
    
    LookupString --> ParseName
    ParseName --> RetrieveFunction
    GlobalStore --> RetrieveFunction
    RetrieveFunction --> PartialFunc
    
    ContextManager --> WithBlock
    WithBlock --> Cleanup
    GlobalStore -.-> ContextManager
```

Sources: [jeo/pp/pp_builder.py:153-196](), [jeo/pp/pp_builder.py:198-229]()

## Utility Functions

The `pp_utils.py` module provides essential utilities for preprocessing operations, including key management, data type handling, and normalization parameter loading.

**Key Utilities**:

- **`InKeyOutKey` Decorator**: Manages input/output key specification for preprocessing operations [jeo/pp/pp_utils.py:87-126]()
- **`get_lookup_table`**: Creates TensorFlow lookup tables for label mapping [jeo/pp/pp_utils.py:32-51]()
- **`load_normalization_ranges`**: Loads normalization statistics from GeeFlow data [jeo/pp/pp_utils.py:54-84]()
- **`maybe_repeat`**: Utility for repeating arguments to match expected lengths [jeo/pp/pp_utils.py:26-29]()

The `InKeyOutKey` decorator is particularly important as it provides a standard pattern for operations that transform single inputs to single outputs while managing dictionary keys:

```python
@InKeyOutKey(indefault="image", outdefault="image")
def my_operation(input_tensor, **kwargs):
    return processed_tensor
```

Sources: [jeo/pp/pp_utils.py:87-126](), [jeo/pp/pp_utils.py:32-84]()

## Data Flow Architecture

The preprocessing system integrates with Jeo's broader training pipeline by transforming raw data dictionaries into model-ready formats. The system expects input data as dictionaries with at least an "image" key containing 3D tensors.

```mermaid
flowchart TD
    subgraph "Data Sources"
        RawData["Raw Data Dictionary<br/>{\"image\": raw_tensor, \"label\": id}"]
        StatsFiles["Normalization Stats<br/>GeeFlow statistics files"]
    end
    
    subgraph "Preprocessing Pipeline"
        ConfigLoad["Load Pipeline Config<br/>pp_pipeline string"]
        BuildPipeline["get_preprocess_fn()<br/>Build preprocessing function"]
        ApplyOps["Sequential Operations<br/>Apply each operation"]
    end
    
    subgraph "Operation Types"
        Decode["Decode Operations<br/>Image format conversion"]
        Transform["Transform Operations<br/>Resize, crop, flip"]
        Normalize["Normalization<br/>Statistics-based scaling"]
        Augment["Augmentation<br/>Data variation"]
    end
    
    subgraph "Output"
        ProcessedData["Processed Data<br/>{\"image\": processed_tensor, ...}"]
        ModelReady["Model-Ready Batches<br/>Training pipeline input"]
    end
    
    RawData --> BuildPipeline
    ConfigLoad --> BuildPipeline
    StatsFiles -.-> Normalize
    
    BuildPipeline --> ApplyOps
    ApplyOps --> Decode
    ApplyOps --> Transform
    ApplyOps --> Normalize
    ApplyOps --> Augment
    
    Decode --> ProcessedData
    Transform --> ProcessedData
    Normalize --> ProcessedData
    Augment --> ProcessedData
    
    ProcessedData --> ModelReady
```

Sources: [jeo/pp/pp_builder.py:72-94](), [jeo/pp/pp_utils.py:54-84]()

## Integration Points

The data processing system integrates with several other components in the Jeo framework:

**Training Integration**: The preprocessing functions generated by `get_preprocess_fn` are used within the input pipeline system to transform data before feeding it to models.

**Configuration System**: Pipeline specifications are typically defined in configuration files and passed to the preprocessing system through the training script.

**Statistics Loading**: The `load_normalization_ranges` function integrates with GeeFlow's statistics system to provide data-driven normalization parameters.

**Logging and Debugging**: The system provides optional logging of data before and after preprocessing, as well as step-by-step operation logging for debugging pipeline behavior.

Sources: [jeo/pp/pp_builder.py:31-95](), [jeo/pp/pp_utils.py:54-84]()

---

