<!-- source: DeepWiki mcp.deepwiki.com · repo awesome-opencode/awesome-opencode · page 3 Data Model · fetched 2026-10-30 -->

# Data Model

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [data/plugins/kilo-auth.yaml](data/plugins/kilo-auth.yaml)
- [data/schema.json](data/schema.json)
- [docs/schema-design.md](docs/schema-design.md)

</details>



This document defines the data model used throughout the awesome-opencode repository. It covers the YAML schema structure, field definitions, validation rules, and type derivation conventions. The data model serves as the contract between contributors who create YAML entries and downstream systems that consume the registry.

For information about how this schema is validated during the build process, see [Validation System](#5.3). For details about the structure of generated output artifacts, see [Data Layer](#2.2).

---

## Schema Architecture

The data model uses a two-tier validation system: a JSON Schema specification ([data/schema.json:1-63]()) defines structural constraints, while additional business rules are enforced programmatically during build time.

**Diagram: Schema Validation Architecture**

```mermaid
graph TB
    subgraph "Source Files"
        yaml_plugins["data/plugins/*.yaml"]
        yaml_themes["data/themes/*.yaml"]
        yaml_agents["data/agents/*.yaml"]
        yaml_projects["data/projects/*.yaml"]
        yaml_resources["data/resources/*.yaml"]
        yaml_forks["data/forks/*.yaml"]
    end
    
    subgraph "Schema Layer"
        schema_json["data/schema.json<br/>JSON Schema Draft-07"]
        schema_doc["docs/schema-design.md<br/>Human Documentation"]
    end
    
    subgraph "Validation Rules"
        required["Required Fields<br/>name, repo, tagline, description"]
        optional["Optional Fields<br/>scope, tags, min_version,<br/>homepage, installation"]
        constraints["Constraints<br/>tagline maxLength: 120<br/>min_version pattern: semver<br/>scope enum: global|project"]
        type_derive["Type Derivation<br/>from directory path"]
    end
    
    yaml_plugins -->|"validates against"| schema_json
    yaml_themes -->|"validates against"| schema_json
    yaml_agents -->|"validates against"| schema_json
    yaml_projects -->|"validates against"| schema_json
    yaml_resources -->|"validates against"| schema_json
    yaml_forks -->|"validates against"| schema_json
    
    schema_json --> required
    schema_json --> optional
    schema_json --> constraints
    
    yaml_plugins -.->|"directory implies"| type_derive
    yaml_themes -.->|"directory implies"| type_derive
    
    schema_doc -.->|"documents"| schema_json
    
    type_derive -->|"plugin"| yaml_plugins
    type_derive -->|"theme"| yaml_themes
    type_derive -->|"agent"| yaml_agents
    type_derive -->|"project"| yaml_projects
    type_derive -->|"resource"| yaml_resources
    type_derive -->|"fork"| yaml_forks
```

Sources: [docs/schema-design.md:1-63](), [data/schema.json:1-63]()

For more details on the validation pipeline, see [Schema System](#3.1).

---

## Required Fields

All YAML entries must contain four required fields. These fields are enforced by the JSON Schema at [data/schema.json:61]().

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| `name` | `string` | `minLength: 1` | Display name of the extension or project |
| `repo` | `string` | `format: uri` | HTTPS repository URL (e.g., `https://github.com/user/repo`) |
| `tagline` | `string` | `minLength: 1`<br/>`maxLength: 120` | Short summary displayed in collapsed view |
| `description` | `string` | `minLength: 1` | Full description, may be multi-line markdown |

The `name` field ([data/schema.json:8-11]()) represents the human-readable display name. The `tagline` field ([data/schema.json:18-22]()) has a strict 120-character limit enforced at the schema level.

For details on all standard fields, see [Common Fields](#3.2).

Sources: [data/schema.json:7-27](), [data/schema.json:61](), [docs/schema-design.md:199-238]()

---

## Optional Fields

Five optional fields provide enhanced metadata and installation guidance. When omitted, sensible defaults are applied by the build system.

| Field | Type | Default | Constraint | Description |
|-------|------|---------|------------|-------------|
| `scope` | `array` | `["global"]` | items: `"global"` or `"project"` | Installation scope (user-wide vs project-specific) |
| `tags` | `array` | `[]` | items: `string` | Freeform tags for filtering and discovery |
| `min_version` | `string` | (none) | pattern: `^[0-9]+\.[0-9]+\.[0-9]+` | Minimum OpenCode version required (semver) |
| `homepage` | `string` | (none) | format: `uri` | Documentation URL if different from `repo` |
| `installation` | `string` | (none) | (none) | Detailed installation instructions in markdown |

The `scope` field ([data/schema.json:29-38]()) determines if an extension is installed to `~/.config/opencode/` (global) or `.opencode/` (project). If omitted, the build system defaults to `["global"]` ([docs/schema-design.md:210]()).

For details on how these fields are used, see [Common Fields](#3.2).

Sources: [data/schema.json:29-59](), [docs/schema-design.md:209-217]()

---

## Type Derivation System

The extension type and unique identifier are **not stored in YAML files**. Instead, they are derived from the directory path and filename. This convention-over-configuration approach ensures consistency and prevents type mismatches.

**Diagram: Directory-to-Type Mapping**

```mermaid
graph LR
    subgraph "File System Structure"
        data["data/"]
        plugins_dir["data/plugins/"]
        themes_dir["data/themes/"]
        agents_dir["data/agents/"]
        projects_dir["data/projects/"]
        resources_dir["data/resources/"]
        forks_dir["data/forks/"]
        
        data --> plugins_dir
        data --> themes_dir
        data --> agents_dir
        data --> projects_dir
        data --> resources_dir
        data --> forks_dir
        
        plugins_dir --> plugin_yaml["kilo-auth.yaml"]
        themes_dir --> theme_yaml["dark-theme.yaml"]
        agents_dir --> agent_yaml["security-agent.yaml"]
        projects_dir --> project_yaml["web-ui.yaml"]
        resources_dir --> resource_yaml["mcp-server.yaml"]
        forks_dir --> fork_yaml["custom-build.yaml"]
    end
    
    subgraph "Derived Type Values"
        plugin_yaml -.->|"type: plugin"| type_plugin["plugin"]
        theme_yaml -.->|"type: theme"| type_theme["theme"]
        agent_yaml -.->|"type: agent"| type_agent["agent"]
        project_yaml -.->|"type: project"| type_project["project"]
        resource_yaml -.->|"type: resource"| type_resource["resource"]
        fork_yaml -.->|"type: fork"| type_fork["fork"]
    end
```

### Key Derivations

*   **Type**: Extracted from the parent directory name (e.g., `data/plugins/` implies `type: plugin`).
*   **Product ID**: Extracted from the filename without extension (e.g., `kilo-auth.yaml` implies `productId: kilo-auth`).

For more details on the derivation logic, see [Type Derivation](#3.3).

Sources: [docs/schema-design.md:17](), [docs/schema-design.md:218-230](), [data/plugins/kilo-auth.yaml:1-4]()

---

## Downstream Field Mapping

The YAML data model is transformed into a machine-readable JSON format for consumption by downstream platforms. This mapping adds derived fields and renames fields for API consistency.

**Diagram: YAML to JSON Transformation**

```mermaid
graph LR
    subgraph "Source YAML (data/*.yaml)"
        yaml_name["name"]
        yaml_repo["repo"]
        yaml_tagline["tagline"]
        yaml_desc["description"]
        yaml_scope["scope"]
        yaml_tags["tags"]
        yaml_home["homepage"]
        yaml_install["installation"]
        yaml_min["min_version"]
    end
    
    subgraph "Derived Values"
        file_path["File Path:<br/>data/plugins/kilo-auth.yaml"]
        directory["Directory: plugins"]
        filename["Filename: kilo-auth"]
    end
    
    subgraph "Output JSON (dist/registry.json)"
        json_display["displayName"]
        json_repo["repoUrl"]
        json_tagline["tagline"]
        json_desc["description"]
        json_type["type"]
        json_product["productId"]
        json_scope["scope"]
        json_tags["tags"]
        json_home["homepageUrl"]
        json_install["installation"]
        json_min["minVersion"]
    end
    
    yaml_name -->|"rename"| json_display
    yaml_repo -->|"rename"| json_repo
    yaml_tagline -->|"copy"| json_tagline
    yaml_desc -->|"copy"| json_desc
    yaml_scope -->|"default: ['global']"| json_scope
    yaml_tags -->|"default: []"| json_tags
    yaml_home -->|"rename"| json_home
    yaml_install -->|"copy"| json_install
    yaml_min -->|"rename"| json_min
    
    file_path --> directory
    file_path --> filename
    directory -->|"extract"| json_type
    filename -->|"extract"| json_product
```

### Transformation Table

| YAML Field | JSON Field | Transformation |
|------------|------------|----------------|
| `name` | `displayName` | Rename |
| `repo` | `repoUrl` | Rename |
| (directory) | `type` | Derive |
| (filename) | `productId` | Derive |
| `homepage` | `homepageUrl` | Rename |
| `min_version` | `minVersion` | Rename |

Sources: [docs/schema-design.md:17](), [data/schema.json:1-63]()

---

## Example Files

Complete example files demonstrating all fields are maintained in the `data/examples/` directory. These serve as the primary reference for contributors.

| Entry Type | Example File Path |
|------------|-------------------|
| Plugin | `data/examples/plugin.yaml` |
| Theme | `data/examples/theme.yaml` |
| Agent | `data/examples/agent.yaml` |
| Project | `data/examples/project.yaml` |
| Resource | `data/examples/resource.yaml` |
| Fork | `data/examples/fork.yaml` |

Sources: [docs/schema-design.md:19-40]()

---

