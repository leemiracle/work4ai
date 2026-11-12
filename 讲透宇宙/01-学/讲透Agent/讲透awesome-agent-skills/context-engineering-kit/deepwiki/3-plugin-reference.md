<!-- source: DeepWiki mcp.deepwiki.com · repo NeoLabHQ/context-engineering-kit · page 3 Plugin Reference · fetched 2026-10-26 -->

# Plugin Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [.claude/commands/bump-plugin.md](.claude/commands/bump-plugin.md)
- [docs/concepts.md](docs/concepts.md)
- [docs/plugins/README.md](docs/plugins/README.md)
- [docs/plugins/ddd/README.md](docs/plugins/ddd/README.md)
- [docs/plugins/ddd/usage-examples.md](docs/plugins/ddd/usage-examples.md)
- [plugins/ddd/README.md](plugins/ddd/README.md)
- [plugins/sadd/.claude-plugin/plugin.json](plugins/sadd/.claude-plugin/plugin.json)

</details>



This page provides a comprehensive reference for all official plugins available in the Context Engineering Kit marketplace. It covers the plugin registry structure, categorization system, and provides a high-level overview of each plugin's purpose and capabilities.

For detailed documentation of specific plugins, see the category-specific pages:
- **Code Quality Plugins**: Focus on review and self-refinement. For details, see [Code Quality Plugins](#3.1).
- **Development Workflow Plugins**: Implement structured methodologies like TDD, SDD, and DDD. For details, see [Development Workflow Plugins](#3.2).
- **Integration Plugins**: Connect with Git and Model Context Protocol (MCP). For details, see [Integration Plugins](#3.3).
- **Continuous Improvement Plugins**: Root cause analysis and documentation management. For details, see [Continuous Improvement Plugins](#3.4).
- **Configuration Plugins**: Project standards and custom agent authoring. For details, see [Configuration Plugins](#3.5).

## Plugin Registry Architecture

The Context Engineering Kit maintains a centralized plugin registry in [.claude-plugin/marketplace.json:1-155](). This registry follows the official Claude Code marketplace schema and contains metadata for all available plugins.

### Registry to Code Entity Mapping
The following diagram bridges the high-level marketplace definitions to the actual file system entities within the repository, using specific names found in the configuration.

Title: Marketplace Entity Mapping
```mermaid
graph TD
    subgraph "Marketplace_Space_(marketplace.json)"
        Registry[".claude-plugin/marketplace.json"]
        Entry["Plugin Entry"]
        EntryName["'name': 'sdd'"]
        EntrySource["'source': './plugins/sdd'"]
    end

    subgraph "Code_Entity_Space_(File_System)"
        PluginDir["plugins/sdd/"]
        Manifest["plugins/sdd/.claude-plugin/plugin.json"]
        CommandsDir["plugins/sdd/commands/"]
        SkillsDir["plugins/sdd/skills/"]
        AgentsDir["plugins/sdd/agents/"]
    end

    Registry -->|"contains"| Entry
    Entry --> EntryName
    Entry --> EntrySource
    EntrySource -->|"points to"| PluginDir
    PluginDir -->|"contains"| Manifest
    PluginDir -->|"contains"| CommandsDir
    PluginDir -->|"contains"| SkillsDir
    PluginDir -->|"contains"| AgentsDir
```

**Registry Location and Plugin Directory Mapping**
The marketplace registry at [.claude-plugin/marketplace.json:10-154]() defines all available plugins. Each plugin's `source` field points to its implementation directory following the pattern `./plugins/{plugin-name}/`. Each plugin directory contains a `.claude-plugin/plugin.json` manifest file that mirrors the registry metadata, such as [plugins/sadd/.claude-plugin/plugin.json:1-9]().

Sources: [.claude-plugin/marketplace.json:1-155](), [plugins/sadd/.claude-plugin/plugin.json:1-9]()

## Plugin Categories

The Context Engineering Kit organizes plugins into two primary categories that determine their focus and typical usage patterns:

| Category | Focus | Token Philosophy | Primary Use Cases |
|----------|-------|------------------|-------------------|
| **productivity** | Immediate value delivery, analysis, and quality improvement | Skills and commands for on-demand analysis | Code review, documentation, continuous improvement, version control |
| **development** | Structured workflows and methodologies | Commands for guided processes, skills for persistent patterns | TDD, DDD, SADD, SDD, custom tooling, tech stack configuration |

Title: Plugin Category Distribution
```mermaid
graph TB
    subgraph "productivity_category"
        Reflexion["'name': 'reflexion'"]
        CodeReview["'name': 'review'"]
        Git["'name': 'git'"]
        Kaizen["'name': 'kaizen'"]
        Docs["'name': 'docs'"]
    end
    
    subgraph "development_category"
        TDD["'name': 'tdd'"]
        SADD["'name': 'sadd'"]
        DDD["'name': 'ddd'"]
        SDD["'name': 'sdd'"]
        CustomAgent["'name': 'customaize-agent'"]
        TechStack["'name': 'tech-stack'"]
        MCP["'name': 'mcp'"]
        FPF["'name': 'fpf'"]
    end
    
    Reflexion --- ProductivityLabel["Productivity Focus:<br/>Immediate Analysis"]
    TDD --- DevelopmentLabel["Development Focus:<br/>Structured Workflows"]
```

**Category Distribution and Component Usage**
The registry at [.claude-plugin/marketplace.json:10-154]() defines 13 plugins. The `category` field, such as in [.claude-plugin/marketplace.json:20]() (productivity) or [.claude-plugin/marketplace.json:53]() (development), determines how the plugin is classified within the marketplace.

Sources: [.claude-plugin/marketplace.json:10-154]()

## Plugin Component Types

Each plugin can provide three types of components, each with different token efficiency characteristics and usage patterns as defined in [docs/concepts.md:12-134]():

- **Commands**: On-demand execution. Loaded only when invoked (e.g., `/plugin-name:command-name`). They are the most token-efficient [docs/concepts.md:14-21]().
- **Skills**: Pre-loaded context. These load automatically and inform all agent decisions, providing best practices and methodologies [docs/concepts.md:52-67]().
- **Agents**: Specialized expertise. Spawns focused sub-agents for specific tasks with their own fresh context [docs/concepts.md:81-91]().

Sources: [docs/concepts.md:12-134]()

## Summary of Official Plugins

### Code Quality Plugins
These plugins focus on verifying and refining existing code.
- **Reflexion**: Implements feedback and refinement loops based on Self-Refine and Reflexion papers [.claude-plugin/marketplace.json:12-21]().
- **Review**: Uses multiple specialized agents (e.g., bug hunter, security auditor) for thorough codebase and PR analysis [.claude-plugin/marketplace.json:23-32]().
- For details, see [Code Quality Plugins](#3.1).

### Development Workflow Plugins
Structured methodologies to guide feature creation from start to finish.
- **TDD**: Test-Driven Development with guidance on anti-patterns and subagent testing skills [.claude-plugin/marketplace.json:45-54]().
- **SDD**: Specification-Driven Development based on GitHub Spec Kit and OpenSpec [.claude-plugin/marketplace.json:78-87]().
- **SADD**: Subagent-Driven Development for task delegation with quality gates [.claude-plugin/marketplace.json:56-65]().
- **DDD**: Domain-Driven Development focusing on Clean Architecture, SOLID, and 14 composable rules [.claude-plugin/marketplace.json:67-76]().
- **FPF**: First Principles Framework for structured reasoning via ADI (Abduction-Deduction-Induction) cycles [.claude-plugin/marketplace.json:144-153]().
- For details, see [Development Workflow Plugins](#3.2).

### Integration Plugins
Connecting Claude Code to the broader engineering ecosystem.
- **Git**: Conventional commits, PR creation, and git worktree management [.claude-plugin/marketplace.json:34-43]().
- **MCP**: Model Context Protocol integration to mandate usage of external tools in `CLAUDE.md` [.claude-plugin/marketplace.json:133-142]().
- For details, see [Integration Plugins](#3.3).

### Continuous Improvement Plugins
Analysis tools for process and documentation.
- **Kaizen**: Lean-inspired root cause analysis including 5 Whys and Cause and Effect Analysis [.claude-plugin/marketplace.json:89-98]().
- **Docs**: Automated documentation generation and refinement for analyzing project structure [.claude-plugin/marketplace.json:111-120]().
- For details, see [Continuous Improvement Plugins](#3.4).

### Configuration Plugins
Standardizing the development environment.
- **Tech Stack**: Language-specific best practices setup (e.g., TypeScript) for `CLAUDE.md` [.claude-plugin/marketplace.json:122-131]().
- **Customaize Agent**: Tools for authoring your own commands, skills, and agents using Anthropic best practices [.claude-plugin/marketplace.json:100-109]().
- For details, see [Configuration Plugins](#3.5).

Sources: [.claude-plugin/marketplace.json:1-155](), [docs/plugins/README.md:1-205](), [docs/plugins/ddd/README.md:1-45]()

---

