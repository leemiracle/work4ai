<!-- source: DeepWiki mcp.deepwiki.com · repo fathah/hermes-desktop · page 9 Agent Skills and Developer Context · fetched 2026-10-30 -->

# Agent Skills and Developer Context

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude/settings.json](.claude/settings.json)
- [.claude/skills/lat-md/SKILL.md](.claude/skills/lat-md/SKILL.md)
- [CLAUDE.md](CLAUDE.md)
- [lat.md/.cache/lat_init.json](lat.md/.cache/lat_init.json)
- [lat.md/model-context.md](lat.md/model-context.md)

</details>



This page documents the internal agent skill definitions and reference materials located in the `.agents/` and `.claude/` directories. These resources provide the Hermes agent with the specialized domain knowledge required to maintain, develop, and troubleshoot the Hermes Desktop codebase itself, specifically utilizing the `lat.md` documentation framework.

## Overview of Agent Context

The codebase includes bundled skill definitions that act as a "manual" for the AI agent. These skills bridge the gap between high-level requirements and specific implementation patterns used in this repository.

### Skill Directories
- **`.agents/skills/`**: Contains active skill definitions including `SKILL.md` files, reference configurations, and diagnostic scripts.
- **`.claude/skills/`**: Specialized versions of skills and context optimized for the Claude agent environment, such as `lat-md` [.claude/skills/lat-md/SKILL.md:1-7]().
- **`lat.md/`**: A structured knowledge graph describing the "what" and "why" of the project's architecture and design decisions [CLAUDE.md:16-18]().

---

## Bundled Skill Ecosystem

The agent utilizes several primary skill sets to manage the desktop application and its documentation:

### 1. Architecture Documentation (`lat-md`)
This skill governs the creation and maintenance of `lat.md/` files. It enforces a strict structure where every section must have a leading paragraph of ≤250 characters [.claude/skills/lat-md/SKILL.md:29-34](). It enables the agent to cross-reference source code with documentation using wiki links like `[[src/main/models.ts#ModelDefinition]]` [lat.md/model-context.md:11-11]() and validates these links using the `lat check` command [.claude/skills/lat-md/SKILL.md:165-169]().

### 2. Electron Professional (`electron-pro`)
Focuses on the desktop-specific architecture of the app. It defines the "Security First" approach, mandating `contextIsolation` and prohibiting `nodeIntegration` in the renderer process. It provides patterns for IPC communication using `ipcRenderer.invoke` for request/response and `ipcMain.handle` for main-process logic.

### 3. Hermes Agent Core (`hermes-agent`)
Provides the comprehensive reference for the underlying Python-based Hermes engine. This skill documents the core architecture, including tool orchestration and the session database logic. It is essential for the agent to understand how the Desktop frontend interacts with the backend gateway.

### 4. TypeScript Expert (`typescript-expert`)
Ensures code quality through strict type safety and performance optimization. It guides the agent on using branded types for domain modeling and advanced conditional types.

For deep technical details on these definitions, see **[Bundled Skill Definitions](#9.1)**.

**Sources:** [.claude/skills/lat-md/SKILL.md:1-7](), [CLAUDE.md:16-28](), [lat.md/model-context.md:11-15]()

---

## Knowledge Mapping: Natural Language to Code Entities

The following diagrams illustrate how the agent maps high-level development concepts to specific code entities and documentation patterns within the Hermes Desktop environment.

### Diagram 1: Documentation and Code Correlation
This diagram bridges the conceptual "Architecture Knowledge" to the actual `lat.md` implementation and code-tagging patterns.

```mermaid
graph TD
    subgraph "NaturalLanguageSpace" ["Natural Language Space"]
        "ArchIntent"["Architectural Intent"]
        "DesignRationale"["Design Rationale"]
        "TestSpecs"["Test Specifications"]
    end

    subgraph "CodeEntitySpace" ["Code Entity Space"]
        "lat_md_files"["lat.md/*.md Files"]
        "wiki_links"["[[path/to/file#Symbol]]"]
        "lat_comments"["// @lat: [[section-id]]"]
        "lat_check"["lat check (Validation)"]
    end

    "ArchIntent" --> "lat_md_files"
    "DesignRationale" --> "lat_md_files"
    "lat_md_files" -- "references" --> "wiki_links"
    "wiki_links" -- "targets" --> "CodeEntitySpace"
    "lat_comments" -- "links back to" --> "lat_md_files"
    "TestSpecs" -- "enforced by" --> "lat_check"
```
**Sources:** [.claude/skills/lat-md/SKILL.md:57-80](), [.claude/skills/lat-md/SKILL.md:92-109](), [CLAUDE.md:34-40]()

### Diagram 2: Context Management Logic
This diagram shows how the agent understands the relationship between model definitions and the UI context gauge.

```mermaid
graph LR
    subgraph "NaturalLanguageSpace" ["Natural Language Space"]
        "ContextOverride"["Context Window Override"]
        "AutoCompaction"["Agent Auto-Compaction"]
        "OccupancyEstimate"["Gauge Occupancy Estimate"]
    end

    subgraph "CodeEntitySpace" ["Code Entity Space"]
        "model_defs"["model-definitions.json"]
        "setModelConfig"["setModelConfig()"]
        "getModelContextWindow"["getModelContextWindow()"]
        "estimateContextTokens"["estimateContextTokens()"]
    end

    "ContextOverride" --> "model_defs"
    "model_defs" --> "getModelContextWindow"
    "ContextOverride" --> "setModelConfig"
    "AutoCompaction" -- "triggered by" --> "getModelContextWindow"
    "OccupancyEstimate" --> "estimateContextTokens"
```
**Sources:** [lat.md/model-context.md:9-15](), [lat.md/model-context.md:17-22](), [lat.md/model-context.md:27-29]()

---

## Developer Utility References

The agent relies on specific tools and lifecycle hooks to maintain the integrity of the documentation and codebase.

| Tool / Resource | Role |
| :--- | :--- |
| `lat search` | Semantic search across all architecture sections to find relevant context [CLAUDE.md:25-25]() |
| `lat check` | Validates that all wiki links and `@lat` code references are valid [.claude/skills/lat-md/SKILL.md:165-169]() |
| `lat expand` | Resolves `[[refs]]` in user prompts to full file locations for the agent [CLAUDE.md:26-26]() |
| `UserPromptSubmit` | Hook that triggers `lat hook claude` to inject context before processing prompts [.claude/settings.json:3-9]() |
| `model-definitions.json` | Centralized storage for `contextLength` and model capabilities [lat.md/model-context.md:11-13]() |

**Sources:** [CLAUDE.md:22-32](), [.claude/skills/lat-md/SKILL.md:163-169](), [.claude/settings.json:1-24](), [lat.md/model-context.md:1-15]()

---

