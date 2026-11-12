<!-- source: DeepWiki mcp.deepwiki.com · repo awesome-opencode/awesome-opencode · page 9 Glossary · fetched 2026-10-30 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/generate-readme.yml](.github/workflows/generate-readme.yml)
- [README.md](README.md)
- [data/agents/gem-team.yaml](data/agents/gem-team.yaml)
- [data/plugins/opencode-mystatus.yaml](data/plugins/opencode-mystatus.yaml)
- [data/resources/akephalos.yaml](data/resources/akephalos.yaml)
- [data/schema.json](data/schema.json)
- [dist/registry.json](dist/registry.json)
- [docs/schema-design.md](docs/schema-design.md)
- [scripts/export-json.js](scripts/export-json.js)
- [scripts/generate-readme.js](scripts/generate-readme.js)
- [scripts/utils/template.js](scripts/utils/template.js)

</details>



This glossary provides definitions for codebase-specific terms, technical jargon, and domain concepts used within the `awesome-opencode` repository. It serves as a reference for onboarding engineers to understand how data is structured, processed, and transformed into user-facing artifacts.

## Core Concepts

### Agent
A custom AI configuration or "skill" that defines specific behaviors, tools, and instructions for specialized tasks within OpenCode [docs/schema-design.md:74-77](). Agents are defined by YAML files in `data/agents/` and often include `SKILL.md` instruction sets [docs/schema-design.md:80-81](). Examples include the `gem-team` orchestrator [data/agents/gem-team.yaml:1-5]().

### Category
A top-level classification of an entry based on its directory location within `data/`. The system recognizes six primary categories: `plugins`, `themes`, `agents`, `projects`, `resources`, and `forks` [docs/schema-design.md:23-35](). The build scripts specifically iterate through `plugins`, `themes`, `agents`, `projects`, and `resources` [scripts/export-json.js:14](), [scripts/generate-readme.js:16]().

### Entry
A single record representing an extension, tool, or resource. Each entry is stored as an individual YAML file within a category subdirectory [docs/schema-design.md:9-10]().

### Fork
Modified builds of OpenCode itself with custom features or patches, stored in `data/forks/` [docs/schema-design.md:115-117]().

### Plugin
A JavaScript or TypeScript module that extends OpenCode's core functionality [docs/schema-design.md:48-50](). Unlike projects, plugins are typically installed directly into OpenCode's internal plugin directories or via npm [docs/schema-design.md:52-54]().

### ProductId
A unique identifier for an entry, used primarily in the machine-readable `registry.json`. It is derived from the source YAML filename (e.g., `opencode-mystatus.yaml` becomes `opencode-mystatus`) [scripts/export-json.js:25-33]().

### Scope
Defines where an extension can be installed. The schema supports `global` (user-wide configuration in `~/.config/opencode/`) and `project` (scoped to a specific repository in `.opencode/`) [data/schema.json:29-38]().

## Technical Terms & Jargon

### Artifact Generation
The process of running scripts to transform YAML source data into output files. This includes generating `README.md` via `scripts/generate-readme.js` and `dist/registry.json` via `scripts/export-json.js` [.github/workflows/generate-readme.yml:49-50]().

### Kebab-Case
The naming convention for YAML files in the `data/` directory (e.g., `opencode-mystatus.yaml`). The `productId` is derived directly from this filename [scripts/export-json.js:26-28]().

### MCP (Model Context Protocol)
A protocol used by certain resources to provide external data or tools to AI models. MCP servers are categorized under `resources` [docs/schema-design.md:100-103](). An example is `akephalos`, which provides a local-first markdown passport [data/resources/akephalos.yaml:1-16]().

### Slugify
A utility function used during the export process to convert human-readable names into URL-friendly strings if a filename is unavailable [scripts/export-json.js:30-31]().

## System Data Flow

The following diagram illustrates how natural language data provided by contributors in YAML files flows through the build system to become code-ready JSON and human-readable Markdown.

**Data Transformation Pipeline**
```mermaid
graph TD
    subgraph "Natural_Language_Space_(Input)"
        ["data/{category}/*.yaml"] --> YAML
        ["templates/README.template.md"] --> README_TMPL
    end

    subgraph "Code_Entity_Space_(Processing)"
        YAML --> ["scripts/utils/validation.js"]
        ["scripts/utils/validation.js"] -- "If Valid" --> ["scripts/generate-readme.js"]
        ["scripts/utils/validation.js"] -- "If Valid" --> ["scripts/export-json.js"]
        README_TMPL --> ["scripts/generate-readme.js"]
    end

    subgraph "Artifact_Space_(Output)"
        ["scripts/generate-readme.js"] --> ["README.md"]
        ["scripts/export-json.js"] --> ["dist/registry.json"]
    end
```
Sources: [scripts/export-json.js:11-12](), [scripts/generate-readme.js:1-40](), [.github/workflows/generate-readme.yml:49-50]()

## Implementation Mapping

This diagram bridges the conceptual "Entry Types" to the specific code logic that handles them during the export and validation phases.

**Entity Logic Mapping**
```mermaid
graph LR
    subgraph "Conceptual_Type"
        ["Plugin"] --> P
        ["Agent"] --> A
        ["Resource"] --> R
    end

    subgraph "Code_Entity:_scripts/export-json.js"
        P & A & R --> ["mapEntry()"]
        ["mapEntry()"] --> ["buildProductId()"]
        ["mapEntry()"] --> ["sanitizeArray()"]
    end

    subgraph "Code_Entity:_data/schema.json"
        ["mapEntry()"] -- "Validates Against" --> ["required: [name, repo, tagline, description]"]
        ["sanitizeArray()"] -- "Defaults to" --> ["enum: [global, project]"]
    end
```
Sources: [scripts/export-json.js:25-63](), [data/schema.json:61-63](), [data/schema.json:33-34]()

## Key Field Definitions

| Field | Implementation Detail | Source |
| :--- | :--- | :--- |
| `name` | Human-readable display name. | [data/schema.json:8-12]() |
| `repo` | Must be a valid URI (usually GitHub). | [data/schema.json:13-17]() |
| `tagline` | Max 120 characters; used for collapsed views in README. | [data/schema.json:18-23]() |
| `min_version` | Validated via SemVer regex pattern `^[0-9]+\.[0-9]+\.[0-9]+`. | [data/schema.json:46-50]() |
| `type` | **Derived** from the directory name during export. | [scripts/export-json.js:50]() |
| `productId` | **Derived** from the filename (`_fileName`) during export. | [scripts/export-json.js:43-49]() |

Sources: [data/schema.json:1-64](), [scripts/export-json.js:42-63]()