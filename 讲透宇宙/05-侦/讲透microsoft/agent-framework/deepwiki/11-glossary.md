<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/agent-framework · page 11 Glossary · fetched 2026-10-26 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/decisions/0022-chat-history-persistence-consistency.md](docs/decisions/0022-chat-history-persistence-consistency.md)
- [docs/specs/004-python-function-calling-loop.md](docs/specs/004-python-function-calling-loop.md)
- [dotnet/samples/02-agents/Agents/Agent_Step19_InFunctionLoopCheckpointing/Program.cs](dotnet/samples/02-agents/Agents/Agent_Step19_InFunctionLoopCheckpointing/Program.cs)
- [dotnet/samples/02-agents/Agents/Agent_Step19_InFunctionLoopCheckpointing/README.md](dotnet/samples/02-agents/Agents/Agent_Step19_InFunctionLoopCheckpointing/README.md)
- [dotnet/src/Microsoft.Agents.AI.Abstractions/AdditionalPropertiesExtensions.cs](dotnet/src/Microsoft.Agents.AI.Abstractions/AdditionalPropertiesExtensions.cs)
- [dotnet/src/Microsoft.Agents.AI/ChatClient/ChatClientAgent.cs](dotnet/src/Microsoft.Agents.AI/ChatClient/ChatClientAgent.cs)
- [dotnet/src/Microsoft.Agents.AI/ChatClient/ChatClientAgentContinuationToken.cs](dotnet/src/Microsoft.Agents.AI/ChatClient/ChatClientAgentContinuationToken.cs)
- [dotnet/src/Microsoft.Agents.AI/ChatClient/ChatClientAgentLogMessages.cs](dotnet/src/Microsoft.Agents.AI/ChatClient/ChatClientAgentLogMessages.cs)
- [dotnet/src/Microsoft.Agents.AI/ChatClient/ChatClientAgentOptions.cs](dotnet/src/Microsoft.Agents.AI/ChatClient/ChatClientAgentOptions.cs)
- [dotnet/src/Microsoft.Agents.AI/ChatClient/ChatClientBuilderExtensions.cs](dotnet/src/Microsoft.Agents.AI/ChatClient/ChatClientBuilderExtensions.cs)
- [dotnet/src/Microsoft.Agents.AI/ChatClient/ChatClientExtensions.cs](dotnet/src/Microsoft.Agents.AI/ChatClient/ChatClientExtensions.cs)
- [dotnet/tests/Microsoft.Agents.AI.Abstractions.UnitTests/AdditionalPropertiesExtensionsTests.cs](dotnet/tests/Microsoft.Agents.AI.Abstractions.UnitTests/AdditionalPropertiesExtensionsTests.cs)
- [dotnet/tests/Microsoft.Agents.AI.UnitTests/ChatClient/ChatClientAgentContinuationTokenTests.cs](dotnet/tests/Microsoft.Agents.AI.UnitTests/ChatClient/ChatClientAgentContinuationTokenTests.cs)
- [dotnet/tests/Microsoft.Agents.AI.UnitTests/ChatClient/ChatClientAgentOptionsTests.cs](dotnet/tests/Microsoft.Agents.AI.UnitTests/ChatClient/ChatClientAgentOptionsTests.cs)
- [dotnet/tests/Microsoft.Agents.AI.UnitTests/ChatClient/ChatClientAgentTestHelper.cs](dotnet/tests/Microsoft.Agents.AI.UnitTests/ChatClient/ChatClientAgentTestHelper.cs)
- [dotnet/tests/Microsoft.Agents.AI.UnitTests/ChatClient/ChatClientAgentTests.cs](dotnet/tests/Microsoft.Agents.AI.UnitTests/ChatClient/ChatClientAgentTests.cs)
- [dotnet/tests/Microsoft.Agents.AI.UnitTests/ChatClient/ChatClientAgent_ApprovalsTests.cs](dotnet/tests/Microsoft.Agents.AI.UnitTests/ChatClient/ChatClientAgent_ApprovalsTests.cs)
- [dotnet/tests/Microsoft.Agents.AI.UnitTests/ChatClient/ChatClientAgent_BackgroundResponsesTests.cs](dotnet/tests/Microsoft.Agents.AI.UnitTests/ChatClient/ChatClientAgent_BackgroundResponsesTests.cs)
- [dotnet/tests/Microsoft.Agents.AI.UnitTests/ChatClient/ChatClientAgent_ChatHistoryManagementTests.cs](dotnet/tests/Microsoft.Agents.AI.UnitTests/ChatClient/ChatClientAgent_ChatHistoryManagementTests.cs)
- [dotnet/tests/Microsoft.Agents.AI.UnitTests/ChatClient/ChatClientAgent_ChatOptionsMergingTests.cs](dotnet/tests/Microsoft.Agents.AI.UnitTests/ChatClient/ChatClientAgent_ChatOptionsMergingTests.cs)
- [dotnet/tests/Microsoft.Agents.AI.UnitTests/ChatClient/ChatClientBuilderExtensionsTests.cs](dotnet/tests/Microsoft.Agents.AI.UnitTests/ChatClient/ChatClientBuilderExtensionsTests.cs)
- [dotnet/tests/Microsoft.Agents.AI.UnitTests/ChatClient/ChatClientExtensionsTests.cs](dotnet/tests/Microsoft.Agents.AI.UnitTests/ChatClient/ChatClientExtensionsTests.cs)
- [python/packages/core/AGENTS.md](python/packages/core/AGENTS.md)
- [python/packages/core/agent_framework/__init__.py](python/packages/core/agent_framework/__init__.py)
- [python/packages/core/agent_framework/__init__.pyi](python/packages/core/agent_framework/__init__.pyi)
- [python/packages/core/agent_framework/_agents.py](python/packages/core/agent_framework/_agents.py)
- [python/packages/core/agent_framework/_clients.py](python/packages/core/agent_framework/_clients.py)
- [python/packages/core/agent_framework/_compaction.py](python/packages/core/agent_framework/_compaction.py)
- [python/packages/core/agent_framework/_harness/_tool_approval.py](python/packages/core/agent_framework/_harness/_tool_approval.py)
- [python/packages/core/agent_framework/_middleware.py](python/packages/core/agent_framework/_middleware.py)
- [python/packages/core/agent_framework/_skills.py](python/packages/core/agent_framework/_skills.py)
- [python/packages/core/agent_framework/_tools.py](python/packages/core/agent_framework/_tools.py)
- [python/packages/core/agent_framework/_types.py](python/packages/core/agent_framework/_types.py)
- [python/packages/core/agent_framework/observability.py](python/packages/core/agent_framework/observability.py)
- [python/packages/core/tests/core/test_agent_hooks.py](python/packages/core/tests/core/test_agent_hooks.py)
- [python/packages/core/tests/core/test_agents.py](python/packages/core/tests/core/test_agents.py)
- [python/packages/core/tests/core/test_clients.py](python/packages/core/tests/core/test_clients.py)
- [python/packages/core/tests/core/test_compaction.py](python/packages/core/tests/core/test_compaction.py)
- [python/packages/core/tests/core/test_function_invocation_logic.py](python/packages/core/tests/core/test_function_invocation_logic.py)
- [python/packages/core/tests/core/test_harness_tool_approval.py](python/packages/core/tests/core/test_harness_tool_approval.py)
- [python/packages/core/tests/core/test_middleware_with_agent.py](python/packages/core/tests/core/test_middleware_with_agent.py)
- [python/packages/core/tests/core/test_middleware_with_chat.py](python/packages/core/tests/core/test_middleware_with_chat.py)
- [python/packages/core/tests/core/test_observability.py](python/packages/core/tests/core/test_observability.py)
- [python/packages/core/tests/core/test_skills.py](python/packages/core/tests/core/test_skills.py)
- [python/packages/core/tests/core/test_tools.py](python/packages/core/tests/core/test_tools.py)
- [python/packages/core/tests/core/test_types.py](python/packages/core/tests/core/test_types.py)
- [python/samples/02-agents/context_providers/cross_session_observer.py](python/samples/02-agents/context_providers/cross_session_observer.py)
- [python/samples/02-agents/observability/README.md](python/samples/02-agents/observability/README.md)
- [python/samples/02-agents/observability/microsoft_opentelemetry_distro.py](python/samples/02-agents/observability/microsoft_opentelemetry_distro.py)
- [python/samples/02-agents/skills/README.md](python/samples/02-agents/skills/README.md)
- [python/samples/02-agents/skills/class_based_skill/README.md](python/samples/02-agents/skills/class_based_skill/README.md)
- [python/samples/02-agents/skills/class_based_skill/class_based_skill.py](python/samples/02-agents/skills/class_based_skill/class_based_skill.py)
- [python/samples/02-agents/skills/code_defined_skill/README.md](python/samples/02-agents/skills/code_defined_skill/README.md)
- [python/samples/02-agents/skills/code_defined_skill/code_defined_skill.py](python/samples/02-agents/skills/code_defined_skill/code_defined_skill.py)
- [python/samples/02-agents/skills/file_based_skill/file_based_skill.py](python/samples/02-agents/skills/file_based_skill/file_based_skill.py)
- [python/samples/02-agents/skills/mixed_skills/README.md](python/samples/02-agents/skills/mixed_skills/README.md)
- [python/samples/02-agents/skills/mixed_skills/mixed_skills.py](python/samples/02-agents/skills/mixed_skills/mixed_skills.py)
- [python/samples/02-agents/skills/script_approval/script_approval.py](python/samples/02-agents/skills/script_approval/script_approval.py)
- [python/samples/02-agents/skills/subprocess_script_runner.py](python/samples/02-agents/skills/subprocess_script_runner.py)

</details>



This glossary defines codebase-specific terms, jargon, abbreviations, and domain concepts that an onboarding engineer needs to know when working with the Microsoft Agent Framework across .NET and Python. Each term includes code pointers to relevant files, classes, and functions.

## Core Abstractions

### Agent
The fundamental unit of the framework. An Agent is a high-level abstraction that encapsulates a chat client, system instructions, tools, and session management, providing a simplified interface for interacting with Large Language Models (LLMs).

* **Python Implementation**: `SupportsAgentRun` protocol and primary concrete class `Agent` defined in `[python/packages/core/agent_framework/_agents.py:1-187]()`.
* **.NET Implementation**: `ChatClientAgent` (inheriting from `AIAgent`) utilized for wrapping `IChatClient` logic `[dotnet/src/Microsoft.Agents.AI/ChatClient/ChatClientAgent.cs:1-100]()`.

Sources: `[python/packages/core/agent_framework/_agents.py:1-187]`, `[dotnet/src/Microsoft.Agents.AI/ChatClient/ChatClientAgent.cs:1-100]()`

### Chat Client
The low-level interface used to communicate with specific AI providers (OpenAI, Azure AI Foundry, Anthropic, etc.). It handles the raw request/response lifecycle, including message formatting and tool call processing.

* **Python Implementation**: `BaseChatClient` and `SupportsChatGetResponse` protocol in `[python/packages/core/agent_framework/_clients.py:1-50]()`.
* **.NET Implementation**: `IChatClient` interface (from `Microsoft.Extensions.AI`) is the primary integration point for provider-specific clients `[dotnet/src/Microsoft.Agents.AI/ChatClient/ChatClientAgent.cs:1-50]()`.

Sources: `[python/packages/core/agent_framework/_clients.py:1-50]`, `[dotnet/src/Microsoft.Agents.AI/ChatClient/ChatClientAgent.cs:1-50]()`

### Tool / Function Tool
A capability provided to an agent that allows it to perform actions or retrieve data from external systems. Tools are defined as functions with metadata (schemas) that the LLM uses to decide when and how to invoke them.

* **Python Implementation**: `FunctionTool` class and the `@tool` decorator in `[python/packages/core/agent_framework/_tools.py:1-50]()`.
* **.NET Implementation**: `AIFunction` and `AITool` abstractions used to expose local code to models `[dotnet/src/Microsoft.Agents.AI/ChatClient/ChatClientAgent.cs:50-90]()`.

Sources: `[python/packages/core/agent_framework/_tools.py:1-50]`, `[dotnet/src/Microsoft.Agents.AI/ChatClient/ChatClientAgent.cs:50-90]()`

---

## Technical Concepts

### AG-UI Protocol
A protocol and set of adapters for connecting agents to frontend user interfaces. It handles complex interactions like tool call approvals, streaming, and state snapshots.
* **Implementation**: Found in the `agent-framework-ag-ui` package and related .NET abstractions.
* **Key Components**: `AGUIThreadSnapshot` for state persistence and predictive state handlers for UI responsiveness.

Sources: `[dotnet/Directory.Packages.props:58-63]()`

### Context Provider
A component that injects additional information into the LLM prompt. This is used for dynamic data like user preferences or RAG results.
* **Python Implementation**: `ContextProvider` in `[python/packages/core/agent_framework/_sessions.py:1-100]()`.
* **Skills as Context**: `SkillsProvider` extends `ContextProvider` to dynamically inject skill instructions into the system prompt `[python/packages/core/agent_framework/_agents.py:1-50]()`.
* **.NET Implementation**: Managed via `ChatClientAgentOptions` which includes `ContextProviderFactories` `[dotnet/src/Microsoft.Agents.AI/ChatClient/ChatClientAgent.cs:80-120]()`.

Sources: `[python/packages/core/agent_framework/_sessions.py:1-100]`, `[python/packages/core/agent_framework/_agents.py:1-50]`, `[dotnet/src/Microsoft.Agents.AI/ChatClient/ChatClientAgent.cs:80-120]()`

### MCP (Model Context Protocol)
An open standard for connecting AI models to tools. The framework acts as an MCP client, allowing agents to use tools hosted on remote MCP servers.
* **Python Implementation**: `MCPTool` base class and transport wrappers.
* **Transports**: Standard I/O, HTTP, and WebSocket protocol channels.
* **Name Normalization**: Ensures remote tool names fit required naming patterns for LLM providers.

Sources: `[python/packages/core/agent_framework/_tools.py:70-95]()`

### Middleware / Layers
A pipeline pattern used to intercept and process requests/responses across chat clients, agents, and tool executions.
* **Python Implementation**: `AgentMiddlewareLayer`, `ChatMiddlewareLayer`, and `FunctionMiddleware` in `[python/packages/core/agent_framework/_middleware.py:1-100]()`.
* **.NET Implementation**: Pipelines constructed using `IChatClient` decorators and agent execution filters.

Sources: `[python/packages/core/agent_framework/_middleware.py:1-100]()`

### Workflow / Orchestration
A system for managing complex multi-agent interactions using a graph-based execution model.
* **Python Implementation**: `Workflow` class and related orchestration classes in `[python/packages/core/agent_framework/_workflows/_workflow.py:1-50]()`.
* **Execution**: Managed by `WorkflowExecutor` and `Runner` in `[python/packages/core/agent_framework/_workflows/_runner.py:1-50]()`.

Sources: `[python/packages/core/agent_framework/_workflows/_workflow.py:1-50]`, `[python/packages/core/agent_framework/_workflows/_runner.py:1-50]()`

---

## Relationship Diagrams

### Natural Language to Code: Agent Execution
This diagram maps a user's natural language intent to the internal code execution flow, highlighting the role of middleware and the chat client.

```mermaid
graph TD
    User[""User(NaturalLanguageRequest)""] -- "Agent.run()" --> AgentRun[""SupportsAgentRun(Protocol)""]
    AgentRun -- "Process" --> Middleware[""AgentMiddlewareLayer(Pipeline)""]
    Middleware -- "ChatRequest" --> ChatClient[""BaseChatClient(Implementation)""]
    ChatClient -- "API Call" --> LLM[""LLMProvider(OpenAI/Anthropic)""]
    LLM -- "ToolCall" --> ToolLayer[""FunctionInvocationLayer/FunctionMiddleware""]
    ToolLayer -- "Invoke" --> ToolInstance[""FunctionTool/MCPTool""]
    ToolInstance -- "Result" --> AgentRun
    AgentRun -- "AgentResponse" --> User
```
Sources: `[python/packages/core/agent_framework/_agents.py:1-64]`, `[python/packages/core/agent_framework/_middleware.py:1-50]`, `[python/packages/core/agent_framework/_tools.py:1-50]()`

### Code Entity Space: Skill and Tooling Architecture
This diagram bridges "Capabilities" to specific code entities and their communication protocols, showing how skills compose tools.

```mermaid
graph LR
    subgraph "NaturalLanguageSpace"
        Cap[""TheAgentCanUseALocalPythonScript""]
        SkillCap[""TheAgentHasASpecializedDomainSkill""]
    end

    subgraph "CodeEntitySpace(agent_framework)"
        ToolDec[""At-toolDecorator""] --> FuncTool[""FunctionTool""]
        MCPClient[""MCPToolSubclasses""] -- "JSON-RPC" --> MCPServer[""ExternalMCPServer""]
        SkillSys[""SkillsProvider""] --> SkillObj[""Skill(InlineSkill/FileSkill/ClassSkill)""]
    end

    subgraph "Infrastructure"
        OTel[""ChatTelemetryLayer""] -.-> Tracing[""OpenTelemetrySpans""]
    end

    Cap -.-> ToolDec
    Cap -.-> MCPClient
    SkillCap -.-> SkillSys
    FuncTool -.-> OTel
    SkillObj -.-> FuncTool
```
Sources: `[python/packages/core/agent_framework/_tools.py:1-50]`, `[python/packages/core/agent_framework/observability.py:90-120]()`

---

## Terminology Table

| Term | Description | Relevant Files |
| :--- | :--- | :--- |
| **Content** | Unified model for message parts (text, image, data URIs, hosted files). | `[python/packages/core/agent_framework/_types.py:50-80]()` |
| **StateBag** | A dictionary used to store arbitrary state in .NET sessions. | `[dotnet/src/Microsoft.Agents.AI.Workflows/WorkflowSession.cs:1-20]()` |
| **uv** | Python package and workspace manager used in the monorepo. | `[python/packages/core/agent_framework/_settings.py:1-50]()` |
| **SerializationMixin** | Provides `to_dict` and `from_dict` capabilities to classes. | `[python/packages/core/agent_framework/_serialization.py:1-50]()` |
| **UsageDetails** | Tracks token consumption (input, output, reasoning, cache). | `[python/packages/core/agent_framework/observability.py:120-140]()` |
| **HarnessAgent** | A "batteries-included" agent pattern with pre-configured tools. | `[python/packages/core/agent_framework/_agents.py:1-50]()` |
| **MessageInjectionMiddleware** | Session-scoped middleware that lets tools enqueue messages for the next model call. | `[python/packages/core/agent_framework/_middleware.py:50-80]()` |

Sources: `[python/packages/core/agent_framework/_types.py:50-80]`, `[python/packages/core/agent_framework/_serialization.py:1-50]`, `[python/packages/core/agent_framework/observability.py:120-140]`

---

## Infrastructure and Tooling

### Monorepo Management
* **Python**: Uses `uv` for workspace management and dependency resolution across packages.
* **.NET**: Centralized versioning and package metadata via Directory.Packages.props and MSBuild properties.

Sources: `[dotnet/Directory.Packages.props:1-100]()`

### Observability
The framework integrates OpenTelemetry for tracing, logging, and metrics.
* **Attributes**: Semantic conventions such as `gen_ai.operation.name` and token usage metrics.
* **Buckets**: Standardized boundaries for token usage and operation duration histograms.
* **Telemetry Layers**: Specialized middleware for capturing telemetry spans (`AgentTelemetryLayer`, `ChatTelemetryLayer`).

Sources: `[python/packages/core/agent_framework/observability.py:1-150]()`