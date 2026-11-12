<!-- source: DeepWiki mcp.deepwiki.com · repo k-kolomeitsev/data-structure-protocol · page 7 Installation · fetched 2026-10-27 -->

# Installation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [hooks/install-hooks.ps1](hooks/install-hooks.ps1)
- [hooks/install-hooks.sh](hooks/install-hooks.sh)
- [install.ps1](install.ps1)
- [install.sh](install.sh)

</details>



The Data Structure Protocol (DSP) provides automated installation scripts to streamline the setup of AI agent skills and repository-level enforcement hooks. Installation is divided into two primary components: the **Skill Installer**, which provides the LLM with the DSP "brain," and the **Hook Installer**, which ensures graph consistency via Git lifecycle events.

### Installation Architecture

The following diagram illustrates how the installation scripts bridge the gap between the remote repository and your local development environment.

**Installation Flow: Remote to Local Agent/Git Space**
```mermaid
graph TD
    subgraph "Remote (GitHub)"
        [Repo] --> [install.sh/ps1]
        [Repo] --> [install-hooks.sh/ps1]
    end

    subgraph "Local Codebase (Natural Language Space)"
        [install.sh/ps1] -- "Downloads Skill" --> [Agent_Skills_Dir]
        [install-hooks.sh/ps1] -- "Copies Hooks" --> [Git_Hooks_Dir]
    end

    subgraph "Code Entity Space (Implementation)"
        [Agent_Skills_Dir] --> ".cursor/skills/data-structure-protocol"
        [Agent_Skills_Dir] --> ".claude/skills/data-structure-protocol"
        [Agent_Skills_Dir] --> ".codex/skills/data-structure-protocol"
        [Git_Hooks_Dir] --> ".git/hooks/pre-commit"
        [Git_Hooks_Dir] --> ".git/hooks/pre-push"
    end
```
**Sources:** [install.ps1:13-32](), [install.sh:43-60](), [hooks/install-hooks.sh:4-13]()

---

### Skill Installation

The main installer scripts (`install.sh` for Unix-like systems and `install.ps1` for Windows) are designed to deploy the DSP skill to specific AI agents. These scripts automate the download, extraction, and placement of the protocol definition files into the directories where agents like Cursor, Claude Code, and Codex expect to find them.

The installer supports three primary parameters:
- **Agent Targeting**: You can specify `cursor`, `claude`, `codex`, or `all` to target specific tools [install.ps1:4-5](), [install.sh:14]().
- **Global vs Local**: By default, skills are installed locally within the current project. The `--global` (or `$Global`) flag redirects installation to the user's home directory (e.g., `~/.cursor/skills/`) to make DSP available across all projects [install.ps1:19-24](), [install.sh:46-51]().
- **Branch Selection**: The `--branch` parameter allows users to install from `main` or experimental development branches [install.ps1:9](), [install.sh:18]().

For detailed usage instructions and a breakdown of the `Install-ForAgent` logic, see **[Skill Installation (install.sh / install.ps1)](#7.1)**.

**Sources:** [install.ps1:3-10](), [install.ps1:34-65](), [install.sh:8-27](), [install.sh:62-79]()

---

### Hook Installation

While the skill allows the agent to read and write the DSP graph, the Git hooks ensure that the graph remains healthy and synchronized with the actual source code. The hook installers (`hooks/install-hooks.sh` and `hooks/install-hooks.ps1`) locate the local `.git` directory and install scripts that run during `git commit` and `git push` events.

**Hook Deployment Logic**
```mermaid
graph LR
    subgraph "Installer Logic"
        [git_rev_parse] -- "Locates" --> [hooksDir]
        [SCRIPT_DIR] -- "Source" --> [pre_commit_script]
    end

    subgraph "Git Lifecycle"
        [hooksDir] --> [pre_commit]
        [hooksDir] --> [pre_push]
    end

    subgraph "Environment Configuration"
        [pre_commit] -. "Reads" .-> [DSP_PRECOMMIT_MODE]
        [pre_commit] -. "Reads" .-> [DSP_SKIP_PATTERNS]
    end
```
**Sources:** [hooks/install-hooks.ps1:3-9](), [hooks/install-hooks.sh:4-13]()

These hooks are configurable via environment variables:
- `DSP_PRECOMMIT_MODE`: Set to `warn` (default) or `block` to determine if consistency errors should stop a commit [hooks/install-hooks.sh:18]().
- `DSP_SKIP_PATTERNS`: A comma-separated list of globs to ignore during validation [hooks/install-hooks.sh:20]().

For configuration details and environment variable mapping, see **[Hook Installation (install-hooks.sh / install-hooks.ps1)](#7.2)**.

**Sources:** [hooks/install-hooks.ps1:13-16](), [hooks/install-hooks.sh:16-21]()

---

### Installation Methods Summary

| Method | Target | Command (Unix) | Command (Windows) |
| :--- | :--- | :--- | :--- |
| **Local Skill** | Current Project | `./install.sh` | `.\install.ps1` |
| **Global Skill** | User Home | `./install.sh --global` | `.\install.ps1 -Global` |
| **Git Hooks** | `.git/hooks/` | `./hooks/install-hooks.sh` | `.\hooks\install-hooks.ps1` |

**Sources:** [install.sh:21-25](), [install.ps1:3-10](), [hooks/install-hooks.sh:7-15](), [hooks/install-hooks.ps1:6-11]()

---

