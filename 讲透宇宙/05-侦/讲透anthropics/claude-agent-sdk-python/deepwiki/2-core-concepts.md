<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/claude-agent-sdk-python · page 2 Core Concepts · fetched 2026-10-26 -->

# Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/claude_agent_sdk/types.py](src/claude_agent_sdk/types.py)

</details>



This section serves as the parent container for foundational architectural and conceptual material in the `claude-agent-sdk-python` repository. It covers the high-level design principles, type contracts, configuration options, and binary lifecycle management that govern how the SDK communicates with the bundled Claude Code CLI.

Since this is a parent overview page, high-level summaries are provided below. For comprehensive technical deep dives, refer to the child pages:
- **[Architecture Overview](#2.1)** — Layered architecture covering user code, the public API, the `Query` control layer, `SubprocessCLITransport`, the bundled Claude CLI binary, and the Anthropic API.
- **[Type System and Message Architecture](#2.2)** — Type hierarchy definitions in `types.py`, including the `Message` union, `ContentBlock` subtypes, and `SDKControl` request/response variants.
- **[ClaudeAgentOptions Configuration Reference](#2.3)** — Comprehensive reference for every field of `ClaudeAgentOptions`.
- **[Bundled CLI Version Management](#2.4)** — The role of `_cli_version.py`, release-time updates, `MINIMUM_CLAUDE_CODE_VERSION` checks, and the `cli_path` override.

---

## 1. Architecture Overview and Layered Design

The SDK is organized into three distinct layers that separate concerns between user-facing abstractions, internal protocol control, and process transport.

### System Mapping: Natural Language Space to Code Entity Space

```mermaid
graph TB
    subgraph "Public API Layer"
        query[""query() function (src/claude_agent_sdk/__init__.py)""]
        Client[""ClaudeSDKClient (src/claude_agent_sdk/client.py)""]
        Options[""ClaudeAgentOptions (src/claude_agent_sdk/types.py)""]
        Decorators["@tool decorator create_sdk_mcp_server (src/claude_agent_sdk/__init__.py)"]
    end
    
    subgraph "Internal Implementation Layer"
        QueryProtocol[""Query (src/claude_agent_sdk/_internal/query.py)""]
        Transport[""SubprocessCLITransport (src/claude_agent_sdk/_internal/transport/subprocess_cli.py)""]
        Parser[""parse_message (src/claude_agent_sdk/_internal/message_parser.py)""]
    end
    
    subgraph "External Dependencies"
        CLI["Claude Code CLI (bundled binary)"]
        API["Anthropic API"]
        MCP["External MCP Servers"]
    end
    
    query --> QueryProtocol
    Client --> QueryProtocol
    Options --> QueryProtocol
    Options --> Transport
    Decorators --> MCP
    
    QueryProtocol --> Transport
    QueryProtocol --> Parser
    Transport --> CLI
    CLI --> API
    CLI --> MCP
```

For details, see [Architecture Overview](#2.1).

Sources: `[src/claude_agent_sdk/_internal/transport/subprocess_cli.py:40-673]()`, `[src/claude_agent_sdk/_internal/query.py:53-626]`, `[src/claude_agent_sdk/client.py:14-404]()`, `[src/claude_agent_sdk/__init__.py:47-155]()`

---

## 2. Communication Modes and Control Protocol

The SDK supports two primary interaction patterns: one-shot execution via `query()` and bidirectional stateful communication via `ClaudeSDKClient`.

### Communication Modes: Natural Language Space to Code Entity Space

```mermaid
graph LR
    subgraph "One-Shot Mode"
        Q1[""query(prompt: str) in __init__.py""]
        Q2[""SubprocessCLITransport --print flag""]
        Q3["CLI process exits"]
        Q1 --> Q2 --> Q3
    end
    
    subgraph "Bidirectional Mode"
        C1[""ClaudeSDKClient.connect() in client.py""]
        C2[""SubprocessCLITransport stream-json""]
        C3[""Query.initialize() in query.py""]
        C4["Bidirectional Control Protocol"]
        C1 --> C2 --> C3 --> C4
    end
```

For details on the bidirectional control protocol, request correlation, task lifecycle tracking, and stream buffering, see [Architecture Overview](#2.1).

Sources: `[src/claude_agent_sdk/_internal/transport/subprocess_cli.py:329-335]()`, `[src/claude_agent_sdk/client.py:87-169]()`, `[src/claude_agent_sdk/_internal/query.py:116-158]()`

---

## 3. Type System and Message Architecture

The SDK relies on a rigorous type hierarchy defined in `src/claude_agent_sdk/types.py`. This module acts as the formal contract between user code, internal parsing logic, and the Claude CLI protocol messages. It defines core unions like `Message`, rich `ContentBlock` subtypes, system prompt structures (`SystemPromptPreset`, `SystemPromptCustom`, `SystemPromptFile`), and permission control types (`PermissionUpdate`, `PermissionRuleValue`).

For details, see [Type System and Message Architecture](#2.2).

Sources: `[src/claude_agent_sdk/types.py:1-2901]()`

---

## 4. Configuration and CLI Version Management

Configuration is handled uniformly via `ClaudeAgentOptions`, which exposes parameters for tools, MCP servers, lifecycle hooks, permission modes, and sandboxing. Concurrently, the SDK manages the bundled Claude CLI binary via `_cli_version.py`, enforcing runtime compatibility checks (`MINIMUM_CLAUDE_CODE_VERSION`) while allowing user overrides through `cli_path`.

For details on configuration fields, see [ClaudeAgentOptions Configuration Reference](#2.3). For details on binary version constraints and compatibility checks, see [Bundled CLI Version Management](#2.4).

Sources: `[src/claude_agent_sdk/types.py:465-574]()`, `[src/claude_agent_sdk/_cli_version.py:1-3]()`

---

