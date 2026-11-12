<!-- source: DeepWiki mcp.deepwiki.com · repo WecoAI/aideml · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [aide/__init__.py](aide/__init__.py)
- [aide/agent.py](aide/agent.py)
- [aide/example_tasks/bitcoin_price/BTC-USD.csv](aide/example_tasks/bitcoin_price/BTC-USD.csv)
- [aide/example_tasks/house_prices/data_description.txt](aide/example_tasks/house_prices/data_description.txt)
- [aide/run.py](aide/run.py)

</details>



## Purpose and Scope

This document provides a high-level architectural overview of AIDE ML, focusing on the core components, their relationships, and how they map to code entities in the codebase. The architecture centers around five primary subsystems: the `Experiment` orchestrator, the `Agent` code generator, the `Interpreter` execution sandbox, the `Journal` solution tracker, and the Backend LLM abstraction layer.

For details on the iterative execution algorithm and tree search mechanics, see [Experiment Execution Flow](#2.1). For configuration system specifics, see [Configuration System](#2.2). For deeper dives into individual subsystems, see [Core Subsystems](#5) and its children.

---

## Core Components Overview

AIDE ML's architecture is organized into five core components that work together to implement agentic tree search over code solutions:

| Component | Primary Class/Module | Location | Responsibility |
|-----------|---------------------|----------|----------------|
| **Experiment** | `Experiment` class | [aide/__init__.py:23-62]() | Top-level orchestrator; initializes components, coordinates execution, returns best solution |
| **Agent** | `Agent` class | [aide/agent.py:47-60]() | Generates code drafts using LLMs, manages search strategy, creates solution tree nodes |
| **Interpreter** | `Interpreter` class | [aide/interpreter.py]() | Executes Python code in isolated sandbox, enforces timeouts, captures stdout/stderr/exceptions |
| **Journal** | `Journal` and `Node` classes | [aide/journal.py]() | Maintains solution tree structure, tracks metrics and bugs, selects best nodes |
| **Backend** | `backend.query` function | [aide/backend/__init__.py]() | Abstracts multiple LLM providers (OpenAI, Anthropic, Gemini, OpenRouter) behind unified interface |

Additionally, a **Configuration System** (see [Configuration System](#2.2)) manages experiment parameters using OmegaConf, and **Utilities** provide metrics, visualization, and reporting.

Sources: [aide/__init__.py:23-63](), [aide/run.py:1-150](), [aide/agent.py:47-60]()

---

## Component Relationships

The following diagram maps AIDE's architectural components to their concrete implementations in code:

```mermaid
graph TB
    subgraph UserLayer["User Entry Points"]
        CLI["CLI: aide command<br/>(aide/run.py:run)"]
        PyAPI["Python API: Experiment class<br/>(aide/__init__.py:Experiment)"]
        WebUI["Web UI: WebUI class<br/>(aide/webui/app.py)"]
    end
    
    subgraph Orchestration["Orchestration Layer"]
        RunFunc["run() function<br/>(aide/run.py:56-146)"]
        ExpClass["Experiment class<br/>(aide/__init__.py:23-62)"]
        ConfigSys["Configuration System<br/>(aide/utils/config.py)"]
    end
    
    subgraph CoreExecution["Core Execution Components"]
        AgentClass["Agent class<br/>(aide/agent.py)"]
        InterpreterClass["Interpreter class<br/>(aide/interpreter.py)"]
        JournalClass["Journal class<br/>(aide/journal.py)"]
        NodeClass["Node class<br/>(aide/journal.py)"]
    end
    
    subgraph LLMLayer["LLM Abstraction Layer"]
        BackendQuery["backend.query()<br/>(aide/backend/__init__.py)"]
        ProviderRouter["Provider Router<br/>(determine_provider logic)"]
        OpenAIBE["backend_openai.py"]
        AnthropicBE["backend_anthropic.py"]
        GeminiBE["backend_gemini.py"]
        OpenRouterBE["backend_openrouter.py"]
    end
    
    subgraph Support["Support Utilities"]
        MetricValue["MetricValue class<br/>(aide/utils/metric.py)"]
        TreeViz["tree_plot.html generator<br/>(aide/utils/tree_viz.py)"]
        Reporter["journal2report()<br/>(aide/journal2report.py)"]
    end
    
    CLI --> RunFunc
    PyAPI --> ExpClass
    WebUI --> ExpClass
    
    RunFunc --> ConfigSys
    RunFunc --> AgentClass
    RunFunc --> InterpreterClass
    RunFunc --> JournalClass
    
    ExpClass --> ConfigSys
    ExpClass --> AgentClass
    ExpClass --> InterpreterClass
    ExpClass --> JournalClass
    
    AgentClass --> BackendQuery
    AgentClass --> JournalClass
    AgentClass --> InterpreterClass
    
    JournalClass --> NodeClass
    JournalClass --> MetricValue
    
    BackendQuery --> ProviderRouter
    ProviderRouter --> OpenAIBE
    ProviderRouter --> AnthropicBE
    ProviderRouter --> GeminiBE
    ProviderRouter --> OpenRouterBE
    
    JournalClass --> TreeViz
    JournalClass --> Reporter
    
    ConfigSys -.configures.-> AgentClass
    ConfigSys -.configures.-> InterpreterClass
```

**Key Relationships:**

- **User Layer** provides three entry points that converge on either `run()` or `Experiment`.
- **Orchestration Layer** initializes components using configuration and coordinates their execution via `agent.step()` [aide/run.py:132]().
- **Agent** drives the search by generating code via `Backend`, tracking results in `Journal`, and executing via `Interpreter`.
- **Journal** maintains the tree structure using `Node` objects and `MetricValue` for comparisons [aide/journal.py]().
- **Backend** abstracts LLM differences through provider-specific implementations.

Sources: [aide/__init__.py:23-62](), [aide/run.py:56-146](), [aide/agent.py:47-60](), [aide/backend/__init__.py]()

---

## Module Structure

AIDE ML's package is organized into focused modules with clear responsibilities:

```mermaid
graph TB
    subgraph Package["aideml package"]
        InitPy["aide/__init__.py<br/>Experiment, Solution"]
        RunPy["aide/run.py<br/>run() orchestrator"]
        
        subgraph AgentMod["aide/agent.py"]
            AgentClass["Agent class"]
        end
        
        subgraph BackendMod["aide/backend/"]
            BackendInit["__init__.py<br/>query(), compile_prompt_to_md()"]
            BackendOpenAI["backend_openai.py"]
            BackendAnthropic["backend_anthropic.py"]
            BackendGemini["backend_gemini.py"]
            BackendOpenRouter["backend_openrouter.py"]
            BackendUtils["function_spec.py<br/>backoff_create.py"]
        end
        
        subgraph InterpreterMod["aide/interpreter.py"]
            InterpClass["Interpreter class"]
        end
        
        subgraph JournalMod["aide/journal.py"]
            JournalClass["Journal, Node classes"]
        end
        
        subgraph UtilsMod["aide/utils/"]
            ConfigPy["config.py<br/>load_cfg, prep_cfg"]
            MetricPy["metric.py<br/>MetricValue class"]
            TreeViz["tree_viz.py<br/>HTML generation"]
        end
        
        subgraph WebUIMod["aide/webui/"]
            AppPy["app.py<br/>Streamlit WebUI"]
        end
        
        J2R["aide/journal2report.py<br/>Report generation"]
    end
    
    InitPy --> AgentMod
    InitPy --> InterpreterMod
    InitPy --> JournalMod
    InitPy --> UtilsMod
    
    RunPy --> AgentMod
    RunPy --> InterpreterMod
    RunPy --> JournalMod
    RunPy --> BackendMod
    RunPy --> UtilsMod
    
    AgentMod --> BackendMod
    AgentMod --> JournalMod
    
    JournalMod --> J2R
```

**Module Responsibilities:**

- **aide/__init__.py**: Public API surface, exposes `Experiment` class and `Solution` dataclass [aide/__init__.py:18-63]().
- **aide/run.py**: CLI entry point, orchestrates full experiment with `Rich` UI [aide/run.py:56-146]().
- **aide/agent.py**: Code generation, tree search strategy (`search_policy`), and prompt construction [aide/agent.py:61-92]().
- **aide/backend/**: Multi-provider LLM abstraction with unified query interface.
- **aide/interpreter.py**: Sandboxed Python execution with timeout enforcement.
- **aide/journal.py**: Solution tree data structure and metric tracking.
- **aide/utils/**: Configuration loading, metrics, and helper functions.
- **aide/journal2report.py**: LLM-powered report generation from experiment history [aide/journal2report.py]().

Sources: [aide/__init__.py](), [aide/run.py](), [aide/agent.py](), [aide/backend/__init__.py]()

---

## Key Abstractions and Their Roles

### Experiment Class

The `Experiment` class ([aide/__init__.py:23-62]()) serves as the primary public API for programmatic use. It:

- Accepts task specification (`data_dir`, `goal`, `eval`).
- Initializes workspace, configuration, and core components.
- Exposes a `run(steps)` method that executes the tree search loop [aide/__init__.py:55-63]().
- Returns a `Solution` dataclass containing best code and metric.

### Agent Class

The `Agent` class ([aide/agent.py:47-60]()) implements the code generation and search logic. It:

- Generates multiple code drafts per iteration using LLM via `plan_and_code_query` [aide/agent.py:153-171]().
- Implements a `search_policy` to decide between drafting new nodes, debugging buggy nodes, or improving the greedy best node [aide/agent.py:61-92]().
- Manages search hyperparameters (`num_drafts`, `debug_prob`, `max_debug_depth`).

### Interpreter Class

The `Interpreter` class ([aide/interpreter.py]()) provides isolated code execution. It:

- Runs Python code in subprocess with timeout enforcement.
- Captures stdout, stderr, and exceptions.
- Returns `ExecutionResult` including metrics and terminal output.
- Provides `cleanup_session()` for resource management [aide/run.py:136]().

### Journal and Node Classes

The `Journal` class ([aide/journal.py]()) maintains the solution tree structure:

- Stores tree as collection of `Node` objects.
- Each `Node` tracks code, metric, bugs, and parent/children relationships.
- Provides `get_best_node()` to retrieve highest-scoring valid solution [aide/run.py:33]().

### Backend Query Function

The `backend.query()` function ([aide/backend/__init__.py]()) abstracts LLM access:

- Accepts model name, messages, optional function specifications.
- Routes to appropriate provider based on model name patterns.
- Returns unified response format across providers.

Sources: [aide/__init__.py:23-62](), [aide/agent.py:47-171](), [aide/run.py:32-53](), [aide/backend/__init__.py]()

---

## Data Flow Architecture

The following diagram shows how data flows through AIDE from inputs to outputs:

```mermaid
graph LR
    subgraph Inputs["Inputs"]
        DataDir["data_dir<br/>(CSV, JSON, TXT files)"]
        TaskSpec["goal + eval<br/>(plain text descriptions)"]
        Config["config.yaml<br/>(hyperparameters)"]
    end
    
    subgraph Preprocessing["Preprocessing"]
        LoadCfg["load_cfg()"]
        LoadTask["load_task_desc()"]
        PrepWS["prep_agent_workspace()"]
    end
    
    subgraph Execution["Execution Loop"]
        GenCode["Agent.step()<br/>generates code drafts"]
        ExecCode["Interpreter.run()<br/>executes in sandbox"]
        ComputeMetric["Compute MetricValue<br/>from output"]
        RecordJournal["Journal.add_node()<br/>updates tree"]
    end
    
    subgraph Persistence["Persistence"]
        LogDir["logs/exp-name/"]
        BestSol["best_solution.py"]
        TreeHTML["tree_plot.html"]
        JournalJSON["journal.json"]
        Report["report.md"]
    end
    
    DataDir --> PrepWS
    TaskSpec --> LoadTask
    Config --> LoadCfg
    
    LoadCfg --> GenCode
    LoadTask --> GenCode
    PrepWS --> ExecCode
    
    GenCode --> ExecCode
    ExecCode --> ComputeMetric
    ComputeMetric --> RecordJournal
    
    RecordJournal -.iterates.-> GenCode
    
    RecordJournal --> LogDir
    LogDir --> BestSol
    LogDir --> TreeHTML
    LogDir --> JournalJSON
    LogDir --> Report
```

**Data Flow Sequence:**

1. **Input Processing**: Task specification and configuration are loaded; workspace is prepared with data files [aide/run.py:60-64]().
2. **Execution Loop**: Agent generates code → Interpreter executes → Metrics computed → Journal records results [aide/run.py:131-135]().
3. **Persistence**: At each step and completion, state is saved to log directory with multiple output formats [aide/run.py:133]().

Sources: [aide/run.py:56-146](), [aide/utils/config.py](), [aide/__init__.py:55-62]()

---

## Layered Architecture

AIDE ML follows a layered architecture with clear separation of concerns:

### Layer 1: User Interface (Entry Points)

- **CLI** ([aide/run.py:56-146]()): `aide` command using Rich console UI.
- **Python API** ([aide/__init__.py:23-62]()): `Experiment` class for programmatic control.
- **Web UI** ([aide/webui/app.py]()): Streamlit-based browser interface.

### Layer 2: Orchestration

The orchestration layer coordinates execution via the `run()` function or `Experiment` class, managing the lifecycle of the agentic search.

### Layer 3: Core Execution

Core components implement the agentic tree search:
- **Agent**: Generates code variations using `search_policy` [aide/agent.py:61-92]().
- **Interpreter**: Executes code in isolation.
- **Journal**: Maintains solution tree and tracks progress.

### Layer 4: LLM Abstraction

The backend layer decouples AIDE from specific LLM providers, providing a unified `query()` interface [aide/backend/__init__.py]().

---

## Execution Context and Isolation

AIDE implements multiple levels of isolation to ensure safe and reproducible experiments:

| Isolation Level | Mechanism | Purpose |
|----------------|-----------|---------|
| **Workspace Directory** | `prep_agent_workspace()` | Isolates data files and generated code [aide/run.py:64]() |
| **Process Isolation** | Subprocess in `Interpreter` | Protects main process from crashes/hangs |
| **Timeout Enforcement** | `cfg.exec.timeout` | Prevents infinite loops or long-running code [aide/agent.py:124]() |
| **Log Directory** | `cfg.log_dir` | Separates results from multiple runs [aide/run.py:106]() |

Sources: [aide/run.py:60-106](), [aide/agent.py:118-128](), [aide/interpreter.py]()

---

## Component Initialization Sequence

The initialization sequence is nearly identical between CLI and Python API modes:

1. **Load Config**: `load_cfg()` or `_load_cfg()` [aide/run.py:57]().
2. **Load Task**: `load_task_desc(cfg)` [aide/run.py:60]().
3. **Prepare Workspace**: `prep_agent_workspace(cfg)` [aide/run.py:64]().
4. **Create Journal**: `Journal()` [aide/run.py:72]().
5. **Create Agent**: `Agent(task_desc, cfg, journal)` [aide/run.py:73]().
6. **Create Interpreter**: `Interpreter(cfg.workspace_dir, ...)` [aide/run.py:78]().
7. **Execute Loop**: `agent.step(exec_callback=...)` [aide/run.py:132]().
8. **Save Results**: `save_run(cfg, journal)` [aide/run.py:133]().

Sources: [aide/run.py:56-146](), [aide/__init__.py:23-62]()

---

