<!-- source: DeepWiki mcp.deepwiki.com · repo wanshuiyin/Auto-claude-code-research-in-sleep · page 6 Configuration & Setup · fetched 2026-10-26 -->

# Configuration & Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SETUP_GUIDE.md](SETUP_GUIDE.md)
- [SETUP_GUIDE_CN.md](SETUP_GUIDE_CN.md)
- [tests/test_install_aris_selective.py](tests/test_install_aris_selective.py)
- [tests/test_install_aris_tools_symlink.py](tests/test_install_aris_tools_symlink.py)
- [tests/test_skill_picker.py](tests/test_skill_picker.py)
- [tools/install_aris.sh](tools/install_aris.sh)
- [tools/install_aris_codex.sh](tools/install_aris_codex.sh)
- [tools/install_aris_copilot.sh](tools/install_aris_copilot.sh)
- [tools/skill_picker.py](tools/skill_picker.py)
- [tools/smart_update_codex.sh](tools/smart_update_codex.sh)
- [tools/smart_update_copilot.sh](tools/smart_update_copilot.sh)

</details>



This page provides step-by-step instructions for configuring ARIS from scratch. It covers configuration files, required dependencies, optional integrations, and verification procedures. ARIS follows a a "graceful degradation" philosophy—skills automatically detect missing integrations and skip optional features without failing.

---

## Overview of Configuration Requirements

ARIS has a tiered configuration model. Core execution requires **Claude Code** (the Executor) and the **Codex MCP** (the Reviewer). Workflow 3 adds LaTeX requirements, while optional integrations (Zotero, Feishu, etc.) enhance research capabilities. The system is designed to be "radically lightweight," with zero required databases or complex daemons.

**Diagram: Configuration Dependency Tiers**

```mermaid
graph TB
    subgraph "Tier1:Core(Required)"
        [ClaudeCodeCLI] --> [SkillsDirectory]
        [CodexCLI] --> [SkillsDirectory]
    end

    subgraph "Tier2:LaTeX(RequiredForW3)"
        [MacTeX/TexLive] --> [LatexmkCompiler]
        [MacTeX/TexLive] --> [PopplerUtils]
    end

    subgraph "Tier3:OptionalIntegrations"
        [ZoteroMCP]
        [ObsidianMCP]
        [FeishuConfig]
        [GPUConfig]
    end

    subgraph "ConfigurationFiles"
        [SettingsJSON]
        [SettingsLocalJSON]
    end

    [ClaudeCodeCLI] --- [SettingsJSON]
    [CodexCLI] --- [SettingsJSON]
    [SettingsLocalJSON] -.->|Auto-Allow| [ClaudeCodeCLI]

    [W1:IdeaDiscovery] --> [ClaudeCodeCLI]
    [W1:IdeaDiscovery] -.-> [ZoteroMCP]

    [W2:AutoReviewLoop] --> [ClaudeCodeCLI]
    [W2:AutoReviewLoop] -.-> [GPUConfig]

    [W3:PaperWriting] --> [ClaudeCodeCLI]
    [W3:PaperWriting] --> [MacTeX/TexLive]
```

Sources: [README.md:11-13](), [README_CN.md:27-29]()

---

## Configuration File Locations

All ARIS configuration files reside in standardized locations within the user's home directory or project directory. Note that as of v0.4.4, ARIS supports a "flat" installation mode where skills are symlinked individually into the project.

**Table: Configuration File Reference**

| File Path | Purpose | Required? | Created By |
|-----------|---------|-----------|------------|
| `~/.claude/settings.json` | MCP servers, environment variables, model mappings | Yes | User (manual edit) |
| `~/.claude/settings.local.json` | Auto-allow permissions for overnight runs | No | User (manual create) |
| `~/.claude/skills/*` | Composable skill definitions (`SKILL.md` files) | Yes | `install_aris.sh` |
| `~/.claude/feishu.json` | Feishu webhook/bridge configuration | No | User (manual create) |
| `~/.codex/config.toml` | Codex CLI OpenAI API key | Yes | `codex configure` |
| `CLAUDE.md` | GPU server SSH/conda configuration (project-level) | No | User (manual create) |
| `.aris/installed-skills.txt` | Manifest tracking managed symlinks | Yes | `install_aris.sh` |
| `REVIEW_STATE.json` | Auto-review-loop state persistence (runtime) | No | `auto-review-loop` skill |

**Diagram: System-to-Code Mapping (Configuration Entities)**

```mermaid
graph LR
    subgraph "Natural Language Space"
        "Auto-Allow Permissions"
        "MCP Server Definition"
        "GPU Credentials"
        "State Persistence"
        "Skill Manifest"
    end

    subgraph "Code Entity Space"
        "Auto-Allow Permissions" --> [settings_local_json]
        "MCP Server Definition" --> [settings_json]
        "GPU Credentials" --> [CLAUDE_md]
        "State Persistence" --> [REVIEW_STATE_json]
        "Skill Manifest" --> [installed_skills_txt]
    end

    [settings_local_json] --- "path: ~/.claude/settings.local.json"
    [settings_json] --- "path: ~/.claude/settings.json"
    [CLAUDE_md] --- "path: ./CLAUDE.md"
    [REVIEW_STATE_json] --- "path: ./REVIEW_STATE.json"
    [installed_skills_txt] --- "path: .aris/installed-skills.txt"
```

Sources: [tools/install_aris.sh:6-8](), [skills/research-pipeline/SKILL.md:12-21](), [skills/idea-discovery/SKILL.md:40-54]()

---

## Core Setup: Required Components

### 1. Claude Code Installation
Claude Code is the primary execution engine. Install via npm:
```bash
npm install -g @anthropic-ai/claude-code
```
Sources: [SETUP_GUIDE.md:13-17]()

### 2. Codex MCP Server Setup
Codex MCP enables Claude Code to invoke adversarial reviewer models (GPT-5.5/o3/gpt-4o).
```bash
# Install Codex CLI and register as MCP
codex --version   # verify installation
codex login       # one-time ChatGPT auth (skip if already logged in)
claude mcp add codex -s user -- codex mcp-server
```
Sources: [SETUP_GUIDE.md:21-31]()

### 3. Skills Installation (New Flat Mode)
ARIS uses `install_aris.sh` to create flat symlinks. This ensures Claude Code's slash-command discovery (which only scans one level deep) correctly finds all skills.
```bash
# 1. Clone ARIS once to a stable location, ~/aris_repo is the local dir name (customizable)
git clone https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep.git ~/aris_repo

# 2. Install in each project that uses ARIS (via symlinks):
cd ~/your-paper-project
bash ~/aris_repo/tools/install_aris.sh
```
Sources: [tools/install_aris.sh:4-9](), [SETUP_GUIDE.md:78-84]()

### 4. LaTeX Toolchain (Workflow 3)
Required for `/paper-write` and `/paper-compile`.
- **macOS**: `brew install --cask mactex` (or `basictex`), `brew install poppler`
- **Linux**: `sudo apt install texlive-full latexmk poppler-utils`
Sources: [SETUP_GUIDE.md:48-52]()

---

## Detailed Setup Guides (Child Pages)

For specific configurations, refer to the following sub-pages:

### [Initial Setup Checklist](#6.1)
A comprehensive verification list to ensure Claude Code, LaTeX, and Codex MCP are correctly communicating. This includes verifying MCP server connections and initializing the Research Wiki. For details, see [Initial Setup Checklist](#6.1).
Sources: [SETUP_GUIDE.md:38-42](), [SETUP_GUIDE.md:198-201]()

### [Installer & Skill Lifecycle Tooling](#6.2)
This section details the various installer scripts like `tools/install_aris.sh`, `tools/install_aris_copilot.sh`, and `tools/install_aris_codex.sh`. It covers how skills are managed (symlinks vs. copies), the role of manifest files (`.aris/installed-skills.txt`), and the safety rules (S1-S14) that prevent accidental data loss. It also explains `tools/smart_update_copilot.sh` and `tools/smart_update_codex.sh` for updating copied installations, and `tools/skill_picker.py` for interactive skill selection. For details, see [Installer & Skill Lifecycle Tooling](#6.2).
Sources: [tools/install_aris.sh:4-77](), [tools/install_aris_copilot.sh:4-60](), [tools/install_aris_codex.sh:4-50](), [tools/smart_update_copilot.sh:2-35](), [tools/smart_update_codex.sh:2-31](), [tools/skill_picker.py:1-26]()

### [Auto-Allow for Overnight Runs](#6.3)
Instructions for configuring `~/.claude/settings.local.json`. This is critical for **unattended execution**, allowing Claude to use tools like `mcp__codex__codex`, `Write`, and `Edit` without manual human approval. For details, see [Auto-Allow for Overnight Runs](#6.3).
Sources: [README.md:33-33]()

### [IDE Adaptations](#6.4)
ARIS is "radically lightweight" and can run in various AI IDEs. This section covers how to adapt ARIS for environments like Trae, Cursor, Antigravity, OpenClaw, and Copilot CLI, including rule/skill conversion, file references, and state recovery mechanisms. For details, see [IDE Adaptations](#6.4).
Sources: [README.md:11-11]()

### [Codex Skills Package](#6.5)
Documentation for the `skills-codex` package and its reviewer overlay packages (`skills-codex-gemini-review`, `skills-codex-claude-review`). This package allows using **OpenAI Codex as the executor** instead of Claude, utilizing `spawn_agent` instead of MCP orchestration. It details the differences from the Claude version, mirror tests, override generation, and installation order. For details, see [Codex Skills Package](#6.5).
Sources: [tools/install_aris_codex.sh:11-16]()

### [Templates & Project Files](#6.6)
Document the `templates/` directory used to bootstrap new projects. This includes workflow input templates, patent templates, findings/experiment-log templates, and `claude-hooks` templates (e.g., `meta_logging`, `corpus_write_guard`). It also explains how to bootstrap new projects using these templates. For details, see [Templates & Project Files](#6.6).

**Diagram: Template-to-Workflow Association**

```mermaid
graph LR
    subgraph "Input Templates"
        [RESEARCH_BRIEF_md]
        [EXPERIMENT_PLAN_md]
        [NARRATIVE_REPORT_md]
    end

    subgraph "Workflow Skills"
        [research_pipeline]
        [experiment_bridge]
        [paper_writing]
    end

    [RESEARCH_BRIEF_md] --> [research_pipeline]
    [EXPERIMENT_PLAN_md] --> [experiment_bridge]
    [NARRATIVE_REPORT_md] --> [paper_writing]
```

| Template | Target Skill | Purpose |
|----------|--------------|---------|
| `RESEARCH_BRIEF_TEMPLATE.md` | `/idea-discovery` | Detailed research direction input |
| `EXPERIMENT_PLAN_TEMPLATE.md` | `/experiment-bridge` | Claim-driven roadmap with budgets |
| `NARRATIVE_REPORT_TEMPLATE.md` | `/paper-writing` | Research narrative for Workflow 3 |

Sources: [skills/idea-discovery/SKILL.md:56-56](), [skills/research-pipeline/SKILL.md:38-38](), [skills/paper-write/SKILL.md:20-25]()

---

