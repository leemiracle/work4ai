<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/DeepCode · page 9 Integrations · fetched 2026-11-09 -->

# Integrations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/mcp/models.py](core/mcp/models.py)
- [core/mcp/runtime.py](core/mcp/runtime.py)
- [core/plugins/mcp.py](core/plugins/mcp.py)
- [docs/LOCAL_PLUGINS.md](docs/LOCAL_PLUGINS.md)
- [tests/test_mcp_runtime_lazy.py](tests/test_mcp_runtime_lazy.py)
- [tests/test_plugins.py](tests/test_plugins.py)

</details>



This page provides a high-level overview of how DeepCode integrates with external systems and tool ecosystems, specifically through the Model Context Protocol (MCP), OpenSpace multi-agent environments, and the Agent Plugins 1.0 packaging specification.

DeepCode acts as both an MCP client—consuming tools from local and remote servers—and a platform capable of loading extension packages via local plugin registries. For detailed implementation mechanics, refer to the child pages linked below.

## MCP Server Integration

DeepCode uses the Model Context Protocol (MCP) as its core interoperability layer for external tools and capabilities. The subsystem is anchored by `McpSessionRuntime` in `core/mcp/runtime.py`, which materializes an immutable `McpRuntimePlan` into the agent's `ToolRegistry` [core/mcp/runtime.py:98-112]().

Key architectural highlights include:
- **Transport Flexibility**: Native support for `stdio`, Server-Sent Events (`sse`), and `streamableHttp` transports configured via `McpServerDefinition` [core/mcp/models.py:111]().
- **Lazy Activation**: Support for deferred loading (`deferLoading`), where servers are kept dormant until explicitly brought online during a session via `_ActivateMcpServerTool` [core/mcp/runtime.py:30-43](), [core/mcp/runtime.py:184-188]().
- **Credential Referencing**: Secure injection of secrets using `McpCredentialRef`, tying runtime environment variables to user-managed provider connections without exposing plain text in configuration files [core/mcp/models.py:65-74]().

For detailed configuration guides, CLI commands (`deepcode mcp`), and TUI management (`/mcp`), see [MCP Server Integration](#9.1).

**Diagram: MCP Runtime and Tool Registry Bridge**

```mermaid
graph TD
    subgraph "core/agent_runtime/tools/registry.py"
        "ToolReg"["ToolRegistry"]
    end

    subgraph "core/mcp/runtime.py"
        "Plan"["McpRuntimePlan"]
        "Conn"["McpConnection"]
        "ActTool"["_ActivateMcpServerTool"]
        "Runtime"["McpSessionRuntime"]
    end

    "Plan" -->|"ensure_started()"| "Runtime"
    "Runtime" -->|"spawns"| "Conn"
    "Conn" -->|"register_tools()"| "ToolReg"
    "ActTool" -->|"execute()"| "Conn"
    "ToolReg" -->|"invokes"| "ActTool"
```

Sources: [core/mcp/runtime.py:30-43](), [core/mcp/runtime.py:98-112](), [core/mcp/runtime.py:175-183]()

## OpenSpace and Local Plugins

DeepCode supports participation in distributed multi-agent workflows through OpenSpace integration and local plugin architectures. OpenSpace relies on `openspace-mcp` servers along with workspace-relative path substitution (`${workspace}`) to coordinate tasks across agents.

Complementing this, the Agent Plugins 1.0 specification allows users to bundle Skills and MCP servers into unified local packages. The parser function `load_agent_plugin_mcp` in `core/plugins/mcp.py` validates `mcp.json` components securely [core/plugins/mcp.py:79-82](), while `LocalPluginHost` manages local plugin lifecycles.

For detailed information on plugin packaging, version pinning, and OpenSpace delegation skills, see [OpenSpace and Local Plugins](#9.2).

**Diagram: Local Plugin and MCP Component Parsing**

```mermaid
graph LR
    subgraph "core/plugins/mcp.py"
        "LoadMcp"["load_agent_plugin_mcp()"]
        "CheckCred"["_credential_diagnostics()"]
    end

    subgraph "core/plugins/host.py"
        "PluginHost"["LocalPluginHost"]
    end

    subgraph "core/mcp/runtime.py"
        "SessionRuntime"["McpSessionRuntime"]
    end

    "PluginHost" -->|"reads mcp.json"| "LoadMcp"
    "LoadMcp" -->|"emits diagnostics"| "CheckCred"
    "LoadMcp" -->|"contributes servers"| "SessionRuntime"
```

Sources: [core/plugins/mcp.py:79-82](), [core/plugins/mcp.py:152-161]()

---

