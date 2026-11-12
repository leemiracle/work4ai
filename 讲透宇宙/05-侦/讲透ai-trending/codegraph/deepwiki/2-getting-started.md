<!-- source: DeepWiki mcp.deepwiki.com · repo colbymchenry/codegraph · page 2 Getting Started · fetched 2026-10-30 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CLAUDE.md](CLAUDE.md)
- [README.md](README.md)
- [__tests__/installer.test.ts](__tests__/installer.test.ts)
- [package-lock.json](package-lock.json)
- [package.json](package.json)
- [site/src/content/docs/core-concepts/how-it-works.md](site/src/content/docs/core-concepts/how-it-works.md)
- [site/src/content/docs/core-concepts/resolution.md](site/src/content/docs/core-concepts/resolution.md)
- [site/src/content/docs/getting-started/installation.md](site/src/content/docs/getting-started/installation.md)
- [site/src/content/docs/getting-started/introduction.md](site/src/content/docs/getting-started/introduction.md)
- [site/src/content/docs/getting-started/quickstart.md](site/src/content/docs/getting-started/quickstart.md)
- [site/src/content/docs/getting-started/your-first-graph.md](site/src/content/docs/getting-started/your-first-graph.md)
- [site/src/content/docs/guides/framework-routes.md](site/src/content/docs/guides/framework-routes.md)
- [site/src/content/docs/guides/indexing.md](site/src/content/docs/guides/indexing.md)
- [site/src/content/docs/reference/api.md](site/src/content/docs/reference/api.md)
- [site/src/content/docs/reference/integrations.md](site/src/content/docs/reference/integrations.md)
- [site/src/content/docs/reference/mcp-server.md](site/src/content/docs/reference/mcp-server.md)
- [src/bin/codegraph.ts](src/bin/codegraph.ts)
- [src/installer/config-writer.ts](src/installer/config-writer.ts)
- [src/installer/index.ts](src/installer/index.ts)
- [src/mcp/tools.ts](src/mcp/tools.ts)

</details>



This page guides you through initial setup and basic usage of CodeGraph, serving as an entry point to the ecosystem. CodeGraph provides a local-first code intelligence system designed to expose structural AST knowledge to AI assistants via the Model Context Protocol (MCP) [site/src/content/docs/getting-started/introduction.md:1-7]().

For a detailed walkthrough of the interactive installer and supported agent targets, see [Installation](#2.1). For common workflows such as initialization, indexing, and queries, see [Quick Start Guide](#2.2). For configuration options and directory structures, see [Configuration](#2.3).

---

## Overview of Setup Flow

CodeGraph setup connects your AI agent environment (Natural Language Space) to the local knowledge graph database and configuration files (Code Entity Space). 

### System Initialization and Agent Wiring

```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        User["UserPrompt"]
        AgentTarget["AgentTargetClaudeCursorCodex"]
    end

    subgraph "CodeEntitySpace"
        CLI["codegraphCLI"]
        Installer["src/installer/index.ts"]
        DB[".codegraph/codegraph.db"]
        Config[".codegraph/config.json"]
        McpConfig["AgentConfig/.mcp.json"]
    end

    User -->| "codegraph install" | Installer
    Installer -->| "writeMcpEntry" | McpConfig
    CLI -->| "codegraph init" | DB
    CLI -->| "codegraph init" | Config
    AgentTarget -->| "spawn serve --mcp" | DB
```
Sources: [src/installer/index.ts:1-14](), [src/installer/config-writer.ts:34-40]()

---

## Runtime Query and Search Flow

When an agent interacts with CodeGraph during a task, requests flow from Natural Language Space down through the MCP tools layer into the Code Entity Space knowledge graph and SQLite database.

### Agent Query Execution Model

```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        AgentPrompt["AgentQueryTask"]
        ToolCall["codegraph_explore"]
    end

    subgraph "CodeEntitySpace"
        MCPHandler["src/mcp/tools.ts"]
        CodeGraphFacade["CodeGraph"]
        QueryPool["QueryPool"]
        SqliteDB["SQLiteDatabase"]
    end

    AgentPrompt -->| "invokes" | ToolCall
    ToolCall -->| "dispatches" | MCPHandler
    MCPHandler -->| "queries" | CodeGraphFacade
    CodeGraphFacade -->| "executes" | QueryPool
    QueryPool -->| "reads" | SqliteDB
```
Sources: [src/mcp/tools.ts:1-25](), [package.json:1-10]()

---

## 2.1 Installation

The installation subsystem uses an interactive installer via `runInstallerWithOptions` to configure global or project-local MCP server integrations [src/installer/index.ts:11-14](). CodeGraph supports a wide array of agent targets through the `AgentTarget` registry, including Claude Code, Cursor, Codex CLI, opencode, Hermes Agent, Gemini CLI, Kiro, Antigravity IDE, and GitHub Copilot (VS Code, CLI, and JetBrains) [README.md:9-39](), [src/installer/index.ts:16-25]().

For detailed walkthroughs covering global vs. local installation scopes, auto-allow permissions, hook configurations, and specific target requirements, see [Installation](#2.1).

Sources: [src/installer/index.ts:11-14](), [README.md:9-39]()

---

## 2.2 Quick Start Guide

Once the CLI is installed and your agent is wired, initializing a project builds the underlying SQLite knowledge graph [site/src/content/docs/guides/indexing.md:6-14](). Running `codegraph init` creates the `.codegraph/` directory and indexes all supported files in a single step [site/src/content/docs/guides/indexing.md:10-13](). During agent sessions, the built-in file watcher and auto-sync policies keep the index fresh without requiring manual intervention [site/src/content/docs/guides/indexing.md:25-41]().

For step-by-step workflows on running your first index, executing queries, and using CodeGraph with Claude Code, see [Quick Start Guide](#2.2).

Sources: [site/src/content/docs/guides/indexing.md:6-41]()

---

## 2.3 Configuration

CodeGraph project behavior is governed by configuration files stored inside the `.codegraph/` directory [site/src/content/docs/getting-started/introduction.md:1-34](). The configuration system handles file exclusion patterns, language-specific parsing rules, deprioritized paths, and multi-repo workspace settings.

For full details on `.codegraph` directory structures, `config.json` parameters, and integration files, see [Configuration](#2.3).

Sources: [site/src/content/docs/getting-started/introduction.md:1-34]()

---

