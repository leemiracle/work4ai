<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-agents-python · page 18 Glossary · fetched 2026-10-26 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/config.md](docs/config.md)
- [docs/examples.md](docs/examples.md)
- [docs/guardrails.md](docs/guardrails.md)
- [docs/human_in_the_loop.md](docs/human_in_the_loop.md)
- [docs/index.md](docs/index.md)
- [docs/mcp.md](docs/mcp.md)
- [docs/models/index.md](docs/models/index.md)
- [docs/realtime/guide.md](docs/realtime/guide.md)
- [docs/realtime/quickstart.md](docs/realtime/quickstart.md)
- [docs/ref/sandbox/util/blocking_io.md](docs/ref/sandbox/util/blocking_io.md)
- [docs/ref/tool_context.md](docs/ref/tool_context.md)
- [docs/release.md](docs/release.md)
- [docs/results.md](docs/results.md)
- [docs/running_agents.md](docs/running_agents.md)
- [docs/sessions/index.md](docs/sessions/index.md)
- [docs/streaming.md](docs/streaming.md)
- [docs/tools.md](docs/tools.md)
- [docs/tracing.md](docs/tracing.md)
- [examples/basic/tools.py](examples/basic/tools.py)
- [mkdocs.yml](mkdocs.yml)
- [src/agents/__init__.py](src/agents/__init__.py)
- [src/agents/exceptions.py](src/agents/exceptions.py)
- [src/agents/function_schema.py](src/agents/function_schema.py)
- [src/agents/result.py](src/agents/result.py)
- [src/agents/run.py](src/agents/run.py)
- [src/agents/run_internal/agent_runner_helpers.py](src/agents/run_internal/agent_runner_helpers.py)
- [src/agents/run_internal/run_loop.py](src/agents/run_internal/run_loop.py)
- [src/agents/run_internal/run_steps.py](src/agents/run_internal/run_steps.py)
- [src/agents/run_internal/session_persistence.py](src/agents/run_internal/session_persistence.py)
- [src/agents/run_internal/turn_resolution.py](src/agents/run_internal/turn_resolution.py)
- [src/agents/run_state.py](src/agents/run_state.py)
- [src/agents/tool.py](src/agents/tool.py)
- [tests/sandbox/test_session_utils.py](tests/sandbox/test_session_utils.py)
- [tests/test_agent_runner.py](tests/test_agent_runner.py)
- [tests/test_agent_runner_streamed.py](tests/test_agent_runner_streamed.py)
- [tests/test_error_logging_redaction.py](tests/test_error_logging_redaction.py)
- [tests/test_function_schema.py](tests/test_function_schema.py)
- [tests/test_function_schema_logger_restore.py](tests/test_function_schema_logger_restore.py)
- [tests/test_function_tool.py](tests/test_function_tool.py)
- [tests/test_function_tool_decorator.py](tests/test_function_tool_decorator.py)
- [tests/test_run_impl_resume_paths.py](tests/test_run_impl_resume_paths.py)
- [tests/test_run_state.py](tests/test_run_state.py)

</details>



This page defines codebase-specific terms, jargon, and domain concepts used throughout the OpenAI Agents SDK. It serves as a technical reference for onboarding engineers to understand the implementation details and data flow of core entities.

## Core Entities and Execution

### Agent
The primary unit of logic. An `Agent` encapsulates instructions, a specific LLM model, tools, and handoff logic. It can be treated as a standalone entity or as a tool by other agents.
*   **Implementation**: Defined in `AgentBase` [src/agents/agent.py:183-184]() and its subclass `Agent` [src/agents/agent.py:225-226]().
*   **Key Attributes**: `instructions`, `tools`, `handoff_description`, and `output_type` [src/agents/agent.py:186-250]().

### RealtimeAgent
A specialized agent designed for low-latency, event-driven interactions, typically over WebSockets. It supports modalities like audio and is optimized for the OpenAI Realtime API.
*   **Implementation**: `RealtimeAgent` class [src/agents/realtime/agent.py:109-110]().
*   **Context**: Often used with `RealtimeSession` [src/agents/realtime/session.py:174-175]().

### SandboxAgent
A specialized agent preconfigured to work within an isolated container or workspace. It is designed for tasks requiring filesystem access, command execution, or long-term state persistence.
*   **Implementation**: `SandboxAgent` class [README.md:49-50]().
*   **Key Components**: Uses a `Manifest` to define the environment [README.md:51-52]() and a `SandboxRunConfig` for execution [README.md:56-57]().

### Runner
The orchestration engine that manages the execution loop of an agent. It handles the transition between LLM generations, tool executions, and agent handoffs.
*   **Implementation**: `Runner` class [src/agents/run.py:212-213]().
*   **Methods**: `run()`, `run_sync()`, and `run_streamed()` [src/agents/run.py:214-280]().

### Turn
A single iteration of the execution loop. A turn typically consists of sending input to a model, receiving a response, and processing that response (e.g., executing tools or performing a handoff).
*   **Implementation**: Managed by `run_single_turn` [src/agents/run_internal/run_loop.py:104-105]().

### RunState
A serializable snapshot of a run's progress. It contains the current agent, conversation history, and any pending interruptions (like tool approvals).
*   **Implementation**: `RunState` class [src/agents/run_state.py:65-66]().
*   **Data Flow**: Generated during `Runner.run()` and can be passed back into `Runner.run()` to resume an execution [src/agents/run.py:214-225]().

Sources: [src/agents/agent.py:183-250](), [src/agents/realtime/agent.py:109-110](), [src/agents/realtime/session.py:174-175](), [README.md:49-57](), [src/agents/run.py:212-280](), [src/agents/run_internal/run_loop.py:104-105](), [src/agents/run_state.py:65-66]()

---

## Natural Language to Code Mapping: Execution Flow

The following diagram bridges the conceptual "Agent Workflow" to the specific classes and functions that handle the execution.

**Execution Entity Mapping**
```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        A[""The Agent Loop""]
        B[""Resuming a Conversation""]
        C[""Streaming Results""]
        D[""Isolated Workspace""]
        E[""Voice/Audio Interaction""]
    end

    subgraph "CodeEntitySpace"
        A --> Runner_run[""Runner.run() [src/agents/run.py:214-225]""]
        Runner_run --> run_single_turn[""run_internal.run_loop.run_single_turn() [src/agents/run_internal/run_loop.py:104-105]""]
        
        B --> RunState[""RunState [src/agents/run_state.py:65-66]""]
        RunState --> Runner_run
        
        C --> RunResultStreaming[""RunResultStreaming [src/agents/result.py:150-151]""]
        RunResultStreaming --> stream_events[""stream_events() [src/agents/result.py:160-161]""]

        D --> SandboxAgent[""SandboxAgent [README.md:49-50]""]
        
        E --> RealtimeSession[""RealtimeSession [src/agents/realtime/session.py:174-175]""]
    end
```
Sources: [src/agents/run.py:214-225](), [src/agents/run_state.py:65-66](), [src/agents/result.py:150-161](), [README.md:49-50](), [src/agents/run_internal/run_loop.py:104-105](), [src/agents/realtime/session.py:174-175]()

---

## Tooling and Capabilities

### FunctionTool
A wrapper around a Python function that allows it to be called by an LLM. It handles schema generation (via Pydantic or docstrings) and argument validation.
*   **Implementation**: `FunctionTool` class [src/agents/tool.py:236-237]().
*   **Decorator**: `@function_tool` [src/agents/tool.py:768-769]().

### Handoff
A mechanism where one agent transfers control of the conversation to another agent.
*   **Implementation**: `Handoff` class [src/agents/handoffs.py:48-49]().
*   **Trigger**: Represented in code as a `HandoffCallItem` [src/agents/items.py:338-339]().

### MCP (Model Context Protocol)
An open protocol that enables agents to access tools and resources from external servers.
*   **Implementation**: `MCPServer` [src/agents/mcp/server.py:224-225]() and `MCPServerManager` [src/agents/mcp/manager.py:35-36]().

Sources: [src/agents/tool.py:236-769](), [src/agents/handoffs.py:48-49](), [src/agents/items.py:338-339](), [src/agents/mcp/server.py:224-225](), [src/agents/mcp/manager.py:35-36]()

---

## Natural Language to Code Mapping: Tooling System

This diagram associates tool-related jargon with the underlying implementation classes.

**Tool System Mapping**
```mermaid
graph LR
    subgraph "NaturalLanguageSpace"
        T1[""Custom Python Tool""]
        T2[""Switching Agents""]
        T3[""External Tool Server""]
        T4[""Local Shell""]
    end

    subgraph "CodeEntitySpace"
        T1 --> FunctionTool[""FunctionTool [src/agents/tool.py:236-237]""]
        T2 --> Handoff[""Handoff [src/agents/handoffs.py:48-49]""]
        T3 --> MCPServer[""MCPServer [src/agents/mcp/server.py:224-225]""]
        T4 --> ShellTool[""ShellTool [src/agents/tool.py:1280-1281]""]
    end
```
Sources: [src/agents/tool.py:236-237](), [src/agents/tool.py:1280-1281](), [src/agents/handoffs.py:48-49](), [src/agents/mcp/server.py:224-225]()

---

## Tracing and Observability

### Span
A timed operation within a trace. Spans are hierarchical, representing the nested nature of agent calls, tool executions, and LLM generations.
*   **Implementation**: `Span` class [src/agents/tracing/span.py:30-31]().
*   **Types**: `AgentSpanData`, `GenerationSpanData`, `FunctionSpanData` [src/agents/tracing/span_data.py:10-100]().

### Trace
A collection of spans representing a single end-to-end workflow execution.
*   **Implementation**: `Trace` class [src/agents/tracing/trace.py:20-21]().

Sources: [src/agents/tracing/span.py:30-31](), [src/agents/tracing/span_data.py:10-100](), [src/agents/tracing/trace.py:20-21]()

---

## Glossary Table

| Term | Definition | Code Pointer |
| :--- | :--- | :--- |
| **RunItem** | The base class for all discrete events in a conversation history (messages, tool calls, etc.). | [src/agents/items.py:114-115]() |
| **Context** | A user-defined object passed through the run, accessible to tools and guardrails. | `TContext` in [src/agents/run_context.py:18-19]() |
| **Guardrail** | A validation function that checks inputs or outputs for safety and compliance. | `InputGuardrail` / `OutputGuardrail` [src/agents/guardrail.py:25-50]() |
| **Tripwire** | A specific type of guardrail that halts execution immediately if triggered. | `is_tripwire` flag in [src/agents/guardrail.py:32-33]() |
| **Session** | A persistence layer for storing and retrieving `RunItem` history. | `SessionABC` [src/agents/memory/session.py:25-26]() |
| **RealtimeSession** | A specialized session for low-latency WebSocket-based audio/text interactions. | `RealtimeSession` [src/agents/realtime/session.py:174-175]() |
| **Manifest** | A declarative definition of a sandbox environment, including files, repos, and environment variables. | `Manifest` [src/agents/sandbox/manifest.py:15-16]() |
| **Max Turns** | The safety limit on the number of iterations the `Runner` will perform in a single call. | `DEFAULT_MAX_TURNS` [src/agents/run_config.py:39-40]() |
| **AnyLLMModel** | A model wrapper allowing integration with multiple providers via LiteLLM or similar backends. | `AnyLLMModel` [src/agents/extensions/models/any_llm_model.py:16-17]() |

Sources: [src/agents/items.py:114-115](), [src/agents/run_context.py:18-19](), [src/agents/guardrail.py:25-50](), [src/agents/memory/session.py:25-26](), [src/agents/realtime/session.py:174-175](), [src/agents/sandbox/manifest.py:15-16](), [src/agents/run_config.py:39-40](), [src/agents/extensions/models/any_llm_model.py:16-17]()