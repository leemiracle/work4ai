<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/knowledge-work-plugins · page 2 Plugin System Architecture · fetched 2026-10-26 -->

# Plugin System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [cowork-plugin-management/.claude-plugin/plugin.json](cowork-plugin-management/.claude-plugin/plugin.json)
- [cowork-plugin-management/skills/cowork-plugin-customizer/SKILL.md](cowork-plugin-management/skills/cowork-plugin-customizer/SKILL.md)
- [cowork-plugin-management/skills/cowork-plugin-customizer/references/mcp-servers.md](cowork-plugin-management/skills/cowork-plugin-customizer/references/mcp-servers.md)
- [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md](cowork-plugin-management/skills/create-cowork-plugin/SKILL.md)
- [cowork-plugin-management/skills/create-cowork-plugin/references/component-schemas.md](cowork-plugin-management/skills/create-cowork-plugin/references/component-schemas.md)
- [cowork-plugin-management/skills/create-cowork-plugin/references/example-plugins.md](cowork-plugin-management/skills/create-cowork-plugin/references/example-plugins.md)
- [data/.mcp.json](data/.mcp.json)
- [data/CONNECTORS.md](data/CONNECTORS.md)

</details>



## Purpose and Scope

This page provides a comprehensive high-level overview of the knowledge work plugins system architecture. It explains how plugins are structured, how they integrate with external tools through MCP servers, and how components like skills, commands, and connectors work together to extend Claude's capabilities [README.md:61-64]().

As a parent page, this document outlines the macro architecture. For detailed technical specifications, implementation guides, and configuration references, see the child pages:
- [Plugin Structure and Components](#2.1) — Detail the standardized plugin directory structure: `plugin.json` manifest, `.mcp.json` configuration, `commands/`, `skills/`, and `assets/`
- [Connector System and Tool Abstraction](#2.2) — Explain the `~~` category placeholder system, how plugins stay tool-agnostic, and how `.mcp.json` maps categories to specific tools
- [Skills vs Commands](#2.3) — Differentiate between skills (auto-activated domain knowledge) and commands (explicit slash commands), with examples and use cases
- [MCP Server Integration](#2.4) — Explain how MCP (Model Context Protocol) servers work, the `.mcp.json` configuration format, and how plugins connect to external tools
- [Customizing Plugins](#2.5) — Guide users through customizing plugins: swapping connectors, adding company context to skills, and adjusting workflows

Sources: [README.md:61-64](), [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md:14-16]()

## Architectural Overview

The plugin system is built entirely on open, file-based components—markdown files and JSON configurations—requiring no code compilation, infrastructure, or complex build steps [README.md:65-65](). Every plugin acts as a self-contained package that injects specialized knowledge, event-driven hooks, and external tool connections into Claude Cowork and Claude Code sessions [README.md:3-9]().

### Component Architecture Diagram

The following diagram illustrates how natural language work requests interact with the file-based entities inside a plugin directory:

```mermaid
graph TB
    subgraph NaturalLanguageSpace["Natural Language & User Intent"]
        UserReq["User Prompt / Request"]
        IntentMatch["Automatic Skill Trigger / Slash Command"]
    end

    subgraph CodeEntitySpace["Plugin Code Entity Space"]
        Manifest[".claude-plugin/plugin.json"]
        MCPConfig[".mcp.json"]
        SkillsDir["skills/*/SKILL.md"]
        HooksFile["hooks/hooks.json"]
    end

    UserReq --> IntentMatch
    IntentMatch --> SkillsDir
    SkillsDir --> MCPConfig
    Manifest --- CodeEntitySpace

    UserReq --- [README.md:7-9]()
    SkillsDir --- [cowork-plugin-management/skills/create-cowork-plugin/references/component-schemas.md:7-17]()
    MCPConfig --- [cowork-plugin-management/skills/create-cowork-plugin/references/component-schemas.md:94-94]()
    Manifest --- [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md:58-69]()
```

Sources: [README.md:7-9](), [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md:58-69](), [cowork-plugin-management/skills/create-cowork-plugin/references/component-schemas.md:7-94]()

## Core Components and Structure

Plugins rely on a standardized directory layout containing a manifest file (`plugin.json`), domain knowledge (`skills/`), slash commands (`commands/`), event hooks (`hooks/`), and tool mappings (`.mcp.json`) [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md:32-45](). This modular design ensures that any role-specific workflows can be bundled cleanly and shared across teams.

For comprehensive details on manifest configuration, directory rules, and component schemas, see [Plugin Structure and Components](#2.1).

Sources: [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md:32-45]()

## Connector System and Tool Abstraction

To remain independent of specific software vendors, plugins utilize an abstraction layer based on category placeholders (`~~category`) rather than hardcoded tool names [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md:106-110](). For example, a workflow references `~~project tracker`, which resolves dynamically via `.mcp.json` and `CONNECTORS.md` to specific implementations like Jira, Asana, or Linear [data/CONNECTORS.md:5-16]().

### Connector Resolution Flow

```mermaid
graph LR
    subgraph NaturalLanguageSpace["Intent Space"]
        Query["User Action in Skill"]
    end

    subgraph CodeEntitySpace["Resolution & Config"]
        Placeholder["~~project tracker"]
        ConnectorDoc["CONNECTORS.md"]
        MCPJson[".mcp.json"]
    end

    subgraph ExecutionSpace["Tool Execution"]
        ClientCall["mcpServers Configuration"]
    end

    Query --> Placeholder
    Placeholder --> ConnectorDoc
    ConnectorDoc --> MCPJson
    MCPJson --> ClientCall

    Query --- [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md:109-111]()
    Placeholder --- [data/CONNECTORS.md:5-7]()
    MCPJson --- [data/.mcp.json:27-30]()
```

For detailed instructions on swapping connectors and understanding the placeholder system, see [Connector System and Tool Abstraction](#2.2).

Sources: [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md:106-127](), [data/CONNECTORS.md:1-17](), [data/.mcp.json:1-35]()

## Skills vs Commands

Claude processes interactions using two primary mechanisms: **skills** and **commands**. Skills are domain-expert markdown files that activate automatically when Claude detects relevant trigger phrases in the conversation [README.md:61-61](). Commands are explicit slash actions invoked directly by the user (e.g., `/finance:reconciliation`) to execute deterministic workflows [README.md:62-62]().

For examples, progressive disclosure rules, and best practices for authoring both types, see [Skills vs Commands](#2.3).

Sources: [README.md:61-62](), [cowork-plugin-management/skills/create-cowork-plugin/references/component-schemas.md:32-57]()

## MCP Server Integration

External data sources and tools are integrated into plugins using the Model Context Protocol (MCP) [README.md:63-63](). Servers are declared in the `.mcp.json` configuration file, specifying endpoints and transport types that allow Claude to securely query databases, project management boards, and repositories [data/.mcp.json:1-35]().

For configuration formats, server types, and troubleshooting connection states, see [MCP Server Integration](#2.4).

Sources: [README.md:63-63](), [data/.mcp.json:1-35]()

## Customizing Plugins

Out-of-the-box plugins provide robust defaults, but their true utility emerges when tailored to an organization's specific terminology, tools, and processes [README.md:7-9](). The `cowork-plugin-customizer` skill automates this adaptation by scanning for placeholders, querying internal company knowledge via MCPs, and updating configurations [cowork-plugin-management/skills/cowork-plugin-customizer/SKILL.md:10-104]().

For a step-by-step walkthrough on swapping connectors, adding company context, and adjusting workflows, see [Customizing Plugins](#2.5).

Sources: [README.md:7-9](), [cowork-plugin-management/skills/cowork-plugin-customizer/SKILL.md:10-104]()

---

