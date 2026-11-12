<!-- source: DeepWiki mcp.deepwiki.com · repo trycua/cua · page 9 Extension Points · fetched 2026-10-29 -->

# Extension Points

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [libs/python/agent/.bumpversion.cfg](libs/python/agent/.bumpversion.cfg)
- [libs/python/agent/README.md](libs/python/agent/README.md)
- [libs/python/agent/pyproject.toml](libs/python/agent/pyproject.toml)
- [libs/python/core/.bumpversion.cfg](libs/python/core/.bumpversion.cfg)
- [libs/python/core/README.md](libs/python/core/README.md)
- [libs/python/core/pyproject.toml](libs/python/core/pyproject.toml)
- [libs/python/som/.bumpversion.cfg](libs/python/som/.bumpversion.cfg)
- [libs/python/som/README.md](libs/python/som/README.md)
- [libs/python/som/pyproject.toml](libs/python/som/pyproject.toml)

</details>



This page introduces the four primary mechanisms for extending and customizing the behavior of `ComputerAgent` in Cua. These extension points allow you to add custom logic, integrate domain-specific tools, modify agent behavior, and control execution environments without modifying core agent code.

For basic agent usage, see [Quick Start: Python SDK](#2.3). For ComputerAgent initialization parameters, see [ComputerAgent SDK](#3.3).

## Extension Point Overview

| Extension Point | Code Entry Point | Complexity | Use Cases |
|----------------|------------------|------------|-----------|
| **Callback System** | `callbacks` parameter in `ComputerAgent.__init__` | Simple to Intermediate | Logging, trajectory recording, budget management, message preprocessing |
| **Custom Tools** | `tools` parameter in `ComputerAgent.__init__` | Easy | Adding function tools, custom computer tools, domain-specific APIs |
| **Custom Agent Loops** | `custom_loop` parameter or `@register_agent` decorator | Advanced | Implementing new model integrations, custom reasoning patterns |
| **Sandboxed Execution** | Docker images, Lume VMs, custom environments | Intermediate | Custom software installations, security isolation, specific OS requirements |

Sources: [libs/python/agent/pyproject.toml:6-10](), [libs/python/agent/cua_agent/agent.py:168-229](), [libs/python/agent/cua_agent/decorators.py:13-48]()

## Extension Point Architecture

The following diagram shows how extension points integrate with `ComputerAgent`:

### Agent Extension Architecture
```mermaid
graph TB
    subgraph "UserCode"
        [UserScript]
    end
    
    subgraph "ComputerAgent_Initialization"
        [AgentInit] -- "ComputerAgent.__init__"
        [ModelParam] -- "model: str"
        [ToolsParam] -- "tools: List[Any]"
        [CallbacksParam] -- "callbacks: List[AsyncCallbackHandler]"
        [CustomLoopParam] -- "custom_loop: Optional[Callable]"
    end
    
    subgraph "Extension_Points"
        [Callbacks] -- "Callback System (9.1)"
        [Tools] -- "Custom Tools (9.3)"
        [Loops] -- "Custom Agent Loops (9.2)"
        [Environment] -- "Sandboxed Execution (9.4)"
    end
    
    subgraph "Core_Agent_Components"
        [AgentRun] -- "agent.run()"
        [PredictStep] -- "agent_loop.predict_step()"
        [HandleItem] -- "_handle_item()"
    end
    
    [UserScript] --> [AgentInit]
    [AgentInit] --> [ModelParam]
    [AgentInit] --> [ToolsParam]
    [AgentInit] --> [CallbacksParam]
    [AgentInit] --> [CustomLoopParam]
    
    [CallbacksParam] --> [Callbacks]
    [ToolsParam] --> [Tools]
    [CustomLoopParam] --> [Loops]
    [ToolsParam] --> [Environment]
    
    [AgentInit] --> [AgentRun]
    [AgentRun] --> [PredictStep]
    [AgentRun] --> [HandleItem]
    
    [Callbacks] -. "lifecycle hooks" .-> [AgentRun]
    [Tools] -. "tool execution" .-> [HandleItem]
    [Loops] -. "model calls" .-> [PredictStep]
```

Sources: [libs/python/agent/cua_agent/agent.py:162-302]()

## Choosing an Extension Point

The following decision tree helps determine which extension point to use:

### Extension Selection Logic
```mermaid
graph TD
    [Start] -- "Need to extend agent behavior?" --> [Q1]
    
    [Q1] -- "Need to add new capabilities?" --> [Q2]
    [Q1] -- "No" --> [Q3]
    
    [Q2] -- "Yes (External APIs/Deterministic)" --> [ToolsEP]
    [Q2] -- "No" --> [Q4]
    
    [Q3] -- "Yes (Intercept messages/Track usage)" --> [CallbacksEP]
    [Q3] -- "No" --> [Q6]
    
    [Q4] -- "Yes (Custom OS/Software)" --> [SandboxEP]
    [Q4] -- "No" --> [ToolsEP]
    
    [Q6] -- "Yes (Custom model provider/reasoning)" --> [LoopsEP]
    [Q6] -- "No" --> [CallbacksEP]

    [ToolsEP] -- "Use Custom Tools (9.3)"
    [SandboxEP] -- "Use Sandboxed Execution (9.4)"
    [CallbacksEP] -- "Use Callback System (9.1)"
    [LoopsEP] -- "Use Custom Agent Loops (9.2)"
```

Sources: [libs/python/agent/cua_agent/agent.py:168-342]()

## Extension Point Details

### 1. Callback System
The callback system uses the `AsyncCallbackHandler` base class to hook into agent lifecycle events. It is used for monitoring, budget enforcement, and normalizing model outputs. Cua provides several built-in handlers like `TrajectorySaverCallback` for recording screenshots and actions [libs/python/agent/cua_agent/agent.py:257-268]().
For details, see [Callback System](#9.1).

### 2. Custom Agent Loops
Custom loops allow you to implement specific logic for different model providers (e.g., Anthropic, OpenAI, Qwen). These are registered via the `@register_agent` decorator [libs/python/agent/cua_agent/decorators.py:13-48]() and implement the `AsyncAgentConfig` protocol. The registration system allows matching model strings to specific loop implementations [libs/python/agent/cua_agent/decorators.py:56-61]().
For details, see [Custom Agent Loops](#9.2).

### 3. Custom Tools
Custom tools can be standard Python functions or complex classes. Cua automatically generates JSON schemas for these tools using `_process_tools` [libs/python/agent/cua_agent/agent.py:323-342]() to be passed to LLMs. The `cua-mcp-server` also facilitates tool discovery for computer-use agents.
For details, see [Custom Tools](#9.3).

### 4. Sandboxed Execution
Cua supports various execution backends including Docker, QEMU, and Lume (macOS). This extension point allows for creating custom images with pre-installed software via the `Image.app_install()` pipeline which leverages the `cua-sandbox-apps` catalog.
For details, see [Sandboxed Execution](#9.4).

## Extension Point Composition

Multiple extension points can be combined for sophisticated customization:

### Production Configuration Diagram
```mermaid
graph TB
    subgraph "Production_Agent_Configuration"
        [CustomDocker] -- "Custom Docker Image (pre-installed tools)"
        [CustomTools] -- "Domain Tools (calculate_roi, query_db)"
        [CustomCallbacks] -- "Monitoring Stack (TrajectorySaver, BudgetManager)"
        [CustomLoop] -- "Custom Agent Loop (specialized grounding model)"
    end
    
    subgraph "ComputerAgent_Init"
        [Init] -- "ComputerAgent(...)"
    end
    
    [CustomDocker] --> [Init]
    [CustomTools] --> [Init]
    [CustomCallbacks] --> [Init]
    [CustomLoop] --> [Init]
    
    [Init] --> [Agent] -- "Fully Customized Agent"
```

Sources: [libs/python/agent/cua_agent/agent.py:168-229]()

### Built-in Callbacks

Cua includes several built-in callbacks for common use cases, managed during `ComputerAgent` initialization:

| Callback Class | Purpose | Auto-added | Configuration |
|---------------|---------|------------|---------------|
| `OperatorNormalizerCallback` | Fixes common model output errors | Always | `callbacks.insert(0, ...)` |
| `LoggingCallback` | Logs agent actions to console | When `verbosity` set | `verbosity=logging.INFO` |
| `TrajectorySaverCallback` | Records trajectory data | When `trajectory_dir` set | `trajectory_dir="./paths"` |
| `BudgetManagerCallback` | Enforces cost/token limits | When `max_trajectory_budget` set | `max_trajectory_budget=10.0` |
| `TelemetryCallback` | Tracks usage metrics | Always | `telemetry_enabled=True` (default) |

Sources: [libs/python/agent/cua_agent/agent.py:231-299](), [libs/python/core/pyproject.toml:26-30]()

## Code Entity Reference

### Core Extension Interfaces

| Interface | File Path | Key Methods/Attributes |
|-----------|-----------|------------------------|
| `AsyncCallbackHandler` | `libs/python/agent/cua_agent/callbacks/base.py` | `on_run_start`, `on_llm_start`, `on_llm_end`, `on_run_end` |
| `AsyncAgentConfig` | `libs/python/agent/cua_agent/loops/base.py` | `predict_step`, `predict_click`, `get_capabilities` |
| `Computer` | `libs/python/computer/computer/computer.py` | `interface`, `run`, `stop` |
| `ComputerAgent.__init__` | [libs/python/agent/cua_agent/agent.py:168-229]() | `tools`, `callbacks`, `custom_loop`, `instructions` |

### Registration and Discovery

| Function/Decorator | File Path | Purpose |
|-------------------|-----------|---------|
| `register_agent` | [libs/python/agent/cua_agent/decorators.py:13-48]() | Register custom agent loops with model pattern matching |
| `find_agent_config` | [libs/python/agent/cua_agent/decorators.py:56-61]() | Find matching agent loop for a model string |
| `_process_tools` | [libs/python/agent/cua_agent/agent.py:323-342]() | Convert tools to schemas and identify computer tools |

Sources: [libs/python/agent/cua_agent/agent.py](), [libs/python/agent/cua_agent/decorators.py]()

---

