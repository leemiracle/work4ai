<!-- source: DeepWiki mcp.deepwiki.com · repo OthmanAdi/planning-with-files · page 9 Platform-Specific Guides · fetched 2026-10-29 -->

# Platform-Specific Guides

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [.claude-plugin/plugin.json](.claude-plugin/plugin.json)
- [.codex/skills/planning-with-files/SKILL.md](.codex/skills/planning-with-files/SKILL.md)
- [.cursor/skills/planning-with-files/SKILL.md](.cursor/skills/planning-with-files/SKILL.md)
- [.opencode/skills/planning-with-files/SKILL.md](.opencode/skills/planning-with-files/SKILL.md)
- [CHANGELOG.md](CHANGELOG.md)
- [CITATION.cff](CITATION.cff)
- [CONTRIBUTORS.md](CONTRIBUTORS.md)
- [README.md](README.md)
- [skills/planning-with-files/SKILL.md](skills/planning-with-files/SKILL.md)

</details>



## Purpose and Scope

This section provides technical guidance for installing and configuring `planning-with-files` across 17+ different AI coding platforms and IDEs. It explains the multi-platform architecture, directory structure conventions, and platform-specific adaptations required for each system.

For installation procedures, see [Installation and Platform Support](#3.1). For hook system behavior across platforms, see [Hook System and Automation](#4.3). For detailed platform-specific instructions, see:
- [Claude Code Integration](#9.1) — Plugin system, hooks, and slash commands.
- [Cursor and Continue IDEs](#9.2) — VS Code and JetBrains integration.
- [Kilocode Integration](#9.3) — Rules system and PowerShell support.
- [Codex and OpenCode](#9.4) — Python-based hooks and session isolation.
- [Gemini CLI and Pi Agent](#9.5) — Skill configuration and platform differences.
- [Hermes Adapter](#9.6) — Python adapter and tool-based context injection.
- [Other Platforms](#9.7) — GitHub Copilot, Kiro, Mastra, and more.

## Multi-Platform Architecture

Planning-with-files achieves broad platform support through a **core-and-adapters architecture**. The core skill logic (workflow, templates, scripts) remains constant, while platform-specific adapters conform to each system's conventions.

### Core Components

```mermaid
graph TB
    subgraph "Core_Skill_Definition"
        [SKILL_md] --> ["SKILL.md (Core Workflow)"]
        [TEMPLATES] --> ["templates/ (task_plan.md, findings.md, progress.md)"]
        [SCRIPTS] --> ["scripts/ (init-session.sh/ps1, check-complete.sh/ps1, session-catchup.py)"]
    end
    
    subgraph "Platform_Adapters"
        [CLAUDE] --> [".claude-plugin/"]
        [CURSOR] --> [".cursor/skills/"]
        [KILOCODE] --> [".kilocode/rules/"]
        [KIRO] --> [".kiro/skills/"]
        [GEMINI] --> [".gemini/skills/"]
        [CONTINUE] --> [".continue/skills/"]
        [CODEX] --> [".codex/skills/"]
        [HERMES] --> [".hermes/plugins/"]
        [COPILOT] --> [".github/hooks/"]
    end
    
    [SKILL_md] --- [CLAUDE]
    [SKILL_md] --- [CURSOR]
    [SKILL_md] --- [KILOCODE]
    [SKILL_md] --- [GEMINI]
    [SKILL_md] --- [CONTINUE]
    [SKILL_md] --- [CODEX]
    
    [TEMPLATES] --- [CLAUDE]
    [TEMPLATES] --- [CURSOR]
    [TEMPLATES] --- [HERMES]
    
    [SCRIPTS] --- [CLAUDE]
    [SCRIPTS] --- [CURSOR]
    [SCRIPTS] --- [CODEX]
    [SCRIPTS] --- [COPILOT]
```

**Architecture Diagram: Core-and-Adapters Pattern**

Sources: [README.md:59-76](), [README.md:227-277](), [.claude-plugin/plugin.json:1-40]()

### Distribution Methods

The skill is distributed through three primary channels:

| Method | Platforms | Mechanism |
|--------|-----------|-----------|
| **Plugin Marketplace** | Claude Code | `claude plugins install OthmanAdi/planning-with-files` |
| **Direct Skill Add** | All Standard Platforms | `npx skills add OthmanAdi/planning-with-files` |
| **Git Clone / Manual** | All platforms | Copy platform-specific directory to user config folder |

Sources: [README.md:14-16](), [CHANGELOG.md:37-41](), [CONTRIBUTORS.md:15-19]()

## Platform Categories

Platforms are grouped by their skill system architecture:

### Standard SKILL.md Format

These platforms use the [Agent Skills specification](https://agentskills.io/specification). The canonical definition is maintained in `skills/planning-with-files/SKILL.md` [skills/planning-with-files/SKILL.md:1-27]().

| Platform | Directory | Install Location |
|----------|-----------|------------------|
| Claude Code | `.claude-plugin/` | `~/.claude/plugins/cache/planning-with-files/` |
| Cursor | `.cursor/skills/` | `~/.cursor/skills/planning-with-files/` |
| Continue | `.continue/skills/` | `~/.continue/skills/planning-with-files/` |
| OpenCode | `.opencode/skills/` | `~/.config/opencode/skills/planning-with-files/` |
| Codex | `.codex/skills/` | `~/.codex/skills/planning-with-files/` |
| Gemini CLI | `.gemini/skills/` | `~/.gemini/skills/planning-with-files/` |
| Pi Agent | `.pi/skills/` | `~/.pi/skills/planning-with-files/` |

Sources: [README.md:59-76](), [CHANGELOG.md:37-41](), [CONTRIBUTORS.md:50-55]()

### Rules-Based & Steering Systems

| Platform | Directory | Format | Notes |
|----------|-----------|--------|-------|
| Kilocode | `.kilocode/rules/` | `planning-with-files.md` | Rule-based enforcement |
| Kiro | `.kiro/skills/` | Agent Skill layout | Native steering integration |
| GitHub Copilot | `.github/hooks/` | JSON hooks + scripts | Native hook integration |

Sources: [CONTRIBUTORS.md:36-41](), [CONTRIBUTORS.md:63-69](), [CONTRIBUTORS.md:70-75]()

## Installation Path Mapping

The following diagram maps repository entities to actual filesystem paths on the user's machine:

```mermaid
graph TB
    subgraph "Repository_Entities"
        [REPO_ROOT] --> [CANONICAL_SKILL["skills/planning-with-files/SKILL.md"]]
        [REPO_ROOT] --> [SHARED_SCRIPTS["scripts/init-session.sh"]]
        [REPO_ROOT] --> [PLATFORM_DIRS[".cursor/, .codex/, .gemini/"]]
    end
    
    subgraph "User_Filesystem_Space"
        [USER_HOME] --> [CLAUDE_CACHE["~/.claude/plugins/cache/planning-with-files/"]]
        [USER_HOME] --> [CURSOR_CONFIG["~/.cursor/skills/planning-with-files/"]]
        [USER_HOME] --> [CODEX_CONFIG["~/.codex/skills/planning-with-files/"]]
        [USER_HOME] --> [GEMINI_CONFIG["~/.gemini/skills/planning-with-files/"]]
    end
    
    [CANONICAL_SKILL] -.->|"sync-ide-folders.py"| [PLATFORM_DIRS]
    [PLATFORM_DIRS] -.->|"Installation"| [USER_HOME]
    [SHARED_SCRIPTS] -.->|"init-session.sh"| [CLAUDE_CACHE]
    [SHARED_SCRIPTS] -.->|"init-session.sh"| [CURSOR_CONFIG]
```

**Diagram: Entity Mapping from Repository to User Environment**

Sources: [CHANGELOG.md:37-41](), [CHANGELOG.md:53-58](), [CONTRIBUTORS.md:107-112]()

## Skill Format Adaptations

### Standard SKILL.md Frontmatter
Most platforms utilize the YAML frontmatter defined in the canonical skill [skills/planning-with-files/SKILL.md:1-27](). This includes the `hooks` configuration for `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, and `Stop`.

### Platform-Specific Hook Resolution
Different platforms resolve script paths differently. For example:
- **Claude Code** uses `${CLAUDE_SKILL_DIR}` [skills/planning-with-files/SKILL.md:24]().
- **Cursor** uses `${CURSOR_SKILL_ROOT}` [.cursor/skills/planning-with-files/SKILL.md:24]().
- **Codex** uses `${CODEX_SKILL_ROOT}` [.codex/skills/planning-with-files/SKILL.md:24]().

## Cross-Platform Script Compatibility

Helper scripts are provided in both Bash and PowerShell to ensure compatibility across Linux, macOS, and Windows.

| Script | Bash | PowerShell | Purpose |
|--------|------|------------|---------|
| **Session Init** | `init-session.sh` | `init-session.ps1` | Initialize planning files |
| **Completion Check** | `check-complete.sh` | `check-complete.ps1` | Verify phase completion |
| **Plan Attestation** | `attest-plan.sh` | `attest-plan.ps1` | Cryptographic plan locking |
| **Recovery** | `session-catchup.py` | `session-catchup.py` | Context restoration |

Sources: [CHANGELOG.md:13-18](), [CHANGELOG.md:37-41](), [CHANGELOG.md:75-77]()

## Security and Portability

- **Execution Policy**: Windows PowerShell scripts use `RemoteSigned` instead of `Bypass` for improved security [CHANGELOG.md:76-77]().
- **Shebang Portability**: Shell scripts use `#!/usr/bin/env bash` for compatibility with NixOS and non-standard Bash locations [CHANGELOG.md:75]().
- **Plan Attestation**: The `/plan-attest` command [CHANGELOG.md:13-14]() and `attest-plan.sh` [CHANGELOG.md:14-15]() provide SHA-256 verification to prevent prompt injection via tampered planning files.

## Detailed Platform Guides

- **[Claude Code Integration](#9.1)** — Deep dive into the `plugin.json` and marketplace integration.
- **[Cursor and Continue IDEs](#9.2)** — Configuration for VS Code-based environments.
- **[Kilocode Integration](#9.3)** — Rules system and Windows-first adaptations.
- **[Codex and OpenCode](#9.4)** — Session isolation and Python hook adapters.
- **[Gemini CLI and Pi Agent](#9.5)** — Skill integration for Google and Pi ecosystems.
- **[Hermes Adapter](#9.6)** — The Python-based adapter for platform 17.
- **[Other Platforms](#9.7)** — Support for Copilot, Kiro, Mastra, and others.

Sources: [README.md:59-100](), [CHANGELOG.md:5-18](), [CHANGELOG.md:73-82]()

---

