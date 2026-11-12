<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/knowledge-work-plugins · page 8 Developer Guide · fetched 2026-10-26 -->

# Developer Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cowork-plugin-management/.claude-plugin/plugin.json](cowork-plugin-management/.claude-plugin/plugin.json)
- [cowork-plugin-management/skills/cowork-plugin-customizer/SKILL.md](cowork-plugin-management/skills/cowork-plugin-customizer/SKILL.md)
- [cowork-plugin-management/skills/cowork-plugin-customizer/references/mcp-servers.md](cowork-plugin-management/skills/cowork-plugin-customizer/references/mcp-servers.md)
- [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md](cowork-plugin-management/skills/create-cowork-plugin/SKILL.md)
- [cowork-plugin-management/skills/create-cowork-plugin/references/component-schemas.md](cowork-plugin-management/skills/create-cowork-plugin/references/component-schemas.md)
- [cowork-plugin-management/skills/create-cowork-plugin/references/example-plugins.md](cowork-plugin-management/skills/create-cowork-plugin/references/example-plugins.md)

</details>



This guide covers the technical process of creating new plugins or extending existing ones in the `knowledge-work-plugins` repository. It includes the plugin file structure, configuration schemas, development workflows, and usage of the `cowork-plugin-management` plugin for programmatic plugin creation and customization.

For conceptual understanding of how plugins work, see [Plugin System Architecture](#2). For detailed documentation on specific components, see [Plugin Structure and Components](#2.1) and [Connector System and Tool Abstraction](#2.2).

## Plugin Development Overview

The `knowledge-work-plugins` repository follows a file-based architecture where plugins are defined entirely through markdown and JSON files. No build steps, compilation, or deployment pipelines are required. Plugins are loaded directly by the Claude runtime from their directory structure.

### Plugin Development Lifecycle

```mermaid
graph TB
    ["Dev"] -- "1. Scaffold" --> ["CreateDirectory"]
    ["CreateDirectory"] -- "2. Define" --> ["Manifest"]
    ["Manifest"] -- "3. Configure" --> ["MCP"]
    ["MCP"] -- "4. Author" --> ["Skills"]
    ["Skills"] -- "5. Author" --> ["Agents"]
    
    subgraph "PluginDirectoryStructure"
        ["Root"] --> [".claude-plugin/"]
        [".claude-plugin/"] --> ["plugin.json"]
        ["Root"] --> [".mcp.json"]
        ["Root"] --> ["skills/"]
        ["Root"] --> ["agents/"]
        ["Root"] --> ["hooks/"]
    end
    
    subgraph "Deployment"
        ["MarketplaceJson"] --> ["ClaudeCLI"]
        ["ClaudeCLI"] --> ["ClaudeRuntime"]
    end
    
    ["Agents"] -- "Register" --> ["MarketplaceJson"]
```

**Development workflow**: Create plugin directory structure → Define manifest → Configure MCP servers → Write skills and agents → Register in `marketplace.json` → Install via CLI.

Sources: [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md:30-55](), [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md:137-180]()

## Plugin File Structure Reference

Every plugin must conform to this exact directory structure. Note that `skills/` is the preferred format for domain knowledge over the legacy `commands/` format.

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json           # Required: plugin manifest
├── skills/                   # Skills (subdirectories with SKILL.md)
│   └── skill-name/
│       ├── SKILL.md          # Core knowledge (required)
│       └── references/       # Detailed docs loaded on demand
├── agents/                   # Subagent definitions (.md files)
├── hooks/                    # Optional: Event-based logic
│   └── hooks.json
├── .mcp.json                 # MCP server definitions
├── CONNECTORS.md             # Documentation for ~~ placeholders
└── README.md                 # Plugin documentation
```

### Directory and File Naming Conventions

| Component | Naming Pattern | Example | Notes |
|-----------|---------------|---------|-------|
| Plugin directory | `kebab-case` | `bio-research/` | Must match `plugin.json` name |
| `plugin.json` | Exact name | `plugin.json` | Inside `.claude-plugin/` [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md:56-69]() |
| Skill directory | `kebab-case` | `skills/api-design/` | Contains `SKILL.md` [cowork-plugin-management/skills/create-cowork-plugin/references/component-schemas.md:38-50]() |
| Agent files | `kebab-case.md` | `agents/code-reviewer.md` | Defined in [cowork-plugin-management/skills/create-cowork-plugin/references/component-schemas.md:60-72]() |
| Hook config | Exact name | `hooks/hooks.json` | Defined in [cowork-plugin-management/skills/create-cowork-plugin/references/component-schemas.md:142-145]() |

Sources: [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md:30-55](), [cowork-plugin-management/skills/create-cowork-plugin/references/component-schemas.md:127-133]()

## Component Schemas

### plugin.json Manifest
Located at `.claude-plugin/plugin.json`. It requires a `name` in kebab-case and a semantic `version`.

```json
{
  "name": "plugin-name",
  "version": "0.1.0",
  "description": "Brief explanation",
  "author": { "name": "Author Name" }
}
```
Sources: [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md:56-74]()

### Skills (SKILL.md)
Skills use Markdown with YAML frontmatter. The `description` field is critical as it contains trigger phrases for Claude. The body should use imperative style and can leverage progressive disclosure via the `references/` directory.

```yaml
---
name: skill-identifier
description: >
  This skill should be used when the user asks to "trigger phrase 1" or "trigger phrase 2".
---
# Skill Content
Instructions for Claude...
```
Sources: [cowork-plugin-management/skills/create-cowork-plugin/references/component-schemas.md:5-37](), [cowork-plugin-management/skills/create-cowork-plugin/references/component-schemas.md:52-56]()

### .mcp.json Configuration
The `.mcp.json` file maps tool identifiers to MCP server processes or endpoints. It supports `stdio` (local process) and `http` types. Use `${CLAUDE_PLUGIN_ROOT}` for all intra-plugin path references.

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/server/index.js"],
      "type": "stdio"
    },
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/"
    }
  }
}
```
Sources: [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md:130-132](), [cowork-plugin-management/skills/create-cowork-plugin/references/component-schemas.md:229-250]()

### Bridging Natural Language to Code Entity Space

This diagram illustrates how a user's natural language request is translated into an interaction with a specific MCP server through the plugin's configuration.

```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        ["UserRequest"] -- "Triggers" --> ["SkillDescription"]
    end

    subgraph "CodeEntitySpace"
        ["SkillDescription"] -- "DefinedIn" --> ["SKILL.md"]
        ["SKILL.md"] -- "Uses" --> ["Placeholder"]
        ["Placeholder"] -- "ResolvedBy" --> ["CONNECTORS.md"]
        ["CONNECTORS.md"] -- "ConfiguredIn" --> [".mcp.json"]
        [".mcp.json"] -- "Instantiates" --> ["McpServer"]
    end

    ["McpServer"] -- "Calls" --> ["ExternalAPI"]
```

Sources: [cowork-plugin-management/skills/create-cowork-plugin/references/component-schemas.md:229-250](), [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md:102-128]()

## Creating a New Plugin

Creating a new plugin involves a structured workflow, from initial concept to a deployable `.plugin` file. This process is designed to ensure consistency and adherence to the plugin architecture.

For a step-by-step guide on scaffolding a plugin from discovery to packaging, see [Creating a New Plugin](#8.1). This child page will cover:
*   **Discovery Phase**: Defining the problem the plugin solves, its target users, and any external tool integrations. [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md:137-151]()
*   **Component Planning**: Determining which plugin component types (Skills, Agents, MCP servers, Hooks) are necessary. [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md:152-166]()
*   **Design & Clarifying Questions**: Specifying each component in detail, including their functionality and interactions. [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md:167-171]()
*   **Implementation**: Creating all necessary plugin files, including the `plugin.json` manifest, `SKILL.md` files, and `.mcp.json` configurations. [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md:172-174]()
*   **Review & Package**: Finalizing the plugin and packaging it into a `.plugin` file. [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md:175-180]()

Sources: [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md:137-180]()

## Using cowork-plugin-management

The `cowork-plugin-management` plugin is a suite of tools for developers to programmatically create, customize, and manage other plugins within a Cowork session.

### Programmatic Plugin Management Architecture

```mermaid
graph LR
    subgraph "cowork-plugin-management"
        ["create-cowork-plugin"]
        ["cowork-plugin-customizer"]
        ["search_mcp_registry"]
    end

    subgraph "PluginFiles"
        ["plugin.json"]
        ["SKILL.md"]
        [".mcp.json"]
    end

    ["create-cowork-plugin"] -- "Generates" --> ["PluginFiles"]
    ["cowork-plugin-customizer"] -- "Modifies" --> ["PluginFiles"]
    ["search_mcp_registry"] -- "Informs" --> ["cowork-plugin-customizer"]
    
    subgraph "Output"
        ["PluginFiles"] -- "PackagedAs" --> [".plugin"]
    end
```

For details on using these tools to automate development, see [Using cowork-plugin-management](#8.2). This child page will cover:
*   **`create-cowork-plugin`**: Guides users through a 5-phase workflow to build new plugins conversationally. [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md:10-25]()
*   **`cowork-plugin-customizer`**: Tailors existing plugins by replacing `~~` placeholders, updating MCP configurations, and modifying skill content to match organizational needs. [cowork-plugin-management/skills/cowork-plugin-customizer/SKILL.md:10-33]()
*   **MCP Discovery and Connection**: Using `search_mcp_registry` and `suggest_connectors` to find and install MCP servers during customization. [cowork-plugin-management/skills/cowork-plugin-customizer/references/mcp-servers.md:1-25]()

Sources: [cowork-plugin-management/skills/create-cowork-plugin/SKILL.md:1-8](), [cowork-plugin-management/skills/cowork-plugin-customizer/SKILL.md:1-8](), [cowork-plugin-management/skills/cowork-plugin-customizer/references/mcp-servers.md:7-25]()

---

