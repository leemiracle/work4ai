<!-- source: DeepWiki mcp.deepwiki.com · repo sst/opencode · page 5 Tool System · fetched 2026-10-26 -->

# Tool System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/opencode/src/tool/apply_patch.ts](packages/opencode/src/tool/apply_patch.ts)
- [packages/opencode/src/tool/apply_patch.txt](packages/opencode/src/tool/apply_patch.txt)
- [packages/opencode/src/tool/edit.ts](packages/opencode/src/tool/edit.ts)
- [packages/opencode/src/tool/external-directory.ts](packages/opencode/src/tool/external-directory.ts)
- [packages/opencode/src/tool/glob.ts](packages/opencode/src/tool/glob.ts)
- [packages/opencode/src/tool/grep.ts](packages/opencode/src/tool/grep.ts)
- [packages/opencode/src/tool/lsp.ts](packages/opencode/src/tool/lsp.ts)
- [packages/opencode/src/tool/read.ts](packages/opencode/src/tool/read.ts)
- [packages/opencode/src/tool/skill.ts](packages/opencode/src/tool/skill.ts)
- [packages/opencode/src/tool/task.ts](packages/opencode/src/tool/task.ts)
- [packages/opencode/src/tool/tool.ts](packages/opencode/src/tool/tool.ts)
- [packages/opencode/src/tool/write.ts](packages/opencode/src/tool/write.ts)
- [packages/opencode/test/tool/apply_patch.test.ts](packages/opencode/test/tool/apply_patch.test.ts)
- [packages/opencode/test/tool/edit.test.ts](packages/opencode/test/tool/edit.test.ts)
- [packages/opencode/test/tool/external-directory.test.ts](packages/opencode/test/tool/external-directory.test.ts)
- [packages/opencode/test/tool/glob.test.ts](packages/opencode/test/tool/glob.test.ts)
- [packages/opencode/test/tool/grep.test.ts](packages/opencode/test/tool/grep.test.ts)
- [packages/opencode/test/tool/question.test.ts](packages/opencode/test/tool/question.test.ts)
- [packages/opencode/test/tool/read.test.ts](packages/opencode/test/tool/read.test.ts)
- [packages/opencode/test/tool/skill.test.ts](packages/opencode/test/tool/skill.test.ts)
- [packages/opencode/test/tool/task.test.ts](packages/opencode/test/tool/task.test.ts)
- [packages/opencode/test/tool/tool-define.test.ts](packages/opencode/test/tool/tool-define.test.ts)
- [packages/opencode/test/tool/write.test.ts](packages/opencode/test/tool/write.test.ts)

</details>



The Tool System enables AI agents to interact with the development environment through a standardized interface for file operations, shell commands, web searches, and language server protocol (LSP) queries. This system provides the "hands" for OpenCode's agents, allowing them to bridge the gap between natural language reasoning and concrete code manipulation.

For information about how tools are configured and restricted per agent, see [Agent System](#3.2). For details on permission evaluation and user-in-the-loop approval, see [Permission System](#5.2).

## Tool Architecture

Tools are defined using the `Tool.define()` function [packages/opencode/src/tool/tool.ts:151-169](), which accepts an ID and an initialization function that returns tool metadata and an execution handler. The `ToolRegistry` manages the lifecycle and availability of these tools, providing them to the agent processing loop based on the current model and agent configuration.

**Natural Language to Code Entity Mapping**

The following diagram shows how high-level tool concepts map to specific classes and functions in the codebase.

```mermaid
graph TB
    subgraph "Natural Language Space"
        ["Agent Intent (e.g. 'read file')"]
        ["Parameter Constraints (Schema.Struct)"]
    end

    subgraph "Code Entity Space"
        ToolDefine["Tool.define()"]
        ToolInfo["Tool.Info interface"]
        ToolExecute["tool.execute()"]
        Params["Parameters (Schema.Struct)"]
        Result["ExecuteResult interface"]
    end

    ["Agent Intent (e.g. 'read file')"] -- "Resolved by Agent" --> ToolDefine
    ToolDefine -- "Implements" --> ToolInfo
    ToolInfo -- "Validates with" --> Params
    ToolInfo -- "Runs" --> ToolExecute
    ToolExecute -- "Returns" --> Result
    ["Parameter Constraints (Schema.Struct)"] -- "Mapped to" --> Params
```
Sources: [packages/opencode/src/tool/tool.ts:24-65](), [packages/opencode/src/tool/read.ts:28-36](), [packages/opencode/src/tool/tool.ts:151-169]()

### Execution Flow

When an agent invokes a tool, the system follows a strict lifecycle of validation, permission checking, and execution. The system also handles automatic truncation of large outputs to stay within LLM context limits using the `Truncate` service [packages/opencode/src/tool/tool.ts:161-164]().

**Natural Language Execution Mapping**

```mermaid
graph TB
    subgraph "Natural Language Space"
        ["LLM Tool Call Request"]
        ["Tool Arguments JSON"]
    end

    subgraph "Code Entity Space"
        Decode["Schema.decodeUnknownEffect"]
        InvalidArgs["InvalidArgumentsError"]
        Ask["ctx.ask()"]
        Execute["tool.execute()"]
        Truncate["Truncate.Service"]
    end

    ["LLM Tool Call Request"] --> Decode
    ["Tool Arguments JSON"] --> Decode
    Decode -- "Failure" --> InvalidArgs
    Decode -- "Success" --> Ask
    Ask -- "Permission Check" --> Execute
    Execute --> Truncate
```
Sources: [packages/opencode/src/tool/tool.ts:24-34](), [packages/opencode/src/tool/tool.ts:111-145]()

For details on tool definitions, execution lifecycle, parameter schemas, and result handling, see [Tool Architecture](#5.1).

## Permission System

Security is managed via a capability-based permission system. Tools must explicitly call `ctx.ask()` [packages/opencode/src/tool/task.ts:120-129]() before performing sensitive operations.

- **Interactive Approval**: Users can approve or deny individual tool calls in the UI via the `Permission` service.
- **Pattern Matching**: Permissions are evaluated against file patterns or command strings [packages/opencode/test/tool/read.test.ts:172-185]().
- **External Directory Checks**: Tools accessing files outside the project root must pass `assertExternalDirectoryEffect` [packages/opencode/src/tool/external-directory.ts:1-16]().
- **Doom Loop Detection**: The session runner monitors for repeated tool failures to prevent "doom loops".

For documentation on permission rules, allow/deny patterns, doom loop detection, and interactive approval, see [Permission System](#5.2).

Sources: [packages/opencode/src/tool/task.ts:120-129](), [packages/opencode/test/tool/read.test.ts:172-185]()

## Built-in Tools Reference

OpenCode includes a comprehensive suite of built-in tools for common development tasks, registered in the tool registry.

| Tool | ID | Purpose | Key File |
|------|-----|---------|----------|
| **Read** | `read` | Read files/directories with line limits | [packages/opencode/src/tool/read.ts:64-70]() |
| **Write** | `write` | Create/Overwrite files | [packages/opencode/src/tool/write.ts:1-1]() |
| **Edit** | `edit` | Precise string-replacement (old/new) | [packages/opencode/src/tool/edit.ts:58-60]() |
| **Apply Patch** | `apply_patch` | Apply complex multi-file diffs/hunks | [packages/opencode/src/tool/apply_patch.ts:22-24]() |
| **Task** | `task` | Spawn sub-agent sessions (sync/async) | [packages/opencode/src/tool/task.ts:81-83]() |
| **Grep** | `grep` | Search file contents using regex | [packages/opencode/src/tool/grep.ts:20-22]() |
| **Glob** | `glob` | Find files matching patterns | [packages/opencode/src/tool/glob.ts:1-1]() |
| **Skill** | `skill` | Load reusable agent patterns | [packages/opencode/src/tool/skill.ts:12-14]() |
| **LSP** | `lsp` | Language server queries (hover, definition) | [packages/opencode/src/tool/lsp.ts:1-1]() |

### File Operations
Tools like `read` [packages/opencode/src/tool/read.ts:137-180]() and `edit` [packages/opencode/src/tool/edit.ts:88-173]() handle filesystem interaction. The `read` tool includes logic to detect binary files and handle large file truncation.

### Sub-Agent Tasks
The `TaskTool` [packages/opencode/src/tool/task.ts:81-83]() allows an agent to delegate complex sub-tasks to specialized agents. It supports background execution [packages/opencode/src/tool/task.ts:97-102]() and creates child sessions with inherited or restricted permissions [packages/opencode/src/tool/task.ts:139-155]().

For reference documentation for all built-in tools, see [Built-in Tools Reference](#5.3).

Sources: [packages/opencode/src/tool/read.ts:64-180](), [packages/opencode/src/tool/edit.ts:58-173](), [packages/opencode/src/tool/apply_patch.ts:22-24](), [packages/opencode/src/tool/task.ts:81-155]()

## Language Server Protocol (LSP) Integration

OpenCode integrates with the Language Server Protocol to provide agents with IDE-grade intelligence.

- **Context Awareness**: The `read` tool "warms" the LSP for files it accesses by calling `lsp.touchFile()` [packages/opencode/src/tool/read.ts:117-120]().
- **Intelligence**: The `LSP.Service` provides definitions, symbols, and type information.

For details on LSP system architecture, server definitions for 20+ languages, and auto-download mechanisms, see [Language Server Protocol Integration](#5.4).

Sources: [packages/opencode/src/tool/read.ts:117-120]()

## Code Formatting System

To ensure code quality, OpenCode includes an auto-formatting system that runs after agent edits.

- **Format-on-Save**: Tools like `edit` [packages/opencode/src/tool/edit.ts:112-114]() and `apply_patch` call `format.file()` immediately after writing changes.
- **BOM Preservation**: The system handles Byte Order Marks (BOM) during the write/format cycle to ensure file encoding consistency [packages/opencode/src/tool/edit.ts:133-135]().

For documentation on the auto-formatting system, supported formatters, and format-on-save configuration, see [Code Formatting System](#5.5).

Sources: [packages/opencode/src/tool/edit.ts:112-135]()

## Model Context Protocol (MCP)

OpenCode extends its capabilities through external integrations via the Model Context Protocol (MCP), allowing agents to connect to external MCP servers for additional tools, prompts, and resources.

For details on MCP integration, server connections, OAuth flows, catalogs, and using external tools, prompts, and resources, see [Model Context Protocol (MCP)](#5.6).

Sources: [packages/opencode/src/tool/tool.ts:1-169]()

## Skills System

The skills system provides reusable agent patterns and command templates. Agents can load skills via the `SkillTool` [packages/opencode/src/tool/skill.ts:12-14](), which discovers markdown instructions and associated scripts from local project directories [packages/opencode/src/tool/skill.ts:34-43]().

For information explaining the skills system for reusable agent patterns and command templates, see [Skills System](#5.7).

Sources: [packages/opencode/src/tool/skill.ts:12-43]()

---

