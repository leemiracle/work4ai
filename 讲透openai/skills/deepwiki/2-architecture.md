<!-- source: DeepWiki mcp.deepwiki.com · repo openai/skills · page 2 Architecture · fetched 2026-10-30 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [README.md](README.md)
- [skills/.system/skill-creator/SKILL.md](skills/.system/skill-creator/SKILL.md)
- [skills/.system/skill-creator/references/openai_yaml.md](skills/.system/skill-creator/references/openai_yaml.md)
- [skills/.system/skill-creator/scripts/generate_openai_yaml.py](skills/.system/skill-creator/scripts/generate_openai_yaml.py)
- [skills/.system/skill-creator/scripts/init_skill.py](skills/.system/skill-creator/scripts/init_skill.py)
- [skills/.system/skill-creator/scripts/quick_validate.py](skills/.system/skill-creator/scripts/quick_validate.py)

</details>



## Purpose and Scope

This document explains the architectural design of the Agent Skills system, including the three-tier skill organization (`.system/`, `.curated/`, `.experimental/`), the progressive disclosure loading model, and the complete skill lifecycle from development to runtime execution. The architecture optimizes for context window efficiency while enabling modular capability distribution.

For detailed information on specific subsystems, see:
- Three-tier categorization and installation methods: [Three-Tier Skill System](#2.1)
- Context window optimization strategy: [Progressive Disclosure Model](#2.2)
- Complete skill journey from creation to execution: [Skill Lifecycle](#2.3)
- MCP-based external service connections: [MCP Integration Pattern](#2.4)

## High-Level System Architecture

The Agent Skills repository implements a modular capability distribution system organized into four functional layers: development tooling, distribution repositories, installation utilities, and runtime execution.

**System Architecture: Development to Runtime**

```mermaid
graph TB
    subgraph "Development Tools (skills/.system/skill-creator/scripts/)"
        init_skill_py["init_skill.py<br/>init_skill(skill_name, path, resources)"]
        quick_validate_py["quick_validate.py<br/>validate_skill(skill_path)"]
        generate_yaml["generate_openai_yaml.py<br/>write_openai_yaml()"]
    end
    
    subgraph "Distribution Repositories"
        system_skills["skills/.system/<br/>skill-creator/<br/>skill-installer/"]
        curated_skills["skills/.curated/<br/>gh-address-comments/<br/>gh-fix-ci/<br/>notion-*/<br/>figma-*/"]
        experimental_skills["skills/.experimental/<br/>create-plan/"]
    end
    
    subgraph "Installation Tools"
        skill_installer["$skill-installer<br/>(CLI utility)"]
    end
    
    subgraph "Runtime Environment"
        codex_home["$CODEX_HOME/skills/<br/>~/.codex/skills/<skill-name>/"]
        skill_md["SKILL.md<br/>YAML frontmatter + Markdown body"]
        agents_yaml["agents/openai.yaml<br/>interface metadata"]
        resources["scripts/ references/ assets/"]
    end
    
    init_skill_py --> skill_md
    init_skill_py --> generate_yaml
    generate_yaml --> agents_yaml
    quick_validate_py --> skill_md
    
    skill_md --> system_skills
    skill_md --> curated_skills
    skill_md --> experimental_skills
    
    skill_installer --> curated_skills
    skill_installer --> experimental_skills
    
    skill_installer --> codex_home
    skill_md -.installed to.-> codex_home
    agents_yaml -.installed to.-> codex_home
    resources -.installed to.-> codex_home
```

**Directory Structure and Installation Methods**

| Directory Path | Purpose | Installation Command | Auto-Installed |
|---------------|---------|---------------------|----------------|
| `skills/.system/` | Core system skills and development tools | N/A | Yes [README.md:14-14]() |
| `skills/.curated/` | Production-ready, reviewed skills | `$skill-installer <skill-name>` | No [README.md:18-22]() |
| `skills/.experimental/` | Development/testing skills | `$skill-installer install ... --path ...` | No [README.md:24-34]() |

**Sources**: [README.md:12-36](), [skills/.system/skill-creator/SKILL.md:48-64](), [skills/.system/skill-creator/scripts/init_skill.py:1-14]()

## Skill Structure and Format

Every skill is a directory containing a mandatory `SKILL.md` file and optional bundled resources. The structure is validated by the `validate_skill()` function in `quick_validate.py`.

**Skill Directory Structure (skill-name/)**

```mermaid
graph TB
    skill_dir["skill-name/"]
    
    subgraph "Required Files"
        skill_md["SKILL.md"]
        frontmatter["---<br/>YAML frontmatter<br/>---"]
        name_field["name: skill-name"]
        desc_field["description: ..."]
        body["Markdown body"]
    end
    
    subgraph "Recommended Files"
        agents_dir["agents/"]
        openai_yaml["openai.yaml"]
        interface_fields["interface:<br/>  display_name<br/>  short_description<br/>  default_prompt"]
    end
    
    subgraph "Optional Resources"
        scripts_dir["scripts/"]
        script_examples["*.py, *.sh"]
        references_dir["references/"]
        ref_examples["*.md (API docs, schemas)"]
        assets_dir["assets/"]
        asset_examples["*.png, *.pptx, templates/"]
    end
    
    skill_dir --> skill_md
    skill_md --> frontmatter
    frontmatter --> name_field
    frontmatter --> desc_field
    skill_md --> body
    
    skill_dir -.-> agents_dir
    agents_dir --> openai_yaml
    openai_yaml --> interface_fields
    
    skill_dir -.-> scripts_dir
    scripts_dir --> script_examples
    skill_dir -.-> references_dir
    references_dir --> ref_examples
    skill_dir -.-> assets_dir
    assets_dir --> asset_examples
```

**Frontmatter Validation Rules (validate_skill())**

The `validate_skill()` function at [skills/.system/skill-creator/scripts/quick_validate.py:15-91]() enforces these constraints:

| Field | Validation Rule | Code Reference |
|-------|----------------|----------------|
| `name` | Required, `^[a-z0-9-]+$`, no leading/trailing/consecutive hyphens, ≤64 chars | [skills/.system/skill-creator/scripts/quick_validate.py:51-76]() |
| `description` | Required, no `<>` characters, ≤1024 chars | [skills/.system/skill-creator/scripts/quick_validate.py:53-89]() |
| Allowed properties | `name`, `description`, `license`, `allowed-tools`, `metadata` | [skills/.system/skill-creator/scripts/quick_validate.py:40-49]() |

**Resource Directory Creation (init_skill())**

The `init_skill.py` script creates resource directories based on the `--resources` argument:

| Directory | Creation Flag | Token Impact | Purpose |
|-----------|-----------|-------------|---------|
| `scripts/` | `--resources scripts` | 0 (executed, not loaded to context) | Executable code (Python, Bash, etc.) [skills/.system/skill-creator/SKILL.md:86-93]() |
| `references/` | `--resources references` | Variable (loaded as needed) | Documentation for context injection [skills/.system/skill-creator/SKILL.md:95-104]() |
| `assets/` | `--resources assets` | 0 (used in output, never loaded) | Templates, images, fonts, boilerplate [skills/.system/skill-creator/SKILL.md:106-113]() |

**Sources**: [skills/.system/skill-creator/SKILL.md:48-65](), [skills/.system/skill-creator/scripts/init_skill.py:23-24](), [skills/.system/skill-creator/scripts/quick_validate.py:15-91]()

## Progressive Disclosure Loading Model

The system implements a three-level progressive disclosure model to optimize context window usage. Each level loads progressively more content as needed, minimizing token overhead across dozens of installed skills.

**Three-Level Loading Strategy**

```mermaid
graph TB
    subgraph "Level 1: Metadata (All Skills)"
        level1_load["Parse YAML frontmatter"]
        level1_fields["name: <skill-name><br/>description: <when-to-use>"]
        level1_cost["~100 words per skill<br/>ALL skills loaded"]
    end
    
    subgraph "Level 2: Body (Triggered Skill)"
        level2_trigger["User query matches description"]
        level2_load["Parse SKILL.md Markdown body"]
        level2_content["## Overview<br/>## Workflow<br/>## Instructions"]
        level2_cost["<5k words<br/>SINGLE skill loaded"]
    end
    
    subgraph "Level 3: Resources (As Needed)"
        level3_decision["Codex determines resource needs"]
        level3_scripts["Execute scripts/*.py<br/>(no context load)"]
        level3_refs["Load references/*.md<br/>(into context)"]
        level3_assets["Use assets/*<br/>(in output, no load)"]
        level3_cost["Variable: 0 (scripts/assets)<br/>to unlimited (references)"]
    end
    
    level1_load --> level1_fields
    level1_fields --> level1_cost
    
    level1_cost --> level2_trigger
    level2_trigger --> level2_load
    level2_load --> level2_content
    level2_content --> level2_cost
    
    level2_cost --> level3_decision
    level3_decision --> level3_scripts
    level3_decision --> level3_refs
    level3_decision --> level3_assets
    level3_scripts --> level3_cost
    level3_refs --> level3_cost
    level3_assets --> level3_cost
```

**Level-by-Level Loading Characteristics**

| Level | Content Loaded | Scope | Token Cost | Loading Condition |
|-------|---------------|-------|------------|------------------|
| 1 | `name`, `description` (YAML frontmatter) | All installed skills | ~100 words × N | Codex startup [skills/.system/skill-creator/SKILL.md:131-131]() |
| 2 | Markdown body (below frontmatter) | Single triggered skill | <5k words | Description matches query [skills/.system/skill-creator/SKILL.md:132-132]() |
| 3 | `scripts/`, `references/`, `assets/` | As determined by Codex | 0 (scripts/assets), variable (references) | Workflow execution [skills/.system/skill-creator/SKILL.md:133-133]() |

For details, see [Progressive Disclosure Model](#2.2).

**Sources**: [skills/.system/skill-creator/SKILL.md:127-133](), [skills/.system/skill-creator/scripts/init_skill.py:73-110]()

## Skill Lifecycle

The complete skill lifecycle from creation to runtime execution follows a standardized process involving initialization, validation, and distribution.

**Development and Distribution Pipeline**

```mermaid
graph LR
    subgraph "Creation (init_skill.py)"
        init["init_skill.py"]
        tmpl["SKILL_TEMPLATE"]
    end
    
    subgraph "Refinement"
        edit["Manual Editing"]
        gen_yaml["generate_openai_yaml.py"]
    end
    
    subgraph "Validation (quick_validate.py)"
        val["validate_skill()"]
    end
    
    subgraph "Distribution"
        inst["$skill-installer"]
    end
    
    init --> tmpl
    tmpl --> edit
    edit --> gen_yaml
    gen_yaml --> val
    val --> inst
```

| Phase | Key Tool | Primary Action | Code Reference |
|-------|----------|----------------|----------------|
| **Creation** | `init_skill.py` | Scaffold directory structure and `SKILL.md` | [skills/.system/skill-creator/scripts/init_skill.py:25-111]() |
| **Refinement** | `generate_openai_yaml.py` | Create `agents/openai.yaml` interface metadata | [skills/.system/skill-creator/scripts/generate_openai_yaml.py:155-186]() |
| **Validation** | `quick_validate.py` | Verify frontmatter and naming constraints | [skills/.system/skill-creator/scripts/quick_validate.py:15-91]() |
| **Distribution** | `$skill-installer` | Download and extract to local skills directory | [README.md:12-36]() |

For details, see [Skill Lifecycle](#2.3).

**Sources**: [skills/.system/skill-creator/scripts/init_skill.py:1-111](), [skills/.system/skill-creator/scripts/quick_validate.py:1-102](), [README.md:12-36]()

## MCP Integration Pattern

Skills connect to external services (like Figma, Notion, or Linear) using the Model Context Protocol (MCP). This pattern uses `streamable_http` transport to allow Codex to invoke tools hosted on remote servers.

**MCP Tool Architecture**

```mermaid
graph LR
    subgraph "Codex Runtime"
        skill["Skill Instructions<br/>(SKILL.md)"]
        config["agents/openai.yaml<br/>(dependencies)"]
    end
    
    subgraph "MCP Client Interface"
        transport["streamable_http"]
    end
    
    subgraph "Remote MCP Server"
        mcp_srv["MCP Server Endpoint"]
        tools["Tools List"]
    end
    
    skill --> config
    config --> transport
    transport -- "HTTP Request" --> mcp_srv
    mcp_srv --> tools
```

**Key Integration Entities**

| Entity | Role | Code Reference |
|--------|------|----------------|
| `dependencies.tools` | Defines the MCP server type, value, and URL in `openai.yaml` | [skills/.system/skill-creator/references/openai_yaml.md:16-23]() |
| `streamable_http` | The transport protocol used for remote MCP connections | [skills/.system/skill-creator/references/openai_yaml.md:21-21]() |
| `interface.default_prompt` | Snippet mentioning `$skill-name` to trigger usage | [skills/.system/skill-creator/references/openai_yaml.md:31-31]() |

For details, see [MCP Integration Pattern](#2.4).

**Sources**: [skills/.system/skill-creator/references/openai_yaml.md:1-44]()

---

