<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-agents-python · page 3 Core Concepts · fetched 2026-10-26 -->

# Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/agents/agent.py](src/agents/agent.py)
- [src/agents/exceptions.py](src/agents/exceptions.py)
- [src/agents/result.py](src/agents/result.py)
- [src/agents/run.py](src/agents/run.py)
- [src/agents/run_config.py](src/agents/run_config.py)
- [src/agents/run_internal/agent_runner_helpers.py](src/agents/run_internal/agent_runner_helpers.py)
- [src/agents/run_internal/run_loop.py](src/agents/run_internal/run_loop.py)
- [src/agents/run_internal/run_steps.py](src/agents/run_internal/run_steps.py)
- [src/agents/run_internal/session_persistence.py](src/agents/run_internal/session_persistence.py)
- [src/agents/run_internal/turn_resolution.py](src/agents/run_internal/turn_resolution.py)
- [src/agents/run_state.py](src/agents/run_state.py)
- [src/agents/tool_context.py](src/agents/tool_context.py)
- [tests/test_agent_as_tool.py](tests/test_agent_as_tool.py)
- [tests/test_agent_runner.py](tests/test_agent_runner.py)
- [tests/test_agent_runner_streamed.py](tests/test_agent_runner_streamed.py)
- [tests/test_error_logging_redaction.py](tests/test_error_logging_redaction.py)
- [tests/test_example_workflows.py](tests/test_example_workflows.py)
- [tests/test_run_config.py](tests/test_run_config.py)
- [tests/test_run_impl_resume_paths.py](tests/test_run_impl_resume_paths.py)
- [tests/test_run_state.py](tests/test_run_state.py)
- [tests/test_source_compat_constructors.py](tests/test_source_compat_constructors.py)
- [tests/test_tool_context.py](tests/test_tool_context.py)

</details>



This document establishes the foundational abstractions that underpin the OpenAI Agents SDK: agents, execution mechanisms, result and output handling, serializable state, dependency injection contexts, and global run configurations. 

As a PARENT page, this section provides a high-level overview of these core concepts and links to detailed child pages for deep technical dives.

For detailed information, see:
- [Agent Architecture](#3.1)
- [Runner and Execution Flow](#3.2)
- [RunResult and Output Management](#3.3)
- [RunState and Resumption](#3.4)
- [Context and Dependency Injection](#3.5)
- [Run Configuration](#3.6)

## Core Abstractions Overview

The SDK architecture centers on typed objects that manage instructions, execution state, tool dispatch, and runtime boundaries.

Title: Core Concept Relationships
```mermaid
graph TB
    subgraph "User Application Space"
        ["ApplicationCode"]
        ["CustomContextObject"]
    end
    
    subgraph "Code Entity Space: Core Orchestration"
        ["Runner"]
        ["Agent"]
        ["RunResult"]
        ["RunState"]
    end
    
    subgraph "Code Entity Space: Context & Injection"
        ["RunContextWrapper"]
        ["ToolContext"]
    end
    
    ["ApplicationCode"] -->|"configures"| ["Agent"]
    ["ApplicationCode"] -->|"invokes"| ["Runner"]
    ["Runner"] -->|"executes"| ["Agent"]
    ["Runner"] -->|"wraps context in"| ["RunContextWrapper"]
    ["Runner"] -->|"returns"| ["RunResult"]
    ["RunResult"] -->|"snapshots into"| ["RunState"]
    ["RunState"] -->|"resumes via"| ["Runner"]
    ["RunContextWrapper"] -->|"specialized as"| ["ToolContext"]
    ["ToolContext"] -->|"injected into"| ["FunctionTool"]
```
Sources: [src/agents/run.py:213-227](), [src/agents/agent.py:183-187](), [src/agents/result.py:107-120](), [src/agents/run_state.py:94-98](), [src/agents/tool_context.py:36-40]()

---

## Agent Architecture

The `Agent` class defines an LLM-powered assistant with specific behavioral properties, system prompts, available tools, handoff targets, guardrails, and structured output formatting [src/agents/agent.py:183-261](). Agents serve as the atomic unit of reasoning and delegation within a multi-agent topology.

For full details on configuration parameters, hook integrations, and agent lifecycles, see [Agent Architecture](#3.1).

Sources: [src/agents/agent.py:183-318]()

---

## Runner and Execution Flow

The `Runner` class orchestrates the execution lifecycle via methods such as `Runner.run()`, `run_sync()`, and `Runner.run_streamed()` [src/agents/run.py:213-271](). It drives the internal turn loop, manages `max_turns`, evaluates guardrails, and coordinates model calls and tool executions [src/agents/run.py:39-39](), [src/agents/run_internal/run_loop.py:104-104]().

Title: Natural Language to Code Flow
```mermaid
sequenceDiagram
    participant User as "Application Code"
    participant Runner as "Runner"
    participant Loop as "run_loop.py"
    participant Agent as "Agent"
    participant Model as "Model Interface"
    
    User->>Runner: "Runner.run(agent, input)"
    Runner->>Loop: "run_single_turn()"
    Loop->>Agent: "get_all_tools(context)"
    Loop->>Model: "get_response(input, tools)"
    Model-->>Loop: "ModelResponse"
    Loop->>Loop: "process_model_response()"
    Note over Loop: "Execute tools / handoffs / guardrails"
    Loop-->>Runner: "SingleStepResult"
    Runner-->>User: "RunResult"
```
Sources: [src/agents/run.py:214-227](), [src/agents/run_internal/run_loop.py:104-104](), [src/agents/run_internal/turn_resolution.py:198-199]()

For complete details on turn loops and streaming mechanics, see [Runner and Execution Flow](#3.2).

Sources: [src/agents/run.py:213-271](), [src/agents/run_internal/run_loop.py:104-104]()

---

## RunResult and Output Management

`RunResult` and `RunResultStreaming` encapsulate the terminal outputs, generated items, raw model responses, and usage metrics of an agent run [src/agents/result.py:107-167](), [src/agents/result.py:441-454](). They provide helper methods like `to_input_list()` and `to_state()` for continuation workflows.

For detailed documentation on output attributes, streaming events, and item conversions, see [RunResult and Output Management](#3.3).

Sources: [src/agents/result.py:107-167](), [src/agents/result.py:441-454]()

---

## RunState and Resumption

`RunState` provides a serializable snapshot of execution state [src/agents/run_state.py:94-98](). It enables Human-in-the-Loop (HITL) workflows by allowing runs to pause at approval gates, serialize state to JSON, persist across storage layers, and resume cleanly via `approve()` or `reject()` logic [src/agents/run_state.py:330-366]().

For deep dives into serialization schemas, pause/resume workflows, and persistence backends, see [RunState and Resumption](#3.4).

Sources: [src/agents/run_state.py:94-1033]()

---

## Context and Dependency Injection

`RunContextWrapper` and `ToolContext` manage state propagation and dependency injection across agent turns and tool calls [src/agents/run_context.py:50-54](), [src/agents/tool_context.py:36-50](). They provide runtime access to user-defined context objects, usage tracking, and tool execution metadata.

For details on context propagation and dependency injection patterns, see [Context and Dependency Injection](#3.5).

Sources: [src/agents/run_context.py:50-134](), [src/agents/tool_context.py:36-171]()

---

## Run Configuration

The `RunConfig` class specifies global execution overrides, model settings, tracing options, error handlers, and tool execution parameters [src/agents/run_config.py:330-410](). It configures guardrail behaviors and input filters applied across all turns in a run.

For full configuration options, see [Run Configuration](#3.6).

Sources: [src/agents/run_config.py:329-410]()

---

## Data Structures and Conversation Items

The SDK uses strongly-typed conversation items inheriting from `RunItem` to track session history and model exchanges [src/agents/items.py:26]().

| Item Type | Description | Code Entity |
|-----------|-------------|-------------|
| **Message** | Assistant message from the LLM | `MessageOutputItem` [src/agents/__init__.py:63]() |
| **Tool Call** | LLM request to execute a tool | `ToolCallItem` [src/agents/__init__.py:68]() |
| **Tool Output** | Result of a tool execution | `ToolCallOutputItem` [src/agents/__init__.py:69]() |
| **Handoff** | LLM request to switch active agents | `HandoffCallItem` [src/agents/__init__.py:57]() |
| **Reasoning** | Internal model reasoning steps | `ReasoningItem` [src/agents/__init__.py:65]() |

Sources: [src/agents/items.py:26-110](), [src/agents/__init__.py:55-73]()

---

