<!-- source: DeepWiki mcp.deepwiki.com · repo trycua/cua · page 10 Monitoring and Operations · fetched 2026-10-29 -->

# Monitoring and Operations

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



This section covers the operational aspects of running Computer-Use Agents: monitoring execution, recording trajectories, managing costs, and handling errors. The Cua framework provides a comprehensive callback system that enables preprocessing and postprocessing hooks throughout the agent lifecycle, allowing developers to observe, control, and record agent behavior without modifying core agent logic.

**Scope**: This page introduces the callback architecture and built-in monitoring capabilities. For detailed implementation of specific subsystems, see:
- [Telemetry System](#10.1) — Telemetry implementation: PostHog integration, privacy-focused design, and session/run ID hierarchy.
- [Trajectory Recording](#10.2) — `TrajectorySaverCallback` deep dive: directory structure, screenshot saving, and action logging.
- [Budget and Cost Management](#10.3) — `BudgetManagerCallback`: token limits, cost limits, and usage tracking.
- [Logging and Error Handling](#10.4) — Logging system: `LoggingCallback`, verbosity levels, and error recovery patterns.

For extending the callback system with custom behavior, see [9.1 Callback System]().

---

## Callback System Architecture

The monitoring and operations infrastructure is built on a callback system that provides hooks into key points of the agent execution flow. All callbacks extend the `AsyncCallbackHandler` base class and are registered with `ComputerAgent` during initialization.

**Key Design Principles**:
- **Async-first**: All hooks are async to support I/O operations (e.g., writing trajectories, sending telemetry).
- **Optional implementation**: Callbacks only need to implement hooks they care about.
- **Early termination**: `on_run_continue` can stop execution (e.g., when budget is exceeded).

**Callback Registration Flow**

```mermaid
graph TB
    subgraph "Callback Registration"
        [Agent] --> [AutoCallbacks]
        [Agent] --> [UserCallbacks]
        
        [Agent] ["ComputerAgent.__init__"]
    end
    
    subgraph "Built-in Callbacks"
        [OperatorNormalizer] ["OperatorNormalizerCallback"]
        [Logging] ["LoggingCallback"]
        [TrajectorySaver] ["TrajectorySaverCallback"]
        [BudgetManager] ["BudgetManagerCallback"]
        [Telemetry] ["TelemetryCallback"]
    end
    
    [AutoCallbacks] --> [OperatorNormalizer]
    [AutoCallbacks] --> [Logging]
    [AutoCallbacks] --> [TrajectorySaver]
    [AutoCallbacks] --> [BudgetManager]
    [AutoCallbacks] --> [Telemetry]
    
    subgraph "Callback List"
        [CallbacksList] ["self.callbacks: List[AsyncCallbackHandler]"]
    end
    
    [OperatorNormalizer] --> [CallbacksList]
    [Logging] --> [CallbacksList]
    [TrajectorySaver] --> [CallbacksList]
    [BudgetManager] --> [CallbacksList]
    [Telemetry] --> [CallbacksList]
    [UserCallbacks] --> [CallbacksList]
```

Sources: [libs/python/agent/pyproject.toml:5-26](), [libs/python/core/pyproject.toml:5-17]()

---

## Agent Lifecycle Hooks

The `ComputerAgent` class provides lifecycle hooks that callbacks can implement. Each hook is called at a specific point in the agent execution flow during the `run()` method.

### Hook Categories

| Category | Hooks | Purpose |
|----------|-------|---------|
| **Run-Level** | `on_run_start`, `on_run_end`, `on_run_continue` | Overall lifecycle and execution control. |
| **Message Processing** | `on_llm_start`, `on_llm_end`, `on_responses` | Intercepting and transforming LLM inputs/outputs. |
| **Action Execution** | `on_computer_call_start`, `on_computer_call_end` | Tracking tool usage and results. |
| **Observability** | `on_usage`, `on_screenshot` | Visibility into costs and visual state. |

Sources: [libs/python/agent/pyproject.toml:5-26](), [libs/python/core/pyproject.toml:5-17]()

---

## Telemetry and Initialization

The framework includes a robust telemetry system designed for observability while respecting user privacy. Telemetry is enabled by default but can be disabled via environment variables or initialization flags. The core telemetry logic is housed in `cua-core` [libs/python/core/pyproject.toml:5-17]().

### Telemetry Configuration
Telemetry is primarily managed through `posthog-python` [libs/python/core/pyproject.toml:15-15](). It can be further extended to support OpenTelemetry for operational metrics like the "Four Golden Signals" (latency, traffic, errors, saturation) using the `otel` optional dependency group [libs/python/core/pyproject.toml:19-24]() or the `telemetry` optional dependency group [libs/python/core/pyproject.toml:26-31]().

### Event Tracking
The system tracks several key events to monitor agent performance and usage patterns:
- **agent_init**: Recorded when a `ComputerAgent` is instantiated.
- **agent_usage**: Tracks token consumption using `litellm` integration [libs/python/agent/pyproject.toml:23-23]().
- **computer_action_executed**: Tracks the types of actions performed (e.g., "click", "screenshot").
- **agent_tool_executed**: Tracks execution of specific tools.

**Code Entity Mapping**

```mermaid
classDiagram
    class [PostHogTelemetryClient] {
        +record_event(name, properties)
    }
    
    class [ComputerAgent] {
        +model: str
        +telemetry_enabled: bool
        +run(messages)
    }
    
    class [AsyncCallbackHandler] {
        +on_run_start()
        +on_usage()
        +on_computer_call_end()
    }
    
    [ComputerAgent] ..> [AsyncCallbackHandler] : "triggers"
    [AsyncCallbackHandler] ..> [PostHogTelemetryClient] : "reports to"
```

Sources: [libs/python/core/pyproject.toml:5-31](), [libs/python/agent/pyproject.toml:5-26]()

---

## Logging and Error Handling

Cua utilizes a structured logging approach. The `cua-agent` package depends on `rich` for formatted console output [libs/python/agent/pyproject.toml:20-20]() and `python-dotenv` for configuration management [libs/python/agent/pyproject.toml:21-21](). The `cua-computer-server` also uses `fastapi` and `uvicorn` for its API, which have their own logging mechanisms.

### Error Types
The framework distinguishes between different failure modes:
- **Tool Errors**: Failures within the execution of a specific tool (e.g., shell command failure).
- **LLM Errors**: Issues communicating with model providers, often handled via `litellm` [libs/python/agent/pyproject.toml:23-23]().
- **Infrastructure Errors**: Issues with the underlying sandbox or VM, such as Lume API timeouts.

### Lume API Error Handling
When interacting with macOS VMs via the Lume provider, the system specifically handles `curl` exit codes to provide descriptive feedback. For example:
- **Code 7**: Connection failure (API server starting up).
- **Code 28**: Operation timeout.
- **Code 52**: Empty reply (Server not fully ready).

Sources: [libs/python/agent/pyproject.toml:20-23]()

---

