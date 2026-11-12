<!-- source: DeepWiki mcp.deepwiki.com · repo neolabhq/context-engineering-kit · page 1 Overview · fetched 2026-10-27 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.bin/install-commands.sh](.bin/install-commands.sh)
- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [.claude/commands/bump-plugin.md](.claude/commands/bump-plugin.md)
- [README.md](README.md)
- [docs/README.md](docs/README.md)
- [docs/concepts.md](docs/concepts.md)
- [docs/getting-started.md](docs/getting-started.md)
- [docs/guides/pr-review.md](docs/guides/pr-review.md)
- [docs/resources/related-projects.md](docs/resources/related-projects.md)
- [plugins/customaize-agent/.claude-plugin/plugin.json](plugins/customaize-agent/.claude-plugin/plugin.json)
- [plugins/sadd/.claude-plugin/plugin.json](plugins/sadd/.claude-plugin/plugin.json)
- [plugins/sdd/.claude-plugin/plugin.json](plugins/sdd/.claude-plugin/plugin.json)

</details>



The Context Engineering Kit (CEK) is a curated plugin marketplace for Claude Code that provides advanced context engineering techniques and patterns. The kit consists of 13 officially maintained plugins organized in the `.claude-plugin/marketplace.json` registry [[.claude-plugin/marketplace.json:1-155]](), designed to improve AI agent output quality while maintaining a minimal token footprint. Each plugin implements scientifically-proven techniques for specific development workflows, code quality improvements, and external integrations [[README.md:19-31]]().

This page provides a high-level architectural overview of the plugin system, marketplace structure, and configuration management. For installation and initial setup instructions, see [Getting Started](#1.1). For detailed architectural principles, see [Architecture & Design Principles](#1.2). For comprehensive plugin documentation, see [Plugin Reference](#3).

**Sources:** [README.md:1-115](), [.claude-plugin/marketplace.json:1-155](), [docs/README.md:5-52]()

## System Architecture

The Context Engineering Kit operates through a multi-tier architecture: the marketplace registry manages plugin metadata, installed plugins load their components (commands, skills, agents) into Claude Code's context, and a hierarchical configuration system persists project knowledge across sessions.

### High-Level Component Structure

```mermaid
graph TB
    subgraph "User_Interaction"
        Developer["Developer"]
        ClaudeCLI["claude CLI"]
    end
    
    subgraph "Marketplace_Core"
        MarketplaceJSON[".claude-plugin/marketplace.json<br/>Registry v2.2.3<br/>13 plugins"]
        PluginDirs["plugins/<br/>reflexion/<br/>code-review/<br/>git/<br/>...13 total"]
    end
    
    subgraph "Configuration_Hierarchy"
        ProjectShared["./CLAUDE.md<br/>Shared Context<br/>Git Tracked"]
        ProjectPersonal["./CLAUDE.local.md<br/>Personal Overrides<br/>Not Tracked"]
        UserGlobal["~/.claude/CLAUDE.md<br/>User Defaults<br/>Cross-Project"]
    end
    
    subgraph "Plugin_Categories"
        Productivity["Productivity<br/>reflexion<br/>code-review<br/>git<br/>kaizen<br/>docs"]
        Development["Development<br/>tdd<br/>sadd<br/>ddd<br/>sdd<br/>customaize-agent<br/>tech-stack<br/>mcp<br/>fpf"]
    end
    
    Developer -->|"executes"| ClaudeCLI
    ClaudeCLI -->|"loads registry"| MarketplaceJSON
    ClaudeCLI -->|"reads at session start"| ProjectShared
    ClaudeCLI -->|"reads at session start"| ProjectPersonal
    ClaudeCLI -->|"reads at session start"| UserGlobal
    
    MarketplaceJSON -->|"references"| PluginDirs
    PluginDirs -->|"categorized as"| Productivity
    PluginDirs -->|"categorized as"| Development
    
    Productivity -->|"may update"| ProjectShared
    Development -->|"may update"| ProjectShared
```

**Sources:** [README.md:40-61](), [.claude-plugin/marketplace.json:1-155](), [docs/concepts.md:1-107]()

### Marketplace Registry Structure

The marketplace is defined by `marketplace.json` which declares plugin metadata, versions, and source locations. Each plugin entry contains:

| Field | Description | Example |
|-------|-------------|---------|
| `name` | Unique plugin identifier | `"reflexion"` |
| `description` | Plugin purpose and techniques | `"Collection of commands that force LLM to reflect..."` |
| `version` | Semantic version | `"1.1.4"` |
| `source` | Path to plugin directory | `"./plugins/reflexion"` |
| `category` | `"productivity"` or `"development"` | `"productivity"` |
| `author` | Plugin maintainer information | `{"name": "...", "email": "..."}` |

**Sources:** [.claude-plugin/marketplace.json:10-154]()

### Plugin Installation and Loading

```mermaid
graph LR
    subgraph "Discovery"
        AddCmd["/plugin marketplace add<br/>NeoLabHQ/context-engineering-kit"]
        AddCmd -->|"downloads"| LocalCache["Local Plugin Cache<br/>marketplace.json"]
    end
    
    subgraph "Installation"
        InstallCmd["/plugin install<br/>reflexion@CEK"]
        InstallCmd -->|"loads from"| LocalCache
        InstallCmd -->|"activates"| PluginComponents["Plugin Components"]
    end
    
    subgraph "Component_Types"
        PluginComponents --> Commands["Commands<br/>/reflexion:reflect<br/>On-demand loading"]
        PluginComponents --> Skills["Skills<br/>TDD best practices<br/>Pre-loaded context"]
        PluginComponents --> Agents["Specialized Agents<br/>code-reviewer<br/>bug-hunter"]
    end
    
    subgraph "Execution"
        Commands -->|"user invokes"| Execution["Command Execution"]
        Skills -->|"informs"| Execution
        Agents -->|"spawned during"| Execution
        Execution -->|"may update"| CLAUDEMD["CLAUDE.md<br/>Knowledge Base"]
    end
```

**Sources:** [README.md:40-61](), [docs/getting-started.md:18-62](), [docs/concepts.md:12-115]()

## Plugin Categories

The marketplace organizes plugins into two categories based on their primary function in `marketplace.json` [[.claude-plugin/marketplace.json:10-154]]():

### Productivity Category (5 plugins)

| Plugin | Primary Function | Key Commands |
|--------|------------------|--------------|
| `reflexion` | Self-refinement and critique | `/reflexion:reflect`, `/reflexion:memorize` |
| `code-review` | Multi-agent code quality analysis | `/code-review:review-local-changes`, `/code-review:review-pr` |
| `git` | Git operations and PR management | `/git:commit`, `/git:create-pr`, `/git:analyze-issue` |
| `kaizen` | Root cause analysis | `/kaizen:why`, `/kaizen:analyse-problem` |
| `docs` | Documentation management | `/docs:update-docs` |

**Sources:** [.claude-plugin/marketplace.json:11-120](), [docs/README.md:33-43]()

### Development Category (8 plugins)

| Plugin | Primary Function | Key Commands |
|--------|------------------|--------------|
| `tdd` | Test-driven development | `/tdd:write-tests`, `/tdd:fix-tests` |
| `sadd` | Subagent orchestration | Skills for dispatching subagents with quality gates |
| `ddd` | Domain-driven design patterns | `/ddd:setup-code-formating` |
| `sdd` | Specification-driven workflow | `/sdd:00-setup` through `/sdd:05-document` |
| `customaize-agent` | Plugin development toolkit | `/customaize-agent:create-command`, `/customaize-agent:test-skill` |
| `tech-stack` | Language/framework best practices | `/tech-stack:add-*` commands |
| `mcp` | MCP server integration | `/mcp:setup-context7-mcp`, `/mcp:setup-serena-mcp` |
| `fpf` | Structured reasoning | `/fpf:propose-hypotheses`, `/fpf:status` |

**Sources:** [.claude-plugin/marketplace.json:44-153](), [docs/README.md:37-47]()

## Configuration Hierarchy

The Context Engineering Kit uses a three-tier `CLAUDE.md` configuration system to manage context at different scopes. This hierarchy allows teams to share project-level knowledge while enabling individual customization.

### Three Configuration Tiers

```mermaid
graph TD
    subgraph "Configuration_Files"
        UserGlobal["~/.claude/CLAUDE.md<br/>User-global defaults<br/>All projects"]
        ProjectShared["./CLAUDE.md<br/>Project shared<br/>Git tracked"]
        ProjectPersonal["./CLAUDE.local.md<br/>Personal overrides<br/>Not tracked"]
    end
    
    subgraph "Content_Types"
        MCPConfig["MCP Configuration<br/>Server endpoints<br/>Library IDs"]
        BestPractices["Best Practices<br/>Code standards<br/>Architecture rules"]
        Learnings["Accumulated Knowledge<br/>Reflexion insights<br/>Pattern discoveries"]
        SetupCmds["Setup Commands<br/>Persistent context<br/>Hard rules"]
    end
    
    subgraph "Plugin_Writers"
        ReflexionWrite["/reflexion:memorize"]
        TechStackWrite["/tech-stack:add-*"]
        MCPWrite["/mcp:setup-*"]
        DDDWrite["/ddd:setup-*"]
    end
    
    subgraph "Plugin_Readers"
        AllPlugins["All Plugins<br/>Session start"]
        CodeReview["code-review<br/>Standards check"]
        SDD["sdd<br/>Architecture compliance"]
    end
    
    UserGlobal -.->|"defaults"| ProjectShared
    ProjectPersonal -.->|"overrides"| ProjectShared
    
    ProjectShared --> MCPConfig
    ProjectShared --> BestPractices
    ProjectShared --> Learnings
    ProjectShared --> SetupCmds
    
    ReflexionWrite -->|"writes"| Learnings
    TechStackWrite -->|"writes"| BestPractices
    MCPWrite -->|"writes"| MCPConfig
    DDDWrite -->|"writes"| SetupCmds
    
    MCPConfig -->|"informs"| AllPlugins
    BestPractices -->|"informs"| CodeReview
    Learnings -->|"informs"| SDD
```

| Configuration Level | File Path | Git Tracked | Scope | Use Case |
|---------------------|-----------|-------------|-------|----------|
| Project Shared | `./CLAUDE.md` | Yes | Team-wide | Shared standards, MCP configs, architecture decisions |
| Project Personal | `./CLAUDE.local.md` | No | Individual | Personal preferences, local overrides, API keys |
| User Global | `~/.claude/CLAUDE.md` | No | Cross-project | Personal defaults, coding style, preferred tools |

**Sources:** [docs/getting-started.md:81-88](), [docs/concepts.md:5-11]()

## Token Efficiency Principles

The Context Engineering Kit is architected to minimize token usage while maximizing context quality through several design patterns:

### Commands vs Skills Trade-off

```mermaid
graph LR
    subgraph "Commands_On_Demand"
        CMD["Commands<br/>Token cost: 0 until invoked<br/>Example: /reflexion:reflect"]
        CMD -->|"user invokes"| LoadCmd["Load command context<br/>Tokens: ~500-2000"]
        LoadCmd -->|"executes"| Result1["Result"]
    end
    
    subgraph "Skills_Pre_Loaded"
        SKILL["Skills<br/>Token cost: Always loaded<br/>Example: prompt-engineering"]
        SKILL -->|"session start"| LoadSkill["Loaded in context<br/>Tokens: ~300-1000"]
        LoadSkill -->|"informs all operations"| Result2["Continuous influence"]
    end
    
    subgraph "Design_Decision"
        PreferCmd["Prefer commands<br/>for specific operations"]
        PreferSkill["Use skills only for<br/>cross-cutting concerns"]
    end
    
    CMD -.->|"design preference"| PreferCmd
    SKILL -.->|"design preference"| PreferSkill
```

**Design Rationale:**
- **Commands** load context only when invoked, keeping baseline token count low [[docs/concepts.md:12-21]]().
- **Skills** are pre-loaded and influence all operations, reserved for frequently-used patterns [[docs/concepts.md:56-73]]().
- **Specialized Agents** spawn with focused context rather than loading all capabilities upfront [[docs/concepts.md:85-97]]().

**Sources:** [README.md:26](), [docs/concepts.md:74-83]()

## Knowledge Accumulation Loop

The Context Engineering Kit implements a feedback loop where plugins update `CLAUDE.md` files with learned patterns, creating continuously improving context over time.

```mermaid
graph TB
    subgraph "Session_N"
        Task1["Developer task<br/>Feature implementation"]
        Execute1["Plugin execution<br/>/reflexion:reflect"]
        Learn1["Identify patterns<br/>Edge cases, solutions"]
        Memorize1["/reflexion:memorize<br/>Update CLAUDE.md"]
    end
    
    subgraph "CLAUDE_md"
        Knowledge["CLAUDE.md<br/>Accumulated knowledge<br/>Architecture decisions<br/>Pattern library<br/>Root causes identified"]
    end
    
    subgraph "Session_N_Plus_1"
        LoadContext["Session start<br/>Load CLAUDE.md"]
        Task2["Similar task<br/>Better context"]
        BetterResult["Improved quality<br/>From accumulated knowledge"]
    end
    
    Task1 --> Execute1
    Execute1 --> Learn1
    Learn1 --> Memorize1
    Memorize1 -->|"appends"| Knowledge
    
    Knowledge -->|"next session"| LoadContext
    LoadContext --> Task2
    Task2 --> BetterResult
    
    BetterResult -.->|"continues cycle"| Task1
```

**Key Knowledge-Writing Plugins:**
- `/reflexion:memorize` - Captures insights from self-refinement cycles [[docs/getting-started.md:81-88]]().
- `/kaizen:*` - Documents root causes and improvement patterns [[.claude-plugin/marketplace.json:89-98]]().
- `/tech-stack:add-*` - Records language-specific best practices [[.claude-plugin/marketplace.json:122-131]]().
- `/mcp:setup-*` - Configures external tool integrations [[.claude-plugin/marketplace.json:133-142]]().
- `/ddd:setup-*` - Establishes architectural constraints [[.claude-plugin/marketplace.json:67-76]]().

**Sources:** [README.md:95-98](), [docs/getting-started.md:81-88]()

## External Integrations

The Context Engineering Kit integrates with external systems to enhance plugin capabilities beyond the base Claude Code functionality.

### GitHub and CI/CD Integration

The `git` plugin provides commands for GitHub operations [[.claude-plugin/marketplace.json:34-43]]():

| Command | Function | GitHub CLI Dependency |
|---------|----------|----------------------|
| `/git:commit` | Conventional commits with emoji | `git` |
| `/git:create-pr` | Create PRs with templates | `gh pr create` |
| `/git:analyze-issue` | Generate technical specs from issues | `gh issue view` |
| `/git:load-issues` | Batch load open issues as markdown | `gh issue list` |

**CI/CD Usage:** The `code-review` plugin can be automated via GitHub Actions for automated PR reviews [[docs/guides/pr-review.md:7-9]]().

**Sources:** [.bin/install-commands.sh:202-213](), [docs/guides/pr-review.md:1-24]()

### MCP (Model Context Protocol) Integration

The `mcp` plugin configures external context servers [[.claude-plugin/marketplace.json:133-142]]():

```mermaid
graph TB
    subgraph "MCP_Plugin_Commands"
        SetupContext7["/mcp:setup-context7-mcp"]
        SetupSerena["/mcp:setup-serena-mcp"]
        SetupCodemap["/mcp:setup-codemap-cli"]
        SetupPaper["/mcp:setup-arxiv-mcp"]
        BuildCustom["/mcp:build-mcp"]
    end
    
    subgraph "MCP_Servers"
        Context7["Context7<br/>Real-time library docs"]
        Serena["Serena<br/>Semantic code analysis"]
        Codemap["Codemap CLI<br/>Codebase visualization"]
        PaperSearch["Paper Search<br/>Academic literature"]
        Custom["Custom MCP Servers<br/>Domain-specific tools"]
    end
    
    subgraph "Enhanced_Plugins"
        SDDEnhanced["sdd plugin<br/>+ Current API docs"]
        KaizenEnhanced["kaizen plugin<br/>+ Research papers"]
        TDDEnhanced["tdd plugin<br/>+ Symbol-based tests"]
    end
    
    SetupContext7 -->|"configures in CLAUDE.md"| Context7
    SetupSerena -->|"configures in CLAUDE.md"| Serena
    SetupCodemap -->|"configures in CLAUDE.md"| Codemap
    SetupPaper -->|"configures in CLAUDE.md"| PaperSearch
    BuildCustom -->|"creates"| Custom
    
    Context7 -->|"enhances"| SDDEnhanced
    Serena -->|"enhances"| SDDEnhanced
    Serena -->|"enhances"| TDDEnhanced
    Serena -->|"enhances"| KaizenEnhanced
    Codemap -->|"enhances"| KaizenEnhanced
    PaperSearch -->|"enhances"| KaizenEnhanced
```

**Sources:** [.bin/install-commands.sh:209-209](), [.claude-plugin/marketplace.json:133-142]()

## Next Steps

To begin using the Context Engineering Kit:

1. **Installation:** Follow the [Getting Started](#1.1) guide to add the marketplace and install your first plugins.
2. **Architecture Understanding:** Review [Architecture & Design Principles](#1.2) for deeper understanding of plugin design patterns.
3. **Plugin Selection:** Browse the [Plugin Reference](#3) to identify plugins for your workflow.
4. **Workflow Integration:** Consult [Development Guides](#5) for complete workflow examples combining multiple plugins.

**Sources:** [docs/README.md:21-47]()

---

