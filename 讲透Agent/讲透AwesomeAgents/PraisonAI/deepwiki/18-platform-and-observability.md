<!-- source: DeepWiki mcp.deepwiki.com · repo MervinPraison/PraisonAI · page 18 Platform and Observability · fetched 2026-10-26 -->

# Platform and Observability

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/python/performance_monitoring_demo.py](examples/python/performance_monitoring_demo.py)
- [src/praisonai-agents/TELEMETRY_SUMMARY.md](src/praisonai-agents/TELEMETRY_SUMMARY.md)
- [src/praisonai-agents/debug_auto_instrument.py](src/praisonai-agents/debug_auto_instrument.py)
- [src/praisonai-agents/debug_telemetry.py](src/praisonai-agents/debug_telemetry.py)
- [src/praisonai-agents/debug_telemetry_double.py](src/praisonai-agents/debug_telemetry_double.py)
- [src/praisonai-agents/praisonaiagents/cli_backend/__init__.py](src/praisonai-agents/praisonaiagents/cli_backend/__init__.py)
- [src/praisonai-agents/praisonaiagents/cli_backend/debug.py](src/praisonai-agents/praisonaiagents/cli_backend/debug.py)
- [src/praisonai-agents/praisonaiagents/hooks/__init__.py](src/praisonai-agents/praisonaiagents/hooks/__init__.py)
- [src/praisonai-agents/praisonaiagents/hooks/events.py](src/praisonai-agents/praisonaiagents/hooks/events.py)
- [src/praisonai-agents/praisonaiagents/hooks/types.py](src/praisonai-agents/praisonaiagents/hooks/types.py)
- [src/praisonai-agents/praisonaiagents/kanban/__init__.py](src/praisonai-agents/praisonaiagents/kanban/__init__.py)
- [src/praisonai-agents/praisonaiagents/kanban/protocols.py](src/praisonai-agents/praisonaiagents/kanban/protocols.py)
- [src/praisonai-agents/praisonaiagents/telemetry/README.md](src/praisonai-agents/praisonaiagents/telemetry/README.md)
- [src/praisonai-agents/praisonaiagents/telemetry/__init__.py](src/praisonai-agents/praisonaiagents/telemetry/__init__.py)
- [src/praisonai-agents/praisonaiagents/telemetry/integration.py](src/praisonai-agents/praisonaiagents/telemetry/integration.py)
- [src/praisonai-agents/praisonaiagents/telemetry/performance_cli.py](src/praisonai-agents/praisonaiagents/telemetry/performance_cli.py)
- [src/praisonai-agents/praisonaiagents/telemetry/performance_monitor.py](src/praisonai-agents/praisonaiagents/telemetry/performance_monitor.py)
- [src/praisonai-agents/praisonaiagents/telemetry/performance_utils.py](src/praisonai-agents/praisonaiagents/telemetry/performance_utils.py)
- [src/praisonai-agents/praisonaiagents/telemetry/telemetry.py](src/praisonai-agents/praisonaiagents/telemetry/telemetry.py)
- [src/praisonai-agents/praisonaiagents/tools/subagent_tool.py](src/praisonai-agents/praisonaiagents/tools/subagent_tool.py)
- [src/praisonai-agents/telemetry_analysis.md](src/praisonai-agents/telemetry_analysis.md)
- [src/praisonai-agents/test_telemetry_performance.py](src/praisonai-agents/test_telemetry_performance.py)
- [src/praisonai-agents/tests/unit/hooks/test_model_fallback.py](src/praisonai-agents/tests/unit/hooks/test_model_fallback.py)
- [src/praisonai-agents/tests/unit/test_cli_backend_hook.py](src/praisonai-agents/tests/unit/test_cli_backend_hook.py)
- [src/praisonai-agents/tests/unit/test_kanban_protocol.py](src/praisonai-agents/tests/unit/test_kanban_protocol.py)
- [src/praisonai-agents/tests/unit/tools/test_subagent_tool.py](src/praisonai-agents/tests/unit/tools/test_subagent_tool.py)
- [src/praisonai/praisonai/cli/commands/kanban.py](src/praisonai/praisonai/cli/commands/kanban.py)
- [src/praisonai/praisonai/integration/bridges/kanban_bridge.py](src/praisonai/praisonai/integration/bridges/kanban_bridge.py)
- [src/praisonai/praisonai/kanban/__init__.py](src/praisonai/praisonai/kanban/__init__.py)
- [src/praisonai/praisonai/tools/__init__.py](src/praisonai/praisonai/tools/__init__.py)
- [src/praisonai/praisonai/tools/kanban_tools.py](src/praisonai/praisonai/tools/kanban_tools.py)
- [src/praisonai/tests/unit/test_kanban_sqlite_store.py](src/praisonai/tests/unit/test_kanban_sqlite_store.py)

</details>



The PraisonAI platform layer provides the multi-tenant, observable foundation for agentic workflows. It bridges the core `praisonaiagents` library with production-grade infrastructure, including a centralized event bus, comprehensive lifecycle hooks, and high-performance telemetry.

## Platform and Multi-Tenancy

The platform layer (detailed in [PraisonAI Platform](#18.1)) manages the transition from local scripts to multi-user environments. It handles workspace isolation, project management, and the `PlatformClient` SDK. This layer is responsible for maintaining the `tenant` context [src/praisonai-agents/praisonaiagents/kanban/protocols.py:41-41]() and providing a FastAPI-based backend for remote agent management.

For details, see [PraisonAI Platform](#18.1).

## Event Bus and Hooks System

The hook system is the primary mechanism for intercepting and modifying agent behavior without altering core code. Unlike UI-driven callbacks, hooks can block execution, modify tool inputs, or route model fallbacks [src/praisonai-agents/praisonaiagents/hooks/__init__.py:4-6]().

### Hook Lifecycle and Types
The system supports both Python function hooks and external shell command hooks [src/praisonai-agents/praisonaiagents/hooks/__init__.py:9-11](). Events cover the entire execution spectrum, from `BEFORE_AGENT` [src/praisonai-agents/praisonaiagents/hooks/events.py:74-74]() to specialized events like `SESSION_PERSIST_FAILED` [src/praisonai-agents/praisonaiagents/hooks/types.py:38-38]() and `MODEL_FALLBACK` [src/praisonai-agents/praisonaiagents/hooks/types.py:47-47]().

### Kanban Protocol
The `KanbanStoreProtocol` [src/praisonai-agents/praisonaiagents/kanban/protocols.py:80-88]() defines how tasks are tracked across statuses such as `triage`, `running`, and `blocked` [src/praisonai-agents/praisonaiagents/kanban/protocols.py:17-26](). This protocol enables the `praisonai-platform` to visualize agent progress in real-time.

For details, see [Event Bus and Hooks](#18.2).

### Hook System Architecture
The following diagram illustrates how the `HookRunner` interacts with various lifecycle events and external command hooks.

**Hook Execution Flow**
```mermaid
graph TD
    subgraph "Agent Runtime"
        [Agent.run] --> [HookRunner.run_hooks]
    end

    subgraph "HookRegistry"
        [HookRunner.run_hooks] --> [FunctionHook]
        [HookRunner.run_hooks] --> [CommandHook]
    end

    subgraph "Event Contexts"
        [FunctionHook] --> [BeforeToolInput]
        [FunctionHook] --> [AfterLLMInput]
        [CommandHook] --> [HookResult]
    end

    [HookResult] -- "Decision: allow/deny/block" --> [Agent.run]
```
**Sources:** [src/praisonai-agents/praisonaiagents/hooks/__init__.py:22-45](), [src/praisonai-agents/praisonaiagents/hooks/types.py:113-185](), [src/praisonai-agents/praisonaiagents/hooks/runner.py]()

## Tracing and Observability

PraisonAI implements a privacy-first, high-performance telemetry system designed to minimize overhead while providing deep insights into agent performance [src/praisonai-agents/praisonaiagents/telemetry/telemetry.py:4-6]().

### Telemetry and Performance
The `MinimalTelemetry` class [src/praisonai-agents/praisonaiagents/telemetry/telemetry.py:111-121]() collects anonymous metrics such as `agent_executions` and `tool_calls` [src/praisonai-agents/praisonaiagents/telemetry/telemetry.py:175-180](). To ensure zero impact on agent latency, telemetry operations are offloaded to a background `ThreadPoolExecutor` [src/praisonai-agents/praisonaiagents/telemetry/integration.py:54-57]() and processed via a `Queue` [src/praisonai-agents/praisonaiagents/telemetry/integration.py:71-71]().

### Performance Monitoring
The `PerformanceMonitor` [src/praisonai-agents/praisonaiagents/telemetry/performance_monitor.py:36-45]() tracks function execution times, identifying bottlenecks where `avg_duration` exceeds thresholds [src/praisonai-agents/praisonaiagents/telemetry/performance_utils.py:176-178]().

For details, see [Tracing and Observability](#18.3).

### Observability Data Flow
This diagram shows how telemetry data is captured from code entities and processed asynchronously to avoid blocking the main execution thread.

**Telemetry Pipeline**
```mermaid
graph LR
    subgraph "Code Execution"
        [Agent.chat] --> [instrument_agent]
        [Tool.call] --> [track_tool_usage]
    end

    subgraph "Async Processing"
        [track_tool_usage] --> [_queue_telemetry_event]
        [_queue_telemetry_event] -- "Non-blocking" --> [telemetry_queue]
        [telemetry_queue] --> [_process_telemetry_queue]
    end

    subgraph "Storage & Analysis"
        [_process_telemetry_queue] --> [MinimalTelemetry._metrics]
        [_process_telemetry_queue] --> [Posthog]
        [PerformanceMonitor] --> [FunctionFlowAnalyzer]
    end
```
**Sources:** [src/praisonai-agents/praisonaiagents/telemetry/telemetry.py:170-181](), [src/praisonai-agents/praisonaiagents/telemetry/integration.py:87-115](), [src/praisonai-agents/praisonaiagents/telemetry/performance_monitor.py:72-92]()

## Platform Component Overview

| Component | Code Entity | Purpose |
| :--- | :--- | :--- |
| **Hook Registry** | `HookRegistry` | Central store for all lifecycle hooks [src/praisonai-agents/praisonaiagents/hooks/registry.py](). |
| **Telemetry Collector** | `MinimalTelemetry` | Anonymous usage tracking with opt-out support [src/praisonai-agents/praisonaiagents/telemetry/telemetry.py:111-111](). |
| **Performance Monitor**| `PerformanceMonitor` | Real-time tracking of function and API latency [src/praisonai-agents/praisonaiagents/telemetry/performance_monitor.py:36-36](). |
| **Flow Analyzer** | `FunctionFlowAnalyzer`| Advanced visualization of execution patterns [src/praisonai-agents/praisonaiagents/telemetry/performance_utils.py:41-41](). |
| **Kanban Store** | `KanbanStoreProtocol` | Interface for task state persistence (e.g., SQLite) [src/praisonai-agents/praisonaiagents/kanban/protocols.py:80-80](). |

**Sources:** [src/praisonai-agents/praisonaiagents/hooks/__init__.py:49-62](), [src/praisonai-agents/praisonaiagents/telemetry/__init__.py:67-83](), [src/praisonai-agents/praisonaiagents/kanban/protocols.py:17-26]()

---

