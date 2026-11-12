<!-- source: DeepWiki mcp.deepwiki.com · repo NousResearch/hermes-agent · page 5 Tool System · fetched 2026-10-30 -->

# Tool System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/tool_dispatch_helpers.py](agent/tool_dispatch_helpers.py)
- [agent/tool_executor.py](agent/tool_executor.py)
- [model_tools.py](model_tools.py)
- [tests/agent/test_tool_dispatch_helpers.py](tests/agent/test_tool_dispatch_helpers.py)
- [tests/tools/test_completed_process_results.py](tests/tools/test_completed_process_results.py)
- [tests/tools/test_process_wait_auto_notify.py](tests/tools/test_process_wait_auto_notify.py)
- [tools/__init__.py](tools/__init__.py)
- [tools/process_registry_results.py](tools/process_registry_results.py)
- [tools/process_registry_wait_policy.py](tools/process_registry_wait_policy.py)
- [toolsets.py](toolsets.py)
- [website/docs/developer-guide/adding-tools.md](website/docs/developer-guide/adding-tools.md)
- [website/docs/developer-guide/tools-runtime.md](website/docs/developer-guide/tools-runtime.md)
- [website/docs/integrations/index.md](website/docs/integrations/index.md)
- [website/docs/reference/tools-reference.md](website/docs/reference/tools-reference.md)
- [website/docs/reference/toolsets-reference.md](website/docs/reference/toolsets-reference.md)
- [website/docs/user-guide/features/overview.md](website/docs/user-guide/features/overview.md)
- [website/docs/user-guide/features/tools.md](website/docs/user-guide/features/tools.md)
- [website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/developer-guide/tools-runtime.md](website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/developer-guide/tools-runtime.md)
- [website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/reference/tools-reference.md](website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/reference/tools-reference.md)
- [website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/reference/toolsets-reference.md](website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/reference/toolsets-reference.md)
- [website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/user-guide/features/browser.md](website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/user-guide/features/browser.md)
- [website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/user-guide/features/tools.md](website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/user-guide/features/tools.md)

</details>



The tool system provides the Hermes Agent with its action capabilities through a structured function-calling architecture. This page introduces the high-level framework of the tool registry, how toolsets are composed and managed, and how tool discovery and execution flow through the system.

Specific technical details about individual tool categories and implementations are delegated to child pages, linked below. This parent page provides the architectural context and explains the integration among major components involved in the Hermes tool system.

Sources: [model_tools.py:1-7]()

---

## Architecture Overview

The Hermes Agent leverages a **centralized registry pattern** for tools, where each tool module self-registers its schema, handler, and availability check function at module import time [model_tools.py:150-150]().

- The **tool registry singleton** (`registry`) holds metadata and handlers, serving as the definitive source of available tools in the system [model_tools.py:21-22]().
- The `model_tools.py` module orchestrates tool discovery by importing all tool modules, then provides the public API for retrieving tool schemas and handling function calls [model_tools.py:1-7]().
- Toolsets declared in `toolsets.py` group tools by use case or scenario, defining core tool pools like `_HERMES_CORE_TOOLS` [toolsets.py:11-36]().
- MCP (Model Context Protocol) servers provide dynamically registered external tools integrated into the same registry [website/docs/integrations/index.md:24-26]().

For details on toolset composition and platform-specific configurations, see [Tool Registry and Toolsets](#5.1).

Sources: [model_tools.py:1-7](), [model_tools.py:21-22](), [model_tools.py:150-150](), [toolsets.py:11-36](), [website/docs/integrations/index.md:24-26]()

---

## Tool Registration and Discovery

Each tool registers itself by calling `registry.register()` at module load time [model_tools.py:150-150](). Tool discovery scans candidate modules in `tools/` using `discover_builtin_tools()` [model_tools.py:150-150]() and leverages a persistent cache to memoize AST registrations [model_tools.py:21-22](). Schema sanitization ensures strict backend compatibility.

For details, see [Tool Registry and Toolsets](#5.1).

```mermaid
%% Title: "Tool Discovery Sequence"
sequenceDiagram
    participant Startup as "hermes_cli/cli.py"
    participant ModelTools as "model_tools.py"
    participant RegistryMod as "tools/registry.py"
    participant ToolModule as "tools/*.py"
    participant Registry as "tools.registry.registry"

    Startup->>ModelTools: "import model_tools"
    ModelTools->>RegistryMod: "discover_builtin_tools()"

    loop "for each tool .py file"
        RegistryMod->>ToolModule: "import module"
        ToolModule->>Registry: "registry.register()"
        Registry->>Registry: "add ToolEntry to _tools dict"
    end
```
Sources: [model_tools.py:21-22](), [model_tools.py:150-150]()

---

## Tool Dispatch and Execution

Tool execution bridges LLM function calls to registered handlers. The `agent/tool_executor.py` module handles sequential and concurrent dispatch of tool calls [agent/tool_executor.py:1-7](). Security guards protect execution via mechanisms like dangerous command detection and self-repo guards [agent/tool_executor.py:90-93]().

```mermaid
%% Title: "Tool Dispatch Flow bridging Natural Language Space to Code Entity Space"
graph TB
    subgraph NaturalLanguageSpace["Natural Language Space"]
        UserReq["User_Input"]
        LLM["LLM_generates_tool_calls"]
    end

    subgraph CodeEntitySpace["Code Entity Space"]
        AgentLoop["AIAgent.chat_loop()"]
        ToolExecutor["agent/tool_executor.py: _execute_tool_calls()"]
        ModelTools["model_tools.py: handle_function_call()"]
        Registry["tools.registry.registry"]
        AsyncBridge["model_tools.py: _run_async()"]
        Handler["tools/terminal_tool.py: terminal_tool()"]
    end

    UserReq --> LLM
    LLM --> AgentLoop
    AgentLoop --> ToolExecutor
    ToolExecutor --> ModelTools
    ModelTools --> Registry
    Registry --> Handler
    Handler -. "async" .-> AsyncBridge
    AsyncBridge --> Result["Return_JSON_string"]
    Result --> ToolExecutor
    ToolExecutor --> AgentLoop
```
Sources: [agent/tool_executor.py:1-7](), [agent/tool_executor.py:90-93](), [model_tools.py:1-7](), [model_tools.py:94-146]()

---

## Toolsets and Sub-Topics

Tools are categorized into functional toolsets and specialized execution domains, detailed in the child pages:

- [Tool Registry and Toolsets](#5.1) — Registration, schema sanitization, tool search/deferral [model_tools.py:21-22]().
- [Terminal and File Operations](#5.2) — Terminal execution, file read/write/patch, fuzzy matching, and safety guards [website/docs/user-guide/features/tools.md:29-29]().
- [Process Management](#5.3) — Background process spawning, process registry, and execution kernels [tests/tools/test_completed_process_results.py:18-20]().
- [Security and Command Approval](#5.4) — Dangerous command detection, Tirith integration, self-repo guards, and allowlists [agent/tool_dispatch_helpers.py:25-26]().
- [Web, Browser, and Vision Tools](#5.5) — Web search/extract, browser automation, vision analysis, and video processing [website/docs/user-guide/features/tools.md:27-27]().
- [Code Execution and MCP Tools](#5.6) — `execute_code` sandbox, MCP server integration and transports [website/docs/user-guide/features/tools.md:32-32]().
- [Subagent Delegation](#5.7) — `delegate_task` tool, async subagent spawning, and iteration budget sharing [website/docs/user-guide/features/tools.md:32-32]().
- [Other Tools](#5.8) — Memory tools, todo management, image/video generation, skill management [website/docs/user-guide/features/tools.md:31-31](), and computer use [toolsets.py:93-98]().

```mermaid
%% Title: "Toolset and Tool Code Entity Mapping bridging Natural Language Space to Code Entity Space"
graph TD
    subgraph NaturalLanguageSpace["Natural Language Space"]
        UserGoal["User_Request_For_Tools"]
    end

    subgraph CodeEntitySpace["Code Entity Space"]
        ToolsetTerminal["toolsets.py: TOOLSETS.terminal"]
        ToolsetFile["toolsets.py: TOOLSETS.file"]
        Registry["tools.registry.registry"]
        TerminalTool["tools.terminal_tool.terminal_tool()"]
        FileTools["tools.file_tools.read_file_tool()"]
    end

    UserGoal --> ToolsetTerminal
    UserGoal --> ToolsetFile
    ToolsetTerminal --> Registry
    ToolsetFile --> Registry
    Registry --> TerminalTool
    Registry --> FileTools
```
Sources: [toolsets.py:99-100](), [toolsets.py:119-123](), [website/docs/user-guide/features/tools.md:27-32]()

---

## Related Child Pages

For detailed technical documentation and implementation specifics, see the following child pages:

- [Tool Registry and Toolsets](#5.1) — Tool registration, discovery, and platform-specific configurations.
- [Terminal and File Operations](#5.2) — Terminal execution and semantic file tools.
- [Process Management](#5.3) — Background process spawning and lifecycle management.
- [Security and Command Approval](#5.4) — Dangerous command detection and approval callbacks.
- [Web, Browser, and Vision Tools](#5.5) — Web search, browser automation, and multimodal analysis.
- [Code Execution and MCP Tools](#5.6) — Python sandbox and MCP server integration.
- [Subagent Delegation](#5.7) — Subagent spawning and iteration budget sharing.
- [Other Tools](#5.8) — Memory, image/video generation, and computer use.

Sources: [model_tools.py:1-7]()

---

