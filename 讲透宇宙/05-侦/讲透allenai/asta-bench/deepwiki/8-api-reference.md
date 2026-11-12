<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/asta-bench · page 8 API Reference · fetched 2026-10-26 -->

# API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [astabench/__init__.py](astabench/__init__.py)

</details>



This section provides comprehensive API documentation for developers who want to extend asta-bench with custom tools, evaluation tasks, or integrate it into their own systems. It covers the main package APIs, extension points, and architectural components that form the foundation of the asta-bench framework.

For configuration options and file formats, see [Configuration Reference](#9). For task-specific implementation details, see [Evaluation Tasks](#5). For development environment setup, see [Development Environment](#6.1).

## Package Structure and Entry Points

The `astabench` package provides a minimal but extensible API surface built on top of the `inspect_ai` framework. The main package structure follows a modular design that separates evaluation tasks, tool configurations, and core framework components.

### Main Package API

```mermaid
graph TB
    subgraph "astabench Package Structure"
        INIT["astabench.__init__"]
        EVALS["astabench.evals"]
        VERSION["__version__"]
        
        INIT --> EVALS
        INIT --> VERSION
    end
    
    subgraph "Core Modules"
        TOOLSET["ToolsetConfig"]
        TASKS["Task Definitions"]
        SCORERS["Scoring Functions"]
        
        EVALS --> TOOLSET
        EVALS --> TASKS
        EVALS --> SCORERS
    end
    
    subgraph "External Dependencies"
        INSPECT["inspect_ai Framework"]
        HF["huggingface_hub"]
        REQUESTS["requests"]
        
        TOOLSET --> INSPECT
        TASKS --> INSPECT
        EVALS --> HF
        EVALS --> REQUESTS
    end
    
    subgraph "Task Categories"
        PF_TASKS["paper_finder.*"]
        SQA_TASKS["sqa.*"]
        SUPER_TASKS["super.*"]
        DB_TASKS["discoverybench.*"]
        
        TASKS --> PF_TASKS
        TASKS --> SQA_TASKS
        TASKS --> SUPER_TASKS
        TASKS --> DB_TASKS
    end
```

**Sources:** [astabench/__init__.py:1-6]()

The core package API is intentionally minimal, exposing only essential components through the main `__init__.py` module. The primary entry point imports the `evals` module and provides version information through the standard `__version__` attribute.

### CLI and Configuration Integration

```mermaid
graph LR
    subgraph "CLI Interface"
        CLI_MAIN["astabench CLI"]
        INSPECT_CLI["inspect_ai CLI"]
        
        CLI_MAIN --> INSPECT_CLI
    end
    
    subgraph "Configuration System"
        YAML_CONFIG["v1.0.0.yml"]
        TASK_CONFIG["Task Configs"]
        TOOL_CONFIG["ToolsetConfig"]
        
        CLI_MAIN --> YAML_CONFIG
        YAML_CONFIG --> TASK_CONFIG
        YAML_CONFIG --> TOOL_CONFIG
    end
    
    subgraph "Evaluation Pipeline"
        EVAL_RUNNER["inspect eval"]
        TASK_EXECUTOR["Task Execution"]
        SCORER["Score Computation"]
        
        INSPECT_CLI --> EVAL_RUNNER
        EVAL_RUNNER --> TASK_EXECUTOR
        TASK_EXECUTOR --> SCORER
    end
    
    subgraph "Output Processing"
        EVAL_LOGS[".eval Log Files"]
        SCORE_CMD["astabench score"]
        AGGREGATION["Score Aggregation"]
        
        SCORER --> EVAL_LOGS
        EVAL_LOGS --> SCORE_CMD
        SCORE_CMD --> AGGREGATION
    end
```

**Sources:** [astabench/__init__.py:1-6]()

## Core Framework Components

The asta-bench framework consists of several key components that work together to provide a comprehensive evaluation system for AI agents conducting scientific research tasks.

### Framework Architecture

```mermaid
graph TB
    subgraph "inspect_ai Foundation"
        INSPECT_CORE["inspect_ai.Task"]
        INSPECT_SOLVER["inspect_ai.Solver"] 
        INSPECT_SCORER["inspect_ai.Scorer"]
        INSPECT_TOOL["inspect_ai.Tool"]
    end
    
    subgraph "astabench Extensions"
        ASTABENCH_TASKS["astabench Task Implementations"]
        TOOLSET_CONFIG["ToolsetConfig.create_tools()"]
        CUSTOM_SCORERS["Domain-specific Scorers"]
        EXTERNAL_TOOLS["External API Tools"]
        
        ASTABENCH_TASKS --> INSPECT_CORE
        TOOLSET_CONFIG --> INSPECT_TOOL
        CUSTOM_SCORERS --> INSPECT_SCORER
        EXTERNAL_TOOLS --> INSPECT_TOOL
    end
    
    subgraph "Task Categories"
        PAPER_FINDING["PaperFindingBench"]
        SCHOLAR_QA["ScholarQA"]
        CODE_TASKS["SUPER/CORE/DS1000"]
        DISCOVERY["DiscoveryBench"]
        
        PAPER_FINDING --> ASTABENCH_TASKS
        SCHOLAR_QA --> ASTABENCH_TASKS
        CODE_TASKS --> ASTABENCH_TASKS
        DISCOVERY --> ASTABENCH_TASKS
    end
    
    subgraph "External Integrations"
        SEMANTIC_SCHOLAR["Semantic Scholar API"]
        AI2I_FINDER["AI2I Paper Finder"]
        HUGGINGFACE["Hugging Face Hub"]
        
        EXTERNAL_TOOLS --> SEMANTIC_SCHOLAR
        EXTERNAL_TOOLS --> AI2I_FINDER
        ASTABENCH_TASKS --> HUGGINGFACE
    end
```

**Sources:** [astabench/__init__.py:3]()

## Tool System Architecture

The tool system provides a flexible configuration mechanism for composing different capabilities that AI agents can access during evaluation tasks.

### ToolsetConfig API Pattern

```mermaid
graph TD
    subgraph "Tool Configuration"
        TOOLSET_CONFIG["ToolsetConfig"]
        BOOLEAN_FLAGS["Boolean Configuration Flags"]
        CREATE_TOOLS["create_tools() method"]
        
        BOOLEAN_FLAGS --> TOOLSET_CONFIG
        TOOLSET_CONFIG --> CREATE_TOOLS
    end
    
    subgraph "Tool Categories"
        SEARCH_TOOLS["search_*: bool"]
        PYTHON_TOOLS["python_session: bool"]
        EDITOR_TOOLS["editor: bool"]
        THINKING_TOOLS["thinking: bool"]
        S2_TOOLS["semantic_scholar: bool"]
        
        CREATE_TOOLS --> SEARCH_TOOLS
        CREATE_TOOLS --> PYTHON_TOOLS
        CREATE_TOOLS --> EDITOR_TOOLS
        CREATE_TOOLS --> THINKING_TOOLS
        CREATE_TOOLS --> S2_TOOLS
    end
    
    subgraph "Tool Implementations"
        SEARCH_IMPL["SearchTool instances"]
        PYTHON_IMPL["PythonSession instances"]
        EDITOR_IMPL["Editor instances"]
        S2_IMPL["SemanticScholarTool instances"]
        
        SEARCH_TOOLS --> SEARCH_IMPL
        PYTHON_TOOLS --> PYTHON_IMPL
        EDITOR_TOOLS --> EDITOR_IMPL
        S2_TOOLS --> S2_IMPL
    end
    
    subgraph "inspect_ai Integration"
        TOOL_LIST["List[Tool]"]
        TASK_INTEGRATION["Task.tools parameter"]
        
        SEARCH_IMPL --> TOOL_LIST
        PYTHON_IMPL --> TOOL_LIST
        EDITOR_IMPL --> TOOL_LIST
        S2_IMPL --> TOOL_LIST
        
        TOOL_LIST --> TASK_INTEGRATION
    end
```

**Sources:** [astabench/__init__.py:3]()

## Task Development Framework

The task development system extends `inspect_ai.Task` with domain-specific implementations for scientific research evaluation.

### Task Implementation Pattern

```mermaid
graph LR
    subgraph "Task Definition"
        TASK_FUNC["@task decorated function"]
        DATASET["Dataset loading"]
        PLAN["Plan definition"]
        SCORER["Scorer specification"]
        TOOLS["Tool configuration"]
        
        TASK_FUNC --> DATASET
        TASK_FUNC --> PLAN
        TASK_FUNC --> SCORER
        TASK_FUNC --> TOOLS
    end
    
    subgraph "Dataset Integration"
        HF_LOAD["load_dataset()"]
        SAMPLE_CONVERSION["Sample conversion"]
        SPLIT_HANDLING["train/validation/test"]
        
        DATASET --> HF_LOAD
        HF_LOAD --> SAMPLE_CONVERSION
        HF_LOAD --> SPLIT_HANDLING
    end
    
    subgraph "Evaluation Pipeline"
        SOLVER_EXECUTION["Solver execution"]
        TOOL_ACCESS["Tool utilization"]
        SCORING["Score computation"]
        LOGGING["Result logging"]
        
        PLAN --> SOLVER_EXECUTION
        TOOLS --> TOOL_ACCESS
        SCORER --> SCORING
        SCORING --> LOGGING
    end
```

**Sources:** [astabench/__init__.py:3]()

## Extension Points

The asta-bench framework provides several well-defined extension points for developers to add new capabilities:

| Extension Point | Purpose | API Reference |
|----------------|---------|---------------|
| Custom Tasks | Add new evaluation scenarios | See [Task Development APIs](#8.3) |
| Custom Tools | Integrate new external services | See [Tool Development APIs](#8.2) |
| Custom Scorers | Implement domain-specific metrics | See [Task Development APIs](#8.3) |
| Configuration | Add new tool or task options | See [Configuration Reference](#9) |

### API Documentation Sections

The following sub-sections provide detailed API documentation for each major component:

- **[Core APIs](#8.1)**: Main astabench package APIs and entry points including the `evals` module structure and version management
- **[Tool Development APIs](#8.2)**: APIs for creating custom tools and integrating with the `ToolsetConfig` system  
- **[Task Development APIs](#8.3)**: APIs and patterns for creating new evaluation tasks that extend the `inspect_ai.Task` framework

Each section includes code examples, parameter specifications, and integration patterns for extending the framework.

**Sources:** [astabench/__init__.py:1-6]()

---

