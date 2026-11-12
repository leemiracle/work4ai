<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-agents-python · page 4 Tools and Capabilities · fetched 2026-10-26 -->

# Tools and Capabilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/ja/tools.md](docs/ja/tools.md)
- [docs/ko/agents.md](docs/ko/agents.md)
- [docs/ko/guardrails.md](docs/ko/guardrails.md)
- [docs/ko/mcp.md](docs/ko/mcp.md)
- [docs/ko/tools.md](docs/ko/tools.md)
- [docs/ko/voice/quickstart.md](docs/ko/voice/quickstart.md)
- [docs/ref/tool_context.md](docs/ref/tool_context.md)
- [docs/zh/agents.md](docs/zh/agents.md)
- [docs/zh/guardrails.md](docs/zh/guardrails.md)
- [docs/zh/mcp.md](docs/zh/mcp.md)
- [docs/zh/tools.md](docs/zh/tools.md)
- [docs/zh/voice/quickstart.md](docs/zh/voice/quickstart.md)
- [examples/basic/tools.py](examples/basic/tools.py)
- [src/agents/__init__.py](src/agents/__init__.py)
- [src/agents/function_schema.py](src/agents/function_schema.py)
- [src/agents/tool.py](src/agents/tool.py)
- [tests/sandbox/test_session_utils.py](tests/sandbox/test_session_utils.py)
- [tests/test_function_schema.py](tests/test_function_schema.py)
- [tests/test_function_schema_logger_restore.py](tests/test_function_schema_logger_restore.py)
- [tests/test_function_tool.py](tests/test_function_tool.py)
- [tests/test_function_tool_decorator.py](tests/test_function_tool_decorator.py)

</details>



Tools are the primary mechanism for agents to take actions beyond text generation. A tool is a callable capability that the model can invoke to perform operations such as fetching data, executing code, calling external APIs, searching the web, or delegating to other agents [docs/ja/tools.md:5-13](). The SDK provides a unified abstraction layer that supports multiple tool execution strategies while maintaining consistent patterns for approval, error handling, and context management.

This page provides an overview of the tool system architecture, tool categories, execution patterns, and integration mechanisms. Because this is a parent page, keep high-level details here and refer to the child pages for complete specifications:

- For general tool architecture and the `Tool` interface, see [Tool System Overview](#4.1)
- For Python function wrapping and schema inference, see [Function Tools](#4.2)
- For OpenAI-managed capabilities, see [Hosted Tools](#4.3)
- For environment-bound tools, see [Local Runtime Tools](#4.4)
- For nested agent execution, see [Agent as Tool](#4.5)
- For turn termination and repetition rules, see [Tool Use Behavior](#4.6)
- For approval workflows and human-in-the-loop gates, see [Tool Approval and Human-in-the-Loop](#4.7)
- For managing large tool outputs via sliding windows, see [Tool Output Trimmer](#4.8)

For Model Context Protocol integration, see [Model Context Protocol (MCP)](#11). For guardrails that validate tool inputs and outputs, see [Safety and Validation](#6).

---

## Tool Categories and Execution Locations

The SDK organizes tools into primary categories based on where and how they execute [docs/ja/tools.md:7-13](). 

Title: Tool Category Architecture (Natural Language Space to Code Entity Space)
```mermaid
graph TB
    subgraph "Natural_Language_Space"
        NLHosted[""OpenAI-Managed Capabilities"""]
        NLLocal[""Local Environment Execution"""]
        NLFunc[""Python Function Wrappers"""]
        NLAgent[""Nested Agent Workflows"""]
    end
    
    subgraph "Code_Entity_Space"
        HostedModel[""OpenAIResponsesModel""<br/>src/agents/models/openai_responses.py]
        CompTool[""ComputerTool""<br/>src/agents/tool.py]
        ShellTool[""ShellTool""<br/>src/agents/tool.py]
        ApplyPatch[""ApplyPatchTool""<br/>src/agents/tool.py]
        FuncTool[""FunctionTool / @function_tool""<br/>src/agents/tool.py]
        AgentTool[""Agent.as_tool()""<br/>src/agents/agent.py]
    end
    
    NLHosted --> HostedModel
    NLLocal --> CompTool
    NLLocal --> ShellTool
    NLLocal --> ApplyPatch
    NLFunc --> FuncTool
    NLAgent --> AgentTool
```
Sources: [docs/ja/tools.md:7-13](), [src/agents/tool.py:35-45](), [src/agents/agent.py:166-178]()

**Execution Location Matrix**

| Tool Category | Execution Location | SDK Component | Request Round-Trip |
|--------------|-------------------|---------------|-------------------|
| **Hosted Tools** | OpenAI servers | `OpenAIResponsesModel` [src/agents/models/openai_responses.py:]() | Single request (results streaming) |
| **Local Runtime** | Your environment | `ComputerTool`, `ShellTool` [src/agents/tool.py:35-45]() | Request → tool exec → continuation |
| **Function Tools** | Your Python process | `@function_tool`, `FunctionTool` [src/agents/tool.py:35-45]() | Request → tool exec → continuation |
| **Agent as Tool** | Your Python process | `Agent.as_tool()` [src/agents/agent.py:166-178]() | Request → nested run → continuation |
| **MCP Tools** | External MCP servers | `MCPServer` implementations | Request → MCP call → continuation |

Sources: [docs/ja/tools.md:7-28](), [src/agents/tool.py:35-45]()

---

## Tool Registration and Discovery

Tools are registered on agents through direct lists, MCP servers, or implicit handoffs [src/agents/agent.py:166-178](). The resolution logic filters tools based on their `is_enabled` status. For details on discovery mechanisms and tool registration on agents, see [Tool System Overview](#4.1).

Sources: [src/agents/agent.py:166-218](), [tests/test_function_tool.py:43-59]()

---

## Tool Execution Pipeline

Title: Tool Execution Pipeline (Natural Language Space to Code Entity Space)
```mermaid
graph TB
    subgraph "Natural_Language_Space"
        NLIdent[""Identify Tool Calls"""]
        NLApprove[""Check Approvals"""]
        NLExec[""Execute Tool Function"""]
        NLOutput[""Serialize Output"""]
    end
    
    subgraph "Code_Entity_Space"
        ModelResp[""Runner.run() / Runner.run_sync()""<br/>src/agents/run.py]
        ProcessResp[""ProcessedResponse.create()""<br/>src/agents/run_internal/]
        ResolveApprove[""resolve_approval_status()""<br/>src/agents/run_internal/]
        InvokeFunc[""invoke_function_tool()""<br/>src/agents/tool.py]
        ToolInvoke[""FunctionTool.on_invoke_tool()""<br/>src/agents/tool.py]
        Serialize[""ToolCallOutputItem""<br/>src/agents/items.py]
    end
    
    NLIdent --> ModelResp
    ModelResp --> ProcessResp
    NLApprove --> ResolveApprove
    NLExec --> InvokeFunc
    InvokeFunc --> ToolInvoke
    NLOutput --> Serialize
```
Sources: [src/agents/run.py:113-124](), [src/agents/tool.py:734-750](), [src/agents/items.py:56-75]()

The execution pipeline processes tool invocations by parsing model outputs, resolving human-in-the-loop requirements, enforcing timeouts and guardrails, and serializing results back into the session history. For detailed execution steps, see [Tool System Overview](#4.1).

Sources: [src/agents/run_internal/tool_execution.py:1-157](), [src/agents/tool.py:734-775]()

---

## Tool Context and Dependency Injection

The SDK provides context wrappers that pass execution state down to tools [src/agents/run_context.py:108-115]() and inject invocation metadata via `ToolContext` [src/agents/tool_context.py:35-58](). For details, see [Function Tools](#4.2) and [Tool System Overview](#4.1).

Sources: [src/agents/run_context.py:108-115](), [src/agents/tool_context.py:35-58]()

---

## Tool Namespaces and Deferred Loading

Namespaces group related tools under a shared label and description for the OpenAI Responses API **Tool Search** feature [docs/ja/tools.md:94-98](). `defer_loading=True` hides tools from initial schemas until loaded on demand [docs/ja/tools.md:78-91](). For details, see [Function Tools](#4.2) and [Hosted Tools](#4.3).

Sources: [docs/ja/tools.md:65-128](), [src/agents/tool.py:56-62]()

---

## Tool Error Handling

The `failure_error_function` parameter controls exception presentation to models [src/agents/tool.py:196-196](). Uncaught errors or custom failure formatters determine whether an exception propagates or returns an error string. For details, see [Function Tools](#4.2).

Sources: [src/agents/tool.py:196-196](), [src/agents/run_internal/tool_execution.py:79-80](), [tests/test_function_tool.py:136-137]()

---

## Advanced Tool Patterns

- **Agent as Tool**: Expose agents as callable tools via `Agent.as_tool()` [docs/ja/tools.md:26-26](). For details, see [Agent as Tool](#4.5).
- **Tool Timeouts**: Configure execution limits and behavior [src/agents/tool.py:195-195](). For details, see [Function Tools](#4.2).
- **Tool Use Behavior**: Configure termination vs continuation rules using `tool_use_behavior` [docs/ko/agents.md:48-48](). For details, see [Tool Use Behavior](#4.6).
- **Tool Approval**: Require human sign-off via `needs_approval`. For details, see [Tool Approval and Human-in-the-Loop](#4.7).
- **Tool Output Trimmer**: Prune large payloads via sliding window filters. For details, see [Tool Output Trimmer](#4.8).

Sources: [src/agents/tool.py:195-195](), [docs/ja/tools.md:26-26](), [docs/ko/agents.md:48-48]()

---

