<!-- source: DeepWiki mcp.deepwiki.com · repo redis/agent-skills · page 4 Plugin Integrations · fetched 2026-10-27 -->

# Plugin Integrations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [.cursor-plugin/marketplace.json](.cursor-plugin/marketplace.json)
- [README.md](README.md)

</details>



The `redis/agent-skills` repository serves as a centralized hub for Redis development best practices, which are distributed to various AI coding assistants through specialized plugin architectures. While the `skills/` directory remains the primary source of truth for the rule content, the repository provides integration manifests and structural layouts required by Cursor and Claude Code.

### Plugin Architecture Overview

The integration strategy relies on mapping the core skill content—specifically the `AGENTS.md` and `SKILL.md` files—into the specific directory structures and metadata formats expected by different AI platforms. This is managed through top-level configuration directories and automated validation scripts to ensure path safety and manifest integrity.

The following diagram illustrates how the core code entities in the `skills/` directory are mapped to the platform-specific plugin manifests.

**Skill-to-Plugin Mapping**
```mermaid
graph TD
    subgraph "Code Entity Space (Source)"
        [SKILL_DIR] --> [AGENTS_MD_FILE]
        [SKILL_DIR] --> [SKILL_MD_FILE]
        [SKILL_DIR] --> [PLUGIN_JSON]
    end

    subgraph "Natural Language Space (Platforms)"
        [CURSOR_IDE]
        [CLAUDE_CODE]
    end

    [SKILL_DIR] -- "referenced by" --> [CURSOR_MARKETPLACE_JSON]
    [CURSOR_MARKETPLACE_JSON] -- "defines" --> [CURSOR_IDE]
    
    [SKILL_DIR] -- "symlinked in" --> [CLAUDE_PLUGIN_DIR]
    [CLAUDE_PLUGIN_DIR] -- "referenced by" --> [CLAUDE_MARKETPLACE_JSON]
    [CLAUDE_MARKETPLACE_JSON] -- "defines" --> [CLAUDE_CODE]

    style [SKILL_DIR] stroke-dasharray: 5 5
```
Sources: [README.md:38-38](), [.cursor-plugin/marketplace.json:10-15](), [.claude-plugin/marketplace.json:13-14]()

---

### Cursor Plugin Integration

Cursor integration is facilitated through the `.cursor-plugin/` directory. It uses a centralized `marketplace.json` to define the available plugins and their metadata. Each skill within the `skills/` directory (e.g., `redis-development`) contains its own `.cursor-plugin/plugin.json` manifest which specifies the rules and files Cursor should ingest.

Key components include:
*   **Marketplace Registry**: Located at [.cursor-plugin/marketplace.json:1-22](), it defines the plugin owner and lists the `redis-development` plugin.
*   **Skill Manifest**: Found within the skill's own directory, providing the fine-grained configuration for Cursor's rule engine.

For details on manifest schemas and path safety, see [Cursor Plugin](#4.1).

---

### Claude Code Plugin Integration

Claude Code integration utilizes the `.claude-plugin/` directory. Unlike Cursor, which points directly to the `skills/` root, the Claude Code marketplace points to a dedicated `plugins/` directory. This directory contains symlinks back to the primary `skills/` content to avoid duplication while satisfying Claude's expected directory structure.

Key components include:
*   **Marketplace Registry**: Located at [.claude-plugin/marketplace.json:1-21](), it points the `source` field to the `./plugins/` path.
*   **Symlink Strategy**: The `plugins/redis-development` folder symlinks the necessary files from `skills/redis-development` to maintain a single source of truth.

For details on the symlink structure and Claude-specific manifests, see [Claude Code Plugin](#4.2).

---

### Plugin Validation Logic

To maintain repository integrity, automated scripts validate the plugin configurations during the CI/CD pipeline. These scripts ensure that all paths referenced in the marketplace and plugin manifests are safe, exist on disk, and follow the repository's security constraints.

**Validation Workflow**
```mermaid
graph LR
    [validate_cursor_plugins_mjs] -- "checks" --> [CURSOR_MARKETPLACE_JSON]
    [validate_claude_plugins_mjs] -- "checks" --> [CLAUDE_MARKETPLACE_JSON]
    
    subgraph "Validation Functions"
        [isSafeRelativePath]
        [validatePluginManifest]
        [extractPathValues]
    end

    [validate_cursor_plugins_mjs] --> [validatePluginManifest]
    [validate_claude_plugins_mjs] --> [validatePluginManifest]
    [validatePluginManifest] --> [isSafeRelativePath]
```
Sources: [README.md:69-69]()

The validation process involves:
1.  **Entry Point**: `main()` functions in platform-specific scripts.
2.  **Path Extraction**: Using `extractPathValues()` to find all file references.
3.  **Safety Checks**: Using `isSafeRelativePath()` to prevent directory traversal attacks or out-of-bounds references.

For a detailed reference of the validation scripts and their exit codes, see [Plugin Validation Scripts](#4.3).

---

