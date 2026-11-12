<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/recoma · page 7 Advanced Features · fetched 2026-10-26 -->

# Advanced Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [configs/inference/drop/decomp.jsonnet](configs/inference/drop/decomp.jsonnet)
- [recoma/search/early_stopping.py](recoma/search/early_stopping.py)
- [recoma/utils/state_renderer.py](recoma/utils/state_renderer.py)

</details>



This document covers advanced functionality for monitoring, debugging, and extending ReComA beyond basic inference operations. These features enable developers to visualize search processes, control resource usage, and extend the framework with custom components.

For basic usage patterns, see [Quick Start Guide](#1.2). For core system architecture, see [Core Architecture](#2).

## State Visualization and Debugging

ReComA provides comprehensive visualization tools for debugging search processes and understanding model interactions through the `StateRenderer` system.

### StateRenderer Architecture

The state rendering system uses a registry pattern to support multiple output formats for search state visualization:

```mermaid
graph TB
    subgraph "StateRenderer System"
        BASE["StateRenderer"]
        REGISTRY["RegistrableFromDict"]
        
        BLOCK["BlockRenderer"]
        TREE["TreeRenderer"]
        OLD["OldStateRenderer"]
        FULL["FullJsonRenderer"]
        SIMPLE["SimpleJsonRenderer"]
    end
    
    subgraph "Output Formats"
        HTML["HTML Output"]
        JSON["JSON Output"]
    end
    
    subgraph "Search State Data"
        STATE["SearchState"]
        NODE["SearchNode"]
        TREE_DATA["Tree Structure"]
    end
    
    BASE --> REGISTRY
    BASE --> BLOCK
    BASE --> TREE
    BASE --> OLD
    BASE --> FULL
    BASE --> SIMPLE
    
    BLOCK --> HTML
    TREE --> HTML
    OLD --> HTML
    FULL --> JSON
    SIMPLE --> JSON
    
    STATE --> NODE
    STATE --> TREE_DATA
    
    BLOCK --> STATE
    TREE --> STATE
    OLD --> STATE
    FULL --> STATE
    SIMPLE --> STATE
```

**Sources:** [recoma/utils/state_renderer.py:1-419]()

### HTML Visualization Renderers

ReComA includes several HTML renderers for different visualization needs:

| Renderer | Registration Key | Purpose | Features |
|----------|------------------|---------|----------|
| `BlockRenderer` | `"block"` | Modern collapsible interface | Inter font, clean styling, expandable details |
| `TreeRenderer` | `"tree"` | Tree-like hierarchical view | CSS tree lines, nested structure |
| `OldStateRenderer` | `"old"` | Legacy styling | Simple details/summary format |

The `BlockRenderer` provides the most polished visualization with modern CSS styling:

```mermaid
graph LR
    subgraph "BlockRenderer Features"
        STYLE["Inter Font Styling"]
        COLLAPSIBLE["Collapsible Details"]
        PROMPTS["Prompt History"]
        CLEAN["Clean HTML Output"]
    end
    
    subgraph "Node Components"
        TAG["Node Tag"]
        INPUT["Input Display"]
        OUTPUT["Output Display"]
        TARGET["Target Model"]
    end
    
    STYLE --> CLEAN
    COLLAPSIBLE --> CLEAN
    PROMPTS --> CLEAN
    
    TAG --> NODE_HTML["HTML Node Representation"]
    INPUT --> NODE_HTML
    OUTPUT --> NODE_HTML
    TARGET --> NODE_HTML
    
    NODE_HTML --> CLEAN
```

**Sources:** [recoma/utils/state_renderer.py:31-207]()

### JSON Export Renderers

For programmatic access to search state data, ReComA provides JSON renderers:

- **`FullJsonRenderer`**: Exports complete search state with all metadata via `SearchState.to_json()`
- **`SimpleJsonRenderer`**: Exports only leaf nodes with essential fields (input, output, model)

The `SimpleJsonRenderer` creates a simplified view focusing on final outputs:

```mermaid
graph TD
    subgraph "SimpleJsonRenderer Process"
        TRAVERSE["Postorder Traversal"]
        FILTER["Filter Leaf Nodes"]
        EXTRACT["Extract Key Fields"]
        FORMAT["JSON Format"]
    end
    
    subgraph "Output Fields"
        INPUT_FIELD["input: node.input_str"]
        OUTPUT_FIELD["output: node.output"]
        MODEL_FIELD["model: node.target"]
    end
    
    TRAVERSE --> FILTER
    FILTER --> EXTRACT
    EXTRACT --> FORMAT
    
    EXTRACT --> INPUT_FIELD
    EXTRACT --> OUTPUT_FIELD
    EXTRACT --> MODEL_FIELD
```

**Sources:** [recoma/utils/state_renderer.py:401-419]()

## Search Control and Early Stopping

ReComA provides multiple mechanisms to control search execution and prevent excessive resource consumption through the `EarlyStoppingCondition` system.

### Early Stopping Architecture

The early stopping system uses a registry pattern with pluggable conditions:

```mermaid
graph TB
    subgraph "EarlyStoppingCondition System"
        BASE["EarlyStoppingCondition"]
        ABSTRACT["should_stop() method"]
        
        DEPTH["MaxSearchDepth"]
        ITERS["MaxSearchIterations"]
        CALLS["MaximumLLMCalls"]
        COST["MaximumLLMCost"]
    end
    
    subgraph "Monitoring Data"
        STATE_DATA["SearchState.data"]
        COUNTERS["Counter objects"]
        REGEX_MATCH["Regex pattern matching"]
    end
    
    subgraph "Stop Conditions"
        DEPTH_LIMIT["Depth > max_search_depth"]
        ITER_LIMIT["Iterations >= max_search_iters"]
        CALL_LIMIT["LLM calls >= max_llm_calls"]
        COST_LIMIT["Total cost >= max_llm_cost"]
    end
    
    BASE --> ABSTRACT
    BASE --> DEPTH
    BASE --> ITERS
    BASE --> CALLS
    BASE --> COST
    
    DEPTH --> DEPTH_LIMIT
    ITERS --> ITER_LIMIT
    CALLS --> CALL_LIMIT
    COST --> COST_LIMIT
    
    CALLS --> STATE_DATA
    COST --> STATE_DATA
    STATE_DATA --> COUNTERS
    STATE_DATA --> REGEX_MATCH
```

**Sources:** [recoma/search/early_stopping.py:1-87]()

### Resource Monitoring

The LLM call and cost monitoring systems track usage through regex pattern matching on `SearchState.data` keys:

| Pattern | Purpose | Example Keys |
|---------|---------|--------------|
| `openai.(.*).calls` | Track OpenAI API calls | `openai.gpt-3.5-turbo.calls` |
| `litellm.(.*).calls` | Track LiteLLM API calls | `litellm.gemini-pro.calls` |
| `openai.(.*).cost` | Track OpenAI costs | `openai.gpt-4.cost` |
| `litellm.(.*).cost` | Track LiteLLM costs | `litellm.claude-3.cost` |

The monitoring system aggregates these values across all models:

```mermaid
graph LR
    subgraph "Cost Monitoring Flow"
        SEARCH_DATA["SearchState.data"]
        REGEX_EXTRACT["Regex Pattern Matching"]
        COUNTER["Counter Aggregation"]
        THRESHOLD["Threshold Checking"]
    end
    
    subgraph "Data Sources"
        OPENAI_CALLS["openai.*.calls"]
        LITELLM_CALLS["litellm.*.calls"]
        OPENAI_COST["openai.*.cost"]
        LITELLM_COST["litellm.*.cost"]
    end
    
    SEARCH_DATA --> REGEX_EXTRACT
    REGEX_EXTRACT --> COUNTER
    COUNTER --> THRESHOLD
    
    OPENAI_CALLS --> SEARCH_DATA
    LITELLM_CALLS --> SEARCH_DATA
    OPENAI_COST --> SEARCH_DATA
    LITELLM_COST --> SEARCH_DATA
```

**Sources:** [recoma/search/early_stopping.py:46-87]()

## Extending the Framework

ReComA uses a consistent registry pattern throughout the codebase that enables easy extension with custom components.

### Registration System

All extensible components inherit from `RegistrableFromDict` and use the `@register` decorator:

```mermaid
graph TB
    subgraph "Registry Pattern"
        REGISTRABLE["RegistrableFromDict"]
        DECORATOR["@register decorator"]
        REGISTRY["Class registry"]
    end
    
    subgraph "Extensible Components"
        MODELS["BaseModel"]
        SEARCH["SearchAlgo"]
        RENDERERS["StateRenderer"]
        EARLY_STOP["EarlyStoppingCondition"]
        READERS["DatasetReader"]
        GENERATORS["LMGenerator"]
    end
    
    subgraph "Configuration Loading"
        JSONNET["JSONNET configs"]
        TYPE_FIELD["type field"]
        INSTANTIATION["Dynamic instantiation"]
    end
    
    REGISTRABLE --> DECORATOR
    DECORATOR --> REGISTRY
    
    REGISTRABLE --> MODELS
    REGISTRABLE --> SEARCH
    REGISTRABLE --> RENDERERS
    REGISTRABLE --> EARLY_STOP
    REGISTRABLE --> READERS
    REGISTRABLE --> GENERATORS
    
    JSONNET --> TYPE_FIELD
    TYPE_FIELD --> REGISTRY
    REGISTRY --> INSTANTIATION
```

### Adding Custom Components

To extend ReComA with custom components:

1. **Inherit from appropriate base class**: Use `BaseModel`, `StateRenderer`, `EarlyStoppingCondition`, etc.
2. **Register with decorator**: Use `@YourBaseClass.register("your_key")`
3. **Implement required methods**: Follow the abstract method signatures
4. **Configure in JSONNET**: Reference by registration key in configuration files

Example registration pattern from the codebase:

```mermaid
graph LR
    subgraph "Custom StateRenderer Example"
        INHERIT["class CustomRenderer(StateRenderer)"]
        REGISTER["@StateRenderer.register('custom')"]
        IMPLEMENT["def to_html(self, search_state)"]
        CONFIG["'renderer': {'type': 'custom'}"]
    end
    
    subgraph "Framework Integration"
        REGISTRY_LOOKUP["Registry lookup by 'custom' key"]
        INSTANTIATION["Dynamic instantiation"]
        USAGE["Used in search pipeline"]
    end
    
    INHERIT --> REGISTER
    REGISTER --> IMPLEMENT
    IMPLEMENT --> CONFIG
    
    CONFIG --> REGISTRY_LOOKUP
    REGISTRY_LOOKUP --> INSTANTIATION
    INSTANTIATION --> USAGE
```

**Sources:** [recoma/utils/state_renderer.py:8-419](), [recoma/search/early_stopping.py:12-87]()

### Configuration Integration

The framework automatically discovers and instantiates registered components based on JSONNET configuration files. The `type` field in configuration objects corresponds to registration keys, enabling declarative component composition.

**Sources:** [configs/inference/drop/decomp.jsonnet:1-39]()

---

