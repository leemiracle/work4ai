<!-- source: DeepWiki mcp.deepwiki.com · repo affaan-m/everything-claude-code · page 9 Configuration Guide · fetched 2026-10-26 -->

# Configuration Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude/rules/node.md](.claude/rules/node.md)
- [AGENTS.md](AGENTS.md)
- [COMMANDS-QUICK-REF.md](COMMANDS-QUICK-REF.md)
- [EVALUATION.md](EVALUATION.md)
- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [REPO-ASSESSMENT.md](REPO-ASSESSMENT.md)
- [WORKING-CONTEXT.md](WORKING-CONTEXT.md)
- [agent.yaml](agent.yaml)
- [commands/auto-update.md](commands/auto-update.md)
- [commands/jira.md](commands/jira.md)
- [docs/zh-CN/AGENTS.md](docs/zh-CN/AGENTS.md)
- [docs/zh-CN/README.md](docs/zh-CN/README.md)
- [manifests/install-modules.json](manifests/install-modules.json)
- [scripts/auto-update.js](scripts/auto-update.js)
- [skills/jira-integration/SKILL.md](skills/jira-integration/SKILL.md)
- [tests/ci/agent-yaml-surface.test.js](tests/ci/agent-yaml-surface.test.js)
- [tests/scripts/auto-update.test.js](tests/scripts/auto-update.test.js)

</details>



This page documents the configuration system for Everything Claude Code (ECC), including directory structure, settings files, package manager detection, MCP configuration, and project-specific overrides. ECC uses a multi-layered configuration approach where global user settings are merged with or overridden by project-level definitions.

---

## Directory Structure

ECC uses a multi-layered directory hierarchy with user-level (`~/.claude/`) and project-level (`.claude/`) configurations. The system is designed to be portable across different AI agent harnesses like Claude Code, Cursor, and OpenCode.

### Directory Hierarchy Diagram

```mermaid
graph TB
    subgraph ["User-Level: ~/.claude/"]
        UserConfig["settings.json"]
        UserMCP["~/.claude.json<br/>(MCP servers)"]
        UserSessions["sessions/<br/>(session files)"]
        UserSkills["skills/<br/>(workflow definitions)"]
        UserAgents["agents/<br/>(subagent definitions)"]
        UserCommands["commands/<br/>(slash commands)"]
        UserRules["rules/<br/>(always-follow guidelines)"]
        UserLearned["skills/learned/<br/>(generated skills)"]
        UserInstincts["homunculus/<br/>(learned patterns)"]
        UserPM["package-manager.json<br/>(global PM preference)"]
        UserState["ecc/state.db<br/>(SQLite State Store)"]
    end
    
    subgraph ["Project-Level: .claude/"]
        ProjSettings[".claude/settings.json<br/>(project overrides)"]
        ProjPM[".claude/package-manager.json<br/>(project PM)"]
        ProjRules[".claude/rules/<br/>(project-specific rules)"]
        ProjContexts[".claude/contexts/<br/>(dev.md, research.md)"]
    end
    
    subgraph ["Plugin System"]
        PluginManifest[".claude-plugin/plugin.json"]
        PluginMarketplace[".claude-plugin/marketplace.json"]
    end
    
    UserConfig -->|merged with| ProjSettings
    UserPM -->|overridden by| ProjPM
    UserRules -->|augmented by| ProjRules
    PluginManifest -->|references| UserSkills
    PluginManifest -->|references| UserAgents
    PluginManifest -->|references| UserCommands
```

**Sources:** [README.md:224-235](), [README.zh-CN.md:224-235](), [manifests/install-modules.json:83-108](), [WORKING-CONTEXT.md:146-157](), [docs/zh-CN/AGENTS.md:148-157]()

For a detailed breakdown of each directory's role and specific file patterns, see [Directory Structure](#9.1).

---

## Settings Configuration

The primary configuration file is `~/.claude/settings.json`, which governs hook behavior, plugin activation, and marketplace sources.

### settings.json Structure Diagram

```mermaid
graph LR
    subgraph ["settings.json Schema"]
        Root["settings.json"]
        Hooks["hooks: {}<br/>(event-driven automations)"]
        DisabledMCP["disabledMcpServers: []<br/>(per-project MCP blacklist)"]
        EnabledPlugins["enabledPlugins: {}<br/>(plugin activation map)"]
        Marketplaces["extraKnownMarketplaces: {}<br/>(marketplace sources)"]
    end
    
    Root --> Hooks
    Root --> DisabledMCP
    Root --> EnabledPlugins
    Root --> Marketplaces
    
    Hooks -->|auto-loaded| HooksJson["hooks/hooks.json"]
    DisabledMCP -->|overrides| UserMCP["~/.claude.json"]
    EnabledPlugins -->|activates| PluginComp["Plugin components"]
    Marketplaces -->|adds| GitHubSrc["GitHub repos"]
```

**Sources:** [README.zh-CN.md:172-204](), [README.md:87-103](), [WORKING-CONTEXT.md:39-46](), [manifests/install-modules.json:63-81]()

For details on schema properties and hook registration, see [Settings Configuration](#9.2).

---

## Context Window Management

MCP servers consume significant context window space by injecting tool descriptions. Excessive MCPs can degrade the effective context window from 200k tokens down to ~70k, leading to performance issues in large refactorings.

### Context Optimization Strategies

| Strategy | Implementation | Purpose |
|----------|----------------|---------|
| **MCP Discipline** | 5-10 enabled MCPs | Prevent tool definition bloat |
| **Selective Install** | `install-plan.js` | Install only required modules |
| **Modular Files** | Coding Style Rule | Keep files under 800 lines |
| **mgrep** | `mgrep` tool | Targeted codebase searching |
| **Strategic Compaction**| `strategic-compact` | Manage session history bloat |

**Sources:** [AGENTS.md:79-79](), [AGENTS.md:141-142](), [README.md:74-80](), [README.zh-CN.md:72-78](), [manifests/install-modules.json:216-216]()

For optimization strategies and detailed token management, see [Context Window Management](#9.3).

---

## MCP Server Configuration

MCP (Model Context Protocol) servers are configured in `~/.claude.json`. This file defines the external tools available to Claude, such as GitHub, Supabase, or local filesystem tools.

### MCP Configuration Mapping

```mermaid
graph TD
    subgraph ["Code Entity Space"]
        MCPConfig["~/.claude.json"]
        GitHubMCP["@modelcontextprotocol/server-github"]
        SupabaseMCP["@supabase/mcp-server-supabase"]
        McpPatterns["skills/mcp-server-patterns"]
        JiraMCP["mcp-atlassian"]
    end

    subgraph ["Natural Language Space"]
        UserReq["'Search my GitHub repos'"]
        SystemCap["Capability: External Data Access"]
    end

    UserReq --> SystemCap
    SystemCap --> MCPConfig
    MCPConfig --> GitHubMCP
    MCPConfig --> SupabaseMCP
    MCPConfig --> JiraMCP
    McpPatterns -->|guides| MCPConfig
```

**Sources:** [README.md:37-39](), [manifests/install-modules.json:142-142](), [skills/jira-integration/SKILL.md:30-45](), [commands/jira.md:82-84]()

For server definitions and API key setup, see [MCP Server Configuration](#9.4).

---

## Continuous Learning Configuration

Continuous Learning v2 is governed by a `config.json` structure that controls the observation daemon and the evolution of "instincts" into "skills."

### Learning Pipeline Entities

| Setting | Code Reference | Purpose |
|---------|----------------|---------|
| `observer.enabled` | `observer.enabled` | Toggles the background analysis daemon |
| `interval` | `run_interval_minutes` | Frequency of pattern detection loops |
| `threshold` | `min_observations_to_analyze` | Minimum data points before analysis |
| `path` | `learned_skills_path` | Target for evolved `.md` skills |
| `evolution` | `/evolve` command | Trigger for instinct-to-skill conversion |

**Sources:** [README.md:76-76](), [README.zh-CN.md:147-147](), [WORKING-CONTEXT.md:38-46](), [manifests/install-modules.json:207-208]()

For details on the evolution pipeline and instinct management, see [Continuous Learning Configuration](#9.5).

---

## Project-Specific Configuration

ECC supports project-level overrides through a `.claude/` directory. This allows for specific package manager settings and "Context Modes" (named markdown files that shift agent behavior).

### Project Override Logic

```mermaid
graph LR
    subgraph ["Global (~/.claude)"]
        GlobalPM["package-manager.json"]
        GlobalRules["rules/common/"]
    end

    subgraph ["Project (.claude)"]
        ProjPM[".claude/package-manager.json"]
        ProjRules[".claude/rules/"]
        ProjContexts["contexts/dev.md"]
    end

    GlobalPM -->|Overridden by| ProjPM
    GlobalRules -->|Augmented by| ProjRules
    ProjContexts -->|Shifts| AgentBehavior["Agent Instructions"]
```

**Sources:** [README.zh-CN.md:176-204](), [README.md:180-184](), [AGENTS.md:112-116]()

For details on project-scoped rules and detection, see [Project-Specific Configuration](#9.6).

---

## State Store & SQLite Persistence

ECC maintains a persistent state store in SQLite at `~/.claude/ecc/state.db`. This database tracks session metadata, skill performance, and governance events across different platforms.

### State Store Schema Entities

```mermaid
graph TD
    subgraph ["SQLite: state.db"]
        SessionTable["session<br/>(id, alias, path, metadata)"]
        SkillRunTable["skillRun<br/>(id, skill_id, status, duration)"]
        DecisionTable["decision<br/>(id, agent_id, reasoning, outcome)"]
        GovernanceTable["governanceEvent<br/>(id, hook_id, action)"]
        InstallState["installState<br/>(module_id, version, target)"]
    end

    SessionTable --- SkillRunTable
    SkillRunTable --- DecisionTable
    GovernanceTable --- InstallState
```

**Sources:** [README.md:96-101](), [WORKING-CONTEXT.md:12-16](), [manifests/install-modules.json:1-3](), [docs/zh-CN/README.md:89-89](), [tests/scripts/auto-update.test.js:17-20]()

For database schema details and CLI usage, see [State Store & SQLite Persistence](#9.7).

---

