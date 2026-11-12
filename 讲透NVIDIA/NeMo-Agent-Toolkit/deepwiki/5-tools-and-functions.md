<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/NeMo-Agent-Toolkit · page 5 Tools and Functions · fetched 2026-10-26 -->

# Tools and Functions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/nvidia_nat_core/src/nat/builder/function_info.py](packages/nvidia_nat_core/src/nat/builder/function_info.py)
- [packages/nvidia_nat_core/tests/nat/builder/test_function_info.py](packages/nvidia_nat_core/tests/nat/builder/test_function_info.py)
- [packages/nvidia_nat_core/tests/nat/builder/test_function_info_future_annotations.py](packages/nvidia_nat_core/tests/nat/builder/test_function_info_future_annotations.py)

</details>



## Purpose and Scope

Tools and functions provide the fundamental execution units that enable agents within the NVIDIA NeMo Agent Toolkit (NAT) to perform actions beyond simple text generation. In the NAT architecture, functions are strongly typed components registered through the global type registry and instantiated via the `Builder` pattern [packages/nvidia_nat_core/src/nat/builder/function.py:58-78](). Agents specify functions by their tool names, and the `Builder` resolves these into framework-wrapped executable entities.

The toolkit provides a robust base class, `FunctionBase`, which handles type generics, Pydantic schema management for inputs/outputs, and type conversion capabilities [packages/nvidia_nat_core/src/nat/builder/function.py:58-78](). Through metadata containers like `FunctionDescriptor` and `FunctionInfo`, the system inspects Python callables—including those utilizing future annotations (`from __future__ import annotations`)—to automatically construct input and output schemas [packages/nvidia_nat_core/src/nat/builder/function_info.py:118-165](), [packages/nvidia_nat_core/tests/nat/builder/test_function_info_future_annotations.py:15-22](). This ensures that when an agent invokes a tool, data is validated and coerced into expected Python types [packages/nvidia_nat_core/src/nat/builder/function.py:105-124]().

This page offers a high-level overview of the lifecycle and usage of tools and functions within workflows. For detailed guidance on specific sub-topics, please refer to the child pages:

*   **Function Registration and Development** ([Function Registration and Development](#5.1)) — Detailed instructions on creating custom functions using `@register_function`, defining function schemas, per-user functions, and managing function groups [packages/nvidia_nat_core/src/nat/plugin_api/__init__.py:53-54]().
*   **Model Context Protocol (MCP) Integration** ([Model Context Protocol (MCP) Integration](#5.2)) — Covers MCP client/server integration, tool discovery, authentication, and bidirectional usage.
*   **MCP Authentication** ([MCP Authentication](#5.3)) — In-depth explanation of OAuth2 flows, service account authentication, token caching, and dual authentication for MCP servers.
*   **Agent-to-Agent Protocol** ([Agent-to-Agent Protocol](#5.4)) — Describes communication protocols for distributed agent teams and inter-agent cooperation.
*   **FastMCP Server** ([FastMCP Server](#5.6)) — Documents how to publish workflows as MCP-native services with FastMCP, including protected server patterns [docs/source/extend/custom-components/mcp-server.md:52-60]().
*   **Text-to-SQL with Vanna** ([Text-to-SQL with Vanna](#5.7)) — Documents the `text2sql` and `execute_db_query` functions powered by Vanna (Note: `nvidia-nat-vanna` was removed in v1.7.0).
*   **Code Execution and Built-in Functions** ([Code Execution and Built-in Functions](#5.8)) — Documents built-in code execution tools [packages/nvidia_nat_langchain/src/nat/plugins/langchain/tools/code_generation_tool.py:28-37]() and internet search integrations (Exa, Wikipedia). Note that Tavily was migrated to a provider-managed plugin (`nemo-agent-toolkit-tavily`) in v1.8.0 [packages/nvidia_nat_langchain/src/nat/plugins/langchain/tools/tavily_internet_search.py:21-29]().
*   **Human-in-the-Loop (HITL)** ([Human-in-the-Loop (HITL)](#5.9)) — Document human-in-the-loop capabilities for gating agent behavior with user approval, utilizing `HITLMiddleware` to present prompts via the `user_interaction_manager` [packages/nvidia_nat_core/src/nat/middleware/hitl/hitl_middleware.py:98-100]().

Sources: [packages/nvidia_nat_core/src/nat/builder/function.py:58-124](), [packages/nvidia_nat_core/src/nat/builder/function_info.py:118-165](), [packages/nvidia_nat_core/tests/nat/builder/test_function_info_future_annotations.py:15-22](), [packages/nvidia_nat_core/src/nat/plugin_api/__init__.py:53-54](), [packages/nvidia_nat_langchain/src/nat/plugins/langchain/tools/tavily_internet_search.py:21-29](), [packages/nvidia_nat_core/src/nat/middleware/hitl/hitl_middleware.py:98-100](), [docs/source/extend/custom-components/mcp-server.md:52-60]()

***

## Tools vs Functions: Terminology and Concepts

In the NAT codebase, the terms **function** and **tool** represent different conceptual layers:

| Concept | Description |
| :--- | :--- |
| **Function** | Low-level implementation unit. NAT uses `Function` [packages/nvidia_nat_core/src/nat/builder/function.py:58]() and its concrete subclasses to manage execution logic, schema generation, and type introspection via `FunctionDescriptor` [packages/nvidia_nat_core/src/nat/builder/function_info.py:118](). |
| **Tool** | Agent-facing interface. Agents reference tools by their names in the configuration, mapping directly to underlying registered functions. |

### Configuration to Runtime Mapping

The `Builder` resolves YAML configuration entries into registered function implementations on startup.

| YAML Configuration Entity | Code Entity | Runtime Representation |
| :--- | :--- | :--- |
| `functions.categorizer._type: categorizer` | `FunctionBaseConfig` subclass [packages/nvidia_nat_core/src/nat/data_models/function.py:35]() | `FunctionInfo` wrapper [packages/nvidia_nat_core/src/nat/builder/function_info.py:118]() |
| `functions.hw_check._type: hardware_check` | `FunctionBaseConfig` subclass [packages/nvidia_nat_core/src/nat/data_models/function.py:35]() | `Function` instance [packages/nvidia_nat_core/src/nat/builder/function.py:58]() |
| `workflow.tool_names: [categorizer]` | `FunctionRef` [packages/nvidia_nat_core/src/nat/data_models/component_ref.py:30]() | `LambdaFunction` or `Function` |

Sources: [packages/nvidia_nat_core/src/nat/builder/function.py:58-82](), [packages/nvidia_nat_core/src/nat/builder/function_info.py:118-210](), [packages/nvidia_nat_core/src/nat/data_models/function.py:35](), [packages/nvidia_nat_core/src/nat/data_models/component_ref.py:30]()

***

## Function Registration and Development

Custom functions are developed using Python type annotations and registered via the `@register_function` decorator [packages/nvidia_nat_core/src/nat/plugin_api/__init__.py:53-54](). The toolkit inspects signatures using `FunctionDescriptor` and `FunctionInfo` to automatically generate Pydantic schemas for inputs and outputs [packages/nvidia_nat_core/src/nat/builder/function_info.py:118-165](). Support for future annotations (`from __future__ import annotations`) ensures string-based type hints are correctly resolved against module namespaces at runtime [packages/nvidia_nat_core/tests/nat/builder/test_function_info_future_annotations.py:15-22]().

For detailed instructions on creating custom functions, per-user functions, and function groups, see [Function Registration and Development](#5.1).

### Registration Flow Diagram: Natural Language to Code Entity Mapping

This diagram illustrates how a developer's intent maps to specific code entities during function registration.

Title: Function Registration Mapping
```mermaid
graph TD
    subgraph NaturalLanguageSpace[""NaturalLanguageSpace""]
        Intent[""I want to register a custom data processing tool""]
    end

    subgraph CodeEntitySpace[""CodeEntitySpace""]
        YAML[""YAML config: functions.processor._type = 'data_processor'""]
        Config[""nat.data_models.function.FunctionBaseConfig subclass""]
        Decorator[""nat.plugin_api.register_function""]
        Impl[""async def data_processor_tool(config, builder)""]
        Info[""nat.builder.function_info.FunctionInfo""]
        Agent[""Agent invokes via tool_names processor""]
    end

    Intent --> YAML
    YAML --> Config
    Config --> Decorator
    Decorator --> Impl
    Impl --> Info
    Info --> Agent
```

Sources: [packages/nvidia_nat_core/src/nat/builder/function.py:58-124](), [packages/nvidia_nat_core/src/nat/builder/function_info.py:118-210](), [packages/nvidia_nat_core/src/nat/plugin_api/__init__.py:53](), [packages/nvidia_nat_core/tests/nat/builder/test_function_info_future_annotations.py:15-22]()

***

## Model Context Protocol (MCP) Integration & Authentication

NAT integrates with the Model Context Protocol (MCP) to allow agents to discover and execute tools hosted remotely or locally on MCP servers. The integration covers bidirectional usage, tool discovery, and seamless client-server communication. Additionally, secure production deployments require robust authentication mechanisms including OAuth2 flows, service account patterns, and token caching.

For comprehensive details on MCP client/server integration, see [Model Context Protocol (MCP) Integration](#5.2). For details on OAuth2 and token management, see [MCP Authentication](#5.3).

Sources: [packages/nvidia_nat_core/src/nat/builder/function.py:58-78]()

***

## Agent-to-Agent Protocol

The Agent-to-Agent (A2A) protocol enables distributed agent teams to communicate, delegate subtasks, and share context across network boundaries. This facilitates modular multi-agent architectures where specialized agents act as tools or peers for other workflows.

For architectural specifics and implementation patterns, see [Agent-to-Agent Protocol](#5.4).

Sources: [packages/nvidia_nat_core/src/nat/builder/function.py:58-78]()

***

## FastMCP Server

Workflows and functions created within NAT can be published as MCP-native services using FastMCP. This allows any standard MCP client to interact with NAT workflows out-of-the-box, supporting protected server configurations and streaming responses.

For instructions on publishing NAT workflows as FastMCP services, see [FastMCP Server](#5.6).

Sources: [docs/source/extend/custom-components/mcp-server.md:52-60]()

***

## Text-to-SQL with Vanna

NAT supports natural language to SQL generation and execution via integrated database tools powered by the Vanna framework, exposing `text2sql` and `execute_db_query` functions. Note that the legacy `nvidia-nat-vanna` package was removed in v1.7.0 in favor of core integrations.

For setup and query execution details, see [Text-to-SQL with Vanna](#5.7).

Sources: [packages/nvidia_nat_core/src/nat/builder/function.py:58-78]()

***

## Code Execution and Built-in Functions

Pre-built functions such as code execution tools [packages/nvidia_nat_langchain/src/nat/plugins/langchain/tools/code_generation_tool.py:28-37]() and internet search integrations (such as Exa and Wikipedia) are available out of the box. Note that third-party search tools like Tavily have been modularized into provider-managed plugins (`nemo-agent-toolkit-tavily`) as of v1.8.0 [packages/nvidia_nat_langchain/src/nat/plugins/langchain/tools/tavily_internet_search.py:21-29]().

For a full catalog of built-in functions and execution environments, see [Code Execution and Built-in Functions](#5.8).

Sources: [packages/nvidia_nat_langchain/src/nat/plugins/langchain/tools/code_generation_tool.py:28-37](), [packages/nvidia_nat_langchain/src/nat/plugins/langchain/tools/tavily_internet_search.py:21-29]()

***

## Human-in-the-Loop (HITL)

Human-in-the-Loop (HITL) capabilities allow workflows to pause execution and request user approval or input before proceeding with sensitive tool calls. This is implemented via `HITLMiddleware` which intercepts function invocations and presents prompts through the `user_interaction_manager` [packages/nvidia_nat_core/src/nat/middleware/hitl/hitl_middleware.py:98-100]().

For configuration patterns and WebSocket-based interaction details, see [Human-in-the-Loop (HITL)](#5.9).

### Execution Path: HITL Code Entity Mapping

Title: HITL Execution Path Mapping
```mermaid
graph LR
    subgraph NaturalLanguageSpace[""NaturalLanguageSpace""]
        UserReq[""Require human verification before running tool invocation""]
    end

    subgraph CodeEntitySpace[""CodeEntitySpace""]
        Base[""nat.builder.function.Function.ainvoke""]
        Chain[""nat.middleware.middleware.InvocationContext""]
        HITL[""nat.middleware.hitl.hitl_middleware.HITLMiddleware""]
        UserInt[""nat.builder.context.Context.get().user_interaction_manager""]
        Impl[""ConcreteFunction._ainvoke""]
    end

    UserReq --> Base
    Base --> Chain
    Chain --> HITL
    HITL --> UserInt
    UserInt --> Impl
```

Sources: [packages/nvidia_nat_core/src/nat/middleware/hitl/hitl_middleware.py:29-118]()

***

## Summary of Core Tool Components

| Component | Purpose | Source |
| :--- | :--- | :--- |
| **Function** | Base class for concrete function implementations with middleware support | [packages/nvidia_nat_core/src/nat/builder/function.py:58]() |
| **FunctionDescriptor** | Metadata descriptor for inspecting callables and synthesizing schemas | [packages/nvidia_nat_core/src/nat/builder/function_info.py:118]() |
| **FunctionInfo** | Metadata container for registering functions (description, converters) | [packages/nvidia_nat_core/src/nat/builder/function_info.py:118]() |
| **FunctionMiddleware** | Interceptor for function calls (pre/post-invoke) | [packages/nvidia_nat_core/src/nat/middleware/function_middleware.py:45]() |
| **HITLMiddleware** | Specialized middleware for Human-in-the-Loop prompting | [packages/nvidia_nat_core/src/nat/middleware/hitl/hitl_middleware.py:29]() |
| **HumanPrompt** | Union type for various user interaction prompts (Text, Binary, etc.) | [packages/nvidia_nat_core/src/nat/data_models/interactive.py:17]() |
| **FunctionBaseConfig** | Pydantic base for function configuration in YAML | [packages/nvidia_nat_core/src/nat/data_models/function.py:35]() |

Sources:
*   [packages/nvidia_nat_core/src/nat/builder/function.py:58]()
*   [packages/nvidia_nat_core/src/nat/builder/function_info.py:118]()
*   [packages/nvidia_nat_core/src/nat/middleware/hitl/hitl_middleware.py:29]()
*   [packages/nvidia_nat_core/src/nat/data_models/function.py:35]()
*   [packages/nvidia_nat_core/src/nat/plugin_api/__init__.py:82-91]()

---

